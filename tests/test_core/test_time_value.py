"""Tests for time value of money functions.

Verifies all TVM functions against textbook examples from Chapter 2.
"""

import math

import pytest

from intangible_valuation.core.time_value import (
    ValuationResult,
    annuity_due_pv,
    annuity_pv,
    continuous_compounding,
    effective_annual_rate,
    future_value,
    growing_annuity_pv,
    growing_perpetuity_pv,
    perpetuity_pv,
    present_value,
    present_value_graduated,
    terminal_value,
)


class TestPresentValue:
    """Test present_value function."""

    def test_basic_q1_book_example(self):
        """Ch 2 Basic Q1: PV of $500,000 in 8 years at 10% = $233,253."""
        result = present_value(future_value=500_000, discount_rate=0.10, periods=8)
        assert isinstance(result, ValuationResult)
        assert math.isclose(result.value, 233_253, abs_tol=1)
        assert result.method == "Present Value of Single Sum"
        assert "PV = FV / (1 + r)^n" in result.formula_reference
        assert len(result.steps) > 0
        assert len(result.assumptions) > 0

    def test_pv_one_period(self):
        """PV of $100 in 1 year at 5%."""
        result = present_value(future_value=100, discount_rate=0.05, periods=1)
        assert math.isclose(result.value, 100 / 1.05, abs_tol=0.01)

    def test_pv_zero_periods(self):
        """PV of $1000 in 0 periods = $1000."""
        result = present_value(future_value=1_000, discount_rate=0.10, periods=0)
        assert math.isclose(result.value, 1_000, abs_tol=0.01)

    def test_pv_large_discount_rate(self):
        """High discount rate should produce low PV."""
        result = present_value(future_value=1_000, discount_rate=0.50, periods=5)
        assert result.value < 1_000
        assert result.value > 0

    def test_pv_negative_future_value_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            present_value(future_value=-100, discount_rate=0.10, periods=5)

    def test_pv_negative_periods_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            present_value(future_value=100, discount_rate=0.10, periods=-1)

    def test_pv_rate_less_than_minus_one_raises(self):
        with pytest.raises(ValueError):
            present_value(future_value=100, discount_rate=-1.5, periods=5)


class TestFutureValue:
    """Test future_value function."""

    def test_basic_q2_book_example(self):
        """Ch 2 Basic Q2: FV $1M, PV $620,921, 5 years -> discount rate = 10%.
        Verify: FV of $620,921 at 10% for 5 years = ~$1,000,000."""
        result = future_value(present_value=620_921, discount_rate=0.10, periods=5)
        assert math.isclose(result.value, 1_000_000, abs_tol=100)
        assert result.method == "Future Value of Single Sum"

    def test_fv_one_period(self):
        """FV of $100 for 1 year at 5% = $105."""
        result = future_value(present_value=100, discount_rate=0.05, periods=1)
        assert math.isclose(result.value, 105, abs_tol=0.01)

    def test_fv_zero_periods(self):
        """FV of $1000 in 0 periods = $1000."""
        result = future_value(present_value=1_000, discount_rate=0.10, periods=0)
        assert math.isclose(result.value, 1_000, abs_tol=0.01)

    def test_fv_negative_present_value_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            future_value(present_value=-100, discount_rate=0.10, periods=5)

    def test_fv_negative_periods_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            future_value(present_value=100, discount_rate=0.10, periods=-1)


class TestAnnuityPV:
    """Test annuity_pv function."""

    def test_intermediate_q1_book_example(self):
        """Ch 2 Intermediate Q1: Annuity $50,000 for 10 years at 15% = $250,937."""
        result = annuity_pv(payment=50_000, discount_rate=0.15, periods=10)
        assert math.isclose(result.value, 250_937, abs_tol=10)
        assert result.method == "Present Value of Ordinary Annuity"

    def test_ch3_example_book(self):
        """Ch 3 Example: PV of $200,000/year for 10 years at 18% = $898,264."""
        result = annuity_pv(payment=200_000, discount_rate=0.18, periods=10)
        assert math.isclose(result.value, 898_264, abs_tol=600)

    def test_annuity_single_payment(self):
        """Annuity of $100 for 1 period at 10% = $90.91."""
        result = annuity_pv(payment=100, discount_rate=0.10, periods=1)
        assert math.isclose(result.value, 100 / 1.10, abs_tol=0.01)

    def test_annuity_zero_periods(self):
        """Annuity for 0 periods = 0."""
        result = annuity_pv(payment=100, discount_rate=0.10, periods=0)
        assert math.isclose(result.value, 0, abs_tol=0.01)

    def test_annuity_zero_rate_raises(self):
        with pytest.raises(ValueError, match="cannot be zero"):
            annuity_pv(payment=100, discount_rate=0.0, periods=5)

    def test_annuity_negative_payment_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            annuity_pv(payment=-100, discount_rate=0.10, periods=5)


