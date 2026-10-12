# TRE

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Regex](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> POSIX regex library in C with a linear-time tagged-NFA matcher and fuzzy matching; beats interpreted PCRE2 only on backtracking-hostile patterns.

| | |
|---|---|
| **Beats** | PCRE2 interpreted pcre2_match, no JIT (page labels it PCRE2 10.10; the published harness tarball bundles PCRE2 10.20-RC1) |
| **Claimed result** | Mixed, not a project claim. x86-64 Linux, Intel Xeon 2.67GHz: TRE 0.8.0 beats interpreted PCRE2 on [a-zA-Z]+ing (954 ms vs 1373 ms, 1.44x, derived from page data) and .{0,2}(Tom\|Sawyer\|Huckleberry\|Finn) (3425 ms vs 5164 ms, 1.51x, derived from page data) and ties on .{2,4}(Tom\|Sawyer\|Huckleberry\|Finn) (5248 ms vs 5298 ms). x86-32 Linux run: 892 ms vs 1740 ms (1.95x), 3641 ms vs 6726 ms (1.85x), 5700 ms vs 7107 ms (1.25x), all derived from page data. x86-64 Windows, Intel Core i5 3.2GHz: 567 ms vs 773 ms (1.36x) and 2170 ms vs 2970 ms (1.37x), derived from page data, but slower on .{2,4}(...) (3298 ms vs 2965 ms). On the remaining 12 of 15 patterns (13 of 15 on Windows) TRE is slower than interpreted PCRE2, by up to 97x on Twain (486 ms vs 5 ms, derived from page data). |
| **Workload** | Find all non-overlapping matches of 15 regex patterns over the \~20 MB Mark Twain e-book mtent12.txt (carriage returns converted to newlines), restarting each search at the previous match end; best of 5 runs per engine, wall time in ms, engines built with default options. The HTML output prints only times, so match counts per engine are not shown on the page. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon 2.67GHz (Linux, 64-bit and 32-bit runs); Intel Core i5 3.2GHz (Windows); exact CPU SKU not stated |
| **Compiler and flags** | GCC 4.8.2 (Linux runs) / GCC 4.4.7 (Windows run). The page states only -O3; the harness MakeGlobals sets CFLAGS = -g -O3 -Wall, which the tre/ and pcre2/ sub-Makefiles include, so both engine libraries and the driver are built with -g -O3 -Wall. Bundled TRE 0.8.0 config: TRE_WCHAR and TRE_MULTIBYTE on, TRE_APPROX off; bundled PCRE2 10.20-RC1 with SUPPORT_UNICODE and SUPPORT_JIT. TRE called via tre_regcomp(REG_EXTENDED\|REG_NEWLINE) and tre_regnexec; PCRE2 via pcre2_compile(PCRE2_MULTILINE, newline ANYCRLF) and pcre2_match. |
| **Adoption** | 925 stars |
| **Last commit** | 2026-05-23 |
| **Links** | [repository](https://github.com/laurikari/tre) · [benchmark](https://raw.githubusercontent.com/zherczeg/sljit/gh-pages/regex_perf.html) |

## Verdict

Zoltan Herczeg's 2015 comparison timed 15 find-all patterns over the 20 MB Mark Twain text (best of 5, GCC 4.8.2 -O3 on an unnamed Intel Xeon 2.67GHz Linux box, GCC 4.4.7 on a Core i5 3.2GHz Windows box): TRE 0.8.0 beat interpreted PCRE2 (no JIT) on [a-zA-Z]+ing (954 vs 1373 ms) and .{0,2}(Tom|Sawyer|Huckleberry|Finn) (3425 vs 5164 ms), tied on .{2,4}(...), and lost the other 12 patterns, by up to 97x. The harness does not print match counts and gives TRE stricter newline semantics on negated classes, which affects only rows TRE lost to PCRE2.

## Use it when

- You need POSIX regcomp/regexec semantics with correct leftmost-longest submatch offsets, for example to replace a libc regex that reports subexpressions wrongly, and can include &lt;tre/regex.h&gt; as a drop-in.
- Approximate (fuzzy) regex search with insertion, deletion and substitution costs, which none of the catalogued siblings offer.
- Untrusted or user-supplied patterns where matching time must stay linear in the input length (no back-references) and regexec should not allocate from the heap (true in the default alloca build); a compiled regex can be shared by many threads.
- Patterns with a leading unanchored repetition or a repeated class before a literal suffix ([a-zA-Z]+ing, .{0,2}(alternation)) when no JIT or RE2 is available: TRE was 1.25x to 1.95x faster than interpreted PCRE2 on those rows in the 2015 comparison (derived from page data).
- Searching binary data containing NUL bytes (length-taking and \*b byte APIs) or wchar_t strings.

## Skip it when

- General regex throughput: in the 2015 table TRE lost to interpreted PCRE2 on 12 of 15 patterns (Twain 486 ms vs 5 ms, Tom|Sawyer|Huckleberry|Finn 1242 ms vs 40 ms on x86-64 Linux) and was slower than RE2 on every pattern whose newline semantics matched; even on .{0,2}(Tom|Sawyer|Huckleberry|Finn), its best row against PCRE2, RE2 took 66 ms and PCRE2-JIT 443 ms against TRE's 3425 ms.
- Literal or literal-prefix searches: there is no Boyer-Moore or SIMD literal prefilter, so every byte goes through the NFA simulation after the first candidate.
- Perl/PCRE syntax and semantics: no lookahead or lookbehind (still on the README roadmap), POSIX longest-match alternation, and back-references fall back to an exponential backtracking matcher.
- UTF-8 locales where speed matters: with MB_CUR_MAX above 1 the input is decoded through mbrtowc and the single-character memchr shortcut is disabled; the measured runs used the default C locale.
- Untrusted input to the approximate matcher: issue #143 (open, June 2026) reports a heap out-of-bounds read in byte-mode tre_regaexecb; issue #101 (open) reports ^|\$ mishandled under REG_NOTBOL, which find-all loops rely on.

## How it is fast

Patterns compile to a tagged NFA (Laurikari's tagged transitions) that is simulated in parallel over the input, one pass per character, carrying tag values for submatch positions; this gives O(M^2 N) worst case with no backtracking, so patterns such as [a-zA-Z]+ing or .{0,2}(Tom|Sawyer|...) that make a backtracker retry many start positions stay linear. The backtracking matcher is used only for back-references, and approximate matching has its own parallel matcher. The only prefilter is a one-shot memchr when exactly one byte can start a match in 8-bit locales (the general first-character skip loop is compiled out with #if 0), which is why literal-heavy patterns are far slower than in PCRE2, RE2 or Oniguruma.

## Compared with alternatives

Pick TRE over RE2, PCRE2, Boost.Regex, CTRE, RE/flex, REAL and Unformat only when you need its specific features (fuzzy edit-distance matching, a plain C POSIX regcomp/regexec drop-in with leftmost-longest submatches, a wide-char API) rather than speed; RE2 also guarantees linear time and was faster on every semantically comparable pattern, and PCRE2 with JIT was faster still on most.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (autotools build; win32 Visual Studio 2022 files per NEWS), small enough to vendor as source |
| **Dependencies** | none required; libutf8 on platforms lacking wide-character support; autoconf, automake, gettext and libtool to build from the git tree |
| **Minimum toolchain** | hosted C compiler, minimum standard not documented; README lists GCC 11, Clang 14 and 18 and Visual Studio 2022 as tested; autoconf 2.69 to regenerate the build |
| **Platforms** | any hosted C platform; tested on FreeBSD 14.1, Ubuntu 22.04, macOS 14.6 and Windows 11 (README); no architecture-specific code |
| **Thread safety** | Thread safe: all exported functions are re-entrant and one compiled regex_t can be used concurrently from several threads (README). |
| **Drop-in for the baseline** | partial — drop-in for the POSIX &lt;regex.h&gt; API via &lt;tre/regex.h&gt;, not for the PCRE2 API or Perl matching semantics |

## Gotchas

- Harness flaw behind the numbers: the published driver (regex-test.tgz) compiles TRE with REG_EXTENDED|REG_NEWLINE, under which negated bracket lists such as [^u-z] and [^"'] stop at newlines, while PCRE2 (PCRE2_MULTILINE only), RE2 (Latin1 defaults) and Oniguruma let them match newlines; and the HTML build of printResult discards the per-engine match count. So rows with negated classes (including [a-q][^u-z]{13}x, where TRE appears to beat RE2 1928 ms vs 3512 ms) compare different work. TRE's three wins over interpreted PCRE2 use only '.' and positive classes, which behave the same in both engines here, so those wins are not affected.
- Both the TRE and PCRE2 drivers restart each search on a new subject pointer after the previous match without REG_NOTBOL or an offset, so ^ and \b treat each restart point as a start of subject; the effect is equal across engines on these 15 patterns but means the loop is not a correct general find-all.
- Upstream now clamps the searched length to TRE_MAX_STRING (INT_MAX) in the parallel matcher, so a single call silently searches at most about 2 GiB; split larger inputs.
- Per-call working memory is num_states x num_tags integers and comes from alloca() in the default build (TRE_USE_ALLOCA), so very large patterns with many groups or counted repetitions can need large stack frames; older releases computed these sizes in int (CVE-2016-8859, an integer overflow leading to out-of-bounds heap writes in tre_tnfa_run_parallel), and the current tree uses size_t but no explicit multiplication overflow check is visible in that function.

## Known shortcomings

- Downgraded A to B: the sljit regex_perf.html harness is public (regex-test.tgz, -g -O3 -Wall, GCC 4.8.2/4.4.7) but the CPU is given only as 'Intel Xeon 2.67GHz'. Not faster overall: TRE wins 2-3 of 15 patterns against interpreted PCRE2 ([a-zA-Z]+ing 1.44x, .{0,2}(alt) 1.51x; Windows run 1.36x and 1.37x) and loses up to 97x (Twain 486 vs 5 ms) and up to 964x against PCRE2-JIT. 2015 versions (page says PCRE2 10.10, tarball bundles 10.20-RC1); match counts not shown; POSIX vs Perl semantics. BSD-2-Clause, active.
- Enricher: in regex-test.tgz TRE is compiled with REG_NEWLINE, so [^u-z] and [^"'] stop at newlines while PCRE2, RE2 and Oniguruma do not, and the HTML printResult drops match counts; the [a-q][^u-z]{13}x row where TRE beats RE2 (1928 vs 3512 ms) therefore compares different work (TRE's three wins over PCRE2 use no negated classes and are unaffected). The only prefilter is a one-shot memchr; the general first-char skip is '#if 0'. Open #143 heap out-of-bounds read in tre_regaexecb; open #101 ^|\$ wrong under REG_NOTBOL; upstream silently clamps input length to INT_MAX; CVE-2016-8859 hit int sizing in older releases and the current size_t tree has no visible overflow check.

## Caveats and trade-offs

The evidence is a third-party comparison page by the author of the PCRE2 sljit JIT (Zoltan Herczeg, page last modified 2015-08-23), not a TRE claim, and TRE is not faster overall: it loses to interpreted PCRE2 on 12 of 15 patterns (up to 97x on Twain, 486 ms vs 5 ms), to PCRE2-JIT by up to 964x ([a-q][^u-z]{13}x, 1928 ms vs 2 ms) and to RE2 by up to 162x (Twain, 486 ms vs 3 ms), all derived from page data. Its wins come on patterns where the PCRE2 backtracker gets no start-of-match optimisation ([a-zA-Z]+ing, .{0,2}(alternation)); .{2,4}(alternation) is a 1 percent tie on x86-64 Linux and a loss on Windows. Against pcre2_dfa_match TRE wins 7 of 15 patterns on x86-64 Linux, but DFA mode is not the default. Versions are from 2015 (TRE 0.8.0; the page says PCRE2 10.10 while the published harness bundles PCRE2 10.20-RC1); current TRE and PCRE2 were not measured. Engines were not tuned (default options). PCRE2 uses leftmost-first Perl semantics and TRE leftmost-longest POSIX semantics, and the harness does not print match counts, so equal work per engine is not demonstrated. CPU is given only as 'Intel Xeon 2.67GHz' with no model number. Heng Li's regex benchmark (lh3lh3.users.sourceforge.net/reb.shtml) reportedly shows TRE third on alternation patterns but was not opened, so it is not used. [retier] Not faster overall: wins 2-3 of 15 patterns vs interpreted PCRE2 (1.44x, 1.51x), loses up to 97x and up to 964x vs PCRE2-JIT. Harness compiles TRE with REG_NEWLINE, so [^u-z] and [^"'] rows stop at newlines unlike PCRE2/RE2/Oniguruma (the RE2 win on [a-q][^u-z]{13}x is not like for like); match counts dropped from the HTML. 2015 versions, CPU only 'Xeon 2.67GHz', POSIX vs Perl semantics. Open #143 heap OOB read in tre_regaexecb, #101 REG_NOTBOL bug.

POSIX leftmost-longest matching with correct submatches, approximate (agrep-style) matching, wide-char and binary-safe APIs, thread safe, regexec does not allocate from the heap (README). No Perl-style backtracking semantics, so results can differ from PCRE2 on alternation; backreferences are exponential.

## Maintenance

Active again (release 0.9.0 per NEWS; commits through 2026-05-23 are mostly hardening and build fixes merged by dag-erling), BSD-2-Clause and small, so copyable; treat it as a correctness- and feature-driven POSIX regex, not a fast one, and keep untrusted input away from the approximate matcher until issue #143 is fixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now B.
- **Tier reason:** Independent third-party comparison by the PCRE2-JIT author with public harness code (regex-test.tgz on zherczeg/sljit gh-pages: main.c, tre.c, pcre2.c, Makefile, MakeGlobals with CFLAGS -g -O3 -Wall), compiler stated (GCC 4.8.2 Linux, GCC 4.4.7 Windows). It falls short of A because the CPU is given only as 'Intel Xeon 2.67GHz' (no model; several Xeon generations share that clock), and the published tarball bundles PCRE2 10.20-RC1 (pcre2.h PCRE2_DATE 2015-06-16) while the page labels the baseline PCRE2 10.10, so the package does not exactly reproduce the labelled table.
- **Verifier notes:** All numbers in the record check out against the page (64-bit and 32-bit Linux tables), and metadata is correct (BSD-2-Clause per LICENSE, 925 stars, last commit 2026-05-23, not archived, not a fork). Shortcomings to record: not faster overall than PCRE2 (wins 2-3 of 15 patterns, loses by up to 97x), 2015-era versions with a 10.10 vs 10.20-RC1 label mismatch in the harness, CPU model not stated, match counts not shown. Evidence is valid (no reject grounds); no duplicate of a listed project found.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-57 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/zherczeg/sljit/gh-pages/regex_perf.html>
  - <https://raw.githubusercontent.com/zherczeg/sljit/gh-pages/regex-test.tgz>
  - <https://github.com/laurikari/tre>
  - <https://github.com/laurikari/tre/commits>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/laurikari/tre>
  - <https://github.com/laurikari/tre/commits/master>
  - <https://github.com/laurikari/tre/issues?q=is%3Aissue>
  - <https://github.com/laurikari/tre/issues/143>
  - <https://github.com/laurikari/tre/issues/101>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/README.md>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/NEWS>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/include/tre/tre.h>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/include/tre/regex.h>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/lib/tre-match-parallel.c>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/lib/tre-compile.c>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/lib/tre-parse.c>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/lib/tre-match-utils.h>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/lib/regexec.c>
  - <https://raw.githubusercontent.com/laurikari/tre/HEAD/lib/tre-internal.h>
  - <https://raw.githubusercontent.com/zherczeg/sljit/gh-pages/regex_perf.html>
  - <https://raw.githubusercontent.com/zherczeg/sljit/gh-pages/regex-test.tgz>
  - WebSearch: TRE regex library laurikari CVE tre_tnfa_run_parallel overflow (snippets from bugzilla.redhat.com/show_bug.cgi?id=1387112 and openwall.com/lists/oss-security/2016/10/19/1 on CVE-2016-8859)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/laurikari/tre`) · [data/wave1/enrich/raw/github_com_laurikari_tre.json](../../../data/wave1/enrich/raw/github_com_laurikari_tre.json) (enrichment confidence 0.78)

</details>
