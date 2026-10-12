# lsm-tree-go

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Small learning-project LSM-tree KV store in Go; beats bbolt only on batched random writes, loses reads and sequential writes.

| | |
|---|---|
| **Beats** | BoltDB |
| **Claimed result** | It wins only on random writes: 1.19M/s vs BoltDB's 0.23M/s (README: '5x faster'; \~5.2x derived from page data). It is slower than BoltDB on the other three columns: sequential write 1.98M/s vs 2.77M/s, read 0.44M/s vs 1.17M/s, and miss-read 1.08M/s vs 1.96M/s. BadgerDB beats it on every column: 7.30M/6.97M/1.29M/1.49M per second, i.e. \~3.7x on sequential writes and \~5.9x on random writes (derived from page data; the README says '4x behind'). |
| **Workload** | Linux, 4 CPU, 1 million keys, 11-byte keys+values, batch size 1000: sequential write, random write, read, and miss-read throughput vs BoltDB and BadgerDB. |
| **Metric** | throughput |
| **Hardware** | Linux, 4 CPU (model unspecified) |
| **Adoption** | 2 stars |
| **Last commit** | 2026-05-31 |
| **Links** | [repository](https://github.com/AasheeshLikePanner/lsm-tree-go) · [benchmark](https://github.com/AasheeshLikePanner/lsm-tree-go#benchmarks) |

## Verdict

The README table has one win: random writes at 1.19M/s vs bbolt v1.4.3's 0.23M/s (about 5.2x). It loses to bbolt on sequential writes (1.98M vs 2.77M), reads (0.44M vs 1.17M) and misses (1.08M vs 1.96M), and BadgerDB v4.9.1 leads on every column. The run was Linux with 4 CPUs of unstated model, Go given only by go.mod's 1.25.4, 1M keys and 1,000-key batches, with keys and values described as 11 bytes although bench/compare generates 12-byte ones. bench/compare runs NoWAL, SyncAsync and SyncAlways against synced and unsynced baselines, and the README does not say which row the table shows. Older hardcoded Linux figures in bench/fulltable.go, possibly from a Lima VM, give 0.76M vs 0.27M/s (about 2.8x) for SyncAlways vs bbolt with fsync per commit.

## Use it when

- Studying or teaching LSM internals: about 52 KB of non-test Go in seven small internal packages covers the WAL, memtable, SSTable format, Bloom filter, sparse index, JSON MANIFEST and leveled compaction, and the README has pprof-driven optimization notes.
- As a starting point for an experimental Go storage engine you intend to own, where you will add range scans, write concurrency and crash-consistency work yourself.
- Batched (about 1,000 keys per call) random-order ingestion of small string keys on Linux, where bbolt's random-insert rate (0.23M/s in the author's table) is the bottleneck and point Get/Put/Delete is enough. Even there, BadgerDB was about 5.9x faster in the same table.

## Skip it when

- Reads or mixed workloads. In the author's own table it does 0.44M/s point reads and 1.08M/s misses, against bbolt's 1.17M/1.96M and Badger's 1.29M/1.49M.
- Sorted or sequential bulk loads (bbolt 2.77M/s and Badger 7.30M/s vs 1.98M/s), or anything that needs range scans, iterators, transactions, snapshots, []byte values or concurrent writers. None of these exist.
- macOS. The hardcoded macOS table in bench/fulltable.go shows 191k sequential, 128k random-write and 164k read ops/s in SyncAsync mode, against bbolt NoSync's 2.35M/162k/1.18M. So on macOS it loses even random writes unless both sides fsync.
- Data you cannot afford to lose. There are 2 commits from one day and no issues or releases. The tests are too small to exercise compaction, and there are the stale-read and crash-window problems listed under gotchas.
- Windows: the code calls syscall.Mmap/Munmap, which Go provides only on Unix, and Windows is not documented.

## How it is fast

Writes are buffered. Each PutBatch is serialised into one CRC32-framed record, appended to an mmap'd write-ahead log (one fdatasync per batch in the default SyncAlways mode), and inserted into a Go map memtable pre-sized for 200k entries. At 4 MB the map is sorted and written sequentially to an mmap'd SSTable, and leveled compaction (10x per level, heap-based k-way merge) runs later. This turns random-key inserts into sequential file writes, which is why it beats bbolt's copy-on-write B+tree on random writes but not on sorted ones. Reads check the map, then probe every SSTable in every level in turn, each through a 10-bits/key FNV-1a double-hashing Bloom filter and then a sparse index (every 128th key) plus a linear scan. The README says reads touch 'one file per level', but the code does not do that, and each probe re-hashes the key and allocates strings, which fits the low 0.44M/s read rate.

