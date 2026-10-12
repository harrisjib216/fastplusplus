# Aliaksei Sala C++ GEMM (C++Now 2025 / CppCon 2025 talk)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · ⚪ unknown

> C++Now/CppCon 2025 talk building a C++ DGEMM step by step to roughly OpenBLAS speed; slides only, no code.

| | |
|---|---|
| **Beats** | OpenBLAS |
| **Claimed result** | CppCon 2025 keynote slides: FP64 GEMM 1.70 TFLOPS vs OpenBLAS 1.58 (\~1.08x, derived) with zen5_packed_kernel on 16 cores at 5.7 GHz; FP32 ties OpenBLAS (3.57 vs 3.57); bf16 3.09 TFLOPS with no OpenBLAS figure. The C++Now 2025 slides on an i5-6300HQ show OpenBLAS ahead (154.1 vs 142.2 GFLOPS). |
| **Workload** | Dense double-precision square GEMM, 2880 x 2880 row-major std::vector&lt;double&gt; (larger than L3), multithreaded, built up step by step from naive loops to tiled, packed, register-blocked, unrolled and prefetched kernels and compared with OpenBLAS. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-6300HQ (4 cores, 2.3 GHz), Linux, per slides; AMD Ryzen 9 9950X per snippet only |
| **Compiler and flags** | Slides: Linux, -O3 -march=haswell -ffast-math; compiler name and version not stated. The talk's versions are C++ with SSE2/AVX2 intrinsics (_mm256_fmadd_pd shown on the slides). A slide titled 'Assembly: Where the FLOPs Really Happen' says 'All kernels are written in assembly' (in context this describes production BLAS libraries; a search snippet of the author's article says the same of OpenBLAS/BLIS) and that versions vary by up to 40% between Clang and GCC, marked 'NOT applicable for the final version'. |
| **Adoption** | Talk at C++Now 2025 and CppCon 2025; slides are in boostcon/cppnow_presentations_2025 (PDF) and CppCon/CppCon2025 (Keynote) |
| **Links** | [benchmark](https://raw.githubusercontent.com/boostcon/cppnow_presentations_2025/main/Presentations/Achieving_Peak_Performance_for_Matrix_Multiplication.pdf) |

## Verdict

C++Now 2025 slides (PDF): final version 0.336 s / 142.2 GFLOPS vs OpenBLAS 0.310 s / 154.1 GFLOPS for 2880^2 FP64 on a 4-core i5-6300HQ under Linux with -O3 -march=haswell -ffast-math, so OpenBLAS is about 8% faster. CppCon 2025 deck (Keynote, text extracted): on a 16-core, 5.7 GHz Zen 5 CPU (kernel named zen5_packed_kernel; consistent with a Ryzen 9 9950X, though the slide text does not name the model) 'Matmul: 1.7 TFLOPS' vs 'Openblas: 1.58 TFLOPS' in FP64 (about 1.08x, derived from page data), a tie at 3.57 TFLOPS in FP32, and 3.09 TFLOPS in bfloat16 with no OpenBLAS counterpart; first-party, no code.

## Use it when

- Learning or teaching how a BLIS-style GEMM is built in C++, with a measured time for every step (152 s naive down to 0.336 s on a 4-core i5-6300HQ)
- Judging whether portable C++ (std::experimental::simd templates) can get close to a tuned BLAS on your CPU before committing to assembly
- A design reference for a custom kernel where your BLAS lacks the type, e.g. bfloat16 GEMM on a Zen 5 desktop, which the CppCon deck says OpenBLAS did not support

## Skip it when

- Any production use: there is no repository, license, test suite or build, so you would be re-typing slide fragments; use OpenBLAS, BLIS, MKL or Eigen
- Expecting a win on AVX2 machines: on the one fully specified run (i5-6300HQ, 2880^2 FP64, -O3 -march=haswell -ffast-math) OpenBLAS took 0.310 s against 0.336 s, about 8% faster (derived from page data)
- Odd or non-square shapes: the slide kernels use fixed constexpr block sizes and show no edge handling, and 2880 is an exact multiple of Mc, Nc and Kc
- Code that needs a BLAS interface (column-major, transposes, alpha/beta, leading dimensions); none is shown
- Relying on the Zen 5 numbers: matrix size, compiler, flags and OpenBLAS version for that run are not stated in the deck

## How it is fast

The steps follow the Goto/BLIS recipe (the deck credits Robert van de Geijn): ikj loop order, 64-wide tiling, AVX2 FMA (_mm256_fmadd_pd), cache blocking with Mc=180, Nc=96, Kc=240, a 4x12 register block (12 ymm accumulators plus 3 for B), OpenMP over the outer blocks with pinned threads, packing B (the slides say packing A had no effect), reordering panels to unit stride, manual unrolling and _mm_prefetch with the NTA hint. The CppCon 2025 deck adds a portable kernel written with std::experimental::simd and index_sequence fold expressions (zen5_packed_kernel), a 4x8 thread grid to use 32 threads, and float and bfloat16 instantiations (bf16 through an intrinsics specialisation the slide says 'will be removed').

## Compared with alternatives

Never as a dependency; as study material it complements optimize-gemm (Avafly), sgemm.c (salykova) and cpu_gemm_opt, which cover the same blocking-and-packing path but ship runnable code that beats OpenBLAS in their own runs, so use those if you want something to build.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenMP; AVX2/FMA intrinsics in the C++Now version, std::experimental::simd (Parallelism TS v2) in the CppCon version |
| **Minimum toolchain** | not documented; the slides use C++17 fold expressions and std::experimental::simd, and the C++Now benchmark was built with -O3 -march=haswell -ffast-math on Linux (compiler not named) |
| **Platforms** | x86-64 with AVX2/FMA (Skylake i5-6300HQ) and an AVX-512 Zen 5 desktop (CppCon deck); nothing else documented |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The slide 'Assembly: Where the FLOPs Really Happen / All kernels are written in assembly' describes production BLAS libraries, not this code; the talk's kernels are C++ (AVX2 intrinsics, then std::experimental::simd), and the CppCon deck concludes 'C++ can deliver assembly-class performance on matrix multiply.'
- Percent-of-peak figures depend on the clock assumed: the C++Now deck uses 2.3 GHz (147.2 GFLOPS peak, so OpenBLAS shows 104%), the CppCon deck 2.8 GHz (179.2 GFLOPS); for Zen 5 it gives 2.9 TFLOPS at 5.7 GHz but expects 1.95 TFLOPS after an AVX-512 downclock to 3.8 GHz.
- Built with -ffast-math, so floating-point reassociation is allowed; results need not match a strict-IEEE BLAS bit for bit.
- The slides report up to 40% performance differences between Clang and GCC for intermediate versions, marked 'NOT applicable for the final version'.

## Known shortcomings

- Not faster on the opened slides: OpenBLAS 154.1 GFLOPS vs the talk's final version 142.2 (i5-6300HQ). The Ryzen 9950X win (1.70 vs 1.58 TFLOPS) is only a Medium snippet. No code repository.
- The CppCon 2025 keynote file (CppCon/CppCon2025 Presentations, Matrix_Multiplication.key) shows FP64 1.70 vs OpenBLAS 1.58 TFLOPS (\~1.08x, derived), an FP32 tie at 3.57 vs 3.57, and bf16 3.09 TFLOPS with no OpenBLAS figure; kernel zen5_packed_kernel (16 cores, 5.7 GHz); CPU model, matrix size and compiler not given. The talk's code is C++ (AVX2 intrinsics, then std::experimental::simd), not hand-written assembly; no code repository.

## Caveats and trade-offs

Not faster on the only opened evidence: the slides end with OpenBLAS ahead of the final C++ version (154.1 vs 142.2 GFLOPS). The opposite claim (1.70 vs 1.58 TFLOPS on a Ryzen 9 9950X) is from search-result snippets of the author's Medium article (medium.com and YouTube egress-blocked): snippet only. No repository: the slides give no code link (only a LinkedIn contact), and a WebSearch for a GitHub repo found none, so has_code=false and it is reference-only. Matrix is std::vector&lt;double&gt;, row-major, 2880x2880, multithreaded on 4 cores. Peak is computed at the 2.3 GHz base clock, so percent-of-peak figures over 100% reflect turbo.

Per the slides the final kernels are hand-written assembly, so the 'C++' result depends on inline assembly and an x86 AVX2/FMA target. Only the double-precision square-matrix case is shown.

## Maintenance

A conference talk, not a maintained project: no code, license or repository was found, so it is reference-only; the author's 'future plans' slide lists finishing the CPU work and repeating it on GPUs and AI chips.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification C, tier now C.
- **Tier reason:** The only benchmark page that could be opened (the C++Now 2025 slides) shows OpenBLAS ahead: 0.310 s / 154.1 GFLOPS vs the final version's 0.336 s / 142.2 GFLOPS on an i5-6300HQ; the 'beats OpenBLAS' numbers (1.70 vs 1.58 TFLOPS on a Ryzen 9 9950X) exist only in a search snippet of a blocked Medium post, and there is no public code, so no opened evidence supports a win.
- **Retiered** D to C: First-party talk material opened in the CppCon/CppCon2025 presentations repository shows a small FP64 win over OpenBLAS on Zen 5 (1.70 vs 1.58 TFLOPS); no code, CPU model, size or compiler, so C.
- **Verifier notes:** Slides PDF opened and the record's numbers match it, but they show OpenBLAS winning; the only win is snippet-only from a blocked Medium post, with no code. Reject as not-faster; if the Medium article or a repo becomes reachable, re-verify on the 9950X numbers.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/boostcon/cppnow_presentations_2025/main/Presentations/Achieving_Peak_Performance_for_Matrix_Multiplication.pdf>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/boostcon/cppnow_presentations_2025/main/Presentations/Achieving_Peak_Performance_for_Matrix_Multiplication.pdf>
  - <https://github.com/CppCon/CppCon2025/tree/main/Presentations>
  - <https://raw.githubusercontent.com/CppCon/CppCon2025/main/Presentations/Achieving_Peak_Performance_for_Matrix_Multiplication.key>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:aliaksei-sala-c-gemm-c-now-2025-cppcon-2025-talk`) · [data/wave8/enrich/raw/paper_aliaksei_sala_c_gemm_c_now_2025_cppcon_2025_talk.json](../../../data/wave8/enrich/raw/paper_aliaksei_sala_c_gemm_c_now_2025_cppcon_2025_talk.json) (enrichment confidence 0.6)

</details>
