# RustFFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pure-Rust SIMD FFT for any length, including primes; beats a scalar, per-call-planned FFTW 3.3.8 at tiny and huge sizes.

| | |
|---|---|
| **Beats** | FFTW 3.3.8 (via the Rust fftw crate v0.8.0, built from source by fftw-src without any SIMD configure flag, FFTW_ESTIMATE plan created inside each timed call) |
| **Claimed result** | Table medians, forward / inverse, plan creation included in the timed region for both libraries. f32 N=8,388,608: RustFFT 103.9 / 103.6 ms vs FFTW 193.3 / 192.9 ms (about 1.86x, derived from page data); f32 N=16: 124.6 / 94.09 ns vs 1.405 / 1.416 us; f32 N=1,048,576: 12.49 / 12.58 ms vs 14.20 / 13.13 ms (about 1.14x forward, derived from page data); f64 N=65,536: 754.4 / 774.5 us vs 953.5 / 966.9 us (about 1.26x forward, derived from page data). RustFFT is SLOWER than this FFTW build at f32 N=1024 (7.707 vs 7.291 us), N=2048 (22.87 vs 11.74 us, FFTW about 1.95x faster, derived from page data), N=4096 (45.33 vs 21.20 us), N=8192 forward (84.08 vs 45.62 us), N=16384 both directions (156.7 / 225.2 vs 101.1 / 180.0 us), and at f64 N=1024 (8.624 vs 7.749 us), N=2048 (18.49 vs 12.54 us) and N=524,288 (9.427 vs 7.911 ms). The author's conclusion 'fftw was consistently slower than both rustfft and phastft' is contradicted by the page's own table for RustFFT. |
| **Workload** | Single-threaded in-place complex-to-complex forward and inverse FFT, f32 and f64, power-of-two lengths 8 to 8,388,608, divan medians, in the third-party astral4/fft-benchmark on an M1 MacBook Pro. Each timed call includes planning: FFTW builds a C2CPlan with FFTW_ESTIMATE \| DESTROYINPUT and executes it; RustFFT calls plan_fft_forward/inverse on a fresh FftPlanner (created in untimed setup) and processes. |
| **Metric** | latency |
| **Hardware** | M1 MacBook Pro |
| **Compiler and flags** | rustc 1.80.0-nightly (d2d24e395 2024-05-03); Cargo.toml [profile.bench] lto = true, strip = true (cargo bench default opt-level 3), no target-cpu or RUSTFLAGS stated; rustfft v6.2.0; fftw crate v0.8.0 default 'source' feature: fftw-src build.rs runs FFTW 3.3.8 './configure --with-pic --enable-static --disable-doc' (plus --enable-single for f32), no SIMD flag, compiled with Apple clang 15.0.0 (clang-1500.0.40.1) |
| **Adoption** | 942 stars; 30M+ crates.io downloads (30,150,241 at time of query) |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/ejmahler/RustFFT) · [benchmark](https://github.com/astral4/fft-benchmark) |

## Verdict

In the third-party astral4/fft-benchmark on an M1 MacBook Pro (rustfft 6.2.0, single thread, divan medians), RustFFT beat FFTW 3.3.8 at N=8 to 32 (about 124 ns vs 1.4 us) and at large sizes (f32 2^20 12.49 ms vs 14.20 ms; 2^23 103.9 ms vs 193.3 ms), but lost at f32 N=1,024 to 16,384 and f64 N=1,024, 2,048 and 524,288. Both libraries planned inside every timed call, and FFTW was planned with FFTW_ESTIMATE and built by the fftw crate's default 'source' feature with no --enable-neon, so the result does not show RustFFT beating a SIMD, pre-planned FFTW; a 2020 Rust-forum post claiming RustFFT 5.0 AVX matched or beat FFTW at every size could only be seen as a search snippet (forum host egress-blocked).

## Use it when

- Rust code needing FFTs of arbitrary or prime lengths without a C dependency; sizes of the form 2^n \* 3^m are fastest under AVX per the crate docs.
- Very small transforms (N = 8 to 32), where it ran about 124 ns vs FFTW's 1.4 us in astral4's plan-included M1 run.
- One-shot transforms where planning cost counts, e.g. a few FFTs of many different sizes.
- WebAssembly targets (wasm_simd feature) and AArch64 with NEON, where it ships native SIMD paths.
- Large single-threaded power-of-two FFTs (2^21 and up) on Apple Silicon, where it beat both PhastFT and the scalar FFTW build in astral4.

## Skip it when

- C or C++ projects: there is no C ABI, and a user report of a hand-written FFI layer hitting double-free and segfaults (issue #148) is unanswered.
- Mid-size power-of-two FFTs (1K to 16K) on Apple M1: even a scalar FFTW_ESTIMATE build planned per call was faster there (e.g. f32 N=2048 11.74 us vs 22.87 us).
- Multi-threaded large transforms: no built-in threading is documented, while PhastFT's parallel feature and FFTW threads exist.
- Memory-tight huge FFTs: astral4 measured about 5x the allocations of PhastFT (335.5 MB vs 67.1 MB at 2^23 f32).
- Real-to-complex or multi-dimensional transforms: the crate exposes only 1-D complex FFTs (a 2-D example is still an open request, issue #146).

## How it is fast

The planner factors N and builds a recipe tree from Radix4/RadixN, MixedRadix (Cooley-Tukey), the Good-Thomas prime-factor algorithm, Rader's algorithm for primes and Bluestein's algorithm for primes with large factors, with hand-written butterflies for sizes 2 to 32. Each algorithm has AVX+FMA, SSE4.1, NEON (optional FCMA on ARMv8.3) and WASM SIMD versions, and the planner picks one by runtime CPU detection. Twiddles are precomputed at plan time and callers can reuse scratch buffers to avoid allocation.

## Compared with alternatives

Pick it over PhastFT when lengths are not powers of two, when transforms are tiny, or for single-threaded power-of-two sizes of 2^21 and up; pick PhastFT for lower memory and multi-core large FFTs. C++ users should look at PocketFFT (C++ branch), PFFFT or KFR instead, since RustFFT has no C interface.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | num-complex, num-traits, num-integer, strength_reduce, transpose, primal-check |
| **Minimum toolchain** | Rust 1.86 (crate v6.4.1); the fcma feature needs nightly |
| **Platforms** | any Rust target; runtime-detected AVX+FMA or SSE4.1 on x86-64, NEON on aarch64, opt-in WASM SIMD; scalar fallback elsewhere |
| **Thread safety** | Fft plans are Send + Sync (the trait requires both), so one Arc&lt;dyn Fft&gt; can be shared across threads; FftPlanner was made Sync in 6.3 (#153) |
| **Drop-in for the baseline** | no |

## Gotchas

- Building an algorithm directly (e.g. Radix4::new) bypasses the planner and disables all AVX, SSE, NEON and WASM SIMD paths.
- process() allocates a scratch Vec on every call; use process_with_scratch with get_inplace_scratch_len() to avoid it (Bluestein sizes may need scratch larger than N).
- wasm_simd cannot be runtime-detected: with the feature on, runtimes without fixed-width SIMD trap.
- Before 6.4.1, Rader's algorithm could panic with multiply overflow on 32-bit and wasm targets at sizes around 3.6M points (issue #163, fixed in 6.4.1 by using u64).

## Known shortcomings

- astral4/fft-benchmark handicaps the FFTW baseline: fftw-src builds FFTW 3.3.8 without SIMD (no --enable-neon), plans with FFTW_ESTIMATE and times plan creation on every call; a 5-star suite, not well known. Losses understated: RustFFT is slower at f32 N=1024-16384 and f64 N=1024, 2048 and 524288, so 'fftw consistently slower' is wrong. Pure Rust, no C ABI.
- No C API; a C++ FFI attempt hit double-free and segfaults (#148, no reply); Rader multiply-overflow panic on 32-bit/wasm (#163) fixed in 6.4.1.

## Caveats and trade-offs

Third-party, single-machine, Apple Silicon only, small repo (5 stars). The FFTW baseline is handicapped: built by the fftw-src crate with no --enable-neon (scalar codelets), planned with FFTW_ESTIMATE, and planning is timed on every call, which explains FFTW's \~1.4 us at N=8 to 32; so the results do not show RustFFT beating a SIMD-enabled, pre-planned FFTW. Even against this build RustFFT is slower at f32 N=1024 to 16384 and f64 N=1024, 2048 and 524,288. The ejmahler/RustFFT README and release notes state no benchmark numbers against FFTW (the 'now faster than FFTW' claim is a 2020 Rust forum post for 5.0.0-experimental.1 that could not be opened from this container). Pure Rust with no C ABI, so not callable from C++ without writing an FFI layer.

Pure Rust, no C API (C++ use needs an FFI wrapper). Any length including primes in O(n log n); AVX and SSE4.1 on x86_64, NEON on AArch64, optional wasm SIMD. Planner chooses the algorithm; large non-power-of-two sizes are slower than power-of-two. Memory use is about 5x PhastFT's in the same shootout.

## Maintenance

Active (last commit 2026-09-29, v6.4.1, about 30M crates.io downloads), MIT OR Apache-2.0 with a no-breaking-changes policy, but usable from C++ only through your own FFI wrapper.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** astral4/fft-benchmark (5 stars, not a well-known suite, so not B) publishes code (benches/fftw.rs, benches/rustfft.rs), rustc/clang versions and an M1 CPU, but its FFTW baseline is handicapped: the fftw crate's default 'source' feature builds FFTW 3.3.8 via fftw-src with './configure --with-pic --enable-static --disable-doc' (no --enable-neon, so scalar codelets), and every timed iteration creates a fresh FFTW_ESTIMATE plan. Treated like a de-optimised baseline (cap at C); even so RustFFT loses at several sizes.
- **Verifier notes:** Numbers match the astral4 README table exactly, but the comparison is against a scalar FFTW 3.3.8 with plan creation timed, and the record understated where RustFFT loses. Scope flag: Rust-only library (no C API); orchestrator may want to file it as a non-C++ entry. Metadata confirmed: MIT OR Apache-2.0, 942 stars, last commit 2026-09-29, not a fork.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/astral4/fft-benchmark>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/benches/fftw.rs>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/benches/rustfft.rs>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/benches/phastft.rs>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/rust-math/fftw/HEAD/fftw-src/build.rs>
  - <https://raw.githubusercontent.com/rust-math/fftw/HEAD/fftw/Cargo.toml>
  - <https://github.com/ejmahler/RustFFT>
  - <https://github.com/ejmahler/RustFFT/commits>
  - <https://github.com/ejmahler/RustFFT/releases>
  - <https://raw.githubusercontent.com/ejmahler/RustFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/ejmahler/RustFFT/HEAD/Cargo.toml>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ejmahler/RustFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/ejmahler/RustFFT/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ejmahler/RustFFT/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/ejmahler/RustFFT/HEAD/src/plan.rs>
  - <https://raw.githubusercontent.com/ejmahler/RustFFT/HEAD/CHANGELOG.md>
  - <https://github.com/ejmahler/RustFFT/issues?q=is%3Aissue>
  - <https://github.com/ejmahler/RustFFT/issues/148>
  - <https://github.com/ejmahler/RustFFT/issues/163>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/benches/fftw.rs>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/benches/rustfft.rs>
  - <https://raw.githubusercontent.com/rust-math/fftw/HEAD/fftw-src/build.rs>
  - <https://raw.githubusercontent.com/rust-math/fftw/HEAD/fftw/Cargo.toml>
  - https://users.rust-lang.org/t/rustfft-5-0-0-experimental-1-now-faster-than-fftw/53049 (egress-blocked; search snippet only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ejmahler/rustfft`) · [data/wave8/enrich/raw/github_com_ejmahler_rustfft.json](../../../data/wave8/enrich/raw/github_com_ejmahler_rustfft.json) (enrichment confidence 0.8)

</details>
