PHASE 3: SPLIT AND BASELINES (split.py, baselines.py)
======================================================================
split.py (positions in BARS after warm-up, label-NaN rows kept; filter to labelled rows inside each block afterwards):
- i2 = first bar at or after year2_start. Year 1 = bars [0, i2 - gap_bars). Year 2 = bars [i2, end). n2 = bars in Year 2.
- FT = [i2, i2 + int(0.50*n2)); Val = [FT_end + gap, FT_end + gap + int(0.20*n2)); Test = [Val_end + gap, end).
- Assert Year1.max_time < FT.min_time < FT.max_time < Val.min_time < Val.max_time < Test.min_time and that every gap is at least gap_bars bars.
- Save block boundary dates and sizes to artifacts/split.json.
baselines.py: score ALL of these on the SAME Val and Test blocks, all labelled rows (Test numbers are only printed in Phase 8):
1. Always-UP. 2. Majority class of Year 1. 3. RSI rule: Up if rsi<40, Down if rsi>60, No signal otherwise (accuracy on signals plus coverage). 4. Previous-bar momentum: Up if ret_1>0 else Down. 5. Logistic regression on standardized features (scaler fit on Year 1 only).
For each report accuracy, coverage, number of signals, net return per signal after costs (2, 5, 10 bps) and Wilson 95% CI.
CHECK: the split assertions pass; a baseline table exists on Val.

======================================================================
