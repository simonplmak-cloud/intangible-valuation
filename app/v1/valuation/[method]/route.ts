import { NextRequest, NextResponse } from "next/server";
import { getMethodCitations } from "@/lib/valuation/citations";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ method: string }> }
) {
  const { method } = await params;

  try {
    const body = await request.json();

    const response = await fetch(
      `${request.nextUrl.origin}/api/index.py`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Valuation-Method": method,
        },
        body: JSON.stringify({ method, ...body }),
      }
    );

    if (!response.ok) {
      const errorData = await response.text();
      let parsedError: Record<string, unknown>;
      try {
        parsedError = JSON.parse(errorData);
      } catch {
        parsedError = { error: "CALCULATION_ERROR", message: errorData };
      }
      return NextResponse.json(parsedError, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json({ ...data, citations: getMethodCitations(method) });
  } catch (error) {
    return NextResponse.json(
      {
        error: "INTERNAL_ERROR",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ method: string }> }
) {
  const { method } = await params;
  return NextResponse.json({
    endpoint: method,
    description: `POST /api/valuation/${method} — Execute the ${method} valuation method`,
    usage: {
      method: "POST",
      contentType: "application/json",
      body: "Method-specific parameters (see documentation)",
    },
  });
}
