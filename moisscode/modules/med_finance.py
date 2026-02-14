"""Medical Finance  - CPT billing and cost tracking for MOISSCode."""

from typing import Dict, List, Any
import datetime


class CPTDatabase:
    """CPT code reference database."""
    CODES = {
        # ─── Critical Care ───
        "99291": {"desc": "Critical Care, first 30-74 min", "price": 285.00},
        "99292": {"desc": "Critical Care, addl 30 min", "price": 140.00},

        # ─── E&M Office Visits ───
        "99211": {"desc": "Office Visit, minimal", "price": 25.00},
        "99212": {"desc": "Office Visit, focused", "price": 45.00},
        "99213": {"desc": "Office Visit, expanded", "price": 75.00},
        "99214": {"desc": "Office Visit, detailed", "price": 110.00},
        "99215": {"desc": "Office Visit, comprehensive", "price": 150.00},

        # ─── ED Visits ───
        "99281": {"desc": "ED Visit, self-limited problem", "price": 50.00},
        "99282": {"desc": "ED Visit, low-moderate severity", "price": 95.00},
        "99283": {"desc": "ED Visit, moderate severity", "price": 150.00},
        "99284": {"desc": "ED Visit, high severity", "price": 250.00},
        "99285": {"desc": "ED Visit, life-threatening", "price": 350.00},

        # ─── Lab & Blood ───
        "36415": {"desc": "Collection of venous blood", "price": 10.00},
        "80053": {"desc": "Comprehensive Metabolic Panel", "price": 35.00},
        "85025": {"desc": "Complete Blood Count (CBC) with diff", "price": 15.00},
        "85610": {"desc": "Prothrombin Time (PT)", "price": 12.00},
        "86900": {"desc": "Blood typing ABO", "price": 10.00},
        "87070": {"desc": "Culture, bacterial, any source", "price": 20.00},
        "87086": {"desc": "Urine culture, quantitative", "price": 18.00},
        "83036": {"desc": "Hemoglobin A1c", "price": 20.00},

        # ─── Imaging ───
        "71046": {"desc": "Chest X-Ray, 2 views", "price": 55.00},
        "74176": {"desc": "CT Abdomen/Pelvis with contrast", "price": 450.00},
        "70553": {"desc": "MRI Brain with/without contrast", "price": 1200.00},
        "93306": {"desc": "Echocardiogram, complete", "price": 350.00},

        # ─── Procedures ───
        "31500": {"desc": "Intubation, endotracheal", "price": 220.00},
        "32551": {"desc": "Chest tube insertion", "price": 400.00},
        "36556": {"desc": "Central venous catheter insertion", "price": 500.00},
        "36620": {"desc": "Arterial line placement", "price": 200.00},
        "49083": {"desc": "Paracentesis, diagnostic/therapeutic", "price": 350.00},
        "62270": {"desc": "Lumbar puncture, diagnostic", "price": 300.00},

        # ─── Respiratory Therapy ───
        "94002": {"desc": "Ventilator management, first day", "price": 180.00},
        "94003": {"desc": "Ventilator management, subsequent", "price": 120.00},

        # ─── Tracking / Quality Measures ───
        "3000F": {"desc": "Sepsis evaluated (Tracking)", "price": 0.00},

        # ─── Chemotherapy / Infusion ───
        "J0897": {"desc": "Injection, Chemo", "price": 500.00},
        "96365": {"desc": "IV infusion, initial, up to 1 hr", "price": 150.00},
        "96374": {"desc": "IV push, single substance", "price": 60.00},

        # ─── Dialysis ───
        "90935": {"desc": "Hemodialysis, single session", "price": 250.00},
        "90945": {"desc": "Dialysis procedure other than hemodialysis", "price": 200.00},
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
