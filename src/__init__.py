"""Intangible Asset Valuation Platform.

Complete implementation of all valuation methodologies from
"Intangible Asset Valuation" (Ascent Partners, 2025).
"""

from importlib.metadata import version

from src.exceptions import (
    CalculationError,
    ConfigurationError,
    InputValidationError,
    ValuationError,
)
from src.logging_config import logger

__version__ = version("intangible-valuation")

__all__ = [
    "CalculationError",
    "ConfigurationError",
    "InputValidationError",
    "ValuationError",
    "logger",
]