class TestPerpetuityPV:
    """Test perpetuity_pv function."""

    def test_ch3_royalty_relief_book_example(self):
        """Ch 3 Example: Trademark $10M revenue, 4% royalty, 15% discount = $2,666,667."""
        annual_royalty = 10_000_000 * 0.04  # $400,000
        result = perpetuity_pv(payment=annual_royalty, discount_rate=0.15)
        assert math.isclose(result.value, 2_666_667, abs_tol=1)
        assert result.method == "Present Value of Perpetuity"

    def test_perpetuity_simple(self):
        """PV of $100/year perpetuity at 10% = $1,000."""
        result = perpetuity_pv(payment=100, discount_rate=0.10)
        assert math.isclose(result.value, 1_000, abs_tol=0.01)

    def test_perpetuity_zero_rate_raises(self):
        with pytest.raises(ValueError, match="positive"):
            perpetuity_pv(payment=100, discount_rate=0.0)

    def test_perpetuity_negative_rate_raises(self):
        with pytest.raises(ValueError, match="positive"):
            perpetuity_pv(payment=100, discount_rate=-0.05)

    def test_perpetuity_negative_payment_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            perpetuity_pv(payment=-100, discount_rate=0.10)


class TestGrowingAnnuityPV:
    """Test growing_annuity_pv function."""

    def test_growing_annuity_basic(self):
        """$100 payment, 5% growth, 10% discount, 5 periods."""
        result = growing_annuity_pv(payment=100, discount_rate=0.10, growth_rate=0.05, periods=5)
        assert result.value > 0
        assert result.method == "Present Value of Growing Annuity"

    def test_growing_annuity_equal_rates(self):
        """When r = g, special formula applies."""
        result = growing_annuity_pv(payment=100, discount_rate=0.10, growth_rate=0.10, periods=5)
        expected = 100 * 5 / 1.10
        assert math.isclose(result.value, expected, abs_tol=0.01)

    def test_growing_annuity_no_growth(self):
        """Zero growth should approximate ordinary annuity."""
        ga_result = growing_annuity_pv(payment=100, discount_rate=0.10, growth_rate=0.0, periods=5)
        ann_result = annuity_pv(payment=100, discount_rate=0.10, periods=5)
        assert math.isclose(ga_result.value, ann_result.value, abs_tol=0.01)

    def test_growing_annuity_negative_growth(self):
        """Negative growth rate should produce lower PV."""
        result = growing_annuity_pv(payment=100, discount_rate=0.10, growth_rate=-0.05, periods=5)
        assert result.value > 0
        assert result.value < 100 * 5

    def test_growing_annuity_negative_payment_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            growing_annuity_pv(payment=-100, discount_rate=0.10, growth_rate=0.05, periods=5)


class TestTerminalValue:
    """Test terminal_value function."""

    def test_gordon_growth_basic(self):
        """TV with $100 FCF, 3% growth, 10% discount."""
        result = terminal_value(
            final_year_cashflow=100,
            perpetual_growth_rate=0.03,
            discount_rate=0.10,
            method="gordon_growth",
        )
        expected = 100 * 1.03 / (0.10 - 0.03)
        assert math.isclose(result.value, expected, abs_tol=0.01)
        assert result.method == "Gordon Growth Model"

    def test_exit_multiple_basic(self):
        """TV with $100 FCF and 8x multiple."""
        result = terminal_value(
            final_year_cashflow=100,
            perpetual_growth_rate=0.0,
            discount_rate=0.10,
            method="exit_multiple",
            exit_multiple=8.0,
        )
        assert math.isclose(result.value, 800, abs_tol=0.01)
        assert result.method == "Exit Multiple Method"

    def test_gordon_growth_rate_ge_discount_raises(self):
        with pytest.raises(ValueError, match="must be greater"):
            terminal_value(
                final_year_cashflow=100,
                perpetual_growth_rate=0.10,
                discount_rate=0.10,
                method="gordon_growth",
            )

    def test_exit_multiple_without_multiple_raises(self):
        with pytest.raises(ValueError, match="exit_multiple is required"):
            terminal_value(
                final_year_cashflow=100,
                perpetual_growth_rate=0.03,
                discount_rate=0.10,
                method="exit_multiple",
            )

    def test_exit_multiple_negative_raises(self):
        with pytest.raises(ValueError, match="positive"):
            terminal_value(
                final_year_cashflow=100,
                perpetual_growth_rate=0.03,
                discount_rate=0.10,
                method="exit_multiple",
                exit_multiple=-1.0,
            )

    def test_unknown_method_raises(self):
        with pytest.raises(ValueError, match="Unknown method"):
            terminal_value(
                final_year_cashflow=100,
                perpetual_growth_rate=0.03,
                discount_rate=0.10,
                method="unknown",
            )

    def test_negative_cashflow_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            terminal_value(
                final_year_cashflow=-100,
                perpetual_growth_rate=0.03,
                discount_rate=0.10,
                method="gordon_growth",
            )


