# Starskey

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MPL-2.0` · 🟡 stale

> Small pure-Go LevelDB/WiscKey-style LSM key-value store; its own bench beats fsync-per-op RocksDB but loses to LMDB.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | Page timings for 10,000 ops with 32-byte keys/values: Starskey write 53.3 ms, get 4.81 ms, delete 28.9 ms vs RocksDB 286.9 ms, 10.1 ms, 283.1 ms, i.e. about 5.4x write, 2.1x get and 9.8x delete (derived from page data). LMDB beats Starskey on every operation (3.74 ms / 2.00 ms / 3.40 ms), and BBolt beats it on get (4.56 ms) and delete (5.46 ms). The RocksDB gap is inflated by a mismatched harness (see caveats). |
| **Workload** | 10,000 ops with 32-byte keys/values: write, get, delete benchmark against Pebble, BBolt, Badger, LMDB and RocksDB, single-threaded, via the starskey-io/bench tool. |
| **Metric** | throughput |
| **Hardware** | Unspecified — author describes it only as a "crappy 4 year old system"; no CPU model given |
| **Adoption** | 161 stars |
| **Last commit** | 2025-03-19 |
| **Links** | [repository](https://github.com/starskey-io/starskey) · [benchmark](https://github.com/starskey-io/bench#starsky-benchmarker) |

## Verdict

The starskey-io/bench README reports one single-threaded run of 10,000 random 33-38-byte keys and values on an unnamed 'crappy 4 year old system': Starskey took 53.3 ms to write, 4.8 ms to get and 28.9 ms to delete, against RocksDB's 286.9, 10.1 and 283.1 ms (about 5.4x, 2.1x and 9.8x). The Go engines were timed by wall clock and RocksDB/LMDB by C clock() in a harness built without an -O level. The comparison is not like-for-like: RocksDB, Pebble and Badger fsync every op, while Starskey (v0.1.8, 64 MB flush threshold) fsyncs every 256 ms in the background and never flushes during the 10K ops, so all three Starskey timings measure WAL appends plus an in-memory T-tree. LMDB beats Starskey on all three operations and BBolt beats it on get and delete; the README's '400k+ ops per second' has no supporting benchmark.

## Use it when

- Studying or forking a compact LSM: about 2.8k lines in one file plus small pager, T-tree, Bloom and trie-filter packages, MPL-2.0 and easy to vendor.
- Small Go datasets that mostly stay in the memtable, with small records (key plus value under roughly 100 bytes so each serialized record fits one 128-byte page), where losing up to \~256 ms of acknowledged writes on a crash is acceptable.
- Single-process, write-mostly tools that want built-in helpers like PrefixSearch, LongestPrefixSearch or DeleteByPrefix without writing iterator code.

## Skip it when

- Workloads that overwrite or delete keys and expect the latest value back. From the code, Get scans each level's SSTables oldest-first and returns the first hit, and mergeTables keeps duplicate keys instead of dropping superseded versions, so once two versions are on disk the older one can win. No test overwrites a key across flushes.
- Records over 128 bytes. The pager splits any record larger than the 128-byte page into up to 128 chunks, each written as its own 144-byte page with a separate stat, seek and write, so a \~1 KB value takes \~116 pages (\~16 KB on disk). Past 16 KiB a chunk no longer fits its page and copy() truncates it, which corrupts the value. This comes from reading pager.go; I did not run it.
- Read-heavy data larger than the memtable. A Get that misses the memtable deserializes every klog record of each candidate SSTable, and Bloom filters are off in the README's example config.
- Concurrent services. One global sync.Mutex (not an RWMutex) serializes every read, write and scan, and flush plus recursive compaction run inline in the caller's Put.
- Strict durability or real ACID. Fsync happens only in the background; a flush truncates the WAL without first fsyncing the new SSTable; and a transaction writes one WAL record per op with no commit marker, so a crash mid-commit can replay a partial transaction.

## How it is fast

A write appends a BSON-encoded record to a paged WAL and inserts into an in-memory T-tree memtable. By default the WAL is fsynced only by a background ticker every 256 ms, and that accounts for most of the benchmark gap to RocksDB, Pebble and Badger, which fsync every op. Once the memtable passes FlushThreshold it is written out as a sorted run with keys and values in separate klog/vlog files (WiscKey-style key-value separation), and leveled partial compaction merges half of a full level into the next, running synchronously inside the Put that crossed the threshold. Optional per-SSTable Bloom filters (xxh3) or a trie filter the project calls SuRF (map-per-node trie nodes, not the paper's succinct encoding) let reads skip SSTables. There is no block index, so a lookup that reaches an SSTable scans its key log linearly.

## Compared with alternatives

Badger is the mature Go implementation of the same WiscKey key-value-separation idea, and Pogreb is the Go option for read-heavy point lookups. Pick Starskey over them only when you want a small, readable LSM to study or fork, not for data you can't afford to lose or read back stale.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/klauspost/compress (S2/Snappy), go.mongodb.org/mongo-driver (BSON record encoding), github.com/zeebo/xxh3, github.com/cespare/xxhash/v2; no cgo |
| **Minimum toolchain** | Go 1.24 (go.mod); CI workflow uses Go 1.23 |
| **Platforms** | Pure Go, so in principle any Go target; CI tests only ubuntu-latest and no platform support is documented |
| **Thread safety** | Safe to share across goroutines through a single global sync.Mutex that serializes all operations (read locks were tried and reverted in PR #37); each Txn has its own mutex. |
| **Drop-in for the baseline** | no |

## Gotchas

- Delete is Put(key, 0xDEADBEEF), so storing that exact 4-byte value makes a key read as deleted. Range also returns the raw tombstone bytes for keys deleted but not yet flushed, because memtable range results are not tombstone-filtered.
- Transactions are weaker than the README's 'fully serializable' claim. Txn.Put's rollback writes a tombstone instead of restoring the old value. Txn.Delete on a memtable-resident key re-puts its current value instead of a tombstone. Txn.Get reads outside the DB lock, so Update read-modify-write can lose updates. A failed Commit calls Rollback while still holding the non-reentrant DB mutex, which deadlocks.
- Most OptionalConfig knobs are ignored: the memtable always uses the package-level TTreeMin/TTreeMax, every pager uses the package-level PageSize, and Bloom filters use the package-level BloomFilterProbability. Passing any OptionalConfig leaves BackgroundFSync at its zero value (false), which turns off fsync entirely (only transaction commits still fsync) rather than making writes synchronous.
- An unset Permission defaults to decimal 750 (octal 01356), not 0750. Logging: true calls log.SetOutput on Go's global logger, sending the whole process's log output into the DB's .log file. Without it, the engine writes every open, flush and compaction line to the standard logger.

## Known shortcomings

- Unfair harness: Starskey fsyncs in the background every 256 ms while RocksDB fsyncs each operation, and RocksDB is timed with CPU clock() vs Go wall clock. LMDB wins every operation and BBolt wins get and delete.
- From code reading (not run): Get scans each level's SSTables oldest-first and merges keep duplicate keys (likely stale reads); records over 128 B split into up to 128 pages and values over 16 KiB are truncated; no SSTable index (disk Get scans the key log linearly); one global mutex with inline compaction in Put. Transactions: a failed Commit deadlocks, Txn.Delete of a memtable key re-puts it, rollback of Put deletes rather than restores. Passing any OptionalConfig turns fsync off; the 10K-op bench never flushes (measures WAL append plus in-memory tree only).

## Caveats and trade-offs

The harness is not like-for-like. Starskey's Put/Delete only append to the WAL and fsync in the background every 256 ms (default BackgroundFSync), while the bench syncs RocksDB (sync=1 and use_fsync=1), Pebble (pebble.Sync) and Badger (SyncWrites) on every op, despite the code comment claiming Starskey 'syncs to disk automatically'. BBolt and LMDB batch all ops in one transaction. RocksDB/LMDB are timed with C clock() (process CPU time), whereas the Go engines use wall-clock time.Since. Hardware is unstated beyond a 'crappy 4 year old system'; there are no Go build flags and the C harness has no -O level. On the page's own numbers LMDB beats Starskey on every operation and BBolt beats it on get and delete, so 'faster than incumbents' holds only against per-op-fsync RocksDB. The bench pins starskey v0.1.8 (latest tag v0.1.9).

LevelDB-WiscKey inspired LSM design; small single-run benchmark, no repeated trials or variance reported.

## Maintenance

Single-maintainer project with no commits since 2025-03-19 (latest tag v0.1.9) and no open issues. It is MPL-2.0 and small enough to vendor, but the correctness problems above make it a study codebase rather than a production store, despite the author calling it production-ready in issue #48.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** The starskey-io/bench README lists first-party timings for Starskey, Pebble, BBolt, Badger, LMDB and RocksDB from public code (main.go for the Go engines, c/main.c for RocksDB/LMDB built with 'gcc ... -Wall', no -O level), but there is no CPU model ('crappy 4 year old system') and no Go flags, and the harness is not like-for-like, so C.
- **Verifier notes:** Every number matches the bench README, but the win over RocksDB compares background-fsync Starskey with per-op-fsync RocksDB timed by CPU clock, so I downgraded the claim (tier stays C). Metadata checks out (MPL-2.0, 161 stars, last commit 2025-03-19 = stale, not archived, not a fork).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/starskey-io/starskey>
  - <https://github.com/starskey-io/bench#starsky-benchmarker>
  - <https://github.com/starskey-io/bench/blob/master/main.go>
  - <https://github.com/starskey-io/bench/blob/master/c/main.c>
  - <https://github.com/starskey-io/starskey/blob/master/starskey.go>
  - <https://github.com/starskey-io/starskey/blob/master/pager/pager.go>
- **Sources the enricher read:**
  - <https://github.com/starskey-io/starskey>
  - <https://github.com/starskey-io/starskey/blob/master/README.md>
  - <https://github.com/starskey-io/starskey/blob/master/starskey.go>
  - <https://github.com/starskey-io/starskey/blob/master/starskey_test.go>
  - <https://github.com/starskey-io/starskey/blob/master/pager/pager.go>
  - <https://github.com/starskey-io/starskey/blob/master/pager/pager_test.go>
  - <https://github.com/starskey-io/starskey/blob/master/ttree/ttree.go>
  - <https://github.com/starskey-io/starskey/blob/master/surf/surf.go>
  - <https://github.com/starskey-io/starskey/blob/master/bloomfilter/bloomfilter.go>
  - <https://github.com/starskey-io/starskey/blob/master/go.mod>
  - <https://github.com/starskey-io/starskey/blob/master/.github/workflows/starskey_ci.yml>
  - <https://github.com/starskey-io/starskey/issues?q=is%3Aissue>
  - <https://github.com/starskey-io/starskey/issues/26>
  - <https://github.com/starskey-io/starskey/issues/27>
  - <https://github.com/starskey-io/starskey/issues/30>
  - <https://github.com/starskey-io/starskey/issues/31>
  - <https://github.com/starskey-io/starskey/issues/32>
  - <https://github.com/starskey-io/starskey/issues/48>
  - <https://github.com/starskey-io/starskey/pull/36>
  - <https://github.com/starskey-io/starskey/pull/37>
  - <https://github.com/starskey-io/starskey/tags>
  - <https://github.com/starskey-io/starskey/commits/master>
  - <https://github.com/starskey-io/bench#starsky-benchmarker>
  - <https://github.com/starskey-io/bench/blob/master/main.go>
  - <https://github.com/starskey-io/bench/blob/master/go.mod>
  - <https://hn.algolia.com/api/v1/search?query=starskey&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/starskey-io/starskey`) · [data/wave6/enrich/raw/github_com_starskey_io_starskey.json](../../../data/wave6/enrich/raw/github_com_starskey_io_starskey.json) (enrichment confidence 0.7)

</details>
