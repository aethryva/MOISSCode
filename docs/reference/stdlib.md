# Medical Library Reference

The MOISSCode Medical Library (`med`) provides the building blocks for medical applications. All 12 modules are accessible via the `med.` prefix.

---

## Core Modules

### `med.scores`  - Clinical Scoring
Standardized medical calculators.

#### `qsofa(p: Patient) -> int`
Calculates the **quick SOFA** score for Sepsis (0-3).
- **Criteria**: RR ≥ 22, SBP ≤ 100, GCS < 15.

```moiss
if med.scores.qsofa(p) >= 2 {
    // Sepsis Protocol
}
```

### `med.io`  - Input/Output
The bridge between code and the physical world.

#### `connect_device(id: str, type: str)`
Establishes a virtual connection to a hardware device.
```moiss
med.io.connect_device("Pump_01", "InfusionPump");
```

#### `infuse(device_id: str, drug: str, rate: float)`
Commands a connected pump to start infusion.
```moiss
med.io.infuse("Pump_01", "Norepinephrine", 0.05);
```

#### `get_lab(test_name: str) -> float`
Fetches the latest lab result for the patient.
```moiss
let lactate = med.io.get_lab("Lactate");
```

### `med.finance`  - Financial Operations
Automated billing and cost tracking.

#### `bill(code: str, description: str)`
Logs a billable event (CPT/ICD-10) to the ledger.
```moiss
med.finance.bill("99291", "Critical Care - First 74 mins");
```

### `med.research`  - Data Privacy
Tools for ethical, HIPAA-compliant data handling.

#### `deidentify(p: Patient) -> Dictionary`
Returns a safe-harbor anonymized version of the patient object.
```moiss
med.research.log_to_datalake(med.research.deidentify(p));
```

---

## Clinical Modules

### `med.pk`  - Pharmacokinetics
Drug profiles, dosing, plasma curves, and interaction checks.

### `med.db`  - Database
SQLite-backed patient storage, audit trails, and alert logging.

### `med.biochem`  - Biochemistry
Enzyme kinetics (Michaelis-Menten), metabolic pathways, anion gap, osmolality.

### `med.lab`  - Laboratory
50+ lab tests across 10 panels with reference ranges. eGFR, ABG interpretation.

### `med.micro`  - Microbiology
10 organisms, MIC breakpoints (CLSI 2024), empiric therapy, Gram stain DDx.

### `med.genomics`  - Pharmacogenomics
CYP450 variants, dosing guidance (CPIC), drug-gene interactions, sequence tools.

### `med.epi`  - Epidemiology
SIR/SEIR models, R₀ calculation, herd immunity, 11 disease profiles.

### `med.nutrition`  - Clinical Nutrition
BMI, BMR (Harris-Benedict, Mifflin-St Jeor), ICU targets, TPN formulation.
