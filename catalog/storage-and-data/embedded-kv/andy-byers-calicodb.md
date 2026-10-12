# CalicoDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Small C++17 embedded transactional B+-tree key-value store modeled on SQLite's WAL design; beats SQLite on large-value reads and sequential fills.

| | |
|---|---|
| **Beats** | SQLite |
| **Claimed result** | Latency in microseconds per op, CalicoDB 0.0.1 vs SQLite3 3.39.5. readrand100K: 58.801 vs 252.367 on Linux (\~4.3x, derived from page data) and 79.160 vs 495.537 on macOS (\~6.3x, derived). readseq100K: 58.518 vs 89.065 on Linux (\~1.5x, derived) and 74.773 vs 203.458 on macOS (\~2.7x, derived). fillseqbatch: 1.040 vs 2.033 on Linux (\~2.0x, derived). fillseq: 23.056 vs 29.767 on Linux (\~1.3x, derived). Results are mixed. On Linux CalicoDB is slower on fillrandom, fillrandbatch, overwrite, overwritebatch, readrandom (4.613 vs 4.270) and fillrand100K. On macOS it is slower on fillrandom, fillrandbatch, overwrite and overwritebatch, and much slower on fillseqsync (1101.377 vs 291.237, \~3.8x slower) and fillrandsync (1117.884 vs 213.655, \~5.2x slower) because it uses F_FULLFSYNC. |
| **Workload** | LevelDB db_bench adapted to CalicoDB and SQLite (fillseq, fillseqsync, fillseqbatch, fillrandom, fillrandsync, fillrandbatch, overwrite, overwritebatch, readrandom, readseq, fillrand100K, fillseq100K, readseq100K, readrand100K), run in CI on GitHub Actions ubuntu-latest and macos-latest. CalicoDB 0.0.1 (commit 30fe767) vs SQLite3 3.39.5. SQLite was configured with a WITHOUT ROWID table, WAL mode, 4 KiB pages, synchronous=NORMAL (FULL for the \*sync benchmarks) and EXCLUSIVE locking. |
| **Metric** | latency |
| **Hardware** | GitHub Actions ubuntu-latest / macos-latest runners (exact CPU model unstated) |
| **Compiler and flags** | gcc (version and flags unstated) |
| **Adoption** | 43 stars |
| **Last commit** | 2023-11-01 |
| **Links** | [repository](https://github.com/andy-byers/CalicoDB) · [benchmark](https://github.com/andy-byers/leveldb/blob/db_bench_calicodb/benchmarks/results.md) |

## Verdict

The author ported LevelDB's db_bench to both engines and ran it once in GitHub Actions CI (ubuntu-latest and macos-latest runners, CPU unstated, gcc Release build with no version given) at commit 30fe767. It compared CalicoDB 0.0.1 against SQLite 3.39.5 in WAL mode, with WITHOUT ROWID, 4 KiB pages, a 4 MB cache, exclusive locking and synchronous NORMAL (FULL for the \*sync tests). CalicoDB won clearly on 100 KB-value reads (4.3x/6.3x random, 1.5x/2.7x sequential, Linux/macOS) and by about 2x on batched sequential fills. It was up to \~1.3x slower on random fills and overwrites and 3.8-5.2x slower on the macOS sync-write tests (all ratios derived from the page's microseconds-per-op table).

## Use it when

- Read-heavy embedded workloads with large (about 100 KB) values: readrand100K ran 58.8 vs 252.4 us/op on Linux (\~4.3x, derived) and 79.2 vs 495.5 on macOS (\~6.3x, derived); readseq100K was \~1.5x and \~2.7x faster (derived).
- Bulk-loading sequential keys, especially in batched transactions: fillseqbatch ran 1.04 vs 2.03 us/op on Linux (\~2.0x, derived) and 1.86 vs 4.57 on macOS (\~2.5x, derived); single-op fillseq was \~1.3x and \~2.0x faster (derived).
- A C++ program on Linux or macOS that uses SQLite only as an ordered, transactional key-value file and wants snapshot readers alongside one writer without a SQL layer.
- Memory-constrained or no-exceptions builds: the library compiles with -fno-exceptions and -fno-rtti, handles malloc failure, supports 32-bit targets, and lets you plug in your own allocator (calicodb::configure), Env (filesystem/I/O) and Wal. It also has an in-memory mode (temp_database).
- As a compact, well-documented modern C++ reimplementation of SQLite's B-tree and WAL architecture to study or fork.

## Skip it when

