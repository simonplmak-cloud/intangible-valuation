"""Vercel-deployable MCP server entry point.

This provides the MCP tools/list and tools/call handlers
as a Vercel Python function, importing from the intangible_valuation package.
"""

import json
from http.server import BaseHTTPRequestHandler

# Lazy import — fails gracefully without the package installed
_MCP_TOOLS = []

try:
    from intangible_valuation.core.time_value import (
        present_value,
        future_value,
        annuity_pv,
        perpetuity_pv,
        growing_annuity_pv,
        terminal_value,
    )
    from intangible_valuation.core.discount_rates import (
        build_up_method,
        capm,
        wacc,
        tax_amortization_benefit,
        control_premium,
        dlom_finnerty,
    )
    from intangible_valuation.income_methods.relief_from_royalty import relief_from_royalty
    from intangible_valuation.income_methods.excess_earnings import mpeem, single_period_excess_earnings
    from intangible_valuation.asset_types.ip_valuation import (
        patent_valuation,
        copyright_valuation,
        trade_secret_valuation,
    )
    from intangible_valuation.asset_types.brand_valuation import trademark_valuation
    from intangible_valuation.asset_types.customer_valuation import customer_relationship_valuation
    from intangible_valuation.advanced.goodwill import goodwill
    from intangible_valuation.advanced.purchase_price_alloc import purchase_price_allocation
    from intangible_valuation.advanced.impairment_testing import goodwill_impairment_test

    _MCP_TOOLS = [
        {"name": "present_value", "description": "Calculate present value (Ch 2, Sec 2.1)", "function": present_value},
        {"name": "future_value", "description": "Calculate future value (Ch 2, Sec 2.1)", "function": future_value},
        {"name": "annuity_pv", "description": "Present value of an annuity (Ch 2, Sec 2.2)", "function": annuity_pv},
        {
            "name": "perpetuity_pv",
            "description": "Present value of a perpetuity (Ch 2, Sec 2.2)",
            "function": perpetuity_pv,
        },
        {
            "name": "growing_annuity_pv",
            "description": "Growing annuity present value (Ch 2, Sec 2.2)",
            "function": growing_annuity_pv,
        },
        {
            "name": "terminal_value",
            "description": "Terminal value (Gordon/Exit Multiple) (Ch 2, Sec 2.4)",
            "function": terminal_value,
        },
        {"name": "capm", "description": "Capital Asset Pricing Model (Ch 2, Sec 2.3)", "function": capm},
        {"name": "wacc", "description": "Weighted Average Cost of Capital (Ch 2, Sec 2.3)", "function": wacc},
        {
            "name": "build_up_discount_rate",
            "description": "Build-up method for discount rate (Ch 2, Sec 2.3)",
            "function": build_up_method,
        },
        {
            "name": "tax_amortization_benefit",
            "description": "Tax Amortization Benefit (Ch 3, Sec 3.4)",
            "function": tax_amortization_benefit,
        },
        {
            "name": "relief_from_royalty",
            "description": "Relief from Royalty with TAB (Ch 4, Sec 4.2)",
            "function": relief_from_royalty,
        },
        {"name": "mpeem", "description": "Multi-Period Excess Earnings Method (Ch 4, Sec 4.1)", "function": mpeem},
        {
            "name": "single_period_excess_earnings",
            "description": "Single-period excess earnings (Ch 4, Sec 4.1)",
            "function": single_period_excess_earnings,
        },
        {"name": "patent_valuation", "description": "Patent valuation (Ch 5)", "function": patent_valuation},
        {"name": "goodwill", "description": "Goodwill calculation (Ch 10, ASC 805)", "function": goodwill},
        {
            "name": "purchase_price_allocation",
            "description": "PPA waterfall (Ch 10, ASC 805)",
            "function": purchase_price_allocation,
        },
        {
            "name": "goodwill_impairment_test",
            "description": "Goodwill impairment test (Ch 11, ASC 350)",
            "function": goodwill_impairment_test,
        },
    ]
except ImportError:
    pass


def _to_plain(result):
    if hasattr(result, "model_dump"):
        return result.model_dump(mode="json")
    if isinstance(result, dict):
        return result
    return {"value": result}


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
        except (json.JSONDecodeError, ValueError):
            self._send_error(-32700, "Parse error")
            return

        req_id = body.get("id")
        method = body.get("method")

        if method == "tools/list":
            tools = [{"name": t["name"], "description": t["description"]} for t in _MCP_TOOLS]
            self._send_json(200, {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}})
            return

        if method == "tools/call":
            params = body.get("params", {})
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})

            tool = next((t for t in _MCP_TOOLS if t["name"] == tool_name), None)
            if not tool:
                self._send_error(-32601, f"Tool not found: {tool_name}", req_id)
                return

            try:
                result = tool["function"](**arguments)
                self._send_json(
                    200,
                    {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {"content": [{"type": "text", "text": json.dumps(_to_plain(result), default=str)}]},
                    },
                )
            except Exception as e:
                self._send_error(-32603, str(e), req_id)
            return

        if method == "initialize":
            self._send_json(
                200,
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "intangible-valuation-mcp", "version": "2.0.0"},
                        "capabilities": {"tools": {}},
                    },
                },
            )
            return

        self._send_error(-32601, f"Method not found: {method}", req_id)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, code, data):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, code, message, req_id=None):
        self._send_json(
            200 if code != -32700 else 400,
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": code, "message": message},
            },
        )
