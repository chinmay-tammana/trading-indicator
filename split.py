import json
import pandas as pd
from config import CONFIG

def chronological_split(dataset):
 bars=dataset.sort_index(); end=bars.index.max(); year2_start=end-pd.Timedelta(days=CONFIG['year_length_days']); i2=int(bars.index.searchsorted(year2_start,'left')); gap=CONFIG['gap_bars']; n2=len(bars)-i2
 i2=max(i2,1); y1_end=max(0,i2-gap); ft_n=int(.5*n2); val_n=int(.2*n2)
 ft_start=i2; ft_end=ft_start+ft_n; val_start=ft_end+gap; val_end=val_start+val_n; test_start=val_end+gap
 spans={'year1':(0,y1_end),'ft':(ft_start,ft_end),'validation':(val_start,val_end),'test':(test_start,len(bars))}
 blocks={k:bars.iloc[a:b].loc[lambda d:d.y.notna()].copy() for k,(a,b) in spans.items()}
 for k,(a,b) in spans.items():
  part=bars.iloc[a:b]; blocks[k].attrs['bar_start']=str(part.index.min()) if len(part) else None; blocks[k].attrs['bar_end']=str(part.index.max()) if len(part) else None
 data={'year2_start':str(year2_start),'gap_bars':gap,'blocks':{k:{'bar_start':bars.iloc[a:b].index.min().isoformat() if b>a else None,'bar_end':bars.iloc[a:b].index.max().isoformat() if b>a else None,'bar_rows':b-a,'labelled_rows':len(blocks[k])} for k,(a,b) in spans.items()}}
 # Validate strictly ordered eras and gaps in bar positions.
 assert y1_end < ft_start and ft_end+gap==val_start and val_end+gap==test_start
 assert blocks['year1'].index.max()<blocks['ft'].index.min()<blocks['validation'].index.min()<blocks['test'].index.min()
 return blocks,data

def save_split(data,path):path.write_text(json.dumps(data,indent=2)+'\n')
