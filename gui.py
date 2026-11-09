import tkinter as tk
from tkinter import messagebox
from board import Board, BOARD_SIZE, BLACK_DISK, WHITE_DISK, EMPTY_CELL

#CONSTANTS
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 780
BOARD_MARGIN = 36
BOARD_BORDER = 8
MIN_BOARD_SIZE = 160

LIGHT_THEME = {
    "background": "#e5edf6", "panel": "#f5f8fc", "text": "#24364b",
    "board": "#27844e", "line": "#14532d", "border": "#b4c4d5",
    "status": "#d3e1f0"
}
DARK_THEME = {
    "background": "#202832", "panel": "#2d3947", "text": "#f1f5f9",
    "board": "#247448", "line": "#103d29", "border": "#5e7186",
    "status": "#35465a"
}


class OthelloGUI:
    def __init__(self, gameBoard=None):
        self.gameBoard = gameBoard if gameBoard is not None else Board()
        self.root = tk.Tk()
        self.root.title("Othello")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(400, 440)

        #APPLICATION SETTINGS
        self.isFullscreen = False
        self.themeName = tk.StringVar(value="Light")
        self.pieceStyle = tk.StringVar(value="Classic")
        self.gameMode = tk.StringVar(value="Local Two Player")
        self.aiColor = tk.StringVar(value="White")
        self.aiDepth = tk.IntVar(value=3)
        self.alphaBetaEnabled = tk.BooleanVar(value=True)
        self.debugEnabled = tk.BooleanVar(value=False)
        self.squarePixels = 0
        self.boardPixels = 0
        self.colors = LIGHT_THEME

        #BUILD WINDOW COMPONENTS
        self.createMenu()
        self.createLayout()
        self.applyTheme()
        self.updateStatus()

        #KEYBOARD SHORTCUTS AND RESIZING
        self.root.bind("<F11>", self.toggleFullscreen)
        self.root.bind("<Escape>", self.exitFullscreen)
        self.boardFrame.bind("<Configure>", self.resizeBoard)
        self.root.after_idle(self.refreshBoard)

    def createMenu(self):
        #CREATE NATIVE DESKTOP MENU BAR
        self.menuBar = tk.Menu(self.root)
        self.root.config(menu=self.menuBar)

        gameMenu = tk.Menu(self.menuBar, tearoff=False)
        gameMenu.add_radiobutton(label="Local Two Player", variable=self.gameMode,
                                 value="Local Two Player", command=self.changeGameMode)
        gameMenu.add_radiobutton(label="Play vs AI", variable=self.gameMode,
                                 value="Play vs AI", command=self.changeGameMode)
        gameMenu.add_separator()
        gameMenu.add_command(label="New Game", command=self.newGame)
        gameMenu.add_command(label="Fullscreen (F11)", command=self.toggleFullscreen)
        gameMenu.add_separator()
        gameMenu.add_command(label="Exit", command=self.root.destroy)
        self.menuBar.add_cascade(label="Game", menu=gameMenu)

        settingsMenu = tk.Menu(self.menuBar, tearoff=False)
        themeMenu = tk.Menu(settingsMenu, tearoff=False)
        for themeName in ("Light", "Dark"):
            themeMenu.add_radiobutton(label=themeName, variable=self.themeName,
                                      value=themeName, command=self.applyTheme)
        settingsMenu.add_cascade(label="Theme", menu=themeMenu)

        pieceMenu = tk.Menu(settingsMenu, tearoff=False)
        for styleName in ("Classic", "Flat", "Glossy"):
            pieceMenu.add_radiobutton(label=styleName, variable=self.pieceStyle,
                                      value=styleName, command=self.refreshBoard)
        settingsMenu.add_cascade(label="Piece Design", menu=pieceMenu)
        settingsMenu.add_separator()
        settingsMenu.add_command(label="AI Settings...", command=self.openAISettings)
        self.menuBar.add_cascade(label="Settings", menu=settingsMenu)

        helpMenu = tk.Menu(self.menuBar, tearoff=False)
        helpMenu.add_command(label="How to Play", command=self.showInstructions)
        helpMenu.add_command(label="About", command=self.showAbout)
        self.menuBar.add_cascade(label="Help", menu=helpMenu)

    def createLayout(self):
        #TOP SCORE AREA
        self.scoreFrame = tk.Frame(self.root, height=100)
        self.scoreFrame.pack(side=tk.TOP, fill=tk.X)
        self.scoreFrame.pack_propagate(False)
        self.blackScoreLabel = tk.Label(self.scoreFrame, font=("Segoe UI", 16, "bold"))
        self.blackScoreLabel.pack(side=tk.LEFT, padx=24)
        self.whiteScoreLabel = tk.Label(self.scoreFrame, font=("Segoe UI", 16, "bold"))
        self.whiteScoreLabel.pack(side=tk.RIGHT, padx=24)
        self.turnLabel = tk.Label(self.scoreFrame, font=("Segoe UI", 14))
        self.turnLabel.pack(side=tk.TOP, pady=15)
        self.modeLabel = tk.Label(self.scoreFrame, font=("Segoe UI", 10))
        self.modeLabel.pack(side=tk.TOP)

        #BOTTOM STATUS AREA
        self.messageFrame = tk.Frame(self.root, height=68)
        self.messageFrame.pack(side=tk.BOTTOM, fill=tk.X)
        self.messageFrame.pack_propagate(False)
        self.messageLabel = tk.Label(self.messageFrame, font=("Segoe UI", 11))
        self.messageLabel.pack(side=tk.TOP, pady=(8, 2))
        self.detailsLabel = tk.Label(self.messageFrame, font=("Segoe UI", 9))
        self.detailsLabel.pack(side=tk.TOP)

        #EXPANDING BOARD AREA
        self.boardFrame = tk.Frame(self.root)
        self.boardFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.boardFrame.pack_propagate(False)
        self.canvas = tk.Canvas(self.boardFrame, borderwidth=BOARD_BORDER,
                                relief="ridge", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def resizeBoard(self, event=None):
        #USE THE SMALLER AVAILABLE DIMENSION TO KEEP THE BOARD SQUARE
        frameWidth = self.boardFrame.winfo_width()
        frameHeight = self.boardFrame.winfo_height()
        newPixels = max(1, min(frameWidth, frameHeight) - BOARD_MARGIN - 2 * BOARD_BORDER)
        if newPixels == self.boardPixels:
            return
        self.boardPixels = newPixels
        self.squarePixels = newPixels / BOARD_SIZE
        self.canvas.configure(width=newPixels, height=newPixels)
        self.drawBoard()

    def refreshBoard(self):
        #REDRAW AFTER A PIECE STYLE OR THEME CHANGE
        self.drawBoard()

    def drawBoard(self):
        #CLEAR ALL OLD CANVAS ITEMS BEFORE REDRAWING
        self.canvas.delete("all")
        if self.squarePixels <= 0:
            return

        #DRAW THE EIGHT BY EIGHT GRID
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = col * self.squarePixels
                y1 = row * self.squarePixels
                x2 = x1 + self.squarePixels
                y2 = y1 + self.squarePixels
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=self.colors["board"],
                                             outline=self.colors["line"], width=1)
        self.drawDisks()

    def drawDisks(self):
        #RENDER DISCS FROM THE BOARD MODEL, NOT A SECOND GUI BOARD
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = self.gameBoard.getCell(row, col)
                if color == EMPTY_CELL:
                    continue
                margin = self.squarePixels * 0.12
                x1 = col * self.squarePixels + margin
                y1 = row * self.squarePixels + margin
                x2 = (col + 1) * self.squarePixels - margin
                y2 = (row + 1) * self.squarePixels - margin
                fillColor = "#17191e" if color == BLACK_DISK else "#f6f7f9"
                edgeColor = "#050607" if color == BLACK_DISK else "#b8c1cb"
                styleName = self.pieceStyle.get()

                if styleName == "Flat":
                    self.canvas.create_oval(x1, y1, x2, y2, fill=fillColor,
                                            outline=fillColor)
                else:
                    self.canvas.create_oval(x1, y1, x2, y2, fill=fillColor,
                                            outline=edgeColor, width=max(1, self.squarePixels * 0.025))
                    if styleName == "Classic":
                        inset = self.squarePixels * 0.09
                        self.canvas.create_oval(x1 + inset, y1 + inset,
                                                x2 - inset, y2 - inset,
                                                outline="#484c52" if color == BLACK_DISK else "#d3d9e0",
                                                width=max(1, self.squarePixels * 0.02))
                    elif styleName == "Glossy":
                        self.canvas.create_oval(x1 + self.squarePixels * 0.14,
                                                y1 + self.squarePixels * 0.10,
                                                x1 + self.squarePixels * 0.42,
                                                y1 + self.squarePixels * 0.24,
                                                fill="#6b7077" if color == BLACK_DISK else "#ffffff",
                                                outline="")

    def applyTheme(self):
        #CHANGE WIDGET COLORS WITHOUT ALTERING GAME DATA
        self.colors = LIGHT_THEME if self.themeName.get() == "Light" else DARK_THEME
        self.root.configure(bg=self.colors["background"])
        self.scoreFrame.configure(bg=self.colors["panel"])
        self.messageFrame.configure(bg=self.colors["status"])
        self.boardFrame.configure(bg=self.colors["background"])
        self.canvas.configure(bg=self.colors["border"])
        for label in (self.blackScoreLabel, self.whiteScoreLabel,
                      self.turnLabel, self.modeLabel):
            label.configure(bg=self.colors["panel"], fg=self.colors["text"])
        for label in (self.messageLabel, self.detailsLabel):
            label.configure(bg=self.colors["status"], fg=self.colors["text"])
        self.refreshBoard()

    def updateStatus(self):
        #READ SCORES DIRECTLY FROM THE CURRENT BOARD
        blackScore = sum(row.count(BLACK_DISK) for row in self.gameBoard.grid)
        whiteScore = sum(row.count(WHITE_DISK) for row in self.gameBoard.grid)
        self.blackScoreLabel.configure(text=f"Black: {blackScore}")
        self.whiteScoreLabel.configure(text=f"White: {whiteScore}")
        self.turnLabel.configure(text="Black's Turn")
        self.modeLabel.configure(text=self.gameMode.get())
        self.messageLabel.configure(text="Welcome to Othello!")
        self.detailsLabel.configure(text=f"AI Depth: {self.aiDepth.get()}  |  "
                                         f"Alpha-Beta: {'On' if self.alphaBetaEnabled.get() else 'Off'}  |  "
                                         f"Debug: {'On' if self.debugEnabled.get() else 'Off'}")

    def changeGameMode(self):
        #MODE SELECTION IS SAVED; GAME CONTROLLER WILL USE IT LATER
        self.updateStatus()
        self.messageLabel.configure(text=f"Selected: {self.gameMode.get()}")

    def newGame(self):
        #RESET THE BOARD WITHOUT IMPLEMENTING TURN LOGIC YET
        self.gameBoard.startingState()
        self.updateStatus()
        self.refreshBoard()

    def toggleFullscreen(self, event=None):
        #F11 TO ENTER OR EXIT FULLSCREEN
        self.isFullscreen = not self.isFullscreen
        self.root.attributes("-fullscreen", self.isFullscreen)

    def exitFullscreen(self, event=None):
        #ESCAPE RETURNS TO WINDOWED MODE
        if self.isFullscreen:
            self.isFullscreen = False
            self.root.attributes("-fullscreen", False)

    def openAISettings(self):
        #OPEN A NONMODAL SETTINGS WINDOW
        settingsWindow = tk.Toplevel(self.root)
        settingsWindow.title("AI Settings")
        settingsWindow.geometry("350x300")
        settingsWindow.resizable(False, False)
        settingsWindow.transient(self.root)
        frame = tk.Frame(settingsWindow, padx=18, pady=16)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="AI Search Depth", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        depthScale = tk.Scale(frame, from_=1, to=6, orient=tk.HORIZONTAL,
                              resolution=1, variable=self.aiDepth,
                              command=lambda value: self.updateStatus())
        depthScale.pack(fill=tk.X)
        tk.Label(frame, text="Higher depths can take much longer to search.",
                 font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 12))
        tk.Label(frame, text="Computer plays as:").pack(anchor=tk.W)
        tk.OptionMenu(frame, self.aiColor, "Black", "White").pack(anchor=tk.W)
        tk.Checkbutton(frame, text="Enable Alpha-Beta Pruning",
                       variable=self.alphaBetaEnabled,
                       command=self.updateStatus).pack(anchor=tk.W, pady=(8, 0))
        tk.Checkbutton(frame, text="Enable Debug Output",
                       variable=self.debugEnabled,
                       command=self.updateStatus).pack(anchor=tk.W)
        tk.Button(frame, text="Close", command=settingsWindow.destroy).pack(pady=(14, 0))

    def showInstructions(self):
        messagebox.showinfo("How to Play",
                            "Players alternate placing discs. A legal move must enclose "
                            "at least one opponent disc in a straight line. Enclosed "
                            "discs flip to the current player's color. The player "
                            "with the most discs at the end wins.\n\n"
                            "Move input will be added in the next milestone.",
                            parent=self.root)

    def showAbout(self):
        messagebox.showinfo("About Othello",
                            "Othello — CSC 475 Project\nPython / Tkinter interface",
                            parent=self.root)

    def run(self):
        #START THE TKINTER EVENT LOOP
        self.root.mainloop()