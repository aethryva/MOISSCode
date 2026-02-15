"""Tests for med.finance - CPT Billing Module."""
import pytest
from moisscode.modules.med_finance import FinancialSystem


@pytest.fixture
def finance():
    return FinancialSystem()


def test_bill_known_code(finance):
    result = finance.bill("99291", "Critical care eval")
    assert result["price"] == 285.00
    assert result["code"] == "99291"

def test_bill_unknown_code(finance):
    result = finance.bill("XXXXX")
    assert result["price"] == 0.0

def test_bill_accumulates_total(finance):
    finance.bill("99291")
    finance.bill("99292")
    assert finance.get_total() == 285.00 + 140.00

def test_ledger_tracks_entries(finance):
    finance.bill("99291")
    finance.bill("80053")
    ledger = finance.get_ledger()
    assert len(ledger) == 2

def test_ledger_empty_initially(finance):
    assert finance.get_total() == 0.0
    assert len(finance.get_ledger()) == 0
