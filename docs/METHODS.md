# 1H–4H–1D için 220 Kural Tabanlı Trading Metodu

> **Sürüm:** 1.0 — 7 Kasım 2026  
> **Kapsam:** Kripto spot/futures, likit hisse/endeks/FX; 1 saat, 4 saat ve günlük kapanmış mumlar  
> **Amaç:** Her fikri backtest edilebilir, deterministik giriş–çıkış kurallarına çevirmek  
> **Uyarı:** Bu dosya yatırım tavsiyesi değildir. Hiçbir yöntem kârlılık garantisi vermez. YouTube'daki başarı oranı/gelir iddiaları doğrulanmış kabul edilmemiştir.

## Nasıl kullanılmalı?

Bu katalogdaki 220 yöntem **220 ayrı hipotezdir**. Aynı backtestte hepsini üst üste yığmak doğru değildir. Önce yöntem bazında, sonra aile bazında eleme yapılmalıdır. Crypto, BIST ve NASDAQ parametreleri ayrı optimize edilmelidir; spot ve futures sonuçları da aynı havuzda birleştirilmemelidir.

### Katalog haritası

| No | Yöntem ailesi | Ana kullanım |
|---:|---|---|
| 001–020 | Trend pullback | Trend yönünde geri çekilme |
| 021–040 | Volatilite kırılımı | Donchian, BB/KC squeeze, range breakout |
| 041–060 | Momentum devamı | RSI/MACD/Stoch/MFI ile yeniden hızlanma |
| 061–080 | Mean reversion | Yatay piyasada banda/ortalamaya dönüş |
| 081–100 | Divergence | Yapı teyitli uyumsuzluk dönüşleri |
| 101–120 | Mum ve mikro-yapı | Engulfing, pin, inside, star ve retest |
| 121–140 | Hacim ve değer alanı | OBV, CMF, MFI, AVWAP, Volume Profile |
| 141–160 | Trend sistemleri | Ichimoku, Supertrend, DMI/ADX |
| 161–180 | 1D→4H→1H | Top-down, kapanmış üst-TF verisi |
| 181–200 | Volatilite rejimi | Sıkışma, NR7, inside serisi, şok |
| 201–220 | Dörtlü hibrit | Trend + momentum + hacim + tetik |

### Zorunlu ortak motor kuralları

1. **Sadece kapanmış mum:** `signal[t]` yalnızca `t` mumu kapandığında hesaplanır. Varsayılan dolum `open[t+1]` ve buna komisyon+slippage eklenir.
2. **Cross tanımı:** `crossUp(x,y) = x[t] > y[t] and x[t-1] <= y[t-1]`; `crossDown` bunun tersidir.
3. **ATR:** `TR=max(H-L, abs(H-C[-1]), abs(L-C[-1]))`; ATR Wilder/RMA ile hesaplanır.
4. **Hacim z-skoru:** `z=(volume-SMA(volume,20))/stdev(volume,20)`. Hacim olmayan/yanlış enstrümanda volume tabanlı metot kapatılır.
5. **EMA eğimi:** `(EMA[t]-EMA[t-5]) / (5*ATR[t])`. Pozitif eşik varsayılan `>0.02`, negatif `<-0.02`.
6. **Pivot:** `pivotLow(L,R)` ancak sağdaki `R` mum kapandıktan sonra onaylanır. Geriye dönük işaretlenen pivot, onay tarihinden önce kullanılamaz.
7. **Divergence:** İki onaylı pivot arası 5–60 bar. Regular bullish: `priceLow2 < priceLow1` ve `indicatorLow2 > indicatorLow1`; bearish tersi. Hidden bullish: `priceLow2 > priceLow1` ve `indicatorLow2 < indicatorLow1`.
8. **Mumlar:** Engulfing gövde bazlıdır; pin bar fitili en az gövdenin 2 katıdır; inside barın high/low'u mother bar içinde kalır.
9. **Risk birimi (R):** `R = abs(entry-stop)`. Pozisyon miktarı `equity*risk_pct/R`; taker ücret, spread ve tahmini slippage ayrıca düşülür.
10. **Aynı mum belirsizliği:** Aynı OHLC mumunda hem stop hem hedef görülürse düşük zaman verisi yokken muhafazakâr olarak stop önce gerçekleşmiş sayılır.
11. **MTF veri:** 1H stratejisinde 4H/1D değerleri yalnızca son tamamlanan üst zaman mumundan alınır; future leak/lookahead yasaktır.
12. **Korelasyon riski:** Aynı yönde güçlü korelasyonlu varlıklarda toplam açık risk varsayılan `%1.5`; tek işlem `%0.35–0.50`.

### Rejim sınıflandırması

| Rejim | Deterministik başlangıç tanımı | Öncelikli aile |
|---|---|---|
| Trend | ADX14 ≥ 23 ve EMA50 eğim mutlak değeri ≥ 0.02 ATR/bar | Pullback, momentum, trend sistemi |
| Range | ADX14 < 20 ve EMA50 eğim mutlak değeri < 0.05 ATR/bar | Mean reversion |
| Sıkışma | BB width son 120 barın %20 persentili altında | Breakout/volatilite |
| Şok | TR > 2.5×ATR14 veya hacim z > 2.5 | İlk barı kovalamama; retest/normalleşme |
| Belirsiz | Yukarıdaki koşulların hiçbiri net değil | İşlem yok veya boyut yarım |

### Backtest kabul kriteri

- Her TF ve piyasa ayrı: en az 200 işlem veya en az 3 yıllık örnek; hangisi daha uzunsa.
- Walk-forward: örnek olarak 18 ay train + 6 ay test; kayan pencere.
- Rapor: CAGR, max drawdown, Calmar, profit factor, expectancy/R, win rate, turnover, ortalama tutma süresi, long/short ayrı.
- Maliyet: gerçek komisyon; 1H için daha yüksek, günlük için daha düşük slippage senaryosu; en az `base` ve `2×cost` stres testi.
- Overfit kontrolü: tek “en iyi” parametre yerine komşu parametrelerde de çalışan plato aranır.

---

# Trend devam / pullback

## 001 — Trend pullback — EMA20>EMA50 + RSI14 önce 45 altını görür, sonra 50 üstünde kapanır

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** EMA20>EMA50 ve EMA50 eğimi pozitif; RSI14 önce 45 altını görür, sonra 50 üstünde kapanır; ATR; ADX
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Onaylı mumda EMA20>EMA50 ve EMA50 eğimi pozitif; fiyat EMA20-EMA50 bölgesine geri çekilir; ardından RSI14 önce 45 altını görür, sonra 50 üstünde kapanır. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda EMA20<EMA50 ve EMA50 eğimi negatif; fiyat EMA20-EMA50 bölgesine geri çekilir; ardından RSI14 önce 55 üstünü görür, sonra 50 altında kapanır. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: RSI14 65'e veya fiyat önceki swing tepeye ulaşana kadar.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: RSI14 35'e veya fiyat önceki swing dibe ulaşana kadar.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 002 — Trend pullback — EMA50>EMA200 + RSI14 önce 45 altını görür, sonra 50 üstünde kapanır

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** EMA50>EMA200 ve kapanış EMA50 üstünde; RSI14 önce 45 altını görür, sonra 50 üstünde kapanır; ATR; ADX
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Onaylı mumda EMA50>EMA200 ve kapanış EMA50 üstünde; fiyat EMA50'ye ±0.25 ATR yaklaşır; ardından RSI14 önce 45 altını görür, sonra 50 üstünde kapanır. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda EMA50<EMA200 ve kapanış EMA50 altında; fiyat EMA50'ye ±0.25 ATR yaklaşır; ardından RSI14 önce 55 üstünü görür, sonra 50 altında kapanır. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: RSI14 65'e veya fiyat önceki swing tepeye ulaşana kadar.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: RSI14 35'e veya fiyat önceki swing dibe ulaşana kadar.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 003 — Trend pullback — SMA20>SMA50>SMA200 + RSI14 önce 45 altını görür, sonra 50 üstünde kapanır

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** SMA20>SMA50>SMA200; RSI14 önce 45 altını görür, sonra 50 üstünde kapanır; ATR; ADX
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Onaylı mumda SMA20>SMA50>SMA200; fiyat SMA20'yi aşağı test edip üstünde kapanır; ardından RSI14 önce 45 altını görür, sonra 50 üstünde kapanır. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda SMA20<SMA50<SMA200; fiyat SMA20'yi yukarı test edip altında kapanır; ardından RSI14 önce 55 üstünü görür, sonra 50 altında kapanır. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: RSI14 65'e veya fiyat önceki swing tepeye ulaşana kadar.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: RSI14 35'e veya fiyat önceki swing dibe ulaşana kadar.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 004 — Trend pullback — Supertrend(10,3) yukarı + RSI14 önce 45 altını görür, sonra 50 üstünde kapanır

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** Supertrend(10,3) yukarı ve EMA100 eğimi pozitif; RSI14 önce 45 altını görür, sonra 50 üstünde kapanır; ATR; ADX
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Onaylı mumda Supertrend(10,3) yukarı ve EMA100 eğimi pozitif; fiyat Supertrend çizgisine 0.3 ATR yaklaşır; ardından RSI14 önce 45 altını görür, sonra 50 üstünde kapanır. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda Supertrend(10,3) aşağı ve EMA100 eğimi negatif; fiyat Supertrend çizgisine 0.3 ATR yaklaşır; ardından RSI14 önce 55 üstünü görür, sonra 50 altında kapanır. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: RSI14 65'e veya fiyat önceki swing tepeye ulaşana kadar.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: RSI14 35'e veya fiyat önceki swing dibe ulaşana kadar.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 005 — Trend pullback — Ichimoku fiyat bulut üstünde, Senkou A>B + RSI14 önce 45 altını görür, sonra 50 üstünde kapanır

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** Ichimoku fiyat bulut üstünde, Senkou A>B; RSI14 önce 45 altını görür, sonra 50 üstünde kapanır; ATR; ADX
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Onaylı mumda Ichimoku fiyat bulut üstünde, Senkou A>B; Tenkan/Kijun bölgesine düzeltme gelir; ardından RSI14 önce 45 altını görür, sonra 50 üstünde kapanır. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda Ichimoku fiyat bulut altında, Senkou A<B; Tenkan/Kijun bölgesine düzeltme gelir; ardından RSI14 önce 55 üstünü görür, sonra 50 altında kapanır. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: RSI14 65'e veya fiyat önceki swing tepeye ulaşana kadar.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: RSI14 35'e veya fiyat önceki swing dibe ulaşana kadar.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 006 — Trend pullback — EMA20>EMA50 + MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** EMA20>EMA50 ve EMA50 eğimi pozitif; MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser; ATR; ADX
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Onaylı mumda EMA20>EMA50 ve EMA50 eğimi pozitif; fiyat EMA20-EMA50 bölgesine geri çekilir; ardından MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda EMA20<EMA50 ve EMA50 eğimi negatif; fiyat EMA20-EMA50 bölgesine geri çekilir; ardından MACD(12,26,9) histogramı azalırken MACD sinyali aşağı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: MACD histogramı iki ardışık bar küçülürse yarı çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: MACD histogramı iki ardışık bar küçülürse yarı çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 007 — Trend pullback — EMA50>EMA200 + MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** EMA50>EMA200 ve kapanış EMA50 üstünde; MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser; ATR; ADX
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Onaylı mumda EMA50>EMA200 ve kapanış EMA50 üstünde; fiyat EMA50'ye ±0.25 ATR yaklaşır; ardından MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda EMA50<EMA200 ve kapanış EMA50 altında; fiyat EMA50'ye ±0.25 ATR yaklaşır; ardından MACD(12,26,9) histogramı azalırken MACD sinyali aşağı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: MACD histogramı iki ardışık bar küçülürse yarı çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: MACD histogramı iki ardışık bar küçülürse yarı çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 008 — Trend pullback — SMA20>SMA50>SMA200 + MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** SMA20>SMA50>SMA200; MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser; ATR; ADX
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Onaylı mumda SMA20>SMA50>SMA200; fiyat SMA20'yi aşağı test edip üstünde kapanır; ardından MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda SMA20<SMA50<SMA200; fiyat SMA20'yi yukarı test edip altında kapanır; ardından MACD(12,26,9) histogramı azalırken MACD sinyali aşağı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: MACD histogramı iki ardışık bar küçülürse yarı çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: MACD histogramı iki ardışık bar küçülürse yarı çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 009 — Trend pullback — Supertrend(10,3) yukarı + MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** Supertrend(10,3) yukarı ve EMA100 eğimi pozitif; MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser; ATR; ADX
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Onaylı mumda Supertrend(10,3) yukarı ve EMA100 eğimi pozitif; fiyat Supertrend çizgisine 0.3 ATR yaklaşır; ardından MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda Supertrend(10,3) aşağı ve EMA100 eğimi negatif; fiyat Supertrend çizgisine 0.3 ATR yaklaşır; ardından MACD(12,26,9) histogramı azalırken MACD sinyali aşağı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: MACD histogramı iki ardışık bar küçülürse yarı çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: MACD histogramı iki ardışık bar küçülürse yarı çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 010 — Trend pullback — Ichimoku fiyat bulut üstünde, Senkou A>B + MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** Ichimoku fiyat bulut üstünde, Senkou A>B; MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser; ATR; ADX
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Onaylı mumda Ichimoku fiyat bulut üstünde, Senkou A>B; Tenkan/Kijun bölgesine düzeltme gelir; ardından MACD(12,26,9) histogramı artarken MACD sinyali yukarı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda Ichimoku fiyat bulut altında, Senkou A<B; Tenkan/Kijun bölgesine düzeltme gelir; ardından MACD(12,26,9) histogramı azalırken MACD sinyali aşağı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: MACD histogramı iki ardışık bar küçülürse yarı çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: MACD histogramı iki ardışık bar küçülürse yarı çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 011 — Trend pullback — EMA20>EMA50 + Stoch(14,3,3) %K 30 altından %D'yi yukarı keser

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** EMA20>EMA50 ve EMA50 eğimi pozitif; Stoch(14,3,3) %K 30 altından %D'yi yukarı keser; ATR; ADX
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Onaylı mumda EMA20>EMA50 ve EMA50 eğimi pozitif; fiyat EMA20-EMA50 bölgesine geri çekilir; ardından Stoch(14,3,3) %K 30 altından %D'yi yukarı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda EMA20<EMA50 ve EMA50 eğimi negatif; fiyat EMA20-EMA50 bölgesine geri çekilir; ardından Stoch(14,3,3) %K 70 üstünden %D'yi aşağı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: Stoch 80 üstünde aşağı keserse çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: Stoch 80 altında yukarı keserse çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 012 — Trend pullback — EMA50>EMA200 + Stoch(14,3,3) %K 30 altından %D'yi yukarı keser

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** EMA50>EMA200 ve kapanış EMA50 üstünde; Stoch(14,3,3) %K 30 altından %D'yi yukarı keser; ATR; ADX
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Onaylı mumda EMA50>EMA200 ve kapanış EMA50 üstünde; fiyat EMA50'ye ±0.25 ATR yaklaşır; ardından Stoch(14,3,3) %K 30 altından %D'yi yukarı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda EMA50<EMA200 ve kapanış EMA50 altında; fiyat EMA50'ye ±0.25 ATR yaklaşır; ardından Stoch(14,3,3) %K 70 üstünden %D'yi aşağı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: Stoch 80 üstünde aşağı keserse çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: Stoch 80 altında yukarı keserse çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 013 — Trend pullback — SMA20>SMA50>SMA200 + Stoch(14,3,3) %K 30 altından %D'yi yukarı keser

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** SMA20>SMA50>SMA200; Stoch(14,3,3) %K 30 altından %D'yi yukarı keser; ATR; ADX
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Onaylı mumda SMA20>SMA50>SMA200; fiyat SMA20'yi aşağı test edip üstünde kapanır; ardından Stoch(14,3,3) %K 30 altından %D'yi yukarı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda SMA20<SMA50<SMA200; fiyat SMA20'yi yukarı test edip altında kapanır; ardından Stoch(14,3,3) %K 70 üstünden %D'yi aşağı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: Stoch 80 üstünde aşağı keserse çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: Stoch 80 altında yukarı keserse çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 014 — Trend pullback — Supertrend(10,3) yukarı + Stoch(14,3,3) %K 30 altından %D'yi yukarı keser

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** Supertrend(10,3) yukarı ve EMA100 eğimi pozitif; Stoch(14,3,3) %K 30 altından %D'yi yukarı keser; ATR; ADX
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Onaylı mumda Supertrend(10,3) yukarı ve EMA100 eğimi pozitif; fiyat Supertrend çizgisine 0.3 ATR yaklaşır; ardından Stoch(14,3,3) %K 30 altından %D'yi yukarı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda Supertrend(10,3) aşağı ve EMA100 eğimi negatif; fiyat Supertrend çizgisine 0.3 ATR yaklaşır; ardından Stoch(14,3,3) %K 70 üstünden %D'yi aşağı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: Stoch 80 üstünde aşağı keserse çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: Stoch 80 altında yukarı keserse çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 015 — Trend pullback — Ichimoku fiyat bulut üstünde, Senkou A>B + Stoch(14,3,3) %K 30 altından %D'yi yukarı keser

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** Ichimoku fiyat bulut üstünde, Senkou A>B; Stoch(14,3,3) %K 30 altından %D'yi yukarı keser; ATR; ADX
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Onaylı mumda Ichimoku fiyat bulut üstünde, Senkou A>B; Tenkan/Kijun bölgesine düzeltme gelir; ardından Stoch(14,3,3) %K 30 altından %D'yi yukarı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda Ichimoku fiyat bulut altında, Senkou A<B; Tenkan/Kijun bölgesine düzeltme gelir; ardından Stoch(14,3,3) %K 70 üstünden %D'yi aşağı keser. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: Stoch 80 üstünde aşağı keserse çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: Stoch 80 altında yukarı keserse çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 016 — Trend pullback — EMA20>EMA50 + bullish engulfing oluşur ve hacim z-skoru ≥0.7

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** EMA20>EMA50 ve EMA50 eğimi pozitif; bullish engulfing oluşur ve hacim z-skoru ≥0.7; ATR; ADX
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Onaylı mumda EMA20>EMA50 ve EMA50 eğimi pozitif; fiyat EMA20-EMA50 bölgesine geri çekilir; ardından bullish engulfing oluşur ve hacim z-skoru ≥0.7. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda EMA20<EMA50 ve EMA50 eğimi negatif; fiyat EMA20-EMA50 bölgesine geri çekilir; ardından bearish engulfing oluşur ve hacim z-skoru ≥0.7. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: karşıt engulfing veya EMA20 altı kapanışta çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: karşıt engulfing veya EMA20 altı kapanışta çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 017 — Trend pullback — EMA50>EMA200 + bullish engulfing oluşur ve hacim z-skoru ≥0.7

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** EMA50>EMA200 ve kapanış EMA50 üstünde; bullish engulfing oluşur ve hacim z-skoru ≥0.7; ATR; ADX
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Onaylı mumda EMA50>EMA200 ve kapanış EMA50 üstünde; fiyat EMA50'ye ±0.25 ATR yaklaşır; ardından bullish engulfing oluşur ve hacim z-skoru ≥0.7. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda EMA50<EMA200 ve kapanış EMA50 altında; fiyat EMA50'ye ±0.25 ATR yaklaşır; ardından bearish engulfing oluşur ve hacim z-skoru ≥0.7. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: karşıt engulfing veya EMA20 altı kapanışta çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: karşıt engulfing veya EMA20 altı kapanışta çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 018 — Trend pullback — SMA20>SMA50>SMA200 + bullish engulfing oluşur ve hacim z-skoru ≥0.7

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** SMA20>SMA50>SMA200; bullish engulfing oluşur ve hacim z-skoru ≥0.7; ATR; ADX
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Onaylı mumda SMA20>SMA50>SMA200; fiyat SMA20'yi aşağı test edip üstünde kapanır; ardından bullish engulfing oluşur ve hacim z-skoru ≥0.7. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda SMA20<SMA50<SMA200; fiyat SMA20'yi yukarı test edip altında kapanır; ardından bearish engulfing oluşur ve hacim z-skoru ≥0.7. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: karşıt engulfing veya EMA20 altı kapanışta çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: karşıt engulfing veya EMA20 altı kapanışta çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 019 — Trend pullback — Supertrend(10,3) yukarı + bullish engulfing oluşur ve hacim z-skoru ≥0.7

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** Supertrend(10,3) yukarı ve EMA100 eğimi pozitif; bullish engulfing oluşur ve hacim z-skoru ≥0.7; ATR; ADX
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Onaylı mumda Supertrend(10,3) yukarı ve EMA100 eğimi pozitif; fiyat Supertrend çizgisine 0.3 ATR yaklaşır; ardından bullish engulfing oluşur ve hacim z-skoru ≥0.7. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda Supertrend(10,3) aşağı ve EMA100 eğimi negatif; fiyat Supertrend çizgisine 0.3 ATR yaklaşır; ardından bearish engulfing oluşur ve hacim z-skoru ≥0.7. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: karşıt engulfing veya EMA20 altı kapanışta çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: karşıt engulfing veya EMA20 altı kapanışta çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)

