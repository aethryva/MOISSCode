"""Tests for MOISSCode Parser."""

import pytest
from moisscode.lexer import MOISSCodeLexer
from moisscode.parser import MOISSCodeParser
from moisscode.ast_nodes import (
    Program, ProtocolDef, IfStmt, LetStmt, AdministerStmt,
    TrackStmt, WhileStmt, ForEachStmt, AssessStmt, AlertStmt,
    FunctionDef, TypeDef, ReturnStmt,
)


def parse(code: str) -> Program:
    lexer = MOISSCodeLexer()
    tokens = lexer.tokenize(code)
    parser = MOISSCodeParser(tokens)
    return parser.parse_program()


# -- Protocol parsing --------------------------------------------------------

def test_empty_protocol():
    prog = parse("protocol Test { }")
    assert len(prog.protocols) == 1
    assert prog.protocols[0].name == "Test"


def test_protocol_with_input():
    prog = parse("protocol Test { input: Patient p; }")
    proto = prog.protocols[0]
    assert len(proto.inputs) == 1
    assert proto.inputs[0].name == "p"
    assert proto.inputs[0].type_name == "Patient"


def test_protocol_with_track():
    prog = parse("protocol Test { input: Patient p; track p.lactate using KAE; }")
    stmts = prog.protocols[0].body
    assert len(stmts) == 1
    assert isinstance(stmts[0], TrackStmt)
    assert stmts[0].using_kae is True


# -- Statement parsing -------------------------------------------------------

def test_administer_parsing():
    prog = parse("protocol T { administer Drug dose: 0.1 mcg/kg/min; }")
    stmt = prog.protocols[0].body[0]
    assert isinstance(stmt, AdministerStmt)
    assert stmt.drug_name == "Drug"
    assert stmt.dose_amount == 0.1
    assert stmt.dose_unit == "mcg/kg/min"


def test_if_statement():
    prog = parse("protocol T { if true { administer X dose: 1.0 mg; } }")
    stmt = prog.protocols[0].body[0]
    assert isinstance(stmt, IfStmt)
    assert len(stmt.then_block) == 1


def test_if_else_statement():
    code = """
    protocol T {
        if true {
            administer X dose: 1.0 mg;
        } else {
            administer Y dose: 2.0 mg;
        }
    }
    """
    prog = parse(code)
    stmt = prog.protocols[0].body[0]
    assert isinstance(stmt, IfStmt)
    assert stmt.else_block is not None
    assert len(stmt.else_block) == 1


def test_let_statement():
    prog = parse("protocol T { let x = 42; }")
    stmt = prog.protocols[0].body[0]
    assert isinstance(stmt, LetStmt)
    assert stmt.name == "x"


def test_while_loop():
    prog = parse("protocol T { while true { administer X dose: 1.0 mg; } }")
    stmt = prog.protocols[0].body[0]
    assert isinstance(stmt, WhileStmt)
    assert len(stmt.body) == 1


def test_for_each_loop():
    code = 'protocol T { for item in items { administer X dose: 1.0 mg; } }'
    prog = parse(code)
    stmt = prog.protocols[0].body[0]
    assert isinstance(stmt, ForEachStmt)
    assert stmt.var_name == "item"


def test_assess_statement():
    prog = parse("protocol T { assess p for sepsis; }")
    stmt = prog.protocols[0].body[0]
    assert isinstance(stmt, AssessStmt)
    assert stmt.target == "p"
    assert stmt.condition == "sepsis"


def test_alert_statement():
    code = 'protocol T { alert "Danger" severity: critical; }'
    prog = parse(code)
    stmt = prog.protocols[0].body[0]
    assert isinstance(stmt, AlertStmt)
    assert stmt.severity == "critical"


# -- Function and type definitions -------------------------------------------

def test_function_def():
    code = "function add(a, b) { return a; }"
    prog = parse(code)
    assert len(prog.function_defs) == 1
    assert prog.function_defs[0].name == "add"
    assert len(prog.function_defs[0].params) == 2


def test_type_def():
    code = "type Organism { name: str; mic: float; }"
    prog = parse(code)
    assert len(prog.type_defs) == 1
    td = prog.type_defs[0]
    assert td.name == "Organism"
    assert len(td.fields) == 2


def test_type_with_extends():
    code = "type Bacteria extends Organism { gram: str; }"
    prog = parse(code)
    td = prog.type_defs[0]
    assert td.parent == "Organism"


# -- Complex programs --------------------------------------------------------

def test_full_protocol():
    code = """
    protocol SepsisScreen {
        input: Patient p;
        track p.lactate using KAE;
        let score = med.scores.qsofa(p);
        if true {
            administer Norepinephrine dose: 0.1 mcg/kg/min;
            alert "Sepsis!" severity: critical;
        }
        assess p for sepsis;
    }
    """
    prog = parse(code)
    assert len(prog.protocols) == 1
    proto = prog.protocols[0]
    assert proto.name == "SepsisScreen"
    assert len(proto.inputs) == 1
    # body: track, let, if, assess
    assert len(proto.body) == 4


def test_multiple_protocols():
    code = """
    protocol A { input: Patient p; }
    protocol B { input: Patient p; }
    """
    prog = parse(code)
    assert len(prog.protocols) == 2
