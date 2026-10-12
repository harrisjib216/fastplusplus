# Bonxai

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MPL-2.0` · 🟢 active

> Header-only C++17 sparse, unbounded VDB-style voxel grid; first-party preliminary numbers show 4.5-22x faster inserts and iteration than Octomap.

| | |
|---|---|
| **Beats** | Octomap (octree-based 3D occupancy map) |
| **Claimed result** | Create 1165 us vs 25522 us (about 21.9x, derived from page data); Update 851 us vs 3824 us (about 4.5x, derived from page data); IterateAllCells 124 us vs 698 us (about 5.6x, derived from page data). README also states Bonxai is 'much faster and, in some cases, even more memory-efficient than an Octree'. |
| **Workload** | Google Benchmark in bonxai_core/benchmark (benchmark_bonxai.cpp vs benchmark_octomap.cpp) on two PCD point clouds from data/: table_scene_mug_rgb.pcd at 0.01 voxel size and room_scan.pcd at 0.05. Create inserts every point into a new grid, Update re-sets the same cells in a filled grid, and IterateAllCells visits every leaf. The README does not say which dataset its numbers come from. |
| **Metric** | latency |
| **Adoption** | 879 stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/facontidavide/Bonxai) · [benchmark](https://github.com/facontidavide/Bonxai) |

## Verdict

The README's preliminary Google Benchmark block (bonxai_core/benchmark, PCD clouds table_scene_mug_rgb at 1 cm or room_scan at 5 cm; which one, and the compiler and CPU, are not stated) reports Create 1165 vs 25522 us, Update 851 vs 3824 us and IterateAllCells 124 vs 698 us against Octomap (about 21.9x, 4.5x and 5.6x, derived from page data). Per point, Bonxai only stores a uint32, while Octomap runs OcTree::updateNode, a probabilistic log-odds update. The like-for-like full-mapping harness (bonxai_map/benchmark/benchmark_kitti.cpp, ProbabilisticMap vs OcTree::insertPointCloud on KITTI) and a NanoVDB harness exist, but no results from them are published.

## Use it when

- Robotics or 3D-mapping code that inserts many points per scan into a sparse voxel map and finds Octomap's per-point insertion too slow.
- Storing custom per-voxel payloads (TSDF values, colours, counters, small structs) without a fixed map boundary.
- Spatially coherent access patterns (scan lines, neighbouring voxels) where the accessor cache avoids most root-map lookups.
- Fast full-map traversal (forEachCell) for publishing or exporting the map.
- Projects that want a small vendorable core: the README says the core data structure is under 1,000 lines and header-only.

## Skip it when

- Very sparse clouds where memory matters: the README says Bonxai can use 20-40% more memory than Octomap there.
- You need multi-resolution queries, octree pruning or Octomap's file formats and ecosystem tools; Bonxai is a single-resolution grid.
- Concurrent writers: VoxelGrid is not thread-safe for writes.
- Safety-critical code without testing: the author calls it a project built 'mostly for fun and for educational purposes', still under development, and memory-safety bugs in accessors and the leaf pool were being fixed as recently as September 2026 (issue #71 open).
- Decisions based on the published speedup: the README numbers are labelled preliminary, give no compiler, CPU or dataset, and compare a plain value store against Octomap's probabilistic update.

## How it is fast

It implements a shallow OpenVDB-style hierarchy (Museth, 'VDB', ACM TOG 2013): a root hash map from block key to an inner grid (default 4^3 bitmask-indexed slots) whose slots point to dense leaf grids (default 8^3 values plus an occupancy bitmask), so a lookup is one hash probe and two array indexes instead of an octree descent. The root map is a custom CoordMap (open addressing, linear probing over 16-byte buckets, values that never move), Accessors cache the last root/inner/leaf so spatially coherent writes skip the hash, leaf blocks for trivial types come from a pooled block allocator, and iteration walks set bits in the masks.

## Compared with alternatives

Pick Bonxai when you need a sparse voxel map that stores values per cell (an Octomap or occupancy-grid replacement). ikd-Tree, nanoflann and PH-tree answer nearest-neighbour or range queries over points, and small_gicp's voxel grid only downsamples clouds for registration.

## Integration

| | |
|---|---|
| **Form** | header-only (bonxai_core, CMake INTERFACE target Bonxai::bonxai_core); bonxai_map and bonxai_ros are optional built components |
| **Dependencies** | none for the core; bonxai_map needs Eigen3 (and is only built when PCL is found); benchmarks need Google Benchmark, PCL and octomap (NanoVDB for its comparison); LZ4 optional; bonxai_ros needs ROS 2 (rclcpp, tf2, pcl_conversions) |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17), CMake 3.10 |
| **Platforms** | portable C++17 with no SIMD intrinsics in the core (GCC/Clang and MSVC attribute macros present); ROS 2 Humble/Jazzy support in bonxai_ros |
| **Thread safety** | Not thread-safe for writes; read-only multithreading is allowed if each thread uses its own accessor (README). The leaf block allocator itself takes a mutex. |
| **Drop-in for the baseline** | partial — it replaces Octomap's OcTree for storing occupancy through bonxai_map::ProbabilisticMap (log-odds hit/miss, clamping, ray casting), but the API, map files and multi-resolution queries differ |

## Gotchas

- Erasing roots or clearing the map through rootMap() frees nodes that accessors may have cached; the header says to recreate accessors afterwards (issue #71 shows a heap-use-after-free reproduction for that pattern). clear() and releaseUnusedMemory() are handled by an epoch counter.
- Moving a VoxelGrid broke its pooled leaves until the 2026-09-28 fix commit ('a moved VoxelGrid keeps its pooled leaves and invalidates accessors'); use a recent main.
- Older code double-destroyed LeafGrid and double-freed Mask::words_ when leaf_bits &gt;= 4 (fixed per an in-source comment), so non-default grid shapes are less battle-tested.
- The default CMake build type is RelWithDebInfo, so set Release explicitly before benchmarking.

## Known shortcomings

- Not like for like: the Octomap benchmark does log-odds updateNode while Bonxai does a plain setValue. No CPU, flags or dataset stated. Octomap is not a category baseline.
- Open #71 (2026-09-28) reports memory-safety bugs including a heap-use-after-free reproduction via rootMap().erase; the move-grid part was fixed the same day and erase is now only documented. An older double-free with leaf_bits&gt;=4 is fixed. benchmark_nanovdb.cpp and benchmark_kitti.cpp exist with no published results.

## Caveats and trade-offs

The README labels the numbers 'preliminary' and says to take them with a grain of salt. It gives no compiler, flags, CPU or dataset; the default CMake build type is RelWithDebInfo. The two sides do not do the same work per point: Bonxai writes a uint32 value with accessor.setValue, while Octomap runs OcTree::updateNode(endpoint, true), a probabilistic log-odds occupancy update. That favors Bonxai in Create and Update. A fairer full-mapping comparison, bonxai_map/benchmark/benchmark_kitti.cpp (probabilistic map with ray casting vs Octomap on KITTI, prints a speed-up), exists, but no results from it are published. The README also says the project is built mostly for fun and education and is under development, and that very sparse clouds can use 20-40% more memory than Octomap. The Octomap baseline is a robotics-mapping incumbent rather than Boost.Geometry/CGAL/GEOS, so the category fit is borderline.

Hierarchical sparse voxel grid influenced by OpenVDB rather than a multi-resolution octree; sparse and unbounded with 32-bit indices (about 40,000 km at 1 cm voxels per the README); core is header-only.

## Maintenance

Actively maintained (last commit 2026-09-28, 879 stars, 1 open and 24 closed issues), MPL-2.0 (file-level copyleft, so the header-only core can be vendored into proprietary code if changes to its files are shared).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'Benchmark (preliminary)' block shows Create 1165 vs 25522 us, Update 851 vs 3824 us and IterateAllCells 124 vs 698 us against Octomap. The matching Google Benchmark code is public (bonxai_core/benchmark/benchmark_bonxai.cpp and benchmark_octomap.cpp), but no compiler, flags, CPU or dataset is given for the published numbers, so this is first-party C.
- **Verifier notes:** Numbers match the README. I found and read the benchmark source the searcher could not locate. Main finding: Octomap does a probabilistic occupancy update per point while Bonxai only stores a value, so the comparison is not like-for-like. Metadata matches: MPL-2.0, 879 stars, not archived, last commit 2026-09-28.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/README.md>
  - <https://github.com/facontidavide/Bonxai>
  - <https://github.com/facontidavide/Bonxai/commits/main>
  - <https://github.com/facontidavide/Bonxai/tree/main/bonxai_core>
  - <https://github.com/facontidavide/Bonxai/tree/main/bonxai_core/benchmark>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/benchmark/benchmark_bonxai.cpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/benchmark/benchmark_octomap.cpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/benchmark/benchmark_utils.hpp>
  - <https://github.com/facontidavide/Bonxai/tree/main/bonxai_map>
  - <https://github.com/facontidavide/Bonxai/tree/main/bonxai_map/benchmark>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_map/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_map/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_map/benchmark/benchmark_pointcloud.cpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_map/benchmark/benchmark_kitti.cpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/CMakeLists.txt>
  - <https://github.com/facontidavide/Bonxai/tree/main/examples>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/README.md>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/package.xml>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/include/bonxai/bonxai.hpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/include/bonxai/coord_map.hpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/include/bonxai/grid_allocator.hpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/include/bonxai/mask.hpp>
  - <https://github.com/facontidavide/Bonxai/tree/main/bonxai_core/benchmark>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/benchmark/benchmark_bonxai.cpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/benchmark/benchmark_octomap.cpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/benchmark/benchmark_utils.hpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/benchmark/benchmark_nanovdb.cpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/benchmark/get_memory.cpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_core/benchmark/synthetic_scan.hpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_map/include/bonxai_map/probabilistic_map.hpp>
  - <https://raw.githubusercontent.com/facontidavide/Bonxai/HEAD/bonxai_map/benchmark/benchmark_kitti.cpp>
  - <https://github.com/facontidavide/Bonxai/issues?q=is%3Aissue>
  - <https://github.com/facontidavide/Bonxai/issues/71>
  - <https://github.com/facontidavide/Bonxai/issues/5>
  - <https://github.com/facontidavide/Bonxai/commits/main>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/facontidavide/bonxai`) · [data/wave8/enrich/raw/github_com_facontidavide_bonxai.json](../../../data/wave8/enrich/raw/github_com_facontidavide_bonxai.json) (enrichment confidence 0.8)

</details>
