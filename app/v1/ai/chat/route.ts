import { NextRequest, NextResponse } from "next/server";
import { advisorChat } from "@/lib/ai/client";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));
  const history = Array.isArray(body.history) ? body.history.slice(-20) : [];

  const reply = await advisorChat(history);
  if (reply === null) {
    return NextResponse.json(
      { error: "AI_ADVISOR_UNAVAILABLE", message: "The AI advisor is not configured." },
      { status: 503 }
    );
  }

  return NextResponse.json({ reply });
}
