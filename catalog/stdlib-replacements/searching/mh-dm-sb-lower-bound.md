# sb_lower_bound (Fastest Branchless Binary Search)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Searching](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Branchless drop-in-shaped replacement for std::lower_bound that relies on clang emitting cmov instead of a branch.

| | |
|---|---|
| **Beats** | std::lower_bound |
| **Claimed result** | Primitive types, average ns/call: with clang++-10 -mllvm -x86-cmov-converter=false, sb_lower_bound 33.24 vs std::lower_bound 61.30 (\~1.84x, derived from page data), geometric mean 19.81 vs 39.17. Without that flag it is roughly parity: gcc 77.22 vs 80.68, clang 80.06 vs 78.66 (sb slower). 8-byte strings: sb_lower_bound slightly slower in every column (gcc 165.66 vs 160.01, clang 162.68 vs 157.71, clang -cmov 164.71 vs 156.06). The article headline says '2x faster'. A later update reports \~2.3x (std::lower_bound \~161 ns vs the prefetching variant sbpm_lower_bound \~71 ns) on arrays up to \~128M entries. |
| **Workload** | Branchless lower_bound over sorted arrays of primitive integer types and over arrays of 8-byte strings, average ns/call across a benchmark suite |
| **Metric** | latency |
| **Hardware** | Intel i7 Kaby Lake |
| **Compiler and flags** | g++-10 / clang++-10, -std=c++20 -Wall -O2 -march=haswell (some clang runs additionally used -mllvm -x86-cmov-converter=false) |
| **Adoption** | 24 stars |
| **Last commit** | 2023-07-06 |
| **Links** | [repository](https://github.com/mh-dm/sb_lower_bound) · [benchmark](https://mhdm.dev/posts/sb_lower_bound/) |

## Verdict

Author's own benchmark (test.cpp) on one unspecified Intel Kaby Lake i7, g++-10/clang++-10 -std=c++20 -O2 -march=haswell, against libstdc++'s std::lower_bound: with clang and -mllvm -x86-cmov-converter=false, sb_lower_bound averages 33.24 ns/call vs 61.30 ns for std::lower_bound (\~1.84x) on primitive types; without that flag, or under gcc, results are roughly parity, and for 8-byte string keys sb_lower_bound is slightly slower in every measured configuration. A later post on the same site reports the separate prefetching variant sbpm_lower_bound at \~71 ns vs std::lower_bound's \~161 ns (\~2.3x) on arrays up to \~128M entries.

## Use it when

- Sorted arrays of primitive integer/float/pointer keys with a single-instruction comparator
- Hot search loops compiled with clang on x86-64 where you can add -mllvm -x86-cmov-converter=false
- Very large (multi-MB to GB scale) arrays where the prefetching variant (sbpm_lower_bound/sbp_lower_bound) can hide memory latency
- Latency-critical code dominated by branch mispredictions from unpredictable/random query patterns
- Willing to vendor a small header and pin toolchain/flags rather than depend on portable stdlib codegen

## Skip it when

- Comparators over strings or other multi-instruction keys - the author's own numbers show it is slightly slower than std::lower_bound for 8-byte string keys in every tested configuration
- Building with GCC, or clang without the cmov flag - branchless codegen doesn't happen and performance is roughly parity with std::lower_bound
- Anything outside x86-64 - all reported gains are clang+cmov on one Haswell-class -march target; no ARM/other-arch data exists
- Only forward iterators are available - despite the 'ForwardIt' template parameter name, the implementation uses operator[], so it actually requires random-access iterators
- Codebases wanting an actively maintained dependency - last commit July 2023, 24 stars, zero issues or PRs to gauge real-world robustness beyond the author's own benchmark

## How it is fast

Classic binary search on random data mispredicts branches roughly half the time, stalling the pipeline; sb_lower_bound's comparison-and-advance step is written so clang (with -mllvm -x86-cmov-converter=false) lowers it to a cmov, letting the CPU avoid that misprediction penalty at the cost of doing k+1 comparisons per lookup instead of std::lower_bound's average log2(n+1). A separate variant in the same repo, sbpm_lower_bound, adds __builtin_prefetch calls on both candidate cache lines once the range exceeds an L2-sized threshold (256KB), which the author's later post credits for most of the gain on multi-hundred-MB arrays.

## Compared with alternatives

Pick sb_lower_bound over the SIMD/layout-restructuring siblings (FastBinarySearch, Lemire's SIMD Quad search, simdsearch) when you want a minimal single-header, std::lower_bound-signature-compatible branchless search for primitive keys on clang/x86-64 without SIMD intrinsics or a precomputed/cache-friendly array layout; pick scandum/binary_search instead if your actual baseline is C's bsearch() rather than std::lower_bound.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (only &lt;bit&gt;, &lt;functional&gt; from the standard library) |
| **Minimum toolchain** | C++20 (repo's own build commands use -std=c++20; functions are constexpr); benchmarked with g++-10 / clang++-10 |
| **Platforms** | x86-64 only in the evidence given (branchless gains shown solely with clang + -mllvm -x86-cmov-converter=false, -march=haswell); GCC does not produce the branchless path |
| **Thread safety** | not documented (stateless, read-only template function - no reason to expect different behavior from std::lower_bound, but the repo makes no explicit statement) |
| **Drop-in for the baseline** | partial - explain: matching call signature (iterator pair + value [+ comp]) to std::lower_bound, but it needs random-access iterators despite the ForwardIt name, and the speed advantage only materializes under clang with the specific -mllvm flag; under gcc or default clang it's a same-signature but not faster substitute |

## Gotchas

- The 'ForwardIt' template parameter is misleading: the body indexes with first[half], so only random-access iterators actually work
- The headline 2x/1.84x numbers require clang plus -mllvm -x86-cmov-converter=false; without that flag (or under gcc) it's roughly as fast as std::lower_bound
- Makes k+1 comparisons per call (2^k &lt;= n &lt; 2^(k+1)) versus std::lower_bound's average log2(n+1), so it can lose on cheap comparators even when branch prediction isn't the bottleneck
- The prefetching variants (sbp_/sbpm_lower_bound) hardcode an L2-sized 256KB threshold and cache-line constants tuned to the author's own benchmark machine

## Caveats and trade-offs

MIT-licensed via LICENSES/MIT.txt and SPDX headers in every file, but GitHub's API does not detect it. The \~1.8x win needs clang with -mllvm -x86-cmov-converter=false. With gcc or default clang it is about as fast as std::lower_bound, and it is slightly slower for 8-byte string keys. Author's own benchmark on one unspecified Kaby Lake i7. Small project (24 stars), last pushed July 2023.

Branchless codegen depends on cmov being emitted, so results are compiler/flag sensitive; gains shrink or reverse for expensive comparators (e.g. string keys); needs random-access iterators

## Maintenance

Abandoned since its last commit on 2023-07-06 (repo not archived, but no open issues or PRs exist to gauge upkeep); MIT-licensed via LICENSES/MIT.txt and per-file SPDX headers even though GitHub's own license detector reports none, and it's small and header-only enough to vendor as-is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** Benchmark code is public (test.cpp times the real std::lower_bound against sb_lower_bound), and compiler and flags are stated (g++-10/clang++-10 -std=c++20 -O2 -march=haswell). The only hardware given is 'an intel i7 kaby lake', a CPU generation with no model/SKU, so tier A is not met; first-party partial methodology is C.
- **Verifier notes:** The record said no license, but LICENSES/MIT.txt plus SPDX-License-Identifier: MIT headers exist, and the article says 'MIT license'. The record also dropped the clang -cmov-converter=false condition from the 2x headline. libc++ was never actually tested: clang++-10 runs had no -stdlib=libc++ flag, and the article mentions libc++ only as a source reference.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline_stdlib`, `license`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://mhdm.dev/posts/sb_lower_bound/>
  - <https://github.com/mh-dm/sb_lower_bound>
  - <https://github.com/mh-dm/sb_lower_bound/blob/master/README.md>
  - <https://github.com/mh-dm/sb_lower_bound/blob/master/LICENSES/MIT.txt>
  - <https://github.com/mh-dm/sb_lower_bound/blob/master/test.cpp>
  - <https://github.com/mh-dm/sb_lower_bound/blob/master/std_lower_bound.h>
  - <https://github.com/mh-dm/sb_lower_bound/blob/master/sb_lower_bound.h>
- **Sources the enricher read:**
  - <https://mhdm.dev/posts/sb_lower_bound/>
  - <https://github.com/mh-dm/sb_lower_bound>
  - <https://github.com/mh-dm/sb_lower_bound/blob/master/README.md>
  - <https://github.com/mh-dm/sb_lower_bound/blob/master/sb_lower_bound.h>
  - <https://github.com/mh-dm/sb_lower_bound/blob/master/std_lower_bound.h>
  - <https://github.com/mh-dm/sb_lower_bound/blob/master/sbpm_lower_bound.h>
  - <https://github.com/mh-dm/sb_lower_bound/blob/master/test.cpp>
  - <https://github.com/mh-dm/sb_lower_bound/issues>
  - <https://github.com/mh-dm/sb_lower_bound/pulls>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mh-dm/sb_lower_bound`) · [data/wave1/enrich/raw/github_com_mh_dm_sb_lower_bound.json](../../../data/wave1/enrich/raw/github_com_mh_dm_sb_lower_bound.json) (enrichment confidence 0.8)

</details>
