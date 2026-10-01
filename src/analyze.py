#!/usr/bin/env python3
"""
Birgivî HTR Benchmark — analysis script / analiz betiği.

Compares each AI tool's output against the reference transcription and computes
character (CER) and word (WER) error metrics. Numbers are written to
results/metrics.csv; per-tool HTML reports identical to the study's original
visual output are written to results/diff/. The article's figures are taken
from the CSV (not transcribed by hand).

Her YZ aracının çıktısını referans transkripsiyonla karşılaştırıp karakter (CER)
ve kelime (WER) metriklerini hesaplar. Sayılar results/metrics.csv'ye; her araç
için çalışmanın özgün görsel çıktısıyla aynı HTML rapor results/diff/'e yazılır.

Run / Çalıştırma:
    pip install -r requirements.txt
    python src/analyze.py
"""
import csv
import os
import re
import Levenshtein

# --- Paths / Yollar ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_PATH = os.path.join(ROOT, "data", "reference", "birgivi_ilk_sayfa.txt")
OUT_DIR = os.path.join(ROOT, "data", "outputs")
RESULTS_DIR = os.path.join(ROOT, "results")
DIFF_DIR = os.path.join(RESULTS_DIR, "diff")

# Output filename -> display name. All tools handled uniformly from docx text.
# Çıktı dosyası -> görünen ad. Tüm araçlar docx metninden tek tip işlenir.
TOOLS = [
    ("gemini.txt",             "Google Gemini 3.0 Pro"),
    ("claude_opus.txt",        "Claude Opus 4.5"),
    ("copilot_thinkdeeper.txt", "Microsoft Copilot Think Deeper"),
    ("chatgpt.txt",            "ChatGPT 5.2"),
    ("perplexity_pro.txt",     "Perplexity Pro"),
]

# --- Normalization / Normalizasyon ---
# Identical to the original study script:
#   1) remove diacritics (U+064B–U+065F, U+0670)
#   2) Persian yeh (ی, U+06CC) -> Arabic alef maksura (ى, U+0649)
_DIACRITICS = re.compile(r"[ً-ٰٟ]")

def normalize(text):
    text = text.strip()
    text = _DIACRITICS.sub("", text)
    text = text.replace("ی", "ى")
    return text

# --- Metrics / Metrikler ---
def count_ops(ops):
    d = sum(1 for t, _, _ in ops if t == "delete")
    i = sum(1 for t, _, _ in ops if t == "insert")
    s = sum(1 for t, _, _ in ops if t == "replace")
    return d, i, s

def compute(ref, hyp):
    ref, hyp = normalize(ref), normalize(hyp)
    cd, ci, cs = count_ops(Levenshtein.editops(ref, hyp))
    char_err = cd + ci + cs
    n_char = len(ref)
    cer_acc = (1 - char_err / n_char) * 100 if n_char else 0.0
    if cer_acc < 0:
        cer_acc = 0.0
    rw, hw = ref.split(), hyp.split()
    wd, wi, ws = count_ops(Levenshtein.editops(rw, hw))
    word_err = wd + wi + ws
    n_word = len(rw)
    wer = (word_err / n_word) * 100 if n_word else 0.0
    return dict(
        n_char=n_char, char_err=char_err, char_del=cd, char_ins=ci, char_sub=cs,
        cer_accuracy=round(cer_acc, 2),
        n_word=n_word, word_err=word_err, word_del=wd, word_ins=wi, word_sub=ws,
        wer=round(wer, 2),
    )

