import json
from pathlib import Path
import numpy as np
import pandas as pd
from config import CONFIG
from data_fetch import normalize
from features import FEATURES,fit_clip_bounds,apply_clip_bounds,make_features
from labels import make_labels
from split import chronological_split,save_split

def main():
 raw=Path(CONFIG['paths']['raw_dir']); source={s:normalize(pd.read_parquet(raw/f'{s}_1h.parquet')) for s in ['GS','SPY','XLF']}
 aligned_idx=source['GS'].index.intersection(source['SPY'].index).intersection(source['XLF'].index)
 frames={s:source[s].loc[aligned_idx] for s in source}
 gs,spy,xlf=frames['GS'],frames['SPY'],frames['XLF']
 feat=make_features(gs,spy,xlf); labels=make_labels(gs.loc[feat.index,'close'],CONFIG['label_threshold']); all_df=feat.join(labels)
 # Yahoo may return more than the requested 729d interval. Preserve the raw
 # files, but restrict modeling rows to the two most recent 365-day eras.
 modeling_start=gs.index.max()-pd.Timedelta(days=2*CONFIG['year_length_days'])
 all_df=all_df.loc[all_df.index>=modeling_start].copy()
 all_df['era']=np.where(all_df.index>=gs.index.max()-pd.Timedelta(days=CONFIG['year_length_days']),'year2','year1')
 # Define eras and blocks on the warm-up-trimmed bar timeline, retaining unlabelled rows for gap math.
 bars=all_df.copy(); blocks,split=chronological_split(bars)
 i2=int(bars.index.searchsorted(pd.Timestamp(split['year2_start'])) if 'year2_start' in split else bars.index.searchsorted(gs.index.max()-pd.Timedelta(days=CONFIG['year_length_days'])))
 # Label the exact positional spans in the full bar table, including NaN label rows.
 year2_start=gs.index.max()-pd.Timedelta(days=CONFIG['year_length_days']); i2=int(bars.index.searchsorted(year2_start)); gap=CONFIG['gap_bars']; n2=len(bars)-i2
 spans={'year1':(0,max(0,i2-gap)),'ft':(i2,i2+int(.5*n2)),'validation':(i2+int(.5*n2)+gap,i2+int(.5*n2)+gap+int(.2*n2)),'test':(i2+int(.5*n2)+gap+int(.2*n2)+gap,len(bars))}
 all_df['block']='excluded'
 for name,(a,b) in spans.items():all_df.iloc[a:b,all_df.columns.get_loc('block')]=name
 year1=all_df[(all_df.block=='year1') & all_df.y.notna()]
 bounds=fit_clip_bounds(year1[FEATURES]); clipped=apply_clip_bounds(all_df[FEATURES],bounds); all_df.loc[:,FEATURES]=clipped
 Path(CONFIG['paths']['clip_bounds']).write_text(json.dumps(bounds,indent=2)+'\n')
 split={'year2_start':str(year2_start),'gap_bars':gap,'blocks':{k:{'start':str(all_df.iloc[a:b].index.min()) if b>a else None,'end':str(all_df.iloc[a:b].index.max()) if b>a else None,'bar_rows':b-a,'labelled_rows':int(all_df.iloc[a:b].y.notna().sum())} for k,(a,b) in spans.items()}}
 ordered=[split['blocks'][k] for k in ['year1','ft','validation','test']]; assert all(pd.Timestamp(a['end'])<pd.Timestamp(b['start']) for a,b in zip(ordered,ordered[1:]))
 save_split(split,Path(CONFIG['paths']['split']))
 counts={}
 for era,d in all_df.groupby('era',sort=True):
  lab=d[d.y.notna()]; counts[f'era_{era}']={'rows':len(d),'labelled':len(lab),'up_share':float(lab.y.mean()) if len(lab) else None,'down_share':float(1-lab.y.mean()) if len(lab) else None,'decisive_share':float(lab.decisive.mean()) if len(lab) else None,'zero_fwd':int((lab.fwd==0).sum())}
 for name,(a,b) in spans.items():
  d=all_df.iloc[a:b]; lab=d[d.y.notna()]; counts[name]={'rows':len(d),'labelled':len(lab),'up_share':float(lab.y.mean()) if len(lab) else None,'down_share':float(1-lab.y.mean()) if len(lab) else None,'decisive_share':float(lab.decisive.mean()) if len(lab) else None,'zero_fwd':int((lab.fwd==0).sum())}
 path=Path(CONFIG['paths']['dataset']); all_df.to_parquet(path)
 report={'counts':counts,'feature_nan_after_warmup':feat.isna().sum().to_dict(),'infinite_values':int(np.isinf(all_df[FEATURES].to_numpy()).sum()),'joined_rows':len(gs),'rows_lost':len(source['GS'])-len(aligned_idx),'range':[str(gs.index.min()),str(gs.index.max())],'split':split,'dividend_treatment':'Unadjusted prices; ex-dividend dates can show as small drops in the overnight gap.'}
 Path(CONFIG['paths']['logs'],'phase2_dataset_report.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2))
if __name__=='__main__':main()
