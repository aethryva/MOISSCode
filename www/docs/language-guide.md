---
sidebar_position: 2
title: Language Guide
---

# MOISSCode Language Guide

## Protocols

Every MOISSCode program contains one or more **protocols** — named blocks of clinical logic.

```
protocol SepsisScreen {
    input: Patient p;
    // statements go here
}
```

## Patient Input

Protocols declare patient inputs. The engine provides a default patient or accepts one via the API.

```
input: Patient p;
```

**Patient has these fields:** `name`, `age`, `weight`, `sex`, `bp`, `hr`, `rr`, `temp`, `spo2`, `gcs`, `lactate`

## Variables

```
let score = med.scores.qsofa(p);
let drugs = ["Vancomycin", "Meropenem"];
let threshold = 2.0;
```

## Conditionals

```
if score >= 2 {
    alert "High risk" severity: critical;
} else {
    alert "Stable" severity: info;
}
```

**Operators:** `>`, `<`, `>=`, `<=`, `==`, `!=`, `and`, `or`, `not`

## Loops

### While Loop
```
let counter = 0;
while counter < 5 {
    let counter = counter + 1;
}
```

### For-Each Loop
```
let drugs = ["A", "B", "C"];
for drug in drugs {
    alert drug severity: info;
}
```

Safety limit: **1000 iterations** maximum.

## Drug Administration

```
administer Norepinephrine dose: 0.1 mcg/kg/min;
```

The MOISS classifier automatically categorizes timing (PROPHYLACTIC, ON_TIME, PARTIAL, MARGINAL, FUTILE, TOO_LATE).

## Tracking with KAE

Track a patient value using the Kalman-Autoencoder estimator:

```
track p.lactate using KAE;
```

## Alerts

```
alert "Sepsis protocol activated" severity: critical;
alert "Monitoring" severity: info;
```

Severity levels: `critical` 🚨, `warning` ⚠️, `info` ℹ️

## Clinical Assessment

```
assess p for sepsis;
```

Automatically calculates qSOFA and assigns risk level (HIGH / MODERATE / LOW).

## Custom Types

Define domain-specific data structures:

```
type Bacteria {
    name: str;
    mic: float;
    resistant: bool;
}

type MDRBacteria extends Bacteria {
    resistance_genes: str;
}
```

Create instances:

```
let ecoli = Bacteria { name: "E.coli", mic: 0.5, resistant: false };
```

## Functions

```
function is_resistant(mic, breakpoint) {
    if mic > breakpoint {
        return true;
    }
    return false;
}

let result = is_resistant(2.0, 1.0);
```

## Lists

```
let panel = ["Vancomycin", "Meropenem", "Ceftriaxone"];
let first = panel[0];
```

## Library Calls

All 13 modules are accessed via the `med.` prefix:

```
let score = med.scores.qsofa(p);
med.io.infuse("Pump_01", "Norepinephrine", 0.1);
med.finance.bill("99291", "Critical Care");
```

## Comments

```
// This is a single-line comment
```

## Imports

```
import med.biochem;
import med.lab;
```
