"""
med.micro  - Microbiology Module for MOISSCode
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

    # ─── v3.0 EXPANSION ──────────────────────────────────
    "S.epidermidis": Organism(
        name="Staphylococcus epidermidis", gram="positive", shape="cocci", oxygen="facultative",
        catalase=True, coagulase=False,
        common_infections=["prosthetic_valve_endocarditis", "catheter_infection", "prosthetic_joint"],
        virulence_factors=["Biofilm", "PIA adhesin"],
        susceptible_to=["Vancomycin", "Daptomycin", "Linezolid"],
        resistant_to=["Oxacillin", "Penicillin"],
        first_line_treatment="Vancomycin"
    ),
    "S.pyogenes": Organism(
        name="Streptococcus pyogenes (Group A Strep)", gram="positive", shape="cocci", oxygen="facultative",
        catalase=False,
        common_infections=["pharyngitis", "cellulitis", "necrotizing_fasciitis", "rheumatic_fever"],
        virulence_factors=["M protein", "Streptolysin O/S", "Hyaluronidase", "SpeA superantigen"],
        susceptible_to=["Penicillin", "Amoxicillin", "Ceftriaxone", "Clindamycin"],
        first_line_treatment="Penicillin"
    ),
    "S.agalactiae": Organism(
        name="Streptococcus agalactiae (Group B Strep)", gram="positive", shape="cocci", oxygen="facultative",
        catalase=False,
        common_infections=["neonatal_sepsis", "neonatal_meningitis", "chorioamnionitis", "UTI_pregnant"],
        virulence_factors=["Capsule", "C5a peptidase", "Beta-hemolysin"],
        susceptible_to=["Penicillin", "Ampicillin", "Vancomycin"],
        first_line_treatment="Penicillin"
    ),
    "E.faecium": Organism(
        name="Enterococcus faecium", gram="positive", shape="cocci", oxygen="facultative",
        catalase=False,
        common_infections=["bacteremia", "UTI", "intra-abdominal", "endocarditis"],
        susceptible_to=["Linezolid", "Daptomycin"],
        resistant_to=["Ampicillin", "Cephalosporins", "TMP-SMX"],
        first_line_treatment="Linezolid"
    ),
    "Proteus": Organism(
        name="Proteus mirabilis", gram="negative", shape="bacilli", oxygen="facultative",
        catalase=True,
        common_infections=["UTI_catheter", "wound_infection", "bacteremia"],
        virulence_factors=["Urease", "Swarming motility", "Fimbriae"],
        susceptible_to=["Ampicillin", "Ceftriaxone", "TMP-SMX", "Ciprofloxacin"],
        first_line_treatment="Ampicillin"
    ),
    "Serratia": Organism(
        name="Serratia marcescens", gram="negative", shape="bacilli", oxygen="facultative",
        catalase=True,
        common_infections=["pneumonia", "UTI", "bacteremia", "wound_infection"],
        virulence_factors=["Prodigiosin pigment", "Chromosomal AmpC"],
        susceptible_to=["Meropenem", "Ciprofloxacin", "TMP-SMX"],
        resistant_to=["Ampicillin", "Cefazolin", "Colistin"],
        first_line_treatment="Ceftriaxone"
    ),
    "Acinetobacter": Organism(
        name="Acinetobacter baumannii", gram="negative", shape="coccobacilli", oxygen="aerobic",
        catalase=True,
        common_infections=["pneumonia_VAP", "bacteremia", "wound_infection", "meningitis_post_surgical"],
        virulence_factors=["Biofilm", "OXA carbapenemases", "Capsule"],
        susceptible_to=["Colistin", "Ampicillin-Sulbactam"],
        resistant_to=["Most_beta_lactams", "Fluoroquinolones"],
        first_line_treatment="Colistin"
    ),
    "Stenotrophomonas": Organism(
        name="Stenotrophomonas maltophilia", gram="negative", shape="bacilli", oxygen="aerobic",
        catalase=True,
        common_infections=["pneumonia_VAP", "bacteremia", "UTI"],
        virulence_factors=["L1/L2 metallo-beta-lactamases", "Biofilm"],
        susceptible_to=["TMP-SMX", "Levofloxacin", "Minocycline"],
        resistant_to=["Carbapenems", "Aminoglycosides"],
        first_line_treatment="TMP-SMX"
    ),
    "Bacteroides": Organism(
        name="Bacteroides fragilis", gram="negative", shape="bacilli", oxygen="anaerobic",
        common_infections=["intra-abdominal_abscess", "peritonitis", "pelvic_abscess"],
        virulence_factors=["Capsular polysaccharide", "Metallo-beta-lactamase"],
        susceptible_to=["Metronidazole", "Meropenem", "Piperacillin-Tazobactam"],
        resistant_to=["Penicillin", "Cephalosporins", "Aminoglycosides"],
        first_line_treatment="Metronidazole"
    ),
    "H.influenzae": Organism(
        name="Haemophilus influenzae", gram="negative", shape="coccobacilli", oxygen="facultative",
        common_infections=["otitis_media", "sinusitis", "pneumonia", "epiglottitis", "meningitis"],
        virulence_factors=["Type B capsule", "IgA protease", "LPS"],
        susceptible_to=["Amoxicillin-Clavulanate", "Ceftriaxone", "Azithromycin"],
        resistant_to=["TMP-SMX"],
        first_line_treatment="Amoxicillin-Clavulanate"
    ),
    "N.meningitidis": Organism(
        name="Neisseria meningitidis", gram="negative", shape="cocci", oxygen="aerobic",
        catalase=True,
        common_infections=["meningitis", "meningococcemia", "septic_shock"],
        virulence_factors=["Polysaccharide capsule", "LPS", "IgA protease"],
        susceptible_to=["Penicillin", "Ceftriaxone", "Ciprofloxacin"],
        first_line_treatment="Ceftriaxone"
    ),
    "N.gonorrhoeae": Organism(
        name="Neisseria gonorrhoeae", gram="negative", shape="cocci", oxygen="aerobic",
        catalase=True,
        common_infections=["urethritis", "cervicitis", "PID", "disseminated_gonococcal"],
        virulence_factors=["Pili", "Opa proteins", "LPS"],
        susceptible_to=["Ceftriaxone"],
        resistant_to=["Ciprofloxacin", "Azithromycin"],
        first_line_treatment="Ceftriaxone + Azithromycin"
    ),
    "M.tuberculosis": Organism(
        name="Mycobacterium tuberculosis", gram="variable", shape="bacilli", oxygen="aerobic",
        common_infections=["pulmonary_TB", "TB_meningitis", "miliary_TB", "skeletal_TB"],
        virulence_factors=["Mycolic acid", "Cord factor", "ESAT-6"],
        susceptible_to=["Isoniazid", "Rifampin", "Pyrazinamide", "Ethambutol"],
        first_line_treatment="RIPE (Rifampin+Isoniazid+Pyrazinamide+Ethambutol)"
    ),
    "Legionella": Organism(
        name="Legionella pneumophila", gram="negative", shape="bacilli", oxygen="aerobic",
        common_infections=["Legionnaires_disease", "Pontiac_fever"],
        virulence_factors=["Intracellular survival", "Dot/Icm T4SS"],
        susceptible_to=["Azithromycin", "Levofloxacin"],
        first_line_treatment="Azithromycin"
    ),
    "C.glabrata": Organism(
        name="Candida glabrata", gram="N/A", shape="yeast", oxygen="facultative",
        common_infections=["candidemia", "UTI", "intra-abdominal"],
        susceptible_to=["Caspofungin", "Micafungin", "Amphotericin_B"],
        resistant_to=["Fluconazole"],
        first_line_treatment="Caspofungin"
    ),
    "C.auris": Organism(
        name="Candida auris", gram="N/A", shape="yeast", oxygen="facultative",
        common_infections=["candidemia", "wound_infection", "ear_infection"],
        virulence_factors=["Environmental persistence", "Biofilm", "Multidrug resistance"],
        susceptible_to=["Caspofungin", "Micafungin"],
        resistant_to=["Fluconazole", "Amphotericin_B"],
        first_line_treatment="Caspofungin"
    ),
    "Aspergillus": Organism(
        name="Aspergillus fumigatus", gram="N/A", shape="mold", oxygen="aerobic",
        common_infections=["invasive_aspergillosis", "aspergilloma", "allergic_bronchopulmonary"],
        virulence_factors=["Galactomannan", "Melanin", "Gliotoxin"],
        susceptible_to=["Voriconazole", "Isavuconazole", "Amphotericin_B"],
        first_line_treatment="Voriconazole"
    ),
    "Cryptococcus": Organism(
        name="Cryptococcus neoformans", gram="N/A", shape="yeast", oxygen="aerobic",
        common_infections=["cryptococcal_meningitis", "pneumonia"],
        virulence_factors=["Polysaccharide capsule", "Melanin", "Urease"],
        susceptible_to=["Amphotericin_B", "Flucytosine", "Fluconazole"],
        first_line_treatment="Amphotericin_B + Flucytosine"
    ),
    "P.jirovecii": Organism(
        name="Pneumocystis jirovecii", gram="N/A", shape="cyst", oxygen="aerobic",
        common_infections=["PCP_pneumonia"],
        virulence_factors=["Major surface glycoprotein"],
        susceptible_to=["TMP-SMX", "Pentamidine", "Atovaquone"],
        first_line_treatment="TMP-SMX"
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
            # ─── v3.0 expansion ──────────────────────────
            "HAP_VAP": {
                "infection": "Hospital/Ventilator-Acquired Pneumonia",
                "empiric": ["Piperacillin-Tazobactam", "Cefepime", "Meropenem"],
                "if_MRSA_risk": ["Add Vancomycin or Linezolid"],
                "if_MDR_risk": ["Add Colistin or Aminoglycoside"],
            },
            "endocarditis": {
                "infection": "Infective Endocarditis",
                "native_valve": ["Vancomycin + Gentamicin"],
                "prosthetic_valve": ["Vancomycin + Gentamicin + Rifampin"],
                "if_MSSA": ["Nafcillin/Oxacillin"],
            },
            "osteomyelitis": {
                "infection": "Osteomyelitis",
                "empiric": ["Vancomycin + Ceftriaxone"],
                "if_MSSA": ["Nafcillin/Cefazolin 4-6 weeks"],
                "if_MRSA": ["Vancomycin 4-6 weeks"],
            },
            "CDI": {
                "infection": "Clostridioides difficile Infection",
                "initial": ["Vancomycin oral 125mg QID x10 days"],
                "severe": ["Vancomycin oral + IV Metronidazole"],
                "recurrent": ["Fidaxomicin", "Fecal microbiota transplant"],
            },
            "intra_abdominal": {
                "infection": "Intra-abdominal Infection",
                "mild_moderate": ["Ceftriaxone + Metronidazole"],
                "severe": ["Piperacillin-Tazobactam", "Meropenem"],
                "if_VRE_risk": ["Add Linezolid or Daptomycin"],
            },
            "febrile_neutropenia": {
                "infection": "Febrile Neutropenia",
                "empiric": ["Cefepime", "Meropenem", "Piperacillin-Tazobactam"],
                "if_MRSA_risk": ["Add Vancomycin"],
                "if_fungal_risk": ["Add Caspofungin or Voriconazole"],
            },
            "diabetic_foot": {
                "infection": "Diabetic Foot Infection",
                "mild": ["Amoxicillin-Clavulanate", "Clindamycin"],
                "moderate_severe": ["Piperacillin-Tazobactam", "Ertapenem"],
                "if_MRSA": ["Add Vancomycin or Linezolid"],
            },
            "nec_fasciitis": {
                "infection": "Necrotizing Fasciitis",
                "empiric": ["Vancomycin + Piperacillin-Tazobactam + Clindamycin"],
                "type_II_GAS": ["Penicillin + Clindamycin"],
            },
            "pyelonephritis": {
                "infection": "Pyelonephritis",
                "outpatient": ["Ciprofloxacin", "TMP-SMX"],
                "inpatient": ["Ceftriaxone", "Ciprofloxacin IV"],
                "severe": ["Piperacillin-Tazobactam", "Meropenem"],
            },
            "TB": {
                "infection": "Pulmonary Tuberculosis",
                "initial_phase": ["Isoniazid + Rifampin + Pyrazinamide + Ethambutol x2 months"],
                "continuation": ["Isoniazid + Rifampin x4 months"],
                "MDR_TB": ["Bedaquiline + Pretomanid + Linezolid"],
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
