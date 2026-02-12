"""Tests for MOISSCode Lexer."""

import pytest
from moisscode.lexer import MOISSCodeLexer


@pytest.fixture
def lexer():
    return MOISSCodeLexer()


def tok_types(lexer, code):
    """Helper: return list of token types."""
    return [t.type for t in lexer.tokenize(code)]


def tok_values(lexer, code):
    """Helper: return list of token values."""
    return [t.value for t in lexer.tokenize(code)]


# -- Basic keywords ----------------------------------------------------------

def test_protocol_keyword(lexer):
    tokens = lexer.tokenize("protocol Foo { }")
    types = [t.type for t in tokens]
    assert types == ["PROTOCOL", "ID", "LBRACE", "RBRACE"]


def test_if_else_keywords(lexer):
    types = tok_types(lexer, "if x { } else { }")
    assert "IF" in types
    assert "ELSE" in types


def test_while_keyword(lexer):
    types = tok_types(lexer, "while true { }")
    assert types[0] == "WHILE"
    assert types[1] == "TRUE"


def test_for_in_keywords(lexer):
    types = tok_types(lexer, "for item in list { }")
    assert types[:3] == ["FOR", "ID", "IN"]


def test_let_keyword(lexer):
    types = tok_types(lexer, "let x = 5;")
    assert types[0] == "LET"
    assert types[2] == "ASSIGN"
    assert types[3] == "INT"


# -- Administer and medical statements ---------------------------------------

def test_administer_statement(lexer):
    code = "administer Drug dose: 0.1 mcg/kg/min;"
    types = tok_types(lexer, code)
    assert types[0] == "ADMINISTER"
    assert "DOSE" in types
    assert "FLOAT" in types
    assert "UNIT" in types


def test_track_using_kae(lexer):
    types = tok_types(lexer, "track p.lactate using KAE;")
    assert types[0] == "TRACK"
    assert "USING" in types
    assert "KAE" in types


def test_assess_statement(lexer):
    types = tok_types(lexer, "assess p for sepsis;")
    assert types[0] == "ASSESS"
    assert types[2] == "FOR"


def test_alert_severity(lexer):
    code = 'alert "Sepsis detected" severity: critical;'
    types = tok_types(lexer, code)
    assert types[0] == "ALERT"
    assert "STRING" in types
    assert "SEVERITY" in types


# -- Literals and operators ---------------------------------------------------

def test_numeric_literals(lexer):
    tokens = lexer.tokenize("42 3.14")
    assert tokens[0].type == "INT"
    assert tokens[0].value == "42"
    assert tokens[1].type == "FLOAT"
    assert tokens[1].value == "3.14"


def test_string_literal(lexer):
    tokens = lexer.tokenize('"hello world"')
    assert tokens[0].type == "STRING"
    assert tokens[0].value == '"hello world"'


def test_comparison_operators(lexer):
    types = tok_types(lexer, ">= <= != == > <")
    assert types == ["GE", "LE", "NE", "EQ", "GT", "LT"]


def test_boolean_keywords(lexer):
    types = tok_types(lexer, "true false null")
    assert types == ["TRUE", "FALSE", "NULL"]


def test_logical_operators(lexer):
    types = tok_types(lexer, "and or not")
    assert types == ["AND", "OR", "NOT"]


# -- Units --------------------------------------------------------------------

def test_medical_units(lexer):
    tokens = lexer.tokenize("mg mcg mL mmHg")
    for t in tokens:
        assert t.type == "UNIT"


# -- Comments and whitespace --------------------------------------------------

def test_comments_ignored(lexer):
    code = "// this is a comment\nlet x = 5;"
    types = tok_types(lexer, code)
    assert "COMMENT" not in types
    assert types[0] == "LET"


# -- Error handling -----------------------------------------------------------

def test_unexpected_character_raises(lexer):
    with pytest.raises(RuntimeError, match="unexpected"):
        lexer.tokenize("$$$")


# -- Function and type definitions -------------------------------------------

def test_function_keyword(lexer):
    types = tok_types(lexer, "function calc(a, b) { return a; }")
    assert types[0] == "FUNCTION"
    assert "RETURN" in types


def test_type_extends(lexer):
    types = tok_types(lexer, "type Foo extends Bar { }")
    assert types[0] == "TYPE"
    assert types[2] == "EXTENDS"
