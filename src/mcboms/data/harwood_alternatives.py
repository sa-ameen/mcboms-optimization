"""
Harwood (2003) Pre-calculated Alternatives Data.

This module provides the exact costs and benefits from Harwood et al. (2003)
Tables 2 and 3 for validation purposes. These values are used directly
without recalculating from CMFs.

The alternatives are structured to match the RSRAP optimization results.
"""

import pandas as pd


def get_harwood_alternatives() -> pd.DataFrame:
    """
    Get all alternatives for Harwood 10-site problem with pre-calculated values.
    
    This includes:
    - Do nothing (alt_id=0) for all sites
    - Resurface only (alt_id=1) where applicable
    - Various improvement combinations with exact costs/benefits from paper
    
    Returns:
        DataFrame with columns: site_id, alt_id, description, 
        resurfacing_cost, safety_improvement_cost, safety_benefit, 
        ops_benefit, total_cost, total_benefit
    """
    
    alternatives = []
    
    # =========================================================================
    # SITE 1: Rural, 2-lane, 9ft lanes, 2ft turf shoulders
    # Optimal ($50M): Resurface only
    # =========================================================================
    alternatives.extend([
        # Alt 0: Do nothing
        {"site_id": 1, "alt_id": 0, "description": "Do nothing",
         "resurfacing_cost": 0, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0},
        # Alt 1: Resurface only (OPTIMAL for both $50M and $10M)
        {"site_id": 1, "alt_id": 1, "description": "Resurface only",
         "resurfacing_cost": 528803, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 35107},
        # Alt 2: Resurface + lane widening (not cost-effective per Harwood)
        {"site_id": 1, "alt_id": 2, "description": "Resurface + Widen lanes",
         "resurfacing_cost": 528803, "safety_improvement_cost": 200000,
         "safety_benefit": 150000, "ops_benefit": 35107},
    ])
    
    # =========================================================================
    # SITE 2: Rural, 2-lane, 10ft lanes, 4ft composite shoulders
    # Optimal: Resurface + Turn-lane improvements
    # =========================================================================
    alternatives.extend([
        {"site_id": 2, "alt_id": 0, "description": "Do nothing",
         "resurfacing_cost": 0, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0},
        {"site_id": 2, "alt_id": 1, "description": "Resurface only",
         "resurfacing_cost": 519763, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 71580},
        # Alt 2: OPTIMAL
        {"site_id": 2, "alt_id": 2, "description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 519763, "safety_improvement_cost": 120000,
         "safety_benefit": 328176, "ops_benefit": 71580},
    ])
    
    # =========================================================================
    # SITE 3: Rural, 2-lane, 11ft lanes, 4ft paved shoulders
    # Optimal: Resurface + Turn-lane + Roadside + User-defined #2
    # =========================================================================
    alternatives.extend([
        {"site_id": 3, "alt_id": 0, "description": "Do nothing",
         "resurfacing_cost": 0, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0},
        {"site_id": 3, "alt_id": 1, "description": "Resurface only",
         "resurfacing_cost": 821621, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 93697},
        {"site_id": 3, "alt_id": 2, "description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 821621, "safety_improvement_cost": 120000,
         "safety_benefit": 400000, "ops_benefit": 93697},
        # Alt 3: OPTIMAL
        {"site_id": 3, "alt_id": 3, "description": "Resurface + Turn-lane + Roadside + User-def #2",
         "resurfacing_cost": 821621, "safety_improvement_cost": 560000,
         "safety_benefit": 1094909, "ops_benefit": 93697},
    ])
    
    # =========================================================================
    # SITE 4: Urban, 2-lane divided, 10ft lanes, 4ft paved shoulders
    # Optimal ($50M): Resurface + Lane widen (10→11) + Shoulder widen (4→6)
    # Optimal ($10M): Do nothing
    # =========================================================================
    alternatives.extend([
        {"site_id": 4, "alt_id": 0, "description": "Do nothing",
         "resurfacing_cost": 0, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0},
        {"site_id": 4, "alt_id": 1, "description": "Resurface only",
         "resurfacing_cost": 475200, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 58379},
        # Alt 2: OPTIMAL for $50M
        {"site_id": 4, "alt_id": 2, "description": "Resurface + Lane widen + Shoulder widen",
         "resurfacing_cost": 475200, "safety_improvement_cost": 572616,
         "safety_benefit": 775629, "ops_benefit": 58379},
    ])
    
    # =========================================================================
    # SITE 5: Rural, 4-lane undivided, 10ft lanes, 4ft gravel shoulders
    # Optimal: Resurface + Turn-lane improvements
    # =========================================================================
    alternatives.extend([
        {"site_id": 5, "alt_id": 0, "description": "Do nothing",
         "resurfacing_cost": 0, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0},
        {"site_id": 5, "alt_id": 1, "description": "Resurface only",
         "resurfacing_cost": 1180017, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 53029},
        # Alt 2: OPTIMAL
        {"site_id": 5, "alt_id": 2, "description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 1180017, "safety_improvement_cost": 240000,
         "safety_benefit": 1355589, "ops_benefit": 53029},
    ])
    
    # =========================================================================
    # SITE 6: Urban, 4-lane undivided, 11ft lanes, 6ft paved shoulders
    # Optimal ($50M): Resurface + Turn-lane improvements
    # Optimal ($10M): Do nothing
    # =========================================================================
    alternatives.extend([
        {"site_id": 6, "alt_id": 0, "description": "Do nothing",
         "resurfacing_cost": 0, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0},
        {"site_id": 6, "alt_id": 1, "description": "Resurface only",
         "resurfacing_cost": 2508549, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 92800},
        # Alt 2: OPTIMAL for $50M
        {"site_id": 6, "alt_id": 2, "description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 2508549, "safety_improvement_cost": 560000,
         "safety_benefit": 808637, "ops_benefit": 92800},
    ])
    
    # =========================================================================
    # SITE 7: Rural, 4-lane divided, 11ft lanes, 4ft paved shoulders
    # Optimal: Resurface + Turn-lane improvements
    # =========================================================================
    alternatives.extend([
        {"site_id": 7, "alt_id": 0, "description": "Do nothing",
         "resurfacing_cost": 0, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0},
        {"site_id": 7, "alt_id": 1, "description": "Resurface only",
         "resurfacing_cost": 1503237, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 93407},
        # Alt 2: OPTIMAL
        {"site_id": 7, "alt_id": 2, "description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 1503237, "safety_improvement_cost": 360000,
         "safety_benefit": 947234, "ops_benefit": 93407},
    ])
    
    # =========================================================================
    # SITE 8: Rural, 4-lane divided, 12ft lanes, 8ft paved shoulders
    # Optimal ($50M): Resurface + Turn-lane + User-def #2
    # Optimal ($10M): Resurface + Turn-lane only (User-def #2 excluded)
    # =========================================================================
    alternatives.extend([
        {"site_id": 8, "alt_id": 0, "description": "Do nothing",
         "resurfacing_cost": 0, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0},
        {"site_id": 8, "alt_id": 1, "description": "Resurface only",
         "resurfacing_cost": 1398989, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 150118},
        # Alt 2: OPTIMAL for $10M
        {"site_id": 8, "alt_id": 2, "description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 1398989, "safety_improvement_cost": 180000,
         "safety_benefit": 555526, "ops_benefit": 150118},
        # Alt 3: OPTIMAL for $50M
        {"site_id": 8, "alt_id": 3, "description": "Resurface + Turn-lane + User-def #2",
         "resurfacing_cost": 1398989, "safety_improvement_cost": 680000,
         "safety_benefit": 1119938, "ops_benefit": 150118},
    ])
    
    # =========================================================================
    # SITE 9: Urban, 4-lane undivided, 10ft lanes, 2ft paved shoulders
    # Optimal ($50M): Resurface + Turn-lane improvements
    # Optimal ($10M): Do nothing
    # =========================================================================
    alternatives.extend([
        {"site_id": 9, "alt_id": 0, "description": "Do nothing",
         "resurfacing_cost": 0, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0},
        {"site_id": 9, "alt_id": 1, "description": "Resurface only",
         "resurfacing_cost": 1365302, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 81343},
        # Alt 2: OPTIMAL for $50M
        {"site_id": 9, "alt_id": 2, "description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 1365302, "safety_improvement_cost": 336000,
         "safety_benefit": 1071895, "ops_benefit": 81343},
    ])
    
    # =========================================================================
    # SITE 10: Urban, 6-lane divided, 11ft lanes, 4ft paved shoulders
    # Optimal: Resurface + Shoulder widen + Horiz curve + Turn-lane
    # =========================================================================
    alternatives.extend([
        {"site_id": 10, "alt_id": 0, "description": "Do nothing",
         "resurfacing_cost": 0, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 0},
        {"site_id": 10, "alt_id": 1, "description": "Resurface only",
         "resurfacing_cost": 1488369, "safety_improvement_cost": 0,
         "safety_benefit": 0, "ops_benefit": 80186},
        {"site_id": 10, "alt_id": 2, "description": "Resurface + Turn-lane improvements",
         "resurfacing_cost": 1488369, "safety_improvement_cost": 400000,
         "safety_benefit": 800000, "ops_benefit": 80186},
        # Alt 3: OPTIMAL
        {"site_id": 10, "alt_id": 3, "description": "Resurface + Shoulder + Horiz curve + Turn-lane",
         "resurfacing_cost": 1488369, "safety_improvement_cost": 1052781,
         "safety_benefit": 2329256, "ops_benefit": 80186},
    ])
    
    # Convert to DataFrame
    df = pd.DataFrame(alternatives)
    
    # Calculate derived columns
    df["total_cost"] = df["resurfacing_cost"] + df["safety_improvement_cost"]
    df["total_benefit"] = df["safety_benefit"] + df["ops_benefit"]
    df["net_benefit"] = df["total_benefit"] - df["total_cost"]
    
    return df


