# Task-based nested multithreaded CHOLMOD for A64FX (OmpSs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C` · `CC-BY-4.0` · ⚪ unknown

> Research OmpSs/OpenMP-task parallelization of CHOLMOD's supernodal Cholesky with selective nesting; 1.95x over multi-threaded-BLAS CHOLMOD on A64FX.

| | |
|---|---|
| **Beats** | CHOLMOD with multi-threaded BLAS |
| **Claimed result** | OPT-D-COST 1.95x average over multi-threaded-BLAS CHOLMOD across 60 SuiteSparse matrices; 1.46x vs best state-of-the-art task-based method (1.07x small matrices, 1.83x large matrices) |
| **Workload** | Sparse multithreaded Cholesky on 60 SuiteSparse matrices, 48-core A64FX |
| **Metric** | throughput |
| **Hardware** | 4-socket A64FX, 48 cores, 2.2GHz, 32GB HBM2 |
| **Compiler and flags** | fcc 4.2.0b, OmpSs-1 19.06, Fujitsu BLAS |
| **Links** | [repository](https://doi.org/10.5281/zenodo.5974376) · [benchmark](https://arxiv.org/pdf/2202.09288) |

## Verdict

On a 48-core 4-socket A64FX (2.2 GHz, 32 GB HBM2) with fcc 4.2.0b, OmpSs-1 19.06 and Fujitsu BLAS, OPT-D-COST averaged 1.46x over a non-nested task-parallel CHOLMOD and 1.95x over stock CHOLMOD with multi-threaded BLAS across 60 SuiteSparse SPD matrices (about 1.07x on small, up to 1.83x on large groups).

## Use it when

- You run CHOLMOD-style supernodal Cholesky on many-core Arm A64FX (Fugaku/FX1000/FX700) and multi-threaded BLAS leaves cores idle.
- Large SPD matrices (millions of nonzeros) where the paper reports 1.67-1.83x over its non-nested task baseline.
- Matrices with wide, shallow elimination trees where mt-BLAS CHOLMOD collapses (e.g. af_shell3: mt-BLAS 0.19x vs OPT-D-COST 1.31x relative to non-nested).
- As a reference design for adding task-granularity control to your own supernodal or multifrontal factorization.

## Skip it when

- Production code: it is a paper artifact under CC-BY-4.0 (not an OSI software license), with no releases, tests or maintenance.
- x86 or GPU machines: only A64FX was evaluated; the authors say thresholds (n/14 goal, 50,000-flop cutoff, D &lt;= 30% of max children) were tuned there and would need re-tuning for x86.
- Small matrices (10k-200k nonzeros): gain over the non-nested task version is only about 1.07x.
- Toolchains without OmpSs-1 (nanos++/mercurium) unless you port the pragmas to plain OpenMP tasks yourself.
- If you need a maintained faster Cholesky, BaSpaCho or Sympiler are catalogued with real repositories.

## How it is fast

Stock CHOLMOD walks supernodes in order and gets parallelism only from multi-threaded BLAS inside each supernode, which starves on small or very sparse fronts. This work exposes elimination-tree parallelism as tasks and uses 'selective nesting': an outer task is split into inner update tasks only if it has at least D updates (D picked per matrix by the OPT-D heuristic targeting max(1.1\*n_super, n/14) tasks), and OPT-D-COST additionally suppresses inner tasks under about 50,000 flops to cut runtime overhead. Nesting is toggled with the OpenMP 'final' clause.

## Compared with alternatives

Pick it over BaSpaCho or Sympiler only if you are staying inside CHOLMOD on A64FX and want its task-granularity heuristics; otherwise those siblings are maintained libraries with code you can actually depend on.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CHOLMOD (SuiteSparse, version not stated), OmpSs-1 19.06 (nanos++ runtime, mercurium compiler), vendor BLAS/LAPACK (Fujitsu BLAS in the paper) |
| **Minimum toolchain** | not documented (paper used Fujitsu fcc 4.2.0b) |
| **Platforms** | evaluated only on aarch64 A64FX (48 cores, HBM2) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — replaces CHOLMOD's numerical factorization internals, but it is not packaged as a patch or library; integration method is not documented |

## Gotchas

- The 1.46x headline is against the authors' own non-nested task version (equivalent to PaStiX-style 1D task decomposition), not against an external library; 1.95x vs mt-BLAS CHOLMOD is the same data (mt-BLAS averages 0.75x of non-nested).
- Always-nested tasks run out of memory on 7 large matrices; selective nesting avoids that, so the D threshold also matters for memory.
- Heuristic constants are empirical and hard-coded; the paper adds further hand-written hybrid conditions (average supernode size &gt; 50, density &lt; 1e-4).
- CHOLMOD version and compiler flags are not stated, so reproducing the numbers needs the archive's scripts.

## Known shortcomings

- Compiler flags and CHOLMOD version not stated; A64FX-only; code is a Zenodo artifact under CC-BY-4.0 (not an OSI software license).
- 1.46x is against the authors' own non-nested OpenMP-task CHOLMOD, not an external library; 1.95x vs multi-threaded-BLAS CHOLMOD is the same data; thresholds tuned on A64FX only, need re-tuning for x86; Zenodo zip has no build instructions; small matrices gain only \~1.07x.

## Caveats and trade-offs

Code, raw data and scripts are in the Zenodo artifact 10.5281/zenodo.5974376 (selective-nesting-main.zip) under CC-BY-4.0, which is not an OSI software license, so reference only. Compiler flags and CHOLMOD version not stated. Niche ARM A64FX hardware with Fujitsu BLAS and OmpSs-1 runtime.

Requires OmpSs runtime and A64FX-specific tuning

## Maintenance

One-off research artifact (Zenodo v3, Oct 2021; paper arXiv 2202.09288, also presented at ESPM2'22) with no ongoing maintenance; reference-only because the artifact is CC-BY-4.0 rather than a software license.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Paper (Le Fevre, Usui, Casas; Zenodo artifact tags it IPDPS 2022) states 1.95x average vs multi-threaded-BLAS CHOLMOD and 1.46x vs best state-of-the-art task method on 60 matrices; artifact code is public and CPU/compiler are stated but compiler flags and CHOLMOD version are not, so not A.
- **Verifier notes:** Paper title is 'Optimization of the Sparse Multi-Threaded Cholesky Factorization for A64FX' (arXiv 2202.09288); artifact title 'A Selective Nesting Approach for the Sparse Multi-threaded Cholesky Factorization'. Orchestrator may set repo_url to https://doi.org/10.5281/zenodo.5974376 (not a correctable field here).
- **Fields the verifier corrected:** `license`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2202.09288>
  - <https://arxiv.org/pdf/2202.09288>
  - <https://zenodo.org/records/5974376>
- **Sources the enricher read:**
  - <https://arxiv.org/abs/2202.09288>
  - <https://arxiv.org/pdf/2202.09288>
  - <https://zenodo.org/records/5974376>
  - <https://nowlab.cse.ohio-state.edu/static/media/workshops/presentations/espm2_22/Valentin_Le_Fevre.pdf>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:task-based-nested-multithreaded-cholmod-for-a64fx-ompss`) · [data/wave8/enrich/raw/paper_task_based_nested_multithreaded_cholmod_for_a64fx_ompss.json](../../../data/wave8/enrich/raw/paper_task_based_nested_multithreaded_cholmod_for_a64fx_ompss.json) (enrichment confidence 0.7)

</details>
