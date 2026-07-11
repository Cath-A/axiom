"""Matrix value type for matrix-lang."""
from __future__ import annotations
from errors import *
from math_helpers import *
from constants import *


class Matrix:
    """A 2D matrix of numeric values.

    Data Representation:
        - Stored as a list of rows
        - Each row is a list of numbers (int or floats)
        - All rows have equal length

    Instance Attributes:
        - rows: the matrix data, where each element is a row of values

    Representation Invariants:
        - len(rows) > 0
        - all(len(row) == len(rows[0]) for row in rows)
    """
    rows: list[list[int | float]]

    def __new__(cls, rows: list[list[int | float]]):
        if cls is Matrix:
            if len(rows) == 1 and len(rows[0]) == 1:
                return rows[0][0]
            if len(rows) == 1:
                instance = object.__new__(RowVector)
                return instance
            if all(len(row) == 1 for row in rows):
                instance = object.__new__(ColumnVector)
                return instance

            return object.__new__(cls)


    def __init__(self, rows: list[list[int | float]]) -> None:
        """Initialise a new matrix."""
        if not isinstance(self, Matrix):
            return
        if len(rows) == 0:
            raise ValueError('Matrix cannot be empty')
        if any(len(row) != len(rows[0]) for row in rows):
            raise ValueError('All rows must be the same length')
        self.rows = rows

    def num_rows(self) -> int:
        """Return the number of rows."""
        return len(self.rows)

    def num_cols(self) -> int:
        """Return the number of columns."""
        return len(self.rows[0])

    def dimensions(self) -> tuple[int, int]:
        """Return the dimensions of the matrix in the form (row, column)."""
        return self.num_rows(), self.num_cols()

    def __neg__(self) -> Matrix:
        """Return the additive inverse of the matrix (-self)."""
        rows = [
            [-value for value in row]
            for row in self.rows
        ]
        return type(self)(rows)

    def __add__(self, other: Matrix) -> Matrix:
        """Return the matrix sum of self and other."""
        if not isinstance(other, Matrix):
            raise MatrixTypeError(f"Cannot add Matrix and {type(other).__name__}")

        elif self.dimensions() != other.dimensions():
            raise MatrixShapeError(
                f"Cannot add matrices with shapes "
                f"{self.num_rows()}x{self.num_cols()} and "
                f"{other.num_rows()}x{other.num_cols()}"
            )

        num_rows, num_cols = self.num_rows(), self.num_cols()
        rows = []

        for i in range(num_rows):
            row = [
                self.rows[i][j] + other.rows[i][j]
                for j in range(num_cols)
            ]
            rows.append(row)

        return type(self)(rows)

    def __sub__(self, other: Matrix) -> Matrix:
        """Return the matrix subtraction of self - other."""
        if not isinstance(other, Matrix):
            raise MatrixTypeError(f"Cannot subtract Matrix and {type(other).__name__}")

        return self + (-other)

    def __mul__(self, other: int | float | Matrix) -> Matrix | int | float:
        """Return the matrix multiplication of self * other"""
        if isinstance(other, (int, float)):
            return type(self)([
                [value * other for value in row]
                for row in self.rows
            ])

        if isinstance(other, Matrix):
            if self.num_cols() != other.num_rows():
                raise MatrixShapeError(
                    f"Invalid matrix multiplication: "
                    f"{self.num_rows()}x{self.num_cols()} * "
                    f"{other.num_rows()}x{other.num_cols()} (inner dimensions must match)"
                )


            result = matrix_multiply(self, other)

            if result.dimensions() == (1, 1):
                return result.rows[0][0]

            return result

        raise MatrixTypeError(f"Cannot multiply Matrix and {type(other).__name__}")

    def __rmul__(self, other: int | float) -> Matrix:
        """Return the scalar multiplication of other * self."""
        if isinstance(other, (int, float)):
            return self * other

        raise MatrixTypeError(f"Cannot multiply {type(other).__name__} and Matrix")

    def transpose(self) -> Matrix:
        """Return the transpose of this matrix.

        The transpose swaps rows and columns: element [i][j] becomes [j][i].
        An m×n matrix becomes n×m.
        """
        new_rows = []

        for j in range(self.num_cols()):
            new_rows.append([self.rows[i][j] for i in range(self.num_rows())])

        return Matrix(new_rows)

    def __pow__(self, power: int | str) -> Matrix:
        """Return this matrix raised to a power, or transposed.

        If power is 'T', returns the transpose.
        If power is an integer n:
            A^0 = I (identity matrix of same size)
            A^1 = A (return self)
            A^n = A * A * ... * A  (n times)
        """
        if power == 'T':
            return self.transpose()

        if not isinstance(power, int) or power < 0:
            raise ValueError("Exponent must be a non-negative integer or 'T'")
        if self.num_rows() != self.num_cols():
            raise MatrixShapeError("Matrix must be square for exponentiation")

        if power == 0:
            from builtin_funcs import identity
            return identity(self.num_rows())

        result = self
        for _ in range(power - 1):
            result = result * self

        return result

    def __getitem__(self, key):
        """Get matrix elements, rows, or columns via indexing.

        Supports:
            - A[i, j]: element at row i, column j
            - A[i, :]: row i
            - A[:, j]: column j
            - A[i]: row i (fallback)

        Instance Attributes:
            - key: indexing key (int or tuple of int/slice(None))
        """
        if isinstance(key, tuple):
            i, j = key
            if i == slice(None) and isinstance(j, int):
                return [row[j] for row in self.rows]

            if j == slice(None) and isinstance(i, int):
                return self.rows[i]

            if isinstance(i, int) and isinstance(j, int):
                return self.rows[i][j]

        return self.rows[key]

    def __eq__(self, other) -> bool:
        """Return whether self and other are equal matrices."""
        if not isinstance(other, Matrix):
            return NotImplemented
        if self.dimensions() != other.dimensions():
            return False
        return all(
            self.rows[i][j] == other.rows[i][j]
            for i in range(self.num_rows())
            for j in range(self.num_cols())
        )

    def __repr__(self) -> str:
        return f'Matrix({self.rows})'

    def _stringify_rows(self) -> list[list[str]]:
        """Return the matrix rows with all values converted to strings."""
        rows = []

        for row in self.rows:
            str_row = []
            for value in row:
                str_row.append(str(value))
            rows.append(str_row)

        return rows

    def _column_widths(self, rows: list[list[str]]) -> list[int]:
        """Return the maximum width of each matrix column."""
        num_cols = self.num_cols()
        widths = [0] * num_cols

        for row in rows:
            for j, value in enumerate(row):
                widths[j] = max(widths[j], len(value))

        return widths

    def _format_row(self, row: list[str], widths: list[int]) -> str:
        """Return a padded string representation of a matrix row."""
        formatted = []

        for value, width in zip(row, widths):
            formatted.append(value.rjust(width))

        return COLUMN_SEPARATOR.join(formatted)

    def _row_brackets(self, row_index: int) -> tuple[str, str]:
        """Return the left and right brackets for a rendered row."""
        if row_index == 0:
            return LEFT_TOP, RIGHT_TOP
        elif row_index == self.num_rows() - 1:
            return LEFT_BOTTOM, RIGHT_BOTTOM
        else:
            return LEFT_MIDDLE, RIGHT_MIDDLE

    def _render_lines(self) -> list[str]:
        """Return the formatted matrix as a list of rendered lines."""
        lines = []
        rows = self._stringify_rows()
        widths = self._column_widths(rows)

        for i in range(self.num_rows()):
            left, right = self._row_brackets(i)
            formatted_row = self._format_row(rows[i], widths)
            lines.append(left + formatted_row + right)

        return lines

    def __str__(self) -> str:
        """Return a formatted string representation of the matrix."""
        return ROW_SEPARATOR.join(self._render_lines())


