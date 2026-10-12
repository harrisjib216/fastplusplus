# fast-matmul (Benson and Ballard)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> Code-generated Strassen-like matrix multiplication in C++ that beat sequential Intel MKL dgemm by 1.1-1.2x on large matrices.

| | |
|---|---|
| **Beats** | Intel MKL dgemm |
| **Claimed result** | Derived from page data (median of five trials, sequential, ms): Strassen with 2 recursion levels 4836 ms vs MKL 5361 ms at N=4000 (1.11x) and 15790 vs 18075 ms at N=6000 (1.14x); 3 levels 15561 ms at N=6000 (1.16x); 1.04x at N=2000. Best exact-algorithm ratios in the file are 1.19x (&lt;4,2,3&gt; one level, N=1000) and 1.17x (&lt;3,2,3&gt; two levels, N=7500); the approximate Bini algorithm reaches 1.21x. Exact algorithms beat MKL in 329 of 756 (algorithm, N) data points. The PPoPP 2015 paper (cited in README) reports better performance than MKL dgemm; the paper itself was not opened here. |
| **Workload** | Sequential square dgemm (N = 1000 to 7500) comparing MKL against Strassen and other fast matrix multiplication algorithms with 1 to 3 recursion levels; run times in ms, median of five trials, data checked into data/all_sequential_algs/square.all.big. |
| **Metric** | throughput |
| **Hardware** | NERSC Edison (data/README.md: 'Performance data collected on Edison'); data/all_sequential_algs/README.md says that because of Intel Turbo Boost the performance should be read relative to a 3.2 GHz processor instead of a 2.4 GHz processor; CPU model not stated in the files read |
| **Compiler and flags** | Intel icpc (version not stated; Edison config loads gcc/4.8.0 module) with -O3 -std=c++11 -DNDEBUG -DBLAS_POST, sequential mode, Intel MKL from composer_xe_2013.5.192 (Makefile and make.incs/make.inc.edison) |
| **Adoption** | 32 stars, 18 forks, 554 commits |
| **Last commit** | 2021-07-06 |
| **Links** | [repository](https://github.com/arbenson/fast-matmul) · [benchmark](https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/data/all_sequential_algs/square.all.big) |

## Verdict

Sequential median-of-five timings checked into data/all_sequential_algs/square.all.big (NERSC Edison, icpc -O3, MKL from composer_xe 2013) show two-level Strassen at 4836 ms vs MKL dgemm 5361 ms for N=4000 (1.11x) and 15790 vs 18075 ms at N=6000 (1.14x), with the best exact algorithms reaching 1.17-1.19x; approximate Bini reaches 1.21x. The PPoPP 2015 paper itself could not be opened here (arxiv.org and dl.acm.org blocked); its abstract, seen only in a search snippet, says novel fast algorithms 'can significantly outperform vendor implementations of the classical algorithm and Strassen's fast algorithm on modest problem sizes and shapes'.

## Use it when

- Large dense float/double products (N of about 2000 and above) where 10-20% off the GEMM time matters and you control the call site.
- Rectangular shapes that match a specific fast algorithm's base case (for example &lt;4,2,3&gt; or &lt;3,2,3&gt;); the paper's point is that the best algorithm depends on shape as well as size.
- Research or teaching on fast matrix multiplication: comparing dozens of algorithms, recursion depths and addition schemes with ready-made benchmarks and stability tests.
- Workloads that tolerate approximate products (for example neural-network training), using the APA/Bini algorithms added in 2021 (ICPP-W 2021).

## Skip it when

- Small or medium matrices: in the checked-in sequential data, exact algorithms beat MKL in only 329 of 756 points, mostly at N of about 2000 and above, and the extra additions dominate below that.
- Code that needs tight error bounds: exact algorithms give relative errors around 1e-14 to 1e-15 (README), errors grow with each recursion level, and the approximate algorithms are lossier still.
- As a general BLAS: FastMatmul has no transpose options, there are no complex types, no batched or level-2 routines, and you must pick algorithm and depth by hand.
- When you need a measured win on current hardware: the evidence is a 2013 MKL on NERSC Edison, and a modern MKL or OpenBLAS may move the crossover or erase the gain.
- Production use expecting maintenance: core code dates from 2014-2017, the last commit was 2021-07-06, and there is no CMake, packaging or CI.

## How it is fast

Each recursion level splits A, B and C into blocks and forms fewer block products than the classical algorithm (Strassen: 7 instead of 8 for 2x2 blocks; &lt;4,2,3&gt;: 20 instead of 24), paying with extra matrix additions; at the leaves it calls the vendor dgemm/sgemm (MKL). The generator applies common-subexpression elimination and offers three addition schemes (write-once, streaming, pairwise), and odd sizes are handled by dynamic peeling. Shared-memory parallel builds choose DFS, BFS or hybrid task scheduling at compile time through OpenMP.

## Compared with alternatives

Pick fast-matmul over fmm-gen when you want fast algorithms layered on a tuned vendor dgemm (MKL) with checked-in timings against that dgemm; fmm-gen fuses the additions into BLIS-style packing with its own AVX kernel instead. For tensor contractions tblis-strassen is the analogue, and for ordinary GEMM speed any tuned BLAS sibling is the simpler choice.

## Integration

| | |
|---|---|
| **Form** | header-only (generated .hpp in algorithms/ plus linalg/ and util/ headers); Python generator for new algorithms |
| **Dependencies** | a Fortran-ABI BLAS providing dgemm/sgemm (README requires Intel MKL; parallel builds call mkl_set_num_threads_local and mkl_set_dynamic); OpenMP for parallel modes |
| **Minimum toolchain** | C++11 with OpenMP; tested mainly with Intel icpc (Edison config: composer_xe 2013, gcc/4.8.0 module); README warns g++ OpenMP task handling can crash the hybrid parallel mode |
| **Platforms** | x86-64 Linux with Intel MKL as tested; other platforms not documented |
| **Thread safety** | not documented; parallel builds call omp_set_nested(1) and change MKL dynamic/thread-local thread settings, which affects the rest of the program |
| **Drop-in for the baseline** | no |

## Gotchas

- FastMatmul takes non-const references, sets a multiplier on A as a side effect, and returns its own elapsed time in milliseconds.
- Dimensions, strides and the allocation size m\*n are plain int, so very large matrices (more than 2^31 elements) overflow.
- The parallel scheme (DFS, BFS, hybrid) is a compile-time define (_PARALLEL_=1/2/3), and sequential versus parallel is chosen in the make include file, not at run time.
- The x argument (default 1e-8) is the approximation parameter used by the approximate algorithms (for example Bini's); exact algorithms ignore it.

## Known shortcomings

- int dimensions and allocation sizes overflow past 2^31 elements; parallel mode changes global OpenMP nesting and MKL thread settings.

## Caveats and trade-offs

The 1.11-1.19x figures are derived from raw timing files and exclude the approximate (Bini) algorithm, which is faster still but numerically lossy; some rows in the data are noisy (for example one-level Strassen at N=1000 takes 405.8 ms vs 108.2 ms for MKL). Exact algorithms win in fewer than half of the data points, and the speedup is mainly at N of about 2000 and above. The baseline is a 2013 MKL on a 2014-era supercomputer node, so the ratio against current MKL on modern CPUs is unknown. The paper itself (arXiv 1409.2908) could not be opened here (arxiv.org blocked); the paper claim is from the README citation and search results. Last commit 2021-07-06 (APA algorithms added); core code from 2014-2017.

Code-generated implementations of Strassen, Bini (approximate) and many other fast algorithms for sequential and shared-memory parallel use, calling MKL for base cases; requires MKL. Fast algorithms have weaker numerical stability (README reports errors about 1e-14 to 1e-15 for exact algorithms and larger for approximate ones) and only win for large matrices.

## Maintenance

Abandoned research code (last commit 2021-07-06, core from 2014-2017) under BSD-2-Clause (Sandia); header-only and small enough to vendor, but re-benchmark the crossover against your BLAS before relying on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed PPoPP 2015 paper (cited in README, confirmed by search results) with its raw timing data checked in; data file times MKL dgemm against Strassen and other exact fast algorithms on Edison. Benchmark code and -O3 flags are public, but the icpc version and CPU model are not stated in the repo files read, so not A.
- **Verifier notes:** All record numbers match square.all.big exactly. The Turbo Boost note lives in data/all_sequential_algs/README.md, not data/README.md as the record said. BSD-2-Clause (Sandia), 32 stars, last commit 2021-07-06 confirmed (abandoned).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/data/all_sequential_algs/square.all.big>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/data/README.md>
  - <https://github.com/arbenson/fast-matmul/tree/master/data/all_sequential_algs>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/README.md>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/Makefile>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/make.incs/make.inc.linux>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/make.incs/make.inc.edison>
  - <https://github.com/arbenson/fast-matmul>
  - <https://github.com/arbenson/fast-matmul/commits>
- **Sources the enricher read:**
  - <https://github.com/arbenson/fast-matmul>
  - <https://github.com/arbenson/fast-matmul/commits/master>
  - <https://github.com/arbenson/fast-matmul/tree/master/codegen>
  - <https://github.com/arbenson/fast-matmul/tree/master/linalg>
  - <https://github.com/arbenson/fast-matmul/tree/master/algorithms>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/README.md>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/Makefile>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/make.incs/make.inc.linux>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/make.incs/make.inc.edison>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/data/README.md>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/data/all_sequential_algs/README.md>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/data/all_sequential_algs/square.all.big>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/codegen/gen.py>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/codegen/gen_all_algorithms.sh>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/examples/strassen.cpp>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/examples/fast433.cpp>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/linalg/linalg.hpp>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/linalg/blas_wrap.hpp>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/algorithms/strassen.hpp>
  - <https://raw.githubusercontent.com/arbenson/fast-matmul/HEAD/algorithms/bini322_10_52_approx.hpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/arbenson/fast-matmul`) · [data/wave8/enrich/raw/github_com_arbenson_fast_matmul.json](../../../data/wave8/enrich/raw/github_com_arbenson_fast_matmul.json) (enrichment confidence 0.75)

</details>
