# abseil (absl::flat_hash_map, Swiss tables)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> SwissTable-based hash map beating std::unordered_map on build, find, churn, and iteration speed.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | u64 keys (absl::flat_hash_map vs std::unordered_map): 5.99x faster build+destroy (19.26 vs 115.31 ns/op; inserts alone 4.25x, 18.50 vs 78.66), 2.43x faster find (23.82 vs 57.89 ns/op), 3.52x faster churn (68.23 vs 240.49 ns/op), 8.28x faster iterate (2.57 vs 21.29 ns/element); std::string keys: 1.76x build+destroy (192.04 vs 337.53), 1.85x find, 1.70x churn, 24.8x iterate (derived from page data) |
| **Workload** | uint64_t- and std::string-keyed maps, 1-2 million entries; build+destroy, find, churn (erase+insert), and iterate ops measured via unordered_dense's third-party benchmark harness. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X |
| **Compiler and flags** | clang 22.1.8, -O3 -DNDEBUG -std=c++20 (per scripts/ab/bench_readme.sh), transparent huge pages (madvise), process pinned to one core, Fedora 44 |
| **Adoption** | 18.1k stars; used in Chromium, TensorFlow, and widely at Google |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/abseil/abseil-cpp) · [benchmark](https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md) |

## Verdict

Benchmarked by unordered_dense's third-party harness (scripts/ab/bench_readme.sh) against std::unordered_map on libstdc++, clang 22.1.8, -O3 -DNDEBUG -std=c++20, AMD Ryzen 9 7950X: absl::flat_hash_map is 5.99x faster build+destroy, 2.43x faster find, 3.52x faster churn, and 8.28x faster iterate on uint64_t keys (1.76x-24.8x across ops on std::string keys), while carrying roughly 1.11x the resident memory of std::unordered_map — a gap the benchmark authors attribute partly to glibc allocator arena retention rather than the map's own footprint.

## Use it when

- uint64_t or small POD keys where build+destroy, find, or iteration dominate: 5.99x/2.43x/8.28x faster than std::unordered_map respectively on this benchmark.
- std::string-keyed maps needing faster iteration (24.8x) or build+destroy (1.76x) than std::unordered_map.
- Codebases already depending on Abseil (absl::Hash, absl::string_view) where adding one more absl:: type has no extra dependency cost.
- Iteration-heavy or lookup-heavy workloads on x86-64 or aarch64 where cache-friendly probing matters.
- General-purpose 'default hash map' choice, which is Abseil's own stated recommendation, when pointer/reference stability is not required.

## Skip it when

- Code that needs pointer/reference stability across insert/rehash — use absl::node_hash_map or std::unordered_map's node-based stability instead.
- Exception-safety requirements: flat_hash_map is explicitly documented as not exception-safe.
- Crossing dynamically-loaded library (.so/.dll) boundaries — unsupported because absl::Hash values are randomized per DSO.
- Untrusted or adversarial key input: absl::Hash is not a cryptographic hash, and open issue #2171 (opened 2026-09-23) shows fixed string pairs that collide for every seed, a hash-flooding-style risk.
- Insert-then-mostly-erase workloads: capacity only shrinks on rehash()/clear(), so tombstones from erase() bloat iteration cost (O(capacity), not O(size)).

## How it is fast

SwissTable: an open-addressing table with quadratic probing over groups of slots, where a separate control-byte array stores a 7-bit hash fragment (H2) per slot and SIMD-style group instructions (SSE-like on x86, bit tricks on other architectures) scan a whole group at once to reject non-matches before touching slot memory. The control-byte array is dense and cache-friendly, packing more logical slots per cache line than a node-based table, and a small-object optimization keeps tiny tables entirely inline, avoiding allocation.

## Compared with alternatives

Pick abseil when you're already in the Abseil ecosystem or want a Google-maintained library with the widest deployment footprint (Chromium, TensorFlow); its u64 numbers (5.99x build+destroy, 8.28x iterate) sit close to boost::unordered_flat_map (5.00x/similar) and unordered_dense (4.84x/13x) on this harness. unordered_dense's own analysis of the same run notes boost::unordered_flat_map beats absl on u64 find and churn (absl scores 0.81x relative on both) — pick boost or unordered_dense instead if lookup/churn latency or a lighter, header-only dependency matters more than ecosystem fit.

## Integration

