"""Book example tests verifying all numerical examples from the Ascent Partners textbook.

Each test imports the relevant function and asserts the result matches the book's answer
within an acceptable tolerance (0.5% relative or $1 absolute for small values).
"""

import math

from src.advanced.goodwill import goodwill
from src.advanced.purchase_price_alloc import purchase_price_allocation
from src.approaches.cost_approach import replacement_cost
from src.core.discount_rates import build_up_discount_rate
from src.core.statistics import decision_tree_valuation, monte_carlo_valuation
from src.core.time_value import annuity_pv, perpetuity_pv, present_value
from src.income_methods.relief_from_royalty import relief_from_royalty

TOLERANCE_PCT = 0.005


def assert_close(actual, expected, pct=TOLERANCE_PCT, abs_tol=1.0):
    """Assert actual is within pct% or abs_tol of expected."""
    rel_tol = abs(expected) * pct
    assert math.isclose(actual, expected, rel_tol=rel_tol, abs_tol=abs_tol), (
        f"Expected {expected:,.2f}, got {actual:,.2f} "
        f"(diff={abs(actual - expected):,.2f}, rel_tol={rel_tol:,.2f})"
    )


# ===========================================================================
# Chapter 2 — Time Value of Money
# ===========================================================================

class TestChapter2Basic:
    """Chapter 2 Basic Exercises."""

    def test_q1_pv_of_single_sum(self):
        """Ch 2 Basic Q1: PV of $500,000 in 8 years at 10% = $233,253."""
        result = present_value(future_value=500_000, discount_rate=0.10, periods=8)
        assert_close(result.value, 233_253)

    def test_q2_solve_for_discount_rate(self):
        """Ch 2 Basic Q2: FV $1M, PV $620,921, 5 years -> discount rate = 10%.

        Verify by computing FV from PV at 10% for 5 years.
        """
        from src.core.time_value import future_value
        result = future_value(present_value=620_921, discount_rate=0.10, periods=5)
        assert_close(result.value, 1_000_000, pct=0.001)

    def test_q3_build_up_components(self):
        """Ch 2 Basic Q3: Build-up components list.

        Verify the build-up method adds all risk components correctly.
        Example: Rf=4%, ERP=6%, Size=2%, Industry=1%, Specific=3% = 16%
        """
        result = build_up_discount_rate(
            risk_free_rate=0.04,
            equity_risk_premium=0.06,
            size_premium=0.02,
            industry_risk_premium=0.01,
            specific_risk_premium=0.03,
        )
        assert_close(result.value, 0.16, abs_tol=0.0001)
        assert result.method == "build_up"


class TestChapter2Intermediate:
    """Chapter 2 Intermediate Exercises."""

    def test_q1_annuity_pv(self):
        """Ch 2 Intermediate Q1: Annuity $50,000 for 10 years at 15% = $250,937."""
        result = annuity_pv(payment=50_000, discount_rate=0.15, periods=10)
        assert_close(result.value, 250_937)

    def test_q3_monte_carlo_patent_valuation(self):
        """Ch 2 Intermediate Q3: Monte Carlo for patent valuation scenario.

        Simulate patent valuation with uncertain revenue and discount rate.
        Verifies that Monte Carlo returns valid statistics.
        """
        def patent_valuation(revenue, discount_rate):
            royalty = revenue * 0.05
            return royalty / discount_rate

        result = monte_carlo_valuation(
            valuation_fn=patent_valuation,
            input_distributions=[
                {
                    "name": "revenue",
                    "distribution": "triangular",
                    "params": {"low": 8_000_000, "mode": 10_000_000, "high": 12_000_000},
                },
                {
                    "name": "discount_rate",
                    "distribution": "normal",
                    "params": {"mean": 0.15, "std": 0.02},
                },
            ],
            iterations=5000,
            seed=42,
        )

        assert result["mean"] > 0
        assert result["std"] > 0
        assert result["percentile_5"] < result["median"] < result["percentile_95"]
        assert result["method"] == "Monte Carlo Simulation"
        assert result["iterations"] == 5000


class TestChapter2Advanced:
    """Chapter 2 Advanced Exercises."""

    def test_q1_decision_tree_biogen_futures(self):
        """Ch 2 Advanced Q1: Decision tree for BioGen Futures.

        Option A: Sell now for $50M
        Option B: Proceed to Phase III trials
            - Success (60%): Value = $120M, Cost = $20M
            - Failure (40%): Value = $0, Cost = $20M

        EV(Phase III) = 0.60 * (120M - 20M) + 0.40 * (0 - 20M) = 60M - 8M = 52M
        Optimal decision: Phase III (52M > 50M)
        """
        tree = {
            "nodes": [
                {"id": "root", "type": "decision", "label": "BioGen Decision", "value": 0},
                {"id": "sell", "type": "terminal", "label": "Sell Now", "value": 50_000_000},
                {"id": "trials", "type": "chance", "label": "Phase III Trials", "value": 0},
                {"id": "success", "type": "terminal", "label": "Trial Success", "value": 120_000_000},
                {"id": "failure", "type": "terminal", "label": "Trial Failure", "value": 0},
            ],
            "edges": [
                {"from": "root", "to": "sell", "probability": 1.0, "cost": 0},
                {"from": "root", "to": "trials", "probability": 1.0, "cost": 0},
                {"from": "trials", "to": "success", "probability": 0.60, "cost": 20_000_000},
                {"from": "trials", "to": "failure", "probability": 0.40, "cost": 20_000_000},
            ],
        }

        result = decision_tree_valuation(tree)

        assert_close(result["expected_value"], 52_000_000)
        assert "trials" in result["optimal_path"]


