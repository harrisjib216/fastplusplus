# hist-rs (hist, Rust unique-line counter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Hash-counting Rust replacement for 'sort | uniq -c | sort -n'; 5.3x faster than the LC_ALL=C pipeline (first-party).

| | |
|---|---|
| **Beats** | Plain 'sort \| uniq -c \| sort -n' as found on PATH (the README calls it coreutils; on macOS the default sort and uniq are the BSD-derived system tools unless GNU coreutils shadows them; implementation and versions not stated), in the default locale and with LC_ALL=C; also uutils coreutils sort/uniq with --parallel 1 and an awk pipeline (awk implementation not stated; README links the gawk manual). |
| **Claimed result** | README table (MacBook M3 Pro, hyperfine): hist 231.5 ms vs naive 'sort \| uniq -c \| sort -n' 5637.6 ms (24.35x), with LC_ALL=C 1219.5 ms (5.27x), awk count pipeline 1265.4 ms (5.47x), uutils sort 3.84x. Independent run in issue #3 (pixelb, Linux GNU sort, LC_ALL=C, 10M records): hist 12.864 s vs 36.238 s, about 2.8x (derived from page data). |
| **Workload** | justfile: nucgen -n 1000000 -l 20 writes 1M FASTQ records, i.e. 4M lines: 1M unique '@seq.N' headers, 1M random 20-nt sequences (effectively all unique), 1M identical '+' lines and 1M identical 20-character '?' quality lines (nucgen src/main.rs and src/write.rs), so about 2M distinct lines out of 4M. Each tool reads the file on stdin and writes to a file; hyperfine --warmup=10 --shell=bash. Second benchmark (bench-stream) prints first occurrences only (hist -u). |
| **Metric** | throughput |
| **Hardware** | MacBook M3 Pro (README) |
| **Compiler and flags** | hist: Cargo.toml [profile.release] lto = true, codegen-units = 1, debug = false (default opt-level 3); .cargo/config.toml rustflags -C target-cpu=native; edition 2024; rustc version not stated. Baselines are prebuilt system or installed binaries with unknown versions and build flags. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Not stated in the README. Inference from Cargo.toml (hashbrown, bumpalo): hash-table counting over an arena instead of an O(n log n) sort of all lines. |
| **Adoption** | 120 stars; 1,318 crates.io downloads (hist-rs 0.1.8) |
| **Last commit** | 2025-12-08 |
| **Links** | [repository](https://github.com/noamteyssier/hist-rs) · [benchmark](https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/README.md) |

## Verdict

First-party hyperfine runs (10 warmups) on a MacBook M3 Pro over a 1M-record FASTQ (4M lines, about 2M distinct) from nucgen: hist 231.5 ms vs default-locale 'sort | uniq -c | sort -n' 5637.6 ms (24.35x), LC_ALL=C 1219.5 ms (5.27x), uutils sort --parallel 1 890.1 ms (3.84x) and awk 1265.4 ms (5.47x); dedup mode 180.6 ms vs awk '!seen[\$0]++' 1307.1 ms (7.24x). The sort, uniq and awk binaries' implementations and versions are not stated, and an independent Linux run in issue #3 puts the like-for-like (LC_ALL=C) gap near 2.8x.

## Use it when

- Histogram of repeated values (log fields, tokens, k-mers, FASTQ headers or sequences) where the distinct set fits comfortably in RAM.
- Replacing 'sort | uniq -c | sort -n' in shell pipelines when you only need counts ordered by abundance, not the stable tie order of sort.
- Count with filtering or normalisation in one pass (regex include, exclude or substitution before counting) instead of chaining grep and sed.
- Order-preserving dedup of a stream (-u) of plain-text lines that contain no commas, double quotes or carriage returns.

## Skip it when

- Inputs whose distinct lines may not fit in memory: everything goes into an in-memory arena and hash table with no spill to disk, while sort does an external merge and -S bounds its memory.
- Pipelines that parse uniq -c output: hist prints count&lt;TAB&gt;line through a CSV writer, so lines containing a tab, double quote or CR are quoted, and ties come out in hash order that can change between runs.
- Data that may not be valid UTF-8 (Latin-1 logs, binary records): writing a non-UTF-8 line returns an error and aborts the run.
- Very large single files on many cores: hist is single-threaded (multi-threading is open issue #16 and PR #17), while GNU sort uses several threads by default and cuniq has --threads and --memmap.
- CSV or FASTQ dedup with -u: see the quoting gotcha below.

## How it is fast

Every line goes through one hashbrown HashMap&lt;&[u8], usize&gt; lookup via the raw-entry API; a new line is copied once into a bumpalo arena, and only the distinct entries are sorted, by an integer count with sort_unstable. The pipeline it replaces sorts every input line (n log n string comparisons, locale collation by default), pipes them through uniq and sorts again, across three processes. Lines are read as raw bytes with bstr's for_byte_line, so there is no UTF-8 validation on input. The gain is algorithmic (hash aggregation instead of sort-based grouping), not a language effect.

## Compared with alternatives

Pick hist over huniq (12.16x slower on this workload) and cuniq (2.43x slower) for single-threaded in-memory counting sorted by abundance with regex prefiltering; pick cuniq for multi-gigabyte files where its --memmap and --threads modes matter, and runiq when dedup must run in bounded memory.

## Integration

| | |
|---|---|
| **Form** | binary (crate hist-rs on crates.io, binary name hist) |
| **Dependencies** | hashbrown 0.16, bumpalo 3, bstr 1, csv 1.4, regex 1.12, clap 4.5, anyhow |
| **Minimum toolchain** | Rust 1.88+ in practice (edition 2024 and let-chains in main.rs; no rust-version declared on crates.io) |
| **Platforms** | any platform Rust supports; no platform-specific code |
| **Thread safety** | single-threaded process |
| **Drop-in for the baseline** | partial: same counts as sort \| uniq -c \| sort -n, but a different output format (count&lt;TAB&gt;line, CSV quoting), unstable tie order, CR LF folded into LF and errors on non-UTF-8 lines |

## Gotchas

- Dedup mode quotes data: 'hist -u' writes each first-seen line through csv::Writer with the default ',' delimiter, so any line containing a comma, double quote, CR or LF is wrapped in double quotes with inner quotes doubled, and an empty line becomes "". Deduplicating a CSV file or real FASTQ (Phred+33 quality strings include ',' and '"') therefore changes the data. The benchmark input (nucgen headers, ACGT sequences, '+' and '?' quality strings) contains none of these bytes, so the published numbers are unaffected.
- Counting mode uses a tab-delimited CSV writer, so lines containing a tab or double quote are quoted; lines ending in CR LF and in LF are counted as the same line because bstr's for_byte_line strips both terminators.
- The headline 24.35x compares against sort in the default locale (export LC_ALL= then sort | uniq -c | sort -n); the final sort -n then orders about 2M count-1 ties by full-line locale collation, work hist does not do. With LC_ALL=C the gap is 5.27x, against single-threaded uutils sort 3.84x, and an independent run in issue #3 (pixelb, Linux GNU sort, LC_ALL=C, 10M FASTQ records) measured 12.864 s vs 36.238 s, about 2.8x (derived from page data).
- The repo's .cargo/config.toml adds -C target-cpu=native, but cargo install ignores project-level config, so 'cargo install hist-rs' as the README instructs produces a generic build; the README does not say which build was benchmarked.

## Known shortcomings

- The 24x mostly reflects the default-locale sort (5.27x with LC_ALL=C, 3.84x vs uutils); the input is 4M FASTQ lines with half being two repeated values, not 'almost all unique'; the gain is algorithmic; MIT only in Cargo.toml (LICENSE.md 404).
- Bug outside the benchmark: hist -u writes via csv::Writer with a ',' delimiter, so lines with a comma, quote or CR get quoted and empty lines become "" (CSV and real FASTQ dedup altered; the benchmark input is unaffected); counting mode quotes tab and quote lines, merges CRLF with LF and aborts on non-UTF-8. Independent run in issue #3 (pixelb, Linux GNU sort, LC_ALL=C, 10M records): 12.864 s vs 36.238 s, about 2.8x. cargo install ignores the repo's target-cpu=native.

## Caveats and trade-offs

Most of the headline 24x comes from locale-aware collation in the default-locale sort: with LC_ALL=C the gap is 5.27x and against uutils sort (single-threaded) 3.84x. The input is not 'almost all unique': half of its 4M lines are two values repeated 1M times each, the other half are unique, so the hash table holds about 2M keys. The speedup is algorithmic (hash counting with hashbrown over a bumpalo arena, then sorting only the distinct entries) against a three-process pipe that sorts every line; it is not a language-level effect. Outputs are not byte-identical: hist writes 'count&lt;TAB&gt;line' through a csv writer (lines containing tabs or quotes get quoted, non-UTF-8 lines error), ties come out in unstable order, and the awk row sorts descending. First-party, one machine, no baseline versions. No LICENSE file in the repo: MIT is declared only in Cargo.toml and on crates.io (0.1.8), and the README badge links a LICENSE.md that returns 404. Sibling tools huniq and cuniq are already listed separately in wave 14. [retier] hist -u writes via csv::Writer with a ',' delimiter, so lines with a comma, quote or CR get quoted and empty lines become "" (CSV and real FASTQ dedup altered; benchmark input unaffected); counting mode quotes tab and quote lines, merges CRLF with LF and aborts on non-UTF-8. cargo install ignores the repo's target-cpu=native.

Holds every distinct line in memory (a hash table), so memory grows with the number of unique lines; output order is by abundance rather than the stable sort order of uniq.

## Maintenance

Active through December 2025 (54 commits, 120 stars, hist-rs 0.1.8 on crates.io with 1,318 downloads, an open multi-threading PR #17); MIT is declared in Cargo.toml but the repo has no LICENSE file (the README badge links a missing LICENSE.md); fine as a CLI for in-memory counting, but -u mangles lines containing commas or quotes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** First-party hyperfine tables in the README with public commands (justfile bench and bench-stream recipes) and a named machine (MacBook M3 Pro), but the rustc version is not stated and the baseline sort, uniq and awk binaries have no stated implementation, version or build flags, so it falls short of A; no independent measurement.
- **Retiered** C to B: Enricher: an independent run in issue #3 by pixelb (Linux GNU sort, LC_ALL=C, 10M records: 12.864 s vs 36.238 s, about 2.8x) is a stated-setup measurement by a coreutils maintainer, so the LC_ALL=C comparison holds independently. C to B.
- **Verifier notes:** Numbers match the README exactly (the ratios are on the page, not derived). Main shortcomings for the record: the 24x is mostly the default-locale sort (5.3x with LC_ALL=C, 3.8x vs uutils), the workload is a FASTQ file in which half the lines are two repeated values, baseline tool implementations and versions are unstated, and the licence is declared only in Cargo.toml (no LICENSE file).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `baseline`, `compiler_and_flags`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-104 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/justfile>
  - <https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/LICENSE.md>
  - <https://github.com/noamteyssier/hist-rs>
  - <https://github.com/noamteyssier/hist-rs/commits>
  - <https://github.com/noamteyssier/hist-rs/tree/main/src>
  - <https://crates.io/api/v1/crates/hist-rs>
  - <https://crates.io/api/v1/crates/nucgen>
  - <https://raw.githubusercontent.com/noamteyssier/nucgen/HEAD/README.md>
  - <https://raw.githubusercontent.com/noamteyssier/nucgen/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/noamteyssier/nucgen/HEAD/src/write.rs>
- **Sources the enricher read:**
  - <https://github.com/noamteyssier/hist-rs>
  - <https://github.com/noamteyssier/hist-rs/commits>
  - <https://github.com/noamteyssier/hist-rs/issues?q=is%3Aissue>
  - <https://github.com/noamteyssier/hist-rs/issues/3>
  - <https://github.com/noamteyssier/hist-rs/issues/14>
  - <https://github.com/noamteyssier/hist-rs/issues/16>
  - <https://github.com/noamteyssier/hist-rs/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/justfile>
  - <https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/noamteyssier/hist-rs/HEAD/src/cli.rs>
  - <https://crates.io/api/v1/crates/hist-rs>
  - <https://raw.githubusercontent.com/BurntSushi/rust-csv/master/csv-core/src/writer.rs>
  - <https://raw.githubusercontent.com/BurntSushi/rust-csv/master/src/writer.rs>
  - <https://raw.githubusercontent.com/BurntSushi/bstr/master/src/io.rs>
  - <https://raw.githubusercontent.com/rust-lang/hashbrown/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/orlp/foldhash/master/README.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/noamteyssier/hist-rs`) · [data/wave14/enrich/raw/github_com_noamteyssier_hist_rs.json](../../../data/wave14/enrich/raw/github_com_noamteyssier_hist_rs.json) (enrichment confidence 0.75)

</details>
