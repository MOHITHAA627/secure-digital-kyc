import pandas as pd

print("\nSTEP 7: SENSITIVITY ANALYSIS (MEAN + 1.5σ)\n")

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------
chennai = pd.read_csv("analysis/monthly_total_upload_TN.csv")
tirupati = pd.read_csv("analysis/monthly_total_upload_AP.csv")

chennai["month"] = pd.to_datetime(chennai["month"])
tirupati["month"] = pd.to_datetime(tirupati["month"])

# ------------------------------------------------
# FUNCTION TO FLAG SENSITIVE HEAVY MONTHS
# ------------------------------------------------
def detect_sensitive_heavy(df, label):
    mean_val = df["Total_Upload"].mean()
    std_val = df["Total_Upload"].std()
    threshold = mean_val + 1.5 * std_val

    df = df.copy()
    df["sensitive_heavy"] = df["Total_Upload"] > threshold

    print(f"\n{label}")
    print(f"Mean       : {mean_val:.2f}")
    print(f"Std Dev    : {std_val:.2f}")
    print(f"Threshold  : {threshold:.2f}")

    flagged = df[df["sensitive_heavy"] == True]

    if flagged.empty:
        print("No sensitive heavy months detected.")
    else:
        print("Sensitive heavy months:")
        print(flagged[["month", "Total_Upload"]])

    return df

# ------------------------------------------------
# APPLY TO BOTH DISTRICTS
# ------------------------------------------------
chennai_result = detect_sensitive_heavy(chennai, "CHENNAI (Sensitive Threshold)")
tirupati_result = detect_sensitive_heavy(tirupati, "TIRUPATI (Sensitive Threshold)")

# ------------------------------------------------
# SAVE OUTPUTS
# ------------------------------------------------
chennai_result.to_csv("analysis/sensitive_heavy_months_TN.csv", index=False)
tirupati_result.to_csv("analysis/sensitive_heavy_months_AP.csv", index=False)

print("\nSTEP 7 COMPLETED SUCCESSFULLY ✅")
