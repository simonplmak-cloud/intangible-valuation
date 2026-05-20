# Intangible Asset Valuation Platform

Status: Approved
Version: 2.0
Last updated: 2026-05-20

## Overview

A Python library, MCP server, and AI-Agent Skills that implements every calculation methodology,
formula, and framework from "Intangible Asset Valuation" (Ascent Partners, 2025, 19 chapters + 3 appendices).
The platform provides programmatic, testable, and AI-accessible valuation calculations for
all intangible asset types covered in the book, plus advanced methods from professional practice.

## User Stories

### Primary
As a valuation analyst, I want to execute any valuation method from the textbook programmatically
so that I can produce auditable, reproducible results without manual spreadsheet errors.

### Secondary
As an AI agent, I want to call valuation tools via MCP protocol so that I can assist users
with intangible asset valuation questions using verified calculation engines.

As a student, I want to verify textbook exercise solutions programmatically so that I can
check my understanding of each valuation method.

## Boundaries

**Always do:**
- Validate all inputs with Pydantic schemas before calculations
- Return structured results with all intermediate calculation steps
- Include formula references (chapter/section) in all outputs
- Raise descriptive errors for invalid inputs (never silent failures)
- Support both point estimates and sensitivity analysis ranges

**Ask first (do not proceed unilaterally):**
- Adding new valuation methods not covered in the book
- Changing existing formula implementations
- Adding external data sources or API dependencies

**Never do:**
- Store or log user financial data
- Use hardcoded financial constants (all rates are parameters)
- Perform network calls from the calculation library
- Round intermediate calculations (only round final output)

## Acceptance Criteria

### Core Math Foundation (Chapter 2, Appendix A)

### AC-1: Time Value of Money Calculations [MUST]
Given future cash flows, discount rate, and number of periods
When the user calls present_value(), future_value(), annuity_pv(), perpetuity_pv(), or growing_annuity_pv()
Then the function returns the mathematically correct result matching textbook formulas (Section 2.1, A.1)

### AC-2: Discount Rate Construction [MUST]
Given risk-free rate, equity risk premium, size premium, industry risk premium, and specific risk premium
When the user calls build_up_discount_rate()
Then the function returns the sum of all components with each component documented in the result

### AC-3: CAPM Discount Rate [MUST]
Given risk-free rate, asset beta, and market return
When the user calls capm_discount_rate()
Then the function returns: risk_free + beta * (market_return - risk_free)

### AC-4: WACC Calculation [MUST]
Given equity value, debt value, cost of equity, cost of debt, and tax rate
When the user calls wacc()
Then the function returns the weighted average cost of capital with correct tax shield on debt

### AC-5: Tax Amortization Benefit (TAB) [MUST]
Given discount rate, useful life, and tax rate
When the user calls tax_amortization_benefit()
Then the function calculates the present value of tax deductions from amortizing the intangible asset (Appendix A.7)

### AC-6: Monte Carlo Simulation [MUST]
Given input distributions (mean, std, type) and number of iterations
When the user calls monte_carlo_valuation()
Then the function returns a distribution of valuation outcomes with mean, median, std, and confidence intervals (Section 2.4)

### AC-7: Decision Tree Analysis [MUST]
Given a tree structure with probabilities, costs, and payoffs at each node
When the user calls decision_tree_valuation()
Then the function returns the expected value at each decision node with optimal path identification

### Core Valuation Approaches (Chapter 3)

### AC-8: Reproduction Cost Method [MUST]
Given development costs (labor, materials, overhead) and obsolescence factors
When the user calls reproduction_cost()
Then the function returns the total reproduction cost adjusted for obsolescence (Section 3.1, A.4)

### AC-9: Replacement Cost Method [MUST]
Given current cost to create equivalent functionality and obsolescence factors
When the user calls replacement_cost()
Then the function returns the depreciated replacement cost (Section 3.1)

### AC-10: Market Approach - Comparable Transactions [MUST]
Given comparable transaction data (sale prices, revenue multiples, asset characteristics)
When the user calls market_approach_comparables()
Then the function returns a valuation range based on comparable multiples with adjustment factors (Section 3.2, A.3)

### AC-11: Market Approach - Royalty Capitalization [MUST]
Given revenue, royalty rate, and discount rate
When the user calls royalty_capitalization()
Then the function returns: (revenue * royalty_rate) / discount_rate (Section 3.2)

### Advanced Income Methods (Chapter 4)

