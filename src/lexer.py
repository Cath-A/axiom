"""Lexer for Axiom.

Converts Axiom source code into a flat list of tokens.
"""
import ast
from typing import Any
from dataclasses import dataclass

from token_types import TokenType
from constants import TOKEN_MAPPINGS


@dataclass
class Token:
    """A single token produced by the lexer.

    Instance Attributes:
        - type: the type of the token
        - value: the literal value of the token
        - line: the source line where the token starts
    """
    type: TokenType
    value: Any
    line: int


class Lexer:
    """Convert Axiom source code into tokens.
    """
    def __init__(self, source: str) -> None:
        self.source = source
        self.index = 0
        self.line = 1
        self.tokens: list[Token] = []

    def current(self) -> str | None:
        """Return the current character, or None at EOF.
        """
        if self.index >= len(self.source):
            return None
        return self.source[self.index]

    def peek(self, offset: int = 1) -> str | None:
        """Return a character ahead of the current position.

        Bounds-safe: returns None when past the end of the source.
        """
        i = self.index + offset

        if i >= len(self.source):
            return None
        return self.source[i]

    def advance(self) -> str | None:
        """Consume and return the current character.
        """
        char = self.current()

        if self.current() is not None:
            self.index += 1
        return char

    def add_token(self, token_type: TokenType, value: Any, line: int | None = None) -> None:
        """Append a token.
        """
        self.tokens.append(
            Token(
                token_type,
                value,
                self.line if line is None else line
            )
        )

    def read_number(self) -> int | float:
        """Read an integer or floating-point number.
        """
        start_line = self.line
        number = ""
        has_dot = False

        while True:
            c = self.current()

            if c is None:
                break

            if c.isdigit():
                number += self.advance()
            elif c == ".":
                if has_dot:
                    raise SyntaxError(f"Invalid number: multiple decimal points. (line {self.line})")
                has_dot = True
                number += self.advance()
            else:
                break

        if number == ".":
            raise SyntaxError(f"Numbers must start with a digit. (line {start_line})")

        if has_dot:
            return float(number)

        return int(number)

    def read_name(self) -> str:
        """Read an identifier."""
        value = ""

        while True:
            c = self.current()
            if c is None or not c.isalnum():
                break
            value += self.advance()

        return value

    def read_string(self) -> str:
        """Read a double-quoted Axiom string.
        """
        start_line = self.line
        start = self.index
        self.advance()  # Opening quote

        while True:
            c = self.current()
            if c is None or c == '\n':
                raise SyntaxError(f"Unterminated string. (line {start_line})")
            elif c == '\\':
                self.advance()
                if self.current() is None:
                    raise SyntaxError(f"Unterminated string. (line {start_line})")
                self.advance()
                continue
            elif c == '"':
                self.advance()
                break
            self.advance()

        raw = self.source[start:self.index]

        try:
            return ast.literal_eval(raw)
        except (SyntaxError, ValueError) as exc:
            raise SyntaxError(f"Invalid string literal. (line {start_line})") from exc

    def skip_comment(self) -> None:
        """Skip a # comment up to, but not including, the newline.
        """
        while self.current() is not None and self.current() != '\n':
            self.advance()

    def tokenise(self) -> list[Token]:
        """Tokenise the entire source file.
        """
        while self.current() is not None:
            c = self.current()

            if c == "#":
                self.skip_comment()
                continue
            elif c in " \t\r":
                self.advance()
                continue
            elif c == '\n':
                self.add_token(TokenType.NEWLINE, '\n')
                self.advance()
                self.line += 1
                continue
            elif c.isdigit():
                value = self.read_number()
                self.add_token(TokenType.NUMBER, value)
                continue
            elif c == '"':
                value = self.read_string()
                self.add_token(TokenType.STRING, value)
                continue
            elif c.isalpha():
                value = self.read_name()
                self.add_token(TokenType.NAME, value)
                continue
            elif c in TOKEN_MAPPINGS:
                token_type = TOKEN_MAPPINGS[c]
                self.add_token(token_type, c)
                self.advance()
                continue
            elif c == ".":
                raise SyntaxError(f"Numbers must start with a digit, not a decimal point. (line {self.line})")

            raise SyntaxError(f"Unexpected character {c!r}. (line {self.line})")

        self.add_token(TokenType.EOF, None)
        return self.tokens
