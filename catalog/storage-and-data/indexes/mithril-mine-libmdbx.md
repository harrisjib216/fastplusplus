# libmdbx

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> LMDB fork: embedded memory-mapped ACID B+tree KV store; author reports 10-30% faster in-tmpfs CRUD than LMDB.

| | |
|---|---|
| **Beats** | LMDB |
| **Claimed result** | README: 'Up to 30% faster than LMDB in CRUD benchmarks'. In-tmpfs benchmarks that test the engine itself show libmdbx 10-20% faster than LMDB, and up to 30% faster when built with options that downgrade several runtime checks to match LMDB. The README says libmdbx may be slower than LMDB on Windows (LockFileEx locking). A separate comparison bullet asserts 'up to 10-100K times faster than both BoltDB and LMDB in particular extreme cases' (excluding disk I/O), with no data behind it. |
| **Workload** | In-tmpfs CRUD benchmarks (engine speed without disk I/O) run with the ioArena harness via 'make bench-quartet', which also covers RocksDB and WiredTiger. No dataset size, key/value sizes, hardware, or result tables are published. |
| **Metric** | throughput |
| **Adoption** | 1.4k+ stars; README claims use in hundreds of open source projects including Ethereum clients |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://sourcecraft.dev/dqdkfa/libmdbx) · [benchmark](https://github.com/Mithril-mine/libmdbx#improvements-beyond-lmdb) |

## Verdict

All numbers are first-party: the README says in-tmpfs CRUD runs of the ioArena harness show libmdbx 10-20% faster than LMDB, and up to 30% faster in builds that drop runtime checks. It publishes no result tables, hardware, compiler flags or LMDB version. The repo's make bench targets default to 25M operations in nosync mode with 4 reader threads for get/iterate, on upstream ioArena's defaults of 16-byte keys and 32-byte values. The '10-100K times faster' line names no cases; separately, the author claims mdbx_cache_get speeds up get by 'several tens of thousands of times'.

## Use it when

- Read-dominated embedded workloads that need ACID transactions, sorted keys and range scans, where readers must never block the single writer and read throughput should scale across cores.
- Several processes on one host sharing a single database file without running a database server.
- You already run LMDB and hit its limits: keys longer than 511 bytes (libmdbx allows 2022 bytes at 4 KiB pages, 32742 at 64 KiB), a data file that never shrinks, bloat from slow readers, or corruption after crashes in no-sync modes (MDBX_SAFE_NOSYNC keeps the DB consistent).
- Hot point lookups on keys that rarely change, where mdbx_cache_get can skip most of the B-tree descent.
- Bulk loading pre-sorted data with the append operation on Linux, the platform the author recommends for speed; Ethereum clients (Erigon, Reth, Silkworm) use it in production.

## Skip it when

