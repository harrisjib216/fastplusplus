# ucg (UniversalCodeGrep)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-3.0-only` · 🟢 active

> Ack-style recursive source-code grep using PCRE2 JIT and threaded traversal; about 3.7x faster than egrep -R on a kernel-tree search.

| | |
|---|---|
| **Beats** | GNU grep (egrep -R with --include filters) |
| **Claimed result** | ripgrep 0.8.0 README, Linux kernel tree, whitelist search for whole-word [A-Z]+_SUSPEND: ucg 0.163s vs GNU grep (egrep -R) 0.611s, about 3.7x faster (derived from page data); ripgrep 0.079s, so ucg is about 2x slower than ripgrep. ucg returned 390 lines against 404 for grep and ripgrep. The same suite's 2018-01-08 run (benchsuite/runs/2018-01-08-archlinux-cheetah/summary) shows mixed single-file results against GNU grep 3.1: ucg faster on subtitles_en_literal (0.386 vs 0.803 s, line mode), subtitles_en_literal_word (0.384 vs 0.788 s), subtitles_en_alternate (1.132 vs 1.828 s) and subtitles_ru_alternate (2.043 vs 7.513 s), but slower on subtitles_en_surrounding_words (3.567 vs 1.070 s), subtitles_en_no_literal (5.394 vs 3.446 s), subtitles_ru_literal (2.418 vs 1.089 s) and subtitles_ru_literal_word (2.404 vs 1.114 s). |
| **Workload** | Recursive search of a built Linux kernel source tree for the whole-word regex [A-Z]+_SUSPEND, restricted to C source files (gitignore handling disabled for ripgrep, --include filters for grep, ucg --type=cc). |
| **Metric** | throughput |
| **Hardware** | Intel i7-6900K 3.2 GHz (per the ripgrep 0.8.0 README, kernel tree built with make defconfig && make -j8) |
| **Compiler and flags** | Not stated in the README table (only 'ripgrep was compiled with SIMD enabled'); commands: ucg --type=cc -w '[A-Z]+_SUSPEND' versus egrep -R -n --include='\*.c' --include='\*.h' -w '[A-Z]+_SUSPEND'. The suite's 2018-01-08 run README lists ucg 0.3.3-251-g9b5a3e3 built with g++ 7.2.1 (-std=gnu++1z, SSE4.2 and POPCNT in use, PCRE2 10.30 with JIT), GNU grep 3.1 and ripgrep built with RUSTFLAGS='-C target-cpu=native' and simd-accel avx-accel; optimization flags for ucg and grep are not given, and the [A-Z]+_SUSPEND table is not part of that run's summary, so these versions are only probably the README's. |
| **Adoption** | 144 stars; packaged for Fedora (Copr), Arch (AUR) and Homebrew core |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/gvansickle/ucg) · [benchmark](https://github.com/BurntSushi/ripgrep/blob/0.8.0/README.md) |

## Verdict

In the ripgrep 0.8.0 README, ripgrep's author ran a whole-word [A-Z]+_SUSPEND search over a built Linux kernel tree, restricted to C files, on an Intel i7-6900K. ucg took 0.163 s, GNU grep (egrep -R with --include filters) 0.611 s and ripgrep 0.079 s, so ucg was about 3.7x faster than grep (derived from page data). ucg searched slightly fewer files (390 lines against 404) and compiler flags for ucg and grep are not given. The same suite's 2018 single-file runs against grep 3.1 are mixed. ucg's own first-party Boost table (Fedora 25, average of 10 runs) shows ucg 0.229 s against grep 2.26 at 0.370 s and ripgrep 0.168 s.

## Use it when

- Interactive regex searches over large multi-language source trees (kernel- or Boost-sized) on multi-core x86-64 Linux, filtered by language type.
- You want ack's command-line conventions or PCRE syntax (lookarounds, backreferences) and something faster than egrep -R --include or ag.
- Machines where ripgrep is unavailable and a GPL-3.0 tool is acceptable (Fedora Copr, AUR and Homebrew packages exist).

## Skip it when

- ripgrep is installed: it beats ucg in every published comparison (0.079 s vs 0.163 s on the kernel whitelist search; 0.168 s vs 0.229 s on ucg's own Boost table).
- Single large files with weak or no literal anchors: in ripgrep's 2018-01-08 suite ucg was slower than GNU grep 3.1 on subtitles_en_surrounding_words (3.567 vs 1.070 s), subtitles_en_no_literal (5.394 vs 3.446 s) and the Russian literal patterns (about 2.2x slower).
- Files larger than about 2 GiB, or filesystems that return short reads: the whole-file read loop does not advance its buffer pointer, so such files are searched incorrectly (see gotchas).
- You need .gitignore handling, context lines (-A/-B/-C, open issue #113), match counts (-c, open issue #61), or a non-x86 build (open issue #123: HEAD does not compile on ARM; #122: 0.3.3 fails on NetBSD).
- You need an embeddable library or a permissive licence: ucg is a GPL-3.0-only CLI with no library API.

## How it is fast

Regex matching runs in PCRE2 with JIT compilation over the whole file buffer, not line by line, and newlines are counted only around matches. Directory traversal runs on its own threads (default 2, --dirjobs) and feeds a queue of scanner threads (default one per core, -j). A literal-prefix analysis of the pattern drives hand-written SSE2/SSE4.2/POPCNT prefilters (PCMPESTRI find_first_of over first-possible code units, PCMPEQB plus movemask for single bytes and newline counting) that skip ahead to candidate positions. The ISA variant is chosen at load time, with scalar fallbacks. Files are read whole with posix_fadvise(SEQUENTIAL) and 128 KB to 1 MB I/O sizing.

## Compared with alternatives

The indexed siblings (ngi, trigrep, frg, ugrep with ugrep-indexer) need an index build before they are fast. ucg needs no index and fits one-off searches with ack syntax. For unindexed search, ripgrep, a non-catalogued incumbent, is faster than ucg in every published source, so choose ucg mainly for its ack-compatible interface.

## Integration

| | |
|---|---|
| **Form** | built command-line binary (autotools: configure && make); no library API |
| **Dependencies** | libpcre2-8 &gt;= 10.20 (preferred) or libpcre &gt;= 8.21; argp-standalone on macOS |
| **Minimum toolchain** | C++20 compiler (configure.ac requires AX_CXX_COMPILE_STDCXX(20, ext, mandatory) and C18); the README's 'gcc 4.8 or greater' line is stale |
| **Platforms** | x86-64 fully supported (SSE2/SSE4.2/POPCNT paths picked at load time, scalar fallbacks); historically tested on Linux, macOS, TrueOS/FreeBSD and Cygwin; ARM build broken at HEAD (issue #123); Fedora 44 test failures open (issue #148) |
| **Thread safety** | not applicable (standalone CLI; internally multithreaded with std::thread) |
| **Drop-in for the baseline** | partial: grep-like output and some grep options, but ack-style defaults differ (smart-case on, only known file types searched, recursion on, no .gitignore, PCRE rather than POSIX ERE syntax) |

## Gotchas

- Whole-file read bug in src/File.cpp: 'while((retval = read(file_descriptor, file_data, file_size)) &gt; 0);' never advances the destination pointer. A short read, which Linux always produces for files above 2,147,479,552 bytes and which can happen on FUSE or network filesystems, makes the next read overwrite the start of the buffer while the tail stays unread. Matches in such files are then wrong or missing. EINTR is not retried. The kernel and Boost benchmark files are small, so the published numbers are not affected.
- Defaults differ from grep: --smart-case is on, so an all-lowercase pattern matches case-insensitively, and -k/--known-types is on, so files with unrecognized extensions are silently skipped. Patterns are compiled with PCRE2_NEVER_UTF and PCRE2_NEVER_UCP, so matching is byte-wise: '.', \w and case folding have no Unicode semantics for UTF-8 text.
- Multithreaded traversal skips directories already reached through a symlink (issue #106), so ucg can search fewer files than grep -R. This is why it printed 390 lines against 404 in the ripgrep benchmark row.
- PCRE2 JIT needs writable-then-executable memory; PaX MPROTECT hardening is unsupported (open issue #101). The mmap read path is disabled in the source as 'very broken'.

## Known shortcomings

- The 0.163 s vs GNU grep 0.611 s row comes from the ripgrep 0.8.0 README, run by a competitor's author with optimisation flags unstated, and ucg searched fewer files than egrep -R (symlinks, issue #106). The same suite's 2018 single-file runs have ucg slower than grep 3.1 on several patterns, and ripgrep beats ucg everywhere.
- Enricher (code reading): src/File.cpp's read loop `while((retval = read(fd, file_data, file_size)) > 0);` never advances its pointer, so any short read (every file over 2,147,479,552 bytes, or a short read on FUSE or NFS) overwrites the start of the buffer and leaves the tail unread, giving wrong or missed matches; EINTR is not retried. Published numbers unaffected (small files). The README says gcc 4.8+ but configure.ac requires C++20; matching is byte-only (PCRE2_NEVER_UTF, NEVER_UCP); ripgrep is faster in every source.

## Caveats and trade-offs

The benchmark was run by the author of the competing tool ripgrep (third party to ucg, but a competitor). The README states the CPU (Intel i7-6900K) and the ripgrep build only; the linked blog post was not reachable. ucg's line count differs because of directory traversal: per gvansickle/ucg issue 106 (opened by BurntSushi, closed 2017-05-07), ucg's multithreaded traversal skips directories already reached through a symlink, so it searched fewer files than egrep -R, which follows symlinks (grep -r without symlink following also returns 390), so ucg did slightly less work in that row. ucg is not uniformly faster than GNU grep: in the same suite's 2018-01-08 single-file subtitles runs it is slower than grep 3.1 on the surrounding-words, no-literal and Russian literal patterns (up to about 3.3x slower) while faster on English literal and alternation patterns. ucg's own README has a first-party table (Boost 1.58.0 source, pattern '#include\s+.\*', Fedora 25, average of 10 runs): ucg 0.3.0 0.228973s, ripgrep 0.2.9 0.167586s, ag 0.32.0 2.29074s, GNU grep 2.26 0.370082s (about 1.6x slower than ucg, derived); its 'Num Diff Chars' column shows ucg output differing from grep's by 189 characters (9511 matched lines against 9509); that table is first-party with no CPU or flags, and ripgrep wins it. All numbers are from 2016-2018 versions; ucg is slower than ripgrep in every source. Recent commits (2026-09-14) are CI, m4 and perf-comparison script changes; the last source-code change is from 2024-12-28. ucg's tests/performance_tests.at and tests/benchmark_progs.csv can regenerate a comparison, but no recent numbers are published. [retier] Enricher (code reading): src/File.cpp's read loop never advances its pointer, so a short read (files over 2,147,479,552 bytes, FUSE or NFS) overwrites the buffer start and leaves the tail unread; EINTR not retried. README says gcc 4.8+ but configure.ac requires C++20; byte-only matching.

GPL-3.0-only (copyleft). Uses PCRE2 with JIT, a multithreaded directory walker and hand-rolled SSE2/SSE4.2 scan loops chosen at load time. Does not read .gitignore; it relies on a built-in per-language file whitelist. Search patterns are PCRE only. Command-line compatible with ack, partly with ag and grep.

## Maintenance

Low-activity single-maintainer project: the last source change was 2024-12-28 (new --null, --line-number and --with-filename options), and the 2026-09-14 commits only touch CI, m4 macros and the perf-comparison setup. It is GPL-3.0-only and usable as a packaged CLI, but the published numbers date from 2016-2018 and a large-file read bug is present at HEAD.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** The ripgrep 0.8.0 README (a widely cited third-party suite, run by a competitor's author) shows ucg 0.163s against GNU grep 0.611s on the Linux kernel [A-Z]+_SUSPEND whitelist search on an Intel i7-6900K; the harness (benchsuite/benchsuite) is public but optimization flags for ucg and grep are not stated, so independent but short of A.
- **Verifier notes:** Record accurate; tier B stands (third-party ripgrep suite, CPU stated, flags missing). Main shortcomings: competitor-run benchmark from 2018, ucg searched fewer files than egrep -R in the quoted row (symlink traversal), and the same suite shows ucg slower than GNU grep on several single-file regex patterns; ripgrep beats ucg everywhere. Metadata checked: GPL-3.0-only, 144 stars, 18 forks, not archived or a fork, last commit 2026-09-14 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-21 (wave 3 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/BurntSushi/ripgrep/blob/0.8.0/README.md>
  - <https://github.com/BurntSushi/ripgrep/tree/0.8.0/benchsuite/runs>
  - <https://github.com/BurntSushi/ripgrep/tree/0.8.0/benchsuite/runs/2018-01-08-archlinux-cheetah>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/0.8.0/benchsuite/runs/2018-01-08-archlinux-cheetah/README>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/0.8.0/benchsuite/runs/2018-01-08-archlinux-cheetah/summary>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/0.8.0/benchsuite/runs/2018-01-08-archlinux-cheetah/raw.csv>
  - <https://github.com/gvansickle/ucg>
  - <https://github.com/gvansickle/ucg/commits>
  - <https://github.com/gvansickle/ucg/commits/master.atom>
  - <https://github.com/gvansickle/ucg/issues/106>
- **Sources the enricher read:**
  - <https://github.com/gvansickle/ucg>
  - <https://raw.githubusercontent.com/gvansickle/ucg/HEAD/README.md>
  - <https://raw.githubusercontent.com/gvansickle/ucg/HEAD/configure.ac>
  - <https://github.com/gvansickle/ucg/tree/master/src>
  - <https://github.com/gvansickle/ucg/commits>
  - <https://raw.githubusercontent.com/gvansickle/ucg/HEAD/src/FileScanner_sse4_2.cpp>
  - <https://raw.githubusercontent.com/gvansickle/ucg/HEAD/src/FileScanner.cpp>
  - <https://raw.githubusercontent.com/gvansickle/ucg/HEAD/src/FileScannerPCRE2.cpp>
  - <https://raw.githubusercontent.com/gvansickle/ucg/HEAD/src/File.cpp>
  - <https://github.com/gvansickle/ucg/issues>
  - <https://github.com/BurntSushi/ripgrep/blob/0.8.0/README.md>
  - <https://github.com/gvansickle/ucg/tree/master/.github/workflows>
  - <https://raw.githubusercontent.com/gvansickle/ucg/HEAD/.github/workflows/github-actions-ucg-ci-using-podman.yml>
  - <https://raw.githubusercontent.com/gvansickle/ucg/HEAD/tests/benchmark_progs.csv>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/gvansickle/ucg`) · [data/wave3/enrich/raw/github_com_gvansickle_ucg.json](../../../data/wave3/enrich/raw/github_com_gvansickle_ucg.json) (enrichment confidence 0.75)

</details>
