# THST (Hierarchical spatial trees)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++03 R-tree and 2D quadtree that compile about 25x faster than Boost.Geometry rtree code; runtime is not faster overall.

| | |
|---|---|
| **Beats** | Boost.Geometry index (rtree) |
| **Claimed result** | 'benchmark compilation: 35,3 sec vs 1,4 sec' versus Boost (about 25x, derived from page data). Runtime charts only: per benchmark/README, Boost.Geometry bulk-loading/rstar gives the best query times, THST quadratic custom comes next; in the dynamic case THST quadratic beats bgi linear above \~400 objects. |
| **Workload** | Compile time of the benchmark program; also load/query time of 1M small boxes and 100K intersection queries (charts only). |
| **Metric** | compile-time |
| **Hardware** | Intel Core i7-4870HQ 2.50GHz, 16 GB RAM, macOS Sierra |
| **Adoption** | 133 stars |
| **Last commit** | 2024-03-16 |
| **Links** | [repository](https://github.com/tuxalin/THST) · [benchmark](https://github.com/tuxalin/THST) |

## Verdict

The author reused Loskot and Wulkiewicz's spatial_index_benchmark: 1M small random boxes inserted iteratively, 100K intersection queries with boxes 10x larger, and a 200-run dynamic clear/query/insert loop, comparing THST quadtree/quadratic/quadratic-sphere (heap and custom allocator) with Boost.Geometry rtree linear/quadratic/R\* (iterative and bulk, compile-time parameters) on an Intel Core i7-4870HQ under macOS Sierra, built as an Xcode Release (exact compiler and flags not stated). The only numeric claim is benchmark compile time, 35.3 s for Boost vs 1.4 s for THST; runtime results are PNG charts in which Boost bulk/R\* leads queries and THST quadratic wins only the dynamic case above about 400 objects.

## Use it when

- Projects where build time matters and Boost.Geometry's rtree headers dominate compile time: the README reports 1.4 s vs 35.3 s to compile the benchmark program
- Games, physics and editors that rebuild or heavily update a small index every frame: the project's dynamic benchmark shows THST quadratic ahead of bgi linear above about 400 objects
- Hierarchical scene partitioning where you want to store data on internal nodes, walk the tree level by level (dbegin/child iterators) or stop a query once a node is fully contained (hierachical_query)
- Ray casting against boxes (rayQuery with a filter predicate) without pulling in a BVH library
- Old toolchains: the core RTree/QuadTree is written for C++03 and needs no dependencies

## Skip it when

- Query-heavy static data: per the project's own charts, Boost.Geometry rtree with bulk loading or R\* gives the best query times, ahead of THST's best (quadratic with custom allocator)
- Large static datasets that you can bulk-load: THST has only one-by-one insertion, while Boost's packing algorithm loads fastest
- Fewer than about 400 objects in a rebuild-every-frame loop: bgi linear was slightly faster there in the same benchmark
- QuadTree for 1M-box workloads: the benchmark README calls quadtree queries 'really slow' and building 'very slow' for capacities 256-1024
- Code that needs active maintenance or a package: last commit March 2024, issue #23 (assertion failure in RTree::choosePartition, Oct 2023) is still open, and there is no vcpkg port (issue #26 open)

## How it is fast

The compile-time win comes from a small templated code base (Guttman's 1984 R-tree via the Greg Douglas / nushoin C++ ports) with none of Boost.Geometry's concept, variant-visitor and strategy machinery. At runtime it uses Guttman's quadratic split (pickSeeds/classify) with an optional spherical-volume measure, fixed-size nodes holding parallel arrays of values, boxes and child pointers, and a pluggable node allocator; the benchmark's fastest THST variant uses a test-only allocator that places all nodes in one pre-sized std::vector. There is no bulk loading (listed under 'Future improvements'), no R\*-tree reinsertion and no SIMD.

## Compared with alternatives

Pick THST over tidwall/rtree.c or GeoToolbox KdBoxTree when you want a templated, header-only C++ tree with hierarchical iteration, ray queries and low compile cost; pick those siblings (or nanoflann for point k-NN) when raw insert/query throughput against Boost is the goal, since THST's own benchmark does not show a runtime win over a bulk-loaded Boost rtree.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (the benchmark needs Boost headers, CMake and gnuplot; tests use doctest as a git submodule) |
| **Minimum toolchain** | C++03 for the core trees; RTree::k_nearest (priority_queue::emplace) and QuadTree::clear (nullptr) need C++11; move constructors are enabled under C++11/MSVC 2013+ |
| **Platforms** | any (portable scalar C++; benchmarked on macOS with Xcode, CMake files also handle MSVC, GCC and Clang) |
| **Thread safety** | not documented; from the source, queries are const and use only local state, while insert/remove modify a shared member scratch buffer (m_parVars), so writes need external locking |
| **Drop-in for the baseline** | partial — the query style (predicate + output iterator) and indexable getter resemble Boost.Geometry's rtree, but the template parameters, predicate names and getter signature differ, and there is no bulk loading, R\*/linear split or general nearest() predicate |

## Gotchas

- Several failure cases are checked only by assert, so release builds do not catch them: inserting a box outside a QuadTree's world box, more than 16 levels in the depth/leaf iterators' fixed stack (a write past the array), and the under-filled node split reported in open issue #23
- RTree::nearest(point, radius) is 2D only (static assert) and ranks by distance to box centre; k_nearest works in N dimensions and uses minimum distance to the box
- Node capacity and min fill are template parameters (defaults M=8, m=M/2); the benchmark sweeps M from small values up to 40x the base and results depend strongly on it
- The 'custom' allocator in the benchmark is test/custom_allocator.h, not part of include/; it must be pre-sized (nodeCount \* 1.5) and only asserts on overflow

## Known shortcomings

- Only win is compile time (35.3 s vs 1.4 s); its own benchmark README says Boost.Geometry rtree has faster queries; wins only the dynamic case above \~400 objects.
- Only win is compile time (35.3 s vs 1.4 s); Boost bulk/R\* rtree has better query times; no bulk loading; open #23 assertion failure in choosePartition (bad node split); several failure cases checked only by assert; iterators use a fixed 16-level stack; nearest() 2D only; 'C++03' claim partial (k_nearest needs C++11).

## Caveats and trade-offs

Speed claim is compile time; at runtime Boost.Geometry rtree (bulk/rstar) is faster for query per the project's own benchmark README, and THST wins only the dynamic case above \~400 objects vs bgi linear. Runtime values only in PNG charts. Compiler/flags not stated; setup copied from mloskot/spatial_index_benchmark. Old hardware and OS (macOS Sierra).

Header-only, C++03; RTree plus 2D QuadTree; hierarchical queries, ray-box queries, custom allocators.

## Maintenance

Stale (last commit 2024-03-16, a CMake install-script PR) but MIT-licensed, dependency-free and small (RTree.h is about 1,800 lines, QuadTree.h about 800), so easy to vendor; treat it as a compile-time and feature pick, not a runtime-speed pick.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README states benchmark compilation 35.3 s (Boost) vs 1.4 s (THST) and has runtime charts vs Boost.Geometry rtree from code in benchmark/ (CPU i7-4870HQ stated), but the compiler and flags are not stated (Xcode Release build implied), so C.
- **Verifier notes:** Not faster at runtime overall; keep as a compile-time win and record the runtime shortcoming. Metadata matches: MIT, 133 stars, last commit 2024-03-16 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tuxalin/THST>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/README.md>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/benchmark/README.md>
  - <https://github.com/tuxalin/THST/commits>
- **Sources the enricher read:**
  - <https://github.com/tuxalin/THST>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/README.md>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/benchmark/README.md>
  - <https://github.com/tuxalin/THST/tree/master/include/THST>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/include/THST/RTree.h>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/include/THST/rtree_detail.h>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/include/THST/QuadTree.h>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/include/THST/allocator.h>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/include/THST/config.h>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/include/THST/bbox.h>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/include/THST/predicates.h>
  - <https://github.com/tuxalin/THST/tree/master/benchmark>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/benchmark/benchmark_thst.cpp>
  - <https://raw.githubusercontent.com/tuxalin/THST/HEAD/test/custom_allocator.h>
  - <https://github.com/tuxalin/THST/issues?q=is%3Aissue>
  - <https://github.com/tuxalin/THST/issues/23>
  - <https://github.com/tuxalin/THST/issues/20>
  - <https://github.com/tuxalin/THST/commits/master>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tuxalin/thst`) · [data/wave8/enrich/raw/github_com_tuxalin_thst.json](../../../data/wave8/enrich/raw/github_com_tuxalin_thst.json) (enrichment confidence 0.75)

</details>
