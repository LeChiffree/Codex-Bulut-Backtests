#!/usr/bin/env python3
from pathlib import Path
import re,json,duckdb,pandas as pd
R=Path(__file__).resolve().parent;O=R/'results';G=str(O/'refined_5m/by_symbol/*_trades.parquet');con=duckdb.connect(str(O/'refined_5m/aggregate.duckdb'));con.execute("PRAGMA threads=4; PRAGMA memory_limit='1GB'; PRAGMA temp_directory='{}'".format(str(O/'tmp')))
con.execute("COPY (SELECT scenario_id,any_value(scenario) scenario,timeframe,symbol,count(*) trades,avg(CASE WHEN r_multiple>0 THEN 1.0 ELSE 0.0 END) win_rate,avg(r_multiple) avg_r,product(1+\"return\")-1 total_return,min(r_multiple) max_loss_r FROM read_parquet(?) GROUP BY scenario_id,timeframe,symbol) TO ? (FORMAT PARQUET,COMPRESSION ZSTD)",[G,str(O/'summary_symbol.parquet')])
con.execute("COPY (SELECT scenario_id,any_value(scenario) scenario,timeframe,symbol,year(entry_time)::INTEGER AS \"year\",product(1+\"return\")-1 annual_return,count(*) trade_count FROM read_parquet(?) GROUP BY scenario_id,timeframe,symbol,year(entry_time)) TO ? (FORMAT PARQUET,COMPRESSION ZSTD)",[G,str(O/'annual_symbol.parquet')])
con.execute("COPY (SELECT scenario_id,any_value(scenario) scenario,timeframe,year,avg(annual_return) annual_return,count(DISTINCT symbol) symbols,sum(trade_count) trades FROM read_parquet(?) GROUP BY scenario_id,timeframe,year ORDER BY scenario_id,timeframe,year) TO ? (HEADER,DELIMITER ',')",[str(O/'annual_symbol.parquet'),str(O/'annual_results.csv')])
overall=con.execute("SELECT scenario_id,any_value(scenario) scenario,timeframe,avg(total_return) total_return,avg(win_rate) win_rate,avg(avg_r) avg_r,sum(trades)::BIGINT trades,count(DISTINCT symbol)::BIGINT symbols FROM read_parquet(?) GROUP BY scenario_id,timeframe",[str(O/'summary_symbol.parquet')]).df();sc=[(int(a),b) for a,b in re.findall(r'^## (\d{3}) — (.+)$',(R/'strategy.md').read_text(),re.M)];cfg=json.loads((R/'config.json').read_text());grid=[]
for sid,title in sc:
 for tf in cfg['timeframes']:
  if 161<=sid<=180 and tf!='1h':continue
  grid.append({'scenario_id':sid,'scenario':title,'timeframe':tf})
overall=pd.DataFrame(grid).merge(overall.drop(columns='scenario'),on=['scenario_id','timeframe'],how='left').fillna(0);overall.to_csv(O/'overall_results.csv',index=False);print('refined overall',len(overall))
