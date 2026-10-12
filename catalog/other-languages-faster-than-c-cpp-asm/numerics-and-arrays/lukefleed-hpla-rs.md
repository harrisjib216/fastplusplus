# hpla-rs (Rust faer-based CSR SpMV and Lanczos exp(-A)b) against Eigen, PETSc, oneMKL and PSBLAS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `MIT declared in the Cargo.toml license field only; the repo has no LICENSE file` · 🟢 active

> Benchmark repo: Rust faer CSR SpMV and Lanczos exp(-A)b beat Eigen on one core but lose to oneMKL and PETSc.

| | |
|---|---|
| **Beats** | Eigen CSR and CSC sparse matrix-vector product (C++); also PETSc CSR (C), Intel oneMKL inspector-executor CSR and CSC (C) and PSBLAS (C++/Fortran), single core |
| **Claimed result** | The README states no speedup. Ratios below are geomeans of per-matrix time ratios from python/data/summary.csv (derived from page data). SpMV, Rust faer/csr against: Eigen CSR 1.12x faster (wins 19 of 28 matrices, per-matrix range 0.85-1.66), Eigen CSC 1.20x faster, PSBLAS CSR 1.02x (parity; faer wins only 13 of 28). oneMKL CSR is 1.24x faster than faer/csr (faer wins 4 of 28), and PETSc CSR is 1.23x faster (faer wins 5 of 28). One-pass Lanczos, faer_csr: 1.04x faster than Eigen CSR (8 of 15) and 1.21x faster than PSBLAS CSR; PETSc is 1.19x faster (faer wins 2 of 15). Two-pass Lanczos, faer_csr: 1.04x faster than Eigen CSR (10 of 15); PETSc is 1.22x faster. |
| **Workload** | Single-core y += A\*x on 28 SuiteSparse matrices, plus one-pass and two-pass Lanczos evaluation of exp(-A)b on 15 symmetric matrices, Criterion with 50 samples. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6418H (Sapphire Rapids), one pinned core, 2 TiB RAM, Ubuntu 24.04.4, Linux 6.8. |
| **Compiler and flags** | Rust nightly-2026-04-14: opt-level=3, lto=fat, codegen-units=1, panic=abort, RUSTFLAGS=-C target-cpu=native. C/C++ wrappers: clang/clang++ from LLVM 22 with -O3 -march=native -mtune=native -flto (build.rs; no -DNDEBUG, and cc-rs never adds it). PSBLAS Fortran wrappers: gfortran 14.3.0 -O3 -march=native -mtune=native -ffat-lto-objects. PETSc and PSBLAS libraries are built by Spack with -g -O3 -march=native -mtune=native -flto (spack.yaml); PETSc is linked against oneMKL. OMP_NUM_THREADS=1, taskset -c 0, MKL linked as mkl_sequential. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | README says the Rust side uses a CSR SpMV specialization in a faer fork; no mechanism analysis was reachable (paper not opened). |
| **Adoption** | 4 stars; companion repo of an arXiv paper |
| **Last commit** | 2026-06-18 |
| **Links** | [repository](https://github.com/lukefleed/hpla-rs) · [benchmark](https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/python/data/summary.csv) |

## Verdict

On one taskset-pinned core of a Xeon Gold 6418H (Criterion, 50 samples, 100 s window), faer/csr built with rustc nightly-2026-04-14 (fat LTO, target-cpu=native) was compared against wrappers built with clang 22 -O3 -march=native -flto and Spack-built PETSc, oneMKL (sequential) and PSBLAS. Geomean SpMV over 28 SuiteSparse matrices: 1.12x faster than Eigen CSR and 1.20x faster than Eigen CSC, parity with PSBLAS CSR (1.02x), but 0.81x of oneMKL CSR and 0.82x of PETSc CSR. Lanczos exp(-A)b: 1.04x Eigen and 0.84x PETSc one-pass, 1.04x Eigen and 0.82x PETSc two-pass. All re-derived here from python/data/summary.csv.

## Use it when

- You need reference numbers for single-core Rust sparse kernels against C, C++ and Fortran libraries on standard SuiteSparse matrices, with code, flags and CPU stated.
- You already use faer in Rust and need CSR SpMV: the fork's faer/csr is 1.11x faster than faer/csc (geomean, 21 of 28 matrices) and 1.12x faster than Eigen CSR (19 of 28), derived from summary.csv.
- Memory-bound Krylov matrix-function evaluation (exp(-A)b) where the basis does not fit: the two-pass Lanczos keeps O(n) storage at twice the SpMV count, and the Rust version is 1.04x Eigen and 1.11x PSBLAS here.
- You want a template for fair cross-language benchmarking: build.rs checks that clang's LLVM major matches rustc's for cross-language LTO, setup stays outside the timed loop, and Criterion runs 50 samples over 100 s.

## Skip it when

- Fastest single-core CSR SpMV on x86: oneMKL inspector-executor is 1.24x faster (faer wins 4 of 28) and PETSc MatMultAdd 1.23x faster (5 of 28); per-matrix PETSc ratios run from 0.54x to 1.47x.
- Lanczos where PETSc is an option: PETSc is 1.19x faster one-pass (faer wins 2 of 15) and 1.22x faster two-pass (4 of 15).
- Multi-threaded or distributed SpMV: everything is Par::Seq on one taskset-pinned core, and there are no parallel results.
- You need a dependency you can ship: there is no LICENSE file (only license = "MIT" in Cargo.toml), the kernel lives in an unreleased git fork pinned to commit 009ac1eb, and nightly Rust is required.
- Machines without Spack: build.rs hard-requires spack-located LLVM 22, GCC 14.3.0, oneMKL, PETSc, Eigen, PSBLAS and OpenMPI, even for cargo check.

## How it is fast

The Rust SpMV is faer's sparse_dense_matmul with Accum::Add and Par::Seq. According to src/lib.rs, faer 0.24 reinterprets a CSR matrix as a transposed CSC matrix and dispatches to dense_sparse_csc_matmul, giving one dot product per row; the fork specialises that CSR path, but its code and the paper's analysis could not be read here (Codeberg and arXiv blocked). It is built with fat LTO, codegen-units=1 and target-cpu=native (AVX-512 on Sapphire Rapids). The Eigen 3.4.0 row-major kernel it beats is a single-accumulator scalar loop (Eigen 5.0 uses two accumulators), and the Eigen SpMV wrapper also pays for a temporary vector (see gotchas). In Lanczos, the Rust recurrence fuses w -= beta\*v_prev with the alpha dot product into one pass over the vectors and reuses preallocated workspaces.

## Compared with alternatives

No sibling in this category covers sparse SpMV or Krylov methods (TriangularSolve.jl and Gaius.jl are dense, Clarabel.rs is a conic solver). Use upstream faer (catalogued separately as sarah-quinones/faer-rs) as the dependency, and this repo to reproduce or extend the Rust-versus-C/C++ sparse comparison.

## Integration

| | |
|---|---|
| **Form** | source-drop (benchmark repo); the Rust kernel comes in as a git dependency on a faer fork |
| **Dependencies** | faer fork (git codeberg.org/lukefleed/faer, commit 009ac1eb, features std and nightly), matrix-market-rs, criterion; baselines via Spack: intel-oneapi-mkl, PETSc (linked to MKL), Eigen, PSBLAS develop, OpenMPI, OpenBLAS, LLVM 22, GCC 14.3.0 |
| **Minimum toolchain** | Rust nightly-2026-04-14 (edition 2024, faer nightly feature); clang from LLVM 22 to match rustc's LLVM for cross-language LTO; gfortran 14.3.0 |
| **Platforms** | x86-64 Linux as tested (Sapphire Rapids, Spack target sapphirerapids, -march=native); others not documented |
| **Thread safety** | single-threaded by design (Par::Seq, OMP_NUM_THREADS=1, mkl_sequential); otherwise not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Eigen SpMV baseline flaw: ffi/spmv/eigen.cpp runs '\*(ctx-&gt;y) += A \* x' without .noalias(). In both Eigen 3.4.0 and 5.0.0, evaluator_assume_aliasing&lt;Product&lt;Lhs, Rhs, DefaultProduct&gt;&gt; is true and call_assignment builds a plain temporary ('tmp(src)') before adding it. So each Eigen call allocates, fills and re-reads an nrows-long vector that the faer, PETSc MatMultAdd and MKL paths do not pay. The Eigen Lanczos wrappers do use .noalias(), and the Eigen gap shrinks there from 1.12x to 1.04x; the cost was confirmed in source, not measured. The missing -DNDEBUG matters less, because Eigen's sparse inner loop calls coeff(), which has only an internal assert.
- The Lanczos rows compare implementations as well as languages: the Rust recurrence (src/lanczos/algorithms/mod.rs) fuses w -= beta\*v_prev with the alpha dot product, while the Eigen wrapper makes separate passes. On the MKL side, mkl_sparse_set_mv_hint is commented out in ffi/spmv/mkl.c, so MKL optimises without a call-count hint and still wins.
- Baseline library versions are not recorded: spack.yaml leaves eigen, petsc and intel-oneapi-mkl unpinned, psblas@develop tracks a branch, and no spack.lock is committed. Which Eigen ran (3.4.x with a one-accumulator loop, or 5.0.x with two) is unknown. The eigen.cpp header comment says -ffast-math, but build.rs has that flag commented out on every wrapper.
- The CSR specialisation behind the faer/csr rows is in the Codeberg fork, not in this repo or upstream faer, and could not be inspected here; x is all ones and y accumulates across iterations by design (bench comment: values do not affect a memory-bound kernel).

## Known shortcomings

- Mixed result: loses to oneMKL and PETSc, parity with PSBLAS (13 of 28 cases); the Eigen wrappers are built without -DNDEBUG and use y += A\*x without noalias(); the Rust side is the authors' tuned faer fork; MIT in Cargo.toml only, no LICENSE file; arXiv 2606.19213 unopened.
- Harness flaw: the Eigen SpMV wrapper does y += A\*x without .noalias(), and Eigen 3.4.0 and 5.0.0 sources confirm a temporary vector per call; the Eigen Lanczos wrappers use noalias, where the gap is 1.04x against 1.12x for SpMV. The Rust Lanczos fuses axpy and dot while the Eigen wrapper does not; the MKL mv hint is commented out; Eigen, PETSc and MKL are unpinned, psblas@develop, no spack.lock; eigen.cpp's comment says -ffast-math but build.rs does not use it. codeberg.org and arxiv.org blocked, so the fork kernel and paper went unread.

## Caveats and trade-offs

The repo has no LICENSE file, only license = "MIT" in Cargo.toml, so usability stays reference (upstream faer is already catalogued). The Rust side is a CSR SpMV specialisation the authors wrote in their own faer fork (codeberg.org/lukefleed/faer, commit 009ac1eb pinned in Cargo.lock; codeberg was unreachable here). That is a tuned kernel set against stock library kernels. Two Eigen-baseline weaknesses (ffi/spmv/eigen.cpp, build.rs): the wrappers compile without -DNDEBUG, so eigen_assert checks stay on, and the product runs as '\*(ctx-&gt;y) += A \* x' without .noalias(). Under Eigen's default product-aliasing rule that may evaluate into a temporary vector every call (not measured). Either could explain part of the 1.12x Eigen gap. The outcome is mixed: Rust beats Eigen on geomean and is at parity with PSBLAS CSR, but loses to oneMKL and PETSc on CSR SpMV and to PETSc on both Lanczos variants; per-matrix ratios against PETSc range 0.54-1.47. The companion paper (arXiv 2606.19213) is a preprint and was not opened (arXiv blocked). The authors ran the benchmarks on one machine. [retier] The Eigen SpMV wrapper does y += A\*x without .noalias(), so Eigen 3.4.0 and 5.0.0 build a temporary vector per call; the Eigen Lanczos wrappers use noalias, where the gap is 1.04x against 1.12x for SpMV. The Rust Lanczos fuses axpy and dot while the Eigen wrapper does not; the MKL mv hint is commented out; Eigen, PETSc and MKL are unpinned, psblas@develop, no spack.lock; eigen.cpp's comment says -ffast-math but build.rs does not use it.

Single core only; the Rust CSR SpMV specialization lives in a fork of faer on Codeberg (lukefleed/faer) pinned in Cargo.toml, not in this repo; needs nightly Rust and a Spack environment with MKL, PETSc and PSBLAS.

## Maintenance

Research companion repo (58 commits, last 2026-06-18, 4 stars, no releases) with no LICENSE file, so reference use only. Reproducing it needs nightly Rust, an unreleased faer fork on Codeberg and a full Spack HPC stack. The Rust-beats-Eigen result is partly a harness artifact (the Eigen SpMV wrapper builds a temporary on every call), and Rust loses to oneMKL and PETSc throughout.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** The benchmark code is public (benches/spmv.rs, benches/lanczos.rs, benches/lanczos_two_pass.rs, ffi/ wrappers, build.rs, spack.yaml). Compilers and flags for both sides are stated (rustc nightly-2026-04-14, opt-level 3, fat LTO, target-cpu=native; clang 22 at -O3 -march=native -mtune=native -flto), and so is the CPU (Xeon Gold 6418H, one pinned core). I re-derived every geomean ratio in the record from python/data/summary.csv.
- **Retiered** A to C: Enricher: the Eigen SpMV wrapper omits .noalias() and so allocates a temporary vector per call (Eigen 3.4.0 and 5.0.0 sources), crippling the headline baseline (the noalias Lanczos wrappers show a 1.04x gap against 1.12x), with Eigen, PETSc and MKL unpinned. Crippled-baseline precedent: A to C.
- **Verifier notes:** Confirm at A; all of the record's ratios check out against summary.csv. Shortcomings to record: a mixed result (loses to oneMKL and PETSc, parity with PSBLAS), Eigen wrappers built without -DNDEBUG and using y += A\*x without noalias(), the Rust side being the authors' own tuned faer fork, a license declared only in Cargo.toml, and an un-reviewed preprint. Metadata checked: 4 stars, last commit 2026-06-18, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-79 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/python/data/summary.csv>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/build.rs>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/spack.yaml>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/benches/spmv.rs>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/ffi/spmv/eigen.cpp>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/rust-lang/cc-rs/main/src/lib.rs>
  - <https://raw.githubusercontent.com/rust-lang/cc-rs/main/src/flags.rs>
  - <https://github.com/lukefleed/hpla-rs>
  - <https://github.com/lukefleed/hpla-rs/commits/main>
- **Sources the enricher read:**
  - <https://github.com/lukefleed/hpla-rs>
  - <https://github.com/lukefleed?tab=repositories>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/python/data/summary.csv>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/build.rs>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/spack.yaml>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/benches/spmv.rs>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/benches/lanczos.rs>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/benches/lanczos_two_pass.rs>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/src/lanczos/algorithms/mod.rs>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/ffi/spmv/eigen.cpp>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/ffi/spmv/petsc.c>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/ffi/spmv/mkl.c>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/ffi/spmv/psblas.cpp>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/ffi/lanczos/eigen_lanczos.cpp>
  - <https://raw.githubusercontent.com/lukefleed/hpla-rs/HEAD/ffi/lanczos/eigen_lanczos_two_pass.cpp>
  - <https://raw.githubusercontent.com/lukefleed/two-pass-lanczos/HEAD/README.md>
  - <https://raw.githubusercontent.com/lukefleed/compressed-intvec/HEAD/README.md>
  - <https://gitlab.com/libeigen/eigen/-/raw/3.4.0/Eigen/src/Core/ProductEvaluators.h>
  - <https://gitlab.com/libeigen/eigen/-/raw/3.4.0/Eigen/src/Core/AssignEvaluator.h>
  - <https://gitlab.com/libeigen/eigen/-/raw/3.4.0/Eigen/src/Core/CwiseBinaryOp.h>
  - <https://gitlab.com/libeigen/eigen/-/raw/3.4.0/Eigen/src/SparseCore/SparseDenseProduct.h>
  - <https://gitlab.com/libeigen/eigen/-/raw/3.4.0/Eigen/src/SparseCore/SparseProduct.h>
  - <https://gitlab.com/libeigen/eigen/-/raw/3.4.0/Eigen/src/SparseCore/SparseAssign.h>
  - <https://gitlab.com/libeigen/eigen/-/raw/5.0.0/Eigen/src/Core/ProductEvaluators.h>
  - <https://gitlab.com/libeigen/eigen/-/raw/5.0.0/Eigen/src/SparseCore/SparseDenseProduct.h>
  - <https://raw.githubusercontent.com/spack/spack-packages/develop/repos/spack_repo/builtin/packages/eigen/package.py>
  - https://codeberg.org/lukefleed/faer/commit/009ac1ebfc150131a4eded7a252f4c16a5f1c5ad (blocked: proxy 403)
  - https://arxiv.org/abs/2606.19213 (blocked: ENOTFOUND)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/lukefleed/hpla-rs`) · [data/wave14/enrich/raw/github_com_lukefleed_hpla_rs.json](../../../data/wave14/enrich/raw/github_com_lukefleed_hpla_rs.json) (enrichment confidence 0.75)

</details>