## 020 — Trend pullback — Ichimoku fiyat bulut üstünde, Senkou A>B + bullish engulfing oluşur ve hacim z-skoru ≥0.7

- **Aile / rejim:** Trend devam / pullback — Yönlü piyasa; ADX yükselen veya EMA eğimi belirgin.
- **Bileşenler:** Ichimoku fiyat bulut üstünde, Senkou A>B; bullish engulfing oluşur ve hacim z-skoru ≥0.7; ATR; ADX
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Onaylı mumda Ichimoku fiyat bulut üstünde, Senkou A>B; Tenkan/Kijun bölgesine düzeltme gelir; ardından bullish engulfing oluşur ve hacim z-skoru ≥0.7. ADX14≥18 ve son 5 barda düşmüyor.
- **SHORT kurulumu:** Onaylı mumda Ichimoku fiyat bulut altında, Senkou A<B; Tenkan/Kijun bölgesine düzeltme gelir; ardından bearish engulfing oluşur ve hacim z-skoru ≥0.7. ADX14≥18 ve son 5 barda düşmüyor.
- **Emir/giriş (LONG):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun tepesine 0.05 ATR buy-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Emir/giriş (SHORT):** Sinyal mumunun kapanışından sonra bir sonraki mum açılışında; alternatif: sinyal mumunun dibine 0.05 ATR sell-stop. Emir 2 mum içinde tetiklenmezse iptal.
- **Stop ve boyut (LONG):** Son onaylı swing dibinin 0.15 ATR altı ile giriş−1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Stop ve boyut (SHORT):** Son onaylı swing tepesinin 0.15 ATR üstü ile giriş+1.5 ATR arasından daha uzak olanı. Pozisyon riski özsermayenin %0.50'si.
- **Çıkış (LONG):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: karşıt engulfing veya EMA20 altı kapanışta çık.
- **Çıkış (SHORT):** 1R'de %40 kapat ve stopu maliyete çek; 2R'de %30 kapat; kalanını EMA20 kapanış iziyle yönet. Ek kural: karşıt engulfing veya EMA20 altı kapanışta çık.
- **İşlem yok / geçersiz:** EMA20 ve EMA50 arası <0.15 ATR ise, ADX<18 ise veya sinyal mumu >2.2 ATR ise işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V02](#v02) [V24](#v24) [V35](#v35) [D01](#d01) [D03](#d03) [D04](#d04)


# Volatilite kırılımı

## 021 — Kırılım — Donchian20 üst bandı + kapanış seviye üstünde ≥0.10 ATR

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** Donchian20 üst bandı; kapanış seviye üstünde ≥0.10 ATR ve hacim z≥1.0; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian20 üst bandı üstünde. Kırılım teyidi: kapanış seviye üstünde ≥0.10 ATR ve hacim z≥1.0. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian20 alt bandı altında. Kırılım teyidi: kapanış seviye altında ≥0.10 ATR ve hacim z≥1.0. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian10 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian10 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 022 — Kırılım — Donchian55 üst bandı + kapanış seviye üstünde ≥0.10 ATR

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** Donchian55 üst bandı; kapanış seviye üstünde ≥0.10 ATR ve hacim z≥1.0; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian55 üst bandı üstünde. Kırılım teyidi: kapanış seviye üstünde ≥0.10 ATR ve hacim z≥1.0. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian55 alt bandı altında. Kırılım teyidi: kapanış seviye altında ≥0.10 ATR ve hacim z≥1.0. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian20 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian20 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 023 — Kırılım — son 20 mumun en yükseği + kapanış seviye üstünde ≥0.10 ATR

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** son 20 mumun en yükseği; kapanış seviye üstünde ≥0.10 ATR ve hacim z≥1.0; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış son 20 mumun en yükseği üstünde. Kırılım teyidi: kapanış seviye üstünde ≥0.10 ATR ve hacim z≥1.0. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış son 20 mumun en düşüğü altında. Kırılım teyidi: kapanış seviye altında ≥0.10 ATR ve hacim z≥1.0. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon son 10 mumun en düşüğü kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon son 10 mumun en düşüğü kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 024 — Kırılım — BB(20,2) üst bandı + kapanış seviye üstünde ≥0.10 ATR

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** BB(20,2) üst bandı; BB genişliği son 120 barın %20 persentilinden çıkıyor; kapanış seviye üstünde ≥0.10 ATR ve hacim z≥1.0; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış BB(20,2) üst bandı; BB genişliği son 120 barın %20 persentilinden çıkıyor üstünde. Kırılım teyidi: kapanış seviye üstünde ≥0.10 ATR ve hacim z≥1.0. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış BB(20,2) alt bandı; BB genişliği son 120 barın %20 persentilinden çıkıyor altında. Kırılım teyidi: kapanış seviye altında ≥0.10 ATR ve hacim z≥1.0. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon BB orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon BB orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 025 — Kırılım — KC(20,2ATR) üst bandı + kapanış seviye üstünde ≥0.10 ATR

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** KC(20,2ATR) üst bandı; önce BB KC içinde squeeze; kapanış seviye üstünde ≥0.10 ATR ve hacim z≥1.0; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış KC(20,2ATR) üst bandı; önce BB KC içinde squeeze üstünde. Kırılım teyidi: kapanış seviye üstünde ≥0.10 ATR ve hacim z≥1.0. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış KC(20,2ATR) alt bandı; önce BB KC içinde squeeze altında. Kırılım teyidi: kapanış seviye altında ≥0.10 ATR ve hacim z≥1.0. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon KC orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon KC orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 026 — Kırılım — Donchian20 üst bandı + ADX14≥22, yükseliyor

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** Donchian20 üst bandı; ADX14≥22, yükseliyor ve +DI>-DI; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian20 üst bandı üstünde. Kırılım teyidi: ADX14≥22, yükseliyor ve +DI>-DI. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian20 alt bandı altında. Kırılım teyidi: ADX14≥22, düşüyor ve -DI>+DI. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian10 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian10 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 027 — Kırılım — Donchian55 üst bandı + ADX14≥22, yükseliyor

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** Donchian55 üst bandı; ADX14≥22, yükseliyor ve +DI>-DI; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian55 üst bandı üstünde. Kırılım teyidi: ADX14≥22, yükseliyor ve +DI>-DI. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian55 alt bandı altında. Kırılım teyidi: ADX14≥22, düşüyor ve -DI>+DI. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian20 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian20 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 028 — Kırılım — son 20 mumun en yükseği + ADX14≥22, yükseliyor

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** son 20 mumun en yükseği; ADX14≥22, yükseliyor ve +DI>-DI; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış son 20 mumun en yükseği üstünde. Kırılım teyidi: ADX14≥22, yükseliyor ve +DI>-DI. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış son 20 mumun en düşüğü altında. Kırılım teyidi: ADX14≥22, düşüyor ve -DI>+DI. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon son 10 mumun en düşüğü kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon son 10 mumun en düşüğü kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 029 — Kırılım — BB(20,2) üst bandı + ADX14≥22, yükseliyor

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** BB(20,2) üst bandı; BB genişliği son 120 barın %20 persentilinden çıkıyor; ADX14≥22, yükseliyor ve +DI>-DI; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış BB(20,2) üst bandı; BB genişliği son 120 barın %20 persentilinden çıkıyor üstünde. Kırılım teyidi: ADX14≥22, yükseliyor ve +DI>-DI. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış BB(20,2) alt bandı; BB genişliği son 120 barın %20 persentilinden çıkıyor altında. Kırılım teyidi: ADX14≥22, düşüyor ve -DI>+DI. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon BB orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon BB orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 030 — Kırılım — KC(20,2ATR) üst bandı + ADX14≥22, yükseliyor

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** KC(20,2ATR) üst bandı; önce BB KC içinde squeeze; ADX14≥22, yükseliyor ve +DI>-DI; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış KC(20,2ATR) üst bandı; önce BB KC içinde squeeze üstünde. Kırılım teyidi: ADX14≥22, yükseliyor ve +DI>-DI. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış KC(20,2ATR) alt bandı; önce BB KC içinde squeeze altında. Kırılım teyidi: ADX14≥22, düşüyor ve -DI>+DI. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon KC orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon KC orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 031 — Kırılım — Donchian20 üst bandı + CMF20>0.05

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** Donchian20 üst bandı; CMF20>0.05 ve OBV son 20 bar tepesini kırıyor; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian20 üst bandı üstünde. Kırılım teyidi: CMF20>0.05 ve OBV son 20 bar tepesini kırıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian20 alt bandı altında. Kırılım teyidi: CMF20<-0.05 ve OBV son 20 bar tepesini kırıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian10 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian10 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 032 — Kırılım — Donchian55 üst bandı + CMF20>0.05

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** Donchian55 üst bandı; CMF20>0.05 ve OBV son 20 bar tepesini kırıyor; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian55 üst bandı üstünde. Kırılım teyidi: CMF20>0.05 ve OBV son 20 bar tepesini kırıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian55 alt bandı altında. Kırılım teyidi: CMF20<-0.05 ve OBV son 20 bar tepesini kırıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian20 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian20 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 033 — Kırılım — son 20 mumun en yükseği + CMF20>0.05

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** son 20 mumun en yükseği; CMF20>0.05 ve OBV son 20 bar tepesini kırıyor; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış son 20 mumun en yükseği üstünde. Kırılım teyidi: CMF20>0.05 ve OBV son 20 bar tepesini kırıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış son 20 mumun en düşüğü altında. Kırılım teyidi: CMF20<-0.05 ve OBV son 20 bar tepesini kırıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon son 10 mumun en düşüğü kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon son 10 mumun en düşüğü kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 034 — Kırılım — BB(20,2) üst bandı + CMF20>0.05

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** BB(20,2) üst bandı; BB genişliği son 120 barın %20 persentilinden çıkıyor; CMF20>0.05 ve OBV son 20 bar tepesini kırıyor; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış BB(20,2) üst bandı; BB genişliği son 120 barın %20 persentilinden çıkıyor üstünde. Kırılım teyidi: CMF20>0.05 ve OBV son 20 bar tepesini kırıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış BB(20,2) alt bandı; BB genişliği son 120 barın %20 persentilinden çıkıyor altında. Kırılım teyidi: CMF20<-0.05 ve OBV son 20 bar tepesini kırıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon BB orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon BB orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 035 — Kırılım — KC(20,2ATR) üst bandı + CMF20>0.05

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** KC(20,2ATR) üst bandı; önce BB KC içinde squeeze; CMF20>0.05 ve OBV son 20 bar tepesini kırıyor; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış KC(20,2ATR) üst bandı; önce BB KC içinde squeeze üstünde. Kırılım teyidi: CMF20>0.05 ve OBV son 20 bar tepesini kırıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış KC(20,2ATR) alt bandı; önce BB KC içinde squeeze altında. Kırılım teyidi: CMF20<-0.05 ve OBV son 20 bar tepesini kırıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon KC orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon KC orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 036 — Kırılım — Donchian20 üst bandı + RSI14>55

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** Donchian20 üst bandı; RSI14>55 ve MACD histogramı pozitif/artıyor; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian20 üst bandı üstünde. Kırılım teyidi: RSI14>55 ve MACD histogramı pozitif/artıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian20 alt bandı altında. Kırılım teyidi: RSI14<45 ve MACD histogramı negatif/azalıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian10 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian10 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 037 — Kırılım — Donchian55 üst bandı + RSI14>55

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** Donchian55 üst bandı; RSI14>55 ve MACD histogramı pozitif/artıyor; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian55 üst bandı üstünde. Kırılım teyidi: RSI14>55 ve MACD histogramı pozitif/artıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış Donchian55 alt bandı altında. Kırılım teyidi: RSI14<45 ve MACD histogramı negatif/azalıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian20 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon Donchian20 karşı bandı kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 038 — Kırılım — son 20 mumun en yükseği + RSI14>55

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** son 20 mumun en yükseği; RSI14>55 ve MACD histogramı pozitif/artıyor; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış son 20 mumun en yükseği üstünde. Kırılım teyidi: RSI14>55 ve MACD histogramı pozitif/artıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış son 20 mumun en düşüğü altında. Kırılım teyidi: RSI14<45 ve MACD histogramı negatif/azalıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon son 10 mumun en düşüğü kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon son 10 mumun en düşüğü kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 039 — Kırılım — BB(20,2) üst bandı + RSI14>55

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** BB(20,2) üst bandı; BB genişliği son 120 barın %20 persentilinden çıkıyor; RSI14>55 ve MACD histogramı pozitif/artıyor; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış BB(20,2) üst bandı; BB genişliği son 120 barın %20 persentilinden çıkıyor üstünde. Kırılım teyidi: RSI14>55 ve MACD histogramı pozitif/artıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış BB(20,2) alt bandı; BB genişliği son 120 barın %20 persentilinden çıkıyor altında. Kırılım teyidi: RSI14<45 ve MACD histogramı negatif/azalıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon BB orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon BB orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)

## 040 — Kırılım — KC(20,2ATR) üst bandı + RSI14>55

- **Aile / rejim:** Volatilite kırılımı — Sıkışmadan genişlemeye geçiş veya güçlü trend devamı.
- **Bileşenler:** KC(20,2ATR) üst bandı; önce BB KC içinde squeeze; RSI14>55 ve MACD histogramı pozitif/artıyor; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış KC(20,2ATR) üst bandı; önce BB KC içinde squeeze üstünde. Kırılım teyidi: RSI14>55 ve MACD histogramı pozitif/artıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **SHORT kurulumu:** Önce en az 5 bar sıkışma; onaylı kapanış KC(20,2ATR) alt bandı; önce BB KC içinde squeeze altında. Kırılım teyidi: RSI14<45 ve MACD histogramı negatif/azalıyor. Kırılan seviye son 3 barda en az iki kez test edilmiş olmalı.
- **Emir/giriş (LONG):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Emir/giriş (SHORT):** Kapanış teyitli market-next-open veya kırılım seviyesine ilk retestte limit; ikisi aynı stratejide karıştırılmaz. Retest seçilirse 3 mum içinde seviye ±0.20 ATR test edilmeli ve yönlü kapanış gelmeli.
- **Stop ve boyut (LONG):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Stop ve boyut (SHORT):** Kırılan seviyenin 0.30 ATR ötesi veya sinyal mumunun karşı ucu; stop mesafesi 0.8–2.5 ATR dışında ise işlem yok.
- **Çıkış (LONG):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon KC orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2.5R ana hedef; kalan pozisyon KC orta bant kapanış ihlalinde çıkar. 10 bar sonra +0.5R oluşmadıysa zaman çıkışı.
- **İşlem yok / geçersiz:** Kırılım mumu >2.5 ATR, karşıda 1R'den yakın majör 4H/1D seviye veya hacim verisi eksikse işlem yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V05](#v05) [V06](#v06) [V08](#v08) [V39](#v39) [D05](#d05) [D06](#d06) [D07](#d07)


# Momentum devamı

## 041 — Momentum devamı — kapanış EMA50 üstünde + RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** kapanış EMA50 üstünde ve EMA50 eğimi pozitif; RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Yön filtresi: kapanış EMA50 üstünde ve EMA50 eğimi pozitif. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: kapanış EMA50 altında ve EMA50 eğimi negatif. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra RSI 50'yi aşağı keser ve RSI ivmesi RSI-RSI[3]<-5. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 042 — Momentum devamı — MACD çizgisi sıfır üstünde + RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** MACD çizgisi sıfır üstünde; RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Yön filtresi: MACD çizgisi sıfır üstünde. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: MACD çizgisi sıfır altında. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra RSI 50'yi aşağı keser ve RSI ivmesi RSI-RSI[3]<-5. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 043 — Momentum devamı — RSI14 son 20 barda 40 altına inmedi + RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** RSI14 son 20 barda 40 altına inmedi ve 70 üstünü gördü; RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Yön filtresi: RSI14 son 20 barda 40 altına inmedi ve 70 üstünü gördü. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: RSI14 son 20 barda 60 üstüne çıkmadı ve 30 altını gördü. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra RSI 50'yi aşağı keser ve RSI ivmesi RSI-RSI[3]<-5. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 044 — Momentum devamı — MFI14>50 + RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** MFI14>50 ve CMF20>0; RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Yön filtresi: MFI14>50 ve CMF20>0. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: MFI14<50 ve CMF20<0. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra RSI 50'yi aşağı keser ve RSI ivmesi RSI-RSI[3]<-5. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 045 — Momentum devamı — Supertrend(10,3) yukarı + RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** Supertrend(10,3) yukarı; RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Yön filtresi: Supertrend(10,3) yukarı. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra RSI 50'yi yukarı keser ve RSI ivmesi RSI-RSI[3]>5. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: Supertrend(10,3) aşağı. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra RSI 50'yi aşağı keser ve RSI ivmesi RSI-RSI[3]<-5. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 046 — Momentum devamı — kapanış EMA50 üstünde + MACD histogramı negatiften pozitife döner

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** kapanış EMA50 üstünde ve EMA50 eğimi pozitif; MACD histogramı negatiften pozitife döner; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Yön filtresi: kapanış EMA50 üstünde ve EMA50 eğimi pozitif. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MACD histogramı negatiften pozitife döner. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: kapanış EMA50 altında ve EMA50 eğimi negatif. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MACD histogramı pozitiften negatife döner. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 047 — Momentum devamı — MACD çizgisi sıfır üstünde + MACD histogramı negatiften pozitife döner

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** MACD çizgisi sıfır üstünde; MACD histogramı negatiften pozitife döner; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Yön filtresi: MACD çizgisi sıfır üstünde. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MACD histogramı negatiften pozitife döner. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: MACD çizgisi sıfır altında. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MACD histogramı pozitiften negatife döner. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 048 — Momentum devamı — RSI14 son 20 barda 40 altına inmedi + MACD histogramı negatiften pozitife döner

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** RSI14 son 20 barda 40 altına inmedi ve 70 üstünü gördü; MACD histogramı negatiften pozitife döner; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Yön filtresi: RSI14 son 20 barda 40 altına inmedi ve 70 üstünü gördü. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MACD histogramı negatiften pozitife döner. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: RSI14 son 20 barda 60 üstüne çıkmadı ve 30 altını gördü. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MACD histogramı pozitiften negatife döner. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 049 — Momentum devamı — MFI14>50 + MACD histogramı negatiften pozitife döner

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** MFI14>50 ve CMF20>0; MACD histogramı negatiften pozitife döner; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Yön filtresi: MFI14>50 ve CMF20>0. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MACD histogramı negatiften pozitife döner. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: MFI14<50 ve CMF20<0. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MACD histogramı pozitiften negatife döner. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 050 — Momentum devamı — Supertrend(10,3) yukarı + MACD histogramı negatiften pozitife döner

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** Supertrend(10,3) yukarı; MACD histogramı negatiften pozitife döner; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Yön filtresi: Supertrend(10,3) yukarı. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MACD histogramı negatiften pozitife döner. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: Supertrend(10,3) aşağı. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MACD histogramı pozitiften negatife döner. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 051 — Momentum devamı — kapanış EMA50 üstünde + Stoch %K 50'yi yukarı keser ve %K>%D

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** kapanış EMA50 üstünde ve EMA50 eğimi pozitif; Stoch %K 50'yi yukarı keser ve %K>%D; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Yön filtresi: kapanış EMA50 üstünde ve EMA50 eğimi pozitif. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra Stoch %K 50'yi yukarı keser ve %K>%D. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: kapanış EMA50 altında ve EMA50 eğimi negatif. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra Stoch %K 50'yi aşağı keser ve %K>%D. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 052 — Momentum devamı — MACD çizgisi sıfır üstünde + Stoch %K 50'yi yukarı keser ve %K>%D

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** MACD çizgisi sıfır üstünde; Stoch %K 50'yi yukarı keser ve %K>%D; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Yön filtresi: MACD çizgisi sıfır üstünde. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra Stoch %K 50'yi yukarı keser ve %K>%D. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: MACD çizgisi sıfır altında. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra Stoch %K 50'yi aşağı keser ve %K>%D. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 053 — Momentum devamı — RSI14 son 20 barda 40 altına inmedi + Stoch %K 50'yi yukarı keser ve %K>%D

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** RSI14 son 20 barda 40 altına inmedi ve 70 üstünü gördü; Stoch %K 50'yi yukarı keser ve %K>%D; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Yön filtresi: RSI14 son 20 barda 40 altına inmedi ve 70 üstünü gördü. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra Stoch %K 50'yi yukarı keser ve %K>%D. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: RSI14 son 20 barda 60 üstüne çıkmadı ve 30 altını gördü. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra Stoch %K 50'yi aşağı keser ve %K>%D. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 054 — Momentum devamı — MFI14>50 + Stoch %K 50'yi yukarı keser ve %K>%D

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** MFI14>50 ve CMF20>0; Stoch %K 50'yi yukarı keser ve %K>%D; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Yön filtresi: MFI14>50 ve CMF20>0. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra Stoch %K 50'yi yukarı keser ve %K>%D. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: MFI14<50 ve CMF20<0. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra Stoch %K 50'yi aşağı keser ve %K>%D. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 055 — Momentum devamı — Supertrend(10,3) yukarı + Stoch %K 50'yi yukarı keser ve %K>%D

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** Supertrend(10,3) yukarı; Stoch %K 50'yi yukarı keser ve %K>%D; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Yön filtresi: Supertrend(10,3) yukarı. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra Stoch %K 50'yi yukarı keser ve %K>%D. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: Supertrend(10,3) aşağı. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra Stoch %K 50'yi aşağı keser ve %K>%D. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 056 — Momentum devamı — kapanış EMA50 üstünde + MFI 50'yi yukarı keser

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** kapanış EMA50 üstünde ve EMA50 eğimi pozitif; MFI 50'yi yukarı keser; hacim z≥0.5; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Yön filtresi: kapanış EMA50 üstünde ve EMA50 eğimi pozitif. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MFI 50'yi yukarı keser; hacim z≥0.5. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: kapanış EMA50 altında ve EMA50 eğimi negatif. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MFI 50'yi aşağı keser; hacim z≥0.5. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 057 — Momentum devamı — MACD çizgisi sıfır üstünde + MFI 50'yi yukarı keser

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** MACD çizgisi sıfır üstünde; MFI 50'yi yukarı keser; hacim z≥0.5; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Yön filtresi: MACD çizgisi sıfır üstünde. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MFI 50'yi yukarı keser; hacim z≥0.5. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: MACD çizgisi sıfır altında. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MFI 50'yi aşağı keser; hacim z≥0.5. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 058 — Momentum devamı — RSI14 son 20 barda 40 altına inmedi + MFI 50'yi yukarı keser

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** RSI14 son 20 barda 40 altına inmedi ve 70 üstünü gördü; MFI 50'yi yukarı keser; hacim z≥0.5; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Yön filtresi: RSI14 son 20 barda 40 altına inmedi ve 70 üstünü gördü. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MFI 50'yi yukarı keser; hacim z≥0.5. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: RSI14 son 20 barda 60 üstüne çıkmadı ve 30 altını gördü. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MFI 50'yi aşağı keser; hacim z≥0.5. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 059 — Momentum devamı — MFI14>50 + MFI 50'yi yukarı keser

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** MFI14>50 ve CMF20>0; MFI 50'yi yukarı keser; hacim z≥0.5; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Yön filtresi: MFI14>50 ve CMF20>0. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MFI 50'yi yukarı keser; hacim z≥0.5. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: MFI14<50 ve CMF20<0. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MFI 50'yi aşağı keser; hacim z≥0.5. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)

