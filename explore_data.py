#inferences
#900 csv files, approximately 3.5 years of data 
#5000 stocks
#every trading day contains all stocks
#no duplicate stocks per day
#there are 6 missing prices on 20220530 (UJK,WJX,TVT,PDY,DAF,BKRP)
#we also know that date appears in 2 formats 2020-01-01 and 5/30/2022

import zipfile
import pandas as pd

ZIP_PATH = "data/stock_data.zip"


def validate_date_matches_filename(file, df):
    """
    Check that the date in the filename matches the date stored in the CSV.
    """

    filename = file.split("/")[-1]              # e.g. 20200101.csv
    filename_date = filename.replace(".csv", "")

    expected_date = pd.to_datetime(filename_date, format="%Y%m%d")
    actual_dates = pd.to_datetime(df["Date"], format="mixed")

    unique_dates = actual_dates.unique()

    if len(unique_dates) != 1 or unique_dates[0] != expected_date:
        print(f"\n❌ Date mismatch in {file}")
        print(f"Expected: {expected_date.date()}")
        print(f"Found: {[d.date() for d in unique_dates]}")


def validate_missing_prices(file, df, missing_price_files):
    """
    Check for missing prices.
    """

    missing_rows = df[df["Price"].isna()]

    if not missing_rows.empty:
        missing_price_files.append((file, missing_rows))


def validate_duplicate_tickers(file, df, duplicate_ticker_files):
    """
    Check for duplicate tickers within a trading day.
    """

    if df["Ticker"].duplicated().any():
        duplicate_ticker_files.append(file)


def validate_dataset(file, df, missing_price_files, duplicate_ticker_files):
    """
    Run all validation checks.
    """

    validate_date_matches_filename(file, df)
    validate_missing_prices(file, df, missing_price_files)
    validate_duplicate_tickers(file, df, duplicate_ticker_files)


def main():

    unique_tickers = set()
    row_counts = []

    missing_price_files = []
    duplicate_ticker_files = []

    with zipfile.ZipFile(ZIP_PATH, "r") as z:

        csv_files = sorted(
            [file for file in z.namelist() if file.endswith(".csv")]
        )

        print(f"Number of CSV files: {len(csv_files)}")

        for i, file in enumerate(csv_files):

            with z.open(file) as f:
                df = pd.read_csv(f)

            # Run validation checks
            validate_dataset(
                file,
                df,
                missing_price_files,
                duplicate_ticker_files
            )

            # Collect statistics
            row_counts.append(len(df))
            unique_tickers.update(df["Ticker"])

            # Print information for the first file only
            if i == 0:
                print("\nFirst few rows:")
                print(df.head())

                print("\nColumns:")
                print(df.columns.tolist())

                print("\nData info:")
                df.info()

                print("\nUnique dates in first file:")
                print(df["Date"].unique())

    print("\n========== DATASET SUMMARY ==========")
    print(f"Processed files      : {len(csv_files)}")
    print(f"Unique tickers       : {len(unique_tickers)}")
    print(f"Minimum rows/file    : {min(row_counts)}")
    print(f"Maximum rows/file    : {max(row_counts)}")

    if missing_price_files:
        print(f"\nFiles with missing prices ({len(missing_price_files)}):")

        for file, rows in missing_price_files:
            print(f"\nMissing prices in {file}:")
            print(rows)

    else:
        print("\n✓ No missing prices found.")

    if duplicate_ticker_files:
        print(f"\nFiles with duplicate tickers ({len(duplicate_ticker_files)}):")
        print(duplicate_ticker_files)

    else:
        print("✓ No duplicate tickers found.")


if __name__ == "__main__":
    main()