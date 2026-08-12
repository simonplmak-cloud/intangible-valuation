"""Vercel serverless API — routes /api/present-value, /api/capm, etc."""

import json, os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from intangible_valuation.core.time_value import present_value, future_value, annuity_pv, perpetuity_pv, terminal_value
from intangible_valuation.core.discount_rates import build_up_discount_rate, capm_discount_rate, wacc
from intangible_valuation.income_methods.relief_from_royalty import relief_from_royalty

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
    def _get_method(self):
        path = urlparse(self.path).path
        return path.rstrip("/").split("/api/")[-1] if "/api/" in path else ""

    def do_POST(self):
        method = self._get_method()
        func = ROUTES.get(method)
        if not func:
            self._respond(404, {"error": f"Unknown: {method}", "available": list(ROUTES.keys())})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
        except json.JSONDecodeError:
            self._respond(400, {"error": "Invalid JSON"})
            return
        try:
            result = func(**body)
            data = result.model_dump() if hasattr(result, "model_dump") else result
            self._respond(200, data)
        except Exception as e:
            self._respond(400, {"error": str(e)})

    def do_GET(self):
        method = self._get_method()
        if method:
            self._respond(200, {"endpoint": method, "available": list(ROUTES.keys())})
        else:
            self._respond(200, {"status": "ok", "endpoints": list(ROUTES.keys())})

    def _respond(self, code, data):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
