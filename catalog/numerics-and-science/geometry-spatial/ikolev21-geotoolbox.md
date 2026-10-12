# GeoToolbox KdBoxTree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Static C++17 k-d tree that indexes boxes as well as points; out-queries Boost.Geometry's R\*-tree on bulk-loaded data.

| | |
|---|---|
| **Beats** | Boost.Geometry 1.90 R\*-tree (also GEOS 3.14.1 STR-tree, nanoflann 1.10.1, tidwall rtree.c) |
| **Claimed result** | README: KdBoxTree is quickest to bulk-load, fastest at range queries on box keys and (from 10^4 elements) on point keys, fastest at nearest queries on box keys; 'Boost R-tree lags behind in query performance'; other indices build 2-4x slower and need 1.5-4x more queries to amortise their build. No single KdBoxTree-vs-Boost ratio is given on the page. |
| **Workload** | Bulk load + range/nearest queries, and insert/erase/reinsert + range queries, on point and box keys (2D/3D, float/double) over synthetic sets (uniform, skewed, clusters, polygon, parcels) and real ESRI-shapefile/OBJ datasets, 10^2 to 10^6 elements |
| **Metric** | throughput |
| **Hardware** | ASUS ROG Strix G16, Windows 11 (CPU model not stated) |
| **Compiler and flags** | MSVC 2026 and Clang 22 (flags not stated) |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-06 |
| **Links** | [repository](https://github.com/ikolev21/GeoToolbox) · [benchmark](https://github.com/ikolev21/GeoToolbox) |

## Verdict

The author's own harness compares KdBoxTree with Boost.Geometry 1.90 R\*-tree, nanoflann 1.10.1, GEOS 3.14.1 STR-tree and tidwall rtree.c on synthetic and real 2D/3D point and box sets of 10^2-10^6 elements. It was built with MSVC 2026 and Clang 22 on an ASUS ROG Strix G16 laptop under Windows 11 (CPU model not stated; the repo's CMake sets /arch:AVX2 plus /GL /LTCG on MSVC and -msse4.2 -flto on Clang). The README reports rankings, not a KdBoxTree-vs-Boost ratio: KdBoxTree builds fastest and wins range queries and box kNN, and Boost 'lags behind in query performance'; raw TSVs are in ikolev21/ikolev21.github.io.

## Use it when

- Bulk-loaded static point or box sets (10^3 to 10^6 elements) queried many times: the README measures it as the fastest index to bulk-load and pays back its build cost within about 100 queries versus a linear scan
- Range/window queries on 2D or 3D box keys (GIS footprints, parcels, mesh triangle bounds), where it ranks first on average ahead of Boost R\*-tree, GEOS and tidwall
- k-nearest queries on box keys: Boost R\*-tree is the only other index in the comparison that supports them, and KdBoxTree is faster
- Point range queries from 10^4 elements upward, or point kNN at 10^6 elements and on strongly structured data, where it passes nanoflann
- Code that needs float or double keys, more than 2 dimensions, and a custom allocator (the template takes a TElementAllocator)

## Skip it when

- Data that changes: there is no insert or erase. Use Boost R\*-tree or tidwall rtree.c for dynamic sets
- Point kNN below about 10^5 elements, or a minimal memory footprint: nanoflann wins both
- 2D box range queries on Polygon-like (ring-shaped) data, where GEOS STR-tree is faster, or 2D boxes around 10^4-10^5 elements, where tidwall is
- Fewer than about 100 queries on about 100 elements: the README says an index tops out at 1.2-2x over a plain std::vector scan at that size
- Production use where maturity matters: 0 stars, no releases or tags, a single author, and the README says it is tested only on Windows

## How it is fast

It is a k-d tree built top-down by midpoint splits on the longest axis of each node's bounding box, with in-place partitioning of a flat element array and nodes kept in one contiguous vector (leaf size 32 by default). Boxes that straddle a split plane go into a third 'middle' child, which is then split only on the other axes, so a box index keeps cheap k-d descent instead of the overlapping MBRs an R-tree has. Each node stores the tight bound of its elements, so a query can return a whole subtree without per-element tests once the window contains the node. An optional StoreSpatialKeys template flag keeps a contiguous copy of the keys so scans need no pointer chasing (about 1.2x faster at the largest sizes, for more memory).

