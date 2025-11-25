"""
Harwood (2003) Validation Tests for MCBOMs.

This module contains tests to validate the MCBOMs implementation
against the benchmark results published in Harwood et al. (2003).

Validation Criteria:
    - Total costs within ±5%
    - Total benefits within ±5%
    - Same sites selected for improvement
    - Same sites deferred (do-nothing)

References:
    Harwood, D. W., et al. (2003). Systemwide optimization of safety
    improvements for resurfacing, restoration, or rehabilitation projects.
    Transportation Research Record, 1840(1), 148-157.
"""

import pytest
import pandas as pd
import numpy as np

from mcboms.io.readers import (
    load_harwood_sites,
    load_harwood_results_50m,
    load_harwood_results_10m,
)


class TestHarwoodDataLoading:
    """Tests for loading Harwood benchmark data."""
    
    def test_load_sites(self):
        """Test loading Harwood site characteristics."""
        sites = load_harwood_sites()
        
        assert len(sites) == 10, "Should have 10 sites"
        assert "site_id" in sites.columns
        assert sites["site_id"].nunique() == 10, "Site IDs should be unique"
        
        # Check site 1 characteristics
        site1 = sites[sites["site_id"] == 1].iloc[0]
        assert site1["area_type"] == "Rural"
        assert site1["lanes"] == 2
        assert site1["adt"] == 1000
        assert site1["length_mi"] == 5.2
        assert site1["lane_width_ft"] == 9
        assert site1["shoulder_width_ft"] == 2
    
    def test_load_results_50m(self):
        """Test loading expected results for $50M budget."""
        results = load_harwood_results_50m()
        
        assert len(results) == 10, "Should have results for all 10 sites"
        
        # Check totals (from Harwood Table 2)
        total_resurfacing = results["resurfacing_cost"].sum()
        total_safety = results["safety_cost"].sum()
        total_benefit = results["total_benefit"].sum()
        
        assert abs(total_resurfacing - 11_789_849) < 100, "Resurfacing cost mismatch"
        assert abs(total_safety - 4_481_397) < 100, "Safety cost mismatch"
        assert abs(total_benefit - 10_640_914) < 100, "Total benefit mismatch"
    
    def test_load_results_10m(self):
        """Test loading expected results for $10M budget."""
        results = load_harwood_results_10m()
        
        assert len(results) == 10, "Should have results for all 10 sites"
        
        # Check do-nothing sites
        do_nothing = results[results["alt_description"] == "Do nothing"]["site_id"].tolist()
        assert set(do_nothing) == {4, 6, 9}, "Sites 4, 6, 9 should be do-nothing"
        
        # Check totals (from Harwood Table 3)
        total_resurfacing = results["resurfacing_cost"].sum()
        total_safety = results["safety_cost"].sum()
        total_benefit = results["total_benefit"].sum()
        
        assert abs(total_resurfacing - 7_440_798) < 100, "Resurfacing cost mismatch"
        assert abs(total_safety - 2_512_781) < 100, "Safety cost mismatch"
        assert abs(total_benefit - 7_187_814) < 100, "Total benefit mismatch"


class TestHarwoodSiteCharacteristics:
    """Tests to verify site characteristics are correctly loaded."""
    
    @pytest.fixture
    def sites(self):
        return load_harwood_sites()
    
    def test_site_count(self, sites):
        """Verify 10 sites in dataset."""
        assert len(sites) == 10
    
    def test_area_types(self, sites):
        """Verify area type distribution."""
        rural_count = (sites["area_type"] == "Rural").sum()
        urban_count = (sites["area_type"] == "Urban").sum()
        
        assert rural_count == 6, "Should have 6 rural sites"
        assert urban_count == 4, "Should have 4 urban sites"
    
    def test_lane_configurations(self, sites):
        """Verify lane configurations."""
        two_lane = (sites["lanes"] == 2).sum()
        four_lane = (sites["lanes"] == 4).sum()
        six_lane = (sites["lanes"] == 6).sum()
        
        assert two_lane == 4, "Should have 4 two-lane sites"
        assert four_lane == 5, "Should have 5 four-lane sites"
        assert six_lane == 1, "Should have 1 six-lane site"
    
    def test_total_crashes(self, sites):
        """Verify crash totals."""
        total_crashes = (
            sites["crashes_nonintersection"].sum() + 
            sites["crashes_intersection"].sum()
        )
        # Sum of all crashes from Table 1
        expected = (8 + 8 + 22 + 18 + 20 + 28 + 26 + 30 + 24 + 28)
        assert total_crashes == expected


