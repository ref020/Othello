# Temporary tests for OthelloAI.chooseMove(). Do not submit with the assignment.
import contextlib
import io
import unittest

from ai import OthelloAI
from board import Board, BLACK_DISK, WHITE_DISK
from game import Game


class TestChooseMove(unittest.TestCase):
    def setUp(self):
        self.ai = OthelloAI()
        self.game = Game()

    def chooseSilently(self, game, depth, color):
        # Suppress board flip messages from hypothetical moves.
        with contextlib.redirect_stdout(io.StringIO()):
            return self.ai.chooseMove(game, depth, color)

    def expectedBestMove(self, game, depth, color):
        # Independent root-level comparison using the existing minimax evaluator.
        moves = game.gameBoard.getLegalMoves(color)
        if not moves:
            return None
        bestMove = None
        bestScore = float('-inf')
        with contextlib.redirect_stdout(io.StringIO()):
            for row, col in moves:
                simulated = game.copyGame()
                self.assertTrue(simulated.makeMove(row, col))
                score = self.ai.minimax(
                    simulated, depth - 1, color,
                    simulated.currentPlayer == color
                )
                if score > bestScore:
                    bestScore = score
                    bestMove = (row, col)
        return bestMove

    def test_returns_legal_move_as_black(self):
        result = self.chooseSilently(self.game, 1, BLACK_DISK)
        self.assertIn(result, self.game.gameBoard.getLegalMoves(BLACK_DISK))

    def test_returns_legal_move_as_white(self):
        # A valid white-to-move state after one black move.
        firstBlackMove = self.game.gameBoard.getLegalMoves(BLACK_DISK)[0]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(self.game.makeMove(*firstBlackMove))
        self.assertEqual(self.game.currentPlayer, WHITE_DISK)
        result = self.chooseSilently(self.game, 1, WHITE_DISK)
        self.assertIn(result, self.game.gameBoard.getLegalMoves(WHITE_DISK))

    def test_returns_none_when_no_moves(self):
        game = Game()
        game.gameBoard.grid = [[BLACK_DISK for _ in range(game.gameBoard.size)] for _ in range(game.gameBoard.size)]
        game.currentPlayer = WHITE_DISK
        self.assertIsNone(self.chooseSilently(game, 1, WHITE_DISK))

    def test_does_not_modify_original_game(self):
        beforeGrid = [row.copy() for row in self.game.gameBoard.grid]
        beforeTurn = self.game.currentPlayer
        beforeMoveCount = self.game.moveCount
        beforeGameOver = self.game.gameOver
        beforeWinner = self.game.winner
        self.chooseSilently(self.game, 3, BLACK_DISK)
        self.assertEqual(self.game.gameBoard.grid, beforeGrid)
        self.assertEqual(self.game.currentPlayer, beforeTurn)
        self.assertEqual(self.game.moveCount, beforeMoveCount)
        self.assertEqual(self.game.gameOver, beforeGameOver)
        self.assertEqual(self.game.winner, beforeWinner)

    def test_picks_highest_evaluation_at_depth_one(self):
        expected = self.expectedBestMove(self.game, 1, BLACK_DISK)
        actual = self.chooseSilently(self.game, 1, BLACK_DISK)
        self.assertEqual(actual, expected)

    def test_picks_minimax_best_move_at_depth_three(self):
        expected = self.expectedBestMove(self.game, 3, BLACK_DISK)
        actual = self.chooseSilently(self.game, 3, BLACK_DISK)
        self.assertEqual(actual, expected)

    def test_is_deterministic_on_same_position(self):
        first = self.chooseSilently(self.game, 2, BLACK_DISK)
        second = self.chooseSilently(self.game, 2, BLACK_DISK)
        self.assertEqual(first, second)

    def test_move_can_be_played_on_real_game(self):
        move = self.chooseSilently(self.game, 2, BLACK_DISK)
        self.assertIsNotNone(move)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(self.game.makeMove(*move))
        self.assertEqual(self.game.moveCount, 1)
        self.assertEqual(self.game.currentPlayer, WHITE_DISK)


if __name__ == '__main__':
    unittest.main()
