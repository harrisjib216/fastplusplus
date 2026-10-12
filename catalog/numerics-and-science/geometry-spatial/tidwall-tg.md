# TG (tidwall geometry library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Single-file C11 planar geometry library whose indexed point-in-polygon and intersects tests beat GEOS PreparedGeometry by about 1.1-2.7x.

| | |
|---|---|
| **Beats** | GEOS (PreparedGeometry and plain geometry) |
| **Claimed result** | Brazil: tg/ystripes 15,174,761 ops/s and tg/natural 10,143,419 ops/s vs geos/prepared 7,885,512 ops/s and geos/none 29,708 ops/s; Texas: 22,453,447 vs 9,868,950 (prepared) |
| **Workload** | Point-in-polygon on 10K random points against Brazil polygon (39,914 points) and other polygons, best of 10 runs |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5950X 16-Core |
| **Compiler and flags** | gcc-11 (Ubuntu 11.4.0) -O3; GEOS 3.12.0 |
| **Adoption** | 673 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/tidwall/tg) · [benchmark](https://github.com/tidwall/tg/blob/HEAD/docs/BENCHMARKS.md) |

## Verdict

The author's tests/bench.c (GEOS_BENCH=1) times 10K random points within each polygon's MBR plus 10%, best of 10 runs, on an AMD Ryzen 9 5950X with gcc 11.4.0 -O3 against GEOS 3.12.0 built from source. On Brazil (39,914 points), TG YStripes reaches 15.17M ops/s and Natural 10.14M against GEOS prepared at 7.89M and unprepared at 29.7K; on Texas, YStripes reaches 22.45M against 9.87M. Across all 13 PIP polygons Natural is 1.08-2.5x and YStripes 1.35-2.7x GEOS prepared (derived from page data), with identical hit counts. The GEOS loop calls the generic GEOSPreparedIntersects_r on prebuilt point geometries, while TG calls its point-specialised tg_poly_intersects_point, so part of the gap is per-call overhead rather than the index.

## Use it when

- Geofencing or stream filtering: many points tested against a fixed set of large polygons (10^3-10^5 vertices), where TG Natural gave 10-22M ops/s on one core for the real-world state and country outlines in the author's runs
- Polygons that are created or reloaded often: Natural index builds in tens of microseconds (Brazil, 39,914 points: 53 us vs 2,060 us for a GEOS prepared geometry) and uses about 4.5x less memory
- Peak point-in-polygon throughput on a long-lived polygon: index it with TG_YSTRIPES (about 1.5-2.7x GEOS prepared on the larger shapes) and keep Natural for other predicates
- Fast WKB/GeoJSON/WKT ingestion in C or C++ (Brazil WKB read 28,320 vs GEOS 3,150 ops/s in the same run)
- Embedding a small, dependency-free geometry core in C/C++ services or WebAssembly builds

## Skip it when

- You need overlay (union/intersection/difference), buffering, simplification, convex hull, Voronoi, DE-9IM relate matrices or validity repair: TG does not implement them; use GEOS
- Geographic (lon/lat on the sphere) semantics: TG is planar Cartesian only, so polygons crossing the antimeridian or spanning large areas need your own handling
- Edge-case OGC semantics on collections and multilinestrings: as of 2026-10-01, issues #29 (covers over multiple components) and #30 (mod-2 boundary rule) are open, and #20 and #24 were only fixed in September 2026
- Input that may be invalid: rings are defined as closed and non-self-intersecting, but tg.c does not check self-intersection, so bad input gives undefined predicate answers
- Highly irregular random-shaped polygons where you want YStripes: on the Random-100 and Random-1000 tests it was slower than Natural, and it costs about 20x Natural's build time

## How it is fast

Point-in-polygon is ray casting, accelerated by two segment indexes built at ring construction. Natural indexing is a flat, multi-level R-tree-like array of branch MBRs whose leaf level is the ring's own segment array in its original order (default spread 16), so the index adds about 7% memory and builds in one pass; by default its rectangles are 32-bit floats rounded outward. YStripes splits the y-range into hash-bucket-like stripes (count from a Polsby-Popper compactness score times segment count, minimum 32), each listing the segments it crosses, which gives O(1) lookup of the segments a horizontal ray can hit. Multi-geometries get a Hilbert-curve-ordered index over their members, clones are O(1) via atomic reference counting, and min/max use single minsd/maxsd instructions on x86-64 to avoid branches.

## Compared with alternatives

Pick TG when the job is polygon predicates (point-in-polygon, segment/geometry intersects) against a few large polygons. nanoflann, tidwall/rtree.c and GeoToolbox KdBoxTree index many separate points or boxes and pair well with TG as a first-stage filter, while Manifold, MeshLib and trueform are 3D mesh libraries for a different problem.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (tg.c and tg.h; C standard library, stdatomic.h unless TG_NOATOMICS is defined) |
| **Minimum toolchain** | C11 compiler; MSVC builds were fixed in September 2026 (issue #15, GCC builtins) |
| **Platforms** | Portable C: x86-64 (inline minsd/maxsd asm under GCC/Clang), aarch64, WebAssembly via Emscripten; big-endian WKB (#18) and ARMv7 alignment (#12) fixed in 2025, wasm32/ILP32 struct-layout bug (#26) closed 2026-09-24 |
| **Thread safety** | Library functions are documented as thread-safe and reentrant, with atomic reference counts for shared geometries. The tg_env_set_\* globals (allocator, default index, spread) must be called once at startup before any other tg_\* call. |
| **Drop-in for the baseline** | no |

## Gotchas

- tg_geom_contains/within return false for a point on the polygon edge; use tg_geom_covers or tg_geom_intersects when boundary points must count
- Arithmetic is plain double with a precision-loss nudge (nexttoward) inside the collinear and raycast tests, not exact or extended-precision predicates; index rectangles are float32 rounded outward unless you build with TG_IXFLOAT64
- Constructors clone their inputs by reference count: every tg_\*_new/parse/clone/copy needs exactly one free. Upcasting tg_line/tg_ring/tg_poly to tg_geom is free, but downcasting is unsafe
- Parsers return an error geometry rather than NULL on bad input; check tg_geom_error() and handle NULL for out-of-memory

## Known shortcomings

- Open correctness issues #29 (covers on multi-component input) and #30 (multilinestring mod-2 boundary rule); #20 and #24 fixed only Sep 2026; #26 wasm32 struct-layout bug closed 2026-09-24.
- Benchmark asymmetry: the GEOS loop calls generic GEOSPreparedIntersects_r on prebuilt points while TG calls point-specific tg_poly_intersects_point, so part of the gap is call overhead; planar only, no robust predicates.

## Caveats and trade-offs

Own benchmark by author; geometry predicates only (PIP, intersects, parsing), not GEOS's wider algorithms. Found as repo with benchmark, not a paper.

Not a full GIS library (no convex hull, voronoi etc.); single tg.c file; indexed polygons use more memory and build time (ystripes \~884us vs GEOS prepared \~2060us for Brazil).

## Maintenance

Actively maintained (last commit 2026-09-26, about 676 stars, MIT), with a stream of predicate-correctness fixes from an outside contributor in September 2026; the library is one tg.c plus tg.h, so vendoring a current commit is easy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/BENCHMARKS.md shows GEOS_BENCH=1 tests/run.sh bench output (bench code tests/bench.c) with CFLAGS -O3, gcc-11 11.4.0, AMD Ryzen 9 5950X and GEOS 3.12.0; Brazil/Texas rows match the record exactly.
- **Verifier notes:** All numbers verified (Brazil tg/ystripes 15,174,761 vs geos/prepared 7,885,512 ops/s; Texas 22,453,447 vs 9,868,950). On Random-1000 rows tg/natural 3.37M vs geos/prepared 1.37M, so wins hold across the PIP table. MIT, 673 stars, last commit 2026-09-26.
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/tidwall/tg/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/tidwall/tg/HEAD/LICENSE>
  - <https://github.com/tidwall/tg>
  - <https://github.com/tidwall/tg/commits>
- **Sources the enricher read:**
  - <https://github.com/tidwall/tg>
  - <https://raw.githubusercontent.com/tidwall/tg/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/tg/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/tidwall/tg/HEAD/docs/POLYGON_INDEXING.md>
  - <https://raw.githubusercontent.com/tidwall/tg/HEAD/docs/API.md>
  - <https://raw.githubusercontent.com/tidwall/tg/HEAD/tg.h>
  - <https://raw.githubusercontent.com/tidwall/tg/HEAD/tg.c>
  - <https://raw.githubusercontent.com/tidwall/tg/HEAD/tests/bench.c>
  - <https://raw.githubusercontent.com/tidwall/tg/HEAD/LICENSE>
  - <https://github.com/tidwall/tg/commits>
  - <https://github.com/tidwall/tg/issues?q=is%3Aissue%20state%3Aopen>
  - <https://github.com/tidwall/tg/issues?q=is%3Aissue%20state%3Aclosed>
  - <https://github.com/tidwall/tg/issues/16>
  - <https://github.com/tidwall/tg/issues/20>
  - <https://github.com/tidwall/tg/issues/24>
  - <https://github.com/tidwall/tg/issues/26>
  - <https://github.com/tidwall/tg/issues/29>
  - <https://github.com/tidwall/tg/issues/30>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tidwall/tg`) · [data/wave8/enrich/raw/github_com_tidwall_tg.json](../../../data/wave8/enrich/raw/github_com_tidwall_tg.json) (enrichment confidence 0.85)

</details>
