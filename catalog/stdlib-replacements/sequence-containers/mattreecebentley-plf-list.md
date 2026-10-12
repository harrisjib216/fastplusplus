# plf::list

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Zlib` · 🟢 active

> Node-clustering drop-in replacement for std::list; faster insertion, erasure, sort, and much faster clear/destruction.

| | |
|---|---|
| **Beats** | std::list |
| **Claimed result** | On the benchmark page: insertion 333% faster on average (raw tests across char/int/double/small-struct/large-struct); sort 77% faster than std::list's internal sort (average of all tests); reverse 70% faster; remove/remove_if 91% faster; unique 63% faster; clear() 1,147,900% faster on average for trivially-destructible small structs (811% for non-trivially-destructible); destruction 6,350% faster (1,248% for non-trivially-destructible); about 25% faster than std::list in ordered low- and high-modification 'real-world' scenario tests. For erasure the page gives no percentage, only 'best erasure performance until very large amounts of memory are involved'. |
| **Workload** | Raw insertion/erasure/iteration tests across char, int, double, small struct and large struct (490-byte) element types; list-specific tests (sort, reverse, remove/remove_if, unique, clear, destruction) and ordered 'real-world' modification scenarios using small structs only; project's own plf benchmark suite |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E3-1241 (Haswell core) |
| **Compiler and flags** | MinGW GCC 9.2 x64, -O2 -march=native |
| **Adoption** | 176 stars |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/mattreecebentley/plf_list) · [benchmark](http://www.plflib.org/benchmarks_haswell_gcc.htm) |

## Verdict

On the project's own benchmark page (MinGW GCC 9.2 x64, -O2 -march=native, Intel Xeon E3-1241 Haswell, libstdc++), plf::list beat std::list by about 333% average insertion throughput, 77% faster sort, 70% faster reverse, 91% faster remove/remove_if, 63% faster unique, and roughly 25% faster in ordered 'real-world' modification scenarios; the multi-order-of-magnitude clear()/destruction gains apply only to trivially-destructible types (811%/1,248% for non-trivial types).

## Use it when

- Hot paths doing frequent insertion/erasure in the middle of a list-like sequence, where std::list's per-node allocation overhead dominates
- Trivially-destructible or small POD element types, where the clear()/destructor speedups are largest
- Code that needs std::list's pointer/iterator stability under insertion and erasure but wants better cache locality from clustered nodes
- GCC/libstdc++ targets on x86-64 similar to the tested environment (MinGW GCC 9.2, Haswell), where the numbers are verified
- Projects that can vendor two headers (plf_list.h, plf_tools.h) and want C++98-through-C++23 portability without a build step

## Skip it when

- Code relying on partial (single-element or range) splicing between two separate list objects — only whole-list splice across instances is supported
- Code that needs a stable sort; plf::list's pointer-array quicksort is explicitly not guaranteed stable, unlike std::list::sort()
- Heavy multi-threaded use beyond simultaneous reads — docs describe only limited concurrency guarantees, not general thread safety
- Anything on libc++ or MSVC STL — only libstdc++ (MinGW GCC 9.2) is benchmarked, so gains on those standard libraries are unverified
- Very large heap-memory scenarios, where the project's own docs say erasure is only 'best... until very large amounts of memory are involved' without quantifying the falloff

## How it is fast

Each memory block keeps a per-block free list of erased slots; on insertion the algorithm searches outward from the target position for a nearby free slot before falling back to allocating a new block, which keeps blocks dense and cuts allocator calls compared to std::list's one-node-per-element scheme. sort() temporarily gathers node pointers into a contiguous array and quicksorts that array instead of mergesorting the linked list in place, which is faster but not guaranteed stable. clear()/destruction skip per-node destructor calls entirely for trivially-destructible element types, which is why those two benchmarks show multiple-order-of-magnitude speedups that don't generalize to non-trivial types.

## Compared with alternatives

Pick plf::list over plf::colony/hive when you need std::list's ordered, doubly-linked semantics and its splice/sort/merge/remove API; plf::colony is unordered and only a substitute when insertion order doesn't matter. The other siblings (eastl::vector, fast_vector, veque) target std::vector, not std::list, so they're not alternatives when you specifically need list-style pointer stability and O(1) mid-sequence insertion/erasure.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (bundles plf_tools.h / plf_tools_undef.h from the same repo for compiler-feature detection) |
| **Minimum toolchain** | C++98 minimum; auto-detects and uses C++11/14/17/20 features (allocator_traits, variadics, concepts, ranges) when the compiler supports them |
| **Platforms** | any (portable standard C++, no platform-specific code); benchmarked on x86-64 Windows/MinGW GCC 9.2 |
| **Thread safety** | Not documented as generally thread-safe. Docs state only simultaneous reads are reliably safe, and that insertion is unaffected by concurrent iteration except at the exact insertion point. |
| **Drop-in for the baseline** | partial — full std::list API plus extras, but splice() between two separate list instances only supports whole-list transfer, not single-element/range splice |

## Gotchas

- sort() is not guaranteed stable, unlike std::list::sort()
- The multiple-order-of-magnitude clear()/destruction speedups apply only to trivially-destructible types; non-trivially-destructible types see 811%/1,248% instead of 1,147,900%/6,350%
- shrink_to_fit() invalidates all pointers, iterators, and references — unlike ordinary insertion/erasure on plf::list
- Splicing an iterator to its own position is undefined behavior, matching std::list (raised as issue #34, closed by the maintainer as user error/UB, not a bug)

## Caveats and trade-offs

First-party benchmark, though code, compiler, flags and CPU are all published. Only libstdc++ (MinGW GCC 9.2) is tested, not libc++ or MSVC STL. The extreme clear/destruction figures apply to trivially-destructible types; for non-trivially-destructible types they drop to 811%/1,248%. The README's 57% erasure / 17% iteration / 20-24% overall / 293% insertion figures (GCC 8.1) do not appear on this benchmark page.

Node-based like std::list, so no contiguous storage or random access; the huge clear()/destruction figures are driven by trivially-destructible fast paths and not representative of typical mixed-type workloads; API is a near drop-in replacement but not fully standard-conformant in every corner case

## Maintenance

Actively maintained (last commit 2026-09-19; all 29 historical GitHub issues are closed) and Zlib-licensed, so it's low-risk to vendor as two header files.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now A.
- **Tier reason:** The benchmark page compares plf::list directly with std::list. It states MinGW GCC 9.2 x64, -O2 -march=native and an Intel Xeon E3-1241 (Haswell). The benchmark code is public as the 'plf benchmark suite' zip linked from the colony page downloads section (https://plflib.org/plf_benchmark_suite_08-07-2026.zip, HTTP 200).
- **Verifier notes:** The tier stays A, but the claim mixed README figures (57% erasure, 17% iteration, 20-24% overall) with benchmark-page figures. It also labelled trivially-destructible-only clear/destruction numbers as averages across types, so claimed_speedup was rewritten to match the page. Metadata checks out: Zlib, 176 stars, last commit 2026-09-19, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <http://www.plflib.org/benchmarks_haswell_gcc.htm>
  - <https://plflib.org/colony.htm>
  - <https://plflib.org/plf_benchmark_suite_08-07-2026.zip>
  - <https://github.com/mattreecebentley/plf_list>
- **Sources the enricher read:**
  - <https://github.com/mattreecebentley/plf_list>
  - <https://github.com/mattreecebentley/plf_list/blob/master/README.md>
  - <https://github.com/mattreecebentley/plf_list/blob/master/plf_list.h>
  - <https://github.com/mattreecebentley/plf_list/blob/master/LICENSE.md>
  - <https://github.com/mattreecebentley/plf_list/issues/34>
  - <http://www.plflib.org/benchmarks_haswell_gcc.htm>
  - <https://plflib.org/list.htm>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mattreecebentley/plf_list`) · [data/wave1/enrich/raw/github_com_mattreecebentley_plf_list.json](../../../data/wave1/enrich/raw/github_com_mattreecebentley_plf_list.json) (enrichment confidence 0.8)

</details>
