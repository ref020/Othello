#Constants go here
BLACK_DISK = -1
WHITE_DISK = 1
EMPTY_CELL = 0
BOARD_SIZE = 8


class Board:
    def __init__(self):
        self.size = BOARD_SIZE
        self.grid = [[EMPTY_CELL for _ in range(self.size)] for _ in range(self.size)]
        self.startingState()

    #displays current game board in the terminal for testing purposes
    def tempTerminalDisplay(self):
        # Column labels
        print("   ", end="")
        for columnNum in range(self.size):
            print(f"{columnNum:^5}", end="")
        print()

        # Horizontal border
        border = "  +" + "----+" * self.size
        print(border)

        # Board rows
        for rowNum in range(self.size):
            print(f"{rowNum} |", end="")

            for colNum in range(self.size):
                print(f"{str(self.grid[rowNum][colNum]):^4}|", end="")

            print()
            print(border)

    def getCell(self, row, col):
        #returns the value of the cell at the specified row and column
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.grid[row][col]
        #returns an error if the row or column is out of bounds
        else:
            raise IndexError("Cell position out of bounds.")

    def startingState(self):
        self.grid = [[EMPTY_CELL for _ in range(self.size)] for _ in range(self.size)]

        #places the starting disks on the board
        mid = self.size // 2
        self.grid[mid - 1][mid - 1] = WHITE_DISK
        self.grid[mid][mid] = WHITE_DISK
        self.grid[mid - 1][mid] = BLACK_DISK
        self.grid[mid][mid - 1] = BLACK_DISK

    def placeDisk(self, row, col, color):
        #places a disk of the specified color at the specified row and column
        if color != BLACK_DISK and color != WHITE_DISK:
            raise ValueError("Invalid disk color. Use BLACK_DISK or WHITE_DISK.")
        else:
            if 0 <= row < self.size and 0 <= col < self.size:
                if self.grid[row][col] == EMPTY_CELL:
                    self.grid[row][col] = color
                else:
                    raise ValueError("Cell is already occupied.")
            else:
                raise IndexError("Cell position out of bounds.")

    def updateBoard(self, row, col, color):
        flips = self.getFlipsForMove(row, col, color)
        if not flips:
            print(f"No disks to flip for move at ({row}, {col}) with color {color}. Move is invalid.")
            return False
        else:
            self.placeDisk(row, col, color)

            for flipRow, flipCol in flips:
                self.grid[flipRow][flipCol] = color

            print(f"Flipped disks at: {flips}")
            return True


    def getFlipsInDirection(self, row, col, color, rowDirection, colDirection):
        currentRow = row + rowDirection
        currentCol = col + colDirection
        flips = []

        while 0 <= currentRow < self.size and 0 <= currentCol < self.size:
            currentCell = self.grid[currentRow][currentCol]
            if currentCell == EMPTY_CELL:
                return []
            elif currentCell == color:
                return flips
            else:
                flips.append((currentRow, currentCol))
                currentRow += rowDirection
                currentCol += colDirection
        return []

    def getFlipsForMove(self, row, col, color):
        if 0 <= row < self.size and 0 <= col < self.size:
            if self.grid[row][col] != EMPTY_CELL:
                return[]

            flips = []
            directions = [(-1, -1), (-1, 0), (-1, 1),
                          (0, -1),          (0, 1),
                          (1, -1), (1, 0), (1, 1)]

            for rowDirection, colDirection in directions:
                flipsInDirection = self.getFlipsInDirection(row, col, color, rowDirection, colDirection)
                flips.extend(flipsInDirection)
            return flips
        else:
            return []

    def getLegalMoves(self, color):
        legalMoves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == EMPTY_CELL:
                    flips = self.getFlipsForMove(row, col, color)
                    if flips:
                        legalMoves.append((row, col))
        return legalMoves

    def isGameOver(self):
        blackLegalMoves = self.getLegalMoves(BLACK_DISK)
        whiteLegalMoves = self.getLegalMoves(WHITE_DISK)
        return not blackLegalMoves and not whiteLegalMoves