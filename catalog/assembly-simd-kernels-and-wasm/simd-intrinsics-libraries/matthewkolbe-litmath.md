# LitMath

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `Apache-2.0` · 🟡 stale

> C#/.NET AVX2 and AVX-512 array math (Exp, Ln, Sin, Erf, normal CDF, Sqrt), 5-7x over a scalar System.Math loop.

| | |
|---|---|
| **Beats** | naive scalar loop over System.Math.Exp and System.Math.Log (NaiveExpDouble, NaiveLogDouble); an older README table also compared Intel MKL via MKL.NET Vml.Exp |
| **Claimed result** | Current README (AVX-512 section, .NET 8): Exp N=100000 NaiveExpDouble 354,491.80 ns vs LitExpDouble 64,727.96 ns (5.5x, derived from page data); Log N=100000 259,985.93 ns vs 35,793.39 ns (7.3x, derived from page data; README text says 7.5x); N=64 Exp 218.69 ns vs 42.34 ns (5.2x, derived), Log 137.06 ns vs 24.89 ns (5.5x, derived). An earlier README table (commit 3d4c302, Nov 2023, AVX2 era, removed on 2023-11-16) shows LitExpDouble vs naive 1.7x at N=3, 3.3x at N=64, 3.1x at N=2048, 2.8x at N=65536 and 2.4x at N=32,000,000, and vs MKL.NET Vml.Exp: LitMath faster at N=3 (6.675 vs 29.871 ns, 4.5x), N=64 (71.946 vs 116.934 ns, 1.6x) and N=2048 (2,446 vs 3,239 ns, 1.3x), but MKL faster at N=65536 (19,160 vs 82,346 ns, 4.3x) and N=32,000,000 (23.7 ms vs 47.1 ms, 2.0x) (ratios derived from page data). The README's '10x versus MKL' remark is not backed by any table. |
| **Workload** | AVX2 and AVX-512 double-precision Exp, Log and other math functions on arrays of 64 and 100000 doubles. |
| **Metric** | throughput |
| **Hardware** | Not stated for the current table (an AVX-512 machine; the author's Zen 3 dev machine has no AVX-512). The MKL comparison was on an unnamed Zen 3 CPU. |
| **Compiler and flags** | BenchmarkDotNet 0.13.1 (LitMathBenchmarks.csproj targets net6.0 and net8.0); the runtime used for the README table is not stated; AVX-512 paths need .NET 8 |
| **Adoption** | 79 stars |
| **Last commit** | 2024-03-28 |
| **Links** | [repository](https://github.com/matthewkolbe/LitMath) · [benchmark](https://github.com/matthewkolbe/LitMath) |

## Verdict

A BenchmarkDotNet table in the README, from an unnamed AVX-512 machine on an unstated runtime (AVX-512 needs .NET 8), times a scalar loop of System.Math.Exp/Log (calling the platform C runtime's exp/log) against Lit.Exp/Lit.Ln on 64 and 100,000 doubles: Exp 218.69 vs 42.34 ns and 354,492 vs 64,728 ns (5.2x and 5.5x), Log 137.06 vs 24.89 ns and 259,986 vs 35,793 ns (5.5x and 7.3x). The benchmark inputs (no exact ties, no zeros, lengths that are multiples of 8) avoid the bugs above, so the timings stand but say nothing about edge-case correctness.

## Use it when

- C# or F# code on x86-64 servers with AVX2 and FMA (or AVX-512 under .NET 8) that applies Exp or Ln to arrays of doubles or floats: 5.2-7.3x over a System.Math loop in the author's AVX-512 table, 2.4-3.3x on AVX2 in the older table.
- Small and medium arrays (a few to about 2,000 elements) where P/Invoke marshalling into Intel MKL dominates: the author's older table has LitMath ahead of MKL.NET Vml.Exp by 4.5x at 3 elements, 1.6x at 64 and 1.3x at 2,048.
- Composite element-wise formulas (option pricing, normal CDF, Erf) written once against the Vector256 overloads so the array is traversed a single time instead of once per function.
- Workloads whose Exp arguments stay small in magnitude (roughly |x| &lt; 30), where the Exp polynomial is within a few ulps.

## Skip it when

- Large arrays where you can call MKL: in the author's own older table MKL.NET Vml.Exp was 4.3x faster at 65,536 elements and 2.0x faster at 32,000,000.
- Non-x86 or pre-AVX2 hardware: apart from the AVX512F switch there are no IsSupported checks or scalar fallbacks, so ARM64 (including Apple silicon) and CPUs without AVX2/FMA get PlatformNotSupportedException.
- Code that needs correct edge cases or full double accuracy at large magnitudes: Ln(0) returns +Infinity on the AVX2 path, Exp error grows to about 220 ulps near |x| = 700, and the AVX-512 paths have the bugs listed under gotchas.
- Projects that need maintenance: the last commit was 2024-03-28 (README edits), there are no issues or releases on GitHub, and the README calls the AVX-512 numbers preliminary.
- C or C++ code: this is a managed .NET library.

## How it is fast

Hand-written System.Runtime.Intrinsics code processes 4 doubles per AVX2 vector, or 8 per AVX-512 vector when running on .NET 8 with AVX512F, with the span loop unrolled four times. Exp computes 2^(x\*log2 e) by rounding to the nearest integer n, evaluating a degree-11 polynomial in FMA (split odd/even Horner chains) on the fraction, and building 2^n from exponent bits (AVX2) or VSCALEFPD (AVX-512). Ln extracts exponent and mantissa (bit masks on AVX2, VGETEXPPD/VGETMANTPD on AVX-512) and evaluates a fitted series of the atanh form ln(d) = 2\*atanh((d-1)/(d+1)), with one division per vector.

## Compared with alternatives

Pick LitMath only from .NET code on x86-64; for C++ the Vector Class Library or corvus give vectorised exp/log/sin in-process, and math_intrinsics and SIMD-math-prims cover single-precision approximations in C. Among .NET siblings, SimpleSIMD and LinqFaster vectorise reductions and LINQ operators, not transcendental functions.

## Integration

| | |
|---|---|
| **Form** | shared lib (NuGet package Kolbe.LitMath, a managed .NET assembly; source is a small set of C# files) |
| **Dependencies** | none beyond the .NET runtime (System.Runtime.Intrinsics); benchmarks use BenchmarkDotNet 0.13.1, MathNet.Numerics 5.0.0 and MKL.NET 1.3.2 (win-x64) |
| **Minimum toolchain** | .NET 6 for the AVX2 paths; .NET 8 for the AVX-512 paths (multi-targets net6.0 and net8.0) |
| **Platforms** | x86-64 with AVX2 and FMA required; AVX-512F used automatically on .NET 8; no ARM64 or scalar fallback |
| **Thread safety** | not documented; the functions are static and keep no shared mutable state apart from static readonly constant vectors, so concurrent calls on disjoint spans look safe (code reading) |
| **Drop-in for the baseline** | partial — same math as System.Math.Exp/Log, but called on spans or Vector256/Vector512 values rather than per scalar, and results differ in the last bits and at edge cases |

## Gotchas

- Correctness bugs in the AVX-512 paths (found by reading the code; emulated in Python with the repo's constants, not run on AVX-512 hardware): Two(Vector512) picks the polynomial's integer part with RoundScale (round to nearest even) but scales by VSCALEFPD of x + 0.5, which floors, so when x\*log2(e) is exactly 0.5, 2.5, -1.5 and similar ties the result is doubled, e.g. Exp(0.5\*ln 2) gives 2.828 instead of 1.414. Ln(Span&lt;double&gt;) with 5 to 7 elements takes a 4-lane Vector256 masked path while VSZ is 8, so outputs 4 to n-1 are never written; the allocating Ln(in Span&lt;double&gt;) overload then returns uninitialised memory there. The AVX-512 Ln also drops the NaN/zero/infinity masking of the AVX2 path. The tests cover n = 1, 3, 9, 15, 33, 62 and negatives only at n = 4 (which takes the AVX2 path), so none of this is caught.
- Ln(0) returns +Infinity on the AVX2 path, because Constants.Double.Log.NEGATIVE_INFINITY is created from double.PositiveInfinity (same typo in the Vector512 constant block).
- Exp reduces with a single multiply by log2(e) and no Cody-Waite split, so the error grows with |x|: about 1.6 ulps on [-1, 1], 14 ulps up to |x| = 30 and about 220 ulps near |x| = 600-700 (emulated); the README's 'Exp at double precision limits' only holds near zero. Ln has about 3.6e-15 absolute error but relative error up to roughly 1e-12 (AVX2) to 2e-11 (AVX-512) just below 1.0 from cancellation.
- Harness and example flaws: the README points to LitExpDoubleParallel as the way to go multicore, but it slices Slice(i, n) instead of Slice(i\*n, n), so the tasks overwrite overlapping copies of the first N/cores elements and most of the array is never computed. In the timed benchmarks the naive loops store into one scalar field while LitMath writes an output array, LogBenchmark at N = 64 is Log(1.0) for every element (integer division), ExpBenchmark feeds Exp(Log(k)) for integers k = 0..100, and the committed ExpBenchmark runs only N = 3,200,000, not the published 64 and 100,000. Span tails reprocess the last vector with overlap, so calling a function in place (same span for input and output) applies it twice to some tail elements when n is not a multiple of the vector width.

## Known shortcomings

- No CPU or .NET version; the published Exp N=64/100000 setup is not in the repo (the committed bench uses 3,200,000) and integer division makes inputs degenerate (Log N=64 all 1.0); the author's older table (commit 3d4c302) shows MKL 4.3x faster at N=65536 and 2.0x at 32M, and the "10x vs MKL" claim has no table. C#. Stale since 2024-03-28.
- Correctness bugs found by code reading plus Python emulation (not run on AVX-512 hardware); the timed numbers are unaffected: the AVX-512 Exp rounds to nearest even but VSCALEFPD floors x + 0.5, so ties double the result (Exp(0.5\*ln 2) gives 2.828, not 1.414); AVX-512 Ln(Span&lt;double&gt;) with 5-7 elements leaves outputs 4..n-1 unwritten; AVX2 Ln(0) returns +Infinity (the NEGATIVE_INFINITY constant is built from PositiveInfinity); Exp error reaches about 220 ulp near |x| = 700. The README-recommended LitExpDoubleParallel slices Slice(i, n) instead of Slice(i\*n, n), so most of the array is never computed.

## Caveats and trade-offs

No CPU model or runtime version beside the table; the README calls the AVX-512 numbers preliminary. The committed ExpBenchmark.cs (last changed Dec 2022) runs N=3,200,000 only, so the published Exp N=64/100000 rows came from an uncommitted configuration. Benchmark inputs are built with C# integer division: LogBenchmark at N=64 computes Log(1.0) for all 64 elements (degenerate input), and ExpBenchmark feeds Log(k) for integers k=0..100 (about 1% -Infinity at N=100000), so inputs cover a narrow range. The naive loops store into a single scalar field while LitMath writes an output array. MKL.NET Vml.Exp beats LitMath at N=65536 and above in the author's own older table; the '10x vs MKL' claim has no table. ATan accuracy is 1e-10 versus 1e-15 for Sin, Log and Cos. C#/.NET library, not C++. [retier] No CPU model or runtime version beside the table; the README calls the AVX-512 numbers preliminary; the committed ExpBenchmark.cs (last changed December 2022) runs N = 3,200,000 only, so the published Exp N = 64/100000 rows came from an uncommitted configuration. Benchmark inputs are narrow: LogBenchmark at N = 64 computes Log(1.0) for every element (integer division) and ExpBenchmark feeds Log(k) for integers k = 0..100; the naive loops store into a single scalar field while LitMath writes an output array. MKL.NET Vml.Exp beats LitMath at N = 65536 and above in the author's own older table. Correctness bugs (found by code reading plus Python emulation with the repo's constants, not run on AVX-512 hardware; timed numbers unaffected): the AVX-512 Two(Vector512) picks the integer part with RoundScale (round to nearest even) but scales with VSCALEFPD of x + 0.5, which floors, so when x\*log2(e) is exactly a tie the result is doubled (Exp(0.5\*ln 2) gives 2.828 instead of 1.414); AVX-512 Ln(Span&lt;double&gt;) with 5-7 elements takes a 4-lane masked path while VSZ is 8, leaving outputs 4..n-1 unwritten; AVX2 Ln(0) returns +Infinity because Constants.Double.Log.NEGATIVE_INFINITY is built from double.PositiveInfinity (same typo in the Vector512 block); Exp reduces with a single multiply by log2(e) and no Cody-Waite split, so error grows to about 14 ulps at |x| = 30 and about 220 ulps near |x| = 600-700; Ln has relative error up to roughly 1e-12 (AVX2) to 2e-11 (AVX-512) just below 1.0. The README-recommended LitExpDoubleParallel slices Slice(i, n) instead of Slice(i\*n, n), so the tasks overwrite the first N/cores elements and most of the array is never computed.

AVX2 or AVX-512 hardware needed for the fast path; stated accuracies: Exp and Sqrt at double limits, ERF 1e-13, Sin/Log/Cos 1e-15, Tan 2e-16 on [0, pi/4], ATan 1e-10; chaining Vector256 functions avoids temporary arrays.

## Maintenance

Stale since 2024-03-28 (last code change 2023-12; 79 stars, no GitHub issues), Apache-2.0 and published on NuGet as Kolbe.LitMath 0.7.0. Usable for AVX2 double Exp and Ln in .NET if you avoid zero inputs, in-place calls and the AVX-512 paths until the rounding, short-span and special-value bugs are fixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party BenchmarkDotNet table in the README against a scalar System.Math.Exp/Log loop; benchmark code is public (LitMathBenchmarks/ExpBenchmark.cs, LogBenchmark.cs) but no CPU model and no .NET runtime version are given for the current table, and the committed ExpBenchmark uses Params(3_200_000), not the N=64/100000 shown, so the run configuration is not in public sources.
- **Verifier notes:** Numbers match the README; ratios are 5.2-7.3x versus a scalar .NET Math loop with AVX-512, about 2.4-3.3x in the older AVX2 table. Shortcomings to record: no CPU model or runtime version, published Exp configuration not in the repo, degenerate integer-division inputs (Log N=64 is all 1.0), MKL faster at large N in the author's own older table, stale since 2024-03-28, C# rather than C++.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`, `baseline`
- **Shortcomings recorded by:** verifier batch-59 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/matthewkolbe/LitMath>
  - <https://github.com/matthewkolbe/LitMath/commits>
  - <https://github.com/matthewkolbe/LitMath/commits/main/LitMathBenchmarks/ExpBenchmark.cs>
  - <https://github.com/matthewkolbe/LitMath/commits/main/README.md>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/README.md>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMathBenchmarks/ExpBenchmark.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMathBenchmarks/LogBenchmark.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMathBenchmarks/Program.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMathBenchmarks/LitMathBenchmarks.csproj>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMath/LitMath.csproj>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/e90aa47/README.md>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/55c178e/README.md>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/3d4c302/README.md>
- **Sources the enricher read:**
  - <https://github.com/matthewkolbe/LitMath>
  - <https://github.com/matthewkolbe/LitMath/commits/main>
  - <https://github.com/matthewkolbe/LitMath/commit/a670a81>
  - <https://github.com/matthewkolbe/LitMath/tree/main/LitMath>
  - <https://github.com/matthewkolbe/LitMath/tree/main/LitMathTests>
  - <https://github.com/matthewkolbe/LitMath/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/README.md>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMath/LitMath.csproj>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMath/Exp.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMath/Log.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMath/Constants.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMath/Utilities.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMath/Basics.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMath/Trig.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMath/Roots.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMath/NormDist.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMath/Polynomial.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMathBenchmarks/ExpBenchmark.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMathBenchmarks/LogBenchmark.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMathBenchmarks/Program.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMathBenchmarks/LitMathBenchmarks.csproj>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMathTests/ExpTest.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMathTests/LogTest.cs>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/LitMathTests/LitMathTests.csproj>
  - <https://api.nuget.org/v3-flatcontainer/kolbe.litmath/index.json>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/matthewkolbe/litmath`) · [data/wave13/enrich/raw/github_com_matthewkolbe_litmath.json](../../../data/wave13/enrich/raw/github_com_matthewkolbe_litmath.json) (enrichment confidence 0.75)

</details>
