# canvas-hypertxt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript` · `MIT` · 🟡 stale

> Zero-dependency JavaScript line breaker for HTML5 canvas text; up to 9.8x faster than canvas-txt 3.x (19x with HyperWrapping).

| | |
|---|---|
| **Beats** | canvas-txt (JavaScript canvas multi-line text library) |
| **Claimed result** | Seconds for 5000 iterations, canvas-txt vs canvas-hypertxt vs canvas-hypertxt with HyperWrapping: 20 char 0.05 vs 0.05 vs 0.05; 100 char 0.59 vs 0.11 vs 0.11; 300 char 2.63 vs 0.40 vs 0.26; 600 char 6.17 vs 0.81 vs 0.47; 1000 char 11.19 vs 1.43 vs 0.77 (about 7.8x and 14.5x, derived from page data); 1800 char (overflow) 22.47 vs 2.29 vs 1.19 (about 9.8x and 18.9x, derived from page data). README also says HyperWrapping makes the measure pass over 100x faster (no numbers) and that canvas-hypertxt is 20-30% faster than canvas-multiline-text without HyperWrapping and about 1.2x with it (no table; canvas-multiline-text excluded for failing a correctness test). |
| **Workload** | Storybook page in a browser: wrap and draw text into a 450 px wide box on a 500x500 canvas at 20px sans-serif, centered, for strings of 20 to 1800 characters (a fixed song-lyric prefix with the iteration number prepended), 5000 iterations per library; the timer wraps canvas-txt drawText versus canvas-hypertxt split plus fillText of each line. |
| **Metric** | latency |
| **Adoption** | 138 stars; used inside glide-data-grid |
| **Last commit** | 2023-11-25 |
| **Links** | [repository](https://github.com/glideapps/canvas-hypertxt) · [benchmark](https://github.com/glideapps/canvas-hypertxt) |

## Verdict

First-party Storybook benchmark in an unnamed browser and machine: 5000 iterations of wrapping a song-lyric string (iteration number prepended, so results are not memo hits) into a 450 px box at 20px sans-serif and drawing it, 1000 chars 11.19 s for canvas-txt 3.x vs 1.43 s for canvas-hypertxt and 0.77 s with HyperWrapping (about 7.8x and 14.5x, derived from page data). The canvas-txt timing includes setting ctx.font on every call, canvas-hypertxt stops drawing below 500 px, and HyperWrapping trains and is measured on the same text.

## Use it when

- Canvas-rendered UIs (data grids, charts, canvas editors) that wrap many short-to-medium Latin strings per frame and draw them themselves, as glide-data-grid does (its core package 6.0.4-alpha25 still depends on canvas-hypertxt ^1.0.3).
- Re-layout of the same strings at the same width (scrolling, redraws): repeated calls return the memoised line array.
- Long-running pages with a large volume of text in one font where HyperWrapping can train, and an occasional line that wraps one word early is acceptable.
- Wrapping at non-space break points (CJK, hyphens) when you can supply break opportunities from a UAX #14 implementation through the optional callback.

## Skip it when

- Text that contains blank lines (consecutive, leading or trailing newlines) or calls with a width narrower than about two thirds of one glyph: open issues #12 and #11, reproduced here with a mock canvas, show the per-font average width becoming NaN, after which every later split() for that font key returns lines unwrapped until clearCache().
- Lines whose characters are much narrower than the font key's learned average (below about two thirds of it, e.g. runs of 'i', 'l', '.' after training on ordinary prose): split() measures only the first 1.5 average line lengths, so such lines are returned unwrapped and overflow (code reading plus mock-canvas reproduction).
- Never-repeating text without HyperWrapping against current alternatives: the canvas-txt maintainer's node-canvas benchmark (issue #13) gives 566.2 µs/op for canvas-hypertxt standard mode vs 51.3 µs/op for canvas-txt v5 on 600-char strings (about 11x slower, derived from page data), and uWrap reports 770 ms for canvas-hypertxt vs 82 ms for itself in Chrome 135.
- Layouts that need justify, vertical alignment, managed line heights or preserved leading spaces (every wrapped line after the first is trimmed; issue #7).
- Projects that need a maintained dependency: last commit and npm release 1.0.3 on 2023-11-25, six open issues with no maintainer replies.

## How it is fast

canvas-txt 3.x finds wrap points by calling ctx.measureText once per added character (and sets ctx.font inside every drawText call); canvas-hypertxt guesses the split point from a running per-font average character width, measures only a window of about 1.5 average line lengths, then steps the guess forward or jumps back to the previous space, so it needs a handful of measureText calls per line. Results are memoised in a 500-entry map keyed by text, font key and width. Optional HyperWrapping learns a per-character width table by gradient-style back-propagation against real measureText results (after 20,000 measured characters for that font key) and, once 500,000 characters have been seen, estimates widths with a 1% safety margin without calling measureText at all.

## Compared with alternatives

uWrap, the only like-for-like sibling, reports about 9x lower time than canvas-hypertxt in Chrome 135 (about 18x in Firefox 137, derived from page data) and better accuracy but documents Latin-only accuracy, no \r\n handling and only pre-line wrapping; pick canvas-hypertxt only when you need its pluggable break-opportunity callback or you already depend on glide-data-grid. Pretext targets DOM-free measurement in general and Parley or text-shaper do real shaping, so none of them replace a canvas line splitter directly.

## Integration

| | |
|---|---|
| **Form** | module (npm package canvas-hypertxt 1.0.3, ESM and CommonJS builds with TypeScript types; the logic is one \~240-line source file that is easy to vendor) |
| **Dependencies** | none |
| **Minimum toolchain** | Any JavaScript runtime with Map, for...of and a CanvasRenderingContext2D (browsers; node-canvas works per the canvas-txt maintainer's benchmark); not documented beyond that |
| **Platforms** | any JavaScript environment with a 2D canvas context |
| **Thread safety** | not documented; all caches (results, per-font metrics, HyperWrapping tables) are module-level globals shared by every caller in a realm, and each web worker gets its own copy |
| **Drop-in for the baseline** | no |

## Gotchas

- fontStyle is only a cache key: the caller must set ctx.font to the matching font before calling split(), use a distinct key per font, and call clearCache() once web fonts finish loading (document.fonts.ready), or the learned widths belong to the fallback font.
- The result memo key is text, font key and width but not hyperWrappingAllowed, and eviction past 500 entries drops the oldest inserted key rather than the least recently used one.
- HyperWrapping estimates are deliberately inflated by 1%, so a minority of lines wrap one word early, and the model is only as good as the text it trained on for that font key.
- Width &lt;= 0 returns an empty array; first lines are right-trimmed and later lines fully trimmed.

## Known shortcomings

- Off-baseline (JavaScript canvas text layout). The harness benchmark.stories.tsx is public but states no browser or machine, and the timing is asymmetric: canvas-txt sets ctx.font inside the timed loop and draws overflow lines while hypertxt keeps warm metrics (the win is still real because canvas-txt calls measureText per character). Stale since 2023-11-25.
- Enricher (e105, 2026-10-05): correctness bug, not behind the numbers: an empty line, or a width below about 2/3 of a glyph, gives a NaN font average, after which split() for that font key returns lines unwrapped (open issues #12 and #11; reproduced in node with a mock canvas: 1 line instead of about 15). Lines of narrow glyphs overflow unwrapped because only the first 1.5 average line lengths are measured (reproduced). Harness order effects and HyperWrapping training on the same text it measures noted. Tier C stands; the baseline is superseded. Lead: canvas-txt v5 benchmarks 51.3 vs 566.2 us/op against canvas-hypertxt standard mode on never-repeating 600-char strings (about 11x, node-canvas, Apple Silicon).

## Caveats and trade-offs

Baseline is canvas-txt 3.x, a niche JavaScript library whose wrap search calls ctx.measureText once per added character; not HarfBuzz or FreeType, and canvas text wrapping is at the edge of the shaping and layout category. Browser, browser version, OS and machine are not stated. The harness (src/stories/benchmark.stories.tsx) is not symmetric: canvas-txt's drawText sets ctx.font inside the timed region on every call (twice, via getTextHeight) while canvas-hypertxt's font is set once before its loop (the README itself calls setting ctx.font 'really slow'); canvas-hypertxt stops drawing lines once y exceeds 500 px while canvas-txt draws every line, which favours canvas-hypertxt in the 1800-char overflow row; canvas-hypertxt's per-font width metrics and HyperWrapping model persist across the 5000 iterations (clearCache is called once before its loop), and HyperWrapping trades accuracy for speed (wraps can land one word early). Fonts rendered are the same (20px sans-serif) and fillText is timed for both. The README says it is not a drop-in replacement (no justify, no managed rendering). Last commit 2023-11-25 (stale). It is also the baseline that uWrap claims to beat.

HyperWrapping trains a weighting model to estimate string widths without calling measureText, trading accuracy for speed: wraps slightly early by a word in a small number of cases (README says estimates are within 1% of measured size). Justified text is not supported.

## Maintenance

Stale since 2023-11-25 (npm 1.0.3) with an open NaN bug that silently disables wrapping, though MIT, dependency-free and small enough to vendor and patch (skip measureText for empty strings); the baseline it beat has since been rewritten (canvas-txt v5).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README table (5000 iterations, canvas-txt vs canvas-hypertxt with and without HyperWrapping) matches the record; the harness src/stories/benchmark.stories.tsx is public but browser, machine and OS are not stated and the timed work differs between libraries, so first-party with partial methodology.
- **Verifier notes:** Numbers match the README; harness read and the canvas-txt v3.0.0 drawText source checked, which shows the speed gap is real (per-character measureText) but inflated somewhat by the timing asymmetries listed in caveats. Metadata (MIT, 138 stars, last commit 2023-11-25, stale) verified.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party benchmark
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/glideapps/canvas-hypertxt/main/README.md>
  - <https://raw.githubusercontent.com/glideapps/canvas-hypertxt/main/src/stories/benchmark.stories.tsx>
  - <https://raw.githubusercontent.com/glideapps/canvas-hypertxt/main/package.json>
  - <https://raw.githubusercontent.com/glideapps/canvas-hypertxt/main/src/index.ts>
  - <https://raw.githubusercontent.com/glideapps/canvas-hypertxt/main/src/multi-line.ts>
  - <https://raw.githubusercontent.com/geongeorge/canvas-txt/v3.0.0/src/index.js>
  - <https://github.com/glideapps/canvas-hypertxt>
  - <https://github.com/glideapps/canvas-hypertxt/commits/main>
- **Sources the enricher read:**
  - <https://github.com/glideapps/canvas-hypertxt>
  - <https://raw.githubusercontent.com/glideapps/canvas-hypertxt/main/README.md>
  - <https://raw.githubusercontent.com/glideapps/canvas-hypertxt/main/package.json>
  - <https://raw.githubusercontent.com/glideapps/canvas-hypertxt/main/src/index.ts>
  - <https://raw.githubusercontent.com/glideapps/canvas-hypertxt/main/src/multi-line.ts>
  - <https://raw.githubusercontent.com/glideapps/canvas-hypertxt/main/src/stories/benchmark.stories.tsx>
  - <https://github.com/glideapps/canvas-hypertxt/tree/main/test>
  - <https://github.com/glideapps/canvas-hypertxt/issues?q=is%3Aissue>
  - <https://github.com/glideapps/canvas-hypertxt/pulls?q=is%3Apr>
  - <https://github.com/glideapps/canvas-hypertxt/issues/11>
  - <https://github.com/glideapps/canvas-hypertxt/issues/12>
  - <https://github.com/glideapps/canvas-hypertxt/issues/13>
  - <https://raw.githubusercontent.com/geongeorge/Canvas-Txt/master/packages/canvas-txt/bench/compare.mjs>
  - <https://raw.githubusercontent.com/glideapps/glide-data-grid/main/packages/core/package.json>
  - <https://registry.npmjs.org/canvas-hypertxt>
  - <https://raw.githubusercontent.com/leeoniya/uWrap/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/glideapps/canvas-hypertxt`) · [data/wave10/enrich/raw/github_com_glideapps_canvas_hypertxt.json](../../../data/wave10/enrich/raw/github_com_glideapps_canvas_hypertxt.json) (enrichment confidence 0.8)

</details>
