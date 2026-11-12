# Temporary test code for Othello AI search statistics.
# Do not include this file in the assignment submission.

import time
import unittest

from ai import OthelloAI
from game import Game


class TestSearchStatistics(unittest.TestCase):
    def test_minimax_vs_alpha_beta(self):
        depth = 4
        game = Game()
        ai = OthelloAI()
        aiColor = game.currentPlayer
        originalGrid = [row.copy() for row in game.gameBoard.grid]
        originalPlayer = game.currentPlayer

        results = {}
        for algorithm, useAlphaBeta in (("Mini-Max", False), ("Alpha-Beta", True)):
            startTime = time.perf_counter()
            move = ai.chooseMove(game, depth, aiColor, useAlphaBeta)
            elapsed = time.perf_counter() - startTime

            results[algorithm] = {
                "move": move,
                "visited": ai.nodesVisited,
                "evaluated": ai.nodesEvaluated,
                "pruning": ai.pruningEvents,
                "time": elapsed,
            }

            self.assertIn(move, game.gameBoard.getLegalMoves(aiColor))
            self.assertGreater(ai.nodesEvaluated, 0)
            self.assertGreaterEqual(ai.nodesVisited, ai.nodesEvaluated)
            self.assertEqual(game.gameBoard.grid, originalGrid)
            self.assertEqual(game.currentPlayer, originalPlayer)

        plain = results["Mini-Max"]
        pruned = results["Alpha-Beta"]

        self.assertEqual(plain["move"], pruned["move"])
        self.assertEqual(plain["pruning"], 0)
        self.assertLessEqual(pruned["visited"], plain["visited"])
        self.assertLessEqual(pruned["evaluated"], plain["evaluated"])
        self.assertGreater(pruned["pruning"], 0)

        print(f"\nSearch depth: {depth}")
        print(f"{'Algorithm':<14} {'Move':<12} {'Visited':>9} {'Evaluated':>11} {'Cutoffs':>9} {'Time (s)':>10}")
        for algorithm, data in results.items():
            print(f"{algorithm:<14} {str(data['move']):<12} {data['visited']:>9} {data['evaluated']:>11} {data['pruning']:>9} {data['time']:>10.4f}")

        if plain["evaluated"]:
            saved = 100 * (plain["evaluated"] - pruned["evaluated"]) / plain["evaluated"]
            print(f"Leaf evaluations saved by alpha-beta: {saved:.1f}%")


if __name__ == "__main__":
    unittest.main()
