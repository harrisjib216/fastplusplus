# Indexicon R-tree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Single-header C++17 dynamic N-D R\*-tree for points or boxes; matches or beats Boost.Geometry's R-tree, by up to about 35%.

| | |
|---|---|
| **Beats** | Boost.Geometry R-tree (boost::geometry::index::rtree) |
| **Claimed result** | README charts only (values read off the images, approximate): insertion on MARINE at capacity 512 about 31.8 s (Boost) vs about 25 s (Indexicon), roughly 20% less time; range query on MARINE at capacity 32 about 425 ms vs about 280 ms (roughly 34% less); TORONTO queries at capacity 32 about 38.5 ms vs about 30.5 ms. Near parity for OSM insertion at capacities 32-64, MIAMI insertion at 32 and TIGER queries at 32-128. Indexicon is at or below Boost in every plotted point (derived from page data). |
| **Workload** | R-tree insertion time and range-query time versus Boost's R-tree for node capacities 32-512 on six spatial datasets (MARINE, MIAMI, OSM, TAXIS, TIGER, TORONTO). |
| **Metric** | latency |
| **Compiler and flags** | Not stated for the Boost comparison; the repo's examples are built with g++ -std=c++17 -O3 (test/run_all.sh). |
| **Adoption** | 25 stars; companion paper arXiv 2606.04676 |
| **Last commit** | 2026-08-17 |
| **Links** | [repository](https://github.com/psimatis/Indexicon-Spatial-Library) · [benchmark](https://github.com/psimatis/Indexicon-Spatial-Library) |

## Verdict

Two first-party README charts compare Indexicon's R-tree with Boost.Geometry's R-tree on six real datasets (MARINE, MIAMI, OSM, TAXIS, TIGER, TORONTO; 3.5M-112.8M points or boxes, 2D and 3D) at node capacities 32-512. Indexicon is at or below Boost at every plotted point: insertion is about 20% lower at capacity 512 (MARINE about 25 s vs 31.8 s) and range queries about 34% lower at capacity 32 (MARINE about 280 ms vs 425 ms), all values read off the images (derived from page data). Neither the Boost balancing algorithm (linear, quadratic or rstar), compiler flags, CPU nor the query workload is stated, and the Boost harness is not in the repo; the companion arXiv paper 2606.04676 (same authors) could not be opened from this environment.

## Use it when

- Dynamic in-memory workloads mixing bulk load, inserts, deletes, range and kNN queries over tens of millions of 2D or 3D points or boxes, which is what the README charts measure (3.5M to 112.8M records)
- You already use Boost's R\*-tree and want the same algorithm with about 10-20% less insertion time at large capacities (256-512) and about 15-35% less range-query time at small capacities, without a Boost dependency
- Projects that want a single dependency-free header and compile-time dimension, coordinate type and node capacities, including more than 3 dimensions
- Research or teaching code that compares several index families (R-tree, quad-tree, MX-CIF, oct-tree, KD-tree) behind one API

## Skip it when

- You need Boost's query language (intersects/within/covered_by/nearest predicates and their combinations), query iterators, or adapting your own geometry types
- Static data queried far more than it changes: packed static indexes such as GeoToolbox KdBoxTree or a Hilbert-packed R-tree avoid insert machinery entirely
- Production code that needs maturity: 17 commits, a repo created in May 2026, no tests beyond usage examples, and no published benchmark harness
- Insertion-heavy workloads where the gap matters: the gain over Boost is small (parity at capacities 32-64 on OSM and MIAMI), while PH-tree reports about 5x faster inserts than Boost

## How it is fast

The R-tree follows the same design and defaults as Boost's rstar&lt;MaxElements&gt; parameters (min elements and forced-reinsert count 0.3 x capacity, overlap-cost threshold 32), and its bulk load is the same top-down packing scheme as Boost's pack_create (median counts by subtree size, nth_element along the longest edge of a hint box). The differences are in the layout and hot paths. Leaf and internal capacities are separate template parameters, and nodes keep entries in fixed inline arrays. The point tree stores raw points in leaves rather than degenerate boxes. R\* splits score every split position with prefix/suffix bounding boxes in one pass per axis. A range query emits a whole subtree without per-entry tests when the query window contains the child's box.

## Compared with alternatives

Pick it over PH-tree or tidwall/rtree.c when you want a classic R\*-tree that behaves like Boost's (same parameters and packing) in arbitrary dimensions, as one dependency-free header. Pick PH-tree for much larger insert gains, tidwall/rtree.c for a plain C 2D dynamic tree, and GeoToolbox KdBoxTree or nanoflann for static data.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | C++17 (the examples build with g++ -std=c++17 -O2/-O3) |
| **Platforms** | any platform with a C++17 compiler; no SIMD or OS-specific code in the R-tree headers |
| **Thread safety** | not documented. query, queryPoint and knnQuery are const and keep no internal mutable state, so concurrent reads look safe; insert and remove need external locking |
| **Drop-in for the baseline** | partial: same R\*-tree parameter set and packing algorithm as boost::geometry::index::rtree&lt;..., rstar&lt;N&gt;&gt;, but a different API (insert(point, value), query(box, out_iter), knnQuery(point, k, out_iter)), no predicates, and no allocator parameter |

## Gotchas

- Both R-tree headers put `using namespace std;` at global scope and define RPoint, RBox, Node, RTree, contains and intersects in the global namespace, so rtree_point.hpp and rtree_mbr.hpp cannot be included in the same translation unit and may clash with your own names
- RTree owns raw node pointers and deletes them in its destructor but neither deletes nor defines copy or move operations, so copying a tree (for example, passing it by value) double-frees
- knnQuery writes the k results in heap order, not sorted by distance, and k = 0 calls front() on an empty vector (undefined behavior)
- Each node is a fixed std::array of capacity + 1 entries (default capacity 128), so sparse nodes still occupy full size. remove() needs an exact coordinate match plus Value ==

## Known shortcomings

- Boost harness not in the repo; paper (arXiv 2606.04676) unreadable here; gains 10-35% with several configs at parity.
- Correctness bugs: RTree has no copy/move handling, so copying double-frees; knnQuery with k=0 calls front() on an empty vector (UB); kNN results come back unsorted. Headers put using namespace std and RTree/RPoint/RBox at global scope, so point and box headers cannot share one translation unit. R-tree reuses Boost rstar defaults and pack_create packing (reimplementation). Boost variant, hardware, flags and query workload unstated; no harness; issue #1 on nanoflann fairness closed without reply.

## Caveats and trade-offs

Own benchmark against Boost only, shown as chart images. The Boost comparison harness is not in the repo (test/ holds usage examples only). Compiler, flags and CPU are not on the README. The comprehensive results are in arXiv preprint 2606.04676 (same authors), which could not be opened because arxiv.org is egress-blocked; a search summary says it also compares against PCL and nanoflann. Which Boost balancing algorithm (linear, quadratic or rstar) was used is not stated. Gains are modest (about 10-35%) and several configurations are at parity. Repo created 2026-05-29 (17 commits).

Single-header C++17 R-tree, quad-tree, MX-CIF quad-tree, oct-tree and KD-tree; point and MBB data; top-down packing, R\* insertion, deletion with orphan reinsertion.

## Maintenance

New, active academic project (MIT, 25 stars, 17 commits, last commit 2026-08-17). Its one GitHub issue, which questioned the fairness of the paper's dynamic-tree vs nanoflann comparison, was closed with no reply shown. Small enough to vendor, but treat it as research-grade code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README shows two chart images (figures/rtree_insert_time.png, rtree_query_time.png) of Indexicon vs the Boost R-tree on six datasets at capacities 32-512, with no table, hardware or flags. The Boost harness is not in the repo. The companion paper is an arXiv preprint by the same authors (not peer-reviewed as far as could be seen), so C.
- **Verifier notes:** Chart read-offs match the record's approximate values. Metadata from the repo page: MIT, 25 stars, not a fork, last commit 2026-08-17. arxiv.org abs and html were both blocked; one WebSearch confirmed the paper's title and authors (Simatis, Bouros, Mamoulis) and its Boost/PCL/nanoflann comparison.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/psimatis/Indexicon-Spatial-Library>
  - <https://github.com/psimatis/Indexicon-Spatial-Library/commits>
  - <https://github.com/psimatis/Indexicon-Spatial-Library/tree/main/test>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/README.md>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/figures/rtree_insert_time.png>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/figures/rtree_query_time.png>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/test/run_all.sh>
- **Sources the enricher read:**
  - <https://github.com/psimatis/Indexicon-Spatial-Library>
  - <https://github.com/psimatis/Indexicon-Spatial-Library/issues?q=is%3Aissue>
  - <https://github.com/psimatis/Indexicon-Spatial-Library/issues/1>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/README.md>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/indexes/rtree_point.hpp>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/indexes/rtree_mbr.hpp>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/test/run_all.sh>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/test/rtree/rtree_point_2d.cpp>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/test/rtree/rtree_mbr_2d.cpp>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/figures/rtree_insert_time.png>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/figures/rtree_query_time.png>
  - <https://raw.githubusercontent.com/psimatis/Indexicon-Spatial-Library/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/boostorg/geometry/develop/include/boost/geometry/index/detail/rtree/pack_create.hpp>
  - <https://raw.githubusercontent.com/boostorg/geometry/develop/include/boost/geometry/index/parameters.hpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/psimatis/indexicon-spatial-library`) · [data/wave8/enrich/raw/github_com_psimatis_indexicon_spatial_library.json](../../../data/wave8/enrich/raw/github_com_psimatis_indexicon_spatial_library.json) (enrichment confidence 0.75)

</details>
