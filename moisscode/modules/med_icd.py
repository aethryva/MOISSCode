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

    # ─── v3.0 Expansion: Neurological ─────────────────
    "I63.9": ICDCode("I63.9", "Cerebral infarction, unspecified", "Cerebrovascular diseases", "IX", True,
                     ["I63.0", "I63.5", "Z86.73"], "432504007"),
    "G40.909": ICDCode("G40.909", "Epilepsy, unspecified, not intractable", "Epilepsy", "VI", True,
                       ["G40.919", "R56.9"], "84757009"),
    "G41.0": ICDCode("G41.0", "Grand mal status epilepticus", "Status epilepticus", "VI", True,
                     ["G40.909"], ""),
    "G30.9": ICDCode("G30.9", "Alzheimer disease, unspecified", "Dementia", "VI", True,
                     ["F03.90"], "26929004"),
    "G20": ICDCode("G20", "Parkinson disease", "Extrapyramidal disorders", "VI", True,
                   ["G21.9"], "49049000"),
    "G35": ICDCode("G35", "Multiple sclerosis", "Demyelinating diseases", "VI", True,
                   [], "24700007"),
    "G93.40": ICDCode("G93.40", "Encephalopathy, unspecified", "Brain disorders", "VI", True,
                      ["G93.41"], ""),

    # ─── v3.0: Psychiatric ───────────────────────
    "F32.9": ICDCode("F32.9", "Major depressive disorder, single episode, unspecified", "Mood disorders", "V", True,
                     ["F33.9", "F31.9"], "35489007"),
    "F41.9": ICDCode("F41.9", "Anxiety disorder, unspecified", "Anxiety disorders", "V", True,
                     ["F41.1", "F41.0"], "197480006"),
    "F10.20": ICDCode("F10.20", "Alcohol dependence, uncomplicated", "Substance use", "V", True,
                      ["F10.10", "F10.239"], ""),
    "F31.9": ICDCode("F31.9", "Bipolar disorder, unspecified", "Mood disorders", "V", True,
                     ["F32.9"], "13746004"),
    "F20.9": ICDCode("F20.9", "Schizophrenia, unspecified", "Psychotic disorders", "V", True,
                     ["F25.9"], "58214004"),
    "F03.90": ICDCode("F03.90", "Unspecified dementia without behavioral disturbance", "Dementia", "V", True,
                      ["G30.9"], ""),

    # ─── v3.0: Hematologic ──────────────────────
    "D64.9": ICDCode("D64.9", "Anemia, unspecified", "Anemias", "III", True,
                     ["D50.9", "D62"], "271737000"),
    "D50.9": ICDCode("D50.9", "Iron deficiency anemia, unspecified", "Nutritional anemia", "III", True,
                     ["D64.9"], "87522002"),
    "D65": ICDCode("D65", "Disseminated intravascular coagulation (DIC)", "Coagulation defects", "III", True,
                   ["D68.9"], "67406007"),
    "D69.6": ICDCode("D69.6", "Thrombocytopenia, unspecified", "Purpura/platelet disorders", "III", True,
                     ["D69.59"], "302215000"),
    "I26.99": ICDCode("I26.99", "Other pulmonary embolism without acute cor pulmonale", "Pulmonary embolism", "IX", True,
                      ["I26.90", "I82.90"], "59282003"),
    "I82.90": ICDCode("I82.90", "Acute embolism and thrombosis of unspecified vein", "DVT", "IX", True,
                      ["I26.99"], "128053003"),

    # ─── v3.0: Musculoskeletal ───────────────────
    "M79.3": ICDCode("M79.3", "Panniculitis, unspecified", "Soft tissue disorders", "XIII", True,
                     [], ""),
    "M86.9": ICDCode("M86.9", "Osteomyelitis, unspecified", "Osteomyelitis", "XIII", True,
                     [], "60168000"),
    "M54.5": ICDCode("M54.5", "Low back pain", "Dorsopathies", "XIII", True,
                     ["M54.41"], "279039007"),

    # ─── v3.0: Oncologic ────────────────────────
    "C34.90": ICDCode("C34.90", "Malignant neoplasm of unspecified part of bronchus or lung", "Lung cancer", "II", True,
                      ["C34.10", "C34.30"], "363358000"),
    "C50.919": ICDCode("C50.919", "Malignant neoplasm of unspecified site of breast", "Breast cancer", "II", True,
                       ["C50.911"], "254837009"),
    "C18.9": ICDCode("C18.9", "Malignant neoplasm of colon, unspecified", "Colorectal cancer", "II", True,
                     ["C18.0", "C20"], "363406005"),
    "C61": ICDCode("C61", "Malignant neoplasm of prostate", "Prostate cancer", "II", True,
                   [], "399068003"),
    "C91.00": ICDCode("C91.00", "Acute lymphoblastic leukemia not having achieved remission", "Leukemia", "II", True,
                      ["C91.10"], ""),
    "C92.00": ICDCode("C92.00", "Acute myeloblastic leukemia not having achieved remission", "Leukemia", "II", True,
                      ["C92.10"], ""),

    # ─── v3.0: Endocrine Extras ─────────────────
    "E87.1": ICDCode("E87.1", "Hypo-osmolality and hyponatremia", "Electrolyte disorders", "IV", True,
                     ["E87.0"], ""),
    "E87.5": ICDCode("E87.5", "Hyperkalemia", "Electrolyte disorders", "IV", True,
                     ["E87.6"], ""),
    "E87.6": ICDCode("E87.6", "Hypokalemia", "Electrolyte disorders", "IV", True,
                     ["E87.5"], ""),
    "E83.52": ICDCode("E83.52", "Hypercalcemia", "Mineral metabolism disorders", "IV", True,
                      ["E83.51"], ""),
    "E16.2": ICDCode("E16.2", "Hypoglycemia, unspecified", "Pancreatic disorders", "IV", True,
                     ["E10.649"], ""),
    "E05.90": ICDCode("E05.90", "Thyrotoxicosis, unspecified", "Thyroid disorders", "IV", True,
                      ["E05.00"], "34486009"),
    "E03.9": ICDCode("E03.9", "Hypothyroidism, unspecified", "Thyroid disorders", "IV", True,
                     ["E03.8"], "40930008"),

    # ─── v3.0: Injury / Poisoning ────────────────
    "T39.1X1A": ICDCode("T39.1X1A", "Poisoning by 4-Aminophenol derivatives (acetaminophen), accidental", "Poisoning", "XIX", True,
                        [], ""),
    "T50.901A": ICDCode("T50.901A", "Poisoning by unspecified drugs, accidental", "Poisoning", "XIX", True,
                        [], ""),
    "T40.2X1A": ICDCode("T40.2X1A", "Poisoning by other opioids, accidental (initial)", "Poisoning", "XIX", True,
                        [], ""),
    "T36.0X5A": ICDCode("T36.0X5A", "Adverse effect of penicillins", "Adverse effects", "XIX", True,
                        [], ""),

    # ─── v3.0: Obesity / Metabolic ────────────────
    "E66.01": ICDCode("E66.01", "Morbid (severe) obesity due to excess calories", "Overweight/Obesity", "IV", True,
                      ["E66.09"], ""),
    "E78.5": ICDCode("E78.5", "Dyslipidemia, unspecified", "Lipid metabolism", "IV", True,
                     ["E78.0", "E78.1"], "370992007"),

    # ─── v3.0: Dermatologic ──────────────────────
    "L03.90": ICDCode("L03.90", "Cellulitis, unspecified", "Skin infections", "XII", True,
                      ["L03.11"], "128045006"),
    "L89.90": ICDCode("L89.90", "Pressure ulcer of unspecified site, unspecified stage", "Pressure ulcers", "XII", True,
                      [], "399912005"),

    # ─── v3.0: Pregnancy/Obstetric ────────────────
    "O14.10": ICDCode("O14.10", "Severe pre-eclampsia, unspecified trimester", "Pre-eclampsia", "XV", True,
                      ["O14.00"], ""),
    "O72.0": ICDCode("O72.0", "Third-stage hemorrhage (postpartum)", "Obstetric hemorrhage", "XV", True,
                     ["O72.1"], ""),

    # ─── v3.0: Respiratory Extras ─────────────────
    "J44.1": ICDCode("J44.1", "COPD with acute exacerbation", "Chronic lower respiratory", "X", True,
                     ["J44.0", "J44.9"], "195951007"),
    "J45.50": ICDCode("J45.50", "Severe persistent asthma, uncomplicated", "Asthma", "X", True,
                      ["J45.40"], "195967001"),
    "J15.9": ICDCode("J15.9", "Unspecified bacterial pneumonia", "Pneumonia", "X", True,
                     ["J18.9", "J13"], ""),
    "J13": ICDCode("J13", "Pneumonia due to Streptococcus pneumoniae", "Pneumonia", "X", True,
                   ["J18.9"], ""),

    # ─── v3.0: Cardiac Extras ────────────────────
    "I42.9": ICDCode("I42.9", "Cardiomyopathy, unspecified", "Cardiomyopathy", "IX", True,
                     ["I42.0"], "85898001"),
    "I46.9": ICDCode("I46.9", "Cardiac arrest, cause unspecified", "Cardiac arrest", "IX", True,
                     ["I46.2"], "410429000"),
    "I33.0": ICDCode("I33.0", "Acute and subacute infective endocarditis", "Endocarditis", "IX", True,
                     ["I33.9"], "56819008"),
    "I40.9": ICDCode("I40.9", "Acute myocarditis, unspecified", "Myocarditis", "IX", True,
                     [], "36171008"),
    "I71.3": ICDCode("I71.3", "Abdominal aortic aneurysm, ruptured", "Aortic aneurysm", "IX", True,
                     ["I71.4"], "12273009"),

    # ─── v3.0: GI Extras ────────────────────────
    "K85.9": ICDCode("K85.9", "Acute pancreatitis, unspecified", "Pancreatic diseases", "XI", True,
                     ["K85.0", "K85.1"], "197456007"),
    "K70.30": ICDCode("K70.30", "Alcoholic cirrhosis of liver without ascites", "Liver diseases", "XI", True,
                      ["K74.60", "K70.31"], ""),
    "K76.0": ICDCode("K76.0", "Fatty (change of) liver, not elsewhere classified", "Liver diseases", "XI", True,
                     ["K76.1"], "197321007"),
    "K25.9": ICDCode("K25.9", "Gastric ulcer, unspecified", "Peptic ulcer", "XI", True,
                     ["K25.0", "K26.9"], "397825006"),
    "A04.72": ICDCode("A04.72", "Enterocolitis due to C. difficile, not specified as recurrent", "C. diff", "I", True,
                      ["A04.71"], ""),

    # ─── v3.0: Renal Extras ──────────────────────
    "N39.0": ICDCode("N39.0", "Urinary tract infection, site not specified", "Urinary disorders", "XIV", True,
                     ["N10", "N30.00"], "68566005"),
    "N10": ICDCode("N10", "Acute pyelonephritis", "Kidney infections", "XIV", True,
                   ["N39.0", "N17.9"], "36689008"),
    "N18.3": ICDCode("N18.3", "Chronic kidney disease, stage 3", "CKD", "XIV", True,
                     ["N18.4", "N18.5"], ""),

    # ─── v3.0: Infectious Extras ──────────────────
    "A41.02": ICDCode("A41.02", "Sepsis due to Methicillin resistant Staphylococcus aureus", "Septicemia", "I", True,
                      ["A41.01", "B95.62"], ""),
    "B37.7": ICDCode("B37.7", "Candidal sepsis", "Mycoses", "I", True,
                     ["A41.9", "B37.1"], ""),
    "A15.0": ICDCode("A15.0", "Tuberculosis of lung", "Tuberculosis", "I", True,
                     ["A15.9"], "154283005"),
    "B20": ICDCode("B20", "Human immunodeficiency virus (HIV) disease", "HIV", "I", True,
                   [], "86406008"),
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

    # ─── v3.0 Expansion DRGs ──────────────────
    "064": {"name": "Intracranial hemorrhage or cerebral infarction w MCC", "weight": 1.82,
            "codes": ["I63.9"]},
    "065": {"name": "Intracranial hemorrhage or cerebral infarction w CC", "weight": 1.12,
            "codes": ["I63.9"]},
    "175": {"name": "Pulmonary embolism w MCC", "weight": 1.48,
            "codes": ["I26.99"]},
    "190": {"name": "COPD w MCC", "weight": 1.17,
            "codes": ["J44.1"]},
    "329": {"name": "Major small and large bowel procedures w MCC", "weight": 4.18,
            "codes": ["K25.9", "K85.9"]},
    "374": {"name": "Digestive malignancy w MCC", "weight": 1.67,
            "codes": ["C18.9"]},
    "640": {"name": "Nutritional and miscellaneous metabolic disorders w MCC", "weight": 0.94,
            "codes": ["E87.1", "E87.5"]},
    "689": {"name": "Kidney and urinary tract infections w MCC", "weight": 0.99,
            "codes": ["N39.0", "N10"]},
    "808": {"name": "Major hematologic/immunologic diagnoses w MCC", "weight": 2.25,
            "codes": ["D65", "D64.9"]},
    "811": {"name": "Red blood cell disorders w MCC", "weight": 1.11,
            "codes": ["D50.9", "D64.9"]},
    "853": {"name": "Infectious and parasitic diseases w MCC", "weight": 1.78,
            "codes": ["A15.0", "B20"]},
    "917": {"name": "Poisoning and toxic effects of drugs w MCC", "weight": 1.20,
            "codes": ["T39.1X1A", "T40.2X1A"]},
    "003": {"name": "ECMO or tracheostomy w MV >96 hrs", "weight": 18.86,
            "codes": ["J96.00", "J80"]},
    "308": {"name": "Cardiac arrhythmia and conduction disorders w MCC", "weight": 1.00,
            "codes": ["I48.91", "I46.9"]},
    "849": {"name": "Radiotherapy", "weight": 0.82,
            "codes": ["Z51.11"]},
    "765": {"name": "Cesarean section w CC/MCC", "weight": 1.32,
            "codes": ["O14.10", "O72.0"]},
    "837": {"name": "Chemo w acute leukemia as secondary diagnosis", "weight": 4.23,
            "codes": ["C91.00", "C92.00"]},
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
