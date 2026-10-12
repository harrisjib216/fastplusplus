# csvql

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig CLI and MCP server that runs read-only SQL on raw CSV files, about 3x faster than DuckDB's raw-CSV path.

| | |
|---|---|
| **Beats** | DuckDB |
| **Claimed result** | Against DuckDB on the raw CSV (BENCHMARKS.md). 2M-row/56MB aggregates, GROUP BY and DISTINCT on Apple M2 Pro: 2.9x-11.3x faster (6.8x-11.3x excluding MEDIAN GROUP BY at 2.9x; e.g. COUNT(\*) 0.012s vs 0.136s), with 1.8MB vs 63.5MB memory. Output formats: 5.7x-8.6x. Joins: 9x-89x. LIKE on 5M rows/173MB (Apple M2): \~19x-36x. IN-subquery on a 4-core Xeon VM: \~5x down to even at 1M resolved values. NYC Taxi, 20M rows/8GB CSV (Apple M-series; csvql 2.6.0 vs DuckDB 1.5.5): 3.1x-3.4x faster with \~6x less peak memory. Also \~1.9x vs DataFusion 52.1.0 and 2.2x-2.5x vs Polars 2.0.0-rc.1 on the 1M-row taxi sample. |
| **Workload** | SQL aggregates/GROUP BY/JOIN/LIKE queries run directly against raw CSV files (no ingest), at multiple scales: 2M rows/56MB, 5M rows/173MB, and the canonical NYC Taxi 20M rows/8GB CSV benchmark, on Apple M2 Pro / M-series hardware (one section on a cloud Intel Xeon VM, called out as not comparable across sections) |
| **Metric** | latency |
| **Hardware** | Apple M2 Pro / Apple M-series (one section: cloud VM, Intel Xeon, 4 cores) |
| **Compiler and flags** | The bench scripts require building with zig build -Doptimize=ReleaseFast. The README says it needs Zig 0.13.0+ and was tested with 0.15.2; the benchmark page names no compiler version for the runs. |
| **Adoption** | 28 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/melihbirim/csvql) · [benchmark](https://github.com/melihbirim/csvql/blob/main/BENCHMARKS.md) |

## Verdict

First-party wall-clock times for whole CLI processes (startup included), best-of-N on a warm page cache, with csvql built -Doptimize=ReleaseFast (Zig version unstated) and DuckDB CLI 1.5.5 (read_csv_auto) both reading raw CSV without ingest: on the 20M-row, 8 GB NYC taxi CSV on an unnamed Apple M-series machine, csvql 2.6.0 ran the four Billion-Taxi-Rides GROUP BY queries in 1.39-1.52 s vs 4.61-4.71 s (3.1-3.4x). On a 2M-row, 56 MB synthetic file on an M2 Pro, aggregates took 12-56 ms vs 130-160 ms, a gap the author attributes mostly to DuckDB's startup and CSV-reader setup.

## Use it when

- One-off or occasional aggregates, filters and DISTINCT over a single large CSV, with low-to-moderate group counts, when DuckDB's ingest would not pay off (2.1 GB native store and about 26 s one-time load for the 8 GB taxi file).
- Giving an LLM agent read-only query access to local CSVs, or remote ones over SSH, through MCP, sandboxed with --root and logged with --audit.
- Joining a big CSV against small lookup CSVs (the right side is loaded into memory, the left is streamed and probed in parallel) when output order does not matter. The 2M x 6-row joins measured 29-89x faster than DuckDB on raw CSV.
- Shell pipelines doing LIKE or WHERE filtering with CSV, JSON or JSONL output on multi-core Apple Silicon or x86-64. LIMIT without ORDER BY stops early.
- Low-memory machines that must scan multi-GB CSVs without loading them. Peak footprint stayed around 30 MB on the 8 GB file for low-cardinality GROUP BY.

## Skip it when

- High-cardinality GROUP BY. The project's own issue #186 (open) measures 16.2 s vs DuckDB's 8.3 s (about 2x slower) at 5M groups over 75M rows, and that is after #184 brought it down from over 150 s.
- Data you query repeatedly, or that needs Parquet, persistent tables or writes. DuckDB's ingested native store is faster after the one-time load, and csvql cannot write.
- SQL beyond the subset: LEFT/RIGHT/FULL/CROSS joins, UNION/INTERSECT/EXCEPT, window functions, correlated or FROM-clause subqueries, and NULLS FIRST/LAST all return errors.
- Full-table ORDER BY with no filter. ARCHITECTURE.md shows DuckDB 1.5x faster (0.108 s vs 0.163 s on 1M rows), because csvql must parse every row to extract the sort key.
- Cases that need bit-reproducible floating-point results. SUM and AVG change in the last digits between --threads 1 and the parallel default (issue #185, open), so the parallel output also differs from DuckDB.

## How it is fast

Files over 10 MB are mmap'd (MADV_SEQUENTIAL), split into newline-aligned chunks and scanned one chunk per core without locks; each worker keeps its own output buffer or GROUP BY hash map, switching to a shared Wyhash-sharded map after 50k groups. Record scanning uses Zig @Vector(16,u8) compares (SSE2/NEON) to find delimiters, quotes and newlines in one pass, falls back to a scalar quote-aware state machine only for quoted records, and returns fields as zero-copy slices into the mapping. ORDER BY uses pre-parsed f64 keys with an LSD radix sort, or a top-K heap under LIMIT. Much of the gap is fixed per-query cost csvql never pays (DuckDB's CSV sniffing, type inference and columnar materialization), which is why the lead is about 10x on a 417 MB file but about 3.2x on 8 GB, where the author measures csvql's COUNT(\*) at 1.05 s against 1.92 s for cat over the same file.

## Compared with alternatives

Pick csvql over Apache DataFusion, or DuckDB itself, for a raw CSV you will query only a few times with scans, low-cardinality aggregates or lookup joins, especially as a small static binary or an agent's MCP tool; its own 1M-row taxi-sample run puts it about 1.9x ahead of DataFusion 52.1.0 with about 5.6x less memory. Pick DataFusion, Databend or chDB when you need full SQL, Parquet or table storage, outer joins, window functions or high-cardinality aggregation.

## Integration

| | |
|---|---|
| **Form** | Standalone CLI binary and MCP stdio server (Homebrew or prebuilt release). Also a C-ABI shared library inside the Python wheel (csvql-query) and the Node addon; the CSV reader can be imported as a Zig package. |
| **Dependencies** | None at runtime (build.zig.zon lists no dependencies). The correctness and benchmark scripts need a DuckDB CLI, and Python's query_df needs pandas. |
| **Minimum toolchain** | Zig 0.15.x in practice. CI pins 0.15.2, and the source uses the 0.15-style unmanaged std.ArrayList API and the newer build.zig.zon format, so the README's 'Zig 0.13.0+' is out of date. The Python wheels need Python 3.10 or later. |
| **Platforms** | Prebuilt for macOS arm64/x86-64, Linux x86-64 and Windows x86-64; Python wheels add Linux aarch64. SIMD uses portable 16-byte @Vector code (SSE2/NEON), so AVX is not required. The differential tests against DuckDB run in CI only on Ubuntu x86-64 and macOS-14 arm64; Windows gets build and unit tests only. |
| **Thread safety** | Not documented for concurrent library calls. The CLI is multi-threaded internally (--threads N, 0 = auto). Each C-ABI call runs on its own thread with a 64 MB stack, uses libc malloc and shares no handle. |
| **Drop-in for the baseline** | partial: it accepts DuckDB-style SELECT text over CSV paths, but only a SELECT subset with INNER joins only, untyped columns, documented output differences (NULL written as an empty field, LENGTH counting bytes, fractional DATEDIFF, an empty field matching col = ''), and no tables or storage. |

## Gotchas

- Join output order, and GROUP BY output without ORDER BY, is undefined. Parallel SUM/AVG differ in the last digits from single-threaded runs and from DuckDB (issue #185).
- Rows wider than the fixed 256-slot field buffer: several scan paths in engine.zig and parallel_mmap.zig catch TooManyColumns with 'continue', which silently skips the row, or truncate the row. The allocating parseCSVFields limit is 64 fields. None of this is documented, so very wide CSVs are unsafe.
- Treat the memory numbers with care. BENCHMARKS.md's '1.8 MB vs 63.5 MB' predates parallel execution; the author's own 2026-08-17 audit measured about 53-74 MB max RSS. The taxi figures use macOS 'peak memory footprint', which leaves out clean mmap'd file pages and so favors csvql's design, and issue #186 notes that max RSS understates badly once macOS compresses pages.
- Without --strict, a WHERE numeric comparison against a non-numeric cell silently drops that row. In SQL mode, SELECT \* with no LIMIT streams the whole file (#170). The project has fixed a long list of silent wrong-answer bugs (#139 parallel aggregate undercount on large files, #142 and #154 dropped AND/OR branches), and correctness rests on differential testing against DuckDB.

## Known shortcomings

- The aggregate range is 2.9-11.3x (MEDIAN 2.9x); ReleaseFast is set only in bench scripts, Zig 0.15.2 is only 'tested with', and the Taxi CPU is given as just 'M-series'.
- Loses high-cardinality GROUP BY (5M groups 16.2 s vs DuckDB 8.3 s, #186 open) and full-table ORDER BY without WHERE (DuckDB 1.5x faster); SUM/AVG last digits change with thread count (#185); rows over 256 fields are silently skipped/truncated. Memory claims are shaky (the '1.8 MB' is stale; \~53-74 MB RSS). Zig 0.15.x only, SELECT subset with INNER joins only, solo author, no independent benchmarks.

## Caveats and trade-offs

First-party benchmark. The ReleaseFast build appears only as a prerequisite in the bench scripts, the Zig version is not tied to the published runs, and the headline NYC Taxi section names only "Apple M-series" with no specific CPU, so it falls short of tier A. The benchmark hardware varies by section (M2 Pro, M2, M-series, and a 4-core Xeon VM that the page itself says is not comparable). The gains are workload-sensitive. MEDIAN GROUP BY is only 2.9x, and IN-subquery drops to parity at 1M resolved values after a \~20x loss was found and fixed. The small-file gaps are inflated by DuckDB process and CSV-reader startup, which the author acknowledges. Results were checked for equality against DuckDB with bench/verify_correctness.sh.

Read-only (SELECT only, no INSERT/UPDATE/DELETE), single-file CSV-in-place querying via mmap, no persistent storage engine; join output order is undefined for parallelism. Positioned as an MCP tool for LLM agents to query large CSVs cheaply rather than a general OLAP replacement.

## Maintenance

Actively developed with frequent releases (v2.7.0 on 2026-09-14), almost entirely by one author (276 of about 322 contributions). It is MIT-licensed and installable via Homebrew, prebuilt binaries or PyPI wheels, but it is young (created 2026-02), has 28 stars, and has no independent benchmarks or discussion (one Show HN post with no comments).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** These are first-party numbers from public scripts (bench/bench_all.sh, bench/bench_taxi.sh, with DuckDB pinned at 1.5.5 in bench/DUCKDB_VERSION). The CPU is named only for some sections (Apple M2 Pro; the headline taxi section says only "Apple M-series"). The build flags appear only as the scripts' prerequisite (zig build -Doptimize=ReleaseFast), and the Zig version is only the README's "tested with 0.15.2", not tied to the runs. So methodology is partial and the tier stays C.
- **Verifier notes:** The benchmark page backs every claimed number except the aggregate range, which I widened to include MEDIAN (2.9x). The record's statement that build flags are not stated was only partly true, so I corrected compiler_and_flags and the caveats. The metadata (MIT, 28 stars, last commit 2026-09-26, not a fork) checks out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/melihbirim/csvql>
  - <https://github.com/melihbirim/csvql/blob/main/BENCHMARKS.md>
  - <https://github.com/melihbirim/csvql/blob/main/README.md>
  - <https://github.com/melihbirim/csvql/blob/main/bench/bench_all.sh>
  - <https://github.com/melihbirim/csvql/blob/main/bench/bench_taxi.sh>
  - <https://github.com/melihbirim/csvql/blob/main/bench/DUCKDB_VERSION>
  - <https://github.com/melihbirim/csvql/blob/main/build.zig>
  - <https://github.com/melihbirim/csvql/blob/main/build.zig.zon>
- **Sources the enricher read:**
  - <https://github.com/melihbirim/csvql>
  - <https://github.com/melihbirim/csvql/blob/main/README.md>
  - <https://github.com/melihbirim/csvql/blob/main/BENCHMARKS.md>
  - <https://github.com/melihbirim/csvql/blob/main/ARCHITECTURE.md>
  - <https://github.com/melihbirim/csvql/blob/main/CORRECTNESS.md>
  - <https://github.com/melihbirim/csvql/blob/main/SQL_REFERENCE.md>
  - <https://github.com/melihbirim/csvql/blob/main/SECURITY.md>
  - <https://github.com/melihbirim/csvql/blob/main/VERIFICATION-LOG.md>
  - <https://github.com/melihbirim/csvql/blob/main/build.zig>
  - <https://github.com/melihbirim/csvql/blob/main/build.zig.zon>
  - <https://github.com/melihbirim/csvql/blob/main/.github/workflows/ci.yml>
  - <https://github.com/melihbirim/csvql/blob/main/bench/bench_taxi.sh>
  - <https://github.com/melihbirim/csvql/blob/main/bench/bench_all.sh>
  - <https://github.com/melihbirim/csvql/blob/main/src/lib.zig>
  - <https://github.com/melihbirim/csvql/blob/main/src/simd.zig>
  - <https://github.com/melihbirim/csvql/blob/main/src/parser.zig>
  - <https://github.com/melihbirim/csvql/blob/main/src/engine.zig>
  - <https://github.com/melihbirim/csvql/blob/main/src/parallel_mmap.zig>
  - <https://github.com/melihbirim/csvql/blob/main/src/csv.zig>
  - <https://github.com/melihbirim/csvql/blob/main/src/aggregation.zig>
  - <https://github.com/melihbirim/csvql/blob/main/docs/LIBRARY.md>
  - <https://github.com/melihbirim/csvql/blob/main/docs/PYTHON.md>
  - <https://github.com/melihbirim/csvql/blob/main/python/pyproject.toml>
  - <https://github.com/melihbirim/csvql/blob/main/docs/blog/csvql-vs-duckdb-nyc-taxi.md>
  - <https://github.com/melihbirim/csvql/blob/main/docs/blog/auditing-our-own-claims.md>
  - <https://github.com/melihbirim/csvql/issues>
  - <https://github.com/melihbirim/csvql/issues/186>
  - <https://github.com/melihbirim/csvql/issues/185>
  - <https://github.com/melihbirim/csvql/issues/184>
  - <https://github.com/melihbirim/csvql/issues/170>
  - <https://github.com/melihbirim/csvql/issues/168>
  - <https://github.com/melihbirim/csvql/releases>
  - <https://pypi.org/pypi/csvql-query/json>
  - <https://hn.algolia.com/api/v1/search?query=csvql&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/melihbirim/csvql`) · [data/wave6/enrich/raw/github_com_melihbirim_csvql.json](../../../data/wave6/enrich/raw/github_com_melihbirim_csvql.json) (enrichment confidence 0.8)

</details>
