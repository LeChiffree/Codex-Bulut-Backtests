# Filtre Kataloğu

Backtestte kullanılan 56 filtre aşağıdadır. `baseline` filtresiz referans sonucudur. Tüm filtreler sinyal anından önce bilinen veriyle uygulanır.

| No | Kimlik | Açıklama |
|---:|---|---|
| 1 | `baseline` | Filtresiz |
| 2 | `btc_1h_above_ema20` | BTC 1h above ema20 |
| 3 | `btc_1h_above_ema50` | BTC 1h above ema50 |
| 4 | `btc_1h_above_ema200` | BTC 1h above ema200 |
| 5 | `btc_1h_ema20_gt_50` | BTC 1h ema20 gt 50 |
| 6 | `btc_1h_ema50_gt_200` | BTC 1h ema50 gt 200 |
| 7 | `btc_1h_rsi_gt_50` | BTC 1h rsi gt 50 |
| 8 | `btc_1h_return_pos` | BTC 1h return pos |
| 9 | `btc_1h_volz_gt_0` | BTC 1h volz gt 0 |
| 10 | `btc_1h_volz_gt_1` | BTC 1h volz gt 1 |
| 11 | `btc_4h_above_ema20` | BTC 4h above ema20 |
| 12 | `btc_4h_above_ema50` | BTC 4h above ema50 |
| 13 | `btc_4h_above_ema200` | BTC 4h above ema200 |
| 14 | `btc_4h_ema20_gt_50` | BTC 4h ema20 gt 50 |
| 15 | `btc_4h_ema50_gt_200` | BTC 4h ema50 gt 200 |
| 16 | `btc_4h_rsi_gt_50` | BTC 4h rsi gt 50 |
| 17 | `btc_4h_return_pos` | BTC 4h return pos |
| 18 | `btc_4h_adx_gt_20` | BTC 4h adx gt 20 |
| 19 | `btc_4h_volz_gt_0` | BTC 4h volz gt 0 |
| 20 | `btc_4h_volz_gt_1` | BTC 4h volz gt 1 |
| 21 | `btc_1d_above_ema20` | BTC 1d above ema20 |
| 22 | `btc_1d_above_ema50` | BTC 1d above ema50 |
| 23 | `btc_1d_above_ema200` | BTC 1d above ema200 |
| 24 | `btc_1d_ema20_gt_50` | BTC 1d ema20 gt 50 |
| 25 | `btc_1d_ema50_gt_200` | BTC 1d ema50 gt 200 |
| 26 | `btc_1d_rsi_gt_50` | BTC 1d rsi gt 50 |
| 27 | `btc_1d_return_pos` | BTC 1d return pos |
| 28 | `btc_1d_adx_gt_20` | BTC 1d adx gt 20 |
| 29 | `btc_1d_atr_high` | BTC 1d atr high |
| 30 | `btc_1d_atr_low` | BTC 1d atr low |
| 31 | `btc_bull_regime` | BTC boğa rejimi: fiyat>EMA200 ve EMA50 yükseliyor |
| 32 | `btc_bear_regime` | BTC ayı rejimi: fiyat<EMA200 ve EMA50 düşüyor |
| 33 | `btc_sideways_adx_lt20` | BTC yatay rejim: günlük ADX<20 |
| 34 | `btc_squeeze_low20pct` | BTC sıkışma: BB genişliği 1 yıllık alt %20 |
| 35 | `btc_donchian20_breakout` | BTC 20 günlük üst kanal kırılımı |
| 36 | `btc_donchian20_breakdown` | BTC 20 günlük alt kanal kırılımı |
| 37 | `usd_below_ema20` | Dolar geniş endeksi below ema20 |
| 38 | `usd_below_ema50` | Dolar geniş endeksi below ema50 |
| 39 | `usd_below_ema200` | Dolar geniş endeksi below ema200 |
| 40 | `usd_ema20_lt50` | Dolar geniş endeksi ema20 lt50 |
| 41 | `usd_ema50_lt200` | Dolar geniş endeksi ema50 lt200 |
| 42 | `usd_return_negative` | Dolar geniş endeksi return negative |
| 43 | `usd_mom20_negative` | Dolar geniş endeksi mom20 negative |
| 44 | `usd_rsi_lt50` | Dolar geniş endeksi rsi lt50 |
| 45 | `usd_vol_high` | Dolar geniş endeksi vol high |
| 46 | `usd_vol_low` | Dolar geniş endeksi vol low |
| 47 | `breadth_above50_gt60` | Piyasa genişliği: coinlerin >%60 EMA50 üstünde |
| 48 | `breadth_above50_lt40` | Piyasa genişliği: coinlerin <%40 EMA50 üstünde |
| 49 | `breadth_positive_gt60` | Piyasa genişliği: coinlerin >%60 günlük pozitif |
| 50 | `breadth_positive_lt40` | Piyasa genişliği: coinlerin <%40 günlük pozitif |
| 51 | `fng_ge_25` | Korku-Açgözlülük >= 25 |
| 52 | `fng_ge_40` | Korku-Açgözlülük >= 40 |
| 53 | `fng_ge_50` | Korku-Açgözlülük >= 50 |
| 54 | `fng_ge_60` | Korku-Açgözlülük >= 60 |
| 55 | `fng_ge_75` | Korku-Açgözlülük >= 75 |
| 56 | `fng_le_25` | Korku-Açgözlülük <= 25 |
