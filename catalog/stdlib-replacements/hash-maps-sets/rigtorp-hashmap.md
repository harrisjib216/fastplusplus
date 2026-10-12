# rigtorp/HashMap

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only open-addressing hash map with backshift deletion, up to \~5x faster than std::unordered_map on delete-heavy workloads.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | In-cache: 24 ns/iter mean (HashMap) vs 67 ns/iter (std::unordered_map), about 2.8x. Out-of-cache: 75 ns/iter (HashMap) vs 408 ns/iter (std::unordered_map), about 5.4x. |
| **Workload** | Delete-heavy loop: look up a random key and erase it if present, otherwise insert it; size_t keys drawn from a uniform int range, 24-byte values, CRC32 hash; working set inside L3 (-c 100000 -i 100000000) and larger than L3 (-c 10000000 -i 1000000000) |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 3900X, Linux 5.8.4-200.fc32.x86_64, isolated core complex (CCX) via isolcpus |
| **Compiler and flags** | gcc (GCC) 10.2.1 20200723 (Red Hat 10.2.1-1); optimization level not stated; CMakeLists.txt adds only -mavx2 plus warning flags to HashMapBenchmark and sets no CMAKE_BUILD_TYPE |
| **Adoption** | 224 stars; cited by Koppl, 'Separate Chaining Meets Compact Hashing' (arXiv 1905.00163, preprint of the 173rd IPSJ SIGAL local proceedings, 2019), which uses it as a benchmark contestant |
| **Last commit** | 2023-09-25 |
| **Links** | [repository](https://github.com/rigtorp/HashMap) · [benchmark](https://github.com/rigtorp/HashMap) |

## Verdict

Self-published benchmark (README + src/HashMapBenchmark.cpp), gcc 10.2.1 on an AMD Ryzen 9 3900X (Fedora, isolcpus-isolated CCX), against libstdc++'s std::unordered_map in a delete-heavy insert-or-erase loop with size_t keys and 24-byte values. In-cache (100K entries): HashMap mean 24 ns/iter vs std::unordered_map 67 ns/iter (\~2.8x). Out-of-cache (10M entries): HashMap 75 ns/iter vs 408 ns/iter (\~5.4x). Optimization flags are not stated (CMakeLists.txt sets no CMAKE_BUILD_TYPE, only -mavx2 and warnings), and it's a single hardware configuration with no independent reproduction.

## Use it when

- Delete-heavy or high-churn workloads (repeated insert+erase of the same keyspace) where backshift deletion avoids the tombstone buildup that degrades linear probing over time
- Keys/values are cheap, default-constructible, and copyable (the benchmark uses size_t keys and a 24-byte POD value), and you can reserve one sentinel value as the 'empty key'
- You want a single-header, zero-dependency container to vendor rather than pull in Abseil/Folly for a hash map
- Latency matters for both cache-resident and larger-than-L3 working sets, and you can tolerate stricter iterator-invalidation and no-destructor-on-erase semantics

## Skip it when

- You need a true drop-in replacement: the constructor signature differs (bucket_count, empty_key) and Key/T must be default constructible, which is also why it's excluded from Martin Ankerl's independent map_benchmark suite (per repo issue #2)
- Values own resources (std::string, std::vector, std::unique_ptr, etc.) where you rely on the destructor running on erase — HashMap does not call destructors on erase
- You need iterator/reference/pointer stability across mutations — every insert, erase, or rehash invalidates them, stricter than std::unordered_map
- You need &gt;50% load factor for memory efficiency, multi-threaded access (thread safety is undocumented), or an actively maintained dependency (last commit 2023-09-25, effectively unmaintained)

## How it is fast

Open addressing with linear probing stores entries directly in a single contiguous std::vector of buckets, avoiding per-node allocation and pointer chasing. On erase it uses backshift deletion (shifting later entries back into the vacated slot) instead of tombstones, so probe sequences stay short even under the paired insert/erase churn in the benchmark. Bucket count is kept a power of two so index computation is a mask (idx & mask) rather than a modulo, and load factor is hard-capped at 50% to bound probe length.

## Compared with alternatives

Pick HashMap when you want the smallest possible dependency (one \~250-line header, no external deps) specifically for delete-heavy/churn workloads where backshift deletion matters; the in-repo numbers show it beating both std::unordered_map and absl::flat_hash_map at that workload. Prefer emhash, ska::flat_hash_map/tsl::robin_map, or absl instead when you need iterator stability, don't want to manage an empty-key sentinel, or want a design that's actually included in independent benchmark suites (Ankerl 2022) and sees ongoing maintenance.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (STL only). The benchmark binary optionally links Abseil and uses x86 CRC32/AVX2 intrinsics plus a Linux huge-page allocator, but none of that is required by the library itself. |
| **Minimum toolchain** | C++14 (CMake target_compile_features cxx_std_14 for the library; the benchmark target additionally requires C++17 and -mavx2) |
| **Platforms** | any (the library is portable, architecture-agnostic C++14); only the benchmark's CRC32 hash, AVX2 flag, and MAP_HUGETLB allocator are x86-64/Linux-specific |
| **Thread safety** | not documented — no synchronization anywhere in the header; assume single-threaded / caller-provided locking |
| **Drop-in for the baseline** | partial: same core API (find/insert/emplace/erase/at/operator[]/iterators) but the constructor requires (bucket_count, empty_key) instead of std::unordered_map's default constructor, Key and T must be default constructible, the empty-key value can never be used as real data, destructors are not run on erase, and iterators invalidate on every modifying operation instead of only on rehash. |

## Gotchas

- A reserved empty-key sentinel is mandatory at construction; using that value as a real key is undefined behavior (only asserted in debug builds)
- Destructors are never invoked on erase — backshift deletion just moves/overwrites slots, so resource-owning values leak until overwritten or the table is destroyed
- Iterators, pointers, and references are invalidated by every insert, erase, or rehash, not just rehashes as in std::unordered_map
- Max load factor is hard-coded to 50%; every insert path calls reserve(size_+1), so the table silently doubles capacity earlier than std::unordered_map would, trading memory for probe length

## Caveats and trade-offs

Optimization flags are not stated, and there is only one hardware configuration. The setup is asymmetric: HashMap and absl use a 2 MB huge-page allocator and HashMap is pre-sized to 2x count buckets, while std::unordered_map uses the default allocator with reserve(count). Self-published. The headline numbers are means; max latencies are HashMap 1082/19026 ns vs std::unordered_map 10299/22422 ns.

Requires a reserved empty-key sentinel value; keys/values must be default constructible; destructors not called on erase; iterators invalidated on all modifying operations.

## Maintenance

Maintenance is stale (last commit 2023-09-25, about to cross into 'abandoned'), but it's MIT-licensed, header-only, and small enough (\~250 lines) to vendor and audit directly rather than depend on for long-term support.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The in-repo benchmark src/HashMapBenchmark.cpp runs against std::unordered_map, and the README states the compiler (gcc 10.2.1) and hardware (Ryzen 9 3900X). The optimization flags are not stated anywhere: CMakeLists.txt adds only -mavx2 plus warning flags and sets no build type. That fails A. It is self-published and has no peer-reviewed or independent run showing the win in text, so it is C.
- **Verifier notes:** The numbers match the README exactly. The downgrade is purely because the flags are unstated and the benchmark is self-published. The last commit (2023-09-25) is days short of 3 years, so it will cross from stale to abandoned very soon. Metadata checks out: MIT, 224 stars.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/rigtorp/HashMap>
  - <https://github.com/rigtorp/HashMap/blob/master/README.md>
  - <https://github.com/rigtorp/HashMap/blob/master/CMakeLists.txt>
  - <https://github.com/rigtorp/HashMap/blob/master/src/HashMapBenchmark.cpp>
  - <https://arxiv.org/abs/1905.00163>
  - <https://arxiv.org/pdf/1905.00163>
- **Sources the enricher read:**
  - <https://github.com/rigtorp/HashMap>
  - <https://github.com/rigtorp/HashMap/blob/master/README.md>
  - <https://github.com/rigtorp/HashMap/blob/master/CMakeLists.txt>
  - <https://github.com/rigtorp/HashMap/blob/master/include/rigtorp/HashMap.h>
  - <https://github.com/rigtorp/HashMap/blob/master/src/HashMapBenchmark.cpp>
  - <https://github.com/rigtorp/HashMap/issues/2>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/rigtorp/hashmap`) · [data/wave1/enrich/raw/github_com_rigtorp_hashmap.json](../../../data/wave1/enrich/raw/github_com_rigtorp_hashmap.json) (enrichment confidence 0.8)

</details>
