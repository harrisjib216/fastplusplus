# tidwall/rtree.c

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Single-file C dynamic R-tree with O(1) copy-on-write clones; inserts 20-40x faster than Boost.Geometry's R\*-tree.

| | |
|---|---|
| **Beats** | Boost.Geometry 1.90 R\*-tree |
| **Claimed result** | GeoToolbox README: tidwall R-tree is 'faster than Boost at insert/erase/reinsert and at querying afterwards'. Linked result TSVs (ikolev21.github.io, Insert-Erase-Query scenario, Boost time / tidwall time, geomean over 69 dataset/size/dim combinations): clang-cl insert 23.7x, erase 3.6x, reinsert 9.4x, range query 1.06x (range 0.30-2.54x), total 4.9x; MSVC insert 34.8x, erase 3.4x, reinsert 9.4x, query 1.08x, total 6.0x; at 10^6 elements total 10.9x (clang-cl) / 12.6x (MSVC) (derived from page data). Own README: 1M random points insert 151.3 ns/op, search-item 242.4 ns/op (clang-17 -O3, Ryzen 9 5950X), no Boost comparison. |
| **Workload** | Dynamic R-tree insert/erase/reinsert then range queries on point and box keys (GeoToolbox suite, 2D/3D synthetic and real datasets). |
| **Metric** | throughput |
| **Hardware** | GeoToolbox: ASUS ROG Strix G16 laptop, Windows 11 (CPU model not stated); own README: AMD Ryzen 9 5950X, Ubuntu 20.04 |
| **Compiler and flags** | GeoToolbox: MSVC 2026 and clang-cl (Clang 22), x64, flags not stated; own README: clang-17 -O3 |
| **Adoption** | 149 stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/tidwall/rtree.c) · [benchmark](https://github.com/ikolev21/GeoToolbox/blob/main/Readme.md) |

## Verdict

The independent GeoToolbox suite compared rtree.c v0.5.3 (compiled as C with RTREE_NOATOMICS, 2D, double) with Boost.Geometry 1.90 R\*-tree on 25 point and 44 box dataset/size combinations of 10^2-10^6 elements. It was built with MSVC 2026 and clang-cl 22 (Release, /arch:AVX2 and LTO per its public CMakeLists) on an ASUS ROG Strix G16 laptop under Windows 11, CPU model not stated. The result TSVs show dynamic insert/erase/reinsert far faster than Boost: insert 21-41x, erase 2.8-4.1x, reinsert 8-10x and the scenario total 4.8-6.4x (geomeans). Range queries were at parity (1.00-1.12x) after dynamic builds and slightly slower (0.80-0.92x) than Boost's bulk-loaded tree (all ratios derived from page data). The author's own README reports 151 ns/op insert and 242 ns/op item search on 1M random points (clang-17 -O3, Ryzen 9 5950X) with no Boost comparison.

## Use it when

- Dynamic 2D sets with heavy churn (moving entities, live map features, geofences, editors): in GeoToolbox's insert/erase/reinsert/query scenario, insert was 21-41x, erase 2.8-4.1x and reinsert 8-10x faster than Boost R\*-tree (geomeans), and the whole scenario 4.8-6.4x faster (11-13x at 10^6 elements). All ratios derived from page data
- Point or box keys with window (intersects) queries on 10^3-10^6 elements when the index is built and updated by insertion. Range queries afterwards were at parity with a dynamically built Boost tree (1.00-1.12x geomean) and up to about 2x faster at 10^4-10^5 elements (derived from page data)
- C code or FFI that wants one MIT-licensed .c/.h pair with no dependencies and a custom malloc/free hook
- Snapshot isolation: rtree_clone is O(1) and copies nodes lazily on write, so readers can keep an old version while a writer mutates a clone
- Input you can pre-sort along a Hilbert curve: the README's 1M-point run drops insert from 151 to 73 ns/op and item search from 242 to 83 ns/op compared with random order

## Skip it when

- Nearest-neighbour or kNN queries: there are none. Use nanoflann (points), GeoToolbox KdBoxTree or Boost R\*-tree
- Static, query-heavy data: there is no bulk load (STR or Hilbert packing). After an insert-built load, range queries were 0.80-0.92x the speed of Boost's packed tree (geomean), and KdBoxTree is faster still. Insert-built loading itself was 1.3-1.5x faster than Boost's packing (derived from page data)
- Tiny sets of about 10^2 elements: range queries ran at 0.3-0.7x Boost's speed and the full insert/erase/query scenario at 0.33-0.79x (derived from page data)
- Tight memory: at 10^6 2D keys it used about 58-70 MB against Boost 43 MB, KdBoxTree 30-50 MB and nanoflann 8-17 MB (GeoToolbox memory deltas)
- Several dimensions or coordinate types in one program: one DIMS/NUMTYPE per compiled copy of rtree.c. GeoToolbox measured only 2D with double coordinates

## How it is fast

Insertion is a cheap Guttman R-tree variant rather than R\*: descending, it takes the first child whose rectangle already contains the new item, otherwise the child with least area enlargement. It never computes overlap and never does R\*'s forced reinsertion, which is where Boost's insert cost goes. A full node is split in one linear pass ('edge snap'): each entry goes to whichever edge of the node's largest axis it is nearer, with no sorting since v0.6.0. Nodes are wide (64 entries) and keep their 64 rectangles in one contiguous array beside the child or payload array, so a search scans packed coordinates with branch-light intersect tests. Deletion only unlinks emptied nodes and never condenses or reinserts, which keeps erase cheap.

## Compared with alternatives

Pick it over GeoToolbox KdBoxTree and nanoflann when the set changes continuously, since neither supports erase. Pick it over THST when you want a plain C, MIT-licensed dynamic tree with copy-on-write snapshots. For static data, or when you need nearest-neighbour queries, KdBoxTree (boxes) or nanoflann (points) are faster, and TG covers polygon predicates rather than indexing.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libc; &lt;stdatomic.h&gt; for copy-on-write reference counts unless RTREE_NOATOMICS is defined) |
| **Minimum toolchain** | C11 (stdatomic.h, compound literals in the examples); MSVC needs RTREE_NOATOMICS or /experimental:c11atomics, which GeoToolbox handles that way. From C++, compile rtree.c as C |
| **Platforms** | any; portable C with no SIMD or platform code |
| **Thread safety** | not documented. From the code: rtree_search and rtree_scan take a const tree and write nothing, so concurrent readers without a writer look safe, and clones share nodes through atomic reference counts, so separate clones can be mutated on separate threads unless RTREE_NOATOMICS is set |
| **Drop-in for the baseline** | no |

