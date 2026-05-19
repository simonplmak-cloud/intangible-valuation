"""Tests for technology valuation module."""

import pytest

from src.asset_types.technology_valuation import (
    data_asset_valuation,
    developed_technology_valuation,
    platform_valuation,
    software_valuation,
)


class TestDevelopedTechnologyValuation:
    """Tests for developed_technology_valuation function."""

    def test_happy_path_emerging(self):
        result = developed_technology_valuation(
            rd_costs=1000000,
            life_cycle_stage="emerging",
            competitive_advantage=5,
            discount_rate=0.08,
            cash_flow_projections=[200000, 300000, 400000, 500000, 600000],
        )
        assert result["value"] > 0
        assert "Life Cycle Risk" in result["method"]
        assert result["assumptions"]["life_cycle_stage"] == "emerging"

    def test_happy_path_mature(self):
        result = developed_technology_valuation(
            rd_costs=500000,
            life_cycle_stage="mature",
            competitive_advantage=10,
            discount_rate=0.10,
            cash_flow_projections=[100000] * 10,
        )
        assert result["value"] > 0

    def test_happy_path_growth(self):
        result = developed_technology_valuation(
            rd_costs=2000000,
            life_cycle_stage="growth",
            competitive_advantage=7,
            discount_rate=0.08,
            cash_flow_projections=[300000, 500000, 700000, 900000],
        )
        assert result["value"] > 0

    def test_happy_path_decline(self):
        result = developed_technology_valuation(
            rd_costs=100000,
            life_cycle_stage="decline",
            competitive_advantage=3,
            discount_rate=0.10,
            cash_flow_projections=[50000, 40000, 30000],
        )
        assert result["value"] > 0

    def test_error_invalid_stage(self):
        with pytest.raises(ValueError):
            developed_technology_valuation(
                rd_costs=100000,
                life_cycle_stage="unknown",
                competitive_advantage=5,
                discount_rate=0.10,
                cash_flow_projections=[100000],
            )

    def test_error_negative_rd_costs(self):
        with pytest.raises(ValueError):
            developed_technology_valuation(
                rd_costs=-100000,
                life_cycle_stage="mature",
                competitive_advantage=5,
                discount_rate=0.10,
                cash_flow_projections=[100000],
            )

    def test_error_negative_cash_flow(self):
        with pytest.raises(ValueError):
            developed_technology_valuation(
                rd_costs=100000,
                life_cycle_stage="mature",
                competitive_advantage=5,
                discount_rate=0.10,
                cash_flow_projections=[-50000],
            )


class TestSoftwareValuation:
    """Tests for software_valuation function."""

    def test_happy_path_subscription(self):
        result = software_valuation(
            development_cost=500000,
            maintenance_cost=100000,
            user_base=10000,
            revenue_model={"type": "subscription", "revenue_per_user": 120},
            useful_life=5,
            discount_rate=0.10,
        )
        assert result["value"] > 0
        assert "Software" in result["method"]

    def test_happy_path_freemium(self):
        result = software_valuation(
            development_cost=200000,
            maintenance_cost=50000,
            user_base=50000,
            revenue_model={"type": "freemium", "revenue_per_user": 5},
            useful_life=3,
            discount_rate=0.12,
        )
        assert result["value"] > 0

    def test_happy_path_cost_dominates(self):
        result = software_valuation(
            development_cost=1000000,
            maintenance_cost=500000,
            user_base=100,
            revenue_model={"type": "license", "revenue_per_user": 10},
            useful_life=3,
            discount_rate=0.10,
        )
        # Cost should dominate when revenue is low
        assert result["value"] >= 1000000

    def test_error_invalid_revenue_model(self):
        with pytest.raises(ValueError):
            software_valuation(
                development_cost=100000,
                maintenance_cost=10000,
                user_base=1000,
                revenue_model={"type": "subscription"},
                useful_life=5,
                discount_rate=0.10,
            )

    def test_error_negative_revenue_per_user(self):
        with pytest.raises(ValueError):
            software_valuation(
                development_cost=100000,
                maintenance_cost=10000,
                user_base=1000,
                revenue_model={"type": "subscription", "revenue_per_user": -10},
                useful_life=5,
                discount_rate=0.10,
            )

    def test_error_negative_development_cost(self):
        with pytest.raises(ValueError):
            software_valuation(
                development_cost=-100000,
                maintenance_cost=10000,
                user_base=1000,
                revenue_model={"type": "subscription", "revenue_per_user": 10},
                useful_life=5,
                discount_rate=0.10,
            )


