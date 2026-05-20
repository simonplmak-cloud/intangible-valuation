"""Tests for purchase price allocation (TASK-034)."""

import pytest

from src.advanced.purchase_price_alloc import (
    bargain_purchase_analysis,
    contingent_consideration_valuation,
    deferred_tax_liability_ppa,
    purchase_price_allocation,
)


class TestPurchasePriceAllocation:
    def test_book_example(self):
        result = purchase_price_allocation(
            purchase_price=100_000_000,
            tangible_assets_fv=15_000_000,
            identified_intangibles=[
                {"name": "Customer Relationships", "value": 20_000_000, "method": "MPEEM"},
                {"name": "Technology", "value": 25_000_000, "method": "Relief-from-Royalty"},
                {"name": "Brand", "value": 15_000_000, "method": "Relief-from-Royalty"},
            ],
            liabilities_fv=0,
        )
        assert result.value == 25_000_000.0
        assert result.method == "Purchase Price Allocation"
        assert "Ch 10.2" in result.formula_reference

    def test_with_liabilities(self):
        result = purchase_price_allocation(
            purchase_price=100_000_000,
            tangible_assets_fv=15_000_000,
            identified_intangibles=[
                {"name": "Patents", "value": 60_000_000, "method": "Relief-from-Royalty"},
            ],
            liabilities_fv=10_000_000,
        )
        net_identifiable = 15_000_000 + 60_000_000 - 10_000_000
        assert result.value == 100_000_000 - net_identifiable

    def test_no_goodwill(self):
        result = purchase_price_allocation(
            purchase_price=75_000_000,
            tangible_assets_fv=15_000_000,
            identified_intangibles=[
                {"name": "Brand", "value": 60_000_000, "method": "Relief-from-Royalty"},
            ],
        )
        assert result.value == 0.0

    def test_bargain_purchase_raises(self):
        with pytest.raises(ValueError, match="Bargain purchase"):
            purchase_price_allocation(
                purchase_price=50_000_000,
                tangible_assets_fv=30_000_000,
                identified_intangibles=[
                    {"name": "Patents", "value": 30_000_000, "method": "MPEEM"},
                ],
            )

    def test_allocation_percentages(self):
        result = purchase_price_allocation(
            purchase_price=100_000_000,
            tangible_assets_fv=15_000_000,
            identified_intangibles=[
                {"name": "Intangible A", "value": 60_000_000, "method": "RFR"},
            ],
        )
        alloc = result.assumptions["allocation"]
        assert alloc["tangible"] == "15.0%"
        assert alloc["intangible"] == "60.0%"
        assert alloc["goodwill"] == "25.0%"

    def test_empty_intangibles_raises(self):
        with pytest.raises(ValueError):
            purchase_price_allocation(
                purchase_price=100_000_000,
                tangible_assets_fv=15_000_000,
                identified_intangibles=[],
            )

    def test_missing_intangible_fields_raises(self):
        with pytest.raises(ValueError):
            purchase_price_allocation(
                purchase_price=100_000_000,
                tangible_assets_fv=15_000_000,
                identified_intangibles=[{"name": "Test"}],
            )

    def test_negative_purchase_price_raises(self):
        with pytest.raises(ValueError):
            purchase_price_allocation(
                purchase_price=-100,
                tangible_assets_fv=50,
                identified_intangibles=[{"name": "X", "value": 10, "method": "Y"}],
            )

    def test_returns_steps(self):
        result = purchase_price_allocation(
            purchase_price=100_000_000,
            tangible_assets_fv=15_000_000,
            identified_intangibles=[
                {"name": "Brand", "value": 60_000_000, "method": "RFR"},
            ],
        )
        assert len(result.steps) >= 5
        assert any(s.get("item") == "Purchase Price" for s in result.steps)
        assert any(s.get("item") == "Goodwill (residual)" for s in result.steps)

    def test_multiple_intangibles(self):
        result = purchase_price_allocation(
            purchase_price=200_000_000,
            tangible_assets_fv=40_000_000,
            identified_intangibles=[
                {"name": "Customer List", "value": 30_000_000, "method": "MPEEM"},
                {"name": "Trade Name", "value": 50_000_000, "method": "RFR"},
                {"name": "Patents", "value": 20_000_000, "method": "RFR"},
                {"name": "Software", "value": 10_000_000, "method": "Cost"},
            ],
            liabilities_fv=5_000_000,
        )
        net = 40_000_000 + 110_000_000 - 5_000_000
        assert result.value == 200_000_000 - net