### AC-12: Relief-from-Royalty Method [MUST]
Given projected revenue stream, royalty rate, discount rate, useful life, and tax rate
When the user calls relief_from_royalty()
Then the function returns the present value of after-tax royalty savings over the asset's useful life, including TAB (Section 4.1)

### AC-13: Multi-Period Excess Earnings Method (MPEEM) [MUST]
Given projected cash flows, contributory asset charges (for working capital, fixed assets, other intangibles), discount rate, and tax rate
When the user calls mpeem()
Then the function returns the present value of excess earnings after deducting charges on all contributory assets (Section 4.2, A.11)

### AC-14: Single-Period Excess Earnings Method [MUST]
Given normalized earnings, contributory asset charges, and capitalization rate
When the user calls single_period_excess_earnings()
Then the function returns: (normalized_earnings - total_cac) / capitalization_rate

### AC-15: Incremental Cash Flow Method [MUST]
Given cash flows with and without the intangible asset, discount rate, and projection period
When the user calls incremental_cashflow()
Then the function returns the present value of the difference between the two cash flow streams (Section 4.3)

### Intellectual Property Valuation (Chapter 5)

### AC-16: Patent Valuation [MUST]
Given patent remaining life, projected cash flows, probability of success, discount rate, and comparable license rates
When the user calls patent_valuation()
Then the function returns a risk-adjusted patent value with probability-weighted scenarios (Section 5.1)

### AC-17: Trademark/Brand Valuation [MUST]
Given brand revenue, brand-specific profit margin, brand strength index, discount rate, and useful life
When the user calls brand_valuation()
Then the function returns the brand value using the relief-from-royalty or excess earnings approach (Section 5.2)

### AC-18: Copyright Valuation [MUST]
Given projected revenue from copyrighted work, useful life, discount rate, and royalty rate
When the user calls copyright_valuation()
Then the function returns the present value of expected royalty or licensing income (Section 5.3)

### AC-19: Trade Secret Valuation [MUST]
Given cost to develop, economic life, competitive advantage period, discount rate, and probability of maintaining secrecy
When the user calls trade_secret_valuation()
Then the function returns a value incorporating secrecy risk and competitive advantage period (Section 5.4)

### Royalty Rate Analysis (Chapter 6)

### AC-20: Royalty Rate Benchmarking [MUST]
Given IP type, industry, and comparable royalty rate database
When the user calls royalty_rate_benchmark()
Then the function returns a recommended royalty rate range with comparable transactions and adjustment factors (Section 6.2)

### AC-21: Royalty Rate Adjustment [MUST]
Given base royalty rate and adjustment factors (profit margin, exclusivity, market conditions, etc.)
When the user calls adjust_royalty_rate()
Then the function returns the adjusted royalty rate with each factor's impact documented (Section 6.3, A.10)

### AC-22: 25% Rule Calculation [SHOULD]
Given licensee's expected profit from the licensed IP
When the user calls twenty_five_percent_rule()
Then the function returns the implied royalty rate as 25% of expected profit margin (Section 6.1)

### Technology and Software Valuation (Chapter 7)

### AC-23: Developed Technology Valuation [MUST]
Given R&D costs, technology life cycle stage, competitive advantage, discount rate, and projected cash flows
When the user calls developed_technology_valuation()
Then the function returns the technology value using appropriate income or cost approach (Section 7.1)

### AC-24: Software Valuation [MUST]
Given development cost, maintenance cost, user base, revenue model, useful life, and discount rate
When the user calls software_valuation()
Then the function returns the software value considering both cost and income approaches (Section 7.2)

### AC-25: Data Asset Valuation [MUST]
Given data acquisition cost, data quality score, revenue contribution, useful life, and discount rate
When the user calls data_asset_valuation()
Then the function returns the data asset value with quality and utility adjustments (Section 7.3)

### AC-26: Platform/Network Asset Valuation [MUST]
Given network size, network effects coefficient, revenue per user, growth rate, and discount rate
When the user calls platform_valuation()
Then the function returns the platform value incorporating network effects (Section 7.4)

### Customer and Market-Related Intangibles (Chapter 8)

### AC-27: Customer Relationship Valuation [MUST]
Given customer count, average revenue per customer, retention rate, profit margin, discount rate, and attrition rate
When the user calls customer_relationship_valuation()
Then the function returns the present value of expected future customer cash flows (Section 8.1)

