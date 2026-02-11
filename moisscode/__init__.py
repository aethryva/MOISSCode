"""
MOISSCode  - Multi Organ Intervention State Space Code.

A domain-specific language for medical orchestration, clinical
decision support, and biotech workflow automation.
"""

from moisscode.version import __version__
from moisscode.lexer import MOISSCodeLexer
from moisscode.parser import MOISSCodeParser
from moisscode.interpreter import MOISSCodeInterpreter
from moisscode.typesystem import Patient, TypeChecker
from moisscode.stdlib import StandardLibrary

__all__ = [
    '__version__',
    'MOISSCodeLexer',
    'MOISSCodeParser',
    'MOISSCodeInterpreter',
    'Patient',
    'TypeChecker',
    'StandardLibrary',
]
