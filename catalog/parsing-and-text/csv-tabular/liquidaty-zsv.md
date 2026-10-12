# zsv (zsv+lib)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> SIMD C CSV parser/CLI beating DuckDB and Polars on read throughput, with a slow correct fallback for nonstandard quoting.

| | |
|---|---|
| **Beats** | DuckDB CSV reader and Python Polars read_csv (also benchmarked against BurntSushi/xsv, qsv, and xan) |
| **Claimed result** | On the darwin-arm64 page (Apple M3 Pro, best-of-5), count on unquoted data: zsv fast --parallel 0.008s (14.29 GB/s) vs DuckDB default 0.085s, DuckDB QUOTE='' (no quote recognition) 0.049s, and single-threaded Polars 0.092s (\~10.6x vs DuckDB default, \~11.5x vs Polars, derived from page data); single-threaded zsv fast 0.023s vs DuckDB 1-thread QUOTE='' 0.112s. select on unquoted: zsv fast --parallel 0.036s vs DuckDB 0.110s and Polars 0.410s; single-threaded zsv fast (0.097s) is slower than xan (0.077s). The memory claim (1.5MB footprint, 52x smaller than DuckDB, 324x smaller than Polars, single-threaded) is on app/benchmark/README.md, not on the results page. |
| **Workload** | count (row counting) and select (full parse + CSV re-output) on four synthetic 500000-row x 20-col datasets (\~118-127MB: unquoted, \~2% sparse-quoted, \~20% RFC-4180 quoted, \~27% nonstandard mid-cell quotes), best-of-5, single- and multi-threaded, via app/benchmark/bench_quoting.sh; the 433MB worldcitiespop setup is described separately in app/benchmark/README.md |
| **Metric** | throughput |
| **Hardware** | Apple M3 Pro (darwin-arm64 results page); a separate linux-x86_64 page uses Intel Xeon Platinum 8488C but excludes DuckDB and Polars |
| **Adoption** | 397 stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/liquidaty/zsv) · [benchmark](https://github.com/liquidaty/zsv/blob/main/app/benchmark/results/benchmark-fast-parser-quoting-darwin-arm64-2026-03-26-1124.md) |

## Verdict

On zsv's first-party darwin-arm64 (Apple M3 Pro) results page, `zsv fast --parallel` counted rows on a 500,000x20 unquoted CSV in 0.008s (14.29 GB/s) versus 0.085s for multi-threaded DuckDB v0.10.2 (default settings), 0.049s for DuckDB with quote recognition disabled, and 0.092s for single-threaded Python Polars 1.35.2; the zsv binary's compiler and optimization flags are not stated on the page.

## Use it when

- Bulk row counting or column-selection/re-shaping over large CSVs (hundreds of MB+) where wall-clock throughput matters more than a dataframe API
- CSV known or verified to be RFC-4180-compliant, so `zsv fast --parallel` can be used safely
- Memory-constrained environments (embedded, containers, CI) — zsv's own README claims \~1.5MB single-threaded footprint vs 76MB (DuckDB) and 475MB (Polars) on the same task
- Need a small embeddable C library or a WebAssembly build rather than a full dataframe/query engine
- Need default handling of 'dirty' real-world CSV (stray unescaped quotes, ragged row lengths) without extra configuration

## Skip it when

- Input has nonstandard (non-RFC-4180) quoting and you want the fastest path — `zsv fast`, alone or with `--parallel`, produces incorrect output on such data per zsv's own benchmark page; must fall back to the slower `compat` parser
- You need SQL/dataframe operations, joins, or broader analytics — DuckDB and Polars are full engines, zsv's `sql` command is CSV-file-scoped
- Workload is `select`-style full-parse-plus-output on unquoted or sparsely-quoted data — sibling `xan`, single-threaded, beats single-threaded zsv there on zsv's own results page
- You need documented thread-safety for sharing one parser instance across threads; not stated in the API header — `--parallel` in the CLI partitions the file rather than exposing a safe shared-parser contract
- Non-C/C++ stack without willingness to wrap the C API or shell out to the CLI — only a community-maintained Ruby binding exists

## How it is fast

The default 'compat' parser is a byte-by-byte state machine; the optional `--parser fast` mode adds a SIMD path using branchless prefix-XOR carry propagation to track quote state across a buffer, available on aarch64 (NEON) and x86-64 (AVX2, SSE2). Either parser mode can be combined with `--parallel` to split input across threads/cores. The library also targets a small, roughly input-size-independent memory footprint rather than buffering whole rows or tables.

## Compared with alternatives

Pick zsv over xan/DuckDB/Polars when you want a small embeddable C library (or WASM target) rather than a broader dataframe/query engine, or specifically need row counting, where zsv wins across all quoting types on its own benchmark; pick xan instead for `select`-style full-parse-and-output on unquoted or sparsely-quoted data, where single-threaded xan beats single-threaded zsv on zsv's own results page.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (source-drop also possible; `./configure && make install` builds both; CLI extensions are plugin shared libraries) |
| **Dependencies** | none documented for the core parser/library; some CLI subcommands (`sql`, `jq`, `sheet`) bundle their own dependencies, not itemized in the README |
| **Minimum toolchain** | C, unspecified standard; GCC 11+ recommended (clang also supported), plus a basic unix toolchain (sh, make/gmake) |
| **Platforms** | macOS (clang/gcc), Linux (gcc), Windows (mingw64), BSD (gcc), and WebAssembly (emscripten); the SIMD fast parser additionally needs aarch64 NEON or x86-64 AVX2/SSE2, other targets use the scalar compat parser |
| **Thread safety** | not documented for a single zsv_parser instance shared across threads; `--parallel` in the CLI internally partitions the input across separate parser instances rather than one instance being called concurrently |
| **Drop-in for the baseline** | false — callback-driven C API and a separate CLI, not source- or API-compatible with DuckDB, Polars, or any existing CSV library |

## Gotchas

- `zsv fast`, with or without `--parallel`, gives incorrect output on non-RFC-4180 quoting (confirmed 'incorrect' on the nonstandard_quoted row of zsv's own results page); use `compat` for untrusted or dirty CSV
- DuckDB and Polars in zsv's benchmark were run with relaxed quote/newline handling ('handicaps' per app/benchmark/README.md) to be competitive, so the headline speedups overstate the gap at correctness-equivalent settings
- The much-cited memory numbers (1.5MB vs 76MB/475MB) come from a separate 433MB worldcitiespop run described in app/benchmark/README.md, not from the quoting benchmark page
- A use-after-free bug was found via ASan and fixed (issue #605, closed) — the project runs ASan in CI, but this indicates memory-safety has needed active fixing, not just inspection-level trust

## Caveats and trade-offs

First-party benchmark (liquidaty/zsv); the zsv binary's compiler and flags are not stated. The DuckDB version used is old (v0.10.2), and zsv's README reports \~100x DuckDB run-to-run variance with only minimum times used. Polars was run single-threaded via Python. The fastest SIMD 'zsv fast' parser gives incorrect output on nonstandard-quoted data (the compat parser is correct but slower). xan beats single-threaded zsv on select for unquoted and sparse data. DuckDB and Polars are broader dataframe engines.

The fast/SIMD parser mode produces incorrect output on nonstandard-quoted (non-RFC-4180) CSV, so full correctness requires falling back to the slower 'compat' parser; DuckDB and Polars were given 'handicaps' (relaxed quote/newline handling) in this comparison to make them competitive at all

## Maintenance

Actively maintained (last commit 2026-09-23, CI-gated) and MIT-licensed, so it's reasonable to depend on directly rather than vendor, though it has a small following (397 stars) and a small maintainer base.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party results page generated by the public app/benchmark/bench_quoting.sh, with CPU (Apple M3 Pro) and tool versions stated. The script takes a prebuilt zsv binary and no compiler or flags are stated, so it is not A.
- **Verifier notes:** Numbers are on the page, but the record paraphrased them loosely: 0.008s is 'zsv fast --parallel', the 0.049s DuckDB figure is the QUOTE='' variant, and the memory ratios and 433MB dataset come from app/benchmark/README.md. Corrected those. Metadata checked: MIT, 397 stars, last commit 2026-09-23.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/liquidaty/zsv>
  - <https://github.com/liquidaty/zsv/blob/main/app/benchmark/results/benchmark-fast-parser-quoting-darwin-arm64-2026-03-26-1124.md>
  - <https://github.com/liquidaty/zsv/blob/main/app/benchmark/results/benchmark-fast-parser-quoting-linux-x86_64-2026-03-26-1713.md>
  - <https://github.com/liquidaty/zsv/blob/main/app/benchmark/README.md>
  - <https://github.com/liquidaty/zsv/blob/main/app/benchmark/bench_quoting.sh>
  - <https://github.com/liquidaty/zsv/blob/main/app/benchmark/bench_fast_parser.sh>
- **Sources the enricher read:**
  - <https://github.com/liquidaty/zsv>
  - <https://github.com/liquidaty/zsv/blob/main/app/benchmark/results/benchmark-fast-parser-quoting-darwin-arm64-2026-03-26-1124.md>
  - <https://github.com/liquidaty/zsv/blob/main/app/benchmark/README.md>
  - <https://github.com/liquidaty/zsv/blob/main/BUILD.md>
  - <https://github.com/liquidaty/zsv/blob/main/include/zsv/api.h>
  - <https://github.com/liquidaty/zsv/issues/605>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/liquidaty/zsv`) · [data/wave3/enrich/raw/github_com_liquidaty_zsv.json](../../../data/wave3/enrich/raw/github_com_liquidaty_zsv.json) (enrichment confidence 0.6)

</details>
