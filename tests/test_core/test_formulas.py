"""Tests for utility functions: useful life estimation, sensitivity analysis, and contributory asset charges."""

import math

import pytest

from src.utils.formulas import (
    contributory_asset_charges,
    double_declining_balance_amortization,
    estimate_useful_life,
    sensitivity_analysis,
    straight_line_amortization,
    sum_of_years_digits_amortization,
    valuation_multiple,
)


class TestEstimateUsefulLife:
    """Test estimate_useful_life function."""

    def test_patent_default(self):
        """Patent with default settings."""
        result = estimate_useful_life(asset_type="patent")
        assert result.value > 0
        assert result.value <= 20  # Legal max for patents
        assert result.method == "Useful Life Estimation"

    def test_trademark_default(self):
        """Trademark with default settings."""
        result = estimate_useful_life(asset_type="trademark")
        assert result.value > 0
        assert result.value >= 10  # Typical economic life

    def test_software_default(self):
        """Software with default 5% obsolescence rate has ~46 year economic life."""
        result = estimate_useful_life(asset_type="software")
        assert result.value > 0
        assert result.value < 50  # ~46 years at 5% default obsolescence

    def test_custom_legal_life(self):
        """Custom legal life overrides default."""
        result = estimate_useful_life(
            asset_type="license",
            legal_life=5,
        )
        assert result.value <= 5

    def test_custom_obsolescence_rate(self):
        """Higher obsolescence rate reduces economic life."""
        result_low = estimate_useful_life(
            asset_type="software",
            obsolescence_rate=0.05,
        )
        result_high = estimate_useful_life(
            asset_type="software",
            obsolescence_rate=0.20,
        )
        assert result_high.value < result_low.value

    def test_economic_factors_competition(self):
        """Competition factor increases effective obsolescence."""
        result_no_comp = estimate_useful_life(
            asset_type="software",
            economic_factors={"competition": 0.0},
        )
        result_high_comp = estimate_useful_life(
            asset_type="software",
            economic_factors={"competition": 1.0},
        )
        assert result_high_comp.value <= result_no_comp.value

    def test_unknown_asset_type_with_legal_life(self):
        """Unknown asset type with provided legal life should work."""
        result = estimate_useful_life(
            asset_type="custom_asset",
            legal_life=10,
        )
        assert result.value > 0
        assert result.value <= 10

    def test_unknown_asset_type_without_legal_life_raises(self):
        with pytest.raises(ValueError, match="Unknown asset type"):
            estimate_useful_life(asset_type="nonexistent_asset")

    def test_obsolescence_out_of_range_raises(self):
        with pytest.raises(ValueError, match="between 0 and 1"):
            estimate_useful_life(asset_type="patent", obsolescence_rate=1.5)


