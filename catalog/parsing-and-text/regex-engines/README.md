# Regex engines

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md)</sub>

**What these beat:** PCRE2, RE2, std::regex, Rust regex  
**12 entries:** 2 tier A · 3 tier B · 7 tier C · 0 tier D · 11 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**nim-regex (nitely/regex)**](nitely-nim-regex.md) | Pure-Nim linear-time regex engine (PCRE-like syntax, no backtracking) beating PCRE2 on find-all throughput. | **A** | Nim | MIT | 🟢 active |
| 2 | [**SafeRE**](eaftan-safere.md) | Linear-time, ReDoS-proof Java regex engine; drop-in java.util.regex replacement, RE2 port, 2.22x faster on real-world workloads. | **A** | Java | BSD-3-Clause | 🟢 active |
| 3 | [**Hyperscan**](intel-hyperscan.md) | SIMD multi-pattern regex matching library beating PCRE2 6.9-183x on large network-security rulesets. | **B** | C | BSD-3-Clause | 🟢 active |
| 4 | [**RE# (Resharp)**](ieviev-resharp-dotnet.md) | Automata-based .NET/F# regex engine beating Rust's regex crate on rebar benchmarks; adds intersection, complement, lookarounds. | **B** | F# | MIT | 🟢 active |
| 5 | [**BLARE (Blazingly Fast Regular Expression)**](mush-zhang-blare.md) | Research framework that decomposes regexes into reordered sub-matches via a bandit-picked plan, layered on RE2/PCRE2/Boost/ICU. | **B** | C++ | no license (study only) | 🟡 stale |
| 6 | [**Vectorscan**](vectorcamp-vectorscan.md) | Portable BSD fork of Intel Hyperscan multi-regex matcher for ARM, Power and x86; 1.4-3.6x faster Snort 3 on ARM routers. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 7 | [**coregex**](coregx-coregex.md) | Drop-in Go regexp replacement using 17 pattern-specific engines and SIMD prefilters; beats Rust regex on literal-heavy patterns only. | **C** | Go | MIT | 🟢 active |
| 8 | [**regexr (Rust regex engine with x86-64/ARM64 JIT)**](ml-rust-regexr.md) | Pure-Rust regex engine with lookarounds, backreferences and an x86-64/AArch64 JIT; claims up to 4x over the regex crate. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 9 | [**nanoregex**](justrach-nanoregex.md) | Pure-Zig regex engine beating Python's re module on 6 of 7 README benchmark patterns. | **C** | Zig | MIT | 🟢 active |
| 10 | [**SRELL**](akenotsuki-com-misc-srell-en.md) | Header-only ECMAScript regex engine with the std::regex class design; a 2023 competitor shootout timed it far ahead of std::regex. | **C** | C++ | BSD-2-Clause | 🟢 active |
| 11 | [**rejit**](coreperf-rejit.md) | Prototype non-backtracking JIT regex compiler for x86-64 that beats RE2 and grep on throughput, unmaintained since 2015. | **C** | C++ | GPL-3.0 | 🔴 abandoned |
| 12 | [**re2jit**](pyos-re2jit.md) | JIT-compiles RE2's NFA to x86-64 machine code; beats RE2 on capture groups and Unicode classes. | **C** | C++ | MIT | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
