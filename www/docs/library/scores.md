---
sidebar_position: 2
title: med.scores
---

# med.scores — Clinical Scores

## `qsofa(patient)` → int

Quick Sequential Organ Failure Assessment (0–3):
- RR ≥ 22 → +1
- SBP ≤ 100 → +1
- GCS < 15 → +1

```
let score = med.scores.qsofa(p);
```

## `sofa(patient)` → int

Full SOFA score (0–24) across 6 organ systems: respiratory, coagulation, liver, cardiovascular, neurologic, renal.
