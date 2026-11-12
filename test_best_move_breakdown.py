# Standalone tests for Othello principal-variation evaluation breakdown.
# Keep this test file separate from the submitted assignment implementation.
import unittest

from ai import OthelloAI
from game import Game
from board import BLACK_DISK, WHITE_DISK


class TestBestMoveBreakdown(unittest.TestCase):
    def makePosition(self, moves):
        game = Game()
        for row, col in moves:
            self.assertTrue(game.makeMove(row, col), f"Setup move {(row, col)} failed")
        return game

    def snapshot(self, game):
        return (
            tuple(tuple(row) for row in game.gameBoard.grid),
            game.currentPlayer,
            game.moveCount,
            game.gameOver,
            game.winner,
        )

    def checkSearch(self, game, color, useAlphaBeta, depth=4):
        ai = OthelloAI()
        before = self.snapshot(game)
        move = ai.chooseMove(game, depth, color, useAlphaBeta)
        self.assertEqual(self.snapshot(game), before, "Search modified the original game")
        self.assertIsNotNone(move)
        self.assertIsNotNone(ai.bestMoveBreakdown)
        self.assertEqual(ai.bestMovePath[0], move)
        self.assertLessEqual(len(ai.bestMovePath), depth)

        replay = game.copyGame()
        for predictedMove in ai.bestMovePath:
            self.assertIn(predictedMove, replay.gameBoard.getLegalMoves(replay.currentPlayer))
            self.assertTrue(replay.makeMove(*predictedMove))

        expected = ai.getEvalBreakdown(replay, color)
        self.assertEqual(ai.bestMoveBreakdown, expected)
        self.assertEqual(ai.bestMoveBreakdown["Evaluated Score"], ai.evaluateGame(replay, color))
        self.assertEqual(self.snapshot(game), before, "Replay modified the original game")
        return ai, move

    def test_black_opening(self):
        game = Game()
        for useAlphaBeta in (False, True):
            with self.subTest(alphaBeta=useAlphaBeta):
                ai, move = self.checkSearch(game, BLACK_DISK, useAlphaBeta)
                self.assertEqual(ai.bestMoveBreakdown["Evaluated Score"], ai.bestMoveScore)
                print(f"Black {'Alpha-Beta' if useAlphaBeta else 'Mini-Max'}: move={move}, "
                      f"score={ai.bestMoveScore}, path={ai.bestMovePath}")

    def test_white_after_black_move(self):
        game = self.makePosition([(2, 3)])
        self.assertEqual(game.currentPlayer, WHITE_DISK)
        for useAlphaBeta in (False, True):
            with self.subTest(alphaBeta=useAlphaBeta):
                ai, move = self.checkSearch(game, WHITE_DISK, useAlphaBeta)
                self.assertEqual(ai.bestMoveBreakdown["Evaluated Score"], ai.bestMoveScore)
                print(f"White {'Alpha-Beta' if useAlphaBeta else 'Mini-Max'}: move={move}, "
                      f"score={ai.bestMoveScore}, path={ai.bestMovePath}")

    def test_algorithms_agree_on_selected_move_and_score(self):
        for game, color in ((Game(), BLACK_DISK), (self.makePosition([(2, 3)]), WHITE_DISK)):
            with self.subTest(color=color):
                minimax, minimaxMove = self.checkSearch(game, color, False)
                alphabeta, alphabetaMove = self.checkSearch(game, color, True)
                self.assertEqual(minimaxMove, alphabetaMove)
                self.assertEqual(minimax.bestMoveScore, alphabeta.bestMoveScore)

    def test_no_legal_moves_resets_breakdown(self):
        ai = OthelloAI()
        game = Game()
        # Use a board with no empty cells and an already-completed game.
        for row in range(game.gameBoard.size):
            for col in range(game.gameBoard.size):
                game.gameBoard.grid[row][col] = BLACK_DISK
        game.gameOver = True
        ai.bestMoveBreakdown = {"stale": True}
        ai.bestMovePath = [(2, 3)]
        ai.bestMoveScore = 123
        self.assertIsNone(ai.chooseMove(game, 4, WHITE_DISK, True))
        self.assertIsNone(ai.bestMoveBreakdown)
        self.assertEqual(ai.bestMovePath, [])
        self.assertIsNone(ai.bestMoveScore)


if __name__ == "__main__":
    unittest.main(verbosity=2)
