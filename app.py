from pathlib import Path

import streamlit as st
import pandas as pd

pd.set_option("future.infer_string", False)

import plotly.express as px

from src.pipeline import build_returns
from src.correlation import calculate_correlation_matrix

MAX_STOCKS = 100

# Cache preprocessing pipeline
@st.cache_data
def load_pipeline():
    parquet_path = Path("data/returns.parquet")

    if parquet_path.exists():
        return pd.read_parquet(parquet_path)

    returns = build_returns("data/stock_data.zip")
    parquet_path.parent.mkdir(exist_ok=True)
    returns.to_parquet(parquet_path)
    return returns

# Page
st.set_page_config(
    page_title="Stock Correlation Explorer",
    layout="wide",
)

st.title("📈 Stock Correlation Explorer")

st.write(
    """
    Explore stock correlations for a selected trading date.

    • Choose the correlation window (10–120 trading days).

    • Select **1 stock** to view its Top 20 correlated stocks.

    • Select **2–100 stocks** to generate a correlation heatmap.
    """
)


# Load data
with st.spinner("Loading stock data..."):
    returns = load_pipeline()


# Sidebar Inputs
st.sidebar.header("Input")

window = st.sidebar.selectbox(
    "Correlation Window (Trading Days)",
    options=[10, 15, 20, 30, 60, 120],
    index=2,
)

valid_dates = returns.index[window - 1:]

date_options = [d.strftime("%Y-%m-%d") for d in valid_dates]

selected_date_str = st.sidebar.selectbox(
    "Trading Date",
    options=date_options,
)

selected_date = pd.Timestamp(selected_date_str)

selected_stocks = st.sidebar.multiselect(
    "Select Stocks",
    options=sorted(returns.columns.tolist()),
    placeholder="Search stocks...",
)


# Analyze
if st.sidebar.button("Analyze"):

    if len(selected_stocks) == 0:
        st.warning("Please select at least one stock.")
        st.stop()

    if len(selected_stocks) > MAX_STOCKS:
        st.error(f"Please select at most {MAX_STOCKS} stocks.")
        st.stop()

    # ONE STOCK
    if len(selected_stocks) == 1:

        stock = selected_stocks[0]

        with st.spinner("Computing correlations..."):

            # For single-stock case corrwith() is used instead of building a full
            # NxN matrix it computes 1-vs-all correlations directly (much cheaper
            # than calculate_correlation_matrix's full corr() call).
            end = returns.index.get_loc(selected_date)
            start = end - window + 1
            window_returns = returns.iloc[start : end + 1]

            correlations = (
                window_returns.corrwith(window_returns[stock])
                .drop(stock)
                .dropna()
            )

        if correlations.empty:
            st.warning(
                f"{stock} doesn't have enough trading history in this "
                "window to compute correlations."
            )
            st.stop()

        correlations = correlations.sort_values(ascending=False).head(20)

        result = correlations.reset_index()
        result.columns = ["Ticker", "Correlation"]

        st.subheader(
            f"Top 20 Correlated Stocks with {stock}"
        )

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True,
        )

    # HEATMAP
    else:

        with st.spinner("Computing correlations..."):

            corr_matrix = calculate_correlation_matrix(
                returns,
                selected_date,
                window=window,
                tickers=selected_stocks,
            )

        st.subheader("Correlation Heatmap")

        fig = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
        )

        fig.update_layout(
            xaxis_title="Stocks",
            yaxis_title="Stocks",
            height=700,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

        st.subheader("Correlation Matrix")

        st.dataframe(
            corr_matrix.round(3),
            use_container_width=True,
        )