class TestBargainPurchaseAnalysis:
    """Tests for bargain_purchase_analysis function."""

    def test_happy_path_basic(self):
        result = bargain_purchase_analysis(
            purchase_price=40_000_000,
            fair_value_net_assets=50_000_000,
        )
        assert result["value"] == 10_000_000.0
        assert "Bargain Purchase" in result["method"]

    def test_happy_path_large_gain(self):
        result = bargain_purchase_analysis(
            purchase_price=30_000_000,
            fair_value_net_assets=60_000_000,
        )
        assert result["value"] == 30_000_000.0

    def test_error_not_bargain_purchase(self):
        with pytest.raises(ValueError, match="Not a bargain purchase"):
            bargain_purchase_analysis(
                purchase_price=60_000_000,
                fair_value_net_assets=50_000_000,
            )

    def test_error_at_par(self):
        with pytest.raises(ValueError):
            bargain_purchase_analysis(
                purchase_price=50_000_000,
                fair_value_net_assets=50_000_000,
            )

    def test_error_negative_purchase_price(self):
        with pytest.raises(ValueError):
            bargain_purchase_analysis(
                purchase_price=-10_000_000,
                fair_value_net_assets=50_000_000,
            )

    def test_returns_gain_percentage(self):
        result = bargain_purchase_analysis(
            purchase_price=40_000_000,
            fair_value_net_assets=50_000_000,
        )
        assert result["assumptions"]["gain_percentage"] == 0.2


class TestContingentConsiderationValuation:
    """Tests for contingent_consideration_valuation function."""

    def test_happy_path_basic(self):
        scenarios = [
            {"probability": 0.3, "payment": 5_000_000, "period": 1},
            {"probability": 0.5, "payment": 10_000_000, "period": 2},
            {"probability": 0.2, "payment": 15_000_000, "period": 3},
        ]
        result = contingent_consideration_valuation(scenarios, 0.10)
        assert result["value"] > 0
        assert "Contingent" in result["method"]

    def test_happy_path_single_scenario(self):
        scenarios = [
            {"probability": 1.0, "payment": 10_000_000, "period": 1},
        ]
        result = contingent_consideration_valuation(scenarios, 0.10)
        assert result["value"] == pytest.approx(10_000_000 / 1.10, rel=0.01)

    def test_happy_path_default_period(self):
        scenarios = [
            {"probability": 0.5, "payment": 5_000_000},
            {"probability": 0.5, "payment": 10_000_000},
        ]
        result = contingent_consideration_valuation(scenarios, 0.10)
        assert result["value"] > 0

    def test_error_probabilities_not_summing_to_one(self):
        scenarios = [
            {"probability": 0.3, "payment": 5_000_000},
            {"probability": 0.3, "payment": 10_000_000},
        ]
        with pytest.raises(ValueError, match="probabilities must sum"):
            contingent_consideration_valuation(scenarios, 0.10)

    def test_error_empty_scenarios(self):
        with pytest.raises(ValueError):
            contingent_consideration_valuation([], 0.10)

    def test_error_negative_payment(self):
        scenarios = [
            {"probability": 1.0, "payment": -5_000_000},
        ]
        with pytest.raises(ValueError):
            contingent_consideration_valuation(scenarios, 0.10)

    def test_error_zero_discount_rate(self):
        scenarios = [
            {"probability": 1.0, "payment": 10_000_000},
        ]
        with pytest.raises(ValueError):
            contingent_consideration_valuation(scenarios, 0)


class TestDeferredTaxLiabilityPPA:
    """Tests for deferred_tax_liability_ppa function."""

    def test_happy_path_zero_tax_basis(self):
        intangibles = [
            {"name": "Customer Relationships", "fair_value": 20_000_000},
            {"name": "Technology", "fair_value": 25_000_000},
        ]
        result = deferred_tax_liability_ppa(intangibles, 0, 0.25)
        assert result["value"] == 11_250_000.0
        assert "Deferred Tax" in result["method"]

    def test_happy_path_with_tax_basis(self):
        intangibles = [
            {"name": "Patents", "fair_value": 30_000_000},
        ]
        result = deferred_tax_liability_ppa(intangibles, 10_000_000, 0.21)
        assert result["value"] == pytest.approx(4_200_000.0, rel=0.01)

    def test_happy_path_single_intangible(self):
        intangibles = [
            {"name": "Brand", "fair_value": 15_000_000},
        ]
        result = deferred_tax_liability_ppa(intangibles, 0, 0.30)
        assert result["value"] == 4_500_000.0

    def test_error_empty_intangibles(self):
        with pytest.raises(ValueError):
            deferred_tax_liability_ppa([], 0, 0.25)

    def test_error_missing_name(self):
        with pytest.raises(ValueError):
            deferred_tax_liability_ppa([{"fair_value": 10_000_000}], 0, 0.25)

    def test_error_negative_fair_value(self):
        with pytest.raises(ValueError):
            deferred_tax_liability_ppa([{"name": "X", "fair_value": -100}], 0, 0.25)

    def test_error_zero_tax_rate(self):
        with pytest.raises(ValueError):
            deferred_tax_liability_ppa(
                [{"name": "X", "fair_value": 10_000_000}], 0, 0
            )

    def test_returns_temporary_difference(self):
        intangibles = [
            {"name": "A", "fair_value": 20_000_000},
            {"name": "B", "fair_value": 30_000_000},
        ]
        result = deferred_tax_liability_ppa(intangibles, 5_000_000, 0.25)
        assert result["assumptions"]["temporary_difference"] == 45_000_000
