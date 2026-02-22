import pandas as pd

print("\nSTEP 5B: DETECTING HEAVY UPLOAD MONTHS (TIRUPATI)\n")

# ------------------------------------------------
# LOAD MONTHLY AGGREGATED DATA (AP)
# ------------------------------------------------
df = pd.read_csv("analysis/monthly_total_upload_AP.csv")

# Convert month to datetime
df["month"] = pd.to_datetime(df["month"])

# ------------------------------------------------
# CALCULATE STATISTICS
# ------------------------------------------------
mean_upload = df["Total_Upload"].mean()
std_upload  = df["Total_Upload"].std()
threshold  = mean_upload + 2 * std_upload

print(f"Mean Upload     : {mean_upload:.2f}")
print(f"Std Deviation   : {std_upload:.2f}")
print(f"Heavy Threshold : {threshold:.2f}\n")

# ------------------------------------------------
# FLAG HEAVY MONTHS
# ------------------------------------------------
df["is_heavy"] = df["Total_Upload"] > threshold

# ------------------------------------------------
# SAVE RESULTS
# ------------------------------------------------
df.to_csv("analysis/heavy_upload_months_AP.csv", index=False)

# ------------------------------------------------
# DISPLAY HEAVY MONTHS
# ------------------------------------------------
heavy = df[df["is_heavy"] == True]

print("--- HEAVY UPLOAD MONTHS (TIRUPATI) ---\n")

if heavy.empty:
    print("No heavy upload months detected.")
else:
    print(heavy[["month", "Total_Upload"]])

print("\nSTEP 5B COMPLETED SUCCESSFULLY ✅")
