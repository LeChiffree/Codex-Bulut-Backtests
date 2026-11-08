#!/usr/bin/env python3
"""Pre-aggregate refined trades for the split-period dashboard."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import duckdb, pandas as pd

BINS=[0,1,3,9,24,72,168,720,10**9]
LABELS=['<1 saat','1–3 saat','3–9 saat','9–24 saat','1–3 gün','3–7 gün','1–4 hafta','4+ hafta']

def records(df):
    return json.loads(df.to_json(orient='records',date_format='iso'))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent); a=ap.parse_args()
    root=a.root; out=root/'dashboard_v2'/'data'; out.mkdir(parents=True,exist_ok=True)
    glob=str(root/'results/refined_5m/by_symbol/*_trades.parquet')
    con=duckdb.connect(str(root/'results/dashboard_v2.duckdb')); con.execute('PRAGMA threads=4'); con.execute("PRAGMA memory_limit='6GB'")
    con.execute('DROP VIEW IF EXISTS t')
    # Existing refined parquet files contain exits written with the old unit.
    # epoch_us(exit_time)/1000 is the intended Unix timestamp in seconds.
    con.execute(f"""CREATE VIEW t AS SELECT scenario_id, scenario, timeframe, symbol, entry_time,
      to_timestamp(epoch_us(exit_time)/1000.0) AS exit_fixed, return AS ret, side, exit_reason,
      greatest(0.0,(epoch_us(exit_time)*1000-epoch_us(entry_time))/3600000000.0) AS hours
      FROM read_parquet('{glob}')""")
    con.execute('DROP TABLE IF EXISTS summary')
    con.execute("""CREATE TABLE summary AS
      SELECT scenario_id, any_value(scenario) scenario, timeframe, 'all' period,
       count(*) trades, count_if(ret>0) wins, count_if(ret<=0) losses,
       sum(CASE WHEN ret>0 THEN ret ELSE 0 END) profit,
       sum(CASE WHEN ret<0 THEN ret ELSE 0 END) loss,
       avg(ret) avg_trade, avg(hours) avg_hours
      FROM t GROUP BY scenario_id,timeframe UNION ALL
      SELECT scenario_id, any_value(scenario), timeframe, '2026',count(*),count_if(ret>0),count_if(ret<=0),
       sum(CASE WHEN ret>0 THEN ret ELSE 0 END),sum(CASE WHEN ret<0 THEN ret ELSE 0 END),avg(ret),avg(hours)
      FROM t WHERE year(entry_time)=2026 GROUP BY scenario_id,timeframe""")
    con.execute('DROP TABLE IF EXISTS calendar')
    con.execute("""CREATE TABLE calendar AS WITH x AS (
      SELECT scenario_id,timeframe,entry_time,ret,
       unnest(['day','week','month','season']) grain,
       unnest([strftime(entry_time,'%Y-%m-%d'),strftime(date_trunc('week',entry_time),'%Y-%m-%d'),strftime(entry_time,'%Y-%m'),
        concat(year(entry_time),'-',CASE WHEN month(entry_time) IN (12,1,2) THEN 'Kış' WHEN month(entry_time) IN (3,4,5) THEN 'İlkbahar' WHEN month(entry_time) IN (6,7,8) THEN 'Yaz' ELSE 'Sonbahar' END)]) bucket
      FROM t)
      SELECT scenario_id,timeframe,grain,bucket,
       sum(CASE WHEN ret>0 THEN ret ELSE 0 END) profit,sum(CASE WHEN ret<0 THEN ret ELSE 0 END) loss,count(*) trades
      FROM x GROUP BY ALL""")
    con.execute('DROP TABLE IF EXISTS duration')
    cases=' '.join(f"WHEN hours>={BINS[i]} AND hours<{BINS[i+1]} THEN '{LABELS[i]}'" for i in range(len(LABELS)))
    con.execute(f"""CREATE TABLE duration AS SELECT scenario_id,timeframe,'all' period,
      CASE {cases} ELSE '4+ hafta' END bucket,count(*) trades,
      sum(CASE WHEN ret>0 THEN ret ELSE 0 END) profit,sum(CASE WHEN ret<0 THEN ret ELSE 0 END) loss
      FROM t GROUP BY scenario_id,timeframe,bucket UNION ALL SELECT scenario_id,timeframe,'2026',
      CASE {cases} ELSE '4+ hafta' END bucket,count(*),sum(CASE WHEN ret>0 THEN ret ELSE 0 END),sum(CASE WHEN ret<0 THEN ret ELSE 0 END)
      FROM t WHERE year(entry_time)=2026 GROUP BY scenario_id,timeframe,bucket""")
    con.execute('DROP TABLE IF EXISTS coin')
    con.execute("""CREATE TABLE coin AS SELECT scenario_id,timeframe,'all' period,symbol,count(*) trades,
      sum(CASE WHEN ret>0 THEN ret ELSE 0 END) profit,sum(CASE WHEN ret<0 THEN ret ELSE 0 END) loss
      FROM t GROUP BY scenario_id,timeframe,symbol UNION ALL SELECT scenario_id,timeframe,'2026',symbol,count(*),
      sum(CASE WHEN ret>0 THEN ret ELSE 0 END),sum(CASE WHEN ret<0 THEN ret ELSE 0 END)
      FROM t WHERE year(entry_time)=2026 GROUP BY scenario_id,timeframe,symbol""")
    con.execute('DROP TABLE IF EXISTS breakdown')
    con.execute("""CREATE TABLE breakdown AS WITH x AS (
      SELECT scenario_id,timeframe,entry_time,ret,
       unnest(['side','exit','weekday']) kind,
       unnest([side,exit_reason,strftime(entry_time,'%w')||' · '||strftime(entry_time,'%A')]) bucket FROM t)
      SELECT scenario_id,timeframe,'all' period,kind,bucket,count(*) trades,
       sum(CASE WHEN ret>0 THEN ret ELSE 0 END) profit,sum(CASE WHEN ret<0 THEN ret ELSE 0 END) loss
      FROM x GROUP BY scenario_id,timeframe,kind,bucket UNION ALL
      SELECT scenario_id,timeframe,'2026',kind,bucket,count(*),
       sum(CASE WHEN ret>0 THEN ret ELSE 0 END),sum(CASE WHEN ret<0 THEN ret ELSE 0 END)
      FROM x WHERE year(entry_time)=2026 GROUP BY scenario_id,timeframe,kind,bucket""")
    scenarios=con.execute('SELECT DISTINCT scenario_id,scenario,timeframe FROM summary ORDER BY scenario_id,timeframe').df()
    (out/'scenarios.json').write_text(json.dumps(records(scenarios),ensure_ascii=False))
    filters=pd.read_csv(root/'results/filter_overall_results.csv')
    names=json.loads((root/'results/filter_definitions.json').read_text())
    for (sid,tf),_ in scenarios.groupby(['scenario_id','timeframe']):
        payload={}
        for table in ['summary','calendar','duration','coin','breakdown']:
            df=con.execute(f'SELECT * FROM {table} WHERE scenario_id=? AND timeframe=?',[int(sid),tf]).df()
            # The file name already identifies these dimensions. Repeating them
            # on every chart row adds tens of MiB to the static deployment.
            df=df.drop(columns=['scenario_id','timeframe'],errors='ignore')
            payload[table]=records(df)
        ff=filters[(filters.scenario_id==sid)&(filters.timeframe==tf)].copy()
        ff['filter_name']=ff.filter_id.map(names); payload['filters']=records(ff[['filter_id','filter_name','total_return','win_rate','avg_r','trades']])
        (out/f'{int(sid)}_{tf}.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')))
    print(f'Built {len(scenarios)} scenario/timeframe datasets in {out}')
if __name__=='__main__': main()
