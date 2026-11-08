#!/usr/bin/env python3
"""Vectorized signal generation and conservative bar-by-bar trade simulation."""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit


def cross_up(a, b):
    if np.isscalar(b):
        return (a > b) & (a.shift(1) <= b)
    return (a > b) & (a.shift(1) <= b.shift(1))


def ema(s, n): return s.ewm(span=n, adjust=False, min_periods=n).mean()
def sma(s, n): return s.rolling(n).mean()


def rsi(s, n=14):
    d = s.diff(); up = d.clip(lower=0); dn = -d.clip(upper=0)
    rs = up.ewm(alpha=1/n, adjust=False, min_periods=n).mean() / dn.ewm(alpha=1/n, adjust=False, min_periods=n).mean()
    return 100 - 100/(1+rs)


def true_range(df):
    pc = df.close.shift(1)
    return pd.concat([(df.high-df.low), (df.high-pc).abs(), (df.low-pc).abs()], axis=1).max(axis=1)


def supertrend(df, period=10, mult=3.0):
    atr = true_range(df).ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    mid = (df.high + df.low) / 2
    up = (mid + mult*atr).to_numpy(); lo = (mid - mult*atr).to_numpy(); c = df.close.to_numpy()
    trend = np.ones(len(df), dtype=np.int8)
    fu, fl = up.copy(), lo.copy()
    for i in range(1, len(df)):
        fu[i] = up[i] if (up[i] < fu[i-1] or c[i-1] > fu[i-1]) else fu[i-1]
        fl[i] = lo[i] if (lo[i] > fl[i-1] or c[i-1] < fl[i-1]) else fl[i-1]
        if c[i] > fu[i-1]: trend[i] = 1
        elif c[i] < fl[i-1]: trend[i] = -1
        else: trend[i] = trend[i-1]
    return pd.Series(trend, index=df.index), pd.Series(np.where(trend > 0, fl, fu), index=df.index)


def indicators(df):
    x = df.copy()
    for n in (20, 50, 100, 200): x[f"ema{n}"] = ema(x.close, n)
    for n in (20, 50, 200): x[f"sma{n}"] = sma(x.close, n)
    x["atr"] = true_range(x).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    x["rsi"] = rsi(x.close)
    fast, slow = ema(x.close, 12), ema(x.close, 26)
    x["macd"] = fast-slow; x["macds"] = ema(x.macd, 9); x["hist"] = x.macd-x.macds
    ll, hh = x.low.rolling(14).min(), x.high.rolling(14).max()
    x["stochk"] = 100*(x.close-ll)/(hh-ll); x["stochd"] = x.stochk.rolling(3).mean()
    tp = (x.high+x.low+x.close)/3
    pos = tp*x.volume.where(tp.diff() > 0, 0); neg = tp*x.volume.where(tp.diff() < 0, 0).abs()
    mr = pos.rolling(14).sum()/neg.rolling(14).sum(); x["mfi"] = 100-100/(1+mr)
    mfv = ((x.close-x.low)-(x.high-x.close))/(x.high-x.low).replace(0,np.nan)*x.volume
    x["cmf"] = mfv.rolling(20).sum()/x.volume.rolling(20).sum()
    x["obv"] = (np.sign(x.close.diff()).fillna(0)*x.volume).cumsum()
    x["volz"] = (x.volume-x.volume.rolling(20).mean())/x.volume.rolling(20).std()
    plus = x.high.diff(); minus = -x.low.diff()
    pdm = plus.where((plus>minus)&(plus>0),0); mdm = minus.where((minus>plus)&(minus>0),0)
    atrs = true_range(x).ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    x["pdi"] = 100*pdm.ewm(alpha=1/14,adjust=False,min_periods=14).mean()/atrs
    x["mdi"] = 100*mdm.ewm(alpha=1/14,adjust=False,min_periods=14).mean()/atrs
    dx = 100*(x.pdi-x.mdi).abs()/(x.pdi+x.mdi); x["adx"] = dx.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    x["dc20h"] = x.high.shift(1).rolling(20).max(); x["dc20l"] = x.low.shift(1).rolling(20).min()
    x["dc55h"] = x.high.shift(1).rolling(55).max(); x["dc55l"] = x.low.shift(1).rolling(55).min()
    x["hh20"] = x.high.shift(1).rolling(20).max(); x["ll20"] = x.low.shift(1).rolling(20).min()
    x["bbm"] = sma(x.close,20); sd=x.close.rolling(20).std(); x["bbu"]=x.bbm+2*sd; x["bbl"]=x.bbm-2*sd
    x["kcu"] = x.ema20+2*x.atr; x["kcl"] = x.ema20-2*x.atr
    x["st"], x["stline"] = supertrend(x)
    high9=x.high.rolling(9).max(); low9=x.low.rolling(9).min(); high26=x.high.rolling(26).max(); low26=x.low.rolling(26).min()
    x["tenkan"]=(high9+low9)/2; x["kijun"]=(high26+low26)/2
    x["span_a"]=(x.tenkan+x.kijun)/2; x["span_b"]=(x.high.rolling(52).max()+x.low.rolling(52).min())/2
    x["bull_engulf"]=(x.close>x.open)&(x.open<=x.close.shift(1))&(x.close>=x.open.shift(1))&(x.close.shift(1)<x.open.shift(1))
    body=(x.close-x.open).abs(); lower=np.minimum(x.open,x.close)-x.low; upper=x.high-np.maximum(x.open,x.close)
    x["bull_pin"]=(lower>=2*body)&(upper<=body)&(x.close>x.open)
    x["inside"]=(x.high<x.high.shift(1))&(x.low>x.low.shift(1))
    x["nr7"]=(x.high-x.low)<(x.high-x.low).shift(1).rolling(6).min()
    x["bull_div"]=(x.low<x.low.shift(1).rolling(20).min())&(x.rsi>x.rsi.shift(1).rolling(20).min())
    x["avwap_week"]=(x.close*x.volume).groupby(x.open_time.dt.to_period("W")).cumsum()/x.volume.groupby(x.open_time.dt.to_period("W")).cumsum()
    x["avwap_month"]=(x.close*x.volume).groupby(x.open_time.dt.to_period("M")).cumsum()/x.volume.groupby(x.open_time.dt.to_period("M")).cumsum()
    x["ret_high"]=(x.low<=x.dc20h.shift(1)+.2*x.atr)&(x.close>x.dc20h.shift(1))
    return x


