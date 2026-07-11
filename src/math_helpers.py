"""Mathematical helper functions for matrix-lang.

Contains standalone algorithm implementations used by the Matrix class.
These are separated to keep matrix.py readable and to make the algorithms independently testable.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from constants import STRASSEN_N_MIN
import math

if TYPE_CHECKING:
    from matrix import Matrix


def matrix_multiply(a: Matrix, b: Matrix) -> Matrix:
    """Return the matrix product of ab.

    Preconditions:
        - a.num_cols() == b.num_rows()
    """
    return type(a)([
        [
            sum(a[i, k] * b[k, j] for k in range(a.num_cols()))
            for j in range(b.num_cols())
        ]
        for i in range(a.num_rows())
    ])


def strassen_multiply(a: Matrix, b: Matrix) -> Matrix:
    """Return the matrix product of a and b using Strassen's algorithm.

    This function acts as the entry point: it handles padding the matrices 
    to a power of 2, invoking the recursive algorithm, and then stripping 
    the padding from the result.
    """
    a_rows, a_cols = a.dimensions()
    b_rows, b_cols = b.dimensions()

    n_min = min(a_rows, a_cols, b_cols)

    if n_min <= STRASSEN_N_MIN:
        return matrix_multiply(a, b)
        
    else:
        max_dim = max(a_rows, a_cols, b_rows, b_cols)
        target_size = _next_power_of_2(max_dim)
        
        # 1. Pad matrices to next power of 2
        padded_a = _pad_matrix(a, target_size)
        padded_b = _pad_matrix(b, target_size)
        
        # 2. Call _strassen_recursive
        result = _strassen_recursive(padded_a, padded_b)
        
        # 3. Remove padding from result to match expected dimensions
        answer = _remove_padding(result, a_rows, b_cols)
        return answer


def _next_power_of_2(n: int) -> int:
    """Return the smallest power of 2 that is greater than or equal to n."""
    return 1 if n == 0 else 1 << (n - 1).bit_length()


def _pad_matrix(matrix: Matrix, target_size: int) -> Matrix:
    """Return a new matrix padded with zeros to be target_size x target_size.
    
    Padding is added to the bottom and right edges of the original matrix.
    """
    rows, cols = matrix.dimensions()
    
    # Pad existing rows with zeros on the right
    new_rows = [
        row + [0] * (target_size - cols)
        for row in matrix.rows
    ]
    
    # Add new entirely zero rows at the bottom
    # (Note: we create a new [0]*target_size list for each row to avoid reference bugs!)
    for _ in range(target_size - rows):
        new_rows.append([0] * target_size)

    return type(matrix)(new_rows)


def _remove_padding(matrix: Matrix, target_rows: int, target_cols: int) -> Matrix:
    """Return a new matrix with padding removed to match the target dimensions.
    
    This safely removes only the padding by slicing the top-left portion 
    of the matrix, leaving any legitimate zeros in the original data intact.
    """
    # Slice the rows list to target_rows, and each row to target_cols
    new_rows = [
        row[:target_cols] 
        for row in matrix.rows[:target_rows]
    ]

    return type(matrix)(new_rows)


def _split_quadrants(matrix: Matrix) -> tuple[Matrix, Matrix, Matrix, Matrix]:
    """Split a matrix into four equal quadrants."""
    mid = matrix.num_rows() // 2
    
    A11 = type(matrix)([row[:mid] for row in matrix.rows[:mid]])
    A12 = type(matrix)([row[mid:] for row in matrix.rows[:mid]])
    A21 = type(matrix)([row[:mid] for row in matrix.rows[mid:]])
    A22 = type(matrix)([row[mid:] for row in matrix.rows[mid:]])
    
    return A11, A12, A21, A22


def _assemble_quadrants(C11: Matrix, C12: Matrix, C21: Matrix, C22: Matrix) -> Matrix:
    """Assemble four quadrants into a single matrix."""
    new_rows = []
    
    for r1, r2 in zip(C11.rows, C12.rows):
        new_rows.append(r1 + r2)
        
    for r1, r2 in zip(C21.rows, C22.rows):
        new_rows.append(r1 + r2)
        
    return type(C11)(new_rows)


def _strassen_recursive(a: Matrix, b: Matrix) -> Matrix:
    """Recursive core of Strassen's algorithm.
    
    Assumes `a` and `b` are square matrices with dimensions that are a power of 2.
    """
    if a.dimensions()[0] <= STRASSEN_N_MIN:
        return matrix_multiply(a, b)

    # 1. Divide a and b into 4 quadrants each
    A11, A12, A21, A22 = _split_quadrants(a)
    B11, B12, B21, B22 = _split_quadrants(b)
    
    # 2. Calculate the 7 intermediate products (M1 to M7)
    M1 = _strassen_recursive(A11 + A22, B11 + B22)
    M2 = _strassen_recursive(A21 + A22, B11)
    M3 = _strassen_recursive(A11, B12 - B22)
    M4 = _strassen_recursive(A22, B21 - B11)
    M5 = _strassen_recursive(A11 + A12, B22)
    M6 = _strassen_recursive(A21 - A11, B11 + B12)
    M7 = _strassen_recursive(A12 - A22, B21 + B22)
    
    # 3. Recombine into C11, C12, C21, C22
    C11 = M1 + M4 - M5 + M7
    C12 = M3 + M5
    C21 = M2 + M4
    C22 = M1 - M2 + M3 + M6
    
    # 4. Assemble the final matrix
    return _assemble_quadrants(C11, C12, C21, C22)
