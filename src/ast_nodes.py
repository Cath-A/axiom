"""AST node definitions for matrix-lang."""

from matrix import *
from typing import Optional, Any
from builtin_funcs import BUILTINS, identity


class Statement:
    """An abstract class representing a matrix-lang statement.

    We think of a statement as being a more general piece of code than a
    single expression, and that can have some kind of "effect".
    """
    def evaluate(self, env: dict[str, Any]) -> Optional[Any]:
        """Evaluate this statement with the given environment.

        Note that the return type here is Optional[Any]: evaluating a statement
        could produce a value (this is true for all expressions), but it might
        only have a *side effect* like mutating `env` or printing something.
        """
        raise NotImplementedError


# ── Statements ────────────────────────────────────────────────────────────────


class Expr(Statement):
    """An abstract class representing a matrix-lang expression.
    """
    def evaluate(self, env: dict[str, Any]) -> Any:
        """Return the *value* of this expression."""
        raise NotImplementedError


class Assign(Statement):
    """An assignment statement (with a single target).

    Instance Attributes:
        - target: the variable name on the left-hand side of the equals sign
        - value: the expression on the right-hand side of the equals sign
    """
    target: str
    value: Expr

    def __init__(self, target: str, value: Expr) -> None:
        """Initialise a new Assign node."""
        self.target = target
        self.value = value

    def evaluate(self, env: dict[str, Any]) -> None:
        """Evaluate this statement with the given environment.
        """
        env[self.target] = self.value.evaluate(env)

    def __repr__(self) -> str:
        return f'Assign({self.target}, {self.value})'


class Print(Statement):
    """A statement representing a call to the built-in print function.

    Instance Attributes:
        - argument: the expression whose value will be printed
    """
    def __init__(self, argument: Expr) -> None:
        """Initialise a new Print node."""
        self.argument = argument

    def evaluate(self, env: dict[str, Any]) -> None:
        """Evaluate this statement.

        This evaluates the argument of the print call, and then actually
        prints it. Note that it doesn't return anything, since `print` doesn't
        return anything.
        """
        print(self.argument.evaluate(env))



# ── Control flow ──────────────────────────────────────────────────────────────


class If(Statement):
    """An if statement.

    This is a statement of the form:
        if <test>:
            <body>
        else:
            <orelse>

    Instance Attributes:
        - test: The condition expression of this if statement.
        - body: A sequence of statements to evaluate if the condition is True.
        - orelse: A sequence of statements to evaluate if the condition is False.
                    (This would be empty in the case that there is no `else` block.)
    """
    test: Expr
    body: list[Statement]
    orelse: list[Statement]

    def __init__(self, test: Expr, body: list[Statement], orelse: list[Statement]) -> None:
        """Initialise a new If node."""
        self.test = test
        self.body = body
        self.orelse = orelse

    def evaluate(self, env: dict[str, Any]) -> None:
        """Evaluate this if statement with the given environment.

        Evaluates the test condition and executes the body if True, otherwise
        executes the orelse block.
        """
        test_result = self.test.evaluate(env)
        if test_result:
            for statement in self.body:
                statement.evaluate(env)
        else:
            for statement in self.orelse:
                statement.evaluate(env)


class ForRange(Statement):
    """A for loop that loops over a range of numbers.

    for <target> in range(<start>, <stop>):
        <body>

    Instance Attributes:
        - target: The loop variable.
        - start: The start for the range (inclusive).
        - stop: The end of the range (this is *exclusive*, so <stop> is not included
                in the loop).
        - body: The statements to execute in the loop body.
    """
    target: str
    start: Expr
    stop: Expr
    body: list[Statement]

    def __init__(self, target: str, start: Expr, stop: Expr, body: list[Statement]) -> None:
        """Initialise a new ForRange node."""
        self.target = target
        self.start = start
        self.stop = stop
        self.body = body

    def evaluate(self, env: dict[str, Any]) -> None:
        """Evaluate this statement with the given environment."""
        start_val = self.start.evaluate(env)
        stop_val = self.stop.evaluate(env)
        for i in range(start_val, stop_val):
            env[self.target] = i
            for statement in self.body:
                statement.evaluate(env)


"""Expressions"""


class Scalar(Expr):
    """A numeric literal.

    Instance Attribute:
        - n: the value of the literal
    """
    n: int | float

    def __init__(self, number: int | float) -> None:
        """Initialise a new numeric literal."""
        self.n = number

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Return the *value* of this expression.

        >>> expr = Scalar(10.5)
        >>> expr.evaluate()
        10.5
        """
        return self.n

    def __repr__(self) -> str:
        return f'Scalar({self.n})'


class MatrixLiteral(Expr):
    """A matrix literal written as [r1c1, r1c2; r2c1, r2c2] in source.

    Instance Attribute:
        - rows: a list of rows, each row being a list of Expr nodes
    """
    rows: list[list[Expr]]

    def __init__(self, rows: list[list[Expr]]) -> None:
        """Initialise a new MatrixLiteral node."""
        self.rows = rows

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Evaluate all element expressions and construct a Matrix.

        Delegates shape promotion to Matrix.__new__: a 1x1 result becomes
        a scalar, 1xn becomes a RowVector, nx1 becomes a ColumnVector,
        and anything else becomes a Matrix.
        """
        rows = [[expr.evaluate(env) for expr in row] for row in self.rows]
        return Matrix(rows)

    def __repr__(self) -> str:
        return f'MatrixLiteral({self.rows})'


