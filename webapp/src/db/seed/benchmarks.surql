-- ============================================================================
-- V001: Seed — Stage-Aware Benchmarks
-- Sources: Damodaran 2025, RoyaltySource 2024, ktMINE, Ascent Partners
-- ============================================================================

-- Discount Rates by Stage
INSERT INTO benchmarks [
  { category: "discount_rate", business_stage: "startup", asset_type: "all", industry: "all", metric_name: "median_wacc", value: 0.25, unit: "percentage", p25: 0.18, p75: 0.35, source: "Damodaran 2025" },
  { category: "discount_rate", business_stage: "startup", asset_type: "all", industry: "technology", metric_name: "median_wacc", value: 0.22, unit: "percentage", p25: 0.15, p75: 0.30, source: "Damodaran 2025" },
  { category: "discount_rate", business_stage: "startup", asset_type: "all", industry: "pharma", metric_name: "median_wacc", value: 0.20, unit: "percentage", p25: 0.14, p75: 0.28, source: "Damodaran 2025" },
  { category: "discount_rate", business_stage: "startup", asset_type: "all", industry: "saas", metric_name: "median_wacc", value: 0.18, unit: "percentage", p25: 0.12, p75: 0.25, source: "Damodaran 2025" },

  { category: "discount_rate", business_stage: "growth", asset_type: "all", industry: "all", metric_name: "median_wacc", value: 0.15, unit: "percentage", p25: 0.10, p75: 0.20, source: "Damodaran 2025" },
  { category: "discount_rate", business_stage: "growth", asset_type: "all", industry: "technology", metric_name: "median_wacc", value: 0.13, unit: "percentage", p25: 0.09, p75: 0.18, source: "Damodaran 2025" },
  { category: "discount_rate", business_stage: "growth", asset_type: "all", industry: "saas", metric_name: "median_wacc", value: 0.12, unit: "percentage", p25: 0.08, p75: 0.16, source: "Damodaran 2025" },

  { category: "discount_rate", business_stage: "mature", asset_type: "all", industry: "all", metric_name: "median_wacc", value: 0.08, unit: "percentage", p25: 0.06, p75: 0.12, source: "Damodaran 2025" },
  { category: "discount_rate", business_stage: "mature", asset_type: "all", industry: "technology", metric_name: "median_wacc", value: 0.09, unit: "percentage", p25: 0.07, p75: 0.11, source: "Damodaran 2025" },

  -- Royalty Rates by Asset Type and Stage
  { category: "royalty_rate", business_stage: "startup", asset_type: "patent", industry: "all", metric_name: "median_royalty_rate", value: 0.06, unit: "percentage", p25: 0.03, p75: 0.10, source: "RoyaltySource 2024" },
  { category: "royalty_rate", business_stage: "growth", asset_type: "patent", industry: "all", metric_name: "median_royalty_rate", value: 0.05, unit: "percentage", p25: 0.02, p75: 0.08, source: "RoyaltySource 2024" },
  { category: "royalty_rate", business_stage: "mature", asset_type: "patent", industry: "all", metric_name: "median_royalty_rate", value: 0.04, unit: "percentage", p25: 0.02, p75: 0.07, source: "RoyaltySource 2024" },

  { category: "royalty_rate", business_stage: "startup", asset_type: "brand", industry: "all", metric_name: "median_royalty_rate", value: 0.05, unit: "percentage", p25: 0.02, p75: 0.10, source: "ktMINE 2024" },
  { category: "royalty_rate", business_stage: "growth", asset_type: "brand", industry: "all", metric_name: "median_royalty_rate", value: 0.04, unit: "percentage", p25: 0.02, p75: 0.08, source: "ktMINE 2024" },
  { category: "royalty_rate", business_stage: "mature", asset_type: "brand", industry: "all", metric_name: "median_royalty_rate", value: 0.03, unit: "percentage", p25: 0.01, p75: 0.06, source: "ktMINE 2024" },

  { category: "royalty_rate", business_stage: "all", asset_type: "technology", industry: "all", metric_name: "median_royalty_rate", value: 0.05, unit: "percentage", p25: 0.03, p75: 0.08, source: "RoyaltySource 2024" },
  { category: "royalty_rate", business_stage: "all", asset_type: "software", industry: "all", metric_name: "median_royalty_rate", value: 0.06, unit: "percentage", p25: 0.04, p75: 0.10, source: "RoyaltySource 2024" },

  -- Useful Life by Asset Type
  { category: "useful_life", business_stage: "startup", asset_type: "patent", industry: "all", metric_name: "median_useful_life", value: 7.0, unit: "years", p25: 3.0, p75: 12.0, source: "Ascent Partners 2025" },
  { category: "useful_life", business_stage: "growth", asset_type: "patent", industry: "all", metric_name: "median_useful_life", value: 10.0, unit: "years", p25: 5.0, p75: 15.0, source: "Ascent Partners 2025" },
  { category: "useful_life", business_stage: "mature", asset_type: "patent", industry: "all", metric_name: "median_useful_life", value: 12.0, unit: "years", p25: 7.0, p75: 17.0, source: "Ascent Partners 2025" },

  { category: "useful_life", business_stage: "all", asset_type: "brand", industry: "all", metric_name: "median_useful_life", value: 15.0, unit: "years", p25: 5.0, p75: 25.0, source: "Ascent Partners 2025" },
  { category: "useful_life", business_stage: "all", asset_type: "technology", industry: "all", metric_name: "median_useful_life", value: 5.0, unit: "years", p25: 2.0, p75: 8.0, source: "Ascent Partners 2025" },
  { category: "useful_life", business_stage: "all", asset_type: "customer", industry: "all", metric_name: "median_useful_life", value: 8.0, unit: "years", p25: 3.0, p75: 15.0, source: "Ascent Partners 2025" },
  { category: "useful_life", business_stage: "all", asset_type: "workforce", industry: "all", metric_name: "median_useful_life", value: 3.0, unit: "years", p25: 1.0, p75: 7.0, source: "Ascent Partners 2025" },
  { category: "useful_life", business_stage: "all", asset_type: "software", industry: "all", metric_name: "median_useful_life", value: 5.0, unit: "years", p25: 2.0, p75: 8.0, source: "Ascent Partners 2025" },

  -- Growth Rates by Stage
  { category: "growth_rate", business_stage: "startup", asset_type: "all", industry: "technology", metric_name: "median_revenue_growth", value: 0.50, unit: "percentage", p25: 0.20, p75: 1.00, source: "Damodaran 2025" },
  { category: "growth_rate", business_stage: "growth", asset_type: "all", industry: "technology", metric_name: "median_revenue_growth", value: 0.20, unit: "percentage", p25: 0.10, p75: 0.40, source: "Damodaran 2025" },
  { category: "growth_rate", business_stage: "mature", asset_type: "all", industry: "technology", metric_name: "median_revenue_growth", value: 0.05, unit: "percentage", p25: 0.02, p75: 0.10, source: "Damodaran 2025" },
  { category: "growth_rate", business_stage: "mature", asset_type: "all", industry: "all", metric_name: "perpetual_growth_rate", value: 0.03, unit: "percentage", p25: 0.02, p75: 0.04, source: "Damodaran 2025" },
];

