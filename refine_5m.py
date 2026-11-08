#!/usr/bin/env python3
"""Refine higher-timeframe exits with chronological Binance 5m klines."""
from __future__ import annotations
import argparse, concurrent.futures as cf, io, json, zipfile
from pathlib import Path
import numpy as np, pandas as pd, requests
from numba import njit

URL='https://data.binance.vision/data/futures/um/monthly/klines'
COLS=['open_time','open','high','low','close','volume','close_time','quote_volume','trades','taker_base','taker_quote','ignore']
def month_range(a,b): return [str(x) for x in pd.period_range(a,b,freq='M')]
def load_5m(symbol,start,end):
 fs=[]
 for m in month_range(start,end):
  u=f'{URL}/{symbol}/5m/{symbol}-5m-{m}.zip'
  try:
   r=requests.get(u,timeout=50)
   if r.status_code!=200: continue
   with zipfile.ZipFile(io.BytesIO(r.content)) as z:
    n=next(x for x in z.namelist() if x.endswith('.csv'));d=pd.read_csv(z.open(n),header=None)
   d=d.iloc[:,:12];d.columns=COLS
   if not pd.api.types.is_numeric_dtype(d.open_time): d=d[pd.to_numeric(d.open_time,errors='coerce').notna()]
   fs.append(d)
  except Exception: continue
 if not fs:return pd.DataFrame()
 d=pd.concat(fs,ignore_index=True);ts=pd.to_numeric(d.open_time,errors='coerce');unit='us' if ts.dropna().median()>1e14 else 'ms';d['open_time']=pd.to_datetime(ts,unit=unit,utc=True)
 for c in ['open','high','low','close']:d[c]=pd.to_numeric(d[c],errors='coerce')
 return d[['open_time','open','high','low','close']].dropna().drop_duplicates('open_time').sort_values('open_time')
def tr(d):
 pc=d.close.shift();return pd.concat([d.high-d.low,(d.high-pc).abs(),(d.low-pc).abs()],axis=1).max(axis=1)
def parent(base,tf):
 if tf=='1h':d=base.copy()
 else:
  rule={'4h':'4h','1d':'1D','1w':'W-MON'}[tf];d=base.set_index('open_time').resample(rule,label='left',closed='left').agg({'open':'first','high':'max','low':'min','close':'last'}).dropna().reset_index()
 d['atr']=tr(d).ewm(alpha=1/14,adjust=False,min_periods=14).mean();d['ema20']=d.close.ewm(span=20,adjust=False,min_periods=20).mean();return d

@njit(cache=True)
def refine(entries,sides,pt,po,pc,pa,pe,mt,mh,ml,mc,cost,maxbars,risk,maxlev):
 n=len(entries);out_r=np.empty(n);out_ret=np.empty(n);out_exit=np.empty(n,dtype=np.int64);out_reason=np.empty(n,dtype=np.int8)
 for q in range(n):
  pi=np.searchsorted(pt,entries[q]);long=sides[q]==1
  if pi>=len(pt) or pt[pi]!=entries[q] or pi<1 or not np.isfinite(pa[pi-1]):out_r[q]=np.nan;out_ret[q]=np.nan;out_exit[q]=entries[q];out_reason[q]=9;continue
  ent=po[pi]*(1+cost if long else 1-cost);R=1.5*pa[pi-1];stop=ent-R if long else ent+R;remain=1.;rr=0.;be=False;end=min(len(pt)-1,pi+maxbars);done=False;reason=0;exit_t=pt[end]
  for k in range(pi,end+1):
   a=np.searchsorted(mt,pt[k]);b=np.searchsorted(mt,pt[k+1] if k+1<len(pt) else pt[k]+604800000000000)
   for j in range(a,b):
    sh=ml[j]<=stop if long else mh[j]>=stop;t1=mh[j]>=ent+R if long else ml[j]<=ent-R;t2=mh[j]>=ent+2*R if long else ml[j]<=ent-2*R
    if sh:
     px=stop*(1-cost if long else 1+cost);rr+=remain*((px-ent)/R)*(1 if long else -1);reason=1;exit_t=mt[j];done=True;break
    if not be and t1:rr+=.4;remain-=.4;be=True;stop=ent
    if remain>.31 and t2:rr+=.6;remain-=.3
   if done:break
   if be and ((pc[k]<pe[k]) if long else (pc[k]>pe[k])):
    px=pc[k]*(1-cost if long else 1+cost);rr+=remain*((px-ent)/R)*(1 if long else -1);reason=2;exit_t=pt[k];done=True;break
  if not done:
   px=pc[end]*(1-cost if long else 1+cost);rr+=remain*((px-ent)/R)*(1 if long else -1)
  actual=min(risk,maxlev*R/ent);out_r[q]=rr;out_ret[q]=rr*actual;out_exit[q]=exit_t;out_reason[q]=reason
 return out_r,out_ret,out_exit,out_reason

