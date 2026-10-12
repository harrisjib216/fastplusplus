# Pogreb

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Pure-Go embedded key-value store with an on-disk hash index; roughly 10-23x goleveldb random-lookup throughput in the author's chart.

| | |
|---|---|
| **Beats** | goleveldb (pure-Go port of LevelDB; the C++ LevelDB was not tested) |
| **Claimed result** | README chart (image only, no numeric table) shows pogreb random-lookup throughput of roughly 1.2M reads/s at 10K keys falling to roughly 0.7M reads/s at 10M keys, vs roughly 0.13M falling to 0.03M reads/s for goleveldb, i.e. about 10x at 10K keys to about 20x at 10M keys (approximate, read off the chart image; derived from page data); bolt and badgerdb are also well below pogreb at every key count. |
| **Workload** | Random point lookups at 10K, 100K, 1M and 10M keys (chart x-axis) against goleveldb, bolt (bbolt) and badgerdb using akrylysov/pogreb-bench; the tool defaults are 16-64 B keys, 128-512 B values and 1 goroutine, but the README does not state which parameters produced the chart. |
| **Metric** | throughput |
| **Hardware** | DigitalOcean droplet, 8 CPUs, 16GB RAM, 160GB SSD, Ubuntu 16.04.3 |
| **Adoption** | 1.35k stars |
| **Last commit** | 2026-04-06 |
| **Links** | [repository](https://github.com/akrylysov/pogreb) · [benchmark](https://github.com/akrylysov/pogreb#performance) |

## Verdict

The README's only numbers are a 2018-2019 chart (pre-0.9 design without a WAL) of single-goroutine random Get throughput after a DB reopen on a DigitalOcean droplet with 8 vCPUs, 16 GB RAM and SSD (Ubuntu 16.04): pogreb falls from about 1.23M to 0.69M reads/s between 10K and 10M keys, while goleveldb (the Go port, not C++ LevelDB, opened with compression off and no bloom filter configured) falls from about 0.13M to 0.03M, roughly 10-23x slower; bolt is about 4-6x and badger about 10-13x slower. No Go version, CPU model or run flags are given, and at the tool's default key/value sizes even 10M keys (about 3.6 GB, derived) fit in the page cache, though a 2025 third-party test with 50M records (issue #35) agrees on direction: pogreb 2.29M QPS, pebble 1.50M, badger 0.70M, SQLite 0.14M.

## Use it when

- A Go service whose on-disk map is read far more than it is written and needs only point Get/Has, for example a lookup table rebuilt daily and then served read-only (the author's original use case).
- Tens to hundreds of millions of keys (well below the hard 2^32-key cap) that are too large for a Go map but whose index and hot records fit in the OS page cache.
- You want the lowest random-lookup latency and memory use among pure-Go stores. In a 2025 third-party test with 50M records (issue #35), pogreb had a p99 of 5 us against pebble's 13 us and badger's 254 us, with about 42 MB of RAM.
- You need pure Go with zero module dependencies and no cgo, cross-compiling for Linux, macOS or Windows on amd64 or 386.

## Skip it when

- You need range or prefix scans, sorted iteration, transactions, atomic multi-key batches or snapshots. The hash index cannot provide any of them.
- Restart time after a crash matters at scale. Any unclean shutdown makes the next Open discard the index and replay the entire WAL; a user with billions of records estimated this at about 8 days (#35), and another user moved to pebble for this reason.
- Write- or update-heavy workloads. A single RWMutex means each write blocks all readers. Compaction is off by default, so overwrites keep growing the disk footprint: one user reported 26 GB where bbolt used 300 MB (#66). Windows writes are about 10x slower than on Linux (#25, open since 2019).
- Random lookups over data much larger than RAM. On an 8 GB Debian server with 10M keys, reads through mmap dropped to about 420 ops/s and were still slow at 100M keys without mmap (#54, open).
- More than about 1-2 billion keys: collisions rise toward the 2^32 limit (#38). Also out: several processes sharing one DB (a lock file blocks this), low-memory 32-bit ARM (1 GiB initial mmap fails with ENOMEM, #72) and Windows ARM64 (build fails in v0.10.2, #76).

## How it is fast

Keys are hashed with seeded 32-bit MurmurHash3 into an on-disk linear-hashing table (Litwin's algorithm). The table uses 512-byte buckets of 31 fixed-size slots (hash, segment ID, key size, value size, 32-bit offset), chains overflow buckets, and splits one bucket at a time at a 0.7 load factor. A Get reads one bucket, scans its slots for a matching 32-bit hash and key length, then reads the record from the WAL segment and compares the full key: about two random reads per lookup, where an LSM tree or B+tree probes several levels. Index and segment files are memory-mapped read-only with MADV_RANDOM, and writes go through pwrite, so warm lookups are memory reads with no cache on the Go heap; the author's 2018 design post says the switch to mmap nearly doubled lookup speed over plain file I/O.

## Compared with alternatives

Badger is the other catalogued pure-Go store (LSM-based, with transactions); pick pogreb over it when you need only point lookups and want the lowest read latency and memory, since Badger read about 10x fewer keys per second in pogreb's chart and 0.70M vs pogreb's 2.29M QPS in a 2025 third-party test with 50M records. HaloDB (Java) and NuDB (C++) serve other language stacks, and lsm-tree-go's win over BoltDB is on writes, not reads.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (go.mod has no require lines) |
| **Minimum toolchain** | Go 1.18 (go.mod; CI tests 1.18.x and latest 1.x) |
| **Platforms** | Linux, macOS and Windows on amd64 (CI matrix), with GOARCH=386 build-tested; Plan 9 uses a non-mmap backend on main; Windows ARM64 does not build in v0.10.2 (#76) |
| **Thread safety** | All DB methods are safe for concurrent goroutines behind one sync.RWMutex: many readers or one writer, so writes stall reads. Only one process may open a database (lock file, 'database is locked'). |
| **Drop-in for the baseline** | partial — Put/Get/Delete on []byte map directly onto goleveldb calls, but there are no ordered iterators, range scans, batches, snapshots or transactions, Items() order is unspecified, and the on-disk format is different |

## Gotchas

- Durability is off by default. BackgroundSyncInterval=0 never fsyncs, so set it to -1 to fsync every write, or call Sync(). Recovery then truncates each segment at its last valid CRC-checked record.
- Unclean shutdown is detected through the lock file. Open then renames the index files to .bac and rebuilds the whole index from the WAL before it returns, and that time grows with total data size.
- Space is not reclaimed automatically. Set BackgroundCompactionInterval or call Compact(); only segments of at least 32 MiB with at least 50% dead bytes are compacted.
- Get copies every value (one allocation per call). GetAppend (no allocation) and Backup exist only on main after the last tag, v0.10.2 (Dec 2023), so `go get` of the latest release lacks them. Items() is not a point-in-time snapshot: it re-takes the read lock on every Next call, bucket by bucket.

## Known shortcomings

- The real baseline is goleveldb (the Go port), not C++ LevelDB; the \~10-20x is read off a 2018-19 chart that predates the 2020 WAL redesign.
- Any unclean shutdown triggers a full index rebuild from the WAL (\~8 days at billions of records, #35). No fsync by default; with compaction off the disk grows (26 GB vs bbolt 300 MB, #66); hard 2^32-key cap from a 32-bit hash (#38). No range scans, transactions or batches; one writer lock blocks reads; one process per DB. Larger-than-RAM reads collapse to \~420 ops/s (#54); Windows writes \~10x slower (#25); Windows ARM64 does not build (#76); last tag v0.10.2 (2023-12).

## Caveats and trade-offs

Numbers exist only as a chart image; the benchmark code lives in the separate first-party pogreb-bench repo (10 stars, last commit 2024-06-30), which contains no results. The chart dates from 2018-2019 (README Performance section added 2018-01-07; the image is served with Last-Modified 2019-09-24), so it predates pogreb's 2020 write-ahead-log redesign and uses old versions of every engine. The baseline is goleveldb, a Go port, not the C++ LevelDB. Only reads were benchmarked, and there is no CPU model, Go version or build flags. By design pogreb cannot do range scans.

Hash-table index makes range scans impossible; single hash table shared across WAL segments means recovery requires rebuilding the entire index (slow at large scale).

## Maintenance

Apache-2.0, single maintainer, zero dependencies and small enough to vendor, but 'active' overstates it: the last tag is v0.10.2 (Dec 2023), main has had only small changes since (Backup, GetAppend, Plan 9 fixes, last commit 2026-04-06), and issues years old about Windows writes, crash reindexing and the 4B-key cap are still open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party chart in the pogreb README ('Random lookup performance', reads/s vs number of keys) shows pogreb far ahead of goleveldb, bolt and badgerdb; benchmark code is public (akrylysov/pogreb-bench, cmd/pogreb-bench + kv/\*.go) but there is no CPU model (only 'DigitalOcean 8 CPUs'), no Go version/flags and no run parameters, so C.
- **Verifier notes:** Numbers are real and favourable, but they come from a stale chart of pre-0.9 pogreb against goleveldb rather than LevelDB proper, so I pointed benchmark_url at the README section that holds the chart. The pogreb-bench URL holds only code. Metadata checks out (Apache-2.0, 1,350 stars, last commit 2026-04-06, not archived, not a fork).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** Third-party test in issue #35 (2025, 50M records): pogreb 2.29M QPS vs Pebble 1.50M and Badger 0.70M reads.
- **Pages the verifier opened:**
  - <https://github.com/akrylysov/pogreb>
  - <https://github.com/akrylysov/pogreb-bench>
  - <https://akrylysov.github.io/pogreb/read-bench.png>
- **Sources the enricher read:**
  - <https://github.com/akrylysov/pogreb>
  - <https://github.com/akrylysov/pogreb/blob/main/docs/design.md>
  - <https://github.com/akrylysov/pogreb/blob/main/CHANGELOG.md>
  - <https://github.com/akrylysov/pogreb/blob/main/go.mod>
  - <https://github.com/akrylysov/pogreb/blob/main/options.go>
  - <https://github.com/akrylysov/pogreb/blob/main/db.go>
  - <https://github.com/akrylysov/pogreb/blob/main/index.go>
  - <https://github.com/akrylysov/pogreb/blob/main/recovery.go>
  - <https://github.com/akrylysov/pogreb/blob/main/iterator.go>
  - <https://github.com/akrylysov/pogreb/blob/main/datalog.go>
  - <https://github.com/akrylysov/pogreb/blob/main/compaction.go>
  - <https://github.com/akrylysov/pogreb/blob/main/backup.go>
  - <https://github.com/akrylysov/pogreb/blob/main/segment.go>
  - <https://github.com/akrylysov/pogreb/blob/main/fs/os_mmap.go>
  - <https://github.com/akrylysov/pogreb/blob/main/fs/os_mmap_windows.go>
  - <https://github.com/akrylysov/pogreb/blob/main/.github/workflows/test.yaml>
  - <https://github.com/akrylysov/pogreb/commits/main>
  - <https://github.com/akrylysov/pogreb/releases>
  - <https://github.com/akrylysov/pogreb/issues>
  - <https://github.com/akrylysov/pogreb/issues/25>
  - <https://github.com/akrylysov/pogreb/issues/35>
  - <https://github.com/akrylysov/pogreb/issues/36>
  - <https://github.com/akrylysov/pogreb/issues/38>
  - <https://github.com/akrylysov/pogreb/issues/45>
  - <https://github.com/akrylysov/pogreb/issues/46>
  - <https://github.com/akrylysov/pogreb/issues/52>
  - <https://github.com/akrylysov/pogreb/issues/54>
  - <https://github.com/akrylysov/pogreb/issues/62>
  - <https://github.com/akrylysov/pogreb/issues/63>
  - <https://github.com/akrylysov/pogreb/issues/66>
  - <https://github.com/akrylysov/pogreb/issues/69>
  - <https://github.com/akrylysov/pogreb/issues/72>
  - <https://github.com/akrylysov/pogreb/issues/76>
  - <https://github.com/akrylysov/pogreb-bench>
  - <https://github.com/akrylysov/pogreb-bench/blob/master/go.mod>
  - <https://github.com/akrylysov/pogreb-bench/blob/master/cmd/pogreb-bench/main.go>
  - <https://github.com/akrylysov/pogreb-bench/blob/master/cmd/pogreb-bench/benchmark.go>
  - <https://github.com/akrylysov/pogreb-bench/blob/master/kv/goleveldb.go>
  - <https://github.com/akrylysov/pogreb-bench/blob/master/kv/pogreb.go>
  - <https://github.com/akrylysov/pogreb-bench/blob/master/kv/badger.go>
  - <https://akrylysov.github.io/pogreb/read-bench.png>
  - <https://artem.krylysov.com/blog/2018/03/24/pogreb-key-value-store/>
  - <https://hn.algolia.com/api/v1/search?query=pogreb&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/akrylysov/pogreb`) · [data/wave6/enrich/raw/github_com_akrylysov_pogreb.json](../../../data/wave6/enrich/raw/github_com_akrylysov_pogreb.json) (enrichment confidence 0.8)

</details>
