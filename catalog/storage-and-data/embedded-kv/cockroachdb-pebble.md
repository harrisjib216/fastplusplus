# Pebble (CockroachDB storage engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `BSD-3-Clause` · 🟢 active

> Go LSM key-value store that replaced RocksDB inside CockroachDB; meets or beats RocksDB on YCSB in vendor benchmarks.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | Text: 'Pebble meets or exceeds RocksDB on the 6 standard YCSB workloads'; the large workload C gap is attributed to better concurrency in Pebble's block and table caches. Chart bars (unlabeled y-axis, approximate readings, derived from page data): at the CockroachDB level, about 21k vs 22.5k (A), 38k vs 40.5k (B), 54k vs 57k (C), 42.5k vs 45k (D), tie at \~6k (E), 9.5k vs 9.8k (F), so about 0-7%. Storage engine only: about 690k vs 860k (A), 750k vs 980k (B), 860k vs 1.6M (C, \~1.85x), 720k vs 890k (D), 185k vs 235k (E), so about 1.2-1.3x except C. |
| **Workload** | YCSB workloads A-F at the CockroachDB level (3-node cluster), plus a storage-engine-only YCSB tool run directly on Pebble and RocksDB for A-E only (workload F was not implemented there). Engines were configured with similar options, identical where they overlapped. Datasets fit in memory; out-of-cache testing is mentioned but not shown. The post does not state the key distribution. |
| **Metric** | throughput |
| **Hardware** | Not specified. The post gives no CPU, instance type or node spec for the charted runs; its AWS/GCP mention refers to the nightly roachtest integration suite, not to these benchmarks. The CockroachDB-level chart is titled '3-node CockroachDB cluster'. |
| **Adoption** | 6,043 stars; default storage engine of CockroachDB since v20.2 (Nov 2020), used in production at scale |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/cockroachdb/pebble) · [benchmark](https://www.cockroachlabs.com/blog/pebble-rocksdb-kv-store/) |

## Verdict

A 2020-09-15 Cockroach Labs post shows unlabeled YCSB bar charts: on a 3-node CockroachDB cluster (A-F) Pebble beat RocksDB by about 0-7% (E tied), and in a storage-engine-only run through the public cmd/pebble YCSB tool (A-E) by about 1.2-1.3x, with about 1.85x on read-only C, all on in-memory datasets. The post names no CPU, instance type, Go or RocksDB version, or flags (RocksDB was presumably 6.2.1, the last version CockroachDB used), and it lists avoiding the cgo boundary as an advantage, so part of the gap may be call overhead; the project's nightly benchmark page tracks Pebble alone, with no RocksDB line.

## Use it when

- A Go service that needs an embedded ordered KV store with RocksDB-style semantics (snapshots, range deletes, merge operators, SST ingestion, prefix bloom filters) without calling C++ through cgo on every operation or maintaining a C++ build.
- Read-heavy, highly concurrent workloads whose working set fits in the block cache. This is where the storage-only comparison showed its largest gain (\~1.85x on YCSB C).
- Write-heavy LSM workloads where read amplification in L0 hurts during write bursts: L0 sublevels and flush splitting target exactly this case.
- Large block caches (tens of GB) in a Go process. Cache and memtable memory live outside the Go heap, which avoids the \~2x RSS blowup the docs describe for GC-managed caches.
- You want an engine that has been the production default of CockroachDB since v20.2 (Nov 2020), with metamorphic and crash testing plus nightly benchmarks.

## Skip it when

- C, C++ or Rust applications: it is a Go library with no C/C++ API, so from those languages RocksDB (or a RocksDB derivative) remains the practical choice.
- You need RocksDB features Pebble omits: column families, transactions, backups, universal or FIFO compaction, tailing iterators, persistent cache, plain or hash table formats, sub-compactions.
- Migrating an existing RocksDB database: v2+ refuses RocksDB-generated DBs, the path runs through v1 plus format-major-version upgrades, and the README warns that unsupported RocksDB features can silently corrupt data.
- Storage-bound or out-of-cache workloads, or when judging end-to-end impact: the published comparison covers only in-memory datasets, and at the CockroachDB cluster level the gain was about 0-7% (workload E tied).
- You depend on direct I/O or io_uring. Neither is part of the design: an io_uring prototype is only an open issue (#4684), and in a 2020 HN thread a maintainer said direct I/O hurt performance in their experiments.

## How it is fast

RocksDB groups concurrent commits into leader/follower batch groups. Pebble instead copies each batch into the WAL buffer under a short mutex, applies it to the lock-free memtable skiplist concurrently, and publishes visible sequence numbers in order through a lock-free single-producer multi-consumer commit queue, which removes the group-concatenation copy and most thread handoffs. The block cache is split into 4 x NumCPU CLOCK-Pro shards whose memory comes from C malloc, outside the Go heap so the GC never scans it; the vendor post credits this cache concurrency for the \~1.85x gap on read-only YCSB C. Smaller contributors: L0 sublevels with flush splitting, a copy-on-write B-tree for file metadata, delete-only compactions under range tombstones, block-property filters that skip blocks, separate flush and compaction pacing, and on newer formats columnar sstable blocks and value separation into blob files; inside a Go program it also avoids a cgo crossing on every call.

## Compared with alternatives

Pick Pebble over the other Go stores in the catalog, Badger and the lookup-focused Pogreb, when you need full RocksDB-style LSM semantics (range tombstones, merge operators, snapshots, SST ingestion) and CockroachDB's production track record, even though Badger's catalogued speedups over RocksDB are much larger. In C++ services, a RocksDB-derived option like Speedb or the Titan plugin keeps you inside the RocksDB ecosystem.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Go modules only, including DataDog/zstd (cgo) or a pure-Go zstd fallback without cgo, golang/snappy, minio/minlz, cockroachdb/errors, cockroachdb/swiss, prometheus client_golang, xxhash/xxh3, google/btree. cgo is optional: with it, cache and memtable buffers come from C malloc; without it, from Go sync.Pool size classes. |
| **Minimum toolchain** | Go 1.23 for the v2.1.7 tag (module path github.com/cockroachdb/pebble/v2); master's go.mod requires Go 1.25.3 and uses the unsuffixed path; CI runs Go 1.26 |
| **Platforms** | PR CI: Linux amd64 (including no-cgo and race builds) and macOS 14. Nightly: Linux 386, Linux arm64, Windows, and s390x under qemu (big-endian). |
| **Thread safety** | Get and NewIter are safe from concurrent goroutines, and concurrent commits go through the commit pipeline. A Batch is not safe for concurrent use (use one per goroutine). The DB must not be closed while any iterator is open. |
| **Drop-in for the baseline** | partial — the Go API mirrors RocksDB concepts and v1 can read RocksDB 6.2.1-format DBs within CockroachDB's feature subset, but there is no C++ API and v2+ cannot open RocksDB databases |

## Gotchas

- Get returns (value, closer, err), and you must call closer.Close(). Cache blocks are reference-counted, manually allocated memory, so a missed Close is a real leak rather than garbage the GC will collect.
- Defaults are small and conservative: 8 MB block cache, 4 MB memtable, and FormatMajorVersion defaults to the oldest supported format (FormatFlushableIngest). Columnar blocks and value separation stay off until you ratchet the format, and ratcheting is permanent.
- Batches are capped at 4 GB, and indexed batches need extra skiplist memory beyond that. The docs point to DB.Ingest of prebuilt sstables for larger atomic writes.
- The docs lag the code: the README's format table ends at FormatColumnarBlocks, while master defines newer formats (FormatValueSeparation, FormatV2BlobFiles, and others). Open issues include SST corruption reports on GCP Hyperdisk (#5726), an unexplained CRC32C mismatch (#6175) and an iterator-state bug in DeletableValueMerger (#6168).

## Known shortcomings

- Evidence is charts only: engine-level \~1.2-1.3x (YCSB-C \~1.85x) and 0-7% at the CockroachDB level; the engine-only run has no workload F; a Go reimplementation tuned for CockroachDB, not a general RocksDB drop-in.
- Go library only (no C/C++ API). Not a drop-in: no column families, transactions, backups or universal/FIFO compaction; v2+ cannot open RocksDB databases and the README warns of silent corruption with unsupported features. Part of the storage-level gain may be cgo call overhead on the RocksDB side; in-memory data only with no hardware/versions. Must Close() the closer from Get or leak off-heap memory; tiny defaults (8 MB cache, 4 MB memtable); one-way format ratchet. Open issues: SST corruption on GCP Hyperdisk (#5726), CRC mismatch (#6175), iterator-state bug (#6168).

## Caveats and trade-offs

The numbers exist only as unlabeled bar charts in a 2020-09-15 vendor post, and the post names no CPU, instance type, Go or RocksDB version, or flags, so it falls short of tier A/B. The YCSB harness is public (cmd/pebble/ycsb.go in the Pebble repo). The storage-only comparison skips workload F. At the CockroachDB level the gain is small (about 0-7%, E tied) because other bottlenecks dominate. The measurements are six years old, and both engines have changed a lot since.

Go, not a drop-in RocksDB replacement (does not implement column families, transactions, backups, universal/FIFO compaction, plain table format, etc.); README carries an explicit warning that opening a RocksDB DB with unsupported features can silently corrupt data.

## Maintenance

Actively maintained (last master commit 2026-09-10, v2.1.7 tagged 2026-08-24, release branches through crl-release-26.2) and usable as an ordinary BSD-3-Clause Go module, though its roadmap and format changes follow CockroachDB's needs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The 2020-09-15 Cockroach Labs post (Peter Mattis) compares Pebble with RocksDB on YCSB in two unlabeled bar charts: a 3-node CockroachDB cluster on A-F and a storage-engine-only run on A-E. The YCSB tool is public (cmd/pebble/ycsb.go), but no CPU, instance type, Go/RocksDB versions or flags are given. That is first-party with partial methodology, so tier C.
- **Verifier notes:** The claim is accurate and conservative. Fixes: the last commit on master is 2026-09-10 (pushed_at 2026-09-26 reflects a push to some other ref); the hardware field wrongly implied the benchmarks ran on AWS/GCP; 'zipf' is not on the page; and chart readings were added. BSD-3-Clause, 6,043 stars, not archived, not a fork.
- **Fields the verifier corrected:** `last_commit`, `hardware`, `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://www.cockroachlabs.com/blog/pebble-rocksdb-kv-store/>
  - <https://images.ctfassets.net/00voh0j35590/6LBp0kl4LVevYtbjryYsVj/33db24b34228d36f5a870182c400bafc/ycsb-3node-cluster-1024x633.png>
  - <https://images.ctfassets.net/00voh0j35590/1Rmz3gGaJ3NUt7kR0aOctj/340739811c9d89e2946d0363b809f6fa/ycsb-storage-engine-only-1024x634.png>
  - <https://github.com/cockroachdb/pebble>
  - <https://github.com/cockroachdb/pebble/tree/master/cmd/pebble>
- **Sources the enricher read:**
  - <https://github.com/cockroachdb/pebble>
  - <https://github.com/cockroachdb/pebble/blob/master/README.md>
  - <https://github.com/cockroachdb/pebble/blob/master/docs/rocksdb.md>
  - <https://github.com/cockroachdb/pebble/blob/master/docs/memory.md>
  - <https://github.com/cockroachdb/pebble/blob/master/go.mod>
  - <https://github.com/cockroachdb/pebble/blob/v2.1.7/go.mod>
  - <https://github.com/cockroachdb/pebble/blob/master/internal/cache/clockpro.go>
  - <https://github.com/cockroachdb/pebble/blob/master/internal/cache/cache.go>
  - <https://github.com/cockroachdb/pebble/blob/master/internal/manual/manual.go>
  - <https://github.com/cockroachdb/pebble/blob/master/internal/manual/manual_cgo.go>
  - <https://github.com/cockroachdb/pebble/blob/master/internal/manual/manual_nocgo.go>
  - <https://github.com/cockroachdb/pebble/blob/master/db.go>
  - <https://github.com/cockroachdb/pebble/blob/master/batch.go>
  - <https://github.com/cockroachdb/pebble/blob/master/iterator.go>
  - <https://github.com/cockroachdb/pebble/blob/master/options.go>
  - <https://github.com/cockroachdb/pebble/blob/master/format_major_version.go>
  - <https://github.com/cockroachdb/pebble/blob/master/cmd/pebble/ycsb.go>
  - <https://github.com/cockroachdb/pebble/blob/master/bench/ycsb.go>
  - <https://github.com/cockroachdb/pebble/blob/master/.github/workflows/ci.yaml>
  - <https://github.com/cockroachdb/pebble/blob/master/.github/workflows/tests.yaml>
  - <https://github.com/cockroachdb/pebble/blob/master/.github/workflows/s390x.yaml>
  - <https://github.com/cockroachdb/pebble/tags>
  - <https://github.com/cockroachdb/pebble/issues?q=is:open+label:C-bug>
  - <https://github.com/cockroachdb/pebble/issues?q=is:open+label:C-performance>
  - <https://github.com/cockroachdb/pebble/issues?q=is:open+corruption>
  - <https://www.cockroachlabs.com/blog/pebble-rocksdb-kv-store/>
  - <https://cockroachdb.github.io/pebble/>
  - <https://hn.algolia.com/api/v1/search?query=pebble%20rocksdb&tags=story>
  - <https://news.ycombinator.com/item?id=24484320>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cockroachdb/pebble`) · [data/wave6/enrich/raw/github_com_cockroachdb_pebble.json](../../../data/wave6/enrich/raw/github_com_cockroachdb_pebble.json) (enrichment confidence 0.8)

</details>