class TestPresentValueGraduated:
    """Test present_value_graduated function."""

    def test_basic_graduated(self):
        """3 periods with increasing discount rates."""
        result = present_value_graduated(
            cash_flows=[100, 200, 300],
            discount_rates=[0.05, 0.055, 0.06],
        )
        assert result.value > 0
        assert result.method == "Present Value with Graduated Discount Rates"
        assert len(result.pv_by_period) == 3

    def test_graduated_vs_flat(self):
        """When all rates are equal, should match flat discount PV."""
        from intangible_valuation.core.time_value import present_value_of_series
        flat = present_value_of_series([100, 200, 300], discount_rate=0.10)
        graduated = present_value_graduated(
            cash_flows=[100, 200, 300],
            discount_rates=[0.10, 0.10, 0.10],
        )
        assert math.isclose(flat.value, graduated.value, abs_tol=0.01)

    def test_graduated_single_period(self):
        """Single period should match simple PV."""
        result = present_value_graduated(
            cash_flows=[1000],
            discount_rates=[0.10],
        )
        expected = 1000 / 1.10
        assert math.isclose(result.value, expected, abs_tol=0.01)

    def test_graduated_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="must match"):
            present_value_graduated(
                cash_flows=[100, 200],
                discount_rates=[0.05, 0.06, 0.07],
            )

    def test_graduated_empty_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            present_value_graduated(cash_flows=[], discount_rates=[])

    def test_graduated_invalid_rate_raises(self):
        with pytest.raises(ValueError, match="must be > -1.0"):
            present_value_graduated(
                cash_flows=[100, 200],
                discount_rates=[0.05, -1.5],
            )


class TestAnnuityDuePV:
    """Test annuity_due_pv function."""

    def test_basic_annuity_due(self):
        """$1000 payment, 8% rate, 5 periods, beginning of period."""
        result = annuity_due_pv(payment=1000, discount_rate=0.08, periods=5)
        ordinary = annuity_pv(payment=1000, discount_rate=0.08, periods=5)
        expected = ordinary.value * 1.08
        assert math.isclose(result.value, expected, abs_tol=0.01)

    def test_annuity_due_vs_ordinary(self):
        """Annuity due should be higher than ordinary annuity."""
        due = annuity_due_pv(payment=100, discount_rate=0.10, periods=5)
        ordinary = annuity_pv(payment=100, discount_rate=0.10, periods=5)
        assert due.value > ordinary.value

    def test_annuity_due_zero_periods(self):
        """Zero periods should return 0."""
        result = annuity_due_pv(payment=100, discount_rate=0.10, periods=0)
        assert math.isclose(result.value, 0, abs_tol=0.01)

    def test_annuity_due_zero_rate(self):
        """Zero rate should return payment * periods."""
        result = annuity_due_pv(payment=100, discount_rate=0.0, periods=5)
        assert math.isclose(result.value, 500, abs_tol=0.01)

    def test_annuity_due_single_period(self):
        """Single period annuity due = payment (paid immediately)."""
        result = annuity_due_pv(payment=100, discount_rate=0.10, periods=1)
        assert math.isclose(result.value, 100, abs_tol=0.01)

    def test_annuity_due_negative_payment_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            annuity_due_pv(payment=-100, discount_rate=0.10, periods=5)

    def test_annuity_due_negative_periods_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            annuity_due_pv(payment=100, discount_rate=0.10, periods=-1)


