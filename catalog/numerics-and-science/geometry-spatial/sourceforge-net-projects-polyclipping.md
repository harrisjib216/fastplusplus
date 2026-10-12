# Clipper (Clipper1 / polyclipping 6.4.2)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSL-1.0` · 🔴 abandoned

> Clipper1: two-file C++ Vatti polygon clipper and offsetter on integer coordinates; reported faster than Boost.Geometry on simple Booleans.

| | |
|---|---|
| **Beats** | Boost.Geometry (polygon intersection/union) |
| **Claimed result** | No numbers seen (search snippet only): 'Clipper is the fastest followed by Boost.Geometry, Sql Server ST and TerraLib'; in a longer test 'Boost.Geometry is the fastest' while 'Clipper starts better'; Boost.Geometry and GEOS give the best performance as the number of intersections increases. |
| **Workload** | Third-party blog benchmark (rogue-modron.blogspot.com, 'Polygon Clipping: a Wrapper, a Benchmark', posted 2011-04, last updated 2013-03-04 per search snippet). Nine C/C++ polygon clipping libraries (Boost.Geometry, Boost.Polygon, Bop, CGAL, Clipper, GEOS, GPC, KBool, TerraLib) were wrapped for use from .NET and compared with SQL Server spatial types. Per snippet the versions were Clipper 5.1.2, Boost 1.53, GEOS 3.3.7 and TerraLib svn 10190. Per-test inputs are unknown. |
| **Metric** | throughput |
| **Adoption** | 100,000+ lifetime SourceForge downloads ('Open Source Excellence' badge); about 7,300 downloads per week, almost all of clipper_ver6.4.2.zip; user rating 4.8/5 (SourceForge page) |
| **Links** | [repository](https://sourceforge.net/projects/polyclipping/) |

## Verdict

The only comparison is a third-party .NET-wrapper benchmark of nine C/C++ clipping libraries (Clipper 5.1.2, Boost 1.53, GEOS 3.3.7, among others), seen only through search snippets: Clipper was fastest in one test, followed by Boost.Geometry, but Boost.Geometry won a longer test and scaled better with more intersections. No numbers, compiler, flags or hardware were visible, and every timing includes .NET marshalling.

## Use it when

- Legacy C++ code (or C#/Delphi) already on ClipperLib 6.x, especially via the many third-party ports bundled in the zip (Python, Java, Go, Ruby, Lua, Matlab and others), where switching APIs is not worth it.
- Polygon Booleans with few edge crossings per scanline, such as clipping to tiles or windows and unioning modest shape sets, the case where the third-party wrapper benchmark had Clipper ahead of Boost.Geometry.
- Offsetting closed or open paths with square, round or miter joins and butt, square or round ends, using integer-scaled CAD, CNC, PCB or 2D game geometry.
- Projects that want a BSL-1.0 two-file source drop (clipper.hpp + clipper.cpp) with no dependencies beyond the C++ standard library.

## Skip it when

- New code: the SourceForge page marks Clipper1 obsolete and unmaintained, superseded by Clipper2 (same author, BSL-1.0); among catalogued siblings, clipper2next reports about 1.6x over Clipper2 on intersection and union.
- Inputs with many intersections, or long multi-stage tests: the same snippet-only benchmark says Boost.Geometry was fastest in a longer test and Boost.Geometry and GEOS scale better as intersection counts grow. The per-scanbeam bubble sort over active edges is consistent with that.
- Floating-point workflows that cannot accept snapping to an integer grid: rounding can leave tiny self-intersection artefacts that need CleanPolygons or StrictlySimple.
- You need validity repair, spatial predicates, buffering on a sphere or OGC semantics: it only clips and offsets planar paths; GEOS-class work fits qdgeo or GeoRepair better.
- You need a reproducible speed claim: no benchmark with numbers, compiler or hardware could be opened, so the evidence is tier D.

## How it is fast

It implements Bala Vatti's scanline clipping algorithm: local minima are sorted once, a std::priority_queue of scanbeam Y values drives the sweep, and an active edge list is updated per scanbeam, with crossings found by bubble-sorting the active edges at the top of each beam. All coordinates are integers (64-bit by default), and 128-bit multiplication (an internal Int128 class) is used only when a coordinate exceeds +/-0x3FFFFFFF, so most inputs run on plain 64-bit math. The docs quote about 10% more speed for flat Paths output instead of PolyTree and 20-30% for the use_int32 build.

## Compared with alternatives

Pick Clipper1 only when you are tied to its API or one of its language ports; for new work, Clipper2 or clipper2next are the maintained successors, and CavalierContours is faster for arc-aware offsetting (3.5x to 4x on its square and pathological profiles, though slower on others).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | C++98-era code; CMake 2.6 build script (shared library by default, SOVERSION 22) |
| **Platforms** | any |
| **Thread safety** | not documented; all sweep state lives in each Clipper/ClipperOffset object (no static mutable state seen in clipper.cpp), so one object per thread is the safe assumption |
| **Drop-in for the baseline** | no |

## Gotchas

- Coordinate limits in the 6.4.2 code differ from the docs: the fast range is +/-0x3FFFFFFF and the hard limit +/-0x3FFFFFFFFFFFFFFF (about 4.6e18); with use_int32 the code limit is +/-0x7FFF (32,767), stricter than the documented +/-46,340. Out-of-range points make AddPath throw clipperException.
- Errors are reported by throwing clipperException (derived from std::exception), including internal errors such as 'ProcessIntersections error' and 'DoMaxima error'.
- Open paths must be added as subjects and need PolyTree output for line clipping; adding them as clip paths throws.
- The 6.x API renamed Polygon/Polygons to Path/Paths and replaced OffsetPolygons with ClipperOffset, so older 4.x/5.x snippets and benchmarks (the third-party one used 5.1.2) do not compile unchanged.

## Known shortcomings

- Obsolete (last release 2017-02-27; superseded by Clipper2). The cited benchmark tested Clipper 5.1.2, not 6.4.2, through .NET wrappers; blog and svn.osgeo.org blocked here, so snippet only.
- Code limits differ from the docs: use_int32 caps coordinates at 0x7FFF (32,767) while the docs say 46,340; the hard limit is 4.6e18 while the docs say 9.2e18. SourceForge lists 6.4.2 as 2024-01-09 but the changelog and header say 2017-02-27.

## Caveats and trade-offs

Snippet only: the blog page returned EGRESS_BLOCKED, so no numbers, flags or hardware were seen, hence tier D. Per search snippets, the benchmark tested Clipper 5.1.2 (not 6.4.2) through .NET wrappers, so marshalling overhead is in every time, and the author warned it may contain errors and did not consider robustness or optimization. The same snippet says Boost.Geometry wins in a longer test and when many intersections occur, so the win is workload dependent. The SourceForge page itself has no performance claims. It marks the project obsolete and no longer maintained, superseded by Clipper2 (github.com/AngusJohnson/Clipper2, a separate rewrite). The last file release, clipper_ver6.4.2.zip, is dated 2017-02-27. A copy of the OSGeo FOSS4G geometry-libraries benchmark (svn.osgeo.org) was also EGRESS_BLOCKED.

Vatti-style clipping and offsetting on integer coordinates; the SourceForge page says this library is obsolete and no longer maintained, superseded by Clipper2 (github.com/AngusJohnson/Clipper2, BSL-1.0, 2.5k stars, last commit 2026-04-20 as opened; its README makes no comparative performance claims and warns its triangulation code is buggy).

## Maintenance

Abandoned: last release 6.4.2 (27 Feb 2017, changelog and header date), marked obsolete in favour of Clipper2, but BSL-1.0, dependency-free and about 5,000 lines, so it is easy to vendor and still downloaded about 7,300 times a week.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** benchmark_url is null, and the only comparison (the rogue-modron.blogspot.com wrapper benchmark) is EGRESS_BLOCKED, so it was seen only through search snippets with no numbers. The SourceForge page makes no performance claim, so the tier stays D. Clipper is kept, not rejected as not-notable, because it is very widely used (100,000+ SourceForge downloads, about 7,300 downloads per week).
- **Verifier notes:** Could not open any numbers page: the blog and svn.osgeo.org are both blocked. Kept at D on snippet evidence; a session with blogspot access should re-check for B. The SourceForge page confirms BSL-1.0, v6.4.2 and an obsolete/unmaintained status (abandoned: last release 2017-02-27). last_commit was left null because SourceForge shows file dates, not commits.
- **Fields the verifier corrected:** `stars_or_usage`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://sourceforge.net/projects/polyclipping/>
  - <https://sourceforge.net/projects/polyclipping/files/>
- **Sources the enricher read:**
  - <https://sourceforge.net/projects/polyclipping/>
  - <https://sourceforge.net/projects/polyclipping/files/clipper_ver6.4.2.zip/download>
  - clipper_ver6.4.2.zip: README (change log)
  - clipper_ver6.4.2.zip: cpp/clipper.hpp
  - clipper_ver6.4.2.zip: cpp/clipper.cpp
  - clipper_ver6.4.2.zip: cpp/CMakeLists.txt
  - clipper_ver6.4.2.zip: Documentation/Docs/Overview/_Body.htm
  - clipper_ver6.4.2.zip: Documentation/Docs/Overview/FAQ.htm
  - clipper_ver6.4.2.zip: Documentation/Docs/Overview/Rounding.htm
  - clipper_ver6.4.2.zip: Documentation/Docs/Units/ClipperLib/Types/CInt.htm
  - clipper_ver6.4.2.zip: Documentation/Docs/Units/ClipperLib/Classes/Clipper/Methods/Execute.htm
  - clipper_ver6.4.2.zip: Documentation/Docs/Units/ClipperLib/Classes/ClipperBase/Methods/AddPath.htm
  - <https://raw.githubusercontent.com/AngusJohnson/Clipper2/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://sourceforge.net/projects/polyclipping`) · [data/wave8/enrich/raw/sourceforge_net_projects_polyclipping.json](../../../data/wave8/enrich/raw/sourceforge_net_projects_polyclipping.json) (enrichment confidence 0.6)

</details>
