# Boost.Algorithm Boyer-Moore / Boyer-Moore-Horspool searchers

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [String search and hashing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only Boyer-Moore / Boyer-Moore-Horspool string searchers, \~4-5x faster than std::search on long patterns.

| | |
|---|---|
| **Beats** | std::search |
| **Claimed result** | std::search: 0.4848s (100%, baseline) vs boyer_moore_search: 0.1171s (24.16%) vs boyer_moore_horspool_search: 0.1076s (22.2%) for a 105-char pattern found mid-corpus -- i.e. boyer_moore \~4.1x faster, boyer_moore_horspool \~4.5x faster than std::search (derived from page data; percentages are verbatim from the PR). A second case (91-char 'not found' pattern) shows std::search 1.028s vs boyer_moore_horspool 0.1825s (\~5.6x, derived from page data). |
| **Workload** | Search a 2,756,252-entry random 8-bit corpus for a 105-entry pattern (middle), a 43-entry pattern (end) and a 91-entry pattern (not found), using boost::algorithm::boyer_moore_search / boyer_moore_horspool_search vs std::search, via Boost.Algorithm's test/search_test2.cpp. |
| **Metric** | throughput |
| **Adoption** | 131 stars; boyer_moore_search/boyer_moore_horspool_search ship in mainline Boost.Algorithm and are used wherever Boost is deployed |
| **Last commit** | 2026-08-05 |
| **Links** | [repository](https://github.com/boostorg/algorithm) · [benchmark](https://github.com/boostorg/algorithm/pull/25) |

## Verdict

PR #25 (opened 2016 by Jeremy Murphy, still open/unmerged) republishes edited test/search_test2.cpp output on a 2,756,252-entry random 8-bit corpus: std::search 0.4848s vs boyer_moore_search 0.1171s (\~4.1x) and boyer_moore_horspool_search 0.1076s (\~4.5x) for a 105-entry pattern found mid-corpus, and std::search 1.028s vs boyer_moore_horspool_search 0.1825s (\~5.6x) for a 91-entry not-found pattern; compiler, flags, CPU model, and standard library are not stated, and the PR author notes \~5-10% run-to-run variance.

## Use it when

- Long patterns (tens to hundreds of elements) searched against large corpora, the shape of the PR's benchmark (105/43/91-entry patterns over a 2.76M-entry corpus)
- The same pattern is searched repeatedly against many or large corpora: construct a boyer_moore/boyer_moore_horspool object once and reuse operator() to amortize the skip-table build
- Pre-C++17 toolchains, or any C++03/11/14 codebase that can take a Boost dependency but can't use std::boyer_moore_searcher
- Searching over random-access ranges of non-char element types with comparable (and ideally hashable) values, not just byte strings

## Skip it when

- Short, one-off pattern searches — the skip-table build can cost more than a plain linear scan for a single small search
- C++17+ code already reaching for std::boyer_moore_searcher/std::boyer_moore_horspool_searcher, which is the same algorithm with no Boost dependency
- Forward-only or input iterators — both searchers require random-access iterators, unlike std::search
- Mixed-type pattern/corpus comparisons — a BOOST_STATIC_ASSERT requires identical value_type on both iterators
- Workloads wanting SIMD-level throughput on x86/ARM byte strings — this is a scalar algorithm; StringZilla or sse4-strstr target that instead

## How it is fast

Both algorithms precompute a bad-character skip table from the pattern (full Boyer-Moore adds a good-suffix table) so on a mismatch the search can jump ahead by more than one position instead of std::search's linear rescan. The skip table is a fixed-size array (O(2^CHAR_BIT) entries) for small numeric value types like unsigned char, or a boost::unordered_map/std::unordered_map otherwise, giving O(pattern length + alphabet size) preprocessing. Horspool drops the good-suffix table for cheaper preprocessing at the cost of slightly weaker worst-case skips.

## Compared with alternatives

Pick this over sse4-strstr or StringZilla when the workload needs a portable, non-SIMD, header-only implementation that works over arbitrary random-access element types (not just bytes) or that reuses a prebuilt search object across many corpora; pick StringZilla or sse4-strstr instead when the goal is maximum single-call byte-string throughput on x86/ARM via SIMD.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Boost.Config, Boost.Assert, Boost.StaticAssert, Boost.Range, Boost.Core, Boost.TypeTraits, Boost.Array, and Boost.Unordered (all header-only Boost libraries; part of full Boost distributions) |
| **Minimum toolchain** | C++03 (README lists 'Properties: C++03, Header-only'; falls back to boost::unordered_map when BOOST_NO_CXX11_HDR_UNORDERED_MAP is defined, std::unordered_map otherwise) |
| **Platforms** | any (portable C++, no SIMD or architecture-specific code observed in the headers read) |
| **Thread safety** | not documented; operator() on the boyer_moore/boyer_moore_horspool functor classes is const and the skip tables are built once in the constructor, but the library makes no explicit thread-safety guarantee |
| **Drop-in for the baseline** | partial — explain: the free-function form takes corpus/pattern iterator pairs in the same order as std::search, but returns a std::pair&lt;iterator,iterator&gt; (match start and end) instead of std::search's single iterator, and requires random-access iterators where std::search accepts forward iterators |

## Gotchas

- Random-access iterators are required for both corpus and pattern; forward/input iterators that std::search accepts will not compile
- Pattern and corpus iterators must share the same value_type, enforced at compile time via BOOST_STATIC_ASSERT
- Non-numeric or wide value types fall back to an unordered_map-based skip table, which is slower to build and probe than the fixed array table used for byte-like data
- The much larger Musser-Nishanov searcher proposed in the same PR #25 (still open/unmerged) had a reported segfault on large real-world corpora during development; that bug is in the unmerged code, not the mainline boyer_moore/boyer_moore_horspool searchers this benchmark measures

## Caveats and trade-offs

The quoted numbers come from PR #25, opened in 2016 by contributor Jeremy Murphy (jeremy-murphy), not Marshall Clow. The PR proposes a Musser-Nishanov searcher and is still open and unmerged. The timing rows used here are for the already-mainline boyer_moore/boyer_moore_horspool searchers. Compiler, flags, CPU model and standard library are not stated, and the author warns of 5-10% run-to-run variance, so treat the \~4-5x figures as indicative. The baseline is plain std::search; since C++17 the standard also ships std::boyer_moore_searcher and std::boyer_moore_horspool_searcher (derived from these Boost searchers), which this PR does not compare against.

Boyer-Moore/Horspool searchers build an O(alphabet + pattern) skip table before searching, which pays off when reused or on longer patterns but adds overhead for a single tiny one-off search; since C++17 the same two algorithms are also standardized as std::boyer_moore_searcher / std::boyer_moore_horspool_searcher, usable directly with std::search -- so on a C++17+ toolchain the standard library itself can close most of this gap without Boost.

## Maintenance

Actively maintained mainline Boost.Algorithm code (develop branch last commit 2026-08-05), BSL-1.0 licensed and header-only, trivial to vendor a single header pair; the PR these benchmark numbers come from has sat open and unmerged since 2016 and proposes a different, unrelated Musser-Nishanov searcher.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** PR #25 shows edited search_test2 output (the benchmark code test/search_test2.cpp is in the mainline repo) timing std::search against boyer_moore_search and boyer_moore_horspool_search. It gives no compiler, flags, CPU or standard library, so the tier is C.
- **Verifier notes:** The numbers match the PR exactly (4.1x/4.5x middle, 5.6x not-found). The caveat misattributed the PR to Marshall Clow; its author is jeremy-murphy. last_commit on the default branch (develop) is 2026-08-05; 2026-08-12 is the repo pushed_at, not a default-branch commit. BSL-1.0, 131 stars and active status are all accurate.
- **Fields the verifier corrected:** `caveats`, `workload`, `last_commit`
- **Pages the verifier opened:**
  - <https://github.com/boostorg/algorithm>
  - <https://github.com/boostorg/algorithm/pull/25>
  - <https://github.com/boostorg/algorithm/tree/develop/test>
- **Sources the enricher read:**
  - <https://github.com/boostorg/algorithm>
  - <https://github.com/boostorg/algorithm/pull/25>
  - <https://github.com/boostorg/algorithm/tree/develop/test>
  - <https://github.com/boostorg/algorithm/blob/develop/include/boost/algorithm/searching/boyer_moore.hpp>
  - <https://github.com/boostorg/algorithm/blob/develop/include/boost/algorithm/searching/boyer_moore_horspool.hpp>
  - <https://github.com/boostorg/algorithm/blob/develop/include/boost/algorithm/searching/detail/bm_traits.hpp>
  - <https://github.com/boostorg/algorithm/blob/develop/test/search_test2.cpp>
  - <https://github.com/boostorg/algorithm/issues?q=boyer_moore>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/boostorg/algorithm`) · [data/wave1/enrich/raw/github_com_boostorg_algorithm.json](../../../data/wave1/enrich/raw/github_com_boostorg_algorithm.json) (enrichment confidence 0.6)

</details>
