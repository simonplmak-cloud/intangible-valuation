# API Contract: Error Handling

## Error Response Format

All errors follow a consistent structured format.

### Validation Error (400)

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Human-readable description of the error",
  "details": {
    "field": "field_name",
    "constraint": "constraint_description",
    "provided_value": "actual_value_provided",
    "acceptable_range": "description_of_valid_range"
  }
}
```

### Division by Zero Error (400)

```json
{
  "error": "DIVISION_BY_ZERO",
  "message": "Cannot calculate perpetuity with zero discount rate",
  "details": {
    "field": "discount_rate",
    "constraint": "must be greater than 0",
    "suggestion": "Use a small positive rate (e.g., 0.001) as a minimum"
  }
}
```

### Incompatible Parameters Error (400)

```json
{
  "error": "INCOMPATIBLE_PARAMETERS",
  "message": "Useful life (20 years) cannot exceed legal patent life (17 years)",
  "details": {
    "field1": "useful_life",
    "value1": 20,
    "field2": "legal_life",
    "value2": 17,
    "constraint": "useful_life <= legal_life"
  }
}
```

### Not Found Error (404)

```json
{
  "error": "TOOL_NOT_FOUND",
  "message": "No MCP tool named 'invalid_method' exists",
  "details": {
    "requested_tool": "invalid_method",
    "suggestion": "Did you mean 'relief_from_royalty'?"
  }
}
```

## Error Codes Summary

| Status | Code | Description |
|--------|------|-------------|
| 400 | VALIDATION_ERROR | Input fails Pydantic validation |
| 400 | DIVISION_BY_ZERO | Calculation would divide by zero |
| 400 | INCOMPATIBLE_PARAMETERS | Parameters are individually valid but incompatible together |
| 400 | NEGATIVE_GOODWILL | Bargain purchase detected (purchase price < net identifiable assets) |
| 404 | TOOL_NOT_FOUND | Requested MCP tool does not exist |
| 500 | CALCULATION_ERROR | Unexpected error during calculation (should never happen) |

## AC Coverage
- AC-E1: VALIDATION_ERROR for all invalid inputs
- AC-E2: DIVISION_BY_ZERO protection
- AC-E3: INCOMPATIBLE_PARAMETERS detection
- AC-E4: MCP error response formatting