## 060 — Momentum devamı — Supertrend(10,3) yukarı + MFI 50'yi yukarı keser

- **Aile / rejim:** Momentum devamı — Trend var, kısa süreli momentum soğuması bitiyor.
- **Bileşenler:** Supertrend(10,3) yukarı; MFI 50'yi yukarı keser; hacim z≥0.5; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Yön filtresi: Supertrend(10,3) yukarı. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MFI 50'yi yukarı keser; hacim z≥0.5. Sinyal kapanışı düzeltme aralığının üst yarısında.
- **SHORT kurulumu:** Yön filtresi: Supertrend(10,3) aşağı. Son 3–8 barlık yatay/düşük eğimli düzeltmeden sonra MFI 50'yi aşağı keser; hacim z≥0.5. Sinyal kapanışı düzeltme aralığının alt yarısında.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme tepesi arası >0.35 ATR ise tepeden buy-stop kullan; 3 bar sonra iptal.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış. Giriş ile düzeltme dibi arası >0.35 ATR ise dipten sell-stop kullan; 3 bar sonra iptal.
- **Stop ve boyut (LONG):** Düzeltme dibinin 0.10 ATR altı; maksimum 2 ATR. %0.50 risk.
- **Stop ve boyut (SHORT):** Düzeltme tepesinin 0.10 ATR üstü; maksimum 2 ATR. %0.50 risk.
- **Çıkış (LONG):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **Çıkış (SHORT):** İlk hedef 1.5R (%50); ikinci hedef 3R. Momentum göstergesi iki bar ters ivme yaparsa veya EMA20 ters kapanırsa kalan çıkış.
- **İşlem yok / geçersiz:** ADX son 5 barda sert düşüyorsa, EMA50 yataysa veya sinyal karşıt 1D trende ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V03](#v03) [V37](#v37) [V38](#v38) [V47](#v47) [D01](#d01) [D02](#d02) [D11](#d11)


# Mean reversion

## 061 — Ortalamaya dönüş — BB(20,2) alt bandının altında kapanıp tekrar band içine dönme + RSI14<30 gördükten sonra 35 üstüne dönüş

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** BB(20,2) alt bandının altında kapanıp tekrar band içine dönme; RSI14<30 gördükten sonra 35 üstüne dönüş; ADX; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: BB(20,2) alt bandının altında kapanıp tekrar band içine dönme. Tetik: RSI14<30 gördükten sonra 35 üstüne dönüş.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: BB(20,2) üst bandının üstünde kapanıp tekrar band içine dönme. Tetik: RSI14>70 gördükten sonra 65 altına dönüş.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 062 — Ortalamaya dönüş — KC(20,2ATR) altına fitil atıp KC içinde kapanma + RSI14<30 gördükten sonra 35 üstüne dönüş

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** KC(20,2ATR) altına fitil atıp KC içinde kapanma; RSI14<30 gördükten sonra 35 üstüne dönüş; ADX; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: KC(20,2ATR) altına fitil atıp KC içinde kapanma. Tetik: RSI14<30 gördükten sonra 35 üstüne dönüş.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: KC(20,2ATR) üstüne fitil atıp KC içinde kapanma. Tetik: RSI14>70 gördükten sonra 65 altına dönüş.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 063 — Ortalamaya dönüş — aylık AVWAP−2 standart sapma bandına temas + RSI14<30 gördükten sonra 35 üstüne dönüş

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** aylık AVWAP−2 standart sapma bandına temas; RSI14<30 gördükten sonra 35 üstüne dönüş; ADX; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: aylık AVWAP−2 standart sapma bandına temas. Tetik: RSI14<30 gördükten sonra 35 üstüne dönüş.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: aylık AVWAP+2 standart sapma bandına temas. Tetik: RSI14>70 gördükten sonra 65 altına dönüş.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 064 — Ortalamaya dönüş — önceki haftanın düşüğü altında sweep + RSI14<30 gördükten sonra 35 üstüne dönüş

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** önceki haftanın düşüğü altında sweep ve tekrar üstünde kapanış; RSI14<30 gördükten sonra 35 üstüne dönüş; ADX; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: önceki haftanın düşüğü altında sweep ve tekrar üstünde kapanış. Tetik: RSI14<30 gördükten sonra 35 üstüne dönüş.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: önceki haftanın yükseği üstünde sweep ve tekrar altında kapanış. Tetik: RSI14>70 gördükten sonra 65 altına dönüş.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 065 — Ortalamaya dönüş — Fibonacci pivot S2 altında reddedilip S2 üstünde kapanış + RSI14<30 gördükten sonra 35 üstüne dönüş

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** Fibonacci pivot S2 altında reddedilip S2 üstünde kapanış; RSI14<30 gördükten sonra 35 üstüne dönüş; ADX; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: Fibonacci pivot S2 altında reddedilip S2 üstünde kapanış. Tetik: RSI14<30 gördükten sonra 35 üstüne dönüş.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: Fibonacci pivot R2 üstünde reddedilip R2 altında kapanış. Tetik: RSI14>70 gördükten sonra 65 altına dönüş.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 066 — Ortalamaya dönüş — BB(20,2) alt bandının altında kapanıp tekrar band içine dönme + MFI14<20 gördükten sonra 25 üstüne dönüş

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** BB(20,2) alt bandının altında kapanıp tekrar band içine dönme; MFI14<20 gördükten sonra 25 üstüne dönüş; ADX; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: BB(20,2) alt bandının altında kapanıp tekrar band içine dönme. Tetik: MFI14<20 gördükten sonra 25 üstüne dönüş.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: BB(20,2) üst bandının üstünde kapanıp tekrar band içine dönme. Tetik: MFI14>80 gördükten sonra 75 altına dönüş.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 067 — Ortalamaya dönüş — KC(20,2ATR) altına fitil atıp KC içinde kapanma + MFI14<20 gördükten sonra 25 üstüne dönüş

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** KC(20,2ATR) altına fitil atıp KC içinde kapanma; MFI14<20 gördükten sonra 25 üstüne dönüş; ADX; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: KC(20,2ATR) altına fitil atıp KC içinde kapanma. Tetik: MFI14<20 gördükten sonra 25 üstüne dönüş.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: KC(20,2ATR) üstüne fitil atıp KC içinde kapanma. Tetik: MFI14>80 gördükten sonra 75 altına dönüş.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 068 — Ortalamaya dönüş — aylık AVWAP−2 standart sapma bandına temas + MFI14<20 gördükten sonra 25 üstüne dönüş

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** aylık AVWAP−2 standart sapma bandına temas; MFI14<20 gördükten sonra 25 üstüne dönüş; ADX; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: aylık AVWAP−2 standart sapma bandına temas. Tetik: MFI14<20 gördükten sonra 25 üstüne dönüş.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: aylık AVWAP+2 standart sapma bandına temas. Tetik: MFI14>80 gördükten sonra 75 altına dönüş.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 069 — Ortalamaya dönüş — önceki haftanın düşüğü altında sweep + MFI14<20 gördükten sonra 25 üstüne dönüş

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** önceki haftanın düşüğü altında sweep ve tekrar üstünde kapanış; MFI14<20 gördükten sonra 25 üstüne dönüş; ADX; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: önceki haftanın düşüğü altında sweep ve tekrar üstünde kapanış. Tetik: MFI14<20 gördükten sonra 25 üstüne dönüş.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: önceki haftanın yükseği üstünde sweep ve tekrar altında kapanış. Tetik: MFI14>80 gördükten sonra 75 altına dönüş.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 070 — Ortalamaya dönüş — Fibonacci pivot S2 altında reddedilip S2 üstünde kapanış + MFI14<20 gördükten sonra 25 üstüne dönüş

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** Fibonacci pivot S2 altında reddedilip S2 üstünde kapanış; MFI14<20 gördükten sonra 25 üstüne dönüş; ADX; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: Fibonacci pivot S2 altında reddedilip S2 üstünde kapanış. Tetik: MFI14<20 gördükten sonra 25 üstüne dönüş.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: Fibonacci pivot R2 üstünde reddedilip R2 altında kapanış. Tetik: MFI14>80 gördükten sonra 75 altına dönüş.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 071 — Ortalamaya dönüş — BB(20,2) alt bandının altında kapanıp tekrar band içine dönme + Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** BB(20,2) alt bandının altında kapanıp tekrar band içine dönme; Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi; ADX; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: BB(20,2) alt bandının altında kapanıp tekrar band içine dönme. Tetik: Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: BB(20,2) üst bandının üstünde kapanıp tekrar band içine dönme. Tetik: Stoch %K>85 iken %K'nın %D'yi aşağı kesmesi.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 072 — Ortalamaya dönüş — KC(20,2ATR) altına fitil atıp KC içinde kapanma + Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** KC(20,2ATR) altına fitil atıp KC içinde kapanma; Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi; ADX; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: KC(20,2ATR) altına fitil atıp KC içinde kapanma. Tetik: Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: KC(20,2ATR) üstüne fitil atıp KC içinde kapanma. Tetik: Stoch %K>85 iken %K'nın %D'yi aşağı kesmesi.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 073 — Ortalamaya dönüş — aylık AVWAP−2 standart sapma bandına temas + Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** aylık AVWAP−2 standart sapma bandına temas; Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi; ADX; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: aylık AVWAP−2 standart sapma bandına temas. Tetik: Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: aylık AVWAP+2 standart sapma bandına temas. Tetik: Stoch %K>85 iken %K'nın %D'yi aşağı kesmesi.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 074 — Ortalamaya dönüş — önceki haftanın düşüğü altında sweep + Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** önceki haftanın düşüğü altında sweep ve tekrar üstünde kapanış; Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi; ADX; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: önceki haftanın düşüğü altında sweep ve tekrar üstünde kapanış. Tetik: Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: önceki haftanın yükseği üstünde sweep ve tekrar altında kapanış. Tetik: Stoch %K>85 iken %K'nın %D'yi aşağı kesmesi.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 075 — Ortalamaya dönüş — Fibonacci pivot S2 altında reddedilip S2 üstünde kapanış + Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** Fibonacci pivot S2 altında reddedilip S2 üstünde kapanış; Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi; ADX; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: Fibonacci pivot S2 altında reddedilip S2 üstünde kapanış. Tetik: Stoch %K<15 iken %K'nın %D'yi yukarı kesmesi.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: Fibonacci pivot R2 üstünde reddedilip R2 altında kapanış. Tetik: Stoch %K>85 iken %K'nın %D'yi aşağı kesmesi.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 076 — Ortalamaya dönüş — BB(20,2) alt bandının altında kapanıp tekrar band içine dönme + RSI bullish divergence

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** BB(20,2) alt bandının altında kapanıp tekrar band içine dönme; RSI bullish divergence ve MACD histogramının yükselmesi; ADX; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: BB(20,2) alt bandının altında kapanıp tekrar band içine dönme. Tetik: RSI bullish divergence ve MACD histogramının yükselmesi.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: BB(20,2) üst bandının üstünde kapanıp tekrar band içine dönme. Tetik: RSI bearish divergence ve MACD histogramının düşmesi.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 077 — Ortalamaya dönüş — KC(20,2ATR) altına fitil atıp KC içinde kapanma + RSI bullish divergence

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** KC(20,2ATR) altına fitil atıp KC içinde kapanma; RSI bullish divergence ve MACD histogramının yükselmesi; ADX; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: KC(20,2ATR) altına fitil atıp KC içinde kapanma. Tetik: RSI bullish divergence ve MACD histogramının yükselmesi.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: KC(20,2ATR) üstüne fitil atıp KC içinde kapanma. Tetik: RSI bearish divergence ve MACD histogramının düşmesi.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 078 — Ortalamaya dönüş — aylık AVWAP−2 standart sapma bandına temas + RSI bullish divergence

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** aylık AVWAP−2 standart sapma bandına temas; RSI bullish divergence ve MACD histogramının yükselmesi; ADX; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: aylık AVWAP−2 standart sapma bandına temas. Tetik: RSI bullish divergence ve MACD histogramının yükselmesi.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: aylık AVWAP+2 standart sapma bandına temas. Tetik: RSI bearish divergence ve MACD histogramının düşmesi.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 079 — Ortalamaya dönüş — önceki haftanın düşüğü altında sweep + RSI bullish divergence

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** önceki haftanın düşüğü altında sweep ve tekrar üstünde kapanış; RSI bullish divergence ve MACD histogramının yükselmesi; ADX; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: önceki haftanın düşüğü altında sweep ve tekrar üstünde kapanış. Tetik: RSI bullish divergence ve MACD histogramının yükselmesi.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: önceki haftanın yükseği üstünde sweep ve tekrar altında kapanış. Tetik: RSI bearish divergence ve MACD histogramının düşmesi.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)

## 080 — Ortalamaya dönüş — Fibonacci pivot S2 altında reddedilip S2 üstünde kapanış + RSI bullish divergence

- **Aile / rejim:** Mean reversion — Yatay piyasa; trend filtresi özellikle düşük.
- **Bileşenler:** Fibonacci pivot S2 altında reddedilip S2 üstünde kapanış; RSI bullish divergence ve MACD histogramının yükselmesi; ADX; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: Fibonacci pivot S2 altında reddedilip S2 üstünde kapanış. Tetik: RSI bullish divergence ve MACD histogramının yükselmesi.
- **SHORT kurulumu:** Range filtresi: ADX14<20 ve EMA50 mutlak eğimi/ATR<0.05. Lokasyon: Fibonacci pivot R2 üstünde reddedilip R2 altında kapanış. Tetik: RSI bearish divergence ve MACD histogramının düşmesi.
- **Emir/giriş (LONG):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye üzerinde değil, teyit kapanışından sonra geri çekilmede.
- **Emir/giriş (SHORT):** Dönüş mumunun kapanışından sonraki açılış; limit emir kullanılacaksa band/seviye altında değil, teyit kapanışından sonra geri çekilmede.
- **Stop ve boyut (LONG):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Stop ve boyut (SHORT):** Sweep/ekstrem noktanın 0.20 ATR ötesi; stop >1.8 ATR ise yok.
- **Çıkış (LONG):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **Çıkış (SHORT):** %50 BB/KC/AVWAP orta çizgide; kalan karşı banda veya 2R'ye. 6 bar içinde orta çizgiye ulaşmazsa zaman çıkışı.
- **İşlem yok / geçersiz:** ADX≥23, BB genişliği artışı son bara göre >%20 veya kırılım yönünde hacim z≥1.5 ise fade edilmez.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V12](#v12) [V29](#v29) [V41](#v41) [D05](#d05) [D06](#d06) [D13](#d13)


# Divergence dönüş/erken trend değişimi

## 081 — Uyumsuzluk — RSI14 regular bullish divergence + son düşen trend çizgisi üstünde kapanış

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** RSI14 regular bullish divergence; son düşen trend çizgisi üstünde kapanış; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: RSI14 regular bullish divergence. Giriş teyidi: son düşen trend çizgisi üstünde kapanış.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: RSI14 regular bearish divergence. Giriş teyidi: son yükselen trend çizgisi altında kapanış.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 082 — Uyumsuzluk — MACD çizgisi ve histogramında çift bullish divergence + son düşen trend çizgisi üstünde kapanış

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** MACD çizgisi ve histogramında çift bullish divergence; son düşen trend çizgisi üstünde kapanış; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: MACD çizgisi ve histogramında çift bullish divergence. Giriş teyidi: son düşen trend çizgisi üstünde kapanış.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: MACD çizgisi ve histogramında çift bearish divergence. Giriş teyidi: son yükselen trend çizgisi altında kapanış.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 083 — Uyumsuzluk — MFI14 bullish divergence + son düşen trend çizgisi üstünde kapanış

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** MFI14 bullish divergence; son düşen trend çizgisi üstünde kapanış; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: MFI14 bullish divergence. Giriş teyidi: son düşen trend çizgisi üstünde kapanış.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: MFI14 bearish divergence. Giriş teyidi: son yükselen trend çizgisi altında kapanış.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 084 — Uyumsuzluk — OBV bullish divergence + son düşen trend çizgisi üstünde kapanış

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** OBV bullish divergence; son düşen trend çizgisi üstünde kapanış; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: OBV bullish divergence. Giriş teyidi: son düşen trend çizgisi üstünde kapanış.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: OBV bearish divergence. Giriş teyidi: son yükselen trend çizgisi altında kapanış.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 085 — Uyumsuzluk — Stochastic bullish divergence + son düşen trend çizgisi üstünde kapanış

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** Stochastic bullish divergence; son düşen trend çizgisi üstünde kapanış; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: Stochastic bullish divergence. Giriş teyidi: son düşen trend çizgisi üstünde kapanış.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: Stochastic bearish divergence. Giriş teyidi: son yükselen trend çizgisi altında kapanış.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 086 — Uyumsuzluk — RSI14 regular bullish divergence + son lower-high üstünde BOS kapanışı

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** RSI14 regular bullish divergence; son lower-high üstünde BOS kapanışı; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: RSI14 regular bullish divergence. Giriş teyidi: son lower-high üstünde BOS kapanışı.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: RSI14 regular bearish divergence. Giriş teyidi: son higher-low altında BOS kapanışı.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 087 — Uyumsuzluk — MACD çizgisi ve histogramında çift bullish divergence + son lower-high üstünde BOS kapanışı

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** MACD çizgisi ve histogramında çift bullish divergence; son lower-high üstünde BOS kapanışı; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: MACD çizgisi ve histogramında çift bullish divergence. Giriş teyidi: son lower-high üstünde BOS kapanışı.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: MACD çizgisi ve histogramında çift bearish divergence. Giriş teyidi: son higher-low altında BOS kapanışı.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 088 — Uyumsuzluk — MFI14 bullish divergence + son lower-high üstünde BOS kapanışı

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** MFI14 bullish divergence; son lower-high üstünde BOS kapanışı; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: MFI14 bullish divergence. Giriş teyidi: son lower-high üstünde BOS kapanışı.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: MFI14 bearish divergence. Giriş teyidi: son higher-low altında BOS kapanışı.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 089 — Uyumsuzluk — OBV bullish divergence + son lower-high üstünde BOS kapanışı

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** OBV bullish divergence; son lower-high üstünde BOS kapanışı; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: OBV bullish divergence. Giriş teyidi: son lower-high üstünde BOS kapanışı.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: OBV bearish divergence. Giriş teyidi: son higher-low altında BOS kapanışı.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 090 — Uyumsuzluk — Stochastic bullish divergence + son lower-high üstünde BOS kapanışı

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** Stochastic bullish divergence; son lower-high üstünde BOS kapanışı; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: Stochastic bullish divergence. Giriş teyidi: son lower-high üstünde BOS kapanışı.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: Stochastic bearish divergence. Giriş teyidi: son higher-low altında BOS kapanışı.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 091 — Uyumsuzluk — RSI14 regular bullish divergence + bullish engulfing ve hacim z≥0.7

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** RSI14 regular bullish divergence; bullish engulfing ve hacim z≥0.7; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: RSI14 regular bullish divergence. Giriş teyidi: bullish engulfing ve hacim z≥0.7.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: RSI14 regular bearish divergence. Giriş teyidi: bearish engulfing ve hacim z≥0.7.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 092 — Uyumsuzluk — MACD çizgisi ve histogramında çift bullish divergence + bullish engulfing ve hacim z≥0.7

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** MACD çizgisi ve histogramında çift bullish divergence; bullish engulfing ve hacim z≥0.7; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: MACD çizgisi ve histogramında çift bullish divergence. Giriş teyidi: bullish engulfing ve hacim z≥0.7.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: MACD çizgisi ve histogramında çift bearish divergence. Giriş teyidi: bearish engulfing ve hacim z≥0.7.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 093 — Uyumsuzluk — MFI14 bullish divergence + bullish engulfing ve hacim z≥0.7

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** MFI14 bullish divergence; bullish engulfing ve hacim z≥0.7; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: MFI14 bullish divergence. Giriş teyidi: bullish engulfing ve hacim z≥0.7.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: MFI14 bearish divergence. Giriş teyidi: bearish engulfing ve hacim z≥0.7.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 094 — Uyumsuzluk — OBV bullish divergence + bullish engulfing ve hacim z≥0.7

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** OBV bullish divergence; bullish engulfing ve hacim z≥0.7; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: OBV bullish divergence. Giriş teyidi: bullish engulfing ve hacim z≥0.7.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: OBV bearish divergence. Giriş teyidi: bearish engulfing ve hacim z≥0.7.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 095 — Uyumsuzluk — Stochastic bullish divergence + bullish engulfing ve hacim z≥0.7

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** Stochastic bullish divergence; bullish engulfing ve hacim z≥0.7; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: Stochastic bullish divergence. Giriş teyidi: bullish engulfing ve hacim z≥0.7.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: Stochastic bearish divergence. Giriş teyidi: bearish engulfing ve hacim z≥0.7.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 096 — Uyumsuzluk — RSI14 regular bullish divergence + ikili dip boyun çizgisi üstünde kapanış

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** RSI14 regular bullish divergence; ikili dip boyun çizgisi üstünde kapanış; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: RSI14 regular bullish divergence. Giriş teyidi: ikili dip boyun çizgisi üstünde kapanış.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: RSI14 regular bearish divergence. Giriş teyidi: ikili tepe boyun çizgisi altında kapanış.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 097 — Uyumsuzluk — MACD çizgisi ve histogramında çift bullish divergence + ikili dip boyun çizgisi üstünde kapanış

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** MACD çizgisi ve histogramında çift bullish divergence; ikili dip boyun çizgisi üstünde kapanış; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: MACD çizgisi ve histogramında çift bullish divergence. Giriş teyidi: ikili dip boyun çizgisi üstünde kapanış.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: MACD çizgisi ve histogramında çift bearish divergence. Giriş teyidi: ikili tepe boyun çizgisi altında kapanış.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 098 — Uyumsuzluk — MFI14 bullish divergence + ikili dip boyun çizgisi üstünde kapanış

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** MFI14 bullish divergence; ikili dip boyun çizgisi üstünde kapanış; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: MFI14 bullish divergence. Giriş teyidi: ikili dip boyun çizgisi üstünde kapanış.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: MFI14 bearish divergence. Giriş teyidi: ikili tepe boyun çizgisi altında kapanış.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 099 — Uyumsuzluk — OBV bullish divergence + ikili dip boyun çizgisi üstünde kapanış

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** OBV bullish divergence; ikili dip boyun çizgisi üstünde kapanış; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: OBV bullish divergence. Giriş teyidi: ikili dip boyun çizgisi üstünde kapanış.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: OBV bearish divergence. Giriş teyidi: ikili tepe boyun çizgisi altında kapanış.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)

