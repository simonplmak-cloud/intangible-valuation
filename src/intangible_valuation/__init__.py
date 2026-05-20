"""Intangible Asset Valuation Platform.

Complete implementation of all valuation methodologies from
"Intangible Asset Valuation" (Ascent Partners, 2025).
"""

from importlib.metadata import version

from intangible_valuation.exceptions import (
    CalculationError,
    ConfigurationError,
    InputValidationError,
    ValuationError,
)
from intangible_valuation.logging_config import logger

__version__ = version("intangible-valuation")

__all__ = [
    "CalculationError",
    "ConfigurationError",
    "InputValidationError",
    "ValuationError",
    "logger",
]
