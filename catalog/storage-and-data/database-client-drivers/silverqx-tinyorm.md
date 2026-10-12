# TinyORM (TinyDrivers MySQL driver)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Database client drivers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Qt-based C++20 ORM whose own MySQL driver layer replaces QtSql/QMYSQL; measured gain is marginal (\~40 ms per 620 queries).

| | |
|---|---|
| **Beats** | QtSql with the QMYSQL driver |
| **Claimed result** | 'Performance is several milliseconds faster compared to QtSql with the QMYSQL driver ... It's \~40ms faster on TinyOrmPlayground project with 620 database queries'; the same page then says performance is 'very similar to QtSql' because 90% of the time is spent inside the MySQL C API. |
| **Workload** | Elapsed time of the TinyOrmPlayground project, 620 MySQL queries, TinyDrivers (TinyORM's own QtSql replacement) vs QtSql/QMYSQL. |
| **Metric** | latency |
| **Compiler and flags** | GCC v13.2.1, Debug build, Linux |
| **Adoption** | 353 stars, 37 forks |
| **Last commit** | 2024-08-26 |
| **Links** | [repository](https://github.com/silverqx/TinyORM) · [benchmark](https://github.com/silverqx/TinyORM/blob/main/docs/tinydrivers/getting-started.mdx) |

## Verdict

The author reports that TinyOrmPlayground (620 MySQL queries) finished about 40 ms sooner with TinyDrivers/TinyMySql than with QtSql/QMYSQL, built with GCC 13.2.1 in Debug mode on Linux, one run, no CPU model, no total runtime and no variance; the same page calls the two 'very similar' because 90% of the time is spent in the MySQL C API. Roughly 65 microseconds per query of driver overhead at most, with the timer also covering connection setup and console logging.

## Use it when

- You already use TinyORM with MySQL or MariaDB and want to drop the QtSql module (smaller Qt footprint, fewer Qt plugins to deploy).
- You want MySQL connection options QMYSQL handles awkwardly, such as valueless non-flag options or MYSQL_OPT_SSL_MODE verify_ca / verify_identity.
- You prefer exceptions over QtSql's bool-plus-lastError() error reporting in a Qt 6, C++20 code base built on MSVC, GCC 11.2-14.2 or Clang 15+ (libstdc++).
- You need a static, shared or runtime-loadable (dlopen / LoadLibrary) driver build that you control instead of Qt's plugin loader.

## Skip it when

- You want measurable query-latency gains: the author's own conclusion is that performance is 'very similar to QtSql'; database round trips dominate.
- You use PostgreSQL or SQLite through TinyORM: TinyDrivers implements MySQL only, so those databases still need QtSql.
- You need multiple result sets: SqlQuery::nextResult() is not implemented (only the first result set of a multi-statement query can be fetched).
- You target macOS or Clang with libc++: unsupported per the supported-compilers page; Qt 5 support was dropped in v0.38.0.
- You need an actively developed driver: the last commit is 2024-08-26 and TinyDrivers is v0.2.0; the official vcpkg port does not include it.

## How it is fast

There is no new algorithm: TinyMySql is a thin, KCacheGrind-tuned wrapper over the MySQL C API (mysql_real_query plus mysql_store_result for normal queries, mysql_stmt_\* with bound buffers for prepared ones). Its small savings come from avoiding some per-value conversions, e.g. integer columns from prepared statements are built straight into a QVariant from the bound buffer without a QString::fromUtf8 round trip, and binding buffers are pre-reserved. The author states that about 90% of the time is spent inside the MySQL C API waiting on the server, so the driver layer has little left to speed up.

## Compared with alternatives

No siblings catalogued yet in database-client-drivers; within the catalogue the closest neighbour is ODB (a compiled C++ ORM), and TinyDrivers is only worth picking if you are already on TinyORM and Qt and want to shed QtSql, not for speed.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (also a runtime-loadable TinyMySql module), built with CMake &gt;=3.22 or qmake |
| **Dependencies** | QtCore (Qt &gt;=6.2), range-v3 &gt;=0.11.0, tabulate, MySQL Connector/C (libmysql/mysqlclient) or MariaDB Connector/C; QtSql is not needed when TinyDrivers is enabled |
| **Minimum toolchain** | C++20; MSVC 2019 16.9+ / 2022, GCC 11.2-14.2, Clang 15+ with libstdc++, clang-cl 15+ |
| **Platforms** | Windows 10+ and Linux; macOS and libc++ not supported |
| **Thread safety** | A connection may be used only from the thread that created it; multi-threading is disabled on Clang &lt;14.0.3 (MSYS2), Clang &lt;14.0.4 (Linux) and GCC on MSYS2 because of thread_local TLS-wrapper bugs; the schema builder and migrations are not thread-safe. TinyMySql calls mysql_thread_end() when a thread's connection is torn down. |
| **Drop-in for the baseline** | partial: 1:1 QtSql API swapped at compile time for TinyORM users, but MySQL only, errors are thrown as exceptions (bool-returning methods always return true), exec(QString) no longer simulates prepared statements, and nextResult() is missing |

## Gotchas

- Error semantics differ from QtSql: code that checks a false return and then lastError() will never see the error, because TinyDrivers throws instead.
- Normal and prepared queries always buffer the whole result set on the client (mysql_store_result / mysql_stmt_store_result); there is no streaming mode, so very large SELECTs cost client memory.
- Harness flaw behind the 40 ms figure: TinyOrmPlayground's only timer (QElapsedTimer in src/main.cpp) wraps the whole run, including connectToDatabase(), connection creation and per-query console logging with title headers, against a live MySQL server, in a Debug build, one run; the total time is never published, so the gap cannot be separated from server and logging noise.
- The playground has since grown to \~1600 queries (TinyORM README), so the 620-query configuration behind the claim is no longer the default and cannot be re-run from published material.

## Known shortcomings

- Tier C: the TinyDrivers quote (about 40 ms faster than QtSql QMYSQL over 620 queries, no total time) comes from getting-started.mdx and the author calls it near parity; one Debug-build run with no CPU model; TinyOrmPlayground has no timing harness; database-client-drivers is outside the wave 6 categories. Stale (last commit 2024-08-26).
- Enricher: gain marginal (author says 'very similar to QtSql'); the TinyOrmPlayground harness has one QElapsedTimer around the whole run (connectToDatabase, connection setup, per-query console logging, live MySQL server), Debug build, one run, no total published, and the playground now runs about 1600 queries so the 620-query configuration is not rerunnable. MySQL only, no nextResult(), throws instead of bool/lastError(), always mysql_store_result. Code stale since 2024-08-26.

## Caveats and trade-offs

Weak claim: first-party, one run, Debug build (tier capped at C), no CPU model, no run-to-run variance, no total elapsed time (so no ratio can be derived), and the author concludes the two are 'very similar' because 90% of the time is spent inside the MySQL C API. The speed-up is about 40 ms on 620 queries (roughly 65 microseconds per query, tuned with KCacheGrind) and is driver overhead, not database work. The README's other claim ('1000 complex queries in 500ms, heavily DB dependent, the PostgreSQL is by far the fastest') has no baseline. The benchmark program, silverqx/TinyOrmPlayground (public, MIT, 0 stars, 444 commits), has build manifests for both TinyDrivers and QtSql but no timing harness or results in its README, so the 40 ms cannot be reproduced from published material. Category 'database-client-drivers' is outside the six wave-6 categories; the seed line guessed embedded-kv. Last commit 2024-08-26 (commits/main page); the repo shows 5,739 commits.

TinyDrivers currently supports MySQL only and is swapped for QtSql at compile time with a 1:1 API; TinyORM itself is a C++20 Eloquent-style ORM that depends on Qt. The official vcpkg port excludes TinyDrivers.

## Maintenance

Stale: no commits since 2024-08-26 (5,739 commits; maintainer still closing issues in 2025, e.g. #69 in Sep 2025), MIT-licensed and copyable, but tied to Qt 6 and TinyORM's own build system, with open Windows build/dllexport issues (#55, #61, #63, #65).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/tinydrivers/getting-started.mdx (Performance section) gives a first-party '\~40ms faster' figure on 620 queries against QtSql/QMYSQL, measured once on a GCC 13.2.1 Debug build with no CPU model and no total runtime; a Debug build caps the tier at C. The workload program (silverqx/TinyOrmPlayground) is public but has no timing harness or published results.
- **Verifier notes:** Claim matches the Performance section of getting-started.mdx word for word; tier C stands; metadata confirmed (MIT, 353 stars, 37 forks, last commit 2024-08-26, stale). Shortcomings to record: effectively parity with QtSql/QMYSQL by the author's own conclusion (\~40 ms over 620 queries, no total time), single first-party Debug-build run with no CPU model, workload program public but without a timing harness, and category database-client-drivers is not a wave-6 category (orchestrator must file it, e.g. by category override).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-88 (wave 6); enricher w6 pair-018
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/docs/tinydrivers/getting-started.mdx>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/README.md>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/LICENSE>
  - <https://github.com/silverqx/TinyORM>
  - <https://github.com/silverqx/TinyORM/commits/main>
  - <https://github.com/silverqx/TinyOrmPlayground>
- **Sources the enricher read:**
  - <https://github.com/silverqx/TinyORM>
  - <https://github.com/silverqx/TinyORM/commits/main>
  - <https://github.com/silverqx/TinyORM/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/README.md>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/docs/tinydrivers/getting-started.mdx>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/docs/dependencies.mdx>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/docs/supported-compilers.mdx>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/docs/stability.mdx>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/docs/database/getting-started.mdx>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/LICENSE>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/vcpkg.json>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/drivers/mysql/src/orm/drivers/mysql/mysqldriver_p.cpp>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/drivers/mysql/src/orm/drivers/mysql/mysqlresult.cpp>
  - <https://raw.githubusercontent.com/silverqx/TinyORM/main/drivers/mysql/src/orm/drivers/mysql/mysqlresult_p.cpp>
  - <https://github.com/silverqx/TinyOrmPlayground>
  - <https://raw.githubusercontent.com/silverqx/TinyOrmPlayground/main/src/main.cpp>
  - <https://raw.githubusercontent.com/silverqx/TinyOrmPlayground/main/src/configuration.hpp>
  - <https://raw.githubusercontent.com/silverqx/TinyOrmPlayground/main/src/configuration.cpp>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/silverqx/tinyorm`) · [data/wave6/enrich/raw/github_com_silverqx_tinyorm.json](../../../data/wave6/enrich/raw/github_com_silverqx_tinyorm.json) (enrichment confidence 0.6)

</details>
