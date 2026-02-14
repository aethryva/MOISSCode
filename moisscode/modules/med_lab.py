"""
med.lab  - Clinical Laboratory Module for MOISSCode
Complete lab panel interpretation with reference ranges and critical value flagging.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class LabReference:
    """Reference range for a lab test."""
    test_name: str
    full_name: str
    unit: str
    low_normal: float
    high_normal: float
    critical_low: Optional[float] = None
    critical_high: Optional[float] = None
    panic_low: Optional[float] = None
    panic_high: Optional[float] = None
    panel: str = ""  # Which panel this belongs to


# ─── Complete Lab Reference Database ──────────────────────
LAB_REFERENCES: Dict[str, LabReference] = {
    # ─── Complete Blood Count (CBC) ───
    "WBC":  LabReference("WBC", "White Blood Cells", "×10³/μL", 4.5, 11.0, 2.0, 30.0, panel="CBC"),
    "RBC":  LabReference("RBC", "Red Blood Cells", "×10⁶/μL", 4.5, 5.5, 2.0, 8.0, panel="CBC"),
    "Hgb":  LabReference("Hgb", "Hemoglobin", "g/dL", 12.0, 17.5, 7.0, 20.0, panel="CBC"),
    "Hct":  LabReference("Hct", "Hematocrit", "%", 36.0, 50.0, 20.0, 60.0, panel="CBC"),
    "MCV":  LabReference("MCV", "Mean Corpuscular Volume", "fL", 80.0, 100.0, panel="CBC"),
    "MCH":  LabReference("MCH", "Mean Corpuscular Hemoglobin", "pg", 27.0, 33.0, panel="CBC"),
    "MCHC": LabReference("MCHC", "Mean Corpuscular Hgb Concentration", "g/dL", 32.0, 36.0, panel="CBC"),
    "RDW":  LabReference("RDW", "Red Cell Distribution Width", "%", 11.5, 14.5, panel="CBC"),
    "PLT":  LabReference("PLT", "Platelets", "×10³/μL", 150.0, 400.0, 50.0, 1000.0, panel="CBC"),
    "MPV":  LabReference("MPV", "Mean Platelet Volume", "fL", 7.5, 12.0, panel="CBC"),

    # ─── Basic Metabolic Panel (BMP) ───
    "Na":     LabReference("Na", "Sodium", "mEq/L", 136.0, 145.0, 120.0, 160.0, panel="BMP"),
    "K":      LabReference("K", "Potassium", "mEq/L", 3.5, 5.0, 2.5, 6.5, 2.0, 7.0, panel="BMP"),
    "Cl":     LabReference("Cl", "Chloride", "mEq/L", 98.0, 106.0, 80.0, 120.0, panel="BMP"),
    "CO2":    LabReference("CO2", "Carbon Dioxide / Bicarb", "mEq/L", 23.0, 29.0, 10.0, 40.0, panel="BMP"),
    "BUN":    LabReference("BUN", "Blood Urea Nitrogen", "mg/dL", 7.0, 20.0, 2.0, 100.0, panel="BMP"),
    "Cr":     LabReference("Cr", "Creatinine", "mg/dL", 0.6, 1.2, 0.3, 10.0, panel="BMP"),
    "Glucose":LabReference("Glucose", "Glucose", "mg/dL", 70.0, 100.0, 40.0, 500.0, 20.0, 700.0, panel="BMP"),
    "Ca":     LabReference("Ca", "Calcium", "mg/dL", 8.5, 10.5, 6.0, 13.0, panel="BMP"),

    # ─── Comprehensive Metabolic Panel (CMP additions) ───
    "AlbA":   LabReference("AlbA", "Albumin", "g/dL", 3.5, 5.5, 1.5, None, panel="CMP"),
    "TotProt":LabReference("TotProt", "Total Protein", "g/dL", 6.0, 8.3, panel="CMP"),
    "ALP_lab":LabReference("ALP_lab", "Alkaline Phosphatase", "U/L", 44.0, 147.0, panel="CMP"),
    "ALT_lab":LabReference("ALT_lab", "Alanine Aminotransferase", "U/L", 7.0, 56.0, panel="CMP"),
    "AST_lab":LabReference("AST_lab", "Aspartate Aminotransferase", "U/L", 10.0, 40.0, panel="CMP"),
    "TBili":  LabReference("TBili", "Total Bilirubin", "mg/dL", 0.1, 1.2, panel="CMP"),

    # ─── Liver Function Tests (LFTs) ───
    "DBili":  LabReference("DBili", "Direct Bilirubin", "mg/dL", 0.0, 0.3, panel="LFT"),
    "GGT":    LabReference("GGT", "Gamma-Glutamyl Transferase", "U/L", 0.0, 51.0, panel="LFT"),
    "LDH_lab":LabReference("LDH_lab", "Lactate Dehydrogenase", "U/L", 140.0, 280.0, panel="LFT"),

    # ─── Coagulation Panel ───
    "PT":     LabReference("PT", "Prothrombin Time", "sec", 11.0, 13.5, panel="COAG"),
    "INR":    LabReference("INR", "International Normalized Ratio", "", 0.8, 1.1, None, 4.5, panel="COAG"),
    "aPTT":   LabReference("aPTT", "Activated Partial Thromboplastin", "sec", 25.0, 35.0, None, 100.0, panel="COAG"),
    "Fibrinogen": LabReference("Fibrinogen", "Fibrinogen", "mg/dL", 200.0, 400.0, 100.0, None, panel="COAG"),
    "DDimer": LabReference("DDimer", "D-Dimer", "ng/mL FEU", 0.0, 500.0, panel="COAG"),

    # ─── Arterial Blood Gas (ABG) ───
    "pH":     LabReference("pH", "Blood pH", "", 7.35, 7.45, 7.1, 7.6, 6.9, 7.8, panel="ABG"),
    "pCO2":   LabReference("pCO2", "Partial CO2 Pressure", "mmHg", 35.0, 45.0, 20.0, 70.0, panel="ABG"),
    "pO2":    LabReference("pO2", "Partial O2 Pressure", "mmHg", 80.0, 100.0, 40.0, None, panel="ABG"),
    "HCO3":   LabReference("HCO3", "Bicarbonate", "mEq/L", 22.0, 26.0, 10.0, 40.0, panel="ABG"),
    "Lactate_lab": LabReference("Lactate_lab", "Lactate", "mmol/L", 0.5, 2.0, None, 4.0, None, 10.0, panel="ABG"),

    # ─── Cardiac Markers ───
    "Troponin": LabReference("Troponin", "Troponin I", "ng/mL", 0.0, 0.04, None, 0.4, panel="CARDIAC"),
    "BNP":      LabReference("BNP", "B-type Natriuretic Peptide", "pg/mL", 0.0, 100.0, None, 500.0, panel="CARDIAC"),
    "CK_MB":    LabReference("CK_MB", "Creatine Kinase-MB", "ng/mL", 0.0, 5.0, panel="CARDIAC"),

    # ─── Thyroid Panel ───
    "TSH":  LabReference("TSH", "Thyroid Stimulating Hormone", "mIU/L", 0.4, 4.0, 0.01, 100.0, panel="THYROID"),
    "FT4":  LabReference("FT4", "Free Thyroxine", "ng/dL", 0.8, 1.8, 0.1, 5.0, panel="THYROID"),
    "FT3":  LabReference("FT3", "Free Triiodothyronine", "pg/mL", 2.3, 4.2, panel="THYROID"),

    # ─── Inflammatory Markers ───
    "CRP":     LabReference("CRP", "C-Reactive Protein", "mg/L", 0.0, 10.0, panel="INFLAM"),
    "ESR":     LabReference("ESR", "Erythrocyte Sedimentation Rate", "mm/hr", 0.0, 20.0, panel="INFLAM"),
    "Procalcitonin": LabReference("Procalcitonin", "Procalcitonin", "ng/mL", 0.0, 0.1, None, 2.0, panel="INFLAM"),

    # ─── Renal Function ───
    "BUN_Cr": LabReference("BUN_Cr", "BUN/Creatinine Ratio", "", 10.0, 20.0, panel="RENAL"),

    # ─── Lipid Panel (v3.0) ───
    "TotalChol": LabReference("TotalChol", "Total Cholesterol", "mg/dL", 0.0, 200.0, panel="LIPID"),
    "LDL":       LabReference("LDL", "Low-Density Lipoprotein", "mg/dL", 0.0, 100.0, panel="LIPID"),
    "HDL":       LabReference("HDL", "High-Density Lipoprotein", "mg/dL", 40.0, 100.0, panel="LIPID"),
    "VLDL":      LabReference("VLDL", "Very Low-Density Lipoprotein", "mg/dL", 2.0, 30.0, panel="LIPID"),
    "TG":        LabReference("TG", "Triglycerides", "mg/dL", 0.0, 150.0, None, 500.0, panel="LIPID"),

    # ─── Iron Studies (v3.0) ───
    "Iron":      LabReference("Iron", "Serum Iron", "μg/dL", 60.0, 170.0, panel="IRON"),
    "TIBC":      LabReference("TIBC", "Total Iron Binding Capacity", "μg/dL", 250.0, 370.0, panel="IRON"),
    "Ferritin":  LabReference("Ferritin", "Ferritin", "ng/mL", 12.0, 300.0, panel="IRON"),
    "TransSat":  LabReference("TransSat", "Transferrin Saturation", "%", 20.0, 50.0, panel="IRON"),

    # ─── Pancreatic Enzymes (v3.0) ───
    "Amylase":   LabReference("Amylase", "Amylase", "U/L", 28.0, 100.0, None, 300.0, panel="PANC"),
    "Lipase":    LabReference("Lipase", "Lipase", "U/L", 0.0, 160.0, None, 500.0, panel="PANC"),

    # ─── Tumor Markers (v3.0) ───
    "CEA":       LabReference("CEA", "Carcinoembryonic Antigen", "ng/mL", 0.0, 3.0, panel="TUMOR"),
    "AFP":       LabReference("AFP", "Alpha-Fetoprotein", "ng/mL", 0.0, 10.0, panel="TUMOR"),
    "CA125":     LabReference("CA125", "Cancer Antigen 125", "U/mL", 0.0, 35.0, panel="TUMOR"),
    "CA19_9":    LabReference("CA19_9", "Cancer Antigen 19-9", "U/mL", 0.0, 37.0, panel="TUMOR"),
    "PSA":       LabReference("PSA", "Prostate-Specific Antigen", "ng/mL", 0.0, 4.0, panel="TUMOR"),

    # ─── Urine (v3.0) ───
    "UProt":     LabReference("UProt", "Urine Protein", "mg/dL", 0.0, 14.0, panel="URINE"),
    "UCr":       LabReference("UCr", "Urine Creatinine", "mg/dL", 20.0, 275.0, panel="URINE"),
    "UOsm":      LabReference("UOsm", "Urine Osmolality", "mOsm/kg", 300.0, 900.0, panel="URINE"),
    "Microalb":  LabReference("Microalb", "Urine Microalbumin", "mg/L", 0.0, 30.0, panel="URINE"),

    # ─── Immunology (v3.0) ───
    "IgG":       LabReference("IgG", "Immunoglobulin G", "mg/dL", 700.0, 1600.0, panel="IMMUNO"),
    "IgA":       LabReference("IgA", "Immunoglobulin A", "mg/dL", 70.0, 400.0, panel="IMMUNO"),
    "IgM":       LabReference("IgM", "Immunoglobulin M", "mg/dL", 40.0, 230.0, panel="IMMUNO"),
    "C3":        LabReference("C3", "Complement C3", "mg/dL", 90.0, 180.0, panel="IMMUNO"),
    "C4":        LabReference("C4", "Complement C4", "mg/dL", 10.0, 40.0, panel="IMMUNO"),

    # ─── Coag Extras (v3.0) ───
    "AntiXa":    LabReference("AntiXa", "Anti-Factor Xa", "IU/mL", 0.5, 1.0, panel="COAG"),
    "TT":        LabReference("TT", "Thrombin Time", "sec", 14.0, 19.0, None, 30.0, panel="COAG"),

    # ─── Endocrine (v3.0) ───
    "Cortisol":  LabReference("Cortisol", "Cortisol (AM)", "μg/dL", 6.2, 19.4, panel="ENDO"),
    "ACTH":      LabReference("ACTH", "Adrenocorticotropic Hormone", "pg/mL", 7.2, 63.3, panel="ENDO"),
    "PTH":       LabReference("PTH", "Parathyroid Hormone", "pg/mL", 15.0, 65.0, panel="ENDO"),
    "VitD":      LabReference("VitD", "25-Hydroxyvitamin D", "ng/mL", 30.0, 100.0, panel="ENDO"),
    "HbA1c":     LabReference("HbA1c", "Hemoglobin A1c", "%", 4.0, 5.6, panel="ENDO"),
    "CPeptide":  LabReference("CPeptide", "C-Peptide", "ng/mL", 0.8, 3.1, panel="ENDO"),

    # ─── Electrolyte Extras (v3.0) ───
    "Mg":        LabReference("Mg", "Magnesium", "mg/dL", 1.7, 2.2, 1.0, 4.0, panel="BMP"),
    "Phos":      LabReference("Phos", "Phosphorus", "mg/dL", 2.5, 4.5, 1.0, 8.0, panel="BMP"),
}



class LabEngine:
    """Clinical laboratory interpretation engine."""

    def __init__(self):
        self.references = LAB_REFERENCES

    def interpret(self, test_name: str, value: float) -> Dict:
        """Interpret a single lab result against reference ranges."""
        ref = self.references.get(test_name)
        if not ref:
            return {"error": f"Unknown test: {test_name}. Use list_tests() to see available tests."}

        # Determine status
        if ref.panic_low and value <= ref.panic_low:
            status = "PANIC_LOW"
        elif ref.panic_high and value >= ref.panic_high:
            status = "PANIC_HIGH"
        elif ref.critical_low and value <= ref.critical_low:
            status = "CRITICAL_LOW"
        elif ref.critical_high and value >= ref.critical_high:
            status = "CRITICAL_HIGH"
        elif value < ref.low_normal:
            status = "LOW"
        elif value > ref.high_normal:
            status = "HIGH"
        else:
            status = "NORMAL"

        is_critical = status.startswith("CRITICAL") or status.startswith("PANIC")

        return {
            "type": "LAB_RESULT",
            "test": test_name,
            "full_name": ref.full_name,
            "value": value,
            "unit": ref.unit,
            "status": status,
            "is_critical": is_critical,
            "reference_range": f"{ref.low_normal}-{ref.high_normal} {ref.unit}",
            "panel": ref.panel
        }

    def interpret_panel(self, panel_name: str, values: Dict[str, float]) -> Dict:
        """Interpret an entire lab panel."""
        panel_tests = {k: v for k, v in self.references.items() if v.panel == panel_name}

        if not panel_tests:
            return {"error": f"Unknown panel: {panel_name}. Available: {self.list_panels()}"}

        results = []
        abnormal = []
        critical = []

        for test_name, ref in panel_tests.items():
            if test_name in values:
                r = self.interpret(test_name, values[test_name])
                results.append(r)
                if r["status"] != "NORMAL":
                    abnormal.append(r)
                if r.get("is_critical"):
                    critical.append(r)

        return {
            "type": "LAB_PANEL",
            "panel": panel_name,
            "total_tests": len(results),
            "abnormal_count": len(abnormal),
            "critical_count": len(critical),
            "results": results,
            "abnormal": abnormal,
            "critical": critical
        }

    def gfr(self, creatinine: float, age: int, sex: str = "M",
            race: str = "other") -> Dict:
        """
        Estimated GFR using CKD-EPI 2021 equation (race-free).
        eGFR = 142 × min(Cr/κ, 1)^α × max(Cr/κ, 1)^-1.200 × 0.9938^Age × (1.012 if female)
        """
        if sex.upper() == "F":
            kappa = 0.7
            alpha = -0.241
            sex_coeff = 1.012
        else:
            kappa = 0.9
            alpha = -0.302
            sex_coeff = 1.0

        min_ratio = min(creatinine / kappa, 1.0)
        max_ratio = max(creatinine / kappa, 1.0)

        egfr = 142 * (min_ratio ** alpha) * (max_ratio ** -1.200) * (0.9938 ** age) * sex_coeff

        # Stage
        if egfr >= 90:
            stage = "G1 - Normal"
        elif egfr >= 60:
            stage = "G2 - Mildly decreased"
        elif egfr >= 45:
            stage = "G3a - Mild-moderately decreased"
        elif egfr >= 30:
            stage = "G3b - Moderate-severely decreased"
        elif egfr >= 15:
            stage = "G4 - Severely decreased"
        else:
            stage = "G5 - Kidney failure"

        return {
            "type": "LAB_GFR",
            "eGFR": round(egfr, 1),
            "unit": "mL/min/1.73m²",
            "stage": stage,
            "equation": "CKD-EPI 2021 (race-free)"
        }

    def abg_interpret(self, ph: float, pco2: float, hco3: float) -> Dict:
        """Interpret arterial blood gas results."""
        # Primary disorder
        if ph < 7.35:
            if pco2 > 45:
                primary = "Respiratory Acidosis"
            elif hco3 < 22:
                primary = "Metabolic Acidosis"
            else:
                primary = "Mixed Acidosis"
        elif ph > 7.45:
            if pco2 < 35:
                primary = "Respiratory Alkalosis"
            elif hco3 > 26:
                primary = "Metabolic Alkalosis"
            else:
                primary = "Mixed Alkalosis"
        else:
            primary = "Normal"

        # Compensation
        compensation = "None"
        if primary.startswith("Respiratory Acidosis") and hco3 > 26:
            compensation = "Metabolic compensation (elevated HCO3)"
        elif primary.startswith("Metabolic Acidosis") and pco2 < 35:
            compensation = "Respiratory compensation (hyperventilation)"
        elif primary.startswith("Respiratory Alkalosis") and hco3 < 22:
            compensation = "Metabolic compensation (reduced HCO3)"
        elif primary.startswith("Metabolic Alkalosis") and pco2 > 45:
            compensation = "Respiratory compensation (hypoventilation)"

        return {
            "type": "LAB_ABG",
            "ph": ph, "pco2": pco2, "hco3": hco3,
            "primary_disorder": primary,
            "compensation": compensation
        }

    def list_tests(self, panel: str = None) -> List[str]:
        """List available lab tests."""
        if panel:
            return [k for k, v in self.references.items() if v.panel == panel]
        return list(self.references.keys())

    def list_panels(self) -> List[str]:
        """List available lab panels."""
        return list(set(v.panel for v in self.references.values() if v.panel))
