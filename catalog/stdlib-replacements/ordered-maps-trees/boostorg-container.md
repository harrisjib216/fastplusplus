# boost::container::flat_set / flat_map

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Ordered maps and trees](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Vector-backed sorted set/map beating std::set on insert+remove at small sizes, up to \~256 elements.

| | |
|---|---|
| **Beats** | std::set |
| **Claimed result** | flat_set \~1.1-2.5x faster than std::set for insert+remove at sizes 2-128 (largest gain at smallest size); crossover between size 128 and 256; std::set \~13.4x faster than flat_set at size 8192 |
| **Workload** | 500,000 randomized insert+remove operations on sets of size 2 to 8192 32-bit-ish elements, comparing vector-backed boost::container::flat_set against red-black-tree std::set |
| **Metric** | throughput |
| **Compiler and flags** | -O3 (hardware and full compiler version not stated) |
| **Adoption** | 127 stars on the split boostorg/container mirror; ships as part of Boost and is used extremely widely across C++ codebases |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/boostorg/container) · [benchmark](https://blog.fellstat.com/?p=376) |

## Verdict

A single-author 2014 blog benchmark (500,000 random insert-then-erase operations on int keys, -O3, compiler and hardware unstated) timed boost::container::flat_set against std::set across sizes 2-8192: flat_set was \~2.5x faster at size 2, \~1.1x faster at 128, then lost ground from 256 elements up, with std::set \~13.4x faster at 8192.

## Use it when

- Sets/maps that stay small (roughly &lt;=128-256 elements per container), even if there are many such containers
- Read-mostly or lookup-heavy workloads where iteration/cache locality matters more than mutation cost
- Cheap-to-move key types (ints, small PODs) where shifting on insert/erase is cheap
- Existing std::set/std::map code that can tolerate iterator/reference invalidation on mutation
- Memory-constrained code avoiding the per-node allocation overhead of tree containers

## Skip it when

- Large sets/maps (thousands+ elements) mutated frequently -- std::set was \~13.4x faster than flat_set at 8192 elements in the cited benchmark
- Code relying on iterator/reference/pointer stability across insert/erase -- flat containers invalidate on shift/reallocation
- Bulk one-at-a-time insertion of very large unsorted datasets -- GitHub issue #154 reports near-hang (100% CPU) inserting \~9M elements individually into flat_map
- Workloads needing guaranteed O(log n) worst-case insert/erase (latency-bounded mutation)
- Large or expensive-to-move key/value types, since every insert/erase move-shifts surrounding elements

## How it is fast

Core technique is cache-friendly linear storage: a sorted vector-like sequence (default plain vector, or a user-supplied vector-like container) gives contiguous memory and random-access iterators, avoiding the pointer-chasing and per-node allocation of a red-black tree. For small containers this locality and lack of per-element allocation outweighs the O(n) shifting cost of insert/erase; std::set's balanced-tree structure only pays off once n is large enough that O(log n) tree operations beat O(n) vector shifts (crossover around 128-256 elements per the cited benchmark).

## Compared with alternatives

Pick flat_set/flat_map over fast-containers, S+ tree, or tlx::btree when the working set stays small (roughly &lt;=128-256 elements) and you want a true drop-in std::set/map replacement shipped with Boost and no extra dependency; the sibling B-tree/B+tree structures target much larger n (up to 10M-scale) and win precisely in the size range where flat_set has already crossed over to being slower than std::set.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Boost.Config, Boost.Move, Boost.Intrusive (ships as part of Boost; no separately compiled library) |
| **Minimum toolchain** | C++03 baseline (README states C++03 support); has conditional code paths for C++11 features like initializer_list and variadic templates when available |
| **Platforms** | any (portable C++, no architecture-specific code observed) |
| **Thread safety** | not documented -- no built-in synchronization; same external-synchronization requirement as std::set/std::map |
| **Drop-in for the baseline** | partial — explain: same associative-container API/semantics as std::set/std::map, but different iterator/reference invalidation rules and iterator category (random-access vs. bidirectional), so algorithmic code ports directly while code depending on node stability does not |

## Gotchas

- Insert/erase invalidate iterators and references to elements after the mutation point (vector shift/reallocation), unlike std::set's per-node stability
- Underlying sequence container is swappable (e.g. stable_vector, static_vector, small_vector) -- use stable_vector for reference stability at the cost of contiguity
- One-at-a-time insertion of large unsorted data can effectively hang (see issue #154); prefer bulk/sorted-range construction to amortize shifting
- Provides random-access iterators, so generic code that dispatches on iterator category behaves differently than with std::set's bidirectional iterators

## Caveats and trade-offs

Benchmark is a single-author 2014 blog post (not the boost repo's own benchmark suite), hardware unspecified, single-run numbers with no error bars, and only covers int-like keys with a 500K insert+remove mix; the performance advantage clearly reverses for larger sets (\~8K elements) in the same data

Vector-backed storage means O(n) insert/erase in the middle versus O(log n) for std::set; no pointer/iterator stability across insert/erase; best suited to small/medium or read-mostly sets, not large frequently-mutated ones

## Maintenance

Actively maintained as a core part of Boost (repo shows a commit dated 2026-09-23) and BSL-1.0 licensed, so it is freely copyable/redistributable with no licensing friction.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** A 2014 single-author blog post gives a timing table for boost::container::flat_set vs std::set, with Rcpp benchmark code inline and -O3 stated. The compiler, its version, the hardware and the Boost version (via the R BH package) are not stated, so it is not A, and it is neither peer-reviewed nor a third-party suite.
- **Verifier notes:** The table matches the claim. flat_set is 2.51x faster at size 2, \~1.10x at 128, and slower from 256 up, with std::set \~13.4x faster at 8192. The loop is 500,000 random inserts, each followed by an erase only if the insert succeeded, timed with std::clock. Metadata checked: BSL-1.0, 127 stars, last commit 2026-09-23 (active).
- **Pages the verifier opened:**
  - <https://blog.fellstat.com/?p=376>
  - <https://github.com/boostorg/container>
- **Sources the enricher read:**
  - <https://github.com/boostorg/container>
  - <https://github.com/boostorg/container/blob/master/include/boost/container/flat_set.hpp>
  - <https://github.com/boostorg/container/issues/154>
  - <https://blog.fellstat.com/?p=376>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/boostorg/container`) · [data/wave1/enrich/raw/github_com_boostorg_container.json](../../../data/wave1/enrich/raw/github_com_boostorg_container.json) (enrichment confidence 0.6)

</details>
