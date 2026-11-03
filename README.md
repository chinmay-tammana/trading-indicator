# GS hourly AI trading indicator: data and baseline stages

This workspace contains Phases 0–3 of the supplied project specification. Model training starts in Phase 4 and has not been run.

Use Python 3.10–3.12 in a clean virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python3 data_fetch.py
python3 prepare_data.py
python3 checks.py
python3 baselines.py
pytest
```

`data_fetch.py` reuses immutable `data/raw/{GS,SPY,XLF}_1h.parquet`; use `--refresh` only when you intentionally want a new raw download. The baseline stage evaluates validation only; the test block is untouched.
