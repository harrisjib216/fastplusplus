# icy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> C++23 consteval perfect-hash map/set for fixed keys; \~1.6-1.8x faster string_view hits than std::unordered_map in the author's benchmark.

| | |
|---|---|
| **Beats** | std::map, std::unordered_map, std::set, std::unordered_set |
| **Claimed result** | std::string_view find() at N=1024: icy 3.228 'cycles/op' vs std::map 44.393, std::unordered_map 5.278, tsl::robin_map 4.595, sorted-vector+lb 23.987. Versus std::unordered_map/set the gain is 1.64-1.77x (map) and 1.69-1.72x (set) for string_view keys. For int64 keys it is only 1.02-1.25x (map) and 1.36-2.39x (set), and tsl::robin_set beats icy at int64 N=512. It is up to \~13.8x faster than std::map and \~14.9x faster than std::set (all ratios derived from page data). The README's own summary claims '1.5\~2x' vs std::unordered_map/set 'with all optimizations enabled'. |
| **Workload** | map/set find() and iteration for std::string_view and std::int64_t keys at N=16/512/1024, comparing icy::map/set (consteval-built, open-addressed) against std::map, std::unordered_map/set, tsl::robin_map/set, and a sorted-vector binary search. |
| **Metric** | latency |
| **Hardware** | Apple M4 Max |
| **Compiler and flags** | Compiler not stated; bench/CMakeLists.txt forces -O3 -DNDEBUG -march=native on bench targets (overriding the -O level of the README's RelWithDebInfo config); the Makefile bench path uses cc -std=c++23 -O3 -march=native -fconstexpr-steps=4000000000 |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/romainaugier/icy) · [benchmark](https://github.com/romainaugier/icy#benchmark) |

## Verdict

The author ran an all-hit microbenchmark on an Apple M4 Max (compiler and stdlib unstated; -O3 -march=native; the timer counts CNTVCT_EL0 ticks, not core cycles, so only the ratios mean anything). With hash-only matching (ICY_OPTIMIZE_KEY_CMP), string_view find() over 16-1024 keys took 2.8-3.2 ticks/op, against 4.9-5.3 for std::unordered_map/set (1.64-1.77x) and 13-44 for std::map/set (up to \~14.9x). int64 find gained only 1.02-1.25x (map) and 1.36-2.39x (set) over std::unordered_\*.

## Use it when

- A fixed set of string keywords, commands or enum names (tens to about 1000 keys) is looked up on a hot path where you would otherwise use a `static const std::unordered_map<std::string_view, T>`.
- You are replacing a static std::map/std::set used only for lookup: the author measured 13.6 vs 3.07 ticks/op at 16 string keys and 44.4 vs 3.23 at 1024.
- You need lookups inside constant expressions (for example `static_assert(keywords.contains("if"))`) or want no runtime initialization and no static-initialization-order problems.
- You want a bounded per-lookup cost: every find() reads at most two table slots, whatever the key set looks like.
- The codebase is already on C++23, preferably Clang, which is the toolchain the author's Makefile uses.

## Skip it when

- Keys are not known at compile time, or you need insert/erase or to change mapped values: both keys and values are immutable.
- int64-key maps: the author's own data shows only 1.02-1.25x over std::unordered_map, and tsl::robin_set beats icy::set at N=512 (0.673 vs 0.777). Integer tables also use 4-32x N slots.
- String lookups on untrusted input with ICY_OPTIMIZE_KEY_CMP enabled, because a hash-only match can report a false hit. With the macro off, which is the safe mode, the speedup has not been measured.
- Pre-C++23 code, or key sets well above about 1000: compile time and constexpr step limits become the constraint.
- Code that needs a mature dependency: the repo was created 2026-09-11, is at v0.2.0 with 0 stars and one author, and CI has built and run no tests since the v0.2 rewrite ('ninja: no work to do', 'No tests were found!!!').

## How it is fast

Construction runs a CHD-style (compress-hash-displace) search, named chd_result/build_perfect_hash in the code. Keys are split into buckets, buckets are placed largest-first, and each bucket gets a displacement seed (up to 4096 tries under up to 128 global seeds) that moves its keys into empty slots. A lookup is one hash, one bucket-slot read and at most one more slot read, with no chains or probe loops. String keys use a constexpr wyhash port, and each slot stores the key's 64-bit hash, so most misses are rejected without touching the key; ICY_OPTIMIZE_KEY_CMP skips the key compare entirely. Integer keys hash by identity plus multiply-shift (Fibonacci hashing) into deliberately sparse tables, and icy::set keeps the key inside the slot to avoid a second array access.

## Compared with alternatives

Pick icy over frozen only if you are on C++23, want the lowest per-hit cost on string_view keys, and can accept an experimental one-author project. frozen (C++14, stable, in maintenance mode, also offers ordered sets/maps and a constinit map with mutable values) remains the safer default. Pick it over Kronuz constexpr-phf when you need string keys or stored values, since that library handles integer keys only; icy has no head-to-head benchmark against any sibling (including ConstexprCore/perfect_hash's 1.08 billion queries/s claim).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only; the benchmarks use the Tessil robin-map git submodule) |
| **Minimum toolchain** | C++23 (`if consteval`, constexpr std::vector and std::sort during consteval construction). The CI matrix names GCC 14, Clang 18, AppleClang (macos-14) and MSVC 2022, but it last compiled tests on v0.1 (2026-09-12). GCC 13 and Clang 17 were dropped from CI. Large key sets need raised constexpr limits (Clang -fconstexpr-steps, GCC -fconstexpr-ops-limit). |
| **Platforms** | Any target with a C++23 compiler; no SIMD or intrinsics are needed (the 64x64 multiply uses __uint128_t, _umul128 on MSVC x64, or a portable fallback). The v0.2.0 benchmarks ran only on an Apple M4 Max. |
| **Thread safety** | Not documented. The object is immutable after consteval construction and every member function is const noexcept, so concurrent reads need no locking. |
| **Drop-in for the baseline** | partial — read-only find()/contains()/iteration match std::unordered_map/set usage, but construction goes through consteval make() with N in the type, keys and values are immutable, there is no operator[]/at()/count(), no custom hash or equality template parameters, no ordered queries, and iteration is in initializer order, not std::map's sorted order |

## Gotchas

- The README's own usage example defines ICY_OPTIMIZE_KEY_CMP. With it, string-key find() returns a hit when only the 64-bit hash matches, so a non-member key that collides returns the wrong entry. wyhash runs with a fixed public secret and seed 0. The exhaustive tests only check sequential and generated misses against 64 keys. Integer keys always get a full compare.
- The macro changes the body of inline member functions. Set it project-wide as a compiler flag, not with a #define in some files, or different translation units get different definitions (an ODR violation).
- The build search runs entirely in the constant evaluator. Hundreds of keys can exceed the default constexpr step budgets, and a failed search is a compile error ('could not build a perfect hash within ICY_MAX_BUILDING_ROUNDS rounds'). Raise ICY_MAX_BUILDING_ROUNDS or the compiler's step limit.
- Some README text is stale or broken. It says 'table_size == 2 \* N ... linear probing', but the code uses hash-and-displace and sizes integer tables at next_pow2(16N+1) up to 64 keys and next_pow2(4N+1) above, so an int64 set of 1024 keys has 8192 16-byte slots (128 KiB), and sets also store every key twice. The CMake bench recipe points at a missing bench.cpp, and tests/CMakeLists.txt passes an undefined \${bench_name}, so the Makefile (Clang-only flags) is the working build path.

## Caveats and trade-offs

bench_find.cpp defines ICY_OPTIMIZE_KEY_CMP. With it, icy's string-key find() checks only the stored 64-bit hash and skips key equality, while the std containers do full key compares, so the string_view comparison is not like for like. All queries are hits; there is no miss workload. On aarch64 the timer is CNTVCT_EL0 (generic-timer ticks, not core cycles), so only the ratios are meaningful. No compiler is named. The README's CMake bench recipe is broken (bench/CMakeLists.txt adds a nonexistent bench.cpp, and there is no icy_bench target), so only the Makefile path builds. icy's near-zero iteration numbers come from a constexpr table and are plausibly constant-folded. Brand-new project (created 2026-09-11, 0 stars), author's own microbenchmark.

Best for small key sets; larger sets (&gt;=1000) need -fconstexpr-steps tuning. Requires C++23 and consteval support. An ICY_OPTIMIZE_KEY_CMP macro skips key comparison in find() for extra speed at the cost of relying purely on hash equality.

## Maintenance

Active but brand-new (created 2026-09-11, v0.2.0 and last commit 2026-09-16, 0 stars, one author). The BSD-3-Clause single header is easy to vendor but should be treated as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README benchmark tables match the quoted numbers (string_view N=1024 map find: icy 3.228, std::map 44.393, std::unordered_map 5.278, tsl 4.595, sorted vector 23.987), and they run against std::map, std::unordered_map and std::set directly. The code is public (bench/bench_find.cpp) and the flags are in bench/CMakeLists.txt and the Makefile, but no compiler is stated (only 'M4 Max, 64 Go'), so the tier stays C.
- **Verifier notes:** Downgraded only because the claim was overstated: the tier stays C, but the README's '1.5\~2x vs std::unordered_map/set' does not hold for int64 map find (1.02-1.25x), and the string results rely on skipping key comparison. Metadata matches: BSD-3-Clause, 0 stars, not a fork, last commit 2026-09-16. baseline_stdlib stays [] because OS and stdlib are not stated (M4 Max suggests libc++, but it is not stated).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/romainaugier/icy>
  - <https://github.com/romainaugier/icy#benchmark>
  - <https://github.com/romainaugier/icy/blob/main/bench/bench_find.cpp>
  - <https://github.com/romainaugier/icy/blob/main/bench/CMakeLists.txt>
  - <https://github.com/romainaugier/icy/blob/main/CMakeLists.txt>
  - <https://github.com/romainaugier/icy/blob/main/Makefile>
  - <https://github.com/romainaugier/icy/blob/main/include/icy.hpp>
  - <https://github.com/romainaugier/icy/blob/main/.github/workflows/ci.yml>
- **Sources the enricher read:**
  - <https://github.com/romainaugier/icy>
  - <https://github.com/romainaugier/icy#benchmark>
  - <https://github.com/romainaugier/icy/blob/main/include/icy.hpp>
  - <https://github.com/romainaugier/icy/blob/main/bench/bench_find.cpp>
  - <https://github.com/romainaugier/icy/blob/main/bench/bench_contains.cpp>
  - <https://github.com/romainaugier/icy/blob/main/bench/CMakeLists.txt>
  - <https://github.com/romainaugier/icy/blob/main/CMakeLists.txt>
  - <https://github.com/romainaugier/icy/blob/main/Makefile>
  - <https://github.com/romainaugier/icy/blob/main/.gitmodules>
  - <https://github.com/romainaugier/icy/blob/main/.github/workflows/ci.yml>
  - <https://github.com/romainaugier/icy/blob/main/.github/workflows/release.yml>
  - <https://github.com/romainaugier/icy/blob/main/tests/CMakeLists.txt>
  - <https://github.com/romainaugier/icy/blob/main/tests/test_map.cpp>
  - <https://github.com/romainaugier/icy/blob/main/tests/test_set_exhaustive_string.cpp>
  - <https://github.com/romainaugier/icy/blob/main/tests/test_set_exhaustive_int.cpp>
  - <https://github.com/romainaugier/icy/blob/main/profiling/profiling.cpp>
  - <https://github.com/romainaugier/icy/commits/main>
  - <https://github.com/romainaugier/icy/commit/a21ed2d>
  - <https://github.com/romainaugier/icy/releases>
  - <https://github.com/romainaugier/icy/pulls?q=is%3Apr>
  - <https://github.com/romainaugier/icy/actions/runs/35136869308>
  - <https://github.com/romainaugier/icy/actions/runs/35134256324>
  - <https://github.com/romainaugier/icy/actions/runs/34665666925>
  - <https://github.com/romainaugier/icy/actions/runs/34723077436>
  - <https://github.com/serge-sans-paille/frozen>
  - <https://github.com/Kronuz/constexpr-phf>
  - <https://github.com/ConstexprCore/perfect_hash>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/romainaugier/icy`) · [data/wave1-phf/enrich/raw/github_com_romainaugier_icy.json](../../../data/wave1-phf/enrich/raw/github_com_romainaugier_icy.json) (enrichment confidence 0.8)

</details>
