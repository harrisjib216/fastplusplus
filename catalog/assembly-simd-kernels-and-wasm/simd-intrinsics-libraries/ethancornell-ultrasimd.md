# UltraSIMD

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟡 stale

> Small x86 AVX2/AVX-512 header of dot, L2, cosine, Hamming, Jaccard and SAXPY kernels; beats non-vectorized scalar loops, barely beats auto-vectorized ones.

| | |
|---|---|
| **Beats** | the benchmark's own scalar reference loops: scalar_dot_product_no_autovec / scalar_dot_{f16,i8,bf16}_no_autovec for dot products (volatile per-element loads, noinline, optnone under Clang), plain inline scalar loops for L2, cosine, Hamming, Jaccard and SAXPY; the whole benchmark target is built with auto-vectorization disabled |
| **Claimed result** | Plain-scalar rows 1.7x to 7.6x; F32 dot 0.18x to 1.84x in the fuller CSV; the 18.7x headline rests on a volatile-slowed baseline. |
| **Workload** | Dot product, SAXPY, L2, cosine, Hamming and Jaccard distances over F32, F16, I8, BF16 and U8 vectors of 15 to 16384 elements, 175 benchmark rows, AVX-512 path versus scalar path. |
| **Metric** | throughput |
| **Hardware** | CPU model not stated; CSV lists features AVX512F, FMA, F16C, VNNI |
| **Compiler and flags** | CMakeLists.txt Release benchmark targets: -O3 -march=native -ffast-math -mavx2 (plus -mavx512f -mavx512bw -mavx512vl when supported), and with SIMD_DISABLE_AUTO_VECTORIZATION ON (the default) also -fno-tree-vectorize -fno-slp-vectorize -fno-tree-loop-vectorize and DISABLE_SCALAR_AUTOVEC (which adds a GCC optimize pragma or '#pragma clang optimize off' over the benchmark functions); compiler and version used for the CSVs not stated |
| **Adoption** | 2 stars |
| **Last commit** | 2025-06-28 |
| **Links** | [repository](https://github.com/EthanCornell/UltraSIMD) · [benchmark](https://github.com/EthanCornell/UltraSIMD/blob/main/simd_v3_benchmark_results_1751127313.csv) |

## Verdict

First-party CSVs from benchmark/benchmark_main_v3.cpp on an unnamed AVX-512 CPU (AVX512F, FMA, F16C, VNNI; compiler and version not stated; -O3 -march=native -ffast-math): against de-vectorized scalar loops the AVX-512 paths reach 15x to 18.7x for F32 dot, but against the compiler's own auto-vectorized loop (the repo's first CSV) F32 dot is 0.18x to 1.8x, I8 dot 0.36x to 2.9x, L2 1.5x to 2.0x and cosine 1.4x to 1.9x; the large gain that holds in every file is F16 dot (about 8x to 10x at 64 elements and up).

## Use it when

- Half-precision (F16) dot products on x86 with F16C, where the repo's numbers show about 7.8x to 10x over a per-element conversion loop for 64 to 8192 elements in all three result files; that reference ran at about 2 Gop/s even in the auto-vectorized file, so the compiler did not vectorize it.
- Int8 dot products or byte-wise Jaccard on AVX-512 machines for vectors of 256 elements or more, where the auto-vectorized comparison still shows 1.3x to 2.9x (I8) and 5.3x to 7.5x (Jaccard).
- As a short, MIT-licensed reference for masked AVX-512 tail handling to copy into your own code rather than as a dependency.

## Skip it when

