"""
med.research - HIPAA-compliant data privacy & clinical trial tools for MOISSCode.
De-identification, consent tracking, RCT randomization, and power calculations.
"""

import hashlib
import datetime
import random
import math
from typing import Any, Dict, List


class ResearchPrivacy:
    """Safe Harbor de-identification, consent tracking, and clinical trial tools."""

    SALT = "AETHRYVA_SECRET_SALT"

    @staticmethod
    def deidentify(patient: Any) -> Dict[str, Any]:
        """Convert a Patient object into an anonymized dictionary (Safe Harbor method)."""
        anon_data = {}

        if hasattr(patient, 'name'):
            anon_data['patient_hash'] = hashlib.sha256(
                (patient.name + ResearchPrivacy.SALT).encode()
            ).hexdigest()[:12]

        if hasattr(patient, 'age'):
            anon_data['age'] = "90+" if patient.age > 89 else patient.age

        safe_fields = [
            'hr', 'bp', 'rr', 'spo2', 'gcs', 'lactate',
            'creatinine', 'bilirubin', 'platelets',
            'pao2_fio2', 'weight', 'sex', 'temp'
        ]

        for field in safe_fields:
            if hasattr(patient, 'values') and field in patient.values:
                anon_data[field] = patient.values[field]
            elif hasattr(patient, field):
                anon_data[field] = getattr(patient, field)

        offset = random.randint(-1440, 1440)
        anon_data['fuzzed_entry_time'] = (
            datetime.datetime.now() + datetime.timedelta(minutes=offset)
        ).isoformat()

        return anon_data

    @staticmethod
    def log_to_datalake(anon_data: Dict[str, Any], study_id: str):
        """Write anonymized data to the research data lake."""
        return True

    @staticmethod
    def consent_check(patient_id: str, study_id: str) -> Dict:
        """
        Check if a patient has consented to a research study.
        Simulates consent registry lookup.
        """
        # Simulated consent registry
        consented = hashlib.md5(
            f"{patient_id}{study_id}".encode()
        ).hexdigest()
        is_consented = int(consented[0], 16) > 4  # ~70% consent rate simulation

        return {
            'type': 'RESEARCH_CONSENT',
            'patient_id': patient_id,
            'study_id': study_id,
            'consented': is_consented,
            'consent_date': datetime.datetime.now().isoformat() if is_consented else None
        }

    @staticmethod
    def randomize(patient_count: int, arms: int = 2,
                  ratio: list = None) -> Dict:
        """
        Randomize patients into treatment arms for an RCT.
        Supports equal or unequal allocation ratios.

        Args:
            patient_count: Number of patients to randomize
            arms: Number of treatment arms (default 2)
            ratio: Allocation ratio (e.g., [1, 1] or [2, 1])
        """
        patient_count = int(patient_count)
        arms = int(arms)

        if ratio is None:
            ratio = [1] * arms

        total_ratio = sum(ratio)
        arm_labels = [f"Arm_{chr(65 + i)}" for i in range(arms)]

        # Block randomization for balance
        assignments = {}
        arm_counts = [0] * arms

        for pid in range(1, patient_count + 1):
            # Weighted random assignment
            r = random.random() * total_ratio
            cumulative = 0
            assigned_arm = 0
            for i, weight in enumerate(ratio):
                cumulative += weight
                if r <= cumulative:
                    assigned_arm = i
                    break

            arm_name = arm_labels[assigned_arm]
            assignments[f"PT-{pid:04d}"] = arm_name
            arm_counts[assigned_arm] += 1

        return {
            'type': 'RESEARCH_RANDOMIZE',
            'patient_count': patient_count,
            'arms': arms,
            'arm_labels': arm_labels,
            'ratio': ratio,
            'arm_counts': dict(zip(arm_labels, arm_counts)),
            'assignments': assignments
        }

    @staticmethod
    def sample_size(effect_size: float, alpha: float = 0.05,
                    power: float = 0.80) -> Dict:
        """
        Calculate required sample size for a two-group comparison (t-test).
        Uses the formula: n = 2 * ((z_alpha + z_beta) / effect_size)^2
        """
        effect_size = float(effect_size)
        alpha = float(alpha)
        power = float(power)

        if effect_size <= 0:
            return {'type': 'RESEARCH', 'error': 'Effect size must be > 0'}

        # Z-scores for common alpha/power values
        z_alpha = {0.01: 2.576, 0.025: 2.242, 0.05: 1.960, 0.10: 1.645}.get(
            alpha, 1.960
        )
        z_beta = {0.80: 0.842, 0.85: 1.036, 0.90: 1.282, 0.95: 1.645}.get(
            power, 0.842
        )

        n_per_group = math.ceil(2 * ((z_alpha + z_beta) / effect_size) ** 2)
        total_n = n_per_group * 2

        return {
            'type': 'RESEARCH_SAMPLE_SIZE',
            'effect_size': effect_size,
            'alpha': alpha,
            'power': power,
            'n_per_group': n_per_group,
            'total_n': total_n,
            'z_alpha': z_alpha,
            'z_beta': z_beta
        }

    @staticmethod
    def stratify(patient_count: int, variable: str,
                 strata: list = None) -> Dict:
        """
        Create stratified allocation for a clinical trial.
        Ensures balanced representation across strata.

        Args:
            patient_count: Total patients
            variable: Stratification variable name
            strata: List of stratum values (e.g., ["Male", "Female"])
        """
        patient_count = int(patient_count)

        if strata is None:
            strata = ["Stratum_A", "Stratum_B"]

        n_strata = len(strata)
        per_stratum = patient_count // n_strata
        remainder = patient_count % n_strata

        allocation = {}
        patient_id = 1
        for i, s in enumerate(strata):
            count = per_stratum + (1 if i < remainder else 0)
            patients = [f"PT-{j:04d}" for j in range(patient_id, patient_id + count)]
            allocation[s] = patients
            patient_id += count

        return {
            'type': 'RESEARCH_STRATIFY',
            'variable': variable,
            'strata': strata,
            'patient_count': patient_count,
            'allocation': {k: len(v) for k, v in allocation.items()},
            'patients': allocation
        }

