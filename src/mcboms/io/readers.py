"""
Data Input/Output Readers for MCBOMs.

This module provides functions for loading site and alternative data
from various file formats (CSV, Excel, JSON).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def load_sites(filepath: str | Path) -> pd.DataFrame:
    """Load site characteristics from a file.
    
    Supports CSV, Excel (.xlsx, .xls), and JSON formats.
    
    Args:
        filepath: Path to the data file
    
    Returns:
        DataFrame with site characteristics
    
    Required columns:
        - site_id: Unique site identifier
    
    Optional columns (used if present):
        - area_type: Rural/Urban
        - roadway_type: Divided/Undivided
        - lanes: Number of lanes
        - adt: Average daily traffic
        - speed_mph: Average speed
        - length_mi: Segment length in miles
        - lane_width_ft: Existing lane width
        - shoulder_width_ft: Existing shoulder width
        - shoulder_type: Paved/Gravel/Turf/Composite
        - crashes_nonintersection: Annual non-intersection crashes
        - crashes_intersection: Annual intersection crashes
    
    Example:
        >>> sites = load_sites('data/input/sites.csv')
        >>> print(sites.columns)
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Site file not found: {filepath}")
    
    suffix = filepath.suffix.lower()
    
    if suffix == ".csv":
        df = pd.read_csv(filepath)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(filepath)
    elif suffix == ".json":
        df = pd.read_json(filepath)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
    
    # Validate required columns
    if "site_id" not in df.columns:
        raise ValueError("Sites file must contain 'site_id' column")
    
    # Ensure site_id is unique
    if df["site_id"].duplicated().any():
        raise ValueError("Duplicate site_id values found")
    
    logger.info(f"Loaded {len(df)} sites from {filepath}")
    
    return df


