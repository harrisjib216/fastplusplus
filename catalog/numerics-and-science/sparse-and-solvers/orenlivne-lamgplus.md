# LAMG+ (lean algebraic multigrid for graph Laplacians)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `Apache-2.0` · 🟢 active

> Julia algebraic multigrid solver for graph-Laplacian systems; 6.6-13.6x faster than PETSc GAMG on social, web and optimization graphs.

| | |
|---|---|
| **Beats** | PETSc GAMG; the same study also runs hypre BoomerAMG, pyAMG, CMG and approximate Cholesky (Laplacians.jl approxchol_lap) |
| **Claimed result** | Class table in doc/lamg_plus.tex, mean microseconds/nnz LAMG+ vs PETSc GAMG: social/citation 0.47 vs 3.10 (about 6.6x, derived from page data), web 0.37 vs 2.76 (7.5x), optimization 0.15 vs 2.04 (13.6x), chimera 0.40 vs 0.91, weighted chimera 0.45 vs 0.96, SDDM chimera 0.30 vs 1.74, anisotropic grid 0.61 vs 1.01; tie on FE/structural (0.12 vs 0.12); PETSc GAMG faster on mesh/grid (0.84 vs 0.23), 3D grid (1.30 vs 0.25), roads (0.68 vs 0.57) and SPE reservoir (1.09 vs 0.90). Versus BoomerAMG: social 0.47 vs 1.53, web 0.37 vs 1.43, optimization 0.15 vs 4.07. |
| **Workload** | Setup plus solve time per nonzero (microseconds/nnz) to relative residual 1e-8 on graph-Laplacian systems from a class-stratified SuiteSparse/SNAP corpus, serial runs, one Julia process. |
| **Metric** | latency |
| **Hardware** | Apple M5 Pro, 18 cores, 48 GB RAM |
| **Compiler and flags** | Julia 1.10 or newer (notebook kernel julia-1.12); competitors run in the same Julia process; build flags not stated |
| **Adoption** | 0 stars |
| **Last commit** | 2026-07-06 |
| **Links** | [repository](https://github.com/orenlivne/lamgplus) · [benchmark](https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/doc/lamg_plus.tex) |

## Verdict

Source: the author's arXiv preprint in the repo (doc/lamg_plus.tex). Setup plus solve to 1e-8 relative residual, run serially on an Apple M5 Pro and reported as mean microseconds per nonzero for each graph class over a class-stratified SuiteSparse/SNAP corpus plus synthetic families. LAMG+ beats PETSc GAMG on social/citation (0.47 vs 3.10), web (0.37 vs 2.76), optimization (0.15 vs 2.04) and the chimera families, ties on FE/structural (0.12), and loses on mesh/grid, 3D grid, road, SPE and star. PETSc, hypre and pyAMG were prebuilt binaries with unstated build flags.

## Use it when

- Laplacian solves on large irregular graphs (social, citation, web, optimization/network-flow), where PETSc GAMG and BoomerAMG slow down by up to an order of magnitude. Class means: 0.47 vs 3.10 us/nnz on social, 0.15 vs 2.04 on optimization.
- Finite-element and structural graph Laplacians. Among the robust solvers it was fastest there (for example bmwcra_1 0.08 vs 0.28 us/nnz for approxchol_lap) and leanest in memory (21-30 bytes/nnz vs 33-55 for approximate Cholesky).
- Graphs with high mean degree: the paper's rule 'LAMG+ wins iff mean degree &gt;= 30' picked the faster solver against approxChol 91% of the time.
- Many right-hand sides on one graph (the hierarchy is reused), or lower-accuracy solves: at 1e-4 its geometric-mean speedup over approxchol_lap rises from 0.99x to 1.20x.
- Julia pipelines (spectral clustering, electrical flow, interior-point network flow) that want a solver depending only on Julia standard libraries.

## Skip it when

- Meshes, grids, roads and reservoir models: PETSc GAMG is faster on mesh/grid (0.23 vs 0.84 us/nnz), 3D grid (0.25 vs 1.30), road (0.57 vs 0.68) and SPE (0.90 vs 1.09), and BoomerAMG is faster still on grids.
- Social, web, citation and chimera graphs when Laplacians.jl approxchol_lap is an option: it is faster there (social 0.25 vs 0.47, web 0.29 vs 0.37, chimera 0.14 vs 0.40 us/nnz).
- C or C++ codebases: the solver is Julia-only and no C API is documented.
- General SPD, SDDM or unsymmetric matrices, and disconnected graphs: `setup` asserts zero row sums, and the library handles several components by reducing to one connected component (`largest_component`) instead of solving them all.
- Multi-core or distributed runs, and memory-tight web/social workloads. All published timings are single-threaded, the paper calls distributed coarsening unresolved, and the hierarchy takes 62-80 bytes/nnz on web/social graphs vs 32-40 for approxChol.

## How it is fast

It implements Lean Algebraic Multigrid (Livne and Brandt, SIAM J. Sci. Comput. 2012). Exact low-degree elimination, a Schur complement over an independent set of nodes with degree at most 4, alternates with caliber-1 (piecewise-constant) aggregation. Because of this, the Galerkin coarse operators stay as sparse as the graph and do not fill in around scale-free hubs the way classical AMG does. Nodes are grouped into aggregates by the affinity (squared cosine) of K=4 Gauss-Seidel-relaxed test vectors, subject to an energy-ratio guard. LAMG+ adds a strength-of-connection veto and a selective caliber-2 interpolation that fix stalls on grid-aligned anisotropy. The paper credits the low per-edge constants to a self-gated reverse Cuthill-McKee reordering, single-pass Gustavson-fused Schur extraction, allocation-free elimination and an in-place, residual-maintaining Gauss-Seidel kernel.

## Compared with alternatives

Pick AMGCL (C++ header-only AMG with faster setup than PETSc GAMG) for PDE and mesh systems in C++. Pick apxchol for parallel approximate-Cholesky Laplacian/SDDM solves from C++. Pick LAMG+ for serial Julia work on graph Laplacians, especially FE/structural or high-degree graphs, where it beats approximate Cholesky.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none beyond Julia standard libraries (LinearAlgebra, SparseArrays, Random, Statistics, Printf); the comparison scripts also need Laplacians.jl, HYPRE.jl, PyCall/pyAMG and PETSc_jll in a separate environment |
| **Minimum toolchain** | Julia 1.10+ |
| **Platforms** | any platform Julia supports (no other restriction documented); the paper's timings are from an Apple M5 Pro |
| **Thread safety** | not documented; published runs are single-threaded (julia -t1), and when nthreads() &gt; 1 the residual and multicolor Gauss-Seidel kernels spread over threads on levels with at least 20,000 nodes |
| **Drop-in for the baseline** | no |

## Gotchas

- The right-hand side must be compatible (zero mean), and the solution is returned orthogonal to the constant vector. The default `max_cycles` is 100, so check `info.cycles` and the residual on hard inputs.
- Setup is randomized (relaxed test vectors) but seeded with a fixed MersenneTwister seed (0xfa11), so runs repeat exactly unless you change `LAMGOptions.seed`.
- The class-comparison harness defaults to graphs with at most 5,000,000 nonzeros and 6 graphs per class. PETSc GAMG, pyAMG and CMG run in subprocesses (PETSc GAMG from the prebuilt PETSc_jll binary, timed inside the subprocess with startup excluded), and hypre runs through HYPRE.jl, which contradicts the paper's statement that every competitor runs in the same Julia process.
- Version 0.1.0 with no release tags. The package UUID is hand-written, and the README installs it from the cloned project, not from a package registry.

## Known shortcomings

- Mixed vs PETSc GAMG: wins 7 of 13 classes and loses 5; PETSc/pyAMG run in subprocesses, not in the same process as the paper says; Claude is co-author on every commit.
- Julia only, no C API (off-language). The paper says competitors run in the same Julia process, but run_class_comparison.jl runs PETSc GAMG/pyAMG/CMG in subprocesses from prebuilt binaries. Class-table defaults: nnz cap 5M, 6 graphs per class. Loses to PETSc GAMG on mesh/grid/3D/road/SPE classes.

## Caveats and trade-offs

Author-run, first-party; the paper in the repo (doc/lamg_plus.tex, arXiv 2606.24791 preprint) is the evidence. PETSc GAMG is beaten only on some classes: it is faster than LAMG+ on mesh/grid, 3D grid, roads, SPE reservoir and star graphs, and fails to converge on 6 instances. The strongest peer, approxchol_lap (Laplacians.jl), is faster than LAMG+ on social/web/chimera/grid classes; over the 201 graphs with m&gt;1e6 LAMG+ is at parity with it (0.99x geometric mean at 1e-8, 1.20x at 1e-4) and wins on FE/structural matrices (for example bmwcra_1 0.08 vs 0.28 us/nnz). The paper says competitors run in the same Julia process, but scripts/run_class_comparison.jl runs PETSc GAMG (PETSc_jll) and pyAMG in subprocesses and hypre through HYPRE.jl, all prebuilt binaries with unstated build flags. Corpus matrices are not shipped (tens of GB, downloadable from SuiteSparse/SNAP). Commit history shows AI-assistant (Claude) co-authorship on every recent commit.

Graph-Laplacian systems only (SPD with the constant vector in the null space); empirically linear-time but no worst-case guarantee; hierarchy memory is 62 to 80 bytes/nnz on web/social graphs against 32 to 40 for approximate Cholesky, and 22 to 30 bytes/nnz on FE/structural matrices.

## Maintenance

Active single-author research code (49 commits, last commit 2026-07-06, 0 stars, no releases). Apache-2.0 and free of dependencies, but Julia-only and not packaged in a registry.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/lamg_plus.tex Table tab:classcomp gives exactly the quoted mean/worst microseconds per nnz for LAMG+, PETSc GAMG, BoomerAMG and others, measured on an Apple M5 Pro; the benchmark code is public (scripts/run_class_comparison.jl, petsc_bench.jl) but no exact Julia version or competitor build flags are stated, and the paper is an author-run arXiv preprint, not peer reviewed, so C.
- **Verifier notes:** Every quoted class-table number matches the tex. Repo: Apache-2.0, 0 stars, 49 commits, last commit 2026-07-06, not a fork. Mixed result versus PETSc GAMG: LAMG+ wins 7 of 13 classes, ties FE/structural, and loses 5 (mesh/grid, grid-3D, road, SPE, and star 0.05 vs 0.04).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/doc/lamg_plus.tex>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/README.md>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/scripts/run_class_comparison.jl>
  - <https://github.com/orenlivne/lamgplus>
  - <https://github.com/orenlivne/lamgplus/commits>
- **Sources the enricher read:**
  - <https://github.com/orenlivne/lamgplus>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/README.md>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/doc/lamg_plus.tex>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/src/LAMG.jl>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/src/setup.jl>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/src/graph.jl>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/src/relaxer.jl>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/src/coarsen.jl>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/src/elimination.jl>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/src/solve_cycle.jl>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/src/interpolation.jl>
  - <https://raw.githubusercontent.com/orenlivne/lamgplus/HEAD/scripts/run_class_comparison.jl>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/orenlivne/lamgplus`) · [data/wave8/enrich/raw/github_com_orenlivne_lamgplus.json](../../../data/wave8/enrich/raw/github_com_orenlivne_lamgplus.json) (enrichment confidence 0.75)

</details>
