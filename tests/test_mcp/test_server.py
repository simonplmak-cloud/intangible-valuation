"""Tests for MCP server startup and tool discovery."""

from __future__ import annotations

import asyncio
import json

from mcp_server.server import mcp


def _get_tool_names() -> set[str]:
    """Get set of registered tool names."""
    tools = asyncio.run(mcp.list_tools())
    return {t.name for t in tools}


class TestServerToolDiscovery:
    """Test that the MCP server has all expected tools registered."""

    def test_server_has_name(self):
        assert mcp.name == "intangible-valuation"

    def test_core_math_tools_registered(self):
        """Verify all core math tools are registered."""
        tool_names = _get_tool_names()
        expected = {
            "present_value",
            "future_value",
            "annuity_pv",
            "perpetuity_pv",
            "growing_annuity_pv",
            "terminal_value",
            "build_up_discount_rate",
            "capm_discount_rate",
            "wacc",
            "tax_amortization_benefit",
            "control_premium",
            "dlom_finnerty",
            "currency_adjusted_discount_rate",
        }
        missing = expected - tool_names
        assert not missing, f"Missing core math tools: {missing}"

    def test_approach_tools_registered(self):
        """Verify all approach tools are registered."""
        tool_names = _get_tool_names()
        expected = {
            "reproduction_cost",
            "replacement_cost",
            "market_approach_comparables",
            "royalty_capitalization",
        }
        missing = expected - tool_names
        assert not missing, f"Missing approach tools: {missing}"

    def test_income_method_tools_registered(self):
        """Verify all income method tools are registered."""
        tool_names = _get_tool_names()
        expected = {
            "relief_from_royalty",
            "mpeem",
            "single_period_excess_earnings",
            "incremental_cashflow",
            "contributory_asset_charges",
        }
        missing = expected - tool_names
        assert not missing, f"Missing income method tools: {missing}"

    def test_asset_type_tools_registered(self):
        """Verify all asset type tools are registered."""
        tool_names = _get_tool_names()
        expected = {
            "patent_valuation",
            "trademark_valuation",
            "copyright_valuation",
            "trade_secret_valuation",
            "developed_technology_valuation",
            "software_valuation",
            "data_asset_valuation",
            "platform_valuation",
            "customer_relationship_valuation",
            "distribution_network_valuation",
            "non_compete_valuation",
            "assembled_workforce_valuation",
            "key_person_value",
        }
        missing = expected - tool_names
        assert not missing, f"Missing asset type tools: {missing}"

    def test_advanced_tools_registered(self):
        """Verify all advanced tools are registered."""
        tool_names = _get_tool_names()
        expected = {
            "goodwill",
            "purchase_price_allocation",
            "goodwill_impairment_test",
            "intangible_impairment_test",
            "royalty_rate_benchmark",
            "adjust_royalty_rate",
            "twenty_five_percent_rule",
            "cup_transfer_price",
            "patent_infringement_damages",
            "monte_carlo_valuation",
            "monte_carlo_sensitivity",
            "decision_tree_valuation",
            "sensitivity_analysis",
            "estimate_useful_life",
        }
        missing = expected - tool_names
        assert not missing, f"Missing advanced tools: {missing}"

    def test_total_tool_count(self):
        """Verify total number of registered tools (13+4+5+13+14 = 49)."""
        tool_names = _get_tool_names()
        assert len(tool_names) == 49, f"Expected 49 tools, got {len(tool_names)}"

    def test_tools_have_descriptions(self):
        """Verify all registered tools have descriptions."""
        tools = asyncio.run(mcp.list_tools())
        for tool in tools:
            assert tool.description, f"Tool '{tool.name}' has no description"

    def test_tools_return_json_strings(self):
        """Verify tools return valid JSON strings."""
        from mcp_server.tools import present_value
        result = present_value(future_value=1000000, discount_rate=0.10, periods=5)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "value" in parsed
        assert "method" in parsed


class TestServerImport:
    """Test that server module imports correctly."""

    def test_server_import(self):
        from mcp_server import server
        assert hasattr(server, "mcp")
        assert hasattr(server, "main")

    def test_tools_import(self):
        from mcp_server import tools
        assert hasattr(tools, "present_value")
        assert hasattr(tools, "goodwill")
        assert hasattr(tools, "mpeem")
