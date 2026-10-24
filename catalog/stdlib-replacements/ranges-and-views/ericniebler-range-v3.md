# range-v3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Ranges and views](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only C++14/17/20 ranges library (basis of std::ranges); one bug-report benchmark beat an unshown hand-rolled loop by 3-13%.

| | |
|---|---|
| **Beats** | the issue's 'handrolled' implementation, marked '# base' in the reporter's table (its code is not shown, so it is not known to be a plain loop); the 'algorithm' row is a further comparison whose code is not shown either |
| **Claimed result** | Time per iteration, from the table in issue #1337 (reporter's machine): at -O2 range_common 10,816,578 ns vs handrolled 12,443,168 ns (about 13% less time, derived from page data) and vs algorithm 25,840,577 ns (about 2.4x faster, derived from page data); at -O3 range_common 9,305,111 ns vs handrolled 9,594,576 ns (about 3% less time, derived from page data) and vs algorithm 21,961,494 ns (about 2.4x faster, derived from page data). The ranges::to variant in the same table is slower than hand-rolled: 23,025,614 ns at -O2 and 21,293,927 ns at -O3 (the issue's subject). |
| **Workload** | Google Benchmark of a lazy views::transform \| views::common pipeline (append '!' to palindromic words) over a list of about 476k words, copied into a std::vector&lt;std::string&gt;, against a hand-rolled version and an 'algorithm' version. |
| **Metric** | throughput |
| **Hardware** | No CPU model named; Google Benchmark header 'Run on (2 X 2684.42 MHz CPU s)' for the reporter, '8 X 2900 MHz CPU s' for the maintainer's run |
| **Compiler and flags** | Compiler not stated in the issue; -O2 and -O3 (binary names benchmark-palindromes-o2 / -o3); Google Benchmark |
| **Adoption** | 4.4k stars; basis of C++20 std::ranges |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/ericniebler/range-v3) · [benchmark](https://github.com/ericniebler/range-v3/issues/1337) |

## Verdict

In issue #1337 (opened 2019-09-29), a reporter used Google Benchmark on a 2-CPU 2684 MHz machine with an unnamed compiler to time a palindrome-marking views::transform | views::common pipeline over about 476k words, copied into std::vector&lt;std::string&gt;. It took 10.8 ms against 12.4 ms for an unshown 'handrolled' version at -O2 (13% less time) and 9.31 ms against 9.59 ms at -O3 (3%, near noise), and was about 2.4x faster than an unshown 'algorithm' version; the ranges::to variant was 1.8x to 2.2x slower than hand-rolled, which is the issue's actual subject. The maintainer's re-run only compared the range_common and range_to forms, with a harness whose input grows between runs.

## Use it when

- C++14 or C++17 codebases that want C++20-style composable views and range algorithms before they can move to std::ranges.
- Code that needs pieces std::ranges lacks, such as actions (eager in-place container algorithms) or views::cache1 to stop a transform being re-evaluated.
- Simple single-pass pipelines (transform and filter over contiguous data) materialized through views::common and the container's iterator-pair constructor, the shape that matched or beat hand-rolled code in issue #1337.
- Writing expressive code first and then benchmarking hot spots, which is the maintainer's own advice in issue #668.

## Skip it when

- Hot loops built on views::concat or views::join: issue #1081 (open) has a 2021 report of about 11,800 ms with concat against about 630 ms without it at -O3 on Clang 11.0.2, issue #700 ('view::join is quite slow') is open, and the transrangers README reports range-v3 doing very badly on a concat|take|filter|transform test on Clang, GCC and Visual Studio.
- Materializing with ranges::to in a hot path: issue #1337 (open since 2019) measured it about 1.8x (-O2) to 2.2x (-O3) slower than the hand-rolled version.
- Debug builds and build-time-sensitive projects: a debug repro in #1081 took about 36 s with concat against 2.5 s without, and compile-time complaints appear in #758 and #1241.
- Projects that need API stability: the README promises no long-term stability outside the ranges::cpp20 namespace, and the last tagged release is 0.12.0 from June 2022.

## How it is fast

Views are lazy adaptors, so a transform/filter pipeline runs as one pass over the source with no intermediate containers. In the cited benchmark, views::common over a transform of a std::vector yields sized random-access iterators, so std::vector's iterator-pair constructor can size the result once and move-construct each transformed string into it; why this beat the unshown hand-rolled version is not explained (allocation strategy is a likely factor, inference). Where range-v3 loses, the cause is iterator abstraction the optimizer cannot see through: view_adaptor passing iterators by reference (issue #668), concat's variant-based iterator (issue #1081), and the extra end-of-range checks of pull-based filter and join that push-based designs such as transrangers avoid.

## Compared with alternatives

None of the catalogued siblings does the same job: svector, plf::colony, veque, EASTL and the other entries are containers, while range-v3 builds and transforms sequences that feed any of them. Pick it for lazy pipelines on pre-C++20 compilers or for adaptors std::ranges lacks; the 'sequence-containers' category is a poor fit, and the existing 'ranges-and-views' category matches better.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (packaged in vcpkg, Conan and build2; CMake target range-v3::range-v3) |
| **Minimum toolchain** | C++14; clang 6+, GCC 7+, Clang/LLVM 6+ on Windows, Visual Studio 2019+ with /permissive- and /std:c++17 or later |
| **Platforms** | any platform with a supported compiler |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — the algorithms keep iterator overloads like &lt;algorithm&gt; and add range overloads, but views, actions and ranges::to are a different interface in namespace ranges, not std |

## Gotchas

- Views are lazy and re-evaluate on dereference: a filter after a transform calls the transform function again for every element that passes (issue #1090); insert views::cache1 after an expensive transform.
- Views are non-owning, so lifetimes are the caller's problem: issue #964 is a heap-use-after-free with view::transform, zip_with and lambdas, and in #1081 a maintainer points out lambdas returning dangling views of lvalue containers.
- In #1337 the views::common plus iterator-pair-constructor form was the fast one and ranges::to the slow one. Current ranges::to reserves and then assigns when the range is sized (conversion.hpp), but no newer measurement shows whether that closes the gap, and the issue is still open.
- The repo's perf/range_conversion.cpp benchmark appends 2,856,000 words (476,000 x 6) in every fixture SetUp and never clears them. Google Benchmark calls SetUp before every run, so the input grows across its iteration-probing runs and can differ between the RangeCommon and RangeTo fixtures; its numbers (201.5 ms against 241.6 ms) are indicative only.

## Known shortcomings

- Issue #1337 numbers match, but the hand-rolled and algorithm code, compiler and CPU model are missing; the 3% win at -O3 is likely noise. The repo's perf/range_conversion.cpp has no hand-rolled baseline. A views library filed under sequence-containers, a loose category fit (no ranges category exists).
- Enricher: perf/range_conversion.cpp's Words fixture grows its input on every run (SetUp appends 2,856,000 words and never clears), so the repo's own RangeCommon vs RangeTo timings are indicative only; the reporter's -O3 win is 3%, near noise; hand-rolled baseline code unshown. Category moved to ranges-and-views.

## Caveats and trade-offs

Weak evidence for a speed win. The numbers come from a bug report titled 'ranges::to is significantly slower than direct construction' (opened 2019-09-29), not from a project claim; the README makes no performance claim and publishes no numbers. The repo's perf/range_conversion.cpp reproduces only the range_common and range_to functions from the issue (Words/RangeCommon vs Words/RangeTo), with no hand-rolled baseline. The win over the hand-rolled row is one workload, 13% at -O2 and 3% at -O3 (likely noise level) on a 2-CPU machine; the compiler is not stated and the bodies of the handrolled and algorithm functions are not shown, so what they do is unknown. The library version tested predates current releases. The maintainer's run (8 CPUs at 2900 MHz, -O3) only compared Words/RangeCommon 201,502,562 ns with Words/RangeTo 241,609,633 ns. No comparison against std::ranges was found. Reachable third-party results go the other way: the transrangers README (Clang 11.0, GCC 11.1, Visual Studio 2019, run on a GitHub Action VM, flags and CPU not stated, times normalized to Range-v3) says transrangers is generally equivalent to handwritten code on Clang and consistently outperforms Range-v3 by a large factor there, that handwritten code and transrangers are generally faster than Range-v3 on Visual Studio except test 1, and that Range-v3 performs very badly on test 2 (concat|take|filter|transform) in all compilers; on GCC tests 4 and 6 fluctuate run to run. Issue #668 ('Poor performance compared to STL', 2017-2019) has a maintainer note that a partial_sum benchmark from a Stack Overflow question was still about half the speed of the STL approach (no compiler or flags). Lead from the books: no timings are given there. Tier C with low confidence. [retier] Enricher: harness defect in perf/range_conversion.cpp: the Words fixture's SetUp appends 2,856,000 words (476,000 x 6) on every run and never clears, and Google Benchmark calls SetUp each run, so the input grows and may differ between Words/RangeCommon and Words/RangeTo; the maintainer's 201.5 vs 241.6 ms is indicative only. The reporter's -O3 win (3%) is near noise. Gotchas: transform followed by filter re-evaluates the transform (#1090, use views::cache1); views::concat is slow (#1081 open); last tag 0.12.0 (June 2022).

Header-only C++14/17/20 library. Views are lazy and non-owning, so lifetime of the underlying range is the caller's problem. Offers more adaptors than std::ranges (actions such as sort/unique/shuffle, extra views). Heavy template machinery: Niebler attributed slow cases to view_adaptor being hard for optimizers (issue #668). Conversion with ranges::to (a range-v3 extension) was about 1.8x (-O2) to 2.2x (-O3) slower than hand-rolled in the same issue's benchmark, derived from page data (issue open since 2019).

## Maintenance

Active (commits through 2026-10-10, 4.4k stars), but the last tag is 0.12.0 from June 2022; it is BSL-1.0, header-only and packaged in vcpkg, Conan and build2, with no stability promise outside ranges::cpp20.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Issue #1337 (opened 2019-09-29 by user cjdb) shows Google Benchmark tables where range_common beats the 'handrolled' row (marked '# base') at -O2 and -O3, but the handrolled and algorithm code, the compiler and the CPU model are not given, so this is a measurement without full methodology: C, not A or B.
- **Verifier notes:** All numbers in claimed_speedup match the issue tables exactly; last commit 2026-10-10, BSL-1.0, 4.4k stars confirmed. Category 'sequence-containers' looks off for a ranges/views library (the measured object is a view pipeline copied into a vector); consider a ranges/algorithms category override. Transrangers caveat reworded to what the README literally says.
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Shortcomings recorded by:** verifier batch-79 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/ericniebler/range-v3/issues/1337>
  - <https://github.com/ericniebler/range-v3>
  - <https://github.com/ericniebler/range-v3/commits/master>
  - <https://raw.githubusercontent.com/ericniebler/range-v3/master/perf/range_conversion.cpp>
  - <https://raw.githubusercontent.com/ericniebler/range-v3/master/perf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/joaquintides/transrangers/master/README.md>
  - <https://github.com/ericniebler/range-v3/issues/668>
- **Sources the enricher read:**
  - <https://github.com/ericniebler/range-v3>
  - <https://raw.githubusercontent.com/ericniebler/range-v3/HEAD/README.md>
  - <https://github.com/ericniebler/range-v3/issues/1337>
  - <https://raw.githubusercontent.com/ericniebler/range-v3/HEAD/perf/range_conversion.cpp>
  - <https://raw.githubusercontent.com/ericniebler/range-v3/HEAD/perf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ericniebler/range-v3/HEAD/include/range/v3/range/conversion.hpp>
  - <https://raw.githubusercontent.com/google/benchmark/HEAD/include/benchmark/benchmark_api.h>
  - <https://github.com/ericniebler/range-v3/issues/668>
  - <https://github.com/ericniebler/range-v3/issues?q=is%3Aissue+performance>
  - <https://github.com/ericniebler/range-v3/issues/1090>
  - <https://github.com/ericniebler/range-v3/issues/1081>
  - <https://github.com/ericniebler/range-v3/tags>
  - <https://raw.githubusercontent.com/joaquintides/transrangers/master/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ericniebler/range-v3`) · [data/wave1/enrich/raw/github_com_ericniebler_range_v3.json](../../../data/wave1/enrich/raw/github_com_ericniebler_range_v3.json) (enrichment confidence 0.7)

</details>
