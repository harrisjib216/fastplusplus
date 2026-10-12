# itlib small and flat containers (itlib::flat_map, itlib::small_vector, itlib::static_vector)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Ordered maps and trees](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Single-header C++11 flat_map/flat_set (sorted vector) plus small_vector and static_vector; claims to beat std::map for small sizes, unmeasured.

| | |
|---|---|
| **Beats** | std::map |
| **Claimed result** | No numbers. Header comment in include/itlib/flat_map.hpp: "It generally performs much faster than std::map for smaller sets of elements" (same sentence for std::set in flat_set.hpp). small_vector.hpp and static_vector.hpp only claim cache-local data; README calls them "similar to boost::small_vector / boost::static_vector / boost::flat_map" with no speed statement. |
| **Workload** | No benchmark exists for these containers; the only qualitative claim is in the header comment of flat_map.hpp and flat_set.hpp about smaller sets of elements versus std::map/std::set. |
| **Metric** | throughput |
| **Adoption** | 212 stars; a search snippet (not opened) says VTK/diy2 merge requests replace chobo small_vector with itlib small_vector |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/iboB/itlib) |

## Verdict

Nothing has been measured. The only performance statement is the header comment that flat_map and flat_set 'generally perform much faster than std::map [std::set] for smaller sets of elements', with no sizes, compiler or hardware. The repo's only benchmark target (test/b-rand_dist.cpp, built with picobench) covers random distributions, and a web search found no third-party numbers.

## Use it when

- Small maps or sets (tens to low hundreds of entries) built once and then looked up or iterated many times, with keys that are cheap to compare and move
- You want a std::map-shaped API without Boost: one MIT header, C++11, no dependencies
- You need a fixed-capacity map with no heap use (embedded or real-time code): back flat_map with itlib::static_vector, as the unit tests do
- Per-object short lists that usually stay under N elements (small_vector), or a known maximum size (static_vector)

## Skip it when

- Large maps with frequent inserts or erases in the middle: each one shifts O(n) elements, so the B-tree siblings fit better
- Code that relies on std::map's stable iterators and references across insert and erase
- Code that inserts or push_backs an element of the same small_vector or static_vector, or erases empty ranges of non-trivial types (see gotchas)
- You need measured evidence of a speedup: the project publishes none; boost::container::flat_map has numbers, and a C++23 standard library that ships std::flat_map is the standard alternative
- Bulk loading unsorted keys one insert at a time: there is no range insert, so this is O(n^2); build the vector and use the sorting constructor instead

## How it is fast

flat_map/flat_set are sorted-array maps: std::lower_bound binary search for lookups and contiguous storage for iteration, so there is no per-node allocation or pointer chasing, at the cost of O(n) element shifts on insert and erase. small_vector and static_vector avoid heap allocation while the size stays under the inline capacity; past that, small_vector grows by about 1.5x. There is no SIMD and no memcpy fast path: elements are moved one at a time through allocator_traits or placement new.

## Compared with alternatives

Pick it over boost::container::flat_map/flat_set (the closest sibling, and the one with numbers: about 1.1-2.5x faster than std::set at sizes 2-128) only when you cannot take a Boost dependency or want to swap the backing container, for example to static_vector. For large maps, tlx btree_map, cpp-btree, frozenca/BTree or fast-containers are the measured choices.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only) |
| **Minimum toolchain** | C++11; CI builds with MSVC on Windows, GCC on Ubuntu and clang on macOS (compiler versions not stated); CMake 3.24 is needed only for the project's own build and tests |
| **Platforms** | any (portable standard C++, no intrinsics) |
| **Thread safety** | not documented; the headers contain no internal locking |
| **Drop-in for the baseline** | partial: flat_map has std::map's lookup and modifier names, but its 4th template parameter is a container rather than an allocator, value_type is std::pair&lt;Key, T&gt; rather than pair&lt;const Key, T&gt;, insert and erase invalidate all iterators, and try_emplace, insert_or_assign, contains, extract, merge and range insert are missing |

## Gotchas

- Aliasing bug (found by code reading, not run): small_vector's push_back, emplace_back and insert call grow_at first, which moves the existing elements (into a new buffer when full, or shifting right in place) and destroys the sources (freeing an old heap buffer) before constructing from the argument. So v.push_back(v[0]) at capacity reads a destroyed or freed element, and v.insert(v.begin(), v[2]) copies whatever was shifted into slot 2 ({10,20,30,40} becomes {20,10,20,30,40}). static_vector::insert has the same in-place problem. std::vector guarantees both cases work, and the unit tests do not cover them.
- Empty-range erase (code reading): erase(first, last) with first == last before end() runs shrink_at with num = 0, which destroys each element from first to end and then move-constructs it from itself. That is undefined behaviour for types such as std::string. The only empty-erase unit test uses int.
- flat_map and flat_set iterators are the container's mutable iterators and flat_map's value_type has a non-const key, so writing through an iterator can silently break the sort order. The default comparator is a transparent operator&lt; functor, not std::less&lt;Key&gt;. When duplicate keys are passed to the container or initializer_list constructor, std::sort (unstable) followed by std::unique decides which value survives, whereas std::map keeps the first.
- small_vector's move constructor and move assignment are unconditionally noexcept but move a static-mode vector element by element, so a throwing T move calls std::terminate. Element transfers use std::move rather than move_if_noexcept, so there is no strong exception guarantee. With the default RevertToStaticBelow = 0 a vector that has spilled to the heap stays there even after clear(); a nonzero value makes erase, resize or pop_back move the elements back into the inline buffer, invalidating all iterators.