def work(job):
 p,root,cfg=job;root=Path(root);symbol=Path(p).stem.removesuffix('_trades');out=root/'results/refined_5m/by_symbol';out.mkdir(parents=True,exist_ok=True);dest=out/f'{symbol}_trades.parquet'
 if dest.exists():return symbol,'cached'
 t=pd.read_parquet(p);base=pd.read_parquet(root/'data/1h'/f'{symbol}.parquet');start=t.entry_time.min().to_period('M');end=t.exit_time.max().to_period('M');m=load_5m(symbol,start,end)
 if m.empty:return symbol,'no_5m'
 mt=m.open_time.astype('int64').to_numpy();mh=m.high.to_numpy();ml=m.low.to_numpy();mc=m.close.to_numpy();parts=[];names=np.array(['timeout','stop_5m','ema20_trail','x','x','x','x','x','x','unmatched'])
 for tf,g in t.groupby('timeframe'):
  keys=g[['entry_time','side']].drop_duplicates();d=parent(base,tf);entries=keys.entry_time.astype('int64').to_numpy();sides=np.where(keys.side.eq('long'),1,-1).astype(np.int8)
  rr,ret,ex,why=refine(entries,sides,d.open_time.astype('int64').to_numpy(),d.open.to_numpy(),d.close.to_numpy(),d.atr.to_numpy(),d.ema20.to_numpy(),mt,mh,ml,mc,cfg['fee_rate_per_side']+cfg['slippage_rate_per_side'],cfg['max_bars_in_trade'],cfg['risk_fraction'],cfg['max_leverage'])
  # Numba receives the parquet timestamps as epoch microseconds.  Passing the
  # integers to pandas without a unit makes pandas assume nanoseconds and
  # shifts exits into 1970, which breaks holding-period reporting.
  keys=keys.copy();keys['r_new']=rr;keys['ret_new']=ret;keys['exit_new']=pd.to_datetime(ex,unit='us',utc=True);keys['reason_new']=names[why]
  z=g.merge(keys,on=['entry_time','side'],how='left');ok=z.r_new.notna();z.loc[ok,'r_multiple']=z.loc[ok,'r_new'];z.loc[ok,'return']=z.loc[ok,'ret_new'];z.loc[ok,'exit_time']=z.loc[ok,'exit_new'];z.loc[ok,'exit_reason']=z.loc[ok,'reason_new'];parts.append(z[t.columns])
 pd.concat(parts,ignore_index=True).to_parquet(dest,index=False,compression='zstd');return symbol,'ok'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--workers',type=int,default=6);a=ap.parse_args();cfg=json.loads((a.root/'config.json').read_text());files=sorted((a.root/'results/by_symbol').glob('*_trades.parquet'));jobs=[(str(p),str(a.root),cfg) for p in files]
 with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
  for i,(s,st) in enumerate(ex.map(work,jobs),1):print(f'[{i}/{len(jobs)}] {s}: {st}',flush=True)
if __name__=='__main__':main()
