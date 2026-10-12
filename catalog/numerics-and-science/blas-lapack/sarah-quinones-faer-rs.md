# faer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust dense (and sparse) linear algebra whose multithreaded QR and mid-size eigensolvers outrun OpenBLAS and Eigen; MKL still leads.

| | |
|---|---|
| **Beats** | OpenBLAS, LAPACK and Eigen (paper text); Intel MKL not claimed as beaten |
| **Claimed result** | JOSS paper text: 'State of the art algorithms are used for each decomposition, allowing performance that matches or even surpasses other low level libraries such as OpenBLAS, LAPACK, and Eigen.' Approximate readings from the paper's linked PDF plots (derived from page data; i5-11400, 12 threads, f64, n^3/s): QR at n=10^4 is about 1.48e11 for faer vs about 0.5e11 for OpenBLAS (\~3x) and about 0.29e11 for Eigen, but below MKL (\~1.57e11). Matmul is on par with OpenBLAS, MKL and BLIS at large n (\~1.3e11) and ahead of OpenBLAS at some mid sizes (\~100-300). Eigendecomposition is ahead of OpenBLAS around n=1000 (\~2.2e9 vs \~1.2e9) but behind OpenBLAS, BLIS and MKL at n=10^4 (\~2.9e9 vs \~3.7e9, \~4.0e9 and \~4.6e9). The f128 plots compare only against Eigen; there faer is several times faster at large n (about 3x on matmul, about 10x on QR). |
| **Workload** | Dense matrix multiplication, QR and eigenvalue decomposition, plotted as n^3 over run time versus matrix size, with Eigen compiled with -fopenmp. |
| **Metric** | throughput |
| **Hardware** | 11th Gen Intel Core i5-11400 @ 2.60GHz, 12 threads |
| **Compiler and flags** | Not stated beyond 'Eigen is compiled with the -fopenmp flag'. The paper gives no Rust toolchain, faer version, optimization flags or BLAS/MKL versions. |
| **Adoption** | 2.6k stars (GitHub mirror; project moved to codeberg.org/sarah-quinones/faer) |
| **Last commit** | 2026-09-04 |
| **Links** | [repository](https://github.com/sarah-quinones/faer-rs) · [benchmark](https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/paper.md) |

## Verdict

The JOSS 2023 paper (peer-reviewed software paper, DOI 10.21105/joss.06099) plots n^3/time for f64 matmul, QR and EVD on an Intel Core i5-11400 with 12 threads against OpenBLAS, BLIS, MKL and Eigen (built with -fopenmp); readings show about 3x OpenBLAS on QR at n=10^4, parity on large matmul, and a mid-size EVD win, while MKL stays ahead. No Rust toolchain, flags, library versions or benchmark code are given, and the plots date from November 2023, before the current 0.24 code.

## Use it when

- Rust code that needs dense factorizations (QR, LU, Cholesky, SVD, EVD) on medium-to-large matrices without linking a C/Fortran BLAS/LAPACK.
- Multithreaded QR of large f64 matrices: the JOSS plots (i5-11400, 12 threads) put faer about 3x OpenBLAS and about 5x Eigen at n=10^4.
- Eigendecomposition around n=1000, where the plots show faer ahead of OpenBLAS (about 2.2e9 vs 1.2e9 n^3/s).
- Extended precision: faer ships a SIMD double-double type (fx128/cx128) and the plots show it several times faster than Eigen on f128 matmul and QR.
- Projects that want one portable static binary (x86-64 and AArch64 NEON SIMD, no_std-capable core) instead of distributing OpenBLAS or MKL.

## Skip it when

- When Intel MKL is available on Intel hardware and only speed matters: the paper's plots show MKL ahead on QR and EVD and level on matmul.
- Large eigendecompositions (n=10^4): the plots show faer behind OpenBLAS, BLIS and MKL (about 2.9e9 vs 3.7e9, 4.0e9 and 4.6e9 n^3/s).
- Small fixed-size matrices (graphics, robotics, 3x3/4x4): the crate docs say its design is not well suited to that and point to nalgebra or cgmath.
- Existing C/C++ or Fortran code that calls BLAS/LAPACK symbols: there is no drop-in ABI, and the C/C++ binding (faer-ffi) is not published on crates.io.
- Ill-conditioned or singular inputs without your own checks: open bug reports show NaN from qr().solve_lstsq on a 1e16-conditioned 3x3 system (#265) and NaN instead of 0 from a singular 3x3 determinant on 0.23.2 (#260).

## How it is fast

Matrix multiplication follows the BLIS approach (packing plus register-blocked micro-kernels), with runtime CPU-feature dispatch to precompiled SIMD variants through the pulp crate, the gemm crate, nano-gemm for small products and, on x86-64 with std, the author's private-gemm-x86 backend (0.22 changelog: 'accelerated matrix multiply backend on x86_64'). Decompositions are blocked so most flops land in that GEMM; memory-bound phases (column-pivoted QR, full-pivot LU, reduction to bidiagonal/tridiagonal/Hessenberg form) use fused kernels that do A x and A^T y in one pass over A. Threading is Rayon (plus the spindle crate); SIMD for user scalar types deinterleaves AoS data to SoA in registers.

## Compared with alternatives

Pick faer over Eigen when you are in Rust or need fast multithreaded large QR or mid-size eigensolvers (Eigen trails both faer and OpenBLAS in the paper's QR plot), and over OxiBLAS when you need full LAPACK-style decompositions rather than BLAS kernels; for matrices in the tens BLASFEO is the better fit.

## Integration

| | |
|---|---|
| **Form** | crate (faer on crates.io); optional cdylib with C and C++ headers built from faer-ffi in the repo |
| **Dependencies** | pure Rust crates: pulp, gemm, nano-gemm, private-gemm-x86 (x86-64, std), dyn-stack, bytemuck, generativity, reborrow, equator, num-complex, num-traits, libm; optional rayon + spindle (default on), rand, npyz |
| **Minimum toolchain** | Rust 1.84.0 (MSRV); nightly needed only for the AVX-512 'nightly' feature; faer.hpp needs C++17 |
| **Platforms** | any Rust target; explicit SIMD on x86-64 (AVX2/FMA, AVX-512 with nightly) and AArch64 NEON; no SVE/SME/RVV kernels yet; an open issue (#255) reports matmul compile failure on i686-unknown-linux-gnu |
| **Thread safety** | Rust ownership rules apply (MatRef is shareable, MatMut is exclusive); parallelism is a global setting (set_global_par/get_global_par) or a per-call Par argument in the low-level API |
| **Drop-in for the baseline** | partial — replaces LAPACK/OpenBLAS functionality for Rust callers through a different API; the C/C++ binding has its own function names (libfaer_v0_24_\*), not BLAS/LAPACK symbols |

## Gotchas

- Development moved to codeberg.org/sarah-quinones/faer; the GitHub repo is a mirror, so file issues and track releases there (crate repository field points to Codeberg).
- Pre-1.0 with frequent breaking changes: 0.20-0.21 was a full project refactor, 0.24 removed serde support, and the docs warn that eigenvalue order from Mat::eigen is unspecified and may change.
- The checked-in faer-ffi/faer.h declares libfaer_v0_23_\* functions while faer.hpp calls libfaer_v0_24_\*; build.rs only regenerates the header when FAER_FFI is set, so build it yourself rather than copying the header.
- The MIT crate carries ported code under other licences (COPYING.EIGEN.MPL2, COPYING.LAPACK.BSD and two SuiteSparse BSD notices in faer/), so keep those notices when vendoring.

## Known shortcomings

- Plots from 2023 (QR \~3x OpenBLAS, matmul level, large EVD loses to OpenBLAS/BLIS/MKL); tier B rests on JOSS acceptance (review #6099); Rust.
- Open correctness bugs: NaN from qr().solve_lstsq on an ill-conditioned 3x3 (#265), NaN determinant for a singular 3x3 on 0.23.2 (#260), full_piv_lu solve (#238), hang in partial_self_adjoint_eigen (#262). Checked-in faer-ffi/faer.h declares libfaer_v0_23_\* while faer.hpp calls v0_24_\*; faer-ffi is not on crates.io. Crate bundles MPL-2.0 Eigen-derived code (COPYING.EIGEN.MPL2). JOSS plots predate 0.24.

## Caveats and trade-offs

The paper's numbers exist only as plots: PDFs attached to the GitHub repo in 2023, while the reviewed release was faer v0.24.4, so the plots predate current code. The readings above are approximate. faer is slower than MKL on QR and eigendecomposition and level with it on matmul, and it loses to OpenBLAS and BLIS on large eigendecompositions. The paper links no benchmark code and gives no Rust toolchain, flags or library versions. JOSS reviews software rather than benchmark methodology, and the benchmarks are first-party. The project's benchmark page (faer.veganb.tw/benchmarks/) and joss.theoj.org were unreachable from this container. The GitHub repository is a mirror; development moved to codeberg.org/sarah-quinones/faer. The library is Rust; a C API is only planned.

Pure Rust dense linear algebra (matmul, Cholesky, LU, QR, SVD, EVD) with its own API, not a drop-in BLAS/LAPACK ABI; a faer-ffi directory exists in the repo for C bindings. Explicit SIMD on x86-64 and AArch64 NEON. Uses Rayon for threading.

## Maintenance

Actively developed (crate 0.24.4 released 2026-06-24, about 4.8M crates.io downloads, last mirror commit 2026-09-04), MIT-licensed and used widely in the Rust ecosystem, but still pre-1.0 with open correctness bugs on ill-conditioned inputs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The JOSS paper is peer-reviewed: review issue openjournals/joss-reviews#6099 is labelled accepted/published, and a search result gives DOI 10.21105/joss.06099. Its plots show faer beating OpenBLAS on QR and mid-size eigendecomposition. No benchmark code, Rust version or flags are given, so it cannot be A.
- **Verifier notes:** The quote is verbatim in paper.md. I rendered the three linked PDF plots (matmul, QR, EVD) and read them: the win over OpenBLAS is real for QR and mid-size EVD, faer is level on matmul and loses to MKL. I removed the record's unopened 'author concedes' statement from caveats. The page confirms MIT, 2.6k stars and the last commit on 2026-09-04.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/sarah-quinones/faer-rs>
  - <https://github.com/sarah-quinones/faer-rs/commits/main>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/paper.md>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/LICENSE>
  - <https://github.com/sarah-quinones/faer-rs/files/13344473/matmul.pdf>
  - <https://github.com/sarah-quinones/faer-rs/files/13344474/qr.pdf>
  - <https://github.com/sarah-quinones/faer-rs/files/13344472/evd.pdf>
  - <https://github.com/openjournals/joss-reviews/issues/6099>
- **Sources the enricher read:**
  - <https://github.com/sarah-quinones/faer-rs>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/paper.md>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/faer/Cargo.toml>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/faer/src/lib.rs>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/faer-ffi/Cargo.toml>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/faer-ffi/build.rs>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/faer-ffi/faer.h>
  - <https://raw.githubusercontent.com/sarah-quinones/faer-rs/HEAD/faer-ffi/faer.hpp>
  - <https://github.com/sarah-quinones/faer-rs/tree/main/faer>
  - <https://github.com/sarah-quinones/faer-rs/tree/main/faer-ffi>
  - <https://github.com/sarah-quinones/faer-rs/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/sarah-quinones/faer-rs/issues/265>
  - <https://github.com/sarah-quinones/faer-rs/issues/260>
  - <https://crates.io/api/v1/crates/faer>
  - <https://crates.io/api/v1/crates/private-gemm-x86>
  - <https://crates.io/api/v1/crates/faer-ffi>
  - <https://raw.githubusercontent.com/aleon1138/linalg-bench/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sarah-quinones/faer-rs`) · [data/wave8/enrich/raw/github_com_sarah_quinones_faer_rs.json](../../../data/wave8/enrich/raw/github_com_sarah_quinones_faer_rs.json) (enrichment confidence 0.75)

</details>
