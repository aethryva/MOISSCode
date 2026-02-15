"""
MOISSCode custom exceptions for clinical-quality error messages.

All exceptions provide actionable context: what went wrong, why, and how to fix it.
"""


class MOISSCodeError(Exception):
    """Base exception for all MOISSCode errors."""
    pass


class DrugNotFoundError(MOISSCodeError):
    """Raised when a drug is not found in the PK registry."""

    def __init__(self, drug_name: str, available_drugs: list = None):
        self.drug_name = drug_name
        self.available_drugs = available_drugs or []
        suggestions = self._suggest(drug_name, self.available_drugs)
        msg = f"Drug '{drug_name}' not found in the PK registry."
        if suggestions:
            msg += f" Did you mean: {', '.join(suggestions)}?"
        msg += f" Use list_drugs() to see all {len(self.available_drugs)} available drugs."
        super().__init__(msg)

    @staticmethod
    def _suggest(name: str, candidates: list, max_results: int = 3) -> list:
        name_lower = name.lower()
        scored = []
        for c in candidates:
            c_lower = c.lower()
            if name_lower in c_lower or c_lower in name_lower:
                scored.append((0, c))
            elif name_lower[:3] == c_lower[:3]:
                scored.append((1, c))
        scored.sort(key=lambda x: x[0])
        return [s[1] for s in scored[:max_results]]


class DoseValidationError(MOISSCodeError):
    """Raised when a drug dose exceeds safety limits."""

    def __init__(self, drug_name: str, dose: float, unit: str,
                 max_dose: float = None, min_dose: float = None,
                 standard_dose: float = None, dose_unit: str = None):
        self.drug_name = drug_name
        self.dose = dose
        self.unit = unit
        parts = [f"{drug_name} dose of {dose}{unit}"]
        if max_dose and dose > max_dose:
            parts.append(f"exceeds maximum safe dose of {max_dose}{dose_unit or unit}")
        elif min_dose and dose < min_dose:
            parts.append(f"below minimum effective dose of {min_dose}{dose_unit or unit}")
        if standard_dose:
            parts.append(f"Standard dose: {standard_dose}{dose_unit or unit}")
        super().__init__(". ".join(parts) + ".")


class LabTestNotFoundError(MOISSCodeError):
    """Raised when a lab test name is not recognized."""

    def __init__(self, test_name: str, available_tests: list = None, panel: str = None):
        self.test_name = test_name
        suggestions = []
        if available_tests:
            name_lower = test_name.lower()
            for t in available_tests:
                if name_lower in t.lower() or t.lower() in name_lower:
                    suggestions.append(t)
        msg = f"Lab test '{test_name}' not found."
        if suggestions:
            msg += f" Did you mean: {', '.join(suggestions[:5])}?"
        if panel:
            msg += f" Available tests in {panel} panel: use list_tests('{panel}')."
        else:
            msg += " Use list_tests() to see all available tests."
        super().__init__(msg)


class PatientFieldError(MOISSCodeError):
    """Raised when required patient fields are missing for a calculation."""

    def __init__(self, score_name: str, missing_fields: list, available_fields: list = None):
        self.score_name = score_name
        self.missing_fields = missing_fields
        msg = f"{score_name} requires patient fields: {', '.join(missing_fields)}."
        if available_fields:
            msg += f" Patient has: {', '.join(available_fields)}."
        super().__init__(msg)


class OrganismNotFoundError(MOISSCodeError):
    """Raised when a microorganism is not found in the database."""

    def __init__(self, organism_name: str, available: list = None):
        msg = f"Organism '{organism_name}' not found in the microbiology database."
        if available:
            msg += f" Use get_organism() with one of: {', '.join(available[:10])}."
        super().__init__(msg)


class ICDCodeError(MOISSCodeError):
    """Raised when an ICD code lookup fails."""

    def __init__(self, code: str):
        super().__init__(
            f"ICD-10-CM code '{code}' not found. "
            f"Use search() to find codes by description, or lookup() with a valid code."
        )


class FHIRValidationError(MOISSCodeError):
    """Raised when FHIR resource generation fails validation."""
    pass
