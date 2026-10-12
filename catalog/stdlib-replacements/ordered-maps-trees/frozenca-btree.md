# frozenca/BTree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Ordered maps and trees](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception OR BSL-1.0` · 🟡 stale

> Header-only C++20 B-tree (BTreeSet/Map) with optional AVX-512 SIMD search, \~5x faster than std::set on int64 keys.

| | |
|---|---|
| **Beats** | std::set |
| **Claimed result** | 1M random std::int64_t (fanout 64, SIMD): insert 175.547ms vs std::set 907.104ms, lookup 197.75ms vs 961.859ms, erase 211.274ms vs 990.027ms (\~4.7-5.2x, derived from page data); without SIMD (fanout 64): 204.187/221.049/249.832ms (\~4.0-4.4x, derived from page data); 1M std::string (length 1-50, fanout 64): insert 1519.62ms vs 1662.92ms, lookup 1188.33ms vs 1666.16ms, erase 1570.44ms vs 1639.79ms (\~1.04-1.4x, derived from page data). |
| **Workload** | insert/lookup/erase of 1,000,000 random std::int64_t keys, and separately 1,000,000 std::string keys (length 1-50), into a balanced-tree set, 200 repeats per measurement |
| **Metric** | throughput |
| **Compiler and flags** | gcc 11.2, -O3 |
| **Adoption** | 249 stars |
| **Last commit** | 2024-10-29 |
| **Links** | [repository](https://github.com/frozenca/BTree) · [benchmark](https://github.com/frozenca/BTree/blob/main/README.md) |

## Verdict

Author-run benchmark (gcc 11.2, -O3, libstdc++, CPU model not stated, 200 repeats) inserting/looking up/erasing 1M random std::int64_t keys: frozenca::BTreeSet (fanout 64, SIMD) averaged 175.5/197.8/211.3ms vs std::set's 907.1/961.9/990.0ms (\~4.7-5.2x); the same test without the SIMD path averaged 204.2/221.0/249.8ms (\~4.0-4.4x). For 1M std::string keys (length 1-50) the gap narrows to \~1.04-1.4x (e.g. insert 1519.6ms vs std::set's 1662.9ms).

## Use it when

- Ordered set/map of primitive keys (int64, float) where insert/lookup/erase throughput matters more than per-node iterator stability, on x86-64 with AVX-512 for the full \~5x gain
- Need operations std::set lacks: O(log n) k-th/rank queries (kth/order), range enumerate()/erase_range(), or tree join()/split()
- Want an out-of-core ordered container: DiskBTreeSet/DiskBTreeMap memory-maps a file, which std::set cannot do at all
- Already on a C++20 toolchain (gcc 11.2+/MSVC 19.32+) and willing to vendor a small, header-only, currently unmaintained library
- Bulk-loading sorted or near-sorted ranges via insert_range(), which the README documents as faster than repeated single inserts

## Skip it when

- Code relies on std::set/map's iterator/reference stability across insert and erase elsewhere in the container — any insert/erase here can invalidate iterators anywhere in the tree
- Keys are std::string or other non-trivial-comparison types: measured speedup drops to \~1.04-1.4x because the SIMD path only covers signed integers/floats
- Need thread safety: concurrency is explicitly unsupported ('thread safety is not guaranteed'), no lock-free path implemented
- Stuck on C++17 or earlier, or need an actively maintained/widely-used dependency: last commit 2024-10-29, 249 stars, effectively a single-maintainer project with no open issues but no recent activity either
- Profiling debug builds: full-tree O(n) sanity checks run on every insert/erase/join/split unless a macro is disabled (per issue #3), so debug-build timings are misleading

## How it is fast

Wider nodes (fanout 64 default, tunable) mean far fewer cache-line-missing pointer chases per operation than a red-black tree's one-key-per-node layout, and in-node key search can use either linear or binary search depending on a tunable threshold. For signed integer/float keys on AVX-512 hardware, an optional SIMD intrinsics path (macro-toggled, credited to Algorithmica's Static B-Trees) vectorizes the in-node comparison; the README's own figures show fanout-64 without SIMD is already \~4.0-4.4x over std::set, with SIMD adding roughly another 10-20% on top.

## Compared with alternatives

