import pandas as pd

print("\nSTEP 9D: DETECTING HEAVY UPLOAD MONTHS (MUMBAI SUBURBAN)\n")

# ------------------------------------------------
# LOAD MONTHLY AGGREGATED DATA
# ------------------------------------------------
df = pd.read_csv("analysis/monthly_total_upload_MH.csv")

# Convert month to datetime
df["month"] = pd.to_datetime(df["month"])

# ------------------------------------------------
# CALCULATE STATISTICS
# ------------------------------------------------
mean_upload = df["Total_Upload"].mean()
std_upload  = df["Total_Upload"].std()
threshold   = mean_upload + 2 * std_upload

print(f"Mean Upload     : {mean_upload:.2f}")
print(f"Std Deviation   : {std_upload:.2f}")
print(f"Heavy Threshold : {threshold:.2f}\n")

# ------------------------------------------------
# FLAG HEAVY MONTHS
# ------------------------------------------------
df["is_heavy"] = df["Total_Upload"] > threshold
heavy = df[df["is_heavy"] == True]

# ------------------------------------------------
# DISPLAY RESULTS
# ------------------------------------------------
print("--- HEAVY UPLOAD MONTHS (MUMBAI SUBURBAN) ---\n")

if heavy.empty:
    print("No heavy upload months detected.")
else:
    print(heavy[["month", "Total_Upload"]])

# ------------------------------------------------
# SAVE OUTPUT
# ------------------------------------------------
df.to_csv("analysis/heavy_upload_months_MH.csv", index=False)

print("\nSTEP 9D COMPLETED SUCCESSFULLY ✅")
