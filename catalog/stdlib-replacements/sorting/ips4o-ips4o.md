# IPS⁴o (In-place Parallel Super Scalar Samplesort)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-2-Clause` · 🟡 stale

> In-place parallel/sequential comparison sort beating std::sort via cache-efficient block-based samplesort partitioning.

| | |
|---|---|
| **Beats** | std::sort |
| **Claimed result** | Sequential (Table 1 of arXiv 2009.13569, average slowdowns relative to the fastest algorithm per input, averaged over the four machines and inputs of at least 2^18 bytes): I1S4o (sequential IPS4o) vs std::sort, Total: double 1.20 vs 2.47, uint64 1.46 vs 2.95, uint32 1.78 vs 3.93, Pair 1.52 vs 2.45; Uniform: double 1.08 vs 2.43, uint64 1.35 vs 3.02, uint32 1.67 vs 4.02. By Total, I1S4o is about 2.06x (double), 2.02x (uint64), 2.21x (uint32) and 1.61x (Pair) faster than std::sort (derived from page data). Fig. 11 (Uniform uint64) shows std::sort off the plot, above I1S4o, on all four machines. Parallel: the paper reports no parallel speedup against std::sort; its parallel speedups (8.37 on A1x16, 40.92 on A1x64, 20.91 on I4x20, 17.49 on I2x16) are relative to sequential I1S4o. |
| **Workload** | Sorting 2^10 to 2^32 uniformly-distributed 64-bit floating point elements (also Pair/Quartet/100Bytes records and skewed distributions), sequential and multi-core, on four different server machines. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3950X (A1x16); AMD EPYC Rome 7702P (A1x64); 2x Intel Xeon E5-2683 v4 (I2x16); 4x Intel Xeon Gold 6138 (I4x20) |
| **Compiler and flags** | GCC 7.5.0, -march=native -O3 |
| **Adoption** | 135 stars (canonical repo); used as the reference sequential/parallel sorting baseline in numerous follow-up algorithm-engineering papers and benchmark suites (e.g. PPQSort) |
| **Last commit** | 2025-01-15 |
| **Links** | [repository](https://github.com/ips4o/ips4o) · [benchmark](https://arxiv.org/abs/2009.13569) |

## Verdict

On the four-machine benchmark suite (arXiv 2009.13569, GCC 7.5.0, -march=native -O3), sequential IPS4o averaged roughly 2x std::sort's throughput on double/uint64/uint32 keys (Table 1 'Total' slowdown factors 1.20-1.78 for IPS4o vs 2.47-3.93 for std::sort's libstdc++ introsort), and Fig. 11 shows std::sort off-plot and slower than IPS4o on uniform uint64 across all four machines (AMD Ryzen 9 3950X, AMD EPYC Rome 7702P, 2x Xeon E5-2683 v4, 4x Xeon Gold 6138). The paper gives no direct parallel-vs-std::sort figure; its parallel speedups (8.37x-40.92x) are relative to sequential IPS4o, not std::sort.

## Use it when

- Sorting large arrays/vectors of primitives, floats, or small records (Pair/Quartet/100-byte) in-place with no extra buffer
- Multi-core machines where parallel::sort (OpenMP or std::thread + TBB) can use the extra cores for large inputs (roughly n &gt;= 2^18)
- Data with many duplicate keys or skewed distributions, which the branchless classifier handles without the usual pathological slowdown
- Sequential drop-in replacement for std::sort on Linux/macOS with a C++14-capable GCC or Clang toolchain

## Skip it when

