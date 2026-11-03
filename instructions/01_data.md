PHASE 1: DATA COLLECTION AND VALIDATION (data_fetch.py)
======================================================================
1. Download GS, SPY, XLF with yf.download(period="729d", interval="1h", auto_adjust=False). Flatten MultiIndex columns, lower-case names, index -> `timestamp`, convert UTC -> America/New_York. Keep timestamp, open, high, low, close, volume.
2. Save untouched raw files to data/raw/{symbol}_1h.parquet. Never overwrite after the first successful download (add a --refresh flag).
3. Validate each file; write artifacts/logs/data_validation.txt covering: duplicate timestamps and strict ordering; regular-session bars only (full days have 7 bars starting 09:30, 10:30, 11:30, 12:30, 13:30, 14:30, 15:30 ET, the last covering 30 minutes); days with a bar count other than 7 (half-days such as the day after Thanksgiving and Christmas Eve) flagged, not deleted; zero-volume bars, NaNs, high<low, close outside [low, high]; gaps between trading days longer than a weekend or holiday; total rows (expect ~3,500 for GS).
4. Inner-join SPY and XLF to GS on timestamp; report rows lost (expect ~0).
5. Define era boundary: year2_start = last GS timestamp minus 365 days. Report date range and bar count for Year 1 and Year 2. Save to artifacts/split.json.
6. Document dividend treatment: unadjusted prices, so ex-dividend dates appear as small drops in the overnight gap.
7. Log in progress.md: every model input must also be available live for GS, SPY and XLF; volume may differ between yfinance and a live feed, so `rvol` gets an ablation.
CHECK: validation report exists and every anomaly is fixed or explained; Year 1 and Year 2 each have ~1,500-1,800 bars; all three symbols aligned.

======================================================================
