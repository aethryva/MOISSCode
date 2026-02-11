---
sidebar_position: 10
title: med.fhir
---

# med.fhir — FHIR R4 Bridge

Bidirectional conversion between MOISSCode and HL7 FHIR R4 resources.

## Methods

### `to_fhir(patient)` → dict
Export a MOISSCode Patient to a FHIR R4 Bundle containing a Patient resource and LOINC-coded Observations.

11 observation types mapped: HR, BP, RR, Temp, SpO2, GCS, Lactate, Weight, Creatinine, Bilirubin, Platelets.

### `from_fhir(bundle)` → dict
Import a FHIR Bundle back into a MOISSCode-compatible patient dict.

### `medication_request(drug, dose, unit)` → dict
Build a FHIR MedicationRequest from an administer event.

### `condition(code, display, severity)` → dict
Build a FHIR Condition with SNOMED severity coding.

### `search_url(base, resource_type, params)` → str
Build a FHIR REST search URL.

### `to_json(resource)` → str
Serialize a FHIR resource to JSON.

## Example

```python
from moisscode import Patient, StandardLibrary

lib = StandardLibrary()
p = Patient(bp=88, hr=115, rr=26, lactate=4.1, sex='F')
bundle = lib.fhir.to_fhir(p)
print(lib.fhir.to_json(bundle))
```
