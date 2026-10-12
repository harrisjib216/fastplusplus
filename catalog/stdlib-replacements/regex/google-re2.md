# RE2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Regex](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Linear-time, non-backtracking C++ regex engine beating classic PCRE on untrusted input; loses to PCRE2 JIT and Hyperscan.

| | |
|---|---|
| **Beats** | PCRE |
| **Claimed result** | Table 5 (seconds): RE2-s beats PCRE v8.41 (JIT enabled per the paper): Talos 6942s -&gt; 1777s (\~3.9x); ET-Open 12800s -&gt; 4696s (\~2.7x) (derived from page data). RE2-s is slower than PCRE2 v10.32 JIT (1777 vs 394 s; 4696 vs 913 s). In multi-regex mode RE2-m beats serially-run PCRE2 on Talos (29 s vs 394 s, \~13.6x, derived from page data) but not on ET-Open (1116 s vs 913 s). Paper states Hyperscan-s beats RE2-s by 10.3x/9.1x. |
| **Workload** | Same NSDI'19 Hyperscan-paper experiment: total wall-clock time for single-regex serial matching (RE2-s) of Snort Talos (1,300 regexes) and Suricata ET-Open (2,800 regexes) rulesets against a 1GB real HTTP traffic trace, single CPU core. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8180 CPU @ 2.50GHz, 48GB memory, single core |
| **Compiler and flags** | GCC 5.4; RE2 v2018-09-01; PCRE v8.41 and PCRE2 v10.32 with JIT enabled ('We enable the JIT option for both PCRE and PCRE2'); PCRE/PCRE2 match one regex at a time, and totals were measured serially for all engines' -s modes; optimization flags not stated. |
| **Adoption** | 9.8k stars; used in production at Google since 2006 and widely elsewhere |
| **Last commit** | 2026-01-22 |
| **Links** | [repository](https://github.com/google/re2) · [benchmark](https://www.usenix.org/system/files/nsdi19-wang-xiang.pdf) |

## Verdict

Third-party NSDI'19 Hyperscan paper (Xeon Platinum 8180, single core, GCC 5.4): RE2 serial mode beat JIT-enabled PCRE 8.41 by \~3.9x on Talos (6942s-&gt;1777s) and \~2.7x on ET-Open (12800s-&gt;4696s), but lost to JIT-enabled PCRE2 10.32 (1777s vs 394s; 4696s vs 913s) and to Hyperscan by \~9-10x; separately, WG21 paper P1433R0 found RE2 far faster than libstdc++/libc++ std::regex on a 1.3GB CSV scan, though with no hardware/flags stated.

## Use it when

- Untrusted or user-supplied regex patterns/input where guaranteed linear-time matching (no ReDoS/catastrophic backtracking) is a security requirement.
- Serial single-regex matching against classic non-JIT PCRE as the baseline: measured \~3.9x (Talos) and \~2.7x (ET-Open) faster on the NSDI'19 HTTP-traffic benchmark.
- C++17+ codebases already depending on Abseil that want a mature (production at Google since 2006), widely used (9.8k stars) engine.
- Need safe submatch extraction on adversarial input without recursion/stack-overflow risk.
- std::regex is the actual baseline: third-party WG21 paper P1433R0 found RE2 roughly 9x-160x faster than libstdc++/libc++ std::regex on a 1.3GB CSV scan.

## Skip it when

- Need backreferences or lookaround assertions — unsupported by design; a 'bounded lookaround' implementation (issue #585, open since Feb 2026) is only a proof of concept, not merged.
- Raw single-regex throughput matters more than backtracking safety and PCRE2 JIT or Hyperscan is available — RE2 lost to PCRE2 10.32 JIT (1777s vs 394s Talos; 4696s vs 913s ET-Open) and to Hyperscan by 9-10x in the same paper.
- Extracting many capturing groups per match on a hot path — GitHub issue #204 reports captures making RE2 \~10x slower than non-capturing matches, ending up slower than PCRE with captures on.
- Need a PCRE-compatible API/syntax for a true drop-in migration — RE2 requires rewriting call sites and possibly patterns.
- Unicode-heavy patterns where compile time matters — issue #46 reports Unicode regex compilation is noticeably slower; RE2 also does no Unicode normalization itself.

## How it is fast

RE2 compiles a pattern to an automaton and executes it with Thompson-NFA/lazy-DFA style simulation that evaluates all alternatives in parallel instead of backtracking, so match time is asymptotically linear in input length regardless of pattern shape, and there is no catastrophic-backtracking worst case like non-JIT PCRE. It uses no SIMD and no JIT compiler of its own — maintainers closed a request (issue #383) to add x86 SIMD to close the gap with Hyperscan — which is exactly why it loses to PCRE2's JIT and to Hyperscan in the cited benchmark.

## Compared with alternatives

Pick RE2 over CTRE when the pattern is runtime-supplied or untrusted (user input, config-driven regexes) rather than known at compile time, or when the toolchain is C++17 without C++20; CTRE beats std::regex by \~10x-125x via compile-time NFA generation but requires the pattern to be a compile-time constant, which RE2 does not.

## Integration

| | |
|---|---|
| **Form** | static lib (also buildable as shared lib via CMake/Bazel, or vendored as source via CMake add_subdirectory) |
| **Dependencies** | Abseil (required); optional ICU for extended \p/\P Unicode properties (RE2_USE_ICU); GoogleTest + Benchmark needed only to build tests/benchmarks |
| **Minimum toolchain** | C++17; build via GNU make, CMake, or Bazel (Bazelisk); Visual Studio 2019+ on Windows |
| **Platforms** | any — Linux, macOS, Windows (VS2019+, MinGW, Cygwin/MSYS); no SIMD or specific-arch requirement documented |
| **Thread safety** | RE2 objects are documented thread-safe and logically immutable once constructed ('safe for concurrent use by multiple threads', re2.h); LazyRE2 is provided for careful lazy static initialization across threads. |
| **Drop-in for the baseline** | partial — explain: RE2::FullMatch/PartialMatch and StringPiece/absl::string_view outputs replace PCRE's pcre_exec/ovector, and the syntax subset drops backreferences and lookaround, so call sites and possibly patterns must be rewritten. |

## Gotchas

- Capturing submatches is expensive: issue #204 measured captures making RE2 \~10x slower than non-capturing matches (2800ns vs 250ns in that benchmark), ending up slower than PCRE with captures enabled.
- No SIMD or JIT of its own, so throughput on modern hardware trails PCRE2 JIT and Hyperscan; maintainers closed a request to add x86 SIMD (issue #383).
- Backreferences and lookaround are unsupported by design; 'bounded lookaround' (issue #585) is an open proof-of-concept, not shipped.
- No Unicode normalization: a codepoint form and a combining-character form of the 'same' character won't match unless normalized before use (README).

## Caveats and trade-offs

RE2's own benchlog files (benchlog.c2/.mini/.r70/.wreck) only compare against classic PCRE on old hardware (Core2 T5600, Opteron 8214 HE, MacPro1,1), with no PCRE2 or std::regex. The only methodologically documented numbers are from the third-party NSDI'19 Hyperscan paper (written by Hyperscan developers). There, RE2 beats JIT-enabled PCRE v8.41, loses to PCRE2 JIT in single-regex mode, and beats PCRE2 only in multi-regex mode on the Talos ruleset. Separately, WG21 paper P1433R0 (by the CTRE author, no hardware/flags stated) reports RE2 3.759 s vs std::regex (libstdc++) 33.585 s and RE2 10.35 s vs std::regex (libc++) 1655 s on a \~1.3 GB CSV scan (C-level evidence). Baseline recorded is PCRE, not std::regex/PCRE2, so baseline_in_list=false.

Linear-time guarantee (no catastrophic backtracking) trades away backreferences and lookaround; RE2's own README explicitly disclaims being a universal speed leader ('It is not a goal to be faster than all other engines under all circumstances'); in this benchmark RE2 loses outright to PCRE2's JIT compiler despite beating classic PCRE.

## Maintenance

Actively maintained (last commit 2026-01-22, not archived or a fork), BSD-3-Clause, used in Google production since 2006; not header-only but the source is small and copyable/vendorable via CMake add_subdirectory.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification B, tier now B.
- **Tier reason:** NSDI'19 is peer-reviewed and third-party to RE2. Its Table 5 shows RE2-s (1,777 s / 4,696 s) beating PCRE v8.41 (6,942 s / 12,800 s) on Talos/ET-Open, with CPU, GCC 5.4 and library versions stated. No harness or artifact is public, and the traffic trace is private, so it is B.
- **Verifier notes:** Numbers verified in Table 5. The record wrongly called PCRE 'classic (non-JIT)': the paper enabled JIT for both PCRE and PCRE2. Fixed that and added the RE2-m vs PCRE2 Talos result plus the P1433R0 std::regex datapoint. Metadata checks out: BSD-3-Clause, 9,803 stars, last commit 2026-01-22, not archived or a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/nsdi19-wang-xiang.pdf>
  - <https://github.com/google/re2>
  - <https://github.com/google/re2/tree/main/benchlog>
  - <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1433r0.pdf>
- **Sources the enricher read:**
  - <https://github.com/google/re2>
  - <https://github.com/google/re2/blob/main/re2/re2.h>
  - <https://github.com/google/re2/issues/383>
  - <https://github.com/google/re2/issues/204>
  - <https://github.com/google/re2/blob/main/SECURITY.md>
  - <https://github.com/google/re2/issues/585>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/google/re2`) · [data/wave0-seed/enrich/raw/github_com_google_re2.json](../../../data/wave0-seed/enrich/raw/github_com_google_re2.json) (enrichment confidence 0.6)

</details>
