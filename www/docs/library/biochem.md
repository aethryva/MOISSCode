---
sidebar_position: 7
title: med.biochem
---

# med.biochem — Biochemistry Engine

Enzyme kinetics, metabolic pathways, and clinical chemistry calculations.

## Methods

### `michaelis_menten(S, Vmax, Km)` → float
Reaction velocity at substrate concentration S.

### `lineweaver_burk(S_values, V_values)` → dict
Double-reciprocal plot fitting.

### `inhibition(S, Vmax, Km, I, Ki)` → float
Competitive inhibition model.

### `get_enzyme(name)` → dict
Enzyme profiles: LDH, CK, ALT, AST, ALP, Amylase, Lipase, ACE.

### `pathway_atp(pathway)` → dict
ATP yield for metabolic pathways: glycolysis, krebs, beta-oxidation, urea cycle.

### `henderson_hasselbalch(pKa, acid, base)` → float
pH calculation.

### `serum_osmolality(Na, glucose, BUN)` → float
Calculated serum osmolality.

### `anion_gap(Na, Cl, HCO3)` → float
Anion gap calculation.