def trend_filter(x, key, long=True):
    s = key.lower(); sign = 1 if long else -1
    if "ema20>ema50" in s: return (x.ema20>x.ema50)&(x.ema50.diff()*sign>0) if long else (x.ema20<x.ema50)&(x.ema50.diff()<0)
    if "ema50>ema200" in s: return (x.ema50>x.ema200)&(x.close>x.ema50) if long else (x.ema50<x.ema200)&(x.close<x.ema50)
    if "sma20>sma50>sma200" in s: return (x.sma20>x.sma50)&(x.sma50>x.sma200) if long else (x.sma20<x.sma50)&(x.sma50<x.sma200)
    if "ichimoku" in s: return (x.close>x[["span_a","span_b"]].max(axis=1))&(x.span_a>x.span_b) if long else (x.close<x[["span_a","span_b"]].min(axis=1))&(x.span_a<x.span_b)
    if "supertrend" in s: return x.st.eq(sign)
    if "kapanış ema50" in s: return x.close>x.ema50 if long else x.close<x.ema50
    if "macd çizgisi sıfır" in s or "macd sıfır" in s: return x.macd>0 if long else x.macd<0
    if "rsi14 son 20" in s: return x.rsi.rolling(20).min()>40 if long else x.rsi.rolling(20).max()<60
    if "mfi14>50" in s: return x.mfi>50 if long else x.mfi<50
    return pd.Series(True,index=x.index)