class ColumnVector(Matrix):
    """A column vector (n x 1 matrix).

    Data Representation:
        - Stored as a matrix with exactly one column
        - Each row contains a single numeric value

    Instance Attributes:
        - rows: list of single-element rows

    Representation Invariants:
        - self.num_cols() == 1
    """
    rows: list[list[int | float]]

    def __init__(self, rows: list[list[int | float]]) -> None:
        """Initialise a new column vector."""
        super().__init__(rows)

        if self.num_cols() != 1:
            raise ValueError("The column vector must have exactly one column")

    def __repr__(self) -> str:
        return f'Vector({self.rows})'


class RowVector(Matrix):
    """A row vector (1 x n matrix).

    Data Representation:
        - Stored as a single row containing multiple values

    Instance Attributes:
        - rows: a list containing exactly one row

    Representation Invariants:
        - self.num_rows() == 1
    """
    rows: list[list[int | float]]

    def __init__(self, rows: list[list[int | float]]) -> None:
        """Initialise a new row vector."""
        super().__init__(rows)

        if self.num_rows() != 1:
            raise ValueError("Row vector must have exactly one row")

    def _row_brackets(self, row_index: int) -> tuple[str, str]:
        return ROW_VECTOR_LEFT, ROW_VECTOR_RIGHT
