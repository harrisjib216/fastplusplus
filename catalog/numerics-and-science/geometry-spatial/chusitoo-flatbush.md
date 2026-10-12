# chusitoo/flatbush (C++ port of Flatbush)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++11 port of the Flatbush packed Hilbert R-tree for static 2D boxes; no measured head-to-head win over any baseline.

| | |
|---|---|
| **Beats** | Flatbush JavaScript original (mourner/flatbush, Node v24) |
| **Claimed result** | No speedup claim on the page. C++ README table (i7-1185G7, bench.cpp): index 1000000 rectangles 55ms (clang 18.1.3), 59ms (gcc 13.3.0), 72ms (cl 19.29); 1000 searches 10%: 79/80/91ms; 1000 searches 1%: 17/18/18ms; 1 search of 1000000 neighbors: 88/86/63ms. JS original README (M1 Pro, Node v24): index 1,000,000 rectangles 109ms; 100 searches 10% area 64ms; 1000 searches 1% area 66ms; 1 search of 1,000,000 neighbors 84ms. Cross-CPU ratios (derived from page data, not like-for-like): index build 109/55 = about 2.0x; 1000 searches 1% about 3.7x (66/18); 1M-neighbor kNN about 1.0x or slower with gcc/clang. |
| **Workload** | Packed Hilbert R-tree: index 1,000,000 rectangles, 1000 bounding-box searches at 10%/1%/0.01% area, k-nearest-neighbour searches (same cases as the JS bench.js). |
| **Metric** | throughput |
| **Hardware** | Intel i7-1185G7 @ 3.00GHz, Win11 25H2 / Ubuntu 24.04.2 LTS (C++ numbers); Apple M1 Pro, Node v24 (JS numbers at https://github.com/mourner/flatbush) |
| **Compiler and flags** | clang 18.1.3, gcc 13.3.0, cl 19.29.30159; CMake WITH_BENCHMARKS forces CMAKE_BUILD_TYPE Release (CMake defaults, explicit -O/-march flags not stated in the README); SIMD level used for the table not stated (SSE2 default on x64, AVX/AVX2/AVX512 selectable); bench uses Google Benchmark fetched at build time |
| **Adoption** | 25 stars; on Conan Center and vcpkg |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/chusitoo/flatbush) · [benchmark](https://github.com/chusitoo/flatbush/blob/HEAD/bench.cpp) |

## Verdict

The repo makes no speedup claim; its README table reports only its own Google Benchmark timings on an i7-1185G7 (clang 18.1.3 / gcc 13.3.0 / MSVC 19.29, CMake Release, SIMD level unstated): index 1M rectangles 55-72 ms, 1000 searches at 1% area 17-18 ms, 1 search of 1M neighbours 63-88 ms. Comparing with the JS original's README (M1 Pro, Node v24) gives only cross-machine directional ratios (about 2x on build, about 3.7x on 1% searches, none on the 1M-neighbour kNN).

## Use it when

- Read-mostly 2D datasets (map features, tiles, bounding boxes of shapes) that are built once and queried many times, from thousands to millions of items.
- Sharing or memory-mapping a prebuilt index, including indexes produced by the JavaScript Flatbush, without a copy (fromView on an aligned buffer).
- Projects that want a single header with no dependencies and C++11 support, installable from Conan Center or vcpkg.
- Range queries returning few hits (the README's 1000 searches at 0.01% area take 2 ms total on an i7-1185G7) and small-k nearest-neighbour lookups.

## Skip it when

- Data that changes after building: there is no insert or delete; any change means a full rebuild.
- 3D or higher-dimensional data, or non-box geometry predicates (polygons, segments): it indexes 2D axis-aligned boxes only.
- Choosing on proven speed over Boost.Geometry rtree, nanoflann or GEOS STRtree: the repo benchmarks only itself and publishes no comparison with any C++ or JS baseline.
- Very large single kNN result sets: the README's 1 search of 1,000,000 neighbours takes 86-88 ms with gcc/clang, no better than the JS original's 84 ms on a different machine.
- Inputs above uint32 item counts: numItems is stored as uint32_t and the builder throws std::length_error past the format limits.

## How it is fast

Items are sorted by the Hilbert-curve value of their box centres (quantized to a 16-bit grid) and packed bottom-up into a fixed-fanout tree (default node size 16) stored in one flat array, so there are no per-node allocations or pointers. The build uses a custom partial quicksort that only orders items down to node granularity, plus a bucket pass, and computes Hilbert indices with SIMD (SSE2 up to AVX-512, chosen at compile time). Queries test node boxes with SIMD comparisons, prefetch child nodes, and kNN uses a priority queue over node distances.

## Compared with alternatives

Pick it over the JavaScript Flatbush when the consumer is C++ (the formats are interchangeable), and over nanoflann or tidwall/rtree.c when you need a static box index (not just points) with zero-copy loading of a prebuilt buffer. If you need updates, 3D or measured speed against Boost.Geometry, GeoToolbox KdBoxTree, PH-tree or nanoflann have published comparisons and this does not.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (Google Benchmark, GoogleTest and fuzztest are fetched by CMake only for benchmarks and tests) |
| **Minimum toolchain** | C++11 (uses std::span automatically in C++20); README table built with clang 18.1.3, gcc 13.3.0 and MSVC 19.29 |
| **Platforms** | any C++11 target; SIMD paths for x86/x86-64 (SSE2 default on x64, SSE3/SSSE3/SSE4/AVX/AVX2/AVX-512 by compiler flags) with a scalar fallback elsewhere; a 32-bit compile failure was fixed in issue #14 (closed 2026-09-25) |
| **Thread safety** | not documented; search() and neighbors() are const and the header declares no mutable members, so concurrent queries on a built index look safe (inferred from source, not stated); the builder is not shared-safe |
| **Drop-in for the baseline** | partial: same serialized format and near-identical API to the JavaScript Flatbush, but not a drop-in for any C++ spatial index |

## Gotchas

- Errors are reported with exceptions (std::invalid_argument, std::length_error): wrong template type for a buffer, misaligned fromView buffer, empty builder, oversized index. Builds with -fno-exceptions need care.
- The SIMD level is fixed at compile time from compiler flags (#pragma message prints which one); the default on x64 is only SSE2, so pass -mavx2 or /arch:AVX2 for the faster paths, and keep the same flags and FLATBUSH_SPAN setting across translation units.
- Integer coordinate types had a SIMD bug: updateBounds stored only the minimum values (issue #9, closed 2026-06-27), corrupting node boxes so queries missed items; use a release after that fix if you index int types. Earlier issues: a multiple-definition link error (#2) and search/neighbors not compiling on 32-bit targets (#14), both closed.
- A custom distance callback must return a lower bound of the point-to-box distance, and it bypasses the SIMD path; fromView requires the buffer to outlive the index and stay unchanged.

## Known shortcomings

- Downgraded C to D: bench.cpp runs no baseline, and the only comparison is two README tables on different CPUs (i7-1185G7 vs M1 Pro); the matching 1M-neighbour kNN row has C++ at 86/88 ms (gcc/clang) against JS 84 ms, so no win is shown. Kept as a separate C++ entry cross-referenced to mourner/flatbush (JS, not callable from C++).
- Issue #9: the SIMD updateBounds stored only min values for integer coordinate types, so queries missed items (closed 2026-06-27; the README bench uses double, so its numbers are unaffected). Issues #2 (multiple definition) and #14 (32-bit compile) also closed.

## Caveats and trade-offs

No head-to-head against any baseline: bench.cpp benchmarks only this library (BM_Index1M, BM_Search10Percent, BM_Search1Percent, BM_Search001Percent, BM_Neighbors100, BM_NeighborsAll, BM_Neighbors1). The only cross-implementation comparison is derived by reading two README tables measured on different CPUs and OSes (i7-1185G7 vs Apple M1 Pro), and the JS table uses a different search mix (100 searches at 10% vs 1000), so it is directional; the matching 1M-neighbor kNN row shows no win for gcc/clang. Author says benchmarks are based on the original bench to allow a close comparison. A search snippet of the project page shows older numbers (93ms clang 10.0.0), so the tables were rerun over time; per-commit runner history is on chusitoo.github.io (blocked here). No comparison with Boost.Geometry rtree, CGAL, GEOS or nanoflann. C++ port of mourner/flatbush (ISC), which is already in the catalog; the port itself is MIT.

Static index: build once, no insert/delete after finish(). Header-only C++11, optional std::span, SIMD box tests, zero-copy fromView on aligned buffers, serialized layout compatible with the JS library.

## Maintenance

Actively maintained (last commit 2026-10-03, 161 commits, CI with unit, fuzz, CodeQL and benchmark jobs), MIT-licensed single header, packaged on Conan Center and vcpkg; evidence tier D because nothing is measured against a baseline.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now D.
- **Tier reason:** The README table numbers are real (bench.cpp, Google Benchmark, CMake Release on i7-1185G7), but neither the README nor bench.cpp runs any baseline: no JS Flatbush, Boost.Geometry, CGAL, GEOS or nanoflann. The only comparison is reading two README tables measured on different CPUs and OSes with partly different search mixes, which measures no speedup, and on the one matching kNN row (1 search of 1,000,000 neighbors) the C++ gcc/clang figures (86/88ms on i7-1185G7) are not faster than JS (84ms on M1 Pro), so the claim is directional only.
- **Verifier notes:** Metadata checked: MIT (LICENSE file; the WebFetch summary's 'ISC' refers to the JS original), 25 stars, 5 forks, not a fork, not archived, 161 commits, last commit 2026-10-03 (active), on Conan Center and vcpkg. Fold-or-keep: it is a port of the listed mourner/flatbush, but that entry is JavaScript and not callable from C++; given the C++-first catalog, I recommend keeping it as a separate C++ entry (the actual artifact a C++ user would adopt) with a cross-reference to mourner/flatbush, rather than folding it as a duplicate. Downgraded to D on evidence, not rejected; keep-and-document applies.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `benchmark_url`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/chusitoo/flatbush>
  - <https://github.com/chusitoo/flatbush/commits>
  - <https://raw.githubusercontent.com/chusitoo/flatbush/HEAD/README.md>
  - <https://raw.githubusercontent.com/chusitoo/flatbush/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/chusitoo/flatbush/HEAD/bench.cpp>
  - <https://raw.githubusercontent.com/chusitoo/flatbush/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mourner/flatbush/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/chusitoo/flatbush/HEAD/README.md>
  - <https://raw.githubusercontent.com/chusitoo/flatbush/HEAD/bench.cpp>
  - <https://raw.githubusercontent.com/chusitoo/flatbush/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chusitoo/flatbush/HEAD/flatbush.h>
  - <https://github.com/chusitoo/flatbush/issues?q=is%3Aissue>
  - <https://github.com/chusitoo/flatbush/issues/9>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/chusitoo/flatbush`) · [data/wave8/enrich/raw/github_com_chusitoo_flatbush.json](../../../data/wave8/enrich/raw/github_com_chusitoo_flatbush.json) (enrichment confidence 0.7)

</details>
