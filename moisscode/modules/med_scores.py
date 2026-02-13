"""Medical Scores - standardized clinical calculators for MOISSCode."""

from typing import Any
import math


class ClinicalScores:
    """Validated clinical scoring systems: sepsis, cardiac, hepatic, pulmonary, renal, and general."""

    # ── Sepsis ─────────────────────────────────────────────

    @staticmethod
    def qsofa(patient: Any) -> int:
        """Quick SOFA score (0-3): RR >= 22, SBP <= 100, GCS < 15."""
        score = 0
        if hasattr(patient, 'rr') and patient.rr >= 22:
            score += 1
        if hasattr(patient, 'bp') and patient.bp <= 100:
            score += 1
        elif hasattr(patient, 'sbp') and patient.sbp <= 100:
            score += 1
        if hasattr(patient, 'gcs') and patient.gcs < 15:
            score += 1
        return score

    @staticmethod
    def sofa(patient: Any) -> int:
        """Sequential Organ Failure Assessment score (0-24)."""
        score = 0

        if hasattr(patient, 'pao2_fio2'):
            ratio = patient.pao2_fio2
            if ratio < 100: score += 4
            elif ratio < 200: score += 3
            elif ratio < 300: score += 2
            elif ratio < 400: score += 1

        if hasattr(patient, 'platelets'):
            plt = patient.platelets
            if plt < 20: score += 4
            elif plt < 50: score += 3
            elif plt < 100: score += 2
            elif plt < 150: score += 1

        if hasattr(patient, 'bilirubin'):
            bili = patient.bilirubin
            if bili > 12: score += 4
            elif bili > 6: score += 3
            elif bili > 2: score += 2
            elif bili > 1.2: score += 1

        if hasattr(patient, 'map'):
            if patient.map < 70: score += 1
            if hasattr(patient, 'on_vasopressors') and patient.on_vasopressors:
                score += 2

        if hasattr(patient, 'gcs'):
            gcs = patient.gcs
            if gcs < 6: score += 4
            elif gcs < 10: score += 3
            elif gcs < 13: score += 2
            elif gcs < 15: score += 1

        if hasattr(patient, 'creatinine'):
            cr = patient.creatinine
            if cr > 5.0: score += 4
            elif cr > 3.5: score += 3
            elif cr > 2.0: score += 2
            elif cr > 1.2: score += 1

        return score

    # ── General / Early Warning ────────────────────────────

    @staticmethod
    def news2(patient: Any) -> dict:
        """
        National Early Warning Score 2 (NEWS2).
        Used across UK NHS. Score 0-20, triggers clinical escalation.
        """
        score = 0

        # Respiratory rate
        rr = getattr(patient, 'rr', 16)
        if rr <= 8: score += 3
        elif rr <= 11: score += 1
        elif rr <= 20: score += 0
        elif rr <= 24: score += 2
        else: score += 3

        # SpO2 (Scale 1 - normal)
        spo2 = getattr(patient, 'spo2', 98)
        if spo2 <= 91: score += 3
        elif spo2 <= 93: score += 2
        elif spo2 <= 95: score += 1

        # Systolic BP
        sbp = getattr(patient, 'bp', 120)
        if sbp <= 90: score += 3
        elif sbp <= 100: score += 2
        elif sbp <= 110: score += 1
        elif sbp <= 219: score += 0
        else: score += 3

        # Heart rate
        hr = getattr(patient, 'hr', 80)
        if hr <= 40: score += 3
        elif hr <= 50: score += 1
        elif hr <= 90: score += 0
        elif hr <= 110: score += 1
        elif hr <= 130: score += 2
        else: score += 3

        # Temperature
        temp = getattr(patient, 'temp', 37.0)
        if temp <= 35.0: score += 3
        elif temp <= 36.0: score += 1
        elif temp <= 38.0: score += 0
        elif temp <= 39.0: score += 1
        else: score += 2

        # Consciousness (using GCS as proxy)
        gcs = getattr(patient, 'gcs', 15)
        if gcs < 15:
            score += 3

        # Risk classification
        if score >= 7:
            risk = "HIGH"
            action = "Emergency assessment by clinical team"
        elif score >= 5:
            risk = "MEDIUM"
            action = "Urgent review by clinician"
        elif score == 3:
            risk = "LOW-MEDIUM"
            action = "Urgent ward-based review"
        else:
            risk = "LOW"
            action = "Continue routine monitoring"

        return {
            'type': 'SCORE',
            'scoring': 'NEWS2',
            'score': score,
            'max_score': 20,
            'risk': risk,
            'action': action
        }

    # ── Cardiology ─────────────────────────────────────────

    @staticmethod
    def cha2ds2_vasc(patient: Any) -> dict:
        """
        CHA2DS2-VASc score for stroke risk in atrial fibrillation.
        Score 0-9. Guides anticoagulation therapy.
        """
        score = 0
        age = getattr(patient, 'age', 0)
        sex = getattr(patient, 'sex', 'U')

        if getattr(patient, 'chf', False): score += 1
        if getattr(patient, 'hypertension', False): score += 1
        if age >= 75: score += 2
        elif age >= 65: score += 1
        if getattr(patient, 'diabetes', False): score += 1
        if getattr(patient, 'stroke_history', False): score += 2
        if getattr(patient, 'vascular_disease', False): score += 1
        if sex == 'F': score += 1

        if score == 0:
            risk = "LOW"
            recommendation = "No anticoagulation needed"
        elif score == 1:
            risk = "MODERATE"
            recommendation = "Consider anticoagulation"
        else:
            risk = "HIGH"
            recommendation = "Anticoagulation recommended"

        return {
            'type': 'SCORE',
            'scoring': 'CHA2DS2-VASc',
            'score': score,
            'max_score': 9,
            'risk': risk,
            'recommendation': recommendation
        }

    @staticmethod
    def heart_score(patient: Any) -> dict:
        """
        HEART score for chest pain risk stratification.
        Score 0-10. Guides disposition (discharge vs observe vs intervene).
        """
        score = 0

        # History (0-2): slightly suspicious=0, moderately=1, highly=2
        history = getattr(patient, 'chest_pain_history', 1)
        score += min(int(history), 2)

        # ECG (0-2): normal=0, non-specific=1, significant ST deviation=2
        ecg = getattr(patient, 'ecg_findings', 0)
        score += min(int(ecg), 2)

        # Age
        age = getattr(patient, 'age', 0)
        if age >= 65: score += 2
        elif age >= 45: score += 1

        # Risk factors (0-2): 0=none, 1=1-2 factors, 2=3+ or known CAD
        risk_factors = getattr(patient, 'cardiac_risk_factors', 0)
        score += min(int(risk_factors), 2)

        # Troponin (0-2): normal=0, 1-3x=1, >3x=2
        troponin_level = getattr(patient, 'troponin_level', 0)
        score += min(int(troponin_level), 2)

        if score <= 3:
            risk = "LOW"
            recommendation = "Consider early discharge"
        elif score <= 6:
            risk = "MODERATE"
            recommendation = "Observation and further testing"
        else:
            risk = "HIGH"
            recommendation = "Early invasive strategy"

        return {
            'type': 'SCORE',
            'scoring': 'HEART',
            'score': score,
            'max_score': 10,
            'risk': risk,
            'recommendation': recommendation
        }

    @staticmethod
    def framingham(patient: Any) -> dict:
        """
        Framingham 10-year cardiovascular disease risk score.
        Returns estimated 10-year risk percentage.
        """
        age = getattr(patient, 'age', 50)
        sex = getattr(patient, 'sex', 'M')
        total_chol = getattr(patient, 'total_cholesterol', 200)
        hdl = getattr(patient, 'hdl', 50)
        sbp = getattr(patient, 'bp', 120)
        smoker = getattr(patient, 'smoker', False)
        bp_treated = getattr(patient, 'bp_treated', False)

        # Simplified Framingham point system (male version as default)
        points = 0

        # Age points
        if age < 35: points += 0
        elif age < 40: points += 2
        elif age < 45: points += 5
        elif age < 50: points += 6
        elif age < 55: points += 8
        elif age < 60: points += 10
        elif age < 65: points += 11
        elif age < 70: points += 12
        elif age < 75: points += 14
        else: points += 15

        # Cholesterol points
        if total_chol < 160: points += 0
        elif total_chol < 200: points += 1
        elif total_chol < 240: points += 2
        elif total_chol < 280: points += 3
        else: points += 4

        # HDL points (inverse)
        if hdl >= 60: points -= 2
        elif hdl >= 50: points -= 1
        elif hdl >= 45: points += 0
        elif hdl >= 35: points += 1
        else: points += 2

        # BP points
        if bp_treated:
            if sbp >= 160: points += 4
            elif sbp >= 140: points += 3
            elif sbp >= 130: points += 2
            elif sbp >= 120: points += 1
        else:
            if sbp >= 160: points += 3
            elif sbp >= 140: points += 2
            elif sbp >= 130: points += 1

        # Smoking
        if smoker: points += 4

        # Female adjustment
        if sex == 'F':
            points -= 3

        # Map points to 10-year risk %
        risk_map = {
            0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3,
            8: 4, 9: 5, 10: 6, 11: 8, 12: 10, 13: 12, 14: 16,
            15: 20, 16: 25, 17: 30
        }
        risk_pct = risk_map.get(max(0, min(points, 17)), 30)

        if risk_pct < 10:
            category = "LOW"
        elif risk_pct < 20:
            category = "MODERATE"
        else:
            category = "HIGH"

        return {
            'type': 'SCORE',
            'scoring': 'Framingham',
            'points': points,
            'risk_10yr_percent': risk_pct,
            'category': category
        }

    # ── Hepatology ─────────────────────────────────────────

    @staticmethod
    def meld(patient: Any) -> dict:
        """
        Model for End-Stage Liver Disease (MELD) score.
        Used for liver transplant prioritization. Score 6-40.
        """
        # Clamp values per MELD specification
        bilirubin = max(1.0, getattr(patient, 'bilirubin', 1.0))
        creatinine = max(1.0, min(4.0, getattr(patient, 'creatinine', 1.0)))
        inr = max(1.0, getattr(patient, 'inr', 1.0))
        sodium = max(125, min(137, getattr(patient, 'sodium', 137)))

        # MELD score formula
        meld_score = (0.957 * math.log(creatinine)
                     + 0.378 * math.log(bilirubin)
                     + 1.120 * math.log(inr)
                     + 0.643) * 10

        meld_score = max(6, min(40, round(meld_score)))

        # MELD-Na adjustment
        meld_na = meld_score - sodium - (0.025 * meld_score * (140 - sodium)) + 140
        meld_na = max(6, min(40, round(meld_na)))

        if meld_na >= 25:
            mortality_3mo = "HIGH (>50%)"
        elif meld_na >= 18:
            mortality_3mo = "MODERATE (20-50%)"
        elif meld_na >= 10:
            mortality_3mo = "LOW-MODERATE (6-20%)"
        else:
            mortality_3mo = "LOW (<6%)"

        return {
            'type': 'SCORE',
            'scoring': 'MELD-Na',
            'meld': meld_score,
            'meld_na': meld_na,
            'mortality_3mo': mortality_3mo
        }

    @staticmethod
    def child_pugh(patient: Any) -> dict:
        """
        Child-Pugh score for liver cirrhosis severity.
        Class A (5-6), B (7-9), C (10-15).
        """
        score = 0

        # Bilirubin
        bili = getattr(patient, 'bilirubin', 1.0)
        if bili < 2: score += 1
        elif bili <= 3: score += 2
        else: score += 3

        # Albumin
        alb = getattr(patient, 'albumin', 3.5)
        if alb > 3.5: score += 1
        elif alb >= 2.8: score += 2
        else: score += 3

        # INR
        inr = getattr(patient, 'inr', 1.0)
        if inr < 1.7: score += 1
        elif inr <= 2.3: score += 2
        else: score += 3

        # Ascites
        ascites = getattr(patient, 'ascites', 'none')
        if ascites == 'none': score += 1
        elif ascites == 'mild': score += 2
        else: score += 3

        # Encephalopathy
        enceph = getattr(patient, 'encephalopathy', 'none')
        if enceph == 'none': score += 1
        elif enceph in ('grade1', 'grade2', 'mild'): score += 2
        else: score += 3

        if score <= 6:
            cls = "A"
            survival_1yr = "100%"
            survival_2yr = "85%"
        elif score <= 9:
            cls = "B"
            survival_1yr = "80%"
            survival_2yr = "60%"
        else:
            cls = "C"
            survival_1yr = "45%"
            survival_2yr = "35%"

        return {
            'type': 'SCORE',
            'scoring': 'Child-Pugh',
            'score': score,
            'class': cls,
            'survival_1yr': survival_1yr,
            'survival_2yr': survival_2yr
        }

    # ── Pulmonology ────────────────────────────────────────

    @staticmethod
    def curb65(patient: Any) -> dict:
        """
        CURB-65 pneumonia severity score.
        Score 0-5. Guides inpatient vs outpatient treatment.
        """
        score = 0

        # Confusion (GCS < 15 as proxy)
        if getattr(patient, 'gcs', 15) < 15:
            score += 1

        # Urea/BUN > 7 mmol/L (or BUN > 19.6 mg/dL)
        bun = getattr(patient, 'bun', 0)
        urea = getattr(patient, 'urea', bun)
        if urea > 7:
            score += 1

        # Respiratory rate >= 30
        if getattr(patient, 'rr', 16) >= 30:
            score += 1

        # Blood pressure: SBP < 90 or DBP <= 60
        if getattr(patient, 'bp', 120) < 90 or getattr(patient, 'diastolic_bp', 80) <= 60:
            score += 1

        # Age >= 65
        if getattr(patient, 'age', 0) >= 65:
            score += 1

        if score <= 1:
            risk = "LOW"
            recommendation = "Outpatient treatment"
            mortality = "<3%"
        elif score == 2:
            risk = "MODERATE"
            recommendation = "Short inpatient or supervised outpatient"
            mortality = "~9%"
        else:
            risk = "HIGH"
            recommendation = "Inpatient, consider ICU if score 4-5"
            mortality = "15-40%"

        return {
            'type': 'SCORE',
            'scoring': 'CURB-65',
            'score': score,
            'max_score': 5,
            'risk': risk,
            'mortality': mortality,
            'recommendation': recommendation
        }

    @staticmethod
    def wells_pe(patient: Any) -> dict:
        """
        Wells criteria for pulmonary embolism probability.
        Score-based (simplified). Guides imaging decisions.
        """
        score = 0.0

        if getattr(patient, 'dvt_symptoms', False): score += 3.0
        if getattr(patient, 'pe_most_likely', False): score += 3.0
        if getattr(patient, 'hr', 80) > 100: score += 1.5
        if getattr(patient, 'recent_immobilization', False): score += 1.5
        if getattr(patient, 'prior_dvt_pe', False): score += 1.5
        if getattr(patient, 'hemoptysis', False): score += 1.0
        if getattr(patient, 'active_cancer', False): score += 1.0

        if score <= 4:
            probability = "LOW"
            recommendation = "D-dimer testing"
        elif score <= 6:
            probability = "MODERATE"
            recommendation = "D-dimer or CT pulmonary angiography"
        else:
            probability = "HIGH"
            recommendation = "CT pulmonary angiography"

        return {
            'type': 'SCORE',
            'scoring': 'Wells-PE',
            'score': score,
            'probability': probability,
            'recommendation': recommendation
        }

    # ── GI / Bleeding ──────────────────────────────────────

    @staticmethod
    def glasgow_blatchford(patient: Any) -> dict:
        """
        Glasgow-Blatchford Bleeding Score (GBS).
        Score 0-23. Predicts need for intervention in upper GI bleed.
        """
        score = 0

        # BUN (mg/dL converted to mmol/L ranges)
        bun = getattr(patient, 'bun', 15)
        if bun >= 25: score += 6
        elif bun >= 22.4: score += 4
        elif bun >= 18.2: score += 3
        elif bun >= 14: score += 2

        # Hemoglobin
        hgb = getattr(patient, 'hemoglobin', 14)
        sex = getattr(patient, 'sex', 'M')
        if sex == 'M':
            if hgb < 10: score += 6
            elif hgb < 12: score += 3
            elif hgb < 13: score += 1
        else:
            if hgb < 10: score += 6
            elif hgb < 12: score += 1

        # Systolic BP
        sbp = getattr(patient, 'bp', 120)
        if sbp < 90: score += 3
        elif sbp < 100: score += 2
        elif sbp < 110: score += 1

        # Heart rate >= 100
        if getattr(patient, 'hr', 80) >= 100:
            score += 1

        # Melena
        if getattr(patient, 'melena', False):
            score += 1

        # Syncope
        if getattr(patient, 'syncope', False):
            score += 2

        # Liver disease
        if getattr(patient, 'liver_disease', False):
            score += 2

        # Heart failure
        if getattr(patient, 'chf', False):
            score += 2

        if score == 0:
            risk = "VERY LOW"
            recommendation = "Consider outpatient management"
        elif score <= 3:
            risk = "LOW"
            recommendation = "Likely suitable for outpatient"
        elif score <= 8:
            risk = "MODERATE"
            recommendation = "Inpatient management"
        else:
            risk = "HIGH"
            recommendation = "Urgent intervention likely needed"

        return {
            'type': 'SCORE',
            'scoring': 'Glasgow-Blatchford',
            'score': score,
            'max_score': 23,
            'risk': risk,
            'recommendation': recommendation
        }

    # ── Renal ──────────────────────────────────────────────

    @staticmethod
    def kdigo_aki(patient: Any) -> dict:
        """
        KDIGO Acute Kidney Injury staging.
        Stage 1-3 based on creatinine rise and urine output.
        """
        baseline_cr = getattr(patient, 'baseline_creatinine', 1.0)
        current_cr = getattr(patient, 'creatinine', 1.0)
        urine_output = getattr(patient, 'urine_output_ml_kg_hr', 1.0)

        cr_ratio = current_cr / baseline_cr if baseline_cr > 0 else 1.0
        cr_rise = current_cr - baseline_cr

        # Stage by creatinine
        if current_cr >= 4.0 or cr_ratio >= 3.0:
            stage = 3
        elif cr_ratio >= 2.0:
            stage = 2
        elif cr_rise >= 0.3 or cr_ratio >= 1.5:
            stage = 1
        else:
            stage = 0

        # Stage by urine output (can upgrade but not downgrade)
        if urine_output < 0.3:
            uo_stage = 3
        elif urine_output < 0.5:
            uo_stage = 2
        else:
            uo_stage = 0

        final_stage = max(stage, uo_stage)

        if final_stage == 0:
            risk = "NO AKI"
            management = "Monitor"
        elif final_stage == 1:
            risk = "Stage 1 AKI"
            management = "Fluid resuscitation, avoid nephrotoxins"
        elif final_stage == 2:
            risk = "Stage 2 AKI"
            management = "Nephrology consult, dose adjustment"
        else:
            risk = "Stage 3 AKI"
            management = "Consider renal replacement therapy"

        return {
            'type': 'SCORE',
            'scoring': 'KDIGO-AKI',
            'stage': final_stage,
            'creatinine_ratio': round(cr_ratio, 2),
            'risk': risk,
            'management': management
        }

    # ── ICU ────────────────────────────────────────────────

    @staticmethod
    def apache_ii(patient: Any) -> dict:
        """
        APACHE II (Acute Physiology and Chronic Health Evaluation).
        Score 0-71. Predicts ICU mortality. Based on worst values in first 24h.
        """
        score = 0

        # Temperature
        temp = getattr(patient, 'temp', 37.0)
        if temp >= 41 or temp <= 29.9: score += 4
        elif temp >= 39 or temp <= 31.9: score += 3
        elif temp >= 38.5 or temp <= 33.9: score += 1

        # MAP
        map_val = getattr(patient, 'map', 80)
        if map_val >= 160 or map_val <= 49: score += 4
        elif map_val >= 130 or map_val <= 59: score += 3
        elif map_val >= 110 or map_val <= 69: score += 2

        # Heart rate
        hr = getattr(patient, 'hr', 80)
        if hr >= 180 or hr <= 39: score += 4
        elif hr >= 140 or hr <= 54: score += 3
        elif hr >= 110 or hr <= 69: score += 2

        # Respiratory rate
        rr = getattr(patient, 'rr', 16)
        if rr >= 50 or rr <= 5: score += 4
        elif rr >= 35 or rr <= 9: score += 3
        elif rr >= 25: score += 1

        # GCS (15 - GCS)
        gcs = getattr(patient, 'gcs', 15)
        score += (15 - gcs)

        # Age points
        age = getattr(patient, 'age', 0)
        if age >= 75: score += 6
        elif age >= 65: score += 5
        elif age >= 55: score += 3
        elif age >= 45: score += 2

        # Chronic health (simplified)
        if getattr(patient, 'chronic_organ_failure', False):
            if getattr(patient, 'emergency_surgery', False):
                score += 5
            else:
                score += 2

        # Estimated mortality (simplified lookup)
        if score <= 4: mortality = "<4%"
        elif score <= 9: mortality = "~8%"
        elif score <= 14: mortality = "~15%"
        elif score <= 19: mortality = "~25%"
        elif score <= 24: mortality = "~40%"
        elif score <= 29: mortality = "~55%"
        elif score <= 34: mortality = "~75%"
        else: mortality = ">85%"

        return {
            'type': 'SCORE',
            'scoring': 'APACHE-II',
            'score': score,
            'max_score': 71,
            'estimated_mortality': mortality
        }
