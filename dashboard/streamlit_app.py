"""Streamlit dashboard for retail demand exploration and forecast evaluation."""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.ml.baselines import walk_forward_baseline_backtest  # noqa: E402
from app.ml.forecasting import walk_forward_ml_backtest  # noqa: E402

DEFAULT_DATA = ROOT / "data" / "processed" / "m5" / "daily_demand.csv"

st.set_page_config(page_title="DecisionOS | Retail Planning", page_icon="📈", layout="wide")
st.title("DecisionOS — Retail Demand Planning")
st.caption("Explore historical retail demand and evaluate forecasts on rolling time-based holdouts.")

@st.cache_data(show_spinner="Loading prepared demand data...")
def load_demand(path: str, modified_time: float) -> pd.DataFrame:
    del modified_time  # included in cache key so a refreshed CSV is reloaded
    frame = pd.read_csv(path, parse_dates=["date"])
    required = {"date", "product_id", "market", "demand"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError("Prepared CSV is missing columns: " + ", ".join(missing))
    frame["product_id"] = frame["product_id"].astype(str)
    frame["market"] = frame["market"].astype(str)
    frame["demand"] = pd.to_numeric(frame["demand"], errors="coerce")
    frame = frame.dropna(subset=["date", "demand"])
    return frame.sort_values("date")

with st.sidebar:
    st.header("Data")
    data_path = st.text_input("Prepared demand CSV", value=str(DEFAULT_DATA))
    st.caption("Create this file with scripts/prepare_m5.py. Raw M5 files stay local and out of Git.")

path = Path(data_path).expanduser()
if not path.is_file():
    st.warning("Prepared demand data was not found. Run the preparation command below, then refresh this page.")
    st.code(
        'python scripts/prepare_m5.py --item-id "HOBBIES_1_001" --store-id "CA_1"',
        language="powershell",
    )
    st.stop()

try:
    data = load_demand(str(path.resolve()), path.stat().st_mtime)
except Exception as exc:
    st.error(f"Could not load prepared demand data: {exc}")
    st.stop()

if data.empty:
    st.error("The prepared demand CSV has no usable rows.")
    st.stop()

with st.sidebar:
    products = sorted(data["product_id"].unique().tolist())
    product_id = st.selectbox("Product", products)
    product_data = data.loc[data["product_id"] == product_id]
    markets = sorted(product_data["market"].unique().tolist())
    market = st.selectbox("Store / market", markets)
    horizon = st.selectbox("Forecast horizon (days)", [7, 14, 28], index=0)
    step = st.selectbox("Backtest step (days)", [7, 14, 28, 56], index=2)

series = data.loc[
    (data["product_id"] == product_id) & (data["market"] == market)
].sort_values("date")
if series.empty:
    st.error("No rows exist for this product/store combination.")
    st.stop()

total_units = float(series["demand"].sum())
avg_daily = float(series["demand"].mean())
last_date = series["date"].max()
previous_period = series.loc[series["date"] >= last_date - pd.Timedelta(days=27), "demand"]
previous_total = float(previous_period.sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Units sold in history", f"{total_units:,.0f}")
c2.metric("Average daily demand", f"{avg_daily:,.2f}")
c3.metric("Latest recorded date", last_date.strftime("%d %b %Y"))
c4.metric("Units in latest 28-day window", f"{previous_total:,.0f}")

st.subheader("Historical demand")
history = series.set_index("date")[["demand"]].rename(columns={"demand": "Units sold"})
st.line_chart(history, height=300)
st.caption("M5 records sales, not on-hand inventory. These charts describe historical sales, not stock availability.")

st.subheader("Forecast model evaluation")
st.write(
    "Run a rolling-origin backtest. Both models use the same selected product, store, "
    "forecast horizon, minimum training window, and step so the metrics are comparable."
)
run = st.button("Run forecast evaluation", type="primary")

if run:
    try:
        with st.spinner("Evaluating baseline and machine-learning forecasts..."):
            baseline_predictions, baseline_summary = walk_forward_baseline_backtest(
                data, product_id=product_id, market=market,
                horizon=int(horizon), min_train_days=56, step=int(step),
            )
            ml_predictions, ml_summary = walk_forward_ml_backtest(
                data, product_id=product_id, market=market,
                horizon=int(horizon), min_train_days=56, step=int(step),
            )

        metric_rows = [
            {
                "Model": "Last-value baseline",
                "MAE": baseline_summary["naive"]["mae"],
                "RMSE": baseline_summary["naive"]["rmse"],
                "WAPE (%)": baseline_summary["naive"]["wape_percent"],
            },
            {
                "Model": "Weekly seasonal-naive",
                "MAE": baseline_summary["seasonal_naive"]["mae"],
                "RMSE": baseline_summary["seasonal_naive"]["rmse"],
                "WAPE (%)": baseline_summary["seasonal_naive"]["wape_percent"],
            },
            {
                "Model": "HistGradientBoosting",
                "MAE": ml_summary["ml_model"]["mae"],
                "RMSE": ml_summary["ml_model"]["rmse"],
                "WAPE (%)": ml_summary["ml_model"]["wape_percent"],
            },
        ]
        metrics = pd.DataFrame(metric_rows).set_index("Model")
        st.dataframe(metrics.style.format("{:.3f}"), use_container_width=True)
        st.caption(
            f"Evaluation uses {baseline_summary['backtest_origins']} rolling origins "
            f"and {baseline_summary['forecasted_observations']} forecasted observations per model. "
            "Lower error is better; WAPE is undefined when total actual demand is zero."
        )

        baseline_chart = baseline_predictions[
            ["date", "actual", "naive_forecast", "seasonal_naive_forecast"]
        ].groupby("date", as_index=True).mean()
        ml_chart = ml_predictions[["date", "actual", "ml_forecast"]].groupby("date", as_index=True).mean()
        st.subheader("Backtest predictions by target date")
        st.write("Baseline forecasts")
        st.line_chart(baseline_chart.rename(columns={
            "actual": "Actual", "naive_forecast": "Last-value", "seasonal_naive_forecast": "Seasonal-naive"
        }))
        st.write("Machine-learning forecasts")
        st.line_chart(ml_chart.rename(columns={"actual": "Actual", "ml_forecast": "HistGradientBoosting"}))

        best_model = metrics["WAPE (%)"].dropna().idxmin() if metrics["WAPE (%)"].notna().any() else None
        if best_model:
            st.success(f"Lowest WAPE on this evaluation: {best_model}. This result applies only to the selected series and settings.")
        st.download_button(
            "Download baseline backtest predictions",
            baseline_predictions.to_csv(index=False).encode("utf-8"),
            file_name="decisionos_baseline_predictions.csv",
            mime="text/csv",
        )
        st.download_button(
            "Download ML backtest predictions",
            ml_predictions.to_csv(index=False).encode("utf-8"),
            file_name="decisionos_ml_predictions.csv",
            mime="text/csv",
        )
    except Exception as exc:
        st.error(f"Forecast evaluation failed: {exc}")
        st.info("Check that the selected product/store has enough history for the requested horizon.")

st.divider()
st.caption("DecisionOS MVP · M5 historical sales · Forecast evaluation is not a guarantee of future performance.")