class UnaryOp(Expr):
    """A unary arithmetic operation.

    Instance Attributes:
        - op: the operator symbol ('-' or '+')
        - operand: the expression being operated on

    Representation Invariants:
        - self.op in {'-', '+'}
    """
    op: str
    operand: Expr

    def __init__(self, op: str, operand: Expr) -> None:
        """Initialise a new unary operation expression.

        Preconditions:
            - op in {'-', '+'}
        """
        self.op = op
        self.operand = operand

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Evaluate this unary operation."""
        value = self.operand.evaluate(env)

        if self.op == '-':
            return -value
        if self.op == '+':
            return value
        raise SyntaxError(f"Unknown unary operator '{self.op}'")

        raise SyntaxError(f"Unknown unary operator {self.op}")


class BinOp(Expr):
    """An arithmetic binary operation.

    Instance Attributes:
        - left: the left operand
        - op: the name of the operator
        - right: the right operand

    Representation Invariants:
        - self.op in {'+', '-', '*', '/'}
    """
    left: Expr
    op: str
    right: Expr

    def __init__(self, left: Expr, op: str, right: Expr) -> None:
        """Initialise a new binary operation expression.

        Preconditions:
            - op in {'+', '-', '*', '/'}
        """
        self.left = left
        self.op = op
        self.right = right

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Evaluate and apply the binary operator to both operands."""
        left = self.left.evaluate(env)
        right = self.right.evaluate(env)

        if self.op == '+':
            return left + right
        elif self.op == '-':
            return left - right
        elif self.op == '*':
            return left * right
        elif self.op == '/':
            return left / right
        else:
            raise TypeError(f"Unsupported operator '{self.op}'")

    def __repr__(self) -> str:
        return f'BinOp({self.left}, {self.op!r}, {self.right})'


class Name(Expr):
    """A variable expression.

    Instance Attributes:
        - id: The variable name.
    """
    id: str

    def __init__(self, id_: str) -> None:
        """Initialise a new variable expression."""
        self.id = id_

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Return the *value* of this expression.

        The name should be looked up in the `env` argument to this method.
        Raise a NameError if the name is not found.
        """
        if self.id in env:
            return env[self.id]
        else:
            raise NameError(f"name '{self.id}' is not defined")

    def __repr__(self) -> str:
        return f'Name({self.id})'


class FuncCall(Expr):
    """A function call expression.

    Instance Attributes:
        - name: the name of the function
        - args: the list of arguments
    """
    name: str
    args: list[Expr]

    def __init__(self, name: str, args: list[Expr]) -> None:
        """Initialise a new FuncCall node."""
        self.name = name
        self.args = args

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Evaluate this function call."""
        evaluated_args = [arg.evaluate(env) for arg in self.args]

        if self.name not in BUILTINS:
            raise NameError(f"Unknown function '{self.name}'")

        return BUILTINS[self.name](*evaluated_args)

    def __repr__(self) -> str:
        return f'FuncCall({self.name}, {self.args})'


class IdentityLiteral(Expr):
    """An identity matrix literal written as I_n in source.

    Instance Attributes:
        - size: an expression that evaluates to the integer size of the matrix

    Examples:
        I_3       → 3×3 identity
        I_n       → n×n identity (n must hold an integer)
        I_{n+1}   → (n+1)×(n+1) identity
    """
    size: Expr

    def __init__(self, size: Expr) -> None:
        """Initialise a new IdentityLiteral node."""
        self.size = size

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Evaluate to produce an identity matrix."""
        n = self.size.evaluate(env)
        
        if not isinstance(n, int): 
            raise TypeError("Size must be an integer")
        if n <= 0:
            raise ValueError("Size must be positive")
        
        return identity(n)

    def __repr__(self) -> str:
        return f'IdentityLiteral({self.size})'


class Symbol(Expr):
    """A symbolic literal used for special markers like 'T' (Transpose).
    
    Evaluates to its string value.
    """
    value: str

    def __init__(self, value: str) -> None:
        self.value = value

    def evaluate(self, env: dict[str, Any]) -> Any:
        return self.value

    def __repr__(self) -> str:
        return f"Symbol({self.value})"


class SuperscriptOp(Expr):
    """A superscript operation (A^x).

    Instance Attributes:
        - base: the expression being operated on
        - superscript: the exponent expression
    """
    base: Expr
    superscript: Expr

    def __init__(self, base: Expr, superscript: Expr) -> None:
        """Initialise a new SuperscriptOp node."""
        self.base = base
        self.superscript = superscript

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Evaluate the superscript operation."""
        base_val = self.base.evaluate(env)
        sup_val = self.superscript.evaluate(env)
        
        if isinstance(base_val, (int, float)):
            if not isinstance(sup_val, (int, float)):
                raise TypeError(f"Cannot raise scalar to {type(sup_val).__name__}")
            
        elif not isinstance(base_val, Matrix):
            raise TypeError(f"Cannot apply '^' to {type(base_val).__name__}")

        return base_val ** sup_val

    def __repr__(self) -> str:
        return f'SuperscriptOp({self.base}, {self.superscript})'


# ── Module ────────────────────────────────────────────────────────────────────


class Module:
    """A class representing a full matrix-lang program.

    Instance Attributes:
        - body: A sequence of statements.
    """
    body: list[Statement]

    def __init__(self, body: list[Statement]) -> None:
        """Initialise a new module with the given body."""
        self.body = body

    def evaluate(self, env: dict[str, Any] = None) -> None:
        """Evaluate all statements in order with the given environment.

        Creates a fresh empty environment if none is provided.
        """
        if env is None:
            env = {}

        for statement in self.body:
            statement.evaluate(env)
