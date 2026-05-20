"""Custom exceptions for intangible valuation library."""

from __future__ import annotations


class ValuationError(Exception):
    """Base exception for all valuation errors."""


class InputValidationError(ValuationError):
    """Raised when input parameters fail validation."""


class CalculationError(ValuationError):
    """Raised when a valuation calculation fails."""


class ConfigurationError(ValuationError):
    """Raised when module configuration is invalid."""
