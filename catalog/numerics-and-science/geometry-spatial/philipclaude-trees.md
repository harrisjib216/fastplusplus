# trees (balanced and left-balanced kd-trees)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> Header-only C++17 kd-trees (balanced and stackless left-balanced) for parallel kNN; builds faster than nanoflann, queries sometimes slower.

| | |
|---|---|
| **Beats** | nanoflann (parallel construction and querying) |
| **Claimed result** | README: 'construction is faster than nanoflann, but querying can be slower'; issue #1 graphs show it faster for small k and nanoflann catching up at about k=100. No numbers in text (graphs only). |
| **Workload** | 3D random points sorted along the z-curve, max 12 points per leaf, kd-tree construction and all-nearest-neighbour queries for varying k, parallel. |
| **Metric** | build-time |
| **Hardware** | Apple M1 Pro (2022 MacBook Pro) |
| **Compiler and flags** | CMakeLists.txt sets -O3 -fPIC -ffast-math -funroll-loops -ffp-contract=fast -DNDEBUG for test/test_kdtree.cpp, which builds both trees and nanoflann; compiler not stated (a commented-out line names g++-13). |
| **Adoption** | 1 star |
| **Last commit** | 2025-06-17 |
| **Links** | [repository](https://github.com/philipclaude/trees) · [benchmark](https://github.com/philipclaude/trees/issues/1) |

## Verdict

Author's issue #1 (Aug 2023, under the earlier name 'mapletrees') compares parallel construction and parallel all-points kNN for k = 10, 50 and 100 against nanoflann on z-curve-sorted random 3D points with 12-point leaves, on a 2022 MacBook Pro with Apple M1 Pro. The results are graphs only: build is faster, and combined build plus query is ahead until nanoflann catches up near k = 100. The flags are -O3 -ffast-math -funroll-loops -ffp-contract=fast, the compiler is not stated, and nanoflann is cloned at HEAD and built with hardware_concurrency threads in the wrapper.

## Use it when

- All-points k-nearest-neighbour queries with small k (roughly 10-50) on millions of 3D points, e.g. Voronoi or Delaunay meshing via the radius-of-security theorem, where build time matters.
- Static point sets that are rebuilt often, so faster parallel construction outweighs slightly slower queries.
- Memory-tight cases: the bucketless left-balanced tree uses one index per point.
- Experiments with stackless, GPU-portable kd-tree traversal (the iterative left-balanced query).

## Skip it when

- Large k (about 100 or more): the author reports nanoflann catching up, and queries can be slower than nanoflann.
- Radius search, dynamic insert/remove or more than 6 dimensions: the README calls radius search experimental and not recommended, I found no radius function in the current kdtree.h, and dim &lt;= 6 is a static_assert.
- Production code that needs support: 1 star, one author, no releases or unit tests (only a benchmark driver), stale since 2025-06-17.
- MSVC builds: the header uses GCC/Clang builtins (__builtin_clz, __builtin_clzll, __builtin_expect).
- Single-nearest queries through NearestNeighborSearch with k = 1: its constructor calls exit(1) unless k &gt; 1 (use the nearest() helper, which searches k = 2 internally).

## How it is fast

Every internal node is itself a data point (the median from std::nth_element along the widest bounding-box extent), and the node stores the point index with the split axis packed into the low 3 bits, so balanced and bucketed left-balanced trees take 3 x sizeof(index_t) per point and the bucketless left-balanced tree only 1 x (README; nanoflann about 3-4 x). The left-balanced layout needs no child pointers and allows a stackless parent-index traversal (after Ingo Wald's work); the balanced query prunes with an incrementally updated point-to-cell box distance. Construction is parallelised by spawning one std::thread per subtree at depth ceil(log2(hardware threads)); the benchmark also pre-sorts points along a Morton (z-order) curve, timed separately and given to both libraries.

## Compared with alternatives

Among catalogued kd-tree siblings, nanoflann is the safer general choice (radius search, dynamic indices, maintained), and PicoTree and Janos95/kdtree also report beating nanoflann. Pick trees only when you want a tiny dependency-free header with parallel construction and a 1-index-per-point layout for small-k all-points kNN, and you can set parallel = false or control input sizes.

## Integration

| | |
|---|---|
| **Form** | header-only (single kdtree.h) |
| **Dependencies** | none for kdtree.h (standard library and std::thread); the benchmark build clones nanoflann, morton-nd and the author's stlext at HEAD |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17) with GCC or Clang builtins; compiler versions not documented |
| **Platforms** | not documented; author benchmarks on an Apple M1 Pro (aarch64) and runs a smaller benchmark in GitHub Actions |
| **Thread safety** | Queries are const and the benchmark runs them concurrently from many threads with per-thread result buffers; construction spawns its own threads. Nothing else is documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Parallel build (options.parallel defaults to true) joins its threads only when the number spawned at depth ceil(log2(hardware_concurrency)) is exactly 2^depth. By my reading of kdtree.h plus a simulation of its split sizes, some inputs spawn fewer: balanced tree, leaf_size 16, 8 threads: n = 136-142; left-balanced with leaves, 8 threads: n = 128-239; bucketless left-balanced, 32 threads: n = 65-125. In those cases the constructor returns while threads still write the tree, the left-balanced constructor then frees its index_ buffer under them, and destroying the tree calls std::terminate on joinable threads. Set options.parallel = false for small or medium inputs.
- Maxima are initialised with std::numeric_limits&lt;coord_t&gt;::min() (the smallest positive value, not the lowest), so on an axis whose coordinates are all negative the split-axis choice and root bounding box are wrong. As far as I can tell this only loosens pruning (results stay correct), but shifting data to positive coordinates avoids it.
- The tree keeps a raw pointer to your coordinate array, which must outlive it and stay unchanged. The point index is stored shifted left by 3 bits (4 for leaf offsets), so uint32_t indices cap out near 2^29 points (2^28 leaf slots); the overflow check is an assert() removed under NDEBUG.
- The balanced KdTree supports only the recursive search: passing NearestNeighborApproach::kIterative hits KDTREE_ASSERT, which calls exit(1) even in release builds.

## Known shortcomings

- Graphs only (plot images unreadable here); flags in CMake (-O3 -ffast-math) but compiler unstated.
- Likely concurrency bug (code reading plus a simulation of split sizes, not compiled or run): the parallel build is on by default and joins its threads only when exactly 2^ceil(log2(hw threads)) are spawned; some n spawn fewer (balanced tree, 8 threads: n 136-142; left-balanced with leaves, 8 threads: n 128-239), so the constructor returns while threads still write the tree, the left-balanced constructor frees index_ under them, and destroying the tree calls std::terminate. k=1 search or kIterative on the balanced tree calls exit(1). Max bounds start at numeric_limits::min() (perf only). README's radius search is not in the current kdtree.h.

## Caveats and trade-offs

Author-run, results as graph images only (issue #1 and CI plots in the README), compiler unstated; author states nanoflann catches up at about k=100 for all-nearest-neighbour queries. nanoflann is cloned at HEAD (depth 1) by CMake, so its version is not recorded. Issue #1 refers to the library by an earlier name, 'mapletrees'. Tiny project (1 star). nanoflann is not a listed incumbent here.

Header-only kd-trees for meshing use: balanced and left-balanced (stackless query) variants; 3 x sizeof(index_t) bytes per point, or 1 x for left-balanced without leaf buckets, vs about 3-4 x for nanoflann per the README.

## Maintenance

Stale (last commit 2025-06-17), 1 star, single author, Apache-2.0; a \~900-line header that is easy to vendor, but treat it as research code and turn off the parallel build for small inputs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Issue #1 (author, Aug 2023) compares parallel construction and k=10/50/100 queries against nanoflann on an Apple M1 Pro, with results only as graph images; the benchmark code (test/test_kdtree.cpp) and flags (CMakeLists.txt) are public but the compiler is not stated, so not A. First-party plotted timings make it C.
- **Verifier notes:** Text on README and issue #1 matches the record's qualitative claim; the plot images could not be read (philipclaude.github.io is blocked here and the issue images are not text), so numbers_found_on_page is null. Metadata: Apache-2.0 LICENSE, 1 star, 1 fork, not archived or a fork, last commit 2025-06-17 (stale).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/philipclaude/trees>
  - <https://github.com/philipclaude/trees/commits>
  - <https://github.com/philipclaude/trees/issues/1>
  - <https://raw.githubusercontent.com/philipclaude/trees/HEAD/README.md>
  - <https://raw.githubusercontent.com/philipclaude/trees/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/philipclaude/trees/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/philipclaude/trees/HEAD/test/test_kdtree.cpp>
- **Sources the enricher read:**
  - <https://github.com/philipclaude/trees>
  - <https://github.com/philipclaude/trees/issues/1>
  - <https://raw.githubusercontent.com/philipclaude/trees/HEAD/README.md>
  - <https://raw.githubusercontent.com/philipclaude/trees/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/philipclaude/trees/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/philipclaude/trees/HEAD/kdtree.h>
  - <https://raw.githubusercontent.com/philipclaude/trees/HEAD/util.h>
  - <https://raw.githubusercontent.com/philipclaude/trees/HEAD/test/test_kdtree.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/philipclaude/trees`) · [data/wave8/enrich/raw/github_com_philipclaude_trees.json](../../../data/wave8/enrich/raw/github_com_philipclaude_trees.json) (enrichment confidence 0.75)

</details>
