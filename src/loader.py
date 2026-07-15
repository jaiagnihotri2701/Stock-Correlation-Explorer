import zipfile

import pandas as pd

def _read_zip(zip_path: str) -> pd.DataFrame:

    dataframes = []

    with zipfile.ZipFile(zip_path, "r") as z:
        csv_files = sorted(
            [file for file in z.namelist() if file.endswith(".csv")]
        )

        if not csv_files:
            raise ValueError("No CSV files found in the zip archive.")
        
        for file in csv_files:
            with z.open(file) as f:
                
                df = pd.read_csv(f,keep_default_na=False)

                columns = {"Ticker","Date","Price"}

                if not columns.issubset(df.columns):
                    raise ValueError(f"Missing required columns in {file}. Expected columns: {columns}")
                
                df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

                if not columns.issubset(df.columns):
                    raise ValueError(f"Missing required columns in {file}. Expected columns: {columns}")
                
                dataframes.append(df)
    return pd.concat(dataframes, ignore_index=True) 

#Load stock data from a zip file and return a cleaned DataFrame.
def load_stock_data(zip_path: str) -> pd.DataFrame:

    df = _read_zip(zip_path)

    #using format mixed to handle different types of date inputs
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", errors="coerce")

    df = df.sort_values(["Date", "Ticker"], ignore_index=True)

    return df

