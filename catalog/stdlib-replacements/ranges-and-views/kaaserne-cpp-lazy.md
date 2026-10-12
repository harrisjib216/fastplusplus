# cpp-lazy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Ranges and views](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++11 lazy-iterator library; first-party 32-element benchmarks show filter 3.6x and chunks 2.6x faster than std::views.

| | |
|---|---|
| **Beats** | std::ranges / std::views (libstdc++ 13): filter, chunk, chunk_by, lazy_split, stride, slide, zip, cartesian_product, repeat, take, join |
| **Claimed result** | README Benchmarks section plus bench/benchmarks-iterators-23.png, per-element column (lz vs std, i.e. time per 32-element pass divided by 32): filter 0.2263 ns vs 0.8116 ns (about 3.6x faster, derived from page data); chunks 0.2425 ns vs 0.6376 ns (about 2.6x); split_single (lz::split vs views::lazy_split on ' ') 0.3902 ns vs 0.5568 ns (about 1.4x); chunk_if 0.4922 ns vs 0.5351 ns (about 1.09x); flatten 0.7095 ns vs 0.7771 ns (about 1.10x). The split_multiple row (0.4866 ns vs 0.8532 ns) is not like-for-like: the std side passes the literal "o " to views::lazy_split, whose pattern then includes the terminating NUL and never matches (one piece instead of six), so it is excluded. Parity within about 1 to 4 percent: map 0.2384 vs 0.2374, repeat 0.2389 vs 0.2372, take_iterable 0.2397 vs 0.2378, take_iterator 0.2389 vs 0.2386, common 0.2399 vs 0.2386, pairwise 0.4477 vs 0.4602, zip2/zip3/zip4 0.4904/0.7233/0.9545 vs 0.4764/0.7238/0.9582, cartesian_product 1.1439 vs 1.1684. Slower than std: take_every 0.9186 ns vs 0.5455 ns for std::views::stride (about 1.7x slower). |
| **Workload** | Google Benchmark (v1.9.1) microbenchmarks over 32-element std::arrays and a 32-character string: each timed iteration constructs the lz:: or std::views adaptor and walks it once with benchmark::DoNotOptimize on each element; the chart divides that time by 32. Built as C++23 with gcc 13.3.0. |
| **Metric** | throughput |
| **Compiler and flags** | gcc 13.3.0 (README); bench/CMakeLists.txt sets no CMAKE_BUILD_TYPE or optimization flags and takes the standard from CMAKE_CXX_STANDARD (23 per the image name; views::chunk, chunk_by and stride need it), so the flags used are not public. |
| **Adoption** | 365 stars |
| **Last commit** | 2026-07-06 |
| **Links** | [repository](https://github.com/Kaaserne/cpp-lazy) · [benchmark](https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/bench/benchmarks-iterators-23.png) |

## Verdict

The project's Google Benchmark 1.9.1 suite builds each adaptor over a 32-element std::array (or 32-char string), walks it once per iteration and reports time per element, with gcc 13.3.0, libstdc++ and C++23. lz::filter took 0.23 vs 0.81 ns per element for std::views::filter (3.6x, predicate matches only the first element), lz::chunks 0.24 vs 0.64 ns for views::chunk (2.6x), split on a char 1.4x over views::lazy_split, and chunk_if and flatten about 1.1x. Most other adaptors were at parity and views::stride was 1.7x faster than lz::take_every; no CPU model or optimization flags are published.

## Use it when

- C++11/14/17 codebases that want composable lazy map/filter/zip/chunk/split/flatten pipelines without moving to C++20 or pulling in range-v3.
- Hot loops that filter or cut contiguous containers into fixed-size chunks: the first-party chart shows these with the largest per-element gaps (3.6x filter, 2.6x chunks vs libstdc++ std::views at gcc 13.3).
- You need adaptors std::views does not have (zip_longest, except, intersection, join_where, unique, duplicates, regex_split, random, interleave).
- Splitting random-access strings into string_view pieces (lz::sv_chunk_if) without lazy_split's inner-range types.

## Skip it when

- C++20/23 code that mostly uses transform, take, zip, repeat, slide or cartesian_product: the same benchmark shows lz within about 1-4% of std::views there, so there is nothing to gain.
- Strided iteration: std::views::stride beat lz::take_every by about 1.7x in the project's own chart.
- You rely on std::ranges concepts, projections or views composing with std::ranges algorithms: lz is a separate API, and sentinelled lz iterables need lz::common before classic STL algorithms.
- Lifetime-sensitive code: lz iterables keep a reference to any input that does not derive from lz::lazy_view (std::vector, std::array, std::string, user ranges), so they dangle if the input dies first unless wrapped with lz::copied / lz::as_copied.
- You need a heavily used, multi-maintainer library: 365 stars, and v9.0.0 broke the API (PascalCase to snake_case, iterators switched to sentinels).

## How it is fast

There is no exotic algorithm: the adaptors are thin iterator wrappers that keep as little state as possible. Forward iterables return an lz::default_sentinel_t instead of storing a second end iterator. lz::filter advances by calling the classic std::find_if whenever its iterator and sentinel types match (Lz/detail/algorithm/find_if.hpp), so the scan is the standard library's own find loop. For random-access inputs lz::chunks stores only the chunk start and computes each chunk's end with one min(chunk_size, end - begin) on dereference. The measured gains are code-generation differences against libstdc++'s view iterators on tiny inputs, not a new technique.

## Compared with alternatives

No siblings catalogued yet.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none required; {fmt} is optional for printing (the CMake build fetches fmt 12.1.0 unless CPP_LAZY_USE_STANDALONE is set; without CMake define LZ_STANDALONE) |
| **Minimum toolchain** | C++11 (range-for over sentinelled iterables needs C++17; optional module build needs C++20); CMake 3.14 for the CMake package |
| **Platforms** | any; README and CI cover GCC, Clang, MSVC and Apple Clang |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- lz::chunk_if drops the delimiter element: tests/chunk_if.cpp expects {1},{3},{5} for an is-even split of {1..5}, while the header's own doc comment shows {1,2},{3,4},{5}. It is not equivalent to std::views::chunk_by, which keeps every element.
- Benchmark harness flaws beyond those the verifier found: in the chunk_if row lz emits 31 elements (delimiter 16 dropped) while std::views::chunk_by emits 32, yet both are divided by 32. The split rows compare against std::views::lazy_split, not the C++20 std::views::split meant for contiguous strings. The README says view creation is excluded, but every benchmark builds the view inside the timed loop. No CPU model is given and bench/CMakeLists.txt sets no build type or optimization flags.
- Since v9.0.0 many iterables return lz::default_sentinel_t instead of a matching end iterator. Iterate them with range-for on C++17+ or lz::for_each on C++11/14, and call lz::common as late as possible in a chain before handing them to code that needs begin/end of the same type.
- CPP_LAZY_DEBUG_ASSERTIONS is on by default in CMake Debug builds and, with GCC/Clang at C++23, links stdc++_libbacktrace. Set it OFF if Debug builds must not carry that dependency.

## Known shortcomings

- The split_multiple row is invalid: the std side passes 'o ' with the NUL included in the pattern to views::lazy_split, yielding 1 piece against 6 (checked with a std-only g++ 13.3 snippet), so that row is dropped from the claim; the README says view creation is excluded while the code times it; bench/CMakeLists.txt sets no build type or flags; no CPU; take_every is slower than std::views::stride. Filed under stdlib-replacements/ranges-and-views (new category) by override although mined into wave 11; the repo moved from MarcDirven to Kaaserne/cpp-lazy.
- Enricher: the chunk_if row is not like-for-like (lz::chunk_if drops the delimiter, so 31 elements are emitted vs 32 for views::chunk_by, both divided by 32; the header doc example contradicts tests/chunk_if.cpp); the split rows use views::lazy_split, not views::split; the filter 3.6x is a codegen gap (lz::filter calls classic std::find_if). No CPU, no flags, views built inside the timed loop.

## Caveats and trade-offs

First-party benchmark with public code but no CPU model, no published optimization flags (bench/CMakeLists.txt sets none) and the standard library only implied (libstdc++ inferred from gcc 13.3.0), so tier C. Tiny workload: 32 elements; the filter predicate (i == 0) matches only the first element, so the 3.6x filter figure measures scanning 32 ints for one match. The README says iterable creation is excluded, but bench/benchmarks-iterators.cpp constructs both the lz and std views inside the timed loop. The split_multiple row is invalid as a comparison: std::views::lazy_split(to_split, "o ") treats the NUL terminator as part of the pattern and yields one piece while lz::split yields six (checked with g++ 13.3 -std=c++23: 1 vs 6 pieces); split_single uses a char delimiter and is like-for-like. take_every and cartesian_product iterate uninitialized arrays. Most other rows are at parity, and std::views::stride beats lz::take_every by 1.7x. Results come from a single PNG with no run-to-run variance and no comparison against range-v3. The repo was formerly MarcDirven/cpp-lazy (the lead URL) and now lives at Kaaserne/cpp-lazy. The lead's suggested category (filesystems-and-io) does not fit; this is a ranges/iterator library, filed under the new category ranges-and-views for the orchestrator to remap.

Works in C++11 through C++23 (the std views need C++20/23), so it fills the gap for older standards; lz iterables hold references to non-view inputs (maybe_owned) unless copied; sentinel-based ranges need workarounds before C++17; API differs from std::ranges (lz::filter(...), not views::filter) and the library is far smaller than range-v3.

## Maintenance

Active (last commit 2026-07-06, latest release v9.0.1), MIT-licensed and header-only, so easy to vendor. The speed claims are first-party microbenchmarks on 32 elements, so it is best treated as a C++11-compatible ranges substitute rather than a proven speedup.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** bench/benchmarks-iterators-23.png and the public bench/benchmarks-iterators.cpp (Google Benchmark v1.9.1) compare lz adaptors with std::views on gcc 13.3.0, but bench/CMakeLists.txt sets no build type or optimization flags and no CPU is named, so first-party C.
- **Verifier notes:** All PNG numbers match the record; the split_multiple std baseline does different work (string-literal pattern includes NUL, verified with a 10-line std-only g++ 13.3 check in scratch), so that row is dropped from the claim; the 3.6x filter and 2.6x chunks rows remain the headline. README claim that view creation is excluded is contradicted by the code. Metadata checked: MIT, 365 stars, not a fork, last commit 2026-07-06; category ranges-and-views is new and needs remapping.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** flagged release build with a corrected split benchmark; enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/bench/benchmarks-iterators-23.png>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/README.md>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/bench/benchmarks-iterators.cpp>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/bench/bar_chart_maker.py>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/include/Lz/chunk_if.hpp>
  - <https://github.com/Kaaserne/cpp-lazy>
  - <https://github.com/Kaaserne/cpp-lazy/tree/master/bench>
  - <https://github.com/Kaaserne/cpp-lazy/commits/master.atom>
- **Sources the enricher read:**
  - <https://github.com/Kaaserne/cpp-lazy>
  - <https://github.com/Kaaserne/cpp-lazy/commits/master>
  - <https://github.com/Kaaserne/cpp-lazy/releases>
  - <https://github.com/Kaaserne/cpp-lazy/issues?q=is%3Aissue>
  - <https://github.com/Kaaserne/cpp-lazy/issues/164>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/README.md>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/bench/benchmarks-iterators.cpp>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/bench/bar_chart_maker.py>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/include/Lz/filter.hpp>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/include/Lz/detail/iterators/filter.hpp>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/include/Lz/algorithm/find_if.hpp>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/include/Lz/detail/algorithm/find_if.hpp>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/include/Lz/chunk_if.hpp>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/include/Lz/chunks.hpp>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/include/Lz/detail/iterators/chunks.hpp>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/include/Lz/take_every.hpp>
  - <https://raw.githubusercontent.com/Kaaserne/cpp-lazy/HEAD/tests/chunk_if.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/kaaserne/cpp-lazy`) · [data/wave11/enrich/raw/github_com_kaaserne_cpp_lazy.json](../../../data/wave11/enrich/raw/github_com_kaaserne_cpp_lazy.json) (enrichment confidence 0.75)

</details>
