# Binance Futures Backtest Dashboard

Teknik bilgisi az olan bir kullanıcının Binance USD-M Futures verisini indirip 220 metodu, 56 filtreyi ve dört zaman dilimini tekrar test edebilmesi için hazırlanmış uçtan uca proje.

## Neler var?

- **220 deterministik metot:** [Metot kataloğu](docs/METHODS.md)
- **56 filtre:** [Filtre kataloğu](docs/FILTERS.md)
- 1h, 4h, 1d ve 1w sinyalleri
- 5 dakikalık mumlarla kronolojik çıkış çözümlemesi
- Aynı 5m mumda belirsizlik varsa korumacı `stop-first` kuralı
- Azami 1x kaldıraç
- Komisyon ve slippage dahil net sonuçlar
- Tüm dönem ve 2026 karşılaştırmalı interaktif dashboard

Canlı örnek: https://binance-futures-backtest-dashboard.hikmet-onur21.chatgpt.site

## En kolay kurulum

Python 3.12 ve Node.js 20+ kurulu olmalıdır.

```bash
git clone <REPO_URL>
cd binance-futures-backtest-dashboard
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

Önce üç coin ve kısa tarih aralığıyla sistemi kontrol et:

```bash
./scripts/quick_test.sh
```

Tam çalıştırma büyük disk alanı ve uzun süre gerektirir:

```bash
./scripts/run_all.sh
```

İstersen kapsamı ortam değişkenleriyle değiştirebilirsin:

```bash
SIZE=100 START=2022-01-01 WORKERS=4 ./scripts/run_all.sh
```

Dashboard’u aç:

```bash
cd dashboard
npm start
```

Tarayıcıda `http://localhost:8080` adresine git.

## İşlem sırası

1. `download_data.py`: Binance 1h verisini indirir.
2. `backtest.py`: 220 metodun ilk sinyallerini ve işlemlerini üretir.
3. `refine_5m.py`: Çıkışları 5m mumlarla kronolojik çözer.
4. `aggregate_refined.py`: Genel ve yıllık sonuçları toplar.
5. `build_filters.py`: 56 piyasa filtresini uygular.
6. `build_dashboard_v2.py`: Dashboard veri dosyalarını üretir.
7. `dashboard/server.js`: Arayüzü yerel olarak sunar.

## Temel ayarlar

[config.json](config.json) içinde risk, komisyon, slippage ve kaldıraç sınırları bulunur. Varsayılan hesaplama 1x kaldıraç sınırıyla ve maliyetler dahil yapılır.

## Klasörler

```text
data/                         İndirilen piyasa verileri (Git'e eklenmez)
results/                      Backtest çıktıları (Git'e eklenmez)
dashboard/                    HTML/Node.js arayüzü
docs/METHODS.md               220 metodun ayrıntılı kuralları
docs/FILTERS.md               56 filtrenin açıklaması
scripts/run_all.sh            Tam otomatik çalışma
scripts/quick_test.sh          Küçük doğrulama çalışması
```

## Veri ve kaynak kod politikası

Ham Binance verileri ve üretilmiş sonuçlar boyutları nedeniyle repoya eklenmez. İndirme, hesaplama ve dashboard üretme kodlarının tamamı repodadır. Sonuçlar yatırım tavsiyesi değildir.
