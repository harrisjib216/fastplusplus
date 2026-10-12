# sparsepp (spp::sparse_hash_map, greg7mdp/sparsepp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Header-only open-addressing hash map/set beating std::unordered_map on memory and, per two independent suites, speed.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | Ankerl 2022, an independent suite with normalized runtimes and the same hash for both maps (the verifier computed the ratios std::unordered_map / spp from the page's table data): geometric mean over all tests 1.98x (mumx) and 2.03x (robin_hood::hash); number find 2.35-2.51x; string find 1.52-1.82x; random insert & erase 1.18-1.31x. With identity std::hash, spp times out in the random insert & erase and number-find tests. Tessil 2017 shootout raw CSV (Clang 5.0 with libstdc++, 200K-3M entries, ratios computed by the verifier): successful lookups 1.11-3.31x faster; misses 1.15-5.60x faster; inserts 0.61-1.47x (slower on string keys). The author's bench.md (graphs only) says insert is 'as fast as the two std::unordered_map implementations', lookup is 'faster than all other alternatives, except for dense_hash_map', and delete is 'outperformed only by dense_hash_map'. |
| **Workload** | std::pair&lt;uint64_t,uint64_t&gt; entries inserted in random order into an initially empty, non-preallocated container; random insert, random lookup (known-present hits plus a 10%-present-probability miss set), and delete, up to \~70-100M entries |
| **Metric** | throughput |
| **Hardware** | Ankerl 2022: Intel i7-8700 locked at 3200 MHz, Manjaro Linux. (Author's bench.md: VirtualBox VM with 5.8GB RAM, Ubuntu written as '14.02'.) |
| **Compiler and flags** | Ankerl 2022: clang++ 13, -O3 -march=native. (Author's bench.md: g++ 4.8.4 and Boost 1.55, flags not stated.) |
| **Adoption** | 1311 stars |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/greg7mdp/sparsepp) · [benchmark](https://martin.ankerl.com/2022/08/27/hashmap-bench-01/) |

## Verdict

Two independent third-party suites (not the author's own graphs) show spp::sparse_hash_map beating libstdc++'s std::unordered_map: Ankerl 2022 (clang++13, -O3 -march=native, Intel i7-8700) measured geometric-mean speedups of 1.98-2.03x depending on hash choice, with number-find up to 2.51x, but spp timed out on integer insert/erase/find when using an unmixed identity hash. Tessil's 2017 shootout (Clang 5.0 with libstdc++, 200K-3M entries) measured 1.11-3.31x faster successful lookups and 1.15-5.60x faster misses, with inserts ranging 0.61-1.47x (slower than std::unordered_map on string keys).

## Use it when

- Memory-constrained C++ workloads (embedded, large in-memory indexes) where per-entry overhead or resize memory spikes from std::unordered_map/dense_hash_map are the bottleneck
- Integer or string key/value hash tables in the hundreds-of-thousands to \~100M entry range, matching the benchmarked workload
- Projects on pre-C++11 or older MSVC/g++ toolchains that can't take the C++11 requirement of greg7mdp/parallel-hashmap
- Throughput-oriented insert/lookup/erase workloads, not strict latency SLAs, with no need for concurrent writers
- Need built-in binary serialize()/unserialize() of the whole table to a file or stream

## Skip it when

- Peak throughput matters most: google::dense_hash_map beats sparsepp on insert, lookup, and delete in the author's own bench.md
- Any C++11+ toolchain is available: the author's README now recommends greg7mdp/parallel-hashmap (or gtl) instead of sparsepp
- Code holds long-lived references or pointers into the map across insert()/erase() — sparsepp invalidates them more aggressively than std::unordered_map
- Code uses a sparse_hash_map/set after moving from it — moved-from tables segfault on further use (issue #83, open, unresolved)
- Hash quality is uncertain (e.g. an unmixed identity hash on integer keys) — spp degrades badly or times out per Ankerl 2022

## How it is fast

Uses Google sparsehash's 'sparsetable' layout: slots are grouped (SPP_GROUP_SIZE, 32 or 64) and each group carries a bitmap (group_bm_type in spp.h) marking which slots are occupied, so mostly-empty regions cost almost nothing to store. Open addressing itself avoids std::unordered_map's per-node allocation and pointer chasing. The README says this layout also keeps the resize memory spike small compared to a plain open-addressing table, though the resize algorithm itself wasn't inspected this session. Integer keys get a built-in bit-mixing default hash to avoid the pathological slowdown that sequential/identity-hashed keys cause on non-present lookups.

## Compared with alternatives

Pick sparsepp over google::dense_hash_map when the final table size is unknown and you can't absorb dense_hash_map's larger resize memory spike; pick it over tsl::robin_map/ska::flat_hash_map/emhash mainly when stuck on a pre-C++11 toolchain, since for any C++11+ project the author's own README recommends parallel-hashmap (not sparsepp) over those newer designs too.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | Works with C++03; C++11 features (move semantics, initializer lists) auto-detected and used if the compiler supports them. Tested on VS2010-2015, g++, clang++. |
| **Platforms** | Windows, Linux, macOS; x86/x64, no SIMD required. Compiler/platform detection macros derived from Boost for portability. |
| **Thread safety** | Follows std library container rules: concurrent reads on one table from multiple threads are safe; if one thread writes to a table, all other reads/writes to that same table must be externally synchronized; separate table instances are fully independent (documented in README). |
| **Drop-in for the baseline** | partial — same STL-style interface as std::unordered_map/set, but erase()/insert() invalidate iterators and value references more aggressively, and a moved-from table is left broken (open bug) rather than empty. |

## Gotchas

- Moved-from sparse_hash_map/set is left in an inconsistent state; calling find() or other operations on it segfaults (issue #83, open as of 2026-09-23; author's own workaround suggestion is to switch to parallel-hashmap)
- insert()/erase() can invalidate references and pointers to stored values, unlike std::unordered_map where references survive unless a rehash occurs
- Default integer hash does bit-mixing to dodge sequential-key pathologies; a user-supplied hash with similar low-order bits across keys needs the SPP_MIX_HASH macro or collisions increase
- Copy construction/assignment is slow relative to the baseline (per verification caveats)

## Caveats and trade-offs

In Ankerl 2022, spp times out with identity std::hash on integer-key insert/erase and find tests, so it is sensitive to hash quality. Its copy is slow, and its memory use is about 3x lower than std::unordered_map. The author's bench.md is a graph-only write-up from about 2016 on a VM. The README now recommends greg7mdp/parallel-hashmap instead of sparsepp.

Slower than google::dense_hash_map on all three operations tested; the author's README now recommends greg7mdp/parallel-hashmap (or gtl) over sparsepp for C++11+ compilers; sparsepp is optimized for low peak memory during resize rather than raw speed

## Maintenance

Actively maintained (last commit 2026-09-19, BSD-3-Clause, 1311 stars, not a fork or archived) but the author's own README now steers users to greg7mdp/parallel-hashmap for any C++11+ project, calling it a better speed/memory trade-off than sparsepp.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** The author's bench.md alone is only tier C: its results are graphs, the code snippet is partial and the flags are not stated. Two independent third-party suites include spp::sparse_hash_map and show it beating libstdc++ std::unordered_map: Ankerl 2022 (martinus/map_benchmark; clang++ 13 -O3 -march=native; i7-8700) and Tessil's 2017 shootout. That keeps it at B.
- **Retiered** B to A: Independent Ankerl 2022 suite: code martinus/map_benchmark src/maps/greg7mdp_spp_sparse_hash_map vs src/maps/std_unordered_map, clang++ 13, -O3 -march=native, Intel i7-8700 locked at 3200 MHz. map_benchmark.js geomean std::unordered_map/spp = 1.98x (mumx), 2.03x (robin_hood::hash).
- **Verifier notes:** Metadata checks out: BSD-3-Clause (the LICENSE text is the 3-clause BSD, while GitHub reports NOASSERTION), 1311 stars, last commit 2026-09-19, not a fork, not archived. benchmark_url now points to the independent Ankerl 2022 suite, because the original bench.md would only support tier C. Ankerl's page labels the license 'modified MIT', but the repo LICENSE file is BSD-3-Clause.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/greg7mdp/sparsepp>
  - <https://github.com/greg7mdp/sparsepp/blob/master/bench.md>
  - <https://github.com/greg7mdp/sparsepp/blob/master/LICENSE>
  - <https://github.com/greg7mdp/sparsepp/blob/master/README.md>
  - <https://martin.ankerl.com/2022/08/27/hashmap-bench-01/>
  - <https://martin.ankerl.com/files/2022/map_benchmark.js>
  - <https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html>
  - <https://tessil.github.io/other/hopscotch_map_benchmark_raw_results.csv>
- **Sources the enricher read:**
  - <https://github.com/greg7mdp/sparsepp>
  - <https://github.com/greg7mdp/sparsepp/blob/master/README.md>
  - <https://github.com/greg7mdp/sparsepp/blob/master/sparsepp/spp_config.h>
  - <https://github.com/greg7mdp/sparsepp/blob/master/sparsepp/spp.h>
  - <https://github.com/greg7mdp/sparsepp/blob/master/CHANGELOG.md>
  - <https://github.com/greg7mdp/sparsepp/issues/83>
  - <https://github.com/greg7mdp/sparsepp/issues?q=bug>
  - <https://github.com/greg7mdp/sparsepp/issues?q=performance>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/greg7mdp/sparsepp`) · [data/wave1/enrich/raw/github_com_greg7mdp_sparsepp.json](../../../data/wave1/enrich/raw/github_com_greg7mdp_sparsepp.json) (enrichment confidence 0.7)

</details>
