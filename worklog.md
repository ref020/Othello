# Othello Project — Research & Development Worklog

**Course:** CSC 475 | **Language:** Python 3.14 / Tkinter  
**Purpose:** Brief record of concepts researched or discussed while developing the Othello game and AI.

> The Google searches below are **suggested search phrases that reflect topics covered during development**, not a claim that every phrase was searched previously. The linked documentation was checked while preparing this log. Implementation details should be verified against the project's source files.

## 1. Python and project structure

| Google search phrase | Concept applied |
| --- | --- |
| `Python classes self instance attributes __init__` | Organized `Board`, `Game`, `OthelloAI`, and `OthelloGUI` as separate classes; distinguished instance attributes from class attributes. |
| `Python import class from another file` | Connected `main.py`, `board.py`, `game.py`, `ai.py`, and `gui.py` with module imports. |
| `Python 2D list copy nested lists` | Copied board grids so simulated AI moves do not modify the real game. |
| `Python tuple unpacking return multiple values` | Returned `(score, path)` from search functions and unpacked the results in `chooseMove()`. |
| `Python dictionary keys values example` | Stored raw and weighted heuristic components in an evaluation breakdown dictionary. |

## 2. Othello game rules and board logic

| Google search phrase | Concept applied |
| --- | --- |
| `Othello Reversi legal moves eight directions` | Checked legal placement by searching in eight directions for bracketed opponent disks. |
| `Othello rules pass turn no legal moves game over` | Automatically passed when the current player had no legal move; ended the game when neither player could move. |
| `Python enumerate grid row column tkinter canvas click coordinates` | Mapped canvas mouse coordinates to board row and column; redrew the board from the game state. |

## 3. AI search and evaluation

| Google search phrase | Concept applied |
| --- | --- |
| `minimax algorithm maximizing minimizing player Python` | Explored future moves recursively and chose the best score from the AI player's perspective. |
| `alpha beta pruning minimax alpha beta cutoff` | Used alpha/beta bounds to skip branches that cannot improve the current decision. |
| `Othello evaluation function mobility corners positional weights` | Evaluated positions using disk difference, legal-move mobility, corner control, and positional square weights. |
| `minimax principal variation best move path` | Recorded the predicted move sequence alongside the search score. |
| `minimax search depth terminal evaluation` | Distinguished heuristic scores for unfinished positions from win/loss/tie scores at terminal positions. |

**Debugging decisions:** `chooseMove()` stores the selected move score, principal variation, visited/evaluated node counts, and pruning count. A copied game replays the principal variation to calculate the final position's heuristic breakdown. Alpha-beta may return bounds from pruned subtrees, so a reported path should not automatically be treated as a fully explored proof of optimal play.

## 4. Tkinter interface and responsiveness

| Google search phrase | Concept applied |
| --- | --- |
| `tkinter canvas resize redraw bind configure event` | Kept the board square while resizing the window; drew disks and grid lines on a canvas. |
| `tkinter Menu radiobutton StringVar BooleanVar IntVar` | Added game mode, AI color, search depth, pruning, theme, and piece-style controls. |
| `tkinter variable trace_add write callback` | Discussed restarting a game when the selected AI color changes. |
| `tkinter after after_cancel schedule callback` | Scheduled AI actions and considered cancellation during game resets. |
| `tkinter threading long running task mainloop freeze` | Moved potentially slow AI search away from the GUI event handler; GUI updates should remain on the Tk event-loop thread. |

## 5. Testing and verification

| Google search phrase | Concept applied |
| --- | --- |
| `Python unittest test cases assertEqual assertTrue` | Used separate test scripts to check board/game behavior, search correctness, and evaluation results. |
| `python -m unittest verbose command` | Ran tests with `python -m unittest <test_file>.py -v`. |
| `Python compare minimax alpha beta node counts` | Compared selected moves, scores, visited nodes, and pruning efficiency. |

**Observed checkpoints:** Depth-4 Mini-Max and alpha-beta agreed on the tested black and white moves. Principal-variation tests passed; evaluation-breakdown tests passed (5 tests); best-move breakdown integration tests passed (4 tests). These results do not substitute for full-game GUI testing.

## Reference documentation

- Python Tkinter documentation: https://docs.python.org/3/library/tkinter.html
- Python `copy` documentation: https://docs.python.org/3/library/copy.html
- Python `unittest` documentation: https://docs.python.org/3/library/unittest.html
- Python `threading` documentation: https://docs.python.org/3/library/threading.html

**Development note:** This log summarizes concepts, guidance, and test milestones. It is not a verbatim browser history or a claim that the project was completed without assistance.
