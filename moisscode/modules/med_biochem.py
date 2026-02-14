"""
med.biochem  - Biochemistry Engine for MOISSCode
Provides enzyme kinetics, metabolic pathway modeling, and reaction rate calculations.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Enzyme:
    """Enzyme profile with kinetic parameters."""
    name: str
    ec_number: str          # Enzyme Commission number (e.g., "1.1.1.27")
    substrate: str
    product: str
    vmax: float             # Maximum reaction velocity (μmol/min)
    km: float               # Michaelis constant (mM)
    kcat: float             # Catalytic constant (1/s)
    optimal_ph: float = 7.4
    optimal_temp: float = 37.0  # °C
    inhibitors: List[str] = field(default_factory=list)
    activators: List[str] = field(default_factory=list)


# ─── Enzyme Database ──────────────────────────────────────
ENZYME_DATABASE: Dict[str, Enzyme] = {
    "LDH": Enzyme(
        name="Lactate Dehydrogenase",
        ec_number="1.1.1.27",
        substrate="Lactate",
        product="Pyruvate",
        vmax=600.0, km=0.5, kcat=250.0,
        optimal_ph=7.4, optimal_temp=37.0,
        inhibitors=["Oxamate", "Oxalate"],
    ),
    "CK": Enzyme(
        name="Creatine Kinase",
        ec_number="2.7.3.2",
        substrate="Creatine + ATP",
        product="Phosphocreatine + ADP",
        vmax=400.0, km=5.0, kcat=180.0,
        optimal_ph=6.8, optimal_temp=37.0,
    ),
    "ALT": Enzyme(
        name="Alanine Aminotransferase",
        ec_number="2.6.1.2",
        substrate="Alanine + α-Ketoglutarate",
        product="Pyruvate + Glutamate",
        vmax=200.0, km=12.0, kcat=100.0,
        optimal_ph=7.4, optimal_temp=37.0,
    ),
    "AST": Enzyme(
        name="Aspartate Aminotransferase",
        ec_number="2.6.1.1",
        substrate="Aspartate + α-Ketoglutarate",
        product="Oxaloacetate + Glutamate",
        vmax=250.0, km=8.0, kcat=120.0,
        optimal_ph=7.4, optimal_temp=37.0,
    ),
    "ALP": Enzyme(
        name="Alkaline Phosphatase",
        ec_number="3.1.3.1",
        substrate="Phosphate Ester",
        product="Alcohol + Phosphate",
        vmax=150.0, km=1.5, kcat=80.0,
        optimal_ph=9.8, optimal_temp=37.0,
    ),
    "Amylase": Enzyme(
        name="α-Amylase",
        ec_number="3.2.1.1",
        substrate="Starch",
        product="Maltose + Dextrins",
        vmax=500.0, km=3.0, kcat=200.0,
        optimal_ph=7.0, optimal_temp=37.0,
        inhibitors=["Acarbose"],
    ),
    "Lipase": Enzyme(
        name="Pancreatic Lipase",
        ec_number="3.1.1.3",
        substrate="Triglyceride",
        product="Fatty Acid + Glycerol",
        vmax=300.0, km=2.0, kcat=150.0,
        optimal_ph=8.0, optimal_temp=37.0,
    ),
    "ACE": Enzyme(
        name="Angiotensin-Converting Enzyme",
        ec_number="3.4.15.1",
        substrate="Angiotensin I",
        product="Angiotensin II",
        vmax=100.0, km=0.3, kcat=50.0,
        optimal_ph=7.4, optimal_temp=37.0,
        inhibitors=["Captopril", "Enalapril", "Lisinopril"],
    ),

    # ─── v3.0 Expansion ──────────────────────────────────
    "GGT": Enzyme(
        name="Gamma-Glutamyl Transferase", ec_number="2.3.2.2",
        substrate="Glutathione + Amino Acid", product="γ-Glutamyl-AA + Cysteinylglycine",
        vmax=180.0, km=2.5, kcat=90.0, optimal_ph=8.0,
    ),
    "Cholinesterase": Enzyme(
        name="Acetylcholinesterase", ec_number="3.1.1.7",
        substrate="Acetylcholine", product="Choline + Acetate",
        vmax=10000.0, km=0.09, kcat=14000.0, optimal_ph=8.0,
        inhibitors=["Neostigmine", "Pyridostigmine", "Donepezil", "Organophosphates"],
    ),
    "Trypsin": Enzyme(
        name="Trypsin", ec_number="3.4.21.4",
        substrate="Peptide (Arg/Lys)", product="Cleaved Peptides",
        vmax=500.0, km=1.0, kcat=200.0, optimal_ph=8.0,
        inhibitors=["Aprotinin", "Soybean Trypsin Inhibitor"],
    ),
    "Pepsin": Enzyme(
        name="Pepsin", ec_number="3.4.23.1",
        substrate="Protein", product="Peptide fragments",
        vmax=400.0, km=2.0, kcat=150.0, optimal_ph=2.0, optimal_temp=37.0,
    ),
    "Carbonic_Anhydrase": Enzyme(
        name="Carbonic Anhydrase", ec_number="4.2.1.1",
        substrate="CO2 + H2O", product="HCO3- + H+",
        vmax=1000000.0, km=12.0, kcat=600000.0, optimal_ph=7.4,
        inhibitors=["Acetazolamide", "Dorzolamide"],
    ),
    "Thrombin": Enzyme(
        name="Thrombin", ec_number="3.4.21.5",
        substrate="Fibrinogen", product="Fibrin",
        vmax=50.0, km=0.01, kcat=30.0, optimal_ph=7.4,
        inhibitors=["Bivalirudin", "Argatroban", "Dabigatran"],
    ),
    "Renin": Enzyme(
        name="Renin", ec_number="3.4.23.15",
        substrate="Angiotensinogen", product="Angiotensin I",
        vmax=10.0, km=0.002, kcat=5.0, optimal_ph=5.5,
        inhibitors=["Aliskiren"],
    ),
    "Tyrosine_Kinase": Enzyme(
        name="Receptor Tyrosine Kinase (EGFR)", ec_number="2.7.10.1",
        substrate="Protein + ATP", product="Phosphoprotein + ADP",
        vmax=80.0, km=0.5, kcat=40.0, optimal_ph=7.4,
        inhibitors=["Imatinib", "Erlotinib", "Gefitinib", "Sorafenib"],
    ),
    "COX1": Enzyme(
        name="Cyclooxygenase-1", ec_number="1.14.99.1",
        substrate="Arachidonic Acid", product="PGH2",
        vmax=120.0, km=5.0, kcat=60.0, optimal_ph=7.4,
        inhibitors=["Aspirin", "Ibuprofen", "Naproxen"],
    ),
    "COX2": Enzyme(
        name="Cyclooxygenase-2", ec_number="1.14.99.1",
        substrate="Arachidonic Acid", product="PGH2",
        vmax=150.0, km=3.0, kcat=75.0, optimal_ph=7.4,
        inhibitors=["Celecoxib", "Aspirin", "Ibuprofen", "Diclofenac"],
    ),
    "MAO_A": Enzyme(
        name="Monoamine Oxidase A", ec_number="1.4.3.4",
        substrate="Serotonin / Norepinephrine", product="Aldehyde + NH3 + H2O2",
        vmax=80.0, km=0.5, kcat=40.0, optimal_ph=7.4,
        inhibitors=["Moclobemide", "Clorgyline"],
    ),
    "MAO_B": Enzyme(
        name="Monoamine Oxidase B", ec_number="1.4.3.4",
        substrate="Dopamine / Phenylethylamine", product="Aldehyde + NH3 + H2O2",
        vmax=90.0, km=0.3, kcat=45.0, optimal_ph=7.4,
        inhibitors=["Selegiline", "Rasagiline"],
    ),
    "Aldolase": Enzyme(
        name="Aldolase", ec_number="4.1.2.13",
        substrate="Fructose-1,6-bisP", product="G3P + DHAP",
        vmax=300.0, km=0.1, kcat=120.0, optimal_ph=7.4,
    ),
    "HMG_CoA_Reductase": Enzyme(
        name="HMG-CoA Reductase", ec_number="1.1.1.34",
        substrate="HMG-CoA", product="Mevalonate",
        vmax=50.0, km=0.01, kcat=25.0, optimal_ph=7.4,
        inhibitors=["Atorvastatin", "Rosuvastatin", "Simvastatin", "Pravastatin"],
    ),
    "Xanthine_Oxidase": Enzyme(
        name="Xanthine Oxidase", ec_number="1.17.3.2",
        substrate="Hypoxanthine", product="Uric Acid",
        vmax=200.0, km=3.0, kcat=80.0, optimal_ph=7.4,
        inhibitors=["Allopurinol", "Febuxostat"],
    ),
    "DNA_Polymerase": Enzyme(
        name="DNA Polymerase III", ec_number="2.7.7.7",
        substrate="dNTP + DNA template", product="Extended DNA strand",
        vmax=1000.0, km=0.01, kcat=500.0, optimal_ph=7.4,
        inhibitors=["Acyclovir-TP", "Cidofovir"],
    ),
    "RNA_Polymerase": Enzyme(
        name="RNA Polymerase II", ec_number="2.7.7.6",
        substrate="NTP + DNA template", product="mRNA",
        vmax=800.0, km=0.05, kcat=400.0, optimal_ph=7.4,
        inhibitors=["Rifampin", "Actinomycin D", "α-Amanitin"],
    ),
}

# ─── Metabolic Pathways (simplified) ──────────────────────
METABOLIC_PATHWAYS = {
    "glycolysis": {
        "name": "Glycolysis",
        "steps": [
            {"enzyme": "Hexokinase", "substrate": "Glucose", "product": "Glucose-6-P", "atp_change": -1},
            {"enzyme": "PFK-1", "substrate": "Fructose-6-P", "product": "Fructose-1,6-bisP", "atp_change": -1},
            {"enzyme": "Aldolase", "substrate": "Fructose-1,6-bisP", "product": "G3P + DHAP", "atp_change": 0},
            {"enzyme": "GAPDH", "substrate": "G3P", "product": "1,3-BPG", "atp_change": 0},
            {"enzyme": "PGK", "substrate": "1,3-BPG", "product": "3-PG", "atp_change": +2},
            {"enzyme": "Pyruvate Kinase", "substrate": "PEP", "product": "Pyruvate", "atp_change": +2},
        ],
        "net_atp": 2,
        "net_nadh": 2,
        "location": "cytoplasm"
    },
    "krebs": {
        "name": "Krebs Cycle (TCA)",
        "steps": [
            {"enzyme": "Citrate Synthase", "substrate": "Acetyl-CoA + OAA", "product": "Citrate", "atp_change": 0},
            {"enzyme": "Isocitrate DH", "substrate": "Isocitrate", "product": "α-Ketoglutarate", "atp_change": 0},
            {"enzyme": "α-KG DH", "substrate": "α-Ketoglutarate", "product": "Succinyl-CoA", "atp_change": 0},
            {"enzyme": "Succinyl-CoA Synthetase", "substrate": "Succinyl-CoA", "product": "Succinate", "atp_change": 1},
            {"enzyme": "Succinate DH", "substrate": "Succinate", "product": "Fumarate", "atp_change": 0},
            {"enzyme": "Malate DH", "substrate": "Malate", "product": "Oxaloacetate", "atp_change": 0},
        ],
        "net_atp": 1,
        "net_nadh": 3,
        "net_fadh2": 1,
        "location": "mitochondria"
    },
    "beta_oxidation": {
        "name": "β-Oxidation",
        "steps": [
            {"enzyme": "Acyl-CoA DH", "substrate": "Acyl-CoA", "product": "Enoyl-CoA", "atp_change": 0},
            {"enzyme": "Enoyl-CoA Hydratase", "substrate": "Enoyl-CoA", "product": "L-Hydroxyacyl-CoA", "atp_change": 0},
            {"enzyme": "Hydroxyacyl-CoA DH", "substrate": "L-Hydroxyacyl-CoA", "product": "Ketoacyl-CoA", "atp_change": 0},
            {"enzyme": "Thiolase", "substrate": "Ketoacyl-CoA", "product": "Acetyl-CoA", "atp_change": 0},
        ],
        "net_atp_per_cycle": 5,     # Via FADH2 + NADH in ETC
        "location": "mitochondria"
    },
    "urea_cycle": {
        "name": "Urea Cycle",
        "steps": [
            {"enzyme": "CPS I", "substrate": "NH4+ + CO2", "product": "Carbamoyl-P", "atp_change": -2},
            {"enzyme": "OTC", "substrate": "Carbamoyl-P + Ornithine", "product": "Citrulline", "atp_change": 0},
            {"enzyme": "ASS", "substrate": "Citrulline + Aspartate", "product": "Argininosuccinate", "atp_change": -1},
            {"enzyme": "ASL", "substrate": "Argininosuccinate", "product": "Arginine + Fumarate", "atp_change": 0},
            {"enzyme": "Arginase", "substrate": "Arginine", "product": "Urea + Ornithine", "atp_change": 0},
        ],
        "net_atp": -3,
        "location": "mitochondria/cytoplasm"
    },

    # ─── v3.0 Expansion ──────────────────────────────────
    "pentose_phosphate": {
        "name": "Pentose Phosphate Pathway",
        "steps": [
            {"enzyme": "Glucose-6-P DH", "substrate": "Glucose-6-P", "product": "6-Phosphoglucono-δ-lactone", "atp_change": 0},
            {"enzyme": "6-Phosphogluconate DH", "substrate": "6-Phosphogluconate", "product": "Ribulose-5-P", "atp_change": 0},
            {"enzyme": "Transketolase", "substrate": "Ribulose-5-P", "product": "Glycolytic intermediates", "atp_change": 0},
        ],
        "net_nadph": 2,
        "net_atp": 0,
        "location": "cytoplasm",
        "key_product": "NADPH (for biosynthesis/antioxidant defense) + Ribose-5-P (for nucleotides)"
    },
    "gluconeogenesis": {
        "name": "Gluconeogenesis",
        "steps": [
            {"enzyme": "Pyruvate Carboxylase", "substrate": "Pyruvate", "product": "Oxaloacetate", "atp_change": -1},
            {"enzyme": "PEPCK", "substrate": "Oxaloacetate", "product": "PEP", "atp_change": -1},
            {"enzyme": "Fructose-1,6-bisphosphatase", "substrate": "Fructose-1,6-bisP", "product": "Fructose-6-P", "atp_change": 0},
            {"enzyme": "Glucose-6-phosphatase", "substrate": "Glucose-6-P", "product": "Glucose", "atp_change": 0},
        ],
        "net_atp": -6,
        "location": "cytoplasm/mitochondria"
    },
    "fatty_acid_synthesis": {
        "name": "Fatty Acid Synthesis",
        "steps": [
            {"enzyme": "Acetyl-CoA Carboxylase", "substrate": "Acetyl-CoA", "product": "Malonyl-CoA", "atp_change": -1},
            {"enzyme": "Fatty Acid Synthase", "substrate": "Malonyl-CoA + Acetyl-CoA", "product": "Palmitate", "atp_change": 0},
        ],
        "net_nadph_consumed": 14,
        "net_atp": -7,
        "location": "cytoplasm",
        "key_product": "Palmitate (C16:0)"
    },
    "electron_transport_chain": {
        "name": "Electron Transport Chain",
        "steps": [
            {"enzyme": "Complex I (NADH DH)", "substrate": "NADH", "product": "NAD+ + 4H+ pumped", "atp_change": 0},
            {"enzyme": "Complex II (Succinate DH)", "substrate": "FADH2", "product": "FAD + 0H+ pumped", "atp_change": 0},
            {"enzyme": "Complex III (Cytochrome bc1)", "substrate": "CoQH2", "product": "CoQ + 4H+ pumped", "atp_change": 0},
            {"enzyme": "Complex IV (Cytochrome c Oxidase)", "substrate": "Cytochrome c + O2", "product": "H2O + 2H+ pumped", "atp_change": 0},
            {"enzyme": "Complex V (ATP Synthase)", "substrate": "ADP + Pi + H+ gradient", "product": "ATP", "atp_change": 0},
        ],
        "atp_per_nadh": 2.5,
        "atp_per_fadh2": 1.5,
        "location": "inner mitochondrial membrane"
    },
}


class BiochemEngine:
    """Biochemistry engine for MOISSCode."""

    def __init__(self):
        self.enzymes = ENZYME_DATABASE
        self.pathways = METABOLIC_PATHWAYS

    # ─── Enzyme Kinetics ───────────────────────────────────────
    def michaelis_menten(self, enzyme_name: str, substrate_conc: float) -> Dict:
        """
        Calculate reaction velocity using Michaelis-Menten equation.
        V = (Vmax × [S]) / (Km + [S])
        """
        enzyme = self.enzymes.get(enzyme_name)
        if not enzyme:
            return {"error": f"Unknown enzyme: {enzyme_name}"}

        v = (enzyme.vmax * substrate_conc) / (enzyme.km + substrate_conc)
        fraction_vmax = v / enzyme.vmax

        return {
            "type": "BIOCHEM_KINETICS",
            "enzyme": enzyme_name,
            "substrate_conc_mM": substrate_conc,
            "velocity": round(v, 4),
            "vmax": enzyme.vmax,
            "km": enzyme.km,
            "fraction_vmax": round(fraction_vmax, 4),
        }

    def lineweaver_burk(self, enzyme_name: str, substrate_concs: List[float]) -> Dict:
        """
        Generate Lineweaver-Burk (double reciprocal) data points.
        1/V = (Km/Vmax)(1/[S]) + 1/Vmax
        """
        enzyme = self.enzymes.get(enzyme_name)
        if not enzyme:
            return {"error": f"Unknown enzyme: {enzyme_name}"}

        points = []
        for s in substrate_concs:
            if s > 0:
                v = (enzyme.vmax * s) / (enzyme.km + s)
                points.append({"inv_S": round(1/s, 4), "inv_V": round(1/v, 6)})

        return {
            "type": "BIOCHEM_LB_PLOT",
            "enzyme": enzyme_name,
            "y_intercept": round(1/enzyme.vmax, 6),
            "x_intercept": round(-1/enzyme.km, 6),
            "slope": round(enzyme.km/enzyme.vmax, 6),
            "data_points": points
        }

    def competitive_inhibition(self, enzyme_name: str, substrate_conc: float,
                                inhibitor_conc: float, ki: float = 1.0) -> Dict:
        """
        Velocity with competitive inhibition:
        V = Vmax × [S] / (Km(1 + [I]/Ki) + [S])
        """
        enzyme = self.enzymes.get(enzyme_name)
        if not enzyme:
            return {"error": f"Unknown enzyme: {enzyme_name}"}

        km_apparent = enzyme.km * (1 + inhibitor_conc / ki)
        v = (enzyme.vmax * substrate_conc) / (km_apparent + substrate_conc)
        v_uninhibited = (enzyme.vmax * substrate_conc) / (enzyme.km + substrate_conc)

        return {
            "type": "BIOCHEM_INHIBITION",
            "enzyme": enzyme_name,
            "inhibition_type": "competitive",
            "velocity_inhibited": round(v, 4),
            "velocity_uninhibited": round(v_uninhibited, 4),
            "percent_inhibition": round((1 - v/v_uninhibited) * 100, 2),
            "km_apparent": round(km_apparent, 4),
        }

    # ─── Metabolic Pathways ────────────────────────────────────
    def get_pathway(self, name: str) -> Dict:
        """Get information about a metabolic pathway."""
        pathway = self.pathways.get(name)
        if not pathway:
            return {"error": f"Unknown pathway: {name}. Available: {list(self.pathways.keys())}"}
        return {"type": "BIOCHEM_PATHWAY", **pathway}

    def atp_yield(self, pathway_name: str, cycles: int = 1) -> Dict:
        """Calculate ATP yield from a metabolic pathway."""
        pathway = self.pathways.get(pathway_name)
        if not pathway:
            return {"error": f"Unknown pathway: {pathway_name}"}

        net = pathway.get('net_atp', 0) * cycles
        nadh = pathway.get('net_nadh', 0) * cycles * 2.5  # ~2.5 ATP per NADH via ETC
        fadh2 = pathway.get('net_fadh2', 0) * cycles * 1.5  # ~1.5 ATP per FADH2

        return {
            "type": "BIOCHEM_ATP",
            "pathway": pathway_name,
            "cycles": cycles,
            "substrate_level_atp": net,
            "from_nadh": nadh,
            "from_fadh2": fadh2,
            "total_atp": net + nadh + fadh2
        }

    # ─── Enzyme Lookup ─────────────────────────────────────────
    def get_enzyme(self, name: str) -> Optional[Dict]:
        """Get enzyme profile."""
        enzyme = self.enzymes.get(name)
        if not enzyme:
            return None
        return {
            "name": enzyme.name,
            "ec": enzyme.ec_number,
            "substrate": enzyme.substrate,
            "product": enzyme.product,
            "vmax": enzyme.vmax,
            "km": enzyme.km,
            "kcat": enzyme.kcat,
            "inhibitors": enzyme.inhibitors,
        }

    def list_enzymes(self) -> List[str]:
        """List all available enzymes."""
        return list(self.enzymes.keys())

    # ─── Henderson-Hasselbalch ─────────────────────────────────
    def ph_buffer(self, pka: float, acid_conc: float, base_conc: float) -> float:
        """Calculate pH using Henderson-Hasselbalch: pH = pKa + log([A-]/[HA])"""
        if acid_conc <= 0:
            return pka + 10  # Essentially all base
        return round(pka + math.log10(base_conc / acid_conc), 2)

    # ─── Osmolality ────────────────────────────────────────────
    def serum_osmolality(self, sodium: float, glucose: float, bun: float) -> Dict:
        """
        Calculate serum osmolality:
        Osm = 2×Na + Glucose/18 + BUN/2.8
        Normal: 275-295 mOsm/kg
        """
        osm = 2 * sodium + glucose / 18.0 + bun / 2.8
        status = "NORMAL" if 275 <= osm <= 295 else ("HIGH" if osm > 295 else "LOW")
        return {
            "type": "BIOCHEM_OSMOLALITY",
            "osmolality": round(osm, 1),
            "status": status,
            "normal_range": "275-295 mOsm/kg"
        }

    # ─── Anion Gap ─────────────────────────────────────────────
    def anion_gap(self, sodium: float, chloride: float, bicarb: float) -> Dict:
        """
        Calculate anion gap: AG = Na - (Cl + HCO3)
        Normal: 8-12 mEq/L
        """
        ag = sodium - (chloride + bicarb)
        status = "NORMAL" if 8 <= ag <= 12 else ("ELEVATED" if ag > 12 else "LOW")
        return {
            "type": "BIOCHEM_ANION_GAP",
            "anion_gap": round(ag, 1),
            "status": status,
            "normal_range": "8-12 mEq/L"
        }
