# DirectLUSolvers (MultifrontalQR, SupernodalLDLT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MPL-2.0` · 🟢 active

> Header-only Eigen add-on: rank-revealing sparse QR far faster than Eigen::SparseQR, plus supernodal LDL^T beating SimplicialLDLT.

| | |
|---|---|
| **Beats** | Eigen::SparseQR (MultifrontalQR); also Eigen::SimplicialLDLT and Eigen::SparseLU for the LDLT/LU solvers |
| **Claimed result** | MultifrontalQR factorization (including rank verification) is 5-6900x faster than Eigen::SparseQR over the 34 SuiteSparse-collection matrices both finished, median 59x per the page (about 56x recomputed from the displayed table, derived from page data); e.g. cell2 66.6 s vs 20 ms, swang2 3182 ms vs 7.7 ms, TSOPF_RS_b9_c6 32.5 s vs 4.7 ms, raefsky2 3095 ms vs 622 ms (the 5x low end). On the author's own setfos samples (separate table): DriftDiffusion n29841 8461 ms vs 0.52 ms. It also returns the right rank where Eigen::SparseQR does not (raefsky5: Eigen reports rank 622 of 6316). SupernodalLDLT is 6.5x faster than Eigen::SimplicialLDLT on lap3d 40^3 (doc/SupernodalLDLT.md). |
| **Workload** | Sparse QR factorization time, single thread, on 38 SuiteSparse-collection matrices (34 finished by both; Eigen had 300 s per run), b = A\*xTrue, MultifrontalQR best of 3 with rank verification included while Eigen::SparseQR (COLAMD ordering) is timed in a single run; plus six matrices from the author's own setfos application corpus. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 5950X (16 cores): stated in doc/Parallelism.md for 2026-09-17 runs, not restated beside the QR table |
| **Compiler and flags** | clang 22, -O3 at the default x86-64 ISA, CMake Release build: stated in doc/Parallelism.md for same-date benchmarks, not restated beside the QR table |
| **Adoption** | 0 stars; 106 commits; docs dated from 2026-08-22, so under 6 weeks of public history |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/rhiestan/DirectLUSolvers) · [benchmark](https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/doc/MultifrontalQR.md) |

## Verdict

First-party, single-threaded runs by the author: MultifrontalQR (best of three, rank verification included) against one run of Eigen::SparseQR with COLAMD ordering and a 300 s limit, on 38 SuiteSparse-collection matrices with b = A\*xTrue, gave 5-6900x faster factorization on the 34 both finished (page median 59x, about 56x from the displayed rows). Hardware and compiler are stated only for same-date runs in doc/Parallelism.md (AMD Ryzen 9 5950X, clang 22 -O3 at the default x86-64 ISA).

## Use it when

- You use Eigen::SparseQR today for least squares, rank detection or singular systems: the author's table shows 5-6900x faster factorization (median 59x) on 34 SuiteSparse matrices, and correct ranks where SparseQR is wrong (raefsky5: 622 of 6316).
- Badly scaled or rank-deficient sparse systems where you need a verified numerical rank, a minimum-norm solution or a null-space basis, real or complex.
- Symmetric sparse systems in an Eigen codebase, including indefinite saddle-point/KKT matrices: SupernodalLDLT factored a 64,000-unknown 3D Laplacian 6.5x faster than Eigen::SimplicialLDLT single-threaded.
- Projects that want no link-time dependencies: the core needs only Eigen 3.3+ and C++17; METIS, OpenMP, oneTBB and MKL are opt-in.

## Skip it when

- When you can use SuiteSparseQR (SPQR), CHOLMOD or PARDISO: the QR benchmark never compares against SPQR, and on the laoss FEM matrices SupernodalLU is about 1.2-1.8x behind MKL PARDISO single-threaded (derived from page data); the 59x median is against a weak baseline.
- General unsymmetric square systems where you would use Eigen::SparseLU: the docs say SupernodalLU is typically 2-3x slower and denser than SparseLU on the testdata set, and for regular square systems an LU is cheaper than MultifrontalQR (3-4x slower than the fastest solver on the small setfos categories).
- Small 2D problems where analysis dominates: Eigen::SimplicialLDLT wins analyze time by about 2-3x and can be the better total choice.
- Production code that needs a long track record: zero stars, one author, public history since 2026-08 with commits co-authored by an AI coding assistant, and a batch of crash and stale-factor fixes as recent as 2026-09-17.
- Very fill-heavy QR problems: matrices with 10-20M entries in R (as-caida, foldoc) take 12-20 s single-threaded, and Q is kept as Householder vectors of about the same size as R.

