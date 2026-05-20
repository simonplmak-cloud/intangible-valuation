"""Edge case tests for ALL core functions.

Tests boundary conditions, extreme values, floating point precision,
and edge cases across time_value, discount_rates, and statistics modules.
"""

import math
import pytest

from src.core.time_value import (
    present_value,
    future_value,
    annuity_pv,
    perpetuity_pv,
    growing_annuity_pv,
    terminal_value,
    present_value_of_series,
    present_value_graduated,
    annuity_due_pv,
    growing_perpetuity_pv,
    effective_annual_rate,
    continuous_compounding,
)
from src.core.discount_rates import (
    build_up_discount_rate,
    capm_discount_rate,
    wacc,
    tax_amortization_benefit,
    control_premium,
    dlom_finnerty,
    currency_adjusted_discount_rate,
    wacc_with_preferred,
    implied_erp,
    beta_unlevered,
    beta_relevered,
    cost_of_equity_fama_french,
    build_up_with_country_risk,
)
from src.core.statistics import (
    monte_carlo_valuation,
    decision_tree_valuation,
    monte_carlo_with_correlation,
    sensitivity_tornado,
    scenario_analysis,
)


class TestPresentValueEdgeCases:
    """Edge cases for present_value."""

    @pytest.mark.parametrize("fv,rate,periods,expected", [
        (1_000_000, 0.0, 5, 1_000_000.0),
        (1_000_000, 0.0001, 1, 999_900.01),
        (1e12, 0.10, 10, 385_543_289_429.53),
        (1, 0.10, 0, 1.0),
        (1_000, 0.50, 1, 666.67),
    ])
    def test_parametrized_pv(self, fv, rate, periods, expected):
        result = present_value(future_value=fv, discount_rate=rate, periods=periods)
        assert math.isclose(result.value, expected, rel_tol=1e-6, abs_tol=1)

    def test_very_large_value(self):
        result = present_value(future_value=1e15, discount_rate=0.05, periods=20)
        assert result.value > 0
        assert math.isfinite(result.value)

    def test_very_small_rate(self):
        result = present_value(future_value=1_000_000, discount_rate=0.0001, periods=10)
        assert math.isclose(result.value, 999_000.50, rel_tol=1e-4)

    def test_zero_periods(self):
        result = present_value(future_value=500_000, discount_rate=0.10, periods=0)
        assert math.isclose(result.value, 500_000, abs_tol=0.01)

    def test_negative_rate_boundary(self):
        result = present_value(future_value=1_000_000, discount_rate=-0.5, periods=2)
        assert math.isclose(result.value, 4_000_000, abs_tol=1)

    def test_negative_fv_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            present_value(future_value=-100, discount_rate=0.10, periods=5)

    def test_negative_periods_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            present_value(future_value=100, discount_rate=0.10, periods=-1)


class TestFutureValueEdgeCases:
    """Edge cases for future_value."""

    @pytest.mark.parametrize("pv,rate,periods,expected", [
        (1_000, 0.0, 5, 1_000.0),
        (1_000, 0.0001, 1, 1_000.10),
        (1, 0.10, 0, 1.0),
        (1e12, 0.05, 30, 4_321_942_375_151.64),
    ])
    def test_parametrized_fv(self, pv, rate, periods, expected):
        result = future_value(present_value=pv, discount_rate=rate, periods=periods)
        assert math.isclose(result.value, expected, rel_tol=1e-4, abs_tol=1)

    def test_very_large_value(self):
        result = future_value(present_value=1e12, discount_rate=0.08, periods=50)
        assert result.value > 1e12
        assert math.isfinite(result.value)

    def test_zero_periods(self):
        result = future_value(present_value=1_000_000, discount_rate=0.10, periods=0)
        assert math.isclose(result.value, 1_000_000, abs_tol=0.01)

    def test_negative_pv_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            future_value(present_value=-100, discount_rate=0.10, periods=5)


