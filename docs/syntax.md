# Syntax Reference

## Superscript Operator (`^`)

The caret `^` applies a superscript operation to an expression. Its meaning depends on what follows the caret:

| Syntax | Meaning | Example | Result |
|--------|---------|---------|--------|
| `A^T` | Transpose | `[1,2;3,4]^T` | `[1,3;2,4]` |
| `A^n` | Power (integer) | `A^2` | `A * A` |
| `A^{expr}` | Power (expression) | `A^{n+1}` | `A` multiplied `n+1` times |
| `x^y` | Scalar exponentiation | `3^2` | `9` |

### Bare vs Braced Superscripts

There is an important distinction between bare and braced superscripts:

- **Bare** `^T` — always means **transpose**. The letter `T` is reserved in superscript position.
- **Braced** `^{T}` — performs **variable lookup**. If `T = 3`, then `A^{T}` computes `A^3`.
- **Bare** `^n` where `n` is a number or variable name — power operation.

This follows standard LaTeX conventions.

### Precedence

`^` binds **tighter** than `*` and `/`. This means:

```
2 * A^T    means    2 * (A^T)       ✓
                    NOT (2*A)^T     ✗
```

### Restrictions

- Negative exponents require braces: `A^{-1}` (not `A^-1`). Note: matrix inverse is not yet implemented.
- Exponents must be non-negative integers for matrices.
- The matrix must be **square** for exponentiation (`A^2` only works if A is n×n).
- `A^0` returns the identity matrix of the same size.

---

## Identity Matrix (`I_n`)

The notation `I_n` produces an n×n identity matrix — a square matrix with 1s on the diagonal and 0s elsewhere.

### Syntax

| Syntax | Meaning | Example |
|--------|---------|---------|
| `I_n` | Identity of size `n` | `I_3` → 3×3 identity |
| `I_{expr}` | Identity of computed size | `I_{n+1}` → (n+1)×(n+1) identity |

### Examples

```
>>> I_3
⎡1  0  0⎤
⎢0  1  0⎥
⎣0  0  1⎦

>>> n = 2
>>> I_{n}
⎡1  0⎤
⎣0  1⎦

>>> A = [1, 2; 3, 4]
>>> A + I_2
⎡2  2⎤
⎣3  5⎦
```

### Notes

- `I` is a **reserved name** — it cannot be used as a variable (see [Reserved Names](reserved.md)).
- The subscript must evaluate to a **positive integer**.
- `I_1` evaluates to the scalar `1` (a 1×1 identity is just the number 1).
