# VortexDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `AGPL-3.0` · 🟢 active

> Hobby C++17 WiscKey-style key-value store with nested sub-databases; beats LevelDB only on small-value new-key inserts.

| | |
|---|---|
| **Beats** | LevelDB |
| **Claimed result** | Small-payload test (10,000 keys, \~8-byte keys, \~10-byte values, memtable 10,000). New-key writes: 550,221 ops/s vs LevelDB's 188,175 (\~2.9x, derived from page data) and vs SQLite individual-transaction mode's 11,222 (\~49x, derived from page data). It is slower than LevelDB on everything else: updates (49,465 vs 188,215 ops/s), read hits (0.063 vs 0.0008 ms/op cold), read misses (0.001 vs 0.0004 ms/op) and range scans (6.58 vs 0.17 ms cold). It is also slower than SQLite's batched mode on writes and updates. With 1 KB values (benchmark.md) it loses to LevelDB on every operation, including new writes (45,709 vs 95,153 ops/s). With a 100k memtable, small-payload writes reach about 536k vs about 186k ops/s. |
| **Workload** | Single-process microbenchmark of 10,000 keys run with an unpublished custom C++ chrono harness. Operations: new-key writes, half-key updates, read hits (cold and hot), read misses and range scans. Payloads are small (\~8-byte keys, \~10-byte values) or 1 KB values, with memtable limits of 1k, 10k and 100k. Baselines are LevelDB v1.23 and SQLite v3.51.3 (synchronous=OFF, journal_mode=MEMORY; individual and batched transactions). |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-12450HX, 12GB RAM @ 4800 MT/s (single channel), 512GB NVMe SSD, Windows 11 Home 64-bit |
| **Compiler and flags** | The benchmark build is not stated. The README build instructions name MSVC (Visual Studio 2019+) or MinGW `g++ -std=c++17 ... -lws2_32`, with no optimization flag. |
| **Adoption** | 3 stars |
| **Last commit** | 2026-05-27 |
| **Links** | [repository](https://github.com/AmeeteSh-A/VortexDB) · [benchmark](https://github.com/AmeeteSh-A/VortexDB#-benchmarking--performance-analysis) |

## Verdict

The author ran an unpublished C++ chrono harness with 10,000 keys on an i5-12450HX laptop (Windows 11, NVMe, single-channel RAM) against LevelDB v1.23 and SQLite v3.51.3 (synchronous=OFF, in-memory journal), with the benchmark's compiler and flags not stated. VortexDB won only small-value (\~8 B key, \~10 B value) new-key inserts, \~550k vs \~188k ops/s (\~2.9x; \~536k vs \~186k with a 100k memtable), and lost updates, read hits, read misses and range scans to LevelDB, plus every operation with 1 KB values.

## Use it when

- Reading or teaching a compact (about 2,000 lines) WiscKey-style engine: value log, sparse-index SSTables, cuckoo filter, heap-based merging iterator, stop-the-world compaction.
- Windows desktop prototypes that want a filesystem-like hierarchical key namespace (root/users/configs) with a text TCP protocol and shell, where losing data is acceptable.
- One-shot bulk loads of tens of thousands of new small keys (\~8-byte keys, \~10-byte values) in one process, the only case where the author measured a win (\~550k vs \~188k ops/s for LevelDB), and only if reads afterwards don't matter.

## Skip it when

- Read-heavy workloads: in the author's small-value test, read hits took 0.063 ms vs LevelDB's 0.0008 ms and range scans 6.58 ms vs 0.17 ms.
- Values of \~1 KB or more, which is where WiscKey is supposed to help: it lost every operation to LevelDB, including new writes (45,709 vs 95,153 ops/s).
- Update-heavy workloads: overwriting a key that is still in the memtable forces a VLog buffer flush plus a VLog read, and small-value updates ran at 49,465 ops/s vs LevelDB's 188,215.
- Anything that needs durability or integrity. There is no fsync. A CRC32 is written with every entry but never checked on read. compact() deletes the old VLog segments before renaming the new one. The memtable index (.idx) is saved only on flush or shutdown, and VLog replay runs only when the loaded index is empty.
- Linux/macOS, concurrent readers, or production use: the server and shell need Winsock2, and the repo has no build system, tests, releases or filed issues (3 stars, one author).

## How it is fast

It uses WiscKey key/value separation: each put appends the entry to a 64 KB user-space buffer in front of 5 MB value-log segments and inserts a pointer into an in-memory std::map, so new-key ingest is buffered sequential appends with no compaction work during the run. A single global cuckoo filter (4 slots per bucket, 8-bit fingerprints) rejects most lookups of absent keys before the memtable or any SSTable is searched. Writes are pushed to the OS only with ofstream::flush; there is no fsync anywhere in the source.

## Compared with alternatives

Only for learning or a Windows toy project, since it is the only one of these with a nested sub-database namespace. For faster writes behind LevelDB's own include/ API pick HyperLevelDB, and for production WiscKey-style key/value separation pick Titan (a C++ RocksDB plugin) or Badger (Go).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the engine (C++17 standard library incl. std::filesystem and std::shared_mutex); ws2_32 (Winsock2) for server.cpp/main.cpp |
| **Minimum toolchain** | C++17; README names MSVC (Visual Studio 2019+) or MinGW g++ -std=c++17 |
| **Platforms** | Windows (only documented platform; server is Winsock2). The engine files use only standard headers, but no non-Windows build is documented. |
| **Thread safety** | One std::shared_mutex per database: writes take it exclusively, but get() holds only the shared lock while it flushes the writer, reopens file handles and edits the LRU cache, so concurrent readers race. |
| **Drop-in for the baseline** | no |

## Gotchas

- The cuckoo filter can give false negatives, which makes get() report an existing key as missing. It is fixed at 10,000 buckets x 4 slots and is never resized. Every put, updates included, adds another fingerprint. A fingerprint is dropped after 500 failed kicks, and the alternate-bucket formula ((i ^ h(fp)) % 10000) is not reversible for a non-power-of-two table. del() of a key that was never stored can also erase a colliding key's fingerprint. The benchmark used only 10,000 keys.
- Every memtable read hit calls invalidate() on its VLog segment. That closes and reopens the file handle and walks the 2,000-entry LRU cache to evict that file's entries, which is why hot reads (0.059 ms) are barely faster than cold ones. Each range or prefix scan also deletes the writer and clears the whole cache.
- get() returns the string "ERROR: Key not found." instead of a status. Any key containing '/' is treated as a path and auto-creates a child database, so such keys can't be stored as plain keys. All files go into the process's current working directory as raw struct/size_t dumps.
- MEMTABLE_LIMIT is a hard-coded const of 100,000, so the 1k and 10k benchmark runs needed source edits. compact() names each 100k-key SSTable chunk with a one-second timestamp, so two chunks written in the same second overwrite each other. The TCP server parses each 1,024-byte recv() as one command, so larger SETs get split. SAVE and LOAD, which copy and delete files, are served with no authentication on 0.0.0.0:8080.

## Known shortcomings

- Loses 4 of 5 operations to LevelDB (with 1 KB values it loses all 5, writes included); the harness is unpublished; the README badge says MIT while LICENSE says AGPL.
- The only win is 10k-key small-value new inserts (\~550k vs \~188k ops/s); it loses to LevelDB on updates, read hits, misses, scans and all 1 KB operations. Its cuckoo filter can give false negatives (fixed 10k buckets, re-insert on every put, fingerprints dropped after 500 kicks, non-reversible alt index), so existing keys can read as missing. get() mutates shared state under a shared lock (concurrent readers race) and reopens the file on every memtable hit.
- SECURITY: unauthenticated SAVE/LOAD commands on 0.0.0.0:8080. No fsync; CRC32 written but never checked; compaction deletes the old value log before the rename; SST chunk names collide within one second. MEMTABLE_LIMIT is hard-coded (the benchmark needed source edits); Winsock-only, no build system or tests; AGPL while the README says MIT.

## Caveats and trade-offs

Tiny single-author hobby project (3 stars). Only 10,000 keys per test, and the benchmark harness is not published in the repo. It loses to LevelDB on 4 of 5 operations with small payloads and on all 5 with 1 KB values, so the only win is small-value bulk inserts. The compiler and flags used for the benchmark are not stated, and the documented g++ build command has no -O flag. Windows-only (Winsock2). The README badge says MIT, but the LICENSE file and GitHub both say AGPL-3.0. Results are self-reported with no independent verification.

WiscKey-style key/value separation wins on sequential new-key ingest (zero write amplification) but loses badly on point-read latency and range scans due to extra random VLog seeks; the update path forces an existence check that drops throughput \~11x versus new writes

## Maintenance

The code is from an April 2026 burst of commits (the only later one, in May 2026, changed the license), with no tests, build files, releases or issues, and it is AGPL-3.0 even though the README badge and footer still say MIT, so vendoring its \~2,000 lines brings AGPL obligations.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README and benchmark.md give first-party numbers against LevelDB v1.23 and SQLite v3.51.3 and state the CPU (i5-12450HX). The 'custom C++ chrono benchmarking suite' is not published in the repo, and the build compiler and flags are not stated, so this is C.
- **Verifier notes:** Downgraded because the claim was overstated. The record said VortexDB loses 3 of 5 operations to LevelDB, but it also loses updates (3.8x slower) and read misses, and benchmark.md shows it losing even new writes with 1 KB values. The only win left is a 10k-key small-value insert test, so the orchestrator may want to treat this as marginal. Metadata checked out: AGPL-3.0, 3 stars, not a fork, last commit 2026-05-27, active.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/AmeeteSh-A/VortexDB#-benchmarking--performance-analysis>
  - <https://github.com/AmeeteSh-A/VortexDB>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/benchmark.md>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/LICENSE>
  - <https://github.com/AmeeteSh-A/VortexDB/tree/main/src>
- **Sources the enricher read:**
  - <https://github.com/AmeeteSh-A/VortexDB>
  - <https://github.com/AmeeteSh-A/VortexDB#-benchmarking--performance-analysis>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/benchmark.md>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/LICENSE>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/vortex.h>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/vortex.cpp>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/vlog.h>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/vlog.cpp>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/sstable.h>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/sstable.cpp>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/cuckoo.h>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/cuckoo.cpp>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/manifest.h>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/manifest.cpp>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/server.h>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/server.cpp>
  - <https://github.com/AmeeteSh-A/VortexDB/blob/main/src/main.cpp>
  - <https://github.com/AmeeteSh-A/VortexDB/commits/main>
  - <https://github.com/AmeeteSh-A/VortexDB/issues?q=is%3Aissue>
  - <https://github.com/AmeeteSh-A/VortexDB/releases>
  - <https://hn.algolia.com/api/v1/search?query=VortexDB&tags=story>
  - <https://github.com/dgraph-io/badger>
  - <https://github.com/tikv/titan>
  - <https://github.com/rescrv/HyperLevelDB>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/ameetesh-a/vortexdb`) · [data/wave6/enrich/raw/github_com_ameetesh_a_vortexdb.json](../../../data/wave6/enrich/raw/github_com_ameetesh_a_vortexdb.json) (enrichment confidence 0.85)

</details>
