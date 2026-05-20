"""Tests for impairment testing (TASK-036)."""

import pytest

from src.advanced.impairment_testing import (
    cash_generating_unit_impairment,
    fair_value_less_costs_to_sell,
    goodwill_impairment_test,
    intangible_impairment_test,
    value_in_use,
)


class TestGoodwillImpairment:
    def test_impairment_asc350(self):
        result = goodwill_impairment_test(
            carrying_value=50_000_000,
            fair_value=40_000_000,
            reporting_unit="Tech Division",
            standard="ASC350",
        )
        assert result.value == 10_000_000.0
        assert result.assumptions["impaired"] is True

    def test_no_impairment_asc350(self):
        result = goodwill_impairment_test(
            carrying_value=50_000_000,
            fair_value=55_000_000,
            standard="ASC350",
        )
        assert result.value == 0.0
        assert result.assumptions["impaired"] is False

    def test_no_impairment_at_par(self):
        result = goodwill_impairment_test(
            carrying_value=50_000_000,
            fair_value=50_000_000,
            standard="ASC350",
        )
        assert result.value == 0.0

    def test_ias36_impairment(self):
        result = goodwill_impairment_test(
            carrying_value=30_000_000,
            fair_value=25_000_000,
            standard="IAS36",
        )
        assert result.value == 5_000_000.0
        assert result.assumptions["impaired"] is True

    def test_ias36_no_impairment(self):
        result = goodwill_impairment_test(
            carrying_value=30_000_000,
            fair_value=35_000_000,
            standard="IAS36",
        )
        assert result.value == 0.0

    def test_default_standard_is_asc350(self):
        result = goodwill_impairment_test(50_000_000, 40_000_000)
        assert "ASC350" in result.method

    def test_invalid_standard_raises(self):
        with pytest.raises(ValueError):
            goodwill_impairment_test(50_000_000, 40_000_000, standard="INVALID")

    def test_negative_carrying_value_raises(self):
        with pytest.raises(ValueError):
            goodwill_impairment_test(-50_000_000, 40_000_000)

    def test_negative_fair_value_raises(self):
        with pytest.raises(ValueError):
            goodwill_impairment_test(50_000_000, -40_000_000)


class TestIntangibleImpairment:
    def test_asc350_impairment(self):
        result = intangible_impairment_test(
            carrying_value=20_000_000,
            fair_value=15_000_000,
            standard="ASC350",
        )
        assert result.value == 5_000_000.0
        assert result.assumptions["impaired"] is True

    def test_asc350_no_impairment(self):
        result = intangible_impairment_test(
            carrying_value=20_000_000,
            fair_value=25_000_000,
            standard="ASC350",
        )
        assert result.value == 0.0

    def test_asc350_missing_fair_value_raises(self):
        with pytest.raises(ValueError, match="fair_value is required"):
            intangible_impairment_test(carrying_value=20_000_000, standard="ASC350")

    def test_ias36_impairment(self):
        result = intangible_impairment_test(
            carrying_value=20_000_000,
            recoverable_amount=16_000_000,
            standard="IAS36",
        )
        assert result.value == 4_000_000.0
        assert result.assumptions["impaired"] is True

    def test_ias36_no_impairment(self):
        result = intangible_impairment_test(
            carrying_value=20_000_000,
            recoverable_amount=22_000_000,
            standard="IAS36",
        )
        assert result.value == 0.0

    def test_ias36_missing_recoverable_amount_raises(self):
        with pytest.raises(ValueError, match="recoverable_amount is required"):
            intangible_impairment_test(carrying_value=20_000_000, standard="IAS36")

    def test_invalid_standard_raises(self):
        with pytest.raises(ValueError):
            intangible_impairment_test(20_000_000, standard="INVALID")

    def test_negative_carrying_value_raises(self):
        with pytest.raises(ValueError):
            intangible_impairment_test(-20_000_000, fair_value=15_000_000)

    def test_returns_steps(self):
        result = intangible_impairment_test(20_000_000, fair_value=15_000_000)
        assert len(result.steps) >= 4


class TestValueInUse:
    """Tests for value_in_use function."""

    def test_happy_path_basic(self):
        result = value_in_use(
            cash_flow_projections=[5_000_000, 5_500_000, 6_000_000],
            terminal_growth_rate=0.02,
            discount_rate=0.10,
        )
        assert result.value > 0
        assert "IAS 36 Value in Use" in result.method

    def test_happy_path_single_period(self):
        result = value_in_use(
            cash_flow_projections=[10_000_000],
            terminal_growth_rate=0.02,
            discount_rate=0.10,
        )
        assert result.value > 0

    def test_happy_path_zero_growth(self):
        result = value_in_use(
            cash_flow_projections=[5_000_000, 5_000_000, 5_000_000],
            terminal_growth_rate=0.0,
            discount_rate=0.10,
        )
        assert result.value > 0

    def test_error_discount_not_exceeding_growth(self):
        with pytest.raises(ValueError, match="Discount rate must exceed"):
            value_in_use(
                cash_flow_projections=[5_000_000],
                terminal_growth_rate=0.10,
                discount_rate=0.10,
            )

    def test_error_negative_cash_flow(self):
        with pytest.raises(ValueError):
            value_in_use(
                cash_flow_projections=[-5_000_000],
                terminal_growth_rate=0.02,
                discount_rate=0.10,
            )

    def test_error_empty_projections(self):
        with pytest.raises(ValueError):
            value_in_use(
                cash_flow_projections=[],
                terminal_growth_rate=0.02,
                discount_rate=0.10,
            )

    def test_returns_terminal_value(self):
        result = value_in_use(
            cash_flow_projections=[5_000_000, 5_500_000, 6_000_000],
            terminal_growth_rate=0.02,
            discount_rate=0.10,
        )
        assert "terminal_value" in result.assumptions
        assert "pv_terminal_value" in result.assumptions