def trigger(x, text, long=True):
    s=text.lower(); sg=1 if long else -1
    if "rsi14 önce 45" in s or "rsi 50'yi" in s or "rsi 50 reclaim" in s or "rsi14 50 üstüne geçer" in s:
        return cross_up(x.rsi,50) if long else cross_up(-x.rsi,-50)
    if "macd" in s and ("yukarı keser" in s or "negatiften pozitife" in s):
        return cross_up(x.macd,x.macds) if long else cross_up(-x.macd,-x.macds)
    if "stoch" in s and ("keser" in s or "%k>%d" in s): return cross_up(x.stochk,x.stochd) if long else cross_up(-x.stochk,-x.stochd)
    if "mfi 50'yi" in s: return cross_up(x.mfi,50) if long else cross_up(-x.mfi,-50)
    if "bullish engulf" in s: return x.bull_engulf if long else ((x.close<x.open)&(x.open>=x.close.shift(1))&(x.close<=x.open.shift(1)))
    if "bullish pin" in s: return x.bull_pin if long else ((np.maximum(x.open,x.close)-x.high).abs()>=2*(x.close-x.open).abs())
    if "inside-bar breakout" in s: return x.close>x.high.shift(1) if long else x.close<x.low.shift(1)
    if "pin-inside" in s: return (x.inside.shift(1)&(x.close>x.high.shift(1))) if long else (x.inside.shift(1)&(x.close<x.low.shift(1)))
    if "morning star" in s: return (x.close>x.open)&(x.close.shift(2)<x.open.shift(2))&(x.close>(x.open.shift(2)+x.close.shift(2))/2) if long else (x.close<x.open)&(x.close.shift(2)>x.open.shift(2))
    if "donchian20" in s: return x.close>x.dc20h if long else x.close<x.dc20l
    if "donchian55" in s: return x.close>x.dc55h if long else x.close<x.dc55l
    if "son 20 mumun" in s: return x.close>x.hh20 if long else x.close<x.ll20
    if "bb(20,2) üst" in s or "bb squeeze üst" in s: return x.close>x.bbu if long else x.close<x.bbl
    if "kc(20,2atr) üst" in s: return x.close>x.kcu if long else x.close<x.kcl
    if "+di -di'yi" in s: return cross_up(x.pdi,x.mdi) if long else cross_up(x.mdi,x.pdi)
    if "supertrend aşağıdan yukarı flip" in s: return cross_up(x.st,0) if long else cross_up(-x.st,0)
    if "tenkan kijun" in s: return cross_up(x.tenkan,x.kijun) if long else cross_up(x.kijun,x.tenkan)
    if "atr14/close" in s: 
        q=(x.atr/x.close).rolling(100).quantile(.25); return cross_up(x.atr/x.close,q)
    if "bb width" in s: return cross_up((x.bbu-x.bbl),(x.kcu-x.kcl))
    if "nr7" in s: return x.nr7
    if "inside-bar serisi" in s: return x.inside & x.inside.shift(1)
    if "atr14 son 20" in s: return x.atr>1.5*x.atr.rolling(20).mean()
    if "divergence" in s or "uyumsuzluk" in s: return x.bull_div if long else ((x.high>x.high.shift(1).rolling(20).max())&(x.rsi<x.rsi.shift(1).rolling(20).max()))
    return pd.Series(True,index=x.index)


def condition(x, text, long=True):
    """Operational definition for title fragments not represented by a cross."""
    s=text.lower()
    if "rsi14 52–68" in s: return x.rsi.between(52,68) if long else x.rsi.between(32,48)
    if "rsi14 50–70" in s: return x.rsi.between(50,70) if long else x.rsi.between(30,50)
    if "cmf20>0.05" in s: return x.cmf>.05 if long else x.cmf<-.05
    if "hacim z≥0.8" in s: return x.volz>=.8
    if "raw-volume z≥1" in s: return x.volz>=1
    if "macd histogramı >0" in s: return x["hist"]>0 if long else x["hist"]<0
    if "stoch %k>%d" in s: return x.stochk>x.stochd if long else x.stochk<x.stochd
    if "mfi14>55" in s: return x.mfi>55 if long else x.mfi<45
    if "mfi14>50" in s: return x.mfi>50 if long else x.mfi<50
    if "obv son 20" in s: return x.obv>x.obv.shift(1).rolling(20).max() if long else x.obv<x.obv.shift(1).rolling(20).min()
    if "son 10 bar tepesinde" in s: return x.close>x.high.shift(1).rolling(10).max() if long else x.close<x.low.shift(1).rolling(10).min()
    if "avwap üstünde" in s or "haftalık avwap üstünde" in s: return x.close>x.avwap_week if long else x.close<x.avwap_week
    if "4h direncin ilk retesti" in s or "kırılan direncin ilk retest" in s or "donchian20 kırılımının ilk retesti" in s: return x.ret_high if long else ((x.high>=x.dc20l.shift(1)-.2*x.atr)&(x.close<x.dc20l.shift(1)))
    if "ema20 retestinden" in s: return ((x.low<=x.ema20)&x.bull_engulf) if long else ((x.high>=x.ema20)&(x.close<x.open))
    if "donchian20 orta çizgisi yükseliyor" in s:
        mid=(x.dc20h+x.dc20l)/2; return mid.diff()>0 if long else mid.diff()<0
    if "ema20>ema50 ve ikisi yükseliyor" in s: return (x.ema20>x.ema50)&(x.ema20.diff()>0)&(x.ema50.diff()>0) if long else (x.ema20<x.ema50)&(x.ema20.diff()<0)&(x.ema50.diff()<0)
    if "önceki hafta düşüğü" in s: return x.low<x.low.shift(1).rolling(7*24).min() if long else x.high>x.high.shift(1).rolling(7*24).max()
    if "%38.2–%61.8" in s:
        hi=x.high.shift(1).rolling(20).max();lo=x.low.shift(1).rolling(20).min();return x.close.between(lo+.382*(hi-lo),lo+.618*(hi-lo))
    return trend_filter(x,text,long)&trigger(x,text,long)


