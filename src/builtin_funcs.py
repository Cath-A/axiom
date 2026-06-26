from matrix import Matrix, RowVector, ColumnVector


def diag(numbers: RowVector | int | float | list) -> Matrix:
    """Create a diagonal matrix from a list of numbers.

    Returns a square Matrix with the given values along the main diagonal and zeros everywhere else.
    """
    if isinstance(numbers, (int, float)):
        numbers = [numbers]
    elif isinstance(numbers, RowVector):
        numbers = numbers.rows[0]
    elif isinstance(numbers, ColumnVector):
        raise TypeError("diag() expects an array, not a column vector")

    size = len(numbers)
    rows = []

    for i in range(size):
        row = [0 for _ in range(size)]
        row[i] = numbers[i]
        rows.append(row)

    matrix = Matrix(rows)
    return matrix


def identity(size: int) -> Matrix:
    """Create an identity matrix of the given size.

    Returns a square Matrix of size x size with ones along the main diagonal and zeros everywhere else.
    """
    return diag([1] * size)


BUILTINS = {
    'print': print,
    'diag': diag,
    'I': identity,
}
