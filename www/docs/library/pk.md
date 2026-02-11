---
sidebar_position: 3
title: med.pk
---

# med.pk — Pharmacokinetic Engine

8 drug profiles with weight-based dosing, interaction checking, and plasma concentration modeling.

## Supported Drugs

| Drug | Class | Onset |
|---|---|---|
| Norepinephrine | Vasopressor | 1 min |
| Vasopressin | Vasopressor | 5 min |
| Epinephrine | Vasopressor | 1 min |
| Vancomycin | Antibiotic | 60 min |
| Furosemide | Diuretic | 30 min |
| Propofol | Sedative | 0.5 min |
| Thiamine | Vitamin | 30 min |
| Heparin | Anticoagulant | 5 min |

## Methods

### `calculate_dose(drug, weight_kg)` → dict
Weight-based dosing calculation.

### `check_interactions(drug_list)` → list
Check for known drug-drug interactions.

### `plasma_curve(drug, dose, hours)` → list
Model plasma concentration over time.

### `get_profile(drug)` → DrugProfile
Get full pharmacokinetic profile.

### `check_contraindications(drug, patient)` → list
Check patient-specific contraindications.
