# Binance Futures Backtest Dashboard

Binance USD-M Futures sözleşmeleri için 1h, 4h, 1d ve 1w sinyallerini 5 dakikalık mumlarla kronolojik olarak çözen, kaldıraçsız backtest ve interaktif dashboard projesi.

## Özellikler

- 220 kural tabanlı senaryo
- 1x azami kaldıraç
- Komisyon ve slippage dahil net sonuçlar
- 5m intrabar çıkış çözümlemesi
- Aynı 5m mumda belirsizlik olduğunda korumacı stop-first kuralı
- 56 piyasa ve rejim filtresi
- Tüm dönem ve 2026 karşılaştırma dashboardu
- Kâr/zarar, süre, coin, drawdown, özsermaye ve filtre grafikleri

## Kurulum

Python 3.12 ve Node.js 20+ önerilir.

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas numpy pyarrow duckdb requests numba
```

## İş akışı

```bash
python download_data.py
python backtest.py
python refine_5m.py
python aggregate_refined.py
python build_filters.py
python build_dashboard_v2.py
```

Dashboard veri çıktısını `dashboard/data/` altına kopyaladıktan sonra:

```bash
cd dashboard
npm start
```

## Veri politikası

Ham Binance verileri ve üretilmiş sonuç dosyaları boyutları nedeniyle repoya eklenmez. İndirme ve üretim kodları repoda bulunur.

## Canlı dashboard

https://binance-futures-backtest-dashboard.hikmet-onur21.chatgpt.site
