"""Tests for Clinical Scores module (qSOFA, SOFA)."""

import pytest
from moisscode.modules.med_scores import ClinicalScores


class MockPatient:
    """Minimal mock patient for scoring tests."""
    def __init__(self, **kwargs):
        # qSOFA fields
        self.rr = kwargs.get('rr', 16)
        self.bp = kwargs.get('bp', 120)
        self.gcs = kwargs.get('gcs', 15)
        # SOFA fields
        self.pao2_fio2 = kwargs.get('pao2_fio2', 400)
        self.platelets = kwargs.get('platelets', 250)
        self.bilirubin = kwargs.get('bilirubin', 0.5)
        self.map = kwargs.get('map', 80)
        self.creatinine = kwargs.get('creatinine', 0.8)


# -- qSOFA -------------------------------------------------------------------

def test_qsofa_all_normal():
    p = MockPatient(rr=16, bp=120, gcs=15)
    assert ClinicalScores.qsofa(p) == 0


def test_qsofa_low_bp_only():
    p = MockPatient(rr=16, bp=90, gcs=15)
    assert ClinicalScores.qsofa(p) == 1


def test_qsofa_high_rr_only():
    p = MockPatient(rr=24, bp=120, gcs=15)
    assert ClinicalScores.qsofa(p) == 1


def test_qsofa_low_gcs_only():
    p = MockPatient(rr=16, bp=120, gcs=13)
    assert ClinicalScores.qsofa(p) == 1


def test_qsofa_all_abnormal():
    p = MockPatient(rr=24, bp=90, gcs=13)
    assert ClinicalScores.qsofa(p) == 3


def test_qsofa_two_criteria():
    p = MockPatient(rr=24, bp=90, gcs=15)
    assert ClinicalScores.qsofa(p) == 2


# -- SOFA --------------------------------------------------------------------

def test_sofa_all_normal():
    p = MockPatient(
        pao2_fio2=400, platelets=250, bilirubin=0.5,
        map=80, creatinine=0.8, gcs=15
    )
    score = ClinicalScores.sofa(p)
    assert score == 0


def test_sofa_severe_hypoxemia():
    p = MockPatient(
        pao2_fio2=80, platelets=250, bilirubin=0.5,
        map=80, creatinine=0.8, gcs=15
    )
    score = ClinicalScores.sofa(p)
    assert score >= 3  # PaO2/FiO2 < 100 = 4 points


def test_sofa_low_platelets():
    p = MockPatient(
        pao2_fio2=400, platelets=40, bilirubin=0.5,
        map=80, creatinine=0.8, gcs=15
    )
    score = ClinicalScores.sofa(p)
    assert score >= 3  # Platelets < 50 = 3 points


def test_sofa_high_bilirubin():
    p = MockPatient(
        pao2_fio2=400, platelets=250, bilirubin=8.0,
        map=80, creatinine=0.8, gcs=15
    )
    score = ClinicalScores.sofa(p)
    assert score >= 3  # Bilirubin >= 6 = 3 points, >= 12 = 4 points


def test_sofa_renal_failure():
    p = MockPatient(
        pao2_fio2=400, platelets=250, bilirubin=0.5,
        map=80, creatinine=5.5, gcs=15
    )
    score = ClinicalScores.sofa(p)
    assert score >= 4  # Creatinine >= 5 = 4 points


def test_sofa_worst_case():
    p = MockPatient(
        pao2_fio2=50, platelets=10, bilirubin=15.0,
        map=50, creatinine=6.0, gcs=3
    )
    score = ClinicalScores.sofa(p)
    # Maximum theoretical: 4+4+4+4+4+4 = 24
    assert score >= 12  # All components severely abnormal
