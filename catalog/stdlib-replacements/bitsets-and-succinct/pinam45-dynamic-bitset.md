# sul::dynamic_bitset

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Bitsets and succinct bit vectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17/20 dynamic bitset beating std::vector&lt;bool&gt; on word-level shift/count operations in third-party benchmarks.

| | |
|---|---|
| **Beats** | std::vector&lt;bool&gt; |
| **Claimed result** | shift_left (small): 13.1 ns vs std 345 ns, \~26x (derived from page data); shift_left (large): 638,896 ns vs std 105,227,752 ns, \~165x (derived from page data); count (small): 6.29 ns vs std 234 ns, \~37x (derived from page data); count (large): 365,279 ns vs std 58,934,071 ns, \~161x (derived from page data); fill (small): 4.79 ns vs std 9.15 ns, \~1.9x (derived from page data); fill (large): 429,375 ns vs std 356,517 ns, dynamic_bitset \~1.2x SLOWER (derived from page data). |
| **Workload** | Same third-party Google Benchmark suite as BitLib (shift_left/right, transform, count, fill) at 'small' (256-bit) and 'large' (16,777,216-bit) sizes, comparing sul::dynamic_bitset against std::vector&lt;bool&gt;. |
| **Metric** | latency |
| **Adoption** | 180 stars |
| **Last commit** | 2026-09-12 |
| **Links** | [repository](https://github.com/pinam45/dynamic_bitset) · [benchmark](https://github.com/bkille/BitLib/blob/master/README.md) |

## Verdict

On BitLib's (bkille/BitLib) third-party Google Benchmark suite — not dynamic_bitset's own repo — sul::dynamic_bitset beat std::vector&lt;bool&gt; by \~26x (small) to \~165x (16,777,216-bit) on shift_left and \~37x to \~161x on count; it was \~1.9x faster than std:: on small fill but \~1.2x slower on large fill (429,375 ns vs 356,517 ns), with large-size set roughly tied (2.37 ns vs 2.39 ns). No compiler, compiler flags, or CPU model are stated on the benchmark page.

## Use it when

- Large bit vectors (roughly 10^5+ bits) doing frequent shift_left/shift_right, count, fill, or transform, where std::vector&lt;bool&gt;'s per-bit loop dominates runtime
- Want boost::dynamic_bitset-like ergonomics (resizable size, bitwise operators, find-next) without taking a Boost dependency
- Bitset size is only known at runtime, ruling out std::bitset&lt;N&gt;
- Want an optional SIMD-accelerated popcount (via libpopcnt) for hot counting loops without writing it yourself
- Want a single header you can vendor into a codebase with no build step

## Skip it when

- Small bitsets (&lt;=256 bits) doing fill/set-style operations: the measured win over std::vector&lt;bool&gt; is marginal (\~1.9x) or a loss (large-size fill is \~1.2x SLOWER, large set is roughly tied)
- Code needs std::bitset's fixed compile-time size, constexpr-friendliness, or std::vector&lt;bool&gt;'s standard iterator/algorithm compatibility
- Code performs bitwise ops (&, |, ^, comparisons) on operands of different sizes expecting boost-style zero-padding: the maintainer explicitly rejected that semantics (see gotchas)
- Need boost::dynamic_bitset's full feature surface (this library states a narrower one)
- Want first-party, reproducible performance numbers before committing: the cited results are from a third-party (BitLib) README, not dynamic_bitset's own benchmark repo, and no compiler, flags, or CPU model are given

## How it is fast

Operations work a whole block (64 bits by default) at a time over an internal std::vector&lt;Block&gt;, instead of the per-bit iteration generic std:: algorithms perform on std::vector&lt;bool&gt;'s bit-reference proxy. Shifts, fills, and transforms move/OR/AND whole words; population count uses compiler builtins or C++20 &lt;bit&gt; intrinsics, and can optionally call kimwalisch/libpopcnt (SIMD popcount) if its header is found at compile time.

## Compared with alternatives

Pick this over BitLib when you want an in-place, resizable container with boost::dynamic_bitset-style ergonomics rather than a span/iterator-based bit-algorithms library (BitLib actually posted faster shift_left/reverse numbers on the same large-size benchmark). Pick over plf::bitset when the size is only known at runtime, not compile-time. CRoaring and pasta::bit_vector target compressed/succinct/rank-select workloads, not general mutable dense bitsets, so they answer a different problem than dynamic_bitset.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none required; optional kimwalisch/libpopcnt (auto-detected via __has_include, used for faster count() if present and not disabled with DYNAMIC_BITSET_NO_LIBPOPCNT) |
| **Minimum toolchain** | C++17 (C++20 optional, enables &lt;bit&gt; intrinsics); CMake 3.10+ only needed if consumed as a CMake subproject |
| **Platforms** | any (CI covers Ubuntu, Windows MSVC, Windows MSYS2, macOS); no SIMD/ISA requirement for the library itself, only for the optional libpopcnt dependency |
| **Thread safety** | not documented; treat as an ordinary unsynchronized container, same as std::vector&lt;bool&gt; |
| **Drop-in for the baseline** | partial — explain: API resembles std::vector&lt;bool&gt;/boost::dynamic_bitset (resize, push_back, operator[], bitwise ops) but it's a different type, has no standard iterators, and comparisons are size-sensitive rather than numeric, so call sites need adaptation, not a type swap |

## Gotchas

- operator&, |, ^, ==, and comparisons all require the caller to manage sizes; the maintainer explicitly rejected boost-style 'pad the shorter operand with zeros' semantics (issue #4) because it breaks algebraic properties like (a^b^b)==a, so mixed-size use needs care
- No standard iterators: bit access uses a reference-proxy object (like std::vector&lt;bool&gt;), so range-for/std::algorithm code expecting real iterators won't compile
- libpopcnt use is silent and header-detected at compile time; vendoring only dynamic_bitset.hpp without libpopcnt.h means count() falls back to builtin popcount, so the cited count() benchmark numbers may not reproduce as-is
- As of the versions discussed in issue #9, there was no documented to_ulong()/to_ullong()-style conversion beyond unsigned long long width without asserts/UB — check the current header if you need numeric conversion

## Caveats and trade-offs

Numbers come from a third party's (bkille/BitLib) README benchmark table, not from dynamic_bitset's own repo. The companion pinam45/dynamic_bitset_benchmarks repo has no published results. BitLib's benchmark code is public (benchmark/), but no compiler, flags or CPU model is stated. Several ratios exceed 50x, so the tier is capped at C. The large-size fill is slower than std::vector&lt;bool&gt; (429,375 vs 356,517 ns), and set (large) is roughly tied (2.37 vs 2.39 ns).

Header-only C++17/20 alternative to boost::dynamic_bitset; dynamic size like std::vector&lt;bool&gt; (not fixed-size like std::bitset); optionally links kimwalisch/libpopcnt for faster counting; narrower feature set than boost::dynamic_bitset.

## Maintenance

Actively maintained (last commit 2026-09-12, MIT license) by a single maintainer who has said free time is limited; being a small header-only file, it's easy to vendor and keep working even if upstream slows further.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** BitLib README's Google Benchmark table has dynamic_bitset:: and std:: (vector&lt;bool&gt;) rows, and every figure in claimed_speedup matches it. The benchmark code is public (bkille/BitLib/benchmark), but no compiler, flags or CPU are stated, and several ratios are above 50x. BitLib (76 stars) is not a well-known independent suite, so C.
- **Verifier notes:** Numbers verified row by row. The wins come mostly from word-level algorithms against bit-by-bit std algorithms on vector&lt;bool&gt;. Metadata checked: MIT, 180 stars, last commit 2026-09-12 (active), not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bkille/BitLib/blob/master/README.md>
  - <https://github.com/bkille/BitLib>
  - <https://github.com/pinam45/dynamic_bitset>
  - <https://github.com/pinam45/dynamic_bitset_benchmarks>
- **Sources the enricher read:**
  - <https://github.com/pinam45/dynamic_bitset>
  - https://github.com/pinam45/dynamic_bitset (README via gh api)
  - <https://github.com/pinam45/dynamic_bitset/blob/master/include/sul/dynamic_bitset.hpp>
  - <https://github.com/pinam45/dynamic_bitset/issues/1>
  - <https://github.com/pinam45/dynamic_bitset/issues/4>
  - https://github.com/pinam45/dynamic_bitset (repo file tree)
  - <https://github.com/bkille/BitLib/blob/master/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/pinam45/dynamic_bitset`) · [data/wave1/enrich/raw/github_com_pinam45_dynamic_bitset.json](../../../data/wave1/enrich/raw/github_com_pinam45_dynamic_bitset.json) (enrichment confidence 0.55)

</details>
