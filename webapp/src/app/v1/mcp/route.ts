import { NextRequest, NextResponse } from "next/server";
import { CATALOG } from "@/lib/valuation/catalog";

// Single source of truth: derive the MCP tool catalog from the canonical
// method catalog instead of hand-copying tool names/descriptions.
const MCP_TOOL_CATALOG = CATALOG.map((m) => ({
  name: m.mcpTool,
  description: `${m.name} — ${m.description} (${m.textbookReference})`,
}));

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