- Windows builds -- the README states the code does not currently compile on Windows
- Very small inputs (n &lt;= 2^15), where BlockQuicksort is faster per the record's caveats
- Need a stable sort that preserves the relative order of equal keys -- not documented as stable, and in-place bucket permutation gives no such guarantee
- Can't add TBB and libatomic (or -mcx16 / native 16-byte CAS) to the build -- parallel mode requires them; sequential-only mode is header-only with no dependencies
- Sanitizer-clean concurrency required -- open, unresolved TSan-flagged data race in the parallel presort check (issue #3)

## How it is fast

Superscalar samplesort: recursively partitions the array in-place into many buckets per pass using a branchless decision tree over sampled splitters, then permutes elements block-by-block to stay cache-efficient without extra memory. It special-cases inputs with many equal elements to avoid pathological partitioning, and the parallel version dynamically load-balances buckets across threads.

## Compared with alternatives

Pick IPS4o over BlockQuicksort/quadsort/fluxsort when you need a parallel multi-core sort or must stay robust across many data types and skewed/duplicate-heavy distributions; pick those instead for a header-only, dependency-free sequential drop-in with a simpler build.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | sequential: none. parallel: pthreads/std::thread, TBB, libatomic (or -mcx16 / native 16-byte compare-and-exchange) |
| **Minimum toolchain** | C++14 (CMakeLists sets CMAKE_CXX_STANDARD 14); benchmarked with GCC 7.5.0, -march=native -O3 |
| **Platforms** | Linux/macOS, GCC or Clang, x86-64 (16-byte CAS needed for fastest parallel mode); does not compile on Windows |
| **Thread safety** | not documented beyond parallel::sort owning its own thread pool per call; issue #3 (open) reports a TSan-flagged data race in the parallel presort check (base_case.hpp isSorted, concurrent vector&lt;bool&gt; writes) |
| **Drop-in for the baseline** | partial -- sequential ips4o::sort(begin, end[, comp]) matches std::sort's signature exactly; parallel::sort is a separate call you opt into, not automatic |

## Gotchas

- Parallel mode needs 16-byte atomic compare-and-exchange (-march=native or -mcx16, plus -latomic) or it falls back to lock emulation and loses speed
- CMake's IPS4O_OPTIMIZE_FOR_NATIVE defaults to ON (-march=native), which can produce binaries that crash on other CPUs if redistributed
- Open, unresolved TSan-flagged data race in the parallel presort check (issue #3)
- The ips4o/ips4o repo ships no benchmark code (only src/example.cpp); the paper's numbers come from the separate GPL-3.0 ips4o-benchmark-suite, which is not linked from the README

## Caveats and trade-offs

Numbers come from the peer-reviewed ESA 2017 paper (Section 5, Figures 6-8), which used the older SaschaWitt/ips4o code. The ips4o/ips4o repo contains no benchmark code. A separate ips4o/ips4o-benchmark-suite (GPL-3.0) has a std::sort target but is not linked from the repo README and matches the later 4-machine journal version. ips4o/ips4o is a GitHub fork of the now-deprecated SaschaWitt/ips4o and is the maintained successor. The 1.86x std::sort factor applies at n=2^32; DualPivot beats IS4o on AlmostSorted input by 1.70x, and IS4o is slower than BlockQuicksort for n&lt;=2^15. The parallel advantage shrinks to \~1.41x on the 4-socket Intel4S machine. [retier] Table 1 values are average slowdown factors, not direct timings. std::sort is the sequential GCC introsort, so no parallel-vs-std::sort figure exists in the paper.

Needs C++14; parallel mode requires OpenMP or std::thread plus TBB and 16-byte atomic compare-and-exchange support (or -mcx16/libatomic); does not compile on Windows; least advantage on already-sorted or low-cardinality inputs where n&lt;=2^15.

## Maintenance

Stale (last commit 2025-01-15) but the maintained successor to the deprecated SaschaWitt/ips4o fork; BSD-2-Clause and header-only for sequential use, so it is easy to vendor even without upstream activity.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now A.
- **Tier reason:** Peer-reviewed ESA 2017 paper states GCC 6.2.0, -march=native -O3 and the three machines, and compares against GCC introsort (std-sort). The ips4o/ips4o repo has no benchmark code (only src/example.cpp), and the paper links SaschaWitt/ips4o. The separate ips4o/ips4o-benchmark-suite is not linked from the repo README and targets the later 4-machine version, so tier A is not met.
- **Retiered** B to A: A rests on the later paper arXiv 2009.13569 (Axtmann et al.), which links github.com/ips4o and says it holds the benchmark suite used: ips4o/ips4o-benchmark-suite src/benchmark/benchmark_stdsort.cpp; GCC 7.5.0, -march=native -O3; AMD Ryzen 9 3950X, AMD EPYC Rome 7702P, 2x Xeon E5-2683 v4, 4x Xeon Gold 6138; Fig. 11 shows std::sort off-plot slower than I1S4o. The record's ESA 2017 run (GCC 6.2.0, -march=native -O3) has no public benchmark code (paper links only SaschaWitt/ips4o, library headers), so benchmark_url and claimed_speedup should move to the 2021 paper.
- **Verifier notes:** The record misattributed the 1.86x std::sort factor to Intel4S. The 1.57x figure is IS4o vs BlockQuicksort on AMD1S, not vs std::sort, and the 2.78x is an average, not 'up to'. GitHub reports ips4o/ips4o as fork=true with parent SaschaWitt/ips4o (167 stars, README says it is deprecated in favor of ips4o/ips4o). Metadata checks out otherwise: BSD-2-Clause, 135 stars, last commit 2025-01-15 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `is_fork_of`, `caveats`, `benchmark_url`, `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://drops.dagstuhl.de/opus/volltexte/2017/7854/pdf/LIPIcs-ESA-2017-9.pdf>
  - <https://github.com/ips4o/ips4o>
  - <https://github.com/SaschaWitt/ips4o>
  - <https://github.com/ips4o/ips4o-benchmark-suite>
- **Sources the enricher read:**
  - <https://github.com/ips4o/ips4o>
  - <https://github.com/ips4o/ips4o/blob/HEAD/CMakeLists.txt>
  - <https://github.com/ips4o/ips4o/blob/HEAD/include/ips4o.hpp>
  - <https://github.com/ips4o/ips4o/blob/HEAD/include/ips4o/ips4o.hpp>
  - <https://github.com/ips4o/ips4o/blob/HEAD/src/example.cpp>
  - <https://github.com/ips4o/ips4o/issues>
  - <https://github.com/ips4o/ips4o/issues/3>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ips4o/ips4o`) · [data/wave1/enrich/raw/github_com_ips4o_ips4o.json](../../../data/wave1/enrich/raw/github_com_ips4o_ips4o.json) (enrichment confidence 0.85)

</details>