class TestDataAssetValuation:
    """Tests for data_asset_valuation function."""

    def test_happy_path_high_quality(self):
        result = data_asset_valuation(
            acquisition_cost=100000,
            quality_score=0.95,
            revenue_contribution=50000,
            useful_life=5,
            discount_rate=0.10,
        )
        assert result["value"] > 0
        assert "Quality Adjustment" in result["method"]

    def test_happy_path_low_quality(self):
        result = data_asset_valuation(
            acquisition_cost=100000,
            quality_score=0.20,
            revenue_contribution=50000,
            useful_life=5,
            discount_rate=0.10,
        )
        # Low quality may make cost floor the value
        assert result["value"] >= 0

    def test_happy_path_zero_quality(self):
        result = data_asset_valuation(
            acquisition_cost=50000,
            quality_score=0.0,
            revenue_contribution=100000,
            useful_life=5,
            discount_rate=0.10,
        )
        # With zero quality, income is 0, so cost floor applies
        assert result["value"] >= 50000

    def test_error_invalid_quality_score(self):
        with pytest.raises(ValueError):
            data_asset_valuation(
                acquisition_cost=100000,
                quality_score=1.5,
                revenue_contribution=50000,
                useful_life=5,
                discount_rate=0.10,
            )

    def test_error_negative_acquisition_cost(self):
        with pytest.raises(ValueError):
            data_asset_valuation(
                acquisition_cost=-100000,
                quality_score=0.80,
                revenue_contribution=50000,
                useful_life=5,
                discount_rate=0.10,
            )


class TestPlatformValuation:
    """Tests for platform_valuation function."""

    def test_happy_path_strong_network_effects(self):
        result = platform_valuation(
            network_size=10000,
            network_effects_coefficient=0.50,
            revenue_per_user=50,
            growth_rate=0.20,
            discount_rate=0.10,
        )
        assert result["value"] > 0
        assert "Network Effects" in result["method"]

    def test_happy_path_no_network_effects(self):
        result = platform_valuation(
            network_size=1000,
            network_effects_coefficient=0.0,
            revenue_per_user=100,
            growth_rate=0.0,
            discount_rate=0.10,
        )
        assert result["value"] > 0

    def test_happy_path_high_growth(self):
        result = platform_valuation(
            network_size=5000,
            network_effects_coefficient=0.30,
            revenue_per_user=25,
            growth_rate=0.50,
            discount_rate=0.12,
        )
        assert result["value"] > 0

    def test_error_negative_network_size(self):
        with pytest.raises(ValueError):
            platform_valuation(
                network_size=-100,
                network_effects_coefficient=0.30,
                revenue_per_user=50,
                growth_rate=0.10,
                discount_rate=0.10,
            )

    def test_error_invalid_coefficient(self):
        with pytest.raises(ValueError):
            platform_valuation(
                network_size=1000,
                network_effects_coefficient=1.5,
                revenue_per_user=50,
                growth_rate=0.10,
                discount_rate=0.10,
            )

    def test_error_negative_growth(self):
        with pytest.raises(ValueError):
            platform_valuation(
                network_size=1000,
                network_effects_coefficient=0.30,
                revenue_per_user=50,
                growth_rate=-0.10,
                discount_rate=0.10,
            )
