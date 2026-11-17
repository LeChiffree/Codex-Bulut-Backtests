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

- Kaynak: `D:/1mdatabinance` aylık Binance USD-M CSV arşivi (`1h` klasörü).
- 58 sembol; kapsam sembolün listelenme tarihine göre **2022-08-01 → 2026-08-31**.
- `prepare_data.py` bu arşivi reponun beklediği `data/1h/<SEMBOL>.parquet`
  düzenine çevirir.
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
| İşlem | 14.975.071 | 7.302.088 | −7.672.983 (bloke %51,24) |
| Kazanma oranı | %47,95 | %47,32 | −0,63 puan |
| Ort. işlem getirisi | −0,0285% | −0,0368% | −0,0083 puan |
| Ort. R | −0,0581 | −0,0748 | −0,0167 |
| 2026 ort. getiri | −0,0267% | −0,0361% | −0,0094 puan |

Zaman dilimi bazında:

| TF | Normal işlem | Singular işlem | Bloke | Bloke % | Normal ort. | Singular ort. |
|---|---:|---:|---:|---:|---:|---:|
| 1h | 12.026.432 | 6.436.553 | 5.589.879 | 46,48 | −0,0351% | −0,0411% |
| 4h | 2.516.049 | 742.253 | 1.773.796 | 70,50 | −0,0050% | −0,0087% |
| 1d | 391.482 | 111.265 | 280.217 | 71,58 | +0,0191% | +0,0221% |
| 1w | 41.108 | 12.017 | 29.091 | 70,77 | +0,0256% | +0,0065% |

Yorum:

- Yüksek zaman dilimleri işlemlerin ~%70'ini kaybediyor; 1h görece daha az
  etkileniyor (%46,5) çünkü sinyaller zaten sık ve kısa ömürlü.
- En anlamlı etki 1d tarafında: ortalama getiri **+0,0191% → +0,0221%**.
- Tek tek bakıldığında, en az 100 singular işlemi olan 624 senaryo x TF
  kombinasyonunun **212'si** ortalama getiride iyileşiyor. En iyi iyileşmeler:
  - `125 1d`: +0,0128% → +0,0875% (+0,0747 puan, 3.078 sinyal bloke)
  - `114 1w`: +0,0657% → +0,1308% (+0,0650 puan)
  - `133 1d` ve `138 1d`: +0,0784% → +0,1434% (+0,0650 puan)
  - `49 1d`: +0,0591% → +0,1211% (+0,0620 puan)
- En kötü etkilenenler `101 1w` (−0,0861 puan) ve `217 1d` (−0,0838 puan).

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
