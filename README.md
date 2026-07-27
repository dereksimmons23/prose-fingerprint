# prose-fingerprint

Measure the **lexical fingerprint** of writing — how varied the vocabulary is, how readable the prose is, and, across several texts, how *consistent* that signature stays from one piece to the next.

Pure Python standard library. No dependencies.

## Why I built it

This is my first empirical tool in Python. I'm a writer and a media guy teaching myself to code, and I wanted to test a hunch: that a writer's lexical-diversity signature holds steady across genres — that a eulogy, a song lyric, and a book chapter by the same hand land in the same narrow band.

So I built the thing that would tell me. Run it across your own corpus and find your band.

## What it measures

- **TTR** (Type-Token Ratio) — unique words ÷ total words. Simple, but it drops as texts get longer, so it's a poor tool for comparing different-sized pieces.
- **MATTR** (Moving-Average TTR) — TTR averaged over a sliding window, so it's *length-corrected* and comparable across texts of any size. This is the one to trust.
- **Flesch Reading Ease** (0–100, higher = easier) and **Flesch-Kincaid grade level** — readability.
- Across multiple files: the **MATTR spread** — how tight your fingerprint is. A small spread means a steady voice.

## Usage

```bash
python fingerprint.py essay.txt                  # one file
python fingerprint.py samples/*.txt              # compare several, see the spread
cat draft.md | python fingerprint.py --markdown  # from stdin, stripping Markdown
python fingerprint.py --window 100 --top 10 chapter*.md
```

Try the included public-domain samples:

```bash
python fingerprint.py samples/lincoln.txt samples/shakespeare.txt
```

## What I found

Run across my own writing — a eulogy, an anniversary essay, a song, a book manuscript — the MATTR stayed inside a roughly 3-point band near 80%. Different genres, different decades, one hand. The fingerprint held. That is the kind of small, checkable finding I built it to get.

## Notes

- Syllable counting (for the Flesch scores) is a vowel-group heuristic — fast and good enough for comparison, not exact on every word.
- Readability scores are close to meaningless for song lyrics and poetry; MATTR still works there.

Built by Derek Simmons. Released under the MIT License.
