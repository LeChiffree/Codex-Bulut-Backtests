# Strateji Taraması / Chosen Ones

Bu sayfa `dashboard/scan_pro.html` tarafından sunulur ve `tools/serve_dash.mjs`
üzerinden **`/tara`** rotasında açılır.

## Veri üretimi

Tarama verisi büyük olduğu için repoya commit edilmez (`dashboard/data/` gitignore).
Sonuç CSV'lerinden yeniden üretmek için:

```bash
python tools/build_scan_data.py
```

Bu komut şunları okur:

- `results/filter_overall_results.csv`
- `results/annual_results.csv`
- `results/filter_definitions.json`

ve `dashboard/data/scan.json` dosyasını yazar.

## Kapsam

- 800 metot × timeframe kombinasyonu (20 kombinasyon işlemsiz olduğu için yok).
- 56 filtre; filtre seçimi tüm satırlara uygulanır.
- Net % ve Ort. R, seçili filtrenin **sembol ortalamasıdır** (portföy toplamı değildir).
- 2026 ve pozitif yıl sütunları filtresiz baz yıllık veridir; 2026 kısmi yıldır.
- Puan 0–100: net %40, 2026 %25, kazanma %15, Ort. R %15, işlem %5
  (800 kombinasyon içinde yüzdelik dilim).

## Chosen Ones

Seçimler tarayıcıda `localStorage` anahtarı `codex_scan_chosen_v1` ile saklanır.
CSV dışa aktarımı `;` ayraçlı ve UTF-8 BOM'ludur; 2020–2026 yıllık getirileri içerir.
