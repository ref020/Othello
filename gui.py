import queue
import threading
import tkinter as tk
from tkinter import messagebox

from ai import OthelloAI
from board import BOARD_SIZE, BLACK_DISK, WHITE_DISK, EMPTY_CELL
from game import Game

# WINDOW AND BOARD SETTINGS
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 780
BOARD_MARGIN = 36
BOARD_BORDER = 8
AI_DELAY_MS = 180

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
    def __init__(self, game=None):
        self.game = game if game is not None else Game()
        self.ai = OthelloAI()
        self.root = tk.Tk()
        self.root.title("Othello")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(400, 440)

        # APPLICATION SETTINGS
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

        # AI SEARCH RESULTS ARE DELIVERED TO THE TKINTER THREAD THROUGH A QUEUE
        self.aiResults = queue.Queue()
        self.searchGeneration = 0
        self.aiPending = False
        self.aiThinking = False
        self.aiAfterId = None
        self.debugWindow = None
        self.debugText = None
        self.lastDebugReport = "No AI search has been completed yet."
        self.closing = False

        self.createMenu()
        self.createLayout()
        self.applyTheme()
        self.updateStatus()

        # KEYBOARD SHORTCUTS AND RESIZING
        self.root.bind("<F11>", self.toggleFullscreen)
        self.root.bind("<Escape>", self.exitFullscreen)
        self.canvas.bind("<Button-1>", self.handleClick)
        self.boardFrame.bind("<Configure>", self.resizeBoard)
        self.root.protocol("WM_DELETE_WINDOW", self.closeWindow)
        self.root.after_idle(self.refreshBoard)
        self.root.after(50, self.pollAIResults)

        # CHANGE OF AI COLOR STARTS A NEW GAME
        self.aiColor.trace_add("write", self.onAIColorChanged)
        self.messageLabel.configure(text="Welcome to Othello!")

    def createMenu(self):
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
        gameMenu.add_command(label="Exit", command=self.closeWindow)
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
        settingsMenu.add_command(label="AI Debug Report...", command=self.openDebugWindow)
        self.menuBar.add_cascade(label="Settings", menu=settingsMenu)

        helpMenu = tk.Menu(self.menuBar, tearoff=False)
        helpMenu.add_command(label="How to Play", command=self.showInstructions)
        helpMenu.add_command(label="About", command=self.showAbout)
        self.menuBar.add_cascade(label="Help", menu=helpMenu)

    def createLayout(self):
        # TOP SCORE AREA
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

        # BOTTOM STATUS AREA
        self.messageFrame = tk.Frame(self.root, height=68)
        self.messageFrame.pack(side=tk.BOTTOM, fill=tk.X)
        self.messageFrame.pack_propagate(False)
        self.messageLabel = tk.Label(self.messageFrame, font=("Segoe UI", 11))
        self.messageLabel.pack(side=tk.TOP, pady=(8, 2))
        self.detailsLabel = tk.Label(self.messageFrame, font=("Segoe UI", 9))
        self.detailsLabel.pack(side=tk.TOP)

        # EXPANDING BOARD AREA
        self.boardFrame = tk.Frame(self.root)
        self.boardFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.boardFrame.pack_propagate(False)
        self.canvas = tk.Canvas(self.boardFrame, borderwidth=BOARD_BORDER,
                                relief="ridge", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def resizeBoard(self, event=None):
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
        self.drawBoard()

    def drawBoard(self):
        self.canvas.delete("all")
        if self.squarePixels <= 0:
            return

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
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = self.game.gameBoard.getCell(row, col)
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
        self.refreshDebugWindow()

    def updateStatus(self):
        blackScore, whiteScore = self.game.getScores()
        self.blackScoreLabel.configure(text=f"Black: {blackScore}")
        self.whiteScoreLabel.configure(text=f"White: {whiteScore}")
        if self.game.gameOver:
            self.turnLabel.configure(text="Game Over!")
            if self.game.winner == BLACK_DISK:
                self.messageLabel.configure(text="Game Over! Black wins!")
            elif self.game.winner == WHITE_DISK:
                self.messageLabel.configure(text="Game Over! White wins!")
            else:
                self.messageLabel.configure(text="Game Over! It's a tie!")
        else:
            self.turnLabel.configure(text=f"Turn: {self.colorName(self.game.currentPlayer)}")
        self.modeLabel.configure(text=self.gameMode.get())
        self.detailsLabel.configure(text=f"AI Depth: {self.aiDepth.get()}  |  "
                                         f"Alpha-Beta: {'On' if self.alphaBetaEnabled.get() else 'Off'}  |  "
                                         f"Debug: {'On' if self.debugEnabled.get() else 'Off'}")

    def colorName(self, color):
        return "Black" if color == BLACK_DISK else "White"

    def getAIColor(self):
        return BLACK_DISK if self.aiColor.get() == "Black" else WHITE_DISK

    def isAITurn(self):
        return (self.gameMode.get() == "Play vs AI" and
                not self.game.gameOver and
                self.game.currentPlayer == self.getAIColor())

    def changeGameMode(self):
        self.newGame()

    def onAIColorChanged(self, *args):
        self.newGame()

    def cancelPendingAI(self):
        # INVALIDATE IN-FLIGHT WORK; WORKER THREADS NEVER MODIFY THE LIVE GAME
        self.searchGeneration += 1
        self.aiPending = False
        self.aiThinking = False
        if self.aiAfterId is not None:
            try:
                self.root.after_cancel(self.aiAfterId)
            except tk.TclError:
                pass
            self.aiAfterId = None

    def newGame(self):
        self.cancelPendingAI()
        self.game.resetGame()
        self.ai = OthelloAI()
        self.lastDebugReport = "No AI search has been completed yet."
        self.refreshDebugWindow()
        self.updateStatus()
        self.refreshBoard()
        self.messageLabel.configure(text="New game started. Black goes first.")
        self.scheduleAITurn()

    def scheduleAITurn(self):
        if self.closing or self.aiPending or not self.isAITurn():
            return
        self.aiPending = True
        self.messageLabel.configure(text=f"Computer ({self.aiColor.get()}) is thinking...")
        self.aiAfterId = self.root.after(AI_DELAY_MS, self.startAISearch)

    def startAISearch(self):
        self.aiAfterId = None
        if self.closing or not self.aiPending or not self.isAITurn():
            self.aiPending = False
            return
        self.aiThinking = True
        generation = self.searchGeneration
        position = self.game.copyGame()
        color = self.getAIColor()
        depth = max(1, int(self.aiDepth.get()))
        useAlphaBeta = bool(self.alphaBetaEnabled.get())

        # SEARCH OFF THE UI THREAD; USE A FRESH AI OBJECT FOR EACH SEARCH
        def searchWorker():
            searchAI = OthelloAI()
            try:
                move = searchAI.chooseMove(position, depth, color, useAlphaBeta)
                self.aiResults.put((generation, move, searchAI, color, depth,
                                    useAlphaBeta, None))
            except Exception as error:
                self.aiResults.put((generation, None, None, color, depth,
                                    useAlphaBeta, error))

        threading.Thread(target=searchWorker, daemon=True).start()

    def pollAIResults(self):
        if self.closing:
            return
        try:
            while True:
                generation, move, searchAI, color, depth, useAlphaBeta, error = self.aiResults.get_nowait()
                if generation != self.searchGeneration or not self.aiPending:
                    continue
                self.aiPending = False
                self.aiThinking = False
                if error is not None:
                    self.messageLabel.configure(text="AI search failed. See error dialog.")
                    messagebox.showerror("AI Search Error", str(error), parent=self.root)
                    continue
                if not self.isAITurn() or self.getAIColor() != color:
                    continue
                self.ai = searchAI
                self.lastDebugReport = self.formatDebugReport(searchAI, color, depth, useAlphaBeta)
                self.refreshDebugWindow()
                if self.debugEnabled.get():
                    print(self.lastDebugReport)
                if move is None:
                    self.messageLabel.configure(text="AI has no legal move.")
                    continue
                if not self.game.makeMove(*move):
                    messagebox.showerror("AI Move Error", f"AI returned illegal move {move}.",
                                         parent=self.root)
                    continue
                self.updateStatus()
                self.refreshBoard()
                if not self.game.gameOver:
                    self.messageLabel.configure(text=f"Computer ({self.colorName(color)}) played {move}.")
                self.scheduleAITurn()
        except queue.Empty:
            pass
        self.root.after(50, self.pollAIResults)

    def formatDebugReport(self, searchAI, color, depth, useAlphaBeta):
        breakdown = searchAI.bestMoveBreakdown
        path = searchAI.bestMovePath
        lines = [
            "OTHELLO AI SEARCH REPORT",
            "=" * 42,
            f"Computer color: {self.colorName(color)}",
            f"Algorithm: {'Alpha-Beta' if useAlphaBeta else 'Mini-Max'}",
            f"Search depth: {depth}",
            f"Selected move: {path[0] if path else 'None'}",
            f"Search score: {searchAI.bestMoveScore}",
            f"Principal variation: {path}",
            "",
            "SEARCH STATISTICS",
            f"Nodes visited: {searchAI.nodesVisited}",
            f"Leaf evaluations: {searchAI.nodesEvaluated}",
            f"Pruning events: {searchAI.pruningEvents}",
            "",
            "EVALUATION AT END OF PREDICTED PATH",
        ]
        if breakdown is None:
            lines.append("No breakdown available.")
        else:
            for key, value in breakdown.items():
                lines.append(f"{key}: {value}")
            if breakdown.get("Evaluated Score") != searchAI.bestMoveScore:
                lines.extend(["", "Note: the reconstructed path's evaluation differs",
                              "from the search bound (possible with alpha-beta pruning)."])
        return "\n".join(lines)

    def openDebugWindow(self):
        if self.debugWindow is not None and self.debugWindow.winfo_exists():
            self.debugWindow.lift()
            self.debugWindow.focus_set()
            return
        self.debugWindow = tk.Toplevel(self.root)
        self.debugWindow.title("AI Debug Report")
        self.debugWindow.geometry("570x530")
        self.debugWindow.minsize(390, 280)
        self.debugText = tk.Text(self.debugWindow, wrap=tk.WORD, font=("Consolas", 10),
                                 padx=12, pady=12)
        scrollBar = tk.Scrollbar(self.debugWindow, command=self.debugText.yview)
        self.debugText.configure(yscrollcommand=scrollBar.set)
        scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
        self.debugText.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.refreshDebugWindow()
        self.debugWindow.protocol("WM_DELETE_WINDOW", self.closeDebugWindow)

    def refreshDebugWindow(self):
        if self.debugWindow is None or not self.debugWindow.winfo_exists():
            return
        self.debugText.configure(state=tk.NORMAL)
        self.debugText.delete("1.0", tk.END)
        self.debugText.insert("1.0", self.lastDebugReport)
        self.debugText.configure(state=tk.DISABLED)

    def closeDebugWindow(self):
        if self.debugWindow is not None:
            self.debugWindow.destroy()
        self.debugWindow = None
        self.debugText = None

    def toggleFullscreen(self, event=None):
        self.isFullscreen = not self.isFullscreen
        self.root.attributes("-fullscreen", self.isFullscreen)

    def exitFullscreen(self, event=None):
        if self.isFullscreen:
            self.isFullscreen = False
            self.root.attributes("-fullscreen", False)

    def openAISettings(self):
        settingsWindow = tk.Toplevel(self.root)
        settingsWindow.title("AI Settings")
        settingsWindow.geometry("350x320")
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
                            "Black moves first. Click an empty square to place a disk. "
                            "A legal move must enclose at least one opponent disk "
                            "in a straight line; enclosed disks flip to your color. "
                            "If a player has no legal move, their turn is skipped. "
                            "The player with the most disks at the end wins.\n\n"
                            "Use Game > Play vs AI to face the computer. "
                            "Choose the computer's color, search depth, and pruning "
                            "under Settings > AI Settings.\n\n"
                            "View the most recent search under Settings > AI Debug Report.",
                            parent=self.root)

    def showAbout(self):
        messagebox.showinfo("About Othello",
                            "Othello — CSC 475 Project\nPython / Tkinter interface",
                            parent=self.root)

    def handleClick(self, event):
        if self.squarePixels <= 0 or self.game.gameOver:
            return
        if self.aiPending or self.isAITurn():
            self.messageLabel.configure(text="Wait for the computer's turn to finish.")
            return

        col = int(event.x // self.squarePixels)
        row = int(event.y // self.squarePixels)
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return

        movingColor = self.game.currentPlayer
        if self.game.makeMove(row, col):
            self.updateStatus()
            self.refreshBoard()
            if not self.game.gameOver:
                self.messageLabel.configure(
                    text=f"Move made at ({row}, {col}) by {self.colorName(movingColor)}.")
            self.scheduleAITurn()
        else:
            self.messageLabel.configure(text=f"Invalid move at ({row}, {col}). Try again.")

    def closeWindow(self):
        self.closing = True
        self.cancelPendingAI()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
