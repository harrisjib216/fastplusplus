# BitLib

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Bitsets and succinct bit vectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> Header-only bit_vector and STL-style bit algorithms that beat std::vector&lt;bool&gt; by operating word-at-a-time instead of bit-at-a-time.

| | |
|---|---|
| **Beats** | std::vector&lt;bool&gt; |
| **Claimed result** | bit::shift_left \~283x faster than std::shift_left at large size (371,224 ns vs 105,227,752 ns, derived from page data); bit::reverse \~236x faster at large size (1,245,260 ns vs 293,563,397 ns, derived); bit::count \~161x faster at large size (365,194 ns vs 58,934,071 ns, derived); bit::rotate \~70x faster at large size (7,333,284 ns vs 514,697,313 ns, derived); bit::set \~1.26x faster at large size (1.90 ns vs 2.39 ns, derived) |
| **Workload** | Google Benchmark micro-benchmarks of STL-style algorithms (set, shift_left/right, reverse, transform (unary/binary), rotate, count, swap_ranges, copy, equal, move, copy_backward, fill, find) over bit containers of size 2^8 (small) through 2^31 (huge) bits, run against bit::bit_vector, pinam45/dynamic_bitset, noporpoise/BitArray, and std::vector&lt;bool&gt;. |
| **Metric** | latency |
| **Adoption** | 76 stars |
| **Last commit** | 2024-06-06 |
| **Links** | [repository](https://github.com/bkille/BitLib) · [benchmark](https://github.com/bkille/BitLib/blob/master/README.md) |

## Verdict

First-party Google Benchmark results in BitLib's README, run on undocumented hardware/compiler/stdlib, show bit:: algorithms beating std:: on std::vector&lt;bool&gt; at 'large' size (2^24 bits): shift_left 371,224ns vs 105,227,752ns (\~283x), reverse 1,245,260ns vs 293,563,397ns (\~236x), count 365,194ns vs 58,934,071ns (\~161x), rotate 7,333,284ns vs 514,697,313ns (\~70x), and set 1.90ns vs 2.39ns (\~1.26x); the same table also benchmarks against pinam45/dynamic_bitset and noporpoise/BitArray.

## Use it when

- Bulk bitset operations (shift, rotate, reverse, transform, count) over large bit ranges (tens of thousands of bits and up) where std::vector&lt;bool&gt;'s bit-by-bit iteration is the bottleneck
- Code already calling &lt;algorithm&gt; functions on std::vector&lt;bool&gt; that can be swapped to bit:: equivalents with matching signatures
- Word-aligned or mostly-aligned access patterns (aligned ranges are 1.5-5x faster than unaligned in BitLib's own numbers)
- Projects that can pin to a single header-only vendored dependency and C++17 or newer
- Prototyping/research code where a stale-but-working header is acceptable and the library can be forked/patched in place

## Skip it when

- You need the exact std::vector&lt;bool&gt; ABI/type (e.g. interop with code expecting std::vector&lt;bool&gt; by value) rather than a similarly-shaped but distinct bit_vector type
- Small containers (small = 256 bits): several bit:: operations are still faster than std but by single-digit-ns margins, not worth a new dependency for
- You need algorithms not yet implemented (sort, stable_sort, inner_product, shuffle, sample, mismatch, search, search_n, move_backward are all open feature requests, not present)
- You need active upstream support: last commit 2024-06-06, no releases/tags visible, solo maintainer
- You need SIMD acceleration out of the box: Highway support exists but is opt-in and unbenchmarked in the published table

## How it is fast

The library is built on 'bit iterators' (from Vincent Reverdy's bit/bit-algorithms projects) that track a word pointer plus a sub-word bit position, letting algorithms process a full WordType (typically uint64_t) per step instead of std::vector&lt;bool&gt;::iterator's implicit bit-by-bit proxy-reference access. Word-aligned ranges get bulk word operations (memmove-style shifts, popcount via libpopcnt for count, word-wise bitwise ops for transform), with a separate slower path for unaligned (U) boundaries. An optional SIMD path via Google Highway (BITLIB_HWY) is available but not on by default.

## Compared with alternatives

Pick BitLib over sul::dynamic_bitset when you need the fuller STL-algorithm surface (rotate, transform, swap_ranges, copy_backward) rather than just a bitset type, and over plf::bitset/better_bitset (which target std::bitset, a fixed-size type) when your container size is runtime-determined like std::vector&lt;bool&gt;. sul::dynamic_bitset showed a larger small-size shift_left win in BitLib's own table (13.1ns vs BitLib's 26.8ns), so for small, shift-heavy workloads it may edge out BitLib.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for core library; Google Highway only if BITLIB_HWY SIMD path is enabled; GoogleTest/Google Benchmark only for building tests/benchmarks |
| **Minimum toolchain** | C++17 (CMakeLists defaults to C++17, notes C++20 is faster and adds std::shift_\* interop); CI tests GCC 11 on Ubuntu 20.04/22.04 with -std=17 and -std=20 only |
| **Platforms** | not documented beyond CI: only Linux+GCC 11 is exercised in CI (.github/workflows/cmake.yml); no macOS/Windows/clang CI coverage, no ISA requirement for the core path (SIMD path via Highway is optional) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — explain: bit_vector's constructors/iterators/most member functions mirror std::vector&lt;bool&gt;, and unsupported std:: algorithms still compile against it, but it is a distinct class template (not std::vector&lt;bool&gt; itself) and the measured speedups only apply when call sites are switched from std:: to bit:: algorithm names |

## Gotchas

- Bit position within a word increases LSB to MSB, which is the opposite of how people usually read a printed bit string; the README calls this out as a common source of bugs when writing custom algorithms against bit_iterator directly
- Aligned (A) vs unaligned (U) vs random (R) iterator boundaries materially change performance (e.g. bit::reverse (large) 1.25ms aligned vs 1.80ms unaligned) — the win over std:: shrinks (but does not disappear) on misaligned ranges
- SIMD path requires manually defining BITLIB_HWY and adding Google Highway as a dependency; it is not covered by the published benchmark table
- Only 10 of the library's own open issues are unimplemented std::algorithm equivalents (sort, mismatch, search, search_n, shuffle, sample, inner_product, move_backward) — check the list before assuming full &lt;algorithm&gt; parity

## Caveats and trade-offs

This is the assignment's known lead. The README's benchmark table has no stated compiler flags or CPU model, so tier is capped at C even though the benchmark code (Google Benchmark, BITLIB_BENCHMARK CMake option) is public. Several ratios exceed 50x (shift_left, reverse, transform at 'large' sizes), which is plausible given std::vector&lt;bool&gt;'s well-documented bit-by-bit iteration cost in libstdc++/libc++, but cannot be independently verified without stated methodology. 11 open issues; last commit 2024-06-06 (stale).

Header-only, C++17+; bit_vector wraps std::vector&lt;WordType&gt; and mirrors std::vector&lt;bool&gt;'s interface, but the speedups only apply when using BitLib's own bit::-namespaced algorithms (bit::rotate, bit::transform, etc.) instead of &lt;algorithm&gt;; optional SIMD path requires opting into Google Highway (BITLIB_HWY).

## Maintenance

Stale: last commit 2024-06-06, 11 open issues (all feature requests, no known correctness bugs found), 76 stars, single maintainer; BSD-3-Clause and header-only, so it is cheap to vendor and patch even without upstream activity.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README shows first-party Google Benchmark results for bit:: algorithms vs std:: on std::vector&lt;bool&gt;, with code in benchmark/. It states no compiler, flags, CPU model, or stdlib, and several ratios exceed 50x, so the tier is capped at C.
- **Verifier notes:** All five cited rows match the README (large = 1&lt;&lt;24 bits), and the derived ratios (283x, 236x, 161x, 70x, 1.26x) are correct. BSD-3-Clause, 76 stars, 11 open issues, and last commit 2024-06-06 (stale) were checked and are correct.
- **Pages the verifier opened:**
  - <https://github.com/bkille/BitLib>
  - <https://github.com/bkille/BitLib/blob/master/README.md>
  - <https://github.com/bkille/BitLib/tree/master/benchmark>
- **Sources the enricher read:**
  - <https://github.com/bkille/BitLib>
  - <https://github.com/bkille/BitLib/blob/master/README.md>
  - <https://github.com/bkille/BitLib/tree/master/benchmark>
  - repos/bkille/BitLib/contents/CMakeLists.txt
  - repos/bkille/BitLib/contents/.github/workflows/cmake.yml
  - repos/bkille/BitLib/contents/include/bitlib/bit-containers/bit_vector.hpp
  - repos/bkille/BitLib/issues (list + #35)
  - repos/bkille/BitLib (repo metadata)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/bkille/bitlib`) · [data/wave1/enrich/raw/github_com_bkille_bitlib.json](../../../data/wave1/enrich/raw/github_com_bkille_bitlib.json) (enrichment confidence 0.6)

</details>
