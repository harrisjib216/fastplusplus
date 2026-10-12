# tiny-skia

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `BSD-3-Clause` · 🟢 active

> Pure-Rust port of Skia's CPU raster pipeline; about 1.7-2.3x faster than cairo on x86 overall, slower on solid rect fills.

| | |
|---|---|
| **Beats** | Cairo (and raqote); slower than Skia |
| **Claimed result** | README: 20-100% slower than Skia on x86-64 and about 100-300% slower on ARM, 'still faster than cairo and raqote in many cases'. Results pages (gh-pages x86_64.html, July 2021; arm.html, Aug 2022), excluding the invalid Fill All (overwrite versus blend) and no-op Destination rows: tiny-skia AVX2 beats cairo in 36 of 44 x86 tests (geometric mean 2.32x; the default SSE2 build 34 of 44 at 1.71x) and beats cairo in most ARM tests, where cairo's build appears to lack NEON (derived from page data). Cairo wins on x86 rect fills (0.37-0.45x), Nearest pattern (0.39x) and Source Over/Destination Over/Plus blending (0.31-0.58x); tiny-skia wins most on non-separable blend modes (4.5-9x) and AA hairlines (4.4x); the bicubic 11.9x compares different filters (cairo Best). Against Skia AVX2 tiny-skia wins only 5 of 50 x86 tests. |
| **Workload** | CPU 2D rendering of common operations (fills, strokes, gradients, patterns, clipping) in the project's benchmark set. |
| **Metric** | throughput |
| **Hardware** | AMD 3700X (Ryzen 7, Gentoo Linux) for x86-64 results; Apple M1 for ARM results |
| **Compiler and flags** | x86 page (committed 2021-07-04): benches/README at that time lists Rust 1.53 (nightly cargo bench), clang 12, tiny-skia -Ctarget-cpu=x86-64 (SSE2) or haswell (AVX2), Skia built with clang -march=x86-64/haswell plus -DSK_FORCE_RASTER_PIPELINE_BLITTER and is_debug=false gn args, cairo 1.16.0 Gentoo system build with gcc -march=native (gcc version and -O level not stated). Current benches/README (ARM update 2022-08-27): Rust 1.62, clang 13, Skia v90; no extra flags on ARM. |
| **Adoption** | 1.6k stars; renderer behind resvg |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/linebender/tiny-skia) · [benchmark](https://github.com/linebender/tiny-skia/tree/main/benches) |

## Verdict

These are the project's own nightly cargo bench numbers. The x86 run (July 2021) used an AMD 3700X on Gentoo with tiny-skia built for SSE2 and for AVX2 (haswell), Skia built with clang and a forced raster-pipeline blitter, and cairo 1.16.0 from the system package (gcc -march=native). The ARM run (Aug 2022) used an Apple M1. Recounted from the gh-pages data, AVX2 beat cairo in 37 of 46 tests (geometric mean 2.24x). Dropping two unfair tests leaves 36 of 44 at 2.32x: 'Fill All' compares tiny-skia's overwrite (Pixmap::fill) with cairo's alpha-blended paint(), and 'Destination' is a no-op. On M1 the figure is 41 of 44 at 2.69x, but cairo's M1 times are 4.9-8.3x worse than its own 3700X times on basic fills while Skia's are unchanged, which points to an M1 cairo/pixman build without SIMD fast paths (the build is not documented).

## Use it when

- Pure-Rust CPU rendering of SVG-like content (paths, gradients, patterns, blend modes) without a C/C++ toolchain. It is the renderer behind resvg and has about 490 reverse dependencies on crates.io (iced_tiny_skia, typst-render, i-slint-core, cosmic-text among them).
- Work heavy in non-separable or exotic blend modes, bilinear or bicubic patterns, AA clipping or hairlines. On the 3700X AVX2 run it was faster than cairo on Screen (9.1x), bilinear patterns (3.9x), AA hairlines (4.4x), spirals (2.0x), AA clip (1.65x) and linear gradients (1.55x) (derived from page data).
- Small binaries and fast builds: the README cites about 14 KLOC, about 200 KiB added to the binary and builds in under 5 s, against multi-MiB Skia builds that need clang and gn.
- no_std or WebAssembly targets: the crate builds without std (no-std-float feature) and has SIMD128 and relaxed-SIMD code paths for wasm.

## Skip it when

- UI-style drawing dominated by solid rect fills and plain source-over blending. In tiny-skia's own x86 data cairo was 2.5-2.7x faster on Rect and Rect AA, 1.7x on Source Over, 3.2x on Plus and 2.6x on nearest-neighbour patterns (derived from page data); the default SSE2 build loses by more (Rect 0.31x).
- When you need the fastest CPU renderer. tiny-skia is slower than Skia in 41 of 45 x86 AVX2 tests (geometric mean 0.68x) and 41 of 45 M1 tests (0.51x), and that Skia was built with SK_FORCE_RASTER_PIPELINE_BLITTER, so stock Skia may be faster still. Blend2D was faster in 870 of 870 thesis cells (about 7.5x), and Vello CPU is faster in most cells (derived from page data).
- Text, GPU rendering, PDF, non-RGBA8888 pixel formats, conic segments or path effects beyond dashing. All are out of scope per the README, which also calls the project 'more of a research project', not a Skia replacement.
- C or C++ code bases: there is no C API in the repository. The catalogued tiny-skia-cpp port claims up to 1.9x faster than the Rust original.
- Performance-sensitive ARM use: issue 55 (open since 2022) reports 2-4x slower than Skia on M1, with rect fills up to 6x slower and gradients 2-3x slower.

## How it is fast

It ports SkRasterPipeline: each draw is compiled into a list of stage function pointers (load, shade, blend, store) that run over 8 or 16 pixels at a time with no branching inside stages. If every stage has a low-precision version, it runs the u16x16 'lowp' pipeline; otherwise it falls back to the f32 'highp' pipeline. On x86 the lowp path is scalar u16x16 code that LLVM auto-vectorises, with SSE2 by default and AVX2 only with -Ctarget-cpu=haswell; AArch64 uses explicit NEON. Coverage comes from Skia's scanline rasteriser, including dedicated anti-aliased hairline code for thin strokes, which is where it beats cairo's general stroker most (4.4x on AA hairlines).

## Compared with alternatives

Pick it over raqote, the other pure-Rust option, almost always: tiny-skia was faster in 40 of 41 comparable x86 tests (geometric mean about 5.8x, derived from page data) and has proper AA hairlines. Pick Vello CPU or Blend2D when speed matters more than a small, stable, dependency-light pure-Rust crate.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | arrayvec, bytemuck, cfg-if, log, tiny-skia-path; png optional (default feature png-format) |
| **Minimum toolchain** | Rust stable (README says 'MSRV: stable'; no rust-version in Cargo.toml; edition 2021). Benchmarks need nightly. |
| **Platforms** | any Rust target; SIMD on x86-64 (SSE2 by default, AVX2 only at compile time with -Ctarget-cpu=haswell, no runtime dispatch), AArch64 NEON, wasm32 SIMD128/relaxed SIMD; scalar elsewhere |
| **Thread safety** | Not documented. No internal threading; each call renders into a caller-owned Pixmap. |
| **Drop-in for the baseline** | no |

## Gotchas

- There is no runtime CPU detection, so the headline AVX2 numbers need a non-portable -Ctarget-cpu=haswell build. A default x86-64 build matches the SSE2 column: faster than cairo in 34 of 44 comparable tests, geometric mean 1.71x, against 2.32x for AVX2 (derived from page data).
- There is no global alpha (only Pattern has opacity), clipping goes through a full alpha Mask (README: Skia's method is 'way faster'; issue 10 on faster rectangular clips is open since 2020), and Pixmap has no stride (issue 168).
- Open panic and assertion reports: issue 100 (non-anti-aliased hairline stroke of a full-width rectangle), 51 (ClipMask debug_assert) and 167 (assertion in path.rs). Recent rendering bugs: 189 (hairline curve just outside the canvas is offset) and 179 (rounded-rect corner artefact at small sizes).
- Stroke cost jumps once a stroke stops being a hairline: issue 158 reports width 2.0 as 'considerably slower' than width 1.0, because thin strokes take the hairline fast path.

## Known shortcomings

- Rust library (language-filter mismatch; C++ use via tiny-skia-cpp port or FFI). Tier A on its benches/ harness with stated compilers, flags and CPUs (AMD 3700X, Apple M1; gh-pages x86_64.html 2021 and arm.html 2022): beats Cairo in 41 of 49 x86 AVX2 tests (geomean 2.27x) and 46 of 49 ARM tests (2.7x), derived from page data; Cairo wins solid rectangle fills and nearest-neighbour patterns. Slower than Skia throughout; the Cairo baseline is a system gcc -march=native build, so a strict reading caps the Cairo comparison at B.
- Harness flaws (retier-16 corrects the claim): the Fill All test compares tiny-skia's Pixmap::fill overwrite with cairo's paint() alpha blend and Skia's draw_color blend, so its 5.1x x86 and 62x ARM wins are invalid; the Destination operator is a no-op; the bicubic row compares cairo Filter::Best with tiny-skia bicubic. Recount against cairo on x86: 36 of 44 valid tests at a 2.32x geometric mean with AVX2, 34 of 44 at 1.71x on the default SSE2 build. The M1 cairo build appears to lack NEON (its basic fills are 4.9-8.3x slower than on the 3700X while Skia is unchanged; undocumented). Skia was handicapped with SK_FORCE_RASTER_PIPELINE_BLITTER, and the 2021 benches README says Skia v85 while the build steps check out m90.

## Caveats and trade-offs

Rust library (language-filter mismatch). Slower than Skia on its own benchmarks; the claim is relative to cairo (and raqote) only. Results are old (x86 page July 2021, ARM page Aug 2022) and the current benches/README environment block (Rust 1.62, clang 13, Skia v90) was written for the 2022 ARM run, not the x86 page; cairo's build is a distro package with only -march=native stated (macOS cairo build for the ARM run not described). Cairo is faster on solid rect fills and nearest-neighbour patterns in tiny-skia's own data. The Vello CPU master thesis (LaurenzV/master-thesis main.pdf, M1 Pro, Blend2D harness with tiny_skia_c bindings, times per 1000 render calls) shows the same split: cairo faster on Fill-Solid-RectA (256x256: 18.6 ms vs 136 ms) and RectU, nearest-neighbour patterns and larger linear-gradient rects, while tiny-skia is about 1.1-2.3x faster than cairo on PolyNZi40 (small sizes), Fish and World fills and on World and Butterfly strokes; tiny-skia is slower than Skia and Vello CPU in most shown tests.

A minimal Skia subset ported to Rust (about 14k lines, about 200KB, no text, no GPU); not a Skia replacement. Needs FFI from C++.

## Maintenance

Maintained but quiet under Linebender: last release 0.12.0 (2026-02-02), and commits since September 2024 are features and maintenance, not performance work; the published benchmarks date from 2021/2022. BSD-3-Clause, about 51.7M crates.io downloads, easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the blocked results pages are readable from the gh-pages branch (x86_64.html, arm.html hold per-test ns for tiny-skia, Skia, cairo, raqote), the benchmark code is public (benches/src, benches/Cargo.toml with cairo-rs/skia-rs/raqote features, gen-charts-\*.py), and benches/README.md states compilers and flags (rustc with -Ctarget-cpu=x86-64/haswell; Skia via clang with -march=x86-64/haswell and listed gn args; cairo 1.16.0 system gcc build with -march=native) and CPUs (AMD 3700X on Gentoo; Apple M1).
- **Verifier notes:** Results pages on linebender.github.io are blocked but the same files are on the gh-pages branch via raw.githubusercontent.com; the per-test data supports 'faster than cairo in many cases' with stated compilers, flags and CPUs, hence the upgrade to A. Cairo build details are thin (system package), so the orchestrator may prefer B/C if strict about baseline flags. Metadata confirmed: BSD-3-Clause, 1.6k stars, not archived, last commit 2026-08-20; Rust, outside the C++ filter.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/README.md>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/gen-charts-x86.py>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/gh-pages/x86_64.html>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/gh-pages/arm.html>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/48d21dfb95ae80675faec14c56dee5f4c66d3613/benches/README.md>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/48d21dfb95ae80675faec14c56dee5f4c66d3613/README.md>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/a6a1c13d1211d5371554bb2b842252463fb3495a/benches/README.md>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/a6a1c13d1211d5371554bb2b842252463fb3495a/README.md>
  - <https://github.com/linebender/tiny-skia>
  - <https://github.com/linebender/tiny-skia/tree/main/benches>
  - <https://github.com/linebender/tiny-skia/commits/main>
  - <https://github.com/linebender/tiny-skia/commits/gh-pages>
  - <https://github.com/linebender/tiny-skia/commits/gh-pages/x86_64.html>
  - <https://github.com/linebender/tiny-skia/commits/main/benches/README.md>
  - <https://raw.githubusercontent.com/LaurenzV/master-thesis/HEAD/main.pdf>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/README.md>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/src/pixmap.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/src/pipeline/mod.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/src/pipeline/lowp.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/src/main.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/src/fill.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/src/blend.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/src/patterns.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/src/hairline.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/src/clip.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/src/gradients.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/benches/src/spiral.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/48d21dfb95ae80675faec14c56dee5f4c66d3613/benches/README.md>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/a6a1c13d1211d5371554bb2b842252463fb3495a/benches/README.md>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/gh-pages/x86_64.html>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/gh-pages/arm.html>
  - <https://github.com/linebender/tiny-skia/tree/main/benches>
  - <https://github.com/linebender/tiny-skia/tree/main/benches/src>
  - <https://github.com/linebender/tiny-skia/commits/main>
  - <https://github.com/linebender/tiny-skia/issues?q=is%3Aissue+slow+OR+performance+OR+panic>
  - <https://github.com/linebender/tiny-skia/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/linebender/tiny-skia/issues/174>
  - <https://github.com/linebender/tiny-skia/issues/158>
  - <https://github.com/linebender/tiny-skia/issues/55>
  - <https://crates.io/api/v1/crates/tiny-skia>
  - <https://crates.io/api/v1/crates/tiny-skia/reverse_dependencies?per_page=10>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/linebender/tiny-skia`) · [data/wave10/enrich/raw/github_com_linebender_tiny_skia.json](../../../data/wave10/enrich/raw/github_com_linebender_tiny_skia.json) (enrichment confidence 0.75)

</details>
