# LinqFaster

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟡 stale

> Eager LINQ-style C# extension methods, with optional SIMD and parallel variants, for arrays, Span and List; beat .NET Framework LINQ 4-55x in 2017.

| | |
|---|---|
| **Beats** | System.Linq (LINQ to Objects) Min, Sum and OrderBy on int arrays under .NET Framework 4.x (CLR 4.0.30319.42000, 64-bit RyuJIT) |
| **Claimed result** | README sample benchmarks (100000 elements, .NET Framework 4.x, BenchmarkDotNet): MinLinq 548.9181 us vs MinFastSIMD 14.5291 us (about 37.8x, derived from page data); SumLinq 541.3823 us vs SumFastSIMD 9.7636 us (about 55.4x, derived; SumS is unchecked while LINQ Sum is overflow-checked, and the checked SumF gives about 10x); OrderByLinq 24,436.0135 us vs OrderByFast 5,612.7712 us (about 4.4x, derived; OrderByF is not a stable sort). The README's SumFastSIMDParallel 3.7074 us row is struck: it was measured at commit 5c5403e (2017-03-31), when the SumSP task lambdas captured the shared loop variable and late-starting tasks summed nothing, so the result was wrong; the fix (11a5421) was followed by 'parallel simd sum fixed but now is slow :D' (e8eb1d7) and the row was never re-measured. |
| **Workload** | LINQ-style extension methods on arrays, Span&lt;T&gt; and List&lt;T&gt;; benchmark with 100000 elements for OrderBy, Min and Sum, including SIMD (MinFastSIMD, SumFastSIMD) and SIMD plus parallel variants. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6600U @ 2.60GHz (2 cores, ProcessorCount=4), Windows, per the Benchmarks.md header; the README says '64bit Win 10, 2 Core I7 Mobile' |
| **Compiler and flags** | BenchmarkDotNet v0.10.3.0, .NET Framework CLR 4.0.30319.42000, 64-bit RyuJIT-v4.6.1637.0, Job=RyuJitX64 Platform=X64 (Benchmarks.md header); the MinFastSIMD and SumFastSIMDParallel README rows are not in Benchmarks.md and carry no methodology |
| **Adoption** | 762 stars; NuGet packages LinqFaster, LinqFaster.SIMD, LinqFaster.Parallel |
| **Last commit** | 2025-09-26 |
| **Links** | [repository](https://github.com/jackmott/LinqFaster) · [benchmark](https://github.com/jackmott/LinqFaster) |

## Verdict

BenchmarkDotNet 0.10.3, .NET Framework 4.x 64-bit RyuJIT, Core i7-6600U, 100,000 random ints in [-100, 100) (Benchmarks.cs at commit f729004, 2017-03-31). LINQ Min took 548.9 us against 14.5 us for MinS (37.8x). LINQ Sum took 541.4 us against 9.76 us for SumS (55.4x), but SumS is unchecked; the like-for-like checked scalar SumF at 53.8 us is about 10x. OrderBy took 24,436 us against 5,613 us for the unstable OrderByF (4.35x). All ratios are derived from page data. The README's SumFastSIMDParallel row (3.7074 us) is not valid evidence (see status_note).

## Use it when

- Hot Sum, Min, Max or Average calls over primitive arrays in code pinned to .NET Framework 4.6.1+ or netstandard2.0, including Unity, which the base package targets.
- Float or int array reductions where SIMD's reordered or unchecked arithmetic is acceptable: SumS ran 9.8 us against 541 us for LINQ on 100,000 ints in 2017.
- Select-then-ToArray or Where-then-Aggregate patterns on arrays where the fused or in-place methods remove intermediate allocations.
- Sorting arrays by a key when stability does not matter: OrderByF ran about 4.35x faster than LINQ OrderBy in the 2017 run.
- Very large arrays or expensive per-element work for the P and SP methods; the README warns they allocate and may not beat the scalar or SIMD versions.

## Skip it when

- .NET 7 and later: runtime LINQ vectorized Min, Max, Sum and Average for arrays and lists in .NET 7, and Enumerable.Sum in .NET 8 (with overflow checks), per search snippets of a PVS-Studio article and a Microsoft compatibility notice. The README itself says that as of .NET 9 the library is 'mostly unnecessary'.
- When you need LINQ's exact semantics: SumS, SumSP and AverageS on int wrap on overflow instead of throwing; OrderByF is not stable; and chained F calls are eager, so each step allocates and iterates where LINQ would make one lazy pass.
- ContainsS on arrays whose length is a multiple of Vector&lt;T&gt;.Count: it misses matches in the last vector-width block (open issue #31; the bug is still in the code at HEAD).
- Small integer element types with the SIMD sum: SumS on ushort[] throws InvalidCastException (open issue #18).
- SIMD over List&lt;T&gt; or Span&lt;T&gt;: the S and SP methods exist only for arrays.

## How it is fast

The scalar methods index the array or list directly instead of going through IEnumerable&lt;T&gt; MoveNext/Current interface calls, and they allocate no enumerator. The S methods accumulate in System.Numerics.Vector&lt;T&gt; registers, whose width the JIT picks (8 ints with AVX2), and reduce horizontally at the end. Generic arithmetic is a chain of typeof(T) == typeof(int) tests that RyuJIT folds away for value types. OrderByF computes a key array and calls Array.Sort(keys, items), an unstable introsort, where LINQ OrderBy runs a stable, lazily enumerated sort. The P and SP methods split the array into ranges across Environment.ProcessorCount tasks.

## Compared with alternatives

LinqFaster is the only catalogued SIMD entry that offers generic LINQ-shaped reductions for C#. The other SIMD libraries are C, C++, Rust or Go (tphakala/simd, argminmax, sse-popcount), and Quickenshtein, the other .NET entry, only computes Levenshtein distance. Pick LinqFaster for legacy .NET Framework, netstandard2.0 or Unity code that wants SIMD Sum, Min, Max or Average over primitive arrays without writing Vector&lt;T&gt; loops; on modern .NET use the built-in LINQ.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | LinqFaster: System.Memory 4.5.3; LinqFaster.SIMD: System.Numerics.Vectors 4.5.0; LinqFaster.Parallel and LinqFaster.SIMD.Parallel: System.Threading.Tasks.Parallel 4.3.0 on netstandard1.3 (SIMD.Parallel also System.Numerics.Vectors 4.5.0) |
| **Minimum toolchain** | netstandard2.0 or net461 for LinqFaster; netstandard2.0 for LinqFaster.SIMD; netstandard1.3, netstandard2.0 or net461 for the two parallel packages. SIMD gains need a JIT with hardware-accelerated Vector&lt;T&gt; (the benchmarks used 64-bit RyuJIT on .NET Framework 4.x). |
| **Platforms** | Any .NET runtime that supports those targets, Unity included for the base package; the SIMD width follows the JIT and CPU (SSE or AVX2). |
| **Thread safety** | not documented; the methods are static and keep no shared state, and the P and SP methods use Tasks internally. |
| **Drop-in for the baseline** | partial: names add an F, S, P or SP suffix; methods are eager and return arrays or lists; OrderByF is unstable; SIMD sums are unchecked |

## Gotchas

- ContainsS at HEAD loops while i &lt; source.Length - count and then scans leftovers from Length - Length % count. When Length is a multiple of Vector&lt;T&gt;.Count, the last full vector is never checked, so new[]{1,2,3,4,5,6,7,8}.ContainsS(5) returns false. This is issue #31, open since April 2022 with a one-character fix proposed.
- SumS(selectorSIMD) silently drops the leftover elements unless you also pass the scalar selector. It steps by Vector&lt;U&gt;.Count while loading Vector&lt;T&gt;, so it is only correct when T and U have the same width. SequenceCompareS reinterprets comparison masks as Vector&lt;int&gt;, so it is only correct for 32-bit element types.
- SumF is checked, like LINQ Sum, but SumS and SumSP are not. AverageS sums through SumS, so int averages wrap on overflow, and float sums differ from the scalar results (the README notes this).
- On nuget.org, LinqFaster stops at 1.0.0 (2018-02-05) while the repo's csproj is 1.1.0 with the Span&lt;T&gt; overloads added in February 2019. The Span support appears to be unpublished in the base package (other package IDs were not checked). LinqFaster.SIMD's last release is 1.0.3 (2019-07-12).

## Known shortcomings

- Baseline is .NET Framework 4.x LINQ on an i7-6600U (Benchmarks.md); the bench methods are commented out at HEAD; SumS is unchecked against LINQ's checked Sum and OrderByF is unstable; .NET 9 LINQ has since absorbed such optimisations. C#. Code unchanged since 2019.
- Harness flaw: the README SumFastSIMDParallel 3.7074 us row was measured at 5c5403e (2017-03-31), when the SumSP task lambdas captured the shared loop variable index, so late-starting tasks summed nothing and the result was wrong; fixed in 11a5421, after which the author committed 'parallel simd sum fixed but now is slow :D' (e8eb1d7) and never re-measured the row (struck from the claim). The like-for-like checked Sum ratio is about 10x (SumF), not 55x (unchecked SumS). Correctness bug at HEAD: ContainsS skips the last full vector when Length % Vector&lt;T&gt;.Count == 0 (issue #31, open since 2022). Benchmarks.md data is random ints in [-100, 100) at f729004. The NuGet base package stops at 1.0.0 (2018); the Span overloads appear unpublished.

## Caveats and trade-offs

The README itself says that as of .NET 9 the library is mostly unnecessary because the runtime LINQ received most of these optimizations; the baseline is .NET Framework 4.x LINQ, which is far slower than modern .NET LINQ. The benchmark methods for these rows are commented out in Benchmarks/Benchmarks.cs at HEAD and TEST_SIZE there is 1000000 (data i % 2), so the published 100000-element run is not reproducible as checked in. SumS (SIMD) sums without overflow checking while LINQ Sum on int throws OverflowException, so the 55x Sum row compares unequal semantics; OrderByF is not a stable sort while LINQ OrderBy is (README Limitations). Several ratios exceed 50x (Sum SIMD about 55.4x, derived). Library code unchanged since 2019-07-12; the 2025-09-26 commit only edited the README. [retier] The README itself says that as of .NET 9 the library is mostly unnecessary because runtime LINQ received most of these optimizations; the baseline is .NET Framework 4.x LINQ, far slower than modern .NET LINQ. The benchmark methods for these rows are commented out in Benchmarks/Benchmarks.cs at HEAD and TEST_SIZE there is 1000000 (data i % 2); Benchmarks.md data is random ints in [-100, 100) at f729004, so the published 100000-element run is not reproducible as checked in. The SumFastSIMDParallel row measured a broken implementation (shared loop variable captured by the task lambdas at 5c5403e) and is struck. SumS and SumSP sum without overflow checking while LINQ Sum on int throws OverflowException (the checked SumF gives about 10x); OrderByF is not a stable sort while LINQ OrderBy is. Correctness bug at HEAD: ContainsS skips the last full vector when Length % Vector&lt;T&gt;.Count == 0, so new[]{1,2,3,4,5,6,7,8}.ContainsS(5) returns false (issue #31, open since April 2022); SumS(selectorSIMD) drops leftover elements unless the scalar selector is also passed; SequenceCompareS is only correct for 32-bit element types. Library code unchanged since 2019-07-12; on nuget.org LinqFaster stops at 1.0.0 (2018) and LinqFaster.SIMD at 1.0.3 (2019), so the Span&lt;T&gt; overloads appear unpublished.

SIMD and parallel variants ship as separate projects and NuGet packages; method names carry an F suffix (for example SelectF, MinF) instead of being drop-in LINQ; extension methods target arrays, Span&lt;T&gt; and List&lt;T&gt;.

## Maintenance

Harness flaw: the README's SumFastSIMDParallel row (3.7074 us, added in commit 5c5403e on 2017-03-31) was measured on SumPS. Its ForStrideAggregate lambdas captured the shared loop variable index, so tasks that started after the loop finished summed an empty range and the result was wrong. The capture was fixed the next day (11a5421, 'fixing parallel bugs'), after which the author committed 'parallel simd sum fixed but now is slow :D' (e8eb1d7), and the row was never re-measured. Separately, the library is stale: its code is unchanged since 2019-07-12 and the last commit (2025-09-26) only edited the README. It is MIT-licensed and small enough to copy, but obsolete on .NET 7 and later, and the ContainsS bug remains open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party BenchmarkDotNet numbers; Benchmarks.md names the CPU (i7-6600U) and runtime, but the benchmark methods behind the README table are commented out in Benchmarks/Benchmarks.cs at HEAD with TEST_SIZE changed to 1000000, and the MinFastSIMD and SumFastSIMDParallel rows appear only in the README with no methodology, so it falls short of A.
- **Verifier notes:** All README numbers match (Min 548.9181 vs 14.5291 us, about 37.8x; Sum 541.3823 vs 9.7636 us, about 55.4x; OrderBy 24,436.0135 vs 5,612.7712 us, about 4.35x; derived from page data). License confirmed MIT (LICENSE, Copyright 2017 Jack Mott); 762 stars, 35 forks, 189 commits; maintenance stays stale (last commit 2025-09-26, a README edit). NuGet package names not checked (nuget.org blocked by egress policy).
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `hardware`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-58 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/jackmott/LinqFaster>
  - <https://github.com/jackmott/LinqFaster/commits>
  - <https://github.com/jackmott/LinqFaster/tree/master/Benchmarks>
  - <https://github.com/jackmott/LinqFaster/tree/master/BenchmarksCore>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/README.md>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/Benchmarks.md>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/Benchmarks/Benchmarks.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/BenchmarksCore/Program.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/BenchmarksCore/BenchmarksCore.csproj>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFasterSIMD/SumSIMD.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFaster/Sum.cs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/README.md>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/Benchmarks.md>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/Benchmarks/Benchmarks.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFasterSIMD/SumSIMD.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFasterSIMD/MinSIMD.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFasterSIMD/ContainsSIMD.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFasterSIMD/SequenceEqualSIMD.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFasterSIMD/AverageSIMD.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFasterSIMD/LinqFasterSIMD.csproj>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFaster/Sum.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFaster/Min.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFaster/OrderBy.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFaster/Utils/GenericOperators.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFaster/LinqFaster.csproj>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFasterParallel/LinqFasterParallel.csproj>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/LinqFasterParallelSIMD/LinqFasterParallelSIMD.csproj>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/f729004/Benchmarks/Benchmarks.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/64ffed4/Benchmarks/Benchmarks.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/eff6c81/Benchmarks/Benchmarks.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/f729004/README.md>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/7b5b743/README.md>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/5c5403e/README.md>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/df2c096/README.md>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/5c5403e/LinqFaster/Utils/ParallelUtils.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/5c5403e/LinqFaster/SIMD/SumSIMD.cs>
  - <https://github.com/jackmott/LinqFaster/commits/master/Benchmarks/Benchmarks.cs>
  - <https://github.com/jackmott/LinqFaster/commits/master/Benchmarks.md>
  - <https://github.com/jackmott/LinqFaster/commits/master/README.md>
  - <https://github.com/jackmott/LinqFaster/commit/1a09730>
  - <https://github.com/jackmott/LinqFaster/commit/e8eb1d7>
  - <https://github.com/jackmott/LinqFaster/commit/11a5421>
  - <https://github.com/jackmott/LinqFaster/tree/master/LinqFasterSIMD>
  - <https://github.com/jackmott/LinqFaster/issues?q=is%3Aissue>
  - <https://github.com/jackmott/LinqFaster/issues/31>
  - <https://github.com/jackmott/LinqFaster/issues/18>
  - <https://api.nuget.org/v3/registration5-semver1/linqfaster/index.json>
  - <https://api.nuget.org/v3/registration5-semver1/linqfaster.simd/index.json>
  - <https://api.nuget.org/v3/registration5-semver1/linqfaster.parallel/index.json>
  - <https://api.nuget.org/v3/registration5-semver1/linqfaster.simd.parallel/index.json>
  - https://learn.microsoft.com/en-in/dotnet/core/compatibility/core-libraries/8.0/enumerable-sum (search snippet only)
  - https://pvs-studio.com/en/blog/posts/csharp/1011 (search snippet only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jackmott/linqfaster`) · [data/wave13/enrich/raw/github_com_jackmott_linqfaster.json](../../../data/wave13/enrich/raw/github_com_jackmott_linqfaster.json) (enrichment confidence 0.75)

</details>
