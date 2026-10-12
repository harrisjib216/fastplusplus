# UnisonDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Go KV database that puts a WAL and memtable in front of LMDB; about 3x LMDB's SET throughput (first-party).

| | |
|---|---|
| **Beats** | LMDB |
| **Claimed result** | (derived from page data, read off scatter plot) SET throughput \~100,000-135,000 req/s for UnisonDB at \~0.2-0.4ms p50 latency vs \~35,000-42,000 req/s for LMDB at \~0.7-0.85ms p50 latency -- roughly 3x higher throughput and \~3x lower latency |
| **Workload** | redis-benchmark against the repo's Redis-compatible Go server (internal/benchtests/cmd/redis-server, run.sh): each of 50 runs issues -t set,get with -n 200000 -r 200000 -d 1000 -c 10 -P 10 --threads 4, i.e. 200k SET then 200k GET requests with 1KB values. Only the SET throughput-vs-p50 chart is published. UnisonDB uses LMDB as its B-tree backend, WAL sync interval 1s and a 16MB memtable arena; the LMDB baseline is PowerDNS/lmdb-go opened with NoSync (periodic env.Sync), with one write transaction per SET. |
| **Metric** | throughput |
| **Hardware** | Apple M2 Pro, 10 cores (6P+4E), 16 GB RAM |
| **Adoption** | 426 stars |
| **Last commit** | 2026-09-12 |
| **Links** | [repository](https://github.com/ankur-anand/unisondb) · [benchmark](https://github.com/ankur-anand/unisondb#redis-compatible-benchmark-unisondb-vs-badgerdb-vs-boltdb-vs-lmdb) |

## Verdict

The author's harness runs redis-benchmark against a Redis-protocol Go server (tidwall/redcon), 50 runs of 200k SET then 200k GET with 1 KB values, 10 clients, pipeline 10 and 4 threads, on an Apple M2 Pro with 16 GB RAM. The Go version is not stated. On the SET-only chart, UnisonDB (LMDB backend, 1 s WAL sync, 16 MB memtable) reaches about 100k-133k req/s at 0.21-0.40 ms p50, against about 35k-42k req/s at 0.69-0.86 ms for PowerDNS/lmdb-go. The LMDB baseline was opened NoSync, synced every 1 s, and used one write transaction per SET. Durability windows are similar, so the roughly 3x comes from write buffering and batching, not a faster B-tree.

## Use it when

- You need one writer fanning out to tens or hundreds of read replicas and want the WAL to be the replication stream, with no separate Kafka or CDC pipeline.
- Write-heavy KV workloads with values around 1 KB, where you would otherwise run LMDB with one small write transaction per update and can accept about 1 s of fsync lag.
- Replicas should keep serving local reads while offline and catch up later from a stored (segment, offset) or LSN.
- Rows where only a few columns change per update, or large objects written as chunks that must commit atomically.
- Linux deployments (the only release target is linux/amd64) with cgo and LMDB headers available.

## Skip it when

- You need a mature embedded KV store: the README marks it alpha, there are no tagged releases, and in December 2025 the author wrote on HN that it was still being hardened in test/staging and not yet in production.
- Every acknowledged write must be durable: SETs return after the mmap append, and the WAL is fsynced only on the 1 s ticker (msync every 1 MB), so a power loss can drop recent writes.
- Read-dominated workloads: GET results are not charted, and a GET can check the active memtable and every sealed memtable before reaching LMDB, so plain LMDB reads should be as fast or faster.
- Windows, or pure-Go builds without cgo: the docs list only Linux and macOS, and the LMDB backend needs cgo.
- Datasets larger than RAM, or sustained writes faster than the LMDB flush can drain: the benchmark keyspace (200k x 1 KB, about 200 MB) fits in page cache, and engine.go has no write stall or backpressure on the sealed-memtable queue.

## How it is fast

Writes do not touch the B+tree inline. Under one engine mutex, each Put appends a FlatBuffer-encoded record to WALFS, an mmap-backed segmented log (msync every 1 MB by default, full fsync on a 1 s ticker), and inserts into an arena skiplist memtable (Badger's skl package) with a Bloom filter. When the arena fills, the memtable is sealed and a background goroutine flushes it to LMDB in key order, 16 puts per write transaction. Compared with raw LMDB doing one copy-on-write transaction per SET, this is ordinary LSM-style write buffering and batching. The B-tree underneath is still LMDB (or bbolt).

## Compared with alternatives

Among the Go siblings (Badger, Pebble, Pogreb, lsm-tree-go), pick UnisonDB only when built-in WAL-streaming replication to many read replicas matters more than engine maturity; on its own chart it also beats Badger v4 on SETs (about 133k vs 67k-80k req/s). For a single-node embedded store, Badger or Pebble are far more mature and have documented Go APIs.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | LMDB via cgo (PowerDNS/lmdb-go) or bbolt; Badger v4 (skiplist arena), bits-and-blooms/bloom, FlatBuffers, gRPC, and AWS/Azure/GCS SDKs for blob replication; ZeroMQ (libzmq) only when built with -tags zeromq |
| **Minimum toolchain** | go.mod declares go 1.25.2 (the docs say Go 1.24+ and the Dockerfile uses golang:1.24); cgo required |
| **Platforms** | Linux and macOS per the docs; goreleaser builds linux/amd64 only; the benchmark ran on Apple M2 Pro (arm64) |
| **Thread safety** | Engine is safe for concurrent use: all writes are serialized under one engine mutex, and reads take a short read lock to snapshot the memtables. Single primary per namespace; replica reads have no strong consistency guarantee (docs). |
| **Drop-in for the baseline** | partial — it uses LMDB (or bbolt) as its storage backend and does not expose LMDB's API. You adopt its own server/HTTP API or its Go engine package, and pay for a WAL and memtable layer on top of LMDB. |

## Gotchas

- The default LMDB map size is 4 GB (btree_config.mmap_size); LMDB fails writes once the map is full, so raise it before loading more data.
- Sealed memtables wait in RAM until the background flush (triggered by rotation or a 30 s ticker) writes them to LMDB. Each is 4 MB by default and 16 MB in the benchmark config. If LMDB falls behind, memory grows and GETs probe more skiplists.
- WAL readers hand out zero-copy slices of mmapped segments. Open issue #186 describes a possible SIGSEGV if the replicator closes a reader, and so unmaps a deleted segment, while the streamer still holds those slices.
- Churn is high: on 2026-09-12 alone the Raft implementation was removed and fixes landed for LMDB/Bolt queue leakage and a replicator busy-loop, so pin a commit.

## Known shortcomings

- The win is architecture, not a faster core: the LMDB baseline commits one NoSync transaction per SET while UnisonDB batches through its WAL and memtable (it also wraps LMDB itself); numbers are chart-derived with no Go version/flags.
- Only SET is charted (no GET numbers); both sides have a \~1 s fsync window and acknowledged writes are not fsynced for up to \~1 s; no backpressure on sealed memtables; LMDB map 4 GB by default. Alpha with no tagged releases (the author said in 2025-12 it is not in production; Raft removed 2026-09-12); possible SIGSEGV in the replicator (#186); cgo required, releases linux/amd64 only, Go 1.25.2+; documented as a server only.

## Caveats and trade-offs

First-party benchmark in its own repo; no Go version or build flags stated. Results exist only as a scatter-plot image, so the numbers are approximate, and GET results are described but not charted. UnisonDB itself uses LMDB as its storage backend. The gain comes from its WAL plus memtable buffering (WAL fsync every 1s, batched flush to LMDB) versus raw LMDB doing one NoSync write transaction per SET behind the same Redis-protocol server. It is a write-path/architecture win, not a faster core B-tree than LMDB. Low confidence.

Numbers only shown as a scatter-plot PNG (docs/ubbl_compare.png), no numeric table, so exact figures are read off axes rather than quoted; Go compiler version not stated; UnisonDB's actual local storage is LMDB itself (it wraps LMDB and adds WAL-based streaming/replication), so the throughput delta likely reflects the Redis-protocol server layer/pipelining differences rather than a faster underlying B-tree.

## Maintenance

Actively developed (last commit 2026-09-12, single main author, 426 stars) and Apache-2.0, but it is an alpha with no tagged releases, recent large architectural changes and an open SIGSEGV issue, so use it only if you can vendor it at a pinned commit and test it yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'SET: Throughput vs p50 Latency' scatter plot (docs/ubbl_compare.png) shows UnisonDB at about 100k-133k req/s and 0.21-0.40 ms p50, against LMDB at about 35k-42k req/s and 0.69-0.86 ms. The harness is public (internal/benchtests/cmd/redis-server/main.go, store/lmdb.go, run.sh) and the CPU is stated (Apple M2 Pro), but no Go version or build flags are given, so this is first-party C, not A.
- **Verifier notes:** Numbers and hardware match the README chart; the record's \~3x throughput / \~3x lower p50 reading is fair (derived from page data). Metadata checks out: Apache-2.0, 426 stars, last commit 2026-09-12, not a fork, not archived. I only sharpened the workload and caveats with the harness config I saw in the source.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ankur-anand/unisondb>
  - <https://github.com/ankur-anand/unisondb#redis-compatible-benchmark-unisondb-vs-badgerdb-vs-boltdb-vs-lmdb>
  - <https://raw.githubusercontent.com/ankur-anand/unisondb/main/README.md>
  - <https://raw.githubusercontent.com/ankur-anand/unisondb/main/docs/ubbl_compare.png>
  - <https://raw.githubusercontent.com/ankur-anand/unisondb/main/internal/benchtests/cmd/redis-server/main.go>
  - <https://raw.githubusercontent.com/ankur-anand/unisondb/main/internal/benchtests/cmd/redis-server/readme.md>
  - <https://raw.githubusercontent.com/ankur-anand/unisondb/main/internal/benchtests/cmd/redis-server/run.sh>
  - <https://raw.githubusercontent.com/ankur-anand/unisondb/main/internal/benchtests/cmd/redis-server/store/lmdb.go>
  - <https://raw.githubusercontent.com/ankur-anand/unisondb/main/internal/benchtests/cmd/redis-server/store/unison.go>
- **Sources the enricher read:**
  - <https://github.com/ankur-anand/unisondb>
  - <https://github.com/ankur-anand/unisondb#redis-compatible-benchmark-unisondb-vs-badgerdb-vs-boltdb-vs-lmdb>
  - <https://raw.githubusercontent.com/ankur-anand/unisondb/main/docs/ubbl_compare.png>
  - <https://github.com/ankur-anand/unisondb/blob/main/internal/benchtests/cmd/redis-server/main.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/internal/benchtests/cmd/redis-server/readme.md>
  - <https://github.com/ankur-anand/unisondb/blob/main/internal/benchtests/cmd/redis-server/run.sh>
  - <https://github.com/ankur-anand/unisondb/blob/main/internal/benchtests/cmd/redis-server/store/lmdb.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/internal/benchtests/cmd/redis-server/store/unison.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/internal/benchtests/cmd/redis-server/store/badger.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/internal/benchtests/cmd/redis-server/store/bolt.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/go.mod>
  - <https://github.com/ankur-anand/unisondb/blob/main/internal/benchtests/go.mod>
  - <https://github.com/ankur-anand/unisondb/blob/main/Makefile>
  - <https://github.com/ankur-anand/unisondb/blob/main/dev.md>
  - <https://github.com/ankur-anand/unisondb/blob/main/Dockerfile>
  - <https://github.com/ankur-anand/unisondb/blob/main/.goreleaser.yml>
  - <https://github.com/ankur-anand/unisondb/blob/main/.github/workflows/go.yml>
  - <https://github.com/ankur-anand/unisondb/blob/main/cmd/unisondb/config.toml>
  - <https://github.com/ankur-anand/unisondb/blob/main/dbkernel/common.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/dbkernel/engine.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/dbkernel/engine_public.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/dbkernel/internal/memtable/memtable.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/dbkernel/internal/wal/wal.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/dbkernel/internal/wal/common.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/pkg/kvdrivers/README.md>
  - <https://github.com/ankur-anand/unisondb/blob/main/pkg/kvdrivers/api.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/pkg/kvdrivers/lmdb.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/pkg/kvdrivers/lmdb_txn_queue.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/pkg/walfs/README.md>
  - <https://github.com/ankur-anand/unisondb/blob/main/pkg/walfs/walog.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/pkg/walfs/segment.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/pkg/notifier/factory_stub.go>
  - <https://github.com/ankur-anand/unisondb/blob/main/pkg/notifier/factory_zeromq.go>
  - <https://github.com/ankur-anand/unisondb/issues>
  - <https://github.com/ankur-anand/unisondb/issues/186>
  - <https://github.com/ankur-anand/unisondb/issues/182>
  - <https://github.com/ankur-anand/unisondb/releases>
  - <https://github.com/ankur-anand/unisondb/tags>
  - <https://github.com/ankur-anand/unisondb/commits/main>
  - <https://unisondb.io/docs/getting-started/>
  - <https://unisondb.io/docs/architecture/>
  - <https://hn.algolia.com/api/v1/search?query=unisondb&tags=story>
  - <https://news.ycombinator.com/item?id=45934624>
  - <https://news.ycombinator.com/item?id=46261281>
  - <https://news.ycombinator.com/item?id=45858740>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/ankur-anand/unisondb`) · [data/wave6/enrich/raw/github_com_ankur_anand_unisondb.json](../../../data/wave6/enrich/raw/github_com_ankur_anand_unisondb.json) (enrichment confidence 0.4)

</details>
