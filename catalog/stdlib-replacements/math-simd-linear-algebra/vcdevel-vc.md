# Vc (SIMD Vector Classes)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> C++11 SIMD vector types (float_v, double_v) with vectorized math for x86 SSE2-AVX2; beats per-element scalar &lt;cmath&gt; loops.

| | |
|---|---|
| **Beats** | Sequential reference loop that calls an out-of-line scalar kernel per element (kernel_reference.cpp is compiled as a separate translation unit without LTO, so the loop cannot be auto-vectorized) using std::exp, std::log and std::sqrt from &lt;cmath&gt; (GCC 5.3.0 libstdc++ forwarding to glibc libm), built with -O3 -ftree-vectorize -ffast-math -mavx2 -mfma |
| **Claimed result** | Third-party data (mean time per loop iteration, GCC 5.3.0, Haswell, 1 thread, SIMD width 4), Vc (simd_class_vectorization) vs sequential std:: reference, ratios derived from page data: simple EXP 7.8586e-09 s vs 2.477e-08 s (3.15x), simple LOG 8.14221e-09 vs 3.58324e-08 (4.40x), simple SQRT 6.41381e-09 vs 1.14677e-08 (1.79x); conditional_math_call EXP 2.27x, LOG 2.39x, SQRT 5.07x (3.3077e-09 vs 1.67538e-08); early_return EXP 2.87x, LOG 3.16x, SQRT 4.30x; nested_branching EXP 1.56x, LOG 1.64x, SQRT 2.19x; while_loop EXP 1.34x, LOG 1.62x, SQRT 0.78x (Vc slower: 5.97054e-08 vs 4.6563e-08). In the same logs plain OpenMP 4.x 'omp declare simd' (explicit_vectorization) reaches only 1.00-1.09x and is slower than Vc in all 15 cases, the paper's enhanced OpenMP version beats Vc in 8 of 15 cases, and hand-written AVX2 intrinsics (manual_vectorization) beat Vc in 12 of 15 cases (derived from page data). |
| **Workload** | Euro-Par 2016 SIMD kernels run on one thread over 8192 doubles with AVX2 (SIMD width 4): simple (sqrt/log/exp wrapper), conditional math call, early return, nested branching, and while loop with varying trip count; the Vc 1.2.0 version (simd_class_vectorization) is compared with the sequential reference. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2680v3 (Haswell) at 1.9 GHz, Cray aprun with --p-state=1900000 |
| **Compiler and flags** | GNU 5.3.0, Vc 1.2.0; makefile.gnu in flwende/simd_benchmarks: g++ -O3 -fopenmp -std=c++11 -ftree-vectorize -ffast-math -fopt-info-vec-optimized -mavx2 -mfma -D__AVX2__ -DBENCHMARK_FUNC_&lt;F&gt;_&lt;F&gt; -DSIMD_WIDTH_LOGICAL_REAL64=4 -DDEBUG, plus -DCONDITIONAL_CALL for all executables (notes.txt); Vc linked from \$(VC_ROOT)/lib/libVc.a. The makefile and the data come from the same August 2016 commits (notes dated 2016-08-15, last commit 2016-08-16). |
| **Adoption** | 1.5k stars; packaged in Debian and Arch Linux and listed in CERN LCG |
| **Last commit** | 2026-07-07 |
| **Links** | [repository](https://github.com/VcDevel/Vc) · [benchmark](https://github.com/flwende/simd_benchmarks/tree/master/data/Euro-Par-2016-conference/hsw_benchmark.gnu-5.3.0_Vc-1.2.0_conditional) |

## Verdict

Third-party Euro-Par 2016 data (Wende et al., flwende/simd_benchmarks): one thread on a Xeon E5-2680v3 (Haswell) pinned at 1.9 GHz, GCC 5.3.0 -O3 -ffast-math -mavx2 -mfma, 8192 doubles with a 50% random call mask; Vc 1.2.0 double_v kernels against a per-element, out-of-line scalar loop over std::exp/std::log/std::sqrt (libstdc++ to glibc) ran 1.34-5.07x faster in 14 of 15 kernel and function pairs and 0.78x on while_loop SQRT. The logs print the max relative error against the reference (3.5e-16 for simple EXP, 3.2e-15 for simple LOG, 0 for while_loop SQRT), so the outputs were checked; the baseline was deliberately non-vectorizable, so no comparison with auto-vectorized code exists.

## Use it when

- Existing x86-only C++ code that needs explicit SIMD across SSE2 to AVX2 without writing intrinsics, especially loops that span function or translation-unit boundaries where auto-vectorization fails.
- Element-wise transcendental work on double or float arrays (exp, log, sqrt over thousands of values): in the Euro-Par 2016 logs Vc's width-4 kernels ran 1.8-4.4x faster than per-element std::exp/std::log/std::sqrt on Haswell.
- Branchy per-element kernels (conditional calls, early returns) that can be expressed as masks: 2.3-5.1x on the conditional_math_call and early_return kernels of the same study.
- Toolchains stuck at C++11 or C++14 (GCC 4.8.1+, clang 3.4+), where std::experimental::simd is not available.

## Skip it when

- New projects: the README says Vc is in maintenance mode and no longer actively developed, and points users to std-simd (std::experimental::simd, shipped with GCC 11 libstdc++).
- AVX-512, ARM NEON/SVE, RISC-V or GPUs: the README lists only SSE2 to AVX2 (AVX-512 and NEON struck out, MIC removed in 1.4); other targets fall back to the Scalar implementation with vector width 1, so no speedup.
- Loops with lane-divergent trip counts: the while_loop SQRT kernel ran at 0.78x of the scalar reference (59.7 vs 46.6 ns per element), because masked-off lanes keep iterating.
- When hand-tuned intrinsics are acceptable: manual AVX2 code beat the Vc version in 12 of 15 single-thread cases in the same logs (for example simple EXP 6.18 vs 7.86 ns per element).

## How it is fast

Each operation maps to one SIMD instruction over 4 doubles (AVX/AVX2) or 2 (SSE), and data-dependent control flow becomes mask arithmetic instead of per-element branches. The transcendental functions are vectorized Cephes-style range reduction plus polynomial evaluation (exp via 2^n scaling and a degree-6 polynomial), so one call evaluates a whole vector instead of one libm call per element.

## Compared with alternatives

Among the catalogued siblings, xsimd is the comparable SIMD-type wrapper, while SLEEF, VDT and fmath only supply vectorized math functions; pick Vc when you maintain x86 code already written against Vc 1.x, or need its masked-assignment and simdize API on a C++11 compiler, and otherwise prefer xsimd or std::experimental::simd for new code and SLEEF or VDT when you only need vector exp/log/sin.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at runtime; CMake 3.5+ to build libVc.a (git submodules only for the test tree) |
| **Minimum toolchain** | C++11; GCC 4.8.1+, clang 3.4+, ICC 18.0.5+, Visual Studio 2019 (64-bit target) |
| **Platforms** | x86 and x86-64 with SSE2, SSE3, SSSE3, SSE4.1/4.2, SSE4a, AVX, AVX2 (+FMA, FMA4, XOP, BMI2); everything else compiles to the Scalar implementation (width 1) |
| **Thread safety** | not documented; vectors are plain value types with no shared state |
| **Drop-in for the baseline** | no |

## Gotchas

- Vector width and therefore data layout and function signatures follow the compile flags (Vc_IMPL is chosen from __AVX2__, __AVX__, __SSE4_2__ and so on), so every translation unit and libVc.a must target the same ISA; a static constructor in every TU calls checkLibraryAbi at startup and aborts if headers and library disagree.
- Containers of Vc types need over-aligned allocation: std::vector&lt;double_v&gt; or structs holding Vc vectors should use Vc::Allocator or Vc_DECLARE_ALLOCATOR, as the Vc/Allocator header documents.
- Masked operations still compute every lane: in the benchmark y(mask) = Vc::exp(...) evaluated all 4 lanes and masked only the store, while the scalar reference skipped about half of the calls (50% random mask) but paid a data-dependent branch; speedups therefore depend on mask density. Results matched the reference to about 3e-16 (exp) and 3e-15 (log) relative error, but the functions are polynomial approximations, not correctly rounded (the float exp returns 0 below about -88.03 instead of a subnormal).
- Open bugs remain: #349 (SSE uchar min/max built with schar; a September 2023 commit 'Fix horizontal max/min for uchar' may cover it), #257 (wrong short SimdArray division), #249 (macOS upper AVX register halves), #242 (clang 7 miscompiled AVX/AVX2 on the 1.3 branch) and #367 (Xcode 26 beta build error, with a C++23 missing-include fix committed in April 2026).

## Known shortcomings

- flwende/simd_benchmarks (Euro-Par 2016 data, Xeon E5-2680v3, GCC 5.3.0): the baseline is a scalar out-of-line std::exp/log/sqrt loop in a separate translation unit that is never auto-vectorized; Vc is 0.78x on the while_loop SQRT case and hand-written intrinsics beat it in 12 of 15 logs; 2016 Vc 1.2.0 data; the README says maintenance mode (std::simd is the successor).
- Harness sound (logs print max relative error vs reference: 3.5e-16 exp, 3.2e-15 log), but the scalar reference skips about 50% of calls behind a random-mask branch while Vc computes all 4 lanes and masks the store, so the gain mixes SIMD math with branch removal. x86 SSE2-AVX2 only (scalar width 1 elsewhere); maintenance mode (successor std-simd); startup ABI check aborts on header/lib mismatch; open bugs #349, #257, #249, #367.

## Caveats and trade-offs

Vc's own README and docs carry no benchmark numbers; the evidence is third-party data from the Euro-Par 2016 paper 'Portable SIMD Performance with OpenMP 4.x Compiler Directives' (Wende et al.), whose subject is OpenMP, not Vc. The baseline is a deliberately scalar loop: the reference kernel sits in a separate translation unit and is called once per element with std::exp/std::log/std::sqrt, so the gains measure 4-wide SIMD with Vc's vector math (and one call per 4 elements) against scalar libm with one call per element, not against an auto-vectorized loop. Vc is slower than the reference on while_loop SQRT (0.78x) and hand-written intrinsics beat Vc in 12 of 15 single-thread cases. Only single-thread width-4 GNU logs were read (threads12, SIMD width 8, Intel 16.0.3, Clang 3.9.0(pre), KNC and KNL logs not read). Arrays are small (n = 8192 doubles, cache-resident) and the -DCONDITIONAL_CALL build adds a per-element mask to every kernel. The HEAD build.gnu sets VC_AVAILABLE=no, so reproducing the Vc rows needs VC_AVAILABLE=yes and VC_ROOT set. The data is from Vc 1.2.0 (2016); Vc is now 1.4.x and its README says it is in maintenance mode and no longer actively developed (pull requests with bug fixes are still reviewed), recommending std::simd (experimental in GCC 11 libstdc++) instead. The Vc authors' own paper and Kretz's dissertation were unreachable (host blocked), so no first-party numbers were checked. The data repo has only 9 commits and 6 stars.

Explicit SIMD value types (float_v, double_v) written into the code, so algorithms must be restructured for data parallelism; supports x86 SSE2 to AVX2 only (AVX-512, NEON and MIC support removed or never finished); the project is in maintenance mode and points users to std-simd (std::experimental::simd in GCC 11+ libstdc++).

## Maintenance

Maintenance mode by the authors' own statement, but the 1.4 branch still takes compatibility and CI fixes (C++23 includes in April 2026, a GCC 14 CMake fix in July 2026; last release 1.4.5 in June 2024; 80 open issues); BSD-3-Clause and easy to build, best kept for existing x86 Vc users.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** All 15 single-thread width-4 logs in data/Euro-Par-2016-conference/hsw_benchmark.gnu-5.3.0_Vc-1.2.0_conditional reproduce the recorded means and ratios; benchmark code is public (flwende/simd_benchmarks src/&lt;kernel&gt;/kernel_reference.cpp and kernel_simd_class_vectorization.cpp, src/common/benchmark.cpp), compiler GNU 5.3.0 and flags (makefile.gnu, unchanged since the 2016-08-16 commit that added the data) and CPU (Xeon E5-2680v3 @ 1.9 GHz, notes.txt) are stated, run by third parties for a peer-reviewed Euro-Par 2016 paper.
- **Verifier notes:** All 15 ratios re-derived from the logs and match; tier A confirmed (public code, GCC 5.3.0, makefile flags from the same 2016 commit, Xeon E5-2680v3). Corrections: the baseline is a scalar out-of-line loop over std::exp/log/sqrt (&lt;cmath&gt;, libstdc++), so baseline_in_list and compared_against_cpp_std_directly become true; plain omp simd is slower than Vc, manual intrinsics faster in 12 of 15. Shortcomings: SIMD-vs-scalar comparison by construction, 0.78x on while_loop SQRT, 2016 Vc 1.2.0 data, project in maintenance mode (std::simd is the successor).
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `baseline_stdlib`, `compared_against_cpp_std_directly`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** flwende/simd_benchmarks (verifier); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/flwende/simd_benchmarks/tree/master/data/Euro-Par-2016-conference/hsw_benchmark.gnu-5.3.0_Vc-1.2.0_conditional>
  - <https://github.com/flwende/simd_benchmarks/tree/master/data/Euro-Par-2016-conference>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/data/Euro-Par-2016-conference/notes.txt>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/data/Euro-Par-2016-conference/hsw_benchmark.gnu-5.3.0_Vc-1.2.0_conditional/benchmark_simple_EXP_EXP_simdwidth4_threads1_n8192_pstate1900000.log>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/data/Euro-Par-2016-conference/hsw_benchmark.gnu-5.3.0_Vc-1.2.0_conditional/benchmark_while_loop_SQRT_SQRT_simdwidth4_threads1_n8192_pstate1900000.log>
  - <https://github.com/flwende/simd_benchmarks>
  - <https://github.com/flwende/simd_benchmarks/commits/master>
  - <https://github.com/flwende/simd_benchmarks/tree/master/src>
  - <https://github.com/flwende/simd_benchmarks/tree/master/src/simple>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/makefile.gnu>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/build.gnu>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/src/makefile_local>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/src/common/benchmark.cpp>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/include/common/kernel.hpp>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/src/simple/kernel_reference.cpp>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/src/simple/kernel_simd_class_vectorization.cpp>
  - <https://github.com/VcDevel/Vc>
  - <https://github.com/VcDevel/Vc/commits/1.4>
- **Sources the enricher read:**
  - <https://github.com/VcDevel/Vc>
  - <https://raw.githubusercontent.com/VcDevel/Vc/HEAD/README.md>
  - <https://raw.githubusercontent.com/VcDevel/Vc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/VcDevel/Vc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/VcDevel/Vc/HEAD/INSTALL>
  - <https://raw.githubusercontent.com/VcDevel/Vc/HEAD/Vc/Vc>
  - <https://raw.githubusercontent.com/VcDevel/Vc/HEAD/Vc/version.h>
  - <https://raw.githubusercontent.com/VcDevel/Vc/HEAD/Vc/global.h>
  - <https://raw.githubusercontent.com/VcDevel/Vc/HEAD/Vc/Allocator>
  - <https://raw.githubusercontent.com/VcDevel/Vc/HEAD/Vc/common/exponential.h>
  - <https://raw.githubusercontent.com/VcDevel/Vc/HEAD/Vc/common/logarithm.h>
  - <https://github.com/VcDevel/Vc/issues>
  - <https://github.com/VcDevel/Vc/issues/349>
  - <https://github.com/VcDevel/Vc/issues/367>
  - <https://github.com/VcDevel/Vc/commits/1.4>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/src/common/benchmark.cpp>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/include/common/kernel.hpp>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/src/simple/kernel_reference.cpp>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/src/simple/kernel_simd_class_vectorization.cpp>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/src/while_loop/kernel_reference.cpp>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/src/while_loop/kernel_simd_class_vectorization.cpp>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/src/makefile_local>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/makefile.gnu>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/build.gnu>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/data/Euro-Par-2016-conference/notes.txt>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/data/Euro-Par-2016-conference/hsw_benchmark.gnu-5.3.0_Vc-1.2.0_conditional/benchmark_simple_EXP_EXP_simdwidth4_threads1_n8192_pstate1900000.log>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/data/Euro-Par-2016-conference/hsw_benchmark.gnu-5.3.0_Vc-1.2.0_conditional/benchmark_simple_LOG_LOG_simdwidth4_threads1_n8192_pstate1900000.log>
  - <https://raw.githubusercontent.com/flwende/simd_benchmarks/HEAD/data/Euro-Par-2016-conference/hsw_benchmark.gnu-5.3.0_Vc-1.2.0_conditional/benchmark_while_loop_SQRT_SQRT_simdwidth4_threads1_n8192_pstate1900000.log>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/vcdevel/vc`) · [data/wave1/enrich/raw/github_com_vcdevel_vc.json](../../../data/wave1/enrich/raw/github_com_vcdevel_vc.json) (enrichment confidence 0.8)

</details>
