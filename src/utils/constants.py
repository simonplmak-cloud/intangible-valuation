"""Industry default rates and constants for valuation calculations."""

from typing import Final

# Default rates
DEFAULT_RISK_FREE_RATE: Final[float] = 0.04
DEFAULT_EQUITY_RISK_PREMIUM: Final[float] = 0.06
DEFAULT_TAX_RATE: Final[float] = 0.25
DEFAULT_MARKET_RETURN: Final[float] = DEFAULT_RISK_FREE_RATE + DEFAULT_EQUITY_RISK_PREMIUM  # 0.10

# Industry-specific discount rate ranges (WACC ranges by sector)
INDUSTRY_DISCOUNT_RANGES: Final[dict[str, dict[str, float]]] = {
    "technology": {"min": 0.12, "max": 0.20, "median": 0.15},
    "healthcare": {"min": 0.10, "max": 0.18, "median": 0.14},
    "financial_services": {"min": 0.08, "max": 0.14, "median": 0.11},
    "consumer_goods": {"min": 0.08, "max": 0.15, "median": 0.12},
    "industrials": {"min": 0.08, "max": 0.14, "median": 0.11},
    "energy": {"min": 0.09, "max": 0.16, "median": 0.12},
    "real_estate": {"min": 0.07, "max": 0.12, "median": 0.09},
    "telecommunications": {"min": 0.08, "max": 0.14, "median": 0.11},
    "utilities": {"min": 0.06, "max": 0.10, "median": 0.08},
    "materials": {"min": 0.09, "max": 0.15, "median": 0.12},
}

# Asset type default useful lives (years)
DEFAULT_USEFUL_LIVES: Final[dict[str, dict[str, float]]] = {
    "patent": {"legal_max": 20, "economic_typical": 10, "tech_obsolescence_rate": 0.10},
    "trademark": {"legal_max": float("inf"), "economic_typical": 20, "tech_obsolescence_rate": 0.02},
    "copyright": {"legal_max": 70, "economic_typical": 25, "tech_obsolescence_rate": 0.05},
    "trade_secret": {"legal_max": float("inf"), "economic_typical": 15, "tech_obsolescence_rate": 0.08},
    "customer_relationship": {"legal_max": float("inf"), "economic_typical": 12, "tech_obsolescence_rate": 0.05},
    "software": {"legal_max": float("inf"), "economic_typical": 5, "tech_obsolescence_rate": 0.15},
    "brand": {"legal_max": float("inf"), "economic_typical": 20, "tech_obsolescence_rate": 0.03},
    "license": {"legal_max": None, "economic_typical": 10, "tech_obsolescence_rate": 0.05},
    "goodwill": {"legal_max": float("inf"), "economic_typical": float("inf"), "tech_obsolescence_rate": 0.0},
}

# Default size premiums (based on company market cap)
SIZE_PREMIUMS: Final[dict[str, float]] = {
    "micro_cap": 0.06,
    "small_cap": 0.04,
    "mid_cap": 0.02,
    "large_cap": 0.0,
}

# Default country risk premiums (selected countries)
COUNTRY_RISK_PREMIUMS: Final[dict[str, float]] = {
    "US": 0.0,
    "UK": 0.01,
    "Germany": 0.01,
    "Japan": 0.01,
    "China": 0.03,
    "India": 0.04,
    "Brazil": 0.05,
    "Russia": 0.06,
    "South_Africa": 0.04,
    "Mexico": 0.03,
}

# Valuation method identifiers
METHOD_GORDON_GROWTH: Final[str] = "gordon_growth"
METHOD_EXIT_MULTIPLE: Final[str] = "exit_multiple"
METHOD_CAPM: Final[str] = "capm"
METHOD_BUILD_UP: Final[str] = "build_up"
METHOD_WACC: Final[str] = "wacc"
METHOD_FINNERTY: Final[str] = "finnerty"