# --- HTML report / HTML rapor ---
# The HTML/CSS template below is preserved verbatim from the study's original
# analysis script so the generated report is identical to the author's original
# screen output. Only the data inputs and the tool name are parameterized.
# Aşağıdaki HTML/CSS şablonu, üretilen raporun yazarın özgün ekran çıktısıyla
# aynı olması için çalışmanın özgün betiğinden birebir korunmuştur.
# Exception (after v1.0.0): the criteria box follows Holley (2009): Good 98-99%,
# Average 90-98%, Poor below 90%. The former "%90 - %97" range and the
# correction-effort captions, which are not in Holley, were removed.
# İstisna (v1.0.0 sonrası): Başarı Kriterleri kutusu Holley'ye (2009) göre düzeltilmiş,
# kaynakta bulunmayan "%90 - %97" aralığı ve düzeltme nitelemeleri çıkarılmıştır.
def render_report(name, ref, hyp, path):
    ref, hyp = normalize(ref), normalize(hyp)

    ops_char = Levenshtein.editops(ref, hyp)
    sub_char, ins_char, del_char = (
        sum(1 for t, i, j in ops_char if t == "replace"),
        sum(1 for t, i, j in ops_char if t == "insert"),
        sum(1 for t, i, j in ops_char if t == "delete"),
    )
    total_err_char = sub_char + ins_char + del_char
    total_char = len(ref)
    accuracy = (1 - (total_err_char / total_char)) * 100 if total_char else 0.0
    if accuracy < 0:
        accuracy = 0

    ref_words, hyp_words = ref.split(), hyp.split()
    ops_word = Levenshtein.editops(ref_words, hyp_words)
    sub_word = sum(1 for t, i, j in ops_word if t == "replace")
    ins_word = sum(1 for t, i, j in ops_word if t == "insert")
    del_word = sum(1 for t, i, j in ops_word if t == "delete")
    total_word = len(ref_words)

    c_del_bg, c_del_tx = "#f8d7da", "#842029"   # Kırmızı
    c_ins_bg, c_ins_tx = "#d1e7dd", "#0f5132"   # Yeşil
    c_sub_bg, c_sub_tx = "#fff3cd", "#664d03"   # Sarı

    if accuracy >= 98:
        durum_renk, durum_mesaj = c_ins_bg, "İYİ"
    elif accuracy >= 90:
        durum_renk, durum_mesaj = c_sub_bg, "ORTA"
    else:
        durum_renk, durum_mesaj = c_del_bg, "ZAYIF"

    left_panel = f"""
<div style="flex: 0 0 380px; font-family: 'Segoe UI', Arial, sans-serif; padding-right: 20px; border-right: 2px solid #ccc; color: #000000;">
    <h3 style="border-bottom: 2px solid #000; padding-bottom: 10px; margin-top:0; color: #000000;">📊 Analiz Raporu</h3>
    <table style="width: 100%; border-collapse: collapse; font-size: 15px; margin-bottom: 20px; color: #000000;">
        <tr style="background-color: #f2f2f2; border-bottom: 1px solid #000;">
            <th style="text-align: left; padding: 8px; border: 1px solid #999; color: #000000;">Metrik</th>
            <th style="text-align: center; padding: 8px; border: 1px solid #999; color: #000000;">Karakter (CER)</th>
            <th style="text-align: center; padding: 8px; border: 1px solid #999; color: #000000;">Kelime (WER)</th>
        </tr>
        <tr>
            <td style="padding: 6px; border: 1px solid #999; font-weight: bold;">Toplam</td>
            <td style="text-align: center; border: 1px solid #999; font-weight: bold;">{total_char}</td>
            <td style="text-align: center; border: 1px solid #999; font-weight: bold;">{total_word}</td>
        </tr>
        <tr>
            <td style="padding: 6px; border: 1px solid #999; color: {c_del_tx}; font-weight: bold;">❌ Silinen</td>
            <td style="text-align: center; border: 1px solid #999; color: {c_del_tx}; font-weight: bold;">{del_char}</td>
            <td style="text-align: center; border: 1px solid #999; color: {c_del_tx}; font-weight: bold;">{del_word}</td>
        </tr>
        <tr>
            <td style="padding: 6px; border: 1px solid #999; color: {c_ins_tx}; font-weight: bold;">➕ Eklenen</td>
            <td style="text-align: center; border: 1px solid #999; color: {c_ins_tx}; font-weight: bold;">{ins_char}</td>
            <td style="text-align: center; border: 1px solid #999; color: {c_ins_tx}; font-weight: bold;">{ins_word}</td>
        </tr>
        <tr>
            <td style="padding: 6px; border: 1px solid #999; color: {c_sub_tx}; font-weight: bold;">🔄 Değişen</td>
            <td style="text-align: center; border: 1px solid #999; color: {c_sub_tx}; font-weight: bold;">{sub_char}</td>
            <td style="text-align: center; border: 1px solid #999; color: {c_sub_tx}; font-weight: bold;">{sub_word}</td>
        </tr>
    </table>
    <div style="background-color: {durum_renk}; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #000; color: #000000;">
        <h4 style="margin:0; color: #000000;">Karakter Doğruluk Oranı</h4>
        <h1 style="margin: 5px 0; font-size: 32px; color: #000000;">%{accuracy:.2f}</h1>
        <span style="font-weight: bold; font-size: 18px; color: #000000;">{durum_mesaj}</span>
    </div>
    <br>
    <h4 style="margin: 15px 0 5px 0; border-bottom: 1px solid #000; color: #000000;">🏆 Başarı Kriterleri</h4>
    <table style="width: 100%; border-collapse: collapse; font-size: 14px; color: #000000;">
        <tr style="background-color: #333; color: white;">
            <th style="padding: 6px; text-align: left; border: 1px solid #000;">Doğruluk Oranı</th>
            <th style="padding: 6px; text-align: left; border: 1px solid #000;">Durum</th>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #999; color: #000000; vertical-align: top;"><b>%98 - %100</b></td>
            <td style="padding: 8px; border: 1px solid #999; color: #000000;">
                <b>İYİ</b>
            </td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #999; color: #000000; vertical-align: top;"><b>%90 - %98</b></td>
            <td style="padding: 8px; border: 1px solid #999; color: #000000;">
                <b>ORTA</b>
            </td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #999; color: #000000; vertical-align: top;"><b>< %90</b></td>
            <td style="padding: 8px; border: 1px solid #999; color: #000000;">
                <b>ZAYIF</b>
            </td>
        </tr>
    </table>
</div>
"""

    diff_html = ""
    for tag, i1, i2, j1, j2 in Levenshtein.opcodes(ref, hyp):
        ref_segment = ref[i1:i2]
        hyp_segment = hyp[j1:j2]
        ref_vis = ref_segment.replace("\n", "")
        hyp_vis = hyp_segment.replace("\n", "<br>")
        if tag == "equal":
            diff_html += f"<span>{hyp_vis}</span>"
        elif tag == "delete":
            if ref_vis:
                diff_html += f'<span style="background-color: {c_del_bg}; color: {c_del_tx}; text-decoration: line-through; margin: 0 1px;">{ref_vis}</span>'
        elif tag == "insert":
            diff_html += f'<span style="background-color: {c_ins_bg}; color: {c_ins_tx}; margin: 0 1px;">{hyp_vis}</span>'
        elif tag == "replace":
            diff_html += f'<span style="background-color: {c_sub_bg}; color: {c_sub_tx}; margin: 0 1px;">{hyp_vis}</span>'

    right_panel = f"""
<div style="flex: 1; min-width: 400px; padding-left: 20px; color: #000000;">
    <h3 style="border-bottom: 2px solid #000; padding-bottom: 10px; margin-top:0; text-align: right; color: #000000;">📝 Görsel Hata Analizi ({name})</h3>
    <div dir="rtl" style="
        font-family: 'Amiri', 'Traditional Arabic', serif;
        font-size: 24px;
        line-height: 1.8;
        color: #000000;
        background-color: #fff;
        padding: 15px;
        border: 1px solid #999;
        border-radius: 4px;
        height: auto;
        min-height: 400px;">
        {diff_html}
    </div>
    <div style="margin-top: 10px; font-size: 13px; text-align: right; color: #000000;">
        <span style="background-color: {c_ins_bg}; padding: 2px 5px; border-radius: 3px; border: 1px solid {c_ins_tx};">Yeşil: Eklenen</span>
        <span style="background-color: {c_sub_bg}; padding: 2px 5px; border-radius: 3px; border: 1px solid {c_sub_tx};">Sarı: Değişen</span>
        <span style="background-color: {c_del_bg}; text-decoration: line-through; padding: 2px 5px; border-radius: 3px; border: 1px solid {c_del_tx};">Kırmızı: Silinen</span>
    </div>
</div>
"""

    full_html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet">
