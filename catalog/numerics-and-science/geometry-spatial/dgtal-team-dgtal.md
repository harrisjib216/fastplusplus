# DGtal QuickHull

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `LGPL-3.0-or-later` · 🟢 active

> Exact-integer QuickHull for convex hulls in any dimension, inside DGtal; authors claim over 2x faster than CGAL convex_hull_3.

| | |
|---|---|
| **Beats** | CGAL convex_hull_3 (Cartesian and Exact_predicates_inexact_constructions_kernel) |
| **Claimed result** | Source doc comment and module docs: 'This version is generally more than twice faster than CGAL convex_hull_3 for the usual CGAL kernels Cartesian and Exact_predicates_inexact_constructions_kernel.' No CGAL timings are given. The same docs say that Delaunay triangulation via the higher-dimensional convex hull is 'generally much slower than CGAL method ... (5-10 times slower in our experience)'. DGtal-only timings (MacBook Pro, 2.7 GHz quad-core Intel Core i7): 1e7 random lattice points in a ball of radius 1000 take 7913 ms in total, of which 4221 ms purge duplicates and 3214 ms is the QuickHull core. |
| **Workload** | 3D convex hull computation (QuickHull class in src/DGtal/geometry/tools/QuickHull.h, arbitrary dimension, exact lattice-point kernel available). |
| **Metric** | throughput |
| **Adoption** | 398 stars (whole DGtal library) |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/DGtal-team/DGtal) · [benchmark](https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/src/DGtal/geometry/tools/QuickHull.h) |

## Verdict

The only comparison is one sentence repeated in QuickHull.h and the module docs: 'generally more than twice faster than CGAL convex_hull_3' for the Cartesian and EPICK kernels, with no CGAL numbers, point sets, CGAL version, compiler or hardware given, and no CGAL benchmark in the repository. The docs' own DGtal-only timings (MacBook Pro, 2.7 GHz quad-core Intel Core i7) are 7.9 s total for 1e7 random lattice points in a radius-1000 ball, of which 3.2 s is the Quickhull core and 4.2 s is duplicate removal.

## Use it when

- 3D convex hulls of integer or voxel/lattice point sets (digital geometry, voxelized shapes) where you want exact, robust results without CGAL's licence or kernel machinery
- Hulls in 4D-6D or higher of lattice points, which convex_hull_3 does not cover; the docs give the int64 coordinate limits per dimension (about 1.5e6 in 3D, 4e4 in 4D, 5e3 in 5D, 1.2e3 in 6D)
- Floating-point points that may be snapped to a rational grid: the rational kernel rounds x \* precision to integers, and the docs report 1e7 points in a radius-1000 ball (precision 1024) in about 7.9 s total on a 2.7 GHz quad-core i7 MacBook Pro
- You need polygonal (merged coplanar) facets, for example lattice polytopes or H-representations, rather than a triangulated hull
- Projects already using DGtal for digital topology or geometry, where the hull comes at no extra dependency cost

## Skip it when

- Delaunay triangulation: the same docs say the lifted-hull Delaunay is 5-10x slower than CGAL's point-location method (1M lattice points in 2D took about 20.7 s), so use CGAL, Delaunay32 or gDel3D/HXT instead
- Incremental or dynamic hulls with point insertion and removal: the docs say it is not tailored for that
- Large coordinates or high dimensions with default int64: overflow is possible past the documented bounds, is reported only as an InvalidRidge or InvalidConvexHull status, and switching to BigInteger costs about 25x (35x when both coordinate and internal types are BigInteger)
- When you need a measured speedup: the '2x faster than CGAL' line has no published CGAL timings, point distributions, compiler or benchmark program
- Small dependency footprint or permissive licence: it ships inside the LGPL-3.0 DGtal library, which needs C++20, CMake 3.20, Boost headers, zlib and Eigen

## How it is fast

It implements Barber et al.'s Quickhull (1996): start from a full-dimensional simplex, assign each point to one facet it lies above, repeatedly take the furthest point of a facet, find visible facets through neighbour links, build the horizon ridges, cone new facets to the point, merge coplanar facets and reassign the outside points. Geometry is delegated to a kernel that uses exact integer arithmetic (int64 by default, optional BigInteger) for facet normals, intercepts and above/on tests, so there is no floating-point filtering or exact-arithmetic fallback cost. Coplanar facets are merged instead of triangulated, which keeps the facet count low on lattice inputs where coplanarity is common.

## Compared with alternatives

