# musql

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Pure-Go SQLite-dialect engine on its own columnar format; JIT filter/aggregate kernels beat C SQLite on read-mostly scans.

| | |
|---|---|
| **Beats** | SQLite (C, via mattn/go-sqlite3); Turso's Go driver is also compared |
| **Claimed result** | docs/benchmarks.md (engine-direct API, selected read shapes): up to about 77x over C SQLite on the published rows; through database/sql (an arm the harness times but the docs omit, about 0.2 ms driver cost per statement per format-design.md) the gain is roughly 9-10x (derived from page data). The 17 non-JIT read shapes dropped by BENCH_SKIP trail C SQLite by about 3.5x per the harness notes; writes, BETWEEN and min/max are not published. |
| **Workload** | Read queries over 100,000 rows on disk-backed files with a warm cache, each checked against C SQLite on 40 bind values before timing, then timed for about 200 ms; musql run with and without its JIT (MUSQL_JIT=0). |
| **Metric** | latency |
| **Hardware** | Apple M4 (arm64, macOS) and Intel Xeon D-2123IT (amd64, Linux) |
| **Compiler and flags** | Go 1.27.0 per go.mod and compat-harness/go.mod (the benchmark page states no toolchain version); default go test build; C SQLite is mattn/go-sqlite3 v1.14.48 built through cgo with default flags (C compiler not stated); Turso via turso.tech/database/tursogo v0.7.2; harness compat-harness/bench_columnar_vs_c_test.go (TestBenchColumnarVsC), JIT on vs MUSQL_JIT=0 |
| **Adoption** | 29 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/samyfodil/musql) · [benchmark](https://github.com/samyfodil/musql/blob/HEAD/docs/benchmarks.md) |

## Verdict

The author's harness TestBenchColumnarVsC ran 100,000-row, disk-backed, warm-cache reads, timed for about 200 ms each, with every arm's answers checked against C SQLite (mattn/go-sqlite3 v1.14.48, Go 1.27 toolchain per go.mod). On Apple M4 and Intel Xeon D-2123IT, musql's engine-direct API with its JIT beat C SQLite 65-92x on integer filtered counts, 7.6-8.5x on sum over a filter, 2.0-2.7x on GROUP BY and top-N, and 1.6-1.8x on whole-table count. It was at parity or 1.2-2.9x slower on rowid, secondary-index and join lookups, with non-JIT shapes and writes excluded from the run.

## Use it when

- Embedded, read-mostly Go applications that run many integer range-filter counts or sums over a table of about 100k rows or more: one-predicate filtered count 28 us vs C SQLite 2.17 ms on Apple M4, 89 us vs 6.19 ms on a Xeon D-2123IT (engine-direct API).
- Simple integer GROUP BY aggregates and `ORDER BY col DESC LIMIT n` top-N over large tables (2.0-2.7x vs C SQLite).
- Projects that need SQLite SQL without cgo (cross-compiles to the Go GOOS/GOARCH matrix) and accept a separate on-disk format.
- Teams already on Turso/libSQL clients who want a self-hosted Hrana server, where musql's reads also beat Turso's Go driver in the published table.

## Skip it when

- Any query shape the recogniser does not model: min/max, BETWEEN, OR, IN lists, IS NULL, LIKE, text ordering, DISTINCT, subqueries, EXISTS, UNION and OFFSET run the ordinary VDBE, which the harness's own comments put at about 3.5x slower than C SQLite on a scan. These shapes were left out of the published table.
- Write-heavy workloads: the harness calls writes the engine's worst side and the published run skipped them. write-path-overlay.md measured 3,442 MB allocated for one bulk UPDATE over about 10k rows, with GC drain at 39% of CPU before cuts.
- Point lookups and indexed joins: rowid lookup 1.8x slower, secondary-index equality 2.9x slower and equi-join 1.3x slower than C SQLite on the Xeon.
- Applications that must open existing SQLite .db files in place or share them with C SQLite processes: conversion is required, and multi-process concurrency against a live C writer is not claimed.
- Production use that needs maturity: one squashed commit (2026-10-05), 29 stars, and a run-time code generator whose linux/arm64 path format-design.md says had never run on hardware when written.

## How it is fast

Most of the win comes from the storage layout. Fixed-width columns are stored contiguously, so a filter reads one `[]int64` block instead of walking SQLite's varint record headers and b-tree cell pointers (format-design.md measures 2.1 ns/row against SQLite's 114 ns/row format floor). A peephole pass (`segment_peephole.go`) spots filter-and-count, sum-over-filter, GROUP BY and ORDER BY ... LIMIT shapes in the compiled VDBE program and adds guarded fast-path opcodes. These call machine code that `internal/jit` emits at run time: AVX2 four-lane or NEON two-lane compare kernels, with a scalar fallback, mapped W^X (mmap RW, copy, mprotect RX) and entered through one Go-assembly trampoline per architecture. Bare `count(*)` is answered from the segments' recorded row counts, and top-N runs a bounded heap over an int64 block.

