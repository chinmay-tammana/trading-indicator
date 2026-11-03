import argparse
import json
from pathlib import Path
import pandas as pd
import yfinance as yf
from config import CONFIG

def normalize(df):
 if isinstance(df.columns,pd.MultiIndex):df.columns=df.columns.get_level_values(0)
 df.columns=[str(c).lower() for c in df.columns]
 idx=pd.DatetimeIndex(df.index)
 if idx.tz is None:idx=idx.tz_localize('UTC')
 df.index=idx.tz_convert(CONFIG['tz']); df.index.name='timestamp'
 return df[['open','high','low','close','volume']].sort_index()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--refresh',action='store_true'); a=ap.parse_args(); raw=Path(CONFIG['paths']['raw_dir']);raw.mkdir(parents=True,exist_ok=True)
 frames={}; reports=[]
 for sym in [CONFIG['ticker'],*CONFIG['context_tickers']]:
  p=raw/f'{sym}_1h.parquet'
  if p.exists() and not a.refresh: df=pd.read_parquet(p)
  else:
   df=normalize(yf.download(sym,period=CONFIG['period'],interval=CONFIG['interval'],auto_adjust=False,progress=False))
   if df.empty: raise RuntimeError(f'Fresh download returned no rows for {sym}; raw file was not written.')
   df.to_parquet(p)
  if df.empty: raise RuntimeError(f'Raw input for {sym} is empty; remove it and rerun data_fetch.py.')
  df=normalize(df); frames[sym]=df; idx=df.index; daily=pd.Series(1,index=idx).groupby(idx.date).sum(); expected=[pd.Timestamp(d).date() for d,n in daily.items() if n!=7]
  rep={'symbol':sym,'rows':len(df),'duplicate_timestamps':int(idx.duplicated().sum()),'strictly_increasing':bool(idx.is_monotonic_increasing),'non_regular_start_bars':int(sum((idx.hour<9)|((idx.hour==9)&(idx.minute<30))|(idx.hour>15)|((idx.hour==15)&(idx.minute>30)))),'timestamps_with_unexpected_start_minute':int((~idx.minute.isin([0,30])).sum()),'interday_gaps_over_3_calendar_days':[str(x) for x in idx.normalize().unique()[1:][(idx.normalize().unique()[1:]-idx.normalize().unique()[:-1]).days>3]],'days_not_7_bars':[str(d) for d in expected],'zero_volume':int((df.volume==0).sum()),'nan_by_column':df.isna().sum().to_dict(),'high_below_low':int((df.high<df.low).sum()),'close_outside_range':int(((df.close<df.low)|(df.close>df.high)).sum())}; reports.append(rep)
 gs=frames['GS']; aligned=gs.index.intersection(frames['SPY'].index).intersection(frames['XLF'].index); lost=len(gs)-len(aligned); last=gs.index.max(); boundary=last-pd.Timedelta(days=CONFIG['year_length_days']); n1=int((gs.index<boundary).sum()); n2=int((gs.index>=boundary).sum())
 text='Data validation report\n'+json.dumps({'symbols':reports,'rows_lost_on_inner_join':lost,'date_range':[str(gs.index.min()),str(last)],'year2_start':str(boundary),'year1_bars':n1,'year2_bars':n2,'dividend_treatment':'Unadjusted prices; ex-dividend dates can appear as small drops in the overnight gap.'},indent=2)+'\n'
 Path(CONFIG['paths']['logs'],'data_validation.txt').write_text(text); print(text)
if __name__=='__main__':main()
