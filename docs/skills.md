# AI-Agent Skills

The Intangible Valuation platform includes AI-Agent Skills that provide domain-specific instructions and workflows for valuation tasks.

## Overview

Skills are specialized instruction sets that guide AI agents through complex valuation workflows. Each skill contains:

- Domain-specific knowledge and best practices
- Step-by-step workflow guidance
- Method selection criteria
- Common pitfalls and how to avoid them
- Reference to relevant textbook chapters

## Available Skills

### Asset Valuation Skill

Guides AI agents through the complete valuation process for different intangible asset types:

- **Patents** — Relief from Royalty, incremental cash flow, litigation damages
- **Trademarks/Brands** — Relief from Royalty, royalty benchmarking, brand strength analysis
- **Technology/Software** — Replacement cost, multi-period excess earnings, useful life estimation
- **Customer Relationships** — Multi-period excess earnings, attrition analysis
- **Human Capital** — Cost approach, excess earnings, replacement cost

### Discount Rate Construction Skill

Walks through building appropriate discount rates:

1. Select method (build-up, CAPM, WACC) based on asset type and data availability
2. Gather risk-free rate, equity risk premium, size premium
3. Add industry-specific and company-specific risk premiums
4. Apply adjustments (DLOM, control premium, currency risk)

### Purchase Price Allocation Skill

Step-by-step PPA workflow:

1. Determine total purchase consideration
2. Identify and value tangible assets at fair value
3. Identify intangible assets and select valuation methods
4. Value each identified intangible
5. Calculate assumed liabilities
6. Compute goodwill as residual
7. Validate allocation percentages

### Monte Carlo Analysis Skill

Guide for uncertainty analysis:

1. Identify uncertain input parameters
2. Select appropriate probability distributions
3. Configure iteration count and random seed
4. Run simulation and interpret results
5. Perform sensitivity analysis on key drivers

### Decision Tree Skill

For valuing assets with contingent outcomes:

1. Map decision points and chance events
2. Assign probabilities and values to each branch
3. Apply backward induction
4. Identify optimal decision path
5. Calculate expected value

## Using Skills

Skills are located in the `skills/` directory. Each skill is a markdown file with:

- **Trigger conditions** — When to use this skill
- **Workflow steps** — Ordered steps to follow
- **Method selection** — Decision trees for choosing valuation methods
- **Validation checks** — Sanity checks on results
- **References** — Textbook chapter and section references

## Integration with MCP Server

Skills complement the MCP server tools:

1. The skill provides the workflow and decision logic
2. The MCP tools execute the calculations
3. The skill interprets results and guides next steps

Example workflow:

```
User: "Value a pharmaceutical patent with 12 years remaining"

Skill triggers: Asset Valuation -> Patent
  1. Determine useful life (min of legal and economic)
  2. Select valuation method (Relief from Royalty recommended)
  3. Call MCP tool: royalty_rate_benchmark("patent", "pharmaceutical")
  4. Call MCP tool: relief_from_royalty(...)
  5. Validate result against benchmark range
  6. Present final valuation with confidence range
```

## Custom Skills

To create a custom skill:

1. Create a new markdown file in `skills/`
2. Define trigger conditions
3. Write workflow steps with MCP tool calls
4. Include validation checks and references
5. Test with sample valuations

## Skill Best Practices

- Always validate inputs before calling valuation tools
- Use benchmark data to sanity-check results
- Document all assumptions made during the valuation
- Provide sensitivity analysis for key inputs
- Cite the relevant textbook chapter for each method used
