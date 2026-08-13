import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/react";
import { AppShell } from "@/components/layout/AppShell";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: {
    default: "Intangible Asset Valuation — The Authority",
    template: "%s | Intangible Valuation",
  },
  description:
    "The most authoritative, traceable, and auditable source of intangible asset valuation. 68 methods, 1,000+ textbook-verified tests, MCP gateway, and AI-agent ready.",
  keywords: [
    "intangible asset valuation",
    "patent valuation",
    "brand valuation",
    "goodwill calculation",
    "purchase price allocation",
    "relief from royalty",
    "MPEEM",
    "discount rate",
    "WACC",
    "CAPM",
    "MCP server",
    "AI valuation",
  ],
  authors: [{ name: "Ascent Partners" }],
  openGraph: {
    title: "Intangible Asset Valuation — The Authority",
    description: "The most authoritative, traceable, and auditable source of intangible asset valuation.",
    type: "website",
    siteName: "Intangible Valuation",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen flex flex-col">
        <AppShell>{children}</AppShell>
        <Analytics />
      </body>
    </html>
  );
}
