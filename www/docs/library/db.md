---
sidebar_position: 11
title: med.db
---

# med.db — Database Module

SQLite-based persistence for patients, protocol runs, alerts, and billing.

## Methods

### `save_patient(patient)` → int
Save a patient record. Returns patient ID.

### `get_patient(patient_id)` → dict
Retrieve a patient by ID.

### `log_run(protocol_name, events, patient_id)` → int
Log a protocol execution as an audit trail entry.

### `log_alert(message, severity, patient_id)` → int
Log a clinical alert.

### `log_intervention(drug, dose, patient_id)` → int
Log a drug intervention.

### `save_lab_result(patient_id, test, value)` → int
Save a lab result.

### `get_patient_history(patient_id)` → list
Retrieve all records for a patient.

Zero-configuration: database file is created automatically at `moisscode_data.db`.