### AC-28: Distribution Network Valuation [MUST]
Given number of distribution channels, revenue per channel, channel margin, useful life, and discount rate
When the user calls distribution_network_valuation()
Then the function returns the present value of distribution network cash flows (Section 8.2)

### AC-29: Non-Compete Agreement Valuation [MUST]
Given protected revenue, profit margin, agreement term, probability of enforcement, and discount rate
When the user calls non_compete_valuation()
Then the function returns the value of protection from competition during the agreement term (Section 8.4)

### Human Capital and Workforce Assets (Chapter 9)

### AC-30: Assembled Workforce Valuation [MUST]
Given number of employees, average replacement cost, training cost, productivity factor, and attrition rate
When the user calls assembled_workforce_valuation()
Then the function returns the cost to replace the assembled workforce adjusted for productivity (Section 9.1)

### AC-31: Key Person Value [MUST]
Given key person's revenue contribution, replacement cost, probability of departure, and discount rate
When the user calls key_person_value()
Then the function returns the economic value of retaining the key person (Section 9.2)

### Goodwill and Purchase Price Allocation (Chapter 10, Appendix A.8)

### AC-32: Purchase Price Allocation (PPA) [MUST]
Given purchase price, fair value of tangible assets, and identified intangible asset values
When the user calls purchase_price_allocation()
Then the function returns the allocation waterfall with goodwill as the residual (Appendix A.8)

### AC-33: Goodwill Calculation [MUST]
Given purchase price and fair value of net identifiable assets
When the user calls goodwill()
Then the function returns: purchase_price - fair_value_of_net_identifiable_assets (Section 10.1)

### AC-34: Goodwill Impairment Testing [MUST]
Given reporting unit carrying value, fair value, and goodwill balance
When the user calls goodwill_impairment_test()
Then the function returns the impairment loss amount (if any) per ASC 350 / IAS 36 methodology (Section 10.4, A.9)

### AC-35: Intangible Asset Impairment Testing [MUST]
Given asset carrying value, fair value (or value in use), and recoverable amount
When the user calls intangible_impairment_test()
Then the function returns the impairment loss and updated carrying value (Section 10.4)

### Advanced Calculations (Appendix A)

### AC-36: Control Premium Calculation [MUST]
Given minority share price and control transaction price
When the user calls control_premium()
Then the function returns the control premium percentage (Appendix A.17)

### AC-37: Discount for Lack of Marketability (DLOM) [MUST]
Given restricted stock discount or put option data
When the user calls dlom()
Then the function returns the marketability discount percentage using Finnerty or Chaffe models (Appendix A.17)

### AC-38: Terminal Value Calculations [MUST]
Given final year cash flow, perpetual growth rate (or exit multiple), and discount rate
When the user calls terminal_value()
Then the function returns terminal value using both Gordon Growth and Exit Multiple methods (Appendix A.12)

### AC-39: Useful Life Estimation [MUST]
Given asset type, industry data, legal life, economic life factors, and obsolescence rate
When the user calls estimate_useful_life()
Then the function returns the estimated remaining useful life with supporting factors (Appendix A.6)

### AC-40: Contributory Asset Charges (CACs) [MUST]
Given asset values, required returns, and charge rates for working capital, fixed assets, and other intangibles
When the user calls contributory_asset_charges()
Then the function returns the total CACs with breakdown by asset type (Appendix A.11)

### AC-41: Sensitivity Analysis [MUST]
Given a valuation function, parameter name, range of values, and other fixed parameters
When the user calls sensitivity_analysis()
Then the function returns a table of valuation results across the parameter range (Appendix A.15)

### Cross-Border and Transfer Pricing (Chapter 16)

### AC-42: Currency Risk Adjustment [MUST]
Given base discount rate, currency risk premium, and country risk premium
When the user calls currency_adjusted_discount_rate()
Then the function returns the discount rate adjusted for currency and country risks (Section 16.3)

### AC-43: Transfer Pricing — Comparable Uncontrolled Price [MUST]
Given controlled transaction price and comparable uncontrolled prices
When the user calls cup_transfer_price()
Then the function returns the arm's length price range (Section 16.1)

### Litigation and Damages (Chapter 15)

### AC-44: Patent Infringement Damages [MUST]
Given lost profits or reasonable royalty basis, infringement period, discount rate, and prejudice interest rate
When the user calls patent_infringement_damages()
Then the function returns total damages including pre-judgment interest (Section 15.2)

