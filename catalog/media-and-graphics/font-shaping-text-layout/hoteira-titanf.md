# TiTanF

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Zero-dependency no_std Rust TrueType rasterizer; 1.5-3.5x faster than RustType and ab_glyph, slower than Fontdue below 200px.

| | |
|---|---|
| **Beats** | RustType and ab_glyph (long-standing, widely used pure-Rust glyph rasterizers); Fontdue, another pure-Rust rasterizer, also measured and faster at 10-160px; FreeType and HarfBuzz are not measured |
| **Claimed result** | README criterion medians, TiTanF / Fontdue / RustType / ab_glyph: 10px 71.0 us / 54.3 / 245.6 / 222.6; 20px 123.2 us / 83.7 / 224.2 / 279.4; 40px 237.3 us / 178.2 / 356.2 / 485.0; 80px 495.4 us / 401.7 / 966.4 / 821.1; 160px 1.08 ms / 1.02 / 2.29 / 2.16; 200px 1.45 ms / 1.60 / 3.21 / 3.07; 320px 3.13 ms / 4.02 / 7.27 / 6.77. TiTanF is 1.5x-3.5x faster than RustType and 1.7x-3.1x faster than ab_glyph across sizes (derived from page data); Fontdue is faster than TiTanF from 10px through 160px, and TiTanF leads it only at 200px (1.1x) and 320px (1.3x) (derived from page data). |
| **Workload** | Rasterizing every character of one 106-character string (30 CJK ideographs plus A-Z, a-z, 0-9 and 14 ASCII punctuation marks; the README says 84 characters, but the MESSAGE constant in benches/rasterize_bench.rs has 106, derived from page data) with NotoSansSC-Medium.ttf at 10, 20, 40, 80, 160, 200 and 320 px into owned coverage bitmaps, glyph cache off (get_char::&lt;false&gt;), criterion medians with 4 s measurement time per case. |
| **Metric** | latency |
| **Compiler and flags** | cargo bench with the default bench profile (release, opt-level 3); Cargo.toml has no [profile] section and no RUSTFLAGS or target-cpu setting is given, so the rustc version and the SIMD level actually compiled in are unstated |
| **Adoption** | 3 stars, 0 forks; crates.io titanf 3.0.0 with 2,559 total downloads (199 recent) as of 2026-10-03 |
| **Last commit** | 2026-07-08 |
| **Links** | [repository](https://github.com/Hoteira/titanf) · [benchmark](https://github.com/Hoteira/titanf) |

## Verdict

These are first-party criterion medians (cargo bench, default bench profile, no RUSTFLAGS, so a baseline SSE2 x86-64 build; CPU and rustc unstated) for rasterizing a 106-character string (30 CJK, 76 ASCII; the README says 84) from NotoSansSC-Medium.ttf, which is not in the repo, at seven sizes with the cache off and every library's font load outside the timed loop. TiTanF is 1.5-3.5x faster than RustType 0.9.3 and 1.7-3.1x faster than ab_glyph 0.2.32. Against fontdue 0.9.3, with FontSettings.scale set to each size, it is 1.06-1.47x slower up to 160 px and 1.10x and 1.28x faster at 200 and 320 px (derived from page data). The table was committed in 0c4078c (2026-07-08), together with the string change and after the restructuring commit, so it matches current code. The README's quality argument that 'Fontdue reuses geometry tessellated for 40px' describes Fontdue's default scale of 40, not the benchmarked setup. No output-equivalence or quality check is run, and TiTanF skips zeroing its output buffer while RustType and ab_glyph allocate zeroed ones.

## Use it when

- Kernels, bootloaders and other no_std + alloc targets that need anti-aliased TrueType text with zero crate dependencies (Fontdue pulls in ttf-parser 0.25).
- Large glyphs: at 200 px and 320 px it beats Fontdue (configured for each size) by 1.10x and 1.28x, and RustType or ab_glyph by 2.1-2.3x (derived from page data).
- Replacing RustType or ab_glyph for per-glyph bitmap rasterization when a one-off whole-font load cost is acceptable: 1.5-3.5x faster per call in the first-party bench.
- Fixed character sets mapped by cmap, such as consoles, terminals and UI labels, where the built-in (glyph id, size) cache of up to 4096 bitmaps absorbs repeats.

## Skip it when

- Body text at 10-160 px: Fontdue is 1.06-1.47x faster in the same bench (54.3 vs 71.0 us at 10 px, 83.7 vs 123.2 us at 20 px).
- CFF/CFF2 .otf fonts, variable fonts, colour or bitmap glyphs, or font collections: only glyf outlines are parsed, and load_font returns TableNotFound("glyf") without that table.
- Shaped or complex-script text: there is no GSUB, and only cmap-reachable glyphs are preprocessed, so get_indexed returns the .notdef glyph for ligature and contextual-form ids that a shaper produces, despite its doc comment suggesting shaper use.
- Supplementary-plane characters (emoji, CJK Extension B) in fonts whose cmap lists a Unicode-platform BMP format 4 subtable before the format 12 one: load_cmap_subtables keeps only one subtable, ranks every platform-0 entry first and sorts stably, so non-BMP code points can fall back to .notdef.
- Fast startup or tight memory with large CJK fonts: every mapped glyph is preprocessed at load (tens of thousands for NotoSansSC), and neither load time nor memory is reported. It is a single-author project with 3 stars and no issues ever filed.

## How it is fast

load_font converts every cmap-mapped glyph once into raster-ready primitives: vertical lines, sloped lines with precomputed reciprocals, and quadratic Beziers split at their extrema into monotonic pieces with precomputed polynomial coefficients. Per call, scaling to pixel space is one SSE multiply-add per primitive. A grid-walk (DDA) cell traversal deposits exact signed-area coverage into a float accumulation buffer, solving the quadratic with one sqrtss at each pixel-boundary crossing instead of flattening curves. A span-limited SSE prefix sum per row then turns the coverage into alpha bytes and re-zeroes only the touched spans, so the buffer never needs a separate clear. The README advertises SSE2/AVX2 and NEON, but the code has only SSE intrinsics on x86 and scalar fallbacks elsewhere.

## Compared with alternatives

Pick it over fontdue only for zero dependencies, mostly large sizes (200 px and up), or exact curves at sizes far from one preset scale. Fontdue is faster from 10 to 160 px, also no_std, and far more used. font-rs has no benchmark numbers in its repo, and ttf-parser only parses outlines, so neither replaces a rasterizer the way this does.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (fontdue 0.9.3, ab_glyph 0.2.32, rusttype 0.9.3 and criterion 0.7 are dev-dependencies for the bench only); optional std feature switches BTreeMap to HashMap and uses std float methods |
| **Minimum toolchain** | Rust edition 2024 with if-let chains (fastmap.rs), which implies rustc 1.88+; no rust-version is declared |
| **Platforms** | x86-64 with SSE intrinsics compiled in unconditionally (no AVX2 code and no runtime dispatch); aarch64 and other targets use scalar fallbacks (including a three-step Newton sqrt), with no NEON code; 32-bit x86 appears not to compile, because geometry/simd.rs imports core::arch::x86_64 under cfg(target_arch = "x86") |
| **Thread safety** | get_char and get_indexed take &mut self, because the bitmap cache and a single reusable coverage buffer live inside TrueTypeFont, so use one font object per thread. TrueTypeFont does not implement Clone, so each thread re-runs load_font. Otherwise not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Outline bugs found by reading the code (not run): (a) a composite glyph whose component is itself a composite loses the outer component's offset and scale, because load_from_parent recurses without passing the transform, and point-matched components (ARGS_ARE_XY_VALUES clear) get no offset at all; (b) a contour that starts with three or more off-curve points drops the curve through its second point, because preprocess() stores it in last_off_curve but the off-curve branch never reads it. The tests use only a synthetic square-glyph font, with no reference-image comparison.
- Metrics are integers: advance_width is truncated to usize and left_side_bearing to isize, so layouts built on them accumulate rounding error, and the baseline comes from the glyf header's yMax rather than the computed bounds.
- The cache (get_char::&lt;true&gt;) keys on the glyph id and the exact f32 bit pattern of the size, flushes completely at 4096 entries, and returns a cloned Vec on every hit. The default dpi is 72, so size is in pixels, and set_dpi flushes the cache.
- Beyond the SIMD intrinsics, the code has other unsafe: to_bitmap calls Vec::set_len on uninitialized bytes (clippy::uninit_vec is silenced), and the rasterizer's coverage writes use get_unchecked_mut, protected only by debug_assert and coordinate clamping.

## Known shortcomings

- Rust font rasterizer (language-filter mismatch) with no FreeType baseline: its own criterion bench (benches/rasterize_bench.rs) against RustType, ab_glyph and Fontdue gives 1.5x-3.5x and 1.7x-3.1x (derived), no CPU or rustc stated; the bench font NotoSansSC-Medium.ttf is gitignored and absent, the string is 106 characters not 84, the whole-font preprocessing runs outside the timed loop, and Fontdue is faster from 10 to 160 px.
- README table is from commit 0c4078c (2026-07-08) and matches the current bench, but the string is 106 characters (not 84); the README's claim that Fontdue reuses a 40 px tessellation is wrong for the bench (scale is set per size); the README says AVX2 and NEON but the code has SSE only with scalar elsewhere, and i686 probably does not compile. Library bugs from code reading (not run, not behind the simple bench glyphs): nested composites drop the outer offset and scale (points.rs load_from_parent); contours starting with three or more off-curve points lose the curve through the second point (lines.rs preprocess); GSUB-only glyph ids render .notdef; a single cmap subtable can drop non-BMP; integer metrics; Vec::set_len on uninitialised memory.

## Caveats and trade-offs

First-party criterion benchmark (benches/rasterize_bench.rs, adapted from Fontdue's bench) with no CPU model, rustc version or run conditions stated, and one font and one string. load_font eagerly converts every glyph of the font into raster-ready geometry outside the timed loop, while RustType and ab_glyph parse each outline inside it, so the per-call times exclude TiTanF's front-loaded parse cost (Fontdue also preprocesses at load). The bench font NotoSansSC-Medium.ttf is gitignored (\*.ttf) and absent from the repo, so cargo bench does not build from a fresh clone and the font version is unstated. The README says 84 characters; the bench string has 106. Fontdue beats TiTanF from 10px to 160px. Baselines are pure-Rust rasterizers, not FreeType; no claim against FreeType or HarfBuzz exists. Tiny new project (3 stars, first crate release 2025-10-16).

Dependency-free no_std Rust TrueType rasterizer; scales better than Fontdue for large glyphs and loses to it for small sizes; TrueType outlines only as far as the README states, with no shaping or hinting.

## Maintenance

Active single-author crate (115 commits, last 2026-07-08, v3.0.0 on crates.io with about 2.6k downloads), MIT and small enough to vendor, but no issues filed and no CI visible; treat the composite-glyph and off-curve-start parsing bugs as open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table matches a first-party criterion benchmark in benches/rasterize_bench.rs (TiTanF, Fontdue, RustType, ab_glyph on the same font, string and sizes), but no CPU model, rustc version or RUSTFLAGS are stated and the bench font is not in the repo, so it falls short of A.
- **Verifier notes:** RustType and ab_glyph are recognisable incumbents within Rust but not the category's C/C++ incumbents, so baseline_in_list stays false; language is Rust (not in the correctable list, set in corrections for the orchestrator to apply as an override). Same glyphs, sizes and output type for all four libraries, but the work split differs (eager whole-font preprocessing at load for TiTanF).
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/README.md>
  - <https://github.com/Hoteira/titanf>
  - <https://github.com/Hoteira/titanf/tree/master/benches>
  - <https://github.com/Hoteira/titanf/commits/master>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/benches/rasterize_bench.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/font.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/render.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/NotoSansSC-Medium.ttf>
  - <https://crates.io/api/v1/crates/titanf>
- **Sources the enricher read:**
  - <https://github.com/Hoteira/titanf>
  - <https://github.com/Hoteira/titanf/tree/master/src>
  - <https://github.com/Hoteira/titanf/tree/master/tests>
  - <https://github.com/Hoteira/titanf/commits/master>
  - <https://github.com/Hoteira/titanf/commit/0c4078c5404bad166b9a8fb9f03173b8d6cad48a>
  - <https://github.com/Hoteira/titanf/commit/43e712f54912bfdec2957007d707be2a0e96509a>
  - <https://github.com/Hoteira/titanf/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/README.md>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/benches/rasterize_bench.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/font.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/render.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/cache.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/fastmap.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/rasterizer/mod.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/rasterizer/dda.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/geometry/mod.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/geometry/simd.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/geometry/lines.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/geometry/points.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/tables/mod.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/tables/glyf.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/tables/cmap.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/src/tables/hmtx.rs>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/tests/font_tests.rs>
  - <https://crates.io/api/v1/crates/titanf>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/src/font.rs>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/Cargo.toml>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/hoteira/titanf`) · [data/wave10/enrich/raw/github_com_hoteira_titanf.json](../../../data/wave10/enrich/raw/github_com_hoteira_titanf.json) (enrichment confidence 0.7)

</details>
