# SyLVER (NLAFET)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Research StarPU task-based sparse Cholesky/LDL^T solver built on SPRAL SSIDS kernels; no published speedup in the repo.

| | |
|---|---|
| **Beats** | SPRAL SSIDS / HSL MA87 / PARDISO (no comparison found in the repo) |
| **Claimed result** | None. The README and doc/source pages (purpose.rst, introduction.rst) describe DAG-based algorithms that 'enable an efficient exploitation of multicore CPU architectures and GPU-accelerated systems' with no numbers. |
| **Workload** | Sparse symmetric positive-definite (Cholesky) and indefinite (LDL^T) direct factorization on multicore and GPU through the StarPU runtime; no benchmark in the repo. |
| **Metric** | throughput |
| **Adoption** | 13 stars, 3 forks |
| **Last commit** | 2020-05-11 |
| **Links** | [repository](https://github.com/NLAFET/SyLVER) · [benchmark](https://github.com/NLAFET/SyLVER) |

## Verdict

The repo has no measured result: the README and doc pages only say the DAG algorithms 'enable an efficient exploitation of multicore CPU architectures and GPU-accelerated systems'. The related NLAFET papers (SpLLT vs HSL MA87 on 28 cores, reported only as 'comparable performance'; SSIDS v2 APTP vs MA86/MA97/PARDISO, 'performs favourably') were seen as search snippets only, because nlafet.eu, researchgate and epubs.stfc.ac.uk are blocked here, and they measure sibling codes, not SyLVER.

## Use it when

- Research on runtime-system (StarPU) scheduling of sparse direct solvers, as a worked example of an STF multifrontal Cholesky/LDL^T on CPU+GPU nodes.
- Studying or reproducing NLAFET-era APTP and heterogeneous-scheduling results where you need the StarPU variant of SSIDS rather than the OpenMP one.
- Large symmetric indefinite systems on one multicore node with optional NVIDIA GPUs, when you already run StarPU and SPRAL and can tolerate prototype code.

## Skip it when

- Production solves: the last commit was 2020-05-11, there are no releases, CI was Travis, and no benchmarks or regression results are published; use SPRAL SSIDS, MUMPS, PARDISO or CHOLMOD instead.
- When you need the factors: open issue #2 (March 2020, unanswered) reports that L and D cannot be obtained from spldlt_factorize().
- Unsymmetric systems: the splu path is commented out of the documentation and has no driver beyond splu_test.F90.
- Simple builds: it needs StarPU &gt;= 1.3, a SPRAL submodule pinned to commit f71ab9e (branch 'gpufix'), MeTiS, hwloc, a sequential BLAS/LAPACK, and Fortran, C and C++ compilers, plus CUDA for GPU runs.
- Distributed-memory (MPI) runs: nothing in the README or CMake options offers them.

## How it is fast

The multifrontal factorization is written as a sequential task flow: fronts are split into blocks (block size nb), and each block operation is submitted as a task to StarPU, which builds the DAG and schedules it across CPU cores and, optionally, NVIDIA GPUs (lws or heteroprio schedulers). Indefinite factorization uses A Posteriori Threshold Pivoting (APTP), which factors blocks optimistically and checks stability afterwards, so pivoting does not serialise the column sweep; failed pivots are delayed or redone with TPP. This is the method of Duff-Hogg-Lopez (NLAFET Working Note 21 / SSIDS v2), which per search snippets performs favourably against HSL MA86, HSL MA97 and PARDISO on multicore, but those numbers are for SSIDS, not for this repo.

## Compared with alternatives

Choose SPRAL SSIDS, which carries the same APTP kernels in a maintained OpenMP/CUDA library with published comparisons, for real solves; pick SyLVER only to study or extend the StarPU task-based variant. For SPD-only problems with published speedups over CHOLMOD, BaSpaCho or Sympiler are better documented.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | StarPU &gt;= 1.3 (or sequential STF runtime), SPRAL (git submodule, built automatically), MeTiS, hwloc, sequential BLAS/LAPACK (MKL/ESSL/OpenBLAS); optional CUDA, CUTLASS, OpenMP |
| **Minimum toolchain** | C++11 (CMAKE_CXX_STANDARD 11), Fortran 2003 compiler, CMake; CUDA toolkit for GPU builds |
| **Platforms** | Linux x86-64 and IBM POWER (ESSL recommended there) are implied by the README; NVIDIA GPUs optional; other platforms not documented |
| **Thread safety** | not documented (parallelism is internal via StarPU; global sylver_init/sylver_finalize suggests one solver context per process) |
| **Drop-in for the baseline** | partial — API mirrors SPRAL SSIDS's analyse/factor/solve cycle in Fortran, but uses its own spldlt_\* names and init/finalize; not a drop-in for PARDISO, MA87 or CHOLMOD |

## Gotchas

- It must be linked against a sequential BLAS/LAPACK (README); a threaded BLAS oversubscribes cores under StarPU.
- It includes SPRAL's internal C++ headers (ssids/cpu/cpu_iface.hxx, ThreadStats.hxx), so it is coupled to the pinned SPRAL submodule commit; building against a current SPRAL release is not documented and may break.
- STARPU_DIR must be set in the environment for FindSTARPU.cmake, and the default runtime is StarPU, so a plain cmake without StarPU fails unless you pass -D SYLVER_RUNTIME=STF.
- The docs claim bit-compatible results, but no test evidence for that is in the repo.

## Known shortcomings

- Tier D: no numbers anywhere (README, docs, drivers; nlafet.eu blocked); StarPU-based successor of SPRAL SSIDS, 13 stars, abandoned 2020-05-11.
- Open issue #2 (2020, unanswered): L and D cannot be extracted. Coupled to SPRAL internal headers through a submodule pinned at f71ab9e (branch gpufix); the splu path is undocumented. NLAFET working notes and RAL-TR-2016-017 (nlafet.eu, epubs.stfc.ac.uk blocked) unread.

## Caveats and trade-offs

No numbers in README, doc/source or drivers (drivers hold only spldlt_test.F90, spldlt_test_debug.F90, splu_test.F90). NLAFET deliverable and working-note PDFs on www.nlafet.eu (for example WN21 Duff-Hogg-Lopez on sparse Cholesky with a task-flow implementation) were returned by WebSearch but nlafet.eu is blocked here, so no paper numbers were read. SyLVER is the StarPU-based successor of SPRAL SSIDS, so SPRAL SSIDS is its natural baseline, and that is a library also listed under this category by other entries. Language label is inferred from the file listing (src/, include/sylver, Fortran drivers); the GitHub language bar was not shown.

Requires StarPU 1.3+, SPRAL (submodule), MeTiS, hwloc and a sequential BLAS/LAPACK (MKL or ESSL recommended); optional CUDA. Mixed C++ and Fortran 2003 sources (test drivers are .F90). Developed for the EU H2020 NLAFET project; last commit May 2020.

## Maintenance

Abandoned since May 2020 (EU H2020 NLAFET project ended), with 844 commits, 13 stars and one unanswered issue; BSD-3-Clause so copyable, but a research prototype with heavy dependencies.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification D, tier now D.
- **Tier reason:** README and repo carry no performance numbers or baseline comparison; related Duff-Hogg-Lopez StarPU task-flow papers (vs HSL MA87 / SSIDS) surfaced only as WebSearch titles with no numbers, and researchgate/nlafet.eu are blocked.
- **Verifier notes:** Record accurate: BSD-3-Clause, last commit 2020-05-11 ('added GPU solve kernel for Cholesky factor'), abandoned. Rejected only under the tier-D not-notable rule (13 stars); per the catalog's keep-and-document rule the orchestrator may override to keep, and a retier could follow if the NLAFET working notes or the 'Experiments with sparse Cholesky using a sequential task-flow implementation' paper can be opened.
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/NLAFET/SyLVER>
  - <https://github.com/NLAFET/SyLVER/commits>
  - <https://raw.githubusercontent.com/NLAFET/SyLVER/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/NLAFET/SyLVER>
  - <https://raw.githubusercontent.com/NLAFET/SyLVER/HEAD/README.md>
  - <https://raw.githubusercontent.com/NLAFET/SyLVER/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NLAFET/SyLVER/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/NLAFET/SyLVER/HEAD/doc/source/purpose.rst>
  - <https://raw.githubusercontent.com/NLAFET/SyLVER/HEAD/doc/source/introduction.rst>
  - <https://raw.githubusercontent.com/NLAFET/SyLVER/HEAD/src/sylver_ciface.hxx>
  - <https://github.com/NLAFET/SyLVER/tree/master/src>
  - <https://github.com/NLAFET/SyLVER/tree/master/examples>
  - <https://github.com/NLAFET/SyLVER/issues?q=is%3Aissue>
  - <https://github.com/orgs/NLAFET/repositories>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/README.md>
  - WebSearch snippets: aimsciences.org naco.2018014 abstract (SpLLT vs HSL MA87), NLAFET WN21 / RAL-TR-2016-017 abstract (SSIDS APTP vs MA86, MA97, PARDISO)
  - Attempted, blocked (CONNECT 403): https://www.nlafet.eu/wp-content/uploads/2017/03/NLAFET-WN14-Duff-Lopez-17-06-13.pdf, https://epubs.stfc.ac.uk/manifestation/30693256/RAL-TR-2016-017.pdf
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nlafet/sylver`) · [data/wave8/enrich/raw/github_com_nlafet_sylver.json](../../../data/wave8/enrich/raw/github_com_nlafet_sylver.json) (enrichment confidence 0.6)

</details>
