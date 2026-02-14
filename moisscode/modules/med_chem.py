"""
med.chem - Medicinal Chemistry Module for MOISSCode
Molecular property calculations, drug-likeness screening, ADMET prediction,
and compound database for drug discovery/screening workflows.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import math
import re


@dataclass
class Compound:
    """Chemical compound profile for drug screening."""
    name: str
    formula: str
    molecular_weight: float
    logp: float              # Octanol-water partition coefficient
    hbd: int                 # Hydrogen bond donors
    hba: int                 # Hydrogen bond acceptors
    psa: float               # Polar surface area (Angstrom^2)
    rotatable_bonds: int
    category: str = ""       # e.g. "antibiotic", "analgesic"
    solubility: str = ""     # "high", "moderate", "low"
    permeability: str = ""   # "high", "moderate", "low"
    known_targets: List[str] = field(default_factory=list)
    therapeutic_class: str = ""
    max_daily_dose_mg: float = 0.0
    ld50_mg_kg: float = 0.0  # Oral LD50 in rat (mg/kg)


# ── Built-in Compound Database ─────────────────────────

COMPOUND_DATABASE: Dict[str, Compound] = {
    "aspirin": Compound(
        name="Aspirin", formula="C9H8O4", molecular_weight=180.16,
        logp=1.2, hbd=1, hba=4, psa=63.6, rotatable_bonds=3,
        category="NSAID", solubility="moderate", permeability="high",
        known_targets=["COX-1", "COX-2"], therapeutic_class="analgesic",
        max_daily_dose_mg=4000, ld50_mg_kg=200
    ),
    "metformin": Compound(
        name="Metformin", formula="C4H11N5", molecular_weight=129.16,
        logp=-1.4, hbd=2, hba=5, psa=91.5, rotatable_bonds=2,
        category="biguanide", solubility="high", permeability="low",
        known_targets=["AMPK", "Complex-I"], therapeutic_class="antidiabetic",
        max_daily_dose_mg=2550, ld50_mg_kg=1000
    ),
    "atorvastatin": Compound(
        name="Atorvastatin", formula="C33H35FN2O5", molecular_weight=558.64,
        logp=4.46, hbd=4, hba=5, psa=111.8, rotatable_bonds=12,
        category="statin", solubility="low", permeability="high",
        known_targets=["HMG-CoA reductase"], therapeutic_class="lipid-lowering",
        max_daily_dose_mg=80, ld50_mg_kg=5000
    ),
    "amoxicillin": Compound(
        name="Amoxicillin", formula="C16H19N3O5S", molecular_weight=365.40,
        logp=0.87, hbd=4, hba=7, psa=158.3, rotatable_bonds=4,
        category="beta-lactam", solubility="moderate", permeability="moderate",
        known_targets=["PBP"], therapeutic_class="antibiotic",
        max_daily_dose_mg=3000, ld50_mg_kg=3000
    ),
    "ibuprofen": Compound(
        name="Ibuprofen", formula="C13H18O2", molecular_weight=206.28,
        logp=3.97, hbd=1, hba=2, psa=37.3, rotatable_bonds=4,
        category="NSAID", solubility="moderate", permeability="high",
        known_targets=["COX-1", "COX-2"], therapeutic_class="analgesic",
        max_daily_dose_mg=3200, ld50_mg_kg=636
    ),
    "lisinopril": Compound(
        name="Lisinopril", formula="C21H31N3O5", molecular_weight=405.49,
        logp=-0.86, hbd=4, hba=7, psa=132.6, rotatable_bonds=11,
        category="ACE inhibitor", solubility="high", permeability="low",
        known_targets=["ACE"], therapeutic_class="antihypertensive",
        max_daily_dose_mg=80, ld50_mg_kg=2000
    ),
    "omeprazole": Compound(
        name="Omeprazole", formula="C17H19N3O3S", molecular_weight=345.42,
        logp=2.23, hbd=1, hba=5, psa=77.1, rotatable_bonds=5,
        category="PPI", solubility="low", permeability="high",
        known_targets=["H+/K+-ATPase"], therapeutic_class="antiulcer",
        max_daily_dose_mg=40, ld50_mg_kg=4000
    ),
    "dexamethasone": Compound(
        name="Dexamethasone", formula="C22H29FO5", molecular_weight=392.46,
        logp=1.83, hbd=3, hba=5, psa=94.8, rotatable_bonds=2,
        category="corticosteroid", solubility="moderate", permeability="high",
        known_targets=["GR"], therapeutic_class="anti-inflammatory",
        max_daily_dose_mg=20, ld50_mg_kg=54
    ),
    "warfarin": Compound(
        name="Warfarin", formula="C19H16O4", molecular_weight=308.33,
        logp=2.7, hbd=1, hba=4, psa=67.5, rotatable_bonds=4,
        category="coumarin", solubility="moderate", permeability="high",
        known_targets=["VKORC1"], therapeutic_class="anticoagulant",
        max_daily_dose_mg=10, ld50_mg_kg=186
    ),
    "ciprofloxacin": Compound(
        name="Ciprofloxacin", formula="C17H18FN3O3", molecular_weight=331.34,
        logp=-0.57, hbd=2, hba=6, psa=72.9, rotatable_bonds=3,
        category="fluoroquinolone", solubility="moderate", permeability="high",
        known_targets=["DNA gyrase", "Topoisomerase IV"],
        therapeutic_class="antibiotic",
        max_daily_dose_mg=1500, ld50_mg_kg=5000
    ),
    "morphine": Compound(
        name="Morphine", formula="C17H19NO3", molecular_weight=285.34,
        logp=0.89, hbd=2, hba=4, psa=52.9, rotatable_bonds=0,
        category="opioid", solubility="moderate", permeability="high",
        known_targets=["mu-opioid receptor"], therapeutic_class="analgesic",
        max_daily_dose_mg=200, ld50_mg_kg=335
    ),
    "insulin_glargine": Compound(
        name="Insulin Glargine", formula="C267H404N72O78S6",
        molecular_weight=6063.0, logp=-2.0, hbd=50, hba=80,
        psa=2500, rotatable_bonds=60,
        category="insulin analog", solubility="low", permeability="low",
        known_targets=["Insulin receptor"], therapeutic_class="antidiabetic",
        max_daily_dose_mg=100, ld50_mg_kg=0
    ),

    # ─── v3.0 Expansion ──────────────────────────────────
    "vancomycin": Compound(
        name="Vancomycin", formula="C66H75Cl2N9O24", molecular_weight=1449.25,
        logp=-3.1, hbd=19, hba=31, psa=530.5, rotatable_bonds=7,
        category="glycopeptide", solubility="high", permeability="low",
        known_targets=["D-Ala-D-Ala terminus"], therapeutic_class="antibiotic",
        max_daily_dose_mg=4000, ld50_mg_kg=5000
    ),
    "meropenem": Compound(
        name="Meropenem", formula="C17H25N3O5S", molecular_weight=383.46,
        logp=-0.6, hbd=2, hba=7, psa=109.0, rotatable_bonds=5,
        category="carbapenem", solubility="high", permeability="high",
        known_targets=["PBP2", "PBP3"], therapeutic_class="antibiotic",
        max_daily_dose_mg=6000, ld50_mg_kg=2000
    ),
    "fluconazole": Compound(
        name="Fluconazole", formula="C13H12F2N6O", molecular_weight=306.27,
        logp=0.4, hbd=1, hba=7, psa=81.7, rotatable_bonds=5,
        category="triazole", solubility="high", permeability="high",
        known_targets=["14-alpha demethylase"], therapeutic_class="antifungal",
        max_daily_dose_mg=400, ld50_mg_kg=1000
    ),
    "remdesivir": Compound(
        name="Remdesivir", formula="C27H35N6O8P", molecular_weight=602.58,
        logp=1.9, hbd=3, hba=12, psa=213.4, rotatable_bonds=14,
        category="nucleotide analog", solubility="low", permeability="moderate",
        known_targets=["RdRp (RNA-dependent RNA polymerase)"], therapeutic_class="antiviral",
        max_daily_dose_mg=200, ld50_mg_kg=0
    ),
    "tacrolimus": Compound(
        name="Tacrolimus", formula="C44H69NO12", molecular_weight=804.02,
        logp=3.3, hbd=3, hba=12, psa=178.4, rotatable_bonds=7,
        category="macrolide", solubility="low", permeability="high",
        known_targets=["FKBP12", "Calcineurin"], therapeutic_class="immunosuppressant",
        max_daily_dose_mg=20, ld50_mg_kg=134
    ),
    "cyclosporine": Compound(
        name="Cyclosporine", formula="C62H111N11O12", molecular_weight=1202.61,
        logp=2.9, hbd=5, hba=12, psa=279.0, rotatable_bonds=15,
        category="cyclic peptide", solubility="low", permeability="high",
        known_targets=["Cyclophilin", "Calcineurin"], therapeutic_class="immunosuppressant",
        max_daily_dose_mg=500, ld50_mg_kg=2329
    ),
    "lisinopril": Compound(
        name="Lisinopril", formula="C21H31N3O5", molecular_weight=405.49,
        logp=-1.22, hbd=4, hba=7, psa=132.7, rotatable_bonds=12,
        category="ACE inhibitor", solubility="high", permeability="low",
        known_targets=["ACE"], therapeutic_class="antihypertensive",
        max_daily_dose_mg=80, ld50_mg_kg=2000
    ),
    "losartan": Compound(
        name="Losartan", formula="C22H23ClN6O", molecular_weight=422.91,
        logp=4.01, hbd=2, hba=5, psa=92.5, rotatable_bonds=8,
        category="ARB", solubility="moderate", permeability="high",
        known_targets=["AT1 receptor"], therapeutic_class="antihypertensive",
        max_daily_dose_mg=100, ld50_mg_kg=1000
    ),
    "amlodipine": Compound(
        name="Amlodipine", formula="C20H25ClN2O5", molecular_weight=408.88,
        logp=3.0, hbd=2, hba=6, psa=100.0, rotatable_bonds=10,
        category="dihydropyridine", solubility="moderate", permeability="high",
        known_targets=["L-type Ca2+ channel"], therapeutic_class="antihypertensive",
        max_daily_dose_mg=10, ld50_mg_kg=0
    ),
    "atorvastatin": Compound(
        name="Atorvastatin", formula="C33H35FN2O5", molecular_weight=558.64,
        logp=6.36, hbd=4, hba=5, psa=111.8, rotatable_bonds=12,
        category="statin", solubility="low", permeability="high",
        known_targets=["HMG-CoA reductase"], therapeutic_class="lipid-lowering",
        max_daily_dose_mg=80, ld50_mg_kg=0
    ),
    "furosemide": Compound(
        name="Furosemide", formula="C12H11ClN2O5S", molecular_weight=330.74,
        logp=2.03, hbd=3, hba=7, psa=122.6, rotatable_bonds=5,
        category="sulfonamide loop diuretic", solubility="moderate", permeability="moderate",
        known_targets=["NKCC2 transporter"], therapeutic_class="diuretic",
        max_daily_dose_mg=600, ld50_mg_kg=2600
    ),
    "methotrexate": Compound(
        name="Methotrexate", formula="C20H22N8O5", molecular_weight=454.44,
        logp=-1.85, hbd=5, hba=12, psa=210.5, rotatable_bonds=10,
        category="antimetabolite", solubility="moderate", permeability="low",
        known_targets=["Dihydrofolate reductase"], therapeutic_class="antineoplastic",
        max_daily_dose_mg=25, ld50_mg_kg=135
    ),
    "imatinib": Compound(
        name="Imatinib", formula="C29H31N7O", molecular_weight=493.60,
        logp=3.5, hbd=2, hba=7, psa=86.3, rotatable_bonds=7,
        category="tyrosine kinase inhibitor", solubility="moderate", permeability="high",
        known_targets=["BCR-ABL", "c-KIT", "PDGFR"], therapeutic_class="antineoplastic",
        max_daily_dose_mg=800, ld50_mg_kg=0
    ),
    "doxorubicin": Compound(
        name="Doxorubicin", formula="C27H29NO11", molecular_weight=543.52,
        logp=1.27, hbd=6, hba=12, psa=206.1, rotatable_bonds=5,
        category="anthracycline", solubility="moderate", permeability="low",
        known_targets=["Topoisomerase II", "DNA intercalation"], therapeutic_class="antineoplastic",
        max_daily_dose_mg=75, ld50_mg_kg=25
    ),
    "lithium_carbonate": Compound(
        name="Lithium Carbonate", formula="Li2CO3", molecular_weight=73.89,
        logp=-2.0, hbd=0, hba=3, psa=63.2, rotatable_bonds=0,
        category="alkali metal salt", solubility="high", permeability="high",
        known_targets=["GSK-3β", "IMPase"], therapeutic_class="mood stabilizer",
        max_daily_dose_mg=1800, ld50_mg_kg=531
    ),
    "valproic_acid": Compound(
        name="Valproic Acid", formula="C8H16O2", molecular_weight=144.21,
        logp=2.78, hbd=1, hba=2, psa=37.3, rotatable_bonds=5,
        category="branched chain fatty acid", solubility="moderate", permeability="high",
        known_targets=["GABA transaminase", "Voltage-gated Na+ channels", "HDAC"], therapeutic_class="anticonvulsant",
        max_daily_dose_mg=3000, ld50_mg_kg=670
    ),
    "fluoxetine": Compound(
        name="Fluoxetine", formula="C17H18F3NO", molecular_weight=309.33,
        logp=4.05, hbd=1, hba=2, psa=21.3, rotatable_bonds=6,
        category="SSRI", solubility="moderate", permeability="high",
        known_targets=["SERT (serotonin transporter)"], therapeutic_class="antidepressant",
        max_daily_dose_mg=80, ld50_mg_kg=452
    ),
    "levetiracetam": Compound(
        name="Levetiracetam", formula="C8H14N2O2", molecular_weight=170.21,
        logp=-0.64, hbd=1, hba=3, psa=63.4, rotatable_bonds=3,
        category="pyrrolidone", solubility="high", permeability="high",
        known_targets=["SV2A"], therapeutic_class="anticonvulsant",
        max_daily_dose_mg=3000, ld50_mg_kg=0
    ),
    "albuterol": Compound(
        name="Albuterol", formula="C13H21NO3", molecular_weight=239.31,
        logp=0.64, hbd=4, hba=4, psa=72.7, rotatable_bonds=4,
        category="phenethylamine", solubility="high", permeability="high",
        known_targets=["β2-adrenergic receptor"], therapeutic_class="bronchodilator",
        max_daily_dose_mg=32, ld50_mg_kg=0
    ),
    "ipratropium": Compound(
        name="Ipratropium", formula="C20H30NO3", molecular_weight=332.46,
        logp=-0.8, hbd=1, hba=4, psa=46.5, rotatable_bonds=5,
        category="tropane alkaloid", solubility="high", permeability="low",
        known_targets=["M1-M3 muscarinic receptors"], therapeutic_class="bronchodilator",
        max_daily_dose_mg=2, ld50_mg_kg=0
    ),
    "empagliflozin": Compound(
        name="Empagliflozin", formula="C23H27ClO7", molecular_weight=450.91,
        logp=1.6, hbd=4, hba=6, psa=108.0, rotatable_bonds=6,
        category="glucoside", solubility="moderate", permeability="high",
        known_targets=["SGLT2"], therapeutic_class="antidiabetic",
        max_daily_dose_mg=25, ld50_mg_kg=0
    ),
    "clopidogrel": Compound(
        name="Clopidogrel", formula="C16H16ClNO2S", molecular_weight=321.82,
        logp=3.37, hbd=0, hba=3, psa=56.6, rotatable_bonds=5,
        category="thienopyridine", solubility="low", permeability="high",
        known_targets=["P2Y12 ADP receptor (active metabolite)"], therapeutic_class="antiplatelet",
        max_daily_dose_mg=75, ld50_mg_kg=0
    ),
    "apixaban": Compound(
        name="Apixaban", formula="C25H25N5O4", molecular_weight=459.50,
        logp=1.88, hbd=1, hba=7, psa=110.8, rotatable_bonds=5,
        category="pyrazole", solubility="low", permeability="high",
        known_targets=["Factor Xa"], therapeutic_class="anticoagulant",
        max_daily_dose_mg=10, ld50_mg_kg=0
    ),
    "heparin_lmwh": Compound(
        name="Enoxaparin (LMWH)", formula="C26H42N2O37S5",
        molecular_weight=4500.0, logp=-4.0, hbd=20, hba=40,
        psa=800, rotatable_bonds=30,
        category="glycosaminoglycan", solubility="high", permeability="low",
        known_targets=["Antithrombin III", "Factor Xa"], therapeutic_class="anticoagulant",
        max_daily_dose_mg=300, ld50_mg_kg=0
    ),
    "naloxone": Compound(
        name="Naloxone", formula="C19H21NO4", molecular_weight=327.37,
        logp=2.09, hbd=2, hba=5, psa=70.0, rotatable_bonds=2,
        category="morphinan", solubility="moderate", permeability="high",
        known_targets=["mu-opioid receptor (antagonist)"], therapeutic_class="opioid antagonist",
        max_daily_dose_mg=10, ld50_mg_kg=150
    ),
    "epinephrine": Compound(
        name="Epinephrine", formula="C9H13NO3", molecular_weight=183.21,
        logp=-1.37, hbd=4, hba=4, psa=72.7, rotatable_bonds=2,
        category="catecholamine", solubility="high", permeability="low",
        known_targets=["α1", "α2", "β1", "β2 adrenergic receptors"], therapeutic_class="vasopressor",
        max_daily_dose_mg=10, ld50_mg_kg=30
    ),
    "adenosine_compound": Compound(
        name="Adenosine", formula="C10H13N5O4", molecular_weight=267.24,
        logp=-1.05, hbd=4, hba=8, psa=139.5, rotatable_bonds=2,
        category="purine nucleoside", solubility="high", permeability="moderate",
        known_targets=["A1 receptor", "AV node"], therapeutic_class="antiarrhythmic",
        max_daily_dose_mg=12, ld50_mg_kg=0
    ),
    "oseltamivir": Compound(
        name="Oseltamivir", formula="C16H28N2O4", molecular_weight=312.40,
        logp=1.0, hbd=2, hba=5, psa=90.7, rotatable_bonds=8,
        category="neuraminidase inhibitor", solubility="high", permeability="high",
        known_targets=["Neuraminidase (influenza)"], therapeutic_class="antiviral",
        max_daily_dose_mg=150, ld50_mg_kg=0
    ),
}



# ── Atomic Weights ─────────────────────────────────────

ATOMIC_WEIGHTS = {
    'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012,
    'B': 10.81, 'C': 12.011, 'N': 14.007, 'O': 15.999,
    'F': 18.998, 'Ne': 20.180, 'Na': 22.990, 'Mg': 24.305,
    'Al': 26.982, 'Si': 28.086, 'P': 30.974, 'S': 32.065,
    'Cl': 35.453, 'Ar': 39.948, 'K': 39.098, 'Ca': 40.078,
    'Fe': 55.845, 'Co': 58.933, 'Cu': 63.546, 'Zn': 65.38,
    'Br': 79.904, 'I': 126.90, 'Pt': 195.08,
}


class ChemEngine:
    """Medicinal chemistry engine for MOISSCode."""

    def __init__(self):
        self.compounds = dict(COMPOUND_DATABASE)

    # ── Molecular Weight ───────────────────────────────────

    @staticmethod
    def molecular_weight(formula: str) -> dict:
        """
        Calculate molecular weight from a chemical formula.
        Supports formulas like C9H8O4, C16H19N3O5S, etc.
        """
        pattern = re.findall(r'([A-Z][a-z]?)(\d*)', formula)
        mw = 0.0
        composition = {}

        for element, count in pattern:
            if element == '':
                continue
            n = int(count) if count else 1
            weight = ATOMIC_WEIGHTS.get(element, 0)
            if weight == 0:
                return {'type': 'CHEM', 'error': f'Unknown element: {element}'}
            mw += weight * n
            composition[element] = n

        return {
            'type': 'CHEM_MW',
            'formula': formula,
            'molecular_weight': round(mw, 2),
            'composition': composition
        }

    # ── Lipinski's Rule of Five ────────────────────────────

    @staticmethod
    def lipinski_check(mw: float, logp: float, hbd: int, hba: int) -> dict:
        """
        Lipinski's Rule of Five - drug-likeness screening.
        A compound is "drug-like" if it violates at most 1 rule.
        Rules: MW <= 500, LogP <= 5, HBD <= 5, HBA <= 10.
        """
        mw = float(mw)
        logp = float(logp)
        hbd = int(hbd)
        hba = int(hba)

        violations = []
        if mw > 500: violations.append(f"MW {mw} > 500")
        if logp > 5: violations.append(f"LogP {logp} > 5")
        if hbd > 5: violations.append(f"HBD {hbd} > 5")
        if hba > 10: violations.append(f"HBA {hba} > 10")

        drug_like = len(violations) <= 1

        return {
            'type': 'CHEM_LIPINSKI',
            'mw': mw,
            'logp': logp,
            'hbd': hbd,
            'hba': hba,
            'violations': len(violations),
            'violation_details': violations,
            'drug_like': drug_like,
            'assessment': 'PASS - drug-like' if drug_like else 'FAIL - poor oral bioavailability predicted'
        }

    # ── BCS Classification ─────────────────────────────────

    @staticmethod
    def bcs_classify(solubility: str, permeability: str) -> dict:
        """
        Biopharmaceutical Classification System (BCS).
        Class I: High sol, High perm (best)
        Class II: Low sol, High perm
        Class III: High sol, Low perm
        Class IV: Low sol, Low perm (worst)
        """
        sol_high = solubility.lower() in ('high', 'moderate')
        perm_high = permeability.lower() in ('high', 'moderate')

        if sol_high and perm_high:
            bcs_class = "I"
            bioavailability = "HIGH"
            formulation = "Standard oral formulation"
        elif not sol_high and perm_high:
            bcs_class = "II"
            bioavailability = "DISSOLUTION-LIMITED"
            formulation = "Consider micronization, amorphous form, or lipid formulation"
        elif sol_high and not perm_high:
            bcs_class = "III"
            bioavailability = "PERMEABILITY-LIMITED"
            formulation = "Consider permeation enhancers or parenteral route"
        else:
            bcs_class = "IV"
            bioavailability = "LOW"
            formulation = "Consider IV route or advanced delivery system"

        return {
            'type': 'CHEM_BCS',
            'solubility': solubility,
            'permeability': permeability,
            'bcs_class': bcs_class,
            'bioavailability': bioavailability,
            'formulation_strategy': formulation
        }

    # ── ADMET Screening ────────────────────────────────────

    @staticmethod
    def admet_screen(mw: float, logp: float, psa: float,
                     rotatable_bonds: int) -> dict:
        """
        ADMET property screening using rule-based filters.
        Predicts Absorption, Distribution, Metabolism, Excretion, Toxicity risk.
        """
        mw = float(mw)
        logp = float(logp)
        psa = float(psa)
        rotatable_bonds = int(rotatable_bonds)

        flags = []
        risk_score = 0

        # Absorption
        if psa > 140:
            flags.append("Poor oral absorption predicted (PSA > 140)")
            risk_score += 2
        if logp < -1:
            flags.append("Very hydrophilic - poor membrane penetration likely")
            risk_score += 1

        # Distribution
        if logp > 5:
            flags.append("High lipophilicity - plasma protein binding likely high")
            risk_score += 2
        if mw > 500:
            flags.append("High MW - limited tissue distribution")
            risk_score += 1

        # Metabolism
        if rotatable_bonds > 10:
            flags.append("High flexibility - susceptible to metabolic degradation")
            risk_score += 1

        # CNS penetration (simplified)
        cns_permeable = psa < 90 and mw < 450 and logp > 1

        # Overall assessment
        if risk_score == 0:
            assessment = "FAVORABLE"
        elif risk_score <= 2:
            assessment = "ACCEPTABLE"
        elif risk_score <= 4:
            assessment = "CONCERNING"
        else:
            assessment = "POOR"

        return {
            'type': 'CHEM_ADMET',
            'mw': mw,
            'logp': logp,
            'psa': psa,
            'rotatable_bonds': rotatable_bonds,
            'risk_score': risk_score,
            'flags': flags,
            'cns_permeable': cns_permeable,
            'assessment': assessment
        }

    # ── Toxicity Screening ─────────────────────────────────

    @staticmethod
    def tox_screen(compound_name: str, dose_mg_kg: float = 0) -> dict:
        """
        Toxicity screening against compound database.
        Returns LD50, therapeutic index, and safety classification.
        """
        key = compound_name.lower().replace(" ", "_")
        dose_mg_kg = float(dose_mg_kg)
        cpd = COMPOUND_DATABASE.get(key)

        if not cpd:
            return {
                'type': 'CHEM_TOX',
                'compound': compound_name,
                'error': f'Compound "{compound_name}" not in database'
            }

        ld50 = cpd.ld50_mg_kg
        max_dose = cpd.max_daily_dose_mg

        # Therapeutic index (simplified)
        if ld50 > 0 and max_dose > 0:
            # Assume 70 kg patient for mg/kg conversion
            therapeutic_dose_mg_kg = max_dose / 70
            ti = ld50 / therapeutic_dose_mg_kg if therapeutic_dose_mg_kg > 0 else 0
        else:
            ti = 0

        if ti > 100:
            safety = "WIDE therapeutic window"
        elif ti > 10:
            safety = "ADEQUATE therapeutic window"
        elif ti > 3:
            safety = "NARROW therapeutic window - monitor closely"
        else:
            safety = "VERY NARROW - therapeutic drug monitoring required"

        result = {
            'type': 'CHEM_TOX',
            'compound': cpd.name,
            'ld50_mg_kg': ld50,
            'max_daily_dose_mg': max_dose,
            'therapeutic_index': round(ti, 1),
            'safety': safety
        }

        if dose_mg_kg > 0 and ld50 > 0:
            margin = ld50 / dose_mg_kg
            result['dose_mg_kg'] = dose_mg_kg
            result['safety_margin'] = round(margin, 1)
            if margin < 3:
                result['dose_warning'] = 'CRITICAL - dose approaches toxic range'
            elif margin < 10:
                result['dose_warning'] = 'CAUTION - narrow safety margin'

        return result

    # ── Compound Lookup & Search ───────────────────────────

    def lookup(self, compound_name: str) -> dict:
        """Look up a compound by name. Returns full profile."""
        key = compound_name.lower().replace(" ", "_")
        cpd = self.compounds.get(key)
        if not cpd:
            return {'type': 'CHEM', 'error': f'Compound "{compound_name}" not found'}
        return {
            'type': 'CHEM_LOOKUP',
            'name': cpd.name,
            'formula': cpd.formula,
            'molecular_weight': cpd.molecular_weight,
            'logp': cpd.logp,
            'hbd': cpd.hbd,
            'hba': cpd.hba,
            'psa': cpd.psa,
            'rotatable_bonds': cpd.rotatable_bonds,
            'category': cpd.category,
            'therapeutic_class': cpd.therapeutic_class,
            'known_targets': cpd.known_targets,
            'max_daily_dose_mg': cpd.max_daily_dose_mg
        }

    def search_by_target(self, target: str) -> dict:
        """Find compounds that act on a specific molecular target."""
        target_lower = target.lower()
        matches = []
        for key, cpd in self.compounds.items():
            for t in cpd.known_targets:
                if target_lower in t.lower():
                    matches.append({
                        'name': cpd.name,
                        'category': cpd.category,
                        'targets': cpd.known_targets
                    })
                    break

        return {
            'type': 'CHEM_SEARCH',
            'target': target,
            'matches': matches,
            'count': len(matches)
        }

    def search_by_class(self, therapeutic_class: str) -> dict:
        """Find compounds by therapeutic class."""
        class_lower = therapeutic_class.lower()
        matches = []
        for key, cpd in self.compounds.items():
            if class_lower in cpd.therapeutic_class.lower() or class_lower in cpd.category.lower():
                matches.append({
                    'name': cpd.name,
                    'category': cpd.category,
                    'therapeutic_class': cpd.therapeutic_class,
                    'mw': cpd.molecular_weight
                })

        return {
            'type': 'CHEM_SEARCH',
            'therapeutic_class': therapeutic_class,
            'matches': matches,
            'count': len(matches)
        }

    def screen_compound(self, compound_name: str) -> dict:
        """
        Full drug-likeness screening for a compound.
        Runs Lipinski, BCS, ADMET, and toxicity checks.
        """
        key = compound_name.lower().replace(" ", "_")
        cpd = self.compounds.get(key)
        if not cpd:
            return {'type': 'CHEM', 'error': f'Compound "{compound_name}" not found'}

        lipinski = ChemEngine.lipinski_check(cpd.molecular_weight, cpd.logp, cpd.hbd, cpd.hba)
        bcs = ChemEngine.bcs_classify(cpd.solubility, cpd.permeability)
        admet = ChemEngine.admet_screen(cpd.molecular_weight, cpd.logp, cpd.psa, cpd.rotatable_bonds)
        tox = ChemEngine.tox_screen(compound_name)

        # Overall verdict
        scores = {
            'lipinski': 1 if lipinski['drug_like'] else 0,
            'bcs': 1 if bcs['bcs_class'] in ('I', 'II') else 0,
            'admet': 1 if admet['assessment'] in ('FAVORABLE', 'ACCEPTABLE') else 0,
            'toxicity': 1 if tox.get('therapeutic_index', 0) > 10 else 0
        }
        total = sum(scores.values())

        if total == 4:
            verdict = "EXCELLENT CANDIDATE"
        elif total >= 3:
            verdict = "GOOD CANDIDATE"
        elif total >= 2:
            verdict = "MODERATE - optimization needed"
        else:
            verdict = "POOR CANDIDATE"

        return {
            'type': 'CHEM_FULL_SCREEN',
            'compound': cpd.name,
            'lipinski': lipinski,
            'bcs': bcs,
            'admet': admet,
            'toxicity': tox,
            'screening_scores': scores,
            'verdict': verdict
        }

    def register_compound(self, compound: Compound):
        """Register a custom compound in the database."""
        key = compound.name.lower().replace(" ", "_")
        self.compounds[key] = compound

    def list_compounds(self, category: str = None) -> list:
        """List all compounds, optionally filtered by category."""
        results = []
        for key, cpd in self.compounds.items():
            if category and category.lower() not in cpd.category.lower():
                continue
            results.append({
                'name': cpd.name,
                'formula': cpd.formula,
                'mw': cpd.molecular_weight,
                'category': cpd.category
            })
        return results
