# corvus

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Accuracy-first SIMD double-precision erf/lgamma/incomplete gamma-beta and sin/cos/exp batch kernels; sin/cos 3.2-5.6x faster than scalar vendor libm.

| | |
|---|---|
| **Beats** | scalar vendor libm called through std::cos/std::sin/std::exp/std::lgamma (UCRT on Windows, Apple libSystem on macOS); also compared against corvus's own element-at-a-time calls |
| **Claimed result** | docs/PERFORMANCE.md section 11.1 (n = 10^6, tier-asserted) and raw outputs in docs/bench-evidence: cos/sin 5.50x/5.58x vs UCRT on Zen 4 (1.6 ns/el), 4.87x/4.98x vs Apple x86 libm on Kaby Lake (4.4 ns/el), 3.27x/3.21x vs Apple arm64 libm on M1 (single gated run, 'reported, not published'). The trig gain is size dependent: at n &lt;= 10^4 it is 2.2x to 2.4x on Zen 4 and 2.7x to 3.0x at n = 1000 on Kaby, and at n = 1000 on M1 sin is 0.28x and cos 1.35x (raw evidence files). exp: 1.20x vs UCRT and 1.28x vs Apple arm64, but 0.65x (slower) vs Apple x86 libm on Kaby. erf: 6.33x vs UCRT at n = 10^6 (3.71x at n = 1000), 3.56x vs Apple x86 libm; erfc 3.12x to 9.34x vs UCRT by band, 1.27x to 3.46x vs Apple x86 libm. lgamma 1.5x to 5.2x vs UCRT but 0.2x to 0.93x vs Apple libm (Kaby and M1). log 0.64x, 0.27x, 0.21x and log1p 0.92x, 0.40x, 0.32x (slower than every libm, by design for correct rounding). Other families (gamma_p, beta, digamma, inverses, Bessel) are timed only against corvus called one element at a time ('upper bnd', 4-140x), not against any library, and those batching tables overstate today's gain by up to about 2.5x after the 2026-09-30 baseline change (#42). |
| **Workload** | Element throughput (ns per element) of SIMD-vectorised double-precision erf, lgamma, exp, log, log1p, cos, sin over n = 10^6 seeded inputs, median of repeated timings after warm-up, on a quiet machine gated at 5% ambient CPU. |
| **Metric** | throughput |
| **Hardware** | Zen 4: AMD Ryzen 7 7445HS (named in issues #37 and #43), Windows UCRT baseline; Kaby Lake x86 Mac (Apple x86 libm); Apple M1 (Apple arm64 libm, single gated run) |
| **Compiler and flags** | clang-cl Release via the windows-clang-cl CMake preset with Ninja (version not stated in PERFORMANCE.md; PLAN.md cites clang-cl 22.1.3 for a later 2026-09-30 build) on Zen 4; Apple Clang 15 Release ('release' preset, Ninja) on Kaby Lake; project-wide -ffp-contract=off (CORVUS_FP_FLAGS); harness tools/quiet_bench.ps1 / tools/quiet_bench.sh, bench sources tests/bench_\*.cpp, raw evidence under docs/bench-evidence/2026-08-30-zen4-quiet, 2026-08-30-kaby-quiet and 2026-08-31-m1-indicative |
| **Adoption** | 1 star; built on Highway for dispatch |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/OldCrow/corvus) · [benchmark](https://github.com/OldCrow/corvus/blob/HEAD/docs/PERFORMANCE.md) |

## Verdict

At n = 10^6 seeded doubles, median of 11 timed reps after a warm-up, corvus cos/sin ran 1.6 ns/el (5.50x/5.58x) against UCRT std::cos/std::sin on a Zen 4 Ryzen 7 (named in issues #37 and #43 as a Ryzen 7 7445HS) built with clang-cl Release at AVX3_ZEN4, 4.4 ns/el (4.87x/4.98x) against Apple's x86 libm on an i7-7820HQ with Apple Clang 15 at AVX2, and 3.27x/3.21x against Apple's arm64 libm on an M1 (single run). erf was 6.33x vs UCRT and 3.43-3.56x vs Apple x86 libm, while exp ranged 0.65-1.28x and log/log1p were slower than every libm; no SIMD peer such as SLEEF or Highway contrib math was timed.

## Use it when

- Large double arrays (10^5 elements and up) of sin/cos or erf/erfc where you also need 1-ULP results over the full double range: 5.5x vs UCRT on Zen 4 and about 4.9x vs Apple's x86 libm on Kaby Lake at n = 10^6.
- Vectorised statistical CDFs, quantiles and maximum-likelihood fits that need incomplete gamma/beta, their inverses, digamma/trigamma or Bessel I0/I1, which no vendor libm or basic SIMD math library provides.
- Windows builds (clang-cl with AVX-512) whose current baseline is UCRT, where lgamma also wins 1.5-5.2x by band.
- One binary that must pick SSE2 through AVX-512 or NEON at run time, with corvus::active_target() reporting the chosen tier.

## Skip it when

- You want faster log or log1p: they are 0.21-0.64x and 0.32-0.92x of every vendor libm measured (correctly rounded by design).
- lgamma or exp on macOS: Apple's libm beats corvus lgamma in every stable band (0.2-0.93x), and exp is 0.65x of Apple's x86 libm on Kaby Lake.
- Small batches on Apple M1: at n = 1000 every corvus row ran 3.5-4x slower per element than at n = 10^4 (cos 15.79 vs 4.01 ns, exp 18.62 vs 4.66 ns), giving sin 0.28x of the libm.
- Single precision, tan/pow/sqrt or broadcast arguments: double only, five elementary functions only, every span must be materialised to full length.
- Incomplete gamma/beta inverses in extreme parameter ranges until the open accuracy bugs are fixed (issues #47-#59, e.g. gamma_p_inv(0.1, 0.99) returns 7.9e106 in #48).

## How it is fast

Speed comes from evaluating a whole vector of lanes per instruction through Google Highway with runtime dispatch (SSE2 to AVX-512 AVX3_ZEN4, and NEON), branch-free region selection by masks, and corvus's own double-double exp/log cores rather than per-element libm calls. cos/sin use an exact-split quadrant reduction for |x| &lt;= 2^23 and a vectorised Payne-Hanek reduction beyond it. The extra double-double work is what makes log/log1p (correctly rounded) and lgamma slower than fast vendor libms, so the gain is lane amortisation minus accuracy cost.

## Compared with alternatives

Pick corvus over math_intrinsics or SIMD-math-prims when you need double precision with 1-ULP bounds over the full argument range rather than fast single-precision approximations, and over VCL or EVE when you need statistical special functions (erf, lgamma, incomplete gamma/beta, quantiles) with a published per-tier accuracy audit; for float throughput the approximate siblings are the better fit.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Google Highway 1.4+ (Apache-2.0; an installed copy is used if found, otherwise 1.4.0 is fetched at configure time with contrib enabled) |
| **Minimum toolchain** | C++20 (std::span in the public header), CMake 3.25+, MSVC 19.30+ (VS 2022) if using cl.exe; CI covers GCC on Linux, Apple Clang on macOS arm64 and MSVC on Windows |
| **Platforms** | x86-64 (SSE2, SSSE3, SSE4, AVX2, AVX-512 tiers) and aarch64 NEON with runtime dispatch; MSVC builds cap at AVX2 (use clang-cl for AVX-512); mingw-w64 GCC 16.1 is unsafe at AVX2 and above |
| **Thread safety** | Stateless and thread-safe; no allocation, every public function noexcept, dispatch pointer resolved on first call (header contract). |
| **Drop-in for the baseline** | partial: covers std::erf/erfc/lgamma/exp/log/log1p/cos/sin only, as batch span calls replacing a loop of std:: calls; no per-element overloads, double only, and results differ from libm in the last bit |

## Gotchas

- Harness size effect: the scalar libm's own cost per element rises with n (Zen 4 UCRT cos 3.92 ns at n = 10^4 vs 8.86 ns at 10^5; Kaby Apple cos 13.47 ns at 10^3 vs 21.24 ns at 10^4) at about 2 GB/s of traffic, far below memory bandwidth, so PERFORMANCE.md's 'leaves cache' explanation is doubtful; the bench re-times one seeded array 11-51 times, which can let the branch predictor learn the libm's data-dependent branches at small n (my inference, not measured). The 5.5x headline is the n &gt;= 10^5 figure; in-cache ratios are 2.2-2.4x on Zen 4.
- PERFORMANCE.md numbers (2026-08-30/31, v0.9.0 kernels) are stale against the dev/v1.1.0 branch: issue #43 reports correctly rounded fast paths that took M1 exp 4.6 to 2.4, log 13.4 to 3.9, erf 2.2 to 1.8 and cos/sin 4.1 to 2.6 ns/el, not yet on main and with no new x86 numbers; the same issue shows the author's own libstats v2.4.1 kernels (about 0.52 ULP, not correctly rounded) still faster on M1 (exp 1.0, log 1.7, erf 1.4 ns/el).
- Open wrong-result bugs in the incomplete gamma/beta family despite the 'production' label: negative probabilities from beta_p at the x = 0.5 seam (#47), divergent gamma_p_inv near the upper tail (#48), 1e6-2e9 ULP beta inverse errors (#50), a negative denormal from gamma_q (#51), large errors from subnormal divisors on non-FMA tiers (#59). The measured elementary functions and erf are not named in these issues.
- Release builds do not check span lengths (a shorter span is out-of-bounds UB) and partial overlap of in and out is UB; only exact aliasing is allowed.

## Known shortcomings

- Tier A holds only for the Kaby Lake rows (tests/bench_trig.cpp, Apple Clang 15 release preset, i7-7820HQ); the Zen 4 CPU model and clang-cl version are unstated; wins only on sin/cos/erf/erfc, exp is 0.65x against Apple's x86 libm, log/log1p and lgamma are slower everywhere; the trig 5.5x is streaming only (2.2-2.4x at n&lt;=10^4, M1 sin 0.28x at n=1000); no SLEEF or Highway comparison; 1 star.
- The headline 5.5x sin/cos holds only at n &gt;= 10^5; the scalar libm's own cost per element rises with n at about 2 GB/s of traffic, so PERFORMANCE.md's 'leaves cache' story is doubtful and branch-predictor learning over the repeated seeded arrays is the likelier cause (inference); on M1 every corvus function runs 3.5-4x slower per element at n = 1000 (unexplained). PERFORMANCE.md is stale against branch dev/v1.1.0 (issue #43: M1 exp 4.6 to 2.4, log 13.4 to 3.9, cos/sin 4.1 to 2.6 ns/el), and the author's own libstats v2.4.1 is still faster on M1. Open wrong-result bugs #47-#59 in the gamma/beta inverses (e.g. gamma_p_inv(0.1, 0.99) = 7.9e106), not in the measured functions. The Zen 4 CPU is a Ryzen 7 7445HS (issues #37 and #43).

## Caveats and trade-offs

Wins are function specific: sin, cos and erf/erfc win against every libm measured, exp is slower than Apple's x86 libm (0.65x), log and log1p are slower than every vendor libm by design (correctly rounded), and lgamma is faster than UCRT but slower than Apple's libm in all stable bands. The libm baseline matters more than the kernel (the document says so). Only Windows UCRT and Apple libms were measured; glibc/libstdc++ and MSVC-compiled builds were not. The baseline is a scalar std:: libm loop; vectorised peers the README itself names (SLEEF, Highway contrib math) were not compared, so the result shows the gain of SIMD batching over scalar libm, not over the SIMD incumbent. Ratios depend on array size: the 5.5x trig headline is the streaming n &gt;= 10^5 figure, n &lt;= 10^4 gives 2.2-2.4x on Zen 4, and M1 at n = 1000 is slower for sin (0.28x). Trig inputs are uniform in [-1e6, 1e6], so the huge-argument reduction path is not timed. The M1 elementary column is a single run (indicative only), the Zen 4 CPU model is not named, erfinv and Bessel families are flagged not reproducible, and the batching-gain tables predate the 2026-09-30 per-element baseline change (#42). A 1-star repository maintained by one author; depends on Google Highway (Apache-2.0). [retier] Wins are function specific: sin, cos and erf/erfc win against every libm measured, exp is slower than Apple's x86 libm (0.65x), log and log1p are slower than every vendor libm by design (correctly rounded), and lgamma is faster than UCRT but slower than Apple's libm. Only Windows UCRT and Apple libms were measured; glibc/libstdc++ and MSVC-compiled builds were not; vectorised peers (SLEEF, Highway contrib math) were not compared. Size effect: the 5.5x headline holds only at n &gt;= 10^5 (2.2x to 2.4x at n &lt;= 10^4 on Zen 4; at n = 1000 on M1 sin is 0.28x); the scalar libm's own per-element cost rises with n at about 2 GB/s of traffic, far below memory bandwidth, so PERFORMANCE.md's 'leaves cache' explanation is doubtful and branch-predictor learning over the 11-51 re-timed seeded arrays is the likelier cause at small n (inference); every corvus function runs 3.5-4x slower per element at n = 1000 on M1 (unexplained). PERFORMANCE.md (2026-08-30/31, v0.9.0 kernels) is stale against branch dev/v1.1.0 (issue #43: M1 exp 4.6 to 2.4, log 13.4 to 3.9, cos/sin 4.1 to 2.6 ns/el, no new x86 numbers), and the author's own libstats v2.4.1 kernels are still faster on M1. Open wrong-result bugs #47-#59 in the incomplete gamma/beta family (not the measured elementary functions). Release builds do not check span lengths; partial overlap of in and out is UB.

Accuracy-first double-precision kernels (about 1 ULP bounds, validated against an mpmath oracle) that carry double-double intermediates, so the README states that throughput is not the claim. Needs array-style batch calls; advantage is close to none at two lanes. Highway (Apache-2.0) is distributed with binaries. Covers statistical special functions (erf/erfc, lgamma, incomplete gamma and beta and inverses, Bessel I0/I1) plus an elementary family.

## Maintenance

Actively developed by one author (324 commits on main to 2026-10-11, v1.0.1 released 2026-09-19, faster kernels on dev/v1.1.0), MIT-licensed and copyable as a CMake static library, but with 1 star and a dozen open accuracy bugs in the incomplete gamma/beta inverses it is best adopted for erf/erfc and sin/cos first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public (tests/bench_trig.cpp and the other tests/bench_\* sources, run by tools/quiet_bench.ps1/.sh), raw per-target outputs are committed under docs/bench-evidence/, and the Kaby Lake rows state Apple Clang 15, the CMake 'release' preset (CMakePresets.json, CMAKE_BUILD_TYPE=Release, project -ffp-contract=off) and the exact CPU (i7-7820HQ). The Zen 4 rows alone would fall short of A: the CPU is given only as 'Ryzen 7 (Zen 4)' and the clang-cl version is not stated in PERFORMANCE.md.
- **Verifier notes:** Numbers in the record match PERFORMANCE.md section 11 and the committed raw outputs; the bench harness (tests/bench_trig.cpp) writes every output and sinks a value, median of 11-51 reps after a warm-up, no harness defect found. Corrections add the size dependence (5.5x streaming vs 2.2-2.4x in cache on Zen 4; M1 sin 0.28x at n = 1000), exp 0.65x vs Apple x86 libm, the erf/erfc rows and the batching-table caveat. baseline_stdlib set to MSVC STL (clang-cl, math from UCRT) and libc++ (Apple Clang, math from libSystem); no comparison against SLEEF or Highway contrib math.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline_stdlib`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-74 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/OldCrow/corvus>
  - <https://github.com/OldCrow/corvus/commits>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/README.md>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/PLAN.md>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/tools/quiet_bench.sh>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/tools/quiet_bench.ps1>
  - <https://github.com/OldCrow/corvus/tree/main/tools>
  - <https://github.com/OldCrow/corvus/tree/main/docs/bench-evidence/2026-08-30-zen4-quiet>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/tests/bench_trig.cpp>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-zen4-quiet/quiet_bench_bench_trig.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-zen4-quiet/quiet_bench_bench_exp.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-zen4-quiet/quiet_bench.log>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-kaby-quiet/quiet_bench_bench_trig.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-kaby-quiet/quiet_bench_bench_exp.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-31-m1-indicative/quiet_bench_bench_trig.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-31-m1-indicative/quiet_bench_bench_exp.txt>
- **Sources the enricher read:**
  - <https://github.com/OldCrow/corvus>
  - <https://github.com/OldCrow/corvus/commits/main>
  - <https://github.com/OldCrow/corvus/branches>
  - <https://github.com/OldCrow/corvus/issues?q=is%3Aissue>
  - <https://github.com/OldCrow/corvus/issues/43>
  - <https://github.com/OldCrow/corvus/issues/37>
  - <https://github.com/OldCrow/corvus/commit/1bcba54>
  - <https://github.com/OldCrow/libstats>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/README.md>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/VERSIONING.md>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/USER-GUIDE.md>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/cmake/FindOrFetchHighway.cmake>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/include/corvus/corvus.h>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/src/trig.cpp>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/PLAN.md>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/tests/bench_trig.cpp>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/tests/bench_exp.cpp>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-zen4-quiet/quiet_bench_bench_trig.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-zen4-quiet/quiet_bench_bench_exp.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-zen4-quiet/quiet_bench_bench_erf.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-zen4-quiet/quiet_bench_bench_log.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-kaby-quiet/quiet_bench_bench_trig.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-kaby-quiet/quiet_bench_bench_exp.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-kaby-quiet/quiet_bench_bench_erf.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-30-kaby-quiet/quiet_bench_bench_log.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-31-m1-indicative/quiet_bench_bench_trig.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-31-m1-indicative/quiet_bench_bench_exp.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-31-m1-indicative/quiet_bench_bench_erf.txt>
  - <https://raw.githubusercontent.com/OldCrow/corvus/HEAD/docs/bench-evidence/2026-08-31-m1-indicative/quiet_bench_bench_log.txt>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/oldcrow/corvus`) · [data/wave13/enrich/raw/github_com_oldcrow_corvus.json](../../../data/wave13/enrich/raw/github_com_oldcrow_corvus.json) (enrichment confidence 0.8)

</details>