def scenario_signal(x, sid, title, long=True, cache=None):
    cache = {} if cache is None else cache
    def cached(kind, text):
        key=(kind,text,long)
        if key not in cache:
            cache[key] = trend_filter(x,text,long) if kind=="trend" else trigger(x,text,long) if kind=="trigger" else condition(x,text,long)
        return cache[key]
    parts = title.split(" — ",2); body = parts[-1]; chunks=[z.strip() for z in re.split(r" \+ | / ", body)]
    if sid<=20:
        sig=cached("trend",chunks[0])&cached("trigger",chunks[-1])
        pull=((x.low<=x.ema20)&(x.high>=x.ema50)) if long else ((x.high>=x.ema20)&(x.low<=x.ema50))
        needs_pull = chunks[0].lower().startswith("ema")
        return sig & (pull if needs_pull else True) & (x.adx>=18)
    if sid<=40:
        sig=cached("trigger",chunks[0])
        if "adx" in body.lower(): sig &= (x.adx>=22)&(x.adx.diff()>0)
        if "cmf" in body.lower(): sig &= x.cmf.gt(.05) if long else x.cmf.lt(-.05)
        if "rsi" in body.lower(): sig &= x.rsi.gt(55) if long else x.rsi.lt(45)
        return sig
    if sid<=60: return cached("trend",chunks[0])&cached("trigger",chunks[-1])
    if sid<=80:
        if "bb(20,2) alt" in body.lower(): setup=(x.close.shift(1)<x.bbl.shift(1))&(x.close>x.bbl) if long else (x.close.shift(1)>x.bbu.shift(1))&(x.close<x.bbu)
        elif "kc(20,2atr) alt" in body.lower(): setup=(x.low<x.kcl)&(x.close>x.kcl) if long else (x.high>x.kcu)&(x.close<x.kcu)
        elif "avwap" in body.lower(): setup=x.low < x.avwap_month-2*x.close.rolling(20).std() if long else x.high>x.avwap_month+2*x.close.rolling(20).std()
        elif "haftanın düşüğü" in body.lower(): setup=x.low<x.low.shift(1).rolling(7*24).min() if long else x.high>x.high.shift(1).rolling(7*24).max()
        else: setup=x.low<x.ll20 if long else x.high>x.hh20
        return setup & cached("trigger",chunks[-1])
    if sid<=100: return cached("trigger",chunks[0])&cached("trigger",chunks[-1])
    if sid<=120: return cached("trigger",chunks[0])&cached("condition",chunks[-1])
    if sid<=140:
        vol=cached("trigger",chunks[0])
        if "obv" in body.lower(): vol=x.obv>x.obv.shift(1).rolling(20).max() if long else x.obv<x.obv.shift(1).rolling(20).min()
        if "cmf20" in body.lower(): vol=cross_up(x.cmf,0) if long else cross_up(-x.cmf,0)
        if "mfi14" in body.lower(): vol=cross_up(x.mfi,50)&(x.volz>=1) if long else cross_up(-x.mfi,-50)&(x.volz>=1)
        if "avwap" in body.lower(): vol=x.close>x.avwap_week if long else x.close<x.avwap_week
        return vol & cached("condition",chunks[-1])
    if sid<=160: return cached("trend",chunks[0])&cached("trigger",chunks[-1])
    if sid<=180: return cached("trend",chunks[0])&cached("trigger",chunks[-1])
    if sid<=200:
        sig=cached("trigger",chunks[0])
        confirm=cached("condition",chunks[-1])
        if "adx" in body.lower(): confirm=(x.adx>=20)&((x.pdi>x.mdi) if long else (x.mdi>x.pdi))
        if "obv" in body.lower(): confirm=(x.obv>x.obv.shift(1).rolling(20).max()) if long else (x.obv<x.obv.shift(1).rolling(20).min())
        return sig&confirm
    sig=pd.Series(True,index=x.index)
    for c in chunks: sig &= cached("condition",c)
    return sig


