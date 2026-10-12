# tuc (Rust cut replacement)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `GPL-3.0-or-later` · 🟢 active

> Rust cut alternative with reordering, negative indices and multi-character or regex delimiters; about 5x faster than the system cut on comma-split field extraction.

| | |
|---|---|
| **Beats** | the system cut binary (C; GNU or BSD and version not stated), also awk, uutils cut, hck and choose in the same table |
| **Claimed result** | README table means: tuc -d , -f 1,8,19 1.080 s vs system cut 5.726 s (5.30x), uutils cut 1.764 s, hck 1.276 s, choose 4.347 s, awk 35.852 s (33.2x); non-sequential fields 1.093 s vs cut 5.723 s (non-sequential order); multi-character delimiter (' '): tuc 1.464 s vs awk -F' ' 14.471 s (9.88x) and 'tr -s \| cut' 5.310 s (3.63x). With a regex delimiter (-e'\s+') tuc takes 9.870 s, no faster than hck (9.834 s). |
| **Workload** | Select fields 1, 8 and 19 (sequential and non-sequential order) from the first 1,000,000 lines of the UCI HEPMASS all_train.csv with a single-character delimiter, and from a multi-character-delimiter text file (data-multichar.txt), output to /dev/null (benchmark.sh, hyperfine --warmup 3 -m 5). |
| **Metric** | throughput |
| **Compiler and flags** | benchmark.sh runs 'cargo build --release'; Cargo.toml [profile.release] lto = true, codegen-units = 1, panic = 'abort', strip = 'debuginfo'; edition 2024, README says rustc &gt;= 1.85.0 is required (exact rustc version not stated); default features regex and fast-lane. The system cut and awk implementations, versions and build flags are not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | The README does not state a mechanism. Visible in the table and Cargo.toml: memory-mapped input (the --no-mmap rows are about 1.14x slower) and the memchr and bstr crates (agent observation, not a source statement). |
| **Adoption** | 821 stars, 16 forks; crates.io tuc 19,805 downloads; packaged in several distributions (repology badge) |
| **Last commit** | 2026-07-01 |
| **Links** | [repository](https://github.com/riquito/tuc) · [benchmark](https://raw.githubusercontent.com/riquito/tuc/HEAD/README.md) |

## Verdict

First-party hyperfine runs (3 warmups, at least 5 runs, output to /dev/null) select fields 1, 8 and 19 from HEPMASS all_train.csv: tuc 1.080 s vs the system cut 5.726 s (5.3x), with uutils cut at 1.764 s and hck -L at 1.276 s. On a three-space-delimited copy, tuc takes 1.464 s vs 5.310 s for 'tr -s | cut'; with a regex delimiter it ties hck. The run was on Linux (the mmap rows differ, and mmap is compiled out on macOS); the CPU, rustc version, cut and awk versions and the actual line count are not stated.

## Use it when

- Pulling a few leading columns out of large single-byte-delimited files (CSV without quoting, TSV, logs) passed as a file path on Linux, where the mmap fast lane applies.
- Splitting on a literal multi-character delimiter such as three spaces or '&lt;sep&gt;': 1.464 s versus 5.310 s for the 'tr -s | cut' pipeline in the README.
- Shell work that needs field reordering, negative indices (-f -1), ranges with fallbacks, templated output or JSON arrays, which cut cannot do.
- Keeping or dropping the first and last lines of a stream (-l 2:-2), or cutting arbitrarily long lines in bounded memory with -M (single-byte delimiter, ascending fields only).

## Skip it when

- Regex delimiters: tuc -e'\s+' (9.870 s) is no faster than hck -d'\s+' (9.834 s) and runs the general path, not the fast lane.
- Real CSV with quoted fields containing the delimiter: there is no CSV quoting support documented; use a CSV-aware tool.
- Scripts that expect POSIX cut semantics: the CLI differs (fields joined without a delimiter unless -j, fields printed in the order given, no --output-delimiter), so it is not a drop-in replacement.
- macOS: mmap is compiled out (cfg target_os = "macos"), so you get the --no-mmap path that was about 1.14x slower in the Linux table.
- GNU coreutils 9.11 (2026-04-20) and later added cut -w for blank-aligned fields, and the unreleased NEWS entry says 'cut -f -w' is up to 10x faster in uni-byte locales, so the 'tr -s | cut' baseline in the multi-character table is now dated.

## How it is fast

For a single-byte delimiter with plain field selection it takes a 'fast lane' (src/fast_lane.rs): bstr's for_byte_line finds line ends, memchr::memchr_iter (SIMD byte search) records each field's start offset in a reused Vec&lt;usize&gt;, and the scan stops at the last requested field, so the tail of the line is never examined for delimiters. Fields are written as slices straight into a 64 KiB BufWriter with no per-field allocation. When given a file path it memory-maps the input on non-macOS targets (memmap2), which its own table shows is about 1.14x faster than buffered reads; multi-character delimiters go through a precomputed memchr::memmem plan. The release profile uses LTO, codegen-units = 1 and panic = 'abort'.

## Compared with alternatives

Pick tuc over hck (sstadick/hck) for literal-delimiter extraction where its own table shows it 1.18x ahead (1.34x for reordered fields), or when you need templates, negative indices, JSON or line slicing. Pick hck for header-name field selection, compressed input, or regex delimiters, where the two tie. Use uutils coreutils cut (1.63x slower than tuc here) when you need cut's exact CLI.

## Integration

| | |
|---|---|
| **Form** | crate (installs the tuc binary; prebuilt binaries, Homebrew, MacPorts, AUR, openSUSE and a WASM playground; lib.rs exposes modules, but there is no documented library API) |
| **Dependencies** | anyhow, bstr, memchr, memmap2, pico-args, serde_json; regex optional (default feature) |
| **Minimum toolchain** | Rust 1.85 (edition 2024) |
| **Platforms** | any platform Rust targets; mmap only on non-macOS targets and only for file-path input; stdin uses a 64 KiB BufReader |
| **Thread safety** | single-threaded CLI; not applicable |
| **Drop-in for the baseline** | partial: covers cut -d/-f/-b/-c/-s/-z use cases, but the default output concatenates fields with no delimiter unless -j is passed, fields come out in the order requested, and option names differ (--complement is -m, no --output-delimiter; use -r) |

## Gotchas

- The benchmarked tuc commands ('tuc -d , -f 1,8,19') omit -j, so tuc prints the three fields concatenated with no separator while cut, hck and awk write delimiters. The outputs are not equivalent, and tuc writes fewer bytes. In the 'non sequential' table, cut -f1,19,8 prints fields in file order (POSIX cut ignores order) while tuc and hck reorder them.
- Harness: the README timings for the other tools nearly match hck's own README, which ran on the full 7M-line HEPMASS all_train.csv on a Ryzen 9 3950X (hck -Ld, 1.276 vs 1.198 s; choose 4.347 vs 4.285 s; hck -d'   ' 2.191 vs 2.180 s; hck -d'\s+' 9.834 vs 10.014 s). benchmark.sh keeps only the first 1,000,000 lines but never regenerates an existing tmp/data.csv. So either the tables were measured on a larger file than the script produces or the machine was about 7x slower; data size, hardware and the cut and awk versions are all unstated. Ratios within each table still compare like with like.
- benchmark.sh copies hck's command list, including two broken awk rows: -F'[:space:]+' lacks the outer brackets, so it splits on the characters ':', 's', 'p', 'a', 'c' and 'e' rather than whitespace, and '{print \$1, \$8 \$19}' is missing a comma and splits on default whitespace. The awk in the single-character table (35.852 s) is about 7x slower than mawk 1.3.4 at a similar volume in hck's table, so the 33x speedup over awk is against a slow, unnamed awk.
- Release 1.3.0 ignores a custom --fixed-memory size; the fix is only on unreleased master (March 2026). --bytes, and --lines with negative or unordered bounds, read the whole input into memory. Input is mapped with an unchecked unsafe Mmap::map, so the usual mmap hazard applies if the file is truncated while being read.

## Known shortcomings

- Hardware, rustc and cut version unstated; the win is memchr SIMD plus mmap, and uutils cut (Rust) is also 3.2x faster than GNU cut.
- Harness flaws: the tuc command omits -j, so its output (fields concatenated) differs from cut's, and in the non-sequential table cut prints file order. The timings match hck's README full 7M-line run on a Ryzen 9 3950X within about 5% (choose 4.347 vs 4.285 s, hck -d'\s+' 9.834 vs 10.014 s) although benchmark.sh keeps only 1M lines and never regenerates tmp/data.csv. Two awk rows copied from hck are broken (-F'[:space:]+' lacks the outer brackets; '\$8 \$19' is missing a comma); the 33x-vs-awk is against an unnamed awk about 7x slower than mawk at similar volume. The fixed-memory size is ignored in 1.3.0; GNU coreutils 9.11 added cut -w, so the 'tr -s | cut' baseline is dated.

## Caveats and trade-offs

First-party tables added to the README on 2025-09-11 (v1.3.0); the hardware, rustc version and the cut and awk implementations and versions are not stated (benchmark.sh uses GNU sed -i syntax, wget and the uutils 'coreutils' multicall binary, which suggests Linux and probably GNU cut, but this is not stated). Only the first 1,000,000 lines of HEPMASS all_train.csv are used and output goes to /dev/null, so write costs are excluded. cut cannot split on a multi-character delimiter, so that table compares against 'tr -s | cut' and awk pipelines. uutils cut (Rust) is also 3.2x faster than the system cut, and hck in literal mode is only 1.18x slower than tuc, so the gap is to the system cut's implementation rather than to C. With a regex delimiter (-e'\s+') tuc (9.870 s) is no faster than hck (9.834 s). Means of at least 5 runs after 3 warmups. [retier] The tuc command omits -j, so its output (fields concatenated) differs from cut's; in the non-sequential table cut prints file order. The timings match hck's README full 7M-line run (Ryzen 9 3950X) within about 5% although benchmark.sh keeps only 1M lines. Two awk rows copied from hck are broken (-F'[:space:]+' lacks the outer brackets; '\$8 \$19' is missing a comma); the 33x-vs-awk is against an unnamed awk about 7x slower than mawk. GNU coreutils 9.11 added cut -w, so the 'tr -s | cut' baseline is dated.

GPL-3.0-or-later (copyleft); not a drop-in cut (own CLI with ranges, negative indices, regex delimiters, JSON output); mmap input has the usual caveats on files that change while read.

## Maintenance

Last code change in March 2026 (unreleased fixes) and only Dependabot bumps since (last 2026-07-01); release 1.3.0 is from 2025-09-10. It is a widely packaged GPL-3.0-or-later CLI that is fine to install, but its source is not permissively licensed for vendoring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party hyperfine tables in the README with public benchmark code (benchmark.sh) and release-profile flags in Cargo.toml, but no CPU model, rustc version, or cut/awk implementation and version, so not A.
- **Verifier notes:** Confirm at C; every quoted number matches the README tables. Shortcomings: hardware, rustc and cut versions unstated, first 1M lines only, output to /dev/null, the win is memchr SIMD scanning plus mmap rather than the language (uutils cut, also Rust, is 1.63x slower than tuc and 3.2x faster than cut). hck (sstadick/hck) and uutils/coreutils are already catalogued.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-77 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/README.md>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/src/fast_lane.rs>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/src/read_utils.rs>
  - <https://github.com/riquito/tuc>
  - <https://github.com/riquito/tuc/commits>
  - <https://github.com/riquito/tuc/commits/master/README.md>
  - <https://github.com/riquito/tuc/tree/master/src>
  - <https://crates.io/api/v1/crates/tuc>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/README.md>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/src/fast_lane.rs>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/src/read_utils.rs>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/src/stream.rs>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/src/bin/tuc.rs>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/src/options.rs>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/src/cut_str.rs>
  - <https://raw.githubusercontent.com/riquito/tuc/HEAD/src/args.rs>
  - <https://raw.githubusercontent.com/riquito/tuc/72d8161/benchmark.sh>
  - <https://raw.githubusercontent.com/riquito/tuc/054f6dc/README.md>
  - <https://raw.githubusercontent.com/riquito/tuc/054f6dc/src/options.rs>
  - <https://github.com/riquito/tuc>
  - <https://github.com/riquito/tuc/tree/master/src>
  - <https://github.com/riquito/tuc/commits>
  - <https://github.com/riquito/tuc/commits/master/benchmark.sh>
  - <https://github.com/riquito/tuc/commits/master/src/options.rs>
  - <https://github.com/riquito/tuc/issues?q=is%3Aissue>
  - <https://crates.io/api/v1/crates/tuc>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/README.md>
  - <https://raw.githubusercontent.com/coreutils/coreutils/HEAD/NEWS>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/riquito/tuc`) · [data/wave14/enrich/raw/github_com_riquito_tuc.json](../../../data/wave14/enrich/raw/github_com_riquito_tuc.json) (enrichment confidence 0.6)

</details>
