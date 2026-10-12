# flex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Lexers and tokenizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause-flex` · 🟢 active

> The standard lex-compatible scanner generator; table-driven DFA scanners its author timed 1.5-3.8x faster than AT&T lex in 1988.

| | |
|---|---|
| **Beats** | AT&T lex |
| **Claimed result** | AT&T lex 29.8 s vs flex 19.3 s with default table compression (\~1.5x, derived from page data), 9.0 s with flex -cfe (\~3.3x, derived from page data) and 7.8 s with flex -cf (\~3.8x, derived from page data); times are user + system CPU and exclude identifier hashing. Snippet only: read from WebSearch result text for comp.compilers 88-04-001, page not opened. |
| **Workload** | Generated C-language tokenizer (recognizing keywords, which the post says maximizes flex's advantage) run over a 28,088-line, 685K-character C input on a Sun 3/60 in April 1988; user + system CPU time, identifier hashing excluded (snippet only). |
| **Metric** | throughput |
| **Hardware** | Sun 3/60 (1988) |
| **Compiler and flags** | flex table options -cfe, -cf and default compression (1988 option syntax); AT&T lex; C compiler and flags not stated |
| **Adoption** | 4.0k stars, 568 forks; standard scanner generator shipped by Linux and BSD distributions |
| **Last commit** | 2026-07-30 |
| **Links** | [repository](https://github.com/westes/flex) · [benchmark](https://compilers.iecc.com/comparch/article/88-04-001) |

## Verdict

The only numbers are first-party and from 1988: Vern Paxson's comp.compilers post 88-04-001 (re-posted as 'old timings' in 90-11-063, November 1990) timed a C tokenizer with keywords on a 28,088-line, 685K-character input on a Sun 3/60: AT&T lex 29.8 s against flex 19.3 s with default tables (about 1.5x), 9.0 s with -cfe (3.3x) and 7.8 s with -cf (3.8x), user plus system CPU, identifier hashing excluded, compiler not stated. The same snippet lists object sizes (lex 41.0K, flex 9.4K, -cfe 49.6K, -cf 126.5K) and generation times (lex 83.0 s, flex 3.9 s, -cfe 7.1 s, -cf 15.0 s), so the 3.8x mode costs about 3x lex's object size; all of it is WebSearch snippet text because compilers.iecc.com is blocked here.

## Use it when

- Lexing ASCII or byte-oriented languages (C-like source, config files, log and protocol formats, DSLs) inside an existing lex/yacc or Bison toolchain.
- Large keyword-plus-identifier rule sets: run-time cost per character is independent of rule count, and -Cfe is the manual's recommended speed/size compromise for production scanners.
- Keeping existing POSIX lex specifications building on current Linux and BSD systems, where flex is the shipped scanner generator.
- Multi-threaded C programs that need several independent scanners: %option reentrant keeps all state in a yyscan_t, and the manual says any thread may run its own scanner without synchronization.
- When a 2-3x gain over default flex tables is enough and larger tables are acceptable: switch from default -Cem to -Cfe, -Cf or -CF and remove the backing-up states reported by -b.

## Skip it when

- Unicode-aware lexing: flex processes 8-bit bytes only; UTF-8 has to be written as byte-sequence regexes (the manual supplies one) and there are no Unicode classes or properties.
- Peak throughput: catalogued alternatives beat flex's table-driven loop (LRSTAR claims 2x flex-generated lexers; simd-lexing reports 34 ms against 231 ms for default flex and 102 ms for flex --fast; StreamTok claims 2-3x).
- Specifications that rely on REJECT, variable-length trailing context or long newline-spanning tokens under yylineno: the manual ranks these as the most expensive features, REJECT cannot be combined with -f/-F, and -l lex-compat costs 'a considerable amount of performance' and rules out -Cf/-CF/-f/-F/-+.
- Inputs with many NUL bytes or very large single tokens: NUL matching is substantially slower, and growing yytext past roughly 8K characters rescans the whole token from its start.
- Rule sets with large bounded repetitions: generation time can explode (open issue #326: ([a-f]|[x-z]){1,256}[x]{1,1024} takes 45 s, real cases 15 minutes) and specifications above 32000 NFA states are rejected (open issue #572).

## How it is fast

All rules are compiled into one deterministic finite automaton, so per-character cost does not depend on the number of rules (the manual: adding rules does not slow the scanner). The default -Cem tables are compressed with equivalence classes (yy_ec), meta-equivalence classes (yy_meta) and a base/def/nxt/chk comb-vector layout that may walk default-state chains per character; -Cf emits a full yy_nxt[state][class] matrix and -CF a per-state transition-record array checked by yy_verify, giving one table load per character (manual FAQ: 'factor of 2-3' over -C). Input is block-buffered (YY_BUF_SIZE defaults to 2\*BUFSIZ), -f/-F bypass stdio with read(), and removing every backing-up state lets -Cf/-CF scanners skip backtracking bookkeeping.

## Compared with alternatives

Pick flex when you need a POSIX lex-compatible generator that every Unix and Bison toolchain already supports; LRSTAR (claimed 2x faster lexers) and StreamTok (claimed 2-3x) are niche or research tools and simd-lexing is an experiment, not a generator. Pick logos (Rust), Accelerated-Zig-Parser-style SIMD tokenizers or a hand-written lexer (as CrossDB did) when throughput matters more than lex compatibility.

## Integration

| | |
|---|---|
| **Form** | source-drop (code generator: flex emits lex.yy.c or lex.yy.cc that you compile; optional libfl static library supplies default yywrap()/main()) |
| **Dependencies** | Generated scanner: C standard library only (std::istream/ostream for the -+ C++ class; read() with -Cr/-f/-F). The flex tool needs m4 on PATH at generation time; building flex from git needs Autoconf 2.62+, gettext 0.19.6 and the autotools chain (release tarballs ship intermediate files prebuilt). |
| **Minimum toolchain** | Generated code is C99 (the manual says flex emits C99 function definitions only; K&R output was removed); the C++ class needs a standard C++ compiler with &lt;iostream&gt;. |
| **Platforms** | Any platform with a C99 compiler for the generated scanner (portable tables, no architecture-specific code); the flex tool targets POSIX-like systems. |
| **Thread safety** | Default scanners keep state in globals and are not thread-safe. %option reentrant (-R) puts state in a yyscan_t and the manual calls such scanners safe in separate threads without synchronization (one scanner per thread); each C++ yyFlexLexer object holds its entire scanning state. |
| **Drop-in for the baseline** | partial — accepts POSIX lex input and generates the lex interface (yylex, yytext, yyleng, yywrap); -l/%option lex-compat gives closer but explicitly not full AT&T lex compatibility, at a considerable speed cost and without -Cf/-CF/-f/-F/-+. |

## Gotchas

- The fastest modes have sharp edges: -Cf/-CF default to 7-bit tables unless flex was configured otherwise, and the manual says 7-bit scanners 'often hang or crash' on 8-bit input (pass -8 or use -Cfe/-CFe); open issue #628 (February 2024, no fix or maintainer reply) reports an AddressSanitizer global-buffer-overflow in -CF -8 scanners on the two-byte input 0x00 0xFF, inside the yy_verify transition loop.
- Table speedups only show if every backing-up state is removed (run -b, add error or catch-all rules); leaving one gives no gain. -CF and -F cannot be used with the -+ C++ class, and the C++ class is still documented as experimental; the default error handlers (YY_FATAL_ERROR, LexerError) exit the process.
- The last release is 2.6.4 (6 May 2017), which distributions ship; master's manual documents unreleased work (an --emit back-end switch with a c99 back end, yybegin()/yyecho()/yyreject() replacing BEGIN/ECHO/REJECT, which remain in the C/C++ back end), so check documentation against the installed version.
- Regenerate scanners produced by flex 2.5.36 to 2.6.0: CVE-2016-6354 is a heap overflow in the generated yy_get_next_buffer, fixed in 2.6.1. Section-1 code and actions pass through m4, so '[[', ']]' and m4_ names in user code are mangled.

## Known shortcomings

- Evidence is the author's 1988 comp.compilers post (lex 29.8 s vs flex 19.3/9.0/7.8 s) seen only as a search snippet; compilers.iecc.com was blocked, so the article is unconfirmed and the repo has no lex timings. A session that can reach compilers.iecc.com should confirm it.
- Enricher: the 1988 comp.compilers table (88-04-001, Paxson; repeated in 90-11-063) shows flex -cf at 3.8x lex run speed but a 126.5K vs 41.0K object and generation 83.0 s (lex) vs 3.9 s; snippet only, no harness. Fastest mode has an open ASan global-buffer-overflow (#628, -CF -8 scanner, since Feb 2024); -Cf/-CF default to 7-bit tables that often hang or crash on 8-bit input; generation blowup #326 (45 s) and a 32000 NFA-state cap (#572). Last release 2.6.4 (May 2017); CVE-2016-6354 in scanners generated by 2.5.36-2.6.0; byte-only, no Unicode. Licence is BSD-3-Clause-flex.

## Caveats and trade-offs

SNIPPET ONLY: the lex vs flex timings come from WebSearch result text attributed to comp.compilers article 88-04-001 ('Re: replacements for LEX: flex, ... , Rex', April 1988, described in the snippet as a reply by Vern Paxson, flex's author, so first-party); article 90-11-063 ('Re: Flex speed') also surfaced and may repeat the same 'old timings'. compilers.iecc.com is blocked by the egress proxy, so the page was never opened and the attribution is not pinned beyond the snippets. Timings are from 1988 hardware, 1988 flex and AT&T lex, with 1988 option syntax. The flex repository (README, NEWS, ONEWS, doc/flex.texi) contains no lex timings; its manual only says -f/-F is 'much faster (factor of 2-3)' than -C (flex against itself) and that -l AT&T-lex compatibility costs performance. Search snippets also say re2c -b scanners are faster than flex -Cf ones. COPYING is flex's own BSD-style text (two numbered conditions plus a no-endorsement paragraph, functionally BSD-3-Clause); GitHub does not identify it and the awesome-c list tags it BSD-2-Clause. [retier] Evidence is Paxson's 1988 comp.compilers post 88-04-001 (repeated as 'old timings' in 90-11-063), seen only as a search snippet since compilers.iecc.com is blocked: lex 29.8 s vs flex 19.3/9.0/7.8 s run time (flex -cf 3.8x), with a 126.5K vs 41.0K object and scanner generation 83.0 s (lex) vs 3.9 s; no harness code, author's own numbers, the repo has no lex timings. The fastest -CF mode has an open ASan global-buffer-overflow (#628, since Feb 2024) and -Cf/-CF default to 7-bit tables that often hang or crash on 8-bit input; generation blowup #326 (45 s), 32000 NFA-state cap #572. Last release 2.6.4 (May 2017) while master documents unreleased --emit backends; CVE-2016-6354 in scanners generated by 2.5.36-2.6.0; byte-only, no Unicode.

Table-driven DFA scanners; the fastest modes (-Cf, -CF) trade large tables for speed. Matching NUL bytes is slow. Interactive scanners are slower. The -l lex-compatibility option is documented as a major performance loss. Lexer only, no Unicode-aware matching.

## Maintenance

Maintained in the sense of dependency bumps and occasional fixes (last commit 30 July 2026, last code fix May 2026) with no release since 2.6.4 in May 2017; the licence is flex's BSD variant (source files now carry SPDX BSD-3-Clause-flex), and the tool is ubiquitous and safe to depend on, but the speed claim rests on a 1988 first-party snippet with no benchmark code to audit and no modern flex-against-lex measurement was found, so treat it as historical.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are the flex author's own 1988 timings against AT&T lex (Sun 3/60, 28,088-line C input), which three WebSearch queries attribute to comp.compilers article 88-04-001 (a reply by Vern Paxson); compilers.iecc.com is EGRESS_BLOCKED, so they are snippet only. First-party, no benchmark code, no compiler or flags: C at most, and nothing in the repository (README, NEWS, ONEWS, doc/flex.texi) carries lex timings.
- **Verifier notes:** Kept at C instead of the null-URL D rule because three separate WebSearch queries returned the exact same numbers attributed to comp.compilers 88-04-001; benchmark_url set to that article, but it was NOT opened (EGRESS_BLOCKED) and page_compares/numbers_found are null for that reason; a session with compilers.iecc.com access should confirm the article or drop the tier to D. Metadata verified on github.com: 4.0k stars, 568 forks, not a fork, not archived, last commit 2026-07-30 (active), COPYING read. Notable regardless of tier (standard lex replacement).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `stars_or_usage`, `caveats`, `license`
- **Shortcomings recorded by:** comp.compilers 88-04-001 snippet (verifier); enricher snippet and code reading
- **Pages the verifier opened:**
  - <https://github.com/westes/flex>
  - <https://github.com/westes/flex/commits/master.atom>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/COPYING>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/README.md>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/NEWS>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/ONEWS>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/doc/flex.texi>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/westes/flex/HEAD/README.md>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/NEWS>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/doc/flex.texi>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/COPYING>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/src/gen.c>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/src/cpp-flex.skl>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/src/c99-flex.skl>
  - <https://raw.githubusercontent.com/westes/flex/HEAD/src/FlexLexer.h>
  - <https://github.com/westes/flex/releases>
  - <https://github.com/westes/flex/commits/master>
  - <https://github.com/westes/flex/issues?q=is%3Aissue+performance>
  - <https://github.com/westes/flex/issues?q=is%3Aissue+CVE>
  - <https://github.com/westes/flex/issues/628>
  - <https://github.com/westes/flex/issues/326>
  - WebSearch snippets for https://compilers.iecc.com/comparch/article/88-04-001 and https://compilers.iecc.com/comparch/article/90-11-063 (pages EGRESS_BLOCKED)
  - WebSearch snippets for CVE-2016-6354 (security-tracker.debian.org, ubuntu.com)
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/westes/flex`) · [data/wave3/enrich/raw/github_com_westes_flex.json](../../../data/wave3/enrich/raw/github_com_westes_flex.json) (enrichment confidence 0.7)

</details>
