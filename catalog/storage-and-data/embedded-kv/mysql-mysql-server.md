# MySQL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `GPL-2.0-only (with Oracle's additional linking permission; libmysqlclient also under the Universal FOSS Exception 1.0)` · 🟢 active

> Oracle's client-server SQL database (InnoDB). It edges PostgreSQL only on sysbench oltp_read_write in one cross-machine, durability-off comparison.

| | |
|---|---|
| **Beats** | PostgreSQL 14.5 (sysbench, PostgreSQL run on a different, larger machine) |
| **Claimed result** | pgtpc oltp_read_write MySQL.48C 900,000 vs PGSQL.48C 722,907 (1.25x, derived) comes from different runs (IO-bound MySQL Optane run vs cached PostgreSQL); with the PG log page's 780,000 figure the lead is about 1.08x. |
| **Workload** | sysbench on 8 tables (10M rows each for oltp_read_only, oltp_read_write and oltp_update_non_index; 50M rows each for oltp_point_select). MySQL 8.0 'extreme config' (checksum, doublewrite, binlog, performance schema and fsync off, latin1) from Oracle's published runs on a 48-core 2.7 GHz box with 2x Optane P4800X, versus PostgreSQL (14.5 per the same machine's normal-config page) with fsync, synchronous_commit and full_page_writes off, wal_level minimal, LATIN1 and prewarmed tables, run by the pgtpc author on AWS c5d.metal with threads forced to 48 (read_write also at 128, point_select swept 1-512). |
| **Metric** | throughput |
| **Hardware** | MySQL side (Oracle's published run): 48 cores at 2.7 GHz, 172 GB, 2x Intel Optane P4800X, CPU model not stated. PostgreSQL side: AWS c5d.metal 96 vCPU at 3.6 GHz, 192 GB, 4x 900 GB ephemeral NVMe. |
| **Adoption** | 12.5k stars, 4.4k forks |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/mysql/mysql-server) · [benchmark](https://github.com/Vonng/pgtpc/blob/master/sysbench/ref-mysql.md) |

## Verdict

The comparison sets Oracle-published MySQL 8.0 sysbench figures (48-core 2.7 GHz box, two Optane P4800X, durability off, latin1) against Vonng's PostgreSQL 14 runs on AWS c5d.metal (fsync, synchronous_commit and full_page_writes off, prewarmed). MySQL leads only on oltp_read_write at 48 threads (900,000 vs 722,907 QPS, 1.25x derived from page data) and trails or ties on point select, read-only and non-index update. No compiler or flags are given for either side, and the point-select row pits an IO-bound MySQL run against an in-memory PostgreSQL run.

## Use it when

- A multi-client, networked OLTP SQL server with mostly point selects and short read-write transactions at high client concurrency (the cited runs drove 48 to 512 sysbench threads)
- Teams already on the MySQL protocol, tooling and replication who want the upstream Oracle server
- Mixed read-write sysbench-style transactions, the one row where the cited table puts MySQL ahead of PostgreSQL
- When an LTS line (8.0, 8.4, 9.7) is needed, since fixes are merged forward from those branches into trunk

## Skip it when

- As an embedded key-value store: there is no in-process engine in trunk, so every operation pays a client-server round trip
- If you are choosing it over PostgreSQL for read throughput: the cited table has PostgreSQL ahead or level on point selects, read-only and non-index updates
- With the settings behind the headline numbers in production: checksums, doublewrite, binlog and fsync off trade crash safety for speed
- Analytical scans and large aggregations: nothing in the cited evidence covers them
- Products that cannot accept GPL-2.0 terms (the extra permissions cover linking with separately licensed parts such as OpenSSL, and the Universal FOSS Exception covers libmysqlclient)

## How it is fast

InnoDB keeps rows in a B+tree clustered on the primary key and caches pages in a buffer pool. An adaptive hash index (btr0sea.cc) builds hash shortcuts over hot B-tree search paths for repeated point lookups. Redo logging is split across dedicated background threads (log writer, log flusher, write and flush notifiers, checkpointer) that user threads wait on by LSN, which lets many concurrent transactions share log writes and fsyncs. The quoted rates come from an 'extreme' configuration with checksums, doublewrite, binlog, performance schema and fsync turned off.

## Compared with alternatives

Among the embedded-kv siblings the only like-for-like peer is the PostgreSQL entry, which cites the same pgtpc page with the opposite conclusion; pick MySQL over it for ecosystem reasons, not on this evidence. LMDB, LevelDB, RocksDB-family engines and SQLite are in-process libraries, so pick MySQL over them only when you need a shared networked SQL server.

## Integration

| | |
|---|---|
| **Form** | standalone server (mysqld); applications link the libmysqlclient client library (static or shared) or a connector |
| **Dependencies** | OpenSSL, plus bundled-or-system curl, protobuf, editline and other libraries selected with WITH_\* CMake options |
| **Minimum toolchain** | C++23 (CMAKE_CXX_STANDARD 23), CMake 3.17.5+, GCC 11+ or Clang 14+ on Linux, Visual Studio 2019 16.11+ on Windows, recent Xcode on macOS |
| **Platforms** | Linux, Windows (64-bit only for the server), macOS; build scripts also cover SUSE and Solaris |
| **Thread safety** | Multi-client server with concurrent sessions handled server-side; the client library's own thread rules were not reviewed here |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the cited comparison: pgtpc's MySQL point-select figure (1,050,000 QPS) comes from Oracle engineer Dimitri Kravtchuk's '1M IO-bound QPS with 8.0 GA on Intel Optane SSD' run. Per a search snippet of his February 2019 slides, that run was IO-bound on 50M x 8 tables with storage saturated. The PostgreSQL side holds the same 95 GB data set fully in memory (128 GB shared_buffers plus pg_prewarm on every table and index). So MySQL's 1.4x-1.7x point-select loss, and the mirrored 1.73x claim in the wave-6 PostgreSQL entry, compare an IO-bound run with a cached one.
- pgtpc is inconsistent about the only MySQL-favourable row: the Compare table gives MySQL oltp_read_write 900,000 QPS, while the PostgreSQL log page annotates the same test 'mysql: 39k/78W' (39k TPS, about 780,000 QPS). With 780,000 the 48-thread MySQL lead shrinks from 1.25x to about 1.08x, and PostgreSQL's 128-thread 910,554 would beat it. The CPU labels are also uneven: '48C' on the MySQL box is 48 cores with hyper-threading per the slides snippet, against '96C' vCPUs on c5d.metal.
- The 'extreme config' is unsafe by design: Percona's Vadim Tkachenko reran Dimitri's tests with innodb_checksum, innodb_doublewrite, sync_binlog=1 and performance schema on (search snippet only; percona.com, dimitrik.free.fr, lefred.be and bugs.mysql.com were unreachable here). MySQL bug #92360 reports only about 500k point-select QPS against the expected 1M (title only seen).
- Versioning changed: trunk is 26.10.0 'INNOVATION' (previous LTS 9.7.0), and open GitHub issues from 2026-10-11 report 26.7.1 missing from the repos and an upgrade path that aborts only after an irreversible data-dictionary upgrade (#837).

## Known shortcomings

- Tier C, not faster than PostgreSQL overall: the only win in Vonng/pgtpc (sysbench/ref-mysql.md) is oltp_read_write 1.25x at 48 threads on a different machine; the 910,554 run was at 128 threads, not 96, and the '48C point-select' figure is the page's c=64 row; the MySQL figures are vendor-published (Oracle blog); durability off on both sides; filed under embedded-kv, which is a poor fit; the PostgreSQL record uses the same page in reverse.
- Enricher: the pgtpc rows compare Dimitri Kravtchuk's separate IO-bound MySQL run (50M x 8, Optane, storage saturated; slide snippet only) with a fully cached PostgreSQL run (95 GB in 128 GB shared_buffers, pg_prewarm); pgtpc is inconsistent on read_write (table says MySQL 900,000 QPS, the PG log page says about 780,000), which shrinks the 1.25x lead to about 1.08x. No libmysqld in trunk, so MySQL is not embeddable; wrong category for embedded-kv.

## Caveats and trade-offs

Weak and mixed evidence, kept for completeness: the only MySQL-favourable row (oltp_read_write at 48 threads) compares Oracle's own published MySQL 8.0 numbers with a PostgreSQL run on a different machine, and the page's author (a PostgreSQL advocate) frames the table as PostgreSQL winning reads. MySQL loses oltp_point_select by about 1.7x and is level or behind on the other rows. Both sides are durability-off 'extreme' configs, not production settings. Oracle's original sources (mysql.com benchmarks page and a MySQL performance blog) were not reachable from this session, so the MySQL figures are quoted only as tabulated in pgtpc. Other head-to-heads found favour PostgreSQL: a HammerDB TPROC-C discussion (https://github.com/TPC-Council/HammerDB/discussions/259, laptop, 1 virtual user, about 3,800 NOPM for MySQL vs about 14,000 for PostgreSQL, versions unstated) and a DoltHub 2024 sysbench latency post seen only as a search summary. The mysql-server repo itself carries no performance claims or benchmark files. [retier] No libmysqld in trunk, so not embeddable; loose fit for embedded-kv.

Client-server RDBMS (InnoDB), not an embedded key-value engine; filed under embedded-kv only because storage-and-data has no relational category in wave 6. GPL-2.0 with additional linking permissions for separately licensed components such as OpenSSL (LICENSE file); Oracle also sells commercial editions. The quoted rates need the durability-off configuration.

## Maintenance

Actively developed by Oracle (trunk commit 2026-09-28, with 8.0, 8.4 and 9.7 fixes merged forward) under GPL-2.0 with linking exceptions; usable as a server, not as an embeddable library, and the performance evidence in this entry is weak and mixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now D.
- **Tier reason:** The MySQL column in pgtpc sysbench/ref-mysql.md is copied from Oracle's own MySQL performance blog posts (vendor numbers, different machine, CPU model not stated), while the PostgreSQL column comes from public sysbench commands and config in sysbench/aws.c5d.metal.extreme.md on an AWS c5d.metal with no CPU model; a cross-machine, vendor-sourced comparison is C at best.
- **Retiered** C to D: Same defect as the PostgreSQL entry: the pgtpc read_write row compares a separate IO-bound MySQL run from Dimitri Kravtchuk's slides (snippet only) with a fully cached PostgreSQL run, and pgtpc's own pages disagree on the MySQL figure (900,000 vs about 780,000 QPS), so there is no like-for-like measurement; directional only.
- **Verifier notes:** All tabulated numbers match ref-mysql.md and the PostgreSQL raw log; corrections fix the '96 threads' label (the 910,554 read_write run was at 128 threads), note that the 48C point-select figure is really the c=64 row, and point benchmark_url at the comparison page. Shortcomings to record: not faster than PostgreSQL (wins only oltp_read_write at 48 threads, by 1.25x, against a run on a different machine; loses point_select by 1.4-1.7x; parity or behind elsewhere), MySQL numbers are vendor-published (Oracle's MySQL performance blog at dimitrik.free.fr, unreachable here: ENOTFOUND) on different hardware with no CPU model, durability-off configs on both sides, wrong category (client-server RDBMS filed as embedded-kv), and the wave-6 postgres/postgres record uses the same pgtpc page in the opposite direction.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `license`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-88 (wave 6); enricher w6 pair-012
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Vonng/pgtpc/master/README.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/master/sysbench/README.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/master/sysbench/ref-mysql.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/master/sysbench/aws.c5d.metal.extreme.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/master/sysbench/aws.c5d.metal.normal.md>
  - <https://github.com/mysql/mysql-server>
  - <https://github.com/mysql/mysql-server/commits/trunk>
  - <https://raw.githubusercontent.com/mysql/mysql-server/trunk/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/mysql/mysql-server>
  - <https://github.com/mysql/mysql-server/commits/trunk>
  - <https://github.com/mysql/mysql-server/issues>
  - <https://raw.githubusercontent.com/mysql/mysql-server/trunk/README>
  - <https://raw.githubusercontent.com/mysql/mysql-server/trunk/LICENSE>
  - <https://raw.githubusercontent.com/mysql/mysql-server/trunk/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mysql/mysql-server/trunk/MYSQL_VERSION>
  - <https://raw.githubusercontent.com/mysql/mysql-server/trunk/cmake/os/Linux.cmake>
  - <https://raw.githubusercontent.com/mysql/mysql-server/trunk/cmake/os/Darwin.cmake>
  - <https://raw.githubusercontent.com/mysql/mysql-server/trunk/cmake/os/Windows.cmake>
  - <https://raw.githubusercontent.com/mysql/mysql-server/trunk/storage/innobase/log/log0write.cc>
  - <https://raw.githubusercontent.com/mysql/mysql-server/trunk/storage/innobase/btr/btr0sea.cc>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/master/README.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/master/sysbench/README.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/master/sysbench/ref-mysql.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/master/sysbench/aws.c5d.metal.extreme.md>
  - WebSearch: dimitrik "1M IO-bound QPS" MySQL 8.0 GA Intel Optane sysbench point select buffer pool (snippets of lefred.be/wp-content/uploads/2019/02/MySQL_Tuning-Feb2019-dim.pdf, percona.com/?p=19007, bugs.mysql.com/92360)
  - https://lefred.be/wp-content/uploads/2019/02/MySQL_Tuning-Feb2019-dim.pdf (ENOTFOUND)
  - https://bugs.mysql.com/bug.php?id=92360 (ENOTFOUND)
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/mysql/mysql-server`) · [data/wave6/enrich/raw/github_com_mysql_mysql_server.json](../../../data/wave6/enrich/raw/github_com_mysql_mysql_server.json) (enrichment confidence 0.6)

</details>