## Gotchas

- rtree.h has no extern "C" guard, so wrap the include from C++. Its prototypes hard-code double coordinates and a void\* payload, and since v0.6.0 rtree.c no longer includes rtree.h. Changing RTREE_NUMTYPE/RTREE_DATATYPE without editing the header therefore compiles silently against mismatched types (inferred from code; the README says to edit the header to match)
- rtree_delete needs a bit-identical rectangle and the same payload pointer (memcmp, or a comparator via rtree_delete_with_comparator), and removes only the first match. It returns true even when nothing matched, so check rtree_count if you need to know
- The published numbers are for older code. GeoToolbox pinned v0.5.3 (May 2024), and the README's run dates from 2023. v0.6.0 (2026-09-05) removed the 10% minimum fill on splits (a node may hold one entry), removed sort-on-split and turned path hints off by default, and no benchmark of the current code is published
- The README's algorithm notes (ties go to the smallest area; an 'equal' bucket during splits) do not match the current code, which keeps the first least-enlargement child and sends ties to the left node. Deletes never refill underfull nodes, so heavy deletion can leave sparse nodes

## Known shortcomings

- Range queries only on par with Boost.Geometry (1.06-1.08x, as low as 0.3x on some datasets); source is a small third-party suite (GeoToolbox) with no flags and no CPU model; highest memory of the indexes tested; no bulk-load, results depend on insertion order.
- GeoToolbox pinned v0.5.3 (May 2024); v0.6.0 (2026-09-05) dropped 10% min fill, sort-on-split and default path hints, so current code is unbenchmarked. Measured 2D double only (record said 2D/3D). Range query vs a bulk-loaded Boost tree 0.80-0.92x, 0.3-0.7x at 10^2 elements; memory 58-70 MB vs Boost 43 MB at 10^6.
- API: rtree_delete returns true when nothing was deleted; rtree.h hard-codes double/void\* and rtree.c no longer includes it, so an RTREE_NUMTYPE override compiles silently mismatched (inferred from code).

