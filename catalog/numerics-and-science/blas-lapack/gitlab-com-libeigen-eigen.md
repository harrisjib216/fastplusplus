# Eigen

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MPL-2.0` · 🟢 active

> Header-only C++ template library for dense/sparse linear algebra; beats OpenBLAS at small-to-mid sizes without linking BLAS.

| | |
|---|---|
| **Beats** | OpenBLAS |
| **Claimed result** | The page reports the geometric mean of Eigen/OpenBLAS rate ratios for square shapes in each size band (above 1 means Eigen is faster). Double-precision bands are n&lt;=16 / 24-128 / 192-1024 / 1536-16384. Results: GEMM 1.11 / 0.85 / 1.07 / 0.94. GEMV 2.23 / 1.63 / 1.08 / 1.07. DOT 4.90 / 2.44 / 1.10 / 1.03. TRSM 1.48 / 3.60 / 2.19 / 1.23. POTRF 1.38 / 1.25 / 1.50 / 1.25. SYEV 1.36 / 1.77 / 2.33 / 1.79. Eigen is slower on GEEV (0.45 at 192-1024) and on GESDD (0.60 / 0.80 / 0.90 at 24-16384). Compared with oneMKL, Eigen wins mostly at small sizes. At large sizes it is often slower (double GEMM 0.93, SYEV 0.37, GEEV 0.41 at 192-1024). A companion Zen 5 page (WSL2) shows double GEMM against OpenBLAS at 1.28 / 0.95 / 1.30 / 1.21. |
| **Workload** | Single-threaded float and double BLAS operations (AXPY, DOT, GEMV, GEMM, TRSM, SYRK) and LAPACK operations (POTRF, GETRF, GEQRF, SYEV, GESDD, GEEV), measured over square and rectangular shapes. The Eigen arm uses no external BLAS. It is compared with OpenBLAS 0.3.26 (one thread, bundled LAPACK), Intel oneMKL 2025.3 (sequential) and BLIS 2.1 (BLAS only). Method: Google Benchmark 1.8.3, 10 repetitions of at least 0.2 s each, median GFLOP/s per cell, 874 operation-shape cells. |
| **Metric** | other |
| **Hardware** | Intel Xeon Gold 6444Y, one socket, 16 cores / 32 threads, bare metal. Benchmark pinned to one logical CPU (single-threaded, AVX-512). Ubuntu 24.04.5 LTS, Linux 6.17.0-35-generic. Performance governor; frequency not locked. |
| **Compiler and flags** | GCC 13.3.0, -O3 -DNDEBUG -mavx512dq -mfma, C++17; Eigen upstream master ab4f7316d with no external BLAS and no OpenMP |
| **Adoption** | 1,190 GitLab stars (GitLab project created 2019-11-21); foundational dependency of ROS, TensorFlow, Ceres Solver, PCL, OpenCV, g2o, Blender, and many other numerical/robotics/vision projects |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://gitlab.com/libeigen/eigen) · [benchmark](https://libeigen.gitlab.io/benchmarks/2026-09-xeon-gold-6444y-blas-lapack-avx512/) |

## Verdict

On an Intel Xeon Gold 6444Y (GCC 13.3.0, -O3 -DNDEBUG -mavx512dq -mfma, single-threaded), Eigen's own kernels beat OpenBLAS 0.3.26's geometric-mean GFLOP/s on GEMV, DOT, TRSM, POTRF and SYEV across most size bands (roughly 1.1-4.9x), are near parity on large GEMM, and lose on GEEV and GESDD; against Intel oneMKL 2025.3, Eigen is generally slower at large sizes. The harness (Google Benchmark 1.8.3, median of 10 reps) is public but still an unmerged GitLab merge request (!2903), and frequency was not locked during the run.

## Use it when

- Small and medium dense ops (roughly n&lt;=1024) where OpenBLAS's dispatch/call overhead dominates -- GEMV and DOT measured 1.1-4.9x faster than OpenBLAS here
- You want a header-only dependency with no external BLAS/LAPACK to build, package, or version-pin
- Fixed-size or compile-time-sized linear algebra (small transforms, small solvers) where Eigen's unrolled kernels apply
- TRSM, POTRF, SYEV workloads at small/mid size, where Eigen beat OpenBLAS by 1.25-3.6x per this benchmark
- C++ codebases that want expression-template ergonomics instead of raw BLAS call signatures

## Skip it when

- Very large dense GEMM/SYRK (n in the 1500+ range) where Eigen is roughly at parity with OpenBLAS and often slower than oneMKL
- GEEV (nonsymmetric eigenvalues) -- measured at 0.45x OpenBLAS at 192-1024, and well behind oneMKL at large sizes
- GESDD (SVD) at mid-to-large sizes -- measured 0.6-0.9x OpenBLAS
- Large-scale multi-threaded numerics -- this benchmark and Eigen's own kernels are single-threaded; OpenMP only parallelizes some ops (dense GEMM, PartialPivLU, a few iterative sparse solvers), not the full LAPACK surface
- Storing fixed-size Eigen objects in STL containers or passing them by value without alignment care -- triggers runtime alignment assertions on SIMD builds

## How it is fast

Expression templates fuse chained operations into a single loop at compile time, avoiding temporaries. Eigen's own GEMM kernel does three-level cache blocking -- mc x kc panels packed for L2/L3, mr x kc micro-panels kept in L1, and a register-blocked micro-kernel -- the same family of technique GotoBLAS/BLIS use, confirmed in the header comment of GeneralBlockPanelKernel.h. Kernels are explicitly SIMD-vectorized (SSE/AVX/AVX-512/NEON/etc.), and small fixed-size matrices get compile-time loop unrolling that skips packing overhead entirely, which is why Eigen's edge over OpenBLAS is largest at small sizes (DOT 4.9x, GEMV 2.2x at n&lt;=16) and shrinks or reverses as size grows.

## Compared with alternatives

no siblings catalogued yet

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (STL only); optional external BLAS/LAPACK backend for large-matrix offload |
| **Minimum toolchain** | C++14 (target_compile_features cxx_std_14 in CMakeLists.txt); CMake 3.18+ only needed for the optional install/test build, not for using the headers |
| **Platforms** | x86-64 (SSE2 baseline, AVX/AVX2/AVX-512 optional), aarch64/ARM NEON, PowerPC Altivec/VSX, MIPS MSA; this benchmark ran on AVX-512 |
| **Thread safety** | Safe across threads if Eigen::initParallel() is called before spawning them (optional on C++11 compilers with thread-safe static init, per TopicMultiThreading); Random()/setRandom() are explicitly not thread-safe or reentrant |
| **Drop-in for the baseline** | partial -- not ABI/API compatible with BLAS/LAPACK call signatures; this benchmark compares Eigen's native API against a separate OpenBLAS binary, it is not a relink-only swap |

## Gotchas

- Fixed-size vectorizable types (Vector4d, Matrix4d, Quaternionf, etc.) assert at runtime if misaligned -- avoid storing them by value in STL containers or passing by value without EIGEN_MAKE_ALIGNED_OPERATOR_NEW
- OpenMP thread count should match physical cores, not logical/hyperthreads -- oversubscription slows things down since Eigen's kernels already saturate a core
- Heavy expression-template usage increases compile times
- For very large dense problems, Eigen's own docs and this benchmark both point toward linking an external BLAS/LAPACK backend instead of relying solely on Eigen's kernels

## Caveats and trade-offs

The Eigen team published this benchmark on its own site, and the harness is still in an open (unmerged) merge request, !2903. Results are mixed. Against OpenBLAS, Eigen is faster at small and medium sizes for level-1/2 BLAS and for several LAPACK operations (TRSM, POTRF, SYEV). For large GEMM and SYRK it is roughly at parity or slightly slower, and it is slower on GEEV and on mid-size GESDD. Against Intel oneMKL, Eigen is generally slower at large sizes. All measurements are single-threaded with frequency not locked. The older eigen.tuxfamily.org Benchmark page (BTL harness, March 2011) is now marked as a historical record.

Header-only template library, so heavy expression-template usage can increase compile times; built-in kernels favor small/fixed-size matrices (avoiding BLAS call overhead) while very large dense problems are the case where linking an external BLAS/LAPACK backend is recommended instead of relying solely on Eigen's own kernels.

## Maintenance

Actively maintained (last commit 2026-09-23) with a large downstream user base (ROS, TensorFlow, Ceres Solver, OpenCV, Blender); MPL-2.0, header-only, trivial to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification D, tier now A.
- **Tier reason:** Upgraded D to A: Eigen's official site now has a benchmark page (dated 2026-09-21) that compares Eigen with OpenBLAS 0.3.26, Intel oneMKL 2025.3 and BLIS 2.1. It states the CPU (Intel Xeon Gold 6444Y), the compiler and flags (GCC 13.3.0, -O3 -DNDEBUG -mavx512dq -mfma) and the method (Google Benchmark 1.8.3, 10 repetitions, median). The harness code is public in Eigen merge request !2903 under benchmarks/comparison/ (for example bench_gemm_compare.cpp and run.py).
- **Verifier notes:** The published page loads at libeigen.gitlab.io. Its source is public at gitlab.com/libeigen/libeigen.gitlab.io under content/en/benchmarks/, with 5 September 2026 pages (Xeon, Zen 5, Apple M4). The metric field ('other') cannot be corrected here; the page measures throughput in GFLOP/s. The GitLab API confirmed license MPL-2.0, not archived, and a last commit on 2026-09-23 (PDT). The record's claim that Eigen 'moved off GitHub' is not supported, so I removed it.
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** Eigen 5.0.1 reached 193.1 GFLOP/s on f32 matmul N=1024 (91% of the host's measured single-core FMA peak of 212.2, 1.42x a hand-written xsimd kernel, 1.85x Blaze), but lost fixed 4x4 multiplies to a naive triple loop (5.87 vs 3.20 ns, naive 1.83x) and 3x3 to hand-rolled xsimd (5.59 vs 2.26 ns, 2.5x). At N=64 hand-rolled xsimd also beat it 1.41x (187.4 vs 133.2 GFLOP/s), and the naive 4x4 win is gcc-specific (clang 18 leaves that loop scalar and Eigen wins there). (developer source, private repo; selection harness in docs/linear-algebra.md, gcc 13 -O3 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party); Built without -march=native, Eigen fell from 193.1 to 34.6 GFLOP/s on f32 matmul N=1024 (5.6x loss), while OpenBLAS with runtime CPU dispatch went from 575.9 to 569.2. sizeof(struct{Eigen::Matrix4f; char;}) is 80/96/128 bytes under SSE2/AVX2/AVX-512, so translation units built with different arch flags silently disagree on layout. (developer source, private repo; selection harness in docs/linear-algebra.md, gcc 13, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://gitlab.com/libeigen/eigen>
  - <https://gitlab.com/api/v4/projects/libeigen%2Feigen>
  - <https://gitlab.com/api/v4/projects/libeigen%2Feigen/repository/commits?per_page=1>
  - <https://eigen.tuxfamily.org/index.php?title=Benchmark>
  - <https://libeigen.gitlab.io/index.php?title=Benchmark>
  - <https://libeigen.gitlab.io/benchmarks/2026-09-xeon-gold-6444y-blas-lapack-avx512/>
  - <https://gitlab.com/libeigen/libeigen.gitlab.io/-/raw/main/content/en/benchmarks/2026-09-xeon-gold-6444y-blas-lapack-avx512.md>
  - <https://gitlab.com/libeigen/libeigen.gitlab.io/-/raw/main/content/en/benchmarks/2026-09-zen5-blas-lapack.md>
  - <https://gitlab.com/libeigen/libeigen.gitlab.io/-/raw/main/content/en/benchmarks/benchmark.md>
  - <https://gitlab.com/libeigen/eigen/-/merge_requests/2903>
- **Sources the enricher read:**
  - <https://gitlab.com/libeigen/eigen>
  - <https://gitlab.com/libeigen/eigen/-/raw/master/README.md>
  - <https://gitlab.com/libeigen/eigen/-/raw/master/INSTALL>
  - <https://gitlab.com/libeigen/eigen/-/raw/master/CMakeLists.txt>
  - <https://gitlab.com/libeigen/eigen/-/raw/master/Eigen/src/Core/products/GeneralBlockPanelKernel.h>
  - <https://libeigen.gitlab.io/benchmarks/2026-09-xeon-gold-6444y-blas-lapack-avx512/>
  - <https://libeigen.gitlab.io/eigen/docs-nightly/TopicMultiThreading.html>
  - <https://libeigen.gitlab.io/eigen/docs-nightly/TopicUnalignedArrayAssert.html>
  - <https://gitlab.com/api/v4/projects/libeigen%2Feigen/issues?labels=Bug&state=opened&per_page=20&order_by=updated_at>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://gitlab.com/libeigen/eigen`) · [data/wave0-seed/enrich/raw/gitlab_com_libeigen_eigen.json](../../../data/wave0-seed/enrich/raw/gitlab_com_libeigen_eigen.json) (enrichment confidence 0.6)

</details>
