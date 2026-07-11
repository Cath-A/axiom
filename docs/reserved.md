# Reserved Names

matrix-lang reserves certain names to avoid ambiguity with mathematical notation. These names **cannot** be used as variable names.

## Reserved Variable Names

| Name | Reason | What it does |
|------|--------|--------------|
| `I` | Identity matrix notation | `I_n` produces an n×n identity matrix |

### Why is `I` reserved?

In linear algebra, **I** universally denotes the identity matrix. To support the `I_n` syntax (e.g., `I_3` for a 3×3 identity), the parser needs to know that `I` always refers to the identity constructor, never a user variable.

**This will error:**
```
>>> I = 5
SyntaxError: 'I' is reserved for identity matrices and cannot be assigned to
```

**Workaround:** Use a different variable name. In linear algebra, single-letter variables are standard — try `J`, `K`, `L`, etc.

---

## Reserved Superscript Names

| Name | Context | Meaning |
|------|---------|---------|
| `T` | After `^` (bare) | Transpose |

### The `T` Asymmetry

When `T` appears **bare** after `^`, it always means transpose:

```
>>> A = [1, 2; 3, 4]
>>> A^T
⎡1  3⎤
⎣2  4⎦
```

When `T` appears **inside braces** after `^`, it is treated as a regular variable:

```
>>> T = 3
>>> A^{T}       ← computes A^3, NOT transpose
```

This follows **LaTeX conventions**, where `A^T` and `A^{T}` have different typesetting but in matrix-lang they have different semantics.

### Summary

| Syntax | Meaning |
|--------|---------|
| `A^T` | Always transpose |
| `A^{T}` | Variable lookup — raises A to the value of T |
| `A^t` | Variable lookup — raises A to the value of t (lowercase t is not reserved) |
