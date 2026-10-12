# Polylidar3D

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> C++ concave-polygon (with holes) extraction from 2D points and 3D data; about 4.8x faster than CGAL 2D alpha shapes.

| | |
|---|---|
| **Beats** | CGAL 2D Alpha Shapes (also PostGIS ST_ConcaveHull 2.5.2 and Spatialite ST_ConcaveHull, which the README treats as GEOS-based) |
| **Claimed result** | concavehull-evaluation README chart (California shape, read by eye): at about 64,000 points Polylidar about 30-40 ms, CGAL alpha shapes about 200 ms, PostGIS about 3,150 ms (no holes) and 4,100 ms (holes), Spatialite about 11,300 ms. The same README lists 30 raw sub-timing runs on caholes_64000 (64,000 points with holes): Polylidar about 36 + 4.4 + 1.0 = about 41 ms per run, CGAL triangulation plus alpha shape about 44.4 + 153 = about 197 ms, Spatialite about 235 + 135 + 10,900 = about 11,300 ms; i.e. about 4.8x faster than CGAL and about 270x faster than Spatialite (derived from page data). Robust predicates were on; disabling them gives a further 30% speedup per the README. |
| **Workload** | Non-convex (concave hull) polygon extraction from random point sets sampled inside the California state outline, 2,000 to about 64,000 points, with and without holes; execution time in ms (concavehull-evaluation repo). |
| **Metric** | latency |
| **Compiler and flags** | Not stated (C++14 compiler; Polylidar built with PL_USE_ROBUST_PREDICATES=1; CGAL 4.12, PostGIS 2.5.2) |
| **Adoption** | 338 stars |
| **Last commit** | 2023-03-13 |
| **Links** | [repository](https://github.com/JeremyBYU/polylidar) · [benchmark](https://github.com/JeremyBYU/concavehull-evaluation) |

## Verdict

In the author's concavehull-evaluation repo, the 2D Polylidar (robust predicates on, Python bindings) was timed against CGAL 4.12 Alpha_shape_2 (C++, alpha shape plus unordered boundary edges), PostGIS 2.5.2 ST_ConcaveHull (via psycopg client, upload excluded) and in-memory Spatialite ST_ConcaveHull on points sampled inside the California outline. At about 64,000 points the chart shows Polylidar at about 30-40 ms versus about 200 ms for CGAL and 3-4 s for PostGIS. The 30-run subtimings on caholes_64000 give about 41 ms for Polylidar versus about 197 ms for CGAL (about 4.8x) and about 11.3 s for Spatialite (about 270x, derived from page data). No hardware, compiler or flags are stated. The RA-L 2020 paper (arXiv 2002.01886) reports 'more than four times speedup' per search snippets, but arxiv.org is blocked here and it was not opened.

## Use it when

- Outlines with holes from dense 2D point sets (footprints, coverage areas, sampled regions) at 10^3-10^5 points, where CGAL alpha shapes took about 200 ms and PostGIS 2.5 ST_ConcaveHull about 3-4 s for 64,000 points versus Polylidar's 30-40 ms
- When you need a ready-made polygon (ordered shell plus holes) rather than unordered boundary edges you must stitch yourself
- Ground-plane or floor-region polygons from airborne LiDAR, RGB-D range images or meshes, in real-time robotics loops (RealSense and KITTI use-case repos exist)
- Python users who want a prebuilt wheel: PyPI polylidar 1.0.9 ships CPython 3.7-3.10 wheels for Linux x86-64, macOS (x86-64, arm64) and Windows x64

## Skip it when

- You need the exact CGAL alpha-shape definition, or many alpha levels from one build: Polylidar's circumradius/edge-length filter defines a different hull, and the benchmark itself notes that CGAL's per-edge alpha intervals give you a whole family of shapes
- Near-degenerate input (collinear or cocircular points) with default builds: Delaunator lacks robust predicates unless you compile with PL_USE_ROBUST_PREDICATES, which is OFF by default in CMake and is not set by setup.py
- Python 3.11+ or a maintained dependency: the last release (1.0.9) and last commit are from 2023-03-13, there are no wheels after cp310, and issues #16 (no polygons on airborne LiDAR) and #19 are open
- Precise geodesic or GIS-grade output: there is no snapping, validity repair or CRS handling, and polygons come back as point-index lists that you turn into geometries yourself (the Python helpers use Shapely)

## How it is fast

It Delaunay-triangulates the points with an in-tree port of Delaunator (mapbox/delaunator-cpp, a sweep-hull algorithm), drops triangles whose circumradius exceeds alpha or whose edges exceed lmax, and groups the remaining edge-connected triangles by breadth-first region growing over the half-edge structure. Each region becomes a polygon through boundary following: border half-edges (those whose twin is missing or filtered out) go into parallel-hashmap tables keyed by point, the shell is traced from the right-most extreme point, and the leftover border loops become holes. In the 64,000-point subtimings, about 36 ms of Polylidar's 41 ms is triangulation, with 4.4 ms for filtering and region growing and 1.0 ms for polygon extraction. CGAL spends 44 ms on triangulation and 153 ms building the alpha shape, including alpha intervals for every edge. In 3D mode, marl fibers and OpenMP parallelize over multiple dominant planes.

## Compared with alternatives

No sibling in this category extracts concave hulls. detria and Delaunay32 are fast 2D triangulators (benchmarked against CDT and Triangle, not Delaunator) but stop at the triangulation, the step that dominates Polylidar's runtime, and CGAL alpha shapes remain the reference when you need the exact alpha-complex definition or a family of alpha values.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Eigen, google/marl (task scheduler), greg7mdp parallel-hashmap and a fast-exp header, all bundled under thirdparty; optional OpenMP (disabled on Apple) and Shewchuk robust predicates (PL_Predicates); pybind11 for the Python module, with numpy, shapely and matplotlib in requirements.txt |
| **Minimum toolchain** | C++14, CMake 3.14+ (the benchmark repo asks for a C++14 compiler) |
| **Platforms** | Linux, Windows and macOS (x86-64 and arm64 wheels on PyPI); no SIMD-specific code found in the files read |
| **Thread safety** | not documented. Each Polylidar3D object creates its own marl::Scheduler (default 4 worker threads, task_threads), and the 2D path writes to the member z_thresh, so share one instance across threads only with care |
| **Drop-in for the baseline** | partial: it replaces 'concave hull of a 2D point set' (CGAL Alpha_shape_2 boundary extraction or PostGIS ST_ConcaveHull) with different parameters (alpha = max circumradius, lmax = max edge length) and returns ordered polygons with holes instead of alpha-classified edges |

## Gotchas

- The benchmarked code is the 2D Polylidar on the polylidar2d branch (the concavehull-evaluation submodule is at commit 6e25d1f). Master is Polylidar3D with a different API, and its 2D timings were not re-measured
- Defaults are tuned for 3D: lmax=1.0, min_triangles=20 and alpha=0.0 (off). For a 2D point set you must set alpha or lmax to your data's scale, or small regions are silently dropped
- When boundary tracing hits a broken edge (e.g. Delaunator mislabelling a hull edge), ConcaveSection prints to stderr and returns an empty shell instead of throwing, so check for empty polygons
- Robust predicates cost speed: the evaluation README says turning them off gives a further \~30%, so the headline numbers were taken with robust predicates on, while stock builds have them off

## Known shortcomings

- Benchmarked code is the old Polylidar2D (submodule 6e25d1f), not current Polylidar3D; RA-L paper unreadable here (possible B on retier); text sub-timings show \~4.8x vs CGAL.
- Benchmarked code is the polylidar2d branch, not master Polylidar3D. Robust predicates are off by default (the benchmark used them on). Boundary-trace failure prints to stderr and returns an empty shell. Abandoned 2023-03; wheels only up to cp310.

## Caveats and trade-offs

The benchmark measured the original 2D Polylidar (submodule thirdparty/polylidar at commit 6e25d1f, now the polylidar2d branch, tied to the RA-L 2020 paper), not the current Polylidar3D code on master, whose API differs. Evidence is a chart image and raw timing lists in a separate 4-star benchmark repo, with no hardware, compiler or flags stated. CGAL timing covers alpha shape construction plus unordered boundary edge extraction only (no polygon assembly) but also computes alpha intervals for the whole family of shapes. CGAL 4.12 and PostGIS 2.5.2 are old; PostGIS timing includes client/server round trip. The RA-L paper (doi 10.1109/LRA.2020.3002212, arXiv 2002.01886) reportedly claims more than 4x speedup over other concave polygon extraction methods but was not opened. Repo unmaintained since 2023-03.

C++ with pybind11 Python bindings; multi-threading (marl) and optional GPU path in the 3D mode; polygons with holes. It extracts planar-region polygons from Delaunay-triangulated data, so the hull is defined differently from an alpha shape or PostGIS concave hull; CGAL returns unordered boundary edges rather than a polygon.

## Maintenance

Abandoned since 2023-03-13 (PyPI 1.0.9; 338 stars) but MIT-licensed. The 2D path is small enough to lift from the polylidar2d branch, while master pulls in marl, Eigen and parallel-hashmap.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark repo (concavehull-evaluation) with public code and a timing chart plus raw sub-timing lists against CGAL alpha shapes, PostGIS and Spatialite, but no hardware, compiler or flags; the peer-reviewed RA-L paper could not be opened (arxiv.org, IEEE and MDPI blocked by egress), so B is unconfirmed.
- **Verifier notes:** Numbers in the record match the chart; added the text sub-timings that are on the same page. arxiv.org, pmc.ncbi.nlm.nih.gov and mdpi.com were egress-blocked, so the peer-reviewed paper could not be checked; a retier check to B is worth doing where arXiv is reachable. MIT, 338 stars, last commit 2023-03-13 (abandoned) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/JeremyBYU/concavehull-evaluation/master/README.md>
  - <https://raw.githubusercontent.com/JeremyBYU/concavehull-evaluation/master/assets/repo/ca_time.png>
  - <https://github.com/JeremyBYU/concavehull-evaluation>
  - <https://github.com/JeremyBYU/concavehull-evaluation/tree/master/thirdparty>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/README.md>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/polylidar2d/README.md>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/6e25d1f1f087f382c6abf5d0d8a32376873b5b74/README.md>
  - <https://github.com/JeremyBYU/polylidar>
  - <https://github.com/JeremyBYU/polylidar/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/README.md>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/polylidar2d/README.md>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/polylidar2d/CMakeLists.txt>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/src/Polylidar/CMakeLists.txt>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/setup.py>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/src/version.txt>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/include/Polylidar/Polylidar.hpp>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/include/Polylidar/Core.hpp>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/include/Polylidar/Types.hpp>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/src/Polylidar/Polylidar.cpp>
  - <https://raw.githubusercontent.com/JeremyBYU/polylidar/HEAD/src/Polylidar/Core.cpp>
  - <https://raw.githubusercontent.com/JeremyBYU/concavehull-evaluation/master/README.md>
  - <https://github.com/JeremyBYU/polylidar/issues?q=is%3Aissue>
  - <https://github.com/JeremyBYU/polylidar/issues/3>
  - <https://github.com/JeremyBYU/polylidar/issues/9>
  - <https://pypi.org/pypi/polylidar/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jeremybyu/polylidar`) · [data/wave8/enrich/raw/github_com_jeremybyu_polylidar.json](../../../data/wave8/enrich/raw/github_com_jeremybyu_polylidar.json) (enrichment confidence 0.75)

</details>
