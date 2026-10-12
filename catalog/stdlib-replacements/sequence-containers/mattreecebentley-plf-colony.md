# plf::colony (plf::hive)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Zlib` · 🟢 active

> Unordered container beating std::vector/deque/list on erase-heavy workloads via O(1) erase that never invalidates other iterators.

| | |
|---|---|
| **Beats** | std::vector, std::deque, std::list |
| **Claimed result** | "three orders of magnitude faster than the vector and deque" at 1% iterate-and-erase with 1024B elements; "the colony in this case is about 361'143 times faster than the vector!" at 50% erasure, largest configuration (verbatim from post). For fill/back-insertion of 8B elements the post says "almost three times slower is the colony" vs vector-with-reserve (32B: "almost the same with less margin"). Linear search: colony "even 50% slower than the list container". |
| **Workload** | Independent microbenchmark suite (fill/back-insertion, linear search, random insert, randomized iterate-and-erase at 1%/50% erasure probability, sort, destruction) across element sizes from 8B to 4096B on GCC/libstdc++. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-4770 @ 3.4GHz, Gentoo Linux |
| **Compiler and flags** | GCC 4.9.4, -std=c++11 -march=native -O2 |
| **Adoption** | 509 stars |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/mattreecebentley/plf_colony) · [benchmark](https://baptiste-wicht.com/posts/2017/05/cpp-containers-benchmark-vector-list-deque-plf-colony.html) |

## Verdict

Third-party benchmark (Baptiste Wicht, 2017) built g++-4.9.4 -std=c++11 -march=native -O2 on an Intel Core i7-4770 @3.4GHz/Gentoo Linux, comparing plf::colony against libstdc++'s std::vector/deque/list across fill, linear-search, random-insert, randomized iterate-and-erase (1%/50% probability), sort and destruction at element sizes 8B-4096B. At 1% erase probability with 1024B elements colony ran about three orders of magnitude faster than vector/deque; at 50% erase probability with 4096B elements colony was about 361,143x faster than vector. The same post reports colony \~3x slower than a reserved vector for plain 8B fill/back-insertion and \~50% slower than list for linear search.

## Use it when

- Randomized insert/erase interleaved with iteration where other code holds pointers/iterators/references to elements that must stay valid across unrelated erasures (game entity/particle pools, object registries).
- Large element sizes (100s of bytes to multi-KB) under heavy erase churn -- the cited benchmark's largest wins (up to \~361,143x vs vector) occur at 4096B elements with 50% random erasure.
- Erase pattern is effectively random-access, not sequential from one end (where deque/list already do fine).
- Concurrent read+insert to different locations is acceptable per the docs (though iterate+write concurrently is not).
- No need for positional indexing or a defined element order.

## Skip it when

- Code relies on operator[] / positional indexing or a stable insertion/iteration order -- colony is explicitly unordered.
- Simple sequential fill / back-insertion of small elements: the cited benchmark measured colony \~3x slower than a reserve()'d std::vector for 8B elements.
- Linear-search-dominated access: colony measured \~50% slower than std::list in the same benchmark.
- Need flat contiguous memory for SIMD/gather-free vectorized access -- colony storage is chunked into blocks, not one array.
- Multithreaded iterate-while-write on the same container: the docs state colony cannot be safely iterated and written to at the same time.

## How it is fast

Elements live in fixed-capacity memory blocks ('groups') allocated contiguously with a parallel 'skipfield' array; erase() marks the slot in the skipfield and threads it onto an intrusive free list instead of shifting or destroying neighboring elements, making erase O(1) per call regardless of position (vs vector/deque's O(n) shift). The skipfield lets ++/-- jump over erased runs without branching, and empty groups are freed so iteration stays bounded. This avoids the copy/move churn that dominates vector's cost under interleaved random erasure.

## Compared with alternatives

Pick colony/hive over plf::list, eastl::vector, fast_vector, or veque specifically when the workload does heavy random-order erasure while other code needs held pointers/iterators to stay valid -- those siblings speed up ordered, indexable, contiguous-or-node storage (growth/allocation/push_back patterns) but don't give colony's O(1) erase-without-invalidation guarantee.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | C++98/03 minimum (per README); move semantics and other modern features activate under C++11+; the plf::hive fork requires C++20+ |
| **Platforms** | any (portable standard C++, no architecture-specific intrinsics); ships an MSVC .natvis debugger visualizer |
| **Thread safety** | Not fully thread-safe. Docs (plflib.org/colony.htm): can be read from and inserted into concurrently at different locations, but cannot be iterated over and written to at the same time. |
| **Drop-in for the baseline** | partial -- explain: STL-container-like API and allocator support, but no operator[], no defined order, and different iterator-invalidation rules, so vector/deque/list call sites require code changes, not just a type alias. |

## Gotchas

- erase(it) invalidates the iterator `it` passed to it (like vector) -- must reassign from erase()'s return value; GitHub issue #57 shows a user hitting this by continuing to use a stale iterator.
- Exception safety is the strong guarantee for all allocating operations except operator=, which only offers the basic guarantee: on exception during assignment the colony ends up empty rather than rolled back.
- clear() has been reported (issue #42) as slower than repeated erase() calls in some cases, which is counterintuitive versus typical container expectations.
- Skipfield element width (8-bit vs 16-bit) is chosen automatically from element size/alignment via the 'priority' template parameter, silently affecting per-block memory overhead.

## Caveats and trade-offs

Benchmark dated 2017 on GCC 4.9.4 (dated compiler); the headline 361,143x figure is specific to a 50%-random-erasure iterate/erase workload on large (multi-KB) elements at whatever container size the author's graph reached, and reflects colony's O(1) erase vs. vector/deque's O(n) erase-and-shift -- an asymptotic-complexity artifact, not a representative 'typical workload' multiplier; for simple sequential fill of small/medium elements the same post reports colony as slower than std::vector. Only libstdc++ (GCC) was exercised in this post, not libc++ or MSVC STL. The library's own site (plflib.org/colony.htm, colony v6.11, GCC 9.2 x64, Intel Xeon E3-1241 Haswell, -O2 -march=native, benchmark source in the colony downloads section) shows qualitatively consistent rankings (colony/list leading insertion and erasure, vector leading iteration) but presents numbers as graph images rather than machine-readable text, so it was used only as corroboration, not the primary citation. The library has since been forked/renamed to plf::hive (github.com/mattreecebentley/plf_hive, 179 stars, also active) to track the pending std::hive standardization proposal (P0447); both repos are maintained in parallel by the same author and the cited benchmark evidence applies to both implementations.

Unordered container: element insertion order is not preserved and elements are not indexable by position like vector's operator[]; higher per-element memory overhead (skip-field metadata) than vector; key advantage is that erase() never invalidates other iterators/pointers/references (unlike vector/deque), which is what makes bulk random erasure O(1) per element instead of O(n).

## Maintenance

Actively maintained (last commit 2026-09-19, days before this review) under the permissive Zlib license, header-only so trivial to vendor into a project; the author now maintains a parallel C++20 fork, plf::hive, tracking the pending std::hive standardization proposal (P0447), so new C++20 codebases may prefer hive while pre-C++20 projects stay on colony.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Third-party post states g++-4.9.4 -std=c++11 -march=native -O2, Intel Core i7-4770 and Gentoo. It links public benchmark code wichtounet/articles src/vector_list_update_1/bench.cpp, which I confirmed exists. It compares plf::colony directly against std::vector/deque/list (libstdc++).
- **Verifier notes:** All quoted figures found verbatim. The \~3x-slower fill figure is for 8B, not 32B, so I fixed it. Metadata matches gh: Zlib, 509 stars, last commit 2026-09-19 (active). plf_hive is a separate repo, 179 stars, not a GitHub fork.
- **Fields the verifier corrected:** `claimed_speedup`
- **Pages the verifier opened:**
  - <https://baptiste-wicht.com/posts/2017/05/cpp-containers-benchmark-vector-list-deque-plf-colony.html>
  - <https://github.com/mattreecebentley/plf_colony>
  - <https://github.com/mattreecebentley/plf_hive>
  - <https://github.com/wichtounet/articles/tree/master/src/vector_list_update_1>
  - <https://plflib.org/colony.htm>
- **Sources the enricher read:**
  - <https://github.com/mattreecebentley/plf_colony>
  - <https://github.com/mattreecebentley/plf_colony/blob/master/README.md>
  - <https://github.com/mattreecebentley/plf_colony/blob/master/plf_colony.h>
  - <https://github.com/mattreecebentley/plf_colony/issues>
  - <https://github.com/mattreecebentley/plf_colony/issues/57>
  - <https://github.com/mattreecebentley/plf_hive>
  - <https://plflib.org/colony.htm>
  - <https://baptiste-wicht.com/posts/2017/05/cpp-containers-benchmark-vector-list-deque-plf-colony.html>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mattreecebentley/plf_colony`) · [data/wave1/enrich/raw/github_com_mattreecebentley_plf_colony.json](../../../data/wave1/enrich/raw/github_com_mattreecebentley_plf_colony.json) (enrichment confidence 0.82)

</details>
