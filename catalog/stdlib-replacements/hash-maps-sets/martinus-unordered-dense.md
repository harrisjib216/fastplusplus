# ankerl::unordered_dense

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Vector-backed hash map beating std::unordered_map on build, iteration, and string-key workloads, with weaker reference stability.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | u64 keys (ankerl::unordered_dense::map vs std::unordered_map): 4.84x faster build+destroy (23.80 vs 115.31 ns/op, CSV ratio 4.8444; inserts alone 3.50x, 22.46 vs 78.66), 1.98x faster find (29.29 vs 57.89 ns/op, ratio 1.9763), 2.84x faster churn (84.63 vs 240.49 ns/op, ratio 2.8417), iterate 0.19 vs 21.29 ns/element ('std::unordered_map needs 110x' per page text); std::string keys: 3.64x build+destroy (92.84 vs 337.53), 1.79x find, 1.57x churn, \~100x iterate (derived from page data) |
| **Workload** | uint64_t- and std::string-keyed maps, 1-2 million entries; build+destroy, find, churn, iterate ops (own doc/benchmarks.md and scripts/ab harness). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X |
| **Compiler and flags** | clang 22.1.8, -O3 -DNDEBUG -std=c++20 (per scripts/ab/bench_readme.sh), transparent huge pages (madvise), process pinned to one core, Fedora 44 |
| **Adoption** | 1.48k stars; used in MySQL, PrusaSlicer and others per doc/users.md |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/martinus/unordered_dense) · [benchmark](https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md) |

## Verdict

On the library's own scripts/ab/bench_readme.sh harness (clang 22.1.8, -O3, transparent huge pages via madvise, pinned to one core, Fedora 44, AMD Ryzen 9 7950X; std::unordered_map presumed on libstdc++) with 1-2 million u64 or std::string keys, ankerl::unordered_dense::map beat std::unordered_map by 4.84x on build+destroy, 1.98x on find, 2.84x on churn, and roughly 110x on full-table iteration (0.19 vs 21.29 ns/element); with std::string keys build+destroy was 3.64x faster. This is a first-party benchmark — the author wrote both the map and the harness, which he states on the page — but the harness, raw CSV, and SVGs are public in the repo.

## Use it when

- Workloads that iterate the whole table often (snapshotting, serialization, aggregation) — 0.19 ns/element vs 21.29 for std::unordered_map (\~110x) and 5.5-13x faster than flat hash maps like abseil/boost
- std::string-keyed maps that are built and torn down repeatedly — 2.1-2.6x faster build+destroy than any flat map measured (93 ns/entry vs 192-237 ns)
- Need to debug/inspect the table's contents easily — data is a plain std::vector, visible in any debugger, plus a bundled LLDB formatter script
- Want a std::unordered_map-shaped container with pluggable storage: std::allocator, polymorphic allocators, a custom random-access container (e.g. boost::interprocess::vector), or a huge-page allocator
- Batch key lookups against a large or partially-missing key set — visit() gives 1.15-1.5x over one-at-a-time find() by overlapping independent memory accesses

## Skip it when

