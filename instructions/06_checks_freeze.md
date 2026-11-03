PHASE 8: INTEGRITY CHECKS (checks.py)
======================================================================
1. Shuffled-label test: run the full pipeline on shuffled labels; Test accuracy must be ~50%. If not, there is a leak.
2. Time-shift test: shift the features by one bar; performance should drop if the model truly uses current information.
3. Truncation test from Phase 2, re-run on the final pipeline.
4. Ledger audit: assert no fit used any row at or after the Val block start, except nothing; i.e. every fit's last timestamp is before Val.min_time.
5. Reproducibility: in a clean clone run the whole pipeline from `python3 data_fetch.py` (using the saved raw files) through `python3 evaluate.py` and confirm identical metrics.
6. Live-compatibility: run make_features on only the last 200 bars and compare the latest row with the full-history value. EMAs depend on history; report how the difference decays. If it is non-trivial, use a longer live window (500 bars) or train with the same window.
CHECK: all six pass or the failures are explained in progress.md.

======================================================================
PHASE 9: FREEZE (end of task)
======================================================================
- artifacts/ contains model.json, calib.joblib, metrics.json, split.json, cv_results.csv, fit_ledger.json, clip_bounds.json, plots.
- Write RESULTS.md: data design and split dates, baseline table, S0-S3 table, ablation table, calibration, Test metrics with CIs, integrity-check results, what did not work, known limitations (small sample, dividends, feed volume differences, last-bar-of-day = No signal).
- Write README.md with the exact commands to reproduce everything from scratch.
- Tag the commit `model-v1`.

When finished, print a final summary: split dates and sizes, S0-S3 Val log-loss, chosen strategy and threshold, Test signal accuracy with CI, coverage, net return per signal at 5 bps, and the best baseline for comparison.