def load_alternatives(filepath: str | Path) -> pd.DataFrame:
    """Load improvement alternatives from a file.
    
    Args:
        filepath: Path to the data file
    
    Returns:
        DataFrame with alternatives
    
    Required columns:
        - site_id: Site identifier (must match sites file)
        - alt_id: Alternative identifier (0 = do nothing)
        - total_cost: Total cost of alternative
        - total_benefit: Total benefit of alternative
    
    Optional columns:
        - description: Human-readable description
        - resurfacing_cost: Cost for resurfacing
        - safety_improvement_cost: Cost for safety improvements
        - safety_benefit: Safety benefits
        - ops_benefit: Operational benefits
        - ccm_benefit: Corridor condition benefits
    
    Example:
        >>> alternatives = load_alternatives('data/input/alternatives.csv')
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Alternatives file not found: {filepath}")
    
    suffix = filepath.suffix.lower()
    
    if suffix == ".csv":
        df = pd.read_csv(filepath)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(filepath)
    elif suffix == ".json":
        df = pd.read_json(filepath)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
    
    # Validate required columns
    required = {"site_id", "alt_id", "total_cost", "total_benefit"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Alternatives file missing columns: {missing}")
    
    # Ensure unique (site_id, alt_id) combinations
    if df.duplicated(subset=["site_id", "alt_id"]).any():
        raise ValueError("Duplicate (site_id, alt_id) combinations found")
    
    logger.info(f"Loaded {len(df)} alternatives from {filepath}")
    
    return df


def load_config(filepath: str | Path) -> dict[str, Any]:
    """Load configuration from YAML or JSON file.
    
    Args:
        filepath: Path to config file
    
    Returns:
        Configuration dictionary
    
    Example:
        >>> config = load_config('config.yaml')
        >>> print(config['economic']['discount_rate'])
    """
    import yaml
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Config file not found: {filepath}")
    
    suffix = filepath.suffix.lower()
    
    with open(filepath, "r") as f:
        if suffix in (".yaml", ".yml"):
            config = yaml.safe_load(f)
        elif suffix == ".json":
            config = json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {suffix}")
    
    logger.info(f"Loaded configuration from {filepath}")
    
    return config


def load_harwood_sites() -> pd.DataFrame:
    """Load the Harwood (2003) benchmark site data.
    
    Returns:
        DataFrame with 10 sites from Harwood Table 1
    """
    data = [
        {"site_id": 1, "area_type": "Rural", "roadway_type": "Undivided", "lanes": 2,
         "adt": 1000, "speed_mph": 35, "length_mi": 5.2, "lane_width_ft": 9,
         "shoulder_width_ft": 2, "shoulder_type": "Turf",
         "crashes_nonintersection": 5, "crashes_intersection": 3},
        {"site_id": 2, "area_type": "Rural", "roadway_type": "Undivided", "lanes": 2,
         "adt": 3000, "speed_mph": 40, "length_mi": 4.6, "lane_width_ft": 10,
         "shoulder_width_ft": 4, "shoulder_type": "Composite",
         "crashes_nonintersection": 4, "crashes_intersection": 4},
        {"site_id": 3, "area_type": "Rural", "roadway_type": "Undivided", "lanes": 2,
         "adt": 4000, "speed_mph": 45, "length_mi": 5.7, "lane_width_ft": 11,
         "shoulder_width_ft": 4, "shoulder_type": "Paved",
         "crashes_nonintersection": 11, "crashes_intersection": 11},
        {"site_id": 4, "area_type": "Urban", "roadway_type": "Divided", "lanes": 2,
         "adt": 7000, "speed_mph": 50, "length_mi": 2.5, "lane_width_ft": 10,
         "shoulder_width_ft": 4, "shoulder_type": "Paved",
         "crashes_nonintersection": 15, "crashes_intersection": 3},
        {"site_id": 5, "area_type": "Rural", "roadway_type": "Undivided", "lanes": 4,
         "adt": 4000, "speed_mph": 55, "length_mi": 4.8, "lane_width_ft": 10,
         "shoulder_width_ft": 4, "shoulder_type": "Gravel",
         "crashes_nonintersection": 10, "crashes_intersection": 10},
        {"site_id": 6, "area_type": "Urban", "roadway_type": "Undivided", "lanes": 4,
         "adt": 6000, "speed_mph": 55, "length_mi": 5.6, "lane_width_ft": 11,
         "shoulder_width_ft": 6, "shoulder_type": "Paved",
         "crashes_nonintersection": 14, "crashes_intersection": 14},
        {"site_id": 7, "area_type": "Rural", "roadway_type": "Divided", "lanes": 4,
         "adt": 5000, "speed_mph": 50, "length_mi": 5.6, "lane_width_ft": 11,
         "shoulder_width_ft": 4, "shoulder_type": "Paved",
         "crashes_nonintersection": 13, "crashes_intersection": 13},
        {"site_id": 8, "area_type": "Rural", "roadway_type": "Divided", "lanes": 4,
         "adt": 10000, "speed_mph": 50, "length_mi": 4.5, "lane_width_ft": 12,
         "shoulder_width_ft": 8, "shoulder_type": "Paved",
         "crashes_nonintersection": 15, "crashes_intersection": 15},
        {"site_id": 9, "area_type": "Urban", "roadway_type": "Undivided", "lanes": 4,
         "adt": 10000, "speed_mph": 60, "length_mi": 3.5, "lane_width_ft": 10,
         "shoulder_width_ft": 2, "shoulder_type": "Paved",
         "crashes_nonintersection": 12, "crashes_intersection": 12},
        {"site_id": 10, "area_type": "Urban", "roadway_type": "Divided", "lanes": 6,
         "adt": 15000, "speed_mph": 60, "length_mi": 2.3, "lane_width_ft": 11,
         "shoulder_width_ft": 4, "shoulder_type": "Paved",
         "crashes_nonintersection": 14, "crashes_intersection": 14},
    ]
    
    df = pd.DataFrame(data)
    logger.info("Loaded Harwood (2003) benchmark site data: 10 sites")
    return df


def load_harwood_results_50m() -> pd.DataFrame:
    """Load expected results for Harwood $50M budget scenario.
    
    Returns:
        DataFrame with expected optimal selections (Table 2)
    """
    data = [
        {"site_id": 1, "alt_description": "Resurface only",
         "resurfacing_cost": 528803, "safety_cost": 0,
         "safety_benefit": 0, "ops_benefit": 35107, "total_benefit": 35107},
        {"site_id": 2, "alt_description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 519763, "safety_cost": 120000,
         "safety_benefit": 328176, "ops_benefit": 71580, "total_benefit": 399756},
        {"site_id": 3, "alt_description": "Resurface + Turn-lane + Roadside + User-def #2",
         "resurfacing_cost": 821621, "safety_cost": 560000,
         "safety_benefit": 1094909, "ops_benefit": 93697, "total_benefit": 1188606},
        {"site_id": 4, "alt_description": "Resurface + Lane widen (10→11) + Shoulder widen (4→6)",
         "resurfacing_cost": 475200, "safety_cost": 572616,
         "safety_benefit": 775629, "ops_benefit": 58379, "total_benefit": 834008},
        {"site_id": 5, "alt_description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 1180017, "safety_cost": 240000,
         "safety_benefit": 1355589, "ops_benefit": 53029, "total_benefit": 1408618},
        {"site_id": 6, "alt_description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 2508549, "safety_cost": 560000,
         "safety_benefit": 808637, "ops_benefit": 92800, "total_benefit": 901437},
        {"site_id": 7, "alt_description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 1503237, "safety_cost": 360000,
         "safety_benefit": 947234, "ops_benefit": 93407, "total_benefit": 1040641},
        {"site_id": 8, "alt_description": "Resurface + Turn-lane + User-def #2",
         "resurfacing_cost": 1398989, "safety_cost": 680000,
         "safety_benefit": 1119938, "ops_benefit": 150118, "total_benefit": 1270056},
        {"site_id": 9, "alt_description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 1365302, "safety_cost": 336000,
         "safety_benefit": 1071895, "ops_benefit": 81343, "total_benefit": 1153243},
        {"site_id": 10, "alt_description": "Resurface + Shoulder widen + Horiz curve + Turn-lane",
         "resurfacing_cost": 1488369, "safety_cost": 1052781,
         "safety_benefit": 2329256, "ops_benefit": 80186, "total_benefit": 2409442},
    ]
    
    df = pd.DataFrame(data)
    df["total_cost"] = df["resurfacing_cost"] + df["safety_cost"]
    df["net_benefit"] = df["total_benefit"] - df["safety_cost"]
    
    logger.info("Loaded Harwood (2003) expected results: $50M budget scenario")
    return df


def load_harwood_results_10m() -> pd.DataFrame:
    """Load expected results for Harwood $10M budget scenario.
    
    Returns:
        DataFrame with expected optimal selections (Table 3)
    """
    data = [
        {"site_id": 1, "alt_description": "Resurface only",
         "resurfacing_cost": 528803, "safety_cost": 0,
         "safety_benefit": 0, "ops_benefit": 35107, "total_benefit": 35107},
        {"site_id": 2, "alt_description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 519763, "safety_cost": 120000,
         "safety_benefit": 328176, "ops_benefit": 71580, "total_benefit": 399756},
        {"site_id": 3, "alt_description": "Resurface + Turn-lane + Roadside + User-def #2",
         "resurfacing_cost": 821621, "safety_cost": 560000,
         "safety_benefit": 1094909, "ops_benefit": 93697, "total_benefit": 1188606},
        {"site_id": 4, "alt_description": "Do nothing",
         "resurfacing_cost": 0, "safety_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0, "total_benefit": 0},
        {"site_id": 5, "alt_description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 1180017, "safety_cost": 240000,
         "safety_benefit": 1355589, "ops_benefit": 53029, "total_benefit": 1408618},
        {"site_id": 6, "alt_description": "Do nothing",
         "resurfacing_cost": 0, "safety_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0, "total_benefit": 0},
        {"site_id": 7, "alt_description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 1503237, "safety_cost": 360000,
         "safety_benefit": 947234, "ops_benefit": 93407, "total_benefit": 1040641},
        {"site_id": 8, "alt_description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 1398989, "safety_cost": 180000,
         "safety_benefit": 555526, "ops_benefit": 150118, "total_benefit": 705644},
        {"site_id": 9, "alt_description": "Do nothing",
         "resurfacing_cost": 0, "safety_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0, "total_benefit": 0},
        {"site_id": 10, "alt_description": "Resurface + Shoulder widen + Horiz curve + Turn-lane",
         "resurfacing_cost": 1488369, "safety_cost": 1052781,
         "safety_benefit": 2329256, "ops_benefit": 80186, "total_benefit": 2409442},
    ]
    
    df = pd.DataFrame(data)
    df["total_cost"] = df["resurfacing_cost"] + df["safety_cost"]
    df["net_benefit"] = df["total_benefit"] - df["safety_cost"]
    
    logger.info("Loaded Harwood (2003) expected results: $10M budget scenario")
    return df
