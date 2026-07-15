import logging

import pandas as pd

from src.transformer import validate_and_clean_data


def sample_data():
    """
    4 distinct (Ticker, Date) rows, no duplicates, no missing values.
    Individual tests add exactly the one issue they want to test on
    top of this clean base.
    """
    return pd.DataFrame(
        {
            "Ticker": ["A", "B", "C", "D"],
            "Date": ["2020-01-01"] * 4,
            "Price": [10.0, 20.0, 30.0, 40.0],
        }
    )


def test_duplicate_rows_removed():
    df = sample_data()

    # Add one duplicate of row A on top of the clean base.
    duplicate_row = df.iloc[[0]]
    df = pd.concat([df, duplicate_row], ignore_index=True)

    cleaned_df = validate_and_clean_data(df)

    assert len(cleaned_df) == 4
    assert cleaned_df.duplicated(subset=["Ticker", "Date"]).sum() == 0


def test_missing_prices_removed():
    df = sample_data()
    df.loc[2, "Price"] = None

    cleaned_df = validate_and_clean_data(df)

    assert cleaned_df["Price"].isna().sum() == 0
    assert len(cleaned_df) == 3


def test_blank_ticker_removed_but_literal_na_ticker_kept():
    df = sample_data()
    df.loc[2, "Ticker"] = ""       # blank ticker, should be dropped
    df.loc[3, "Ticker"] = "NA"     # real ticker symbol, must be kept

    cleaned_df = validate_and_clean_data(df)

    assert "" not in cleaned_df["Ticker"].values
    assert "NA" in cleaned_df["Ticker"].values
    assert len(cleaned_df) == 3


def test_clean_data_passes_through_unchanged():
    df = sample_data()

    cleaned_df = validate_and_clean_data(df)

    assert len(cleaned_df) == len(df)


def test_logs_error_when_too_many_rows_removed(caplog):
    df = sample_data()

    # Remove 2 out of 4 rows (>1%)
    df.loc[1, "Price"] = None
    df.loc[2, "Price"] = None

    with caplog.at_level(logging.ERROR):
        validate_and_clean_data(df)

    assert "Too many rows removed" in caplog.text


def test_no_error_logged_when_no_rows_removed(caplog):
    df = sample_data()

    with caplog.at_level(logging.ERROR):
        validate_and_clean_data(df)

    assert "Too many rows removed" not in caplog.text