## 100 — Uyumsuzluk — Stochastic bullish divergence + ikili dip boyun çizgisi üstünde kapanış

- **Aile / rejim:** Divergence dönüş/erken trend değişimi — Yorulan trend veya majör seviye; tek başına divergence yeterli değil.
- **Bileşenler:** Stochastic bullish divergence; ikili dip boyun çizgisi üstünde kapanış; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat dibi arasında 5–60 bar. İkinci fiyat dibi daha düşük/eşitken göstergenin ikinci dibi daha yüksek: Stochastic bullish divergence. Giriş teyidi: ikili dip boyun çizgisi üstünde kapanış.
- **SHORT kurulumu:** Pivotlar kesinleşmiş olmalı: iki fiyat tepesi arasında 5–60 bar. İkinci fiyat tepesi daha yüksek/eşitken göstergenin ikinci tepesi daha düşük: Stochastic bearish divergence. Giriş teyidi: ikili tepe boyun çizgisi altında kapanış.
- **Emir/giriş (LONG):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Emir/giriş (SHORT):** Yapı teyit kapanışından sonraki açılış; pivot onayı için gelecekteki mum kullanılmaz. Gecikmiş sinyalde fiyat tetik seviyesinden >0.75 ATR uzaksa pas.
- **Stop ve boyut (LONG):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Stop ve boyut (SHORT):** İkinci pivot ekstreminden 0.20 ATR öte. Risk %0.35; dönüş işlemleri trend devamından daha düşük boyutlanır.
- **Çıkış (LONG):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **Çıkış (SHORT):** 1R'de %33; EMA50/önceki swing seviyesinde %33; kalan 2.5R veya karşıt divergence/yapı kırılımında.
- **İşlem yok / geçersiz:** İkinci pivotta ADX artıyor ve DI trend yönünde genişliyorsa; divergence genliği gösterge normal aralığının %5'inden küçükse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V31](#v31) [V45](#v45) [V46](#v46) [V50](#v50) [D01](#d01) [D02](#d02) [D09](#d09) [D11](#d11)


# Mum ve mikro-yapı

## 101 — Fiyat aksiyonu — bullish engulfing / yükselen EMA50 ve ona ±0.30 ATR temas

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** bullish engulfing: mevcut gövde önceki gövdeyi tamamen kapsar ve kapanış üst %25'te; yükselen EMA50 ve ona ±0.30 ATR temas; hacim; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Bağlam zorunlu: yükselen EMA50 ve ona ±0.30 ATR temas. Formasyon: bullish engulfing: mevcut gövde önceki gövdeyi tamamen kapsar ve kapanış üst %25'te. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: düşen EMA50 ve ona ±0.30 ATR temas. Formasyon: bearish engulfing: mevcut gövde önceki gövdeyi tamamen kapsar ve kapanış alt %25'te. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 102 — Fiyat aksiyonu — bullish pin bar / yükselen EMA50 ve ona ±0.30 ATR temas

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** bullish pin bar: alt fitil gövdenin ≥2 katı, üst fitil ≤gövde, kapanış aralığın üst %35'inde; yükselen EMA50 ve ona ±0.30 ATR temas; hacim; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Bağlam zorunlu: yükselen EMA50 ve ona ±0.30 ATR temas. Formasyon: bullish pin bar: alt fitil gövdenin ≥2 katı, üst fitil ≤gövde, kapanış aralığın üst %35'inde. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: düşen EMA50 ve ona ±0.30 ATR temas. Formasyon: bearish pin bar: üst fitil gövdenin ≥2 katı, alt fitil ≤gövde, kapanış aralığın alt %35'inde. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 103 — Fiyat aksiyonu — pin-inside / yükselen EMA50 ve ona ±0.30 ATR temas

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** pin-inside: bullish pin bardan sonra gelen mum tamamen pin bar aralığında; yükselen EMA50 ve ona ±0.30 ATR temas; hacim; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Bağlam zorunlu: yükselen EMA50 ve ona ±0.30 ATR temas. Formasyon: pin-inside: bullish pin bardan sonra gelen mum tamamen pin bar aralığında. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: düşen EMA50 ve ona ±0.30 ATR temas. Formasyon: pin-inside: bearish pin bardan sonra gelen mum tamamen pin bar aralığında. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 104 — Fiyat aksiyonu — morning star / yükselen EMA50 ve ona ±0.30 ATR temas

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** morning star: düşüş mumu + küçük gövde + ilk gövdenin orta noktası üstünde güçlü kapanış; yükselen EMA50 ve ona ±0.30 ATR temas; hacim; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Bağlam zorunlu: yükselen EMA50 ve ona ±0.30 ATR temas. Formasyon: morning star: düşüş mumu + küçük gövde + ilk gövdenin orta noktası üstünde güçlü kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: düşen EMA50 ve ona ±0.30 ATR temas. Formasyon: evening star: düşüş mumu + küçük gövde + ilk gövdenin orta noktası altında güçlü kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 105 — Fiyat aksiyonu — inside-bar breakout / yükselen EMA50 ve ona ±0.30 ATR temas

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** inside-bar breakout: mother bar sonrası iç mum ve mother high üstü kapanış; yükselen EMA50 ve ona ±0.30 ATR temas; hacim; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Bağlam zorunlu: yükselen EMA50 ve ona ±0.30 ATR temas. Formasyon: inside-bar breakout: mother bar sonrası iç mum ve mother high üstü kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: düşen EMA50 ve ona ±0.30 ATR temas. Formasyon: inside-bar breakout: mother bar sonrası iç mum ve mother low altı kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 106 — Fiyat aksiyonu — bullish engulfing / önceki hafta düşüğü veya onaylı 4H destek sweep'i

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** bullish engulfing: mevcut gövde önceki gövdeyi tamamen kapsar ve kapanış üst %25'te; önceki hafta düşüğü veya onaylı 4H destek sweep'i; hacim; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Bağlam zorunlu: önceki hafta düşüğü veya onaylı 4H destek sweep'i. Formasyon: bullish engulfing: mevcut gövde önceki gövdeyi tamamen kapsar ve kapanış üst %25'te. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: önceki hafta yükseği veya onaylı 4H direnç sweep'i. Formasyon: bearish engulfing: mevcut gövde önceki gövdeyi tamamen kapsar ve kapanış alt %25'te. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 107 — Fiyat aksiyonu — bullish pin bar / önceki hafta düşüğü veya onaylı 4H destek sweep'i

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** bullish pin bar: alt fitil gövdenin ≥2 katı, üst fitil ≤gövde, kapanış aralığın üst %35'inde; önceki hafta düşüğü veya onaylı 4H destek sweep'i; hacim; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Bağlam zorunlu: önceki hafta düşüğü veya onaylı 4H destek sweep'i. Formasyon: bullish pin bar: alt fitil gövdenin ≥2 katı, üst fitil ≤gövde, kapanış aralığın üst %35'inde. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: önceki hafta yükseği veya onaylı 4H direnç sweep'i. Formasyon: bearish pin bar: üst fitil gövdenin ≥2 katı, alt fitil ≤gövde, kapanış aralığın alt %35'inde. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 108 — Fiyat aksiyonu — pin-inside / önceki hafta düşüğü veya onaylı 4H destek sweep'i

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** pin-inside: bullish pin bardan sonra gelen mum tamamen pin bar aralığında; önceki hafta düşüğü veya onaylı 4H destek sweep'i; hacim; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Bağlam zorunlu: önceki hafta düşüğü veya onaylı 4H destek sweep'i. Formasyon: pin-inside: bullish pin bardan sonra gelen mum tamamen pin bar aralığında. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: önceki hafta yükseği veya onaylı 4H direnç sweep'i. Formasyon: pin-inside: bearish pin bardan sonra gelen mum tamamen pin bar aralığında. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 109 — Fiyat aksiyonu — morning star / önceki hafta düşüğü veya onaylı 4H destek sweep'i

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** morning star: düşüş mumu + küçük gövde + ilk gövdenin orta noktası üstünde güçlü kapanış; önceki hafta düşüğü veya onaylı 4H destek sweep'i; hacim; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Bağlam zorunlu: önceki hafta düşüğü veya onaylı 4H destek sweep'i. Formasyon: morning star: düşüş mumu + küçük gövde + ilk gövdenin orta noktası üstünde güçlü kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: önceki hafta yükseği veya onaylı 4H direnç sweep'i. Formasyon: evening star: düşüş mumu + küçük gövde + ilk gövdenin orta noktası altında güçlü kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 110 — Fiyat aksiyonu — inside-bar breakout / önceki hafta düşüğü veya onaylı 4H destek sweep'i

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** inside-bar breakout: mother bar sonrası iç mum ve mother high üstü kapanış; önceki hafta düşüğü veya onaylı 4H destek sweep'i; hacim; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Bağlam zorunlu: önceki hafta düşüğü veya onaylı 4H destek sweep'i. Formasyon: inside-bar breakout: mother bar sonrası iç mum ve mother high üstü kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: önceki hafta yükseği veya onaylı 4H direnç sweep'i. Formasyon: inside-bar breakout: mother bar sonrası iç mum ve mother low altı kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 111 — Fiyat aksiyonu — bullish engulfing / %38.2–%61.8 son impuls retracement bölgesi

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** bullish engulfing: mevcut gövde önceki gövdeyi tamamen kapsar ve kapanış üst %25'te; %38.2–%61.8 son impuls retracement bölgesi; hacim; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Bağlam zorunlu: %38.2–%61.8 son impuls retracement bölgesi. Formasyon: bullish engulfing: mevcut gövde önceki gövdeyi tamamen kapsar ve kapanış üst %25'te. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: %38.2–%61.8 son impuls retracement bölgesi. Formasyon: bearish engulfing: mevcut gövde önceki gövdeyi tamamen kapsar ve kapanış alt %25'te. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 112 — Fiyat aksiyonu — bullish pin bar / %38.2–%61.8 son impuls retracement bölgesi

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** bullish pin bar: alt fitil gövdenin ≥2 katı, üst fitil ≤gövde, kapanış aralığın üst %35'inde; %38.2–%61.8 son impuls retracement bölgesi; hacim; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Bağlam zorunlu: %38.2–%61.8 son impuls retracement bölgesi. Formasyon: bullish pin bar: alt fitil gövdenin ≥2 katı, üst fitil ≤gövde, kapanış aralığın üst %35'inde. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: %38.2–%61.8 son impuls retracement bölgesi. Formasyon: bearish pin bar: üst fitil gövdenin ≥2 katı, alt fitil ≤gövde, kapanış aralığın alt %35'inde. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 113 — Fiyat aksiyonu — pin-inside / %38.2–%61.8 son impuls retracement bölgesi

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** pin-inside: bullish pin bardan sonra gelen mum tamamen pin bar aralığında; %38.2–%61.8 son impuls retracement bölgesi; hacim; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Bağlam zorunlu: %38.2–%61.8 son impuls retracement bölgesi. Formasyon: pin-inside: bullish pin bardan sonra gelen mum tamamen pin bar aralığında. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: %38.2–%61.8 son impuls retracement bölgesi. Formasyon: pin-inside: bearish pin bardan sonra gelen mum tamamen pin bar aralığında. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 114 — Fiyat aksiyonu — morning star / %38.2–%61.8 son impuls retracement bölgesi

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** morning star: düşüş mumu + küçük gövde + ilk gövdenin orta noktası üstünde güçlü kapanış; %38.2–%61.8 son impuls retracement bölgesi; hacim; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Bağlam zorunlu: %38.2–%61.8 son impuls retracement bölgesi. Formasyon: morning star: düşüş mumu + küçük gövde + ilk gövdenin orta noktası üstünde güçlü kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: %38.2–%61.8 son impuls retracement bölgesi. Formasyon: evening star: düşüş mumu + küçük gövde + ilk gövdenin orta noktası altında güçlü kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 115 — Fiyat aksiyonu — inside-bar breakout / %38.2–%61.8 son impuls retracement bölgesi

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** inside-bar breakout: mother bar sonrası iç mum ve mother high üstü kapanış; %38.2–%61.8 son impuls retracement bölgesi; hacim; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Bağlam zorunlu: %38.2–%61.8 son impuls retracement bölgesi. Formasyon: inside-bar breakout: mother bar sonrası iç mum ve mother high üstü kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: %38.2–%61.8 son impuls retracement bölgesi. Formasyon: inside-bar breakout: mother bar sonrası iç mum ve mother low altı kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 116 — Fiyat aksiyonu — bullish engulfing / Donchian20 kırılımının ilk retesti

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** bullish engulfing: mevcut gövde önceki gövdeyi tamamen kapsar ve kapanış üst %25'te; Donchian20 kırılımının ilk retesti; hacim; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Bağlam zorunlu: Donchian20 kırılımının ilk retesti. Formasyon: bullish engulfing: mevcut gövde önceki gövdeyi tamamen kapsar ve kapanış üst %25'te. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: Donchian20 kırılımının ilk retesti. Formasyon: bearish engulfing: mevcut gövde önceki gövdeyi tamamen kapsar ve kapanış alt %25'te. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 117 — Fiyat aksiyonu — bullish pin bar / Donchian20 kırılımının ilk retesti

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** bullish pin bar: alt fitil gövdenin ≥2 katı, üst fitil ≤gövde, kapanış aralığın üst %35'inde; Donchian20 kırılımının ilk retesti; hacim; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Bağlam zorunlu: Donchian20 kırılımının ilk retesti. Formasyon: bullish pin bar: alt fitil gövdenin ≥2 katı, üst fitil ≤gövde, kapanış aralığın üst %35'inde. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: Donchian20 kırılımının ilk retesti. Formasyon: bearish pin bar: üst fitil gövdenin ≥2 katı, alt fitil ≤gövde, kapanış aralığın alt %35'inde. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 118 — Fiyat aksiyonu — pin-inside / Donchian20 kırılımının ilk retesti

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** pin-inside: bullish pin bardan sonra gelen mum tamamen pin bar aralığında; Donchian20 kırılımının ilk retesti; hacim; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Bağlam zorunlu: Donchian20 kırılımının ilk retesti. Formasyon: pin-inside: bullish pin bardan sonra gelen mum tamamen pin bar aralığında. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: Donchian20 kırılımının ilk retesti. Formasyon: pin-inside: bearish pin bardan sonra gelen mum tamamen pin bar aralığında. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 119 — Fiyat aksiyonu — morning star / Donchian20 kırılımının ilk retesti

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** morning star: düşüş mumu + küçük gövde + ilk gövdenin orta noktası üstünde güçlü kapanış; Donchian20 kırılımının ilk retesti; hacim; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Bağlam zorunlu: Donchian20 kırılımının ilk retesti. Formasyon: morning star: düşüş mumu + küçük gövde + ilk gövdenin orta noktası üstünde güçlü kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: Donchian20 kırılımının ilk retesti. Formasyon: evening star: düşüş mumu + küçük gövde + ilk gövdenin orta noktası altında güçlü kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)

## 120 — Fiyat aksiyonu — inside-bar breakout / Donchian20 kırılımının ilk retesti

