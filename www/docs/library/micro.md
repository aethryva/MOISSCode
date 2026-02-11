---
sidebar_position: 5
title: med.micro
---

# med.micro — Microbiology Engine

10 organism profiles, MIC breakpoints (CLSI 2024), and empiric therapy protocols.

## Organisms

E.coli, Klebsiella, Pseudomonas, MRSA, MSSA, Enterococcus, VRE, Strep pneumo, C.diff, Candida

## Methods

### `get_organism(name)` → dict
Get organism profile with Gram stain, morphology.

### `check_susceptibility(organism, antibiotic, mic)` → str
Test MIC against CLSI breakpoints (S/I/R).

### `empiric_therapy(infection_type)` → dict
Get empiric antibiotic recommendations for: CAP, UTI, sepsis, SSTI, meningitis.

### `gram_stain_ddx(gram, morphology)` → list
Differential diagnosis from Gram stain result.