No sibling entry is a dedicated 3D convex hull: pgl beats CGAL on convex_hull_2 in the plane only, and gDel3D or HXT target 3D Delaunay, where DGtal's lifted method is 5-10x slower than CGAL. Pick DGtal QuickHull for exact integer hulls in 3D or more dimensions, especially if you already use DGtal; pick Delaunay32, gDel3D or HXT for triangulations.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | DGtal headers (DGtal 2.x is 'almost header only'), Boost headers (fetched via CPM at CMake time), zlib and Eigen as required DGtal build dependencies; the QuickHull core itself uses only DGtal kernel types and the standard library |
| **Minimum toolchain** | C++20 compiler, CMake 3.20 (DGtal 2.0+); Visual Studio supported per README |
| **Platforms** | any (portable C++, no SIMD); CI covers Linux, macOS and Windows; Python wheels are published to PyPI, though whether QuickHull is exposed there is not documented |
| **Thread safety** | not documented; the implementation is single-threaded and the QuickHull object holds mutable state, so use one instance per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Facets are not simplicial: a facet can be any planar polygon (or higher-dimensional cell), so code expecting CGAL's triangle mesh must triangulate the facets itself
- Roughly half of total time goes to duplicate removal (a sort over the input, 4.2 s of 7.9 s for 1e7 points); pass remove_duplicates = false to setInput only if your input is known to be duplicate-free
- Choose CoordinateInteger and InternalInteger to fit your coordinate range and dimension; overflow is not an exception but a bad status (InvalidRidge or InvalidConvexHull) that you must check
- The rational kernels round coordinates to multiples of 1/precision, so distinct real points can collapse into one vertex, and too large a precision overflows int64

## Known shortcomings

- Claim is one '&gt;2x vs CGAL convex_hull_3' sentence with no CGAL numbers (C/D border); its own docs say Delaunay mode is 5-10x slower than CGAL.
- The &gt;2x vs CGAL claim has no CGAL numbers and no CGAL benchmark in the repo; DGtal's own docs say Delaunay via the lifted hull is 5-10x slower than CGAL. Overflow is reported only as a status (InvalidRidge/InvalidConvexHull), not an error. Needs C++20, Boost headers, zlib and Eigen.

## Caveats and trade-offs

The claim is a single qualitative sentence, repeated in the module docs, with no CGAL numbers, point distributions, flags or compiler. The only timings are DGtal's own, on a MacBook Pro i7 2.7 GHz quad-core. Only the 3D convex hull is claimed faster. The docs themselves say the Delaunay use is 5-10x slower than CGAL's Delaunay triangulation. Unlike CGAL, the hull is not simplicial (facets may be polygons). The exact lattice kernels are about 25x slower when BigInteger is used for the internal integers. The QuickHull module is part of the much larger LGPL DGtal library.

Part of the DGtal digital-geometry library, so using it pulls in DGtal and its dependencies. Facets are not necessarily triangles/simplices in the output, unlike CGAL's simplicial hull. Kernel is selectable, with an exact integral kernel for lattice points. Not tailored for incremental or dynamic hulls. LGPL.

## Maintenance

Actively maintained (DGtal 2.1 released and 2.1.1 in development, last commit 2026-09-23, 398 stars, SGP 2016 Software Award), LGPL-3.0, with QuickHull present since DGtal 1.2; there are no QuickHull-specific issues, but you must take the whole DGtal library to use it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The QuickHull.h doc comment and the module documentation source (src/DGtal/geometry/doc/moduleQuickHull.dox) both say only 'generally more than twice faster than CGAL convex_hull_3' for the Cartesian and EPICK kernels. Neither gives CGAL timings, point counts or a benchmark program. This first-party ratio claim without methodology sits at the C/D border; it is kept at C because a &gt;2x figure is stated.
- **Verifier notes:** The claim is verbatim in QuickHull.h (lines 131-133) and in moduleQuickHull.dox, which I read from the source tree instead of the unreachable rendered docs page. I added the docs' own counter-statement that Delaunay is 5-10x slower than CGAL, and the DGtal-only timings. LGPL-3.0-or-later (file header), 398 stars, last commit 2026-09-23 and not a fork confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/src/DGtal/geometry/tools/QuickHull.h>
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/src/DGtal/geometry/doc/moduleQuickHull.dox>
  - <https://github.com/DGtal-team/DGtal>
  - <https://github.com/DGtal-team/DGtal/commits>
- **Sources the enricher read:**
  - <https://github.com/DGtal-team/DGtal>
  - <https://github.com/DGtal-team/DGtal/issues?q=quickhull>
  - <https://github.com/DGtal-team/DGtal/issues?q=is%3Aissue%20convex%20hull>
  - <https://github.com/DGtal-team/DGtal/tree/main/examples/geometry/tools>
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/src/DGtal/geometry/tools/QuickHull.h>
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/src/DGtal/geometry/tools/QuickHullKernels.h>
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/src/DGtal/geometry/doc/moduleQuickHull.dox>
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/src/DGtal/geometry/volumes/ConvexityHelper.h>
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/README.md>
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/ChangeLog.md>
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/cmake/CheckDGtalDependencies.cmake>
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/examples/geometry/tools/checkLatticeBallQuickHull.cpp>
  - <https://raw.githubusercontent.com/DGtal-team/DGtal/HEAD/examples/geometry/tools/exampleLatticeBallQuickHull3D.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/dgtal-team/dgtal`) · [data/wave8/enrich/raw/github_com_dgtal_team_dgtal.json](../../../data/wave8/enrich/raw/github_com_dgtal_team_dgtal.json) (enrichment confidence 0.7)

</details>
