"""Synthetic demonstration data generator.

This module exists so the pipeline can be executed without network access and so
the repository contains reviewable example outputs.

IMPORTANT: data produced here is SYNTHETIC. It is generated from random
distributions and contains no real agencies, vendors or transactions. It is used
only to demonstrate that the pipeline executes and to show the SHAPE of the
outputs. No finding produced from this data says anything about the District of
Columbia or any real organisation.

Run the pipeline against the live source (default mode) to produce real results.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SYNTHETIC_AGENCIES = [f"SYNTHETIC AGENCY {chr(65 + i)}" for i in range(10)]
SYNTHETIC_MCCS = [
    "OFFICE SUPPLIES",
    "IT HARDWARE",
    "SOFTWARE SUBSCRIPTION",
    "FACILITIES MAINTENANCE",
    "PROFESSIONAL SERVICES",
    "FUEL",
    "LABORATORY SUPPLIES",
    "TRAINING SERVICES",
    "MEDICAL SUPPLIES",
    "PRINTING",
    "CATERING",
    "SECURITY SERVICES",
]


def generate(n_transactions: int = 6000, seed: int = 7) -> pd.DataFrame:
    """Generate a synthetic purchase-card extract matching the source schema.

    The generator deliberately injects a small number of structured patterns
    (split-style repeats, same-day bursts, a concentrated vendor relationship)
    so the scoring engine has something to find. This is a demonstration
    fixture, not a labelled ground truth: the injected rows are not marked, and
    the engine receives no hint that they exist.
    """
    rng = np.random.default_rng(seed)

    vendors = [f"SYNTHETIC VENDOR {i:03d}" for i in range(150)]
    # Vendor popularity is skewed, as it is in real procurement data.
    vendor_weights = rng.dirichlet(np.full(len(vendors), 0.6))

    agency = rng.choice(SYNTHETIC_AGENCIES, n_transactions)
    vendor = rng.choice(vendors, n_transactions, p=vendor_weights)
    mcc = rng.choice(SYNTHETIC_MCCS, n_transactions)
    amount = np.round(rng.lognormal(mean=5.6, sigma=1.15, size=n_transactions), 2)

    start = pd.Timestamp("2023-10-01")
    offsets = rng.integers(0, 640, n_transactions)
    date = start + pd.to_timedelta(offsets, unit="D")

    df = pd.DataFrame(
        {
            "AGENCY": agency,
            "VENDOR_NAME": vendor,
            "MCC_DESCRIPTION": mcc,
            "VENDOR_STATE_PROVINCE": rng.choice(
                ["DC", "MD", "VA", "NY", "CA"], n_transactions, p=[0.4, 0.2, 0.2, 0.1, 0.1]
            ),
            "TRANSACTION_DATE": date,
            "TRANSACTION_AMOUNT": amount,
        }
    )

    df = pd.concat([df, _injected_patterns(rng)], ignore_index=True)
    df = df.sort_values("TRANSACTION_DATE").reset_index(drop=True)
    df.insert(0, "OBJECTID", np.arange(1, len(df) + 1))

    # The pipeline's quality gate should see a realistic, imperfect extract.
    null_idx = rng.choice(len(df), size=max(int(len(df) * 0.004), 1), replace=False)
    df.loc[null_idx, "VENDOR_STATE_PROVINCE"] = np.nan

    # Return dates as epoch milliseconds to match the live ArcGIS JSON response,
    # so the same normalization path is exercised in both modes.
    df["TRANSACTION_DATE"] = df["TRANSACTION_DATE"].astype("datetime64[ms]").astype("int64")
    return df


def _injected_patterns(rng: np.random.Generator) -> pd.DataFrame:
    """Inject structured behaviour so the demo queue is not pure noise."""
    rows: list[dict] = []

    # 1) Repeated identical amounts just under a scenario review threshold.
    repeat_profiles = [
        ("SYNTHETIC AGENCY C", "SYNTHETIC VENDOR 021", "PROFESSIONAL SERVICES", 4900.00),
        ("SYNTHETIC AGENCY E", "SYNTHETIC VENDOR 088", "TRAINING SERVICES", 4750.00),
        ("SYNTHETIC AGENCY A", "SYNTHETIC VENDOR 034", "SOFTWARE SUBSCRIPTION", 4995.00),
    ]
    for agency_name, vendor_name, category, value in repeat_profiles:
        for _ in range(int(rng.integers(3, 6))):
            base = pd.Timestamp("2024-04-08") + pd.Timedelta(days=int(rng.integers(0, 300)))
            for offset in range(int(rng.integers(2, 4))):
                rows.append(
                    {
                        "AGENCY": agency_name,
                        "VENDOR_NAME": vendor_name,
                        "MCC_DESCRIPTION": category,
                        "VENDOR_STATE_PROVINCE": "VA",
                        "TRANSACTION_DATE": base + pd.Timedelta(days=offset),
                        "TRANSACTION_AMOUNT": value,
                    }
                )

    # 2) Same-day bursts against a single vendor.
    for i in range(10):
        day = pd.Timestamp("2024-08-14") + pd.Timedelta(days=int(rng.integers(0, 90)))
        for _ in range(int(rng.integers(4, 8))):
            rows.append(
                {
                    "AGENCY": "SYNTHETIC AGENCY F",
                    "VENDOR_NAME": "SYNTHETIC VENDOR 067",
                    "MCC_DESCRIPTION": "IT HARDWARE",
                    "VENDOR_STATE_PROVINCE": "MD",
                    "TRANSACTION_DATE": day,
                    "TRANSACTION_AMOUNT": float(np.round(rng.uniform(800, 2600), 2)),
                }
            )

    # 3) A late-appearing vendor that rapidly concentrates one agency's spend.
    for i in range(60):
        rows.append(
            {
                "AGENCY": "SYNTHETIC AGENCY I",
                "VENDOR_NAME": "SYNTHETIC VENDOR 142",
                "MCC_DESCRIPTION": "FACILITIES MAINTENANCE",
                "VENDOR_STATE_PROVINCE": "DC",
                "TRANSACTION_DATE": pd.Timestamp("2025-03-01")
                + pd.Timedelta(days=int(rng.integers(0, 75))),
                "TRANSACTION_AMOUNT": float(np.round(rng.uniform(6000, 19000), 2)),
            }
        )

    return pd.DataFrame(rows)
