# fd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust parallel, gitignore-aware replacement for GNU find; 13-23x faster wall time on one regex name search, by using every core.

| | |
|---|---|
| **Beats** | GNU find (findutils, C) |
| **Claimed result** | fd -u '[0-9]\.jpg\$' 854.8 ms vs find -iregex 19.922 s (README: approximately 23 times faster) and vs find -iname 11.226 s (about 13 times faster). |
| **Workload** | Search the author's home folder (about 750,000 subdirectories and about 4 million files) for names ending in [0-9].jpg with a warm disk cache, timed with hyperfine. The commands were find \~ -iregex '.\*[0-9]\.jpg\$', find \~ -iname '\*[0-9].jpg' and fd -u '[0-9]\.jpg\$' \~ (fd-benchmarks warm-cache-simple-pattern.sh uses fd -HI, 5 warm-up runs, and diffs the outputs). Both tools returned the same 546 files. |
| **Metric** | latency |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Parallelized directory traversal (README feature list: 'Very fast due to parallelized directory traversal'). |
| **Adoption** | 44.8k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/sharkdp/fd) · [benchmark](https://github.com/sharkdp/fd) |

## Verdict

First-party hyperfine runs (README, updated 2023-12-19) on the author's warm-cache home folder (about 750k directories, 4M files): fd -u '[0-9]\.jpg\$' 854.8 ms against GNU find -iregex 19.922 s (about 23x) and find -iname 11.226 s (about 13x), both returning the same 546 files. CPU model, core count, fd and findutils versions and build flags are not stated, fd used all cores, and third-party runs in the issue tracker range from 4x faster (33M files, current master) to slower than find (pre-9.0 builds, single directories, startup-bound runs).

## Use it when

- Interactive name, extension or regex searches over large warm-cache trees (hundreds of thousands to millions of entries) on a multi-core workstation, where wall time matters more than CPU time.
- Source trees where skipping .gitignore'd and hidden paths is what you want anyway; the pre-2023 README timed the default mode at 123.7 ms against 811.6 ms for fd -HI on a 1M-file home folder.
- Generating file lists for fzf, editors and launchers (FZF_DEFAULT_COMMAND='fd --type file').
- Slow or cold storage, where parallel directory reads overlap I/O (issue #1661: 33M files, cold cache, fd master 5.645 s vs find 25.325 s).
- Running a command per match in parallel: on 8 cores fd -x rm took 2.69 s against find -exec rm {} \; at 17.17 s (issue #1778).

## Skip it when

- Scripts that rely on POSIX find semantics (expression operators, -prune, -newer chains, -delete, full -printf) or on find's default of listing everything: fd's defaults differ and it is not a drop-in replacement.
- Shared or many-core machines where total CPU matters: on an i9-13900T fd took 0.383 s real but 1.920 s user + 6.126 s sys, against 1.103 s real and about 1.1 s CPU for find -iregex (issue #1395); a reporter on a 128-thread server saw it slow other jobs (#1661). Pass -j N there.
- Many short invocations or single flat directories: fd's startup was 5.4 ms against 0.64 ms for find -quit, mostly from spawning worker threads, and GNU find -printf %f was 1.79x faster than fd --format on a PATH listing (issue #1614).
- Pre-9.0 distribution builds (for example Debian 12's package): on 33M files with a hot cache that fd took 18.67 s against find's 14.67 s and about 12.5x the CPU, while a current master build took 3.675 s (issue #1661).
- Per-file deletion or process spawning via -x: use -X (fd -X rm 0.15 s) or find -delete (0.12 s), since -x spawns one process per match with extra futex and pipe overhead (issue #1778).

## How it is fast

Directory traversal runs on the ignore crate's WalkParallel (shared with ripgrep), one worker per logical core capped at 64, using readdir file types so most entries need no stat. Each worker matches the base name with the Rust regex crate (finite-automaton engine with literal prefilters) and sends hits in batches of up to 256 over a bounded crossbeam channel to one printer thread; jemalloc is the allocator on most Linux targets. Issue data suggest about a 3x single-thread gain from the faster matcher and the rest from threads: on a Chromium checkout (2.1M files) fd -u -j1 took 2.543 s against find -iregex 8.736 s and find | grep 2.970 s, while the default parallel fd took 221.8 ms (ratios derived from page data, issue #1395).

## Compared with alternatives

Pick fd over minifind or c-blake's cligen/dents when you want a mature, distribution-packaged, gitignore-aware finder with regex/glob matching and parallel exec; dents claims about 1.7x over fd on plain walks and minifind is a narrower find reimplementation. For find-compatible syntax, bfs (C, catalogued in wave 11) is the closer choice.

## Integration

| | |
|---|---|
| **Form** | standalone CLI binary (crate fd-find; packaged by Debian/Ubuntu as fdfind, Fedora, Arch, Alpine, Homebrew and others) |
| **Dependencies** | Rust crates ignore, regex, regex-syntax, globset, aho-corasick, crossbeam-channel, clap, lscolors, jiff, nix/libc; tikv-jemallocator by default (feature use-jemalloc) on Linux and other targets except Windows, macOS, FreeBSD, OpenBSD, Android, illumos, riscv64 and 32-bit musl |
| **Minimum toolchain** | Rust 1.90.0 (edition 2024) to build 10.5.0; prebuilt binaries otherwise |
| **Platforms** | Linux, macOS, Windows, BSDs and others; 10.4.0 dropped full support for Intel Macs and Windows 7 |
| **Thread safety** | Not applicable (CLI); traversal threads default to available_parallelism capped at 64, set with -j/--threads |
| **Drop-in for the baseline** | partial — different syntax and defaults (hidden and ignored files skipped, regex on the base name, smart case); add -u (alias for -HI since v8.4.0) and -p to approach find's coverage, and there is no find expression language |

## Gotchas

- Benchmark harness: the README's 23x/13x is wall clock only, on an unstated machine with all logical cores against single-threaded GNU find, with no CPU time reported. The numbers date from commit 61ebd9b (2023-12-19, around v9.0.0) on a 4M-file corpus; the previous README run on a 1M-file corpus showed 9x and 5x (fd -HI 811.6 ms vs find -iregex 7.236 s). The README command (fd -u '[0-9]\.jpg\$') differs from the published fd-benchmarks script (fd -HI '.\*[0-9]\.jpg\$'), whose output diff checks only find -iregex against fd -HI. No correctness bug was found behind the numbers.
- The baseline is GNU find's slow path: -iregex runs a gnulib regex over the full path, and plain find | grep was already 2.9x faster than find -iregex on the Chromium tree (issue #1395), so much of the headline gap is the matcher and the threads, not the walk.
- Output order is not deterministic: results are sorted only if the search finishes within 100 ms with at most 1000 hits buffered; otherwise they stream in worker order. Patterns match the base name only unless -p/--full-path is given, and -H ignores .git/ since v9.0.0.
- Memory and threading history: fd 8.3/8.4 used an unbounded channel and reached about 24.6 GB RSS on a 200M-entry tree (issue #918, fixed with a bounded queue in Nov 2022); thread start-up made default runs hundreds of times slower than -j1 on WSL2 before 9.0 (issue #1131).

## Known shortcomings

- First-party with no hardware or versions on a private home-directory dataset; parallel fd against single-threaded find plus a different regex engine; fd issue #304 shows unfiltered listing only at parity with find and fd -j1 1.49x slower.
- No correctness bug behind the numbers. The README 23x/13x is wall clock only, all cores against single-threaded find, with no CPU time or hardware stated; the numbers date from commit 61ebd9b (2023-12-19), and the prior 1M-file corpus gave 9x/5x. The README command fd -u '[0-9]\.jpg\$' differs from the fd-benchmarks script (fd -HI '.\*[0-9]\.jpg\$'). Issue #1395 (tavianator, Chromium tree): fd -j1 2.543 s vs find -iregex 8.736 s vs find|grep 2.970 s, so about 3x comes from the regex engine and the rest from threads; issue #1661: a Debian 12 pre-9.0 build was slower than find (18.67 s vs 14.67 s, about 12.5x the CPU); #1614 start-up 5.4 ms vs 0.64 ms; #1778 per-file -x slow; #918 24.6 GB RSS (fixed).

## Caveats and trade-offs

First-party benchmark on one unnamed machine against the author's own home directory. The README says 'one particular benchmark on one particular machine'. fd, find and compiler versions are not stated, and nor is GNU find's build (distribution packages are usually -O2). fd walks directories in parallel with one thread per core by default, while GNU find is single-threaded. The task is dominated by pattern matching: find -iregex uses gnulib regex on the full path, and -iname uses case-folding fnmatch. Without a pattern the gap disappears. In sharkdp/fd issue #304 (2018, fd 7.0-7.1, Linux source tree, warm cache, no hardware stated), multi-threaded fd -HI -t f only reached parity with 'find . -type f' (69.1 ms vs 68.9 ms after commit 50a2bab), and fd -j1 was 1.49x slower than find. In the reporter's home-directory runs find was 2.15x (warm) and 1.85x (cold) faster than fd 7.0.0. So the README's 13-23x is a parallelism plus regex-engine win on a filtering query, not a codegen win, and single-threaded fd is slower than find on plain traversal. The README credits the regex and ignore crates (shared with ripgrep). [retier] The README 23x/13x is wall clock only on all cores against single-threaded find, with no CPU time or hardware; the numbers date from commit 61ebd9b (2023-12-19) and the prior 1M-file corpus gave 9x/5x. Issue #1395 (tavianator, Chromium tree): fd -j1 2.543 s vs find -iregex 8.736 s vs find|grep 2.970 s, so about 3x comes from the regex engine and the rest from threads; issue #1661: a Debian 12 pre-9.0 build was slower than find; #1614 start-up 5.4 ms vs 0.64 ms.

Respects .gitignore and skips hidden files by default (the benchmark needs -u to match find's work); regex search by default instead of glob; parallel traversal uses all cores.

## Maintenance

Actively maintained (10.5.0, commits into October 2026, 44.8k stars), MIT OR Apache-2.0 and packaged by every major distribution; the README benchmark has not been re-run since December 2023 and older distribution builds lack the v9.0.0 traversal speedups.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmark section gives first-party hyperfine results against GNU find (19.922 s, 11.226 s and 854.8 ms; '23 times' and '13 times'). The scripts are public (sharkdp/fd-benchmarks warm-cache-simple-pattern.sh, config.sh, prelude.sh). There is no CPU, no fd or find version, no build flags, and the dataset is the author's own home folder, so it is not reproducible: C. WebSearch found no independent suite.
- **Verifier notes:** Numbers and the 546-file equality check match the README verbatim. Metadata is confirmed: MIT OR Apache-2.0, 44.8k stars, last commit 2026-10-06, not archived. Shortcomings to record: first-party, no hardware or versions, private dataset, a parallel versus single-threaded comparison, and issue #304 shows find matching or beating fd on unfiltered listing and fd -j1 1.49x slower than find.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-14 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/sharkdp/fd>
  - <https://raw.githubusercontent.com/sharkdp/fd/HEAD/README.md>
  - <https://github.com/sharkdp/fd/commits/master>
  - <https://github.com/sharkdp/fd-benchmarks>
  - <https://raw.githubusercontent.com/sharkdp/fd-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/sharkdp/fd-benchmarks/HEAD/warm-cache-simple-pattern.sh>
  - <https://raw.githubusercontent.com/sharkdp/fd-benchmarks/HEAD/config.sh>
  - <https://raw.githubusercontent.com/sharkdp/fd-benchmarks/HEAD/prelude.sh>
  - <https://github.com/sharkdp/fd/issues/304>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sharkdp/fd/HEAD/README.md>
  - <https://raw.githubusercontent.com/sharkdp/fd/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sharkdp/fd/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/sharkdp/fd/HEAD/src/walk.rs>
  - <https://raw.githubusercontent.com/sharkdp/fd/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/sharkdp/fd/HEAD/src/cli.rs>
  - <https://raw.githubusercontent.com/sharkdp/fd/HEAD/src/config.rs>
  - <https://raw.githubusercontent.com/sharkdp/fd-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/sharkdp/fd-benchmarks/HEAD/warm-cache-simple-pattern.sh>
  - <https://raw.githubusercontent.com/sharkdp/fd-benchmarks/HEAD/config.sh>
  - <https://raw.githubusercontent.com/sharkdp/fd-benchmarks/HEAD/prelude.sh>
  - <https://github.com/sharkdp/fd/blame/master/README.md>
  - <https://github.com/sharkdp/fd/commit/61ebd9be6a0c0e380028509be9553aac7931fe08>
  - <https://github.com/sharkdp/fd/issues?q=is%3Aissue%20slower%20than%20find>
  - <https://github.com/sharkdp/fd/issues/1395>
  - <https://github.com/sharkdp/fd/issues/1661>
  - <https://github.com/sharkdp/fd/issues/1614>
  - <https://github.com/sharkdp/fd/issues/1778>
  - <https://github.com/sharkdp/fd/issues/1131>
  - <https://github.com/sharkdp/fd/issues/918>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/sharkdp/fd`) · [data/wave14/enrich/raw/github_com_sharkdp_fd.json](../../../data/wave14/enrich/raw/github_com_sharkdp_fd.json) (enrichment confidence 0.82)

</details>
