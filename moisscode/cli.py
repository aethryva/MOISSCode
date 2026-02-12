"""MOISSCode CLI  - run, validate, and interact with MOISSCode protocols."""

import sys
import argparse
from moisscode.version import get_version

BANNER = r"""
  __  __  ___  ___ ___ ___  ___         _
 |  \/  |/ _ \|_ _/ __/ __|/ __|___  __| |___
 | |\/| | (_) || |\__ \__ \ (__/ _ \/ _` / -_)
 |_|  |_|\___/|___|___/___/\___\___/\__,_\___|
 Multi Organ Intervention State Space Code
 Aethryva Deeptech
"""

DISCLAIMER = (
    "\n\033[33m⚠️  RESEARCH USE ONLY\033[0m\n"
    "MOISSCode is a research prototype. It is NOT approved by FDA, CDSCO,\n"
    "or any regulatory body for clinical decision-making. Do not use\n"
    "MOISSCode output to make real patient care decisions.\n"
    "Aethryva Deeptech accepts no liability for clinical outcomes.\n"
)


def print_disclaimer():
    """Print the research use disclaimer."""
    print(DISCLAIMER)


def cmd_run(args):
    """Execute a .moiss protocol file."""
    print_disclaimer()

    if getattr(args, 'unsafe', False):
        print("\n\033[31;1m" + "=" * 50)
        print("  UNSAFE MODE ENABLED")
        print("  Dose validation errors will be bypassed.")
        print("  This is intended for research scenarios ONLY.")
        print("=" * 50 + "\033[0m\n")

    from moisscode.lexer import MOISSCodeLexer
    from moisscode.parser import MOISSCodeParser
    from moisscode.interpreter import MOISSCodeInterpreter

    with open(args.file, 'r', encoding='utf-8') as f:
        code = f.read()

    lexer = MOISSCodeLexer()
    tokens = lexer.tokenize(code)

    parser = MOISSCodeParser(tokens)
    program = parser.parse_program()

    interpreter = MOISSCodeInterpreter()
    interpreter.unsafe_mode = getattr(args, 'unsafe', False)
    events = interpreter.execute(program)

    print(f"\n{'=' * 50}")
    print(f"  {len(events)} events generated")
    print(f"{'=' * 50}")

    if args.verbose:
        for i, e in enumerate(events):
            print(f"  [{i + 1}] {e.get('type', '?')}: {e.get('message', e)}")


def cmd_validate(args):
    """Parse-only validation of a .moiss file."""
    print_disclaimer()
    from moisscode.lexer import MOISSCodeLexer
    from moisscode.parser import MOISSCodeParser

    with open(args.file, 'r', encoding='utf-8') as f:
        code = f.read()

    try:
        lexer = MOISSCodeLexer()
        tokens = lexer.tokenize(code)
        parser = MOISSCodeParser(tokens)
        program = parser.parse_program()

        n_proto = len(program.protocols)
        n_types = len(program.type_defs)
        n_funcs = len(program.function_defs)
        n_imps = len(program.imports)

        print(f"  ✅ Valid MOISSCode")
        print(f"     Protocols: {n_proto}  |  Types: {n_types}  |  Functions: {n_funcs}  |  Imports: {n_imps}")

    except Exception as e:
        print(f"  ❌ Syntax Error: {e}")
        sys.exit(1)


def cmd_repl(args):
    """Interactive MOISSCode REPL."""
    from moisscode.lexer import MOISSCodeLexer
    from moisscode.parser import MOISSCodeParser
    from moisscode.interpreter import MOISSCodeInterpreter

    print_disclaimer()
    print(BANNER.strip())
    print(f"REPL v{get_version()}")
    print(f"Type a protocol or statement. Use Ctrl+C to exit.\n")

    interpreter = MOISSCodeInterpreter()
    buffer = []

    while True:
        try:
            prompt = "moiss> " if not buffer else "  ...> "
            line = input(prompt)

            if line.strip() in ('exit', 'quit'):
                break

            buffer.append(line)
            code = '\n'.join(buffer)

            if code.count('{') <= code.count('}'):
                try:
                    lexer = MOISSCodeLexer()
                    tokens = lexer.tokenize(code)
                    parser = MOISSCodeParser(tokens)
                    program = parser.parse_program()
                    interpreter.execute(program)
                except Exception as e:
                    print(f"  Error: {e}")
                buffer = []

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break


def cmd_version(args):
    """Print version information."""
    print(BANNER.strip())
    print(f"v{get_version()}")


def main():
    parser = argparse.ArgumentParser(
        prog='moiss',
        description='MOISSCode  - Multi Organ Intervention State Space Code'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # moiss run
    run_parser = subparsers.add_parser('run', help='Execute a .moiss protocol file')
    run_parser.add_argument('file', help='Path to .moiss file')
    run_parser.add_argument('-v', '--verbose', action='store_true', help='Show all events')
    run_parser.add_argument('--unsafe', action='store_true', help='Bypass dose validation errors (research only)')
    run_parser.set_defaults(func=cmd_run)

    # moiss validate
    val_parser = subparsers.add_parser('validate', help='Parse-only validation')
    val_parser.add_argument('file', help='Path to .moiss file')
    val_parser.set_defaults(func=cmd_validate)

    # moiss repl
    repl_parser = subparsers.add_parser('repl', help='Interactive REPL')
    repl_parser.set_defaults(func=cmd_repl)

    # moiss version
    ver_parser = subparsers.add_parser('version', help='Print version')
    ver_parser.set_defaults(func=cmd_version)

    args = parser.parse_args()

    if not args.command:
        print(BANNER.strip())
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == '__main__':
    main()
