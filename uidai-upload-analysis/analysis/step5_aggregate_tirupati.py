import pandas as pd

print("\nSTEP 5A: AGGREGATING UIDAI DATA (TIRUPATI)\n")

# ------------------------------------------------
# LOAD ANDHRA PRADESH DATA
# ------------------------------------------------
enrol = pd.read_csv("data/Aadhaar Monthly Enrolment-AP.csv")
bio   = pd.read_csv("data/Aadhaar Biometric-AP.csv")
demo  = pd.read_csv("data/Aadhaar Demographic -AP.csv")

# ------------------------------------------------
# CONVERT DATE COLUMN (INDIAN FORMAT SAFE)
# ------------------------------------------------
enrol["date"] = pd.to_datetime(enrol["date"], dayfirst=True, errors="coerce")
bio["date"]   = pd.to_datetime(bio["date"], dayfirst=True, errors="coerce")
demo["date"]  = pd.to_datetime(demo["date"], dayfirst=True, errors="coerce")

# ------------------------------------------------
# CREATE MONTH COLUMN
# ------------------------------------------------
enrol["month"] = enrol["date"].dt.to_period("M").astype(str)
bio["month"]   = bio["date"].dt.to_period("M").astype(str)
demo["month"]  = demo["date"].dt.to_period("M").astype(str)

# ------------------------------------------------
# CREATE TOTAL COUNTS
# ------------------------------------------------
enrol["enrolment_total"] = (
    enrol["age_0_5"]
    + enrol["age_5_17"]
    + enrol["age_18_greater"]
)

bio["biometric_total"] = (
    bio["bio_age_5_17"]
    + bio["bio_age_17_"]
)

demo["demographic_total"] = (
    demo["demo_age_5_17"]
    + demo["demo_age_17_"]
)

# ------------------------------------------------
# AGGREGATE MONTHLY (DISTRICT LEVEL)
# ------------------------------------------------
enrol_m = enrol.groupby(
    ["state", "district", "month"]
)["enrolment_total"].sum().reset_index()

bio_m = bio.groupby(
    ["state", "district", "month"]
)["biometric_total"].sum().reset_index()

demo_m = demo.groupby(
    ["state", "district", "month"]
)["demographic_total"].sum().reset_index()

# ------------------------------------------------
# MERGE & COMPUTE TOTAL UPLOAD
# ------------------------------------------------
merged = enrol_m.merge(bio_m, on=["state", "district", "month"])
merged = merged.merge(demo_m, on=["state", "district", "month"])

merged["Total_Upload"] = (
    merged["enrolment_total"]
    + merged["biometric_total"]
    + merged["demographic_total"]
)

# ------------------------------------------------
# SAVE OUTPUT
# ------------------------------------------------
merged.to_csv("analysis/monthly_total_upload_AP.csv", index=False)

print("--- MONTHLY TOTAL UPLOAD (TIRUPATI SAMPLE) ---\n")
print(merged.head())

print("\nSTEP 5A COMPLETED SUCCESSFULLY ✅")
