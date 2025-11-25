"""
Alternative Enumeration Module for MCBOMs.

This module implements the alternative enumeration approach following
Harwood et al. (2003), where partial-length improvements and treatment
combinations are enumerated at the preprocessing stage rather than
handled through optimization constraints.

Key Concepts:
    - Each site has a set of feasible improvement alternatives
    - Alternatives include "do nothing" (j=0)
    - Combinations of treatments (lane widening + shoulder widening) 
      are enumerated as separate alternatives
    - Partial-length improvements can be enumerated with segment definitions

References:
    - Harwood et al. (2003) - Alternative enumeration approach
    - Banihashemi (2007) - MIL constraints (alternative approach, not used here)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from itertools import product
from typing import Any, Iterator

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ImprovementType:
    """Definition of an improvement type.
    
    Attributes:
        name: Improvement type name (e.g., "lane_widening")
        options: List of option values (e.g., [10, 11, 12] for lane width in feet)
        unit_cost_per_mile: Cost per mile for each option increment
        base_cmf: Base crash modification factor
    """
    name: str
    options: list[Any]
    unit_cost_per_mile: float = 0.0
    base_cmf: float = 1.0
    description: str = ""


@dataclass
class Alternative:
    """A single improvement alternative for a site.
    
    Attributes:
        site_id: Site identifier
        alt_id: Alternative identifier (0 = do nothing)
        description: Human-readable description
        improvements: Dict of improvement type -> selected option
        resurfacing_cost: Cost for resurfacing
        safety_improvement_cost: Cost for safety improvements
        safety_benefit: Present value of safety benefits
        ops_benefit: Present value of operational benefits
        ccm_benefit: Present value of corridor condition benefits
    """
    site_id: int
    alt_id: int
    description: str
    improvements: dict[str, Any] = field(default_factory=dict)
    resurfacing_cost: float = 0.0
    safety_improvement_cost: float = 0.0
    safety_benefit: float = 0.0
    ops_benefit: float = 0.0
    ccm_benefit: float = 0.0
    
    @property
    def total_cost(self) -> float:
        """Total cost (resurfacing + safety improvements)."""
        return self.resurfacing_cost + self.safety_improvement_cost
    
    @property
    def total_benefit(self) -> float:
        """Total benefit (safety + operations + CCM)."""
        return self.safety_benefit + self.ops_benefit + self.ccm_benefit
    
    @property
    def net_benefit(self) -> float:
        """Net benefit (total benefit - total cost)."""
        return self.total_benefit - self.total_cost
    
    @property
    def bcr(self) -> float:
        """Benefit-cost ratio."""
        if self.total_cost == 0:
            return float('inf') if self.total_benefit > 0 else 0.0
        return self.total_benefit / self.total_cost
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return {
            "site_id": self.site_id,
            "alt_id": self.alt_id,
            "description": self.description,
            "resurfacing_cost": self.resurfacing_cost,
            "safety_improvement_cost": self.safety_improvement_cost,
            "safety_benefit": self.safety_benefit,
            "ops_benefit": self.ops_benefit,
            "ccm_benefit": self.ccm_benefit,
            "total_cost": self.total_cost,
            "total_benefit": self.total_benefit,
            "net_benefit": self.net_benefit,
            "bcr": self.bcr,
            **{f"imp_{k}": v for k, v in self.improvements.items()},
        }


class AlternativeEnumerator:
    """Enumerates improvement alternatives for sites.
    
    This class implements the Harwood (2003) approach where all feasible
    combinations of improvements are enumerated as discrete alternatives.
    
    Example:
        >>> enumerator = AlternativeEnumerator()
        >>> enumerator.add_improvement_type(
        ...     "lane_width",
        ...     options=[10, 11, 12],
        ...     unit_cost_per_mile=100000
        ... )
        >>> alternatives = enumerator.enumerate_site(site)
    """
    
    def __init__(self) -> None:
        """Initialize the enumerator."""
        self.improvement_types: dict[str, ImprovementType] = {}
        self._cost_calculator = None
        self._benefit_calculator = None
    
    def add_improvement_type(
        self,
        name: str,
        options: list[Any],
        unit_cost_per_mile: float = 0.0,
        base_cmf: float = 1.0,
        description: str = "",
    ) -> None:
        """Add an improvement type to consider.
        
        Args:
            name: Improvement type name
            options: List of feasible options (include existing as first option)
            unit_cost_per_mile: Cost per mile per increment
            base_cmf: Base crash modification factor
            description: Human-readable description
        """
        self.improvement_types[name] = ImprovementType(
            name=name,
            options=options,
            unit_cost_per_mile=unit_cost_per_mile,
            base_cmf=base_cmf,
            description=description,
        )
        logger.debug(f"Added improvement type: {name} with {len(options)} options")
    
    def enumerate_site(
        self,
        site: dict[str, Any],
        include_do_nothing: bool = True,
        include_resurface_only: bool = True,
    ) -> list[Alternative]:
        """Enumerate all alternatives for a single site.
        
        Args:
            site: Site characteristics dictionary
            include_do_nothing: Whether to include "do nothing" alternative
            include_resurface_only: Whether to include "resurface only" alternative
        
        Returns:
            List of Alternative objects
        """
        site_id = site["site_id"]
        alternatives = []
        alt_id = 0
        
        # Alternative 0: Do nothing
        if include_do_nothing:
            alternatives.append(Alternative(
                site_id=site_id,
                alt_id=alt_id,
                description="Do nothing",
                improvements={},
                resurfacing_cost=0,
                safety_improvement_cost=0,
                safety_benefit=0,
                ops_benefit=0,
            ))
            alt_id += 1
        
        # Alternative 1: Resurface only (if applicable)
        if include_resurface_only:
            resurfacing_cost = self._calculate_resurfacing_cost(site)
            ops_benefit = self._calculate_resurfacing_ops_benefit(site)
            alternatives.append(Alternative(
                site_id=site_id,
                alt_id=alt_id,
                description="Resurface only",
                improvements={"resurface": True},
                resurfacing_cost=resurfacing_cost,
                safety_improvement_cost=0,
                safety_benefit=0,
                ops_benefit=ops_benefit,
            ))
            alt_id += 1
        
        # Get applicable improvement types for this site
        applicable_types = self._get_applicable_improvements(site)
        
        if not applicable_types:
            return alternatives
        
        # Generate all combinations
        type_names = list(applicable_types.keys())
        option_lists = [applicable_types[name] for name in type_names]
        
        for combination in product(*option_lists):
            # Skip if all options are "existing" (no improvement)
            improvements = dict(zip(type_names, combination))
            if all(self._is_existing_option(name, opt, site) for name, opt in improvements.items()):
                continue
            
            # Create alternative
            description = self._create_description(improvements, site)
            costs = self._calculate_costs(site, improvements)
            benefits = self._calculate_benefits(site, improvements)
            
            alternatives.append(Alternative(
                site_id=site_id,
                alt_id=alt_id,
                description=description,
                improvements=improvements,
                resurfacing_cost=costs["resurfacing"],
                safety_improvement_cost=costs["safety"],
                safety_benefit=benefits["safety"],
                ops_benefit=benefits["ops"],
                ccm_benefit=benefits.get("ccm", 0),
            ))
            alt_id += 1
        
        logger.info(f"Site {site_id}: Enumerated {len(alternatives)} alternatives")
        return alternatives
    
    def enumerate_all_sites(
        self,
        sites: pd.DataFrame,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Enumerate alternatives for all sites.
        
        Args:
            sites: DataFrame with site characteristics
            **kwargs: Additional arguments passed to enumerate_site
        
        Returns:
            DataFrame with all alternatives
        """
        all_alternatives = []
        
        for _, site_row in sites.iterrows():
            site_dict = site_row.to_dict()
            site_alts = self.enumerate_site(site_dict, **kwargs)
            all_alternatives.extend([alt.to_dict() for alt in site_alts])
        
        df = pd.DataFrame(all_alternatives)
        
        logger.info(
            f"Enumerated {len(df)} total alternatives for {len(sites)} sites"
        )
        
        return df
    
    def _get_applicable_improvements(
        self,
        site: dict[str, Any],
    ) -> dict[str, list[Any]]:
        """Determine applicable improvements for a site.
        
        Args:
            site: Site characteristics
        
        Returns:
            Dict mapping improvement type to list of feasible options
        """
        applicable = {}
        
        for name, imp_type in self.improvement_types.items():
            # Get current value from site
            current = site.get(name, site.get(f"{name}_ft", None))
            
            # Filter options to those >= current (improvements only)
            if current is not None:
                feasible = [opt for opt in imp_type.options if opt >= current]
                if len(feasible) > 1:  # Has improvement options beyond existing
                    applicable[name] = feasible
            else:
                applicable[name] = imp_type.options
        
        return applicable
    
    def _is_existing_option(
        self,
        imp_name: str,
        option: Any,
        site: dict[str, Any],
    ) -> bool:
        """Check if option represents existing condition (no change)."""
        current = site.get(imp_name, site.get(f"{imp_name}_ft", None))
        return option == current
    
    def _create_description(
        self,
        improvements: dict[str, Any],
        site: dict[str, Any],
    ) -> str:
        """Create human-readable description of improvements."""
        parts = ["Resurface"]
        
        for name, value in improvements.items():
            current = site.get(name, site.get(f"{name}_ft", None))
            if current is not None and value != current:
                parts.append(f"{name.replace('_', ' ')} {current}→{value}")
        
        return " + ".join(parts)
    
    def _calculate_resurfacing_cost(self, site: dict[str, Any]) -> float:
        """Calculate resurfacing cost for a site.
        
        This is a placeholder - actual implementation should use
        agency-specific unit costs.
        """
        # Default: $100,000 per mile
        length = site.get("length_mi", site.get("length", 1.0))
        lanes = site.get("lanes", 2)
        return 100_000 * length * (lanes / 2)
    
    def _calculate_resurfacing_ops_benefit(self, site: dict[str, Any]) -> float:
        """Calculate operational benefits from resurfacing.
        
        Per Harwood (2003): ~1 mph speed increase post-resurfacing.
        """
        # Placeholder - will be implemented in benefits module
        return 0.0
    
    def _calculate_costs(
        self,
        site: dict[str, Any],
        improvements: dict[str, Any],
    ) -> dict[str, float]:
        """Calculate costs for an improvement combination.
        
        Returns:
            Dict with "resurfacing" and "safety" costs
        """
        resurfacing = self._calculate_resurfacing_cost(site)
        safety = 0.0
        
        length = site.get("length_mi", site.get("length", 1.0))
        
        for name, target in improvements.items():
            if name in self.improvement_types:
                current = site.get(name, site.get(f"{name}_ft", 0))
                if target > current:
                    unit_cost = self.improvement_types[name].unit_cost_per_mile
                    # Cost proportional to improvement magnitude
                    safety += unit_cost * (target - current) * length
        
        return {"resurfacing": resurfacing, "safety": safety}
    
    def _calculate_benefits(
        self,
        site: dict[str, Any],
        improvements: dict[str, Any],
    ) -> dict[str, float]:
        """Calculate benefits for an improvement combination.
        
        This is a placeholder - actual implementation will call
        the benefits calculation modules.
        
        Returns:
            Dict with "safety", "ops", and "ccm" benefits
        """
        # Placeholder - will be implemented using benefits modules
        return {"safety": 0.0, "ops": 0.0, "ccm": 0.0}


