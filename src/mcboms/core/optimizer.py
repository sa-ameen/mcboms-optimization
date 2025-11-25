"""
Core MILP Optimizer for MCBOMs.

This module implements the Mixed-Integer Linear Programming (MILP) formulation
for optimizing transportation infrastructure investment decisions.

Mathematical Formulation:
    
    Objective:
        max Σᵢ Σⱼ (Bᵢⱼ - Cᵢⱼ) × xᵢⱼ
    
    Subject to:
        Σⱼ xᵢⱼ ≤ 1           ∀i  (mutual exclusivity)
        Σᵢ Σⱼ Cᵢⱼ × xᵢⱼ ≤ B      (budget constraint)
        xᵢⱼ ∈ {0, 1}         ∀i,j (binary)

References:
    - Harwood et al. (2003). Systemwide optimization of safety improvements
      for resurfacing, restoration, or rehabilitation projects.
    - Banihashemi (2007). Optimization of highway safety and operation by
      using crash prediction models with accident modification factors.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    import gurobipy as gp

from mcboms.utils.economics import calculate_discount_factors

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Container for optimization results.
    
    Attributes:
        status: Solver status (optimal, infeasible, etc.)
        objective_value: Optimal objective function value
        net_benefit: Total net benefit (benefits - costs)
        total_cost: Total cost of selected alternatives
        total_benefit: Total benefit of selected alternatives
        selected_alternatives: DataFrame of selected alternatives by site
        budget_utilization: Fraction of budget used
        solve_time: Solver time in seconds
        gap: Optimality gap (for MIP)
    """
    status: str
    objective_value: float
    net_benefit: float
    total_cost: float
    total_benefit: float
    selected_alternatives: pd.DataFrame
    budget_utilization: float
    solve_time: float
    gap: float = 0.0
    sites_improved: int = 0
    sites_deferred: int = 0
    
    def __repr__(self) -> str:
        return (
            f"OptimizationResult(\n"
            f"  status='{self.status}',\n"
            f"  net_benefit=${self.net_benefit:,.0f},\n"
            f"  total_cost=${self.total_cost:,.0f},\n"
            f"  budget_utilization={self.budget_utilization:.1%},\n"
            f"  sites_improved={self.sites_improved},\n"
            f"  solve_time={self.solve_time:.3f}s\n"
            f")"
        )
    
    def summary(self) -> str:
        """Generate a summary report of optimization results."""
        lines = [
            "=" * 60,
            "MCBOMs OPTIMIZATION RESULTS",
            "=" * 60,
            f"Status: {self.status}",
            f"Solve Time: {self.solve_time:.3f} seconds",
            f"Optimality Gap: {self.gap:.4%}",
            "",
            "FINANCIAL SUMMARY",
            "-" * 40,
            f"Total Cost:        ${self.total_cost:>15,.0f}",
            f"Total Benefit:     ${self.total_benefit:>15,.0f}",
            f"Net Benefit:       ${self.net_benefit:>15,.0f}",
            f"Budget Utilization: {self.budget_utilization:>14.1%}",
            "",
            "PROJECT SUMMARY",
            "-" * 40,
            f"Sites Improved:    {self.sites_improved:>15d}",
            f"Sites Deferred:    {self.sites_deferred:>15d}",
            "=" * 60,
        ]
        return "\n".join(lines)


@dataclass
class OptimizerConfig:
    """Configuration for the optimizer.
    
    Attributes:
        budget: Total available budget ($)
        discount_rate: Annual discount rate (e.g., 0.07 for 7%)
        analysis_horizon: Analysis period in years
        time_limit: Maximum solver time in seconds
        mip_gap: Acceptable optimality gap
        verbose: Whether to print solver output
    """
    budget: float
    discount_rate: float = 0.07
    analysis_horizon: int = 20
    time_limit: float = 300.0
    mip_gap: float = 0.0001
    verbose: bool = False
    
    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.budget <= 0:
            raise ValueError(f"Budget must be positive, got {self.budget}")
        if not 0 < self.discount_rate < 1:
            raise ValueError(f"Discount rate must be between 0 and 1, got {self.discount_rate}")
        if self.analysis_horizon <= 0:
            raise ValueError(f"Analysis horizon must be positive, got {self.analysis_horizon}")


