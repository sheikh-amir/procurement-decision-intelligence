"""Configuration and governed analytical assumptions.

All thresholds below are portfolio-scenario settings, not claims about DC policy.
"""

MODEL_VERSION = "2.0.0"

API_URL = (
    "https://maps2.dcgis.dc.gov/dcgis/rest/services/"
    "DCGIS_DATA/Public_Service_WebMercator/MapServer/50/query"
)

EXPECTED_COLUMNS = {
    "AGENCY",
    "TRANSACTION_DATE",
    "TRANSACTION_AMOUNT",
    "VENDOR_NAME",
    "VENDOR_STATE_PROVINCE",
    "MCC_DESCRIPTION",
    "OBJECTID",
}

SCENARIO_REVIEW_AMOUNT = 5_000.0
MIN_PEER_SIZE = 8
DEFAULT_REVIEW_MINUTES = 12
DEFAULT_WEEKLY_REVIEW_HOURS = 40
DEFAULT_SLA_DAYS = 5

# The score deliberately mixes different evidence families rather than allowing
# a single statistical technique to dominate the queue.
WEIGHTS = {
    "peer_amount": 0.15,
    "near_duplicate": 0.13,
    "burst_activity": 0.09,
    "rare_agency_mcc": 0.08,
    "round_amount": 0.035,
    "weekend": 0.025,
    "threshold_proximity": 0.05,
    "unsupervised": 0.11,
    "vendor_concentration": 0.10,
    "vendor_cross_agency_reach": 0.07,
    "temporal_spend_spike": 0.10,
    "new_vendor_for_agency": 0.06,
}

SIGNAL_FAMILIES = {
    "peer_amount": "magnitude",
    "near_duplicate": "pattern",
    "burst_activity": "pattern",
    "rare_agency_mcc": "context",
    "round_amount": "amount_format",
    "weekend": "timing",
    "threshold_proximity": "scenario",
    "unsupervised": "multivariate",
    "vendor_concentration": "network",
    "vendor_cross_agency_reach": "network",
    "temporal_spend_spike": "temporal",
    "new_vendor_for_agency": "relationship",
}
