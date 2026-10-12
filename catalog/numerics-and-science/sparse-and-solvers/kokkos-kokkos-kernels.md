# Kokkos Kernels SpGEMM (KKSPGEMM / KKMEM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> Portable Kokkos SpGEMM (hash-accumulator KKSPGEMM) that beat CUDA 8 cuSPARSE and MKL 18 sparse multiply in 2018 tests.

| | |
|---|---|
| **Beats** | cuSPARSE SpGEMM (CUDA 8.0.44) on P100; Intel MKL sparse-sparse multiply (MKL-INS, MKL7, MKL8 variants; intel-18.0.128) on Knights Landing |
| **Claimed result** | All figures derived from page data (I parsed the xlsx tables linked from the SpGEMM_Benchmarks wiki page, skipping their summary rows; ratio = baseline time / KKSPGEMM time per matrix, then geometric mean over matrices where both ran). P100: KKSPGEMM faster than cuSPARSE on 75 of 81 multiplications, geomean 3.61x (the table's own geomean row shows 0.441 s vs 0.122 s); faster than viennaCL CUDA on 62 of 72, geomean 1.95x; but NOT faster than Nsparse (faster on only 28 of 77, geomean ratio 0.92x). KNL flat-DDR: versus MKL-INS 1.25x (faster on 63 of 83), MKL7 1.79x (75 of 83), MKL8 2.95x (72 of 78). KNL cache mode: MKL-INS 1.19x (56 of 83), MKL7 2.25x (80 of 83), MKL8 3.75x (77 of 78). Power8 OpenMP versus viennaCL: 2.79x (78 of 83). |
| **Workload** | Sparse matrix-matrix multiplication (symbolic plus numeric phases, 'NoReuse' case) on 81-83 SuiteSparse/UFL multiplications (mostly A\*A); best time over thread counts per method; Kokkos 2.50 / Kokkos Kernels 2.60; the wiki ties the setup to the Deveci et al. paper 'Multi-threaded Sparse Matrix-Matrix Multiplication for Many-Core and GPU Architectures'. |
| **Metric** | latency |
| **Hardware** | NVIDIA Tesla P100-SXM2-16GB (host Power8, machine 'White'); Intel Knights Landing 68-core nodes (machine 'Bowman', up to 256 threads, quadrant mode); Power8 for the viennaCL comparison. Exact CPU SKUs not stated. |
| **Compiler and flags** | P100 runs: nvcc_wrapper with gcc 5.4.0 and CUDA 8.0.44, CXXFLAGS='-Wall -pedantic -Werror -O3 -g -Wshadow -Wsign-compare -Wignored-qualifiers -Wempty-body -Wclobbered -Wuninitialized', KOKKOS_ARCHS=Pascal60,Power8, KOKKOSKERNELS_TPLS=cusparse, eti-only, double/int; KNL runs: icpc from module intel/compilers/18.0.128 (the SpGEMM page names MKL intel-18.0.128) with the same CXXFLAGS, KOKKOS_ARCHS=KNL, MKL TPL; Power8 runs: g++ 5.4.0, same CXXFLAGS, KOKKOS_ARCHS=Power8. OMP_PROC_BIND=spread, OMP_PLACES=threads; 6 runs with the first discarded as warm-up. |
| **Adoption** | 403 stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/kokkos/kokkos-kernels) · [benchmark](https://raw.githubusercontent.com/wiki/kokkos/kokkos-kernels/SpGEMM_Benchmarks.md) |

## Verdict

2018 wiki data (Kokkos 2.50 / Kokkos Kernels 2.60, symbolic plus numeric, 81-83 SuiteSparse products, best time over thread counts). On a Tesla P100 with CUDA 8.0.44 and gcc 5.4, KKSPGEMM beat cuSPARSE by a 3.61x geomean (faster on 75 of 81) but lost to Nsparse (0.92x). On 68-core KNL with icpc and MKL 18.0.128 it beat MKL by 1.19-1.25x (inspector-executor) and 1.79-3.75x (two-phase variants), and on Power8 it beat ViennaCL OpenMP by 2.79x; all ratios were derived from the linked xlsx tables.

## Use it when

- You need one SpGEMM code path across OpenMP CPUs and NVIDIA, AMD (HIP) or Intel (SYCL) GPUs instead of maintaining cuSPARSE, rocSPARSE and MKL calls separately.
- Repeated products with fixed sparsity and changing values, such as algebraic multigrid setup (A\*P, R\*AP): run symbolic once and reuse the handle for numeric.
- Your code already uses Kokkos or Trilinos (Tpetra builds on Kokkos Kernels), so the dependency is already paid for.
- Many-core CPUs where vendor sparse-sparse multiply is weak: in the 2018 KNL runs it beat MKL 18's two-phase variants by 1.8-3.75x geomean.
- You also want the graph kernels that share the machinery (graph coloring, triangle counting, Gauss-Seidel with coloring).

## Skip it when

- Peak CUDA-only SpGEMM throughput: the repo's own 2018 P100 tables put Nsparse ahead (KKSPGEMM 0.92x geomean, faster on 28 of 77), and the spECK paper (PPoPP '20, search snippet only) found KokkosKernels best on 3 of 2,263 matrices, at 2730% of the best method's time on average; GPU-specific codes like spECK or OpSparse are faster.
- You need current numbers: the only published comparison is from 2018 (CUDA 8 cuSPARSE, MKL 18.0, P100, KNL), and today's perf_test driver no longer runs the vendor baselines.
- Small or one-off products in a code without Kokkos: you must build Kokkos plus Kokkos Kernels with explicit template instantiation, which takes a long time and now requires C++20.
- Distributed-memory SpGEMM: the kernels are local to one process; MPI distribution has to come from a layer such as Tpetra.
- Very large graphs on some CPU backends: issue #2291 reports a numeric-phase segfault on uk-2005 (39.5M rows, OpenMP, aarch64), and issue #1542 (open) reports openmp.sparse_spgemm hanging with GCC 10 and ARMPL 21.

