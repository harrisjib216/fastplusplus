# Sep

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C#` · `MIT` · 🟢 active

> Zero-allocation, SIMD-vectorized .NET CSV/TSV parser built to beat CsvHelper on throughput.

| | |
|---|---|
| **Beats** | CsvHelper (the most widely used .NET CSV parsing library) |
| **Claimed result** | AMD EPYC 7763 tables (Sep 0.13, CsvHelper 33.1): NCsvPerf PackageAssets 50K rows, Sep faster than CsvHelper by 17.8x (Row), 20.9x (Cols), 3.1x (Asset); PackageAssets with Quotes 6.8x (Row), 8.4x (Cols), 2.8x (Asset); PackageAssets with Spaces and Quotes: README says 'about 10x' (Sep_ 12.92 ms vs CsvHelper_TrimUnescape 142.26 ms, ratio 11.01, but like-for-like Sep_TrimUnescape 19.40 ms vs 142.26 ms is \~7.3x, derived from page data); Floats 4.6x single-threaded. README headline: 'up to 35x faster than CsvHelper' with ParallelEnumerate (Ryzen 9 9950X Floats table: Sep_MT 2.063 ms vs CsvHelper 68.322 ms, \~33x, derived from page data). |
| **Workload** | Parsing CSV rows into columns/floats (PackageAssets and Floats benchmarks, 50000 rows, with/without trimming and unescaping) using BenchmarkDotNet on .NET 9.0 |
| **Metric** | throughput |
| **Hardware** | Multiple platforms tested: AMD EPYC 7763 (Ubuntu 22.04, virtual), AMD Ryzen 7 PRO 7840U, AMD Ryzen 9 5950X, AMD Ryzen 9 9950X, AMD Ryzen 9 9950X3D2, Apple M1 (virtual), plus a 'Cobalt.100' ARM platform |
| **Compiler and flags** | .NET 9.0.X per README (current comparison-bench.ps1 runs `dotnet run -c Release -f net10.0`), BenchmarkDotNet, GC DATAS disabled (GarbageCollectionAdaptationMode=0 / DOTNET_GCDynamicAdaptationMode=0); settings in src/Sep.ComparisonBenchmarks/Sep.ComparisonBenchmarks.csproj |
| **Adoption** | 1.5k stars |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/nietras/Sep) · [benchmark](https://github.com/nietras/Sep#comparison-benchmarks) |

## Verdict

First-party BenchmarkDotNet comparisons on .NET 9.0.X (current script targets net10.0) with GC DATAS disabled, run across multiple CPUs (AMD EPYC 7763, Ryzen 9950X, etc.), show Sep (0.13-0.17.1) beating CsvHelper 33.1 on the NCsvPerf PackageAssets benchmark (50K rows) by 17.8x/20.9x/3.1x (row/cols/asset) unquoted and 6.8-8.4x with quotes on EPYC 7763; the README's headline 'about 10x'/'up to 35x' figures come from a non-like-for-like Spaces-and-Quotes trim/unescape comparison (\~7.3x like-for-like) and a multi-threaded Floats benchmark on Ryzen 9 9950X (Sep_MT 2.06ms vs CsvHelper 68.3ms, \~33x) respectively.

## Use it when

- Large CSV/TSV files with mostly numeric columns (floats, ints) parsed repeatedly in .NET, where CsvHelper's throughput is the bottleneck
- ML/data-pipeline style workloads reading many rows where zero-allocation parsing after warmup matters
- .NET 8+/9+ services that need AOT/NativeAOT or trimmed deployments (no reflection or dynamic codegen)
- Offline/batch parsing of very large files where the fixed overhead of ParallelEnumerate's multi-threaded batching pays off
- Projects that can accept an opinionated, non-CsvHelper API and control both the writer and reader side

## Skip it when

- You need CsvHelper's mature feature set: attribute/class mapping, broad configuration surface, long compatibility history
- Input has heavy quoting, embedded newlines, or stray spaces and you rely on automatic unescape/trim — Sep disables both by default and requires explicit opt-in
- Comma-separated files without a usable header row: default separator is ';', inferred from the header, so plain ',' input needs explicit configuration
- Small files or one-off scripts, where ParallelEnumerate's batching/LINQ overhead outweighs any gain over single-threaded CsvHelper
- You need native `#` comment-line support — Sep has none; you must filter such rows manually in the read loop

## How it is fast

Uses architecture-specific and cross-platform SIMD vectorized scanning (64/128/256/512-bit paths, e.g. AVX2, AVX-512 on .NET 8+, NEON) to find separators/quotes, and the csFastFloat library for fast float/double parsing. Memory is pooled (ArrayPool&lt;T&gt;, ref structs, Span&lt;T&gt;) so steady-state parsing is zero-allocation after warmup. An opt-in `ParallelEnumerate` API adds multi-threaded batch parsing on top via LINQ AsParallel/AsOrdered for further throughput on large files.

## Compared with alternatives

None of the catalogued CSV siblings (DuckDB, Polars, qsv, zsv, vroom, xan, cisv, go-simdcsv, simd-csv, zsv-ruby) target .NET — Sep is the only .NET-specific entry in this category, so pick it whenever the project is C#/.NET and needs faster-than-CsvHelper parsing of numeric-heavy CSV into typed columns; reach for one of the others only if you're not on .NET.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | csFastFloat (NuGet package reference, used for fast float/double parsing) |
| **Minimum toolchain** | C# 13.0+ (repo currently builds with C# 14.0), .NET 8.0+ (SepReader implements IAsyncEnumerable/native enumerable behavior added for .NET 9+), AllowUnsafeBlocks enabled in the csproj |
| **Platforms** | Any platform/architecture .NET runs on; SIMD fast paths for x86-64 AVX2/AVX-512 (.NET 8+) and ARM NEON, with a portable fallback elsewhere. Comparison benchmarks were run on AMD EPYC 7763, Ryzen 7840U/5950X/9950X/9950X3D2, Apple M1 (virtual), and a Cobalt ARM VM |
| **Thread safety** | not documented as safe for concurrent access to a single reader/writer instance; multi-threaded parsing is instead opt-in via `ParallelEnumerate`, which batches rows and parallelizes with LINQ AsParallel().AsOrdered() using pooled arrays — callers must ensure their per-row delegate touches no shared mutable state |

## Gotchas

- Default column separator is ';', not ',' — inferred from the header row unless set explicitly
- No automatic unescaping or trimming: must opt in via SepReaderOptions (Unescape/Trim); trimming/unescaping can happen in-place, leaving the row's raw Span in a documented 'garbage' state for those columns after processing
- ParallelEnumerate carries real fixed overhead (batching + LINQ AsParallel/AsOrdered) and can be slower than plain single-threaded Enumerate/foreach on small inputs — the README explicitly warns to measure before using it
- An 'AccessViolation on .NET 10' issue (#423, opened Nov 2025) was reported and closed — worth checking against your exact .NET 10 build if adopting early

## Caveats and trade-offs

First-party benchmark by the library's maintainer. The 12.92 ms vs 142.26 ms (11x) figure comes from the 'PackageAssets with Spaces and Quotes' benchmark and compares Sep with no trimming against CsvHelper with trim+unescape; the plain 'with Quotes' benchmark shows 2.8-8.4x on EPYC 7763. Tables mix Sep versions (0.9-0.17.1) and platforms, and the README says .NET 9 while the current runner script targets net10.0. The README's own disclaimer notes CsvHelper has a different feature set and backwards-compatibility constraints, and CsvHelper can only expose columns as strings.

Opinionated API tailored to ML use cases, no automatic quote unescaping/trimming by default (must opt in), default separator is ';' not ',', requires modern C#/.NET (Span&lt;T&gt;, generic math)

## Maintenance

Actively maintained (last commit 2026-09-19, most recent push 2026-09-21) with \~1.5k GitHub stars; MIT-licensed NuGet package, small and simple enough to vendor or pin if needed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** README Comparison Benchmarks tables compare Sep against CsvHelper (and Sylvan) with BenchmarkDotNet on named CPUs (AMD EPYC 7763, Ryzen 9 9950X, etc.) with runtime (.NET 9.0.X) and GC settings stated; benchmark code is public in src/Sep.ComparisonBenchmarks/ (PackageAssetsBench.cs, FloatsReaderBench.cs) with build settings in its csproj and comparison-bench.ps1 (dotnet run -c Release).
- **Verifier notes:** Record's example (12.92 ms vs 142.26 ms) was mislabeled as 'PackageAssets-with-quotes'; it is the Spaces-and-Quotes trim/unescape table, and not like-for-like. claimed_speedup was rewritten from the page tables. Metadata checked: MIT, 1474 stars, last commit 2026-09-19.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/nietras/Sep>
  - <https://github.com/nietras/Sep#comparison-benchmarks>
  - <https://github.com/nietras/Sep/blob/main/src/Sep.ComparisonBenchmarks/Sep.ComparisonBenchmarks.csproj>
  - <https://github.com/nietras/Sep/blob/main/src/Sep.ComparisonBenchmarks/Program.cs>
  - <https://github.com/nietras/Sep/blob/main/comparison-bench.ps1>
- **Sources the enricher read:**
  - <https://github.com/nietras/Sep>
  - <https://github.com/nietras/Sep#comparison-benchmarks>
  - <https://github.com/nietras/Sep/blob/main/src/Sep/Sep.csproj>
  - <https://github.com/nietras/Sep/issues/423>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/nietras/sep`) · [data/wave3/enrich/raw/github_com_nietras_sep.json](../../../data/wave3/enrich/raw/github_com_nietras_sep.json) (enrichment confidence 0.85)

</details>
