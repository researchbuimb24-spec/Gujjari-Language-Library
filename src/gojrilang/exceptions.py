"""Custom exceptions for the GojriLang toolkit.

All exceptions inherit from GojriLangError for consistent exception handling.
"""

from __future__ import annotations


class GojriLangError(Exception):
    """Base exception for all errors raised by the GojriLang library."""

    pass


class WordNotFoundError(GojriLangError):
    """Raised when a requested word is not found in the verified dictionary."""

    def __init__(self, word: str, details: str | None = None) -> None:
        message = f"Word '{word}' was not found in the verified Gojri dictionary."
        if details:
            message += f" Details: {details}"
        super().__init__(message)
        self.word = word


class UnsupportedScriptError(GojriLangError):
    """Raised when an operation is requested on an unrecognised or unsupported script."""

    def __init__(self, script: str, supported: list[str] | None = None) -> None:
        msg = f"Script '{script}' is unsupported or unrecognised."
        if supported:
            msg += f" Supported scripts are: {', '.join(supported)}."
        super().__init__(msg)
        self.script = script
        self.supported = supported or []


class UnsupportedTransliterationError(GojriLangError):
    """Raised when transliteration between two requested scripts has not been validated."""

    def __init__(self, source_script: str, target_script: str, reason: str | None = None) -> None:
        msg = (
            f"Transliteration from '{source_script}' to '{target_script}' has not been "
            "validated against authentic Gojri orthographic standards."
        )
        if reason:
            msg += f" {reason}"
        super().__init__(msg)
        self.source_script = source_script
        self.target_script = target_script


class RuleNotFoundError(GojriLangError):
    """Raised when a specified grammar rule identifier is not found."""

    def __init__(self, rule_id: str) -> None:
        super().__init__(f"Grammar rule with ID '{rule_id}' was not found.")
        self.rule_id = rule_id


class DataSchemaValidationError(GojriLangError):
    """Raised when an internal dataset violates the required schema."""

    def __init__(self, dataset_name: str, errors: list[str]) -> None:
        super().__init__(
            f"Data schema validation failed for '{dataset_name}': {'; '.join(errors)}"
        )
        self.dataset_name = dataset_name
        self.errors = errors


class InvalidDialectError(GojriLangError):
    """Raised when an unsupported or unknown dialect variant is specified."""

    def __init__(self, dialect: str, supported: list[str] | None = None) -> None:
        msg = f"Dialect '{dialect}' is unrecognised."
        if supported:
            msg += f" Recognized dialects/regions: {', '.join(supported)}."
        super().__init__(msg)
        self.dialect = dialect
        self.supported = supported or []


class DialectProfileNotFoundError(GojriLangError):
    """Raised when a requested dialect profile ID does not exist."""

    def __init__(self, profile_id: str) -> None:
        super().__init__(f"Dialect profile '{profile_id}' was not found.")
        self.profile_id = profile_id


class BookNotFoundError(GojriLangError):
    """Raised when a requested literature collection or book ID does not exist."""

    def __init__(self, book_id: str) -> None:
        super().__init__(f"Book with ID '{book_id}' was not found in the literature collection.")
        self.book_id = book_id


class UnsupportedNumberRangeError(GojriLangError):
    """Raised when a number is outside the authenticated Gojri counting range."""

    def __init__(self, number: int, min_val: int = 0, max_val: int = 100) -> None:
        super().__init__(
            f"Number {number} is outside the verified Gojri counting range [{min_val}-{max_val}]. "
            "Higher numbers require verified dialectal and multiplicative counting documentation."
        )
        self.number = number
        self.min_val = min_val
        self.max_val = max_val


class DatasetValidationError(GojriLangError):
    """Raised when a dataset file fails schema validation."""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []

