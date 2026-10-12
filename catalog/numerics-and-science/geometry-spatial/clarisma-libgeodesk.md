# GeoDesk (libgeodesk)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `LGPL-3.0` · 🟢 active

> Embedded C++20 query engine over memory-mapped OpenStreetMap GOL files; claims 50x faster queries than an SQL database.

| | |
|---|---|
| **Beats** | SQL-based geospatial databases (README says 'SQL'; PostgreSQL/PostGIS is implied but not named) |
| **Claimed result** | Queries 'typically 50 times faster than SQL'; converting .osm.pbf to a GOL is '20 times faster than an import into an SQL database'; GOL files are 20% to 50% larger than the source PBF, 'less than a tenth of the storage consumed by a traditional SQL-based database'. |
| **Workload** | Feature queries (tag and spatial) on OpenStreetMap data in an in-process GOL file, plus GOL build time and storage size, versus a SQL-based database; no workload, dataset or hardware is described in the README. |
| **Metric** | throughput |
| **Adoption** | 20 stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/clarisma/libgeodesk) · [benchmark](https://github.com/clarisma/libgeodesk) |

## Verdict

Only first-party README slogans exist: queries 'typically 50 times faster than SQL', GOL build '20 times faster than an import into an SQL database', and GOL files 20% to 50% larger than the source PBF and under a tenth of SQL storage, with no hardware, compiler, dataset or named database. The repo's Catch2 benchmark times 1,000 containing() queries on Western European admin areas and a count of all US buildings, GeoDesk only, with no SQL baseline.

## Use it when

- Repeated tag-plus-area queries over OSM extracts (country or planet) from a C++ program, where running and importing into PostGIS is the alternative.
- Desktop or batch tools that need OSM relation semantics (route members, multipolygon areas, parent relations) without an SQL schema.
- Low-ops deployments: a single read-mostly file, no database server, any 64-bit Windows, Linux or macOS machine.
- Region-scoped workflows that can download pre-made tiles instead of processing a full planet PBF.

## Skip it when

- Non-OSM geometry: it indexes only GOL-encoded OSM features, not your own polygons or point clouds; use TG, GEOS or an R-tree library for those.
- When you need the claimed speedup proven: the README ratios (50x queries, 20x import, under one tenth of SQL storage) have no methodology, hardware, dataset or named database, and the repo's only benchmark times GeoDesk alone against hard-coded local Windows paths.
- Heavy transactional writes or arbitrary SQL joins and aggregates; the engine is a read-mostly query API.
- Toolchains without solid C++20 support or projects that cannot accept LGPL-3.0 linking terms; an open issue (#34) lists GCC 14.3 / Clang 19 install and link failures on Linux.
- Regional extracts where area relations may be incomplete: open bug #43 says such relations can still match as areas (false positives).

## How it is fast

The GOL file is memory-mapped (clarisma::FreeStore over MemoryMapping) and queried in place, with no row decoding or ORM layer. Data is partitioned into a tile pyramid walked depth-first against the query box (TileIndexWalker), and each tile holds separate spatial indexes for nodes, ways, areas and relations, each an R-tree whose branches carry a bitmask of indexed tag keys so branches lacking the queried keys are skipped before any bounding-box test. Tag queries are compiled into matchers, strings are interned in a global string table, and tiles are scanned in parallel by a thread-pool of TileQueryTask workers.

## Compared with alternatives

Pick it when the data is OpenStreetMap and the alternative is an osm2pgsql/PostGIS import; TG or GeoToolbox are better when you need fast predicates or indexes over your own geometries rather than an OSM feature store.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | gtl (greg7mdp, fetched by CMake); optional GEOS and GDAL/OGR; Catch2 for tests; Java 16+ for the separate gol build tool |
| **Minimum toolchain** | C++20, CMake 3.14+ |
| **Platforms** | 64-bit Windows, Linux, macOS |
| **Thread safety** | Single-threaded query access by default; the CMake option GEODESK_MULTITHREADED enables sharing one GOL across threads (atomic refcounts). Each query internally fans tile scans out to a thread pool. |
| **Drop-in for the baseline** | no |

## Gotchas

- Builds a static library by default (BUILD_SHARED_LIBS forced OFF in CMakeLists.txt); shared builds need GEODESK_SHARED handling.
- RelWithDebInfo builds strip NDEBUG (-U NDEBUG), so assertions stay on; benchmark with Release.
- Without the GOL tool (Java) you cannot create GOL files from .osm.pbf; an open issue (#36) asks for in-process conversion.
- Open todo issues note missing guards for truncated files (#40) and extremely large GOQL queries (#42), and a reported segfault when a .gol file is not found (#34).

## Known shortcomings

- README slogans only ('50x faster than SQL', database unnamed); benchmark_main.cpp has no SQL baseline and hard-coded d:\ paths.
- The 50x/20x README ratios have no methodology and cannot be reproduced. Open #43: incomplete area relations in regional extracts match as false positives. #34: Linux build/link failures (GCC 14.3, Clang 19) and a segfault when the .gol file is missing. Borderline category: an OSM feature store, not a geometry library.

## Caveats and trade-offs

First-party marketing ratios with no methodology, hardware, compiler or named baseline. 'SQL' and 'traditional SQL-based database' presumably mean PostGIS/osm2pgsql, but the README does not say so. benchmark/benchmark_main.cpp (inspected) has two Catch2 benchmarks that time only GeoDesk: 1,000 containing(Coordinate) queries on admin areas over Western Europe, and counting all buildings in the United States. They read hard-coded local Windows GOL paths (d:\geodesk\tests\\*.gol) and contain no SQL comparison. The same three claims appear in the Java sibling repo clarisma/geodesk (201 stars, Apache-2.0), so the claim comes from the GeoDesk project as a whole, not from libgeodesk's C++ code specifically. geodesk.com was EGRESS_BLOCKED. Narrow OSM-only domain, and the baseline is not one of Boost.Geometry, CGAL, GEOS or R-tree, so the category fit is borderline; low confidence.

Read-mostly embedded query engine on its own GOL file format for OpenStreetMap data, not a general geometry library; optional GEOS integration for buffer, union and similar operations; C++20; the GOL tool needs Java; query engine adds under 250 KB per the README.

## Maintenance

Actively developed by one main author (last commit 2026-09-28, 186 commits, 20 stars) with Java and Python siblings; LGPL-3.0-only, so check the license's relinking terms before shipping the default static build inside a closed-source product.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states only first-party ratios ('typically 50 times faster than SQL'; GOL build '20 times faster than an import into an SQL database'; under a tenth of SQL storage). It gives no methodology, hardware or named database. The repo's only benchmark (benchmark/benchmark_main.cpp) times GeoDesk queries alone, with no SQL baseline, so this is C at best.
- **Verifier notes:** README claims verified verbatim and benchmark_main.cpp read: it has no SQL baseline. Metadata matches: LGPL-3.0 (sources carry SPDX LGPL-3.0-only), 20 stars, not archived, last commit 2026-09-28. Kept at C under the 'numbers without methodology' rule, though the numbers are slogan-level.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/README.md>
  - <https://github.com/clarisma/libgeodesk>
  - <https://github.com/clarisma/libgeodesk/tree/main/benchmark>
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/benchmark/benchmark_main.cpp>
  - <https://github.com/clarisma/libgeodesk/commits/main>
  - <https://raw.githubusercontent.com/clarisma/geodesk/HEAD/README.md>
  - <https://github.com/clarisma/geodesk>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/README.md>
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/benchmark/benchmark_main.cpp>
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/src/query/Query.cpp>
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/src/query/TileQueryTask.cpp>
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/src/query/TileIndexWalker.cpp>
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/include/geodesk/query/Query.h>
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/include/geodesk/query/TileQueryTask.h>
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/include/geodesk/query/TileIndexWalker.h>
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/include/geodesk/feature/FeatureStore.h>
  - <https://raw.githubusercontent.com/clarisma/libgeodesk/HEAD/include/clarisma/libero/FreeStore.h>
  - <https://github.com/clarisma/libgeodesk>
  - <https://github.com/clarisma/libgeodesk/tree/main/src>
  - <https://github.com/clarisma/libgeodesk/tree/main/src/query>
  - <https://github.com/clarisma/libgeodesk/tree/main/include/geodesk/query>
  - <https://github.com/clarisma/libgeodesk/commits/main>
  - <https://github.com/clarisma/libgeodesk/issues>
  - <https://github.com/clarisma/libgeodesk/issues/43>
  - <https://github.com/clarisma/libgeodesk/issues/34>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/clarisma/libgeodesk`) · [data/wave8/enrich/raw/github_com_clarisma_libgeodesk.json](../../../data/wave8/enrich/raw/github_com_clarisma_libgeodesk.json) (enrichment confidence 0.6)

</details>
