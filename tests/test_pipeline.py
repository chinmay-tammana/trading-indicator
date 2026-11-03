import numpy as np
import pandas as pd
from labels import make_labels
from metrics import wilson
from features import make_features
from split import chronological_split

def test_labels_drop_session_end_and_zero_is_down():
 idx=pd.DatetimeIndex(['2024-01-02 15:30','2024-01-03 09:30','2024-01-03 10:30'],tz='America/New_York')
 got=make_labels(pd.Series([100.,101.,101.],index=idx),.001)
 assert pd.isna(got.fwd.iloc[0]) and pd.isna(got.fwd.iloc[2])
 assert got.y.iloc[1]==0 and got.fwd.iloc[1]==0

def test_wilson_bounds():
 lo,hi=wilson(50,100); assert lo<.5<hi
 assert wilson(0,0)==[None,None]

def test_split_keeps_chronological_gaps():
 idx=pd.date_range('2020-01-01',periods=1200,freq='B',tz='UTC')
 frame=pd.DataFrame({'y':np.ones(1200),'fwd':np.zeros(1200)},index=idx)
 blocks,meta=chronological_split(frame)
 assert blocks['year1'].index.max()<blocks['ft'].index.min()<blocks['validation'].index.min()<blocks['test'].index.min()
 assert meta['gap_bars']==8

def test_features_causal_and_expected_columns():
 idx=pd.date_range('2024-01-02 09:30',periods=80,freq='h',tz='America/New_York')
 def frame(mult):
  c=np.arange(80,dtype=float)*mult+100
  return pd.DataFrame({'open':c,'high':c+1,'low':c-1,'close':c,'volume':np.arange(80)+100},index=idx)
 fs=[frame(1),frame(.5),frame(.2)]
 a=make_features(*fs); b=make_features(*(f.iloc[:65] for f in fs))
 pd.testing.assert_series_equal(a.loc[idx[64]],b.loc[idx[64]],check_names=False)
 assert 'ret_1' in a and 'rsi' in a
