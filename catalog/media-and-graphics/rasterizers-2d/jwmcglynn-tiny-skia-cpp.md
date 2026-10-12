# tiny-skia-cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> C++20 port of Rust tiny-skia (Skia-subset CPU rasterizer) with AVX2/NEON backends; first-party 1.2-1.9x faster than the Rust original.

| | |
|---|---|
| **Beats** | Rust tiny-skia (linebender/tiny-skia, a Skia subset) |
| **Claimed result** | README: up to 1.9x faster than Rust tiny-skia at 512x512, normalized to Rust = 1.0x: FillRect 1.9x ARM (NEON) and 1.3x x86 (AVX2+FMA); FillPath 1.4x ARM and 1.2x x86; C++ SIMD over C++ scalar up to 2.3x (x86) and 1.9x (ARM). The x86 ratios compare an AVX2+FMA C++ build with a Rust build that has no AVX enabled. The regression test's calibrated baselines (tests/benchmarks/run_render_perf_regression_test.sh) match the README on x86 (simd_over_rust 1.18 FillPath, 1.29 FillRect) but not on arm64 (simd_over_rust 2.90 FillPath and 3.50 FillRect; simd_over_scalar 2.80 and 3.90), so the README's ARM figures and the calibration disagree. No raw result files are published. |
| **Workload** | 512x512 FillRect and FillPath rendering, C++ SIMD backend vs the Rust tiny-skia implementation, normalized to Rust = 1.0x (ARM measured on Apple Silicon NEON, x86 on Intel/AMD with AVX2+FMA). |
| **Metric** | throughput |
| **Hardware** | Apple Silicon (NEON) and Intel/AMD (AVX2+FMA), exact CPU models not stated |
| **Compiler and flags** | Bazel -c opt. C++ library copts: -std=c++20 -ffp-contract=off -Wall -O3, plus -mavx2 -mfma for the native x86 build (bazel/defs.bzl); host C++ compiler and version not stated (CONTRIBUTING lists GCC 11+, Clang 14+ or MSVC 19.30+ as supported). Rust tiny-skia 0.12.0 is built through rules_rust 0.71.3 as a rust_static_library with no rustc target-cpu or target-feature flags (tests/rust_ffi/BUILD.bazel, MODULE.bazel), so it runs SSE2 code on x86-64; tiny-skia's README says AVX needs -Ctarget-cpu=haswell. Google Benchmark 1.9.5: 5 repetitions, min_time 0.2 s, mean real time; the Rust time is the average of its runs in the native and scalar binaries. |
| **Adoption** | 9 stars |
| **Last commit** | 2026-07-04 |
| **Links** | [repository](https://github.com/jwmcglynn/tiny-skia-cpp) · [benchmark](https://github.com/jwmcglynn/tiny-skia-cpp) |

## Verdict

First-party Google Benchmark runs (RenderPerfBench.cpp, 5 repetitions, mean real time) of one 512x512 anti-aliased FillRect and one FillPath, C++ AVX2+FMA or NEON build against Rust tiny-skia 0.12.0 called through FFI, on unnamed Apple Silicon and Intel/AMD machines with an unstated compiler: README 1.9x/1.3x (FillRect, ARM/x86) and 1.4x/1.2x (FillPath). The README chart matches the 2026-03-03 calibration in run_render_perf_regression_test.sh (arm64 1.42 FillPath, 1.91 FillRect; x86 1.18 and 1.29) and was never updated; later arm64 calibrations rose to 2.00/2.80 (2026-03-05) and 2.90/3.50 (2026-04-02), so the ARM numbers are stale rather than contradicted, while the x86 side still compares AVX2+FMA C++ with SSE2-only Rust.

## Use it when

- A C++ program needs a small, dependency-free, BSD-licensed CPU rasterizer with Skia-style semantics (SVG-like paths, strokes, gradients, patterns, masks), for example SVG rendering, thumbnails or offscreen chart output.
- You are porting Rust tiny-skia or resvg-style rendering code to C++ and want output that matches the Rust crate within a golden-image tolerance.
- ARM64 / Apple Silicon targets, where the project's own numbers show the largest gain over Rust tiny-skia (README 1.4-1.9x; later calibrated baselines 2.9-3.5x).
- You need SVG filter primitives (blur, colour matrix, lighting, displacement, turbulence) in C++ without pulling in a browser engine or Skia.

## Skip it when

- Maximum CPU rendering throughput: it is measured only against Rust tiny-skia, which its own README puts 20-100% slower than Skia on x86-64 and 100-300% slower on ARM; on the independent bl_bench M1 Pro run, Blend2D, Vello CPU and the JUCE renderer (3.09x Rust tiny-skia, derived from page data) are far ahead of Rust tiny-skia, and none of them has been compared with this port.
- Portable x86-64 binaries: the native target is compiled with -mavx2 -mfma (CMake and Bazel) with no runtime dispatch, so it faults on CPUs without AVX2 and FMA (the author's Donner issue #1286 says this of the vendored copy); ship the tiny_skia_scalar target or per-ISA builds instead.
- Text rendering: like Rust tiny-skia (whose README lists text as the main missing feature), the drawing API is fillRect, fillPath, strokePath, drawPixmap and applyMask only.
- You need bit-exact Rust tiny-skia output: analytic AA and other changes make it near-pixel-accurate only.
- Low risk tolerance: 9 stars, one maintainer with many commits co-authored by an AI assistant, no tagged releases seen, and an out-of-bounds pixel write in the anti-aliased blitter fixed only on 2026-07-04 (PR #30).

## How it is fast

Rendering goes through a port of Skia's raster pipeline (high-precision float and low-precision 16-bit stage paths) whose vector types (F32x8T, U16x16T and friends in src/tiny_skia/wide/) are hand-written for AVX2+FMA on x86-64 and NEON on ARM64, selected at compile time, with a scalar fallback. Since 2026-04-02 anti-aliased path fills use a port of Skia's Analytic Anti-Aliasing rasterizer (SkScan_AAAPath, src/tiny_skia/scan/PathAa.cpp), which computes exact edge coverage instead of the supersampled scanlines Rust tiny-skia uses. Axis-aligned anti-aliased rectangles take a dedicated fillRectAa path with no edge building.

## Compared with alternatives

Pick it over Rust tiny-skia when the host program is C++ and you want the same rendering model with native SIMD and SVG filters; pick Blend2D or AGG instead when raw speed or a long track record matters, since this port has never been measured against them, Skia or Cairo.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at runtime; the tests and benchmarks use GoogleTest, Google Benchmark and a Rust toolchain (rules_rust) for the tiny-skia FFI cross-checks |
| **Minimum toolchain** | C++20; GCC 11+, Clang 14+ or MSVC 19.30+ (CONTRIBUTING); Bazel 7+ or CMake 3.16+ |
| **Platforms** | x86-64 (native target requires AVX2+FMA), ARM64 (NEON), any other target via the scalar library; CI builds Bazel on Ubuntu and CMake on Ubuntu and macOS, with no Windows CI |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — same object model and algorithms as Rust tiny-skia (Pixmap, PathBuilder, Paint, Transform) in C++ naming, so Rust call sites port mechanically, but it is a C++ library, not a crate, and its output is not bit-exact |

## Gotchas

- SIMD backend is chosen at compile time: link tiny_skia (native) or tiny_skia_scalar deliberately, and on x86 the native build assumes AVX2+FMA on every target machine.
- Versions before PR #30 (merged 2026-07-04) could read or write one pixel past the pixmap in RasterPipelineBlitter::blitAntiH2/blitAntiV2 when an anti-aliased edge touched the right or bottom edge; use a later commit.
- Anti-aliased fillPath uses Skia's analytic AA, not Rust tiny-skia's supersampling, so edge pixels differ slightly from the Rust crate; the golden-image tests compare with a tolerance.
- The library compiles with -ffp-contract=off; if you vendor the sources into a build without it (or with -ffast-math), float rounding may drift from the golden images (inference from the build files).

## Known shortcomings

- Port of linebender/tiny-skia (catalogued at A in this wave), so a possible duplicate; its baseline is the Rust original, not a listed incumbent. The x86 comparison is unfair: the C++ build uses -mavx2 -mfma while the Rust tiny-skia was built without AVX, and FillPath runs analytic anti-aliasing against the Rust path. README ARM figures (1.9x/1.4x) conflict with the committed regression baselines (3.50/2.90).
- A C++ port of the listed linebender/tiny-skia (duplicate rule would apply; kept because it adds analytic anti-aliasing and SVG filters). The README chart is stale: it matches the 2026-03-03 calibration (arm64 1.42/1.91, x86 1.18/1.29) while later arm64 calibrations read 2.00/2.80 and 2.90/3.50 (2026-04-02). Flaws: the timed loop clears the pixmap (memset in C++, a per-pixel store loop in Rust); FillPath since April 2 is analytic AA against Rust supersampling; the regression guard is skipped in CI (no -c option); x86 compares AVX2 against SSE2. The native target needs AVX2 plus FMA with no runtime dispatch (illegal instruction elsewhere). PR #30 (2026-07-04) fixed a one-pixel out-of-bounds write in blitAntiH2/V2 (benchmark shapes never touch the edge).

## Caveats and trade-offs

C++ port of linebender/tiny-skia, benchmarked only against its own Rust original, not against Skia, Cairo or Blend2D. On x86 the comparison is unequal: the C++ side is compiled with -mavx2 -mfma, the Rust side without AVX. On FillPath the two sides run different anti-aliasing algorithms: the C++ port fills anti-aliased paths with analytic AA (src/tiny_skia/scan/PathAa.cpp, ported from Skia's SkScan_AAAPath.cpp), which the README names as one reason its output is not bit-exact with Rust tiny-skia. The README's ARM ratios disagree with the arm64 baselines in the regression test (2.90x and 3.50x). Only two workloads at one size; CPU models and compiler versions not stated. Rust tiny-skia's README says it is 20-100% slower than Skia on x86-64 and 100-300% slower on ARM, so a 1.2-1.9x gain over it does not show the port beats Skia (inference). 9 stars, 156 commits; the latest commits (2026-07-04) are mostly renovate[bot] dependency bumps alongside one author commit.

CPU-only C++20 port of the Skia-subset algorithms with x86-64 AVX2+FMA and ARM64 NEON backends plus a scalar fallback, zero dependencies, Bazel or CMake. Output is near-pixel-accurate against Rust tiny-skia, not bit-exact (extra analytic AA and filter primitives). Only a subset of Skia features.

## Maintenance

Active but small (156 commits, 9 stars, last author commit 2026-07-04, then only renovate[bot] dependency PRs); BSD-3-Clause and dependency-free so easy to vendor, and the author also vendors it as the default CPU renderer in jwmcglynn/donner (third_party/tiny-skia-cpp), whose copy already adds a wasm simd128 backend the standalone repo lacks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README chart with public Google Benchmark code (tests/benchmarks/RenderPerfBench.cpp, run_render_perf_compare.sh) and flags readable from bazel/defs.bzl, but no compiler version, no CPU models and no published result files, so C.
- **Verifier notes:** Possible duplicate or port: the baseline is the project's own original, linebender/tiny-skia, which wave 10 batch-03 already confirmed at tier A; the orchestrator may want decision duplicate, or keep it as the C++ form of that entry. Numbers on the README match the record, but the x86 build is ISA-mismatched and the ARM figures conflict with the repo's own calibrated regression baselines. Metadata checked: BSD-3-Clause, 9 stars, last commit 2026-07-04, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/HEAD/README.md>
  - <https://github.com/jwmcglynn/tiny-skia-cpp>
  - <https://github.com/jwmcglynn/tiny-skia-cpp/commits/main>
  - <https://github.com/jwmcglynn/tiny-skia-cpp/tree/main/tests/benchmarks>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/benchmarks/README.md>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/benchmarks/RenderPerfBench.cpp>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/benchmarks/run_render_perf_compare.sh>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/benchmarks/run_render_perf_regression_test.sh>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/benchmarks/BUILD.bazel>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/bazel/defs.bzl>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/.bazelrc>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/MODULE.bazel>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/rust_ffi/BUILD.bazel>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/rust_ffi/Cargo.toml>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/CONTRIBUTING.md>
  - <https://github.com/jwmcglynn/tiny-skia-cpp/tree/main/src/tiny_skia/scan>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/src/tiny_skia/scan/PathAa.cpp>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/src/tiny_skia/Painter.cpp>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/jwmcglynn/tiny-skia-cpp>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/README.md>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/AGENTS.md>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/BUILD.bazel>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/MODULE.bazel>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/.bazelrc>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/bazel/defs.bzl>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/.github/workflows/cmake.yml>
  - <https://github.com/jwmcglynn/tiny-skia-cpp/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/benchmarks/README.md>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/benchmarks/RenderPerfBench.cpp>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/benchmarks/BUILD.bazel>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/benchmarks/run_render_perf_compare.sh>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/benchmarks/run_render_perf_regression_test.sh>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/d57568508b0eeefb29bd164226820fc086bb7fe0/tests/benchmarks/run_render_perf_regression_test.sh>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/71d4e0b3525491f6863d5b58f40a7714ca449d42/tests/benchmarks/run_render_perf_regression_test.sh>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/58bf9777e50afa521d47e55fc538415e7f52e2bd/tests/benchmarks/run_render_perf_regression_test.sh>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/5fbbb77b8f679db46bed783e00b4f8fb376735c5/tests/benchmarks/run_render_perf_regression_test.sh>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/3dd0987b4039ef2d55c161c02124825fa6d1faba/tests/benchmarks/run_render_perf_regression_test.sh>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/5fbbb77b8f679db46bed783e00b4f8fb376735c5/README.md>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/3dd0987b4039ef2d55c161c02124825fa6d1faba/README.md>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/rust_ffi/BUILD.bazel>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/rust_ffi/Cargo.toml>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/rust_ffi/Cargo.lock>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/tests/rust_ffi/src/lib.rs>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/src/tiny_skia/Pixmap.cpp>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/src/tiny_skia/Painter.cpp>
  - <https://raw.githubusercontent.com/jwmcglynn/tiny-skia-cpp/main/src/tiny_skia/scan/PathAa.cpp>
  - <https://github.com/jwmcglynn/tiny-skia-cpp/issues?q=is%3Aissue>
  - <https://github.com/jwmcglynn/tiny-skia-cpp/pulls?q=is%3Apr>
  - <https://github.com/jwmcglynn/tiny-skia-cpp/pull/30>
  - <https://github.com/jwmcglynn/tiny-skia-cpp/commits/main/README.md>
  - <https://github.com/jwmcglynn/tiny-skia-cpp/commits/main/tests/benchmarks/run_render_perf_regression_test.sh>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/v0.12.0/src/pixmap.rs>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/v0.12.0/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/tiny-skia/HEAD/README.md>
  - <https://github.com/jwmcglynn/donner>
  - <https://github.com/jwmcglynn/donner/issues/1286>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2026-06-08.json>
  - WebSearch: "tiny-skia-cpp" donner SVG renderer jwmcglynn
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/jwmcglynn/tiny-skia-cpp`) · [data/wave10/enrich/raw/github_com_jwmcglynn_tiny_skia_cpp.json](../../../data/wave10/enrich/raw/github_com_jwmcglynn_tiny_skia_cpp.json) (enrichment confidence 0.7)

</details>
