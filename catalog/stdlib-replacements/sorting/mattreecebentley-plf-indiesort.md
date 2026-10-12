# Indiesort (plf::indiesort)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib` · 🟢 active

> Indirect sort wrapper: sorts indices or pointers, then permutes once; beats std::sort on structs over \~152 bytes.

| | |
|---|---|
| **Beats** | std::sort (also std::list::sort) |
| **Claimed result** | +146% faster than std::sort on vectors or arrays of large structs (496 bytes), on average across all numbers of sorted elements; crossover is any type larger than 152 bytes. +28% faster than std::list's internal sort on types smaller than 272 bytes. |
| **Workload** | Sorting vectors or arrays of large structs (496 bytes) with plf::indiesort, which sorts an index/pointer array and then permutes the elements, versus direct std::sort; also sorting std::list contents versus std::list::sort for types under 272 bytes; averaged across all numbers of sorted elements. |
| **Metric** | throughput |
| **Adoption** | 25 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/mattreecebentley/plf_indiesort) · [benchmark](https://github.com/mattreecebentley/plf_indiesort) |

## Verdict

The README says indiesort averages +146% (about 2.46x) faster than std::sort on vectors or arrays of 496-byte structs and +28% faster than std::list::sort for types under 272 bytes, with crossovers at 152 bytes (vs std::sort) and 272 bytes (vs list::sort); a 2020 announcement quoted +130% on \~480-byte structs. These are first-party averages over unspecified element counts on a Haswell machine with GCC (from a search snippet of the blocked plflib.org pages), with no compiler version, flags or CPU model, and the benchmark code is not in the repo; the test suite's large_struct is exactly 496 bytes on 64-bit, so it probably matches the benchmarked type.

## Use it when

- Sorting a std::vector, std::deque or C array of large structs (well above 152 bytes) where moving an element costs far more than comparing two keys
- Element types that are expensive or non-trivial to move or copy, where one move per element beats std::sort's repeated swaps
- Sorting std::list, std::forward_list, plf::colony/hive or other non-random-access containers of small to medium types (under \~272 bytes) faster than list::sort, or where no member sort exists at all
- Codebases stuck on C++98/03 that still want a generic indirect sort; it is also a ready-made argsort harness for plugging in pdqsort or another sort through the PLF_SORT_FUNCTION macro

## Skip it when

- Arrays of built-in or small types: below 152 bytes it just calls std::sort, so a SIMD or radix sort (vqsort, x86-simd-sort, pdqsort, spreadsort) is the place to look for speed
- When stability matters: the default inner sort is std::sort on indices, so equal elements end in unspecified order (std::list::sort is stable); define PLF_SORT_FUNCTION as std::stable_sort if you need it
- std::list of types larger than \~272 bytes: the author's own figures say list::sort (which only relinks nodes) is faster there, and indiesort does not switch to it automatically
- Memory-tight or allocation-sensitive paths: every non-trivial call heap-allocates N indices (random access) or N pointer+size_t pairs (list path) through std::allocator, ignoring the container's allocator
- Code that holds iterators, references or pointers into a std::list across the sort: indiesort moves values between nodes rather than relinking them, so those handles end up pointing at different values

## How it is fast

It is an indirect sort (argsort) followed by in-place permutation by cycle-following. For random-access ranges it fills an array of the smallest unsigned type that can hold N (unsigned char up to 255 elements, then unsigned short, unsigned int, size_t), sorts those indices with a comparator that dereferences first + index, then walks each permutation cycle so every element is moved about once instead of the O(N log N) moves std::sort makes; with 496-byte elements the move traffic dominates, so cheap index swaps win. For non-random-access ranges it sorts an array of {element pointer, original index} pairs the same way, or, for elements no bigger than two pointers, copies them into a contiguous array, sorts that and copies back.

## Compared with alternatives

Pick indiesort over pdqsort, x86-simd-sort or vqsort when elements are large, opaque structs compared through an arbitrary comparator, or when the container is not random-access; those siblings target built-in keys or contiguous arrays, while indiesort cuts the element-move cost and can wrap pdqsort itself through PLF_SORT_FUNCTION. If the key is a single 32- or 64-bit field and the target is x86, x86-simd-sort's object_qsort (also an argsort, with SIMD) is likely faster.

## Integration

| | |
|---|---|
| **Form** | header-only (plf_indiesort.h plus the shared plf_tools.h and plf_tools_undef.h shipped in the repo); also packaged as vcpkg port plf-indiesort 1.4.10 (depends on plf-tools) and Conan Center plf_indiesort (up to 1.41) |
| **Dependencies** | none outside the standard library; needs the bundled plf_tools.h |
| **Minimum toolchain** | C++98 per the README (C++98/03/11/14/etc-compatible); plf_tools.h enables move semantics and type traits from C++11 and constexpr functions from C++20 (GCC 12+/Clang 15+ with matching libstdc++/libc++, or MSVC 19.29+) |
| **Platforms** | any: portable standard C++, no intrinsics or architecture-specific code in the sort itself |
| **Thread safety** | not documented; it is a stateless function template with no globals, so concurrent calls on disjoint ranges are safe, but the caller must not touch the range during the sort |
| **Drop-in for the baseline** | partial: same (first, last[, comp]) shape as std::sort and identical results up to the order of equal keys, but it allocates a temporary index array and is not a replacement for std::list::sort semantics (unstable, values move between nodes, element type must be move- or copy-assignable) |

## Gotchas

- Not stable by default: ties come out in std::sort's unspecified order. Swapping the inner sort is a compile-time macro (define PLF_SORT_FUNCTION before including the header), so it applies to every indiesort call in that translation unit.
- On std::list it reassigns element values across existing nodes instead of relinking them, unlike list::sort, so outstanding iterators and references now see different values and the element type must be assignable.
- Scratch buffers are raw std::allocator allocations with no RAII: a throwing comparator leaks the index array, and a throwing move during the permutation phase also leaves one element moved-from. In the small-element list path, moved-from temporaries are deallocated without their destructors being run when the type is nothrow-move-assignable but not trivially copy-assignable.
- The 152-byte switch to plain std::sort is a hard-coded constant taken from the author's Haswell + GCC runs; on other CPUs, compilers or element layouts the real crossover may differ, and the repo ships no benchmark code to re-measure it (the test suite only checks sortedness, not that the multiset of elements is preserved).

## Known shortcomings

- Tier C: README figures (+146% vs std::sort on 496-byte structs, crossover 152 bytes; +28% vs std::list::sort under 272 bytes) are first-party with no compiler, flags, CPU, element counts or stdlib named; the repo has no timing code (plf_indiesort_test_suite.cpp has none); the headline was +130% in older releases; the win applies only to element types over 152 bytes. plflib.org blocked (snippet: Haswell with GCC).
- Enricher: no benchmark code in the repo, so the numbers cannot be rerun; the 152-byte switch to plain std::sort is hard-coded from Haswell+GCC runs. Unstable (std::sort on indices). On std::list it moves values between nodes instead of relinking, so iterators see different values (not list::sort semantics). Scratch buffers have no RAII; the small-element list path skips destructors of moved-from temporaries. The test suite checks sortedness only; its large_struct is 496 bytes, matching the README type.

## Caveats and trade-offs

First-party README numbers only. The README gives no compiler, flags, CPU, element counts or standard library; the repo contains no benchmark code (plf_indiesort_test_suite.cpp is a correctness test with no timing). The methodology pages plflib.org/indiesort.htm and plflib.org/benchmarks_haswell_gcc.htm#sort were EGRESS_BLOCKED; a web search snippet (snippet only) says the benchmarks were run on a Haswell machine with GCC (so libstdc++ is likely but unconfirmed; exact CPU model and flags not seen). Older pages quoted '+130% ... vector with 496 byte structs' (and '\~480 bytes'), so the headline figure has moved between releases (README now says +146%). The win only exists for large or non-trivially-movable element types (std::sort is faster below 152 bytes; std::list::sort is faster above 272 bytes), so the average depends on which sizes and element counts the benchmark includes. Extra temporary memory: N \* sizeof(U) for random-access ranges, N \* (sizeof(pointer) + sizeof(size_t)) otherwise.

Header-only, C++98 through C++20 compatible. Temporary memory of N \* (sizeof(pointer) + sizeof(size_t)) for non-random-access ranges and N \* sizeof(U) for random-access ranges (U is the smallest unsigned type able to hold N). Not a win for small types: std::sort is faster on vectors and arrays below 152 bytes, and std::list's own sort is faster for types above 272 bytes. Its main use is letting std::sort-style algorithms run on non-random-access containers.

## Maintenance

Actively maintained by its single author (51 commits, v1.4.10 in July 2026, plf_tools updates through 2026-10-03; both GitHub issues closed), Zlib-licensed and three small headers, so trivial to vendor or pull from vcpkg/Conan; usability is copyable but the speed numbers are first-party only and cannot be rerun from the repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states the +146% (vs std::sort, 496-byte structs, crossover above 152 bytes) and +28% (vs std::list::sort, types under 272 bytes) figures verbatim, but these are first-party averages with no compiler, flags, CPU model or element counts; the repo holds only a correctness test suite (plf_indiesort_test_suite.cpp has no timing code), and the benchmark page on plflib.org is EGRESS_BLOCKED, so the benchmark code and methodology could not be seen.
- **Verifier notes:** Real, active (last commit 2026-10-03), Zlib-licensed (LICENSE.md, OSI-approved), 25 stars, not a fork, not archived; claim matches README exactly. Shortcomings: first-party only, no benchmark code or methodology in the repo, plflib.org methodology blocked (snippet says Haswell + GCC), headline number changed from +130% to +146% across releases, speedup confined to element types larger than 152 bytes.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-60 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/mattreecebentley/plf_indiesort>
  - <https://github.com/mattreecebentley/plf_indiesort/commits>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_indiesort/HEAD/README.md>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_indiesort/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_indiesort/HEAD/plf_indiesort_test_suite.cpp>
- **Sources the enricher read:**
  - <https://github.com/mattreecebentley/plf_indiesort>
  - <https://github.com/mattreecebentley/plf_indiesort/commits>
  - <https://github.com/mattreecebentley/plf_indiesort/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_indiesort/HEAD/README.md>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_indiesort/HEAD/plf_indiesort.h>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_indiesort/HEAD/plf_tools.h>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_indiesort/HEAD/plf_tools_undef.h>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_indiesort/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_indiesort/HEAD/plf_indiesort_test_suite.cpp>
  - <https://raw.githubusercontent.com/conan-io/conan-center-index/master/recipes/plf_indiesort/config.yml>
  - <https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/plf-indiesort/vcpkg.json>
  - https://plflib.org/indiesort.htm (EGRESS_BLOCKED)
  - https://lists.isocpp.org/sg14/2020/06/0406.php (EGRESS_BLOCKED)
  - WebSearch snippet: plf::indiesort benchmark, Haswell GCC (+130% on \~480-byte structs, plflib.org/benchmarks_haswell_gcc.htm#sort)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mattreecebentley/plf_indiesort`) · [data/wave1/enrich/raw/github_com_mattreecebentley_plf_indiesort.json](../../../data/wave1/enrich/raw/github_com_mattreecebentley_plf_indiesort.json) (enrichment confidence 0.75)

</details>
