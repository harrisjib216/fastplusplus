# qsv

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> CLI data-wrangling toolkit that computes CSV summary stats far faster than pandas describe, no DataFrame required.

| | |
|---|---|
| **Beats** | pandas read_csv / pandas .describe()-style stats |
| **Claimed result** | 75x faster (pandas 12s vs qsv &lt;0.16s); 6x faster with `stats --everything` (2s) |
| **Workload** | Computing summary statistics (`qsv stats`) on a 124MB, 2.7M-row CSV, compared to pandas computing the same stats |
| **Metric** | throughput |
| **Adoption** | 3.8k stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/dathere/qsv) · [benchmark](https://github.com/dathere/datapusher-plus/discussions/15) |

## Verdict

On a 124MB, 2.7M-row CSV, qsv's default `stats` finished in under 0.16s versus pandas computing comparable stats in 12s (75x faster), and `stats --everything` (48 measures) took 2s (6x faster); these are the maintainer's own numbers from an April 28, 2022 GitHub Discussion post, with no hardware or compiler flags disclosed for that specific comparison (a separate footnote's 22.4s/Ryzen 7 4800H figure is for a different, larger NYC-311 run with no pandas comparison).

## Use it when

- One-off or scripted CSV summary stats / type inference from shell pipelines, Makefiles, or CI, without spinning up Python or pandas.
- You can build a `qsv index` for the file first (or set QSV_AUTOINDEX_SIZE) to unlock multithreaded stats, frequency, split, and instant count/slice/sample.
- You need guaranteed, deterministic type inference per column rather than pandas' best-effort dtype guessing.
- Large CSVs (hundreds of MB to tens of GB) where you want the default 'streaming' stats in constant memory rather than a full in-memory DataFrame.
- Batch/ETL contexts where a standalone compiled CLI (or its MCP server) is an acceptable dependency.

## Skip it when

- You need the result as an in-memory DataFrame/array for further Python computation — qsv emits CSV/JSON text, not a DataFrame object.
- Your CSVs are malformed or non-UTF-8: `stats` explicitly assumes well-formed, valid UTF-8 input and warns of undefined behavior otherwise; run `qsv validate` first.
- You need the full 48-statistic 'advanced' set (median, quartiles, mode, cardinality) on very large files without accepting an extra chunked, higher-memory pass.
- Team is Python-only and can't add a separate compiled binary/CLI step to the pipeline.
- You want a reproducible, modern-hardware performance claim: the 75x/6x numbers are from an April 2022 maintainer GitHub Discussion post, not a benchmark suite, with no hardware or compiler flags given for that specific run.

## How it is fast

`stats` streams the file once and computes its default statistic set (sum, min/max, mean, stddev, sparsity, etc.) in constant memory instead of materializing a DataFrame, and it multithreads per-column work once a `qsv index` (.idx) exists for the file. The non-streaming statistics that need the whole dataset (median, quartiles, mode, cardinality) use a memory-aware chunking algorithm rather than a naive full load. `stats` also assumes the CSV is well-formed and UTF-8, letting it skip repeated UTF-8 validation and bounds checks that a general-purpose parser like pandas' would perform.

## Compared with alternatives

Pick qsv over xan, zsv, or DuckDB's CSV reader when you want one CLI with dozens of built-in wrangling verbs (join, dedupe, geocode, schema/JSON-Schema inference, Polars-backed SQL) beyond just fast parsing or stats. Pick zsv or xan instead when raw parse/read throughput is the goal — zsv's own darwin-arm64 shootout benchmarks it directly against qsv (and xsv, xan) and shows it ahead on parsing speed.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for prebuilt binaries; building from source pulls in many optional, feature-gated crates (Polars, DuckDB-backed commands, Luau, geocoding databases, etc.) — the project's Cargo.toml notes `cargo install qsv` from crates.io is not currently supported |
| **Minimum toolchain** | Rust 1.98 (edition 2024), per Cargo.toml and the README badge |
| **Platforms** | Linux (x86_64 GNU/musl, aarch64 GNU), macOS (Apple Silicon), Windows (x86_64 MSVC, aarch64), plus IBM Power (PowerPC64 LE) and IBM Z (s390x); prebuilt x86_64 binaries deliberately skip CPU-specific optimizations to avoid SIGILL faults across CPU variants |
| **Thread safety** | not documented as a library API (qsv is a CLI process, not embeddable); internally, `stats`/`frequency`/`split`/`schema`/`tojsonl` multithread per-column/per-chunk work once an index is built |
| **Drop-in for the baseline** | partial — explain: same problem (CSV summary statistics + type inference) as pandas describe, but a different interface entirely: a CLI subcommand you shell out to or pipe through, not a Python API returning a DataFrame |

## Gotchas

- `stats` assumes a well-formed, UTF-8 CSV and skips validation for speed; malformed input is explicitly undefined behavior — run `qsv validate` first if unsure.
- Multithreading, instant `count`/`slice`/`sample`, and faster `stats`/`frequency`/`schema`/`split` only kick in once you build a `qsv index`; without one, stats runs single-threaded and streaming.
- Only the default 'streaming' statistics run in constant memory; median, quartiles, mode/antimode, and cardinality require loading more data (via a memory-aware chunker, not the naive whole file) and must be enabled explicitly (e.g. `--everything`).
- GitHub's UI reports the license as NOASSERTION; the repo's own LICENSE-MIT, COPYING, and Cargo.toml confirm MIT-only licensing since v21.1.1 (dual MIT/Unlicense in v21.1.1 and earlier).

## Caveats and trade-offs

The numbers come from the qsv maintainer in a GitHub Discussion (2022-04-28), not a blog post or paper, so they reflect a 2022-era qsv. Hardware and compiler flags are not given for the 75x figure (its footnote only cites the qsv whirlwind tour), and the ratio is above 50x, so the tier is capped at C. The Ryzen 7 4800H / 32GB footnote belongs to a separate 22.4s NYC-311 run (27.8M rows, 16GB) with no pandas comparison. qsv began as a fork of BurntSushi/xsv but GitHub no longer tracks it as a fork. GitHub reports the license as NOASSERTION, but LICENSE-MIT and COPYING say qsv is MIT-only after v21.1.1 (v21.1.1 and earlier were also under the Unlicense).

CLI tool, not an in-process library like pandas; streaming design gives constant memory footprint but requires shelling out; users must learn qsv's own command set.

## Maintenance

Actively maintained (commits as recently as today) and MIT-licensed since v21.1.1; ships as prebuilt binaries for all major OS/arch combinations or builds from a Rust 1.98 source tree, making it straightforward to vendor as a standalone CLI tool.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** Maintainer jqnatividad's discussion (2022-04-28): 'pandas took 12 seconds to calculate statistics qsv computed in less than 0.16 seconds (75x faster) for a 124MB, 2.7M row CSV file', with --everything taking 2s (6x). No hardware for that figure and no code, and &gt;50x with unstated flags, so C.
- **Verifier notes:** Numbers are verbatim on the page. License confirmed as MIT from LICENSE-MIT, COPYING and Cargo.toml despite gh's NOASSERTION; 3,796 stars and a last commit of 2026-09-25 are confirmed.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dathere/datapusher-plus/discussions/15>
  - <https://github.com/dathere/qsv>
- **Sources the enricher read:**
  - <https://github.com/dathere/qsv>
  - <https://github.com/dathere/qsv#readme>
  - <https://github.com/dathere/qsv/blob/master/Cargo.toml>
  - <https://github.com/dathere/qsv/blob/master/LICENSE-MIT>
  - <https://github.com/dathere/qsv/blob/master/COPYING>
  - <https://github.com/dathere/qsv/blob/master/docs/PERFORMANCE.md>
  - <https://github.com/dathere/qsv/blob/master/docs/help/stats.md>
  - <https://github.com/dathere/datapusher-plus/discussions/15>
  - <https://github.com/dathere/qsv/issues?q=stats+performance>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/dathere/qsv`) · [data/wave3/enrich/raw/github_com_dathere_qsv.json](../../../data/wave3/enrich/raw/github_com_dathere_qsv.json) (enrichment confidence 0.65)

</details>
