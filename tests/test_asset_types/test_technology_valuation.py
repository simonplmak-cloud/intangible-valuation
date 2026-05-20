"""Tests for technology valuation module."""

import pytest

from src.asset_types.technology_valuation import (
    algorithm_valuation,
    api_valuation,
    data_asset_valuation,
    developed_technology_valuation,
    platform_valuation,
    software_valuation,
    technology_obsolescence_curve,
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


class TestTechnologyObsolescenceCurve:
    """Tests for technology_obsolescence_curve function."""

    def test_happy_path_basic(self):
        result = technology_obsolescence_curve(1_000_000, 0.20, 5)
        assert result["value"] > 0
        assert result["value"] < 1_000_000
        assert "Obsolescence" in result["method"]

    def test_happy_path_high_obsolescence(self):
        result = technology_obsolescence_curve(1_000_000, 0.50, 3)
        assert result["value"] == pytest.approx(125_000, rel=0.01)

    def test_happy_path_low_obsolescence(self):
        result = technology_obsolescence_curve(1_000_000, 0.05, 5)
        assert result["value"] > 700_000

    def test_happy_path_single_period(self):
        result = technology_obsolescence_curve(1_000_000, 0.20, 1)
        assert result["value"] == pytest.approx(800_000, rel=0.01)

    def test_error_zero_initial_value(self):
        with pytest.raises(ValueError):
            technology_obsolescence_curve(0, 0.20, 5)

    def test_error_zero_obsolescence_rate(self):
        with pytest.raises(ValueError):
            technology_obsolescence_curve(1_000_000, 0, 5)

    def test_error_zero_periods(self):
        with pytest.raises(ValueError):
            technology_obsolescence_curve(1_000_000, 0.20, 0)

    def test_returns_value_at_each_period(self):
        result = technology_obsolescence_curve(1_000_000, 0.20, 3)
        assert "value_at_each_period" in result["assumptions"]
        assert len(result["assumptions"]["value_at_each_period"]) == 3


class TestApiValuation:
    """Tests for api_valuation function."""

    def test_happy_path_basic(self):
        result = api_valuation(
            api_calls_per_month=1_000_000,
            revenue_per_call=0.001,
            growth_rate=0.15,
            useful_life=5,
            discount_rate=0.10,
        )
        assert result["value"] > 0
        assert "API Income" in result["method"]

    def test_happy_path_no_growth(self):
        result = api_valuation(
            api_calls_per_month=500_000,
            revenue_per_call=0.005,
            growth_rate=0.0,
            useful_life=3,
            discount_rate=0.10,
        )
        assert result["value"] > 0

    def test_happy_path_high_volume(self):
        result = api_valuation(
            api_calls_per_month=10_000_000,
            revenue_per_call=0.0001,
            growth_rate=0.20,
            useful_life=7,
            discount_rate=0.12,
        )
        assert result["value"] > 0

    def test_error_zero_calls(self):
        with pytest.raises(ValueError):
            api_valuation(
                api_calls_per_month=0,
                revenue_per_call=0.001,
                growth_rate=0.10,
                useful_life=5,
                discount_rate=0.10,
            )

    def test_error_zero_discount_rate(self):
        with pytest.raises(ValueError):
            api_valuation(
                api_calls_per_month=1_000_000,
                revenue_per_call=0.001,
                growth_rate=0.10,
                useful_life=5,
                discount_rate=0,
            )

    def test_error_zero_useful_life(self):
        with pytest.raises(ValueError):
            api_valuation(
                api_calls_per_month=1_000_000,
                revenue_per_call=0.001,
                growth_rate=0.10,
                useful_life=0,
                discount_rate=0.10,
            )

    def test_returns_year1_revenue(self):
        result = api_valuation(
            api_calls_per_month=1_000_000,
            revenue_per_call=0.001,
            growth_rate=0.0,
            useful_life=1,
            discount_rate=0.10,
        )
        assert "year1_revenue" in result["assumptions"]


class TestAlgorithmValuation:
    """Tests for algorithm_valuation function."""

    def test_happy_path_basic(self):
        result = algorithm_valuation(
            computational_savings=500_000,
            deployment_scale=3.0,
            competitive_advantage_years=5,
            discount_rate=0.12,
        )
        assert result["value"] > 0
        assert "Algorithm" in result["method"]

    def test_happy_path_single_year(self):
        result = algorithm_valuation(
            computational_savings=1_000_000,
            deployment_scale=1.0,
            competitive_advantage_years=1,
            discount_rate=0.10,
        )
        assert result["value"] == pytest.approx(1_000_000 / 1.10, rel=0.01)

    def test_happy_path_large_scale(self):
        result = algorithm_valuation(
            computational_savings=100_000,
            deployment_scale=10.0,
            competitive_advantage_years=7,
            discount_rate=0.10,
        )
        assert result["value"] > 0

    def test_error_zero_savings(self):
        with pytest.raises(ValueError):
            algorithm_valuation(
                computational_savings=0,
                deployment_scale=1.0,
                competitive_advantage_years=5,
                discount_rate=0.10,
            )

    def test_error_zero_scale(self):
        with pytest.raises(ValueError):
            algorithm_valuation(
                computational_savings=500_000,
                deployment_scale=0,
                competitive_advantage_years=5,
                discount_rate=0.10,
            )

    def test_error_zero_advantage_years(self):
        with pytest.raises(ValueError):
            algorithm_valuation(
                computational_savings=500_000,
                deployment_scale=1.0,
                competitive_advantage_years=0,
                discount_rate=0.10,
            )

    def test_returns_annual_benefit(self):
        result = algorithm_valuation(
            computational_savings=500_000,
            deployment_scale=2.0,
            competitive_advantage_years=3,
            discount_rate=0.10,
        )
        assert result["assumptions"]["annual_benefit"] == 1_000_000
