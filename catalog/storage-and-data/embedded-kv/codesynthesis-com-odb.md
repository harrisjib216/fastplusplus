# ODB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `C++` · `GPL-2.0-only or commercial (libodb, libodb-sqlite, libodb-pgsql, libodb-mysql, libodb-qt, libodb-boost); GPL-3.0-only (odb compiler); NCUEL non-commercial or commercial (libodb-oracle, libodb-mssql); Unlicense (odb-example)` · 🟢 active

> Code-generating C++ ORM for MySQL, SQLite, PostgreSQL, Oracle and SQL Server; its 2x-over-Dapper claim compares different databases.

| | |
|---|---|
| **Beats** | Hand-coded ADO.NET SqlDataReader and Dapper (C#/.NET micro-ORM), using Dapper's published 500-object SELECT benchmark |
| **Claimed result** | ODB with MySQL 5.1.49 on Linux 24 ms per 500 iterations vs Dapper 47 ms on SQL Server (different machine and database); ODB 1.8.0 on SQL Server 222 ms (Win7) and 152 ms (Win2008R2) per 500, later about 65 ms derived, all slower than Dapper's 49 ms. |
| **Workload** | Dapper's benchmark reimplemented in C++: load 500 randomly chosen post objects (Stack Overflow-style posts table) one by one, timing 500 iterations. |
| **Metric** | latency |
| **Hardware** | ODB side: Intel Xeon E5520 at 2.27 GHz (snippet only). C#/Dapper side: not stated by Dapper (snippet only). |
| **Adoption** | 65 stars, 6 forks, 5,139 commits on GitHub; long-standing C++ ORM with MySQL, SQLite, PostgreSQL, Oracle and SQL Server backends |
| **Last commit** | 2026-07-27 |
| **Links** | [repository](https://github.com/codesynthesis-com/odb) · [benchmark](https://codesynthesis.com/~boris/blog/2011/04/06/performance-odb-cxx-orm-vs-cs-orm/) |

## Verdict

The author ported Dapper's test to C++ (load 500 random Stack Overflow-style post objects one at a time). ODB 1.x on MySQL 5.1.49 under Linux (Xeon E5520 2.27 GHz per snippets) took 24 ms per 500 loads, against Dapper's own published 47 ms for hand-coded SqlDataReader and 49 ms for Dapper on SQL Server, on hardware Dapper did not state. The same author's January 2012 ODB 1.8.0 post ran ODB against SQL Server on Windows and got 222 ms (Windows 7) and 152 ms (Windows Server 2008 R2) per 500 objects; a February 2012 update gave 130 us per object locally, about 65 ms per 500 (derived). Those same-database figures are all slower than Dapper's 49 ms, so the 2x comes from comparing MySQL with SQL Server, not ODB with Dapper (search snippets only; codesynthesis.com was unreachable, and no benchmark source, compiler or flags were found).

## Use it when

- C++ applications that store typed domain objects (with relationships, inheritance, containers) in MySQL, PostgreSQL or SQLite and want the mapping code generated instead of hand-written binding code
- Code that must run against several databases from one model: ODB supports multi-database builds (static or dynamic) and generates per-database schema
- Load-by-id and query-heavy workloads where statement preparation and binding overhead matter: statements are prepared once per connection and reused
- Long-lived schemas: ODB has built-in schema versioning and migration, including SQLite version-aware DDL in 2.6.0

## Skip it when

- Closed-source products that cannot pay for a licence: the runtimes are GPL-2.0-only or commercial, and the Oracle and SQL Server runtimes are non-commercial-use only (NCUEL) unless you buy a licence
- Toolchains without a GCC that has plugin support (gcc-N-plugin-dev): the ODB compiler is a GCC plugin, needs GCC 5 or later on the build host, and on Windows needs MinGW GCC even when the target uses MSVC
- Projects that need key-value storage or an embedded engine: ODB is a mapping layer over an SQL database, not a storage engine, so it cannot compete with the key-value siblings on raw throughput
- Teams that want a header-only or reflection-based library with no extra code-generation step in the build
- Anyone choosing it on the Dapper comparison: on SQL Server (the database Dapper used) the author's own 2012 figures are slower than Dapper's published numbers

## How it is fast

The mapping is generated at build time, so there is no runtime reflection or string-keyed column lookup. Generated per-class bind buffers go straight into each database's native C API: the MySQL runtime uses the binary prepared-statement protocol (mysql_stmt_prepare, mysql_stmt_bind_param/bind_result, mysql_stmt_fetch), and SQLite uses sqlite3_bind/step. Prepared statements are built once per connection and kept in a statement_cache keyed by type_info, connections are pooled, and an optional session cache avoids reloading objects already in memory. Explicit prepared queries, bulk persist/update/erase (Oracle and SQL Server only) and, since 2.6.0, direct loading of containers of object pointers in one SELECT (to avoid the N+1 problem) reduce round trips further.

## Compared with alternatives

None of the embedded-kv siblings (LMDB, LevelDB, RocksDB derivatives, NuDB, UnQLite) is an ORM. Pick ODB when the data belongs in an SQL database (SQLite, PostgreSQL, MySQL) and you want generated, prepared-statement C++ mapping code. Pick a sibling such as LMDB or LevelDB when you need a fast byte-level key-value engine and can write your own serialisation.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Build host: ODB compiler (GPL-3.0) built as a GCC plugin, needing GCC 5+ with plugin headers, libcutl and libstudxml; build2 0.18+ is the supported build system (other build systems via 'Installing ODB with build2'). Target: libodb plus libodb-sqlite (libsqlite3), libodb-pgsql (libpq), libodb-mysql (libmysqlclient or MariaDB), libodb-oracle (OCI) or libodb-mssql (SQL Server ODBC driver); optional libodb-boost, libodb-qt (Qt6 only in 2.6.0). Shared or static runtimes. |
| **Minimum toolchain** | C++11 (2.6.0 dropped C++98); compiler defaults to --std c++11, std::optional mapping needs --std c++17. ODB compiler itself needs GCC 5+ with plugin support; target code can use any compiler. |
| **Platforms** | Linux, macOS, Windows (compiler via MinGW GCC; the manifest excludes non-GCC Windows builds of the compiler and static compiler builds); libodb-mysql and libodb-pgsql are excluded from wasm builds |
| **Thread safety** | The connection pool is mutex- and condition-protected and hands each requesting thread its own connection (waiting threads block when max_connections is reached); the current transaction and current session are per-thread (session.hxx). Per-connection rules (statement cache, session object cache) are in the manual, which was not reachable; not documented in the files read. |
| **Drop-in for the baseline** | no |

## Gotchas

- The SQLite connection pool and new-connection factories turn on SQLite shared-cache mode (SQLITE_OPEN_SHAREDCACHE) unless the database is opened with SQLITE_OPEN_PRIVATECACHE (connection-factory.cxx). SQLite discourages shared cache, and it serialises access at table level, so pass the private-cache flag when using WAL mode.
- The ODB compiler picks up the gcc found on PATH (open issue #37), and new GCC releases can break it (GCC 15 support issue #25, open gcc16 static-assertion issue #34), so pin the GCC used to run ODB.
- Object pointers load lazily by default, one SELECT per pointed-to object (the N+1 problem). Direct loading of containers of pointers arrived only in 2.6.0, and the polymorphic case is still open (issue #27).
- Each database::begin() heap-allocates a transaction implementation, and query parameters and pooled-connection shared_ptr control blocks are also heap-allocated. The author lists these as open ideas in issue #28 with no measurements.

## Known shortcomings

- Tier C, snippet only (codesynthesis.com ENOTFOUND): 24 ms vs hand-coded C# 47 ms and Dapper 49 ms per 500 loads; the ODB side ran on a Xeon E5520 2.27 GHz while the Dapper side is its own published figure on SQL Server with hardware unstated. Usability mixed: libodb-oracle and libodb-mssql are under the NCUEL licence. ORM filed under embedded-kv, a poor fit.
- Enricher: the 2x over Dapper compares ODB on MySQL/Linux with Dapper's SQL Server numbers; the author's own ODB 1.8.0 SQL Server runs (222 ms on Win7, 152 ms on Win2008R2 per 500, later 130 us per object, about 65 ms derived) are all slower than Dapper's 49 ms (snippet only, codesynthesis.com blocked). SQLite pool turns on shared-cache by default; the compiler is a GCC plugin that picks gcc from PATH (#37), gcc 16 break open (#34); NCUEL licence for Oracle and MSSQL; an ORM is off-category in embedded-kv. 2.6.0 released 2026-07-27.

## Caveats and trade-offs

SNIPPET ONLY: codesynthesis.com is unreachable from this session (DNS ENOTFOUND for WebFetch), so the 2011-04-06 blog post and the January 2012 follow-up were never opened; the figures come from WebSearch result summaries, which also say the ODB run used a Xeon E5520 2.27 GHz machine while Dapper's numbers name no hardware. The C# figures (47 ms hand-coded SqlDataReader, 49 ms Dapper) are Dapper's published numbers on a different machine, a different database (SQL Server) and a different language, so the roughly 2x is indicative only. Roughly 15-year-old numbers on MySQL 5.1, PostgreSQL 9.0 and SQLite 3.7; the exact database versions were not re-confirmed in the snippets seen. No benchmark source, compiler or flags were found. The repo carries no benchmark claims, and no comparison against another C++ ORM (sqlpp11, SOCI, sqlite_orm, Wt::Dbo) was found. Licensing is split per package: runtime libraries GPL-2.0-only or commercial, compiler GPL-3.0-only, but the Oracle and SQL Server runtimes are under the non-OSI NCUEL, hence usability mixed. Category embedded-kv does not fit an ORM. [retier] ORM, off-category in embedded-kv; SQLite pool shared-cache by default; GCC-plugin compiler picks gcc from PATH; NCUEL licence for Oracle and MSSQL.

Code-generating ORM: a separate ODB compiler processes annotated C++ headers into persistence code; an ORM mapping layer rather than a raw client. The repo file list shows GPLv2, GPLv3, NCUEL and Unlicense files and the README defers to the product page for terms, so check the licence split before closed-source use.

## Maintenance

Actively maintained by Code Synthesis: 2.6.0 was released on 2026-07-27, the issue tracker is active, and the package manifests name git.codesynthesis.com as the source repository. Usability is mixed because of the GPL-2.0/GPL-3.0/NCUEL-or-commercial licence split, and the only performance evidence is first-party 2011-2012 blog numbers that do not survive a same-database comparison.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party blog numbers (ODB's author) seen only through search-result snippets because codesynthesis.com is unreachable (ENOTFOUND); the snippets confirm ODB 24 ms vs 47 ms hand-coded C# and 49 ms Dapper per 500 iterations, but no benchmark code, compiler or flags were found, and the C# side is Dapper's own figures on unstated hardware with SQL Server. Snippet-only evidence is capped at C.
- **Retiered** C to D: Lowered C to D: the 2x over Dapper compares ODB on MySQL/Linux with Dapper's SQL Server numbers from a different machine and database, and the author's own SQL Server runs are slower than Dapper, so no like-for-like measurement supports a win; directional only.
- **Verifier notes:** Blog post blocked (ENOTFOUND), but two WebSearch snippets corroborate 24 ms vs 47 ms/49 ms per 500 iterations and the PostgreSQL 27 ms / MySQL 24 ms / SQLite 7 ms follow-up; tier C kept on snippet-only evidence; usability corrected to mixed because libodb-oracle and libodb-mssql are NCUEL. Shortcomings to record: snippet-only first-party evidence, cross-language, cross-database (MySQL vs SQL Server) and cross-machine comparison against Dapper's own figures, 2011-era versions, no benchmark code or flags, off-category (ORM filed under embedded-kv).
- **Fields the verifier corrected:** `hardware`, `license`, `usability`, `stars_or_usage`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-88 (wave 6); enricher w6 pair-010
- **Pages the verifier opened:**
  - <https://github.com/codesynthesis-com/odb>
  - <https://github.com/codesynthesis-com/odb/commits/master>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/codesynthesis-com/odb>
  - <https://github.com/codesynthesis-com/odb/commits/master>
  - <https://github.com/codesynthesis-com/odb/issues?q=is%3Aissue>
  - <https://github.com/codesynthesis-com/odb/issues/28>
  - <https://github.com/codesynthesis-com/odb/issues/33>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/README.md>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/LICENSE>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/NEWS>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/packages.manifest>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/PACKAGE-README.md>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/odb/manifest>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/odb/README.md>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/libodb/manifest>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/libodb/README.md>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/libodb-sqlite/manifest>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/odb-tests/README.md>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/libodb/odb/session.hxx>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/libodb-sqlite/odb/sqlite/statement-cache.hxx>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/libodb-sqlite/odb/sqlite/statement.hxx>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/libodb-sqlite/odb/sqlite/connection.hxx>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/libodb-sqlite/odb/sqlite/connection-factory.hxx>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/libodb-sqlite/odb/sqlite/connection-factory.cxx>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/libodb-sqlite/odb/sqlite/database.hxx>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/libodb-sqlite/odb/sqlite/database.cxx>
  - <https://raw.githubusercontent.com/codesynthesis-com/odb/master/libodb-mysql/odb/mysql/statement.cxx>
  - WebSearch snippets of https://codesynthesis.com/\~boris/blog/2011/04/06/performance-odb-cxx-orm-vs-cs-orm/ (fetch failed: getaddrinfo ENOTFOUND)
  - WebSearch snippets of https://www.codesynthesis.com/\~boris/blog/2012/01/31/odb-1-8-0-released/ and https://www.codesynthesis.com/\~boris/blog/2012/02/02/updated-odb-benchmark-results/ (fetch failed: getaddrinfo ENOTFOUND www.codesynthesis.com)
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/codesynthesis-com/odb`) · [data/wave6/enrich/raw/github_com_codesynthesis_com_odb.json](../../../data/wave6/enrich/raw/github_com_codesynthesis_com_odb.json) (enrichment confidence 0.55)

</details>
