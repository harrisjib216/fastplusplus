# [Boost].UT (boost-ext/ut)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compile caching and distribution](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Macro-free C++20 single-header/module unit-testing framework whose 2019 benchmark compiled faster than Boost.Test, GoogleTest and Catch2.

| | |
|---|---|
| **Beats** | GoogleTest 1.10.0, Catch2 2.10.2, Boost.Test 1.71.0, doctest 2.3.5 (compile time of test code using each framework) |
| **Claimed result** | README: 'Compiles 5x faster because it doesn't introduce a new type for each lambda' (design claim, no number attached) and 'faster to compile and execute than similar frameworks'. Benchmark results exist only as bar-chart images; values read off the charts (approximate): include-only compile about 0.4 s for UT vs about 1.0 s Boost.Test, 0.8 s GoogleTest, 5 to 16 s Catch2, 1.3 to 3.3 s doctest. 1,000 tests in one file, clang9 default: UT about 1 s vs about 7 s Boost.Test, 4.5 s GoogleTest, 5.5 s Catch2, 2.2 s doctest. 100-file suite with asserts and STL, clang9 default: UT about 55 s vs about 195 s Boost.Test, 130 s GoogleTest, 110 s Catch2, 50 s doctest; gcc9 -O3: UT about 230 s vs about 730 s Boost.Test, 430 s GoogleTest, 705 s Catch2, 270 s doctest. Execution of that suite (unoptimized): UT about 0.04 s vs about 1.1 s Boost.Test, 0.1 s GoogleTest, 1.8 s Catch2, 0.5 s doctest. |
| **Workload** | Compile and run synthetic test programs generated from templates: 0 tests (include only), 1 test with 1,000,000 asserts, 1,000 tests in one file, and a 100-file suite of 10,000 tests with 20,000 to 40,000 asserts (with and without STL use), built by clang 9 and gcc 9 in default, -g and -O3 modes. |
| **Metric** | compile-time |
| **Compiler and flags** | Public bench.sh: clang++ and g++ (gcc 9.2.0 toolchain) with -std=c++2a; variants default, -g and -O3 -DNDEBUG; UT-only extra runs with -stdlib=libc++. Catch2 built with CATCH_CONFIG_FAST_COMPILE, doctest with DOCTEST_CONFIG_SUPER_FAST_ASSERTS, Boost.Test and GoogleTest as static libraries. |
| **Adoption** | 1.4k stars |
| **Last commit** | 2026-10-24 |
| **Links** | [repository](https://github.com/boost-ext/ut) · [benchmark](https://github.com/cpp-testing/ut-benchmark) |

## Verdict

UT's own linked benchmark (cpp-testing/ut-benchmark, 2019) compiled generated test programs one translation unit at a time with clang 9 (gcc 9.2 libstdc++) and gcc 9 in default, -g and -O3 -DNDEBUG modes, timing each cell once with GNU time on an unstated machine: UT 1.1.0 against GoogleTest 1.10.0 and Boost.Test 1.71.0 (prebuilt static libraries), Catch2 2.10.2 (CATCH_CONFIG_FAST_COMPILE) and doctest 2.3.5 (DOCTEST_CONFIG_SUPER_FAST_ASSERTS). Read off bar charts, include-only took about 0.4 s for UT against 0.8-1.0 s for GoogleTest/Boost.Test and 1.3-16 s for doctest and Catch2 (which compile their whole runner in that file), and the 100-file STL suite took about 55 s against 50-195 s with clang9 default.

## Use it when

- C++20 code bases that want macro-free tests using std::source_location, concepts and designated-initializer configuration
- Moving off Boost.Test, GoogleTest or a Catch2 v2 single header where test-code compile time hurts: on the 2019 100-file suite with STL asserts (clang9 default) UT took about 55 s against about 195 s, 130 s and 110 s (chart readings)
- Many small test cases per file: 1,000 empty tests in one file compiled in about 1 s against about 2.2 s (doctest) to 7 s (Boost.Test) with clang9 default
- Projects that want a test framework consumable as a C++20 module or need a custom runner/reporter (for example JUnit output) without forking the framework

## Skip it when

- Anything below C++20, or Clang 12-16 with libstdc++: issue #637 (open) reports segfaults and silently skipped tests traced to initialization-order assumptions for the cfg variable template; workarounds are a single test TU with cfg instantiated first, -stdlib=libc++, or staying on v1.1.9
- Large multi-file suites where doctest is the alternative: on the same 2019 chart doctest compiled the 100-file suite about as fast as UT in default and -g modes and faster with clang9 -O3 (about 145 s vs 215 s); UT led only with gcc9 -O3 (about 230 s vs 270 s)
- Expecting the published numbers to hold for current UT: they measure 1.1.0 with the interface/implementation split; the current header pulls in more than three times as many standard headers (25 against 7) and has not been re-benchmarked
- Needing built-in mocking (the README points to GUnit, FakeIt or hippomocks), abort/death checks on Windows (aborts() uses fork() and is Unix-only), or a working in-process parallel runner (issue #641 reports the parallel-runner example ran every suite on one thread)
- Relying on C++20 modules today: issues #713, #697, #650 and #623 (open) report import boost.ut failing, module builds breaking, and tests always skipped when ut is included into a module

## How it is fast

The README's FAQ credits a few design choices: tests are assigned through a plain function pointer (operator=(void (\*)())) rather than a template instantiated for every lambda type (the header comment says this 'compiles 5x faster', with no benchmark attached); type-name erasure so comparison objects such as eq&lt;int, int&gt; can be memoized; simplified internal versions of std::function and std::string_view; and a single header with few includes. In the benchmarked UT 1.1.0 the test files defined BOOST_UT_INTERFACE and saw only a slim interface (7 standard includes), with the runner compiled once in a BOOST_UT_IMPLEMENTATION translation unit; that split is absent from v1.1.9 onward, and v2.0.0 through v2.3.1 include 25 standard headers plus &lt;format&gt; and &lt;source_location&gt; when available.

## Compared with alternatives

Against doctest, pick UT for C++20-only code with many small tests per file or when you want macro-free syntax; the 2019 chart shows UT clearly ahead on include-only and single-file workloads, while doctest ties or wins on large multi-file suites and also supports C++11. The cache and distribution siblings (ccache, sccache, distcc, FASTBuild and others) are complementary: they reduce rebuild cost for any test framework rather than the cost of compiling test code itself.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none |
| **Minimum toolchain** | C++20; README lists GCC 9+, Clang 9+, Apple Clang 11+, MSVC 2019+ (asterisked) and Clang-cl 9+ as tested |
| **Platforms** | any platform with a C++20 compiler; aborts() is limited to Unix-like systems because it uses fork() |
| **Thread safety** | not documented; ut.hpp contains no mutex or atomic, so concurrent expect() calls from several threads are not synchronized by the framework |
| **Drop-in for the baseline** | no |

## Gotchas

- expect(a == b) on plain built-in values only prints [false] on failure; to see the operands you must use the UT literals (1_i == 2), that % a == b, or eq()/neq(), which also reject mixed-type comparisons
- Test registration relies on static objects and the cfg variable template; across several translation units with some compilers this has produced crashes or skipped tests (issue #637)
- With using namespace boost::ut, the framework's nothrow can clash with the libstdc++ declaration (issue #648); throws()/nothrow() exist only when exceptions are enabled (__cpp_exceptions)
- The benchmark's 'suite' workloads gave Catch2 and doctest one TEST_CASE with 100 SECTION/SUBCASE blocks per file but gave UT and GoogleTest 100 separate tests, so the execution-time bars for Catch2 (about 1.8 s) and doctest (about 0.5 s) partly measure section re-entry rather than framework overhead

## Known shortcomings

- First-party charts, no CPU model; benchmark repo has no licence file. doctest compiles faster than UT on the large suite with clang9 -O3 (about 145 s vs 215 s) and ties with gcc9 default and -g. A test framework measured on compile time: compile-caching-and-distribution is a loose category fit (no test-framework category exists).
- Enricher: benchmarked 1.1.0 predates the v2.x include growth (7 to 25 std headers); Catch2/doctest get one TEST_CASE with 100 sections against 100 separate tests for UT/GoogleTest; single-file workloads build the doctest/Catch2 runner but link prebuilt GoogleTest/Boost.Test; one run per cell; open #637 (Clang 12-16 static-init SEGV).

## Caveats and trade-offs

Numbers come only from bar-chart PNGs in the benchmark repo (no tables), so every figure above is read off a chart and approximate. The CPU model and machine are not stated anywhere, so the run falls short of tier A. The benchmark repo (cpp-testing/ut-benchmark, 13 stars, no license file) is the UT README's own linked benchmark, i.e. first-party. Versions are from 2019 (UT 1.1.0, GoogleTest 1.10.0, Catch2 2.10.2, doctest 2.3.5, Boost.Test 1.71.0, gcc 9 and clang 9); UT itself is now at 2.x and newer releases of every framework exist and were not re-measured. On the large suite+assert+stl workload doctest matches or beats UT: about 50 s vs 55 s with clang9 default, about equal with gcc9 default and -g (about 80 s and 88 s each), and clearly faster with clang9 -O3 (about 145 s vs 215 s); only with gcc9 -O3 is UT ahead (about 230 s vs 270 s). UT's compile-time lead is clear against Boost.Test, GoogleTest and Catch2 and mixed against doctest; on the include-only and 1,000-test single-file workloads UT leads all frameworks including doctest. The '5x faster because it does not introduce a new type for each lambda' line is a code comment in the README's implementation section, a design claim with no benchmark behind it. UT's own test registration style differs from the baselines, so workloads are not byte-identical test programs. [retier] Enricher: the benchmarked 1.1.0 used a BOOST_UT_INTERFACE/IMPLEMENTATION split that is gone by v1.1.9, and standard includes grew from 7 to 25 in v2.x, so current compile cost is unmeasured. The suite gives Catch2 and doctest one TEST_CASE with 100 SECTION/SUBCASE per file but UT and GoogleTest 100 separate tests, so execution bars are not like-for-like; single-file workloads time the full doctest/Catch2 runner build while GoogleTest and Boost.Test link prebuilt libraries; one run per cell. Open #637: SEGV or skipped tests on Clang 12-16 (static-init order).

Needs C++20 (GCC 9+, Clang 9+, Apple Clang 11+, MSVC 2019+). Single header or C++20 module, macro-free API built on concepts, source_location and designated initializers, so error messages and idioms differ from GoogleTest, Catch2 and doctest; the project is a testing framework, not a build tool, so its place in the compile-caching category is a loose fit for 'faster to compile test code'.

## Maintenance

Actively maintained (commits through 2026-10-24, latest tag v2.3.1 from 2025-04-02), BSL-1.0 and a single header that is easy to vendor, but the speed evidence is a first-party 2019 run of UT 1.1.0 that has never been refreshed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark (cpp-testing/ut-benchmark, linked from the UT README as its benchmark) with public code (benchmarks/bench.sh, Makefile) and stated compilers and flags (clang++ with gcc 9.2.0 toolchain, g++, -std=c++2a, -g, -O3 -DNDEBUG), but no CPU model or machine, so not A; first-party, so C.
- **Verifier notes:** All chart readings in claimed_speedup checked against the PNGs and match. Added the clang9 -O3 suite row where doctest compiles faster than UT. Category compile-caching-and-distribution is a loose fit for a unit-testing framework whose claim is faster compile of test code; orchestrator may want a category override.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-09 (wave 2 book seed pass, 2026-10-24); enrichment (wave 2 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/boost-ext/ut>
  - <https://github.com/boost-ext/ut/commits>
  - <https://github.com/cpp-testing/ut-benchmark>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/bench.sh>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/results/Compilation_include.png>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/results/Compilation_test.png>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/results/Compilation_suite+assert+stl.png>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/results/Execution_suite+assert+stl.png>
- **Sources the enricher read:**
  - <https://github.com/boost-ext/ut>
  - <https://raw.githubusercontent.com/boost-ext/ut/HEAD/README.md>
  - <https://raw.githubusercontent.com/boost-ext/ut/HEAD/include/boost/ut.hpp>
  - <https://raw.githubusercontent.com/boost-ext/ut/v1.1.0/include/boost/ut.hpp>
  - <https://raw.githubusercontent.com/boost-ext/ut/v1.1.9/include/boost/ut.hpp>
  - <https://raw.githubusercontent.com/boost-ext/ut/v2.0.0/include/boost/ut.hpp>
  - <https://github.com/boost-ext/ut/commits>
  - <https://github.com/boost-ext/ut/tags>
  - <https://github.com/boost-ext/ut/issues>
  - <https://github.com/boost-ext/ut/issues/637>
  - <https://github.com/boost-ext/ut/issues/641>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/bench.sh>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/ut/suite+assert+stl.erb>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/doctest/suite+assert+stl.erb>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/catch2/suite+assert+stl.erb>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/googletest/suite+assert+stl.erb>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/ut/include.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/doctest/include.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/catch2/include.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/googletest/include.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/ut/main.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/doctest/main.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/catch2/main.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/ut/test.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/doctest/test.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/ut/assert.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/doctest/assert.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/catch2/test.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/catch2/assert.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/googletest/test.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/benchmarks/googletest/assert.cpp>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/results/Compilation_include.png>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/results/Compilation_suite+assert+stl.png>
  - <https://raw.githubusercontent.com/cpp-testing/ut-benchmark/master/results/Execution_suite+assert+stl.png>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/boost-ext/ut`) · [data/wave2/enrich/raw/github_com_boost_ext_ut.json](../../../data/wave2/enrich/raw/github_com_boost_ext_ut.json) (enrichment confidence 0.8)

</details>
