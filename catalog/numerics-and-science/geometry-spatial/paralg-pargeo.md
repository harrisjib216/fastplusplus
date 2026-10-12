# ParGeo (parallel 3D convex hull and kd-tree library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Multicore C++17 computational-geometry library (3D convex hull, kd-tree, spatial graphs) that outruns sequential CGAL and Qhull hulls through parallelism.

| | |
|---|---|
| **Beats** | CGAL (3D convex hull) and Qhull |
| **Claimed result** | From a search-result snippet of the ESA 2022 paper (paper not opened): fastest ParGeo convex hull up to 44.7x self-relative parallel speedup and up to 559x speedup against the best existing sequential implementation; Pseudohull up to 43.7x parallel speedup compared to Qhull and up to 5.05x over CGAL on 3-dimensional shapes. Exact paper wording and the per-dataset table were not verified. |
| **Workload** | Wall-clock time to compute 3D convex hulls of synthetic and scanned point sets on 36 cores with two-way hyper-threading, ParGeo Pseudohull / divide-and-conquer versus Qhull and CGAL (the repo's own benchmark/hull3d_bench.cpp uses 10M-point in-sphere, on-sphere, in-cube and on-cube sets plus scanned models such as Armadillo, Dragon, Buddha, Thai Statue, Lucy, but only runs ParGeo's own variants). |
| **Metric** | throughput |
| **Hardware** | 36 cores with two-way hyper-threading (72 threads; repo benchmark sets maxThreads = 72); CPU model not seen because the paper was unreachable. |
| **Compiler and flags** | Repo CMakeLists.txt: C++17, -DHOMEGROWN -pthread -mcx16 -O3 -DNDEBUG -fPIC (parlaylib homegrown scheduler); compiler name and version not stated in the repo, and the paper's setup was not readable. |
| **Adoption** | 54 stars; ESA 2022 paper (LIPIcs, per search results) and PPoPP 2022 poster |
| **Last commit** | 2022-09-12 |
| **Links** | [repository](https://github.com/ParAlg/ParGeo) · [benchmark](https://arxiv.org/pdf/2207.01834) |

## Verdict

Not reproduced, and the paper was not opened (arxiv.org, cs.ucr.edu, par.nsf.gov, dspace.mit.edu blocked). Search-result snippets of the ESA 2022 paper say the fastest parallel hulls on 36 cores with two-way hyper-threading are 10.5-124x (61.4x on average) faster than CGAL and 5.68-43.8x (19.9x on average) faster than Qhull for 3D hulls, while another snippet says pseudohull reaches up to 43.7x over Qhull and up to 5.05x over CGAL; the two statements conflict, and CPU model, compiler and CGAL/Qhull versions are unknown.

## Use it when

- 3D convex hulls of millions of float or double points on a many-core machine (the paper used 36 cores with two-way hyper-threading), where single-threaded CGAL or Qhull is the bottleneck.
- Batch k-NN or radius/box range queries over a static 2D-7D point set, where a parallel kd-tree build plus data-parallel queries fit the workload.
- Building spatial graphs in parallel: k-NN graph, 2D Delaunay graph, beta-skeleton/Gabriel graph, WSPD-based t-spanner, Euclidean MST.
- Research or prototyping that wants several parallel geometry primitives (enclosing ball, closest pair, Morton sort) on one scheduler.

## Skip it when

- Inputs needing robust hulls: visibility tests compare against a fixed absolute epsilon of 1e-5 in float/double (pargeo point eps, pseudohull numericKnob); there are no exact predicates in the code read, so very small, very large or degenerate (coplanar, duplicate) coordinates are risky, and the README says nothing about robustness.
- Few cores or single-threaded builds: the claimed gains come from parallelism, and the repo's own benchmark compares only ParGeo's serial quickhull against its pseudohull, not CGAL or Qhull.
- Hulls above 3D, or callers who need a half-edge/polyhedron mesh: hulls are 2D and 3D only, and the 3D result is a flat list of triangle facets (vertex coordinates).
- Production code that needs maintenance: last commit 2022-09-12; the only issue (#1, January 2024, clang rejects a redefined default template argument in src/dataset/seedSpreader.cpp) is still open.
- Dynamic kd-tree workloads where a maintained alternative exists (see Pkd-tree under siblings).

## How it is fast

All modules run on parlaylib's work-stealing fork-join scheduler. The 3D pseudohull first prunes interior points in parallel: it builds an extreme-point simplex, partitions points by the facet they see (split_k), recurses on each facet's points in parallel, then runs a parallel quickhull on the survivors; per search snippets of the paper, its parallel hull uses a reservation technique so several facets can be inserted into the hull concurrently. The divide-and-conquer hull splits the input into one block per processor, hulls each block with sequential quickhull, and hulls the union of block-hull vertices. The kd-tree splits in parallel during construction and runs queries data-parallel.

## Compared with alternatives

Pick ParGeo over DGtal QuickHull (sequential, about 2x CGAL convex_hull_3) when you have many cores and very large 3D point sets and can accept epsilon-based float predicates; prefer DGtal for single-threaded or integer-lattice work. For parallel kd-trees, the Pkd-tree from the same research lineage (ucrparlay) is newer and benchmarks against the CGAL kd-tree and Boost R-tree directly, so use ParGeo's kd-tree mainly when you also want its WSPD, EMST or spatial-graph routines.

## Integration

| | |
|---|---|
| **Form** | static lib (each hull module builds its own CMake library, e.g. pseudoHull3dLib) plus header-only parts (kd-tree, point types) |
| **Dependencies** | parlaylib (ParAlg fork, pargeo branch, git submodule); batch-dynamic-kdtree submodule; Google Benchmark and Google Test for benchmarks/tests; pthreads |
| **Minimum toolchain** | C++17, CMake 3.10; GCC-style flags; clang fails to build seedSpreader.cpp without the one-line fix in issue #1 |
| **Platforms** | x86-64 as configured (CMakeLists hard-codes -mcx16 for 16-byte compare-and-swap); other architectures not documented |
| **Thread safety** | not documented; parallelism uses parlaylib's global scheduler, whose thread count comes from the PARLAY_NUM_THREADS environment variable (default std::thread::hardware_concurrency) |
| **Drop-in for the baseline** | no |

## Gotchas

- The root CMakeLists.txt overwrites CMAKE_CXX_FLAGS with set(...) (-DHOMEGROWN -pthread -mcx16 -O3 -DNDEBUG -fPIC), so flags you pass on the command line are discarded unless you edit it; USE_PARALLEL=OFF switches to -DPARLAY_SEQUENTIAL.
- pseudo::compute is explicitly instantiated only for fpoint&lt;3&gt; and point&lt;3&gt;; other point types will not link without adding instantiations.
- By construction the pseudohull filter only discards interior points, so inputs with most points on the hull (the repo's onSphere set) get little benefit from the pruning step.
- The README's Multi-core Parallelism section is empty; thread control is only through parlaylib.

## Known shortcomings

- Tier C: the CGAL/Qhull speedups come from arXiv 2207.01834 and a PPoPP poster, both blocked here and unverified; benchmark/hull3d_bench.cpp times only ParGeo's own serial quickhull versus pseudohull. Last commit 2022-09-12, abandoned. Paper-access retier candidate (possible B).
- Search snippets conflict on the paper's numbers (one says 10.5-124x, 61.4x average, over CGAL and 5.68-43.8x, 19.9x average, over Qhull on 36 cores; another says up to 5.05x over CGAL); the paper is still unopened. The hull visibility test uses a fixed absolute epsilon of 1e-5 (float and double) with no exact predicates. CMakeLists overwrites CMAKE_CXX_FLAGS and hard-codes -mcx16; the Clang build fails (issue #1, open since 2024-01). Pseudohull is instantiated only for fpoint&lt;3&gt;/point&lt;3&gt;.

## Caveats and trade-offs

Numbers are from a search-result snippet only: arxiv.org, drops.dagstuhl.de, par.nsf.gov, www.cs.ucr.edu and www.cs.umd.edu were all EGRESS_BLOCKED (www.cs.ucr.edu re-checked by the verifier), so benchmark_url was NOT opened and the CPU model, compiler, baseline versions and point types are unknown. Tier is C under the cloud-harness rule for snippet-only evidence; a peer-reviewed ESA 2022 paper exists (B candidate, A if the paper or artifact states compiler, flags and CPU), so re-tier when paper access is available. The repo itself carries no CGAL or Qhull comparison: benchmark/hull3d_bench.cpp times only serialQuick_\* versus pseudo_\* on 10M synthetic sets and scanned models, with maxThreads = 72. Root CMakeLists.txt sets -DHOMEGROWN -pthread -mcx16 -O3 -DNDEBUG -fPIC (parlaylib scheduler). The README cites only the PPoPP 2022 poster and the GeoGraph paper, while the lead named ESA 2022; the ESA title match came from the search snippet. Parallel versus sequential baselines means unequal core counts; the 559x figure is against 'best existing sequential implementation', not CGAL. The original repo wangyiqiu/pargeo (12 stars) now points to ParAlg/ParGeo. Last commit 2022-09-12 (over 4 years, not archived).

Needs a multicore machine to win: the headline speedups come from parallelism, not from a faster sequential algorithm. Depends on the parlaylib git submodule and Google Benchmark/Google Test. Point dimension is a template parameter (2 to 7 supported for most modules); convex hull is 2D and 3D only. The README does not discuss numerical robustness or degenerate inputs, and the repo benchmark uses float points.

## Maintenance

Abandoned since 2022-09-12 (one open build issue from 2024) but MIT-licensed; modules are small enough to vendor together with the parlaylib fork, and the ESA 2022 paper documents the algorithms.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** benchmark_url (arXiv 2207.01834) is on a host the cloud harness marks EGRESS_BLOCKED and was not opened, and the README-cited PPoPP poster (www.cs.ucr.edu) returned EGRESS_BLOCKED; the repo's benchmark/hull3d_bench.cpp only times ParGeo's own serial quickhull versus pseudohull, so the CGAL/Qhull numbers remain snippet-only and stay C.
- **Verifier notes:** Repo metadata verified on github.com (MIT, 54 stars, 13 forks, not archived, not a fork, last commit 2022-09-12 'Fix compilation', so abandoned). The paper could not be opened, so the CGAL/Qhull speedups are unverified; queue for a paper-access retier (possible B).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/ParAlg/ParGeo>
  - <https://github.com/ParAlg/ParGeo/commits/main>
  - <https://github.com/ParAlg/ParGeo/tree/main/benchmark>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/README.md>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/benchmark/hull3d_bench.cpp>
  - <https://github.com/wangyiqiu?tab=repositories>
  - <https://github.com/wangyiqiu/pargeo>
- **Sources the enricher read:**
  - <https://github.com/ParAlg/ParGeo>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/README.md>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/benchmark/hull3d_bench.cpp>
  - <https://github.com/ParAlg/ParGeo/tree/main/include>
  - <https://github.com/ParAlg/ParGeo/tree/main/include/convexHull3d>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/include/convexHull3d/pseudo/hull.h>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/include/convexHull3d/divideConquer/hull.h>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/include/convexHull3d/parallelQuickHull/hull.h>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/include/convexHull3d/hullTopology.h>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/include/kdTree/kdTree.h>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/include/pargeo/point.h>
  - <https://github.com/ParAlg/ParGeo/tree/main/src/convexHull3d>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/src/convexHull3d/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/src/convexHull3d/plot.py>
  - <https://github.com/ParAlg/ParGeo/tree/main/src/convexHull3d/pseudoHull>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/src/convexHull3d/pseudoHull/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/src/convexHull3d/pseudoHull/hull.cpp>
  - <https://raw.githubusercontent.com/ParAlg/ParGeo/HEAD/example/convexHull.cpp>
  - <https://raw.githubusercontent.com/ParAlg/parlaylib/pargeo/include/parlay/scheduler.h>
  - <https://github.com/ParAlg/ParGeo/issues?q=is%3Aissue>
  - <https://github.com/ParAlg/ParGeo/issues/1>
  - <https://github.com/yushangdi/yushangdi.github.io>
  - <https://github.com/yushangdi/yushangdi.github.io/tree/master/files>
  - https://www.cs.ucr.edu/\~ygu/papers/ESA22/ParGeo.pdf (EGRESS_BLOCKED)
  - https://dspace.mit.edu/bitstream/handle/1721.1/151320/wang-yiqiuw-phd-eecs-2023-thesis.pdf (blocked by proxy)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/paralg/pargeo`) · [data/wave8/enrich/raw/github_com_paralg_pargeo.json](../../../data/wave8/enrich/raw/github_com_paralg_pargeo.json) (enrichment confidence 0.55)

</details>