class TestAnnuityPVEdgeCases:
    """Edge cases for annuity_pv."""

    def test_very_small_rate(self):
        result = annuity_pv(payment=1_000, discount_rate=0.0001, periods=10)
        assert result.value > 0
        assert math.isclose(result.value, 9_994.50, rel_tol=1e-2)

    def test_very_large_payment(self):
        result = annuity_pv(payment=1e12, discount_rate=0.10, periods=5)
        assert result.value > 0
        assert math.isfinite(result.value)

    def test_large_periods(self):
        result = annuity_pv(payment=1_000, discount_rate=0.10, periods=100)
        assert result.value > 0
        assert math.isfinite(result.value)

    def test_zero_rate_raises(self):
        with pytest.raises(ValueError, match="cannot be zero"):
            annuity_pv(payment=1_000, discount_rate=0.0, periods=10)

    def test_negative_payment_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            annuity_pv(payment=-100, discount_rate=0.10, periods=5)

    def test_single_period(self):
        result = annuity_pv(payment=1_000, discount_rate=0.10, periods=1)
        assert math.isclose(result.value, 909.09, abs_tol=1)


class TestPerpetuityPVEdgeCases:
    """Edge cases for perpetuity_pv."""

    @pytest.mark.parametrize("payment,rate,expected", [
        (1_000, 0.01, 100_000.0),
        (1_000, 0.50, 2_000.0),
        (1e12, 0.10, 1e13),
        (0.001, 0.10, 0.01),
    ])
    def test_parametrized_perpetuity(self, payment, rate, expected):
        result = perpetuity_pv(payment=payment, discount_rate=rate)
        assert math.isclose(result.value, expected, rel_tol=1e-6, abs_tol=0.01)

    def test_very_small_rate(self):
        result = perpetuity_pv(payment=1_000, discount_rate=0.0001)
        assert math.isclose(result.value, 10_000_000, rel_tol=1e-4)

    def test_zero_rate_raises(self):
        with pytest.raises(ValueError, match="positive"):
            perpetuity_pv(payment=1_000, discount_rate=0.0)

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError, match="positive"):
            perpetuity_pv(payment=1_000, discount_rate=-0.01)


class TestGrowingAnnuityPVEdgeCases:
    """Edge cases for growing_annuity_pv."""

    def test_rate_equals_growth(self):
        result = growing_annuity_pv(payment=1_000, discount_rate=0.10, growth_rate=0.10, periods=10)
        expected = 1_000 * 10 / 1.10
        assert math.isclose(result.value, expected, rel_tol=1e-6)

    def test_very_small_rates(self):
        result = growing_annuity_pv(payment=1_000, discount_rate=0.0001, growth_rate=0.00005, periods=10)
        assert result.value > 0
        assert math.isfinite(result.value)

    def test_growth_greater_than_discount(self):
        result = growing_annuity_pv(payment=1_000, discount_rate=0.05, growth_rate=0.08, periods=10)
        assert result.value > 0

    def test_zero_growth(self):
        result_growing = growing_annuity_pv(payment=1_000, discount_rate=0.10, growth_rate=0.0, periods=10)
        result_annuity = annuity_pv(payment=1_000, discount_rate=0.10, periods=10)
        assert math.isclose(result_growing.value, result_annuity.value, rel_tol=1e-6)

    def test_negative_growth(self):
        result = growing_annuity_pv(payment=1_000, discount_rate=0.10, growth_rate=-0.05, periods=10)
        assert result.value > 0
        assert result.value < annuity_pv(payment=1_000, discount_rate=0.10, periods=10).value

    def test_zero_periods(self):
        result = growing_annuity_pv(payment=1_000, discount_rate=0.10, growth_rate=0.05, periods=0)
        assert math.isclose(result.value, 0.0, abs_tol=0.01)


