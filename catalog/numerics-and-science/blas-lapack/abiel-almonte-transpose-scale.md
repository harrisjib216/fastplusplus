# transpose-scale (hpit)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C++` · `no license` · 🟢 active

> Single-file SIMD kernel for in-place square float transpose with scaling; 3-6x faster than MKL mkl_simatcopy at N&gt;=64.

| | |
|---|---|
| **Beats** | Intel MKL 2025.1.0 mkl_simatcopy (in-place transpose with scale); cblas_simatcopy from OpenBLAS on ARM |
| **Claimed result** | README: '3-6x faster than MKL' (i7-14700K, Intel MKL 2025.1.0). Chart images/bandwidth_barchart_po2.png (values read approximately from the image): speedup about 1.4x at N=16, 2.7x at N=32, 3.1-3.3x at N=64-256, 4.9x at N=512, 4.4x at N=1024 and 6.2x at N=2048; custom kernel about 131-135 GB/s at N=64-512 vs MKL about 40-43 GB/s, falling to about 80 vs 13 GB/s at N=2048. |
| **Workload** | In-place square float matrix transpose fused with a scale factor, tiled SIMD kernel (AVX2/SSE/NEON), latency and bandwidth percentiles over power-of-two sizes. |
| **Metric** | throughput |
| **Hardware** | Intel i7-14700K @ 5.5 GHz |
| **Compiler and flags** | clang-17 / clang++-17 (build_and_run.sh); -O3 -march=native -ffast-math, C++20 (CMakeLists.txt); MKL 2025.1 linked sequential (mkl_intel_lp64, mkl_sequential, mkl_core) |
| **Adoption** | 1 star |
| **Last commit** | 2026-01-10 |
| **Links** | [repository](https://github.com/abiel-almonte/transpose-scale) · [benchmark](https://github.com/abiel-almonte/transpose-scale) |

## Verdict

utils/time_kernel.cpp times the kernel against mkl_simatcopy('R','T') from MKL 2025.1 linked sequential, single-threaded and pinned to CPU 0 on an i7-14700K at 5.5 GHz. It was built with clang-17 -O3 -march=native -ffast-math, and a final element-by-element check compares the two results. Percentile bandwidth (p10/p50/p90) over power-of-two sizes gives about 1.4x at N=16, 2.7x at N=32, 3.1-3.3x at N=64-256 and 4.4-6.2x at N=512-2048, with values read from a chart image.

## Use it when

- Single-threaded in-place transpose-and-scale of square float matrices from about 64x64 to 2048x2048 on x86 with SSE/AVX2, where the chart shows about 3.1-6.2x over MKL 2025.1 sequential.
- Hot loops that call mkl_simatcopy on small or medium square float matrices and only need the transposed, scaled result.
- As a readable reference for a fused SIMD 4x4/8x8 in-register transpose to adapt into your own code, after getting the author's permission (no license).

## Skip it when

- Any shipped code: the repo has no LICENSE file, so the code cannot legally be copied or vendored.
- Rectangular, out-of-place, double, complex or conjugate transposes: only square float in place is implemented.
- Very small matrices (about 1.4x at N=16) or very large ones (m\*stride above 2^32 elements overflows its uint32_t index math, by inspection of the source).
- Multi-threaded workloads: the kernel is single-threaded and was compared only against single-threaded (sequential) MKL.
- ARM: a NEON path and an OpenBLAS cblas_simatcopy comparison exist in code, but no ARM results are published.

## How it is fast

Two-level cache blocking: 32x32 blocks, each split into 4x4 (SSE/NEON) or 8x8 (AVX2) register tiles. Off-diagonal tile pairs are swapped by loading one tile into a small buffer and doing an in-register unpack/shuffle transpose of each side, with the alpha multiply fused into the same pass so the data is touched only once. Separate loops handle full blocks, edge blocks, edge tiles and the diagonal (the README calls this 'branch-elimination via structured iteration spaces'), so the inner loops carry no bounds checks. The baseline instead calls a general imatcopy routine.

## Compared with alternatives

No catalogued sibling in this category does in-place transposes; the others (Eigen, BLASFEO, the GEMM kernels) solve different problems. The real choice is against the baseline: use this over mkl_simatcopy or cblas_simatcopy only for single-threaded, square, float, in-place transpose-scale at N&gt;=64, and only if the license question is settled.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the kernel. The benchmark needs Intel MKL 2025.1 at a hard-coded /opt/intel/oneapi path on x86, or OpenBLAS at /opt/homebrew on ARM; perf counters are Linux only. |
| **Minimum toolchain** | C++17 for the kernel (if constexpr). The project builds as C++20 with clang-17 and CMake 3.8+. |
| **Platforms** | x86-64 with SSE (AVX2 8x8 tiles only with -DFORCE_AVX2=ON), aarch64 with NEON. Anything else hits '#error Only SSE/AVX2 and NEON are supported'. |
| **Thread safety** | not documented. The function keeps no global state (its scratch buffer is on the stack), so concurrent calls on different matrices look safe by inspection. |
| **Drop-in for the baseline** | partial — it covers only mkl_simatcopy with ordering 'R'/'C', trans 'T', rows == cols and lda == ldb. The signature differs, uses uint32_t sizes and has no error handling. |

## Gotchas

- The kernel tells the compiler A is 64-byte aligned (__builtin_assume_aligned(A, 64)). Passing an unaligned pointer is undefined behaviour, even though the intrinsics use unaligned loads.
- The default build (build_and_run.sh passes -DFORCE_AVX2=OFF) uses 128-bit 4x4 tiles even on AVX2 machines. The llvm-mca analysis shows almost only xmm instructions, so the published numbers are presumably from the SSE path. 8x8 AVX2 tiles must be enabled explicitly.
- Reported bandwidth counts only the m(m-1)/2 off-diagonal pairs (2 loads + 2 stores each). The matrix is rewritten before every timed call, so both kernels start from cache-warm data.
- The benchmark uses stride = m + 16 floats (one cache line of padding), which avoids power-of-two set conflicts. Unpadded power-of-two strides were not measured.

## Known shortcomings

- '3-6x' holds only for N&gt;=64 (about 1.4x at N=16, 2.7x at N=32, up to 6.2x at N=2048); no LICENSE file (reference only); both sides single-threaded; only one CPU (i7-14700K) tested.
- Default build (-DFORCE_AVX2=OFF) uses SSE 4x4 tiles, so published numbers presumably come from the SSE path; kernel assumes 64-byte-aligned A (unaligned pointer is UB); uint32_t index math overflows above 2^32 elements.

## Caveats and trade-offs

No LICENSE file (LICENSE, LICENSE.md, LICENSE.txt, COPYING all 404; repo page shows none), so code cannot be copied. Numbers appear only in a chart image; the '3-6x' holds only for N&gt;=64 (about 1.4x at N=16, 2.7x at N=32). The baseline call is mkl_simatcopy (in-place) on x86 and cblas_simatcopy from OpenBLAS on ARM, read from utils/time_kernel.cpp; only x86 results are published. Single-threaded on both sides (MKL sequential, process pinned to CPU 0); one CPU; padded stride m+16; square float matrices only. -ffast-math applies only to the custom kernel.

Square in-place transpose with scaling only (BLAS-extension imatcopy), not GEMM; single-precision; AVX2/NEON; no license file.

## Maintenance

Hobby/portfolio project (1 star, last commit 2026-01-10) with no license, so it is reference-only: the technique is worth studying, but the code cannot be copied without the author's permission.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the benchmark code is public (utils/time_kernel.cpp times the custom kernel against mkl_simatcopy with a result sanity check; build_and_run.sh -t -s runs the size sweep), the compiler is named in build_and_run.sh (clang-17/clang++-17), flags in CMakeLists.txt (-O3 -march=native -ffast-math, C++20, MKL 2025.1 sequential), and the CPU in the README (Intel i7-14700K @ 5.5 GHz).
- **Verifier notes:** README claim and chart verified; the benchmark source compares against MKL with a correctness check and the compiler is named in build_and_run.sh, which is enough for tier A. Metadata confirmed: no license, 1 star, not a fork, last commit 2026-01-10 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/abiel-almonte/transpose-scale>
  - <https://github.com/abiel-almonte/transpose-scale/commits>
  - <https://github.com/abiel-almonte/transpose-scale/tree/master/analysis>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/README.md>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/build_and_run.sh>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/utils/time_kernel.cpp>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/utils/perf_kernel.cpp>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/images/bandwidth_barchart_po2.png>
- **Sources the enricher read:**
  - <https://github.com/abiel-almonte/transpose-scale>
  - <https://github.com/abiel-almonte/transpose-scale/commits/master>
  - <https://github.com/abiel-almonte/transpose-scale/tree/master/analysis>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/README.md>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/build_and_run.sh>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/transpose_inplace_tiled_simd.cpp>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/utils/time_kernel.cpp>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/utils/perf_kernel.cpp>
  - <https://raw.githubusercontent.com/abiel-almonte/transpose-scale/HEAD/analysis/transpose_inplace_tiled_simd_mca.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/abiel-almonte/transpose-scale`) · [data/wave8/enrich/raw/github_com_abiel_almonte_transpose_scale.json](../../../data/wave8/enrich/raw/github_com_abiel_almonte_transpose_scale.json) (enrichment confidence 0.8)

</details>
