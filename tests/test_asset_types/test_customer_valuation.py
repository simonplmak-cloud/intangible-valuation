"""Tests for customer valuation module."""

import pytest

from intangible_valuation.asset_types.customer_valuation import (
    backlog_valuation,
    churn_impact_analysis,
    customer_lifetime_value,
    customer_relationship_valuation,
    distribution_network_valuation,
    non_compete_valuation,
)


class TestCustomerRelationshipValuation:
    """Tests for customer_relationship_valuation function."""

    def test_happy_path_basic(self):
        result = customer_relationship_valuation(
            customer_count=1000,
            avg_revenue_per_customer=5000,
            retention_rate=0.85,
            profit_margin=0.20,
            discount_rate=0.10,
            projection_period=5,
        )
        assert result["value"] > 0
        assert "Attrition" in result["method"]
        assert len(result["steps"]) > 0

    def test_happy_path_high_retention(self):
        result = customer_relationship_valuation(
            customer_count=500,
            avg_revenue_per_customer=10000,
            retention_rate=0.95,
            profit_margin=0.30,
            discount_rate=0.08,
            projection_period=10,
        )
        assert result["value"] > 0

    def test_happy_path_low_retention(self):
        result = customer_relationship_valuation(
            customer_count=1000,
            avg_revenue_per_customer=1000,
            retention_rate=0.50,
            profit_margin=0.15,
            discount_rate=0.12,
            projection_period=5,
        )
        assert result["value"] >= 0

    def test_happy_path_zero_retention(self):
        result = customer_relationship_valuation(
            customer_count=1000,
            avg_revenue_per_customer=5000,
            retention_rate=0.0,
            profit_margin=0.20,
            discount_rate=0.10,
            projection_period=5,
        )
        assert result["value"] == 0.0

    def test_error_zero_customers(self):
        with pytest.raises(ValueError):
            customer_relationship_valuation(
                customer_count=0,
                avg_revenue_per_customer=5000,
                retention_rate=0.85,
                profit_margin=0.20,
                discount_rate=0.10,
                projection_period=5,
            )

    def test_error_invalid_retention(self):
        with pytest.raises(ValueError):
            customer_relationship_valuation(
                customer_count=1000,
                avg_revenue_per_customer=5000,
                retention_rate=1.5,
                profit_margin=0.20,
                discount_rate=0.10,
                projection_period=5,
            )

    def test_error_negative_revenue(self):
        with pytest.raises(ValueError):
            customer_relationship_valuation(
                customer_count=1000,
                avg_revenue_per_customer=-5000,
                retention_rate=0.85,
                profit_margin=0.20,
                discount_rate=0.10,
                projection_period=5,
            )


class TestDistributionNetworkValuation:
    """Tests for distribution_network_valuation function."""

    def test_happy_path_basic(self):
        result = distribution_network_valuation(
            channel_count=50,
            revenue_per_channel=200000,
            channel_margin=0.15,
            useful_life=10,
            discount_rate=0.10,
        )
        assert result["value"] > 0
        assert "Distribution Network" in result["method"]

    def test_happy_path_single_channel(self):
        result = distribution_network_valuation(
            channel_count=1,
            revenue_per_channel=500000,
            channel_margin=0.25,
            useful_life=5,
            discount_rate=0.08,
        )
        assert result["value"] > 0

    def test_happy_path_high_margin(self):
        result = distribution_network_valuation(
            channel_count=100,
            revenue_per_channel=100000,
            channel_margin=0.40,
            useful_life=7,
            discount_rate=0.12,
        )
        assert result["value"] > 0

    def test_error_zero_channels(self):
        with pytest.raises(ValueError):
            distribution_network_valuation(
                channel_count=0,
                revenue_per_channel=100000,
                channel_margin=0.15,
                useful_life=5,
                discount_rate=0.10,
            )

    def test_error_negative_revenue(self):
        with pytest.raises(ValueError):
            distribution_network_valuation(
                channel_count=10,
                revenue_per_channel=-100000,
                channel_margin=0.15,
                useful_life=5,
                discount_rate=0.10,
            )

    def test_error_invalid_margin(self):
        with pytest.raises(ValueError):
            distribution_network_valuation(
                channel_count=10,
                revenue_per_channel=100000,
                channel_margin=1.5,
                useful_life=5,
                discount_rate=0.10,
            )


class TestNonCompeteValuation:
    """Tests for non_compete_valuation function."""

    def test_happy_path_basic(self):
        result = non_compete_valuation(
            protected_revenue=1000000,
            profit_margin=0.20,
            term=3,
            enforcement_probability=0.80,
            discount_rate=0.10,
        )
        assert result["value"] > 0
        assert "Non-Compete" in result["method"]

    def test_happy_path_certain_enforcement(self):
        result = non_compete_valuation(
            protected_revenue=500000,
            profit_margin=0.25,
            term=5,
            enforcement_probability=1.0,
            discount_rate=0.08,
        )
        assert result["value"] > 0

    def test_happy_path_zero_enforcement(self):
        result = non_compete_valuation(
            protected_revenue=1000000,
            profit_margin=0.20,
            term=3,
            enforcement_probability=0.0,
            discount_rate=0.10,
        )
        assert result["value"] == 0.0

    def test_error_negative_revenue(self):
        with pytest.raises(ValueError):
            non_compete_valuation(
                protected_revenue=-1000000,
                profit_margin=0.20,
                term=3,
                enforcement_probability=0.80,
                discount_rate=0.10,
            )

    def test_error_invalid_enforcement(self):
        with pytest.raises(ValueError):
            non_compete_valuation(
                protected_revenue=1000000,
                profit_margin=0.20,
                term=3,
                enforcement_probability=-0.1,
                discount_rate=0.10,
            )

    def test_error_zero_term(self):
        with pytest.raises(ValueError):
            non_compete_valuation(
                protected_revenue=1000000,
                profit_margin=0.20,
                term=0,
                enforcement_probability=0.80,
                discount_rate=0.10,
            )

    def test_error_invalid_margin(self):
        with pytest.raises(ValueError):
            non_compete_valuation(
                protected_revenue=1000000,
                profit_margin=-0.10,
                term=3,
                enforcement_probability=0.80,
                discount_rate=0.10,
            )


