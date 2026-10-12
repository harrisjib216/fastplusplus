# UnQLite

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> Single-file embedded C key/value and JSON document store (linear hashing); faster than SQLite only for point lookups in one informal Python test.

| | |
|---|---|
| **Beats** | SQLite (Python sqlite3 module, one INSERT then commit per key; one SELECT per key) |
| **Claimed result** | Write 1.4x and read figures from the gist both measure UnQLite on uncommitted in-memory pages (auto-commit at unqlite_close, unlimited pager cache) against SQLite with fsync per INSERT; neither is like-for-like. LevelDB, Kyoto Cabinet and GDBM are 2.8-8x faster in the same gist. |
| **Workload** | Store 100,000 small key/value pairs (key str(i), value i) and then read all of them back, through the Python unqlite and sqlite3 bindings, one database file under /tmp, each test run once. |
| **Metric** | throughput |
| **Adoption** | 2.3k stars, 181 forks |
| **Last commit** | 2026-09-05 |
| **Links** | [repository](https://github.com/symisc/unqlite) · [benchmark](https://gist.github.com/coleifer/3057f97a7628d44c2e59) |

## Verdict

A single-run Python 2 script by the unqlite-python author stored and then read 100,000 small string pairs: UnQLite 1.05 s writes / 1.35 s reads vs Python sqlite3 6.98 s / 1.89 s, with no hardware, OS, library versions or compiler stated. SQLite committed every row inside the timer while UnQLite's writes and reads ran in one uncommitted in-memory transaction committed at close, so the numbers compare an in-memory hash table against per-row durable SQL transactions, not two equally durable stores.

## Use it when

- Embedded C or C++ application that needs single-key get/put on an ACID single-file store and does not need SQL or range scans.
- You want a JSON-ish document store inside the process (Jx9 collections) without running a server.
- Bulk loads that can sit in one transaction and fit in RAM, committed once at the end (the default auto-commit-on-close pattern).
- Builds where one portable C99 amalgamation compiled with your app (no external dependency) beats linking a larger engine.

## Skip it when

- Raw key/value speed matters: in the same informal Python test LevelDB (0.38 s / 0.31 s), Kyoto Cabinet (0.25-0.28 s) and GDBM (0.29 s / 0.17 s) were about 2.8-8x faster than UnQLite (1.05 s / 1.35 s) for 100,000 writes and reads.
- You need ordered iteration or range queries: the default engine is a hash table; the b+tree engine named in the code as a fallback is not registered in the amalgamation.
- Several processes share one database file: open issue #168 (Apr 2024, no maintainer reply) reports a segfault and an endless UNQLITE_BUSY loop when two processes use the same file on macOS/iOS; #137 was an earlier multiprocess corruption bug.
- You run untrusted Jx9 scripts or document-store input: 2025-2026 issues #172, #173 and #176 were memory-safety bugs (global-buffer-overflow and heap overflow) in the Jx9 engine; one fix was merged, reverted and redone in Apr-Sep 2026.
- Large write transactions on memory-constrained systems: the default unlimited page cache keeps every dirty page in RAM until commit unless UNQLITE_CONFIG_MAX_PAGE_CACHE is set.

## How it is fast

The default on-disk engine is Litwin's linear hashing (lhash_kv.c, extended with what the authors call a Virtual Bucket Table), giving O(1) average point lookups with no SQL parse/plan step. Pages go through a SQLite-derived pager with a rollback journal ('_unqlite_journal' file); by default the page cache is unlimited (nCacheMax = SXU32_HIGH), so a write transaction accumulates dirty pages in memory until commit, and with the default auto-commit that commit happens only at unqlite_close(). In-memory databases use a separate in-memory hash engine ('mem').

## Compared with alternatives

Choose UnQLite over LMDB or LevelDB only when you want a single C amalgamation that also gives you a schemaless JSON document store and SQLite-like single-file deployment; for pure key/value throughput or ordered scans, LMDB (mmap B+tree) and LevelDB (LSM, 3-4x faster than UnQLite in the same Python test) are the better picks, and CalicoDB is the closer 'beats SQLite' sibling with C-level numbers.

## Integration

| | |
|---|---|
| **Form** | source-drop (amalgamation unqlite.c + unqlite.h); optional CMake &gt;=3.10 static lib |
| **Dependencies** | none (pthreads on UNIX when built with UNQLITE_ENABLE_THREADS) |
| **Minimum toolchain** | C99 (README builds with cc -O2 -std=c99 or MSVC /TC) |
| **Platforms** | Windows and UNIX VFS built in; other platforms must register their own VFS and mutex subsystem |
| **Thread safety** | Not thread-safe by default: all mutex code is compiled out unless UNQLITE_ENABLE_THREADS is defined; with it, handles may be shared across threads (UNQLITE_LIB_CONFIG_THREAD_LEVEL_MULTI). Multiprocess sharing relies on file locks and has open crash reports. |
| **Drop-in for the baseline** | no |

## Gotchas

- Writes are only durable at commit; with the default settings that is unqlite_close(). Crash before close and the whole session's writes roll back; call unqlite_commit() explicitly for durability points, and note UNQLITE_CONFIG_DISABLE_AUTO_COMMIT turns off the close-time commit.
- Harness flaw behind the benchmark: the gist never commits UnQLite inside either timed loop, the pager cache is unlimited, and auto-commit happens at close after both timers stop, so UnQLite's 100,000 writes are in-memory linear-hash inserts and its 100,000 reads are served from the same uncommitted dirty pages, while SQLite journals and fsyncs one transaction per INSERT and answers each read with a SQL SELECT against the committed file. Neither the 6.6x write ratio nor the 1.4x read ratio is like-for-like.
- UNQLITE_OPEN_MMAP is silently dropped unless the database is opened read-only (unqlite.c clears it for CREATE and READWRITE opens).
- The current unqlite-python binding's fetch() calls unqlite_kv_fetch twice per key (size probe, then copy), so Python-level read timings carry extra lookup and binding cost that a C caller would not pay.

## Known shortcomings

- Claim downgraded (tier C): the coleifer gist's 6.6x write figure is unfair because SQLite commits every row inside the timed loop while UnQLite never commits there (auto-commit on close runs after timing; checked in unqlite.c); the fair figure is reads only, 1.4x. Single run, no hardware or versions; the gist author also maintains unqlite-python; LevelDB, Kyoto Cabinet and GDBM are faster in the same table. BSD-2-Clause, active.
- Enricher: the gist's read figure is not fair either: the pager cache is unlimited by default (nCacheMax = SXU32_HIGH) and auto-commit happens only at unqlite_close() after both timers stop, so UnQLite writes are in-memory linear-hash inserts and reads come from the same uncommitted dirty pages, while SQLite pays fsync per INSERT plus a SQL SELECT on a committed file. LevelDB, Kyoto Cabinet and GDBM are 2.8-8x faster in the same gist. Hash engine only (no ordered scans, btree fallback not registered); open multiprocess segfault issue #168; Jx9 memory-safety bugs #172, #173, #176 (2025-2026); not thread-safe without UNQLITE_ENABLE_THREADS; unqlite-python fetch() calls unqlite_kv_fetch twice per key.

## Caveats and trade-offs

Informal evidence: a one-file Python 2 script (gist by coleifer, who also maintains the unqlite-python binding; gist last active 2 Sep 2020, creation date not shown) run once per engine with no stated hardware, OS, library versions, compiler or flags. Write timings are not comparable: the SQLite test calls commit() after every INSERT inside the timed loop (one durable transaction per row, no WAL or PRAGMA tuning), while the UnQLite test only assigns db[i] = i and never commits; UnQLite's default is auto-commit on close (unqlite.c: UNQLITE_FL_DISABLE_AUTO_COMMIT 'Disable auto-commit on close'; unqliteDbRelease commits the outstanding transaction), and the script closes the database after both timings, so UnQLite's commit and fsync cost is excluded. The 1.4x read gap is the only fair figure, and it includes Python binding overhead (SQLite reads also run a SQL SELECT plus fetchall per key). The script's RocksDB read method has no return statement (the page does not comment on this). unqlite.org and unqlite.symisc.net did not resolve from this environment; the repo README carries no benchmarks. The two UnQLite seed lines are the same project, filed as one record. [retier] Hash engine only, no ordered scans; not thread-safe without UNQLITE_ENABLE_THREADS; open multiprocess segfault issue #168; Jx9 memory-safety bugs #172, #173, #176.

Single-file ACID store with a raw key/value layer plus a Jx9 scripting document store; amalgamation unqlite.c plus unqlite.h. No SQL, no secondary indexes. Pure key/value lookups only, which is the only workload the cited test touches.

## Maintenance

Active (last commit 2026-09-05, release 1.2.1 on 2026-04-30, 168 commits, 2.3k stars), BSD-2-Clause and trivially vendored as two files, but maintenance is mostly security fixes in Jx9 and the multiprocess crash #168 is unanswered.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** The gist run_bench.py (coleifer, the author of the unqlite-python binding) times UnQLite against Python sqlite3 and prints 1.054 s / 1.353 s for UnQLite and 6.977 s / 1.890 s for SQLite at N = 100,000, but states no hardware, library versions, compiler or flags and runs each test once, so it is informal evidence below A and not a recognised suite (not B). Tier stays C; the verdict is downgrade because the 6.6x write ratio is not a like-for-like measurement.
- **Verifier notes:** Numbers on the gist match the record. Shortcomings to record: write ratio excludes UnQLite's commit (auto-commit on close happens outside the timed region) while SQLite fsyncs per row; read win only 1.4x; single run, no hardware/versions; benchmark author maintains the UnQLite Python binding; several other stores (LevelDB, Kyoto, GDBM) beat UnQLite in the same table. Metadata checked: BSD-2-Clause, 2.3k stars, 181 forks, last commit 2026-09-05 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-90 (wave 6); enricher w6 pair-018
- **Pages the verifier opened:**
  - <https://gist.github.com/coleifer/3057f97a7628d44c2e59>
  - <https://github.com/symisc/unqlite>
  - <https://github.com/symisc/unqlite/commits>
  - <https://raw.githubusercontent.com/symisc/unqlite/HEAD/unqlite.c>
  - <https://github.com/coleifer/unqlite-python>
- **Sources the enricher read:**
  - <https://github.com/symisc/unqlite>
  - <https://github.com/symisc/unqlite/commits>
  - <https://github.com/symisc/unqlite/issues?q=is%3Aissue>
  - <https://github.com/symisc/unqlite/issues/168>
  - <https://raw.githubusercontent.com/symisc/unqlite/HEAD/README.md>
  - <https://raw.githubusercontent.com/symisc/unqlite/HEAD/unqlite.h>
  - <https://raw.githubusercontent.com/symisc/unqlite/HEAD/unqlite.c>
  - <https://raw.githubusercontent.com/symisc/unqlite/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/symisc/unqlite/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/symisc/unqlite/HEAD/CHANGELOG.md>
  - <https://gist.github.com/coleifer/3057f97a7628d44c2e59>
  - <https://raw.githubusercontent.com/coleifer/unqlite-python/HEAD/unqlite.pyx>
  - <https://raw.githubusercontent.com/coleifer/unqlite-python/HEAD/README.md>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/symisc/unqlite`) · [data/wave6/enrich/raw/github_com_symisc_unqlite.json](../../../data/wave6/enrich/raw/github_com_symisc_unqlite.json) (enrichment confidence 0.7)

</details>