class TestTerminalValueEdgeCases:
    """Edge cases for terminal_value."""

    def test_gordon_growth_boundary_r_close_to_g(self):
        result = terminal_value(
            final_year_cashflow=1_000_000,
            perpetual_growth_rate=0.0299,
            discount_rate=0.03,
            method="gordon_growth",
        )
        assert result.value > 0
        assert result.value > 100_000_000

    def test_exit_multiple_very_large(self):
        result = terminal_value(
            final_year_cashflow=1e12,
            perpetual_growth_rate=0.02,
            discount_rate=0.10,
            method="exit_multiple",
            exit_multiple=20.0,
        )
        assert math.isclose(result.value, 2e13, rel_tol=1e-6)

    def test_gordon_growth_rate_equals_discount_raises(self):
        with pytest.raises(ValueError, match="must be greater"):
            terminal_value(
                final_year_cashflow=1_000_000,
                perpetual_growth_rate=0.10,
                discount_rate=0.10,
                method="gordon_growth",
            )

    def test_exit_multiple_missing_raises(self):
        with pytest.raises(ValueError, match="exit_multiple is required"):
            terminal_value(
                final_year_cashflow=1_000_000,
                perpetual_growth_rate=0.02,
                discount_rate=0.10,
                method="exit_multiple",
            )

    def test_unknown_method_raises(self):
        with pytest.raises(ValueError, match="Unknown method"):
            terminal_value(
                final_year_cashflow=1_000_000,
                perpetual_growth_rate=0.02,
                discount_rate=0.10,
                method="unknown",
            )


class TestPresentValueOfSeriesEdgeCases:
    """Edge cases for present_value_of_series."""

    def test_single_cash_flow(self):
        result = present_value_of_series(cash_flows=[1_000_000], discount_rate=0.10)
        expected = 1_000_000 / 1.10
        assert math.isclose(result.value, expected, rel_tol=1e-6)

    def test_very_large_cash_flows(self):
        result = present_value_of_series(cash_flows=[1e12, 1e12, 1e12], discount_rate=0.10)
        assert result.value > 0
        assert math.isfinite(result.value)

    def test_zero_discount_rate(self):
        result = present_value_of_series(cash_flows=[100, 200, 300], discount_rate=0.0)
        assert math.isclose(result.value, 600, abs_tol=0.01)

    def test_empty_cash_flows_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            present_value_of_series(cash_flows=[], discount_rate=0.10)

    def test_mixed_positive_negative(self):
        result = present_value_of_series(cash_flows=[100, -50, 200], discount_rate=0.10)
        assert result.value > 0


class TestPresentValueGraduatedEdgeCases:
    """Edge cases for present_value_graduated."""

    def test_all_same_rates_equals_flat(self):
        cfs = [100, 200, 300]
        rates = [0.10, 0.10, 0.10]
        result = present_value_graduated(cash_flows=cfs, discount_rates=rates)
        flat = present_value_of_series(cash_flows=cfs, discount_rate=0.10)
        assert math.isclose(result.value, flat.value, rel_tol=1e-6)

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="must match"):
            present_value_graduated(cash_flows=[100, 200], discount_rates=[0.10])

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            present_value_graduated(cash_flows=[], discount_rates=[])


class TestAnnuityDuePVEdgeCases:
    """Edge cases for annuity_due_pv."""

    def test_zero_periods(self):
        result = annuity_due_pv(payment=1_000, discount_rate=0.10, periods=0)
        assert math.isclose(result.value, 0.0, abs_tol=0.01)

    def test_zero_rate(self):
        result = annuity_due_pv(payment=1_000, discount_rate=0.0, periods=5)
        assert math.isclose(result.value, 5_000, abs_tol=0.01)

    def test_annuity_due_greater_than_ordinary(self):
        due = annuity_due_pv(payment=1_000, discount_rate=0.10, periods=5)
        ordinary = annuity_pv(payment=1_000, discount_rate=0.10, periods=5)
        assert due.value > ordinary.value

    def test_very_large_value(self):
        result = annuity_due_pv(payment=1e12, discount_rate=0.10, periods=10)
        assert math.isfinite(result.value)


class TestGrowingPerpetuityPVEdgeCases:
    """Edge cases for growing_perpetuity_pv."""

    def test_zero_growth(self):
        result = growing_perpetuity_pv(first_payment=1_000, discount_rate=0.10, growth_rate=0.0)
        expected = perpetuity_pv(payment=1_000, discount_rate=0.10).value
        assert math.isclose(result.value, expected, rel_tol=1e-6)

    def test_rate_close_to_growth(self):
        result = growing_perpetuity_pv(first_payment=1_000, discount_rate=0.0301, growth_rate=0.03)
        assert result.value > 0
        assert result.value > 100_000

    def test_rate_equals_growth_raises(self):
        with pytest.raises(ValueError, match="must be greater"):
            growing_perpetuity_pv(first_payment=1_000, discount_rate=0.10, growth_rate=0.10)

    def test_rate_less_than_growth_raises(self):
        with pytest.raises(ValueError, match="must be greater"):
            growing_perpetuity_pv(first_payment=1_000, discount_rate=0.05, growth_rate=0.10)


