import pandas as pd

# Load one dataset from each type (TN only for inspection)
tn_enrol = pd.read_csv("data/Aadhaar Enrolment-TN.csv")
tn_bio   = pd.read_csv("data/Aadhaar Biometric-TN.csv")
tn_demo  = pd.read_csv("data/Aadhaar Demographic-TN.csv")

print("\n--- TN ENROLMENT COLUMNS ---")
print(tn_enrol.columns)

print("\n--- TN BIOMETRIC COLUMNS ---")
print(tn_bio.columns)

print("\n--- TN DEMOGRAPHIC COLUMNS ---")
print(tn_demo.columns)