## Compared with alternatives

Pick musql over pg_jitter, AsmJit-backed or sljit-backed PostgreSQL JITs when you need an embedded, cgo-free SQLite-dialect store in Go and your hot queries are integer filter/count/sum, GROUP BY or top-N over read-mostly data. Use those PostgreSQL JITs if you are on PostgreSQL, and stay on C SQLite for point lookups, joins, writes or arbitrary SQL shapes.

## Integration

| | |
|---|---|
| **Form** | Go module (`go get github.com/samyfodil/musql/driver`), plus musqld server binary or Docker image |
| **Dependencies** | github.com/coder/websocket, golang.org/x/sys, google.golang.org/protobuf; no cgo (the benchmark/differential harness is a separate module that needs cgo for mattn/go-sqlite3) |
| **Minimum toolchain** | Go 1.27 |
| **Platforms** | Any Go target for the engine; JIT kernels only on amd64 and arm64 under linux or darwin (AVX2 vector kernel on amd64, scalar kernel without AVX2, NEON on arm64); exercised on darwin/arm64 and amd64, linux/arm64 builds but was untested per format-design.md |
| **Thread safety** | database/sql semantics; two musql connections in one process are covered by TestN4ConcurrentReadersAndWriters, cross-process concurrency with a live C SQLite writer is not claimed; README asks for one SQL statement per Exec/Query call |
| **Drop-in for the baseline** | partial: SQL dialect and database/sql driver name match (import swap), but data must be converted to .musq and the JIT speedups apply only to a few read shapes |

## Gotchas

- Harness finding: the published musql column is the engine-direct API (`musqlengine.Open` + `ReadOnlyPager.QueryArgs`, returning raw Values), while C SQLite is timed through database/sql, cgo and fmt-rendered strings. The harness also times a musql arm through database/sql (the API the README tells users to adopt), but docs/benchmarks.md does not publish that column. format-design.md section 8b measured the driver's per-statement cost at about 0.2 ms at an earlier stage and said it dwarfs the 44 us kernel, so the 70-92x filtered-count wins should not be expected through database/sql (derived from page data: about 0.2 ms plus 28 us against C's 2.17 ms would be roughly 9-10x on M4, if that older overhead figure still holds; no current driver numbers are published).
- Speedups fall off a cliff when a query leaves the recognised shape. The same one-predicate count takes 9.83 ms with the fast path off vs 2.17 ms for C on M4. A bare `count(*)` falls back to 74.5 ms (M4) and 276.8 ms (Xeon) against C's 9 us and 47 us, because without the segment row-count shortcut the VDBE decodes every row. Small SQL edits such as BETWEEN for a range or an added OR move a query off the fast path.
- The published run sets BENCH_SKIP to drop 17 read shapes (including min/max and BETWEEN, which sit next to the winning shapes) and all writes. C SQLite is opened with driver defaults (no cache_size or mmap_size PRAGMA), so it is an untuned baseline. The page says each workload is checked on 40 bind values before timing; in the code the check loop runs after the timing loop (5-40 values by cost) and is fatal before the table prints, so published tables did pass it.
- The JIT writes machine code into mmap'd memory and jumps into it from Go through hand-written trampolines (Go's frame and LR conventions on arm64, X18 reserved on darwin). That is an unsafe surface in an otherwise memory-safe codebase, and design notes record several fast paths that silently declined or returned wrong cells until the counters and value-by-value differential checks were added.

## Known shortcomings

- The published BENCH_SKIP drops 17 non-JIT read shapes (the harness notes they trail C SQLite by about 3.5x) and all writes, so the docs/benchmarks.md table is cherry-picked; no Go or cgo C compiler version (go.mod 1.27.0 only) and the repo is one squashed commit. Off-baseline (C SQLite); Go.
- Enricher: the published numbers use the engine-direct API while the harness also times a database/sql arm that docs/benchmarks.md omits; format-design.md puts the driver cost near 0.2 ms per statement, so through database/sql the gain is roughly 9-10x rather than 77x (derived), and the speedup comes mostly from the columnar format rather than the JIT. C SQLite is untuned (no cache_size or mmap PRAGMA) and BENCH_SKIP drops BETWEEN, min/max and writes.

