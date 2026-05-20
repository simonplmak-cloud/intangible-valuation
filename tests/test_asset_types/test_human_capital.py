"""Tests for human capital valuation module."""

import pytest

from intangible_valuation.asset_types.human_capital import (
    assembled_workforce_valuation,
    key_person_value,
)


class TestAssembledWorkforceValuation:
    """Tests for assembled_workforce_valuation function."""

    def test_happy_path_basic(self):
        result = assembled_workforce_valuation(
            employee_count=100,
            avg_replacement_cost=50000,
            training_cost=10000,
            productivity_factor=0.70,
            attrition_rate=0.10,
        )
        assert result["value"] > 0
        assert "Replacement Cost" in result["method"]
        assert len(result["steps"]) > 0

    def test_happy_path_large_workforce(self):
        result = assembled_workforce_valuation(
            employee_count=1000,
            avg_replacement_cost=75000,
            training_cost=15000,
            productivity_factor=0.60,
            attrition_rate=0.15,
        )
        assert result["value"] > 0

    def test_happy_path_low_attrition(self):
        result = assembled_workforce_valuation(
            employee_count=50,
            avg_replacement_cost=100000,
            training_cost=20000,
            productivity_factor=0.80,
            attrition_rate=0.02,
        )
        assert result["value"] > 0

    def test_happy_path_zero_attrition(self):
        result = assembled_workforce_valuation(
            employee_count=100,
            avg_replacement_cost=50000,
            training_cost=10000,
            productivity_factor=0.70,
            attrition_rate=0.0,
        )
        assert result["value"] > 0

    def test_error_zero_employees(self):
        with pytest.raises(ValueError):
            assembled_workforce_valuation(
                employee_count=0,
                avg_replacement_cost=50000,
                training_cost=10000,
                productivity_factor=0.70,
                attrition_rate=0.10,
            )

    def test_error_negative_replacement_cost(self):
        with pytest.raises(ValueError):
            assembled_workforce_valuation(
                employee_count=100,
                avg_replacement_cost=-50000,
                training_cost=10000,
                productivity_factor=0.70,
                attrition_rate=0.10,
            )

    def test_error_invalid_productivity(self):
        with pytest.raises(ValueError):
            assembled_workforce_valuation(
                employee_count=100,
                avg_replacement_cost=50000,
                training_cost=10000,
                productivity_factor=1.5,
                attrition_rate=0.10,
            )

    def test_error_invalid_attrition(self):
        with pytest.raises(ValueError):
            assembled_workforce_valuation(
                employee_count=100,
                avg_replacement_cost=50000,
                training_cost=10000,
                productivity_factor=0.70,
                attrition_rate=-0.10,
            )


class TestKeyPersonValue:
    """Tests for key_person_value function."""

    def test_happy_path_basic(self):
        result = key_person_value(
            revenue_contribution=500000,
            replacement_cost=200000,
            departure_probability=0.10,
            discount_rate=0.10,
        )
        assert result["value"] > 0
        assert "Key Person" in result["method"]
        assert len(result["steps"]) > 0

    def test_happy_path_high_revenue(self):
        result = key_person_value(
            revenue_contribution=2000000,
            replacement_cost=500000,
            departure_probability=0.05,
            discount_rate=0.08,
        )
        assert result["value"] > 0

    def test_happy_path_high_departure_risk(self):
        result = key_person_value(
            revenue_contribution=500000,
            replacement_cost=200000,
            departure_probability=0.50,
            discount_rate=0.10,
        )
        # Value should still include replacement cost
        assert result["value"] >= 200000

    def test_happy_path_certain_departure(self):
        result = key_person_value(
            revenue_contribution=500000,
            replacement_cost=200000,
            departure_probability=1.0,
            discount_rate=0.10,
        )
        # With certain departure, only replacement cost remains
        assert result["value"] >= 200000

    def test_happy_path_zero_departure(self):
        result = key_person_value(
            revenue_contribution=500000,
            replacement_cost=200000,
            departure_probability=0.0,
            discount_rate=0.10,
        )
        assert result["value"] > 0

    def test_error_negative_revenue(self):
        with pytest.raises(ValueError):
            key_person_value(
                revenue_contribution=-500000,
                replacement_cost=200000,
                departure_probability=0.10,
                discount_rate=0.10,
            )

    def test_error_negative_replacement_cost(self):
        with pytest.raises(ValueError):
            key_person_value(
                revenue_contribution=500000,
                replacement_cost=-200000,
                departure_probability=0.10,
                discount_rate=0.10,
            )

    def test_error_invalid_departure_probability(self):
        with pytest.raises(ValueError):
            key_person_value(
                revenue_contribution=500000,
                replacement_cost=200000,
                departure_probability=1.5,
                discount_rate=0.10,
            )

    def test_error_negative_discount_rate(self):
        with pytest.raises(ValueError):
            key_person_value(
                revenue_contribution=500000,
                replacement_cost=200000,
                departure_probability=0.10,
                discount_rate=-0.01,
            )
