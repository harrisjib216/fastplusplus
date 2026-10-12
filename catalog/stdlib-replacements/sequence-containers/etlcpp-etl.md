# ETL static containers (etl::vector, etl::map, etl::unordered_map)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Heap-free, fixed-capacity STL-style containers (vector, map, unordered_map) for embedded C++03+; no maintained speed claim against std.

| | |
|---|---|
| **Beats** | std::unordered_map (the only container with a timing harness); also std::vector and std::map |
| **Claimed result** | Issue #13 (maintainer, 2016-12-31, i7 3.40 GHz, VS2015 /O2, 16 rounds insert-then-erase): std::unordered_map vs etl::unordered_map 10k 26 vs 4 ms, 100k 437 vs 41, 1M 6,386 vs 420, 10M 88,020 vs 4,096 (about 21x); an earlier third-party bx run had ETL slowest (9,690 vs STL 3,573) before the pool rewrite of February 2017 |
| **Workload** | No published measurement. The repo's test/Performance/unordered_map program times 16 rounds of inserting then erasing 10,000,000 sequential uint64_t-&gt;uint16_t entries in std::unordered_map and in etl::unordered_map sized for 10,000,000 entries, printing milliseconds for each, but no results are recorded anywhere in the repo or docs. |
| **Metric** | other |
| **Adoption** | 3.1k stars, 549 forks |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/ETLCPP/etl) |

## Verdict

No speed claim in the README or docs, but GitHub issue #13 holds first-party numbers from the maintainer (Dec 31, 2016; Intel i7 3.40 GHz, Windows 10 x64, Visual Studio 2015 /O2): 16 rounds of insert-then-erase of N sequential uint64_t-&gt;uint16_t keys, std::unordered_map vs etl::unordered_map, 26 vs 4 ms at 10k, 437 vs 41 ms at 100k, 6,386 vs 420 ms at 1M and 88,020 vs 4,096 ms at 10M (about 21x, derived from page data), measured on the then-new pool before its Feb 2017 release, apparently with the in-repo harness (committed the same day, same 16 rounds). Two days earlier a third party (bkaradzic, bx handle_bench) had found ETL the slowest map (ETL 9,690 vs STL 3,573 vs TinySTL 4,534, unitless), which the maintainer traced to the old bitset pool and fixed; no one has re-measured since.

## Use it when

- Firmware or RTOS code where dynamic allocation is banned or must be bounded, and the worst-case element count is known at build time.
- Hard real-time paths that need insert/erase without allocator latency spikes (node pool allocate/release is O(1)).
- Toolchains stuck on C++03 or without a usable STL (Keil, IAR, TI, avr-gcc, Arduino) where you still want map/unordered_map/vector semantics.
- Small, bounded lookup tables with integer keys where a statically sized hash map or AVL map is enough.

## Skip it when

- Host or server code chasing throughput: chained buckets plus a modulo per lookup are not competitive with open-addressing tables; nothing shows ETL beating a modern std::unordered_map replacement.
- Unknown or highly variable sizes: capacity cannot grow, and an unordered_map&lt;K,V,N&gt; reserves N nodes plus N buckets up front (on 64-bit about 16 bytes per bucket and a link pointer per node, used or not).
- Workloads that erase keys in descending order or repeatedly erase the highest-index occupied bucket: each such erase rescans buckets from first to last (O(bucket range)), so with identity-hashed sequential keys a reverse-order erase is quadratic.
- Keys that share low-order bits with a fixed bucket count (e.g. multiples of the bucket count) under the identity integer hash: there is no rehash, so they pile into one chain.

## How it is fast

There is no algorithmic trick; any speed edge comes from never calling malloc/free. Node containers (map, unordered_map) draw nodes from an embedded etl::pool: an intrusive free list threaded through unused slots with lazy initialisation, so allocate and release are O(1) pointer pops. etl::unordered_map is separate chaining over intrusive singly linked buckets indexed by hash % bucket_count with no rehashing; etl::map is an AVL-style balanced binary tree (per-node balance field) on the same pool. etl::hash&lt;uint64_t&gt; on a 64-bit target is the identity function.

## Compared with alternatives