Pick this over cpp-btree or tlx::btree when you specifically want std::set-compatible rank queries (kth/order), range enumerate()/erase_range(), tree join()/split(), or the disk-backed memory-mapped variant, none of which those siblings offer; prefer cpp-btree or tlx::btree instead if you need broader compiler/standard support, since this one hard-requires C++20 and its full headline speedup needs AVX-512.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for library use; Catch2 only to build the test suite (per vcpkg.json) |
| **Minimum toolchain** | C++20; README states verified against gcc 11.2 and MSVC 19.32. "There are currently no plans to support C++17 and earlier." Apple Clang compile errors were reported and fixed via PRs (issue #7) but Clang isn't in the README's stated verified-compiler list |
| **Platforms** | x86-64 for the optional AVX-512 SIMD path; base header-only containers are architecture-agnostic. POSIX and Windows both supported for the memory-mapped disk variant |
| **Thread safety** | not thread-safe; README: 'Currently, thread safety is not guaranteed. Lock-free support is the first TODO' |
| **Drop-in for the baseline** | partial — same STL-like member surface as std::set/map (insert, lower_bound, iterators, structured bindings for maps) but different invalidation semantics: any insert/erase can invalidate iterators anywhere in the tree, unlike std::set's per-node stability, so it's a source-level swap requiring an invalidation-rule audit, not a behavior-identical drop-in |

## Gotchas

- Any insert or erase can invalidate iterators anywhere in the tree, because a B-tree node holds multiple keys, unlike std::set's one-key-per-node stability guarantee
- SIMD path only helps signed integer/floating-point keys and requires both a macro toggle and AVX-512 hardware; without it the README's own non-SIMD numbers show \~4.0-4.4x rather than \~5x
- DiskBTreeSet/DiskBTreeMap requires std::trivially_copyable key/value types with alignment at least that of a pointer, and its memory-mapped pool cannot be extended after creation without invalidating all allocator pointers
- Debug builds run O(n) full-tree sanity checks on every insert/erase/join/split (confirmed in closed issue #3, 'Performance issue'); only release-build numbers are meaningful

## Caveats and trade-offs

CPU model never stated ('in my machine'); the headline int64 numbers use the optional SIMD path, which the README says needs AVX-512 (non-SIMD is \~4.0-4.4x); int64 speedup (\~5x) far exceeds the string-key speedup (\~1.04-1.4x); README license (Apache-2.0 with LLVM exception or BSL-1.0) differs from the repo's only license file, LICENSE.md, which holds plain Apache-2.0 text and is what GitHub detects.

any insert/erase invalidates iterators (nodes hold multiple keys, unlike std::set's per-node stability); requires C++20; default fanout 64, tunable; optional AVX-512 SIMD path for signed integer/float keys; also offers a disk-backed/memory-mapped variant not present in std::set

## Maintenance

Stale: last commit 2024-10-29, effectively single-maintainer, 249 stars, all 15 filed issues closed with none open; but it's header-only and small enough to vendor as-is if C++20 support is acceptable. License is plain Apache-2.0 per LICENSE.md and GitHub's own detection, despite the README additionally advertising an Apache-2.0-with-LLVM-exception/BSL-1.0 dual license.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section gives gcc 11.2, -O3, 200 repeats, and averages/stdev vs std::set, with test/perftest.cpp and test/perftest_string.cpp in the repo, but no CPU model ('in my machine') and the README says the code was only 'similar with test/perftest.cpp', so C.
- **Verifier notes:** All numbers verified in README; added the non-SIMD figures and the AVX-512 caveat, and marked the ratios as derived. Metadata: GitHub spdx Apache-2.0, 249 stars, last commit 2024-10-29 (stale), not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/frozenca/BTree/blob/main/README.md>
  - <https://github.com/frozenca/BTree>
  - <https://github.com/frozenca/BTree/blob/main/LICENSE.md>
- **Sources the enricher read:**
  - <https://github.com/frozenca/BTree/blob/main/README.md>
  - <https://github.com/frozenca/BTree>
  - <https://github.com/frozenca/BTree/blob/main/LICENSE.md>
  - https://github.com/frozenca/BTree/issues (all 15, incl. #3 'Performance issue', #4, #6, #7, #11)
  - <https://github.com/frozenca/BTree/blob/main/vcpkg.json>
  - <https://github.com/frozenca/BTree/blob/main/CMakeLists.txt>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/frozenca/btree`) · [data/wave1/enrich/raw/github_com_frozenca_btree.json](../../../data/wave1/enrich/raw/github_com_frozenca_btree.json) (enrichment confidence 0.6)

</details>
