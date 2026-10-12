# ALP/GraphBLAS (nonblocking backend)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++ GraphBLAS framework whose nonblocking backend fuses chained sparse ops at run time; paper reports beating SuiteSparse:GraphBLAS and Eigen.

| | |
|---|---|
| **Beats** | SuiteSparse:GraphBLAS and Eigen |
| **Claimed result** | Peer-reviewed paper (Mastoras, Anagnostidis, Yzelman, 'Design and implementation for nonblocking execution in GraphBLAS: tradeoffs and performance', ACM TACO 20(1), 2023, doi 10.1145/3561652), per its abstract as quoted in search results: nonblocking execution reaches up to 16.1x over SuiteSparse:GraphBLAS and up to 12.2x over Eigen on ten matrices for the PageRank algorithm, and up to 4.11x (5.13x with the analytic model) over ALP's own blocking execution. Paper body not opened. |
| **Workload** | PageRank on ten sparse matrices for the headline numbers against SuiteSparse:GraphBLAS and Eigen (per the abstract as quoted in search results); the paper reportedly also evaluates other algorithms such as conjugate gradient, which was not confirmed here. ALP/GraphBLAS nonblocking shared-memory backend. |
| **Metric** | latency |
| **Adoption** | 33 stars; PyPI package alp-graphblas (pyalp bindings, backends pyalp_ref, pyalp_omp, pyalp_nonblocking) |
| **Last commit** | 2026-02-24 |
| **Links** | [repository](https://github.com/Algebraic-Programming/ALP) · [benchmark](https://dl.acm.org/doi/10.1145/3561652) |

## Verdict

Per the peer-reviewed ACM TACO 20(1) 2023 paper's abstract as quoted in search results (paper not opened), the nonblocking backend reaches up to 16.1x over SuiteSparse:GraphBLAS and up to 12.2x over Eigen, with PageRank on ten matrices as the headline and CG and sparse DNN inference also evaluated, and up to 4.11x over ALP's own blocking mode. A search snippet places the experiments on a dual-socket Xeon Gold 6238T (44 cores, 1.9 GHz, hyper-threading and turbo off), but compiler, flags and baseline versions remain undocumented here.

## Use it when

- Iterative sparse algorithms written as long chains of vector operations around SpMV, such as PageRank, conjugate gradient or sparse DNN inference, on a multi-core Linux CPU, where fusing the vector ops between SpMVs cuts memory traffic.
- You want one algorithm source that runs sequential, OpenMP, nonblocking or distributed-memory (LPF bsp1d/hybrid) by switching a compiler-wrapper flag.
- Algorithm work in C++ under an Apache-2.0 license, or quick prototyping through the alp-graphblas Python wheels (0.8.43, x86-64 Linux, CPython 3.9-3.12).
- NUMA machines: libnuma is a hard dependency and shared data defaults to interleaved allocation.

## Skip it when

- Level-3 workloads (mxm/SpGEMM, triangle counting): blas3 and some blas2 primitives are not natively nonblocking, run blocking and print a warning, so the fusion advantage disappears.
- A single isolated kernel such as one SpMV: the speedup comes from fusing several operations, and no single-kernel numbers are published in the repo.
- Code that must use the GraphBLAS C API or the SuiteSparse:GraphBLAS ecosystem (LAGraph, python-graphblas): ALP exposes a C++ API and only a subset of Sparse BLAS.
- macOS or Windows targets: Mac OS X support is an open enhancement issue, and the build requires libnuma and POSIX threads.
- Decisions that need verified numbers: the 16.1x and 12.2x figures are 'up to' maxima from the TACO paper abstract, and its hardware, compiler and baseline versions could not be checked here.

## How it is fast

In the nonblocking backend each level-1/level-2 call is recorded as a lambda stage instead of running immediately (lazy evaluation); dynamic data-dependence analysis groups stages that share containers into one pipeline, which is then executed with loop fusion and loop tiling so a tile of every vector stays in cache across the fused operations. An analytic model picks the thread count and tile size per pipeline from vector count, element size, L1 size (98% target, 512-element minimum tile) and core count. Sparse-vector bookkeeping uses lock-free per-tile local coordinate stacks merged by prefix sum, and is skipped entirely when vectors are known dense (dense descriptor or run-time analysis).

## Compared with alternatives

Pick ALP over the GPU GraphBLAS siblings (GraphBLAST, spla, cuBool) when you run on CPUs, possibly across nodes via LPF, and your algorithm is iteration-heavy level-1/level-2 work that benefits from fusion; stay with SuiteSparse:GraphBLAS when you need the C API, its ecosystem or mxm-heavy workloads.

## Integration

| | |
|---|---|
| **Form** | static lib (headers plus per-backend libraries installed via CMake; programs link statically, through the grbcxx/grbrun wrappers or find_package(ALPGraphBLAS)) |
| **Dependencies** | OpenMP, libnuma, POSIX threads, libm; optional LPF 1.0+ for distributed/hybrid backends; doxygen/graphviz/pdflatex only for docs |
| **Minimum toolchain** | C++11 compiler with OpenMP (README: GCC 4.8.2 or higher), CMake 3.13+ |
| **Platforms** | Linux (libnuma required); x86-64 Python wheels on PyPI; SIMD width must be set per target in include/graphblas/base/config.hpp; experimental RISC-V Snitch (Banshee simulator) backend |
| **Thread safety** | not documented; the backends parallelise internally with OpenMP, and the nonblocking backend queues work in a global lazy-evaluation object, so treat concurrent ALP calls from several user threads as unsafe |
| **Drop-in for the baseline** | no |

## Gotchas

- Lazy evaluation moves work and error checks: pipelines run on reads through iterators, container construction or destruction, scalar-returning ops like grb::dot, or grb::wait, so timings and failures appear there; the docs say an illegal dense descriptor on a vector that becomes dense inside the pipeline cannot be caught (also an open issue).
- Configuration is compile-time constexpr (SIMD_SIZE, cache line, L1 size, index types); objects compiled with different configurations are undefined behaviour when linked, so keep one install per target architecture.
- Run-time knobs: OMP_NUM_THREADS is an upper bound for the analytic model, GRB_NONBLOCKING_TILE_SIZE forces a fixed tile size, and the README asks for OMP_PROC_BIND; pipelines beyond 4 concurrent, 16 containers or 16 stages print capacity warnings.
- Open bugs at the time of reading include 'std::swap for nonblocking vectors is broken', reference/reference_omp grb::dot mishandling aliasing, a masked set overwriting values outside the mask (question label) and a constexpr build error on some compilers.

## Known shortcomings

- Up to 16.1x over SuiteSparse:GraphBLAS and 12.2x over Eigen for PageRank only (TACO paper abstract via search; paper blocked); paper year 2023, not 2022.
- Open bugs: std::swap broken for nonblocking vectors; grb::dot aliasing; bad dense-descriptor use not always caught. Level-3 ops are not nonblocking. Paper unopened here (dl.acm.org blocked); search snippet gives dual Xeon Gold 6238T, 44 cores.

## Caveats and trade-offs

Paper not opened (dl.acm.org, arxiv.org and researchgate.net are blocked from this container) and the ALP README contains no numbers, so matrices, CPU, thread counts, compiler, flags and the SuiteSparse:GraphBLAS/Eigen versions are unverified. The figures are 'up to' maxima for PageRank only; typical speedups and other algorithms are unknown. Gains come from fusing chained GraphBLAS primitives, so single-kernel speedups are likely smaller. The README dates the TACO paper 20(1), 2023 (the record said 2022).

Header-based C++11 framework needing OpenMP, libnuma, pthreads and CMake; run-time fusion of linear-algebra primitives (nonblocking mode) and shared/distributed-memory backends. GraphBLAS-style API rather than an Eigen- or PETSc-style API.

## Maintenance

Actively developed (latest commit 2026-02-24, PyPI alp-graphblas 0.8.43), Apache-2.0 and Huawei-backed with 179 issues filed; copyable as a library, though the nonblocking backend still covers only level-1/level-2 natively.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The ALP README cites the peer-reviewed ACM TACO 20(1) 2023 paper (doi 10.1145/3561652); two search results quoting its abstract give up to 16.1x over SuiteSparse:GraphBLAS and 12.2x over Eigen on ten matrices for PageRank. The paper itself could not be opened (dl.acm.org is egress-blocked), so methodology and CPU are unseen; B per the precedent for peer-reviewed papers confirmed via abstract snippets.
- **Verifier notes:** README (Apache-2.0 header, lists the nonblocking backend and the TACO and IPDPSW 2022 papers), repo page (Apache-2.0, 33 stars, 6 forks, not a fork, default branch develop) and commits page (latest 2026-02-24) match the record. benchmark_url set to the README-linked DOI page, which I could not open; a later pass with access should confirm hardware and Eigen/SuiteSparse versions.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Algebraic-Programming/ALP/HEAD/README.md>
  - <https://github.com/Algebraic-Programming/ALP>
  - <https://github.com/Algebraic-Programming/ALP/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Algebraic-Programming/ALP/HEAD/README.md>
  - <https://raw.githubusercontent.com/Algebraic-Programming/ALP/HEAD/docs/Nonblocking_backend.md>
  - <https://raw.githubusercontent.com/Algebraic-Programming/ALP/HEAD/docs/Use_ALPGraphBLAS_in_your_own_project.md>
  - <https://raw.githubusercontent.com/Algebraic-Programming/ALP/HEAD/include/graphblas/nonblocking/config.hpp>
  - <https://raw.githubusercontent.com/Algebraic-Programming/ALP/HEAD/include/graphblas/nonblocking/analytic_model.hpp>
  - <https://github.com/Algebraic-Programming/ALP/tree/develop/docs>
  - <https://github.com/Algebraic-Programming/ALP/tree/develop/include/graphblas/nonblocking>
  - <https://github.com/Algebraic-Programming/ALP/issues?q=is%3Aissue>
  - <https://pypi.org/pypi/alp-graphblas/json>
  - https://dl.acm.org/doi/10.1145/3561652 (EGRESS_BLOCKED; abstract and setup taken from WebSearch snippets)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/algebraic-programming/alp`) · [data/wave8/enrich/raw/github_com_algebraic_programming_alp.json](../../../data/wave8/enrich/raw/github_com_algebraic_programming_alp.json) (enrichment confidence 0.7)

</details>