- **Aile / rejim:** Mum ve mikro-yapı — Trend pullback, sweep dönüşü veya retest.
- **Bileşenler:** inside-bar breakout: mother bar sonrası iç mum ve mother high üstü kapanış; Donchian20 kırılımının ilk retesti; hacim; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Bağlam zorunlu: Donchian20 kırılımının ilk retesti. Formasyon: inside-bar breakout: mother bar sonrası iç mum ve mother high üstü kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon tepesini kırmalı.
- **SHORT kurulumu:** Bağlam zorunlu: Donchian20 kırılımının ilk retesti. Formasyon: inside-bar breakout: mother bar sonrası iç mum ve mother low altı kapanış. Formasyon mumu hacmi 20-bar medyanının ≥1.1 katı veya takip mumu formasyon dibini kırmalı.
- **Emir/giriş (LONG):** Formasyon tepesine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Emir/giriş (SHORT):** Formasyon dibine 1 tick/0.02 ATR stop-emir; 2 bar içinde tetiklenmezse iptal. Geniş gap ile açılırsa (>0.3 ATR) takip edilmez.
- **Stop ve boyut (LONG):** Formasyonun en düşük noktasının 0.10 ATR altı; formasyon aralığı >2 ATR ise pas.
- **Stop ve boyut (SHORT):** Formasyonun en yüksek noktasının 0.10 ATR üstü; formasyon aralığı >2 ATR ise pas.
- **Çıkış (LONG):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun düşüğüyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **Çıkış (SHORT):** 1R'de stop maliyet; 2R'de %60; kalan son 2 mumun yükseğiyle izlenir. Karşıt güçlü engulfing kapanışında tamamen çık.
- **İşlem yok / geçersiz:** Formasyon tek başına, bağlam seviyesinden >0.5 ATR uzakta ise geçersiz. Doji/çok küçük gövde takip teyidi olmadan kullanılmaz.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V10](#v10) [V14](#v14) [V15](#v15) [V21](#v21) [V22](#v22) [V25](#v25) [V36](#v36)


# Hacim ve değer alanı

## 121 — Hacim teyidi — OBV son 20 bar tepesini fiyat tepesinden önce kırar + EMA20>EMA50

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** OBV son 20 bar tepesini fiyat tepesinden önce kırar; EMA20>EMA50 ve son 10 bar tepesinin kırılması; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Hacim/katılım koşulu: OBV son 20 bar tepesini fiyat tepesinden önce kırar. Fiyat koşulu: EMA20>EMA50 ve son 10 bar tepesinin kırılması. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: OBV son 20 bar dibini fiyat dibinden önce kırar. Fiyat koşulu: EMA20<EMA50 ve son 10 bar dibinin kırılması. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 122 — Hacim teyidi — CMF20 -0.05 altından 0 üstüne geçer + EMA20>EMA50

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** CMF20 -0.05 altından 0 üstüne geçer; EMA20>EMA50 ve son 10 bar tepesinin kırılması; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Hacim/katılım koşulu: CMF20 -0.05 altından 0 üstüne geçer. Fiyat koşulu: EMA20>EMA50 ve son 10 bar tepesinin kırılması. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: CMF20 0.05 üstünden 0 altına geçer. Fiyat koşulu: EMA20<EMA50 ve son 10 bar dibinin kırılması. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 123 — Hacim teyidi — MFI14 50 üstüne geçer ve raw-volume z≥1 + EMA20>EMA50

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** MFI14 50 üstüne geçer ve raw-volume z≥1; EMA20>EMA50 ve son 10 bar tepesinin kırılması; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Hacim/katılım koşulu: MFI14 50 üstüne geçer ve raw-volume z≥1. Fiyat koşulu: EMA20>EMA50 ve son 10 bar tepesinin kırılması. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: MFI14 50 altına geçer ve raw-volume z≥1. Fiyat koşulu: EMA20<EMA50 ve son 10 bar dibinin kırılması. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 124 — Hacim teyidi — haftalık AVWAP üstünde kabul + EMA20>EMA50

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** haftalık AVWAP üstünde kabul: art arda 2 kapanış; EMA20>EMA50 ve son 10 bar tepesinin kırılması; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Hacim/katılım koşulu: haftalık AVWAP üstünde kabul: art arda 2 kapanış. Fiyat koşulu: EMA20>EMA50 ve son 10 bar tepesinin kırılması. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: haftalık AVWAP altında kabul: art arda 2 kapanış. Fiyat koşulu: EMA20<EMA50 ve son 10 bar dibinin kırılması. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 125 — Hacim teyidi — Volume Profile VAH üstünde kapanış ve POC yukarı göç eder + EMA20>EMA50

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** Volume Profile VAH üstünde kapanış ve POC yukarı göç eder; EMA20>EMA50 ve son 10 bar tepesinin kırılması; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Hacim/katılım koşulu: Volume Profile VAH üstünde kapanış ve POC yukarı göç eder. Fiyat koşulu: EMA20>EMA50 ve son 10 bar tepesinin kırılması. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: Volume Profile VAL altında kapanış ve POC aşağı göç eder. Fiyat koşulu: EMA20<EMA50 ve son 10 bar dibinin kırılması. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 126 — Hacim teyidi — OBV son 20 bar tepesini fiyat tepesinden önce kırar + kırılan direncin ilk retestinde bullish pin/engulfing

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** OBV son 20 bar tepesini fiyat tepesinden önce kırar; kırılan direncin ilk retestinde bullish pin/engulfing; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Hacim/katılım koşulu: OBV son 20 bar tepesini fiyat tepesinden önce kırar. Fiyat koşulu: kırılan direncin ilk retestinde bullish pin/engulfing. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: OBV son 20 bar dibini fiyat dibinden önce kırar. Fiyat koşulu: kırılan direncin ilk retestinde bearish pin/engulfing. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 127 — Hacim teyidi — CMF20 -0.05 altından 0 üstüne geçer + kırılan direncin ilk retestinde bullish pin/engulfing

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** CMF20 -0.05 altından 0 üstüne geçer; kırılan direncin ilk retestinde bullish pin/engulfing; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Hacim/katılım koşulu: CMF20 -0.05 altından 0 üstüne geçer. Fiyat koşulu: kırılan direncin ilk retestinde bullish pin/engulfing. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: CMF20 0.05 üstünden 0 altına geçer. Fiyat koşulu: kırılan direncin ilk retestinde bearish pin/engulfing. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 128 — Hacim teyidi — MFI14 50 üstüne geçer ve raw-volume z≥1 + kırılan direncin ilk retestinde bullish pin/engulfing

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** MFI14 50 üstüne geçer ve raw-volume z≥1; kırılan direncin ilk retestinde bullish pin/engulfing; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Hacim/katılım koşulu: MFI14 50 üstüne geçer ve raw-volume z≥1. Fiyat koşulu: kırılan direncin ilk retestinde bullish pin/engulfing. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: MFI14 50 altına geçer ve raw-volume z≥1. Fiyat koşulu: kırılan direncin ilk retestinde bearish pin/engulfing. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 129 — Hacim teyidi — haftalık AVWAP üstünde kabul + kırılan direncin ilk retestinde bullish pin/engulfing

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** haftalık AVWAP üstünde kabul: art arda 2 kapanış; kırılan direncin ilk retestinde bullish pin/engulfing; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Hacim/katılım koşulu: haftalık AVWAP üstünde kabul: art arda 2 kapanış. Fiyat koşulu: kırılan direncin ilk retestinde bullish pin/engulfing. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: haftalık AVWAP altında kabul: art arda 2 kapanış. Fiyat koşulu: kırılan direncin ilk retestinde bearish pin/engulfing. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 130 — Hacim teyidi — Volume Profile VAH üstünde kapanış ve POC yukarı göç eder + kırılan direncin ilk retestinde bullish pin/engulfing

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** Volume Profile VAH üstünde kapanış ve POC yukarı göç eder; kırılan direncin ilk retestinde bullish pin/engulfing; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Hacim/katılım koşulu: Volume Profile VAH üstünde kapanış ve POC yukarı göç eder. Fiyat koşulu: kırılan direncin ilk retestinde bullish pin/engulfing. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: Volume Profile VAL altında kapanış ve POC aşağı göç eder. Fiyat koşulu: kırılan direncin ilk retestinde bearish pin/engulfing. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 131 — Hacim teyidi — OBV son 20 bar tepesini fiyat tepesinden önce kırar + RSI14 50 üstü

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** OBV son 20 bar tepesini fiyat tepesinden önce kırar; RSI14 50 üstü ve MACD histogramı pozitif; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Hacim/katılım koşulu: OBV son 20 bar tepesini fiyat tepesinden önce kırar. Fiyat koşulu: RSI14 50 üstü ve MACD histogramı pozitif. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: OBV son 20 bar dibini fiyat dibinden önce kırar. Fiyat koşulu: RSI14 50 üstü ve MACD histogramı negatif. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 132 — Hacim teyidi — CMF20 -0.05 altından 0 üstüne geçer + RSI14 50 üstü

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** CMF20 -0.05 altından 0 üstüne geçer; RSI14 50 üstü ve MACD histogramı pozitif; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Hacim/katılım koşulu: CMF20 -0.05 altından 0 üstüne geçer. Fiyat koşulu: RSI14 50 üstü ve MACD histogramı pozitif. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: CMF20 0.05 üstünden 0 altına geçer. Fiyat koşulu: RSI14 50 üstü ve MACD histogramı negatif. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 133 — Hacim teyidi — MFI14 50 üstüne geçer ve raw-volume z≥1 + RSI14 50 üstü

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** MFI14 50 üstüne geçer ve raw-volume z≥1; RSI14 50 üstü ve MACD histogramı pozitif; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Hacim/katılım koşulu: MFI14 50 üstüne geçer ve raw-volume z≥1. Fiyat koşulu: RSI14 50 üstü ve MACD histogramı pozitif. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: MFI14 50 altına geçer ve raw-volume z≥1. Fiyat koşulu: RSI14 50 üstü ve MACD histogramı negatif. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 134 — Hacim teyidi — haftalık AVWAP üstünde kabul + RSI14 50 üstü

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** haftalık AVWAP üstünde kabul: art arda 2 kapanış; RSI14 50 üstü ve MACD histogramı pozitif; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Hacim/katılım koşulu: haftalık AVWAP üstünde kabul: art arda 2 kapanış. Fiyat koşulu: RSI14 50 üstü ve MACD histogramı pozitif. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: haftalık AVWAP altında kabul: art arda 2 kapanış. Fiyat koşulu: RSI14 50 üstü ve MACD histogramı negatif. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 135 — Hacim teyidi — Volume Profile VAH üstünde kapanış ve POC yukarı göç eder + RSI14 50 üstü

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** Volume Profile VAH üstünde kapanış ve POC yukarı göç eder; RSI14 50 üstü ve MACD histogramı pozitif; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Hacim/katılım koşulu: Volume Profile VAH üstünde kapanış ve POC yukarı göç eder. Fiyat koşulu: RSI14 50 üstü ve MACD histogramı pozitif. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: Volume Profile VAL altında kapanış ve POC aşağı göç eder. Fiyat koşulu: RSI14 50 üstü ve MACD histogramı negatif. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 136 — Hacim teyidi — OBV son 20 bar tepesini fiyat tepesinden önce kırar + ADX14 20 üstüne geçer

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** OBV son 20 bar tepesini fiyat tepesinden önce kırar; ADX14 20 üstüne geçer ve +DI>-DI; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Hacim/katılım koşulu: OBV son 20 bar tepesini fiyat tepesinden önce kırar. Fiyat koşulu: ADX14 20 üstüne geçer ve +DI>-DI. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: OBV son 20 bar dibini fiyat dibinden önce kırar. Fiyat koşulu: ADX14 20 altına geçer ve -DI>+DI. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 137 — Hacim teyidi — CMF20 -0.05 altından 0 üstüne geçer + ADX14 20 üstüne geçer

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** CMF20 -0.05 altından 0 üstüne geçer; ADX14 20 üstüne geçer ve +DI>-DI; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Hacim/katılım koşulu: CMF20 -0.05 altından 0 üstüne geçer. Fiyat koşulu: ADX14 20 üstüne geçer ve +DI>-DI. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: CMF20 0.05 üstünden 0 altına geçer. Fiyat koşulu: ADX14 20 altına geçer ve -DI>+DI. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 138 — Hacim teyidi — MFI14 50 üstüne geçer ve raw-volume z≥1 + ADX14 20 üstüne geçer

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** MFI14 50 üstüne geçer ve raw-volume z≥1; ADX14 20 üstüne geçer ve +DI>-DI; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Hacim/katılım koşulu: MFI14 50 üstüne geçer ve raw-volume z≥1. Fiyat koşulu: ADX14 20 üstüne geçer ve +DI>-DI. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: MFI14 50 altına geçer ve raw-volume z≥1. Fiyat koşulu: ADX14 20 altına geçer ve -DI>+DI. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 139 — Hacim teyidi — haftalık AVWAP üstünde kabul + ADX14 20 üstüne geçer

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** haftalık AVWAP üstünde kabul: art arda 2 kapanış; ADX14 20 üstüne geçer ve +DI>-DI; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Hacim/katılım koşulu: haftalık AVWAP üstünde kabul: art arda 2 kapanış. Fiyat koşulu: ADX14 20 üstüne geçer ve +DI>-DI. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: haftalık AVWAP altında kabul: art arda 2 kapanış. Fiyat koşulu: ADX14 20 altına geçer ve -DI>+DI. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)

## 140 — Hacim teyidi — Volume Profile VAH üstünde kapanış ve POC yukarı göç eder + ADX14 20 üstüne geçer

- **Aile / rejim:** Hacim ve değer alanı — Katılımın fiyat hareketini doğruladığı trend/kırılım.
- **Bileşenler:** Volume Profile VAH üstünde kapanış ve POC yukarı göç eder; ADX14 20 üstüne geçer ve +DI>-DI; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Hacim/katılım koşulu: Volume Profile VAH üstünde kapanış ve POC yukarı göç eder. Fiyat koşulu: ADX14 20 üstüne geçer ve +DI>-DI. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **SHORT kurulumu:** Hacim/katılım koşulu: Volume Profile VAL altında kapanış ve POC aşağı göç eder. Fiyat koşulu: ADX14 20 altına geçer ve -DI>+DI. Hacim sinyali fiyat sinyalinden en fazla 5 bar önce oluşabilir.
- **Emir/giriş (LONG):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Emir/giriş (SHORT):** Fiyat tetik kapanışından sonraki açılış; profil seviyesinde retest seçeneği ayrı varyant olarak test edilir.
- **Stop ve boyut (LONG):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAH altı; en fazla 2 ATR.
- **Stop ve boyut (SHORT):** Fiyat tetik yapısının 0.20 ATR ötesi veya AVWAP/VAL üstü; en fazla 2 ATR.
- **Çıkış (LONG):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **Çıkış (SHORT):** 1.5R'de %50; karşı değer alanı/önceki swingte %25; OBV/CMF ters sinyal + fiyat EMA20 ihlalinde kalan.
- **İşlem yok / geçersiz:** Borsada güvenilir hacim yoksa MFI/OBV/CMF yöntemleri kullanılmaz. Stablecoin/parite hacmi değişimlerinde veri sürekliliği kontrol edilir.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V26](#v26) [V32](#v32) [V39](#v39) [V40](#v40) [V42](#v42) [V44](#v44) [D08](#d08) [D09](#d09) [D11](#d11) [D12](#d12)


# Ichimoku / Supertrend / DMI

## 141 — Trend sistemi — Ichimoku + Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** Ichimoku: fiyat Kumo üstünde, Senkou A>B, Chikou 26 bar önceki fiyat üstünde; Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Trend durumu: Ichimoku: fiyat Kumo üstünde, Senkou A>B, Chikou 26 bar önceki fiyat üstünde. Tetik: Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: Ichimoku: fiyat Kumo altında, Senkou A<B, Chikou 26 bar önceki fiyat altında. Tetik: Tenkan Kijun'u aşağı keser / fiyat Kijun'a retest yapar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 142 — Trend sistemi — Supertrend(10,3) yukarı ve EMA200 üstünde + Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** Supertrend(10,3) yukarı ve EMA200 üstünde; Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Trend durumu: Supertrend(10,3) yukarı ve EMA200 üstünde. Tetik: Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: Supertrend(10,3) aşağı ve EMA200 altında. Tetik: Tenkan Kijun'u aşağı keser / fiyat Kijun'a retest yapar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 143 — Trend sistemi — ADX14≥25, yükseliyor ve +DI>-DI + Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** ADX14≥25, yükseliyor ve +DI>-DI; Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Trend durumu: ADX14≥25, yükseliyor ve +DI>-DI. Tetik: Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: ADX14≥25, düşüyor ve -DI>+DI. Tetik: Tenkan Kijun'u aşağı keser / fiyat Kijun'a retest yapar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 144 — Trend sistemi — üç Supertrend + Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** üç Supertrend: (10,1),(11,2),(12,3) üçü de yukarı; Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Trend durumu: üç Supertrend: (10,1),(11,2),(12,3) üçü de yukarı. Tetik: Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: üç Supertrend: (10,1),(11,2),(12,3) üçü de aşağı. Tetik: Tenkan Kijun'u aşağı keser / fiyat Kijun'a retest yapar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 145 — Trend sistemi — Parabolic SAR fiyat altında ve Supertrend yukarı + Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** Parabolic SAR fiyat altında ve Supertrend yukarı; Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Trend durumu: Parabolic SAR fiyat altında ve Supertrend yukarı. Tetik: Tenkan Kijun'u yukarı keser / fiyat Kijun'a retest yapar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: Parabolic SAR fiyat üstünde ve Supertrend aşağı. Tetik: Tenkan Kijun'u aşağı keser / fiyat Kijun'a retest yapar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 146 — Trend sistemi — Ichimoku + Supertrend aşağıdan yukarı flip eder

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** Ichimoku: fiyat Kumo üstünde, Senkou A>B, Chikou 26 bar önceki fiyat üstünde; Supertrend aşağıdan yukarı flip eder ve sonraki mum flip tepesini kırar; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Trend durumu: Ichimoku: fiyat Kumo üstünde, Senkou A>B, Chikou 26 bar önceki fiyat üstünde. Tetik: Supertrend aşağıdan yukarı flip eder ve sonraki mum flip tepesini kırar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: Ichimoku: fiyat Kumo altında, Senkou A<B, Chikou 26 bar önceki fiyat altında. Tetik: Supertrend yukarıdan aşağı flip eder ve sonraki mum flip dibini kırar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 147 — Trend sistemi — Supertrend(10,3) yukarı ve EMA200 üstünde + Supertrend aşağıdan yukarı flip eder

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** Supertrend(10,3) yukarı ve EMA200 üstünde; Supertrend aşağıdan yukarı flip eder ve sonraki mum flip tepesini kırar; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Trend durumu: Supertrend(10,3) yukarı ve EMA200 üstünde. Tetik: Supertrend aşağıdan yukarı flip eder ve sonraki mum flip tepesini kırar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: Supertrend(10,3) aşağı ve EMA200 altında. Tetik: Supertrend yukarıdan aşağı flip eder ve sonraki mum flip dibini kırar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 148 — Trend sistemi — ADX14≥25, yükseliyor ve +DI>-DI + Supertrend aşağıdan yukarı flip eder

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** ADX14≥25, yükseliyor ve +DI>-DI; Supertrend aşağıdan yukarı flip eder ve sonraki mum flip tepesini kırar; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Trend durumu: ADX14≥25, yükseliyor ve +DI>-DI. Tetik: Supertrend aşağıdan yukarı flip eder ve sonraki mum flip tepesini kırar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: ADX14≥25, düşüyor ve -DI>+DI. Tetik: Supertrend yukarıdan aşağı flip eder ve sonraki mum flip dibini kırar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 149 — Trend sistemi — üç Supertrend + Supertrend aşağıdan yukarı flip eder

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** üç Supertrend: (10,1),(11,2),(12,3) üçü de yukarı; Supertrend aşağıdan yukarı flip eder ve sonraki mum flip tepesini kırar; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Trend durumu: üç Supertrend: (10,1),(11,2),(12,3) üçü de yukarı. Tetik: Supertrend aşağıdan yukarı flip eder ve sonraki mum flip tepesini kırar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: üç Supertrend: (10,1),(11,2),(12,3) üçü de aşağı. Tetik: Supertrend yukarıdan aşağı flip eder ve sonraki mum flip dibini kırar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 150 — Trend sistemi — Parabolic SAR fiyat altında ve Supertrend yukarı + Supertrend aşağıdan yukarı flip eder

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** Parabolic SAR fiyat altında ve Supertrend yukarı; Supertrend aşağıdan yukarı flip eder ve sonraki mum flip tepesini kırar; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Trend durumu: Parabolic SAR fiyat altında ve Supertrend yukarı. Tetik: Supertrend aşağıdan yukarı flip eder ve sonraki mum flip tepesini kırar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: Parabolic SAR fiyat üstünde ve Supertrend aşağı. Tetik: Supertrend yukarıdan aşağı flip eder ve sonraki mum flip dibini kırar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 151 — Trend sistemi — Ichimoku + +DI -DI'yi yukarı keser

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** Ichimoku: fiyat Kumo üstünde, Senkou A>B, Chikou 26 bar önceki fiyat üstünde; +DI -DI'yi yukarı keser ve ADX iki bar artar; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Trend durumu: Ichimoku: fiyat Kumo üstünde, Senkou A>B, Chikou 26 bar önceki fiyat üstünde. Tetik: +DI -DI'yi yukarı keser ve ADX iki bar artar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: Ichimoku: fiyat Kumo altında, Senkou A<B, Chikou 26 bar önceki fiyat altında. Tetik: -DI +DI'yi yukarı keser ve ADX iki bar artar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 152 — Trend sistemi — Supertrend(10,3) yukarı ve EMA200 üstünde + +DI -DI'yi yukarı keser

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** Supertrend(10,3) yukarı ve EMA200 üstünde; +DI -DI'yi yukarı keser ve ADX iki bar artar; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Trend durumu: Supertrend(10,3) yukarı ve EMA200 üstünde. Tetik: +DI -DI'yi yukarı keser ve ADX iki bar artar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: Supertrend(10,3) aşağı ve EMA200 altında. Tetik: -DI +DI'yi yukarı keser ve ADX iki bar artar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 153 — Trend sistemi — ADX14≥25, yükseliyor ve +DI>-DI + +DI -DI'yi yukarı keser

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** ADX14≥25, yükseliyor ve +DI>-DI; +DI -DI'yi yukarı keser ve ADX iki bar artar; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Trend durumu: ADX14≥25, yükseliyor ve +DI>-DI. Tetik: +DI -DI'yi yukarı keser ve ADX iki bar artar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: ADX14≥25, düşüyor ve -DI>+DI. Tetik: -DI +DI'yi yukarı keser ve ADX iki bar artar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 154 — Trend sistemi — üç Supertrend + +DI -DI'yi yukarı keser

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** üç Supertrend: (10,1),(11,2),(12,3) üçü de yukarı; +DI -DI'yi yukarı keser ve ADX iki bar artar; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Trend durumu: üç Supertrend: (10,1),(11,2),(12,3) üçü de yukarı. Tetik: +DI -DI'yi yukarı keser ve ADX iki bar artar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: üç Supertrend: (10,1),(11,2),(12,3) üçü de aşağı. Tetik: -DI +DI'yi yukarı keser ve ADX iki bar artar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 155 — Trend sistemi — Parabolic SAR fiyat altında ve Supertrend yukarı + +DI -DI'yi yukarı keser

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** Parabolic SAR fiyat altında ve Supertrend yukarı; +DI -DI'yi yukarı keser ve ADX iki bar artar; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Trend durumu: Parabolic SAR fiyat altında ve Supertrend yukarı. Tetik: +DI -DI'yi yukarı keser ve ADX iki bar artar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: Parabolic SAR fiyat üstünde ve Supertrend aşağı. Tetik: -DI +DI'yi yukarı keser ve ADX iki bar artar. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 156 — Trend sistemi — Ichimoku + RSI14 50 üstüne geçer

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** Ichimoku: fiyat Kumo üstünde, Senkou A>B, Chikou 26 bar önceki fiyat üstünde; RSI14 50 üstüne geçer ve MACD histogramı pozitif; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Trend durumu: Ichimoku: fiyat Kumo üstünde, Senkou A>B, Chikou 26 bar önceki fiyat üstünde. Tetik: RSI14 50 üstüne geçer ve MACD histogramı pozitif. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: Ichimoku: fiyat Kumo altında, Senkou A<B, Chikou 26 bar önceki fiyat altında. Tetik: RSI14 50 altına geçer ve MACD histogramı negatif. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 157 — Trend sistemi — Supertrend(10,3) yukarı ve EMA200 üstünde + RSI14 50 üstüne geçer

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** Supertrend(10,3) yukarı ve EMA200 üstünde; RSI14 50 üstüne geçer ve MACD histogramı pozitif; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Trend durumu: Supertrend(10,3) yukarı ve EMA200 üstünde. Tetik: RSI14 50 üstüne geçer ve MACD histogramı pozitif. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: Supertrend(10,3) aşağı ve EMA200 altında. Tetik: RSI14 50 altına geçer ve MACD histogramı negatif. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 158 — Trend sistemi — ADX14≥25, yükseliyor ve +DI>-DI + RSI14 50 üstüne geçer

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** ADX14≥25, yükseliyor ve +DI>-DI; RSI14 50 üstüne geçer ve MACD histogramı pozitif; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Trend durumu: ADX14≥25, yükseliyor ve +DI>-DI. Tetik: RSI14 50 üstüne geçer ve MACD histogramı pozitif. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: ADX14≥25, düşüyor ve -DI>+DI. Tetik: RSI14 50 altına geçer ve MACD histogramı negatif. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 159 — Trend sistemi — üç Supertrend + RSI14 50 üstüne geçer

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** üç Supertrend: (10,1),(11,2),(12,3) üçü de yukarı; RSI14 50 üstüne geçer ve MACD histogramı pozitif; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Trend durumu: üç Supertrend: (10,1),(11,2),(12,3) üçü de yukarı. Tetik: RSI14 50 üstüne geçer ve MACD histogramı pozitif. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: üç Supertrend: (10,1),(11,2),(12,3) üçü de aşağı. Tetik: RSI14 50 altına geçer ve MACD histogramı negatif. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)

