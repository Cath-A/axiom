"""Constants for the Axiom interpreter.
"""
from token_types import TokenType

# Rendering constants

# Matrix brackets
LEFT_TOP = '⎡'
LEFT_MIDDLE = '⎢'
LEFT_BOTTOM = '⎣'

RIGHT_TOP = '⎤'
RIGHT_MIDDLE = '⎥'
RIGHT_BOTTOM = '⎦'

# Row vector brackets
ROW_VECTOR_LEFT = '['
ROW_VECTOR_RIGHT = ']'

# Formatting
COLUMN_SEPARATOR = '  '
ROW_SEPARATOR = '\n'

# Optional spacing configuration
MIN_COLUMN_WIDTH = 1

# Lexer constants
TOKEN_MAPPINGS = {
    "=": TokenType.EQUALS,
    "!": TokenType.BANG,
    ">": TokenType.GREATER,
    "<": TokenType.LESS,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    ",": TokenType.COMMA,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    ";": TokenType.SEMICOLON,
    "^": TokenType.CARET,
    "_": TokenType.UNDERSCORE,
}

# Parser constants
KEYWORDS = ["I", "and", "or", "if", "else", "while", "for"]
