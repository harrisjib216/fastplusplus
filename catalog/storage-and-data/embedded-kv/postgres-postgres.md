# PostgreSQL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `PostgreSQL` · 🟢 active

> Client-server SQL RDBMS; one advocate's durability-off sysbench run beats MySQL 8.0's published point-select peak, not read-write.

| | |
|---|---|
| **Beats** | MySQL 8.0 (InnoDB, sysbench; MySQL figures are Oracle's published 'extreme config' sysbench numbers as tabulated in the pgtpc repo) |
| **Claimed result** | pgtpc Compare table point-select 1,814,404 vs 1,050,000 QPS (1.73x, derived) is not like for like: PostgreSQL fully in memory (95 GB prewarmed into 128 GB shared_buffers) vs an IO-bound MySQL Optane run from different slides; scripts do not reproduce as published. |
| **Workload** | sysbench oltp_point_select on 8 tables x 50M rows and oltp_read_only, oltp_read_write and oltp_update_non_index on 8 tables x 10M rows, 300 s runs at 1 to 512 threads over a Unix socket, PostgreSQL 14.5 (version stated on the NORMAL-config page) with a 'NOT FOR PRODUCTION' config (fsync off, synchronous_commit off, full_page_writes off, wal_level minimal, autovacuum off, shared_buffers 128GB, tables rebuilt at fillfactor 75 and pg_prewarm'ed) on an AWS c5d.metal, versus MySQL 8.0 peak numbers copied from dimitrik.free.fr blog posts (48 cores with HT, checksum, doublewrite, binlog, PFS and fsync off, latin1). |
| **Metric** | throughput |
| **Hardware** | PostgreSQL side: AWS c5d.metal, 96 vCPU at 3.6 GHz (per the Compare table), 192 GB, 4x 900 GB ephemeral NVMe, CPU model not stated. MySQL side (Oracle's published run): 48 cores at 2.7 GHz, 172 GB, 2x Intel Optane P4800X. |
| **Compiler and flags** | PostgreSQL 14.5; build compiler and flags not stated. initdb with LATIN1 and C locale, postgresql.conf and sysbench commands are listed in sysbench/aws.c5d.metal.extreme.md of the benchmark repo. |
| **Adoption** | 22.4k stars (GitHub mirror of the official git repository) |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/postgres/postgres) · [benchmark](https://github.com/Vonng/pgtpc) |

## Verdict

Vonng's pgtpc ran sysbench against PostgreSQL 14.5 with a 'NOT FOR PRODUCTION' durability-off config on one AWS c5d.metal (96 vCPU, 192 GB, local NVMe; compiler and CPU model not stated) and compared the peaks with MySQL 8.0 numbers copied from blog runs by Oracle's MySQL performance team (dimitrik.free.fr) on a 48-core 2.7 GHz Optane machine: point select 1,814,404 vs 1,050,000 QPS, read_only 941,694 vs 920,000, update_non_index 269,233 vs 240,000, read_write 722,907 vs 900,000 (MySQL ahead). No same-machine run exists, and the point-select comparison sets an in-memory PostgreSQL run against an IO-bound MySQL one.

## Use it when

- You need a general-purpose relational server and want read-heavy OLTP throughput: the pgtpc run reached about 1.37M point-select QPS with a standard production config and 2.33M with durability off on one c5d.metal.
- Primary-key lookups over a working set that fits in shared_buffers (the pgtpc runs size shared_buffers at 128 GB of 192 GB RAM and prewarm the tables).
- Many concurrent clients on a large multi-core host, where point-select throughput keeps rising up to about 104 client threads on 96 vCPUs before flattening.
- You want SQL features (joins, constraints, extensions) and a permissive licence (PostgreSQL licence, BSD-style) rather than a key-value API.

## Skip it when

- You need an embedded in-process key-value store: PostgreSQL needs a running server, a client protocol round trip per query and server tuning; the catalogue's real embedded baselines (SQLite, LMDB, RocksDB) were never measured against it.
- Write-heavy OLTP is the deciding factor: in the same pgtpc table MySQL 8.0's published oltp_read_write figure (900,000 QPS) beats PostgreSQL's 722,907 at 48 threads, and PostgreSQL only reaches parity (910,554) at 128 threads.
- Production deployments that copy the benchmark config: fsync off can cause unrecoverable corruption after a crash or power loss (PostgreSQL's own docs), and autovacuum off leads to bloat and eventually transaction-ID wraparound shutdown.
- Workloads with thousands of short-lived connections and no pooler: each connection is a separate backend process (the benchmark caps max_connections at 256).

## How it is fast

The quoted numbers come from tuning rather than a single algorithm: a 128 GB shared buffer pool holding the whole 95 GB point-select data set after pg_prewarm, heap tables rebuilt at fillfactor 75 so updates can stay on the same page (HOT updates), sysbench clients on the same host over a Unix socket, and WAL durability switched off (fsync, synchronous_commit and full_page_writes off, wal_level minimal, autovacuum off). Point selects are B-tree primary-key probes answered entirely from shared memory, which is why reads scale to about 2.33M QPS at 104 client threads on a 96-vCPU box.

## Compared with alternatives

Pick PostgreSQL over the catalogued MySQL entry for read-heavy primary-key OLTP that fits in memory and for its licence and SQL feature set; stay with MySQL if a read-write mix at moderate concurrency is the bottleneck, and pick an embedded sibling such as LMDB, mpedb or Reindexer when you need in-process storage without a server.

## Integration

| | |
|---|---|
| **Form** | server application built from source (autoconf/make or Meson &gt;= 0.57.2) or installed from distribution packages; clients link the libpq shared library or use a language driver |
| **Dependencies** | build: C11 compiler, flex, bison 2.3+, Perl 5.14+; readline (or libedit) and zlib by default; ICU, OpenSSL, LZ4 and zstd optional |
| **Minimum toolchain** | C11 compiler (current master, version 20devel); the benchmarked 14.5 release needed only C99 |
| **Platforms** | x86, ARM, PowerPC, S/390, SPARC, MIPS, RISC-V; Linux, Windows, macOS, FreeBSD, OpenBSD, NetBSD, DragonFlyBSD, AIX, Solaris, illumos |
| **Thread safety** | multi-process server with one backend process per connection and shared memory between them; client-side thread safety depends on the driver (not documented in the pages read) |
| **Drop-in for the baseline** | no |

## Gotchas

- Point-select headline is not like for like: PostgreSQL's 50M x 8 tables (95 GB) were prewarmed into 128 GB shared_buffers, so the run is fully in memory, while MySQL's 1,050,000 QPS figure is from the '1M IO-bound QPS' Optane run by Dimitri of Oracle's MySQL performance team (dimitrik.free.fr) (storage saturated, per a WebSearch snippet of his slides; the blog is blocked here). The 1.73x win compares an in-memory run against an IO-bound one.
- The published scripts do not reproduce as written: initdb creates /data/pg/data with LATIN1 and C locale, but the config is copied into and the server started from /data/pgtpcb; huge_pages is set to 'on' and later to 'try', and PostgreSQL uses only the last entry; the only prepare command shown builds 50M-row tables while the read_only, read_write and update runs pass --table_size=10000000, so those runs probably touched the first 10M rows of 50M-row tables.
- Column labels are loose: 'PGSQL.48C' point select is the 64-thread result (48 threads gives 1,503,656 QPS, 1.43x), the 96C figures are 104- and 128-thread peaks, the MySQL table is headed 'TPS' though it lists QPS, and MySQL read_write is given as 780,000 ('39k/78W') on one page and 900,000 on another.
- Both sides run with durability off (MySQL without checksum, doublewrite, binlog, PFS and fsync; PostgreSQL with fsync, synchronous_commit and full_page_writes off) on different machines (48 cores at 2.7 GHz with Optane versus 96 vCPU at 3.6 GHz with NVMe), so neither number describes a production server.

## Known shortcomings

- Tier C: in Vonng/pgtpc the MySQL column is copied from the Oracle-team dimitrik.free.fr blog on different hardware, durability is off on both sides, MySQL is faster at read_write (48 threads) and ties at 128, the raw data puts point-select 1,814,404 at 64 threads (48 threads gives 1,503,656, 1.43x) and the page gives MySQL read_write as both 780,000 and 900,000. Client-server RDBMS filed under embedded-kv (MySQL is not a listed baseline); pgtpc is unlicensed and stale since 2022-08-22.
- Enricher: the pgtpc point-select headline (1,814,404 vs 1,050,000, 1.73x) is not like for like: PostgreSQL ran with 95 GB prewarmed into 128 GB shared_buffers (fully in memory) while the MySQL figure is Dimitri Kravtchuk's separate IO-bound 1M QPS Optane run; the pgtpc scripts do not reproduce as published (initdb on /data/pg/data but the server starts from /data/pgtpcb; huge_pages set twice; prepare builds 50M-row tables but the runs use --table_size=10000000; the MySQL table is headed TPS but holds QPS); both sides durability-off and MySQL wins read_write. A client-server RDBMS is a loose fit for embedded-kv.

## Caveats and trade-offs

The head-to-head is not same-machine: the PostgreSQL rows were run by the pgtpc author (Vonng) on c5d.metal (PostgreSQL 14.5, listed as 96C 3.6 GHz), while the MySQL 8.0 rows are copied from two dimitrik.free.fr blog posts by Oracle's MySQL performance team (linked from sysbench/ref-mysql.md; the blog and mysql.com are blocked from this session) on a 48-core 2.7 GHz box with 2x Optane P4800X, so clock speed, storage and run conditions differ. Both sides use durability-off 'extreme' settings (pgtpc says MySQL's run turns off checksum, doublewrite, binlog, PFS and fsync and uses latin1; PostgreSQL has fsync, synchronous_commit, full_page_writes and autovacuum off) and are not production configurations. Column labels are loose: 'PGSQL.48C' (comment 'FORCE c=48') holds a point-select figure that the page's own raw data puts at 64 client threads (48 threads gives 1,503,656, 1.43x), and the 96C figures are peaks at 104 and 128 threads. MySQL wins oltp_read_write at 48 threads and only ties at 128, read_only is parity, and the extreme page quotes MySQL read_write as 780,000 in one place and 900,000 in another, so the win is limited to point selects and a small update margin. No compiler, flags or CPU model, so not tier A; the benchmark repo has 42 stars, 20 commits, no LICENSE file and its last commit is 2022-08-22; its author maintains a PostgreSQL distribution and calls MySQL's published benchmark 'shameless'. Category mismatch: PostgreSQL is a client-server RDBMS, not an embedded key-value store, and MySQL is not one of the category's baselines (RocksDB, LevelDB, LMDB, SQLite); no PostgreSQL vs SQLite number was found. Corroboration, same direction: a HammerDB TPROC-C discussion on a laptop (https://github.com/TPC-Council/HammerDB/discussions/259; i7-1165G7, 16 GB, Docker 'latest' images limited to 12 GB, 100 warehouses, 1 virtual user) reports about 14,000 NOPM for PostgreSQL vs about 3,800 for MySQL, with the HammerDB maintainer replying that PostgreSQL performs better on this single-threaded test but that the gap is closer on servers; database versions are not stated. A small Takeruso/rdbms-performance-comparison repo (sysbench 10 threads, 60 s, Docker on WSL) shows near parity in transactions (about 20,963 PostgreSQL vs 20,845 MySQL) with PostgreSQL at 4.77 ms vs 28.78 ms average latency (not re-opened by the verifier). A DoltHub 2024 blog post (Postgres 15.5 vs MySQL 8.0.35) was seen only as a WebSearch summary. [retier] Both sides durability-off; MySQL wins oltp_read_write; MySQL column headed TPS but holds QPS; loose fit for embedded-kv.

Client-server RDBMS with process-per-connection backends, MVCC with vacuum, WAL and a full SQL planner; not an embedded key-value engine (filed under embedded-kv only because storage-and-data has no relational category in wave 6, SQLite being the nearest baseline). Needs a running server and tuning (shared_buffers, WAL settings) to reach the quoted rates.

## Maintenance

Very actively maintained (commits on 2026-10-10, master at 20devel; the GitHub repo is a read-only mirror that takes no pull requests) and copyable under the BSD-style PostgreSQL licence, but the evidence is a single advocate's unlicensed 42-star benchmark repo last updated 2022-08-22, and the category (embedded-kv) does not fit a client-server RDBMS.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now D.
- **Tier reason:** pgtpc (sysbench/ref-mysql.md, sysbench/aws.c5d.metal.extreme.md) lists the PostgreSQL configs and sysbench commands but no compiler, flags or CPU model, and the MySQL 8.0 column is copied from dimitrik.free.fr blog posts run by Oracle's MySQL performance team on a different 48-core 2.7 GHz Optane machine, so it is an unreproducible cross-machine comparison by a single PostgreSQL advocate (42-star repo, no licence): tier C.
- **Retiered** C to D: The headline compares two unrelated runs (an in-memory PostgreSQL run against a separate IO-bound MySQL run from Dimitri Kravtchuk's slides, known from a snippet only) and the pgtpc scripts do not reproduce as published, so no like-for-like measurement exists; directional only.
- **Verifier notes:** Numbers match the pgtpc pages, but the '48 threads' label is wrong for point select (raw data puts 1,814,404 at 64 threads; 48 threads gives 1.43x) and the 96-thread figures are really 104/128-thread peaks; the MySQL column is copied from Oracle-team blog runs on different hardware, and the page contradicts itself on MySQL read_write (780,000 vs 900,000). Shortcomings to record: cross-machine copied baseline, durability-off configs, MySQL faster or tied on read_write, wrong category (client-server RDBMS in embedded-kv; MySQL not a category baseline), benchmark repo unlicensed and stale; consider a category override or keep-and-document.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-89 (wave 6); enricher w6 pair-016
- **Pages the verifier opened:**
  - <https://github.com/Vonng/pgtpc>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/HEAD/README.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/HEAD/sysbench/README.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/HEAD/sysbench/aws.c5d.metal.extreme.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/HEAD/sysbench/ref-mysql.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/HEAD/sysbench/aws.c5d.metal.normal.md>
  - <https://github.com/Vonng/pgtpc/commits/master>
  - <https://github.com/postgres/postgres>
  - <https://github.com/postgres/postgres/commits/master>
  - <https://github.com/TPC-Council/HammerDB/discussions/259>
- **Sources the enricher read:**
  - <https://github.com/postgres/postgres>
  - <https://github.com/postgres/postgres/commits/master>
  - <https://raw.githubusercontent.com/postgres/postgres/HEAD/README.md>
  - <https://raw.githubusercontent.com/postgres/postgres/HEAD/COPYRIGHT>
  - <https://raw.githubusercontent.com/postgres/postgres/HEAD/meson.build>
  - <https://raw.githubusercontent.com/postgres/postgres/HEAD/doc/src/sgml/installation.sgml>
  - <https://raw.githubusercontent.com/postgres/postgres/HEAD/doc/src/sgml/maintenance.sgml>
  - <https://raw.githubusercontent.com/postgres/postgres/HEAD/doc/src/sgml/config.sgml>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/HEAD/README.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/HEAD/sysbench/README.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/HEAD/sysbench/aws.c5d.metal.extreme.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/HEAD/sysbench/aws.c5d.metal.normal.md>
  - <https://raw.githubusercontent.com/Vonng/pgtpc/HEAD/sysbench/ref-mysql.md>
  - WebSearch: dimitrik 1M IO-bound QPS MySQL 8.0 GA Intel Optane (snippets of https://lefred.be/wp-content/uploads/2019/02/MySQL_Tuning-Feb2019-dim.pdf, https://www.mysql.com/why-mysql/benchmarks/mysql/ and https://www.percona.com/blog/2018/07/13/on-mysql-and-intel-optane-performance/; dimitrik.free.fr, lefred.be and postgresql.org were unreachable)
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/postgres/postgres`) · [data/wave6/enrich/raw/github_com_postgres_postgres.json](../../../data/wave6/enrich/raw/github_com_postgres_postgres.json) (enrichment confidence 0.6)

</details>
