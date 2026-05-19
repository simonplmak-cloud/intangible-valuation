# MCP Server

The Intangible Valuation MCP (Model Context Protocol) server exposes all valuation methods as tools for AI agents.

## Overview

The MCP server provides AI agents with access to:

- Time value of money calculations
- Discount rate construction (build-up, CAPM, WACC)
- Relief from Royalty valuations
- Purchase Price Allocation
- Monte Carlo simulation
- Decision tree analysis
- Goodwill calculation
- Royalty benchmarking

## Setup

### Installation

```bash
pip install intangible-valuation[mcp]
```

### Configuration

Add the MCP server to your AI agent configuration:

```json
{
  "mcpServers": {
    "intangible-valuation": {
      "command": "intangible-valuation-mcp",
      "args": []
    }
  }
}
```

### Running Standalone

```bash
intangible-valuation-mcp
```

## Available Tools

### Time Value of Money

| Tool | Description |
|------|-------------|
| `present_value` | Calculate PV of a single future cash flow |
| `future_value` | Calculate FV of a present amount |
| `annuity_pv` | Calculate PV of an ordinary annuity |
| `perpetuity_pv` | Calculate PV of a perpetuity |
| `growing_annuity_pv` | Calculate PV of a growing annuity |
| `terminal_value` | Calculate terminal value (Gordon Growth or Exit Multiple) |

### Discount Rates

| Tool | Description |
|------|-------------|
| `build_up_discount_rate` | Build-up method with risk premiums |
| `capm_discount_rate` | CAPM cost of equity |
| `wacc` | Weighted Average Cost of Capital |
| `dlom_finnerty` | Finnerty model for lack of marketability |
| `control_premium` | Control premium calculation |
| `tax_amortization_benefit` | TAB present value |

### Valuation Methods

| Tool | Description |
|------|-------------|
| `relief_from_royalty` | Relief from Royalty method with TAB |
| `reproduction_cost` | Depreciated reproduction cost |
| `replacement_cost` | Depreciated replacement cost |
| `purchase_price_allocation` | Full PPA waterfall |
| `goodwill` | Goodwill as residual |
| `monte_carlo_valuation` | Monte Carlo simulation |
| `decision_tree_valuation` | Decision tree analysis |

## Example Usage

An AI agent can call the tools like this:

```
Tool: relief_from_royalty
Arguments:
  revenue_projections: [1000000, 1100000, 1200000, 1300000, 1400000]
  royalty_rate: 0.05
  discount_rate: 0.12
  tax_rate: 0.25
  useful_life: 5

Result:
  value: 387654.32
  method: Relief from Royalty
  tab_factor: 1.23
```

## Architecture

The MCP server is built with FastMCP and exposes all valuation functions as tools with:

- Full parameter validation via Pydantic
- Rich descriptions for each tool
- Structured JSON responses with calculation steps
- Error handling with detailed messages

## Development

```bash
# Run the server in development mode
python -m mcp_server.server

# Test MCP tools
python -c "from mcp_server import tools; print(tools.list_tools())"
```
