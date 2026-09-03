"""Data-quality controls and observability metrics."""
from __future__ import annotations

import pandas as pd

from .config import EXPECTED_COLUMNS


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return control metrics used as an ingestion quality gate."""
    rows: list[dict] = []
    n = max(len(df), 1)
    for col in sorted(EXPECTED_COLUMNS):
        if col not in df.columns:
            rows.append({"metric": f"missing_column::{col}", "value": 1.0, "status": "FAIL"})
            continue
        null_rate = float(df[col].isna().mean())
        rows.append(
            {
                "metric": f"null_rate::{col}",
                "value": round(null_rate, 6),
                "status": "PASS" if null_rate <= 0.05 else "WARN",
            }
        )

    duplicate_rate = 0.0
    if "OBJECTID" in df.columns:
        duplicate_rate = float(df["OBJECTID"].duplicated().sum() / n)
    rows.append(
        {
            "metric": "duplicate_objectid_rate",
            "value": round(duplicate_rate, 6),
            "status": "PASS" if duplicate_rate == 0 else "FAIL",
        }
    )

    if "TRANSACTION_AMOUNT" in df.columns:
        numeric_rate = float(pd.to_numeric(df["TRANSACTION_AMOUNT"], errors="coerce").notna().mean())
        rows.append(
            {
                "metric": "numeric_amount_rate",
                "value": round(numeric_rate, 6),
                "status": "PASS" if numeric_rate >= 0.99 else "FAIL",
            }
        )
    return pd.DataFrame(rows)


def enforce_quality_gate(report: pd.DataFrame) -> None:
    failures = report.loc[report["status"] == "FAIL", "metric"].tolist()
    if failures:
        raise ValueError(f"Data-quality gate failed: {failures}")
