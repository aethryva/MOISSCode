"""
med.epi — Epidemiology Module for MOISSCode
SIR/SEIR models, R₀ calculations, outbreak tracking, and incidence metrics.
"""

import math
from typing import Dict, List, Optional, Tuple


class EpiEngine:
    """Epidemiology modeling engine."""

    # ─── Basic Reproduction Number ─────────────────────────────
    def r0(self, beta: float, gamma: float, sigma: float = None) -> Dict:
        """
        Calculate basic reproduction number.
        SIR model:  R₀ = β / γ
        SEIR model: R₀ = β / γ  (same, σ affects timing not R₀)

        Args:
            beta:  transmission rate (contacts per unit time × probability of transmission)
            gamma: recovery rate (1/infectious_period in days)
            sigma: incubation rate (1/incubation_period in days), optional for SEIR
        """
        if gamma == 0:
            return {"error": "Recovery rate (gamma) cannot be zero"}

        r0_val = beta / gamma
        status = "EPIDEMIC" if r0_val > 1 else ("ENDEMIC" if r0_val == 1 else "DECLINING")

        result = {
            "type": "EPI_R0",
            "R0": round(r0_val, 3),
            "beta": beta,
            "gamma": gamma,
            "infectious_period_days": round(1/gamma, 1),
            "status": status,
            "herd_immunity_threshold": round(1 - 1/r0_val, 3) if r0_val > 1 else 0
        }

        if sigma:
            result["sigma"] = sigma
            result["incubation_period_days"] = round(1/sigma, 1)
            result["model"] = "SEIR"
        else:
            result["model"] = "SIR"

        return result

    # ─── SIR Model Simulation ──────────────────────────────────
    def sir_model(self, population: int, initial_infected: int,
                  beta: float, gamma: float, days: int = 100) -> Dict:
        """
        Run SIR (Susceptible-Infected-Recovered) model simulation.
        dS/dt = -β × S × I / N
        dI/dt = β × S × I / N - γ × I
        dR/dt = γ × I
        """
        N = population
        S = population - initial_infected
        I = initial_infected
        R = 0
        dt = 0.1  # Time step

        trajectory = [{"day": 0, "S": S, "I": I, "R": R}]
        peak_I = I
        peak_day = 0

        for step in range(int(days / dt)):
            dS = -beta * S * I / N * dt
            dI = (beta * S * I / N - gamma * I) * dt
            dR = gamma * I * dt

            S = max(0, S + dS)
            I = max(0, I + dI)
            R = max(0, R + dR)

            day = (step + 1) * dt
            if abs(day - round(day)) < dt/2 and day == int(day):
                trajectory.append({"day": int(day), "S": int(S), "I": int(I), "R": int(R)})

            if I > peak_I:
                peak_I = I
                peak_day = day

        return {
            "type": "EPI_SIR",
            "population": N,
            "R0": round(beta/gamma, 3),
            "peak_infected": int(peak_I),
            "peak_day": int(peak_day),
            "total_infected": int(R),
            "attack_rate": round(R / N * 100, 2),
            "trajectory": trajectory[:days+1]  # One point per day
        }

    # ─── SEIR Model ────────────────────────────────────────────
    def seir_model(self, population: int, initial_exposed: int,
                   beta: float, gamma: float, sigma: float,
                   days: int = 100) -> Dict:
        """
        SEIR model with exposed (latent) compartment.
        dS/dt = -β × S × I / N
        dE/dt = β × S × I / N - σ × E
        dI/dt = σ × E - γ × I
        dR/dt = γ × I
        """
        N = population
        S = population - initial_exposed
        E = initial_exposed
        I = 0
        R = 0
        dt = 0.1

        trajectory = [{"day": 0, "S": S, "E": E, "I": I, "R": R}]
        peak_I = 0
        peak_day = 0

        for step in range(int(days / dt)):
            dS = -beta * S * I / N * dt
            dE = (beta * S * I / N - sigma * E) * dt
            dI = (sigma * E - gamma * I) * dt
            dR = gamma * I * dt

            S = max(0, S + dS)
            E = max(0, E + dE)
            I = max(0, I + dI)
            R = max(0, R + dR)

            day = (step + 1) * dt
            if abs(day - round(day)) < dt/2 and day == int(day):
                trajectory.append({"day": int(day), "S": int(S), "E": int(E), "I": int(I), "R": int(R)})

            if I > peak_I:
                peak_I = I
                peak_day = day

        return {
            "type": "EPI_SEIR",
            "population": N,
            "R0": round(beta/gamma, 3),
            "incubation_period": round(1/sigma, 1),
            "infectious_period": round(1/gamma, 1),
            "peak_infected": int(peak_I),
            "peak_day": int(peak_day),
            "total_infected": int(R),
            "attack_rate": round(R / N * 100, 2),
            "trajectory": trajectory[:days+1]
        }

    # ─── Incidence / Prevalence ────────────────────────────────
    def incidence_rate(self, new_cases: int, population_at_risk: int,
                       time_period_days: int = 365) -> Dict:
        """Calculate incidence rate per 100,000 per year."""
        rate = (new_cases / population_at_risk) * 100000 * (365 / time_period_days)
        return {
            "type": "EPI_INCIDENCE",
            "new_cases": new_cases,
            "population_at_risk": population_at_risk,
            "time_period_days": time_period_days,
            "incidence_per_100k_per_year": round(rate, 2)
        }

    def prevalence(self, total_cases: int, population: int) -> Dict:
        """Calculate point prevalence."""
        prev = total_cases / population * 100
        return {
            "type": "EPI_PREVALENCE",
            "total_cases": total_cases,
            "population": population,
            "prevalence_percent": round(prev, 4),
            "prevalence_per_100k": round(total_cases / population * 100000, 2)
        }

    # ─── Case Fatality Rate ────────────────────────────────────
    def cfr(self, deaths: int, confirmed_cases: int) -> Dict:
        """Case fatality rate."""
        rate = deaths / confirmed_cases * 100 if confirmed_cases > 0 else 0
        return {
            "type": "EPI_CFR",
            "deaths": deaths,
            "confirmed_cases": confirmed_cases,
            "cfr_percent": round(rate, 3)
        }

    # ─── Vaccination Coverage ──────────────────────────────────
    def herd_immunity(self, r0: float) -> Dict:
        """Calculate herd immunity threshold for a given R₀."""
        if r0 <= 1:
            return {"type": "EPI_HERD", "R0": r0, "threshold": 0,
                    "note": "R0 ≤ 1, epidemic will not sustain"}

        threshold = 1 - 1/r0
        return {
            "type": "EPI_HERD",
            "R0": r0,
            "threshold_fraction": round(threshold, 4),
            "threshold_percent": round(threshold * 100, 2),
            "interpretation": f"{round(threshold*100, 1)}% of population must be immune"
        }

    # ─── Known Disease Parameters ──────────────────────────────
    def disease_params(self, disease: str) -> Dict:
        """Get known R₀ and epidemiological parameters for common diseases."""
        diseases = {
            "measles":     {"R0": 15.0, "incubation_days": 10, "infectious_days": 8, "cfr": 0.2},
            "covid19":     {"R0": 3.0,  "incubation_days": 5,  "infectious_days": 10, "cfr": 1.0},
            "influenza":   {"R0": 1.5,  "incubation_days": 2,  "infectious_days": 5,  "cfr": 0.1},
            "ebola":       {"R0": 2.0,  "incubation_days": 11, "infectious_days": 7,  "cfr": 50.0},
            "pertussis":   {"R0": 12.0, "incubation_days": 9,  "infectious_days": 21, "cfr": 0.5},
            "smallpox":    {"R0": 5.0,  "incubation_days": 12, "infectious_days": 14, "cfr": 30.0},
            "chickenpox":  {"R0": 10.0, "incubation_days": 14, "infectious_days": 7,  "cfr": 0.001},
            "mumps":       {"R0": 7.0,  "incubation_days": 16, "infectious_days": 9,  "cfr": 0.01},
            "rubella":     {"R0": 6.0,  "incubation_days": 16, "infectious_days": 7,  "cfr": 0.01},
            "tuberculosis":{"R0": 3.5,  "incubation_days": 28, "infectious_days": 180,"cfr": 15.0},
            "malaria":     {"R0": 100.0,"incubation_days": 12, "infectious_days": 30, "cfr": 0.3},
        }

        if disease not in diseases:
            return {"error": f"Unknown disease: {disease}. Available: {list(diseases.keys())}"}

        d = diseases[disease]
        hit = 1 - 1/d["R0"]
        return {
            "type": "EPI_DISEASE",
            "disease": disease,
            **d,
            "herd_immunity_threshold": round(hit * 100, 1)
        }