class TestEffectiveAnnualRateEdgeCases:
    """Edge cases for effective_annual_rate."""

    @pytest.mark.parametrize("rate,periods,expected", [
        (0.12, 1, 0.12),
        (0.12, 2, 0.1236),
        (0.12, 12, 0.126825),
        (0.0, 12, 0.0),
    ])
    def test_parametrized_ear(self, rate, periods, expected):
        result = effective_annual_rate(nominal_rate=rate, compounding_periods=periods)
        assert math.isclose(result.value, expected, rel_tol=1e-4)

    def test_very_high_compounding(self):
        result = effective_annual_rate(nominal_rate=0.10, compounding_periods=8760)
        assert result.value > 0.10
        assert math.isclose(result.value, 0.10517, rel_tol=1e-4)

    def test_single_period(self):
        result = effective_annual_rate(nominal_rate=0.08, compounding_periods=1)
        assert math.isclose(result.value, 0.08, abs_tol=1e-6)

    def test_zero_periods_raises(self):
        with pytest.raises(ValueError, match="at least 1"):
            effective_annual_rate(nominal_rate=0.10, compounding_periods=0)


class TestContinuousCompoundingEdgeCases:
    """Edge cases for continuous_compounding."""

    def test_zero_time(self):
        result = continuous_compounding(principal=1_000, rate=0.05, time=0)
        assert math.isclose(result.value, 1_000, abs_tol=0.01)

    def test_zero_rate(self):
        result = continuous_compounding(principal=1_000, rate=0.0, time=5)
        assert math.isclose(result.value, 1_000, abs_tol=0.01)

    def test_very_large_principal(self):
        result = continuous_compounding(principal=1e12, rate=0.05, time=10)
        assert math.isfinite(result.value)
        assert result.value > 1e12

    def test_very_small_rate(self):
        result = continuous_compounding(principal=1_000, rate=0.0001, time=10)
        assert math.isclose(result.value, 1_001.00, rel_tol=1e-3)

    def test_negative_principal_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            continuous_compounding(principal=-100, rate=0.05, time=5)


class TestBuildUpDiscountRateEdgeCases:
    """Edge cases for build_up_discount_rate."""

    def test_all_zero_premiums(self):
        result = build_up_discount_rate(
            risk_free_rate=0.04,
            equity_risk_premium=0.06,
            size_premium=0.0,
            industry_risk_premium=0.0,
            specific_risk_premium=0.0,
        )
        assert math.isclose(result.value, 0.10, abs_tol=1e-6)

    def test_very_large_premiums(self):
        result = build_up_discount_rate(
            risk_free_rate=0.04,
            equity_risk_premium=0.06,
            size_premium=0.10,
            industry_risk_premium=0.10,
            specific_risk_premium=0.10,
        )
        assert math.isclose(result.value, 0.40, abs_tol=1e-6)

    def test_negative_risk_free_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            build_up_discount_rate(risk_free_rate=-0.01, equity_risk_premium=0.06)

    def test_negative_erp_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            build_up_discount_rate(risk_free_rate=0.04, equity_risk_premium=-0.01)


