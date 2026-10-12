# Hyperscan

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Regex engines](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> SIMD multi-pattern regex matching library beating PCRE2 6.9-183x on large network-security rulesets.

| | |
|---|---|
| **Beats** | PCRE2 |
| **Claimed result** | Table 5 (seconds, lower=better): Talos ruleset - PCRE 6942, PCRE2 394, RE2-s 1777, Hyperscan-s 173, RE2-m 29, Hyperscan-m 2.15. ET-Open - PCRE 12800, PCRE2 913, RE2-s 4696, Hyperscan-s 516, RE2-m 1116, Hyperscan-m 133. Paper states: 'Hyperscan-s outperforms PCRE, RE2-s, and PCRE2 by 40.1x, 10.3x, and 2.3x' (Talos); 'Hyperscan-m is 13.5x faster than RE2-m while it reveals 183.3x performance improvement over PCRE2' (Talos); 'Hyperscan-s shows 24.8x, 9.1x, and 1.8x speedups over PCRE, RE2-s, and PCRE2' (ET-Open); 'Hyperscan-m outperforms RE2-m and PCRE2 by 8.4x and 6.9x' (ET-Open). Separately, Hyperscan-ported Snort achieves 986 Mbps vs 113 Mbps for stock Snort (8.73x) on the same real traffic. |
| **Workload** | Total wall-clock time to match Snort Talos (1,300 regexes) and Suricata ET-Open (2,800 regexes) rulesets against a 1GB real HTTP traffic trace (818,682 packets), single CPU core, comparing PCRE, PCRE2, RE2, and Hyperscan in single-regex (-s) and multi-regex parallel (-m) modes. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8180 CPU @ 2.50GHz, 48GB memory, single core used for evaluation |
| **Compiler and flags** | GCC 5.4; PCRE v8.41 and PCRE2 v10.32 built with JIT enabled; RE2 v2018-09-01; Hyperscan v5.0. Full optimization flags not stated. |
| **Adoption** | 5.5k stars; used in Snort/Suricata-class DPI, widely deployed in network security products |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/intel/hyperscan) · [benchmark](https://www.usenix.org/system/files/nsdi19-wang-xiang.pdf) |

## Verdict

Measured on a single core of an Intel Xeon Platinum 8180 (GCC 5.4) against PCRE2 v10.32 with JIT enabled: Hyperscan's multi-pattern mode matched the Suricata ET-Open ruleset (2,800 regexes) against a 1GB real HTTP trace in 133s vs PCRE2's 913s (6.9x), and the Snort Talos ruleset (1,300 regexes) in 2.15s vs 394s (183x); single-pattern mode was a more modest 1.8-2.3x over PCRE2 on the same traces.

## Use it when

- Large multi-pattern rulesets (hundreds to tens of thousands of regexes) scanned against the same input stream, e.g. Snort/Suricata-style DPI
- x86-64 or 32-bit x86 targets with at least SSSE3; larger gains with AVX2 present
- Throughput-bound network/security scanning where the multi-mode win (6.9-183x over PCRE2) matters more than compile-step latency
- Streaming matching across TCP-like flows using block or streaming scan modes
- Workloads where a fast approximate prefilter match followed by a slower exact-match confirmation pass is acceptable

## Skip it when

- Single-pattern lookups, where the win over PCRE2 is a modest 1.8-2.3x and API complexity may not be worth it
- Patterns needing backreferences, capturing sub-expressions, atomic/possessive quantifiers, conditional patterns, or arbitrary zero-width assertions -- these are compile errors, not degraded matches
- Non-x86 targets: no upstream ARM/aarch64/PowerPC support (issues #187, #197 open since 2018-19 unresolved); use the community Vectorscan fork instead
- Latency-sensitive single-shot small scans where the separate pattern-database compile step doesn't amortize
- Streaming mode when block mode is possible -- docs note streaming carries extra overhead per record versus block

## How it is fast

Uses hybrid automata (combinations of NFA/DFA representations) plus SIMD-accelerated multi-literal prefilter engines (FDR/Teddy) to scan tens of thousands of patterns in one pass over the input, instead of running each regex independently as PCRE2 does. Minimum requirement is SSSE3; it can additionally use SSE4.2, BMI/BMI2, POPCNT, and AVX2 if present, selected at compile time. Because matching is batched across the whole compiled pattern database, speedups scale with ruleset size: 1.8-2.3x over PCRE2 for single-pattern matching but 6.9-183x for multi-pattern (multi-mode) matching.

## Compared with alternatives

no siblings catalogued yet

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib |
| **Dependencies** | CMake &gt;=2.8.11, Ragel 6.9, Python 2.7, Boost &gt;=1.57 (headers only), OpenSSL (required, used for HMAC-SHA256 database integrity); pcap optional, only for example code |
| **Minimum toolchain** | C99 + C++11; GCC 4.8.1+, Clang 3.4+, Intel C++ Compiler 15+, or MSVC 2017 Build Tools |
| **Platforms** | x86-64 and 32-bit x86 only; minimum SSSE3, optionally uses SSE4.2/BMI/BMI2/AVX2; no official ARM or PowerPC build |
| **Thread safety** | Library calls are re-entrant, but hs_scratch_t is not thread-safe -- one scratch space per thread is required, made cheaply via hs_clone_scratch |
| **Drop-in for the baseline** | partial -- pattern syntax is PCRE-compatible (validated against PCRE 8.41) but the C API is compile-then-scan with callback-based matching against a precompiled database, not PCRE2's single exec call |

## Gotchas

- Backreferences, capturing groups, lookaround/zero-width assertions, atomic and possessive quantifiers, and conditional patterns fail to compile rather than silently degrading
- Prefiltering mode returns a superset of true matches and requires a second exact-match pass with another engine
- OpenSSL is a hard build dependency (used for database integrity hashing), not optional
- No official ARM/aarch64 build; long-open issues (#187, #197) point users to the community Vectorscan fork instead

## Caveats and trade-offs

Benchmark was run and published by the paper's authors, several of whom (Intel, branchfree.org's Geoff Langdale) are Hyperscan's own developers, so despite NSDI peer review it is not fully independent. The real-world HTTP traffic trace ('obtained at a cloud service provider') is not public, so exact reproduction needs a substitute trace; no explicit public artifact/script repo for the Snort/ruleset harness was found, only library versions and hardware/compiler, so tier capped at B rather than A. Some ratios exceed 50x (e.g. 183.3x) but compiler/hardware/library versions are stated and it is not a debug/-O0 build, so the hard-rule auto-cap-to-C does not apply.

x86-specific (SIMD/SSE/AVX) C API; requires precompiled pattern databases (compile step separate from scan); biggest wins are in multi-pattern/large-ruleset DPI workloads (6.9-183x over PCRE2) rather than single-pattern matching (2.3x over PCRE2); streaming mode has extra overhead vs block mode.

## Maintenance

Actively maintained (last commit 2026-09-17) under BSD-3-Clause, used in production DPI stacks like Snort/Suricata; last tagged release is 5.4.2 (2023-04-19), and it is flagged 'copyable' usability in this catalog.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed NSDI'19 paper. Table 5 and its text give exactly the quoted times and speedups vs PCRE2 v10.32 (JIT), on a Xeon Platinum 8180 with GCC 5.4. The harness and traffic trace are not public, and the authors are Hyperscan developers, so B, not A.
- **Verifier notes:** All Table 5 values, the quoted ratios (40.1x/10.3x/2.3x, 13.5x/183.3x, 24.8x/9.1x/1.8x, 8.4x/6.9x) and the Snort figures (113 vs 986 Mbps, 8.73x) are verified verbatim. GitHub reports license NOASSERTION, but COPYING is BSD-3-Clause and LICENSE says BSD with bundled Boost (BSL-1.0) headers, so BSD-3-Clause stands. 5,492 stars, last commit 2026-09-17. Category 'regex-engines' is inconsistent with 'regex' used elsewhere in this batch (not a correctable field).
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/nsdi19-wang-xiang.pdf>
  - <https://github.com/intel/hyperscan>
  - <https://github.com/intel/hyperscan/blob/master/COPYING>
  - <https://github.com/intel/hyperscan/blob/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/intel/hyperscan>
  - <https://github.com/intel/hyperscan/blob/master/README.md>
  - <https://github.com/intel/hyperscan/blob/master/doc/dev-reference/getting_started.rst>
  - <https://github.com/intel/hyperscan/blob/master/doc/dev-reference/runtime.rst>
  - <https://github.com/intel/hyperscan/blob/master/doc/dev-reference/performance.rst>
  - <https://github.com/intel/hyperscan/blob/master/doc/dev-reference/compilation.rst>
  - <https://github.com/intel/hyperscan/blob/master/CMakeLists.txt>
  - <https://github.com/intel/hyperscan/blob/master/CHANGELOG.md>
  - <https://github.com/intel/hyperscan/issues/187>
  - <https://github.com/intel/hyperscan/issues/197>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/intel/hyperscan`) · [data/wave0-seed/enrich/raw/github_com_intel_hyperscan.json](../../../data/wave0-seed/enrich/raw/github_com_intel_hyperscan.json) (enrichment confidence 0.85)

</details>
