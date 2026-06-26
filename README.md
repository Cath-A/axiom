# matrix-lang

Hello, this is a personal project, a DSL for linear algebra, the main goals are to learn about how 
programming languges are made and to try and use proofs to make matrix operations more efficient to calculate.

It's definetely a WIP right now, with a long road ahead, however it's been fun understanding at least a little more
of what goes on behind the scenes.

---

## Running it

Open the REPL:

```bash
python src/repl.py
```

Then just type matrix-lang code. Type `exit` or `quit` to leave.

```
>>> A = diag([1, 2, 3])
>>> A + [1, 0, 0; 2, 0, 0; 3, 0, 0]
⎡2  0  0⎤
⎢2  2  0⎥
⎣3  0  3⎦
>>> exit

```

---


## Benchmarks
***Test types:***
- Matrix Multiplication: the size the largest square matrix it can multiply in under 10 seconds

**Test #1**
- matrix multiplication: 302


---

## TODOs
**Immediate**
- deal with printing large matrices
- matrix multiplication efficiency


**Future**
- While loops
- Comparison operators (`==`, `!=`, `<`, `>`)
- String support, at least for printing labels
- (consider adding) 'let' to first time assigning variables, and the implications of that for matrix mutability
