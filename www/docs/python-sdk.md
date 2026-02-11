---
sidebar_position: 10
title: Python SDK
---

# Python SDK

MOISSCode can be embedded directly in any Python application.

## Install

```bash
pip install -e .
```

## Public API

```python
from moisscode import (
    MOISSCodeLexer,       # Tokenizer
    MOISSCodeParser,      # AST parser
    MOISSCodeInterpreter, # Runtime engine
    Patient,              # Patient dataclass
    StandardLibrary,      # 13-module library
    __version__,          # "1.0.0-beta"
)
```

## Execute a Protocol

```python
from moisscode import MOISSCodeLexer, MOISSCodeParser, MOISSCodeInterpreter

code = open('my_protocol.moiss').read()

tokens = MOISSCodeLexer().tokenize(code)
program = MOISSCodeParser(tokens).parse_program()
events = MOISSCodeInterpreter().execute(program)

# events is a list of dicts
for e in events:
    if e['type'] == 'ALERT':
        print(f"Alert: {e['message']} ({e['severity']})")
    elif e['type'] == 'ADMINISTER':
        print(f"Drug: {e['drug']} at {e['dose']}")
```

## Inject Patient Data

```python
from moisscode import MOISSCodeInterpreter, Patient

patient = Patient(
    name="Jane Doe",
    age=67,
    weight=72.0,
    bp=88,
    hr=115,
    rr=26,
    temp=38.9,
    spo2=92,
    gcs=13,
    lactate=4.1,
    sex='F'
)

interp = MOISSCodeInterpreter()
interp.scope['p'] = {'type': 'Patient', 'value': patient}

# Now execute — the protocol will use your injected patient
events = interp.execute(program)
```

## Use Library Modules Directly

```python
from moisscode import Patient, StandardLibrary

lib = StandardLibrary()
p = Patient(bp=85, hr=110, rr=24, gcs=14, lactate=3.2, sex='M')

# Clinical scores
score = lib.scores.qsofa(p)

# FHIR export
bundle = lib.fhir.to_fhir(p)

# PK dosing
dose = lib.pk.calculate_dose("Vancomycin", weight_kg=70)
```

## Event Types

| Type | Fields | Description |
|---|---|---|
| `LOG` | `message` | Internal log entry |
| `TRACK` | `target`, `raw`, `kae_pos`, `kae_vel` | Value tracking with KAE |
| `ADMINISTER` | `drug`, `dose`, `moiss_class` | Drug administration |
| `ALERT` | `message`, `severity` | Clinical alert |
| `ASSESS` | `condition`, `score`, `risk` | Clinical assessment |
| `LET` | `name`, `value` | Variable assignment |
| `FOR_EACH` | `var`, `count` | Loop summary |
