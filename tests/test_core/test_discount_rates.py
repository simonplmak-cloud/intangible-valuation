"""Tests for discount rate construction functions.

Verifies all discount rate functions against textbook examples and edge cases.
"""

import math
import pytest

from src.core.discount_rates import (
    build_up_discount_rate,
    capm_discount_rate,
    control_premium,
    currency_adjusted_discount_rate,
    dlom_finnerty,
    tax_amortization_benefit,
    wacc,
)


class TestBuildUpDiscountRate:
    """Test build_up_discount_rate function."""

    def test_basic_build_up(self):
        """Basic build-up with risk-free 4% and ERP 6%."""
        result = build_up_discount_rate(
            risk_free_rate=0.04,
            equity_risk_premium=0.06,
        )
        assert math.isclose(result.value, 0.10, abs_tol=1e-6)
        assert result.method == "build_up"
        assert len(result.steps) > 0

    def test_build_up_with_all_premiums(self):
        """Build-up with size, industry, and specific risk premiums."""
        result = build_up_discount_rate(
            risk_free_rate=0.04,
            equity_risk_premium=0.06,
            size_premium=0.02,
            industry_risk_premium=0.01,
            specific_risk_premium=0.03,
        )
        assert math.isclose(result.value, 0.16, abs_tol=1e-6)

    def test_build_up_zero_premiums(self):
        """Build-up with only base components."""
        result = build_up_discount_rate(
            risk_free_rate=0.05,
            equity_risk_premium=0.05,
        )
        assert math.isclose(result.value, 0.10, abs_tol=1e-6)

    def test_build_up_negative_rf_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            build_up_discount_rate(risk_free_rate=-0.01, equity_risk_premium=0.06)

    def test_build_up_negative_erp_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            build_up_discount_rate(risk_free_rate=0.04, equity_risk_premium=-0.01)


class TestCAPMDiscountRate:
    """Test capm_discount_rate function."""

    def test_basic_capm(self):
        """CAPM with Rf=4%, beta=1.2, Rm=10%."""
        result = capm_discount_rate(
            risk_free_rate=0.04,
            beta=1.2,
            market_return=0.10,
        )
        expected = 0.04 + 1.2 * (0.10 - 0.04)  # 0.112
        assert math.isclose(result.value, expected, abs_tol=1e-6)
        assert result.method == "capm"

    def test_capm_beta_one(self):
        """Beta=1 should give market return."""
        result = capm_discount_rate(
            risk_free_rate=0.04,
            beta=1.0,
            market_return=0.10,
        )
        assert math.isclose(result.value, 0.10, abs_tol=1e-6)

    def test_capm_beta_zero(self):
        """Beta=0 should give risk-free rate."""
        result = capm_discount_rate(
            risk_free_rate=0.04,
            beta=0.0,
            market_return=0.10,
        )
        assert math.isclose(result.value, 0.04, abs_tol=1e-6)

    def test_capm_beta_negative(self):
        """Negative beta should give rate below risk-free."""
        result = capm_discount_rate(
            risk_free_rate=0.04,
            beta=-0.5,
            market_return=0.10,
        )
        assert result.value < 0.04

    def test_capm_market_below_rf_raises(self):
        with pytest.raises(ValueError, match="market_return must be >= risk_free_rate"):
            capm_discount_rate(risk_free_rate=0.04, beta=1.0, market_return=0.02)


class TestWACC:
    """Test wacc function."""

    def test_basic_wacc(self):
        """WACC with 60% equity at 12%, 40% debt at 6%, tax 25%."""
        result = wacc(
            equity_value=600,
            debt_value=400,
            cost_of_equity=0.12,
            cost_of_debt=0.06,
            tax_rate=0.25,
        )
        expected = 0.6 * 0.12 + 0.4 * 0.06 * 0.75  # 0.09
        assert math.isclose(result.value, expected, abs_tol=1e-6)
        assert result.method == "wacc"

    def test_wacc_all_equity(self):
        """All equity financing."""
        result = wacc(
            equity_value=1000,
            debt_value=0,
            cost_of_equity=0.12,
            cost_of_debt=0.06,
            tax_rate=0.25,
        )
        assert math.isclose(result.value, 0.12, abs_tol=1e-6)

    def test_wacc_all_debt(self):
        """All debt financing."""
        result = wacc(
            equity_value=0,
            debt_value=1000,
            cost_of_equity=0.12,
            cost_of_debt=0.06,
            tax_rate=0.25,
        )
        expected = 0.06 * 0.75
        assert math.isclose(result.value, expected, abs_tol=1e-6)

    def test_wacc_zero_capital_raises(self):
        with pytest.raises(ValueError, match="Total capital"):
            wacc(
                equity_value=0,
                debt_value=0,
                cost_of_equity=0.12,
                cost_of_debt=0.06,
                tax_rate=0.25,
            )

    def test_wacc_negative_equity_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            wacc(
                equity_value=-100,
                debt_value=400,
                cost_of_equity=0.12,
                cost_of_debt=0.06,
                tax_rate=0.25,
            )


