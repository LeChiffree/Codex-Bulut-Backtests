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
- `D:/1mdatabinance/1m` altındaki **526 coin klasörünün tamamı**; kapsam her
  sembolün mevcut veri tarihinden **2026-11-17** sonuna kadar.
- `prepare_data.py`, 1m mumları UTC saatlerine doğru OHLCV kurallarıyla
  toplar ve reponun beklediği `data/1h/<SEMBOL>.parquet` düzenine çevirir.
- Tüm işlem mekaniği kök motordan (`backtest.py`) aynen alınır: 1.5 ATR stop,
  1R/2R kısmi kâr al, EMA20 takip çıkışı, 500 bar timeout, stop-first önceliği,
  komisyon + slippage.

## Çalıştırma

```bash
# 1) veriyi hazırla (D:/1mdatabinance/1h -> data/1h)
python Singular-Backtest/prepare_data.py

# D:/1mdatabinance/1m altındaki bütün coin klasörleri
python Singular-Backtest/prepare_data.py --all-symbols

# 2) tam koşu (526 coin x 220 senaryo x 4 TF x 2 yön)
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
- `--aggregate-only`: mevcut parquetlerden yalnızca özetleri yeniden üretir.

Geniş coin evreninde agregasyon, belleği taşırmamak için otomatik olarak
DuckDB ile disk üstünde yapılır.

## Çıktılar (`results/`)

| Dosya | İçerik |
|---|---|
| `normal_trades/<SEMBOL>.parquet` | Motorun ürettiği tüm aday işlemler (kilit öncesi). |
| `singular_trades/<SEMBOL>.parquet` | Kural sonrası kabul edilen işlemler. |
| `singular_summary.csv` | Senaryo x TF metrikleri (normal / singular / bloke). |
| `singular_coins.csv` | Coin bazında kırılım (374.013 satır). |
| `singular_results.json` | Dashboard için kompakt payload (özet + strateji + senaryo + coin). |
| `run_manifest.json` | Sembol bazında normal/singular işlem sayıları. |

`results/` gitignore'dadır. Dashboard'un kullandığı iki dosya bu klasörün köküne
de kopyalanır:

- `Singular-Backtest/singular_results.json`
- `Singular-Backtest/run_manifest.json`

## Sonuç özeti

| | Normal | Singular | Fark |
|---|---:|---:|---:|
| İşlem | 121.037.497 | 58.027.196 | −63.010.301 (bloke %52,06) |
| Kazanma oranı | %47,80 | %47,15 | −0,65 puan |
| Ort. işlem getirisi | −0,0275% | −0,0343% | −0,0068 puan |
| Ort. R | −0,1757 | −0,2429 | −0,0672 |

Zaman dilimi bazında:

| TF | Normal işlem | Singular işlem | Bloke | Bloke % | Normal ort. | Singular ort. |
|---|---:|---:|---:|---:|---:|---:|
| 1h | 97.445.225 | 51.235.067 | 46.210.158 | 47,42 | −0,0318% | −0,0372% |
| 4h | 20.299.573 | 5.854.098 | 14.445.475 | 71,16 | −0,0107% | −0,0146% |
| 1d | 3.042.510 | 866.324 | 2.176.186 | 71,53 | −0,0050% | −0,0017% |
| 1w | 250.189 | 71.707 | 178.482 | 71,34 | +0,0091% | −0,0011% |

Yorum:

- 526 coinlik tam koşuda toplam adayların %52,06'sı tek-açık-işlem kuralı nedeniyle
  bloke edildi.
- Toplam ortalama getiri singular uygulamada −0,0275%'ten −0,0343%'e geriledi;
  kural bütün evrende tek başına performans iyileştirmedi.
- 1d ortalaması −0,0050%'ten −0,0017%'e iyileşirken 1w ortalaması
  +0,0091%'den −0,0011%'e geriledi. Bunlar tarihsel sonuçlardır; bağımsız ileri
  dönem doğrulaması değildir.

## Doğrulama

`verify_singular.py` üç şeyi kontrol eder ve hepsi **0 ihlal** ile geçer:

1. Aynı `senaryo + coin` için çakışan singular işlem yok.
2. Normal motorda aynı `senaryo + coin + TF + yön` için çakışma yok (motor
   değişmezi).
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
$env:FILTER_STATES_ONLY='1'; python build_filters.py  # filtre durumları (ağ gerekir)
python Singular-Backtest/run_filters_singular.py
```

Çıktı anahtarı `scenario_id|timeframe|filter_id`; değerler `trades`, `wins`,
`losses`, `retAll`, `ret2026`, `winRatio`, `winHoldH`, `profitDays`, `lossDays`.
All-in dashboard, bu dosyayı senaryo adı + TF + filtre etiketiyle eşleştirip
Allinone tablosundaki `(S)` sütunlarını doldurur.

Teorik katalog kapsamı `220 strateji x 56 filtre x 4 TF = 49.280` ayrı
senaryodur. 526 coinle coin bazlı teorik kapsam 25.921.280 kombinasyondur;
normal ve singular sonuçları birlikte sayılırsa 51.842.560 metrik hücresi olur.
Mevcut veride işlem üreten kombinasyonlar 44.770 normal ve 44.767 singular
özet satırı oluşturdu. Baseline toplamları sırasıyla 121.037.497 ve 58.027.196
işlemdir ve ana koşuyla birebir eşleşir.

`filter_normal.json` aynı aday işlem ve filtre durumlarından **normal** (tekil
olmayan) metrikleri üretir; dashboard Codex normal sütunlarını bu dosyayla
hizalayıp kaynak tablodaki şişmiş işlem sayılarını düzeltir.
