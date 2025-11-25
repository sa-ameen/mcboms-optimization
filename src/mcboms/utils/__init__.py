"""
Utility modules for MCBOMs.
"""

from mcboms.utils.economics import (
    calculate_discount_factor,
    calculate_discount_factors,
    calculate_present_worth_factor,
    calculate_npv,
    calculate_bcr,
    annualize_value,
    DEFAULT_DISCOUNT_RATE,
    DEFAULT_ANALYSIS_HORIZON,
    CRASH_COSTS_USDOT_2024,
    CRASH_COSTS_HARWOOD_2003,
    VOT_USDOT_2024,
    VOT_HARWOOD_2003,
)

__all__ = [
    "calculate_discount_factor",
    "calculate_discount_factors",
    "calculate_present_worth_factor",
    "calculate_npv",
    "calculate_bcr",
    "annualize_value",
    "DEFAULT_DISCOUNT_RATE",
    "DEFAULT_ANALYSIS_HORIZON",
    "CRASH_COSTS_USDOT_2024",
    "CRASH_COSTS_HARWOOD_2003",
    "VOT_USDOT_2024",
    "VOT_HARWOOD_2003",
]
