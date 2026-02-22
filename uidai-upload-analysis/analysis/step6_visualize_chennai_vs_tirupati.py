import pandas as pd
import matplotlib.pyplot as plt

print("\nSTEP 6: VISUALIZING CHENNAI VS TIRUPATI\n")

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------
chennai = pd.read_csv("analysis/monthly_total_upload_TN.csv")
tirupati = pd.read_csv("analysis/monthly_total_upload_AP.csv")

chennai["month"] = pd.to_datetime(chennai["month"])
tirupati["month"] = pd.to_datetime(tirupati["month"])

chennai = chennai.sort_values("month")
tirupati = tirupati.sort_values("month")

# ------------------------------------------------
# VISUAL 1: MONTHLY TREND (LINE PLOT)
# ------------------------------------------------
print("Showing Plot 1: Monthly Trend")

plt.figure()
plt.plot(chennai["month"], chennai["Total_Upload"], marker="o", label="Chennai")
plt.plot(tirupati["month"], tirupati["Total_Upload"], marker="o", label="Tirupati")

plt.xlabel("Month")
plt.ylabel("Total Aadhaar Upload")
plt.title("Monthly Aadhaar Upload Trend")
plt.legend()
plt.grid(True)

plt.show()

# ------------------------------------------------
# VISUAL 2: AVERAGE MONTHLY UPLOAD (BAR CHART)
# ------------------------------------------------
print("Showing Plot 2: Average Monthly Load")

avg_chennai = chennai["Total_Upload"].mean()
avg_tirupati = tirupati["Total_Upload"].mean()

plt.figure()
plt.bar(["Chennai", "Tirupati"], [avg_chennai, avg_tirupati])

plt.xlabel("District")
plt.ylabel("Average Monthly Aadhaar Upload")
plt.title("Average Monthly Aadhaar Upload Comparison")
plt.grid(axis="y")

plt.show()

print("\nSTEP 6 COMPLETED SUCCESSFULLY ✅")

# ------------------------------------------------
# VISUAL 3: TREND WITH HEAVY UPLOAD THRESHOLD
# ------------------------------------------------
print("Showing Plot 3: Trend with Threshold")

# --- Chennai threshold ---
mean_chennai = chennai["Total_Upload"].mean()
std_chennai = chennai["Total_Upload"].std()
threshold_chennai = mean_chennai + 2 * std_chennai

plt.figure()
plt.plot(chennai["month"], chennai["Total_Upload"], marker="o", label="Chennai Upload")
plt.axhline(threshold_chennai, linestyle="--", label="Chennai Heavy Threshold")

plt.xlabel("Month")
plt.ylabel("Total Aadhaar Upload")
plt.title("Chennai: Monthly Upload vs Heavy Threshold")
plt.legend()
plt.grid(True)

plt.show()

# --- Tirupati threshold ---
mean_tirupati = tirupati["Total_Upload"].mean()
std_tirupati = tirupati["Total_Upload"].std()
threshold_tirupati = mean_tirupati + 2 * std_tirupati

plt.figure()
plt.plot(tirupati["month"], tirupati["Total_Upload"], marker="o", label="Tirupati Upload")
plt.axhline(threshold_tirupati, linestyle="--", label="Tirupati Heavy Threshold")

plt.xlabel("Month")
plt.ylabel("Total Aadhaar Upload")
plt.title("Tirupati: Monthly Upload vs Heavy Threshold")
plt.legend()
plt.grid(True)

plt.show()

print("STEP 6 (PLOT 3) COMPLETED ✅")
