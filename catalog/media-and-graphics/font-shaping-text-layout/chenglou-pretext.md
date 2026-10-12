# Pretext

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `TypeScript` · `MIT` · 🟢 active

> TypeScript library that predicts the browser's line breaks and paragraph heights from cached Canvas widths, so apps skip DOM reflow reads.

| | |
|---|---|
| **Beats** | Browser DOM text measurement (getBoundingClientRect, offsetHeight and the layout reflow they trigger) |
| **Claimed result** | No Pretext-versus-DOM numbers in the repository. The current README says 'Fast, accurate' and that layout() is 'pure arithmetic. No DOM layout & reflow!'. Early README versions in the npm tarballs 0.0.0 to 0.0.4 (March-April 2026) gave first-party absolute timings with no DOM baseline: prepare() about 17-19 ms and layout() about 0.09-0.10 ms for a shared 500-text batch. Third-party blogs and landing pages (snippets only) call it '300-600x' or '500x faster' than DOM measurement; none of this is measured in the repo. |
| **Workload** | Measuring multiline text height and line breaks in the browser without DOM layout: prepare() once per text, then layout() as pure arithmetic over cached widths. |
| **Metric** | latency |
| **Adoption** | 50.7k stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/chenglou/pretext) · [benchmark](https://github.com/chenglou/pretext) |

## Verdict

No Pretext-versus-DOM measurement exists in the repo: bun harness bench times Pretext builds against each other in Chrome 154, Firefox 156.0.1 and Safari 27 on an M5 Max, and the only absolute figures are Pretext's own (chat demo on a stand-in Canvas: 46-100 us per first prepare, 0.4-0.7 us per layout; Chrome 153 prepared the corpora in 115 ms and Safari 26.5.2 in 350 ms on 2026-09-15; early npm READMEs: prepare about 19 ms and layout about 0.09 ms for 500 texts). The 300-600x, 500x and 540x figures come from third-party pages (one snippet: about 380 ms DOM versus 0.7 ms on 1,000 paragraphs), and per a search snippet the author called that comparison unfair because it sets a cached layout() against a cold DOM measurement.

## Use it when

- Virtualized lists, chat histories and feeds with thousands of text rows whose exact heights must be known before render and recomputed on every resize: prepare each message once, then call layout() per width (RESEARCH.md, before #338 and on a stand-in Canvas: 0.4-0.7 us per layout, 43-59 ms median to re-lay out 100,000 messages).
- Userland layout that needs line geometry: masonry grids, chat bubbles shrink-wrapped to the widest line (walkLineRanges), text flowing around images (layoutNextLineRange), or drawing wrapped text into Canvas or SVG.
- Code that would otherwise interleave DOM writes and reads across components and has to batch them to avoid layout thrashing.
- Pre-sizing textarea-like pre-wrap text, or checking in development that labels do not wrap, in Chrome, Firefox and Safari 27 with named fonts and px sizes, including CJK, Arabic, Thai and emoji.

## Skip it when

- Measuring a text once: prepare() still calls Canvas measureText for every new segment, and nothing in the repo compares that cold cost with one DOM read; the gain comes from repeated layout() calls on cached widths.
- Server-side rendering, Node or Bun without a Canvas, and React Native: it throws 'Text measurement requires OffscreenCanvas or a DOM canvas context.' (SSR #123 and React Native #131/#157 are open, server-side measurement is punted).
- Pagination, print or any place where an undercount breaks the page: open #334 reports Songti SC 16px at 120 and 135 px giving 2 lines where Chrome gives 3, and #421 (2026-10-04) reports kerned overlong words ('AV', 'WAVE', 'To.') broken one letter off in Firefox 156, Chromium 147 and WebKit 26.4.
- CSS outside its subset: system-ui or -apple-system on macOS, rem/em sizes, font-feature-settings or font-variation-settings, non-default font-kerning or word-spacing, hyphens: auto, word-break: break-all (#402), overflow-wrap: normal, bidi visual order, or per-span font sizes beyond what rich-inline models.
- C or C++ code, or native apps: it is browser JavaScript tied to the host's Canvas text engine; for native shaping and layout see HarfBuzz-based stacks or Parley.

## How it is fast

A two-phase cache. prepare() runs ports of each engine's own line-break scan and grapheme rules (Blink, WebKit and Gecko tables pinned to browser builds, src/line-breaks.ts and src/gecko-line-breaks.ts), splits the text into break-delimited segments and measures each with Canvas measureText on an OffscreenCanvas, caching widths per (font, segment) in a shared Map. layout() is a greedy first-fit line walk over parallel arrays (widths as number[], segment kinds as a Uint8Array) with no Canvas calls, string work or per-line allocation; for plain prose a single numeric loop counts lines (the #338 fast path the CHANGELOG credits with a 2-3x faster layout() in Chrome and Safari). The range APIs return cursors instead of line strings, because the project found that most of the cost of getting lines was allocating strings and the GC that followed.

## Compared with alternatives

The other browser-JavaScript siblings (text-shaper, rustybuzz-wasm, Typr.js) parse fonts and shape glyphs themselves; Pretext does no shaping and instead predicts where the browser will wrap text it paints with its own font engine. Pick Pretext when the browser renders and app code needs heights or line breaks ahead of time; pick text-shaper or a HarfBuzz/Parley stack when you draw glyphs yourself or work outside a browser.

## Integration

| | |
|---|---|
| **Form** | module (npm @chenglou/pretext, ESM only, ships dist JS and TypeScript source; subpath export @chenglou/pretext/rich-inline) |
| **Dependencies** | none at runtime (devDependencies only); needs Canvas 2D measureText via OffscreenCanvas or a DOM canvas, Unicode property escapes, and Intl.Segmenter for Thai, Lao, Khmer, Myanmar and other Southeast Asian scripts |
| **Minimum toolchain** | ES2018+ JavaScript engine with Unicode property escapes (a SyntaxError at load without them); built with TypeScript 6.0.2, developed with Bun; the WebKit profile follows Safari 27 |
| **Platforms** | Browsers: Chrome/Edge (Blink), Firefox (Gecko), Safari 27 (WebKit); unrecognized engines get Blink's rules; works in Web Workers through OffscreenCanvas (emoji correction off there). Harness runs are on macOS (M5 Max) and an iOS simulator; Windows and Android are untested. |
| **Thread safety** | Single-threaded JavaScript. One measurement context and the per-font segment-width cache are module globals per realm, so each worker has its own; setLocale() and clearCache() reset them for all later prepares. Prepared handles are not mutated by layout and copy through structuredClone() or postMessage(). |
| **Drop-in for the baseline** | partial — replaces offsetHeight/getBoundingClientRect reads for paragraph height and line breaks only when the caller passes the same canvas font string, px line height and width as the CSS, and the text stays inside the supported CSS subset; the browser still paints the text. |

## Gotchas

- On main a JSON copy of a handle hangs: JSON.parse(JSON.stringify(prepared)) turns the Uint8Array segmentFlags into an object with no length, and the line APIs never return (CHANGELOG, #340); 0.0.9 tolerated it. Use structuredClone() or postMessage().
- The shared per-font width cache grows with every new segment until clearCache() (TODO.md lists bounding it as open). After a web font finishes loading, call clearCache() and prepare again, or the cached widths stay those of the fallback font; the emoji correction also goes stale when zoom or devicePixelRatio crosses 1.25/1.5, leaving 4-5 px per emoji (#418).
- Overlong words break between graphemes like overflow-wrap: break-word, which is not CSS's default, so set that property on the painted text; an empty string gives lineCount 0 where browsers size one line; a maxWidth that is NaN or undefined lays out as unbounded.
- npm 'latest' is 0.0.9 (2026-09-07). Main carries a large unreleased section (engine ports #340, layout fast path #338, main bundle about 38 KB gzipped against 16 KB in 0.0.9), the maintainer holds releases until an API review, and license notices for the ported browser line-breaking code and engine data are not written yet (TODO.md), so check licensing before vendoring main.

## Known shortcomings

- TypeScript library (language-filter mismatch) that measures and breaks lines without glyph shaping. Tier D: no DOM head-to-head anywhere; the bun bench compares Pretext builds only, early npm READMEs give its own timings only (prepare 17-19 ms, layout 0.09-0.10 ms per 500 texts), and the 500x claim exists only in third-party snippets. Kept as notable (50.7k stars).
- No Pretext-versus-DOM number in the repo (tier D); its own RESEARCH.md figures are against a stand-in Canvas (46-100 us first prepare, 0.4-0.7 us layout, 43-59 ms per 100k-message resize), and the third-party 540x snippet (380 ms versus 0.7 ms on 1,000 paragraphs) sets a cached layout() against cold DOM measurement, which the author called unfair. npm 0.0.9 lags main (main bundle 38 KB gzipped versus 16 KB); a JSON-copied handle hangs the line APIs; the width cache is unbounded until clearCache(); open issues #334 (undercount) and #421 (kerned-word break); no SSR; licence notices for ported engine code and data not yet written (TODO.md).

## Caveats and trade-offs

Tier D: no head-to-head DOM measurement table in README, RESEARCH.md, DEVELOPMENT.md, harness/README.md, pages/ or the early npm READMEs; the bun harness bench compares Pretext builds with each other. The baseline (browser DOM measurement via getBoundingClientRect/offsetHeight and the reflow they force) is the recognisable web-platform incumbent, but not a C/C++ library, and the project is TypeScript, so it does not match the catalog's default C++ language filter. The work differs from the baseline: prepare() still measures segments with the browser's Canvas text measurement, and layout() is arithmetic over cached widths, so a 'faster than DOM' figure compares a cached re-layout with a full style and layout pass. It measures and breaks lines; it does not shape glyphs, so HarfBuzz or FreeType are not comparable baselines. Included as a notable (50.7k stars) tier D entry.

Layout only: the browser still paints the text, and it reads font widths through canvas measureText, so correctness depends on the host font engine; no bidi levels or visual order; not a general CSS inline formatting engine; in a worker small emoji measure too wide in Chrome and Firefox on macOS. JavaScript, not usable from C++.

## Maintenance

Very active (1,511 commits on main, last commit 2026-10-03, 50.7k stars, 38 open issues) and MIT-licensed, but pre-1.0: the published 0.0.9 lags main by a month of engine rewrites, and the maintainer will not release before an API review.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** No Pretext-versus-DOM numbers anywhere in the repo: the README only says it side-steps getBoundingClientRect/offsetHeight reflow, and the bun harness bench (harness/README.md 'Bench') times Pretext builds against each other (base vs candidate), not against DOM measurement. Early npm READMEs (0.0.0-0.0.4) gave only Pretext's own timings with no DOM figure, and the 300-600x / 500x claims exist only in third-party blog and landing-page snippets.
- **Verifier notes:** Kept at D; notable (50.7k stars, 2.8k forks), so not a reject. Metadata from github.com and the npm registry: MIT (LICENSE in the npm tarball), last commit 2026-10-03, not archived. The orchestrator's brief called all three records Rust or WebAssembly, but Pretext is TypeScript and its language field is already right.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/chenglou/pretext>
  - <https://github.com/chenglou/pretext/commits/main>
  - <https://github.com/chenglou/pretext/tree/main/pages>
  - <https://github.com/chenglou/pretext/tree/main/harness>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/README.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/DEVELOPMENT.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/RESEARCH.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/package.json>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/harness/README.md>
  - <https://registry.npmjs.org/@chenglou/pretext>
  - <https://registry.npmjs.org/@chenglou/pretext/-/pretext-0.0.0.tgz>
  - <https://registry.npmjs.org/@chenglou/pretext/-/pretext-0.0.2.tgz>
  - <https://registry.npmjs.org/@chenglou/pretext/-/pretext-0.0.4.tgz>
  - <https://registry.npmjs.org/@chenglou/pretext/-/pretext-0.0.6.tgz>
- **Sources the enricher read:**
  - <https://github.com/chenglou/pretext>
  - <https://github.com/chenglou/pretext/tree/main/src>
  - <https://github.com/chenglou/pretext/tree/main/pages>
  - <https://github.com/chenglou/pretext/issues>
  - <https://github.com/chenglou/pretext/issues/334>
  - <https://github.com/chenglou/pretext/issues/421>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/README.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/DEVELOPMENT.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/RESEARCH.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/AGENTS.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/TODO.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/ENGINE_FOLLOWUPS.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/PLATFORM_BUGS.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/package.json>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/tsconfig.json>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/harness/README.md>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/src/layout.ts>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/src/line-break.ts>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/src/measurement.ts>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/src/prepare.ts>
  - <https://raw.githubusercontent.com/chenglou/pretext/main/src/analysis.ts>
  - <https://registry.npmjs.org/@chenglou/pretext>
  - WebSearch: chenglou pretext benchmark versus DOM measurement getBoundingClientRect (result snippets from pasqualepillitteri.it, hackernoon.com, dev.to, cloudmagazin.com, pretextjs.net; pages not opened)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/chenglou/pretext`) · [data/wave10/enrich/raw/github_com_chenglou_pretext.json](../../../data/wave10/enrich/raw/github_com_chenglou_pretext.json) (enrichment confidence 0.7)

</details>
