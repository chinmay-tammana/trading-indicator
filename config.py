from pathlib import Path
ROOT=Path(__file__).resolve().parent
CONFIG={
 'ticker':'GS','context_tickers':['SPY','XLF'],'interval':'1h','period':'729d','tz':'America/New_York','year_length_days':365,'seed':42,'horizon_bars':1,'gap_bars':8,'warmup_rows':30,'label_threshold':0.0010,'label_threshold_candidates':[0.0005,0.0010,0.0015,0.0020],'ft_frac':0.50,'val_frac':0.20,'test_frac':0.30,'ft_cv_folds':4,'n_iter_search':40,'year1_weight_options':[0.3,0.6,1.0],'warm_start_rounds_options':[50,100,200],'warm_start_lr_options':[0.01,0.02,0.05],'threshold_sweep':(0.52,0.70,0.01),'min_coverage':0.15,'min_signals':40,'costs_bps':[2,5,10],'primary_cost_bps':5,'rsi_buy_below':40,'rsi_sell_above':60,
 'paths':{'raw_dir':ROOT/'data/raw','dataset':ROOT/'data/dataset.parquet','artifacts':ROOT/'artifacts','logs':ROOT/'artifacts/logs','model':ROOT/'artifacts/model/base_model.json','calibrator':ROOT/'artifacts/calibrator/calib.joblib','split':ROOT/'artifacts/split.json','metrics':ROOT/'artifacts/metrics/metrics.json','fit_ledger':ROOT/'artifacts/fit_ledger.json','clip_bounds':ROOT/'artifacts/clip_bounds.json'}
}
CONFIG['base_model']={'max_depth':3,'learning_rate':0.05,'n_estimators':200,'subsample':0.8,'colsample_bytree':0.8,'eval_metric':'logloss','random_state':CONFIG['seed'],'n_jobs':1}
CONFIG['base_cv']={'n_splits':5,'gap':8,'prediction_threshold':0.5}
CONFIG['paths']['model']=CONFIG['paths']['artifacts']/'base_model.json'
