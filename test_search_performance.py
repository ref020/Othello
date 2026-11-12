# Temporary performance test for Othello AI; not part of the submitted game.
import contextlib
import io
import time
import unittest

from ai import OthelloAI
from board import BLACK_DISK
from game import Game


class TestSearchPerformance(unittest.TestCase):
    def test_compare_minimax_and_alpha_beta(self):
        depth = 4
        game = Game()
        ai = OthelloAI()
        originalGrid = [row.copy() for row in game.gameBoard.grid]
        originalPlayer = game.currentPlayer

        results = {}
        for useAlphaBeta, label in ((False, "Mini-Max"), (True, "Alpha-Beta")):
            # Hide move-by-move board debugging during the search.
            with contextlib.redirect_stdout(io.StringIO()):
                start = time.perf_counter()
                move = ai.chooseMove(game, depth, BLACK_DISK, useAlphaBeta)
                elapsed = time.perf_counter() - start

            results[label] = {
                "move": move,
                "evaluations": ai.nodesEvaluated,
                "seconds": elapsed,
            }

        plain = results["Mini-Max"]
        pruned = results["Alpha-Beta"]
        reduction = (100 * (plain["evaluations"] - pruned["evaluations"]) /
                     plain["evaluations"] if plain["evaluations"] else 0)

        print(f"\nSearch depth: {depth}")
        print(f"{'Algorithm':<15} {'Chosen move':<15} {'Evaluations':>12} {'Time (s)':>12}")
        for label, result in results.items():
            print(f"{label:<15} {str(result['move']):<15} "
                  f"{result['evaluations']:>12,} {result['seconds']:>12.4f}")
        print(f"Leaf evaluations saved by alpha-beta: {reduction:.1f}%")

        self.assertIn(plain["move"], game.gameBoard.getLegalMoves(BLACK_DISK))
        self.assertEqual(plain["move"], pruned["move"],
                         "Both search methods should choose the same move")
        self.assertGreater(plain["evaluations"], 0)
        self.assertGreater(pruned["evaluations"], 0)
        self.assertLessEqual(pruned["evaluations"], plain["evaluations"],
                             "Alpha-beta should not evaluate more leaves here")
        self.assertEqual(game.gameBoard.grid, originalGrid,
                         "Searching must not modify the original board")
        self.assertEqual(game.currentPlayer, originalPlayer)


if __name__ == "__main__":
    unittest.main(verbosity=2)
