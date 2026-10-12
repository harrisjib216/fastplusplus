# Janos95/kdtree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🔴 abandoned

> Tiny 2020 Magnum/Corrade 3D kd-tree with 1-NN only; build \~15% faster than nanoflann, query claim invalidated by a pruning bug.

| | |
|---|---|
| **Beats** | nanoflann |
| **Claimed result** | README: construction about 15 percent faster than nanoflann. The README's 'nearest neighbor query about 10 percent faster' is invalid: the search over-prunes (linear gap vs squared distance) and returns wrong neighbours, and benchmark.cpp never checks results. |
| **Workload** | benchmark.cpp: 1,000,000 uniform random 3D float points in [-1,1]^3; tree construction timed 10 times; 10,000 random single nearest-neighbour (k=1) queries, each wrapped in its own ScopedTimer; nanoflann KDTreeSingleIndexAdaptor with max leaf size 10 as the comparison. |
| **Metric** | build-time |
| **Adoption** | 11 stars |
| **Last commit** | 2020-06-18 |
| **Links** | [repository](https://github.com/Janos95/kdtree) · [benchmark](https://github.com/Janos95/kdtree) |

## Verdict

The README reports, from the author's own measurements, about 15% faster construction and about 10% faster 1-NN queries than nanoflann (KDTreeSingleIndexAdaptor, max leaf size 10) on 1,000,000 uniform random 3D float points with 10,000 queries; no timings, compiler, flags or CPU are published. The construction comparison stands as a first-party claim, but the query comparison is not like-for-like, because the kd-tree's query is inexact.

## Use it when

- Reading a short (about 170-line) median-split kd-tree to learn the technique, for example the bounding-box-trimmed recursion.
- Already on Magnum/Corrade and wanting a zero-copy index over a strided vertex attribute (the demo builds it straight from a mesh's Position attribute).
- One-shot 3D tree builds where only construction time matters and you will write your own query code.

## Skip it when

- Any case that needs exact nearest neighbours as written: in this session's pure-Python port of kdtree.h's construct and query logic (uniform [-1,1]^3, as in benchmark.cpp), 338 of 1,000 queries over 20,000 points and 88 of 200 queries over 100,000 points returned a non-nearest point; squaring the plane gap fixed all of them.
- Projects without Magnum/Corrade: the header pulls in Magnum Math and Corrade Containers and only accepts Magnum vector types.
- k-NN, radius or range queries, dynamic insert/delete, or high dimensions: only single nearest-neighbour search exists.
- Production or closed-source use: no LICENSE file, so by default all rights are reserved; 9 commits, all from June 2020, no releases, no tests.

## How it is fast

Construction is a classic median-split kd-tree: an index array is partitioned recursively with std::nth_element on the axis depth % dim, and each node (three int32 fields) holds exactly one point, so there is no leaf bucket and no point copy. Queries recurse near-side first, prune a subtree when the squared distance from the query to its trimmed bounding box exceeds the best so far, and use a splitting-plane test to decide whether to visit the far side. That plane test compares the linear gap |p[cd] - q[cd]| with the squared best distance, which over-prunes whenever distances are below 1, so part of the measured query speed comes from skipping subtrees an exact search must visit.

## Compared with alternatives

Rarely: nanoflann, PicoTree, picoflann and kd3 (all catalogued) have exact k-NN and radius search, licences and wider use; pick this only as a Magnum-native teaching example, and fix the plane-prune comparison before trusting its results.

## Integration

| | |
|---|---|
| **Form** | header-only (kdtree.h); the benchmark and demo build with CMake |
| **Dependencies** | Magnum and Corrade (Math, Containers); the benchmark also needs nanoflann (git submodule) and a scoped_timer subdirectory; the demo app needs Magnum SDL2Application, GL, SceneGraph, Shaders, Trade, MeshTools, Primitives and MagnumPlugins AssimpImporter |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17; uses if constexpr and a class template deduction guide), CMake 3.16 |
| **Platforms** | Any platform Magnum supports; no SIMD or architecture-specific code; benchmark.cpp's doNotOptimize uses GCC/Clang inline asm |
| **Thread safety** | not documented; nearestNeighbor is a non-const member but only reads tree state, and the tree keeps a non-owning view of the caller's points |
| **Drop-in for the baseline** | partial — replaces only nanoflann's k=1 knnSearch on 3D Magnum vectors; different API (no adaptor class, no k-NN or radius search, no leaf-size parameter), and its query results are not exact (see gotchas) |

## Gotchas

- Query correctness bug in recurse(): the far-side test 'if (p[cd] - q[cd] &lt; result.distanceSquared)' (and its mirror) compares a linear distance with a squared one. For point sets in the unit range, where best squared distances are well below 1, far subtrees that may contain the true nearest neighbour are skipped, so nearestNeighbor returns wrong answers and the '10 percent faster' query claim compares an inexact search with nanoflann's exact one.
- benchmark.cpp never checks that KDTree and nanoflann return the same neighbour, which is how the bug went unnoticed; it also wraps each of the 10,000 queries in its own ScopedTimer, so timer overhead is part of every query sample.
- The tree stores a non-owning StridedArrayView of the points: the caller must keep the point buffer alive and unchanged for the tree's lifetime.
- The header does 'using namespace Magnum; using namespace Corrade;' at global scope, which leaks into every file that includes it; an empty point set leaves NNResult.pointIndex uninitialized.

## Known shortcomings

- No license; benchmark.cpp (1M random 3D points, 10k 1-NN queries vs nanoflann) has no published results.
- Correctness bug: recurse() decides on the far child with the linear gap p[cd]-q[cd] compared against a squared distance, over-pruning when distances are below 1; an independent port gave 338/1000 wrong nearest neighbours at 20k points and 88/200 at 100k (uniform [-1,1]^3), and squaring the gap fixes all. benchmark.cpp never checks results, so the 10% faster query claim timed an inexact search and is invalid; the 15% faster build claim stands. No licence.

## Caveats and trade-offs

Two-sentence README claim from 'my measurements'; benchmark.cpp (1M uniform random 3D points, 10k 1-NN queries, nanoflann leaf size 10) exists but no results, hardware, compiler or flags are published, and per-query timing with a scoped timer adds overhead to both sides. Tied to Magnum/Corrade types. No LICENSE file (LICENSE, LICENSE.txt, LICENSE.md, COPYING all 404; no licence header in kdtree.h), so reference only. nanoflann is not a listed incumbent here.

Lightweight kd-tree on top of Magnum/Corrade; does not copy the point cloud (takes a strided view).

## Maintenance

Abandoned since June 2020 (9 commits, 11 stars, no issues or releases) and unlicensed, so reference only; the construction code is a fine small example, but the query code needs its prune fixed before use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README states 'about 15 percent faster' build and 'about 10 percent faster' query vs nanoflann from the author's own measurements; benchmark.cpp in the repo times both, but no output, CPU, compiler or flags are published, so first-party C.
- **Verifier notes:** Small (11 stars, 9 commits, all June 2020) but has a real side-by-side benchmark file against nanoflann, so tier C rather than D. Metadata (stars, last commit 2020-06-18, no license, not a fork) checked on github.com.
- **Fields the verifier corrected:** `workload`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/Janos95/kdtree>
  - <https://github.com/Janos95/kdtree/commits>
  - <https://raw.githubusercontent.com/Janos95/kdtree/HEAD/README.md>
  - <https://raw.githubusercontent.com/Janos95/kdtree/HEAD/benchmark.cpp>
  - <https://raw.githubusercontent.com/Janos95/kdtree/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Janos95/kdtree/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/Janos95/kdtree/HEAD/kdtree.h>
- **Sources the enricher read:**
  - <https://github.com/Janos95/kdtree>
  - <https://raw.githubusercontent.com/Janos95/kdtree/HEAD/README.md>
  - <https://raw.githubusercontent.com/Janos95/kdtree/HEAD/kdtree.h>
  - <https://raw.githubusercontent.com/Janos95/kdtree/HEAD/benchmark.cpp>
  - <https://raw.githubusercontent.com/Janos95/kdtree/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Janos95/kdtree/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/Janos95/kdtree/HEAD/application.cpp>
  - <https://raw.githubusercontent.com/Janos95/kdtree/HEAD/types.hpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/janos95/kdtree`) · [data/wave8/enrich/raw/github_com_janos95_kdtree.json](../../../data/wave8/enrich/raw/github_com_janos95_kdtree.json) (enrichment confidence 0.8)

</details>
