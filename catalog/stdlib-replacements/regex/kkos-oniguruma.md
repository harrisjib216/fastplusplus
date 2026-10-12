# Oniguruma

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Regex](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-2-Clause` · 🔴 abandoned

> Ruby-style backtracking regex library in C; beats std::regex on every shared pattern and interpreted PCRE2 on some, not PCRE2-JIT.

| | |
|---|---|
| **Beats** | PCRE2 (pcre2_match interpreter; pcre2_jit_match and pcre2_dfa_match also measured); secondary baseline C++ std::regex |
| **Claimed result** | Mixed result, numbers in ms read from the repo's results_20221012.png (shown in the README). Versus PCRE2 interpreter ('pcre' column), Oniguruma is faster on 10 of the 17 patterns it can run: [a-z]shing 9.5 vs 432.9; [a-q][^u-z]{13}x 22.8 vs 417.5; .{0,2}(Tom\|Sawyer\|Huckleberry\|Finn) 48.8 vs 3201.7; .{2,4}(Tom\|Sawyer\|Huckleberry\|Finn) 48.2 vs 3330.2; \s[a-zA-Z]{0,12}ing\s 42.2 vs 314.9; ([A-Za-z]awyer\|[A-Za-z]inn)\s 114.6 vs 755.5; [a-zA-Z]+ing 379.9 vs 837.3 (ratios 45.6x, 18.3x, 65.6x, 69.1x, 7.5x, 6.6x, 2.2x, derived from page data); the other three wins are near ties or small (\b\w+nn\b 436.6 vs 573.2, (?i)Tom\|Sawyer\|Huckleberry\|Finn 149.9 vs 227.5, Tom.{10,25}river\|river.{10,25}Tom 42.6 vs 43.8). Versus PCRE2 JIT ('pcre-jit' column) it wins on only 4 of 17: [a-q][^u-z]{13}x 22.8 vs 114.8 (5.0x); .{0,2}(Tom\|...) 48.8 vs 176.3 (3.6x); .{2,4}(Tom\|...) 48.2 vs 166.7 (3.5x); \s[a-zA-Z]{0,12}ing\s 42.2 vs 59.7 (1.4x) (derived from page data). It is slower than the interpreter on 7 patterns, for example Twain 11.2 vs 2.5, ∞\|✓ 21.1 vs 0.5 and (.\*?,){13}z 5558.3 vs 567.5 (JIT 32.6). Versus std::regex ('cppstd' column) it is faster on all 15 patterns where both ran, from 2.2x ([a-zA-Z]+ing 379.9 vs 853.3) to 41.7x (.{2,4}(Tom\|...) 48.2 vs 2010.4), e.g. [a-q][^u-z]{13}x 22.8 vs 726.3 (31.9x) and .{0,2}(Tom\|...) 48.8 vs 1941.8 (39.8x) (ratios derived from page data); \p{Sm} is n/a for Oniguruma (ASCII encoding) and std::regex. |
| **Workload** | Time to find all matches of each of 18 regexes (literals, alternations, bounded repeats, case-insensitive, Unicode) over a \~16 MB English text file (3200.txt) with the rust-leipzig/regex-performance harness, 5 repeats per test, compile time excluded; Oniguruma runs with ONIG_ENCODING_ASCII and ONIG_SYNTAX_DEFAULT. |
| **Metric** | throughput |
| **Hardware** | AMD Threadripper 3960X (Zen2) at 3.8 GHz, Ubuntu 20.04.5 LTS |
| **Compiler and flags** | Harness (CMakeLists.txt at HEAD, the 2022-10-13 commit that produced the chart): default build type Release, -O3 plus -march=native -fsigned-char -fno-asynchronous-unwind-tables -fno-stack-protector and GCC-style warnings (-Wstack-usage=5000); CMAKE_C_FLAGS -std=c11 and CMAKE_CXX_FLAGS -std=c++11, while CMAKE_CXX_STANDARD 20 is also set, so the effective C++ standard flag is ambiguous. Compiler name and version not stated. Oniguruma and PCRE2 (PCRE2_SUPPORT_JIT=ON) are ExternalProject builds of upstream master (vendor/CMakeLists.txt) given only -DCMAKE_BUILD_TYPE=Release, so they use their own CMake Release flags (Oniguruma's CMakeLists sets none, so CMake's -O3 -DNDEBUG) and not -march=native; versions unpinned. std::regex is compiled into the harness with the harness flags. |
| **Adoption** | 2.5k stars (repo archived read-only 2025-04-24; benchmark repo rust-leipzig/regex-performance 124 stars, Apache-2.0) |
| **Last commit** | 2025-04-24 |
| **Links** | [repository](https://github.com/kkos/oniguruma) · [benchmark](https://github.com/rust-leipzig/regex-performance) |

## Verdict

In rust-leipzig/regex-performance (October 2022 run, AMD Threadripper 3960X, Ubuntu 20.04.5, compiler unnamed, -O3 Release builds of unpinned master, mean of 5 runs over a 16 MB Mark Twain text, compile time excluded) Oniguruma in ASCII mode beat libstdc++ std::regex on all 15 shared patterns (2.2x-41.7x) and the PCRE2 interpreter on 10 of 17 patterns (up to 69x on .{2,4}(Tom|Sawyer|Huckleberry|Finn)), but lost to PCRE2-JIT on 13 of 17 and to RE2 on 15 of 17 (ratios derived from page data). A 2015 sljit page by the PCRE2-JIT author shows the same per-pattern shape against PCRE2 10.10.

## Use it when

- You need Oniguruma/Ruby regex semantics: TextMate grammars (VS Code's vscode-oniguruma is a WASM build of it), jq filters (jq vendors it as a submodule) or PHP mbstring/mbregex compatibility (php-src ext/mbstring links it).
- Text in non-UTF-8 encodings (Shift_JIS, EUC-JP, EUC-KR, GB18030, Big5, KOI8-R, UTF-16/32) that you want to match without transcoding, since the encoding is set per regex.
- Replacing std::regex in C or C++ code where a C library is acceptable: in the rust-leipzig run it was faster than libstdc++ std::regex on all 15 shared patterns, 2.2x to 41.7x (derived from page data).
- ASCII text with patterns that have a bounded wildcard prefix or a required character class or literal at a fixed distance, on a platform where PCRE2's JIT is unavailable (W^X or no JIT target): the 7 clear wins over the PCRE2 interpreter are 2.2x to 69x on such rows.
- Features most engines lack: variable-length look-behind, the absent operator (?\~...), subexpression calls \g&lt;name&gt;, conditionals, callouts and multi-pattern RegSet search.

## Skip it when

- PCRE2 with JIT is available: PCRE2-JIT beats Oniguruma on 13 of 17 patterns of the same benchmark (e.g. Huck[a-zA-Z]+|Saw[a-zA-Z]+ 1.1 vs 22.8 ms, [a-zA-Z]+ing 44 vs 379.9 ms); RE2 beats it on 15 of 17 (derived from page data).
- Untrusted patterns or inputs: it is a backtracker; (.\*?,){13}z takes 5558.3 ms against 21.1 ms for RE2 and 32.6 ms for PCRE2-JIT, the default retry limit is 10,000,000 per match attempt with no per-search, stack or time limit (USE_TIME_LIMIT is commented out in regint.h). Use RE2 for linear-time guarantees.
- Literal or few-literal searches (log grepping, keyword lists): Twain 11.2 ms vs 2.5 ms for the PCRE2 interpreter and 0.8 ms for PCRE2-JIT; the UTF-8 alternation row 21.1 ms vs 0.5 ms; search loops are scalar byte scans with no memchr or SIMD.
- General mixed workloads: Ferroni's README (a Rust port, first-party, 2026-10-01, Apple M4 Pro and AMD EPYC runners) puts C Oniguruma at 2.2x Ferroni's time against 1.6-1.8x for the PCRE2 interpreter on 32 shared-syntax text tasks, i.e. roughly 1.2-1.4x slower than interpreted PCRE2 and about 4-5x slower than PCRE2-JIT there (derived from page data).
- Projects that need security fixes or maintenance: the author ended the project and archived the repository on 2025-04-24; HISTORY lists past CVEs (CVE-2019-13224, CVE-2019-13225, CVE-2019-19012, CVE-2019-19203, CVE-2019-19204) and many OSS-Fuzz fixes, and no further fixes will come upstream.

## How it is fast

At compile time the optimizer (set_optimize_info_from_tree in regcomp.c) extracts either a required literal or a first-byte map together with the minimum and maximum distance (dist_min, dist_max) of that piece from the match start; onig_search's forward_search then skips through the text with Sunday quick search / Boyer-Moore-Horspool (OPTIMIZE_STR_FAST) or a byte-map scan (OPTIMIZE_MAP) and backs up at most dist_max bytes before running the matcher. That is the likely reason bounded-prefix patterns such as .{0,2}(Tom|Sawyer|Huckleberry|Finn) and [a-q][^u-z]{13}x run 18-69x faster than the PCRE2 interpreter in the benchmark (inferred from the code and the per-pattern numbers). The matcher itself (match_at in regexec.c) is a backtracking VM with direct-threaded dispatch (GCC/Clang labels-as-values, enabled in regint.h) and, per HISTORY, automatic possessification (a\*b compiled as (?&gt;a\*)b). There is no JIT and no SIMD or memchr anywhere in regexec.c/regcomp.c, so plain literal and short-alternation scans lose to PCRE2 (Twain 11.2 ms vs 2.5 ms).

## Compared with alternatives

Pick Oniguruma over PCRE2 and RE2 only when you need its syntax, per-regex encodings or features (TextMate/Ruby compatibility, Shift_JIS or EUC text, absent operator, subexpression calls); for speed PCRE2-JIT and RE2 win most rows of the same benchmark and RE2 is linear-time. Against Boost.Regex, the other run-time std::regex replacement, it wins 8 of 16 shared rows of that chart, and CTRE or RE/flex are better when patterns are fixed at compile time.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake defaults BUILD_SHARED_LIBS=ON; also autotools, make_win.bat, distro packages such as libonig5/oniguruma-devel, vcpkg) |
| **Dependencies** | none (plain C; optional POSIX and GNU regex API wrappers) |
| **Minimum toolchain** | C compiler plus CMake 3.1+ or autotools; C standard not documented. Direct-threaded dispatch only under __GNUC__ (GCC/Clang); other compilers such as MSVC get the switch-based matcher. GCC 15 (C23) build failure fixed 2024-11-18 (#312). |
| **Platforms** | Linux, Unix, Cygwin/MinGW and Windows (Visual Studio) per the README; portable C with no architecture-specific code or SIMD |
| **Thread safety** | Not documented for compiled regex objects. Global state is process-wide: onig_initialize, the default syntax and the retry/stack limit setters; onig_unicode_define_user_property is documented as not thread safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in rust-leipzig/regex-performance src/onig.c: onig_search returns a negative value both for no match (ONIG_MISMATCH, -1) and for errors such as ONIGERR_RETRY_LIMIT_IN_MATCH_OVER (-17), and the loop breaks on any res &lt; 0, so a limit error would silently end the search and be timed as a finished scan. Match counts are printed but never compared across engines and are not in the published PNG, so the (.\*?,){13}z row (5558.3 ms) and the others cannot be checked for truncation; nothing shows that it fired. Also: times are the mean of 5 clock() CPU-time runs, not the best time the README states; Oniguruma and PCRE2 restart the subject at each previous match end (ptr += end, so \b and string-start see a fresh string) while std::regex iterates over the whole text; Oniguruma and PCRE2 are unpinned master builds without -march=native.
- Pathological-pattern defaults: retry limit 10,000,000 per match attempt, 0 (unlimited) per search, unlimited match stack, and the time limit is compiled out; set onig_set_retry_limit_in_search() / onig_set_match_stack_limit_size() yourself, and treat every negative return other than ONIG_MISMATCH as an error (issue #290 asks exactly whether 'retry-limit-in-match over' means no match).
- doc/API says not to pass byte strings that are invalid in the regex's encoding to onig_search; it does not validate UTF-8, so validate untrusted input first. With ONIG_ENCODING_ASCII, Unicode properties such as \p{Sm} fail to compile (the n/a row). onig_new() auto-initializes if onig_initialize() was never called but prints a warning.
- Case-insensitive UTF-8 patterns can lose the literal-prefix search: issue #71 (2017, closed) measured /----k/i at 8.10 s and /----s/i at 8.21 s against 1.13 s for /----a/i and 1.12 s for /----k/i in ASCII; whether later releases fixed it was not checked.

## Known shortcomings

- Tier B on rust-leipzig/regex-performance (public code, CMake flags, Threadripper 3960X; compiler not named): wins 10 of 17 patterns against the PCRE2 interpreter (3 of them near ties), 4 of 17 against PCRE2-JIT and 15 of 15 against std::regex (2.2x-41.7x, derived from page data), but loses 13 of 17 to PCRE2-JIT and blows up on (.\*?,){13}z (5558.3 vs 32.6 ms). Single 2022 run, means of 5 clock() repeats, engines built from unpinned master, -march=native reaches only the harness. The 2015 sljit regex_perf page (Oniguruma 5.9.6 vs PCRE2 10.10, GCC 4.8.2 -O3) agrees on 6 of 15 wins over interpreted PCRE2. Repo archived 2025-04-24; BSD-2-Clause.
- Enricher (rust-leipzig src/onig.c): the loop stops on any onig_search result below 0, so an error such as ONIGERR_RETRY_LIMIT_IN_MATCH_OVER would silently end the scan and be timed as done (match counts never cross-checked; no evidence it fired); results are the mean of 5 clock() runs, not 'best' as the README says; Onig and PCRE2 restart the subject at each match end while std::regex walks the whole text; engines built from unpinned master without -march=native. Loses to PCRE2-JIT 13 of 17 and RE2 15 of 17, beats Boost.Regex only 8 of 16; literal search slow (Twain 11.2 vs PCRE2 2.5 ms; scalar search loops, no memchr/SIMD); default retry limit 10M per match with search, stack and time unlimited; no UTF-8 validation; 2019 CVEs in HISTORY. Ferroni's README (Rust port, first-party, 2026-10-01) has C Oniguruma about 1.2-1.4x slower than the PCRE2 interpreter on 32 shared-syntax tasks (derived), so the interpreter wins are pattern-specific.

## Caveats and trade-offs

Third-party community shootout, not a project claim: Oniguruma's own README and docs carry no benchmark. The numbers exist only as a PNG (results_20221012.png, October 2022 run), not as a data file, and were read from the image. The README says the tool prints the best time of 5 repeats but src/onig.c and pcre2.c fill a times array and report mean and standard deviation. Compiler is not named, tier A is therefore borderline; Oniguruma and PCRE2 versions are whatever master was in 2022. Match counts are printed but not asserted equal across engines, and Oniguruma runs in ASCII encoding while PCRE2 runs in default (non-UTF) mode with PCRE2_MULTILINE, so semantics are close but not identical. It loses to PCRE2 JIT on 13 of 17 patterns, so the win holds only against the interpreter, not against the usual fast PCRE2 configuration. Snippet-only, not opened (hosts blocked here): a 2003 mailing-list post by the author said Oniguruma was 10-20% faster than PCRE 3.9 under ASCII encoding (obsolete PCRE 3.x), and Heng Li's regex benchmark (onig-posix 5.9.2 vs PCRE 8.10 and RE2 2010) was summarised as onig fastest on '|'-free regexes; neither used PCRE2. Verifier additions: the chart is a single run; times are means of 5 repeats measured with clock() (process CPU time), and the repository HEAD (commit #19, 2022-10-13, 'updated the benchmarks') is the harness that produced the chart. The harness's -march=native applies only to the driver and the header-only std::regex code; Oniguruma and PCRE2 are ExternalProject builds that receive only -DCMAKE_BUILD_TYPE=Release, so they use their own CMake Release flags. The repo's Dockerfile uses Debian 9 g++, but the published run was on Ubuntu 20.04.5, so the Dockerfile does not identify the compiler. std::regex was built with std::regex::optimize (ECMAScript) and cannot run the (?i) rows; baseline_stdlib libstdc++ is inferred (Ubuntu toolchain, no -stdlib flag in the CMake files), not stated. Independent corroboration with an older pairing: Zoltan Herczeg's sljit regex_perf page (2015, Oniguruma 5.9.6 vs PCRE2 10.10, GCC 4.8.2 -O3, Intel Xeon 2.67GHz without SKU, harness regex-test.tgz) shows the same shape on x86-64 Linux: Oniguruma beats interpreted PCRE2 on 6 of 15 patterns ([a-z]shing 15 vs 564 ms, [a-q][^u-z]{13}x 61 vs 746, .{0,2}(Tom|...) 127 vs 5164, .{2,4}(Tom|...) 124 vs 5298, \s[a-zA-Z]{0,12}ing\s 78 vs 592, ([A-Za-z]awyer|[A-Za-z]inn)\s 243 vs 1112) and loses on the other 9, and beats PCRE2-JIT only on .{0,2}/.{2,4}(Tom|...) and \s[a-zA-Z]{0,12}ing\s (127 vs 443, 124 vs 487, 78 vs 140 ms). That page was written by the PCRE2-JIT author. Oniguruma has no JIT, is a backtracker (the (.\*?,){13}z row is 5558.3 ms), and the repository was archived by its author on 2025-04-24. [retier] rust-leipzig/regex-performance (Threadripper 3960X, 2022, means of 5 clock() runs, engines from unpinned master without -march=native): wins 10/17 vs PCRE2 interpreter (3 near ties), 4/17 vs PCRE2-JIT, 15/15 vs std::regex; loses 13/17 to PCRE2-JIT and 15/17 to RE2; (.\*?,){13}z blows up (5558.3 ms); literal search slow (Twain 11.2 vs 2.5 ms). Harness loop stops silently on any negative onig_search result and never cross-checks match counts. Ferroni README (first-party, 2026) has C Oniguruma 1.2-1.4x slower than the PCRE2 interpreter on 32 tasks. Archived 2025-04-24; no UTF-8 validation; unlimited search/stack/time by default.

Backtracking matcher, so pathological patterns blow up (the (.\*?,){13}z row takes 5558.3 ms against 32.6 ms for PCRE2 JIT and 21.1 ms for RE2). Ruby/Oniguruma syntax and many per-regex character encodings rather than Perl/PCRE syntax and Unicode properties (the \p{Sm} row is n/a for it). No JIT. Project ended and archived by the author on 2025-04-24, so it is now a frozen codebase.

## Maintenance

Abandoned: the author ended the project and archived the repository read-only on 2025-04-24 at version 6.9.10 (Unicode 16.0); BSD-2-Clause, widely packaged and still embedded by jq, PHP mbstring and VS Code, so it is usable as a frozen dependency, but security fixes now depend on distributions or forks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite rust-leipzig/regex-performance (src/onig.c, src/pcre2.c, src/cppstd.cpp, src/main.c) with public code, CMake flags and a named CPU (Threadripper 3960X) shows Oniguruma beating std::regex on all 15 shared patterns and the PCRE2 interpreter on 10 of 17, but the compiler is not named, so not A. Corroborated by the 2015 sljit regex_perf page (GCC 4.8.2 -O3, CPU without SKU), which shows the same per-pattern wins over interpreted PCRE2.
- **Verifier notes:** All numbers in claimed_speedup match the PNG (onig, pcre, pcre-jit, cppstd columns checked row by row; 10/17 vs interpreter, 4/17 vs JIT, 15/15 vs std::regex). Shortcomings to record: not faster than PCRE2-JIT (loses 13 of 17), mixed vs interpreted PCRE2, compiler unnamed, single 2022 run with unpinned master builds, archived 2025-04-24, catastrophic backtracking on (.\*?,){13}z. Not a duplicate; Onigmo (fork) is not listed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** verifier batch-68 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/rust-leipzig/regex-performance>
  - <https://github.com/rust-leipzig/regex-performance/commits/master>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/README.md>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/results_20221012.png>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/vendor/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/onig.c>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/pcre2.c>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/cppstd.cpp>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/main.h>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/Dockerfile>
  - <https://github.com/kkos/oniguruma>
  - <https://github.com/kkos/oniguruma/commits>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/COPYING>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/zherczeg/sljit/gh-pages/regex_perf.html>
- **Sources the enricher read:**
  - <https://github.com/kkos/oniguruma>
  - <https://github.com/kkos/oniguruma/issues?q=is%3Aissue+performance>
  - <https://github.com/kkos/oniguruma/security>
  - <https://github.com/kkos/oniguruma/issues/290>
  - <https://github.com/kkos/oniguruma/issues/71>
  - <https://github.com/kkos/oniguruma/issues/143>
  - <https://github.com/kkos/oniguruma/issues/284>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/README.md>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/COPYING>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/HISTORY>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/doc/API>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/doc/RE>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/doc/SYNTAX.md>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/src/oniguruma.h>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/src/regint.h>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/src/regexec.c>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/src/regcomp.c>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/src/regparse.c>
  - <https://raw.githubusercontent.com/kkos/oniguruma/HEAD/src/regsyntax.c>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/README.md>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/results_20221012.png>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/vendor/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/onig.c>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/pcre2.c>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/cppstd.cpp>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/re2.cpp>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/src/main.h>
  - <https://raw.githubusercontent.com/rust-leipzig/regex-performance/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/jqlang/jq/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/php/php-src/HEAD/ext/mbstring/config.m4>
  - <https://raw.githubusercontent.com/microsoft/vscode-oniguruma/HEAD/README.md>
  - <https://crates.io/api/v1/crates/ferroni>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/kkos/oniguruma`) · [data/wave1/enrich/raw/github_com_kkos_oniguruma.json](../../../data/wave1/enrich/raw/github_com_kkos_oniguruma.json) (enrichment confidence 0.8)

</details>
