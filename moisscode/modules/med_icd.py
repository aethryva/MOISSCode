"""
med.icd - Medical Coding Module for MOISSCode
ICD-10-CM code lookup, search, categorization, DRG grouping, and SNOMED CT mapping.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ICDCode:
    """ICD-10-CM diagnosis code entry."""
    code: str
    description: str
    category: str        # Chapter/category description
    chapter: str         # ICD-10 chapter (e.g., "I" for Infectious)
    is_billable: bool
    related: List[str]   # Related codes
    snomed: str = ""     # SNOMED CT concept ID if mapped


# ── ICD-10 Database (Common Clinical Codes) ────────────

ICD10_DATABASE: Dict[str, ICDCode] = {
    # Sepsis/Infectious
    "A41.9": ICDCode("A41.9", "Sepsis, unspecified organism", "Septicemia", "I", True,
                     ["A41.0", "A41.1", "R65.20"], "91302008"),
    "A41.01": ICDCode("A41.01", "Sepsis due to Methicillin susceptible Staphylococcus aureus", "Septicemia", "I", True,
                      ["A41.02", "A41.9"], ""),
    "A49.02": ICDCode("A49.02", "Methicillin resistant Staphylococcus aureus (MRSA), unspecified", "Bacterial infection", "I", True,
                      ["A41.02", "B95.62"], ""),
    "B95.62": ICDCode("B95.62", "MRSA as cause of disease classified elsewhere", "Bacterial agents", "I", True,
                      ["A49.02"], ""),

    # Diabetes
    "E11.9": ICDCode("E11.9", "Type 2 diabetes mellitus without complications", "Diabetes mellitus", "IV", True,
                     ["E11.65", "E11.21", "E13.9"], "44054006"),
    "E11.65": ICDCode("E11.65", "Type 2 DM with hyperglycemia", "Diabetes mellitus", "IV", True,
                      ["E11.9", "E11.10"], ""),
    "E10.10": ICDCode("E10.10", "Type 1 DM with ketoacidosis without coma", "Diabetes mellitus", "IV", True,
                      ["E10.11", "E10.9"], ""),
    "E10.11": ICDCode("E10.11", "Type 1 DM with ketoacidosis with coma", "Diabetes mellitus", "IV", True,
                      ["E10.10"], ""),
    "E13.9": ICDCode("E13.9", "Other specified DM without complications", "Diabetes mellitus", "IV", True,
                     ["E11.9"], ""),

    # Cardiovascular
    "I10": ICDCode("I10", "Essential (primary) hypertension", "Hypertensive diseases", "IX", True,
                   ["I11.9", "I12.9"], "59621000"),
    "I21.9": ICDCode("I21.9", "Acute myocardial infarction, unspecified", "Ischemic heart diseases", "IX", True,
                     ["I21.0", "I21.3", "I25.10"], "22298006"),
    "I25.10": ICDCode("I25.10", "Atherosclerotic heart disease of native coronary artery", "Chronic ischemic heart disease", "IX", True,
                      ["I25.11", "I21.9"], ""),
    "I48.91": ICDCode("I48.91", "Unspecified atrial fibrillation", "Other cardiac arrhythmias", "IX", True,
                      ["I48.0", "I48.1", "I48.2"], "49436004"),
    "I50.9": ICDCode("I50.9", "Heart failure, unspecified", "Heart failure", "IX", True,
                     ["I50.20", "I50.30", "I50.40"], "84114007"),

    # Respiratory
    "J18.9": ICDCode("J18.9", "Pneumonia, unspecified organism", "Pneumonia", "X", True,
                     ["J15.9", "J13", "J12.9"], "233604007"),
    "J96.00": ICDCode("J96.00", "Acute respiratory failure, unspecified", "Respiratory failure", "X", True,
                      ["J96.01", "J96.02", "J80"], ""),
    "J80": ICDCode("J80", "Acute respiratory distress syndrome (ARDS)", "Other respiratory diseases", "X", True,
                   ["J96.00", "J96.01"], "67782005"),

    # Renal
    "N17.9": ICDCode("N17.9", "Acute kidney failure, unspecified", "Kidney failure", "XIV", True,
                     ["N17.0", "N17.1", "N18.6"], "14669001"),
    "N18.6": ICDCode("N18.6", "End stage renal disease", "Chronic kidney disease", "XIV", True,
                     ["N18.5", "N17.9"], "46177005"),

    # GI/Hepatic
    "K74.60": ICDCode("K74.60", "Unspecified cirrhosis of liver", "Liver diseases", "XI", True,
                      ["K70.30", "K76.0"], "19943007"),
    "K92.0": ICDCode("K92.0", "Hematemesis (vomiting blood)", "GI hemorrhage", "XI", True,
                     ["K92.1", "K92.2"], ""),
    "K92.1": ICDCode("K92.1", "Melena (black tarry stool)", "GI hemorrhage", "XI", True,
                     ["K92.0", "K92.2"], ""),

    # Critical Care / Symptoms
    "R65.20": ICDCode("R65.20", "Severe sepsis without septic shock", "SIRS/Sepsis", "XVIII", True,
                      ["R65.21", "A41.9"], ""),
    "R65.21": ICDCode("R65.21", "Severe sepsis with septic shock", "SIRS/Sepsis", "XVIII", True,
                      ["R65.20", "A41.9"], "76571007"),
    "R57.1": ICDCode("R57.1", "Hypovolemic shock", "Shock", "XVIII", True,
                     ["R57.0", "R57.8"], ""),
    "R50.9": ICDCode("R50.9", "Fever, unspecified", "General symptoms", "XVIII", True,
                     ["R50.81", "A41.9"], "386661006"),

    # Procedures (Z-codes)
    "Z51.11": ICDCode("Z51.11", "Encounter for antineoplastic chemotherapy", "Encounters for procedures", "XXI", True,
                      ["Z51.12"], ""),
    "Z86.73": ICDCode("Z86.73", "Personal history of TIA and cerebral infarction", "Health status", "XXI", True,
                      ["I63.9"], ""),
}

# ── DRG Groupings ──────────────────────────────────────

DRG_GROUPS = {
    "870": {"name": "Septicemia or severe sepsis w MV >96 hours", "weight": 5.44,
            "codes": ["A41.9", "R65.20", "R65.21"]},
    "871": {"name": "Septicemia or severe sepsis w/o MV >96 hours w MCC", "weight": 1.88,
            "codes": ["A41.9", "R65.20"]},
    "291": {"name": "Heart failure and shock w MCC", "weight": 1.40,
            "codes": ["I50.9", "R57.1"]},
    "193": {"name": "Pneumonia w MCC", "weight": 1.17,
            "codes": ["J18.9", "J15.9"]},
    "682": {"name": "Renal failure w MCC", "weight": 1.26,
            "codes": ["N17.9", "N18.6"]},
    "637": {"name": "Diabetes w MCC", "weight": 1.20,
            "codes": ["E11.9", "E11.65", "E10.10"]},
    "280": {"name": "Acute myocardial infarction", "weight": 1.44,
            "codes": ["I21.9"]},
    "441": {"name": "Liver disorders w MCC", "weight": 1.93,
            "codes": ["K74.60"]},
}


class ICDEngine:
    """ICD-10-CM coding engine for MOISSCode."""

    def __init__(self):
        self.codes = dict(ICD10_DATABASE)

    def lookup(self, code: str) -> dict:
        """Look up an ICD-10-CM code and return its description."""
        code = code.upper().strip()
        entry = self.codes.get(code)

        if not entry:
            return {
                'type': 'ICD',
                'code': code,
                'error': f'Code "{code}" not found'
            }

        return {
            'type': 'ICD_LOOKUP',
            'code': entry.code,
            'description': entry.description,
            'category': entry.category,
            'chapter': entry.chapter,
            'is_billable': entry.is_billable,
            'related_codes': entry.related,
            'snomed_ct': entry.snomed if entry.snomed else None
        }

    def search(self, term: str) -> dict:
        """Search ICD-10 codes by keyword in description."""
        term_lower = term.lower()
        matches = []

        for code, entry in self.codes.items():
            if (term_lower in entry.description.lower() or
                term_lower in entry.category.lower()):
                matches.append({
                    'code': entry.code,
                    'description': entry.description,
                    'category': entry.category,
                    'billable': entry.is_billable
                })

        return {
            'type': 'ICD_SEARCH',
            'query': term,
            'results': matches,
            'count': len(matches)
        }

    def category(self, code: str) -> dict:
        """Get the category and chapter for a code."""
        code = code.upper().strip()
        entry = self.codes.get(code)

        if not entry:
            return {'type': 'ICD', 'error': f'Code "{code}" not found'}

        return {
            'type': 'ICD_CATEGORY',
            'code': code,
            'category': entry.category,
            'chapter': entry.chapter
        }

    def related(self, code: str) -> dict:
        """Find related ICD-10 codes."""
        code = code.upper().strip()
        entry = self.codes.get(code)

        if not entry:
            return {'type': 'ICD', 'error': f'Code "{code}" not found'}

        related_details = []
        for rel_code in entry.related:
            rel_entry = self.codes.get(rel_code)
            if rel_entry:
                related_details.append({
                    'code': rel_entry.code,
                    'description': rel_entry.description
                })
            else:
                related_details.append({'code': rel_code, 'description': 'Not in database'})

        return {
            'type': 'ICD_RELATED',
            'code': code,
            'description': entry.description,
            'related': related_details
        }

    def drg_lookup(self, diagnosis_codes: list) -> dict:
        """
        Find potential DRG grouping from a list of diagnosis codes.
        Returns matching DRG with highest weight.
        """
        matches = []

        for drg_code, drg_info in DRG_GROUPS.items():
            overlap = [c for c in diagnosis_codes if c in drg_info['codes']]
            if overlap:
                matches.append({
                    'drg': drg_code,
                    'name': drg_info['name'],
                    'weight': drg_info['weight'],
                    'matching_codes': overlap
                })

        # Sort by weight (highest first)
        matches.sort(key=lambda x: x['weight'], reverse=True)

        return {
            'type': 'ICD_DRG',
            'input_codes': diagnosis_codes,
            'matches': matches,
            'primary_drg': matches[0] if matches else None
        }

    def snomed_to_icd(self, snomed_code: str) -> dict:
        """Map a SNOMED CT concept ID to ICD-10-CM codes."""
        snomed_code = str(snomed_code).strip()
        matches = []

        for code, entry in self.codes.items():
            if entry.snomed == snomed_code:
                matches.append({
                    'code': entry.code,
                    'description': entry.description
                })

        return {
            'type': 'ICD_SNOMED_MAP',
            'snomed_ct': snomed_code,
            'icd10_matches': matches,
            'count': len(matches)
        }

    def validate_codes(self, codes: list) -> dict:
        """Validate a list of ICD-10 codes. Returns valid/invalid status for each."""
        results = []
        valid_count = 0

        for code in codes:
            code_upper = code.upper().strip()
            entry = self.codes.get(code_upper)
            if entry:
                results.append({
                    'code': code_upper,
                    'valid': True,
                    'billable': entry.is_billable,
                    'description': entry.description
                })
                valid_count += 1
            else:
                results.append({
                    'code': code_upper,
                    'valid': False,
                    'billable': False,
                    'description': 'Not found'
                })

        return {
            'type': 'ICD_VALIDATE',
            'total': len(codes),
            'valid': valid_count,
            'invalid': len(codes) - valid_count,
            'results': results
        }

    def list_codes(self, chapter: str = None) -> list:
        """List all codes, optionally filtered by chapter."""
        results = []
        for code, entry in self.codes.items():
            if chapter and entry.chapter != chapter:
                continue
            results.append({
                'code': entry.code,
                'description': entry.description,
                'chapter': entry.chapter
            })
        return results
