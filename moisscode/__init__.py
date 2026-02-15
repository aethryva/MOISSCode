"""
MOISSCode - Multi Organ Intervention State Space Code.

A domain-specific language for clinical decision support and
biotech workflow automation.

Quick Start::

    from moisscode import StandardLibrary, Patient

    lib = StandardLibrary()
    p = Patient(bp=85, hr=110, rr=24, gcs=14, lactate=3.2, sex='M')
    score = lib.scores.qsofa(p)

Direct module imports::

    from moisscode.modules import PharmacokineticEngine, LabEngine
    pk = PharmacokineticEngine()
    lab = LabEngine()
"""

from moisscode.version import __version__
from moisscode.lexer import MOISSCodeLexer
from moisscode.parser import MOISSCodeParser
from moisscode.interpreter import MOISSCodeInterpreter
from moisscode.typesystem import Patient, TypeChecker
from moisscode.stdlib import StandardLibrary
from moisscode.exceptions import (
    MOISSCodeError,
    DrugNotFoundError,
    DoseValidationError,
    LabTestNotFoundError,
    PatientFieldError,
    OrganismNotFoundError,
    ICDCodeError,
    FHIRValidationError,
)

# Re-export module classes for convenience
from moisscode.modules import (
    ClinicalScores,
    PharmacokineticEngine,
    DrugProfile,
    LabEngine,
    MicroEngine,
    GenomicsEngine,
    BiochemEngine,
    EpiEngine,
    NutritionEngine,
    FHIRBridge,
    GlucoseEngine,
    ChemEngine,
    SignalEngine,
    ICDEngine,
    MedDatabase,
    MedIO,
    FinancialSystem,
    ResearchPrivacy,
    PapersEngine,
)

__all__ = [
    '__version__',
    'MOISSCodeLexer',
    'MOISSCodeParser',
    'MOISSCodeInterpreter',
    'Patient',
    'TypeChecker',
    'StandardLibrary',
    # Module classes
    'ClinicalScores',
    'PharmacokineticEngine',
    'DrugProfile',
    'LabEngine',
    'MicroEngine',
    'GenomicsEngine',
    'BiochemEngine',
    'EpiEngine',
    'NutritionEngine',
    'FHIRBridge',
    'GlucoseEngine',
    'ChemEngine',
    'SignalEngine',
    'ICDEngine',
    'MedDatabase',
    'MedIO',
    'FinancialSystem',
    'ResearchPrivacy',
    'PapersEngine',
]
