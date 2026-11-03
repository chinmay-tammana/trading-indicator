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

`data_fetch.py` downloads fresh data when raw files are absent and then preserves them. Use `--refresh` only when you intentionally want a new raw download. Yahoo may return more than the requested range; downstream training uses only the two latest 365-day eras. Phase 2 creates labels and descriptive block counts for the full split as required by the project specification. Baselines evaluate validation only; test performance is not evaluated before Phase 8.
