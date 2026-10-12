# folly F14 (F14ValueMap)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> SIMD 14-way probing hash map (F14) in Facebook's Folly library; 2-4x faster build/find/churn, 16x faster iteration than std::unordered_map.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | u64 keys (folly::F14ValueMap vs std::unordered_map): 3.97x faster build+destroy (29.05 vs 115.31 ns/op; inserts alone 2.81x, 27.98 vs 78.66), 1.72x faster find (33.58 vs 57.89 ns/op), 2.63x faster churn (91.34 vs 240.49 ns/op), 16.35x faster iterate (1.30 vs 21.29 ns/element); std::string keys: 1.48x build+destroy (228.41 vs 337.53), 1.73x find, 1.62x churn, 29.7x iterate (derived from page data) |
| **Workload** | uint64_t- and std::string-keyed maps, 1-2 million entries; build+destroy, find, churn, iterate ops measured via unordered_dense's third-party benchmark harness, F14ValueMap variant specifically. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X |
| **Compiler and flags** | clang 22.1.8, -O3 -DNDEBUG -std=c++20 (per scripts/ab/bench_readme.sh), transparent huge pages (madvise), process pinned to one core, Fedora 44 |
| **Adoption** | 30.5k stars; used extensively in Meta/Facebook production C++ services |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/facebook/folly) · [benchmark](https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md) |

## Verdict

Read directly from martinus/unordered_dense's bench_readme.csv (clang 22.1.8, -O3 -DNDEBUG -std=c++20, libstdc++, AMD Ryzen 9 7950X, 1-2M entries): for u64 keys folly::F14ValueMap beat std::unordered_map 3.97x on build+destroy (29.05 vs 115.31 ns/op; inserts alone 2.81x, 27.98 vs 78.66), 1.72x on find (33.58 vs 57.89), 2.63x on churn (91.34 vs 240.49), and 16.35x on iteration (1.30 vs 21.29 ns/element); for std::string keys the wins were smaller on build/find/churn (1.48x/1.73x/1.62x) but iteration was 29.7x. std::unordered_map had lower peak RSS per u64 entry (45.78 B) than every SIMD/flat map tested, including F14ValueMap.

## Use it when

- u64 or other small trivially-copyable keys where build/insert and find throughput matter more than reference stability (F14ValueMap or F14FastMap).
- Iteration-heavy workloads: F14ValueMap iterates 16x faster (u64) to 30x faster (std::string) than std::unordered_map on this harness because there's no per-node pointer chasing.
- High churn workloads (caches, dedup tables, repeated insert/erase cycles) where std::unordered_map's tombstone-driven rehashes hurt.
- You need std::unordered_map-compatible reference/iterator stability but still want a speed win over it: use F14NodeMap specifically (1.28x faster build+destroy, still much slower than F14ValueMap in this benchmark).
- You're already building/linking Folly (or accept doing so) on x86-64/aarch64 with a C++20 toolchain.

## Skip it when

