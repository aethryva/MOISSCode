"""Tests for med.nutrition - Clinical Nutrition Module."""
import pytest
from moisscode.modules.med_nutrition import NutritionEngine


@pytest.fixture
def nutr():
    return NutritionEngine()


def test_bmi_normal(nutr):
    result = nutr.bmi(weight_kg=70, height_cm=175)
    assert 22 < result["bmi"] < 24
    assert result["category"] == "Normal"

def test_bmi_obese(nutr):
    result = nutr.bmi(weight_kg=110, height_cm=170)
    assert result["bmi"] > 30

def test_ideal_body_weight_male(nutr):
    result = nutr.ideal_body_weight(height_cm=180, sex="M")
    assert result["ibw_kg"] > 0

def test_ideal_body_weight_female(nutr):
    result = nutr.ideal_body_weight(height_cm=165, sex="F")
    assert result["ibw_kg"] > 0

def test_adjusted_body_weight(nutr):
    result = nutr.adjusted_body_weight(actual_kg=120, height_cm=170, sex="M")
    ibw = nutr.ideal_body_weight(height_cm=170, sex="M")["ibw_kg"]
    assert ibw < result["adjusted_bw_kg"] < 120

def test_harris_benedict_male(nutr):
    result = nutr.harris_benedict(weight_kg=80, height_cm=180, age=30, sex="M")
    assert result["bee_kcal"] > 1500

def test_harris_benedict_female(nutr):
    result = nutr.harris_benedict(weight_kg=60, height_cm=165, age=25, sex="F")
    assert result["bee_kcal"] > 1200

def test_mifflin_st_jeor_male(nutr):
    result = nutr.mifflin_st_jeor(weight_kg=80, height_cm=180, age=30, sex="M")
    assert result["ree_kcal"] > 1500

def test_total_energy_sedentary(nutr):
    result = nutr.total_energy(bee_kcal=2000, activity="sedentary", stress="none")
    assert result["tee_kcal"] >= 2000

def test_total_energy_with_stress(nutr):
    result = nutr.total_energy(bee_kcal=2000, activity="sedentary", stress="sepsis")
    assert result["tee_kcal"] > 2000

def test_icu_caloric_target_acute(nutr):
    result = nutr.icu_caloric_target(weight_kg=70, phase="acute")
    assert result["calorie_target_low"] > 0

def test_icu_caloric_target_recovery(nutr):
    result = nutr.icu_caloric_target(weight_kg=70, phase="recovery")
    assert result["calorie_target_low"] > 0

def test_tpn_calculate(nutr):
    result = nutr.tpn_calculate(weight_kg=70, calorie_target=2000, protein_target_g=80)
    assert "dextrose_g" in result
    assert "lipid_g" in result

def test_maintenance_fluids_adult(nutr):
    result = nutr.maintenance_fluids(weight_kg=70)
    assert result["daily_volume_ml"] > 0

def test_maintenance_fluids_child(nutr):
    result = nutr.maintenance_fluids(weight_kg=8)
    assert result["daily_volume_ml"] == 800
