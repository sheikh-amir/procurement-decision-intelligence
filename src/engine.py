"""Explainable exception signals, prioritization, and workload simulation."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from .config import MIN_PEER_SIZE, SCENARIO_REVIEW_AMOUNT, SIGNAL_FAMILIES, WEIGHTS
from .explain import add_explanations
from .network import add_network_features


def _robust_peer_score(series: pd.Series) -> pd.Series:
    """Return a 0..1 robust magnitude score using median absolute deviation."""
    x = series.astype(float)
    median = x.median()
    mad = (x - median).abs().median()
    if pd.isna(mad) or mad == 0:
        return x.rank(pct=True, method="average").fillna(0.5).clip(0, 1)
    robust_z = 0.6745 * (x - median) / mad
    return (1 / (1 + np.exp(-robust_z.clip(-10, 10)))).clip(0, 1)


def _hierarchical_peer_score(df: pd.DataFrame) -> pd.Series:
    """Use agency+MCC peers when the group is large enough, else back off to MCC then agency."""
    fine_count = df.groupby(["AGENCY", "MCC_DESCRIPTION"], dropna=False)["OBJECTID"].transform("count")
    fine = df.groupby(["AGENCY", "MCC_DESCRIPTION"], dropna=False)["TRANSACTION_AMOUNT"].transform(
        lambda s: _robust_peer_score(s.abs())
    )
    mcc = df.groupby("MCC_DESCRIPTION", dropna=False)["TRANSACTION_AMOUNT"].transform(
        lambda s: _robust_peer_score(s.abs())
    )
    agency = df.groupby("AGENCY", dropna=False)["TRANSACTION_AMOUNT"].transform(
        lambda s: _robust_peer_score(s.abs())
    )
    return fine.where(fine_count >= MIN_PEER_SIZE, mcc).fillna(agency).astype(float)


def _temporal_relationship_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["month"] = out["TRANSACTION_DATE"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        out.groupby(["AGENCY", "VENDOR_NAME", "month"], dropna=False)["TRANSACTION_AMOUNT"]
        .apply(lambda s: float(s.abs().sum()))
        .rename("month_spend")
        .reset_index()
        .sort_values(["AGENCY", "VENDOR_NAME", "month"])
    )

    keys = ["AGENCY", "VENDOR_NAME"]
    monthly["prior_median"] = monthly.groupby(keys)["month_spend"].transform(
        lambda s: s.shift(1).rolling(6, min_periods=2).median()
    )
    monthly["prior_mad"] = monthly.groupby(keys)["month_spend"].transform(
        lambda s: s.shift(1).rolling(6, min_periods=2).apply(
            lambda x: float(np.median(np.abs(x - np.median(x)))), raw=True
        )
    )
    mad = monthly["prior_mad"].replace(0, np.nan)
    rz = 0.6745 * (monthly["month_spend"] - monthly["prior_median"]) / mad
    percentile_fallback = monthly.groupby("AGENCY")["month_spend"].rank(pct=True)
    spike = (1 / (1 + np.exp(-rz.clip(-10, 10)))).where(rz.notna(), percentile_fallback)
    monthly["temporal_spend_spike"] = spike.fillna(0.5).clip(0, 1)

    out = out.merge(
        monthly[["AGENCY", "VENDOR_NAME", "month", "temporal_spend_spike"]],
        on=["AGENCY", "VENDOR_NAME", "month"],
        how="left",
    )
    first_observed = out.groupby(["AGENCY", "VENDOR_NAME"], dropna=False)["TRANSACTION_DATE"].transform("min")
    age_days = (out["TRANSACTION_DATE"] - first_observed).dt.days
    # This is "new in the observed dataset", not proof that the vendor was newly onboarded.
    out["new_vendor_for_agency"] = (age_days <= 30).astype(float)
    out["relationship_age_days_observed"] = age_days.clip(lower=0)
    return out.drop(columns=["month"])


def add_features(df: pd.DataFrame, scenario_amount: float = SCENARIO_REVIEW_AMOUNT) -> pd.DataFrame:
    out = df.copy().sort_values("TRANSACTION_DATE").reset_index(drop=True)
    amount_abs = out["TRANSACTION_AMOUNT"].abs()

    out["peer_amount"] = _hierarchical_peer_score(out)

    key_cols = ["AGENCY", "VENDOR_NAME", "TRANSACTION_AMOUNT"]
    prev_date = out.groupby(key_cols, dropna=False)["TRANSACTION_DATE"].shift(1)
    next_date = out.groupby(key_cols, dropna=False)["TRANSACTION_DATE"].shift(-1)
    near_prev = (out["TRANSACTION_DATE"] - prev_date).dt.days.between(0, 3)
    near_next = (next_date - out["TRANSACTION_DATE"]).dt.days.between(0, 3)
    out["near_duplicate"] = (near_prev | near_next).fillna(False).astype(float)

    daily_count = out.groupby(
        ["AGENCY", "VENDOR_NAME", out["TRANSACTION_DATE"].dt.date], dropna=False
    )["OBJECTID"].transform("count")
    out["burst_activity"] = np.minimum((daily_count - 1) / 3, 1).clip(0, 1)

    combo_count = out.groupby(["AGENCY", "MCC_DESCRIPTION"], dropna=False)["OBJECTID"].transform("count")
    agency_count = out.groupby("AGENCY", dropna=False)["OBJECTID"].transform("count")
    combo_share = (combo_count / agency_count.replace(0, np.nan)).fillna(0)
    out["rare_agency_mcc"] = (1 - np.minimum(combo_share / 0.10, 1)).clip(0, 1)

    out["round_amount"] = ((amount_abs >= 100) & (amount_abs % 100 == 0)).astype(float)
    out["weekend"] = out["TRANSACTION_DATE"].dt.dayofweek.isin([5, 6]).astype(float)

    distance = (amount_abs - scenario_amount).abs()
    out["threshold_proximity"] = np.exp(-distance / max(scenario_amount * 0.10, 1))

    out = add_network_features(out)
    out = _temporal_relationship_features(out)
    out["unsupervised"] = _isolation_signal(out)
    return out


def _isolation_signal(df: pd.DataFrame) -> pd.Series:
    if len(df) < 20:
        return pd.Series(np.zeros(len(df)), index=df.index, dtype=float)

    amount_abs = df["TRANSACTION_AMOUNT"].abs().clip(lower=0)
    vendor_freq = df.groupby("VENDOR_NAME")["OBJECTID"].transform("count")
    mcc_freq = df.groupby("MCC_DESCRIPTION")["OBJECTID"].transform("count")
    agency_freq = df.groupby("AGENCY")["OBJECTID"].transform("count")

    X = pd.DataFrame(
        {
            "log_amount": np.log1p(amount_abs),
            "vendor_freq": np.log1p(vendor_freq),
            "mcc_freq": np.log1p(mcc_freq),
            "agency_freq": np.log1p(agency_freq),
            "day_of_week": df["TRANSACTION_DATE"].dt.dayofweek,
            "vendor_share": df.get("vendor_agency_spend_share", 0),
            "relationship_age": np.log1p(df.get("relationship_age_days_observed", 0)),
        }
    ).fillna(0)

    model = IsolationForest(
        n_estimators=300,
        max_samples="auto",
        contamination="auto",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X)
    raw = -model.score_samples(X)
    lo, hi = float(raw.min()), float(raw.max())
    if hi == lo:
        return pd.Series(np.zeros(len(df)), index=df.index, dtype=float)
    return pd.Series((raw - lo) / (hi - lo), index=df.index, dtype=float)


def score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    total_weight = sum(WEIGHTS.values())
    weighted = sum(out[col].fillna(0).clip(0, 1) * weight for col, weight in WEIGHTS.items())
    out["priority_score"] = (100 * weighted / total_weight).round(1).clip(0, 100)
    out["signal_count"] = sum((out[col] >= 0.5).astype(int) for col in WEIGHTS)

    def family_count(row: pd.Series) -> int:
        return len({SIGNAL_FAMILIES[c] for c in WEIGHTS if float(row[c]) >= 0.5})

    out["signal_family_count"] = out.apply(family_count, axis=1)
    out["priority_band"] = pd.cut(
        out["priority_score"],
        bins=[-0.01, 39.99, 59.99, 79.99, 100],
        labels=["Low", "Moderate", "High", "Critical"],
    )
    out["reasons"] = out.apply(_reasons, axis=1)
    out = add_explanations(out)
    return out.sort_values(["priority_score", "signal_family_count", "TRANSACTION_AMOUNT"], ascending=[False, False, False])


def _reasons(row: pd.Series) -> str:
    labels = {
        "peer_amount": "high vs hierarchical peers",
        "near_duplicate": "near-duplicate vendor/amount pattern",
        "burst_activity": "same-day vendor burst",
        "rare_agency_mcc": "unusual merchant category for agency",
        "round_amount": "round-dollar amount",
        "weekend": "weekend transaction",
        "threshold_proximity": "near scenario review threshold",
        "unsupervised": "multivariate anomaly",
        "vendor_concentration": "high vendor concentration for agency",
        "vendor_cross_agency_reach": "vendor spans many agencies",
        "temporal_spend_spike": "vendor spend spike vs recent history",
        "new_vendor_for_agency": "new relationship in observed dataset",
    }
    reasons = [label for col, label in labels.items() if float(row[col]) >= 0.5]
    return "; ".join(reasons) if reasons else "no strong rule signal"


def capacity_simulation(scored: pd.DataFrame, thresholds=range(40, 91, 5)) -> pd.DataFrame:
    rows = []
    total = max(len(scored), 1)
    for threshold in thresholds:
        selected = scored[scored["priority_score"] >= threshold]
        rows.append(
            {
                "score_threshold": threshold,
                "alerts": len(selected),
                "alert_rate_pct": round(100 * len(selected) / total, 2),
                "multi_signal_alerts": int((selected["signal_count"] >= 2).sum()),
                "multi_family_alerts": int((selected["signal_family_count"] >= 3).sum()),
                "estimated_review_hours_at_12min_each": round(len(selected) * 12 / 60, 1),
            }
        )
    return pd.DataFrame(rows)


def agency_summary(scored: pd.DataFrame) -> pd.DataFrame:
    return (
        scored.groupby("AGENCY", dropna=False)
        .agg(
            transactions=("OBJECTID", "count"),
            spend=("TRANSACTION_AMOUNT", "sum"),
            avg_priority_score=("priority_score", "mean"),
            high_plus=("priority_score", lambda x: int((x >= 60).sum())),
            avg_signal_families=("signal_family_count", "mean"),
            max_vendor_concentration=("vendor_agency_spend_share", "max"),
        )
        .assign(high_plus_rate_pct=lambda d: 100 * d["high_plus"] / d["transactions"])
        .sort_values("high_plus", ascending=False)
        .reset_index()
    )
