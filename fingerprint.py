#!/usr/bin/env python3
"""
prose-fingerprint — measure the lexical fingerprint of writing.

Computes lexical diversity (TTR, MATTR) and readability (Flesch Reading Ease,
Flesch-Kincaid grade) for one or more text files. Across multiple files, it
reports how *tight* the fingerprint is: how consistent lexical diversity stays
from one piece to the next.

My first empirical tool in Python. I built it to test a hunch — that a writer's
lexical-diversity signature holds steady across genres. Run it on your own
corpus and find your band.

Pure standard library. No dependencies.

Usage:
    python fingerprint.py essay.txt
    python fingerprint.py samples/*.txt
    cat draft.md | python fingerprint.py --markdown
    python fingerprint.py --window 100 --top 10 chapter*.md
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


def words(text):
    """Lowercase word tokens: letters and apostrophes only."""
    return re.findall(r"[a-z']+", text.lower())


def strip_markdown(text):
    """Remove common Markdown so formatting marks don't skew the counts."""
    text = re.sub(r"^\s*#.*$", "", text, flags=re.M)   # headings
    text = re.sub(r"[*_`>#\[\]]", "", text)             # inline marks
    return text


def ttr(ws):
    """Type-Token Ratio: unique words / total words, as a percent.

    Simple, but length-sensitive: the longer the text, the lower it reads,
    which makes raw TTR a poor tool for comparing texts of different sizes.
    """
    return len(set(ws)) / len(ws) * 100 if ws else 0.0


def mattr(ws, window=50):
    """Moving-Average TTR: TTR averaged over a sliding window.

    Length-corrected, so it *is* comparable across texts of different sizes.
    This is the number to trust for comparison.
    """
    if len(ws) <= window:
        return ttr(ws)
    spans = len(ws) - window + 1
    return sum(len(set(ws[i:i + window])) / window * 100 for i in range(spans)) / spans


def syllables(word):
    """Heuristic syllable count: vowel groups, minus a silent trailing 'e'."""
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    vowels = "aeiouy"
    count, prev_vowel = 0, False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def readability(text):
    """Flesch Reading Ease (0-100, higher = easier) and Flesch-Kincaid grade."""
    ws = words(text)
    sents = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    if not ws or not sents:
        return 0.0, 0.0
    syl = sum(syllables(w) for w in ws)
    words_per_sentence = len(ws) / len(sents)
    syl_per_word = syl / len(ws)
    ease = 206.835 - 1.015 * words_per_sentence - 84.6 * syl_per_word
    grade = 0.39 * words_per_sentence + 11.8 * syl_per_word - 15.59
    return ease, grade


def analyze(text, window=50, top=8):
    ws = words(text)
    sents = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    ease, grade = readability(text)
    return {
        "words": len(ws),
        "unique": len(set(ws)),
        "sentences": len(sents),
        "wps": len(ws) / len(sents) if sents else 0.0,
        "ttr": ttr(ws),
        "mattr": mattr(ws, window),
        "ease": ease,
        "grade": grade,
        "top": Counter(ws).most_common(top),
    }


def load(path, markdown=False):
    text = Path(path).read_text(errors="ignore")
    return strip_markdown(text) if markdown else text


def print_one(name, r):
    print(f"\n{name}")
    print("-" * len(name))
    print(f"  Words:                {r['words']}")
    print(f"  Unique words:         {r['unique']}")
    print(f"  Sentences:            {r['sentences']}")
    print(f"  Avg sentence length:  {r['wps']:.1f} words")
    print(f"  TTR:                  {r['ttr']:.0f}%")
    print(f"  MATTR:                {r['mattr']:.0f}%")
    print(f"  Flesch Reading Ease:  {r['ease']:.0f}/100")
    print(f"  Flesch-Kincaid grade: {r['grade']:.1f}")
    print("  Most repeated:        " + ", ".join(f"{w}({n})" for w, n in r["top"]))


def print_fingerprint(results):
    """Cross-file comparison: how tight is the lexical fingerprint?"""
    print("\n" + "=" * 60)
    print(f"{'FILE':<32}{'words':>7}{'MATTR':>8}{'grade':>7}")
    print("-" * 60)
    for name, r in results:
        print(f"{Path(name).name[:32]:<32}{r['words']:>7}{r['mattr']:>7.0f}%{r['grade']:>7.1f}")
    mattrs = [r["mattr"] for _, r in results]
    lo, hi = min(mattrs), max(mattrs)
    print("-" * 60)
    print(f"\nLexical fingerprint: MATTR {lo:.0f}%-{hi:.0f}% "
          f"(spread {hi - lo:.0f} points across {len(results)} texts)")
    print("Tightest spread = most consistent voice. "
          "Under ~5 points is a steady signature.")


def main():
    p = argparse.ArgumentParser(
        description="Measure the lexical fingerprint of writing (TTR, MATTR, readability).")
    p.add_argument("files", nargs="*", help="text files to analyze; omit to read stdin")
    p.add_argument("--window", type=int, default=50, help="MATTR window size (default 50)")
    p.add_argument("--top", type=int, default=8, help="how many most-repeated words to show")
    p.add_argument("--markdown", action="store_true", help="strip Markdown before analyzing")
    args = p.parse_args()

    if not args.files:
        text = sys.stdin.read()
        if args.markdown:
            text = strip_markdown(text)
        print_one("stdin", analyze(text, args.window, args.top))
        return

    results = []
    for f in args.files:
        r = analyze(load(f, args.markdown), args.window, args.top)
        results.append((f, r))
        print_one(f, r)

    if len(results) > 1:
        print_fingerprint(results)


if __name__ == "__main__":
    main()