## How it is fast

MultifrontalQR's main gain is structural: Eigen::SparseQR never permutes rows, so R fills in badly (16.8M entries against 87k on TSOPF_RS_b9_c6), while this solver assigns each row to the front of its leftmost column (multifrontal, blocked compact-WY Householder per front) or, for sparse R, uses a scalar left-looking Householder QR with CSparse's cs_vcount row assignment; an Auto mode picks the engine per matrix and the ordering (COLAMD or AMD on A^H A) by predicted nnz(R). Rank is decided with Heath's rule on a row- and column-equilibrated matrix, then verified with condition estimates or inverse iteration and repaired with an SVD of a deferred block. SupernodalLDLT uses supernodes with BLAS-3 style dense kernels and Bunch-Kaufman 2x2 pivots instead of Eigen's scalar simplicial code; fronts or supernodes in one elimination-tree level, plus chunks of large root updates, run in parallel through a pluggable Executor.

## Compared with alternatives

No catalogued sibling offers sparse QR, so this is the pick for rank-revealing or least-squares sparse solves inside Eigen. For symmetric systems, choose SupernodalLDLT over BaSpaCho or Sympiler when the matrix may be indefinite or you want a header-only Eigen drop-in; those siblings target SPD Cholesky and are measured against CHOLMOD, a stronger baseline.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Eigen 3.3+ only for the core; optional METIS + GKlib, OpenMP, oneTBB, MKL PARDISO (benchmarks only); CMake build of the tests needs Threads |
| **Minimum toolchain** | C++17; documented builds with clang++ (GNU driver, LLVM 22 verified), clang-cl/MSVC on Windows and GCC; CMake 3.16 for the tests |
| **Platforms** | Portable C++17 with no ISA-specific code mentioned; measured on x86-64 (AMD Ryzen 9 5950X) at the default x86-64 ISA |
| **Thread safety** | Not documented for concurrent use of one solver object; separate solver objects are independent (the bench_ceiling driver runs independent factorizations concurrently). Internal parallelism goes through a chosen Executor (Serial default, std::thread pool, OpenMP or TBB), and MultifrontalQR's parallel results are documented as bit-identical to serial. |
| **Drop-in for the baseline** | partial — same compute/solve/info interface as Eigen::SparseQR and Eigen::SimplicialLDLT, but different template parameters and options, and MultifrontalQR returns the minimum-norm solution by default where SparseQR returns a basic one |

## Gotchas

- MultifrontalQR's default Scaling::Auto equilibrates rows only for square matrices; for rectangular least squares it scales columns only, and row scaling turns least squares into a weighted problem, so set Scaling::RowsAndColumns only when the rank decision matters more than the weights.
- Rank verification is on by default and costs from a tenth of the factorization up to 1.6x it; setRankVerification(false) removes it, and the headline timings include it.
- The CMake build forces Release before project() because an MSVC-targeting toolchain otherwise builds at -O0, a 50-100x timing error; in your own build make sure optimization is on.
- Do not pre-symmetrize input to LeftRightLU or PointBlockLU: the docs measured 102x more fill on gemat11.

## Known shortcomings

- Claim fixed: the DriftDiffusion example comes from the author's own setfos table, not the 34 SuiteSparse matrices; the displayed table gives a median of about 56x vs 59x stated (derived from page data); the bench times Eigen::SparseQR once but MFQR best of 3; weak baseline (no SPQR comparison); SupernodalLU is 2-3x slower than Eigen::SparseLU on general matrices, so it is dropped from the name; GitHub description says 'implemented with Claude Code'.
- Weak baseline: compared only against Eigen::SparseQR, never SuiteSparseQR (SPQR). Crash and stale-factor fixes landed 2026-09-17, the same day as the benchmark re-runs. Commits are co-authored with an AI assistant.

