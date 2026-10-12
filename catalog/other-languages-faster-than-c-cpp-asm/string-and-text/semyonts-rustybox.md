# RustyBox (Rust BusyBox-style userland)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MPL-2.0` · 🟢 active

> Single-binary Rust multicall userland (sort, sed, grep, cut, wc and about 45 more) claiming small wins over GNU sort and sed.

| | |
|---|---|
| **Beats** | GNU coreutils sort and GNU sed (versions not stated); BusyBox, Toybox and FreeBSD native tools for the other rows |
| **Claimed result** | README 'selected highlights' (RustyBox vs competitor): sort -n 100k numbers 25.4 ms vs GNU 48.4 ms (1.9x) on Linux and 30.0 ms vs GNU 139.5 ms (4.7x) on FreeBSD; sed 100k lines 29.8 ms vs GNU 37.4 ms (1.3x) on Linux; cat \| grep \| wc pipeline 10.1 ms vs GNU 12.6 ms (1.3x); grep 7.4 ms vs BusyBox 100.6 ms (13.6x). |
| **Workload** | hyperfine on 100k-line inputs: sort -n of 100k numbers, sed over 100k lines, cat \| grep \| wc pipeline, grep, cut, on Arch Linux and a FreeBSD 14.4 VM. |
| **Metric** | latency |
| **Hardware** | Arch Linux on Intel Core i7-8550U; FreeBSD 14.4 in a VM |
| **Compiler and flags** | Not stated; Cargo.toml has no [profile.release] override (cargo default release opt-level 3). GNU builds are distribution binaries of unstated version. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 1 star; crates.io 60 downloads (rustybox_utils 0.1.4) |
| **Last commit** | 2026-08-10 |
| **Links** | [repository](https://github.com/SemyonTs/RustyBox) · [benchmark](https://github.com/SemyonTs/RustyBox) |

## Verdict

The author's README reports hyperfine means on 100k-line inputs on an Intel i7-8550U running Arch Linux: sort -n 25.4 ms vs GNU sort 48.4 ms (1.9x), sed 29.8 ms vs GNU sed 37.4 ms (1.3x) and a cat | grep | wc pipeline 10.1 ms vs GNU 12.6 ms (1.3x), plus a FreeBSD 14.4 VM row of 30.0 ms vs 139.5 ms for sort -n; the larger 4x-21x rows are against BusyBox or FreeBSD base tools. GNU versions, locale, commands, inputs and RustyBox build flags are not stated (Cargo.toml uses the default release profile), so none of this can be reproduced.

## Use it when

- Small container or embedded images where you want one statically linked 2.4 MB binary instead of BusyBox or Toybox, and BusyBox grep/sed/cut speed is the bottleneck (the 4x-21x rows are against BusyBox and FreeBSD base tools).
- FreeBSD or other non-GNU systems where simple `grep`, `cut` or `cat | grep | wc` scripts over UTF-8 text are slow with the base tools.
- Whole-line `sort` or `sort -n` of clean numeric or ASCII input (one number per line) where C-locale byte ordering is acceptable.
- Simple `sed` scripts limited to s///, p, d, a, i, c with numeric or regex addresses, on valid UTF-8 input.

## Skip it when

- As a replacement for GNU coreutils/sed in existing scripts: sed supports only s, p, d, a, i and c (no y, q, n/N, hold space, branches, -i, -E, s flags other than g), and grep lacks -o, context options and backreferences.
- Any input that is not valid UTF-8 (Latin-1 logs, binary data): sort, sed and wc read lines into Rust Strings and abort with an error instead of processing the bytes.
- Locale-sensitive sorting, keyed sorts with modifiers, or sort -u on keys: collation is always byte order and several -k/-u paths differ from POSIX (see gotchas).
- Numeric data with exponents, units suffixes, thousands separators or integers above 2^53: `sort -n` parses whole lines as f64, so '1e3' sorts as 1000, '12 kB' as 0, and large integers can compare equal.
- Production use generally: 1 star, 60 crates.io downloads, one author, two months of history, and the README's speed table has no published harness.

## How it is fast

No special algorithm: the measured paths are plain Rust with buffered I/O. `sort -n` on whole lines takes a fast path that parses each line once into an f64, sorts (f64, index) pairs with the standard library's unstable pattern-defeating quicksort, and prints by index, with no locale collation and no last-resort tie comparison. `grep` and `sed` compile patterns with the Rust `regex` crate (lazy DFA with literal prefilters; grep uses the byte-oriented API to skip UTF-8 validation), which is why they beat BusyBox's libc-regex loops by 10x or more. The GNU-baseline rows are 10-50 ms runs, so process start-up and libc/locale initialisation are a large share of what is measured.

## Compared with alternatives

Pick uutils coreutils when you need GNU compatibility (it implements far more of sort and many more utilities, and claims 1.46x on numeric sort); pick sd for find-and-replace or rust-sort for large sorts; pick RustyBox only when one small multicall binary replacing BusyBox or Toybox is the goal and the scripts use its simple subset.

## Integration

| | |
|---|---|
| **Form** | crate (rustybox_utils on crates.io) building one multicall binary `rustybox`; use via symlinks named after each command |
| **Dependencies** | Rust crates libc, regex, chrono, filetime, linkme, lexopt, rustyline (statically linked; no runtime dependencies) |
| **Minimum toolchain** | Rust edition 2024 (Rust 1.85+); no rust-version field in Cargo.toml |
| **Platforms** | POSIX only: tested on Linux (Arch, x86-64) and FreeBSD 14.4; README claims macOS and NetBSD but no CI or test evidence; no Windows |
| **Thread safety** | not applicable (each command is a single-threaded process); README's 'thread safety in parallel pipelines' claim is marketing, not a feature |
| **Drop-in for the baseline** | partial — same command names and common flags, but sed lacks most commands and `$`/`&`, several sort flags behave differently from GNU/POSIX, and non-UTF-8 input fails |

## Gotchas

- sed correctness bugs (src/commands/sed.rs): `is_last` is hard-coded to false ('Full \$ support ... omitted for brevity'), so the advertised `$` address never matches (`sed '$d'` deletes nothing); `&` in a replacement is emitted literally (only \1-\9 are expanded); the `p` command suppresses auto-print, so `sed p` without -n prints each line once instead of twice; the script is split on every ';', breaking patterns that contain one; and BRE `+ ? { |` are passed to the Rust regex crate as ERE metacharacters. The sed benchmark command is not published, so it is unknown whether the 1.3x row exercised any of these.
- sort correctness bugs (src/commands/sort.rs): the whole-line fast path ignores -b and per-key modifiers, so `sort -k1n` sorts lexicographically and `sort -k1r` ascending; in the generic path `-u` (and `-c -u`) compares whole lines after the keys, so `sort -u -k2,2` keeps every line with a duplicate key; `-k N` without an end field covers only field N instead of running to end of line, and the default key in the generic path (e.g. `sort -f`) is only the first field. No -s, -g, -h, -V, -z or -S options.
- The `sort -n` speed comes partly from doing less than GNU: an f64 parse of the trimmed whole line (Rust syntax, so exponents, 'inf' and 'NaN' are numbers, and lines with a non-numeric suffix become 0), an unstable sort with no last-resort whole-line comparison, and byte rather than locale ordering. `wc -l` counts a final line without a trailing newline (GNU counts newlines), so it can report one more than GNU wc.
- No benchmark scripts, inputs, tool versions, locale or build flags are published (the repository holds only src/, tests/ and docs). The 'GNU' sort used for the FreeBSD 4.7x row is not identified, and every GNU row is a 10-50 ms run where start-up dominates. Of the sort, sed, grep, cut, wc and cat sources, only sort contains unsafe code (a thread-local raw pointer to the config in the sort -m heap comparator), which is harmless here but at odds with the README's 'memory-safe by construction' line.

## Known shortcomings

- No bench scripts in the repo; the sort -n fast path does less work than GNU (whole-line f64 parse, unstable sort, no tie-break); only 4 of 9 rows are against GNU, 1.3-1.9x on Linux.
- Code bugs found by reading (not shown to be behind the numbers): sed.rs hard-codes is_last=false, so \$ never matches, & in replacements prints literally, and sed p without -n prints each line once instead of twice; sort.rs's fast path ignores -b and per-key modifiers, so sort -k1n sorts as text, and -u -k dedups only identical whole lines; non-UTF-8 input makes sort, sed and wc abort; wc -l counts a final line with no newline. No bench harness or inputs are published, and the grep win is against BusyBox only.

## Caveats and trade-offs

Only 'selected highlights' are shown and every listed row is a win: 4 of the 9 rows compare against GNU (sort -n Linux and FreeBSD, sed Linux, cat|grep|wc Linux), the rest against BusyBox or FreeBSD native tools. No benchmark scripts or input files are in the repository (top level holds src/, tests/ and docs only), GNU versions, locale and build flags are not given, and the provenance of the 'GNU' sort used in the FreeBSD VM rows (139.5 ms vs 48.4 ms on Linux) is not stated. Inputs are 100k lines (10 ms to 30 ms runs, where process start-up matters). The sort -n fast path (src/commands/sort.rs sort_numeric_fast) parses each whole trimmed line with Rust's f64 parser (a line with a non-numeric suffix becomes 0, unlike GNU's leading-number parse), sorts with an unstable sort and has no last-resort whole-line comparison, so it does less work than GNU sort -n and can order ties differently. errata.md lists known shell parsing gaps. 1 star, crates.io 60 downloads. [retier] Code bugs by reading: sed.rs hard-codes is_last=false, so \$ never matches, & in replacements prints literally, and sed p without -n prints each line once; sort.rs's fast path ignores -b and per-key modifiers, so sort -k1n sorts as text, and -u -k dedups only identical whole lines; non-UTF-8 input makes sort, sed and wc abort; wc -l counts a final line with no newline. Whether the unpublished benchmark inputs exercise these paths is unknown.

