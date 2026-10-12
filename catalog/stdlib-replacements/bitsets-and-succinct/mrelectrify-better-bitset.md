# better_bitset

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Bitsets and succinct bit vectors](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🔴 abandoned

> Header-only C++20 bitset adding fast first_one/first_zero bit-scan that std::bitset lacks above 64 bits.

| | |
|---|---|
| **Beats** | std::bitset |
| **Claimed result** | README claims 'improvements averaging 60x' versus the iterative std::bitset approach. benchmark/results.txt: N=8192: 953,294 ns (std::bitset .test(i) loop) vs 18,134 ns (better_bitset) = \~52.6x faster (derived from page data); N=1024: 128,450 vs 1,789 ns = \~71.8x (derived from page data); N=64: 6,349 vs 213 ns = \~29.8x (derived from page data); N=8: 701 vs 218 ns = \~3.2x (derived from page data); but N=4: 250 ns (std::bitset) vs 405 ns (better_bitset), so better_bitset is \~1.6x SLOWER there (derived from page data). The mean of the 13 per-size ratios is \~34x (derived from page data), below the README's 60x. |
| **Workload** | Find index of first set bit ('first_one') across bitsets of size 4-8192 bits, \~5 average one-bits per bitset, 1000 random bitsets per size, measured with Google Benchmark; the std::bitset side is a manual bit-by-bit loop using .test(i), since std::bitset has no built-in bit-scan for sizes above 64. |
| **Metric** | latency |
| **Hardware** | 20 logical CPUs @ \~3609.6 MHz (Google Benchmark auto-detected clock speed and cache sizes only; exact CPU model name not recorded) |
| **Adoption** | 8 stars |
| **Last commit** | 2022-04-08 |
| **Links** | [repository](https://github.com/MrElectrify/better_bitset) · [benchmark](https://github.com/MrElectrify/better_bitset/blob/master/benchmark/results.txt) |

## Verdict

First-party Google Benchmark (compiler/flags unstated) on a 20-logical-core \~3.6GHz host: better_bitset::first_one() beats a naive std::bitset .test(i) bit-by-bit loop from N=8 through N=8192 (e.g. 18,134ns vs 953,294ns at N=8192, \~52.6x; 1,789ns vs 128,450ns at N=1024, \~71.8x), but is \~1.6x slower than std::bitset at N=4 (405ns vs 250ns). The mean of the 13 per-size ratios is \~34x, well below the README's claimed '60x average'.

## Use it when

- Fixed-size bitsets above 64 bits where you need the position of the first set/unset bit (e.g. slot allocation) without hand-writing a scan loop
- Bitsets of 16 bits or fewer, where the smaller backing integer type (uint8_t/uint16_t) saves a few bytes versus std::bitset
- You're willing to vendor a single \~200-line header and require only C++20, with no upstream support expected
- Reference/inspiration for implementing your own countr_zero/countr_one-based bit-scan rather than using the library directly
- N is not tiny: the measured gains hold from N=8 up through N=8192 in the authors' own benchmark

## Skip it when

- You need bitwise operators (&, |, ^, \~) between bitsets — not implemented
- You need std::bitset's assignable reference proxy (bs[i] = true) — operator[] here is const-only
- You need a maintained dependency — inactive since last commit 2022-04-08, 8 stars, two open issues with no response
- You need to ship/vendor code under a known license — no LICENSE file exists and an open issue (#4) asking for one is unanswered
- Your bitsets are consistently very small (N=4) — the authors' own benchmark shows better_bitset \~1.6x slower than std::bitset there

## How it is fast

first_one()/first_zero() call std::countr_zero()/std::countr_one() on each 64-bit (or smaller) storage chunk instead of the .test(i) bit-by-bit loop std::bitset forces on scans above 64 bits. On x86 these compile to a single hardware bit-scan instruction (the BSF/TZCNT family) per chunk, turning an O(N) per-bit test into O(N/64) chunk-level instructions. No SIMD or manual vectorization beyond whatever the compiler emits for those built-ins.

## Compared with alternatives

Pick better_bitset over plf::bitset only if you want a single tiny header with zero build configuration and care solely about first_one/first_zero on fixed-size bitsets above 64 bits; plf::bitset covers more operations (set_range/reset_range, shifts) with gains measured on both GCC and MSVC and is the more complete std::bitset alternative in this catalog. For runtime-sized bitsets use sul::dynamic_bitset or BitLib instead (they target std::vector&lt;bool&gt;), and for sparse/succinct workloads use CRoaring or pasta::bit_vector.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (Google Benchmark is only required to build the optional benchmark target) |
| **Minimum toolchain** | C++20 (cxx_std_20 required; uses std::countr_zero/std::countr_one/std::popcount from &lt;bit&gt; and a requires-clause template constraint) |
| **Platforms** | any (portable C++20 &lt;bit&gt; functions; the only benchmark run was on x86-64, no architecture-specific intrinsics in the header) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — implements test/all/any/none/count/size/set/reset/flip/to_string plus first_one/first_zero, but lacks bitwise operators and std::bitset's reference-proxy type |

## Gotchas

- No LICENSE file in the repo; an open, unanswered GitHub issue (#4, filed 2024-11-03) asks the maintainer to add one — treat the code as look-but-don't-ship
- Open issue #3 (2024-10-01, unaddressed) disputes the correctness of first_one/first_zero for some bit patterns; unresolved since the repo has had no commits since 2022
- Benchmark numbers are self-reported with no stated compiler or optimization flags (the CMakeLists sets neither CMAKE_BUILD_TYPE nor compile options), so real gains under -O2/-O3 may differ
- Only smaller than std::bitset for N&lt;=16; at N=4 in the authors' own benchmark it was slower than std::bitset's naive loop (405ns vs 250ns)

## Caveats and trade-offs

Small, unmaintained repo (last commit 2022, 8 stars). The benchmark is first-party and results.txt records no compiler or optimization flags (the CMakeLists set neither, so the build may not have been optimized), and names the CPU only by core count and clock speed. The std::bitset side is a naive bit-by-bit .test(i) loop written for the benchmark (standard std::bitset has no find-first operation; libstdc++'s non-standard _Find_first() was not used), so the speedup is mostly an algorithmic win over a strawman. better_bitset is slower at N=4. There is no LICENSE file, so the code can be studied but not safely reused.

Not a drop-in replacement: only implements first_zero/first_one plus the common subset (all/any/none/count/size/set/reset/flip/to_string); lacks bitwise operators and the std::bitset reference-proxy type. Also smaller than std::bitset for sizes &lt;=16 bits.

## Maintenance

Abandoned since its last commit on 2022-04-08 (8 stars); no LICENSE file exists and a 2024 issue asking for one is unanswered, so it's readable reference code, not something to vendor as-is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark code (benchmark/benchmark.cpp) and raw output (results.txt) are public, but no compiler, flags or CPU model are stated (the CMakeLists set no build type or optimization flags), so it cannot be A or B. The unstated flags plus a &gt;50x gain would cap it at C anyway.
- **Verifier notes:** The numbers quoted in the record are correct, but it left out the N=4 loss, and the README's '60x average' is not supported by results.txt (mean per-size ratio \~34x, max \~72x). Metadata confirmed: no license, 8 stars, last commit 2022-04-08 (abandoned), not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/MrElectrify/better_bitset>
  - <https://github.com/MrElectrify/better_bitset/blob/master/benchmark/results.txt>
  - <https://github.com/MrElectrify/better_bitset/blob/master/benchmark/benchmark.cpp>
- **Sources the enricher read:**
  - <https://github.com/MrElectrify/better_bitset>
  - <https://github.com/MrElectrify/better_bitset/blob/master/README.md>
  - <https://github.com/MrElectrify/better_bitset/blob/master/include/better_bitset.hpp>
  - <https://github.com/MrElectrify/better_bitset/blob/master/benchmark/benchmark.cpp>
  - <https://github.com/MrElectrify/better_bitset/blob/master/benchmark/results.txt>
  - <https://github.com/MrElectrify/better_bitset/blob/master/benchmark/CMakeLists.txt>
  - <https://github.com/MrElectrify/better_bitset/blob/master/CMakeLists.txt>
  - <https://github.com/MrElectrify/better_bitset/blob/master/vcpkg.json>
  - <https://github.com/MrElectrify/better_bitset/issues/2>
  - <https://github.com/MrElectrify/better_bitset/issues/3>
  - <https://github.com/MrElectrify/better_bitset/issues/4>
  - <https://github.com/MrElectrify/better_bitset/pull/1>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mrelectrify/better_bitset`) · [data/wave1/enrich/raw/github_com_mrelectrify_better_bitset.json](../../../data/wave1/enrich/raw/github_com_mrelectrify_better_bitset.json) (enrichment confidence 0.55)

</details>