@pytest.mark.validation
class TestHarwoodValidation50M:
    """Validation tests for $50M budget scenario.
    
    These tests compare MCBOMs optimization results against
    the expected results from Harwood (2003) Table 2.
    """
    
    @pytest.fixture
    def expected_results(self):
        return load_harwood_results_50m()
    
    @pytest.fixture
    def expected_totals(self):
        """Expected totals from Harwood Table 2."""
        return {
            "total_resurfacing_cost": 11_789_849,
            "total_safety_cost": 4_481_397,
            "total_safety_benefit": 9_831_263,
            "total_ops_benefit": 809_651,
            "total_benefit": 10_640_914,
            "net_benefit": 6_159_517,
        }
    
    def test_expected_totals_match_table(self, expected_results, expected_totals):
        """Verify our expected results match Harwood Table 2."""
        actual_resurfacing = expected_results["resurfacing_cost"].sum()
        actual_safety_cost = expected_results["safety_cost"].sum()
        actual_benefit = expected_results["total_benefit"].sum()
        
        assert abs(actual_resurfacing - expected_totals["total_resurfacing_cost"]) < 10
        assert abs(actual_safety_cost - expected_totals["total_safety_cost"]) < 10
        assert abs(actual_benefit - expected_totals["total_benefit"]) < 10
    
    @pytest.mark.skip(reason="MCBOMs optimizer not yet implemented with benefit calculations")
    def test_mcboms_matches_harwood_50m(self, expected_totals):
        """Test MCBOMs optimization matches Harwood $50M results."""
        from mcboms.core import Optimizer
        from mcboms.io import load_harwood_sites
        
        sites = load_harwood_sites()
        # TODO: Generate alternatives with proper costs/benefits
        
        optimizer = Optimizer(
            sites=sites,
            alternatives=None,  # TODO
            budget=50_000_000,
            discount_rate=0.04,  # Harwood uses 4%
        )
        
        result = optimizer.solve()
        
        # Validate within 5% tolerance
        tolerance = 0.05
        
        assert abs(result.total_cost - expected_totals["total_resurfacing_cost"] - 
                  expected_totals["total_safety_cost"]) / (
                      expected_totals["total_resurfacing_cost"] + 
                      expected_totals["total_safety_cost"]
                  ) < tolerance, "Total cost outside 5% tolerance"
        
        assert abs(result.total_benefit - expected_totals["total_benefit"]) / (
            expected_totals["total_benefit"]
        ) < tolerance, "Total benefit outside 5% tolerance"


@pytest.mark.validation
class TestHarwoodValidation10M:
    """Validation tests for $10M budget scenario.
    
    These tests compare MCBOMs optimization results against
    the expected results from Harwood (2003) Table 3.
    """
    
    @pytest.fixture
    def expected_results(self):
        return load_harwood_results_10m()
    
    @pytest.fixture
    def expected_totals(self):
        """Expected totals from Harwood Table 3."""
        return {
            "total_resurfacing_cost": 7_440_798,
            "total_safety_cost": 2_512_781,
            "total_expenditure": 9_953_579,
            "total_safety_benefit": 6_610_690,
            "total_ops_benefit": 577_124,
            "total_benefit": 7_187_814,
            "net_benefit": 4_675_033,
            "do_nothing_sites": {4, 6, 9},
        }
    
    def test_expected_totals_match_table(self, expected_results, expected_totals):
        """Verify our expected results match Harwood Table 3."""
        actual_resurfacing = expected_results["resurfacing_cost"].sum()
        actual_safety_cost = expected_results["safety_cost"].sum()
        
        assert abs(actual_resurfacing - expected_totals["total_resurfacing_cost"]) < 10
        assert abs(actual_safety_cost - expected_totals["total_safety_cost"]) < 10
    
    def test_do_nothing_sites(self, expected_results, expected_totals):
        """Verify correct sites are marked as do-nothing."""
        do_nothing = expected_results[
            expected_results["alt_description"] == "Do nothing"
        ]["site_id"].tolist()
        
        assert set(do_nothing) == expected_totals["do_nothing_sites"]
    
    @pytest.mark.skip(reason="MCBOMs optimizer not yet implemented with benefit calculations")
    def test_mcboms_matches_harwood_10m(self, expected_totals):
        """Test MCBOMs optimization matches Harwood $10M results."""
        from mcboms.core import Optimizer
        from mcboms.io import load_harwood_sites
        
        sites = load_harwood_sites()
        
        optimizer = Optimizer(
            sites=sites,
            alternatives=None,  # TODO
            budget=10_000_000,
            discount_rate=0.04,
        )
        
        result = optimizer.solve()
        
        # Check do-nothing sites match
        do_nothing_sites = set(
            result.selected_alternatives[
                result.selected_alternatives["alt_id"] == 0
            ]["site_id"].tolist()
        )
        
        assert do_nothing_sites == expected_totals["do_nothing_sites"], \
            f"Do-nothing sites mismatch: got {do_nothing_sites}, expected {expected_totals['do_nothing_sites']}"
        
        # Check budget constraint satisfied
        assert result.total_cost <= 10_000_000, "Budget constraint violated"


class TestEconomicCalculations:
    """Tests for economic utility functions."""
    
    def test_discount_factor_year_1(self):
        """Test discount factor for year 1 at 7%."""
        from mcboms.utils.economics import calculate_discount_factor
        
        df = calculate_discount_factor(0.07, 1)
        expected = 1 / 1.07
        
        assert abs(df - expected) < 1e-10
    
    def test_discount_factor_year_20(self):
        """Test discount factor for year 20 at 7%."""
        from mcboms.utils.economics import calculate_discount_factor
        
        df = calculate_discount_factor(0.07, 20)
        expected = 1 / (1.07 ** 20)
        
        assert abs(df - expected) < 1e-10
    
    def test_present_worth_factor(self):
        """Test uniform-series present worth factor."""
        from mcboms.utils.economics import calculate_present_worth_factor
        
        # At 7% for 20 years
        pwf = calculate_present_worth_factor(0.07, 20)
        
        # Should be approximately 10.594
        assert abs(pwf - 10.594) < 0.01
    
    def test_discount_factors_array(self):
        """Test array of discount factors."""
        from mcboms.utils.economics import calculate_discount_factors
        
        factors = calculate_discount_factors(0.07, 20)
        
        assert len(factors) == 20
        assert factors[0] == pytest.approx(1/1.07, rel=1e-6)
        assert factors[19] == pytest.approx(1/1.07**20, rel=1e-6)
        
        # Factors should be decreasing
        assert all(factors[i] > factors[i+1] for i in range(len(factors)-1))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