- Production data. The README says it is 'not ready for production'. The v0.1.1 changelog records a WAL sync bug that 'would have likely resulted in data loss/corruption', and issue #118 says the file-format fuzzer 'produces crashes quickly' on corrupted files. There have been no commits since 2023-11-01.
- Random-key inserts and overwrites: SQLite was faster on fillrandom (\~1.09x Linux, \~1.05x macOS), fillrandbatch (\~1.20x / \~1.31x), overwrite and overwritebatch (up to \~1.22x on macOS), and small-value readrandom on Linux (4.61 vs 4.27 us/op). All ratios are derived.
- Per-commit durable writes on macOS: kSyncFull calls fcntl(F_FULLFSYNC). fillseqsync ran 1101 vs 291 us/op (\~3.8x slower) and fillrandsync 1118 vs 214 (\~5.2x slower) against the system SQLite, which the page says uses F_BARRIERFSYNC.
- Windows or MSVC (CMake stops with a fatal error), network filesystems (the README at the benchmarked commit warns it will not work there), or platforms without shared-memory primitives, which only work in exclusive locking mode.
- Workloads that need SQL, multiple concurrent writers, a stable on-disk format or API, or datasets that don't fit comfortably in one file. The README says it is 'only practical for datasets that can reasonably be stored in a single file', and each connection is single-threaded with blocking I/O.

## How it is fast

