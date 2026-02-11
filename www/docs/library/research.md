---
sidebar_position: 14
title: med.research
---

# med.research — Research Privacy

HIPAA-compliant data de-identification using the Safe Harbor method.

## Methods

### `deidentify(patient)` → dict
Convert a Patient to an anonymized dictionary:
- Names → SHA-256 hash (first 12 chars)
- Ages > 89 → "90+"
- Timestamps → fuzzed ±24 hours
- Clinical data → preserved

### `log_to_datalake(anon_data, study_id)` → bool
Write anonymized data to the research data lake.

## Example

```python
from moisscode import Patient, StandardLibrary

lib = StandardLibrary()
p = Patient(name="Jane Doe", age=92, bp=88, hr=115, rr=26, sex='F')
anon = lib.research.deidentify(p)
print(anon)
# {'patient_hash': 'a3b8c1...', 'age': '90+', 'hr': 115, 'bp': 88, ...}
```
