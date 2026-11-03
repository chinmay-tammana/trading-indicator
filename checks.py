import numpy as np
import pandas as pd
from pathlib import Path
from config import CONFIG
from data_fetch import normalize
from features import FEATURES,make_features
from labels import make_labels

def truncation_check(samples=50):
 raw=Path(CONFIG['paths']['raw_dir']); fs={s:normalize(pd.read_parquet(raw/f'{s}_1h.parquet')) for s in ['GS','SPY','XLF']}; idx=fs['GS'].index.intersection(fs['SPY'].index).intersection(fs['XLF'].index); fs={k:v.loc[idx] for k,v in fs.items()}
 full=make_features(fs['GS'],fs['SPY'],fs['XLF'],_print_nan_counts=False); rng=np.random.default_rng(CONFIG['seed']); candidates=np.arange(CONFIG['warmup_rows']+100,len(idx)); points=rng.choice(candidates,min(samples,len(candidates)),replace=False)
 for i in points:
  ts=idx[i]
  local=make_features(fs['GS'].iloc[:i+1],fs['SPY'].iloc[:i+1],fs['XLF'].iloc[:i+1],_print_nan_counts=False); pd.testing.assert_series_equal(full.loc[ts],local.loc[ts],check_names=False,check_exact=False,rtol=1e-12,atol=1e-12)
 return len(points)
def main():
 n=truncation_check(); print(f'truncation check passed for {n} random bars')
if __name__=='__main__':main()