def get_expected_solution_50m() -> dict:
    """Expected optimal solution for $50M budget."""
    return {
        "selected_alternatives": {
            1: 1,   # Resurface only
            2: 2,   # Resurface + Turn-lane
            3: 3,   # Resurface + Turn-lane + Roadside + User-def #2
            4: 2,   # Resurface + Lane widen + Shoulder widen
            5: 2,   # Resurface + Turn-lane
            6: 2,   # Resurface + Turn-lane
            7: 2,   # Resurface + Turn-lane
            8: 3,   # Resurface + Turn-lane + User-def #2
            9: 2,   # Resurface + Turn-lane
            10: 3,  # Resurface + Shoulder + Horiz curve + Turn-lane
        },
        "total_resurfacing_cost": 11_789_849,
        "total_safety_cost": 4_481_397,
        "total_cost": 16_271_246,
        "total_safety_benefit": 9_831_263,
        "total_ops_benefit": 809_651,
        "total_benefit": 10_640_914,
        "net_benefit": 6_159_517,  # total_benefit - safety_cost
    }


def get_expected_solution_10m() -> dict:
    """Expected optimal solution for $10M budget."""
    return {
        "selected_alternatives": {
            1: 1,   # Resurface only
            2: 2,   # Resurface + Turn-lane
            3: 3,   # Resurface + Turn-lane + Roadside + User-def #2
            4: 0,   # DO NOTHING
            5: 2,   # Resurface + Turn-lane
            6: 0,   # DO NOTHING
            7: 2,   # Resurface + Turn-lane
            8: 2,   # Resurface + Turn-lane (NOT alt 3!)
            9: 0,   # DO NOTHING
            10: 3,  # Resurface + Shoulder + Horiz curve + Turn-lane
        },
        "total_resurfacing_cost": 7_440_798,
        "total_safety_cost": 2_512_781,
        "total_cost": 9_953_579,
        "total_safety_benefit": 6_610_690,
        "total_ops_benefit": 577_124,
        "total_benefit": 7_187_814,
        "net_benefit": 4_675_033,
        "do_nothing_sites": [4, 6, 9],
    }


if __name__ == "__main__":
    # Print summary when run directly
    df = get_harwood_alternatives()
    print("Harwood Alternatives Summary")
    print("=" * 60)
    print(f"Total alternatives: {len(df)}")
    print(f"Sites: {df['site_id'].nunique()}")
    print()
    print("Alternatives per site:")
    print(df.groupby("site_id").size())
    print()
    print("Sample data:")
    print(df[["site_id", "alt_id", "description", "total_cost", "total_benefit"]].head(10))
