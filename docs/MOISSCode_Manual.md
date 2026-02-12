# MOISSCode Language Reference
**Version**: 1.0.0
**By**: Aethryva Deeptech

---

## What is MOISSCode?

MOISSCode is a programming language designed for medicine. Instead of writing complex computer code, you write in **medical English**:

```moiss
protocol SepsisCheck {
    input: Patient p;
    if p.bp < 65 mmHg {
        administer Norepinephrine dose: 0.1 mcg/kg/min;
        alert "Blood pressure critical" severity: high;
    }
}
```

**That's it.** No imports, no classes, no frameworks. Just medical intent → executable logic.

---

## 1. Programs and Protocols

Everything in MOISSCode lives inside a **protocol**. A protocol is like a recipe  - it has inputs and steps.

```moiss
protocol MyProtocol {
    // Steps go here
}
```

- **`protocol`**  - Keyword that starts a new medical protocol.
- **Name**  - Give it a descriptive name (no spaces). Example: `SepsisManagement`, `BloodPressureAlert`.
- **`{ }`**  - Curly braces contain the steps.

---

## 2. Inputs (Declaring What You Need)

Before you can do anything, you tell MOISSCode what data you're working with:

```moiss
input: Patient p;
```

- **`input:`**  - Declares an input variable.
- **`Patient`**  - The type (currently: `Patient` is the main type).
- **`p`**  - A short name you'll use to refer to this patient.
- **`;`**  - Every statement ends with a semicolon.

A `Patient` object has these properties you can access:
| Property | What It Is | Example Value |
|:---|:---|:---|
| `p.bp` | Blood pressure (MAP) | `60` mmHg |
| `p.sbp` | Systolic blood pressure | `90` mmHg |
| `p.rr` | Respiratory rate | `24` /min |
| `p.gcs` | Glasgow Coma Scale | `14` |
| `p.lactate` | Serum lactate level | `3.5` mmol/L |
| `p.age` | Patient age | `55` years |
| `p.weight` | Body weight | `70.0` kg |
| `p.name` | Patient name | `"John Doe"` |

---

## 3. Variables (`let`)

Store values for later use:

```moiss
let score = med.scores.qsofa(p);
let threshold = 2;
```

- **`let`**  - Creates a new variable.
- **Name**  - Any name you choose (`score`, `threshold`, `risk_level`).
- **`=`**  - Assigns a value.
- You can optionally add a type: `let score: int = med.scores.qsofa(p);`

---

## 4. Conditions (`if` / `else`)

Make decisions based on patient data:

```moiss
if p.bp < 65 mmHg {
    alert "BP too low!" severity: critical;
    administer Norepinephrine dose: 0.1 mcg/kg/min;
} else {
    alert "BP is stable" severity: info;
}
```

### Comparison Operators
| Operator | Meaning | Example |
|:---|:---|:---|
| `<` | Less than | `p.bp < 65` |
| `>` | Greater than | `p.lactate > 4.0` |
| `<=` | Less than or equal | `score <= 1` |
| `>=` | Greater than or equal | `score >= 2` |
| `==` | Equal to | `p.gcs == 15` |
| `!=` | Not equal to | `p.gcs != 15` |

### Logical Operators
| Operator | Meaning | Example |
|:---|:---|:---|
| `and` | Both must be true | `p.bp < 65 and p.lactate > 4.0` |
| `or` | Either can be true | `p.rr > 22 or p.gcs < 15` |

---

## 5. Units (Safety System)

MOISSCode **enforces physical units**. You cannot accidentally mix incompatible units:

```moiss
// ✅ This works (both are pressure)
if p.bp < 65 mmHg { ... }

// ❌ This would be caught (pressure vs mass)
// if p.bp < 65 mg { ... }  // ERROR: mmHg vs mg
```

### Supported Units
| Category | Units |
|:---|:---|
| **Mass** | `mg`, `mcg`, `g`, `kg` |
| **Volume** | `L`, `mL` |
| **Pressure** | `mmHg` |
| **Amount** | `mmol`, `mol` |
| **Activity** | `IU` |
| **Compound** | `mcg/kg/min`, `mg/hr`, etc. |

