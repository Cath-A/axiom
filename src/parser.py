"""Parser for the Axiom programming language.

Converts a token list into an AST.

Raises ParseError on invalid input.
"""
from joblib.testing import param
from numpy.f2py.crackfortran import parameterpattern

from lexer import Token
from constants import KEYWORDS
from ast_nodes import *


class Parser:
    """Recursive-descent parser for Axiom.

    The parser owns the current position rather than passing
    (tokens, index) through every parsing function.
    """
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    # ------------------------------------------------------------------
    # Token navigation
    # ------------------------------------------------------------------

    def current(self) -> Token:
        """Return the current token.

        Always safe because the lexer guarantees a final EOF token.
        """
        return self.tokens[min(self.index, len(self.tokens) - 1)]

    def peek(self, offset: int = 1) -> Token:
        """Look ahead by offset tokens.

        Bounds-safe by construction: looking beyond EOF returns EOF.
        """
        i = self.index + offset
        i = min(i, len(self.tokens) - 1)
        return self.tokens[i]

    def check(self, *types: TokenType) -> bool:
        """Return True if the current token has one of the given types.
        """
        return self.current().type in types

    def check_name(self, *names: str) -> bool:
        """Return True if the current token is a NAME with one of the names.
        """
        token = self.current()
        return token.type == TokenType.NAME and token.value in names

    def advance(self) -> Token:
        """Consume and return the current token.
        """
        token = self.current()
        if token.type != TokenType.EOF:
            self.index += 1
        return token

    def expect(self, token_type: TokenType, message: str) -> Token:
        """Consume a token of the expected type.

        Raises SyntaxError if the current token is not the expected type.
        """
        if not self.check(token_type):
            token = self.current()
            raise SyntaxError(f"{message}. (line {token.line})")
        return self.advance()

    def expect_name(self, name: str, message: str) -> Token:
        """Consume a NAME token with an exact value."""
        token = self.current()
        if token.type != TokenType.NAME or token.value != name:
            raise SyntaxError(f"{message}. (line {token.line})")
        return self.advance()

    def skip_newlines(self) -> None:
        """Consume any number of newline tokens.
        """
        while self.check(TokenType.NEWLINE):
            self.advance()

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def parse(self) -> Module:
        """Parse the complete token stream into a Module.
        """
        body: list[Statement] = []
        self.skip_newlines()

        while not self.check(TokenType.EOF):
            statement = self.parse_statement()
            body.append(statement)

            if self.check(TokenType.NEWLINE):
                self.skip_newlines()
            elif not self.check(TokenType.EOF):
                token = self.current()
                raise SyntaxError(f"Expected end of statement, got {token.value!r}. (line {token.line})")

        return Module(body)

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def parse_statement(self) -> Statement:
        """Parse one statement.
        """
        if self.check_name("if"):
            return self.parse_if()
        elif self.check_name("while"):
            return self.parse_while()
        elif self.check_name("for"):
            return self.parse_for_range()
        elif self.check_name("func"):
            return self.parse_function_def()
        elif self.check_name("return"):
            return self.parse_return()
        elif self.check(TokenType.NAME) and self.peek().type == TokenType.EQUALS:
            return self.parse_assign()

        return self.parse_or()

    def parse_assign(self) -> Assign:
        """Parse: name = expression
        """
        target_token = self.current()
        target = target_token.value

        if target in KEYWORDS:
            raise SyntaxError(f"{target} is reserved and cannot be assigned to. (line {target_token.line})")
        self.advance()
        self.expect(TokenType.EQUALS, "Expected '=' in assignment")
        value = self.parse_or()

        if not self.check(TokenType.NEWLINE, TokenType.EOF, TokenType.RBRACE):
            token = self.current()
            raise SyntaxError(f"Chained assignment is not allowed. (line {token.line})")

        return Assign(target, value)

    # ------------------------------------------------------------------
    # Control flow
    # ------------------------------------------------------------------

    def parse_function_def(self) -> FunctionDef:
        """Parse:
            func name(a, b) {
                statements
            }
        """
        self.expect_name("func", "Expected 'func'")

        if not self.check(TokenType.NAME):
            token = self.current()
            raise SyntaxError(f"Expected function name after 'func'. (line {token.line})")

        name = self.advance().value
        self.expect(TokenType.LPAREN, "Expected '(' after function name")

        parameters: list[str] = []

        if not self.check(TokenType.RPAREN):
            while True:
                if not self.check(TokenType.NAME):
                    token = self.current()
                    raise SyntaxError(f"Expected parameter name. (line {token.line})")

                parameter = self.advance().value

                if parameter in KEYWORDS:
                    raise SyntaxError(f"{parameter} is reserved and cannot be a parameter. (line {self.current().line})")
                if parameter in parameters:
                    raise SyntaxError(f"Duplicate parameter '{parameter}'. (line {self.current().line})")

                parameters.append(parameter)

                if not self.check(TokenType.COMMA):
                    break

                self.advance()

            self.expect(TokenType.RPAREN, "Expected ')' after function parameters")

        body = self.parse_block()
        return FunctionDef(name, parameters, body)

    def parse_return(self) -> Return:
        """Parse:
            return expression
        """
        token = self.expect_name("return", "Expected 'return'")

        if self.check(TokenType.NEWLINE, TokenType.RBRACE, TokenType.EOF):
            raise SyntaxError(f"Expected expression after 'return'. (line {token.line})")

        value = self.parse_or()

        if not self.check(TokenType.NEWLINE, TokenType.RBRACE, TokenType.EOF):
            token = self.current()
            raise SyntaxError(f"Expected end of statement after return. (line {token.line}")

        return Return(value)

    def parse_if(self) -> If:
        """Parse:
            if condition {
                statements
            } else {
                statements
            }

        with an optional else block.
        """
        self.expect_name("if", "Expected 'if'")

        test = self.parse_or()
        body = self.parse_block()
        orelse: list[Statement] = []

        self.skip_newlines()

        if self.check_name("else"):
            self.advance()
            orelse = self.parse_block()

        return If(test, body, orelse)

    def parse_while(self) -> While:
        """Parse:
            while condition {
                statements
            }
        """
        self.expect_name("while", "Expected 'while'")
        test = self.parse_or()
        body = self.parse_block()

        return While(test, body)

    def parse_for_range(self) -> ForRange:
        """Parse:
            for i in range(start, stop) {
                statements
            }
        """
        self.expect_name("for", "Expected 'for'")

        if not self.check(TokenType.NAME):
            token = self.current()
            raise SyntaxError(f"Expected loop variable after 'for'. (line {token.line})")

        target = self.advance().value

        self.expect_name("in", "Expected 'in' after loop variable")
        self.expect_name("range", "Expected 'range' in for loop")

        self.expect(TokenType.LPAREN, "Expected '(' after 'range'")
        start = self.parse_or()
        self.expect(TokenType.COMMA, "Expected ',' between range arguments")
        stop = self.parse_or()
        self.expect(TokenType.RPAREN, "Expected ')' after range arguments")
        body = self.parse_block()

        return ForRange(target, start, stop, body)

    def parse_block(self) -> list[Statement]:
        """Parse a { ... } block."""
        self.expect(TokenType.LBRACE, "Expected '{' to start block")
        self.skip_newlines()

        body: list[Statement] = []

        while not self.check(TokenType.RBRACE, TokenType.EOF):
            statement = self.parse_statement()
            body.append(statement)

            if self.check(TokenType.NEWLINE):
                self.skip_newlines()
            elif not self.check(TokenType.RBRACE):
                token = self.current()
                raise SyntaxError(
                    f"Expected newline or '}}' after statement. (line {token.line})"
                )

        self.expect(TokenType.RBRACE, "Expected '}' to close block")

        return body

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def parse_or(self) -> Expr:
        """Parse logical OR expressions.
        """
        lhs = self.parse_and()

        while self.check_name('or'):
            self.advance()
            rhs = self.parse_and()
            lhs = BinOp(lhs, "or", rhs)

        return lhs

    def parse_and(self) -> Expr:
        """Parse logical AND expressions.
        """
        lhs = self.parse_equality()

        while self.check_name('and'):
            self.advance()
            rhs = self.parse_and()
            lhs = BinOp(lhs, "and", rhs)

        return lhs

    def parse_equality(self) -> Expr:
        """Parse equality comparisons.
        """
        lhs = self.parse_relational()

        while True:
            if self.check_name("equals"):
                self.advance()
                op = "equals"
            elif self.check(TokenType.BANG) and self.peek().type == TokenType.EQUALS:
                self.advance()
                self.advance()
                op = "!="
            else:
                break

            rhs = self.parse_relational()
            lhs = BinOp(lhs, op, rhs)

        return lhs

    def parse_relational(self) -> Expr:
        """Parse <, >, <= and >=.
        """
        lhs = self.parse_addition()

        while self.check(TokenType.GREATER, TokenType.LESS):
            op = self.advance().value

            if self.check(TokenType.EQUALS):
                self.advance()
                op += "="

            rhs = self.parse_addition()
            lhs = BinOp(lhs, op, rhs)

        return lhs

    def parse_addition(self) -> Expr:
        """Prase + and -.
        """
        lhs = self.parse_multiplication()

        while self.check(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            rhs = self.parse_multiplication()
            lhs = BinOp(lhs, op, rhs)

        return lhs

    def parse_multiplication(self) -> Expr:
        """Parse * and /.
        """
        lhs = self.parse_unary()

        while self.check(TokenType.STAR, TokenType.SLASH):
            op = self.advance().value
            rhs = self.parse_unary()
            lhs = BinOp(lhs, op, rhs)

        return lhs

    def parse_unary(self) -> Expr:
        """Parse unary + and -.
        """
        if self.check(TokenType.MINUS):
            self.advance()
            operand = self.parse_unary()
            return UnaryOp("-", operand)

        if self.check(TokenType.PLUS):
            self.advance()
            operand = self.parse_unary()
            return UnaryOp("+", operand)

        return self.parse_power()

    def parse_power(self) -> Expr:
        """Parse ^ expressions.

        Power is right-associative.
        """
        base = self.parse_atom()

        if not self.check(TokenType.CARET):
            return base

        self.advance()

        if self.check(TokenType.NUMBER):
            exponent = Scalar(self.advance().value)

        elif self.check(TokenType.NAME):
            name = self.advance().value
            if name == "T":
                exponent = Symbol("T")
            else:
                exponent = Name(name)

        elif self.check(TokenType.LBRACE):
            self.advance()
            exponent = self.parse_or()
            self.expect(TokenType.RBRACE, "Expected '}' to close superscript")

        else:
            token = self.current()
            raise SyntaxError(f"Expected superscript after '^'. (line {token.line})")

        return SuperscriptOp(base, exponent)

    # ------------------------------------------------------------------
    # Atoms
    # ------------------------------------------------------------------

    def parse_atom(self) -> Expr:
        """Parse a single atomic expression.
        """
        token = self.current()

        if token.type == TokenType.NUMBER:
            self.advance()
            return Scalar(token.value)
        elif token.type == TokenType.STRING:
            self.advance()
            return StringLiteral(token.value)
        elif token.type == TokenType.NAME:
            return self.parse_name_atom()
        elif token.type == TokenType.LPAREN:
            self.advance()
            expression = self.parse_or()
            self.expect(TokenType.RPAREN, "Expected ')' to close expression")
            return expression
        elif token.type == TokenType.LBRACKET:
            return self.parse_matrix()
        elif token.type == TokenType.NEWLINE:
            raise SyntaxError(f"Unexpected end of line in expression. (line {token.line})")
        elif token.type == TokenType.EOF:
            raise SyntaxError(f"Unexpected end of file in expression. (line {token.line})")
        raise SyntaxError(f"Unexpected token in expression: {token.value!r}. (line {token.line})")

    def parse_name_atom(self) -> Expr:
        """Parse names, function calls and I_n identity literals.
        """
        name_token = self.current()
        name = name_token.value

        # I_n / I_3 / I_{...}
        if name == "I" and self.peek().type == TokenType.UNDERSCORE:
            self.advance()  # I
            self.advance()  # _

            if self.check(TokenType.NUMBER):
                return IdentityLiteral(Scalar(self.advance().value))
            elif self.check(TokenType.NAME):
                return IdentityLiteral(Name(self.advance().value))
            elif self.check(TokenType.LBRACE):
                self.advance()
                size = self.parse_or()
                self.expect(TokenType.RBRACE, "Expected '}' to close identity size")
                return IdentityLiteral(size)

            token = self.current()
            raise SyntaxError(f"Expected identity size after 'I_' (line {token.line})")

        # Function call
        if self.peek().type == TokenType.LPAREN:
            return self.parse_function_call()

        self.advance()
        return Name(name)

    def parse_function_call(self) -> Expr:
        """Parse a function call.
        """
        name = self.expect(TokenType.NAME, "Expected function name").value
        self.expect(TokenType.LPAREN, "Expected '(' after function name")
        args: list[Expr] = []

        if self.check(TokenType.RPAREN):
            self.advance()
            return FuncCall(name, args)

        while True:
            args.append(self.parse_or())
            if not self.check(TokenType.COMMA):
                break
            self.advance()

        self.expect(TokenType.RPAREN, "Expected ')' to close function call")
        return FuncCall(name, args)

    def parse_matrix(self) -> MatrixLiteral:
        """Parse a matrix literal.
        """
        self.expect(TokenType.LBRACKET, "Expected '[' to start matrix")

        if self.check(TokenType.RBRACKET):
            token = self.current()
            raise SyntaxError(f"Empty matrix is not allowed. (line {token.line})")

        rows: list[list[Expr]] = []

        while not self.check(TokenType.RBRACKET, TokenType.EOF):
            row: list[Expr] = []
            if self.check(TokenType.SEMICOLON, TokenType.RBRACKET):
                token = self.current()
                raise SyntaxError(f"Matrix row cannot be empty. (line {token.line})")

            while not self.check(TokenType.SEMICOLON, TokenType.RBRACKET, TokenType.EOF):
                row.append(self.parse_or())
                if self.check(TokenType.COMMA):
                    self.advance()
                    if self.check(TokenType.SEMICOLON, TokenType.RBRACKET):
                        break
                else:
                    break

            rows.append(row)

            if self.check(TokenType.SEMICOLON):
                self.advance()

        self.expect(TokenType.RBRACKET, "Expected ']' to close matrix")
        return MatrixLiteral(rows)
