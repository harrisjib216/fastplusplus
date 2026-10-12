# geo-utils-cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only C++17 port of Google Maps' spherical geometry utils; beats Boost.Geometry's spherical strategies on area and point-in-polygon.

| | |
|---|---|
| **Beats** | Boost.Geometry 1.90 (spherical_equatorial strategy: bg::within and bg::area); also S2 Geometry 0.14.0 and GeographicLib 2.7 |
| **Claimed result** | contains (M queries/s, geo-utils-cpp vs Boost.Geometry): 16.2 vs 1.91 at N=10, 2.87 vs 0.234 at N=100, 0.329 vs 0.024 at N=1000 (about 8.5x, 12x and 14x, derived from page data). area (M polygons/s): 69.9 vs 45.0 at N=10, 67.2 vs 36.2 at N=100, 67.7 vs 36.6 at N=1000 (about 1.5-1.9x, derived from page data). heading is about 1.05-1.1x faster (24.9 vs 22.5 at N=1000, 15.5 vs 14.7 at N=100,000). distance_between (40.5 vs 39.8 and 28.2 vs 28.8) and path_length (54.0 vs 48.7 down to 41.7 vs 40.2) tie Boost.Geometry within noise. |
| **Workload** | Google Benchmark on seeded random lat/lng data: spherical point-in-polygon (polygons of 10, 100 and 1000 vertices, 1000 query points per iteration) and spherical polygon area (10/100/1000 vertices); native library types are built outside the timed loop. |
| **Metric** | throughput |
| **Hardware** | Apple M1, 8 cores, 8 GB RAM, macOS 15.7 |
| **Compiler and flags** | Apple clang 17, -std=c++17 -O2 -DNDEBUG, Release, Google Benchmark 1.8.4, Boost 1.90.0 |
| **Adoption** | 56 stars |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/gistrec/geo-utils-cpp) · [benchmark](https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/docs/benchmarks.md) |

## Verdict

The author's Google Benchmark runs (Apple M1, Apple clang 17, -std=c++17 -O2 -DNDEBUG, Boost 1.90.0, s2geometry 0.14.0, GeographicLib 2.7, median of 5 repetitions) show area at 67-70 M polygons/s vs Boost.Geometry 36-45 M/s, and contains at about 8.5-14x Boost's spherical bg::within on a regular 5-degree n-gon of 10-1000 vertices with 1000 jittered query points. The contains gap is partly an algorithm difference (rhumb ray cast vs great-circle winding), and distance, heading and path_length are within noise of Boost.

## Use it when

- Polygon area on lat/lng data is a hot path: about 1.5-1.9x Boost.Geometry and about 5x S2's S2Loop::GetArea in the author's M1 runs.
- Point-in-polygon for GPS/geofencing on small to medium polygons (10-1000 vertices) where rhumb-line edges are acceptable and S2 is too heavy a dependency.
- You want zero dependencies and a single header (amalgamated geo.hpp) instead of pulling in Boost, S2 plus Abseil, or GeographicLib.
- Mobile/backend code that must give the same answers as Google Maps Android Utils (same spherical model and conventions).
- Route utilities on lat/lng (point_at_distance, polyline6 encode/decode for OSRM, Valhalla or Mapbox).

## Skip it when

- Sub-meter or survey-grade work: it is spherical, not WGS84 ellipsoidal (use GeographicLib), and precision degrades near the poles and for antipodal pairs.
- contains on large polygons or many queries: S2 measured 18-21 M queries/s at N=100-1000 vs 2.87 and 0.33 M/s here, because the scan is linear with no built-in index or bounding-box prefilter.
- You need great-circle containment semantics that match Boost's bg::within: the default contains uses rhumb-line edges, so answers differ on long edges and at high latitude; geodesic=true exists but was not benchmarked.
- Planar/projected geometry, polygon booleans, validity repair or spatial indexing are needed; the feature set is far smaller than Boost.Geometry, GEOS or TG.
- Very young codebase (first release in 2026, 56 stars), so there is little production track record.

## How it is fast

