"""Built-in functions available in matrix-lang.

This module defines the functions provided by matrix-lang without
requiring the user to define them. Built-ins include matrix operations,
type inspection, and output functions.

The BUILTINS dictionary maps language-level function names to their
Python implementations so that the evaluator can resolve built-in
function calls.
"""
from typing import Any
from matrix import Matrix, RowVector, ColumnVector


def diag(numbers: RowVector | int | float | list) -> Matrix:
    """Create a diagonal matrix from a list of numbers."""

    if isinstance(numbers, (int, float)):
        numbers = [numbers]
    elif isinstance(numbers, RowVector):
        numbers = numbers.rows[0]
    elif isinstance(numbers, ColumnVector):
        raise TypeError("diag() expects an array, not a column vector")
    elif not isinstance(numbers, list):
        raise TypeError("diag() expects a scalar, row vector, or list")

    size = len(numbers)
    rows = []

    for i in range(size):
        row = [0 for _ in range(size)]
        row[i] = numbers[i]
        rows.append(row)

    return Matrix(rows)


def identity(size: int) -> Matrix:
    """Create an identity matrix of the given size.

    Returns a square Matrix of size x size with ones along the main diagonal and zeros everywhere else.
    """
    return diag([1] * size)


def type_of(value: Any) -> str:
    """Return the Axiom type name of a value.
    """
    if isinstance(value, RowVector):
        return "row vector"
    elif isinstance(value, bool):
        return "column vector"
    elif isinstance(value, Matrix):
        return "matrix"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, (int, float)):
        return "scalar"
    elif isinstance(value, str):
        return "string"

    return type(value).__name__


BUILTINS = {
    'print': print,
    'diag': diag,
    'type': type_of,
}
