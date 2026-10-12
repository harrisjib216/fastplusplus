# voracious_radix_sort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust MSD/LSD radix-sort crate for primitive types and custom structs, several times faster than Rust's own sort on large arrays.

| | |
|---|---|
| **Beats** | std::sort |
| **Claimed result** | i64 uniform, 1,000 elements: Rust std stable sort \~36us (36.80 ns/item) vs Voracious trait sort \~23us (23.57 ns/item), \~1.56x (derived from page data). At this size Voracious ties Rust sort_unstable (23.64 ns/item) because it falls back to pdqsort. The radix advantage shows at large sizes: at 1,000,000 elements single-thread Voracious takes 9311us vs Rust sort_unstable 37945us (\~4.1x) and Rust stable sort 66765us (\~7.2x); at 10,000,000 elements 117667us vs 535417us (\~4.6x) and 757896us (\~6.4x) (derived from page data). Page columns are mean time in us, standard deviation in ns and time per item in ns. |
| **Workload** | In-memory sort of i64 (and other primitive-type) arrays at sizes from 100 to 1000+ elements across \~25 synthetic distributions (uniform, +-1e9 range, ascending/descending +variants, Zipf, normal, sqrt, pipe organ, etc.), 5 iterations, single- and multi-threaded, run on the maintainer's own machine and checked into the repo's results/ directory |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 3950x 16c/32t (per repos/lakwet/voracious_sort/results/benchmark_1_2_0/computer_spec) |
| **Compiler and flags** | README 'Version' section lists rustc 1.46.0 stable as last tested. The results file is output from a cargo test run; the repo's .env exports RUSTFLAGS="-C target-cpu=native" and the Makefile test target uses cargo test --release, but the exact invocation for this run is not stated. |
| **Adoption** | 75 stars |
| **Last commit** | 2025-12-08 |
| **Links** | [repository](https://github.com/lakwet/voracious_sort) · [benchmark](https://github.com/lakwet/voracious_sort/blob/master/results/benchmark_1_2_0/benchmark_results_trait_i64) |

## Verdict

A first-party benchmark checked into results/benchmark_1_2_0/ on an AMD Ryzen 3950x compares Voracious's trait sort against Rust's own sort_unstable (pdqsort-era) and stable sort on i64 arrays, not C++ std::sort. At 1,000,000 elements Voracious took 9.31ms vs sort_unstable's 37.9ms (\~4.1x) and stable sort's 66.8ms (\~7.2x); at 10,000,000 elements the gap was \~4.6x and \~6.4x respectively. At 1,000 elements Voracious is roughly tied with sort_unstable because it has already fallen back to pdqsort at that size. Compiler flags for the specific run are not stated.

## Use it when

- Large in-memory arrays (roughly 1M+ elements) of primitive integer, float, bool or char types where extra memory for an out-of-place sort is acceptable
- Types already covered in PROFILING.md's tuned table (bool, char, f32/f64, u8/u32/u64, i32/i64, usize/isize 8/32/64) on x86-64 hardware similar to a Ryzen 3950x
- Throughput-bound batch sorting where you can re-run the benchmarks and re-tune constants on your own CPU before committing
- Multithreaded sorts of very large arrays (RELEASES.md 1.2.0 fixed Peeka sort scaling past 1B elements) via the voracious_multithread feature

## Skip it when

- Small or medium arrays below the per-type diversion threshold (e.g. \~300-800 elements for f64) — you're just paying trait dispatch over calling Rust's own sort directly
- Sorting String, tuples, or arrays — unsupported (Rust's orphan rule blocks tuple impls; String has no implementation yet)
- Types outside the profiled table (u16, u128, i8/i16/i128, and most custom-struct field types) — these fall back to an untuned 'default default' profile the README says is 'clearly not optimized'
- Memory-constrained environments — the out-of-place trait variants can use up to 2x the input array's memory
- Needing an actively released, MSRV-stable dependency — crates.io's last documented release is 1.2.0 (March 2023) and the README's own 'last tested' toolchain is rustc 1.46.0 (2020), despite commits into late 2025

## How it is fast

Uses most-significant-digit (MSD) radix partitioning derived from Ska sort, with a Verge-sort pre-processing heuristic to detect near-sorted runs and switch strategy; depending on type and size it may instead use DLSD (a diverting LSD radix sort) or 'Rollercoaster' (MSD then LSD hybrid, the author's own contribution). The multithreaded Peeka sort is an in-place parallel MSD radix sort based on MIT's Regions-sort. Per-type/size constants (radix width, diversion thresholds, thread chunk sizes) are hand-'profiled' ahead of time rather than computed at runtime, cutting overhead once arrays are large enough to amortize the histogram passes.

## Compared with alternatives

It's the only Rust entry among these siblings (the others are C++), so pick it when you're already in a Rust codebase sorting large primitive arrays and don't want an FFI shim to a C++ sort. If you need a C/C++ library instead, poor-circle/radix_sort is the closer analog (also LSD-style radix sort, benchmarked directly against std::sort/std::stable_sort at up to 1B int32).

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none for single-thread use; optional rayon 1.7 pulled in only by the 'voracious_multithread' feature flag |
| **Minimum toolchain** | edition 2018; README's stated 'last tested' toolchain is rustc 1.46.0 stable (2020) — no formal MSRV policy documented |
| **Platforms** | not explicitly documented; all tuning constants in PROFILING.md are profiled on an AMD Ryzen 9 3950x (x86-64) and the README says they are 'valid only for the computer on which I am doing the profiling' |
| **Thread safety** | single-thread trait methods only require the element type to be Copy + PartialOrd; voracious_mt_sort additionally requires Send + Sync and only compiles when the voracious_multithread feature is enabled |
| **Drop-in for the baseline** | partial — explain: different call syntax (.voracious_sort()/.voracious_stable_sort()/.voracious_mt_sort(n) instead of .sort()/.sort_unstable()); primitive slices/Vec work immediately via blanket impls, custom struct types must implement the Radixable trait by hand |

## Gotchas

- Falls back to Rust's stock sort below a per-type size threshold, so 'wins' on small arrays in the benchmark data are really just measuring Rust's own sort_unstable/stable sort
- Only the types checked off in PROFILING.md's table are actually tuned; everything else (u16, u128, i8/i16/i128, most struct field types) uses an unoptimized default profile
- Closed GitHub issue #22 reports voracious_mt_sort appearing to hang for 2+ hours (192 threads) sorting 200 billion u64 values; the issue was closed with no comments or stated fix, so the failure mode is unresolved in the public record
- Tuning constants (radix, diversion thresholds, thread chunk sizes) are hardcoded per the maintainer's own Ryzen 3950x — PROFILING.md explicitly warns gains may not transfer to other CPUs without re-profiling

## Caveats and trade-offs

This compares against Rust's own slice::sort/sort_unstable (the pdqsort-era implementations), not C++ std::sort, so compared_against_cpp_std_directly=false. Rust replaced these with driftsort/ipnsort in 1.81, so the baseline is outdated. Build flags for the run are not stated, which caps it at tier C. Below a few hundred to thousand elements Voracious falls back to Rust's pdqsort, so small-array 'wins' are only against the stable sort; the real radix gains (4-7x vs Rust sorts) appear at 1M+ elements. The trait sort may use up to 2x memory (out of place).

out-of-place variants use up to 2x memory; only sorts primitive types and custom structs (no String/Tuple/Array support); radix sort is only worthwhile on larger arrays, falling back to native Rust sort for small inputs; best performance requires per-CPU tuning constants ('profiling'), and the shipped defaults are calibrated for the author's own Ryzen 3950x machine, so gains may not transfer to other CPUs

## Maintenance

Repository shows commits into late 2025 (maintenance_status: active), but the crate's own RELEASES.md stops at 1.2.0 (March 2023) and the README's 'last tested' toolchain is rustc 1.46.0 from 2020. MIT-licensed and small enough to vendor or fork if you need to refresh the tuning constants or toolchain yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The checked-in results file compares Voracious against Rust sort_unstable, Rust stable sort and Rayon on i64 at 100 to 10M elements, with the CPU stated (Ryzen 3950x in computer_spec). The baseline is Rust's own sort, not C++ std::sort, and the build flags for the run are not stated, so it is first-party tier C.
- **Verifier notes:** The record's '36.525us vs 23.334us' misreads the columns: '36us 525ns' is mean 36us plus a 525ns standard deviation per the README legend. The ratio happened to come out the same, but I corrected claimed_speedup and added the representative large-array numbers. Metadata verified: MIT, 75 stars, last commit 2025-12-08, active.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lakwet/voracious_sort>
  - <https://github.com/lakwet/voracious_sort/blob/master/README.md>
  - <https://github.com/lakwet/voracious_sort/blob/master/results/benchmark_1_2_0/benchmark_results_trait_i64>
  - <https://github.com/lakwet/voracious_sort/blob/master/results/benchmark_1_2_0/computer_spec>
  - <https://github.com/lakwet/voracious_sort/blob/master/PROFILING.md>
  - <https://github.com/lakwet/voracious_sort/blob/master/Cargo.toml>
  - <https://github.com/lakwet/voracious_sort/blob/master/Makefile>
  - <https://github.com/lakwet/voracious_sort/blob/master/.env>
- **Sources the enricher read:**
  - <https://github.com/lakwet/voracious_sort>
  - <https://github.com/lakwet/voracious_sort/blob/master/README.md>
  - <https://github.com/lakwet/voracious_sort/blob/master/Cargo.toml>
  - <https://github.com/lakwet/voracious_sort/blob/master/src/traits/radixsort.rs>
  - <https://github.com/lakwet/voracious_sort/blob/master/src/traits/radixable.rs>
  - <https://github.com/lakwet/voracious_sort/blob/master/PROFILING.md>
  - <https://github.com/lakwet/voracious_sort/blob/master/RELEASES.md>
  - <https://github.com/lakwet/voracious_sort/issues/22>
  - <https://github.com/lakwet/voracious_sort/issues>
  - <https://github.com/lakwet/voracious_sort/blob/master/results/benchmark_1_2_0/benchmark_results_trait_i64>
  - <https://github.com/lakwet/voracious_sort/blob/master/results/benchmark_1_2_0/computer_spec>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/lakwet/voracious_sort`) · [data/wave1/enrich/raw/github_com_lakwet_voracious_sort.json](../../../data/wave1/enrich/raw/github_com_lakwet_voracious_sort.json) (enrichment confidence 0.4)

</details>
