"""Example: Embedding MOISSCode in a Python application."""

from moisscode import MOISSCodeLexer, MOISSCodeParser, MOISSCodeInterpreter


def main():
    code = """
    protocol SepsisCheck {
        input: Patient p;
        if med.scores.qsofa(p) >= 1 {
            med.io.infuse("Pump_01", "Norepinephrine", 0.05);
            med.finance.bill("99291", "Critical Care");
        }
    }
    """

    lexer = MOISSCodeLexer()
    tokens = lexer.tokenize(code)

    parser = MOISSCodeParser(tokens)
    program = parser.parse_program()

    interpreter = MOISSCodeInterpreter()
    events = interpreter.execute(program)

    for e in events:
        etype = e.get('type', '?')
        if etype == 'ADMINISTER':
            print(f"DRUG: {e['drug']} @ {e['dose']}")
        elif etype == 'LOG':
            print(f"LOG:  {e['message']}")


if __name__ == "__main__":
    main()
