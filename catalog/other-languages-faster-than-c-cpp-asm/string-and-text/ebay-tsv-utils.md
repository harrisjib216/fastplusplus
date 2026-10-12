# eBay TSV Utilities (D)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `D` · `BSL-1.0` · 🔴 abandoned

> D toolkit of single-purpose TSV tools (filter, select, join, summarize) that outruns awk, cut and datamash on multi-GB files.

| | |
|---|---|
| **Beats** | GNU awk 4.2.1, mawk 1.3.3, GNU cut 8.25 and GNU Datamash 1.3 (all C) |
| **Claimed result** | 2018 first-party study, Linux (16-CPU Intel Haswell 2095 MHz cloud machine), seconds, 10th percentile of 35 runs: numeric row filter tsv-filter 5.48 vs mawk 11.31 vs GNU awk 42.80 (about 2.1x and 7.8x, derived from page data); column selection (4.8 GB) tsv-select 4.79 vs mawk 9.51 vs GNU cut 14.46 (about 3.0x vs cut, derived); summary statistics tsv-summarize 15.78 vs GNU Datamash 48.51 (about 3.1x, derived); regex row filter tsv-filter 8.80 vs mawk 17.74 vs GNU awk 29.02, but xsv (Rust) 7.97 is faster; narrow-line column selection (86M short lines) GNU cut 5.60 beats tsv-select 8.26. MacOS (Mac mini, 2-core 3 GHz i7): numeric filter 3.35 vs mawk 15.06 vs GNU awk 24.25; narrow column selection tsv-select 10.18 vs GNU cut 10.65. Independent hck README (AMD Ryzen 9 3950X, hyperfine, comma-delimited 7M-line HEPMASS CSV): tsv-select v2.2.0 1.702 s vs GNU cut 8.30 7.541 s (about 4.4x, derived from page data; about 4.0x on min times 1.687 vs 6.827) and vs awk 4.993 s (about 2.9x, derived); hck itself is faster at 1.198 s. |
| **Workload** | Six command-line tasks on multi-GB delimited text: numeric row filter and regex row filter (4.8 GB / 2.7 GB), column selection (wide and narrow lines), file join, summary statistics, CSV-to-TSV; also compared with xsv (Rust) and csvtk (Go). |
| **Metric** | throughput |
| **Hardware** | 2018 study, Linux: 16 CPU Intel Haswell 2095 MHz, 32 GB RAM, Ubuntu 16.04 cloud machine; MacOS: Mac mini, 3 GHz Intel i7 (2 cores), 16 GB, MacOS 10.13.3. hck run: AMD Ryzen 9 3950X 16-core, 64 GB DDR4, NVMe, Ubuntu 20. |
| **Compiler and flags** | 2018 study: tsv-utils v1.1.19 prebuilt release binaries (LDC; the page credits LTO and PGO for the 2018 gains); GNU awk 4.2.1, mawk 1.3.3/1.3.4, GNU cut 8.25/8.29 and GNU Datamash 1.3 from standard package managers (build flags not stated). hck run: tsv-utils v2.2.0 compiled locally with ldc2 'with optimizations'; GNU cut 8.30 and mawk 1.3.4 from Ubuntu 20 (flags not stated). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | no |
| **Why it wins** | Author's stated reasons: straightforward D with avoidance of GC allocation, LDC link-time and profile-guided optimisation (2018 gain), TSV-only data model (no CSV escape handling, which the docs call computationally more expensive); the tools are single-threaded, so none of the gain is from parallelism. |
| **Adoption** | 1.5k stars, 84 forks; prebuilt Linux and macOS binaries |
| **Last commit** | 2021-06-13 |
| **Links** | [repository](https://github.com/eBay/tsv-utils) · [benchmark](https://github.com/eBay/tsv-utils/blob/master/docs/comparative-benchmarks-2018.md) |

## Verdict

In the April 2018 first-party study (v1.1.19 LTO+PGO binaries vs package-manager C tools, 10th percentile of 35 runs on a 16-CPU Haswell 2095 MHz Ubuntu 16.04 cloud VM), tsv-filter took 5.48 s vs mawk 1.3.3 11.31 s and GNU awk 4.2.1 42.80 s on a 4.8 GB numeric filter, tsv-select 4.79 s vs GNU cut 8.25 14.46 s, and tsv-summarize 15.78 s vs Datamash 1.3 48.51 s, while GNU cut won the narrow-line test and xsv the regex test. An independent hyperfine run in the hck README (Ryzen 9 3950X, Ubuntu 20) measured tsv-select v2.2.0 at 1.702 s vs GNU cut 8.30 at 7.541 s (min 6.827 s) and awk at 4.993 s on the 7M-line HEPMASS CSV.

## Use it when

- Repeated filtering, column selection, joins or per-column statistics over plain TSV files in the hundreds of MB to tens of GB on one machine, where awk or datamash pipelines are the bottleneck.
- Pipelines where field names in the header are easier to maintain than awk field numbers (\$4, \$16).
- Numeric row filters and summary statistics, where the 2018 Linux run shows about 2x over mawk 1.3.3, 7.8x over GNU awk and 3.1x over GNU Datamash.
- Converting messy CSV once (csv2tsv) and then working in escape-free TSV with the rest of the toolkit.
- x86-64 Linux or macOS hosts where the prebuilt LTO+PGO binaries can be dropped onto PATH.

## Skip it when

- Short lines or small files: GNU cut beat tsv-select on the 86M-line narrow test on Linux (5.60 vs 8.26 s) and on a 279 MB file in the 2017 study (0.99 vs 1.21 s).
- Pure column cutting where a newer specialist is available: hck (1.198 s) and tuc are faster than tsv-select (1.702 s) in hck's own run on the same file.
- Regex filtering, where xsv (Rust) was faster on both platforms in 2018 (7.97 vs 8.80 s Linux, 7.03 vs 8.28 s macOS).
- Real CSV with quoted delimiters or embedded newlines in every step: only csv2tsv understands CSV escapes; the other tools split blindly on the delimiter.
- Arbitrary per-row logic (computed columns, conditionals across many fields): there is no expression language, so awk or Miller remain necessary.

## How it is fast

Input goes through bufferedByLine, which rawReads 128 KB blocks and hands out line slices in place instead of copying each line; output goes through BufferedOutputRange, which batches writes into about 10 KB chunks before touching stdout (the author says output buffering gave the biggest gain on the narrow-line test). tsv-filter splits only up to the highest field a test references and runs a precompiled list of test closures; tsv-select uses InputFieldReordering plus template specialisation to drop branches from the inner loop. Prebuilt binaries are LDC builds with -O3 -boundscheck=off plus PGO and LTO extended into druntime and Phobos; the 2018 page lists LTO/PGO, output buffering and compiler improvements as the sources of the 7-64% gain over 2017. Everything is single-threaded.

## Compared with alternatives

Pick tsv-utils over hck or tuc when you need filtering, joins, sampling and statistics in one consistent header-aware toolkit, not only column cutting, where hck and tuc are faster; pick it over Miller 6 or awkrs when the job is a fixed filter or summary on large TSV and a scripting language is not needed.

## Integration

| | |
|---|---|
| **Form** | standalone executables (prebuilt tarballs, make, or dub) |
| **Dependencies** | none at run time (prebuilt Linux binaries statically link the C runtime); building needs a D compiler (DMD 2.088.1+ or LDC 1.18.0+; LDC 1.9.0+ for LTO/PGO) |
| **Minimum toolchain** | LDC 1.18.0 or DMD 2.088.1 (prebuilt v2.2.0 uses LDC 1.24.0); builds with current compilers are not documented |
| **Platforms** | Linux and macOS, x86-64 prebuilt only; no ARM64 assets (issue #357), v2.2.1 has no Linux assets (issue #349); Windows only via WSL or Docker (issue #317) |
| **Thread safety** | not applicable (single-threaded processes) |
| **Drop-in for the baseline** | partial — new command-line syntax (tsv-filter --gt 4:0.3, tsv-select -f 1,8,19); tsv-select covers cut -f usage, the others replace specific awk or datamash idioms rather than accepting their scripts |

## Gotchas

- Stricter than awk: tsv-filter aborts with 'Not enough fields in line' on short or blank lines (open issue #355 was trailing blank lines), throws when a numeric test hits a non-numeric field instead of treating it as 0, and the tools reject CRLF line endings.
- Speed depends on the build: source builds default to DMD without LTO/PGO, and the 2017 study shows DMD up to 2x slower than LDC (tsv-join 41.23 vs 20.78 s, csv2tsv 56.08 vs 27.41 s); use make DCOMPILER=ldc2 LDC_LTO_RUNTIME=1 LDC_PGO=2 or the prebuilt binaries.
- Release builds use -release -boundscheck=off, so D's array bounds checks and asserts are off in the shipped binaries.
- Benchmark harness gaps: the Linux mawk baseline is 1.3.3 while macOS used 1.3.4, locale is not stated (it affects GNU awk regex and field handling but not cut), C tools come from package managers with unstated flags, Datamash was fed through 'cat |', and no output-equivalence check is described.

## Known shortcomings

- Tier B rests on the independent hck README run (Ryzen 9 3950X: tsv-select 1.702 s vs GNU cut 8.30 7.541 s, about 4.4x derived); the awk rows pit a specialised tool against an interpreter, the D side is built with LTO+PGO while the C tools are distro binaries, GNU cut wins narrow lines and xsv wins regex. Abandoned since 2021-06-13.
- Harness flaws in the 2018 study: Linux mawk baseline 1.3.3 against macOS 1.3.4, locale never stated (affects GNU awk regex, not cut), C tool flags unstated, Datamash fed through 'cat |', outputs never checked for equality. GNU cut also beats tsv-select on a 279 MB file in the 2017 study (0.99 vs 1.21 s). Source builds default to DMD without LTO or PGO (up to 2x slower), release builds use -boundscheck=off, tsv-filter aborts on short or blank lines (issue #355) and on non-numeric fields; no ARM64 binaries (#357) and v2.2.1 has no Linux binaries (#349).

## Caveats and trade-offs

The 2018 study is first-party and 8 years old; the author frames it as a gauge of D performance, not a like-for-like language comparison. The awk rows compare a specialised compiled filter against a general-purpose awk interpreter running a script per line, and Datamash was fed through 'cat |', so same_algorithm is false; the closest like-for-like baseline is GNU cut, which wins the Linux narrow-line test (5.60 vs 8.26 s). Unmatched optimisation: the D tools are LDC builds with LTO and PGO while the C tools are distro package binaries (typically -O2, not crippled). xsv (Rust) wins regex filtering. tsv-utils is single-threaded, so no gain is from parallelism. The independent hck numbers (a competitor's README that says it is not authoritative) cover only column selection; GNU cut's 7.541 s mean has a 1.250 s spread. Repo has no commits since 2021-06-13 (abandoned, not archived). [retier] 2018 study gaps: Linux mawk 1.3.3 against macOS 1.3.4, locale never stated, C tool flags unstated, Datamash fed through 'cat |', outputs never checked for equality; GNU cut also beats tsv-select on a 279 MB file in the 2017 study (0.99 vs 1.21 s). Source builds default to DMD without LTO or PGO (up to 2x slower); release builds use -boundscheck=off; tsv-filter aborts on short or blank lines (issue #355) and non-numeric fields; no ARM64 binaries (#357), v2.2.1 has no Linux binaries (#349).

TSV-only (no CSV escapes except csv2tsv); a toolkit of single-purpose tools rather than awk-like scripting; D toolchain needed to build.

## Maintenance

Effectively unmaintained since the v2.2.1 tag of 2021-06-13 (21 open issues, unanswered requests for Linux and ARM64 binaries) but BSL-1.0, not archived, and the x86-64 v2.2.0 binaries still work as standalone executables.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: besides the first-party 2018 study (command lines and public datasets, but only 'Intel Haswell 2095 MHz' and distro binaries with unknown flags), an independent hyperfine run in the hck README (AMD Ryzen 9 3950X, Ubuntu 20, tool versions and command lines stated) measures tsv-select v2.2.0 at 1.702 s vs GNU cut 8.30 at 7.541 s on the same 7M-line HEPMASS file; C-side build flags are unstated on both pages, so not A.
- **Verifier notes:** All 2018 Linux numbers match the page. Tier raised C to B on the independent hck README measurement (tsv-select about 4.4x faster than GNU cut 8.30, Ryzen 9 3950X); other task claims remain first-party only. Shortcomings: specialised tool vs awk interpreters, LTO+PGO D builds vs distro C binaries, GNU cut wins narrow lines, xsv wins regex, abandoned since 2021.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-12 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/eBay/tsv-utils/HEAD/docs/comparative-benchmarks-2018.md>
  - <https://github.com/eBay/tsv-utils>
  - <https://github.com/eBay/tsv-utils/commits/master>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/eBay/tsv-utils>
  - <https://raw.githubusercontent.com/eBay/tsv-utils/HEAD/README.md>
  - <https://raw.githubusercontent.com/eBay/tsv-utils/HEAD/docs/comparative-benchmarks-2018.md>
  - <https://raw.githubusercontent.com/eBay/tsv-utils/HEAD/docs/comparative-benchmarks-2017.md>
  - <https://raw.githubusercontent.com/eBay/tsv-utils/HEAD/docs/Performance.md>
  - <https://raw.githubusercontent.com/eBay/tsv-utils/HEAD/docs/AboutTheCode.md>
  - <https://raw.githubusercontent.com/eBay/tsv-utils/HEAD/docs/BuildingWithLTO.md>
  - <https://raw.githubusercontent.com/eBay/tsv-utils/HEAD/makedefs.mk>
  - <https://raw.githubusercontent.com/eBay/tsv-utils/HEAD/dub.json>
  - <https://raw.githubusercontent.com/eBay/tsv-utils/HEAD/common/src/tsv_utils/common/utils.d>
  - <https://raw.githubusercontent.com/eBay/tsv-utils/HEAD/tsv-filter/src/tsv_utils/tsv-filter.d>
  - <https://raw.githubusercontent.com/eBay/tsv-utils/HEAD/tsv-select/src/tsv_utils/tsv-select.d>
  - <https://github.com/eBay/tsv-utils/issues>
  - <https://github.com/eBay/tsv-utils/issues/359>
  - <https://github.com/eBay/tsv-utils/issues/349>
  - <https://github.com/eBay/tsv-utils/issues/355>
  - <https://github.com/eBay/tsv-utils/releases>
  - <https://raw.githubusercontent.com/sstadick/hck/HEAD/README.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/ebay/tsv-utils`) · [data/wave14/enrich/raw/github_com_ebay_tsv_utils.json](../../../data/wave14/enrich/raw/github_com_ebay_tsv_utils.json) (enrichment confidence 0.8)

</details>
