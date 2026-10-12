# PhastFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Safe-Rust, in-place, power-of-two FFT with low memory and optional threads; beats RustFFT at mid sizes and a scalar FFTW build.

| | |
|---|---|
| **Beats** | FFTW 3.3.8 (via the Rust fftw crate); also RustFFT |
| **Claimed result** | astral4/fft-benchmark (M1 MacBook Pro, single thread, plan created inside each timed iteration for every library; forward times): f32 N=1024 4.749 us (PhastFT) vs 7.291 us (FFTW, FFTW_ESTIMATE); f32 N=1,048,576 10.21 ms vs 14.20 ms; f32 N=8,388,608 109.0 ms vs 193.3 ms (RustFFT 103.9 ms). Author's conclusion: 'phastft was the fastest in most tests, but rustfft was the fastest on the smallest and largest sequence lengths tested'; 'fftw was consistently slower than both rustfft and phastft'. PhastFT allocated about 5x less memory than RustFFT (derived from page data: 8.388 MB vs 41.94 MB at N=2^20 f32). PhastFT's own single-threaded criterion overlays (Apple M2, FFTW 3.3.8 via the fftw crate, plan reused) show FFTW_MEASURE at 1.31x to 2.04x PhastFT's time for f32 N=2^6 to 2^14 and 2.1x to 3.6x for f32 N=2^15 to 2^24, and 1.2x to 2.0x for f64 N=2^15 to 2^24 (derived from the bar labels in the SVG plots, which are relative to RustFFT). |
| **Workload** | Single-threaded complex-to-complex forward and inverse FFT, f32 and f64, power-of-two lengths 8 to 8,388,608, divan benchmark on an M1 MacBook Pro in a third-party benchmark repo (astral4/fft-benchmark). |
| **Metric** | throughput |
| **Hardware** | M1 MacBook Pro (Apple M1; exact model not stated) for astral4; PhastFT's own plots use a MacBook Air with Apple M2, 4P+4E cores, 24 GB, macOS 26.4.1 |
| **Compiler and flags** | astral4 run: rustc 1.80.0-nightly (d2d24e395 2024-05-03), cargo bench profile with lto = true and default opt-level 3, no target-cpu (Cargo.toml); phastft v0.2.1, rustfft v6.2.0, fftw crate v0.8.0 over FFTW 3.3.8 compiled with Apple clang 15.0.0 (clang-1500.0.40.1); FFTW configure flags (e.g. NEON) not stated |
| **Adoption** | 309 stars |
| **Last commit** | 2026-07-31 |
| **Links** | [repository](https://github.com/smu160/PhastFT) · [benchmark](https://github.com/astral4/fft-benchmark) |

## Verdict

Third-party astral4/fft-benchmark (M1 MacBook Pro, single thread, phastft 0.2.1, plan built inside every timed call for all libraries) shows PhastFT ahead of FFTW 3.3.8 at every size (e.g. f32 2^10 4.75 us vs 7.29 us, 2^23 109 ms vs 193 ms), but that FFTW was planned with FFTW_ESTIMATE on each call and built by the fftw crate's default 'source' feature, whose configure line has no --enable-neon. PhastFT's own steady-state criterion plots (Apple M2, plans reused) put FFTW_MEASURE at about 2.3x to 3.4x RustFFT's time for f32 2^15 to 2^24 with the same scalar FFTW build (PhastFT's dev-dependency is fftw 0.8.0 with default features), so no comparison against a SIMD-enabled FFTW exists.

## Use it when

