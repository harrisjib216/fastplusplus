# Highway (vqsort)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0 OR BSD-3-Clause` · 🟢 active

> SIMD-dispatched vectorized quicksort/quickselect for built-in key types; \~10x faster than LLVM std::sort on large arrays.

| | |
|---|---|
| **Beats** | std::sort |
| **Claimed result** | About 10x faster than LLVM's std::sort for large arrays of built-in types (as of 2022-06-07). README example: AVX3, f32, uniform32, 1.00E+06 keys: std::sort 54 MB/s vs vqsort 1143 MB/s (\~21x on that specific case, derived from page data). |
| **Workload** | bench_sort benchmark sorting arrays of built-in types (e.g. f32, uniform32 distribution) up to 1e6 keys with AVX-512 (AVX3), comparing LLVM libc++ std::sort against vqsort, reporting output throughput in MB/s of sorted key bytes. |
| **Metric** | throughput |
| **Hardware** | Xeon 6154 (Skylake-X), clocked at 3 GHz |
| **Compiler and flags** | Clang (tested with 13.0.1 and 15.0.6), Bazel `-c opt` optimized build |
| **Adoption** | 5.9k stars; used in Google projects and backed by a peer-reviewed paper (arXiv:2205.05982) |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/google/highway) · [benchmark](https://github.com/google/highway/blob/master/hwy/contrib/sort/README.md) |

## Verdict

hwy/contrib/sort/README.md shows vqsort at 1143 MB/s vs LLVM libc++ std::sort at 54 MB/s (\~21x) sorting 1e6 uniform-random f32 keys under AVX3 (AVX-512) on a Xeon 6154 (Skylake-X) at 3 GHz, built with Clang 13.0.1/15.0.6 via `bazelisk build -c opt`; the README's own headline claim is the more conservative '\~10x for large arrays of built-in types' as of 2022-06-07, and it separately notes pdqsort-class scalar sorts are about 2x std::sort, not 10x.

## Use it when

- Sorting large arrays (README recommends &gt;=100 KiB, i.e. roughly 100K+ elements) of built-in numeric types on hardware with real SIMD (AVX2/AVX3, NEON, SVE/SVE2, etc.)
- Throughput-bound bulk sorting where equal-key order doesn't need to be preserved (unstable sort)
- Sorting packed key-value pairs (K32V32, K64V64) or 128-bit keys without a separate index/permutation array
- Top-k or median-style workloads via VQPartialSort/VQSelect instead of a full sort
- Already-vectorized pipelines that keep AVX-512 'warm', so even small VQSort calls benefit without startup penalty (README AVX-512 startup analysis)

## Skip it when

- Sorting custom structs/classes or needing a user-supplied comparator — only fixed built-in key types with ascending/descending order are supported
- Anywhere a stable sort is required; VQSort does not preserve the relative order of equal keys
- Near-sorted input on aarch64/NEON: issue #3139 (open) reports VQSelect/VQSort running 2-4x slower than scalar sort in that case
- Small arrays dropped into an otherwise scalar codebase: AVX-512 warm-up/downclocking can shrink the effective speedup on \~10K-element inputs from \~10x to as little as 1.4x (README AVX-512 startup study)
- SVE2-128 targets: issue #3336 (open) reports a Clang-only Min-instruction workaround costs 26-40% of VQSort's runtime there

## How it is fast

Vectorized Quicksort (VQSort paper, arXiv:2205.05982): wide-SIMD partitioning (AVX-512/AVX2/NEON/SVE-width) with in-register sorting networks for base cases, and pivot selection from a 384-byte random sample to balance partitions and avoid recursing into all-equal runs. Later work added 8x2/8x4/4x1/8x1 sorting-network shapes for small inputs and moved RNG seeding into a per-thread TLS cache (previously it fetched OS entropy on every call), which removed most of the small-array overhead (hwy/contrib/sort/README.md, 'Optimizations for small arrays').

## Compared with alternatives

Pick vqsort over pdqsort/ska_sort/vergesort when the target hardware has AVX2/AVX3/NEON/SVE and the data is built-in numeric keys (or 32/64-bit key-value pairs) sorted in bulk at 100K+ elements — its wide-SIMD partitioning beats the scalar-only pdqsort/ska_sort/vergesort by roughly an order of magnitude over plain std::sort. Favor the scalar siblings instead when you need a custom comparator, arbitrary key types, a guaranteed-scalar target, or want to avoid Highway's runtime-dispatch machinery entirely.

## Integration

| | |
|---|---|
| **Form** | source-drop \| static lib \| shared lib |
| **Dependencies** | none for the sort module itself (only the rest of the Highway headers, e.g. hwy/base.h, hwy/os_rng.h); Highway's own test suite additionally uses googletest, not required for library use |
| **Minimum toolchain** | C++17; CMake build (Bazel also supported); published sort benchmarks used Clang 13.0.1/15.0.6 |
| **Platforms** | 27 Highway targets across x86-64 (SSE2 through AVX10.2), Armv7+/NEON/SVE/SVE2, POWER8-10, RISC-V (RVV), IBM Z14/Z15, LoongArch, and WebAssembly; the headline vqsort speedup needs AVX2/AVX3/NEON/SVE-class SIMD |
| **Thread safety** | Not formally documented, but vqsort.h notes each call caches its RNG seed in an internal thread-local cache, so concurrent VQSort calls on independent arrays from different threads are safe by design |
| **Drop-in for the baseline** | false — different call signature (pointer + count + SortAscending/SortDescending tag, no iterators/comparator) and a fixed set of supported key types |

## Gotchas

- Not a stable sort — equal keys can be reordered
- An earlier version re-seeded from OS entropy on every call, which was costly for arrays of \~100-1000 elements; fixed in PR #1334 by caching seeds in TLS per thread — some historical benchmark numbers predate this fix
- Near-sorted arrays on aarch64/NEON can be 2-4x slower than scalar sort (issue #3139, open as of 2026-09)
- The 'about 10x' headline figure assumes AVX-512 is already warm; in a scalar-only surrounding codebase the effective win on medium-small inputs can drop to \~1.4x due to AVX-512 startup and downclocking overhead

## Caveats and trade-offs

The README itself notes pdqsort-class scalar algorithms are 'about twice as fast as LLVM's std::sort' (as of 2023-06), so the 10x figure is specifically vs plain std::sort, not vs the best scalar competitor. Independent analysis by Lukas Bergdoll (sort-research-rs) found a performance bug (entropy fetched from the OS on every call) that was fixed in PR #1334 after the original numbers were published; some published figures predate that fix.

Full speedup needs SIMD-capable hardware (AVX2/AVX3/NEON/SVE) with runtime dispatch; not a stable sort; speedup magnitude varies a lot by instruction set, key type, and distribution; small-array performance was a later optimization added after the original headline number.

## Maintenance

Actively maintained as part of Google's Highway SIMD library (last commit 2026-09-23, 5.9k stars); dual Apache-2.0/BSD-3-Clause. Listed as 'copyable' — the sort module can be vendored as source (hwy/contrib/sort plus the core Highway headers it depends on) rather than requiring the full library as a prebuilt external dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** hwy/contrib/sort/README.md states the '\~10x vs LLVM's std::sort' claim (2022-06-07) and shows std 54 MB/s vs vq 1143 MB/s (AVX3, f32 uniform32, 1e6 keys) on a Xeon 6154 at 3 GHz. It names Clang 13.0.1/15.0.6 and `bazelisk build -c opt`. The public benchmark code is hwy/contrib/sort/bench_sort.cc.
- **Verifier notes:** Numbers, the pdqsort 'twice as fast' note, and the Bergdoll/#1334 entropy fix are all verified in the README. The README doesn't say which of the two Clang versions produced the excerpt. The paper is peer-reviewed (Software: Practice and Experience 52(12), 2022, DOI 10.1002/spe.3142). GitHub reports license NOASSERTION, but LICENSE is dual Apache-2.0/BSD-3-Clause, so the record is correct. 5,873 stars, last commit 2026-09-23.
- **Shortcomings recorded by:** In developer source's SIMD selection Highway measured within noise of xsimd on all three kernels over 8.4M floats (fused sum+min+max, dot product, filter/count; xsimd was 7.1x, 2.3x and 1.4x over -O3 autovectorised scalar). It was rejected on integration cost, not speed, because only its static-dispatch subset is header-only; vqsort itself was not measured. (developer source, private repo; selection measurement in third_party/xsimd/VENDORING.md, median of 45 samples, -O3 -march=native baseline; evaluation for run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://github.com/google/highway/blob/master/hwy/contrib/sort/README.md>
  - <https://github.com/google/highway>
  - <https://github.com/google/highway/tree/master/hwy/contrib/sort>
  - <https://github.com/google/highway/blob/master/LICENSE>
  - <https://api.crossref.org/works?query.bibliographic=Vectorized+and+performance-portable+Quicksort+Wassenberg&rows=3>
- **Sources the enricher read:**
  - <https://github.com/google/highway>
  - <https://github.com/google/highway/blob/master/hwy/contrib/sort/README.md>
  - <https://github.com/google/highway/tree/master/hwy/contrib/sort>
  - <https://github.com/google/highway/blob/master/hwy/contrib/sort/vqsort.h>
  - <https://github.com/google/highway/blob/master/hwy/contrib/sort/algo-inl.h>
  - <https://github.com/google/highway/issues/3139>
  - <https://github.com/google/highway/issues/3336>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/google/highway`) · [data/wave0-seed/enrich/raw/github_com_google_highway.json](../../../data/wave0-seed/enrich/raw/github_com_google_highway.json) (enrichment confidence 0.88)

</details>
