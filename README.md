# Stock Correlation Explorer

Loads daily price data for thousands of stocks from a zip of CSVs, computes
trailing return correlations for any date/window, and lets you explore them
through a Streamlit GUI.

## Project Structure
```
.
├── app.py
├── src/
│   ├── loader.py                     #fetch csv from zip file and create dataset
│   ├── transformer.py                #transform loaded dataset and validate it
│   ├── returns.py                    #calculate returns matrix
│   ├── correlation.py                #calculate correlations matrix for selected stocks
│   └── pipeline.py                   #execute the flow of loading data and create returns matrix
├── scripts/
│   └── precompute_returns.py
├── tests/
│   ├── test_loader.py
│   ├── test_transformer.py
│   └── test_correlation.py
├── data/
│   ├── stock_data.zip
│   └── returns.parquet
├── requirements.txt
├── pytest.ini
└── README.md
```

## Setup
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Ensure the zip file of CSV's is kept as data/stock_data.zip
Run tests
```
pytest tests/ -v
```
Run the app:
```
streamlit run app.py
```

## How It Works

1. **Load** – Read all CSVs out of the zip into one long-form table.
2. **Clean** – Drop rows with missing prices/dates, blank tickers, and
   duplicate pairs.
3. **Reshape** – Pivot into a Date × Ticker price matrix, then convert to
   daily % returns.
4. **Correlate** – For a chosen date and window, slice the last N days
   of returns and compute correlations.
   - 1 stock selected → corrwith(), correlated against all tickers
   - 2–100 stocks selected → .corr(), scoped to just those tickers
5. **Display** – Top 20 correlated stocks as a table, or a heatmap for
   multiple stocks.

## Storage

A full 5,000×5,000 correlation matrix is ~200MB (25M cells × 8 bytes).
Storing one for every trading date (~1,260 days) would need **~250GB** —
not feasible, and not the "efficient storage" the brief asks for.

Instead:
- We build and save only the **returns matrix**
  (~50MB as Parquet) — a fraction of the size, since it's one row per
  day instead of one full matrix per day.
- Correlations are computed **on demand**, scoped to only the selected
  tickers (1 stock → `corrwith()`, up to 100 → `.corr()` on just those
  columns) instead of the full 5,000×5,000 matrix.

This cuts storage from ~250GB to ~50MB, and computation from ~12.5M
pairwise correlations per request down to at most ~5,000 — so results
still return in milliseconds without ever storing more than needed.

## Things to Improve

- **Cache invalidation is manual** – `returns.parquet` is reused just
  because it exists, not checked against the source zip. A modified-time
  check would auto-rebuild it when the data changes.
- **Single-stock logic lives in `app.py`, not `src/`** – the `corrwith()`
  path isn't in `correlation.py` like the heatmap path is.
- **Only Pearson correlation** – no option for alternative measures
  (e.g. Spearman) in the GUI.
- **No `min_periods` guard** – recently listed
  stocks) could produce misleading correlations from very few
  overlapping days.
- **No tests for `pipeline.py`** – entire process of load → clean → pivot → returns wasnt tested
