"""Medical Finance  - CPT billing and cost tracking for MOISSCode."""

from typing import Dict, List, Any
import datetime


class CPTDatabase:
    """CPT code reference database."""
    CODES = {
        "99291": {"desc": "Critical Care, first 30-74 min", "price": 285.00},
        "99292": {"desc": "Critical Care, addl 30 min", "price": 140.00},
        "36415": {"desc": "Collection of venous blood", "price": 10.00},
        "3000F": {"desc": "Sepsis evaluated (Tracking)", "price": 0.00},
        "J0897": {"desc": "Injection, Chemo", "price": 500.00},
    }


class FinancialSystem:
    """Automated billing ledger with CPT code validation."""

    def __init__(self):
        self.ledger: List[Dict[str, Any]] = []
        self.current_total = 0.0

    def bill(self, code: str, rationale: str = "") -> Dict:
        """Log a billable event. Returns the billing entry with running total."""
        if code not in CPTDatabase.CODES:
            price = 0.0
            desc = "Unknown"
        else:
            entry = CPTDatabase.CODES[code]
            price = entry["price"]
            desc = entry["desc"]

        timestamp = datetime.datetime.now().isoformat()

        self.ledger.append({
            "code": code,
            "desc": desc,
            "price": price,
            "rationale": rationale,
            "time": timestamp
        })

        self.current_total += price

        return {
            "type": "FINANCE_EVENT",
            "code": code,
            "desc": desc,
            "price": price,
            "rationale": rationale,
            "total": self.current_total
        }

    def get_total(self) -> float:
        return self.current_total

    def get_ledger(self) -> List[Dict[str, Any]]:
        return self.ledger
