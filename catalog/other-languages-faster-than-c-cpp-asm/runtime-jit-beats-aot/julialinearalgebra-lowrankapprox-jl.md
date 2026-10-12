# LowRankApprox.jl (Julia randomized interpolative decomposition) vs SciPy/Fortran ID

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🟡 stale

> Julia package of randomized, early-terminating low-rank factorizations (ID, pivoted QR, SVD, CUR); README times an ID about 3.5x faster than SciPy's Fortran ID.

| | |
|---|---|
| **Beats** | SciPy interpolative decomposition (scipy.linalg.interpolative via PyMatrixID), which at the README's time wrapped the Fortran77 ID library; SciPy 1.15.0 ported that code to Cython. The README also names MATLAB. Neither is a C or C++ -O3 baseline. |
| **Claimed result** | README: \~0.02 s with LowRankApprox in Julia vs \~0.07 s with SciPy (Fortran backend) and \~0.3 s in MATLAB, i.e. about 3.5x faster than SciPy (derived from page data); the README also says 'large speedups over similar codes written in MATLAB and Python (and even some in Fortran and C)'. |
| **Workload** | Interpolative decomposition (ID) of a 1024 x 1024 Hilbert matrix to relative precision about 1e-15. |
| **Metric** | latency |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: 'in part both algorithmic improvements as well as ... low-level optimizations' (the package uses an early-terminating pivoted-QR based ID rather than the Fortran library's algorithm). |
| **Adoption** | 129 stars; Julia General registry package |
| **Last commit** | 2024-02-10 |
| **Links** | [repository](https://github.com/JuliaLinearAlgebra/LowRankApprox.jl) · [benchmark](https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/README.md) |

## Verdict

The README reports an interpolative decomposition of a 1024 x 1024 Hilbert matrix to relative precision about 1e-15 in \~0.02 s with LowRankApprox (Julia), \~0.07 s with SciPy calling the Fortran 77 id_dist library, and \~0.3 s in MATLAB (about 3.5x vs SciPy, derived from page data). No hardware, versions, flags or benchmark code are given, SciPy's interp_decomp defaults to its randomized path (rand=True) but the README does not say which was used, and no C or C++ baseline was measured.

## Use it when

- Dense matrices with rapidly decaying spectra (kernel, Cauchy, Hilbert-like or integral-equation blocks in hierarchical or fast multipole solvers) where you want an approximation to a stated relative tolerance rather than a fixed rank.
- Matrix-free operators: wrap a product or composition as a LinearOperator and factor it from matvecs only, without forming the matrix.
- When you need actual skeleton columns or rows (ID or CUR) for compression or interpretability instead of an abstract basis.
- Julia codebases that already link OpenBLAS or MKL and want partial SVD/eigen or range finding with tunable sketches (randn, srft, sub, sprn).

## Skip it when

- Matrices that are not numerically low-rank: the adaptive sketch keeps doubling its order and the total cost exceeds a plain dense QR or SVD.
- Small matrices: issue #25 shows psvd on a 49x80 matrix taking about 998 us and 504 KiB vs about 746 us and 125 KiB for LinearAlgebra's svd.
- When results must be deterministic or carry a guaranteed error bound: sketches use the global RNG (the README notes the Hilbert rank comes out 26 or 27 between runs), and atol/rtol are checked only against QR pivot magnitudes, so accuracy is approximate by the README's own description.
- C or C++ projects: this is Julia-only; LAPACK 3.12's xGEQP3RK now offers the same tolerance-terminated pivoted QR directly (issue #60 proposes adopting it), and SciPy 1.15+ ships a Cython port of the ID code.
- Projects that need an actively maintained dependency: last commit 2024-02-10 and nine open issues, including an unanswered Julia 1.12 warning.

## How it is fast

By default it sketches the matrix with a Gaussian random matrix of order k+8 (starting at the block size 32 and doubling until the rank is found), which is one Level-3 BLAS GEMM, then runs an early-terminating blocked pivoted QR built on LAPACK's xLAQPS panel kernel (called via ccall) that stops once a pivot falls below max(atol, rtol times the largest column norm); the ID follows from that partial QR. The SciPy baseline at the README's time wrapped the id_dist Fortran 77 library, whose iddp_aid makes a separate rank-estimation pass and uses its own Householder pivoted QR and per-column subsampled randomized Fourier transform, with no BLAS or LAPACK calls (checked in SciPy v1.14.1 sources). So the gap is algorithm plus optimized BLAS/LAPACK, not Julia code generation.

## Compared with alternatives

No sibling does randomized low-rank or interpolative decomposition; pick it for that job in Julia. Unlike NativeMinuit.jl or NonuniformFFTs.jl, which beat C++ implementations of comparable algorithms with Julia code, this entry's edge is a different algorithm plus LAPACK against a Python/Fortran baseline, so it is not evidence that a JIT beats AOT C++.

## Integration

| | |
|---|---|
| **Form** | module (Julia package in the General registry, v0.5.5) |
| **Dependencies** | FFTW, LowRankMatrices, Nullables, and the LinearAlgebra, SparseArrays and Random standard libraries; LAPACK via LinearAlgebra.BLAS.liblapack (OpenBLAS by default) |
| **Minimum toolchain** | Julia 1.0 per Project.toml compat (CI runs 1.0 and the latest 1.x) |
| **Platforms** | any platform Julia's BLAS/LAPACK supports; CI covers x64 Linux, macOS and Windows |
| **Thread safety** | not documented (sketches draw from Julia's default RNG; factorization objects are mutable structs) |
| **Drop-in for the baseline** | no |

## Gotchas

- No benchmark harness exists: the README's \~0.02 s vs \~0.07 s vs \~0.3 s are approximate 'early tests' from around 2015 with no hardware, Julia, BLAS, SciPy or MATLAB versions, no thread counts and no statement of whether Julia's first-call compilation was excluded. The baseline is the same author's own Python wrapper (scipy.linalg.interpolative is copyright 2013 Kenneth L. Ho; LowRankApprox.jl copyright 2015 Ken Ho) over BLAS-free Fortran 77, while Julia's sketch runs in the linked BLAS GEMM with an unstated thread count, so part of the 3.5x may come from BLAS (and possibly multithreading) rather than the algorithm.
- First call in a session pays Julia's JIT compilation for the whole idfact/sketch/LAPACK-wrapper chain, which is not part of the README figure.
- Calls LAPACK's auxiliary routine xLAQPS directly, so it depends on the linked LAPACK exporting it; issue #35 reported an access violation after pqr with MKL on Julia 1.5.4 (fine with OpenBLAS on 1.6), closed as not planned.
- Julia 1.12 prints 'Constructor for type "Array" was extended in LowRankApprox without explicit qualification or import' (issue #62, open, no reply).

## Known shortcomings

- Off-baseline: compared with SciPy's Fortran77 ID code (Cython since SciPy 1.15.0) and MATLAB, no C/C++ baseline; README figures are approximate; the core work is LAPACK xLAQPS and BLAS through ccall into OpenBLAS, so the win is library and algorithm, not Julia; last commit 2024-02-10.
- No benchmark harness exists. The SciPy baseline (scipy.linalg.interpolative) is the same author's own 2013 wrapper over BLAS-free Fortran 77 id_dist (checked against SciPy v1.14.1 sources), while the Julia side uses a BLAS GEMM sketch plus LAPACK xLAQPS, so the gain is algorithm plus BLAS, not JIT. Thread count, versions and whether compile time was excluded are all unstated. LAPACK 3.12's xGEQP3RK now gives the same truncated QRCP directly (issue #60); the Julia 1.12 warning (#62) is open without reply.

## Caveats and trade-offs

Single approximate figure per language ('early tests', package origin 2015) with no hardware, Julia, SciPy, BLAS or compiler versions and no benchmark script; it is not stated whether SciPy ran its deterministic or randomized ID routine. The baseline is a Python wrapper over Fortran77 (since SciPy 1.15.0 a Cython port), not C or C++ at -O3, so the README figure no longer describes current SciPy. The README attributes the gap partly to a different algorithm, and the package's core work is LAPACK xLAQPS plus BLAS calls through ccall, so any win is algorithm plus OpenBLAS/LAPACK rather than Julia codegen. The 'even some in Fortran and C' claim has no numbers. Last commit 2024-02-10 (stale). [retier] No benchmark harness exists; the SciPy baseline (scipy.linalg.interpolative) is the same author's 2013 wrapper over BLAS-free Fortran 77 id_dist, while the Julia side uses a BLAS GEMM sketch plus LAPACK xLAQPS, so the gain is algorithm plus BLAS, not JIT. Thread count, versions and compile-time exclusion unstated. LAPACK 3.12's xGEQP3RK now gives the same truncated QRCP directly (issue #60); the Julia 1.12 warning (#62) is open.

Randomized, early-terminating approximation; works on BLAS/LAPACK-compatible matrices and matrix-free operators.

## Maintenance

Stale since February 2024 (v0.5.5, nine open issues without maintainer replies) but MIT-licensed, about 4,000 lines of Julia, and still installable from the General registry; usable only from Julia.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives three approximate first-party timings (\~0.02 s Julia, \~0.07 s SciPy, \~0.3 s MATLAB) for an ID of a 1024x1024 Hilbert matrix with no benchmark script, hardware, library versions or flags, so it is first-party numbers without methodology (C). The baseline is off-target for this wave (Python over Fortran77, now Cython; MATLAB), not C or C++ at -O3.
- **Verifier notes:** Numbers match the README exactly (3.5x vs SciPy derived from page data). Not a language-level win: the ID's heavy lifting is LAPACK xLAQPS and BLAS via ccall into OpenBLAS, the baseline is Fortran77-through-Python (Cython since SciPy 1.15.0), and no C or C++ baseline exists; record as off-baseline, library- and algorithm-driven. Metadata checked: MIT (Expat) LICENSE.md, 129 stars, last commit 2024-02-10, not a fork.
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Shortcomings recorded by:** verifier batch-75 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/README.md>
  - <https://github.com/JuliaLinearAlgebra/LowRankApprox.jl>
  - <https://github.com/JuliaLinearAlgebra/LowRankApprox.jl/commits>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/LICENSE.md>
  - <https://github.com/JuliaLinearAlgebra/LowRankApprox.jl/tree/master/src>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/lapack.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/pqr.jl>
  - <https://raw.githubusercontent.com/scipy/scipy/main/doc/source/release/1.15.0-notes.rst>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/README.md>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/Project.toml>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/LICENSE.md>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/LowRankApprox.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/lapack.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/pqr.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/id.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/sketch.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/matrixlib.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/psvd.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/cur.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/snorm.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/linop.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/permute.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/trapezoidal.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/prange.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/src/util.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/test/runtests.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/LowRankApprox.jl/master/test/id.jl>
  - <https://github.com/JuliaLinearAlgebra/LowRankApprox.jl/commits/master>
  - <https://github.com/JuliaLinearAlgebra/LowRankApprox.jl/issues?q=is%3Aissue>
  - <https://github.com/JuliaLinearAlgebra/LowRankApprox.jl/issues/25>
  - <https://github.com/JuliaLinearAlgebra/LowRankApprox.jl/issues/32>
  - <https://github.com/JuliaLinearAlgebra/LowRankApprox.jl/issues/35>
  - <https://github.com/JuliaLinearAlgebra/LowRankApprox.jl/issues/60>
  - <https://github.com/JuliaLinearAlgebra/LowRankApprox.jl/issues/62>
  - <https://raw.githubusercontent.com/JuliaRegistries/General/master/L/LowRankApprox/Versions.toml>
  - <https://raw.githubusercontent.com/JuliaRegistries/General/master/L/LowRankApprox/Compat.toml>
  - <https://raw.githubusercontent.com/scipy/scipy/main/scipy/linalg/interpolative.py>
  - <https://raw.githubusercontent.com/scipy/scipy/v1.14.1/scipy/linalg/src/id_dist/src/iddp_aid.f>
  - <https://raw.githubusercontent.com/scipy/scipy/v1.14.1/scipy/linalg/src/id_dist/src/idd_qrpiv.f>
  - <https://raw.githubusercontent.com/scipy/scipy/v1.14.1/scipy/linalg/src/id_dist/src/idd_frm.f>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/julialinearalgebra/lowrankapprox.jl`) · [data/wave14/enrich/raw/github_com_julialinearalgebra_lowrankapprox_jl.json](../../../data/wave14/enrich/raw/github_com_julialinearalgebra_lowrankapprox_jl.json) (enrichment confidence 0.75)

</details>
