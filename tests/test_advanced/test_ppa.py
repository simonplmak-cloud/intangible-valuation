"""Tests for purchase price allocation (TASK-034)."""

import pytest

from src.advanced.purchase_price_alloc import purchase_price_allocation


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
