# uWrap

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `TypeScript` · `MIT` · 🟡 stale

> Sub-2KB TypeScript Canvas2D line-wrap counter for virtualized lists; 7.7-18x faster than canvas-hypertxt in the author's browser runs.

| | |
|---|---|
| **Beats** | canvas-hypertxt (JavaScript canvas text-wrapping library) |
| **Claimed result** | README headline '10x faster'. Table: Chrome 135 82ms vs 770ms (about 9.4x, derived from page data); Firefox 137 90ms vs 1660ms (about 18x, derived from page data); Safari 18.1 185ms vs 1430ms (about 7.7x, derived from page data). README also says it is better in memory use and more accurate. |
| **Workload** | 100,000 random sentences (demo/txtgen.mjs) wrapped at random widths of 50-250px, using a Canvas2D context set to 14px Inter with letterSpacing 0.15px. uWrap is timed as varPreLine(ctx) setup plus count(text, width) per sentence. canvas-hypertxt is timed as split(ctx, text, font, width, true) per sentence, with hyper-wrapping enabled, and the length of the returned array is read. Each library is timed once with console.time on the demo page (demo/index.html), run from the DevTools console. |
| **Metric** | latency |
| **Adoption** | 319 stars |
| **Last commit** | 2025-08-01 |
| **Links** | [repository](https://github.com/leeoniya/uWrap) · [benchmark](https://github.com/leeoniya/uWrap) |

## Verdict

First-party README numbers: 100k random txtgen sentences at random widths of 50-250px, 14px Inter with 0.15px letterSpacing. uWrap setup plus count() took 82, 90 and 185 ms, against 770, 1660 and 1430 ms for canvas-hypertxt split(hyper=true), in Chrome 135, Firefox 137 and Safari 18.1 (9.4x, 18.4x, 7.7x, derived from page data), one console.time run each, machine unstated. The enricher reran the same loops in Node 22 with a synthetic measureText (4-vCPU Xeon 2.80GHz container, 3 reps, identical inputs for both libraries): uWrap count 122-133 ms, uWrap split 139-142 ms, canvas-hypertxt 909-989 ms. Timing count() instead of split() therefore flatters uWrap by only 7-14%, and the gap stays 6.4-7.1x like for like, mostly algorithmic. No flaw was found in the timed code beyond the count-vs-split mismatch and the single unrepeated runs.

## Use it when

- Virtualized lists and data grids in the browser that need row heights for thousands to hundreds of thousands of Latin-text cells without DOM reflow.
- UI text in one font and size per context (for example 14px Inter) with letterSpacing or wordSpacing and pre-line semantics: explicit newlines plus wrapping at spaces and hyphens.
- Only a line count or a 'does it wrap' test is needed: count() and test() allocate nothing per call, and test() stops after the second line.
- Bundle-size-sensitive front ends: under 2KB minified, no runtime dependencies, ESM and IIFE builds.

## Skip it when

- Text without spaces between words, such as CJK or Thai: a 32-character Chinese string came back as one overflowing line in the enricher's test. Breaks happen only at the ASCII space and after '-'. There is no UAX #14 line breaking and no shaping or ligature handling, and characters outside the BMP are measured one UTF-16 code unit at a time.
- Text with tabs or Windows line endings: tabs are not break points (CSS pre-line turns them into spaces, so browsers wrap there), and '\r' stays inside the line ('first line\r\nsecond line' gave 'line\r' as a line). The README says \r\n is not handled.
- Long words or URLs that need overflow-wrap or word-break: they are not split and overflow one line (issue #1 is the open TODO).
- white-space normal, pre-wrap or break-spaces, mixed fonts or rich text: only the pre-line strategy exists, with one font per context.
- Node or server-side use without a Canvas2D implementation: it needs a CanvasRenderingContext2D (the tests use skia-canvas).

## How it is fast

Setup measures each of the \~95 printable ASCII characters, plus every uppercase-led pair (26x95), with ctx.measureText once, filling a width table and a kerning table; that was 2,594 calls in the enricher's run. After that, wrapping is one linear pass over charCodeAt with table lookups and greedy tracking of break points. The hot loop calls measureText only for unseen non-ASCII characters (then cached), and count/test allocate no strings. canvas-hypertxt does far more per call: it builds a string cache key and re-measures growing prefixes one character at a time in getSplitPoint, which is quadratic in line length. In hyper mode it switches to trained per-character estimates times 1.01 after 500k measured characters.

## Compared with alternatives

Pick uWrap over canvas-hypertxt for predicting Latin pre-line row heights. Its pass is linear, needs no per-call cache key, and in the enricher's synthetic-font test it matched an exact greedy wrap on 99.5% of 100k inputs (the rest were hyphen breaks the reference ignored), against 65.7% for hyper-mode canvas-hypertxt, which over-counted lines on 34%. Pretext is the broader DOM-free measurement and layout sibling; look at it when you need more than Latin pre-line line counting.

## Integration

| | |
|---|---|
| **Form** | module (npm uwrap: ESM dist/uWrap.mjs, IIFE dist/uWrap.iife.min.js, TypeScript .d.ts) |
| **Dependencies** | none at run time; needs a CanvasRenderingContext2D (browser canvas, or skia-canvas in Node as the tests do) |
| **Minimum toolchain** | Any JS runtime with ES modules or a script tag and Canvas2D measureText; Canvas letterSpacing is optional (a faux fallback adds it manually) |
| **Platforms** | Browsers (README timings for Chrome 135, Firefox 137, Safari 18.1); Node with a canvas implementation |
| **Thread safety** | Not documented. JavaScript is single-threaded per realm, but the closures share one ctx and add unseen characters to a shared width cache, so build one varPreLine per font/context. |
| **Drop-in for the baseline** | no |

## Gotchas

- The width tables are built from ctx.font when varPreLine() runs. Changing ctx.font afterwards, or building before a web font has loaded, leaves stale widths, so rebuild after the font is ready.
- Accuracy bug in the faux letter-spacing path, used when the canvas ignores letterSpacing (Safari before 18.4 per the source comment, which includes the README's Safari 18.1 run): an uppercase letter followed by an ASCII character loses its letter spacing, because the pair width subtracts the next character's spacing and adds back only one. In a Node test with 2px spacing, 'ABCDEF' came out 10px (5 x 2px) narrower than expected and 'Hello World' 4px narrower. This affects predicted widths, not timing.
- Widths are sums of per-character advances measured in isolation, with kerning only for uppercase-plus-ASCII pairs. The README's accuracy claim is backed only by the visual overlays on the demo page.
- A trailing newline produces an extra empty line: split('abc\n') returns ['abc', ''] and count gives 2, so check this case against how your renderer sizes rows.

## Known shortcomings

- Off-baseline (JavaScript canvas text wrapping, not HarfBuzz or FreeType) and the harness times different calls: uWrap's count() (a counter with no strings) against canvas-hypertxt's split(..., true), which slices and trims line strings and builds a cache key; each library draws its own random widths; both are approximations (character LUT plus uppercase kerning versus a trained estimate); the accuracy and memory claims carry no numbers; single console.time runs with no machine named. Last commit 2025-08-01.
- Enricher (e112, 2026-10-05): a Node 22 re-run with synthetic measureText gives count 122-133 ms, split 139-142 ms, canvas-hypertxt 909-989 ms, a 6.4-7.1x like-for-like gap that is mostly algorithmic (hypertxt's quadratic prefix re-measure); the count-vs-split asymmetry is only 7-14%. C stands. Accuracy bugs, not timing: the faux letterSpacing path (Safari before 18.4, including the README's Safari 18.1 run) drops spacing on uppercase plus ASCII pairs ('ABCDEF' 10 px short at 2 px); no CJK or tab wraps; '\r' kept; a trailing '\n' adds an empty line. Synthetic accuracy: uWrap 99.5% match to exact greedy, hypertxt hyper mode 65.7%.

## Caveats and trade-offs

The baseline is a third-party canvas wrapping helper (glideapps/canvas-hypertxt, 138 stars, used by Glide Data Grid), not HarfBuzz or FreeType. This is Latin-only line wrapping at the edge of the shaping and layout category, so the entry is off-baseline. The harness does not time the same calls. uWrap is timed through count(), which only increments a counter and allocates no line strings. canvas-hypertxt is timed through split(), which slices and trims an array of line strings and builds a string cache key for every call. uWrap's split() was not benchmarked, so part of the gap comes from the different work. Each library draws its own random widths, so the two do not wrap identical (text, width) pairs. Each figure is a single console.time run with no repetitions or warm-up control, and uWrap always runs first. Browsers are named but the machine and CPU are not. Both libraries approximate wrapping instead of measuring every line. uWrap sums per-character widths from a one-time lookup table plus uppercase-pair kerning, works for Latin text and the pre-line strategy only, and does not handle \r\n. canvas-hypertxt in hyper mode switches to a trained per-character estimate (times 1.01) after about 500k characters. The README's accuracy and memory claims have no numbers: accuracy is shown only as visual overlays on the demo page.

Under 2KB minified. Only the pre-line wrapping strategy is implemented; works most accurately for Latin text; does not handle Windows-style \r\n line breaks. It predicts row heights for virtualized lists and does not do shaping.

## Maintenance

Stale since 2025-08-01: 17 commits, npm uwrap 0.1.2 published 2025-07-28, MIT, 319 stars, 5 forks, one open issue (word-break TODO). It is small enough to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance table gives first-party console.time numbers (uWrap 82/90/185 ms vs canvas-hypertxt 770/1660/1430 ms in Chrome 135, Firefox 137, Safari 18.1). The harness is public (demo/index.html with a vendored demo/canvas-hypertxt.mjs and demo/txtgen.mjs), but there is no machine or CPU model, only one console.time run per library and no independent measurement, so it stays at C.
- **Verifier notes:** The numbers match the README exactly: 9.4x (Chrome), 18.4x (Firefox) and 7.7x (Safari), derived from page data. The main shortcoming is that the harness times uWrap count() against canvas-hypertxt split(), which allocates line strings. The last commit is 2025-08-01 (14 months old, so stale), the license is MIT, there are 319 stars, and it is not a fork. The only issue (#1) is a word-break TODO, and no independent measurement was found.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** first-party benchmark; enricher re-run
- **Pages the verifier opened:**
  - <https://github.com/leeoniya/uWrap>
  - <https://github.com/leeoniya/uWrap/commits>
  - <https://github.com/leeoniya/uWrap/tree/main/demo>
  - <https://github.com/leeoniya/uWrap/tree/main/test>
  - <https://github.com/leeoniya/uWrap/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/README.md>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/demo/index.html>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/demo/canvas-hypertxt.mjs>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/demo/canvas-txt.mjs>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/demo/txtgen.mjs>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/src/uWrap.ts>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/package.json>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/LICENSE>
  - <https://github.com/glideapps/canvas-hypertxt>
- **Sources the enricher read:**
  - <https://github.com/leeoniya/uWrap>
  - <https://github.com/leeoniya/uWrap/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/README.md>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/package.json>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/src/uWrap.ts>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/dist/uWrap.mjs>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/dist/uWrap.d.ts>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/test/uWrap.test.mjs>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/demo/index.html>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/demo/canvas-hypertxt.mjs>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/demo/txtgen.mjs>
  - <https://registry.npmjs.org/uwrap>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/leeoniya/uwrap`) · [data/wave10/enrich/raw/github_com_leeoniya_uwrap.json](../../../data/wave10/enrich/raw/github_com_leeoniya_uwrap.json) (enrichment confidence 0.8)

</details>
