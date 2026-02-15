"""Tests for med.glucose - Diabetes & Glucose Management Module."""
import pytest
from moisscode.modules.med_glucose import GlucoseEngine


@pytest.fixture
def glucose():
    return GlucoseEngine()


# ── HbA1c Calculations ──

def test_hba1c_from_glucose_normal(glucose):
    result = glucose.hba1c_from_glucose(100)
    assert 4.5 < result["estimated_hba1c"] < 5.5

def test_hba1c_from_glucose_diabetic(glucose):
    result = glucose.hba1c_from_glucose(200)
    assert result["estimated_hba1c"] > 7.0

def test_glucose_from_hba1c(glucose):
    result = glucose.glucose_from_hba1c(7.0)
    assert result["estimated_mean_glucose_mgdl"] > 100


# ── Time in Range ──

def test_time_in_range_all_in_range(glucose):
    readings = [100, 110, 120, 130, 140]
    result = glucose.time_in_range(readings)
    assert result["time_in_range_pct"] == 100.0

def test_time_in_range_all_below(glucose):
    readings = [50, 55, 60]
    result = glucose.time_in_range(readings)
    assert result["time_below_range_pct"] == 100.0

def test_time_in_range_mixed(glucose):
    readings = [50, 100, 200]
    result = glucose.time_in_range(readings)
    assert 30 < result["time_in_range_pct"] < 40


# ── GMI ──

def test_gmi_normal_range(glucose):
    result = glucose.gmi(120)
    assert "gmi" in result
    assert 5.0 < result["gmi"] < 7.0


# ── Glycemic Variability ──

def test_glycemic_variability_stable(glucose):
    readings = [100, 101, 99, 100, 102]
    result = glucose.glycemic_variability(readings)
    assert result["cv_percent"] < 36.0
    assert result["target"]  # truthy string like 'CV < 36%'

def test_glycemic_variability_unstable(glucose):
    readings = [40, 300, 50, 280, 60, 250]
    result = glucose.glycemic_variability(readings)
    assert result["cv_percent"] > 36.0


# ── Insulin Sensitivity Factor ──

def test_isf_rapid(glucose):
    result = glucose.insulin_sensitivity_factor(60, "rapid")
    assert result["isf"] == 30.0

def test_isf_regular(glucose):
    result = glucose.insulin_sensitivity_factor(50, "regular")
    assert result["isf"] == 30.0


# ── Carb Ratio ──

def test_carb_ratio(glucose):
    result = glucose.carb_ratio(50)
    assert result["icr"] == 10.0


# ── Correction Dose ──

def test_correction_dose_above_target(glucose):
    result = glucose.correction_dose(250, 100, 30)
    assert result["correction_units"] == 5.0

def test_correction_dose_below_target(glucose):
    result = glucose.correction_dose(80, 120, 30)
    assert result["correction_units"] == 0


# ── Basal Rate ──

def test_basal_rate(glucose):
    result = glucose.basal_rate(40)
    assert result["basal_units_per_day"] == 20.0


# ── Sliding Scale ──

def test_sliding_scale_low(glucose):
    result = glucose.sliding_scale(120)
    assert result["recommended_dose_units"] == 0

def test_sliding_scale_high(glucose):
    result = glucose.sliding_scale(300)
    assert result["recommended_dose_units"] > 0


# ── Full Regimen ──

def test_full_regimen_returns_all_fields(glucose):
    result = glucose.full_regimen(60)
    assert "tdd" in result
    assert "basal_units_per_day" in result
    assert "isf" in result
    assert "icr" in result


# ── DKA Check ──

def test_dka_check_positive(glucose):
    result = glucose.dka_check(glucose=400, ph=7.1, bicarb=10, ketones=3.0)
    assert result["diagnosis"] != "NOT_DKA"

def test_dka_check_negative(glucose):
    result = glucose.dka_check(glucose=120, ph=7.4, bicarb=24, ketones=0)
    assert result["diagnosis"] == "NOT_DKA" or result["severity"] == "NOT_DKA"


# ── Hypo Check ──

def test_hypo_check_normal(glucose):
    result = glucose.hypo_check(90)
    assert result["level"] == 0

def test_hypo_check_level_1(glucose):
    result = glucose.hypo_check(65)
    assert result["level"] >= 1

def test_hypo_check_level_2(glucose):
    result = glucose.hypo_check(50)
    assert result["level"] >= 2
