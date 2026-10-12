# Culumi PRNG (SIMD CLMUL-based 128-bit-per-step generator)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (SSE4/PCLMUL/FMA) and C#` · `CC0-1.0` · 🔴 abandoned

> SIMD PRNG returning 128 bits per call via carry-less multiply; author's table puts it ahead of xoshiro256\*\*, PCG64DXSM, MT19937.

| | |
|---|---|
| **Beats** | MT19937_32 (also SFMT19937, PCG64DXSM, xoshiro256\*\*, xoroshiro128++, SFC64 listed in the same table) |
| **Claimed result** | ns/KiB: Culumi 58.68, Shioi 81.97, SplitMix 91.80, Seiran 97.26, SFC64 97.80, xoroshiro128++ 113.53, xoshiro256\*\* 137.79, PCG64DXSM 308.30, MT19937_32 547.58, SFMT19937 953.13. That is about 9.3x faster than MT19937_32, 5.3x faster than PCG64DXSM and 2.3x faster than xoshiro256\*\* (derived from page data). Against .NET System.Random: Next() 0.9371 ns versus 1.6193 ns (1.73x). |
| **Workload** | Table of time in ns per KiB of output for common PRNGs, fastest to slowest; separate BenchmarkDotNet table of Culumi versus System.Random methods. |
| **Metric** | throughput |
| **Hardware** | 12th Gen Intel Core i7-12700F (stated for the .NET 8 BenchmarkDotNet table on Windows 11; the page does not say which environment produced the ns/KiB table) |
| **Adoption** | 4 stars |
| **Last commit** | 2023-05-25 |
| **Links** | [repository](https://github.com/andanteyk/prng-culumi) · [benchmark](https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/README.md) |

## Verdict

The README's comparison table lists Culumi at 58.68 ns per KiB against xoshiro256\*\* 137.79, PCG64DXSM 308.30 and MT19937_32 547.58 (about 2.3x, 5.3x and 9.3x, derived from page data). It names no language, compiler, flags or CPU and ships no harness; its baseline links point at .NET, Java and Unity generators, SFMT comes out slower than MT, and Shishua is listed at 220.97 ns/KiB, far below SHISHUA's own figures, so the baselines look like scalar managed ports, not std::mt19937 or SIMD code. A separate BenchmarkDotNet run (.NET 8 preview, RyuJIT AVX2, i7-12700F, Windows 11) puts Culumi's Next() at 0.937 ns against System.Random's 1.619 ns (1.73x); its benchmark code is not published either.

## Use it when

- .NET 7/8 code that wants a faster, richer System.Random replacement: the author's BenchmarkDotNet table (i7-12700F) has Next() at 0.94 ns vs 1.62 ns, NextDouble() 1.08 vs 1.85 ns and Shuffle(char[16]) 19 vs 55 ns.
- x86-64 C/C++ code that consumes random bits 128 at a time (bulk byte fills, SIMD Monte Carlo with 4x float or 2x double lanes) and wants a 32-byte state.
- Parallel simulations that need many non-overlapping streams via constant-time jumps (2^128 streams of length 2^128 per the README).
- Projects that want public-domain (CC0) code they can paste in without license tracking.

## Skip it when

- Anything security-sensitive: the README says the internal state was recovered from three consecutive 128-bit outputs with the Z3 solver in a few hours.
- Portable C/C++: the C version uses x86 intrinsics and needs SSE4.1, PCLMUL and FMA; there is no ARM or scalar path in C (only the C# version has ARM and software fallbacks).
- When you need a std::-compatible engine, a maintained library or independent numbers: 4 commits, all on 2023-05-25, no benchmark harness in the repo, and the ns/KiB table states no language, compiler or CPU.
- If you just need fast scalar 64-bit outputs: the same table has SFC64 at 97.80 and xoroshiro128++ at 113.53 ns/KiB against Culumi's 58.68, a gap small enough that a portable, better-studied generator may be the better trade.

## How it is fast

The state update is GF(2)-linear (an LFSR-type step): one PCLMULQDQ carry-less multiply of the low 64 bits by a constant, two XORs and a 64-bit lane swap, which is what makes the 2^256-1 period provable. The output scrambler is nonlinear and also cheap: a 64-bit-lane add of the two state halves, a pshufb byte shuffle, and another add. So each call yields 128 bits from a handful of SSE instructions. The helpers use the whole vector: four 32-bit or two 64-bit bounded integers per call (multiply-high with a rejection/carry fix-up, no division) and 4x float or 2x double conversions with FMA.

## Compared with alternatives

Pick Culumi over the same author's scalar Shioi and Seiran when you can rely on x86 PCLMUL (or .NET) and consume 128-bit vectors. For raw bulk throughput SHISHUA is the stronger sibling (its own README claims 52.93 GB/s, about 19 ns/KiB derived, against Culumi's 58.68 ns/KiB), and SIMD xoshiro ports such as simdrng suit you better if you want a well-analysed generator with C++ engine semantics.

## Integration

| | |
|---|---|
| **Form** | source-drop (one C file with an embedded test main(); one C# file) |
| **Dependencies** | none (C: x86intrin.h or intrin.h, seeds from /dev/urandom or rand_s; C#: .NET base library only) |
| **Minimum toolchain** | C: gcc/clang/MSVC with -msse4 -mpclmul -mfma (source comment); C#: README says .NET 7, the shipped Culumi.csproj targets net8.0 |
| **Platforms** | C: x86-64 with SSE4.1 + PCLMULQDQ + FMA; C#: any .NET 7+ runtime, fast on x86 PCLMUL and ARM AES (PMULL), with a slow software carry-less multiply fallback elsewhere |
| **Thread safety** | not documented; the state is a plain mutable struct/class with no locking, so use one instance per thread (jump() or C# Split() to separate streams) |
| **Drop-in for the baseline** | partial — the C# class mirrors System.Random method names (Next, NextDouble, NextBytes, Shuffle, GetItems) but does not derive from System.Random; the C code has no std::mt19937-style engine interface |

## Gotchas

- Correctness bug in the C port (found by reading the code; not run): the retry path of nextDouble2 and nextFloat4, taken when min + u\*(max-min) rounds up to max, passes _mm_andnot_pd/_ps arguments in the wrong order (Intel's andnot(a,b) is \~a & b, while the C# original's Vector128.AndNot(a,b) is a & \~b), and nextDouble2's retry multiplies by min2 where max2 belongs. A lane that already succeeded is zeroed and the retried lane gets garbage bits. The retry is rare for ranges near zero but common for narrow ranges at large magnitude (about 6% of draws per lane for [1e15, 1e15+1), derived). The C# version is correct.
- nextBytes stores through an __m128i\* cast of the caller's byte buffer, which compilers may emit as aligned stores, so pass a 16-byte-aligned buffer.
- In C, next() is declared non-static 'inline' (DLLEXPORT inline), which under C99 inline rules can fail to link at -O0, and the exported names (init, next, prev, jump64) are generic enough to collide; rename or make them static inline when vendoring.
- initState() calls exit(-1) on an all-zero seed, and init() falls back to time()/clock() seeding, which the source comment says lacks entropy, if /dev/urandom cannot be read.

## Known shortcomings

- ns/KiB table likely used managed non-SIMD baselines (SFMT slower than MT).
- Correctness bug in the C port (code reading, not run): the nextDouble2/nextFloat4 retry path passes _mm_andnot arguments in the wrong order and nextDouble2 uses min2 where max2 belongs, so the valid lane is zeroed and the retried lane gets garbage (rare near zero, \~6% of draws per lane for [1e15, 1e15+1), derived). C# version is correct. README rates SHISHUA at 220.97 ns/KiB, far below SHISHUA's own \~19 ns/KiB, so the baselines look like scalar/managed ports. c/culumi.c holds the full library plus a test main().

## Caveats and trade-offs

First-party README. The ns/KiB table gives no compiler, flags, hardware or benchmark code. Its links (xoshiro256\*\* to .NET System.Random docs, xoroshiro128++ to Java docs) and SFMT19937 coming out slower than MT19937 suggest managed, non-SIMD implementations of the baselines. So the 9.3x versus MT19937 does not describe std::mt19937 or a SIMD SFMT. The System.Random table names .NET 8 preview on an i7-12700F, but its BenchmarkDotNet harness is not published. CC0 grants no patent rights (no patent grant). Not cryptographically secure: the README says the state was recovered from three outputs with Z3. Needs SSE4/PCLMUL/FMA in C. The latest commit (2023-05-25) is more than 3 years old.

Needs x86 SSE4/PCLMUL/FMA for the C version; period 2^256-1 with jump functions of 2^128 and 2^192; 32 bytes of state; not cryptographically secure (state recoverable from three outputs with Z3 in a few hours per the README).

## Maintenance

Abandoned (4 commits, all on 2023-05-25; 4 stars, no issues filed) but CC0 and one file per language, so it is easy to vendor; prefer the C# file, or fix the C retry bug before using the C range helpers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README ns/KiB table lists Culumi at 58.68 against MT19937_32 547.58, PCG64DXSM 308.30, xoshiro256\*\* 137.79 and others, but gives no harness, language, compiler or hardware for it. The BenchmarkDotNet table against System.Random states .NET 8 preview, RyuJIT AVX2 and an i7-12700F. The BenchmarkDotNet code is not in the repo, though (csharp/Program.cs is a 17-line test runner, and c/culumi.c holds only test vectors), so both are first-party C.
- **Verifier notes:** Every number in the record matches the README. The table also has Lehmer128, Shishua and xorshift rows, all slower than Culumi. Four commits, all on 2023-05-25; 4 stars.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/README.md>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/csharp/Program.cs>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/csharp/Culumi.csproj>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/csharp/README-csharp.md>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/c/culumi.c>
  - <https://github.com/andanteyk/prng-culumi>
  - <https://github.com/andanteyk/prng-culumi/tree/main/csharp>
  - <https://github.com/andanteyk/prng-culumi/tree/main/c>
  - <https://github.com/andanteyk/prng-culumi/commits/main>
- **Sources the enricher read:**
  - <https://github.com/andanteyk/prng-culumi>
  - <https://github.com/andanteyk/prng-culumi/tree/main/csharp>
  - <https://github.com/andanteyk/prng-culumi/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/README.md>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/c/culumi.c>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/csharp/Culumi.cs>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/csharp/Program.cs>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/csharp/Culumi.csproj>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/csharp/README-csharp.md>
  - <https://github.com/andanteyk?tab=repositories&q=prng>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/andanteyk/prng-culumi`) · [data/wave8/enrich/raw/github_com_andanteyk_prng_culumi.json](../../../data/wave8/enrich/raw/github_com_andanteyk_prng_culumi.json) (enrichment confidence 0.75)

</details>
