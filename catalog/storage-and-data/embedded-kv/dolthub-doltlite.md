# DoltLite

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> SQLite fork with a prolly-tree storage engine that adds Git-style branch, merge and diff; 1.1-2.9x slower than SQLite, not faster.

| | |
|---|---|
| **Beats** | SQLite (stock SQLite built from the reference amalgamation by test/build_stock_reference.sh) |
| **Claimed result** | No overall speedup claimed; the report is a regression gate with slowdown ceilings and DoltLite is slower on every aggregate (time, SQLite then DoltLite): in-memory reads 9.57s vs 11.12s (1.2x), in-memory writes 1.94s vs 3.03s (1.6x), file-backed reads 10.16s vs 11.24s (1.1x), file-backed writes 3.66s vs 4.03s (1.1x), autocommit writes 816.91ms vs 2.35s (2.9x). Individual integer-key file-backed rows where DoltLite is faster: oltp_point_select 64.75ms vs 30.79ms (0.5x time), select_random_ranges 7.90ms vs 4.29ms (0.5x), oltp_read_only 126.32ms vs 81.03ms (0.6x), oltp_write_only 80.38ms vs 59.68ms (0.7x). These read wins exist only against SQLite in its default rollback-journal mode: the ac_reads section runs the same SQL files with SQLite in WAL mode and the same rows become ties or losses (oltp_point_select 30.19ms vs 30.89ms, select_random_ranges 4.27ms vs 4.29ms, oltp_read_only 77.16ms vs 80.98ms). |
| **Workload** | Sysbench-style SQL workloads (oltp_point_select, range selects, updates, inserts, joins; 100,000-row fixtures, integer, text, blob and composite primary keys), in-memory and file-backed, run through the same C timer harness against both engines on a GitHub-hosted runner, paired alternating runs, medians. |
| **Metric** | latency |
| **Hardware** | GitHub-hosted runner (runs-on ubuntu-latest, image ubuntu24 20260927.320.1); CPU model not stated. |
| **Compiler and flags** | cc -O2 -Werror for the sysbench_timer.c harness, linked to libdoltlite.a or the stock-reference sqlite3.o (compiler version not stated in the nightly workflow); DoltLite library built with ./configure && make (flags not read). |
| **Adoption** | 302 stars |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/dolthub/doltlite) · [benchmark](https://raw.githubusercontent.com/dolthub/doltlite/HEAD/performance-report.md) |

## Verdict

The project's nightly report (2026-10-06, commit 3e4ff81, GitHub-hosted ubuntu24 runner, cc -O2 harness, 100,000-row sysbench-style fixtures, medians of 55 paired alternating runs) shows DoltLite slower than a stock SQLite reference built from the same tree on every aggregate: 1.2x in-memory reads, 1.6x in-memory writes, 1.1x file-backed reads and writes and 2.9x durable autocommit writes; the handful of file-backed rows where DoltLite is faster exist only against rollback-journal SQLite and vanish against SQLite in WAL mode.

## Use it when

- You want an embedded SQL database with branches, commits, three-way merge, row-level diff and history queries (dolt_diff_&lt;table&gt;, dolt_history_&lt;table&gt;, dolt_blame_&lt;table&gt;) for local-first or agent workflows, and can accept SQLite-class but slower throughput.
- Syncing a database between devices or with Dolt-style remotes (push, pull, clone, lazy clones) where shipping only changed chunks matters more than raw query latency.
- Workloads that batch writes into explicit transactions and keep the working set inside the cache budget: there the report shows 1.0-1.3x SQLite for file-backed reads and writes.
- Applications already written against the sqlite3_\* API or a SQLite binding (Python, Go, Rust, Node, .NET, Swift, Android and WASM packages exist) that need versioning without moving to a server database.

## Skip it when

- When you want something faster than SQLite: every aggregate in the nightly report is slower (in-memory reads 1.2x, in-memory writes 1.6x, file-backed reads and writes 1.1x, durable autocommit writes 2.9x), and the release notes for v0.50.11-v0.50.15 show the same 1.0-3.7x range.
- Commit-heavy OLTP with one statement per transaction: autocommit writes run 2.5-3.2x slower than SQLite in WAL mode with synchronous=FULL, and the nightly gate tolerates up to 5.5x.
- Working sets larger than the chunk cache: the pragma docs say chunks are re-read and BLAKE3-verified on every pass once the budget is exceeded, and the 100,000-row nightly fixtures never exercise that regime.
- Software that relies on SQLite file-format or pager semantics: no rollback journal or WAL files, journal_mode/page_size/mmap_size pragmas are inert, multi-database atomic commits are refused, non-integer primary keys become clustered NOT NULL keys, and the file cannot be read by stock SQLite.
- Production systems that cannot tolerate beta-quality merge logic: the project is labelled Beta and on 2026-10-06 alone filed P1 issues such as a merge committing duplicate keys (#3695) and conflict resolution leaving a row an index lookup cannot find (#3691).

## How it is fast

It is not a speed play: the prolly tree (content-addressed immutable nodes with rolling-hash chunk boundaries, as in Dolt) exists to make diff, merge and structural sharing across history cheap, and it costs time on ordinary SQL. What keeps the gap to SQLite at 1.1-1.6x for wrapped workloads is a 64 MiB chunk/node cache (cache_size), an append-only chunk WAL with periodic checkpoints instead of a page journal, and the unchanged SQLite front end; every chunk read from the file is verified against its BLAKE3 address. Durable per-statement commits remain about 3x SQLite's WAL path.

## Compared with alternatives

Pick it over the SQLite-beating siblings (CalicoDB, mpedb, ForestDB, BTreePlus) only when you need versioned SQL with branch/merge/diff semantics, since they are faster key-value or B-tree engines without history; for raw embedded speed LMDB or stock SQLite remain the better choice.

## Integration

| | |
|---|---|
| **Form** | static lib (libdoltlite.a) or shared lib (libdoltlite.so/.dylib), plus CLI and language bindings |
| **Dependencies** | zlib, pthreads, libm (link -lpthread -lz -lm); Tcl for building from source on MSYS2; vec1 vector extension built in by default |
| **Minimum toolchain** | C compiler with autoconf-style ./configure && make (SQLite 3.54.0 code base); compiler version requirements not documented |
| **Platforms** | Linux x86_64 and arm64, macOS Apple Silicon (prebuilt), Windows via MSYS2/MinGW64 and prebuilt x64 tools, WebAssembly (ext/wasm) |
| **Thread safety** | SQLite threading modes apply; across connections and processes one durable writer at a time via a graph-lock sidecar (concurrent writers get SQLITE_BUSY), readers stay live during writes and GC |
| **Drop-in for the baseline** | partial — same sqlite3_\* API, symbol names and SQL semantics, and stock SQLite files still open on the original B-tree engine, but DoltLite-format files are a different on-disk format and storage-coupled pragmas and behaviours differ |

## Gotchas

- The per-row 'wins' in the report are harness artifacts: in file_reads and file_writes stock SQLite runs in default rollback-journal mode (only PRAGMA cache_size=16384 is added) and every read statement is its own transaction; with the same SQL in WAL mode (ac_reads) SQLite's oltp_point_select drops from 64.75 ms to 30.19 ms and DoltLite ties or loses on every row, about 3.5 us of rollback-mode overhead per statement (derived from page data). The 0.7-0.9x file_writes rows are also against the rollback journal, and no WAL-mode wrapped-write run exists to check them.
- The timer (test/sysbench_timer.c) runs each workload as one sqlite3_exec script, so every statement is parsed and prepared afresh in both engines; that shared front-end cost sits in both sides of each ratio, so the storage-layer slowdown is larger than the 1.1-1.6x headline ratios suggest.
- The 'stock SQLite' baseline is the fork's own SQLite 3.54.0 tree built with DOLTLITE_PROLLY=0 on a shared ubuntu-latest runner with configure-default flags and no CPU model; test/build_stock_reference.sh records that CI once shipped a reference that silently used DoltLite storage and passed by construction, so older reports and blog numbers may be invalid.
- Open time grows with the chunk WAL since the last checkpoint (thresholds DOLTLITE_WAL_CHECKPOINT_THRESHOLD and DOLTLITE_WAL_CHECKPOINT_CHUNKS), space is reclaimed only by dolt_gc/VACUUM, and PRAGMA page_size echoes whatever you set even though no pages exist.

## Known shortcomings

- Claim overstated (verifier downgrade, tier stays C): slower than stock SQLite on every aggregate (1.1x-2.9x); the file-backed wins hold only against default rollback-journal SQLite, and the same SQL in the report's ac_reads section against SQLite WAL gives a tie or loss (point_select 30.19 vs 30.89 ms). Shared CI runner with no CPU model; an old CI stock reference once shared DoltLite storage (fixed). Licence Apache-2.0 plus public-domain SQLite parts.
- Enricher: the file_reads and file_writes 'wins' hold only against rollback-journal SQLite, about 3.5 us per statement of overhead (derived from page data), with no WAL-mode run for batched BEGIN/COMMIT writes; sysbench_timer.c re-parses every statement through sqlite3_exec in both engines, so the headline ratios understate the storage-layer slowdown; 100k-row fixtures fit the 64 MiB cache, so the BLAKE3 re-verify cost beyond cache was never measured; the 'stock' baseline is the fork's own SQLite 3.54.0 tree built with DOLTLITE_PROLLY=0, and CI once shipped a reference that used DoltLite storage and passed by construction. Beta with P1 merge bugs filed 2026-10-06 (#3695 duplicate keys, #3691, #3688); not the SQLite file format; journal_mode, page_size and mmap_size pragmas are inert.

## Caveats and trade-offs

Not a speed claim: the project's own docs (doc/doltlite/performance.md) say the stock comparison tracks 'the remaining SQL performance gap', and the nightly gate allows DoltLite to be up to 2.3x slower per workload (5.5x for autocommit writes). The file-backed rows where DoltLite wins are an artifact of the baseline configuration: in file_reads/file_writes stock SQLite runs with only PRAGMA cache_size=16384 in its default rollback-journal mode, and every read workload issues thousands of standalone SELECTs (10,000 for oltp_point_select), each its own read transaction; the ac_reads section runs the identical SQL files with SQLite in WAL mode (synchronous=FULL), where SQLite's point-select time halves (64.75ms to 30.19ms) and DoltLite ties or loses on every row. The same pattern holds in the textpk, blobpk and compositepk tables, and file-backed oltp_write_only is 1.2x and 1.3x slower for blob and composite keys. Shared GitHub-hosted runner (ubuntu24 20260927.320.1) with no CPU model; the timer harness is built with cc -O2 -Werror, the libraries with configure defaults, compiler version unstated. test/build_stock_reference.sh notes that CI once shipped a 'stock' reference that shared DoltLite's storage and so passed by construction; the current report uses the rebuilt, asserted stock reference, but older nightly numbers and blog figures may predate that fix (not verified). DoltHub blog posts (dolthub.com blocked; search snippets only) put the prolly-tree tax at 1.20x on reads, 1.67x on batched writes and 4.00x on autocommit writes, with file-backed reads about 5% faster to parity. Licence: DoltLite extensions Apache-2.0, inherited SQLite sources public domain (no patent grant for those). The README describes the project as the product of agentic engineering. [retier] Slower than stock SQLite on every aggregate (1.1x-2.9x); file_reads/file_writes wins only vs rollback-journal SQLite (about 3.5 us per statement, derived from page data), tie or loss vs WAL (point_select 30.19 vs 30.89 ms); sysbench_timer.c re-parses every statement in both engines; fixtures fit the 64 MiB cache so BLAKE3 re-verify beyond cache is unmeasured; baseline is the fork's own SQLite 3.54.0 tree with DOLTLITE_PROLLY=0. Shared CI runner, no CPU model. Beta; P1 merge bugs #3695, #3691, #3688; not the SQLite file format.

Replaces SQLite's B-tree with a content-addressed prolly tree to give Git-like version control (branch, merge, diff, history) on a SQL database; stores in a single-file chunk store, so the file format is not SQLite-compatible. Durable autocommit writes cost about 3x SQLite. Project is labelled Beta.

## Maintenance

Very active beta (commits daily through 2026-10-07, releases weekly, v0.50.15 on 2026-10-05, format version 12 frozen) under Apache-2.0 for DoltLite code with public-domain SQLite sources; usable as a library today, but merge and schema-merge correctness bugs are still being filed and fixed at a high rate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** performance-report.md (nightly, generated 2026-10-06, commit 3e4ff81) compares DoltLite with a stock SQLite reference built by test/build_stock_reference.sh, using public harness code (test/sysbench_compare\*.sh, test/lib/sysbench_benchmark.sh, test/sysbench_timer.c, .github/workflows/nightly-performance.yml), but the runner is a shared ubuntu-latest GitHub runner with no CPU model and no compiler version, and the library builds use configure defaults, so first-party C.
- **Verifier notes:** All quoted numbers match performance-report.md, but the record presented per-row wins without noting that they vanish when stock SQLite uses WAL (the report's own ac_reads section, same SQL files); claim corrected, tier stays C. Record as shortcomings: not faster than SQLite (1.1x-2.9x slower on every aggregate), per-row wins only against default rollback-journal SQLite, shared CI runner without CPU model.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-87 (wave 6); enricher (wave 6)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/performance-report.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/test/sysbench_compare.sh>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/test/lib/sysbench_benchmark.sh>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/test/sysbench_timer.c>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/test/build_stock_reference.sh>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/.github/workflows/nightly-performance.yml>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/doc/doltlite/performance.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/README.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/LICENSE.md>
  - <https://github.com/dolthub/doltlite>
  - <https://github.com/dolthub/doltlite/commits/master>
  - <https://github.com/dolthub/doltlite/tree/master/.github/workflows>
- **Sources the enricher read:**
  - <https://github.com/dolthub/doltlite>
  - <https://github.com/dolthub/doltlite/commits/master>
  - <https://github.com/dolthub/doltlite/releases>
  - <https://github.com/dolthub/doltlite/issues?q=is%3Aissue+is%3Aopen>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/README.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/VERSION>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/performance-report.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/doc/doltlite/performance.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/doc/doltlite/README.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/doc/doltlite/building.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/doc/doltlite/embedding.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/doc/doltlite/concurrency.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/doc/doltlite/storage-format.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/doc/doltlite/sqlite-compatibility.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/doc/doltlite/pragmas.md>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/test/sysbench_compare.sh>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/test/lib/sysbench_benchmark.sh>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/test/sysbench_timer.c>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/test/build_stock_reference.sh>
  - <https://raw.githubusercontent.com/dolthub/doltlite/HEAD/.github/workflows/nightly-performance.yml>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/dolthub/doltlite`) · [data/wave6/enrich/raw/github_com_dolthub_doltlite.json](../../../data/wave6/enrich/raw/github_com_dolthub_doltlite.json) (enrichment confidence 0.8)

</details>
