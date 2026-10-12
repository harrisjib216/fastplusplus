# ConstexprCore/perfect_hash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++23 compile-time perfect-hash set/map for fixed string keys; author measures \~10x std::unordered_map throughput on a 6-key set.

| | |
|---|---|
| **Beats** | std::unordered_map, gperf, frozen::unordered_map, absl::flat_hash_map, pthash, ankerl::unordered_dense, if/else chain |
| **Claimed result** | 1.08 billion queries/s for this library vs 0.23 (gperf), 0.22 (kronuz::phf), 0.16 (frozen::unordered_map), 0.14 (absl::flat_hash_map / pthash), 0.10 (std::unordered_map / ankerl::dense_hash_map), 0.19 (naive) -- roughly 10x std::unordered_map and 4x the next-fastest competitor |
| **Workload** | Billion-queries-per-second table for the URL-protocol key set (http, https, ftp, ws, wss, file); a broader benchmark suite also covers S&P 100 tickers, C++ keywords, HTTP headers, MIME types, letters a-z, and JS reserved words, each queried hit-only/miss-only/mixed. |
| **Metric** | throughput |
| **Hardware** | Apple M4 |
| **Compiler and flags** | Compiler not stated for the headline table; top-level CMakeLists.txt defaults CMAKE_BUILD_TYPE to Release, C++23 |
| **Adoption** | 17 stars |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/ConstexprCore/perfect_hash) · [benchmark](https://github.com/ConstexprCore/perfect_hash#ridiculously-fast) |

## Verdict

On an Apple M4, the README's URL-protocol table (6 keys) reports 1.08 billion queries/s (\~0.93 ns per lookup) vs 0.10 for std::unordered_map, 0.16 for frozen::unordered_map and 0.23 for gperf. The repo's harness times 200,000 shuffled lookups and keeps the fastest of 300 runs; the compiler, standard library and hit/miss mix for that table are not stated, and the bench builds as CMake Release by default. An older committed baseline run (hardware and compiler not stated) shows a smaller gap against std::unordered_map: 1.97 vs 13.32 ns on hits (\~6.8x), 3.33 vs 4.45 ns on misses (\~1.3x), and 5.75 vs 13.08 ns mixed (\~2.3x).

## Use it when

- Classifying short tokens from a small, fixed vocabulary on a hot path: HTTP methods or headers, URL schemes, MIME types, language keywords, string-to-enum parsing.
- Streams where most lookups hit: the committed baseline shows the widest gap on all-hit queries (URL protocols 1.97 ns vs 13.32 ns for std::unordered_map; S&P 100 tickers 2.89 ns vs 13.55 ns).
- Tables that must exist with no startup cost and no allocation: the table is a constexpr object and can be queried inside static_assert.
- Large generated symbol lists (hundreds to a few thousand keys) through the wide container, if seconds of compile time are acceptable. The author reports 1.7 ns vs 7.6 ns for absl::flat_hash_map&lt;std::string_view, int&gt; on 5,581 Nasdaq tickers (Apple M3 Max).
- Projects that already build as C++23 on x86-64, AArch64 or LoongArch64 (CI covers GCC 14, Clang 18, AppleClang, MSVC 2022 and GCC 14 cross-compiled for LoongArch64).

## Skip it when

- Keys that are not known at compile time, or tables that change at runtime. There is no insert or erase; use a runtime hash map.
- Streams dominated by misses (negative filters) on some key sets. In the committed baseline, C++ Keywords all-miss lookups took 6.91 ns vs 3.49 ns for absl::flat_hash_map and 4.68 ns for ankerl, and URL-protocol misses were only \~1.3x faster than std::unordered_map (3.33 vs 4.45 ns).
- Codebases that cannot use C++23. The headers use `if consteval`, and the string keys are class-type template arguments.
- Builds where compile time matters and key sets are large. The 5,581-key map takes \~5 s of compile time and needs -fconstexpr-steps (Clang) or -fconstexpr-ops-limit (GCC) raised. Precompiled headers are the documented fix.
- Risk-averse production use: v0.2.0, repo created March 2026, and every performance number is first-party. Issue #29 (open) argues the gperf baseline could be tuned better, and issue #28 (open) reported that the CMake dependency failed to clone.

## How it is fast

For up to 255 keys, a gperf-style generator runs at compile time. It picks a minimal set of byte positions that tell the keys apart, then solves per-position association values so that h = len + sum(asso[pos][key[pos]]) never collides. If the key set cannot be split that way, it falls back to hash-and-displace (CHD-style), then to a seeded whole-key hash. A lookup is a few small table loads, a power-of-two mask, and one branchless compare against inline key bytes: overlapping 2-byte loads for keys of 4 bytes or less, and page-guarded, masked 16-byte NEON/SSE2/LSX loads for longer keys. Past 255 keys or 254-byte keys, a 'wide' container uses a PTHash-like scheme: one multiply per 64-bit key lane, a per-bucket pilot (displacement) table, and a packed-lane compare, with small integer values stored inside the key word.

## Compared with alternatives

Pick this over frozen (C++14; ordered and unordered containers; integer or string keys) and Kronuz constexpr-phf (C++17; integer keys only, so strings must be hashed first) when you have string keys, a C++23 compiler and a hot lookup path. On the URL-protocol set, this repo's own benchmark gives frozen::unordered_map 0.16 and kronuz::phf 0.22 billion queries/s against 1.08 for this library. Pick it over code generators such as gperf, triehash or strager/perfect-hash-tables when you want no separate generation step in the build.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the amalgamated singleheader/perfect_hash.h, which bundles fixed_string.h. The CMake/FetchContent route pulls ConstexprCore/useful_abstractions at an unpinned `master` (the repo is public now; issue #28 reported that the clone failed). |
| **Minimum toolchain** | C++23 (CMake 3.20+ for the CMake route). CI covers GCC 14, Clang 18, AppleClang on a macOS 15 runner, MSVC 2022, and GCC 14 cross-compiled for LoongArch64. |
| **Platforms** | x86-64 (SSE2 compare path), AArch64 (NEON path), LoongArch64 (LSX path, tested under QEMU), scalar fallback elsewhere. The seeded whole-key-hash tier assumes little-endian, and big-endian execution was not tested. |
| **Thread safety** | Not documented. Tables are immutable constexpr objects and every lookup is a const noexcept member function, so concurrent reads need no locking. |
| **Drop-in for the baseline** | partial — only for read-only, string-keyed tables fixed at compile time. The API is contains()/lookup() returning std::optional, with no insert, erase, iterators or operator[], and generation errors (such as duplicate keys) are compile errors. |

## Gotchas

- SIMD key compares read a whole 16-byte chunk, which can go past the end of the query string. A page guard keeps the read inside the same 4 KB page. These functions opt out of ASan (no_sanitize("address")) and assume pages of at least 4 KB.
- Every classic table embeds MAX_POSITIONS x 256 bytes of association tables (4 KB with the default of 16), however many positions are actually used. Shrink it with -DCONSTEXPRCORE_MAX_POSITIONS.
- make_perfect_map takes each value as a non-type template argument (kv&lt;"GET", Method::GET&gt;), so values must be structural types such as enums or integers. Other value types need the array-based wide factories.
- The factories pick the wide container only above 255 keys or for keys of 255+ bytes. Opting in explicitly for small sets can help all-hit streams (S&P 100: 1.77 to 1.32 ns on an M3 Max) but lost 17-30% on C++ Keywords on a Xeon with GCC 14, so measure first. Wide sets with keys of 16+ bytes also reject keys that differ only by trailing NUL bytes.

## Caveats and trade-offs

No compiler is named for the headline billion-queries/s table (only 'Apple M4 processor'), and the table does not say whether it is the hits, misses or mixed workload. The bench builds as CMake Release by default, so it is capped at C. The committed perf_viz/baseline_results.json run (hardware and compiler unstated) shows a smaller gap for URL Protocols: hits 1.97 ns vs 13.32 ns for std::unordered_map (\~6.8x); misses 3.33 vs 4.45 ns (\~1.3x); mixed 5.75 vs 13.08 ns (\~2.3x) (derived from page data). Other M3 Max figures in the README (wide container, ticker sets) compare only against absl::flat_hash_map and a trie, not std::unordered_map. Young project (repo created 2026-03-04, 17 stars), first-party numbers only, not independently reproduced.

Wide container needed past 255 keys or 254-byte keys (different code path, whole-key multiplicative hash). Requires C++23. Compile time grows with key-set size (raising -fconstexpr-steps/-fconstexpr-ops-limit is needed for large sets, e.g. \~5s for 5,581 keys).

## Maintenance

Actively maintained (last commit and v0.2.0 release on 2026-09-13; commits mostly from GitHub users lemire and FranciscoThiesen); MIT and shipped as one self-contained header that is easy to vendor, but young (created 2026-03-04, 17 stars).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'Ridiculously fast' table matches the claim exactly: 1.08 billion queries/s vs gperf 0.23, kronuz::phf 0.22, frozen 0.16, absl 0.14, pthash 0.14, naive 0.19, std::unordered_map 0.10 and ankerl 0.10, with 'four times' and 'ten times' stated in the text. The benchmark code is public (benchmarks/bench_protocol.cpp, which uses lemire/counters and a CMake default Release build), but the only platform detail for that table is 'Apple M4', with no compiler named, so the evidence stays at C.
- **Verifier notes:** All metadata matches: MIT, 17 stars, not a fork, last commit 2026-09-13. docs/pr30_review.md states the platform in full (M3 Max, AppleClang 15, -O3), but it only compares the library's own revisions, not the baselines, so it does not qualify for A. baseline_stdlib stays [] because no OS or stdlib is stated (libc++ on macOS is likely but not stated).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ConstexprCore/perfect_hash>
  - <https://github.com/ConstexprCore/perfect_hash#ridiculously-fast>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/benchmarks/bench_protocol.cpp>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/benchmarks/bench_common.h>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/CMakeLists.txt>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/perf_viz/baseline_results.json>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/perf_viz/README.md>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/docs/pr30_review.md>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/perf_viz/pr30_review_results.json>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/.github/workflows/ci.yml>
- **Sources the enricher read:**
  - <https://github.com/ConstexprCore/perfect_hash>
  - <https://github.com/ConstexprCore/perfect_hash#ridiculously-fast>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/include/ConstexprCore/perfect_hash.h>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/include/ConstexprCore/wide_perfect_hash.h>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/include/ConstexprCore/detail/gperf_generator.h>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/include/ConstexprCore/detail/wide_generator.h>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/include/ConstexprCore/detail/simd16.h>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/include/ConstexprCore/detail/neon_compare.h>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/include/ConstexprCore/detail/sse2_compare.h>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/include/ConstexprCore/perfect_hash_version.h>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/CMakeLists.txt>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/benchmarks/bench_protocol.cpp>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/benchmarks/bench_common.h>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/docs/pr30_review.md>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/perf_viz/README.md>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/perf_viz/baseline_results.json>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/.github/workflows/ci.yml>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/.github/workflows/loongarch64.yml>
  - <https://github.com/ConstexprCore/perfect_hash/blob/main/tests/test_edge_cases.cpp>
  - <https://github.com/ConstexprCore/perfect_hash/issues>
  - <https://github.com/ConstexprCore/perfect_hash/issues/28>
  - <https://github.com/ConstexprCore/perfect_hash/issues/29>
  - <https://github.com/ConstexprCore/perfect_hash/pulls>
  - <https://github.com/ConstexprCore/perfect_hash/releases>
  - <https://github.com/ConstexprCore/perfect_hash/graphs/contributors>
  - <https://github.com/ConstexprCore/useful_abstractions>
  - <https://github.com/serge-sans-paille/frozen>
  - <https://github.com/Kronuz/constexpr-phf>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/constexprcore/perfect_hash`) · [data/wave1-phf/enrich/raw/github_com_constexprcore_perfect_hash.json](../../../data/wave1-phf/enrich/raw/github_com_constexprcore_perfect_hash.json) (enrichment confidence 0.78)

</details>
