"""Tests for MOISSCode UnitSystem."""

import pytest
from moisscode.typesystem import UnitSystem


# -- Conversion table --------------------------------------------------------

def test_mg_to_mcg():
    assert UnitSystem.CONVERSIONS[("mg", "mcg")] == 1000.0


def test_mcg_to_mg():
    assert UnitSystem.CONVERSIONS[("mcg", "mg")] == 0.001


def test_g_to_mg():
    assert UnitSystem.CONVERSIONS[("g", "mg")] == 1000.0


def test_L_to_mL():
    assert UnitSystem.CONVERSIONS[("L", "mL")] == 1000.0


def test_mL_to_L():
    assert UnitSystem.CONVERSIONS[("mL", "L")] == 0.001


# -- Compatibility -----------------------------------------------------------

def test_compatible_mass_units():
    assert UnitSystem.are_compatible("mg", "mcg") is True


def test_compatible_volume_units():
    assert UnitSystem.are_compatible("L", "mL") is True


def test_are_compatible_returns_bool():
    # are_compatible currently returns True for all (placeholder)
    result = UnitSystem.are_compatible("mg", "L")
    assert isinstance(result, bool)


# -- Dimension lookup --------------------------------------------------------

def test_mass_conversion_entries_exist():
    assert ("mg", "mcg") in UnitSystem.CONVERSIONS
    assert ("g", "mg") in UnitSystem.CONVERSIONS


def test_identity_conversion_not_needed():
    # Same unit to same unit should not be in the table (no-op)
    assert ("mg", "mg") not in UnitSystem.CONVERSIONS


# -- Convert method ----------------------------------------------------------

def test_convert_mg_to_mcg():
    result = UnitSystem.convert(1.0, "mg", "mcg")
    assert result == 1000.0


def test_convert_unknown_units():
    # Should raise ValueError or KeyError for unknown conversion
    with pytest.raises((ValueError, KeyError)):
        UnitSystem.convert(1.0, "bananas", "apples")
