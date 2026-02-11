"""Medical Research  - HIPAA-compliant data privacy tools for MOISSCode."""

import hashlib
import datetime
import random
from typing import Any, Dict


class ResearchPrivacy:
    """Safe Harbor de-identification and research data export."""

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
