# ikd-Tree (incremental k-d tree)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-2.0-only` · 🔴 abandoned

> Incremental 3-D k-d tree for LiDAR SLAM maps: point/box updates without full rebuilds; per-scan time 1.03-2.1x below nanoflann and Boost R\*-tree.

| | |
|---|---|
| **Beats** | Boost.Geometry R\*-tree, PCL octree and nanoflann dynamic k-d tree, each integrated into FAST-LIO2 (FAST-LIO2, IEEE T-RO 2022, Table III); also a static k-d tree rebuilt every scan (FAST-LIO, and the ikd-Tree preprint's PCL comparison) |
| **Claimed result** | FAST-LIO2 Table III (average ms per scan over 18 sequences, single-thread kNN; ratios derived from page data): total time (incremental update + kNN), ikd-Tree vs Boost.Geometry R\*-tree 1.26-2.09x faster (e.g. nclt 3: 15.42 vs 32.29 ms; utbm 1: 18.42 vs 26.50), vs PCL octree 2.29-3.06x (utbm 1: 18.42 vs 45.00), vs nanoflann 1.03-1.34x (nclt 1: 15.64 vs 20.41). kNN search: R\*-tree 1.25-2.09x slower, nanoflann 1.04-1.34x slower, octree 2.6-3.3x slower. Incremental update: the octree is fastest in most sequences (ikd-Tree up to 1.8x slower, e.g. utbm 1 3.23 vs 2.12 ms); ikd-Tree beats the R\*-tree by 1.17-2.2x, and nanoflann is slightly faster on ulhk 1-3 and lili 2. Worst case: nanoflann's incremental-update peaks exceed 3 s on seven utbm sequences and 7 s on three nclt sequences, against an ikd-Tree maximum of 214.4 ms (nclt 2) and under 150 ms elsewhere. System level (Table VII): FAST-LIO, which rebuilds a static k-d tree each scan, spends 13.81 ms per scan on mapping vs 0.13 ms for FAST-LIO2 with ikd-Tree (Intel). The ikd-Tree preprint numbers (about 1.6 ms vs over 10 ms for PCL's static tree; 4% of static computation time) were seen only through search snippets. |
| **Workload** | LiDAR-inertial SLAM map maintenance (FAST-LIO2 style): incremental point insertion, box deletion and k-NN on a growing 3-D map. |
| **Metric** | latency |
| **Hardware** | DJI Manifold 2-C: Intel Core i7-8550U (1.8 GHz, 4 cores), 8 GB RAM, for the data-structure comparison; FAST-LIO2 alone was also run on a Khadas VIM3 (2.2 GHz Cortex-A73, 4 GB RAM). |
| **Compiler and flags** | Not stated in the FAST-LIO2 paper. The ikd-Tree demo CMakeLists uses -std=c++14 -pthread -O3 and links PCL. |
| **Adoption** | 810 stars, 219 forks; used inside FAST-LIO2 (IEEE T-RO 2022) |
| **Last commit** | 2022-03-04 |
| **Links** | [repository](https://github.com/hku-mars/ikd-Tree) · [benchmark](https://raw.githubusercontent.com/hku-mars/FAST_LIO/HEAD/doc/Fast_LIO_2.pdf) |

## Verdict

In the peer-reviewed FAST-LIO2 paper (IEEE T-RO 2022, same group), the authors wired ikd-Tree, Boost.Geometry's R\*-tree, PCL's octree and nanoflann's dynamic k-d tree into FAST-LIO2 and timed 18 sequences on an Intel i7-8550U (DJI Manifold 2-C), k=5, compiler not stated. Total per-scan time (updates plus kNN) was 1.03-1.34x lower than nanoflann, 1.26-2.09x lower than the R\*-tree and 2.29-3.06x lower than the octree (derived from page data). The octree had the fastest updates in most sequences, and the main win over nanoflann is avoiding its multi-second update peaks. The baseline integration code (with emulated downsampling for the other trees) is not public.

## Use it when

- LiDAR or LiDAR-inertial odometry and mapping that inserts a few thousand downsampled points per scan and runs small k-NN (FAST-LIO2 uses k=5) against a local map of 10^5-10^6 points
- Sliding-window or moving-map applications that need box-wise deletion of everything outside a region, which ikd-Tree does with lazy labels instead of per-point removes
- Real-time loops where worst-case update latency matters more than mean: in FAST-LIO2's Table III ikd-Tree's update peak stays at or under 214 ms while nanoflann's dynamic index peaks above 3 s on seven sequences
- Embedded x86 or ARM Linux robots already using PCL (the paper runs FAST-LIO2 on an i7-8550U and on a Cortex-A73 board)

## Skip it when

- Anything other than 3-D float points: x/y/z and per-axis node ranges are hard-coded (issue #26 asks about 2-D; issue #39 reports pcl::PointXYZL not working)
- Bulk loading or large batch inserts: Add_Points inserts point by point, and issue #36 reports 30,000-point inserts slower than PCL's kd-tree
- Commercial or permissive-license projects: GPLv2, and the README asks commercial users to contact the authors
- Code that needs a maintained dependency or exact deletes: last commit 2022-03-04, 24 open issues, including an open report (#25) that ties on the split coordinate make point lookups miss
- Pure insert-heavy workloads: in FAST-LIO2's comparison PCL's octree has the fastest incremental updates in most sequences; ikd-Tree wins on k-NN and total time

## How it is fast

Each node stores its subtree's bounding cuboid, size and lazy 'deleted' labels, so box deletes and box re-adds mark whole subtrees in O(log n)-style traversals and push labels down later instead of touching every point. Points are inserted one at a time, and a subtree is rebuilt only when it violates an alpha-balanced criterion (child share outside 1-alpha_bal..alpha_bal) or an alpha-deleted criterion (invalid share above alpha_del), a scapegoat-tree style partial rebuild. Subtrees of 1,500 points or more are rebuilt on a second pthread while the main thread keeps updating and querying; updates made meanwhile go into an operation log that is replayed onto the new subtree before it is swapped in. k-NN uses bounding-box ('bounds-overlap-ball') pruning plus the max-distance cutoff that LiDAR odometry naturally supplies.

## Compared with alternatives

Pick ikd-Tree over nanoflann's dynamic index when you need bounded worst-case update latency, box deletion and on-tree downsampling for a single 3-D LiDAR map; nanoflann is BSD, header-only, any dimension and maintained. Pick PSI/SpaceTreeLib or Pkd-tree instead for large parallel batch updates on many-core servers, and PH-tree for a permissively licensed dynamic index with general key types.

## Integration

| | |
|---|---|
| **Form** | source-drop (ikd-Tree/ikd_Tree.h + ikd_Tree.cpp; FAST-LIO2 vendors its own copy) |
| **Dependencies** | PCL (the header includes pcl/point_types.h; Eigen::aligned_allocator arrives through it), POSIX threads (pthread, usleep). The demos need PCL 1.8+ |
| **Minimum toolchain** | C++14 (the demo CMakeLists builds with -std=c++14 -pthread -O3); CMake 2.8+ |
| **Platforms** | POSIX/Linux (pthread and unistd.h); Windows and macOS not documented |
| **Thread safety** | Not documented in the README. Internally each tree runs its own rebuild thread synchronised with mutexes, and the FAST-LIO2 paper says k-NN supports multi-threaded search, but issue #20 reports a double free when Nearest_Search is called from several OpenMP threads (closed, no fix shown). Treat updates as single-writer |
| **Drop-in for the baseline** | no |

## Gotchas

- Each KD_TREE object embeds a 1,000,000-entry operation-log ring buffer (MANUAL_Q, Q_LEN) by value, about 44 MB per tree for its own point type and about 64 MB for pcl::PointXYZI (derived from the header's struct layout), so construct it on the heap (KD_TREE::Ptr). The ring buffer's push has no overflow check, so more than 10^6 operations logged during one background rebuild would silently overwrite entries
- Deletes are lazy: deleted points stay in memory and in tree size until a rebuild, so memory and k-NN cost depend on rebuild timing (issue #42 reports memory not released after deleting the root). Delete_by_point descends one side only on strict less-than, which is why issue #25's tie case can miss a point
- The constructor starts a pthread and prints 'Multi thread started' to stdout; the destructor joins it (issue #43 reports a hang on destruction). Default parameters differ between the constructor (balance 0.6) and InitializeKDTree (balance 0.7)
- Only ikdTree_PointType, pcl::PointXYZ and pcl::PointXYZI are explicitly instantiated in ikd_Tree.cpp; other point types need an added 'template class' line (issue #30 reports an undefined reference to KD_TREE&lt;POINT_TYPE&gt;::\~KD_TREE(), the symptom of a missing instantiation)

## Known shortcomings

- Evidence is the FAST-LIO2 T-RO 2022 paper (PDF in hku-mars/FAST_LIO), Table III on an i7-8550U: total time 1.26-2.09x vs Boost.Geometry R\*-tree, 2.3-3.1x vs PCL octree, only 1.03-1.34x vs nanoflann; the octree is faster at updates. GPL-2.0; abandoned since 2022.
- Correctness: open #25 confirmed in code, point delete searches only one side of each split, so a point tying on the split coordinate can be missed. Security/robustness: #20 double free when Nearest_Search runs on several OpenMP threads (closed, no fix shown); open #37 segfault. The 1M-entry rebuild log ring buffer has no overflow check and adds \~44-64 MB to every tree object. GPLv2; abandoned since 2022, 24 open issues.

## Caveats and trade-offs

The evidence is a peer-reviewed paper by the same group (first-party but reviewed). The baselines were wrapped into FAST-LIO2 by the authors, with downsampling emulated through range or radius search for the R\*-tree, octree and nanoflann (nanoflann masks deleted points instead of removing them, so its tree grows); that integration code is not public. ikd-Tree is not uniformly faster: the PCL octree has the fastest incremental updates in most sequences, and nanoflann's updates are slightly faster on ulhk 1-3 and lili 2. The gain over nanoflann in total time is small (3-34%); the main advantage is bounded worst-case latency. The 13.81 vs 0.13 ms mapping figure compares two different SLAM pipelines (FAST-LIO rebuilds a static tree per scan), so it measures incremental vs rebuild, not tree speed. The repo's own demo (examples/ikd_Tree_demo.cpp) times only ikd-Tree. The header includes pcl/point_types.h, so PCL is a dependency. Last commit 2022-03-04. README says GPLv2 (links the GPL-2.0 text) with no 'or later' clause and asks commercial users to contact the authors; SPDX GPL-2.0-only is a reading of that.

GPLv2 (README: contact the authors for commercial use). Dynamic deletion is lazy: points are flagged deleted and removed during a background rebuild, so memory and k-NN cost depend on rebuild timing; threaded rebuild (-pthread). Supports box delete, box/radius search and on-tree downsampling; written for 3-D LiDAR points and later templated (README thanks a contributor for templating it). Demo build requires PCL.

## Maintenance

Abandoned since 2022-03-04 (24 open issues, several crash and correctness reports unanswered) and GPLv2-only, so vendor it knowingly; the copy inside FAST-LIO2 is the best-exercised version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the peer-reviewed FAST-LIO2 paper (IEEE T-RO 2022; PDF in hku-mars/FAST_LIO doc/Fast_LIO_2.pdf) benchmarks ikd-Tree against the Boost.Geometry R\*-tree, PCL octree and nanoflann dynamic k-d tree on 18 sequences (Table III, Fig. 5) on an Intel i7-8550U. Not A: the integration code for the three baselines is not public and no compiler or flags are stated.
- **Verifier notes:** Found the peer-reviewed FAST-LIO2 paper PDF in the hku-mars/FAST_LIO repo (raw.githubusercontent.com works), which has a real head-to-head against Boost.Geometry's R\*-tree (a category baseline), so it upgrades to B and baseline_in_list becomes true. Metadata confirmed: 810 stars, 219 forks, 39 commits, last commit 2022-03-04, GPL-2.0 LICENSE.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/hku-mars/ikd-Tree>
  - <https://github.com/hku-mars/ikd-Tree/commits>
  - <https://raw.githubusercontent.com/hku-mars/ikd-Tree/HEAD/README.md>
  - <https://raw.githubusercontent.com/hku-mars/ikd-Tree/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/hku-mars/ikd-Tree/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/hku-mars/ikd-Tree/HEAD/examples/ikd_Tree_demo.cpp>
  - <https://raw.githubusercontent.com/hku-mars/ikd-Tree/HEAD/ikd-Tree/ikd_Tree.h>
  - <https://raw.githubusercontent.com/hku-mars/ikd-Tree/HEAD/ikd-Tree/ikd_Tree.cpp>
  - <https://github.com/hku-mars/FAST_LIO>
  - <https://raw.githubusercontent.com/hku-mars/FAST_LIO/HEAD/README.md>
  - <https://raw.githubusercontent.com/hku-mars/FAST_LIO/HEAD/doc/Fast_LIO_2.pdf>
- **Sources the enricher read:**
  - <https://github.com/hku-mars/ikd-Tree/issues?q=is%3Aissue>
  - <https://github.com/hku-mars/ikd-Tree/issues/20>
  - <https://github.com/hku-mars/ikd-Tree/issues/25>
  - <https://github.com/hku-mars/ikd-Tree/issues/35>
  - <https://github.com/hku-mars/ikd-Tree/issues/36>
  - <https://github.com/hku-mars/ikd-Tree/issues/37>
  - <https://raw.githubusercontent.com/hku-mars/ikd-Tree/HEAD/README.md>
  - <https://raw.githubusercontent.com/hku-mars/ikd-Tree/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/hku-mars/ikd-Tree/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/hku-mars/ikd-Tree/HEAD/ikd-Tree/ikd_Tree.h>
  - <https://raw.githubusercontent.com/hku-mars/ikd-Tree/HEAD/ikd-Tree/ikd_Tree.cpp>
  - <https://raw.githubusercontent.com/hku-mars/ikd-Tree/HEAD/examples/ikd_Tree_demo.cpp>
  - <https://raw.githubusercontent.com/hku-mars/FAST_LIO/HEAD/doc/Fast_LIO_2.pdf>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/hku-mars/ikd-tree`) · [data/wave8/enrich/raw/github_com_hku_mars_ikd_tree.json](../../../data/wave8/enrich/raw/github_com_hku_mars_ikd_tree.json) (enrichment confidence 0.75)

</details>
