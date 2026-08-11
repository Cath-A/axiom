"""Interactive REPL and command-line entry point for the Axiom language.

Provides functions for running Axiom source code, starting the interactive
REPL, and executing Axiom programs form `.ax` files.
"""
import sys

from ast_nodes import Expr
from lexer import Lexer
from parser import Parser

def braces_balance(source: str) -> int:
    """Return the number of unmatched opening braces.

    Braces inside strings and comments are ignored.
    """
    balance = 0
    in_string = False
    escaped = False
    in_comment = False

    for char in source:
        if in_comment:
            if char == '\n':
                in_comment = False
            continue
        if in_string:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "#":
            in_comment = True
        elif char == "{":
            balance += 1
        elif char == "}":
            balance -= 1

    return balance


def run(source: str, env: dict) -> None:
    """Run Axiom source code in the given environment.
    """
    lexer = Lexer(source)
    tokens = lexer.tokenise()
    parser = Parser(tokens)
    module = parser.parse()

    # detect if this is a single expression statement
    if len(module.body) == 1 and isinstance(module.body[0], Expr):
        result = module.body[0].evaluate(env)
        print(result)
    else:
        module.evaluate(env)


def start_repl() -> None:
    """Start the Axiom interactive REPL.
    """
    print("Welcome to matrix-lang! \nType 'exit' or 'quit' to leave.")
    env = {}

    while True:
        try:
            code = input(">>> ")
            if code in ("quit", "exit"):
                break
            while braces_balance(code) > 0:
                code += "\n" + input("... ")
            run(code, env)
        except (SyntaxError, NameError) as e:
            print(f"{type(e).__name__}: {e}")
        except Exception as e:
            print(f"Error: {e}")


def run_file(path: str) -> None:
    """Run a .ax file."""
    try:
        with open(path) as f:
            source = f.read()

        env = {}
        run(source, env)

    except FileNotFoundError:
        print(f"File not found: {path}")

    except PermissionError:
        print(f"Permission denied: {path}")

    except (SyntaxError, NameError) as e:
        print(f"{type(e).__name__}: {e}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        start_repl()
