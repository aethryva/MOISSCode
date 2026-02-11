from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Patient:
    name: str = "Unknown"
    age: int = 0
    weight: float = 0.0
    sex: str = "U"
    bp: float = 120.0       # Systolic blood pressure (mmHg)
    hr: float = 80.0        # Heart rate (bpm)
    rr: float = 16.0        # Respiratory rate
    temp: float = 37.0      # Temperature (°C)
    spo2: float = 98.0      # O2 saturation (%)
    gcs: int = 15           # Glasgow Coma Scale
    lactate: float = 1.0    # Lactate (mmol/L)

    def __repr__(self):
        return f"Patient(name={self.name}, age={self.age}, bp={self.bp}, hr={self.hr})"

class MedicalType:
    def __init__(self, name: str, unit: Optional[str] = None):
        self.name = name
        self.unit = unit

    def __repr__(self):
        if self.unit:
            return f"{self.name}<{self.unit}>"
        return self.name

class UnitSystem:
    # Map each unit to its dimension category
    DIMENSIONS = {
        'mg':   'mass',
        'mcg':  'mass',
        'g':    'mass',
        'kg':   'mass',
        'L':    'volume',
        'mL':   'volume',
        'mmHg': 'pressure',
        'mmol': 'amount',
        'mol':  'amount',
        'IU':   'activity',
        'min':  'time',
        'hr':   'time',
    }

    CONVERSIONS = {
        ('mcg', 'mg'):  0.001,
        ('mg', 'mcg'):  1000.0,
        ('mg', 'g'):    0.001,
        ('g', 'mg'):    1000.0,
        ('g', 'kg'):    0.001,
        ('kg', 'g'):    1000.0,
        ('mL', 'L'):    0.001,
        ('L', 'mL'):    1000.0,
        ('min', 'hr'):  1/60,
        ('hr', 'min'):  60.0,
    }

    @staticmethod
    def get_dimension(unit: str) -> Optional[str]:
        """Get the dimension category for a unit (e.g., 'mg' -> 'mass')."""
        # Handle compound units like mcg/kg/min by checking the base
        base = unit.split('/')[0]
        return UnitSystem.DIMENSIONS.get(base)

    @staticmethod
    def are_compatible(unit1: str, unit2: str) -> bool:
        """Check if two units are compatible (same dimension)."""
        if unit1 == unit2:
            return True

        dim1 = UnitSystem.get_dimension(unit1)
        dim2 = UnitSystem.get_dimension(unit2)

        if dim1 is None or dim2 is None:
            # Unknown units — allow for forward-compatibility
            return True

        return dim1 == dim2

    @staticmethod
    def convert(value: float, from_unit: str, to_unit: str) -> float:
        """Convert a value between compatible units."""
        if from_unit == to_unit:
            return value
        key = (from_unit, to_unit)
        if key in UnitSystem.CONVERSIONS:
            return value * UnitSystem.CONVERSIONS[key]
        raise ValueError(f"Cannot convert from {from_unit} to {to_unit}")

class TypeChecker:
    def __init__(self):
        self.symbol_table: Dict[str, MedicalType] = {}

    def declare_variable(self, name: str, type_name: str, unit: str = None):
        self.symbol_table[name] = MedicalType(type_name, unit)

    def check_compatibility(self, type1: MedicalType, type2: MedicalType) -> bool:
        if type1.name != type2.name:
            # Allow int/float interchange
            if type1.name in ['int', 'float'] and type2.name in ['int', 'float']:
                return True
            raise TypeError(f"Incompatible types: {type1} vs {type2}")

        if type1.unit and type2.unit:
            if not UnitSystem.are_compatible(type1.unit, type2.unit):
                raise TypeError(
                    f"Unit mismatch: cannot compare {type1.unit} ({UnitSystem.get_dimension(type1.unit)}) "
                    f"with {type2.unit} ({UnitSystem.get_dimension(type2.unit)})"
                )
        return True

if __name__ == "__main__":
    # Test unit checking
    print("=== Unit Compatibility Tests ===")

    tests = [
        ("mg", "mcg", True),    # Both mass
        ("mg", "mL", False),    # mass vs volume
        ("mmHg", "mg", False),  # pressure vs mass
        ("mg", "g", True),      # Both mass
        ("L", "mL", True),      # Both volume
        ("min", "hr", True),    # Both time
    ]

    for u1, u2, expected in tests:
        result = UnitSystem.are_compatible(u1, u2)
        status = "✓" if result == expected else "✗ FAIL"
        print(f"  {status}  {u1} vs {u2} -> {result} (expected {expected})")

    # Test conversion
    print("\n=== Conversion Tests ===")
    print(f"  1000 mcg -> {UnitSystem.convert(1000, 'mcg', 'mg')} mg")
    print(f"  2 g -> {UnitSystem.convert(2, 'g', 'mg')} mg")
    print(f"  500 mL -> {UnitSystem.convert(500, 'mL', 'L')} L")