58 commands in a 2.4 MB binary; incomplete compared with GNU coreutils; POSIX-only APIs.

## Maintenance

Single-author project created August 2026 (83 commits on main, last release 0.1.4 on 2026-08-10, an open dev-branch PR from 2026-09-02 adding untested commands), MPL-2.0; usable for simple scripts on UTF-8 text, but sed and sort have correctness gaps against POSIX/GNU that its shallow test suite does not catch, so treat the speed claims as unverified first-party numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party hyperfine numbers in the README 'Selected Highlights' table with CPU named (i7-8550U) but no benchmark scripts in the repo (only src/ and tests/), no GNU versions, no build flags or locale; C.
- **Verifier notes:** README numbers match the record. Small first-party claims (1.3x to 1.9x over GNU on Linux) with no published harness; the sort -n win comes partly from doing less than GNU -n (whole-line f64 parse, no tie-break comparison).
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-83 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/README.md>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/errata.md>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/NOTICE>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/src/commands/sort.rs>
  - <https://github.com/SemyonTs/RustyBox>
  - <https://github.com/SemyonTs/RustyBox/commits>
  - <https://github.com/SemyonTs/RustyBox/tree/main/tests>
  - <https://github.com/SemyonTs/RustyBox/tree/main/src>
  - <https://crates.io/api/v1/crates/rustybox_utils>
