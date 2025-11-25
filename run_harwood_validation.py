#!/usr/bin/env python3
"""
MCBOMs Harwood (2003) Validation Runner

This script validates the MCBOMs optimizer against the benchmark results
from Harwood et al. (2003) Tables 2 and 3.

Usage:
    python run_harwood_validation.py

Requirements:
    - Python 3.11+
    - gurobipy (with valid license)
    - pandas, numpy

The script will:
    1. Load Harwood site data and pre-calculated alternatives
    2. Run optimization for $50M budget (unconstrained)
    3. Run optimization for $10M budget (constrained)
    4. Compare results against expected values
    5. Print validation report
"""

import sys
from pathlib import Path

# Add src to path if running from project root
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
import numpy as np


def print_header(text: str, char: str = "=") -> None:
    """Print a formatted header."""
    print()
    print(char * 70)
    print(text)
    print(char * 70)


def print_comparison_table(label: str, expected: float, actual: float) -> None:
    """Print a comparison row."""
    diff = actual - expected
    pct = (diff / expected * 100) if expected != 0 else 0
    status = "✓" if abs(pct) < 5 else "✗"
    print(f"  {label:<30} ${expected:>12,.0f}  ${actual:>12,.0f}  {pct:>+6.1f}%  {status}")


def run_validation():
    """Run the complete Harwood validation."""
    
    print_header("MCBOMs HARWOOD (2003) VALIDATION")
    print("Validating optimizer against benchmark results from:")
    print("  Harwood et al. (2003). Systemwide optimization of safety")
    print("  improvements for R3 projects. TRR 1840, pp. 148-157.")
    
    # =========================================================================
    # Step 1: Load Data
    # =========================================================================
    print_header("STEP 1: Loading Data", "-")
    
    from mcboms.io.readers import load_harwood_sites
    from mcboms.data.harwood_alternatives import (
        get_harwood_alternatives,
        get_expected_solution_50m,
        get_expected_solution_10m,
    )
    
    sites = load_harwood_sites()
    alternatives = get_harwood_alternatives()
    
    print(f"  Sites loaded: {len(sites)}")
    print(f"  Alternatives loaded: {len(alternatives)}")
    print(f"  Alternatives per site: {len(alternatives) / len(sites):.1f} avg")
    
    # =========================================================================
    # Step 2: Run $50M Budget Optimization
    # =========================================================================
    print_header("STEP 2: Optimization - $50M Budget (Unconstrained)", "-")
    
    from mcboms.core.optimizer import Optimizer
    
    optimizer_50m = Optimizer(
        sites=sites,
        alternatives=alternatives,
        budget=50_000_000,
        discount_rate=0.04,  # Harwood uses 4%
        verbose=False,
    )
    
    result_50m = optimizer_50m.solve()
    expected_50m = get_expected_solution_50m()
    
    print(f"  Status: {result_50m.status}")
    print(f"  Solve time: {result_50m.solve_time:.3f} seconds")
    print()
    
    print("  COMPARISON ($50M Budget):")
    print("  " + "-" * 66)
    print(f"  {'Metric':<30} {'Expected':>12}  {'Actual':>12}  {'Diff':>7}  OK?")
    print("  " + "-" * 66)
    
    # Calculate actual totals
    selected_50m = result_50m.selected_alternatives
    actual_resurfacing_50m = selected_50m["resurfacing_cost"].sum() if "resurfacing_cost" in selected_50m.columns else 0
    actual_safety_cost_50m = selected_50m["safety_improvement_cost"].sum() if "safety_improvement_cost" in selected_50m.columns else 0
    
    print_comparison_table("Total Cost", expected_50m["total_cost"], result_50m.total_cost)
    print_comparison_table("Total Benefit", expected_50m["total_benefit"], result_50m.total_benefit)
    print_comparison_table("Net Benefit", expected_50m["net_benefit"], result_50m.net_benefit)
    
    # Check selected alternatives
    print()
    print("  SELECTED ALTERNATIVES ($50M):")
    print("  " + "-" * 50)
    
    selected_dict_50m = {}
    for _, row in selected_50m.iterrows():
        selected_dict_50m[row["site_id"]] = row["alt_id"]
        expected_alt = expected_50m["selected_alternatives"].get(row["site_id"], -1)
        match = "✓" if row["alt_id"] == expected_alt else "✗"
        print(f"    Site {row['site_id']:>2}: Alt {row['alt_id']} (expected {expected_alt}) {match}")
    
    # =========================================================================
    # Step 3: Run $10M Budget Optimization
    # =========================================================================
    print_header("STEP 3: Optimization - $10M Budget (Constrained)", "-")
    
    optimizer_10m = Optimizer(
        sites=sites,
        alternatives=alternatives,
        budget=10_000_000,
        discount_rate=0.04,
        verbose=False,
    )
    
    result_10m = optimizer_10m.solve()
    expected_10m = get_expected_solution_10m()
    
    print(f"  Status: {result_10m.status}")
    print(f"  Solve time: {result_10m.solve_time:.3f} seconds")
    print(f"  Budget utilization: {result_10m.budget_utilization:.1%}")
    print()
    
    print("  COMPARISON ($10M Budget):")
    print("  " + "-" * 66)
    print(f"  {'Metric':<30} {'Expected':>12}  {'Actual':>12}  {'Diff':>7}  OK?")
    print("  " + "-" * 66)
    
    print_comparison_table("Total Cost", expected_10m["total_cost"], result_10m.total_cost)
    print_comparison_table("Total Benefit", expected_10m["total_benefit"], result_10m.total_benefit)
    print_comparison_table("Net Benefit", expected_10m["net_benefit"], result_10m.net_benefit)
    
    # Check selected alternatives
    print()
    print("  SELECTED ALTERNATIVES ($10M):")
    print("  " + "-" * 50)
    
    selected_10m = result_10m.selected_alternatives
    selected_dict_10m = {}
    for _, row in selected_10m.iterrows():
        selected_dict_10m[row["site_id"]] = row["alt_id"]
    
    # Show all sites including do-nothing
    for site_id in range(1, 11):
        actual_alt = selected_dict_10m.get(site_id, 0)  # 0 if not selected = do nothing
        expected_alt = expected_10m["selected_alternatives"].get(site_id, 0)
        match = "✓" if actual_alt == expected_alt else "✗"
        label = " (DO NOTHING)" if actual_alt == 0 else ""
        print(f"    Site {site_id:>2}: Alt {actual_alt}{label:<15} (expected {expected_alt}) {match}")
    
    # Check do-nothing sites specifically
    actual_do_nothing = [s for s in range(1, 11) if selected_dict_10m.get(s, 0) == 0]
    expected_do_nothing = expected_10m["do_nothing_sites"]
    
    print()
    print(f"  Do-nothing sites - Expected: {expected_do_nothing}")
    print(f"  Do-nothing sites - Actual:   {actual_do_nothing}")
    print(f"  Match: {'✓ YES' if set(actual_do_nothing) == set(expected_do_nothing) else '✗ NO'}")
    
    # =========================================================================
    # Step 4: Summary
    # =========================================================================
    print_header("VALIDATION SUMMARY")
    
    # Calculate pass/fail
    tests_passed = 0
    tests_total = 6
    
    # $50M tests
    if abs(result_50m.total_cost - expected_50m["total_cost"]) / expected_50m["total_cost"] < 0.05:
        tests_passed += 1
    if abs(result_50m.total_benefit - expected_50m["total_benefit"]) / expected_50m["total_benefit"] < 0.05:
        tests_passed += 1
    if abs(result_50m.net_benefit - expected_50m["net_benefit"]) / expected_50m["net_benefit"] < 0.05:
        tests_passed += 1
    
    # $10M tests
    if abs(result_10m.total_cost - expected_10m["total_cost"]) / expected_10m["total_cost"] < 0.05:
        tests_passed += 1
    if abs(result_10m.total_benefit - expected_10m["total_benefit"]) / expected_10m["total_benefit"] < 0.05:
        tests_passed += 1
    if set(actual_do_nothing) == set(expected_do_nothing):
        tests_passed += 1
    
    print(f"  Tests passed: {tests_passed}/{tests_total}")
    print()
    
    if tests_passed == tests_total:
        print("  ╔════════════════════════════════════════════════════════════════╗")
        print("  ║  ✓ VALIDATION SUCCESSFUL                                       ║")
        print("  ║    MCBOMs optimizer matches Harwood (2003) benchmark results   ║")
        print("  ╚════════════════════════════════════════════════════════════════╝")
        return 0
    else:
        print("  ╔════════════════════════════════════════════════════════════════╗")
        print("  ║  ✗ VALIDATION FAILED                                           ║")
        print("  ║    Some results do not match expected values                   ║")
        print("  ╚════════════════════════════════════════════════════════════════╝")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(run_validation())
    except ImportError as e:
        print(f"Import error: {e}")
        print()
        print("Make sure you have installed the package:")
        print("  pip install -e .")
        print()
        print("Or install dependencies:")
        print("  pip install gurobipy pandas numpy")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