## Known shortcomings

- No numbers anywhere: only a header comment 'much faster than std::map for smaller sets'; 212 stars; continues the archived chobo-shl. Whole-stdlib decomposition seed kept at D for completeness.
- Enricher: still no numbers (the only benchmark is test/b-rand_dist.cpp); two bugs found by code reading: small_vector push_back, emplace_back and insert move and destroy the old elements (and free the old heap buffer) before copying the argument, so v.push_back(v[0]) at capacity reads a freed element and v.insert(begin, v[2]) inserts the wrong value (static_vector::insert has the same in-place bug); erase(first, last) with first == last before end() destroys each element and then move-constructs it from itself (UB for std::string); tests cover empty erase on int only.

## Caveats and trade-offs

No numeric comparison against std::map, std::vector, boost::container::flat_map or boost::container::small_vector anywhere found: repo has no bench folder, test/ holds one benchmark (b-rand_dist.cpp, random distributions only, no results published), and a web search found no third-party numbers. The README adds only qualitative wording (flat_map/flat_set "better cache locality", static_vector "cache-local value members", pod_vector skips constructors and uses memcpy/realloc "to improve performance"). itlib continues Chobolabs/chobo-shl (archived 2020-10-15; its README says it is no longer supported and points to iboB/itlib), which also has no numbers. Tier D; 212 stars is below the usual notability bar for D entries. Header says only "generally ... for smaller sets", no sizes or machine. small_vector and static_vector belong to sequence-containers rather than ordered-maps-trees.

Single-header, MIT, C++11. flat_map/flat_set keep a sorted std::vector-compatible container (swappable via template argument, so itlib::static_vector or small_vector can back them); lookup O(log n), insert and erase O(n); iterators and references invalidated on insert/erase; template signature differs from std::map (last parameter is a container, not an allocator). small_vector has a static buffer then falls back to heap; static_vector has fixed capacity.

## Maintenance

Actively maintained (last commit 2026-10-06, 451 commits, 212 stars, CI with sanitizers on MSVC, GCC and clang), MIT-licensed and easy to vendor one header at a time, but tier D: no performance numbers exist, and code reading shows that small_vector and static_vector mishandle self-referencing insert and push_back and empty-range erase of non-trivial types.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** No numbers anywhere: the only comparative statement is the header comment in include/itlib/flat_map.hpp ("It generally performs much faster than std::map for smaller sets of elements") and the same sentence for std::set in flat_set.hpp; test/ holds only b-rand_dist.cpp as a benchmark, and a web search found no third-party measurement.
- **Verifier notes:** Record accurate (212 stars, MIT, last commit 2026-10-06, header claim quoted correctly). Keep at D with shortcomings: no numbers at all, qualitative header comment only, low notability (212 stars); the VTK/diy2 usage claim is from a search snippet and was not verified. GitHub casing is iboB/itlib; id left unchanged.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-71 (wave 1, stdlib decomposition); enricher (wave 1 stdlib seeds, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/iBob/itlib>
  - <https://github.com/iboB/itlib/commits/master>
  - <https://github.com/iboB/itlib/tree/master/test>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/include/itlib/flat_map.hpp>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/include/itlib/flat_set.hpp>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/include/itlib/small_vector.hpp>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/include/itlib/static_vector.hpp>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/README.md>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/LICENSE.txt>
  - <https://github.com/Chobolabs/chobo-shl>
- **Sources the enricher read:**
  - <https://github.com/iboB/itlib>
  - <https://github.com/iboB/itlib/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/README.md>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/include/itlib/flat_map.hpp>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/include/itlib/flat_set.hpp>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/include/itlib/small_vector.hpp>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/include/itlib/static_vector.hpp>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/test/t-small_vector-11.cpp>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/test/t-static_vector-11.cpp>
  - <https://raw.githubusercontent.com/iboB/itlib/HEAD/test/t-flat_map-11.cpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ibob/itlib`) · [data/wave1/enrich/raw/github_com_ibob_itlib.json](../../../data/wave1/enrich/raw/github_com_ibob_itlib.json) (enrichment confidence 0.65)

</details>
