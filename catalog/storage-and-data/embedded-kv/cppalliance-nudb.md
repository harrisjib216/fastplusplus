# NuDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟡 stale

> Header-only, insert-only on-disk hash table for SSDs; its own benchmark shows higher insert and large-DB fetch throughput than default-config RocksDB.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | Sample table in repo: insert throughput 406598 vs 231937 ops/sec at 100K keys, 374330 vs 258519 at 1M keys (NuDB faster); fetch throughput 333443/337300 vs 34557/20835 ops/sec at 1M/10M keys (NuDB faster) but 325228 vs 697158 at 100K keys (NuDB slower) (numbers as printed on page) |
| **Workload** | Insert N pseudo-random key/value pairs then fetch M random keys, at database sizes of 100,000 / 1,000,000 / 10,000,000 keys, per the project's own bench.cpp harness. |
| **Metric** | throughput |
| **Adoption** | 415 stars |
| **Last commit** | 2025-04-24 |
| **Links** | [repository](https://github.com/cppalliance/NuDB) · [benchmark](https://github.com/cppalliance/NuDB/blob/master/bench/README.md) |

## Verdict

By default the project's bench.cpp inserts 64-byte random keys with random values of 250-750 bytes in single-threaded batches of 20,000, then fetches random existing keys; RocksDB is opened with default Options, with only create_if_missing set. The README 'sample output' has NuDB at about 1.45-1.75x RocksDB's insert ops/s at 100K and 1M keys, about 10-16x RocksDB's fetch ops/s at 1M and 10M keys, and about 0.47x at 100K keys. With default settings each cell is a single 20,000-op batch. No CPU, SSD, compiler, flags or RocksDB version is given, and NuDB's commit (a close/reopen between phases) falls outside the timed insert loop.

## Use it when

- Write-once, read-many data with fixed-size keys, especially content-addressable storage keyed by a 32- or 64-byte hash (rippled/XRPL node store is the reference deployment, reported at over 3 TB and later over 10 TB).
- Random point lookups over data sets much larger than RAM on SSD/NVMe, where you want roughly constant per-lookup I/O and memory use that does not grow with DB size.
- Sustained single-writer ingestion where losing up to about one second of unflushed inserts on a crash is acceptable, but on-disk consistency after the crash is required (the log file rolls back partial commits).
- Projects that want a header-only dependency and already build with Boost.

## Skip it when

- Any workload that needs update, overwrite, delete, TTL or compaction: records are immutable, duplicate inserts fail with key_exists, and removing data means rewriting the whole DB offline (issue #98).
- Range scans, prefix queries, ordered iteration or variable-length keys; the only iteration is a sequential walk of the data file in insertion order.
- Spinning disks: the author says it 'will be extremely slow' on HDDs (issue #67).
- Multi-process access or several store instances on the same files: the author says this is undefined behavior (issue #72).
- Small data sets that fit in cache: in the project's own sample run RocksDB fetched about 2.1x faster at 100K keys.

## How it is fast

The key file is a bucketed linear-hashing table (Litwin/Larson): each bucket is one device block (default 4096 bytes) of entries sorted by a 48-bit prefix of a salted xxHash64, so a fetch is usually one pread of the bucket plus one pread of the value, with no LSM levels or compaction to make reads costlier as the DB grows. Full buckets spill into records appended to the data file, which form a linked list. Inserts go into an in-memory pool, and a background context thread commits them about once per second with bulk sequential appends and a rollback log; the README says locks are never held during disk reads or writes.

## Compared with alternatives

Pick NuDB over SplinterDB, TerarkDB or Titan only when data is truly append-only with fixed-size hash keys and you want a small header-only engine with O(1) point lookups. For updates, deletes, range queries or a RocksDB-compatible API, those siblings (or RocksDB itself) are the better fit.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Boost 1.69+ (Boost.System and Boost.Thread must be linked; uses boost::optional, boost::shared_mutex); bench needs RocksDB, zlib and snappy; tests need Boost.Beast |
| **Minimum toolchain** | README says C++11; the CMake build sets cxx_std_14. CI covered GCC 5-8 and Clang 6-8 on Ubuntu 16.04 plus VS2019; newer compilers not documented. |
| **Platforms** | 64-bit Linux and other POSIX (pread/pwrite, posix_fadvise skipped on macOS) and Windows (win32_file); 32-bit correctness is an open issue (#2). SSD or other high-IOPS storage required. |
| **Thread safety** | insert and fetch are safe to call concurrently with each other; open and close are not. Inserts are serialized by a mutex, fetches run concurrently. One process and one store instance per set of files. |
| **Drop-in for the baseline** | false — different API and data model: fixed key size chosen at create time, insert-only, no delete/update/iterators/column families/snapshots, and no on-disk format compatibility with RocksDB. |

## Gotchas

- Inserts are buffered in memory and committed about once per second by a background thread, so they are not durable when insert returns; call close (or context::flush in manual mode) to commit. The destructor calls close but discards its error. After one failed commit, every later insert and fetch returns that error until the DB is closed.
- Key size, block size, load factor, salt and Hasher are fixed at create time; opening with a different Hasher fails the pepper check. Values must be 1 byte to 4 GB (a zero-length value trips an assert, issue #101). Tune block size to the device and AllocSize to the average value size.
- The fetch callback can run while an internal shared lock is held (when the key is still in the uncommitted insert pool), so a slow callback can stall the commit thread (issue #53).
- insert is not write-only: its duplicate check reads the key-file bucket (plus the data file on a hash match). Writers get 25 ms sleeps when the insert rate beats the measured flush rate and more than the 4 MB burst (set_burst) is buffered; issue #83 traced rippled latency spikes to the earlier throttle logic.

## Known shortcomings

- Bench numbers are 'sample output' with no CPU, SSD, compiler, flags or RocksDB version; each cell is one 20K-op batch; RocksDB runs with default Options and NuDB's commit isn't timed in the insert loop. Loses fetch at 100K keys (\~0.47x RocksDB). Insert-only (no update, delete or range scan), fixed-size keys, not durable until the \~1 s background commit, no multi-process access (#72), very slow on HDD (#67). Stale since 2021 apart from small fixes; CI only on GCC 5-8/Clang 6-8/Boost 1.69; no 32-bit (#2). Fetch callbacks can run under an internal lock and stall commits (#53).

## Caveats and trade-offs

The bench README labels the table 'a sample output', so it is unclear whether it is a captured real run. No CPU model or compiler/flags are given for it; the build instructions use a CMake Release build. The prose cites 340397 ops/sec for fetch at 10M keys, but the table shows 337300. Insert at 10M keys is NA. NuDB is slower than RocksDB on fetch at 100K keys.

Append-only, insert-only design (no update/delete), all keys must be the same size; optimized specifically for random-read performance on SSDs, e.g. content-addressable storage.

## Maintenance

Stale: only a missing-includes fix (July 2024) and a 2.0.9 version bump (April 2025) since 2021, and the author calls it mature with 'nothing more to do' (issue #96). It is BSL-1.0 and header-only, so easy to vendor, but CI only targeted old toolchains (GCC 5-8, Clang 6-8, Boost 1.69).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The project's own harness (bench/bench.cpp, with bench/rocksdb_support) prints a NuDB vs RocksDB insert/fetch table. The README shows it only as 'a sample output', with no CPU, compiler, or flags for that run, so it is first-party with partial methodology: C.
- **Verifier notes:** All table numbers match the page and belong to the nudb and rocksdb columns. last_commit was the pushed_at date (2025-04-30); the newest commit on master is 2025-04-24, which is still stale. License BSL-1.0, 415 stars, not archived and not a fork, all confirmed.
- **Fields the verifier corrected:** `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cppalliance/NuDB/blob/master/bench/README.md>
  - <https://github.com/cppalliance/NuDB>
- **Sources the enricher read:**
  - <https://github.com/cppalliance/NuDB>
  - <https://github.com/cppalliance/NuDB/blob/master/README.md>
  - <https://github.com/cppalliance/NuDB/blob/master/bench/README.md>
  - <https://github.com/cppalliance/NuDB/blob/master/bench/bench.cpp>
  - <https://github.com/cppalliance/NuDB/blob/master/CHANGELOG.md>
  - <https://github.com/cppalliance/NuDB/blob/master/CMakeLists.txt>
  - <https://github.com/cppalliance/NuDB/blob/master/.drone.star>
  - <https://github.com/cppalliance/NuDB/blob/master/include/nudb/basic_store.hpp>
  - <https://github.com/cppalliance/NuDB/blob/master/include/nudb/impl/basic_store.ipp>
  - <https://github.com/cppalliance/NuDB/blob/master/include/nudb/context.hpp>
  - <https://github.com/cppalliance/NuDB/blob/master/include/nudb/xxhasher.hpp>
  - <https://github.com/cppalliance/NuDB/blob/master/include/nudb/impl/posix_file.ipp>
  - <https://github.com/cppalliance/NuDB/blob/master/include/nudb/native_file.hpp>
  - <https://github.com/cppalliance/NuDB/blob/master/include/nudb/version.hpp>
  - <https://github.com/cppalliance/NuDB/blob/master/include/nudb/_experimental/test/test_store.hpp>
  - <https://github.com/cppalliance/NuDB/issues/2>
  - <https://github.com/cppalliance/NuDB/issues/53>
  - <https://github.com/cppalliance/NuDB/issues/64>
  - <https://github.com/cppalliance/NuDB/issues/67>
  - <https://github.com/cppalliance/NuDB/issues/72>
  - <https://github.com/cppalliance/NuDB/issues/83>
  - <https://github.com/cppalliance/NuDB/issues/96>
  - <https://github.com/cppalliance/NuDB/issues/97>
  - <https://github.com/cppalliance/NuDB/issues/98>
  - <https://github.com/cppalliance/NuDB/issues/99>
  - <https://github.com/cppalliance/NuDB/issues/101>
  - <https://github.com/cppalliance/NuDB/blob/master/include/nudb/impl/context.ipp>
  - <https://github.com/cppalliance/NuDB/blob/master/include/nudb/detail/bucket.hpp>
  - <https://github.com/cppalliance/NuDB/blob/master/include/nudb/detail/format.hpp>
  - <https://github.com/cppalliance/NuDB/issues?q=is%3Aissue>
  - <https://github.com/cppalliance/NuDB/commits/master>
  - <http://vinniefalco.github.io/nudb/>
  - <https://hn.algolia.com/api/v1/search?query=NuDB&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cppalliance/nudb`) · [data/wave6/enrich/raw/github_com_cppalliance_nudb.json](../../../data/wave6/enrich/raw/github_com_cppalliance_nudb.json) (enrichment confidence 0.75)

</details>
