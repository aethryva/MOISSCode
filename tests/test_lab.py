"""Tests for Clinical Laboratory module."""

import pytest
from moisscode.modules.med_lab import LabEngine


@pytest.fixture
def lab():
    return LabEngine()


# -- Single lab interpretation -----------------------------------------------

def test_normal_sodium(lab):
    result = lab.interpret("Na", 140.0)
    assert result["status"] == "NORMAL"


def test_low_sodium(lab):
    result = lab.interpret("Na", 125.0)
    assert result["status"] in ("LOW", "CRITICAL_LOW", "PANIC_LOW")


def test_high_sodium(lab):
    result = lab.interpret("Na", 155.0)
    assert result["status"] in ("HIGH", "CRITICAL_HIGH", "PANIC_HIGH")


def test_normal_potassium(lab):
    result = lab.interpret("K", 4.0)
    assert result["status"] == "NORMAL"


def test_critical_low_potassium(lab):
    result = lab.interpret("K", 2.0)
    assert "CRITICAL" in result["status"] or "PANIC" in result["status"]


def test_critical_high_potassium(lab):
    result = lab.interpret("K", 7.0)
    assert "CRITICAL" in result["status"] or "PANIC" in result["status"]


def test_unknown_test(lab):
    result = lab.interpret("made_up_test", 99.0)
    assert "error" in result


# -- Panel interpretation ---------------------------------------------------

def test_bmp_panel(lab):
    values = {
        "Na": 140.0,
        "K": 4.0,
        "Cl": 102.0,
        "CO2": 24.0,
        "BUN": 15.0,
        "Cr": 1.0,
        "Glucose": 90.0,
        "Ca": 9.5,
    }
    results = lab.interpret_panel("BMP", values)
    assert isinstance(results, dict)
    assert results.get("type") == "LAB_PANEL"
    assert results.get("total_tests", 0) > 0


# -- eGFR calculation -------------------------------------------------------

def test_gfr_returns_dict(lab):
    result = lab.gfr(creatinine=0.9, age=30, sex="M")
    assert isinstance(result, dict)
    assert "eGFR" in result
    assert result["eGFR"] > 0


def test_gfr_normal_young_male(lab):
    result = lab.gfr(creatinine=0.9, age=30, sex="M")
    assert result["eGFR"] > 90


def test_gfr_elevated_creatinine(lab):
    result = lab.gfr(creatinine=3.0, age=60, sex="M")
    assert result["eGFR"] < 30


def test_gfr_female_adjustment(lab):
    male = lab.gfr(creatinine=1.0, age=50, sex="M")
    female = lab.gfr(creatinine=1.0, age=50, sex="F")
    assert male["eGFR"] != female["eGFR"]


# -- ABG interpretation -----------------------------------------------------

def test_abg_normal(lab):
    result = lab.abg_interpret(ph=7.40, pco2=40.0, hco3=24.0)
    assert result["primary_disorder"] == "Normal"


def test_abg_respiratory_acidosis(lab):
    result = lab.abg_interpret(ph=7.25, pco2=60.0, hco3=24.0)
    assert "Respiratory Acidosis" in result["primary_disorder"]


def test_abg_metabolic_acidosis(lab):
    result = lab.abg_interpret(ph=7.25, pco2=30.0, hco3=16.0)
    assert "Metabolic Acidosis" in result["primary_disorder"]


# -- List tests and panels ---------------------------------------------------

def test_list_tests_returns_list(lab):
    tests = lab.list_tests()
    assert isinstance(tests, list)
    assert len(tests) > 0


def test_list_panels_returns_list(lab):
    panels = lab.list_panels()
    assert isinstance(panels, list)
    assert len(panels) > 0
