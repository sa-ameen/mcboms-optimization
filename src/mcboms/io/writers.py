"""
Data Output Writers for MCBOMs.

This module provides functions for writing optimization results
to various file formats.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    from mcboms.core.optimizer import OptimizationResult

logger = logging.getLogger(__name__)


def write_results(
    result: OptimizationResult,
    output_dir: str | Path,
    prefix: str = "mcboms",
    formats: list[str] | None = None,
) -> dict[str, Path]:
    """Write optimization results to files.
    
    Args:
        result: OptimizationResult from optimizer
        output_dir: Directory for output files
        prefix: Filename prefix
        formats: List of output formats ('csv', 'xlsx', 'json', 'txt')
    
    Returns:
        Dict mapping format to output filepath
    
    Example:
        >>> paths = write_results(result, 'data/output/', prefix='run1')
        >>> print(paths['csv'])
    """
    if formats is None:
        formats = ["csv", "txt"]
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_files = {}
    
    for fmt in formats:
        if fmt == "csv":
            path = output_dir / f"{prefix}_results_{timestamp}.csv"
            result.selected_alternatives.to_csv(path, index=False)
            output_files["csv"] = path
            
        elif fmt == "xlsx":
            path = output_dir / f"{prefix}_results_{timestamp}.xlsx"
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                result.selected_alternatives.to_excel(
                    writer, sheet_name="Selected Alternatives", index=False
                )
                # Summary sheet
                summary_df = pd.DataFrame([{
                    "Status": result.status,
                    "Net Benefit": result.net_benefit,
                    "Total Cost": result.total_cost,
                    "Total Benefit": result.total_benefit,
                    "Budget Utilization": result.budget_utilization,
                    "Sites Improved": result.sites_improved,
                    "Sites Deferred": result.sites_deferred,
                    "Solve Time (s)": result.solve_time,
                }])
                summary_df.to_excel(writer, sheet_name="Summary", index=False)
            output_files["xlsx"] = path
            
        elif fmt == "json":
            path = output_dir / f"{prefix}_results_{timestamp}.json"
            data = {
                "status": result.status,
                "objective_value": result.objective_value,
                "net_benefit": result.net_benefit,
                "total_cost": result.total_cost,
                "total_benefit": result.total_benefit,
                "budget_utilization": result.budget_utilization,
                "sites_improved": result.sites_improved,
                "sites_deferred": result.sites_deferred,
                "solve_time": result.solve_time,
                "gap": result.gap,
                "selected_alternatives": result.selected_alternatives.to_dict(orient="records"),
            }
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            output_files["json"] = path
            
        elif fmt == "txt":
            path = output_dir / f"{prefix}_results_{timestamp}.txt"
            with open(path, "w") as f:
                f.write(result.summary())
                f.write("\n\nSELECTED ALTERNATIVES:\n")
                f.write("-" * 60 + "\n")
                f.write(result.selected_alternatives.to_string())
            output_files["txt"] = path
    
    logger.info(f"Results written to {output_dir}")
    
    return output_files


def write_comparison_report(
    mcboms_result: OptimizationResult,
    benchmark_df: pd.DataFrame,
    output_path: str | Path,
    benchmark_name: str = "Harwood (2003)",
) -> Path:
    """Write a comparison report between MCBOMs and benchmark results.
    
    Args:
        mcboms_result: MCBOMs optimization result
        benchmark_df: DataFrame with benchmark expected results
        output_path: Path for output report
        benchmark_name: Name of benchmark study
    
    Returns:
        Path to output file
    """
    output_path = Path(output_path)
    
    # Merge results
    mcboms_df = mcboms_result.selected_alternatives.copy()
    comparison = pd.merge(
        benchmark_df,
        mcboms_df,
        on="site_id",
        suffixes=("_benchmark", "_mcboms"),
        how="outer"
    )
    
    # Calculate differences
    if "total_cost_benchmark" in comparison.columns and "total_cost_mcboms" in comparison.columns:
        comparison["cost_diff"] = comparison["total_cost_mcboms"] - comparison["total_cost_benchmark"]
        comparison["cost_diff_pct"] = comparison["cost_diff"] / comparison["total_cost_benchmark"] * 100
    
    if "total_benefit_benchmark" in comparison.columns and "total_benefit_mcboms" in comparison.columns:
        comparison["benefit_diff"] = comparison["total_benefit_mcboms"] - comparison["total_benefit_benchmark"]
        comparison["benefit_diff_pct"] = comparison["benefit_diff"] / comparison["total_benefit_benchmark"] * 100
    
    # Write report
    lines = [
        "=" * 70,
        f"MCBOMs vs {benchmark_name} COMPARISON REPORT",
        "=" * 70,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "SUMMARY COMPARISON",
        "-" * 50,
    ]
    
    benchmark_total_cost = benchmark_df["total_cost"].sum() if "total_cost" in benchmark_df else 0
    benchmark_total_benefit = benchmark_df["total_benefit"].sum() if "total_benefit" in benchmark_df else 0
    
    lines.extend([
        f"{'Metric':<25} {'Benchmark':>15} {'MCBOMs':>15} {'Diff %':>10}",
        "-" * 70,
        f"{'Total Cost':<25} ${benchmark_total_cost:>14,.0f} ${mcboms_result.total_cost:>14,.0f} "
        f"{(mcboms_result.total_cost - benchmark_total_cost) / benchmark_total_cost * 100 if benchmark_total_cost else 0:>9.1f}%",
        f"{'Total Benefit':<25} ${benchmark_total_benefit:>14,.0f} ${mcboms_result.total_benefit:>14,.0f} "
        f"{(mcboms_result.total_benefit - benchmark_total_benefit) / benchmark_total_benefit * 100 if benchmark_total_benefit else 0:>9.1f}%",
        "",
        "SITE-BY-SITE COMPARISON",
        "-" * 50,
        comparison.to_string(),
        "",
        "=" * 70,
    ])
    
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    
    logger.info(f"Comparison report written to {output_path}")
    
    return output_path
