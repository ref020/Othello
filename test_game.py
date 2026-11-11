
import unittest

from board import Board, BLACK_DISK, WHITE_DISK
from game import Game


class TestGameCopy(unittest.TestCase):

    def setUp(self):
        self.original = Game()

    def test_copy_is_new_game_object(self):
        copied = self.original.copyGame()

        self.assertIsNot(copied, self.original)
        self.assertIsInstance(copied, Game)

    def test_board_is_independent(self):
        copied = self.original.copyGame()

        self.assertIsNot(copied.gameBoard, self.original.gameBoard)
        self.assertIsNot(copied.gameBoard.grid, self.original.gameBoard.grid)

        for originalRow, copiedRow in zip(
            self.original.gameBoard.grid,
            copied.gameBoard.grid
        ):
            self.assertIsNot(originalRow, copiedRow)

    def test_initial_board_contents_match(self):
        copied = self.original.copyGame()

        self.assertEqual(
            copied.gameBoard.grid,
            self.original.gameBoard.grid
        )
        self.assertEqual(copied.getScores(), (2, 2))

    def test_copy_preserves_non_initial_board(self):
        self.assertTrue(self.original.makeMove(2, 3))

        copied = self.original.copyGame()

        self.assertEqual(
            copied.gameBoard.grid,
            self.original.gameBoard.grid
        )
        self.assertEqual(copied.getScores(), (4, 1))
        self.assertEqual(copied.currentPlayer, WHITE_DISK)
        self.assertEqual(copied.moveCount, 1)

    def test_copy_preserves_game_attributes(self):
        self.original.makeMove(2, 3)
        copied = self.original.copyGame()

        self.assertEqual(
            copied.currentPlayer,
            self.original.currentPlayer
        )
        self.assertEqual(
            copied.moveCount,
            self.original.moveCount
        )
        self.assertEqual(
            copied.gameOver,
            self.original.gameOver
        )
        self.assertEqual(
            copied.winner,
            self.original.winner
        )

    def test_modifying_copy_does_not_modify_original(self):
        copied = self.original.copyGame()

        copied.gameBoard.grid[3][3] = BLACK_DISK

        self.assertEqual(
            self.original.gameBoard.grid[3][3],
            WHITE_DISK
        )
        self.assertNotEqual(
            copied.gameBoard.grid,
            self.original.gameBoard.grid
        )

    def test_legal_move_on_copy_does_not_change_original(self):
        self.assertTrue(self.original.makeMove(2, 3))

        originalGrid = [
            row.copy() for row in self.original.gameBoard.grid
        ]
        originalTurn = self.original.currentPlayer
        originalMoveCount = self.original.moveCount
        originalScores = self.original.getScores()

        copied = self.original.copyGame()

        self.assertTrue(copied.makeMove(2, 2))

        self.assertEqual(self.original.gameBoard.grid, originalGrid)
        self.assertEqual(self.original.currentPlayer, originalTurn)
        self.assertEqual(self.original.moveCount, originalMoveCount)
        self.assertEqual(self.original.getScores(), originalScores)

        self.assertEqual(copied.moveCount, 2)
        self.assertEqual(copied.currentPlayer, BLACK_DISK)

    def test_original_move_does_not_change_copy(self):
        copied = self.original.copyGame()

        copiedGrid = [
            row.copy() for row in copied.gameBoard.grid
        ]

        self.assertTrue(self.original.makeMove(2, 3))

        self.assertEqual(copied.gameBoard.grid, copiedGrid)
        self.assertEqual(copied.getScores(), (2, 2))
        self.assertEqual(copied.currentPlayer, BLACK_DISK)
        self.assertEqual(copied.moveCount, 0)

    def test_finished_game_state_is_preserved(self):
        self.original.gameOver = True
        self.original.winner = WHITE_DISK
        self.original.moveCount = 60

        copied = self.original.copyGame()

        self.assertTrue(copied.gameOver)
        self.assertEqual(copied.winner, WHITE_DISK)
        self.assertEqual(copied.moveCount, 60)

        copied.winner = BLACK_DISK
        copied.gameOver = False

        self.assertEqual(self.original.winner, WHITE_DISK)
        self.assertTrue(self.original.gameOver)

    def test_resetting_copy_does_not_reset_original(self):
        self.assertTrue(self.original.makeMove(2, 3))

        copied = self.original.copyGame()
        copied.resetGame()

        self.assertEqual(self.original.getScores(), (4, 1))
        self.assertEqual(self.original.moveCount, 1)
        self.assertEqual(self.original.currentPlayer, WHITE_DISK)

        self.assertEqual(copied.getScores(), (2, 2))
        self.assertEqual(copied.moveCount, 0)
        self.assertEqual(copied.currentPlayer, BLACK_DISK)


if __name__ == "__main__":
    unittest.main(verbosity=2)
