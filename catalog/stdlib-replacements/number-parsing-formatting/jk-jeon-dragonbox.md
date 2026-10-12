# Dragonbox

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception OR BSL-1.0` · 🟡 stale

> Shortest round-trip double/float-to-decimal conversion, faster than std::to_chars.

| | |
|---|---|
| **Beats** | std::to_chars |
| **Claimed result** | 1.77x faster than std::to_chars per double (28.95ns vs 51.35ns; derived from page data); also 25.723x faster than sprintf (744.72ns), directly stated in the same table |
| **Workload** | Converting each of a 1.7M-value pool of random doubles (reduced to 1-17 significant digits) to a shortest round-trip decimal string via jkj::dragonbox::to_chars_n (full cache table) vs. std::to_chars, measured with Google Benchmark; mean time per conversion. |
| **Metric** | latency |
| **Hardware** | MacBook Pro (Apple M1 Pro) |
| **Compiler and flags** | Apple clang version 21.0.0 (clang-2100.0.123.102); CMake default Release build type (CMakeLists.txt sets CMAKE_BUILD_TYPE=Release for optimized code; exact -O flag not printed in the results table itself) |
| **Adoption** | 818 stars; algorithm is used internally by {fmt} and (via fmt) by many downstream projects for double-to-string conversion |
| **Last commit** | 2025-09-12 |
| **Links** | [repository](https://github.com/jk-jeon/dragonbox) · [benchmark](https://github.com/fmtlib/dtoa-benchmark) |

## Verdict

On the independent fmtlib/dtoa-benchmark suite (Apple M1 Pro, Apple clang 21.0.0, Release build via libc++), Dragonbox's to_chars_n with the full cache table converts a double to its shortest round-trip decimal string in a mean 28.95ns vs 51.35ns for libc++'s std::to_chars (1.77x) and 744.72ns for sprintf (25.72x), over a mixed 1.7M-value pool spanning 1-17 significant digits.

## Use it when

- Hot-path double/float-to-string conversion where scientific-notation output is acceptable and every ns matters
- Already depending on {fmt} indirectly and want the same algorithm standalone/header-only without the rest of fmt
- x86-64 target with a C++17-capable toolchain (C++20 unlocks constexpr everywhere)
- Want to tune static-data footprint via the full-vs-compact cache policy
- Need output strictly faster than libc++/libstdc++ std::to_chars on the same double-conversion workload

## Skip it when

- Need std::to_chars-compatible signature/namespace as a true drop-in replacement
- Need %f-style fixed-point output directly — Dragonbox only emits scientific notation (0.1 -&gt; 1E-1); you write the reformatting
- Targeting ARM or other non-x86 architectures — maintainer-acknowledged correctness bugs in intrinsic fallback/detection are open and unresolved (issue #11, filed 2024)
- Require an actual C++11 toolchain — README claims C++11 but the shipped CMakeLists.txt requires cxx_std_17; a C++11 port was requested in 2023 and never delivered (issue #8)
- Low-volume/non-hot-path formatting where the \~22ns/call saved over std::to_chars doesn't justify vendoring three files and a template-heavy API

## How it is fast

Based on Schubfach (a continuous pigeonhole-principle argument), itself inspired by Grisu/Grisu-Exact. It picks the shortest correctly-rounded decimal digits directly from a precomputed power-of-10 cache table plus magic-number/branchless integer arithmetic, avoiding the big-integer or iterative digit-adjustment loops older dtoa algorithms use. A full cache table (9904 bytes for double) trades static data for speed; a compact table (584 bytes) is \~20% slower.

## Compared with alternatives

On the same fmtlib/dtoa-benchmark table, Dragonbox (28.95ns) beats both catalogued siblings Ryu (46.07ns) and {fmt} (36.84ns) and is the only one of the three verified directly against std::to_chars rather than just sprintf; pick it over them when raw to_chars-class conversion speed is the goal and the policy-template API/scientific-notation-only output are acceptable, and pick {fmt} instead when you also want its broader formatting API (fmt already uses Dragonbox internally). fast_float solves the reverse problem (string-to-double parsing), so it's complementary, not a substitute.

## Integration

| | |
|---|---|
| **Form** | header-only (core dragonbox.h); to_chars string-generation layer adds dragonbox_to_chars.h + one .cpp |
| **Dependencies** | none (C++ standard library only; Ryu/Schubfach/Grisu-Exact in the repo are benchmark-only subprojects, not runtime deps) |
| **Minimum toolchain** | CMakeLists.txt requires cxx_std_17 for both targets; README's 'C++11 or higher' claim is not what the build actually enforces (see issue #8). Full constexpr support needs C++20. |
| **Platforms** | x86-64 (benchmarked/used in production via fmt); ARM and other architectures have open, maintainer-acknowledged correctness bugs in intrinsic fallback/detection (issue #11, opened 2024, still open) — not documented as safe there |
| **Thread safety** | not documented explicitly; grep of dragonbox.h found no mutable static or thread_local state, only constexpr statics over immutable cache tables, so the functions are stateless and inherently thread-safe by construction |
| **Drop-in for the baseline** | partial — different namespace/function names than std::to_chars, output is scientific-notation only, and the 5-kind policy-template system changes the call shape further |

## Gotchas

- Output is always scientific notation (e.g. 0.1 -&gt; 1E-1), never %f-style; callers add their own formatting for printf-like output
- README says C++11 but the CMakeLists.txt pins cxx_std_17 for both the dragonbox and dragonbox_to_chars CMake targets
- ARM/non-x86 support has open, maintainer-confirmed correctness bugs in intrinsic fallback detection (issue #11, unresolved since 2024)
- Policy-template API (sign, trailing-zero, decimal-to-binary rounding, binary-to-decimal rounding, cache) can cause binary bloat if many policy combinations get instantiated

## Caveats and trade-offs

Dragonbox's own README benchmarks Grisu-Exact, Ryu and Schubfach, not std::to_chars/printf/strtod directly, so it does not by itself satisfy the WHAT COUNTS rule; this record instead relies on the independent, third-party fmtlib/dtoa-benchmark suite which does include a to_chars column. The to_chars-relative ratio is derived (both numbers are on the page, ratio computed here); single-hardware-sample (Apple M1 Pro); 'Release' build config confirmed via CMakeLists.txt rather than printed alongside the results. Last commit is just over 12 months old, hence 'stale' rather than 'active'.

Always produces the shortest round-trip representation in scientific-notation form (e.g. 0.1 -&gt; 1E-1), not fixed-point %f-style output, so callers need extra formatting logic for printf-like output; the library's policy-based template API can cause binary bloat if many policy combinations are instantiated; header for the core algorithm is separate from the to_chars string-generation layer.

## Maintenance

Stale by commit cadence (last commit 2025-09-12, \~1 year old) but not abandoned — issues still receive maintainer replies through 2026; dual Apache-2.0-with-LLVM-exception/BSL-1.0 licensing and a 3-file footprint for the to_chars path make it easy to vendor despite the slow pace.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** The fmtlib/dtoa-benchmark README table shows dragonbox 28.95 ns, to_chars 51.35 ns and sprintf 744.72 ns (25.723x) on an Apple M1 Pro with Apple clang 21.0.0. The benchmark code is public (src/benchmark.cc, src/dragonbox-test.cc, src/to_chars-test.cc), and CMakeLists.txt pins CMAKE_BUILD_TYPE=Release (CMake's -O3 -DNDEBUG), so the flags come from the committed build config.
- **Verifier notes:** The 1.77x ratio (51.35/28.95) is correctly derived. The license (Apache-2.0 WITH LLVM-exception OR BSL-1.0) matches the README and the LICENSE-Apache2-LLVM and LICENSE-Boost files; the gh spdx value of 'Apache-2.0' is incomplete. The last default-branch commit is 2025-09-12, just over 12 months ago, so 'stale' is correct. The A tier relies on the flags being fixed by the build type in the public CMakeLists.txt, not printed next to the results.
- **Shortcomings recorded by:** Measured through {fmt} 12.2.0's built-in Dragonbox path, not the standalone library: 20k doubles to shortest round-trip decimal at 52.679 ns each vs 288.311 ns for snprintf %.17g (5.47x) and 456.477 ns for std::ostringstream, while emitting fewer characters than %.17g. (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-02-core)
- **Pages the verifier opened:**
  - <https://github.com/fmtlib/dtoa-benchmark>
  - <https://github.com/fmtlib/dtoa-benchmark/blob/main/CMakeLists.txt>
  - <https://github.com/fmtlib/dtoa-benchmark/blob/main/src/dragonbox-test.cc>
  - <https://github.com/fmtlib/dtoa-benchmark/blob/main/src/to_chars-test.cc>
  - <https://github.com/fmtlib/dtoa-benchmark/tree/main/results>
  - <https://github.com/jk-jeon/dragonbox>
- **Sources the enricher read:**
  - <https://github.com/jk-jeon/dragonbox>
  - <https://github.com/jk-jeon/dragonbox/blob/master/README.md>
  - <https://github.com/jk-jeon/dragonbox/blob/master/CMakeLists.txt>
  - <https://github.com/jk-jeon/dragonbox/blob/master/include/dragonbox/dragonbox.h>
  - <https://github.com/jk-jeon/dragonbox/issues/11>
  - <https://github.com/jk-jeon/dragonbox/issues/8>
  - <https://github.com/jk-jeon/dragonbox/issues>
  - <https://github.com/fmtlib/dtoa-benchmark>
  - <https://github.com/fmtlib/dtoa-benchmark/blob/main/README.md>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/jk-jeon/dragonbox`) · [data/wave0-seed/enrich/raw/github_com_jk_jeon_dragonbox.json](../../../data/wave0-seed/enrich/raw/github_com_jk_jeon_dragonbox.json) (enrichment confidence 0.85)

</details>
