"""Tests for med.icd - ICD-10-CM Coding Module."""
import pytest
from moisscode.modules.med_icd import ICDEngine


@pytest.fixture
def icd():
    return ICDEngine()


def test_lookup_known_code(icd):
    result = icd.lookup("E11.9")
    assert "description" in result

def test_lookup_unknown_code(icd):
    result = icd.lookup("ZZZ99.99")
    assert "error" in result

def test_search_diabetes(icd):
    result = icd.search("diabetes")
    assert "results" in result
    assert len(result["results"]) > 0

def test_search_results_have_codes(icd):
    result = icd.search("sepsis")
    for r in result["results"]:
        assert "code" in r

def test_category(icd):
    result = icd.category("E11.9")
    assert "category" in result

def test_related(icd):
    result = icd.related("E11.9")
    assert isinstance(result, dict)
    assert "related_codes" in result or "code" in result

def test_drg_lookup(icd):
    result = icd.drg_lookup(["A41.9"])
    assert result is not None

def test_snomed_to_icd(icd):
    result = icd.snomed_to_icd("73211009")
    assert result is not None

def test_validate_codes(icd):
    result = icd.validate_codes(["E11.9", "ZZZ99"])
    assert "results" in result or isinstance(result, list) or isinstance(result, dict)

def test_list_codes(icd):
    result = icd.list_codes()
    assert len(result) > 0
