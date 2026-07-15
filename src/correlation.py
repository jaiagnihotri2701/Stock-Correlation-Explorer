import pandas as pd

DEFAULT_WINDOW = 20


def calculate_correlation_matrix(
    returns: pd.DataFrame,
    date: str | pd.Timestamp,
    window: int = DEFAULT_WINDOW,
    tickers: list[str] | None = None,
) -> pd.DataFrame:
    """
    Calculate the rolling correlation matrix for a given date.
    """

    if returns.empty:
        raise ValueError("Returns DataFrame is empty.")

    if window <= 1:
        raise ValueError("Window size must be greater than 1.")

    date = pd.Timestamp(date)

    if date not in returns.index:
        raise ValueError(f"{date.date()} not found in returns data.")

    end = returns.index.get_loc(date)

    if end < window - 1:
        raise ValueError(
            f"Not enough historical data before {date.date()}."
        )

    start = end - window + 1
    window_returns = returns.iloc[start : end + 1]

    if tickers is not None:
        window_returns = window_returns[tickers]

    correlation_matrix = window_returns.corr()

    return correlation_matrix