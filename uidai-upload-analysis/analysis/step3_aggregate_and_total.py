import pandas as pd

print("\nSTEP 3: AGGREGATING UIDAI DATA (TAMIL NADU)\n")

# ------------------------------------------------
# LOAD TAMIL NADU DATA
# ------------------------------------------------
enrol = pd.read_csv("data/Aadhaar Enrolment-TN.csv")
bio   = pd.read_csv("data/Aadhaar Biometric-TN.csv")
demo  = pd.read_csv("data/Aadhaar Demographic-TN.csv")

# ------------------------------------------------
# CONVERT DATE COLUMN (DD-MM-YYYY SAFE)
# ------------------------------------------------
enrol["date"] = pd.to_datetime(enrol["date"], dayfirst=True, errors="coerce")
bio["date"]   = pd.to_datetime(bio["date"], dayfirst=True, errors="coerce")
demo["date"]  = pd.to_datetime(demo["date"], dayfirst=True, errors="coerce")

# ------------------------------------------------
# CREATE MONTH COLUMN (YYYY-MM)
# ------------------------------------------------
enrol["month"] = enrol["date"].dt.to_period("M").astype(str)
bio["month"]   = bio["date"].dt.to_period("M").astype(str)
demo["month"]  = demo["date"].dt.to_period("M").astype(str)

# ------------------------------------------------
# CREATE TOTAL COUNTS FROM AGE COLUMNS
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
# AGGREGATE DAILY → MONTHLY
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
merged.to_csv("analysis/monthly_total_upload_TN.csv", index=False)

print("\n--- MONTHLY TOTAL UPLOAD (TN SAMPLE) ---\n")
print(merged.head())

print("\nSTEP 3 COMPLETED SUCCESSFULLY ✅")
