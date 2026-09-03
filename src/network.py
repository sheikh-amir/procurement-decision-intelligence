"""Vendor-agency relationship and concentration features."""
from __future__ import annotations

import numpy as np
import pandas as pd


def add_network_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add graph-inspired vendor relationship risk features without opaque graph ML.

    The public dataset does not contain a full procurement process graph, so the
    module only derives defensible relationship features from observed agency-vendor edges.
    """
    out = df.copy()
    amount_abs = out["TRANSACTION_AMOUNT"].abs()

    edge_spend = out.groupby(["AGENCY", "VENDOR_NAME"], dropna=False)["TRANSACTION_AMOUNT"].transform(
        lambda s: s.abs().sum()
    )
    agency_spend = out.groupby("AGENCY", dropna=False)["TRANSACTION_AMOUNT"].transform(
        lambda s: s.abs().sum()
    )
    share = (edge_spend / agency_spend.replace(0, np.nan)).fillna(0).clip(0, 1)
    # Concentration becomes strong when one vendor is >25% of agency spend.
    out["vendor_concentration"] = (share / 0.25).clip(0, 1)
    out["vendor_agency_spend_share"] = share

    vendor_agency_count = out.groupby("VENDOR_NAME", dropna=False)["AGENCY"].transform("nunique")
    max_reach = max(int(vendor_agency_count.max()), 1)
    out["vendor_cross_agency_reach"] = (
        np.log1p(vendor_agency_count) / np.log1p(max_reach)
    ).clip(0, 1)
    out["vendor_agency_count"] = vendor_agency_count.astype(int)

    out["vendor_transaction_count"] = out.groupby("VENDOR_NAME", dropna=False)["OBJECTID"].transform("count")
    out["agency_vendor_transaction_count"] = out.groupby(
        ["AGENCY", "VENDOR_NAME"], dropna=False
    )["OBJECTID"].transform("count")
    return out