## Caveats and trade-offs

The published run sets BENCH_SKIP to drop 17 read shapes that no musql fast path answers (min/max, GROUP BY with HAVING, OR, BETWEEN, IN list, IS NULL, LIKE, ORDER BY text, group_concat, DISTINCT, subqueries, EXISTS, UNION, OFFSET, join projecting) plus every write (UPDATE, INSERT, DELETE); the harness's own comments say those shapes run the ordinary VDBE, which trails C SQLite by about 3.5x on a scan, and that writes are where the engine is at its worst, so the published table shows the JIT-served shapes plus three point lookups only. The win comes from columnar storage plus JIT against SQLite's row store (musql reads its own .musq format after VACUUM; SQLite files need conversion); without the JIT musql is much slower than C SQLite on the same scans (9.83 ms vs 2.17 ms for the one-predicate filtered count on M4). Arms are not identical: musql is timed through its direct engine API while C SQLite is timed through database/sql and cgo with each result rendered to a string, which matters only for the microsecond rows. Whole-table count is answered from segments' recorded row counts, not a scan. Microsecond-scale rows vary run to run, more on amd64. The README headline 75x is the two-machine average of the one-predicate (73x) and two-predicate (77x) rows. The repository history is a single squashed commit (2026-10-05). [retier] Published table is engine-direct and cherry-picked (BENCH_SKIP drops 17 non-JIT read shapes, writes, BETWEEN and min/max); the database/sql arm is omitted; C SQLite is untuned (no cache_size or mmap PRAGMA); the speedup comes mostly from the columnar storage format rather than the JIT. No Go or cgo C compiler version (go.mod 1.27.0 only); the repo is one squashed commit. Off-baseline (C SQLite); Go.

SQLite-compatible SQL on a new columnar .musq segment format with an append-only delta; import/export tools to and from SQLite files. The JIT covers only supported scan/filter/aggregate query paths; point lookups and joins do not use it. Pure Go driver, but the benchmark harness needs cgo.

## Maintenance

Active but very young: published as a single squashed commit on 2026-10-05, 29 stars, Apache-2.0, pure Go and easy to vendor. It has a strong differential-testing culture (67,800-73,855 SQLite test-suite statements with zero wrong results), but treat it as a fast path for a narrow set of read shapes on converted data, not as a general SQLite replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/benchmarks.md carries every quoted number for Apple M4 and Intel Xeon D-2123IT against C SQLite (mattn/go-sqlite3 v1.14.48, pinned in compat-harness/go.mod) and Turso, from the public harness compat-harness/bench_columnar_vs_c_test.go (TestBenchColumnarVsC) with the exact go test command and BENCH_SKIP list; the harness checks every arm's answers against C SQLite before timing. Go 1.27.0 comes from go.mod (the page itself names no toolchain or cgo C compiler versions), which matches the wazy precedent for this author's Go harnesses.
- **Verifier notes:** Numbers and ratios match docs/benchmarks.md row for row, and results are checked against C SQLite before timing, so the evidence is valid; the main shortcoming is a cherry-picked published table (BENCH_SKIP removes the non-JIT read shapes where musql trails C SQLite by about 3.5x, and all writes). Apache-2.0, 29 stars, 3 forks, one commit on main dated 2026-10-05; arguably a database engine more than a JIT, category left as filed.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/README.md>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/compat-harness/bench_columnar_vs_c_test.go>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/go.mod>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/compat-harness/go.mod>
  - <https://github.com/samyfodil/musql>
  - <https://github.com/samyfodil/musql/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/README.md>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/compat-harness/bench_columnar_vs_c_test.go>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/compat-harness/bench_vs_c_test.go>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/go.mod>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/compat-harness/go.mod>
  - <https://github.com/samyfodil/musql/tree/main/compat-harness>
  - <https://github.com/samyfodil/musql/tree/main/engine>
  - <https://github.com/samyfodil/musql/tree/main/docs>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/docs/format-design.md>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/docs/segment-format-compatibility.md>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/docs/write-path-overlay.md>
  - <https://raw.githubusercontent.com/samyfodil/musql/HEAD/docs/swap-readiness.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/samyfodil/musql`) · [data/wave12/enrich/raw/github_com_samyfodil_musql.json](../../../data/wave12/enrich/raw/github_com_samyfodil_musql.json) (enrichment confidence 0.75)

</details>
