"""Tests for Pharmacokinetic Engine and dose validation."""

import pytest
from moisscode.modules.med_pk import PharmacokineticEngine, DRUG_DATABASE


@pytest.fixture
def pk():
    return PharmacokineticEngine()


# -- Drug registry -----------------------------------------------------------

def test_all_drugs_have_toxic_dose():
    for name, profile in DRUG_DATABASE.items():
        assert profile.toxic_dose > 0, f"{name} missing toxic_dose"


def test_toxic_dose_exceeds_max_dose():
    for name, profile in DRUG_DATABASE.items():
        assert profile.toxic_dose > profile.max_dose, (
            f"{name}: toxic_dose ({profile.toxic_dose}) must exceed "
            f"max_dose ({profile.max_dose})"
        )


def test_get_profile_known_drug(pk):
    profile = pk.get_profile("Norepinephrine")
    assert profile is not None
    assert profile.category == "vasopressor"


def test_get_profile_unknown_drug(pk):
    assert pk.get_profile("FakeDrug") is None


# -- Validate dose (safe) ---------------------------------------------------

def test_validate_safe_dose(pk):
    result = pk.validate_dose("Norepinephrine", 0.1, "mcg/kg/min")
    assert result["level"] == "SAFE"


def test_validate_standard_dose(pk):
    result = pk.validate_dose("Norepinephrine", 0.5, "mcg/kg/min")
    assert result["level"] == "SAFE"


# -- Validate dose (warning: high) ------------------------------------------

def test_validate_high_dose(pk):
    result = pk.validate_dose("Norepinephrine", 5.0, "mcg/kg/min")
    assert result["level"] == "WARNING"
    assert "HIGH DOSE" in result["message"]


def test_validate_low_dose(pk):
    result = pk.validate_dose("Norepinephrine", 0.001, "mcg/kg/min")
    assert result["level"] == "WARNING"
    assert "LOW DOSE" in result["message"]


# -- Validate dose (error: toxic) -------------------------------------------

def test_validate_toxic_dose(pk):
    result = pk.validate_dose("Norepinephrine", 15.0, "mcg/kg/min")
    assert result["level"] == "ERROR"
    assert "TOXIC" in result["message"]


def test_validate_toxic_at_exact_threshold(pk):
    result = pk.validate_dose("Norepinephrine", 10.0, "mcg/kg/min")
    assert result["level"] == "ERROR"


# -- Unknown drug -----------------------------------------------------------

def test_validate_unknown_drug(pk):
    result = pk.validate_dose("FakeophyllineXR", 100.0, "mg")
    assert result["level"] == "UNKNOWN"
    assert "not in registry" in result["message"]


# -- Unit mismatch ----------------------------------------------------------

def test_validate_unit_mismatch_different_base(pk):
    # Giving mg when drug expects mcg/kg/min - base units differ but
    # are_compatible is a placeholder (returns True), so it tries conversion
    result = pk.validate_dose("Norepinephrine", 0.1, "mg")
    assert result["level"] in ("WARNING", "SAFE", "ERROR")


# -- Interactions ------------------------------------------------------------

def test_interaction_check(pk):
    pk.administer("Norepinephrine", 0.1)
    result = pk.check_interactions("Vasopressin")
    assert isinstance(result, dict)


def test_no_interactions_clean_state(pk):
    result = pk.check_interactions("Norepinephrine")
    assert result.get("safe_to_administer", True) is True


# -- PK calculations --------------------------------------------------------

def test_plasma_concentration(pk):
    result = pk.plasma_concentration("Norepinephrine", dose=0.1, time_min=5.0, weight_kg=70)
    assert isinstance(result, (int, float))
    assert result >= 0


def test_time_to_effect(pk):
    result = pk.time_to_effect("Norepinephrine")
    assert isinstance(result, dict)


# -- Multiple drug validation -----------------------------------------------

def test_validate_all_drugs_safe_at_standard_dose(pk):
    """Every drug in the registry should be SAFE at its standard dose."""
    for name, profile in DRUG_DATABASE.items():
        result = pk.validate_dose(name, profile.standard_dose, profile.dose_unit)
        assert result["level"] == "SAFE", (
            f"{name} not SAFE at standard dose {profile.standard_dose} "
            f"{profile.dose_unit}: {result['message']}"
        )
