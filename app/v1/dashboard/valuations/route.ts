import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth/config";
import { getUserValuations } from "@/lib/valuation/store";

export async function GET(request: NextRequest) {
  const session = await auth();
  if (!session?.user?.email) {
    return NextResponse.json({ error: "UNAUTHORIZED", message: "Authentication required" }, { status: 401 });
  }
  const userId = (session.user as { id?: string }).id || session.user.email;

  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get("page") || "1", 10);
  const limit = Math.min(parseInt(searchParams.get("limit") || "20", 10), 100);
  const method = searchParams.get("method") || undefined;
  const category = searchParams.get("category") || undefined;
  const sort = searchParams.get("sort") || "created_at";
  const order = (searchParams.get("order") || "desc") as "asc" | "desc";

  try {
    const result = await getUserValuations(userId, {
      page,
      limit,
      method,
      category,
      sort,
      order,
    });

    return NextResponse.json({
      valuations: result.valuations,
      pagination: {
        page,
        limit,
        total: result.total,
        pages: Math.ceil(result.total / limit),
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: "INTERNAL_ERROR", message: error instanceof Error ? error.message : "Database error" },
      { status: 500 }
    );
  }
}
