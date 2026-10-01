#!/usr/bin/env python3
"""
Birgivî HTR Benchmark — recitation (memory-only) baseline / ezberden okuma taban çizgisi.

Question: could a model reach a high score on this page by reciting the well-known
hadith texts from memory, without reading the image? The manuscript page departs
from the commonly printed text at many points (hamza-less Ottoman orthography,
"الصلوة", "أجزم", undotted "العانه", "انتفاص", the title line, bracketed
interlinear additions). This script measures
  (1) the ceiling of a flawless recitation in standard modern orthography, and
  (2) diagnostic features in each tool's output at those points.

Soru: Bir model, görsele bakmadan, yaygın biçimde bilinen hadis metinlerini ezberden
yazarak bu sayfada yüksek puan alabilir mi? Betik, (1) standart imlayla kusursuz bir
ezber okumasının referansa göre alabileceği en yüksek puanı ve (2) nüshanın yaygın
metinden ayrıldığı noktalarda her aracın çıktısındaki ayırt edici özellikleri ölçer.

Run / Çalıştırma:
    python src/recitation_baseline.py
"""
import csv
import os
import re

import analyze as A

# The four hadiths and the opening formulae in standard modern orthography, with the
# SAME wording as the manuscript (the most favourable case for recitation).
# Dört hadis ve giriş kalıpları, nüshayla AYNI lafızla ve standart imlayla
# (ezberden okuma için en elverişli durum).
TITLE_LINE = "هذا حديث الاربعون بركووى محمّد افندى"
CANONICAL_BODY = """بسم الله الرحمن الرحيم
الحمد لله رب العالمين والصلاة والسلام على محمد
وآله أجمعين الحديث الأول إنما الأعمال بالنيات
وإنما لكل امرئ ما نوى فمن كانت هجرته إلى الله و
رسوله فهجرته إلى الله ورسوله ومن كانت هجرته
إلى دنيا يصيبها أو امرأة يتزوجها فهجرته
إلى ما هاجر إليه الحديث الثاني كل أمر ذي بال لم يبدأ
فيه ببسم الله الرحمن الرحيم وفي رواية بالحمد لله فهو أقطع
وفي رواية أجذم الحديث الثالث إذا استيقظ أحدكم
من نومه فلا يغمس يده في الإناء حتى يغسلها ثلاثا فإنه لا يدري
أين باتت يده الحديث الرابع عشر من الفطرة قص
الشارب وإعفاء اللحية والسواك واستنشاق الماء
وقص الأظفار وغسل البراجم ونتف الإبط وحلق
العانة وانتقاص الماء يعني الاستنجاء قال الراوي"""

BASELINES = [
    ("recitation_with_title", "Standart imla, başlık satırı nüshadaki gibi", TITLE_LINE + "\n" + CANONICAL_BODY),
    ("recitation_without_title", "Standart imla, başlık satırı yok", CANONICAL_BODY),
]

_HAMZA = re.compile("[أإآؤئ]")


def features(text):
    n = A.normalize(text)
    return {
        "hamza_letters": len(_HAMZA.findall(n)),
        "final_ya_dotted": len(re.findall(r"ي(?=\s|$)", n)),
        "final_ya_undotted": len(re.findall(r"ى(?=\s|$)", n)),
        "salawat_spelling": "الصلوة" if "الصلوة" in n else ("الصلاة" if "الصلاة" in n else "-"),
        "bi_bismi": "ببسم" in n,
        "ajzam_with_zay": ("اجزم" in n) or ("أجزم" in n),
        "ajdham_with_dhal": ("اجذم" in n) or ("أجذم" in n),
        "yatazawwajuha": "يتزوجها" in n,
        "yankihuha": "ينكحها" in n,
        "abtar": ("أبتر" in n) or ("ابتر" in n),
        "fal_yaghsil": "فليغسل" in n,
        "al_anah_undotted": "العانه" in n,
        "intifas": "انتفاص" in n,
        "intiqas": "انتقاص" in n,
        "qala_al_rawi": ("الراوى" in n) or ("الراوي" in n),
    }


def main():
    with open(A.REF_PATH, encoding="utf-8") as f:
        ref = f.read()

    print("Ezberden okuma taban çizgisi / Recitation baseline")
    base_rows = []
    for key, label, text in BASELINES:
        m = A.compute(ref, text)
        base_rows.append({"baseline": key, "aciklama": label, **m})
        print("  {:<48} karakter doğruluğu %{:.2f} ({} hata) | WER %{:.2f}".format(
            label, m["cer_accuracy"], m["char_err"], m["wer"]))

    feat_rows = [{"text": "REFERENCE (manuscript)", **features(ref)}]
    for fname, display in A.TOOLS:
        with open(os.path.join(A.OUT_DIR, fname), encoding="utf-8") as f:
            feat_rows.append({"text": display, **features(f.read())})

    print("\nAyırt edici özellikler / Diagnostic features")
    for r in feat_rows:
        print("  {:<32} hemzeli harf {:>2} | {} | أجزم:{} أجذم:{} | ينكحها:{} أبتر:{} فليغسل:{} | انتفاص:{} انتقاص:{}".format(
            r["text"], r["hamza_letters"], r["salawat_spelling"], r["ajzam_with_zay"], r["ajdham_with_dhal"],
            r["yankihuha"], r["abtar"], r["fal_yaghsil"], r["intifas"], r["intiqas"]))

    os.makedirs(A.RESULTS_DIR, exist_ok=True)
    p1 = os.path.join(A.RESULTS_DIR, "recitation_baseline.csv")
    with open(p1, "w", encoding="utf-8", newline="") as f:
        fields = ["baseline", "aciklama", "n_char", "char_err", "char_del", "char_ins", "char_sub",
                  "cer_accuracy", "n_word", "word_err", "wer"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(base_rows)
    p2 = os.path.join(A.RESULTS_DIR, "diagnostic_features.csv")
    with open(p2, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(feat_rows[0].keys()))
        w.writeheader()
        w.writerows(feat_rows)
    print("\nYazıldı / Written: {}\n                   {}".format(p1, p2))


if __name__ == "__main__":
    main()
