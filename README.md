# Birgivî Forty Hadith — AI Tools' Arabic Manuscript Recognition Benchmark

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20720244.svg)](https://doi.org/10.5281/zenodo.20720244)

*[English](#english) · [Türkçe](#türkçe)*

---

## English

This repository contains the **data and code** of the study *"Performance of
Popular Artificial Intelligence Tools in Recognizing Arabic Manuscripts: A
Comparative Analysis on the Example of the First Page of Birgivî's Forty Hadith
Treatise,"* released for reproducibility.

Five AI tools' transcription outputs for the first page of İmam Birgivî's
*al-Ahādīth al-Arbaʿūn* are compared against a human-made reference text and
evaluated at the character (CER) and word (WER) levels.

### Repository structure

```
birgivi-htr-benchmark/
├── README.md
├── LICENSE                         # code: MIT
├── CITATION.cff                    # citation metadata + Zenodo DOI
├── requirements.txt
├── data/
│   ├── LICENSE                     # data: CC BY 4.0
│   ├── reference/
│   │   └── birgivi_ilk_sayfa.txt   # reference transcription (ground truth)
│   ├── outputs/                    # tool outputs (hypothesis), extracted from docx
│   │   ├── gemini.txt
│   │   ├── claude_opus.txt
│   │   ├── copilot_thinkdeeper.txt
│   │   ├── chatgpt.txt
│   │   ├── perplexity_pro.txt
│   │   └── pretests/               # first attempts (9 Jan 2026), not compared
│   └── manuscript/                 # manuscript image (copyright note)
├── src/
│   ├── analyze.py                  # processes all tools → results/
│   ├── recitation_baseline.py      # recitation ceiling + diagnostic features
│   └── sensitivity.py              # whitespace/bracket checks, first attempts
└── results/
    ├── metrics.csv                 # single source of all reported numbers
    ├── recitation_baseline.csv
    ├── diagnostic_features.csv
    ├── sensitivity.csv
    ├── pretests.csv
    └── diff/                       # per-tool visual error report (HTML)
```

### Running

```bash
pip install -r requirements.txt
python src/analyze.py
```

The script produces `results/metrics.csv` and `results/diff/*.html`. All numbers
reported in the article are taken from this CSV; they are not typed by hand.

### Method

**Reference text.** `data/reference/birgivi_ilk_sayfa.txt` (682 characters, 124
words); identical to the canonical reference embedded in the study's original
analysis script.

**Normalization.** To avoid counting orthographic variants that do not change
meaning as errors, both texts are passed through:

1. Diacritics removed (U+064B–U+065F, U+0670).
2. Persian yeh (ی, U+06CC) → Arabic alef maksura (ى, U+0649).

Arabic dotted yeh (ي) is kept; kaf (ك/ک) and teh marbuta (ة) are not merged.
This rule set reproduces the numbers reported in the article.

**Metrics.** Character- and word-level `editops` are computed with
`python-Levenshtein`; deletions/insertions/substitutions are counted separately.
- Character accuracy = (1 − total_char_errors / total_chars) × 100
- Erroneous word count = deletions + insertions + substitutions

### Results (results/metrics.csv)

| Tool | CER accuracy | Char errors (del/ins/sub) | Word errors (del/ins/sub) |
|---|---|---|---|
| Google Gemini 3.0 Pro | 98.68% | 9 (5/0/4) | 8 (2/0/6) |
| Claude Opus 4.5 | 89.00% | 75 (26/40/9) | 23 (5/7/11) |
| Microsoft Copilot Think Deeper | 85.34% | 100 (29/10/61) | 50 (5/1/44) |
| ChatGPT 5.2 | 84.90% | 103 (53/2/48) | 49 (10/0/39) |
| Perplexity Pro | 83.58% | 112 (28/39/45) | 44 (5/7/32) |

All values are produced uniformly by `src/analyze.py` from the source texts in
`data/outputs/`.

> **Note — ChatGPT (corrected).** ChatGPT's docx output stores its line breaks
> as soft returns inside a single paragraph. In v1.0.0 these were dropped during
> text extraction, which glued the last word of each line to the first word of
> the next and produced 83.14% (115 errors). With the line breaks preserved, as
> for every other tool, the same output yields 84.90% (103 errors: 53/2/48;
> 49 word errors: 10/0/39). `data/outputs/chatgpt.txt` has been corrected
> accordingly; the earlier statement that 84.90% came "from a different ChatGPT
> output" was wrong.

> **Note — criteria box.** The "Başarı Kriterleri" box of the HTML reports now
> follows Holley (2009): Good 98-99%, Average 90-98%, Poor below 90%. The
> "%90 - %97" range and the correction-effort captions of v1.0.0, which are not
> in Holley, were removed. No score is affected.

### Recitation baseline

`src/recitation_baseline.py` asks whether the page could be scored highly by
reciting the well-known hadith texts from memory. A flawless recitation in
standard modern orthography reaches at most 94.13% character accuracy against
the diplomatic reference (88.86% without the manuscript-specific title line).
Diagnostic features per tool (hamza-bearing letters, `الصلوة`/`الصلاة`,
`أجزم`/`أجذم`, substituted variant wordings) are written to
`results/diagnostic_features.csv`.

### Sensitivity checks and first attempts

`src/sensitivity.py` reports how the scores change when line breaks are
collapsed and when the four square brackets marking interlinear additions are
ignored, and how many errors each tool made in the rubricated title line. With
whitespace collapsed the order of the last three tools changes (Copilot 87.22%,
Perplexity 86.49%, ChatGPT 85.17%), so their ranking should not be read as
definitive. The same script scores the first attempts of 9 January 2026
(`data/outputs/pretests/`: Claude Sonnet 4.5 78.01%, Copilot Smart 80.50%,
Perplexity standard search 23.46%, Google Vision), which were not used in the
comparison.

### How to cite

Özbek, Muhammed Sadık. (2026). *Birgivî Kırk Hadis Risalesi — Popüler YZ
Araçlarının Arapça El Yazması Tanıma Performansı (Veri ve Kod)* (v1.0.0)
[Data set]. Zenodo. https://doi.org/10.5281/zenodo.20720244

### License

- Code: MIT (see `LICENSE`)
- Data: CC BY 4.0 (see `data/LICENSE`)
- Manuscript image: belongs to the holding library/collection (see `data/manuscript/README.md`)

---

## Türkçe

Bu depo, "Popüler Yapay Zeka Araçlarının Arapça El Yazmalarını Tanıma
Performansı: Birgivî'nin Kırk Hadis Risalesi'nin İlk Sayfası Örneğinde
Karşılaştırmalı Bir Analiz" başlıklı çalışmanın **veri ve kodunu**
tekrarlanabilirlik ilkesi gereği içerir.

Beş YZ aracının, İmam Birgivî'nin *el-Ehâdîsü'l-Erbaûn* risalesinin ilk
sayfasına ait transkripsiyon çıktıları, insan eliyle hazırlanmış referans
metinle karşılaştırılarak karakter (CER) ve kelime (WER) düzeyinde değerlendirilir.

### Depo yapısı

Bk. yukarıdaki ağaç (dosya adları ortaktır).

### Çalıştırma

```bash
pip install -r requirements.txt
python src/analyze.py
```

Betik `results/metrics.csv` ve `results/diff/*.html` dosyalarını üretir.
Makalede raporlanan sayılar bu CSV dosyasından alınır; elle aktarılmaz.

### Yöntem

**Referans metin.** `data/reference/birgivi_ilk_sayfa.txt` (682 karakter, 124
kelime); çalışmanın özgün analiz betiğindeki kanonik referansla aynıdır.

**Normalizasyon.** Anlamı değiştirmeyen yazım farklarının sahte hata sayılmaması
için her iki metne uygulanan kurallar:

1. Harekeler silinir (U+064B–U+065F, U+0670).
2. Farsça ye (ی, U+06CC) → Arapça elif-i maksûre (ى, U+0649).

Arapça noktalı ye (ي) korunur; kef (ك/ک) ve te marbuta (ة) birleştirilmez.
Bu kural seti makaledeki sayıları üretir.

**Metrikler.** `python-Levenshtein` ile karakter ve kelime düzeyinde `editops`
hesaplanır; silme/ekleme/değiştirme ayrı sayılır.
- Karakter doğruluk oranı = (1 − toplam_karakter_hatası / toplam_karakter) × 100
- Hatalı kelime sayısı = silinen + eklenen + değişen

### Sonuçlar (results/metrics.csv)

| Araç | CER doğruluk | Karakter hata (sil/ekle/değiş) | Hatalı kelime (sil/ekle/değiş) |
|---|---|---|---|
| Google Gemini 3.0 Pro | %98,68 | 9 (5/0/4) | 8 (2/0/6) |
| Claude Opus 4.5 | %89,00 | 75 (26/40/9) | 23 (5/7/11) |
| Microsoft Copilot Think Deeper | %85,34 | 100 (29/10/61) | 50 (5/1/44) |
| ChatGPT 5.2 | %84,90 | 103 (53/2/48) | 49 (10/0/39) |
| Perplexity Pro | %83,58 | 112 (28/39/45) | 44 (5/7/32) |

Tüm değerler `src/analyze.py` tarafından `data/outputs/` altındaki kaynak
metinlerden tek tip biçimde üretilir.

> **Not — ChatGPT (düzeltme).** ChatGPT'nin docx çıktısında satır sonları tek
> paragraf içinde satır başı karakteri olarak saklanmıştır. v1.0.0'da metne
> çevirme sırasında bunlar düşmüş, her satırın son kelimesi bir sonraki satırın
> ilk kelimesine yapışmış ve %83,14 (115 hata) elde edilmiştir. Satır sonları
> diğer araçlarda olduğu gibi korunduğunda aynı çıktı %84,90 (103 hata: 53/2/48;
> 49 hatalı kelime: 10/0/39) verir. `data/outputs/chatgpt.txt` buna göre
> düzeltilmiştir; %84,90 değerinin "farklı bir ChatGPT çıktısından geldiği"
> yönündeki önceki not yanlıştı.

> **Not — Başarı Kriterleri kutusu.** HTML raporlardaki kutu Holley'ye (2009)
> göre düzeltilmiştir: İyi %98-99, Orta %90-98, Zayıf %90'ın altı. v1.0.0'daki
> "%90 - %97" aralığı ile kaynakta bulunmayan düzeltme nitelemeleri
> çıkarılmıştır. Puanlar bu değişiklikten etkilenmez.

### Ezberden okuma taban çizgisi

`src/recitation_baseline.py`, sayfanın yaygın biçimde bilinen hadis metinleri
ezberden yazılarak yüksek puanla geçilip geçilemeyeceğini sınar. Standart
imlayla kusursuz bir ezber okuması, diplomatik referansa göre en fazla %94,13
karakter doğruluğuna ulaşır (nüshaya özgü başlık satırı olmadan %88,86). Araç
başına ayırt edici özellikler (hemzeli harf sayısı, `الصلوة`/`الصلاة`,
`أجزم`/`أجذم`, ikame edilen rivayet lafızları)
`results/diagnostic_features.csv` dosyasına yazılır.

### Duyarlılık denetimleri ve ilk denemeler

`src/sensitivity.py`, satır sonları tek boşluğa indirildiğinde ve satır arası
kayıtları gösteren dört köşeli ayraç yok sayıldığında puanların nasıl
değiştiğini ve her aracın kırmızı mürekkepli başlık satırında kaç hata
yaptığını raporlar. Boşluklar tekleştirildiğinde son üç aracın sırası değişir
(Copilot %87,22, Perplexity %86,49, ChatGPT %85,17); bu sebeple bu üç aracın
sıralaması kesin kabul edilmemelidir. Aynı betik 9 Ocak 2026 tarihli ilk
denemeleri de puanlar (`data/outputs/pretests/`: Claude Sonnet 4.5 %78,01,
Copilot Smart %80,50, Perplexity standart arama %23,46, Google Vision); bu
çıktılar karşılaştırmada kullanılmamıştır.

### Atıf

Özbek, Muhammed Sadık. (2026). *Birgivî Kırk Hadis Risalesi — Popüler YZ
Araçlarının Arapça El Yazması Tanıma Performansı (Veri ve Kod)* (v1.0.0)
[Veri seti]. Zenodo. https://doi.org/10.5281/zenodo.20720244

### Lisans

- Kod: MIT (bk. `LICENSE`)
- Veri: CC BY 4.0 (bk. `data/LICENSE`)
- Yazma görseli: ilgili kütüphane/koleksiyona aittir (bk. `data/manuscript/README.md`)
