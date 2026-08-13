import type { MetadataRoute } from "next";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://intangible-valuation.simonmak.com";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: ["/dashboard", "/admin", "/sign-in", "/sign-up", "/api/"] },
    sitemap: `${BASE_URL}/sitemap.xml`,
  };
}
