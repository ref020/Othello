# Standalone tests for the Othello AI evaluation breakdown.
# This file is for local verification, not assignment submission.
import contextlib
import io
import unittest

from ai import OthelloAI
from board import BLACK_DISK, WHITE_DISK
from game import Game


class TestEvaluationBreakdown(unittest.TestCase):
    CONTRIBUTION_KEYS = (
        'Weighted Disk Difference',
        'Weighted Mobility Difference',
        'Weighted Corner Ownership Difference',
        'Weighted Positional Difference',
    )

    def setUp(self):
        self.ai = OthelloAI()

    def assertBreakdownConsistent(self, game, aiColor):
        originalGrid = [row.copy() for row in game.gameBoard.grid]
        originalState = (game.currentPlayer, game.moveCount, game.gameOver, game.winner)
        breakdown = self.ai.getEvalBreakdown(game, aiColor)

        expectedKeys = {
            'Disk Difference', 'Weighted Disk Difference',
            'Mobility Difference', 'Weighted Mobility Difference',
            'Corner Ownership Difference', 'Weighted Corner Ownership Difference',
            'Positional Difference', 'Weighted Positional Difference',
            'Heuristic Total Score', 'Evaluated Score',
        }
        self.assertEqual(set(breakdown), expectedKeys)
        self.assertEqual(
            sum(breakdown[key] for key in self.CONTRIBUTION_KEYS),
            breakdown['Heuristic Total Score'],
            'Weighted contributions do not add up to the heuristic total',
        )
        self.assertEqual(
            breakdown['Evaluated Score'], self.ai.evaluateGame(game, aiColor),
            'Breakdown does not match the AI evaluation',
        )
        if not game.gameOver:
            self.assertEqual(
                breakdown['Heuristic Total Score'], breakdown['Evaluated Score'],
                'Nonterminal heuristic and evaluation should agree',
            )
        self.assertEqual(game.gameBoard.grid, originalGrid, 'Breakdown modified the board')
        self.assertEqual(
            (game.currentPlayer, game.moveCount, game.gameOver, game.winner),
            originalState, 'Breakdown modified game state',
        )
        return breakdown

    def test_initial_board(self):
        game = Game()
        for color in (BLACK_DISK, WHITE_DISK):
            with self.subTest(aiColor=color):
                breakdown = self.assertBreakdownConsistent(game, color)
                self.assertEqual(breakdown['Heuristic Total Score'], 0)
                self.assertEqual(breakdown['Evaluated Score'], 0)
                print(f'Initial board, AI color {color}: score={breakdown["Evaluated Score"]}')

    def test_nonterminal_positions_and_color_symmetry(self):
        game = Game()
        for moveNumber in range(5):
            with self.subTest(moveNumber=moveNumber):
                black = self.assertBreakdownConsistent(game, BLACK_DISK)
                white = self.assertBreakdownConsistent(game, WHITE_DISK)
                for key in (
                    'Disk Difference', 'Weighted Disk Difference',
                    'Mobility Difference', 'Weighted Mobility Difference',
                    'Corner Ownership Difference', 'Weighted Corner Ownership Difference',
                    'Positional Difference', 'Weighted Positional Difference',
                    'Heuristic Total Score', 'Evaluated Score',
                ):
                    self.assertEqual(black[key], -white[key], f'Color symmetry failed: {key}')
                print(f'After {moveNumber} moves: black={black["Evaluated Score"]}, '
                      f'white={white["Evaluated Score"]}')
                if moveNumber < 4:
                    moves = game.gameBoard.getLegalMoves(game.currentPlayer)
                    self.assertTrue(moves, 'Unexpectedly no legal move in opening test')
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertTrue(game.makeMove(*moves[0]))

    def makeTerminalGame(self, blackCount):
        # Construct a full board with the specified number of black disks.
        game = Game()
        cells = [BLACK_DISK] * blackCount + [WHITE_DISK] * (64 - blackCount)
        game.gameBoard.grid = [cells[row * 8:(row + 1) * 8] for row in range(8)]
        game.advanceTurn()
        self.assertTrue(game.gameOver)
        return game

    def test_terminal_black_victory(self):
        game = self.makeTerminalGame(40)
        self.assertEqual(game.winner, BLACK_DISK)
        self.assertEqual(self.assertBreakdownConsistent(game, BLACK_DISK)['Evaluated Score'], 100000)
        self.assertEqual(self.assertBreakdownConsistent(game, WHITE_DISK)['Evaluated Score'], -100000)

    def test_terminal_white_victory(self):
        game = self.makeTerminalGame(20)
        self.assertEqual(game.winner, WHITE_DISK)
        self.assertEqual(self.assertBreakdownConsistent(game, WHITE_DISK)['Evaluated Score'], 100000)
        self.assertEqual(self.assertBreakdownConsistent(game, BLACK_DISK)['Evaluated Score'], -100000)

    def test_terminal_tie(self):
        game = self.makeTerminalGame(32)
        self.assertEqual(game.winner, 0)
        for color in (BLACK_DISK, WHITE_DISK):
            with self.subTest(aiColor=color):
                self.assertEqual(self.assertBreakdownConsistent(game, color)['Evaluated Score'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
