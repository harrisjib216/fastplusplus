# emhash (ktprime/emhash: emhash5/6/7/8 + emilib)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only open-addressing C++ hash table family; emhash7 beats std::unordered_map on insert/find/erase/iterate at 10M elements.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | emhash7 vs std::unordered_map (10M elements, integer keys, AMD 5800H/Windows 10/GCC 11.3; times, lower is better, units not labeled in the table): insert 66.0 vs 295 (\~4.5x), find-hit 16.9 vs 33.0 (\~2x), find-miss 18.1 vs 52.0 (\~2.9x), erase 20.4 vs 293 (\~14x), iterate 0.74 vs 62.6 (\~85x) |
| **Workload** | 10M elements, integer keys (key width not stated): insert, find-hit, find-miss, erase, and iterate; separate 0.999 load-factor test (1M+ pre-sized buckets) that compares emhash variants only, with no std::unordered_map |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5800H, Windows 10 |
| **Compiler and flags** | GCC 11.3 (Windows 10), -O3 -march=native -std=c++17 (stated in docs/PERFORMANCE_TRACKING.md for this same table; bench/Makefile uses -O3 -DNDEBUG -march=native) |
| **Adoption** | 732 stars |
| **Last commit** | 2026-09-05 |
| **Links** | [repository](https://github.com/ktprime/emhash) · [benchmark](https://github.com/ktprime/emhash/blob/master/docs/performance.md) |

## Verdict

On an AMD Ryzen 7 5800H / Windows 10, GCC 11.3 (-O3 -march=native -std=c++17) build, emhash7 beat std::unordered_map (libstdc++) at 10M integer-key elements: insert \~4.5x (66.0 vs 295), find-hit \~2x (16.9 vs 33.0), find-miss \~2.9x (18.1 vs 52.0), erase \~14x (20.4 vs 293), and iterate \~85x (0.74 vs 62.6). These are the project's own docs/performance.md numbers, reproducible via bench/ebench but not independently re-run for this entry.

## Use it when

- Mixed insert/find/erase workloads on integer or POD keys where throughput close to hand-tuned open addressing matters (emhash7)
- Need a load factor above 0.9 (up to 0.999) without the clustering/degradation open addressing usually shows at that density
- Iteration-heavy hot paths over the whole map/set (emhash7/emhash8), since the flat array scan beats std::unordered_map's node chasing by an order of magnitude
- Want a header-only, dependency-free drop-in (copy one .hpp) rather than adding a build dependency
- Input keys are trusted/internal, not adversarially chosen

## Skip it when

- Code holds long-lived references or pointers into the map across inserts — open addressing invalidates them on rehash; std::unordered_map does not
- Keys come from untrusted/adversarial input: emhash7/8 don't cap probe-sequence length by default, which SECURITY.md flags as a hash-flooding DoS risk unless you enable EMH_SAFE_HASH or switch to an emilib EMH_SAFE_PSL variant
- Multiple threads write concurrently without your own locking — emhash provides no internal synchronization
- You want independently reproduced numbers rather than the vendor's own benchmark (emhash's table is self-measured on one Windows/GCC config, not verified here against Ankerl 2022 or Allan 2024 methodology)
- Very large value types where rehash-driven moves are costly and you haven't wrapped them in unique_ptr

## How it is fast

emhash7 stores key-value pairs inline in one contiguous array plus a separate bitmask for fast empty-slot scanning, and repairs the bucket chain on erase instead of leaving tombstones, so mixed insert/erase workloads don't degrade even at load factor 0.999. Iteration is a straight scan of that array, which is why it beats std::unordered_map's pointer-chasing linked-node layout by roughly 85x on the 10M-element iterate benchmark. The emilib variants instead use Swiss-table-style SIMD group probing with a 1-byte H2 tag per bucket to filter most candidates before a full key comparison.

## Compared with alternatives