## Caveats and trade-offs

Third-party comparison is a small, low-visibility repo; range-query speed vs Boost is roughly at parity (geomean \~1.06-1.08x, worst 0.3x), the large wins are in dynamic insert/erase/reinsert; tidwall is the heaviest index in memory; no bulk-loading, so order-sensitive. Ratios are derived from the linked TSVs, not stated on the README.

Dimensions and scalar type fixed at compile time via macros; no bulk-load, so builds by insertion and is sensitive to input order; heaviest memory use of the indices tested; no nearest query in the comparison.

## Maintenance

Maintained by a single author (v0.6.1 tagged 2026-09-06, last commit 2026-09-21, 149 stars, 2 open issues), MIT-licensed and about 800 lines of C, so easy to vendor. Pin a tag, because v0.6.0 changed the split rules after the published benchmarks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now C.
- **Tier reason:** Independent but small third-party suite (GeoToolbox, benchmark code public in the repo) compares directly against Boost.Geometry 1.90 R\*-tree, with per-run numbers in linked TSVs; compiler named (MSVC 2026, clang-cl 22) but flags unstated and hardware given only as a laptop model (ASUS ROG Strix G16), no CPU model, so not A; not a well-known suite, so not B.
- **Verifier notes:** Real win vs Boost R\*-tree on dynamic updates (insert \~20-35x), query parity. Could rise to A if GeoToolbox's CMake flags and the laptop CPU model are pinned down.
- **Fields the verifier corrected:** `claimed_speedup`, `benchmark_url`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ikolev21/GeoToolbox/blob/main/Readme.md>
  - <https://github.com/tidwall/rtree.c>
  - <https://github.com/tidwall/rtree.c/commits>
  - <https://github.com/ikolev21/ikolev21.github.io>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/tidwall/rtree.c/HEAD/README.md>
  - <https://raw.githubusercontent.com/ikolev21/ikolev21.github.io/HEAD/CompareSpatialIndices_ikrogwin11_clangcl_x64.tsv>
  - <https://raw.githubusercontent.com/ikolev21/ikolev21.github.io/HEAD/CompareSpatialIndices_ikrogwin11_msvc_x64.tsv>
- **Sources the enricher read:**
  - <https://github.com/tidwall/rtree.c>
  - <https://github.com/tidwall/rtree.c/commits>
  - <https://github.com/tidwall/rtree.c/tags>
  - <https://github.com/tidwall/rtree.c/commit/fe57eb8>
  - <https://github.com/tidwall/rtree.c/issues?q=is%3Aissue>
  - <https://github.com/tidwall/rtree.c/issues/2>
  - <https://raw.githubusercontent.com/tidwall/rtree.c/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/rtree.c/HEAD/rtree.h>
  - <https://raw.githubusercontent.com/tidwall/rtree.c/HEAD/rtree.c>
  - <https://raw.githubusercontent.com/tidwall/rtree.c/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tidwall/rtree.c/HEAD/tests/run.sh>
  - <https://raw.githubusercontent.com/tidwall/rtree.c/v0.5.3/rtree.c>
  - <https://github.com/ikolev21/GeoToolbox>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/test/Performance/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/test/Performance/TidwallRtree.hpp>
  - <https://raw.githubusercontent.com/ikolev21/ikolev21.github.io/HEAD/CompareSpatialIndices_ikrogwin11_clangcl_x64.tsv>
  - <https://raw.githubusercontent.com/ikolev21/ikolev21.github.io/HEAD/CompareSpatialIndices_ikrogwin11_msvc_x64.tsv>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tidwall/rtree.c`) · [data/wave8/enrich/raw/github_com_tidwall_rtree_c.json](../../../data/wave8/enrich/raw/github_com_tidwall_rtree_c.json) (enrichment confidence 0.8)

</details>