Pick ETL over EASTL's fixed containers or sfl-library's static_vector when you need the whole fixed-capacity family (vector, map, unordered_map, strings, pools) with zero heap fallback and C++03 support on embedded compilers; pick EASTL (published std comparisons) or ankerl::svector / sfl small_vector when you want inline storage that can still spill to the heap, and fast_vector or veque when raw std::vector throughput is the goal.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (optionally uses the STL unless ETL_NO_STL is defined; chrono and print need user-supplied platform hooks) |
| **Minimum toolchain** | C++03 (C++98 badge); CI on GCC and Clang for C++11 through C++26, MSVC; README says tested with VS2022, GCC 12, Clang 14; CMake 3.10+ for the INTERFACE target |
| **Platforms** | any (bare metal, RTOS, desktop); also Arduino, Zephyr, PlatformIO, Conan packages |
| **Thread safety** | not documented; the container and pool code read has no internal synchronisation |
| **Drop-in for the baseline** | partial: std-like member names, but capacity is a template parameter, the types are not std types, there is no allocator parameter, and growth past capacity is an error |

## Gotchas

- Overflow checking depends on macros: etl::vector::push_back is unchecked unless ETL_CHECK_PUSH_POP is defined (the vector doc implies asserts or exceptions suffice), and with no ETL_THROW_EXCEPTIONS/ETL_LOG_ERRORS in an NDEBUG build ETL_ASSERT is a no-op, so inserting into a full unordered_map gets a null node from the pool and dereferences it.
- unordered_map::erase rescans buckets from first to last whenever the erased node sits in the current last bucket; the shipped harness erases in ascending order and never hits this path.
- The only timing harness (test/Performance/unordered_map, Dec 2016, VS2015 v140 project) includes ../../../../src/unordered_map.h and src/ipool.h; the repo has no src/ directory now (code is in include/etl), so it does not build against the current tree without edits.
- That harness favours ETL by construction: identity etl::hash with sequential keys 0..N-1 and N buckets gives one key per bucket walked in memory order, the ETL map is a pre-sized 10M-capacity global while std::unordered_map rehashes as it grows in round 1, the std loop runs first in the same process, and each container is timed once.

## Known shortcomings

- No published numbers; the Windows-only test/Performance/unordered_map harness is crude (std runs first, single timing) and ships no results. Kept at D as a whole-stdlib decomposition seed.
- Enricher: first-party numbers exist in issue #13 (maintainer, 2016-12-31, i7 3.40 GHz, Windows 10 x64, VS2015 /O2, 16 rounds of insert-then-erase, std::unordered_map vs etl: 10k 26 vs 4 ms, 100k 437 vs 41, 1M 6,386 vs 420, 10M 88,020 vs 4,096, about 21x) measured on pre-release pool code after an earlier third-party bx run had ETL slowest (9,690 vs STL 3,573) with the old bitset pool (rewritten February 2017); the harness uses the identity etl::hash&lt;uint64_t&gt; with sequential keys (one key per bucket in memory order, best case), pre-sizes the ETL map while std rehashes in round 1, times once, and no longer builds; unordered_map erase in the last bucket rescans from the first (O(N^2) descending erase); vector::push_back is unchecked unless ETL_CHECK_PUSH_POP; a full unordered_map insert in an NDEBUG build without exceptions dereferences a null pool node. Retiered D to C. Lead: bkaradzic/bx HandleHashMap.

## Caveats and trade-offs

Tier D: the project does not claim to be faster than the std containers; its stated goals are determinism and heap-free operation for embedded targets. A Windows-only timing harness exists (QueryPerformanceCounter, Visual Studio project): https://github.com/ETLCPP/etl/blob/master/test/Performance/unordered_map/unordered_map/unordered_map.cpp, but it ships no results, flags or hardware, so running it is the way to get tier A evidence. Where ETL is faster, the likely cause is avoided heap allocation, which a fixed-capacity container gets by construction; a std::vector with reserve() or a pooled allocator would narrow the gap. Searched the README, docs/containers, docs/blog and test/Performance, plus two WebSearch queries for independent ETL-vs-std timings; none found. The etlcpp.com site was not opened. The harness itself is crude: the std::unordered_map loop runs first in the same process, the etl::unordered_map is a 10,000,000-capacity static global (its storage is pre-sized, while the std map rehashes as it grows in round one), the insert results are unused, and there is a single timing per container with no repetitions. The README states ETL is 'not intended as a full replacement' for the STL. A third WebSearch query (verifier) also found no ETL-vs-std benchmark. [retier] Identity etl::hash&lt;uint64_t&gt; on sequential keys (one key per bucket, best case); ETL map pre-sized while std rehashes in round 1; one timing each; pre-release pool code; harness no longer builds; erase in the last bucket rescans from the first (O(N^2) descending erase); push_back unchecked unless ETL_CHECK_PUSH_POP; full insert without exceptions dereferences a null pool node in NDEBUG builds

