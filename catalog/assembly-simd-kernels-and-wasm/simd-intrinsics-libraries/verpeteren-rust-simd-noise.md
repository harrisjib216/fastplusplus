# SIMDNoise (simdnoise crate)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟡 stale

> Rust crate generating simplex, FBM, ridge, turbulence and cellular noise with SSE2/SSE4.1/AVX2 runtime dispatch; beats its own 1-lane scalar path.

| | |
|---|---|
| **Beats** | the crate's own scalar (non-SIMD) fallback implementation of the same noise generators |
| **Claimed result** | 2D 4k Fbm 3 octaves: scalar 888 ms, sse2 225 ms, sse41 186 ms, avx2 108 ms (avx2 about 8.2x vs scalar, derived from page data). 3D 128^3 cell noise: scalar 1,400 ms, sse2 128 ms, sse41 94 ms, avx2 47 ms (avx2 about 29.8x vs scalar, derived from page data). |
| **Workload** | Time to generate one 2D 4k (3840 x 2160) Fbm noise block with 3 octaves, and one 3D 128 x 128 x 128 cell noise block, single-threaded, measured with Criterion.rs. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700 @ 3.40GHz, single-threaded |
| **Compiler and flags** | Not stated (README names Criterion.rs only; rustc version and RUSTFLAGS absent, and the repo has no .cargo/config). Benchmark source is benches/benchmarks.rs; since the November 2024 simdeez v2 port the intrinsics::{sse41,avx2}::get_\*_noise functions carry no #[target_feature], so a default cargo bench at HEAD likely times out-of-line AVX2/SSE4.1 op calls (not run). |
| **Adoption** | 267 stars, 20 forks; crates.io simdnoise 81,004 total downloads (2,924 recent); latest published version 3.1.6 (2020-05-30), while the repo HEAD (3.1.7 on simdeez 2.0.0-dev3) is unpublished |
| **Last commit** | 2024-11-20 |
| **Links** | [repository](https://github.com/verpeteren/rust-simd-noise) · [benchmark](https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/README.md) |

## Verdict

First-party README table, added in commit 498bf3d (2019-03-05) by Jack Mott: on an i7-6700, single-threaded, Criterion.rs, rustc and RUSTFLAGS not stated, a 3840 x 2160 3-octave FBM block takes 888 ms on the crate's scalar path versus 108 ms with AVX2 (about 8.2x) and a 128^3 cellular block 1,400 ms versus 47 ms (about 29.8x), derived from page data. The baseline is the same generic code on simdeez's 1-lane Scalar engine, and the numbers predate the 3.1.x releases (August 2019 onward) and the November 2024 simdeez v2 port.

## Use it when

- Pure-Rust procedural content (terrain heightmaps, textures, voxel density fields) on x86-64 where whole 2D or 3D blocks of FBM, ridge, turbulence or cellular noise are generated at once.
- Large single-threaded blocks such as a 3840 x 2160 FBM map or a 128^3 cellular volume, where the README reports 8.2x (FBM) and 29.8x (cellular) over the crate's scalar path with AVX2.
- Projects that want automatic SSE2/SSE4.1/AVX2 selection at runtime without shipping separate binaries.
- Callers that already hold SIMD registers and want per-vector noise evaluation through the intrinsics module, wrapped in their own #[target_feature] function.

## Skip it when

- C++ codebases: there is no C or C++ API, and FastNoise2 is the native C++ SIMD option with comparisons against independent libraries.
- ARM or Apple Silicon targets that need SIMD speed: NEON and AVX-512 are TODO; HEAD falls back to scalar on aarch64, and the published 3.1.6 crate fails to compile on an M1 (issue #52, error E0425 for F32x4 in sse41.rs).
- Anyone who needs a maintained crates.io release: crates.io still serves 3.1.6 (2020-05-30, simdeez ^1.0.3); HEAD 3.1.7 is unpublished and pins the prerelease simdeez 2.0.0-dev3 although simdeez 2.0.0 and 3.0.1 are out; issue #35 'crates.io release' has been open since 2021.
- Workloads that need seamless or artifact-free output without checking: open issues report seams at high octaves and low frequency (#39), grid-like artifacts in turbulence_3d (#15), Cellular2 3D resetting when z changes (#37) and weak seed randomness (#42).
- Windows MSVC builds of 3D AVX2 noise from git HEAD: issue #38 reports a stack overflow (forced #[inline(always)] creates a single frame above the __chkstk limit); the 3.1.6 release is not affected.

## How it is fast

Each noise function is written once as generic code over simdeez's Simd trait and instantiated for SSE2 (4 lanes), SSE4.1 (4 lanes) and AVX2 with FMA3 (8 lanes); block generation walks the grid a full vector of x coordinates at a time and keeps running min/max in registers. The top-level get_\*_noise functions use simdeez's simd_runtime_generate! macro, which checks is_x86_feature_detected! once and runs the body inside a #[target_feature]-enabled closure so the intrinsics inline. The 'scalar' path is the same generic code on simdeez's 1-lane Scalar engine, not a separately tuned scalar implementation.

## Compared with alternatives

Pick SIMDNoise over FastNoise2 only when you need pure Rust without a C++ build or FFI layer and x86 SSE2/AVX2 is enough; FastNoise2 has more noise types, ARM NEON and AVX-512 support, and benchmarks against independent libraries (FastNoise Lite, libnoise, stb_perlin) rather than its own scalar path.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | simdeez 2.0.0-dev3 at HEAD (prerelease pin); simdeez ^1.0.3 in the published 3.1.6 |
| **Minimum toolchain** | Rust edition 2018, stable rustc (CI builds on stable); MSRV not documented |
| **Platforms** | x86 and x86-64 with SSE2, SSE4.1 or AVX2+FMA3 picked at runtime; other targets use the scalar engine at HEAD only |
| **Thread safety** | not documented; generators are pure functions that take settings by value or reference, read static permutation tables and return a new Vec, so concurrent calls look safe, but the project does not state it |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw at HEAD: since the November 2024 simdeez v2 port, simdnoise::intrinsics::{sse41,avx2}::get_\*_noise are plain generic functions without #[target_feature], while simdeez 2.0.0-dev3 marks every AVX2/SSE4.1 op #[inline] #[target_feature(enable = ...)]; benches/benchmarks.rs calls them straight from Criterion closures (the repo's own tests wrap each call in a #[target_feature] function) and the repo has no RUSTFLAGS or .cargo/config (removed 2024-11-19), so a default cargo bench at HEAD likely times out-of-line op calls for the sse41 and avx2 rows (not run here). The README table is not from this harness: it first appears in commit 498bf3d (2019-03-05), when the avx2 entry points carried #[target_feature(enable = "avx2")].
- The baseline is simdeez's 1-lane Scalar engine running the same generic SIMD code (the 2019 scalar.rs instantiates cellular_3d::&lt;Scalar&gt; on F32x1), not a hand-written scalar generator or a third-party library; the superlinear 10.9x SSE2 gain on 4 lanes for 3D cellular noise points to emulation overhead in that path. Earlier README tables on the same i7-6700 (June-July 2018) showed only 3.6-6.7x for AVX2 FBM. The committed golden outputs at HEAD agree between scalar and SIMD paths within 8.7e-5 (3D cellular) and 1.9e-6 (2D FBM), derived from tests/assets, so the paths do compute the same function.
- fbm_1d (f32 and f64) updates amp each octave but never multiplies the octave by it, so 1D FBM ignores the gain setting while the 2D-4D versions apply it (fbm_4d itself was fixed in 2024 for using only 3 dimensions).
- Tests lock in current output rather than cross-checking paths: the scalar-versus-SIMD consistency tests in src/lib.rs are commented out, test assets were regenerated on 2024-11-18 ('accept current implementation as-is'), four f64 SSE2 tests are #[ignore]d, and the README's 'call noise functions directly' example uses pre-port signatures (no ::&lt;S&gt; type argument, simplex_2d without seed) that do not compile against HEAD.

## Known shortcomings

- Baseline is the crate's own scalar fallback and the SSE2 cell-noise gain is superlinear (10.9x on 4 lanes); the README table dates from June 2018, before the simdeez v2 rewrite; no LICENSE file (licence only in Cargo.toml); loose category fit; last publish 3.1.6 on 2020-05-30.
- Harness flaw at HEAD: since the November 2024 simdeez v2 port, intrinsics::{sse41,avx2}::get_\*_noise have no #[target_feature], and benches/benchmarks.rs calls them straight from Criterion closures while the tests wrap the same calls in #[target_feature]; the repo has no RUSTFLAGS and no .cargo/config, so a default cargo bench at HEAD likely times out-of-line AVX2/SSE4.1 op calls (not run). The baseline is simdeez's 1-lane Scalar engine running the same generic code, not a tuned scalar path. Correction: the README table first appears in commit 498bf3d (2019-03-05), not June 2018; the 2018 tables showed only 3.6-6.7x. Committed golden outputs show scalar and SIMD agree within 8.7e-5 (3D cellular) and 1.9e-6 (2D FBM), but the scalar-vs-SIMD consistency tests are commented out; fbm_1d (f32, f64) ignores gain; the README direct-call example does not compile against HEAD; the published crate is still 3.1.6 (simdeez ^1.0.3).

## Caveats and trade-offs

Baseline is the crate's own scalar fallback, not a third-party library (no comparison with FastNoise/FastNoiseSIMD or noise-rs), so the claim shows the benefit of SIMD for this algorithm rather than a win over an independent incumbent. The scalar-to-SSE2 gain on 3D cell noise is 10.9x on 4 lanes (1,400 to 128 ms, derived from page data), which is superlinear and suggests a weak scalar fallback rather than an optimised scalar baseline. The README benchmark table comes from Jack Mott's June 2018 commits ('updated benchmarks'), long before the November 2024 port to simdeez v2, so the numbers do not describe the current code or the published 3.1.6 crate exactly. Compiler version and flags are not stated. In benches/benchmarks.rs the Criterion sample_size and measurement_time settings are applied after the bench_function calls, so they do not take effect. i7-6700 is a 2015 CPU. The repo was transferred from jackmott/rust-simd-noise (that URL now resolves here) and is maintained by Peter Reijnders. There is no LICENSE file in the repo; the licence is declared only in Cargo.toml as 'Apache-2.0/MIT' (same on crates.io). The HN thread was seen only as a search-result title. It is a SIMD noise-generation library built on simdeez rather than an intrinsics wrapper, so the category is a loose fit. [retier] Baseline is the crate's own scalar fallback, simdeez's 1-lane Scalar engine running the same generic SIMD code (not a hand-written scalar generator or a third-party library such as FastNoise/FastNoiseSIMD or noise-rs); the superlinear 10.9x SSE2 gain on 4 lanes for 3D cellular noise points to emulation overhead in that path, so the claim shows the benefit of SIMD for this algorithm rather than a win over an independent incumbent. The README benchmark table first appears in commit 498bf3d (2019-03-05); earlier 2018 tables on the same i7-6700 showed only 3.6-6.7x for AVX2 FBM. Harness flaw at HEAD: since the November 2024 simdeez v2 port the intrinsics entry points have no #[target_feature] while simdeez 2.0.0-dev3 marks every AVX2/SSE4.1 op #[inline] #[target_feature], and benches/benchmarks.rs calls them straight from Criterion closures (the tests wrap the same calls in #[target_feature] functions) with no RUSTFLAGS or .cargo/config, so a default cargo bench likely times out-of-line op calls. Committed golden outputs show scalar and SIMD agree within 8.7e-5 (3D cellular) and 1.9e-6 (2D FBM), but the scalar-vs-SIMD consistency tests in src/lib.rs are commented out, test assets were regenerated on 2024-11-18 ('accept current implementation as-is') and four f64 SSE2 tests are ignored. Library bug: fbm_1d (f32 and f64) ignores the gain setting. The README's direct-call example uses pre-port signatures that do not compile against HEAD; the published crate is still 3.1.6 (simdeez ^1.0.3).

Rust crate, not directly callable from C++ without an FFI wrapper. x86 only (SSE2, SSE4.1, AVX2 plus FMA3, runtime detection picks the best set); README lists AVX-512 and ARM NEON as TODO. Output is noise generation only, not a general SIMD wrapper.

## Maintenance

Stale (last commit 2024-11-20, 'port benchmarks to simdeez v2'; latest crates.io release 3.1.6 from 2020-05-30, about 81k downloads), dual Apache-2.0/MIT declared only in Cargo.toml, and HEAD depends on a simdeez prerelease, so pin a git revision or vendor it and benchmark your own block sizes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table (i7-6700, single-threaded, Criterion.rs) gives scalar 888 / sse2 225 / sse41 186 / avx2 108 ms for 2D 4k Fbm and 1,400 / 128 / 94 / 47 ms for 3D 128^3 cell noise, with bench code in benches/benchmarks.rs; rustc version and RUSTFLAGS are not stated and the table predates the current code, so C.
- **Verifier notes:** Numbers, CPU and Criterion note all on the README; metadata confirmed (267 stars, last commit 2024-11-20 'port benchmarks to simdeez v2', stale). Shortcomings: self-baseline (own scalar fallback, superlinear 10.9x SSE2 gain on cell noise), 2018 numbers predating the simdeez v2 rewrite, no licence file in repo (Cargo.toml only), loose category fit.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-96 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/README.md>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/benches/benchmarks.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/noise_builder.rs>
  - <https://raw.githubusercontent.com/jackmott/rust-simd-noise/HEAD/README.md>
  - <https://github.com/verpeteren/rust-simd-noise>
  - <https://github.com/verpeteren/rust-simd-noise/commits>
  - <https://github.com/verpeteren/rust-simd-noise/commits/master/README.md>
  - <https://github.com/jackmott/rust-simd-noise>
  - <https://crates.io/api/v1/crates/simdnoise>
- **Sources the enricher read:**
  - <https://github.com/verpeteren/rust-simd-noise>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/README.md>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/benches/benchmarks.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/noise_builder.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/noise_helpers_32.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/shared.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/intrinsics/mod.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/settings/fbm_settings.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/settings/mod.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/intrinsics/avx2.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/intrinsics/sse2.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/intrinsics/scalar.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/noise/fbm_32.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/noise/fbm_64.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/noise/cell_32.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/src/noise/simplex_32.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/tests/helpers.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/tests/intrinsics.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/tests/noisebuilder.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/tests/assets/intrinsics_cellular_32_3d_scalar_normal.bin>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/tests/assets/intrinsics_cellular_32_3d_avx2_normal.bin>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/tests/assets/intrinsics_fbm_32_2d_scalar_normal.bin>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/tests/assets/intrinsics_fbm_32_2d_avx2_normal.bin>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/HEAD/.github/workflows/rust.yml>
  - <https://github.com/verpeteren/rust-simd-noise/tree/master/src>
  - <https://github.com/verpeteren/rust-simd-noise/tree/master/src/intrinsics>
  - <https://github.com/verpeteren/rust-simd-noise/tree/master/tests>
  - <https://github.com/verpeteren/rust-simd-noise/tree/master/.github/workflows>
  - <https://github.com/verpeteren/rust-simd-noise/commits>
  - <https://github.com/verpeteren/rust-simd-noise/commits/master/README.md>
  - <https://github.com/verpeteren/rust-simd-noise/commits/master/.cargo/config>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/77fd20d/.cargo/config>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/91603f2/.cargo/config>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/10a9097/README.md>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/87c75e9/README.md>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/498bf3d/README.md>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/498bf3d/benches/benchmarks.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/498bf3d/src/avx2.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/498bf3d/src/scalar.rs>
  - <https://raw.githubusercontent.com/verpeteren/rust-simd-noise/498bf3d/src/lib.rs>
  - <https://github.com/verpeteren/rust-simd-noise/issues>
  - <https://github.com/verpeteren/rust-simd-noise/issues/38>
  - <https://github.com/verpeteren/rust-simd-noise/issues/52>
  - <https://crates.io/api/v1/crates/simdnoise>
  - <https://crates.io/api/v1/crates/simdnoise/3.1.6/dependencies>
  - <https://crates.io/api/v1/crates/simdeez>
  - <https://crates.io/api/v1/crates/simdeez/2.0.0-dev3/download>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/verpeteren/rust-simd-noise`) · [data/wave13/enrich/raw/github_com_verpeteren_rust_simd_noise.json](../../../data/wave13/enrich/raw/github_com_verpeteren_rust_simd_noise.json) (enrichment confidence 0.75)

</details>
