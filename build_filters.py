#!/usr/bin/env python3
from pathlib import Path
import json, os, requests, duckdb, pandas as pd, numpy as np

ROOT=Path(__file__).resolve().parent; OUT=ROOT/'results'; DATA=ROOT/'data/1h'; TRADES_GLOB=os.environ.get('FILTER_TRADES_GLOB',f'{OUT}/by_symbol/*_trades.parquet')
def ema(s,n): return s.ewm(span=n,adjust=False,min_periods=n).mean()
def rsi(s,n=14):
 d=s.diff();u=d.clip(lower=0).ewm(alpha=1/n,adjust=False,min_periods=n).mean();v=(-d.clip(upper=0)).ewm(alpha=1/n,adjust=False,min_periods=n).mean();return 100-100/(1+u/v)
def adx(d,n=14):
 tr=pd.concat([d.high-d.low,(d.high-d.close.shift()).abs(),(d.low-d.close.shift()).abs()],axis=1).max(axis=1);a=tr.ewm(alpha=1/n,adjust=False).mean();p=d.high.diff();m=-d.low.diff();p=p.where((p>m)&(p>0),0).ewm(alpha=1/n,adjust=False).mean();m=m.where((m>p)&(m>0),0).ewm(alpha=1/n,adjust=False).mean();di1=100*p/a;di2=100*m/a;return (100*(di1-di2).abs()/(di1+di2)).ewm(alpha=1/n,adjust=False).mean()
btc=pd.read_parquet(DATA/'BTCUSDT.parquet').set_index('open_time')
idx=btc.index; state=pd.DataFrame(index=idx); defs={'baseline':'Filtresiz'}
for tf,rule in [('1h','1h'),('4h','4h'),('1d','1D')]:
 d=btc if tf=='1h' else btc.resample(rule,label='left',closed='left').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna()
 z=(d.volume-d.volume.rolling(20).mean())/d.volume.rolling(20).std(); rr=d.close.pct_change(); aa=adx(d); atr=(d.high-d.low).rolling(14).mean()/d.close
 vals={f'btc_{tf}_above_ema20':d.close>ema(d.close,20),f'btc_{tf}_above_ema50':d.close>ema(d.close,50),f'btc_{tf}_above_ema200':d.close>ema(d.close,200),f'btc_{tf}_ema20_gt_50':ema(d.close,20)>ema(d.close,50),f'btc_{tf}_ema50_gt_200':ema(d.close,50)>ema(d.close,200),f'btc_{tf}_rsi_gt_50':rsi(d.close)>50,f'btc_{tf}_return_pos':rr>0}
 if tf in ('4h','1d'): vals[f'btc_{tf}_adx_gt_20']=aa>20
 if tf in ('1h','4h'): vals[f'btc_{tf}_volz_gt_0']=z>0;vals[f'btc_{tf}_volz_gt_1']=z>1
 if tf=='1d': vals['btc_1d_atr_high']=atr>atr.rolling(100).median();vals['btc_1d_atr_low']=atr<=atr.rolling(100).median()
 for k,v in vals.items(): state[k]=v.shift(1).reindex(idx,method='ffill').fillna(False);defs[k]=k.replace('btc_','BTC ').replace('_',' ')
# BTC market-regime filters (daily values are shifted before hourly expansion).
bd=btc.resample('1D').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna();be50=ema(bd.close,50);be200=ema(bd.close,200);ba=adx(bd)
bbm=bd.close.rolling(20).mean();bbw=4*bd.close.rolling(20).std()/bbm;bbw_q=bbw.rolling(252,min_periods=100).quantile(.20);dh=bd.high.shift(1).rolling(20).max();dl=bd.low.shift(1).rolling(20).min()
btc_regimes={'btc_bull_regime':(bd.close>be200)&(be50.diff()>0),'btc_bear_regime':(bd.close<be200)&(be50.diff()<0),'btc_sideways_adx_lt20':ba<20,'btc_squeeze_low20pct':bbw<bbw_q,'btc_donchian20_breakout':bd.close>dh,'btc_donchian20_breakdown':bd.close<dl}
for k,v in btc_regimes.items(): state[k]=v.shift(1).reindex(idx,method='ffill').fillna(False)
defs.update({'btc_bull_regime':'BTC boğa rejimi: fiyat>EMA200 ve EMA50 yükseliyor','btc_bear_regime':'BTC ayı rejimi: fiyat<EMA200 ve EMA50 düşüyor','btc_sideways_adx_lt20':'BTC yatay rejim: günlük ADX<20','btc_squeeze_low20pct':'BTC sıkışma: BB genişliği 1 yıllık alt %20','btc_donchian20_breakout':'BTC 20 günlük üst kanal kırılımı','btc_donchian20_breakdown':'BTC 20 günlük alt kanal kırılımı'})
# Dollar-strength proxy: Federal Reserve nominal broad U.S. dollar index.
usd=pd.read_csv('https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS');usd['observation_date']=pd.to_datetime(usd.observation_date,utc=True);usd['DTWEXBGS']=pd.to_numeric(usd.DTWEXBGS,errors='coerce');u=usd.set_index('observation_date').DTWEXBGS.dropna();ue20=ema(u,20);ue50=ema(u,50);ue200=ema(u,200);ur=rsi(u);uv=u.pct_change().rolling(20).std();uvm=uv.rolling(252,min_periods=100).median()
usd_filters={'usd_below_ema20':u<ue20,'usd_below_ema50':u<ue50,'usd_below_ema200':u<ue200,'usd_ema20_lt50':ue20<ue50,'usd_ema50_lt200':ue50<ue200,'usd_return_negative':u.pct_change()<0,'usd_mom20_negative':u.pct_change(20)<0,'usd_rsi_lt50':ur<50,'usd_vol_high':uv>uvm,'usd_vol_low':uv<=uvm}
for k,v in usd_filters.items(): state[k]=v.shift(1).reindex(idx,method='ffill').fillna(False)
defs.update({k:'Dolar geniş endeksi '+k.removeprefix('usd_').replace('_',' ') for k in usd_filters})
# Crypto breadth, using only symbols with observations on each date.
above=[];positive=[]
for p in DATA.glob('*.parquet'):
 q=pd.read_parquet(p,columns=['open_time','close']).set_index('open_time').close.resample('1D').last();above.append((q>ema(q,50)).where(q.notna()).rename(p.stem));positive.append((q.pct_change()>0).where(q.notna()).rename(p.stem))
