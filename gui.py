import threading
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from image import extractSudoku
from sudoku import Sudoku
from oldsudoku import OldSudoku


labels = [[] for _ in range(9)]

extractedSudoku = None
solver = None


# -------------------------
# Root
# -------------------------

root = Tk()
root.title("Sudoku Solver")
root.geometry("650x900")
root.configure(bg="#f5f5f5")


# -------------------------
# Events
# -------------------------

def showBeginSolving():
    solveLinearButton.pack(side=LEFT, padx=5)
    solveEfficientButton.pack(side=LEFT, padx=5)


def hideBeginSolving():
    solveLinearButton.pack_forget()
    solveEfficientButton.pack_forget()


def showSudokuInvalidErrorMessage():
    errorMessage.pack(pady=(5, 0))


def hideSudokuInvalidErrorMessage():
    errorMessage.pack_forget()


def showLoading():
    uploadSudokuButton.config(state="disabled")

    loadingLabel.pack(side=LEFT, padx=(10, 5))
    loadingBar.pack(side=LEFT, padx=5)

    loadingBar.start(10)


def hideLoading():
    loadingBar.stop()

    loadingBar.pack_forget()
    loadingLabel.pack_forget()

    uploadSudokuButton.config(state="normal")


def solveStep():
    global solver

    try:
        row, col, value = next(solver)

        labels[row][col].config(
            text="" if value is None else value
        )

        root.after(1, solveStep)

    except StopIteration:
        print("Solved")


def solveLinearly(event=None):
    global solver

    try:
        sudokuBrain = OldSudoku(extractedSudoku)
        solver = sudokuBrain.solve()

        beginSolving()

    except Exception as e:
        showSudokuInvalidErrorMessage()


def solveMostEfficient(event=None):
    global solver

    try:
        sudokuBrain = Sudoku(extractedSudoku)
        solver = sudokuBrain.solveSteps()

        beginSolving()

    except Exception as e:
        showSudokuInvalidErrorMessage()


def printInitialSudoku():
    for rowIndex, row in enumerate(extractedSudoku):
        for colIndex, number in enumerate(row):
            labels[rowIndex][colIndex].config(
                text="" if number is None else number
            )

    root.update()


def beginSolving():
    root.after(1, solveStep)

    hideBeginSolving()


def uploadAction(event=None):
    hideSudokuInvalidErrorMessage()
    hideBeginSolving()

    filename = filedialog.askopenfilename(
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg"),
            ("All files", "*.*")
        ]
    )

    if not filename:
        return

    showLoading()

    threading.Thread(
        target=extractSudokuInBackground,
        args=(filename,),
        daemon=True
    ).start()


def extractSudokuInBackground(filename):
    try:
        sudoku = extractSudoku(filename)

        root.after(
            0,
            lambda: uploadComplete(sudoku)
        )

    except Exception as e:
        root.after(
            0,
            uploadFailed
        )


def uploadComplete(sudoku):
    global extractedSudoku

    hideLoading()

    # Validate the extracted Sudoku
    if (
        sudoku is None
        or len(sudoku) != 9
        or any(len(row) != 9 for row in sudoku)
    ):
        showSudokuInvalidErrorMessage()
        return

    extractedSudoku = sudoku

    printInitialSudoku()
    showBeginSolving()


def uploadFailed():
    hideLoading()
    showSudokuInvalidErrorMessage()


# -------------------------
# Styles
# -------------------------

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Title.TLabel",
    background="#f5f5f5",
    font=("Segoe UI", 24, "bold")
)

style.configure(
    "Subtitle.TLabel",
    background="#f5f5f5",
    foreground="#666666",
    font=("Segoe UI", 11)
)

style.configure(
    "Solve.TButton",
    font=("Segoe UI", 11, "bold"),
    foreground="black",
    padding=(20, 10)
)

style.configure(
    "Error.TLabel",
    background="#f5f5f5",
    foreground="red",
    font=("Segoe UI", 9, "bold")
)

style.configure(
    "Loading.TLabel",
    background="#f5f5f5",
    foreground="#666666",
    font=("Segoe UI", 9)
)


# -------------------------
# Header
# -------------------------

header = Frame(
    root,
    bg="#f5f5f5"
)

header.pack(pady=(30, 15))


title = ttk.Label(
    header,
    text="Sudoku Solver",
    style="Title.TLabel"
)

title.pack()


subtitle = ttk.Label(
    header,
    text="Watch the solver work through the puzzle",
    style="Subtitle.TLabel"
)

subtitle.pack(pady=(5, 0))


# -------------------------
# Errors
# -------------------------

errors = Frame(
    root,
    bg="#f5f5f5"
)

errors.pack()

errorMessage = ttk.Label(
    errors,
    text="The sudoku provided is not in the correct format",
    style="Error.TLabel"
)

# -------------------------
# Sudoku grid
# -------------------------

sudokuContainer = Frame(
    root,
    bg="#222222",
    padx=3,
    pady=3
)

sudokuContainer.pack(pady=15)


sudokuGrid = Frame(
    sudokuContainer,
    bg="white"
)

sudokuGrid.pack()


for row in range(9):
    for col in range(9):

        border = Frame(
            sudokuGrid,
            bg="#222222" if (
                (col + 1) % 3 == 0 or
                (row + 1) % 3 == 0
            ) else "#cccccc",
            padx=1,
            pady=1
        )

        border.grid(
            row=row,
            column=col,
            padx=1 if col % 3 == 0 else 0,
            pady=1 if row % 3 == 0 else 0
        )

        numberInSquare = Label(
            border,
            text="",
            width=2,
            height=1,
            bg="white",
            fg="#222222",
            font=("Segoe UI", 22, "bold"),
            anchor="center"
        )

        numberInSquare.pack(
            ipadx=8,
            ipady=5
        )

        labels[row].append(numberInSquare)


# -------------------------
# Controls
# -------------------------

controls = Frame(
    root,
    bg="#f5f5f5"
)

controls.pack(pady=20)


uploadSudokuButton = ttk.Button(
    controls,
    text="Choose Sudoku",
    style="Solve.TButton",
    command=uploadAction
)


solveLinearButton = ttk.Button(
    controls,
    text="Solve Linearly",
    style="Solve.TButton",
    command=solveLinearly
)


solveEfficientButton = ttk.Button(
    controls,
    text="Solve efficiently",
    style="Solve.TButton",
    command=solveMostEfficient
)

loadingLabel = ttk.Label(
    controls,
    text="Reading Sudoku...",
    style="Loading.TLabel"
)


loadingBar = ttk.Progressbar(
    controls,
    mode="indeterminate",
    length=120
)


# Only show upload button initially
uploadSudokuButton.pack(
    side=LEFT,
    padx=5
)

# -------------------------
# Start application
# -------------------------

root.mainloop()