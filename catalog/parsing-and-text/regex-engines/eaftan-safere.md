# SafeRE

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Regex engines](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `BSD-3-Clause` · 🟢 active

> Linear-time, ReDoS-proof Java regex engine; drop-in java.util.regex replacement, RE2 port, 2.22x faster on real-world workloads.

| | |
|---|---|
| **Beats** | java.util.regex (JDK) |
| **Claimed result** | Geometric mean 2.22x faster than JDK java.util.regex on the 150-row real-world matrix (1.88x without the 2 pathological backtracking rows), but 22% slower than JDK on Core and 7% slower on Application. 12.5x faster than RE2/J and 3.06x faster than RE2-FFM on the real-world matrix. Against native engines on the real-world matrix, SafeRE is 13% slower than C++ RE2 (150 rows), takes 2.03x as long as Rust regex (150 rows) and 2.47x as long as PCRE2 JIT (only 48 supported rows). It is 1.32x faster than native RE2 on Core. |
| **Workload** | JMH microbenchmarks: 150-row real-world matrix (25 patterns x match/no-match x 1K/10K/100K input sizes), plus 8 'Core' and 8 'Application' workloads, run against java.util.regex (JDK), RE2/J, RE2-FFM (Java FFM binding to native C++ RE2), native C++ RE2, PCRE2 JIT, Go regexp, Rust regex crate, and .NET's non-backtracking engine. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-11700K, 8 cores/16 threads, 3.6 GHz base, 16 GiB RAM under WSL2, Ubuntu 24.04 on Windows 11 host, Linux 6.6.87.2-microsoft-standard-WSL2 |
| **Compiler and flags** | Java: OpenJDK 26.0.2+10-55 targeting Java 21, JMH 1.37 (2 forks, 2 warmup iters x500ms, 5 measurement iters x500ms); C++: g++ 13.3.0, -O3 -DNDEBUG, RE2 snapshot 2025-11-05; PCRE2 10.47 with JIT enabled; Go 1.26.1 linux/amd64; Rust rustc 1.97.1 with regex 1.13.1; .NET SDK 10.0.110 |
| **Adoption** | 20 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/eaftan/safere) · [benchmark](https://github.com/eaftan/safere/blob/main/BENCHMARKS.md) |

## Verdict

On the project's own JMH suite (OpenJDK 26.0.2 targeting Java 21, JMH 1.37, Intel i7-11700K under WSL2/Ubuntu 24.04), SafeRE is a 2.22x geometric-mean win over java.util.regex across a 150-row real-world matrix (1.88x excluding 2 pathological-backtracking rows), but 22% slower than the JDK on 8 'Core' operations and 7% slower on 8 'Application' tasks; against native C++ RE2 (g++ 13.3.0 -O3), Rust regex 1.13.1, and PCRE2 10.47 JIT on the same real-world matrix it is 13%, 103%, and 147% slower respectively.

## Use it when

- Untrusted or user-supplied patterns where a JDK backtracking engine could hang (ReDoS); SafeRE rejects unsafe constructs at compile time and guarantees linear time.
- Java 21+ services replacing java.util.regex on workloads shaped like the 150-row real-world matrix (mixed pattern types, 1K-100K inputs, match and no-match) where the 2.22x geomean win was measured.
- JVM data/storage/network code that already holds text as UTF-8 bytes and wants to skip an input-sized UTF-8 to UTF-16 conversion before matching.
- Need to test many patterns against the same input in one pass (PatternSet).
- Willing to trade much slower pattern compilation for consistently bounded match latency.

## Skip it when

- Compile-heavy workloads (many distinct patterns compiled once or rarely reused): compilation is 71.2x slower than the JDK and 11.7x slower than RE2/J.
- Workloads shaped like the project's own Core/Application suites (short literal/class/API-style operations): SafeRE measured 22% and 7% slower than java.util.regex there.
- Need backreferences, lookahead/lookbehind, possessive quantifiers over consuming operands, or atomic groups -- all rejected at compile time, not silently degraded.
- Already running native C++/Rust/Go/.NET: SafeRE is 13% slower than C++ RE2, 2.03x slower than Rust regex, and 2.47x slower than PCRE2 JIT on the same real-world matrix.
- Need Matcher.hitEnd()/requireEnd() or exact JDK matcher-state parity after usePattern()/a terminal empty find() -- SafeRE intentionally diverges there.

## How it is fast

Like RE2, SafeRE compiles patterns to finite automata instead of a backtracking NFA, and picks among five engines per query (OnePass, DFA, BitState, Pike-VM NFA, and reverse DFA) to fit the query's structure. This avoids catastrophic backtracking entirely (0.089us vs the JDK's 17,079us on an adversarial a?{25}a{25} pattern) and, on the real-world 150-row matrix, comes out ahead of java.util.regex's backtracking overhead overall. A SWAR (and experimental incubating-Vector-API) byte scanner accelerates ASCII character-class/literal prefix scans on the UTF-8 input path.

## Compared with alternatives

