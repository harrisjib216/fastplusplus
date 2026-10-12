# Contour-Coherent Hausdorff Distance

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only exact discrete Hausdorff distance for ordered 2D contours; 245x faster than Boost.Geometry on similar silhouettes (author's run).

| | |
|---|---|
| **Beats** | Boost.Geometry discrete_hausdorff_distance |
| **Claimed result** | Walking silhouettes: 50.48 ms total package (0.240 ms per HD) vs Boost discrete Hausdorff 12382.56 ms (58.96 ms per HD), stated as approximately 245x faster; also 16.3x faster than brute force with shuffling and 88.9x faster than brute force with early stop. Boost was only run on this package; on unrelated shape sets (Kimia216) the method is only about equal to shuffled brute force. |
| **Workload** | Exact discrete Hausdorff distance between all pairs of ordered image contours (21 related walking silhouettes, 210 pair evaluations), total package time. |
| **Metric** | latency |
| **Compiler and flags** | CMake Release build: Windows preset x64-release (Visual Studio 2026 toolchain, Ninja, vcpkg) or Linux -DCMAKE_BUILD_TYPE=Release with GCC/Ninja. Which toolchain produced the published numbers, and the explicit optimization flags, are not stated. |
| **Adoption** | 1 star |
| **Last commit** | 2026-06-01 |
| **Links** | [repository](https://github.com/Kate-droid-cpu/contour-coherent-hausdorff) · [benchmark](https://github.com/Kate-droid-cpu/contour-coherent-hausdorff) |

## Verdict

On one dataset (21 walking silhouettes, 210 symmetric pairs) the author's benchmark app timed 50.48 ms for the method against 12,382.56 ms for Boost.Geometry discrete_hausdorff_distance (245x). Boost was called with int point_xy linestrings converted on every call, and in a configuration that does a plain O(n\*m) scan. The author's own shuffled brute force is already about 15x faster than Boost there, and the article's headline is 2.2-14.5x over shuffled early break on coherent data, with ties or losses on mixed data. Hardware and the compiler that produced the numbers are not stated.

## Use it when

- Comparing related ordered contours: segmentation masks against ground truth, frame-to-frame tracking contours, a part against a reference outline in inspection, or regression tests of a contour extractor.
- All-pairs Hausdorff over a batch of similar silhouettes, where the author measured 0.24 ms per pair against 3.9 ms for shuffled brute force and 59 ms for Boost.
- Large complex contours (the README's snowflake set has 23k-28k points each) where a fixed-order brute-force early break degrades badly (3.9 ms vs 642 ms per pair).
- When you need an exact result with no extra memory: unlike a kd-tree (OpenCV FLANN in the author's tests was not strictly exact) it builds no index and allocates nothing.

## Skip it when

- Unordered point clouds, or contours with inconsistent sampling or start points that make nearest-neighbour indices jump: the speedup collapses toward brute force with early break, and the worst case stays O(n\*m).
- All-vs-all comparisons of dissimilar shapes: on Kimia216 it only ties shuffled brute force (813.40 vs 812.02 ms) while doing about 2.4x more distance checks.
- 3D meshes or surfaces, or geographic coordinates: it is 2D only and works in float.
- Production code that needs a maintained dependency: it is a 10-commit, 1-star personal project with no tests directory, CI or releases.

## How it is fast

It applies the standard early-break rule for Hausdorff distance: stop scanning targets for a source point once its running minimum is no greater than the current maximum. The new part is the scan order. Each source point's search starts one past the previous point's nearest-neighbour index in the target contour and expands outward bidirectionally (start, start-1, start+1, start-2, ...), so on coherent contours the early break usually fires after a few checks. No spatial index, shuffle buffer or allocation is needed, and squared distances are compared with a single sqrt at the end. The baseline, Boost's discrete_hausdorff_distance, does a plain O(n\*m) scan without early break unless BOOST_GEOMETRY_ENABLE_SIMILARITY_RTREE is defined.

## Compared with alternatives

Use it rather than a kd-tree sibling (nanoflann, PicoTree) when inputs are ordered, similar 2D contours and you want an exact answer with no index build per pair. For unordered or dissimilar point sets, a nanoflann/PicoTree nearest-neighbour Hausdorff (or shuffled early break) is the safer choice.

## Integration

| | |
|---|---|
| **Form** | header-only (single header; the benchmark executable is separate) |
| **Dependencies** | none for the header (standard library only); OpenCV and Boost only for the benchmark app, contour extraction and baselines |
| **Minimum toolchain** | C++17 (structured bindings; benchmark CMake sets CMAKE_CXX_STANDARD 17); built with Visual Studio 2026 on Windows and GCC on Linux/WSL per the README |
| **Platforms** | any (portable scalar C++, no intrinsics) |
| **Thread safety** | Not documented. The source is a pure function with no static or global state, so concurrent calls on different or read-only inputs are safe. |
| **Drop-in for the baseline** | partial: it computes the same exact symmetric discrete Hausdorff value as calling Boost's discrete_hausdorff_distance both ways and taking the max, but it takes std::vector of .x/.y points instead of Boost geometries and returns a {checks, distance} pair |

## Gotchas

- The return value is std::pair{checks, distance}; the first element is a diagnostic counter, so bind it as auto [checks, hd] rather than using .first.
- The built-in policies compute in float even for double or large integer coordinates. Squared integer distances above 2^24 (points more than 4096 units apart) are rounded, so for large coordinates or double precision you need a custom Distance policy with value_type double.
- An empty input contour returns NaN, not 0 or an error.
- Speed depends on both contours having the same orientation and on point order. Reversing one contour (clockwise vs counter-clockwise) or using a different start point weakens the forward prediction, though the result stays exact.

## Known shortcomings

- The 245x is against Boost's plain O(n\*m) scan with no early break; the author's own shuffled brute force is already \~15x faster than Boost; Boost timing includes conversion; ties the shuffled brute force on Kimia216.
- Built-in distance policies compute in float, so squared distances above 2^24 are rounded; the exact claim holds only to float precision. The article's headline is 2.2-14.5x over a shuffled early-break baseline, not 245x.

## Caveats and trade-offs

First-party benchmark; hardware not stated in the README or the article (docs/article.html). The speedup exploits contour ordering that Boost's general function cannot use, so it is a specialised-input comparison. Without BOOST_GEOMETRY_ENABLE_SIMILARITY_RTREE (not defined in this build), Boost's discrete_hausdorff_distance is a plain O(n\*m) scan with no early break. The author's own shuffled brute force is already about 15x faster than Boost on the same package (821.73 vs 12382.56 ms, derived from page data), and the method beats that by 16.3x. The Boost timing includes converting contours to Boost linestrings on every call (CalcHausdorffDistanceBoost). Boost is reported only for the walking-silhouette package; the article says Boost was used mainly as a correctness reference. On Kimia216 the method only ties shuffled brute force (813.40 vs 812.02 ms). The README also lists an OpenCV FLANN kd-tree baseline, which the article says is not strictly exact. Very new repo (first commit 2026-05-14, 10 commits, 1 star).

Header-only, dependency-free; exact result; custom point types and L2/L1/Chebyshev policies; relies on ordered, coherent contours; worst case still O(n\*m).

## Maintenance

New personal project (first commit 2026-05-14, last 2026-06-01, 10 commits, 1 star), but MIT-licensed and a \~240-line dependency-free header that is trivial to vendor and audit.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's walking-silhouettes table gives Boost.Geometry discrete Hausdorff at 12382.56 ms vs 50.48 ms for the method (245x), and the benchmark code is public (HausdorffDistanceOptimized/src/baselines, main.cpp, scripts/run_benchmarks.\*). No hardware or explicit flags are stated (README, docs/article.html) and the measurement is first-party, so C; the &gt;50x gain with unstated flags also caps it at C.
- **Verifier notes:** Numbers match the README. Metadata checked on the repo page: MIT, 1 star, not a fork, last commit 2026-06-01. The GitHub Pages article host (kate-droid-cpu.github.io) is egress-blocked, so the same article was read from raw docs/article.html.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/Kate-droid-cpu/contour-coherent-hausdorff>
  - <https://github.com/Kate-droid-cpu/contour-coherent-hausdorff/commits>
  - <https://raw.githubusercontent.com/Kate-droid-cpu/contour-coherent-hausdorff/HEAD/README.md>
  - <https://raw.githubusercontent.com/Kate-droid-cpu/contour-coherent-hausdorff/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/Kate-droid-cpu/contour-coherent-hausdorff/HEAD/HausdorffDistanceOptimized/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Kate-droid-cpu/contour-coherent-hausdorff/HEAD/HausdorffDistanceOptimized/src/baselines/HausdorffDistanceBaselineLibs.cpp>
  - <https://raw.githubusercontent.com/Kate-droid-cpu/contour-coherent-hausdorff/HEAD/docs/article.html>
  - <https://raw.githubusercontent.com/boostorg/geometry/develop/include/boost/geometry/algorithms/discrete_hausdorff_distance.hpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Kate-droid-cpu/contour-coherent-hausdorff/HEAD/README.md>
  - <https://raw.githubusercontent.com/Kate-droid-cpu/contour-coherent-hausdorff/HEAD/docs/article.html>
  - <https://raw.githubusercontent.com/Kate-droid-cpu/contour-coherent-hausdorff/HEAD/HausdorffDistanceOptimized/include/ContourHausdorff/ContourCoherentHausdorffDistance.hpp>
  - <https://raw.githubusercontent.com/Kate-droid-cpu/contour-coherent-hausdorff/HEAD/HausdorffDistanceOptimized/src/baselines/HausdorffDistanceBaselineLibs.cpp>
  - <https://raw.githubusercontent.com/Kate-droid-cpu/contour-coherent-hausdorff/HEAD/HausdorffDistanceOptimized/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Kate-droid-cpu/contour-coherent-hausdorff/HEAD/CMakePresets.json>
  - <https://github.com/Kate-droid-cpu/contour-coherent-hausdorff>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/kate-droid-cpu/contour-coherent-hausdorff`) · [data/wave8/enrich/raw/github_com_kate_droid_cpu_contour_coherent_hausdorff.json](../../../data/wave8/enrich/raw/github_com_kate_droid_cpu_contour_coherent_hausdorff.json) (enrichment confidence 0.8)

</details>
