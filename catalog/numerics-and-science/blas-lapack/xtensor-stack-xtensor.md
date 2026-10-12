# xtensor

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Header-only C++ n-d arrays with NumPy-style broadcasting and lazy expressions; beats NumPy on SIMD transcendentals, loses on large reductions.

| | |
|---|---|
| **Beats** | NumPy (built from source with -O3 -march=native, called from the same C++ executable via embedded Python) |
| **Claimed result** | PR #2915 geomean over 64x64 and 512x512: 34 xtensor faster, 10 NumPy faster, 2 level; at 512x512 only 23 faster, 6 within 5%, 17 slower (sum_all 0.45x, amax_all 0.22x, axis-0 reductions 0.09-0.11x); the sinh 9.43x row is an input-range artifact. |
| **Workload** | 46 NumPy-comparable functions (elementwise math such as sin, cos, tan, sinh, hypot, add, multiply, and reducers sum/mean/amin/amax/prod over all elements or one axis) on square 2D float64 arrays of 64x64 and 512x512 (Google Benchmark Range(64, 512)), single-threaded (OMP/OpenBLAS/MKL thread env vars set to 1); xtensor writes into a preallocated result via xt::noalias, NumPy is called from the same C++ executable through embedded Python with out= into the same buffer, Google Benchmark cpu_time, ratio = NumPy time / xtensor time (geomean over the two sizes). |
| **Metric** | throughput |
| **Hardware** | Host 'Quantstacklaptopalexis' (laptop); CPU model not stated; CPU scaling enabled and ASLR enabled |
| **Compiler and flags** | Benchmark CMake in the PR adds -O3 -g and, for GCC/Clang/Intel, -march=native; build with -DXTENSOR_USE_XSIMD=ON; NumPy built with CFLAGS -O3 -march=native and OpenBLAS. CI uses GCC 14 on Ubuntu 24.04, but the compiler of the reported run is not stated. |
| **Adoption** | 3.8k stars; 443 forks |
| **Last commit** | 2026-08-27 |
| **Links** | [repository](https://github.com/xtensor-stack/xtensor) · [benchmark](https://github.com/xtensor-stack/xtensor/pull/2915) |

## Verdict

In open contributor PR #2915 (single laptop run, CPU model, compiler and NumPy version not reported, CPU scaling on, Google Benchmark cpu_time, single thread, xsimd on, -O3 -march=native), xtensor with xt::noalias into a preallocated float64 buffer beat NumPy (built from source, called with out= through embedded Python) by 1.4-3.7x on most transcendental ufuncs at 512x512 and by about 1.1x on add/multiply/divide, but lost every reduction except prod_all and prod_axis1 (2-11x slower) and the exp family. The 9.43x sinh headline comes from inputs that all fall under xsimd's |x| &lt; 1 fast path.

## Use it when

- Porting NumPy elementwise math to C++ while keeping broadcasting semantics, especially transcendental-heavy code (sin, cos, tan, log10, log1p, atanh, hypot were 2.0-3.7x faster than NumPy at 512x512 float64 in PR #2915)
- Small arrays called in tight loops from C++, where NumPy's per-call Python overhead dominates (most 64x64 benchmarks were 1.1-4.7x faster, largely for this reason)
- Operating in place on NumPy, Julia or R buffers from a C++ extension through xtensor-python, xtensor-julia or xtensor-r
- Fixed-rank float64 work with known dimensionality, using xt::xtensor&lt;T, N&gt; and xt::noalias with xsimd enabled

## Skip it when

- Large reductions: at 512x512 xtensor lost 13 of 15 reduction benchmarks to NumPy (sum_all 0.45x, amax_all 0.22x, sum/mean/amin/amax/prod along axis 0 at 0.09-0.11x); only prod_all and prod_axis1 won; issue #2771 reports slow means over strided axes
- When Eigen is an option for vectors and matrices: navigation2 issue #4237 measured a 2000x60 dot product at 5.36 ms in xtensor vs 0.76 ms in Eigen, and MPPI controllers 20-26% faster after porting to Eigen::Array; the README's 'match Eigen' claim has no published numbers
- Exp-family functions: NumPy was faster on exp (0.92x), exp2 (0.83x), expm1 (0.77x) and cosh (0.55x) at 512x512
- Mixed-precision or integer arithmetic: issue #2849 shows uint16 division by 2 about 19-37x slower than std::transform (integer promotion blocks the SIMD path; still open), and #2881 reports xsimd slower than scalar for mixed precision
- Toolchains older than C++20: master and 0.27.x require C++20 (0.26.x C++17), so older compilers must pin an old release

## How it is fast

Expression templates fuse a whole elementwise expression into one loop with no temporaries, and xt::noalias skips the aliasing temporary on assignment. With XTENSOR_USE_XSIMD the fused loop runs on xsimd batches (SSE through AVX-512, NEON), and transcendental functions use xsimd's Boost.SIMD-derived polynomial and rational kernels instead of scalar libm calls, which is where the 2-4x wins over NumPy on sin, cos, tan, hypot, log10 and atanh come from. Fixed-rank xtensor and fixed-shape containers keep shapes and strides on the stack, which the README says matters for speed. Optional TBB or OpenMP parallel assignment exists (XTENSOR_USE_TBB / XTENSOR_USE_OPENMP, mutually exclusive).

## Compared with alternatives

Pick xtensor over Eigen or Armadillo when you need NumPy semantics (n-d arrays, broadcasting, universal functions) or zero-copy work on NumPy buffers; for matrix and vector algebra and for reductions, Eigen is the measured-faster choice and Armadillo the simpler MATLAB-like one.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | xtl (&gt;= 0.8.0); optional xsimd (CMake on master asks for 14.2.0 while the README table says ^13.2.0), TBB or OpenMP, nlohmann_json; xtensor-blas plus a BLAS/LAPACK for linear algebra |
| **Minimum toolchain** | C++20 for 0.27.x and master (cxx_std_20), C++17 for 0.26.x, C++14 before 0.26.0; CMake 3.15+ |
| **Platforms** | any C++20 target; SIMD via xsimd on x86 (SSE through AVX-512) and Arm NEON, scalar otherwise; conda-forge packages |
| **Thread safety** | not documented beyond plain value semantics; separate containers can be used from separate threads, and opt-in TBB/OpenMP parallelizes assignment internally |
| **Drop-in for the baseline** | partial: NumPy-like function names and broadcasting rules, but a C++ API; xtensor-python lets NumPy arrays be passed to C++ code written with it |

## Gotchas

- PR #2915 harness flaw behind the headline: init_benchmark_data makes inputs shrink with size (0.5\*j/(j+1) + sqrt(i)\*9/cols), so every 512x512 input is below 0.90 while 76% of 64x64 inputs are at or above 1. xsimd's sinh returns from its polynomial kernel early when all lanes are below 1 and only otherwise runs the exp path, so the 9.43x sinh figure at 512 (0.63 ns per element, against 3.3 ns per element at 64) is an artifact of the input range, not of typical sinh workloads.
- PR #2915 summary overstates the win count: its 34-of-46 tally is a geomean over 64x64, where every NumPy call pays PyObject_Call and np.sum wrapper overhead (np.sum takes 2978 ns at 64x64 vs 58006 ns for 64x the data at 512x512), and 512x512. At 512x512 alone (derived from page data) xtensor is faster on 23, within 5% on 6 and slower on 17. The harness also never checks that xtensor and NumPy return the same values, and xt::round (std::round, halves away from zero) is timed against np.round (halves to even).
- SIMD is off unless XTENSOR_USE_XSIMD is defined before any xtensor header (or the CMake option is set); without it the transcendental wins disappear.
- Accuracy under -ffast-math is unverified: open issue #2811 reports xt::cos returning wrong values with GCC 13 and -ffast-math (fine with GCC 11 or without the flag); xsimd's approximations were not compared against libm in the benchmark.

## Known shortcomings

- Unmerged first-party PR #2915 (34 xtensor faster, 10 NumPy faster, 2 level on 64x64 and 512x512 2D arrays, single-threaded); CPU and compiler of the run unstated; NumPy timings include embedded-Python call overhead; no result check; axis-0 reductions slower (prod_axis0 11.6x slower at 512x512); Eigen faster per navigation2 #4237; loose fit for blas-lapack.
- Enricher: in PR #2915 the inputs shrink with size (all 512x512 inputs are below 0.90, 76% of 64x64 inputs are 1 or above) and xsimd sinh returns early when all lanes are below 1, so the sinh 9.43x is an input-range artifact; the 34/46 tally is a geomean that includes 64x64, where NumPy pays Python call overhead. At 512x512 only: 23 faster, 6 within 5%, 17 slower including 13 of 15 reductions (sum_all 0.45x, amax_all 0.22x, axis0 0.09-0.11x); round compares std::round with np.round (half-to-even); no result check. Open issues #2849 (uint16 divide 19-37x slower) and #2811 (cos wrong with GCC 13 -ffast-math).

## Caveats and trade-offs

(1) Numbers come from an open, unmerged pull request (#2915, 'Add comparative benchmarks with numpy', opened 2026-05-13, ready for review 2026-05-18, no reviews) by xtensor contributor Alex-PLACET; the merged benchmark/ directory has no NumPy, Eigen or BLAS comparison and no published results (benchmark_stl.cpp only compares xtensor with std::transform). (2) Single laptop run, two sizes (64x64 and 512x512) per function, CPU model and compiler of that run not stated, CPU scaling and ASLR enabled. (3) NumPy is built from source with unpinned version; every NumPy timing includes the embedded-Python PyObject_Call overhead, which inflates small (64x64) ratios for cheap ops; the harness has no check that xtensor/xsimd and NumPy produce the same values (accuracy of xsimd transcendental approximations is not compared). (4) Mixed result: xtensor faster on 34 of 46 functions, NumPy faster on 10 (exp, exp2, cosh, amax_all, amin_all and the axis-0 reductions sum/mean/amin/amax/prod; prod_axis0 at 512x512 is 11.6x slower in xtensor), 2 level (round, sum_all). (5) The category's baseline Eigen is not beaten: README says only that statically dimensioned performance 'matches' Eigen (no numbers), and the independent ros-navigation/navigation2 issue #4237 ('[MPPI]: Replace xtensor with Eigen Experiment') reports Eigen faster (2000x60 dot product 5.36 ms xtensor vs 0.76 ms Eigen; MPPI BM_DiffDrive 11.56 vs 8.58 ms on an 8th-gen i7 with AVX2; ROS1 control loop on an i5-12400F level at 5 ms average), compiler not stated. (6) The separate xtensor-benchmark repo (xtensor vs Eigen3, Armadillo, Blitz++) publishes no result numbers. (7) Category fit is loose: elementwise math and reductions, not BLAS/LAPACK kernels. [retier] Unmerged first-party PR; CPU and compiler unstated; NumPy timings include embedded-Python call overhead; no result check; round compares std::round with half-to-even np.round; open #2849 and #2811.

Header-only n-d array library with NumPy-style broadcasting and lazy expressions, SIMD via xsimd. README says shapes of dynamically dimensioned xarray are heap allocated and cost a little more than statically dimensioned xtensor. Linear algebra needs the separate xtensor-blas package over BLAS/LAPACK, so xtensor itself is not a BLAS/LAPACK implementation; blas-lapack is only the nearest wave-8 category.

## Maintenance

Active (QuantStack; last commit 2026-08-27, 384 open issues, 44 open PRs), BSD-3-Clause and header-only, so it is easy to vendor; the NumPy benchmark is still an unmerged, unreviewed PR, so treat its numbers as first-party and correct the record's sinh and 34-of-46 claims as described in gotchas (tier stays C).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** PR #2915 publishes the benchmark code (benchmark/benchmark_numpy.cpp, benchmark/CMakeLists.txt, tools/report_numpy_benchmarks.py) with -O3 -march=native flags, but the reported run states neither the compiler nor the CPU model (only host 'Quantstacklaptopalexis', CPU scaling on), and the numbers are first-party from an unmerged contributor PR, so it cannot be A.
- **Verifier notes:** Numbers in claimed_speedup match the PR #2915 summary table exactly (hypot 3.85x, tan 3.76x, cos 2.85x, sinh 4.95x with 165511 vs 1560352 ns at 512, atanh 2.36x, prod_axis0 0.39x with 632740 vs 54496 ns, mean_axis0 0.58x, amax_axis0 0.47x, cosh 0.70x, round 1.01x, sum_all 1.05x; 34/10/2 split). Harness is sound (xtensor result forced via noalias assignment and DoNotOptimize, NumPy writes to a preallocated out buffer) but includes Python call overhead on the NumPy side and no result check; shortcomings: unmerged first-party PR, no CPU/compiler, slower than NumPy on axis-0 reductions and slower than Eigen per navigation2 #4237. Metadata confirmed: BSD-3-Clause, 3.8k stars, 443 forks, last commit 2026-08-27, not archived.
- **Fields the verifier corrected:** `workload`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-177 (wave 8); enricher w8 pair-042
- **Pages the verifier opened:**
  - <https://github.com/xtensor-stack/xtensor/pull/2915>
  - <https://github.com/xtensor-stack/xtensor/pull/2915/files>
  - <https://raw.githubusercontent.com/Alex-PLACET/xtensor/78bcf9db3864fb71d0243992a4672c6321622be2/benchmark/benchmark_numpy.cpp>
  - <https://github.com/xtensor-stack/xtensor>
  - <https://github.com/xtensor-stack/xtensor/commits/master>
  - <https://github.com/ros-navigation/navigation2/issues/4237>
- **Sources the enricher read:**
  - <https://github.com/xtensor-stack/xtensor>
  - <https://raw.githubusercontent.com/xtensor-stack/xtensor/HEAD/README.md>
  - <https://raw.githubusercontent.com/xtensor-stack/xtensor/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/xtensor-stack/xtensor/HEAD/environment-dev.yml>
  - <https://raw.githubusercontent.com/xtensor-stack/xtensor/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/xtensor-stack/xtensor/HEAD/benchmark/benchmark_stl.cpp>
  - <https://github.com/xtensor-stack/xtensor/pull/2915>
  - <https://raw.githubusercontent.com/Alex-PLACET/xtensor/78bcf9db3864fb71d0243992a4672c6321622be2/benchmark/benchmark_numpy.cpp>
  - <https://raw.githubusercontent.com/Alex-PLACET/xtensor/78bcf9db3864fb71d0243992a4672c6321622be2/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Alex-PLACET/xtensor/78bcf9db3864fb71d0243992a4672c6321622be2/tools/report_numpy_benchmarks.py>
  - <https://github.com/xtensor-stack/xsimd/tree/master/include/xsimd/arch/common>
  - <https://raw.githubusercontent.com/xtensor-stack/xsimd/HEAD/include/xsimd/arch/common/xsimd_common_trigo.hpp>
  - <https://raw.githubusercontent.com/xtensor-stack/xsimd/HEAD/include/xsimd/arch/common/xsimd_common_math.hpp>
  - <https://raw.githubusercontent.com/xtensor-stack/xsimd/HEAD/include/xsimd/arch/common/xsimd_common_details.hpp>
  - <https://github.com/xtensor-stack/xtensor/issues?q=is%3Aissue+is%3Aopen+slow+OR+performance+OR+wrong>
  - <https://github.com/xtensor-stack/xtensor/issues/2849>
  - <https://github.com/xtensor-stack/xtensor/issues/2811>
  - <https://github.com/ros-navigation/navigation2/issues/4237>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/xtensor-stack/xtensor`) · [data/wave8/enrich/raw/github_com_xtensor_stack_xtensor.json](../../../data/wave8/enrich/raw/github_com_xtensor_stack_xtensor.json) (enrichment confidence 0.7)

</details>
