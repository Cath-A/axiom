"""Converts a token list into an AST.

Raises ParseError on invalid input.
"""
from lexer import Token, TokenType
from ast_nodes import *


def parse(tokens: list[Token]) -> Module:
    """Parse a list of tokens into a Module AST node.

    Returns the root Module representing the full program.
    """
    body = []
    i = 0

    while tokens[i].type != TokenType.EOF:
        while tokens[i].type == TokenType.NEWLINE:
            i += 1
            if tokens[i].type == TokenType.EOF:
                break

        statement, i = _parse_statement(tokens, i)
        body.append(statement)

        if tokens[i].type == TokenType.NEWLINE:
            i += 1
        elif tokens[i].type != TokenType.EOF:
            raise SyntaxError(f"Unexpected token: {tokens[i].value}")

    return Module(body)


def _parse_statement(tokens: list[Token], i: int) -> tuple[Statement, int]:
    """Parse a single statement starting at index i.

    Returns the Statement node and the index of the next unread token.
    """
    # assignment: NAME = expr
    if (
        tokens[i].type == TokenType.NAME
        and tokens[i + 1].type == TokenType.EQUALS
    ):
        return _parse_assign(tokens, i)

    # otherwise parse as expression
    return _parse_addition(tokens, i)


def _parse_assign(tokens: list[Token], i: int) -> tuple[Assign, int]:
    """Parse an assignment statement starting at index i.

    `i` should point at the NAME token on the left hand side.
    Representation Invariants:
        - tokens[i].type == TokenType.NAME
        - tokens[i + 1].type == TokenType.EQUALS
        - tokens[i + 2:] begins a valid expression
        - this function is only called by _parse_statement for assignment cases

    Returns the Assign node and the index of the next unread token.
    """
    target = tokens[i].value

    if target == 'I':
        raise SyntaxError("'I' is reserved for identity matrices and cannot be assigned to")

    i += 2
    value, i = _parse_addition(tokens, i)

    # forbid chained assignment: must end statement here
    if tokens[i].type not in (TokenType.NEWLINE, TokenType.EOF):
        raise SyntaxError("Chained assignment is not allowed")

    return Assign(target, value), i


def _parse_addition(tokens: list[Token], i: int) -> tuple[Expr, int]:
    """Parse an addition or subtraction expression starting at index i.

    Entry point for all expression parsing - always call this first.
    Returns the Expr node at the index of the next unread token.
    """
    lhs, i = _parse_multiplication(tokens, i)

    while tokens[i].type in (TokenType.PLUS, TokenType.MINUS):
        op = tokens[i].value
        i += 1

        rhs, i = _parse_multiplication(tokens, i)

        lhs = BinOp(lhs, op, rhs)

    return lhs, i


def _parse_multiplication(tokens: list[Token], i: int) -> tuple[Expr, int]:
    """Parse a multiplication or division expression starting at index i

    Never call directly - called by _parse_addition.
    Returns the Expr node and the index of the next unread token.
    """
    lhs, i = _parse_unary(tokens, i)

    while tokens[i].type in (TokenType.STAR, TokenType.SLASH):
        op = tokens[i].value
        i += 1

        rhs, i = _parse_atom(tokens, i)

        lhs = BinOp(lhs, op, rhs)

    return lhs, i


def _handle_function(tokens: list[Token], i: int) -> tuple[Expr, int]:
    """Parse a function call from source starting at index i.

    Returns the function call as a FuncCall expression and the index of the last USED token.
    """
    name = tokens[i].value
    args = []
    i += 2

    # CASE 1: empty argument list
    if tokens[i].type == TokenType.RPAREN:
        return FuncCall(name, args), i

    # CASE 2: at least 1 argument
    arg, i = _parse_addition(tokens, i)
    args.append(arg)

    while tokens[i].type == TokenType.COMMA:
        i += 1
        arg, i = _parse_addition(tokens, i)
        args.append(arg)

    if tokens[i].type != TokenType.RPAREN:
        raise SyntaxError("Expected ')' to close function call")

    return FuncCall(name, args), i

def _handle_identity(tokens: list[Token], i: int) -> tuple[Expr, int]:
    i += 2

    if tokens[i].type == TokenType.NUMBER:
        n = Scalar(tokens[i].value)
    elif tokens[i].type == TokenType.NAME:
        n = Name(tokens[i].value)
    elif tokens[i].type == TokenType.LBRACE:
        i += 1
        n, i = _parse_addition(tokens, i)

        if tokens[i].type != TokenType.RBRACE:
            raise SyntaxError("Expected '}' to close braced expression")
    else:
        raise SyntaxError("Expected size after 'I_")

    return IdentityLiteral(n), i
    

