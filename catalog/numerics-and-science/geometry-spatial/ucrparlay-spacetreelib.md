# PSI-Lib / SpaceTreeLib (P-Orth tree, SPaC-tree; also contains the Pkd-tree)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only parallel kd-, orth- and space-filling-curve trees with batch updates; 2-3x faster batch updates than a Zd-tree.

| | |
|---|---|
| **Beats** | Boost.Geometry bgi::rtree (quadratic, sequential); the repo also benchmarks CPAM and Zd-tree, and has a CGAL kd-tree harness (tests/cgal.cpp) |
| **Claimed result** | Ratios derived from page data (real_world.csv 'tot' column, seconds). Read the Boost rows carefully: script/merge_real_world.py maps Boost's '## incre insert full' to Insert/1.0, '## incre insert half' to Insert/0.0001 and '## incre delete half' to Delete/0.0001. So Boost 'Insert 1.0' is n sequential single-point inserts into a quadratic bgi::rtree, and Boost's '0.0001' rows are n/2 single-point inserts or deletes. PSI '1.0' is one parallel batch insert of all n points (a build), and PSI '0.0001' is all n points inserted, or deleted, in 10^4 parallel batches. Whole set: Cosmo50 Boost 414.38 vs P-Orth (OrthTree) 1.899 and SPaC-Z (PTree-Z) 0.8365 (about 218x and 495x); OSM 666.0 vs 4.960 and 2.122 (about 134x and 314x); GeoLife 0.2132 vs 0.00639 and PTree-H 0.00150 (about 33x and 142x). Deletes: Cosmo50 Boost 1482.7 s for n/2 single deletes vs OrthTree 17.85 and PTree-Z 8.463 for all n in batches (about 83x and 175x in total time, with Boost doing half the work); OSM 264.2 vs 14.93 and 7.368 (about 18x and 36x). On GeoLife, Boost's n/2 single deletes take less total time (0.064) than OrthTree (0.089) or PTree-H (0.137) deleting all n. Large range report (RRL), both sides parallel: Cosmo50 Boost 19.25 vs OrthTree 1.738, OSM 8.347 vs 1.128, GeoLife 7.829 vs 0.4466 (about 7-18x). Small range report (RRS) favours Boost: Cosmo50 0.00044 vs OrthTree 0.00082, OSM 0.00026 vs 0.00063, GeoLife 0.00028 vs 0.00086. Boost k-NN columns are not comparable (harness bug, see caveats). Against the third-party parallel Zd-tree in the same harness: SPaC-Z batch updates at 0.01% are about 2.1-3.2x faster (Cosmo50 insert 13.83 vs 5.631, delete 20.66 vs 8.463; OSM insert 16.50 vs 7.906, delete 23.86 vs 7.368), and P-Orth is roughly on par with Zd-tree (0.85-1.6x). The SPaC-Z build is about 2.0-2.8x faster than Zd-tree on Cosmo50 and OSM. On queries, P-Orth beats Zd-tree on large range report (Cosmo50 1.738 vs 2.197) and k=10 uniform k-NN (0.244 vs 0.301), while SPaC trees are much slower on k-NN (Cosmo50 IDU10 PTree-H 1.869, PTree-Z 11.55). Paper (search summary only): P-Orth and SPaC trees beat existing parallel kd-trees and Orth-trees on batch updates, with competitive queries, and SPaC-trees are 2-6x faster than Pkd-trees on updates. |
| **Workload** | Real-world point sets GeoLife (3-D), Cosmo50 (3-D) and OSM (2-D): whole-set build, all n points inserted or deleted in 10^4 batches of 0.01%, k-NN (k=1,10,100) on four query distributions, and range count/report (small/medium/large). Parallel PSI trees and the parallel Zd-tree are compared against a Boost bgi::rtree&lt;quadratic&lt;32&gt;&gt; that is updated one point at a time on one thread and queried in parallel with parlay::parallel_for (script/data/real_world/real_world.csv, from the PPoPP '26 scripts). |
| **Metric** | throughput |
| **Hardware** | CPU model not stated in the repo; docs/ARTIFACT_EVALUATION.md asks for at least 512 GB RAM and preferably more than 128 cores; run scripts use numactl -i all. A search summary of the paper mentions 72 cores with 2-way hyperthreading (unverified, paper blocked). |
| **Compiler and flags** | Clang &gt;= 19 or g++ &gt;= 14 (CMakeLists check); Release -O3; docs/ARTIFACT_EVALUATION.md says the paper numbers were measured with -march=native -mcx16 (PSI_NATIVE_ARCH=ON). The compiler used for the paper runs is not stated. |
| **Adoption** | 10 stars, 734 commits; PPoPP 2026 (doi 10.1145/3774934.3786412) and SIGMOD 2025 artifacts; successor repo of ucrparlay/Pkd-tree |
| **Last commit** | 2026-09-09 |
| **Links** | [repository](https://github.com/ucrparlay/SpaceTreeLib) · [benchmark](https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/script/data/real_world/real_world.csv) |

## Verdict

The repo's PPoPP '26 real_world.csv (times presumably seconds; CPU model and compiler not stated, -march=native -mcx16, many-core machine) compares parallel PSI trees with a Zd-tree implementation, pristine CPAM and a quadratic&lt;32&gt; bgi::rtree. The fairest comparisons are the Zd-tree and CPAM rows, with two limits: the Zd-tree is the authors' own in-repo implementation built on PSI's base_tree (THIRD_PARTY.md), not the original ParGeo code, and the pristine CPAM copy differs from PSI's fork on the k-NN path. SPaC-Z batch updates at 0.01% are about 2-3x faster than that Zd-tree and about 2-3.4x faster than pristine CPAM-Z (derived from page data), and P-Orth matches the Zd-tree on updates while winning k-NN and large range reports. The 134-495x 'build' ratios over Boost compare a parallel build with n single-threaded single-point inserts (Boost's packing bulk-load was timed but dropped from the CSV), the Boost '0.0001' rows do half the work of PSI's, and the Boost k-NN columns use the wrong query points, so only the Boost range-query columns are like-for-like (both parallel; PSI 7-18x faster on large ranges, slower on small).

## Use it when

- Update-heavy 2-D or 3-D point sets on a many-core server where whole batches arrive at once: in the repo's real-world CSV, SPaC-Z inserts all of Cosmo50 in 10^4 batches in 5.6 s vs 13.8 s for the Zd-tree implementation and 19.0 s for pristine CPAM-Z (derived from page data)
- Mixed workloads that need both batch updates and fast k-NN: P-Orth k=10 uniform k-NN on Cosmo50 is 0.244 vs Zd-tree 0.301, while its 0.01% batch deletes total 17.9 s vs 800 s for the Pkd-tree in the same CSV
- Query-heavy or higher-dimensional data (the generator covers 2-16 D): use kd_tree, which the library's own guide recommends for queries and higher dimensions
- Replacing a bgi::rtree that is fed one point at a time from a single thread: the repo's Boost harness shows 134-495x faster whole-set loads, though against Boost's slowest construction path (see verified_claims_summary)
- Research or benchmarking of parallel spatial indexes: it ships baselines (pristine CPAM, a Zd-tree implementation, Boost R-tree and CGAL drivers), a data generator and the PPoPP '26 and SIGMOD '25 scripts

## Skip it when

- Small queries or few cores: Boost's R-tree wins small range reports on all three real-world sets (Cosmo50 0.00044 vs P-Orth 0.00082), and single queries are sequential by design; every win comes from parallel batches
- k-NN-heavy work on SPaC trees: SPaC-Z k=10 k-NN on Cosmo50 takes 11.5 vs 0.24 for P-Orth (about 47x slower), so pick the tree type per workload
- Point-at-a-time updates: the manual calls a loop over insert/erase 'the wrong shape'; orth_tree also does not grow its bounding box, so inserting outside bounds() is an error
- Boxes, polygons, segments, non-Euclidean metrics or approximate search: points only, Euclidean k-NN and axis-aligned box queries
- Old toolchains, MSVC or a need for stable releases: CMake rejects g++ below 14 and clang below 19, only Linux/x86-64 builds are documented, and issue #1 asked for versioned releases; pin a commit

## How it is fast

Build and batch updates are fork-join parallel on ParlayLib. kd_tree and orth_tree build a multi-level skeleton at once (default skeleton height 6, so 64 buckets per round), sieve points into the buckets in parallel blocks, recurse in parallel (serial below 1024 points, 32-point leaves) and rebuild only subtrees whose weight balance passes an imbalance ratio of 30%. The orth tree splits at spatial midpoints in every dimension per level (2^d children), so a batch update never has to re-pick splitters. p_tree sorts points by Morton (libmorton) or Hilbert code with a sample sort and stores them in a heavily modified fork of CPAM (a parallel augmented, blocked balanced tree with bounding-box augmentation), so batch insert and delete are CPAM multi_insert/multi_delete on a 1-D key.

## Compared with alternatives

Pick PSI over its predecessor Pkd-tree (ucrparlay/Pkd-tree, frozen) for new work: it contains the same kd-tree plus orth and SPaC trees, which handle small-batch updates far better. Pick nanoflann or PicoTree for single-threaded, static k-NN with no ParlayLib or C++20 requirement, and ArborX for GPU or Kokkos batched queries over boxes and other geometry.

## Integration

| | |
|---|---|
| **Form** | header-only (include/psi) with ParlayLib and libmorton as git submodules; CMake target PSI::PSI or find_package(PSI) |
| **Dependencies** | ParlayLib and libmorton (submodules, MIT); vendored CPAM fork (MIT) and a Rice University Hilbert-curve file that requires an attribution notice. Boost (bgi R-tree driver), CGAL+TBB (correctness oracles, CGAL=OFF by default) and jemalloc are only for benchmarks |
| **Minimum toolchain** | C++20; CMake 3.15+; g++ 14+ or clang 19+ (enforced by CMakeLists.txt) |
| **Platforms** | Linux x86-64 documented; PSI_NATIVE_ARCH=ON by default adds -march=native and -mcx16 (x86 only, and the binary will not run on other CPUs; turn it off for portable builds). Other platforms not documented |
| **Thread safety** | Manual: queries do not mutate the tree, so many can run at once (parallelise them yourself with parlay::parallel_for); build, batch updates and flatten are internally parallel and must not run concurrently with anything |
| **Drop-in for the baseline** | partial — the manual gives a bgi::rtree to PSI mapping table, but PSI stores points only, has no query predicates or lazy iterators, writes results into caller buffers or returned sequences, and trees are move-only |

## Gotchas

- batch_delete requires every point to be present; use batch_diff when some may be absent. In p_tree, points are identified by their id field, so every point needs a distinct id
- Results from knn(point, queue) are references into tree-owned storage and dangle after any update; knn(point, k) returns copies. range_query into a too-small buffer silently truncates and returns the written count
- PSI's -O3 and -march=native apply only to PSI's own targets: the manual warns that an unoptimised consumer build makes the index 'look broken rather than slow'. The orth tree's skeleton height must be a multiple of the dimension (static_assert)
- The README says the code was refactored with AI help after the papers and some indexes are 'slightly affected'; commit af67b82 is the original design. bounds() is a loose bound after batch deletes (except in p_tree)

## Known shortcomings

- Boost harness bugs: kNN queries the wrong points (ignores the query set; 3-D uses only x,y); the merge script mislabels Boost's n/2 single-point inserts/deletes as 0.01% batches; the 218-495x 'build' figures compare against one-at-a-time inserts (the Boost bulk loader is timed but dropped). Boost queries run in parallel and win small ranges. Against the fair rival Zd-tree, SPaC-Z is 2.1-3.2x faster on batch updates. Contains the archived Pkd-tree (catalogued separately).
- The Zd-tree it is compared against is the authors' own in-repo rewrite on PSI's base_tree (THIRD_PARTY.md), not ParGeo's code, so the 2-3x over Zd-tree is weaker than a third-party comparison. Boost also wins small range queries.

## Caveats and trade-offs

The Boost baseline harness (tests/boost_rtree.cpp) has three problems. (1) Its k-NN loop (run_rtree_knn) ignores the query set it is given and queries wp[0..batch_size) for all four distributions, building each query point from only pnt[0] and pnt[1], so 3-D data sets (Cosmo50, GeoLife) get a query point whose third coordinate does not come from the data. The Boost k-NN times are therefore nearly identical across the IDS/ODS/IDU/ODU columns (Cosmo50 k=10: 0.2735, 0.2765, 0.2759, 0.2756) and are not comparable with PSI's. (2) Boost updates are sequential single-point insert/remove, while PSI and Zd-tree use parallel batches; Boost's bulk-loading (packing) constructor is timed as '## build tree half' but merge_real_world.py drops it, so the 134-495x 'build' ratios compare a parallel build with Boost's slowest construction path. (3) merge_real_world.py labels Boost's n/2 single-point insert/delete runs as ratio 0.0001, so those rows do half the work of the PSI rows with the same label. Boost queries run in parallel, so the range-query ratios are parallel against parallel; Boost wins small range reports on all three data sets. Numbers come from the paper-era code: the README says the library was later refactored with AI and some indexes are 'slightly affected' (original design at commit af67b82). The paper (dl.acm.org, cs.ucr.edu, conference-publishing.com) was blocked, so peer review is confirmed from the README citation and search results only. Pkd-tree (kd_tree.h, KdTree rows) is part of this library and is catalogued separately as ucrparlay/pkd-tree; on Cosmo50, Pkd-tree's 0.01% batch deletes total 800.3 s vs 8.46 s for SPaC-Z. include/psi/dependence/space_filling_curve/hilbert.hpp is under a Rice University notice license (attribution notice required); the CPAM fork and the submodules are MIT.

Header-only C++20 on ParlayLib (submodule) and libmorton; needs many cores to win; points only (2-D to 16-D data generator), kd/orth/SPaC trees chosen per update-heavy vs query-heavy use. SPaC trees are built on a permanent fork of CPAM; vendored Hilbert code carries a Rice University notice requirement (THIRD_PARTY.md). A migration table from bgi::rtree is in docs/MANUAL.md. README notes the code was recently refactored with AI help and gives commit af67b82 for the original design.

## Maintenance

Actively maintained (last commit 2026-09-09; 734 commits, 10 stars) MIT research library with CI, docs and a Docker artifact, but no documented release versioning; ship the THIRD_PARTY.md Rice University Hilbert-curve notice with any product.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Stays B on the peer-reviewed PPoPP '26 paper (Parallel Dynamic Spatial Indexes, doi 10.1145/3774934.3786412) with public scripts and raw CSV (script/data/real_world/real_world.csv, tests/boost_rtree.cpp, tests/test_framework.h), plus Zd-tree rows in the same harness. Not A: CPU model and the compiler used for the paper runs are not stated. Verdict is downgrade because the record's Boost claim was overstated.
- **Verifier notes:** Metadata confirmed (MIT, 10 stars, 0 forks, 734 commits, last commit 2026-09-09, not a fork). Shortcomings worth recording: Boost k-NN harness bug (wrong query points), mislabeled Boost update rows, and a 'build' comparison against one-at-a-time insertion rather than Boost's bulk loader. The fair third-party comparison is Zd-tree in the same CSV (SPaC-Z about 2-3x faster on batch updates).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/ucrparlay/SpaceTreeLib>
  - <https://github.com/ucrparlay/SpaceTreeLib/commits/main>
  - <https://github.com/ucrparlay/SpaceTreeLib/tree/main/tests>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/script/data/real_world/real_world.csv>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/README.md>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/docs/ARTIFACT_EVALUATION.md>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/script/merge_real_world.py>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/THIRD_PARTY.md>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/tests/boost_rtree.cpp>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/tests/test_framework.h>
- **Sources the enricher read:**
  - <https://github.com/ucrparlay/SpaceTreeLib>
  - <https://github.com/ucrparlay/SpaceTreeLib/issues?q=is%3Aissue>
  - <https://github.com/ucrparlay/SpaceTreeLib/tree/main/include/psi/orth_tree_impl>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/README.md>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/docs/ARTIFACT_EVALUATION.md>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/docs/MANUAL.md>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/docs/TREE_ANSWER.md>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/THIRD_PARTY.md>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/script/merge_real_world.py>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/script/data/real_world/real_world.csv>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/tests/boost_rtree.cpp>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/include/psi/orth_tree.h>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/include/psi/orth_tree_impl/orth_build_tree.hpp>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/include/psi/p_tree.h>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/include/psi/p_tree_impl/p_batch_insert.hpp>
  - <https://raw.githubusercontent.com/ucrparlay/SpaceTreeLib/HEAD/include/psi/tree_traits.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ucrparlay/spacetreelib`) · [data/wave8/enrich/raw/github_com_ucrparlay_spacetreelib.json](../../../data/wave8/enrich/raw/github_com_ucrparlay_spacetreelib.json) (enrichment confidence 0.75)

</details>
