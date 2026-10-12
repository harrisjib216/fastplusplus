# fontdue

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0 OR Zlib` · 🟢 active

> Pure-Rust, no_std TrueType/OpenType glyph rasterizer and simple layout; first-party plots show 2.3x-11x lower per-glyph latency than FreeType.

| | |
|---|---|
| **Beats** | FreeType 2 (glyph rasterization, via freetype-rs); also rusttype 0.9.2 and ab_glyph 0.2.3 for rasterization, glyph_brush_layout 0.2.0 for layout |
| **Claimed result** | README says it 'currently has the lowest end to end latency for a font rasterizer' and gives plots only, no numbers. Reading the plotted lines (approximate, derived from page data): TrueType, fontdue about 15 us vs FreeType 2 about 45 us at 10 px/em (about 3x) and about 235 us vs about 545 us at 200 px/em (about 2.3x); OpenType/CFF, fontdue about 12 us vs FreeType about 135 us at 10 px/em (about 11x) and about 220 us vs about 625 us at 200 px/em (about 2.8x). Layout plot: fontdue about 24 us vs glyph_brush_layout about 139 us at 1000 characters (about 5.8x, derived from page data). |
| **Workload** | Time to produce glyph metrics and bitmaps for the 37-character string 'Sphinx of black quartz, judge my vow.' at 10, 20, 40, 80, 160 and 200 px/em, for an Exo2 TrueType (glyf) font and the OpenType (CFF) version of it; separate layout benchmark of 100-1000 Roboto-Regular characters with word wrapping. |
| **Metric** | latency |
| **Adoption** | 1.7k stars |
| **Last commit** | 2026-07-29 |
| **Links** | [repository](https://github.com/mooman219/fontdue) · [benchmark](https://github.com/mooman219/fontdue) |

## Verdict

First-party criterion plots last regenerated in September 2020 (CPU, rustc, flags and FreeType version unstated) time 37 glyphs of a pangram in Exo 2 at 10-200 px: roughly 3x faster than FreeType 2 (via freetype-rs) for TrueType and 11x for CFF at 10 px, 2.3x and 2.8x at 200 px, and 5.8x faster layout than glyph_brush_layout at 1000 characters (chart readings). The comparison favours fontdue: its parsing and flattening run at load outside the timed loop, while every FreeType iteration calls set_char_size and then parses, hints and renders each glyph. In current FreeType source that size request resets the auto-hinter and TrueType size state, and this TTF (no fpgm, 7-byte prep, maxSizeOfInstructions 0) meets ftobjs.c's rule for the auto-hinter. In the layout benchmark glyph_brush_layout does a kerning lookup per glyph pair and returns a new Vec per call, while fontdue reuses its Layout and applies no kerning.

## Use it when

- Rust games, immediate-mode GUIs or wasm apps that rasterize Latin-like glyphs on demand into a glyph atlas, load a font once, and care about per-glyph latency.
- no_std + alloc targets (embedded, wasm) that need TTF/OTF grayscale coverage without linking FreeType or another C library.
- Replacing rusttype or ab_glyph plus glyph_brush_layout where simple left-to-right wrapping without kerning or shaping is acceptable.
- Rendering at one or a few known sizes: building a Font with FontSettings.scale equal to that size reproduces the setup behind the README plots.

## Skip it when

- Complex scripts, running-text ligatures or bidi: there is no shaping (the README points to Cosmic Text) and the layout is self-described as naive.
- Crisp small UI text: no hinting of any kind, and open issues #162 and #168 report blurry text at small sizes.
- Large CJK fonts or tight memory: every mapped glyph is parsed and flattened at load (fast load is a stated non-goal); #164 links a Slint report of a 170 MB memory difference with a 28,987-glyph Chinese font.
- Untrusted font files in a hardened process: a transmute-to-char UB on crafted cmap data (#172) was fixed only in 0.9.4 (2026-07-29), the rasterizer relies on unchecked writes over sanitised geometry, and a fuzzing-harness PR (#17) has been open since April 2020.
- Colour emoji, embedded bitmap strikes, variable-font axes (#121, no API) or a C/C++ codebase: unsupported, and the API is Rust-only with no C ABI.

## How it is fast

Most work is moved to load time: every glyph reachable from cmap (and GSUB when load_substitutions is on) is outlined through ttf-parser, curves are flattened by midpoint subdivision with a triangle-area tolerance tied to FontSettings.scale, lines are re-based to the glyph bounding box with orientation fixed and reciprocal slopes precomputed. Per call it only scales those lines and runs a font-rs style signed-area accumulation rasterizer: each line walks the pixels it crosses (a separate path for vertical lines) and adds coverage deltas into an f32 buffer with unchecked indexing, then one prefix-sum pass converts the buffer to 8-bit coverage, four lanes at a time with SSE shift-adds, truncating converts and saturating packs into an output vector that is not zero-initialised. There is no hinting and no per-call table parsing; char-to-glyph lookup is a hashbrown HashMap.

## Compared with alternatives

Pick fontdue over TiTanF when you want the more widely used pure-Rust rasterizer (TiTanF's own README measures fontdue faster at 10-160 px) and over raw ttf-parser when you need bitmaps, not just outlines; font-rs is the project it was forked from and then rewritten. Pick Parley (or cosmic-text) instead whenever text needs shaping, bidi or real paragraph layout.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | ttf-parser 0.25 (opentype-layout, no-std-float); hashbrown 0.15 by default (or the std feature for std::HashMap); optional rayon 1.10 for the parallel feature (threaded font loading) |
| **Minimum toolchain** | Not documented: no rust-version in Cargo.toml (edition 2018); the default hashbrown 0.15 dependency declares Rust 1.63 |
| **Platforms** | Any target with alloc (no_std); SSE/SSE2 intrinsics on x86 and x86-64 with the default simd feature, scalar fallback elsewhere (aarch64, wasm) |
| **Thread safety** | Font is documented as immutable after creation and owns all its data (Vec and HashMap, no lifetimes), so it can be shared across threads by Rust's auto traits; Layout is mutated through &mut and should be one per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- FontSettings.scale (default 40 px) fixes the curve-flattening tolerance at load: per the doc comment, smaller sizes render slightly slower and larger sizes look worse. The README plots built a separate Font per benchmarked size with scale equal to that size, so a single default Font will not match them at 10 px or 200 px.
- rasterize allocates a new f32 accumulation buffer and a new Vec&lt;u8&gt; on every call; cache results (layout's GlyphRasterConfig is the documented hashable key).
- Kerning is read only from the legacy kern table (GPOS pair kerning is ignored, #161), and the Layout type applies no kerning at all.
- Open #169 reports wrong glyphs for U+0080-U+00FF with Courier, Monaco and Menlo; from_bytes merges codepoints from every cmap subtable without checking whether the subtable is Unicode, which would let a Mac Roman subtable overwrite Latin-1 entries (my reading of src/font.rs; not confirmed by the maintainer). Separately, the name-table decoder (unicode::decode_utf16, called from from_bytes) still builds chars with from_u32_unchecked without validating surrogates: a name string that starts with a low surrogate yields a code point of 0x110000 or more, the same class of UB as #172.

## Known shortcomings

- Rust library (language-filter mismatch). Plots are dated 2020-09-05 and the harness is not like-for-like: the FreeType side renders hinted (LoadFlag::RENDER) and calls set_char_size inside the timed loop, while fontdue's Font::from_bytes parses and flattens every outline outside the timed loop at the exact benchmark size.
- Benchmark asymmetry is larger than the record states: the FreeType loop calls set_char_size on every iteration (resetting the TrueType size state and autohint metrics), and the Exo2 test font has no fpgm, a 7-byte prep and maxSizeOfInstructions 0, so current FreeType routes it to the auto-hinter, meaning the TrueType rows include auto-hinting too (the 2020 FreeType version is unknown); the bench builds a separate Font per size with scale=size; the end-to-end dev/benches/load.rs results were never published; the layout bench pits glyph_brush_layout's per-pair kerning against fontdue's no-kerning layout that reuses its Layout. Soundness, not behind the numbers: unicode::decode_utf16 (name table, reached from Font::from_bytes) still uses from_u32_unchecked, so a leading lone low surrogate yields a code point of 0x110000 or more (undefined behaviour, same class as #172, unfixed in 0.9.4); #169 wrong glyphs for U+0080-U+00FF (cmap subtables merged without an is_unicode check); #164 170 MB for a 28,987-glyph CJK font.

## Caveats and trade-offs

Evidence is three plots in /images with no table, CPU model, rustc version, flags or FreeType version; the numbers in claimed_speedup are read off the charts (approximate; checked against the images). The plots were last updated on 2020-09-05 (commits 'Freetype bench' and 'More data and be more color blind friendly'), when fontdue was far older than today's 0.9.4, and they have not been regenerated since. Benchmark code is public (dev/benches/rasterize.rs and layout.rs, criterion 0.3; the FreeType case only builds with the freetype_benchmark feature, freetype-rs 0.26). The comparison is not apples-to-apples: (1) fontdue::Font::from_bytes, run outside the timed loop, parses and flattens every glyph outline up front, with FontSettings.scale set to the exact benchmarked size, so the timed fontdue loop only rasterizes cached geometry; (2) the FreeType loop calls set_char_size and then load_char with LoadFlag::RENDER for every character, so it parses each glyph (glyf or CFF charstrings), applies FreeType's default hinting and renders, while fontdue does not hint. The large CFF gap at small sizes (about 11x at 10 px/em) is consistent with charstring parsing and hinting landing only on the FreeType side. The layout benchmark compares with glyph_brush_layout 0.2.0 (a Rust library), not a C/C++ incumbent. fontdue began as a fork of font-rs and was rewritten; font-rs is a separate entry.

Rust, no_std, pure-Rust rasterizer and naive layout only; no text shaping (author points to Cosmic Text for that), no hinting. Fonts are fully parsed into custom structures on load (slow, allocating load is an explicit non-goal to fix), so it wins on per-glyph latency, not load time. Not directly usable from C++ without writing an FFI layer.

## Maintenance

Active but solo and slow-moving (Cargo badge 'experimental'): 0.9.4 on 2026-07-29 only fixed soundness issue #172, with 30 open issues and 7 open PRs; 9.2M crates.io downloads (2.3M recent) and an MIT OR Apache-2.0 OR Zlib licence make it easy to adopt in Rust, but it is not copyable into C++ without an FFI layer.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party criterion plots in the README (images/rasterize_glyf.png, rasterize_cff.png, layout.png) against FreeType 2 via freetype-rs, with public bench code (dev/benches/rasterize.rs, dev/benches/layout.rs) but no CPU model, compiler, flags or FreeType version, and the FreeType side does more work per call: C.
- **Verifier notes:** Rust library: language-filter mismatch for a C++ catalog, kept as Rust per the record. Chart readings in claimed_speedup match the images (TrueType 10 px FreeType reads about 45-50 us). Metadata checked on github.com: MIT OR Apache-2.0 OR Zlib, 1.7k stars, 87 forks, not archived, not a fork, last commit 2026-07-29 (active). The orchestrator's hinting concern is confirmed in code, and the bigger asymmetry is that fontdue's glyph parsing and outline flattening happen at font load, outside the timed loop.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/mooman219/fontdue>
  - <https://github.com/mooman219/fontdue/commits>
  - <https://github.com/mooman219/fontdue/tree/master/dev>
  - <https://github.com/mooman219/fontdue/commits/master/images/rasterize_glyf.png>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/README.md>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/dev/Cargo.toml>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/dev/README.md>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/dev/benches/rasterize.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/dev/benches/layout.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/font.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/images/rasterize_glyf.png>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/images/rasterize_cff.png>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/images/layout.png>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/README.md>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/dev/Cargo.toml>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/dev/README.md>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/dev/benches/rasterize.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/dev/benches/layout.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/dev/benches/load.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/dev/resources/fonts/Exo2-Regular.ttf>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/dev/resources/fonts/Exo2-Regular.otf>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/font.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/raster.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/math.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/layout.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/hash.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/unicode/mod.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/platform/mod.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/platform/simd_x86.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/platform/simd_core.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/platform/float/mod.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/platform/float/get_bitmap.rs>
  - <https://github.com/mooman219/fontdue/issues>
  - <https://github.com/mooman219/fontdue/issues/172>
  - <https://github.com/mooman219/fontdue/issues/164>
  - <https://github.com/mooman219/fontdue/issues/169>
  - <https://github.com/mooman219/fontdue/pulls>
  - <https://github.com/slint-ui/slint/issues/7434>
  - <https://crates.io/api/v1/crates/fontdue>
  - <https://crates.io/api/v1/crates/hashbrown/0.15.0>
  - <https://crates.io/api/v1/crates/ttf-parser/0.25.0>
  - <https://gist.github.com/7sDream/0bb194be42b8cb1f1926ca12151c8d76>
  - <https://raw.githubusercontent.com/freetype/freetype/HEAD/src/base/ftobjs.c>
  - <https://raw.githubusercontent.com/freetype/freetype/HEAD/src/truetype/ttdriver.c>
  - <https://raw.githubusercontent.com/freetype/freetype/HEAD/src/truetype/ttobjs.c>
  - <https://raw.githubusercontent.com/freetype/freetype/HEAD/src/truetype/ttgload.c>
  - <https://raw.githubusercontent.com/alexheretic/glyph-brush/HEAD/layout/src/characters.rs>
  - <https://raw.githubusercontent.com/alexheretic/glyph-brush/HEAD/layout/src/lines.rs>
  - <https://raw.githubusercontent.com/alexheretic/glyph-brush/HEAD/layout/src/words.rs>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/mooman219/fontdue`) · [data/wave10/enrich/raw/github_com_mooman219_fontdue.json](../../../data/wave10/enrich/raw/github_com_mooman219_fontdue.json) (enrichment confidence 0.75)

</details>