</head>
<body style="background-color: #f0f2f5; padding: 20px;">
    <div style="
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        background-color: white;
        padding: 30px;
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        font-family: sans-serif;
        color: #000000;
        max-width: 1200px;
        margin: 0 auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    ">
        {left_panel}
        {right_panel}
    </div>
</body>
</html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(full_html)

# --- Run / Çalıştırma ---
def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(DIFF_DIR, exist_ok=True)
    with open(REF_PATH, encoding="utf-8") as f:
        ref = f.read()

    rows = []
    for fname, display in TOOLS:
        with open(os.path.join(OUT_DIR, fname), encoding="utf-8") as f:
            hyp = f.read()
        m = compute(ref, hyp)
        m["tool"] = display
        m["file"] = fname
        m["kaynak"] = "analyze.py (data/outputs/{})".format(fname)
        rows.append(m)
        render_report(display, ref, hyp, os.path.join(DIFF_DIR, fname.replace(".txt", ".html")))

    rows.sort(key=lambda r: r["cer_accuracy"], reverse=True)

    fields = ["tool", "file", "n_char", "char_err", "char_del", "char_ins", "char_sub",
              "cer_accuracy", "n_word", "word_err", "word_del", "word_ins", "word_sub", "wer", "kaynak"]
    csv_path = os.path.join(RESULTS_DIR, "metrics.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})

    print(f"Referans / Reference: {rows[0]['n_char']} karakter, {rows[0]['n_word']} kelime\n")
    print(f"{'Araç / Tool':<32}{'CER %':>8}{'Krk(d/i/s)':>18}{'Kel(d/i/s)':>18}")
    for r in rows:
        cstr = "{}({}/{}/{})".format(r["char_err"], r["char_del"], r["char_ins"], r["char_sub"])
        wstr = "{}({}/{}/{})".format(r["word_err"], r["word_del"], r["word_ins"], r["word_sub"])
        print(f"{r['tool']:<32}{r['cer_accuracy']:>8}{cstr:>18}{wstr:>18}")
    print(f"\nYazıldı / Written: {csv_path}")
    print(f"Raporlar / Reports: {DIFF_DIR}/")

if __name__ == "__main__":
    main()