class TestSensitivityAnalysis:
    """Test sensitivity_analysis function."""

    def test_sensitivity_present_value(self):
        """Sensitivity of PV to discount rate."""
        result = sensitivity_analysis(
            function_name="present_value",
            parameter_name="discount_rate",
            parameter_range=[0.05, 0.10, 0.15, 0.20],
            fixed_parameters={"future_value": 1_000_000, "periods": 10},
        )
        assert result["function_name"] == "present_value"
        assert result["parameter_name"] == "discount_rate"
        assert len(result["results"]) == 4
        assert result["min_result"] is not None
        assert result["max_result"] is not None

    def test_pv_decreases_with_higher_rate(self):
        """PV should decrease as discount rate increases."""
        result = sensitivity_analysis(
            function_name="present_value",
            parameter_name="discount_rate",
            parameter_range=[0.05, 0.10, 0.15],
            fixed_parameters={"future_value": 1_000_000, "periods": 10},
        )
        values = [r["result"] for r in result["results"]]
        assert values[0] > values[1] > values[2]

    def test_sensitivity_annuity(self):
        """Sensitivity of annuity PV to discount rate."""
        result = sensitivity_analysis(
            function_name="annuity_pv",
            parameter_name="discount_rate",
            parameter_range=[0.05, 0.10, 0.15],
            fixed_parameters={"payment": 100_000, "periods": 10},
        )
        assert len(result["results"]) == 3

    def test_sensitivity_perpetuity(self):
        """Sensitivity of perpetuity PV to discount rate."""
        result = sensitivity_analysis(
            function_name="perpetuity_pv",
            parameter_name="discount_rate",
            parameter_range=[0.05, 0.10, 0.15],
            fixed_parameters={"payment": 100_000},
        )
        values = [r["result"] for r in result["results"]]
        assert values[0] > values[1] > values[2]

    def test_sensitivity_wacc(self):
        """Sensitivity of WACC to tax rate."""
        result = sensitivity_analysis(
            function_name="wacc",
            parameter_name="tax_rate",
            parameter_range=[0.15, 0.25, 0.35],
            fixed_parameters={
                "equity_value": 600,
                "debt_value": 400,
                "cost_of_equity": 0.12,
                "cost_of_debt": 0.06,
            },
        )
        assert len(result["results"]) == 3

    def test_sensitivity_build_up(self):
        """Sensitivity of build-up rate to equity risk premium."""
        result = sensitivity_analysis(
            function_name="build_up_discount_rate",
            parameter_name="equity_risk_premium",
            parameter_range=[0.04, 0.06, 0.08],
            fixed_parameters={"risk_free_rate": 0.04},
        )
        values = [r["result"] for r in result["results"]]
        assert values[0] < values[1] < values[2]

    def test_sensitivity_terminal_value(self):
        """Sensitivity of terminal value to growth rate."""
        result = sensitivity_analysis(
            function_name="terminal_value",
            parameter_name="perpetual_growth_rate",
            parameter_range=[0.01, 0.02, 0.03],
            fixed_parameters={
                "final_year_cashflow": 1_000_000,
                "discount_rate": 0.10,
                "method": "gordon_growth",
            },
        )
        values = [r["result"] for r in result["results"]]
        assert values[0] < values[1] < values[2]

    def test_sensitivity_range_empty_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            sensitivity_analysis(
                function_name="present_value",
                parameter_name="discount_rate",
                parameter_range=[],
                fixed_parameters={"future_value": 1000, "periods": 5},
            )

    def test_sensitivity_unknown_function_raises(self):
        with pytest.raises(ValueError, match="Unsupported function"):
            sensitivity_analysis(
                function_name="nonexistent_function",
                parameter_name="x",
                parameter_range=[1, 2, 3],
                fixed_parameters={},
            )

    def test_sensitivity_invalid_params(self):
        """Some parameter values may be invalid for the function."""
        result = sensitivity_analysis(
            function_name="perpetuity_pv",
            parameter_name="discount_rate",
            parameter_range=[0.0, 0.05, 0.10],
            fixed_parameters={"payment": 100_000},
        )
        assert result["results"][0]["result"] is None  # rate=0 is invalid
        assert result["results"][1]["result"] is not None


class TestContributoryAssetCharges:
    """Test contributory_asset_charges function."""

    def test_basic_cac(self):
        """Basic CAC with working capital and fixed assets."""
        result = contributory_asset_charges([
            {"type": "working_capital", "value": 500_000, "return_rate": 0.05},
            {"type": "fixed_assets", "value": 2_000_000, "return_rate": 0.08},
        ])
        expected = 500_000 * 0.05 + 2_000_000 * 0.08  # 185,000
        assert math.isclose(result["total_cac"], expected, abs_tol=1)
        assert len(result["asset_charges"]) == 2

    def test_cac_single_asset(self):
        """CAC with single asset."""
        result = contributory_asset_charges([
            {"type": "working_capital", "value": 1_000_000, "return_rate": 0.06},
        ])
        assert math.isclose(result["total_cac"], 60_000, abs_tol=1)

    def test_cac_multiple_assets(self):
        """CAC with multiple asset types."""
        assets = [
            {"type": "working_capital", "value": 300_000, "return_rate": 0.05},
            {"type": "fixed_assets", "value": 1_500_000, "return_rate": 0.08},
            {"type": "assembled_workforce", "value": 500_000, "return_rate": 0.12},
            {"type": "trade_secrets", "value": 200_000, "return_rate": 0.15},
        ]
        result = contributory_asset_charges(assets)
        expected = (
            300_000 * 0.05
            + 1_500_000 * 0.08
            + 500_000 * 0.12
            + 200_000 * 0.15
        )
        assert math.isclose(result["total_cac"], expected, abs_tol=1)

    def test_cac_asset_charge_details(self):
        """Each asset charge should be correctly calculated."""
        result = contributory_asset_charges([
            {"type": "working_capital", "value": 1_000_000, "return_rate": 0.06},
        ])
        charge = result["asset_charges"][0]
        assert math.isclose(charge["charge"], 60_000, abs_tol=1)
        assert charge["type"] == "working_capital"

    def test_cac_empty_list_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            contributory_asset_charges([])

    def test_cac_negative_value_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            contributory_asset_charges([
                {"type": "working_capital", "value": -100, "return_rate": 0.06},
            ])

    def test_cac_negative_rate_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            contributory_asset_charges([
                {"type": "working_capital", "value": 100_000, "return_rate": -0.01},
            ])


