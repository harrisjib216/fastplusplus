# Pkd-tree (parallel kd-tree with batch updates)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Parallel ParlayLib kd-tree with batch insert/delete; builds 80-277x faster than CGAL's kd-tree on 10^9 points.

| | |
|---|---|
| **Beats** | CGAL kd-tree (Spatial_searching) and Boost.Geometry R-tree (also BHL-tree and Log-tree) |
| **Claimed result** | Repo raw results (script/data, times presumably in seconds, hardware unstated), all ratios derived from page data: build.csv, 10^9 3-D points: CGAL kd-tree 1082.4 vs Pkd-tree 3.91 (uniform, about 277x) and 381.3 vs 4.77 (Varden, about 80x). knn.csv, 10^9 3-D points, k=10: CGAL 0.223 vs 0.162 (uniform, about 1.4x) and 3.066 vs 1.713 (Varden, about 1.8x). summary.csv, 10^8 12-D points: build 112.18 vs 0.938 (uniform, about 120x) and 46.69 vs 1.07 (Varden, about 44x); 10% batch insert 171.2 vs 0.115 and 10% delete 29.99 vs 0.148 (uniform); range query 109.1 vs 17.4 (uniform, about 6.3x); kNN column 63.7 vs 51.4 (uniform) but 0.046 vs 0.048 on Varden (CGAL slightly faster). insert.csv/delete.csv: CGAL needs 709-2794 for any batch insert (it rebuilds the tree), and CGAL deletion of 0.1M points takes 0.347 vs 0.0054 (uniform) and 0.033 vs 0.0062 (Varden). Paper numbers seen only in search-result summaries, not checked: 17.4-40.7x faster insertions and 3.27-21.7x faster deletions than Log-tree; on 96 cores 91.9-115x faster construction than the sequential Boost R-tree, 10.4-14.8x faster kNN and 4.13-4.17x faster range report. |
| **Workload** | Parallel kd-tree construction, batch insertion and deletion, k-nearest-neighbor, range query and range count on large point sets, compared with CGAL, Boost's sequential R-tree and other parallel kd-tree baselines (SIGMOD 2025 paper). |
| **Metric** | throughput |
| **Hardware** | 96 cores (CPU model not seen) |
| **Compiler and flags** | -O3 -mcx16 -march=native (CMakeLists.txt Release build); README: tested with clang 17, also compiles with g++ 13; the compiler used for the paper runs was not confirmed |
| **Adoption** | 90 stars, 4 forks; SIGMOD 2025 (PACMMOD 3(1)) artifact; README says the code now lives in ucrparlay/SpaceTreeLib (PSI-Lib) |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/ucrparlay/Pkd-tree) · [benchmark](https://github.com/ucrparlay/Pkd-tree/tree/main/script/data) |

## Verdict

First-party raw CSVs in script/data compare parallel Pkd-tree with CGAL's kd-tree, which was built with Parallel_tag and queried inside tbb::parallel_for. The CSVs give no units, hardware or date; times are presumably seconds. On 10^9 3-D points, build took 3.91 vs 1082.4 (uniform) and 4.77 vs 381.3 (Varden), and kNN (k=10) was only 1.4-1.8x faster. The batch insert and delete ratios are huge mainly because CGAL rebuilds after inserts and removes points one at a time. The SIGMOD 2025 paper was not opened; search snippets put its runs on a 96-core four-way Xeon Gold 6252 with 1.5 TB RAM. The code is built with -O3 -mcx16 -march=native, and the repo's Boost baseline is a sequentially built 2-D bgi::rtree&lt;quadratic&lt;2&gt;&gt;, a very small node capacity, so the Boost ratios flatter Pkd-tree.

## Use it when

- Building kd-trees over 10^8-10^9 low-dimensional points on a many-core server: build.csv for 10^9 3-D points shows 3.91 vs CGAL 1082.4 (uniform, about 277x) and 4.77 vs 381.3 (Varden, about 80x), derived from page data
- Point sets that change through large batches (sliding windows, simulation steps, streaming scans): 10% batch insert into 10^8 12-D points took 0.115 vs CGAL's 171.2 (CGAL inserts and rebuilds), and deleting 0.1M points took 0.0054 vs 0.347 (uniform)
- Range report and range count on large static sets: the 12-D uniform range query took 17.4 vs 109.1 for CGAL (about 6.3x, derived from page data)
- Heavily skewed inputs (the Varden distribution), where the sampled multi-level build still stays balanced

## Skip it when

- kNN-dominated workloads: kNN was only 1.4-1.8x faster than parallel CGAL on 10^9 3-D points, and CGAL was slightly faster on one 12-D Varden row. Search snippets of the paper (not opened) say Pkd-tree, BHL-tree and CGAL have similar kNN performance
- Few cores or single-threaded use: every win comes from parallel build and update; a SERIAL build mode exists, but no single-thread comparison was found
- Production code that needs a maintained dependency: the README says 'This repository will no longer be updated'. The successor, PSI-Lib, notes it was later refactored with AI assistance and that some indexes' performance is 'slightly affected'
- Boxes, polygons, segments, non-Euclidean metrics or approximate NN: points only
- Windows, MSVC or non-x86 targets: only Linux with clang 17 and g++ 13 is documented, and the Release flags include the x86-only -mcx16 -march=native

## How it is fast

Instead of one median split per level, the build samples about 32x64 points (hash-indexed) to choose splitters for 6 levels at once (63 pivots, 64 buckets). It then distributes the points into the buckets with a blocked, cache-friendly parallel 'sieve' (per-block counts plus prefix sums), and recurses in parallel with ParlayLib fork-join; the split axis is the dimension with the widest extent. Leaves hold up to 32 points, and subtrees below 1024 points are built serially. Batch updates sieve the whole batch down the same multi-level skeleton and rebuild only subtrees whose children leave weight balance (imbalance ratio 30%, alpha 0.3). An update therefore costs about the size of the batch, not a full rebuild (CGAL rebuilds on insert). Queries are classic kd-tree searches with bounding-box pruning and a bounded priority queue for kNN.

## Compared with alternatives

Pick Pkd-tree over nanoflann when you have many cores and need parallel build or large batch updates at 10^8-10^9 scale. nanoflann is single-threaded by default, but it is header-only with no ParlayLib dependency, maintained and widely packaged. Pick ArborX instead for GPU or Kokkos batched queries over arbitrary geometry with rebuild-only updates. For new projects, consider the successor PSI-Lib, which adds orth-trees and space-filling-curve trees.

## Integration

| | |
|---|---|
| **Form** | header-only (include/cpdd) plus ParlayLib as a git submodule |
| **Dependencies** | ParlayLib (submodule). Optional: jemalloc, numactl. CGAL with TBB, Boost and ParGeo/Zdtree are only for the benchmark harnesses |
| **Minimum toolchain** | C++20; CMake 3.15+; tested with clang 17 (recommended for speed), compiles with g++ 13 |
| **Platforms** | Linux x86-64 documented (Release build uses -O3 -mcx16 -march=native); other platforms not documented |
| **Thread safety** | not documented. The harness calls k_nearest, range_count and range_query concurrently from parlay::parallel_for on an already-built tree; build, batchInsert and batchDelete are internally parallel and presumably must not overlap queries (not stated) |
| **Drop-in for the baseline** | no |

## Gotchas

- The default batchDelete overload assumes every point to delete is in the tree (FullCoveredTag, per the header comment). Use the PartialCoverTag overload when some points may be absent
- The build files disagree with the README: the README lists the CGAL option as default OFF, but CMakeLists.txt sets option(CGAL ON) and calls find_package(Boost REQUIRED) unconditionally. A plain 'cmake ..' therefore fails without CGAL and Boost; pass -DCGAL=OFF or just include the headers
- Tuning knobs (BUILD_DEPTH_ONCE=6, LEAVE_WRAP=32, INBALANCE_RATIO=30) are static constexpr members. The README warns that different values 'on different machine may influence the performance dramatically'
- Benchmark reading: by default the repo's kNN harness (queryKNN in tests/testFramework.h) flattens the tree's own points into the query array inside the timed loop. Queries are therefore the indexed points in tree order, a locality-friendly workload

## Known shortcomings

- Boost baseline is a 2-D bgi::rtree quadratic&lt;2&gt; run sequentially vs 96 cores; CGAL update wins come from CGAL's missing batch insert; repo no longer updated (successor ucrparlay/SpaceTreeLib).
- Claim inflation: the Boost baseline is a sequential 2-D bgi::rtree&lt;quadratic&lt;2&gt;&gt;; the repo kNN harness queries the tree's own points in tree order; kNN is only 1.4-1.8x over CGAL (paper snippet says kNN similar). Repo frozen; successor is PSI-Lib (ucrparlay/SpaceTreeLib). CMake needs CGAL+Boost by default although the README says CGAL is off.
- Per notes in Kiddo's benches/profile_cpp_competitors.rs, Pkd-tree's f32 build aborts on a box-containment assertion from 2^22 points up.

## Caveats and trade-offs

The SIGMOD 2025 paper (doi 10.1145/3709712, arXiv 2411.09275) could not be opened (arxiv.org and cs.ucr.edu blocked), so paper numbers and the CPU model (a search summary says four-way Xeon Gold 6252, 96 cores) are unverified. Comparisons are parallel Pkd-tree against CGAL built with Parallel_tag (TBB) and parallel TBB queries, which is fair for build and query, but CGAL's kd-tree has no batch insert (the harness inserts then rebuilds) and deletes one point at a time, so the huge update ratios reflect a missing CGAL feature. The Boost baseline at HEAD (tests/rtree.cpp) is a 2-D bgi::rtree with quadratic&lt;2&gt; node capacity (a very small node size) built and updated sequentially while Pkd-tree uses all cores; its kNN queries run in a parlay parallel_for. The repo CSVs name no hardware or date. CGAL is slightly faster for one 12-D Varden kNN row. The README says this repository will no longer be updated; the maintained code is ucrparlay/SpaceTreeLib.

Built on ParlayLib (git submodule) for shared-memory parallelism, so wins need many cores; low-dimensional point sets (kNN, range, count queries), not general geometry or polygons. The repo README says Pkd-tree is now integrated into PSI-Lib (github.com/ucrparlay/SpaceTreeLib, MIT, PPoPP 2026 'Parallel Dynamic Spatial Indexes') which adds orth-trees and space-filling-curve indexes.

## Maintenance

Frozen research artifact (the README says it will no longer be updated; last commit 2026-08-20) under MIT; the maintained code is PSI-Lib (ucrparlay/SpaceTreeLib, MIT, PPoPP 2026).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed SIGMOD 2025 paper (PACMMOD 3(1), cited in the README) with public harnesses (tests/cgal.cpp, tests/rtree.cpp, script/run_\*.sh), Release flags -O3 -mcx16 -march=native in CMakeLists.txt and first-party raw results in script/data/\*.csv; the paper could not be opened and no opened page names the CPU model, so not A.
- **Verifier notes:** Kept at B: peer-reviewed venue confirmed via the README citation; opening the paper would likely make it A since code and flags are public. Metadata confirmed on github.com: MIT, 90 stars, 4 forks, last commit 2026-08-20 (README edit). The successor ucrparlay/SpaceTreeLib (PSI-Lib, MIT) is a possible new lead.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment; enrichment (third-party bench notes)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/README.md>
  - <https://github.com/ucrparlay/Pkd-tree>
  - <https://github.com/ucrparlay/Pkd-tree/commits>
  - <https://github.com/ucrparlay/Pkd-tree/tree/main/tests>
  - <https://github.com/ucrparlay/Pkd-tree/tree/main/script>
  - <https://github.com/ucrparlay/Pkd-tree/tree/main/script/data>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/tests/rtree.cpp>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/tests/cgal.cpp>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/script/run_summary.sh>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/script/data/build.csv>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/script/data/summary.csv>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/script/data/knn.csv>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/script/data/insert.csv>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/script/data/delete.csv>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/README.md>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/LICENSE>
  - <https://github.com/ucrparlay/Pkd-tree/tree/main/include>
  - <https://github.com/ucrparlay/Pkd-tree/tree/main/include/cpdd>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/include/cpdd/kdTreeParallel.h>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/include/cpdd/cpdd.h>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/include/cpdd/basic_point.h>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/include/cpdd/batch_op/build_tree.hpp>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/tests/testFramework.h>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/tests/cgal.cpp>
  - <https://raw.githubusercontent.com/ucrparlay/Pkd-tree/HEAD/tests/rtree.cpp>
  - <https://github.com/ucrparlay/Pkd-tree/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/README.md>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/docs/TREE_ANSWER.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ucrparlay/pkd-tree`) · [data/wave8/enrich/raw/github_com_ucrparlay_pkd_tree.json](../../../data/wave8/enrich/raw/github_com_ucrparlay_pkd_tree.json) (enrichment confidence 0.75)

</details>
