# ReLAPACK

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT` · 🔴 abandoned

> Recursive C replacements for LAPACK compute kernels (LU, Cholesky, LDL, trtri, Sylvester) that beat reference LAPACK's blocked versions.

| | |
|---|---|
| **Beats** | reference LAPACK, OpenBLAS LAPACK routines and Intel MKL LAPACK routines |
| **Claimed result** | README: 'ReLAPACK's routines not only outperform the reference LAPACK but also improve upon the performance of tuned implementations, such as OpenBLAS and MKL.' No numbers on the README page. |
| **Workload** | Recursive implementations of LAPACK compute kernels (LU, Cholesky, triangular inversion, Sylvester and Lyapunov solvers and others) that call BLAS; README says they outperform LAPACK and improve on OpenBLAS and MKL. |
| **Metric** | throughput |
| **Adoption** | 44 stars; vendored in OpenBLAS (relapack/ directory, optional build); published as ACM TOMS Algorithm 979 |
| **Last commit** | 2022-02-20 |
| **Links** | [repository](https://github.com/HPAC/ReLAPACK) · [benchmark](https://github.com/HPAC/ReLAPACK/blob/master/README.md) |

## Verdict

The repo states only that ReLAPACK outperforms reference LAPACK and improves on OpenBLAS and MKL; no numbers, hardware or compiler details are in any repo file. The measurements are in Peise and Bientinesi, arXiv:1602.06763 (ACM TOMS Algorithm 979), which could not be opened here (arxiv.org blocked), so the claim stays directional (tier D).

## Use it when

- Code that calls reference LAPACK (or a LAPACK without tuned factorizations) for LU, Cholesky, LDL^T, triangular inversion or Sylvester solves and you want a faster drop-in without changing call sites.
- Matrix sizes where blocked LAPACK's panel factorization is BLAS-2 bound and a good BLAS-3 is available underneath (OpenBLAS, BLIS, MKL, Accelerate).
- Sylvester (xtrsyl, xtgsyl) and generalized symmetric-definite reduction (xsygst) workloads, which most tuned libraries leave as reference LAPACK code.
- Building OpenBLAS with BUILD_RELAPACK=1 (and RELAPACK_REPLACE=1 to override the LAPACK symbols), which uses OpenBLAS's maintained copy of this code.

## Skip it when

- QR, eigenvalue reductions (sytrd, gehrd, gebrd) and SVD: not covered, because recursive variants need extra FLOPs (coverage.md).
- ILP64 (64-bit integer) builds: the upstream code uses plain int for every dimension and pivot; only OpenBLAS's copy was converted to blasint/INTERFACE64 (OpenBLAS commits 9a19616, 798c448, 2019).
- Symmetric indefinite LDL^T (xsytrf/xhetrf) from upstream: the workspace size it reports and allocates (n\*(n/2)) can be smaller than what the recursion writes when the split exceeds n/2; OpenBLAS fixed this on 2026-08-08 (commit 4a4cd8f, 'silently corrupting both the factorization and the heap'), upstream src/dsytrf.c still has the old formula.
- When the vendor library already has recursive or parallel factorizations (OpenBLAS's own getrf/potrf, MKL): the gain over them is claimed in the paper but no numbers are in the repo, and the code was last compared with 2016-2017 OpenBLAS and MKL versions.
- Projects needing an actively maintained upstream: the HPAC repo's last commit is a 2022 typo fix, its two issues are unanswered (issue #5 on XERBLA arguments is still open), and later bug fixes went only into OpenBLAS's copy.

## How it is fast

Instead of LAPACK's fixed-block-size loops with BLAS-2 panel factorizations, each routine splits the matrix into two halves recursively (split point rounded so one half is a multiple of 8 or 16 elements for cache-line alignment) and does the trailing updates with large BLAS-3 calls (dtrsm, dgemm), so almost all FLOPs run in the tuned GEMM. Recursion stops at a crossover size (default 24) where LAPACK's unblocked xxxf2 kernel takes over, which removes the block-size tuning that blocked LAPACK needs. xsygst can use an n^2/2 scratch buffer to do about 30% fewer FLOPs than LAPACK (config.md).

## Compared with alternatives

Pick ReLAPACK when you want unchanged LAPACK call sites in C/C++/Fortran and need faster getrf/potrf/sytrf/trtri/trsyl on top of whatever BLAS you already use; BLASFEO is faster for matrices in the tens but uses its own panel-major API, and RecursiveFactorization.jl applies the same recursive-LU idea only to Julia and only to LU.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | a BLAS plus LAPACK (for unblocked kernels such as dgetf2, dlaswp, dsytf2); tests need LAPACK 3.5.0 or newer |
| **Minimum toolchain** | C99 compiler (make.inc default: gcc -O3 -std=c99 -pedantic); plain Makefile, no CMake |
| **Platforms** | any platform with a Fortran-convention BLAS/LAPACK; no architecture-specific code (speed comes from the BLAS underneath) |
| **Thread safety** | not documented; from the source the routines keep no global state (stack values plus per-call malloc'd workspace), so concurrent calls rely on the underlying BLAS being thread-safe; ReLAPACK adds no threading of its own beyond what the BLAS does |
| **Drop-in for the baseline** | partial — same Fortran LAPACK symbols and signatures for the covered routines when linked before LAPACK, but only 10 routine families (40+ routines) are covered, LP64 int only upstream, and MKL needs COMPLEX_FUNCTIONS_AS_ROUTINES=1 or ctrsyl/ztrsyl break |

## Gotchas

- Complex-return calling convention: default is the gfortran struct-return style; with MKL set COMPLEX_FUNCTIONS_AS_ROUTINES=1 in config.h, otherwise ctrsyl/ztrsyl segfault or return errors of order 1 (config.md).
- Hidden allocations: xsygst and xsytrf malloc n^2/2-sized buffers by default (ALLOW_MALLOC), and xpbtrf/xgbtrf call malloc unconditionally without a NULL check; OpenBLAS disabled the xsytrf reallocation in 2019 after memory problems in the LAPACK tests (commit 2cd463e).
- Upstream lacks fixes that OpenBLAS's relapack/ copy carries: workspace sign errors and zero-size early returns in xgbtrf/xpbtrf (de63675, 2020), xGEMMT argument lists (2022, 2024) and the sytrf/hetrf workspace size (2026). Prefer OpenBLAS's copy if you can.
- Upstream xgetrf passes the shared info pointer to the second recursive half, whose dgetf2 leaf resets it, so a zero pivot found in the left half may not be reported (read from src/dgetrf.c, not tested); OpenBLAS's copy returns early when info is set. A guide written for OpenBLAS builders also advises against BUILD_RELAPACK=1 because 'make lapack-test' shows too many errors.

## Known shortcomings

- No numbers on any reachable page; TOMS paper blocked here, so tier D for now (likely B with the paper); notable because OpenBLAS vendors relapack/.
- Security/correctness bug: upstream xsytrf/xhetrf workspace query and malloc size n\*(n/2) while the recursion can write n\*REC_SPLIT(n), corrupting the heap; fixed only in OpenBLAS's copy (commit 4a4cd8f, 2026-08-08), upstream src/dsytrf.c unchanged; 32-bit int only (no ILP64); gbtrf/pbtrf workspace fixes also only in OpenBLAS (de63675). Use OpenBLAS's maintained relapack/ (BUILD_RELAPACK=1) instead of upstream.

## Caveats and trade-offs

No numbers anywhere in the repo. The measurements are in Peise and Bientinesi, 'Recursive Algorithms for Dense Linear Algebra: The ReLAPACK Collection' (arXiv:1602.06763; web-search results give ACM TOMS 44(2), 16:1-16:19, 2017, as Algorithm 979), which this run could not open (arxiv.org, ar5iv, Semantic Scholar and the HPAC site are blocked); its abstract, seen in search snippets, says only that ReLAPACK 'clearly outperforms reference LAPACK, and even improves upon the performance of optimized libraries' in many scenarios. A check with access to the paper should raise the tier to B. Last commit is a 2022 typo fix; the code dates from 2016-2017 and was compared with OpenBLAS and MKL versions of that era. Linking with MKL requires COMPLEX_FUNCTIONS_AS_ROUTINES=1.

Drop-in LAPACK interface (links in front of LAPACK, replaces only the covered routines); needs a BLAS plus LAPACK unblocked kernels underneath; covers only routines where recursion helps (see coverage.md); C code with Fortran-style interfaces.

## Maintenance

Upstream abandoned (code from 2016-2017, last commit a 2022 typo fix) but MIT-licensed and small; the maintained copy with ILP64 support and bug fixes lives in OpenBLAS's relapack/ directory (optional BUILD_RELAPACK=1).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now D.
- **Tier reason:** The README (and config.md, coverage.md, test/README.md, examples/README.md) state that ReLAPACK outperforms reference LAPACK and improves on OpenBLAS and MKL but give no numbers; the peer-reviewed paper that holds the measurements (arXiv:1602.06763, ACM TOMS Algorithm 979) could not be opened, so only a qualitative claim was seen.
- **Verifier notes:** Downgraded C to D because no numbers were visible on any reachable page; do not reject: it is notable (OpenBLAS ships a copy under relapack/, peer-reviewed TOMS algorithm). Recommend an Opus retier check against the arXiv paper, which likely yields B. Metadata verified: MIT, 44 stars, last commit 2022-02-20, abandoned.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/HPAC/ReLAPACK>
  - <https://github.com/HPAC/ReLAPACK/commits/master>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/README.md>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/test/README.md>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/examples/README.md>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/config.md>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/coverage.md>
  - <https://github.com/OpenMathLib/OpenBLAS/tree/develop/relapack>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/README.md>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/config.md>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/coverage.md>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/test/README.md>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/examples/README.md>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/config.h>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/make.inc>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/Makefile>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/src/relapack.h>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/src/dgetrf.c>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/src/dpotrf.c>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/src/dsytrf.c>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/src/dsygst.c>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/src/dpbtrf.c>
  - <https://raw.githubusercontent.com/HPAC/ReLAPACK/HEAD/src/dgbtrf.c>
  - <https://github.com/HPAC/ReLAPACK/issues>
  - <https://github.com/HPAC/ReLAPACK/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/HPAC/ReLAPACK/issues/4>
  - <https://github.com/HPAC/ReLAPACK/issues/5>
  - <https://github.com/OpenMathLib/OpenBLAS/tree/develop/relapack>
  - <https://github.com/OpenMathLib/OpenBLAS/commits/develop/relapack>
  - <https://github.com/OpenMathLib/OpenBLAS/commit/de63675>
  - <https://github.com/OpenMathLib/OpenBLAS/commit/4a4cd8f>
  - <https://github.com/OpenMathLib/OpenBLAS/commit/2cd463e>
  - <https://raw.githubusercontent.com/OpenMathLib/OpenBLAS/develop/Makefile.rule>
  - <https://raw.githubusercontent.com/OpenMathLib/OpenBLAS/develop/relapack/relapack_config.h>
  - <https://raw.githubusercontent.com/OpenMathLib/OpenBLAS/develop/relapack/src/dgetrf.c>
  - <https://github.com/OpenMathLib/OpenBLAS/issues/788>
  - <https://github.com/bgeneto/build-install-compile-openblas>
  - https://arxiv.org/abs/1602.06763 (EGRESS_BLOCKED)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/hpac/relapack`) · [data/wave8/enrich/raw/github_com_hpac_relapack.json](../../../data/wave8/enrich/raw/github_com_hpac_relapack.json) (enrichment confidence 0.75)

</details>
