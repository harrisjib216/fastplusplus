# HYLU

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C (C API header with extern "C", closed-source prebuilt library)` · `None stated: no LICENSE file, and the README, include/hylu.h and doc/ug_en.pdf give no terms; prebuilt binaries only (unlike CKTSO, no license key file is required)` · 🟢 active

> Closed-source multicore sparse LU/Cholesky solver for general large matrices; first-party 1.70x geomean over MKL PARDISO one-time solve.

| | |
|---|---|
| **Beats** | Intel MKL PARDISO |
| **Claimed result** | One-time solve: 1.70X faster than Intel MKL PARDISO on geometric mean in total time (preprocessing + factorization + solve); 2.36X faster in numerical factorization, 1.48X faster in preprocessing, but forward-backward substitution 18% slower. Repeated solve with identical sparsity pattern: 2.90X faster in numerical factorization, 2.53X faster in factorization + solve total, forward-backward substitution 20% slower. Also claims an order of magnitude higher accuracy (residual) on geometric mean. |
| **Workload** | Parallel sparse LU solve (preprocessing, numerical factorization, forward-backward substitution) of 37 SuiteSparse Matrix Collection matrices with dimensions 525,825 to 5,558,326, wall time with 16 threads. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6130 @ 2.1GHz, 256GB memory, Ubuntu 24.04 LTS, 16 threads |
| **Compiler and flags** | Test code compiled with gcc 13.3.0 (flags not stated); HYLU library compiled with gcc 8.5.0 on Rocky Linux 8.10 (flags not stated); MKL 2025.3; HYLU version 20260331 |
| **Adoption** | 9 stars, 1 fork |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/chenxm1986/hylu) · [benchmark](https://raw.githubusercontent.com/chenxm1986/hylu/HEAD/doc/results.pdf) |

## Verdict

Author's results.pdf: HYLU 20260331 vs Intel MKL PARDISO 2025.3, 16 threads on one Xeon Gold 6130, 37 SuiteSparse matrices (n 525,825 to 5,558,326): one-time solve 1.70x geomean total (factorization 2.36x, preprocessing 1.48x, substitution 18% slower); repeated solve 2.90x factorization and 2.53x factor+solve, substitution 20% slower; residuals about an order of magnitude lower on geomean. PARDISO settings and compiler flags are not stated, no benchmark harness is public, and the earlier arXiv preprint (34 matrices) reported 1.95x and 2.40x factorization speedups with near-parity on relatively dense matrices.

## Use it when

- One-time or repeated solves of large general sparse systems (the benchmark set is n = 525,825 to 5,558,326) on a 16-core-class x86-64 server where MKL PARDISO's factorization time dominates.
- Repeated factorization with a fixed sparsity pattern (Newton loops, transient simulation, time stepping): call Analyze once with repeat=true and the first-party results show 2.90x geomean in factorization and faster factor+solve than PARDISO on all 37 test matrices.
- Very sparse, circuit-like or KKT-like matrices where PARDISO's METIS-based fill-in blows up (results.pdf names ASIC_680k, ASIC_680ks, circuit5M and nlpkkt80 as PARDISO's worst cases).
- Projects that can take a binary-only dependency and want a simple C API with 64-bit index variants, complex Hermitian support and condition-number/determinant output without OpenMP.

## Skip it when

- Anything that must be open source, audited, rebuilt or redistributed under clear terms: there is no source and no license file or terms anywhere in the repo, only x86-64 Linux .so and Windows .dll binaries.
- ARM, Apple Silicon, 32-bit or CPUs without AVX2 and FMA; only x64 Windows 7/10/11 and Linux (CentOS 7/8 named) are supported.
- Solve-dominated workloads (one factorization, many right-hand sides): forward-backward substitution is 18-20% slower than PARDISO on geometric mean, partly from iterative refinement.
- Symmetric indefinite systems that need pivoting: the LDL^H path does no pivoting at all, and the user guide's fallback is to solve them as unsymmetric with the full matrix.
- Shared or oversubscribed machines and small problems: the guide says performance degrades severely if worker threads exceed idle cores, and no results exist below n = 525,825 or for sequential runs.

## How it is fast

The core is a parallel up-looking (row-by-row) LU and Cholesky factorization that switches between hybrid numerical kernels according to local sparsity, so very sparse regions avoid dense supernode overhead while denser regions run as supernodes (minimum 32 columns by default); the arXiv abstract, seen only as a search snippet, says this is why it is much faster than PARDISO on highly sparse matrices and about even on relatively dense ones. Preprocessing combines static pivoting and scaling with a choice of four fill-reducing orderings (two approximate-minimum-degree and two parallel nested-dissection variants, auto-selected, or best-of-all when repeat=true). Stability comes from static pivoting plus dynamic pivoting restricted to the diagonal supernode, pivot perturbation and automatic iterative refinement, which keeps the factorization's data structures static and parallel; threads are native OS threads (no OpenMP), and the builds link either MKL BLAS or OpenBLAS.

## Compared with alternatives

Pick HYLU over CKTSO or NICSLU (same author, tuned for circuit matrices and KLU-style refactorization) when the matrices are general FEM/CFD/KKT systems or symmetric/SPD, and over GSS (binary-only, compared with a 2013 PARDISO) or RSLAB (Rust, factorization slower than PARDISO) when you want the fastest PARDISO replacement on x86 multicore; choose Basker (open source in Trilinos) or PanguLU (distributed multi-GPU) when you need source or scale beyond one node.

## Integration

| | |
|---|---|
| **Form** | shared lib (prebuilt .so / .dll, four per platform, MKL-BLAS or OpenBLAS builds) plus one C header; no source |
| **Dependencies** | README says only the header and one library file are needed; Linux links also need -lpthread -lm -ldl (-lrt on old distros); Windows uses the .lib import library and the .dll |
| **Minimum toolchain** | C99 (stdbool.h) or C++ via extern "C"; demos build with gcc -O3 -std=gnu11; results.pdf says the library is built with gcc 8.5.0 on Rocky Linux 8.10 (folder names say centos7_x64) |
| **Platforms** | x86-64 only, AVX2 and FMA required (AVX-512 recommended); 64-bit Linux and Windows 7/10/11 |
| **Thread safety** | not documented for concurrent calls; each solver instance creates and owns its worker threads, and the guide warns that the total thread count must not exceed idle cores |
| **Drop-in for the baseline** | partial — same analyze / factorize / solve phases and matrix types as MKL PARDISO, but a different C API, 0-based CSR input with only the upper triangle for symmetric types, and no source to adapt |

## Gotchas

- Pivoting is limited to the diagonal supernode, so some unsymmetric systems come back inaccurate; the user guide's fix is parm[23]=0, a larger parm[6] and sequential factorization, which costs speed. Check parm[11] (perturbed pivots) and the residual yourself.
- Passing ax=NULL to HYLU_Analyze disables static pivoting and scaling for unsymmetric matrices; the guide strongly recommends passing values.
- Builds linked with Intel MKL BLAS leak memory (the user guide blames MKL BLAS itself); use the OpenBLAS build for long-running processes if that matters.
- With parm[23]=0 and several threads, the parallel nested-dissection ordering is non-deterministic; even with the default setting, sequential and parallel numerical results may differ slightly.

## Known shortcomings

- Binary-only (no licence text); numbers in doc/results.pdf (Xeon Gold 6130, gcc 13.3.0/8.5.0, no flags, no harness); no paper PDF in the repo. The residual chart shows relative residual about 1 or higher on CurlCurl_2, CurlCurl_4 and dgreen (PARDISO worse), yet those timings count toward the means; the geomean is lifted by 4 PARDISO fill-in outliers; HYLU is slower in total time on af_shell10 (\~0.8x). Read from charts, approximate.
- The forward-backward solve is 18-20% slower than PARDISO; the symmetric-indefinite LDL^H does no pivoting, and pivoting is limited to the diagonal supernode, so some unsymmetric systems come back inaccurate; MKL-BLAS builds leak memory (user guide); no license terms anywhere. The arXiv 2509.07690 snippet says near parity with PARDISO on relatively dense matrices; the paper was blocked.

## Caveats and trade-offs

First-party evidence only: README and doc/results.pdf by the author, plus the author's arXiv preprint 2509.07690 (not opened; arXiv is unreachable here, and no copy of the paper is checked into the repo: doc/ holds only results.pdf, ug_cn.pdf and ug_en.pdf). A WebSearch snippet of the preprint abstract gives older figures: 34 SuiteSparse matrices, numerical factorization 1.95X (one-time) and 2.40X (repeated) faster than MKL PARDISO, versus 2.36X and 2.90X on 37 matrices in results.pdf (version 20260331). No benchmark code is public (demo/ only builds examples with gcc -O3 -std=gnu11 and solves sample .mtx files), compiler flags for the timed builds and the MKL PARDISO settings (ordering, iparm) are not stated, and all results are 16-thread wall time on one Xeon Gold 6130 with no sequential numbers. No license file or terms anywhere, and only binaries are provided (Linux .so built for CentOS 7 and Windows DLLs, MKL or OpenBLAS variants, x64 with AVX2/FMA), so it can be neither audited nor copied; usability is reference and has_code is false. Baseline is Intel MKL PARDISO, not SuiteSparse, Eigen sparse or PETSc. Per-matrix charts in results.pdf (read visually, approximate): in one-time total time HYLU is slower than PARDISO on af_shell10 (about 0.8x) and roughly even on CurlCurl_4 and a few others, while off-scale wins on ASIC_680k, ASIC_680ks, circuit5M and nlpkkt80, where PARDISO creates huge fill-in, lift the geometric mean; forward-backward substitution is slower on most matrices. The residual chart shows HYLU relative residuals near or above 1 on CurlCurl_2, CurlCurl_4 and dgreen (PARDISO worse still) and about 0.1 on nv2, so those timings come from runs that did not produce accurate solutions; the text acknowledges only Hamrle3. The matrix set is limited to 37 large SuiteSparse matrices (n from 525,825 to 5,558,326), and results.pdf (created 2026-04-01) uses version 20260331 while the latest is 20260930. Repo history runs from 2025-09-12 (initial release) to 2026-09-30 (39 commits). A sibling project by the same author, CKTSO, is already catalogued (https://github.com/chenxm1986/cktso); HYLU is a separate general-purpose solver, not a duplicate.

Closed source: the repo ships one C header (include/) plus prebuilt x64 libraries (centos7_x64_mkl, centos7_x64_openblas, win7_x64_mkl, win7_x64_openblas) and a demo; no solver source. Needs an x64 CPU with AVX2 and FMA; Windows or Linux only (README names Windows 7/10/11 and CentOS 7/8, other mainstream Linux said to work). Supports unsymmetric, symmetric indefinite and symmetric positive-definite matrices, real and complex, 32-bit and 64-bit index APIs. Forward-backward substitution is slower than MKL PARDISO (18-20% on geometric mean), so the win comes from preprocessing and factorization.

## Maintenance

Actively developed (version 20260930, last commit 2026-09-30, 39 commits since 2025) but binary-only with no license terms, so it is a reference to call, not code to copy or ship without asking the author.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/results.pdf (first-party, 5 pages) compares HYLU 20260331 with Intel MKL PARDISO 2025.3 on 37 SuiteSparse matrices and states CPU (Xeon Gold 6130), compilers (gcc 13.3.0 test code, gcc 8.5.0 library) and 16 threads, but no flags, no PARDISO settings and no public benchmark harness (demo/ only solves sample matrices); the library is binary-only and the arXiv preprint is not peer-reviewed as far as seen, so C.
- **Verifier notes:** All claimed numbers (1.70X, 2.36X, 1.48X, 18% slower FBS, 2.90X, 2.53X, 20% slower, order-of-magnitude accuracy) appear verbatim in doc/results.pdf text. No paper PDF is checked into the repo (unlike CKTSO's doc/tcad.pdf), so no B retier is possible; shortcoming worth recording: per the residual chart, several timed matrices (CurlCurl_2, CurlCurl_4, dgreen) were not solved accurately by either solver, and the geometric mean is lifted by four matrices where PARDISO fills in pathologically.
- **Fields the verifier corrected:** `license`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/chenxm1986/hylu>
  - <https://github.com/chenxm1986/hylu/tree/main/doc>
  - <https://github.com/chenxm1986/hylu/commits/main>
  - <https://github.com/chenxm1986/hylu/tree/main/demo>
  - <https://github.com/chenxm1986/hylu/tree/main/demo/unsym_r>
  - <https://github.com/chenxm1986/hylu/tree/main/centos7_x64_mkl>
  - <https://raw.githubusercontent.com/chenxm1986/hylu/HEAD/README.md>
  - <https://raw.githubusercontent.com/chenxm1986/hylu/HEAD/doc/results.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/hylu/HEAD/doc/ug_en.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/hylu/HEAD/include/hylu.h>
  - <https://raw.githubusercontent.com/chenxm1986/hylu/HEAD/demo/Makefile>
- **Sources the enricher read:**
  - <https://github.com/chenxm1986/hylu>
  - <https://github.com/chenxm1986/hylu/commits/main>
  - <https://github.com/chenxm1986/hylu/issues?q=is%3Aissue>
  - <https://github.com/chenxm1986/hylu/tree/main/centos7_x64_openblas>
  - <https://raw.githubusercontent.com/chenxm1986/hylu/HEAD/README.md>
  - <https://raw.githubusercontent.com/chenxm1986/hylu/HEAD/include/hylu.h>
  - <https://raw.githubusercontent.com/chenxm1986/hylu/HEAD/doc/results.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/hylu/HEAD/doc/ug_en.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/hylu/HEAD/demo/Makefile>
  - <https://raw.githubusercontent.com/chenxm1986/hylu/HEAD/demo/unsym_r/unsym_r.c>
  - https://www.arxiv.org/pdf/2509.07690 (EGRESS_BLOCKED; abstract read from a search snippet only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/chenxm1986/hylu`) · [data/wave8/enrich/raw/github_com_chenxm1986_hylu.json](../../../data/wave8/enrich/raw/github_com_chenxm1986_hylu.json) (enrichment confidence 0.8)

</details>
