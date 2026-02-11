"""Run a .moiss protocol file through the MOISSCode engine."""

import sys
from moisscode.lexer import MOISSCodeLexer
from moisscode.parser import MOISSCodeParser
from moisscode.interpreter import MOISSCodeInterpreter
from moisscode.typesystem import Patient


def run_file(path: str, patient: Patient = None):
    """Lex, parse, and execute a .moiss file. Returns runtime events."""
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    lexer = MOISSCodeLexer()
    tokens = lexer.tokenize(code)

    parser = MOISSCodeParser(tokens)
    program = parser.parse_program()

    interpreter = MOISSCodeInterpreter()
    if patient:
        interpreter.scope['p'] = {'type': 'Patient', 'value': patient}

    events = interpreter.execute(program)

    print(f"\n=== {len(events)} Events Generated ===")
    for i, e in enumerate(events):
        print(f"  [{i+1}] {e.get('type', '?')}: {e.get('message', e)}")

    return events


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_moiss.py <file.moiss>")
        sys.exit(1)
    run_file(sys.argv[1])
