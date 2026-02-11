---
sidebar_position: 8
title: med.epi
---

# med.epi — Epidemiology Engine

Compartmental disease models and public health statistics.

## Models

### `sir(S, I, R, beta, gamma, days)` → list
SIR compartmental model trajectory.

### `seir(S, E, I, R, beta, sigma, gamma, days)` → list
SEIR model with exposed compartment.

## Statistics

### `r0(beta, gamma)` → float
Basic reproduction number.

### `herd_immunity(R0)` → float
Herd immunity threshold.

### `incidence_rate(cases, population, time)` → float
Incidence rate calculation.

### `prevalence(cases, population)` → float
Point prevalence.

### `cfr(deaths, cases)` → float
Case fatality rate.

### `vaccination_coverage(R0)` → float
Required vaccination coverage to achieve herd immunity.

## Pre-loaded Diseases

COVID-19, Measles, Influenza, Ebola, HIV, Tuberculosis, Malaria, Cholera, Dengue, Smallpox, SARS
