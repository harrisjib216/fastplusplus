# CavalierContours

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++ offsetting and booleans for 2D polylines with exact arcs; up to 16-85x faster than Clipper1 offsets when arcs stay exact.

| | |
|---|---|
| **Beats** | Clipper (ClipperLib polygon offsetting, Angus Johnson, original Clipper) |
| **Claimed result** | Arcs approximated for both (1e-2): 3.5x faster on the square (0.21 vs 0.72 ms), 4.0x on PathologicalProfile1/100 (336.37 vs 1347.09 ms), but slower on BM_Profile1 (0.7x) and BM_Profile2 (0.9x). Arcs kept exactly vs Clipper at 1e-2: 76.4x on the circle (0.12 vs 9.47 ms), 84.9x on PathologicalProfile1/10 (1.61 vs 136.46 ms), 15.8x on PathologicalProfile1/100 (85.10 vs 1347.09 ms). Against Clipper at 1e-3: up to 494.7x on the circle and 861.0x on PathologicalProfile1/10. |
| **Workload** | Repeated inward and outward offsetting (rounded joins) of 2D polylines with arcs: square, circle, rounded rectangle, two small profiles and pathological circles of N alternating half-circle arcs; Clipper given arcs approximated at 1e-2 or 1e-3. |
| **Metric** | latency |
| **Hardware** | Windows 10 64-bit, Intel i7-6700K @ 4.00GHz |
| **Compiler and flags** | MSVC 2019 19.24.28314 targeting 64-bit (MinGW 7.3 64-bit gave similar results); optimization flags not stated |
| **Adoption** | 515 stars |
| **Last commit** | 2024-08-28 |
| **Links** | [repository](https://github.com/jbuckmccready/CavalierContours) · [benchmark](https://github.com/jbuckmccready/CavalierContours) |

## Verdict

First-party Google Benchmark runs (Windows 10 x64, i7-6700K at 4.00 GHz, MSVC 2019 19.24.28314; optimisation flags not stated) offset nine profiles repeatedly inward and outward with rounded joins against original Clipper (ClipperOffset, jtRound, input scaled by 1e8). With arcs approximated for both at 1e-2, cavc ranges from 0.7x (BM_Profile1) to 4.0x (PathologicalProfile1/100); with arcs kept exact vs Clipper at 1e-2 it is 3.4x-84.9x, and vs Clipper at 1e-3 up to 494.7x (circle) and 861.0x (PathologicalProfile1/10), largely because the arc representation needs far fewer segments.

## Use it when

- CAD/CAM tool-path generation (cutter compensation, pocketing/cleanout passes) on profiles made of lines and arcs, especially DXF-style bulge polylines
- Offsets where exactness of rounded joins matters: output stays at a constant distance with true arcs, so no re-fitting of arcs after offsetting
- Repeated inward/outward offsets of small to medium profiles (tens to a few thousand vertices); with arcs kept exact the README times are 0.12-85 ms where Clipper1 took 9-1347 ms
- C or FFI consumers that want a small, dependency-free library with a C API (a Python wrapper exists over it)

## Skip it when

- Line-only polygons, where the advantage shrinks: with arcs approximated for both libraries cavc is 0.7x on BM_Profile1 and 0.9x on BM_Profile2 at 1e-2, and 1.0x on the circle
- General polygon clipping with holes, many paths and fill rules (even-odd, non-zero): booleans here take exactly two closed polylines; Clipper2 or clipper2next fit that job
- Robustness-critical pipelines without your own validation: open bug reports include a union that returns empty when operands are swapped (#71, 2025), offset failures on open polylines (#59), numeric failures after translating input (#53), and ParallelOffsetIslands output errors (#49), and the author has stopped fixing bugs in the C++ version
- Inputs with coordinates far from the 0.1-1000 range: fixed absolute epsilons (1e-8, 1e-5, 1e-4) mean you may need to rescale, as the README itself advises
- New projects that can take a Rust dependency: development moved to the Rust cavalier_contours crate (MIT/Apache-2.0, with a C FFI crate), and the author recommends using it from C++

## How it is fast

The offset follows Liu et al. 2007 ('An offset algorithm for polyline curves'): build raw offset segments, join them with exact arcs, find self-intersects (and dual-offset intersects for open or self-intersecting input), slice, discard slices closer than the offset to the original, and stitch the rest. Because arcs are kept as single bulge segments, a circle stays 2 vertices instead of 142-446 line segments, which is where the 15-860x ratios come from. Intersection and distance queries go through a packed Hilbert R-tree (StaticSpatialIndex, flatbush-style, node size 16), giving O(n log n) for typical CAD/CAM input and O(n^2) only when all segment boxes overlap.

## Compared with alternatives

Pick it over clipper2next or Clipper2 when your geometry has real arcs and you need exact arc output for machining; pick clipper2next/Clipper2 for line-only polygons, multi-path clipping with fill rules, or integer-exact robustness. No other catalogued sibling offsets arc polylines.

## Integration

| | |
|---|---|
| **Form** | header-only (CAVC_HEADER_ONLY) or shared/static lib for the C API |
| **Dependencies** | none for the library; GoogleTest for tests; google/benchmark plus the author's clipper-lib mirror (FetchContent at origin/master) for benchmarks |
| **Minimum toolchain** | README says C++14; the current top-level CMakeLists sets CMAKE_CXX_STANDARD 20 and CMake 3.21 (since the 2024 reorganisation); benchmarks were built with MSVC 2019 19.24 and MinGW 7.3 |
| **Platforms** | any (portable scalar C++, no SIMD intrinsics); benchmarked on Windows 10 x64; the dev app also builds to WebAssembly via Emscripten |
| **Thread safety** | not documented; functions are stateless templates that take const inputs and return new polylines, so concurrent calls on separate data look safe, but no guarantee is stated |
| **Drop-in for the baseline** | no |

## Gotchas

- parallelOffset takes a hasSelfIntersects flag (default false); for a closed, self-intersecting input you must pass true to get the dual-offset path, otherwise results can be wrong
- Internal consistency checks use CAVC_ASSERT, which is plain assert(); in release builds (NDEBUG) cases like 'Bug detected, should never loop this many times!' in polylinecombine.hpp are not checked
- Offsets always use rounded (arc) joins; there is no miter or square join, so sharp-corner offsets need post-processing (issue #44)
- The Clipper benchmark used Clipper1 (original ClipperLib, scaled by 1e8 into 64-bit ints) from an unpinned mirror; Clipper2, its successor, was not compared

## Known shortcomings

- Bench code in tests/benchmarks/clipperbenchmarks.cpp but flags unstated; the &gt;50x ratios apply only to exact arcs; Clipper version unpinned.
- Open correctness bugs: union returns empty when operands are swapped (#71, 2025), offset failures (#59), wrong results after translating input (#53, closed without fix). Internal checks are assert() only, off in release builds. Baseline is Clipper1; Clipper2 not compared. README says C++14 but CMakeLists sets C++20. Development continues in the Rust cavalier_contours crate (has a C FFI crate).

## Caveats and trade-offs

First-party benchmark on about 2019-2020 hardware. The benchmark code is in tests/benchmarks of this repo (clipperbenchmarks.cpp; Clipper is fetched by tests/benchmarks/clipper.cmake from the author's jbuckmccready/clipper-lib mirror at origin/master, so the Clipper version is not pinned). Optimization flags and build type are not stated. Most of the large ratios come from keeping arcs exact instead of approximating them, a different representation from Clipper's. With arcs approximated for both, the result is close: at 1e-2, 1.0x on the circle, 0.7x on BM_Profile1 and 0.9x on BM_Profile2; at 1e-3, 0.9x on BM_Profile1. The author says the C++ version is no longer actively developed (the Rust cavalier_contours replaces it) and the last commit was 2024-08-28.

Header-only C++14 with C API; 2D polylines with constant-radius arcs; offset, boolean ops, winding number and area; packed Hilbert R-tree spatial index; absolute float thresholds so inputs may need rescaling.

## Maintenance

Stale: the author says the C++ version will get no new features or bug fixes (last commit 2024-08-28, a contributed fix); MIT-licensed, header-only and easy to vendor, but the Rust cavalier_contours with its C FFI is the maintained path.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README benchmark tables against Clipper match the record and state compiler (MSVC 2019 19.24.28314 x64) and CPU (i7-6700K). The benchmark code is public in this repo (tests/benchmarks/clipperbenchmarks.cpp and offsetbenchmarks.cpp, Google Benchmark), but optimization flags and build type are not stated, so not A. First-party, so C; the &gt;50x arcs-exact ratios with unstated flags also cap it at C.
- **Verifier notes:** All quoted ratios and timings match the README tables. Metadata from the repo page: MIT, 515 stars, not a fork or archived, last commit 2024-08-28 (stale). Clipper is not a spec-named incumbent but is the de facto polygon-offsetting library, so it is a recognizable baseline.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/jbuckmccready/CavalierContours>
  - <https://github.com/jbuckmccready/CavalierContours/commits/master>
  - <https://github.com/jbuckmccready/CavalierContours/tree/master>
  - <https://github.com/jbuckmccready/CavalierContours/tree/master/tests>
  - <https://github.com/jbuckmccready/CavalierContours/tree/master/tests/benchmarks>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/HEAD/README.md>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/tests/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/tests/benchmarks/clipper.cmake>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/tests/benchmarks/clipperbenchmarks.cpp>
  - <https://github.com/jbuckmccready/CavalierContoursDev>
- **Sources the enricher read:**
  - <https://github.com/jbuckmccready/CavalierContours>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/README.md>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/LICENSE>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/tests/benchmarks/clipperbenchmarks.cpp>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/tests/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/tests/benchmarks/clipper.cmake>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/include/cavc/mathutils.hpp>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/include/cavc/polylineoffset.hpp>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/include/cavc/polylinecombine.hpp>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/include/cavc/polyline.hpp>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/include/cavc/staticspatialindex.hpp>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/include/cavc/internal/common.hpp>
  - <https://raw.githubusercontent.com/jbuckmccready/CavalierContours/master/c_api_include/cavaliercontours.h>
  - <https://github.com/jbuckmccready/CavalierContours/tree/master/include/cavc>
  - <https://github.com/jbuckmccready/CavalierContours/commits/master>
  - <https://github.com/jbuckmccready/CavalierContours/issues?q=is%3Aissue>
  - <https://github.com/jbuckmccready/CavalierContours/issues/71>
  - <https://github.com/jbuckmccready/CavalierContours/issues/59>
  - <https://github.com/jbuckmccready/CavalierContours/issues/53>
  - <https://github.com/jbuckmccready/cavalier_contours>
  - <https://raw.githubusercontent.com/AngusJohnson/Clipper2/main/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jbuckmccready/cavaliercontours`) · [data/wave8/enrich/raw/github_com_jbuckmccready_cavaliercontours.json](../../../data/wave8/enrich/raw/github_com_jbuckmccready_cavaliercontours.json) (enrichment confidence 0.75)

</details>
