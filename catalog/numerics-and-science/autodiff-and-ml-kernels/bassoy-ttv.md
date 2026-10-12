# TTV (tlib tensor-times-vector library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `LGPL-3.0` · 🟢 active

> Header-only C++17 mode-q tensor-times-vector product built on BLAS gemv/dot; beat Eigen Tensor, TBLIS and usually TCL in 2019.

| | |
|---|---|
| **Beats** | Eigen Tensor (sequential in-place tensor-times-vector); also TBLIS and TCL |
| **Claimed result** | The README has no speedups in text, only plots. Approximate values read from the README PNG plots (misc/\*_speedup_\*.png), per test case: over Eigen (sequential), about 3x to 300x on symmetric tensors and up to about 900x on asymmetric single-precision tensors; over TBLIS, about 1x to 17x, mostly 2-8x; over TCL, about 0.3x to 35x, so TTV is slower than TCL in some cases. On symmetric single-precision tensors TTV reaches about 20-35 Gflop/s, against up to about 31 for TCL, about 15 for TBLIS and about 8 for Eigen. The paper's abstract, seen only as a search-engine snippet because the paper itself could not be opened, says TTV is on average 6.1x and up to 12.6x faster than TCL's TTGT implementation and reaches 34.8 Gflop/s in single precision. |
| **Workload** | Mode-q tensor-times-vector products for symmetric (order 2-7, 324 cases) and asymmetric (order 2-10, 1296 cases) shapes in single and double precision. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-7900X (10 cores, 20 threads, 3.3 GHz) |
| **Compiler and flags** | GCC 7.3 with -Ofast -march=native -pthread -fopenmp; OpenBLAS 0.2.20 dot/gemv; OpenMP 4.5 |
| **Adoption** | 24 stars |
| **Last commit** | 2025-11-02 |
| **Links** | [repository](https://github.com/bassoy/ttv) · [benchmark](https://github.com/bassoy/ttv#experiments) |

## Verdict

Bassoy's ICCS 2019 paper and the README plots compare TTV (OpenBLAS 0.2.20 gemv/dot, OpenMP, GCC 7.3 -Ofast -march=native) against TCL 0.1.1, TBLIS 1.0.0 and sequential Eigen 3.3.90 on a 10-core Core i9-7900X across 324 symmetric and 1296 asymmetric order-2 to 10 shapes: read off the plots, TTV is mostly 2-8x faster than TBLIS, between 0.3x and 35x of TCL (abstract: 6.1x average, 12.6x maximum over TCL) and peaks near 35 Gflop/s in single precision. The large Eigen ratios (up to about 900x) compare 20 parallel threads with single-threaded Eigen, and the comparison harness is not in the repo.

## Use it when

- Repeated mode-q tensor-times-vector products (for example in higher-order power methods, tensor decompositions or multilinear PCA) on dense, contiguous tensors of order 2 to 10
- Float or double tensors on a multicore x86-64 Linux box where OpenBLAS, MKL or BLIS is already linked
- You must contract in place on first-order (column-major), last-order or permuted layouts without allocating a transposed copy
- You want a small, header-only dependency instead of a full tensor framework, or a numpy-callable TTV via ttvpy

## Skip it when

- General tensor-tensor contractions or tensor-times-matrix: use TCL or TBLIS (the same author's separate bassoy/ttm repo covers tensor-times-matrix)
- Strided views or sparse tensors: elements must be stored contiguously
- Complex or other non-float/double element types where speed matters: the BLAS path only calls sgemv/dgemv, and other types fall back to the built-in loops
- Non-Linux or non-GCC builds: CI runs only g++ on ubuntu-latest, core detection shells out to lscpu, and the two open issues (2023) report link failures and failing MatrixTimesVector tests on macOS/PowerPC
- Applications that set their own BLAS or OpenMP thread counts: the parallel paths reset them globally on each call

## How it is fast

Loops-over-GEMM (LOG): instead of transposing the tensor (the TTGT approach TCL uses), it views contiguous slices or larger subtensors of A in place as matrices and calls the BLAS sgemv/dgemv (or dot) on each, so no copy or extra memory is needed. Loop fusion collapses the outer loops into one, and OpenMP parallelizes across slices or subtensors, with a mode that splits cores between OpenMP threads and BLAS threads; for large tensors it reaches the BLAS gemv's own throughput. Without a BLAS it falls back to its own OpenMP-SIMD gemv loops.

## Compared with alternatives

Pick TTV over TCL when the contraction is specifically tensor-times-vector and you cannot afford TCL's transpose (TTGT) buffers; TCL stays the choice for general contractions and was faster than TTV in a few plotted cases. LIBXSMM and Fastor target small dense GEMM, not tensor-times-vector.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | OpenMP headers (matrix_times_vector.h includes &lt;omp.h&gt; unconditionally); optional BLAS: OpenBLAS (-DUSE_OPENBLAS), Intel MKL (-DUSE_MKL, ILP64 in the shipped mkl.mk) or BLIS (-DUSE_BLIS); googletest for the tests; numpy for ttvpy |
| **Minimum toolchain** | C++17 (if constexpr, inline variables, nested namespaces); tested with GCC only (paper runs: GCC 7.3; CI: current Ubuntu g++) |
| **Platforms** | x86-64 Linux documented and CI-tested; other platforms not documented (open issue reports test failures on macOS PowerPC) |
| **Thread safety** | Not documented. The parallel policies call openblas_set_num_threads / mkl_set_num_threads / bli_thread_set_num_threads, omp_set_nested(true) and set per-thread BLAS counts, all process-wide settings, so concurrent calls from several threads, or other BLAS users in the same process, can interfere. |
| **Drop-in for the baseline** | no |

## Gotchas

- The README and wiki say to compile with -DUSE_INTELBLAS for MKL, but the headers only test USE_MKL; with -DUSE_INTELBLAS the code silently builds the non-BLAS fallback
- The README's policy names (tlib::execution::blas, tlib::slicing::large, tlib::tensor) predate the 2024 move to the tlib::ttv namespace; the code now uses tlib::ttv::execution_policy::par_blas, slicing_policy::subtensor and so on, so README snippets need adapting
- The first parallel call runs popen("lscpu ...") to count physical cores (cached in a function-local static); this spawns a shell, fails quietly where lscpu is absent (it then uses std::thread::hardware_concurrency) and may be unwelcome in sandboxed or setuid processes
- Validation errors (bad mode, shape, layout or stride, null pointers) throw std::runtime_error, so the low-level interface is not usable with exceptions disabled

## Known shortcomings

- Claim not reproducible from the repo: no benchmark harness (test/ has only gtest unit tests, misc/ only PNG plots); ICCS 2019 paper unreachable here (abstract snippet: 6.1x average, 12.6x max over TCL). Plots: Eigen 3-900x is sequential Eigen vs 10-core TTV (not like-for-like); TBLIS 1-17x; TCL 0.3-35x, so TTV is slower than TCL in some cases.
- Wraps OpenBLAS/MKL gemv/dot, so it is not faster than BLAS itself; likely the wrong category (tensor-times-vector contraction, not blas-lapack); LICENSE.txt is LGPL-3.0 while the README badge says GPL.
- README and wiki say to build with -DUSE_INTELBLAS but the code checks only USE_MKL, so that flag silently builds the non-BLAS fallback; complex types never hit BLAS; the first parallel call runs popen("lscpu"); parallel paths reset process-wide BLAS/OpenMP thread counts; Eigen ratios compare 20 threads with Eigen's 1; open #4/#5 link failures and failing tests on macOS/PowerPC.

## Caveats and trade-offs

The repo has no benchmark harness for the TCL/TBLIS/Eigen comparison (test/ holds gtest unit tests only, misc/ holds PNG plots only), so the README plots cannot be reproduced from the repo. Speedups appear only as scatter plots, so the per-case values are approximate readings. In several cases TTV is slower than TCL (plotted speedup below 1). Eigen ran sequentially while TTV ran in parallel on 10 cores/20 threads, which inflates the Eigen ratios; the 100-900x Eigen points are not like for like. TTV calls OpenBLAS/MKL gemv/dot and is not faster than BLAS itself, so this is really a tensor-contraction entry rather than a BLAS replacement. The experiments date from 2019 and use GCC 7.3, OpenBLAS 0.2.20, TCL 0.1.1, TBLIS 1.0.0 and Eigen 3.3.90. LICENSE.txt is LGPL-3.0, while the README badge just says GPL. The verifier could not open the ICCS paper (Springer, iccs-meeting.org and Fraunhofer hosts are blocked).

Covers only the tensor-times-vector contraction (loops-over-GEMV/DOT), not general contractions; needs contiguous storage; relies on a BLAS (OpenBLAS, MKL or BLIS) for peak speed.

## Maintenance

Maintained by a single author (last commit 2025-11-02 added a combined OpenMP/BLAS policy; 24 stars, no releases); LGPL-3.0 header-only code is easy to vendor but carries LGPL obligations, and the README badge wrongly says GPL.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** The measurements come from a peer-reviewed paper (Bassoy, ICCS 2019, Springer LNCS pp. 32-45) that compares TTV with Eigen, TCL and TBLIS; the README repeats its setup (i9-7900X, GCC 7.3, -Ofast -march=native -fopenmp, OpenBLAS 0.2.20) and its plots. Not A, because the harness that runs TCL/TBLIS/Eigen is not public: test/ holds only gtest unit tests, example/ holds interface demos and misc/ holds only PNG plots.
- **Verifier notes:** The repo exists and is not a fork or archived; it has 24 stars, 5 forks, the LGPL-3.0 license (LICENSE.txt) and a last commit on 2025-11-02. The B tier rests on the paper's ICCS 2019 venue and its abstract numbers (6.1x average, 12.6x maximum over TCL), which were seen only through search-engine snippets. The orchestrator might move this entry from blas-lapack to a tensor-contraction category.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bassoy/ttv>
  - <https://github.com/bassoy/ttv/commits>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/README.md>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/misc/symmetric_speedup_single_precision.png>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/misc/symmetric_speedup_double_precision.png>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/misc/nonsymmetric_speedup_single_precision.png>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/misc/symmetric_throughput_single_precision.png>
  - <https://github.com/bassoy/ttv/tree/master/test>
  - <https://github.com/bassoy/ttv/tree/master/test/src>
  - <https://github.com/bassoy/ttv/tree/master/misc>
  - <https://github.com/bassoy/ttv/tree/master/example>
- **Sources the enricher read:**
  - <https://github.com/bassoy/ttv>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/README.md>
  - <https://github.com/bassoy/ttv/tree/master/include/tlib>
  - <https://github.com/bassoy/ttv/tree/master/include/tlib/detail>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/include/tlib/ttv.h>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/include/tlib/detail/tags.h>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/include/tlib/detail/tensor_times_vector.h>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/include/tlib/detail/matrix_times_vector.h>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/.github/workflows/test.yml>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/openblas.mk>
  - <https://raw.githubusercontent.com/bassoy/ttv/HEAD/mkl.mk>
  - <https://github.com/bassoy/ttv/tree/master/ttvpy>
  - <https://github.com/bassoy/ttv/wiki>
  - <https://github.com/bassoy/ttv/issues?q=is%3Aissue>
  - <https://github.com/bassoy/ttv/commits/master>
  - <https://github.com/bassoy/ttm>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/bassoy/ttv`) · [data/wave8/enrich/raw/github_com_bassoy_ttv.json](../../../data/wave8/enrich/raw/github_com_bassoy_ttv.json) (enrichment confidence 0.75)

</details>