- Rust code doing power-of-two FFTs of 2^6 to 2^14 points single-threaded, where its own M2 plots show it 0.70x to 0.93x of RustFFT's time at most sizes.
- Very large power-of-two FFTs (megabytes to gigabytes) on a multi-core machine, using the parallel feature that the README headline plots measure.
- Memory-limited jobs: in astral4's run it allocated about 5x less than RustFFT (8.39 MB vs 41.94 MB at 2^20 f32), and the README claims up to 2x lower memory.
- Projects that forbid unsafe code (the crate uses #![forbid(unsafe_code)]) and want runtime SIMD selection without -C target-cpu=native.

## Skip it when

- Non-power-of-two lengths: the planner asserts is_power_of_two and panics; use RustFFT, PocketFFT or FFTW.
- Single-threaded large FFTs: in its own M2 plots PhastFT takes 1.01x to 1.19x RustFFT's time from about 2^17 points up, and astral4 shows RustFFT faster at f32 N&gt;=2^22 and f64 N&gt;=2^21 (issue #120 raises the same point).
- Tiny transforms (N=16, 32), where RustFFT's hand-written butterflies win.
- C or C++ code bases: no C ABI, so you would need your own FFI layer.
- When you need FFTW's multi-dimensional or arbitrary-stride interfaces; the README documents only 1-D transforms.

## How it is fast

Radix-2 decimation-in-time Cooley-Tukey written recursively (cache-oblivious, switching to a loop once a block fits in L1), with a separate bit-reversal pass using the cache-optimal CO-BRAVO algorithm with SIMD. Working in place on split real/imaginary arrays cuts memory traffic and peak memory compared with out-of-place or self-sorting FFTs. SIMD kernels for SSE4.2, AVX2, NEON and WASM come from fearless_simd with runtime dispatch, and the default 'parallel' feature uses rayon for the recursive FFT and two threads for bit reversal on large inputs.

## Compared with alternatives

Choose it over RustFFT when lengths are powers of two and memory or multi-core throughput on huge transforms matters; stay with RustFFT for arbitrary lengths and tiny sizes. For C++ projects, PocketFFT (C++ branch) or PFFFT are the native-language siblings with similar 'no FFTW dependency' appeal.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | num-traits, fearless_simd; rayon (default 'parallel' feature); num-complex and bytemuck with the optional 'complex-nums' feature |
| **Minimum toolchain** | Rust 1.88 (rust-version in Cargo.toml, crate v0.4.1); the 2024 v0.2.1 used in astral4's benchmark needed nightly for portable SIMD |
| **Platforms** | any Rust target; SIMD on x86-64 (SSE4.2, AVX2), aarch64 (NEON) and wasm, picked at runtime |
| **Thread safety** | not documented; calls take &mut slices and a shared &Planner, and the parallel feature spawns rayon work inside each call |
| **Drop-in for the baseline** | no |

## Gotchas

- The 'parallel' feature is on by default, so a plain dependency is multi-threaded; set default-features = false for single-threaded or deterministic-latency use.
- The inverse FFT scales by 1/N (IFFT(FFT(x)) == x), unlike FFTW and RustFFT, which leave output unnormalized.
- The interleaved Complex API allocates temporary buffers and is slower than the split real/imag API; the convenience fft_\* functions build a new planner on every call.
- Issue #73 (open) reports intermittent slowdowns at the largest sizes on x86, suspected cache-associativity or TLB effects of power-of-two strides.

## Known shortcomings

- astral4 benchmark builds a new FFTW_ESTIMATE plan inside every timed iteration, so FFTW's 'slower' result comes from planning cost; PhastFT's own benchmarks are first-party with numbers only as plot labels; repo moved to smu160/PhastFT; Rust.
- In its own M2 plots PhastFT single-threaded is 1.01-1.19x slower than RustFFT from about 2^17 points up (#120); its FFTW baseline is the fftw crate's default build without NEON/AVX, so there is no comparison against a SIMD FFTW; the default 'parallel' feature makes it multi-threaded.

## Caveats and trade-offs

The independent astral4 benchmark times plan creation inside every iteration for all three libraries and plans FFTW with FFTW_ESTIMATE, which explains FFTW's roughly 1.4 us floor at N=8; it is a one-shot (plan plus execute) comparison, not a measure of FFTW's steady-state execution. It is a small personal repo from 2024 benchmarking phastft v0.2.1, while the crate is now v0.4.1 with the parallel feature on by default. RustFFT beats PhastFT at N=16 and 32 and at N&gt;=2^22 for f32, and at N=16, 32, 65,536 and N&gt;=2^21 for f64. In PhastFT's own steady-state plots FFTW (3.3.8 built by the Rust fftw crate) is also 1.3x to 3.9x slower than RustFFT, which suggests that FFTW build lacks NEON codelets on Apple Silicon (inference, not stated anywhere), so the FFTW comparison on Apple Silicon should be treated with caution. PhastFT's README plots are multi-threaded vs single-threaded RustFFT and FFTW3; numbers appear only as plot bar labels. Rust library, power-of-two lengths only. The QuState/PhastFT URL redirects to smu160/PhastFT.

Power-of-two lengths only. Runtime SIMD selection (no -C target-cpu=native needed). In-place algorithm with much lower memory than RustFFT. Optional multi-threading through the 'parallel' feature. The 2024 benchmark used v0.2.1, which needed nightly Rust for portable SIMD; the current Cargo.toml says rust-version 1.88.

## Maintenance

Active (last commit 2026-07-31, v0.4.1), MIT OR Apache-2.0 and pure safe Rust, so it is easy to depend on from Rust but not callable from C++ without a wrapper.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** astral4/fft-benchmark is independent but a small personal repo (5 stars), not a well-known suite, and its benches/fftw.rs builds a new FFTW_ESTIMATE plan inside every timed iteration (PhastFT and RustFFT also plan per iteration), so it measures one-shot plan-plus-execute rather than FFTW's execution speed. PhastFT's own steady-state benches (benches/fftw_lib/mod.rs, FFTW_MEASURE plan reused) are first-party, plots only, on an Apple M2 with no compiler version stated, so C.
- **Verifier notes:** Numbers match the astral4 README, but its bench code creates an FFTW_ESTIMATE plan inside every timed iteration, so 'fftw was consistently slower' is a planning-overhead artifact and B (well-known suite) does not apply. Downgraded to C. The repo has moved to smu160/PhastFT (309 stars, last commit 2026-07-31); repo_url may need updating.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/QuState/PhastFT>
  - <https://github.com/smu160/PhastFT/commits/main>
  - <https://raw.githubusercontent.com/QuState/PhastFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/QuState/PhastFT/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/QuState/PhastFT/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/QuState/PhastFT/HEAD/benches/fftw_lib/mod.rs>
  - <https://raw.githubusercontent.com/smu160/PhastFT/main/assets/criterion_overlay_c2c_forward_f32_6_14.svg>
  - <https://raw.githubusercontent.com/smu160/PhastFT/main/assets/criterion_overlay_c2c_forward_f32_15_24.svg>
  - <https://raw.githubusercontent.com/smu160/PhastFT/main/assets/criterion_overlay_c2c_forward_f64_15_24.svg>
  - <https://github.com/astral4/fft-benchmark>
  - <https://github.com/astral4/fft-benchmark/tree/main/benches>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/benches/fftw.rs>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/benches/phastft.rs>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/benches/rustfft.rs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/smu160/PhastFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/smu160/PhastFT/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/smu160/PhastFT/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/smu160/PhastFT/HEAD/src/planner.rs>
  - <https://raw.githubusercontent.com/smu160/PhastFT/HEAD/src/options.rs>
  - <https://raw.githubusercontent.com/smu160/PhastFT/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/smu160/PhastFT/HEAD/benches/fftw_lib/mod.rs>
  - <https://raw.githubusercontent.com/smu160/PhastFT/main/assets/criterion_overlay_c2c_forward_f32_6_14.svg>
  - <https://raw.githubusercontent.com/smu160/PhastFT/main/assets/criterion_overlay_c2c_forward_f32_15_24.svg>
  - <https://raw.githubusercontent.com/smu160/PhastFT/main/assets/criterion_overlay_c2c_forward_f64_15_24.svg>
  - <https://github.com/smu160/PhastFT/issues?q=is%3Aissue>
  - <https://github.com/smu160/PhastFT/issues/73>
  - <https://github.com/smu160/PhastFT/issues/120>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/benches/fftw.rs>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/benches/rustfft.rs>
  - <https://raw.githubusercontent.com/astral4/fft-benchmark/HEAD/benches/phastft.rs>
  - <https://raw.githubusercontent.com/rust-math/fftw/HEAD/fftw-src/build.rs>
  - <https://raw.githubusercontent.com/rust-math/fftw/HEAD/fftw/Cargo.toml>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/qustate/phastft`) · [data/wave8/enrich/raw/github_com_qustate_phastft.json](../../../data/wave8/enrich/raw/github_com_qustate_phastft.json) (enrichment confidence 0.8)

</details>
