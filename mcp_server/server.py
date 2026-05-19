"""MCP server for intangible asset valuation.

Exposes all valuation methods as MCP tools via fastmcp.
Run with: python -m mcp_server.server
"""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_server.tools import (
    present_value,
    future_value,
    annuity_pv,
    perpetuity_pv,
    growing_annuity_pv,
    terminal_value,
    build_up_discount_rate,
    capm_discount_rate,
    wacc,
    tax_amortization_benefit,
    control_premium,
    dlom_finnerty,
    currency_adjusted_discount_rate,
    reproduction_cost,
    replacement_cost,
    market_approach_comparables,
    royalty_capitalization,
    relief_from_royalty,
    mpeem,
    single_period_excess_earnings,
    incremental_cashflow,
    contributory_asset_charges,
    patent_valuation,
    trademark_valuation,
    copyright_valuation,
    trade_secret_valuation,
    developed_technology_valuation,
    software_valuation,
    data_asset_valuation,
    platform_valuation,
    customer_relationship_valuation,
    distribution_network_valuation,
    non_compete_valuation,
    assembled_workforce_valuation,
    key_person_value,
    goodwill,
    purchase_price_allocation,
    goodwill_impairment_test,
    intangible_impairment_test,
    royalty_rate_benchmark,
    adjust_royalty_rate,
    twenty_five_percent_rule,
    cup_transfer_price,
    patent_infringement_damages,
    monte_carlo_valuation,
    monte_carlo_sensitivity,
    decision_tree_valuation,
    sensitivity_analysis,
    estimate_useful_life,
)

mcp = FastMCP("intangible-valuation")

# Core Math
mcp.tool()(present_value)
mcp.tool()(future_value)
mcp.tool()(annuity_pv)
mcp.tool()(perpetuity_pv)
mcp.tool()(growing_annuity_pv)
mcp.tool()(terminal_value)
mcp.tool()(build_up_discount_rate)
mcp.tool()(capm_discount_rate)
mcp.tool()(wacc)
mcp.tool()(tax_amortization_benefit)
mcp.tool()(control_premium)
mcp.tool()(dlom_finnerty)
mcp.tool()(currency_adjusted_discount_rate)

# Approaches
mcp.tool()(reproduction_cost)
mcp.tool()(replacement_cost)
mcp.tool()(market_approach_comparables)
mcp.tool()(royalty_capitalization)

# Income Methods
mcp.tool()(relief_from_royalty)
mcp.tool()(mpeem)
mcp.tool()(single_period_excess_earnings)
mcp.tool()(incremental_cashflow)
mcp.tool()(contributory_asset_charges)

# Asset Types
mcp.tool()(patent_valuation)
mcp.tool()(trademark_valuation)
mcp.tool()(copyright_valuation)
mcp.tool()(trade_secret_valuation)
mcp.tool()(developed_technology_valuation)
mcp.tool()(software_valuation)
mcp.tool()(data_asset_valuation)
mcp.tool()(platform_valuation)
mcp.tool()(customer_relationship_valuation)
mcp.tool()(distribution_network_valuation)
mcp.tool()(non_compete_valuation)
mcp.tool()(assembled_workforce_valuation)
mcp.tool()(key_person_value)

# Advanced
mcp.tool()(goodwill)
mcp.tool()(purchase_price_allocation)
mcp.tool()(goodwill_impairment_test)
mcp.tool()(intangible_impairment_test)
mcp.tool()(royalty_rate_benchmark)
mcp.tool()(adjust_royalty_rate)
mcp.tool()(twenty_five_percent_rule)
mcp.tool()(cup_transfer_price)
mcp.tool()(patent_infringement_damages)
mcp.tool()(monte_carlo_valuation)
mcp.tool()(monte_carlo_sensitivity)
mcp.tool()(decision_tree_valuation)
mcp.tool()(sensitivity_analysis)
mcp.tool()(estimate_useful_life)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
