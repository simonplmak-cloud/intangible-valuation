"""Tests for litigation damages (TASK-042)."""

import pytest

from intangible_valuation.advanced.litigation import patent_infringement_damages


class TestPatentInfringementDamages:
    def test_basic_damages(self):
        result = patent_infringement_damages(
            lost_profits_or_royalty=1_000_000,
            infringement_period=5,
            discount_rate=0.10,
            prejudgment_interest_rate=0.05,
        )
        assert result.value > 0
        assert "Patent Infringement Damages" in result.method

    def test_pv_of_annuity(self):
        result = patent_infringement_damages(
            lost_profits_or_royalty=1_000_000,
            infringement_period=5,
            discount_rate=0.10,
            prejudgment_interest_rate=0.05,
        )
        pv = result.assumptions["pv_damages"]
        assert pv > 0
        assert pv < 5_000_000

    def test_prejudgment_interest_positive(self):
        result = patent_infringement_damages(
            lost_profits_or_royalty=1_000_000,
            infringement_period=5,
            discount_rate=0.10,
            prejudgment_interest_rate=0.05,
        )
        assert result.assumptions["prejudgment_interest"] > 0

    def test_zero_interest_rate(self):
        result = patent_infringement_damages(
            lost_profits_or_royalty=1_000_000,
            infringement_period=3,
            discount_rate=0.10,
            prejudgment_interest_rate=0,
        )
        assert result.assumptions["prejudgment_interest"] == 0.0

    def test_longer_period_higher_damages(self):
        r1 = patent_infringement_damages(1_000_000, 3, 0.10, 0.05)
        r2 = patent_infringement_damages(1_000_000, 7, 0.10, 0.05)
        assert r2.value > r1.value

    def test_higher_royalty_higher_damages(self):
        r1 = patent_infringement_damages(500_000, 5, 0.10, 0.05)
        r2 = patent_infringement_damages(1_000_000, 5, 0.10, 0.05)
        assert r2.value > r1.value

    def test_negative_royalty_raises(self):
        with pytest.raises(ValueError):
            patent_infringement_damages(-1_000_000, 5, 0.10, 0.05)

    def test_zero_period_raises(self):
        with pytest.raises(ValueError):
            patent_infringement_damages(1_000_000, 0, 0.10, 0.05)

    def test_zero_discount_raises(self):
        with pytest.raises(ValueError):
            patent_infringement_damages(1_000_000, 5, 0, 0.05)

    def test_discount_over_one_raises(self):
        with pytest.raises(ValueError):
            patent_infringement_damages(1_000_000, 5, 1.5, 0.05)

    def test_interest_over_one_raises(self):
        with pytest.raises(ValueError):
            patent_infringement_damages(1_000_000, 5, 0.10, 1.5)

    def test_returns_steps(self):
        result = patent_infringement_damages(1_000_000, 5, 0.10, 0.05)
        assert len(result.steps) >= 6
        assert any("Total Damages" in s.get("description", "") for s in result.steps)

    def test_formula_reference(self):
        result = patent_infringement_damages(1_000_000, 5, 0.10, 0.05)
        assert "Ch 15.2" in result.formula_reference
