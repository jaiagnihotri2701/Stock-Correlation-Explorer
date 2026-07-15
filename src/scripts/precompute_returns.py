from src.pipeline import build_returns


def main():
    returns = build_returns("data/stock_data.zip")
    returns.to_parquet("data/returns.parquet")
    print(f"Saved returns.parquet: {returns.shape}")


if __name__ == "__main__":
    main()