### MCP Server

### AC-45: MCP Tool Exposure [MUST]
Given a running MCP server
When an AI agent queries available tools
Then all valuation functions are exposed as MCP tools with proper descriptions, parameter schemas, and examples

### AC-46: MCP Tool Execution [MUST]
Given a valid MCP tool call with parameters
When the server executes the tool
Then it returns the structured calculation result with all intermediate steps and formula references

### AI-Agent Skills

### AC-47: Valuation Calculator Skill [MUST]
Given a user query about intangible asset valuation
When the AI agent loads the valuation-calculator skill
Then it has access to all calculation methods with guided workflows for each valuation type

### AC-48: PPA Workflow Skill [MUST]
Given a purchase price allocation scenario
When the AI agent loads the ppa-workflow skill
Then it guides the user through the full PPA process: identify assets → value each → calculate goodwill → generate report

### AC-49: Impairment Checker Skill [SHOULD]
Given an asset or reporting unit
When the AI agent loads the impairment-checker skill
Then it guides the user through impairment testing with appropriate methodology selection

### Error Handling

### Advanced Core Methods (Enhanced)

### AC-50: Graduated Discount Rate PV [SHOULD]
Given cash flows with period-specific discount rates (yield curve)
When the user calls present_value_graduated()
Then the function returns the PV using each period's specific rate

### AC-51: Annuity Due [SHOULD]
Given payment, discount rate, and periods for beginning-of-period payments
When the user calls annuity_due_pv()
Then the function returns PV = PMT * [(1 - (1+r)^-n) / r] * (1+r)

### AC-52: Growing Perpetuity [SHOULD]
Given first payment, discount rate, and growth rate
When the user calls growing_perpetuity_pv()
Then the function returns PV = PMT / (r - g)

### AC-53: Effective Annual Rate [SHOULD]
Given nominal rate and compounding frequency
When the user calls effective_annual_rate()
Then the function returns EAR = (1 + r/n)^n - 1

### AC-54: Continuous Compounding [SHOULD]
Given principal, rate, and time
When the user calls continuous_compounding()
Then the function returns FV = PV * e^(rt)

### AC-55: WACC with Preferred Stock [SHOULD]
Given equity, debt, preferred values and their respective costs
When the user calls wacc_with_preferred()
Then the function returns WACC including preferred stock in capital structure

### AC-56: Beta Unlevering/Relevering [SHOULD]
Given levered beta, D/E ratio, and tax rate
When the user calls beta_unlevered() or beta_relevered()
Then the function returns the unlevered/relevered beta using Hamada equation

### AC-57: Fama-French 3-Factor Cost of Equity [SHOULD]
Given market beta, SMB beta, HML beta, and respective premiums
When the user calls cost_of_equity_fama_french()
Then the function returns cost of equity using Fama-French model

### AC-58: Implied ERP from Market P/E [SHOULD]
Given market P/E ratio and perpetual growth rate
When the user calls implied_erp()
Then the function returns implied equity risk premium

### AC-59: Monte Carlo with Correlated Inputs [SHOULD]
Given input distributions and correlation matrix
When the user calls monte_carlo_with_correlation()
Then the function returns simulation results using Cholesky decomposition

### AC-60: Scenario Analysis [SHOULD]
Given multiple scenarios with probabilities and parameters
When the user calls scenario_analysis()
Then the function returns probability-weighted expected value

### AC-61: Sensitivity Tornado [SHOULD]
Given base parameters and ranges for each parameter
When the user calls sensitivity_tornado()
Then the function returns tornado diagram data sorted by impact

### Enhanced Asset Type Methods

### AC-62: Patent Portfolio Valuation [SHOULD]
Given a portfolio of patents with individual values
When the user calls patent_portfolio_valuation()
Then the function returns total portfolio value with diversification adjustment

### AC-63: Real Options Patent Valuation [SHOULD]
Given exercise cost, expected value, volatility, time to expiry
When the user calls option_pricing_patent()
Then the function returns patent value using Black-Scholes approximation

### AC-64: Interbrand Brand Valuation [SHOULD]
Given brand earnings, role of brand index, brand strength score
When the user calls interbrand_brand_valuation()
Then the function returns brand value using Interbrand methodology

### AC-65: Brand Strength Index [SHOULD]
Given revenue stability, market share, geographic reach, loyalty, investment
When the user calls brand_strength_index()
Then the function returns composite brand strength score (0-100)

