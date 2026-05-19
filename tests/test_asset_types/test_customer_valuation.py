"""Tests for customer valuation module."""

import pytest

from src.asset_types.customer_valuation import (
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
