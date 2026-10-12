# Quickenshtein

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C#` · `MIT` · 🔴 abandoned

> Allocation-free .NET Levenshtein distance with an SSE4.1/AVX2 anti-diagonal kernel; about 4.8-5.3x faster than Fastenshtein on long strings.

| | |
|---|---|
| **Beats** | naive baseline Levenshtein implementation in the repo, and Fastenshtein (other fast .NET Levenshtein library) |
| **Claimed result** | docs/OverallComparison.md (BenchmarkDotNet 0.12.1 ShortRun, i7-6700HQ), 8000 characters on .NET Core 5.0: Baseline 356,315,300.0 ns, Quickenshtein 17,253,112.5 ns, Fastenshtein 82,207,344.4 ns; about 20.65x over the same-runtime naive baseline (the table's 20.92x is relative to the .NET 4.7.2 Baseline job) and about 4.76x faster than Fastenshtein (derived from page data); the library's own no-intrinsics path is 5.78x slower (100.04 vs 17.31 ms). The .NET Core 5.0 'Quickenshtein_Threaded' row (16,973,617.7 ns) is not a threaded result: CalculationOptions.DefaultWithThreading enables threading only from 16,000 characters on .NET Core (4,000 on .NET Framework) while the benchmark tops out at 8,000, so that row ran the single-threaded path (same 9 B allocation); only the .NET 4.7.2 threaded row (30,820,936.5 ns, 1,024 B allocated) is genuinely multi-threaded, against single-threaded Fastenshtein. 400 and 10 character rows per the docs; slower than Fastenshtein on 10-character strings (317.7 vs 181.4 ns) and at 20 characters on .NET 6 (issue #86: 935.7 vs 663.8 ns). |
| **Workload** | Levenshtein edit distance of 10, 400 and 8000 character strings in BenchmarkDotNet, with AVX2/SSE4.1 intrinsics, optional threading, on .NET Framework 4.7.2 and .NET Core 5.0. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700HQ 2.60GHz (Skylake), 4 cores, Windows 10 2004 |
| **Compiler and flags** | BenchmarkDotNet v0.12.1, .NET Core SDK 5.0.201, .NET Core 5.0.4 and .NET Framework 4.8 (4.7.2 target), ShortRun job IterationCount=3 LaunchCount=1 WarmupCount=3 |
| **Adoption** | 315 stars |
| **Last commit** | 2023-08-01 |
| **Links** | [repository](https://github.com/Turnerj/Quickenshtein) · [benchmark](https://github.com/Turnerj/Quickenshtein/blob/main/docs/OverallComparison.md) |

## Verdict

On an Intel i7-6700HQ (Skylake, 4 cores) with .NET Core 5.0.4 x64 RyuJIT and a BenchmarkDotNet 0.12.1 ShortRun over one synthetic periodic string pair, single-threaded Quickenshtein took 17.25 ms at 8,000 chars versus Fastenshtein 1.0.0.x at 82.21 ms (4.76x) and the repo's naive LINQ baseline at 356.3 ms (20.65x). At 400 chars it was 5.28x faster than Fastenshtein; at 10 chars it was 1.75x slower. AVX2 accounts for 28.94 ms down to 17.31 ms and SSE4.1 for the drop from about 100 ms.

## Use it when

- .NET Core 3.0+ / .NET 5+ on x86-64 with AVX2 and strings of hundreds to tens of thousands of characters: 64.8 µs vs Fastenshtein's 342.3 µs at 400 chars and 17.3 ms vs 82.2 ms at 8,000 chars (.NET Core 5, i7-6700HQ).
- GC-sensitive hot loops: single-threaded calls rent their buffers from ArrayPool and report 0-9 B allocated per call.
- Pairs that share a long common prefix or suffix, which are trimmed before the DP (516.4 ns vs Fastenshtein 672.1 ns on a 20-char similar pair in issue #86).
- .NET Framework with very long strings, where opt-in threading cut 8,000 chars from 99.8 ms to 30.8 ms on 4 cores.

## Skip it when

- Short strings without a shared prefix or suffix: Fastenshtein wins at 10 chars on .NET Core 5 (181.4 ns vs 317.7 ns) and at 20 chars on .NET 6 in a user report (663.8 ns vs 935.7 ns, issue #86, closed as not planned).
- .NET Framework / netstandard2.0 consumers and ARM64 (Apple Silicon, Graviton): the SIMD paths use only x86 Sse41/Avx2 classes, so these get the scalar loop, which lost to Fastenshtein at 400 chars on .NET 4.7.2 (625.7 µs vs 346.1 µs).
- When you need a distance cutoff, Damerau transpositions, weights, an edit script or fuzzy ratios: none exist (k-threshold issue #16 and edit-script issue #68 are closed with no such API in CalculationOptions or GetDistance).
- Grapheme- or culture-aware comparison: it compares UTF-16 code units ordinally, so a surrogate pair counts as two characters.
- C/C++ projects: this is C#. The algorithm comes from the header-only C++ levenshtein-sse, and bit-parallel Myers/Hyyrö implementations such as rapidfuzz-cpp (already catalogued) handle 64 DP cells per machine word versus 16 lanes here.

## How it is fast

It trims the common prefix and suffix first, then fills the DP matrix along anti-diagonals, so cells on one diagonal are independent. Using .NET hardware intrinsics it computes 16 ushort cells per AVX2 instruction (8 with SSE4.1; int32 lanes instead when the shorter string has 16 chars or fewer or either string reaches 65,535), with min/add/compare-equal and a byte shuffle that reverses the target slice. The wavefront scheme is credited in the code to Anna Henningsen's C++ levenshtein-sse. Only two diagonals are kept, rented from ArrayPool, so single-threaded calls do not allocate. Without intrinsics it falls back to a row-wise loop unrolled four rows at a time.

## Compared with alternatives

No catalogued sibling in simd-intrinsics-libraries does edit distance; they cover argmin/argmax, popcount, sorting, noise and linear algebra. For C++ the closer catalogued alternative is rapidfuzz-cpp (bit-parallel Levenshtein); pick Quickenshtein only when you are in .NET on x86 and need exact, unbounded Levenshtein on long strings.

## Integration

| | |
|---|---|
| **Form** | NuGet package (pure C# library with unsafe code) |
| **Dependencies** | none on netcoreapp3.0+; System.Memory on netstandard2.0 |
| **Minimum toolchain** | .NET Core 3.0+ for the intrinsics paths (NuGet 1.5.1 targets netcoreapp3.0 and netstandard2.0; repo main targets netcoreapp3.1 and netstandard2.0) |
| **Platforms** | any .NET platform; SIMD only on x86/x64 with SSE4.1 (16-lane path needs AVX2); ARM64 and .NET Framework run the scalar path |
| **Thread safety** | Static API with no mutable shared state apart from ArrayPool.Shared, so concurrent calls look safe from the code; not documented. Threaded mode itself fans one call out over the shared ThreadPool |
| **Drop-in for the baseline** | partial: same shape as Fastenshtein's static distance call (two strings in, int out) but a different namespace and method name (Levenshtein.GetDistance) |

## Gotchas

- Harness flaw in docs/OverallComparison.md: on .NET Core, CalculationOptions.DefaultWithThreading enables threading only at 16,000 chars (4,000 on .NET Framework), but the benchmark tops out at 8,000. The .NET Core 'Quickenshtein_Threaded' rows therefore run the single-threaded path: 16.97 ms vs 17.25 ms with the same 9 B allocated, against 1,024 B on the genuinely threaded .NET 4.7.2 row. docs/StringScenarios.md, an older run, shows threading barely helps on .NET Core (18.53 ms vs 18.02 ms at 8,192 chars; 286.3 ms vs 295.4 ms at 32,768). The threaded path uses the row-wise SSE4.1 kernel, not the AVX2 anti-diagonal kernel.
- Threaded mode busy-waits on Interlocked.CompareExchange without yielding, queues up to Environment.ProcessorCount - 1 workers on the shared ThreadPool and runs the last segment on the caller. Under ThreadPool starvation or oversubscription the caller spins until queued workers start; issue #13, 'Improving Threading Calculation Performance', is still open.
- The headline 20.92x is against a deliberately naive LINQ jagged-matrix baseline that allocates 256 MB at 8,000 chars, and the Ratio/Speedup columns are relative to the .NET 4.7.2 Baseline job (20.65x against the same-runtime baseline). Fastenshtein (about 4.8x) and the library's own no-intrinsics path (5.78x, 100.04 ms vs 17.31 ms) are the meaningful comparisons.
- Docs are stale relative to the code: published numbers are .NET Core 5.0.4 with a BenchmarkDotNet 0.12.1 ShortRun (3 iterations, 8,000-char error ±3.56 ms), while HEAD's benchmark project targets net6.0/net472 with BenchmarkDotNet 0.13.4. The StringScenarios header names .NET Core 3.0.1 jobs while its rows say .NET Core 5.0. All inputs are one synthetic pair of periodic 17-char patterns.

## Known shortcomings

- The 20.92x column is measured against a .NET 4.7.2 baseline (20.65x same-runtime, derived); the baseline is a naive LINQ matrix built to lose; slower than Fastenshtein at 10 characters and at 400 characters on .NET Framework; benchmark docs date from .NET 5; C#, loose category fit. Abandoned (last commit 2023-08-01).
- Harness flaw: on .NET Core, DefaultWithThreading enables threading only from 16,000 characters while the benchmark tops out at 8,000, so the .NET Core 'Threaded' rows ran the single-threaded path (same 9 B allocation; 16.97 vs 17.25 ms), and docs/StringScenarios.md shows threading giving about no gain on .NET Core (18.53 vs 18.02 ms). Issue #86: slower than Fastenshtein at 20 characters on .NET 6 (935.7 vs 663.8 ns). No ARM64 SIMD path; NuGet 1.5.1 was the last release (2021-05-23).

## Caveats and trade-offs

Slower than Fastenshtein on 10-character strings on .NET Core 5.0 (317.7 ns vs 181.4 ns). On .NET Framework 4.7.2 (no hardware intrinsics) Quickenshtein loses to Fastenshtein at 400 characters (625,731.9 ns vs 346,120.9 ns) and ties it at 8000 characters single-threaded (99,787,886.7 ns vs 101,566,466.7 ns); it wins there only in threaded mode (30,820,936.5 ns), which compares multi-threaded against single-threaded Fastenshtein. The 'Baseline' is a deliberately naive jagged-matrix implementation built with LINQ that allocates the full (n+1)x(m+1) matrix (256 MB at 8000 characters), so the 20x figure is against a strawman; Fastenshtein (about 4.8x) and the library's own no-intrinsics path (about 5.8x) are the meaningful comparisons. The table's Ratio/Speedup columns are relative to the .NET 4.7.2 Baseline job, not the same-runtime baseline. ShortRun job with 3 iterations and 1 launch, so error bars are wide (Quickenshtein 8000 chars: error 3,559,513.67 ns). One synthetic string pair built by repeating 'aabcdecbaabcadbab' and 'babdacbaabcedcbaa'. Published numbers come from an older revision (.NET Core 5.0, BenchmarkDotNet 0.12.1); the current benchmark project targets net6.0 and net472 with BenchmarkDotNet 0.13.4 and Fastenshtein 1.0.0.8, so HEAD reproduces a different configuration. C# library, not C++. [retier] The headline 20.92x is against a deliberately naive LINQ jagged-matrix baseline that allocates the full (n+1)x(m+1) matrix (256 MB at 8,000 chars); Fastenshtein (about 4.8x) and the library's own no-intrinsics path (5.78x) are the meaningful comparisons. Harness flaw: the .NET Core 'Threaded' rows ran single-threaded (threading threshold 16,000 chars above the benchmark's 8,000), and docs/StringScenarios.md shows threading giving about no gain on .NET Core (18.53 vs 18.02 ms). On .NET Framework 4.7.2 (no hardware intrinsics) Quickenshtein loses to Fastenshtein at 400 characters and ties it at 8000 single-threaded, winning only in threaded mode. Threaded mode busy-waits on Interlocked.CompareExchange without yielding and queues workers on the shared ThreadPool (issue #13 open). Published numbers are .NET Core 5.0.4 with a 3-iteration ShortRun (error plus or minus 3.56 ms at 8,000 chars) while HEAD's benchmark project targets net6.0/net472 with BenchmarkDotNet 0.13.4; all inputs are one synthetic pair of periodic 17-char patterns. No ARM64 SIMD path; last NuGet release 1.5.1 (2021-05-23).

Uses hardware intrinsics with scalar fallback; optional multi-threading allocates a little; the benchmark shows large gains only with SSE4.1 and AVX2 enabled (disabling SSE4.1 gives the no-intrinsics time).

## Maintenance

Abandoned: last release NuGet 1.5.1 on 2021-05-23 (about 888K downloads), last commit a 2023-08-01 dependency bump, four open performance issues since 2020; MIT, pure C# and a handful of files, so easy to vendor, but no ARM64 SIMD path.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/OverallComparison.md is BenchmarkDotNet output from benchmarks/Quickenshtein.Benchmarks/Comparisons/QuickComparisonBenchmark.cs (public), comparing the repo's naive LevenshteinBaseline.cs and Fastenshtein, with .NET Core SDK 5.0.201 / .NET Core 5.0.4 RyuJIT and .NET Framework 4.8, BenchmarkDotNet ShortRun job and Intel Core i7-6700HQ stated, so code, toolchain, job settings and CPU model are all present.
- **Verifier notes:** Numbers match OverallComparison.md and IntrinsicsPerformance.md exactly; the only claim fix is that the 20.92x column is relative to the .NET 4.7.2 Baseline job (20.65x vs the same-runtime baseline, derived). Main shortcomings for decisions.json: strawman baseline (naive LINQ jagged-matrix), slower than Fastenshtein on 10-char strings and on .NET Framework at 400 chars, stale docs from .NET 5, C# not C++; category simd-intrinsics-libraries fits loosely (it is a Levenshtein library that uses SIMD, closer to a string-algorithms category). Last commit 2023-08-01 (dependency bump), more than 3 years old, so 'abandoned' stands; license MIT (License.txt), 315 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-57 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Turnerj/Quickenshtein/blob/main/docs/OverallComparison.md>
  - <https://github.com/Turnerj/Quickenshtein/blob/main/docs/IntrinsicsPerformance.md>
  - <https://github.com/Turnerj/Quickenshtein/blob/main/readme.md>
  - <https://github.com/Turnerj/Quickenshtein/blob/main/License.txt>
  - <https://github.com/Turnerj/Quickenshtein>
  - <https://github.com/Turnerj/Quickenshtein/commits>
  - <https://github.com/Turnerj/Quickenshtein/tree/main/benchmarks/Quickenshtein.Benchmarks>
  - <https://github.com/Turnerj/Quickenshtein/tree/main/benchmarks/Quickenshtein.Benchmarks/Comparisons>
  - <https://github.com/Turnerj/Quickenshtein/tree/main/benchmarks/Quickenshtein.Benchmarks/Config>
  - <https://github.com/Turnerj/Quickenshtein/blob/main/benchmarks/Quickenshtein.Benchmarks/LevenshteinBaseline.cs>
  - <https://github.com/Turnerj/Quickenshtein/blob/main/benchmarks/Quickenshtein.Benchmarks/Program.cs>
  - <https://github.com/Turnerj/Quickenshtein/blob/main/benchmarks/Quickenshtein.Benchmarks/Quickenshtein.Benchmarks.csproj>
  - <https://github.com/Turnerj/Quickenshtein/blob/main/benchmarks/Quickenshtein.Benchmarks/Comparisons/QuickComparisonBenchmark.cs>
  - <https://github.com/Turnerj/Quickenshtein/blob/main/benchmarks/Quickenshtein.Benchmarks/Config/BaseRuntimeQuickConfig.cs>
  - <https://github.com/Turnerj/Quickenshtein/blob/main/benchmarks/Quickenshtein.Benchmarks/Config/BaseRuntimeConfig.cs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/readme.md>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/docs/OverallComparison.md>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/docs/IntrinsicsPerformance.md>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/docs/StringScenarios.md>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/src/Quickenshtein/Levenshtein.cs>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/src/Quickenshtein/Levenshtein.Intrinsics.cs>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/src/Quickenshtein/Levenshtein.Threaded.cs>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/src/Quickenshtein/Levenshtein.Common.cs>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/src/Quickenshtein/CalculationOptions.cs>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/src/Quickenshtein/WorkerState.cs>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/src/Quickenshtein/AssemblyInternals.cs>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/src/Quickenshtein/Quickenshtein.csproj>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/src/Directory.Build.props>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/benchmarks/Quickenshtein.Benchmarks/LevenshteinBaseline.cs>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/benchmarks/Quickenshtein.Benchmarks/Comparisons/QuickComparisonBenchmark.cs>
  - <https://raw.githubusercontent.com/Turnerj/Quickenshtein/main/benchmarks/Quickenshtein.Benchmarks/Quickenshtein.Benchmarks.csproj>
  - <https://github.com/Turnerj/Quickenshtein/tree/main/src/Quickenshtein>
  - <https://github.com/Turnerj/Quickenshtein/issues?q=is%3Aissue>
  - <https://github.com/Turnerj/Quickenshtein/issues/86>
  - <https://www.nuget.org/packages/Quickenshtein/>
  - <https://github.com/addaleax/levenshtein-sse>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/turnerj/quickenshtein`) · [data/wave13/enrich/raw/github_com_turnerj_quickenshtein.json](../../../data/wave13/enrich/raw/github_com_turnerj_quickenshtein.json) (enrichment confidence 0.75)

</details>
