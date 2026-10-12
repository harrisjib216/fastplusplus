# recip_rsqrt_benchmark (fast vectorized reciprocal and rsqrt)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🔴 abandoned

> SSE recipes for approximate 1/x and 1/sqrt(x) (rcpps/rsqrtps, optional Newton-Raphson) that beat divps and sqrtps+divps throughput 2-13x.

| | |
|---|---|
| **Beats** | the repo's own 'ieee' variants in routines_sse.h: _mm_div_ps(1, x) and _mm_div_ps(1, _mm_sqrt_ps(x)) (and the _pd forms), i.e. the divps/sqrtps instructions a compiler emits for 1.0f/x and 1.0f/sqrtf(x) |
| **Claimed result** | README sample results (float4): recip ieee 7.30 cycles vs fast 1.13 (about 6.5x, max error 3.0e-4) vs nr1 3.69 (about 2.0x, error 1.47e-7); rsqrt ieee 14.46 vs fast 1.12 (about 12.9x, error 3.3e-4) vs nr1 5.52 (about 2.6x, error 3.1e-7); double2 rsqrt ieee 28.21 vs fast 3.38 (about 8.3x) (ratios derived from page data). |
| **Workload** | Vectorized 1/x and 1/sqrt(x) on __m128 (4 floats) or __m128d (2 doubles; the fast double variants convert to float and use rcpps/rsqrtps) over about 33.5M float and 16.8M double test values (an exhaustive 1.0 to 2.0 range plus exp2 of uniform(-20, 20)); each value is passed through the function 4 times in 4 interleaved streams; rdtsc cycles per call and maximal relative error against the div/sqrt variant. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-3770 (Ivy Bridge) |
| **Compiler and flags** | MSVC 2013 C++ compiler, x64 mode (README); optimisation flags not stated and no project or build file in the repo; later commits fixed compilation on GCC (2015) and MSVC 2017 (2018) |
| **Adoption** | 11 stars; tied to a Stack Overflow answer |
| **Last commit** | 2018-12-05 |
| **Links** | [repository](https://github.com/stgatilov/recip_rsqrt_benchmark) · [benchmark](https://raw.githubusercontent.com/stgatilov/recip_rsqrt_benchmark/HEAD/README.md) |

## Verdict

On an Intel Core i7-3770 (Ivy Bridge) built with MSVC 2013 x64 (flags not stated), the README's single run measures rcpps at 1.13 TSC ticks per 4-float call versus 7.30 for divps (about 6.5x) and rsqrtps at 1.12 versus 14.46 for sqrtps+divps (about 12.9x), with max relative error about 3e-4. One Newton-Raphson step gives 3.69 and 5.52 ticks (about 2.0x and 2.6x) at 1.5e-7 and 3.1e-7. Double rows go through float: rsqrt estimate 3.38 versus 28.21 ticks (about 8.3x), and the series variants recip r5 and rsqrt r5 reach 2.2e-16 and 3.2e-16 error at about 1.35x and 2.1x (ratios derived from page data). The baseline is the repo's own exact SSE variant, not a library.

## Use it when

- Float SIMD inner loops (vector normalisation, lighting, physics, softmax-style scaling) bound by divps or sqrtps throughput, where about 3e-4 (raw estimate) or about 1.5e-7 to 3.1e-7 (one Newton-Raphson step) relative error is acceptable
- Older x86 cores of the Ivy Bridge era, where the sample run shows 6.5x (recip) and 12.9x (rsqrt) for the raw estimate and 2.0x and 2.6x with one refinement step
- Double 1/x or 1/sqrt(x) on inputs that stay well inside float range (about 1.2e-38 to 3.4e38), where recip_double2_r5 (2.2e-16, 10.51 vs 14.17 ticks, about 1.35x) or rsqrt_double2_r5 (3.2e-16, 13.51 vs 28.21 ticks, about 2.1x) gives near-full precision faster (derived from page data)
- As a reference table of precision versus cost before you write your own estimate-plus-refinement code or choose a math library

## Skip it when

- You need correctly rounded IEEE results or reproducible bit-exact output; every non-ieee variant is approximate
- Inputs can be 0, +inf, denormal or outside the tested 2^-20 to 2^20 range, or are doubles beyond float range: the refined variants return NaN or 0 there (see gotchas)
- Current Intel and AMD cores: dividers and square-root units are much faster than on Ivy Bridge (general knowledge, not measured here), and a search snippet of LLVM review D5658 says LLVM limited rsqrt estimates to AMD btver2 because Intel Core sqrt/divide units were 'just too fast' for estimate plus refinement to pay off; re-measure first
- Your compiler can already do this: GCC -mrecip (and -ffast-math for 1.0f/sqrtf) emits rcpps/rsqrtps with one Newton-Raphson step when -funsafe-math-optimizations, -ffinite-math-only and -fno-trapping-math are on (GCC documentation via search snippet)
- You need AVX, AVX-512 or Arm NEON versions or a licensed library: only 128-bit SSE code is here and the repo has no licence file

## How it is fast

The fast rows use the hardware estimate instructions rcpps and rsqrtps (about 12-bit accuracy, max error about 3e-4 in the sample run) instead of the slow divider and square-root unit. The nr1/nr2 rows add one or two Newton-Raphson steps (x(2 - ax) for 1/x, x(3 - ax^2)/2 for 1/sqrt(x)). The r3-r5 double rows evaluate a truncated series x\*poly(r) with r = 1 - ax (or 1 - ax^2), so one correction reaches 2.2e-16 to 3.2e-16 error. Double variants convert to float, take the float estimate and refine in double precision.

## Compared with alternatives

Pick this over math_intrinsics, corvus or LitMath only when the hot spot is plain 1/x or 1/sqrt(x) on SSE registers and you want to choose an exact precision/cost point and hand-copy a few lines; those siblings are maintained vector-math function sets (trig, exp, log) with stated libc or framework baselines, and this repo is a licence-less reference.

## Integration

| | |
|---|---|
| **Form** | source-drop (copy individual static inline functions from routines_sse.h; reference only, no licence) |
| **Dependencies** | none beyond SSE/SSE2 intrinsics headers; the harness also needs aligned_allocator.h (in the repo) and _mm_malloc |
| **Minimum toolchain** | C++11 for the harness (enum class, &lt;random&gt;, variadic templates); sample results from MSVC 2013 x64; the routines themselves are plain SSE2 intrinsics |
| **Platforms** | x86 and x86-64 with SSE2; no AVX, AVX-512, NEON or scalar fallback |
| **Thread safety** | the routines are stateless pure functions of their argument (from code reading); thread safety is not documented |
| **Drop-in for the baseline** | partial — same __m128/__m128d in, out signature as the divps and sqrtps+divps forms, but results are approximate and special values (0, inf, out-of-float-range doubles) differ |

## Gotchas

- Special values are not handled and never tested: the harness only feeds positive finite values (all floats in [1, 2] plus exp2 of uniform(-20, 20)). From code reading, recip_float4_nr1(+inf) computes inf\*0 and returns NaN instead of 0; rsqrt_float4_nr1(0) computes 0\*inf\*inf and returns NaN instead of +inf. The double variants round to float first, so a double above about 3.4e38 becomes inf and recip_double2_nr1 returns 0 (true value about 1e-300 for x = 1e300). A double below about 1.2e-38 becomes 0 or a float denormal, which rcpps treats as 0, so the refined result is NaN.
- Harness flaw in the precision column: the 'exhaustive' double range is enum_all_floats(1.0, 1.0 + DBL_EPSILON \* (1&lt;&lt;23)), that is [1, 1 + 2^-29]. All of those 8.4M doubles round to the same float 1.0 before rcpps or rsqrtps, so the double max-error figures rest on the 16.8M random exp2 samples only. For float rsqrt, the exhaustive sweep covers [1, 2] only and the [2, 4) half of the mantissa-exponent space is sampled randomly. The 'ieee' rsqrt reference is div after sqrt (two roundings), so the 3.2e-16 to 5e-14 rsqrt figures are measured against a reference that is itself not correctly rounded.
- Timing is one unrepeated rdtsc pass (TSC reference ticks, not core cycles) over about 168 MB of floats and about 201 MB of doubles (sizes derived from main.cpp), far larger than cache. The 1.1-tick fast float rows move about 3.5 bytes per tick, about 12 GB/s at a nominal 3.4 GHz TSC (derived), so they may be partly memory-bound; that would understate, not inflate, the fast-row speedups. Each value goes through 4 chained calls in 4 interleaved streams, so the figure is a throughput measure, not latency as the catalog metric says.
- Build: the 2018 'Fixed compilation on MSVC2017' commit (505a8fc) added an unconditional #include &lt;intrin.h&gt;, an MSVC/MinGW header, so main.cpp as checked in will not compile with GCC or Clang on Linux (from code reading, not built). There is no build file and the optimisation flags are not stated. test_values_double is declared as vector&lt;double, aligned_allocator&lt;float, ...&gt;&gt;, a value_type mismatch that only works through the allocator's rebind.

## Known shortcomings

- No licence (reference); 2015 Ivy Bridge run with MSVC 2013 and flags unstated; approximate results (about 3e-4 error); the metric is throughput, not latency.
- Harness flaw: the 'exhaustive' double range is only [1, 1 + 2^-29], and all 8.4M of those doubles round to the float 1.0, so the double max-error column rests on the 16.8M random samples only. Special values are untested: the NR variants return NaN for 0 and +inf, and the double variants return 0 or NaN outside the float range. Since the 2018 commit 505a8fc an unconditional &lt;intrin.h&gt; breaks the Linux GCC/Clang build (code reading, not built). The arrays (about 168 and 201 MB) exceed cache, so the fast rows may be memory-bound and the speedups understated, not inflated; the metric is throughput, not latency.

## Caveats and trade-offs

No licence file, so reference only. Results are from July 2015 on Ivy Bridge with MSVC 2013; newer CPUs have much faster divps and sqrtps (general knowledge, not from the page), so the gap is likely smaller today. The README describes the metric as throughput (cycles per call), not latency; the harness chains 4 calls per stream over 4 independent streams, so it mixes latency and throughput, and rdtsc counts reference cycles rather than core cycles. The fast variants trade accuracy (max relative error about 3e-4 without refinement, about 1.5e-7 to 3e-7 with one Newton-Raphson step), so they are not drop-in replacements for exact division; the 'ieee' rsqrt reference is div plus sqrt (two roundings), not a correctly rounded rsqrt. The baseline is the authors' own exact variant in the same harness. Tied to a Stack Overflow question (31555260). [retier] No licence file, so reference only. Results are from July 2015 on Ivy Bridge with MSVC 2013 (flags not stated, no build file); newer CPUs have much faster divps and sqrtps, so the gap is likely smaller today. Metric: one unrepeated rdtsc pass (TSC reference ticks, not core cycles) over about 168 MB of floats and 201 MB of doubles, far larger than cache, with each value going through 4 chained calls in 4 interleaved streams, so it mixes latency and throughput; the 1.1-tick fast float rows move about 12 GB/s (derived), so they may be partly memory-bound, which would understate rather than inflate the fast-row speedups. Precision column flaw: the 'exhaustive' double range is enum_all_floats(1.0, 1.0 + DBL_EPSILON \* (1 &lt;&lt; 23)), i.e. [1, 1 + 2^-29], and all 8.4M of those doubles round to the same float 1.0 before rcpps or rsqrtps, so the double max-error figures rest on the 16.8M random exp2 samples only; for float rsqrt the exhaustive sweep covers [1, 2] only. Special values are never tested (the harness feeds only positive finite values): recip_float4_nr1(+inf) returns NaN instead of 0, rsqrt_float4_nr1(0) returns NaN instead of +inf, and the double variants round to float first so inputs above about 3.4e38 become inf (recip returns 0). The fast variants trade accuracy (max relative error about 3e-4 without refinement, about 1.5e-7 to 3e-7 with one Newton-Raphson step). Build: the 2018 commit 505a8fc added an unconditional #include &lt;intrin.h&gt;, so main.cpp as checked in will not compile with GCC or Clang on Linux (code reading, not built).

Approximate results (error trade-off listed per variant); SSE on x86 only; benchmark of approximate rcpps/rsqrtps tricks rather than a packaged library.

## Maintenance

Abandoned since 2018-12-05 (11 commits, 11 stars, no licence file), so reference only: read the five-line recipes and reimplement them, and re-measure on a current CPU before relying on the 2015 Ivy Bridge ratios.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README sample results with public benchmark code (main.cpp, routines_sse.h, rdtsc.h), compiler (MSVC 2013 x64) and CPU (Core i7-3770) stated, but no optimisation flags and no build file in the repo, so not A.
- **Verifier notes:** All claimed numbers appear in the README sample results and the ratios are correctly labelled as derived. The record's metric 'latency' should read 'throughput' per the README (metric is not a correctable field here). Main shortcomings: no licence, 2015 Ivy Bridge/MSVC 2013 data with flags unstated, and approximate results (about 12-bit accuracy for the fastest rows).
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-111 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/stgatilov/recip_rsqrt_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/stgatilov/recip_rsqrt_benchmark/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/stgatilov/recip_rsqrt_benchmark/HEAD/routines_sse.h>
  - <https://github.com/stgatilov/recip_rsqrt_benchmark>
  - <https://github.com/stgatilov/recip_rsqrt_benchmark/commits>
- **Sources the enricher read:**
  - <https://github.com/stgatilov/recip_rsqrt_benchmark>
  - <https://raw.githubusercontent.com/stgatilov/recip_rsqrt_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/stgatilov/recip_rsqrt_benchmark/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/stgatilov/recip_rsqrt_benchmark/HEAD/routines_sse.h>
  - <https://raw.githubusercontent.com/stgatilov/recip_rsqrt_benchmark/HEAD/rdtsc.h>
  - <https://raw.githubusercontent.com/stgatilov/recip_rsqrt_benchmark/HEAD/aligned_allocator.h>
  - <https://raw.githubusercontent.com/stgatilov/recip_rsqrt_benchmark/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/stgatilov/recip_rsqrt_benchmark/HEAD/LICENSE>
  - <https://github.com/stgatilov/recip_rsqrt_benchmark/commits>
  - <https://github.com/stgatilov/recip_rsqrt_benchmark/commit/505a8fc>
  - <https://github.com/stgatilov/recip_rsqrt_benchmark/commit/fdab51c>
  - WebSearch: "Fast vectorized rsqrt and reciprocal with SSE/AVX depending on precision" (snippets incl. https://reviews.llvm.org/D5658)
  - WebSearch: gcc -mrecip RCPPS RSQRTPS Newton-Raphson (snippets incl. https://gcc.gnu.org/pipermail/gcc/2016-July/221444.html and https://gcc.gnu.org/bugzilla/show_bug.cgi?id=55760)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/stgatilov/recip_rsqrt_benchmark`) · [data/wave13/enrich/raw/github_com_stgatilov_recip_rsqrt_benchmark.json](../../../data/wave13/enrich/raw/github_com_stgatilov_recip_rsqrt_benchmark.json) (enrichment confidence 0.8)

</details>
