# wz (Rust wc replacement)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🔴 abandoned

> Rust wc alternative with table/JSON output; beats GNU wc on chars and words in a UTF-8 locale, loses on bytes.

| | |
|---|---|
| **Beats** | GNU wc (the runner's 'wc'; version not stated) |
| **Claimed result** | BENCH.md hyperfine means (wz vs wc, relative factor as printed): chars (wz -c vs wc -m) 1.9 ms vs 19.8 ms (10.46 +/- 3.16x); default mode 7.3 ms vs 21.4 ms (2.95 +/- 0.19x); words 7.5 ms vs 20.5 ms (2.72 +/- 0.32x); high load 14.9 ms vs 58.2 ms (3.90 +/- 0.29x); lines 1.8 ms vs 2.2 ms (1.20 +/- 0.10x). Bytes go the other way: wz -b 1.9 ms vs wc -c 0.8 ms (wz 2.44 +/- 0.61x slower). No max-line-length result is published. |
| **Workload** | bench/bench.sh, run by the workflow_dispatch job cli_bench in .github/workflows/bench.yml on ubuntu-latest (2 vCPUs): hyperfine 1.15.0 (-m 100 minimum runs, -w 2 warmups) of wz against GNU wc over the 11 files in crates/wz-utf8/tests/resources (about 3.17 MB in total, mostly world192.txt 2.41 MB and Lorem_big.txt 0.75 MB, plus small Arabic, French, Spanish and sample files and an empty file): wz -b vs wc -c, -w vs -w, wz -c vs wc -m, -l vs -l, -L vs -L, default mode, and a high-load case with the file list tripled. The script also produces max-length.md, but BENCH.md does not publish the -L table. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions runner, Intel Xeon Platinum 8272CL @ 2.60GHz, 2 vCPUs (BENCH.md machine information) |
| **Compiler and flags** | wz built by `cargo install --path .` with the Rust stable toolchain current at run time (version not recorded), Cargo.toml release profile: opt-level 2, fat LTO, codegen-units 1, panic abort, strip; bytecount with the runtime-dispatch-simd feature. GNU wc is the ubuntu-latest runner's coreutils binary (version, build flags and locale not recorded). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | README says it is 'heavily optimized' and counts several files in parallel with rayon; no per-mode mechanism is given. |
| **Adoption** | 4 stars, 0 forks; crates.io package wz, 10,947 downloads (32 recent), latest version 1.0.3 published 2022-11-04 |
| **Last commit** | 2023-08-01 |
| **Links** | [repository](https://github.com/Altair-Bueno/wz) · [benchmark](https://github.com/Altair-Bueno/wz/blob/master/BENCH.md) |

## Verdict

Only the author's single hyperfine run backs the claim (BENCH.md, committed 2022-09-09), on a 2-vCPU GitHub Actions runner (Intel Xeon Platinum 8272CL) over 11 test files of about 3.2 MB, against the runner's GNU wc. The rustc version, wc version and locale were not recorded; ubuntu-latest was then probably Ubuntu 20.04, an inference. wz took 1.9 vs 19.8 ms for chars, 7.5 vs 20.5 ms for words, 7.3 vs 21.4 ms in default mode, 14.9 vs 58.2 ms on 33 files and 1.8 vs 2.2 ms for lines, and lost bytes at 1.9 vs 0.8 ms. The counter code for these modes is unchanged from that commit to HEAD apart from doc comments.

## Use it when

- Counting many files at once when you want a per-file table or a JSON summary with totals instead of wc's columns.
- Character counts of valid UTF-8 text, where GNU wc -m in a UTF-8 locale decodes every character and is about 10x slower on the author's runner.
- Word counts of text whose whitespace is ASCII (English or European prose, source code, logs).
- Multi-core machines with many files: rayon spreads files across cores (there is no parallelism inside a single file).
- Old Mac files with CR-only line breaks (-n cr).

## Skip it when

- Scripts that parse wc output or rely on wc's flags and exit status.
- Byte counts alone: wz reads every byte, while GNU wc -c answers from the file size, and BENCH.md shows wz 2.4x slower.
- Line length by display width (-L), or text with Unicode spaces such as U+3000 ideographic space: the answers differ from GNU wc (see gotchas).
- Large single files: nothing larger than the 2.4 MB world192.txt was measured, reads go through a buffer of about 10 KB, and one file uses one thread.
- UTF-16 input (the README lists it as 'coming later'; the encoding option offers only UTF8), or anything needing upkeep: no author changes since 1.0.3 in November 2022.

## How it is fast

Each enabled counter is a trait object chained in a small linked list ('Sheath') allocated in a bumpalo arena, and every counter sees the same read buffer of about 10 KB. Lines use bytecount::count and characters use bytecount::num_chars, which counts bytes that are not UTF-8 continuation bytes with runtime-dispatched SSE2/AVX2. Words are a scalar fold over ASCII-whitespace transitions, and bytes just add up the buffer lengths. With more than one file, rayon counts files in parallel. Most of the measured gain comes from skipping GNU wc's per-character multibyte decoding and from that parallelism, not from a faster algorithm with the same semantics.

## Compared with alternatives

Pick wz over cw when you want table or JSON output across many files and fast UTF-8 character counts. cw was measured on a 341 MB file against GNU wc 8.30 and FreeBSD wc, with gains on lines and default counts, so it is the better-evidenced choice for big single files. hwc and the Haskell and APL wc experiments are demonstrations rather than maintained tools.

## Integration

| | |
|---|---|
| **Form** | crate (binary; cargo install wz); the counters are also published as the no_std crate wz-utf8 |
| **Dependencies** | rayon, bumpalo, bytecount (runtime-dispatch-simd), memchr, clap 4, tabled, terminal_size, serde, serde_json |
| **Minimum toolchain** | Rust 2021 edition; Cargo workspace dependency inheritance needs Cargo 1.64 or later; no rust-version declared, and Cargo.lock was removed from the repo on 2023-01-01 |
| **Platforms** | any Rust target; SIMD only through bytecount's runtime dispatch on x86/x86-64 (SSE2, AVX2), with scalar fallbacks elsewhere; performance on non-x86-64 is unvalidated (issue #11, open) |
| **Thread safety** | not applicable (CLI); files are counted in parallel on rayon's global pool |
| **Drop-in for the baseline** | partial: same quantities as wc, but -c means characters (wc -m) and -b means bytes (wc -c), output is a table or JSON with a Total row, -L counts characters rather than display columns, and the exit status is 0 even when a file cannot be opened |

## Gotchas

- Errors do not fail the run. A missing or unreadable file becomes an 'error' row in the table or JSON, and main still returns Ok, so the exit status is 0. The default table is truncated with '...' to the terminal width (80 columns when piped), so use --output json in scripts.
- -L counts UTF-8 characters per line, not display columns. wz's own test expects "One\ntwo\t\nanother" to give 7, counting the tab as one character, whereas GNU wc -L expands tabs to 8-column stops and counts wide characters as two. Correction to the record: BENCH.md publishes no -L table because at its commit (585793b, 2022-09-09) the -L flag did not exist yet and the max-length line in bench/bench.sh was commented out, not because the result went unpublished.
- Words split only on ASCII whitespace (0x20, 0x09, 0x0A-0x0D), and characters count non-continuation bytes without validating UTF-8 (its own test expects the invalid bytes \xF1\xF3 to count as 2 characters). The 10.5x chars and 2.7x words wins therefore compare this byte-level shortcut against GNU wc's locale-aware multibyte decoding, and counts can differ on Unicode spaces or invalid UTF-8. The runner's locale was not recorded; a user report says the ubuntu-20.04 runner image is C.UTF-8, and under LC_ALL=C GNU wc would not decode at all.
- The comparison mixes parallel and serial work: wz runs rayon over the 11 files (33 in the high-load case) on 2 vCPUs, while GNU wc is single-threaded. Every run takes 0.8-60 ms on about 3.2 MB of input, so process start-up is a large share of each timing.

## Known shortcomings

- Locale and wc version unrecorded; wz runs files in parallel (rayon) against single-threaded wc on 2 vCPUs; word count is ASCII-only vs wc's locale-aware decoding; loses the byte count; the -L table is unpublished; inputs are crates/wz-utf8/tests/resources (about 3.17 MB).
- No -L table because -L did not exist at BENCH commit 585793b (the bench line is commented out), not because results were left unpublished. wz -L counts a tab as one character against wc's display width. The 10.5x chars and 2.7x words wins come from a byte-level shortcut (ASCII-only whitespace, no UTF-8 validation; its own test counts \xF1\xF3 as 2 chars) against GNU wc's multibyte decoding in an unrecorded locale, plus rayon parallelism against single-threaded wc; exit status is 0 on unreadable files.

## Caveats and trade-offs

Inputs are small (about 3.17 MB across 11 files), so runs of 2 to 60 ms include process start-up. wz counts the files in parallel with rayon on the 2-vCPU runner while wc is single-threaded. The char and word wins depend on the locale, which is not recorded: wz counts chars with bytecount::num_chars (SIMD count of non-continuation bytes) and words with an ASCII-only isspace byte fold (0x20, 0x09, 0x0A-0x0D), whereas GNU wc -m and -w in a UTF-8 locale decode every multibyte character and test Unicode whitespace, so the two tools do different work for -w and may differ on non-ASCII whitespace (inference from the sources; wc under LC_ALL=C would not decode). wz loses the plain byte count (wc -c answers from file size). The -L results were produced but not published. No commits since 2023-08-01 (dependabot bumps); 4 stars. [retier] Inputs are small (about 3.17 MB across 11 files), so runs of 2 to 60 ms include process start-up; wz counts files in parallel with rayon on the 2-vCPU runner while wc is single-threaded. The 10.5x chars and 2.7x words wins come from byte-level shortcuts (SIMD count of non-continuation bytes with no UTF-8 validation, ASCII-only whitespace; its own test counts \xF1\xF3 as 2 chars) against GNU wc's multibyte decoding in an unrecorded locale. There is no -L row because -L did not exist at BENCH commit 585793b (the bench line is commented out); wz -L counts a tab as one character against wc's display width. Bytes go the other way (wz 2.44x slower than wc -c). Exit status is 0 on unreadable files. GNU wc version not stated; abandoned since 2022-11-04.

Extra output formats (table, JSON); parallel file counting uses more CPU; bytes mode is slower than wc.

## Maintenance

Abandoned: the last author change was release 1.0.3 on 2022-11-04, followed only by dependabot merges up to 2023-08-01, and there are no GitHub release binaries. It is MIT-licensed, small and readable, and installable from crates.io (wz 1.0.3, about 10,900 downloads, 4 stars).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party BENCH.md with public harness (bench/bench.sh driven by .github/workflows/bench.yml) and the runner CPU (Xeon Platinum 8272CL), but the rustc version, the GNU wc version and build, and the locale are not recorded, so it falls short of A.
- **Verifier notes:** All BENCH.md numbers match the record; input files identified (crates/wz-utf8/tests/resources, about 3.17 MB). Keep at C with shortcomings: locale and wc version unrecorded, wz parallel vs single-threaded wc on 2 vCPUs, word definition is ASCII-only vs wc's locale-aware decoding, loses byte count, -L table unpublished, abandoned since 2023-08.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-63 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/BENCH.md>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/README.md>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/bench/bench.sh>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-utf8/src/lib.rs>
  - <https://github.com/Altair-Bueno/wz>
  - <https://github.com/Altair-Bueno/wz/commits>
  - <https://github.com/Altair-Bueno/wz/tree/master/.github/workflows>
  - <https://github.com/Altair-Bueno/wz/tree/master/crates/wz-utf8/tests/resources>
  - <https://github.com/Altair-Bueno/wz/tree/master/crates/wz-utf8/src>
  - <https://crates.io/api/v1/crates/wz>
- **Sources the enricher read:**
  - <https://github.com/Altair-Bueno/wz>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/README.md>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/BENCH.md>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/bench/bench.sh>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/src/run.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/src/builder.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/src/sheath.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-utf8/src/lib.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-utf8/Cargo.toml>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-utf8/benches/resources.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-utf8/tests/__resources__.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-utf8/tests/words.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-utf8/tests/chars.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-utf8/tests/max_line_length.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-conf/src/lib.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-conf/src/config.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-core/src/lib.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-fmt/src/lib.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-fmt/src/table.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/HEAD/crates/wz-fmt/src/json.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/585793b/crates/wz-utf8/src/lib.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/585793b/src/run.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/585793b/src/builder.rs>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/585793b/Cargo.toml>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/585793b/bench/bench.sh>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/585793b/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/Altair-Bueno/wz/585793b/crates/wz-conf/src/lib.rs>
  - <https://github.com/Altair-Bueno/wz/commits/master>
  - <https://github.com/Altair-Bueno/wz/commits/master/BENCH.md>
  - <https://github.com/Altair-Bueno/wz/issues?q=is%3Aissue>
  - <https://github.com/Altair-Bueno/wz/tree/master/crates/wz-utf8/tests>
  - <https://crates.io/api/v1/crates/wz>
  - https://forum.posit.co/t/github-action-with-ubuntu-20-04-locale-lc-ctype-is-c-utf-8-localetocharset-returns-na/95459 (WebSearch snippet only)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/altair-bueno/wz`) · [data/wave14/enrich/raw/github_com_altair_bueno_wz.json](../../../data/wave14/enrich/raw/github_com_altair_bueno_wz.json) (enrichment confidence 0.7)

</details>
