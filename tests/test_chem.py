"""Tests for med.chem - Medicinal Chemistry Module."""
import pytest
from moisscode.modules.med_chem import ChemEngine


@pytest.fixture
def chem():
    return ChemEngine()


def test_molecular_weight_aspirin():
    result = ChemEngine.molecular_weight("C9H8O4")
    assert 178 < result["molecular_weight"] < 182

def test_molecular_weight_water():
    result = ChemEngine.molecular_weight("H2O")
    assert 17 < result["molecular_weight"] < 19

def test_lipinski_drug_like():
    result = ChemEngine.lipinski_check(mw=300, logp=2.0, hbd=2, hba=5)
    assert result["drug_like"] is True
    assert result["violations"] == 0

def test_lipinski_not_drug_like():
    result = ChemEngine.lipinski_check(mw=600, logp=7.0, hbd=8, hba=15)
    assert result["drug_like"] is False

def test_bcs_classify():
    result = ChemEngine.bcs_classify(solubility="high", permeability="high")
    assert result["bcs_class"] == "I"

def test_bcs_class_4():
    result = ChemEngine.bcs_classify(solubility="low", permeability="low")
    assert result["bcs_class"] == "IV"

def test_admet_screen():
    result = ChemEngine.admet_screen(mw=350, logp=2.5, psa=80, rotatable_bonds=5)
    assert "assessment" in result

def test_lookup_known(chem):
    compounds = chem.list_compounds()
    # list_compounds returns list of dicts with 'name' key
    name = compounds[0]["name"] if isinstance(compounds[0], dict) else compounds[0]
    result = chem.lookup(name)
    assert "name" in result

def test_lookup_unknown(chem):
    result = chem.lookup("nonexistent_compound_xyz")
    assert "error" in result

def test_list_compounds(chem):
    result = chem.list_compounds()
    assert len(result) > 0

def test_search_by_target(chem):
    result = chem.search_by_target("COX")
    assert isinstance(result, (list, dict))

def test_search_by_class(chem):
    result = chem.search_by_class("analgesic")
    assert isinstance(result, (list, dict))

def test_screen_compound(chem):
    compounds = chem.list_compounds()
    name = compounds[0]["name"] if isinstance(compounds[0], dict) else compounds[0]
    result = chem.screen_compound(name)
    assert "lipinski" in result
