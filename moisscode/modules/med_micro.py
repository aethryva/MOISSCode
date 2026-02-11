"""
med.micro — Microbiology Module for MOISSCode
Bacterial taxonomy, antibiotic susceptibility tables, MIC breakpoints.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Organism:
    """Microorganism profile."""
    name: str
    gram: str                # "positive", "negative", "variable", "N/A"
    shape: str               # "cocci", "bacilli", "spirochete", etc.
    oxygen: str              # "aerobic", "anaerobic", "facultative"
    catalase: Optional[bool] = None
    coagulase: Optional[bool] = None
    common_infections: List[str] = field(default_factory=list)
    virulence_factors: List[str] = field(default_factory=list)
    susceptible_to: List[str] = field(default_factory=list)
    resistant_to: List[str] = field(default_factory=list)
    first_line_treatment: str = ""


# ─── MIC Breakpoints (CLSI 2024 simplified) ──────────────
# Format: (organism_group, antibiotic) -> {"S": ≤value, "R": ≥value}
MIC_BREAKPOINTS: Dict[tuple, Dict[str, float]] = {
    # Enterobacterales
    ("Enterobacterales", "Ampicillin"):     {"S": 8, "R": 32},
    ("Enterobacterales", "Ceftriaxone"):    {"S": 1, "R": 4},
    ("Enterobacterales", "Ciprofloxacin"):  {"S": 1, "R": 4},
    ("Enterobacterales", "Meropenem"):      {"S": 1, "R": 4},
    ("Enterobacterales", "Gentamicin"):     {"S": 4, "R": 16},
    ("Enterobacterales", "TMP-SMX"):        {"S": 2, "R": 4},
    ("Enterobacterales", "Piperacillin-Tazobactam"): {"S": 16, "R": 128},

    # Staphylococcus
    ("Staphylococcus", "Oxacillin"):        {"S": 2, "R": 4},
    ("Staphylococcus", "Vancomycin"):       {"S": 2, "R": 16},
    ("Staphylococcus", "Daptomycin"):       {"S": 1, "R": None},
    ("Staphylococcus", "Linezolid"):        {"S": 4, "R": 8},
    ("Staphylococcus", "Clindamycin"):      {"S": 0.5, "R": 4},
    ("Staphylococcus", "TMP-SMX"):          {"S": 2, "R": 4},

    # Pseudomonas
    ("Pseudomonas", "Ceftazidime"):         {"S": 8, "R": 32},
    ("Pseudomonas", "Ciprofloxacin"):       {"S": 1, "R": 4},
    ("Pseudomonas", "Meropenem"):           {"S": 2, "R": 8},
    ("Pseudomonas", "Piperacillin-Tazobactam"): {"S": 16, "R": 128},
    ("Pseudomonas", "Tobramycin"):          {"S": 4, "R": 16},
    ("Pseudomonas", "Colistin"):            {"S": 2, "R": 4},

    # Streptococcus
    ("Streptococcus", "Penicillin"):        {"S": 0.12, "R": 2},
    ("Streptococcus", "Ceftriaxone"):       {"S": 1, "R": 4},
    ("Streptococcus", "Vancomycin"):        {"S": 1, "R": None},
    ("Streptococcus", "Erythromycin"):      {"S": 0.25, "R": 1},

    # Enterococcus
    ("Enterococcus", "Ampicillin"):         {"S": 8, "R": 16},
    ("Enterococcus", "Vancomycin"):         {"S": 4, "R": 32},
    ("Enterococcus", "Linezolid"):          {"S": 4, "R": 8},
    ("Enterococcus", "Daptomycin"):         {"S": 4, "R": None},
}


# ─── Organism Database ────────────────────────────────────
ORGANISM_DATABASE: Dict[str, Organism] = {
    "E.coli": Organism(
        name="Escherichia coli",
        gram="negative", shape="bacilli", oxygen="facultative",
        catalase=True, coagulase=False,
        common_infections=["UTI", "bacteremia", "meningitis", "intra-abdominal"],
        virulence_factors=["Type 1 fimbriae", "LPS", "K1 capsule"],
        susceptible_to=["Ceftriaxone", "Ciprofloxacin", "Meropenem", "TMP-SMX"],
        resistant_to=[],
        first_line_treatment="Ceftriaxone"
    ),
    "Klebsiella": Organism(
        name="Klebsiella pneumoniae",
        gram="negative", shape="bacilli", oxygen="facultative",
        catalase=True,
        common_infections=["pneumonia", "UTI", "bacteremia", "liver_abscess"],
        virulence_factors=["Capsule", "LPS", "Siderophores"],
        susceptible_to=["Ceftriaxone", "Meropenem", "Ciprofloxacin"],
        resistant_to=["Ampicillin"],
        first_line_treatment="Ceftriaxone"
    ),
    "Pseudomonas": Organism(
        name="Pseudomonas aeruginosa",
        gram="negative", shape="bacilli", oxygen="aerobic",
        catalase=True,
        common_infections=["pneumonia_VAP", "wound_infection", "UTI", "bacteremia"],
        virulence_factors=["Pyocyanin", "Biofilm", "Elastase", "ExoS/T/U/Y"],
        susceptible_to=["Ceftazidime", "Meropenem", "Ciprofloxacin", "Piperacillin-Tazobactam"],
        resistant_to=["Ampicillin", "Ceftriaxone"],
        first_line_treatment="Piperacillin-Tazobactam"
    ),
    "MRSA": Organism(
        name="Methicillin-Resistant Staphylococcus aureus",
        gram="positive", shape="cocci", oxygen="facultative",
        catalase=True, coagulase=True,
        common_infections=["skin_soft_tissue", "bacteremia", "endocarditis", "osteomyelitis"],
        virulence_factors=["PBP2a", "Protein A", "TSST-1", "PVL"],
        susceptible_to=["Vancomycin", "Daptomycin", "Linezolid", "TMP-SMX"],
        resistant_to=["Oxacillin", "Penicillin", "Cephalosporins"],
        first_line_treatment="Vancomycin"
    ),
    "MSSA": Organism(
        name="Methicillin-Sensitive Staphylococcus aureus",
        gram="positive", shape="cocci", oxygen="facultative",
        catalase=True, coagulase=True,
        common_infections=["skin_soft_tissue", "bacteremia", "endocarditis"],
        susceptible_to=["Oxacillin", "Cefazolin", "Vancomycin"],
        resistant_to=["Penicillin"],
        first_line_treatment="Cefazolin"
    ),
    "Enterococcus_faecalis": Organism(
        name="Enterococcus faecalis",
        gram="positive", shape="cocci", oxygen="facultative",
        catalase=False,
        common_infections=["UTI", "endocarditis", "intra-abdominal", "bacteremia"],
        susceptible_to=["Ampicillin", "Vancomycin", "Linezolid"],
        resistant_to=["Cephalosporins", "TMP-SMX"],
        first_line_treatment="Ampicillin"
    ),
    "VRE": Organism(
        name="Vancomycin-Resistant Enterococcus",
        gram="positive", shape="cocci", oxygen="facultative",
        catalase=False,
        common_infections=["UTI", "bacteremia", "intra-abdominal"],
        virulence_factors=["vanA/vanB gene"],
        susceptible_to=["Linezolid", "Daptomycin"],
        resistant_to=["Vancomycin", "Ampicillin"],
        first_line_treatment="Linezolid"
    ),
    "Strep_pneumo": Organism(
        name="Streptococcus pneumoniae",
        gram="positive", shape="cocci", oxygen="facultative",
        catalase=False,
        common_infections=["pneumonia_CAP", "meningitis", "otitis_media", "sinusitis"],
        virulence_factors=["Capsule", "Pneumolysin", "IgA protease"],
        susceptible_to=["Penicillin", "Ceftriaxone", "Vancomycin"],
        first_line_treatment="Penicillin"
    ),
    "C.diff": Organism(
        name="Clostridioides difficile",
        gram="positive", shape="bacilli", oxygen="anaerobic",
        common_infections=["pseudomembranous_colitis", "antibiotic_associated_diarrhea"],
        virulence_factors=["Toxin A", "Toxin B", "Spore formation"],
        susceptible_to=["Vancomycin_oral", "Fidaxomicin", "Metronidazole"],
        first_line_treatment="Vancomycin_oral"
    ),
    "Candida_albicans": Organism(
        name="Candida albicans",
        gram="N/A", shape="yeast", oxygen="facultative",
        common_infections=["candidemia", "thrush", "vulvovaginal_candidiasis"],
        susceptible_to=["Fluconazole", "Caspofungin", "Amphotericin_B"],
        first_line_treatment="Fluconazole"
    ),
}


class MicroEngine:
    """Microbiology engine for MOISSCode."""

    def __init__(self):
        self.organisms = ORGANISM_DATABASE
        self.breakpoints = MIC_BREAKPOINTS

    def identify(self, organism_key: str) -> Dict:
        """Get organism profile."""
        org = self.organisms.get(organism_key)
        if not org:
            return {"error": f"Unknown organism: {organism_key}. Available: {list(self.organisms.keys())}"}

        return {
            "type": "MICRO_ID",
            "key": organism_key,
            "name": org.name,
            "gram": org.gram,
            "shape": org.shape,
            "oxygen": org.oxygen,
            "common_infections": org.common_infections,
            "first_line": org.first_line_treatment,
            "susceptible_to": org.susceptible_to,
            "resistant_to": org.resistant_to,
        }

    def susceptibility(self, organism_key: str, antibiotic: str,
                       mic_value: float = None) -> Dict:
        """Test antibiotic susceptibility for an organism."""
        org = self.organisms.get(organism_key)
        if not org:
            return {"error": f"Unknown organism: {organism_key}"}

        # Check known susceptibility/resistance
        if antibiotic in org.susceptible_to:
            intrinsic = "SUSCEPTIBLE"
        elif antibiotic in org.resistant_to:
            intrinsic = "RESISTANT"
        else:
            intrinsic = "UNKNOWN"

        result = {
            "type": "MICRO_SUSCEPTIBILITY",
            "organism": organism_key,
            "antibiotic": antibiotic,
            "intrinsic_susceptibility": intrinsic,
        }

        # If MIC provided, interpret against breakpoints
        if mic_value is not None:
            result["mic"] = mic_value
            result["interpretation"] = self._interpret_mic(organism_key, antibiotic, mic_value)

        return result

    def _interpret_mic(self, organism_key: str, antibiotic: str, mic: float) -> str:
        """Interpret MIC against CLSI breakpoints."""
        # Determine organism group
        org = self.organisms.get(organism_key)
        if not org:
            return "UNKNOWN"

        # Map organism to breakpoint group
        group_map = {
            "E.coli": "Enterobacterales", "Klebsiella": "Enterobacterales",
            "MRSA": "Staphylococcus", "MSSA": "Staphylococcus",
            "Pseudomonas": "Pseudomonas",
            "Strep_pneumo": "Streptococcus",
            "Enterococcus_faecalis": "Enterococcus", "VRE": "Enterococcus",
        }
        group = group_map.get(organism_key)
        if not group:
            return "NO_BREAKPOINT"

        bp = self.breakpoints.get((group, antibiotic))
        if not bp:
            return "NO_BREAKPOINT"

        if mic <= bp["S"]:
            return "SUSCEPTIBLE"
        elif bp["R"] and mic >= bp["R"]:
            return "RESISTANT"
        else:
            return "INTERMEDIATE"

    def empiric_therapy(self, infection_type: str) -> Dict:
        """Suggest empiric antibiotic therapy for common infections."""
        therapies = {
            "CAP": {
                "infection": "Community-Acquired Pneumonia",
                "mild": ["Amoxicillin", "Azithromycin"],
                "moderate": ["Ceftriaxone + Azithromycin"],
                "severe": ["Ceftriaxone + Azithromycin", "Piperacillin-Tazobactam"],
            },
            "UTI": {
                "infection": "Urinary Tract Infection",
                "uncomplicated": ["Nitrofurantoin", "TMP-SMX"],
                "complicated": ["Ceftriaxone", "Ciprofloxacin"],
                "urosepsis": ["Meropenem", "Piperacillin-Tazobactam"],
            },
            "sepsis": {
                "infection": "Sepsis/Septic Shock",
                "empiric": ["Vancomycin + Piperacillin-Tazobactam", "Vancomycin + Meropenem"],
                "if_MRSA": ["Add Vancomycin"],
                "if_pseudomonas": ["Use anti-pseudomonal beta-lactam"],
            },
            "SSTI": {
                "infection": "Skin and Soft Tissue Infection",
                "purulent": ["TMP-SMX", "Doxycycline"],
                "non_purulent": ["Cephalexin", "Dicloxacillin"],
                "severe": ["Vancomycin + Piperacillin-Tazobactam"],
            },
            "meningitis": {
                "infection": "Bacterial Meningitis",
                "empiric_adult": ["Ceftriaxone + Vancomycin + Dexamethasone"],
                "empiric_neonate": ["Ampicillin + Cefotaxime"],
                "if_listeria": ["Add Ampicillin"],
            },
        }

        if infection_type not in therapies:
            return {"error": f"Unknown infection: {infection_type}. Available: {list(therapies.keys())}"}

        return {"type": "MICRO_EMPIRIC", **therapies[infection_type]}

    def gram_stain_ddx(self, gram: str, shape: str) -> List[Dict]:
        """Get differential diagnosis based on Gram stain morphology."""
        matches = []
        for key, org in self.organisms.items():
            if org.gram == gram and org.shape == shape:
                matches.append({
                    "key": key,
                    "name": org.name,
                    "first_line": org.first_line_treatment
                })
        return matches

    def list_organisms(self) -> List[str]:
        """List all organisms in the database."""
        return list(self.organisms.keys())