def create_harwood_enumerator() -> AlternativeEnumerator:
    """Create an enumerator configured for Harwood (2003) case study.
    
    Returns:
        AlternativeEnumerator with Harwood-style improvement types
    """
    enumerator = AlternativeEnumerator()
    
    # Lane widening options (ft)
    enumerator.add_improvement_type(
        name="lane_width",
        options=[9, 10, 11, 12],
        unit_cost_per_mile=50_000,  # per foot of widening
        description="Lane width in feet"
    )
    
    # Shoulder widening options (ft)
    enumerator.add_improvement_type(
        name="shoulder_width",
        options=[0, 2, 4, 6, 8],
        unit_cost_per_mile=30_000,  # per foot of widening
        description="Shoulder width in feet"
    )
    
    return enumerator


def enumerate_partial_length_alternatives(
    site: dict[str, Any],
    improvement_type: str,
    segment_lengths: list[float],
) -> list[dict[str, Any]]:
    """Enumerate partial-length alternatives for a site.
    
    This implements the approach described by the reviewer where
    partial-length improvements are enumerated as separate alternatives.
    
    Example for a 5-mile site with 2-mile and 3-mile segments:
        - Apply to first 2 miles only
        - Apply to last 3 miles only
        - Apply to full 5 miles
    
    Args:
        site: Site characteristics
        improvement_type: Type of improvement (e.g., "lane_widening")
        segment_lengths: List of segment lengths to consider
    
    Returns:
        List of partial-length alternative specifications
    
    Example:
        >>> alternatives = enumerate_partial_length_alternatives(
        ...     site={"site_id": 1, "length_mi": 5.0},
        ...     improvement_type="lane_widening",
        ...     segment_lengths=[2.0, 3.0]
        ... )
        >>> len(alternatives)  # First 2mi, last 3mi, full 5mi
        3
    """
    site_length = site.get("length_mi", site.get("length", 0))
    alternatives = []
    
    cumulative = 0.0
    for i, seg_len in enumerate(segment_lengths):
        alternatives.append({
            "segment_id": i,
            "start_mile": cumulative,
            "end_mile": cumulative + seg_len,
            "length": seg_len,
            "improvement_type": improvement_type,
        })
        cumulative += seg_len
    
    # Full length option
    alternatives.append({
        "segment_id": -1,  # Indicates full length
        "start_mile": 0,
        "end_mile": site_length,
        "length": site_length,
        "improvement_type": improvement_type,
    })
    
    return alternatives
