import math
import numpy as np

def wilson(k,n,z=1.959963984540054):
 if n==0:return [None,None]
 p=k/n; den=1+z*z/n; center=(p+z*z/(2*n))/den; half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return [center-half,center+half]

def score_predictions(frame,signals,costs):
 sig=np.asarray(signals); y=frame.y.astype(int).to_numpy(); active=sig!=0; n=int(active.sum()); correct=int((sig[active]==np.where(y[active]==1,1,-1)).sum())
 values={'accuracy':correct/n if n else None,'coverage':n/len(frame) if len(frame) else 0,'signals':n,'wilson_95':wilson(correct,n),'costs':{}}
 direction=np.where(sig[active]==1,1,-1); returns=frame.fwd.to_numpy()[active]*direction
 for bps in costs:
  net=returns-bps/10000
  values['costs'][str(bps)]={'net_return_per_signal':float(net.mean()) if n else None,'signals':n}
 return values
