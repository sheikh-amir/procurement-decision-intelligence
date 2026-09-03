"""Data acquisition, source validation and normalization utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import requests

from .config import API_URL, EXPECTED_COLUMNS


def fetch_all_raw(page_size: int = 1000) -> pd.DataFrame:
    """Download source records without cleaning so quality controls see raw defects."""
    rows: list[dict] = []
    offset = 0

    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "false",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": page_size,
            "orderByFields": "OBJECTID",
        }
        response = requests.get(API_URL, params=params, timeout=60)
        response.raise_for_status()
        payload = response.json()
        if "error" in payload:
            raise RuntimeError(f"ArcGIS API error: {payload['error']}")

        features = payload.get("features", [])
        rows.extend(feature.get("attributes", {}) for feature in features)

        if len(features) < page_size:
            break
        offset += page_size

    df = pd.DataFrame(rows)
    validate_columns(df.columns)
    return df


def fetch_all(page_size: int = 1000) -> pd.DataFrame:
    """Backward-compatible convenience function returning normalized source data."""
    return normalize(fetch_all_raw(page_size=page_size))


def validate_columns(columns: Iterable[str]) -> None:
    missing = EXPECTED_COLUMNS.difference(set(columns))
    if missing:
        raise ValueError(f"Dataset schema changed; missing columns: {sorted(missing)}")


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize types and analysis keys without mutating the input."""
    out = df.copy()
    # ArcGIS dates are epoch milliseconds when returned as JSON.
    if not pd.api.types.is_datetime64_any_dtype(out["TRANSACTION_DATE"]):
        out["TRANSACTION_DATE"] = pd.to_datetime(
            out["TRANSACTION_DATE"], unit="ms", errors="coerce"
        )
    out["TRANSACTION_AMOUNT"] = pd.to_numeric(out["TRANSACTION_AMOUNT"], errors="coerce")
    for col in ["AGENCY", "VENDOR_NAME", "VENDOR_STATE_PROVINCE", "MCC_DESCRIPTION"]:
        out[col] = out[col].fillna("UNKNOWN").astype(str).str.strip()
    out = out.dropna(subset=["TRANSACTION_DATE", "TRANSACTION_AMOUNT"])
    out = out.drop_duplicates(subset=["OBJECTID"]).reset_index(drop=True)
    return out


def save_raw(df: pd.DataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