Pick emhash over rigtorp::HashMap, ska::flat_hash_map, or tsl::robin_map/hopscotch_map when you need a load factor up to 0.999 without tombstone-driven degradation on mixed insert/erase workloads, or want a matched family (emhash6/7/8) tuned per access pattern instead of one fixed design. Pick a sibling instead when you want a single implementation whose speedup was measured by an independent, cross-library suite (e.g. Ankerl 2022) rather than the vendor's own benchmark.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (wyhash is bundled in config.hpp; pass -DEMH_NO_BUILTIN_WYHASH to supply your own) |
| **Minimum toolchain** | C++17 (some examples use C++20); GCC, Clang, or MSVC |
| **Platforms** | Windows, Linux, macOS; x86-64 and ARM64 (Apple M1/M2). emhash5-8 are scalar (no SIMD requirement); emilib variants add SSE2/AVX2/AVX-512 group probing where available |
| **Thread safety** | Not thread-safe. Concurrent writes require an external mutex; concurrent read-only access (find/contains/count) with no active writer is safe (per docs/usage_notes.md) |
| **Drop-in for the baseline** | partial — operator[], find, insert, emplace, erase, reserve, begin/end, load_factor, etc. match std::unordered_map's signatures, but there is no reference/iterator stability guarantee, no node handle, and bucket()/bucket_size() require the EMH_STATIS build flag |

## Gotchas

- emhash7/8 do not cap probe-sequence length by default; SECURITY.md calls this a hash-flooding DoS risk on untrusted keys. Mitigate with EMH_SAFE_HASH (\~10% overhead) or an emilib EMH_SAFE_PSL variant
- Any insert that triggers a rehash invalidates all existing references and iterators, unlike std::unordered_map's node-based stability
- Erasing inside a plain range-for is undefined behavior; use the iterator-returning erase(it) or erase_if() instead
- Some thirdparty/emilib variants (e.g. emilib2ss) can degrade into a full table scan under an all-keys-collide attack; the maintained include/emilib/emihmap2.hpp (emilib2::HashMap) is not the affected fork, but pick emilib2o/emilib2s for untrusted input regardless

## Caveats and trade-offs

Numbers come from the project's own benchmark and were not independently reproduced. docs/performance.md does not label units or name the program that produced the table; PERFORMANCE_TRACKING.md points to bench/ebench. Only one hardware/compiler configuration (Windows/MinGW, so libstdc++). emhash is also a contestant in Martin Ankerl's (2022) and Jackson Allan's (2024) independent benchmarks, which were not used for these numbers.

Multiple variants (emhash5/6/7/8, emilib1-4) trade iteration speed, erase behavior (tombstones vs none), and memory layout differently; open addressing means no pointer/reference stability; the 0.999 load-factor mode is non-standard behavior most peer libraries don't support

## Maintenance

Actively maintained (last commit 2026-09-05, v1.1.0) and MIT-licensed; header-only, so a single .hpp such as hash_table7.hpp can be vendored with no external dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/performance.md has a table (AMD 5800H / Windows 10 / GCC 11.3) that includes std::unordered_map. docs/PERFORMANCE_TRACKING.md repeats the same table, gives the build flags as -O3 -march=native -std=c++17, and says to reproduce it with bench/ebench. bench/ebench.cpp benchmarks std::unordered_map as "stl_hash" and is built by bench/Makefile (-O3 -DNDEBUG -march=native).
- **Verifier notes:** All numbers match the page exactly. The only gap was the flags, which docs/PERFORMANCE_TRACKING.md fills. The high-load-factor section has no std baseline. Metadata checks out: MIT, 732 stars, last commit 2026-09-05, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ktprime/emhash>
  - <https://github.com/ktprime/emhash/blob/master/docs/performance.md>
  - <https://github.com/ktprime/emhash/blob/master/docs/PERFORMANCE_TRACKING.md>
  - <https://github.com/ktprime/emhash/blob/master/README.md>
  - <https://github.com/ktprime/emhash/blob/master/bench/README.md>
  - <https://github.com/ktprime/emhash/blob/master/bench/Makefile>
  - <https://github.com/ktprime/emhash/blob/master/bench/ebench.cpp>
  - <https://github.com/ktprime/emhash/blob/master/bench/comprehensive_bench.cpp>
- **Sources the enricher read:**
  - <https://github.com/ktprime/emhash>
  - <https://github.com/ktprime/emhash/blob/master/README.md>
  - <https://github.com/ktprime/emhash/blob/master/docs/performance.md>
  - <https://github.com/ktprime/emhash/blob/master/docs/PERFORMANCE_TRACKING.md>
  - <https://github.com/ktprime/emhash/blob/master/docs/usage_notes.md>
  - <https://github.com/ktprime/emhash/blob/master/docs/design.md>
  - <https://github.com/ktprime/emhash/blob/master/docs/migration_guide.md>
  - <https://github.com/ktprime/emhash/blob/master/SECURITY.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ktprime/emhash`) · [data/wave1/enrich/raw/github_com_ktprime_emhash.json](../../../data/wave1/enrich/raw/github_com_ktprime_emhash.json) (enrichment confidence 0.85)

</details>
