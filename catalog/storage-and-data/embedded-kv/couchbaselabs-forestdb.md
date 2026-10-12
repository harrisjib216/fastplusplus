# ForestDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Couchbase's embedded key-value engine built on an HB+-trie; first-party 2014 tests show up to 8x faster reads than SQLite.

| | |
|---|---|
| **Beats** | SQLite |
| **Claimed result** | Reads up to 8x faster than SQLite; writes up to 2.3x faster than SQLite (at larger batch sizes); mixed workload up to 7x faster than SQLite. |
| **Workload** | Mobile-side test on a Google Nexus 5: 1M documents loaded, key length 8-32 bytes, value size 256 bytes; random read of 80K records, random update of 80K records (batch size 1-20), and a mixed read+update workload; ForestDB vs a single two-column SQLite table (WAL mode). |
| **Metric** | latency |
| **Hardware** | Google Nexus 5, Qualcomm Snapdragon 800 MSM8974 (quad-core, 2260MHz, Krait 400), 2GB RAM |
| **Compiler and flags** | SQLite 3.7.11 on Android KitKat 4.4.2 (native compiler/flags not stated) |
| **Adoption** | 1,333 stars. The README says production Couchbase Server builds use the 'cb-master' branch (Couchbase Server 6.5 onward), and 'master' is left unsupported for community users. ForestDB was also a Couchbase Lite storage option. |
| **Last commit** | 2019-05-10 |
| **Links** | [repository](https://github.com/couchbaselabs/forestdb) · [benchmark](https://github.com/couchbaselabs/forestdb/wiki/Performance-Results) |

## Verdict

In a first-party 2014 test, Couchbase used a Nexus 5 (Snapdragon 800, 2GB RAM, Android 4.4.2) and loaded 1M documents (8-32 byte keys, 256-byte values) into ForestDB and into a two-column SQLite 3.7.11 table in WAL mode. It then timed 80K random reads, 80K random updates at batch sizes 1-20, and a two-thread mixed read/update run: ForestDB was up to 8x faster on reads, up to 2.3x faster on writes at larger batches (slower at batch 1), and up to 7x faster on the mixed run. The figures are 'up to' values read off charts, no compiler or flags are given, and the analysis is commented out of the live wiki page.

## Use it when

- Embedded storage where reads must never block on a writer. MVCC allows one writer plus many readers per file, e.g. UI-thread reads while a sync thread writes, which is why Couchbase Lite 1.x offered it.
- Long or hash-like keys (8+ bytes, roughly uniform), where HB+-trie chunking keeps the index small and shallow compared with a B+-tree that stores whole keys.
- Writes that can be batched into multi-document commits. In Couchbase's SQLite comparison, ForestDB only pulled ahead on writes as the batch size grew.
- Apps that need a change feed: iterate the sequence index from a saved sequence number to drive replication, backup or external secondary indexes.
- Apps that need cheap point-in-time snapshots or rollback of the whole store to an earlier commit header.

## Skip it when

- Single-document synchronous commits: at batch size 1 ForestDB was slower than SQLite in Couchbase's own mobile test, because append-only storage causes more write amplification.
- You need SQL, secondary indexes, or serializable or repeatable-read isolation. Only read committed and read uncommitted exist.
- You want an active, general-purpose upstream. 'master' has been frozen and unsupported since 2019, and the last tag is v1.2 (2016). Fixes land only on Couchbase release branches, and Couchbase Lite dropped ForestDB in 2.0 (issue #19).
- Disk-constrained devices: the append-only file grows until compaction copies live data into a new file. The wiki says compaction of very large stores can take tens of minutes to hours. Circular stale-block reuse (block_reusing_threshold) is the only mitigation, and it has to be tuned.
- Opening untrusted database files: a fuzzed malformed file segfaults forestdb_dump in superblock parsing (issue #23, open since 2022, no fix referenced).

## How it is fast

The primary index is an HB+-trie. Keys are split into fixed-size chunks (8 bytes by default), and each trie level is a B+-tree keyed on one chunk. That keeps node comparisons short and nodes block-aligned, so long or random keys need fewer disk reads. 'Leaf B+-trees' that store whole key suffixes limit the skew caused by repetitive key patterns. Writes are appended to a log-structured file and found through in-memory hash-table WAL indexes. The main index is updated in batches when the WAL passes a threshold (4,096 docs by default) or at commit, which spreads write amplification across batched writes. ForestDB also runs its own buffer cache, which weights index nodes above data pages and can use O_DIRECT, instead of relying on the OS page cache.

## Compared with alternatives

Against the other SQLite challengers catalogued (SNKV, CalicoDB, DBX, CacheAdvance), pick ForestDB when you need MVCC snapshots, a sequence-number change feed and readers that never block, and can live with a dormant upstream and the oldest, least reproducible numbers of the group. Against LSM siblings such as HyperLevelDB or Badger, its case is lower write amplification (Couchbase measured 7-20x per synchronous update vs LevelDB's 166-387x), not raw throughput.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | pthread; Snappy for optional document-body compression (built in by default on non-Windows standalone builds unless SNAPPY_OPTION=Disable); optional libaio (Linux), jemalloc, and OpenSSL, CommonCrypto or LibTomCrypt for encryption |
| **Minimum toolchain** | C++11 compiler; CMake 3.1+ per INSTALL.md (the neo branch's CMakeLists requires 3.13); applications call the extern "C" API |
| **Platforms** | README lists CentOS, Ubuntu, macOS, Windows, iOS and Android. The 'master' branch fails to build on aarch64 Linux (x86-only signal-handler code, issue #24) and with VS 2019 (offsetof error, issue #22). The 'neo' branch has AArch64 fixes and disables that handler. |
| **Thread safety** | Operations are thread-safe only when each thread opens its own fdb_file_handle and fdb_kvs_handle; sharing a handle across threads is unsupported. Writers are serialized, and readers do not block on writers (MVCC). One writer per file is recommended. |
| **Drop-in for the baseline** | no |

## Gotchas

- The default GitHub branch 'master' contains changes Couchbase never shipped. Production code lives on 'cb-master' and 'neo', so check out one of those, or tag v1.2, rather than master.
- On MSVC, fdb_types.h does '#define bool int' for C callers, so fdb_config's layout differs from the C++-built library. Issue #17 reports broken fdb_get_default_config results unless the caller is also compiled as C++.
- Nothing is durable until fdb_commit, and the async durability modes can lose data on a crash. Deletes remain as tombstones until compaction purges them. Snapshot or rollback calls to sequence numbers that a concurrent compaction has already dropped return errors.
- The buffer cache is global: buffercache_size is ignored once the first fdb_open has initialized it. A file created in auto-compaction mode cannot be opened in manual mode, or the reverse, without calling fdb_switch_compaction_mode.

## Known shortcomings

- The 8x/2.3x/7x figures sit in a commented-out wiki page; master abandoned since 2019-05 (cb-master branch touched 2024-04, neo 2025-11).
- Weak evidence: 2014 first-party 'up to' values read off charts with no compiler/flags; the analysis is commented out of the live wiki page. Master is frozen since 2019 and unsupported (last tag v1.2, 2016); shipping code lives on cb-master/neo; Couchbase Lite dropped it in 2.0. C API over a C++11 implementation.
- Batch-1 synchronous writes are slower than SQLite; only read-committed/uncommitted isolation; append-only, so compaction is needed. Open bugs: malformed-file segfault (#23), master breaks aarch64 (#24) and VS2019 (#22), MSVC C callers hit a bool ABI mismatch (#17). Handles are not shareable across threads; one writer per file advised.

## Caveats and trade-offs

The analysis section is inside an HTML comment on the live wiki page. The rendered page shows only 'The new benchmark results and analysis will be available soon' (last edited 2016-01-29), so the numbers come from the page's raw Markdown source. The results date from 2014 and are first-party (Couchbase's own team). The figures are 'up to' values read from charts. Writes are slower than SQLite at batch size 1 because append-only storage causes more write amplification. The README says the default 'master' branch is unsupported and was last committed 2019-05-10. Production fixes went to 'cb-master' (last commit 2024-04-11) and the 'neo' release branch (last commit 2025-11-21).

The same page also compares ForestDB server-side against LevelDB v1.15 and RocksDB v3.1 on an Intel Xeon E5-2620 box: ForestDB showed much lower write amplification (7x-20x vs RocksDB's 31x-35x and LevelDB's 166x-387x), but those server-side throughput numbers are only shown as bar-chart images, not text, so they are not quoted as a numeric claim here.

## Maintenance

'master' has been frozen and unsupported since May 2019, but the Apache-2.0 'neo' branch still gets occasional Couchbase fixes (last commit 2025-11-21). Current Couchbase Server Community Edition docs still name ForestDB as the standard index storage engine, and a small community fork (ForestDB-KVStore/forestdb, last push April 2025) adds Conan packaging.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party 2014 Couchbase numbers against SQLite 3.7.11 (WAL mode) on a Nexus 5, with the hardware and configs stated. No compiler or flags are stated, and the results are read off charts plus 'up to' prose, so it is C. The IEEE TC 2016 ForestDB paper is peer-reviewed, but I could not open it to check for a SQLite comparison (paywalled; the computer.org preprint link returns HTML).
- **Verifier notes:** All three figures (reads up to 8x, writes up to 2.3x at larger batch sizes, mixed up to 7x vs SQLite) appear verbatim in the commented-out raw wiki Markdown, along with the hardware and SQLite config. The record's last_commit 2020-09-02 did not match any branch; the default-branch head is 2019-05-10, so 'abandoned' stands, though Couchbase still patches release branches (neo, 2025-11-21). License Apache-2.0 confirmed; not a fork, not archived.
- **Fields the verifier corrected:** `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/couchbaselabs/forestdb/wiki/Performance-Results>
  - <https://raw.githubusercontent.com/wiki/couchbaselabs/forestdb/Performance-Results.md>
  - <https://github.com/couchbaselabs/forestdb>
  - <https://raw.githubusercontent.com/couchbaselabs/forestdb/master/README.md>
  - <https://raw.githubusercontent.com/couchbaselabs/forestdb/neo/README.md>
  - <https://raw.githubusercontent.com/couchbaselabs/forestdb/neo/LICENSE>
  - <https://www.computer.org/csdl/trans/tc/preprint/07110563.pdf>
  - <https://api.crossref.org/works/10.1109/tc.2015.2435779>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/TC.2015.2435779>
- **Sources the enricher read:**
  - <https://github.com/couchbaselabs/forestdb>
  - <https://github.com/couchbaselabs/forestdb/blob/master/README.md>
  - <https://github.com/couchbaselabs/forestdb/blob/master/INSTALL.md>
  - <https://github.com/couchbaselabs/forestdb/blob/master/include/libforestdb/forestdb.h>
  - <https://github.com/couchbaselabs/forestdb/blob/neo/include/libforestdb/forestdb.h>
  - <https://github.com/couchbaselabs/forestdb/blob/neo/include/libforestdb/fdb_types.h>
  - <https://github.com/couchbaselabs/forestdb/blob/master/CMakeLists.txt>
  - <https://github.com/couchbaselabs/forestdb/blob/neo/CMakeLists.txt>
  - <https://github.com/couchbaselabs/forestdb/blob/neo/src/hbtrie.h>
  - <https://github.com/couchbaselabs/forestdb/blob/master/utils/debug.cc>
  - <https://github.com/couchbaselabs/forestdb/blob/neo/utils/debug.cc>
  - <https://github.com/couchbaselabs/forestdb/commits/neo>
  - <https://github.com/couchbaselabs/forestdb/tags>
  - <https://raw.githubusercontent.com/couchbaselabs/forestdb/neo/LICENSE>
  - <https://github.com/couchbaselabs/forestdb/wiki/_pages>
  - <https://raw.githubusercontent.com/wiki/couchbaselabs/forestdb/Performance-Results.md>
  - <https://raw.githubusercontent.com/wiki/couchbaselabs/forestdb/Home.md>
  - <https://raw.githubusercontent.com/wiki/couchbaselabs/forestdb/Overview.md>
  - <https://raw.githubusercontent.com/wiki/couchbaselabs/forestdb/Implementation-Details.md>
  - <https://raw.githubusercontent.com/wiki/couchbaselabs/forestdb/Public-APIs.md>
  - <https://raw.githubusercontent.com/wiki/couchbaselabs/forestdb/Future-Work.md>
  - <https://raw.githubusercontent.com/wiki/couchbaselabs/forestdb/Integration-into-Couchbase-Lite.md>
  - <https://raw.githubusercontent.com/wiki/couchbaselabs/forestdb/Bindings-to-Other-Languages.md>
  - <https://github.com/couchbaselabs/forestdb/issues>
  - <https://github.com/couchbaselabs/forestdb/issues/17>
  - <https://github.com/couchbaselabs/forestdb/issues/19>
  - <https://github.com/couchbaselabs/forestdb/issues/21>
  - <https://github.com/couchbaselabs/forestdb/issues/22>
  - <https://github.com/couchbaselabs/forestdb/issues/23>
  - <https://github.com/couchbaselabs/forestdb/issues/24>
  - <https://github.com/ForestDB-KVStore/forestdb>
  - <https://api.crossref.org/works/10.1109/tc.2015.2435779>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/TC.2015.2435779>
  - <https://hn.algolia.com/api/v1/search?query=forestdb>
  - <https://hn.algolia.com/api/v1/items/8409300>
  - <https://docs.couchbase.com/server/current/learn/services-and-indexes/indexes/indexing-and-query-perf.html>
  - <https://docs.couchbase.com/server/current/learn/services-and-indexes/indexes/storage-modes.html>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/couchbaselabs/forestdb`) · [data/wave6/enrich/raw/github_com_couchbaselabs_forestdb.json](../../../data/wave6/enrich/raw/github_com_couchbaselabs_forestdb.json) (enrichment confidence 0.75)

</details>