@njit(cache=True)
def _simulate_core(o,h,l,c,atr,e20,sig,long,cost,max_bars):
    rows=[]; n=len(o); i=1
    while i<n-1:
        if not sig[i] or not np.isfinite(atr[i]) or atr[i]<=0 or not np.isfinite(o[i+1]) or o[i+1]<=0: i+=1; continue
        ent=o[i+1]*(1+cost if long else 1-cost); stop=ent-1.5*atr[i] if long else ent+1.5*atr[i]; R=abs(ent-stop)
        if not np.isfinite(R) or R<=1e-15: i+=1; continue
        remain=1.0; rmult=0.0; be=False; exit_i=min(n-1,i+1+max_bars); reason=0
        j=i+1
        while j<=exit_i:
            stop_hit=l[j]<=stop if long else h[j]>=stop
            t1_hit=h[j]>=ent+R if long else l[j]<=ent-R
            t2_hit=h[j]>=ent+2*R if long else l[j]<=ent-2*R
            if stop_hit:
                px=stop*(1-cost if long else 1+cost); rmult += remain*((px-ent)/R)*(1 if long else -1); reason=1; exit_i=j; remain=0; break
            if not be and t1_hit:
                rmult += .4*1; remain-=.4; be=True; stop=ent
            if remain>.31 and t2_hit:
                rmult += .3*2; remain-=.3
            if be and ((c[j]<e20[j]) if long else (c[j]>e20[j])):
                px=c[j]*(1-cost if long else 1+cost); rmult += remain*((px-ent)/R)*(1 if long else -1); reason=2; exit_i=j; remain=0; break
            j+=1
        if remain>0:
            px=c[exit_i]*(1-cost if long else 1+cost); rmult += remain*((px-ent)/R)*(1 if long else -1)
        rows.append((i+1,exit_i,rmult,reason))
        i=max(i+1,exit_i+1)
    return rows


def simulate(x, signal, long, cfg):
    cost=cfg["fee_rate_per_side"]+cfg["slippage_rate_per_side"]
    times=x.open_time.to_numpy(); opens=x.open.to_numpy(); atrs=x.atr.to_numpy()
    core=_simulate_core(opens,x.high.to_numpy(),x.low.to_numpy(),x.close.to_numpy(),atrs,x.ema20.to_numpy(),signal.fillna(False).to_numpy(dtype=np.bool_),long,cost,cfg["max_bars_in_trade"])
    names=("timeout","stop","ema20_trail"); risk=cfg["risk_fraction"]
    rows=[]
    for a,b,r,reason in core:
        entry=opens[a]*(1+cost if long else 1-cost); stop_pct=(1.5*atrs[a-1])/entry
        actual_risk=min(risk,cfg["max_leverage"]*stop_pct)
        rows.append((pd.Timestamp(times[a]),pd.Timestamp(times[b]),"long" if long else "short",float(r),float(r*actual_risk),names[reason]))
    return rows


def resample(df, tf):
    if tf=="1h": return df
    rule={"4h":"4h","1d":"1D","1w":"W-MON"}[tf]
    return df.set_index("open_time").resample(rule,label="left",closed="left").agg({"open":"first","high":"max","low":"min","close":"last","volume":"sum","quote_volume":"sum","trades":"sum","taker_base":"sum","taker_quote":"sum"}).dropna(subset=["open","close"]).reset_index()


def parse_scenarios(path):
    pat=re.compile(r"^## (\d{3}) — (.+)$",re.M)
    return [(int(a),b) for a,b in pat.findall(path.read_text())]


