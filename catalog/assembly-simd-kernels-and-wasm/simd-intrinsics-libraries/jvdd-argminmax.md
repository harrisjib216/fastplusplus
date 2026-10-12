# argminmax

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust crate: argmin and argmax indices in one SIMD pass, 2.4-21x faster than its own scalar loop.

| | |
|---|---|
| **Beats** | scalar Rust argmin+argmax loop (the repo's own scalar_\* benchmark rows) |
| **Claimed result** | README: 'Benchmarks on my laptop (AMD Ryzen 7 4800U, 1.8 GHz, 16GB RAM) using criterion show that the function is 3-20x faster than the scalar implementation (depending of data type)'. benches/results rows (v0.4.0, 2023), Ryzen 7 4800U: i16 scalar 74.039 us vs impl 4.4617 us (about 16.6x, derived from page data); i8 scalar 76.858 us vs impl 7.2931 us (about 10.5x, derived); f32 scalar 65.058 us vs impl 11.186 us (about 5.8x, derived); f16 scalar 97.594 us vs impl 4.6024 us (about 21.2x, derived). Low end on the same CPU: f64 66.831 us vs 22.857 us (about 2.9x, derived) and u64 74.233 us vs 31.163 us (about 2.4x, derived), so the README's 3x lower bound is slightly overstated. i7-1185G7: f32 scalar 55.549 us vs impl 6.9749 us (about 8.0x, derived). |
| **Workload** | Single-pass argmin and argmax over a 102,400-element uniformly random array (ARRAY_LENGTH_LONG in dev_utils/src/config.rs, the same at v0.4.0 and HEAD) for i8..u64, f16, f32 and f64. Runtime-dispatched SSE, AVX, AVX2, AVX-512 or NEON kernels (the impl_\* rows) are timed against the library's own scalar loop (the scalar_\* rows). |
| **Metric** | throughput |
| **Hardware** | Results file lists Intel i7-1185G7 laptop, AMD Ryzen 7 4800U laptop, AMD Ryzen 5 2600X desktop, Xeon E5-2650 v2 server, Raspberry Pi 3B (ARMv7) and Pi 4B (AArch64); README headline uses the Ryzen 7 4800U |
| **Compiler and flags** | The rows in benches/results were measured at v0.4.0 (file last changed 2023-02-03, commit 74436c9) with an unstated rustc version; no rust-toolchain.toml existed then, and HEAD now pins nightly-2026-10-06. Built with cargo bench using criterion 0.3 and codspeed-criterion-compat, the default bench profile and no RUSTFLAGS or target-cpu (kernels picked by runtime feature detection). The code is benches/bench_&lt;type&gt;.rs at that commit (row names scalar_random_long_\*); the current benches emit scalar_&lt;type&gt;_argminmax rows instead, so HEAD's bench code no longer reproduces these row names. |
| **Adoption** | 64 stars; 15,387,918 crates.io downloads (2,967,157 recent); reverse dependencies include polars-ops and polars-utils; implements traits for ndarray and Arrow arrays |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/jvdd/argminmax) · [benchmark](https://github.com/jvdd/argminmax/blob/main/benches/results) |

## Verdict

First-party criterion runs at v0.4.0 (2023, unstated nightly rustc, no target-cpu flags) on 102,400 uniformly random elements, comparing the dispatched SIMD path with the crate's own scalar loop: on a Ryzen 7 4800U, 2.4x (u64) and 2.9x (f64) up to 10.5x (i8), 16.6x (i16) and 21.2x (f16); 64-bit types were no faster than scalar on a Xeon E5-2650 v2 (no AVX2) and on the Raspberry Pi 3B and 4B. These numbers predate 0.7.0's kernel changes and its float-path correctness fixes.

## Use it when

- Rust code that needs both the argmin and the argmax (or either one) of large primitive arrays, such as time-series downsampling, plotting or columnar analytics; the published rows use 102,400-element arrays.
- 8- and 16-bit integer or f16 data, where the integer-mapped SIMD kernels gave about 10-21x over the scalar loop on a Ryzen 7 4800U.
- Shipping one binary to heterogeneous x86-64 machines: runtime dispatch picks SSE4.1, AVX2 or AVX-512 without `-C target-cpu`.
- Arrow or Polars columns with validity bitmaps: the masked variants skip nulls and return `None` when nothing is valid (0.7.0).

## Skip it when

- 64-bit integers on x86 CPUs without AVX2 (Xeon E5-2650 v2 in the results file): dispatch falls back to scalar because SSE was slower than scalar (i64 140.98 vs 98.20 us), so there is no gain; the f64 low end on a Ryzen 7 4800U is 2.9x and u64 2.4x.
- Short arrays: PR #88's Apple M5 measurements show the newer code ranging 0.88-1.43x of the old at 32 elements, and no published number covers small inputs against the scalar loop.
- When an empty input must not panic: the functions assert a non-empty slice (and the arrow impls panic when every value is null); issue #27 asking for `Option` returns is still open.
- 32-bit ARM on stable Rust: NEON there needs nightly plus the `nightly_simd` feature, otherwise the scalar path runs; i128 and u128 are always scalar.
- Pinned to 0.6.x (Polars main pins 0.6.3): that line lacks the October 2026 fixes for NaN-returning -0.0/0.0 ties (#98, #100), NaN-ignoring results when only infinities remain (#97, #102), and an illegal-instruction dispatch of 16-bit types to AVX-512 on CPUs with AVX512F but no AVX512BW (#84, reachable with `nightly_simd`).

## How it is fast

The core keeps a vector of running minima, a vector of running maxima and matching index vectors, compares each loaded vector against them and blends with the comparison mask, so the inner loop has no data-dependent branches; a horizontal reduction at the end picks the value and the lowest index on ties. Unsigned ints and f16 (and floats in the NaN-returning variant) are bit-transformed into ordered signed integers so integer compare instructions can be used, which is why 8- and 16-bit types get the largest speedups. Index lanes have the data's width, so 8- and 16-bit inputs are processed in overflow-safe chunks. Since 0.7.0 the loop reduces each group of 4 vectors to one candidate before touching the running min/max, shortening the loop-carried dependency chain (PR #88); the instruction set (SSE4.1, AVX, AVX2, AVX-512, NEON) is chosen by runtime CPU feature detection on every call.

## Compared with alternatives

Pick it in Rust whenever you need indices rather than values: numpy-minmax returns only min and max values for NumPy, and kelindar/simd, vek and FastArrayOps cover min/sum/find in Go and C++. It is also the only one here with NaN-policy variants, Arrow null masks and runtime dispatch from SSE4.1 to AVX-512 and NEON.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | num-traits; optional half 2.7 (f16), ndarray 0.17, arrow (any version, `>0`) |
| **Minimum toolchain** | Rust 1.89 for 0.7.0 (AVX-512 kernels on stable since that release); 0.6.x builds on older stable but uses AVX-512 only on nightly with `nightly_simd`; v0.4.0, which produced the published results, required nightly unconditionally |
| **Platforms** | x86 and x86-64 (SSE4.1, AVX, AVX2, AVX-512F/BW, runtime-detected), aarch64 NEON, 32-bit ARM NEON on nightly; scalar fallback elsewhere |
| **Thread safety** | not documented; the functions take `&[T]` and keep no state beyond std's CPU-feature detection cache |
| **Drop-in for the baseline** | partial — replaces a hand-written min/max index loop with a trait method returning (argmin, argmax); returns the first index on ties, panics on empty input, and float NaN handling depends on which trait you call |

## Gotchas

- The benchmark baseline is the crate's own branchy scalar loop (`if v < low {..} else if v > high {..}` over `get_unchecked`), run on uniformly random data where min/max updates are rare and branches predict well; no third-party baseline (std iterators, NumPy) is measured, and the worst-case-order benches exist in the v0.4.0 bench files but are commented out of `criterion_group!`.
- benches/results is from v0.4.0 (2023), which required nightly (`#![feature(stdsimd)]` at the top of lib.rs) and always enabled AVX-512. In 0.6.x on stable, AVX-512 is gated behind `nightly_simd`, so the i7-1185G7 'impl' rows (for example f32 8.0x, derived from page data) do not apply there; the same CPU's AVX/AVX2 rows are f32 2.5x, i64 1.3x and u64 2.1x over scalar (derived from page data). Current 0.7.0 kernels are up to 1.8x faster than before PR #88, so the file is stale in both directions. Data alignment was not controlled (open issue #95).
- For 8-bit types, x86 dispatch deliberately prefers SSE4.1: in the results AVX-512 was slower than SSE for i8 on the i7-1185G7 (10.49 vs 6.78 us), because 8-bit index lanes force short overflow-safe chunks.
- `ArgMinMax` on an all-NaN float array returns index 0, and `NaNArgMinMax` does not guarantee the first NaN when several NaN bit patterns are present (README limitations).

## Known shortcomings

- benches/results rows date from v0.4.0 (2023-02-03) with the rustc version unstated; float paths were fixed since (#40, #100, #102); the baseline is the crate's own scalar code; README 3-20x is overstated at the low end (u64 2.4x on a Ryzen 4800U) and SSE i64/u64 is slower than scalar on a Xeon E5-2650 v2.
- Results come from v0.4.0, which required nightly and always enabled AVX-512; in 0.6.x on stable AVX-512 sits behind the nightly_simd feature, so the i7-1185G7 8.0x f32 row does not apply there (its AVX/AVX2 rows give 2.5x f32, 1.3x i64, 2.1x u64). The baseline is the crate's own branchy scalar loop on random data; worst-case benches are commented out. 0.6.x users (Polars main pins 0.6.3) lack the 0.7.0 fixes of 2026-10-09: -0.0/0.0 tie mismatches (#98, #100), infinities-only NaN-ignore results (#97, #102), AVX512F-without-BW illegal instruction on 16-bit types (#84).

## Caveats and trade-offs

The baseline is the library's own scalar loop, not a third-party implementation (NumPy, std iterator min_by_key). The results file is stale: last changed 2023-02-03 at v0.4.0, while the crate is now 0.7.0 with later perf work (#88, #104) and correctness fixes on the float paths (#40 scalar ignore-NaN double update in March 2023, #100 f16 -0.0/0.0 equality and #102 NaN-ignore with only infinities left in October 2026). The toolchain for the rows is unstated. Some x86 SIMD kernels are slower than scalar (Xeon E5-2650 v2: SSE i64 140.98 us vs scalar 98.203 us; SSE u64 157.79 us vs 124.12 us), so dispatch falls back to scalar there. AVX-512 is slower than SSE for i8 and u8 on the i7-1185G7 (10.491 us vs 6.7829 us for i8). On the Raspberry Pi 3B and 4B the f64, i64 and u64 rows had no SIMD path at v0.4 (impl equals scalar). Several rows are annotated slower than v0.3, and the author's own remark says v0.4 is a lot slower on ARM than v0.3.1. [retier] First-party criterion results in benches/results from v0.4.0 (2023), which required nightly and always enabled AVX-512; in 0.6.x on stable AVX-512 sits behind the nightly_simd feature, so the i7-1185G7 8.0x f32 row does not apply to stable builds (that CPU's AVX/AVX2 rows give 2.5x f32, 1.3x i64, 2.1x u64). The baseline is the crate's own branchy scalar loop on random data; the worst-case benches are commented out; no comparison with a C++ -O3 baseline. 0.6.x users (Polars main pins 0.6.3) lack the 0.7.0 fixes of 2026-10-09: -0.0/0.0 tie mismatches (#98, #100), infinities-only NaN-ignore results (#97, #102) and an AVX512F-without-BW illegal instruction on 16-bit types (#84).

x86-64 (SSE, AVX, AVX2, AVX-512) and AArch64 NEON; 32-bit ARM NEON needs nightly; i128 and u128 use the scalar path; NaN handling is ignore-NaN or return-first-NaN variants (ignore-NaN variant is advertised as 5-30% faster); inner loop is branch-free so runtime does not depend on data order.

## Maintenance

Very actively maintained (0.7.0 released 2026-10-09 after a burst of correctness, NEON i64/u64 and performance PRs), MIT, about 15.4M crates.io downloads, almost all on 0.6.x through Polars; adopt 0.7.0 on Rust 1.89+ and treat the 2023 results file as directional for the current code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** benches/results holds first-party criterion runs on named CPUs against the library's own scalar loop, and the bench code that produced them is public (benches/bench_&lt;type&gt;.rs at v0.4.0, commit 74436c9). But the rustc version is not stated anywhere for those rows: no rust-toolchain.toml existed then, and the nightly-2026-10-06 pin is today's HEAD. The rows date from 2023-02-03 and predate later fixes to the float paths (#40 scalar ignore-NaN double update, #100 f16 -0.0/0.0, #102 NaN-ignore with only infinities left), so C, not A.
- **Verifier notes:** All quoted numbers match benches/results, but those rows are first-party, about 3.7 years old (v0.4.0) and from an unstated rustc version, so not A; down to C. Main shortcomings: stale results versus the current 0.7.0 code (float paths fixed since), self-baseline scalar loop, the README 3-20x range understates the 2.4x u64 low end, and SSE i64/u64 is slower than scalar on the Xeon E5-2650 v2. Notable as a Polars dependency (15.4M crates.io downloads).
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `workload`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-56 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/jvdd/argminmax>
  - <https://github.com/jvdd/argminmax/tree/main/benches/results>
  - <https://github.com/jvdd/argminmax/commits/main/benches/results>
  - <https://github.com/jvdd/argminmax/commits/main>
  - <https://github.com/jvdd/argminmax/commits/main?after=4ab1c3e&page=2>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/README.md>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/benches/results>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/benches/bench_i16.rs>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/src/scalar/generic.rs>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/dev_utils/src/config.rs>
  - <https://raw.githubusercontent.com/jvdd/argminmax/74436c9/Cargo.toml>
  - <https://raw.githubusercontent.com/jvdd/argminmax/74436c9/dev_utils/src/config.rs>
  - <https://crates.io/api/v1/crates/argminmax>
  - <https://crates.io/api/v1/crates/argminmax/reverse_dependencies?per_page=20>
- **Sources the enricher read:**
  - <https://github.com/jvdd/argminmax/issues?q=is%3Aissue>
  - <https://github.com/jvdd/argminmax/pulls?q=is%3Apr>
  - <https://github.com/jvdd/argminmax/pull/83>
  - <https://github.com/jvdd/argminmax/pull/84>
  - <https://github.com/jvdd/argminmax/pull/88>
  - <https://github.com/jvdd/argminmax/pull/98>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/README.md>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/benches/results>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/benches/bench_i16.rs>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/src/scalar/generic.rs>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/src/simd/generic.rs>
  - <https://raw.githubusercontent.com/jvdd/argminmax/HEAD/dev_utils/src/config.rs>
  - <https://raw.githubusercontent.com/jvdd/argminmax/74436c9/benches/bench_f32.rs>
  - <https://raw.githubusercontent.com/jvdd/argminmax/74436c9/benches/bench_i16.rs>
  - <https://raw.githubusercontent.com/jvdd/argminmax/74436c9/src/scalar/generic.rs>
  - <https://raw.githubusercontent.com/jvdd/argminmax/74436c9/src/lib.rs>
  - <https://raw.githubusercontent.com/jvdd/argminmax/74436c9/Cargo.toml>
  - <https://crates.io/api/v1/crates/argminmax>
  - <https://raw.githubusercontent.com/pola-rs/polars/main/Cargo.toml>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jvdd/argminmax`) · [data/wave13/enrich/raw/github_com_jvdd_argminmax.json](../../../data/wave13/enrich/raw/github_com_jvdd_argminmax.json) (enrichment confidence 0.8)

</details>
