import numpy as np
import pandas as pd

def make_labels(close,threshold):
 fwd=close.shift(-1)/close-1
 dates=pd.Series(close.index.date,index=close.index)
 fwd=fwd.mask(dates.ne(dates.shift(-1)))
 return pd.DataFrame({'fwd':fwd,'y':np.where(fwd.notna(),(fwd>0).astype(float),np.nan),'decisive':np.where(fwd.notna(),(fwd.abs()>threshold).astype(float),np.nan)},index=close.index)
