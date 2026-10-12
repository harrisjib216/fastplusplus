# Typr.js

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript` · `MIT` · 🟡 stale

> Small browser JavaScript font parser (TTF/OTF/TTC/WOFF) that claims 2x-5x faster parsing than opentype.js, largely by parsing less up front.

| | |
|---|---|
| **Beats** | opentype.js (the widely used JavaScript OpenType font parser, a recognisable incumbent in JavaScript); HarfBuzz and FreeType are not measured |
| **Claimed result** | README: 'ultra fast (2x to 5x faster parsing than opentype.js)' |
| **Workload** | Parsing TTF/OTF/TTC/WOFF font files into a JavaScript font object, compared with opentype.js; the README gives no corpus, machine or timing table. |
| **Metric** | throughput |
| **Adoption** | about 1.0k stars, 80 forks; main text engine of the Photopea image editor (README) |
| **Last commit** | 2025-08-28 |
| **Links** | [repository](https://github.com/photopea/Typr.js) · [benchmark](https://github.com/photopea/Typr.js/) |

## Verdict

Nothing measurable is published. The README has said 'ultra fast (2x to 5x faster parsing than opentype.js)' since at least May 2020 (when it also gave the size as 70 kB), with no benchmark code, font set, opentype.js version, JavaScript engine or machine. Reading both parsers shows the comparison is not like-for-like: Typr defers glyph decoding, skips GPOS and GDEF and keeps only GSUB feature tags, whereas current opentype.js parses GDEF, GPOS and GSUB eagerly.

## Use it when

- Browser apps that need glyph outlines from user-supplied fonts to draw on Canvas or export as SVG paths: text-as-paths in an image or vector editor (the README says it is Photopea's main text engine), font previews and thumbnails.
- Opening many fonts quickly just to read metadata or cmap coverage (font pickers, family/instance lists from fvar, glyph-coverage checks), where lazy outlines and the skipped layout tables keep load cheap.
- Variable and colour fonts in the browser without a native dependency: outlines interpolated through gvar, avar and HVAR, COLR/CPAL layers, SVG glyphs, and CBDT/sbix PNG glyphs (with UPNG.js loaded).
- Pages where script size matters: three plain script files (README: 110 kB unminified, 4x smaller than opentype.js) with no build step. You can pair it with a HarfBuzz WASM build via Typr.U.initHB when complex scripts need real shaping.

## Skip it when

- Shaping text with the library alone: in the current code, Typr.U.shape maps each code point to one glyph and adds only legacy 'kern' table pairs (found by linear indexOf) and HVAR advances. It applies no GSUB ligatures, no GPOS kerning or mark positioning, and ignores the fts and ltr parameters, so fonts that keep kerning only in GPOS get none. This also contradicts the catalogue record's tradeoff that shape covers ligatures. For real shaping use shapeHB with a HarfBuzz WASM file (the README links one hosted on photopea.com; it is not in the repo) or a dedicated JavaScript shaper.
- Node.js, Deno or Web Workers without shims: src/Typr.js reads window['TextDecoder'] when it loads (Typr.B._tdec) and has no module export, so it throws a ReferenceError where window is undefined. The npm package named typr.js is a third-party snapshot from January 2018 (version 1.0.0), not this repository.
- WOFF2 fonts, or WOFF 1.0 without pako: WOFF tables are inflated through a global pako object that the repo does not ship. WOFF2 is unsupported, and because its 'wOF2' signature starts with the same 0x77 byte as WOFF, it is routed into the WOFF 1.0 converter and fails (inferred from the source).
- Untrusted or malformed fonts where you need clean failures: the byte readers have their bounds checks commented out, so out-of-range reads yield undefined/NaN instead of errors, failures are thrown as bare strings (for example 'unknown cmap table format'), and issue #55 (October 2024, no reply) reports browser crashes when loading the genseki-font TTC files.
- When you need a measured speed advantage or a font writer: the 2x-5x figure has no benchmark behind it, and opentype.js can also write fonts.

## How it is fast

The parser is a set of hand-written table readers over one Uint8Array with manual big-endian byte reads. It also does much less work at load time. The glyf table becomes an array of nulls, and each glyph is decoded on the first glyphToPath call and memoised in font.glyf. CFF CharStrings and subroutines become zero-copy Uint8Array views that are interpreted only when a path is requested. GPOS and GDEF are not parsed at all, and GSUB is reduced to a set of feature tags. By contrast, current opentype.js master parses GDEF, GPOS and GSUB and builds its kerning pairs inside its parse routine. Tables shared between TTC members are parsed once (keyed by offset). With no benchmark in the repo, it is unknown how much of the claimed gap comes from leaner code and how much from skipped tables.

## Compared with alternatives

Pick Typr.js for in-browser font loading and glyph outlines (including variable and colour fonts) from a tiny dependency-free script. For shaping in JavaScript, the catalogued text-shaper and rustybuzz-wasm were actually measured against harfbuzzjs and opentype.js; in native or Rust code, ttf-parser covers outline parsing with published numbers against FreeType.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for TTF/OTF/TTC; global pako for WOFF 1.0; global UPNG (UPNG.js) for CBDT/sbix PNG glyphs; a HarfBuzz WASM build plus fetch and WebAssembly for Typr.U.shapeHB |
| **Minimum toolchain** | Not documented. The code needs an ES2015 engine (typed arrays, String.codePointAt) and a global window object; the variable-font naming path calls String.replaceAll (ES2021); shapeHB needs fetch, WebAssembly and TextEncoder. |
| **Platforms** | Web browsers (main thread). Node.js, Deno and Workers work only with a window shim. readUint/readInt reassemble bytes through a shared typed-array scratch buffer, which assumes a little-endian host (true of all mainstream JS engines). |
| **Thread safety** | Not documented. JavaScript runs one thread per realm, but Typr.B shares one 8-byte scratch buffer, parsed glyphs are memoised into the font object, and shapeHB keeps a single cached HarfBuzz face in closure state. |
| **Drop-in for the baseline** | no |

## Gotchas

- Typr.parse ends with an uncommented console.log(out) (src/Typr.js line 126 on gh-pages), so every parse logs the parsed fonts; while DevTools is open those objects, each holding the whole font buffer, stay reachable. The name-table parser also logs when it meets unknown encodings.
- For a variable font, Typr.parse returns one object per fvar named instance, not one per file, and a font whose fvar lists zero named instances yields an empty array (inferred from readFONT), so Typr.parse(buf)[0] is undefined.
- Typr.U.shape sets the cluster index cl to the glyph's position in the glyph list, not its UTF-16 offset, so cl drifts from the string index after any astral character such as an emoji. shapeHB caches its HarfBuzz face by postScriptName, so two different font files that share a PostScript name reuse the first one's face.
- Lazy glyph decoding re-scans the table directory (findTable) for each glyph and re-parses empty glyphs on every call. Memory grows as glyphs are drawn because parsed glyphs are cached in font.glyf and never evicted.

## Known shortcomings

- JavaScript (language-filter mismatch). Only a README line ('2x to 5x faster parsing than opentype.js') with no benchmark code, corpus or machine; Typr.parse is lazy on glyf and skips GPOS and GDEF, so the parsing work is not equal. Last commit 2025-08-28.
- The speed claim is unchanged since at least May 2020 with no benchmark, and the comparison is not like-for-like: Typr skips GPOS and GDEF, reads only GSUB tags and parses glyf lazily while opentype.js master parses GDEF, GPOS and GSUB eagerly. The record's trade-off text is wrong: Typr.U.shape has no GSUB ligatures and no GPOS, only legacy kern pairs, and ignores fts and ltr. console.log(out) runs on every parse; the module reads window at load so breaks in Node and Workers; WOFF2 is sent down the WOFF1 path and WOFF needs a global pako; a variable font with 0 named instances returns []; the npm typr.js package is a third-party 2018 snapshot.

## Caveats and trade-offs

First-party one-line README claim with no benchmark code, font corpus, opentype.js version, JavaScript engine, machine or timing numbers anywhere in the repo (demo/ holds three fonts and two HTML pages with no timing code), so it cannot be reproduced. Parsing depth is not shown to be equivalent: Typr.parse fills glyf with null placeholders and parses each glyph lazily via _parseGlyf, and GPOS and GDEF are commented out of its table parser list, so part of the gap may be less work done at parse time. The baseline is opentype.js, not HarfBuzz or FreeType, and parse speed says nothing about shaping or rasterization. Recent commits are mostly 'Add files via upload'; last commit 2025-08-28, more than 12 months ago.

Static-function API over plain JavaScript objects with no classes; shaping (Typr.U.shape) covers ligatures, kerning and variable-font axes but is much less complete than HarfBuzz; 110 kB unminified, 4x smaller than opentype.js.

## Maintenance

Stale: the last commit is 2025-08-28 ('Add files via upload' on the gh-pages default branch), there are no tags, releases or package.json, and none of the 8 open issues has a maintainer reply. It is MIT-licensed, three files to vendor, and per the README still Photopea's main text engine.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The only evidence is the first-party README line '2x to 5x faster parsing than opentype.js'; the repo (src/, demo/, index.html) contains no benchmark code, corpus, machine or timing table, so it is a number without methodology.
- **Verifier notes:** opentype.js is a recognisable JavaScript incumbent but not HarfBuzz or FreeType, so baseline_in_list stays false; language JavaScript set in corrections for the orchestrator to apply as an override. maintenance_status moved from active to stale because the last commit (2025-08-28, gh-pages default branch) is over 12 months before today. One WebSearch found only copies of the README claim, no independent measurement.
- **Fields the verifier corrected:** `maintenance_status`, `stars_or_usage`, `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/photopea/Typr.js/HEAD/README.md>
  - <https://github.com/photopea/Typr.js>
  - <https://github.com/photopea/Typr.js/commits/gh-pages>
  - <https://github.com/photopea/Typr.js/tree/gh-pages/demo>
  - <https://github.com/photopea/Typr.js/tree/gh-pages/src>
  - <https://raw.githubusercontent.com/photopea/Typr.js/gh-pages/demo/index.html>
  - <https://raw.githubusercontent.com/photopea/Typr.js/gh-pages/index.html>
  - <https://raw.githubusercontent.com/photopea/Typr.js/gh-pages/demo/photopea.html>
  - <https://raw.githubusercontent.com/photopea/Typr.js/gh-pages/src/Typr.js>
  - <https://github.com/photopea/Typr.js/issues?q=is%3Aissue+opentype>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/photopea/Typr.js/gh-pages/README.md>
  - <https://raw.githubusercontent.com/photopea/Typr.js/3c17ea8/README.md>
  - <https://raw.githubusercontent.com/photopea/Typr.js/gh-pages/src/Typr.js>
  - <https://raw.githubusercontent.com/photopea/Typr.js/gh-pages/src/Typr.U.js>
  - <https://raw.githubusercontent.com/photopea/Typr.js/gh-pages/src/Typr.U.SVG.js>
  - <https://raw.githubusercontent.com/photopea/Typr.js/gh-pages/index.html>
  - <https://raw.githubusercontent.com/photopea/Typr.js/gh-pages/demo/index.html>
  - <https://raw.githubusercontent.com/photopea/Typr.js/gh-pages/package.json>
  - <https://github.com/photopea/Typr.js/tree/gh-pages/src>
  - <https://github.com/photopea/Typr.js/commits/gh-pages>
  - <https://github.com/photopea/Typr.js/commits/gh-pages/README.md>
  - <https://github.com/photopea/Typr.js/issues>
  - <https://github.com/photopea/Typr.js/issues/55>
  - <https://github.com/photopea/Typr.js/issues/54>
  - <https://raw.githubusercontent.com/opentypejs/opentype.js/master/src/opentype.mjs>
  - <https://registry.npmjs.org/typr.js>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/photopea/typr.js`) · [data/wave10/enrich/raw/github_com_photopea_typr_js.json](../../../data/wave10/enrich/raw/github_com_photopea_typr_js.json) (enrichment confidence 0.8)

</details>
