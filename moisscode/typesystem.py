"""
MOISSCode Type System  - Patient, units, and type checking.
"""

from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Patient:
    """
    Extensible patient model.

    Core vitals are always available with clinical defaults.
    Additional fields can be set via the ``extra`` dict or keyword arguments
    and accessed transparently as attributes.

    Examples:
        # Using core fields
        p = Patient(name="John", age=55, bp=85)

        # Adding custom fields
        p = Patient(creatinine=1.4, bilirubin=3.2, platelets=90)
        print(p.creatinine)  # 1.4

        # Setting fields dynamically
        p.set_field("pao2_fio2", 180)
        print(p.pao2_fio2)  # 180
    """
    # ── Core vitals (always present) ────────────────────────
    name: str = "Unknown"
    age: int = 0
    weight: float = 0.0
    sex: str = "U"
    bp: float = 120.0           # Systolic blood pressure (mmHg)
    diastolic_bp: float = 80.0  # Diastolic blood pressure (mmHg)
    hr: float = 80.0            # Heart rate (bpm)
    rr: float = 16.0            # Respiratory rate
    temp: float = 37.0          # Temperature (°C)
    spo2: float = 98.0          # O2 saturation (%)
    gcs: int = 15               # Glasgow Coma Scale
    lactate: float = 1.0        # Lactate (mmol/L)
    height: float = 170.0       # Height (cm)

    # ── Extended attributes (any additional clinical data) ──
    extra: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, **kwargs):
        """Initialize Patient with core fields and any extra fields.

        Any keyword argument matching a core field is set normally.
        All other keyword arguments are stored in ``extra`` and accessible
        as regular attributes.
        """
        core_fields = {
            'name', 'age', 'weight', 'sex', 'bp', 'diastolic_bp',
            'hr', 'rr', 'temp', 'spo2', 'gcs', 'lactate', 'height',
        }

        # Set defaults
        self.name = "Unknown"
        self.age = 0
        self.weight = 0.0
        self.sex = "U"
        self.bp = 120.0
        self.diastolic_bp = 80.0
        self.hr = 80.0
        self.rr = 16.0
        self.temp = 37.0
        self.spo2 = 98.0
        self.gcs = 15
        self.lactate = 1.0
        self.height = 170.0
        self.extra = {}

        for key, value in kwargs.items():
            if key in core_fields:
                object.__setattr__(self, key, value)
            else:
                self.extra[key] = value

    def __getattr__(self, name: str) -> Any:
        """Transparent access to extended fields via self.extra."""
        if name == 'extra':
            raise AttributeError(name)
        try:
            return self.extra[name]
        except KeyError:
            raise AttributeError(
                f"Patient has no field '{name}'. "
                f"Core fields: name, age, weight, sex, bp, diastolic_bp, hr, rr, temp, spo2, gcs, lactate, height. "
                f"Extra fields set: {list(self.extra.keys())}"
            )

    def set_field(self, name: str, value: Any):
        """Set any field (core or custom) on the patient."""
        core_fields = {
            'name', 'age', 'weight', 'sex', 'bp', 'diastolic_bp',
            'hr', 'rr', 'temp', 'spo2', 'gcs', 'lactate', 'height',
        }
        if name in core_fields:
            object.__setattr__(self, name, value)
        else:
            self.extra[name] = value

    def has_field(self, name: str) -> bool:
        """Check if a field exists (core or custom)."""
        return hasattr(self, name) or name in self.extra

    @property
    def map(self) -> float:
        """Mean Arterial Pressure  - computed from bp and diastolic_bp."""
        return self.diastolic_bp + (self.bp - self.diastolic_bp) / 3

    @property
    def bmi(self) -> float:
        """Body Mass Index  - computed from weight (kg) and height (cm)."""
        if self.height <= 0:
            return 0.0
        height_m = self.height / 100
        return round(self.weight / (height_m ** 2), 1)

    def all_fields(self) -> Dict[str, Any]:
        """Return all fields (core + extra) as a flat dict."""
        result = {
            'name': self.name, 'age': self.age, 'weight': self.weight,
            'sex': self.sex, 'bp': self.bp, 'diastolic_bp': self.diastolic_bp,
            'hr': self.hr, 'rr': self.rr, 'temp': self.temp,
            'spo2': self.spo2, 'gcs': self.gcs, 'lactate': self.lactate,
            'height': self.height,
        }
        result.update(self.extra)
        return result

    def __repr__(self):
        extras = f", +{len(self.extra)} extra" if self.extra else ""
        return f"Patient(name={self.name}, age={self.age}, bp={self.bp}, hr={self.hr}{extras})"


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
            # Unknown units  - allow for forward-compatibility
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
