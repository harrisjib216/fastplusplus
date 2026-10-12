# Boost.Sort — spreadsort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Hybrid radix/comparison sort in Boost; beats std::sort on large random integers, strings, and objects.

| | |
|---|---|
| **Beats** | std::sort |
| **Claimed result** | spreadsort \~1.94x faster than std::sort on 100M random 64-bit ints (8.2154s vs 4.2248s); the in-repo benchmark_numbers.cpp table on the same page gives 8.21s vs 4.26s (\~1.93x). \~2.57x faster on 10M random strings (6.2442s vs 2.4323s); \~1.62x faster on 100M 8-byte objects with a heavy comparator (8.25s vs 5.10s). spreadsort is slower than std::sort on fully reverse-sorted ints (1.87s vs 1.36s). |
| **Workload** | Sorting 100,000,000 random 64-bit integers, 10,000,000 random strings, and up to 100,000,000 random small objects (8-512 bytes) compared by a heavy or light comparator, single-threaded. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-5820K @ 3.30GHz, 6 cores / 2 threads per core, 15MB cache |
| **Compiler and flags** | GCC 6.3 on Linux; in-repo run scripts (benchmark/single/runGCC_benchmark_\*.sh) compile with g++ -std=c++11 -march=native -w -fno-operator-names -O3 -s |
| **Adoption** | 58 stars on the standalone mirror repo; ships as part of Boost, one of the most widely deployed C++ library collections |
| **Last commit** | 2026-04-11 |
| **Links** | [repository](https://github.com/boostorg/sort) · [benchmark](https://github.com/boostorg/sort/blob/develop/doc/linux_single.qbk) |

## Verdict

In the library's own linux_single.qbk benchmark (GCC 6.3, -std=c++11 -march=native -O3, Intel i7-5820K, libstdc++), spreadsort sorted 100M random 64-bit ints in 4.2248s vs std::sort's 8.2154s (\~1.94x), 10M random strings in 2.4323s vs 6.2442s (\~2.57x), and 100M 8-byte objects with a heavy comparator in 5.10s vs 8.25s (\~1.62x); spreadsort was slower than std::sort on reverse-sorted ints (1.87s vs 1.36s).

## Use it when

- Sorting 100K-100M+ 64-bit integers, floats, or std::strings single-threaded, where the \~2x win on random data matters.
- Large or expensive-to-compare elements (long keys, heavy comparators, key+payload records) — the object benchmark shows bigger wins as element size grows.
- Data that is already sorted or nearly sorted forward — spreadsort has an early-exit fast path competitive with pdqsort.
- Custom numeric-like keys where you can write a correct right-shift functor (fixed-point types, custom integer wrappers).
- You are fine with an unstable sort, same as std::sort.

## Skip it when

- Reverse-sorted or adversarial input — the repo's own benchmark shows spreadsort slower than std::sort here (1.87s vs 1.36s on 100M ints).
- Inputs under \~1000 elements — falls back to pdqsort internally, so there is no spreadsort-specific benefit.
- Need a stable sort — use Boost's spinsort/flat_stable_sort instead, though neither beat std::stable_sort on random data in this same benchmark, only on near-sorted input.
- Indirect/argsort-style sorting through an index lookup — GitHub issue #85 shows overriding only the right-shift functor without also overriding the comparator silently falls back to plain (wrong-looking) comparison behavior for small inputs.
- Need the benchmarked \~2x margins reproduced on current hardware/toolchains — the doc's numbers are from GCC 6.3 on a 2017-era CPU and have not been re-run since.

## How it is fast

It is a hybrid radix/comparison sort: it recursively buckets elements by their most-significant bits (read via a right-shift functor) and dynamically chooses radix or comparison-based sorting per bucket, whichever has better worst-case cost. Worst case is the lesser of O(N log N) comparisons and O(N log(K/S + S)) operations, where K is key bit-width and S (max_splits, default 11) is a tunable constant. This gives near-linear behavior on wide or clustered integer/float/string keys where std::sort spends more time on comparisons.

## Compared with alternatives

Pick spreadsort over comparison-based siblings (BlockQuicksort, pdqsort-class sorts) when data is plain integers/floats/strings with wide or clustered key bits and you don't need stability or multithreading; pick IPS4o or x86-simd-sort instead when you can parallelize or vectorize, and pick fluxsort/quadsort instead when stability matters more than raw unstable-sort throughput.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Boost.Range, Boost.TypeTraits, Boost.Core (static_assert) — ships as part of Boost, not a standalone zero-dependency library |
| **Minimum toolchain** | C++11 (README states a C++11 compiler is required; parallel algorithms in the same repo also need C++11) |
| **Platforms** | any — portable C++ template code, no SIMD/intrinsics or arch-specific code observed in the spreadsort headers |
| **Thread safety** | not documented — each call sorts one range with no shared/global state visible in the headers; safe to run independent calls on separate data from separate threads, but this is inferred, not stated |
| **Drop-in for the baseline** | partial — explain: the two-iterator spreadsort(first,last)/integer_sort(first,last) overload matches std::sort's call signature for random-access iterators and is unstable like std::sort, but only accepts types with the right type_traits (integer/IEC-559 float/std::string); other key types need integer_sort/float_sort/string_sort called directly with a right-shift functor |

## Gotchas

- Right-shift functor must fully discriminate between elements consistent with operator&lt; (documented requirement, GitHub issue #7).
- Overriding the right-shift functor alone for indirect/argsort use (sorting indices via a lambda into another array) without also overriding the comparator can give surprising results on small inputs that fall back to default comparison (issue #85).
- Doc header warns exceptions during comparisons, swaps/moves, the right shift, or iterator operations propagate and 'may cause data loss'; only the internal small-vector-resize-throw path is documented as data-loss-free.
- Needs O(key_length) extra memory for radix buckets, so memory scales with key bit-width as well as N — not a fixed small overhead like introsort's O(log N).

## Caveats and trade-offs

Benchmark authored by the library's own maintainers, not an independent third party. The 4-decimal integer, string and object figures come from 'complex' benchmarks that the doc says are not included in the library (non-free software); the reproducible in-repo benchmark_numbers.cpp gives near-identical integer results. Flags come from the in-repo run scripts, not the doc text. Hardware (i7-5820K) and GCC 6.3 date to \~2017 and have not been re-run on recent toolchains. spreadsort is slower than std::sort on reverse-sorted input, and pdqsort (also in Boost.Sort) is about as fast as spreadsort on random ints.

spreadsort is unstable and needs O(key_length) extra memory; it is a hybrid radix/comparison sort so wins depend on key bit-width/distribution; the library's other stable algorithms (spinsort, flat_stable_sort) were NOT faster than std::stable_sort on uniformly random data in this same benchmark, only on near-sorted inputs.

## Maintenance

Actively maintained as part of Boost (last commit 2026-04-11 on develop); BSL-1.0 licensed, header-only, and small enough to vendor without a build step.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** linux_single.qbk compares spreadsort vs std::sort, gives GCC 6.3 and the i7-5820K hardware, and ties the integer table to in-repo benchmark/single/benchmark_numbers.cpp. The run script benchmark/single/runGCC_benchmark_numbers.sh builds it with g++ -std=c++11 -march=native -O3; benchmark_strings.cpp and benchmark_objects.cpp are also in the repo.
- **Verifier notes:** Numbers verified exactly in doc/linux_single.qbk. Default branch (develop) last commit is 2026-04-11; the record's 2026-08-12 matches repo pushed_at, not a commit on the default branch. License API field is null, but README and file headers state Boost Software License 1.0 (BSL-1.0), so the license is correct.
- **Fields the verifier corrected:** `last_commit`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/boostorg/sort>
  - <https://github.com/boostorg/sort/blob/develop/doc/linux_single.qbk>
  - <https://github.com/boostorg/sort/tree/develop/benchmark/single>
  - <https://github.com/boostorg/sort/blob/develop/benchmark/single/runGCC_benchmark_numbers.sh>
  - <https://github.com/boostorg/sort/blob/develop/benchmark/single/benchmark_numbers.cpp>
  - <https://github.com/boostorg/sort/blob/develop/README.md>
- **Sources the enricher read:**
  - <https://github.com/boostorg/sort>
  - <https://github.com/boostorg/sort/blob/develop/README.md>
  - <https://github.com/boostorg/sort/blob/develop/doc/linux_single.qbk>
  - <https://github.com/boostorg/sort/blob/develop/doc/spreadsort.qbk>
  - <https://github.com/boostorg/sort/tree/develop/include/boost/sort>
  - <https://github.com/boostorg/sort/blob/develop/include/boost/sort/spreadsort/spreadsort.hpp>
  - <https://github.com/boostorg/sort/blob/develop/include/boost/sort/spreadsort/integer_sort.hpp>
  - <https://github.com/boostorg/sort/issues/7>
  - <https://github.com/boostorg/sort/issues/45>
  - <https://github.com/boostorg/sort/issues/60>
  - <https://github.com/boostorg/sort/issues/85>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/boostorg/sort`) · [data/wave1/enrich/raw/github_com_boostorg_sort.json](../../../data/wave1/enrich/raw/github_com_boostorg_sort.json) (enrichment confidence 0.85)

</details>
