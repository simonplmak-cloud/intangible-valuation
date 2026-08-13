import { NextRequest, NextResponse } from "next/server";

const MCP_TOOL_CATALOG = [
  { name: "present_value", description: "Calculate present value of a future cash flow (Ch 2, Sec 2.1)" },
  { name: "future_value", description: "Calculate future value of a present sum (Ch 2, Sec 2.1)" },
  { name: "annuity_pv", description: "Calculate present value of an annuity (Ch 2, Sec 2.2)" },
  { name: "perpetuity_pv", description: "Calculate present value of a perpetuity (Ch 2, Sec 2.2)" },
  { name: "growing_annuity_pv", description: "Calculate present value of a growing annuity (Ch 2, Sec 2.2)" },
  { name: "terminal_value", description: "Calculate terminal value via Gordon Growth or Exit Multiple (Ch 2, Sec 2.4)" },
  { name: "capm", description: "Capital Asset Pricing Model — determine cost of equity (Ch 2, Sec 2.3)" },
  { name: "wacc", description: "Weighted Average Cost of Capital (Ch 2, Sec 2.3)" },
  { name: "build_up_discount_rate", description: "Build-up method for discount rate (Ch 2, Sec 2.3)" },
  { name: "tax_amortization_benefit", description: "Calculate Tax Amortization Benefit (Ch 3, Sec 3.4)" },
  { name: "control_premium", description: "Calculate control premium (Ch 3, Sec 3.5)" },
  { name: "dlom_finnerty", description: "Discount for Lack of Marketability — Finnerty model (Ch 3, Sec 3.5)" },
  { name: "relief_from_royalty", description: "Relief from Royalty method with TAB (Ch 4, Sec 4.2)" },
  { name: "mpeem", description: "Multi-Period Excess Earnings Method (Ch 4, Sec 4.1)" },
  { name: "single_period_excess_earnings", description: "Single-period excess earnings (Ch 4, Sec 4.1)" },
  { name: "incremental_cashflow", description: "Incremental cash flow method (Ch 4, Sec 4.4)" },
  { name: "reproduction_cost", description: "Reproduction cost method (Ch 3, Sec 3.1)" },
  { name: "replacement_cost", description: "Replacement cost method (Ch 3, Sec 3.1)" },
  { name: "market_approach_comparables", description: "Market approach using comparable transactions (Ch 3, Sec 3.2)" },
  { name: "patent_valuation", description: "Patent valuation using multiple methods (Ch 5)" },
  { name: "trademark_valuation", description: "Trademark/brand valuation (Ch 6)" },
  { name: "copyright_valuation", description: "Copyright valuation (Ch 5)" },
  { name: "trade_secret_valuation", description: "Trade secret valuation (Ch 5)" },
  { name: "customer_relationship_valuation", description: "Customer relationship valuation (Ch 8)" },
  { name: "assembled_workforce_valuation", description: "Assembled workforce valuation (Ch 9)" },
  { name: "goodwill", description: "Goodwill calculation (Ch 10, ASC 805)" },
  { name: "purchase_price_allocation", description: "Purchase Price Allocation waterfall (Ch 10, ASC 805)" },
  { name: "goodwill_impairment_test", description: "Goodwill impairment test (Ch 11, ASC 350)" },
  { name: "intangible_impairment_test", description: "Intangible asset impairment test (Ch 11, IAS 36)" },
  { name: "patent_infringement_damages", description: "Patent infringement damages (Ch 15)" },
  { name: "monte_carlo_sensitivity", description: "Monte Carlo sensitivity analysis (Ch 17)" },
  { name: "decision_tree_valuation", description: "Decision tree valuation (Ch 17)" },
  { name: "sensitivity_tornado", description: "Sensitivity tornado chart generation (Ch 17)" },
  { name: "scenario_analysis", description: "Multi-scenario analysis (Ch 17)" },
  { name: "royalty_rate_benchmark", description: "Royalty rate benchmarking (Ch 6, Sec 6.3)" },
  { name: "profit_split_method", description: "Transfer pricing profit split (Ch 16, OECD TP)" },
];

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Handle MCP tools/list
    if (body.method === "tools/list") {
      return NextResponse.json({
        jsonrpc: "2.0",
        id: body.id,
        result: {
          tools: MCP_TOOL_CATALOG.map((t) => ({
            ...t,
            inputSchema: {
              type: "object",
              properties: {},
            },
          })),
        },
      });
    }

    // Handle MCP tools/call — forward to Vercel Python API
    if (body.method === "tools/call") {
      const toolName = body.params?.name;
      const args = body.params?.arguments || {};

      try {
        const pyResponse = await fetch(
          `${request.nextUrl.origin}/api/index.py`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-Valuation-Method": toolName },
            body: JSON.stringify({ method: toolName, ...args }),
          }
        );

        const data = await pyResponse.json();

        return NextResponse.json({
          jsonrpc: "2.0",
          id: body.id,
          result: {
            content: [{ type: "text", text: JSON.stringify(data) }],
          },
        });
      } catch (error) {
        return NextResponse.json({
          jsonrpc: "2.0",
          id: body.id,
          error: {
            code: -32603,
            message: error instanceof Error ? error.message : "Tool execution failed",
          },
        });
      }
    }

    return NextResponse.json({
      jsonrpc: "2.0",
      id: body.id,
      error: { code: -32601, message: `Method not found: ${body.method}` },
    });
  } catch {
    return NextResponse.json(
      { jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } },
      { status: 400 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
