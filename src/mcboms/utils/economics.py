"""
Economic Utility Functions for MCBOMs.

This module provides functions for economic calculations including:
- Net Present Value (NPV)
- Discount factors
- Benefit-cost ratios
- Annualization
"""

from __future__ import annotations

import logging
from typing import Sequence

import numpy as np

logger = logging.getLogger(__name__)


def calculate_discount_factor(
    rate: float,
    year: int,
) -> float:
    """Calculate single-year discount factor.
    
    Args:
        rate: Annual discount rate (e.g., 0.07 for 7%)
        year: Year number (1-indexed)
    
    Returns:
        Discount factor for the specified year
    
    Formula:
        DF_t = 1 / (1 + r)^t
    
    Example:
        >>> calculate_discount_factor(0.07, 10)
        0.5083...
    """
    if rate < 0:
        raise ValueError(f"Discount rate must be non-negative, got {rate}")
    if year < 0:
        raise ValueError(f"Year must be non-negative, got {year}")
    
    return 1 / (1 + rate) ** year


def calculate_discount_factors(
    rate: float,
    horizon: int,
) -> np.ndarray:
    """Calculate discount factors for all years in analysis horizon.
    
    Args:
        rate: Annual discount rate
        horizon: Number of years
    
    Returns:
        Array of discount factors [DF_1, DF_2, ..., DF_T]
    
    Example:
        >>> factors = calculate_discount_factors(0.07, 20)
        >>> factors[0]  # Year 1
        0.9345...
        >>> factors[19]  # Year 20
        0.2584...
    """
    years = np.arange(1, horizon + 1)
    return 1 / (1 + rate) ** years


def calculate_present_worth_factor(
    rate: float,
    years: int,
) -> float:
    """Calculate uniform-series present worth factor (P/A).
    
    Used to convert uniform annual benefits to present value.
    
    Args:
        rate: Annual discount rate
        years: Number of years
    
    Returns:
        Present worth factor
    
    Formula:
        (P/A, i, n) = [(1+i)^n - 1] / [i * (1+i)^n]
    
    Example:
        >>> calculate_present_worth_factor(0.07, 20)
        10.594...
    """
    if rate == 0:
        return float(years)
    
    return ((1 + rate) ** years - 1) / (rate * (1 + rate) ** years)


def calculate_npv(
    cash_flows: Sequence[float],
    rate: float,
    initial_investment: float = 0,
) -> float:
    """Calculate Net Present Value of cash flows.
    
    Args:
        cash_flows: Sequence of annual cash flows (benefits - costs)
        rate: Annual discount rate
        initial_investment: Initial cost at year 0
    
    Returns:
        Net Present Value
    
    Example:
        >>> cash_flows = [100_000] * 20  # $100K annual benefit
        >>> npv = calculate_npv(cash_flows, 0.07, initial_investment=500_000)
    """
    factors = calculate_discount_factors(rate, len(cash_flows))
    pv_benefits = np.sum(np.array(cash_flows) * factors)
    return pv_benefits - initial_investment


def calculate_bcr(
    benefits: float,
    costs: float,
) -> float:
    """Calculate Benefit-Cost Ratio.
    
    Args:
        benefits: Total present value of benefits
        costs: Total present value of costs
    
    Returns:
        Benefit-cost ratio (or inf if costs are zero)
    """
    if costs == 0:
        return float('inf') if benefits > 0 else 0.0
    return benefits / costs


def annualize_value(
    present_value: float,
    rate: float,
    years: int,
) -> float:
    """Convert present value to equivalent uniform annual value.
    
    Args:
        present_value: Present value amount
        rate: Annual discount rate
        years: Number of years
    
    Returns:
        Equivalent uniform annual value
    
    Formula:
        A = P * [i * (1+i)^n] / [(1+i)^n - 1]
    """
    if rate == 0:
        return present_value / years
    
    pwf = calculate_present_worth_factor(rate, years)
    return present_value / pwf


# Default economic parameters (USDOT 2024)
DEFAULT_DISCOUNT_RATE = 0.07
DEFAULT_ANALYSIS_HORIZON = 20

# USDOT 2024 crash costs
CRASH_COSTS_USDOT_2024 = {
    "fatal": 13_200_000,      # Value of Statistical Life
    "injury_a": 800_000,       # Incapacitating
    "injury_b": 400_000,       # Non-incapacitating
    "injury_c": 200_000,       # Possible injury
    "pdo": 15_000,             # Property damage only
}

# Harwood (2003) crash costs (1994 FHWA)
CRASH_COSTS_HARWOOD_2003 = {
    "fatal": 2_600_000,
    "injury_a": 180_000,
    "injury_b": 36_000,
    "injury_c": 19_000,
    "pdo": 2_000,
}

# Value of time (USDOT 2024, $/hour)
VOT_USDOT_2024 = {
    "personal": 17.80,
    "business": 33.60,
    "truck": 32.80,
}

# Harwood (2003) VOT
VOT_HARWOOD_2003 = {
    "all": 10.00,  # Single value used
}
