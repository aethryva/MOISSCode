"""
med.pk  - Pharmacokinetic Engine for MOISSCode
Provides ADME profiles, drug interaction checking, and weight-based dosing.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class DrugProfile:
    """Complete pharmacokinetic profile for a drug."""
    name: str
    category: str               # e.g., "vasopressor", "antibiotic", "sedative"

    # Pharmacokinetic parameters
    bioavailability: float      # 0.0 - 1.0 (fraction absorbed)
    onset_min: float            # Minutes to initial effect
    peak_min: float             # Minutes to peak effect
    half_life_min: float        # Elimination half-life in minutes
    duration_min: float         # Total duration of action in minutes

    # Dosing
    standard_dose: float        # Standard dose amount
    dose_unit: str              # e.g., "mcg/kg/min", "mg", "mg/kg"
    max_dose: float             # Maximum safe dose
    min_dose: float             # Minimum effective dose
    toxic_dose: float = 0.0     # Dose above which is dangerously toxic (0 = not set)

    # Safety
    contraindications: List[str] = field(default_factory=list)
    interactions: Dict[str, str] = field(default_factory=dict)  # drug -> severity
    renal_adjust: bool = False  # Requires renal dose adjustment
    hepatic_adjust: bool = False  # Requires hepatic dose adjustment

    # Metabolism
    route: str = "IV"           # Administration route
    metabolism: str = "hepatic" # Primary metabolism pathway
    excretion: str = "renal"    # Primary excretion pathway


# ─── Drug Database ─────────────────────────────────────────
DRUG_DATABASE: Dict[str, DrugProfile] = {
    "Norepinephrine": DrugProfile(
        name="Norepinephrine",
        category="vasopressor",
        bioavailability=1.0,
        onset_min=1.0,
        peak_min=2.0,
        half_life_min=2.5,
        duration_min=5.0,
        standard_dose=0.1,
        dose_unit="mcg/kg/min",
        max_dose=3.3,
        min_dose=0.01,
        toxic_dose=10.0,
        contraindications=["mesenteric_ischemia", "peripheral_vascular_disease"],
        interactions={
            "MAO_inhibitors": "SEVERE",
            "Tricyclics": "MAJOR",
            "Halothane": "MAJOR",
        },
        route="IV",
        metabolism="COMT/MAO",
        excretion="renal"
    ),

    "Vasopressin": DrugProfile(
        name="Vasopressin",
        category="vasopressor",
        bioavailability=1.0,
        onset_min=1.0,
        peak_min=5.0,
        half_life_min=15.0,
        duration_min=30.0,
        standard_dose=0.04,
        dose_unit="units/min",
        max_dose=0.04,
        min_dose=0.01,
        toxic_dose=0.1,
        contraindications=["coronary_artery_disease"],
        interactions={
            "Norepinephrine": "MONITOR",
        },
        route="IV",
        metabolism="hepatic/renal",
        excretion="renal"
    ),

    "Epinephrine": DrugProfile(
        name="Epinephrine",
        category="vasopressor",
        bioavailability=1.0,
        onset_min=1.0,
        peak_min=3.0,
        half_life_min=3.5,
        duration_min=10.0,
        standard_dose=0.05,
        dose_unit="mcg/kg/min",
        max_dose=2.0,
        min_dose=0.01,
        toxic_dose=5.0,
        contraindications=["narrow_angle_glaucoma"],
        interactions={
            "Beta_blockers": "MAJOR",
            "MAO_inhibitors": "SEVERE",
        },
        route="IV",
        metabolism="COMT/MAO",
        excretion="renal"
    ),

    "Vancomycin": DrugProfile(
        name="Vancomycin",
        category="antibiotic",
        bioavailability=1.0,
        onset_min=30.0,
        peak_min=60.0,
        half_life_min=360.0,    # 6 hours
        duration_min=720.0,     # 12 hours
        standard_dose=15.0,
        dose_unit="mg/kg",
        max_dose=20.0,
        toxic_dose=40.0,
        min_dose=10.0,
        contraindications=[],
        interactions={
            "Aminoglycosides": "MAJOR",   # Nephrotoxicity
            "Furosemide": "MODERATE",     # Ototoxicity
        },
        renal_adjust=True,
        route="IV",
        metabolism="minimal",
        excretion="renal"
    ),

    "Furosemide": DrugProfile(
        name="Furosemide",
        category="diuretic",
        bioavailability=1.0,
        onset_min=5.0,
        peak_min=30.0,
        half_life_min=120.0,    # 2 hours
        duration_min=360.0,     # 6 hours
        standard_dose=40.0,
        dose_unit="mg",
        max_dose=200.0,
        toxic_dose=600.0,
        min_dose=20.0,
        contraindications=["anuria", "hepatic_coma"],
        interactions={
            "Aminoglycosides": "MAJOR",
            "Digoxin": "MODERATE",
            "Lithium": "MAJOR",
        },
        route="IV",
        metabolism="hepatic",
        excretion="renal"
    ),

    "Propofol": DrugProfile(
        name="Propofol",
        category="sedative",
        bioavailability=1.0,
        onset_min=0.5,
        peak_min=1.0,
        half_life_min=40.0,
        duration_min=10.0,
        standard_dose=50.0,
        dose_unit="mcg/kg/min",
        max_dose=200.0,
        toxic_dose=500.0,
        min_dose=5.0,
        contraindications=["egg_allergy", "propofol_infusion_syndrome_risk"],
        interactions={
            "Fentanyl": "MODERATE",
            "Midazolam": "MODERATE",
        },
        route="IV",
        metabolism="hepatic",
        excretion="renal"
    ),

    "Thiamine": DrugProfile(
        name="Thiamine",
        category="vitamin",
        bioavailability=1.0,
        onset_min=15.0,
        peak_min=60.0,
        half_life_min=360.0,    # 6 hours
        duration_min=1440.0,    # 24 hours
        standard_dose=100.0,
        dose_unit="mg",
        max_dose=500.0,
        min_dose=100.0,
        toxic_dose=1500.0,
        contraindications=[],
        interactions={},
        route="IV",
        metabolism="hepatic",
        excretion="renal"
    ),

    "Heparin": DrugProfile(
        name="Heparin",
        category="anticoagulant",
        bioavailability=1.0,
        onset_min=5.0,
        peak_min=10.0,
        half_life_min=90.0,
        duration_min=240.0,     # 4 hours
        standard_dose=18.0,
        dose_unit="units/kg/hr",
        max_dose=25.0,
        min_dose=10.0,
        toxic_dose=50.0,
        contraindications=["active_bleeding", "HIT_history", "severe_thrombocytopenia"],
        interactions={
            "Warfarin": "MAJOR",
            "NSAIDs": "MAJOR",
            "Thrombolytics": "SEVERE",
        },
        route="IV",
        metabolism="hepatic/RES",
        excretion="renal"
    ),

    # ─── Analgesics / Sedatives ─────────────────────────────
    "Morphine": DrugProfile(
        name="Morphine",
        category="analgesic",
        bioavailability=1.0,
        onset_min=5.0,
        peak_min=20.0,
        half_life_min=180.0,    # 3 hours
        duration_min=300.0,     # 5 hours
        standard_dose=0.1,
        dose_unit="mg/kg",
        max_dose=0.2,
        min_dose=0.05,
        toxic_dose=0.5,
        contraindications=["respiratory_depression", "paralytic_ileus"],
        interactions={
            "Benzodiazepines": "SEVERE",
            "MAO_inhibitors": "SEVERE",
            "Propofol": "MAJOR",
        },
        route="IV",
        metabolism="hepatic",
        excretion="renal"
    ),

    "Fentanyl": DrugProfile(
        name="Fentanyl",
        category="analgesic",
        bioavailability=1.0,
        onset_min=1.0,
        peak_min=5.0,
        half_life_min=219.0,    # 3.7 hours
        duration_min=60.0,
        standard_dose=1.0,
        dose_unit="mcg/kg",
        max_dose=5.0,
        min_dose=0.5,
        toxic_dose=15.0,
        contraindications=["respiratory_depression", "MAO_inhibitor_use"],
        interactions={
            "Benzodiazepines": "SEVERE",
            "Propofol": "MODERATE",
            "MAO_inhibitors": "SEVERE",
        },
        route="IV",
        metabolism="hepatic_CYP3A4",
        excretion="renal"
    ),

    "Midazolam": DrugProfile(
        name="Midazolam",
        category="sedative",
        bioavailability=1.0,
        onset_min=2.0,
        peak_min=5.0,
        half_life_min=120.0,    # 2 hours
        duration_min=120.0,
        standard_dose=0.05,
        dose_unit="mg/kg",
        max_dose=0.1,
        min_dose=0.02,
        toxic_dose=0.3,
        contraindications=["acute_angle_glaucoma", "myasthenia_gravis"],
        interactions={
            "Fentanyl": "MAJOR",
            "Propofol": "MODERATE",
            "Ketoconazole": "MAJOR",
        },
        route="IV",
        metabolism="hepatic_CYP3A4",
        excretion="renal"
    ),

    "Dexmedetomidine": DrugProfile(
        name="Dexmedetomidine",
        category="sedative",
        bioavailability=1.0,
        onset_min=15.0,
        peak_min=60.0,
        half_life_min=120.0,    # 2 hours
        duration_min=240.0,
        standard_dose=0.5,
        dose_unit="mcg/kg/hr",
        max_dose=1.5,
        min_dose=0.2,
        toxic_dose=4.0,
        contraindications=["heart_block", "severe_bradycardia"],
        interactions={
            "Beta_blockers": "MAJOR",
            "Digoxin": "MODERATE",
        },
        route="IV",
        metabolism="hepatic",
        excretion="renal"
    ),

    "Ketamine": DrugProfile(
        name="Ketamine",
        category="anesthetic",
        bioavailability=1.0,
        onset_min=1.0,
        peak_min=5.0,
        half_life_min=150.0,    # 2.5 hours
        duration_min=25.0,
        standard_dose=1.5,
        dose_unit="mg/kg",
        max_dose=4.5,
        min_dose=0.5,
        toxic_dose=10.0,
        contraindications=["severe_hypertension", "eclampsia", "raised_ICP"],
        interactions={
            "Theophylline": "MAJOR",
            "Thyroid_hormones": "MODERATE",
        },
        route="IV",
        metabolism="hepatic_CYP3A4",
        excretion="renal"
    ),

    # ─── Common Medications ────────────────────────────────
    "Amoxicillin": DrugProfile(
        name="Amoxicillin",
        category="antibiotic",
        bioavailability=0.95,
        onset_min=30.0,
        peak_min=120.0,
        half_life_min=60.0,     # 1 hour
        duration_min=480.0,     # 8 hours
        standard_dose=500.0,
        dose_unit="mg",
        max_dose=3000.0,
        min_dose=250.0,
        toxic_dose=6000.0,
        contraindications=["penicillin_allergy"],
        interactions={
            "Methotrexate": "MAJOR",
            "Warfarin": "MODERATE",
        },
        route="PO",
        metabolism="hepatic",
        excretion="renal"
    ),

    "Metformin": DrugProfile(
        name="Metformin",
        category="antidiabetic",
        bioavailability=0.55,
        onset_min=60.0,
        peak_min=150.0,
        half_life_min=390.0,    # 6.5 hours
        duration_min=720.0,     # 12 hours
        standard_dose=500.0,
        dose_unit="mg",
        max_dose=2550.0,
        min_dose=500.0,
        toxic_dose=5000.0,
        contraindications=["renal_failure_eGFR_below_30", "metabolic_acidosis"],
        interactions={
            "Contrast_dye": "MAJOR",
            "Alcohol": "MODERATE",
        },
        renal_adjust=True,
        route="PO",
        metabolism="none",
        excretion="renal"
    ),

    "Insulin_Regular": DrugProfile(
        name="Insulin_Regular",
        category="antidiabetic",
        bioavailability=1.0,
        onset_min=15.0,
        peak_min=60.0,
        half_life_min=60.0,
        duration_min=360.0,
        standard_dose=0.1,
        dose_unit="units/kg",
        max_dose=0.3,
        min_dose=0.05,
        toxic_dose=1.0,
        contraindications=["hypoglycemia"],
        interactions={"Beta_blockers": "MODERATE", "Thiazides": "MODERATE"},
        route="IV", metabolism="hepatic/renal", excretion="renal"
    ),

    # ─── ANTIBIOTICS (v3.0 expansion) ─────────────────────
    "Ceftriaxone": DrugProfile(
        name="Ceftriaxone", category="antibiotic", bioavailability=1.0,
        onset_min=30.0, peak_min=120.0, half_life_min=480.0, duration_min=1440.0,
        standard_dose=1000.0, dose_unit="mg", max_dose=4000.0, min_dose=250.0, toxic_dose=8000.0,
        contraindications=["cephalosporin_allergy", "neonatal_hyperbilirubinemia"],
        interactions={"Calcium_IV": "SEVERE", "Warfarin": "MODERATE"},
        route="IV", metabolism="minimal", excretion="renal/biliary"
    ),
    "Meropenem": DrugProfile(
        name="Meropenem", category="antibiotic", bioavailability=1.0,
        onset_min=15.0, peak_min=60.0, half_life_min=60.0, duration_min=480.0,
        standard_dose=1000.0, dose_unit="mg", max_dose=6000.0, min_dose=500.0, toxic_dose=12000.0,
        contraindications=["carbapenem_allergy"],
        interactions={"Valproic_Acid": "SEVERE", "Probenecid": "MODERATE"},
        renal_adjust=True, route="IV", metabolism="renal", excretion="renal"
    ),
    "Piperacillin_Tazobactam": DrugProfile(
        name="Piperacillin_Tazobactam", category="antibiotic", bioavailability=1.0,
        onset_min=15.0, peak_min=30.0, half_life_min=60.0, duration_min=480.0,
        standard_dose=4500.0, dose_unit="mg", max_dose=18000.0, min_dose=2250.0, toxic_dose=36000.0,
        contraindications=["penicillin_allergy"],
        interactions={"Methotrexate": "MAJOR", "Vancomycin": "MONITOR", "Heparin": "MODERATE"},
        renal_adjust=True, route="IV", metabolism="minimal", excretion="renal"
    ),
    "Azithromycin": DrugProfile(
        name="Azithromycin", category="antibiotic", bioavailability=0.37,
        onset_min=120.0, peak_min=180.0, half_life_min=4080.0, duration_min=14400.0,
        standard_dose=500.0, dose_unit="mg", max_dose=2000.0, min_dose=250.0, toxic_dose=4000.0,
        contraindications=["macrolide_allergy", "QT_prolongation"],
        interactions={"Warfarin": "MODERATE", "Digoxin": "MODERATE", "Amiodarone": "MAJOR"},
        route="PO", metabolism="hepatic", excretion="biliary"
    ),
    "Levofloxacin": DrugProfile(
        name="Levofloxacin", category="antibiotic", bioavailability=0.99,
        onset_min=60.0, peak_min=120.0, half_life_min=480.0, duration_min=1440.0,
        standard_dose=750.0, dose_unit="mg", max_dose=750.0, min_dose=250.0, toxic_dose=1500.0,
        contraindications=["fluoroquinolone_allergy", "myasthenia_gravis", "tendon_rupture_history"],
        interactions={"Warfarin": "MAJOR", "Theophylline": "MODERATE", "NSAIDs": "MODERATE"},
        renal_adjust=True, route="IV", metabolism="minimal", excretion="renal"
    ),
    "Ciprofloxacin": DrugProfile(
        name="Ciprofloxacin", category="antibiotic", bioavailability=0.70,
        onset_min=60.0, peak_min=120.0, half_life_min=240.0, duration_min=720.0,
        standard_dose=400.0, dose_unit="mg", max_dose=1200.0, min_dose=200.0, toxic_dose=2400.0,
        contraindications=["fluoroquinolone_allergy", "myasthenia_gravis"],
        interactions={"Theophylline": "MAJOR", "Warfarin": "MAJOR", "Tizanidine": "SEVERE"},
        renal_adjust=True, route="IV", metabolism="hepatic_CYP1A2", excretion="renal"
    ),
    "Gentamicin": DrugProfile(
        name="Gentamicin", category="antibiotic", bioavailability=1.0,
        onset_min=30.0, peak_min=60.0, half_life_min=120.0, duration_min=480.0,
        standard_dose=5.0, dose_unit="mg/kg", max_dose=7.0, min_dose=1.0, toxic_dose=10.0,
        contraindications=["aminoglycoside_allergy", "myasthenia_gravis"],
        interactions={"Vancomycin": "MAJOR", "Furosemide": "MAJOR", "Neuromuscular_blockers": "MAJOR"},
        renal_adjust=True, route="IV", metabolism="minimal", excretion="renal"
    ),
    "Metronidazole": DrugProfile(
        name="Metronidazole", category="antibiotic", bioavailability=0.90,
        onset_min=60.0, peak_min=120.0, half_life_min=480.0, duration_min=480.0,
        standard_dose=500.0, dose_unit="mg", max_dose=4000.0, min_dose=250.0, toxic_dose=8000.0,
        contraindications=["first_trimester_pregnancy"],
        interactions={"Alcohol": "SEVERE", "Warfarin": "MAJOR", "Lithium": "MAJOR"},
        hepatic_adjust=True, route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Doxycycline": DrugProfile(
        name="Doxycycline", category="antibiotic", bioavailability=0.93,
        onset_min=120.0, peak_min=180.0, half_life_min=1080.0, duration_min=1440.0,
        standard_dose=100.0, dose_unit="mg", max_dose=200.0, min_dose=100.0, toxic_dose=600.0,
        contraindications=["pregnancy", "children_under_8"],
        interactions={"Warfarin": "MODERATE", "Antacids": "MODERATE", "Isotretinoin": "MAJOR"},
        route="PO", metabolism="hepatic", excretion="fecal/renal"
    ),
    "Fluconazole": DrugProfile(
        name="Fluconazole", category="antifungal", bioavailability=0.90,
        onset_min=60.0, peak_min=120.0, half_life_min=1800.0, duration_min=1440.0,
        standard_dose=400.0, dose_unit="mg", max_dose=800.0, min_dose=100.0, toxic_dose=1600.0,
        contraindications=["azole_allergy"],
        interactions={"Warfarin": "SEVERE", "Phenytoin": "MAJOR", "Cyclosporine": "MAJOR"},
        renal_adjust=True, route="IV", metabolism="hepatic_CYP2C9", excretion="renal"
    ),
    "Amphotericin_B": DrugProfile(
        name="Amphotericin_B", category="antifungal", bioavailability=1.0,
        onset_min=60.0, peak_min=120.0, half_life_min=10080.0, duration_min=1440.0,
        standard_dose=0.5, dose_unit="mg/kg", max_dose=1.5, min_dose=0.25, toxic_dose=3.0,
        contraindications=["renal_failure"],
        interactions={"Aminoglycosides": "SEVERE", "Cyclosporine": "MAJOR", "Digoxin": "MAJOR"},
        route="IV", metabolism="minimal", excretion="renal"
    ),
    "Caspofungin": DrugProfile(
        name="Caspofungin", category="antifungal", bioavailability=1.0,
        onset_min=60.0, peak_min=120.0, half_life_min=600.0, duration_min=1440.0,
        standard_dose=50.0, dose_unit="mg", max_dose=70.0, min_dose=35.0, toxic_dose=140.0,
        contraindications=["echinocandin_allergy"],
        interactions={"Cyclosporine": "MAJOR", "Rifampin": "MODERATE"},
        hepatic_adjust=True, route="IV", metabolism="hepatic", excretion="renal/fecal"
    ),
    "Linezolid": DrugProfile(
        name="Linezolid", category="antibiotic", bioavailability=1.0,
        onset_min=60.0, peak_min=120.0, half_life_min=300.0, duration_min=720.0,
        standard_dose=600.0, dose_unit="mg", max_dose=1200.0, min_dose=600.0, toxic_dose=2400.0,
        contraindications=["MAO_inhibitor_use", "uncontrolled_hypertension"],
        interactions={"SSRIs": "SEVERE", "MAO_inhibitors": "SEVERE", "Tyramine_foods": "MAJOR"},
        route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Daptomycin": DrugProfile(
        name="Daptomycin", category="antibiotic", bioavailability=1.0,
        onset_min=30.0, peak_min=60.0, half_life_min=480.0, duration_min=1440.0,
        standard_dose=6.0, dose_unit="mg/kg", max_dose=10.0, min_dose=4.0, toxic_dose=15.0,
        contraindications=["pneumonia"],
        interactions={"Statins": "MAJOR", "Warfarin": "MONITOR"},
        renal_adjust=True, route="IV", metabolism="minimal", excretion="renal"
    ),
    "Cefazolin": DrugProfile(
        name="Cefazolin", category="antibiotic", bioavailability=1.0,
        onset_min=15.0, peak_min=30.0, half_life_min=108.0, duration_min=480.0,
        standard_dose=1000.0, dose_unit="mg", max_dose=6000.0, min_dose=500.0, toxic_dose=12000.0,
        contraindications=["cephalosporin_allergy"],
        interactions={"Probenecid": "MODERATE", "Warfarin": "MODERATE"},
        renal_adjust=True, route="IV", metabolism="minimal", excretion="renal"
    ),
    "Cefepime": DrugProfile(
        name="Cefepime", category="antibiotic", bioavailability=1.0,
        onset_min=15.0, peak_min=60.0, half_life_min=120.0, duration_min=720.0,
        standard_dose=2000.0, dose_unit="mg", max_dose=6000.0, min_dose=500.0, toxic_dose=12000.0,
        contraindications=["cephalosporin_allergy"],
        interactions={"Aminoglycosides": "MODERATE", "Furosemide": "MODERATE"},
        renal_adjust=True, route="IV", metabolism="minimal", excretion="renal"
    ),
    "TMP_SMX": DrugProfile(
        name="TMP_SMX", category="antibiotic", bioavailability=0.95,
        onset_min=60.0, peak_min=120.0, half_life_min=600.0, duration_min=720.0,
        standard_dose=160.0, dose_unit="mg", max_dose=320.0, min_dose=80.0, toxic_dose=960.0,
        contraindications=["sulfonamide_allergy", "megaloblastic_anemia", "severe_renal_failure"],
        interactions={"Warfarin": "MAJOR", "Methotrexate": "SEVERE", "ACE_inhibitors": "MAJOR"},
        renal_adjust=True, route="PO", metabolism="hepatic", excretion="renal"
    ),
    "Clindamycin": DrugProfile(
        name="Clindamycin", category="antibiotic", bioavailability=0.90,
        onset_min=30.0, peak_min=60.0, half_life_min=150.0, duration_min=480.0,
        standard_dose=600.0, dose_unit="mg", max_dose=2700.0, min_dose=150.0, toxic_dose=4800.0,
        contraindications=["C_diff_history"],
        interactions={"Neuromuscular_blockers": "MAJOR", "Erythromycin": "MAJOR"},
        hepatic_adjust=True, route="IV", metabolism="hepatic_CYP3A4", excretion="renal/biliary"
    ),
    "Colistin": DrugProfile(
        name="Colistin", category="antibiotic", bioavailability=1.0,
        onset_min=30.0, peak_min=120.0, half_life_min=300.0, duration_min=720.0,
        standard_dose=2.5, dose_unit="mg/kg", max_dose=5.0, min_dose=1.5, toxic_dose=7.5,
        contraindications=["myasthenia_gravis"],
        interactions={"Aminoglycosides": "SEVERE", "Neuromuscular_blockers": "MAJOR", "Vancomycin": "MAJOR"},
        renal_adjust=True, route="IV", metabolism="minimal", excretion="renal"
    ),
    "Rifampin": DrugProfile(
        name="Rifampin", category="antibiotic", bioavailability=0.93,
        onset_min=120.0, peak_min=180.0, half_life_min=210.0, duration_min=1440.0,
        standard_dose=600.0, dose_unit="mg", max_dose=600.0, min_dose=300.0, toxic_dose=1200.0,
        contraindications=["jaundice", "concurrent_protease_inhibitors"],
        interactions={"Warfarin": "SEVERE", "Cyclosporine": "SEVERE", "Oral_contraceptives": "SEVERE",
                      "Methadone": "SEVERE", "HIV_protease_inhibitors": "SEVERE"},
        hepatic_adjust=True, route="PO", metabolism="hepatic", excretion="biliary"
    ),

    # ─── CARDIOVASCULAR (v3.0 expansion) ──────────────────
    "Amiodarone": DrugProfile(
        name="Amiodarone", category="antiarrhythmic", bioavailability=0.50,
        onset_min=120.0, peak_min=420.0, half_life_min=57600.0, duration_min=43200.0,
        standard_dose=200.0, dose_unit="mg", max_dose=400.0, min_dose=100.0, toxic_dose=800.0,
        contraindications=["sinus_node_disease", "heart_block", "thyroid_disease"],
        interactions={"Warfarin": "SEVERE", "Digoxin": "SEVERE", "Simvastatin": "SEVERE",
                      "Cyclosporine": "MAJOR", "Fentanyl": "MAJOR"},
        hepatic_adjust=True, route="IV", metabolism="hepatic_CYP3A4", excretion="biliary"
    ),
    "Diltiazem": DrugProfile(
        name="Diltiazem", category="calcium_channel_blocker", bioavailability=0.40,
        onset_min=3.0, peak_min=15.0, half_life_min=210.0, duration_min=600.0,
        standard_dose=0.25, dose_unit="mg/kg", max_dose=0.35, min_dose=0.15, toxic_dose=1.0,
        contraindications=["heart_block", "severe_hypotension", "WPW_syndrome"],
        interactions={"Beta_blockers": "MAJOR", "Digoxin": "MAJOR", "Simvastatin": "MAJOR"},
        hepatic_adjust=True, route="IV", metabolism="hepatic_CYP3A4", excretion="renal"
    ),
    "Metoprolol": DrugProfile(
        name="Metoprolol", category="beta_blocker", bioavailability=0.50,
        onset_min=5.0, peak_min=20.0, half_life_min=210.0, duration_min=360.0,
        standard_dose=5.0, dose_unit="mg", max_dose=15.0, min_dose=2.5, toxic_dose=50.0,
        contraindications=["severe_bradycardia", "heart_block", "cardiogenic_shock", "decompensated_HF"],
        interactions={"Verapamil": "SEVERE", "Clonidine": "MAJOR", "Digoxin": "MODERATE"},
        hepatic_adjust=True, route="IV", metabolism="hepatic_CYP2D6", excretion="renal"
    ),
    "Atenolol": DrugProfile(
        name="Atenolol", category="beta_blocker", bioavailability=0.50,
        onset_min=60.0, peak_min=180.0, half_life_min=420.0, duration_min=1440.0,
        standard_dose=50.0, dose_unit="mg", max_dose=100.0, min_dose=25.0, toxic_dose=300.0,
        contraindications=["severe_bradycardia", "heart_block", "cardiogenic_shock"],
        interactions={"Verapamil": "SEVERE", "Clonidine": "MAJOR"},
        renal_adjust=True, route="PO", metabolism="minimal", excretion="renal"
    ),
    "Lisinopril": DrugProfile(
        name="Lisinopril", category="ACE_inhibitor", bioavailability=0.25,
        onset_min=60.0, peak_min=420.0, half_life_min=720.0, duration_min=1440.0,
        standard_dose=10.0, dose_unit="mg", max_dose=40.0, min_dose=2.5, toxic_dose=80.0,
        contraindications=["angioedema_history", "bilateral_renal_artery_stenosis", "pregnancy"],
        interactions={"Potassium_sparing_diuretics": "SEVERE", "Lithium": "MAJOR", "NSAIDs": "MODERATE"},
        renal_adjust=True, route="PO", metabolism="none", excretion="renal"
    ),
    "Amlodipine": DrugProfile(
        name="Amlodipine", category="calcium_channel_blocker", bioavailability=0.64,
        onset_min=360.0, peak_min=600.0, half_life_min=2160.0, duration_min=1440.0,
        standard_dose=5.0, dose_unit="mg", max_dose=10.0, min_dose=2.5, toxic_dose=30.0,
        contraindications=["severe_aortic_stenosis", "cardiogenic_shock"],
        interactions={"Simvastatin": "MAJOR", "Cyclosporine": "MODERATE"},
        hepatic_adjust=True, route="PO", metabolism="hepatic_CYP3A4", excretion="renal"
    ),
    "Nitroglycerin": DrugProfile(
        name="Nitroglycerin", category="vasodilator", bioavailability=1.0,
        onset_min=1.0, peak_min=5.0, half_life_min=3.0, duration_min=30.0,
        standard_dose=5.0, dose_unit="mcg/min", max_dose=200.0, min_dose=5.0, toxic_dose=400.0,
        contraindications=["severe_hypotension", "PDE5_inhibitor_use", "right_ventricular_MI"],
        interactions={"Sildenafil": "SEVERE", "Tadalafil": "SEVERE", "Alteplase": "MODERATE"},
        route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Dobutamine": DrugProfile(
        name="Dobutamine", category="inotrope", bioavailability=1.0,
        onset_min=2.0, peak_min=10.0, half_life_min=2.0, duration_min=10.0,
        standard_dose=5.0, dose_unit="mcg/kg/min", max_dose=20.0, min_dose=2.0, toxic_dose=40.0,
        contraindications=["IHSS", "severe_aortic_stenosis"],
        interactions={"Beta_blockers": "MAJOR", "MAO_inhibitors": "SEVERE"},
        route="IV", metabolism="COMT/MAO", excretion="renal"
    ),
    "Milrinone": DrugProfile(
        name="Milrinone", category="inotrope", bioavailability=1.0,
        onset_min=5.0, peak_min=15.0, half_life_min=144.0, duration_min=360.0,
        standard_dose=0.375, dose_unit="mcg/kg/min", max_dose=0.75, min_dose=0.125, toxic_dose=1.5,
        contraindications=["severe_aortic_stenosis"],
        interactions={"Furosemide": "MODERATE"},
        renal_adjust=True, route="IV", metabolism="minimal", excretion="renal"
    ),
    "Digoxin": DrugProfile(
        name="Digoxin", category="cardiac_glycoside", bioavailability=0.75,
        onset_min=30.0, peak_min=120.0, half_life_min=2160.0, duration_min=4320.0,
        standard_dose=0.25, dose_unit="mg", max_dose=0.5, min_dose=0.0625, toxic_dose=2.0,
        contraindications=["VT", "VF", "hypokalemia"],
        interactions={"Amiodarone": "SEVERE", "Verapamil": "MAJOR", "Quinidine": "SEVERE",
                      "Spironolactone": "MODERATE"},
        renal_adjust=True, route="PO", metabolism="minimal", excretion="renal"
    ),
    "Hydralazine": DrugProfile(
        name="Hydralazine", category="vasodilator", bioavailability=0.35,
        onset_min=10.0, peak_min=30.0, half_life_min=180.0, duration_min=360.0,
        standard_dose=10.0, dose_unit="mg", max_dose=40.0, min_dose=5.0, toxic_dose=100.0,
        contraindications=["coronary_artery_disease", "mitral_valve_rheumatic"],
        interactions={"Beta_blockers": "MODERATE", "Diuretics": "MODERATE"},
        route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Nitroprusside": DrugProfile(
        name="Nitroprusside", category="vasodilator", bioavailability=1.0,
        onset_min=0.5, peak_min=2.0, half_life_min=2.0, duration_min=10.0,
        standard_dose=0.3, dose_unit="mcg/kg/min", max_dose=10.0, min_dose=0.3, toxic_dose=15.0,
        contraindications=["compensatory_hypertension", "inadequate_cerebral_perfusion"],
        interactions={"Sildenafil": "SEVERE"},
        hepatic_adjust=True, route="IV", metabolism="RBC/hepatic", excretion="renal"
    ),
    "Losartan": DrugProfile(
        name="Losartan", category="ARB", bioavailability=0.33,
        onset_min=60.0, peak_min=180.0, half_life_min=120.0, duration_min=1440.0,
        standard_dose=50.0, dose_unit="mg", max_dose=100.0, min_dose=25.0, toxic_dose=300.0,
        contraindications=["pregnancy", "bilateral_renal_artery_stenosis"],
        interactions={"Potassium_sparing_diuretics": "MAJOR", "Lithium": "MAJOR", "NSAIDs": "MODERATE"},
        hepatic_adjust=True, route="PO", metabolism="hepatic_CYP2C9/3A4", excretion="renal/biliary"
    ),
    "Enalapril": DrugProfile(
        name="Enalapril", category="ACE_inhibitor", bioavailability=0.60,
        onset_min=60.0, peak_min=240.0, half_life_min=660.0, duration_min=1440.0,
        standard_dose=5.0, dose_unit="mg", max_dose=40.0, min_dose=1.25, toxic_dose=80.0,
        contraindications=["angioedema_history", "pregnancy"],
        interactions={"Potassium_sparing_diuretics": "SEVERE", "Lithium": "MAJOR"},
        renal_adjust=True, route="PO", metabolism="hepatic", excretion="renal"
    ),

    # ─── ANALGESICS (v3.0 expansion) ─────────────────────
    "Hydromorphone": DrugProfile(
        name="Hydromorphone", category="analgesic", bioavailability=1.0,
        onset_min=5.0, peak_min=15.0, half_life_min=150.0, duration_min=240.0,
        standard_dose=0.5, dose_unit="mg", max_dose=4.0, min_dose=0.2, toxic_dose=10.0,
        contraindications=["respiratory_depression", "paralytic_ileus"],
        interactions={"Benzodiazepines": "SEVERE", "MAO_inhibitors": "SEVERE"},
        hepatic_adjust=True, route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Remifentanil": DrugProfile(
        name="Remifentanil", category="analgesic", bioavailability=1.0,
        onset_min=1.0, peak_min=3.0, half_life_min=6.0, duration_min=10.0,
        standard_dose=0.1, dose_unit="mcg/kg/min", max_dose=0.5, min_dose=0.025, toxic_dose=2.0,
        contraindications=["epidural_use"],
        interactions={"Benzodiazepines": "SEVERE", "Propofol": "MAJOR"},
        route="IV", metabolism="plasma_esterases", excretion="renal"
    ),
    "Acetaminophen": DrugProfile(
        name="Acetaminophen", category="analgesic", bioavailability=0.85,
        onset_min=30.0, peak_min=60.0, half_life_min=120.0, duration_min=360.0,
        standard_dose=1000.0, dose_unit="mg", max_dose=4000.0, min_dose=325.0, toxic_dose=10000.0,
        contraindications=["severe_hepatic_impairment"],
        interactions={"Warfarin": "MODERATE", "Isoniazid": "MAJOR"},
        hepatic_adjust=True, route="PO", metabolism="hepatic", excretion="renal"
    ),
    "Ketorolac": DrugProfile(
        name="Ketorolac", category="NSAID", bioavailability=1.0,
        onset_min=10.0, peak_min=30.0, half_life_min=300.0, duration_min=360.0,
        standard_dose=30.0, dose_unit="mg", max_dose=120.0, min_dose=15.0, toxic_dose=240.0,
        contraindications=["active_GI_bleeding", "renal_impairment", "NSAID_allergy", "perioperative_CABG"],
        interactions={"Anticoagulants": "SEVERE", "Lithium": "MAJOR", "Methotrexate": "MAJOR"},
        renal_adjust=True, route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Lorazepam": DrugProfile(
        name="Lorazepam", category="sedative", bioavailability=0.90,
        onset_min=5.0, peak_min=15.0, half_life_min=720.0, duration_min=480.0,
        standard_dose=0.5, dose_unit="mg", max_dose=4.0, min_dose=0.5, toxic_dose=10.0,
        contraindications=["acute_angle_glaucoma", "severe_respiratory_insufficiency"],
        interactions={"Opioids": "SEVERE", "Propofol": "MAJOR", "Alcohol": "SEVERE"},
        hepatic_adjust=True, route="IV", metabolism="hepatic_glucuronidation", excretion="renal"
    ),
    "Gabapentin": DrugProfile(
        name="Gabapentin", category="anticonvulsant_analgesic", bioavailability=0.60,
        onset_min=120.0, peak_min=180.0, half_life_min=360.0, duration_min=480.0,
        standard_dose=300.0, dose_unit="mg", max_dose=3600.0, min_dose=100.0, toxic_dose=8000.0,
        contraindications=[],
        interactions={"Opioids": "MAJOR", "Antacids": "MODERATE"},
        renal_adjust=True, route="PO", metabolism="none", excretion="renal"
    ),

    # ─── ANTICOAGULANTS (v3.0 expansion) ──────────────────
    "Enoxaparin": DrugProfile(
        name="Enoxaparin", category="anticoagulant", bioavailability=0.92,
        onset_min=180.0, peak_min=240.0, half_life_min=270.0, duration_min=720.0,
        standard_dose=1.0, dose_unit="mg/kg", max_dose=1.5, min_dose=0.5, toxic_dose=3.0,
        contraindications=["active_bleeding", "HIT_history", "severe_thrombocytopenia"],
        interactions={"NSAIDs": "MAJOR", "Warfarin": "MAJOR", "Thrombolytics": "SEVERE"},
        renal_adjust=True, route="SC", metabolism="hepatic", excretion="renal"
    ),
    "Warfarin": DrugProfile(
        name="Warfarin", category="anticoagulant", bioavailability=0.95,
        onset_min=1440.0, peak_min=4320.0, half_life_min=2400.0, duration_min=7200.0,
        standard_dose=5.0, dose_unit="mg", max_dose=10.0, min_dose=1.0, toxic_dose=20.0,
        contraindications=["active_bleeding", "pregnancy", "unsupervised_dementia"],
        interactions={"Amiodarone": "SEVERE", "Rifampin": "SEVERE", "NSAIDs": "MAJOR",
                      "Fluconazole": "SEVERE", "Metronidazole": "MAJOR"},
        hepatic_adjust=True, route="PO", metabolism="hepatic_CYP2C9", excretion="renal"
    ),
    "Apixaban": DrugProfile(
        name="Apixaban", category="anticoagulant", bioavailability=0.50,
        onset_min=180.0, peak_min=240.0, half_life_min=720.0, duration_min=720.0,
        standard_dose=5.0, dose_unit="mg", max_dose=10.0, min_dose=2.5, toxic_dose=20.0,
        contraindications=["active_bleeding", "prosthetic_heart_valve"],
        interactions={"Ketoconazole": "MAJOR", "Rifampin": "MAJOR"},
        route="PO", metabolism="hepatic_CYP3A4", excretion="renal/fecal"
    ),
    "Rivaroxaban": DrugProfile(
        name="Rivaroxaban", category="anticoagulant", bioavailability=0.80,
        onset_min=120.0, peak_min=180.0, half_life_min=660.0, duration_min=1440.0,
        standard_dose=20.0, dose_unit="mg", max_dose=20.0, min_dose=10.0, toxic_dose=40.0,
        contraindications=["active_bleeding", "severe_hepatic_impairment"],
        interactions={"Ketoconazole": "MAJOR", "Rifampin": "MAJOR", "NSAIDs": "MODERATE"},
        renal_adjust=True, route="PO", metabolism="hepatic_CYP3A4", excretion="renal"
    ),
    "Alteplase": DrugProfile(
        name="Alteplase", category="thrombolytic", bioavailability=1.0,
        onset_min=5.0, peak_min=30.0, half_life_min=5.0, duration_min=60.0,
        standard_dose=0.9, dose_unit="mg/kg", max_dose=90.0, min_dose=0.5, toxic_dose=150.0,
        contraindications=["active_bleeding", "recent_surgery", "intracranial_hemorrhage", "aortic_dissection"],
        interactions={"Heparin": "SEVERE", "Anticoagulants": "SEVERE", "Antiplatelet_agents": "MAJOR"},
        route="IV", metabolism="hepatic", excretion="hepatic"
    ),
    "Clopidogrel": DrugProfile(
        name="Clopidogrel", category="antiplatelet", bioavailability=0.50,
        onset_min=120.0, peak_min=240.0, half_life_min=480.0, duration_min=7200.0,
        standard_dose=75.0, dose_unit="mg", max_dose=300.0, min_dose=75.0, toxic_dose=600.0,
        contraindications=["active_bleeding"],
        interactions={"Omeprazole": "MAJOR", "NSAIDs": "MAJOR", "Warfarin": "MAJOR"},
        hepatic_adjust=True, route="PO", metabolism="hepatic_CYP2C19", excretion="renal/fecal"
    ),
    "Ticagrelor": DrugProfile(
        name="Ticagrelor", category="antiplatelet", bioavailability=0.36,
        onset_min=60.0, peak_min=120.0, half_life_min=420.0, duration_min=720.0,
        standard_dose=90.0, dose_unit="mg", max_dose=180.0, min_dose=60.0, toxic_dose=360.0,
        contraindications=["active_bleeding", "intracranial_hemorrhage_history", "severe_hepatic_impairment"],
        interactions={"Ketoconazole": "MAJOR", "Rifampin": "MAJOR", "Simvastatin": "MODERATE",
                      "Digoxin": "MODERATE"},
        route="PO", metabolism="hepatic_CYP3A4", excretion="biliary/renal"
    ),
    "Bivalirudin": DrugProfile(
        name="Bivalirudin", category="anticoagulant", bioavailability=1.0,
        onset_min=2.0, peak_min=5.0, half_life_min=25.0, duration_min=60.0,
        standard_dose=0.75, dose_unit="mg/kg", max_dose=1.75, min_dose=0.1, toxic_dose=5.0,
        contraindications=["active_bleeding"],
        interactions={"Heparin": "MAJOR", "Thrombolytics": "SEVERE"},
        renal_adjust=True, route="IV", metabolism="proteolytic", excretion="renal"
    ),

    # ─── NEURO / PSYCH (v3.0 expansion) ──────────────────
    "Levetiracetam": DrugProfile(
        name="Levetiracetam", category="anticonvulsant", bioavailability=1.0,
        onset_min=30.0, peak_min=60.0, half_life_min=420.0, duration_min=720.0,
        standard_dose=500.0, dose_unit="mg", max_dose=3000.0, min_dose=250.0, toxic_dose=6000.0,
        contraindications=[], interactions={},
        renal_adjust=True, route="IV", metabolism="minimal", excretion="renal"
    ),
    "Phenytoin": DrugProfile(
        name="Phenytoin", category="anticonvulsant", bioavailability=0.90,
        onset_min=30.0, peak_min=120.0, half_life_min=1320.0, duration_min=1440.0,
        standard_dose=15.0, dose_unit="mg/kg", max_dose=20.0, min_dose=10.0, toxic_dose=30.0,
        contraindications=["sinus_bradycardia", "heart_block", "Adams-Stokes_syndrome"],
        interactions={"Warfarin": "MAJOR", "Carbamazepine": "MAJOR", "Valproic_Acid": "MAJOR"},
        hepatic_adjust=True, route="IV", metabolism="hepatic_CYP2C9/2C19", excretion="renal"
    ),
    "Valproic_Acid": DrugProfile(
        name="Valproic_Acid", category="anticonvulsant", bioavailability=1.0,
        onset_min=15.0, peak_min=60.0, half_life_min=660.0, duration_min=720.0,
        standard_dose=20.0, dose_unit="mg/kg", max_dose=60.0, min_dose=10.0, toxic_dose=100.0,
        contraindications=["hepatic_disease", "urea_cycle_disorders", "pregnancy"],
        interactions={"Meropenem": "SEVERE", "Lamotrigine": "MAJOR", "Phenobarbital": "MAJOR"},
        hepatic_adjust=True, route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Haloperidol": DrugProfile(
        name="Haloperidol", category="antipsychotic", bioavailability=0.60,
        onset_min=10.0, peak_min=30.0, half_life_min=1080.0, duration_min=1440.0,
        standard_dose=2.0, dose_unit="mg", max_dose=20.0, min_dose=0.5, toxic_dose=40.0,
        contraindications=["Parkinson_disease", "QT_prolongation", "CNS_depression"],
        interactions={"Lithium": "MAJOR", "Carbamazepine": "MODERATE", "QT_prolonging_drugs": "SEVERE"},
        hepatic_adjust=True, route="IV", metabolism="hepatic_CYP3A4/2D6", excretion="renal"
    ),
    "Olanzapine": DrugProfile(
        name="Olanzapine", category="antipsychotic", bioavailability=0.60,
        onset_min=15.0, peak_min=30.0, half_life_min=1800.0, duration_min=1440.0,
        standard_dose=5.0, dose_unit="mg", max_dose=20.0, min_dose=2.5, toxic_dose=40.0,
        contraindications=["benzodiazepine_concurrent_IM"],
        interactions={"Carbamazepine": "MAJOR", "Fluvoxamine": "MAJOR", "Diazepam": "MODERATE"},
        hepatic_adjust=True, route="IM", metabolism="hepatic_CYP1A2/2D6", excretion="renal"
    ),
    "Lacosamide": DrugProfile(
        name="Lacosamide", category="anticonvulsant", bioavailability=1.0,
        onset_min=30.0, peak_min=60.0, half_life_min=780.0, duration_min=720.0,
        standard_dose=200.0, dose_unit="mg", max_dose=400.0, min_dose=50.0, toxic_dose=800.0,
        contraindications=["second_or_third_degree_heart_block"],
        interactions={"Carbamazepine": "MODERATE", "PR_prolonging_drugs": "MAJOR"},
        renal_adjust=True, route="IV", metabolism="hepatic_CYP2C19", excretion="renal"
    ),
    "Carbamazepine": DrugProfile(
        name="Carbamazepine", category="anticonvulsant", bioavailability=0.85,
        onset_min=120.0, peak_min=360.0, half_life_min=1080.0, duration_min=720.0,
        standard_dose=200.0, dose_unit="mg", max_dose=1600.0, min_dose=100.0, toxic_dose=3200.0,
        contraindications=["bone_marrow_suppression", "MAO_inhibitor_use", "HLA_B1502_positive"],
        interactions={"Warfarin": "MAJOR", "Phenytoin": "MAJOR", "Oral_contraceptives": "MAJOR"},
        hepatic_adjust=True, route="PO", metabolism="hepatic_CYP3A4", excretion="renal"
    ),
    "Quetiapine": DrugProfile(
        name="Quetiapine", category="antipsychotic", bioavailability=0.09,
        onset_min=60.0, peak_min=90.0, half_life_min=420.0, duration_min=720.0,
        standard_dose=25.0, dose_unit="mg", max_dose=800.0, min_dose=25.0, toxic_dose=1600.0,
        contraindications=["dementia_related_psychosis"],
        interactions={"Ketoconazole": "MAJOR", "Carbamazepine": "MAJOR", "QT_prolonging_drugs": "MAJOR"},
        hepatic_adjust=True, route="PO", metabolism="hepatic_CYP3A4", excretion="renal"
    ),

    # ─── GI / ENDOCRINE (v3.0 expansion) ─────────────────
    "Omeprazole": DrugProfile(
        name="Omeprazole", category="PPI", bioavailability=0.40,
        onset_min=60.0, peak_min=120.0, half_life_min=60.0, duration_min=1440.0,
        standard_dose=40.0, dose_unit="mg", max_dose=80.0, min_dose=20.0, toxic_dose=160.0,
        contraindications=["rilpivirine_use"],
        interactions={"Clopidogrel": "MAJOR", "Methotrexate": "MAJOR", "Diazepam": "MODERATE"},
        hepatic_adjust=True, route="IV", metabolism="hepatic_CYP2C19/3A4", excretion="renal"
    ),
    "Pantoprazole": DrugProfile(
        name="Pantoprazole", category="PPI", bioavailability=0.77,
        onset_min=120.0, peak_min=150.0, half_life_min=60.0, duration_min=1440.0,
        standard_dose=40.0, dose_unit="mg", max_dose=80.0, min_dose=20.0, toxic_dose=240.0,
        contraindications=["rilpivirine_use"],
        interactions={"Methotrexate": "MAJOR", "Warfarin": "MODERATE"},
        route="IV", metabolism="hepatic_CYP2C19", excretion="renal"
    ),
    "Ondansetron": DrugProfile(
        name="Ondansetron", category="antiemetic", bioavailability=0.60,
        onset_min=5.0, peak_min=15.0, half_life_min=210.0, duration_min=480.0,
        standard_dose=4.0, dose_unit="mg", max_dose=16.0, min_dose=4.0, toxic_dose=32.0,
        contraindications=["QT_prolongation", "congenital_long_QT"],
        interactions={"Apomorphine": "SEVERE", "QT_prolonging_drugs": "MAJOR"},
        hepatic_adjust=True, route="IV", metabolism="hepatic_CYP3A4/1A2/2D6", excretion="renal"
    ),
    "Hydrocortisone": DrugProfile(
        name="Hydrocortisone", category="corticosteroid", bioavailability=1.0,
        onset_min=30.0, peak_min=60.0, half_life_min=90.0, duration_min=480.0,
        standard_dose=100.0, dose_unit="mg", max_dose=300.0, min_dose=25.0, toxic_dose=1000.0,
        contraindications=["systemic_fungal_infections"],
        interactions={"NSAIDs": "MODERATE", "Warfarin": "MODERATE", "Insulin": "MODERATE"},
        route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Methylprednisolone": DrugProfile(
        name="Methylprednisolone", category="corticosteroid", bioavailability=1.0,
        onset_min=30.0, peak_min=60.0, half_life_min=180.0, duration_min=1080.0,
        standard_dose=125.0, dose_unit="mg", max_dose=1000.0, min_dose=40.0, toxic_dose=2000.0,
        contraindications=["systemic_fungal_infections"],
        interactions={"Ketoconazole": "MAJOR", "Warfarin": "MODERATE", "NSAIDs": "MODERATE"},
        route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Levothyroxine": DrugProfile(
        name="Levothyroxine", category="thyroid_hormone", bioavailability=0.80,
        onset_min=1440.0, peak_min=4320.0, half_life_min=10080.0, duration_min=7200.0,
        standard_dose=1.6, dose_unit="mcg/kg", max_dose=300.0, min_dose=0.5, toxic_dose=500.0,
        contraindications=["untreated_adrenal_insufficiency", "acute_MI"],
        interactions={"Warfarin": "MAJOR", "Calcium": "MODERATE", "Iron": "MODERATE", "PPIs": "MODERATE"},
        route="PO", metabolism="hepatic", excretion="renal/fecal"
    ),
    "Octreotide": DrugProfile(
        name="Octreotide", category="somatostatin_analog", bioavailability=1.0,
        onset_min=30.0, peak_min=60.0, half_life_min=90.0, duration_min=720.0,
        standard_dose=50.0, dose_unit="mcg", max_dose=500.0, min_dose=25.0, toxic_dose=1000.0,
        contraindications=[], interactions={"Cyclosporine": "MODERATE", "Insulin": "MODERATE"},
        route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Metoclopramide": DrugProfile(
        name="Metoclopramide", category="prokinetic", bioavailability=0.80,
        onset_min=3.0, peak_min=10.0, half_life_min=360.0, duration_min=120.0,
        standard_dose=10.0, dose_unit="mg", max_dose=40.0, min_dose=5.0, toxic_dose=80.0,
        contraindications=["GI_obstruction", "pheochromocytoma", "seizure_history"],
        interactions={"Levodopa": "MAJOR", "MAO_inhibitors": "MAJOR"},
        renal_adjust=True, route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Famotidine": DrugProfile(
        name="Famotidine", category="H2_blocker", bioavailability=0.45,
        onset_min=30.0, peak_min=120.0, half_life_min=180.0, duration_min=720.0,
        standard_dose=20.0, dose_unit="mg", max_dose=40.0, min_dose=10.0, toxic_dose=160.0,
        contraindications=[], interactions={"Ketoconazole": "MODERATE", "Atazanavir": "MAJOR"},
        renal_adjust=True, route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Dexamethasone": DrugProfile(
        name="Dexamethasone", category="corticosteroid", bioavailability=0.80,
        onset_min=60.0, peak_min=120.0, half_life_min=2160.0, duration_min=4320.0,
        standard_dose=4.0, dose_unit="mg", max_dose=20.0, min_dose=0.5, toxic_dose=40.0,
        contraindications=["systemic_fungal_infections"],
        interactions={"Warfarin": "MODERATE", "NSAIDs": "MODERATE", "Phenytoin": "MODERATE"},
        route="IV", metabolism="hepatic_CYP3A4", excretion="renal"
    ),

    # ─── RESPIRATORY (v3.0 expansion) ────────────────────
    "Albuterol": DrugProfile(
        name="Albuterol", category="bronchodilator", bioavailability=0.15,
        onset_min=5.0, peak_min=30.0, half_life_min=300.0, duration_min=360.0,
        standard_dose=2.5, dose_unit="mg", max_dose=10.0, min_dose=1.25, toxic_dose=20.0,
        contraindications=[],
        interactions={"Beta_blockers": "MAJOR", "MAO_inhibitors": "MAJOR", "Digoxin": "MODERATE"},
        route="INH", metabolism="hepatic", excretion="renal"
    ),
    "Ipratropium": DrugProfile(
        name="Ipratropium", category="anticholinergic_bronchodilator", bioavailability=0.02,
        onset_min=15.0, peak_min=120.0, half_life_min=120.0, duration_min=360.0,
        standard_dose=0.5, dose_unit="mg", max_dose=2.0, min_dose=0.25, toxic_dose=4.0,
        contraindications=["soy_allergy", "peanut_allergy"],
        interactions={"Anticholinergics": "MODERATE"},
        route="INH", metabolism="hepatic", excretion="renal"
    ),
    "Budesonide": DrugProfile(
        name="Budesonide", category="inhaled_corticosteroid", bioavailability=0.10,
        onset_min=120.0, peak_min=240.0, half_life_min=180.0, duration_min=720.0,
        standard_dose=0.5, dose_unit="mg", max_dose=2.0, min_dose=0.25, toxic_dose=4.0,
        contraindications=["status_asthmaticus"],
        interactions={"Ketoconazole": "MAJOR"},
        route="INH", metabolism="hepatic_CYP3A4", excretion="renal/fecal"
    ),

    # ─── EMERGENCY (v3.0 expansion) ──────────────────────
    "Atropine": DrugProfile(
        name="Atropine", category="anticholinergic", bioavailability=1.0,
        onset_min=1.0, peak_min=3.0, half_life_min=180.0, duration_min=240.0,
        standard_dose=0.5, dose_unit="mg", max_dose=3.0, min_dose=0.5, toxic_dose=10.0,
        contraindications=["narrow_angle_glaucoma", "obstructive_uropathy"],
        interactions={"Anticholinergics": "MAJOR"},
        route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Adenosine": DrugProfile(
        name="Adenosine", category="antiarrhythmic", bioavailability=1.0,
        onset_min=0.2, peak_min=0.5, half_life_min=0.17, duration_min=1.0,
        standard_dose=6.0, dose_unit="mg", max_dose=12.0, min_dose=6.0, toxic_dose=24.0,
        contraindications=["second_or_third_degree_heart_block", "sick_sinus_syndrome"],
        interactions={"Carbamazepine": "MAJOR", "Dipyridamole": "SEVERE", "Theophylline": "MAJOR"},
        route="IV", metabolism="RBC/endothelium", excretion="cellular"
    ),
    "Naloxone": DrugProfile(
        name="Naloxone", category="opioid_antagonist", bioavailability=1.0,
        onset_min=2.0, peak_min=5.0, half_life_min=60.0, duration_min=60.0,
        standard_dose=0.4, dose_unit="mg", max_dose=10.0, min_dose=0.04, toxic_dose=20.0,
        contraindications=[],
        interactions={"Opioids": "EXPECTED"},
        route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Flumazenil": DrugProfile(
        name="Flumazenil", category="benzodiazepine_antagonist", bioavailability=1.0,
        onset_min=1.0, peak_min=5.0, half_life_min=60.0, duration_min=60.0,
        standard_dose=0.2, dose_unit="mg", max_dose=3.0, min_dose=0.1, toxic_dose=5.0,
        contraindications=["chronic_benzodiazepine_use", "TCA_overdose", "seizure_history"],
        interactions={"Benzodiazepines": "EXPECTED"},
        route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Calcium_Chloride": DrugProfile(
        name="Calcium_Chloride", category="electrolyte", bioavailability=1.0,
        onset_min=1.0, peak_min=5.0, half_life_min=30.0, duration_min=120.0,
        standard_dose=1000.0, dose_unit="mg", max_dose=3000.0, min_dose=500.0, toxic_dose=6000.0,
        contraindications=["hypercalcemia", "digoxin_toxicity"],
        interactions={"Digoxin": "SEVERE", "Ceftriaxone": "SEVERE"},
        route="IV", metabolism="none", excretion="renal"
    ),
    "Sodium_Bicarbonate": DrugProfile(
        name="Sodium_Bicarbonate", category="alkalinizer", bioavailability=1.0,
        onset_min=2.0, peak_min=5.0, half_life_min=30.0, duration_min=120.0,
        standard_dose=1.0, dose_unit="mEq/kg", max_dose=200.0, min_dose=0.5, toxic_dose=400.0,
        contraindications=["metabolic_alkalosis", "hypocalcemia"],
        interactions={"Aspirin": "MAJOR", "Lithium": "MAJOR"},
        route="IV", metabolism="none", excretion="renal"
    ),
    "Magnesium_Sulfate": DrugProfile(
        name="Magnesium_Sulfate", category="electrolyte", bioavailability=1.0,
        onset_min=5.0, peak_min=30.0, half_life_min=240.0, duration_min=360.0,
        standard_dose=2000.0, dose_unit="mg", max_dose=6000.0, min_dose=1000.0, toxic_dose=10000.0,
        contraindications=["heart_block", "myocardial_damage"],
        interactions={"Neuromuscular_blockers": "MAJOR", "Calcium_channel_blockers": "MAJOR"},
        renal_adjust=True, route="IV", metabolism="none", excretion="renal"
    ),
    "Epinephrine_IV": DrugProfile(
        name="Epinephrine_IV", category="vasopressor", bioavailability=1.0,
        onset_min=0.5, peak_min=2.0, half_life_min=3.0, duration_min=10.0,
        standard_dose=1.0, dose_unit="mg", max_dose=10.0, min_dose=0.1, toxic_dose=20.0,
        contraindications=["narrow_angle_glaucoma"],
        interactions={"Beta_blockers": "MAJOR", "MAO_inhibitors": "SEVERE", "TCAs": "MAJOR"},
        route="IV", metabolism="COMT/MAO", excretion="renal"
    ),

    # ─── ANTIDIABETICS (v3.0 expansion) ──────────────────
    "Insulin_Lispro": DrugProfile(
        name="Insulin_Lispro", category="antidiabetic", bioavailability=1.0,
        onset_min=15.0, peak_min=60.0, half_life_min=60.0, duration_min=300.0,
        standard_dose=0.1, dose_unit="units/kg", max_dose=0.3, min_dose=0.05, toxic_dose=1.0,
        contraindications=["hypoglycemia"],
        interactions={"Beta_blockers": "MODERATE", "Thiazides": "MODERATE"},
        route="SC", metabolism="hepatic/renal", excretion="renal"
    ),
    "Insulin_Glargine": DrugProfile(
        name="Insulin_Glargine", category="antidiabetic", bioavailability=1.0,
        onset_min=120.0, peak_min=0.0, half_life_min=720.0, duration_min=1440.0,
        standard_dose=0.2, dose_unit="units/kg", max_dose=0.5, min_dose=0.1, toxic_dose=2.0,
        contraindications=["hypoglycemia", "diabetic_ketoacidosis"],
        interactions={"Beta_blockers": "MODERATE", "Thiazides": "MODERATE", "Pioglitazone": "MODERATE"},
        route="SC", metabolism="hepatic/renal", excretion="renal"
    ),
    "Glipizide": DrugProfile(
        name="Glipizide", category="sulfonylurea", bioavailability=0.95,
        onset_min=30.0, peak_min=120.0, half_life_min=240.0, duration_min=720.0,
        standard_dose=5.0, dose_unit="mg", max_dose=40.0, min_dose=2.5, toxic_dose=80.0,
        contraindications=["DKA", "severe_hepatic_impairment"],
        interactions={"Fluconazole": "MAJOR", "Beta_blockers": "MODERATE", "NSAIDs": "MODERATE"},
        hepatic_adjust=True, route="PO", metabolism="hepatic_CYP2C9", excretion="renal"
    ),
    "Empagliflozin": DrugProfile(
        name="Empagliflozin", category="SGLT2_inhibitor", bioavailability=0.78,
        onset_min=60.0, peak_min=90.0, half_life_min=780.0, duration_min=1440.0,
        standard_dose=10.0, dose_unit="mg", max_dose=25.0, min_dose=10.0, toxic_dose=50.0,
        contraindications=["severe_renal_impairment", "dialysis"],
        interactions={"Diuretics": "MODERATE", "Insulin": "MODERATE"},
        renal_adjust=True, route="PO", metabolism="hepatic_UGT", excretion="renal/fecal"
    ),

    # ─── ANTIVIRALS (v3.0 expansion) ─────────────────────
    "Remdesivir": DrugProfile(
        name="Remdesivir", category="antiviral", bioavailability=1.0,
        onset_min=30.0, peak_min=60.0, half_life_min=60.0, duration_min=1440.0,
        standard_dose=200.0, dose_unit="mg", max_dose=200.0, min_dose=100.0, toxic_dose=400.0,
        contraindications=["eGFR_below_30"],
        interactions={"Chloroquine": "MAJOR", "Hydroxychloroquine": "MAJOR"},
        renal_adjust=True, route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Oseltamivir": DrugProfile(
        name="Oseltamivir", category="antiviral", bioavailability=0.80,
        onset_min=60.0, peak_min=240.0, half_life_min=420.0, duration_min=720.0,
        standard_dose=75.0, dose_unit="mg", max_dose=150.0, min_dose=30.0, toxic_dose=300.0,
        contraindications=[],
        interactions={"Live_vaccines": "MAJOR", "Warfarin": "MONITOR"},
        renal_adjust=True, route="PO", metabolism="hepatic", excretion="renal"
    ),
    "Acyclovir": DrugProfile(
        name="Acyclovir", category="antiviral", bioavailability=0.20,
        onset_min=30.0, peak_min=60.0, half_life_min=180.0, duration_min=480.0,
        standard_dose=10.0, dose_unit="mg/kg", max_dose=20.0, min_dose=5.0, toxic_dose=40.0,
        contraindications=["hypersensitivity"],
        interactions={"Probenecid": "MODERATE", "Nephrotoxic_drugs": "MAJOR"},
        renal_adjust=True, route="IV", metabolism="minimal", excretion="renal"
    ),
    "Tenofovir": DrugProfile(
        name="Tenofovir", category="antiviral", bioavailability=0.25,
        onset_min=60.0, peak_min=120.0, half_life_min=1020.0, duration_min=1440.0,
        standard_dose=300.0, dose_unit="mg", max_dose=300.0, min_dose=150.0, toxic_dose=600.0,
        contraindications=[],
        interactions={"Nephrotoxic_drugs": "MAJOR", "Didanosine": "MAJOR"},
        renal_adjust=True, route="PO", metabolism="minimal", excretion="renal"
    ),

    # ─── IMMUNOSUPPRESSANTS / OTHERS (v3.0 expansion) ────
    "Tacrolimus": DrugProfile(
        name="Tacrolimus", category="immunosuppressant", bioavailability=0.25,
        onset_min=60.0, peak_min=180.0, half_life_min=720.0, duration_min=1440.0,
        standard_dose=0.05, dose_unit="mg/kg", max_dose=0.3, min_dose=0.01, toxic_dose=0.5,
        contraindications=["hypersensitivity"],
        interactions={"Ketoconazole": "SEVERE", "Cyclosporine": "SEVERE", "Rifampin": "SEVERE",
                      "Phenytoin": "MAJOR", "Grapefruit": "MAJOR"},
        hepatic_adjust=True, route="IV", metabolism="hepatic_CYP3A4", excretion="biliary"
    ),
    "Cyclosporine": DrugProfile(
        name="Cyclosporine", category="immunosuppressant", bioavailability=0.30,
        onset_min=60.0, peak_min=240.0, half_life_min=1140.0, duration_min=1440.0,
        standard_dose=3.0, dose_unit="mg/kg", max_dose=5.0, min_dose=1.0, toxic_dose=10.0,
        contraindications=["uncontrolled_hypertension", "renal_impairment"],
        interactions={"Ketoconazole": "SEVERE", "Rifampin": "SEVERE", "Statins": "MAJOR",
                      "ACE_inhibitors": "MAJOR", "Methotrexate": "MAJOR"},
        renal_adjust=True, route="IV", metabolism="hepatic_CYP3A4", excretion="biliary"
    ),
    "Methotrexate": DrugProfile(
        name="Methotrexate", category="antimetabolite", bioavailability=0.60,
        onset_min=60.0, peak_min=180.0, half_life_min=480.0, duration_min=1440.0,
        standard_dose=15.0, dose_unit="mg", max_dose=25.0, min_dose=7.5, toxic_dose=50.0,
        contraindications=["pregnancy", "severe_renal_impairment", "hepatic_insufficiency"],
        interactions={"NSAIDs": "SEVERE", "TMP_SMX": "SEVERE", "Penicillins": "MAJOR"},
        renal_adjust=True, route="PO", metabolism="hepatic", excretion="renal"
    ),
    "Lithium": DrugProfile(
        name="Lithium", category="mood_stabilizer", bioavailability=0.95,
        onset_min=360.0, peak_min=720.0, half_life_min=1440.0, duration_min=1440.0,
        standard_dose=300.0, dose_unit="mg", max_dose=1800.0, min_dose=150.0, toxic_dose=3600.0,
        contraindications=["severe_renal_impairment", "severe_cardiovascular_disease"],
        interactions={"ACE_inhibitors": "MAJOR", "NSAIDs": "MAJOR", "Thiazides": "MAJOR",
                      "Metronidazole": "MAJOR"},
        renal_adjust=True, route="PO", metabolism="none", excretion="renal"
    ),
    "Furosemide": DrugProfile(
        name="Furosemide", category="loop_diuretic", bioavailability=0.50,
        onset_min=5.0, peak_min=30.0, half_life_min=90.0, duration_min=120.0,
        standard_dose=40.0, dose_unit="mg", max_dose=200.0, min_dose=20.0, toxic_dose=600.0,
        contraindications=["anuria", "severe_hypokalemia"],
        interactions={"Aminoglycosides": "MAJOR", "Digoxin": "MAJOR", "Lithium": "MAJOR",
                      "ACE_inhibitors": "MODERATE"},
        renal_adjust=True, route="IV", metabolism="hepatic", excretion="renal"
    ),
    "Spironolactone": DrugProfile(
        name="Spironolactone", category="potassium_sparing_diuretic", bioavailability=0.73,
        onset_min=2880.0, peak_min=4320.0, half_life_min=84.0, duration_min=2880.0,
        standard_dose=25.0, dose_unit="mg", max_dose=100.0, min_dose=12.5, toxic_dose=400.0,
        contraindications=["hyperkalemia", "Addison_disease", "anuria"],
        interactions={"ACE_inhibitors": "MAJOR", "ARBs": "MAJOR", "Potassium_supplements": "SEVERE",
                      "Digoxin": "MODERATE"},
        renal_adjust=True, route="PO", metabolism="hepatic", excretion="renal/fecal"
    ),
}


class PharmacokineticEngine:
    """Full PK/PD engine for MOISSCode."""

    def __init__(self):
        self.drugs = dict(DRUG_DATABASE)  # Copy so user registrations don't mutate global
        self.active_drugs: Dict[str, Dict] = {}  # Currently administered drugs

    # ─── Drug Registry ─────────────────────────────────────────
    def register_drug(self, profile: DrugProfile):
        """Register a custom drug profile.

        Allows developers to extend the built-in drug database with
        any drug. The profile must be a DrugProfile dataclass instance.

        Example::

            pk = PharmacokineticEngine()
            pk.register_drug(DrugProfile(
                name="Remdesivir",
                category="antiviral",
                bioavailability=1.0,
                onset_min=30.0,
                peak_min=120.0,
                half_life_min=1500.0,
                duration_min=1440.0,
                standard_dose=200.0,
                dose_unit="mg",
                max_dose=200.0,
                min_dose=100.0,
            ))
        """
        if not isinstance(profile, DrugProfile):
            raise TypeError(f"Expected DrugProfile, got {type(profile).__name__}")
        self.drugs[profile.name] = profile
        print(f"[PK] Registered drug: {profile.name} ({profile.category})")

    def unregister_drug(self, drug_name: str) -> bool:
        """Remove a drug from the registry. Returns True if removed."""
        if drug_name in self.drugs:
            del self.drugs[drug_name]
            return True
        return False

    def list_categories(self) -> List[str]:
        """List all unique drug categories."""
        return list(set(d.category for d in self.drugs.values()))

    # ─── Drug Lookup ───────────────────────────────────────────
    def get_profile(self, drug_name: str) -> Optional[DrugProfile]:
        """Get the PK profile for a drug."""
        return self.drugs.get(drug_name)

    def list_drugs(self, category: str = None) -> List[str]:
        """List available drugs, optionally filtered by category."""
        if category:
            return [name for name, d in self.drugs.items() if d.category == category]
        return list(self.drugs.keys())

    # ─── Dosing Calculations ───────────────────────────────────
    def calculate_dose(self, drug_name: str, weight_kg: float,
                       dose_per_kg: float = None) -> Dict:
        """Calculate weight-based dose for a drug."""
        profile = self.get_profile(drug_name)
        if not profile:
            # Suggest similar drug names
            name_lower = drug_name.lower()
            suggestions = [d for d in self.drugs
                           if name_lower in d.lower() or d.lower() in name_lower
                           or (len(name_lower) >= 3 and name_lower[:3] == d.lower()[:3])]
            msg = f"Drug '{drug_name}' not found in registry."
            if suggestions:
                msg += f" Did you mean: {', '.join(suggestions[:3])}?"
            msg += f" Use list_drugs() to see all {len(self.drugs)} available drugs."
            return {"error": msg}

        if dose_per_kg is None:
            dose_per_kg = profile.standard_dose

        # Weight-based calculation
        if "kg" in profile.dose_unit:
            total_dose = dose_per_kg * weight_kg
        else:
            total_dose = dose_per_kg  # Fixed dose, not weight-based

        # Safety check
        is_safe = profile.min_dose <= dose_per_kg <= profile.max_dose
        warning = None
        if dose_per_kg > profile.max_dose:
            warning = f"EXCEEDS MAX DOSE ({profile.max_dose} {profile.dose_unit})"
        elif dose_per_kg < profile.min_dose:
            warning = f"BELOW MIN DOSE ({profile.min_dose} {profile.dose_unit})"

        result = {
            "type": "PK_DOSE",
            "drug": drug_name,
            "dose_per_kg": dose_per_kg,
            "total_dose": round(total_dose, 2),
            "unit": profile.dose_unit,
            "patient_weight": weight_kg,
            "is_safe": is_safe,
            "warning": warning
        }

        print(f"[PK] {drug_name}: {dose_per_kg} {profile.dose_unit} × {weight_kg}kg = {total_dose:.2f}")
        if warning:
            print(f"[PK] ⚠️ {warning}")

        return result

    # ─── Drug Interaction Check ────────────────────────────────
    def check_interactions(self, drug_name: str,
                          current_drugs: List[str] = None) -> Dict:
        """Check for drug-drug interactions."""
        profile = self.get_profile(drug_name)
        if not profile:
            return {"error": f"Unknown drug: {drug_name}"}

        if current_drugs is None:
            current_drugs = list(self.active_drugs.keys())

        interactions_found = []
        max_severity = "NONE"
        severity_rank = {"NONE": 0, "MONITOR": 1, "MODERATE": 2, "MAJOR": 3, "SEVERE": 4}

        for active_drug in current_drugs:
            if active_drug in profile.interactions:
                severity = profile.interactions[active_drug]
                interactions_found.append({
                    "drug_a": drug_name,
                    "drug_b": active_drug,
                    "severity": severity
                })
                if severity_rank.get(severity, 0) > severity_rank.get(max_severity, 0):
                    max_severity = severity

        result = {
            "type": "PK_INTERACTION",
            "drug": drug_name,
            "interactions": interactions_found,
            "max_severity": max_severity,
            "safe_to_administer": max_severity not in ["SEVERE", "MAJOR"]
        }

        if interactions_found:
            print(f"[PK] ⚠️ Interactions found for {drug_name}:")
            for ix in interactions_found:
                print(f"    {ix['drug_b']}: {ix['severity']}")
        else:
            print(f"[PK] ✓ No interactions found for {drug_name}")

        return result

    # ─── Concentration Curve ───────────────────────────────────
    def plasma_concentration(self, drug_name: str, dose: float,
                             time_min: float, weight_kg: float = 70.0) -> float:
        """
        Estimates plasma concentration at a given time after dose.
        Uses a one-compartment IV bolus model:
            C(t) = (Dose × Bioavailability) / Vd × e^(-ke × t)
        """
        profile = self.get_profile(drug_name)
        if not profile:
            return 0.0

        # Estimated volume of distribution (simplified: 0.3 L/kg for most drugs)
        vd = 0.3 * weight_kg
        ke = math.log(2) / profile.half_life_min  # Elimination rate constant

        c0 = (dose * profile.bioavailability) / vd
        ct = c0 * math.exp(-ke * time_min)

        return round(ct, 4)

    # ─── Time to Therapeutic Range ─────────────────────────────
    def time_to_effect(self, drug_name: str) -> Dict:
        """Get timing information for a drug."""
        profile = self.get_profile(drug_name)
        if not profile:
            return {"error": f"Unknown drug: {drug_name}"}

        return {
            "type": "PK_TIMING",
            "drug": drug_name,
            "onset_min": profile.onset_min,
            "peak_min": profile.peak_min,
            "duration_min": profile.duration_min,
            "half_life_min": profile.half_life_min
        }

    # ─── Active Drug Management ────────────────────────────────
    def validate_dose(self, drug_name: str, dose_amount: float,
                      dose_unit: str) -> Dict:
        """Validate a dose against the drug's PK profile.

        Returns a dict with:
            level: "SAFE", "WARNING", "ERROR", or "UNKNOWN"
            message: human-readable explanation
            converted_dose: dose after unit conversion (if applicable)
            converted_unit: unit after conversion (if applicable)
        """
        profile = self.get_profile(drug_name)
        if not profile:
            return {
                "level": "UNKNOWN",
                "message": f"Drug '{drug_name}' not in registry. Dose validation skipped.",
                "converted_dose": dose_amount,
                "converted_unit": dose_unit,
            }

        effective_dose = dose_amount
        effective_unit = dose_unit

        # Check unit compatibility
        if dose_unit != profile.dose_unit:
            # Extract base units (first part before /)
            given_base = dose_unit.split('/')[0]
            expected_base = profile.dose_unit.split('/')[0]

            from moisscode.typesystem import UnitSystem

            if UnitSystem.are_compatible(given_base, expected_base):
                # Same dimension, try to convert
                try:
                    factor = UnitSystem.CONVERSIONS.get((given_base, expected_base))
                    if factor is not None:
                        effective_dose = dose_amount * factor
                        effective_unit = profile.dose_unit
                        print(f"[PK] Unit converted: {dose_amount} {dose_unit} -> {effective_dose} {effective_unit}")
                    else:
                        # Same dimension but no direct conversion path
                        return {
                            "level": "WARNING",
                            "message": (
                                f"Unit '{dose_unit}' differs from expected '{profile.dose_unit}' "
                                f"for {drug_name}. No direct conversion available."
                            ),
                            "converted_dose": dose_amount,
                            "converted_unit": dose_unit,
                        }
                except ValueError:
                    pass
            else:
                return {
                    "level": "WARNING",
                    "message": (
                        f"Unit mismatch for {drug_name}: given '{dose_unit}', "
                        f"expected '{profile.dose_unit}'. Cannot convert between different dimensions."
                    ),
                    "converted_dose": dose_amount,
                    "converted_unit": dose_unit,
                }

        # Check dose ranges
        if profile.toxic_dose > 0 and effective_dose >= profile.toxic_dose:
            return {
                "level": "ERROR",
                "message": (
                    f"TOXIC DOSE for {drug_name}: {effective_dose} {effective_unit} "
                    f"exceeds toxic threshold ({profile.toxic_dose} {profile.dose_unit}). "
                    f"Administration blocked."
                ),
                "converted_dose": effective_dose,
                "converted_unit": effective_unit,
            }

        if effective_dose > profile.max_dose:
            return {
                "level": "WARNING",
                "message": (
                    f"HIGH DOSE for {drug_name}: {effective_dose} {effective_unit} "
                    f"exceeds max safe dose ({profile.max_dose} {profile.dose_unit})."
                ),
                "converted_dose": effective_dose,
                "converted_unit": effective_unit,
            }

        if effective_dose < profile.min_dose:
            return {
                "level": "WARNING",
                "message": (
                    f"LOW DOSE for {drug_name}: {effective_dose} {effective_unit} "
                    f"below min effective dose ({profile.min_dose} {profile.dose_unit})."
                ),
                "converted_dose": effective_dose,
                "converted_unit": effective_unit,
            }

        return {
            "level": "SAFE",
            "message": f"{drug_name} {effective_dose} {effective_unit} within safe range.",
            "converted_dose": effective_dose,
            "converted_unit": effective_unit,
        }

    def administer(self, drug_name: str, dose: float,
                   weight_kg: float = 70.0) -> Dict:
        """Register that a drug has been administered (for interaction tracking)."""
        profile = self.get_profile(drug_name)
        if not profile:
            return {"error": f"Unknown drug: {drug_name}"}

        # Check interactions with currently active drugs
        interaction_check = self.check_interactions(drug_name)

        self.active_drugs[drug_name] = {
            "dose": dose,
            "weight": weight_kg,
            "administered_at": "now"
        }

        return {
            "type": "PK_ADMINISTER",
            "drug": drug_name,
            "dose": dose,
            "interactions": interaction_check,
            "onset_min": profile.onset_min,
            "safe": interaction_check.get("safe_to_administer", True)
        }

    # ─── Contraindication Check ────────────────────────────────
    def check_contraindications(self, drug_name: str,
                                 patient_conditions: List[str] = None) -> Dict:
        """Check if a drug is contraindicated for a patient."""
        profile = self.get_profile(drug_name)
        if not profile:
            return {"error": f"Unknown drug: {drug_name}"}

        if patient_conditions is None:
            patient_conditions = []

        found = [c for c in patient_conditions if c in profile.contraindications]

        return {
            "type": "PK_CONTRAINDICATION",
            "drug": drug_name,
            "contraindicated": len(found) > 0,
            "reasons": found
        }


    # ── Renal / Hepatic Dose Adjustment ────────────────────

    def renal_adjust(self, drug_name: str, gfr: float) -> Dict:
        """
        Calculate renal dose adjustment based on eGFR.
        Returns adjustment factor and recommendation.
        """
        profile = self.get_profile(drug_name)
        if not profile:
            return {"error": f"Unknown drug: {drug_name}"}

        gfr = float(gfr)

        if not profile.renal_adjust:
            return {
                'type': 'PK_RENAL',
                'drug': drug_name,
                'gfr': gfr,
                'adjustment': 1.0,
                'recommendation': 'No renal adjustment needed for this drug'
            }

        if gfr >= 60:
            factor = 1.0
            recommendation = "Normal dose"
        elif gfr >= 30:
            factor = 0.75
            recommendation = "Reduce dose by 25% or extend interval"
        elif gfr >= 15:
            factor = 0.5
            recommendation = "Reduce dose by 50%, monitor closely"
        else:
            factor = 0.25
            recommendation = "Reduce dose by 75%, consider alternative, monitor drug levels"

        adjusted_dose = profile.standard_dose * factor

        return {
            'type': 'PK_RENAL',
            'drug': drug_name,
            'gfr': gfr,
            'adjustment_factor': factor,
            'original_dose': profile.standard_dose,
            'adjusted_dose': round(adjusted_dose, 1),
            'dose_unit': profile.dose_unit,
            'recommendation': recommendation
        }

    def hepatic_adjust(self, drug_name: str, child_pugh_class: str) -> Dict:
        """
        Calculate hepatic dose adjustment based on Child-Pugh class.
        Classes: A (mild), B (moderate), C (severe).
        """
        profile = self.get_profile(drug_name)
        if not profile:
            return {"error": f"Unknown drug: {drug_name}"}

        child_pugh_class = child_pugh_class.upper()

        if not profile.hepatic_adjust:
            return {
                'type': 'PK_HEPATIC',
                'drug': drug_name,
                'child_pugh': child_pugh_class,
                'adjustment': 1.0,
                'recommendation': 'No hepatic adjustment needed for this drug'
            }

        adjustments = {
            'A': (1.0, 'Normal dose, monitor LFTs'),
            'B': (0.5, 'Reduce dose by 50%, monitor closely'),
            'C': (0.25, 'Use with extreme caution or avoid, consider alternative'),
        }

        factor, recommendation = adjustments.get(child_pugh_class, (1.0, 'Unknown class'))
        adjusted_dose = profile.standard_dose * factor

        return {
            'type': 'PK_HEPATIC',
            'drug': drug_name,
            'child_pugh': child_pugh_class,
            'adjustment_factor': factor,
            'original_dose': profile.standard_dose,
            'adjusted_dose': round(adjusted_dose, 1),
            'dose_unit': profile.dose_unit,
            'recommendation': recommendation
        }

    def therapeutic_range(self, drug_name: str) -> Dict:
        """
        Get therapeutic drug monitoring targets (trough and peak levels).
        """
        # Common TDM ranges
        tdm_ranges = {
            'Vancomycin': {'trough': (15, 20), 'peak': (25, 40), 'unit': 'mcg/mL'},
            'Heparin': {'trough': None, 'peak': None, 'unit': 'units/mL',
                       'aptt_target': (60, 85), 'aptt_unit': 'seconds'},
            'Insulin_Regular': {'trough': None, 'peak': None, 'unit': 'mU/mL',
                               'glucose_target': (70, 180), 'glucose_unit': 'mg/dL'},
            'Metformin': {'trough': (0.5, 2.0), 'peak': (1, 4), 'unit': 'mcg/mL'},
        }

        profile = self.get_profile(drug_name)
        if not profile:
            return {"error": f"Unknown drug: {drug_name}"}

        tdm = tdm_ranges.get(drug_name, None)

        if tdm:
            return {
                'type': 'PK_TDM',
                'drug': drug_name,
                'category': profile.category,
                **tdm
            }

        return {
            'type': 'PK_TDM',
            'drug': drug_name,
            'category': profile.category,
            'trough': None,
            'peak': None,
            'note': 'No specific TDM ranges defined for this drug'
        }

    def trough_estimate(self, drug_name: str, dose: float,
                        interval_hr: float, weight_kg: float = 70.0) -> Dict:
        """
        Estimate trough concentration using one-compartment model.
        Ctrough = (Dose * F / Vd) * e^(-ke * tau)
        """
        profile = self.get_profile(drug_name)
        if not profile:
            return {"error": f"Unknown drug: {drug_name}"}

        dose = float(dose)
        interval_hr = float(interval_hr)
        weight_kg = float(weight_kg)

        ke = 0.693 / (profile.half_life_min / 60)  # elimination rate constant (per hour)
        vd = weight_kg * 0.7  # estimated Vd (L)
        tau = interval_hr  # dosing interval (hours)

        c_peak = (dose * profile.bioavailability) / vd
        c_trough = c_peak * math.exp(-ke * tau)

        return {
            'type': 'PK_TROUGH',
            'drug': drug_name,
            'dose': dose,
            'interval_hr': interval_hr,
            'c_peak_estimated': round(c_peak, 2),
            'c_trough_estimated': round(c_trough, 4),
            'half_life_hr': round(profile.half_life_min / 60, 1),
            'unit': 'mg/L'
        }


if __name__ == "__main__":
    pk = PharmacokineticEngine()

    print("=== Available Drugs ===")
    for name in pk.list_drugs():
        p = pk.get_profile(name)
        print(f"  {name} ({p.category})  - onset: {p.onset_min}min, t½: {p.half_life_min}min")

    print("\n=== Weight-Based Dosing ===")
    pk.calculate_dose("Norepinephrine", weight_kg=70)
    pk.calculate_dose("Vancomycin", weight_kg=70)

    print("\n=== Drug Interactions ===")
    pk.administer("Norepinephrine", 0.1, 70)
    pk.check_interactions("Epinephrine", ["Norepinephrine"])
    pk.check_interactions("Heparin", ["Norepinephrine"])

    print("\n=== Plasma Concentration (Norepinephrine, 7mg bolus) ===")
    for t in [0, 1, 2, 5, 10, 15]:
        c = pk.plasma_concentration("Norepinephrine", 7.0, t, 70)
        print(f"  t={t}min: C = {c} mg/L")

    print("\n=== Contraindication Check ===")
    result = pk.check_contraindications("Heparin", ["active_bleeding", "diabetes"])
    print(f"  Contraindicated: {result['contraindicated']}  - Reasons: {result['reasons']}")
