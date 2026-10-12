# Sophia

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🔴 abandoned

> Abandoned C MVCC key-value engine (append-only, RAM-disk hybrid); self-reported 2.6x LevelDB random reads in 2013, never reproduced.

| | |
|---|---|
| **Beats** | LevelDB 1.17 (HyperLevelDB also in the gist) |
| **Claimed result** | Write: Sophia 1.1 fillrandom 74,143 vs LevelDB 1.17 48,930 ops/s (1.5x, derived from page data; HyperLevelDB 113,355), 4000-byte values 7,368 vs 3,187 (2.3x) in Howard Chu's 2015 gist. Read: first-party 438,084 vs 167,476 random reads/s (2.6x) never independently reproduced; the gist crashed before readrandom. |
| **Workload** | Random reads on the Sophia author's SSD-based machine, per the sphia.org benchmark page as quoted in a September 2013 bitcoin-development mailing list post; Sophia v1.x era. |
| **Metric** | throughput |
| **Hardware** | SSD-based machine, CPU not stated |
| **Adoption** | 1.9k stars; storage engines of Amelia and Monotone are 'heavily inspired' by it (per README) |
| **Last commit** | 2026-03-03 |
| **Links** | [repository](https://github.com/pmwkaa/sophia) |

## Verdict

The read claim rests on 2013 sphia.org figures relayed in a bitcoin-development mailing-list post (438,084 vs 167,476 random reads/sec against LevelDB on an unnamed SSD machine, 2.6x derived, seen as search snippets only, not reproduced by the poster, with a smaller gap to HyperLevelDB); no code, flags, CPU or versions are known. The only independent numbers found are Howard Chu's 2015 db_bench gist (hyc/87929fa3f95404512b4d: Samsung 830 SSD, 8 GB RAM, 160M records with 16-byte keys and 100-byte values, CPU and compiler not stated), where Sophia 1.1 fillrandom ran at 74,143 ops/sec versus LevelDB 1.17 at 48,930 (1.5x, derived) and HyperLevelDB 1.14 at 113,355, but Sophia crashed before any random-read test; with 4,000-byte values it filled at 7,368 versus 3,187 (2.3x, derived) and 24,836 for HyperLevelDB, and crashed again.

## Use it when

- Studying or porting a storage-engine design: the README and architecture docs explain the region/branch/node layout, and the author's later engines (Amelia, Monotone) build on it.
- Maintaining an existing application already on Sophia 2.2 whose storage format and workload are known to work.
- Single-process programs that want cross-database SSI transactions and upsert from one dependency-free C file, and that can size db.compaction.cache from the memory-requirements tables.
- Read-mostly workloads with small keys and values on SSD, the email-index case the author said the original homepage benchmark modelled.

## Skip it when

- Any new production system: the README says the project is no longer developed, the last code commit is 2019-01-25 (later commits edit the README), there are no tagged releases (issue #160 'Tag a New Release' is open) and 53 issues are open.
- Write-heavy multi-threaded workloads: in issue #137 (2016) the maintainer said Sophia does not benefit from multithreaded access, and in an independent 2015 run HyperLevelDB 1.14 filled random keys about 1.5x faster than Sophia 1.1.
- Large datasets with tight RAM: the documented cache requirement grows with write rate and capacity (for example 20,686 MB of cache for 1 MB/s of writes into 1000 GB on a 100 MB/s disk), and reopening a big database replays all logs (issue #137 reports a re-run stuck for over an hour).
- Workloads that need proven crash safety: open issues include #171 (segfault with more than 6 key/value components), #54 (crash with multiple threads), #53 (crash in cursor iterator), #50 (deadlock when opening two cursors), #142 (broken backups) and #47/#48 (memory leaks).
- Windows (open issue #96 asks for a Windows makefile; the makefile only handles Linux and Darwin).

## How it is fast

In the v1.2/2.x design each Node is one file of Branches; a Branch is a set of sorted, non-overlapping Regions with an in-memory region index, and each Node also keeps two in-memory key indexes that act like an LSM memtable. Writes are a WAL append plus an in-memory insert; a Branch operation later writes the sorted regions sequentially to the end of the node file, and a multi-threaded scheduler compacts a node's branches. A point read touches only one node and only the regions whose min/max range covers the key (amortized O(max_branch_count_per_node) disk reads), and pread or mmap access lets recently written branches be served from the page cache.

## Compared with alternatives

Against the catalogued LevelDB, HyperLevelDB and LMDB entries, pick Sophia only when you need multi-database SSI transactions and upsert in one small C file and can maintain it yourself; LMDB is maintained and read-optimized, and HyperLevelDB beat Sophia 1.1 on random fills in the only independent run found.

## Integration

| | |
|---|---|
| **Form** | source-drop (amalgamated sophia.c and sophia.h generated by make) or static/shared lib |
| **Dependencies** | none per README and build docs; lz4 and zstd compression are built in, and open issues #153 and #179 say the bundled third-party code is old |
| **Minimum toolchain** | C99 compiler with pthreads (documented build line: cc -O2 -DNDEBUG -std=c99 -pedantic -Wall -Wextra -pthread -c sophia.c) |
| **Platforms** | Linux and macOS per the makefile; other POSIX not documented; Windows unsupported; armv6l asked about in open issue #172 |
| **Thread safety** | Docs state all methods are thread-safe and atomic, with optimistic N-writer/M-reader concurrency, but the maintainer said in 2016 that it gains nothing from multiple threads, and a multi-thread crash report (#54) is still open. |
| **Drop-in for the baseline** | no |

## Gotchas

- The default makefile always compiles with -DSS_INJECTION_ENABLE -g at -O2 and without -DNDEBUG, so fault-injection hooks ship in libsophia; build sophia.c yourself with the documented -O2 -DNDEBUG line for production.
- The README headline 'O(1) worst case for read, write and range scan' describes the v1.1 design; the v1.2 docs give get as amortized O(max_branch_count_per_node) and full range traversal as O(total_region_count).
- Multi-statement transactions can end in a 'lock' status (2) or a rollback (1); deadlocks are not resolved automatically (check the transaction's 'deadlock' field and destroy one side), and errors inside a transaction do not roll it back.
- In the independent 2015 db_bench run, Sophia 1.1's fillrandsync row was 8.519 us/op against LevelDB 1.17's 6,370.717 us/op on the same SSD, far below a device flush latency, so Sophia's sync row probably did not fsync each write (log.sync is an option in 2.x); its random-fill database took about 26.2 GB on disk for 16 GB of data versus about 14.3 GB for LevelDB, and Sophia crashed before the read tests in both runs.

## Known shortcomings

- Downgraded C to D: no reachable benchmark (sphia.org dead, the 2013 bitcoin-dev post blocked at lists.linuxfoundation.org and mirror.b10c.me), so the 438,084 vs LevelDB 167,476 random reads/s figure is snippet only; the project is no longer developed (last code commit 2019-01-25). BSD-2-Clause.
- Enricher found an independent 2015 run (Howard Chu gist hyc/87929fa3f95404512b4d: Samsung 830 SSD, 8 GB RAM, 160M x 16B/100B keys, CPU and compiler unstated): Sophia 1.1 fillrandom 74,143 vs LevelDB 1.17 48,930 ops/s (1.5x derived), HyperLevelDB 113,355; 4000-byte values 7,368 vs 3,187 (2.3x); Sophia crashed before readrandom in both runs, so the 2.6x read claim stays unmeasured; the fillrandsync row (8.519 us/op vs LevelDB 6,370.717) implies no per-write fsync; disk 26.2 GB vs 14.3 GB for 16 GB of data. Default makefile builds -DSS_INJECTION_ENABLE -g without NDEBUG; maintainer says no multithread benefit (#137); open crashes #171, #54, #53, broken backups #142, no tagged release.

## Caveats and trade-offs

Snippet only: the 438,084 vs 167,476 random reads/sec figures (2.6x, derived) come from WebSearch summaries of a September 2013 bitcoin-development mailing-list post that cites sphia.org/benchmarks.html and says the poster had not tried to replicate the numbers; the same post says the gap to HyperLevelDB is much smaller and HyperLevelDB writes faster. sphia.org, sophia.systems and the mailing-list mirrors are unreachable from this session (lists.linuxfoundation.org getaddrinfo ENOTFOUND, mirror.b10c.me proxy 403), no GitHub copy of the old site exists under pmwkaa, and the author's ioarena benchmark tool (github.com/pmwkaa/ioarena) supports Sophia but publishes no results. Benchmark code, compiler, flags, CPU, key and value sizes and LevelDB version unknown; numbers predate Sophia 1.2 and the 2.x line. The repo README and docs index (SUMMARY.md) contain no benchmark results, only Big-O claims. Last code commit is 2019-01-25; the 2025-02-13 and 2026-03-03 commits are README edits, and the README says the project is no longer developed, so maintenance is recorded as abandoned. Licence is BSD-2-Clause (LICENSE file). No SQLite, LMDB or RocksDB comparison found. [retier] Sync row likely no per-write fsync; 26.2 GB on disk vs 14.3 GB for 16 GB of data; default makefile builds with -DSS_INJECTION_ENABLE -g and no NDEBUG; open crash issues #171, #54, #53; no tagged release.

MVCC, append-only, ACID, RAM-disk hybrid engine in plain C with zero dependencies, amalgamated source; O(1) worst-case read, write and range scan is the stated design target. Key-value plus row/document API, not SQL. Author states the project is no longer developed.

## Maintenance

Abandoned: the author says it is no longer developed, the last code commit is 2019-01-25 and no release was ever tagged; it is BSD-2-Clause and one amalgamated C file, so it is easy to vendor for study or legacy use but not a sound choice for new production storage.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** No reachable numbers page: benchmark_url is null, sphia.org/benchmarks.html and the 2013 bitcoin-dev post (lists.linuxfoundation.org ENOTFOUND, mirror.b10c.me proxy 403) cannot be opened, and the repo README, documentation/SUMMARY.md and the author's ioarena tool carry no results, so per the null-benchmark_url rule the entry cannot stay above D.
- **Retiered** D to C: Raised D to C: an independent 2015 run (Howard Chu gist) measures Sophia 1.1 fillrandom at 1.5x LevelDB 1.17 (2.3x at 4000-byte values), but the run crashed before readrandom in both attempts, its sync row shows no per-write fsync, CPU and compiler are unstated and the build is a decade old, so it does not reach B; the original 2.6x read claim remains first-party and unmeasured.
- **Verifier notes:** Real, notable (1.9k stars) storage engine, but the only numbers are a 2013 third-hand quote of a dead project page seen through WebSearch snippets, so tier D (downgrade from C). Shortcomings to record: no reachable benchmark, numbers unreproduced by the poster, smaller gap to HyperLevelDB, project no longer developed (last code commit 2019-01-25).
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`, `baseline`
- **Shortcomings recorded by:** verifier batch-89 (wave 6); enricher w6 pair-014
- **Pages the verifier opened:**
  - <https://github.com/pmwkaa/sophia>
  - <https://github.com/pmwkaa/sophia/commits/master>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/SUMMARY.md>
  - <https://github.com/pmwkaa?tab=repositories&q=sophia>
  - <https://github.com/pmwkaa/ioarena>
- **Sources the enricher read:**
  - <https://github.com/pmwkaa/sophia>
  - <https://github.com/pmwkaa/sophia/issues>
  - <https://github.com/pmwkaa/sophia/issues?page=2&q=is%3Aissue+is%3Aopen>
  - <https://github.com/pmwkaa/sophia/issues/137>
  - <https://github.com/pmwkaa/sophia/issues/84>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/README.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/makefile>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/SUMMARY.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/tutorial/build.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/tutorial/api.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/tutorial/workflow.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/admin/memory_requirements.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/admin/version.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/admin/mmap.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/admin/compression.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/admin/compaction.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/crud/transactions.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/crud/deadlocks.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/conf/db_performance.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/conf/sophia.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/conf/db.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/conf/log.md>
  - <https://raw.githubusercontent.com/pmwkaa/sophia/HEAD/documentation/conf/scheduler.md>
  - <https://gist.github.com/hyc?page=3>
  - <https://gist.github.com/hyc/87929fa3f95404512b4d>
  - <https://github.com/pmwkaa/monotone>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/pmwkaa/sophia`) · [data/wave6/enrich/raw/github_com_pmwkaa_sophia.json](../../../data/wave6/enrich/raw/github_com_pmwkaa_sophia.json) (enrichment confidence 0.55)

</details>
