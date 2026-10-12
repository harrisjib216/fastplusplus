# SimpleSIMD

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🔴 abandoned

> C# .NET 7 generic Vector&lt;T&gt; span helpers (Sum, Min/Max, Dot, elementwise); about 6x a naive int loop.

| | |
|---|---|
| **Beats** | naive scalar loop over int[] (Sum), BenchmarkDotNet 'Naive' row |
| **Claimed result** | README BenchmarkDotNet table: length 10000 SIMD 585.275 ns vs Naive 3,938.198 ns (ratio 0.15, about 6.7x, derived from page data); length 1000 66.018 ns vs 388.244 ns (ratio 0.17); length 100000 7,325.734 ns vs 40,283.073 ns (ratio 0.19); length 10 3.556 ns vs 5.357 ns (0.66). |
| **Workload** | Sum over an int[] of 10 to 100000 elements using System.Numerics.Vector&lt;T&gt; based helpers versus a plain loop, plus a value-delegate versus Func benchmark. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-10510U 1.80GHz (4 cores, 8 logical), Windows 11 |
| **Compiler and flags** | BenchmarkDotNet v0.13.2, .NET SDK 7.0.100, .NET 7.0.0 X64 RyuJIT AVX2, DefaultJob |
| **Adoption** | 93 stars |
| **Last commit** | 2022-11-19 |
| **Links** | [repository](https://github.com/giladfrid009/SimpleSIMD) · [benchmark](https://github.com/giladfrid009/SimpleSIMD) |

## Verdict

The author's BenchmarkDotNet 0.13.2 run on .NET 7.0.0 (RyuJIT AVX2, Intel i7-10510U, Windows 11) timed SimdOps.Sum over an int[] at 585 ns against 3,938 ns for a naive scalar loop at 10,000 elements (about 6.7x), 5-6.7x from 100 to 100,000 elements and 1.5x at 10. Only Sum on int was measured, the benchmark project is not public, and neither LINQ nor TensorPrimitives was compared.

## Use it when

- .NET 7 or 8 code that needs one generic (INumber&lt;T&gt;) API for span reductions and elementwise arithmetic across all primitive numeric types without hand-writing Vector&lt;T&gt; loops.
- Integer or float arrays of roughly 100 elements and up: the README shows 5-6.7x over a naive int loop from 100 to 100,000 elements (only about 1.5x at 10).
- Custom per-element kernels where you can supply both a Vector&lt;T&gt; and a scalar version as structs (for example Sum of a transformed value, IndexOf with a predicate).
- As a small, readable MIT template for Vector&lt;T&gt; loops to copy into your own code.

## Skip it when

- .NET 9 and later: System.Numerics.Tensors.TensorPrimitives ships vectorized Sum/Max/Min and elementwise ops generic over INumber&lt;T&gt;, and the LinqFaster README says .NET 9 moved most such optimizations into LINQ; SimpleSIMD has no numbers against either.
- Code that relies on LINQ semantics: Sum returns T and wraps on overflow, Average&lt;int&gt; is an integer division of that wrapped sum, and Min/Max of an empty span return a sentinel instead of throwing.
- Floating-point reductions that must be bit-reproducible with a sequential loop: the vector accumulator reorders additions.
- Select or Concat with an output type whose Vector&lt;TRes&gt;.Count differs from Vector&lt;T&gt;.Count (see gotchas: out-of-bounds write or unwritten results).
- Projects that need a maintained package: last commit 2022-11-19, NuGet 4.6.0 targets net7.0 only; no explicit Vector128/256/512 or hardware-intrinsic paths, so AVX-512-specific code gains nothing extra.

## How it is fast

Each method reinterprets the span as a run of System.Numerics.Vector&lt;T&gt; with MemoryMarshal.GetReference and Unsafe.As (no bounds checks), processes whole vectors (8 int lanes on an AVX2 host), then finishes with a scalar tail; reductions keep one vector accumulator and reduce it at the end with Vector.Dot(v, One). The 'value delegate' pattern (struct type parameters constrained to IFunc) lets RyuJIT specialize and inline the user's kernel; the README's own table shows the Func-delegate overloads 2.4-4.5x slower. The measured gain comes from 8-lane AVX2 Vector&lt;int&gt; against a scalar loop that .NET 7 RyuJIT does not auto-vectorize.

## Compared with alternatives

Pick it over LinqFaster when you are on .NET 7 and want one generic INumber&lt;T&gt; API with custom struct kernels rather than LINQ-shaped helpers; pick LitMath instead for vectorized Exp/Log/Sin, which SimpleSIMD lacks (Sqrt is its only math function). C++ users should look at EVE or the Vector Class Library; SimpleSIMD is C# only.

## Integration

| | |
|---|---|
| **Form** | NuGet package (SimpleSIMD 4.6.0) or source-drop (C# class library plus a Roslyn source generator project) |
| **Dependencies** | System.Runtime.Experimental &gt;= 6.0.2 (declared NuGet dependency); the Generator project uses Microsoft.CodeAnalysis.CSharp 4.4.0 at build time |
| **Minimum toolchain** | .NET 7 (net7.0 target), C# 11; Generator targets netstandard2.0 |
| **Platforms** | any .NET 7 runtime; the vector path runs only when Vector.IsHardwareAccelerated is true, otherwise the scalar loop runs |
| **Thread safety** | not documented; methods are static and keep no shared state |
| **Drop-in for the baseline** | partial — one call replaces a hand-written loop over T[]/Span&lt;T&gt;, but it is not LINQ: eager, span-only, wrapping integer Sum and integer Average |

## Gotchas

- Memory-safety bug in Select&lt;T,TRes&gt; and Concat&lt;T,TRes&gt;: the loop count is span.Length / Vector&lt;T&gt;.Count but each iteration stores a whole Vector&lt;TRes&gt; at Offset(i). Commit 2b7bd56 (2022-11-16, shipped in 4.6.0) removed the check that threw when Vector&lt;TRes&gt;.Count != Vector&lt;T&gt;.Count, so a narrower TRes (int to short or byte) writes past the end of the result span through Unsafe.As, and a wider TRes (int to long or double) leaves part of the result unwritten. The tests only call Select&lt;int,int&gt; and Concat&lt;int,int&gt;.
- Max and Min start from T.MinValue and T.MaxValue, so a float span of all -Infinity returns float.MinValue from Max, an empty span returns the sentinel, and NaN handling differs between the vector loop (Vector.Max/Min) and the scalar tail (T.Max/Min).
- Each custom kernel needs two structs that must compute the same function (vector and scalar); a mismatch silently gives results that depend on the span length. The generated Func overloads are 2.4-4.5x slower than the struct versions (README ValueDelegate table).
- Reductions use a single vector accumulator and the Tests project has no reduction tests (only Comparison.cs and Elementwise.cs); the README benchmark source is not in the repo.

## Known shortcomings

- No benchmark code in the repo (solution holds only SimpleSIMD, Generator and xunit Tests); the baseline is a naive int loop, not LINQ, and the ValueDelegate table compares the library against itself; .NET 9 LINQ has since absorbed such optimisations. C#, not callable from C++. Abandoned 2022-11-19.
- Enricher: memory-safety bug: commit 2b7bd56 (2022-11-16, NuGet 4.6.0) removed the check that Vector&lt;TRes&gt;.Count equals Vector&lt;T&gt;.Count in Select and Concat while the loop count still comes from Vector&lt;T&gt;.Count, so a narrower TRes writes past the result span through Unsafe.As and a wider TRes leaves results unwritten (tests cover &lt;int,int&gt; only); Sum wraps on overflow and Average&lt;int&gt; integer-divides the wrapped sum; Max/Min start from T.MinValue/T.MaxValue so an all -Infinity span gives float.MinValue; no reduction tests and no benchmark source; superseded by TensorPrimitives on .NET 9+.

## Caveats and trade-offs

The benchmark source is not public: SimpleSIMD.sln contains only SimpleSIMD, Generator and Tests, and Tests.csproj is an xunit unit-test project with no BenchmarkDotNet reference, so only the README table can be checked. Only Sum over int[] is benchmarked, against a hand-written scalar loop rather than LINQ Enumerable.Sum. The gain (about 6.7x at 10,000 elements) comes from 8-lane AVX2 Vector&lt;int&gt; against a loop that .NET 7 RyuJIT does not auto-vectorize. The second README table (ValueDelegate vs Delegate) compares the library against itself, with both paths SIMD-accelerated, not against an incumbent. Integer Sum wraps on overflow in both paths. The LinqFaster README states that as of .NET 9 most such optimizations are in the native LINQ library, so the advantage over current runtimes is unmeasured. Last commit 2022-11-19.

Uses portable Vector&lt;T&gt; (width follows the CPU); value delegates (struct generics) are needed to keep lambdas inlined; targets .NET 7 generic math.

## Maintenance

Abandoned since 2022-11-19 (NuGet 4.6.0 for net7.0 only); MIT and small enough to vendor, but restore the Vector&lt;TRes&gt;.Count check in Select/Concat before using mixed-type kernels, and prefer TensorPrimitives on .NET 9+.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'Performance Benefits' BenchmarkDotNet table compares SIMD Sum against a Naive loop over int[] with runtime, OS and CPU (i7-10510U) stated, but the benchmark source is not in the repo: SimpleSIMD.sln holds only the SimpleSIMD, Generator and Tests projects, and Tests.csproj references xunit, not BenchmarkDotNet. First-party numbers without public benchmark code are tier C.
- **Verifier notes:** README numbers match the record exactly (10: 3.556 vs 5.357 ns; 1000: 66.018 vs 388.244 ns; 10000: 585.275 vs 3,938.198 ns; 100000: 7,325.734 vs 40,283.073 ns). The Sum implementation in SimpleSIMD/Reduction/Sum.cs is a correct vector accumulation plus scalar tail. The entry is C#, not C++ and not callable from C++: shortcomings are no public benchmark code, a naive-loop baseline only, and abandonment (MIT, 93 stars, 174 commits).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-60 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/giladfrid009/SimpleSIMD>
  - <https://github.com/giladfrid009/SimpleSIMD/commits>
  - <https://github.com/giladfrid009/SimpleSIMD/tree/master/Tests>
  - <https://github.com/giladfrid009/SimpleSIMD/tree/master/SimpleSIMD>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/README.md>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/Tests/Tests.csproj>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD.sln>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Reduction/Sum.cs>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/giladfrid009/SimpleSIMD>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/README.md>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD.sln>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/SimpleSIMD.csproj>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/SimdOps.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Delegates.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Reduction/Sum.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Reduction/Average.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Reduction/Max.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Reduction/Min.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Reduction/Dot.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/General/IndexOf.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/General/All.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Elementwise/Add.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Elementwise/Divide.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Elementwise/Sqrt.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Elementwise/Select.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Elementwise/Concat.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/SimpleSIMD/Comparison/Equal.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/Generator/Generator.csproj>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/Tests/Tests.csproj>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/Tests/Elementwise.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/Tests/Comparison.cs>
  - <https://raw.githubusercontent.com/giladfrid009/SimpleSIMD/HEAD/LICENSE>
  - <https://github.com/giladfrid009/SimpleSIMD/tree/master/SimpleSIMD>
  - <https://github.com/giladfrid009/SimpleSIMD/tree/master/Tests>
  - <https://github.com/giladfrid009/SimpleSIMD/issues?q=is%3Aissue>
  - <https://github.com/giladfrid009/SimpleSIMD/commits/master>
  - <https://github.com/giladfrid009/SimpleSIMD/commit/2b7bd56>
  - <https://api.nuget.org/v3/registration5-semver1/simplesimd/index.json>
  - <https://raw.githubusercontent.com/jackmott/LinqFaster/HEAD/README.md>
  - <https://raw.githubusercontent.com/matthewkolbe/LitMath/HEAD/README.md>
  - WebSearch snippet: '.NET 9 TensorPrimitives generic INumber Sum Max Dot System.Numerics.Tensors vectorized' (dotnet/runtime PR 91596, source.dot.net TensorPrimitives references)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/giladfrid009/simplesimd`) · [data/wave13/enrich/raw/github_com_giladfrid009_simplesimd.json](../../../data/wave13/enrich/raw/github_com_giladfrid009_simplesimd.json) (enrichment confidence 0.78)

</details>
