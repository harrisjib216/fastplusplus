# ToplingDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `GPL-2.0 OR Apache-2.0` · 🟢 active

> RocksDB 8.10 fork with a trie memtable and searchable compressed SSTs; about 5x RocksDB's in-cache random-read throughput.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | Run of 2026-09-15 (run_id 34935695406), fillrandom suite, readrandom stage. ToplingDB zipkeyvalue reached 1,735,572 ops/sec vs 348,705 for RocksDB v8.10 (4.98x, stated on the page, which calls this 'the fairest comparison') and vs 378,878 for RocksDB master (4.58x, on page). ToplingDB zipkeyonly, which stores values uncompressed while RocksDB uses Snappy/Zstd, reached 4,720,755 ops/sec: 13.54x vs v8.10 and 12.46x vs master (on page). Other stages: fillrandom 1,660,002 vs 664,354 ops/sec (2.50x, on page) and readseq 16,936,378 vs 10,771,647 (1.57x, on page). ToplingDB is slower on compaction: zipkeyvalue runs at 0.62x of v8.10 in the fillrandom suite and 0.30x in the fillseq suite. The page is a live dashboard, so the numbers change with each CI run. |
| **Workload** | db_bench fillrandom, fillseq and fillseq (CSPP) suites (fill, flush, compact, readseq x3, readrandom): 50,000,000 records, 8-byte keys, 50-byte values, batch_size 1000. The DB lives on /dev/shm (tmpfs) and the on-disk DB (\~1.9 GiB for fillrandom) fits inside the 7.8 GiB RocksDB block cache. ToplingDB uses ToplingZipTable (zipkeyonly/zipkeyvalue), the CSPP memtable and -enable_zero_copy. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7763 64-Core Processor (4 logical CPUs; GitHub Actions ubuntu-latest runner, Azure kernel 6.17), Ubuntu 24.04.5 LTS, 15.6 GiB RAM, DB on /dev/shm |
| **Compiler and flags** | Not stated on the page. The public CI workflow builds ToplingDB with `make ... DEBUG_LEVEL=0` and upstream RocksDB with DEBUG_LEVEL=0 PORTABLE=haswell (to match ToplingDB's -march=haswell). The compiler is the ubuntu-latest default (gcc) unless the workflow's use_clang input is set, and the version is unstated. |
| **Adoption** | 1016 stars |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/topling/toplingdb) · [benchmark](https://topling.github.io/toplingdb/) |

## Verdict

The project's own GitHub Actions dashboard (run 34935695406, 2026-09-15) ran db_bench with 50M 8-byte keys and 50-byte values, one client thread, and the DB on /dev/shm fitting inside a 7.8 GiB block cache. Hardware was an AMD EPYC 7763 with 4 vCPU and 15.6 GiB RAM on Ubuntu 24.04, with release builds at -march=haswell and the compiler unstated. ToplingDB zipkeyvalue did 1.74M readrandom ops/s against 349K for RocksDB 8.10.2 (4.98x) and 379K for RocksDB master (4.58x), with 2.50x fillrandom, 1.57x readseq and 0.62x compaction speed. The sides are tuned differently: ToplingDB uses a tuned YAML (512 MB write buffer, CSPP memtable as WAL index, zero-copy reads), while RocksDB uses db_bench defaults plus an OPTIONS file that mainly sets the L0-none/Snappy/L6-Zstd compression ladder.

## Use it when

- An existing RocksDB app on Linux x86-64 with bytewise-ordered keys where point lookups are CPU-bound and the data fits in RAM or page cache. The project's dashboard shows 3.7-5.0x single-thread readrandom (zipkeyvalue vs RocksDB v8.10/master across three suites) with 8-byte keys and 50-byte values.
- Scan-heavy work on small values: readseq is 1.6-1.9x RocksDB v8.10, and scans that skip loading values (ToplingDB's lazy value load) reach 3.6-4.8x.
- RAM- or disk-constrained nodes: in the fillrandom suite, zipkeyvalue used 0.56x RocksDB's disk and 18% of its RSS during readrandom. Page cache is counted separately.
- Teams that want YAML/JSON-defined DB configuration, online option changes and Prometheus metrics built in, and can either license the Enterprise components or run the open-source distributed-compaction workers (topling-dcompact) to absorb compression CPU.

## Skip it when

- You need a fully open-source build. The components that deliver the speedup, the ToplingZipTable builder (private topling-rocks) and the CSPP MemTable (private), ship only as precompiled 90-day trial objects. No published benchmark covers a build with both turned off.
- Windows or macOS: the maintainer says ToplingDB currently supports only Linux (issues #66, #67). The released JNI jar contains only librocksdbjni-linux64.so.
- Custom comparators: the CSPP MemTable supports only BytewiseComparator and ReverseBytewiseComparator, and the performance components are built around bytewise order.
- Compaction- or write-bound workloads on few cores: compaction runs at 0.62x (fillrandom) and 0.30x (fillseq) of RocksDB v8.10, and ZipTable compression costs about 2x zstd CPU. In the project's dcompact run with the write side capped at 50% CPU, fillseq was 0.64x RocksDB v8.10 and fillrandom only about 1.0x.
- Larger-than-memory datasets or apps that need recent upstream RocksDB features: every published run fits in cache, the code base tracks RocksDB 8.10.2, and dynamic column-family creation, user timestamps and wide columns are compiled out by default.

## How it is fast

ToplingZipTable SSTs pair a CO-Index (NestLoudsTrie, a nested LOUDS succinct trie mapping key to id) with PA-Zip (DictZipBlobStore, global-dictionary compression that can read one value directly). Both are searched while still compressed in mmap'd memory, so there is no block decompression or block cache, and uncompressed values go back to the caller zero-copy. The CSPP MemTable, a Crash-Safe Parallel Patricia trie, replaces the skiplist and uses integer offsets instead of pointers. So with memtable_as_log_index it can point into the WAL and be turned straight into an SST without a flush. Comparator calls are devirtualized and key-prefix caches were added in hot paths such as MergingIterator and FindFileInRange, which only works because these components are limited to bytewise key order.

## Compared with alternatives

Pick ToplingDB over Titan when values are tiny and reads dominate: Titan's catalogued gains grow with value size, while ToplingDB's come from 50-byte-value lookups and scans. Pick it over research engines such as PebblesDB, KVell or SplinterDB when you want to keep RocksDB's API and feature set. Prefer those siblings or F2 for write-heavy or larger-than-memory work, where ToplingDB's compaction is slower and its gains are unmeasured.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib built from source with make (install-dev-shared installs headers and the .so); also a JNI jar, and Rust bindings in a separate repo |
| **Dependencies** | libaio, gflags, zlib, bzip2, libcurl, liburing, snappy, jemalloc, lz4, zstd; the Makefile auto-clones rockside (Apache-2.0), topling-zip (BSD-3, with bundled boost headers and zstd), cspp-wbwi, topling-sst and topling-zip_table_reader, and downloads trial objects for the private components |
| **Minimum toolchain** | C++17; gcc 8.3+ recommended, clang also works (C++20 with coroutines if USE_COROUTINES=1) |
| **Platforms** | Linux only. x86-64 builds use -march=haswell when the CPU has BMI2; the Makefile has aarch64 flags and the wiki quotes ARM CSPP numbers, but whether trial objects exist for each architecture is not documented |
| **Thread safety** | Same model as RocksDB: one process opens a DB, and a DB\* can be shared across threads without external locking, while Iterator and WriteBatch objects need external synchronization. CSPP is designed for parallel writers. The published benchmarks use one client thread. |
| **Drop-in for the baseline** | partial — same rocksdb:: API and on-disk lineage, but you must open through SidePluginRepo plus a YAML/JSON file (or use the env-var 'Easy Migrate' path). Some RocksDB features are compiled out by default, the fast components require bytewise comparators, and memtable_as_log_index writes a WAL format that RocksDB cannot read. |

## Gotchas

- A default release make (DEBUG_LEVEL=0) tries an SSH clone of the private topling-rocks repo. If that fails, it silently wgets precompiled top_zip_table_builder.o and cspp_memtable.o from an Aliyun OSS bucket as 90-day trials. For a clean open build pass WITH_TOPLING_ROCKS=0 WITH_CSPP_MEMTABLE=0 together; CSPP cannot be on without topling-rocks. What the trial builder does after 90 days is not documented, though the ZipTable reader is open source.
- Dynamic ColumnFamily creation (ROCKSDB_DYNAMIC_CREATE_CF), user-level key timestamps and wide columns are disabled at compile time by default. RocksDB code that calls CreateColumnFamily at runtime needs a rebuild with -DROCKSDB_DYNAMIC_CREATE_CF.
- memtable_as_log_index is an immutable DB option with its own WAL format. All WALs must be flushed before you toggle it. A large WriteBatch can overflow the WAL mmap and fail with 'IO fenced off ... exceeds mmap size' unless max_total_wal_size is large enough.
- CSPP reserves mem_cap of virtual address space per memtable (default 2G, max 16G). The wiki warns that on Linux, touching that memory when the system has no free RAM segfaults instead of returning an error, unless explicit commit (MADV_POPULATE_WRITE, kernel 5.14+) is used.

## Known shortcomings

- The fair figure is zipkeyvalue 4.98x; the 13.5x zipkeyonly result stores values uncompressed. The ZipTable builder and CSPP memtable that produce the speedups are private and shipped as 90-day trial binaries; compiler not stated.
- The default make silently downloads the private ZipTable/CSPP trial object files; behaviour after the 90-day expiry is undocumented. Linux only (#66, #67); only bytewise/reverse comparators; dynamic column families, user timestamps and wide columns are compiled out by default; its WAL format differs from RocksDB's.
- Compaction is slower (0.30-0.62x; with distributed compaction fillseq 0.64x, fillrandom \~1.0x). Unequal tuning: ToplingDB uses a tuned YAML (512 MB write buffer, memtable as WAL index) while RocksDB runs db_bench defaults, and the data fits in cache. License is RocksDB's GPLv2/Apache-2.0 dual license.

## Caveats and trade-offs

The benchmark is run and published by the ToplingDB project itself, and the results page does not name the compiler. The dataset sits entirely in cache on tmpfs, which the page itself calls a CPU/memory comparison, so the result may not carry over to larger-than-cache workloads. The 13.5x headline uses zipkeyonly, which leaves values uncompressed against a compressed RocksDB and uses 1.24-1.97x more disk; the fair zipkeyvalue figure is \~5x. Compaction is slower than RocksDB. Most importantly, the components benchmarked, the ToplingZipTable builder (private topling-rocks repo) and the CSPP MemTable (private), are closed source; the build downloads them as precompiled 90-day trial objects. Only the RocksDB-derived core and some plugins are open (GPL-2.0/Apache-2.0 inherited from RocksDB).

GPL-2.0 is more restrictive than RocksDB's BSD/Apache-2.0 dual license, which can block adoption in permissively-licensed downstream projects. Several advertised features (distributed compaction, some CSPP tooling) are gated behind a separate paid 'Enterprise' build not in this open repo.

## Maintenance

Actively maintained by Topling Inc (pushes through 2026-09-20, CI benchmark runs through 2026-09-15, 1016 stars). Usability is mixed: it is Linux-only, and the components behind the headline numbers are proprietary trial binaries. The open parts keep RocksDB's GPLv2/Apache-2.0 dual license, so the license is no stricter than upstream's.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** A first-party live CI dashboard against RocksDB v8.10.2 and RocksDB master. The code is public (.github/workflows/db_bench-build.yml, db_bench-run.yml, .github/scripts/build_upstream_rocksdb.sh, .github/bench-conf) and the page states the CPU model (AMD EPYC 7763, 4 vCPU). The workflow shows release builds (DEBUG_LEVEL=0, PORTABLE=haswell), but neither the page nor the run states which compiler or version was used; a use_clang input switches between gcc and clang. So not A.
- **Verifier notes:** The numbers match the 2026-09-15 run. The record's 'RocksDB master 378,000' should read 378,878, and the 13.5x ratio is printed on the page, not just derived. ToplingDB is a RocksDB fork (the README says 'forked from RocksDB', and db_bench reports version 8.10.2), even though GitHub's fork flag is false. The key performance components are proprietary trial binaries, hence usability 'mixed'.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `license`, `usability`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://topling.github.io/toplingdb/>
  - <https://topling.github.io/toplingdb/runs/20260915-071823-plain-34935695406/raw/zipkeyonly/db_bench-all.log>
  - <https://topling.github.io/toplingdb/runs/20260915-071823-plain-34935695406/raw/rocksdb-v8.10/db_bench-all.log>
  - <https://topling.github.io/toplingdb/runs/20260915-071823-plain-34935695406/raw/zipkeyvalue/db_bench-fillrandom.yaml>
  - <https://github.com/topling/toplingdb>
  - <https://github.com/topling/toplingdb/blob/memtable_as_log_index/README.md>
  - <https://github.com/topling/toplingdb/blob/memtable_as_log_index/.github/workflows/db_bench-build.yml>
  - <https://github.com/topling/toplingdb/blob/memtable_as_log_index/.github/workflows/db_bench-run.yml>
  - <https://github.com/topling/toplingdb/blob/memtable_as_log_index/.github/scripts/build_upstream_rocksdb.sh>
  - <https://github.com/topling/toplingdb/actions/runs/34935695406>
- **Sources the enricher read:**
  - <https://github.com/topling/toplingdb>
  - <https://github.com/topling/toplingdb/blob/memtable_as_log_index/README.md>
  - <https://github.com/topling/toplingdb/blob/memtable_as_log_index/README-zh_cn.md>
  - <https://github.com/topling/toplingdb/blob/memtable_as_log_index/Makefile>
  - <https://github.com/topling/toplingdb/blob/memtable_as_log_index/.github/workflows/db_bench-run.yml>
  - <https://github.com/topling/toplingdb/blob/memtable_as_log_index/.github/bench-conf/rocksdb_db_bench.ini>
  - <https://github.com/topling/toplingdb/issues>
  - <https://github.com/topling/toplingdb/issues/66>
  - <https://github.com/topling/toplingdb/issues/67>
  - <https://github.com/topling/toplingdb/issues/68>
  - <https://topling.github.io/toplingdb/>
  - <https://topling.github.io/toplingdb/runs/20260915-071823-plain-34935695406/raw/zipkeyvalue/db_bench-fillrandom.yaml>
  - <https://topling.github.io/toplingdb/runs/20260915-071823-plain-34935695406/raw/zipkeyvalue/db_bench-all.log>
  - <https://topling.github.io/toplingdb/runs/20260915-071823-plain-34935695406/raw/rocksdb-v8.10/db_bench-all.log>
  - <https://topling.github.io/toplingdb/dcompact/>
  - <https://github.com/topling/sideplugin-wiki-en/wiki/101>
  - <https://github.com/topling/sideplugin-wiki-en/wiki/ToplingZipTable>
  - <https://github.com/topling/sideplugin-wiki-en/wiki/CSPP-MemTable>
  - <https://github.com/topling/sideplugin-wiki-en/wiki/Devirtualization-And-Key-Prefix-Cache-Principle>
  - <https://github.com/topling/topling-zip_table_reader>
  - <https://github.com/topling/topling-zip_table_reader/blob/HEAD/src/table/top_zip_table.cc>
  - <https://github.com/topling/topling-zip_table_reader/blob/HEAD/src/table/top_zip_table_reader.cc>
  - <https://github.com/topling/topling-zip>
  - <https://github.com/topling/topling-dcompact>
  - <https://github.com/topling/rockside>
  - <https://github.com/topling/cspp-memtable>
  - <https://github.com/topling/topling-rocks>
  - <https://github.com/facebook/rocksdb/wiki/Basic-Operations>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/topling/toplingdb`) · [data/wave6/enrich/raw/github_com_topling_toplingdb.json](../../../data/wave6/enrich/raw/github_com_topling_toplingdb.json) (enrichment confidence 0.72)

</details>
