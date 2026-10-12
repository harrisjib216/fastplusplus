# kd3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `AGPL-3.0` · 🟢 active

> AGPL header-only C++23 static kd-tree for low-dimensional points (3D default); median 3.7x faster builds and 1.9x faster k-NN than nanoflann.

| | |
|---|---|
| **Beats** | nanoflann (header-only C++ kd-tree) |
| **Claimed result** | README: k-NN queries 'in most scenarios are significantly faster compared to nanoflann'. From the committed CSV (assets/results/5950X/kd3_datasets_report.csv, 132 rows, ratios derived from page data): median build 3.7x faster (range 0.22x-6.42x); median query throughput 1.86x of nanoflann (range 0.01x-5.05x); aabb and fast-aabb configs about 1.7x-2.9x median, on-cloud queries with the fast config up to 5.05x. Example row: autzen, 5M points, k=10, on-cloud: 511,698 vs 295,318 queries/s, build 0.086 s vs 0.416 s. |
| **Workload** | kd-tree build time and k-NN query throughput (k=1 and k=10, 100,000 queries) on 11 point-cloud datasets (autzen LiDAR, bunny, dragon, cities, synthetic blobs, sphere shell, torus, solid, anisotropic, powerlaw, mixture) in four kd3 configurations (base, aabb, fast, fast-aabb), validated against brute force. |
| **Metric** | throughput |
| **Hardware** | Workstation with a '5950X' CPU (results directory name; exact model and thread count not stated) |
| **Compiler and flags** | Compiler not stated. xmake release mode set_optimize('fastest'); the 'native' option (default true in xmake.lua at HEAD) adds -march=native -ffast-math to benchmarks.comparative, so kd3 and nanoflann are built with the same flags in one binary. README recommends profile-guided optimization. |
| **Adoption** | 11 stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/KaruroChori/kd3) · [benchmark](https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/assets/results/5950X/kd3_datasets_report.csv) |

## Verdict

The author's comparative benchmark (benchmarks.comparative.cpp: 100,000 queries per row, one timed pass, every row checked against brute force) ran on a '5950X' workstation with an unstated compiler, built for both libraries with xmake's 'fastest' optimisation plus -march=native -ffast-math. kd3's build is a median 3.68x faster than nanoflann's (leaf size 10, same OpenMP thread count), and its single-threaded query throughput a median 1.86x higher across 132 rows on 11 datasets. 39 rows are slower than nanoflann, mostly base or fast configurations on volume queries; the has_aabb configurations (aabb and fast-aabb, 66 rows) are slower in only 9.

## Use it when

- Static 2-4D point clouds (LiDAR tiles, scanned meshes, surflets for SDF raymarching) with 10^5-10^7 points, queried at high rates for 1-NN or small-k k-NN.
- Queries that lie on or near the data, such as k-NN graphs, ICP-style correspondence or jittered samples: the 5950X CSV shows on-cloud k=10 with the base config at a median 1.73x nanoflann and 1-NN at 2.21x.
- Queries spread through empty space, provided you enable has_aabb: aabb configurations reach a median 1.68x (k=10) and 2.23x (1-NN) on bbox-volume queries, where the base config loses.
- Pipelines that rebuild the tree often on many cores: OpenMP task build, median 3.7x faster than nanoflann given the same thread count.
- Ray, cylinder or nearest-distance queries that must also run in a shader (GLSL generator) or from C via kd3-c.h, and AGPL-3.0 (or a negotiated licence) is acceptable.

## Skip it when