class TestCAPMEdgeCases:
    """Edge cases for capm_discount_rate."""

    @pytest.mark.parametrize("rf,beta,rm,expected", [
        (0.04, 1.0, 0.10, 0.10),
        (0.04, 0.0, 0.10, 0.04),
        (0.04, 2.0, 0.10, 0.16),
        (0.0, 1.0, 0.08, 0.08),
    ])
    def test_parametrized_capm(self, rf, beta, rm, expected):
        result = capm_discount_rate(risk_free_rate=rf, beta=beta, market_return=rm)
        assert math.isclose(result.value, expected, abs_tol=1e-6)

    def test_beta_zero(self):
        result = capm_discount_rate(risk_free_rate=0.04, beta=0.0, market_return=0.10)
        assert math.isclose(result.value, 0.04, abs_tol=1e-6)

    def test_market_equals_risk_free(self):
        result = capm_discount_rate(risk_free_rate=0.05, beta=1.5, market_return=0.05)
        assert math.isclose(result.value, 0.05, abs_tol=1e-6)

    def test_market_below_risk_free_raises(self):
        with pytest.raises(ValueError, match="must be >="):
            capm_discount_rate(risk_free_rate=0.05, beta=1.0, market_return=0.03)


class TestWACCEdgeCases:
    """Edge cases for wacc."""

    def test_all_equity(self):
        result = wacc(equity_value=1_000, debt_value=0, cost_of_equity=0.12, cost_of_debt=0.06, tax_rate=0.25)
        assert math.isclose(result.value, 0.12, abs_tol=1e-6)

    def test_all_debt(self):
        result = wacc(equity_value=0, debt_value=1_000, cost_of_equity=0.12, cost_of_debt=0.06, tax_rate=0.25)
        assert math.isclose(result.value, 0.045, abs_tol=1e-6)

    def test_zero_tax_rate(self):
        result = wacc(equity_value=500, debt_value=500, cost_of_equity=0.12, cost_of_debt=0.06, tax_rate=0.0)
        assert math.isclose(result.value, 0.09, abs_tol=1e-6)

    def test_very_large_values(self):
        result = wacc(equity_value=1e12, debt_value=5e11, cost_of_equity=0.12, cost_of_debt=0.06, tax_rate=0.25)
        assert result.value > 0
        assert math.isfinite(result.value)

    def test_zero_total_capital_raises(self):
        with pytest.raises(ValueError, match="must be positive"):
            wacc(equity_value=0, debt_value=0, cost_of_equity=0.12, cost_of_debt=0.06, tax_rate=0.25)


class TestTaxAmortizationBenefitEdgeCases:
    """Edge cases for tax_amortization_benefit."""

    def test_zero_rate_special_case(self):
        result = tax_amortization_benefit(
            discount_rate=0.0000001,
            useful_life=10,
            tax_rate=0.25,
            asset_value=1_000_000,
        )
        assert result.value > 0

    def test_very_long_useful_life(self):
        result = tax_amortization_benefit(
            discount_rate=0.10,
            useful_life=100,
            tax_rate=0.25,
            asset_value=1_000_000,
        )
        assert result.value > 0
        assert math.isfinite(result.value)

    def test_zero_tax_rate(self):
        result = tax_amortization_benefit(
            discount_rate=0.10,
            useful_life=10,
            tax_rate=0.0,
            asset_value=1_000_000,
        )
        assert math.isclose(result.value, 0.0, abs_tol=0.01)

    def test_zero_asset_value(self):
        result = tax_amortization_benefit(
            discount_rate=0.10,
            useful_life=10,
            tax_rate=0.25,
            asset_value=0,
        )
        assert math.isclose(result.value, 0.0, abs_tol=0.01)


class TestControlPremiumEdgeCases:
    """Edge cases for control_premium."""

    def test_equal_prices(self):
        result = control_premium(minority_price=100, control_price=100)
        assert math.isclose(result.value, 0.0, abs_tol=1e-6)

    def test_very_large_premium(self):
        result = control_premium(minority_price=1, control_price=100)
        assert math.isclose(result.value, 99.0, abs_tol=1e-6)

    def test_control_below_minority_raises(self):
        with pytest.raises(ValueError, match="must be >="):
            control_premium(minority_price=100, control_price=90)


class TestDLOMFinnertyEdgeCases:
    """Edge cases for dlom_finnerty."""

    def test_short_restriction(self):
        result = dlom_finnerty(restricted_period=0.5, volatility=0.30, risk_free_rate=0.04)
        assert 0 <= result.value <= 1

    def test_high_volatility(self):
        result = dlom_finnerty(restricted_period=2.0, volatility=0.80, risk_free_rate=0.04)
        assert 0 <= result.value <= 1

    def test_zero_volatility_raises(self):
        with pytest.raises(ValueError, match="positive"):
            dlom_finnerty(restricted_period=1.0, volatility=0.0, risk_free_rate=0.04)

    def test_zero_period_raises(self):
        with pytest.raises(ValueError, match="positive"):
            dlom_finnerty(restricted_period=0.0, volatility=0.30, risk_free_rate=0.04)


