# ParAMD (parallel approximate minimum degree ordering)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> OpenMP parallel approximate minimum degree ordering, 2.9-8.5x faster than sequential SuiteSparse AMD on 64 cores.

| | |
|---|---|
| **Beats** | SuiteSparse AMD (single-threaded approximate minimum degree fill-reducing ordering) |
| **Claimed result** | 64 threads: 2.85x (nd24k) to 8.51x (nlpkkt240) faster than SuiteSparse AMD (pre2 3.25x, ldoor 4.64x, dielFilterV3real 5.92x, Flan_1565 6.11x, HV15R 6.21x, Queen_4147 6.18x, stokes 7.95x). Single thread: 0.44x to 1.01x, i.e. slower than SuiteSparse on 8 of 9 matrices. Fill-in ratio versus SuiteSparse at 64 threads: 0.98x to 1.16x. |
| **Workload** | Fill-reducing AMD ordering time and fill-in on 9 SuiteSparse Matrix Collection matrices (pre2, nd24k, ldoor, dielFilterV3real, Flan_1565, HV15R, Queen_4147, stokes, nlpkkt240); median of five random row permutations, ParAMD at 1 and 64 threads versus SuiteSparse AMD. |
| **Metric** | latency |
| **Hardware** | AMD EPYC 7763 (64 cores) for the committed exemplar outputs; README says benchmarks need at least 64 physical cores and 256 GB RAM |
| **Compiler and flags** | GCC v13.2.1 with OpenMP; CMakeLists.txt defaults CMAKE_BUILD_TYPE to Release; scripts/build.sh builds SuiteSparse v7.10.1 (AMD only) with its CMake defaults; scripts/scaling.sh runs seeds 1-5 with OMP_NUM_THREADS=1 or 64 and OMP_PLACES=cores. |
| **Adoption** | 9 stars |
| **Last commit** | 2025-11-04 |
| **Links** | [repository](https://github.com/PASSIONLab/ParAMD) · [benchmark](https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/plots/scaling.csv) |

## Verdict

On a 64-core AMD EPYC 7763 (GCC 13.2.1, OpenMP, CMake Release), ParAMD at 64 threads computed AMD orderings of nine SuiteSparse matrices 2.85x (nd24k) to 8.51x (nlpkkt240) faster than single-threaded SuiteSparse AMD v7.10.1, taking the median of five random symmetric permutations, with fill-in 0.98x to 1.16x of SuiteSparse's; at one thread it was 0.44x to 1.01x as fast. These are the authors' committed exemplar results (plots/scaling.csv), reproducible with scripts/build.sh and scripts/scaling.sh.

## Use it when

- Large sparse matrices (tens to hundreds of millions of nonzeros) where the AMD ordering itself takes seconds to minutes: stokes 79 s to 10 s and nlpkkt240 296 s to 35 s at 64 threads in the committed table.
- Many-core shared-memory nodes (the benchmarks assume 64 physical cores, for example an AMD EPYC 7763) whose cores otherwise sit idle during the symbolic/analysis phase of a direct solver.
- Workflows that reorder many different sparsity patterns, such as changing meshes or repeated analyse-factor cycles, where ordering time adds up.
- When a few percent more fill (0.98x to 1.16x SuiteSparse's in the published runs) is an acceptable price for a faster ordering.

## Skip it when

- Few cores or serial use: at one thread it ran at 0.44x to 1.01x the speed of SuiteSparse AMD, slower on 8 of 9 matrices.
- One-shot factorizations of huge matrices where factor cost dwarfs ordering cost: nlpkkt240's predicted fill rises from 1.60e12 to 1.85e12 (1.16x), which can cost more in factorization time and memory than the 260 s saved on ordering (judgement derived from page data).
- You need COLAMD, CAMD, constrained or column orderings, or SuiteSparse's Control/Info options: only symmetric AMD is provided (issue #1, January 2026, asks for COLAMD and is unanswered).
- Matrices beyond 32-bit index range: vtype and etype are both int32_t and there is no 64-bit variant like SuiteSparse's amd_l_order.
- Non-GCC or non-Linux toolchains without checking: the reader uses POSIX mmap and libstdc++ parallel mode (__gnu_parallel::sort), and the core needs OpenMP '#pragma omp atomic compare' support (GCC 13.2.1 was used).

## How it is fast

It keeps SuiteSparse AMD's quotient-graph machinery (approximate external degrees, supervariables, element absorption with aggressive absorption, dense rows above 10\*sqrt(n) set aside) but replaces one-pivot-at-a-time elimination with multiple elimination. Each round it gathers candidates whose approximate degree is within a relaxation factor (mult, default 1.1) of the current minimum, capped at lim/threads (default 8192/threads), and picks a distance-2 independent set among them with Luby-style random priorities, so the chosen pivots share no neighbours and different threads can eliminate them concurrently. Degree lists are per-thread with thread affinity, new element lists are appended to a shared buffer through an atomic fetch-and-add, and the A+A^T symmetrization step is parallel too.

## Compared with alternatives

It is the only fill-reducing ordering among the catalogued sparse-and-solvers entries, so it complements rather than competes with them: put it in front of a direct solver such as CHOLMOD (or the task-based A64FX CHOLMOD entry), BaSpaCho or PanguLU when a sequential AMD step shows up in the analysis-phase profile.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | OpenMP (5.1 'atomic compare' support); optional SuiteSparse AMD (v7.10.1 in the scripts) only for the comparison mode of the CLI |
| **Minimum toolchain** | C++17, CMake 3.22+, a GCC that supports '#pragma omp atomic compare' (GCC 13.2.1 used); Python 3.13 environment only for the benchmark plots |
| **Platforms** | Linux shared-memory multicore (tested on x86-64 AMD EPYC 7763, 64 cores); no SIMD or ISA requirement in the code |
| **Thread safety** | not documented; each paramd() call opens its own OpenMP parallel region sized by OMP_NUM_THREADS, and concurrent calls from several host threads are not discussed |
| **Drop-in for the baseline** | partial — takes the same int32 (n, Ap, Ai) pattern and fills a perm array like amd_order, but has no Control/Info arrays or 64-bit amd_l variant, returns a fill count instead of a status, and produces a different (slightly worse, thread-count-dependent) ordering |

## Gotchas

- The quotient-graph buffer is malloc'd once at (1 + mem) times the symmetrized nonzero count (mem defaults to 1.5), and new element lists are appended at an atomically advanced offset with no capacity check and no compaction, unlike SuiteSparse AMD's garbage collection; if a matrix needs more elbow room the code would write past the buffer, so raise --mem for unusual inputs.
- All offsets are int32 (etype): the reader checks that the file's nonzero count fits, but symmetric expansion roughly doubles it and the elbow room multiplies it by 2.5 at default settings, so inputs above roughly 850 million symmetrized off-diagonal entries would overflow 32-bit offsets (derived from the code).
- Library code calls exit(1) on reader errors, malloc results are not checked, and the mmap failure test compares against NULL rather than MAP_FAILED; config::print() reports 'Symmetry enabled' from the stat flag instead of sym (cosmetic).
- Orderings depend on the thread count (per-thread mt19937 seeded by thread id and per-thread candidate lists), so 1-thread and 64-thread fill-ins differ; the CLI randomly permutes the input first (--seed, default 1) to break ties, but a bare paramd() library call does not.

## Known shortcomings

- Win is parallel scaling only: single-threaded ParAMD is slower than SuiteSparse AMD on 8 of 9 matrices, and fill-in grows up to 1.16x.
- Possible memory bug: the quotient-graph buffer is allocated once at (1+mem) x nnz and new data is appended with no capacity check or compaction, so a large enough matrix could write past the buffer. All offsets are int32 (no 64-bit variant). Library code calls exit(1) on reader errors. Venue (SIAM PP26 proceedings) seen only in search snippets.

## Caveats and trade-offs

Authors' own benchmark (PASSIONLab, arXiv preprint 2504.17097, whose abstract reports up to 8.30x; the paper itself could not be opened here and no peer-reviewed venue was confirmed). The committed plots/scaling.csv is one exemplar run on one machine. The headline speedups compare 64 threads to the single-threaded SuiteSparse AMD, so they measure parallel scaling, not per-core efficiency; at 1 thread ParAMD is slower on 8 of 9 matrices. Ordering quality drops slightly (fill-in up to 1.16x SuiteSparse's on nlpkkt240). Repository is young (4 commits, April to November 2025) and has few users.

Approximate parallel variant: ordering quality is slightly worse (fill-in up to 1.16x SuiteSparse AMD in the committed table). Needs many cores to pay off; at one thread it is slower than SuiteSparse AMD. Provides libparamd.so, a paramd.h header and a CLI; reads Matrix Market input; OpenMP; relaxation factors (mult, lim, mem) are tunable.

## Maintenance

Young Berkeley Lab project (v1.0.0, 4 commits April to November 2025, 9 stars, one open issue) under BSD-3-Clause with a Zenodo DOI; the arXiv paper 2504.17097 appears, per WebSearch snippets only, in the SIAM PP26 proceedings, which could not be confirmed because the publisher site is blocked here.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** plots/scaling.csv (AMD EPYC 7763) is reproduced by public scripts (scripts/build.sh, scripts/scaling.sh, bin/main.cpp) that build SuiteSparse AMD v7.10.1 and ParAMD, with GCC 13.2.1 stated in the README and a Release build forced by CMakeLists.txt; code, compiler, flags and CPU are all public, so A.
- **Verifier notes:** All nine speedups, single-thread ratios and fill-in ratios in the record match plots/scaling.csv. The record's 'SuiteSparse AMD version not stated' was wrong: build.sh pins SuiteSparse v7.10.1. Metadata: BSD-3-Clause LICENSE, 9 stars, not archived or a fork, last commit 2025-11-04 (active); arxiv.org is blocked here, the 8.30x figure comes from a WebSearch snippet of the abstract.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/plots/scaling.csv>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/README.md>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/scripts/build.sh>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/scripts/scaling.sh>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/LICENSE>
  - <https://github.com/PASSIONLab/ParAMD>
  - <https://github.com/PASSIONLab/ParAMD/commits>
- **Sources the enricher read:**
  - <https://github.com/PASSIONLab/ParAMD>
  - <https://github.com/PASSIONLab/ParAMD/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/README.md>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/include/paramd/paramd.h>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/bin/main.cpp>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/src/paramd.cpp>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/src/config.cpp>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/src/matrix.cpp>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/src/utils.cpp>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/environment.yml>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/scripts/build.sh>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/scripts/scaling.sh>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/scripts/download.sh>
  - <https://raw.githubusercontent.com/PASSIONLab/ParAMD/HEAD/plots/scaling.csv>
  - WebSearch: "Parallelizing the Approximate Minimum Degree Ordering Algorithm" Chang Buluç Demmel (snippets from arxiv.org/abs/2504.17097 and ui.adsabs.harvard.edu)
  - WebSearch: ParAMD venue (snippets naming the 2026 SIAM Conference on Parallel Processing for Scientific Computing proceedings)
  - https://sparsitute.lbl.gov/publications (EGRESS_BLOCKED)
  - https://epubs.siam.org/doi/10.1137/1.9781611979022 (EGRESS_BLOCKED)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/passionlab/paramd`) · [data/wave8/enrich/raw/github_com_passionlab_paramd.json](../../../data/wave8/enrich/raw/github_com_passionlab_paramd.json) (enrichment confidence 0.85)

</details>
