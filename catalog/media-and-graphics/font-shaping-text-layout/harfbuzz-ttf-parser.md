# ttf-parser

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (with a basic C API)` · `MIT OR Apache-2.0` · 🟢 active

> Safe, zero-allocation Rust font parser with a C API; extracts unscaled glyph outlines 1.3-5x faster than FreeType's FT_Load_Glyph path.

| | |
|---|---|
| **Beats** | FreeType (FT_Load_Glyph with FT_LOAD_NO_SCALE, glyph outlining); stb_truetype also compared |
| **Claimed result** | x86 (AMD 3700X), ms to outline all glyphs, ttf-parser vs FreeType: glyf 0.901 vs 1.171, gvar 2.972 vs 4.132, CFF 1.197 vs 5.647, CFF2 1.968 vs 6.392. ARM (Apple M1): glyf 0.550 vs 0.854, gvar 2.270 vs 4.594, CFF 1.054 vs 5.223, CFF2 1.765 vs 5.995. Derived from page data: x86 1.30x, 1.39x, 4.72x, 3.25x; M1 1.55x, 2.02x, 4.96x, 3.40x. On plain glyf, stb_truetype is faster than ttf-parser on x86 (0.675 ms) but slower on M1 (0.703 ms). |
| **Workload** | Time to outline every glyph of a font (callbacks that only count move/line/quad/cubic segments) for glyf, glyf with gvar variations, CFF and CFF2 fonts; benchmark is C++ (benches/outline/outline.cc, Google Benchmark) calling FreeType, stb_truetype and the ttf-parser C API. |
| **Metric** | latency |
| **Hardware** | AMD 3700X (x86) and Apple M1 (ARM) |
| **Compiler and flags** | benches/outline/README.md: cargo build --release for the C API, meson --buildtype release (meson's release optimization level, no debug), C++14 per meson.build; C++ compiler and rustc versions not stated; FreeType is the system freetype2 (meson requires &gt;=2.8), version not stated |
| **Adoption** | 793 stars |
| **Last commit** | 2026-08-06 |
| **Links** | [repository](https://github.com/harfbuzz/ttf-parser) · [benchmark](https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/README.md) |

## Verdict

The author's Google Benchmark 1.4.1 harness (benches/outline/outline.cc) outlined every glyph of Source Sans Pro (TTF and OTF) and Source Sans Variable (TTF with gvar, OTF with CFF2, wght 500) through the ttf-parser C API, FreeType (FT_LOAD_NO_SCALE + FT_Outline_Decompose) and stb_truetype, on an AMD 3700X and an Apple M1; ttf-parser was 1.30x/1.55x faster on glyf, 1.39x/2.02x on gvar, 4.72x/4.96x on CFF and 3.25x/3.40x on CFF2 (x86/M1, derived from page data). The table first appeared in the v0.14.0 README (2021-12-28), when the feature table's 'Tested version' row read ttf-parser 0.14.0, FreeType 2.10.4, stb_truetype 1.24; that row was later bumped to 0.17.0/2.12.0 without the numbers changing, so the benchmark's FreeType version is likely 2.10.4 but never stated, and no compiler or rustc version is given. The harness ignores ttfp_outline_glyph's return value and never compares segment counts between libraries (ttf-parser's counter also counts close_path, which FreeType has no callback for), so it does not prove that ttf-parser outlined every glyph it was timed on.

## Use it when

- Rust code that needs unscaled glyph outlines to feed its own rasterizer, SDF/MSDF generator, path tessellator or PDF/SVG writer, especially from CFF/CFF2 (OTF) fonts, where the measured gap to FreeType was largest (3.3x-5.0x).
- Parsing untrusted fonts in a memory-safe way: no unsafe code in the core crate, no heap allocation by default, depth limits on recursion and panics treated as bugs (use the main branch to get the 2026 work-budget fixes, see below).
- no_std or WASM targets that need metrics, cmap lookup and outlines with zero dependencies (core_maths only for no_std float).
- Projects that already pull it in through fontdue, rustybuzz or Typst (all depend on ttf-parser 0.25) and want direct outline or table access without a second font stack.
- C or C++ programs that only need outlines, metrics and cmap and are willing to ship a Rust-built shared library to replace FreeType's parsing layer.

## Skip it when

- Anything that needs hinting, scaled or hinted bitmaps, LCD filtering or rasterization, which is FreeType's main job; ttf-parser stops at font-unit outlines.
- Plain static TrueType (glyf) outlining from C or C++: in the same harness stb_truetype beat it on x86 (0.675 vs 0.901 ms) and was only 1.28x slower on M1 (0.703 vs 0.550 ms), as one header with no Rust toolchain.
- New projects: the README (2026-08-06) puts the crate in maintenance mode (bug fixes only, no performance work) and recommends fontations (read-fonts and skrifa); issue #230 (2026-08-05) called it unmaintained and announced a fork.
- Shipping the crates.io release 0.25.1 (2024-11-29, 112.7M downloads) against untrusted fonts: the unreleased main branch fixes a CFF subroutine fan-out where a 255-byte CFF table hung for over 30 s, an infinite loop on self-referential GSUB/GPOS extension lookups in release builds, unbounded composite-glyph and COLRv1 fan-out, and a C API panic in ttfp_get_glyph_name that aborts across the extern "C" boundary.
- Fonts that hit 0.25.1 correctness gaps fixed only on main: CFF fonts with a non-default FontMatrix outlined at the wrong scale, static CFF2 fonts without a vstore returned no outline for any glyph, glyphs using the deprecated dotsection operator produced no outline, and 65536-glyph loca tables dropped glyf entirely. Composite point matching and cmap format 8 remain unsupported.

## How it is fast

Everything is zero-copy over the font bytes (lazy arrays and a big-endian Stream reader) and nothing is allocated or copied into a glyph slot: the glyf path walks the flag/x/y streams with iterators, synthesises implied on-curve midpoints on the fly (Builder::push_point) and calls the user's callbacks directly while accumulating the bbox. CFF and CFF2 use a Type 2 charstring interpreter with a fixed 48-entry operand stack and a 10-deep subroutine limit that skips all hint operators ('We are ignoring the hint operators'). gvar deltas are applied while streaming, holding up to 32 tuple iterators on the stack and re-parsing a contour when it has to infer untouched-point (IUP) deltas. The FreeType side of the benchmark instead loads each glyph into the face's glyph slot with FT_Load_Glyph(FT_LOAD_NO_SCALE) and then walks it a second time with FT_Outline_Decompose.

## Compared with alternatives

fontdue and Typst already use ttf-parser for parsing; pick it directly when you need the outlines or tables themselves rather than fontdue's rasterized bitmaps or Typst's layout. Pick fontdue (or FreeType) when you need pixels, and a HarfBuzz-family shaper (rustybuzz, SixLabors.Fonts, text-shaper) when you need shaping, which ttf-parser does not do.

## Integration

| | |
|---|---|
| **Form** | crate (Rust); C API is a separate crate (ttf-parser-capi) built as a cdylib, or a static lib via cargo-c, with the hand-written header ttfparser.h |
| **Dependencies** | none (optional core_maths for no_std float); the C API needs a Rust toolchain to build |
| **Minimum toolchain** | crates.io 0.25.1: Rust 1.63 (manifest rust-version); main branch: Rust 1.88, edition 2024. Header is plain C (stdbool/stdint); the benchmark compiles it as C++14 |
| **Platforms** | any Rust target, including no_std and WASM; scalar code, no SIMD or platform-specific paths |
| **Thread safety** | All parsing methods are immutable and the README's comparison table marks it thread safe, so one face can be read from many threads; ttfp_set_variation / Face::set_variation is the only mutating call and stores coordinates in the face, so use one face copy per variation instance. |
| **Drop-in for the baseline** | false: different API (opaque ttfp_face plus callback builder instead of FT_Face/glyph slot), outlines in font units only, no hinting, scaling or rendering |

## Gotchas

- ttfp_outline_glyph may already have emitted segments when it returns false on a partially malformed outline; the header says to check the return value before using the builder's output.
- gvar glyphs with more than 32 variation tuples fail unless the gvar-alloc feature is enabled (it then heap-allocates), so 'zero allocation' and full gvar support are mutually exclusive.
- C API: the caller mallocs ttfp_face_size_of() bytes and passes them to ttfp_face_init, the font buffer must outlive the face, and the C API omits GSUB/GPOS/morx and other layout tables. The c-api crate is licensed MIT only, not MIT OR Apache-2.0 like the core crate.
- Every C API call wraps the Rust code in catch_unwind; the core crate forbids unsafe, but the FFI layer necessarily uses it.

## Known shortcomings

- Rust crate with a basic C API (language-filter mismatch). The FreeType comparison table (1.3x to 5x on AMD 3700X and Apple M1; benches/outline/outline.cc) lives only in the v0.25.1 tagged README: it was cut from the current README on 2026-08-06 as stale (unchanged since v0.15.0), compiler and FreeType versions are unstated, and stb_truetype is faster on x86 glyf outlines. README now says maintenance mode.
- The benchmark table first appeared in the v0.14.0 README (2021-12-28) with FreeType 2.10.4 as the tested version, later relabelled 2.12.0 with the numbers unchanged, so the measured FreeType is probably 2.10.4 and never stated. The harness ignores ttfp_outline_glyph's return value and never compares segment counts (ttf-parser's counter includes close_path), so the record's 'same segment counts' caveat is unsupported. crates.io 0.25.1 (2024-11-29) lacks main-branch fixes: a CFF subroutine hang (a 255-byte table takes over 30 s), a GSUB/GPOS extension infinite loop, wrong scale on a non-default FontMatrix, and static CFF2 without vstore yielding no outlines; gvar with more than 32 tuples fails without gvar-alloc; the C API crate is MIT only; maintenance mode, fontations recommended.

## Caveats and trade-offs

The performance table was cut from the current README on 2026-08-06 (commit 'docs: cut the stale comparison table and benchmarks from the README'); it survives in tagged READMEs (read from v0.25.1, v0.20.0, v0.17.0 and v0.15.0, all identical), and v0.12.0 carried an earlier x86-only table (glyf 0.915 vs 1.258 ms, CFF 1.365 vs 5.992 ms), so the numbers are several releases old and were never refreshed. The author's own note under the table: 'FreeType is surprisingly slow, so I'm worried that I've messed something up.' FreeType is asked for unscaled outlines only (FT_Load_Glyph with FT_LOAD_NO_SCALE, then FT_Outline_Decompose), which loads the glyph into a glyph slot before decomposing, while ttf-parser streams segments straight to callbacks; both produce the same segment counts, but this is outline extraction, not rasterization or hinting. Benchmark code is public and CPUs are named, but compilers and library versions are not, so this sits just under tier A. Wins on plain glyf are modest (1.3x to 1.55x) and stb_truetype beats ttf-parser on glyf on x86. The current README says the crate is in maintenance mode (bug fixes only, no performance work) and recommends fontations (read-fonts/skrifa) for new projects.

Parser and outliner only: no rasterization, no shaping, no hinting. Safe Rust, zero allocation, zero dependencies; C API is basic. The repo is in maintenance mode (bug fixes only, no new features or performance work) and recommends fontations (read-fonts and skrifa) for new projects.

## Maintenance

Maintenance mode since 2026-08-06 (bug fixes only) with active security hardening on main, but the last crates.io release is 0.25.1 from November 2024, so pin a main-branch commit for the hang and correctness fixes; MIT OR Apache-2.0 core, MIT C API.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The v0.25.1 README table (identical since v0.15.0) shows ttf-parser vs FreeType and stb_truetype on AMD 3700X and Apple M1, and the benchmark code is public (benches/outline/outline.cc, Google Benchmark, meson --buildtype release + cargo --release), but no C++ compiler or rustc version and no FreeType version are named, so it stays first-party tier C rather than A.
- **Verifier notes:** All eight ttf-parser and FreeType numbers and the derived ratios check out against the tagged README. The record is Rust with a C API, so it does not match a C++ language filter. It is a font parser and outliner rather than a shaper, so the category fit is approximate. Metadata confirmed: 793 stars, MIT OR Apache-2.0, last commit 2026-08-06, not archived, not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/RazrFalcon/ttf-parser/v0.25.1/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.20.0/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.17.0/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.15.0/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.12.0/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/benches/outline/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/benches/outline/outline.cc>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/benches/outline/meson.build>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/LICENSE-MIT>
  - <https://github.com/harfbuzz/ttf-parser>
  - <https://github.com/harfbuzz/ttf-parser/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/benches/outline/outline.cc>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/benches/outline/meson.build>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/benches/outline/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/c-api/Cargo.toml>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/c-api/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/src/tables/glyf.rs>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/src/tables/gvar.rs>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/src/tables/cff/cff1.rs>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/HEAD/src/tables/cff/charstring.rs>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/Cargo.toml>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/benches/outline/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/benches/outline/outline.cc>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/benches/outline/meson.build>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/benches/outline/subprojects/google-benchmark.wrap>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/benches/outline/subprojects/stb_truetype.wrap>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/c-api/ttfparser.h>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/c-api/lib.rs>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.25.1/c-api/Cargo.toml>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.17.0/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.15.0/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.14.0/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.13.0/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.12.0/README.md>
  - <https://github.com/harfbuzz/ttf-parser/tree/v0.25.1/benches/outline>
  - <https://github.com/harfbuzz/ttf-parser/tree/v0.25.1/benches/outline/subprojects>
  - <https://github.com/harfbuzz/ttf-parser/commits/main>
  - <https://github.com/harfbuzz/ttf-parser/issues?q=is%3Aissue+performance+OR+slow+OR+freetype>
  - <https://github.com/harfbuzz/ttf-parser/issues/76>
  - <https://github.com/harfbuzz/ttf-parser/issues/230>
  - <https://crates.io/api/v1/crates/ttf-parser>
  - <https://raw.githubusercontent.com/mooman219/fontdue/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/typst/typst/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Hoteira/titanf/HEAD/Cargo.toml>
  - <https://github.com/typst/pixglyph/pull/4>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/harfbuzz/ttf-parser`) · [data/wave10/enrich/raw/github_com_harfbuzz_ttf_parser.json](../../../data/wave10/enrich/raw/github_com_harfbuzz_ttf_parser.json) (enrichment confidence 0.8)

</details>