class TestGrowingPerpetuityPV:
    """Test growing_perpetuity_pv function."""

    def test_basic_growing_perpetuity(self):
        """$100 payment, 10% discount, 3% growth."""
        result = growing_perpetuity_pv(first_payment=100, discount_rate=0.10, growth_rate=0.03)
        expected = 100 / (0.10 - 0.03)
        assert math.isclose(result.value, expected, abs_tol=0.01)

    def test_growing_perpetuity_vs_perpetuity(self):
        """Zero growth should match simple perpetuity."""
        gp = growing_perpetuity_pv(first_payment=100, discount_rate=0.10, growth_rate=0.0)
        p = perpetuity_pv(payment=100, discount_rate=0.10)
        assert math.isclose(gp.value, p.value, abs_tol=0.01)

    def test_growing_perpetuity_rate_equals_growth_raises(self):
        with pytest.raises(ValueError, match="must be greater"):
            growing_perpetuity_pv(first_payment=100, discount_rate=0.05, growth_rate=0.05)

    def test_growing_perpetuity_rate_less_than_growth_raises(self):
        with pytest.raises(ValueError, match="must be greater"):
            growing_perpetuity_pv(first_payment=100, discount_rate=0.03, growth_rate=0.05)

    def test_growing_perpetuity_negative_payment_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            growing_perpetuity_pv(first_payment=-100, discount_rate=0.10, growth_rate=0.03)


class TestEffectiveAnnualRate:
    """Test effective_annual_rate function."""

    def test_annual_compounding(self):
        """Annual compounding: EAR = nominal rate."""
        result = effective_annual_rate(nominal_rate=0.12, compounding_periods=1)
        assert math.isclose(result.value, 0.12, abs_tol=1e-6)

    def test_monthly_compounding(self):
        """12% nominal, monthly: EAR = (1 + 0.12/12)^12 - 1 = 12.68%."""
        result = effective_annual_rate(nominal_rate=0.12, compounding_periods=12)
        expected = (1 + 0.12 / 12) ** 12 - 1
        assert math.isclose(result.value, expected, abs_tol=1e-6)

    def test_daily_compounding(self):
        """Daily compounding produces higher EAR than monthly."""
        monthly = effective_annual_rate(nominal_rate=0.12, compounding_periods=12)
        daily = effective_annual_rate(nominal_rate=0.12, compounding_periods=365)
        assert daily.value > monthly.value

    def test_semi_annual_compounding(self):
        """10% nominal, semi-annual: EAR = (1 + 0.10/2)^2 - 1 = 10.25%."""
        result = effective_annual_rate(nominal_rate=0.10, compounding_periods=2)
        assert math.isclose(result.value, 0.1025, abs_tol=1e-6)

    def test_zero_periods_raises(self):
        with pytest.raises(ValueError, match="at least 1"):
            effective_annual_rate(nominal_rate=0.10, compounding_periods=0)

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError, match=">= -1.0"):
            effective_annual_rate(nominal_rate=-2.0, compounding_periods=12)


class TestContinuousCompounding:
    """Test continuous_compounding function."""

    def test_basic_continuous(self):
        """$1000 at 5% for 3 years: FV = 1000 * e^(0.05*3) = ~$1,161.83."""
        result = continuous_compounding(principal=1000, rate=0.05, time=3)
        expected = 1000 * math.exp(0.05 * 3)
        assert math.isclose(result.value, expected, abs_tol=0.01)

    def test_zero_time(self):
        """Zero time: FV = PV."""
        result = continuous_compounding(principal=1000, rate=0.05, time=0)
        assert math.isclose(result.value, 1000, abs_tol=0.01)

    def test_continuous_vs_discrete(self):
        """Continuous should produce higher FV than annual compounding."""
        from intangible_valuation.core.time_value import future_value
        discrete = future_value(present_value=1000, discount_rate=0.05, periods=3)
        continuous = continuous_compounding(principal=1000, rate=0.05, time=3)
        assert continuous.value > discrete.value

    def test_large_values(self):
        """Large principal and long time period."""
        result = continuous_compounding(principal=1_000_000, rate=0.08, time=30)
        expected = 1_000_000 * math.exp(0.08 * 30)
        assert math.isclose(result.value, expected, abs_tol=1)

    def test_negative_principal_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            continuous_compounding(principal=-1000, rate=0.05, time=3)

    def test_negative_time_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            continuous_compounding(principal=1000, rate=0.05, time=-1)


class TestValuationResult:
    """Test ValuationResult model."""

    def test_to_dict(self):
        result = ValuationResult(
            value=100.0,
            method="test",
            formula_reference="ref",
            steps=["step1"],
            assumptions=["assumption1"],
        )
        d = result.to_dict()
        assert d["value"] == 100.0
        assert d["method"] == "test"
        assert d["formula_reference"] == "ref"
        assert d["steps"] == ["step1"]
        assert d["assumptions"] == ["assumption1"]

    def test_default_fields(self):
        result = ValuationResult(value=100.0, method="test", formula_reference="ref")
        assert result.steps == []
        assert result.assumptions == []
