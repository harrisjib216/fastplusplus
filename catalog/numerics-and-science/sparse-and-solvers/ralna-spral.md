# SPRAL SSIDS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Fortran (with C interface; GPU build via CUDA)` · `BSD-3-Clause` · 🟢 active

> BSD-licensed multicore/GPU sparse symmetric indefinite LDL^T solver (SSIDS); paper claims beat HSL and PARDISO, unverified here.

| | |
|---|---|
| **Beats** | Not verified from an opened page. Per search snippets only: the ACM TOMS 2016 GPU paper compares against 'a state-of-the-art multifrontal solver on a multicore CPU' (not named in the snippet); the Duff-Hogg-Lopez a-posteriori-threshold-pivoting paper (RAL-TR-2016-017 / NLAFET Working Note 21) compares SSIDS v2 with HSL_MA86, HSL_MA97 and PARDISO on a multicore machine. MUMPS is not named in either snippet. |
| **Claimed result** | No numbers in the repo. From search-engine snippets of paper abstracts (not opened): the TOMS 2016 paper says that for large indefinite problems SSIDS on a GPU achieves up to 4.6x over a state-of-the-art multifrontal solver on a multicore CPU; the APTP paper says SSIDS v2 'performs favorably' against HSL_MA86, HSL_MA97 and PARDISO on a multicore machine (no ratio in the snippet). An independent study (Swirydowicz et al., 'Linear solvers for power grid optimization problems: a review of GPU-accelerated linear solvers', Parallel Computing, arXiv 2106.13909) found, per snippet, that turning on GPU acceleration in SSIDS slowed it down compared with CPU-only, and that all GPU solvers tested were slower than one-thread MA57 on power-grid KKT matrices; on CPU, SSIDS was fastest for the smallest case (ACTIVSg2000). |
| **Workload** | Sparse symmetric indefinite LDL^T direct solves on CPU, multi-GPU and heterogeneous nodes; the README cites Hogg, Ovtchinnikov and Scott, ACM TOMS 42(1), 2016 for SSIDS. |
| **Metric** | throughput |
| **Adoption** | 142 stars |
| **Last commit** | 2026-08-14 |
| **Links** | [repository](https://github.com/ralna/spral) |

## Verdict

No benchmark could be opened: the repo has no performance numbers and the papers are on blocked hosts. Search snippets say the TOMS 2016 paper reports up to 4.6x for large indefinite problems against an unnamed state-of-the-art multifrontal solver on a multicore CPU (GPU version), and the SISC 2020 APTP paper (42(2) C23-C42) compares SSIDS v2 with HSL_MA86, HSL_MA97 and PARDISO with no ratio in the snippet; an independent power-grid study (snippet) found GPU mode slower than CPU-only and than one-thread MA57. Treat speed as unverified (tier D).

## Use it when

- Large sparse symmetric indefinite systems (KKT and saddle-point matrices from interior-point optimization, mixed finite elements) on a multicore node where you need LDL^T with 2x2 pivoting and the inertia, under a BSD licence instead of HSL MA57/MA97 or MKL PARDISO terms.
- Ipopt or other C/C++ optimizers that want an open-source parallel alternative to MUMPS or MA27: Ipopt ships an interface (linear_solver=spral; Ipopt 3.14.13 needs SPRAL v2023.03.29 or later).
- Sequences of factorizations with a fixed sparsity pattern: analyse once and reuse akeep for many ssids_factor calls.
- Workflows that need run-to-run bit-identical results: the docs promise bit-compatibility given bit-compatible BLAS and compiler options.
- Very large problems on NVIDIA GPU nodes, where subtrees above 5e9 flops are offloaded (the paper's up to 4.6x claim is for large indefinite problems).

## Skip it when

- Small or medium KKT systems such as power-grid optimal power flow: an independent study (Swirydowicz et al., Parallel Computing, seen only as a snippet) found SSIDS's GPU mode slower than its CPU mode and slower than one-thread MA57, and Ipopt merged PR #677 (2023) 'Linear solvers such as MUMPS should be prefered over SPRAL' when choosing its default.
- Positive definite problems: the docs warn that SSIDS is designed for indefinite systems and its Cholesky path may be slower than a dedicated Cholesky solver (CHOLMOD, BaSpaCho).
- Solve-dominated workloads (many right-hand sides or many repeated solves per factorization): the docs state the solve phase runs in serial.
- Unsymmetric, complex or single-precision matrices, or distributed-memory (MPI) runs: SSIDS is real double symmetric only and the build has no MPI dependency.
- Windows, or host applications that cannot set OMP_CANCELLATION=TRUE process-wide: Windows support is an open question (issue #137), and without that variable SSIDS fails with error -53.

## How it is fast

The assembly tree is cut into leaf subtrees that are pre-assigned to NUMA regions or GPUs and factored in parallel, after which all CPU cores cooperate on the root subtree (OpenMP tasks); small leaf subtrees below small_subtree_threshold (4e6 flops) are merged into one task to cut scheduling overhead. On CPU the default pivoting is block a posteriori threshold pivoting (APTP, Duff-Hogg-Lopez): blocks are eliminated optimistically with a Cholesky-like communication pattern and pivots that fail the threshold test afterwards only force recomputation of their block column, which keeps the factorization task-parallel where classic threshold partial pivoting is serial. Dense kernels are blocked (cpu_block_size 256, inner block 32) with AVX/AVX2/AVX-512 intrinsics in SimdVec.hxx plus BLAS/LAPACK; the GPU path (TOMS 2016 paper) runs subtrees of at least min_gpu_work (5e9 flops) in CUDA with cuBLAS.

## Compared with alternatives

Most catalogued sparse direct siblings are LU solvers (Basker, NICSLU, CKTSO, HYLU, PanguLU) or Cholesky-only (BaSpaCho, Sympiler); pick SPRAL SSIDS when the matrix is symmetric indefinite and you need 2x2 pivoting plus inertia under BSD with optional GPU offload. RSLAB (Rust LDL^T) has measured numbers against PARDISO but is Rust; for SPD problems BaSpaCho's measured wins over CHOLMOD are the better bet.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | BLAS, LAPACK, METIS (4 or 5, optional 64-bit idx), OpenMP; hwloc optional (topology detection; needs CUDA support for GPU use); CUDA 10+ with cuBLAS optional |
| **Minimum toolchain** | Fortran compiler (gfortran, Intel ifx/ifort, NAG, NVIDIA HPC or LLVM flang) plus C99 and C++11 compilers; Meson 0.63+ |
| **Platforms** | Linux x86-64 primarily (AVX/AVX2/AVX-512 kernels when compiled with those flags, scalar fallback otherwise); macOS handled in the build but issue #258 reports a test failure on aarch64-darwin; NVIDIA GPUs optional |
| **Thread safety** | not documented; each analyse/factor/solve call parallelizes internally with OpenMP and needs OMP_CANCELLATION=TRUE (and OMP_PROC_BIND=TRUE for NUMA placement); state lives in per-problem akeep/fkeep handles |
| **Drop-in for the baseline** | no |

## Gotchas

- Set OMP_CANCELLATION=TRUE and OMP_PROC_BIND=TRUE in the environment before the OpenMP runtime starts, or factorization returns error -53 (cancellation) or warning +50 (binding); these are process-wide settings that also affect the host application.
- meson.build adds no -m flags, and SimdVec.hxx uses AVX intrinsics only under __AVX__/__AVX2__/__AVX512F__, so a default build runs the scalar kernels; pass e.g. -Dcpp_args=-march=native (inference from the source; not documented). For GPU builds set -Dgpu_arch to the card's sm_XX: meson.build warns a mismatched JIT-compiled arch can silently produce wrong results.
- ssids_free must be called explicitly (going out of scope leaks C++/CUDA memory, and akeep must outlive its fkeeps); open issues include memory leaks (#259), a segfault in assemble_expected_contrib on a large Ipopt problem with 5.7M Hessian nonzeros (#218, no maintainer reply) and GPU test failures with CUDA 12.5 (#223).
- Ipopt's ChangeLog records a use-after-free in its SPRAL interface when solving a second structurally singular system (fixed in Ipopt 3.14.20, 2026-08-27, PR #848), so use Ipopt 3.14.20 or later if you go through it.

## Known shortcomings

- Tier D: the repo publishes no numbers. The TOMS 2016 paper (up to 4.6x vs an unnamed multicore CPU multifrontal solver) and the APTP paper (vs HSL_MA86, HSL_MA97, PARDISO) were blocked (centaur.reading.ac.uk, nlafet.eu, osti.gov) and seen only as snippets; retier candidate to B. An independent study (Swirydowicz, Parallel Computing) found SSIDS's GPU mode slower than its CPU mode and than single-thread MA57.
- The solve phase is serial and the docs say the positive-definite path may trail a dedicated Cholesky. The default meson build adds no -march flags, so the AVX kernels are probably not compiled in (inferred from source, undocumented); a mismatched gpu_arch can silently give wrong results (meson.build comment). Open issues #218 (segfault on a large Ipopt problem, no reply), #223 (GPU tests fail on CUDA 12.5), #259 (memory leaks), #258 (aarch64-darwin test failure); Ipopt PR #677 (2023) ranked MUMPS above SPRAL as the default.
- Tasseff et al. (arXiv 1909.08104, snippet only) rank SPRAL's GPU solver worst among Ipopt linear solvers, with MA57 and MUMPS best.

## Caveats and trade-offs

Evidence not reachable: the SSIDS GPU paper (Hogg, Ovtchinnikov and Scott, ACM TOMS 42(1), 2016, doi 10.1145/2756548 as cited in the README; preprint RAL-P-2014-006 on epubs.stfc.ac.uk) and the CPU a-posteriori-pivoting report cited in docs/Fortran/ssids.rst are on egress-blocked hosts (doi.org, dl.acm.org, epubs.stfc.ac.uk, nlafet.eu, centaur.reading.ac.uk, osti.gov), so the figures in claimed_speedup come from search snippets only and no ratio is verified. A session that can open the TOMS paper or the APTP report could retier to B (peer reviewed, against HSL codes and PARDISO). Independent counter-evidence (Swirydowicz et al., Parallel Computing, per snippet): on power-grid optimization KKT matrices SSIDS's GPU mode was slower than its CPU mode and slower than one-thread MA57, so the GPU claim is workload dependent. The baselines are not in the catalog's list for this category (SuiteSparse, Eigen sparse, PETSc), so baseline_in_list is false. The library is Fortran with a C interface (callable from C++). The ChangeLog entry of 2016-09-23 says SSIDS v2 added CPU, multi-GPU and heterogeneous execution. SSIDS needs OMP_CANCELLATION=TRUE and OMP_PROC_BIND=TRUE or it fails with error -53 (README). [retier] 2026-10-03 retier attempt: arXiv 1909.08104 (Tasseff, Coffrin, Waechter, Laird, 'Exploring Benefits of Linear Solver Parallelism on Modern Nonlinear Optimization Applications') is egress-blocked here. Per search snippets only (not opened): in Ipopt, MA57 and MUMPS were the best performers over most of the problem set, SPRAL (CPU) had difficulty solving easy problems quickly but eventually solved as many problems as PARDISO, and SPRAL (GPU) was the worst performer. This matches the Swirydowicz et al. counter-evidence already recorded. No SPRAL-versus-HSL ratio has been verified from an opened page.

Needs METIS and hwloc (hwloc built with CUDA support for GPU use) and a BLAS/LAPACK; builds with Meson. Environment variables OMP_CANCELLATION=TRUE and OMP_PROC_BIND=TRUE must be set or SSIDS fails with error flag -53. Per its docs the solve phase is performed in serial at present. Does posdef Cholesky or indefinite factorization with 1x1 and 2x2 pivots; leaf subtrees are pre-assigned to NUMA regions or GPUs.

## Maintenance

Active (version 2025.09.18 in meson.build, last commit 2026-08-14, 142 stars, 19 open issues including an unanswered large-problem segfault), BSD-3-Clause and maintained by STFC's numerical analysis group; a mixed Fortran/C++/CUDA build with external METIS and BLAS, so not something to vendor casually.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** benchmark_url is null and the repo (README, LICENCE, docs/Fortran/ssids.rst) has no performance numbers; the SSIDS papers that carry numbers (ACM TOMS 2016, Duff-Hogg-Lopez APTP report) are on egress-blocked hosts and were seen only as search snippets, so the record cannot go above D here.
- **Verifier notes:** Repo metadata checks out (BSD-3-Clause LICENCE, 142 stars, last commit 2026-08-14, active). Kept at D because no numbers page could be opened; it is a notable library (Ipopt linear-solver option, cited TOMS paper), so it should not be dropped. Retier candidate to B once the TOMS 2016 paper or RAL-TR-2016-017 can be opened; note the independent power-grid study where SSIDS GPU lost to one-thread MA57.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/ralna/spral>
  - <https://github.com/ralna/spral/commits>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/README.md>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/LICENCE>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/docs/Fortran/ssids.rst>
- **Sources the enricher read:**
  - <https://github.com/ralna/spral/tree/master/src/ssids/cpu>
  - <https://github.com/ralna/spral/tree/master/src/ssids/cpu/kernels>
  - <https://github.com/ralna/spral/issues>
  - <https://github.com/ralna/spral/issues/218>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/README.md>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/LICENCE>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/meson.build>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/meson_options.txt>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/docs/Fortran/ssids.rst>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/docs/C/ssids.rst>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/include/spral_ssids.h>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/src/ssids/cpu/kernels/SimdVec.hxx>
  - <https://raw.githubusercontent.com/ralna/spral/HEAD/src/ssids/cpu/kernels/ldlt_app.cxx>
  - <https://raw.githubusercontent.com/NLAFET/SyLVER/HEAD/README.md>
  - <https://raw.githubusercontent.com/coin-or/Ipopt/HEAD/ChangeLog.md>
  - <https://github.com/coin-or/Ipopt/issues/677>
  - WebSearch: Duff Hogg Lopez 'a posteriori threshold pivoting' SSIDS HSL_MA97 PARDISO SISC 2020 (snippets only)
  - WebSearch: 'a posteriori threshold pivoting' OR SSIDS sparse LDLT pdf site:github.com (no usable copy found)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ralna/spral`) · [data/wave8/enrich/raw/github_com_ralna_spral.json](../../../data/wave8/enrich/raw/github_com_ralna_spral.json) (enrichment confidence 0.65)

</details>
