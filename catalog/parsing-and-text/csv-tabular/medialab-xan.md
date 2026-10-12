# xan

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Unlicense` · 🟢 active

> CLI CSV toolkit with a SIMD parser and built-in expression language; faster single-threaded select than xsv, Polars, DuckDB.

| | |
|---|---|
| **Beats** | BurntSushi/xsv and Python Polars/DuckDB CSV readers (independent comparison; xan itself targets csvkit-style CSV toolkits) |
| **Claimed result** | On zsv's darwin-arm64 shootout (Apple M3 Pro, xan 0.54.1, 500000x20 datasets, best-of-5), xan select takes 0.077s (unquoted) and 0.081s (sparse_quoted). Comparisons: xsv 0.189s/0.195s (\~2.4x, derived from page data); single-threaded Polars 0.410s/0.408s; DuckDB default 0.110s/0.105s; single-threaded zsv fast 0.097s/0.105s. That makes xan the fastest single-threaded tool there, not the fastest overall: zsv fast --parallel (0.036s/0.035s), zsv compat --parallel (0.044s/0.047s) and, on sparse_quoted, DuckDB QUOTE='' (0.066s) are faster. xan count on unquoted: 0.023s, tied with zsv fast, vs xsv 0.087s. xan is N/A (incorrect output) on nonstandard_quoted data. On the Linux Xeon Platinum 8488C page (xan 0.56.0), xan select on unquoted takes 0.082s vs xsv 0.600s. |
| **Workload** | Same zsv-authored count/select benchmark: 'select' operation on unquoted and sparsely-quoted \~118MB CSV data (500000 rows x 20 cols) |
| **Metric** | throughput |
| **Hardware** | Apple M3 Pro (darwin-arm64 results page); a separate linux-x86_64 page uses Intel Xeon Platinum 8488C (zsv/xsv/xan/qsv only, no DuckDB/Polars) |
| **Adoption** | 4.5k stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/medialab/xan) · [benchmark](https://github.com/liquidaty/zsv/blob/main/app/benchmark/results/benchmark-fast-parser-quoting-darwin-arm64-2026-03-26-1124.md) |

## Verdict

On zsv's own darwin-arm64 shootout (Apple M3 Pro, xan 0.54.1, csv crate-based xsv as baseline, 500000x20-row unquoted/sparse-quoted data, best-of-5), xan's `select` ran 0.077s/0.081s versus xsv's 0.189s/0.195s (\~2.4x), beating single-threaded Polars (0.410s/0.408s) and default DuckDB v0.10.2 (0.110s/0.105s), but losing to zsv fast/compat in --parallel mode and to DuckDB with QUOTE='' on sparse-quoted data; the xan binary's compiler flags are not stated.

## Use it when

- Ad hoc CLI exploration and filtering of large (GB-TB) CSV files where you'd otherwise reach for xsv or csvkit
- Unquoted or sparsely-quoted CSV where single-threaded select/count throughput matters (fastest single-threaded tool in the zsv shootout)
- Want stats, join, dedup, pivot, and format conversion in one CLI without leaving the shell for pandas/DuckDB
- Converting CSV to/from JSON, ndjson, Excel, Parquet, or numpy from the command line
- Already scripting with xsv and want a faster, more feature-rich drop-in CLI replacement

## Skip it when

- Need an embeddable Rust/Python library rather than a CLI binary; not documented as an embeddable API (use simd-csv or the csv crate directly instead)
- Data contains nonstandard-quoted CSV; xan produces incorrect output there per the wave3 verification pass
- Need the single fastest option regardless of thread count: zsv fast/compat with --parallel and DuckDB with QUOTE='' beat xan on the same benchmark
- Need a build with documented, reproducible compiler flags; the benchmarked xan binary's flags are unstated (evidence tier C)
- Want a minimal, small dependency footprint; xan bundles 60+ crates including Excel, Parquet, HTML, and Markdown parsers

## How it is fast

Core parsing goes through medialab/simd-csv, a separate SIMD-accelerated CSV parser crate, instead of a byte-at-a-time scalar reader like the csv crate xsv uses. Selected commands (e.g. the `parallel` subcommand and some stats/aggregation paths) multithread across cores. The moonblade expression language is evaluated directly by xan rather than by invoking an external scripting interpreter, cutting subprocess/interpreter overhead for row transforms.

## Compared with alternatives

Pick xan over qsv, zsv, or DuckDB/Polars when you want one feature-rich CLI (stats, join, expression language, multi-format conversion) rather than the single fastest parser; pick zsv (especially --parallel) or DuckDB's QUOTE='' path instead when raw select/count throughput is the only goal, and pick simd-csv directly if you want the SIMD parser as a Rust library dependency rather than a CLI tool.

## Integration

| | |
|---|---|
| **Form** | crate (binary via cargo install; not designed as an embeddable library) |
| **Dependencies** | 60+ crates, including ahash, aho-corasick, csv, calamine (Excel), comrak (Markdown), docopt, jiff, and medialab/simd-csv for the fast CSV path |
| **Minimum toolchain** | Rust 1.88.0, edition 2024 (per Cargo.toml) |
| **Platforms** | x86_64 (Linux gnu/musl, macOS, Windows msvc), aarch64 (macOS, Linux gnu); ppc64le only via unofficial conda-forge build, not CI-built |
| **Thread safety** | not documented as a library API; CLI exposes an explicit `parallel` subcommand for multithreaded batch runs |
| **Drop-in for the baseline** | partial — explain: CLI-compatible successor to xsv's command style and originally forked from it, but nearly entirely rewritten and not an API-level drop-in |

## Gotchas

- Produces incorrect output on nonstandard-quoted CSV, the same limitation zsv-fast has (per wave3 verifier notes)
- Cargo.toml licenses it "Unlicense OR MIT" (dual), though the catalog record lists Unlicense only
- The competitive benchmark numbers come from rival project zsv's own shootout script, not from xan's own README or docs
- Large dependency surface (Excel, Parquet, HTML, Markdown parsing all bundled) makes this a heavyweight binary, not a minimal tool

## Caveats and trade-offs

Evidence comes from a competitor's (liquidaty/zsv) own shootout, not an independent well-known suite; the xan binary's build/compiler flags are not stated. Per its README, xan is originally a fork of BurntSushi/xsv, nearly entirely rewritten and not marked as a GitHub fork, so the xsv baseline is its own ancestor. The DuckDB version used is old (v0.10.2) and Polars was run single-threaded. xan produces incorrect output on nonstandard-quoted data. xan's parser is medialab/simd-csv (a separate record).

xan's win is workload-specific (only on unquoted/sparsely-quoted data for 'select'); it produces incorrect output on nonstandard-quoted CSV, same limitation zsv-fast has; xan's own README/docs do not present this benchmark themselves

## Maintenance

Actively maintained (last commit 2026-09-23, 4.5k stars) and Unlicense-licensed per the catalog record (Cargo.toml also permits MIT), so it is safe to install via cargo/brew/pacman/nix — but it ships as a CLI tool, not a library, so "copyable" usability applies to its command surface rather than embedding its source.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** The only numbers come from a competitor's vendor shootout (liquidaty/zsv app/benchmark/bench_quoting.sh), not a peer-reviewed paper or well-known independent suite, so B does not apply. Script, CPU (Apple M3 Pro) and xan version (0.54.1) are public, but the xan binary's compiler and flags are not stated, so it is not A.
- **Verifier notes:** The claim that xan is 'the fastest tool for select' was overstated: it is fastest only among single-threaded tools, and zsv --parallel variants beat it. Tier B-&gt;C because a competitor's vendor benchmark is not a well-known independent suite. Metadata checked: Unlicense (OSI-approved; no patent grant), 4527 stars, last commit 2026-09-23.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/medialab/xan>
  - <https://github.com/liquidaty/zsv/blob/main/app/benchmark/results/benchmark-fast-parser-quoting-darwin-arm64-2026-03-26-1124.md>
  - <https://github.com/liquidaty/zsv/blob/main/app/benchmark/results/benchmark-fast-parser-quoting-linux-x86_64-2026-03-26-1713.md>
  - <https://github.com/liquidaty/zsv/blob/main/app/benchmark/bench_quoting.sh>
  - <https://github.com/liquidaty/zsv>
- **Sources the enricher read:**
  - <https://github.com/medialab/xan>
  - https://github.com/medialab/xan (README via gh api repos/medialab/xan/readme)
  - https://github.com/medialab/xan/blob/main/Cargo.toml (via gh api repos/medialab/xan/contents/Cargo.toml)
  - https://github.com/medialab/xan (repo file tree via gh api repos/medialab/xan/git/trees/HEAD)
  - <https://github.com/liquidaty/zsv/blob/main/app/benchmark/results/benchmark-fast-parser-quoting-darwin-arm64-2026-03-26-1124.md>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/medialab/xan`) · [data/wave3/enrich/raw/github_com_medialab_xan.json](../../../data/wave3/enrich/raw/github_com_medialab_xan.json) (enrichment confidence 0.6)

</details>
