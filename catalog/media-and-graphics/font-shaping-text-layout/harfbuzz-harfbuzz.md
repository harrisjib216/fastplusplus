# harfbuzz

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT-Modern-Variant` · 🟢 active

> The standard OpenType/AAT text shaping engine (C++11, no C++ standard library); 1.76x geomean faster than its Rust port rustybuzz.

| | |
|---|---|
| **Beats** | rustybuzz (Rust port of HarfBuzz); the guessed 'built-in text shaping' baseline has no published numbers |
| **Claimed result** | rustybuzz README: "At the moment, performance isn't that great. We're 1.5-2x slower than harfbuzz." benches/README.md rows (ns/iter, hb vs rb): english paragraph_long 134,123.63 vs 350,304.15 (2.61x, derived from page data); arabic paragraph_long 164,095.44 vs 336,837.60 (2.05x, derived); hindi paragraph_long 518,143.75 vs 835,427.60 (1.61x, derived); myanmar paragraph_long 1,037,674.90 vs 2,947,060.40 (2.84x, derived); english paragraph_medium 95,546.23 vs 251,779.15 (2.64x, derived); english aat_paragraph_long 427,435.42 vs 536,666.60 (1.26x, derived). Over all 70 rows the rb/hb time ratio has geometric mean 1.76x, median 1.89x, range 0.42x to 4.38x (derived from page data). |
| **Workload** | Time per shaping call (face and buffer creation included in each iteration) of HarfBuzz via harfbuzz_rs versus rustybuzz on 70 text/font pairs (English, Arabic, Hebrew, Hindi, Khmer, Myanmar, Thai; words, sentences, paragraphs, AAT fonts, zalgo, variable fonts), Rust nightly cargo bench on an Apple M1 Pro. |
| **Metric** | latency |
| **Hardware** | Apple M1 Pro (heading 'Results (on M1 Pro)') |
| **Compiler and flags** | cargo +nightly bench (#![feature(test)]) with HARFBUZZ_SYS_NO_PKG_CONFIG="", which makes harfbuzz_rs's build.rs skip pkg-config and compile its bundled harfbuzz/src/harfbuzz.cc with the cc crate (-std=c++11, optimization level from cargo's bench profile); rustc nightly version and C++ compiler (presumably Apple clang) not stated. HarfBuzz comes from harfbuzz_rs git rev 43f0fb5 ('update bindings to 9.0', so about HarfBuzz 9.0.0; harfbuzz submodule at commit b8087db). Harness: harfbuzz/rustybuzz benches/src/lib.rs. |
| **Adoption** | 6.1k stars; used in Android, Chrome, Firefox, Flutter, GNOME, GTK, KDE, Qt, LibreOffice, OpenJDK, Godot and Unreal Engine per its README |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/harfbuzz/harfbuzz) · [benchmark](https://github.com/harfbuzz/rustybuzz/blob/main/benches/README.md) |

## Verdict

The rival rustybuzz project's cargo +nightly bench on an Apple M1 Pro (July 2024) timed face, font and buffer creation plus one shaping call per iteration over 70 text/font pairs, with HarfBuzz about 9.0 compiled from harfbuzz_rs's bundled amalgamation via the cc crate (-std=c++11): HarfBuzz was faster on 65 rows, geomean 1.76x and median 1.89x (English long paragraph 134 vs 350 us, Myanmar 1.04 vs 2.95 ms), and slower on five single-word rows (0.42x to 0.87x). Compiler versions are not stated.

## Use it when

- Any product that has to shape complex scripts correctly and quickly (Arabic, Nastaliq Urdu, Devanagari and other Indic scripts, Khmer, Myanmar, Thai, Hebrew) or apply OpenType features and variable-font axes; it is the engine inside Android, Chrome, Firefox, Qt, GTK, LibreOffice and Unreal according to its README.
- Long-lived renderers (editors, browsers, game UIs) that keep hb_face_t/hb_font_t objects alive and shape many runs per frame: caches and shape plans then amortize, the case the rival port's cold-start harness did not measure.
- Cross-platform apps that want identical shaping on Linux, Windows, macOS, Android and WASM instead of CoreText/DirectWrite differences, including AAT (morx/kerx/trak) fonts on non-Apple systems.
- C or C++ codebases that can vendor one file: the amalgamated src/harfbuzz.cc builds with a plain C++11 compiler and no required dependencies; bindings exist for Python (uharfbuzz), Rust (harfbuzz_rs/harfbuzz-sys) and .NET (HarfBuzzSharp).
- Font pipelines that also need subsetting or instancing (hb-subset) next to shaping.

## Skip it when

- Pure-Rust or no-C++-toolchain projects: HarfRust (the maintained successor of rustybuzz, tracking HarfBuzz 14.5.1) says it is less than 25% slower on most common fonts and needs no C++ build; rustybuzz itself is archived.
- Hinted glyph rendering: HarfBuzz does no hinting or autohinting; pair it with FreeType or Skrifa.
- Shaping single words with a freshly created face and font every call: in the cold-start harness rustybuzz won five such rows (English AAT word 4.4 vs 10.5 us, Arabic single words about 10.4 vs 12.6 us), so cache faces and fonts.
- Expecting a full text-layout stack: line breaking, font fallback and paragraph layout are outside libharfbuzz; use Pango, Parley or a browser engine on top.
- Rendering text from fonts with broken GSUB/GPOS and expecting partial features: since 12.3.0 invalid layout tables are rejected outright (like CoreText, unlike DirectWrite and HarfRust), so such fonts shape without those features.

## How it is fast

Per-face accelerators and caches that the rustybuzz port deliberately left out (its README blames the gap on HarfBuzz's 'accelerators and caches'): lazily built GSUB/GPOS lookup accelerators, a per-face shaping cache for kerning and ligature lookups (about 1 KB per face, 10.3.0), Coverage caching and a (Chain)Context fast path (12.3.0), a faster AAT state machine (10.3.0 and 12.3.0), and allocation-free draw/paint in the hb-ot path (11.0.0). It uses its own containers instead of the C++ standard library, generated state machines for the Indic-family shapers (ragel) and packed Unicode tables (PackTab). Shape plans are cached on the face, so long-lived faces and fonts amortize setup.

## Compared with alternatives

Pick HarfBuzz over kb_text_shape whenever script coverage or speed matters (the maintainer's run shows HarfBuzz 1.2-6.6x faster on four script rows, 160x on Gulzar with English text, and kbts 40-760x slower at font load), and over managed or WASM-side shapers (SixLabors.Fonts, text-shaper, rustybuzz-wasm, which compare against HarfBuzzSharp or harfbuzzjs rather than native HarfBuzz) when you can link native C++; choose HarfRust or Parley's stack only when a pure-Rust build matters more than the last 25%.

## Integration

| | |
|---|---|
| **Form** | shared lib or static lib (Meson build), or source-drop via the amalgamated src/harfbuzz.cc (also harfbuzz-subset.cc and harfbuzz-world.cc) |
| **Dependencies** | none required for libharfbuzz; optional FreeType, GLib/GObject, ICU, Cairo, graphite2, CoreText, DirectWrite, GDI, Uniscribe and fontations/HarfRust backends (BUILD.md's distro package lists also include ragel) |
| **Minimum toolchain** | C++11 (meson.build sets cpp_std=c++11; the benchmark compiled it with -std=c++11); Meson 0.60+ for the official build; GCC, Clang and MSVC are covered by CI |
| **Platforms** | any: CI on Linux, macOS and Windows (MSVC); also used through WASM (harfbuzzjs) and mobile; scalar portable code |
| **Thread safety** | Thread-safe by default (HB_NO_MT or the HB_TINY profile disables it); faces and fonts can be shared once set up (make_immutable), lifecycle calls are always thread-safe, and an hb_buffer_t may be used by only one thread at a time |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness design behind the 1.76x: rustybuzz's benches/src/lib.rs creates the face, font and buffer inside every timed iteration on both sides, so shape-plan compilation and HarfBuzz's lazily loaded table accelerators are paid on every call. That is why HarfBuzz loses on single words and why the numbers say little about warm, cached use; HarfBuzz's own perf/benchmark-shape.cc warms the font and buffer once and reuses them. Both sides otherwise do equivalent work (harfbuzz_rs::shape guesses segment properties like rustybuzz, Face::from_bytes wraps the bytes without copying).
- Stale versions on both sides: the numbers are from July 2024 with HarfBuzz about 9.0 (harfbuzz_rs rev 43f0fb5); HarfBuzz is at 14.6.0 (2026-10-05) and its own NEWS reports AAT shaping on LucidaGrande going from 14.6 to 5.9 ms in 10.3.0 plus a further 12% in 12.3.0, so the measured 1.26x on the AAT paragraph row likely understates the current gap. The baseline rustybuzz was archived and replaced by HarfRust, whose own '&lt;25% slower' comparison sits in a Google spreadsheet that could not be opened.
- First-party cross-check only: in discussion #5375 (2025-07-23) the HarfBuzz maintainer ran perf/benchmark-shape with the 'ot' shaper against the kbts backend (kb_text_shape): Roboto little-prince 9.11 vs 26.5 ms, Roboto words 11.3 vs 38.4 ms, Amiri Persian 40.6 vs 48.3 ms, Gulzar Persian 782 vs 5198 ms, Devanagari words 25.3 vs 50.5 ms; hardware and build type not stated. No published comparison against CoreText, DirectWrite or Uniscribe exists, although benchmark-shape can run those shapers when they are compiled in.
- Security history to track: CVE-2024-56732 (heap overflow in hb_cairo_glyphs_from_buffer, the Cairo integration, 8.5.0 to 10.0.1, CVSS 8.8) and CVE-2026-22693 (NULL dereference in the cmap cache, fixed in 12.3.0), both from search snippets; the core is fuzzed continuously on OSS-Fuzz, and the project asks for 90 days before public disclosure.

## Known shortcomings

- rustybuzz benches (July 2024, M1 Pro, HarfBuzz about 9.0 via harfbuzz_rs rev 43f0fb5): geomean 1.76x over rustybuzz, 65 of 70 rows faster, but the baseline is a deliberately unoptimized Rust port and compiler and flags are unstated. Licence is MIT-Modern-Variant.
- Enricher: the rustybuzz harness rebuilds face, font and buffer every iteration (cold, plan compile timed), so it says little about cached use; numbers are HarfBuzz about 9.0 (Jul 2024) while HarfBuzz is now 14.6.0 and its own NEWS reports AAT 14.6 to 5.9 ms, so the gap is likely understated; the rustybuzz baseline is archived; since 12.3.0 invalid GSUB/GPOS fonts are rejected outright; first-party discussion #5375 has HarfBuzz ot 1.2-160x faster than kbts. CVE-2024-56732, CVE-2026-22693.

## Caveats and trade-offs

The only numbers against an outside baseline come from the rival Rust port's own benches (rustybuzz, now under the harfbuzz GitHub org, archived 2026-07-26), not from the HarfBuzz project. The results were committed by rustybuzz maintainer LaurenzV on 2024-07-01..03, against HarfBuzz about 9.0.0 (harfbuzz_rs rev 43f0fb5) and a rustybuzz that predates its later sync to HarfBuzz v10.1.0; both sides are older than current HarfBuzz 14.x, so today's gap may differ. rustybuzz admits it is not a faithful port and that HarfBuzz's 'accelerators and caches' were deliberately left out of it, which explains much of the gap. HarfBuzz is faster on 65 of 70 rows; rustybuzz wins five short-text rows (arabic word_1/2/3 at 0.82x/0.87x/0.82x rb/hb time ratio, english aat_word_1 at 0.42x, hindi aat_word at 0.62x, all derived from page data). Each iteration builds the face and buffer (and for HarfBuzz also an hb_font via harfbuzz_rs::Font::new), so setup cost is included for both sides and HarfBuzz probably rebuilds its lazily loaded table accelerators every call, which likely explains its losses on single-word rows. Successor HarfRust's README says it is 'less than 25% slower than HarfBuzz on most common fonts' but backs it only with a Google spreadsheet that was not reachable (docs.google.com blocked). HarfBuzz's own NEWS and perf/README.md contain only before/after self-comparisons (for example 10.3.0: AAT shaping of LucidaGrande 14.6 ms to 5.9 ms) and no comparison with CoreText, DirectWrite, Uniscribe, ICU or FreeType; no hb-subset versus fonttools figure was found. The listed 'built-in text shaping' baseline therefore has no numbers here. Licence is HarfBuzz's 'Old MIT' (SPDX MIT-Modern-Variant, OSI-approved); some subdirectories carry their own COPYING files.

The Old MIT licence in COPYING (no SPDX id of its own; effectively MIT). Written in C++ without the C++ standard library (README of the Rust ports notes 'harfbuzz doesn't use C++ std') and amalgamated single-file builds exist. HarfBuzz is optimized for 'robustness, correctness, and performance - in that order'. Malformed fonts fall back to a dummy shaper instead of failing; it has no hinting.

## Maintenance

Actively developed (14.6.0 released 2026-10-05, about 22k commits, 6.1k stars, two main maintainers per SECURITY.md) under the Old MIT licence with a stable API/ABI, and the single-file amalgamation makes it easy to vendor; the benchmark's baseline, rustybuzz, is archived.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent measurement by the rival rustybuzz port (results committed by its maintainer LaurenzV, July 2024) with public harness benches/src/lib.rs and CPU stated (Apple M1 Pro), but the rustc nightly version and the C++ compiler used for the bundled HarfBuzz are not stated, so not A; B as an independent third-party measurement.
- **Verifier notes:** All quoted rows and the 70-row statistics (geomean 1.76x, median 1.89x, range 0.42x to 4.38x rb/hb, 65 of 70 rows faster) recomputed exactly from benches/README.md; rustybuzz README '1.5-2x slower than harfbuzz' confirmed. Corrections: licence is MIT-Modern-Variant (HarfBuzz 'Old MIT', OSI-approved per SPDX data) rather than MIT; bundled HarfBuzz pinned to about 9.0.0; results date from July 2024. Shortcomings: baseline is a deliberately unoptimized Rust port, not a system shaper; HarfBuzz itself publishes no comparison against CoreText/DirectWrite/ICU; numbers are two years old.
- **Fields the verifier corrected:** `license`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-113 (wave 10); enricher w10 pair-028
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/harfbuzz/rustybuzz/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/rustybuzz/HEAD/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/rustybuzz/HEAD/benches/Cargo.toml>
  - <https://raw.githubusercontent.com/harfbuzz/rustybuzz/HEAD/benches/src/lib.rs>
  - <https://github.com/harfbuzz/rustybuzz/commits/main/benches/README.md>
  - <https://github.com/harfbuzz/rustybuzz>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz_rs/43f0fb5/Cargo.toml>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz_rs/43f0fb5/build.rs>
  - <https://github.com/harfbuzz/harfbuzz_rs/tree/43f0fb5>
  - <https://github.com/harfbuzz/harfbuzz_rs/commit/43f0fb5>
  - <https://github.com/harfbuzz/harfbuzz/commit/b8087dbdd58361aaad8c2b0e57f3414f500cc8a7>
  - <https://raw.githubusercontent.com/harfbuzz/harfrust/HEAD/README.md>
  - <https://github.com/harfbuzz/harfbuzz>
  - <https://github.com/harfbuzz/harfbuzz/commits>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/COPYING>
  - <https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json>
- **Sources the enricher read:**
  - <https://github.com/harfbuzz/harfbuzz>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/NEWS>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/perf/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/perf/benchmark-shape.cc>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/perf/meson.build>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/meson.build>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/meson_options.txt>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/CONFIG.md>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/BUILD.md>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/docs/usermanual-object-model.xml>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/docs/usermanual-buffers-language-script-and-direction.xml>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/HEAD/docs/usermanual-install-harfbuzz.xml>
  - <https://github.com/harfbuzz/harfbuzz/discussions/5375>
  - <https://raw.githubusercontent.com/harfbuzz/rustybuzz/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/rustybuzz/HEAD/benches/src/lib.rs>
  - <https://raw.githubusercontent.com/harfbuzz/rustybuzz/HEAD/benches/Cargo.toml>
  - <https://raw.githubusercontent.com/harfbuzz/rustybuzz/HEAD/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz_rs/43f0fb5/build.rs>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz_rs/43f0fb5/Cargo.toml>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz_rs/43f0fb5/src/lib.rs>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz_rs/43f0fb5/src/font.rs>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz_rs/43f0fb5/src/face.rs>
  - <https://raw.githubusercontent.com/harfbuzz/harfrust/HEAD/README.md>
  - <https://github.com/harfbuzz/harfrust>
  - WebSearch: harfbuzz CVE 2025 2026 (snippets: CVE-2024-56732, CVE-2026-22693)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/harfbuzz/harfbuzz`) · [data/wave10/enrich/raw/github_com_harfbuzz_harfbuzz.json](../../../data/wave10/enrich/raw/github_com_harfbuzz_harfbuzz.json) (enrichment confidence 0.7)

</details>
