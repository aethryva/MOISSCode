"""Tests for MOISSCode Interpreter."""

import pytest
from moisscode.lexer import MOISSCodeLexer
from moisscode.parser import MOISSCodeParser
from moisscode.interpreter import MOISSCodeInterpreter


def run(code: str, unsafe=False):
    """Helper: lex -> parse -> interpret, return events list."""
    lexer = MOISSCodeLexer()
    tokens = lexer.tokenize(code)
    parser = MOISSCodeParser(tokens)
    program = parser.parse_program()
    interp = MOISSCodeInterpreter()
    interp.unsafe_mode = unsafe
    return interp.execute(program)


def event_types(events):
    return [e['type'] for e in events if e['type'] != 'LOG']


# -- Protocol execution -----------------------------------------------------

def test_empty_protocol():
    events = run("protocol T { }")
    log_msgs = [e['message'] for e in events if e['type'] == 'LOG']
    assert any("Executing: T" in m for m in log_msgs)


def test_patient_input_default():
    events = run("protocol T { input: Patient p; track p.hr; }")
    track = [e for e in events if e.get('type') == 'TRACK']
    assert len(track) == 1
    assert track[0]['value'] == 110  # default patient


# -- Variable scoping -------------------------------------------------------

def test_let_and_use():
    code = "protocol T { let x = 42; }"
    events = run(code)
    let_events = [e for e in events if e.get('type') == 'LET']
    assert len(let_events) == 1
    assert let_events[0]['value'] == 42


# -- Conditionals -----------------------------------------------------------

def test_if_true_branch():
    code = """
    protocol T {
        if true {
            let x = 1;
        } else {
            let x = 2;
        }
    }
    """
    events = run(code)
    lets = [e for e in events if e.get('type') == 'LET']
    assert lets[0]['value'] == 1


def test_if_false_branch():
    code = """
    protocol T {
        if false {
            let x = 1;
        } else {
            let x = 2;
        }
    }
    """
    events = run(code)
    lets = [e for e in events if e.get('type') == 'LET']
    assert lets[0]['value'] == 2


# -- Loops -------------------------------------------------------------------

def test_while_loop_counts():
    code = """
    protocol T {
        let i = 0;
        while i < 3 {
            let i = i + 1;
        }
    }
    """
    events = run(code)
    # Should have multiple LET events from the loop
    lets = [e for e in events if e.get('type') == 'LET']
    assert len(lets) >= 2


# -- Administer with dose validation ----------------------------------------

def test_administer_safe_dose():
    code = "protocol T { administer Norepinephrine dose: 0.1 mcg/kg/min; }"
    events = run(code)
    admin = [e for e in events if e.get('type') == 'ADMINISTER']
    assert len(admin) == 1
    assert admin[0]['dose_validation'] == 'SAFE'


def test_administer_high_dose_warns():
    code = "protocol T { administer Norepinephrine dose: 5.0 mcg/kg/min; }"
    events = run(code)
    admin = [e for e in events if e.get('type') == 'ADMINISTER']
    assert admin[0]['dose_validation'] == 'WARNING'


def test_administer_toxic_dose_raises():
    code = "protocol T { administer Norepinephrine dose: 15.0 mcg/kg/min; }"
    with pytest.raises(RuntimeError, match="TOXIC"):
        run(code)


def test_administer_toxic_dose_unsafe_mode():
    code = "protocol T { administer Norepinephrine dose: 15.0 mcg/kg/min; }"
    events = run(code, unsafe=True)
    admin = [e for e in events if e.get('type') == 'ADMINISTER']
    assert len(admin) == 1  # Should not raise in unsafe mode


def test_administer_unknown_drug():
    code = "protocol T { administer InventedDrug dose: 1.0 mg; }"
    events = run(code)
    admin = [e for e in events if e.get('type') == 'ADMINISTER']
    assert admin[0]['dose_validation'] == 'UNKNOWN'


# -- Assess ------------------------------------------------------------------

def test_assess_sepsis():
    code = "protocol T { input: Patient p; assess p for sepsis; }"
    events = run(code)
    assess = [e for e in events if e.get('type') == 'ASSESS']
    assert len(assess) == 1
    assert 'score' in assess[0]


# -- Alert -------------------------------------------------------------------

def test_alert_event():
    code = 'protocol T { alert "Test alert" severity: warning; }'
    events = run(code)
    alerts = [e for e in events if e.get('type') == 'ALERT']
    assert len(alerts) == 1
    assert alerts[0]['severity'] == 'warning'


# -- Functions ---------------------------------------------------------------

def test_user_function():
    code = """
    function greet(name) {
        return name;
    }
    protocol T {
        let result = greet("hello");
    }
    """
    events = run(code)
    lets = [e for e in events if e.get('type') == 'LET']
    assert lets[0]['value'] == 'hello'


# -- Multiple protocols ------------------------------------------------------

def test_multiple_protocols():
    code = """
    protocol A { let x = 1; }
    protocol B { let y = 2; }
    """
    events = run(code)
    lets = [e for e in events if e.get('type') == 'LET']
    assert len(lets) == 2
