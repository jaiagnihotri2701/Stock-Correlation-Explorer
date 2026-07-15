import logging

import pandas as pd

logger = logging.getLogger(__name__)

def validate_and_clean_data(df: pd.DataFrame) -> pd.DataFrame:
 
    original_rows = len(df)

    # Remove rows with missing prices and dates
    df = df.dropna(subset=["Price", "Date"])

    # Remove rows with blank tickers
    df = df[df["Ticker"].astype(str).str.strip() != ""]

    # Remove duplicate (Ticker, Date) pairs.
    df = df.drop_duplicates(subset=["Ticker", "Date"])

    removed_rows = original_rows - len(df)

    logger.info(f"Removed {removed_rows} rows during data cleaning.")

    if removed_rows > 0.01 * original_rows:
        logger.error(
            "Too many rows removed during data cleaning: "
            f"{removed_rows} ({removed_rows / original_rows:.2%})"
        )

    return df

#transforming to a pivoted price matrix
def transform_to_price_matrix(df: pd.DataFrame) -> pd.DataFrame:

    required_columns = {"Ticker", "Date", "Price"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Missing required columns. Expected columns: {required_columns}"
        )

    price_matrix = df.pivot(
        index="Date",
        columns="Ticker",
        values="Price",
    )

    return price_matrix