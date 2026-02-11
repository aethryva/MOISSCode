"""Medical Scores  - standardized clinical calculators for MOISSCode."""

from typing import Any


class ClinicalScores:
    """qSOFA, SOFA, and other validated clinical scoring systems."""

    @staticmethod
    def qsofa(patient: Any) -> int:
        """Quick SOFA score (0-3): RR ≥ 22, SBP ≤ 100, GCS < 15."""
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
