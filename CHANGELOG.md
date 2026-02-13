# Changelog

All notable changes to MOISSCode are documented here. This project follows [Semantic Versioning](https://semver.org/).

---

## [2.0.0] - 2026-02-13

### 4 new modules, 4 expanded modules.

### Added: New Modules

- **med.glucose** - Diabetes and glucose management
  - HbA1c estimation (ADAG equation), eAG conversions
  - CGM analytics: Time In Range, Glucose Management Indicator, glycemic variability (CV, MAGE)
  - Insulin dosing: sensitivity factor, carb ratio, correction dose, basal rate, sliding scale, full regimen
  - DKA assessment and hypoglycemia classification (ADA criteria)

- **med.chem** - Medicinal chemistry
  - Molecular weight calculation from chemical formula
  - Lipinski's Rule of Five for oral drug-likeness screening
  - Biopharmaceutical Classification System (BCS)
  - ADMET property screening (absorption, distribution, metabolism, excretion, toxicity)
  - Toxicity analysis with LD50 and therapeutic index
  - Built-in compound database (12 drugs) with target and class search
  - Full screening pipeline combining all checks

- **med.signal** - Biosignal processing
  - Peak detection for ECG and pulse waveforms
  - Heart rate from R-R intervals with classification
  - Heart Rate Variability: SDNN, RMSSD, pNN50
  - Cardiac rhythm classification
  - SpO2 from pulse oximeter data (Beer-Lambert)
  - Moving average filter, anomaly detection
  - Respiratory rate estimation, perfusion index

- **med.icd** - Medical coding
  - ICD-10-CM database (30+ common clinical codes)
  - Code lookup, keyword search, related code retrieval
  - DRG grouping (8 common DRGs with weights)
  - SNOMED CT to ICD-10 mapping
  - Code validation and chapter filtering

### Expanded: Existing Modules

- **med.scores** - Expanded from 2 to 12 validated clinical scores:
  - NEWS2, MELD-Na, CHA2DS2-VASc, HEART, Framingham, Child-Pugh, CURB-65, Wells PE, Glasgow-Blatchford, KDIGO AKI, APACHE II

- **med.io** - Full device management overhaul:
  - Patient monitor: `read_monitor()`, `read_all_vitals()`
  - Ventilator: `send_ventilator()`, `read_ventilator()`
  - Waveform capture: `read_waveform()` for ECG, Pleth, Resp, ABP
  - Alarm management: `set_alarm()`, `check_alarms()`
  - Infusion pump: `bolus()`, `stop_infusion()`

- **med.pk** - Therapeutic drug monitoring:
  - `renal_adjust()` - Dose adjustment by eGFR
  - `hepatic_adjust()` - Dose adjustment by Child-Pugh class
  - `therapeutic_range()` - TDM range lookup
  - `trough_estimate()` - One-compartment trough prediction

- **med.research** - Clinical trial design:
  - `consent_check()` - Patient consent verification
  - `randomize()` - RCT randomization (equal/unequal, stratified, blocked)
  - `sample_size()` - Power-based sample size calculation
  - `stratify()` - Stratified allocation

### Documentation
- Full API reference pages for all 4 new modules
- Rewritten documentation for med.scores, med.io, med.pk, med.research
- Updated library overview with all 19 modules
- Added Changelog page to documentation site
- Added 2 new walkthrough examples (Diabetes CGM Dashboard, Drug Discovery Pipeline)

---

## [1.1.0] - 2026-02-09

### Added
- Gotchas & Tips documentation page
- Example Projects page with 3 production-style walkthroughs (ICU Admission, Antibiotic Stewardship, Outbreak Response)
- AI/LLM integration guide (`for-ai.md`)
- Python SDK documentation improvements

### Fixed
- Em dashes replaced globally for terminal compatibility
- Module count references corrected across all documentation
- Example file names corrected to match actual files

---

## [1.0.0] - 2026-01-26

### Initial Release
- MOISSCode language engine: lexer, parser, interpreter, type system
- 15 medical modules: scores, pk, lab, micro, genomics, biochem, epi, nutrition, fhir, db, io, finance, research, kae, moiss
- CLI tool (`moiss run`, `moiss check`, `moiss fmt`)
- Python SDK with `StandardLibrary` class
- 16-drug pharmacokinetic engine with custom drug registration
- 50+ lab tests with age/sex-adjusted reference ranges
- FHIR R4 bridge (Patient, Bundle, MedicationRequest)
- KAE biomarker tracking (Kalman-Autoencoder)
- MOISS intervention timing classifier
- Docusaurus documentation website
- 5 example protocols
