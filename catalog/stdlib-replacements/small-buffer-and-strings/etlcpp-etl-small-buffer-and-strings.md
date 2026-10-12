# ETL fixed-capacity strings and algorithms (etl::string, etl::algorithm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Heap-free fixed-capacity strings (etl::string&lt;N&gt;) and STL-style algorithms for embedded C++03+; no speed claim versus std::string or std::sort.

| | |
|---|---|
| **Beats** | std::string |
| **Claimed result** | None stated. The docs describe etl::string as a fixed-capacity string with a truncation flag and etl::algorithm as STL-style algorithm implementations, with no speed claim. |
| **Workload** | No published measurement for strings or for the algorithm and sort functions; nothing was found in the README, docs/strings, docs/utilities or the test tree. |
| **Metric** | other |
| **Adoption** | 3.1k stars, 549 forks |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/ETLCPP/etl) |

## Verdict

Nothing was measured: no numbers for etl::string versus std::string or etl::sort versus std::sort exist in the README, docs (strings, utilities/algorithms, blog), test tree or issue tracker; the only ETL timing (GitHub issue #13, Dec 2016, VS2015 /O2) covers unordered_map, not strings or algorithms. Code reading shows no speed technique beyond avoiding the heap, and the no-STL sort path is quadratic.

## Use it when

- Firmware or RTOS code that bans heap allocation but wants a std::string-like API (append, find, replace, compare) with a hard length bound.
- Fixed-format text such as protocol fields, log lines or display buffers whose maximum length is known and where silent or flagged truncation is acceptable.
- Strings that must live in static storage, shared memory or a memcpy'd struct (repair() fixes the internal pointer after a raw copy; \*_ext strings wrap an existing char buffer).
- C++03 toolchains without &lt;algorithm&gt;, where etl::heap_sort, etl::lower_bound and friends stand in for the missing STL.

## Skip it when

- Throughput-oriented string processing: substring find is a naive nested loop and compare is char-by-char, so expect no win and possibly a loss against std::string's library-optimised search and comparison.
- Strings with no sensible upper bound, or many mostly-short strings with a large N: every etl::string&lt;N&gt; occupies N+1 chars plus a buffer pointer, size, capacity and a flag byte regardless of content.
- Code that relies on cheap moves: etl::string has no move constructor, so moving or returning one without copy elision copies size() characters, unlike std::string's pointer steal for heap strings.
- Sorting more than a few thousand elements with ETL_NO_STL defined: etl::sort becomes etl::shell_sort, whose inner loop never exits early, so it does about n^2 comparisons for every input (98,176,009 for n=10,000, counted from the loop bounds), even on already sorted data.

## How it is fast

No speed technique: the only performance property is that construction, copy and append never call malloc, so long strings cost no allocator call and latency is bounded by N. Bulk copies of pointer ranges use memmove and C-string length uses ::strlen, but compare() is a character loop and find() of a substring is the naive O(n\*m) etl::search (no memchr/memcmp). With the STL enabled, etl::sort and etl::stable_sort simply call std::sort and std::stable_sort; with ETL_NO_STL they fall back to etl::shell_sort and etl::insertion_sort.

## Compared with alternatives

Pick etl::string over EASTL fixed_string or Coost fastring when you need a strictly heap-free string with a truncation flag on a C++03 or no-STL embedded toolchain; pick EASTL's string (published std::string ratios), FastString or MengRao/str when the goal is measured speed over std::string, and to_static_string when you only need allocation-free number formatting.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (uses the STL if present unless ETL_NO_STL is defined; ::strlen/::wcslen from the C library) |
| **Minimum toolchain** | C++03 (C++98 badge); CI on GCC and Clang for C++11 through C++26 and MSVC; README says tested with VS2022, GCC 12, Clang 14 |
| **Platforms** | any (bare metal, RTOS, desktop); Arduino, Zephyr, PlatformIO and Conan packages exist |
| **Thread safety** | not documented; no internal synchronisation in the string code read |
| **Drop-in for the baseline** | partial: member functions mirror std::basic_string, but etl::string&lt;N&gt; is a different type with a capacity template parameter and truncates instead of growing |

## Gotchas

- Truncation is silent by default: text past capacity is dropped and only the truncated() flag records it; an error is raised only if ETL_STRING_TRUNCATION_IS_ERROR (or ETL_ENABLE_ERROR_ON_STRING_TRUNCATION) is defined, and a string assigned from a truncated string inherits the flag even when it fits.
- etl::shell_sort (used by etl::sort under ETL_NO_STL, the configuration the README and setup page profiles show) uses Shell's n/2 gap sequence with no early break in the inner loop, so it is Theta(n^2) on every input; use etl::heap_sort (since 16.2.0) for larger ranges. etl::stable_sort under ETL_NO_STL is upper_bound+rotate insertion sort, O(n^2) element moves.
- etl::find and etl::search are always ETL's own loops, even when the STL is available; only sort and stable_sort forward to std.
- The secure-clear feature is compiled in by default (ETL_DISABLE_STRING_CLEAR_AFTER_USE removes it): once set_secure() marks a string, it zeroes all unused capacity after every modification, an O(N) cost per edit.

## Known shortcomings

- No numbers and no speed claim (README has a cache-design line only); kept at D as a whole-stdlib decomposition seed.
- Enricher: no numbers anywhere; etl::shell_sort (which is etl::sort under ETL_NO_STL) has no early break, so about n^2 comparisons on every input (98,176,009 for n=10,000, sorted input too); naive O(n\*m) substring find, char-loop compare, no move constructor, silent truncation by default.

## Caveats and trade-offs

Tier D: no numbers anywhere, and no sign that the author claims a speed win over std::string or std::sort; the value is heap-free, fixed-capacity strings with predictable latency. The README's only performance-related line is a design statement ('Cache Efficiency: Containers use contiguous memory layouts for optimal cache performance'), not a comparison. docs/utilities/algorithms.md lists the functions and says nothing about speed, and docs/blog has no performance post. Kept as a placeholder record in case a user benchmark appears; the container record for the same repo has the only existing timing harness (test/Performance/unordered_map, no results). Three WebSearch queries for independent etl::string or ETL timings found nothing.

etl::string&lt;N&gt; keeps N characters in the object with no heap; text that would exceed capacity is truncated and an internal truncated flag is set (or an error is asserted if ETL_STRING_TRUNCATION_IS_ERROR is defined). It is a distinct type from std::string, and the algorithm functions exist mainly so that code can run without the STL header set (C++03 backports and extra helpers).

## Maintenance

Actively maintained (v20.49.0, last commit 2026-10-04, 3.1k stars) MIT header-only library, copyable; useful for heap-free determinism, not for speed, and this record stays a tier D placeholder with a documented quadratic etl::shell_sort under ETL_NO_STL.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** No benchmark_url and no numbers anywhere: the README has only a design statement ('Containers use contiguous memory layouts for optimal cache performance'), the docs tree (strings, utilities, blog) has no timing, and test/Performance holds only an unordered_map harness without results.
- **Verifier notes:** Kept at tier D rather than rejected: notable (3.1k stars, 549 forks) and the keep-and-document rule applies. Shortcoming to record: no speed claim or measurement against std::string or std::sort exists. Metadata checked on github.com: MIT, last commit 2026-10-04, not archived, not a fork.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-74 (wave 1, stdlib decomposition); enricher (wave 1 stdlib seeds, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ETLCPP/etl>
  - <https://github.com/ETLCPP/etl/commits/master>
  - <https://github.com/ETLCPP/etl/tree/master/test/Performance>
  - <https://github.com/ETLCPP/etl/tree/master/docs>
  - <https://github.com/ETLCPP/etl/tree/master/docs/blog>
- **Sources the enricher read:**
  - <https://github.com/ETLCPP/etl>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/README.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/basic_string.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/string.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/algorithm.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/platform.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/error_handler.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/version.txt>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/library.json>
  - <https://github.com/ETLCPP/etl/tree/master/docs>
  - <https://github.com/ETLCPP/etl/tree/master/docs/strings>
  - <https://github.com/ETLCPP/etl/tree/master/docs/getting-started>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/strings/string.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/strings/_index.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/utilities/algorithms.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/getting-started/macros.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/getting-started/setup.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/getting-started/no-stl.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/getting-started/compilers.md>
  - <https://github.com/ETLCPP/etl/issues?q=is%3Aissue+sort>
  - <https://github.com/ETLCPP/etl/issues?q=is%3Aissue+performance>
  - <https://github.com/ETLCPP/etl/issues/13>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/etlcpp/etl#small-buffer-and-strings`) · [data/wave1/enrich/raw/github_com_etlcpp_etl_small_buffer_and_strings.json](../../../data/wave1/enrich/raw/github_com_etlcpp_etl_small_buffer_and_strings.json) (enrichment confidence 0.8)

</details>