breadth=pd.concat(above,axis=1).mean(axis=1);posbreadth=pd.concat(positive,axis=1).mean(axis=1)
bfilters={'breadth_above50_gt60':breadth>.60,'breadth_above50_lt40':breadth<.40,'breadth_positive_gt60':posbreadth>.60,'breadth_positive_lt40':posbreadth<.40}
for k,v in bfilters.items(): state[k]=v.shift(1).reindex(idx,method='ffill').fillna(False)
defs.update({'breadth_above50_gt60':'Piyasa genişliği: coinlerin >%60 EMA50 üstünde','breadth_above50_lt40':'Piyasa genişliği: coinlerin <%40 EMA50 üstünde','breadth_positive_gt60':'Piyasa genişliği: coinlerin >%60 günlük pozitif','breadth_positive_lt40':'Piyasa genişliği: coinlerin <%40 günlük pozitif'})
fg=requests.get('https://api.alternative.me/fng/?limit=0&format=json',timeout=60).json()['data'];fg=pd.DataFrame(fg);fg['date']=pd.to_datetime(pd.to_numeric(fg.timestamp),unit='s',utc=True).dt.floor('D');fg['value']=pd.to_numeric(fg.value);fg=fg.sort_values('date')
daily=pd.DataFrame({'date':idx.floor('D')},index=idx).merge(fg[['date','value']],on='date',how='left').set_index(idx)['value'].ffill()
for op,val in [('ge',25),('ge',40),('ge',50),('ge',60),('ge',75),('le',25)]:
 k=f'fng_{op}_{val}';state[k]=(daily>=val if op=='ge' else daily<=val).fillna(False);defs[k]=f'Korku-Açgözlülük {">=" if op=="ge" else "<="} {val}'
state.insert(0,'entry_time',idx);state.to_parquet(OUT/'filter_states.parquet',index=False,compression='zstd');(OUT/'filter_definitions.json').write_text(json.dumps(defs,ensure_ascii=False,indent=2))
filters=list(defs); cols=[]
for k in filters:
 cond='TRUE' if k=='baseline' else f's."{k}"'
 cols += [f'count(*) FILTER (WHERE {cond}) AS "{k}__trades"',f'avg(CASE WHEN t.r_multiple>0 THEN 1.0 ELSE 0.0 END) FILTER (WHERE {cond}) AS "{k}__win"',f'avg(t.r_multiple) FILTER (WHERE {cond}) AS "{k}__avg_r"',f'product(1+t."return") FILTER (WHERE {cond})-1 AS "{k}__ret"']
con=duckdb.connect(str(OUT/'filters.duckdb'));con.execute("PRAGMA threads=4; PRAGMA memory_limit='1GB'; PRAGMA temp_directory='{}'".format(str(OUT/'tmp')))
q=f'''COPY (SELECT t.scenario_id,any_value(t.scenario) scenario,t.timeframe,t.symbol,{','.join(cols)} FROM read_parquet('{TRADES_GLOB}') t JOIN read_parquet('{OUT}/filter_states.parquet') s USING(entry_time) GROUP BY t.scenario_id,t.timeframe,t.symbol) TO '{OUT}/filter_symbol_wide.parquet' (FORMAT PARQUET,COMPRESSION ZSTD)''';con.execute(q)
w=con.execute(f"SELECT * FROM read_parquet('{OUT}/filter_symbol_wide.parquet')").df();rows=[]
for k in filters:
 x=w[['scenario_id','scenario','timeframe','symbol',f'{k}__trades',f'{k}__win',f'{k}__avg_r',f'{k}__ret']].copy();x.columns=['scenario_id','scenario','timeframe','symbol','trades','win_rate','avg_r','total_return'];x['filter_id']=k;rows.append(x.dropna(subset=['trades']))
long=pd.concat(rows,ignore_index=True);long.to_parquet(OUT/'filter_symbol.parquet',index=False,compression='zstd')
agg=long.groupby(['filter_id','scenario_id','scenario','timeframe']).agg(total_return=('total_return','mean'),win_rate=('win_rate','mean'),avg_r=('avg_r','mean'),trades=('trades','sum'),symbols=('symbol','nunique')).reset_index();agg[['total_return','win_rate','avg_r','trades','symbols']]=agg[['total_return','win_rate','avg_r','trades','symbols']].fillna(0);agg.to_csv(OUT/'filter_overall_results.csv',index=False)
print('filters',len(filters),'rows',len(agg))
