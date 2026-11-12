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
        self.nodesEvaluated = 0
        self.nodesVisited = 0
        self.pruningEvents = 0
        self.bestMoveScore = None
        self.bestMovePath = []
        self.bestMoveBreakdown = None

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
    
    def minimax(self, game, depth, aiColor, isMaximizing):
        self.nodesVisited += 1
        if depth == 0 or game.gameOver == True:
            self.nodesEvaluated += 1
            return (self.evaluateGame(game, aiColor), [])
        else:
            if isMaximizing:
                bestScore = float("-inf")
            else:
                bestScore = float("inf")

            bestPath = []

            legalMoves = game.gameBoard.getLegalMoves(game.currentPlayer)

            if legalMoves:
                for row, col in legalMoves:
                    copiedGame = game.copyGame()
                    copiedGame.makeMove(row, col)
                    
                    score, childPath = self.minimax(copiedGame, depth - 1, aiColor, copiedGame.currentPlayer == aiColor)
                    currentMove = [(row, col)]

                    if isMaximizing:
                        if score > bestScore:
                            bestScore = score
                            bestPath = currentMove + childPath
                    else:
                        if score < bestScore:
                            bestScore = score
                            bestPath = currentMove + childPath                    
                    
                return (bestScore, bestPath)
            else:
                gameCopy = game.copyGame()

                if gameCopy.gameBoard.getLegalMoves(-gameCopy.currentPlayer):
                    gameCopy.currentPlayer *= -1
                    return self.minimax(gameCopy, depth, aiColor, gameCopy.currentPlayer == aiColor)
                else:
                    gameCopy.gameOver = True
                    gameCopy.getWinner()
                    self.nodesEvaluated += 1
                    return (self.evaluateGame(gameCopy, aiColor), [])

    def chooseMove(self, game, depth, aiColor, useAlphaBeta):
        options = game.gameBoard.getLegalMoves(aiColor)
        self.nodesEvaluated = 0
        self.nodesVisited = 0
        self.pruningEvents = 0
        self.bestMoveScore = None
        self.bestMovePath = []
        self.bestMoveBreakdown = None

        if not options:
            return None
        else:
            bestMove = None
            bestScore = float("-inf")

            for row, col in options:
                copyForMove = game.copyGame()
                copyForMove.makeMove(row, col)

                testedScore, testedPath = self.minimax(copyForMove, depth - 1, aiColor, copyForMove.currentPlayer == aiColor) if not useAlphaBeta else self.minimaxAlphaBeta(copyForMove, depth - 1, aiColor, copyForMove.currentPlayer == aiColor, bestScore, float("inf"))

                if testedScore > bestScore:
                    bestScore = testedScore
                    bestMove = (row, col)
                    self.bestMovePath = [(row, col)] + testedPath
            
            self.bestMoveScore = bestScore
            self.calculateBestMoveBreakdown(game, aiColor)
            return bestMove

    def minimaxAlphaBeta(self, game, depth, aiColor, isMaximizing, alpha, beta):
        self.nodesVisited += 1
        if depth == 0 or game.gameOver == True:
            self.nodesEvaluated += 1
            return (self.evaluateGame(game, aiColor), [])
        else:
            if isMaximizing:
                bestScore = float("-inf")
            else:
                bestScore = float("inf")

            bestPath = []

            legalMoves = game.gameBoard.getLegalMoves(game.currentPlayer)

            if legalMoves:
                for row, col in legalMoves:
                    copiedGame = game.copyGame()
                    copiedGame.makeMove(row, col)
                    
                    score, childPath = self.minimaxAlphaBeta(copiedGame, depth - 1, aiColor, copiedGame.currentPlayer == aiColor, alpha, beta)
                    currentMove = [(row, col)]

                    if isMaximizing:
                        if score > bestScore:
                            bestScore = score
                            bestPath = currentMove + childPath
                        alpha = max(bestScore, alpha)
                    else:
                        if score < bestScore:
                            bestScore = score
                            bestPath = currentMove + childPath
                        beta = min(bestScore, beta)

                    if beta <= alpha:
                        self.pruningEvents += 1
                        break

                return (bestScore, bestPath)
            else:
                gameCopy = game.copyGame()

                if gameCopy.gameBoard.getLegalMoves(-gameCopy.currentPlayer):
                    gameCopy.currentPlayer *= -1
                    return self.minimaxAlphaBeta(gameCopy, depth, aiColor, gameCopy.currentPlayer == aiColor, alpha, beta)
                else:
                    gameCopy.gameOver = True
                    gameCopy.getWinner()
                    self.nodesEvaluated += 1
                    return (self.evaluateGame(gameCopy, aiColor), [])


    def getEvalBreakdown(self, game, aiColor):
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

        heuristicTotal =  (DISK_WEIGHT * diskDifference) + (MOBILITY_WEIGHT * mobilityDifference) + (CORNER_WEIGHT * cornerOwnershipDifference) + (POSITIONAL_WEIGHT_MULT * positionalDifference)
        totalScore = self.evaluateGame(game, aiColor)

        breakdown = {
            "Disk Difference" : diskDifference,
            "Weighted Disk Difference" : (DISK_WEIGHT * diskDifference),
            "Mobility Difference" : mobilityDifference,
            "Weighted Mobility Difference" : (MOBILITY_WEIGHT * mobilityDifference),
            "Corner Ownership Difference" : cornerOwnershipDifference,
            "Weighted Corner Ownership Difference" : (CORNER_WEIGHT * cornerOwnershipDifference),
            "Positional Difference" : positionalDifference,
            "Weighted Positional Difference" : (POSITIONAL_WEIGHT_MULT * positionalDifference),
            "Heuristic Total Score" : heuristicTotal,
            "Evaluated Score" : totalScore
        }

        return breakdown

    def calculateBestMoveBreakdown(self, game, aiColor):
        breakdownCopy = game.copyGame()

        for row, col in self.bestMovePath:
            if not breakdownCopy.makeMove(row, col):
                raise ValueError (f"Invalid move in principal variation: ({row}, {col})")

        self.bestMoveBreakdown = self.getEvalBreakdown(breakdownCopy, aiColor)

        return self.bestMoveBreakdown