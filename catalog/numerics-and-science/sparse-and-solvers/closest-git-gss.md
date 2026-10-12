# GSS (GRUS Sparse Solver, trial binaries)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · 🔴 abandoned

> Closed-source Windows x64 sparse direct solver (LU/Cholesky/LDLt) with optional CUDA offload; about 2.9x PARDISO on large SPD-type factorizations.

| | |
|---|---|
| **Beats** | Intel MKL PARDISO (Intel Composer XE 2013 SP1), CPU only |
| **Claimed result** | README: 'For many large matrices, GSS is about 2-3 times faster than PARDISO and other CPU based solvers.' User guide Table 1 (numerical factorization time, s, GSS 2.4 CPU-GPU hybrid vs PARDISO): total 315.114 vs 904.244 over 12 matrices, about 2.9x (derived from page data); per matrix up to 5.4x on nd24k (15.880 vs 85.519) and 4.3x on Fault_639 (43.633 vs 186.405), but GSS is slower on msdoor (1.061 vs 0.424), inline_1 (3.385 vs 2.605) and boneS10 (5.585 vs 4.636). The guide itself says 'For matrices need short time computing, PARDISO is faster than GSS.' |
| **Workload** | Numerical factorization time only (not symbolic analysis or solve) on 12 SuiteSparse/UF matrices (msdoor, inline_1, apache2, boneS10, audikw_1, bone010, StocF-1465, nd24k, Fault_639, Flan_1565, Emilia_923, nd12k), both solvers at default parameters; GSS 2.4 runs CPU-GPU hybrid, PARDISO runs CPU only. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-4770 (3.4 GHz), 24 GB RAM, ASUS GTX 780 GPU (compute capability 3.5), CUDA Toolkit 5.5, Windows 7 64-bit (user guide section 7, dated 2014). |
| **Adoption** | 22 stars; 9 commits |
| **Last commit** | 2021-10-05 |
| **Links** | [repository](https://github.com/closest-git/GSS) · [benchmark](https://github.com/closest-git/GSS/blob/master/GSS%202.4.1%20x64%20TRIAL/doc/GSS%202.4%20quick%20start%20user%20guide.pdf) |

## Verdict

Vendor user guide (GSS 2.4, 2014), Table 1: numeric-factorization time only, GSS 2.4 in CPU+GPU hybrid mode vs CPU-only PARDISO from Intel Composer XE 2013 SP1, on a Core i7-4770 with 24 GB, a GTX 780 and CUDA 5.5 under Windows 7 x64. Over 12 SuiteSparse matrices the totals are 315 s vs 904 s (about 2.9x, derived from page data), with GSS losing on the 3 shortest jobs; no harness, compiler flags or thread settings are published.

## Use it when

- Historical or comparative interest: a 2014-era data point for CPU+GPU hybrid supernodal factorization against PARDISO
- Windows x64 with an old CUDA-capable NVIDIA card (compute capability 3.0+, CUDA 5.5) and large SPD or structurally symmetric matrices whose numeric factorization takes tens of seconds; the guide shows 1.5x-5.4x there
- Repeated factorizations of the same sparsity pattern, where the symbolic phase is reused and numeric factorization dominates
- If you can obtain a current commercial licence from the vendor; the repository itself grants no rights

## Skip it when

- Anything that needs source, a licence grant or Linux/macOS: there is no LICENSE file, no source, and only a Windows x64 DLL
- Short factorizations: the guide says PARDISO is faster when computing time is short, and GSS loses on msdoor (1.061 vs 0.424 s), inline_1 and boneS10
- General unsymmetric, symmetric-indefinite or complex matrices if you want the GPU path: hybrid mode supports only types 10 and 11
- Modern GPUs and toolchains: built against CUDA 5.5 and bundles cublas64_55.dll; behaviour on current drivers and GPUs is not documented
- Matrices with more than 2^31 nonzeros: even the 64-bit ('_l') entry points take int\* ptr/ind arrays

## How it is fast

Supernodal elimination-tree factorization in which an 'adaptive task-load-tree split' carves out a subtree of heavy supernodes small enough to factor entirely on the GPU (via cuBLAS), so CPU-GPU transfers stay small, while light independent supernodes run on CPU threads. A dynamic scheduler hands more tasks to whichever device is faster and splits a long-running GPU task to give child tasks to idle CPU threads. The README and the author's 2021 arXiv preprint (2109.14929) describe Q-learning for ordering, task scheduling and pivoting; the 2014 guide that carries the benchmark describes only adaptive scheduling, so how much of the Q-learning work is in this DLL is not documented.

## Compared with alternatives

Rarely: RSLAB is an open-source alternative that reports faster solves than PARDISO, CKTSO covers circuit matrices against KLU with a PARDISO comparison, and BaSpaCho or PanguLU give GPU-accelerated sparse Cholesky/LU on current CUDA with source. Pick GSS only if you already hold a commercial licence and run on Windows.

## Integration

| | |
|---|---|
| **Form** | shared lib (closed-source Windows DLL, trial build) |
| **Dependencies** | GrusLic_de.dll and gss_spd.lic licence files; NVIDIA CUDA 5.5 cuBLAS (cublas64_55.dll bundled) for hybrid mode |
| **Minimum toolchain** | Any C or Fortran compiler that links Windows DLLs (header uses __declspec(dllimport); samples include a VC 2010 x64 project) |
| **Platforms** | Windows x64 only (this repo ships only bin_64); GPU mode needs an NVIDIA GPU with compute capability 3.0+, GTX 780 class or better recommended |
| **Thread safety** | not documented; thread count is set via setting[24] (0 = automatic) |
| **Drop-in for the baseline** | partial: same three-phase workflow and CSC lower-triangle input as PARDISO, but a different API (GSS_\* calls with a 32-entry settings array, not pardiso() with iparm), and only the double-precision real 64-bit DLL is in the trial |

## Gotchas

- The bundled trial licence file gss_spd.lic contains the string 'Thu Dec 31 10:11:11 2015', which looks like a trial expiry date; whether the DLL still runs today is not documented
- GPU hybrid mode is off by default (setting[20]=0 is CPU only, 5 is hybrid), yet the guide says its benchmark used 'default parameters' while running hybrid; the exact settings behind Table 1 are therefore unclear
- The header is still stamped v2.3.0 (2012) and its float solve prototypes differ (GSS_solve_is takes a double rhs, GSS_solve_ls a float rhs); the trial DLL list only has the double-precision real build
- After a failed GSS_numeric call the samples set the handle to NULL ('must set hSolver to NULL') and skip GSS_clear; follow that pattern, because the handle's state after an error is not documented

## Known shortcomings

- Not like-for-like: GPU-hybrid GSS (GTX 780) measured against CPU-only PARDISO (Composer XE 2013 SP1); GSS slower on 3 of 12 matrices (msdoor, inline_1, boneS10); 2014 hardware (i7-4770, Win7, CUDA 5.5).
- Closed-source Windows trial DLLs with a trial .lic file: no license, no source, no harness or flags, so not reproducible; abandoned since 2021-10-05.
- Closed-source trial: gss_spd.lic contains 'Thu Dec 31 10:11:11 2015', apparently an expiry date; only a Windows x64 double-precision real DLL ships. Guide says both solvers used default parameters, yet GPU hybrid mode is off by default (setting[20]=0), so Table 1's settings are unclear. The '64-bit' (_l) API still takes int\* index arrays (2^31 nonzero limit). Claim cannot be reproduced.

## Caveats and trade-offs

Closed-source trial distribution: the repo holds only Windows x64 DLLs (GSS_Dl.dll, GrusLic_de.dll, cublas64_55.dll), a trial license file (gss_spd.lic), headers, C/Fortran samples and a PDF guide; no license grant, no source. The speedup compares a CPU+GPU hybrid run against CPU-only PARDISO on 2013-era hardware, covers numerical factorization only, and GSS loses on 3 of 12 matrices (smaller/shorter jobs). No benchmark harness or compiler flags are published, so the numbers cannot be reproduced. Built against CUDA 5.5. Last commit 2021-10-05; the benchmarked release (GSS 2.4) dates from 2014. The linked arXiv paper (2109.14929, Q-learning for sparse Gaussian elimination) is a preprint; it could not be opened from this environment.

Closed-source commercial solver; the repo contains only 'GSS 2.4.1 x64 TRIAL' binaries with C and Fortran samples and a user guide PDF. Claims hybrid CPU+GPU (CUDA) execution with a Q-learning scheduler.

## Maintenance

Abandoned: the benchmarked release is from 2014, the repo's last commit is from October 2021, and it is a closed-source trial with no licence grant, so treat it as reference only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README only repeats a '2-3 times faster than PARDISO' headline, but the bundled user guide (GSS 2.4 quick start, section 7, Table 1) gives first-party numeric-factorization times for 12 SuiteSparse (UF) matrices against Intel Composer XE 2013 SP1 PARDISO, naming CPU, GPU, CUDA version and OS. The library ships only as closed Windows binaries with no benchmark code or compiler flags, so the numbers are first-party and not reproducible: C.
- **Verifier notes:** README alone has only the headline; the real numbers are in the user guide PDF inside the trial folder (Table 1, page 15), so benchmark_url now points there. The headline 2-3x holds for long-running matrices (sum ratio about 2.9x), but it is GPU-assisted GSS against CPU-only PARDISO, and PARDISO wins on short jobs. Metadata checked on github.com: 22 stars, 3 forks, 9 commits, not a fork, not archived, no license file; the grusoft.com comparison image and arxiv.org were not opened (arxiv.org is blocked by egress here).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `baseline`, `caveats`
- **Shortcomings recorded by:** User guide Table 1: 12 SuiteSparse matrices, numerical factorization only, 315.1 s vs PARDISO 904.2 s, about 2.9x (derived from page data); best case nd24k 5.4x.; enrichment
- **Pages the verifier opened:**
  - <https://github.com/closest-git/GSS>
  - <https://github.com/closest-git/GSS/commits>
  - <https://github.com/closest-git/GSS/tree/master/GSS%202.4.1%20x64%20TRIAL>
  - <https://github.com/closest-git/GSS/tree/master/GSS%202.4.1%20x64%20TRIAL/bin_64>
  - <https://raw.githubusercontent.com/closest-git/GSS/HEAD/README.md>
  - <https://raw.githubusercontent.com/closest-git/GSS/master/GSS%202.4.1%20x64%20TRIAL/doc/GSS%202.4%20quick%20start%20user%20guide.pdf>
- **Sources the enricher read:**
  - <https://github.com/closest-git/GSS>
  - <https://raw.githubusercontent.com/closest-git/GSS/HEAD/README.md>
  - <https://raw.githubusercontent.com/closest-git/GSS/master/GSS%202.4.1%20x64%20TRIAL/doc/GSS%202.4%20quick%20start%20user%20guide.pdf>
  - <https://github.com/closest-git/GSS/tree/master/GSS%202.4.1%20x64%20TRIAL>
  - <https://github.com/closest-git/GSS/tree/master/GSS%202.4.1%20x64%20TRIAL/include>
  - <https://raw.githubusercontent.com/closest-git/GSS/master/GSS%202.4.1%20x64%20TRIAL/include/grus_sparse_solver.h>
  - <https://github.com/closest-git/GSS/tree/master/GSS%202.4.1%20x64%20TRIAL/bin_64>
  - <https://raw.githubusercontent.com/closest-git/GSS/master/GSS%202.4.1%20x64%20TRIAL/bin_64/gss_spd.lic>
  - <https://github.com/closest-git/GSS/tree/master/GSS%202.4.1%20x64%20TRIAL/Samples>
  - <https://github.com/closest-git/GSS/tree/master/GSS%202.4.1%20x64%20TRIAL/Samples/c>
  - <https://raw.githubusercontent.com/closest-git/GSS/master/GSS%202.4.1%20x64%20TRIAL/Samples/c/gss_spd_demo_en.c>
  - <https://github.com/closest-git/GSS/issues>
  - WebSearch: arXiv 2109.14929 abstract via search snippets (arxiv.org not opened)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/closest-git/gss`) · [data/wave8/enrich/raw/github_com_closest_git_gss.json](../../../data/wave8/enrich/raw/github_com_closest_git_gss.json) (enrichment confidence 0.7)

</details>
