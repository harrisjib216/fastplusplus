# SparseX (CSX-format SpMV library with LLVM runtime code generation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Multicore CPU SpMV library: CSX compressed format plus LLVM-JIT kernels per matrix; claims parity-or-better vs Intel MKL CSR.

| | |
|---|---|
| **Beats** | Intel MKL CSR SpMV (and pOSKI, ViennaCL in the TOMS paper) |
| **Claimed result** | No verified numbers. SparseX TOMS 2018 abstract (search-result quote): superior performance over competitive libraries on large-scale problems, comparable performance to Intel MKL and ViennaCL. The earlier '19.5x over MKL inspector-executor (1.6x average) for HPC matrices' belongs to a different paper by the same group (arXiv 1711.05487, a CSR-based optimizer), not to SparseX. |
| **Workload** | Sparse matrix-vector multiplication (SpMV) on multicore CPUs; the Compressed Sparse eXtended (CSX) format stores dense substructures compactly to cut memory bandwidth and emits specialised kernels per matrix. |
| **Metric** | throughput |
| **Adoption** | 43 stars, 9 forks, 701 commits |
| **Last commit** | 2018-06-10 |
| **Links** | [repository](https://github.com/cslab-ntua/sparsex) · [benchmark](https://dl.acm.org/doi/10.1145/3134442) |

## Verdict

No SparseX-versus-MKL numbers could be read from an opened page. Per search snippets, the TOMS 2018 abstract claims superior performance on large-scale problems and performance comparable to Intel MKL and ViennaCL. A third-party ICS 2025 paper (DIV, snippet only) says SparseX reliably speeds up SpMV on large matrices by a 13% median and 7.7% geometric mean; its baseline is presumably MKL CSR but is not stated in the snippet, and no hardware or compiler is given.

## Use it when

- Iterative solvers (CG, GMRES, eigen-solvers) on one large sparse matrix that run thousands of SpMVs, so the one-off tuning and JIT cost is amortized; spx_mat_save/spx_mat_restore can skip re-tuning in later runs
- Matrices with regular dense substructure (FEM and structural meshes with blocks, diagonals or long row runs), where index compression cuts memory traffic the most
- Large symmetric matrices, where CSX-sym (spx.matrix.symmetric) halves the storage that has to be streamed
- Multi-socket NUMA Linux servers, where the library's thread pinning and NUMA placement do the tuning for you
- As a historical baseline in SpMV research: later papers (DIV, ICS 2025) still benchmark against it

## Skip it when

- One-shot or few SpMVs: the user's guide calls CSX preprocessing (substructure detection plus JIT compile) 'non-negligible' even with sampling
- Any current toolchain: configure.ac accepts only LLVM 4.0.0 to 6.0.0, the JIT uses Clang's internal C++ API (which the README says breaks with almost every LLVM release), and the last commit is from 2018. The two open issues (#2 Boost.atomic not found with Boost 1.58, #4 cannot install LLVM) have no fix
- Matrices whose sparsity pattern changes: after tuning, nonzeros cannot be inserted or deleted, only existing values updated through spx_mat_set_entry
- GPUs, Windows or macOS: CPU only, Linux only (futex wrapper, libnuma required)
- When a large margin over MKL is the goal: the only third-party figures found (DIV, ICS 2025, search snippet) put SparseX at a 13% median and 7.7% geometric-mean speedup on large matrices, and DIV reports 1.87x (Intel) and 2.0x (AMD) over SparseX

## How it is fast

SpMV on CPUs is limited by memory bandwidth, and CSR spends one column index per nonzero. CSX (Compressed Sparse eXtended, PPoPP'11 / TPDS'13) detects dense substructures: horizontal, vertical, diagonal and anti-diagonal runs, row- and column-aligned blocks, and delta-encoded leftovers. It stores one short descriptor per substructure instead of per-element indices, which shrinks the index stream. For each matrix, the library fills C kernel templates for the patterns it chose (src/templates/\*_tmpl.c), compiles them at runtime with the Clang frontend and LLVM MCJIT, and runs them on a pinned thread pool with NUMA-aware allocation. A symmetric variant (CSX-sym) stores only half the matrix, and optional Reverse Cuthill-McKee reordering improves locality.

## Compared with alternatives

Pick SparseX over merge-spmv, CSR5 or CVR only when the matrix has strong block, diagonal or run structure (or is symmetric and large) and you can pin an old LLVM 4-6 toolchain. For irregular or scale-free matrices, CVR and merge-spmv report clearer wins over MKL, and SPC5 is the maintained block-kernel option for AVX-512 and ARM SVE.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | LLVM/Clang 4.0.0-6.0.0 (linked, used at runtime for the JIT), Boost &gt;= 1.48 (atomic, regex, serialization, system), libnuma &gt;= 2.0.7, pthreads; optional Intel MKL or pOSKI for the bundled benchmark driver |
| **Minimum toolchain** | gcc/g++ &gt;= 4.8 plus LLVM/Clang 4.0.0-6.0.0 exactly (configure rejects other versions); autotools (autoreconf -vi) to build from git; JIT kernels are compiled as C99 |
| **Platforms** | Linux on SMP and NUMA multicore CPUs; the JIT targets the host triple, and CPU architectures beyond an x86_64-specific fix in the ChangeLog are not documented |
| **Thread safety** | The library runs its own thread pool (spx.rt.nr_threads, default all cores, pinned by spx.rt.cpu_affinity). Calling it concurrently from several user threads is not documented. |
| **Drop-in for the baseline** | partial — spx_matvec_kernel_csr() accepts plain CSR arrays and computes y = alpha\*A\*x + beta\*y like MKL, but x and y must be wrapped as spx_vector_t objects tied to the matrix partition, and index/value types are fixed at configure time (default int/double) |

## Gotchas

- The public headers read (sparsex.h, matvec.h, common.h, types.h) have no extern "C" guards; C++ callers must wrap the #include themselves (the cslab-ntua SpMV-Research wrapper notes undefined references otherwise)
- The JIT compiles C at runtime and needs the system C headers: set SPX_JIT_INC_PATH if they are in a non-standard location, and LD_LIBRARY_PATH for a non-standard install prefix
- The default thread count and affinity grab all cores with a share-nothing pinning policy, which can clash with an OpenMP or MPI application's own pinning; set spx.rt.nr_threads and spx.rt.cpu_affinity explicitly
- The bundled User's Guide still lists LLVM == 3.0, the README says &gt;= 4.0, and configure.ac accepts only 4.0.0-6.0.0; trust configure.ac. Explicit zeros in the input are kept as logical nonzeros

## Known shortcomings

- Downgraded to D: the 19.5x/1.6x vs MKL came from a different paper (arXiv 1711.05487, a CSR optimizer), not SparseX; the SparseX TOMS abstract only says 'comparable to MKL'.
- configure.ac accepts only LLVM 4.0.0-6.0.0 (Clang-internal JIT) while the User's Guide says LLVM 3.0; issues #2 (Boost.atomic) and #4 (LLVM install) unresolved; public headers lack extern "C". No opened page shows SparseX vs MKL numbers. The same lab's DIV (ICS 2025, snippet) beats SparseX by 87% (Intel) and 100% (AMD) and MKL by 77% / 115%, and the same snippet puts SparseX at a 13% median, 7.7% geomean gain on large matrices.

## Caveats and trade-offs

No numbers for SparseX itself could be verified: the TOMS paper (dl.acm.org) and the SparseX home page are blocked here, and its abstract as quoted only claims superior performance on large-scale problems and comparable performance to MKL and ViennaCL. The figure the search agent recorded (up to 19.5x, 1.6x average over MKL inspector-executor for HPC matrices) comes from a different paper by the same authors (arXiv 1711.05487) about a CSR-based optimization selector, so it does not apply to SparseX. A 2025 third-party paper (DIV, ICS 2025; snippet only) says SparseX mainly speeds up SpMV for large matrices, median 13 percent, geometric mean 7.7 percent, baseline not visible. The repo ships a benchmark driver (src/bench, bench_spmv with --enable-bench and --with-mkl / pOSKI) but no results. Requires LLVM/Clang &gt;= 4 for its JIT and notes every LLVM release breaks the JIT module; last commit 2018 (LLVM 6 support), so it likely does not build against current LLVM.

Needs LLVM/Clang &gt;= 4.0, Boost &gt;= 1.48 (regex, serialization, system), numactl and gcc &gt;= 4.8 (README); autotools build; format conversion and tuning step before the first multiply, so it pays off only for repeated SpMV (iterative solvers).

## Maintenance

Abandoned since 2018-06-10, when the last change added LLVM 6 support; BSD-3-Clause and copyable, but expect to port the Clang-based JIT before it builds against any LLVM newer than 6.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now D.
- **Tier reason:** The record's 19.5x / 1.6x figures are misattributed: a WebSearch result ties them to a different Elafrou/Goumas/Koziris paper ('Performance Analysis and Optimization of Sparse Matrix-Vector Multiplication on Modern Multi- and Many-Core Processors', arXiv 1711.05487), whose CSR-based optimizer, not SparseX/CSX, beats MKL inspector-executor. The SparseX TOMS 2018 abstract, as quoted in search results, says only 'superior performance over competitive libraries on large-scale problems' and 'comparable performance to Intel MKL and ViennaCL'; the README, User's Guide (doc/SparseX_UG.pdf) and repo hold no numbers, so D.
- **Verifier notes:** Shortcoming to record: claimed speedup misattributed (numbers belong to arXiv 1711.05487, not SparseX). Kept as D rather than rejected because SparseX is a peer-reviewed TOMS library that later SpMV papers still benchmark against; under the keep-and-document rule it stays with this shortcoming. Metadata checked: BSD-3-Clause (LICENSE.txt), 43 stars, 9 forks, 701 commits, last commit 2018-06-10 (abandoned).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/cslab-ntua/sparsex>
  - <https://github.com/cslab-ntua/sparsex/commits>
  - <https://github.com/cslab-ntua/sparsex/tree/master/doc>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/README>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/LICENSE.txt>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/doc/SparseX_UG.pdf>
- **Sources the enricher read:**
  - <https://github.com/cslab-ntua/sparsex>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/README>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/LICENSE.txt>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/ChangeLog>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/configure.ac>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/INSTALL>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/AUTHORS>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/doc/SparseX_UG.pdf>
  - <https://github.com/cslab-ntua/sparsex/issues?q=is%3Aissue>
  - <https://github.com/cslab-ntua/sparsex/tree/master/include/sparsex>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/include/sparsex/matvec.h>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/include/sparsex/sparsex.h>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/include/sparsex/types.h>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/include/sparsex/common.h>
  - <https://github.com/cslab-ntua/sparsex/tree/master/src>
  - <https://github.com/cslab-ntua/sparsex/tree/master/src/internals>
  - <https://github.com/cslab-ntua/sparsex/tree/master/src/templates>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/src/templates/csx_spmv_tmpl.c>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/src/templates/horiz_tmpl.c>
  - <https://raw.githubusercontent.com/cslab-ntua/sparsex/master/src/internals/JitCompiler.cpp>
  - <https://github.com/cslab-ntua/SpMV-Research>
  - <https://github.com/cslab-ntua/SpMV-Research/tree/main/benchmark_results>
  - <https://github.com/cslab-ntua/SpMV-Research/tree/main/benchmark_code/CPU/AMD/spmv_code_bench>
  - <https://raw.githubusercontent.com/cslab-ntua/SpMV-Research/main/benchmark_code/CPU/AMD/spmv_code_bench/spmv_kernel_sparsex.cpp>
  - WebSearch snippets: SparseX TOMS 2018 abstract; DIV: An Index & Value compression method for SpMV on large matrices (ICS 2025)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/cslab-ntua/sparsex`) · [data/wave8/enrich/raw/github_com_cslab_ntua_sparsex.json](../../../data/wave8/enrich/raw/github_com_cslab_ntua_sparsex.json) (enrichment confidence 0.55)

</details>
