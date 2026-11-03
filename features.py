import numpy as np
import pandas as pd
from config import CONFIG
FEATURES=['ret_1','ret_2','ret_3','ret_6','ret_14','gap','rsi','macd_n','macd_hist_n','bb_pos','bb_width','atr_n','vol_20','rvol','hour','dow','is_first_bar','spy_ret_1','spy_ret_3','xlf_ret_1','xlf_ret_3','rel_ret_1']
CLIP_FEATURES=[*FEATURES[:6],'rvol','spy_ret_1','spy_ret_3','xlf_ret_1','xlf_ret_3','rel_ret_1']
def _as_series(frame,col):
 return frame[col].astype(float)
def make_features(df_gs,df_spy,df_xlf, _print_nan_counts=True):
 gs=df_gs.sort_index(); spy=df_spy.sort_index(); xlf=df_xlf.sort_index()
 out=pd.DataFrame(index=gs.index); c=_as_series(gs,'close')
 for n in [1,2,3,6,14]:out[f'ret_{n}']=c.pct_change(n)
 out['gap']=_as_series(gs,'open')/c.shift(1)-1
 diff=c.diff(); up=diff.clip(lower=0); down=-diff.clip(upper=0)
 avg_up=up.ewm(alpha=1/14,adjust=False,min_periods=14).mean(); avg_down=down.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
 out['rsi']=100-100/(1+avg_up/avg_down.replace(0,np.nan))
 fast=c.ewm(span=12,adjust=False,min_periods=12).mean(); slow=c.ewm(span=26,adjust=False,min_periods=26).mean(); macd=fast-slow; signal=macd.ewm(span=9,adjust=False).mean()
 out['macd_n']=macd/c; out['macd_hist_n']=(macd-signal)/c
 mean=c.rolling(20,min_periods=20).mean(); std=c.rolling(20,min_periods=20).std(ddof=0)
 out['bb_pos']=(c-(mean-2*std))/(4*std).replace(0,np.nan); out['bb_width']=4*std/mean
 prev=c.shift(1); tr=pd.concat([_as_series(gs,'high')-_as_series(gs,'low'),(_as_series(gs,'high')-prev).abs(),(_as_series(gs,'low')-prev).abs()],axis=1).max(axis=1)
 out['atr_n']=tr.ewm(alpha=1/14,adjust=False,min_periods=14).mean()/c
 out['vol_20']=out.ret_1.rolling(20,min_periods=20).std(ddof=0); out['rvol']=_as_series(gs,'volume')/_as_series(gs,'volume').rolling(20,min_periods=20).mean()
 out['hour']=gs.index.hour+gs.index.minute/60; out['dow']=gs.index.dayofweek; out['is_first_bar']=(gs.index.hour==9).astype(int)
 # Context returns are computed on each instrument's native timeline before alignment.
 for name,frame in [('spy',spy),('xlf',xlf)]:
  returns=_as_series(frame,'close').pct_change()
  out[f'{name}_ret_1']=returns.reindex(gs.index)
  out[f'{name}_ret_3']=_as_series(frame,'close').pct_change(3).reindex(gs.index)
 out['rel_ret_1']=out.ret_1-out.spy_ret_1
 nan=out.isna().sum()
 if _print_nan_counts: print('NaN counts before warmup:',nan.to_dict())
 out=out.replace([np.inf,-np.inf],np.nan).iloc[CONFIG['warmup_rows']:]
 return out

def fit_clip_bounds(features):return {c:[float(features[c].quantile(.005)),float(features[c].quantile(.995))] for c in CLIP_FEATURES}
def apply_clip_bounds(features,bounds):
 out=features.copy()
 for c,(lo,hi) in bounds.items():out[c]=out[c].clip(lo,hi)
 return out