- Write-heavy workloads with strict durability: only one write transaction runs at a time and the README says syncing shadow pages to disk can bottleneck write-intensive loads. The write-optimized LSM engines in this category are a better fit.
- Performance-sensitive Windows or macOS deployments: by default Windows uses LockFileEx and macOS/iOS use F_FULLFSYNC, and the README says both make libmdbx slower than LMDB. WSL1 is refused outright (ENOLCK) and shrinking the file on Windows is limited.
- Long-running read transactions (analytics scans, backups by iteration) alongside steady writes: pinned pages make the file grow and throughput drop unless you use transaction parking or the Handle-Slow-Readers callback.
- You need a current head-to-head against LMDB: the 10-30% figures are old first-party claims (an 'up to 20% faster' version was posted in 2019) and have not been republished against LMDB 1.0, which shipped in July 2026 with faster large-transaction commits.
- Processes that open untrusted or corrupted database files, or strict supply-chain policies: 2026 fuzzing found an out-of-bounds read in mdbx_env_chk (issue #375) and a null dereference on corrupted DBs (#297), both since fixed. The project is still 0.x and led by one author after corporate funding ended in 2025, and the README says the successor MithrilDB may be withheld from countries that sanction Russia.

## How it is fast

The core is LMDB's design: a copy-on-write (shadow-paging) B+tree in a memory-mapped file with MVCC snapshots, so reads are zero-copy pointer walks with no buffer pool and no WAL, and readers are wait-free without atomic operations. On top of that libmdbx adds LIFO reuse of freed pages (shorter page circulation, better write-back cache hit rates), 'refund' auto-compaction that truncates freed tail pages at commit, 'Big Foot' chunking of huge retired-page lists, bulk deletion by cutting whole B-tree branches, and mdbx_cache_get, which stores a key's version and mmap offset client-side and stops the B-tree descent at the first page that has not changed. The top '30% faster' figure needs builds that relax runtime checks (the MDBX_DISABLE_VALIDATION option, described as bringing corruption detection 'closer to the LMDB').

## Compared with alternatives

SplinterDB, NuDB, TerarkDB and Titan are all write-optimized engines benchmarked against RocksDB on insert and load throughput (for example SplinterDB reports 6-10x faster inserts and Titan about 70% faster loading). Pick libmdbx when the workload is read-dominated, needs ordered range scans with zero-copy reads and snapshot isolation, or has several processes sharing one file. Pick a sibling when ingest rate is the bottleneck.

## Integration

| | |
|---|---|
| **Form** | source-drop (amalgamated mdbx.c + mdbx.h, optional mdbx.c++ + mdbx.h++); CMake or GNU Make builds it as a static or shared lib |
| **Dependencies** | none beyond libc and pthreads (ntdll.lib on Windows); bash, GNU Make or CMake to build |
| **Minimum toolchain** | C99/C11 (CMake picks C23, C11 or C99; GNU Make uses -std=gnu11); C++ API needs C++11 and prefers C++17 to C++23. Tested since 2026 with GCC 11.3+, Clang 14+, MSVC 19.44+ (VS 2022), Elbrus LCC 1.28+; MinGW 10.2+ on Windows |
| **Platforms** | Linux, Windows (not WSL1), macOS, iOS, Android, FreeBSD, NetBSD, OpenBSD, DragonFly, Solaris/illumos, HarmonyOS and other POSIX.1-2008 systems; the file format depends on endianness only, not 32/64-bit; the header prints a warning when built for RISC-V |
| **Thread safety** | One environment can be shared by threads and processes. Writers are serialized by a single mutex (one write transaction at a time), and readers never block writers or each other. A transaction or cursor must never be used from two threads at once. Read transactions are tied to their OS thread unless MDBX_NOSTICKYTHREADS is set (meant for Go/Rust runtimes). A write transaction must commit or abort on the thread that began it. Do not reuse an env in a child after fork() (use mdbx_env_resurrect_after_fork) and do not open the same DB twice in one process. |
| **Drop-in for the baseline** | partial — the C API keeps LMDB's model and error-code range under mdbx_ names, but it is not ABI-compatible and no LMDB file-format compatibility is documented (an LMDB-to-MDBX migration guide is still on the TODO list). Some semantics differ: every cursor must be closed explicitly, ambiguous updates return MDBX_EMULTIVAL, and fsync/locking defaults differ on macOS and Windows. |

## Gotchas

- Values returned by get/cursor calls point into the map and stay valid only until the next update or the end of the transaction. Writing through them causes SIGSEGV, or silent DB corruption under MDBX_WRITEMAP or on dirty pages.
- mdbx_dbi_close is not synchronized with transactions running on other threads. Nested-transaction DDL had data-loss and assertion bugs fixed in mid-2026: a drop inside a child transaction that was then aborted emptied the table (#361), and rename caused a commit assertion (#360). Pin to the stable branch or a release.
- Sharing a DB across containers requires one kernel page cache, a shared PID namespace (e.g. --pid=host) and matching libmdbx/libc build options (compare the 'options:' line of mdbx_chk -V).
- Since December 2025 only amalgamated source ships and most tests are not included, so you cannot rerun the full test suite from a release tarball.

## Known shortcomings

- The measured claim is 'up to 30% faster than LMDB in CRUD benchmarks' (10-20% in tmpfs runs; up to 30% only with build options that relax runtime checks); the README's '10-100K x' line is an unmeasured assertion about extreme cases (verifier downgrade). Canonical origin moved to sourcecraft.dev; GitHub is a mirror.
- The 10-30% over LMDB is first-party only, with no tables, hardware, flags or LMDB version; the claim dates to 2019 and was never re-run against LMDB 1.0 (2026-07, faster large-transaction commits). The 30% needs MDBX_DISABLE_VALIDATION, which weakens corruption detection; bench defaults are nosync, 16 B keys, 32 B values. The '10-100K x' names no cases (the author ties it to mdbx_cache_get). Slower than LMDB by default on Windows (LockFileEx) and macOS (F_FULLFSYNC); WSL1 refused. 2026 bugs fixed: nested drop+abort data loss (#361), OOB read on malformed DB in mdbx_env_chk (#375), commit flush error reported as success. Still 0.x with one lead author; the successor MithrilDB may be withheld from sanctioning countries.

## Caveats and trade-offs

Self-reported percentages with no published result tables, hardware, or compiler/flags. The ioArena harness is public (sourcecraft.dev/dqdkfa/ioarena, originally github.com/pmwkaa/ioarena). The README says libmdbx may be slower than LMDB on Windows (LockFileEx) and slower on macOS with the default F_FULLFSYNC durability setting. The '10-100K times faster' line covers unspecified extreme cases and is not a measured figure. Canonical origin is SourceCraft; GitHub Mithril-mine/libmdbx is a mirror.

Slower than LMDB on Windows due to native file locking; larger feature surface than LMDB increases complexity; the canonical project has moved off GitHub and this is now a mirror/transfer

## Maintenance

Actively maintained: stable v0.14.4 shipped 2026-09-19, master is v0.15 development, and the last commit was 2026-09-25. It is Apache-2.0 amalgamated C and easy to vendor, but still pre-1.0, driven by one lead author, and developed on SourceCraft with GitHub (Mithril-mine) only as a mirror.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README claim with no published result tables, hardware, or compiler/flags. The 'Improvements beyond LMDB' section says in-tmpfs CRUD benchmarks show libmdbx 10-20% faster than LMDB, and up to 30% faster with build options that relax runtime checks, reproducible with ioArena 'make bench-quartet'. The '10-100K times' line is an unmeasured assertion about 'particular extreme cases'.
- **Verifier notes:** The measured claim is 10-30% faster than LMDB, not 10-100K x. That line is on the page but is a qualitative extreme-case assertion, so claimed_speedup is rewritten around the CRUD figure. Correct repo_url: the README and libmdbx.dqdkfa.ru name https://sourcecraft.dev/dqdkfa/libmdbx as the origin and https://github.com/Mithril-mine/libmdbx as a mirror (the old github.com/erthink/libmdbx now redirects to Mithril-mine). License Apache-2.0, 1468 stars, last commit 2026-09-25, all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `benchmark_url`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Mithril-mine/libmdbx>
  - <https://github.com/Mithril-mine/libmdbx#comparison-with-other-databases>
  - <https://github.com/erthink/libmdbx>
  - <https://sourcecraft.dev/dqdkfa/libmdbx>
  - <https://sourcecraft.dev/dqdkfa/ioarena>
  - <https://libmdbx.dqdkfa.ru>
  - <https://github.com/pmwkaa/ioarena>
- **Sources the enricher read:**
  - <https://github.com/Mithril-mine/libmdbx>
  - <https://github.com/Mithril-mine/libmdbx#improvements-beyond-lmdb>
  - <https://github.com/Mithril-mine/libmdbx/releases>
  - <https://github.com/Mithril-mine/libmdbx/issues>
  - <https://github.com/Mithril-mine/libmdbx/issues/360>
  - <https://github.com/Mithril-mine/libmdbx/issues/361>
  - <https://github.com/Mithril-mine/libmdbx/issues/375>
  - <https://github.com/Mithril-mine/libmdbx/discussions/314>
  - <https://raw.githubusercontent.com/Mithril-mine/libmdbx/master/mdbx.h>
  - <https://raw.githubusercontent.com/Mithril-mine/libmdbx/master/mdbx.h++>
  - <https://raw.githubusercontent.com/Mithril-mine/libmdbx/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Mithril-mine/libmdbx/master/GNUmakefile>
  - <https://raw.githubusercontent.com/Mithril-mine/libmdbx/master/ChangeLog.md>
  - <https://raw.githubusercontent.com/Mithril-mine/libmdbx/master/TODO.md>
  - <https://raw.githubusercontent.com/Mithril-mine/libmdbx/master/SECURITY.md>
  - <https://raw.githubusercontent.com/Mithril-mine/libmdbx/master/VERSION.json>
  - <https://sourcecraft.dev/dqdkfa/libmdbx>
  - <https://libmdbx.dqdkfa.ru/intro.html>
  - <https://github.com/pmwkaa/ioarena/blob/master/src/ia_config.c>
  - <https://hn.algolia.com/api/v1/search?query=libmdbx>
  - <https://news.ycombinator.com/item?id=48766598>
  - <https://news.ycombinator.com/item?id=30154655>
  - <https://github.com/erigontech/erigon/wiki/Criteria-for-transitioning-from-LMDB-to-MDBX>
  - <https://export.arxiv.org/api/query?search_query=abs:libmdbx>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/mithril-mine/libmdbx`) · [data/wave6/enrich/raw/github_com_mithril_mine_libmdbx.json](../../../data/wave6/enrich/raw/github_com_mithril_mine_libmdbx.json) (enrichment confidence 0.7)

</details>
