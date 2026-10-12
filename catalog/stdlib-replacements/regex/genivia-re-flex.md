# RE/flex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Regex](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Flex-style C++ lexer generator plus a multi-engine regex matcher library; DFA scanners far outrun std::regex, PCRE2, and Boost.Regex at tokenizing.

| | |
|---|---|
| **Beats** | std::regex |
| **Claimed result** | 8.7 us (reflex --fast --noindent), 8.9 us (--fast) and 20.6 us (--full), all RE/flex 3.4.1, vs 6490 us for std::cregex_iterator() (C++11 std::regex): \~315x-746x faster on this tokenizing workload. In the same table RE/flex --fast also beats PCRE2 JIT (60.8 us), PCRE2 non-JIT (500 us), Boost.Regex perl (205 us), Boost.Regex POSIX (392 us) and RE2 (218 us). |
| **Workload** | Tokenizing a 2 KB representative C source file into 244 tokens; elapsed time in microseconds, averaged over 1000-10000 benchmark runs, comparing reflex-generated scanners against Flex, Boost.Spirit.Lex, PCRE2 (JIT/DFA), Hyperscan, RE2, GNU POSIX regex, and std::regex (std::cregex_iterator). |
| **Metric** | latency |
| **Hardware** | 2.9 GHz Intel Core i7, 16 GB 2133 MHz LPDDR3, Mac OS X 12.6.9 |
| **Compiler and flags** | clang 12.0.0 -O2 |
| **Adoption** | 599 stars; used by ugrep and the Tiger Compiler |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/Genivia/RE-flex) · [benchmark](https://github.com/Genivia/RE-flex/blob/master/README.md) |

## Verdict

On a 2 KB representative C source file tokenized into 244 tokens, a reflex --fast --noindent generated scanner (RE/flex 3.4.1) measured 8.7 us versus 6490 us for std::cregex_iterator (C++11 std::regex, libc++ inferred from platform) — about 746x faster — measured with clang 12.0.0 -O2 on a 2.9 GHz Intel Core i7 / 16 GB LPDDR3 Mac running macOS 12.6.9. The repo is now at 6.5.0; the std::regex leg was run through RE/flex's own std-ecma matcher adapter with one large alternation pattern rather than a hand-written std::regex loop.

## Use it when

- Tokenizing/scanning a stream into many tokens (lexer/parser front-ends) where std::regex's per-call setup and backtracking overhead dominate
- Building a Flex/Bison-based C++ toolchain and wanting Unicode-aware, POSIX-compliant scanning with less porting effort than plain Flex++
- Need indent/dedent-sensitive tokenizing (Python-like languages) or multi-encoding (UTF-8/16/32, legacy code pages) file input
- Want one API that can fall back to PCRE2 or Boost.Regex for fuller Perl syntax while keeping the fast DFA engine on the hot path
- Large text/file scanning workloads (RE/flex backs ugrep) where guaranteed linear-time DFA matching is preferable to std::regex's backtracking risk

## Skip it when

- Need capture groups with RE/flex's own fast engine: not supported natively (open issue #95, only non-capturing groups); must switch to PCRE2Matcher/BoostMatcher/StdMatcher and give up some speed
- Need backreferences or lookaround: the native engine is IEEE POSIX P1003.2-compliant DFA matching, which structurally excludes these (only the PCRE2/Boost adapters support them)
- Only need a handful of ad hoc regex checks in otherwise std::regex-shaped code: the reflex code-generation step plus a libreflex build add more integration surface than warranted
- Pattern shapes with a leading unanchored wildcard (e.g. `.*literal`) used with Matcher::find(): one reported benchmark (#220) showed \~15000x slowdown versus removing the leading `.*`, so verify your actual pattern shape
- Strict correctness under MemorySanitizer: issue #234 reports a use-of-uninitialized-value warning in AbstractMatcher::reset_text() via text()

## How it is fast

The native RE/flex regex engine compiles patterns to a DFA using a backtrack-free lazy-matching transformation (credited to Robert van Engelen) that matches in linear time without backtracking, unlike std::regex's NFA engine. Generated scanners run as compact FSM code rather than re-entering a general matching engine per token. Matcher::find() and related search paths additionally use runtime-dispatched SIMD (SSE2/AVX2/AVX512BW on x86, NEON/AArch64 on Arm) to accelerate scanning for the next candidate match.

## Compared with alternatives

Pick RE/flex over Boost.Regex, REAL, or Unformat when the job is generating a real tokenizer/scanner (many tokens per input, Flex/Bison-style workflow) rather than replacing scattered std::regex match/search calls; Boost.Regex and REAL are closer to a source-level drop-in for individual std::regex call sites with far less build/integration surface.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib |
| **Dependencies** | none required; PCRE2 and Boost.Regex are optional, only needed if you use reflex::PCRE2Matcher or reflex::BoostMatcher |
| **Minimum toolchain** | C++11 (CMAKE_CXX_STANDARD 11 in CMakeLists.txt); strview() needs C++17 |
| **Platforms** | Windows, macOS, Linux, NetBSD, BSD; x86-64 with SSE2/AVX2/AVX512BW auto-detected at runtime (configure --disable-avx / --disable-sse2 to turn off), aarch64/NEON supported for search, portable C++ fallback otherwise |
| **Thread safety** | not documented as a formal guarantee; README states multiple generated lexer classes can be used by multiple threads, implying each thread should own its own matcher/lexer instance rather than share one |
| **Drop-in for the baseline** | partial — explain: reflex::StdMatcher wraps std::regex behind RE/flex's own API (not source-compatible with std::regex/std::smatch code), and the fast native engine additionally requires a build-time code-generation step (the reflex tool), so no matcher class is a header-swap drop-in for std::regex |

## Gotchas

- Native Matcher has no capture groups (non-capturing groups only); this is a known, still-open design gap, not a bug that will be fixed soon
- A leading unanchored `.*` in a pattern used with find() can be \~15000x slower than the equivalent anchored/literal search on the same input (issue #220)
- libreflex is a real build artifact (libreflex.a/.so via configure/make or CMake), not a header you can just #include and go
- SIMD (AVX2/AVX512BW) is auto-detected at runtime by default; disable via configure flags if you hit CPU-detection or build issues on older toolchains

## Caveats and trade-offs

This is the author's own benchmark. The harness is an external zip on genivia.com (perfcomp.zip, dated Sept 2023), not committed to the git repo. It was measured with RE/flex 3.4.1, while the repo is now at 6.x. The std::regex figure comes from running std::regex through RE/flex's std-ecma matcher adapter with one large alternation pattern, not a hand-written std::regex loop. libc++ is inferred from macOS/clang, not stated explicitly.

RE/flex is a Flex-style lexical-analyzer generator (requires a code-generation step to build a DFA-based scanner), not a drop-in std::regex object; PCRE2/Boost.Regex are optionally integrated for Perl-style matching, otherwise matching is DFA-based and linear-time; larger API/build surface than std::regex.

## Maintenance

Actively maintained (last commit 2026-09-15, now versioned 6.5.0 vs. the benchmarked 3.4.1) and BSD-3-Clause/copyable, but the reflex code-generation step and libreflex build make it heavier to vendor than a header-only std::regex replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The README table and note state clang 12.0.0 -O2, a 2.9 GHz Intel Core i7 with 16 GB LPDDR3, and Mac OS X 12.6.9. The README's linked 'Download the tests' artifact (genivia.com/files/perfcomp.zip, live) contains the Makefile and sources, including the std::regex leg: target stdecmatest, built from ecmareflextest.l with reflex -m=std-ecma, -std=c++11 -O2.
- **Verifier notes:** The numbers match the README exactly; the record only garbled the PCRE2 and Boost ranges, now fixed. Metadata verified: BSD-3-Clause, 599 stars, last commit 2026-09-15, not a fork. The README confirms use by ugrep and the Tiger Compiler.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Genivia/RE-flex/blob/master/README.md>
  - <https://github.com/Genivia/RE-flex>
  - <https://www.genivia.com/files/perfcomp.zip>
- **Sources the enricher read:**
  - <https://github.com/Genivia/RE-flex>
  - <https://github.com/Genivia/RE-flex/blob/master/README.md>
  - <https://github.com/Genivia/RE-flex/blob/master/CMakeLists.txt>
  - <https://github.com/Genivia/RE-flex/blob/master/configure.ac>
  - <https://github.com/Genivia/RE-flex/issues/95>
  - <https://github.com/Genivia/RE-flex/issues/220>
  - <https://github.com/Genivia/RE-flex/issues/234>
  - <https://github.com/Genivia/RE-flex/issues?q=bug>
  - <https://github.com/Genivia/RE-flex/issues?q=performance>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/genivia/re-flex`) · [data/wave1/enrich/raw/github_com_genivia_re_flex.json](../../../data/wave1/enrich/raw/github_com_genivia_re_flex.json) (enrichment confidence 0.8)

</details>