## 160 — Trend sistemi — Parabolic SAR fiyat altında ve Supertrend yukarı + RSI14 50 üstüne geçer

- **Aile / rejim:** Ichimoku / Supertrend / DMI — Belirgin trend; çizgi bazlı trailing uygun.
- **Bileşenler:** Parabolic SAR fiyat altında ve Supertrend yukarı; RSI14 50 üstüne geçer ve MACD histogramı pozitif; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Trend durumu: Parabolic SAR fiyat altında ve Supertrend yukarı. Tetik: RSI14 50 üstüne geçer ve MACD histogramı pozitif. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **SHORT kurulumu:** Trend durumu: Parabolic SAR fiyat üstünde ve Supertrend aşağı. Tetik: RSI14 50 altına geçer ve MACD histogramı negatif. Kapanış sinyali onaylı olmalı; bulut/çizgi intrabar değişimi kullanılmaz.
- **Emir/giriş (LONG):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Emir/giriş (SHORT):** Sinyal kapanışından sonraki açılış; Ichimoku için bulut içinde emir yok. Supertrend flip mumu >2 ATR ise ilk retest beklenir.
- **Stop ve boyut (LONG):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Stop ve boyut (SHORT):** Kijun/Supertrend/son swing çizgisinin 0.2 ATR ötesi; hangisi girişe daha uzaksa. Risk %0.50.
- **Çıkış (LONG):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **Çıkış (SHORT):** 2R'de %50; kalan Kijun veya en yavaş Supertrend ters kapanışında. ADX tepe yaptıktan sonra 3 bar düşerse stop 1 ATR'ye sıkılaştırılır.
- **İşlem yok / geçersiz:** Ichimoku bulut içinde, Supertrendler ayrışık veya ADX<18 olduğunda yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V07](#v07) [V49](#v49) [D04](#d04) [D14](#d14) [D15](#d15)


# 1D→4H→1H top-down

## 161 — MTF — 1D kapanış EMA50 üstünde / 4H EMA20'ye pullback + RSI 50 reclaim

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D kapanış EMA50 üstünde ve EMA50 yükseliyor; 4H EMA20'ye pullback + RSI 50 reclaim; 1H yapı; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Üst yön: 1D kapanış EMA50 üstünde ve EMA50 yükseliyor. Kurulum: 4H EMA20'ye pullback + RSI 50 reclaim. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D kapanış EMA50 altında ve EMA50 düşüyor. Kurulum: 4H EMA20'ye pullback + RSI 50 reclaim. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 162 — MTF — 1D MACD sıfır üstünde / 4H EMA20'ye pullback + RSI 50 reclaim

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D MACD sıfır üstünde ve histogram artıyor; 4H EMA20'ye pullback + RSI 50 reclaim; 1H yapı; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Üst yön: 1D MACD sıfır üstünde ve histogram artıyor. Kurulum: 4H EMA20'ye pullback + RSI 50 reclaim. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D MACD sıfır altında ve histogram azalıyor. Kurulum: 4H EMA20'ye pullback + RSI 50 reclaim. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 163 — MTF — 1D Ichimoku fiyat bulut üstünde / 4H EMA20'ye pullback + RSI 50 reclaim

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D Ichimoku fiyat bulut üstünde; 4H EMA20'ye pullback + RSI 50 reclaim; 1H yapı; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Üst yön: 1D Ichimoku fiyat bulut üstünde. Kurulum: 4H EMA20'ye pullback + RSI 50 reclaim. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D Ichimoku fiyat bulut altında. Kurulum: 4H EMA20'ye pullback + RSI 50 reclaim. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 164 — MTF — 1D Supertrend(10,3) yukarı / 4H EMA20'ye pullback + RSI 50 reclaim

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D Supertrend(10,3) yukarı; 4H EMA20'ye pullback + RSI 50 reclaim; 1H yapı; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Üst yön: 1D Supertrend(10,3) yukarı. Kurulum: 4H EMA20'ye pullback + RSI 50 reclaim. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D Supertrend(10,3) aşağı. Kurulum: 4H EMA20'ye pullback + RSI 50 reclaim. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 165 — MTF — 1D RSI14 50–70 aralığında / 4H EMA20'ye pullback + RSI 50 reclaim

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D RSI14 50–70 aralığında; 4H EMA20'ye pullback + RSI 50 reclaim; 1H yapı; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Üst yön: 1D RSI14 50–70 aralığında. Kurulum: 4H EMA20'ye pullback + RSI 50 reclaim. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D RSI14 30–50 aralığında. Kurulum: 4H EMA20'ye pullback + RSI 50 reclaim. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 166 — MTF — 1D kapanış EMA50 üstünde / 4H Donchian20 kırılımı ve retest

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D kapanış EMA50 üstünde ve EMA50 yükseliyor; 4H Donchian20 kırılımı ve retest; 1H yapı; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Üst yön: 1D kapanış EMA50 üstünde ve EMA50 yükseliyor. Kurulum: 4H Donchian20 kırılımı ve retest. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D kapanış EMA50 altında ve EMA50 düşüyor. Kurulum: 4H Donchian20 kırılımı ve retest. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 167 — MTF — 1D MACD sıfır üstünde / 4H Donchian20 kırılımı ve retest

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D MACD sıfır üstünde ve histogram artıyor; 4H Donchian20 kırılımı ve retest; 1H yapı; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Üst yön: 1D MACD sıfır üstünde ve histogram artıyor. Kurulum: 4H Donchian20 kırılımı ve retest. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D MACD sıfır altında ve histogram azalıyor. Kurulum: 4H Donchian20 kırılımı ve retest. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 168 — MTF — 1D Ichimoku fiyat bulut üstünde / 4H Donchian20 kırılımı ve retest

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D Ichimoku fiyat bulut üstünde; 4H Donchian20 kırılımı ve retest; 1H yapı; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Üst yön: 1D Ichimoku fiyat bulut üstünde. Kurulum: 4H Donchian20 kırılımı ve retest. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D Ichimoku fiyat bulut altında. Kurulum: 4H Donchian20 kırılımı ve retest. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 169 — MTF — 1D Supertrend(10,3) yukarı / 4H Donchian20 kırılımı ve retest

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D Supertrend(10,3) yukarı; 4H Donchian20 kırılımı ve retest; 1H yapı; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Üst yön: 1D Supertrend(10,3) yukarı. Kurulum: 4H Donchian20 kırılımı ve retest. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D Supertrend(10,3) aşağı. Kurulum: 4H Donchian20 kırılımı ve retest. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 170 — MTF — 1D RSI14 50–70 aralığında / 4H Donchian20 kırılımı ve retest

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D RSI14 50–70 aralığında; 4H Donchian20 kırılımı ve retest; 1H yapı; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Üst yön: 1D RSI14 50–70 aralığında. Kurulum: 4H Donchian20 kırılımı ve retest. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D RSI14 30–50 aralığında. Kurulum: 4H Donchian20 kırılımı ve retest. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 171 — MTF — 1D kapanış EMA50 üstünde / 4H bullish divergence + BOS

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D kapanış EMA50 üstünde ve EMA50 yükseliyor; 4H bullish divergence + BOS; 1H yapı; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Üst yön: 1D kapanış EMA50 üstünde ve EMA50 yükseliyor. Kurulum: 4H bullish divergence + BOS. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D kapanış EMA50 altında ve EMA50 düşüyor. Kurulum: 4H bearish divergence + BOS. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 172 — MTF — 1D MACD sıfır üstünde / 4H bullish divergence + BOS

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D MACD sıfır üstünde ve histogram artıyor; 4H bullish divergence + BOS; 1H yapı; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Üst yön: 1D MACD sıfır üstünde ve histogram artıyor. Kurulum: 4H bullish divergence + BOS. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D MACD sıfır altında ve histogram azalıyor. Kurulum: 4H bearish divergence + BOS. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 173 — MTF — 1D Ichimoku fiyat bulut üstünde / 4H bullish divergence + BOS

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D Ichimoku fiyat bulut üstünde; 4H bullish divergence + BOS; 1H yapı; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Üst yön: 1D Ichimoku fiyat bulut üstünde. Kurulum: 4H bullish divergence + BOS. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D Ichimoku fiyat bulut altında. Kurulum: 4H bearish divergence + BOS. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 174 — MTF — 1D Supertrend(10,3) yukarı / 4H bullish divergence + BOS

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D Supertrend(10,3) yukarı; 4H bullish divergence + BOS; 1H yapı; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Üst yön: 1D Supertrend(10,3) yukarı. Kurulum: 4H bullish divergence + BOS. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D Supertrend(10,3) aşağı. Kurulum: 4H bearish divergence + BOS. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 175 — MTF — 1D RSI14 50–70 aralığında / 4H bullish divergence + BOS

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D RSI14 50–70 aralığında; 4H bullish divergence + BOS; 1H yapı; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Üst yön: 1D RSI14 50–70 aralığında. Kurulum: 4H bullish divergence + BOS. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D RSI14 30–50 aralığında. Kurulum: 4H bearish divergence + BOS. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 176 — MTF — 1D kapanış EMA50 üstünde / 4H BB squeeze sonrası üst bant kapanışı

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D kapanış EMA50 üstünde ve EMA50 yükseliyor; 4H BB squeeze sonrası üst bant kapanışı; 1H yapı; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Üst yön: 1D kapanış EMA50 üstünde ve EMA50 yükseliyor. Kurulum: 4H BB squeeze sonrası üst bant kapanışı. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D kapanış EMA50 altında ve EMA50 düşüyor. Kurulum: 4H BB squeeze sonrası üst bant kapanışı. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 177 — MTF — 1D MACD sıfır üstünde / 4H BB squeeze sonrası üst bant kapanışı

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D MACD sıfır üstünde ve histogram artıyor; 4H BB squeeze sonrası üst bant kapanışı; 1H yapı; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Üst yön: 1D MACD sıfır üstünde ve histogram artıyor. Kurulum: 4H BB squeeze sonrası üst bant kapanışı. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D MACD sıfır altında ve histogram azalıyor. Kurulum: 4H BB squeeze sonrası üst bant kapanışı. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 178 — MTF — 1D Ichimoku fiyat bulut üstünde / 4H BB squeeze sonrası üst bant kapanışı

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D Ichimoku fiyat bulut üstünde; 4H BB squeeze sonrası üst bant kapanışı; 1H yapı; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Üst yön: 1D Ichimoku fiyat bulut üstünde. Kurulum: 4H BB squeeze sonrası üst bant kapanışı. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D Ichimoku fiyat bulut altında. Kurulum: 4H BB squeeze sonrası üst bant kapanışı. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 179 — MTF — 1D Supertrend(10,3) yukarı / 4H BB squeeze sonrası üst bant kapanışı

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D Supertrend(10,3) yukarı; 4H BB squeeze sonrası üst bant kapanışı; 1H yapı; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Üst yön: 1D Supertrend(10,3) yukarı. Kurulum: 4H BB squeeze sonrası üst bant kapanışı. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D Supertrend(10,3) aşağı. Kurulum: 4H BB squeeze sonrası üst bant kapanışı. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)

## 180 — MTF — 1D RSI14 50–70 aralığında / 4H BB squeeze sonrası üst bant kapanışı