| | |
|---|---|
| **Form** | source-drop / static lib (built via Bazel or CMake; not a single header) |
| **Dependencies** | none beyond the C++ standard library (absl/base itself has no dependency on other Abseil code) |
| **Minimum toolchain** | C++17 (per README); CMake 3.16+ if using the CMake build |
| **Platforms** | x86 (SIMD-style group scan) with a portable bit-trick fallback for other architectures such as aarch64, per raw_hash_set.h; any platform with a C++17 compiler and Bazel or CMake |
| **Thread safety** | not documented in the headers read this session |
| **Drop-in for the baseline** | partial — explain: same O(1) find/insert/erase API shape as std::unordered_map, but weaker iterator/pointer stability (invalidated on rehash and move), requires CopyConstructible keys and MoveConstructible values, erase(iterator) returns void, and constructors take a reservation size instead of a bucket count. |

## Gotchas

- rehash() and move invalidate all iterators, pointers, and references — std::unordered_map keeps references stable on rehash, flat_hash_map does not.
- Not exception-safe (stated directly in flat_hash_map.h's header comment).
- Iteration is O(capacity), not O(size); heavy erase() churn slows down begin()/++iterator, and capacity never shrinks except on rehash()/clear().
- Open issue #2171 (filed 2026-09-23, unresolved as of this writing): absl::Hash has fixed string-pair inputs that collide under every seed — worth checking if keys are attacker-controlled.

## Caveats and trade-offs

Numbers come from a third-party harness (unordered_dense's scripts/ab/bench_readme.sh), not abseil's own repo; absolute ns/op are in the page's linked raw CSV doc/bench_readme.csv (rows 'absl' and 'std'), ratios derived. Original record mislabelled the CSV 'build' column (inserts only) as build+destroy; the page's build+destroy panel is the CSV 'buildfree' column, where std::unordered_map is 115.31 ns/op (chart shows std at 4.84 relative to unordered_dense). Standard library not named on the page; baseline_stdlib set to libstdc++ by inference (harness calls plain clang++ with no -stdlib flag on Fedora, where clang defaults to libstdc++; page also discusses glibc arenas). Speed only: in the same run std::unordered_map has lower peak RSS per u64 entry (45.78 B) than every flat map. Abseil release tested was LTS 20250814, not HEAD.

SwissTable open addressing gives no pointer/reference stability on rehash or erase, unlike std::unordered_map's node-based stability; resident memory is roughly on par with std (CSV 'rss' row: absl 1.11x vs std 0.94x-1.06x depending on metric).

## Maintenance

Actively maintained by Google with a 'live-at-head' philosophy (last commit 2026-09-24) plus LTS releases for teams that can't track head; Apache-2.0, 18.1k stars, used at Chromium/TensorFlow/Google scale — mature and well-tested, but requires a Bazel or CMake build rather than a drop-in single header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** Public harness scripts/ab/bench_readme.sh + scripts/ab/maps.cpp in martinus/unordered_dense runs every map incl. std::unordered_map; page states clang 22.1.8, -O3, Ryzen 9 7950X. Code+compiler+flags+CPU all present, so A holds.
- **Verifier notes:** Tier A confirmed; build+destroy figure corrected (was the inserts-only column) and string-key results added. Metadata (Apache-2.0, 18,139 stars, last commit 2026-09-24, not archived) matches.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline_stdlib`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/bench_readme.csv>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/bench-readme-u64.svg>
  - <https://github.com/martinus/unordered_dense/blob/main/scripts/ab/bench_readme.sh>
  - <https://github.com/abseil/abseil-cpp>
- **Sources the enricher read:**
  - <https://github.com/abseil/abseil-cpp>
  - <https://github.com/abseil/abseil-cpp/blob/main/absl/container/flat_hash_map.h>
  - <https://github.com/abseil/abseil-cpp/blob/main/absl/container/internal/raw_hash_set.h>
  - <https://github.com/abseil/abseil-cpp/blob/main/CMakeLists.txt>
  - <https://github.com/abseil/abseil-cpp/issues/2171>
  - <https://github.com/abseil/abseil-cpp/issues?q=flat_hash_map+performance>
  - <https://github.com/abseil/abseil-cpp/issues?q=hash+flooding>
  - <https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/abseil/abseil-cpp`) · [data/wave0-seed/enrich/raw/github_com_abseil_abseil_cpp.json](../../../data/wave0-seed/enrich/raw/github_com_abseil_abseil_cpp.json) (enrichment confidence 0.85)

</details>
