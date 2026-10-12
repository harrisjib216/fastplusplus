# hck (Rust cut replacement)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT OR Unlicense` · 🟢 active

> Rust cut(1) clone with regex or literal delimiters and column reordering; 4.6-6.3x faster than GNU cut 8.30 field extraction.

| | |
|---|---|
| **Beats** | GNU cut 8.30 (coreutils, C), also mawk 1.3.4 |
| **Claimed result** | README hyperfine means (7M-line CSV): hck -Ld, 1.198 s, hck -d, 1.649 s vs GNU cut -d, 7.541 s (6.3x and 4.6x), mawk 1.3.4 4.993 s, tsv-select 1.702 s, xsv 5.693 s, choose 4.285 s. Independent run in the riquito/tuc README (public benchmark.sh, hardware and cut version unstated): hck -Ld, 1.276 s vs system cut 5.726 s (about 4.5x, derived from page data). |
| **Workload** | Selecting fields 1, 8 and 19 from the 7-million-line UCI all_train.csv with a single-character ',' delimiter, and from a derived file whose fields are separated by three spaces (benchmark.sh, hyperfine --warmup 3 -m 5, output to /dev/null). hck memory-maps the input by default; --no-mmap rows are also reported. |
| **Metric** | throughput |
| **Hardware** | Ubuntu 20, AMD Ryzen 9 3950X 16-core, 64 GB DDR4, NVMe |
| **Compiler and flags** | Not stated for the benchmark run. Repo Cargo.toml release profile: lto = "fat", codegen-units = 1; the README says release binaries are built with profile-guided optimisation and the justfile's install-native target adds -C target-cpu=native, but which hck build was timed is not said. xsv 0.13.0, choose 1.3.2 and tsv-utils 2.2.0 (ldc2) 'compiled locally with optimizations'; GNU cut 8.30 and mawk 1.3.4 are Ubuntu 20 packages (distro build flags, not stated on the page). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | no |
| **Adoption** | 745 stars; 69,173 crates.io downloads; packaged for Homebrew, conda-forge, MacPorts and as a .deb |
| **Last commit** | 2026-06-15 |
| **Links** | [repository](https://github.com/sstadick/hck) · [benchmark](https://github.com/sstadick/hck) |

## Verdict

On a Ryzen 9 3950X under Ubuntu 20 (hyperfine, 3 warmups, 5 runs, output to /dev/null), extracting fields 1, 8 and 19 from the 7M-line UCI all_train.csv took hck -L 1.198 s and hck regex mode 1.649 s against 7.541 s for Ubuntu's GNU cut 8.30 (6.3x and 4.6x), with the hck build flags and toolchain unstated. An independent table in the tuc README (machine and cut version unstated) shows the same order: hck -Ld, 1.276 s vs system cut 5.726 s, about 4.5x (derived from page data).

## Use it when

- Pulling a few fields out of large single-byte-delimited files (CSV/TSV logs, multi-GB exports) on Linux, where the -L fast path ran 1.2 s against 7.5 s for GNU cut 8.30 on 7M lines.
- Splitting on runs of spaces, multi-character literals ('\$;\$') or regexes without a tr -s pipe, for example ps aux | hck -f2,1,3-.
- Selecting or excluding columns by header name or header regex, or emitting columns in a different order than the input, which cut cannot do.
- Reading gzip/zstd/xz inputs or writing tabix-indexable BGZF output in the same step (-z / -Z).

## Skip it when

- Real CSV with quoted fields or embedded delimiters: hck splits on every delimiter occurrence (stated non-goal); use xsv or another CSV parser.
- Scripts that rely on cut semantics: a line without the delimiter is treated as a single field 1, so it is printed whole only when field 1 is selected (cut prints it whatever the selection, unless -s); the output delimiter defaults to tab rather than the input delimiter; there are no byte/character modes.
- Regex delimiters for speed: hck -d'\s+' (10.0 s) and -d'[[:space:]]+' (8.6 s) were slower than tr -s ' ' | cut (7.5 s) in its own table. GNU coreutils 9.11+ also has cut -w for blank-run fields, and the next release's NEWS says cut -f -w is up to 10x faster.
- Column reordering at full speed: any -f order other than ascending disables the fast path (tuc's table: hck -Ld, -f1,19,8 1.465 s vs 1.276 s in order).
- macOS and 32-bit targets get no mmap (disabled in mmap.rs), so the headline mmap rows do not apply there.

## How it is fast

With -L and a single-byte delimiter, fields in ascending order and a one-byte line terminator, hck runs a fast path. memchr2 scans for the separator and the newline in one SIMD pass, and once the rightmost requested field is found it jumps to the next newline with a single memchr. Files are memory-mapped by default (ripgrep's MmapChoice logic) and otherwise read through a ripgrep-derived line buffer. Other modes split each line with bstr substring search or the Rust regex crate. Release builds use fat LTO, codegen-units=1 and PGO, which the README credits with 5-30%.

## Compared with alternatives

Against tuc, which measured 1.080 s to hck's 1.276 s on the same 1,8,19 task and is GPL-3.0, pick hck when you need MIT/Unlicense terms, header-name/regex column selection, or -z/-Z compression handling. Against eBay tsv-utils' tsv-select (1.702 s in hck's table) and uutils cut (1.764 s in tuc's table), hck is faster for plain single-byte extraction but is not a TSV toolkit.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | regex, memchr, bstr, memmap2, ripline, grep-cli (external decompressor binaries for -z on non-.gz files), gzp with zlib-ng and libdeflate (C) for -Z, flate2 (zlib-ng-compat), clap |
| **Minimum toolchain** | Rust edition 2024 with let-chains (Rust 1.88+ in practice); no rust-version declared |
| **Platforms** | Linux, macOS (no mmap) and Windows release binaries; the PGO plus native just recipe does not work on Windows; mmap only on 64-bit |
| **Thread safety** | Single-threaded field parsing; only -Z output compression uses worker threads (-t) |
| **Drop-in for the baseline** | partial: same -f/-d range syntax, but -d is a regex unless -L is given, the output delimiter is tab unless -D or -I is set, lines lacking the delimiter are treated as field 1 instead of echoed whole, and -b/-c/-s/--complement are missing |

## Gotchas

- Likely edge-case bug (code reading, not executed): the single-byte fast path (SingleByteDelimParser::fill_line, used for -L plus a one-byte delimiter in both mmap and --no-mmap modes) requires the buffer to end in a newline. When the last line has no trailing '\n', memchr finds no newline and the parser returns io::ErrorKind::InvalidData, so hck logs an error and exit(1)s. The last line is dropped and unflushed BufWriter output may be lost. Every test writes files with writeln!, so this case is untested.
- Headline cut ratio is against GNU cut 8.30 (2018), whose field loop reads byte by byte with getc. hck also stops scanning each line after field 19, and output delimiters differ (tab vs comma) although all output goes to /dev/null. The cut row is noisy (6.827-9.769 s), and at its minimum the gap is about 5.7x (derived from page data). mawk 1.3.4 (4.993 s) also beat cut.
- mmap is not always the faster default: in issue #42 a user measured the literal path at 11.69 s with mmap vs 7.48 s with --no-mmap on a 10 GB TSV. Before v0.6.6 (Sep 2021) the literal fast path kept scanning past the rightmost field and lost to the regex path.
- The multi-character comparison pits one tool against a pipeline: hck inside the same tr -s pipeline takes 6.171 s against 7.471 s for tr | cut, and tuc's README measured 5.266 vs 5.310 s, so the 4.3x headline mostly measures avoiding tr.

## Known shortcomings

- No compiler or flags stated for either side; the win comes from memchr plus mmap against GNU cut 8.30's per-byte getc loop, not the language; regex-delimiter mode is slower than tr | cut (10.014 vs 7.471 s) and the multi-character 4.3x mostly comes from avoiding tr.
- Likely bug (code reading, not run): the -L single-byte fast path returns InvalidData when the last line lacks a newline, exits 1 and drops the last line (not behind the benchmark numbers). The 4.3x multi-character headline mostly avoids tr; mmap is slower than --no-mmap in issue #42; GNU coreutils 9.11+ adds cut -w. Independent run in the riquito/tuc README (public benchmark.sh): hck -Ld, 1.276 s vs system cut 5.726 s (about 4.5x), hardware and cut version unstated.

## Caveats and trade-offs

First-party; the README says the benchmarks are 'not meant to be an authoritative set' and only show hck is 'in the same ballpark'. The script (benchmark.sh) and data link are public, but toolchain versions, the hck build mode (release, PGO or native) and the Ubuntu build flags of cut and mawk are unstated, so equal optimisation cannot be shown. GNU cut 8.30 dates from 2018 and processes fields byte by byte with getc; newer coreutils releases were not tested. The cut row has a wide spread (6.827-9.769 s); using its minimum the gap is about 5.8x (derived from page data); hck --no-mmap literal mode is 1.349 s. Output formats differ (hck writes tab-separated output by default, cut keeps the comma), though both go to /dev/null. The multi-character comparison pits a single tool against a pipeline: hck -Ld'   ' 1.718 s vs tr -s ' ' | cut 7.471 s (4.3x), but hck in the same tr pipeline takes 6.171 s, so most of that gap is avoiding tr; hck's headline regex-delimiter mode is slower than tr | cut on this input (-d'\s+' 10.014 s, -d'[[:space:]]+' 8.597 s vs 7.471 s). mawk (4.993 s) also beats cut here. Not a language-level result: same_algorithm false. [retier] Likely bug (code reading): the -L single-byte fast path returns InvalidData when the last line lacks a newline, exits 1 and drops the last line (not behind the benchmark numbers). The 4.3x multi-character headline mostly avoids tr; mmap is slower than --no-mmap in issue #42; GNU coreutils 9.11+ adds cut -w.

Regex or literal multi-character delimiters and column reordering that cut lacks; offers memory-mapped input (the --no-mmap rows are 13% to 28% slower); regex delimiters are about 4x to 6x slower than literal ones.

## Maintenance

Maintenance mode: since 2024 the commits are dependency, toolchain and fmt bumps, the latest being v0.11.6 on 2026-06-15. It is MIT OR Unlicense, about 69k crates.io downloads, and packaged for Homebrew, conda-forge, MacPorts, NetBSD and as a .deb.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** The README benchmark tables (driven by benchmark.sh in the repo root: hyperfine --warmup 3 -m 5) time hck against GNU cut 8.30 and mawk 1.3.4 on a stated Ryzen 9 3950X, but the Rust toolchain, the hck build actually timed (plain release, PGO or target-cpu=native) and the distro build flags of cut and mawk are not stated; first-party, so C rather than A.
- **Retiered** C to B: Enricher: the riquito/tuc README's public benchmark.sh run (independent of hck) measures hck -Ld, at 1.276 s against system cut 5.726 s, about 4.5x, confirming the first-party ballpark; hardware and cut version unstated, so B not A. C to B.
- **Verifier notes:** Numbers match the README exactly; tier C stays because compiler and flags are missing for both sides. The win is memchr plus mmap against GNU cut 8.30's per-byte getc loop, so it is an implementation win over an old cut release, and hck's regex-delimiter mode loses to tr | cut. why_faster filled from the sources.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-13 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/sstadick/hck>
  - <https://github.com/sstadick/hck/commits>
  - <https://github.com/sstadick/hck/tree/master/src/lib>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/README.md>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/justfile>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/src/lib/single_byte_delim_parser.rs>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/src/lib/core.rs>
  - <https://raw.githubusercontent.com/coreutils/coreutils/v8.30/src/cut.c>
  - <https://crates.io/api/v1/crates/hck>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/README.md>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/justfile>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/src/lib/mod.rs>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/src/lib/core.rs>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/src/lib/single_byte_delim_parser.rs>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/src/lib/line_parser.rs>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/src/lib/field_range.rs>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/src/lib/mmap.rs>
  - <https://raw.githubusercontent.com/sstadick/ripline/HEAD/src/line_buffer.rs>
  - <https://github.com/sstadick/hck/issues?q=is%3Aissue>
  - <https://github.com/sstadick/hck/issues?page=2&q=is%3Aissue>
  - <https://github.com/sstadick/hck/issues/12>
  - <https://github.com/sstadick/hck/issues/42>
  - <https://github.com/sstadick/hck/commits>
  - <https://crates.io/api/v1/crates/hck>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/README.md>
  - <https://raw.githubusercontent.com/coreutils/coreutils/master/NEWS>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/sstadick/hck`) · [data/wave14/enrich/raw/github_com_sstadick_hck.json](../../../data/wave14/enrich/raw/github_com_sstadick_hck.json) (enrichment confidence 0.75)

</details>
