import pandas as pd

print("\nSTEP 4: DETECTING HEAVY UPLOAD MONTHS (CHENNAI)\n")

# ------------------------------------------------
# LOAD STEP 3 OUTPUT
# ------------------------------------------------
df = pd.read_csv("analysis/monthly_total_upload_TN.csv")

# Convert month column to datetime
df["month"] = pd.to_datetime(df["month"])

# ------------------------------------------------
# CALCULATE STATISTICS
# ------------------------------------------------
mean_upload = df["Total_Upload"].mean()
std_upload = df["Total_Upload"].std()
threshold = mean_upload + 2 * std_upload

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
df.to_csv("analysis/heavy_upload_months_TN.csv", index=False)

# ------------------------------------------------
# DISPLAY HEAVY MONTHS
# ------------------------------------------------
heavy_months = df[df["is_heavy"] == True]

print("--- HEAVY UPLOAD MONTHS (TN) ---\n")

if heavy_months.empty:
    print("No heavy upload months detected.")
else:
    print(heavy_months[["month", "Total_Upload"]])

print("\nSTEP 4 COMPLETED SUCCESSFULLY ✅")