class TestCurrencyAdjustedEdgeCases:
    """Edge cases for currency_adjusted_discount_rate."""

    def test_no_premiums(self):
        result = currency_adjusted_discount_rate(base_rate=0.10)
        assert math.isclose(result.value, 0.10, abs_tol=1e-6)

    def test_large_premiums(self):
        result = currency_adjusted_discount_rate(
            base_rate=0.10,
            currency_risk_premium=0.05,
            country_risk_premium=0.05,
        )
        assert math.isclose(result.value, 0.20, abs_tol=1e-6)


class TestWACCWithPreferredEdgeCases:
    """Edge cases for wacc_with_preferred."""

    def test_no_preferred(self):
        result = wacc_with_preferred(
            equity_value=600, debt_value=400, preferred_value=0,
            cost_of_equity=0.12, cost_of_debt=0.06, cost_of_preferred=0.08,
            tax_rate=0.25,
        )
        assert math.isclose(result.value, 0.09, abs_tol=1e-4)

    def test_all_preferred(self):
        result = wacc_with_preferred(
            equity_value=0, debt_value=0, preferred_value=1_000,
            cost_of_equity=0.12, cost_of_debt=0.06, cost_of_preferred=0.08,
            tax_rate=0.25,
        )
        assert math.isclose(result.value, 0.08, abs_tol=1e-6)

    def test_zero_total_raises(self):
        with pytest.raises(ValueError, match="must be positive"):
            wacc_with_preferred(
                equity_value=0, debt_value=0, preferred_value=0,
                cost_of_equity=0.12, cost_of_debt=0.06, cost_of_preferred=0.08,
                tax_rate=0.25,
            )


class TestImpliedERPEdgeCases:
    """Edge cases for implied_erp."""

    @pytest.mark.parametrize("pe,growth,expected", [
        (20, 0.03, 0.02),
        (10, 0.02, 0.08),
        (50, 0.04, -0.02),
    ])
    def test_parametrized_implied_erp(self, pe, growth, expected):
        result = implied_erp(market_pe_ratio=pe, perpetual_growth_rate=growth)
        assert math.isclose(result.value, expected, abs_tol=1e-4)

    def test_zero_pe_raises(self):
        with pytest.raises(ValueError, match="positive"):
            implied_erp(market_pe_ratio=0, perpetual_growth_rate=0.03)


class TestBetaUnleveredReleveredEdgeCases:
    """Edge cases for beta_unlevered and beta_relevered."""

    def test_unlevered_no_debt(self):
        result = beta_unlevered(beta_levered=1.2, debt_to_equity=0.0, tax_rate=0.25)
        assert math.isclose(result.value, 1.2, abs_tol=1e-6)

    def test_relevered_no_debt(self):
        result = beta_relevered(beta_unlevered=1.0, target_debt_to_equity=0.0, tax_rate=0.25)
        assert math.isclose(result.value, 1.0, abs_tol=1e-6)

    def test_unlevered_high_debt(self):
        result = beta_unlevered(beta_levered=1.5, debt_to_equity=2.0, tax_rate=0.25)
        assert result.value < 1.5

    def test_roundtrip(self):
        unlevered = beta_unlevered(beta_levered=1.2, debt_to_equity=0.5, tax_rate=0.25).value
        relevered = beta_relevered(beta_unlevered=unlevered, target_debt_to_equity=0.5, tax_rate=0.25).value
        assert math.isclose(relevered, 1.2, abs_tol=1e-4)

    def test_negative_de_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            beta_unlevered(beta_levered=1.0, debt_to_equity=-0.1, tax_rate=0.25)