- **Aile / rejim:** 1D→4H→1H top-down — Üst zaman trendi, orta zaman kurulum, alt zaman tetik.
- **Bileşenler:** 1D RSI14 50–70 aralığında; 4H BB squeeze sonrası üst bant kapanışı; 1H yapı; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Üst yön: 1D RSI14 50–70 aralığında. Kurulum: 4H BB squeeze sonrası üst bant kapanışı. 1H giriş tetiği: son 5 bar tepesinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **SHORT kurulumu:** Üst yön: 1D RSI14 30–50 aralığında. Kurulum: 4H BB squeeze sonrası üst bant kapanışı. 1H giriş tetiği: son 5 bar dibinde kapanış ve hacim z≥0.5. Tüm üst TF değerleri son kapanmış mumdan alınır.
- **Emir/giriş (LONG):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Emir/giriş (SHORT):** 1H tetik kapanışından sonraki 1H açılışı. 4H/1D mum kapanmadan onların geçici değerleri kullanılmaz.
- **Stop ve boyut (LONG):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Stop ve boyut (SHORT):** 1H giriş yapısının 0.15 ATR(1H) ötesi; ayrıca 4H stop mesafesi 3×1H ATR'den yakınsa daha uzak 4H yapı stopu seçilir ve boyut küçültülür.
- **Çıkış (LONG):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **Çıkış (SHORT):** 1H'de 1R kısmi; 4H hedef seviyesinde 2R–3R; 4H kurulum tersine dönünce kalan çıkış. 1D bias tersine dönerse tüm pozisyon kapanır.
- **İşlem yok / geçersiz:** 1D ve 4H yönleri zıt, 1H tetik 1D majör seviyeye <1R mesafede veya HTF veri henüz kapanmamışsa yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V18](#v18) [V20](#v20) [V47](#v47) [D18](#d18)


# Volatilite rejimi

## 181 — Volatilite taktiği — ATR14/Close son 100 bar %25 persentil altından yukarı çıkar + EMA50 eğimi ve fiyat aynı yönde

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** ATR14/Close son 100 bar %25 persentil altından yukarı çıkar; EMA50 eğimi ve fiyat aynı yönde; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Volatilite olayı: ATR14/Close son 100 bar %25 persentil altından yukarı çıkar. Yön filtresi: EMA50 eğimi ve fiyat aynı yönde. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: ATR14/Close son 100 bar %25 persentil altından yukarı çıkar. Yön filtresi: EMA50 eğimi ve fiyat aynı yönde. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 182 — Volatilite taktiği — BB width KC width'ün altından üstüne geçer (squeeze release) + EMA50 eğimi ve fiyat aynı yönde

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** BB width KC width'ün altından üstüne geçer (squeeze release); EMA50 eğimi ve fiyat aynı yönde; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Volatilite olayı: BB width KC width'ün altından üstüne geçer (squeeze release). Yön filtresi: EMA50 eğimi ve fiyat aynı yönde. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: BB width KC width'ün altından üstüne geçer (squeeze release). Yön filtresi: EMA50 eğimi ve fiyat aynı yönde. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 183 — Volatilite taktiği — NR7: mevcut bar son 7 barın en dar aralığı + EMA50 eğimi ve fiyat aynı yönde

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** NR7: mevcut bar son 7 barın en dar aralığı; sonraki bar tepe kırar; EMA50 eğimi ve fiyat aynı yönde; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Volatilite olayı: NR7: mevcut bar son 7 barın en dar aralığı; sonraki bar tepe kırar. Yön filtresi: EMA50 eğimi ve fiyat aynı yönde. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: NR7: mevcut bar son 7 barın en dar aralığı; sonraki bar tepe kırar. Yön filtresi: EMA50 eğimi ve fiyat aynı yönde. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 184 — Volatilite taktiği — inside-bar serisi ≥2 + EMA50 eğimi ve fiyat aynı yönde

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** inside-bar serisi ≥2; mother-bar tepe kırılır; EMA50 eğimi ve fiyat aynı yönde; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Volatilite olayı: inside-bar serisi ≥2; mother-bar tepe kırılır. Yön filtresi: EMA50 eğimi ve fiyat aynı yönde. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: inside-bar serisi ≥2; mother-bar tepe kırılır. Yön filtresi: EMA50 eğimi ve fiyat aynı yönde. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 185 — Volatilite taktiği — ATR14 son 20 bar ortalamasının 1.5 katına çıkar + EMA50 eğimi ve fiyat aynı yönde

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** ATR14 son 20 bar ortalamasının 1.5 katına çıkar; EMA50 eğimi ve fiyat aynı yönde; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Volatilite olayı: ATR14 son 20 bar ortalamasının 1.5 katına çıkar. Yön filtresi: EMA50 eğimi ve fiyat aynı yönde. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: ATR14 son 20 bar ortalamasının 1.5 katına çıkar. Yön filtresi: EMA50 eğimi ve fiyat aynı yönde. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 186 — Volatilite taktiği — ATR14/Close son 100 bar %25 persentil altından yukarı çıkar + MACD sıfır çizgisi yönü ve RSI50 tarafı aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** ATR14/Close son 100 bar %25 persentil altından yukarı çıkar; MACD sıfır çizgisi yönü ve RSI50 tarafı aynı; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Volatilite olayı: ATR14/Close son 100 bar %25 persentil altından yukarı çıkar. Yön filtresi: MACD sıfır çizgisi yönü ve RSI50 tarafı aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: ATR14/Close son 100 bar %25 persentil altından yukarı çıkar. Yön filtresi: MACD sıfır çizgisi yönü ve RSI50 tarafı aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 187 — Volatilite taktiği — BB width KC width'ün altından üstüne geçer (squeeze release) + MACD sıfır çizgisi yönü ve RSI50 tarafı aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** BB width KC width'ün altından üstüne geçer (squeeze release); MACD sıfır çizgisi yönü ve RSI50 tarafı aynı; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Volatilite olayı: BB width KC width'ün altından üstüne geçer (squeeze release). Yön filtresi: MACD sıfır çizgisi yönü ve RSI50 tarafı aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: BB width KC width'ün altından üstüne geçer (squeeze release). Yön filtresi: MACD sıfır çizgisi yönü ve RSI50 tarafı aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 188 — Volatilite taktiği — NR7: mevcut bar son 7 barın en dar aralığı + MACD sıfır çizgisi yönü ve RSI50 tarafı aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** NR7: mevcut bar son 7 barın en dar aralığı; sonraki bar tepe kırar; MACD sıfır çizgisi yönü ve RSI50 tarafı aynı; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Volatilite olayı: NR7: mevcut bar son 7 barın en dar aralığı; sonraki bar tepe kırar. Yön filtresi: MACD sıfır çizgisi yönü ve RSI50 tarafı aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: NR7: mevcut bar son 7 barın en dar aralığı; sonraki bar tepe kırar. Yön filtresi: MACD sıfır çizgisi yönü ve RSI50 tarafı aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 189 — Volatilite taktiği — inside-bar serisi ≥2 + MACD sıfır çizgisi yönü ve RSI50 tarafı aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** inside-bar serisi ≥2; mother-bar tepe kırılır; MACD sıfır çizgisi yönü ve RSI50 tarafı aynı; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Volatilite olayı: inside-bar serisi ≥2; mother-bar tepe kırılır. Yön filtresi: MACD sıfır çizgisi yönü ve RSI50 tarafı aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: inside-bar serisi ≥2; mother-bar tepe kırılır. Yön filtresi: MACD sıfır çizgisi yönü ve RSI50 tarafı aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 190 — Volatilite taktiği — ATR14 son 20 bar ortalamasının 1.5 katına çıkar + MACD sıfır çizgisi yönü ve RSI50 tarafı aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** ATR14 son 20 bar ortalamasının 1.5 katına çıkar; MACD sıfır çizgisi yönü ve RSI50 tarafı aynı; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Volatilite olayı: ATR14 son 20 bar ortalamasının 1.5 katına çıkar. Yön filtresi: MACD sıfır çizgisi yönü ve RSI50 tarafı aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: ATR14 son 20 bar ortalamasının 1.5 katına çıkar. Yön filtresi: MACD sıfır çizgisi yönü ve RSI50 tarafı aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 191 — Volatilite taktiği — ATR14/Close son 100 bar %25 persentil altından yukarı çıkar + Donchian20 yönü ve OBV kırılımı aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** ATR14/Close son 100 bar %25 persentil altından yukarı çıkar; Donchian20 yönü ve OBV kırılımı aynı; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Volatilite olayı: ATR14/Close son 100 bar %25 persentil altından yukarı çıkar. Yön filtresi: Donchian20 yönü ve OBV kırılımı aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: ATR14/Close son 100 bar %25 persentil altından yukarı çıkar. Yön filtresi: Donchian20 yönü ve OBV kırılımı aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 192 — Volatilite taktiği — BB width KC width'ün altından üstüne geçer (squeeze release) + Donchian20 yönü ve OBV kırılımı aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** BB width KC width'ün altından üstüne geçer (squeeze release); Donchian20 yönü ve OBV kırılımı aynı; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Volatilite olayı: BB width KC width'ün altından üstüne geçer (squeeze release). Yön filtresi: Donchian20 yönü ve OBV kırılımı aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: BB width KC width'ün altından üstüne geçer (squeeze release). Yön filtresi: Donchian20 yönü ve OBV kırılımı aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 193 — Volatilite taktiği — NR7: mevcut bar son 7 barın en dar aralığı + Donchian20 yönü ve OBV kırılımı aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** NR7: mevcut bar son 7 barın en dar aralığı; sonraki bar tepe kırar; Donchian20 yönü ve OBV kırılımı aynı; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Volatilite olayı: NR7: mevcut bar son 7 barın en dar aralığı; sonraki bar tepe kırar. Yön filtresi: Donchian20 yönü ve OBV kırılımı aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: NR7: mevcut bar son 7 barın en dar aralığı; sonraki bar tepe kırar. Yön filtresi: Donchian20 yönü ve OBV kırılımı aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 194 — Volatilite taktiği — inside-bar serisi ≥2 + Donchian20 yönü ve OBV kırılımı aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** inside-bar serisi ≥2; mother-bar tepe kırılır; Donchian20 yönü ve OBV kırılımı aynı; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Volatilite olayı: inside-bar serisi ≥2; mother-bar tepe kırılır. Yön filtresi: Donchian20 yönü ve OBV kırılımı aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: inside-bar serisi ≥2; mother-bar tepe kırılır. Yön filtresi: Donchian20 yönü ve OBV kırılımı aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 195 — Volatilite taktiği — ATR14 son 20 bar ortalamasının 1.5 katına çıkar + Donchian20 yönü ve OBV kırılımı aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** ATR14 son 20 bar ortalamasının 1.5 katına çıkar; Donchian20 yönü ve OBV kırılımı aynı; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Volatilite olayı: ATR14 son 20 bar ortalamasının 1.5 katına çıkar. Yön filtresi: Donchian20 yönü ve OBV kırılımı aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: ATR14 son 20 bar ortalamasının 1.5 katına çıkar. Yön filtresi: Donchian20 yönü ve OBV kırılımı aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 196 — Volatilite taktiği — ATR14/Close son 100 bar %25 persentil altından yukarı çıkar + ADX≥20 ve DI yönü kırılımla aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** ATR14/Close son 100 bar %25 persentil altından yukarı çıkar; ADX≥20 ve DI yönü kırılımla aynı; ATR
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Volatilite olayı: ATR14/Close son 100 bar %25 persentil altından yukarı çıkar. Yön filtresi: ADX≥20 ve DI yönü kırılımla aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: ATR14/Close son 100 bar %25 persentil altından yukarı çıkar. Yön filtresi: ADX≥20 ve DI yönü kırılımla aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 197 — Volatilite taktiği — BB width KC width'ün altından üstüne geçer (squeeze release) + ADX≥20 ve DI yönü kırılımla aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** BB width KC width'ün altından üstüne geçer (squeeze release); ADX≥20 ve DI yönü kırılımla aynı; ATR
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Volatilite olayı: BB width KC width'ün altından üstüne geçer (squeeze release). Yön filtresi: ADX≥20 ve DI yönü kırılımla aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: BB width KC width'ün altından üstüne geçer (squeeze release). Yön filtresi: ADX≥20 ve DI yönü kırılımla aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 198 — Volatilite taktiği — NR7: mevcut bar son 7 barın en dar aralığı + ADX≥20 ve DI yönü kırılımla aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** NR7: mevcut bar son 7 barın en dar aralığı; sonraki bar tepe kırar; ADX≥20 ve DI yönü kırılımla aynı; ATR
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Volatilite olayı: NR7: mevcut bar son 7 barın en dar aralığı; sonraki bar tepe kırar. Yön filtresi: ADX≥20 ve DI yönü kırılımla aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: NR7: mevcut bar son 7 barın en dar aralığı; sonraki bar tepe kırar. Yön filtresi: ADX≥20 ve DI yönü kırılımla aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 199 — Volatilite taktiği — inside-bar serisi ≥2 + ADX≥20 ve DI yönü kırılımla aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** inside-bar serisi ≥2; mother-bar tepe kırılır; ADX≥20 ve DI yönü kırılımla aynı; ATR
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Volatilite olayı: inside-bar serisi ≥2; mother-bar tepe kırılır. Yön filtresi: ADX≥20 ve DI yönü kırılımla aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: inside-bar serisi ≥2; mother-bar tepe kırılır. Yön filtresi: ADX≥20 ve DI yönü kırılımla aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)

## 200 — Volatilite taktiği — ATR14 son 20 bar ortalamasının 1.5 katına çıkar + ADX≥20 ve DI yönü kırılımla aynı

