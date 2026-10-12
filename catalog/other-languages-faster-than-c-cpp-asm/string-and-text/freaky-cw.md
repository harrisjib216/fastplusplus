# cw (Rust wc replacement)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🔴 abandoned

> Rust wc clone with SIMD line and UTF-8 character counting; 1.5-70x faster than FreeBSD 12 wc and GNU wc 8.30 in 2019.

| | |
|---|---|
| **Beats** | wc from FreeBSD base (C) and GNU coreutils 8.30 wc (gwc, C) |
| **Claimed result** | README hyperfine ratios (cw faster by) vs FreeBSD wc / GNU wc 8.30 on the 341,152,640-byte Pickwick Papers XML: -l 3.44x / 4.17x; default counts 1.45x / 2.05x; -m 70.36x / 30.21x; -mLlw 3.15x / 1.35x; on test-utf-8.html -m 84.74x / 124.21x. The -lL (1.73x / 15.07x) and -mlL (9.05x / 3.88x; 9.42x / 18.95x) rows time a LinesLongest fast path with a line-length bug and count characters where GNU wc -L counts display width, so they are struck. |
| **Workload** | Counting bytes, lines, words, characters and max line length of a 341,152,640-byte XML file (Dickens_Charles_Pickwick_Papers.xml) and of test-utf-8.html, single file and many files via xargs; timed with hyperfine-style 'times faster' output. |
| **Metric** | throughput |
| **Hardware** | FreeBSD 12 on a 2.1 GHz Westmere Xeon (README; exact CPU model not stated) |
| **Compiler and flags** | cw built with 'cargo build --release --features runtime-dispatch-simd' (recommended in README); baseline build flags and Rust version not stated; gwc is GNU coreutils 8.30. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: line counts use the bytecount crate (SIMD, runtime dispatch), line-length mode uses the memchr crate, -m has a UTF-8 character-counting fast path, and --threads counts several files in parallel. The author notes gwc is pessimised in places by FreeBSD's weak memchr. |
| **Adoption** | 107 stars; crates.io 14k downloads (crate cw 0.7.0) |
| **Last commit** | 2021-03-09 |
| **Links** | [repository](https://github.com/Freaky/cw) · [benchmark](https://github.com/Freaky/cw) |

## Verdict

In January 2019 the author ran hyperfine on FreeBSD 12 on a 2.1 GHz Westmere Xeon, timing cw 0.4-0.5 (built with runtime-dispatch-simd) against FreeBSD's base wc and GNU coreutils 8.30 wc on a 341 MB Dickens XML file: -l 3.44x and 4.17x faster, default counts 1.45x and 2.05x, -m 70x and 30x, and about 1.6x/2.4x single-threaded on a many-file run (derived from page data; 11.55x/17.31x with 12 threads). No rustc version, wc build flags, locale or benchmark script is given, and gwc's -L rows measure GNU's display-width semantics rather than the byte count cw computes.

## Use it when

- Counting lines (-l) or UTF-8 code points (-m) of large, well-formed UTF-8 files where a SIMD byte count is all you need.
- Totalling many files at once on a multi-core box via --threads or --files0-from (the README's 12-thread xargs run was 11.55x faster than FreeBSD wc).
- BSD systems where the system wc runs a scalar byte loop and GNU wc is held back by a weak libc memchr.
- Scripts that only need -l, -c or -m and do not depend on locale-specific word or display-width rules.

## Skip it when

- Anything that relies on -L: the -lL fast path is buggy (see gotchas), and even when correct it reports bytes or characters, not GNU's tab-expanded display width.
- Non-UTF-8 locales or legacy encodings: cw ignores the locale entirely; -m assumes UTF-8 and words without -m split on ASCII whitespace only (no vertical tab, no Unicode spaces).
- Modern Linux with GNU coreutils 9.x for plain -l: coreutils 9.0 added an AVX2 newline counter (src/wc_avx2.c), so the 2019 -l ratios no longer describe that comparison.
- Scripts parsing GNU wc output: cw always pads fields to 7 columns BSD-style (issues #4 and #8) and treats '-' as a file name rather than stdin.
- Projects needing a maintained tool: last commit March 2021, open PR #6 and issues #5, #7, #8 unanswered, and the CHANGELOG's 0.8.0 was never tagged or published.

## How it is fast

At startup it picks the cheapest of seven specialised counting loops that covers the requested flags: -c uses stat() on regular files, -l uses bytecount::count (Joshua Landau's 'hyperscreamingcount' SWAR/SSE2/AVX2 byte counting), -m uses bytecount::num_chars (counts bytes that are not UTF-8 continuation bytes, no decoding), -lL scans with memchr, and only -mw-style combinations fall back to a bstr chars() loop. Files are opened with posix_fadvise(SEQUENTIAL) and read in 32 KiB blocks, and --threads hands whole files to a scoped worker pool. The wc baselines run one general loop for every flag combination (FreeBSD 12 wc does a scalar byte loop for -l and calls mbrtowc per character for -m; GNU 8.30 wc -L computes tab-expanded display width with wcwidth).

## Compared with alternatives

Pick cw over wz (the other Rust wc) when you need -L, --files0-from or multi-file --threads on a BSD system; prefer wz for numbers against a current GNU wc on Linux. hwc and the Haskell and APL wc projects are demonstrations rather than maintained tools, so cw is the more practical drop-in of this group despite being unmaintained.

## Integration

| | |
|---|---|
| **Form** | crate (binary; also exposes an undocumented library) |
| **Dependencies** | bytecount 0.6, memchr 2, bstr 0.2, structopt 0.3 (clap 2), crossbeam-channel 0.5, crossbeam-utils 0.8, libc 0.2; winapi on Windows |
| **Minimum toolchain** | Rust 2018 edition; minimum rustc not documented (bytecount 0.6 needs Rust 1.32+); issue #7 shows a 2025 rustc builds it with one unexpected_cfgs warning |
| **Platforms** | Unix (posix_fadvise, F_RDAHEAD on macOS, SIGINFO on BSD/macOS and SIGUSR1 everywhere) and Windows (FILE_FLAG_SEQUENTIAL_SCAN); SIMD only via bytecount runtime-dispatch-simd (SSE2/AVX2 on x86) or nightly-only generic-simd, scalar elsewhere |
| **Thread safety** | Single process CLI; --threads uses scoped threads with an atomic work index and prints results in input order; library thread safety not documented |
| **Drop-in for the baseline** | partial — same core flags as wc (-c -l -w -m -L) plus GNU --files-from/--files0-from, but no locale support, -m and -c override each other instead of printing both, -L counts bytes or characters (FreeBSD semantics, not GNU display width), '-' is not stdin, and output padding is fixed-width |

## Gotchas

- Correctness bug in the -lL fast path (LinesLongest in src/count.rs, unchanged since the benchmarked v0.5.0): the line-length carry is overwritten instead of added when a 32 KiB read holds no newline, the first line of each file is counted one byte short, and a file whose first byte is a newline underflows usize (debug builds panic; release builds report 18446744073709551615). A Python transcription of the closure reports 47,231 for an 80,000-byte line and 4 instead of 5 for 'moooo\nfoo\n'. The README's -lL timings (1.73x and 15.07x) were taken on this code and its output was never shown.
- Every -L path (-lL, -mlL, -wL, -mwL) ignores a final line without a trailing newline; GNU wc 8.30 counts it (its loop updates linelength after the read loop). FreeBSD 12 wc also skips it.
- The 15.07x '-lL vs gwc' and 3.88x/18.95x '-mlL vs gwc' rows compare different work: GNU wc -L computes display width (tabs to every 8th column, wcwidth per character via mbrtowc), while cw and FreeBSD wc count bytes or characters. The 70-124x -m rows compare bytecount's continuation-byte count, which does no validation, against wc's per-character mbrtowc loop; on invalid UTF-8 the counts differ (FreeBSD counts each bad byte as a character and warns, cw counts stray continuation bytes as zero). The locale used for the runs and the content of test-utf-8.html are not stated.
- SIGUSR1 is hooked on every Unix: sending it prints progress to stderr instead of terminating the process. The repo's CHANGELOG lists a 0.8.0 (posix_fadvise, threading tweaks) that was never tagged or published, so 'cargo install cw' gives 0.7.0 from July 2019.

## Known shortcomings

- First-party FreeBSD 12 numbers from January 2019 that predate coreutils 9.0's AVX2 wc -l; the 70-124x -m rows compare a UTF-8 fast path against locale decoding; the win comes from SIMD crates and threads, not the language; last commit 2021-03-09.
- Correctness bug in the -lL fast path (LinesLongest in src/count.rs, same code in benchmarked v0.5.0 and HEAD): the line-length carry is overwritten when a 32 KiB read holds no newline (a Python transcription gives 47,231 for an 80,000-byte line), the first line of each file is counted one byte short, a leading empty line underflows (debug panic, release prints 18446744073709551615), all -L paths skip an unterminated last line, and -lL output is never shown. gwc -L counts display width (tabs, wcwidth per character), so the 15.07x and 3.88x/18.95x rows measure different work; -m rows count continuation bytes with no validation against an mbrtowc loop; locale not stated. CHANGELOG 0.8.0 was never tagged or published (crates.io latest 0.7.0, 2019).

## Caveats and trade-offs

First-party numbers from one FreeBSD 12 machine, measured in January 2019 with cw 0.4-0.5 (the README's benchmark sections were last edited on 2019-01-18; the record's '2020-2021' was wrong), against GNU coreutils 8.30. The README itself says gwc is pessimised on FreeBSD by the system's weak memchr, so Linux/glibc ratios will be smaller; GNU coreutils 9.0 (2021) added an AVX2 newline-counting path to wc -l (WebSearch snippet only), so the -l ratios are outdated. The 70x to 124x -m ratios compare a UTF-8-only byte-counting fast path against locale-aware multibyte decoding in both wc implementations; without -m cw counts bytes and ignores the locale. The win comes from algorithms and crates (SIMD bytecount, memchr, threading), not from Rust code generation (same_algorithm false). Input files other than the Dickens XML are not included, the hyperfine commands are shown only as output, and build flags for both wc binaries and the rustc version are not stated. Several rows depend on multi-threading or the optional runtime-dispatch-simd feature. Unmaintained since March 2021. [retier] Correctness bug in the -lL fast path (src/count.rs LinesLongest, same code in benchmarked v0.5.0 and HEAD): the line-length carry is overwritten when a 32 KiB read holds no newline (47,231 for an 80,000-byte line), the first line of each file is counted one byte short, a leading empty line underflows (release prints 18446744073709551615), all -L paths skip an unterminated last line. gwc -L counts display width (tabs, wcwidth), so the -L rows measure different work; -m rows count continuation bytes with no validation against an mbrtowc loop; locale not stated. CHANGELOG 0.8.0 was never tagged or published (crates.io latest 0.7.0, 2019).

Byte-oriented unless -m; ignores locale (no locale support yet per README Future list); UTF-8 only; no test suite listed at time of README; word counting uses a slow path.

## Maintenance

Abandoned since March 2021 (crates.io 0.7.0 from 2019, 14k downloads) but MIT-licensed, about 850 lines of Rust and still builds on a 2025 toolchain; fine for -l, -c and -m on UTF-8 files, but do not trust its -L output: the -lL fast path has an unfixed carry and off-by-one bug.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party hyperfine output in the README against FreeBSD 12's wc and GNU coreutils 8.30 wc on a 2.1 GHz Westmere Xeon (no exact CPU model), with no rustc version, no build flags for either wc, no benchmark script and only one of the input files identified, so it falls short of A; first-party, so C.
- **Verifier notes:** Confirm at C: every ratio in the record matches the README's hyperfine output, metadata checks out (MIT LICENSE.txt and Cargo.toml, 107 stars, 5 forks, not a fork, last commit 2021-03-09, so abandoned). Shortcomings to record: first-party 2019 numbers on FreeBSD 12 against GNU wc 8.30 that predate coreutils 9.0's AVX2 wc -l; the 70-124x -m rows compare a UTF-8-only fast path with locale-aware decoding; win is SIMD crates and threading rather than the language; no benchmark script, flags or rustc version; abandoned. Not a duplicate (wz, the other Rust wc replacement in this wave, is a separate project).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-76 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/README.md>
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/CHANGELOG.md>
  - <https://github.com/Freaky/cw>
  - <https://github.com/Freaky/cw/commits>
  - <https://github.com/Freaky/cw/commits/master/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/README.md>
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/src/count.rs>
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/src/args.rs>
  - <https://raw.githubusercontent.com/Freaky/cw/HEAD/src/siginfo.rs>
  - <https://raw.githubusercontent.com/Freaky/cw/v0.5.0/src/main.rs>
  - <https://github.com/Freaky/cw/issues?q=is%3Aissue>
  - <https://github.com/Freaky/cw/issues/4>
  - <https://github.com/Freaky/cw/issues/7>
  - <https://github.com/Freaky/cw/issues/8>
  - <https://github.com/Freaky/cw/pulls?q=is%3Apr>
  - <https://github.com/Freaky/cw/pull/6>
  - <https://github.com/Freaky/cw/pull/6/files>
  - <https://github.com/Freaky/cw/commits/master>
  - <https://github.com/Freaky/cw/tags>
  - <https://crates.io/api/v1/crates/cw>
  - <https://raw.githubusercontent.com/coreutils/coreutils/v8.30/src/wc.c>
  - <https://raw.githubusercontent.com/coreutils/coreutils/v9.0/src/wc_avx2.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/releng/12.0/usr.bin/wc/wc.c>
  - <https://raw.githubusercontent.com/llogiq/bytecount/master/README.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/freaky/cw`) · [data/wave14/enrich/raw/github_com_freaky_cw.json](../../../data/wave14/enrich/raw/github_com_freaky_cw.json) (enrichment confidence 0.8)

</details>
