# cpp-btree (Kronuz)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Ordered maps and trees](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Header-only B-tree replacement for std::map/set/multimap/multiset with C++17 try_emplace API and lower per-element memory.

| | |
|---|---|
| **Beats** | std::map, std::set, std::multimap, std::multiset |
| **Claimed result** | STL vs B-Tree nanoseconds per op, e.g. BM_set_int32_lookup 1160ns vs 414ns (+64.31%), BM_map_int32_insert 1551ns vs 636ns (+58.99%), BM_set_int32_fwditer 158ns vs 26ns (+83.54%); string keys much smaller gap, e.g. BM_set_string_lookup 1709ns vs 1600ns (+6.38%), and string fifo is actually slower for the btree (-61.01%) |
| **Workload** | Google's original 2010 btree_bench: random insert/lookup/fulllookup/delete/queueaddrem/mixedaddrem/fifo/forward-iteration of int32, int64, and string keys/values into btree::set/map (node size 256) vs the STL red-black-tree set/map |
| **Metric** | throughput |
| **Hardware** | "pmattis-warp.nyc (4 X 2200 MHz CPUs)" per the embedded 2010 comment; vague/old machine label, not a specific CPU model |
| **Adoption** | 280 stars |
| **Last commit** | 2021-01-08 |
| **Links** | [repository](https://github.com/Kronuz/cpp-btree) · [benchmark](https://github.com/Kronuz/cpp-btree/blob/master/btree/btree.h) |

## Verdict

The header comment (btree/btree.h, lines \~51-101) reproduces Google's original 2010 btree_bench table comparing the STL red-black-tree set/map against btree::set/map (node size 256) for int32, int64 and string keys/values, run on 'pmattis-warp.nyc (4 X 2200 MHz CPUs)': integer-key ops improve roughly 40-84% (e.g. set_int32_lookup 1160ns to 414ns, set_int32_fwditer 158ns to 26ns), string-key ops improve much less (set_string_lookup 1709ns to 1600ns, +6.38%) and two fifo benchmarks regress (set_string_fifo -61.01%, map_string_fifo -49.75%). No compiler, flags, or exact CPU model are given, and this repo ships no benchmark harness to reproduce the numbers.

## Use it when

- Large in-memory ordered containers of small fixed-size keys (int32/int64) where memory footprint and cache-miss-bound lookup/insert/delete dominate
- Workloads with heavy forward iteration, where the header's own numbers show the largest gains (e.g. +83.54% on BM_set_int32_fwditer, +80%+ on int64/map variants)
- Call sites that don't retain iterators across mutation (short-lived iterators, no insert/erase while iterating elsewhere)
- Willing to vendor a small, unmaintained 3-file header rather than depend on absl::btree or another maintained B-tree
- Need per-instantiation control of node size for your specific key/value size

## Skip it when

- String or other expensive-to-move keys/values: gains shrink to single digits (+6.38% string set lookup, +1.16% string set insert) and fifo-pattern workloads regress (-61.01% set_string_fifo, -49.75% map_string_fifo) because rebalancing moves values between nodes
- Code that holds iterators across mutation — std::map's stable-iterator guarantee does not hold here; any insert/erase can invalidate unrelated iterators
- Need an actively maintained dependency: last commit 2021-01-08, one open unresolved bug (#2: assertion failure / later segfault reachable via operator[] -&gt; try_emplace on a non-trivial value type) with zero maintainer response since it was filed in 2020
- Need heterogeneous/transparent lookup (is_transparent-style comparators) — requested in still-open issue #10, not implemented
- Need documented thread-safety guarantees — none are given anywhere in the headers; treat it as unsynchronized, same as std::map

## How it is fast

Each node packs many keys/values into a fixed target size (256 bytes by default, tunable via the TargetNodeSize template parameter) instead of one value per red-black-tree node with three pointers plus color bit, so a lookup does several in-node comparisons per cache line touched rather than one pointer-chasing hop per comparison. The header's own comment attributes the win to better cache locality from this packing, not to a different asymptotic complexity — both are O(log n); a btree::set&lt;int32_t&gt; reportedly uses \~4.9 bytes/element total vs \~20 bytes for the red-black-tree set.

## Compared with alternatives

Pick cpp-btree over frozenca/BTree or fast-containers when you want a minimal, dependency-free, three-header vendor-in rather than a SIMD-tuned or hugepage-backed B-tree; its own numbers are far more modest (roughly 1.1-1.85x on integer-key ops, near-parity or a regression on strings) than frozenca/BTree's \~4.7-5.2x or fast-containers' \~2.1-4.8x, so prefer those when benchmark rigor and larger margins matter more than a small self-contained header.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the C++ standard library (&lt;algorithm&gt;, &lt;functional&gt;, &lt;memory&gt;, &lt;iterator&gt;, etc.) |
| **Minimum toolchain** | C++11 minimum (variadic templates, forward_as_tuple, piecewise_construct used throughout); README targets C++17-style semantics (try_emplace); contains() only compiles under C++20 (#if __cplusplus &gt; 201703L) |
| **Platforms** | any — portable C++ template code; no SIMD intrinsics or platform-specific code in btree.h/map.h/set.h |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — explain: same container names and STL-style method surface (insert/emplace/try_emplace/find/erase/operator[]) as std::map/set/multimap/multiset, but modifying the container invalidates ALL outstanding iterators rather than only erased ones, so code relying on std::map's iterator-stability guarantee cannot be ported unmodified |

## Gotchas

- Any insert/erase/rebalance invalidates every outstanding iterator on the container, not just ones pointing at removed elements — a real semantic break from std::map/std::set
- The header's own CAVEATS comment still points to a 'safe_btree' iterator-safe wrapper as a workaround, but no safe_btree.h ships in this repo — only btree.h, map.h and set.h exist
- Open issue #2 (filed 2020-09-24, still unresolved): assertion failure / later segfault in btree_node::construct_value, reached via operator[] -&gt; try_emplace on a non-trivial value type; no maintainer response
- Values are moved within and between nodes on every rebalance, so an expensive-to-move value_type can make this slower than std::map despite the smaller footprint

## Caveats and trade-offs

the benchmark numbers are a 2010-era comment carried over verbatim from Google's original (now-defunct Google Code) cpp-btree project; this repo does not include the btree_bench benchmark harness itself, so the numbers cannot be reproduced from what's here; hardware is only vaguely identified and compiler/flags are unstated, so this is capped at C despite the original project's rigor; string-key gains are much smaller than integer-key gains and one op (fifo on strings) is actually a regression

modifying the container invalidates ALL outstanding iterators (not just erased ones, unlike std::map/std::set); btree::set&lt;int32_t&gt; uses \~1 byte/element overhead vs \~16-20 bytes for a red-black-tree set; values are moved within/between nodes on rebalance, so it can lose to std::map when value_type is expensive to move

## Maintenance

Abandoned since the last real commit on 2021-01-08, with one open, unanswered bug report from 2020; Apache-2.0-licensed, header-only, and small enough (3 header files) to vendor as-is despite the lack of maintenance.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** btree/btree.h lines 51-101 carry Google's 2010 btree_bench table (STL vs B-Tree ns/op, e.g. set_int32_lookup 1160 vs 414 +64.31%, set_string_fifo -61.01%) run on 'pmattis-warp.nyc (4 X 2200 MHz CPUs)'; no harness in repo, no compiler/flags or CPU model, so C.
- **Verifier notes:** All quoted numbers match the header comment verbatim; map_string_fifo is also a regression (-49.75%). The record's last_commit (2023-08-11) was the repo's pushed_at; the latest commit on master is 2021-01-08, still 'abandoned'. Apache-2.0, 280 stars, not a GitHub fork (content derives from Google's code.google.com cpp-btree).
- **Fields the verifier corrected:** `last_commit`
- **Pages the verifier opened:**
  - <https://github.com/Kronuz/cpp-btree/blob/master/btree/btree.h>
  - <https://github.com/Kronuz/cpp-btree>
- **Sources the enricher read:**
  - <https://github.com/Kronuz/cpp-btree>
  - <https://github.com/Kronuz/cpp-btree/blob/master/README.md>
  - <https://github.com/Kronuz/cpp-btree/blob/master/btree/btree.h>
  - <https://github.com/Kronuz/cpp-btree/blob/master/btree/map.h>
  - <https://github.com/Kronuz/cpp-btree/blob/master/btree/set.h>
  - <https://github.com/Kronuz/cpp-btree/blob/master/LICENSE>
  - <https://github.com/Kronuz/cpp-btree/issues>
  - <https://github.com/Kronuz/cpp-btree/issues/2>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/kronuz/cpp-btree`) · [data/wave1/enrich/raw/github_com_kronuz_cpp_btree.json](../../../data/wave1/enrich/raw/github_com_kronuz_cpp_btree.json) (enrichment confidence 0.62)

</details>
