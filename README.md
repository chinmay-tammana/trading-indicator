# GS Hourly Trading Indicator

This project explores whether hourly market data can help predict the direction of Goldman Sachs (GS) stock over the next same-day hourly bar. It uses fresh GS, SPY, and XLF data downloaded from Yahoo Finance.

## Work completed

- **Phases 0–1:** Set up the project and downloaded and checked the market data.
- **Phase 2:** Created technical and market-context features and next-bar direction labels.
- **Phase 3:** Split the data chronologically and compared simple baselines on validation data. Previous-bar momentum reached 57.24% accuracy.
- **Phase 4:** Trained the initial XGBoost model on decisive Year 1 rows and checked it with time-series cross-validation. On validation, it reached 49.49% accuracy and 0.7407 log-loss. The training-to-CV loss gap suggests overfitting.

The main dataset is available as [CSV](data/dataset.csv) for spreadsheet apps and as [Parquet](data/dataset.parquet) for Python workflows. The Phase 4 model, fit ledger, reports, and progress checklist are also saved in this repository.

**Status:** Work stopped after Phase 4. Fine-tuning and calibration have not been done, and the test block has not been evaluated.

## Run the pipeline

Use Python 3.10–3.12:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python3 data_fetch.py
python3 prepare_data.py
python3 checks.py
python3 baselines.py
python3 train_base.py
```

`data_fetch.py` keeps existing raw downloads unchanged; pass `--refresh` to intentionally download them again. See [instructions/progress.md](instructions/progress.md) for the phase checklist and decisions.