class TestStraightLineAmortization:
    """Test straight_line_amortization function."""

    def test_basic_schedule(self):
        """$1M over 5 years = $200K/year."""
        result = straight_line_amortization(asset_value=1_000_000, useful_life=5)
        assert len(result["schedule"]) == 5
        assert math.isclose(result["schedule"][0]["amortization"], 200_000, abs_tol=1)
        assert result["method"] == "Straight-Line Amortization"

    def test_total_amortization_equals_asset(self):
        """Total amortization should equal asset value."""
        result = straight_line_amortization(asset_value=500_000, useful_life=10)
        assert math.isclose(result["total_amortization"], 500_000, abs_tol=1)

    def test_final_book_value_zero(self):
        """Final year book value should be zero."""
        result = straight_line_amortization(asset_value=1_000_000, useful_life=5)
        assert math.isclose(result["schedule"][-1]["book_value"], 0, abs_tol=1)

    def test_accumulated_increases(self):
        """Accumulated amortization should increase each year."""
        result = straight_line_amortization(asset_value=1_000_000, useful_life=5)
        for i in range(1, len(result["schedule"])):
            assert result["schedule"][i]["accumulated"] > result["schedule"][i - 1]["accumulated"]

    def test_single_year(self):
        """Single year: full amortization."""
        result = straight_line_amortization(asset_value=100_000, useful_life=1)
        assert math.isclose(result["schedule"][0]["amortization"], 100_000, abs_tol=1)
        assert math.isclose(result["schedule"][0]["book_value"], 0, abs_tol=1)

    def test_negative_value_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            straight_line_amortization(asset_value=-1000, useful_life=5)

    def test_zero_life_raises(self):
        with pytest.raises(ValueError, match="at least 1"):
            straight_line_amortization(asset_value=1000, useful_life=0)


class TestSumOfYearsDigitsAmortization:
    """Test sum_of_years_digits_amortization function."""

    def test_basic_syd(self):
        """$1M over 5 years: SYD = 15, Year 1 = 5/15 * 1M = 333,333."""
        result = sum_of_years_digits_amortization(asset_value=1_000_000, useful_life=5)
        assert len(result["schedule"]) == 5
        assert math.isclose(result["schedule"][0]["amortization"], 333_333.33, abs_tol=1)
        assert result["method"] == "Sum-of-Years'-Digits Amortization"

    def test_first_year_highest(self):
        """First year should have highest amortization."""
        result = sum_of_years_digits_amortization(asset_value=1_000_000, useful_life=5)
        for i in range(1, len(result["schedule"])):
            assert result["schedule"][i]["amortization"] < result["schedule"][i - 1]["amortization"]

    def test_total_amortization_equals_asset(self):
        """Total should equal asset value."""
        result = sum_of_years_digits_amortization(asset_value=1_000_000, useful_life=5)
        assert math.isclose(result["total_amortization"], 1_000_000, abs_tol=1)

    def test_final_book_value_zero(self):
        """Final book value should be zero."""
        result = sum_of_years_digits_amortization(asset_value=1_000_000, useful_life=5)
        assert math.isclose(result["schedule"][-1]["book_value"], 0, abs_tol=1)

    def test_single_year(self):
        """Single year: full amortization."""
        result = sum_of_years_digits_amortization(asset_value=100_000, useful_life=1)
        assert math.isclose(result["schedule"][0]["amortization"], 100_000, abs_tol=1)

    def test_negative_value_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            sum_of_years_digits_amortization(asset_value=-1000, useful_life=5)