### AC-66: Customer Lifetime Value [SHOULD]
Given revenue per period, retention rate, discount rate, margin
When the user calls customer_lifetime_value()
Then the function returns infinite-horizon CLV

### AC-67: Order Backlog Valuation [SHOULD]
Given contract backlog, completion probabilities, discount rate
When the user calls backlog_valuation()
Then the function returns risk-adjusted PV of backlog

### AC-68: Churn Impact Analysis [SHOULD]
Given churn rates before/after, customer count, revenue per customer
When the user calls churn_impact_analysis()
Then the function returns value impact of churn change

### AC-69: Technology Obsolescence Curve [SHOULD]
Given initial value, obsolescence rate, projection periods
When the user calls technology_obsolescence_curve()
Then the function returns technology value decay over time

### AC-70: API Valuation [SHOULD]
Given API call volume, revenue per call, growth rate
When the user calls api_valuation()
Then the function returns API asset value via income approach

### Enhanced Advanced Methods

### AC-71: Value in Use (IAS 36) [SHOULD]
Given cash flow projections, terminal growth rate, discount rate
When the user calls value_in_use()
Then the function returns IAS 36 value in use with terminal value

### AC-72: CGU Impairment Allocation [SHOULD]
Given CGU carrying value, recoverable amount, allocated goodwill
When the user calls cash_generating_unit_impairment()
Then the function returns impairment allocated to goodwill first, then pro rata

### AC-73: Contingent Consideration Valuation [SHOULD]
Given earn-out scenarios with probabilities and discount rate
When the user calls contingent_consideration_valuation()
Then the function returns probability-weighted earn-out value

### AC-74: Deferred Tax Liability from PPA [SHOULD]
Given identified intangibles, tax basis, statutory rate
When the user calls deferred_tax_liability_ppa()
Then the function returns DTL from PPA step-up

### AC-75: Bargain Purchase Analysis [SHOULD]
Given purchase price below fair value of net assets
When the user calls bargain_purchase_analysis()
Then the function returns bargain purchase amount with documentation

### AC-76: Amortization Schedules [SHOULD]
Given asset value and useful life
When the user calls straight_line_amortization(), sum_of_years_digits_amortization(), or double_declining_balance_amortization()
Then the function returns the complete amortization schedule

### AC-77: Profit Split Method [SHOULD]
Given licensor and licensee contribution percentages
When the user calls profit_split_method()
Then the function returns royalty using OECD profit split approach

### Error Handling

### AC-E1: Invalid Input Validation [MUST]
Given a negative discount rate, negative cash flow where not allowed, or missing required parameter
When any valuation function is called
Then it raises a ValidationError with a descriptive message identifying the invalid field and acceptable range

### AC-E2: Division by Zero Protection [MUST]
Given a zero discount rate in a perpetuity calculation or zero revenue in a royalty calculation
When the function is called
Then it raises a ValidationError explaining the constraint and suggesting alternatives

### AC-E3: Incompatible Parameter Detection [MUST]
Given a useful life longer than the legal life of a patent or a retention rate above 100%
When the function is called
Then it raises a ValidationError with a specific explanation of the incompatibility

### AC-E4: MCP Tool Error Response [MUST]
Given an invalid MCP tool call (missing required parameter, wrong type)
When the server processes the call
Then it returns a structured error response with the validation error details, not a stack trace

### Non-Functional Requirements

- Performance: All single-asset valuations complete in < 100ms; Monte Carlo with 10,000 iterations in < 5s
- Accuracy: All results match textbook examples to 2 decimal places
- Test coverage: 100% of public functions have unit tests; all book exercises have verification tests
- Documentation: Every function has docstring with formula, parameters, returns, and book reference
- Reproducibility: Monte Carlo simulations support seed parameter for reproducible results

## Out of Scope

- Real-time market data feeds (rates, multiples are user-provided)
- Full accounting system integration
- GUI application (library + MCP + CLI only)
- Multi-currency conversion (user provides amounts in single currency)
- Tax filing or compliance automation

## Open Questions

- [RESOLVED] Package name → `intangible-valuation`
- [RESOLVED] MCP framework → fastmcp
- [RESOLVED] Python minimum version → 3.11
- [RESOLVED] Testing framework → pytest
- [NEEDS CLARIFICATION] Should royalty benchmark database be bundled or external API?
- [NEEDS CLARIFICATION] Should CLI be included in v1 or deferred?
