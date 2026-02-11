"""MOISSCode Medical Library  - core classes and module registry."""

import math
import numpy as np
from typing import Any, List, Dict
from dataclasses import dataclass
from .modules.med_scores import ClinicalScores
from .modules.med_research import ResearchPrivacy
from .modules.med_io import MedIO
from .modules.med_finance import FinancialSystem
from .modules.med_db import MedDatabase
from .modules.med_pk import PharmacokineticEngine
from .modules.med_biochem import BiochemEngine
from .modules.med_lab import LabEngine
from .modules.med_micro import MicroEngine
from .modules.med_genomics import GenomicsEngine
from .modules.med_epi import EpiEngine
from .modules.med_nutrition import NutritionEngine
from .modules.med_fhir import FHIRBridge

class KAE_Estimator:
    """Kalman-Autoencoder Estimator from the KAE Framework paper."""
    def __init__(self):
        self.R0 = 25.0
        self.Q0 = 0.1
        self.state = {'pos': 0.0, 'vel': 0.0}
        self.P = {'p11': 1.0, 'p22': 100.0}
        self.dt = 5.0  # minutes

    def update(self, measurement, reliability=1.0):
        if reliability < 0.0001: reliability = 0.0001
        R = self.R0 / reliability

        pred_pos = self.state['pos'] + self.state['vel'] * self.dt
        pred_vel = self.state['vel']

        p11_pred = self.P['p11'] + self.dt**2 * self.P['p22'] + self.Q0
        p22_pred = self.P['p22'] + self.Q0

        S = p11_pred + R
        K1 = p11_pred / S
        K2 = (self.P['p22'] * self.dt) / S

        innovation = measurement - pred_pos

        self.state['pos'] = pred_pos + K1 * innovation
        self.state['vel'] = pred_vel + K2 * innovation

        self.P['p11'] = (1 - K1) * p11_pred
        self.P['p22'] = (1 - K2 * self.dt) * p22_pred

        return self.state

class MOISS_Classifier:
    """
    Multi Organ Intervention State Space classifier.
    Uses PK engine for real drug timing when available.
    """
    def __init__(self, pk_engine: PharmacokineticEngine = None):
        self.pk = pk_engine or PharmacokineticEngine()

    def classify(self, t_crit_min: float, drug_name: str) -> str:
        profile = self.pk.get_profile(drug_name)
        t_effect = profile.onset_min if profile else 30.0

        delta_t = t_crit_min - t_effect

        if delta_t > t_effect:
            return "PROPHYLACTIC"
        elif 0 < delta_t <= t_effect:
            return "ON_TIME"
        elif -0.25 * t_effect < delta_t <= 0:
            return "PARTIAL"
        elif -0.5 * t_effect < delta_t <= -0.25 * t_effect:
            return "MARGINAL"
        elif -1.0 * t_effect < delta_t <= -0.5 * t_effect:
            return "FUTILE"
        else:
            return "TOO_LATE"

class StandardLibrary:
    """MOISSCode Medical Library  - all 13 modules."""

    def __init__(self):
        self.pk = PharmacokineticEngine()
        self.kae = KAE_Estimator()
        self.moiss = MOISS_Classifier(pk_engine=self.pk)
        self.scores = ClinicalScores()
        self.research = ResearchPrivacy()
        self.io = MedIO()
        self.finance = FinancialSystem()
        self.db = MedDatabase()
        self.biochem = BiochemEngine()
        self.lab = LabEngine()
        self.micro = MicroEngine()
        self.genomics = GenomicsEngine()
        self.epi = EpiEngine()
        self.nutrition = NutritionEngine()
        self.fhir = FHIRBridge()
