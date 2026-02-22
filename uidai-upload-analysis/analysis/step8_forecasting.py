import pandas as pd

print("\nSTEP 8: SIMPLE FORECASTING (MOVING AVERAGE)\n")

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
# FUNCTION TO FORECAST NEXT N MONTHS
# ------------------------------------------------
def forecast_next_months(df, label, window=3, periods=3):
    df = df.copy()
    df["rolling_avg"] = df["Total_Upload"].rolling(window=window).mean()

    last_avg = df["rolling_avg"].iloc[-1]
    last_month = df["month"].iloc[-1]

    future_months = pd.date_range(
        start=last_month + pd.offsets.MonthBegin(1),
        periods=periods,
        freq="MS"
    )

    forecast_df = pd.DataFrame({
        "month": future_months,
        "forecast_Total_Upload": [last_avg] * periods
    })

    print(f"\n{label}")
    print("Forecasted next months:")
    print(forecast_df)

    return forecast_df

# ------------------------------------------------
# APPLY FORECASTING
# ------------------------------------------------
forecast_chennai = forecast_next_months(chennai, "CHENNAI FORECAST")
forecast_tirupati = forecast_next_months(tirupati, "TIRUPATI FORECAST")

# ------------------------------------------------
# SAVE OUTPUTS
# ------------------------------------------------
forecast_chennai.to_csv("analysis/forecast_chennai.csv", index=False)
forecast_tirupati.to_csv("analysis/forecast_tirupati.csv", index=False)

print("\nSTEP 8 COMPLETED SUCCESSFULLY ✅")
