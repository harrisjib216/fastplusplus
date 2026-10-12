# Fontations (skrifa / read-fonts)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Google's memory-safe Rust OpenType stack (read-fonts, skrifa); mostly 1.1-1.6x slower than HarfBuzz's own OT font functions.

| | |
|---|---|
| **Beats** | HarfBuzz OT font backend (hb-ot font functions: cmap lookup, advances, extents, outline drawing) |
| **Claimed result** | Mixed and mostly slower; Fontations is not faster than HarfBuzz OT overall. Issue #2196 (body revised 2026-10-04, HarfBuzz 692a0aa30e vs Fontations 08bfef45) geometric means of Fontations/OT time (above 1 means Fontations is slower): nominal glyphs 1.52x, horizontal advances 1.39x, vertical advances 1.10x, vertical origins 1.62x, glyph extents 1.33x, drawing 1.56x, paint 1.16x, load face and shape 1.06x (derived from page data). Fontations is faster in 10 of 96 rows, mainly varied Roboto Flex vertical origins and glyph extents and Adobe CFF2 glyph extents. Worst row: Adobe VF Prototype nominal glyphs 3.50x slower. The earlier revision (eff2d6b9 / ec902bd2) had geomeans 1.53x, 1.39x, 1.11x, 1.58x, 1.29x, 1.51x, 1.26x and 1.05x with Noto Serif Myanmar nominal glyphs 3.12x as the worst row. No FreeType library timing is on the page. |
| **Workload** | HarfBuzz perf/benchmark-font (Google Benchmark) run with the Fontations backend versus the native OT backend on Roboto, Roboto Flex, Source Sans Pro, Adobe VF Prototype, Source Serif Variable, Comfortaa, Noto Nastaliq Urdu and Noto Serif Myanmar, default and wght=500 instances: nominal glyph lookup, horizontal and vertical advances, vertical origins, glyph extents, drawing, painting, load face and shape. |
| **Metric** | throughput |
| **Hardware** | Linux x86_64, AMD Ryzen 9 5900X (12 cores / 24 threads), pinned to CPU 6, seven repetitions, CPU medians |
| **Compiler and flags** | Clang 21.1.7 for HarfBuzz, meson --buildtype=release -Db_lto=true -Dfontations=enabled -Dbenchmark=enabled; Rust 1.94.0-nightly (2025-12-20), release profile, fat LTO, one codegen unit; HarfBuzz commit 692a0aa30e, Fontations commit 08bfef45 (revised 2026-10-04; the earlier revision measured eff2d6b995e0b45e3224079640457fa524c411b9 and ec902bd22b5b045e0178bcc3010604e36a7b8342); run as taskset -c 6 b/perf/benchmark-font --benchmark_filter="/(fontations\|ot)\$" --benchmark_min_time=0.05s --benchmark_repetitions=7. Harness skews against Fontations: the Rust std is built with optimize_for_size and forced frame pointers, and there is no cross-language LTO. |
| **Adoption** | 835 stars; skrifa is the Rust font stack Google builds to replace FreeType in its applications (README) |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/googlefonts/fontations) · [benchmark](https://github.com/googlefonts/fontations/issues/2196) |

## Verdict

HarfBuzz maintainer behdad's issue #2196 runs HarfBuzz's perf/benchmark-font with the 'fontations' and 'ot' backends doing the same hb_font calls on eight test fonts (default and wght=500), Clang 21.1.7 -O3 LTO and Rust 1.94.0-nightly fat LTO, pinned to one core of a Ryzen 9 5900X, CPU medians of seven runs. The page was revised on 2026-10-04 and now cites HarfBuzz 692a0aa30e and Fontations 08bfef45 rather than the eff2d6b9/ec902bd2 commits in the record; its numbers give Fontations/OT geometric means of 1.52x nominal glyphs, 1.39x horizontal advances, 1.10x vertical advances, 1.62x vertical origins, 1.33x extents, 1.56x drawing, 1.16x paint and 1.06x load-and-shape (derived from page data; above 1 means slower).

## Use it when

- Rendering untrusted or web fonts where memory safety matters more than the last 30-60% of font-funcs speed: both read-fonts and skrifa use #![forbid(unsafe_code)] and are fuzzed on OSS-Fuzz.
- Rust programs that need FreeType-equivalent outlines and hinting (TrueType, CFF, CFF2, autohinter) and full variable-font support without linking FreeType.
- Heavily varied instances of glyf/gvar fonts queried for extents or vertical origins: on varied Roboto Flex (wght=500) the issue measures 0.63-0.64x HarfBuzz OT's time.
- Glyph extents on CFF2 variable fonts (Adobe VF Prototype 0.92-0.93x of OT time) or nominal-glyph lookup on simple cmaps (about 0.98-0.99x).
- Projects that already pull the Rust font stack in through HarfBuzz -Dfontations, Skia or Chromium and want one implementation for shaping metrics and rasterisation.

## Skip it when

- As a speed upgrade over HarfBuzz's built-in OT font functions: across the 96 benchmark rows only 10 are faster; unvaried glyf extents and vertical origins are about 1.7-1.8x slower, unhinted drawing 1.17-1.94x slower, and Adobe VF Prototype nominal glyphs 3.5x slower.
- Fast CFF outline extraction in Rust: issue #1551 (July 2025) reports skrifa about 4x slower than ttf-parser on CFF outlining, about half of it from reparsing the Private DICT per glyph; only part of that has been fixed (PR #2204).
- C or C++ projects without a Rust toolchain: there is no C API, and HarfBuzz's meson rules for the backend use bindgen and cargo with -Z flags, so a nightly Rust is needed.
- Code that needs a stable API: all crates are pre-1.0 and bump the minor version for breaking changes roughly monthly (read-fonts 0.43.0 Aug 12, 0.44.0 Sep 8, 0.45.0 Oct 3, 2026).

## How it is fast

Tables are newtype wrappers over the font's byte slice with codegen'd accessors: minimal validation at parse time, big-endian records cast in place, and no allocation or copying. The current optimisation round (PR #2197, split into #2199-#2206) adds HarfBuzz-style lazily filled per-instance scalar caches for HVAR, VVAR and gvar (128 entries), skips scalar evaluation for zero deltas, reuses supplied gvar scalars for outlines and drawing, inlines cmap dispatch and CFF charstring opcode decoding, and skips unused Private DICT entries for unhinted CFF. None of this makes it faster than HarfBuzz OT except on a few varied-instance rows.

## Compared with alternatives

Pick Fontations over ttf-parser when you need hinting, an autohinter, COLRv1 painting and FreeType-matching output (the repo's fauntlet tool compares against FreeType), and accept slower CFF outlining; ttf-parser is the faster parser for raw outline extraction. For rasterising, ab_glyph or fontdue are complete small rasterisers, while skrifa only produces outlines for a separate rasteriser such as Skia.

## Integration

| | |
|---|---|
| **Form** | crate (read-fonts, skrifa, font-types, write-fonts); from C/C++ via HarfBuzz built with -Dfontations=enabled, which links a Rust staticlib |
| **Dependencies** | read-fonts: font-types, yoke, bytemuck, once_cell (core_maths with the libm feature, serde optional); skrifa: read-fonts, bytemuck; HarfBuzz backend: cargo, bindgen, meson's unstable-rust module |
| **Minimum toolchain** | Rust 1.85 (workspace rust-version, edition 2021); HarfBuzz's backend needs a nightly cargo for its -Z build-std and -Z unstable-options arguments |
| **Platforms** | any Rust target; std is a default feature and the libm feature exists for builds without std |
| **Thread safety** | not documented; the crates read immutable byte slices with no unsafe code, and HarfBuzz's glue serialises instance updates with a Mutex |
| **Drop-in for the baseline** | partial — inside HarfBuzz it swaps in for the OT font functions with one call (hb_font_set_funcs_using(font, "fontations")), but it is a different, Rust-only API everywhere else |

## Gotchas

- read-fonts returns a default value (0, None or an empty array) when a field of malformed table data cannot be read, instead of an error, so corrupt fonts degrade silently.
- Unhinted CFF drawing without a reusable HintingInstance reparses the Private DICT for every glyph (issue #1551); keep one instance per size if you draw many CFF glyphs.
- Through HarfBuzz, metric calls (cmap, advances, extents, origins) run HarfBuzz's own Rust glue (src/rust/font.rs, about 1,570 lines) over read_fonts::model; skrifa is used only for drawing, painting and bitmaps, so the benchmark is as much a test of that glue as of skrifa.
- HarfBuzz's backend build compiles Rust std with -Z build-std-features=optimize_for_size and -C force-frame-pointers=yes, and links it as a staticlib with no cross-language LTO, while the C++ side gets -O3 and LTO; the comparison is somewhat tilted against Fontations.

## Known shortcomings

- Mostly slower than HarfBuzz's OT font functions on HarfBuzz's own perf/benchmark-font.cc (Clang 21.1.7, meson release -O3 with LTO, Ryzen 9 5900X pinned to CPU 6): geometric means 1.29-1.58x slower and paint 1.26x slower, faster only on varied Roboto Flex origins (0.64x) and extents (0.63x), Adobe CFF2 extents (0.87x and 0.89x) and a few rows at 0.97-0.99x (derived from page data). The measured commit ec902bd2 is the head of the open, unmerged HarfBuzz PR #2197 plus local Cargo patches.
- Enricher (e107, 2026-10-05): A stands, no correctness bug. Issue #2196's body was revised 2026-10-04 (HarfBuzz 692a0aa30e vs Fontations 08bfef45; geomeans now nominal 1.52x, h-adv 1.39x, v-adv 1.10x, v-orig 1.62x, extents 1.33x, draw 1.56x, paint 1.16x, load+shape 1.06x; 10 of 96 rows faster; worst row Adobe VF nominal 3.50x). PR #2197 was closed and split into #2199-#2206, four merged 2026-10-04 and four still open, so the measured code is partly unreleased. Harness skews against Fontations: Rust std built optimize_for_size with forced frame pointers, no cross-language LTO; load_face_and_shape shapes a single space, so it measures setup cost; metric rows run HarfBuzz's src/rust/font.rs over read_fonts::model, not skrifa. Issue #1551: skrifa about 4x slower than ttf-parser on CFF outlining. Corrections in retier-31.

## Caveats and trade-offs

Weak 'faster' evidence: issue #2196 is a performance-gap report by the HarfBuzz maintainer (behdad; page shows opened 4 October 2026, updated 3 October 2026, still open). Fontations is slower than HarfBuzz OT in most rows (unvaried glyf extents and origins about 1.7-1.8x slower, unhinted drawing about 1.5x slower, paint about 1.26x slower, varied Adobe CFF2 advances 2.74x slower) and faster in a handful of varied-instance cases. The Fontations side measured commit ec902bd2, which is a head commit of the open, unmerged PR #2197 ('Reduce font model variation and lookup overhead', not on main), built with local Cargo patches for read-fonts 0.45.0, skrifa 0.48.0 and font-types 0.12.6; the HarfBuzz side was tuned in the same effort (HarfBuzz PR #6318, commit 5d86ce2980), so the table is a snapshot of in-flight optimisation on both sides and released crates may differ. Fontations is timed through HarfBuzz's font-funcs FFI layer (hb_font_set_funcs_using 'fontations'), so the numbers include that glue rather than standalone skrifa calls. They cover the font model only, not shaping or rasterization; there is no direct skrifa versus FreeType timing (the README's Performance section only points to HarfBuzz perf/README.md; fauntlet compares output, not speed). Some tables in the issue (supplied gvar scalars, PR #2197 numbers) used Rust 1.89 rather than the 1.94 nightly of the main table.

Memory-safe Rust, no allocation or copying in read-fonts, usable from C++ only through the HarfBuzz hb-fontations backend or a C wrapper (not a native C API). Hinting, autohinting and variable-font caches are separate costs that the issue does not isolate.

## Maintenance

Very active: read-fonts 0.45.0 and skrifa 0.48.0 shipped 2026-10-03, four of the eight split optimisation PRs merged 2026-10-04 (#2199, #2203, #2204, #2205) while #2200, #2201, #2202 and #2206 were still open on 2026-10-05, so the measured code is not all released; dual Apache-2.0/MIT, and skrifa has about 31 million crates.io downloads.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Issue #2196 runs the public HarfBuzz harness perf/benchmark-font.cc (same hb_font calls for both backends via hb_font_set_funcs_using, 'fontations' vs 'ot') at HarfBuzz commit eff2d6b9 and Fontations commit ec902bd2, with the HarfBuzz build stated (Clang 21.1.7, meson --buildtype=release (-O3) -Db_lto=true), the Rust build stated (1.94.0-nightly 2025-12-20, fat LTO, one codegen unit), the command line, and the CPU (AMD Ryzen 9 5900X, pinned to CPU 6, seven repetitions, CPU medians): code, compiler, flags and CPU model are all present, so A stands for a mostly-slower result.
- **Verifier notes:** All claimed numbers match the issue page and the harness does identical work for both backends, so the record is confirmed at A as a flagged mostly-slower entry (keep-and-document). HarfBuzz build is stated (Clang 21.1.7, release -O3, LTO); the measured Fontations code is an unmerged PR branch, which belongs in the shortcoming.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** HarfBuzz maintainer benchmark (issue #2196)
- **Pages the verifier opened:**
  - <https://github.com/googlefonts/fontations/issues/2196>
  - <https://github.com/googlefonts/fontations/pull/2197>
  - <https://github.com/googlefonts/fontations/commit/ec902bd22b5b045e0178bcc3010604e36a7b8342>
  - <https://github.com/googlefonts/fontations>
  - <https://github.com/googlefonts/fontations/commits/main>
  - <https://raw.githubusercontent.com/googlefonts/fontations/HEAD/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/eff2d6b995e0b45e3224079640457fa524c411b9/perf/benchmark-font.cc>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/perf/benchmark-font.cc>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/googlefonts/fontations/main/README.md>
  - <https://raw.githubusercontent.com/googlefonts/fontations/main/Cargo.toml>
  - <https://raw.githubusercontent.com/googlefonts/fontations/main/skrifa/README.md>
  - <https://raw.githubusercontent.com/googlefonts/fontations/main/skrifa/Cargo.toml>
  - <https://raw.githubusercontent.com/googlefonts/fontations/main/read-fonts/README.md>
  - <https://raw.githubusercontent.com/googlefonts/fontations/main/read-fonts/Cargo.toml>
  - <https://raw.githubusercontent.com/googlefonts/fontations/main/font-types/Cargo.toml>
  - <https://raw.githubusercontent.com/googlefonts/fontations/main/read-fonts/src/lib.rs>
  - <https://raw.githubusercontent.com/googlefonts/fontations/main/read-fonts/src/model.rs>
  - <https://raw.githubusercontent.com/googlefonts/fontations/main/read-fonts/src/model/metrics.rs>
  - <https://github.com/googlefonts/fontations/issues/2196>
  - <https://github.com/googlefonts/fontations/pull/2197>
  - <https://github.com/googlefonts/fontations/pull/2199>
  - <https://github.com/googlefonts/fontations/commit/08bfef45>
  - <https://github.com/googlefonts/fontations/pulls?q=is%3Apr+author%3Abehdad>
  - <https://github.com/googlefonts/fontations/issues?q=is%3Aissue+performance+OR+slow+OR+panic>
  - <https://github.com/googlefonts/fontations/issues/1551>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/692a0aa30e5962c6665f9f093519bb3f0cfff1ff/perf/benchmark-font.cc>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/perf/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/692a0aa30e5962c6665f9f093519bb3f0cfff1ff/src/hb-fontations.h>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/692a0aa30e5962c6665f9f093519bb3f0cfff1ff/meson_options.txt>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/692a0aa30e5962c6665f9f093519bb3f0cfff1ff/src/meson.build>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/692a0aa30e5962c6665f9f093519bb3f0cfff1ff/src/rust/meson.build>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/692a0aa30e5962c6665f9f093519bb3f0cfff1ff/src/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/692a0aa30e5962c6665f9f093519bb3f0cfff1ff/src/rust/lib.rs>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/692a0aa30e5962c6665f9f093519bb3f0cfff1ff/src/rust/font.rs>
  - <https://crates.io/api/v1/crates/read-fonts>
  - <https://crates.io/api/v1/crates/skrifa>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/googlefonts/fontations`) · [data/wave10/enrich/raw/github_com_googlefonts_fontations.json](../../../data/wave10/enrich/raw/github_com_googlefonts_fontations.json) (enrichment confidence 0.75)

</details>
