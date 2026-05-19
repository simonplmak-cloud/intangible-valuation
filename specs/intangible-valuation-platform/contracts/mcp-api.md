# API Contract: MCP Server

## MCP Server API

The MCP server exposes all valuation functions as tools. Each tool follows the MCP tool specification.

### Server Configuration

**Server Name:** `intangible-valuation`
**Protocol:** stdio (default), sse (optional)
**Binding:** localhost only (default)

### Tool Discovery

**Request:** `tools/list`
**Response:** List of all available valuation tools with name, description, and input schema.

```json
{
  "tools": [
    {
      "name": "present_value",
      "description": "Calculate present value of a future cash flow. Formula: PV = FV / (1 + r)^n. Reference: Ch 2.1",
      "inputSchema": {
        "type": "object",
        "properties": {
          "future_value": {"type": "number", "minimum": 0, "description": "Future cash flow amount"},
          "discount_rate": {"type": "number", "minimum": 0, "maximum": 1, "description": "Discount rate as decimal"},
          "periods": {"type": "integer", "minimum": 1, "description": "Number of periods"}
        },
        "required": ["future_value", "discount_rate", "periods"]
      }
    }
  ]
}
```

### Tool Execution

**Request:** `tools/call` with `{name: "present_value", arguments: {future_value: 100000, discount_rate: 0.12, periods: 5}}`

**Response (200 OK):**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"value\": 56742.69, \"method\": \"Present Value\", \"formula_reference\": \"Ch 2.1, Appendix A.1\", \"steps\": [...]}"
    }
  ],
  "isError": false
}
```

**Error Response (400):**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"error\": \"VALIDATION_ERROR\", \"message\": \"discount_rate must be greater than 0\", \"details\": {\"field\": \"discount_rate\", \"constraint\": \"gt(0)\"}}"
    }
  ],
  "isError": true
}
```

### Available Tool Categories

| Category | Tool Count | Description |
|----------|-----------|-------------|
| Core Math | 12 | Time value, discount rates, terminal value, TAB |
| Approaches | 4 | Cost approach, market approach methods |
| Income Methods | 5 | RFR, MPEEM, SPEEM, incremental cash flow, CAC |
| Asset Types | 13 | IP, brand, technology, customer, human capital |
| Advanced | 10 | Goodwill, PPA, impairment, royalty, transfer pricing, litigation |
| Analysis | 3 | Monte Carlo, decision tree, sensitivity analysis |

### AC Coverage
- AC-45: Tool discovery (tools/list)
- AC-46: Tool execution (tools/call)
- AC-E4: Error response formatting