class TestFairValueLessCostsToSell:
    """Tests for fair_value_less_costs_to_sell function."""

    def test_happy_path_basic(self):
        result = fair_value_less_costs_to_sell(10_000_000, 500_000)
        assert result.value == 9_500_000.0
        assert "Fair Value Less Costs" in result.method

    def test_happy_path_zero_costs(self):
        result = fair_value_less_costs_to_sell(10_000_000, 0)
        assert result.value == 10_000_000.0

    def test_happy_path_high_costs(self):
        result = fair_value_less_costs_to_sell(10_000_000, 2_000_000)
        assert result.value == 8_000_000.0

    def test_error_negative_fair_value(self):
        with pytest.raises(ValueError):
            fair_value_less_costs_to_sell(-10_000_000, 500_000)

    def test_error_negative_disposal_costs(self):
        with pytest.raises(ValueError):
            fair_value_less_costs_to_sell(10_000_000, -500_000)

    def test_returns_steps(self):
        result = fair_value_less_costs_to_sell(10_000_000, 500_000)
        assert len(result.steps) >= 4


class TestCGUImpairment:
    """Tests for cash_generating_unit_impairment function."""

    def test_happy_path_impairment(self):
        result = cash_generating_unit_impairment(
            cgu_carrying_value=100_000_000,
            cgu_recoverable_amount=80_000_000,
            goodwill_allocated=15_000_000,
            other_assets=[
                {"name": "Patents", "carrying_value": 40_000_000},
                {"name": "Equipment", "carrying_value": 45_000_000},
            ],
        )
        assert result.value == 20_000_000.0
        assert "CGU Impairment" in result.method

    def test_happy_path_no_impairment(self):
        result = cash_generating_unit_impairment(
            cgu_carrying_value=100_000_000,
            cgu_recoverable_amount=110_000_000,
            goodwill_allocated=15_000_000,
            other_assets=[
                {"name": "Patents", "carrying_value": 40_000_000},
            ],
        )
        assert result.value == 0.0

    def test_happy_path_goodwill_fully_written_off(self):
        result = cash_generating_unit_impairment(
            cgu_carrying_value=100_000_000,
            cgu_recoverable_amount=70_000_000,
            goodwill_allocated=10_000_000,
            other_assets=[
                {"name": "Patents", "carrying_value": 45_000_000},
                {"name": "Equipment", "carrying_value": 45_000_000},
            ],
        )
        assert result.value == 30_000_000.0
        allocation = result.assumptions["allocation"]
        gw_alloc = next(a for a in allocation if a["asset"] == "Goodwill")
        assert gw_alloc["impairment"] == 10_000_000.0

    def test_error_empty_assets(self):
        with pytest.raises(ValueError):
            cash_generating_unit_impairment(
                cgu_carrying_value=100_000_000,
                cgu_recoverable_amount=80_000_000,
                goodwill_allocated=15_000_000,
                other_assets=[],
            )

    def test_error_missing_asset_name(self):
        with pytest.raises(ValueError):
            cash_generating_unit_impairment(
                cgu_carrying_value=100_000_000,
                cgu_recoverable_amount=80_000_000,
                goodwill_allocated=15_000_000,
                other_assets=[{"carrying_value": 40_000_000}],
            )

    def test_error_negative_carrying_value(self):
        with pytest.raises(ValueError):
            cash_generating_unit_impairment(
                cgu_carrying_value=100_000_000,
                cgu_recoverable_amount=80_000_000,
                goodwill_allocated=15_000_000,
                other_assets=[{"name": "X", "carrying_value": -100}],
            )

    def test_returns_allocation_details(self):
        result = cash_generating_unit_impairment(
            cgu_carrying_value=100_000_000,
            cgu_recoverable_amount=80_000_000,
            goodwill_allocated=15_000_000,
            other_assets=[
                {"name": "Patents", "carrying_value": 40_000_000},
                {"name": "Equipment", "carrying_value": 45_000_000},
            ],
        )
        assert "allocation" in result.assumptions
        assert len(result.assumptions["allocation"]) == 3
