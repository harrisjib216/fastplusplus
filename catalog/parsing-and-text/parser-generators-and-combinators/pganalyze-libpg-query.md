# libpg_query

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Parser generators and combinators](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> PostgreSQL's own Bison parser as a standalone C library; raw parse about 5-7x faster than sqlparser-rs in a rival's harness.

| | |
|---|---|
| **Beats** | sqlparser-rs (Rust SQL parser, sqlparser crate 0.52, MySQL dialect rows) |
| **Claimed result** | pg_query_raw_parse vs sqlparser-rs, reference results table: simple SELECT 684 ns vs 4,687 ns (6.9x, derived from page data), SELECT JOIN 1,646 ns vs 10,684 ns (6.5x, derived), complex SELECT 3,304 ns vs 23,411 ns (7.1x, derived), INSERT 781 ns vs 3,784 ns (4.8x, derived), BEGIN 230 ns vs 412 ns (1.8x, derived). With the public pg_query_parse JSON output: simple SELECT 1,872 ns vs 4,687 ns (2.5x, derived), complex SELECT 8,675 ns vs 23,411 ns (2.7x, derived), but BEGIN 421 ns vs 412 ns (parity). |
| **Workload** | Parse-only latency of single statements (simple SELECT, SELECT with JOIN, complex SELECT with GROUP BY/HAVING/ORDER BY/LIMIT, INSERT VALUES, BEGIN) through pg_query_raw_parse (Google Benchmark) versus sqlparser-rs Parser::parse_sql (Criterion), as measured in the ParserSQL project's comparison harness. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 5950X, Linux 6.17 (reference results in REPRODUCING.md; docs/benchmarks/latest.md confirms the CPU and g++ 13.3.0). |
| **Compiler and flags** | GCC 13.3 (g++ 13.3.0 per docs/benchmarks/latest.md); libpg_query built with its own Makefile default -O3 (plus -g per REPRODUCING.md), the Google Benchmark harness bench/bench_comparison.cpp built from Makefile.release (-std=c++17 -O3); sqlparser-rs through cargo bench (default bench profile, rustc version not stated), criterion 0.5.1, sqlparser 0.52.0 (Cargo.lock). |
| **Adoption** | 1.5k stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/pganalyze/libpg_query) · [benchmark](https://github.com/ProxySQL/ParserSQL/blob/main/docs/benchmarks/REPRODUCING.md) |

## Verdict

In the ProxySQL/ParserSQL comparison harness (AMD Ryzen 9 5950X, Linux 6.17, GCC 13.3 at -O3, Google Benchmark for C, Criterion with sqlparser 0.52.0 for Rust), libpg_query's internal raw parse took 230-3,304 ns per statement versus sqlparser-rs's MySQL-dialect parse_sql at 412-23,411 ns (1.8x on BEGIN, 4.8-7.1x on SELECT and INSERT, derived from page data); through the public JSON API the gain is 2.0-2.7x and BEGIN is at parity. The table comes from a rival project whose own parser is the winner, the PostgreSQL-dialect sqlparser-rs rows were run but not published, and libpg_query was an unpinned HEAD clone.

## Use it when

- Tools that must accept exactly what a given PostgreSQL major version accepts: linters, query analyzers, migration checkers, language servers, proxies and query-fingerprinting pipelines.
- Grouping or deduplicating queries by fingerprint compatible with Postgres queryid semantics (Postgres 18 rules by default, PG17 compatibility flag available).
- Bindings from Ruby, Go, Rust, Python, Node or OCaml where a mature wrapper already exists (pg_query, pg_query_go, pg_query.rs, pglast and others).
- Single-statement parse latency in the sub-microsecond to few-microsecond range is acceptable (about 0.2-3.3 us raw, 0.4-8.7 us with JSON on a Ryzen 9 5950X in the ParserSQL harness).

## Skip it when

- Any dialect other than PostgreSQL (MySQL, SQLite, T-SQL, BigQuery): the grammar rejects it; sqlparser-rs or a dialect-aware parser is the tool.
- Hot paths that need the fastest possible PostgreSQL parse: the raw tree is only reachable through the internal header pg_query_internal.h, and the public JSON path costs about 2.7x the raw parse; in the same harness the hand-written ParserSQL was about 3x faster than the raw path.
- Builds that cannot afford a large C library: the static archive is about 30 MB per the ParserSQL instructions and the README warns that make takes up to 3 minutes.
- Normalizing untrusted query text on releases older than 18.1.0 or 17-6.2.4: GHSA-6ggm-xmc9-8ffg is a heap out-of-bounds write and read in pg_query_normalize.
- Projects that need one parser across Postgres major versions: each major lives on its own branch (18-latest active, 17-latest critical fixes only, older unsupported) and token numbers change between versions.

## How it is fast

The speed is PostgreSQL's: a table-driven LALR(1) Bison parser fed by a Flex scanner, allocating nodes in a per-call AllocSet memory context that is deleted wholesale at the end, built at -O3 by default. The raw tree (List of RawStmt nodes) is cheap; most of the public-API cost is the JSON or Protobuf serialization on top, which in the ParserSQL harness takes the simple SELECT from 684 ns raw to 1,872 ns with JSON. The 18.1.0 release replaced protobuf-c with the vendored upb runtime, which the changelog says is substantially faster (no numbers published).

## Compared with alternatives

The catalogued siblings (PEGTL, lexy, re2c, PAPAGENO, Pika) are toolkits for writing your own grammar; pick libpg_query when the grammar you need is PostgreSQL's SQL itself, since it gives byte-for-byte server parity without writing or maintaining a grammar.

## Integration

| | |
|---|---|
| **Form** | static lib (libpg_query.a; shared lib target also in the Makefile) |
| **Dependencies** | none external at runtime besides pthreads; vendors upb (Protobuf runtime), xxHash and the extracted PostgreSQL sources; building needs make and a C compiler (nmake with Makefile.msvc on Windows) |
| **Minimum toolchain** | not documented; C compiler with __thread thread-local storage (GCC or Clang), MSVC via Makefile.msvc |
| **Platforms** | Linux, macOS, FreeBSD and Windows (MSVC) per the build files; x86-64, ARM and PPC per the changelog |
| **Thread safety** | Thread-safe through thread-local storage since 9.5-1.4.0; each thread gets its own top-level memory context, initialized on first call and freed by a pthread exit hook (or pg_query_exit); test/concurrency.c runs 50-500 threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness note: the fast rows call the internal pg_query_raw_parse and never free result.stderr_buffer (pg_query_raw_parse strdup()s it on every call), so the raw benchmark leaks one small allocation per iteration and omits that free from the timing; the public pg_query_parse rows free it.
- Each call creates and deletes a fresh memory context and, since 18.1.0, re-measures the thread's stack to set the stack-depth limit (100 kB default, up to 2 MB); deeply nested queries now return 'stack depth limit exceeded' instead of crashing, but the numbers above were taken on an unpinned HEAD clone and may predate this.
- Comments are ignored when parsing but significant when scanning (18.1.0); fingerprints changed between 17 and 18 (schema ignored, alias used) unless PG_QUERY_FINGERPRINT_RANGEVAR_PG17_COMPAT is passed.
- Open issues include a process abort in pg_query_deparse_protobuf on valid parse results (#330) and PL/pgSQL parse regressions in 18.0.0 (#337); the README recommends pinning a tagged release for production.

## Known shortcomings

- Tier A on ProxySQL/ParserSQL (bench_comparison.cpp, parse_bench.rs, GCC 13.3 -O3, Ryzen 9 5950X; raw parse 684 ns vs sqlparser-rs 4,687 ns, 6.9x derived) but off-baseline: sqlparser-rs is not a category baseline and libpg_query is itself Bison-generated; baseline rows use the MySQL dialect; the fast path uses the internal pg_query_raw_parse API; libpg_query unpinned; rustc version unstated; rival's harness in which libpg_query loses to ParserSQL by about 3.1x.
- Enricher: the ParserSQL bench_comparison.cpp raw rows never free result.stderr_buffer, which pg_query_raw_parse strdup()s on every call, so each iteration leaks it and the free cost is left out of raw timing (minor); off-baseline (sqlparser-rs MySQL dialect rows published, PG-dialect rows run but unpublished), fast path is an internal API, rival's harness, unpinned HEAD clone; 18.1.0 adds a per-call stack-depth check and upb, so the numbers likely predate it. GHSA-6ggm-xmc9-8ffg heap OOB in pg_query_normalize fixed in 18.1.0 / 17-6.2.4; open #330 deparse abort.

## Caveats and trade-offs

Not a libpg_query claim: the numbers come from a rival project's harness (ProxySQL/ParserSQL, 4 stars, AGENTS.md and CLAUDE.md in the repo), where libpg_query is the baseline being beaten (ParserSQL 3.1x faster on parse-only, 8.4x with JSON). The libpg_query entry is a derived ratio against sqlparser-rs, which is not one of the category's baselines (Bison/Flex, ANTLR, Boost.Spirit, nom); libpg_query is itself PostgreSQL's Bison-generated parser, so it stands for the Bison incumbent rather than beating it, and the comparison is C versus a hand-written Rust parser. The reported sqlparser-rs rows are the MySQL-dialect ones (sqlparser_rs_mysql_\*); parse_bench.rs also runs PostgreSqlDialect rows, which are the closer match to libpg_query's grammar but are not published. The fast rows use pg_query_raw_parse from the internal header pg_query_internal.h (timed with memory-context enter/exit); through the public pg_query_parse JSON API the gain falls to 2.0-2.7x and BEGIN is at parity (421 ns vs 412 ns). libpg_query was cloned at HEAD (--depth 1) without a pin and the rustc version is not stated; the ParserSQL README gives rounded figures (libpg_query \~4x and sqlparser-rs \~25x slower than ParserSQL) that differ from the REPRODUCING.md table, so numbers are version-dependent. The table values were read from the committed page, not rerun. libpg_query's own benchmark/ directory covers only the Protobuf layer and publishes no results. A PgDog blog post (search snippet only) reports 5x faster parsing by replacing Protobuf with direct C-to-Rust bindings, which concerns the binding layer, not the parser.

Extracts the real PostgreSQL parser (Bison grammar, lexer, node types, memory contexts) into a standalone C library, so it accepts PostgreSQL syntax exactly but only PostgreSQL syntax. The public API pays for JSON or Protobuf serialization on top of the raw parse (about 2.7x the raw parse time in this harness); the raw parse API is internal. The 18-latest branch uses upb for Protobuf (changelog: substantially faster than protobuf-c, no numbers).

## Maintenance

Actively maintained by pganalyze (18.1.0 released 2026-09-30 with a security fix, about 1.5k stars, BSD-3-Clause plus the PostgreSQL licence) and widely embedded (DuckDB, pganalyze, Supabase's Postgres language server); copyable, but pin a tag and upgrade past GHSA-6ggm-xmc9-8ffg if you normalize untrusted input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** ProxySQL/ParserSQL bench/bench_comparison.cpp (Google Benchmark, pg_query_raw_parse and pg_query_parse) and bench/sqlparser_rs_bench/benches/parse_bench.rs (Criterion, sqlparser 0.52.0 per Cargo.lock) are public; REPRODUCING.md states AMD Ryzen 9 5950X, Linux 6.17, GCC 13.3 -O3, and libpg_query's Makefile defaults to -O3, so A holds (rustc version for the baseline is not stated).
- **Verifier notes:** All claimed figures appear in the REPRODUCING.md Reference Results table and the derived ratios are correct (6.9x/6.5x/7.1x/4.8x/1.8x raw; 2.5x/2.7x/parity with JSON). Shortcomings to record: off-baseline (sqlparser-rs is not a category baseline and libpg_query is itself Bison-generated), MySQL-dialect baseline rows, fast path uses an internal API, unpinned libpg_query and unstated rustc version, numbers from a rival's harness. Lead: ProxySQL/ParserSQL (4 stars) claims 3.1x over libpg_query raw parse on the same harness.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-91 (wave 6); enricher w6 pair-014
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/docs/benchmarks/REPRODUCING.md>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/docs/benchmarks/latest.md>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/README.md>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/bench/bench_comparison.cpp>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/bench/sqlparser_rs_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/bench/sqlparser_rs_bench/Cargo.lock>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/bench/sqlparser_rs_bench/benches/parse_bench.rs>
  - <https://github.com/ProxySQL/ParserSQL>
  - <https://github.com/pganalyze/libpg_query>
  - <https://github.com/pganalyze/libpg_query/commits/18-latest>
  - <https://raw.githubusercontent.com/pganalyze/libpg_query/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/pganalyze/libpg_query>
  - <https://github.com/pganalyze/libpg_query/issues>
  - <https://github.com/pganalyze/libpg_query/issues?q=is%3Aissue+performance>
  - <https://raw.githubusercontent.com/pganalyze/libpg_query/HEAD/README.md>
  - <https://raw.githubusercontent.com/pganalyze/libpg_query/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/pganalyze/libpg_query/HEAD/Makefile>
  - <https://raw.githubusercontent.com/pganalyze/libpg_query/HEAD/pg_query.h>
  - <https://raw.githubusercontent.com/pganalyze/libpg_query/HEAD/src/pg_query_internal.h>
  - <https://raw.githubusercontent.com/pganalyze/libpg_query/HEAD/src/pg_query_parse.c>
  - <https://raw.githubusercontent.com/pganalyze/libpg_query/HEAD/src/pg_query.c>
  - <https://raw.githubusercontent.com/pganalyze/libpg_query/HEAD/test/concurrency.c>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/docs/benchmarks/REPRODUCING.md>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/docs/benchmarks/latest.md>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/README.md>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/bench/bench_comparison.cpp>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/bench/sqlparser_rs_bench/benches/parse_bench.rs>
  - <https://raw.githubusercontent.com/ProxySQL/ParserSQL/HEAD/Makefile>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/pganalyze/libpg_query`) · [data/wave6/enrich/raw/github_com_pganalyze_libpg_query.json](../../../data/wave6/enrich/raw/github_com_pganalyze_libpg_query.json) (enrichment confidence 0.6)

</details>
