#!/usr/bin/env python3
"""
Birgivî HTR Benchmark — sensitivity checks and first-attempt outputs / duyarlılık denetimleri ve ilk denemeler.

(1) How much do the scores depend on counting line breaks and the four square brackets
    that mark interlinear additions in the reference?
(2) How well was the rubricated (red-ink) title line read?
(3) Scores of the first attempts of 9 January 2026 (other model/mode of three platforms,
    plus Google Vision), which were not used in the comparison.

(1) Puanlar, satır sonlarının ve referansta satır arası kayıtları gösteren dört köşeli
    ayracın karakter sayılmasına ne ölçüde bağlı?
(2) Kırmızı mürekkeple yazılmış başlık satırı ne ölçüde doğru okunmuş?
(3) 9 Ocak 2026 tarihli ilk denemelerin (üç platformun diğer modeli/modu ve Google Vision)
    puanları; bu çıktılar karşılaştırmada kullanılmamıştır.

Run / Çalıştırma:
    python src/sensitivity.py
"""
import csv
import os

import Levenshtein

import analyze as A

TITLE_LINE = "هذا حديث الاربعون بركووى محمّد افندى"
PRETESTS = [
    ("claude_sonnet.txt", "Claude Sonnet 4.5", "2026-01-09"),
    ("copilot_smart.txt", "Microsoft Copilot Smart", "2026-01-09"),
    ("perplexity_standard.txt", "Perplexity (standard search)", "2026-01-09"),
    ("google_vision.txt", "Google Vision", "2026-01-09"),
]


def collapse(text):
    """All whitespace (incl. line breaks) -> single space. / Tüm boşluklar tek boşluk."""
    return " ".join(text.split())


def no_brackets(text):
    return text.replace("[", "").replace("]", "")


def title_errors(hyp):
    t = A.normalize(TITLE_LINE)
    h = A.normalize(hyp)
    return min(Levenshtein.distance(t, h[:k]) for k in range(len(t) - 8, len(t) + 12)), len(t)


def main():
    with open(A.REF_PATH, encoding="utf-8") as f:
        ref = f.read()
    rows = []
    print("{:<32}{:>10}{:>14}{:>14}{:>16}".format("Araç / Tool", "asıl", "boşluk tek", "ayraçsız", "başlık hatası"))
    for fname, display in A.TOOLS:
        with open(os.path.join(A.OUT_DIR, fname), encoding="utf-8") as f:
            hyp = f.read()
        base = A.compute(ref, hyp)
        ws = A.compute(collapse(ref), collapse(hyp))
        nb = A.compute(no_brackets(ref), no_brackets(hyp))
        te, tn = title_errors(hyp)
        rows.append({"tool": display, "cer_accuracy": base["cer_accuracy"], "char_err": base["char_err"],
                     "cer_accuracy_whitespace_collapsed": ws["cer_accuracy"], "char_err_whitespace_collapsed": ws["char_err"],
                     "cer_accuracy_no_brackets": nb["cer_accuracy"], "title_line_errors": te, "title_line_chars": tn})
        print("{:<32}{:>10}{:>14}{:>14}{:>16}".format(display, base["cer_accuracy"], ws["cer_accuracy"], nb["cer_accuracy"], "{}/{}".format(te, tn)))
    os.makedirs(A.RESULTS_DIR, exist_ok=True)
    p1 = os.path.join(A.RESULTS_DIR, "sensitivity.csv")
    with open(p1, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    pre = []
    print("\nİlk denemeler / First attempts (not used in the comparison)")
    for fname, display, date in PRETESTS:
        with open(os.path.join(A.OUT_DIR, "pretests", fname), encoding="utf-8") as f:
            m = A.compute(ref, f.read())
        pre.append({"tool": display, "date": date, "file": "pretests/" + fname, **m})
        print("  {:<30} {}  karakter doğruluğu %{:.2f} ({} hata)".format(display, date, m["cer_accuracy"], m["char_err"]))
    p2 = os.path.join(A.RESULTS_DIR, "pretests.csv")
    with open(p2, "w", encoding="utf-8", newline="") as f:
        fields = ["tool", "date", "file", "n_char", "char_err", "char_del", "char_ins", "char_sub", "cer_accuracy",
                  "n_word", "word_err", "word_del", "word_ins", "word_sub", "wer"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(pre)
    print("\nYazıldı / Written: {}\n                   {}".format(p1, p2))


if __name__ == "__main__":
    main()