None of the catalogued siblings target java.util.regex -- they beat RE2, PCRE2, Python re, or Rust regex directly. Pick SafeRE specifically when java.util.regex is your incumbent and you need a same-API, linear-time-guaranteed replacement; if you can drop java.util.regex API compatibility, RE2/J or a native RE2/PCRE2/Rust-regex binding will outrun SafeRE on the same benchmark matrix.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none for the core org.safere:safere artifact; the separate safere-ffm-re2 module adds a native RE2 FFM binding used only for benchmarking |
| **Minimum toolchain** | Java 21+ (built with JDK 26 targeting --release 21; CI verifies JDK 21 through 26) |
| **Platforms** | any JVM platform; optional experimental Vector API scanner needs a JDK 21+ incubator module flag and only covers UTF-8 prefix scans |
| **Thread safety** | Pattern is documented as thread-safe and reusable (README quick start); Matcher thread-safety is not documented, consistent with java.util.regex's stateful, non-thread-safe Matcher. |
| **Drop-in for the baseline** | partial — drop-in for java.util.regex.Pattern/Matcher on supported syntax, but backreferences, lookaround, possessive-over-consuming quantifiers, atomic groups, and CANON_EQ are rejected at compile time, hitEnd()/requireEnd() are unsupported, and a few matcher-state edge cases after usePattern() or a terminal empty find() intentionally diverge from the JDK. |

## Gotchas

- usePattern() keeps the prior match's group-zero bounds/text valid; JDK 26 instead nulls group() while leaving start()/end() non-throwing, an inconsistency SafeRE deliberately does not reproduce (tracked upstream as JDK-8390449).
- After a terminal empty find() at the region end, hasMatch() becomes false and start()/end()/group() throw IllegalStateException, whereas the JDK leaves inconsistent-but-non-throwing state; replaceAll/replaceFirst output text itself still matches the JDK.
- Unsupported syntax (backreferences, lookaround, possessive quantifiers over consuming operands, atomic groups, CANON_EQ) fails at Pattern.compile time with an explicit error rather than falling back silently.
- The experimental Vector scanner needs both --add-modules=jdk.incubator.vector and a system property; without both it silently keeps using the default SWAR scanner.

## Caveats and trade-offs

SafeRE is a from-scratch Java port of RE2's design (not a GitHub fork), so is_fork_of is null even though it is explicitly 'based on RE2'. GitHub reports the license as NOASSERTION because the LICENSE file is a compound notice, but the file text states both RE2 and RE2/J (and by extension this port) are BSD-3-Clause. Critically, on the primary 150-row real-world matrix, SafeRE is NOT faster than any of the three named baselines it tested that are on our incumbent list (RE2, PCRE2, Rust regex) -- it is slower than all three there; its clear win is only over java.util.regex, which is a widely used incumbent but not one of PCRE2/RE2/std::regex/Rust regex. This is an unusually rigorous, self-critical benchmark report (authors explicitly flag their own losses), which raises confidence in the numbers despite the mixed result.

71.2x slower to compile a pattern than the JDK (11.7x slower than RE2/J), and retains substantially more memory per compiled pattern, in exchange for guaranteed linear-time matching with no catastrophic-backtracking risk (e.g. 0.089us vs the JDK's 17,079us on an adversarial pattern). Cross-runtime ratios mix FFI/marshalling overhead with engine cost, so they are not pure same-runtime comparisons.

## Maintenance

Actively maintained (commits as recent as today, extensive open design docs and issue tracker) and published to Maven Central; BSD-3-Clause per pom.xml and the LICENSE text even though GitHub's license detector shows NOASSERTION because the LICENSE file bundles RE2's and RE2/J's notices.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The project's own JMH suite is public (safere-benchmarks/, run-java-benchmarks.sh, raw results under benchmark-results/published/516a1ff...). BENCHMARKS.md states OpenJDK 26.0.2 with JMH settings, g++ 13.3.0 -O3 -DNDEBUG for native RE2, and CPU i7-11700K, against java.util.regex, so A.
- **Verifier notes:** Numbers match BENCHMARKS.md. I fixed one inaccuracy: the PCRE2 JIT ratio covers 48 supported rows, not the full 150-row matrix. The license is BSD-3-Clause (pom.xml declares it; GitHub shows NOASSERTION because LICENSE bundles the RE2 and RE2/J notices), and the GPL OpenJDK-derived suite lives in a separate repo. It is a mixed result that only beats the JDK incumbent, which is not on the list.
- **Fields the verifier corrected:** `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/eaftan/safere/blob/main/BENCHMARKS.md>
  - <https://github.com/eaftan/safere>
  - <https://github.com/eaftan/safere/blob/main/LICENSE>
  - <https://github.com/eaftan/safere/blob/main/pom.xml>
  - <https://github.com/eaftan/safere/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/eaftan/safere>
  - <https://github.com/eaftan/safere/blob/main/README.md>
  - <https://github.com/eaftan/safere/blob/main/BENCHMARKS.md>
  - <https://github.com/eaftan/safere/blob/main/pom.xml>
  - <https://github.com/eaftan/safere/blob/main/LICENSE>
  - <https://github.com/eaftan/safere/blob/main/INTENTIONAL_DIVERGENCES.md>
  - <https://github.com/eaftan/safere/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/eaftan/safere`) · [data/wave3/enrich/raw/github_com_eaftan_safere.json](../../../data/wave3/enrich/raw/github_com_eaftan_safere.json) (enrichment confidence 0.7)

</details>
