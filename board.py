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
        #updates the board after a move is made
        self.placeDisk(row, col, color)
        # Additional logic to flip opponent's disks would go here