"""Tests for med.biochem - Biochemistry Module."""
import pytest
from moisscode.modules.med_biochem import BiochemEngine


@pytest.fixture
def biochem():
    return BiochemEngine()


def test_michaelis_menten_half_vmax(biochem):
    enzymes = biochem.list_enzymes()
    enzyme_name = enzymes[0]
    enzyme = biochem.get_enzyme(enzyme_name)
    km = enzyme["km"]
    result = biochem.michaelis_menten(enzyme_name, km)
    expected = enzyme["vmax"] / 2
    assert abs(result["velocity"] - expected) < 0.01

def test_michaelis_menten_unknown_enzyme(biochem):
    result = biochem.michaelis_menten("fake_enzyme", 1.0)
    assert "error" in result

def test_lineweaver_burk(biochem):
    enzymes = biochem.list_enzymes()
    result = biochem.lineweaver_burk(enzymes[0], [0.5, 1.0, 2.0, 5.0])
    assert len(result) > 0

def test_competitive_inhibition_reduces_velocity(biochem):
    enzymes = biochem.list_enzymes()
    name = enzymes[0]
    v_normal = biochem.michaelis_menten(name, 1.0)["velocity"]
    ci_result = biochem.competitive_inhibition(name, 1.0, 5.0, ki=1.0)
    v_inhibited = ci_result["velocity_inhibited"]
    assert v_inhibited < v_normal

def test_get_enzyme_known(biochem):
    enzymes = biochem.list_enzymes()
    result = biochem.get_enzyme(enzymes[0])
    assert "name" in result
    assert "vmax" in result

def test_get_enzyme_unknown(biochem):
    result = biochem.get_enzyme("unknown_enzyme_xyz")
    assert result is None

def test_list_enzymes_nonempty(biochem):
    result = biochem.list_enzymes()
    assert len(result) > 0

def test_get_pathway_glycolysis(biochem):
    result = biochem.get_pathway("glycolysis")
    assert result is not None

def test_atp_yield_glycolysis(biochem):
    result = biochem.atp_yield("glycolysis")
    assert result["total_atp"] > 0

def test_ph_buffer(biochem):
    result = biochem.ph_buffer(pka=6.1, acid_conc=1.0, base_conc=20.0)
    if isinstance(result, (int, float)):
        assert 7.0 < result < 7.5
    else:
        assert 7.0 < result["ph"] < 7.5

def test_serum_osmolality_normal(biochem):
    result = biochem.serum_osmolality(sodium=140, glucose=100, bun=15)
    osm = result.get("osmolality", result.get("serum_osmolality", 0))
    assert 275 < osm < 300

def test_anion_gap_normal(biochem):
    result = biochem.anion_gap(sodium=140, chloride=104, bicarb=24)
    ag = result.get("anion_gap", 0)
    assert 8 < ag < 16
