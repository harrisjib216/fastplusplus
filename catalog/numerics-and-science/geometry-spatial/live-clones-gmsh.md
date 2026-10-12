# HXT parallel 3D Delaunay (in Gmsh)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-2.0-or-later` · 🟢 active

> Gmsh's HXT module: OpenMP-parallel 3D Delaunay tetrahedralization in C, about 3x faster serially than CGAL, TetGen and Geogram.

| | |
|---|---|
| **Beats** | CGAL 3D Delaunay triangulation (CGAL 4.12) |
| **Claimed result** | Sequential: \~2 s for 1M points vs \~6 s for CGAL/TetGen/Geogram (about 3x, abstract); parallel on 64-core Xeon Phi 7210, 10M points: 4.48 s vs CGAL 4.12 20.15 s, CGAL did not complete 10^8 points (Fig. 11b); 3 billion tetrahedra in 53 s on AMD EPYC |
| **Workload** | 3D Delaunay triangulation of 1M to 100M+ random points, sequential and parallel |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700HQ; Intel Xeon Phi 7210 (64 cores); AMD EPYC 7551 dual socket |
| **Adoption** | 127 stars on GitHub mirror; Gmsh is widely used FEM mesher |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/live-clones/gmsh) · [benchmark](https://arxiv.org/abs/1805.08831) |

## Verdict

The HXT authors' paper (arXiv 1805.08831, published in IJNME 117(9):967-990, 2019 per the HXT README and the Gmsh manual) reports a serial kernel about 3x faster than CGAL, TetGen and Geogram (about 2 s vs about 6 s for 1M random points). In parallel it reports 10M points in 4.48 s vs 20.15 s for CGAL 4.12 on a 64-core Xeon Phi 7210, with CGAL not completing 10^8 points, and 3 billion tetrahedra in 53 s on a dual-socket EPYC 7551. Compiler and flags are not stated, the authors wrote HXT, and CGAL 4.12 (2018) is old.

## Use it when

- Unconstrained 3D Delaunay of 10^6 to 10^9 points on a many-core shared-memory CPU: 10M points in 4.48 s on a 64-core Xeon Phi 7210 vs 20.15 s for CGAL 4.12, and 3 billion tetrahedra in 53 s on a dual-socket EPYC 7551 (paper)
- Volume tetrahedral meshing for FEM inside Gmsh, where Mesh.Algorithm3D=10 parallelises the meshing of a single volume (the default Delaunay algorithm does not)
- GPL-compatible open-source C or C++ codes that want a fast Delaunay kernel and can vendor C99 sources built as CMake object libraries
- Pipelines that need bit-identical meshes across thread counts: reproducible=1 reorders the output deterministically, at extra cost

## Skip it when

- Proprietary or closed-source products: HXT is GPL-2.0-or-later, and its exception only covers combining with Gmsh's own code
- Dynamic or specialised triangulations (vertex removal, incremental point location queries, weighted/regular or periodic Delaunay): CGAL has them, while HXT's single-point insertion API is commented out as 'NOT IMPLEMENTED YET'
- More than about 4.29 billion vertices: vertex indices are uint32_t (ghost vertex = UINT32_MAX), and '40+ bits nodes' is still a TODO in the README
- Robustness-first meshing of messy CAD or STL input: the Gmsh manual calls the default 'Delaunay' algorithm the most robust and the only one that makes hybrid meshes with pyramids. Search results list Gmsh tracker issues on HXT crashes in reshapeCavityIfNeeded, failures on discontinuous STL and runaway memory with size fields (not opened)
- An NVIDIA GPU is available and the point set fits in its memory: gDel3D is the GPU alternative

## How it is fast

Points are sorted along a Moore (closed Hilbert) space-filling curve with radix sort and inserted in BRIO rounds by the Bowyer-Watson kernel: walk to the containing tetrahedron, breadth-first search to dig the cavity with Shewchuk's adaptive orient3d/insphere predicates (Devillers-Teillaud symbolic perturbation breaks ties), then refill it, computing the new adjacencies in `omp simd` loops over aligned buffers. For parallelism each OpenMP thread owns a contiguous range of Moore indices. An insertion whose cavity touches a vertex outside the thread's range is deferred to a later round, which re-sorts along a randomly shifted Moore curve and lowers the thread count when the conflict ratio rises. Conflicts are avoided by these partition-ownership checks, not by per-element locks; the README lists Geogram-style point locks only as future work.

## Compared with alternatives

Among the catalogued siblings only gDel3D also does 3D Delaunay, and it needs a CUDA GPU (4-10x over serial CGAL 4.2). Pick HXT for many-core CPUs, no NVIDIA GPU, or point sets too large for GPU memory. The other siblings (mesh booleans: Manifold, MeshLib, trueform; spatial indexes: nanoflann, rtree.c, KdBoxTree, THST) solve different problems.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenMP 4 (optional, with a serial fallback) and libm; tetMesh also needs HXT core, predicates (Shewchuk) and tetBR (TetGen/BR boundary recovery, C++). Full Gmsh optionally adds FLTK and OpenCASCADE. |
| **Minimum toolchain** | C99 compiler plus a C++ compiler for tetBR, CMake 3.9+; the README builds with -march=native so that parts of tetMesh auto-vectorise |
| **Platforms** | Any platform with a C99/OpenMP compiler. The paper ran on x86-64 (Core i7-6700HQ, Xeon Phi 7210, EPYC 7551). The standalone HXT CMake turns OpenMP off by default under MSVC, which makes it serial. |
| **Thread safety** | Internally OpenMP-parallel (delaunayThreads: 0 = omp_get_max_threads, &lt;0 = omp_get_num_procs); calling it concurrently from user threads is not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- An error inside the parallel insertion region calls exit() (the HXT_OMP_CHECK macro in hxt_tetDelaunay.c), so a failure kills the host process instead of returning an HXTStatus
- Licensing trap when extracting HXT from Gmsh: the standalone tetBR copy is TetGen 1.5 code headed 'redistributed for non-commercial use' and is relicensed only for use in Gmsh. The source emits the compile warning 'Using TetgenBR without Gmsh - please note the different licensing terms', and the tetMesh CMake always links tetBR.
- hxtDelaunay reorders mesh-&gt;vertices into Moore order, overwrites each vertex's 4th coordinate and deletes vertices it could not insert; use hxtDelaunaySteadyVertices when indices must stay stable. Multithreaded tetrahedron order is nondeterministic unless reproducible=1.
- Gmsh's default 3D algorithm is Delaunay (1), not HXT, so you must set Mesh.Algorithm3D=10 or -algo hxt to get this code path, including through gmsh::algorithm::tetrahedralize

## Known shortcomings

- No compiler or flags; authors are Gmsh developers; CGAL 4.12 baseline is old; repo is a mirror; venue unconfirmed by verifier.
- Licence trap: tetMesh CMake always links tetBR, whose standalone copy is TetGen 1.5 'non-commercial use' code relicensed only for use inside Gmsh (source warns 'Using TetgenBR without Gmsh - please note the different licensing terms').
- HXT_OMP_CHECK calls exit() on error inside a parallel region, killing the host process; uint32 vertex indices; Gmsh's default 3D algorithm is Delaunay (1), not HXT (10), so users must opt in.

## Caveats and trade-offs

Compiler and flags not stated in the paper; repo_url is the live-clones mirror of canonical gitlab.onelab.info/gmsh/gmsh; 2018 paper so CGAL 4.12 is old; authors are Gmsh developers (first-party); last_commit is for Gmsh as a whole; GPL-2.0-or-later with a linking exception. [retier] Venue confirmed as Int J Numer Methods Eng 117(9):967-990 (2019), DOI 10.1002/nme.5987 (peer-reviewed; the authors are the Gmsh/HXT developers). The paper states no compiler or flags. contrib/hxt/README.md recommends building with CMAKE_BUILD_TYPE=Release and -march=native (C and CXX flags) and says `Delaunay_CLI -sv2 -G10000000` gives logs very similar to Table 2 of the paper, but that reproduces only the HXT side. The CGAL/TetGen/Geogram comparison harness is not in the repo, and those README flags are recommendations, not the stated paper build.

GPL (with linking exception for external libraries) code inside a large mesh generator; HXT lives under contrib/hxt in Gmsh; floating-point predicates are exact-adaptive.

## Maintenance

Gmsh is very active (mirror commits on 2026-09-28; the canonical repo is gitlab.onelab.info), but the HXT Delaunay file changes rarely: its last edits were 2025 warning fixes and a division-by-zero guard. It is GPL-2.0-or-later, so it can only be copied into GPL-compatible code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Research paper (arXiv 1805.08831, by the Gmsh authors) times CGAL 4.12 against HXT on named CPUs; no compiler/flags stated, so not A. First-party authors, but a peer-reviewed-style paper; B kept.
- **Verifier notes:** Numbers checked in the arXiv PDF (v3). I did not confirm the journal venue (believed published in IJNME, unverified), so tier B rests on it being a research paper; orchestrator may retier to C if strict on first-party. Mirror: 127 stars, last commit 2026-09-28.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** paper Fig. 11b: 10M points on 64-core Xeon Phi 4.48 s vs CGAL 4.12 20.15 s
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/1805.08831>
  - <https://arxiv.org/pdf/1805.08831>
  - <https://github.com/live-clones/gmsh>
  - <https://github.com/live-clones/gmsh/commits>
- **Sources the enricher read:**
  - <https://github.com/live-clones/gmsh>
  - <https://github.com/live-clones/gmsh/commits>
  - <https://github.com/live-clones/gmsh/commits/master/contrib/hxt/tetMesh/src/hxt_tetDelaunay.c>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/README.txt>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/CREDITS.txt>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/CHANGELOG.txt>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/README.md>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/LICENSE.txt>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/CMakeLists.txt>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/core/CMakeLists.txt>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/core/include/hxt_omp.h>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/core/include/hxt_mesh.h>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/tetMesh/CMakeLists.txt>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/tetMesh/include/hxt_tetDelaunay.h>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/tetMesh/include/hxt_vertices.h>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/tetMesh/src/hxt_tetDelaunay.c>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/tetMesh/src/hxt_vertices.c>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/tetMesh/exe/Delaunay_CLI.c>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/tetBR/CMakeLists.txt>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/tetBR/src/hxt_boundary_recovery.cxx>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/contrib/hxt/tetBR/src/tetgenBR.h>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/src/mesh/tetgenBR.h>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/src/mesh/meshGRegionHxt.cpp>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/src/common/gmsh.cpp>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/api/gmsh.h>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/doc/texinfo/gmsh.texi>
  - <https://raw.githubusercontent.com/live-clones/gmsh/HEAD/doc/texinfo/opt_mesh.texi>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/live-clones/gmsh`) · [data/wave8/enrich/raw/github_com_live_clones_gmsh.json](../../../data/wave8/enrich/raw/github_com_live_clones_gmsh.json) (enrichment confidence 0.75)

</details>
