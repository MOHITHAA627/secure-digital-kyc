import pandas as pd

# -------- CONFIG --------
INPUT_FILE = "analysis/monthly_total_upload_TN.csv"
OUTPUT_FILE = "analysis/resource_priority_TN.csv"

# -------- LOAD DATA --------
df = pd.read_csv(INPUT_FILE)

# -------- METRICS --------
mean_upload = df["Total_Upload"].mean()
std_upload = df["Total_Upload"].std()

heavy_threshold = mean_upload + 2 * std_upload
readiness_index = mean_upload / heavy_threshold

# -------- PRIORITY LOGIC --------
if readiness_index < 0.5:
    priority = "LOW"
elif readiness_index < 0.75:
    priority = "MEDIUM"
else:
    priority = "HIGH"

# -------- OUTPUT --------
summary = pd.DataFrame({
    "Mean_Upload": [round(mean_upload, 2)],
    "Heavy_Threshold": [round(heavy_threshold, 2)],
    "Readiness_Index": [round(readiness_index, 3)],
    "Resource_Priority": [priority]
})

summary.to_csv(OUTPUT_FILE, index=False)

print("✅ Resource priority assessment completed")
print(summary)
