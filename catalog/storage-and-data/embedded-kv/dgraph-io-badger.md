# Badger (BadgerDB)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Pure-Go embedded LSM key-value store using WiscKey key-value separation; 3.7x lower random-read latency than RocksDB in Dgraph's 2017 test.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | Random reads: Badger is 3.67x faster (32361 ns/op vs 118982 ns/op for RocksDB). Population of 75M x 1KB records: 17m10s (Badger) vs 78m8s (RocksDB), about 4.6x faster (derived from page data). |
| **Workload** | populate + random-read benchmark: 250M keys with 128-byte values for the read test, and 75M keys with 1KB values for the population/write-time test; Badger's WiscKey-style value log vs RocksDB SSTables. |
| **Metric** | latency |
| **Hardware** | Amazon EC2 i3.large dedicated instance: 2 cores, 16GB RAM, 450GB local NVMe SSD (fio measured \~93K random-read IOPS at 4K block size); CPU model not stated |
| **Compiler and flags** | Go toolchain version not stated anywhere in badger-bench's BENCH-rocks.txt, README or the 2017 blog post (the record's 'Go 1.8' is unsupported). RocksDB v5.1.4 was built with `export USE_RTTI=1 && make shared_lib` (badger-bench README) and called from Go through cgo bindings (badger-bench rdb/). |
| **Adoption** | 15.8k stars; used by IPFS, Usenet Express, Decred, Insolar, IoTex, 194+ dependent Go packages |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/dgraph-io/badger) · [benchmark](https://github.com/dgraph-io/badger-bench/blob/master/BENCH-rocks.txt) |

## Verdict

Dgraph ran this benchmark itself in 2017 on a 2-core AWS i3.large (16 GB RAM, local NVMe, \~93K 4 KB random-read IOPS). Random Gets over 250M 22-byte keys with 128 B values averaged 32.4 us in Badger vs 119.0 us in RocksDB 5.1.4 called through cgo (3.67x), and loading 75M x 1 KB took 17m10s vs 78m08s (\~4.6x). RocksDB was opened read-only with its default block cache and a 16-bit bloom filter while Badger held its LSM tables in RAM (LoadToRAM), and neither the Go version nor the CPU model is stated.

## Use it when

- Go services that need an embedded, ordered, persistent KV store without cgo. You get plain `go get`, easy cross-compilation, and full visibility in the Go CPU and memory profilers. Cgo pain is why Dgraph replaced its RocksDB binding with Badger.
- Random point reads of values around 1 KB or larger, with a dataset bigger than RAM, on local NVMe. The 2017 log shows Get latency 3.7x lower than RocksDB at 128 B, 4.2x lower at 1 KB and 5.4x lower at 16 KB. On current versions this only applies if you lower ValueThreshold so values actually go to the value log.
- Bulk loading of large values. In the same log, loading 75M x 1 KB was about 4.6x faster than RocksDB (17m10s vs 78m08s), and 5M x 16 KB about 12x faster (6m55s vs 1h22m21s).
- Key-only scans and existence checks. With PrefetchValues=false, iteration never touches the value log: 250M keys took 0.71 s, against 5.8 s for RocksDB's key+value iteration.
- Embedded use that needs concurrent ACID transactions with SSI conflict detection, TTLs or multi-version reads. Dgraph, Jaeger and go-ipfs are listed users.

## Skip it when

- Small values under write-heavy load. In the same log Badger loaded 250M x 128 B more slowly than RocksDB (45m27s vs 39m11s) and 1B x 16 B about 1.9x more slowly (3h04m vs 1h38m). Dgraph's blog blames Badger's slower compactions.
- Range scans that return values. Iterating 250M x 128 B with values took 75.8 s vs 5.8 s for RocksDB (about 13x slower), and about 4x slower at 1 KB, because each value is a separate read from the value log.
- Memory-limited or 32-bit deployments. Peak RSS while loading was about 14 GB vs 0.6 GB for RocksDB. Value-log files are always mmapped, since the FileIO mode was removed in v3. Users report page-cache thrashing in 500 MB containers (#2255) and mmap failures on 386 (#2287).
- Heavy delete or overwrite workloads that need disk space back automatically. The application has to drive value-log GC through RunValueLogGC, which frees at most one file per call. Open issues report GC stalls when the active file has the most garbage (#2334) and tombstones that automatic compaction never removes from L6 (#2329).
- Non-Go stacks, or anything that expects RocksDB's API, on-disk format or tools. Badger's own on-disk format also changes between major versions, and moving data across one requires a backup and restore.

## How it is fast

It follows the WiscKey paper (FAST '16): values above ValueThreshold go to an append-only value log that doubles as the write-ahead log, and the LSM tree holds only keys plus 12-byte value pointers (file id, length, offset). This keeps the tree small enough to stay in RAM (Dgraph measured a 1.7 GB LSM tree for 75M keys x 1 KB, against 50 GB for RocksDB), so a point read is an in-memory table search with bloom filters plus one read from the value log. Compactions rewrite only keys and pointers, so write amplification falls as values grow. Supporting pieces are an arena-allocated, atomics-based concurrent skiplist memtable adapted from RocksDB's inline skiplist, per-table bloom filters, Ristretto block and index caches, and mmap-backed value-log files.

## Compared with alternatives

Pick Badger when the application is written in Go and must stay cgo-free: every catalogued sibling (Titan, PebblesDB, SplinterDB, NuDB, ToplingDB, etc.) is C/C++. If you already run RocksDB and want the same key-value-separation gain for large values, Titan provides it as a RocksDB plugin (reported \~70% faster data loading) without changing engine or API.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Pure Go, no cgo. Depends on dgraph-io/ristretto/v2 (caches and allocator), klauspost/compress (zstd), cespare/xxhash, google/flatbuffers, protobuf, golang.org/x/sys, OpenTelemetry (zpages) and cobra (CLI only). jemalloc is optional: only the CLI Makefile builds with the `jemalloc` tag. |
| **Minimum toolchain** | go.mod declares go 1.24.0, though the README still says Go 1.23+. Import path is github.com/dgraph-io/badger/v4. |
| **Platforms** | Linux, macOS and BSD are fully supported (POSIX locking and fsync). On Windows, directory locking works differently. AIX has no directory fsync, and Plan9 and WASM/JS have no file locking. 32-bit builds are fragile because of mmap address-space limits (#2287), and a ppc64el test failure is open (#2079). The source tree contains no assembly files. |
| **Thread safety** | The DB is safe for concurrent use, and many transactions can run at once, with SSI conflict detection returning ErrConflict on commit. A single Txn is not thread-safe, so call its methods serially. A directory lock allows one read-write process per directory; ReadOnly mode lets several processes open the same directory. |
| **Drop-in for the baseline** | no |

## Gotchas

- Current defaults do not match the benchmark. Since v3.2103.0 (2021), ValueThreshold defaults to 1 MB, so values under 1 MB are stored inline in the LSM tree and Badger behaves like an ordinary LSM store. The default was 32 B until it was raised to 1 KB and then 1 MB. The 2017 run also used TableLoadingMode=LoadToRAM, an option removed in v3.2011.0. Call WithValueThreshold with a small value to get the WiscKey behaviour that was measured.
- Space reclamation is manual. Call db.RunValueLogGC(ratio) on a ticker, re-running while it returns nil. It never collects inline values or the active vlog file. TTL expiry and deletes also do not shrink a database that has stopped taking writes, because compactions only run when writes arrive.
- Use v4.9.6 or later. v4.9.3 and v4.9.4 fixed deleted keys reappearing after compaction (#2278) and after vlog GC (#2310), and fixed acknowledged writes being dropped during DropPrefix/DropAll (#2313). The v4.9.4 compaction fix then slowed large bulk imports about 3x (#2327), which v4.9.6 fixed (#2330).
- Transaction and size limits: a transaction fails with ErrTxnTooBig once pending writes pass 15% of MemTableSize (use WriteBatch for bulk loads). Keys are capped at 65,000 bytes and values at ValueLogFileSize. Calling Close twice, or writing after Close, panics with a closed-channel error.

## Known shortcomings

- First-party benchmark with no CPU model: RocksDB ran with default options through cgo while Badger's LSM sat in RAM. Loads with 128 B values are slower than RocksDB.
- The benchmark does not reflect current defaults (ValueThreshold is 1 MB since v3.2103.0, so values under 1 MB are stored inline in a plain LSM; LoadToRAM removed in v3.2011.0). Loses on small values (128 B load 45 vs 39 min; 16 B \~1.9x slower); scans with values \~13x slower at 128 B and \~4x at 1 KB. Peak RSS during load \~14 GB vs 0.6 GB for RocksDB; mmap cannot be disabled.
- Value-log GC is manual and frees at most one file per call; open GC stall (#2334) and never-compacted L6 tombstones (#2329). Use &gt;=v4.9.6: earlier versions had deleted-data-reappears bugs (#2278/#2310), dropped acknowledged writes (#2313) and a 3x bulk-import regression in v4.9.4 (#2327).

## Caveats and trade-offs

This is Dgraph's own 2017 benchmark against RocksDB v5.1.4, and the badger-bench repo has been archived (last commit 2019-09-20). Tuning was asymmetric: RocksDB was opened read-only with default options, a 16-bit bloom filter and the default block cache, called through cgo, while Badger ran with TableLoadingMode=LoadToRAM so its LSM tree sat in memory. Badger did not win every test. Loading 250M x 128B was slower with Badger (45:26.56 vs 39:10.78 for RocksDB), and the blog post says Badger can be 2-3x slower to load 16-byte values. Go version and CPU model are not stated.

Pure Go, no Cgo; separates keys from values (WiscKey design) so full-value iteration is much slower than RocksDB's (see companion BENCH-lmdb-bolt.md iterate-with-values numbers); higher resident memory during population (14GB+ RSS) than RocksDB in this test.

## Maintenance

Actively maintained (v4.9.6 released 2026-08-05, commits through 2026-09-21), Apache-2.0, and used in production by Dgraph, Jaeger and go-ipfs. The headline numbers, though, come from an archived 2017 benchmark whose options and defaults no longer exist, so re-benchmark current v4 before relying on them.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** BENCH-rocks.txt is Dgraph's own log with public code (badger-bench bench_test.go, populate/, store/store.go) and states the i3.large instance plus the RocksDB v5.1.4 build (USE_RTTI=1 make shared_lib, in the README). It gives no CPU model and no Go version, so it cannot be A, and a first-party run with partial methodology is C.
- **Verifier notes:** The numbers match the page: 118982 vs 32361 ns/op and the 3.67x headline, plus 1:18:08 vs 17:09.66 for loading 75M x 1KB (\~4.55x, derived). The page shows the same trend at 1KB reads (156694 vs 37053 ns/op) and 16KB reads (215171 vs 40178). The original blog URLs (blog.dgraph.io/post/badger/, dgraph.io/blog/post/badger/) return 404, so I read an archive.org copy. The default branch's last commit is 2026-09-21; 2026-09-23 is pushed_at.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dgraph-io/badger-bench/master/BENCH-rocks.txt>
  - <https://raw.githubusercontent.com/dgraph-io/badger-bench/master/README.md>
  - <https://raw.githubusercontent.com/dgraph-io/badger-bench/master/bench_test.go>
  - <https://raw.githubusercontent.com/dgraph-io/badger-bench/master/store/store.go>
  - <https://github.com/dgraph-io/badger-bench>
  - <https://github.com/dgraph-io/badger>
  - <https://dgraph.io/blog/post/badger/>
  - <https://blog.dgraph.io/post/badger/>
  - <https://web.archive.org/web/2018/https://blog.dgraph.io/post/badger/>
- **Sources the enricher read:**
  - <https://github.com/dgraph-io/badger>
  - <https://github.com/dgraph-io/badger/blob/main/README.md>
  - <https://github.com/dgraph-io/badger/blob/main/go.mod>
  - <https://github.com/dgraph-io/badger/blob/main/docs/design.md>
  - <https://github.com/dgraph-io/badger/blob/main/docs/quickstart.md>
  - <https://github.com/dgraph-io/badger/blob/main/docs/troubleshooting.md>
  - <https://github.com/dgraph-io/badger/blob/main/doc.go>
  - <https://github.com/dgraph-io/badger/blob/main/options.go>
  - <https://github.com/dgraph-io/badger/blob/main/CHANGELOG.md>
  - <https://github.com/dgraph-io/badger/blob/main/txn.go>
  - <https://github.com/dgraph-io/badger/blob/main/db.go>
  - <https://github.com/dgraph-io/badger/blob/main/value.go>
  - <https://github.com/dgraph-io/badger/blob/main/iterator.go>
  - <https://github.com/dgraph-io/badger/blob/main/batch.go>
  - <https://github.com/dgraph-io/badger/blob/main/structs.go>
  - <https://github.com/dgraph-io/badger/blob/main/skl/skl.go>
  - <https://github.com/dgraph-io/badger/blob/main/skl/README.md>
  - <https://github.com/dgraph-io/badger/blob/main/table/README.md>
  - <https://github.com/dgraph-io/badger/blob/main/Makefile>
  - <https://github.com/dgraph-io/badger/blob/main/badger/Makefile>
  - <https://github.com/dgraph-io/badger/releases/tag/v4.9.5>
  - <https://github.com/dgraph-io/badger/releases/tag/v4.9.6>
  - <https://github.com/dgraph-io/badger/issues>
  - <https://github.com/dgraph-io/badger/issues/2334>
  - <https://github.com/dgraph-io/badger/issues/2329>
  - <https://github.com/dgraph-io/badger/issues/2327>
  - <https://github.com/dgraph-io/badger/issues/2287>
  - <https://github.com/dgraph-io/badger/issues/2286>
  - <https://github.com/dgraph-io/badger/issues/2255>
  - <https://github.com/dgraph-io/badger/issues/2049>
  - <https://raw.githubusercontent.com/dgraph-io/badger-bench/master/BENCH-rocks.txt>
  - <https://raw.githubusercontent.com/dgraph-io/badger-bench/master/README.md>
  - <https://raw.githubusercontent.com/dgraph-io/badger-bench/master/bench_test.go>
  - <https://hypermode.com/blog/badger/>
  - <https://web.archive.org/web/2018/https://blog.dgraph.io/post/badger/>
  - <https://hn.algolia.com/api/v1/search?query=badgerdb&tags=comment>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/dgraph-io/badger`) · [data/wave6/enrich/raw/github_com_dgraph_io_badger.json](../../../data/wave6/enrich/raw/github_com_dgraph_io_badger.json) (enrichment confidence 0.85)

</details>
