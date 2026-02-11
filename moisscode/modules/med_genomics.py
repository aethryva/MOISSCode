"""
med.genomics — Pharmacogenomics Module for MOISSCode
CYP450 variants, drug metabolism phenotypes, and basic sequence handling.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class CYP450Gene:
    """Cytochrome P450 gene profile for pharmacogenomics."""
    gene: str
    full_name: str
    substrates: List[str]       # Drugs metabolized by this enzyme
    inhibitors: List[str]       # Drugs that inhibit this enzyme
    inducers: List[str]         # Drugs that induce this enzyme
    phenotypes: Dict[str, str]  # genotype -> phenotype (PM/IM/NM/RM/UM)


# ─── CYP450 Database ──────────────────────────────────────
CYP450_DATABASE: Dict[str, CYP450Gene] = {
    "CYP2D6": CYP450Gene(
        gene="CYP2D6",
        full_name="Cytochrome P450 2D6",
        substrates=["Codeine", "Tramadol", "Metoprolol", "Fluoxetine", "Tamoxifen",
                    "Ondansetron", "Haloperidol", "Risperidone"],
        inhibitors=["Paroxetine", "Fluoxetine", "Bupropion", "Quinidine"],
        inducers=["Dexamethasone", "Rifampin"],
        phenotypes={
            "*1/*1": "NM",      # Normal Metabolizer
            "*1/*4": "IM",      # Intermediate Metabolizer
            "*4/*4": "PM",      # Poor Metabolizer
            "*1/*1xN": "UM",    # Ultrarapid Metabolizer
            "*1/*2": "NM",
            "*2/*2": "NM",
            "*4/*5": "PM",
        }
    ),
    "CYP2C19": CYP450Gene(
        gene="CYP2C19",
        full_name="Cytochrome P450 2C19",
        substrates=["Clopidogrel", "Omeprazole", "Voriconazole", "Escitalopram",
                    "Diazepam", "Phenytoin", "Proguanil"],
        inhibitors=["Omeprazole", "Fluconazole", "Fluoxetine", "Fluvoxamine"],
        inducers=["Rifampin", "Carbamazepine"],
        phenotypes={
            "*1/*1": "NM",
            "*1/*2": "IM",
            "*2/*2": "PM",
            "*1/*17": "RM",     # Rapid Metabolizer
            "*17/*17": "UM",
            "*2/*3": "PM",
        }
    ),
    "CYP3A4": CYP450Gene(
        gene="CYP3A4",
        full_name="Cytochrome P450 3A4",
        substrates=["Tacrolimus", "Cyclosporine", "Midazolam", "Fentanyl",
                    "Statins", "Amlodipine", "Apixaban", "Rivaroxaban"],
        inhibitors=["Ketoconazole", "Itraconazole", "Grapefruit", "Ritonavir",
                    "Clarithromycin", "Erythromycin"],
        inducers=["Rifampin", "Carbamazepine", "Phenytoin", "St_Johns_Wort"],
        phenotypes={
            "*1/*1": "NM",
            "*1/*22": "IM",
            "*22/*22": "PM",
        }
    ),
    "CYP2C9": CYP450Gene(
        gene="CYP2C9",
        full_name="Cytochrome P450 2C9",
        substrates=["Warfarin", "Phenytoin", "Losartan", "Celecoxib",
                    "Glipizide", "Ibuprofen", "Diclofenac"],
        inhibitors=["Fluconazole", "Amiodarone", "Metronidazole"],
        inducers=["Rifampin"],
        phenotypes={
            "*1/*1": "NM",
            "*1/*2": "IM",
            "*1/*3": "IM",
            "*2/*2": "PM",
            "*2/*3": "PM",
            "*3/*3": "PM",
        }
    ),
}


# ─── Pharmacogenomic Dosing Guidelines ────────────────────
PGX_GUIDELINES: Dict[tuple, Dict] = {
    ("CYP2D6", "Codeine", "PM"): {
        "recommendation": "AVOID codeine — no analgesic effect (cannot convert to morphine)",
        "alternative": "Use morphine or non-opioid analgesics",
        "source": "CPIC"
    },
    ("CYP2D6", "Codeine", "UM"): {
        "recommendation": "AVOID codeine — risk of toxicity (excessive morphine formation)",
        "alternative": "Use non-opioid analgesics or morphine with dose reduction",
        "source": "CPIC"
    },
    ("CYP2C19", "Clopidogrel", "PM"): {
        "recommendation": "AVOID clopidogrel — reduced antiplatelet effect",
        "alternative": "Use prasugrel or ticagrelor",
        "source": "CPIC"
    },
    ("CYP2C19", "Clopidogrel", "IM"): {
        "recommendation": "Consider alternative antiplatelet — reduced effect possible",
        "alternative": "Prasugrel or ticagrelor preferred",
        "source": "CPIC"
    },
    ("CYP2C9", "Warfarin", "PM"): {
        "recommendation": "REDUCE warfarin dose by 50-80% — increased bleeding risk",
        "alternative": "Consider lower starting dose (1-2 mg/day) with close INR monitoring",
        "source": "CPIC"
    },
    ("CYP2C9", "Warfarin", "IM"): {
        "recommendation": "REDUCE warfarin dose by 20-40%",
        "alternative": "Lower starting dose with close monitoring",
        "source": "CPIC"
    },
    ("CYP3A4", "Tacrolimus", "PM"): {
        "recommendation": "REDUCE tacrolimus dose by 50% — risk of toxicity",
        "alternative": "Close therapeutic drug monitoring required",
        "source": "CPIC"
    },
}


class GenomicsEngine:
    """Pharmacogenomics engine for MOISSCode."""

    def __init__(self):
        self.cyp_genes = CYP450_DATABASE
        self.guidelines = PGX_GUIDELINES

    def get_phenotype(self, gene: str, genotype: str) -> Dict:
        """Determine metabolizer phenotype from genotype."""
        cyp = self.cyp_genes.get(gene)
        if not cyp:
            return {"error": f"Unknown gene: {gene}. Available: {list(self.cyp_genes.keys())}"}

        phenotype = cyp.phenotypes.get(genotype, "UNKNOWN")
        phenotype_names = {
            "PM": "Poor Metabolizer",
            "IM": "Intermediate Metabolizer",
            "NM": "Normal Metabolizer",
            "RM": "Rapid Metabolizer",
            "UM": "Ultrarapid Metabolizer",
        }

        return {
            "type": "GENOMICS_PHENOTYPE",
            "gene": gene,
            "genotype": genotype,
            "phenotype": phenotype,
            "phenotype_full": phenotype_names.get(phenotype, "Unknown"),
        }

    def drug_gene_check(self, drug: str) -> Dict:
        """Check which CYP450 genes affect a drug's metabolism."""
        affected = []
        for gene_name, cyp in self.cyp_genes.items():
            role = []
            if drug in cyp.substrates:
                role.append("substrate")
            if drug in cyp.inhibitors:
                role.append("inhibitor")
            if drug in cyp.inducers:
                role.append("inducer")
            if role:
                affected.append({"gene": gene_name, "roles": role})

        return {
            "type": "GENOMICS_DRUG_CHECK",
            "drug": drug,
            "affected_genes": affected,
            "num_genes": len(affected)
        }

    def dosing_guidance(self, gene: str, drug: str, genotype: str) -> Dict:
        """Get pharmacogenomic dosing guidance."""
        phenotype_result = self.get_phenotype(gene, genotype)
        phenotype = phenotype_result.get("phenotype", "UNKNOWN")

        guideline = self.guidelines.get((gene, drug, phenotype))

        result = {
            "type": "GENOMICS_DOSING",
            "gene": gene,
            "drug": drug,
            "genotype": genotype,
            "phenotype": phenotype,
        }

        if guideline:
            result.update(guideline)
            result["has_guideline"] = True
        else:
            result["recommendation"] = "Standard dosing — no pharmacogenomic adjustment needed"
            result["has_guideline"] = False

        return result

    def interaction_check(self, current_drugs: List[str]) -> Dict:
        """Check for CYP450-mediated drug-drug interactions."""
        interactions = []

        for gene_name, cyp in self.cyp_genes.items():
            substrates_present = [d for d in current_drugs if d in cyp.substrates]
            inhibitors_present = [d for d in current_drugs if d in cyp.inhibitors]
            inducers_present = [d for d in current_drugs if d in cyp.inducers]

            for substrate in substrates_present:
                for inhibitor in inhibitors_present:
                    if substrate != inhibitor:
                        interactions.append({
                            "type": "INHIBITION",
                            "gene": gene_name,
                            "substrate": substrate,
                            "inhibitor": inhibitor,
                            "effect": f"{inhibitor} inhibits {gene_name} → {substrate} levels may INCREASE",
                            "severity": "MODERATE"
                        })
                for inducer in inducers_present:
                    if substrate != inducer:
                        interactions.append({
                            "type": "INDUCTION",
                            "gene": gene_name,
                            "substrate": substrate,
                            "inducer": inducer,
                            "effect": f"{inducer} induces {gene_name} → {substrate} levels may DECREASE",
                            "severity": "MODERATE"
                        })

        return {
            "type": "GENOMICS_INTERACTION",
            "drugs_checked": current_drugs,
            "interactions": interactions,
            "total": len(interactions)
        }

    # ─── Basic Sequence Tools ──────────────────────────────────
    def complement(self, dna_sequence: str) -> str:
        """Get complement of a DNA sequence."""
        comp = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G',
                'a': 't', 't': 'a', 'g': 'c', 'c': 'g'}
        return ''.join(comp.get(base, base) for base in dna_sequence)

    def reverse_complement(self, dna_sequence: str) -> str:
        """Get reverse complement of a DNA sequence."""
        return self.complement(dna_sequence)[::-1]

    def gc_content(self, sequence: str) -> float:
        """Calculate GC content of a nucleotide sequence."""
        seq = sequence.upper()
        gc = sum(1 for b in seq if b in 'GC')
        return round(gc / len(seq) * 100, 2) if seq else 0.0

    def translate(self, mrna_sequence: str) -> str:
        """Translate mRNA to protein (single-letter amino acids)."""
        codon_table = {
            'UUU': 'F', 'UUC': 'F', 'UUA': 'L', 'UUG': 'L',
            'CUU': 'L', 'CUC': 'L', 'CUA': 'L', 'CUG': 'L',
            'AUU': 'I', 'AUC': 'I', 'AUA': 'I', 'AUG': 'M',
            'GUU': 'V', 'GUC': 'V', 'GUA': 'V', 'GUG': 'V',
            'UCU': 'S', 'UCC': 'S', 'UCA': 'S', 'UCG': 'S',
            'CCU': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
            'ACU': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
            'GCU': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
            'UAU': 'Y', 'UAC': 'Y', 'UAA': '*', 'UAG': '*',
            'CAU': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'AAU': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
            'GAU': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
            'UGU': 'C', 'UGC': 'C', 'UGA': '*', 'UGG': 'W',
            'CGU': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
            'AGU': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
            'GGU': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
        }
        mrna = mrna_sequence.upper().replace('T', 'U')
        protein = []
        for i in range(0, len(mrna) - 2, 3):
            codon = mrna[i:i+3]
            aa = codon_table.get(codon, '?')
            if aa == '*':
                break
            protein.append(aa)
        return ''.join(protein)