- You want a header-only, dependency-free drop-in: F14 requires building and linking libfolly, whose manifest lists \~13 external deps (boost, gflags, glog, libdwarf, libevent, libsodium, fast_float, fmt, lz4, openssl, snappy, zstd, xz) plus Linux-only libaio/libiberty/libunwind.
- Targeting WebAssembly: an open folly issue (#1973) reports F14 is slower and more memory-hungry than std::unordered_map there.
- Less-common platforms: open build-failure issues on ppc64le (#1838) and other powerpc targets (#2128) show threading/endianness and compile rough edges; README's platform list (Linux/macOS/Windows/iOS, x86-32/64, ARM) is not the CI-tested set.
- You default to F14ValueMap/F14VectorMap/F14FastMap but need reference/iterator stability across mutation — only F14NodeMap provides that; the others may invalidate references on any insert.
- Exception safety must be contractually guaranteed: an open upstream issue (#2308, filed 2024, still open) states F14's exception safety is undocumented.

## How it is fast

Each table position is a 14-slot chunk; F14 packs a 1-byte hash 'tag' per key into a 16-byte SIMD vector (SSE2 on x86_64, NEON on aarch64) so one vector compare filters up to 14 candidate slots per probe, letting the table run at a 12/14 max load factor with a \~1.04 average probe length on hits. Collisions resolve via double hashing with per-chunk 'overflow' reference counts standing in for tombstones, so insert/erase churn doesn't force the periodic full-table rehashes that tombstone-based open addressing needs to reclaim slots. F14ValueMap further stores entries inline in the chunk instead of behind a per-node heap allocation, which is what drives its build and iteration advantage over std::unordered_map's pointer-chasing.

## Compared with alternatives

On this exact harness F14ValueMap is the slowest of the four SIMD hash maps compared for u64 keys: abseil's flat_hash_map (19.26 ns/op buildfree), Boost.Unordered's flat_map (23.04), and ankerl::unordered_dense (23.80) all beat F14ValueMap's 29.05, and similarly on find. Pick F14 when you're already building/linking Folly and want the ValueMap-vs-NodeMap choice between raw speed and std-compatible reference stability in one library, or need Folly's built-in heterogeneous/transparent lookup; pick a single-header sibling (unordered_dense, robin_hood) when you want the speed without Folly's \~13-dependency build.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | boost, gflags, glog, libdwarf, libevent, libsodium, fast_float, fmt, lz4, openssl, snappy, zstd, xz (googletest for tests only); Linux additionally needs libaio, libiberty, libunwind |
| **Minimum toolchain** | C++20 (CMakeLists.txt pins CMAKE_CXX_STANDARD 20), CMake 3.14+, gcc/clang/MSVC |
| **Platforms** | x86-64 (SSE2, a non-optional baseline ISA feature) and aarch64 (NEON) are the vectorized fast paths; a non-SIMD fallback exists but is untested by this benchmark. WASM and some powerpc targets have open correctness/perf issues. |
| **Thread safety** | not documented beyond the same non-synchronized, single-writer-or-multiple-readers model as std::unordered_map; no built-in locking |
| **Drop-in for the baseline** | partial — F14NodeMap matches std::unordered_map's reference/iterator stability and is a safe substitute; F14ValueMap, F14VectorMap, and F14FastMap are not (no reference stability, no bucket API, max_load_factor is a no-op) |

## Gotchas

- F14ValueMap/F14VectorMap/F14FastMap may rehash before evaluating an insert's arguments, so code like map.insert(k2, map[k1]) is unsafe with them, per F14.md (same caveat as dense_hash_map and absl::flat_hash_map).
- Debug and ASAN builds intentionally randomize iteration order and inject extra rehashes to expose stability bugs, so two identically-constructed maps can iterate in different orders even in the same process/build.
- clear() frees all backing memory once a table has ever held &gt;100 keys (std only requires O(size())), so a clear-and-refill loop on a table that grew large will repeatedly reallocate rather than reuse capacity.
- Only F14NodeMap provides std::unordered_map's reference/iterator stability; the other three variants can move or invalidate elements on any insert.

## Caveats and trade-offs

Numbers from a third-party harness (unordered_dense's scripts/ab/bench_readme.sh); absolute ns/op in the linked raw CSV doc/bench_readme.csv (rows 'f14-value' and 'std'), ratios derived. Folly snapshot 65749da, not HEAD. For u64 keys F14FastMap resolves to F14ValueMap (F14Map.h: sizeof(pair&lt;const K,M&gt;) &lt; 24), so these numbers also describe F14FastMap; with std::string keys F14FastMap is F14VectorMap (separate 'f14-vector' CSV row). F14NodeMap is the closer drop-in. Original record mislabelled the CSV 'build' column (inserts only) as build+destroy; the page's build+destroy panel is the CSV 'buildfree' column, where std::unordered_map is 115.31 ns/op (chart shows std at 4.84 relative to unordered_dense). Standard library not named on the page; baseline_stdlib set to libstdc++ by inference (harness calls plain clang++ with no -stdlib flag on Fedora, where clang defaults to libstdc++; page also discusses glibc arenas). Speed only: in the same run std::unordered_map has lower peak RSS per u64 entry (45.78 B) than every flat map. 

F14ValueMap stores values inline so it lacks std::unordered_map's iterator/reference stability on rehash; F14NodeMap is the stability-preserving variant, at a speed cost; three storage policies plus F14FastMap auto-selector add API/tuning surface versus a single std::unordered_map.

## Maintenance

Actively maintained (commits current as of 2026-09-24, 30.5k stars, heavy internal Meta production use) under Apache-2.0, but folly gives no ABI-compatibility guarantee across commits and its own README recommends static linking and pinning a version rather than tracking main.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** Public harness scripts/ab/bench_readme.sh + scripts/ab/maps.cpp in martinus/unordered_dense runs every map incl. std::unordered_map; page states clang 22.1.8, -O3, Ryzen 9 7950X. Code+compiler+flags+CPU all present, so A holds.
- **Verifier notes:** Tier A confirmed; build+destroy corrected to the buildfree column and the F14FastMap caveat fixed (for u64 it is F14ValueMap). Apache-2.0, 30,544 stars, last commit 2026-09-24.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline_stdlib`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/bench_readme.csv>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/bench-readme-u64.svg>
  - <https://github.com/martinus/unordered_dense/blob/main/scripts/ab/bench_readme.sh>
  - <https://github.com/facebook/folly>
  - <https://github.com/facebook/folly/blob/main/folly/container/F14Map.h>
- **Sources the enricher read:**
  - <https://github.com/facebook/folly>
  - <https://github.com/facebook/folly/blob/main/folly/container/F14Map.h>
  - <https://github.com/facebook/folly/blob/main/folly/container/F14.md>
  - <https://github.com/facebook/folly/blob/main/folly/container/detail/F14Table.h>
  - <https://github.com/facebook/folly/blob/main/CMakeLists.txt>
  - <https://github.com/facebook/folly/blob/main/build/fbcode_builder/manifests/folly>
  - <https://github.com/facebook/folly/issues/2308>
  - <https://github.com/facebook/folly/issues/1973>
  - <https://github.com/facebook/folly/issues/1838>
  - <https://github.com/facebook/folly/issues/2128>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/bench_readme.csv>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/facebook/folly`) · [data/wave0-seed/enrich/raw/github_com_facebook_folly.json](../../../data/wave0-seed/enrich/raw/github_com_facebook_folly.json) (enrichment confidence 0.85)

</details>
