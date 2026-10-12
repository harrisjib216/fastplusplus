# geogram (ParallelDelaunay3d)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> BSD-licensed C++ geometry library whose multithreaded 3D Delaunay/regular triangulation (PDEL) outruns CGAL on large point sets.

| | |
|---|---|
| **Beats** | CGAL 3D Delaunay / regular triangulation, single-threaded and CGAL Parallel; the paper also has SciPy, Voro++, HXT (Gmsh) and gDel3D (GPU) columns |
| **Claimed result** | Snippet only (paper not opened). Clustered weighted point sets, Geogram on 16 cores versus single-threaded CGAL: 100k points 0.060 s vs 0.449 s (about 7.5x, derived); 500k 0.250 vs 2.299 (about 9.2x); 1M 0.413 vs 4.808 (about 11.6x); 15M 5.890 vs 74.723 (about 12.7x), but these ratios compare 16 threads with one thread. Against CGAL Parallel on the same 16 cores the gap is far smaller: white noise 15M points, Geogram 6.138 s vs CGAL Parallel 6.903 s (about 1.12x, derived from snippet data); clustered 100k points, Geogram 0.060 s vs CGAL Parallel 0.533 s. HXT (Gmsh) beats Geogram at scale: 2.259 s at 15M points, white noise (Geogram about 2.7x slower, derived from snippet data); the paper calls HXT the best CPU baseline, closely followed by Geogram. |
| **Workload** | Runtime of 3D Voronoi / Delaunay construction on synthetic white-noise and density-gradient point sets and of power-diagram (weighted, regular triangulation) construction on clustered point sets, 0.1M to 15M points, plus real-world neural-rendering point sets, in a third-party SIGGRAPH 2026 GPU Voronoi paper (Taveira, Lindstrom, Fatemi, Hammarstrand, Kahl) that uses SciPy, CGAL, CGAL Parallel, Geogram, Voro++ and HXT as CPU baselines on 16 cores. |
| **Metric** | throughput |
| **Hardware** | CPU methods on 16 cores of an AMD EPYC 9534 (WebSearch snippet only; GPU not captured) |
| **Adoption** | 2.6k stars; Symposium on Geometry Processing Software Award 2023 |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/BrunoLevy/geogram) · [benchmark](https://arxiv.org/pdf/2605.06408) |

## Verdict

Third-party SIGGRAPH 2026 paper (Taveira et al., arXiv 2605.06408), seen only as search snippets: CPU baselines ran on 16 cores of an AMD EPYC 9534 with compiler, flags and library versions unknown. On clustered weighted point sets (power diagrams), 16-thread Geogram ran 7.5x to 12.7x faster than single-threaded CGAL from 100k to 15M points; on the same 16 cores it was about 1.12x faster than CGAL Parallel at 15M white-noise points (6.138 s vs 6.903 s) and about 2.7x slower than HXT (2.259 s). A separate third-party wrapper, GeoDel, measured Geogram single-threaded at 5.27 s vs 58.0 s for SciPy/Qhull on 1M uniform points (best of three, hardware unstated).

## Use it when

- 3D Delaunay tetrahedralization of 1M to tens of millions of points on a multicore CPU, when a BSD-3-Clause library fits your licensing better than CGAL or Gmsh's HXT.
- Power or Laguerre diagrams (weighted points), for example semi-discrete optimal transport or particle methods; the third-party paper's clustered weighted sets ran 7.5x to 12.7x faster than single-threaded CGAL, and 0.060 s vs 0.533 s against CGAL Parallel at 100k points (snippet data).
- Periodic Voronoi or Delaunay diagrams in a box, through the related PeriodicDelaunay3d class.
- Memory-bound runs: the FAQ claims point sets of hundreds of millions, and the third-party GeoDel wrapper measured 308 MB peak RSS for 1M points vs 2,371 MB for SciPy/Qhull (see the 32-bit index caveat).
- Embedding just the triangulator: the Delaunay_psm.h/.cpp amalgamation (about 36,000 lines per GeoDel's README) drops into another build without the rest of Geogram.

## Skip it when

- Raw CPU speed on very large uniform point sets: in the SIGGRAPH 2026 comparison HXT (Gmsh) took 2.259 s at 15M white-noise points, about 2.7x faster than Geogram, and against CGAL Parallel on the same 16 cores Geogram was only about 1.12x faster (6.138 s vs 6.903 s, snippet data).
- Dynamic triangulations: no vertex removal (the FAQ says CGAL has it and Geogram does not), and public incremental insert_vertex() is still an open request (issue #255).
- Degenerate input: the class comment says it does not support input where all points are coplanar or collinear and recommends CGAL for that; duplicate points are silently skipped and left as isolated vertices.
- Constrained or quality-meshing tetrahedralization: PDEL is unconstrained; Geogram delegates constrained meshing to its bundled TetGen.
- A small header-only dependency: the full library is a CMake-built C++17 project with graphics, Lua and legacy-numerics options on by default; use the PSM amalgamation or GEOGRAM_LIB_ONLY to trim it.

## How it is fast

Points are first sorted in BRIO order (Amenta-Choi-Rote biased randomized insertion with Hilbert-style spatial sorting via std::nth_element), then inserted with the Bowyer-Watson cavity algorithm, traversing the cavity from inside as CGAL does. The first BRIO levels (about 1,000 points) are inserted sequentially; each later level is split into one contiguous chunk per thread, and threads claim tetrahedra with compare-and-swap on a one-byte per-tetrahedron ownership array, rolling back and retrying (or inserting from the other end of their chunk) when they collide with another thread. Memory is preallocated at 7 tetrahedra per point and split into per-thread pools, and points that overflow a pool are inserted sequentially at the end. Point location uses an inexact walk followed by the exact one (structural filtering), with filtered floating-point predicates that fall back to exact expansion arithmetic.

## Compared with alternatives

Pick Geogram over HXT (which ships inside Gmsh) when you want a standalone BSD-3-Clause library with power or periodic diagrams and Voronoi cell extraction and can accept being about 2.7x slower at 15M uniform points, and over gDel3D when there is no NVIDIA GPU or the input is clustered rather than uniform. For 2D, the Delaunay32, detria or pgl entries fit better.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake); the Delaunay module is also available as a single-file source drop (Delaunay_psm.h/.cpp) |
| **Dependencies** | none required for Delaunay; optional TBB (GEOGRAM_WITH_TBB, off by default); the bundled TetGen and Triangle are built by default (GEOGRAM_WITH_TETGEN and GEOGRAM_WITH_TRIANGLE ON), and their licences are separate from Geogram's BSD-3-Clause, so check them or turn the options off |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17), CMake 3.5 or newer; exact predicates need -ffp-contract=off (and, per GeoDel, -frounding-math) |
| **Platforms** | Linux, Windows, macOS, Android, Emscripten per the FAQ; x86-64 and aarch64; up to 126 threads by default (one-byte cell-status array), more only with GEO_CONNECTION_MACHINE |
| **Thread safety** | One ParallelDelaunay3d instance spawns its own worker threads (Process::maximum_concurrent_threads(), capped at 126); separate instances on separate threads are the supported pattern (issue #297 fixed this for Delaunay2d), and concurrent neighbour queries need set_thread_safe(true). Otherwise not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Build flags are part of correctness: the exact predicates break if the compiler fuses multiply-adds. Geogram's Linux gcc config adds -ffp-contract=off, but clang configs for aarch64 (Android, Darwin/Apple Silicon) and Linux clang lacked it until fixes in 2026 (issues #358 and #382): locate_inexact() looped or hit its 2,500-step guard, and a 9 s tetrahedralization took 30 s to over 13 minutes, nondeterministically. Vendoring the sources into your own build means copying these flags.
- Issue #367 (July 2026): PDEL hit an out-of-range vertex index in the parallel locate_inexact() walk (19,202 points, 32 threads, keeps_infinite, v1.9.x and v1.10.0). It was fixed by PR #368 ('fix locate_inexact() reading deleted-tet vertex slot') in v1.10.1, so the SIGGRAPH 2026 paper's Geogram runs (arXiv May 2026) predate the fix. It is a rare-case robustness fix, and nothing shows that it changes timings.
- With the default 32-bit index_t, set_vertices() computes the tetrahedron pool size as nb_vertices \* 7 \* 4 in index_t, which wraps above about 153M points (2^32 / 28, derived from source), and no guard was found in set_vertices. Build with GEOGRAM_WITH_GARGANTUA (64-bit indices) before relying on the FAQ's hundreds-of-millions claim.
- Delaunay::create() does not fail loudly in normal builds: if the name is not registered (for example GEO::initialize() was not called), it logs a warning and returns a Delaunay_NearestNeighbors object, which has no tetrahedra. set_vertices() keeps a pointer to your coordinate array rather than copying it, so the array must outlive the triangulation. Weights for dimension 4 are passed as a fourth coordinate sqrt(W - w_i), not as weights.

## Known shortcomings

- Tier C, snippet only: the SIGGRAPH 2026 paper (arXiv 2605.06408) and its mirrors are blocked. The 12.7x compares 16-core EPYC 9534 Geogram with single-thread CGAL; against CGAL's parallel Delaunay the lead is about 1.12x (15M points: 6.138 vs 6.903 s); HXT (Gmsh, already listed) is about 2.7x faster than Geogram; the clustered table measures weighted power diagrams. CGAL is the incumbent baseline. Tier B possible if the paper becomes reachable.
- Enricher (paper still snippet-only): #367 out-of-range vertex in the parallel locate_inexact walk (v1.9.x, v1.10.0) was fixed by PR #368 in v1.10.1 after the paper's May 2026 runs (rare-case robustness fix, no timing effect shown); #358/#382: clang and aarch64 configs lacked -ffp-contract=off so FMA broke the predicates (a 9 s run became 30 s to 13+ minutes; the paper ran on x86 EPYC, flags unknown). Default 32-bit index_t: the set_vertices pool size nb_vertices\*7\*4 wraps above about 153M points with no guard found (derived from source), so the FAQ's 'hundred millions points' needs GEOGRAM_WITH_GARGANTUA; Delaunay::create falls back to NN mode with only a warning; duplicate points skipped silently; no coplanar input, no vertex removal. Extra evidence: GeoDel (anttwo/geodel, Python wrapper) single-thread 1M uniform points 5.27 s vs SciPy/Qhull 58.0 s, hardware unstated.

## Caveats and trade-offs

Snippet only: arxiv.org, research.chalmers.se (full-text PDF), research.zenseact.com (project page), emergentmind.com and themoonlight.io are blocked in this environment, so the paper (Taveira, Lindstrom, Fatemi, Hammarstrand, Kahl, 'Scalable GPU Construction of 3D Voronoi and Power Diagrams', SIGGRAPH 2026, arXiv 2605.06408, ACM DOI 10.1145/3799902.3811229) was not opened; the numbers come from WebSearch result text summarising its tables. CPU baselines ran on 16 cores of an AMD EPYC 9534 (snippet); compiler, flags, thread settings, Geogram and CGAL versions are unknown. The headline 7.5-12.7x compares 16-thread Geogram with single-threaded CGAL; against CGAL Parallel on the same cores Geogram is only about 1.12x faster at 15M white-noise points (6.138 s vs 6.903 s). The clustered table is power-diagram (weighted) construction, not plain Delaunay. Geogram is not the fastest CPU code in the comparison: HXT (Gmsh, already listed) took 2.259 s at 15M points, and the HXT paper reports a serial kernel about 3x faster than Geogram. The paper's purpose is a GPU method, with Geogram and CGAL as baselines. Geogram's own README and wiki pages carry no numbers.

Geogram's ParallelDelaunay3d uses floating-point predicates with exact-arithmetic fallback (expansion_nt/PCK) and is multithreaded; it is a general geometry-processing toolkit with its own mesh data structures rather than CGAL's generic kernel framework. Input points may be perturbed or duplicated points handled differently from CGAL (not checked).

## Maintenance

Actively maintained (commits through 2026-10-06; v1.10.1 carried the PDEL locate fix) and BSD-3-Clause, with a 2023 SGP Software Award; copyable, most easily through the Delaunay PSM amalgamation, provided you keep the -ffp-contract=off build flag.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The source is a third-party peer-reviewed paper (SIGGRAPH 2026, arXiv 2605.06408, ACM DOI 10.1145/3799902.3811229) that would support B, but arxiv.org, research.chalmers.se, research.zenseact.com, emergentmind and themoonlight were all EGRESS_BLOCKED, so its tables were seen only as WebSearch snippets; capped at C per the snippet-only rule.
- **Verifier notes:** Every paper host and mirror tried (arxiv.org, research.chalmers.se PDF, research.zenseact.com, emergentmind, themoonlight) returned EGRESS_BLOCKED; 5 WebSearch queries confirmed the record's clustered numbers, the AMD EPYC 9534 16-core CPU setup, and same-core CGAL Parallel numbers. Claim corrected: the 12.7x is 16 threads vs 1 thread, the like-for-like gain over CGAL Parallel is about 1.12x at 15M points, and HXT (already listed) is about 2.7x faster than Geogram. baseline_in_list set true (CGAL is a geometry-spatial incumbent). Retier to B is possible if the paper PDF becomes reachable. Metadata from github.com: BSD-3-Clause, 2.6k stars, not archived, last commit 2026-10-06 (active).
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `hardware`, `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-58 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/BrunoLevy/geogram>
  - <https://github.com/BrunoLevy/geogram/commits>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/BrunoLevy/geogram>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/README.md>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/cmake/geogram.cmake>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/cmake/platforms/Linux.cmake>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/cmake/platforms/Linux-gcc.cmake>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/src/lib/geogram/CMakeLists.txt>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/src/lib/geogram/delaunay/parallel_delaunay_3d.h>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/src/lib/geogram/delaunay/parallel_delaunay_3d.cpp>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/src/lib/geogram/delaunay/delaunay.h>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/src/lib/geogram/delaunay/delaunay.cpp>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/src/lib/geogram/delaunay/delaunay_sync.h>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/src/lib/geogram/basic/numeric.h>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/src/lib/geogram/basic/common.h>
  - <https://raw.githubusercontent.com/BrunoLevy/geogram/HEAD/src/lib/geogram/api/defs.h>
  - <https://github.com/BrunoLevy/geogram/wiki/Delaunay3D>
  - <https://github.com/BrunoLevy/geogram/wiki/FAQ>
  - <https://github.com/BrunoLevy/geogram/issues?q=is%3Aissue+delaunay>
  - <https://github.com/BrunoLevy/geogram/issues/367>
  - <https://github.com/BrunoLevy/geogram/issues/358>
  - <https://github.com/BrunoLevy/geogram/issues/382>
  - <https://github.com/BrunoLevy/geogram/releases>
  - <https://github.com/BrunoLevy/geogram/releases/tag/v1.10.1>
  - <https://github.com/BrunoLevy/geogram/commits>
  - <https://github.com/anttwo/geodel>
  - <https://raw.githubusercontent.com/anttwo/geodel/HEAD/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/brunolevy/geogram`) · [data/wave1/enrich/raw/github_com_brunolevy_geogram.json](../../../data/wave1/enrich/raw/github_com_brunolevy_geogram.json) (enrichment confidence 0.6)

</details>
