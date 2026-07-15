import zipfile

import pandas as pd
import pytest

from src.loader import load_stock_data


# ---------------------------------------------------------
# Failure paths
# ---------------------------------------------------------

def test_no_csv_files(tmp_path):
    """
    Test that loading a ZIP archive with no CSV files raises an error.
    """
    zip_path = tmp_path / "empty.zip"

    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("README.txt", "No CSV files here.")

    with pytest.raises(ValueError, match="No CSV files found"):
        load_stock_data(zip_path)


def test_missing_required_columns(tmp_path):
    """
    Test that a CSV missing the Price column raises an error.
    """
    csv_data = (
        "Ticker,Date,SecPrice\n"
        "A,2020-01-01,20.0\n"
    )

    zip_path = tmp_path / "bad_schema.zip"

    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("stock_data.csv", csv_data)

    with pytest.raises(ValueError, match="Missing required columns"):
        load_stock_data(zip_path)


# ---------------------------------------------------------
# Happy path
# ---------------------------------------------------------

def test_successful_load(tmp_path):
    """
    A well-formed zip should load with the correct columns, row count,
    and dtypes (Date as datetime, Price as numeric).
    """
    csv_data = (
        "Ticker,Date,Price\n"
        "AAPL,2020-01-02,150.0\n"
        "MSFT,2020-01-02,300.0\n"
        "AAPL,2020-01-03,151.0\n"
    )

    zip_path = tmp_path / "good.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("stock_data.csv", csv_data)

    df = load_stock_data(zip_path)

    assert list(df.columns) == ["Ticker", "Date", "Price"]
    assert len(df) == 3
    assert pd.api.types.is_datetime64_any_dtype(df["Date"])
    assert pd.api.types.is_numeric_dtype(df["Price"])


# ---------------------------------------------------------
# "NA" ticker edge case
# ---------------------------------------------------------

def test_na_ticker_preserved_not_treated_as_null(tmp_path):
    """
    keep_default_na=False must preserve a literal 'NA' ticker symbol
    rather than pandas silently converting it to a missing value.
    """
    csv_data = "Ticker,Date,Price\nNA,2020-01-02,10.0\n"

    zip_path = tmp_path / "na_ticker.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("stock_data.csv", csv_data)

    df = load_stock_data(zip_path)

    assert len(df) == 1
    assert df.loc[0, "Ticker"] == "NA"
    assert pd.notna(df.loc[0, "Ticker"])