import pandas as pd

#Calculate daily  returns
def calculate_returns(price_matrix: pd.DataFrame) -> pd.DataFrame:
    
    if price_matrix.empty:
        raise ValueError("Price matrix is empty.")

    returns = price_matrix.pct_change()

    return returns

