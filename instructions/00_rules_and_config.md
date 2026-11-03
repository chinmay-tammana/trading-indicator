You are a senior ML engineer. Build, validate and freeze a trained model for a Goldman Sachs (GS) AI trading indicator. Work autonomously, phase by phase, in this repository. Do NOT build the live backend or frontend; the task ends when the model artifacts are frozen.

======================================================================
STEP 0 (DO THIS FIRST): SAVE THESE INSTRUCTIONS INTO THE REPO
======================================================================
Before writing any code:
1. Create `instructions/` and save this entire specification into it, split by phase, as: 00_rules_and_config.md, 01_data.md, 02_features_labels.md, 03_split_baselines.md, 04_train_finetune.md, 05_calibration_evaluation.md, 06_checks_freeze.md. Copy the content verbatim; do not summarize.
2. Create `instructions/progress.md` with a checklist of every phase and a section "Decisions and assumptions".
3. Create `AGENTS.md` at the repo root saying: read AGENTS.md first, then every file in instructions/ in numeric order before coding; work phase by phase; after each phase run the CHECK, save logs to artifacts/logs/, commit as "phase N: <name>", update progress.md; never edit instructions/ except progress.md; if a check fails, fix it or stop and log the failure; never skip a failed check; test set is read only once, in Phase 8; no placeholders or TODOs; all parameters in config.py; seed 42; report honest numbers; when ambiguous choose the more conservative leak-free option and log it.
4. From now on, re-read the relevant instruction file at the start of each phase.

======================================================================
GLOBAL RULES
======================================================================
- Asset: GS only. Bar size: 1h. Horizon: the next 1h bar. Context series: SPY and XLF.
- Python 3.10 to 3.12, fresh virtualenv. Install: yfinance pandas numpy scikit-learn xgboost pyarrow scipy joblib matplotlib pytest. Pin installed versions in requirements.txt. Do NOT use pandas-ta; compute every indicator in plain pandas/numpy so the same `make_features()` can be reused by a future live backend.
- No placeholders, TODOs or pseudocode. Every script runs end to end with `python3 <script>.py`.
- All parameters live in config.py. Seed 42 everywhere. Final fit must be deterministic (random_state=42, n_jobs=1).
- Write pytest tests in tests/ for features, labels, splits, Wilson interval and calibration helpers.
- Save every printed report to artifacts/logs/. Commit after each phase.
- FIT LEDGER: every model fit (search folds, ablations, integrity checks, final fits) appends an entry to artifacts/fit_ledger.json with purpose, first and last timestamp of the rows used, and row count.
- TEST-SET DISCIPLINE: the test block is read only in Phase 8, once. No tuning, thresholding, feature selection or model selection may use test data. If this is violated, record it in progress.md.

======================================================================
DATA DESIGN (IMPORTANT)
======================================================================
yfinance gives at most ~729 days of 1h data. Split by time into two eras:
- YEAR 1 (older ~12 months): BASE TRAINING only.
- YEAR 2 (newer ~12 months): FINE-TUNING block (first 50% of Year 2 bars), VALIDATION block (next 20%), TEST block (last 30%).
- Leave a gap of `gap_bars` (8) bars between every pair of adjacent blocks: Year1 -> FT, FT -> Val, Val -> Test.

|--- Year 1: base training ---|gap|-- FT 50% --|gap|-- Val 20% --|gap|-- Test 30% --|
|<------ older ------------------------------------------------------- newest ------>|

Roles: Year 1 fits the base model. FT block is used for hyperparameter search and fine-tuning strategies. Val block is used for calibration, the confidence threshold, choosing the fine-tuning strategy and ablations. Test block is the final report, touched once.
Expected sizes (rough): about 1,500 labelled bars per year; Year 1 decisive rows ~1,200; FT ~750; Val ~300; Test ~450.

======================================================================
PHASE 0: SETUP
======================================================================
Create this layout: config.py, data_fetch.py, features.py, labels.py, split.py, baselines.py, train_base.py, finetune.py, calibrate.py, evaluate.py, checks.py, tests/, data/, artifacts/ (model, calibrator, metrics, plots, logs), instructions/, AGENTS.md, requirements.txt, README.md.

Create config.py with CONFIG containing at least:
ticker "GS"; context_tickers ["SPY","XLF"]; interval "1h"; period "729d"; tz "America/New_York"; year_length_days 365; seed 42; horizon_bars 1; gap_bars 8; warmup_rows 30; label_threshold 0.0010; label_threshold_candidates [0.0005,0.0010,0.0015,0.0020]; ft_frac 0.50; val_frac 0.20; test_frac 0.30; ft_cv_folds 4; n_iter_search 40; year1_weight_options [0.3,0.6,1.0]; warm_start_rounds_options [50,100,200]; warm_start_lr_options [0.01,0.02,0.05]; threshold_sweep (0.52, 0.70, 0.01); min_coverage 0.15; min_signals 40; costs_bps [2,5,10]; primary_cost_bps 5; rsi_buy_below 40; rsi_sell_above 60; and a paths dict (raw_dir, dataset, artifacts, logs, model, calibrator, split, metrics, fit_ledger).
XGBoost search space: max_depth 2-5, learning_rate 0.01-0.1, n_estimators 100-500, subsample 0.6-1.0, colsample_bytree 0.6-1.0, min_child_weight 1-20, reg_lambda 1-20, gamma 0-2, plus year1_weight from config. Keep models shallow and regularized.
CHECK: `python3 -c "import config"` works, layout exists, git initialised, first commit made.

======================================================================
