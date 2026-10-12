# IntrinsicML (hand-vectorized SIMD microkernels for ML)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Teaching-grade AVX2/AVX-512 SGEMM and activation kernels; beats a strided scalar triple loop, reaches 4-60% of single-thread OpenBLAS.

| | |
|---|---|
| **Beats** | plain triple-loop scalar C++ reference (GCC -O3 -ffast-math); also OpenBLAS sgemm single thread (where it is slower) |
| **Claimed result** | README table (approximate, 'this environment', no backing table): packed SGEMM vs a plain triple-loop scalar reference about 0.7x at 64x64 (slower), about 10x at 128, about 26x at 256; vs single-thread OpenBLAS about 4%, 29%, 55%, 59% of its speed at 64-512. docs/BENCHMARKS.md CI run (main_bench, avx_matmul kernel vs scalar): 0.069 vs 0.017 ms at 64 (4.1x), 1.114 vs 0.162 ms at 128 (6.9x), 20.88 vs 2.006 ms at 256 (10.4x) (derived from page data); OpenBLAS table 6.4 vs 165.0 GFLOPS at 64 up to 73.8 vs 124.0 at 1024. GeLU: the README's 6-10x is the author's expected speedup on platforms without SVML; the measured CI run shows AVX2 tanh GeLU and the erff reference within 2% of each other (1,908,062 vs 1,939,830 cycles at n = 1M). |
| **Workload** | Single-precision GEMM (packed AVX2/AVX-512 kernel) at 64x64 to 512x512, and GeLU on 1M elements, single core. |
| **Metric** | throughput |
| **Hardware** | Virtualised x86-64 CI runner with AVX2+FMA, about 2.1 GHz calibrated TSC, exact model varies (docs/BENCHMARKS.md) |
| **Compiler and flags** | docs/BENCHMARKS.md: GCC-12, -O3 -march=native -mfma -ffast-math -DNDEBUG, Ubuntu 22.04 (CMakeLists.txt PERF_FLAGS); README states both kernel and scalar reference built with -O3 -ffast-math |
| **Adoption** | 15 stars; Zenodo preprint |
| **Last commit** | 2026-08-10 |
| **Links** | [repository](https://github.com/Mattral/SIMD-Microkernels-for-ML-Workloads) · [benchmark](https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/README.md) |

## Verdict

On a virtualised CI runner (AVX2+FMA, about 2.1 GHz calibrated TSC, CPU model not stated, GCC 12 -O3 -march=native -mfma -ffast-math, Ubuntu 22.04), the avx_matmul 6x16 kernel beat the repo's strided scalar i-j-k loop 4.1x, 6.9x and 10.4x at N = 64, 128 and 256 (RDTSC, minimum of 10 runs). The packed kernel that Python calls reached 6.4-73.8 GFLOPS against 165-124 GFLOPS for single-thread OpenBLAS (4-60%), and the AVX2 GeLU matched glibc's SVML-vectorised erff (1.02x). The README's 10x/26x GEMM and 6-10x GeLU figures are not backed by any committed table.

## Use it when

- Learning or teaching how a packed BLIS-style SGEMM is built: every tiling constant and kernel choice is explained in comments and docs/DESIGN.md.
- Vendoring a small Apache-2.0 AVX2 SGEMM or activation kernel into a project that cannot link OpenBLAS, MKL or BLIS and only needs one-core FP32 throughput in the tens of GFLOPS.
- GeLU or SiLU on libc builds without vectorised erff/tanh (musl/Alpine, macOS), where the author expects 6-10x over the scalar loop; this is a projection, not a measurement.
- Experimenting with AVX2 versus AVX-512 dispatch, or FP16/BF16-to-FP32 conversion GEMM, through a NumPy-callable module with an isa= override.

## Skip it when

- Whenever OpenBLAS, MKL or BLIS is available: single-thread OpenBLAS was 1.7x (N=1024) to 26x (N=64) faster in the author's own run (165-124 vs 6.4-73.8 GFLOPS, derived from page data).
- GeLU on glibc 2.22 or later: GCC vectorises the erff reference through SVML (_ZGVdN8v_erff), and the AVX2 tanh kernel measured within 2% of it (1,908,062 vs 1,939,830 cycles at n = 1M).
- Non-x86 targets: the SIMD paths need AVX2 and FMA (the GEMM sources #error without AVX2); other CPUs get a scalar-only build.
- Multi-threaded GEMM: OpenMP is off by default, and when enabled it parallelises only the NC=2048 column loop, so matrices with N &lt;= 2048 still run on one thread.
- Transposed, strided or non-float32 inputs: the Python sgemm accepts only float32 C-contiguous arrays with lda = K and no transpose flags, and the package is not on PyPI (build from source).

## How it is fast

GEMM follows the Goto/BLIS five-loop scheme: B is packed into KC=256-deep NR-wide panels and A into MC x KC panels, then an 8x8 AVX2 register-blocked micro-kernel (8 YMM accumulators, broadcast of A, FMA against one B row, unrolled by 4 with software prefetch) or an 8x16 AVX-512 kernel chosen at run time computes each tile; avx_matmul.cpp holds a second 6x16/6x32 kernel. Most of the headline speedup comes from the baseline: the scalar i-j-k loop walks B with a stride of N floats per step and falls from 7.6 to 1.6 GFLOPS between N=64 and N=256. GeLU uses the tanh approximation with tanh computed as (e^2y - 1)/(e^2y + 1) from a Cody-Waite range-reduced polynomial exp and an rcp plus Newton-step division, 8 lanes per AVX2 instruction.

## Compared with alternatives

Pick it over marcelcases/simd, Vectis or UltraSIMD when you want a complete, documented packed SGEMM plus ML activations callable from NumPy rather than single-loop kernels; to write your own kernels portably, EVE or the Vector Class Library are the better base, and for production GEMM use a real BLAS.

## Integration

| | |
|---|---|
| **Form** | static lib + Python extension module (pybind11, built from source with scikit-build-core; not published on PyPI) |
| **Dependencies** | none for the C++ library; pybind11 &gt;= 2.11 and NumPy &gt;= 1.24 for Python; optional OpenMP (SIMD_ML_OPENMP) and OpenBLAS (benchmark baseline only) |
| **Minimum toolchain** | C++17, GCC &gt;= 12 or Clang &gt;= 15, CMake &gt;= 3.22, Python &gt;= 3.9 |
| **Platforms** | x86-64 with AVX2 + FMA (AVX-512F+DQ 8x16 kernel auto-dispatched; F16C for the FP16 GEMM); scalar-only build elsewhere |
| **Thread safety** | Python bindings release the GIL during kernels and the ISA override is thread_local; no other thread-safety statement |
| **Drop-in for the baseline** | partial: sgemm_packed and simd_sgemm take a row-major sgemm-like argument list (M, N, K, alpha, A, lda, B, ldb, beta, C, ldc) but no transpose flags, so they are not a cblas_sgemm or BLAS sgemm_ replacement; the scalar baseline is the repo's own loop, not a std facility |

## Gotchas

- The committed result files contradict docs/BENCHMARKS.md: benchmarks/results/bench_results.json (an RDTSC run with older 'Scalar GeLU' labels, undated) shows simd_sgemm stuck near 29.3M cycles at 64, 128 and 256, so the SIMD GEMM is 213x slower than scalar at 64x64 (0.044 vs 9.32 GFLOPS) and 5.5x slower at 128, and only 1.7x faster at 256 (derived from file data). The regression baseline gemm_results.json shows 76.9 and 88.2 GFLOPS at 256 and 512, against 64.1 and 73.3 in the docs. Neither discrepancy is explained, so no published GEMM number is reproducible from the repo's own artifacts.
- The published N=64 and N=128 figures predate the current code: since commit acb42de (2026-08-07), sgemm_packed sends max(M,N,K) &lt;= 128 to sgemm_direct_avx2, an unpacked loop with one 8-wide accumulator per column strip (a serial FMA dependency chain over K), and no new numbers were captured. The README still describes the 0.7x-at-64 regression as an open roadmap item while ROADMAP.md marks it done.
- Each packed call above the 128 threshold allocates and zero-fills about 2.1 MB of packing buffers (make_aligned_array memsets a fixed KC x NC B panel plus an MC x KC A panel) whatever the matrix size, a fixed cost per call that is not amortised for mid-size matrices.
- Kernels are built with -march=native -ffast-math, so binaries are host-specific and NaN/Inf behaviour is undefined, while the precision tests use a separate non-fast-math build. The Python sgemm casts C to a float32 array before validating it, so a float64 C would be converted to a copy and the 'in-place' result would not reach the caller's array (from reading the binding, not run).

## Known shortcomings

- The README GeLU 6-10x is a projection (measured 1.02x vs erff); beats only a naive i-j-p scalar loop and loses to OpenBLAS everywhere (4-59%); README GEMM ratios differ from docs/BENCHMARKS.md (4.1/6.9/10.4x); CI virtual machine, no CPU model.
- Evidence flaw: the committed benchmarks/results/bench_results.json (an undated RDTSC run) shows simd_sgemm stuck near 29.3M cycles at 64-256, i.e. 213x slower than scalar at 64 and 5.5x slower at 128; the committed gemm_results.json (76.9/88.2 GFLOPS at 256/512) disagrees with docs/BENCHMARKS.md (64.1/73.3); the N &lt;= 128 numbers predate commit acb42de (2026-08-07), which sends small matrices to the unpacked single-accumulator sgemm_direct_avx2, with no new numbers since. Each packed call memsets about 2.1 MB of buffers; OpenMP parallelises only the NC = 2048 loop; the build is -march=native -ffast-math. Slower than single-thread OpenBLAS at every size.

## Caveats and trade-offs

Slower than OpenBLAS at every size (4% to 60% of its single-thread throughput) and, per the README, slower than the scalar loop at 64x64. The baseline is a textbook i-j-p triple loop that walks B with stride N (naive_gemm.hpp), whose throughput falls from 7.6 to 1.6 GFLOPS between 64 and 256, so the 10x-26x figures are against a straw-man scalar loop. The README speedups are rounded figures not traceable to any committed table; docs/BENCHMARKS.md shows 4x-10x for the avx_matmul path, and the bench_stat harness that times the packed kernel has no scalar row. The GeLU 6-10x is an expectation for non-SVML platforms; measured, the AVX2 tanh approximation equals glibc's SVML-vectorised erff (1.02x), and the two compute different formulas. The main_bench 'GElems/s' column is a FLOP proxy (15 ops per element), about 15x the true element rate. Numbers come from noisy shared CI VMs with no CPU model, and OpenBLAS's 165 GFLOPS at N=64 exceeds the stated 2.1 GHz peak, so the utilisation percentages are unreliable. The Zenodo preprint was not opened (zenodo blocked). [retier] Slower than single-thread OpenBLAS at every size (4% to 60% of its throughput) and, per the README, slower than the scalar loop at 64x64. The README speedups are rounded figures not traceable to any committed table, and the committed results contradict them: benchmarks/results/bench_results.json (an undated RDTSC run with older 'Scalar GeLU' labels) shows simd_sgemm stuck near 29.3M cycles at 64, 128 and 256, i.e. 213x slower than scalar at 64x64 (0.044 vs 9.32 GFLOPS) and 5.5x slower at 128, only 1.7x faster at 256 (derived from file data); gemm_results.json shows 76.9 and 88.2 GFLOPS at 256 and 512 against 64.1 and 73.3 in docs/BENCHMARKS.md, which itself shows 4x-10x for the avx_matmul path (not the packed kernel) against a textbook i-j-p triple loop that walks B with stride N (7.6 to 1.6 GFLOPS from 64 to 256). The N = 64 and N = 128 figures predate commit acb42de (2026-08-07), which sends max(M,N,K) &lt;= 128 to the unpacked single-accumulator sgemm_direct_avx2 (a serial FMA chain over K), and no new numbers were captured. Each packed call above the 128 threshold allocates and zero-fills about 2.1 MB of packing buffers; OpenMP parallelises only the NC = 2048 loop; kernels are built with -march=native -ffast-math (host-specific, NaN/Inf undefined) while the precision tests use a separate non-fast-math build. The GeLU 6-10x is an expectation for non-SVML platforms; measured, the AVX2 tanh approximation equals glibc's SVML-vectorised erff.

Needs AVX2 + FMA (AVX-512 kernel auto-dispatched); educational middle ground between textbook loops and production BLAS; Python bindings via pybind11.

## Maintenance

Active (125 commits, last on 2026-08-10, 15 stars, 5 forks, no issues or releases), Apache-2.0 and copyable as well-commented teaching code, but it is slower than OpenBLAS everywhere, and its documentation and committed baselines disagree with each other.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** Public benchmark code (src/main_bench.cpp, src/bench_stat.cpp) with compiler and flags stated in docs/BENCHMARKS.md (GCC-12, -O3 -march=native -mfma -ffast-math), but the CPU is a virtualised CI runner whose model 'varies by runner', so not A; first-party only, so C. Verdict downgrade because the README's GeLU 6-10x is a projection, not a measurement.
- **Retiered** C to D: Enricher: the README speedups are rounded figures untraceable to any committed table, the committed benchmarks/results/bench_results.json contradicts them (simd_sgemm 213x slower than scalar at 64 and 5.5x slower at 128), the committed gemm_results.json disagrees with docs/BENCHMARKS.md, the N &lt;= 128 figures predate commit acb42de with no re-measurement, and the kernel is slower than single-thread OpenBLAS at every size. No valid measurement supports the claim: C to D.
- **Verifier notes:** Real but weak entry: it beats only a cache-unfriendly naive scalar loop and loses to OpenBLAS everywhere. GeLU 6-10x is projected, not measured (measured 1.02x vs the erff reference), and the README GEMM ratios do not match docs/BENCHMARKS.md (4.1x/6.9x/10.4x). CI VM with no CPU model; Apache-2.0, active (last commit 2026-08-10), 15 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-110 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/README.md>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/kernels/gemm/naive_gemm.hpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/main_bench.cpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/bench_stat.cpp>
  - <https://github.com/Mattral/SIMD-Microkernels-for-ML-Workloads>
  - <https://github.com/Mattral/SIMD-Microkernels-for-ML-Workloads/commits>
- **Sources the enricher read:**
  - <https://github.com/Mattral/SIMD-Microkernels-for-ML-Workloads>
  - <https://github.com/Mattral/SIMD-Microkernels-for-ML-Workloads/commits>
  - <https://github.com/Mattral/SIMD-Microkernels-for-ML-Workloads/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/README.md>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/docs/DESIGN.md>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/docs/ROADMAP.md>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/main_bench.cpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/bench_stat.cpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/kernels/avx_matmul.hpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/kernels/avx_matmul.cpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/kernels/gemm/naive_gemm.hpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/kernels/gemm/avx2_gemm_packed.hpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/kernels/gemm/avx2_gemm_packed.cpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/kernels/gemm/gemm_dispatcher.cpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/kernels/cache_alloc.hpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/kernels/intrinsic_gelu.hpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/kernels/intrinsic_gelu.cpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/kernels/simd_math.hpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/bindings/pybind_entry.cpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/src/dispatch/cpuid.hpp>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/benchmarks/results/bench_results.json>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/benchmarks/results/gemm_results.json>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/benchmarks/results/README.md>
  - <https://raw.githubusercontent.com/Mattral/SIMD-Microkernels-for-ML-Workloads/HEAD/.github/workflows/bench.yml>
  - <https://pypi.org/pypi/simd-ml-microkernels/json>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mattral/simd-microkernels-for-ml-workloads`) · [data/wave13/enrich/raw/github_com_mattral_simd_microkernels_for_ml_workloads.json](../../../data/wave13/enrich/raw/github_com_mattral_simd_microkernels_for_ml_workloads.json) (enrichment confidence 0.6)

</details>
