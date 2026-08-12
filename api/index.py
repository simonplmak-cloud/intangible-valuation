"""Vercel serverless API for intangible valuation — all formulas inline, zero deps."""

import json, math
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse


def present_value(future_value, discount_rate, periods):
    pv = future_value / ((1 + discount_rate) ** periods)
    steps = [f"PV = FV / (1 + r)^n", f"PV = {future_value} / (1 + {discount_rate})^{periods}", f"PV = ${pv:,.2f}"]
    return {
        "value": round(pv, 2),
        "method": "Present Value",
        "formula_reference": "PV = FV / (1+r)^n",
        "steps": steps,
        "assumptions": ["Discount rate constant", "Single cash flow at period n"],
    }


def future_value(present_value, discount_rate, periods):
    fv = present_value * ((1 + discount_rate) ** periods)
    return {"value": round(fv, 2), "method": "Future Value", "formula_reference": "FV = PV * (1+r)^n"}


def annuity_pv(payment, discount_rate, periods):
    pv = payment * (1 - (1 + discount_rate) ** -periods) / discount_rate if discount_rate > 0 else payment * periods
    return {"value": round(pv, 2), "method": "Annuity PV", "formula_reference": "PV = PMT * [1-(1+r)^(-n)] / r"}


def perpetuity_pv(payment, discount_rate):
    return {"value": round(payment / discount_rate, 2), "method": "Perpetuity PV", "formula_reference": "PV = PMT / r"}


def terminal_value(final_year_cashflow, perpetual_growth_rate, discount_rate):
    tv = final_year_cashflow * (1 + perpetual_growth_rate) / (discount_rate - perpetual_growth_rate)
    return {
        "value": round(tv, 2),
        "method": "Terminal Value (Gordon Growth)",
        "formula_reference": "TV = FCF*(1+g)/(r-g)",
    }


def build_up_discount_rate(
    risk_free_rate, equity_risk_premium, size_premium=0, industry_risk_premium=0, specific_risk_premium=0
):
    rate = risk_free_rate + equity_risk_premium + size_premium + industry_risk_premium + specific_risk_premium
    return {
        "value": round(rate, 4),
        "method": "Build-Up Discount Rate",
        "formula_reference": "r = Rf + ERP + Size + Industry + Specific",
    }


def capm_discount_rate(risk_free_rate, beta, market_return):
    rate = risk_free_rate + beta * (market_return - risk_free_rate)
    return {"value": round(rate, 4), "method": "CAPM", "formula_reference": "r = Rf + Beta*(Rm-Rf)"}


def wacc(equity_value, debt_value, cost_of_equity, cost_of_debt, tax_rate):
    total = equity_value + debt_value
    rate = (equity_value / total) * cost_of_equity + (debt_value / total) * cost_of_debt * (1 - tax_rate)
    return {"value": round(rate, 4), "method": "WACC", "formula_reference": "WACC = (E/V)*Re + (D/V)*Rd*(1-Tc)"}


def relief_from_royalty(revenue_projections, royalty_rate, discount_rate, tax_rate, useful_life, tab_enabled=True):
    pv = 0.0
    steps = []
    for t, rev in enumerate(revenue_projections, 1):
        royalty = rev * royalty_rate
        after_tax = royalty * (1 - tax_rate)
        period_pv = after_tax / ((1 + discount_rate) ** t)
        pv += period_pv
        steps.append(
            f"Period {t}: revenue=${rev:,.0f}, royalty=${royalty:,.0f}, after-tax=${after_tax:,.0f}, PV=${period_pv:,.0f}"
        )
    tab = 1.0
    if tab_enabled and tax_rate > 0:
        af = sum(1 / ((1 + discount_rate) ** t) for t in range(1, useful_life + 1))
        tab = 1 / (1 - (tax_rate * af / useful_life))
    value = pv * tab
    steps.append(f"PV before TAB: ${pv:,.2f}, TAB factor: {tab:.4f}")
    return {
        "value": round(value, 2),
        "method": "Relief from Royalty",
        "formula_reference": "Ch 4: RFR with TAB",
        "steps": steps,
        "assumptions": ["Arm's length royalty rate", "Reasonable revenue projections"],
        "pv_before_tab": round(pv, 2),
        "tab_factor": round(tab, 4),
    }


ROUTES = {
    "present-value": present_value,
    "future-value": future_value,
    "annuity-pv": annuity_pv,
    "perpetuity-pv": perpetuity_pv,
    "terminal-value": terminal_value,
    "build-up-discount-rate": build_up_discount_rate,
    "capm": capm_discount_rate,
    "wacc": wacc,
    "relief-from-royalty": relief_from_royalty,
}


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        method = urlparse(self.path).path.rstrip("/").split("/api/")[-1]
        func = ROUTES.get(method)
        if not func:
            self._send(404, {"error": f"Unknown: {method}", "available": sorted(ROUTES.keys())})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
        except (json.JSONDecodeError, ValueError):
            self._send(400, {"error": "Invalid JSON body"})
            return
        try:
            self._send(200, func(**body))
        except Exception as e:
            self._send(400, {"error": str(e)})

    def do_GET(self):
        method = urlparse(self.path).path.rstrip("/").split("/api/")[-1]
        if method and method != "api":
            self._send(200, {"endpoint": method, "available": sorted(ROUTES.keys())})
        else:
            self._send(
                200, {"status": "ok", "endpoints": sorted(ROUTES.keys()), "docs": "intangible-valuation.simonmak.com"}
            )

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send(self, code, data):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
