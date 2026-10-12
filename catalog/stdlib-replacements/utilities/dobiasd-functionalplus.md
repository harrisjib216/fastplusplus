# FunctionalPlus (fplus::keep_if)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Utilities](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only functional helpers (keep_if, transform, fold, compose) over STL containers; matches std::copy_if speed, does not beat it.

| | |
|---|---|
| **Beats** | std::copy_if (and a hand-written for loop) |
| **Claimed result** | No speedup claimed; parity: hand-written for loop 0.632 s, std::copy_if 0.641 s, fplus::keep_if 0.627 s (fplus::keep_if about 2% below std::copy_if, derived from page data). README: 'the compiler seems to do a very good job optimizing and inlining everything to basically equal machine code performance-wise.' |
| **Workload** | README example: keep the odd numbers of 5000 random integers, 20000 consecutive runs accumulated, comparing a hand-written loop, std::copy_if and fplus::keep_if. |
| **Metric** | throughput |
| **Hardware** | 'a standard desktop PC' (CPU model not stated) |
| **Compiler and flags** | GCC with -O3 (version not stated) |
| **Adoption** | 2.3k stars |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/Dobiasd/FunctionalPlus) · [benchmark](https://github.com/Dobiasd/FunctionalPlus/blob/master/examples/readme_perf_examples.cpp) |

## Verdict

First-party README run of examples/readme_perf_examples.cpp: keeping the odd values of 5000 rand() integers, 20000 runs accumulated, GCC with -O3 on an unnamed desktop PC, gave hand loop 0.632 s, std::copy_if 0.641 s and fplus::keep_if 0.627 s. Because keep_if on that input is std::copy_if, this shows zero abstraction overhead, not a speedup.

## Use it when

- Readability-first code that filters, maps and folds std::vector/std::list/std::string and wants value-returning functions instead of output iterators.
- Chained transformations where intermediate containers are r-values, so keep_if/sort/transform can reuse the input buffer in place.
- C++14 codebases that cannot move to C++20 std::ranges but want composable container operations.
- Prototyping data-processing code where a later profiling pass replaces only the hot stages with hand-written loops.

## Skip it when

- When you need a speedup over std::copy_if or a hand loop: the only published measurement is parity, and the code path is std::copy_if itself.
- Long pipelines on large inputs where materialising every intermediate container costs memory and bandwidth; lazy std::ranges or range-v3 views allocate nothing between stages (README).
- Hot paths that call the more complex functions; the README says some of them could be written more efficiently and invites reports.
- Build-time-sensitive projects: the umbrella header (the all-in-one fplus.hpp is about 16,100 lines, 565 KB) includes 43 distinct standard headers (iostream, fstream, future, thread, map, random among them), and the CMake target links Threads::Threads.

## How it is fast

It is not faster; it aims for zero overhead over the STL. keep_if on a const lvalue is literally std::copy_if into std::back_inserter on a fresh container (filter.hpp, create_new_container_t path), so it compiles to the same code as the baseline. When the argument is a non-const r-value (e.g. in chained calls) it dispatches on internal::can_reuse_v and filters in place with the erase-remove idiom, saving one allocation and copy per stage.

## Compared with alternatives

The catalogued utilities siblings (micron.cpp memcpy/memset, netbsd-curses) solve unrelated problems; pick FunctionalPlus only for expressive container algorithms at STL speed, not for a measured speedup.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none at runtime; CMake target requires Threads (find_package(Threads REQUIRED)); Python optional to regenerate fwd/curry headers |
| **Minimum toolchain** | C++14; GCC 4.9+, Clang 3.7+ with libc++ 3.7+, Visual Studio 2015+, Xcode 9+ |
| **Platforms** | any platform with a C++14 compiler and the standard library |
| **Thread safety** | Functions are pure over their arguments; transform_parallelly uses std::async and transform_parallelly_n_threads std::thread; benchmark_session guards its map with a std::mutex. No broader thread-safety statement is documented. |
| **Drop-in for the baseline** | partial — keep_if(pred, xs) replaces a copy_if-into-back_inserter idiom on a whole container, but it is not an iterator-based algorithm and always returns a new (or reused r-value) container |

## Gotchas

- Harness flaw: the README numbers come from examples/readme_perf_examples.cpp, which is public (the record's claim that no benchmark code is in the repo is wrong). In it fplus::keep_if receives a const lvalue, so it runs exactly std::copy_if with std::back_inserter; the 0.641 s vs 0.627 s gap is run-to-run noise between identical code, not a library effect.
- The same harness sets numRuns = 10 when NDEBUG is defined (the '#if defined NDEBUG || defined _DEBUG' guard is inverted relative to its 'make debug runs faster' comment), so a standard CMake Release build (-O3 -DNDEBUG) times only 10 runs; the README's 20000-run figures need a build without NDEBUG.
- Every timed call goes through std::function&lt;std::vector&lt;int&gt;(std::vector&lt;int&gt;)&gt; and copies the 5000-int input by value, an allocation plus 20 KB copy per iteration shared by all three variants, which dilutes any difference; timing uses system_clock, one pass, no spread.
- In-place reuse only happens for non-const r-values whose value_type is self-assignable; passing an lvalue silently allocates a new container.

## Known shortcomings

- Parity, not faster: keep_if 0.627 s vs std::copy_if 0.641 s; no benchmark code, CPU and GCC version unstated. Licence BSL-1.0.
- Enricher: the benchmark code is public at examples/readme_perf_examples.cpp (the verifier's 'no benchmark code' was wrong); keep_if on a const lvalue is std::copy_if plus std::back_inserter itself (filter.hpp), so 0.641 vs 0.627 s is noise between identical code; the numRuns guard '#if defined NDEBUG || defined _DEBUG' is inverted, so a CMake Release build runs 10 iterations, not 20000; every call goes through std::function and copies the 5000-int input; umbrella header 16,100 lines, 43 std headers.

## Caveats and trade-offs

This is a parity result, not a speed win: the only number in the README is a single 5000-element keep-odd micro-example in which fplus::keep_if is within about 2% of std::copy_if and a hand loop, and the README itself says the more complex functions could be written more efficiently. Hardware is 'a standard desktop PC', GCC version unstated, and the benchmark source is not linked from the README (no benchmark directory in the repo listing), so it is not reproducible from public code. Single-run style accumulated timing with no spread. The seed list tagged the licence MIT and a filesystems-and-io category; the repo is Boost Software License 1.0 and the library is a general container-algorithm helper, so the category was moved to stdlib-replacements/utilities. Kept as a documented 'not faster' entry. [retier] Parity, not faster (same code path as std::copy_if); numRuns guard inverted (10 iterations in Release); every call through std::function copying the 5000-int input; 16,100-line umbrella header.

Header-only functional-programming helpers (map, filter, fold, compose) over ordinary STL containers; requires C++14. Chained calls can reuse storage when given r-value containers, but not in every case, so complex functions can allocate and copy more than hand-written code. The README contrasts it with range-v3, whose lazy ranges allocate no intermediate containers, but gives no numbers for that.

## Maintenance

Active (last commit 2026-09-13 adding a Clang 23 CI build, version 0.2.28), BSL-1.0, 2.3k stars, packaged in vcpkg and Conan; copyable, but catalogued as a parity entry with no performance advantage over std::copy_if.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README Performance section gives hand loop 0.632 s, std::copy_if 0.641 s, fplus::keep_if 0.627 s ('a standard desktop PC', GCC with O3), but no benchmark code is in the repo (test/ has only unit tests; benchmark_session_test.cpp tests the timing utility, not this comparison), GCC version and CPU are unstated, so C.
- **Verifier notes:** Numbers match the README exactly; this is a parity result (about 2% from std::copy_if, within noise for a single accumulated run), so record it as 'not faster' rather than a win. Metadata checked: BSL-1.0 (LICENSE file), 2.3k stars, not archived, last commit 2026-09-13. baseline_stdlib left empty: GCC implies libstdc++ but the README does not say.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Shortcomings recorded by:** verifier batch-60 (wave 11); enricher w11 pair-022
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/README.md>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/test/benchmark_session_test.cpp>
  - <https://github.com/Dobiasd/FunctionalPlus>
  - <https://github.com/Dobiasd/FunctionalPlus/commits>
  - <https://github.com/Dobiasd/FunctionalPlus/tree/master/test>
- **Sources the enricher read:**
  - <https://github.com/Dobiasd/FunctionalPlus>
  - <https://github.com/Dobiasd/FunctionalPlus/commits>
  - <https://github.com/Dobiasd/FunctionalPlus/issues?q=is%3Aissue+performance>
  - <https://github.com/Dobiasd/FunctionalPlus/tree/master/examples>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/README.md>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/examples/readme_perf_examples.cpp>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/examples/performance_range_v3.cpp>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/examples/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/include/fplus/fplus.hpp>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/include/fplus/filter.hpp>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/include/fplus/container_common.hpp>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/include/fplus/container_traits.hpp>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/include/fplus/internal/container_common.hpp>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/include/fplus/internal/meta.hpp>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/include/fplus/transform.hpp>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/include/fplus/benchmark_session.hpp>
  - <https://raw.githubusercontent.com/Dobiasd/FunctionalPlus/HEAD/include_all_in_one/include/fplus/fplus.hpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/dobiasd/functionalplus`) · [data/wave11/enrich/raw/github_com_dobiasd_functionalplus.json](../../../data/wave11/enrich/raw/github_com_dobiasd_functionalplus.json) (enrichment confidence 0.85)

</details>
