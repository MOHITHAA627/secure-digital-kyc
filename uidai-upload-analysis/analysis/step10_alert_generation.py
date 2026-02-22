import pandas as pd

# -------- CONFIG --------
INPUT_FILE = "analysis/monthly_total_upload_TN.csv"
OUTPUT_FILE = "analysis/alert_status_TN.csv"

# -------- LOAD DATA --------
df = pd.read_csv(INPUT_FILE)

# -------- CALCULATE THRESHOLD --------
mean_upload = df["Total_Upload"].mean()
std_upload = df["Total_Upload"].std()

heavy_threshold = mean_upload + 2 * std_upload

# -------- ALERT FLAG LOGIC --------
def generate_alert(upload):
    if upload > heavy_threshold:
        return "HIGH LOAD ALERT"
    else:
        return "NORMAL"

df["Alert_Status"] = df["Total_Upload"].apply(generate_alert)

# -------- SAVE --------
df.to_csv(OUTPUT_FILE, index=False)

print("✅ Alert generation completed")
print("Heavy Threshold:", round(heavy_threshold, 2))
