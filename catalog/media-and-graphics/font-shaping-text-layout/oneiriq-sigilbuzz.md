# sigilbuzz

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (C ABI)` · `Apache-2.0` · 🟢 active

> Pure-Rust, no_std HarfBuzz-API text shaper with an hb_\* C library; faster than rustybuzz on Latin/Hebrew only, slower on complex scripts.

| | |
|---|---|
| **Beats** | rustybuzz 0.20 (archived Rust port of HarfBuzz) only; HarfBuzz itself and FreeType are never measured, and the sigilbuzz-capi hb_\* C library is never benchmarked against libharfbuzz |
| **Claimed result** | Against rustybuzz only, faster on two of five scripts: Latin 11.39 us vs 15.03 us (page ratio 0.76x, about 1.32x faster, derived from page data) and Hebrew 10.99 us vs 17.28 us (page ratio 0.64x, about 1.57x faster, derived from page data). Slower on the other three: Arabic 290 us vs 108 us (2.70x slower), Devanagari 419 us vs 85.8 us (4.89x slower), Khmer 91.6 us vs 49.0 us (1.87x slower). No HarfBuzz comparison exists, so no win over HarfBuzz is shown. |
| **Workload** | Each Criterion bench shapes one fixed \~200-codepoint string per script through sigilbuzz and rustybuzz 0.20 back to back with no explicit features (font defaults such as liga and kern apply), face parsed once outside the loop and a fresh buffer per iteration: Latin on Open Sans, Arabic on Amiri (RTL), Devanagari on Noto Sans Devanagari, Khmer on Noto Sans Khmer, Hebrew on Noto Sans Hebrew (RTL). Medians from the 0.6.0 release. |
| **Metric** | latency |
| **Hardware** | maintainer's macOS arm64 workstation; CPU model not stated |
| **Compiler and flags** | cargo bench with Criterion; current Cargo.toml bench profile inherits release (lto = thin, codegen-units = 1, panic = abort, debug = true); rustc version not stated (MSRV 1.81). The table dates from 0.6.0 (2026-04-24), before the 0.22.0 move to Criterion 0.8, so the exact settings used for these numbers are not stated. |
| **Adoption** | 0 stars, 0 forks; crates.io crate first published 2026-10-02 (0.22.0), 0.23.0 published 2026-10-03, 55 downloads |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/Oneiriq/sigilbuzz) · [benchmark](https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/docs/PERFORMANCE.md) |

## Verdict

First-party Criterion medians from the 0.6.0 release on the maintainer's unnamed macOS arm64 machine (rustc version not stated) shape one fixed string per script against rustybuzz 0.20 with default features: sigilbuzz is faster on Latin (11.39 vs 15.03 us) and Hebrew (10.99 vs 17.28 us) and slower on Arabic (290 vs 108 us), Devanagari (419 vs 85.8 us) and Khmer (91.6 vs 49.0 us). Reading the bench sources shows only the Latin corpus is the 200 codepoints PERFORMANCE.md claims (compile-time asserted); Arabic is 183, Devanagari 188, Hebrew 179 and Khmer 147 codepoints (same string for both engines, so ratios are unaffected). The CHANGELOG says the Indic shaper matched HarfBuzz 14.5.0 on only 4,826 of 7,656 test strings and the Khmer shaper on 281 of the first 510 before the 0.22.0 rewrites, so the Devanagari and Khmer timings were taken on shapers later replaced for correctness, and no run shows output parity on the bench strings.

## Use it when

- Rust projects that need a dependency-free, no_std (alloc-only) shaper, e.g. wasm32-unknown-unknown or embedded targets, where linking C HarfBuzz is not an option.
- Byte-for-byte deterministic shaping output for golden-file tests, replays or lockstep networking (no random hashers, integer design-unit output).
- Mostly Latin or Hebrew text where the first-party Criterion run showed it 1.32x (Latin, Open Sans) and 1.57x (Hebrew, Noto Sans Hebrew) faster than rustybuzz 0.20 on an unnamed Apple arm64 machine.
- C or C++ builds that want to drop the C/C++ toolchain dependency of HarfBuzz and can live with the hb_\* subset declared in sigilbuzz-capi's include/hb.h.
- Projects that also want subsetting, WOFF2, COLRv1 paint and a GPU outline encoder from one pure-Rust workspace.

## Skip it when

- Arabic, Indic (Devanagari etc.) or Khmer heavy workloads: the only published numbers show it 2.70x, 4.89x and 1.87x slower than rustybuzz, which rustybuzz's own README puts at 1.5-2x slower than HarfBuzz; there is no measurement against HarfBuzz at all.
- When you want a speedup over libharfbuzz from C/C++: the hb_\* drop-in library has never been benchmarked against HarfBuzz, and every shape() call rebuilds its plan (no shape-plan cache), unlike hb_shape_plan caching in HarfBuzz.
- Production stacks that need maturity: 0 stars and 0 forks, crates.io publication only since 2026-10-02, releases 0.1.0 to 0.21.0 all cut on 2026-04-24/25, pre-1.0 API that may change in any minor release, and a ROADMAP 'Known bugs' list (CFF2 FDSelect format 4 truncation, morx ligature action bug, VARC axis inheritance, CFF hint-mask sizing).
- Code that relies on the full HarfBuzz C API: sigilbuzz-capi exports only what include/hb.h declares (e.g. no hb_font_draw_glyph, no hb_paint_funcs_get_empty, the paint image callback never fires) and targets the 8.2 API surface.
- Text that needs HarfBuzz's automatic fraction features or rand, or relies on Script-property lookups outside the older UnicodeScript block ranges (ROADMAP lists these as gaps).

## How it is fast

There is no special fast-path technique; the documented gains are removal of algorithmic waste in the GSUB driver. Per docs/PERFORMANCE.md (0.6.0, #74-#76) it keeps one glyph-ID snapshot per lookup instead of rebuilding a Vec at every cursor step, parses each lookup's subtables once per lookup walk (ParsedGsubSubtable in src/shape/gsub_parsed.rs) instead of at every position, and pre-checks coverage so positions whose glyph is in no subtable's coverage skip dispatch, mirroring HarfBuzz's skip-iterator digest check. In 0.22.0 GSUB moved to HarfBuzz's out-buffer model (out_info/next_glyph/replace_glyphs), making ligature and multiple substitution linear instead of quadratic in run length. src/shape/pipeline.rs states there is no shape-plan cache, so every shape() call re-selects features and re-parses lookup subtables, which is a likely reason it trails rustybuzz on complex scripts.

## Compared with alternatives

Among shaping siblings, SixLabors.Fonts is the pick for .NET and text-shaper or rustybuzz-wasm for JavaScript, and those at least compare against a HarfBuzz build; pick sigilbuzz only when you need a pure-Rust, no_std or C-toolchain-free shaper (or an hb_\*-compatible C library built from Rust) and can accept that no HarfBuzz parity in speed has been shown. For full paragraph layout in Rust, Parley (on HarfRust) is the more established choice.

## Integration

| | |
|---|---|
| **Form** | crate (sigilbuzz); C library via sigilbuzz-capi built as cdylib + staticlib with cargo-c (cargo cinstall installs libsigilbuzz, include/sigilbuzz/hb.h, sigilbuzz.pc and a CMake package) |
| **Dependencies** | none for the core crate; companion crates add miniz_oxide (WOFF1/PNG), brotli (WOFF2) and clap (CLI); sigilbuzz-capi build needs cargo-c 0.10.0+ for the install step |
| **Minimum toolchain** | Rust 1.81 (MSRV, edition 2021); cargo-c 0.10.0+ for the C library install |
| **Platforms** | any target stable Rust builds, including wasm32-unknown-unknown and no_std + alloc; benchmarks only reported for macOS arm64 |
| **Thread safety** | Not documented for shape(); OwnedFace (Arc&lt;[u8]&gt;, no lifetime) is documented as a face you can cache or share across threads. C API thread safety not documented. |
| **Drop-in for the baseline** | partial — sigilbuzz-capi claims link-level compatibility with HarfBuzz's hb_\* ABI for the covered 8.2 subset (blobs, faces, fonts, buffers, shaping, sets, subset, paint), but not the whole HarfBuzz API; the Rust API is HarfBuzz-shaped but differs from rustybuzz's (Buffer/shape(&font,&buffer,&features) vs UnicodeBuffer/shape(&face,..)). |

## Gotchas

- An unset direction shapes as LTR even for Arabic or Hebrew (no automatic direction detection in shape()); set Direction::Rtl yourself, as the benches do for Arabic and Hebrew.
- With no script set, shape() splits mixed text into script runs and shapes each with its own shaper, which differs from HarfBuzz; call buffer.guess_segment_properties() first to get HarfBuzz's one-shaper behavior.
- sigilbuzz-capi returns a fresh empty object where HarfBuzz returns its inert singleton, and earlier capi releases had different reference/destroy rules for subset sets: code written for capi before 0.3.0 can double-free now.
- The published PERFORMANCE.md numbers come from 0.6.0 (2026-04-24) and were never re-run after the 0.22.0 rewrite of GSUB and the Indic, Khmer, Myanmar and USE shapers, despite the file's own rule to update it whenever a hot path changes; current speed relative to rustybuzz is unknown in either direction.

## Known shortcomings

- Rust with a C ABI via sigilbuzz-capi (exports hb_\* symbols; language-filter mismatch). Compared only against rustybuzz 0.20, never HarfBuzz, so no HarfBuzz win is shown: Latin 1.32x and Hebrew 1.57x faster, Arabic 2.70x, Devanagari 4.89x and Khmer 1.87x slower; numbers from 0.6.0 (2026-04-24, current 0.23.0) on an unnamed macOS arm64 machine. rustybuzz itself is 1.5-2x slower than HarfBuzz.
- PERFORMANCE.md dates from 0.6.0 and was never re-run after 0.22.0 rewrote GSUB (previously quadratic) and the Indic, Khmer and USE shapers; before 0.22.0 the Indic shaper matched HarfBuzz on only 4,826 of 7,656 strings and Khmer on 281 of 510, so the Devanagari and Khmer timings come from shapers later replaced for correctness. Only the Latin corpus has the claimed 200 code points (Arabic 183, Devanagari 188, Hebrew 179, Khmer 147; the same string on both sides, so ratios hold). No shape-plan cache (pipeline.rs); no HarfBuzz timing anywhere; 0 stars; releases 0.1.0 to 0.21.0 were all cut on 2026-04-24/25; ROADMAP lists known bugs (CFF2 FDSelect, morx).

## Caveats and trade-offs

No HarfBuzz win is shown: the only baseline is rustybuzz 0.20, and the sigilbuzz-capi drop-in hb_\* library is never timed against libharfbuzz. rustybuzz's own README says it is 1.5-2x slower than HarfBuzz and that the project is archived in favour of HarfRust, so even the Latin and Hebrew wins (1.32x and 1.57x over rustybuzz) do not imply parity with HarfBuzz, and the 1.9x-4.9x losses on Arabic, Devanagari and Khmer suggest sigilbuzz is well behind HarfBuzz on complex scripts (inference, not measured). Numbers are first-party, from one unnamed Apple arm64 machine and one \~200-codepoint string per script, and date from 0.6.0 (2026-04-24) while the current release is 0.23.0; PERFORMANCE.md has not been refreshed since, and the CHANGELOG quotes slightly different ratios for the same run (Devanagari 4.98x, Arabic 2.72x, Khmer 1.88x). The crate is pure Rust; C and C++ use goes through the sigilbuzz-capi crate (cargo-c build). The repo has 0 stars and the crate was first published on 2026-10-02. Kept as a C-callable HarfBuzz-API alternative with an honest, mixed comparison against a HarfBuzz port, not as a faster-than-HarfBuzz library.

Pure Rust core (no_std, no runtime dependencies, deterministic output). C and C++ callers go through the sigilbuzz-capi crate, which exports HarfBuzz hb_\* symbols so it can be linked in place of libharfbuzz. Pre-1.0 API, no bug-for-bug compatibility with older HarfBuzz. Also ships a subsetter, WOFF/WOFF2 wrap and unwrap, UAX 14 line breaking, hyphenation, a CPU rasterizer and a Slug-style GPU outline encoder.

## Maintenance

Very active (0.23.0 on 2026-10-03, 546 commits, Apache-2.0) but young and unadopted: 0 stars, crates.io since 2026-10-02, pre-1.0 API, and a speed table that predates the current shaping engine by 16 minor releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/PERFORMANCE.md tabulates first-party Criterion medians from the 0.6.0 release for sigilbuzz vs rustybuzz 0.20 (bench code public in benches/shape_{latin,arabic,devanagari,khmer,hebrew}.rs), but rustc version and CPU model are not stated (only 'macOS arm64 workstation'), so it cannot be A; there is no independent measurement and no HarfBuzz measurement at all.
- **Verifier notes:** No HarfBuzz comparison exists anywhere in the repo (README, docs/PERFORMANCE.md, CHANGELOG, benches/); the page does compare against the record's named baseline, rustybuzz, with a mixed result, so this is a keep-and-document entry, not a reject. Language is Rust (pure-Rust core, C ABI via crates/sigilbuzz-capi exporting hb_\* symbols); 'language' is not a correctable field, so set it via decisions.json if a different label is wanted. Repo history starts 2026-04-24 (0.1.0) per CHANGELOG; 546 commits on main.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/docs/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/README.md>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/benches/shape_latin.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/benches/shape_arabic.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/benches/shape_hebrew.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/benches/shape_devanagari.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/benches/shape_khmer.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/crates/sigilbuzz-capi/README.md>
  - <https://github.com/Oneiriq/sigilbuzz>
  - <https://github.com/Oneiriq/sigilbuzz/commits>
  - <https://crates.io/api/v1/crates/sigilbuzz>
  - <https://raw.githubusercontent.com/harfbuzz/rustybuzz/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/Oneiriq/sigilbuzz>
  - <https://github.com/Oneiriq/sigilbuzz/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/README.md>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/docs/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/benches/shape_latin.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/benches/shape_arabic.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/benches/shape_devanagari.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/benches/shape_khmer.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/benches/shape_hebrew.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/crates/sigilbuzz-capi/README.md>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/crates/sigilbuzz-capi/Cargo.toml>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/crates/sigilbuzz-capi/src/lib.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/src/shape.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/src/shape/gsub_parsed.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/src/shape/pipeline.rs>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/docs/ROADMAP.md>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/docs/STABILITY.md>
  - <https://raw.githubusercontent.com/Oneiriq/sigilbuzz/HEAD/agent.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/oneiriq/sigilbuzz`) · [data/wave10/enrich/raw/github_com_oneiriq_sigilbuzz.json](../../../data/wave10/enrich/raw/github_com_oneiriq_sigilbuzz.json) (enrichment confidence 0.75)

</details>
