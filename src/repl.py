"""Interactive REPL and command-line entry point for the Axiom language.

Provides functions for running Axiom source code, starting the interactive
REPL, and executing Axiom programs form `.ax` files.
"""
import sys

from ast_nodes import Expr
from lexer import Lexer
from parser import Parser


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
        code = input(">>> ")

        if code in ('quit', 'exit'):
            break
        try:
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
