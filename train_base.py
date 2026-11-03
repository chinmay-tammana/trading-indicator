"""Fit and evaluate the Year 1 XGBoost base model (Phase 4 only)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBClassifier

from config import CONFIG
from features import FEATURES


def _append_fit_ledger(purpose, timestamps):
    ledger_path = Path(CONFIG['paths']['fit_ledger'])
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    ledger.append({
        'purpose': purpose,
        'first_timestamp': pd.Timestamp(timestamps.min()).isoformat(),
        'last_timestamp': pd.Timestamp(timestamps.max()).isoformat(),
        'row_count': int(len(timestamps)),
    })
    ledger_path.write_text(json.dumps(ledger, indent=2) + '\n')


def _make_model():
    return XGBClassifier(**CONFIG['base_model'])


def _score_model(model, x, y):
    probabilities = model.predict_proba(x)[:, 1]
    predictions = (probabilities >= CONFIG['base_cv']['prediction_threshold']).astype(int)
    return {
        'log_loss': float(log_loss(y, probabilities, labels=[0, 1])),
        'brier_score': float(brier_score_loss(y, probabilities)),
        'accuracy': float(accuracy_score(y, predictions)),
        'rows': int(len(y)),
    }


def run_phase4():
    data_path = Path(CONFIG['paths']['dataset'])
    # Exclude FT and test blocks at parquet read time. Validation is read only
    # for the required Phase 4 score and never enters a fit.
    data = pd.read_parquet(data_path, filters=[('block', 'in', ['year1', 'validation'])])
    year1 = data.loc[(data['block'] == 'year1') & data['y'].notna() & (data['decisive'] == 1)].sort_index()
    validation = data.loc[(data['block'] == 'validation') & data['y'].notna()].sort_index()
    if year1.empty or validation.empty:
        raise ValueError('Year 1 decisive rows and labelled validation rows are both required.')
    if year1.index.max() >= validation.index.min():
        raise AssertionError('Year 1 fit rows must precede validation.')

    x_year1 = year1[FEATURES]
    y_year1 = year1['y'].astype(int)
    cv = TimeSeriesSplit(n_splits=CONFIG['base_cv']['n_splits'], gap=CONFIG['base_cv']['gap'])
    folds = []
    for fold_number, (train_pos, validation_pos) in enumerate(cv.split(x_year1), start=1):
        x_train, y_train = x_year1.iloc[train_pos], y_year1.iloc[train_pos]
        x_fold_val, y_fold_val = x_year1.iloc[validation_pos], y_year1.iloc[validation_pos]
        if x_train.index.max() >= x_fold_val.index.min():
            raise AssertionError(f'CV fold {fold_number} is not chronological.')
        model = _make_model()
        model.fit(x_train, y_train, verbose=False)
        train_score = _score_model(model, x_train, y_train)
        fold_score = _score_model(model, x_fold_val, y_fold_val)
        _append_fit_ledger(f'phase4_year1_timeseries_cv_fold_{fold_number}', x_train.index)
        folds.append({
            'fold': fold_number,
            'train_start': x_train.index.min().isoformat(),
            'train_end': x_train.index.max().isoformat(),
            'cv_start': x_fold_val.index.min().isoformat(),
            'cv_end': x_fold_val.index.max().isoformat(),
            'train_rows': int(len(x_train)),
            'cv_rows': int(len(x_fold_val)),
            'train_log_loss': train_score['log_loss'],
            'cv_log_loss': fold_score['log_loss'],
            'cv_accuracy': fold_score['accuracy'],
        })

    final_model = _make_model()
    final_model.fit(x_year1, y_year1, verbose=False)
    final_train = _score_model(final_model, x_year1, y_year1)
    validation_score = _score_model(final_model, validation[FEATURES], validation['y'].astype(int))
    _append_fit_ledger('phase4_final_base_model_year1_decisive_only', x_year1.index)

    model_path = Path(CONFIG['paths']['model'])
    model_path.parent.mkdir(parents=True, exist_ok=True)
    final_model.save_model(str(model_path))

    mean_cv = float(np.mean([f['cv_log_loss'] for f in folds]))
    mean_fold_train = float(np.mean([f['train_log_loss'] for f in folds]))
    report = {
        'phase': 4,
        'model_parameters': CONFIG['base_model'],
        'training_block': 'year1 decisive rows only',
        'training_rows': int(len(year1)),
        'training_first_timestamp': year1.index.min().isoformat(),
        'training_last_timestamp': year1.index.max().isoformat(),
        'cv': {
            'method': 'TimeSeriesSplit',
            'n_splits': CONFIG['base_cv']['n_splits'],
            'gap': CONFIG['base_cv']['gap'],
            'folds': folds,
            'mean_validation_log_loss': mean_cv,
            'mean_training_log_loss': mean_fold_train,
            'mean_cv_accuracy': float(np.mean([f['cv_accuracy'] for f in folds])),
            'mean_cv_minus_train_gap': float(mean_cv - mean_fold_train),
        },
        'final_model_train_metrics': final_train,
        's0_validation_metrics_all_labelled_rows': validation_score,
        'validation_first_timestamp': validation.index.min().isoformat(),
        'validation_last_timestamp': validation.index.max().isoformat(),
        'model_path': str(model_path),
        'test_block_read_for_scoring': False,
    }
    logs = Path(CONFIG['paths']['logs'])
    logs.mkdir(parents=True, exist_ok=True)
    report_path = logs / 'phase4_training_report.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    console_path = logs / 'phase4_training_console.txt'
    console_path.write_text(json.dumps(report, indent=2) + '\n')

    # Phase 4 CHECK: artifact exists; train/CV gap and validation log loss exist;
    # every ledger fit ends before validation starts.
    if not model_path.is_file() or model_path.stat().st_size == 0:
        raise AssertionError('Base model artifact was not saved.')
    if report['cv']['mean_training_log_loss'] is None or report['cv']['mean_validation_log_loss'] is None:
        raise AssertionError('CV/train log-loss gap was not reported.')
    if report['s0_validation_metrics_all_labelled_rows']['log_loss'] is None:
        raise AssertionError('S0 validation log-loss was not recorded.')
    ledger = json.loads(Path(CONFIG['paths']['fit_ledger']).read_text())
    for entry in ledger:
        if pd.Timestamp(entry['last_timestamp']) >= validation.index.min():
            raise AssertionError(f"Fit ledger contains validation or later rows: {entry}")
    print(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    run_phase4()
