# ArborX

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Kokkos linear BVH for batched kNN/radius search on CPUs and GPUs; single-threaded kNN beats Boost R-tree at 10^7 points.

| | |
|---|---|
| **Beats** | Boost.Geometry.Index R-tree (packing/bulk-load algorithm, Boost 1.67.0) and nanoflann kd-tree (hash 3b2065e) |
| **Claimed result** | Figures 5 and 6 plot speedup relative to nanoflann (bars read by eye, single thread). Filled case: construction ArborX about 0.85x-1.37x vs Boost about 0.87x-1.32x (similar); nearest search ArborX about 0.58x-0.78x at 10^4-10^6 and about 1.48x at 10^7, Boost about 0.55x-0.93x, so ArborX is about 1.6x faster than Boost at 10^7 (derived from page data). Hollow case: nearest search ArborX about 0.95x, 1.75x, 2.0x, 2.6x at 10^4-10^7 vs Boost about 0.62x-1.22x, so about 2.1x over Boost at 10^7 (derived from page data); construction ArborX about 0.87x-1.12x vs Boost about 1.02x-1.40x, i.e. Boost builds faster in the hollow case. Paper text: 'ArborX and Boost.Geometry.Index libraries perform similarly' for construction; for nearest search 'ArborX significantly outperforms both Boost.Geometry.Index and nanoflann libraries for larger numbers of objects, particularly for the hollow case.' |
| **Workload** | Section 3.2 of the ACM TOMS 2020 paper: single-threaded tree construction, k=10 nearest search and radius (spatial) search with m = n source/target points from 10^4 to 10^7, for a filled case (filled sphere queries in a filled cube) and a hollow case (hollow sphere in hollow cube), ArborX BVH vs Boost.Geometry.Index packing R-tree and nanoflann; Google Benchmark median, run on one core of a CADES node. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2695 v4 (18 cores, 2.1 GHz; CADES node, one thread used for the library comparison); scaling runs on OLCF Summit (2x IBM POWER9, NVIDIA V100) |
| **Adoption** | 242 stars; Trilinos/Kokkos ecosystem library; ACM TOMS papers (2020 and 2025 v2.0) |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/arborx/ArborX) · [benchmark](https://raw.githubusercontent.com/dalg24/dalg24.github.io/HEAD/files/2020-paper-toms-arborx.pdf) |

## Verdict

The ACM TOMS 2020 paper ran single-threaded Google Benchmark medians on one core of an Intel Xeon E5-2695 v4 (2.1 GHz, CADES) for m = n from 10^4 to 10^7 points, comparing ArborX against Boost.Geometry.Index 1.67.0 (packed R-tree) and nanoflann 3b2065e. Its bar charts (relative to nanoflann) show similar construction times and k=10 nearest search about 1.6x (filled) and 2.1x (hollow) faster than Boost at 10^7 points, but slower than nanoflann below 10^6 in the filled case (bars read by eye, derived from page data). The paper states no compiler, flags or Kokkos version. The repo's bvh_driver still has a Boost R-tree backend (linear&lt;16&gt;, bulk-loaded) but no nanoflann backend.

## Use it when

- Batched neighbour search over 10^6-10^7+ points where all queries are known up front (particle neighbour lists, contact detection, mesh-to-mesh data transfer). In the paper's single-thread runs, kNN (k=10) at 10^7 points was about 1.6x (filled) and 2.1x (hollow) faster than Boost's packed R-tree (bars read by the verifier, derived from page data)
- Codes already on Kokkos (Trilinos, exascale applications) that need one search code path for OpenMP, CUDA, HIP and SYCL. The paper found one V100 beat a full two-socket POWER9 node except on small problems
- Multicore CPU batches: OpenMP strong scaling at n=10^7 (filled case, Table 1) reached 10.5x for construction, 12.2x for spatial search and 12.1x for nearest search on 16 threads
- Search over non-point primitives (boxes, triangles, segments, spheres, tetrahedra, rays) in arbitrary dimension, or distributed-memory search through DistributedTree with MPI

## Skip it when

- Small or medium single-threaded problems: in the filled case the paper shows ArborX slower than nanoflann for nearest search from 10^4 to 10^6 points (about 0.58-0.78x of nanoflann). Thread scaling is also poor below roughly 1000 objects per thread, because the Morton sort is the bottleneck (paper section 3.3)
- Data that changes by a few inserts or deletes at a time: there is no incremental update API, so every change means rebuilding the tree
- Projects that cannot take on Kokkos 4.5+, C++20 and CMake 3.22. ArborX is header-only, but Kokkos must be built and configured for your backend
- Construction-dominated workloads on surface-like (hollow) data: Boost's packed R-tree built faster in the paper's hollow case (about 1.02-1.40x of nanoflann vs 0.87-1.12x for ArborX)
- One-off queries from host code in a hot loop: each batched query() call sorts the predicates and launches Kokkos kernels, so the fixed cost per call is high. The PerThread overload helps only inside your own kernel

## How it is fast

Construction is a linear BVH: object boxes are reduced to a scene box, centroids are mapped to 64-bit Morton codes (the curve is pluggable), sorted, and the hierarchy plus internal boxes are built in one parallel bottom-up pass using Apetrei's agglomerative variant of Karras's 2012 LBVH (one atomic compare-exchange per internal node). The 2020 paper used plain Karras; the current source uses Apetrei. Spatial queries walk the tree stacklessly through 'ropes' (skip links stored at build time), and nearest queries use a short stack that visits the closer child first (after Patwary et al.) and a k-sized max-heap in a preallocated per-query buffer that shrinks the search radius once k hits are found. Queries are pre-sorted by Morton code so neighbouring threads traverse similar nodes, and spatial results use a count-then-fill two-pass scheme or a one-pass scheme when the caller supplies a per-query buffer size.

## Compared with alternatives

Pick ArborX over nanoflann or the single-threaded tree siblings (THST, PH-tree, tidwall rtree.c) when you need GPU or multithreaded batched queries, non-point geometry, or kNN at 10^7 scale. nanoflann is lighter (header-only, no Kokkos) and faster single-threaded up to about 10^6 points. Pick Pkd-tree instead when the point set changes through large parallel batch inserts and deletes on a CPU.

## Integration

| | |
|---|---|
| **Form** | header-only (CMake INTERFACE target; configuring generates ArborX_Config.hpp and a version header, so install through CMake rather than copying src/) |
| **Dependencies** | Kokkos 4.5+ (required). Optional: MPI (DistributedTree), rocThrust (HIP, on by default), oneDPL (SYCL), Trilinos 16+. Tests and benchmarks only: Boost 1.67+ and Google Benchmark 1.5.4+ (auto-fetched) |
| **Minimum toolchain** | C++20, CMake 3.22, Kokkos 4.5.00; compiler minimums follow Kokkos, and NVCC must be 11.5+ |
| **Platforms** | any Kokkos backend: Serial, OpenMP, Threads, CUDA, HIP, SYCL. Test failures were reported on aarch64/ppc64le (issue #1196 hang, closed; issue #1241, stack smashing and wrong neighbour lists in v2.0 tests on aarch64) |
| **Thread safety** | query() is const and parallelizes the batch itself over the given execution space. A PerThread overload is callable from inside user kernels. Concurrent query() calls from several host threads are not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Spatial queries default to two traversals (count, then fill). TraversalPolicy::setBufferSize(n) enables one pass: a positive n falls back to two passes when exceeded, a negative n throws. An oversized estimate costs memory; the paper could not run the one-pass variant above 10^6 points in the hollow case
- Predicates are Morton-sorted before traversal by default. The paper found this hurt serial hollow-case spatial search at 10^7 points; turn it off with TraversalPolicy::setPredicateSorting(false)
- Nearest traversal keeps a fixed 64-entry stack with no bounds check (ArborX_TreeTraversal.hpp). Trees deeper than that, possible in principle with extreme clustering or duplicate Morton codes, are not guarded. This comes from reading the source; I found no issue reporting it
- API churn: v2.0 (2025-04-16) removed the APIv1 index interfaces and moved to C++20 and Kokkos 4.5. Several geometries and helpers (Segment, Ellipsoid, MST, attach_indices, DefaultIndexableGetter) still sit in the Experimental namespace. Within one query, the order of spatial results is unspecified

## Known shortcomings

- Modest win: \~1.6-2.1x over Boost only for nearest search at 10^7; Boost builds faster in the hollow case; single thread on Xeon E5-2695 v4 with no compiler/flags.
- Wins are single-thread kNN at 10^7 only; slower than nanoflann at &lt;=10^6. Nearest traversal uses a fixed 64-entry stack with no bounds check (source reading, no issue filed). aarch64 test failures (#1241).

## Caveats and trade-offs

Wins are single-threaded and modest: construction is on par with Boost (Boost is faster in the hollow case), ArborX is slower than nanoflann for nearest search in the filled case up to 10^6 points, and the clear win (about 1.6x-2.1x over Boost, derived from bars read by eye) appears only for nearest search at 10^7 points; spatial search in the hollow case at 10^6-10^7 favors Boost over ArborX's 2P variant. Numbers are bar charts with no table. The paper states no compiler, flags or Kokkos version; Boost 1.67.0 and nanoflann 3b2065e are from 2018-2019. The repo's bvh_driver keeps a Boost R-tree backend but no nanoflann backend. ArborX's main value is multithreaded and GPU search (Kokkos), which Boost and nanoflann do not offer.

Kokkos-based performance-portable C++ library (CPU threads plus CUDA/HIP/SYCL GPU backends) with optional distributed trees; the BVH is built for static or batch-rebuilt data rather than being a dynamic insert/delete R-tree; heavier build dependency than a header-only R-tree.

## Maintenance

Actively developed by an ORNL-led team (v2.1.0 on 2026-04-28, last commit 2026-09-16, a second TOMS paper for v2.0 in 2025) under BSD-3-Clause; easy to vendor as headers, but practical only if you can adopt Kokkos.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed ACM TOMS 47(1) 2020 paper (author copy opened) compares ArborX single-threaded against Boost.Geometry.Index 1.67.0 (packing R-tree) and nanoflann 3b2065e on a named CPU (Xeon E5-2695 v4), and the repo holds a Boost R-tree benchmark backend (benchmarks/bvh_driver/bvh_driver.cpp, backend 'rtree'); the paper states no compiler or flags, so it is not A.
- **Verifier notes:** Paper read from the first author's GitHub Pages repo via raw.githubusercontent.com (arxiv.org, deepai.org and pith.science are blocked). Metadata confirmed on github.com: BSD-3-Clause, 242 stars, 47 forks, not fork/archived, last commit 2026-09-16.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `workload`, `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dalg24/dalg24.github.io/HEAD/files/2020-paper-toms-arborx.pdf>
  - <https://github.com/arborx/ArborX>
  - <https://github.com/arborx/ArborX/commits>
  - <https://github.com/arborx/ArborX/wiki>
  - <https://github.com/arborx/ArborX/tree/master/benchmarks/bvh_driver>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/benchmarks/bvh_driver/bvh_driver.cpp>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/benchmarks/bvh_driver/benchmark_registration.hpp>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/benchmarks/bvh_driver/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dalg24/dalg24.github.io/HEAD/files/2020-paper-toms-arborx.pdf>
  - <https://github.com/arborx/ArborX>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/README.md>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/CITATION.bib>
  - <https://github.com/arborx/ArborX/wiki/Build>
  - <https://github.com/arborx/ArborX/wiki/ArborX%3A%3ABoundingVolumeHierarchy>
  - <https://github.com/arborx/ArborX/releases>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/src/ArborX.hpp>
  - <https://github.com/arborx/ArborX/tree/master/src/spatial>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/src/spatial/ArborX_LinearBVH.hpp>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/src/spatial/detail/ArborX_TreeConstruction.hpp>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/src/spatial/detail/ArborX_TreeTraversal.hpp>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/src/spatial/detail/ArborX_TraversalPolicy.hpp>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/examples/simple_intersection/example_intersection.cpp>
  - <https://github.com/arborx/ArborX/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/benchmarks/bvh_driver/bvh_driver.cpp>
  - <https://raw.githubusercontent.com/arborx/ArborX/HEAD/test/ArborX_BoostRTreeHelpers.hpp>
  - <https://github.com/arborx/ArborX/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/arborx/ArborX/issues?q=stack>
  - <https://github.com/arborx/ArborX/issues/1241>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/arborx/arborx`) · [data/wave8/enrich/raw/github_com_arborx_arborx.json](../../../data/wave8/enrich/raw/github_com_arborx_arborx.json) (enrichment confidence 0.8)

</details>