class TestDoubleDecliningBalanceAmortization:
    """Test double_declining_balance_amortization function."""

    def test_basic_ddb(self):
        """$1M over 5 years: DDB rate = 40%, Year 1 = $400K."""
        result = double_declining_balance_amortization(asset_value=1_000_000, useful_life=5)
        assert len(result["schedule"]) == 5
        assert math.isclose(result["schedule"][0]["amortization"], 400_000, abs_tol=1)
        assert result["method"] == "Double-Declining Balance Amortization"

    def test_first_year_highest(self):
        """First year should have highest amortization (excluding final year plug)."""
        result = double_declining_balance_amortization(asset_value=1_000_000, useful_life=5)
        for i in range(1, len(result["schedule"]) - 1):
            assert result["schedule"][i]["amortization"] < result["schedule"][i - 1]["amortization"]

    def test_final_year_plug(self):
        """Final year should fully amortize remaining value."""
        result = double_declining_balance_amortization(asset_value=1_000_000, useful_life=5)
        assert math.isclose(result["schedule"][-1]["book_value"], 0, abs_tol=1)

    def test_total_amortization_equals_asset(self):
        """Total should equal asset value."""
        result = double_declining_balance_amortization(asset_value=1_000_000, useful_life=5)
        assert math.isclose(result["total_amortization"], 1_000_000, abs_tol=1)

    def test_accelerated_vs_straight_line(self):
        """DDB year 1 should be higher than straight-line year 1."""
        ddb = double_declining_balance_amortization(asset_value=1_000_000, useful_life=5)
        sl = straight_line_amortization(asset_value=1_000_000, useful_life=5)
        assert ddb["schedule"][0]["amortization"] > sl["schedule"][0]["amortization"]

    def test_single_year(self):
        """Single year: full amortization."""
        result = double_declining_balance_amortization(asset_value=100_000, useful_life=1)
        assert math.isclose(result["schedule"][0]["amortization"], 100_000, abs_tol=1)

    def test_negative_value_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            double_declining_balance_amortization(asset_value=-1000, useful_life=5)

    def test_zero_life_raises(self):
        with pytest.raises(ValueError, match="at least 1"):
            double_declining_balance_amortization(asset_value=1000, useful_life=0)


class TestValuationMultiple:
    """Test valuation_multiple function."""

    def test_basic_ev_revenue(self):
        """EV/Revenue = $50M / $10M = 5.0x."""
        result = valuation_multiple(value=50_000_000, metric=10_000_000, multiple_type="EV/Revenue")
        assert math.isclose(result["multiple"], 5.0, abs_tol=0.01)
        assert result["multiple_type"] == "EV/Revenue"

    def test_pe_ratio(self):
        """P/E = $100 / $5 = 20x."""
        result = valuation_multiple(value=100, metric=5, multiple_type="P/E")
        assert math.isclose(result["multiple"], 20.0, abs_tol=0.01)

    def test_ev_ebitda(self):
        """EV/EBITDA = $500M / $50M = 10x."""
        result = valuation_multiple(value=500_000_000, metric=50_000_000, multiple_type="EV/EBITDA")
        assert math.isclose(result["multiple"], 10.0, abs_tol=0.01)

    def test_zero_metric_raises(self):
        with pytest.raises(ValueError, match="cannot be zero"):
            valuation_multiple(value=100, metric=0, multiple_type="P/E")

    def test_negative_value_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            valuation_multiple(value=-100, metric=10, multiple_type="P/E")

    def test_negative_metric_raises(self):
        with pytest.raises(ValueError, match="positive"):
            valuation_multiple(value=100, metric=-10, multiple_type="P/E")
