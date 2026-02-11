---
sidebar_position: 4
title: med.lab
---

# med.lab — Laboratory Engine

50+ lab tests across 10 panels with normal, critical, and panic ranges.

## Panels

CBC, BMP, CMP, LFTs, Coagulation, ABG, Cardiac, Thyroid, Inflammatory, Renal

## Methods

### `interpret(test_name, value)` → dict
Interpret a single lab value against reference ranges.

### `run_panel(panel_name, values)` → dict
Run a full panel with interpretation.

### `calculate_gfr(creatinine, age, sex)` → float
CKD-EPI 2021 race-free GFR calculation.

### `interpret_abg(pH, pCO2, HCO3)` → dict
Full acid-base interpretation.
