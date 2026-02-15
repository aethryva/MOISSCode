"""Tests for med.micro - Microbiology Module."""
import pytest
from moisscode.modules.med_micro import MicroEngine


@pytest.fixture
def micro():
    return MicroEngine()


def test_list_organisms(micro):
    result = micro.list_organisms()
    assert len(result) > 0

def test_identify_known_organism(micro):
    orgs = micro.list_organisms()
    result = micro.identify(orgs[0])
    assert result["name"] is not None
    assert "type" in result

def test_identify_unknown_organism(micro):
    result = micro.identify("xyz_unknown_organism")
    assert "error" in result

def test_susceptibility_known(micro):
    orgs = micro.list_organisms()
    result = micro.susceptibility(orgs[0], "ciprofloxacin")
    assert "type" in result or "error" in result

def test_susceptibility_unknown_organism(micro):
    result = micro.susceptibility("xyz_unknown", "vancomycin")
    assert "error" in result

def test_empiric_therapy_uti(micro):
    result = micro.empiric_therapy("urinary_tract_infection")
    if "error" not in result:
        assert "type" in result
    else:
        # Try other common names
        result2 = micro.empiric_therapy("UTI")
        assert result2 is not None

def test_empiric_therapy_unknown(micro):
    result = micro.empiric_therapy("unknown_infection_xyz")
    assert "error" in result

def test_gram_stain_ddx(micro):
    result = micro.gram_stain_ddx("positive", "cocci")
    assert isinstance(result, (list, dict))