class TestCustomerLifetimeValue:
    """Tests for customer_lifetime_value function."""

    def test_happy_path_basic(self):
        result = customer_lifetime_value(100, 0.80, 0.10, 0.30)
        assert result["value"] == pytest.approx(80.0, rel=0.01)
        assert "Lifetime Value" in result["method"]

    def test_happy_path_high_retention(self):
        result = customer_lifetime_value(200, 0.95, 0.08, 0.40)
        assert result["value"] > 0

    def test_happy_path_low_margin(self):
        result = customer_lifetime_value(100, 0.70, 0.10, 0.05)
        assert result["value"] > 0

    def test_happy_path_zero_retention(self):
        result = customer_lifetime_value(100, 0.0, 0.10, 0.30)
        assert result["value"] == 0.0

    def test_error_retention_equals_one(self):
        with pytest.raises(ValueError):
            customer_lifetime_value(100, 1.0, 0.10, 0.30)

    def test_error_zero_revenue(self):
        with pytest.raises(ValueError):
            customer_lifetime_value(0, 0.80, 0.10, 0.30)

    def test_error_negative_margin(self):
        with pytest.raises(ValueError):
            customer_lifetime_value(100, 0.80, 0.10, -0.10)

    def test_returns_profit_per_period(self):
        result = customer_lifetime_value(100, 0.80, 0.10, 0.30)
        assert result["assumptions"]["profit_per_period"] == 30.0


class TestBacklogValuation:
    """Tests for backlog_valuation function."""

    def test_happy_path_basic(self):
        backlog = [
            {"value": 500_000, "period": 1},
            {"value": 300_000, "period": 2},
        ]
        result = backlog_valuation(backlog, 0.90, 0.10)
        assert result["value"] > 0
        assert "Backlog" in result["method"]

    def test_happy_path_default_period(self):
        backlog = [
            {"value": 500_000},
            {"value": 300_000},
        ]
        result = backlog_valuation(backlog, 0.90, 0.10)
        assert result["value"] > 0

    def test_happy_path_certain_completion(self):
        backlog = [{"value": 1_000_000, "period": 1}]
        result = backlog_valuation(backlog, 1.0, 0.10)
        assert result["value"] == pytest.approx(1_000_000 / 1.10, rel=0.01)

    def test_happy_path_zero_probability(self):
        backlog = [{"value": 1_000_000, "period": 1}]
        result = backlog_valuation(backlog, 0.0, 0.10)
        assert result["value"] == 0.0

    def test_error_empty_backlog(self):
        with pytest.raises(ValueError):
            backlog_valuation([], 0.90, 0.10)

    def test_error_invalid_probability(self):
        with pytest.raises(ValueError):
            backlog_valuation([{"value": 500_000}], 1.5, 0.10)

    def test_returns_num_contracts(self):
        backlog = [
            {"value": 500_000, "period": 1},
            {"value": 300_000, "period": 2},
            {"value": 200_000, "period": 3},
        ]
        result = backlog_valuation(backlog, 0.90, 0.10)
        assert result["assumptions"]["num_contracts"] == 3


class TestChurnImpactAnalysis:
    """Tests for churn_impact_analysis function."""

    def test_happy_path_churn_reduction(self):
        result = churn_impact_analysis(
            current_customers=1000,
            churn_rate_before=0.20,
            churn_rate_after=0.15,
            revenue_per_customer=5000,
            discount_rate=0.10,
        )
        assert result["value"] > 0
        assert "Churn Impact" in result["method"]

    def test_happy_path_churn_increase(self):
        result = churn_impact_analysis(
            current_customers=1000,
            churn_rate_before=0.10,
            churn_rate_after=0.20,
            revenue_per_customer=5000,
            discount_rate=0.10,
        )
        assert result["value"] < 0

    def test_happy_path_no_change(self):
        result = churn_impact_analysis(
            current_customers=1000,
            churn_rate_before=0.15,
            churn_rate_after=0.15,
            revenue_per_customer=5000,
            discount_rate=0.10,
        )
        assert result["value"] == 0.0

    def test_happy_path_large_base(self):
        result = churn_impact_analysis(
            current_customers=100_000,
            churn_rate_before=0.25,
            churn_rate_after=0.20,
            revenue_per_customer=1000,
            discount_rate=0.08,
        )
        assert result["value"] > 0

    def test_error_zero_customers(self):
        with pytest.raises(ValueError):
            churn_impact_analysis(0, 0.20, 0.15, 5000, 0.10)

    def test_error_churn_rate_one(self):
        with pytest.raises(ValueError):
            churn_impact_analysis(1000, 1.0, 0.15, 5000, 0.10)

    def test_error_zero_revenue(self):
        with pytest.raises(ValueError):
            churn_impact_analysis(1000, 0.20, 0.15, 0, 0.10)

    def test_returns_pv_details(self):
        result = churn_impact_analysis(
            current_customers=1000,
            churn_rate_before=0.20,
            churn_rate_after=0.15,
            revenue_per_customer=5000,
            discount_rate=0.10,
        )
        assert "pv_before" in result["assumptions"]
        assert "pv_after" in result["assumptions"]
