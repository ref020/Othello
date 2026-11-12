# Standalone tests only; do not submit as assignment implementation.
import contextlib
import io
import unittest

from ai import OthelloAI
from game import Game
from board import BLACK_DISK, WHITE_DISK


class TestPrincipalVariation(unittest.TestCase):
    DEPTH = 4

    def makePosition(self, aiColor):
        game = Game()
        if aiColor == WHITE_DISK:
            # Make a legal opening move so White is to play.
            opening = game.gameBoard.getLegalMoves(game.currentPlayer)[0]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(game.makeMove(*opening))
        self.assertEqual(game.currentPlayer, aiColor)
        return game

    def search(self, game, aiColor, useAlphaBeta):
        ai = OthelloAI()
        originalGrid = [row.copy() for row in game.gameBoard.grid]
        originalState = (game.currentPlayer, game.moveCount, game.gameOver, game.winner)
        with contextlib.redirect_stdout(io.StringIO()):
            move = ai.chooseMove(game, self.DEPTH, aiColor, useAlphaBeta)
        self.assertEqual(game.gameBoard.grid, originalGrid, 'Search modified the original board')
        self.assertEqual((game.currentPlayer, game.moveCount, game.gameOver, game.winner), originalState,
                         'Search modified the original game state')
        self.assertIn(move, game.gameBoard.getLegalMoves(aiColor))
        self.assertIsInstance(ai.bestMoveScore, (int, float))
        self.assertIsInstance(ai.bestMovePath, list)
        self.assertGreaterEqual(len(ai.bestMovePath), 1)
        self.assertLessEqual(len(ai.bestMovePath), self.DEPTH)
        self.assertEqual(ai.bestMovePath[0], move)
        self.assertGreaterEqual(ai.nodesVisited, ai.nodesEvaluated)
        self.assertGreater(ai.nodesEvaluated, 0)
        if not useAlphaBeta:
            self.assertEqual(ai.pruningEvents, 0)

        # Replay the predicted moves on a separate copy, including automatic passes.
        replay = game.copyGame()
        with contextlib.redirect_stdout(io.StringIO()):
            for index, step in enumerate(ai.bestMovePath):
                self.assertFalse(replay.gameOver, f'Path continues after game over at index {index}')
                self.assertIn(step, replay.gameBoard.getLegalMoves(replay.currentPlayer),
                              f'Illegal predicted move {step} at index {index}')
                self.assertTrue(replay.makeMove(*step))
        return move, ai.bestMoveScore, ai.bestMovePath, ai

    def test_black_and_white(self):
        for aiColor, name in ((BLACK_DISK, 'Black'), (WHITE_DISK, 'White')):
            with self.subTest(color=name):
                game = self.makePosition(aiColor)
                plain = self.search(game, aiColor, False)
                pruned = self.search(game, aiColor, True)
                self.assertEqual(plain[0], pruned[0], 'Algorithms chose different moves')
                self.assertEqual(plain[1], pruned[1], 'Algorithms gave different best scores')
                print(f'\n{name} at depth {self.DEPTH}:')
                print(f'  Mini-Max:   move={plain[0]}, score={plain[1]}, path={plain[2]}')
                print(f'  Alpha-Beta: move={pruned[0]}, score={pruned[1]}, path={pruned[2]}')
                print(f'  Nodes visited: {plain[3].nodesVisited} vs {pruned[3].nodesVisited}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