- **Sources the enricher read:**
  - <https://github.com/SemyonTs/RustyBox>
  - <https://github.com/SemyonTs/RustyBox/commits>
  - <https://github.com/SemyonTs/RustyBox/issues?q=is%3Aissue>
  - <https://github.com/SemyonTs/RustyBox/pulls>
  - <https://github.com/SemyonTs/RustyBox/pull/2>
  - <https://github.com/SemyonTs/RustyBox/tree/main/tests>
  - <https://github.com/SemyonTs/RustyBox/tree/dev>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/README.md>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/errata.md>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/NOTICE>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/src/commands/mod.rs>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/src/commands/sort.rs>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/src/commands/sed.rs>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/src/commands/grep.rs>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/src/commands/wc.rs>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/src/commands/cat.rs>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/src/commands/cut.rs>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/tests/sort_test.rs>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/HEAD/tests/sed_test.rs>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/dev/changelog.md>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/dev/README.md>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/dev/src/commands/sort.rs>
  - <https://raw.githubusercontent.com/SemyonTs/RustyBox/dev/src/commands/sed.rs>
  - <https://crates.io/api/v1/crates/rustybox_utils>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/semyonts/rustybox`) · [data/wave14/enrich/raw/github_com_semyonts_rustybox.json](../../../data/wave14/enrich/raw/github_com_semyonts_rustybox.json) (enrichment confidence 0.25)

</details>
