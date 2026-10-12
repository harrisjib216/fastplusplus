# PH-tree (phtree-cpp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only PH-tree (bitwise Z-order quadtree) spatial map; about 5x faster inserts than Boost.Geometry's R-tree, slower kNN.

| | |
|---|---|
| **Beats** | Boost.Geometry R-tree (boost::geometry::index::rtree); libspatialindex R-tree also measured |
| **Claimed result** | Insert at 1M entries (CUBE / CLUSTER): points PhTreeMM 2.79M/s vs BoostRT 500k/s and 3.97M/s vs 781k/s (about 5.6x and 5.1x, derived from page data); boxes PhTree3D 1.44M/s vs BoostRT 406k/s and 3.18M/s vs 573k/s (about 3.5x and 5.6x, derived); libspatialindex is slower still. Window queries are mixed: point data at 1M, PhTree3D 314k q/s vs BoostRT 364k q/s on CUBE (Boost 1.16x faster) and 1.35M q/s vs 990k q/s on CLUSTER (PH-tree 1.36x faster), with about 3-4 results per query; with about 100 results per query BoostRT wins (121k vs 84k q/s for PhTreeMM2 on CUBE). Box data at 1M on CUBE: PhTree3D 56.3k q/s vs BoostRT 263.6k q/s (Boost about 4.7x faster). kNN clearly favours Boost: 3D, 1M points, k=1, BoostRT 736k/741k q/s vs PhTree3D 28.4k/54.9k q/s on CUBE/CLUSTER (Boost about 26x and 13x faster, derived from page data). |
| **Workload** | 3D points and boxes, CUBE (uniform) and CLUSTER datasets, 1K to 1M entries: insert, window query (about 3-15 results per query) and kNN, PH-tree vs Boost R-tree vs libspatialindex vs MCXME PH-tree. |
| **Metric** | throughput |
| **Hardware** | 8 x 4600 MHz CPU, L3 12 MiB (model not named in the result files) |
| **Compiler and flags** | GCC 12.1 (insert and window-query runs, 2023-02-01/02) and Clang 14.0.0 (3D kNN run, 2023-03-09; the 10D block is labelled 'GCC 14.0.0'). Built with bazel --config=benchmark, which in the current .bazelrc means opt mode with -O3 -g -mavx -mbmi2 -std=c++17. The result files do not record the flags used at the time. |
| **Adoption** | 37 stars |
| **Last commit** | 2026-03-19 |
| **Links** | [repository](https://github.com/tzaeschke/phtree-cpp) · [benchmark](https://github.com/tzaeschke/phtree-cpp-perf) |

## Verdict

In the author's separate phtree-cpp-perf repo (Google Benchmark, PH-tree 1.4.0 vendored, Feb-Mar 2023, GCC 12.1 and Clang 14, 8 x 4600 MHz CPU with 12 MiB L3, model unnamed), 3D inserts at 1M entries run at 2.79M/s vs 500k/s (points, CUBE) and 1.44M/s vs 406k/s (boxes) against Boost.Geometry's R-tree, about 3.5-5.6x; window queries are mixed and Boost wins box queries (about 4.7x) and 3D kNN (about 13-26x).

## Use it when

- Dynamic point sets with heavy insert/erase/move churn (simulations, game entities, moving objects) where an R-tree's rebalancing costs dominate; author's benchmark shows about 5x Boost R-tree insert throughput at 1M 3D points
- Small window queries returning roughly up to 100 results per query, especially on clustered data (PH-tree 1.36x faster than Boost on 1M CLUSTER points)
- Map semantics on exact coordinates (one value per key, find/count by point) with spatial queries on the same structure
- Moderate dimensionality: the README says it works very well up to about 30 (sometimes 50) dimensions, with a hard limit of 63
- Large datasets (millions of entries) built incrementally rather than bulk-loaded

## Skip it when

- kNN-heavy workloads: in the author's own 3D run Boost's R-tree answers k=1 queries about 13-26x faster at 1M points; there is no kNN for box keys at all (issue #36 open)
- Box (rectangle) data with window queries: Boost R-tree is about 4.7x faster on 1M CUBE boxes in the same benchmark
- Queries returning large result sets (the README says 1000+ results is inefficient; Boost already wins at about 100 results per query)
- Static datasets that can be bulk-loaded once (packed R-trees or kd-trees such as nanoflann build fast and query faster)
- Concurrent access: the README states the implementation does not support concurrency

## How it is fast

The PH-tree (Zaeschke et al., SIGMOD 2014) is a bitwise prefix-sharing 2^DIM-ary trie: each node is a binary hypercube addressed by one bit per dimension, so entries sit in Z-order (Morton) order and a lookup or insert walks at most one path with bit arithmetic, no rebalancing. Insert/erase modify only one node (plus possibly one created or deleted), which is why updates are cheap; relocate() reuses the shared path when an entry moves a short distance. Node entry storage switches by dimension (fixed array_map for DIM&lt;=3, sparse sorted vector up to 8, B+tree beyond), and traversal relies on count-trailing-zeros (TZCNT/BMI2) and AVX, hence the recommended -O3 -mavx -mbmi2. Doubles are mapped to int64 losslessly via their IEEE bit pattern by default.

## Compared with alternatives

Pick PH-tree over GeoToolbox KdBoxTree or nanoflann when the dataset changes constantly (insert, erase, relocate) rather than being bulk-loaded and queried, and over tidwall/rtree.c when you want a typed C++17 map API with up to 63 dimensions; pick nanoflann or Boost's R-tree instead when kNN or box queries dominate.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library (copy include/phtree); Bazel or CMake 3.14 only for tests, examples and benchmarks, which use GoogleTest and Google Benchmark |
| **Minimum toolchain** | C++17; verified with GCC 12, Clang 14, Visual Studio 2022 (CMake) and AppleClang 14 (Bazel) |
| **Platforms** | Linux, Windows, macOS; x86-64 recommended with -mavx -mbmi2 for TZCNT (works without, slower bit iteration); benchmarks do not build on Windows |
| **Thread safety** | not thread-safe: README says the current implementation 'doesn't support concurrency or serialization'; external locking required |
| **Drop-in for the baseline** | no |

## Gotchas

- Map semantics: inserting a duplicate key silently does nothing (the FAQ calls this 'losing updates'); use PhTreeMultiMap or a set as value type
- Iteration order is Z-order on the unsigned bit pattern, so negative coordinates come after positive ones; iterators are invalid after modification except as a hint after exactly one erase()
- Correctness history: a heap-use-after-free in multimap relocate (vector reallocation in a node's sparse map, issue #153) was fixed in 1.6.2; issue #154 (bug, open since Aug 2023) reports a crash in the multimap test with NUM_DUPL=10 where emplace_hint after erase inserts at the wrong location
- Lossy ConverterMultiply can speed indexes up by 10%+ but truncates coordinates; the default IEEE converter is lossless. Values are stored inside nodes, so store pointers for large objects

## Known shortcomings

- Insert \~5x over the Boost R-tree is real, but for 3D kNN Boost is \~13-26x faster (record understated this); the perf repo vendors PH-tree 1.4.0 with 2023 runs and an unnamed CPU.
- Open bug #154: multimap emplace_hint after erase inserts at the wrong location; test crashes with NUM_DUPL=10. Heap use-after-free in multimap relocate (#153) fixed only in 1.6.2. No concurrency support per README; kNN for box keys not implemented (#36).

## Caveats and trade-offs

Benchmark written and run by the PH-tree author in a separate repo (tzaeschke/phtree-cpp-perf, MIT, 0 stars). The phtree-cpp README does not link to it, and it vendors PH-tree C++ 1.4.0, while the library is now at 1.7.0. Results date from February-March 2023. The perf README notes that Boost RT was driven with std::array coordinates (a small slowdown), that the libspatialindex wrapper uses a buffering hack, and that an unexplained libspatialindex bug appears on the WEB dataset. The win is insertion (about 5x over Boost's R-tree). Window queries are mixed and box queries favour Boost; 3D kNN favours Boost by about 13-26x. CPU model not named (8 x 4600 MHz, 12 MiB L3), so not tier A. Fork of Improbable's unmaintained original, now maintained by the original PH-tree developer.

Z-order PH-tree: very fast insert/erase/relocate, scales to millions of entries and higher dimensions; not efficient when queries return 1000+ results; header-only C++17; coordinates go through converters; multimap variants exist.

## Maintenance

Maintained by the original PH-tree author as a fork of Improbable's abandoned repo; last commit 2026-03-19 but the last release is v1.7.0 (GitHub release dated March 2024; CHANGELOG header says 2025) with 14 open issues, so slow-moving; Apache-2.0 and header-only, easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The author's phtree-cpp-perf repo has public benchmark code and raw Google Benchmark output against Boost.Geometry's R-tree, and the insert and window-query figures in the record match the result files. The CPU model is never named ('8 X 4600 MHz', 12 MiB L3), so this is first-party C, not A.
- **Verifier notes:** Numbers checked line by line in results_insert_mm_d.txt, results_insert_mm_box_d.txt, results_query_mm_d.txt, results_query_mm_box_d.txt and results_knn_mm_d.txt. The record understated how badly PH-tree loses kNN to Boost, so I added the figures. Metadata checked on github.com: Apache-2.0, 37 stars, forked from improbable-eng/phtree-cpp, last commit 2026-03-19.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/tzaeschke/phtree-cpp>
  - <https://github.com/tzaeschke/phtree-cpp/commits>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp/HEAD/README.md>
  - <https://github.com/tzaeschke/phtree-cpp-perf>
  - <https://github.com/tzaeschke/phtree-cpp-perf/commits>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp-perf/HEAD/README.md>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp-perf/HEAD/.bazelrc>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp-perf/HEAD/results_insert_mm_d.txt>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp-perf/HEAD/results_insert_mm_box_d.txt>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp-perf/HEAD/results_query_mm_d.txt>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp-perf/HEAD/results_query_mm_box_d.txt>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp-perf/HEAD/results_knn_mm_d.txt>
- **Sources the enricher read:**
  - <https://github.com/tzaeschke/phtree-cpp>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp/HEAD/MODULE.bazel>
  - <https://github.com/tzaeschke/phtree-cpp/tree/master/include/phtree/v16>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp/HEAD/include/phtree/v16/phtree_v16.h>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp/HEAD/include/phtree/v16/node.h>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp/HEAD/include/phtree/v16/iterator_knn_hs.h>
  - <https://github.com/tzaeschke/phtree-cpp/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/tzaeschke/phtree-cpp/issues/153>
  - <https://github.com/tzaeschke/phtree-cpp/issues/154>
  - <https://github.com/tzaeschke/phtree-cpp/releases>
  - <https://raw.githubusercontent.com/tzaeschke/phtree-cpp-perf/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tzaeschke/phtree-cpp`) · [data/wave8/enrich/raw/github_com_tzaeschke_phtree_cpp.json](../../../data/wave8/enrich/raw/github_com_tzaeschke_phtree_cpp.json) (enrichment confidence 0.8)

</details>