## How it is fast

Row-wise (Gustavson) two-phase SpGEMM. The symbolic phase compresses B's column indices into bit sets so structure counting touches fewer words. The numeric phase accumulates each output row in a two-level hash map: level 1 in team scratch (GPU shared) memory, level 2 in chunks from a pre-allocated uniform memory pool in global memory. On CPUs it switches to dense accumulators when the problem looks dense. Team and vector sizes are chosen from a flop estimate per row, and one templated source covers the CPU and GPU backends (the Deveci et al. 'Multi-threaded Sparse Matrix-Matrix Multiplication for Many-Core and GPU Architectures' design).

## Compared with alternatives

Pick Kokkos Kernels over spECK, OpSparse or TileSpGEMM when you need a maintained, vendor-portable library that also runs on CPUs and AMD or Intel GPUs and supports symbolic reuse. Pick those CUDA-only research codes when raw NVIDIA SpGEMM speed is the only goal; their papers report wins over cuSPARSE and nsparse, which Kokkos Kernels does not beat.

## Integration

| | |
|---|---|
| **Form** | static or shared lib (CMake or Spack), with explicit template instantiation (ETI) for the scalar, ordinal, offset and device types chosen at configure time |
| **Dependencies** | Kokkos core (current develop requires Kokkos 5.1.1+); optional TPLs cuSPARSE, rocSPARSE, MKL, cuBLAS, BLAS/LAPACK, MAGMA |
| **Minimum toolchain** | C++20, inherited from Kokkos 5 (Kokkos changelog: GCC 10.4+ for C++20; CMake 3.25.2 for CUDA C++20); Kokkos Kernels' own CMake minimum is 3.16 |
| **Platforms** | any Kokkos backend: Serial, OpenMP, Threads, CUDA, HIP, SYCL; x86-64, aarch64, Power, NVIDIA, AMD and Intel GPUs |
| **Thread safety** | not documented for SpGEMM; each handle holds state for one A\*B sparsity pattern |
| **Drop-in for the baseline** | no |

## Gotchas