class TestTaxAmortizationBenefit:
    """Test tax_amortization_benefit function."""

    def test_tab_basic(self):
        """TAB for $1M asset, 10% discount, 10 year life, 25% tax."""
        result = tax_amortization_benefit(
            discount_rate=0.10,
            useful_life=10,
            tax_rate=0.25,
            asset_value=1_000_000,
        )
        assert result.value > 0
        assert result.value < 1_000_000 * 0.25  # Less than full tax shield

    def test_tab_longer_life_higher_value(self):
        """Longer useful life spreads amortization, reducing annual tax savings PV."""
        result_short = tax_amortization_benefit(
            discount_rate=0.10, useful_life=5,
            tax_rate=0.25, asset_value=1_000_000,
        )
        result_long = tax_amortization_benefit(
            discount_rate=0.10, useful_life=15,
            tax_rate=0.25, asset_value=1_000_000,
        )
        assert result_short.value > result_long.value

    def test_tab_zero_rate(self):
        """At zero discount rate, TAB = asset_value * tax_rate."""
        result = tax_amortization_benefit(
            discount_rate=0.0,
            useful_life=10,
            tax_rate=0.25,
            asset_value=1_000_000,
        )
        assert math.isclose(result.value, 250_000, abs_tol=1)

    def test_tab_negative_asset_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            tax_amortization_benefit(
                discount_rate=0.10, useful_life=10,
                tax_rate=0.25, asset_value=-100,
            )

    def test_tab_zero_life_raises(self):
        with pytest.raises(ValueError, match="positive"):
            tax_amortization_benefit(
                discount_rate=0.10, useful_life=0,
                tax_rate=0.25, asset_value=1_000_000,
            )


class TestControlPremium:
    """Test control_premium function."""

    def test_basic_control_premium(self):
        """Control price $120, minority price $100 -> 20% premium."""
        result = control_premium(minority_price=100, control_price=120)
        assert math.isclose(result.value, 0.20, abs_tol=1e-6)

    def test_equal_prices(self):
        """Equal prices -> 0% premium."""
        result = control_premium(minority_price=100, control_price=100)
        assert math.isclose(result.value, 0.0, abs_tol=1e-6)

    def test_large_premium(self):
        """50% premium."""
        result = control_premium(minority_price=100, control_price=150)
        assert math.isclose(result.value, 0.50, abs_tol=1e-6)

    def test_control_below_minority_raises(self):
        with pytest.raises(ValueError, match="must be >="):
            control_premium(minority_price=100, control_price=80)

    def test_zero_minority_price_raises(self):
        with pytest.raises(ValueError, match="positive"):
            control_premium(minority_price=0, control_price=100)


class TestDLOMFinnerty:
    """Test dlom_finnerty function."""

    def test_basic_dlom(self):
        """DLOM with 2 year restriction, 30% volatility, 4% risk-free."""
        result = dlom_finnerty(
            restricted_period=2.0,
            volatility=0.30,
            risk_free_rate=0.04,
        )
        assert 0 < result.value < 1
        assert result.method == "finnerty"

    def test_longer_restriction_higher_dlom(self):
        """Longer restriction period should produce higher DLOM."""
        result_short = dlom_finnerty(
            restricted_period=1.0, volatility=0.30, risk_free_rate=0.04,
        )
        result_long = dlom_finnerty(
            restricted_period=3.0, volatility=0.30, risk_free_rate=0.04,
        )
        assert result_long.value > result_short.value

    def test_higher_volatility_higher_dlom(self):
        """Higher volatility should produce higher DLOM."""
        result_low = dlom_finnerty(
            restricted_period=2.0, volatility=0.20, risk_free_rate=0.04,
        )
        result_high = dlom_finnerty(
            restricted_period=2.0, volatility=0.40, risk_free_rate=0.04,
        )
        assert result_high.value > result_low.value

    def test_zero_restriction_raises(self):
        with pytest.raises(ValueError, match="positive"):
            dlom_finnerty(restricted_period=0, volatility=0.30, risk_free_rate=0.04)

    def test_zero_volatility_raises(self):
        with pytest.raises(ValueError, match="positive"):
            dlom_finnerty(restricted_period=2.0, volatility=0, risk_free_rate=0.04)


class TestCurrencyAdjustedDiscountRate:
    """Test currency_adjusted_discount_rate function."""

    def test_basic_adjustment(self):
        """Base 10%, currency risk 2%, country risk 3%."""
        result = currency_adjusted_discount_rate(
            base_rate=0.10,
            currency_risk_premium=0.02,
            country_risk_premium=0.03,
        )
        assert math.isclose(result.value, 0.15, abs_tol=1e-6)

    def test_no_premiums(self):
        """Base rate with no additional premiums."""
        result = currency_adjusted_discount_rate(
            base_rate=0.12,
        )
        assert math.isclose(result.value, 0.12, abs_tol=1e-6)

    def test_emerging_market(self):
        """Emerging market with high country risk."""
        result = currency_adjusted_discount_rate(
            base_rate=0.10,
            currency_risk_premium=0.03,
            country_risk_premium=0.05,
        )
        assert math.isclose(result.value, 0.18, abs_tol=1e-6)

    def test_negative_currency_premium_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            currency_adjusted_discount_rate(
                base_rate=0.10,
                currency_risk_premium=-0.01,
            )
