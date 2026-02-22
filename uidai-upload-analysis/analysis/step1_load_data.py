import os
import pandas as pd

print("SCRIPT STARTED\n")

data_path = "data"

print("FILES INSIDE data FOLDER:\n")
for file in os.listdir(data_path):
    print(repr(file))

print("\n--- Loading CSV files ---\n")

# ---- Tamil Nadu (Chennai) ----
tn_enrol = pd.read_csv("data/Aadhaar Enrolment-TN.csv")
tn_bio   = pd.read_csv("data/Aadhaar Biometric-TN.csv")
tn_demo  = pd.read_csv("data/Aadhaar Demographic-TN.csv")

# ---- Andhra Pradesh (Tirupati) ----
ap_enrol = pd.read_csv("data/Aadhaar Monthly Enrolment-AP.csv")
ap_bio   = pd.read_csv("data/Aadhaar Biometric-AP.csv")
ap_demo  = pd.read_csv("data/Aadhaar Demographic -AP.csv")

print("Tamil Nadu Enrolment shape:", tn_enrol.shape)
print("Tamil Nadu Biometric shape:", tn_bio.shape)
print("Tamil Nadu Demographic shape:", tn_demo.shape)

print("Andhra Pradesh Enrolment shape:", ap_enrol.shape)
print("Andhra Pradesh Biometric shape:", ap_bio.shape)
print("Andhra Pradesh Demographic shape:", ap_demo.shape)