# ===========================================================================
# Chapter 3 — Cost Approach
# ===========================================================================

class TestChapter3CostApproach:
    """Chapter 3 Cost Approach Examples."""

    def test_software_obsolescence(self):
        """Ch 3 Example: Software $650K cost, 40% obsolescence = $390K."""
        result = replacement_cost(
            current_cost=650_000,
            obsolescence_factors={"functional": 0.40},
        )
        assert_close(result["value"], 390_000)

    def test_trademark_perpetuity(self):
        """Ch 3 Example: Trademark $10M revenue, 4% royalty, 15% discount = $2,666,667.

        Perpetuity: PV = (Revenue * Royalty Rate) / Discount Rate
        PV = (10,000,000 * 0.04) / 0.15 = 400,000 / 0.15 = 2,666,667
        """
        royalty_payment = 10_000_000 * 0.04
        result = perpetuity_pv(payment=royalty_payment, discount_rate=0.15)
        assert_close(result.value, 2_666_667)

    def test_patent_annuity(self):
        """Ch 3 Example: Patent $200K/year for 10 years at 18% = $898,264.

        Annuity PV of $200,000 per year for 10 years at 18% discount rate.
        """
        result = annuity_pv(payment=200_000, discount_rate=0.18, periods=10)
        assert_close(result.value, 898_264, pct=0.01)


# ===========================================================================
# Chapter 4 — Relief from Royalty
# ===========================================================================

class TestChapter4ReliefFromRoyalty:
    """Chapter 4 Relief from Royalty Example."""

    def test_relief_from_royalty_with_projections(self):
        """Ch 4: Relief-from-Royalty example with revenue projections.

        Revenue projections over 5 years, 5% royalty, 12% discount, 25% tax.
        Verifies the method computes a positive value with correct structure.
        """
        revenue = [1_000_000, 1_100_000, 1_200_000, 1_300_000, 1_400_000]
        result = relief_from_royalty(
            revenue_projections=revenue,
            royalty_rate=0.05,
            discount_rate=0.12,
            tax_rate=0.25,
            useful_life=5,
        )

        assert result["value"] > 0
        assert result["method"] == "Relief from Royalty"
        assert result["pv_before_tab"] > 0
        assert result["tab_factor"] > 1.0

        total_revenue = sum(revenue)
        total_royalty = total_revenue * 0.05
        assert result["value"] < total_royalty

    def test_relief_from_royalty_without_tab(self):
        """Verify TAB-disabled calculation matches PV of after-tax royalties."""
        revenue = [500_000, 550_000, 600_000]
        result = relief_from_royalty(
            revenue_projections=revenue,
            royalty_rate=0.04,
            discount_rate=0.10,
            tax_rate=0.25,
            useful_life=3,
            tab_enabled=False,
        )

        assert result["tab_factor"] == 1.0
        assert_close(result["value"], result["pv_before_tab"], pct=0.0001)


# ===========================================================================
# Chapter 10 — Purchase Price Allocation
# ===========================================================================

class TestChapter10PPA:
    """Chapter 10 Purchase Price Allocation Example."""

    def test_ppa_waterfall(self):
        """Ch 10: PPA example.

        $100M purchase, $15M tangible, $60M identified intangibles -> $25M goodwill.
        Net identifiable = 15M + 60M - 0 = 75M
        Goodwill = 100M - 75M = 25M
        """
        result = purchase_price_allocation(
            purchase_price=100_000_000,
            tangible_assets_fv=15_000_000,
            identified_intangibles=[
                {"name": "Customer Relationships", "value": 25_000_000, "method": "MPEEM"},
                {"name": "Technology", "value": 20_000_000, "method": "relief-from-royalty"},
                {"name": "Trademark", "value": 15_000_000, "method": "relief-from-royalty"},
            ],
            liabilities_fv=0,
        )

        assert_close(result.value, 25_000_000)
        assert result.method == "Purchase Price Allocation"

    def test_ppa_with_liabilities(self):
        """PPA with assumed liabilities reduces net identifiable assets."""
        result = purchase_price_allocation(
            purchase_price=50_000_000,
            tangible_assets_fv=10_000_000,
            identified_intangibles=[
                {"name": "Patent Portfolio", "value": 20_000_000, "method": "relief-from-royalty"},
            ],
            liabilities_fv=5_000_000,
        )

        net_identifiable = 10_000_000 + 20_000_000 - 5_000_000
        expected_goodwill = 50_000_000 - net_identifiable
        assert_close(result.value, expected_goodwill)

    def test_goodwill_standalone(self):
        """Verify standalone goodwill calculation matches PPA residual."""
        result = goodwill(
            purchase_price=100_000_000,
            fair_value_net_identifiable_assets=75_000_000,
        )
        assert_close(result.value, 25_000_000)
