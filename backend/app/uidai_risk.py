import pandas as pd
import os

# Load your alert status CSV
BASE = os.path.join(
    os.path.dirname(__file__),
    "../../uidai-upload-analysis/analysis"
)

# Build district risk map manually from your findings
DISTRICT_RISK = {
    "Chennai": {"flag": "NORMAL", "readiness": 0.72},
    "Tirupati": {"flag": "NORMAL", "readiness": 0.68},
    "Mumbai Suburban": {"flag": "HIGH", "readiness": 0.91},
    "Mumbai": {"flag": "HIGH", "readiness": 0.91},
    "Delhi": {"flag": "NORMAL", "readiness": 0.75},
    "Bangalore": {"flag": "NORMAL", "readiness": 0.70},
    "Hyderabad": {"flag": "NORMAL", "readiness": 0.68},
    "Kolkata": {"flag": "HIGH", "readiness": 0.85},

}

def get_district_risk_score(district: str) -> int:
    info = DISTRICT_RISK.get(district)
    if info is None:
        return 15  # unknown district = mild risk
    if info["flag"] == "HIGH":
        return 25  # high load district = higher fraud risk
    return 0       # normal district = no extra risk
