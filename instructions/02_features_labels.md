PHASE 2: FEATURES AND LABELS (features.py, labels.py)
======================================================================
Feature rules: stationary (returns, ratios, bounded oscillators; never raw dollar prices); causal (bar t uses only data up to and including the close of bar t); computable live from a rolling window of the last 200+ closed bars.

features.py exposes `make_features(df_gs, df_spy, df_xlf)` and `FEATURES`. Compute SPY and XLF returns on their own series BEFORE merging. Features:
- Returns: ret_1, ret_2, ret_3, ret_6, ret_14 (pct_change).
- Overnight: gap = open / previous close - 1.
- Momentum: rsi (Wilder, 14, ewm alpha=1/14), macd_n = MACD(12,26)/close, macd_hist_n = (MACD - signal(9))/close.
- Volatility: bb_pos = %B (20, 2 std), bb_width = 4*std/mean, atr_n = ATR(14, Wilder)/close, vol_20 = rolling std of ret_1 over 20 bars.
- Volume: rvol = volume / rolling 20-bar mean volume.
- Time (ET): hour = bar start hour + minute/60, dow, is_first_bar.
- Market context: spy_ret_1, spy_ret_3, xlf_ret_1, xlf_ret_3, rel_ret_1 = ret_1 - spy_ret_1.
Do not drop rows with dropna(). Drop the first `warmup_rows` rows, and print NaN counts per column first.
Clipping: clip ret_*, gap, rvol and the market-context returns at the 0.5 and 99.5 percentiles, with bounds FITTED ON YEAR 1 ONLY, saved to artifacts/clip_bounds.json and applied to every block.

labels.py:
- fwd = close[t+1] / close[t] - 1 (a simple return; call it that in all text).
- fwd = NaN for the last bar of each trading day (found per date, not hard-coded to 15:30) and for any bar whose next bar is not on the same ET date, so overnight moves are never labelled. Live, the indicator will show "No signal" on that bar.
- y = 1 if fwd > 0 else 0 (print how many rows have fwd == 0).
- decisive = |fwd| > label_threshold. Models are TRAINED only on decisive rows. EVALUATION always uses ALL labelled rows (live, every candle is scored).
- Print Up, Down and decisive shares per era and per block.
Save the full dataset (features, fwd, y, decisive, era) to data/dataset.parquet.
Truncation test (checks.py): for ~50 random bars t, recompute features on data cut at t and assert the row at t equals the full-data value; this proves no look-ahead.
CHECK: truncation test passes; no inf values; no constant feature; no label on last-bar-of-day rows; pytest passes.

======================================================================