class Optimizer:
    """MILP Optimizer for MCBOMs framework.
    
    This class implements the core optimization engine using Gurobi
    to solve the project selection problem.
    
    Example:
        >>> optimizer = Optimizer(
        ...     sites=sites_df,
        ...     alternatives=alternatives_df,
        ...     budget=10_000_000
        ... )
        >>> results = optimizer.solve()
        >>> print(results.summary())
    
    Attributes:
        sites: DataFrame containing site characteristics
        alternatives: DataFrame containing improvement alternatives
        config: Optimizer configuration
    """
    
    def __init__(
        self,
        sites: pd.DataFrame,
        alternatives: pd.DataFrame,
        budget: float,
        discount_rate: float = 0.07,
        analysis_horizon: int = 20,
        **kwargs: Any,
    ) -> None:
        """Initialize the optimizer.
        
        Args:
            sites: DataFrame with site characteristics (site_id, adt, length, etc.)
            alternatives: DataFrame with alternatives (site_id, alt_id, cost, benefit)
            budget: Total available budget
            discount_rate: Annual discount rate
            analysis_horizon: Analysis period in years
            **kwargs: Additional configuration options
        """
        self.sites = sites
        self.alternatives = alternatives
        self.config = OptimizerConfig(
            budget=budget,
            discount_rate=discount_rate,
            analysis_horizon=analysis_horizon,
            **kwargs,
        )
        
        self._model: gp.Model | None = None
        self._variables: dict[tuple[int, int], Any] = {}
        
        # Validate inputs
        self._validate_inputs()
        
        logger.info(
            f"Optimizer initialized with {len(sites)} sites, "
            f"{len(alternatives)} alternatives, budget=${budget:,.0f}"
        )
    
    def _validate_inputs(self) -> None:
        """Validate input data."""
        required_site_cols = {"site_id"}
        required_alt_cols = {"site_id", "alt_id", "total_cost", "total_benefit"}
        
        missing_site = required_site_cols - set(self.sites.columns)
        if missing_site:
            raise ValueError(f"Sites DataFrame missing columns: {missing_site}")
        
        missing_alt = required_alt_cols - set(self.alternatives.columns)
        if missing_alt:
            raise ValueError(f"Alternatives DataFrame missing columns: {missing_alt}")
        
        # Check all sites have at least one alternative
        site_ids_in_sites = set(self.sites["site_id"])
        site_ids_in_alts = set(self.alternatives["site_id"])
        
        missing = site_ids_in_sites - site_ids_in_alts
        if missing:
            logger.warning(f"Sites without alternatives: {missing}")
    
    def _build_model(self) -> None:
        """Build the Gurobi MILP model."""
        import gurobipy as gp
        from gurobipy import GRB
        
        logger.info("Building MILP model...")
        
        # Create model
        self._model = gp.Model("MCBOMs")
        
        # Set parameters
        self._model.Params.TimeLimit = self.config.time_limit
        self._model.Params.MIPGap = self.config.mip_gap
        if not self.config.verbose:
            self._model.Params.OutputFlag = 0
        
        # Create decision variables: x[i,j] = 1 if alternative j selected for site i
        self._variables = {}
        for _, row in self.alternatives.iterrows():
            site_id = row["site_id"]
            alt_id = row["alt_id"]
            var_name = f"x_{site_id}_{alt_id}"
            self._variables[(site_id, alt_id)] = self._model.addVar(
                vtype=GRB.BINARY, name=var_name
            )
        
        # Objective: Maximize net benefit
        # Net benefit = total_benefit - total_cost for each selected alternative
        obj_expr = gp.quicksum(
            (row["total_benefit"] - row["total_cost"]) * self._variables[(row["site_id"], row["alt_id"])]
            for _, row in self.alternatives.iterrows()
        )
        self._model.setObjective(obj_expr, GRB.MAXIMIZE)
        
        # Constraint 1: Mutual exclusivity - at most one alternative per site
        for site_id in self.sites["site_id"].unique():
            site_alts = self.alternatives[self.alternatives["site_id"] == site_id]
            if len(site_alts) > 0:
                self._model.addConstr(
                    gp.quicksum(
                        self._variables[(site_id, row["alt_id"])]
                        for _, row in site_alts.iterrows()
                    ) <= 1,
                    name=f"exclusivity_{site_id}"
                )
        
        # Constraint 2: Budget constraint
        budget_expr = gp.quicksum(
            row["total_cost"] * self._variables[(row["site_id"], row["alt_id"])]
            for _, row in self.alternatives.iterrows()
        )
        self._model.addConstr(budget_expr <= self.config.budget, name="budget")
        
        self._model.update()
        
        logger.info(
            f"Model built: {self._model.NumVars} variables, "
            f"{self._model.NumConstrs} constraints"
        )
    
    def solve(self) -> OptimizationResult:
        """Solve the optimization problem.
        
        Returns:
            OptimizationResult containing the optimal solution.
        
        Raises:
            RuntimeError: If optimization fails.
        """
        from gurobipy import GRB
        
        # Build model if not already built
        if self._model is None:
            self._build_model()
        
        logger.info("Solving MILP...")
        
        # Solve
        self._model.optimize()
        
        # Check status
        status = self._model.Status
        status_map = {
            GRB.OPTIMAL: "optimal",
            GRB.INFEASIBLE: "infeasible",
            GRB.UNBOUNDED: "unbounded",
            GRB.TIME_LIMIT: "time_limit",
            GRB.INTERRUPTED: "interrupted",
        }
        status_str = status_map.get(status, f"unknown_{status}")
        
        if status == GRB.INFEASIBLE:
            logger.error("Model is infeasible")
            raise RuntimeError("Optimization problem is infeasible")
        
        if status not in (GRB.OPTIMAL, GRB.TIME_LIMIT):
            logger.error(f"Optimization failed with status: {status_str}")
            raise RuntimeError(f"Optimization failed: {status_str}")
        
        # Extract results
        return self._extract_results(status_str)
    
    def _extract_results(self, status: str) -> OptimizationResult:
        """Extract results from solved model."""
        from gurobipy import GRB
        
        # Get selected alternatives
        selected = []
        for (site_id, alt_id), var in self._variables.items():
            if var.X > 0.5:  # Binary variable selected
                alt_row = self.alternatives[
                    (self.alternatives["site_id"] == site_id) &
                    (self.alternatives["alt_id"] == alt_id)
                ].iloc[0]
                selected.append({
                    "site_id": site_id,
                    "alt_id": alt_id,
                    "description": alt_row.get("description", ""),
                    "total_cost": alt_row["total_cost"],
                    "total_benefit": alt_row["total_benefit"],
                    "net_benefit": alt_row["total_benefit"] - alt_row["total_cost"],
                })
        
        selected_df = pd.DataFrame(selected)
        
        # Calculate totals
        total_cost = selected_df["total_cost"].sum() if len(selected_df) > 0 else 0
        total_benefit = selected_df["total_benefit"].sum() if len(selected_df) > 0 else 0
        net_benefit = total_benefit - total_cost
        
        # Count sites
        sites_improved = len(selected_df[selected_df["alt_id"] != 0]) if len(selected_df) > 0 else 0
        total_sites = len(self.sites)
        sites_deferred = total_sites - len(selected_df)
        
        result = OptimizationResult(
            status=status,
            objective_value=self._model.ObjVal,
            net_benefit=net_benefit,
            total_cost=total_cost,
            total_benefit=total_benefit,
            selected_alternatives=selected_df,
            budget_utilization=total_cost / self.config.budget if self.config.budget > 0 else 0,
            solve_time=self._model.Runtime,
            gap=self._model.MIPGap if hasattr(self._model, "MIPGap") else 0,
            sites_improved=sites_improved,
            sites_deferred=sites_deferred,
        )
        
        logger.info(f"Optimization complete: {result}")
        
        return result
    
    def add_constraint(
        self,
        name: str,
        expression: Any,
        sense: str = "<=",
        rhs: float = 0,
    ) -> None:
        """Add a custom constraint to the model.
        
        Args:
            name: Constraint name
            expression: Left-hand side expression
            sense: Constraint sense ('<=', '>=', '==')
            rhs: Right-hand side value
        """
        if self._model is None:
            self._build_model()
        
        from gurobipy import GRB
        
        sense_map = {
            "<=": GRB.LESS_EQUAL,
            ">=": GRB.GREATER_EQUAL,
            "==": GRB.EQUAL,
        }
        
        self._model.addConstr(expression, sense_map[sense], rhs, name=name)
        logger.info(f"Added constraint: {name}")
    
    def get_variable(self, site_id: int, alt_id: int) -> Any:
        """Get a decision variable by site and alternative ID.
        
        Args:
            site_id: Site identifier
            alt_id: Alternative identifier
        
        Returns:
            Gurobi variable object
        """
        return self._variables.get((site_id, alt_id))


def solve_harwood_problem(
    sites: pd.DataFrame,
    alternatives: pd.DataFrame,
    budget: float,
    discount_rate: float = 0.04,  # Harwood uses 4%
) -> OptimizationResult:
    """Convenience function to solve Harwood-style problem.
    
    This function sets up the optimizer with parameters matching
    Harwood et al. (2003) for validation purposes.
    
    Args:
        sites: Site characteristics DataFrame
        alternatives: Alternatives DataFrame
        budget: Budget constraint
        discount_rate: Discount rate (default 4% per Harwood)
    
    Returns:
        OptimizationResult
    """
    optimizer = Optimizer(
        sites=sites,
        alternatives=alternatives,
        budget=budget,
        discount_rate=discount_rate,
        analysis_horizon=20,
        verbose=False,
    )
    return optimizer.solve()
