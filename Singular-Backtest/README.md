# Singular-Backtest — Tek Açık İşlem Kuralı

Bu klasör, repo kökündeki normal backtestten **tamamen ayrı** çalışan bir varyanttır.
Normal sonuçlara (`results/`) dokunmaz; tüm çıktılar `Singular-Backtest/results/`
altında üretilir.

## Kural

Her **strateji (senaryo)** için bir coinde **aynı anda en fazla bir açık işlem**
bulunabilir.

- Coinde açık işlem yoksa gelen sinyal onaylanır, işlem açılır.
- Coinde aynı senaryoya ait açık işlem varken yeni sinyal gelirse **sinyal bloke
  edilir** (işlem açılmaz, kuyruğa da alınmaz).
- Kural, aynı senaryonun **tüm zaman dilimleri** (1h/4h/1d/1w) ve **tüm yönleri**
  (long/short) için geçerlidir. Yani 1h long açıkken gelen 4h short sinyali de
  bloke olur.

Aynı sinyal zamanına birden fazla aday düşerse sıralama deterministiktir:
önce `1h > 4h > 1d > 1w`, eşitlikte `long > short`.

## Kapsam seçenekleri

| `--scope` | Anlam |
|---|---|
| `scenario` (varsayılan) | Kilit anahtarı `senaryo + coin`. Zaman dilimi ve yön fark etmeksizin tek işlem. |
| `scenario_tf` | Kilit anahtarı `senaryo + zaman dilimi + coin`. Sadece aynı TF içinde tek işlem (karşılaştırma için). |

## Veri

- Kaynak: `D:/1mdatabinance`. Eski aylık `1h` CSV arşivi, günlük `1m`
  Parquet arşiviyle birleştirilir; çakışan saatlerde güncel 1m kaynağı kazanır.
- `selected_symbols.txt` içindeki 60 sembol; kapsam sembolün listelenme tarihine
  göre **2020-01-01 → 2026-11-17**.
- `prepare_data.py`, 1m mumları UTC saatlerine doğru OHLCV kurallarıyla
  toplar ve reponun beklediği `data/1h/<SEMBOL>.parquet` düzenine çevirir.
- Tüm işlem mekaniği kök motordan (`backtest.py`) aynen alınır: 1.5 ATR stop,
  1R/2R kısmi kâr al, EMA20 takip çıkışı, 500 bar timeout, stop-first önceliği,
  komisyon + slippage.

## Çalıştırma

```bash
# 1) veriyi hazırla (D:/1mdatabinance/1h -> data/1h)
python Singular-Backtest/prepare_data.py

# 2) tam koşu (58 sembol x 220 senaryo x 4 TF x 2 yön)
python Singular-Backtest/run_singular.py --workers 10

# 3) doğrulama (çakışma / alt küme kontrolü)
python Singular-Backtest/verify_singular.py

# 4) özet
python Singular-Backtest/summarize_singular.py --min-trades 500
```

Faydalı bayraklar:

- `--from-cache`: `normal_trades/` parquetlerini yeniden kullanır, sadece
  singular seçimi ve agregasyonu yeniden üretir.
- `--symbols BTCUSDT ETHUSDT`: sembol alt kümesi.
- `--scope scenario_tf`: TF bazlı kilit.
- `--force`: cache'i yok sayar.

## Çıktılar (`results/`)

| Dosya | İçerik |
|---|---|
| `normal_trades/<SEMBOL>.parquet` | Motorun ürettiği tüm aday işlemler (kilit öncesi). |
| `singular_trades/<SEMBOL>.parquet` | Kural sonrası kabul edilen işlemler. |
| `singular_summary.csv` | Senaryo x TF metrikleri (normal / singular / bloke). |
| `singular_coins.csv` | Coin bazında kırılım (42.484 satır). |
| `singular_results.json` | Dashboard için kompakt payload (özet + strateji + senaryo + coin). |
| `run_manifest.json` | Sembol bazında normal/singular işlem sayıları. |