def process_symbol(job):
    p, root_s, cfg, scenarios = job
    root=Path(root_s); symbol=Path(p).stem; out=root/"results/by_symbol"; out.mkdir(parents=True,exist_ok=True)
    trade_file=out/f"{symbol}_trades.parquet"; summary_file=out/f"{symbol}_summary.parquet"
    if trade_file.exists() and summary_file.exists(): return symbol,"cached"
    base=pd.read_parquet(p); trade_parts=[]; summary=[]
    for tf in cfg["timeframes"]:
        x=indicators(resample(base,tf))
        signal_cache={}
        for sid,title in scenarios:
            if 161<=sid<=180 and tf!="1h": continue
            alltr=[]
            for long in (True,False): alltr += simulate(x,scenario_signal(x,sid,title,long,signal_cache),long,cfg)
            if not alltr: continue
            td=pd.DataFrame(alltr,columns=["entry_time","exit_time","side","r_multiple","return","exit_reason"])
            td["symbol"]=symbol;td["timeframe"]=tf;td["scenario_id"]=sid;td["scenario"]=title; trade_parts.append(td)
            summary.append({"symbol":symbol,"timeframe":tf,"scenario_id":sid,"scenario":title,"trades":len(td),"win_rate":float((td.r_multiple>0).mean()),"avg_r":float(td.r_multiple.mean()),"total_return":float(np.prod(1+td["return"])-1),"max_loss_r":float(td.r_multiple.min())})
    if trade_parts: pd.concat(trade_parts,ignore_index=True).to_parquet(trade_file,index=False,compression="zstd")
    else: pd.DataFrame(columns=["entry_time","exit_time","side","r_multiple","return","exit_reason","symbol","timeframe","scenario_id","scenario"]).to_parquet(trade_file,index=False)
    pd.DataFrame(summary).to_parquet(summary_file,index=False,compression="zstd")
    return symbol,"ok"


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parent); ap.add_argument("--limit-symbols",type=int); ap.add_argument("--workers",type=int,default=8); args=ap.parse_args()
    cfg=json.loads((args.root/"config.json").read_text()); scenarios=parse_scenarios(args.root/"strategy.md")
    files=sorted((args.root/"data/1h").glob("*.parquet")); files=files[:args.limit_symbols] if args.limit_symbols else files
    outdir=args.root/"results"; (outdir/"by_symbol").mkdir(parents=True,exist_ok=True)
    jobs=[(str(p),str(args.root),cfg,scenarios) for p in files]
    with cf.ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i,(symbol,status) in enumerate(ex.map(process_symbol,jobs),1): print(f"[{i}/{len(jobs)}] {symbol}: {status}",flush=True)
    sfiles=list((outdir/"by_symbol").glob("*_summary.parquet")); tfiles=list((outdir/"by_symbol").glob("*_trades.parquet"))
    s=pd.concat([pd.read_parquet(p) for p in sfiles],ignore_index=True); s.to_parquet(outdir/"summary_symbol.parquet",index=False)
    t=pd.concat([pd.read_parquet(p) for p in tfiles],ignore_index=True); t["year"]=pd.to_datetime(t.entry_time,utc=True).dt.year
    yg=t.groupby(["scenario_id","scenario","timeframe","symbol","year"])
    y=yg["return"].apply(lambda z: np.prod(1+z)-1).reset_index(name="annual_return")
    counts=yg.size().reset_index(name="trade_count"); y=y.merge(counts,on=["scenario_id","scenario","timeframe","symbol","year"])
    y.to_parquet(outdir/"annual_symbol.parquet",index=False)
    agg=y.groupby(["scenario_id","scenario","timeframe","year"]).agg(annual_return=("annual_return","mean"),symbols=("symbol","nunique"),trades=("trade_count","sum")).reset_index()
    agg.to_csv(outdir/"annual_results.csv",index=False)
    overall=s.groupby(["scenario_id","scenario","timeframe"]).agg(total_return=("total_return","mean"),win_rate=("win_rate","mean"),avg_r=("avg_r","mean"),trades=("trades","sum"),symbols=("symbol","nunique")).reset_index()
    # Keep zero-signal scenarios visible instead of silently dropping them.
    grid=[]
    for sid,title in scenarios:
        for tf in cfg["timeframes"]:
            if 161<=sid<=180 and tf!="1h": continue
            grid.append({"scenario_id":sid,"scenario":title,"timeframe":tf})
    overall=pd.DataFrame(grid).merge(overall,on=["scenario_id","scenario","timeframe"],how="left")
    for col in ("total_return","win_rate","avg_r","trades","symbols"): overall[col]=overall[col].fillna(0)
    overall.to_csv(outdir/"overall_results.csv",index=False)


if __name__=="__main__": main()