area uses the polar-triangle accumulation from PolyUtil (Todhunter's two-sides-and-included-angle formula, one tan and one atan2 per vertex) in a tight loop with no allocation, against Boost's strategy machinery. contains is an O(N) ray cast to the South Pole that by default treats edges as rhumb lines (a Mercator-latitude comparison per edge) with cheap linear-latitude early exits, while Boost's bg::within with spherical_equatorial picks a great-circle winding strategy that costs more per edge. distance uses haversine with cached degree-to-radian factors, which ties Boost and hand-written haversine rather than beating them.

## Compared with alternatives

Pick it over TG when your data is raw lat/lng and you want spherical (rhumb or great-circle) area and containment without projecting; TG is planar but has indexed point-in-polygon (ystripes/natural) that scales far better on big polygons. Pair it with an index such as nanoflann or tidwall/rtree.c when you have many polygons, since it ships no spatial index of its own.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (Google Test only for the test suite; Google Benchmark, Boost, S2 and GeographicLib only for the opt-in benchmarks) |
| **Minimum toolchain** | C++17; CMake 3.14+ for the optional CMake package; CI covers GCC and Clang on Linux, AppleClang on macOS and MSVC on Windows |
| **Platforms** | any (portable scalar code, no SIMD or intrinsics) |
| **Thread safety** | All functions are pure (no global mutable state or caching) and documented as safe to call concurrently. |
| **Drop-in for the baseline** | partial — covers Boost.Geometry's spherical distance, area and within for lat/lng points, but through its own LatLng/Path API; Boost geometry types and strategies are not accepted. |

## Gotchas

- contains defaults to rhumb-line edges (geodesic=false) while on_edge and on_path default to great-circle edges; pass geodesic explicitly. The South Pole is always outside a polygon.
- LatLng is never validated: out-of-range coordinates give unspecified (memory-safe, no-throw) results; call is_valid() or normalized() on untrusted input.
- LatLng::operator== is approximate (1e-12 degree epsilon, longitude modulo 360), not bitwise.
- Polygons are implicitly closed (last vertex connects to the first); encode, decode and simplify allocate and can throw std::bad_alloc. decode had signed-overflow UB on malformed input before v1.2.0 (fixed, found by fuzzing).

## Known shortcomings

- The contains win compares rhumb-line with great-circle tests, not like-for-like; port of android-maps-utils (Java).
- Benchmark compares a rhumb-line ray cast (default geodesic=false) against Boost great-circle winding, so the two compute different predicates; geodesic=true is not benchmarked. Bench polygon is a regular 5-degree n-gon, not random lat/lng as the record says. Port of android-maps-utils (Java).

## Caveats and trade-offs

The contains comparison is not like for like. geo-utils-cpp uses an O(N) ray cast over rhumb-line edges by default, while bg::within with the spherical CS picks a great-circle winding strategy. So the two give different answers near the poles and on long edges, and the 8-14x gap partly reflects that choice (the docs say so). S2 beats it by a wide margin on contains (18.0 M/s at N=100), on path_length (about 2x) and on snap-to-route (about 3x). The benchmarks were run on one machine only (Apple M1, Apple clang), with no GCC, MSVC or x86 numbers. The library is a C++ port of the geometry utilities in Google's android-maps-utils (Java, Apache-2.0). The repo is young: the oldest visible commit is from May 2026.

Header-only, no dependencies, lat/lng-native API. Spherical Earth only (mean radius 6371009 m), not WGS84 ellipsoidal; accuracy degrades near the poles and for antipodal pairs. Far smaller feature set than Boost.Geometry (no generic geometry types, no spatial index).

## Maintenance

Active (v1.2.2, last commit 2026-09-20, CI with ASan/UBSan and a libFuzzer target on decode), Apache-2.0 with Google's original notices kept, and small enough (about 50 KB of headers) to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/benchmarks.md gives the compiler and flags (Apple clang 17, -std=c++17 -O2 -DNDEBUG, Release), the CPU (Apple M1) and library versions (Boost 1.90.0, s2geometry 0.14.0, GeographicLib 2.7). The Google Benchmark code is public under benchmarks/ (bench_geo_utils, bench_boost, bench_s2, bench_geographiclib, with shared inputs from benchmarks/common/random_data.hpp).
- **Verifier notes:** Every number in the record appears in docs/benchmarks.md. I added the small heading win and the path_length tie, and the caveat that the library is a port of android-maps-utils (Java, so this is not a duplicate of a C++ entry). Apache-2.0, 56 stars, last commit 2026-09-20 and not a fork all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/benchmarks/README.md>
  - <https://github.com/gistrec/geo-utils-cpp>
  - <https://github.com/gistrec/geo-utils-cpp/commits>
- **Sources the enricher read:**
  - <https://github.com/gistrec/geo-utils-cpp>
  - <https://github.com/gistrec/geo-utils-cpp/issues?q=is%3Aissue>
  - <https://github.com/gistrec/geo-utils-cpp/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/docs/api.md>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/benchmarks/common/random_data.hpp>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/benchmarks/speed/bench_boost.cpp>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/benchmarks/speed/bench_geo_utils.cpp>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/include/geo/geo.hpp>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/include/geo/spherical.hpp>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/include/geo/poly.hpp>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/include/geo/latlng.hpp>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/include/geo/bounds.hpp>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/include/geo/encoding.hpp>
  - <https://raw.githubusercontent.com/gistrec/geo-utils-cpp/HEAD/include/geo/version.hpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/gistrec/geo-utils-cpp`) · [data/wave8/enrich/raw/github_com_gistrec_geo_utils_cpp.json](../../../data/wave8/enrich/raw/github_com_gistrec_geo_utils_cpp.json) (enrichment confidence 0.85)

</details>