- Closed-source or SaaS products without a separate licence from the author: AGPL-3.0-only network copyleft.
- Base or fast configurations with queries spread through the volume: in the CSV they are slower than nanoflann in 10 of 11 (k-NN base), 9 of 11 (1-NN base) and 8 of 11 (1-NN fast) datasets, down to 0.013x on synthetic-anisotropic 1-NN.
- Small clouds where build time matters: on bunny (35,947 points) every kd3 configuration builds slower than nanoflann (about 11.4 ms vs 2.5 ms for base, 0.22x).
- Radius or range search, dynamic insert/delete, high-dimensional data (&gt;4D), or compilers without C++23 (std::expected, std::span): kd3 offers only 1-NN, k-NN, nearest distance and ray queries on a static tree; nanoflann or Pkd-tree (batch updates) fit those cases better.
- Projects needing a mature, widely deployed library: 11 stars, 38 commits, first stable release July 2026.

## How it is fast

Leaves are fixed-size buckets stored structure-of-arrays (coords[D][leaf_size], aligned to the SIMD width), so distances are computed for a whole bucket in vectorizable loops; the default leaf size is 4x the detected SIMD lane count (32 floats on AVX2). Internal nodes are an implicit array of split values with split dimensions bit-packed into 64-bit words, and the tree size is fixed up front from n / leaf_size, so the build is std::nth_element median partitioning into preallocated arrays, run as OpenMP tasks above 10,000 points. Queries use a bounded stack (96 entries) with no heap allocation. The optional has_aabb stores a tight box per subtree, so queries far from the data prune whole subtrees, and has_payload = NONE drops ids for a distance-only 1-NN path.

## Compared with alternatives

Over nanoflann and PicoTree when the data is 3D, static and queried far more often than rebuilt, you can enable has_aabb, and AGPL is acceptable; otherwise nanoflann or PicoTree (also catalogued, about 2.6x faster builds than nanoflann) are the safer defaults, and Pkd-tree fits when you need parallel batch updates. Unlike Janos95/kdtree, kd3 checks every benchmark row against brute force.

## Integration

