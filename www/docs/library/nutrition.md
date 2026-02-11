---
sidebar_position: 9
title: med.nutrition
---

# med.nutrition — Clinical Nutrition Engine

## Methods

### `bmi(weight_kg, height_m)` → dict
BMI calculation with WHO category.

### `ideal_body_weight(height_cm, sex)` → float
Devine formula.

### `adjusted_body_weight(actual, ideal)` → float
25% adjustment factor for obese patients.

### `bee(weight, height, age, sex)` → dict
Basal energy expenditure via Harris-Benedict and Mifflin-St Jeor.

### `tee(bee, activity_factor, stress_factor)` → float
Total energy expenditure.

### `icu_calories(weight_kg, bmi)` → dict
ICU caloric targets per ASPEN/SCCM 2024 guidelines.

### `tpn(weight_kg, calories, protein_gkg)` → dict
TPN formulation calculator with GIR safety check.

### `maintenance_iv(weight_kg)` → dict
Holliday-Segar method for maintenance IV fluids.
