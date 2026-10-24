# doctest

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compile caching and distribution](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Single-header C++11 unit-testing framework whose header and asserts compile far faster than Catch2 v2's single header.

| | |
|---|---|
| **Beats** | Catch2 (Catch 2.3.0 single header catch.hpp) |
| **Claimed result** | Header cost: doctest.h costs 11ms-23ms per source file against 380ms-470ms for catch.hpp (page: more than 36 times lighter on MSVC). 201 files with header everywhere, Linux GCC Release: 11.05s vs 99.48s (baselines 4.29s vs 4.50s); MSVC Release: 8.71s vs 87.17s. 50k CHECK(a==b) asserts, Linux GCC Release: 257.40s vs 608.94s; MSVC Release: 58.73s vs 448.68s (page: between 0 and 8 times faster than Catch); with DOCTEST_CONFIG_SUPER_FAST_ASSERTS 97.46s on Linux GCC Release. Runtime 10M asserts: MSVC Release 0.40s vs 0.76s, Linux GCC Release 0.29s vs 0.29s, Linux Clang Release 0.28s vs 0.32s; with INFO logging Linux GCC Release 0.52s vs 3.60s (page: around 20% faster for plain asserts, a few times faster with logging). |
| **Workload** | bench.py-generated CMake projects built single-threaded: (1) 201 source files with the framework header included in every file, (2) 50k CHECK(a==b) asserts across 10 files, (3) a runtime loop of 10 million passing CHECK(i == i) asserts, with and without INFO(i) logging. |
| **Metric** | compile-time |
| **Hardware** | Intel i7 3770k, 16G RAM; Windows 7 on an SSD, and Ubuntu 17.04 in a VirtualBox VM on a HDD |
| **Compiler and flags** | MSVC 2017 15.8.1, MinGW-w64 GCC 8.1.0, Linux GCC 6.3.0, Linux Clang 4.0.0. scripts/bench/bench.py configures CMake with CMAKE_BUILD_TYPE Debug or Release (so CMake's default per-config flags apply: -O3 -DNDEBUG for GCC/Clang Release, /O2 /Ob2 /DNDEBUG for MSVC Release), adds -std=c++11 on non-MSVC and -w on GCC/Clang, and builds single-threaded with cmake --build; scripts/bench/run_all.py averages 3 runs per table cell. |
| **Adoption** | 6.9k stars |
| **Last commit** | 2026-03-27 |
| **Links** | [repository](https://github.com/doctest/doctest) · [benchmark](https://raw.githubusercontent.com/doctest/doctest/HEAD/doc/markdown/benchmarks.md) |

## Verdict

The project's own December 2018 benchmark built bench.py-generated CMake projects single-threaded with doctest 2.2.0 and Catch 2.3.0 on an Intel i7 3770k (Windows 7 on SSD with MSVC 2017 15.8 and MinGW GCC 8.1; Ubuntu 17.04 in a VirtualBox VM on HDD with GCC 6.3 and Clang 4.0): including the header in 200 files took 8.71 s vs 87.17 s on MSVC Release and 11.05 s vs 99.48 s on Linux GCC Release, and 50k CHECK(a==b) asserts took 58.73 s vs 448.68 s on MSVC Release but 257.40 s vs 608.94 s on Linux GCC Release (about 2.4x, derived from page data). Runtime of 10M passing asserts was near parity on GCC and Clang Release and several times faster only with INFO() logging.

## Use it when

- Test headers included in many translation units, or tests written inline in production .cpp/.h files: the 2018 run measured 11-23 ms per extra TU for doctest.h against 380-470 ms for Catch 2.3.0's catch.hpp
- Replacing a Catch2 v2 single-header (catch.hpp) setup where header cost dominates the test build; the FAQ gives SECTION and tagged TEST_CASE macro shims for migration
- Codebases held to C++11/14/17, where [Boost].UT (C++20 only) is not an option
- Suites with tens of thousands of asserts where you can switch to CHECK_EQ-style binary asserts and define DOCTEST_CONFIG_SUPER_FAST_ASSERTS (the page's fastest assert-compile configuration)
- Shipping tests inside release sources and removing them from the final binary with DOCTEST_CONFIG_DISABLE

## Skip it when

- Already on Catch2 v3 (a compiled library with cheap per-test headers): no benchmark covers it, and issue #1168 (June 2026) reports a 13-file, 1,273-assert executable taking about 30 s with both Catch2 v3.7.1 and doctest 2.5.2 (MSVC 14.44 and GCC 13.1); a maintainer replied that the benchmarks are outdated and that doctest.h now pulls in all of its machinery
- Expecting faster test execution for plain asserts: the page shows parity on Linux GCC Release (0.29 s vs 0.29 s for 10M asserts) and a small gap on Clang Release (0.28 s vs 0.32 s); the big runtime wins appear only with INFO() logging
- Needing death tests or first-class Google Mock integration (the FAQ lists both as gaps versus Google Test), Catch2's micro-benchmarking, or in-process parallel execution of test cases (test cases run serially; parallelism means launching the binary several times with test ranges)
- Generating many SUBCASEs in a loop on doctest 2.5.0-2.5.3: issue #1208 (open) reports super-linear scaling from a linear sibling scan added in 2.5.0, with one reporter's binary going from 112 s on 2.4.12 to 2420 s
- Optimized builds with Visual Studio 2026 cl.exe 19.51+: issue #1138 (open) reports some CHECK()/CHECK_UNARY() calls evaluating incorrectly; the reporter attributes it to an MSVC regression and filed it with Microsoft

## How it is fast

The public part of doctest.h forward-declares what it needs (it even forward-declares std::ostream, std::istream, std::tuple and std::nullptr_t inside namespace std) and pulls no standard headers into user translation units; all the iostream, container and threading includes live only in the implementation TU. Expression-decomposing CHECK(a==b) uses template machinery (ExpressionDecomposer plus a ResultBuilder wrapped in try/catch); DOCTEST_CONFIG_SUPER_FAST_ASSERTS collapses each assert into a single call to an out-of-line, non-inlined function (decomp_assert, binary_assert, unary_assert) with no try/catch, and the binary CHECK_EQ(a,b) form skips expression decomposition entirely. Together these cut per-assert instantiation and code size, which is where the assert-compile gains come from.

## Compared with alternatives

Against [Boost].UT, pick doctest when you cannot require C++20, want the more widely used Catch-style macro API, or have large multi-file suites, where UT's own benchmark shows doctest compiling as fast or faster except at gcc9 -O3. The cache and distribution tools in this category (ccache, sccache, distcc, FASTBuild and others) are complementary: they cut rebuild cost of any test framework, while doctest cuts the per-translation-unit cost of the test code itself.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none |
| **Minimum toolchain** | C++11 (tag 1.2.9 for C++98); features page (marked partly outdated) lists GCC 4.8-12, Clang 3.5-15 and MSVC 2015-2022 as tested |
| **Platforms** | Windows, Linux and macOS in CI; any C++11 compiler claimed; Windows SEH and POSIX signal handling are configurable |
| **Thread safety** | Assertion and logging macros may be called from multiple threads spawned by one test case; test cases run serially and SUBCASEs must be used only from the runner thread. DOCTEST_CONFIG_NO_MULTITHREADING removes the threading support for single-threaded speed. |
| **Drop-in for the baseline** | partial — Catch-like macro surface (TEST_CASE, CHECK, REQUIRE, INFO, Approx), but SECTION becomes SUBCASE, Catch tags must be folded into test names, and Catch matchers, BENCHMARK and other features differ; the FAQ supplies a few #define shims for the common cases |

## Gotchas

- DOCTEST_CONFIG_SUPER_FAST_ASSERTS implies DOCTEST_CONFIG_NO_TRY_CATCH_IN_ASSERTS: an exception thrown while evaluating an assert aborts the whole test case, and a debugger breaks inside doctest's internal function instead of at the assert line
- The default forward declarations of std::ostream, std::tuple and friends inside namespace std are not permitted by the C++ standard; a niche standard library can fail to compile, and DOCTEST_CONFIG_USE_STD_HEADERS fixes it at the cost of including the real headers
- Self-registering tests compiled into a static library are dropped by the linker unless something references their object file; use CMake OBJECT libraries, the shipped doctest_force_link_static_lib_in_target() helper, or /OPT:NOREF or /WHOLEARCHIVE on MSVC
- char\* operands are compared as pointers unless DOCTEST_CONFIG_TREAT_CHAR_STAR_AS_STRING is defined

## Known shortcomings

- 2018 run (doctest 2.2.0 vs Catch 2.3.0, no Catch2 v3); Linux results from a VirtualBox VM on an HDD; scripts/bench/bench.py edited since the run; no variance given. Plain-assert runtime at parity on GCC; Linux GCC assert compile only 2.4x. A test framework measured on compile time: compile-caching-and-distribution is a loose category fit (no test-framework category exists).

## Caveats and trade-offs

The project's own benchmark (Dec 2018): doctest 2.2.0 against Catch 2.3.0, both far behind current releases; Catch2 v3 became a compiled library with a different compile-time profile and was not measured. Flags come from the public script (CMake build-type defaults) rather than the page text. Linux numbers come from a VirtualBox VM on a HDD. run_all.py at HEAD averages 3 runs per cell, but the page gives no variance, and bench.py has been edited since the 2018 run (a 2019 fix, a 2025 newline/encoding chore, a 2026 cmake_minimum_required bump to 3.14), so a rerun uses a slightly different script. Runtime for plain asserts is near parity on GCC and Clang Release (0.29s vs 0.29s, 0.28s vs 0.32s); the large runtime win is only with INFO logging (the page's 'over 18 times faster' case is MSVC Debug, 11.41s vs 213.91s). README says compile time is better 'by orders of magnitude', while the tables show roughly 9-10x on whole-build header cost and up to about 8x on assert macros (MSVC Release 58.73s vs 448.68s; Linux GCC Release only about 2.4x, derived from page data). Google Test and Boost.Test are not benchmarked on the page. doctest is a unit-testing framework whose speed claim is compile time; it does not cache or distribute builds.

Smaller feature set than Catch2 (modelled on Catch; the FAQ lists the differences, not read). The biggest assert-compile wins need the non-decomposing CHECK_EQ(a,b) form and the DOCTEST_CONFIG_SUPER_FAST_ASSERTS define, so they are not like-for-like with Catch's CHECK(a==b). DOCTEST_CONFIG_DISABLE strips tests from the binary. Single header, C++11.

## Maintenance

Actively maintained (v2.5.3 tagged 2026-07-06, dev branch commits through 2026-10-18; master stops at the v2.5.0 release commit of 2026-03-27), MIT-licensed single header that is trivial to vendor, though maintainers themselves call the benchmark suite outdated and plan to redo it for 2.6.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** doc/markdown/benchmarks.md compares doctest 2.2.0 against Catch 2.3.0 using the public harness scripts/bench/bench.py (generates the sources and CMakeLists, downloads catch.hpp 2.3.0, times cmake --build) driven by scripts/bench/run_all.py, with compiler versions and the CPU (Intel i7 3770k) stated; flags are fixed by the script (CMAKE_BUILD_TYPE Debug/Release, -std=c++11, -w), so the setup is reproducible.
- **Verifier notes:** All claimed_speedup numbers match the page rows. Category compile-caching-and-distribution is a loose fit (test framework with a compile-time claim); orchestrator may want a category/domain override. Metadata checked on github.com: MIT, 6.9k stars, not archived or fork, last commit 2026-03-27 (v2.5.0 release).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-11 (wave 2 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/doc/markdown/benchmarks.md>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/scripts/bench/bench.py>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/scripts/bench/run_all.py>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/LICENSE.txt>
  - <https://github.com/doctest/doctest>
  - <https://github.com/doctest/doctest/commits/master>
  - <https://github.com/doctest/doctest/commits/master/scripts/bench/bench.py>
- **Sources the enricher read:**
  - <https://github.com/doctest/doctest>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/README.md>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/doc/markdown/benchmarks.md>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/doc/markdown/faq.md>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/doc/markdown/features.md>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/doc/markdown/configuration.md>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/doc/markdown/assertions.md>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/doc/markdown/build-systems.md>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/scripts/bench/bench.py>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/scripts/bench/run_all.py>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/scripts/bench/tests.json>
  - <https://raw.githubusercontent.com/doctest/doctest/HEAD/doctest/doctest.h>
  - <https://github.com/doctest/doctest/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/doctest/doctest/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/doctest/doctest/issues/1168>
  - <https://github.com/doctest/doctest/issues/1208>
  - <https://github.com/doctest/doctest/issues/1138>
  - <https://github.com/doctest/doctest/tags>
  - <https://github.com/doctest/doctest/commits/dev>
  - <https://github.com/doctest/doctest/commits/master>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/doctest/doctest`) · [data/wave2/enrich/raw/github_com_doctest_doctest.json](../../../data/wave2/enrich/raw/github_com_doctest_doctest.json) (enrichment confidence 0.85)

</details>
