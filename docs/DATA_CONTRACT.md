# Data Contract

## Purpose

Define the minimum source expectations required before the analytical process may execute. The contract separates **source reliability** from **analytical scoring** so data failures cannot silently become risk signals.

## Required fields

| Field | Expected type | Business meaning | Criticality |
|---|---|---|---|
| `OBJECTID` | unique identifier | source transaction key | Critical |
| `AGENCY` | text | organizational owner | Critical |
| `TRANSACTION_DATE` | date/time | transaction timing | Critical |
| `TRANSACTION_AMOUNT` | numeric | transaction value | Critical |
| `VENDOR_NAME` | text | supplier / merchant | Critical |
| `VENDOR_STATE_PROVINCE` | text | vendor geography | Medium |
| `MCC_DESCRIPTION` | text | merchant category context | Critical |

## Quality gates

| Rule | Threshold | Action |
|---|---:|---|
| required column missing | any | fail pipeline |
| duplicate `OBJECTID` | > 0 | fail pipeline |
| parseable amount rate | < 99% | fail pipeline |
| null rate in required field | > 5% | warn / investigate |

## Lineage

```text
DC Open Data API
  → raw source response
  → normalized transaction table
  → feature table
  → scored transaction table
  → management decision outputs
```

## Known semantic limitations

- The public data does not provide investigation outcomes.
- “New vendor” means newly observed in the dataset window, not necessarily newly onboarded.
- Merchant category descriptions may not fully describe procurement purpose.
- Vendor names may contain aliases or formatting differences; production implementation should add governed entity resolution.
- Transaction-level data cannot prove policy violation without policy and supporting-document context.
