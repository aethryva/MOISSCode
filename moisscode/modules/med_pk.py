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
        half_life_min=60.0,     # 1 hour
        duration_min=360.0,     # 6 hours
        standard_dose=0.1,
        dose_unit="units/kg",
        max_dose=0.3,
        min_dose=0.05,
        toxic_dose=1.0,
        contraindications=["hypoglycemia"],
        interactions={
            "Beta_blockers": "MODERATE",
            "Thiazides": "MODERATE",
        },
        route="IV",
        metabolism="hepatic/renal",
        excretion="renal"
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
            return {"error": f"Unknown drug: {drug_name}"}

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
