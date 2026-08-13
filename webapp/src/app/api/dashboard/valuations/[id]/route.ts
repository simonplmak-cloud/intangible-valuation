import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth/config";
import { getValuationById, deleteValuation, toggleFavorite } from "@/lib/valuation/store";
import { logAuditTrail } from "@/lib/valuation/audit";

async function getUserId(): Promise<string | null> {
  const session = await getServerSession(authOptions);
  if (!session?.user?.email) return null;
  return (session.user as { id?: string }).id || session.user.email;
}

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  const userId = await getUserId();
  if (!userId) {
    return NextResponse.json({ error: "UNAUTHORIZED", message: "Authentication required" }, { status: 401 });
  }

  try {
    const valuation = await getValuationById(`valuations:${params.id}`);
    if (!valuation) {
      return NextResponse.json({ error: "NOT_FOUND", message: "Valuation not found" }, { status: 404 });
    }
    return NextResponse.json(valuation);
  } catch (error) {
    return NextResponse.json(
      { error: "INTERNAL_ERROR", message: error instanceof Error ? error.message : "Database error" },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const userId = await getUserId();
  if (!userId) {
    return NextResponse.json({ error: "UNAUTHORIZED" }, { status: 401 });
  }

  try {
    await deleteValuation(`valuations:${params.id}`);
    await logAuditTrail({ userId, valuationId: params.id, action: "deleted" });
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json(
      { error: "INTERNAL_ERROR", message: error instanceof Error ? error.message : "Database error" },
      { status: 500 }
    );
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const userId = await getUserId();
  if (!userId) {
    return NextResponse.json({ error: "UNAUTHORIZED" }, { status: 401 });
  }

  try {
    const body = await request.json();
    if (body.action === "toggle_favorite") {
      const valuation = await getValuationById(`valuations:${params.id}`);
      if (!valuation) {
        return NextResponse.json({ error: "NOT_FOUND" }, { status: 404 });
      }
      await toggleFavorite(`valuations:${params.id}`, (valuation as { is_favorite?: boolean }).is_favorite ?? false);
      return NextResponse.json({ success: true });
    }
    return NextResponse.json({ error: "Invalid action" }, { status: 400 });
  } catch (error) {
    return NextResponse.json(
      { error: "INTERNAL_ERROR", message: error instanceof Error ? error.message : "Database error" },
      { status: 500 }
    );
  }
}
