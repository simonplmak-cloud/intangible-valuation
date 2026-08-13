import { getToken } from "next-auth/jwt";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const publicPaths = [
  "/",
  "/about",
  "/calculator",
  "/docs",
  "/mcp",
  "/skills",
  "/pricing",
  "/terms",
  "/privacy",
  "/sign-in",
  "/sign-up",
  "/v1/valuation",
  "/v1/mcp",
  "/v1/benchmarks",
  "/v1/billing/webhook",
  "/v1/auth",
  "/favicon.ico",
];

function isPublic(pathname: string): boolean {
  return publicPaths.some((p) => pathname === p || pathname.startsWith(p + "/"));
}

function isAdminPath(pathname: string): boolean {
  return pathname.startsWith("/admin");
}

function isDashboardPath(pathname: string): boolean {
  return pathname.startsWith("/dashboard");
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths, static assets
  if (isPublic(pathname) || pathname.startsWith("/_next") || pathname.includes(".")) {
    return NextResponse.next();
  }

  const token = await getToken({
    req: request,
    secret: process.env.NEXTAUTH_SECRET,
  });

  // Admin routes require admin role
  if (isAdminPath(pathname)) {
    if (!token) {
      return NextResponse.redirect(new URL(`/sign-in?callbackUrl=${encodeURIComponent(pathname)}`, request.url));
    }
    if (token.role !== "admin") {
      return NextResponse.redirect(new URL("/", request.url));
    }
    return NextResponse.next();
  }

  // Dashboard routes require any auth
  if (isDashboardPath(pathname)) {
    if (!token) {
      return NextResponse.redirect(new URL(`/sign-in?callbackUrl=${encodeURIComponent(pathname)}`, request.url));
    }
    return NextResponse.next();
  }

  // All other routes require auth
  if (!token) {
    return NextResponse.redirect(new URL(`/sign-in?callbackUrl=${encodeURIComponent(pathname)}`, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
