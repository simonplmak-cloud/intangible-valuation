"""Logging configuration for intangible valuation library."""

from __future__ import annotations

import logging

logger = logging.getLogger("intangible_valuation")

if not logger.handlers:
    handler = logging.NullHandler()
    logger.addHandler(handler)
