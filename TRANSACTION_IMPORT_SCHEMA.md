# Transaction Import JSON Schema

This document describes the exact JSON schema for importing transactions into the Maaser Calculator & Tracker application. Use this reference to convert any transaction files into the correct format.

## Format Overview

The JSON file must be an **array of transaction objects**. Each transaction object represents a single income or maaser transaction.

```json
[
  { /* transaction 1 */ },
  { /* transaction 2 */ },
  { /* transaction 3 */ }
]
```

## Transaction Object Schema

### Required Fields

These fields **must** be present in every transaction object:

| Field | Type | Description | Valid Values | Example |
|-------|------|-------------|--------------|---------|
| `type` | string | The type of transaction | `"income"` or `"maaser"` | `"income"` |
| `amount` | number | The monetary amount | Any positive number | `150.50` |
| `date` | string | The transaction date | Format: `"YYYY-MM-DD"` | `"2024-03-15"` |

### Optional Fields

These fields are optional and will use default values if not provided:

| Field | Type | Description | Default Value | Example |
|-------|------|-------------|---------------|---------|

| `memo` | string | Transaction description/note | `""` (empty string) | `"Weekly paycheck"` |
| `account_id` | string \| null | Associated bank account ID | `null` (represents cash) | `"a1b2c3d4-..."` |

### Generated Fields

The following field will be **automatically generated** during import (do not include in your JSON):

- `id`: A unique UUID identifier will be assigned to each transaction

## Detailed Field Specifications

### `type` (Required)
- **Must be exactly** `"income"` or `"maaser"`
- Case-sensitive (lowercase only)
- Transactions with invalid types will be skipped

### `amount` (Required)
- **Must be a valid number**
- Can be integer or decimal
- Negative amounts are technically allowed but not recommended
- Examples: `100`, `50.99`, `1234.56`

### `date` (Required)
- **Must follow ISO 8601 date format**: `YYYY-MM-DD`
- Year must be 4 digits
- Month must be 2 digits (01-12)
- Day must be 2 digits (01-31)
- Examples: `"2024-01-15"`, `"2023-12-31"`, `"2025-06-01"`



### `memo` (Optional)
- **String containing transaction notes**
- Can be any text description
- Used for searching and categorizing transactions
- If omitted, defaults to empty string `""`
- Examples: `"Salary - March 2024"`, `"Donation to local charity"`, `"Paycheck"`

### `account_id` (Optional)
- **String UUID or null**
- References a bank account defined in your system
- Use `null` or omit entirely to indicate a cash transaction
- Account IDs must already exist in your system
- Example: `"f47ac10b-58cc-4372-a567-0e02b2c3d479"`
- For cash transactions: `null` or simply omit the field

## Complete Examples

### Minimal Valid Transaction (Income)
```json
[
  {
    "type": "income",
    "amount": 1000,
    "date": "2024-11-27"
  }
]
```

### Complete Transaction with All Fields (Income)
```json
[
  {
    "type": "income",
    "amount": 2500.00,
    "date": "2024-11-15",

    "memo": "Monthly salary - November",
    "account_id": null
  }
]
```

### Maaser Transaction
```json
[
  {
    "type": "maaser",
    "amount": 250.00,
    "date": "2024-11-20",

    "memo": "Donation to local food bank"
  }
]
```

### Multiple Transactions
```json
[
  {
    "type": "income",
    "amount": 3000.00,
    "date": "2024-11-01",

    "memo": "Consulting project payment"
  },
  {
    "type": "income",
    "amount": 500.00,
    "date": "2024-11-10",
    "memo": "Freelance work"
  },
  {
    "type": "maaser",
    "amount": 350.00,
    "date": "2024-11-15",

    "memo": "Monthly maaser payment",
    "account_id": null
  },
  {
    "type": "maaser",
    "amount": 100.00,
    "date": "2024-11-20",
    "memo": "Tzedakah box"
  }
]
```

## Validation Rules

The import system will:

1. **Skip invalid entries** that don't meet requirements
2. **Require all three core fields**: `type`, `amount`, `date`
3. **Validate type values**: Must be exactly `"income"` or `"maaser"`
4. **Validate amount**: Must be convertible to a floating-point number
5. **Generate unique IDs**: Each imported transaction receives a new UUID
6. **Apply defaults for optional fields**:

   - `memo` defaults to `""`
   - `account_id` defaults to `null` (cash)

## Common Conversion Scenarios

### From CSV with Headers
If you have a CSV like:
```csv
income,1500.00,2024-11-01,Salary
maaser,150.00,2024-11-05,Charity
```

Convert to JSON:
```json
[
  {
    "type": "income",
    "amount": 1500.00,
    "date": "2024-11-01",

    "memo": "Salary"
  },
  {
    "type": "maaser",
    "amount": 150.00,
    "date": "2024-11-05",

    "memo": "Charity"
  }
]
```

### From Bank Statement
If you have bank data with different field names:
```
Transaction Date: 11/15/2024
Amount: $2,500.00
Description: SALARY DEPOSIT
```

Convert to JSON:
```json
[
  {
    "type": "income",
    "amount": 2500.00,
    "date": "2024-11-15",
    "memo": "SALARY DEPOSIT"
  }
]
```

## LLM Conversion Prompt Template

When using an LLM to convert transaction files, use this prompt:

---

**Convert the following transaction data into valid JSON for the Maaser Calculator & Tracker application.**

**Required JSON Format:**
- Array of transaction objects
- Each object MUST have: `type` (either "income" or "maaser"), `amount` (number), `date` (YYYY-MM-DD format)
- Optional fields: `memo` (string), `account_id` (UUID string or null)

**Important Rules:**
1. Dates must be in ISO 8601 format: YYYY-MM-DD

3. Type must be exactly "income" or "maaser" (lowercase)
4. Amount must be a valid number (no currency symbols)

6. For cash transactions, omit account_id or set it to null

**Transaction data to convert:**
[Paste your transaction data here]

**Expected output:**
```json
[
  {
    "type": "income",
    "amount": 0.00,
    "date": "YYYY-MM-DD",

    "memo": "description"
  }
]
```

---

## Troubleshooting

### Common Errors

**"Invalid JSON format: must be an array of objects"**
- Ensure your JSON starts with `[` and ends with `]`
- Each transaction should be wrapped in `{}`

**"No valid transactions found in the provided JSON"**
- Check that each transaction has `type`, `amount`, and `date` fields
- Verify `type` is exactly "income" or "maaser"
- Confirm `amount` is a valid number

**"Invalid JSON. Please check the syntax."**
- Validate your JSON using a JSON validator
- Check for missing commas between objects
- Ensure all strings are in double quotes
- Remove trailing commas after the last item in arrays/objects

### Testing Your JSON

Before importing, you can validate your JSON:
1. Use an online JSON validator (e.g., jsonlint.com)
2. Check that it parses as valid JSON
3. Verify it follows the array-of-objects structure
4. Confirm all required fields are present

## Summary Checklist

- [ ] Root structure is an array: `[...]`
- [ ] Each transaction is an object: `{...}`
- [ ] Every transaction has `type`, `amount`, and `date`
- [ ] `type` is either `"income"` or `"maaser"`
- [ ] `amount` is a valid number
- [ ] `date` follows `YYYY-MM-DD` format

- [ ] Optional: `memo` is a string
- [ ] Optional: `account_id` is a UUID string or null
- [ ] All strings use double quotes (`"`)
- [ ] Proper JSON syntax (commas, brackets, etc.)

---

**Version:** 1.0  
**Last Updated:** 2025-11-27  
**Application:** Maaser Calculator & Tracker
