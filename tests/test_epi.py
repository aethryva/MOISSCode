"""Tests for med.epi - Epidemiology Module."""
import pytest
from moisscode.modules.med_epi import EpiEngine


@pytest.fixture
def epi():
    return EpiEngine()


def test_r0_sir(epi):
    result = epi.r0(beta=0.3, gamma=0.1)
    assert result["R0"] == 3.0

def test_r0_seir(epi):
    result = epi.r0(beta=0.5, gamma=0.1, sigma=0.2)
    assert result["R0"] == 5.0

def test_sir_model_runs(epi):
    result = epi.sir_model(population=10000, initial_infected=10,
                           beta=0.3, gamma=0.1, days=30)
    # Returns dict with summary + trajectory
    assert isinstance(result, dict)
    assert "R0" in result or "peak_infected" in result

def test_seir_model_runs(epi):
    result = epi.seir_model(population=10000, initial_exposed=10,
                            beta=0.3, gamma=0.1, sigma=0.2, days=30)
    assert isinstance(result, dict)

def test_incidence_rate(epi):
    result = epi.incidence_rate(new_cases=100, population_at_risk=100000)
    assert result["incidence_per_100k_per_year"] == 100.0

def test_prevalence(epi):
    result = epi.prevalence(total_cases=500, population=10000)
    assert result["prevalence_percent"] == 5.0

def test_cfr(epi):
    result = epi.cfr(deaths=10, confirmed_cases=100)
    assert result["cfr_percent"] == 10.0

def test_herd_immunity(epi):
    result = epi.herd_immunity(r0=3.0)
    assert 66 < result["threshold_percent"] < 67

def test_disease_params_covid(epi):
    result = epi.disease_params("covid19")  # no hyphen
    assert "R0" in result or "r0" in result

def test_disease_params_unknown(epi):
    result = epi.disease_params("made_up_disease")
    assert "error" in result