---

## 6. Medical Actions

### `track`  - Monitor a Vital Sign
```moiss
track p.lactate using KAE;
```
- **What it does**: Starts monitoring a value using the **KAE (Kalman-Autoencoder)** algorithm.
- **Why**: KAE predicts where the value is *heading*, not just where it is now.
- **Output**: Estimated value + velocity (rate of change).

### `administer`  - Give a Drug
```moiss
administer Norepinephrine dose: 0.1 mcg/kg/min;
```
- **What it does**: Requests drug administration.
- **Safety**: Automatically runs the **MOISS Safety Check** to determine if the drug will be effective in time.
- **MOISS Classifications**:
  - `PROPHYLACTIC`  - Drug given early, plenty of time.
  - `ON_TIME`  - Drug will work just in time.
  - `PARTIAL`  - Drug may partially help.
  - `MARGINAL`  - Drug effect is uncertain.
  - `FUTILE`  - Too late for this drug to help.
  - `TOO_LATE`  - Organ damage has already occurred.

### `assess`  - Evaluate a Condition
```moiss
assess p for sepsis;
```
- **What it does**: Runs a clinical assessment using available scoring systems.
- **For `sepsis`**: Uses the **qSOFA score** (0-3).
- **Output**: Risk level (`LOW`, `MODERATE`, `HIGH`).

### `alert`  - Notify the Clinician
```moiss
alert "Patient deteriorating" severity: critical;
```
- **Severity levels**: `info`, `warning`, `high`, `critical`
- **What it does**: Sends a notification to the clinical dashboard.

---

## 7. Loops (`while`)

Repeat actions while a condition is true:

```moiss
while p.lactate > 2.0 {
    track p.lactate using KAE;
    administer Fluids dose: 500 mL;
}
```

**Safety**: Loops are automatically limited to 1,000 iterations to prevent infinite loops.

---

## 8. Medical Library (`med`)

The standard library provides built-in tools. You call them with `med.module.function()`.

### 8.1 Clinical Scores (`med.scores`)

| Function | What It Calculates | Returns |
|:---|:---|:---|
| `med.scores.qsofa(p)` | Quick SOFA score for sepsis screening | `0` to `3` |
| `med.scores.sofa(p)` | Full SOFA organ failure score | `0` to `24` |

**qSOFA Criteria** (1 point each):
- Respiratory rate ≥ 22 /min
- Systolic BP ≤ 100 mmHg
- Glasgow Coma Scale < 15

**Example:**
```moiss
let score = med.scores.qsofa(p);
if score >= 2 {
    alert "Sepsis likely!" severity: high;
}
```

### 8.2 Device Control (`med.io`)

| Function | What It Does |
|:---|:---|
| `med.io.connect_device("Pump_01", "InfusionPump")` | Registers a medical device |
| `med.io.infuse("Pump_01", "Norepinephrine", 0.05)` | Commands a pump to infuse a drug |
| `med.io.get_lab("Lactate")` | Fetches the latest lab result |
| `med.io.command("Vent_01", "START")` | Sends a command to a device |

**Example:**
```moiss
med.io.connect_device("Pump_Main", "AlarisSystem");
med.io.infuse("Pump_Main", "Norepinephrine", 0.05);

if med.io.get_lab("Lactate") > 4.0 {
    alert "Critical lactate!" severity: critical;
}
```

### 8.3 Billing (`med.finance`)

| Function | What It Does |
|:---|:---|
| `med.finance.bill("99291", "Critical Care")` | Logs a billable CPT code |

**Common CPT Codes:**
| Code | Description | Price |
|:---|:---|:---|
| `99291` | Critical Care, first 30-74 min | $285.00 |
| `99292` | Critical Care, additional 30 min | $140.00 |
| `36415` | Venous blood collection | $10.00 |
| `J0897` | Injection, Chemo | $500.00 |

**Example:**
```moiss
med.finance.bill("99291", "Critical Care - First Hour");
med.finance.bill("36415", "Blood draw for lactate");
```

### 8.4 Research & Privacy (`med.research`)

