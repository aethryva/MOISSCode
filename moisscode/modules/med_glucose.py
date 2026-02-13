"""
med.glucose - Diabetes & Glucose Management Module for MOISSCode
HbA1c estimation, CGM analytics, insulin dosing algorithms, and DKA assessment.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import math


@dataclass
class InsulinRegimen:
    """Calculated insulin regimen for a patient."""
    tdd: float              # Total Daily Dose (units)
    basal_dose: float       # Basal insulin (units/day)
    basal_pct: float        # % of TDD as basal
    isf: float              # Insulin Sensitivity Factor
    icr: float              # Insulin-to-Carb Ratio
    isf_rule: str           # Which rule was used
    icr_rule: str           # Which rule was used


class GlucoseEngine:
    """Diabetes and glucose management engine for MOISSCode."""

    # ── HbA1c / eAG Conversions ────────────────────────────

    @staticmethod
    def hba1c_from_glucose(mean_glucose_mgdl: float) -> dict:
        """
        Estimate HbA1c from mean glucose using the ADAG equation.
        eA1C = (mean_glucose + 46.7) / 28.7
        Source: Nathan et al., Diabetes Care 2008.
        """
        mean_glucose_mgdl = float(mean_glucose_mgdl)
        a1c = (mean_glucose_mgdl + 46.7) / 28.7

        if a1c < 5.7:
            category = "NORMAL"
        elif a1c < 6.5:
            category = "PREDIABETES"
        else:
            category = "DIABETES"

        return {
            'type': 'GLUCOSE',
            'method': 'ADAG',
            'mean_glucose_mgdl': mean_glucose_mgdl,
            'estimated_hba1c': round(a1c, 1),
            'category': category
        }

    @staticmethod
    def glucose_from_hba1c(hba1c: float) -> dict:
        """
        Estimate mean glucose from HbA1c using the ADAG equation.
        eAG = 28.7 * A1C - 46.7
        """
        hba1c = float(hba1c)
        eag = 28.7 * hba1c - 46.7

        return {
            'type': 'GLUCOSE',
            'method': 'ADAG_reverse',
            'hba1c': hba1c,
            'estimated_mean_glucose_mgdl': round(eag, 1),
            'estimated_mean_glucose_mmol': round(eag / 18.0, 1)
        }

    # ── CGM Analytics ──────────────────────────────────────

    @staticmethod
    def time_in_range(readings: list, low: float = 70, high: float = 180) -> dict:
        """
        Calculate Time In Range (TIR) from CGM readings.
        International consensus targets: 70-180 mg/dL for T1D/T2D.
        Returns TIR, time below range (TBR), time above range (TAR).
        """
        readings = [float(r) for r in readings]
        total = len(readings)
        if total == 0:
            return {'type': 'GLUCOSE', 'error': 'No readings provided'}

        low = float(low)
        high = float(high)

        in_range = sum(1 for r in readings if low <= r <= high)
        below = sum(1 for r in readings if r < low)
        very_below = sum(1 for r in readings if r < 54)
        above = sum(1 for r in readings if r > high)
        very_above = sum(1 for r in readings if r > 250)

        tir = round(100 * in_range / total, 1)

        # Targets per international consensus
        if tir >= 70:
            assessment = "EXCELLENT"
        elif tir >= 50:
            assessment = "GOOD"
        elif tir >= 30:
            assessment = "NEEDS_IMPROVEMENT"
        else:
            assessment = "POOR"

        return {
            'type': 'GLUCOSE_TIR',
            'total_readings': total,
            'time_in_range_pct': tir,
            'time_below_range_pct': round(100 * below / total, 1),
            'time_below_54_pct': round(100 * very_below / total, 1),
            'time_above_range_pct': round(100 * above / total, 1),
            'time_above_250_pct': round(100 * very_above / total, 1),
            'range_low': low,
            'range_high': high,
            'assessment': assessment
        }

    @staticmethod
    def gmi(mean_glucose_mgdl: float) -> dict:
        """
        Glucose Management Indicator (GMI).
        GMI = 3.31 + 0.02392 * mean_glucose_mgdl
        Replaces "estimated A1C" for CGM data. Source: Bergenstal et al. 2018.
        """
        mean_glucose_mgdl = float(mean_glucose_mgdl)
        gmi_val = 3.31 + 0.02392 * mean_glucose_mgdl

        return {
            'type': 'GLUCOSE',
            'method': 'GMI',
            'mean_glucose_mgdl': mean_glucose_mgdl,
            'gmi': round(gmi_val, 1),
            'interpretation': 'GMI approximates lab A1C from CGM data'
        }

    @staticmethod
    def glycemic_variability(readings: list) -> dict:
        """
        Calculate glycemic variability metrics from CGM data.
        CV (coefficient of variation) < 36% is the target.
        """
        readings = [float(r) for r in readings]
        n = len(readings)
        if n < 2:
            return {'type': 'GLUCOSE', 'error': 'Need >= 2 readings'}

        mean_val = sum(readings) / n
        variance = sum((r - mean_val) ** 2 for r in readings) / (n - 1)
        sd = math.sqrt(variance)
        cv = (sd / mean_val * 100) if mean_val > 0 else 0

        # MAGE (Mean Amplitude of Glycemic Excursions) - simplified
        excursions = []
        for i in range(1, n):
            diff = abs(readings[i] - readings[i-1])
            if diff > sd:
                excursions.append(diff)
        mage = sum(excursions) / len(excursions) if excursions else 0

        if cv < 36:
            stability = "STABLE"
        elif cv < 50:
            stability = "MODERATE_VARIABILITY"
        else:
            stability = "HIGH_VARIABILITY"

        return {
            'type': 'GLUCOSE_VARIABILITY',
            'mean': round(mean_val, 1),
            'sd': round(sd, 1),
            'cv_percent': round(cv, 1),
            'mage': round(mage, 1),
            'min': round(min(readings), 1),
            'max': round(max(readings), 1),
            'stability': stability,
            'target': 'CV < 36%'
        }

    # ── Insulin Dosing ─────────────────────────────────────

    @staticmethod
    def insulin_sensitivity_factor(tdd: float, insulin_type: str = "rapid") -> dict:
        """
        Calculate Insulin Sensitivity Factor (ISF).
        Rapid-acting: 1800 rule. Regular: 1500 rule.
        ISF = how much 1 unit of insulin drops glucose (mg/dL).
        """
        tdd = float(tdd)
        if tdd <= 0:
            return {'type': 'GLUCOSE', 'error': 'TDD must be > 0'}

        if insulin_type == "regular":
            isf = 1500 / tdd
            rule = "1500 rule"
        else:
            isf = 1800 / tdd
            rule = "1800 rule"

        return {
            'type': 'GLUCOSE_ISF',
            'tdd': tdd,
            'isf': round(isf, 1),
            'rule': rule,
            'unit': 'mg/dL per unit',
            'interpretation': f'1 unit lowers glucose by ~{round(isf)} mg/dL'
        }

    @staticmethod
    def carb_ratio(tdd: float) -> dict:
        """
        Calculate Insulin-to-Carb Ratio (ICR) using the 500 rule.
        ICR = 500 / TDD. Result = grams of carbs covered by 1 unit.
        """
        tdd = float(tdd)
        if tdd <= 0:
            return {'type': 'GLUCOSE', 'error': 'TDD must be > 0'}

        icr = 500 / tdd

        return {
            'type': 'GLUCOSE_ICR',
            'tdd': tdd,
            'icr': round(icr, 1),
            'rule': '500 rule',
            'interpretation': f'1 unit covers ~{round(icr)} g carbohydrates'
        }

    @staticmethod
    def correction_dose(current_bg: float, target_bg: float, isf: float) -> dict:
        """
        Calculate correction insulin dose.
        Correction = (current_BG - target_BG) / ISF
        """
        current_bg = float(current_bg)
        target_bg = float(target_bg)
        isf = float(isf)

        if isf <= 0:
            return {'type': 'GLUCOSE', 'error': 'ISF must be > 0'}

        correction = (current_bg - target_bg) / isf

        return {
            'type': 'GLUCOSE_CORRECTION',
            'current_bg': current_bg,
            'target_bg': target_bg,
            'isf': isf,
            'correction_units': round(max(0, correction), 1),
            'action': 'Give correction insulin' if correction > 0 else 'No correction needed'
        }

    @staticmethod
    def basal_rate(tdd: float) -> dict:
        """
        Calculate basal insulin dose using the 50% rule.
        Basal = 50% of TDD. Remainder is bolus/mealtime.
        """
        tdd = float(tdd)
        basal = tdd * 0.5
        bolus = tdd * 0.5

        return {
            'type': 'GLUCOSE_BASAL',
            'tdd': tdd,
            'basal_units_per_day': round(basal, 1),
            'bolus_units_per_day': round(bolus, 1),
            'rule': '50% rule',
            'hourly_rate': round(basal / 24, 2)
        }

    @staticmethod
    def sliding_scale(current_bg: float) -> dict:
        """
        Traditional sliding scale insulin dosing.
        Returns recommended rapid-acting insulin dose.
        """
        current_bg = float(current_bg)

        if current_bg < 70:
            dose = 0
            action = "HYPOGLYCEMIA - give glucose, hold insulin"
            severity = "critical"
        elif current_bg <= 150:
            dose = 0
            action = "No insulin needed"
            severity = "normal"
        elif current_bg <= 200:
            dose = 2
            action = "Low-dose correction"
            severity = "mild"
        elif current_bg <= 250:
            dose = 4
            action = "Moderate correction"
            severity = "moderate"
        elif current_bg <= 300:
            dose = 6
            action = "Significant correction"
            severity = "elevated"
        elif current_bg <= 350:
            dose = 8
            action = "High correction"
            severity = "high"
        elif current_bg <= 400:
            dose = 10
            action = "Very high correction - monitor closely"
            severity = "high"
        else:
            dose = 12
            action = "CRITICAL - consider IV insulin, call physician"
            severity = "critical"

        return {
            'type': 'GLUCOSE_SLIDING_SCALE',
            'current_bg': current_bg,
            'recommended_dose_units': dose,
            'action': action,
            'severity': severity
        }

    @staticmethod
    def full_regimen(tdd: float, insulin_type: str = "rapid") -> dict:
        """
        Calculate a complete insulin regimen from TDD.
        Returns basal dose, ISF, ICR, and hourly pump rate.
        """
        tdd = float(tdd)
        if tdd <= 0:
            return {'type': 'GLUCOSE', 'error': 'TDD must be > 0'}

        basal = tdd * 0.5
        if insulin_type == "regular":
            isf = 1500 / tdd
            isf_rule = "1500 rule"
        else:
            isf = 1800 / tdd
            isf_rule = "1800 rule"
        icr = 500 / tdd

        return {
            'type': 'GLUCOSE_REGIMEN',
            'tdd': tdd,
            'basal_units_per_day': round(basal, 1),
            'basal_hourly_rate': round(basal / 24, 2),
            'bolus_units_per_day': round(tdd - basal, 1),
            'isf': round(isf, 1),
            'isf_rule': isf_rule,
            'icr': round(icr, 1),
            'icr_rule': '500 rule'
        }

    # ── DKA Assessment ─────────────────────────────────────

    @staticmethod
    def dka_check(glucose: float, ph: float = 7.4, bicarb: float = 24,
                  ketones: float = 0) -> dict:
        """
        Diabetic Ketoacidosis (DKA) diagnostic assessment.
        Criteria: glucose > 250, pH < 7.3, bicarb < 18, ketones present.
        """
        glucose = float(glucose)
        ph = float(ph)
        bicarb = float(bicarb)
        ketones = float(ketones)

        criteria_met = 0
        findings = []

        if glucose > 250:
            criteria_met += 1
            findings.append(f"Hyperglycemia: {glucose} mg/dL")
        if ph < 7.3:
            criteria_met += 1
            findings.append(f"Acidosis: pH {ph}")
        if bicarb < 18:
            criteria_met += 1
            findings.append(f"Low bicarbonate: {bicarb} mEq/L")
        if ketones > 0.6:
            criteria_met += 1
            findings.append(f"Ketonemia: {ketones} mmol/L")

        # Severity classification
        if ph < 7.0 or bicarb < 5:
            severity = "SEVERE"
            management = "ICU admission, IV insulin drip, aggressive fluid resuscitation"
        elif ph < 7.15 or bicarb < 10:
            severity = "MODERATE"
            management = "IV insulin drip, fluid resuscitation, hourly monitoring"
        elif criteria_met >= 3:
            severity = "MILD"
            management = "SC insulin, IV fluids, q2h monitoring"
        else:
            severity = "NOT_DKA"
            management = "Continue monitoring, standard glucose management"

        return {
            'type': 'GLUCOSE_DKA',
            'glucose': glucose,
            'ph': ph,
            'bicarb': bicarb,
            'ketones': ketones,
            'criteria_met': criteria_met,
            'findings': findings,
            'diagnosis': 'DKA' if criteria_met >= 3 else 'NOT_DKA',
            'severity': severity,
            'management': management
        }

    # ── Hypoglycemia Assessment ────────────────────────────

    @staticmethod
    def hypo_check(glucose: float) -> dict:
        """
        Hypoglycemia classification per ADA guidelines.
        Level 1: < 70 mg/dL, Level 2: < 54 mg/dL, Level 3: severe (altered consciousness).
        """
        glucose = float(glucose)

        if glucose < 54:
            level = 2
            severity = "CLINICALLY_SIGNIFICANT"
            action = "Immediate fast-acting glucose (15-20g), recheck in 15 min"
        elif glucose < 70:
            level = 1
            severity = "ALERT_VALUE"
            action = "Consume 15g fast-acting carbohydrate, recheck in 15 min"
        else:
            level = 0
            severity = "NORMAL"
            action = "No intervention needed"

        return {
            'type': 'GLUCOSE_HYPO',
            'glucose': glucose,
            'level': level,
            'severity': severity,
            'action': action
        }
