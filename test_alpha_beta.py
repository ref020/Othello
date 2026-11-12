# Temporary tests for the Othello AI. Do not include in the assignment submission.
import contextlib
import io
import unittest

from ai import OthelloAI
from board import BLACK_DISK, WHITE_DISK, EMPTY_CELL
from game import Game


class TestAlphaBeta(unittest.TestCase):
    def setUp(self):
        self.ai = OthelloAI()

    def evaluateQuietly(self, method, *args):
        # The game's existing move-debug messages are irrelevant to these tests.
        with contextlib.redirect_stdout(io.StringIO()):
            return method(*args)

    def compareSearches(self, game, depth, aiColor):
        isMaximizing = game.currentPlayer == aiColor
        plain = self.evaluateQuietly(self.ai.minimax, game, depth, aiColor, isMaximizing)
        pruned = self.evaluateQuietly(
            self.ai.minimaxAlphaBeta, game, depth, aiColor,
            isMaximizing, float('-inf'), float('inf')
        )
        self.assertEqual(plain, pruned)
        return pruned

    def test_depth_zero_matches_evaluation(self):
        game = Game()
        result = self.evaluateQuietly(
            self.ai.minimaxAlphaBeta, game, 0, BLACK_DISK, True,
            float('-inf'), float('inf')
        )
        self.assertEqual(result, self.ai.evaluateGame(game, BLACK_DISK))

    def test_maximizing_root_matches_minimax(self):
        self.compareSearches(Game(), 3, BLACK_DISK)

    def test_minimizing_root_matches_minimax(self):
        self.compareSearches(Game(), 3, WHITE_DISK)

    def test_multiple_depths_match_minimax(self):
        game = Game()
        for depth in (1, 2, 3, 4):
            with self.subTest(depth=depth):
                self.compareSearches(game, depth, BLACK_DISK)

    def test_midgame_matches_minimax_for_both_colors(self):
        game = Game()
        # Build a reproducible legal position, without choosing illegal coordinates.
        with contextlib.redirect_stdout(io.StringIO()):
            for _ in range(10):
                if game.gameOver:
                    break
                legal = game.gameBoard.getLegalMoves(game.currentPlayer)
                if not legal:
                    break
                self.assertTrue(game.makeMove(*legal[0]))
        for aiColor in (BLACK_DISK, WHITE_DISK):
            with self.subTest(aiColor=aiColor):
                self.compareSearches(game, 3, aiColor)

    def test_forced_pass_matches_minimax(self):
        game = Game()
        # White cannot move; Black can play at (0, 0) and flip (0, 1).
        game.gameBoard.grid = [[BLACK_DISK] * 8 for _ in range(8)]
        game.gameBoard.grid[0][0] = EMPTY_CELL
        game.gameBoard.grid[0][1] = WHITE_DISK
        game.currentPlayer = WHITE_DISK
        self.assertEqual(game.gameBoard.getLegalMoves(WHITE_DISK), [])
        self.assertIn((0, 0), game.gameBoard.getLegalMoves(BLACK_DISK))
        self.compareSearches(game, 2, WHITE_DISK)
        self.assertEqual(game.currentPlayer, WHITE_DISK)
        self.assertFalse(game.gameOver)

    def test_terminal_win_loss_and_draw(self):
        for label, grid, expectedBlack, expectedWhite in (
            ('black_win', [[BLACK_DISK] * 8 for _ in range(8)], 100000, -100000),
            ('white_win', [[WHITE_DISK] * 8 for _ in range(8)], -100000, 100000),
            ('draw', [[BLACK_DISK] * 8 for _ in range(4)] + [[WHITE_DISK] * 8 for _ in range(4)], 0, 0),
        ):
            with self.subTest(outcome=label):
                game = Game()
                game.gameBoard.grid = [row.copy() for row in grid]
                game.gameOver = True
                game.getWinner()
                self.assertEqual(self.compareSearches(game, 3, BLACK_DISK), expectedBlack)
                self.assertEqual(self.compareSearches(game, 3, WHITE_DISK), expectedWhite)

    def test_search_does_not_mutate_original_game(self):
        game = Game()
        beforeGrid = [row.copy() for row in game.gameBoard.grid]
        beforeState = (game.currentPlayer, game.moveCount, game.gameOver, game.winner)
        self.evaluateQuietly(
            self.ai.minimaxAlphaBeta, game, 4, BLACK_DISK, True,
            float('-inf'), float('inf')
        )
        self.assertEqual(game.gameBoard.grid, beforeGrid)
        self.assertEqual((game.currentPlayer, game.moveCount, game.gameOver, game.winner), beforeState)


if __name__ == '__main__':
    unittest.main()
