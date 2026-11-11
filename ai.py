from board import *
from game import *

# Weights for each factor
DISK_WEIGHT = 1
MOBILITY_WEIGHT = 5
CORNER_WEIGHT = 25
POSITIONAL_WEIGHT_MULT = 1

class OthelloAI:
    def __init__(self):
        self.positionalWeights = [[100, -20, 10, 5, 5, 10, -20, 100], 
                                  [-20, -50, -2, -2, -2, -2, -50, -20], 
                                  [10, -2, 1, 1, 1, 1, -2, 10], 
                                  [5, -2, 1, 0, 0, 1, -2, 5], 
                                  [5, -2, 1, 0, 0, 1, -2, 5], 
                                  [10, -2, 1, 1, 1, 1, -2, 10], 
                                  [-20, -50, -2, -2, -2, -2, -50, -20], 
                                  [100, -20, 10, 5, 5, 10, -20, 100]
                                  ]

    def evaluateGame(self, game, aiColor):
        if game.gameOver:
            return 100000 if game.winner == aiColor else -100000 if game.winner == -aiColor else 0
        
        scores = game.getScores()
        if aiColor == BLACK_DISK:
            diskDifference = scores[0] - scores[1]
        else:
            diskDifference = scores[1] - scores[0]

        mobilityDifference = len(game.gameBoard.getLegalMoves(aiColor)) - len(game.gameBoard.getLegalMoves(-aiColor))

        cornerOwnershipDifference = 0
        corners = [(0, 0), (0, BOARD_SIZE - 1), (BOARD_SIZE - 1, 0), (BOARD_SIZE - 1, BOARD_SIZE - 1)]
        for corner in corners:
            cornerValue = game.gameBoard.getCell(corner[0], corner[1])
            if cornerValue == aiColor:
                cornerOwnershipDifference += 1
            elif cornerValue == -aiColor:
                cornerOwnershipDifference -= 1

        positionalDifference = 0
        for row in range(game.gameBoard.size):
            for col in range(game.gameBoard.size):
                if game.gameBoard.getCell(row, col) == aiColor:
                    positionalDifference += self.positionalWeights[row][col]
                elif game.gameBoard.getCell(row, col) == -aiColor:
                    positionalDifference -= self.positionalWeights[row][col]

        totalScore =  (DISK_WEIGHT * diskDifference) + (MOBILITY_WEIGHT * mobilityDifference) + (CORNER_WEIGHT * cornerOwnershipDifference) + (POSITIONAL_WEIGHT_MULT * positionalDifference)

        return totalScore
    
        