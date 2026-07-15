import pandas as pd
import pytest

from src.correlation import calculate_correlation_matrix


def sample_returns():
    """
    20 trading days of returns for 4 tickers.
    A and B move in perfect lockstep (to test correlation == 1.0).
    C and D are just extra tickers to test filtering/ordering.
    """
    dates = pd.date_range("2020-01-01", periods=20, freq="B")

    return pd.DataFrame(
        {
            "A": [0.01, -0.02, 0.03, 0.01, -0.01] * 4,
            "B": [0.01, -0.02, 0.03, 0.01, -0.01] * 4,  # identical to A
            "C": [0.02, 0.01, -0.03, 0.00, 0.01] * 4,
            "D": [-0.01, 0.02, 0.01, -0.02, 0.03] * 4,
        },
        index=dates,
    )


def test_perfect_correlation_is_exactly_one():
    """
    A and B have identical returns in every window, so their correlation
    must be exactly 1.0. This is the simplest possible correctness check
    for the underlying math - if this fails, the correlation logic itself
    is broken, independent of any windowing/filtering concerns.
    """
    returns = sample_returns()
    target_date = returns.index[19]

    corr_matrix = calculate_correlation_matrix(returns, target_date, window=20)

    assert corr_matrix.loc["A", "B"] == pytest.approx(1.0)


def test_earliest_valid_date_boundary():
    """
    The function has an explicit off-by-one-prone boundary: end < window - 1
    raises, but end == window - 1 should succeed and use exactly `window`
    rows. This test targets that exact boundary rather than a date safely
    in the middle of the series, where an off-by-one bug could hide.
    """
    returns = sample_returns()
    window = 20
    earliest_valid_date = returns.index[window - 1]

    corr_matrix = calculate_correlation_matrix(
        returns, earliest_valid_date, window=window
    )

    assert corr_matrix.shape == (4, 4)


def test_insufficient_history_raises_error():
    """
    Requesting a date that doesn't have `window` days of history before it
    must fail loudly rather than silently computing a correlation from
    fewer days than requested (which would be misleading).
    """
    returns = sample_returns()
    window = 20
    too_early_date = returns.index[window - 2]  # one day short

    with pytest.raises(ValueError, match="Not enough historical data"):
        calculate_correlation_matrix(returns, too_early_date, window=window)


def test_tickers_filter_restricts_and_orders_output():
    """
    The `tickers` param exists specifically to avoid computing a full
    NxN matrix when only a subset is needed. This test checks both that
    filtering actually happens and that the output preserves the order
    of the `tickers` list passed in, since the app relies on that order
    when slicing the heatmap.
    """
    returns = sample_returns()
    target_date = returns.index[19]
    selected = ["C", "A", "D"]

    corr_matrix = calculate_correlation_matrix(
        returns, target_date, window=20, tickers=selected
    )

    assert list(corr_matrix.columns) == selected
    assert list(corr_matrix.index) == selected
