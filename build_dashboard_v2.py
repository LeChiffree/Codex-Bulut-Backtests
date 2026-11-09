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
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent); ap.add_argument('--reuse-allocation',action='store_true'); a=ap.parse_args()
    root=a.root; out=root/'dashboard_v2'/'data'; out.mkdir(parents=True,exist_ok=True)
    glob=str(root/'results/refined_5m/by_symbol/*_trades.parquet')
    con=duckdb.connect(str(root/'results/dashboard_v2.duckdb')); con.execute('PRAGMA threads=2'); con.execute("PRAGMA memory_limit='4GB'"); con.execute("PRAGMA preserve_insertion_order=false"); con.execute(f"PRAGMA temp_directory='{root/'results/dashboard_tmp'}'"); con.execute("PRAGMA max_temp_directory_size='40GB'")
    con.execute('DROP VIEW IF EXISTS t')
    # Existing refined parquet files contain exits written with the old unit.
    # epoch_us(exit_time)/1000 is the intended Unix timestamp in seconds.
    con.execute(f"""CREATE VIEW t AS SELECT scenario_id, scenario, timeframe, symbol, entry_time,
      to_timestamp(epoch_us(exit_time)/1000.0) AS exit_fixed, return AS ret, side, exit_reason,
      greatest(0.0,(epoch_us(exit_time)*1000-epoch_us(entry_time))/3600000000.0) AS hours
      FROM read_parquet('{glob}')""")
    # Fractionally allocate simultaneous trades so aggregate open risk cannot
    # exceed 1.5% (three 0.5%-risk slots). Trades in the same entry batch share
    # the available risk equally. This makes cross-symbol totals capital aware.
    if not a.reuse_allocation:
        con.execute('DROP TABLE IF EXISTS active_entry')
        con.execute("CREATE TABLE active_entry(scenario_id BIGINT,timeframe VARCHAR,ts TIMESTAMPTZ,allocation DOUBLE)")
        keys=con.execute("SELECT DISTINCT scenario_id,timeframe FROM t ORDER BY scenario_id,timeframe").fetchall()
        for sid,tf in keys:
            con.execute("""INSERT INTO active_entry WITH events AS (
              SELECT entry_time ts,count(*) enter_n,0::BIGINT exit_n FROM t WHERE scenario_id=? AND timeframe=? GROUP BY 1
              UNION ALL SELECT exit_fixed ts,0::BIGINT,count(*) exit_n FROM t WHERE scenario_id=? AND timeframe=? GROUP BY 1
            ), grouped AS (SELECT ts,sum(enter_n) enter_n,sum(exit_n) exit_n FROM events GROUP BY 1),
            running AS (SELECT *,sum(enter_n-exit_n) OVER(ORDER BY ts ROWS UNBOUNDED PRECEDING) active_after FROM grouped)
            SELECT ?,?,ts,least(1.0,3.0/greatest(active_after,1)) FROM running WHERE enter_n>0""",
            [int(sid),tf,int(sid),tf,int(sid),tf])
    con.execute('DROP VIEW IF EXISTS ta')
    con.execute("""CREATE VIEW ta AS SELECT t.*,t.ret*a.allocation pret,a.allocation
      FROM t JOIN active_entry a ON t.scenario_id=a.scenario_id AND t.timeframe=a.timeframe AND t.entry_time=a.ts""")
    con.execute('DROP TABLE IF EXISTS summary')
    con.execute("""CREATE TABLE summary AS
      SELECT scenario_id, any_value(scenario) scenario, timeframe, 'all' period,
       count(*) trades, count_if(ret>0) wins, count_if(ret<=0) losses,
       sum(CASE WHEN pret>0 THEN pret ELSE 0 END) profit,
       sum(CASE WHEN pret<0 THEN pret ELSE 0 END) loss,
       avg(pret) avg_trade, avg(hours) avg_hours
      FROM ta GROUP BY scenario_id,timeframe UNION ALL
      SELECT scenario_id, any_value(scenario), timeframe, '2026',count(*),count_if(ret>0),count_if(ret<=0),
       sum(CASE WHEN pret>0 THEN pret ELSE 0 END),sum(CASE WHEN pret<0 THEN pret ELSE 0 END),avg(pret),avg(hours)
      FROM ta WHERE year(exit_fixed)=2026 GROUP BY scenario_id,timeframe""")
    con.execute('DROP TABLE IF EXISTS calendar')
    con.execute("""CREATE TABLE calendar AS WITH x AS (
      SELECT scenario_id,timeframe,exit_fixed event_time,pret,
       unnest(['day','week','month','season']) grain,
       unnest([strftime(event_time,'%Y-%m-%d'),strftime(date_trunc('week',event_time),'%Y-%m-%d'),strftime(event_time,'%Y-%m'),
        concat(year(event_time),'-',CASE WHEN month(event_time) IN (12,1,2) THEN 'Kış' WHEN month(event_time) IN (3,4,5) THEN 'İlkbahar' WHEN month(event_time) IN (6,7,8) THEN 'Yaz' ELSE 'Sonbahar' END)]) bucket
      FROM ta)
      SELECT scenario_id,timeframe,grain,bucket,
       sum(CASE WHEN pret>0 THEN pret ELSE 0 END) profit,sum(CASE WHEN pret<0 THEN pret ELSE 0 END) loss,count(*) trades
      FROM x GROUP BY ALL""")
    con.execute('DROP TABLE IF EXISTS duration')
    cases=' '.join(f"WHEN hours>={BINS[i]} AND hours<{BINS[i+1]} THEN '{LABELS[i]}'" for i in range(len(LABELS)))
    con.execute(f"""CREATE TABLE duration AS SELECT scenario_id,timeframe,'all' period,
      CASE {cases} ELSE '4+ hafta' END bucket,count(*) trades,
      sum(CASE WHEN pret>0 THEN pret ELSE 0 END) profit,sum(CASE WHEN pret<0 THEN pret ELSE 0 END) loss
      FROM ta GROUP BY scenario_id,timeframe,bucket UNION ALL SELECT scenario_id,timeframe,'2026',
      CASE {cases} ELSE '4+ hafta' END bucket,count(*),sum(CASE WHEN pret>0 THEN pret ELSE 0 END),sum(CASE WHEN pret<0 THEN pret ELSE 0 END)
      FROM ta WHERE year(exit_fixed)=2026 GROUP BY scenario_id,timeframe,bucket""")
    con.execute('DROP TABLE IF EXISTS coin')
    con.execute("""CREATE TABLE coin AS SELECT scenario_id,timeframe,'all' period,symbol,count(*) trades,
      sum(CASE WHEN pret>0 THEN pret ELSE 0 END) profit,sum(CASE WHEN pret<0 THEN pret ELSE 0 END) loss
      FROM ta GROUP BY scenario_id,timeframe,symbol UNION ALL SELECT scenario_id,timeframe,'2026',symbol,count(*),
      sum(CASE WHEN pret>0 THEN pret ELSE 0 END),sum(CASE WHEN pret<0 THEN pret ELSE 0 END)
      FROM ta WHERE year(exit_fixed)=2026 GROUP BY scenario_id,timeframe,symbol""")
    con.execute('DROP TABLE IF EXISTS breakdown')
    con.execute("""CREATE TABLE breakdown AS WITH x AS (
      SELECT scenario_id,timeframe,entry_time,exit_fixed,pret,
       unnest(['side','exit','weekday']) kind,
       unnest([side,exit_reason,strftime(entry_time,'%w')||' · '||strftime(entry_time,'%A')]) bucket FROM ta)
      SELECT scenario_id,timeframe,'all' period,kind,bucket,count(*) trades,
       sum(CASE WHEN pret>0 THEN pret ELSE 0 END) profit,sum(CASE WHEN pret<0 THEN pret ELSE 0 END) loss
      FROM x GROUP BY scenario_id,timeframe,kind,bucket UNION ALL
      SELECT scenario_id,timeframe,'2026',kind,bucket,count(*),
       sum(CASE WHEN pret>0 THEN pret ELSE 0 END),sum(CASE WHEN pret<0 THEN pret ELSE 0 END)
      FROM x WHERE year(exit_fixed)=2026 GROUP BY scenario_id,timeframe,kind,bucket""")
    scenarios=pd.read_csv(root/'results/overall_results.csv')[['scenario_id','scenario','timeframe']].drop_duplicates().sort_values(['scenario_id','timeframe'])
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
