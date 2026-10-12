# TurboKV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Async (Tokio) Rust LSM key-value store whose unsynced-WAL mode acknowledges single-caller writes 2-4x faster than fjall 2.11.

| | |
|---|---|
| **Beats** | fjall (the page's like-for-like peer); redb shown only as architectural context |
| **Claimed result** | Like-for-like vs fjall (TurboKV Durable vs fjall Buffer, both process-crash-recoverable, no per-write sync): sequential fill 1,774,574 vs 485,252 ops/s (\~3.7x, derived from page data); random fill 906,806 vs 456,924 (\~2.0x, derived from page data); batch 1,000/txn 2,380,390 vs 572,671 (\~4.2x, derived from page data). The TurboKV column comes from a separate 'modes' run; in the single ingest run the ratios are \~1.8-4.4x (derived from page data). Against redb there is no like-for-like number, because redb Eventual issues a macOS F_BARRIERFSYNC per transaction. TurboKV Fast (no WAL) batch-1000 at 3,724,635 vs redb 134,636 (\~27.7x, derived from page data) crosses durability classes, and the page says Fast 'is not comparable to persistent engine rows'. TurboKV Paranoid (full sync) loses to redb Eventual at 1 key/txn (213 vs 1,397) and at 100 keys/txn (20,670 vs 80,197), and edges it at 1,000 keys/txn (162,938 vs 134,636). |
| **Workload** | 200,000 deterministic 20-byte keys / 400-byte values (84MB, above the 64MiB memtable), single caller, sequential/random fill, overwrite, and batched (100/1000 keys per txn) writes, compression and block cache disabled. |
| **Metric** | throughput |
| **Hardware** | Apple M4 (Mac16,1), 32 GiB RAM, macOS 15.3.2, APFS |
| **Compiler and flags** | rustc 1.88.0 (6b00bc388 2025-06-23); cargo bench with benchmarks/Cargo.toml [profile.bench] opt-level=3, lto=thin, codegen-units=1. The README recommends RUSTFLAGS -C target-feature=+aes,+neon (ARM) / +aes,+sse2 (x86) for the AES Bloom-filter path, but the result artifacts do not record RUSTFLAGS. |
| **Adoption** | 270 stars |
| **Last commit** | 2026-08-29 |
| **Links** | [repository](https://github.com/kingroryg/turbokv) · [benchmark](https://github.com/kingroryg/turbokv#benchmarks) |

## Verdict

The author's harness pits TurboKV 0.6.0 durable (unsynced mmap WAL) against fjall 2.11.2 PersistMode::Buffer. Setup: one caller, 200,000 x 20-byte keys / 400-byte values (84 MB), compression and block cache off, rustc 1.88.0 at opt-level 3 with thin LTO, Apple M4 / macOS 15.3.2 / APFS, 3 repetitions. The README table shows median write-acknowledgement throughput of 3.7x (sequential fill), 2.0x (random fill), 2.1x (overwrite), 4.5x (100-key batches) and 4.2x (1,000-key batches) over fjall. But the TurboKV column comes from a later separate run: within the single shared run the ratios are 1.8-4.4x, and counting forced flush and compaction ('settled' throughput) they shrink to about 1.1-1.6x.

## Use it when

- A Rust service already on Tokio that needs a local ordered byte-key store and whose bottleneck is write ingest from one or a few callers.
- You can accept losing recent acknowledged writes on power loss or a kernel crash, but not on a process crash. That is the durable() contract, the same class as fjall's PersistMode::Buffer.
- Bulk loads or grouped writes: atomic batches of 100-1,000 keys reached about 2.3M keys/s in durable mode and about 0.16M keys/s in paranoid mode (1,000/batch) on an Apple M4.
- Rebuildable caches or scratch data, where fast() (no WAL) acknowledged 1.2-3.9M keys/s for 400-byte values.
- Prefix- or range-scan access patterns over small-to-mid values (the tests used 20-byte keys and 400-byte values).

## Skip it when

- You need every acknowledged single write to survive power loss from one caller: paranoid() managed about 210-226 ops/s on the M4 (sync-latency bound), below redb Eventual's 1,397-1,549.
- Read-heavy or restart-sensitive workloads. In the older 0.5.0 full matrix, redb beat TurboKV on random point reads (246,119 vs 183,154 ops/s, with fjall at 184,160 tied), and TurboKV reopened about 1 time/s (\~0.97 s per reopen) vs about 10/s for fjall and 12/s for redb. 0.6.0 has no published read or recovery numbers.
- Space-constrained or larger-than-RAM datasets. Disk amplification at the measurement boundary was 2.14x (3.22x for overwrites) vs fjall's 1.43x. Only an 84 MB dataset on a 32 GiB machine was tested, and mmap reads beyond RAM are unmeasured.
- Non-Tokio or no_std environments, multi-process or replicated access, or CPUs/targets without AES+SSE2 or AES+NEON. gxhash has no software fallback, so the crate does not build there.
- You need a mature engine: it is pre-1.0 with about 540 total crates.io downloads and one maintainer. 0.6.0 removed many public APIs, and its v5 WAL cannot be opened by older TurboKV versions.

## How it is fast

In durable mode, each record goes into a WAL segment that is physically preallocated (fallocate on Linux, F_PREALLOCATE on macOS) and shared-memory-mapped, with a record CRC and a commit tag written last. So an acknowledgement is a memcpy into the page cache, not a write(2) or fsync. Encoding uses a thread-local buffer, and a coarse cached clock stamps WAL records; the changelog measures that clock at 599,648 vs 541,401 ops/s for sequential writes. The memtable is a lock-free crossbeam skip list guarded by 65,536 striped per-key mutexes, and fast mode stages inserts in 64-entry per-thread buffers. Reads use mmap'd SSTables, a sharded LRU block cache and exact-key Bloom filters hashed with gxhash (AES-NI/NEON). Flush and leveled compaction are deferred to background tasks, so the headline acknowledgement rate does not include that work.

## Compared with alternatives

Pick TurboKV over SurrealKV or Badger when you want a Rust/Tokio store and single-caller write acknowledgement under process-crash durability is the metric that matters. Prefer SurrealKV (Rust) or Badger (Go) when you need published point-read and update numbers against RocksDB, which TurboKV does not have; its only current cross-engine data is write ingest against fjall 2.11.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | tokio (rt-multi-thread, fs, sync, time), crossbeam-skiplist, parking_lot, memmap2, lz4_flex, snap, zstd (builds the zstd C library via zstd-sys), gxhash 3, crc32fast, lru, bytes, byteorder, serde/serde_bytes, thiserror, tracing, libc, num_cpus; windows-sys on Windows |
| **Minimum toolchain** | Rust 1.85 (MSRV, gated in CI; edition 2021), plus RUSTFLAGS -C target-feature=+aes,+sse2 (x86) or +aes,+neon (ARM), or -C target-cpu=native |
| **Platforms** | Linux, macOS and Windows are built and tested in CI. Needs x86/x86-64 with AES-NI+SSE2 or ARM/AArch64 with AES+NEON. The preallocated mapped-WAL fast path is used where native reservation exists; other filesystems fall back to ordered file writes. |
| **Thread safety** | A Db is shared across Tokio tasks through an Arc (see the concurrent example). Mutations are ordered and batches publish atomically, and each scan sees a point-in-time snapshot. Only one open Db/Engine per directory is allowed: an advisory lock rejects a second opener in the same or another process with DirectoryLocked. |
| **Drop-in for the baseline** | no |

## Gotchas

- The default preset, durable(), does not fsync each write. The WAL is synced only on memtable flush (checked every 60 s, rotation near 64 MiB), on 1 GiB segment rotation and on clean close, and the README says there is no exact loss bound. Use paranoid() if every acknowledgement must reach stable storage.
- A plain `cargo build` fails unless RUSTFLAGS enables AES (gxhash). The persisted Bloom-filter bits depend on gxhash 3's hash, so the on-disk format is tied to that hash.
- Dropping a Db is not a clean shutdown; call close() or close_with_status(). A failed or cancelled mutation may already be in the WAL, so check state before retrying a non-idempotent write. A paranoid group-commit error poisons the handle until reopen.
- Streaming iterators advance synchronously inside async code, doing mmap reads, checksums and decompression, and they pin snapshot readers. Creating a scan can freeze the active memtable, so frequent small scans add flush work. Media or mapping faults on the mmap'd WAL can terminate the process instead of returning an error.

## Known shortcomings

- The \~27x headline compares TurboKV's Fast mode with redb and is not like-for-like; against fjall at matched durability the gain is \~2-4.5x, and Paranoid mode loses to redb at 1/100 keys.
- The default durable() mode does not fsync per write (recent acknowledged writes can be lost on power loss); paranoid() manages \~210 ops/s for a single caller, below redb Eventual (1,397). README fjall ratios mix two runs (same run 1.8-4.4x; \~1.1-1.6x counting flush and compaction); tested only against fjall 2.11.2 with 84 MB of data on a 32 GiB box (no RocksDB/LMDB/sled, nothing larger than RAM). redb is faster on reads (246k vs 183k); reopen \~1 s vs \~0.1 s; disk amplification 2.14x vs fjall 1.43x. Build fails without AES RUSTFLAGS (gxhash); needs Tokio; pre-1.0, one maintainer, agent-driven PRs.

## Caveats and trade-offs

First-party benchmark, though the methodology is unusually complete (pinned versions, source-manifest hash, raw repetitions, CVs). The author compares cross-engine only against fjall and treats redb as 'architectural context'. The artifacts themselves say 'These are baseline observations, not performance claims.' The README table mixes two runs: the TurboKV columns come from the modes artifact and the fjall/redb columns from an earlier ingest artifact. The redb write gap is mostly a durability-boundary artifact (a per-transaction macOS barrier fsync). In the older TurboKV 0.5.0 full matrix, redb beats TurboKV on random reads (246,119 vs 183,154 ops/s), recovery and compaction, and ties on sequential scans. Only writes were benchmarked in the current table. Single machine (Apple M4, APFS), OS page cache not cleared.

redb's single-key rows under Eventual durability pay a macOS F_BARRIERFSYNC per transaction, which the article itself flags as architectural context rather than a strict like-for-like comparison; single-writer, no distributed/replication features; async/Tokio-based API.

## Maintenance

Actively developed (0.6.0 released 2026-08-28, last commit 2026-08-29) under Apache-2.0 and installable with `cargo add turbokv`. It is a young, pre-1.0, single-maintainer crate that needs AES RUSTFLAGS and Tokio, and was developed largely through agent-driven PRs (codex/\* branches, 'ready-for-agent' issues).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now A.
- **Tier reason:** The README Benchmarks table compares against fjall 2.11.2 and redb 2.6.3 using the public harness benchmarks/main.rs (plus engine.rs, workloads.rs, protocol.rs). It states rustc 1.88.0 and the Apple M4 (Mac16,1). The optimization flags are in the committed benchmarks/Cargo.toml [profile.bench] (opt-level=3, lto=thin, codegen-units=1), and the raw JSON/TXT artifacts pin the commit. So A holds; the downgrade is for the overstated claim, not the tier.
- **Verifier notes:** The numbers match the README exactly, but the record's headline (\~27x vs redb) pits TurboKV Fast (no WAL) against redb's barrier-synced Eventual mode, which the page explicitly calls not comparable. So claimed_speedup is restated around the fjall like-for-like rows, and baseline is changed to fjall with redb as context. Metadata verified: Apache-2.0, 270 stars, last commit 2026-08-29, not a fork, not archived.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kingroryg/turbokv>
  - <https://github.com/kingroryg/turbokv#benchmarks>
  - <https://github.com/kingroryg/turbokv/blob/main/benchmarks/README.md>
  - <https://github.com/kingroryg/turbokv/blob/main/benchmarks/Cargo.toml>
  - <https://github.com/kingroryg/turbokv/blob/main/Cargo.toml>
  - <https://github.com/kingroryg/turbokv/blob/main/benchmarks/results/apple-m4-macos-15.3.2/durability-baseline-ingest-current.txt>
  - <https://github.com/kingroryg/turbokv/blob/main/benchmarks/results/apple-m4-macos-15.3.2/durability-baseline-modes-current.txt>
  - <https://github.com/kingroryg/turbokv/blob/main/benchmarks/results/apple-m4-macos-15.3.2/durability-baseline-current.txt>
- **Sources the enricher read:**
  - <https://github.com/kingroryg/turbokv>
  - <https://github.com/kingroryg/turbokv#benchmarks>
  - <https://github.com/kingroryg/turbokv/blob/main/README.md>
  - <https://github.com/kingroryg/turbokv/blob/main/Cargo.toml>
  - <https://github.com/kingroryg/turbokv/blob/main/CHANGELOG.md>
  - <https://github.com/kingroryg/turbokv/blob/main/Dockerfile>
  - <https://github.com/kingroryg/turbokv/blob/main/.github/workflows/ci.yml>
  - <https://github.com/kingroryg/turbokv/blob/main/.github/workflows/soundness.yml>
  - <https://github.com/kingroryg/turbokv/blob/main/benchmarks/README.md>
  - <https://github.com/kingroryg/turbokv/blob/main/benchmarks/Cargo.toml>
  - <https://github.com/kingroryg/turbokv/blob/main/benchmarks/results/apple-m4-macos-15.3.2/durability-baseline-ingest-current.txt>
  - <https://github.com/kingroryg/turbokv/blob/main/benchmarks/results/apple-m4-macos-15.3.2/durability-baseline-modes-current.txt>
  - <https://github.com/kingroryg/turbokv/blob/main/benchmarks/results/apple-m4-macos-15.3.2/durability-baseline-current.txt>
  - <https://github.com/kingroryg/turbokv/blob/main/src/lib.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/src/core/crypto.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/src/storage/db.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/src/storage/engine.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/src/storage/compaction.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/src/storage/cache.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/src/storage/memtable/mod.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/src/storage/memtable/table.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/src/storage/memtable/manager.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/src/storage/wal/mod.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/src/storage/wal/reservation.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/src/storage/sstable/bloom.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/src/storage/sstable/reader.rs>
  - <https://github.com/kingroryg/turbokv/blob/main/examples/concurrent.rs>
  - <https://github.com/kingroryg/turbokv/issues?q=is%3Aissue>
  - <https://github.com/kingroryg/turbokv/pulls?q=is%3Apr>
  - <https://github.com/kingroryg/turbokv/issues/1>
  - <https://github.com/kingroryg/turbokv/issues/63>
  - <https://github.com/hanshiro-dev/turbokv>
  - <https://crates.io/api/v1/crates/turbokv>
  - <https://crates.io/api/v1/crates/fjall>
  - <https://hn.algolia.com/api/v1/items/49486334>
  - <https://github.com/ogxd/gxhash>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/kingroryg/turbokv`) · [data/wave6/enrich/raw/github_com_kingroryg_turbokv.json](../../../data/wave6/enrich/raw/github_com_kingroryg_turbokv.json) (enrichment confidence 0.8)

</details>
