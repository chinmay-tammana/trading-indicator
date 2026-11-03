PHASE 4: BASE TRAINING ON YEAR 1 (train_base.py)
======================================================================
1. Fit default-ish XGBClassifier (max_depth=3, learning_rate=0.05, n_estimators=200, subsample 0.8, colsample_bytree 0.8, eval_metric logloss, random_state 42, n_jobs 1) on Year 1 DECISIVE rows only.
2. Sanity check inside Year 1: TimeSeriesSplit(n_splits=5, gap=8) CV log-loss and accuracy. Report train vs CV log-loss to spot overfitting.
3. Score the base model on the Val block (all labelled rows): log-loss, Brier score, accuracy. This is the "S0 / before fine-tuning" number. Do NOT score it on Test.
4. Save artifacts/base_model.json and log the fit in the ledger.
CHECK: base model saved; CV vs train gap reported; Val log-loss recorded. A log-loss near 0.693 means almost no edge, which is normal for hourly equity data.

======================================================================
PHASE 5: FINE-TUNING ON THE FT BLOCK (finetune.py)
======================================================================
Fine-tuning has two parts.

PART A: HYPERPARAMETER SEARCH with walk-forward folds over the FT block.
- Split FT labelled rows into `ft_cv_folds` (4) equal chronological chunks C1..C4.
- Fold k: train = Year 1 decisive rows (sample_weight = year1_weight) + decisive rows of chunks before k, removing any row within gap_bars bars before chunk k's first bar; validate on ALL labelled rows of chunk k. Metric: log-loss.
- Sample `n_iter_search` (40) random configurations with sklearn ParameterSampler (seed 42) from the search space, including year1_weight. Score each by mean validation log-loss across folds.
- Log every configuration and fold score to artifacts/cv_results.csv. Keep the search small: on this little data large searches only find noise. Treat configurations within 0.001 mean log-loss as tied and prefer the simpler one (shallower, fewer trees).

PART B: FINE-TUNING STRATEGIES, compared on the VAL block (all labelled rows) by log-loss (also Brier and accuracy):
- S0: base model from Phase 4 (Year 1, default params), the "before" number.
- S1: Year 1 only, with the tuned parameters.
- S2: refit from scratch on Year 1 (weight year1_weight) + the whole FT block (weight 1), tuned params.
- S3: warm start: train on Year 1 with the tuned params, then continue boosting on the FT block via `fit(X_ft, y_ft, xgb_model=<year1 booster>)` for a number of extra rounds and a lower learning rate chosen from warm_start_rounds_options and warm_start_lr_options (a small search, selected on Val).
Pick the strategy with the lowest Val log-loss; ties go to the simpler one (S1 < S2 < S3). Never refit on Val or Test.

PART C: ABLATIONS (re-run the same procedure with seed 42, select on Val log-loss, keep the list short): with/without time features; with/without SPY and XLF features; with/without rvol; label threshold in label_threshold_candidates. Record what did not help, because the report is graded on it.

PART D: FEATURE IMPORTANCE: gain importance plus permutation importance on Val. Drop a feature only if Val agrees it adds nothing.

Final fit: the chosen strategy and configuration, deterministic, saved to artifacts/model.json, logged in the ledger. Write artifacts/finetune_report.md with the S0-S3 table, ablation table and the what-didn't-work list.
CHECK: cv_results.csv exists; strategy table exists; model saved; overfit check done (train vs CV vs Val log-loss); no Val or Test rows in any fit (the ledger proves it).

======================================================================