Fixed capacity set at compile time and no heap use at all: no malloc, no new, deterministic latency, contiguous storage, memory fully known at build time. Cost: a container cannot grow past its template capacity (overflow goes to the configured ETL error handler or assert), and etl::unordered_map&lt;K,V,MAX_SIZE,MAX_BUCKETS&gt; reserves its whole node pool and bucket array up front. Size-independent i-prefixed base types (ivector, iunordered_map) allow size-erased use. Supports C++03 upward and does not depend on the STL.

## Maintenance

Actively maintained (v20.49.0, last commit 2026-10-04, 3.1k stars, vendored under 3rdparty in the Qt for MCUs 2.1 automotive demo) and MIT-licensed header-only, so copyable; the 2016 issue #13 numbers make the unordered_map claim first-party (tier C at best: CPU model not given, pre-release code, stale harness with an identity-hash best case), while vector and map have no measurement at all.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now C.
- **Tier reason:** No benchmark_url and no published numbers: the README makes no speed claim beyond 'contiguous memory layouts for optimal cache performance', and test/Performance/unordered_map/unordered_map/unordered_map.cpp is a Windows-only harness that prints std and ETL milliseconds but ships no results, flags or hardware. A further WebSearch found no independent ETL-vs-std timing.
- **Retiered** D to C: Enricher (2026-10-12): first-party numbers exist after all. Issue #13 carries the maintainer's 2016-12-31 run (i7 3.40 GHz, Windows 10 x64, VS2015 /O2, 16 rounds of insert-then-erase): std::unordered_map vs etl::unordered_map 10k 26 vs 4 ms, 100k 437 vs 41, 1M 6,386 vs 420, 10M 88,020 vs 4,096 (about 21x), measured on pre-release pool code with an identity hash on sequential keys, a pre-sized ETL map and a single timing; the harness no longer builds and the exact CPU model is not given, so C rather than A.
- **Verifier notes:** Record accurate; harness code matches (16 rounds of insert-then-erase of 10M sequential uint64_t-&gt;uint16_t keys, QueryPerformanceCounter). No numbers anywhere; tier D stays; notable (3.1k stars, 549 forks, last commit 2026-10-04, MIT). Shortcoming: no performance claim or published measurement; determinism, not speed, is the goal.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-73 (wave 1, stdlib decomposition); enricher (wave 1 stdlib seeds, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ETLCPP/etl>
  - <https://github.com/ETLCPP/etl/commits>
  - <https://github.com/ETLCPP/etl/tree/master/test/Performance>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/test/Performance/unordered_map/unordered_map/unordered_map.cpp>
- **Sources the enricher read:**
  - <https://github.com/ETLCPP/etl>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/README.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/library.json>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/library.properties>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/version.txt>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/test/Performance/unordered_map/unordered_map/unordered_map.cpp>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/test/Performance/unordered_map/unordered_map/unordered_map.vcxproj>
  - <https://github.com/ETLCPP/etl/tree/master/test/Performance/unordered_map/unordered_map>
  - <https://github.com/ETLCPP/etl/commits/master/test/Performance/unordered_map/unordered_map/unordered_map.cpp>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/unordered_map.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/intrusive_forward_list.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/hash.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/pool.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/ipool.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/vector.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/map.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/error_handler.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/include/etl/platform.h>
  - <https://github.com/ETLCPP/etl/tree/master/docs>
  - <https://github.com/ETLCPP/etl/tree/master/docs/containers>
  - <https://github.com/ETLCPP/etl/tree/master/docs/containers/maps>
  - <https://github.com/ETLCPP/etl/tree/master/docs/getting-started>
  - <https://github.com/ETLCPP/etl/tree/master/hugo>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/containers/maps/unordered-map.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/containers/maps/map.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/containers/maps/_index.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/containers/vectors/vector.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/getting-started/macros.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/getting-started/compilers.md>
  - <https://raw.githubusercontent.com/ETLCPP/etl/HEAD/docs/getting-started/setup.md>
  - <https://github.com/ETLCPP/etl/issues?q=is%3Aissue+performance>
  - <https://github.com/ETLCPP/etl/issues?q=is%3Aissue+unordered_map>
  - <https://github.com/ETLCPP/etl/issues/13>
  - <https://github.com/ETLCPP/etl/issues/803>
  - http://www.etlcpp.com/benchmarks.html (ENOTFOUND, not reachable)
  - WebSearch: etlcpp.com benchmarks unordered_map STL ETL ms pool (no benchmark page found; showed ETL bundled in Qt for MCUs 2.1 docs)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/etlcpp/etl`) · [data/wave1/enrich/raw/github_com_etlcpp_etl.json](../../../data/wave1/enrich/raw/github_com_etlcpp_etl.json) (enrichment confidence 0.8)

</details>