- Code that depends on iterator or reference stability across insert/erase — elements live in a std::vector, so growth reallocates and erase moves the last element into the freed slot
- Integer-keyed, find- or churn-dominated workloads where every ns counts — loses to boost::unordered_flat_map on u64 find (0.73x) and churn (0.61x), and to abseil's flat_hash_map similarly
- Erase-heavy workloads specifically — erase needs two lookups (the target slot and the slot of the element swapped into it), called out in the README as "relatively slow"
- Any code path where a value's destructor (or other callback) re-enters erase() on the same map while an erase is already in progress — this infinite-loops; the maintainer says it is unsupported and won't be fixed (GitHub issue #126)
- Need const Key in the stored pair (std::pair&lt;const Key, Value&gt;) — this map's pair has a non-const key, unlike std::unordered_map

## How it is fast

Values live in a std::vector, so iteration is a linear scan with no pointer chasing. Lookups use a separate flat array of 88-byte 'group' blocks (16 slots each: 16 one-byte fingerprints, 8 overflow counters, 16 value indices); a probe loads all 16 fingerprints and compares them in one SSE2 (x86-64) or NEON (AArch64) instruction. Overflow counters replace tombstones, so erase never forces a rehash. Inserts emplace_back onto the vector and record the slot in the index, keeping iteration order equal to insertion order until an erase reorders it.

## Compared with alternatives

Pick unordered_dense over abseil::flat_hash_map or boost::unordered_flat_map when iteration speed or std::string-keyed build/destroy dominate (its 0.19 ns/element iterate and \~93 ns/entry string build+destroy beat both); pick abseil or boost instead when integer-keyed find/churn throughput is what matters, since unordered_dense loses to boost there (0.73x find, 0.61x churn) and to abseil similarly. Against folly's F14ValueMap, unordered_dense wins on both build+destroy (4.84x vs 3.97x) and find (1.98x vs 1.72x) per this catalog's numbers. robin_hood::unordered_map is an earlier project by the same author with a different (robin-hood) index; unordered_dense's 5.0 index replaced that design and is reported 1.6x faster build+destroy than it on u64 keys, per doc/benchmarks.md.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (include/ankerl/unordered_dense.h + include/ankerl/stl.h; huge_page_allocator.h is a separate optional header needing &lt;sys/mman.h&gt;) |
| **Minimum toolchain** | C++17 for map/set; C++20 required only for the optional module build (import ankerl.unordered_dense) |
| **Platforms** | x86-64 (SSE2 probe, part of the baseline, no flag needed), AArch64 (NEON probe, likewise automatic); any other architecture falls back to a portable word-at-a-time probe via ANKERL_UNORDERED_DENSE_HAS_SSE2/NEON=0. huge_page_allocator degrades to std::allocator on Windows/macOS. |
| **Thread safety** | not documented — no built-in synchronization; standard container assumptions apply (concurrent reads are fine, no writer may run concurrently with any other access) |
| **Drop-in for the baseline** | partial — explain: same STL-style API as std::unordered_map/set for nearly everything, but no const Key in the pair, weaker iterator/reference stability on insert/erase, and erase() is not reentrant |

## Gotchas

- No iterator or reference stability on insert or erase — elements live in a std::vector, so any growth or erase can relocate other elements
- Reentrant erase() (e.g. a destructor triggered by that very erase calling erase() again on the same map) infinite-loops; maintainer confirmed this is unsupported and won't be fixed (issue #126)
- A custom hash functor without `using is_avalanching = void;` is silently treated as low-quality and gets an extra mixing step; forgetting the marker on a genuinely good hash costs speed with no warning (require_avalanching&lt;Hash&gt; exists to make this a compile error instead)
- Post-5.0 the index is one 88-byte block per 16 slots (5.5-9.5 bytes/slot depending on bucket_type), not one bucket per slot as in 4.x — code carried over from 4.x that computes memory as bucket_count() \* sizeof(bucket_type) still compiles but silently gives the wrong number; use index_bytes() instead

## Caveats and trade-offs

First-party benchmark: the library author wrote both map and harness and says so on the page; harness, raw CSV (doc/bench_readme.csv) and SVGs are published. Original record mislabelled the CSV 'build' column (inserts only) as build+destroy; the page's build+destroy panel is the CSV 'buildfree' column, where std::unordered_map is 115.31 ns/op (chart shows std at 4.84 relative to unordered_dense). Standard library not named on the page; baseline_stdlib set to libstdc++ by inference (harness calls plain clang++ with no -stdlib flag on Fedora, where clang defaults to libstdc++; page also discusses glibc arenas). Speed only: in the same run std::unordered_map has lower peak RSS per u64 entry (45.78 B) than every flat map. Page itself says integer find/churn lose to boost/absl flat maps; treat &lt;5% as a tie.

No reference/iterator stability on insert or erase (elements live in a std::vector, so growth or erase can move everything); erase is relatively slow (needs two lookups); loses to boost::unordered_flat_map on integer find (0.73x of boost's time) and churn (0.61x) despite winning iteration and string build/destroy.

## Maintenance

Actively maintained (last commit 2026-09-23, 1,482 stars, CMakeLists shows current release 5.0.1); MIT-licensed, header-only, and used in production projects including MySQL and PrusaSlicer per doc/users.md.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** Public harness scripts/ab/bench_readme.sh + scripts/ab/maps.cpp in martinus/unordered_dense runs every map incl. std::unordered_map; page states clang 22.1.8, -O3, Ryzen 9 7950X. Code+compiler+flags+CPU all present, so A holds. First-party, but the rules say who ran it does not matter.
- **Verifier notes:** Tier A confirmed; build+destroy corrected from 3.50x (inserts-only column) to 4.84x as the page's chart shows. MIT, 1,482 stars, last commit 2026-09-23, users.md lists MySQL and PrusaSlicer.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** On 1M uint64 keys ankerl::unordered_dense was slower than developer source's own fastcpp::flat_hash_map on all three workloads measured (hit lookup, miss lookup, build from empty), and that map in turn lost lookups to phmap (1.29x on hits, 1.39x on misses). Per-operation figures for unordered_dense were not published. (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-02-libraries)
- **Pages the verifier opened:**
  - <https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/bench_readme.csv>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/bench-readme-u64.svg>
  - <https://github.com/martinus/unordered_dense/blob/main/scripts/ab/bench_readme.sh>
  - <https://github.com/martinus/unordered_dense>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/users.md>
- **Sources the enricher read:**
  - <https://github.com/martinus/unordered_dense>
  - <https://github.com/martinus/unordered_dense/blob/main/README.md>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/usage.md>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/design.md>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md>
  - <https://github.com/martinus/unordered_dense/blob/main/CMakeLists.txt>
  - <https://github.com/martinus/unordered_dense/issues?q=bug>
  - <https://github.com/martinus/unordered_dense/issues?q=is%3Aopen>
  - <https://github.com/martinus/unordered_dense/issues/98>
  - <https://github.com/martinus/unordered_dense/issues/126>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/martinus/unordered_dense`) · [data/wave0-seed/enrich/raw/github_com_martinus_unordered_dense.json](../../../data/wave0-seed/enrich/raw/github_com_martinus_unordered_dense.json) (enrichment confidence 0.85)

</details>