`results/` gitignore'dadır. Dashboard'un kullandığı iki dosya bu klasörün köküne
de kopyalanır:

- `Singular-Backtest/singular_results.json`
- `Singular-Backtest/run_manifest.json`

## Sonuç özeti

| | Normal | Singular | Fark |
|---|---:|---:|---:|
| İşlem | 21.003.940 | 9.985.822 | −11.018.118 (bloke %52,46) |
| Kazanma oranı | %48,07 | %47,50 | −0,57 puan |
| Ort. işlem getirisi | −0,0248% | −0,0325% | −0,0077 puan |
| Ort. R | −0,0506 | −0,0662 | −0,0156 |

Zaman dilimi bazında:

| TF | Normal işlem | Singular işlem | Bloke | Bloke % | Normal ort. | Singular ort. |
|---|---:|---:|---:|---:|---:|---:|
| 1h | 16.842.220 | 8.798.460 | 8.043.760 | 47,76 | −0,0313% | −0,0368% |
| 4h | 3.545.674 | 1.014.067 | 2.531.607 | 71,40 | −0,0026% | −0,0056% |
| 1d | 556.798 | 155.570 | 401.228 | 72,06 | +0,0233% | +0,0292% |
| 1w | 59.248 | 17.725 | 41.523 | 70,08 | +0,0490% | +0,0218% |

Yorum:

- Güncel tam koşuda toplam adayların %52,46'sı tek-açık-işlem kuralı nedeniyle
  bloke edildi.
- En az 500 singular işlem koşulunda `133 1d` ve `138 1d`, normalde
  +0,0935% ortalama getiriden singular koşuda +0,1741%'e yükseldi.
- `125 1d`, 4.320 sinyal bloke edildikten sonra +0,0389%'dan +0,1241%'e
  yükseldi. Bunlar tarihsel sonuçlardır; bağımsız ileri dönem doğrulaması değildir.

## Doğrulama

`verify_singular.py` üç şeyi kontrol eder ve hepsi **0 ihlal** ile geçer:

1. Aynı `senaryo + coin` için çakışan singular işlem yok.
2. Normal motorda aynı `senaryo + coin + TF + yön` için çakışma yok (motor
   değişmezı).
3. Her singular işlem normal aday kümesinde birebir mevcut.

## Notlar

- ATR ≈ 0 olan bozuk barlar (LITUSDT 4h, 3 adet) elenir; bunlar `stop_pct`
  sıfıra yakın olduğu için R çarpanını anlamsız büyütüyordu.
- `strategy.md` UTF-8 olarak okunur (Türkçe karakterler).
- Bloke oranı, aynı senaryoda aynı coinde aynı anda birden fazla sinyalin
  biriktiği durumlarda doğal olarak yüksektir; bu, kuralın çalıştığının
  göstergesidir.

## Filtre düzeyi tekil sonuçlar

Normal laboratuvar 56 filtreyi işlem sonrası uygular. `run_filters_singular.py`,
aynı filtre durumlarını kullanarak **her filtre için ayrı** tekil tarama yapar ve
`results/filter_singular.json` üretir:

```powershell
python build_filters.py                       # results/filter_states.parquet (ağ gerekir)
python Singular-Backtest/run_filters_singular.py
```

Çıktı anahtarı `scenario_id|timeframe|filter_id`; değerler `trades`, `wins`,
`losses`, `retAll`, `ret2026`, `winRatio`, `winHoldH`, `profitDays`, `lossDays`.
All-in dashboard, bu dosyayı senaryo adı + TF + filtre etiketiyle eşleştirip
Allinone tablosundaki `(S)` sütunlarını doldurur.

`filter_normal.json` aynı aday işlem ve filtre durumlarından **normal** (tekil
olmayan) metrikleri üretir; dashboard Codex normal sütunlarını bu dosyayla
hizalayıp kaynak tablodaki şişmiş işlem sayılarını düzeltir.
