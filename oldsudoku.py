import math

# The sudoku solver below uses a linear method
# It could only solve easy problems and so was replaced

class OldSudoku:
    def __init__(self, sudoku):
        # A row should look like this 
        # [1,2,3,4,5,6,7,8,9]

        if (len(sudoku) != 9):
            print (
                "Invalid Sudoku passed in.", 
                len(sudoku), 
                "rows passed in. Should be 9"
            )

        for index, row in enumerate(sudoku):
            if (len(row) != 9):
                print (
                    "Invalid Sudoku passed in.", 
                    len(row), 
                    "columns passed in on row" ,
                    index + 1, 
                    ". Should be 9"
                )

        self._checks = []
        self._state = [row[:] for row in sudoku]
        self.sudoku = sudoku 

    def _findValidValue(self, rowIndex, columnIndex, value):
        column = []
        grid = []
        row = self._state[rowIndex]

        for rowRange in range(0,9):
            # Get the values in the column
            column.append(self._state[rowRange][columnIndex])
                    
        upToIndexRow = (int(math.floor((rowIndex) / 3)) + 1) * 3
        upToIndexCol = (int(math.floor((columnIndex) / 3)) + 1) * 3
        
        # Get the values in the same grid
        for rowRange in range(upToIndexRow - 3, upToIndexRow):
            for col in range(upToIndexCol - 3, upToIndexCol):
                grid.append(self._state[rowRange][col])

        # Now try each possible value
        while value <= 10:
            if value == 10:
                # We have looped through all the possible values
                # So leave cell blank and go back 
                return None
            
            if (
                value not in column and 
                value not in row and 
                value not in grid
            ):
                return value     

            value += 1   

    def _next(self, row, col):
        if col + 1 < 9:
            return row, col + 1
        else:
            return row + 1, 0 

    def solve(self):
        row = 0
        col = 0

        while row < 9:
            activeCell = self._state[row][col]

            # Fixed cell from the original Sudoku
            if activeCell is not None and activeCell == self.sudoku[row][col]:
                row, col = self._next(row, col)
                continue

            # Determine where to start looking for a value
            value = 1

            if activeCell is not None:
                # We're revisiting this cell after backtracking
                value = activeCell + 1

            # Find the next valid value
            cellValue = self._findValidValue(row, col, value)

            self._state[row][col] = cellValue

            # Tell Tkinter about the change
            yield row, col, cellValue

            if cellValue is None:
                # No valid value found.
                #
                # Remove this cell from the stack because we're
                # going back to the previous decision.
                if not self._checks:
                    return

                row, col = self._checks.pop()

                # The previous cell will be retried with its
                # next possible value.
                continue

            # We found a valid value, so remember this cell as
            # a decision point.
            self._checks.append((row, col))

            row, col = self._next(row, col)

        return self._state