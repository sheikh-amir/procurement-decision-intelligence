"""Interactive management cockpit for Procurement Control Intelligence."""
from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path("data")

st.set_page_config(page_title="Procurement Control Intelligence", page_icon="PCI", layout="wide")
st.title("Procurement Control Intelligence")
st.caption("Explainable exception prioritization + capacity-constrained management decision support")

ranked_path = DATA / "processed_ranked_exceptions.csv"
frontier_path = DATA / "threshold_decision_frontier.csv"
decision_path = DATA / "management_decision.json"

if not ranked_path.exists():
    st.error("No processed data found. Run `python -m src.pipeline` first.")
    st.stop()

ranked = pd.read_csv(ranked_path, parse_dates=["TRANSACTION_DATE"])
frontier = pd.read_csv(frontier_path) if frontier_path.exists() else pd.DataFrame()
decision = json.loads(decision_path.read_text()) if decision_path.exists() else {}

page = st.sidebar.radio(
    "View",
    ["Executive decision", "Investigation queue", "Vendor relationships", "Data quality & governance"],
)

if page == "Executive decision":
    rec = decision.get("recommended_threshold", {})
    workload = decision.get("workload_risk", {})
    sensitivity = decision.get("weight_sensitivity", {})
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Transactions", f"{len(ranked):,}")
    c2.metric("Recommended threshold", rec.get("score_threshold", "n/a"))
    c3.metric("Selected alerts", rec.get("alerts", "n/a"))
    c4.metric("Backlog probability", f"{workload.get('backlog_probability_pct', 0)}%")
    c5.metric("Queue stability", sensitivity.get("mean_top_queue_jaccard", "n/a"))

    st.subheader("Management decision frontier")
    if not frontier.empty:
        fig = px.scatter(
            frontier,
            x="review_hours",
            y="proxy_risk_coverage_pct",
            size="avg_selected_score",
            hover_data=["score_threshold", "alerts", "multi_family_rate_pct"],
            labels={
                "review_hours": "Estimated review hours",
                "proxy_risk_coverage_pct": "Priority-score coverage (%)",
            },
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Priority-score coverage is a decision proxy, not a fraud-detection accuracy measure.")

    band = ranked["priority_band"].value_counts().rename_axis("band").reset_index(name="count")
    st.plotly_chart(px.bar(band, x="band", y="count", title="Queue by priority band"), use_container_width=True)

elif page == "Investigation queue":
    min_score = st.sidebar.slider("Minimum priority score", 0, 100, 60)
    agencies = ["All"] + sorted(ranked["AGENCY"].dropna().astype(str).unique().tolist())
    agency = st.sidebar.selectbox("Agency", agencies)
    q = ranked[ranked["priority_score"] >= min_score].copy()
    if agency != "All":
        q = q[q["AGENCY"] == agency]

    st.subheader(f"Ranked queue — {len(q):,} records")
    cols = [
        "TRANSACTION_DATE", "AGENCY", "VENDOR_NAME", "TRANSACTION_AMOUNT",
        "MCC_DESCRIPTION", "priority_score", "signal_family_count", "reasons",
        "top_score_contributors"
    ]
    st.dataframe(q[cols].head(500), use_container_width=True, hide_index=True)

    if len(q):
        selected_id = st.selectbox("Inspect OBJECTID", q["OBJECTID"].head(100).tolist())
        row = q[q["OBJECTID"] == selected_id].iloc[0]
        st.markdown("### Explainability card")
        st.write({
            "priority_score": float(row["priority_score"]),
            "priority_band": str(row["priority_band"]),
            "evidence_families": int(row["signal_family_count"]),
            "reason_codes": row["reasons"],
            "top_contributors": row["top_score_contributors"],
        })

elif page == "Vendor relationships":
    st.subheader("Vendor dependency and cross-agency reach")
    vendor = (
        ranked.groupby("VENDOR_NAME")
        .agg(
            total_spend=("TRANSACTION_AMOUNT", lambda s: s.abs().sum()),
            agencies=("AGENCY", "nunique"),
            transactions=("OBJECTID", "count"),
            avg_priority=("priority_score", "mean"),
            max_agency_share=("vendor_agency_spend_share", "max"),
        )
        .reset_index()
    )
    fig = px.scatter(
        vendor,
        x="agencies",
        y="max_agency_share",
        size="total_spend",
        hover_name="VENDOR_NAME",
        hover_data=["transactions", "avg_priority"],
        labels={"agencies": "Agency reach", "max_agency_share": "Maximum agency spend share"},
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("This view surfaces concentration and reach; it does not imply vendor misconduct.")

else:
    st.subheader("Governance controls")
    dq_path = DATA / "data_quality_report.csv"
    if dq_path.exists():
        dq = pd.read_csv(dq_path)
        st.dataframe(dq, use_container_width=True, hide_index=True)
    st.markdown(
        """
        **Control design**
        - Schema and quality gates before scoring
        - Versioned analytical configuration
        - Retained component signals and reason codes
        - Capacity-constrained threshold decision
        - Evidence-diversity metric separate from score
        - Explicit caveat: screening output is not a finding of misconduct
        """
    )
