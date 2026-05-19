"""Tests for impairment testing (TASK-036)."""

import pytest

from src.advanced.impairment_testing import goodwill_impairment_test, intangible_impairment_test


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
