# Timsort (gfx::timsort, cpp-TimSort)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++20 TimSort and TimSort-merge; beats std::sort/std::stable_sort only on presorted, reversed or run-structured input.

| | |
|---|---|
| **Beats** | std::sort and std::stable_sort (also std::inplace_merge for gfx::timmerge) |
| **Claimed result** | README bench_sort output (seconds for 100 sorts of 100000 elements): reversed int std::sort 0.045461 vs timsort 0.019139 (about 2.4x, derived from page data); sorted int 0.021876 vs 0.008042 (about 2.7x, derived from page data); reversed std::string 0.586707 vs 0.345099 (about 1.7x, derived from page data); sorted std::string 0.402458 vs 0.298639 (about 1.35x, derived from page data); against std::stable_sort, reversed int 0.575431 vs 0.019139 (about 30x, derived from page data) and reversed std::string 2.715778 vs 0.345099 (about 7.9x, derived from page data). On randomized data timsort is SLOWER: int std::sort 0.695253 vs timsort 1.255825, std::string 3.438217 vs 5.791845 (also slower than std::stable_sort 0.868916 and 4.122629). README and wiki bench_merge output (ms for 100 merges, averaged over middle positions): sorted std::string std::inplace_merge 158.238114 vs timmerge 0.273858 (about 578x, derived from page data; the subranges are already in order, so timmerge's galloping does almost no work), sorted int 4.291098 vs 0.105571, reversed int 11.441404 vs 4.017482 (about 2.8x), reversed std::string 305.649503 vs 114.773898 (about 2.7x), randomized std::string 324.964249 vs 210.297207 (about 1.5x); randomized int 33.404430 vs 37.047990 (timmerge slower). |
| **Workload** | bench_sort: 100000-element int vectors (values (i+1)\*10) and std::string vectors (their decimal strings), randomized (fixed-seed mt19937 shuffle), reversed or already sorted; each figure is the std::clock CPU time of 100 iterations of copy-then-sort. bench_merge: a 100000-element sequence whose two subranges, split at 19 middle positions, are each sorted before merging; each cell is total milliseconds (steady_clock) for 100 merges, and the reported figure is a trapezoidal average over middle positions. In the merge 'sorted' case the two subranges are already in final order (no overlap), in the 'reversed' case they are non-overlapping but swapped, and in the 'randomized' case they overlap heavily. |
| **Metric** | throughput |
| **Hardware** | CPU model not stated (target x86_64-apple-darwin14.5.0 for the sort run, x86_64-pc-linux-gnu for the merge run) |
| **Compiler and flags** | Sort run: Apple LLVM 7.0.0 (clang-700.0.72), c++ -Wall -Wextra -g -DNDEBUG -O2 -std=c++11 example/bench.cpp. Merge run: GCC 10.2.0 on Linux (Manjaro per the wiki page), c++ -Wall -Wextra -g -DNDEBUG -O2 -std=c++11 bench_merge.cpp. Standard libraries inferred from the toolchains (Apple clang on darwin uses libc++, GCC on Linux uses libstdc++), not stated. |
| **Adoption** | 319 stars; on Conan Center as timsort |
| **Last commit** | 2024-12-03 |
| **Links** | [repository](https://github.com/gfx/cpp-TimSort) · [benchmark](https://github.com/timsort/cpp-TimSort) |

## Verdict

The project's own README runs, no CPU model: with Apple LLVM 7.0.0 (libc++ inferred), -O2, 100 copy-then-sort passes over 100000 elements, timsort beat std::sort 2.4x on reversed ints and 2.7x on sorted ints (1.35-1.7x on std::string) and std::stable_sort up to 30x on reversed ints, but lost 1.8x to std::sort and 1.45x to std::stable_sort on random ints. With GCC 10.2.0 on Manjaro x86_64 (libstdc++ inferred), timmerge beat std::inplace_merge on all std::string cases (1.5x random overlap, 2.7x swapped halves, 578x when the halves are already in order, a degenerate case) and lost slightly on randomly overlapping int halves.

## Use it when

- Stable sorting of data that is already mostly ordered: re-sorting a vector after appending a few elements, nearly sorted timestamps or log records, inputs made of a few long ascending or descending runs.
- Merging two sorted halves with little overlap, such as appending a sorted batch to a sorted vector: timmerge gallops past the in-place parts (README GCC 10.2 run: 0.11 ms vs 4.29 ms per 100 int merges when the halves are already in order).
- Elements with expensive comparisons or moves, such as std::string or composite keys, where galloping saves comparisons: the README merge run shows timmerge 1.5x faster than std::inplace_merge on randomly overlapping std::string halves and 2.7x on swapped halves.
- C++20 code that wants a stable sort with projections and sentinel or proxy-iterator support (std::views::zip works from v3.0.1).
- Porting Python or Java code whose performance assumptions rely on TimSort's run adaptivity.

## Skip it when

- Random or uniformly distributed keys: the README run has timsort 1.8x slower than std::sort on 100000 random ints (1.256 s vs 0.695 s for 100 sorts) and 1.45x slower than std::stable_sort (0.869 s); the same holds for std::string.
- Memory-constrained code: merges allocate a temporary buffer of up to half the range, and an allocation failure throws std::bad_alloc instead of falling back to an in-place O(n log^2 n) merge as std::stable_sort and std::inplace_merge can.
- Merging heavily overlapping halves of cheap types: timmerge was slower than std::inplace_merge on randomly overlapping int halves (37.0 ms vs 33.4 ms average per 100 merges).
- Pre-C++20 toolchains: 3.x needs C++20 concepts and ranges, and the C++11 (2.x.y) and C++03 (1.x.y) branches are no longer actively maintained.
- Non-random-access containers (std::list, forward ranges) or parallel sorting: it requires random-access iterators and runs single-threaded with no execution-policy overloads.

## How it is fast

TimSort scans the input for natural runs (non-decreasing, or strictly decreasing runs reversed in place), extends short runs to a minimum run length (32-64 since v2.0.1) with binary insertion sort, and merges runs on a stack under the length invariants. Merges first gallop (exponential plus binary search) to skip the prefix and suffix that are already in place, then switch between one-at-a-time merging and galloping mode when one side keeps winning. An already sorted or strictly reversed input is a single run, so it costs n-1 comparisons (plus one reverse), which is where all the claimed wins come from.

## Compared with alternatives

Pick it over pdqsort or vergesort when you need a stable result with C++20 projections and the data is presorted or run-structured; both are unstable sorts whose catalogued wins are on random-data distributions where gfx::timsort loses to std::sort. For stable sorting of primitive keys on random or mixed data pick fluxsort, quadsort or blitsort, which beat std::stable_sort there while gfx::timsort is 1.45x slower than it; among these siblings only gfx::timmerge replaces std::inplace_merge.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only); the tests use Catch2, fetched by CMake |
| **Minimum toolchain** | C++20 for 3.x (CI: GCC 10, Clang 11 on Ubuntu; MSVC 19.37; MinGW-w64 GCC 12; GCC 10 and Clang 17 on macOS); CMake 3.14+ for the install target; branch 2.x.y needs C++11, 1.x.y C++03 |
| **Platforms** | any (portable scalar C++, no intrinsics); CI on Linux, Windows (MSVC, MinGW) and macOS |
| **Thread safety** | not documented; each call builds its own local TimSort object and keeps no global state, so concurrent calls on disjoint ranges are independent (read from the source) |
| **Drop-in for the baseline** | partial: same call shape as std::ranges::stable_sort / std::stable_sort and std::ranges::inplace_merge (namespace gfx), but random-access only, no allocation-failure fallback, no execution policies, and it is a replacement for std::sort only when a stable result is wanted and the input is presorted |

## Gotchas

- Every branch (1.x.y, 2.x.y, 3.0.1) writes the adaptive gallop threshold back as minGallop_ = (std::min)(minGallop, 1), where OpenJDK's TimSort.java writes back max(minGallop, 1) ('minGallop &lt; 1 ? 1 : minGallop') and CPython stores the adapted value. After the first merge of a timsort call, every later merge therefore starts in galloping mode almost at once. Results stay correct and stable; it may cost extra comparisons on random input (not measured here) and does not inflate any claimed win, since sorted and reversed inputs are single runs with no merges and each timmerge call starts fresh at MIN_GALLOP 7.
- v3.0.0 returned wrong results on proxy iterators such as std::views::zip (issue #40, fixed in v3.0.1 on 2024-12-03); use 3.0.1. The 3.0.1 header still defines GFX_TIMSORT_VERSION_PATCH 0 (the macros say 3.0.0 while CMake says 3.0.1), so do not gate code on the version macros.
- A comparator that is not a strict weak ordering is only caught by an assertion when GFX_TIMSORT_ENABLE_ASSERT is defined (Java's TimSort throws instead). If a comparator throws mid-merge, the elements already moved into the internal buffer are destroyed during unwinding and the range keeps moved-from values in their place; exception guarantees are not documented.
- No published number reflects the current 3.x code: the README sort output is from the 2015 example/bench.cpp built with Apple LLVM 7.0.0 at -O2 (before the v2.0.1 minRunLength fix, issue #33), the merge output was built with -std=c++11 from 2.x-era code, and no CPU model is given. bench_sort has no sortedness check (bench_merge checks is_sorted) and each timing includes a std::copy of the 100000-element input, which narrows the ratios rather than inflating them.

## Known shortcomings

- Faster only on sorted or reversed input and slower than std::sort and std::stable_sort on random data in its own example/bench.cpp (Apple LLVM 7.0.0, 2015, no CPU model; timings are totals of 100 iterations); the 578x merge row is runs already in order with no overlap. Last commit 2024-12-03; gfx URL redirects to timsort/cpp-TimSort.
- Enricher: no published number comes from 3.x code (the sort run is 2015 Apple LLVM 7.0.0, before the v2.0.1 minRunLength fix #33); random ints are 1.8x slower than std::sort and 1.45x slower than std::stable_sort; every branch writes back minGallop_ = min(minGallop, 1) where OpenJDK writes max(minGallop, 1), so later merges start in galloping mode (results correct, extra comparisons on random input, unmeasured); bench_sort has no sortedness check; v3.0.0 gave wrong results with std::views::zip (#40, fixed 3.0.1).

## Caveats and trade-offs

Tier C: the project's own benchmark code with compiler and flags but no CPU model and no standard-library statement. The README sort output was produced with Apple LLVM 7.0.0 (2015 toolchain, libc++ of that era) at -O2 from the old C++11 example/bench.cpp, not from a run of the current benchmarks directory built with -DBUILD_BENCHMARKS=ON; std::sort implementations have changed since, so current ratios may differ. The README states plainly that timsort is slower than std::ranges::sort on randomized sequences and faster only on partially-sorted ones, so the win is limited to presorted, reversed or nearly sorted inputs. Baseline for the 'faster' rows is std::sort, which is not stable; the fair stable baseline is std::stable_sort (also beaten on reversed and sorted input, also slower on random input). Sort timings are CPU-clock totals for 100 iterations that each include a std::copy of the input, timed on all three algorithms alike. The headline 578x merge figure is the degenerate case where the two runs are already in final order (timmerge gallops past them while std::inplace_merge still does linear work); on heavily overlapping int runs timmerge is slower. The merge run used GCC 10.2.0 on Manjaro x86_64 (wiki https://github.com/timsort/cpp-TimSort/wiki/Benchmark-results lists all middle positions) with no CPU model. The repo moved from gfx/cpp-TimSort to timsort/cpp-TimSort; the old URL redirects. The current 3.x.y branch requires C++20; the 2.x.y (C++11) and 1.x.y (C++03) branches are no longer actively maintained.

Stable O(n log n) sort that needs extra heap memory and cannot fall back to an O(n log^2 n) in-place algorithm when allocation is short. Slower than std::sort on random data. Version 3.x requires C++20 (ranges, projections); branches 2.x.y (C++11) and 1.x.y (C++03) are no longer actively maintained.

## Maintenance

Low activity (last commit and release v3.0.1 on 2024-12-03, one open enhancement issue, 319 stars, on Conan Center as timsort/3.0.1), MIT-licensed single header that is easy to vendor; the older C++11 and C++03 branches are unmaintained, and the code clamps its gallop threshold with std::min where OpenJDK uses max (a performance deviation that leaves results correct and does not touch the benchmarked wins).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README prints the project's own benchmark output (sort run from the old example/bench.cpp, now benchmarks/bench_sort.cpp; merge run from benchmarks/bench_merge.cpp) against std::sort, std::stable_sort and std::inplace_merge, with compiler and -O2 flags stated but no CPU model, so it falls short of A; first-party only, so C.
- **Verifier notes:** All README numbers match the record; bench_sort.cpp and bench_merge.cpp (100 iterations each, merge output checked with is_sorted) look sound, with no correctness or no-op problem found. Shortcomings for the orchestrator: faster only on presorted or reversed input (slower than std::sort and std::stable_sort on random data), no CPU model, sort numbers from a 2015 Apple clang toolchain, and the 578x merge row is a no-overlap degenerate case. Metadata checked: MIT, 319 stars, 49 forks, not archived, not a fork, last commit 2024-12-03 (Release v3.0.1), stale.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party README (verifier, not faster on random data); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/timsort/cpp-TimSort>
  - <https://github.com/gfx/cpp-TimSort>
  - <https://github.com/timsort/cpp-TimSort/commits>
  - <https://github.com/timsort/cpp-TimSort/wiki/Benchmark-results>
  - <https://github.com/timsort/cpp-TimSort/tree/3.x.y/benchmarks>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/HEAD/README.md>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wiki/timsort/cpp-TimSort/Benchmark-results.md>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/3.x.y/benchmarks/bench_sort.cpp>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/3.x.y/benchmarks/benchmarker.hpp>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/3.x.y/benchmarks/bench_merge.cpp>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/3.x.y/benchmarks/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/timsort/cpp-TimSort>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/HEAD/README.md>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/HEAD/include/gfx/timsort.hpp>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/HEAD/benchmarks/bench_sort.cpp>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/HEAD/benchmarks/bench_merge.cpp>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/HEAD/benchmarks/benchmarker.hpp>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/1.x.y/include/gfx/timsort.hpp>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/2.x.y/include/gfx/timsort.hpp>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/v3.0.0/include/gfx/timsort.hpp>
  - <https://raw.githubusercontent.com/timsort/cpp-TimSort/v3.0.1/include/gfx/timsort.hpp>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/share/classes/java/util/TimSort.java>
  - <https://raw.githubusercontent.com/python/cpython/main/Objects/listobject.c>
  - <https://github.com/timsort/cpp-TimSort/issues?q=is%3Aissue>
  - <https://github.com/timsort/cpp-TimSort/issues?q=minGallop>
  - <https://github.com/timsort/cpp-TimSort/issues/40>
  - <https://github.com/timsort/cpp-TimSort/issues/33>
  - <https://github.com/timsort/cpp-TimSort/issues/24>
  - <https://github.com/timsort/cpp-TimSort/issues/18>
  - <https://github.com/timsort/cpp-TimSort/issues/5>
  - <https://github.com/timsort/cpp-TimSort/releases>
  - <https://github.com/timsort/cpp-TimSort/commits/3.x.y>
  - <https://github.com/timsort/cpp-TimSort/wiki/Benchmark-results>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/gfx/cpp-timsort`) · [data/wave1/enrich/raw/github_com_gfx_cpp_timsort.json](../../../data/wave1/enrich/raw/github_com_gfx_cpp_timsort.json) (enrichment confidence 0.85)

</details>