- **Aile / rejim:** Volatilite rejimi — Sıkışma→genişleme veya şok sonrası normalleşme.
- **Bileşenler:** ATR14 son 20 bar ortalamasının 1.5 katına çıkar; ADX≥20 ve DI yönü kırılımla aynı; ATR
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Volatilite olayı: ATR14 son 20 bar ortalamasının 1.5 katına çıkar. Yön filtresi: ADX≥20 ve DI yönü kırılımla aynı. Long için olay barı/sonraki bar yukarı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **SHORT kurulumu:** Volatilite olayı: ATR14 son 20 bar ortalamasının 1.5 katına çıkar. Yön filtresi: ADX≥20 ve DI yönü kırılımla aynı. Long için olay barı/sonraki bar aşağı kırılım kapanışı üretmeli; wick-only kırılım sayılmaz.
- **Emir/giriş (LONG):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Emir/giriş (SHORT):** Kapanış teyitli kırılım; giriş bir sonraki açılış. Şok yöntemi (ATR 1.5×) için ilk bar kovalanmaz, 1–3 barlık daralma ve yeniden kırılım beklenir.
- **Stop ve boyut (LONG):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Stop ve boyut (SHORT):** Sıkışma kutusunun karşı tarafı veya 1.5 ATR; daha uzak olan. Stop >2.5 ATR ise pas.
- **Çıkış (LONG):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 altına inerse kalan kapanır.
- **Çıkış (SHORT):** İlk 2R; sonra Chandelier Exit(22,3ATR). 8 bar içinde +0.5R yoksa çık. Volatilite tekrar persentil 25 üstüne inerse kalan kapanır.
- **İşlem yok / geçersiz:** Aşırı geniş sinyal mumu (>3 ATR), düşük likidite veya spread >ATR'nin %5'i ise yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V04](#v04) [V08](#v08) [V39](#v39) [D03](#d03) [D05](#d05) [D06](#d06) [D07](#d07)


# Dörtlü hibrit

## 201 — 4'lü konfluens — EMA50>EMA200 / RSI14 52–68 / CMF20>0.05 / son 10 bar tepesinde kapanış

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** EMA50>EMA200; RSI14 52–68 ve yükseliyor; CMF20>0.05; son 10 bar tepesinde kapanış
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Dört rol aynı anda: trend=EMA50>EMA200; momentum=RSI14 52–68 ve yükseliyor; katılım=CMF20>0.05; tetik=son 10 bar tepesinde kapanış. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=EMA50<EMA200; momentum=RSI14 32–48 ve düşüyor; katılım=CMF20<-0.05; tetik=son 10 bar dibinde kapanış. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 202 — 4'lü konfluens — Supertrend(10,3) yukarı / RSI14 52–68 / hacim z≥0.8 / 4H direncin ilk retesti

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** Supertrend(10,3) yukarı; RSI14 52–68 ve yükseliyor; hacim z≥0.8; 4H direncin ilk retesti
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Dört rol aynı anda: trend=Supertrend(10,3) yukarı; momentum=RSI14 52–68 ve yükseliyor; katılım=hacim z≥0.8; tetik=4H direncin ilk retesti. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=Supertrend(10,3) aşağı; momentum=RSI14 32–48 ve düşüyor; katılım=hacim z≥0.8; tetik=4H direncin ilk retesti. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 203 — 4'lü konfluens — Ichimoku fiyat bulut üstünde / RSI14 52–68 / AVWAP üstünde kapanış / BB squeeze üst kırılımı

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** Ichimoku fiyat bulut üstünde; RSI14 52–68 ve yükseliyor; AVWAP üstünde kapanış; BB squeeze üst kırılımı
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Dört rol aynı anda: trend=Ichimoku fiyat bulut üstünde; momentum=RSI14 52–68 ve yükseliyor; katılım=AVWAP üstünde kapanış; tetik=BB squeeze üst kırılımı. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=Ichimoku fiyat bulut altında; momentum=RSI14 32–48 ve düşüyor; katılım=AVWAP altında kapanış; tetik=BB squeeze alt kırılımı. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 204 — 4'lü konfluens — EMA20>EMA50 ve ikisi yükseliyor / RSI14 52–68 / OBV son 20 bar tepesinde / EMA20 retestinden bullish engulfing

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** EMA20>EMA50 ve ikisi yükseliyor; RSI14 52–68 ve yükseliyor; OBV son 20 bar tepesinde; EMA20 retestinden bullish engulfing
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Dört rol aynı anda: trend=EMA20>EMA50 ve ikisi yükseliyor; momentum=RSI14 52–68 ve yükseliyor; katılım=OBV son 20 bar tepesinde; tetik=EMA20 retestinden bullish engulfing. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=EMA20<EMA50 ve ikisi düşüyor; momentum=RSI14 32–48 ve düşüyor; katılım=OBV son 20 bar tepesinde; tetik=EMA20 retestinden bearish engulfing. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 205 — 4'lü konfluens — Donchian20 orta çizgisi yükseliyor / RSI14 52–68 / MFI14>50 / son 10 bar tepesinde kapanış

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** Donchian20 orta çizgisi yükseliyor; RSI14 52–68 ve yükseliyor; MFI14>50 ve hacim medyan üstü; son 10 bar tepesinde kapanış
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Dört rol aynı anda: trend=Donchian20 orta çizgisi yükseliyor; momentum=RSI14 52–68 ve yükseliyor; katılım=MFI14>50 ve hacim medyan üstü; tetik=son 10 bar tepesinde kapanış. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=Donchian20 orta çizgisi düşüyor; momentum=RSI14 32–48 ve düşüyor; katılım=MFI14<50 ve hacim medyan üstü; tetik=son 10 bar dibinde kapanış. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 206 — 4'lü konfluens — EMA50>EMA200 / MACD histogramı >0 / CMF20>0.05 / 4H direncin ilk retesti

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** EMA50>EMA200; MACD histogramı >0 ve artıyor; CMF20>0.05; 4H direncin ilk retesti
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Dört rol aynı anda: trend=EMA50>EMA200; momentum=MACD histogramı >0 ve artıyor; katılım=CMF20>0.05; tetik=4H direncin ilk retesti. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=EMA50<EMA200; momentum=MACD histogramı <0 ve azalıyor; katılım=CMF20<-0.05; tetik=4H direncin ilk retesti. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 207 — 4'lü konfluens — Supertrend(10,3) yukarı / MACD histogramı >0 / hacim z≥0.8 / BB squeeze üst kırılımı

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** Supertrend(10,3) yukarı; MACD histogramı >0 ve artıyor; hacim z≥0.8; BB squeeze üst kırılımı
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Dört rol aynı anda: trend=Supertrend(10,3) yukarı; momentum=MACD histogramı >0 ve artıyor; katılım=hacim z≥0.8; tetik=BB squeeze üst kırılımı. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=Supertrend(10,3) aşağı; momentum=MACD histogramı <0 ve azalıyor; katılım=hacim z≥0.8; tetik=BB squeeze alt kırılımı. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 208 — 4'lü konfluens — Ichimoku fiyat bulut üstünde / MACD histogramı >0 / AVWAP üstünde kapanış / EMA20 retestinden bullish engulfing

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** Ichimoku fiyat bulut üstünde; MACD histogramı >0 ve artıyor; AVWAP üstünde kapanış; EMA20 retestinden bullish engulfing
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Dört rol aynı anda: trend=Ichimoku fiyat bulut üstünde; momentum=MACD histogramı >0 ve artıyor; katılım=AVWAP üstünde kapanış; tetik=EMA20 retestinden bullish engulfing. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=Ichimoku fiyat bulut altında; momentum=MACD histogramı <0 ve azalıyor; katılım=AVWAP altında kapanış; tetik=EMA20 retestinden bearish engulfing. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 209 — 4'lü konfluens — EMA20>EMA50 ve ikisi yükseliyor / MACD histogramı >0 / OBV son 20 bar tepesinde / son 10 bar tepesinde kapanış

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** EMA20>EMA50 ve ikisi yükseliyor; MACD histogramı >0 ve artıyor; OBV son 20 bar tepesinde; son 10 bar tepesinde kapanış
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Dört rol aynı anda: trend=EMA20>EMA50 ve ikisi yükseliyor; momentum=MACD histogramı >0 ve artıyor; katılım=OBV son 20 bar tepesinde; tetik=son 10 bar tepesinde kapanış. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=EMA20<EMA50 ve ikisi düşüyor; momentum=MACD histogramı <0 ve azalıyor; katılım=OBV son 20 bar tepesinde; tetik=son 10 bar dibinde kapanış. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 210 — 4'lü konfluens — Donchian20 orta çizgisi yükseliyor / MACD histogramı >0 / MFI14>50 / 4H direncin ilk retesti

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** Donchian20 orta çizgisi yükseliyor; MACD histogramı >0 ve artıyor; MFI14>50 ve hacim medyan üstü; 4H direncin ilk retesti
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Dört rol aynı anda: trend=Donchian20 orta çizgisi yükseliyor; momentum=MACD histogramı >0 ve artıyor; katılım=MFI14>50 ve hacim medyan üstü; tetik=4H direncin ilk retesti. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=Donchian20 orta çizgisi düşüyor; momentum=MACD histogramı <0 ve azalıyor; katılım=MFI14<50 ve hacim medyan üstü; tetik=4H direncin ilk retesti. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 211 — 4'lü konfluens — EMA50>EMA200 / Stoch %K>%D / CMF20>0.05 / BB squeeze üst kırılımı

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** EMA50>EMA200; Stoch %K>%D ve 40–80; CMF20>0.05; BB squeeze üst kırılımı
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Dört rol aynı anda: trend=EMA50>EMA200; momentum=Stoch %K>%D ve 40–80; katılım=CMF20>0.05; tetik=BB squeeze üst kırılımı. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=EMA50<EMA200; momentum=Stoch %K>%D ve 40–80; katılım=CMF20<-0.05; tetik=BB squeeze alt kırılımı. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 212 — 4'lü konfluens — Supertrend(10,3) yukarı / Stoch %K>%D / hacim z≥0.8 / EMA20 retestinden bullish engulfing

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** Supertrend(10,3) yukarı; Stoch %K>%D ve 40–80; hacim z≥0.8; EMA20 retestinden bullish engulfing
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Dört rol aynı anda: trend=Supertrend(10,3) yukarı; momentum=Stoch %K>%D ve 40–80; katılım=hacim z≥0.8; tetik=EMA20 retestinden bullish engulfing. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=Supertrend(10,3) aşağı; momentum=Stoch %K>%D ve 40–80; katılım=hacim z≥0.8; tetik=EMA20 retestinden bearish engulfing. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 213 — 4'lü konfluens — Ichimoku fiyat bulut üstünde / Stoch %K>%D / AVWAP üstünde kapanış / son 10 bar tepesinde kapanış

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** Ichimoku fiyat bulut üstünde; Stoch %K>%D ve 40–80; AVWAP üstünde kapanış; son 10 bar tepesinde kapanış
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Dört rol aynı anda: trend=Ichimoku fiyat bulut üstünde; momentum=Stoch %K>%D ve 40–80; katılım=AVWAP üstünde kapanış; tetik=son 10 bar tepesinde kapanış. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=Ichimoku fiyat bulut altında; momentum=Stoch %K>%D ve 40–80; katılım=AVWAP altında kapanış; tetik=son 10 bar dibinde kapanış. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 214 — 4'lü konfluens — EMA20>EMA50 ve ikisi yükseliyor / Stoch %K>%D / OBV son 20 bar tepesinde / 4H direncin ilk retesti

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** EMA20>EMA50 ve ikisi yükseliyor; Stoch %K>%D ve 40–80; OBV son 20 bar tepesinde; 4H direncin ilk retesti
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Dört rol aynı anda: trend=EMA20>EMA50 ve ikisi yükseliyor; momentum=Stoch %K>%D ve 40–80; katılım=OBV son 20 bar tepesinde; tetik=4H direncin ilk retesti. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=EMA20<EMA50 ve ikisi düşüyor; momentum=Stoch %K>%D ve 40–80; katılım=OBV son 20 bar tepesinde; tetik=4H direncin ilk retesti. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 215 — 4'lü konfluens — Donchian20 orta çizgisi yükseliyor / Stoch %K>%D / MFI14>50 / BB squeeze üst kırılımı

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** Donchian20 orta çizgisi yükseliyor; Stoch %K>%D ve 40–80; MFI14>50 ve hacim medyan üstü; BB squeeze üst kırılımı
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Dört rol aynı anda: trend=Donchian20 orta çizgisi yükseliyor; momentum=Stoch %K>%D ve 40–80; katılım=MFI14>50 ve hacim medyan üstü; tetik=BB squeeze üst kırılımı. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=Donchian20 orta çizgisi düşüyor; momentum=Stoch %K>%D ve 40–80; katılım=MFI14<50 ve hacim medyan üstü; tetik=BB squeeze alt kırılımı. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 216 — 4'lü konfluens — EMA50>EMA200 / MFI14>55 / CMF20>0.05 / EMA20 retestinden bullish engulfing

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** EMA50>EMA200; MFI14>55; CMF20>0.05; EMA20 retestinden bullish engulfing
- **TF parametre notu:** 1H: ATR14, ana bakış 4H EMA50; 4H: ATR14, ana bakış 1D EMA50; 1D: ATR20, ana bakış 1W EMA20. Diğer periyotlar yöntemde yazıldığı gibidir.
- **LONG kurulumu:** Dört rol aynı anda: trend=EMA50>EMA200; momentum=MFI14>55; katılım=CMF20>0.05; tetik=EMA20 retestinden bullish engulfing. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=EMA50<EMA200; momentum=MFI14<45; katılım=CMF20<-0.05; tetik=EMA20 retestinden bearish engulfing. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 217 — 4'lü konfluens — Supertrend(10,3) yukarı / MFI14>55 / hacim z≥0.8 / son 10 bar tepesinde kapanış

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** Supertrend(10,3) yukarı; MFI14>55; hacim z≥0.8; son 10 bar tepesinde kapanış
- **TF parametre notu:** 1H/4H: RSI14, ADX14, ATR14; 1D: RSI14, ADX14, ATR20. 1H'de hacim eşiği z≥1.0, 4H/1D'de z≥0.7.
- **LONG kurulumu:** Dört rol aynı anda: trend=Supertrend(10,3) yukarı; momentum=MFI14>55; katılım=hacim z≥0.8; tetik=son 10 bar tepesinde kapanış. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=Supertrend(10,3) aşağı; momentum=MFI14<45; katılım=hacim z≥0.8; tetik=son 10 bar dibinde kapanış. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 218 — 4'lü konfluens — Ichimoku fiyat bulut üstünde / MFI14>55 / AVWAP üstünde kapanış / 4H direncin ilk retesti

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** Ichimoku fiyat bulut üstünde; MFI14>55; AVWAP üstünde kapanış; 4H direncin ilk retesti
- **TF parametre notu:** 1H: yapı pivotu L=3/R=3; 4H: L=3/R=3; 1D: L=2/R=2. Pivot ancak sağdaki R mum kapandıktan sonra kesinleşir.
- **LONG kurulumu:** Dört rol aynı anda: trend=Ichimoku fiyat bulut üstünde; momentum=MFI14>55; katılım=AVWAP üstünde kapanış; tetik=4H direncin ilk retesti. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=Ichimoku fiyat bulut altında; momentum=MFI14<45; katılım=AVWAP altında kapanış; tetik=4H direncin ilk retesti. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 219 — 4'lü konfluens — EMA20>EMA50 ve ikisi yükseliyor / MFI14>55 / OBV son 20 bar tepesinde / BB squeeze üst kırılımı

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** EMA20>EMA50 ve ikisi yükseliyor; MFI14>55; OBV son 20 bar tepesinde; BB squeeze üst kırılımı
- **TF parametre notu:** 1H: kanal 20, trend EMA100; 4H: kanal 20, trend EMA50; 1D: kanal 55, trend EMA100. ATR14 tümünde.
- **LONG kurulumu:** Dört rol aynı anda: trend=EMA20>EMA50 ve ikisi yükseliyor; momentum=MFI14>55; katılım=OBV son 20 bar tepesinde; tetik=BB squeeze üst kırılımı. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=EMA20<EMA50 ve ikisi düşüyor; momentum=MFI14<45; katılım=OBV son 20 bar tepesinde; tetik=BB squeeze alt kırılımı. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

## 220 — 4'lü konfluens — Donchian20 orta çizgisi yükseliyor / MFI14>55 / MFI14>50 / EMA20 retestinden bullish engulfing

- **Aile / rejim:** Dörtlü hibrit — Seçici trend/kırılım; az sinyal, yüksek konfluens hedefi.
- **Bileşenler:** Donchian20 orta çizgisi yükseliyor; MFI14>55; MFI14>50 ve hacim medyan üstü; EMA20 retestinden bullish engulfing
- **TF parametre notu:** Tüm TF'lerde taban ayar aynıdır; 1H, 4H ve 1D ayrı ayrı optimize edilir. Bir TF'de bulunan parametre diğerine taşınmaz.
- **LONG kurulumu:** Dört rol aynı anda: trend=Donchian20 orta çizgisi yükseliyor; momentum=MFI14>55; katılım=MFI14>50 ve hacim medyan üstü; tetik=EMA20 retestinden bullish engulfing. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **SHORT kurulumu:** Dört rol aynı anda: trend=Donchian20 orta çizgisi düşüyor; momentum=MFI14<45; katılım=MFI14<50 ve hacim medyan üstü; tetik=EMA20 retestinden bearish engulfing. Dört koşul da aynı kapanışta doğru veya ilk üç koşul son 3 bar içinde kesintisiz doğru olmalı.
- **Emir/giriş (LONG):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Emir/giriş (SHORT):** Tetik kapanışından sonraki açılış. Dört koşuldan biri giriş anında bozulmuşsa emir iptal.
- **Stop ve boyut (LONG):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Stop ve boyut (SHORT):** Tetik yapısının 0.2 ATR ötesi ve en az 1.2 ATR. Risk %0.40; korelasyonlu coinlerde toplam açık risk %1.5'i geçmez.
- **Çıkış (LONG):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **Çıkış (SHORT):** 1R'de %25; 2R'de %35; kalan trend filtresi tersine dönene kadar 2 ATR Chandelier ile. Momentum ve hacim aynı bar tersine dönerse erken çık.
- **İşlem yok / geçersiz:** Dört indikatörden ikisi aynı bilgiyi kopyalıyorsa (ör. RSI+Stoch aşırı benzer) varyant ayrı test edilir; likidite/volume eksikse yok.
- **Kod mantığı:** `if flat and regime_ok and setup and trigger_on_close: size=risk_budget/abs(entry-stop); enter_next_open(); manage_R_targets_and_trail()`
- **Araştırma izi:** [V01](#v01) [V03](#v03) [V32](#v32) [V47](#v47) [V49](#v49) [D01](#d01) [D02](#d02) [D04](#d04) [D08](#d08)

---

# Kaynaklar ve araştırma izi
## YouTube/transkript taraması (50 video)
Bu listedeki transkript/özet sayfalarından kural özü çıkarılmış, ancak performans iddiaları doğru kabul edilmemiştir. Telif nedeniyle transkriptler kopyalanmamış; yalnızca algoritmaya çevrilen fikir özeti verilmiştir.
- <a id="v01"></a> **V01 — [EMA + RSI + ADX](https://glasp.co/youtube/p/scalping-trading-was-impossible-until-i-found-how-to-combine-ema-rsi-adx-indicators-full-strategy):** EMA yön, RSI tetik, ADX güç filtresi.
- <a id="v02"></a> **V02 — [EMA foundation + RSI/Stochastic](https://glasp.co/youtube/wf6s7HHUP_8):** varlığa göre EMA testi ve katmanlı EMA destekleri.
- <a id="v03"></a> **V03 — [EMA + CCI + MACD](https://glasp.co/youtube/_Wr57vS9ADM):** EMA yön, CCI sapma, MACD teyidi.
- <a id="v04"></a> **V04 — [Bollinger Bands systems](https://glasp.co/youtube/p/bollinger-bands-strategies-that-actually-work-trading-systems-with-bb-indicator):** range, trend pullback ve squeeze ayrımı.
- <a id="v05"></a> **V05 — [Break and retest](https://glasp.co/youtube/qsawJuLmJEM):** ilk retest, hacim ve mum teyidi.
- <a id="v06"></a> **V06 — [Break and retest pattern](https://glasp.co/youtube/kg-rOo9_xjU):** bölge kırılımı, retest, engulfing, en az 2R.
- <a id="v07"></a> **V07 — [Ichimoku swing framework](https://glasp.co/youtube/M0flnBqjVzU):** bulut dışı yön, Chikou teyidi, bulut içinde işlem yok.
- <a id="v08"></a> **V08 — [Donchian breakout](https://glasp.co/youtube/r7gzyEnPTwg):** kanal kırılımı ve trend takip.
- <a id="v09"></a> **V09 — [Liquidity + market structure](https://glasp.co/youtube/JhBX0TQ41H8):** swing likiditesi, sweep, BOS ve düzeltme.
- <a id="v10"></a> **V10 — [Engulfing pin bar](https://glasp.co/youtube/p/you-ll-never-trade-price-action-the-same-way-again-easiest-trading-strategy):** engulfing gövde + uzun fitil reddi.
- <a id="v11"></a> **V11 — [Moving-average crossover practice](https://glasp.co/youtube/yPbUn3Wuh98):** yüksek zaman dilimi ve gürültü filtresi.
- <a id="v12"></a> **V12 — [Fibonacci pivot points](https://glasp.co/youtube/p/trading-with-fibonacci-pivot-points-made-easy-forex-stock-market-strategy-for-beginners):** pivot bias ve Fibonacci destek/direnç.
- <a id="v13"></a> **V13 — [20/50 MA crossover](https://glasp.co/youtube/r7jIc5hZoxU):** 20/50 kesişimi, yanlış sinyal filtresi.
- <a id="v14"></a> **V14 — [Pin bar + inside bar](https://glasp.co/youtube/p/you-won-t-believe-the-power-of-this-strategy-1-price-action-candlestick-trading-system):** reddin ardından sıkışma ve yönlü kırılım.
- <a id="v15"></a> **V15 — [Engulfing with trend](https://glasp.co/youtube/p/an-incredibly-easy-strategy-to-trade-price-action-using-engulfing-candlestick-pattern):** trend ve destek/direnç bağlamında engulfing.
- <a id="v16"></a> **V16 — [Supply-demand + FVG + pivot](https://glasp.co/youtube/z3TBWjnHRqg):** fresh bölge, boşluk ve pivot birleşimi.
- <a id="v17"></a> **V17 — [Scale into winners](https://glasp.co/youtube/iu0l8wdwDfg):** kazanana ekleme ve toplam risk sınırı.
- <a id="v18"></a> **V18 — [1H/4H key levels](https://glasp.co/youtube/N7SM8a7Dc9s):** 1H/4H yüksek-düşük seviyeleri ve hedefleme.
- <a id="v19"></a> **V19 — [Multi-method technical strategy](https://glasp.co/youtube/ZX-Tp4zgJYc):** Fibonacci, breakout, momentum ve hacim.
- <a id="v20"></a> **V20 — [Top-down strategy catalog](https://glasp.co/youtube/hJyYxKtys04):** üst zaman yönü, yapı, retest ve EMA.
- <a id="v21"></a> **V21 — [Candlestick context](https://glasp.co/youtube/LbP8o1Tf1Sg):** pin/engulfing/star formasyonlarını seviyede kullanma.
- <a id="v22"></a> **V22 — [High-volume pin bar](https://glasp.co/youtube/oc866aQoYcM):** trend EMA'sı ile yüksek hacimli pin bar.
- <a id="v23"></a> **V23 — [Fibonacci + market structure](https://glasp.co/youtube/L-ReMHiavPM):** swing tabanlı retracement ve yapı.
- <a id="v24"></a> **V24 — [20 and 200 moving averages](https://glasp.co/youtube/gddYspvW0_w):** eğim, dokunuş, düzeltme ve konsolidasyon.
- <a id="v25"></a> **V25 — [Pin bar execution](https://glasp.co/youtube/p/trading-price-action-using-pin-bars-best-forex-candlestick-reversal-pattern):** önceki hareket + fitil reddi + yapı stopu.
- <a id="v26"></a> **V26 — [Volume profile](https://glasp.co/youtube/qihraSSdI_M):** POC, değer alanı ve kabul/ret.
- <a id="v27"></a> **V27 — [Price-action confluence](https://glasp.co/youtube/8VxVkNoSIuE):** seviye + engulfing/pin bar teyidi.
- <a id="v28"></a> **V28 — [Moving average + Fibonacci](https://glasp.co/youtube/p/my-incredibly-easy-trading-strategy-made-me-31k-this-month):** trend ortalaması ve düzeltme bölgesi.
- <a id="v29"></a> **V29 — [Pivot point strategy](https://glasp.co/youtube/WQ8hdLQtzzQ):** merkez pivot ve yönsel seviyeler.
- <a id="v30"></a> **V30 — [Fibonacci extensions](https://glasp.co/youtube/vBJgPXW1nAM):** yapıdan hedef üretme.
- <a id="v31"></a> **V31 — [Hidden divergence + Fibonacci](https://glasp.co/youtube/p/a-leading-trading-strategy-to-predict-future-price-swings):** gizli uyumsuzluk ile trend devamı.
- <a id="v32"></a> **V32 — [Anchored VWAP toolkit](https://glasp.co/youtube/1zg2fctwsgU):** AVWAP, pivot, ADX ve yapı birleşimi.
- <a id="v33"></a> **V33 — [SMA crossover backtest](https://glasp.co/youtube/kEJiGT-ZS1w):** 50/200 günlük kesişim ve otomasyon.
- <a id="v34"></a> **V34 — [Supply-demand + pin/inside](https://glasp.co/youtube/3wvnpLXs2zE):** bölge içinde pin-inside tetikleyici.
- <a id="v35"></a> **V35 — [Buy weakness above EMA50](https://glasp.co/youtube/nDlm1wypn68):** EMA50 üstünde zayıflığı alma / altında gücü satma.
- <a id="v36"></a> **V36 — [Candlesticks need context](https://glasp.co/youtube/wIeYqqXcgtU):** mumun tek başına değil lokasyonla kullanılması.
- <a id="v37"></a> **V37 — [MA spacing and momentum](https://glasp.co/youtube/7lXm5obeMOc):** ortalama açılması, eğim ve trend kalitesi.
- <a id="v38"></a> **V38 — [Moving-average continuation](https://glasp.co/youtube/p/lost-a-lot-of-money-trading-moving-averages-here-are-my-best-tips):** EMA aralığı ve küçük pullback devamı.
- <a id="v39"></a> **V39 — [Volume-led breakout](https://glasp.co/youtube/nffM_kEHWd0):** yüksek hacimli dönem ve kurumsal katılım.
- <a id="v40"></a> **V40 — [Volume profile full tutorial](https://glasp.co/youtube/AmvnhaAUk2g):** değer alanı, POC ve dağılım.
- <a id="v41"></a> **V41 — [Price-volume analysis](https://glasp.co/youtube/3zKGz6aTw64):** hacimle fade veya continuation rejimi.
- <a id="v42"></a> **V42 — [Orderflow + volume profile](https://glasp.co/youtube/cUTsoU-15Tc):** profil seviyesi + akış teyidi.
- <a id="v43"></a> **V43 — [SMC + order flow](https://glasp.co/youtube/jVomJTjmxL4):** yapı kırılımı ve hacim kümeleri.
- <a id="v44"></a> **V44 — [Volume profile playbook](https://glasp.co/youtube/Xe30nXrRxYg):** HVN/LVN, kabul ve reddetme.
- <a id="v45"></a> **V45 — [RSI divergence automation](https://glasp.co/youtube/8S6F1AahM0s):** pivot tabanlı, lookahead'siz RSI uyumsuzluğu.
- <a id="v46"></a> **V46 — [Double MACD divergence](https://glasp.co/youtube/p/trading-macd-divergences-like-professional-traders-forex-stocks-strategy):** fiyat yapısı + çift MACD uyumsuzluğu + trend çizgisi kırılımı.
- <a id="v47"></a> **V47 — [MACD three-system map](https://glasp.co/youtube/S2HaCa0b-bY):** sıfır çizgisi, divergence ve çoklu zaman teyidi.
- <a id="v48"></a> **V48 — [Chart patterns in context](https://glasp.co/youtube/pnG4k4AaHMo):** formasyon şekli yerine bağlam ve likidite.
- <a id="v49"></a> **V49 — [Stochastic/ADX/Fisher entries](https://glasp.co/youtube/tO1tQyDy090):** farklı bilgi taşıyan giriş araçları.
- <a id="v50"></a> **V50 — [Stochastic divergence at prior-day levels](https://glasp.co/youtube/p/i-regret-not-using-this-swing-trading-strategy-before):** 1H/4H önceki gün yüksek-düşük + stochastic divergence.

## Teknik/formül ve uygulama kaynakları
- <a id="d01"></a> **D01 — [TradingView RSI](https://www.tradingview.com/support/solutions/43000502338-relative-strength-index-rsi/)**
- <a id="d02"></a> **D02 — [TradingView MACD](https://www.tradingview.com/support/solutions/43000502344-moving-average-convergence-divergence-macd-indicator/)**
- <a id="d03"></a> **D03 — [TradingView ATR](https://www.tradingview.com/support/solutions/43000501823-average-true-range-atr/)**
- <a id="d04"></a> **D04 — [TradingView ADX](https://www.tradingview.com/support/solutions/43000589099-average-directional-index-adx/)**
- <a id="d05"></a> **D05 — [TradingView Bollinger Bands](https://www.tradingview.com/support/solutions/43000501840-bollinger-bands-bb/)**
- <a id="d06"></a> **D06 — [TradingView Keltner Channels](https://www.tradingview.com/support/solutions/43000502266-keltner-channels-kc/)**
- <a id="d07"></a> **D07 — [TradingView Donchian Channels](https://www.tradingview.com/support/solutions/43000502253-donchian-channels-dc/)**
- <a id="d08"></a> **D08 — [TradingView CMF](https://www.tradingview.com/support/solutions/43000501974-chaikin-money-flow-cmf/)**
- <a id="d09"></a> **D09 — [TradingView OBV](https://www.tradingview.com/support/solutions/43000502593-on-balance-volume-obv/)**
- <a id="d10"></a> **D10 — [TradingView Stochastic](https://www.tradingview.com/support/solutions/43000502332-stochastic-stoch/)**
- <a id="d11"></a> **D11 — [TradingView MFI](https://www.tradingview.com/support/solutions/43000502348-money-flow-mfi/)**
- <a id="d12"></a> **D12 — [TradingView VWAP](https://www.tradingview.com/support/solutions/43000502018-volume-weighted-average-price-vwap/)**
- <a id="d13"></a> **D13 — [TradingView Anchored VWAP](https://www.tradingview.com/support/solutions/43000669764-anchored-vwap-drawing-tool/)**
- <a id="d14"></a> **D14 — [TradingView Supertrend](https://www.tradingview.com/support/solutions/43000634738-supertrend/)**
- <a id="d15"></a> **D15 — [TradingView Ichimoku](https://www.tradingview.com/support/solutions/43000589152-ichimoku-cloud/)**
- <a id="d16"></a> **D16 — [TradingView order execution](https://www.tradingview.com/pine-script-docs/faq/strategies)**
- <a id="d17"></a> **D17 — [TradingView strategy costs](https://www.tradingview.com/support/solutions/43000628599-strategy-properties/)**
- <a id="d18"></a> **D18 — [TradingView lookahead](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/)**
- <a id="d19"></a> **D19 — [Binance public kline schema](https://github.com/binance/binance-public-data)**
- <a id="d20"></a> **D20 — [Whitebox RSI+ADX+EMA implementation](https://docs.whitebox.so/the-secret-mindset/rsi-adx-ema-strategy)**


## Uygulama sırası (öneri)

1. Önce `001–040` (trend pullback + breakout) ve `161–180` (MTF) ile temel bir benchmark oluştur.
2. Sonra `061–100` (mean reversion + divergence) yöntemlerini yalnız uygun rejimde test et.
3. Hacim kalitesi yeterliyse `121–140`; değilse bu aileyi kapat.
4. Dörtlü yöntemlerde sinyal sayısı azalacağı için sonuçları yalnız win rate ile değil expectancy ve drawdown ile değerlendir.
5. En iyi 10 yöntemi farklı coinler, farklı yıllar, spot/futures ve 2× maliyet altında yeniden doğrula.

## Minimum veri kolonları

`open_time, open, high, low, close, volume, close_time, quote_volume, trades, taker_buy_base, taker_buy_quote`. Temel yöntemler OHLCV ile çalışır; taker-buy tabanlı ileri filtreler için son üç kolon gerekir. Binance spot public kline şemasında bu alanlar sağlanır; 2025 sonrası spot timestamp birimi mikrosaniye olabildiği için ingest aşamasında otomatik birim tespiti yapılmalıdır.

## Son not

Bu katalog “hangi strateji kesin çalışır?” sorusunu cevaplamaz. Doğru kullanım, her yöntemi açık bir hipotez olarak test etmek; maliyet, likidite, rejim ve out-of-sample dayanıklılığı geçmeyeni elemek; kalanları skor motoruna bağımsız sinyal modülü olarak bağlamaktır.
