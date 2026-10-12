# Boost.Unordered (boost::unordered_flat_map)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only SIMD open-addressing hash map/set for Boost; unordered_flat_map is 2.7x-11.6x faster than std::unordered_map.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | u64 keys (boost::unordered_flat_map vs std::unordered_map): 5.00x faster build+destroy (23.04 vs 115.31 ns/op; inserts alone 3.54x, 22.23 vs 78.66), 2.70x faster find (21.42 vs 57.89 ns/op), 4.66x faster churn (51.57 vs 240.49 ns/op), 11.60x faster iterate (1.84 vs 21.29 ns/element); std::string keys: 1.55x build+destroy (218.19 vs 337.53), 1.55x find, 1.72x churn, 32.9x iterate (derived from page data) |
| **Workload** | uint64_t- and std::string-keyed maps, 1-2 million entries; build+destroy, find, churn, iterate ops measured via unordered_dense's third-party benchmark harness. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X |
| **Compiler and flags** | clang 22.1.8, -O3 -DNDEBUG -std=c++20 (per scripts/ab/bench_readme.sh), transparent huge pages (madvise), process pinned to one core, Fedora 44 |
| **Adoption** | 92 stars on the standalone module repo; ships inside Boost proper (used far more broadly than the module repo's own star count reflects) |
| **Last commit** | 2026-06-17 |
| **Links** | [repository](https://github.com/boostorg/unordered) · [benchmark](https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md) |

## Verdict

On unordered_dense's public bench_readme.sh harness (clang 22.1.8, -O3 -DNDEBUG -std=c++20, transparent huge pages, one pinned core, Fedora 44, AMD Ryzen 9 7950X), boost::unordered_flat_map was 5.00x faster build+destroy, 2.70x faster find, 4.66x faster churn, and 11.60x faster iterate than std::unordered_map (libstdc++, inferred) on uint64_t keys, with 1.55x-32.9x gains on std::string keys.

## Use it when

- uint64_t or other cheap-to-hash keys, 1-2M+ entries, throughput-bound build/find/churn/iterate workloads
- Whole-container iteration is common — flat layout iterates 11.6x faster than std::unordered_map on u64 keys
- x86-64 (SSE2) or aarch64 (Neon) targets that benefit from SIMD metadata scanning
- Want boost::unordered_map's near-drop-in API but don't need pointer/reference stability across mutation
- Already use Boost, or can add a header-only dependency with no link step

## Skip it when

- Code relies on pointer/reference stability across insert/erase — use boost::unordered_node_map or std::unordered_map
- Memory is tighter than speed: in the same benchmark std::unordered_map had lower peak RSS per u64 entry (45.78 B) than every flat map
- Can't tolerate Boost's transitive include weight — issue #195 flags a large transitive-include graph hurting compile times
- Need concurrent mutation from multiple threads — use boost::concurrent_flat_map instead, unordered_flat_map has no built-in synchronization
- Bulk-loading one flat_map from another already-hashed container via a plain insert loop without reserve() first — open issue #178 documents quadratic insertion in that pattern

## How it is fast

Elements sit in groups of 15 slots backed by a 16-byte metadata word (per-slot reduced hash byte plus an overflow byte); SSE2/Neon SIMD scans the whole metadata word in one op to rule out non-matching slots before touching real elements, with quadratic probing to the next group on overflow (non-SIMD architectures emulate this via bit-interleaving). The library also auto-post-mixes ('avalanches') whatever hash function you supply so a poor-quality hash doesn't degrade open-addressing performance, at a small cost you can opt out of by declaring your hash `is_avalanching`.

## Compared with alternatives

Pick Boost.Unordered when you want one vendor for the whole hash-container family (flat/node/concurrent variants, all header-only) rather than a single map type; abseil's absl::flat_hash_map is faster on these exact numbers (5.99x vs 5.00x build+destroy, 2.43x vs 2.70x find) but pulls in more of the Abseil ecosystem, and ankerl::unordered_dense is a smaller single-header option that wins on pure iteration speed but has no concurrent or pointer-stable variants.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Boost (Boost.Container_hash, Boost.Core, Boost.Config, Boost.Assert and other Boost headers pulled in transitively) |
| **Minimum toolchain** | C++11 (CTAD deduction guides need C++17) |
| **Platforms** | any; SIMD-accelerated on x86-64 (SSE2) and aarch64 (Neon), portable bit-interleaved metadata scan elsewhere |
| **Thread safety** | not documented for unordered_flat_map itself (ordinary container assumption: concurrent reads only); use boost::concurrent_flat_map/node_map for concurrent mutation |
| **Drop-in for the baseline** | partial — explain: std::unordered_map API surface mostly matches, but no pointer/reference stability across insert/erase, begin() is not O(1), erase(iterator) returns a proxy not an iterator, no bucket iteration API, and max_load_factor isn't user-settable |

## Gotchas

- Inserting into a flat_map by iterating another (already hash-ordered) container with plain insert() can degrade to quadratic time; call reserve() first or use the copy constructor instead (open issue boostorg/unordered#178)
- Open addressing is hash-quality sensitive; the library auto post-mixes your hash unless it's tagged `using is_avalanching = std::true_type;`, which skips the safety net for a small speed gain
- erase(iterator) returns a proxy object convertible to an iterator, not an iterator directly — code that assumes the std return type may need adjustment
- value_type must be move-constructible and there's no pointer stability under rehash or node extraction/insertion API (use boost::unordered_node_map if you need those)

## Caveats and trade-offs

Numbers from a third-party harness (unordered_dense's scripts/ab/bench_readme.sh); absolute ns/op in the linked raw CSV doc/bench_readme.csv (rows 'boost' and 'std'), ratios derived. Boost 1.90 tested. Original record mislabelled the CSV 'build' column (inserts only) as build+destroy; the page's build+destroy panel is the CSV 'buildfree' column, where std::unordered_map is 115.31 ns/op (chart shows std at 4.84 relative to unordered_dense). Standard library not named on the page; baseline_stdlib set to libstdc++ by inference (harness calls plain clang++ with no -stdlib flag on Fedora, where clang defaults to libstdc++; page also discusses glibc arenas). Speed only: in the same run std::unordered_map has lower peak RSS per u64 entry (45.78 B) than every flat map. stars_or_usage reflects only the boostorg/unordered module repo, not Boost's install base.

unordered_flat_map is open-addressed, so no pointer/reference stability across insert/erase, unlike Boost's own node-based boost::unordered_map or std::unordered_map; requires reasonably modern C++ (11+).

## Maintenance

Actively maintained core Boost module (last commit 2026-06-17); BSL-1.0 licensed and header-only, so it's trivially vendorable despite the standalone module mirror's low star count — it ships inside every Boost install and is used far more broadly than that number suggests.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** Public harness scripts/ab/bench_readme.sh + scripts/ab/maps.cpp in martinus/unordered_dense runs every map incl. std::unordered_map; page states clang 22.1.8, -O3, Ryzen 9 7950X. Code+compiler+flags+CPU all present, so A holds.
- **Verifier notes:** Tier A confirmed; build+destroy corrected to the buildfree column and iterate ratio fixed from 11.61x to 11.60x. BSL-1.0, 92 stars, last default-branch (develop) commit 2026-06-17.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline_stdlib`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/bench_readme.csv>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/bench-readme-u64.svg>
  - <https://github.com/martinus/unordered_dense/blob/main/scripts/ab/bench_readme.sh>
  - <https://github.com/boostorg/unordered>
- **Sources the enricher read:**
  - <https://github.com/boostorg/unordered>
  - <https://github.com/boostorg/unordered/blob/develop/doc/modules/ROOT/pages/compliance.adoc>
  - <https://github.com/boostorg/unordered/blob/develop/doc/modules/ROOT/pages/structures.adoc>
  - <https://github.com/boostorg/unordered/blob/develop/doc/modules/ROOT/pages/hash_quality.adoc>
  - <https://github.com/boostorg/unordered/issues/178>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/boostorg/unordered`) · [data/wave0-seed/enrich/raw/github_com_boostorg_unordered.json](../../../data/wave0-seed/enrich/raw/github_com_boostorg_unordered.json) (enrichment confidence 0.85)

</details>
