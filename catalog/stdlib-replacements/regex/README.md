# Regex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::regex  
**9 entries:** 3 tier A · 3 tier B · 3 tier C · 0 tier D · 9 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**PCRE2**](pcre2project-pcre2.md) | Mature C library for Perl-compatible regex matching; 4-12x faster than libstdc++'s std::regex on find-and-count benchmarks. | **A** | C | BSD-3-Clause WITH… | 🟢 active |
| 2 | [**RE/flex**](genivia-re-flex.md) | Flex-style C++ lexer generator plus a multi-engine regex matcher library; DFA scanners far outrun std::regex, PCRE2, and Boost.Regex at tokenizing. | **A** | C++ | BSD-3-Clause | 🟢 active |
| 3 | [**Boost.Regex**](boostorg-regex.md) | Header-only successor to std::regex: same backtracking engine, hand-tuned matcher and pooled allocation for real throughput gains. | **A** | C++ | BSL-1.0 | 🟢 active |
| 4 | [**RE2**](google-re2.md) | Linear-time, non-backtracking C++ regex engine beating classic PCRE on untrusted input; loses to PCRE2 JIT and Hyperscan. | **B** | C++ | BSD-3-Clause | 🟢 active |
| 5 | [**TRE**](laurikari-tre.md) | POSIX regex library in C with a linear-time tagged-NFA matcher and fuzzy matching; beats interpreted PCRE2 only on backtracking-hostile patterns. | **B** | C | BSD-2-Clause | 🟢 active |
| 6 | [**Oniguruma**](kkos-oniguruma.md) | Ruby-style backtracking regex library in C; beats std::regex on every shared pattern and interpreted PCRE2 on some, not PCRE2-JIT. | **B** | C | BSD-2-Clause | 🔴 abandoned |
| 7 | [**CTRE (compile-time regular expressions)**](hanickadot-compile-time-regular-expressions.md) | Header-only C++ template-metaprogramming regex engine for compile-time-known patterns, with large wall-clock wins over std::regex. | **C** | C++ | Apache-2.0 | 🟢 active |
| 8 | [**Unformat**](adamyaxley-unformat.md) | Single-header scanf-style '{}' field extractor for fixed-shape strings; beats std::regex when regex is overkill. | **C** | C++ | Unlicense | 🟢 active |
| 9 | [**REAL (real-regex)**](reche23-real-regex.md) | Header-only C++20 linear-time regex engine with lookaround support, beating std::regex 8x-152x and RE2 on every supported pattern. | **C** | C++ | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
