# tlx::btree_map / btree_set / btree_multimap (STX B+Tree lineage)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Ordered maps and trees](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟡 stale

> Header-only B+ tree implementing STL's map/set/multimap/multiset; beats libstdc++'s red-black tree at large n.

| | |
|---|---|
| **Beats** | std::map, std::multiset |
| **Claimed result** | 2007 run: for n &gt; 1,024,000 items, the red-black tree (libstdc++ multiset) needs almost twice as much time as a B+ tree with 32 slots. Per-item insertion diverges beyond \~16,000 items. 2011 run: same qualitative win, with the insertion curves diverging at \~100,000 items. 2013 run: results 'very similar' to 2011, and std::map is noted as much slower than std::set while the B+ tree map is only slightly slower than the B+ tree set. The in-repo tlx results PDF (tests/container/btree_speedtest_results.pdf, 2019) plots tlx::btree_multiset below std::multiset for insert, find and insert/find/delete at large n, roughly 3x at 2^26 items by visual chart reading. |
| **Workload** | Random-integer multiset (and, in 2013, map/multimap) tests: insert-only, insert+find+erase, and find-only on pre-filled trees. n runs from 125 to 4,096,000, 32,768,000 or 65,536,000 depending on the run, doubling each step. Several B+ tree slot sizes (4-256) are tested against the libstdc++ red-black tree and hash tables. |
| **Metric** | throughput |
| **Hardware** | 2007: Pentium 4 3.2GHz, 2GB RAM; 2011: Intel Core i7 950 @3.07GHz; 2013: Intel Core i7 920 @2.67GHz |
| **Compiler and flags** | 2007: g++ 4.1.2 -O3 -fomit-frame-pointer; 2011: gcc 4.4.5 -O3 -fomit-frame-pointer; 2013: gcc 4.5.0 -O3 -march=native |
| **Adoption** | 458 stars (tlx); predecessor stx-btree used in academic string-sorting/Thrill research code |
| **Last commit** | 2025-01-10 |
| **Links** | [repository](https://github.com/tlx/tlx) · [benchmark](https://panthema.net/2007/stx-btree/speedtest/) |

## Verdict

Evidence tier A: the author's own STX-btree/tlx speedtest (code public in tests/container/btree_speedtest.cpp) measured random-integer multiset insert-only, insert+find+erase, and find-only workloads at n from 125 to tens of millions against libstdc++'s std::multiset/std::multimap (red-black tree). Per the benchmark page (fetched this session): the 2007 run (g++ 4.1.2, -O3 -fomit-frame-pointer, Pentium 4 3.2GHz) showed the red-black tree taking almost 2x as long as a 32-slot B+ tree above roughly 1,024,000 items; the 2011/2013 reruns (gcc 4.4.5/4.5.0, Core i7 9xx, -O3 with -fomit-frame-pointer or -march=native) show the same divergence starting near 100,000 items. The input record additionally reports a 2019 in-repo results PDF (btree_speedtest_results.pdf, not opened by me this session) showing tlx::btree_multiset roughly 3x faster than std::multiset by n=2^26, with no hardware/compiler stated for that run.

## Use it when

- Large (roughly &gt;100k-1M+ element) in-memory ordered map/set/multiset/multimap of cheaply-comparable keys (e.g. integers) where insert, find and erase are all exercised and cache-miss-bound traversal dominates.
- You want an STL-like drop-in-ish replacement for std::map/std::set without taking on SIMD or hugepage requirements.
- You need sorted-order range queries (lower_bound/upper_bound/equal_range) alongside point lookups; B+ tree leaves are linked so range scans stay cheap.
- You can vendor a small BSL-1.0 header (or the wider tlx repo) instead of a heavier dependency.
- Your workload includes bulk-loading a pre-sorted range into an empty container (bulk_load()).

## Skip it when

- You rely on std::map's pointer/reference/iterator stability across insert/erase; tlx's B+ tree gives no such guarantee.
- You need C++17/20 map features: emplace, try_emplace, insert_or_assign, extract, merge, or node_type/heterogeneous lookup; none appear in btree_map.hpp.
- You need move construction/assignment on the container itself; only a copy constructor, copy assignment, and swap() are defined in the header I read.
- Small containers (tens of elements or fewer); none of the record's benchmarks show a win below tens of thousands of items, and boost::flat_set/flat_map targets exactly that small-size regime.
- You need erase(first,last) or lock-free/concurrent access; range-erase is unimplemented (only aborts under a debug-only macro) and no synchronization is documented or visible in the header.

## How it is fast

Leaf and inner nodes are sized by btree_default_traits to hold as many keys as fit in roughly a 256-byte block, so a comparison step touches one cache line instead of the one-key-per-node layout of a red-black tree. Leaves store keys and their associated data in two separate parallel arrays rather than an array of key/value pairs, and descent does an in-node search over a wide node instead of following per-key left/right/parent pointers. Net effect: fewer pointer-chasing cache misses per operation at large n, at the cost of more in-node comparisons per level.

## Compared with alternatives

Pick tlx::btree over fast-containers, S+/S-tree, or boost::container::flat_set/flat_map when the workload is genuinely dynamic (both insert and erase, not build-once-then-query) at large scale (roughly &gt;100k-1M items) and you want a permissively licensed (BSL-1.0), dependency-free header with no SIMD/AVX/hugepage requirement; prefer S+/S-tree if the workload is static (bulk-built once, then read-only lower_bound queries), fast-containers if you can require SIMD+hugepages for its larger, more recently measured wins at 10M-element scale, or boost::flat_set/flat_map if containers stay small (roughly 2-128 elements).

## Integration

| | |
|---|---|
| **Form** | header-only (for the btree containers themselves; the wider tlx repo also builds a small static/shared libtlx for unrelated modules like digest/string helpers, but tlx/container/btree\*.hpp are pure templates with no matching .cpp in LIBTLX_SOURCES) |
| **Dependencies** | none for normal insert/find/erase use (README states zero external dependencies; btree.hpp only includes &lt;algorithm&gt; &lt;cassert&gt; &lt;cstddef&gt; &lt;functional&gt; &lt;iterator&gt; &lt;memory&gt; &lt;utility&gt; and tlx/die/core.hpp). Caveat: verify() and the self_verify trait call tlx_die_unless() -&gt; die_with_message(), which is declared in tlx/die/core.hpp but defined only in tlx/die/core.cpp, so using invariant verification requires linking libtlx or compiling that one file yourself. |
| **Minimum toolchain** | C++11 minimum. Root CMakeLists.txt auto-probes compiler flags, preferring -std=c++20 and falling back through c++17/c++14/c++11/c++0x. CI (.github/workflows/cmake.yml) builds with GCC 7.5, 9.3 (incl. -m32), 11, 13 and Clang 15 on macOS 13-15; requires CMake &gt;= 3.7. |
| **Platforms** | x86-64 and 32-bit x86 on Linux, and macOS (Clang) are exercised in the GitHub Actions matrix I read; a Windows job exists in that same file but is commented out/disabled. README claims general portability ('smartphones, supercomputers, windows, etc.') and the README badge references a separate AppVeyor Windows build, which I did not open this session. |
| **Thread safety** | not documented; no locks or atomics are visible in tlx/container/btree.hpp. Treat it like std::map: concurrent writers need external synchronization. |
| **Drop-in for the baseline** | partial — explain: same iterator/begin-end/find/insert/erase/operator[]/comparison-operator surface as std::map/std::set with the same Key/Compare/Allocator template parameter order, but missing emplace/try_emplace/insert_or_assign/extract/merge/node_type, no move constructor (only copy ctor/assign plus swap()), erase(first,last) not implemented, and no iterator/pointer stability guarantee across mutation (std::map guarantees this) — a mechanical typedef swap will not always compile or behave identically. |

## Gotchas

- verify()/self_verify require linking tlx/die/core.cpp (or libtlx) for die_with_message(); not fully header-only if you use invariant checking.
- No move constructor or move-assignment on btree_map/btree_set — only copy constructor, copy assignment, and swap() are defined.
- erase(first, last) is unimplemented: it only exists (and aborts) if TLX_BTREE_TODO is defined, otherwise the method is absent entirely.
- No iterator/pointer stability guarantee across insert/erase, unlike std::map/std::set — don't hold iterators or pointers across mutations.

## Caveats and trade-offs

The page's numbers are 12-19 years old, from Pentium 4 and Core i7 9xx machines with gcc 4.x. The speedtest page belongs to the predecessor stx-btree project (marked OBSOLETE and folded into tlx). tlx does ship its own btree_speedtest.cpp and a 2019 results PDF showing the same win vs std::multiset, but that PDF states no hardware or compiler. The page's speedups are shown mainly as plots, and the text states only the \~2x figure.

B+tree stores keys and values in separate parallel arrays per node (different memory layout than std::map's node-per-pair); no pointer/iterator stability guarantee; pulls in the broader tlx helper-library dependency

## Maintenance

Stale: last commit 2025-01-10 per the record, and the only open GitHub issue I found (#62) concerns the unrelated d_ary heap, not btree. BSL-1.0 licensed (unlike the GPL-3.0 predecessor stx-btree) and small enough to vendor as a handful of headers — copyable per the record's usability field.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B, because B needs peer review or an independent third-party suite and this is the author's own benchmark. The speedtest page states compiler, flags and hardware for each run, and the benchmark code is public: bingmann/stx-btree speedtest/speedtest.cc, and its current form in tlx at tests/container/btree_speedtest.cpp. That code runs against libstdc++ std::multiset/std::multimap.
- **Verifier notes:** The 2013 flags were '-O3 -march=native', not -fomit-frame-pointer plus -march=native. The tier was re-derived as A because both the code and full methodology are public (it is the author's benchmark, not third-party). Metadata checked: BSL-1.0, 458 stars, last commit 2025-01-10 (stale). The predecessor bingmann/stx-btree is GPL-3.0, while the tlx code is BSL-1.0.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://panthema.net/2007/stx-btree/speedtest/>
  - <https://github.com/tlx/tlx>
  - <https://github.com/tlx/tlx/blob/master/tests/container/btree_speedtest.cpp>
  - <https://github.com/tlx/tlx/blob/master/tests/container/btree_speedtest_results.pdf>
  - <https://github.com/bingmann/stx-btree>
- **Sources the enricher read:**
  - <https://github.com/tlx/tlx>
  - <https://github.com/tlx/tlx/blob/master/tlx/container/btree_map.hpp>
  - <https://github.com/tlx/tlx/blob/master/tlx/container/btree.hpp>
  - <https://github.com/tlx/tlx/blob/master/tlx/die/core.hpp>
  - <https://github.com/tlx/tlx/blob/master/CMakeLists.txt>
  - <https://github.com/tlx/tlx/blob/master/tlx/CMakeLists.txt>
  - <https://github.com/tlx/tlx/blob/master/.github/workflows/cmake.yml>
  - <https://github.com/tlx/tlx/issues>
  - <https://panthema.net/2007/stx-btree/speedtest/>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/tlx/tlx`) · [data/wave1/enrich/raw/github_com_tlx_tlx.json](../../../data/wave1/enrich/raw/github_com_tlx_tlx.json) (enrichment confidence 0.75)

</details>
