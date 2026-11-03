# Progress

- [x] Phase 0: setup and clean Git history
- [x] Phase 1: fresh data collection and validation
- [x] Phase 2: features and labels
- [x] Phase 3: split and validation baselines
- [ ] Phase 4: base training — not started; user requested stop before Phase 4
- [ ] Phase 5: fine-tuning — out of scope
- [ ] Phase 6: calibration — out of scope
- [ ] Phase 7: evaluation — out of scope
- [ ] Phase 8: integrity checks — out of scope
- [ ] Phase 9: freeze — out of scope

## Decisions and assumptions

- User request "stop before phase 4" means no base model training, calibration, or test performance evaluation.
- The workspace began empty. No files from any other project were used as inputs. The initially copied neighboring-project files and all derived results were deleted, and local Git history was reset before downloading fresh data.
- Fresh GS, SPY, and XLF hourly files were fetched directly from Yahoo Finance in this task. The first attempt was blocked by DNS; a network escalation retry succeeded.
- Yahoo returned 5,069 rows per symbol over a longer range than requested (Dec 6, 2023–Nov 2, 2026). Raw files are preserved unchanged. The model dataset is limited to the latest two 365-day eras to follow the required split design: Year 1 has 1,731 bars and Year 2 has 1,739 bars after warm-up.
- Phase 1 flagged early closes on Jul 3, Nov 29, and Dec 24 dates, plus incomplete Yahoo source days Jan 30, 2026 (GS/SPY/XLF only 09:30) and Feb 2, 2026 (only 13:30, 14:30, 15:30). These dates remain in raw files. SPY has zero-volume bars at 2023-12-12 14:30, 2024-07-26 14:30, and 2024-08-01 12:30 ET; XLF has one at 2024-09-27 13:30 ET. GS has none. These are retained and reported.
- No price anomalies, duplicate timestamps, NaNs, or rows lost on the context-series join were found. Prices are unadjusted, so ex-dividend dates can appear as small overnight drops.
- Every model input is available from rolling live GS, SPY, and XLF bars. Volume source differences remain a future `rvol` ablation item.
- Phase 2 generated the required full labelled dataset and block label-share report, which includes descriptive counts for the test block. No test results were used for model selection, fitting, or performance evaluation. Do not use test metrics before Phase 8.
- `pytest` could not be installed because package-index DNS was unavailable in the available Python environment. All four test functions were run directly and passed; truncation (50 bars), no infinities, non-constant features, session-final label, and split-gap checks passed.

## Phase log

### Phase 0 — setup

Complete. Created the project structure, instructions, configuration, requirements, source scripts, and a clean local Git repository.

### Phase 1 — data collection and validation

Complete. Fresh Yahoo downloads are in `data/raw/`; validation is in `artifacts/logs/data_validation.txt`. The raw feed returned extra history beyond `729d`; the modeling window uses the latest two 365-day eras without altering raw files.

### Phase 2 — features and labels

Complete. The dataset, Year 1 clipping bounds, era/block label counts, and truncation/integrity checks are saved under `data/` and `artifacts/`.

### Phase 3 — split and baselines

Complete. The split and validation-only baseline table are saved under `artifacts/`. The best validation baseline is previous-bar momentum: 57.24% signal accuracy (Wilson 95% CI 51.56%–62.74%), 100% coverage, and +0.0107% net return per signal after 5 bps.

### Phase 4 and later

Not started per user request.
