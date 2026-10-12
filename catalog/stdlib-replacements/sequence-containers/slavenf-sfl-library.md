# sfl-library small and static containers (sfl::small_vector, sfl::static_vector, sfl::small_flat_map)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Zlib` · 🟢 active

> Header-only C++11 small_vector, static_vector and small_flat_map that avoid heap allocation for up to N elements; no benchmark numbers.

| | |
|---|---|
| **Beats** | std::vector |
| **Claimed result** | No numbers. README and doc pages describe small_vector as a vector that "embeds small statically allocated storage internally to avoid dynamic memory allocation" and static_vector as backed entirely by static storage "cache-friendly"; the only comparative wording is qualitative (devector "faster insertion and deletion at the front" than vector; segmented_devector "a superior alternative to std::deque"). |
| **Workload** | No published measurement for small_vector, static_vector or small_flat_map; the repo's benchmark/ folder holds benchmark sources for other components only. |
| **Metric** | throughput |
| **Compiler and flags** | Benchmark makefile (not tied to published results): g++ -std=c++20 -O3 -DNDEBUG |
| **Adoption** | 164 stars; packaged in FreeBSD ports (devel/sfl-library) and the AUR (sfl-git) per search snippets (not opened) |
| **Last commit** | 2026-03-16 |
| **Links** | [repository](https://github.com/slavenf/sfl-library) |

## Verdict

Nothing was measured: the README and doc pages only call these containers 'compact and cache-friendly' and say small_vector avoids dynamic allocation for up to N elements; the repo's benchmark folder (g++ -std=c++20 -O3 -DNDEBUG makefile) times segmented_devector against std::deque and boost::container::deque and the hash maps against std::unordered_map, publishes no results, and has no harness for small_vector, static_vector or small_flat_map.

## Use it when

- Many short-lived vectors whose size is usually below a known bound (e.g. per-node child lists, argument lists, small result sets) where std::vector's first allocation dominates.
- Bare-metal or allocation-free code paths that need a std::vector-shaped container with a fixed compile-time capacity (static_vector, also usable in C++20 constant expressions).
- Small sorted maps (tens of keys) where a contiguous sorted array beats std::map's node allocations, and you want the inline-buffer variant of flat_map.
- Codebases stuck on old toolchains: the library is tested down to GCC 4.8.5 and Clang 3.4.2 in C++11 mode, and supports stateful allocators and fancy pointers.
- Teams that want one consistent family of small/static/flat containers from a single header-only, zlib-licensed project rather than mixing Boost, Abseil and LLVM types.

## Skip it when

- When you need evidence that it is faster: the project publishes no numbers for small_vector, static_vector or small_flat_map, and nothing compares it with boost::container::small_vector, absl::InlinedVector or llvm::SmallVector.
- Memory-tight objects: the header layout gives 24 bytes of pointer overhead on 64-bit targets on top of N\*sizeof(T) (derived from the header layout), where ankerl::svector and absl::InlinedVector document 8 bytes.
- Large or frequently moved inline contents: moving or swapping a small_vector whose elements are inline moves element by element (documented as linear in N in the worst case), unlike std::vector's constant-time pointer swap.
- Release builds that rely on capacity checks: static_vector overflow is only an assert (SFL_ASSERT is plain assert), so with NDEBUG an extra push_back writes past the inline array.
- Constant-evaluated code using the small_\* containers: the README says only non-small_\* containers work in C++20 constant expressions.

## How it is fast

The speed argument is allocation avoidance, not a new algorithm: small_vector holds three pointers (first, last, end of storage) plus a union of N elements, and the begin pointer always points at the live buffer, so element access and push_back are the same pointer arithmetic as std::vector with no inline-or-heap branch; growth is 1.5x and never drops below N. static_vector removes the allocator entirely (capacity is a compile-time constant and push_back only asserts it is not full). small_flat_map does a binary search (O(log n) lookup, O(n) insert/erase) over contiguous pairs, which is cache-friendly for small maps compared with node-based std::map.

## Compared with alternatives

Pick sfl when you want a standards-conforming, allocator-aware family (small_vector plus static, flat and linear-map variants) that builds on C++11 compilers and fancy pointers; pick ankerl::svector when you need published speedups and minimal 8-byte overhead, and ETL when you need a whole embedded, allocation-free container suite rather than just these types.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only); benchmarks additionally need Boost |
| **Minimum toolchain** | C++11; tested GCC 4.8.5, Clang 3.4.2, GCC 7.3.1, Clang 5.0.1, GCC 15.2.1, Clang 22.1.1, MSVC 19.44 (C++14 and later); CMake 3.15+ for the INTERFACE target |
| **Platforms** | any with a conforming compiler (tested on CentOS 7 and Arch Linux x86-64 and MSVC; a 32-bit build problem, issue #29, was fixed in October 2025) |
| **Thread safety** | not documented; no internal synchronization in the headers, so the usual std container rules apply by convention |
| **Drop-in for the baseline** | partial — std::vector-compatible member set (plus nth/index_of) with an extra capacity template parameter; moved-from objects are not guaranteed empty, static_vector has no allocator and UB on overflow, and small_flat_map's value_type is std::pair&lt;Key, T&gt; rather than std::pair&lt;const Key, T&gt; |

## Gotchas

- A moved-from small_vector may still hold its elements (documented 'valid but unspecified'); issue #3 (Dec 2023) was a user test asserting v1.size() == 0 after a move, closed by the maintainer as intended behavior. That reporter also said sfl::small_vector crashed in their program and switched to absl::InlinedVector, with no reproducer posted.
- small_flat_map exposes std::pair&lt;Key, T&gt; with a non-const key through its iterators; modifying a key in place silently breaks the sort order the binary search relies on.
- The record's 'many are constexpr in C++20' does not cover these entries' small_\* types: the README states small_\* containers are not usable in constant expressions; static_vector is, but on GCC you cannot declare a constexpr static_vector object and data() is not constexpr.
- Benchmark harness (for other containers, not these three): benchmark/src/small_unordered_map.cpp and segmented_devector.cpp call std::mt19937 inside the timed loop for every element, and with 2-16 elements each sample is a single steady_clock interval; no results are checked in, so there is nothing to verify for small_vector, static_vector or small_flat_map.

## Known shortcomings

- No benchmark for small_vector, static_vector or small_flat_map; the repo's benchmarks cover only unordered_map and segmented_devector with unpublished results; 164 stars. Whole-stdlib decomposition seed kept at D for completeness.
- Enricher: no numbers for small_vector, static_vector or small_flat_map (the repo's bench sources cover other containers and time mt19937 inside the loop); 24-byte pointer overhead (derived from the header); moved-from vectors are not guaranteed empty (#3); static_vector overflow is checked only by assert; README excludes small_\* from constexpr use.

## Caveats and trade-offs

Tier D: no numeric comparison found. benchmark/src has unordered_map.cpp (sfl::unordered_map vs std::unordered_map vs boost::unordered_map), small_unordered_map.cpp (sfl small/linear maps vs std::unordered_map) and segmented_devector.cpp (vs std::deque and boost::container::deque, 10'000'000 integers, 20 iterations, times sorted for a median), built by benchmark/makefile with g++ -std=c++20 -O3 -DNDEBUG; none cover small_vector, static_vector or small_flat_map and no results are published in the repo (commit 'Reworked benchmarks' 2026-03-10). boost::container::small_vector and absl::InlinedVector are not benchmarked at all; a web search found no third-party numbers. 164 stars is below the usual notability bar for tier D. If benchmark results get published, unordered_map or segmented_devector would be the better-documented components.

Header-only C++11; small_vector keeps N elements inline then falls back to heap; static_vector never allocates and exceeding N is undefined behavior; containers support stateful and fancy-pointer allocators and many are constexpr in C++20. Interface follows std::vector, not a boost::container::small_vector drop-in.

## Maintenance

Actively maintained by a single author (886 commits, last on 2026-03-16 after a benchmark rework on 2026-03-10), zlib-licensed and header-only, so it is easy to vendor; tests are run under Valgrind, but treat its performance as unmeasured.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** No published numbers: README and doc/small_vector.md, doc/static_vector.md, doc/small_flat_map.md only describe the containers as "compact and cache-friendly"; benchmark/src holds only segmented_devector.cpp, small_unordered_map.cpp and unordered_map.cpp, none covering small_vector, static_vector or small_flat_map, and no results are checked in.
- **Verifier notes:** Record accurate (164 stars, Zlib, last commit 2026-03-16, benchmark folder contents as described). Keep at D with shortcomings: no numbers for the listed containers, qualitative cache-friendly wording only, low notability (164 stars, but distro-packaged).
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-71 (wave 1, stdlib decomposition); enricher (wave 1 stdlib seeds, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/slavenf/sfl-library>
  - <https://github.com/slavenf/sfl-library/commits/master>
  - <https://github.com/slavenf/sfl-library/tree/master/benchmark>
  - <https://github.com/slavenf/sfl-library/tree/master/benchmark/src>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/benchmark/makefile>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/README.md>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/doc/small_vector.md>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/doc/static_vector.md>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/doc/small_flat_map.md>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/benchmark/src/segmented_devector.cpp>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/benchmark/src/unordered_map.cpp>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/benchmark/src/small_unordered_map.cpp>
- **Sources the enricher read:**
  - <https://github.com/slavenf/sfl-library>
  - <https://github.com/slavenf/sfl-library/commits/master>
  - <https://github.com/slavenf/sfl-library/issues?q=is%3Aissue>
  - <https://github.com/slavenf/sfl-library/issues/1>
  - <https://github.com/slavenf/sfl-library/issues/3>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/README.md>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/doc/small_vector.md>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/doc/static_vector.md>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/doc/small_flat_map.md>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/include/sfl/small_vector.hpp>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/include/sfl/static_vector.hpp>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/include/sfl/small_flat_map.hpp>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/include/sfl/detail/cpp.hpp>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/include/sfl/private.hpp>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/benchmark/makefile>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/benchmark/src/small_unordered_map.cpp>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/benchmark/src/segmented_devector.cpp>
  - <https://raw.githubusercontent.com/slavenf/sfl-library/HEAD/benchmark/src/unordered_map.cpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/slavenf/sfl-library`) · [data/wave1/enrich/raw/github_com_slavenf_sfl_library.json](../../../data/wave1/enrich/raw/github_com_slavenf_sfl_library.json) (enrichment confidence 0.75)

</details>
