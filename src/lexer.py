"""Lexer for matrix-lang. Converts raw input into a flat list of tokens."""

from typing import Any
from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    """All possible token types in matrix-lang."""
    NAME = auto()
    NUMBER = auto()
    EQUALS = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    SEMICOLON = auto()
    CARET = auto()
    UNDERSCORE = auto()
    NEWLINE = auto()
    EOF = auto()


@dataclass
class Token:
    """A single token produced by the lexer.

    Instance Attributes:
        - type: the type of the token
        - value: the literal value of the token
    """
    type: TokenType
    value: Any


def _read_number(source: str, i: int) -> tuple[int | float, int]:
    """Read a number from source starting at index i.

    Returns the number as an integer or a float and the index of the last character.
    """
    number = ''
    has_dot = False
    while i < len(source) and (source[i].isdigit() or source[i] == '.'):
        if source[i] == '.':
            if number == '':
                raise SyntaxError('Numbers must start with a digit, not a decimal point')
            if has_dot:
                raise SyntaxError('Invalid number: multiple decimal points')
            has_dot = True
        number += source[i]
        i += 1

    if has_dot:
        number = float(number)
    else:
        number = int(number)

    return number, i - 1


def _read_name(source: str, i: int) -> tuple[str, int]:
    """Read a name from source starting at index i.

    Returns the name as a string and the index of the last character.
    """
    value = ''

    while i < len(source) and (source[i].isalpha() or source[i].isdigit()):
        value += source[i]
        i += 1

    return value, i - 1


def tokenise(source: str) -> list[Token]:
    """Convert a raw source string into a list of tokens."""
    tokens = []
    i = 0

    while i < len(source):
        c = source[i]
        token_value = c

        if c == ' ':
            i += 1
            continue

        elif c.isdigit():
            token_value, i = _read_number(source, i)
            token_type = TokenType.NUMBER

        elif c == '=':
            token_type = TokenType.EQUALS
        elif c == '(':
            token_type = TokenType.LPAREN
        elif c == ')':
            token_type = TokenType.RPAREN
        elif c == '{':
            token_type = TokenType.LBRACE
        elif c == '}':
            token_type = TokenType.RBRACE
        elif c == '[':
            token_type = TokenType.LBRACKET
        elif c == ']':
            token_type = TokenType.RBRACKET
        elif c == ',':
            token_type = TokenType.COMMA
        elif c == '+':
            token_type = TokenType.PLUS
        elif c == '-':
            token_type = TokenType.MINUS
        elif c == '*':
            token_type = TokenType.STAR
        elif c == '/':
            token_type = TokenType.SLASH
        elif c == ';':
            token_type = TokenType.SEMICOLON
        elif c == '^':
            token_type = TokenType.CARET
        elif c == '_':
            token_type = TokenType.UNDERSCORE    
        elif c == '\n':
            token_type = TokenType.NEWLINE
        elif c.isalpha():
            token_value, i = _read_name(source, i)
            token_type = TokenType.NAME
        elif c == '.':
            raise SyntaxError('Numbers must start with a digit, not a decimal point')
        else:
            raise SyntaxError(f'Unexpected character: {c}')

        token = Token(token_type, token_value)
        tokens.append(token)
        i += 1

    tokens.append(Token(TokenType.EOF, None))
    return tokens