## Compared with alternatives

Pick it over nanoflann when the keys are boxes, or when you have points at 10^6 scale or need range queries above 10^4 elements. Pick it over tidwall rtree.c when the data is static and large or unevenly spread and you need kNN or runtime-chosen dimensions/scalar types. tidwall, and Boost R\*-tree for its versatility, remain the choice for dynamic data, and TG is for polygon predicates rather than indexing.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the index itself: KdBoxTree.hpp plus GeoToolbox's own GeometryTools/Span/SpatialTools headers and the standard library. Eigen is optional; Catch2, Shapelib and LodePNG are only for the tests and benchmarks |
| **Minimum toolchain** | C++17; tested with MSVC 2026 and Clang 22 on Windows |
| **Platforms** | Tested only on Windows x64 (README). The core code is plain portable C++, but the repo's CMake adds /arch:AVX2 (MSVC) or -msse4.2 (other compilers), so on non-x86 targets you build the header yourself |
| **Thread safety** | not documented (queries are const member functions over immutable storage, so concurrent reads look safe, but the author does not state it) |
| **Drop-in for the baseline** | partial: it replaces the bulk-loaded (packing constructor) use of boost::geometry::index::rtree for intersects-window and k-nearest queries, but the API is different and there is no insert/remove, no predicate composition and no Boost.Geometry type adaptation |

## Gotchas

- IndexType is int, so one tree holds fewer than 2^31 elements
- The constructor takes the element vector by value and reorders it during the build. Queries hand back elements by reference or as indices into the tree's own reordered copy, not into your original vector
- StoreSpatialKeys defaults to false, but the published benchmark results were measured with it on. Turning it on raises memory on box keys slightly above Boost R\*-tree
- Splits are at the box midpoint, not the median. Coincident points or rounding make a split fail, which leaves that node an oversized leaf; heavily duplicated keys can therefore produce large leaves

## Known shortcomings

- First-party only; README gives no CPU model, flags or explicit ratio against Boost; 0 stars.
- Tested only on Windows, no releases; index has no insert or erase; published results used StoreSpatialKeys=true while the template defaults to false. Flags are in CMakeLists (/arch:AVX2 /GL /LTCG on MSVC, -msse4.2 -flto otherwise); CPU still unstated.

## Caveats and trade-offs

First-party benchmark; CPU model and compiler flags not stated in README (a commit message mentions AVX2 + LTO enabled for MSVC); raw results live in ikolev21/ikolev21.github.io (not opened). Same README reports nanoflann faster on point nearest queries up to 10^5, GEOS faster on the Polygon box dataset, tidwall on 2D box sets around 10^4-10^5. Repo has 0 stars.

Static index only: bulk-load, no insert/erase. Stores an extra copy of spatial keys by default (StoreSpatialKeys); turning it off is about 1.2x slower at the largest sizes. Boost R\*-tree is the most versatile (dynamic insert/erase, any dimension).

## Maintenance

Active single-author project (last commit 2026-09-06, no releases, 0 stars) under BSL-1.0; the index is one roughly 1,300-line header plus a few helper headers, so vendoring it is straightforward.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README comparison against Boost.Geometry 1.90 R\*-tree (plus nanoflann, GEOS, tidwall) with public benchmark code in the repo, but CPU model and compiler flags are not stated (only 'ASUS ROG Strix G16, Windows 11', MSVC 2026/Clang 22); the README gives rankings and a few ratios, no explicit KdBoxTree-vs-Boost ratio.
- **Verifier notes:** Claims check out against the current README; license BSL-1.0 confirmed from LICENSE.txt; last commit 2026-09-06 from commits page.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ikolev21/GeoToolbox>
  - <https://github.com/ikolev21/GeoToolbox/commits>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/LICENSE.txt>
- **Sources the enricher read:**
  - <https://github.com/ikolev21/GeoToolbox>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/include/GeoToolbox/KdBoxTree.hpp>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/include/GeoToolbox/SpatialTools.hpp>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/CMakeLists.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ikolev21/geotoolbox`) · [data/wave8/enrich/raw/github_com_ikolev21_geotoolbox.json](../../../data/wave8/enrich/raw/github_com_ikolev21_geotoolbox.json) (enrichment confidence 0.75)

</details>
