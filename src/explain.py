"""Transaction-level explainability and evidence-diversity diagnostics."""
from __future__ import annotations

import pandas as pd

from .config import SIGNAL_FAMILIES, WEIGHTS


def add_explanations(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()

    def explain(row: pd.Series) -> str:
        contributions = []
        for signal, weight in WEIGHTS.items():
            value = float(row.get(signal, 0.0))
            contributions.append((value * weight, signal, value))
        contributions.sort(reverse=True)
        parts = [f"{signal}={value:.2f}" for contrib, signal, value in contributions[:4] if contrib > 0]
        return " | ".join(parts) if parts else "no material contribution"

    def family_count(row: pd.Series) -> int:
        families = {
            SIGNAL_FAMILIES[s]
            for s in WEIGHTS
            if float(row.get(s, 0.0)) >= 0.5
        }
        return len(families)

    out["top_score_contributors"] = out.apply(explain, axis=1)
    out["signal_family_count"] = out.apply(family_count, axis=1)
    # Confidence is evidence diversity, not probability of wrongdoing.
    out["evidence_confidence"] = (out["signal_family_count"] / 6).clip(0, 1).round(3)
    return out