- The handle's default SPGEMM_DEFAULT dispatches to the vendor TPL (cuSPARSE on CUDA, rocSPARSE on HIP, MKL) when that TPL is enabled at build time, so the default path can be the baseline itself. Request SPGEMM_KK to get the native kernel that was benchmarked; the README says KKMEM is outdated and KKSPGEMM is the default native algorithm. Issue #3153 (closed July 2026) was a regression in this routing.
- A handle cannot be reused for a product with a different sparsity pattern; spgemm_symbolic throws if the rowptrs or entries of A or B differ from the first call.
- On GPUs the level-2 hash pool is capped at half of the free device memory and rounded down to a power-of-two number of chunks, so on a nearly full device teams share chunks and contend.
- Correctness reports exist on less-tested backends: wrong entries with HIP at -O0 on MI50 (#2083, closed), a hang on tiny matrices with SYCL (#1668, open), and a float unit-test failure on serial and OpenMP (#2232, closed).

## Known shortcomings

- Tier A rests on the 2018-era P100 vs cuSPARSE (CUDA 8.0.44) SpGEMM tables; the MKL 18.0.128 KNL rows state no CPU SKU, and the P100 comparison with Nsparse is 0.92x overall (28 of 77 matrices won). Compiler on the configure page is Intel 18.0.128, not 18.2.199 as the record said (corrected).
- The handle default SPGEMM_DEFAULT dispatches to cuSPARSE, rocSPARSE or MKL when the TPL is enabled, so a default build may run the baseline; SPGEMM_KK must be requested explicitly. Open issues #1542 (OpenMP hang with GCC 10 and ARMPL 21), #1668 (SYCL hang on a tiny matrix), #2291 (segfault on uk-2005, OpenMP aarch64). Needs C++20 via Kokkos 5.1.1+. The spECK PPoPP '20 paper (snippet only, tugraz.at blocked) found KokkosKernels best on only 3 of 2,263 matrices at 2730% of the best time on average: an independent counter-benchmark.

## Caveats and trade-offs

Results are from 2018 (Kokkos 2.50, Kokkos Kernels 2.60, CUDA 8 cuSPARSE, MKL 18.0, P100 and KNL hardware); modern cuSPARSE/MKL SpGEMM may differ. On P100 KKSPGEMM is on average slower than Nsparse (v1.2): faster on only 28 of 77 multiplications, geomean 0.92x (derived from page data). None of the baselines is in the catalog's listed set (SuiteSparse, Eigen sparse, PETSc). Per-matrix times are best over thread counts (32-256), and MKL-INS times exclude Trilinos-style post-processing ('Actual DOUBLE MKL SPMM Time Without Free'), while MKL7/MKL8 exclude 1-based conversion. KNL CPU SKU is not given (only '68 cores', quadrant mode), Power8 SKU not given; the P100 GPU model is stated in the logged output. The current perf_test driver no longer offers the cuSPARSE/MKL/viennaCL algorithm options; reproducing needs the 2.6.00-era tag. The wiki is marked deprecated in favour of kokkos.org docs. The P100 xlsx sheet is named 'Power8' internally but holds the P100 columns (KKSPGEMM, KKMEM, KKLP, cuSPARSE, Nsparse, viennaCL). The wiki SpMV page compares only against Kokkos Kernels' own reference, so SpMV carries no incumbent comparison. [retier] Counter-evidence, snippet-only (paper not opened; tugraz.at, dl.acm.org and researchgate are egress-blocked): Parger, Winter, Mlakar and Steinberger, 'spECK: Accelerating GPU Sparse Matrix-Matrix Multiplication through Lightweight Analysis', PPoPP '20, compared six GPU SpGEMM implementations on 2263 SuiteSparse matrices. Per a search snippet, KokkosKernels took 2730% of the fastest approach's time on average. The 'best on 3 matrices' count, the GPU model, the CUDA version and whether Kokkos Kernels' default KKMEM or another SpGEMM variant was timed are not verified. The GPUPeople/spECK README says the code targets CUDA 10.1/10.2/11.0, which places the measurement on a newer CUDA and cuSPARSE than the 2018 CUDA 8 tables.

Templated C++ on top of Kokkos (needs the Kokkos library, explicit template instantiation 'eti-only' builds); one source targets OpenMP, CUDA and other Kokkos backends instead of hand-tuned vendor code. Also wraps cuSPARSE, MKL, cuBLAS and MAGMA as optional TPLs. Covers BLAS, sparse BLAS, graph (coloring, triangle counting), Gauss-Seidel and batched kernels. Performance depends on the Kokkos backend and architecture flags chosen at build time.

## Maintenance

Actively maintained (last commit 2026-10-01; release 5.2.0, which needs Kokkos 5.1.1+), Apache-2.0 WITH LLVM-exception, 403 stars, used under Trilinos; the SpGEMM benchmark wiki is deprecated and reproducing it needs the 2.6.00-era tag.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The SpGEMM_Benchmarks wiki links raw per-matrix tables (xlsx) against cuSPARSE (CUDA 8.0.44), MKL 18.0.128 and viennaCL 1.7.1; the benchmark driver is public (perf_test/sparse/KokkosSparse_spgemm.cpp at tag 2.6.00 exposes --algorithm CUSPARSE|MKL|MKL2|VIENNA), and the configure pages give compilers, full CXXFLAGS, run procedure and the GPU model (Tesla P100-SXM2-16GB). I re-derived every ratio in claimed_speedup from the xlsx tables and they match exactly.
- **Verifier notes:** All ratios (P100 cuSPARSE 3.61x on 75/81, viennaCL 1.95x on 62/72, Nsparse 0.92x on 28/77; KNL-DDR MKL-INS 1.25x, MKL7 1.79x, MKL8 2.95x; KNL-cache 1.19x/2.25x/3.75x; Power8 viennaCL 2.79x on 78/83) reproduced exactly from the four xlsx tables. The record's 'icpc (Intel 18.2.199)' is not on the configure page (it says intel/compilers/18.0.128), corrected; machine names 'White'/'Bowman' in the hardware field were not on the pages I opened, left as is. A rests on the P100 vs cuSPARSE comparison where the device model is stated; the KNL rows alone would be borderline (no CPU SKU).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier re-derived every ratio in claimed_speedup from the four SpGEMM_Benchmarks xlsx tables; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wiki/kokkos/kokkos-kernels/SpGEMM_Benchmarks.md>
  - <https://raw.githubusercontent.com/wiki/kokkos/kokkos-kernels/p100_configure.md>
  - <https://raw.githubusercontent.com/wiki/kokkos/kokkos-kernels/knl_configure.md>
  - <https://raw.githubusercontent.com/wiki/kokkos/kokkos-kernels/power8_configure.md>
  - <https://raw.githubusercontent.com/wiki/kokkos/kokkos-kernels/figures/spgemm_benchmark/P100-table.xlsx>
  - <https://raw.githubusercontent.com/wiki/kokkos/kokkos-kernels/figures/spgemm_benchmark/knl-ddr-table.xlsx>
  - <https://raw.githubusercontent.com/wiki/kokkos/kokkos-kernels/figures/spgemm_benchmark/knl-cache-table.xlsx>
  - <https://raw.githubusercontent.com/wiki/kokkos/kokkos-kernels/figures/spgemm_benchmark/power8-table.xlsx>
  - <https://github.com/kokkos/kokkos-kernels>
  - <https://github.com/kokkos/kokkos-kernels/commits/develop>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/perf_test/sparse/KokkosSparse_spgemm.cpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/2.6.00/perf_test/sparse/KokkosSparse_spgemm.cpp>
- **Sources the enricher read:**
  - <https://github.com/kokkos/kokkos-kernels>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/README.md>
  - <https://raw.githubusercontent.com/wiki/kokkos/kokkos-kernels/SpGEMM_Benchmarks.md>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/BUILD.md>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/sparse/src/KokkosSparse_spgemm.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/sparse/src/KokkosSparse_spgemm_handle.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/sparse/src/KokkosSparse_spgemm_symbolic.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/sparse/src/KokkosSparse_spgemm_numeric.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/sparse/src/KokkosKernels_Handle.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/sparse/impl/KokkosSparse_spgemm_impl.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/sparse/impl/KokkosSparse_spgemm_impl_def.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/sparse/impl/KokkosSparse_spgemm_impl_symbolic.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/sparse/impl/KokkosSparse_spgemm_impl_kkmem.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/sparse/impl/KokkosSparse_spgemm_symbolic_spec.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos-kernels/HEAD/sparse/impl/KokkosSparse_spgemm_numeric_spec.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos/HEAD/CHANGELOG.md>
  - <https://github.com/kokkos/kokkos-kernels/issues?q=is%3Aissue%20spgemm>
  - <https://github.com/kokkos/kokkos-kernels/issues/3153>
  - <https://github.com/kokkos/kokkos-kernels/issues/2291>
  - <https://github.com/kokkos/kokkos-kernels/issues/2083>
  - <https://github.com/GPUPeople/spECK>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/kokkos/kokkos-kernels`) · [data/wave8/enrich/raw/github_com_kokkos_kokkos_kernels.json](../../../data/wave8/enrich/raw/github_com_kokkos_kokkos_kernels.json) (enrichment confidence 0.8)

</details>
