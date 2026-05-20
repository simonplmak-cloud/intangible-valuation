# AGENTS.md — Intangible Asset Valuation

## Commands

```bash
pip install -e ".[dev]"         # install with dev deps (pytest, ruff, coverage, mypy)
pytest                           # run all 698 tests
pytest --cov=src                 # with coverage
ruff check .                     # lint
mypy src/                        # type check
```

CI runs `mypy` + `pytest --cov=src --cov-report=term-missing -v` on Python 3.11/3.12. Docs build with `mkdocs build`.

## Architecture

- `src/` — 22 modules, 124+ functions. All return `ValuationResult` (never bare numbers).
- `src/core/` — Time value of money, discount rates, statistics (Ch 2)
- `src/approaches/` — Cost and market approaches (Ch 3)
- `src/income_methods/` — Relief from Royalty, MPEEM, incremental cash flow (Ch 4)
- `src/asset_types/` — IP, brand, technology, customer, human capital (Ch 5–9)
- `src/advanced/` — Goodwill, PPA, impairment, litigation, Monte Carlo, decision trees (Ch 10–18)
- `src/utils/` — Constants, formulas, sensitivity analysis
- `mcp_server/server.py` — FastMCP server with 54 tools. Run: `cd mcp_server && python server.py`. Requires `pip install -e ".[mcp]"`.
- `skills/` — 3 AI-Agent SKILL.md files (asset-valuation, discount-rate-construction, purchase-price-allocation).
- `docs/` — MkDocs Material site (API reference, examples, chapter index). Deployed to GitHub Pages.
- `specs/` — SDD artifacts for valuation projects.

## Key Conventions

- Every library function returns `ValuationResult` with `value`, `method`, `inputs`, `assumptions`, and step-by-step calculation breakdowns.
- MCP tools unwrap `ValuationResult` to plain dicts (`{"value": ..., "method": ...}`) for agent consumption.
- Tests validate against textbook example values — do not change expected values without verifying against the source book.
- `numpy` used for Monte Carlo simulations and numerical calculations.
- `pydantic` used for input validation in MCP tools.
- Per-module test files: one `test_*.py` per module in `tests/`.

## Gotchas

- `src/` layout: must use `pip install -e` or set `PYTHONPATH=src` for imports to resolve.
- `fastmcp` is an optional dependency (`.[mcp]`) — not installed by default with `.[dev]`.
- Test tolerances use `pytest.approx(abs=N)` — textbook values have rounding variance.
- MkDocs uses `mkdocstrings` for auto-generated API docs — docstrings must be Google-style.
- Package name on PyPI is `intangible-valuation` (with hyphen), import is `intangible_valuation` (with underscore).