## Caveats and trade-offs

Very new (docs dated from 2026-08), zero-star, one-author project; the GitHub description reads 'Sparse direct LU solvers based on Eigen, implemented with Claude Code'. All numbers are the author's own, from the repo's benchmark drivers (test/bench_multifrontal_qr.cpp, test/bench_setfos_samples.cpp); hardware and compiler are recorded in doc/Parallelism.md, not beside the QR table. bench_multifrontal_qr times Eigen::SparseQR once but MultifrontalQR as best of N. Eigen::SparseQR is a weak baseline (the docs say it never permutes rows, so it has huge fill and wrong rank on badly scaled matrices); there is no comparison against SuiteSparseQR (SPQR), the real incumbent for sparse QR. Three matrices where only Eigen timed out (as-caida, foldoc, onetone2) are excluded from the median. The page's stated median (59x) is slightly above what the displayed table gives (about 56x). SupernodalLU is typically 2-3x slower and denser than Eigen::SparseLU on general unsymmetric matrices (doc/SupernodalLU.md), though 2.4-2.6x faster on the large laoss FEM matrices, so the speedup claim applies mainly to QR and symmetric LDLT; SimplicialLDLT still wins analyze time by 2-3x.

Header-only C++17 on top of Eigen, with optional METIS, oneTBB, OpenMP and MKL. Eigen-style solver interface (compute/solve/info). MultifrontalQR is rank-revealing and handles any matrix shape. The same repo also offers SupernodalLDLT (README and doc/SupernodalLDLT.md claim about 2x faster factorization than its own LU on symmetric 3D Laplacians and 6.5x vs Eigen::SimplicialLDLT at n=64000, though SimplicialLDLT wins on analyze time) and SupernodalLU/LeftRightLU, which the docs say are typically 2-3x slower and denser than Eigen::SparseLU on general matrices (but more robust on some matrices Eigen::SparseLU fails on) and about 1.5-1.8x behind MKL PARDISO.

## Maintenance

Very active (106 commits, last commit 2026-09-29) but very young and unproven, with zero stars; MPL-2.0 and header-only, so it is easy to vendor alongside Eigen as long as modified files stay MPL-licensed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party table in doc/MultifrontalQR.md driven by public test/bench_multifrontal_qr.cpp, but compiler, flags and CPU are not stated for the QR runs (clang 22 -O3 on a Ryzen 9 5950X appears only in doc/Parallelism.md for the bench_parallel runs), and the median gain is above 50x, so C.
- **Verifier notes:** Range 5-6900x, median 59x, cell2, swang2 and raefsky5 rank all on doc/MultifrontalQR.md; the DriftDiffusion example comes from the separate setfos table, not the 34-matrix SuiteSparse set, so claimed_speedup was reworded. Name lists SupernodalLU, which is generally slower than Eigen::SparseLU; consider dropping it from the name. MPL-2.0, 0 stars, 106 commits, last commit 2026-09-29 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/doc/MultifrontalQR.md>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/doc/Parallelism.md>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/doc/Testing.md>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/doc/SupernodalLU.md>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/doc/SupernodalLDLT.md>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/test/bench_multifrontal_qr.cpp>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/README.md>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/LICENSE>
  - <https://github.com/rhiestan/DirectLUSolvers>
  - <https://github.com/rhiestan/DirectLUSolvers/commits>
- **Sources the enricher read:**
  - <https://github.com/rhiestan/DirectLUSolvers>
  - <https://github.com/rhiestan/DirectLUSolvers/commits/main>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/README.md>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/doc/MultifrontalQR.md>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/doc/SupernodalLDLT.md>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/doc/SupernodalLU.md>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/doc/Parallelism.md>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/doc/Testing.md>
  - <https://raw.githubusercontent.com/rhiestan/DirectLUSolvers/HEAD/test/bench_multifrontal_qr.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/rhiestan/directlusolvers`) · [data/wave8/enrich/raw/github_com_rhiestan_directlusolvers.json](../../../data/wave8/enrich/raw/github_com_rhiestan_directlusolvers.json) (enrichment confidence 0.8)

</details>
