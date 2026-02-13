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
    import os

    with open(args.file, 'r', encoding='utf-8-sig') as f:
        code = f.read()

    lexer = MOISSCodeLexer()
    tokens = lexer.tokenize(code)

    parser = MOISSCodeParser(tokens)
    program = parser.parse_program()

    interpreter = MOISSCodeInterpreter()
    interpreter.unsafe_mode = getattr(args, 'unsafe', False)
    events = interpreter.execute(program)

    # ── Branded Summary ────────────────────────────────────────
    W = 56
    C_RESET = "\033[0m"
    C_RED = "\033[31m"
    C_BRED = "\033[1;31m"
    C_DIM = "\033[2m"
    C_YELLOW = "\033[33m"
    C_GREEN = "\033[32m"
    C_CYAN = "\033[36m"
    C_BOLD = "\033[1m"
    C_MAGENTA = "\033[35m"

    filename = os.path.basename(args.file)

    print(f"\n{C_RED}{'=' * W}{C_RESET}")
    print(f"{C_BRED}  MOISSCode{C_RESET}{C_DIM}  |  Execution Report{C_RESET}")
    print(f"{C_RED}{'=' * W}{C_RESET}")
    print(f"  {C_DIM}File:{C_RESET}  {filename}")
    print(f"  {C_DIM}Events:{C_RESET} {len(events)}")

    if args.verbose:
        # ── Group events by type ──
        logs = []
        tracks = []
        alerts = []
        admin = []
        assess = []
        lib_calls = []
        other = []

        for e in events:
            t = e.get('type', '?')
            if t == 'LOG':
                msg = e.get('message', '')
                if '[Alert]' in msg:
                    alerts.append(e)
                elif '[Track]' in msg:
                    tracks.append(e)
                elif '[Administer]' in msg:
                    admin.append(e)
                elif '[Assess]' in msg:
                    assess.append(e)
                elif '[Let]' in msg or '[If]' in msg or '[Protocol]' in msg or '[Function]' in msg or '[Type]' in msg or '[Import]' in msg:
                    logs.append(e)
                else:
                    other.append(e)
            elif t == 'TRACK':
                tracks.append(e)
            elif t == 'ALERT':
                alerts.append(e)
            elif t == 'ADMINISTER':
                admin.append(e)
            elif t == 'ASSESS':
                assess.append(e)
            elif t.endswith('_CALL'):
                lib_calls.append(e)
            else:
                other.append(e)

        # ── Execution Flow ──
        if logs:
            print(f"\n{C_CYAN}  {'─' * (W - 4)}{C_RESET}")
            print(f"  {C_CYAN}{C_BOLD}▸ Execution Flow{C_RESET}")
            print(f"{C_CYAN}  {'─' * (W - 4)}{C_RESET}")
            for e in logs:
                msg = e.get('message', str(e))
                # Color-code different log types
                if '[Protocol]' in msg:
                    print(f"  {C_BOLD}⬢{C_RESET} {msg.replace('[Protocol] ', '')}")
                elif '[Import]' in msg:
                    print(f"  {C_DIM}↳ {msg.replace('[Import] ', 'import ')}{C_RESET}")
                elif '[Type]' in msg:
                    print(f"  {C_MAGENTA}◆{C_RESET} {msg.replace('[Type] ', '')}")
                elif '[Function]' in msg:
                    print(f"  {C_MAGENTA}ƒ{C_RESET} {msg.replace('[Function] ', '')}")
                elif '[Let]' in msg:
                    val = msg.replace('[Let] ', '')
                    print(f"  {C_DIM}  ▪ let {val}{C_RESET}")
                elif '[If]' in msg:
                    cond = msg.replace('[If] ', '')
                    print(f"    {C_DIM}? {cond}{C_RESET}")

        # ── KAE Tracking ──
        if tracks:
            print(f"\n{C_GREEN}  {'─' * (W - 4)}{C_RESET}")
            print(f"  {C_GREEN}{C_BOLD}▸ KAE Biomarker Tracking{C_RESET}")
            print(f"{C_GREEN}  {'─' * (W - 4)}{C_RESET}")
            for e in tracks:
                if e.get('type') == 'TRACK':
                    target = e.get('target', '?')
                    raw = e.get('raw', e.get('value', '?'))
                    kae_pos = e.get('kae_pos')
                    if kae_pos is not None:
                        vel = e.get('kae_vel', 0)
                        trend = "↑" if vel > 0.1 else ("↓" if vel < -0.1 else "→")
                        print(f"  {C_GREEN}📊{C_RESET} {target}: {raw} → KAE: {kae_pos} {trend}")
                    else:
                        print(f"  {C_GREEN}📊{C_RESET} {target}: {raw}")
                else:
                    msg = e.get('message', str(e))
                    print(f"  {C_GREEN}📊{C_RESET} {msg.replace('[Track] ', '')}")

        # ── Alerts ──
        if alerts:
            print(f"\n{C_YELLOW}  {'─' * (W - 4)}{C_RESET}")
            print(f"  {C_YELLOW}{C_BOLD}▸ Clinical Alerts{C_RESET}")
            print(f"{C_YELLOW}  {'─' * (W - 4)}{C_RESET}")
            for e in alerts:
                if e.get('type') == 'ALERT':
                    sev = e.get('severity', 'info')
                    msg = e.get('message', '?')
                else:
                    msg = e.get('message', str(e))
                    if 'CRITICAL' in msg:
                        sev = 'critical'
                    elif 'WARNING' in msg:
                        sev = 'warning'
                    else:
                        sev = 'info'
                    msg = msg.split('] ', 1)[-1] if '] ' in msg else msg

                if sev == 'critical':
                    print(f"  {C_BRED}🚨 {msg}{C_RESET}")
                elif sev == 'warning':
                    print(f"  {C_YELLOW}⚠️  {msg}{C_RESET}")
                else:
                    print(f"  {C_DIM}ℹ️  {msg}{C_RESET}")

        # ── Drug Administration ──
        if admin:
            print(f"\n{C_RED}  {'─' * (W - 4)}{C_RESET}")
            print(f"  {C_RED}{C_BOLD}▸ Drug Administration{C_RESET}")
            print(f"{C_RED}  {'─' * (W - 4)}{C_RESET}")
            for e in admin:
                if e.get('type') == 'ADMINISTER':
                    drug = e.get('drug', '?')
                    dose = e.get('dose', '?')
                    unit = e.get('unit', '')
                    moiss = e.get('moiss_class', '')
                    vlevel = e.get('validation_level', '')
                    print(f"  {C_RED}💉{C_RESET} {drug} {dose} {unit} {C_DIM}[{moiss}|{vlevel}]{C_RESET}")
                else:
                    msg = e.get('message', str(e))
                    print(f"  {C_RED}💉{C_RESET} {msg.replace('[Administer] ', '')}")

        # ── Library Calls ──
        if lib_calls:
            print(f"\n{C_MAGENTA}  {'─' * (W - 4)}{C_RESET}")
            print(f"  {C_MAGENTA}{C_BOLD}▸ Library Calls ({len(lib_calls)}){C_RESET}")
            print(f"{C_MAGENTA}  {'─' * (W - 4)}{C_RESET}")
            # Group by module
            modules = {}
            for e in lib_calls:
                method = e.get('method', '?')
                mod = method.split('.')[1] if '.' in method else '?'
                modules.setdefault(mod, []).append(e)
            for mod, calls in modules.items():
                print(f"  {C_MAGENTA}◈{C_RESET} med.{mod} - {len(calls)} calls")

        # ── Assessments ──
        if assess:
            print(f"\n{C_BOLD}  {'─' * (W - 4)}{C_RESET}")
            print(f"  {C_BOLD}▸ Clinical Assessments{C_RESET}")
            print(f"  {'─' * (W - 4)}")
            for e in assess:
                if e.get('type') == 'ASSESS':
                    cond = e.get('condition', '?')
                    risk = e.get('risk', '?')
                    score = e.get('score', '?')
                    print(f"  🏥 {cond}: score={score}, risk={risk}")
                else:
                    msg = e.get('message', str(e))
                    print(f"  🏥 {msg.replace('[Assess] ', '')}")

    # ── Footer ──
    print(f"\n{C_RED}{'=' * W}{C_RESET}")
    print(f"  {C_DIM}MOISSCode v{get_version()} | Aethryva Deeptech{C_RESET}")
    print(f"  {C_DIM}Research Use Only{C_RESET}")
    print(f"{C_RED}{'=' * W}{C_RESET}\n")



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
