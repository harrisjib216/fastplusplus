# Speedb

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> RocksDB fork, API-compatible through RocksDB 8.6.7, adding a hash-based memtable and gradual write throttling to beat stock RocksDB.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | Speedb's sorted hash memtable vs RocksDB v7.2.2 with its skiplist memtable: "Up to 155% improvement in overwrite workload", "Up to 68% improvement in 50% random read workload", "Up to 15% improvement in random seek workload". Per-point values are only in chart images. The README and dynamic-delayed-writes doc only show a chart (no numbers) of steady random-write throughput without stalls vs RocksDB's older delayed-write mechanism. |
| **Workload** | db_bench with 1 billion objects, 1KB values, 64MB write buffer, 4 threads, max 4 write buffers, 1 column family, 16 CPU cores, no compression: 100% overwrite, 50% random read, and 100% random seek, comparing Speedb with the sorted hash memtable (speedb.HashSpdRepFactory) against RocksDB v7.2.2 with its default skiplist memtable. |
| **Metric** | throughput |
| **Hardware** | Memtable test: 16 CPU cores, model not stated. Delayed-write test in the README: 16 cores of an Intel Xeon Platinum 8370C @ 2.80GHz (per the dynamic-delayed-writes doc). |
| **Adoption** | 1009 stars |
| **Last commit** | 2024-06-12 |
| **Links** | [repository](https://github.com/speedb-io/speedb) · [benchmark](https://github.com/speedb-io/documentation/blob/main/speedb-features/sorted-hash-memtable.md) |

## Verdict

Speedb's own docs benchmark Speedb with the sorted hash memtable against RocksDB v7.2.2 with its default skiplist, the same RocksDB base as Speedb 2.0/2.1, using db_bench (1B objects, 1KB values, 64MB write buffers, 4 threads, 16 cores, no compression). They report headline 'up to' gains of 155% on 100% overwrite, 68% on a 50% random-read mix and 15% on random seek; per-point values appear only in charts, and no CPU model, compiler or flags are given. The README's no-stall random-write chart (80M objects, 1KB values, 50 threads, 16-core Xeon Platinum 8370C) has no numbers at all.

## Use it when

- You run RocksDB 7.x to 8.6 and overwrite- or update-heavy workloads with roughly 1KB values are limited by the skiplist memtable; setting memtable_factory to speedb.HashSpdRepFactory is the change the vendor benchmarks (up to +155% overwrite, +68% on a 50% read mix).
- Sustained bulk random writes where RocksDB's delayed-write mechanism gives sawtooth throughput and stalls; Speedb's dynamic delay (default on) and a shared WriteController smooth the write rate across column families and across several DBs in one process.
- Many DB instances or column families in one process sharing one memory budget: SharedOptions gives them one cache, one WriteBufferManager with proactive flushes, and one write controller.
- Filters with high bits-per-key (about 20 and up) where filter memory matters: the paired Bloom filter claims about 30% less memory at the same false-positive rate.
- You want to A/B a RocksDB-compatible engine with almost no code change; the docs say you can switch back to RocksDB at any time.

## Skip it when

- You need RocksDB features, fixes or on-disk options added after 8.6.7 (September 2023). Speedb has not rebased since then and has had no commits since March 2024, when Redis acquired the company.
- Memory-constrained deployments using the hash memtable. In one Speedb test log (issue #749), malloc stats showed 6040 MB with hash spdb vs 3292 MB with the skiplist. Issue #540 says memtable memory is underestimated, and more so with HashSpdRepFactory. A memory-reduction ticket (#618) is still open.
- Workloads dominated by seeks or scans: the claimed gain is only up to 15%, and a seek over freshly written data has to wait for the background thread to sort the pending write list.
- Code that relies on Iterator::Refresh() or memtable insert hints: the hash memtable reports IsRefreshIterSupported()=false, and InsertKeyWithHint ignores the hint.
- Latency-sensitive point reads through the paired Bloom filter: Speedb's own doc says building and probing it is about 2x slower than RocksDB's default filter, so it saves memory, not time.

## How it is fast

The sorted hash memtable replaces RocksDB's skiplist with a fixed array of hash buckets (MurmurHash of the user key). Each bucket is a short sorted linked list with its own reader-writer lock, so point writes and Gets are bucket probes instead of O(log n) skiplist walks. Each insert also goes onto an atomic, unsorted write list that a background thread cuts into sorted vectors (up to 10K keys each, or whenever a seek arrives). Iterators merge those vectors with a binary heap, so writes keep flowing while a seek waits only for its own cut to be sorted, and a pre-built standby memtable hides the cost of allocating the buckets. Separately, dynamic delayed writes (use_dynamic_delay, on by default) cut the write rate in linear steps according to how far L0 file count, pending compaction bytes or memtable count are past the slowdown trigger. RocksDB instead moves the rate by fixed +25%/-20% steps, and the README's no-stall chart credits this change.

## Compared with alternatives

Pick Speedb over ToplingDB or PsiTri's RocksDB-API layer when you want the smallest behavioral change from stock RocksDB 8.x (same LSM engine, speedups that are opt-in memtable and filter swaps) and can live with an unmaintained fork. Pick Titan for large values, where its gains come from key-value separation, and ToplingDB if you want a RocksDB fork with larger published speedups and benchmark runs as recent as September 2026.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake/make targets speedb and speedb-shared) |
| **Dependencies** | None required for the core library. Optional: snappy, lz4, zlib, zstd, bzip2 and jemalloc. The CMake option WITH_LIBURING defaults to ON. gflags is needed for db_bench and the tools. |
| **Minimum toolchain** | C++17; GCC 7+ or Clang 5+ per INSTALL.md; Visual Studio 2017+ on Windows |
| **Platforms** | Linux, macOS, Windows and iOS per INSTALL.md, with CMake code paths for x86-64, aarch64 (armv8 CRC), ppc64 and s390x. The default build targets the build machine's CPU; use PORTABLE=1 for a portable binary. |
| **Thread safety** | Same threading model as the RocksDB code it forks. The hash memtable declares concurrent-insert support, using a reader-writer lock per bucket plus one background sort thread per memtable (SpdbVectorContainer::SortThread). |
| **Drop-in for the baseline** | partial — same include/rocksdb headers and API, and the docs call it fully compatible and reversible. But you link speedb instead of rocksdb, the API stops at RocksDB 8.6.7, the speedups need opt-in options (or EnableSpeedbFeatures), and several defaults differ from RocksDB. |

## Gotchas

- Some defaults differ from RocksDB: level_compaction_dynamic_level_bytes=false (Speedb's changelog says the flag 'is not working properly with Speedb', issue #786), compaction_readahead_size=0, 8 compaction threads, and use_dynamic_delay=true. A tuned RocksDB config can therefore behave differently.
- The docs describe hash-memtable writes as needing no synchronization, but the code takes a per-bucket write lock on every insert. ApproximateMemoryUsage() returns 0, and the bucket vector is allocated outside the arena, so memtable size accounting undercounts.
- Bucket count is a fixed cost paid per memtable: the docs cite 1,000,000 buckets (about 8 MB, and creation is slow), while main lowered the default to 400,000 (#854) after the last release. Speedb pre-creates a standby memtable to hide the creation time.
- The Speedb write flow (use_spdb_writes) is still marked experimental and uses more memory. How to go back to RocksDB after enabling Speedb-only memtable or filter options is not documented.

## Known shortcomings

- The README chart has no numbers; the Speedb docs repo gives sorted-hash memtable gains (up to 155% overwrite, 68% at 50% reads, 15% seek vs RocksDB 7.2.2 skiplist), and that memtable is opt-in. docs.speedb.io is dead; last commit 2024-03, around Redis's acquisition of Speedb.
- Stale: last release 2.8.0 is based on RocksDB 8.6.7. Speed evidence is vendor 'up to' numbers vs RocksDB 7.2.2 with no CPU/compiler/flags. The hash memtable is memory-heavy (6040 MB vs 3292 MB skiplist in #749; memory undercounted, #540 and #618 open); docs say lock-free but inserts take a per-bucket lock; iterator Refresh unsupported.
- Defaults differ from RocksDB (dynamic level bytes off #786, compaction readahead 0, 8 compaction threads), and migrating back to RocksDB after using Speedb-only options is undocumented. The paired Bloom filter saves memory only and its own docs say it is \~2x slower.

## Caveats and trade-offs

First-party vendor docs, and the figures are 'up to' headlines; per-point results exist only as chart images. The sorted hash memtable is opt-in (--memtablerep=speedb.HashSpdRepFactory), not the default. The baseline is old: RocksDB v7.2.2. No compiler, flags or CPU model are given for the memtable test. The README's delayed-write chart has no numbers. docs.speedb.io no longer resolves; the docs survive in the speedb-io/documentation GitHub repo. Commits stopped in March 2024, the same month as an HN-listed TechCrunch story (2024-03-21) that says Redis acquired Speedb.

100% RocksDB API-compatible drop-in; Speedb Ltd (the company) reportedly wound down in 2024, matching the last-commit date.

## Maintenance

Stale: last commit March 2024 and last release 2.8.0 (January 2024, on RocksDB 8.6.7) after Redis acquired Speedb, docs.speedb.io is gone, and 146 issues are still open. It is Apache-2.0 and buildable, but you would have to do every future RocksDB rebase yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgraded from D. The README chart has no numbers, but Speedb's own docs page for the sorted hash memtable gives numeric headline gains over RocksDB v7.2.2 (default skiplist memtable) with a db_bench configuration. It is first-party, gives only a core count and no CPU model, compiler or flags, and states the numbers as 'up to' figures, so it is C.
- **Verifier notes:** benchmark_url now points to the docs page that has actual numbers vs RocksDB; the README anchor is chart-only. Metadata matches gh: Apache-2.0, 1009 stars, last commit 2024-03-11 (stale), not archived and not a fork. The paired-bloom-filter doc makes a memory claim (about 30% less memory at equal FPR) but says construction and use are about 2x slower, so it is not a speed win.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/speedb-io/speedb>
  - <https://github.com/speedb-io/speedb#-example-benchmark>
  - <https://github.com/speedb-io/documentation>
  - <https://raw.githubusercontent.com/speedb-io/documentation/main/enhancements/dynamic-delayed-writes.md>
  - <https://raw.githubusercontent.com/speedb-io/documentation/main/speedb-features/sorted-hash-memtable.md>
  - <https://github.com/speedb-io/documentation/blob/main/speedb-features/sorted-hash-memtable.md>
  - <https://raw.githubusercontent.com/speedb-io/documentation/main/performance-testing.md>
  - <https://raw.githubusercontent.com/speedb-io/documentation/main/speedb-features/paired-bloom-filter.md>
  - <https://docs.speedb.io/enhancements/dynamic-delayed-writes>
  - <https://hn.algolia.com/api/v1/search?query=Redis%20Speedb&tags=story>
- **Sources the enricher read:**
  - <https://github.com/speedb-io/speedb>
  - <https://github.com/speedb-io/speedb/blob/main/README.md>
  - <https://github.com/speedb-io/speedb/blob/main/HISTORY.md>
  - <https://github.com/speedb-io/speedb/blob/main/INSTALL.md>
  - <https://github.com/speedb-io/speedb/blob/main/CMakeLists.txt>
  - <https://github.com/speedb-io/speedb/blob/main/memtable/hash_spdb_rep.cc>
  - <https://github.com/speedb-io/speedb/blob/main/memtable/spdb_sorted_vector.h>
  - <https://github.com/speedb-io/speedb/blob/main/include/rocksdb/options.h>
  - <https://github.com/speedb-io/speedb/blob/main/include/rocksdb/advanced_options.h>
  - <https://github.com/speedb-io/speedb/blob/main/port/port_posix.h>
  - <https://github.com/speedb-io/speedb/releases>
  - <https://github.com/speedb-io/speedb/commits/main>
  - <https://github.com/speedb-io/speedb/branches>
  - <https://github.com/speedb-io/speedb/issues/749>
  - <https://github.com/speedb-io/speedb/issues/540>
  - <https://github.com/speedb-io/speedb/issues/618>
  - <https://github.com/speedb-io/speedb/issues/807>
  - <https://github.com/speedb-io/speedb/issues/854>
  - <https://github.com/speedb-io/speedb/issues/858>
  - <https://github.com/speedb-io/speedb/issues?q=hashspdb>
  - <https://github.com/speedb-io/documentation>
  - <https://github.com/speedb-io/documentation/blob/main/speedb-features/sorted-hash-memtable.md>
  - <https://github.com/speedb-io/documentation/blob/main/enhancements/dynamic-delayed-writes.md>
  - <https://github.com/speedb-io/documentation/blob/main/getting-started/drop-in-replacement.md>
  - <https://github.com/speedb-io/documentation/blob/main/speedb-features/write-flow.md>
  - <https://github.com/speedb-io/documentation/blob/main/performance-testing.md>
  - <https://github.com/speedb-io/documentation/blob/main/speedb-features/speedb-tuning-function.md>
  - <https://github.com/speedb-io/documentation/blob/main/speedb-features/paired-bloom-filter.md>
  - <https://hn.algolia.com/api/v1/search?query=Speedb&tags=story&hitsPerPage=20>
  - <https://hn.algolia.com/api/v1/items/39781651>
  - <https://hn.algolia.com/api/v1/items/33531408>
  - <https://techcrunch.com/2024/03/21/redis-switches-licenses-acquires-speedb-to-go-beyond-its-core-in-memory-database/>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/speedb-io/speedb`) · [data/wave6/enrich/raw/github_com_speedb_io_speedb.json](../../../data/wave6/enrich/raw/github_com_speedb_io_speedb.json) (enrichment confidence 0.72)

</details>
