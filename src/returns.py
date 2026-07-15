#this function will take in a df of prices and will return a df of returns calculations 
import pandas as pd


def calculate_returns(price_matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily percentage returns from a price matrix.
    """

    if price_matrix.empty:
        raise ValueError("Price matrix is empty.")

    returns = price_matrix.pct_change()

    return returns