def _handle_matrix(tokens: list[Token], i: int) -> tuple[Expr, int]:
    """Parse a matrix from source starting at index i.

    Returns the matrix as a MatrixLiteral expression and the index of the last USED token.
    """
    i += 1
    if tokens[i].type == TokenType.RBRACKET:
        raise SyntaxError("Empty Matrix")

    rows = []
    while tokens[i].type not in (TokenType.EOF, TokenType.NEWLINE, TokenType.RBRACKET):
        row = []

        while tokens[i].type not in (TokenType.SEMICOLON, TokenType.RBRACKET, TokenType.NEWLINE, TokenType.EOF):
            expression, i = _parse_addition(tokens, i)
            row.append(expression)
            if tokens[i].type == TokenType.COMMA:
                i += 1

        rows.append(row)
        if tokens[i].type == TokenType.SEMICOLON:
            i += 1

    if tokens[i].type != TokenType.RBRACKET:
        raise SyntaxError("Expected ']' to close matrix definition")

    matrix = MatrixLiteral(rows)
    return matrix, i


def _parse_unary(tokens: list[Token], i: int) -> tuple[Expr, int]:
    """Parse unary + and - operators."""
    if tokens[i].type == TokenType.MINUS:
        i += 1
        operand, i = _parse_unary(tokens, i)
        return UnaryOp('-', operand), i

    if tokens[i].type == TokenType.PLUS:
        i += 1
        operand, i = _parse_unary(tokens, i)
        return UnaryOp('+', operand), i

    return _parse_power(tokens, i)


def _parse_power(tokens: list[Token], i: int) -> tuple[Expr, int]:
    """Parse a superscript (^) expression, right-associative.

    Handles:
        - A^T         → SuperscriptOp(A, None, is_transpose=True)
        - A^2         → SuperscriptOp(A, Scalar(2))
        - A^n         → SuperscriptOp(A, Name('n'))
        - A^{expr}    → SuperscriptOp(A, expr)

    Returns the Expr node and the index of the next unread token.
    """
    base, i = _parse_atom(tokens, i)

    if tokens[i].type != TokenType.CARET:
        return base, i

    i += 1

    if tokens[i].type == TokenType.NUMBER:
        expr = Scalar(tokens[i].value)
    elif tokens[i].type == TokenType.NAME and tokens[i].value == 'T':
        expr = Symbol('T')
    elif tokens[i].type == TokenType.NAME:
        expr = Name(tokens[i].value)
    elif tokens[i].type == TokenType.LBRACE:
        i += 1
        expr, i = _parse_addition(tokens, i)

        if tokens[i].type != TokenType.RBRACE:
            raise SyntaxError("Expected '}' to close braced expression")
    else:
        raise SyntaxError("Expected superscript after '^'")

    i += 1
    return SuperscriptOp(base, expr), i


# TODO: rest of the atoms
def _parse_atom(tokens: list[Token], i: int) -> tuple[Expr, int]:
    """Parse an atomic expression starting at index i.

     Handles scalars, names, function calls, matrix literals, and
     parenthesised expressions. Never call directly - called by _parse_multiplication.
     Returns the Expr node and the index of the next unread token.
    """
    if tokens[i].type == TokenType.NUMBER:
        expression = Scalar(tokens[i].value)

    elif tokens[i].type == TokenType.NAME:
        if tokens[i].value == 'I' and tokens[i + 1].type == TokenType.UNDERSCORE:
            expression, i = _handle_identity(tokens, i)
        elif tokens[i + 1].type == TokenType.LPAREN:
            expression, i = _handle_function(tokens, i)
        else:
            expression = Name(tokens[i].value)

    elif tokens[i].type == TokenType.LPAREN:
        i += 1
        expression, i = _parse_addition(tokens, i)

        if tokens[i].type != TokenType.RPAREN:
            raise SyntaxError("Expected ')'")

    elif tokens[i].type == TokenType.LBRACKET:
        expression, i = _handle_matrix(tokens, i)

    elif tokens[i].type == TokenType.NEWLINE:
        raise SyntaxError("Unexpected end of line in expression")

    else:
        raise SyntaxError(f"Unexpected token in atom: {tokens[i].type}")

    i += 1
    return expression, i
