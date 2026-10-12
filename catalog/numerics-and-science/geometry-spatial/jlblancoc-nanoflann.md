# nanoflann

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Header-only C++11 k-d tree for exact point kNN/radius search; about 2.4x faster point kNN than Boost.Geometry's R\*-tree.

| | |
|---|---|
| **Beats** | Boost.Geometry 1.90 R\*-tree (point k-nearest and range queries) |
| **Claimed result** | GeoToolbox: nanoflann is fastest at point nearest queries (KdBoxTree only overtakes at 10^6) and 'competitive at range queries on point keys' while Boost 'lags behind in query performance'; uses the least memory. Own README: \~50% faster queries than original FLANN. |
| **Workload** | Point-key k-nearest and range queries over 2D/3D datasets, 10^2 to 10^6 points (GeoToolbox suite). |
| **Metric** | throughput |
| **Hardware** | ASUS ROG Strix G16, Windows 11 (CPU model not stated) |
| **Compiler and flags** | MSVC 2026 and Clang 22 (flags not stated) |
| **Adoption** | 2.7k stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/jlblancoc/nanoflann) · [benchmark](https://github.com/ikolev21/GeoToolbox) |

## Verdict

The independent GeoToolbox harness compared nanoflann 1.10.1 (pinned tag, compile-time DIM, L2_Simple, single-threaded build) with Boost.Geometry 1.90 R\*-tree on 2D/3D point sets of 10^2-10^6 elements. It was built with MSVC 2026 and clang-cl 22 (Release, /arch:AVX2 and LTO per its public CMakeLists) on an ASUS ROG Strix G16 laptop under Windows 11, CPU model not stated. Its result TSVs give point-kNN query times 2.40x (clang-cl) and 2.52x (MSVC) faster than Boost as a geomean, falling to about 1.85x at 10^6 points, and point range queries 1.14-1.23x faster. Bulk load was 1.4-1.7x slower, and the range queries used GeoToolbox's own traversal code rather than nanoflann's findWithinBox (all ratios derived from page data). The README's separate \~50% speedup over original FLANN comes from first-party charts with no stated CPU or compiler, and the perf-tests directory it links has moved to MRPT/nanoflann-benchmark.

## Use it when

- Static 2D/3D point clouds (LiDAR scans, ICP correspondences, particle neighbours) queried many times for k nearest or fixed-radius neighbours: point kNN was about 2.4-2.5x faster than Boost R\*-tree (geomean over 49 GeoToolbox runs, derived from page data)
- Memory-constrained indexing: zero-copy adaptors over your existing array. In GeoToolbox, 10^6 2D points took about 8.8 MB of index versus about 43 MB for Boost R\*-tree (derived from page data)
- Data already in Eigen matrices or std::vector&lt;std::vector&lt;T&gt;&gt;, using the bundled adaptors, or in custom containers via a three-method adaptor
- Many concurrent query threads against one immutable index: queries are const and documented thread-safe while nothing is building
- Sliding-window maps that need add/remove: KDTreeSingleIndexIncrementalAdaptor (single self-balancing tree with removeBox/removeOutsideBox) or the Bentley-Saxe KDTreeSingleIndexDynamicAdaptor forest

## Skip it when

- Box or polygon keys: points only. Encoding a box as a 2N-D point needs custom query code and was about 1.4-1.5x slower than Boost on box range queries (derived from page data). Use GeoToolbox KdBoxTree, tidwall rtree.c or Boost
- Build-dominated workloads: the single-threaded bulk load (n_thread_build=1 in GeoToolbox's adapter) was about 1.4-1.7x slower than Boost R\*-tree packing. At 10^6 points the GeoToolbox nearest scenario's total time (build plus queries) favoured Boost (Boost/nanoflann 0.68-0.72, derived from page data); use n_thread_build or 1.13+'s faster concurrent build
- Strongly structured data such as points on concentric circles: on GeoToolbox's 2D Synthetic_Polygon set at 10^6 points, nanoflann kNN took 146 ms versus 53 ms for Boost and 15 ms for KdBoxTree
- Approximate NN in high dimensions: no randomized trees, no LSH and no auto-tuning. The only approximation knob is eps in SearchParameters, so use FLANN, FAISS or an HNSW library
- Metrics beyond L1/L2/SO(2)/SO(3), C or Python bindings from this repo, or SE(3): not supported (README 1.6)

## How it is fast

It is a code-level fork of FLANN's single k-d tree with the virtual-dispatch layers replaced by CRTP and inlined templates. An optional compile-time DIM lets the compiler unroll the distance loops. Splits use FLANN's sliding-midpoint rule: cut the widest-spread axis among those near the maximum bounding-box span at the box midpoint, clamped to the data's min/max, then partition three ways (Dutch national flag). Queries descend the nearer child first and prune the other with an incremental per-axis distance bound (mindist + cut_dist - old_dist, as in Arya-Mount ANN). Leaves hold up to leaf_max_size points (default 10) that are scanned linearly. Since 1.14.0, nodes sit in one contiguous depth-first array and the far child is prefetched (__builtin_prefetch) while the near one is searched.

## Compared with alternatives

Pick nanoflann over GeoToolbox KdBoxTree for exact point kNN/radius search up to about 10^5 points, for the smallest memory footprint, or for a widely packaged dependency (apt, vcpkg, Conan, ROS). KdBoxTree wins on box keys, at 10^6 points and on structured data. Pick it over tidwall rtree.c or THST when keys are points and queries are proximity rather than box overlap.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library; std::thread/std::async unless NANOFLANN_NO_THREADS is defined). Eigen is optional for the Eigen adaptors; GTest and Eigen only for the tests and examples |
| **Minimum toolchain** | C++11 (uses if constexpr when C++17 is available); CI covers GCC/Clang on Linux, MSVC and clang-cl on Windows, and macOS 14/15 |
| **Platforms** | any; no intrinsics apart from a GCC/Clang prefetch builtin. ROS 2 binaries are built for amd64 and arm64 |
| **Thread safety** | Queries (findNeighbors, knnSearch, radiusSearch, rknnSearch) are const and safe for concurrent readers. Building, or mutating a dynamic or incremental index, must not overlap any query. The internal PooledAllocator is not thread-safe. The build itself can be parallelized with n_thread_build |
| **Drop-in for the baseline** | no |

## Gotchas

- With L2 metrics, the radius you pass and every distance returned are squared distances
- The index stores only indices into your adaptor's data, which must outlive the index. A static index does not see points appended or changed after the build, so call buildIndex() again or use the dynamic or incremental adaptors. removePoint does not touch your dataset (open issue #304)
- The default IndexType is uint32_t (about 4.29e9 points). Unsigned coordinate types need an explicitly signed, wide-enough DistanceType; before 1.13.0 this case crashed or returned wrong results
- saveIndex files are version-locked: loadIndex throws on any NANOFLANN_VERSION mismatch, so persisted indices must be rebuilt after an upgrade. Tie order between equidistant points is unspecified unless NANOFLANN_FIRST_MATCH is defined

## Known shortcomings

- \~50% gain over FLANN only in first-party charts, no CPU or compiler stated (code in perf-tests/); FLANN not in the category list; Boost comparison only in GeoToolbox's README.
- GeoToolbox tested 1.10.1, not 1.14.0, and its range queries used GeoToolbox's own traversal, not findWithinBox; bulk load 1.4-1.7x slower than Boost; at 10^6 points Boost wins build+nearest total (0.68-0.72x); 2D Synthetic_Polygon 10^6 kNN 2.7x slower than Boost; unsigned ElementType crash/wrong results fixed only in 1.13.0; README perf-tests link stale (moved to MRPT/nanoflann-benchmark).

## Caveats and trade-offs

Baseline FLANN is not in the category list; README numbers are charts without stated CPU/compiler/flags (reproduction code in perf-tests/); nanoflann is a code-level fork of FLANN (not a GitHub fork); latest release 1.14.0 (2026-09-25); the Boost.Geometry comparison comes only from the GeoToolbox README, where nanoflann wins point nearest queries up to 10^5 elements and uses the least memory.

Points only (boxes need a 2N-dimensional encoding costing \~2x); no erase; stores only indices into caller's dataset; no box nearest query.

## Maintenance

Actively maintained (1.14.0 released 2026-09-25, four releases since June 2026; 2.7k stars; packaged in Debian/Ubuntu, Homebrew, vcpkg, Conan and ROS 2) under BSD-2-Clause, and a single header you can vendor; the measured 1.10.1 predates the 1.13 build rewrite and the 1.14 contiguous-node layout.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now C.
- **Tier reason:** README section 3.2 shows first-party charts and states '\~50% time saving with respect to the original flann implementation'; perf-tests/ code is public but CPU model, compiler and flags are not stated.
- **Verifier notes:** COPYING text is the 2-clause BSD license, so BSD-2-Clause is confirmed. Benchmark code lives at https://github.com/jlblancoc/nanoflann/tree/master/perf-tests (linked from README, not opened).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** kNN geomean 2.40x (clang-cl) / 2.52x (MSVC) vs Boost.Geometry (derived from GeoToolbox page data).
- **Pages the verifier opened:**
  - <https://github.com/jlblancoc/nanoflann>
  - <https://github.com/jlblancoc/nanoflann/commits>
  - <https://raw.githubusercontent.com/jlblancoc/nanoflann/HEAD/README.md>
  - <https://raw.githubusercontent.com/jlblancoc/nanoflann/HEAD/COPYING>
- **Sources the enricher read:**
  - <https://github.com/jlblancoc/nanoflann>
  - <https://github.com/jlblancoc/nanoflann/issues>
  - <https://github.com/jlblancoc/nanoflann/issues/235>
  - <https://github.com/jlblancoc/nanoflann/issues/304>
  - <https://raw.githubusercontent.com/jlblancoc/nanoflann/HEAD/README.md>
  - <https://raw.githubusercontent.com/jlblancoc/nanoflann/HEAD/include/nanoflann.hpp>
  - <https://raw.githubusercontent.com/jlblancoc/nanoflann/HEAD/CHANGELOG.rst>
  - <https://raw.githubusercontent.com/jlblancoc/nanoflann/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jlblancoc/nanoflann/HEAD/COPYING>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/ikolev21/ikolev21.github.io/HEAD/CompareSpatialIndices_ikrogwin11_clangcl_x64.tsv>
  - <https://raw.githubusercontent.com/ikolev21/ikolev21.github.io/HEAD/CompareSpatialIndices_ikrogwin11_msvc_x64.tsv>
  - <https://github.com/ikolev21/GeoToolbox>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/test/Performance/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ikolev21/GeoToolbox/HEAD/test/Performance/NanoflannAdapter.hpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jlblancoc/nanoflann`) · [data/wave8/enrich/raw/github_com_jlblancoc_nanoflann.json](../../../data/wave8/enrich/raw/github_com_jlblancoc_nanoflann.json) (enrichment confidence 0.8)

</details>
