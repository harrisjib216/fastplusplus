# SIMD Quad search (Lemire blog benchmark)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Searching](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C++` · `no license` · 🟢 active

> SIMD quaternary-interpolation search over sorted 16-bit arrays in 16-element blocks; beats std::binary_search on Roaring-Bitmap-style containers.

| | |
|---|---|
| **Beats** | std::binary_search |
| **Claimed result** | Results are charts only. Post: 'in all instances, SIMD Quad is faster than the binary search' (std::binary_search). Intel Emerald Rapids/GCC: 'more than twice as fast as the binary search on the warm cache. The benefits are lesser on the cold cache.' Apple M4/Apple LLVM: 'it is with the cold cache that the SIMD Quad is more than twice as fast, whereas the benefits are more marginal on the warm cache.' The quad step over plain SIMD binary 'has little effect on the Apple platform, but it is a decent optimization on the Intel platform for large arrays in the cold case.' |
| **Workload** | Membership queries on sorted arrays of 16-bit unsigned integers, sizes 2-4096 elements, 100,000 arrays per size, 10M cold-cache queries + 10M warm-cache queries per size, on Roaring-Bitmap-style array containers |
| **Metric** | latency |
| **Hardware** | Intel Emerald Rapids server CPU; Apple M4 |
| **Compiler and flags** | GCC (Intel Emerald Rapids run) and Apple LLVM (Apple M4 run), versions not stated. The benchmark's CMakeLists.txt defaults CMAKE_BUILD_TYPE to Release (CMake default -O3 -DNDEBUG) with C++23 and no -march flags. simple.cpp times std::binary_search(arr.begin(), arr.end(), k) and std::find(arr.begin(), arr.end(), k) != arr.end(). |
| **Adoption** | 962 stars (whole blog-code monorepo, not this snippet alone) |
| **Last commit** | 2026-04-27 |
| **Links** | [repository](https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog) · [benchmark](https://lemire.me/blog/2026/04/27/you-can-beat-the-binary-search/) |

## Verdict

On an Intel Emerald Rapids server (GCC) and an Apple M4 (Apple LLVM), Release-mode C++23 builds (CMake default -O3 -DNDEBUG, no -march flags) benchmarking membership queries on sorted uint16_t arrays (sizes 2-4096, 100,000 arrays per size, 10M cold-cache + 10M warm-cache queries per size): simd_quad beat std::binary_search in every tested configuration, with the &gt;2x speedup holding specifically for Intel-warm-cache and Apple-M4-cold-cache; the opposite cache mode on each platform showed smaller, numerically unstated gains (charts only, no numeric tables in the post text).

## Use it when

- Sorted arrays of uint16_t, roughly 16-4096 elements (the tested range and Roaring array-container size cap)
- Membership-only lookups (found/not-found), not insertion-point queries
- Workload is warm-cache-dominated on x86 (author measured &gt;2x vs std::binary_search there) or cold-cache-dominated on Apple Silicon (&gt;2x there)
- You can adapt call sites to the array_container_t{const uint16_t\*, size_t} shape and compile with NEON or SSE2 guaranteed
- You're comfortable vendoring a \~40-line function rather than linking a library

## Skip it when

- Any key type other than uint16_t — the compares are hardcoded to 16-bit values
- General-purpose sorted containers with arbitrary element types/sizes where std::binary_search/lower_bound already fits
- Platforms without SSE2 or NEON — no scalar/AVX2/SVE fallback beyond a small-array linear scan below 16 elements
- Need for an insertion point (lower_bound semantics) — simd_quad only returns a boolean
- Anything requiring production hardening: this is unpackaged blog-benchmark code with no test suite beyond a self-check against std::binary_search inside the benchmark harness itself, and no issue tracker for this specific function

## How it is fast

It narrows to a candidate 16-element block using quaternary interpolation search over block-boundary keys (comparing 3 split points per round instead of binary search's 1, so fewer rounds), then checks all 16 candidates in that block with one SIMD compare pass (NEON vceqq_u16 or SSE2 _mm_cmpeq_epi16 over two 8-lane loads, ORed and reduced) instead of continuing scalar element-by-element comparisons.

## Compared with alternatives

Pick simd_quad over the generic siblings (sb_lower_bound, scandum/binary_search, FastBinarySearch) only when you're already working with sorted uint16_t arrays capped near 4096 elements in the Roaring-Bitmap array-container shape and can adapt to its struct-based calling convention; for generic sorted-array membership or lower_bound over other primitive types or larger/unbounded sizes, the siblings are closer to drop-in replacements for std::lower_bound/bsearch and are the better fit.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the algorithm itself; the benchmark harness additionally pulls lemire/counters v3.1.0 via CPM for perf-counter instrumentation, not needed to use simd_quad on its own |
| **Minimum toolchain** | the function itself only needs NEON (__ARM_NEON) or SSE2 (__SSE2__) intrinsic headers; the author's benchmark harness requires C++23 (std::print/std::format) and CMake's default Release build (-O3 -DNDEBUG) |
| **Platforms** | x86-64 with SSE2 (always available on x86-64) or aarch64 with NEON; no portable fallback path for other architectures |
| **Thread safety** | not documented; the function only reads caller-owned memory and writes no shared state, so concurrent calls over the same array should be safe by inspection |
| **Drop-in for the baseline** | partial — same asymptotic membership-test job as std::binary_search but a different signature (struct pointer + cardinality instead of an iterator pair) and returns only a bool, not an iterator or insertion point |

## Gotchas

- Assumes the array is already sorted ascending; the code does not check this and will silently return wrong answers on unsorted input
- Arrays smaller than 16 elements (the fixed block size) skip the SIMD/interpolation path entirely and fall back to a plain linear scan, so there's no benefit below that size
- The quaternary-interpolation step over plain SIMD-binary-search only helped in the author's own ablation on the Intel machine (large arrays, cold cache); on Apple M4 it had little effect, so porting it as-is to ARM buys less than the Intel numbers suggest

## Caveats and trade-offs

Single-author blog benchmark, not a packaged library. The implementation is a \~20-line function in the post's appendix and in 2026/04/26/benchmark/benchmarks/simple.cpp. The monorepo has no LICENSE file. Results are charts without numeric tables. The &gt;2x gain holds only for warm cache on Intel and cold cache on Apple M4; the other cache mode gives smaller gains. Only two machines tested, and the Intel one is identified only as Emerald Rapids.

Specialized to 16-bit-unsigned-integer arrays laid out in fixed 16-element blocks (built for Roaring Bitmap array containers), needs NEON or SSE2; the quaternary-interpolation half of the trick only pays off on the Intel platform per the author's own three-way ablation, not on Apple M4

## Maintenance

Not a maintained library — it's single-author blog-benchmark code; the repo README explicitly disclaims industrial-strength quality ('don't expect or ask for industrial-strength software... it can be wrong, slow, poorly coded') and states the code is public domain ('don't bother forking, just steal it') even though no formal LICENSE file exists. Usability is reference-only: read the technique, don't depend on the repo as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now A.
- **Tier reason:** Public code: 2026/04/26/benchmark/benchmarks/simple.cpp times std::binary_search(arr.begin(), arr.end(), k) and std::find against simd_quad. CMakeLists.txt forces a Release build (CMake default -O3 -DNDEBUG, C++23, no -march). Compilers are named (GCC, Apple LLVM; versions unstated), and one machine is an exact chip (Apple M4), so A holds. The Intel machine is only 'Emerald Rapids'.
- **Verifier notes:** The record overstated the claim as &gt;2x 'in every tested configuration'. The post says &gt;2x only for Intel-warm and Apple-cold, with smaller gains otherwise. It also says the quad step barely helps on Apple. No numeric values appear in the post text (charts only), so numbers_found_on_page=false for the quoted qualitative claims. last_commit 2026-04-27 is the benchmark directory's commit; the repo's latest commit is 2026-09-24.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://lemire.me/blog/2026/04/27/you-can-beat-the-binary-search/>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/tree/master/2026/04/26/benchmark>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/master/2026/04/26/benchmark/CMakeLists.txt>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/master/2026/04/26/benchmark/README.md>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/master/2026/04/26/benchmark/benchmarks/simple.cpp>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/master/2026/04/26/benchmark/benchmarks/benchmark.cpp>
- **Sources the enricher read:**
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/master/README.md>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/tree/master/2026/04/26/benchmark>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/master/2026/04/26/benchmark/CMakeLists.txt>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/master/2026/04/26/benchmark/README.md>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/master/2026/04/26/benchmark/benchmarks/simple.cpp>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/master/2026/04/26/benchmark/benchmarks/benchmark.cpp>
  - <https://lemire.me/blog/2026/04/27/you-can-beat-the-binary-search/>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/lemire/code-used-on-daniel-lemire-s-blog`) · [data/wave1/enrich/raw/github_com_lemire_code_used_on_daniel_lemire_s_blog.json](../../../data/wave1/enrich/raw/github_com_lemire_code_used_on_daniel_lemire_s_blog.json) (enrichment confidence 0.8)

</details>