| | |
|---|---|
| **Form** | header-only (include/kd3/\*.hpp); optional static lib and STB-style C interface (kd3-c.h); xmake package, and release tarballs of the headers |
| **Dependencies** | C++ standard library (nth_element, sort, vector, span, expected) and OpenMP (or the author's omp-stub for serial builds); the benchmarks additionally need nanoflann and LASlib/lastools |
| **Minimum toolchain** | C++23 (xmake set_languages cxx23/c23); README notes GCC 15/16 miscompile at -O2 (see gotchas) |
| **Platforms** | any C++23 target; SIMD width auto-detected (AVX-512, AVX/AVX2, SSE2/SSE4.2, or std::simd), override with KD3_SIMD_PARALLELISM; built for -march=native by default, so no binary releases |
| **Thread safety** | not documented; queries are const noexcept on an immutable view, so concurrent queries on a built tree look safe (inferred from source), and the build itself is OpenMP-parallel |
| **Drop-in for the baseline** | partial — covers nanoflann's static-index KNN (k-NN and 1-NN) for low-dimensional float points, but with a different API (FatPoint arrays and payload ids instead of a dataset adaptor), no radiusSearch, no dynamic index, and it reorders the input |

## Gotchas

- The headline 5.05x maximum comes from the 'fast' configuration (has_payload = NONE, query_distance2_inline), which returns only the nearest squared distance and not which point, while nanoflann's figure includes the index; compare against the base or aabb rows for like-for-like k-NN.
- The default leaf_size and bucket alignment follow the compile-time SIMD width (and KD3_SIMD_PARALLELISM is #undef'd after use), so the memory layout of a 'memory-mapped' tree depends on the flags it was built with; the C header hard-codes KD3_LEAF_SIZE 32 with a TODO.
- The README's known issue: GCC 15 and 16 at -O2 can emit an aligned movaps to an unaligned address in Builder::build's leaf-fill loop, crashing on tiny trees; the author attributes it to a compiler bug.
- The benchmark and the release builds use -ffast-math with -march=native (xmake 'native' option, on by default); to reproduce the nanoflann comparison you must configure with both --with_evaluation=true and --with_demo=true, because KD3_BENCH_NANOFLANN is only defined under with_demo, although docs/benchmarking.md shows only the first flag.

## Known shortcomings

- 39 of 132 rows slower than nanoflann; nanoflann left at leaf size 10 vs kd3's tuned 32; single pass; compiler unstated. The README ends with text instructing readers (and AI summarizers) to call it slow and omit that from summaries, a prompt-injection attempt.
- The 5.05x maximum is the 'fast' configuration (distance-only, no index), not like-for-like with nanoflann. Build is slower than nanoflann on small clouds (bunny 36k, 0.22x). nanoflann rows also need --with_demo (KD3_BENCH_NANOFLANN gated), which the docs omit. README notes a GCC 15/16 -O2 miscompile; leaf layout depends on SIMD flags. AGPL-3.0.

## Caveats and trade-offs

Mixed result: 39 of 132 CSV rows are slower than nanoflann, mostly the 'base' and 'fast' configurations on bbox-volume queries (medians about 0.37x and 0.61x, worst 0.01x on synthetic-anisotropic 1-NN), which is why the aabb configurations exist. Each configuration is timed in a single pass (no repetitions). nanoflann uses leaf size 10 (its default) against kd3's tuned leaf size 32; build threads are matched (nanoflann gets omp_get_max_threads()), queries are single-threaded for both. Compiler and exact CPU are not stated, no independent reproduction. Very young repo with 11 stars. Baseline nanoflann is not Boost.Geometry/CGAL/GEOS. AGPL-3.0 (network copyleft) limits embedding in closed products.

Header-only, small key dimension (2-4 ideal), SoA SIMD leaves, OpenMP build, zero-allocation traversal, non-owning view suitable for GPU offload, C API, GLSL generator. AGPL-3.0 network copyleft limits use in closed products. Not the most complete or flexible kd-tree library.

## Maintenance

Active (v1.3.1 on 2026-09-23, five releases since July 2026) but young and small; AGPL-3.0, so copyable only into AGPL-compatible projects, with a different licence available from the author on request.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party CSV (assets/results/5950X/kd3_datasets_report.csv) from public benchmark code (benchmarks/benchmarks.comparative.cpp, xmake target benchmarks.comparative) against nanoflann, but the compiler is not stated and the CPU is identified only by a directory name ('5950X'), so not A.
- **Verifier notes:** All numbers in claimed_speedup re-derived from the CSV and match (132 rows; build median 3.68x, range 0.22x-6.42x; query median 1.86x, range 0.01x-5.05x; autzen 5M k=10 on-cloud row exact). License file is LICENCE.txt (AGPL-3.0), last commit 2026-09-23, 11 stars, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/README.md>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/assets/results/5950X/kd3_datasets_report.csv>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/docs/benchmarking.md>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/xmake.lua>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/benchmarks/benchmarks.comparative.cpp>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/LICENCE.txt>
  - <https://github.com/KaruroChori/kd3>
  - <https://github.com/KaruroChori/kd3/commits>
- **Sources the enricher read:**
  - <https://github.com/KaruroChori/kd3>
  - <https://github.com/KaruroChori/kd3/releases>
  - <https://github.com/KaruroChori/kd3/tree/master/include/kd3>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/README.md>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/docs/benchmarking.md>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/xmake.lua>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/benchmarks/benchmarks.comparative.cpp>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/assets/results/5950X/kd3_datasets_report.csv>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/LICENCE.txt>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/include/kd3/kd3.hpp>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/include/kd3/query.hpp>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/include/kd3/build.hpp>
  - <https://raw.githubusercontent.com/KaruroChori/kd3/HEAD/include/kd3/kd3-c.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/karurochori/kd3`) · [data/wave8/enrich/raw/github_com_karurochori_kd3.json](../../../data/wave8/enrich/raw/github_com_karurochori_kd3.json) (enrichment confidence 0.8)

</details>
