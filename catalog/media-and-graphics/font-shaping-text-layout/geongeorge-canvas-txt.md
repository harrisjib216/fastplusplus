# Canvas-Txt v5

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `TypeScript` · `MIT` · 🟢 active

> Canvas 2D text-box layout for JavaScript that wraps text about 9-11x faster than canvas-hypertxt's measuring mode by caching word widths.

| | |
|---|---|
| **Beats** | canvas-hypertxt (standard measuring mode) |
| **Claimed result** | README table, 600-char strings, µs/op: same text repeated 1.1 (canvas-txt v5) vs 0.9 (canvas-hypertxt, hypertxt faster); 500 strings cycled 5.6 vs 48.3 (about 8.6x, derived from page data); never-repeating strings 51.3 vs 566.2 (about 11.0x, derived from page data). canvas-txt v4: 1,566 / 1,423 / 1,382 µs/op. |
| **Workload** | Word-wrap of 600-character lorem-ipsum strings at width 400 px, 16px Arial, 5000 iterations per scenario, node-canvas measureText, three scenarios: same text repeated, 500 strings cycled, never-repeating strings (bench/compare.mjs, calls splitText against canvas-hypertxt split). |
| **Metric** | latency |
| **Hardware** | Apple Silicon (chip model not stated) |
| **Compiler and flags** | Node.js (version not stated; engines &gt;=18), node-canvas ^3.2.3, canvas-hypertxt ^1.0.3 and canvas-txt@4.1.1 per packages/canvas-txt/package.json devDependencies; not a compiled benchmark |
| **Adoption** | 540 stars; widely used npm package (canvas-txt) |
| **Last commit** | 2026-08-10 |
| **Links** | [repository](https://github.com/geongeorge/Canvas-Txt) · [benchmark](https://github.com/geongeorge/Canvas-Txt) |

## Verdict

First-party run of packages/canvas-txt/bench/compare.mjs on an unnamed Apple Silicon machine (Node version not stated, node-canvas ^3.2.3, canvas-hypertxt ^1.0.3): 5,000 splitText calls on 600-character lorem-ipsum strings at 400 px in 16px Arial, one timed pass per contender, took 51.3 vs 566.2 µs/op on never-repeating strings (about 11x) and 5.6 vs 48.3 µs/op on 500 cycled strings (about 8.6x, both derived from page data), while canvas-hypertxt was slightly faster when one string repeats (0.9 vs 1.1 µs/op, both answering from a result memo). canvas-txt ran its approximate cached mode, not its exact whole-line mode.

## Use it when

- Canvas apps that re-wrap the same vocabulary repeatedly (data grids, canvas editors, chart labels, games), where the per-font width cache stays warm.
- Render loops that redraw unchanged text: layoutText once and paint with drawTextLayout every frame with no re-measuring.
- Server-side image generation with node-canvas or skia-canvas, where measureText is costly and the cache saves the most.
- Text with CJK, Thai or emoji where splitting inside a grapheme or surrogate pair is unacceptable and a whitespace-only splitter breaks badly.
- You want a complete text-box renderer (alignment, ellipsis, justification, debug guides) in about 4 kB gzipped with zero dependencies.

## Skip it when

- Typeset-quality line breaking: breaks come from UAX-29 word boundaries, not UAX-14 line-break rules, so a trailing comma, period, closing parenthesis or the second half of a hyphenated word can start a new line (reproduced this session with the repo's wrap.ts).
- One-off wrapping of unique text with an unfamiliar vocabulary: on a cold cache every segment still costs a measureText call, and the shipped benchmark never measures a cold-cache case.
- You need kerning-exact line widths by default: the cached default sums per-segment widths; the exact whole-line mode (cache: false) exists but was not benchmarked.
- Older runtimes: v5 needs Intl.Segmenter and ES2022 in browsers and Node 18 or newer (a whitespace-split fallback runs where Intl.Segmenter is absent, losing the Unicode handling).
- Pure row-height prediction for virtualised lists of Latin text, where uWrap reports roughly 10x over canvas-hypertxt in browsers with a smaller footprint.

## How it is fast

Text is cut into segments with Intl.Segmenter (word granularity), each segment's width is measured once per font and kept in a module-level Map (FIFO cap 10,000 segments per font key), and line fitting then sums cached numbers instead of calling measureText on growing substrings, which is what canvas-hypertxt's standard mode does character by character. Whole results are also memoised (500 split results and 500 layouts, FIFO) and returned frozen, so repeated identical calls are a Map lookup. The speedup therefore comes from avoiding measureText calls, which are especially slow in node-canvas (Pango/Cairo), the backend the benchmark used.

## Compared with alternatives

Pick canvas-txt over canvas-hypertxt when you want a full text-box renderer with Unicode-aware segmentation and your text reuses a vocabulary, since its cached mode was about 9-11x faster on cycled and never-repeating strings; pick uWrap when you only need line counts or splits for Latin text in browser virtualised lists, and Pretext when you need DOM-free measurement for HTML layout rather than canvas drawing.

## Integration

| | |
|---|---|
| **Form** | module (npm package canvas-txt; ESM, CJS and an IIFE global window.canvasTxt) |
| **Dependencies** | none at runtime (node-canvas, canvas-hypertxt and canvas-txt@4.1.1 are devDependencies for tests and the benchmark) |
| **Minimum toolchain** | Node &gt;= 18 (engines field); modern evergreen browsers with Intl.Segmenter and ES2022; TypeScript types included |
| **Platforms** | any JavaScript runtime with a Canvas 2D-like context (browsers, workers via OffscreenCanvas, node-canvas, skia-canvas) |
| **Thread safety** | not documented; JavaScript is single-threaded, and the width caches and result memos are module-level state shared by every caller in one realm (each worker keeps its own copy) |
| **Drop-in for the baseline** | partial — returns string[] lines like canvas-hypertxt's split, but the call takes ({ctx, text, width}) and uses the context's current font instead of a font argument, and has no estimation (hyper) mode |

## Gotchas

- Harness flaw: the benchmark times canvas-txt's default cached mode, which sums per-segment widths and ignores kerning across segment boundaries, against canvas-hypertxt's standard mode, which measures every candidate substring with measureText; the README calls this 'exact measuring', but canvas-txt's own exact mode is cache: false (whole-line measuring), which compare.mjs never runs. The repo's tests check that cached and exact modes give identical breaks on 5 texts at 3 widths in node-canvas Arial, and that summed widths are within 0.5 px.
- Benchmark cache handling is one-sided: only canvas-hypertxt's cache is cleared before each contender, so canvas-txt's never-repeating 600-character row starts with all 5,000 numeric prefixes and the lorem-ipsum vocabulary already measured by the earlier 100-character pass; the text has no punctuation, so the punctuation line-break behaviour above is never exercised, and the printed line-count sanity check is not reported.
- Memoised layouts and split results are frozen and shared; mutating them throws in strict mode. Pass cache: false for mutable, unshared results.
- Width caches are keyed by the font string and never notice a web font finishing loading: call clearMeasurementCache() after document.fonts.ready, or widths measured on the fallback font persist.

## Known shortcomings

- No CPU model or Node version; the README's 'faster on every workload' is contradicted by its own same-text row (0.9 vs 1.1 us/op); the bench clears only the canvas-hypertxt cache while canvas-txt's width cache stays warm across scenarios; wrapping only, single run.
- Enricher: the bench times canvas-txt's default cached mode (summed per-word widths, kerning across word boundaries ignored) against canvas-hypertxt's standard mode, which measures every candidate substring exactly; canvas-txt's exact mode (cache: false) never runs in compare.mjs although the README says 'exact measuring'; only hypertxt's cache is cleared and the bench text has no punctuation. Correctness bug: wrap uses UAX-29 word segments as break points instead of UAX-14 line-break opportunities, so a comma, period or '\$' can split or '-known' can start a line (reproduced with the repo's wrap.ts under bun: 'hello world' / ', again'), against the README's Unicode-correct wrapping claim.

## Caveats and trade-offs

Benchmark code is public (packages/canvas-txt/bench/compare.mjs, read in full) but the CPU model, Node version and run-to-run variance are not stated, so tier C rather than A; one performance.now() total per contender, no repeated runs. It times line-wrapping and measurement only (splitText; the script's layoutText row is not in the README table), not drawing, and not node-canvas fillText, so the lead's second baseline is not measured. The README's feature table says 'faster than canvas-hypertxt on every workload', but its own Performance table shows canvas-hypertxt faster on repeated identical text (0.9 vs 1.1 µs/op), and the README admits hypertxt's estimation mode is faster on long never-seen strings. Cache handling favours canvas-txt: the script clears only canvas-hypertxt's cache before each contender (hyperClearCache), while canvas-txt's module-level per-font width cache and layout memo are never cleared, so in the never-repeating scenario canvas-txt starts with the numeric prefixes and vocabulary already measured by the earlier 100-character pass and Scenario B, whereas hypertxt gets only its 100 warm-up iterations. The never-repeating scenario also keeps the vocabulary warm (about 70 distinct lorem-ipsum words). README numbers are for 600 characters; the script also runs 100 and 1000. The script prints a line-count sanity check (v5 vs hypertxt) whose output is not reported. Lead said issue #13 holds these numbers: it does not, issue #13 is an unrelated request to return the computed text height. The v5 rewrite and recent commits (all 2026-08-10) are co-authored with an AI assistant. Not C++ (TypeScript); baseline is another JavaScript library, so no std comparison applies. [retier] bench/compare.mjs (node-canvas, Apple Silicon, no CPU model or Node version, single run) times canvas-txt's default cached mode (summed per-word widths, no cross-word kerning) against canvas-hypertxt's exact standard mode; the exact mode (cache: false) is never benchmarked and only hypertxt's cache is cleared. 8.6x and 11.0x on never-repeating 600-char strings, but 0.9 vs 1.1 us/op on repeated text. Wrapping breaks on UAX-29 word segments, not UAX-14, so punctuation can start a line. canvas-hypertxt is catalogued.

Per-font width cache and bounded memoised layouts (about 500 entries); memoised layouts come back frozen; the cache must be cleared with clearMeasurementCache() after web fonts load. Uses Intl.Segmenter for Unicode-correct breaks (CJK, Thai, emoji). About 4 kB gzipped, zero dependencies.

## Maintenance

Active (v5.0.2 rewrite and all recent commits on 2026-08-10, co-authored with an AI assistant, every listed issue closed), MIT-licensed and dependency-free, so easy to adopt; the speed numbers are first-party, single-run and favour canvas-txt's warm cache, and its UAX-29-based wrapping can push punctuation onto a new line.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README Performance table backed by public benchmark code (packages/canvas-txt/bench/compare.mjs), but the CPU model ('Apple Silicon' only) and Node version are not stated, so C, not A.
- **Verifier notes:** README table numbers match the record exactly (1.1/0.9, 5.6/48.3, 51.3/566.2 µs/op; v4 1,566/1,423/1,382). Shortcomings to record: no CPU model or Node version, README 'faster on every workload' contradicted by its own same-text row, benchmark clears only the baseline's cache (canvas-txt's width cache stays warm across scenarios), wrapping only, single run. MIT, 540 stars, last commit 2026-08-10 confirmed; canvas-hypertxt is already a listed entry.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** cold-cache comparison on both sides; exact-mode comparison with UAX-14 breaks
- **Pages the verifier opened:**
  - <https://github.com/geongeorge/Canvas-Txt>
  - <https://github.com/geongeorge/Canvas-Txt/commits/master>
  - <https://github.com/geongeorge/Canvas-Txt/tree/master/packages/canvas-txt/bench>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/README.md>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/packages/canvas-txt/bench/compare.mjs>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/packages/canvas-txt/package.json>
- **Sources the enricher read:**
  - <https://github.com/geongeorge/Canvas-Txt/tree/master/packages/canvas-txt/src>
  - <https://github.com/geongeorge/Canvas-Txt/issues?q=is%3Aissue>
  - <https://github.com/geongeorge/Canvas-Txt/commits/master>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/README.md>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/MIGRATION.md>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/packages/canvas-txt/bench/compare.mjs>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/packages/canvas-txt/package.json>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/packages/canvas-txt/src/cache.ts>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/packages/canvas-txt/src/wrap.ts>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/packages/canvas-txt/src/measure.ts>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/packages/canvas-txt/src/layout.ts>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/packages/canvas-txt/src/index.ts>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/packages/canvas-txt/src/font.ts>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/HEAD/packages/canvas-txt/src/canvas-txt.test.ts>
  - <https://github.com/glideapps/canvas-hypertxt/tree/main/src>
  - <https://raw.githubusercontent.com/glideapps/canvas-hypertxt/main/src/multi-line.ts>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/geongeorge/canvas-txt`) · [data/wave10/enrich/raw/github_com_geongeorge_canvas_txt.json](../../../data/wave10/enrich/raw/github_com_geongeorge_canvas_txt.json) (enrichment confidence 0.8)

</details>
