"""
MCBOMs: Multidisciplinary Cost-Benefit Optimization Models

A Python framework for optimizing transportation infrastructure investment
decisions using Mixed-Integer Linear Programming (MILP).

Example:
    >>> from mcboms import Optimizer, load_sites
    >>> sites = load_sites('data/input/sites.csv')
    >>> optimizer = Optimizer(sites=sites, budget=10_000_000)
    >>> results = optimizer.solve()
    >>> print(f"Net Benefit: ${results.net_benefit:,.0f}")
"""

__version__ = "0.1.0"
__author__ = "Texas A&M Transportation Institute"
__license__ = "MIT"

from mcboms.core.optimizer import Optimizer
from mcboms.core.alternatives import AlternativeEnumerator
from mcboms.io.readers import load_sites, load_alternatives, load_harwood_sites
from mcboms.io.writers import write_results
from mcboms.data.harwood_alternatives import get_harwood_alternatives

__all__ = [
    "Optimizer",
    "AlternativeEnumerator",
    "load_sites",
    "load_alternatives",
    "load_harwood_sites",
    "get_harwood_alternatives",
    "write_results",
    "__version__",
]
