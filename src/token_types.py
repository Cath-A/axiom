"""Token types for the Axiom lexer.
"""

from enum import Enum, auto


class TokenType(Enum):
    """All possible token types in Axiom.
    """
    NAME = auto()
    NUMBER = auto()
    STRING = auto()

    EQUALS = auto()
    BANG = auto()
    GREATER = auto()
    LESS = auto()

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