class TestFamaFrenchEdgeCases:
    """Edge cases for cost_of_equity_fama_french."""

    def test_all_zero_betas(self):
        result = cost_of_equity_fama_french(
            risk_free_rate=0.04,
            market_beta=0.0, smb_beta=0.0, hml_beta=0.0,
            market_premium=0.06, smb_premium=0.03, hml_premium=0.04,
        )
        assert math.isclose(result.value, 0.04, abs_tol=1e-6)

    def test_capm_equivalent(self):
        result = cost_of_equity_fama_french(
            risk_free_rate=0.04,
            market_beta=1.0, smb_beta=0.0, hml_beta=0.0,
            market_premium=0.06, smb_premium=0.03, hml_premium=0.04,
        )
        assert math.isclose(result.value, 0.10, abs_tol=1e-6)


class TestMonteCarloEdgeCases:
    """Edge cases for monte_carlo_valuation."""

    def test_single_iteration(self):
        def simple_fn(x):
            return x
        result = monte_carlo_valuation(
            valuation_fn=simple_fn,
            input_distributions=[{"name": "x", "distribution": "uniform", "params": {"low": 10, "high": 10.001}}],
            iterations=1,
            seed=42,
        )
        assert result["mean"] > 9

    def test_empty_distributions_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            monte_carlo_valuation(valuation_fn=lambda x: x, input_distributions=[], iterations=100)

    def test_zero_iterations_raises(self):
        with pytest.raises(ValueError, match="at least 1"):
            monte_carlo_valuation(
                valuation_fn=lambda x: x,
                input_distributions=[{"name": "x", "distribution": "uniform", "params": {"low": 0, "high": 1}}],
                iterations=0,
            )


class TestDecisionTreeEdgeCases:
    """Edge cases for decision_tree_valuation."""

    def test_single_terminal(self):
        tree = {
            "nodes": [
                {"id": "root", "type": "decision", "label": "Root", "value": 0},
                {"id": "end", "type": "terminal", "label": "End", "value": 100},
            ],
            "edges": [
                {"from": "root", "to": "end", "probability": 1.0, "cost": 0},
            ],
        }
        result = decision_tree_valuation(tree)
        assert math.isclose(result["expected_value"], 100, abs_tol=0.01)

    def test_probabilities_not_summing_raises(self):
        tree = {
            "nodes": [
                {"id": "root", "type": "chance", "label": "Root", "value": 0},
                {"id": "a", "type": "terminal", "label": "A", "value": 100},
                {"id": "b", "type": "terminal", "label": "B", "value": 200},
            ],
            "edges": [
                {"from": "root", "to": "a", "probability": 0.3, "cost": 0},
                {"from": "root", "to": "b", "probability": 0.3, "cost": 0},
            ],
        }
        with pytest.raises(ValueError, match="sum to"):
            decision_tree_valuation(tree)


class TestScenarioAnalysisEdgeCases:
    """Edge cases for scenario_analysis."""

    def test_single_scenario(self):
        result = scenario_analysis([
            {"name": "Only", "probability": 1.0, "params": {"future_value": 100, "discount_rate": 0.0, "periods": 0}, "function_name": "present_value"},
        ])
        assert math.isclose(result["expected_value"], 100, abs_tol=0.01)

    def test_probabilities_not_summing_raises(self):
        with pytest.raises(ValueError, match="sum to"):
            scenario_analysis([
                {"name": "A", "probability": 0.3, "params": {}, "function_name": "present_value"},
                {"name": "B", "probability": 0.3, "params": {}, "function_name": "present_value"},
            ])

    def test_empty_scenarios_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            scenario_analysis([])


class TestSensitivityTornadoEdgeCases:
    """Edge cases for sensitivity_tornado."""

    def test_single_parameter(self):
        result = sensitivity_tornado(
            function_name="present_value",
            base_params={"future_value": 1_000, "discount_rate": 0.10, "periods": 5},
            parameter_ranges={"discount_rate": [0.05, 0.10, 0.15]},
        )
        assert len(result["tornado"]) == 1
        assert result["tornado"][0]["parameter"] == "discount_rate"

    def test_empty_ranges_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            sensitivity_tornado(
                function_name="present_value",
                base_params={"future_value": 1_000, "discount_rate": 0.10, "periods": 5},
                parameter_ranges={},
            )
