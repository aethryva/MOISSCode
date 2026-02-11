"""
med.nutrition — Clinical Nutrition Module for MOISSCode
Caloric calculations, TPN formulations, BMI, and metabolic equations.
"""

import math
from typing import Dict, Optional


class NutritionEngine:
    """Clinical nutrition and metabolic calculations."""

    # ─── BMI ───────────────────────────────────────────────────
    def bmi(self, weight_kg: float, height_cm: float) -> Dict:
        """
        Calculate Body Mass Index.
        BMI = weight(kg) / height(m)²
        """
        height_m = height_cm / 100.0
        bmi_val = weight_kg / (height_m ** 2) if height_m > 0 else 0

        if bmi_val < 18.5:
            category = "Underweight"
        elif bmi_val < 25:
            category = "Normal"
        elif bmi_val < 30:
            category = "Overweight"
        elif bmi_val < 35:
            category = "Obese Class I"
        elif bmi_val < 40:
            category = "Obese Class II"
        else:
            category = "Obese Class III (Morbid)"

        return {
            "type": "NUTR_BMI",
            "bmi": round(bmi_val, 1),
            "category": category,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
        }

    # ─── Ideal Body Weight ─────────────────────────────────────
    def ideal_body_weight(self, height_cm: float, sex: str = "M") -> Dict:
        """
        Devine formula for Ideal Body Weight.
        Male:   IBW = 50 + 2.3 × (height_inches - 60)
        Female: IBW = 45.5 + 2.3 × (height_inches - 60)
        """
        height_in = height_cm / 2.54
        if sex.upper() == "M":
            ibw = 50.0 + 2.3 * max(0, height_in - 60)
        else:
            ibw = 45.5 + 2.3 * max(0, height_in - 60)

        return {
            "type": "NUTR_IBW",
            "ibw_kg": round(ibw, 1),
            "height_cm": height_cm,
            "sex": sex,
            "formula": "Devine"
        }

    def adjusted_body_weight(self, actual_kg: float, height_cm: float,
                              sex: str = "M") -> Dict:
        """Adjusted body weight for obese patients: AdjBW = IBW + 0.4 × (Actual - IBW)"""
        ibw_result = self.ideal_body_weight(height_cm, sex)
        ibw = ibw_result["ibw_kg"]
        adj = ibw + 0.4 * (actual_kg - ibw)

        return {
            "type": "NUTR_ADJBW",
            "adjusted_bw_kg": round(adj, 1),
            "ibw_kg": ibw,
            "actual_kg": actual_kg,
            "use_adjusted": actual_kg > ibw * 1.2  # Use if >120% IBW
        }

    # ─── Basal Metabolic Rate ──────────────────────────────────
    def harris_benedict(self, weight_kg: float, height_cm: float,
                        age: int, sex: str = "M") -> Dict:
        """
        Harris-Benedict equation for Basal Energy Expenditure (BEE).
        Male:   BEE = 66.5 + 13.75×W + 5.003×H - 6.755×A
        Female: BEE = 655.1 + 9.563×W + 1.850×H - 4.676×A
        """
        if sex.upper() == "M":
            bee = 66.5 + 13.75 * weight_kg + 5.003 * height_cm - 6.755 * age
        else:
            bee = 655.1 + 9.563 * weight_kg + 1.850 * height_cm - 4.676 * age

        return {
            "type": "NUTR_BEE",
            "bee_kcal": round(bee, 0),
            "formula": "Harris-Benedict",
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "age": age,
            "sex": sex,
        }

    def mifflin_st_jeor(self, weight_kg: float, height_cm: float,
                        age: int, sex: str = "M") -> Dict:
        """
        Mifflin-St Jeor equation (more accurate than Harris-Benedict).
        Male:   REE = 10×W + 6.25×H - 5×A + 5
        Female: REE = 10×W + 6.25×H - 5×A - 161
        """
        if sex.upper() == "M":
            ree = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            ree = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

        return {
            "type": "NUTR_REE",
            "ree_kcal": round(ree, 0),
            "formula": "Mifflin-St Jeor",
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "age": age,
            "sex": sex,
        }

    # ─── Stress/Activity Factors ───────────────────────────────
    def total_energy(self, bee_kcal: float, activity: str = "sedentary",
                     stress: str = "none") -> Dict:
        """
        Calculate Total Energy Expenditure with activity and stress factors.
        TEE = BEE × Activity Factor × Stress Factor
        """
        activity_factors = {
            "bedrest": 1.2,
            "sedentary": 1.3,
            "ambulatory": 1.5,
            "active": 1.7,
            "very_active": 1.9
        }
        stress_factors = {
            "none": 1.0,
            "minor_surgery": 1.1,
            "major_surgery": 1.2,
            "infection": 1.3,
            "sepsis": 1.5,
            "burns_20": 1.5,
            "burns_40": 1.8,
            "burns_60": 2.0,
            "trauma": 1.35,
            "head_injury": 1.6,
        }

        af = activity_factors.get(activity, 1.3)
        sf = stress_factors.get(stress, 1.0)
        tee = bee_kcal * af * sf

        return {
            "type": "NUTR_TEE",
            "tee_kcal": round(tee, 0),
            "bee_kcal": bee_kcal,
            "activity_factor": af,
            "stress_factor": sf,
            "activity": activity,
            "stress": stress
        }

    # ─── ICU Nutrition ─────────────────────────────────────────
    def icu_caloric_target(self, weight_kg: float, phase: str = "acute") -> Dict:
        """
        ICU nutrition targets (ASPEN/SCCM 2024 guidelines).
        Acute (days 1-2):  12-20 kcal/kg/day
        Recovery:          25-30 kcal/kg/day
        """
        targets = {
            "acute":    {"low": 12, "high": 20, "protein_g_per_kg": 1.2},
            "early":    {"low": 15, "high": 20, "protein_g_per_kg": 1.2},
            "recovery": {"low": 25, "high": 30, "protein_g_per_kg": 1.5},
            "obese":    {"low": 11, "high": 14, "protein_g_per_kg": 2.0},
        }

        t = targets.get(phase, targets["acute"])
        return {
            "type": "NUTR_ICU",
            "phase": phase,
            "calorie_target_low": round(t["low"] * weight_kg),
            "calorie_target_high": round(t["high"] * weight_kg),
            "protein_target_g": round(t["protein_g_per_kg"] * weight_kg),
            "kcal_per_kg_range": f"{t['low']}-{t['high']}",
            "protein_g_per_kg": t["protein_g_per_kg"],
            "weight_kg": weight_kg,
            "guideline": "ASPEN/SCCM 2024"
        }

    # ─── TPN Formulation ──────────────────────────────────────
    def tpn_calculate(self, weight_kg: float, calorie_target: float,
                      protein_target_g: float) -> Dict:
        """
        Calculate TPN (Total Parenteral Nutrition) components.
        Protein: 4 kcal/g (from amino acids)
        Dextrose: 3.4 kcal/g
        Lipid: 10 kcal/g (20% intralipid)
        """
        # Protein calories
        protein_kcal = protein_target_g * 4.0
        non_protein_kcal = calorie_target - protein_kcal

        # Split non-protein: 60-70% dextrose, 30-40% lipid
        dextrose_kcal = non_protein_kcal * 0.65
        lipid_kcal = non_protein_kcal * 0.35

        dextrose_g = dextrose_kcal / 3.4
        lipid_g = lipid_kcal / 10.0  # 20% intralipid

        # Volume (rough estimate)
        amino_acid_vol_ml = protein_target_g / 0.1  # 10% amino acid solution
        dextrose_vol_ml = dextrose_g / 0.7  # 70% dextrose
        lipid_vol_ml = lipid_g / 0.2  # 20% lipid emulsion

        gir = (dextrose_g * 1000) / (weight_kg * 1440)  # mg/kg/min

        return {
            "type": "NUTR_TPN",
            "total_kcal": round(calorie_target),
            "protein_g": round(protein_target_g, 1),
            "protein_kcal": round(protein_kcal),
            "dextrose_g": round(dextrose_g, 1),
            "dextrose_kcal": round(dextrose_kcal),
            "lipid_g": round(lipid_g, 1),
            "lipid_kcal": round(lipid_kcal),
            "glucose_infusion_rate_mg_kg_min": round(gir, 2),
            "estimated_volume_ml": round(amino_acid_vol_ml + dextrose_vol_ml + lipid_vol_ml),
            "npn_ratio": round(non_protein_kcal / (protein_target_g / 6.25)) if protein_target_g > 0 else 0,
            "weight_kg": weight_kg,
            "gir_safe": gir <= 5.0,
            "gir_warning": "GIR > 5 mg/kg/min may cause hyperglycemia" if gir > 5 else None
        }

    # ─── Fluid Requirements ────────────────────────────────────
    def maintenance_fluids(self, weight_kg: float) -> Dict:
        """
        Holliday-Segar method for maintenance IV fluids.
        First 10 kg: 100 mL/kg/day
        Next 10 kg:  50 mL/kg/day
        Each kg after: 20 mL/kg/day
        """
        if weight_kg <= 10:
            vol = weight_kg * 100
        elif weight_kg <= 20:
            vol = 1000 + (weight_kg - 10) * 50
        else:
            vol = 1500 + (weight_kg - 20) * 20

        return {
            "type": "NUTR_FLUIDS",
            "daily_volume_ml": round(vol),
            "hourly_rate_ml": round(vol / 24, 1),
            "weight_kg": weight_kg,
            "formula": "Holliday-Segar"
        }
