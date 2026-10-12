# text-shaper

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `TypeScript` · `MIT` · 🟢 active

> Pure-TypeScript OpenType shaper and rasterizer; about 1.2-1.5x harfbuzzjs (WASM) on simple-script shaping under Bun.

| | |
|---|---|
| **Beats** | harfbuzzjs ^0.4.13 (HarfBuzz compiled to WebAssembly, called from JavaScript), not native HarfBuzz; opentype.js also compared; the rasterization rows compare with FreeType through the freetype2 (node-freetype2) Node native binding |
| **Claimed result** | Like-for-like rows against harfbuzzjs (committed docs/.vitepress/data/benchmarks.json, ops/s, M1 Pro, Bun 1.3.4, derived from page data): English paragraph 1.48x, Russian/Ukrainian/Belarusian 1.18-1.26x, Greek 1.17x, Chinese/Japanese/Korean 1.26-1.31x, Hebrew 1.24x, Arabic 1.04x. The complex-script rows (Hindi 3.6x, Myanmar 10.5x, Thai 1.58x, Khmer 2.25x) compare incomplete shaping (no Indic, Thai, Khmer, Myanmar or USE default features; GSUB ignores per-glyph masks) against full HarfBuzz shaping; the path-extraction 16x and text-to-SVG 5.3-7.1x rows time WeakMap cache hits. README claims vs opentype.js: 4x to 86x. |
| **Workload** | OpenType shaping of word to paragraph texts in Latin, Cyrillic, Greek, Arabic, Hebrew, Hindi, Thai, Khmer, Myanmar and CJK (Noto fonts and texts from the reference/rustybuzz submodule; Cyrillic, Greek and CJK use macOS's Arial Unicode.ttf), plus glyph path extraction, text to SVG and grayscale/LCD rasterization, timed under Bun with a batch timer (bench/utils.ts measure: shaping uses 10 warmup calls, then 3 timed batches of 100 calls). |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro MacBook Pro, 16 GB (meta block of docs/.vitepress/data/benchmarks.json, generated 2025-12-16, 1 run); the README table states no hardware |
| **Compiler and flags** | Bun 1.3.4 runtime running the TypeScript sources via bun test ./bench/ (from benchmarks.json meta and package.json); no build flags apply |
| **Adoption** | 51 stars; used by wiedymi/restty (411 stars) |
| **Last commit** | 2026-07-17 |
| **Links** | [repository](https://github.com/wiedymi/text-shaper) · [benchmark](https://github.com/wiedymi/text-shaper/blob/main/docs/.vitepress/data/benchmarks.json) |

## Verdict

Under Bun 1.3.4 on an M1 Pro (one run, 2025-12-16, 10 warmup calls then 3 batches of 100), shapeInto with reused buffers beat harfbuzzjs ^0.4.13 by about 1.2-1.5x on Latin, Cyrillic, Greek and CJK text. These are the only comparable rows, and output was never compared. The Hindi 3.25x, Khmer 2.25x, Thai 1.58x and Myanmar 10.6x rows time shaping that applies no script-specific GSUB features (only content-detected reordering), so they are not comparable. The path-extraction (50x) and text-to-SVG (5.3-7.1x) rows time WeakMap cache hits for getGlyphPath and pathToSVG against harfbuzzjs regenerating path strings, plus a buffer.json() serialization in the pipeline case.

## Use it when

- Browser, Bun or Node apps that need shaping plus rendering in JavaScript without shipping a HarfBuzz WASM binary: Canvas or WebGL text, glyph atlases, SDF/MSDF, hinted grayscale or LCD bitmaps.
- Latin, Cyrillic, Greek and CJK text with standard features (ccmp, locl, liga, calt, kern, mark). These are the only like-for-like rows, at about 1.2-1.5x harfbuzzjs ops/s on an M1 Pro under Bun.
- Hot loops that shape many short strings with the same font and options, where shapeInto with reused buffers and cached plans avoids per-call allocation.
- Repeated SVG or path output for the same glyphs (icons, labels), where the WeakMap path and SVG caches turn repeated requests into lookups.

## Skip it when

- Arabic, Indic, Thai, Khmer, Myanmar or other complex scripts where output must match HarfBuzz. getDefaultGsubFeatures enables Arabic, Syriac, Mongolian, Tibetan, Ethiopic and Georgian extras but no Indic, Thai, Khmer, Myanmar or USE features. GSUB lookups run in lookup-index order over the whole buffer, and no code in shaper.ts reads the per-glyph masks that setupArabicMasks or setupIndicMasks write. The complex-script tests check glyph counts and mask arrays, not glyph output.
- RTL or mixed-direction text through shape() alone: reversal happens only when options.direction is 'rtl'. UnicodeBuffer.setDirection does not trigger it, and shapeInto does no bidi, despite the README's 'automatically reordered' example. Use processBidi and reorderGlyphs yourself.
- C, C++ or native code: it is TypeScript only, and native HarfBuzz was never measured. The baseline is harfbuzzjs, the WASM build.
- Decisions based on the README table: it does not match the committed results file. The results come from one 2025-12-16 run, and on mixed text with features turned off text-shaper is slower (0.91x).
- CommonJS-only consumers: the package is ESM-only ("type": "module", import-only exports), built for a browser target.

## How it is fast

It is plain JIT-friendly TypeScript with no JS-to-WASM boundary. Shape plans are cached per font, script, language, features and axis coordinates, and shapeInto reuses caller-owned buffers. Each lookup carries a SetDigest filter, so lookups whose coverage cannot match any glyph in the buffer are skipped, and single-subtable delta substitutions take a fast path. In the benchmark, each harfbuzzjs call instead pays for buffer creation, a text copy into WASM memory, segment-property guessing and destroy. Glyph outlines and default SVG strings are memoized in WeakMaps (getGlyphPath, pathToSVG), and optional embedded WASM kernels accelerate some raster paths. Much of the measured lead on complex scripts comes from doing less shaping work, not from faster code.

## Compared with alternatives

Pick it over Typr.js (a parser vs opentype.js) when you need GSUB/GPOS shaping plus hinted rasterization in pure JavaScript. Pick it over rustybuzz-wasm (parity with harfbuzzjs) when you want no WASM and your text is Latin, Cyrillic, Greek or CJK. For correct complex-script output in JavaScript, harfbuzzjs or rustybuzz-wasm remains the safer choice. fontdue, font-rs and TiTanF are Rust rasterizers and do not compete in JS.

## Integration

| | |
|---|---|
| **Form** | module (npm package text-shaper, ESM, 0.1.28 at HEAD) |
| **Dependencies** | none at runtime (harfbuzzjs, opentype.js and freetype2 are dev-only, for the benchmarks) |
| **Minimum toolchain** | an ES-module JavaScript runtime (modern browser, Bun or Node.js); no minimum versions documented; built with Bun and TypeScript 7.0.2 |
| **Platforms** | any JavaScript runtime; optional embedded WebAssembly kernels for some raster paths |
| **Thread safety** | not documented; shape() draws from a module-level GlyphBuffer pool, and the shape-plan, path and SVG caches are per-module state, so each Worker has its own copies |
| **Drop-in for the baseline** | no |

## Gotchas

- shape() returns a GlyphBuffer from a shared pool. Call releaseBuffer() when done, and do not keep using a buffer after releasing it, or the next shape() call will overwrite it.
- Without options.script, the buffer's default script 'Zyyy' selects the font's DFLT (then latn) lookups with only the default feature set. Content-based detection then sets masks that lookups never consult, so pass script and features explicitly.
- getGlyphPath and pathToSVG return cached objects and strings for default options. Mutating a returned GlyphPath corrupts later calls for that glyph.
- Cluster values from addStr are code-point indices starting at startCluster, not UTF-8 or UTF-16 offsets.

## Known shortcomings

- Downgraded to C: TypeScript library whose baseline is harfbuzzjs (WASM), not native HarfBuzz. Several README rows are not valid comparisons: the path-extraction row times a WeakMap cache hit, and the complex-script rows call shapeInto with no script or direction (Zyyy, LTR), so default features only and no RTL shaping. README ratios differ from the committed benchmarks.json (Apple M1 Pro, Bun 1.3.4); the no-features row is 0.91x (slower). Only the Latin, Cyrillic, Greek and CJK rows are like-for-like, at about 1.2-1.5x.
- The complex-script rows (Hindi 3.6x, Myanmar 10.5x, Thai, Khmer) compare incomplete shaping: by code reading there are no Indic, Thai, Khmer, Myanmar or USE default features, GSUB lookups never read the per-glyph masks set by the Arabic and Indic setup, and the complex-script tests check glyph counts only (retier-25 limits the claim to the Latin, Cyrillic, Greek, CJK, Hebrew and Arabic rows at 1.04-1.48x). pathToSVG is WeakMap-cached, so the text-to-SVG 5.3-7.1x rows time cache hits while the harfbuzzjs side pays buffer.json(); shape() ignores buffer direction and the README's bidi auto-reorder claim is not implemented.

## Caveats and trade-offs

Baseline is harfbuzzjs, the WebAssembly build of HarfBuzz driven from JavaScript, not native HarfBuzz; each timed harfbuzzjs call creates a buffer, copies the text into WASM memory, guesses segment properties, shapes and destroys the buffer, while text-shaper reuses its buffers (shapeInto). Several headline rows time different work: (1) Path extraction: getGlyphPath caches paths per font and glyph in a WeakMap (src/render/path.ts), so after warmup the text-shaper side times a cache lookup while harfbuzzjs glyphToPath rebuilds an SVG path string on every call. (2) Complex scripts: bench/shaping.test.ts calls shapeInto without script or direction, and UnicodeBuffer.addStr never sets them (script defaults to 'Zyyy', direction LTR), so the cached shape plan enables only the default features (ccmp, locl, rlig, rclt, calt, liga, kern, mark, mkmk; src/shaper/shape-plan.ts) and no RTL reversal runs. Arabic joining forms and Indic/Myanmar/Khmer script features from the fonts are therefore not applied on the text-shaper side, while harfbuzzjs guesses script and direction and runs the full script shaper; the Arabic, Hebrew, Hindi, Khmer, Thai and Myanmar ratios compare unequal work, and the output is not checked against HarfBuzz. (3) Rasterization vs FreeType: rasterizeGlyph defaults to hinting off and reuses the cached glyph path (hinted runs reuse a hinted-glyph cache), while FreeType's loadGlyph({render: true}) loads, hints with default flags and renders every call through a Node native binding. The README table does not match the committed results file (e.g. path extraction 16x vs 50x; text to SVG 1.2-1.5x vs 5.3-7.1x; Arabic 1.2x vs 1.04x), so its source run is unknown; 'outperforms across all benchmarks' is contradicted by the no-features row (0.91x). The results file is a single run from 2025-12-16, while the bench code read here is the 2026-07 HEAD. Bench fonts and texts come from the reference/rustybuzz git submodule (harfbuzz/rustybuzz @ 51d99b8), so they are public; the Cyrillic, Greek and CJK cases need macOS's /System/Library/Fonts/Supplemental/Arial Unicode.ttf.

Pure TypeScript (zero dependencies, runs in browsers and Bun/Node), so not usable from C++. Also does TrueType hinting and FreeType-style or libass-style rasterization. Young project (npm 0.1.x).

## Maintenance

Active (version 0.1.28, last commit 2026-07-17, MIT, 51 stars, 2 closed issues and 0 open). It is a young solo project, fine to vendor for JavaScript rendering of simple scripts, but not a verified HarfBuzz substitute for complex scripts.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party numbers: a README table plus a committed results file (docs/.vitepress/data/benchmarks.json: 1 run, MacBook Pro M1 Pro, Bun 1.3.4) from public bench code (bench/shaping.test.ts, bench/path.test.ts, bench/raster.test.ts, bench/utils.ts). The baseline is the WebAssembly build of HarfBuzz, and several headline rows time different work, so the claim is overstated: C.
- **Verifier notes:** TypeScript library vs the WASM build of HarfBuzz: language-filter mismatch and not a native-HarfBuzz comparison. Downgraded for an overstated claim: the 16x path-extraction row times a cache hit and the complex-script rows run without script/direction (default features only), so only the Latin/Cyrillic/Greek/CJK rows (about 1.2-1.5x vs harfbuzzjs) are like-for-like. The orchestrator may weigh a reject for the invalid rows; the record survives on the comparable rows. Metadata checked on github.com: MIT, 51 stars, 4 forks, not archived, not a fork, last commit 2026-07-17 (active); the restty usage figure was not checked.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `hardware`, `compiler_and_flags`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/wiedymi/text-shaper>
  - <https://github.com/wiedymi/text-shaper/commits>
  - <https://github.com/wiedymi/text-shaper/tree/main/bench>
  - <https://github.com/wiedymi/text-shaper/tree/main/src>
  - <https://github.com/wiedymi/text-shaper/tree/main/src/raster>
  - <https://github.com/wiedymi/text-shaper/tree/main/src/render>
  - <https://github.com/wiedymi/text-shaper/tree/main/src/shaper>
  - <https://github.com/wiedymi/text-shaper/tree/main/src/buffer>
  - <https://github.com/wiedymi/text-shaper/tree/main/reference>
  - <https://github.com/wiedymi/text-shaper/blob/main/docs/.vitepress/data/benchmarks.json>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/README.md>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/package.json>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/bench/shaping.test.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/bench/utils.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/bench/path.test.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/bench/cjk.test.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/bench/raster.test.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/bench/caching.test.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/scripts/update-benchmarks.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/docs/.vitepress/data/benchmarks.json>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/src/render/path.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/src/raster/rasterize.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/src/shaper/shaper.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/src/shaper/shape-plan.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/src/buffer/unicode-buffer.ts>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/README.md>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/package.json>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/bench/shaping.test.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/bench/utils.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/bench/path.test.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/bench/raster.test.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/docs/.vitepress/data/benchmarks.json>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/src/index.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/src/shaper/shaper.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/src/shaper/shape-plan.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/src/shaper/complex/arabic.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/src/buffer/unicode-buffer.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/src/render/path.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/tests/shaper/shaper.test.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/tests/shaper/complex/indic.test.ts>
  - <https://raw.githubusercontent.com/wiedymi/text-shaper/HEAD/tests/shaper/complex/arabic.test.ts>
  - <https://github.com/wiedymi/text-shaper/tree/main/tests>
  - <https://github.com/wiedymi/text-shaper/tree/main/tests/shaper>
  - <https://github.com/wiedymi/text-shaper/tree/main/tests/shaper/complex>
  - <https://github.com/wiedymi/text-shaper/issues?q=is%3Aissue>
  - <https://github.com/wiedymi/text-shaper/commits/main>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/wiedymi/text-shaper`) · [data/wave10/enrich/raw/github_com_wiedymi_text_shaper.json](../../../data/wave10/enrich/raw/github_com_wiedymi_text_shaper.json) (enrichment confidence 0.75)

</details>
