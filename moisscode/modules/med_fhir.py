"""Medical FHIR — HL7 FHIR R4 bridge for MOISSCode.

Converts between MOISSCode Patient objects and FHIR R4 resources,
enabling interoperability with EHR systems, health information
exchanges, and clinical data warehouses.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json


# ─── FHIR Resource Templates ──────────────────────────────────

OBSERVATION_LOINC = {
    'hr':         {'code': '8867-4',  'display': 'Heart rate',            'unit': '/min'},
    'bp':         {'code': '8480-6',  'display': 'Systolic blood pressure', 'unit': 'mmHg'},
    'rr':         {'code': '9279-1',  'display': 'Respiratory rate',      'unit': '/min'},
    'temp':       {'code': '8310-5',  'display': 'Body temperature',      'unit': 'Cel'},
    'spo2':       {'code': '2708-6',  'display': 'Oxygen saturation',     'unit': '%'},
    'gcs':        {'code': '9269-2',  'display': 'Glasgow coma score',    'unit': '{score}'},
    'lactate':    {'code': '2524-7',  'display': 'Lactate',               'unit': 'mmol/L'},
    'weight':     {'code': '29463-7', 'display': 'Body weight',           'unit': 'kg'},
    'creatinine': {'code': '2160-0',  'display': 'Creatinine',            'unit': 'mg/dL'},
    'bilirubin':  {'code': '1975-2',  'display': 'Bilirubin total',       'unit': 'mg/dL'},
    'platelets':  {'code': '777-3',   'display': 'Platelets',             'unit': '10*3/uL'},
}


class FHIRBridge:
    """Bidirectional conversion between MOISSCode Patient and FHIR R4 resources."""

    # ─── Export: Patient → FHIR Bundle ─────────────────────────
    @staticmethod
    def to_fhir(patient: Any) -> Dict:
        """Convert a MOISSCode Patient to a FHIR R4 Bundle (Patient + Observations)."""
        patient_resource = FHIRBridge._build_patient_resource(patient)
        observations = FHIRBridge._build_observations(patient)

        entries = [{'resource': patient_resource}]
        for obs in observations:
            entries.append({'resource': obs})

        return {
            'resourceType': 'Bundle',
            'type': 'collection',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'entry': entries
        }

    @staticmethod
    def _build_patient_resource(patient: Any) -> Dict:
        resource = {
            'resourceType': 'Patient',
            'id': getattr(patient, 'id', 'moiss-patient-001'),
        }

        if hasattr(patient, 'name') and patient.name:
            parts = patient.name.split()
            resource['name'] = [{
                'use': 'official',
                'family': parts[-1] if len(parts) > 1 else parts[0],
                'given': parts[:-1] if len(parts) > 1 else []
            }]

        if hasattr(patient, 'sex') and patient.sex:
            resource['gender'] = 'male' if patient.sex.upper() in ('M', 'MALE') else 'female'

        if hasattr(patient, 'age') and patient.age:
            birth_year = datetime.now().year - int(patient.age)
            resource['birthDate'] = f"{birth_year}-01-01"

        return resource

    @staticmethod
    def _build_observations(patient: Any) -> List[Dict]:
        observations = []
        for field, loinc in OBSERVATION_LOINC.items():
            value = getattr(patient, field, None)
            if value is not None:
                observations.append({
                    'resourceType': 'Observation',
                    'status': 'final',
                    'code': {
                        'coding': [{
                            'system': 'http://loinc.org',
                            'code': loinc['code'],
                            'display': loinc['display']
                        }]
                    },
                    'valueQuantity': {
                        'value': float(value),
                        'unit': loinc['unit'],
                        'system': 'http://unitsofmeasure.org'
                    },
                    'effectiveDateTime': datetime.utcnow().isoformat() + 'Z'
                })
        return observations

    # ─── Import: FHIR Bundle → Patient ─────────────────────────
    @staticmethod
    def from_fhir(bundle: Dict) -> Dict:
        """Convert a FHIR R4 Bundle into a MOISSCode-compatible patient dictionary."""
        patient_data = {}
        reverse_loinc = {v['code']: k for k, v in OBSERVATION_LOINC.items()}

        for entry in bundle.get('entry', []):
            resource = entry.get('resource', {})
            rtype = resource.get('resourceType')

            if rtype == 'Patient':
                names = resource.get('name', [{}])
                if names:
                    given = ' '.join(names[0].get('given', []))
                    family = names[0].get('family', '')
                    patient_data['name'] = f"{given} {family}".strip()

                gender = resource.get('gender', '')
                patient_data['sex'] = 'M' if gender == 'male' else 'F'

                birth_date = resource.get('birthDate', '')
                if birth_date:
                    birth_year = int(birth_date[:4])
                    patient_data['age'] = datetime.now().year - birth_year

            elif rtype == 'Observation':
                codings = resource.get('code', {}).get('coding', [])
                value_qty = resource.get('valueQuantity', {})

                for coding in codings:
                    loinc_code = coding.get('code')
                    if loinc_code in reverse_loinc:
                        field_name = reverse_loinc[loinc_code]
                        patient_data[field_name] = value_qty.get('value')

        return patient_data

    # ─── FHIR REST Query Builder ───────────────────────────────
    @staticmethod
    def search_url(base: str, resource_type: str, params: Dict[str, str] = None) -> str:
        """Build a FHIR REST search URL."""
        url = f"{base.rstrip('/')}/{resource_type}"
        if params:
            query = '&'.join(f"{k}={v}" for k, v in params.items())
            url += f"?{query}"
        return url

    # ─── MedicationRequest Builder ─────────────────────────────
    @staticmethod
    def medication_request(drug_name: str, dose: float, unit: str,
                           patient_id: str = 'moiss-patient-001') -> Dict:
        """Create a FHIR MedicationRequest resource from an administer event."""
        return {
            'resourceType': 'MedicationRequest',
            'status': 'active',
            'intent': 'order',
            'medicationCodeableConcept': {
                'text': drug_name
            },
            'subject': {
                'reference': f"Patient/{patient_id}"
            },
            'dosageInstruction': [{
                'doseAndRate': [{
                    'doseQuantity': {
                        'value': dose,
                        'unit': unit,
                        'system': 'http://unitsofmeasure.org'
                    }
                }]
            }],
            'authoredOn': datetime.utcnow().isoformat() + 'Z'
        }

    # ─── Condition Builder ─────────────────────────────────────
    @staticmethod
    def condition(code: str, display: str, severity: str = 'moderate',
                  patient_id: str = 'moiss-patient-001') -> Dict:
        """Create a FHIR Condition resource from an assess event."""
        severity_map = {
            'LOW': '255604002',
            'MODERATE': '6736007',
            'HIGH': '24484000',
        }
        return {
            'resourceType': 'Condition',
            'clinicalStatus': {
                'coding': [{'code': 'active'}]
            },
            'severity': {
                'coding': [{
                    'system': 'http://snomed.info/sct',
                    'code': severity_map.get(severity.upper(), '6736007'),
                    'display': severity.capitalize()
                }]
            },
            'code': {
                'coding': [{
                    'system': 'http://snomed.info/sct',
                    'code': code,
                    'display': display
                }]
            },
            'subject': {
                'reference': f"Patient/{patient_id}"
            },
            'recordedDate': datetime.utcnow().isoformat() + 'Z'
        }

    # ─── Utility ───────────────────────────────────────────────
    @staticmethod
    def to_json(resource: Dict, indent: int = 2) -> str:
        """Serialize a FHIR resource to JSON."""
        return json.dumps(resource, indent=indent, default=str)
