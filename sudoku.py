class Sudoku:
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

        rows, columns, grids = self._parseSudoku(sudoku)

        allSectionsToValidate = rows + columns + grids

        for section in allSectionsToValidate:
            searchedDigits = []
            for digit in section:
                if (digit is None):
                    continue

                if digit in searchedDigits:
                    raise Exception("Invalid sudoku!")

                searchedDigits.append(digit)

        self._checks = []
        self.sudoku = sudoku 
        self.count = 0

    def _parseSudoku(self, sudoku):
        columns = [[] for _ in range(9)]    
        grids = [[[], [], []] for _ in range(3)]
        rows = []

        for indexRow, row in enumerate(sudoku):
            # Get the values in each row
            rows.append(row)
            for indexCol, entity in enumerate(row):
                # Gets the values in each column
                columns[indexCol].append(entity)
                # Gets the values in each grid
                grids[indexRow // 3][indexCol // 3].append(entity)

        return rows, columns, grids
    
    def _findEmptySquares(self, sudoku):
        emptySquares = []
        for indexRow, row in enumerate(sudoku):
            for indexCol, col in enumerate(row):
                if not col:
                    emptySquares.append((indexRow, indexCol))

        return emptySquares
    
    def _getPossibilitiesForEverySquare(self, sudoku):
        valuesPerSquare = {}

        rows, columns, grids = self._parseSudoku(sudoku)
        emptySquares = self._findEmptySquares(sudoku)

        # Get all the valid values per empty square 
        for (row, col) in emptySquares:
            validValues = []

            for i in range(1,10):
                if (
                    i not in columns[col] and
                    i not in rows[row] and
                    i not in grids[row // 3][col // 3]
                ):
                    validValues.append(i)

            valuesPerSquare[(row, col)] = validValues

        return valuesPerSquare

    def _findSquareWithLeastPossibilities(self, sudoku):
        valuesPerSquare = self._getPossibilitiesForEverySquare(sudoku)

        lowest = 10000 # Comically high so first iteration it always takes the new value
        bestSquare = ()

        # Find the square with the least number of values
        # To speed up the process, if a square has one value then do that square

        for square, validValues in valuesPerSquare.items():
            if len(validValues) == 1:
                return (square, validValues)

            if len(validValues) < lowest:
                lowest = len(validValues)
                bestSquare = (square, validValues)

        return bestSquare
        
    def solveSteps(self, sudoku=None):
        if sudoku is None:
            sudoku = self.sudoku


        result = self._findSquareWithLeastPossibilities(sudoku)

        # No empty squares left
        if not result:
            return self._validateSudoku(sudoku)

        square, validValues = result
        row, col = square

        for number in validValues:
            sudoku[row][col] = number

            # Tell the UI that a number was placed
            yield row, col, number

            # Recursively solve, but yield every step back to the caller
            result = yield from self.solveSteps(sudoku)

            if result:
                return True

            # Backtrack
            sudoku[row][col] = None

            # Tell the UI that the number was removed
            yield row, col, None

        return False

    def _validateOneToNine(self, array):
        for n in array:
            if not n:
                return False

        for i, number in enumerate(sorted(array)):
            if number != i + 1:
                return False
    
        return True
    
    def _validateSudoku(self, sudoku):
        if not sudoku:
            return False

        rows, columns, grids = self._parseSudoku(sudoku)

        checks = []

        grids_flat = [item for grid in grids for item in grid]
        checks.extend(grids_flat)
        checks.extend(rows)
        checks.extend(columns)

        for arr in checks:
            if not self._validateOneToNine(arr):
                return False

        return True

    @staticmethod          
    def getFormattedSudoku(sudoku):
        completedSudoku = ''
          
        for rowIndex, row in enumerate(sudoku):

            completedSudoku += "\n"
            if rowIndex != 0 and rowIndex % 3 == 0:
                completedSudoku += "-" * ((len(sudoku)) * 4)
                completedSudoku += "\n"

            for colIndex, number in enumerate(row):
                if colIndex != 0 and colIndex % 3 == 0:
                    completedSudoku += " | "

                if colIndex == 0:
                    completedSudoku += " "

                completedSudoku += f" {str(number)} "

        return completedSudoku

