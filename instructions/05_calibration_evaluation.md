PHASE 6: CALIBRATION AND CONFIDENCE THRESHOLD (calibrate.py)
======================================================================
1. Raw p = model.predict_proba(X)[:,1]. Calibrate on the Val block, ALL labelled rows (no decisive filter): Platt scaling (LogisticRegression on logit(p), clipped to [1e-6, 1-1e-6]). Compare isotonic; choose Platt unless isotonic is clearly better, since Val is small.
2. Reliability diagram and Brier score before and after calibration, saved to artifacts/plots/. A calibrated "68%" should be right about 68% of the time.
3. Signal rule: Up if p_cal >= t, Down if p_cal <= 1 - t, else No signal. Sweep t over threshold_sweep on Val. Choose the t that maximises the Wilson 95% LOWER BOUND of signal accuracy, subject to coverage >= min_coverage and at least min_signals signals. If none qualifies, relax coverage to the largest feasible value while keeping min_signals, and log this in progress.md.
4. Save artifacts/calib.joblib containing calibrator, threshold t, FEATURES, label_threshold, horizon_bars, clip bounds path and the chosen strategy name.
CHECK: calibration plot exists; threshold chosen on Val only; at least min_signals signals on Val.

======================================================================
PHASE 7: FINAL EVALUATION, ONCE (evaluate.py)
======================================================================
Run once on the TEST block, all labelled rows, and save artifacts/metrics.json:
- Accuracy on signals, coverage, number of signals, Wilson 95% CI, plus log-loss and Brier for all rows.
- Every baseline from Phase 3 on the same rows, plus the majority-class rate.
- Simulated net return per signal (long on Up, short on Down) and cumulative return after costs at 2, 5 and 10 bps; hit rate after costs, max drawdown, number of trades.
- Breakdown by hour of day, day of week, volatility regime (high/low atr_n, split at the Year 1 median) and confidence bucket.
- Calibration on Test.
Be honest about statistics: with ~100 signals a 58% accuracy has a CI of roughly +/-10 points. Do not claim an edge the CI does not support. State the go/no-go: if the model does not beat the best baseline on Val log-loss, or the Test CI includes 50%, say so plainly in RESULTS.md and suggest a longer horizon or 15-minute bars for more data.
CHECK: metrics.json written; Test was read exactly once; CIs present.

======================================================================
