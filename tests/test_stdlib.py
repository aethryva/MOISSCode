"""Tests for StandardLibrary integration and moisscode package imports."""
import pytest


def test_standard_library_has_all_modules():
    from moisscode import StandardLibrary
    lib = StandardLibrary()
    assert hasattr(lib, 'scores')
    assert hasattr(lib, 'pk')
    assert hasattr(lib, 'lab')
    assert hasattr(lib, 'micro')
    assert hasattr(lib, 'genomics')
    assert hasattr(lib, 'biochem')
    assert hasattr(lib, 'epi')
    assert hasattr(lib, 'nutrition')
    assert hasattr(lib, 'fhir')
    assert hasattr(lib, 'glucose')
    assert hasattr(lib, 'chem')
    assert hasattr(lib, 'signal')
    assert hasattr(lib, 'icd')
    assert hasattr(lib, 'db')
    assert hasattr(lib, 'io')
    assert hasattr(lib, 'finance')
    assert hasattr(lib, 'research')
    assert hasattr(lib, 'papers')
    assert hasattr(lib, 'kae')
    assert hasattr(lib, 'moiss')


def test_direct_module_import():
    from moisscode.modules import PharmacokineticEngine
    pk = PharmacokineticEngine()
    assert len(pk.list_drugs()) > 0


def test_top_level_import():
    from moisscode import PharmacokineticEngine
    pk = PharmacokineticEngine()
    assert len(pk.list_drugs()) > 0


def test_version_exists():
    from moisscode import __version__
    assert __version__ is not None
    assert len(__version__) > 0


def test_patient_import():
    from moisscode import Patient
    p = Patient(bp=120, hr=80, rr=16, gcs=15)
    assert p.bp == 120


def test_kae_estimator():
    from moisscode import StandardLibrary
    lib = StandardLibrary()
    result = lib.kae.update(100.0, reliability=0.9)
    assert "pos" in result
    assert "vel" in result


def test_moiss_classifier():
    from moisscode import StandardLibrary
    lib = StandardLibrary()
    classification = lib.moiss.classify(t_crit_min=60, drug_name="Vancomycin")
    valid = {"PROPHYLACTIC", "ON_TIME", "PARTIAL",
             "MARGINAL", "FUTILE", "TOO_LATE"}
    assert classification in valid


def test_scores_qsofa_via_stdlib():
    from moisscode import StandardLibrary, Patient
    lib = StandardLibrary()
    p = Patient(bp=85, hr=110, rr=24, gcs=14)
    score = lib.scores.qsofa(p)
    assert score >= 2
