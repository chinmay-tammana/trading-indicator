import json
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from config import CONFIG
from features import FEATURES
from metrics import score_predictions

def baseline_predictions(year1,target):
 majority=int(year1.y.mean()>=.5)
 rsi=np.zeros(len(target),dtype=int); rsi[target.rsi<CONFIG['rsi_buy_below']]=1; rsi[target.rsi>CONFIG['rsi_sell_above']]=-1
 model=make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),LogisticRegression(max_iter=2000,random_state=CONFIG['seed']))
 model.fit(year1[FEATURES],year1.y.astype(int)); prob=model.predict_proba(target[FEATURES])[:,1]
 return {'always_up':np.ones(len(target),dtype=int),'year1_majority':np.full(len(target),1 if majority else -1),'rsi_rule':rsi,'previous_bar_momentum':np.where(target.ret_1>0,1,-1),'logistic_regression':np.where(prob>=.5,1,-1)}
def evaluate_baselines(year1,val):return {name:score_predictions(val,pred,CONFIG['costs_bps']) for name,pred in baseline_predictions(year1,val).items()}
def main():
 from pathlib import Path
 data=pd.read_parquet(CONFIG['paths']['dataset']); val=data[(data.block=='validation')&data.y.notna()]; year1=data[(data.block=='year1')&data.y.notna()]
 results=evaluate_baselines(year1,val); p=Path(CONFIG['paths']['artifacts'])/'baseline_table.csv'; rows=[]
 for name,m in results.items(): rows.append({'baseline':name,'accuracy':m['accuracy'],'coverage':m['coverage'],'signals':m['signals'],'wilson_low':m['wilson_95'][0],'wilson_high':m['wilson_95'][1],**{f'net_return_per_signal_{c}bps':m['costs'][str(c)]['net_return_per_signal'] for c in CONFIG['costs_bps']}})
 pd.DataFrame(rows).to_csv(p,index=False); print(pd.DataFrame(rows).to_string(index=False))
 (Path(CONFIG['paths']['logs'])/'phase3_baselines.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':main()