## Compared with alternatives

Pick it only when you want a small, readable Go LSM to study or fork. For a real Go embedded store pick Badger, which beat it on every column of this same benchmark (7.30M vs 1.98M sequential writes/s, 1.29M vs 0.44M reads/s) and has transactions and iterators. For read-heavy Go point lookups consider Pogreb.

## Integration

| | |
|---|---|
| **Form** | source-drop (every package is under internal/ and go.mod declares module github.com/aasheesh/lsmtree, which does not match the repo path, so it cannot be go-get'd or imported from another module) |
| **Dependencies** | none for the engine (Go standard library only: syscall mmap, hash/fnv, hash/crc32, container/heap). The bbolt v1.4.3 and BadgerDB v4.9.1 entries in go.mod are used only by bench/compare. |
| **Minimum toolchain** | Go 1.25.4 (go.mod 'go' directive) |
| **Platforms** | Linux (fdatasync, optional io_uring WAL mode) and other Unix systems with syscall.Mmap, such as macOS (fsync fallback). Pure Go and architecture-independent. Windows is not supported. |
| **Thread safety** | One DB-wide sync.RWMutex. Get takes the read lock and PutBatch/Delete take the write lock, so writes are serialised (the README says 'single writer'). The background compaction goroutine holds the write lock for a whole compaction pass. Stats counters are atomics. |
| **Drop-in for the baseline** | no |

## Gotchas

- It cannot be imported as a module. All packages sit under internal/ and the module path is github.com/aasheesh/lsmtree, so you must copy the tree into your own module and rewrite the imports.
- Possible stale reads (from code reading). Get scans L0 SSTables oldest-first and returns the first hit, so a key that was overwritten or deleted across two not-yet-compacted L0 files (up to 8 are kept) can return the older value. A file's 'max key' is taken from its last sparse-index entry (every 128th key), so L0-to-L1 overlap detection can miss files. The shipped tests cannot catch this: with at most 50k keys, writing 0.3-2 MB against 0.5-4 MB flush thresholds, the correctness and 'compaction' tests flush at most once, never compact, and read overwrites back only from the memtable. The benchmark ignores the values it reads.
- Write and read stalls. The memtable flush runs synchronously inside the caller's PutBatch, and a forced L0 compaction also runs there once L0 exceeds 16 files. The 'background' compaction goroutine holds the DB-wide write lock while it merges all of level L with all of level L+1, which blocks readers and writers. Compaction errors are discarded.
- Durability varies by mode, and there are crash windows. The zero-value WALSyncMode is SyncAlways (fdatasync per batch). SyncAsync can lose about 10 ms of writes. NoWAL, the fastest mode in bench/compare, loses the unflushed memtable even on a clean Close(), because Close never flushes. SyncIouring is broken as written: the ring's file offset starts at 0, writes are submitted only when the 256-entry ring fills, and the WAL cursor never advances, so Close truncates the log, and reopening an existing WAL in that mode is refused. A flush truncates the WAL before the MANIFEST lists the new SSTable, and compaction deletes its inputs before rewriting the MANIFEST. Open silently skips unreadable SSTables and deletes any .sst file not in the MANIFEST, so a crash in either window loses data. The crash test uses SIGKILL only, not power loss, a point HN commenters also raised.

## Known shortcomings

- Beats BoltDB only on random writes (5.2x) and loses sequential writes, reads and misses; BoltDB is not a listed baseline; README says MIT but there is no LICENSE file; a toy project.
- Not importable (all packages under internal/ and the module path differs from the repo); the win is only random writes vs bbolt (1.19M vs 0.23M/s), losing sequential writes, reads and misses (Badger wins every column); on macOS it loses even random writes. fulltable.go prints hard-coded numbers rather than measuring.
- From code reading: Get scans L0 oldest-first (stale reads, undone deletes possible); flush runs in the caller's PutBatch and compaction holds a DB-wide write lock; errors are dropped. Crash windows: WAL truncated before MANIFEST, inputs deleted before MANIFEST, orphan .sst deleted, NoWAL Close loses the memtable, SyncIouring broken. Two commits in one day; no scans/transactions; no Windows.

## Caveats and trade-offs

The only win is random writes vs BoltDB (a B+tree, where random inserts are its known weak case). It is slower than BoltDB on sequential writes, reads and miss-reads, and slower than BadgerDB everywhere. CPU model unstated; Go toolchain only implied by go.mod (go 1.25.4). bench/compare runs several durability modes (NoWAL, SyncAsync, SyncAlways vs BoltDB/BadgerDB with and without sync), and the README does not say which mode the table shows. The license is declared only by a one-word 'License: MIT' README section: there is no LICENSE file or copyright notice, and GitHub reports none, so confirm with the author before vendoring. BoltDB is not one of the category's named incumbents, though it is a widely used embedded KV store (bbolt/etcd). 2 stars; single-writer toy engine.

Small personal/teaching LSM-tree implementation, not a hardened production engine; read throughput (0.44M/s) is lower than both BoltDB and BadgerDB in the same table.

## Maintenance

This is a single code drop: two commits on 2026-05-31, nothing since, and no releases, tags, issues or PRs. It is MIT only through a one-word README section with no LICENSE file. It is small enough to vendor by copying, but treat it as study material rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README table against BoltDB (bbolt v1.4.3) and BadgerDB (v4.9.1). The benchmark code is public (bench/compare/compare.go), but the CPU model is unstated ('Linux, 4 CPU'), the Go toolchain is given only by go.mod's 'go 1.25.4', and the durability mode behind the table is unspecified, so this is C.
- **Verifier notes:** Downgraded because the claim was overstated by omission: the README table shows lsm-tree-go losing to BoltDB on 3 of 4 columns, which the record never said. The README explicitly declares MIT, so license and usability are corrected to MIT/copyable, with a caveat that there is no LICENSE file. Other metadata checks out: 2 stars, not a fork, last commit 2026-05-31, active.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/AasheeshLikePanner/lsm-tree-go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go#benchmarks>
  - <https://raw.githubusercontent.com/AasheeshLikePanner/lsm-tree-go/main/README.md>
  - <https://raw.githubusercontent.com/AasheeshLikePanner/lsm-tree-go/main/bench/compare/compare.go>
  - <https://raw.githubusercontent.com/AasheeshLikePanner/lsm-tree-go/main/go.mod>
- **Sources the enricher read:**
  - <https://github.com/AasheeshLikePanner/lsm-tree-go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go#benchmarks>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/README.md>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/go.mod>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/.gitignore>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/lsm/lsm.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/lsm/correctness_test.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/lsm/compaction_test.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/lsm/crash_test.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/memtable/entry.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/wal/wal.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/wal/sync_linux.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/wal/sync_default.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/wal/io_uring_linux.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/wal/io_uring_stub.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/compaction/compaction.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/sstable/sstable.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/sstable/sync_linux.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/sstable/sync_default.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/bloom/bloom.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/internal/sparseindex/sparseindex.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/bench/compare/compare.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/bench/fulltable.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/blob/main/cmd/lsmdemo/main.go>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/commits/main>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/issues?q=is%3Aissue>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/pulls?q=is%3Apr>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/releases>
  - <https://github.com/AasheeshLikePanner/lsm-tree-go/tags>
  - <https://github.com/aasheesh/lsmtree>
  - <https://hn.algolia.com/api/v1/search?query=lsm-tree-go>
  - <https://hn.algolia.com/api/v1/search?query=AasheeshLikePanner>
  - <https://hn.algolia.com/api/v1/search?query=My%20LSM%20tree%20was%20slower%20than%20a%20B-tree&tags=story>
  - <https://hn.algolia.com/api/v1/items/48542963>
  - <https://aasheesh.vercel.app/blog/lsm-tree>
  - <https://medium.com/@ashishrathour1102/my-lsm-tree-was-slower-than-a-b-tree-then-i-profiled-it-26da851ed33a>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/aasheeshlikepanner/lsm-tree-go`) · [data/wave6/enrich/raw/github_com_aasheeshlikepanner_lsm_tree_go.json](../../../data/wave6/enrich/raw/github_com_aasheeshlikepanner_lsm_tree_go.json) (enrichment confidence 0.8)

</details>
