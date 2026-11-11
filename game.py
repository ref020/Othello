from board import *

class Game:
    def __init__(self, gameBoard=None):
        self.gameBoard = gameBoard if gameBoard is not None else Board()
        self.currentPlayer = BLACK_DISK
        self.moveCount = 0
        self.gameOver = False
        self.winner = None

    def makeMove(self, row, col):
        if not self.gameOver:
            if self.gameBoard.updateBoard(row, col, self.currentPlayer):
                self.moveCount += 1
                self.advanceTurn()
                return True
            else:
                print(f"Invalid move at ({row}, {col}) for player {self.currentPlayer}.")
                return False
        else:
            print("Game is over. No more moves can be made.")
            return False

    def advanceTurn(self):
        newTurnAvailable = self.gameBoard.getLegalMoves(self.currentPlayer*-1)
        if newTurnAvailable:
            self.currentPlayer *= -1
        else:
            print(f"No legal moves available for player {self.currentPlayer*-1}. Turn remains with player {self.currentPlayer}.")
            if not self.gameBoard.getLegalMoves(self.currentPlayer):
                self.gameOver = True
                self.getWinner()

    def getScores(self):
        return sum(row.count(BLACK_DISK) for row in self.gameBoard.grid), sum(row.count(WHITE_DISK) for row in self.gameBoard.grid)

    def getWinner(self):
        if self.gameOver:    
            blackScore, whiteScore = self.getScores()
            if blackScore > whiteScore:
                self.winner = BLACK_DISK
            elif whiteScore > blackScore:
                self.winner = WHITE_DISK
            else:
                self.winner = 0

    def resetGame(self):
        self.gameBoard = Board()
        self.currentPlayer = BLACK_DISK
        self.moveCount = 0
        self.gameOver = False
        self.winner = None

    def copyGame(self):
        copiedGameBoard = Board()

        originalGrid = self.gameBoard.grid
        copiedGrid = []

        for row in originalGrid:
            copiedGrid.append(row.copy())

        copiedGameBoard.grid = copiedGrid

        copiedGame = Game(copiedGameBoard)

        copiedGame.currentPlayer = self.currentPlayer
        copiedGame.moveCount = self.moveCount
        copiedGame.gameOver = self.gameOver
        copiedGame.winner = self.winner

        return copiedGame