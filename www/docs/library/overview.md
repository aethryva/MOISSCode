---
sidebar_position: 1
title: Overview
---

# Medical Library Reference

MOISSCode ships with **13 built-in modules**, all accessible via the `med.` prefix.

## Module Index

| Module | Description |
|---|---|
| [`med.scores`](/docs/library/scores) | Clinical scores — qSOFA, SOFA |
| [`med.pk`](/docs/library/pk) | Pharmacokinetic engine — 8 drugs, dosing, interactions, plasma curves |
| [`med.lab`](/docs/library/lab) | Lab panels — 50+ tests, reference ranges, interpretation |
| [`med.micro`](/docs/library/micro) | Microbiology — organisms, MIC breakpoints, empiric therapy |
| [`med.genomics`](/docs/library/genomics) | Pharmacogenomics — CYP450, CPIC guidelines, sequence tools |
| [`med.biochem`](/docs/library/biochem) | Enzyme kinetics — Michaelis-Menten, metabolic pathways |
| [`med.epi`](/docs/library/epi) | Epidemiology — SIR/SEIR models, R₀, herd immunity |
| [`med.nutrition`](/docs/library/nutrition) | Clinical nutrition — BMI, BEE, TPN, IV fluids |
| [`med.fhir`](/docs/library/fhir) | FHIR R4 bridge — Patient ↔ Bundle, MedicationRequest |
| [`med.db`](/docs/library/db) | SQLite persistence — patients, audit trail, alerts |
| [`med.io`](/docs/library/io) | Device I/O — pumps, ventilators, lab interfaces |
| [`med.finance`](/docs/library/finance) | CPT billing and cost tracking |
| [`med.research`](/docs/library/research) | HIPAA-compliant de-identification |

## Usage

All modules are available instantly — no imports needed:

```
protocol Example {
    input: Patient p;
    let score = med.scores.qsofa(p);
    med.finance.bill("99291", "Critical Care");
}
```

From Python:

```python
from moisscode import StandardLibrary

lib = StandardLibrary()
print(lib.scores.qsofa(patient))
print(lib.pk.calculate_dose("Vancomycin", weight_kg=70))
```
