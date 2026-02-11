---
sidebar_position: 13
title: med.finance
---

# med.finance — CPT Billing

Automated billing ledger with CPT code validation.

## Methods

### `bill(code, rationale)` → dict
Log a billable event. Returns entry with running total.

### `get_total()` → float
Current cumulative total.

### `get_ledger()` → list
Full billing ledger.

## Supported CPT Codes

| Code | Description | Price |
|---|---|---|
| 99291 | Critical Care, first 30–74 min | $285.00 |
| 99292 | Critical Care, addl 30 min | $140.00 |
| 36415 | Collection of venous blood | $10.00 |
| 3000F | Sepsis evaluated (Tracking) | $0.00 |
| J0897 | Injection, Chemo | $500.00 |
