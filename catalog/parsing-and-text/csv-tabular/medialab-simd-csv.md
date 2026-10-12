# simd-csv (Rust crate)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> SIMD-accelerated Rust CSV reader/writer family beating the csv crate on throughput, gains data-dependent.

| | |
|---|---|
| **Beats** | csv crate (docs.rs/csv, i.e. BurntSushi/rust-csv, the de facto standard Rust CSV library) |
| **Claimed result** | Up to \~6.0x faster (tweets.csv, split), \~4.0-4.8x (articles.csv), \~1.5-4.2x on most other files, \~1.1-1.4x on range.csv, and \~1.0-1.2x on quote-always.csv; worst-case.csv is \~1.0x (split), \~1.1x (zero_copy) and \~0.9x (copy, i.e. slightly slower). README: 'Sometimes you will go up to \~8 times faster, sometimes you will only go as fast as scalar code.' |
| **Workload** | Streaming CSV parsing including IO from SSD across 10 files (100MB-11GB, e.g. articles.csv 11GB/3M rows, tweets.csv 6.5GB/\~7M rows, worldcitiespop.csv 500MB, worst-case.csv 100MB), comparing Splitter (split), ZeroCopyReader (zero_copy) and Reader (copy) against the csv crate, on x86_64 with AVX2 |
| **Metric** | throughput |
| **Compiler and flags** | Rust, x86_64 with AVX2 (RUSTFLAGS='-C target-cpu=native' explicitly stated as not required) |
| **Adoption** | 19 stars |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/medialab/simd-csv) · [benchmark](https://github.com/medialab/simd-csv#regarding-performance) |

## Verdict

First-party README table compares simd-csv's three reader modes (Splitter/split, ZeroCopyReader/zero_copy, Reader/copy) against the docs.rs `csv` crate (v1.3.1 in dev-dependencies) parsing 10 files (100MB-11GB) streamed from SSD on x86_64 with AVX2, no CPU model given. Reported gains range from \~1.0x on worst-case.csv (100MB, split mode) up to \~6.0x on tweets.csv (6.5GB, split mode), with most files in the \~1.5-4.8x range and quote-heavy/low-entropy files (quote-always.csv, range.csv) near 1.0-1.4x.

## Use it when

- Large CSV/TSV files (hundreds of MB to multi-GB) streamed from disk where parse throughput matters
- Data with large records/cells and mostly non-quoted content (README: bigger cells/records give bigger wins)
- Just need record or line counts / positions: Splitter or LineReader avoid cell-level work entirely
- x86_64 (SSE2 baseline, AVX2 auto-detected), aarch64 (NEON), or wasm (simd128) targets
- Willing to depend on a young Rust crate (memchr as only hard dependency) and adapt to a non-csv-crate API

## Skip it when

- QUOTE_ALWAYS-style or heavily-quoted data, or single-column/short-cell data: gains shrink to \~1.0-1.4x (quote-always.csv, range.csv, worst-case.csv)
- Need the csv crate's full feature set, serde integration, or maximum flexibility/ergonomics
- CSV with lone-CR (old Mac style) line endings: only CRLF and LF are recognized, and leading CR bytes are silently trimmed
- Data where fields may contain a stray opening quote mid-field: the parser has no 'beginning of field' concept and can merge/misalign subsequent fields
- Risk-averse production use of a 19-star, single-maintainer crate not yet used outside its own xan CLI ecosystem

## How it is fast

Hybrid design: a traditional state machine for CSV structure, combined with memchr-style SIMD string searching for structural characters (comma, newline, quote) instead of byte-by-byte scanning. Unquoted runs use an amortized move-mask scan that reuses a mask across multiple matches instead of restarting per match; quoted runs instead use memchr's unrolled routines directly, because the authors found wider AVX2 registers hurt performance there. ByteRecord stores fields as ranges over the raw byte slice (rather than pure offsets) so the copying Reader can copy large runs of unquoted bytes at once instead of field-by-field.

## Compared with alternatives

Use simd-csv over the plain csv crate when writing Rust code that streams large, mostly-unquoted CSV/TSV from disk and you can tolerate its lower-level, non-drop-in API; use its sibling xan instead if you just want a ready-made CLI (xan is built by the same authors for the same use case) rather than a library to embed. The other siblings (go-simdcsv, Sep, zsv, cisv, zsv-ruby) target Go, .NET, C, Node and Ruby respectively and aren't relevant unless leaving the Rust ecosystem.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | memchr 2.7.6 (required); simdutf8 0.1.5 (optional, only for the `str` feature) |
| **Minimum toolchain** | Rust 1.81.0 (pinned in rust-toolchain.toml), edition 2021 |
| **Platforms** | x86_64 (SSE2 always, AVX2 via runtime detection), aarch64 (NEON), wasm (simd128), scalar/SWAR fallback elsewhere |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — explain: Reader/ReaderBuilder/ByteRecord mirror the csv crate's copying Reader closely, but ZeroCopyReader, Splitter, LineReader, TotalReader, Seeker and ReverseReader are lower-level APIs with no csv-crate equivalent |

## Gotchas

- Mid-field opening quotes can corrupt output: the parser has no 'beginning of field' state, so quotes anywhere except a field's true start can merge subsequent fields/rows
- Only CRLF and LF line terminators are handled; lone CR is not, and leading CR characters are trimmed from record starts as a documented tradeoff
- In single-column CSV, an empty cell must be written as a quoted empty string ("") — an unquoted blank line is treated as a skipped empty line, not an empty record
- Wider AVX2 registers are deliberately avoided for unquoted-data scanning because the authors measured them as slower than the amortized memchr approach used

## Caveats and trade-offs

First-party benchmark with no CPU model (only 'x86_64 with avx2 support') and only approximate ratios ('\~4.8x'); most benchmark data files (articles, tweets, mediapart) are not public; the gain is very data-dependent and the Reader (copy) path is \~0.9x on worst-case.csv.

Author's own README says explicitly not to expect the 16-32x gains of a true SIMD parser like simdjson; performance is very data-dependent (near-1x on worst-case/quote-always files); less flexible/user-friendly API than the csv crate; built specifically to serve the xan CLI tool's needs

## Maintenance

Actively maintained (last commit 2026-09-16, steady stream of open enhancement issues, no open bug-tagged issues found) but a tiny, single-maintainer project (19 stars); MIT-licensed and small enough to vendor/copy if the dependency risk is a concern.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table of approximate speedups vs the csv crate, only described as 'x86_64 with avx2 support' with no CPU model or build flags. A bench script exists (scripts/bench.sh: cargo build --release plus hyperfine), but most data files are private, so this falls short of A.
- **Verifier notes:** The table matches the README. Fixed the file-size range (smallest is 100MB worst-case.csv) and noted the \~0.9x copy-mode case. RUSTFLAGS note in compiler_and_flags is a general build remark from the README, not the benchmark's stated flags. Metadata checked: MIT, 19 stars, last commit 2026-09-16.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/medialab/simd-csv>
  - <https://github.com/medialab/simd-csv#regarding-performance>
  - <https://github.com/medialab/simd-csv/blob/master/scripts/bench.sh>
- **Sources the enricher read:**
  - <https://github.com/medialab/simd-csv>
  - <https://github.com/medialab/simd-csv#regarding-performance>
  - <https://github.com/medialab/simd-csv/blob/master/Cargo.toml>
  - <https://github.com/medialab/simd-csv/blob/master/rust-toolchain.toml>
  - <https://github.com/medialab/simd-csv/blob/master/scripts/bench.sh>
  - <https://github.com/medialab/simd-csv/blob/master/src/lib.rs>
  - <https://github.com/medialab/simd-csv/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/medialab/simd-csv`) · [data/wave3/enrich/raw/github_com_medialab_simd_csv.json](../../../data/wave3/enrich/raw/github_com_medialab_simd_csv.json) (enrichment confidence 0.55)

</details>
