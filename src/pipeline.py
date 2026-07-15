import pandas as pd
 
from src.loader import load_stock_data
from src.transformer import transform_to_price_matrix, validate_and_clean_data
from src.returns import calculate_returns
 
#executes full pipeline to load data and calculate return matrix 
def build_returns(zip_path: str) -> pd.DataFrame:
    df = load_stock_data(zip_path)
    df = validate_and_clean_data(df)
    price_matrix = transform_to_price_matrix(df)
    return calculate_returns(price_matrix)
