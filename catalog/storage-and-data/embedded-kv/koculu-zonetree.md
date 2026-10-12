# ZoneTree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C#` · `MIT` · 🟢 active

> Pure-C# LSM-tree ordered key-value engine for .NET; beats RocksDB (via RocksDbSharp) and SQLite on its own indexed profile-store benchmark.

| | |
|---|---|
| **Beats** | RocksDB, SQLite |
| **Claimed result** | Total run time 181,390 ms (ZoneTree) vs 429,036 ms (RocksDB, \~2.4x faster, derived from page data) vs 1,062,037 ms (SQLite, \~5.9x faster, derived from page data). Lookup by email: 388,867/s (ZoneTree) vs 138,471/s (RocksDB) vs 277,620/s (SQLite). Read by user id: 970,010/s vs 272,133/s (RocksDB) vs 404,469/s (SQLite). The raw insert phase is a tie with RocksDB (182,070/s vs 181,662/s). Once the post-insert stabilization is counted, RocksDB's insert-ready throughput (154,360/s) is ahead of ZoneTree's (141,281/s). |
| **Workload** | Live profile-store workload, 2,000,000 profiles: individual inserts, primary-key reads, secondary-index (email) lookups, ordered index scans, indexed range queries, updates, and post-update re-reads, with deterministic checksums verifying identical result sets across engines. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 4345P 8-Core Processor (16 logical processors), 60.4GB available memory, Ubuntu 24.04.3 LTS, X64 |
| **Compiler and flags** | .NET 10.0.9 (net10.0, C# 14), dotnet run -c Release, Server GC. The benchmark policy says reference runs set DOTNET_TieredCompilation=0. |
| **Adoption** | 504 stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/koculu/ZoneTree) · [benchmark](https://github.com/ZoneTree/ZoneTree/blob/main/docs/benchmark/reference/2m/2m.md) |

## Verdict

On the project's own 2M-profile run (one worker, .NET 10.0.9 Release with Server GC, AMD EPYC 4345P 8C/16T, 60.4 GB, Ubuntu 24.04), ZoneTree finished the full live insert/read/index-scan/query/update workload in 181,390 ms. RocksDB 6.2.2 via RocksDbSharp took 429,036 ms and SQLite 3.50.3 took 1,062,037 ms, all with identical checksums. Id reads ran 3.6x faster than RocksDB and email lookups 2.8x faster; raw inserts tied, and RocksDB led on insert-plus-stabilize readiness (154,360/s vs 141,281/s). At 100M profiles the read lead shrinks to about 1.9x and updates tie, and at 20M and 50M RocksDB wins the raw insert and update phases.

## Use it when

- .NET services that need an embedded, ordered, persistent key-value store with seek/range scans and reverse iteration, and want only managed dependencies (K4os LZ4 and ZstdSharp ports, no native RocksDB binaries). It supports NativeAOT on net7.0 and later.
- Read-heavy point lookups and ordered index scans with a working set that fits in RAM with room to spare. At 2M profiles it did 970,010 id reads/s vs RocksDB's 272,133/s and 388,867 email lookups/s vs 138,471/s.
- Live, unbatched single-record writes where SQLite autocommit becomes the bottleneck. At 2M profiles it inserted 182,070 rows/s vs SQLite's 6,231/s (WAL journal, synchronous=NORMAL).
- Building your own index, queue, event-store, TTL or full-text layer on an ordered keyspace. There is an official ZoneTree.FullTextSearch package, plus operation indexes for async replication and live backup of non-transactional trees.
- Cache, temporary or rebuildable data. The NoWAL mode removes WAL cost entirely.

## Skip it when

- Memory-constrained hosts. Peak process memory vs RocksDB was 3.3 GB vs 1.1 GB at 2M profiles, 33.0 GB vs 3.6 GB at 20M, and 56.3 GB vs 11.1 GB at 100M on a 60.4 GB machine, where ZoneTree's on-disk data was only 7.4 GB.
- Write-dominated workloads at tens of millions of rows. On the project's own 20M and 50M runs, RocksDB's raw insert and update phases were faster (20M: 173,190 vs 156,633 inserts/s and 44,044 vs 39,440 updates/s). At 100M, updates were a tie. In issue #108 a user loading 10M string-to-byte[] records measured 7.8 s for ZoneTree vs 4.5 s for RocksDB with batched writes. Without batching, ZoneTree was about 4x faster, and random lookups were about even.
- You need SQL, native secondary indexes, joins or cross-language access. ZoneTree is a .NET-only key-value engine, and the benchmark maintains every secondary index in application code as a separate tree.
- Strict per-write power-loss durability. The default AsyncCompressed WAL can lose recent writes on a crash. Even Sync WAL only flushes to the OS kernel (maintainer, issue #116), and SyncCompressed writes its tail every 500 ms.
- If you are comparing against a tuned modern RocksDB, the published numbers do not tell you the answer. The harness uses RocksDB 6.2.2 through the RocksDbSharp P/Invoke wrapper as five separate instances and sets no block-based-table options (no Bloom filter, no enlarged block cache). Meanwhile ZoneTree runs with a dense sparse index and a block cache bounded by lifetime, not size.

## How it is fast

It is a classic LSM tree. Writes land in an in-memory B+Tree mutable segment (128-entry nodes, node-level monitor locks by default) that sits behind a concurrent Bloom filter and a background async Zstd-compressed WAL. A background maintainer then freezes these segments and merges them into sorted, compressed disk segments. Disk segments are 'multipart': each logical segment is a set of immutable key-range parts, so a merge rewrites only the parts whose range changed and carries clean parts forward, which bounds write amplification. Reads go through a sparse index (step 16 in the benchmark, 1,024 by default), a cache of decompressed 4 MB blocks, 16-entry materialized key/value chunks, per-segment circular key/value caches and prefetch hints for sequential lookups; the project attributes its higher peak memory to the decompressed-block caching.

## Compared with alternatives

Pick ZoneTree when your code is .NET and you want an ordered, embedded, managed-only store with range scans. Most siblings here (Badger, Pogreb, SurrealKV, Speedb, ToplingDB, SplinterDB, NuDB) are Go, Rust or C/C++ engines and would need a native binding such as the RocksDbSharp wrapper this benchmark used. F2/FASTER is the other .NET-relevant sibling; the ZoneTree repo ships a ZoneTree-vs-FASTER harness for Int64 point inserts and lookups but publishes no results from it, so that head-to-head is unmeasured.

## Integration

| | |
|---|---|
| **Form** | shared lib (NuGet package `ZoneTree`, managed assembly) |
| **Dependencies** | K4os.Compression.LZ4 1.3.8, ZstdSharp.Port 0.8.8 (both managed NuGet packages) |
| **Minimum toolchain** | .NET 6 (multi-targets net6.0 through net10.0; library built with C# 14 / LangVersion 14.0) |
| **Platforms** | any .NET 6-10 runtime (managed code with unsafe blocks). Published benchmark runs are Linux x64 and Windows 11 x64. |
| **Thread safety** | The regular write and read APIs (Upsert, TryAdd, TryDelete, TryGet) are designed for concurrent use. Atomic methods synchronize only with each other, for same-key read-modify-write. Multi-key atomicity needs a transactional tree with optimistic transactions. The in-memory B+Tree defaults to node-level monitor locks. NoLock mode is single-thread only. |
| **Drop-in for the baseline** | false. It has its own generic C# API, not RocksDB's C++ API or a SQL interface, and data must be migrated. In the benchmark both engines use a similar layout (one store per index), so porting a RocksDB-style multi-store design is direct, but porting a SQLite schema means rebuilding indexes in application code. |

## Gotchas

- Values in in-memory segments are held by reference. Mutating an object after Upsert, or one returned by TryGet or ReadCommittedTryGet, silently changes what readers see: no WAL record, and a transaction rollback does not undo it (issue #120). Use immutable records or structs, or clone before upserting.
- The comparer, serializers and value types are part of the database identity and cannot change behavior on an existing store. A custom comparer also needs an IKeyHasher that agrees with its equality (for example, a case-insensitive string comparer needs a case-insensitive hasher), or the mutable-segment Bloom filter can wrongly report misses.
- Memory limits are record counts, not bytes: MutableSegmentMaxItemCount defaults to 1,000,000, which is far too much for large string or document values. You also need a maintainer (CreateMaintainer) or your own maintenance loop, or read-only segments pile up. .NET keeps freed memory, so process RSS stays high after merges.
- In v1.8.7 the package and namespace were renamed from Tenray.ZoneTree to ZoneTree, and in v1.9.0 the repo moved from koculu/ZoneTree to the ZoneTree org. TotalRecordCount counts physical versions, not live keys (use Count()). Built-in live backup does not cover transactional trees.

## Known shortcomings

- The 'raw insert 154,360/s' is insert plus stabilize; raw inserts tie RocksDB (182,070 vs 181,662/s). Baseline is RocksDB 6.2.2 via RocksDbSharp; the repo moved to ZoneTree/ZoneTree.
- Memory-heavy: peak 3.3 GB vs RocksDB 1.1 GB at 2M keys, 33 vs 3.6 GB at 20M, 56.3 vs 11.1 GB at 100M (on-disk data only 7.4 GB). Writes lose at scale (RocksDB wins raw insert+update at 20M/50M; a user in #108 saw batched RocksDB inserts 4.5 s vs ZoneTree 7.8 s). Weak baseline: RocksDB 6.2.2 via RocksDbSharp P/Invoke, 5 instances, no Bloom/block-cache options.
- Mutable reference values stay in memory, so mutating after Upsert changes data without the WAL and rollback will not undo it (#120). The default async WAL can lose writes on crash; Sync WAL is only an OS-kernel flush. A custom comparer needs a matching hasher (else Bloom false misses); package renamed Tenray.ZoneTree to ZoneTree at v1.8.7.

## Caveats and trade-offs

Several reference sizes are published (100K to 100M profiles, plus Windows 11 p1/p16 runs). The numbers above come from the 2M-profile Linux report only. The benchmark is a single custom profile-store workload, and the project explicitly warns against generalizing it. The RocksDB baseline is RocksDbSharp/RocksDbNative 6.2.2, an old RocksDB release reached through C# P/Invoke. It runs as five separate RocksDB instances with application-managed secondary indexes and no cross-index WriteBatch. SQLite (3.50.3 via Microsoft.Data.Sqlite) does single-row autocommit writes with synchronous=NORMAL, which is why its insert and update phases are slow. Durability settings differ: ZoneTree uses an async compressed WAL, while RocksDB uses a WAL with unsynced writes. ZoneTree's peak process memory (3.3 GB) is about 3x RocksDB's (1.1 GB). The repo now lives at github.com/ZoneTree/ZoneTree, and koculu/ZoneTree redirects there.

Uses substantially more peak process memory than RocksDB in this benchmark (3.3GB vs 1.1GB) in exchange for higher read/query throughput; ZoneTree and RocksDB secondary indexes are maintained by the benchmark application (separate stores) while SQLite/MySQL maintain them natively, so the storage layouts differ even though results are checksum-identical.

## Maintenance

Actively maintained: v1.9.8 released 2026-09-15, 99 NuGet versions, zero open issues, authored by Ahmed Yasin Koculu under the ZoneTree GitHub org. MIT-licensed and installed from NuGet with no native binaries.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The 2M reference report compares ZoneTree against RocksDB and SQLite, plus MySQL, with matching checksums across engines. It states the CPU (AMD EPYC 4345P), OS and .NET 10.0.9. The benchmark code is public at benchmarks/profile-store/src (ProfileStore.Benchmark.csproj, BenchmarkRunner.cs, RocksDbProfileStore.cs, SqliteProfileStore.cs), and its README gives the build and run settings: dotnet run -c Release, Server GC, DOTNET_TieredCompilation=0 for reference runs.
- **Verifier notes:** Every quoted number matches the 2M report. The only wording error was calling 154,360/s RocksDB's 'raw insert throughput': that figure is its insert-plus-stabilize readiness throughput, and the raw insert phase is effectively tied. Metadata checks out: MIT, 504 stars, last commit 2026-09-15, not a fork, not archived. The canonical owner is now the ZoneTree org.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/koculu/ZoneTree/blob/main/docs/benchmark/reference/2m/2m.md>
  - <https://raw.githubusercontent.com/koculu/ZoneTree/main/docs/benchmark/reference/2m/2m.md>
  - <https://github.com/koculu/ZoneTree>
  - <https://raw.githubusercontent.com/ZoneTree/ZoneTree/main/benchmarks/profile-store/README.md>
  - <https://raw.githubusercontent.com/ZoneTree/ZoneTree/main/benchmarks/profile-store/src/ProfileStore.Benchmark.csproj>
  - <https://raw.githubusercontent.com/ZoneTree/ZoneTree/main/docs/benchmark/benchmark.md>
- **Sources the enricher read:**
  - <https://github.com/koculu/ZoneTree>
  - <https://github.com/ZoneTree/ZoneTree>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/README.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/benchmark/benchmark.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/benchmark/reference/2m/2m.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/benchmark/reference/20m/20m.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/benchmark/reference/50m/50m.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/benchmark/reference/100m/100m.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/benchmark/reference/windows-11/2m-p16/2m-p16.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/benchmarks/profile-store/README.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/benchmarks/profile-store/src/ProfileStore.Benchmark.csproj>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/benchmarks/profile-store/src/ZoneTreeProfileStore.cs>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/benchmarks/profile-store/src/RocksDbProfileStore.cs>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/benchmarks/zonetree-vs-faster/README.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/src/ZoneTree/ZoneTree.csproj>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/src/ZoneTree/Directory.Build.props>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/src/ZoneTree/Collections/BTree/BTree.cs>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/src/ZoneTree/Collections/BTree/Lock/BTreeLockMode.cs>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/src/ZoneTree/Segments/InMemory/MutableSegment.cs>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/src/ZoneTree/Options/ZoneTreeOptions.cs>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/src/ZoneTree/Options/DefaultValues.cs>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/concepts/lsm-tree.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/concepts/segments.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/concepts/value-mutability.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/concepts/bloom-filters.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/concepts/serializers-and-comparers.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/usage/reads-and-writes.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/usage/transactions.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/durability/wal-modes.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/durability/recovery.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/storage/memory-usage.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/storage/compression.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/tuning/write-amplification.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/tuning/read-path-caching.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/tuning/large-values.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/reference/api-overview.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/operations/production-checklist.md>
  - <https://github.com/ZoneTree/ZoneTree/blob/main/docs/operations/troubleshooting.md>
  - <https://github.com/ZoneTree/ZoneTree/issues?q=is%3Aissue>
  - <https://github.com/ZoneTree/ZoneTree/issues/108>
  - <https://github.com/ZoneTree/ZoneTree/issues/115>
  - <https://github.com/ZoneTree/ZoneTree/issues/116>
  - <https://github.com/ZoneTree/ZoneTree/issues/120>
  - <https://github.com/ZoneTree/ZoneTree/issues/133>
  - <https://github.com/ZoneTree/ZoneTree/releases>
  - <https://github.com/ZoneTree/ZoneTree/releases/tag/release-v1.9.8>
  - <https://github.com/ZoneTree/ZoneTree/releases/tag/release-v1.9.5>
  - <https://github.com/ZoneTree/ZoneTree/releases/tag/release-v1.8.8>
  - <https://github.com/ZoneTree/ZoneTree/releases/tag/release-v1.8.7>
  - <https://api.nuget.org/v3-flatcontainer/zonetree/index.json>
  - <https://hn.algolia.com/api/v1/search?query=ZoneTree&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/koculu/zonetree`) · [data/wave6/enrich/raw/github_com_koculu_zonetree.json](../../../data/wave6/enrich/raw/github_com_koculu_zonetree.json) (enrichment confidence 0.8)

</details>
