# RadixMap (radix-map)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Ordered maps and trees](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only PATRICIA/radix-tree map beating std::map on insert/contains for string and numeric keys.

| | |
|---|---|
| **Beats** | std::map |
| **Claimed result** | 3.2x faster insert / 5.4x faster contains() for string keys; 2.2x faster insert / 2.3x faster contains() for double keys (RadixMap \~111-118ms / \~70-73ms / \~101-104ms / \~46-47ms vs std::map \~366-369ms / \~379-407ms / \~215-234ms / \~100-109ms for the same 20,000-key runs) |
| **Workload** | Catch2 benchmark harness (Release build), inserting and contains()-looking-up 20,000 std::string keys and, separately, 20,000 double keys |
| **Metric** | throughput |
| **Compiler and flags** | Release build, -O3 (compiler and version unstated) |
| **Adoption** | 0 stars (new project, first commit 2026-07) |
| **Last commit** | 2026-07-09 |
| **Links** | [repository](https://github.com/lrmoorejr/radix-map) · [benchmark](https://github.com/lrmoorejr/radix-map/blob/main/README.md) |

## Verdict

README's Catch2 [benchmark]-tagged test cases (Release build, -O3, compiler version and CPU unstated), inserting and then contains()-checking 20,000 keys, report RadixMap 3.2x faster insert and 5.4x faster contains() than std::map for std::string keys (\~111-118ms/\~70-73ms vs std::map's \~366-369ms/\~379-407ms), and 2.2x faster insert / 2.3x faster contains() for double keys (\~101-104ms/\~46-47ms vs std::map's \~215-234ms/\~100-109ms).

## Use it when

- Sorted map over std::string or integral/floating-point keys where insert/contains throughput matters most: 3.2x/5.4x faster than std::map for strings, 2.2x/2.3x for doubles at 20,000 keys (Release, -O3, per README).
- Need prefix search over string keys (prefix_range) instead of hand-rolling lower_bound() plus an increment-last-byte upper bound that breaks on a 0xFF-terminated prefix.
- Workload dominated by contains()/at()/operator[] rather than find()/lower_bound(): contains() is far cheaper than find() in the same benchmarks (e.g. \~70-73ms vs \~452-461ms for 20,000 string keys).
- Single-threaded or externally-synchronized use only — no built-in thread safety.
- C++20 codebase willing to vendor two header files (RadixMap.hpp + BoundedVector.hpp) rather than link a library.

## Skip it when

- Need reverse iteration: no rbegin()/rend()/operator--, forward-only because the tree has no parent pointers.
- Need a custom comparator or allocator template parameter — the header's own doc comment lists both as unsupported.
- Erase-heavy workloads: erase() is a tombstone that clears the value but leaves the compressed tree structure (and its memory) untouched, so memory grows with churn beyond the live entry count.
- Key type has no RadixMapKeyTraits specialization and you don't want to write one (only std::string and arithmetic types are built in).
- Risk-averse selection: 0 GitHub stars, first commit 2026-07-06, single author, 0 issues opened yet, no independent benchmarking or production use documented.

## How it is fast

Uses a PATRICIA/radix-tree structure that stores each shared key prefix once per node (a node for "http://" is shared by every key starting with it) instead of comparing whole keys node-by-node like a red-black tree, and branches via an adaptively-sized bit-mask over the next byte rather than per-byte/per-key comparison. Nodes and values are allocated from a block-based bump/arena allocator (RadixMapArena) rather than individually. For fixed-length keys (integral/floating-point), the find()/lower_bound() traversal stack is backed by the vendored BoundedVector, making that state heap-allocation-free.

## Compared with alternatives

Pick RadixMap over the B-tree-family siblings (fast-containers, Flat-Map-RB-Tree, cpp-btree, frozenca/BTree, tlx::btree_map) when you specifically need prefix_range()-style prefix queries over std::string keys, or want a two-header vendor-and-go dependency rather than a library benchmarked at multi-million-element scale. Pick libart instead if you want a more independently scrutinized adaptive radix tree (with a C API, not a std::map-like C++ interface); pick a B-tree sibling if you need comparator/allocator customization or verified performance at 1M+ elements, since RadixMap has only been measured at 20,000 keys by its sole author.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none at runtime; Catch2 3 is required only to build/run the bundled RadixMap-test.cpp benchmark/test suite; optional integration with a separate Ensure.hpp project for throw_if(), falls back to an equivalent local implementation if that header isn't present |
| **Minimum toolchain** | C++20 (CMakeLists.txt sets CMAKE_CXX_STANDARD 20) |
| **Platforms** | no explicit architecture requirement documented; CI (.github/workflows/ci.yml) builds and tests on ubuntu-24.04 and macos-latest via CMake+Ninja; Windows/MSVC not covered by CI |
| **Thread safety** | not thread-safe — the class's own doc comment explicitly lists 'thread-safety' under 'Not supported' |
| **Drop-in for the baseline** | partial — explain: same core operations as std::map (insert/contains/at/operator[]/erase/find/lower_bound/upper_bound/iteration) but no comparator/allocator template parameter, requires a RadixMapKeyTraits&lt;Key&gt; specialization for any Key beyond std::string/arithmetic types, and needs a second vendored header (BoundedVector.hpp) despite the repo description calling it single-header |

## Gotchas

- Range-for needs auto&& or auto, never auto&: operator\*() returns a proxy Entry{Key first; Value& second;}, not a reference into a stored pair, so 'for(auto &entry : map)' fails to compile.
- +0.0 and -0.0 double keys encode to different byte patterns and are treated as distinct, unlike std::map&lt;double,...&gt;'s default std::less which treats them as equal.
- erase() does not reclaim compression: repeated insert/erase churn leaves memory usage above the current live-entry count, with no compact() available yet.
- prefix_range() degenerates to at most a single entry for fixed-width key types like double, since a shorter double isn't itself a valid key — it only does useful prefix work for std::string keys.

## Caveats and trade-offs

very new, unstarred, single-author project with no independent scrutiny yet; the README explicitly benchmarks a Release/-O3 build but names neither a compiler version nor a CPU model, so it's capped at C, not A/B; only one key count (20,000) was tested

keys limited to std::string or integral/floating-point types with a RadixMapKeyTraits specialization; erase() is a tombstone and does not reclaim compression, so heavy churn grows memory beyond the live entry count; iteration is forward-only (no reverse iterators); +0.0 and -0.0 double keys are treated as distinct, unlike std::map's default std::less

## Maintenance

Active but very new (first commit 2026-07-06, last commit 2026-07-09), single-author, 0 stars, 0 issues opened; Apache-2.0 licensed and header-only (two files: RadixMap.hpp + BoundedVector.hpp), trivial to vendor or drop.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section gives std::map comparison tables (3.2x/5.4x/2.2x/2.3x, with \~111-118 ms vs \~366-369 ms etc.) from public Catch2 [benchmark] cases in RadixMap-test.cpp, Release/-O3; no compiler version or CPU model stated, so first-party C.
- **Verifier notes:** All numbers match the README verbatim. GitHub reports license NOASSERTION, but LICENSE file is the full Apache License 2.0 text, so Apache-2.0/copyable stands. Repo created 2026-07-06, last commit 2026-07-09, 0 stars.
- **Pages the verifier opened:**
  - <https://github.com/lrmoorejr/radix-map>
  - <https://github.com/lrmoorejr/radix-map/blob/main/README.md>
  - <https://github.com/lrmoorejr/radix-map/blob/main/LICENSE>
  - <https://github.com/lrmoorejr/radix-map/blob/main/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/lrmoorejr/radix-map>
  - <https://github.com/lrmoorejr/radix-map/blob/main/README.md>
  - <https://github.com/lrmoorejr/radix-map/blob/main/CMakeLists.txt>
  - <https://github.com/lrmoorejr/radix-map/blob/main/RadixMap.hpp>
  - <https://github.com/lrmoorejr/radix-map/blob/main/.github/workflows/ci.yml>
  - <https://github.com/lrmoorejr/radix-map/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/lrmoorejr/radix-map`) · [data/wave1/enrich/raw/github_com_lrmoorejr_radix_map.json](../../../data/wave1/enrich/raw/github_com_lrmoorejr_radix_map.json) (enrichment confidence 0.45)

</details>