| Function | What It Does |
|:---|:---|
| `med.research.deidentify(p)` | Returns anonymized patient data (HIPAA Safe Harbor) |
| `med.research.log_to_datalake(data, "STUDY_001")` | Sends anonymized data to research database |

**What `deidentify` removes:**
- Patient name → hashed ID
- Age > 89 → reported as "90+"
- Timestamps → randomly shifted ±24 hours

**Example:**
```moiss
let safe_data = med.research.deidentify(p);
med.research.log_to_datalake(safe_data, "SEPSIS_TRIAL_2026");
```

---

## 9. Comments

Use `//` to write notes:

```moiss
// This is a comment  - it doesn't execute
track p.lactate using KAE; // Inline comment too
```

---

## 10. Complete Example: Sepsis Management Protocol

```moiss
protocol SepsisManagement {
    input: Patient p;

    // Step 1: Calculate clinical score
    let score = med.scores.qsofa(p);

    // Step 2: Track the key biomarker
    track p.lactate using KAE;

    // Step 3: Act based on the score
    if score >= 2 {
        // Connect the pump
        med.io.connect_device("Pump_01", "InfusionPump");

        // Give the drug
        administer Norepinephrine dose: 0.1 mcg/kg/min;
        med.io.infuse("Pump_01", "Norepinephrine", 0.1);

        // Alert the team
        alert "Sepsis protocol activated" severity: critical;

        // Bill for the encounter
        med.finance.bill("99291", "Critical Care");

        // Log for research (anonymized)
        let safe_data = med.research.deidentify(p);

        // Assess the patient
        assess p for sepsis;
    } else {
        alert "Patient stable - continue monitoring" severity: info;
    }
}
```

---

## 11. Gotchas & Tips

### Reserved Keywords
Words like `severity`, `protocol`, `input`, `let`, `if`, `else`, `while`, `for`, `in`, `track`, `using`, `assess`, `alert`, `administer`, `dose`, `import`, `type`, `extends`, `function`, `return`, `true`, `false`, `null`, `and`, `or`, `not` are reserved and **cannot be used as variable names**.

```moiss
// ❌ WRONG — "severity" is a keyword
let severity = med.scores.qsofa(p);

// ✅ CORRECT
let qsofa_score = med.scores.qsofa(p);
```

### No Dict Literals
MOISSCode does not support `{}` as inline dictionaries. Curly braces are for type constructors and code blocks only. Use individual function calls instead:

```moiss
// ❌ WRONG
let result = med.lab.interpret_panel("CBC", {"WBC": 18.5});

// ✅ CORRECT
let wbc = med.lab.interpret("WBC", 18.5);
```

### All Numbers Are Floats
The parser returns all numeric literals as floats (e.g., `90` becomes `90.0`). Module developers must cast where needed: `days = int(days)`.

### File Encoding
When reading `.moiss` files programmatically, use `utf-8-sig` encoding to handle BOM:
```python
with open("file.moiss", encoding="utf-8-sig") as f:
    code = f.read()
```

---

## Glossary


| Term | What It Means |
|:---|:---|
| **Protocol** | A set of medical instructions (like a recipe) |
| **KAE** | Kalman-Autoencoder  - an algorithm that predicts where a vital sign is heading |
| **MOISS** | Multi Organ Intervention State Space  - checks if a drug will work in time |
| **qSOFA** | Quick Sepsis-related Organ Failure Assessment  - a 0-3 score |
| **SOFA** | Sequential Organ Failure Assessment  - a 0-24 score |
| **CPT Code** | Current Procedural Terminology  - standardized billing codes |
| **HIPAA** | Health Insurance Portability and Accountability Act  - patient privacy law |
| **Safe Harbor** | A method of de-identifying patient data to comply with HIPAA |
| **MAP** | Mean Arterial Pressure  - average blood pressure |
| **GCS** | Glasgow Coma Scale  - consciousness assessment (3-15) |
| **Lactate** | A blood marker that rises during tissue oxygen deprivation |
| **Vasopressor** | A drug (like Norepinephrine) that raises blood pressure |
| **DSL** | Domain-Specific Language  - a programming language for a specific field |
