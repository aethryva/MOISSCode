---
sidebar_position: 6
title: med.genomics
---

# med.genomics — Pharmacogenomics Engine

CYP450 gene profiles, CPIC dosing guidelines, and basic sequence analysis.

## Genes

CYP2D6, CYP2C19, CYP3A4, CYP2C9

## Methods

### `get_phenotype(gene, genotype)` → str
Map genotype to metabolizer phenotype (poor/intermediate/normal/rapid/ultra-rapid).

### `get_dosing(drug, phenotype)` → dict
CPIC-guided dosing recommendation.

### `check_interactions(drug_list)` → list
CYP450-mediated drug-drug interactions.

### `complement(sequence)` → str
DNA complement.

### `reverse_complement(sequence)` → str
Reverse complement.

### `gc_content(sequence)` → float
GC content percentage.

### `translate(mrna)` → str
mRNA to protein translation.