It is essentially SQLite's storage design without the SQL layer. It uses a B+-tree over slotted pages with a fixed-width indirection vector for in-node binary search, pointer-map pages that hold parent pointers so splits and merges don't rewrite child pages, overflow chains for large payloads, and a SQLite-style write-ahead log with a shared-memory WAL index. Dirty pages sit in a page cache (LevelDB-derived hash table plus LRU list; default 1024 pages) and go to the WAL only on commit or eviction; checkpoints write each unique page back once, sorted by page number. Sequential inserts take a split_nonroot_fast path that splits at the right edge instead of redistributing cells 50/50, and pivot keys are suffix-truncated (Bayer and Unterauer's simple prefix B-tree). The benchmark page credits the gap mainly to SQLite's higher per-operation RDBMS overhead; no per-benchmark profiling is published.

## Compared with alternatives

Every catalogued sibling (for example Titan, ToplingDB, Nova-LSM and DiaLSM) is benchmarked against RocksDB and mostly targets LSM-scale write throughput; pick CalicoDB only when you want a tiny, dependency-free, single-file B+-tree with SQLite-style WAL transactions to replace SQLite as a plain key-value store, especially for large-value reads. Its evidence is one mixed-result CI run from 2023, weaker than most siblings'.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the library (POSIX system calls only); tests need googletest (fetched by CMake FetchContent) and Python 3 |
| **Minimum toolchain** | C++17, CMake 3.14+, GCC 7+ or Clang 5+; MSVC not supported |
| **Platforms** | POSIX only: Linux and macOS are tested in CI (ubuntu-latest, macos-latest, gcc and clang). The -shm file must support mmap unless exclusive locking mode is used. The design doc and v0.2.0 notes claim 32-bit support. No Windows. |
| **Thread safety** | A DB handle and every object derived from it are single-threaded, so give each thread or process its own DB (threads may share an Env). Across connections there is one writer plus concurrent snapshot readers, using SQLite WAL-style shm locks; contended calls return Status::busy(). calicodb::configure() is not thread safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- The published numbers are for commit 30fe767 (2023-07-02, labelled 0.0.1). That predates v0.1.0, predates the v0.1.1 WAL sync fix, and used an older public API with no tx.h or bucket.h. The 54 later commits (nested buckets, a larger local cell size, corruption fixes) were never re-published. The linked raw CI output (actions run 5437371027) now returns 404, and the bench workflow builds CalicoDB from main, so rerunning it today will not reproduce those numbers.
- SQLite is the system libsqlite3 that the runner links, driven through SQL statements with wal_autocheckpoint=4096. CalicoDB runs with its default auto_checkpoint of 1000 frames. The author's disclaimer says SQLite carries more per-operation overhead, so part of each 'win' is simply skipping SQL.
- If a system call fails inside a read-write transaction, the Tx is poisoned: every call returns that error until you return from the update() lambda. commit() does not release file locks until the Tx is deleted, and only one Tx can be live per DB handle.
- Handles are raw pointers you must delete yourself (DB, Tx, Bucket, Cursor), and Bucket handles must be deleted before their transaction ends. Page size (512 to 32768, default 4 KiB) is fixed when the database is created. The last connection to close checkpoints and unlinks the WAL.

## Known shortcomings

- Loses some benchmarks (readrandom on Linux; the \*sync workloads on macOS are about 4-5x slower than SQLite). Stale; the author says it is not production-ready.
- Numbers come from commit 30fe767 (2023-07, older API) and were never re-run over 54 later commits; the raw CI log is gone and the benchmark builds from main, so they cannot be reproduced. The v0.1.1 changelog lists a WAL sync bug 'likely' causing data loss/corruption; fuzzer crashes open (#118). Loses random fills/overwrites by up to \~1.3x; the SQLite side is the system library through SQL with a different autocheckpoint (4096 vs 1000); no Windows/MSVC.

## Caveats and trade-offs

Benchmarked on generic CI runners with no CPU model and no stated compiler version or flags, so it falls short of Tier A despite public benchmark code. The author's disclaimer says SQLite is an RDBMS with more per-operation overhead than a KV store, and the README says CalicoDB is 'not ready for production'. The results are for an old commit (30fe767). Wins are concentrated in large-value (100K) reads and sequential or batched fills; CalicoDB is slower on random and overwrite writes, and several times slower on the macOS \*sync benchmarks. No commits since November 2023.

Results are mixed rather than a clean win: faster on sequential writes and large random-read batches, slower on plain random writes/overwrites. Tiny, low-visibility project (43 stars).

## Maintenance

Stale since 2023-11-01 (v0.2.0 plus 54 unreleased commits, 43 stars) and self-described as not production-ready. It is MIT-licensed and about 50 source files with no dependencies, so it can be vendored for experiments, but you would own maintenance and crash-safety validation.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party db_bench comparison against SQLite 3.39.5. The benchmark code is public (andy-byers/leveldb, branch db_bench_calicodb, benchmarks/db_bench_calicodb.cc and benchmarks/db_bench_sqlite3.cc), but the page states only 'compiled with gcc', with no version or flags, and the runs are on generic GitHub Actions ubuntu-latest and macos-latest runners with no CPU model. That falls short of A.
- **Verifier notes:** The page numbers match the record exactly. The original claimed_speedup undercounted where CalicoDB loses: readrandom on Linux, overwritebatch, fillrand100K on Linux, and the macOS \*sync benchmarks. The last commit (2023-11-01) makes it stale; 43 stars and the MIT license are verified.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/andy-byers/leveldb/blob/db_bench_calicodb/benchmarks/results.md>
  - <https://github.com/andy-byers/CalicoDB>
  - <https://github.com/andy-byers/leveldb/tree/db_bench_calicodb>
- **Sources the enricher read:**
  - <https://github.com/andy-byers/CalicoDB>
  - <https://github.com/andy-byers/CalicoDB/blob/main/doc/design.md>
  - <https://github.com/andy-byers/CalicoDB/blob/main/doc/doc.md>
  - <https://github.com/andy-byers/CalicoDB/blob/main/CMakeLists.txt>
  - <https://github.com/andy-byers/CalicoDB/blob/main/include/calicodb/options.h>
  - <https://github.com/andy-byers/CalicoDB/blob/main/include/calicodb/db.h>
  - <https://github.com/andy-byers/CalicoDB/blob/main/include/calicodb/tx.h>
  - <https://github.com/andy-byers/CalicoDB/blob/main/include/calicodb/bucket.h>
  - <https://github.com/andy-byers/CalicoDB/blob/main/include/calicodb/config.h>
  - <https://github.com/andy-byers/CalicoDB/blob/main/src/tree.cpp>
  - <https://github.com/andy-byers/CalicoDB/blob/main/src/env_posix.cpp>
  - <https://github.com/andy-byers/CalicoDB/blob/main/src/bufmgr.h>
  - <https://github.com/andy-byers/CalicoDB/blob/main/src/pager.cpp>
  - <https://github.com/andy-byers/CalicoDB/blob/main/.github/workflows/bench.yml>
  - <https://github.com/andy-byers/CalicoDB/blob/main/.github/workflows/test.yml>
  - <https://github.com/andy-byers/CalicoDB/commit/30fe767249aebf155c7465271ffe54f03eea4bb0>
  - <https://github.com/andy-byers/CalicoDB/blob/30fe767249aebf155c7465271ffe54f03eea4bb0/README.md>
  - <https://github.com/andy-byers/CalicoDB/blob/30fe767249aebf155c7465271ffe54f03eea4bb0/src/tree.cpp>
  - <https://github.com/andy-byers/CalicoDB/compare/30fe767...main>
  - <https://github.com/andy-byers/CalicoDB/commits/main>
  - <https://github.com/andy-byers/CalicoDB/releases>
  - <https://github.com/andy-byers/CalicoDB/issues?q=is%3Aissue>
  - <https://github.com/andy-byers/CalicoDB/issues/106>
  - <https://github.com/andy-byers/CalicoDB/issues/118>
  - <https://github.com/andy-byers/CalicoDB/actions/runs/5437371027>
  - <https://github.com/andy-byers/leveldb/blob/db_bench_calicodb/benchmarks/results.md>
  - <https://github.com/andy-byers/leveldb/blob/db_bench_calicodb/benchmarks/db_bench_calicodb.cc>
  - <https://github.com/andy-byers/leveldb/blob/db_bench_calicodb/benchmarks/db_bench_sqlite3.cc>
  - <https://github.com/andy-byers/leveldb/blob/db_bench_calicodb/CMakeLists.txt>
  - <https://github.com/andy-byers/leveldb/commits/db_bench_calicodb>
  - <https://hn.algolia.com/api/v1/search?query=calicodb&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=andy-byers&restrictSearchableAttributes=url>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/andy-byers/calicodb`) · [data/wave6/enrich/raw/github_com_andy_byers_calicodb.json](../../../data/wave6/enrich/raw/github_com_andy_byers_calicodb.json) (enrichment confidence 0.78)

</details>