- If your compiler already auto-vectorizes the plain loop (-O3 -march=native -ffast-math): in the repo's own auto-vectorized comparison, F32 dot is 0.18x to 1.8x, I8 dot 0.36x to 2.9x, SAXPY 0.44x to 1.7x and BF16 about 1.0x, losing below about 64 elements.
- Projects with more than one translation unit: non-template functions (dot_f16, dot_i8, dot_bf16, hamming_distance, jaccard_distance and the avx2:: and avx512:: kernels) are defined in the header without inline, so including it twice causes multiple-definition link errors.
- Portable binaries: every SIMD path is compiled only under #ifdef __AVX2__ / __AVX512F__, so you must build the whole translation unit with -mavx2 or -mavx512f (the CMake uses -march=native), after which the binary needs that CPU regardless of the runtime check; CPU detection does not check OS support via XGETBV.
- Code that needs an exact cosine distance (approximate rsqrt, about 1e-5 to 5e-5 relative error in the repo's CSVs) or BF16 inputs whose length is not a multiple of 32 (see gotchas).
- Anything needing maintenance or ARM support: two commits on 2025-06-28, 2 stars, no issues, no NEON path; for a maintained library see EVE or VCL.

## How it is fast

Straight intrinsics loops: one 512-bit FMA accumulator with masked loads for the tail (AVX-512) or 8-wide FMA with a scalar tail (AVX2); F16C _mm256_cvtph_ps conversion for half-precision dot products; sign-extend to 16 bits plus madd_epi16 for int8; XOR plus a nibble-lookup (pshufb) or bit-loop popcount and sad_epu8 for Hamming and Jaccard. Cosine distance replaces sqrt and divide with a magic-constant approximate reciprocal square root (0x5F1FFFF9 plus one refinement step). There is no unrolling into multiple accumulators, no VNNI (dot_i8_vnni_fixed just calls the AVX-512 version) and no blocking.

## Compared with alternatives

Rarely: marcelcases/simd and libalgebra make the same kind of comparison against -fno-tree-vectorize scalar code but say so; Vectis compares its AVX2 dot product against scalar, 4-accumulator scalar and -ffast-math builds, which is the fairer reference; EVE or the Vector Class Library are the maintained choices for general x86 SIMD. UltraSIMD is only worth taking as a small MIT snippet for F16C-based half-precision dot products.

## Integration

| | |
|---|---|
| **Form** | header-only (single file include/simd_v3.hpp, but see the multiple-definition gotcha) |
| **Dependencies** | none (OpenMP optional for batch_cosine_similarity) |
| **Minimum toolchain** | C++17 (if constexpr); README says GCC 7+, Clang 6+, MSVC 2019+; the AVX-512 BF16 path needs a compiler with _mm512_dpbf16_ps and -mavx512bf16 |
| **Platforms** | x86-64 only; AVX2+FMA (F16C for dot_f16) or AVX-512F/BW/VL selected at compile time and again at run time; scalar fallback otherwise |
| **Thread safety** | Not documented; kernels are stateless apart from a function-local static CPUID struct (thread-safe initialisation under C++11), so concurrent calls look safe. |
| **Drop-in for the baseline** | partial — replaces hand-written scalar loops with one call per kernel on raw pointers, but there is no std:: equivalent API, cosine returns an approximation, and the header cannot be included from two .cpp files without edits |

## Gotchas

- Harness flaw behind the 18.7x headline, confirmed from the CSVs: the library's own throughput is the same in all three result files (F32 dot about 33-37 Gop/s at 4096-8192 elements), and only the scalar reference changes. In simd_v3_benchmark_results.csv the reference ran at 20-32 Gop/s (auto-vectorized by the compiler) and F32 dot is 0.18x to 1.80x; in the _1751127313 and _fixed files the reference (volatile locals, noinline, optnone under Clang, -fno-tree-vectorize) ran at about 1.9-2.7 Gop/s, which turns the same SIMD numbers into 15x to 18.7x. The headline measures vectorized against non-vectorized code, not the library against what a compiler gives you.
- The BF16 rows (2.0x to 11.4x in the later files) did not exercise any BF16 hardware: the CPUFeatures column lists AVX512F, FMA, F16C and VNNI but not BF16 (the harness would print it), so simd::dot_bf16 ran its plain C++ fallback; that path matches the auto-vectorized reference in the first file (0.76x to 1.02x).
- Correctness bug in the untested AVX-512 BF16 path: for a remainder under 32 elements, the tail loop adds each product with _mm512_set1_ps, i.e. into all 16 lanes, and the final _mm512_reduce_add_ps then counts every tail product 16 times; any n not divisible by 32 returns a wrong result on BF16-capable CPUs. The benchmark CPU lacked BF16, so the CSVs never ran it.
- 32 of the 175 CSV rows (EdgeCase_Dot, KNN_Search, BatchCosineSim, MemoryBW) carry a fixed speedup of 1.00 with no scalar comparison; the L2 'scalar' loop ran at about 10 billion elements per second, so they were vectorized or hoisted out of the timing loop despite the no-vectorize flags. The unit test (test/test_main.cpp) covers only the old simd.hpp with assert(), which Release builds compile out.

## Known shortcomings

- Headline 18.7x compares against dot-product scalar code slowed with volatile locals (optnone under Clang); another CSV in the repo shows F32 dot 0.18x to 1.84x with 38 of 175 rows slower than scalar; plain-scalar rows 1.7x to 7.6x; no CPU or compiler. Crippled-baseline precedent (AssemblyScript): lowered to D.
- Enricher: SIMD throughput is identical in all three CSVs and only the scalar reference changes: the first CSV's reference ran auto-vectorised at 20-32 Gop/s (F32 dot 0.18-1.80x) while the later CSVs ran it de-vectorised at about 2 Gop/s (15-18.7x); the BF16 rows never touched BF16 hardware (CPUFeatures lacks BF16, so the C++ fallback ran at about 1.0x); the AVX-512 BF16 tail adds via _mm512_set1_ps so each tail product counts 16x when n%32 != 0; the header defines non-inline functions so multi-TU builds fail to link; only the F16 dot (about 8-10x) holds in every file.

## Caveats and trade-offs

Headline 18.7x is not a valid gain over scalar code: the dot-product scalar references copy every element into volatile locals (forced stack store and reload), are noinline, and become optnone (-O0 equivalent) under Clang, while the whole benchmark target is built with auto-vectorization disabled. The third CSV in the repo, probably from before the scalar reference was changed (code comments say 'FIXED: Scalar reference with auto-vectorization DISABLED'), shows F32 dot product at 0.18x to 1.84x of scalar and 38 of 175 rows slower than scalar. The fair-looking rows (plain scalar loops without auto-vectorization) give 1.7x to 7.6x. No CPU model or compiler stated (CSV lists AVX512F, FMA, F16C, VNNI); three CSVs with different results and no record of which run is current; vectors of 15 to 16384 elements, cache-resident. Tiny repo (2 stars, 2 commits on 2025-06-28); no comparison with Highway, xsimd or Eigen. README mentions AMD enterprise support, but the repo is a personal project. [retier] Crippled baseline; 38 of 175 rows slower than scalar; no CPU or compiler stated.

Header-only, x86-64 only (scalar, AVX2, AVX-512 dispatch), no NEON; ships F16/BF16/I8 types; README calls it production quality but the repo has two commits.

## Maintenance

Stale personal project (two commits on 2025-06-28, 2 stars, no issues), MIT-licensed and small enough to copy from, but not usable as a header-only dependency in multi-file builds without adding inline; the README's 'production-quality' label, AMD enterprise support line and Catch2 test suite are not backed by the repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** First-party CSVs from public benchmark code (benchmark/benchmark_main_v3.cpp) with flags in CMakeLists.txt, but no CPU model or compiler stated, so C. The tier stays C, but the claim is overstated: the 18.7x headline comes from dot-product rows whose scalar reference is handicapped (volatile locals on every element, noinline, and optnone under Clang).
- **Retiered** C to D: Lowered C to D: the headline 18.7x is measured against a scalar baseline crippled with volatile locals (optnone under Clang), and the repo's own fuller CSV has 38 of 175 rows slower than scalar; no CPU or compiler; AssemblyScript crippled-baseline precedent.
- **Verifier notes:** Downgrade for an overstated claim, kept at C on the non-dot kernels; shortcoming to record: the 18.7x headline is measured against a volatile-handicapped scalar dot product (optnone under Clang), and an earlier CSV in the same repo shows the F32 dot product at 0.18x to 1.84x of scalar. If the orchestrator treats the headline as the entry's claim, the AssemblyScript crippled-baseline precedent (C to D) would apply.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-12 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/EthanCornell/UltraSIMD>
  - <https://github.com/EthanCornell/UltraSIMD/commits/main>
  - <https://github.com/EthanCornell/UltraSIMD/blob/main/simd_v3_benchmark_results_1751127313.csv>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/README.md>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/simd_v3_benchmark_results.csv>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/simd_v3_benchmark_results_1751127313.csv>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/simd_v3_benchmark_results_fixed.csv>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/build.sh>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/benchmark/benchmark_main_v3.cpp>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/COMPLETE_GUIDE.md>
- **Sources the enricher read:**
  - <https://github.com/EthanCornell/UltraSIMD>
  - <https://github.com/EthanCornell/UltraSIMD/commits/main>
  - <https://github.com/EthanCornell/UltraSIMD/issues>
  - <https://github.com/EthanCornell/UltraSIMD/tree/main/include>
  - <https://github.com/EthanCornell/UltraSIMD/tree/main/test>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/README.md>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/COMPLETE_GUIDE.md>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/build.sh>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/include/simd.hpp>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/include/simd_v2.hpp>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/include/simd_v3.hpp>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/benchmark/benchmark_main_v3.cpp>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/test/test_main.cpp>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/simd_v3_benchmark_results.csv>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/simd_v3_benchmark_results_1751127313.csv>
  - <https://raw.githubusercontent.com/EthanCornell/UltraSIMD/HEAD/simd_v3_benchmark_results_fixed.csv>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/ethancornell/ultrasimd`) · [data/wave13/enrich/raw/github_com_ethancornell_ultrasimd.json](../../../data/wave13/enrich/raw/github_com_ethancornell_ultrasimd.json) (enrichment confidence 0.8)

</details>