-- Skills Catalog
INSERT INTO skills_catalog [
  { slug: "asset-valuation", name: "Asset Valuation", description: "Comprehensive valuation workflow for any intangible asset type using all available methods.", category: "valuation", markdown_path: "skills/asset-valuation/SKILL.md", mcp_tools_required: ["relief_from_royalty","mpeem","cost_approach","market_approach"] },
  { slug: "discount-rate-construction", name: "Discount Rate Construction", description: "Build appropriate discount rates using CAPM, WACC, build-up method, and DLOM.", category: "valuation", markdown_path: "skills/discount-rate-construction/SKILL.md", mcp_tools_required: ["capm","wacc","build_up_discount_rate","dlom_finnerty"] },
  { slug: "purchase-price-allocation", name: "Purchase Price Allocation", description: "Complete PPA workflow following ASC 805/IFRS 3 with full waterfall calculation.", category: "workflow", markdown_path: "skills/purchase-price-allocation/SKILL.md", mcp_tools_required: ["purchase_price_allocation","goodwill","valuation_multiple_methods"] },
  { slug: "impairment-testing", name: "Impairment Testing", description: "Goodwill and intangible asset impairment testing compliant with ASC 350/IAS 36.", category: "compliance", markdown_path: "skills/impairment-testing/SKILL.md", mcp_tools_required: ["goodwill_impairment_test","intangible_impairment_test","value_in_use"] },
];
