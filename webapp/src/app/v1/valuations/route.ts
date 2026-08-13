import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth/config";
import { saveValuation } from "@/lib/valuation/store";
import { canSaveValuation } from "@/lib/billing/gate";

export async function POST(request: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.email) {
    return NextResponse.json({ error: "UNAUTHORIZED", message: "Authentication required" }, { status: 401 });
  }
  const userId = (session.user as { id?: string }).id ?? session.user.email;

  // Tier gating (AC-GATE-01): block the paid action when the free quota is
  // exceeded, but never block the core calculation itself.
  const allowed = await canSaveValuation(userId);
  if (!allowed) {
    return NextResponse.json(
      {
        error: "QUOTA_EXCEEDED",
        message: "Free tier limit reached — upgrade to save more valuations.",
      },
      { status: 402 }
    );
  }

  const body = await request.json().catch(() => ({}));

  try {
    const { id } = await saveValuation({
      userId,
      method: body.method ?? "unknown",
      category: body.category ?? "core",
      assetType: body.assetType,
      businessStage: body.businessStage,
      inputs: body.inputs ?? {},
      result: body.result ?? { value: 0, method: "unknown", formula_reference: "", steps: [], assumptions: [] },
    });

    return NextResponse.json({ id });
  } catch (error) {
    return NextResponse.json(
      { error: "INTERNAL_ERROR", message: error instanceof Error ? error.message : "Failed to save valuation" },
      { status: 500 }
    );
  }
}
