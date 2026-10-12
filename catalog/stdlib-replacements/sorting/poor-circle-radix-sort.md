# poor-circle/radix_sort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🔴 abandoned

> Header-only C++20 LSD byte-radix sort for ints/floats/pointers/pairs/structs; drop-in call syntax beats std::sort.

| | |
|---|---|
| **Beats** | std::sort |
| **Claimed result** | README, 1 billion int32: radix_sort 6402ms vs std::sort 91407ms (README says '14.28x faster than std::sort') and vs std::stable_sort 82896ms (\~12.9x). The README sets the parallel figure (radix_sort(par) 2603ms) only against single-threaded std::sort. benchmark/benchmark_output.txt shows std::sort(par) at 12537ms, so parallel against parallel is \~4.8x. The gain is smaller for wider keys. At 1e9 elements single-threaded it is \~5.2x for uint64 (17831ms vs 91867ms) and \~2.9x for pair&lt;uint64,uint64&gt; (33830ms vs 96751ms). In parallel on pair&lt;uint64,uint64&gt;, radix_sort(par) is slightly slower than std::sort(par) (24608ms vs 23532ms). The README headline range is '2.5-14.3x faster than std::sort'. |
| **Workload** | benchmark/benchmark.cpp: 1e6, 1e7, 1e8 and 1e9 uniformly random int, uint64, pair&lt;int,uint32&gt; and pair&lt;uint64,uint64&gt; (first-key) elements, 5 rounds averaged. Covers std::sort, std::stable_sort and radix_sort, both sequential and with std::execution::par. The README headline uses 1e9 int32. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-9900K @ 4.7GHz, DDR4-3000MHz RAM |
| **Compiler and flags** | Microsoft Visual C++ 2022, release mode (per benchmark/benchmark_output.txt); exact compiler flags not stated and no project file in repo |
| **Adoption** | 33 stars |
| **Last commit** | 2022-01-31 |
| **Links** | [repository](https://github.com/poor-circle/radix_sort) · [benchmark](https://github.com/poor-circle/radix_sort#benchmark) |

## Verdict

First-party benchmark (author's benchmark/benchmark.cpp, MSVC 2022 release build, Intel i9-9900K @4.7GHz / DDR4-3000): sequential radix_sort sorted 1e9 int32 elements in 6402ms vs std::sort's 91407ms (\~14.3x) and std::stable_sort's 82896ms (\~12.9x); the margin narrows to \~5.2x on uint64 and \~2.9x on pair&lt;uint64,uint64&gt;, and measured against std::sort(par) instead of sequential std::sort the parallel win is only \~4.8x on int32, with radix_sort(par) slightly slower than std::sort(par) on pair&lt;uint64,uint64&gt; (24608ms vs 23532ms).

## Use it when

- Sorting large (1e6+) arrays of int32/uint32/float/pointer keys, where the key type already has or can get a radix_trait
- Composite keys such as std::pair&lt;K,V&gt; or small structs, where a byte-radix trait can be written for the sort key
- Throughput-bound batch sorting, sequential or with std::execution::par, on x86 with MSVC-class compilers
- Need for stable, comparator-free sorting of fixed-width keys rather than an arbitrary Compare predicate
- Willing to vendor one C++20 header (GPL-3.0 permitting) into the project

## Skip it when

- Need arbitrary/custom comparators (sort by a runtime-selected field or lambda) — radix_sort needs a compile-time radix_trait, not a Compare object
- Wide keys (64-bit ints, pair&lt;uint64,uint64&gt;): sequential speedup drops to \~2.9-5.2x, and radix_sort(par) can be slightly slower than std::sort(par) (measured 24608ms vs 23532ms on 1e9 pair&lt;uint64,uint64&gt;)
- Memory-constrained workloads: needs an O(n) auxiliary buffer the size of the input unless the caller supplies one
- Non-MSVC toolchains: the author only benchmarked MSVC STL on Windows, not libstdc++/libc++
- Projects needing active upstream support: single author, no commits since Jan 2022, one open usage question unanswered

## How it is fast

LSD (least-significant-byte-first) radix sort: one 256-bucket counting-sort pass per byte of the key (histogram, prefix-sum, scatter), so it never does a per-element comparison. The count and scatter loops are manually unrolled 4-wide with Duff's device, and each pass ping-pongs the data between the input and an auxiliary buffer rather than sorting in place. The `std::execution::par` overload shards the range across std::async tasks that count locally, merge per-thread histograms, then scatter concurrently for each byte pass, layering thread parallelism on top of the linear-time algorithm.

## Compared with alternatives

Unlike the comparison-based siblings (BlockQuicksort, IPS4o, LearnedSort, x86-simd-sort) or the stable-sort replacements (fluxsort, quadsort), radix_sort is the only non-comparison LSD byte-radix sort in this set; pick it when the key is an integer, float, pointer, or a pair/struct you can describe with a byte-radix trait and you want the largest win on 32-bit keys, and prefer a comparison-sort sibling for 64-bit/wide keys or arbitrary comparators where radix_sort's edge shrinks or vanishes.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only: &lt;vector&gt;, &lt;array&gt;, &lt;execution&gt;, &lt;future&gt;, &lt;memory&gt;, &lt;cstring&gt;, &lt;limits&gt;) |
| **Minimum toolchain** | C++20 (uses std::unsigned_integral/signed_integral/floating_point concepts and requires-clauses) |
| **Platforms** | any (portable C++20, no SIMD or platform intrinsics); author only benchmarked Windows/MSVC x86-64 |
| **Thread safety** | not documented; the std::execution::par overload spawns its own std::async tasks per byte pass rather than using a caller-supplied thread pool or a standard execution-policy backend |
| **Drop-in for the baseline** | partial — explain: same (first, second[, policy]) call syntax as std::sort, but restricted to types with a radix_trait specialization and adds an extra optional buffer parameter |

## Gotchas

- std::execution::par is accepted only as a dispatch tag; it always drives its own std::async tasks internally rather than routing through a standard execution-policy engine
- demo/demo.cpp's custom-struct example does not compile as written (its radix_trait&lt;mystruct&gt; and my_trait reference undefined p1/p2 identifiers) — follow the README's mystruct pattern instead
- Signed integers and floats flip the sign/exponent bit (XOR 0x80) inside the built-in radix_trait so byte order matches numeric order; a hand-written trait for a new type must replicate this or sort order breaks silently
- Without a caller-supplied buffer, every call allocates a full extra copy of the input (sizeof(value_type) \* n bytes)

## Caveats and trade-offs

Single-author project, unmaintained since Jan 2022. Only MSVC STL was tested (no libstdc++/libc++), and exact MSVC flags are not stated. The README's parallel figure sets parallel radix_sort against sequential std::sort; against std::sort(par) the win is \~4.8x for int32. The speedup falls for 64-bit and pair keys, and parallel radix_sort is slightly slower than std::sort(par) on pair&lt;uint64,uint64&gt;.

LSD radix sort restricted to keys with a defined 'radix trait' (integers, floats, pointers, pairs, user structs via traits) rather than arbitrary-comparator sorting like std::sort; needs an O(n) auxiliary buffer (user-suppliable).

## Maintenance

Abandoned since its last commit on 2022-01-31 (single author, one unanswered open issue); GPL-3.0-licensed and a single header, so still copyable, but expect no fixes or support.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** These are first-party numbers, with no paper or independent suite, so tier B does not apply. The repo has runnable benchmark code (benchmark/benchmark.cpp) that calls std::sort, std::stable_sort and their std::execution::par versions, and benchmark_output.txt gives the hardware (i9-9900K 4.7GHz, DDR4-3000) and compiler ('Microsoft Visual C++ 2022, release mode'). No compiler flags or project file are given, so it cannot be A.
- **Verifier notes:** The headline numbers on the README match exactly. Tier goes from B to C because this is a first-party benchmark with no stated flags. The '\~35.1x parallel' claim was an unfair comparison (parallel vs sequential) and has been corrected with the std::sort(par) data from the repo's benchmark_output.txt. License (GPL-3.0), 33 stars, last commit 2022-01-31 and 'abandoned' status are all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/poor-circle/radix_sort>
  - <https://github.com/poor-circle/radix_sort#benchmark>
  - <https://github.com/poor-circle/radix_sort/blob/master/benchmark/benchmark.cpp>
  - <https://github.com/poor-circle/radix_sort/blob/master/benchmark/benchmark_output.txt>
- **Sources the enricher read:**
  - <https://github.com/poor-circle/radix_sort>
  - <https://github.com/poor-circle/radix_sort/blob/master/README.md>
  - <https://github.com/poor-circle/radix_sort/blob/master/include/radix_sort.hpp>
  - <https://github.com/poor-circle/radix_sort/blob/master/benchmark/benchmark_output.txt>
  - <https://github.com/poor-circle/radix_sort/blob/master/demo/demo.cpp>
  - <https://github.com/poor-circle/radix_sort/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/poor-circle/radix_sort`) · [data/wave1/enrich/raw/github_com_poor_circle_radix_sort.json](../../../data/wave1/enrich/raw/github_com_poor_circle_radix_sort.json) (enrichment confidence 0.6)

</details>
