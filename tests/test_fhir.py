"""Tests for med.fhir - FHIR R4 Bridge Module."""
import json
import pytest
from moisscode.modules.med_fhir import FHIRBridge
from moisscode.typesystem import Patient


@pytest.fixture
def fhir():
    return FHIRBridge()


@pytest.fixture
def patient():
    return Patient(bp=120, hr=80, rr=16, gcs=15, sex="M", age=45)


def test_to_fhir_returns_bundle(patient):
    result = FHIRBridge.to_fhir(patient)
    assert result["resourceType"] == "Bundle"
    assert result["type"] == "collection"

def test_to_fhir_has_entries(patient):
    result = FHIRBridge.to_fhir(patient)
    assert len(result["entry"]) > 0

def test_from_fhir_round_trip(patient):
    bundle = FHIRBridge.to_fhir(patient)
    result = FHIRBridge.from_fhir(bundle)
    assert "bp" in result or "hr" in result

def test_search_url():
    url = FHIRBridge.search_url("https://fhir.example.com/r4", "Patient",
                                 {"family": "Smith"})
    assert "Patient" in url
    assert "family=Smith" in url

def test_medication_request():
    result = FHIRBridge.medication_request("Vancomycin", 1000, "mg")
    assert result["resourceType"] == "MedicationRequest"
    assert "Vancomycin" in str(result)

def test_condition():
    result = FHIRBridge.condition("A41.9", "Sepsis, unspecified")
    assert result["resourceType"] == "Condition"

def test_to_json():
    resource = {"resourceType": "Patient", "id": "1"}
    result = FHIRBridge.to_json(resource)
    parsed = json.loads(result)
    assert parsed["resourceType"] == "Patient"
