import pandas as pd

from src.engine import add_features, capacity_simulation, score


def fixture_df():
    rows = []
    for i in range(25):
        rows.append(
            {
                "OBJECTID": i + 1,
                "AGENCY": "Agency A" if i < 20 else "Agency B",
                "TRANSACTION_DATE": pd.Timestamp("2026-01-05") + pd.Timedelta(days=i % 10),
                "TRANSACTION_AMOUNT": 100 + i * 11,
                "VENDOR_NAME": f"Vendor {i % 5}",
                "VENDOR_STATE_PROVINCE": "DC",
                "MCC_DESCRIPTION": "Office Supplies" if i < 22 else "Rare Category",
            }
        )
    # Create a clear near-duplicate pair and an extreme amount.
    rows[1]["VENDOR_NAME"] = "Vendor X"
    rows[2]["VENDOR_NAME"] = "Vendor X"
    rows[1]["TRANSACTION_AMOUNT"] = 777.0
    rows[2]["TRANSACTION_AMOUNT"] = 777.0
    rows[2]["TRANSACTION_DATE"] = rows[1]["TRANSACTION_DATE"] + pd.Timedelta(days=1)
    rows[-1]["TRANSACTION_AMOUNT"] = 25_000.0
    return pd.DataFrame(rows)


def test_score_bounds_and_reasons():
    scored = score(add_features(fixture_df()))
    assert scored["priority_score"].between(0, 100).all()
    assert scored["reasons"].notna().all()


def test_near_duplicate_detected():
    featured = add_features(fixture_df())
    pair = featured[(featured["VENDOR_NAME"] == "Vendor X") & (featured["TRANSACTION_AMOUNT"] == 777.0)]
    assert (pair["near_duplicate"] == 1).all()


def test_capacity_threshold_is_monotonic():
    scored = score(add_features(fixture_df()))
    sim = capacity_simulation(scored)
    assert sim["alerts"].is_monotonic_decreasing
