# emugemm-cdna

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> FP32 GEMM emulated with bf16 matrix-core products on AMD MI250; 1.20-1.22x over per-shape-tuned rocBLAS sgemm at a lower accuracy tier.

| | |
|---|---|
| **Beats** | rocBLAS native FP32 sgemm on AMD MI250 (per-shape tuned solutions) |
| **Claimed result** | bf16x3 vs native FP32 rocBLAS, both sides per-shape solution-tuned, on one MI250 GCD: 45.33 vs 37.52 TFLOP/s at M=8192 N=28672 K=8192 (1.21x), 44.26 vs 37.03 at M=16384 N=8192 K=8192 (1.20x), 45.06 vs 37.02 at M=N=K=12288 (1.22x) (docs/RESULTS_ROUND8.md section C; README summarizes as 1.20-1.22x on every shape tested). Whole node, 8 GCDs at 8192^3: 325.1 vs 278.4 TF (1.17x). |
| **Workload** | FP32 GEMM emulated by splitting inputs into three BF16 slices (bf16x3) multiplied on the matrix cores, on one MI250 GCD, three shapes (8192x28672x8192, 16384x8192x8192, 12288^3), with the native rocBLAS FP32 side also tuned per shape; row-major, non-transposed, alpha=1, beta=0 only. |
| **Metric** | throughput |
| **Hardware** | AMD MI250 (gfx90a), 1 GCD, 104 CU |
| **Compiler and flags** | hipcc -O3 -Wno-deprecated-declarations --offload-arch=gfx90a, ROCm 7.2.3 |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/Mazukiri/emugemm-cdna) · [benchmark](https://github.com/Mazukiri/emugemm-cdna/blob/main/docs/RESULTS_ROUND8.md) |

## Verdict

On one MI250 GCD with ROCm 7.2.3 and hipcc -O3 --offload-arch=gfx90a, the author's emu_tuned harness measured bf16x3 at 45.33, 44.26 and 45.06 TFLOP/s against per-shape-tuned rocBLAS FP32 at 37.52, 37.03 and 37.02 (1.21x, 1.20x, 1.22x) on 8192x28672x8192, 16384x8192x8192 and 12288^3, and 325.1 vs 278.4 TFLOP/s (1.17x) with all 8 GCDs at 8192^3. These are first-party numbers from an unpublished harness, measured before the 2026-08-13 timing-error fixes, and they compare against FP32 that is about 2.8x more accurate at those K.

## Use it when

- Large FP32 GEMMs (thousands per side, e.g. 8192x28672x8192 or 12288^3) on an MI250 / gfx90a GCD where about 4.5e-6 normwise relative error is acceptable.
- GEMM-bound pipelines; the repo's CholeskyQR2 randomized SVD got 1.19x end to end at a 1e-5 target, while a Householder-QR pipeline gained only 1.8% because GEMM was 300 of 6192 ms.
- Inputs with wide dynamic range where you want FP32's 8-bit exponent kept (bf16 path) rather than fp16 scaling tricks.
- All-positive or non-cancelling data (counts, histograms, convolutions): Round 9 measured bf16x3 4x more accurate than FP32 at K=65536 on U(0,1) inputs.
- As a template for tuning rocBLAS itself: the tuning-table and solution-index plumbing (and the ROCm/rocm-libraries#9985 evidence) show where the default rocBLAS heuristic leaves 1.3-4.5x on skinny or large-K shapes.

## Skip it when

- When you need bit-for-bit or better-than-native FP32 accuracy: bf16x3 has a hard floor of 4.4355e-6, worse than native FP32 at K=8192 (4.49e-6 vs 1.62e-6 in the repo's own table); below the floor the planner falls back to FP32 with FP64 chunk sums, which is slower than native.
- Strongly cancelling products (large rho = || |A||B| || / ||AB||): bf16x3 error grew to 1.65e-3 (35x FP32) in Round 9 and peaked at 31.5x FP32 near rho = 1.2e4 in Round 10; the planner probes rho with 64 Rademacher vectors (about 1.6% extra cost) and may then refuse or escalate.
- Any GPU other than gfx90a: every model constant and the tuning table were measured on MI250 with ROCm 7.2.3; the README says CDNA3/CDNA4 may invert the conclusions, and on CDNA2 FP64 emulation is a loss.
- Small shapes: scan and split passes (one read of A and B plus two low-precision copies) cost more than the GEMM saves; the planner then returns native FP32 (the doc cites 2048x2048x4096 at 1.39 ms vs 1.03 ms before that fix).
- Production code needing transposes, alpha/beta, batched calls, column-major layout or concurrency from several host threads: none of these is supported.

## How it is fast

Multiword (split-precision) GEMM emulation in the line of Markidis 2018, Ootomo and Yokota 2022, and Fasi-Higham et al. 2023: each FP32 value x becomes s0 = bf16(x) and s1 = bf16(x - s0), and C = A0\*B0 + A0\*B1 + A1\*B0 (the small A1\*B1 term is dropped). On MI250 the bf16 MFMA rate is 3.98x the FP32 MFMA rate (169.2 vs 42.5 TFLOP/s measured), so three bf16 products cost about 0.75 of one FP32 product, a ceiling of 1.33x; the repo reaches 1.20-1.22x of it. Solution tuning is what makes the bf16 side reach that rate: an offline table (data/tune_table.csv, 820 rows) maps shapes to rocBLAS solution indices via rocblas_gemm_algo_solution_index, because the default rocBLAS bf16 kernel choice ran as low as 83.9 TFLOP/s versus 137.8 for the best solution at the MLP shape.

## Compared with alternatives

It is the only catalogued GEMM entry for AMD Instinct GPUs: pick it over the NVIDIA-only blackwell-tensorcore-kernels, gpu-compute and CUDA-L2 when you are on an MI250, have FP32 data, and can accept about 4.5e-6 error in exchange for about 1.2x.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | ROCm (tested 7.2.3) with HIP and rocBLAS; rocSOLVER only for the randsvd2 example; a tuning table generated by bench/gen_tune_table.cpp for your GPU and ROCm version |
| **Minimum toolchain** | hipcc from ROCm 7.2.3 (only version tested); C++ (std::vector, lambdas, so C++11 or later); C-compatible extern "C" API |
| **Platforms** | AMD CDNA GPUs; only gfx90a (MI250) tested |
| **Thread safety** | not documented; the code keeps the workspace buffers and tuning table in unsynchronized file-scope globals, so concurrent calls from several host threads are unsafe |
| **Drop-in for the baseline** | partial — different entry point and signature from rocblas_sgemm; row-major, non-transposed, alpha=1, beta=0 only; results are not bit-identical to FP32 |

## Gotchas

- Unless you pass a_absmax, b_absmax and rho in emu_hints_t, every call runs an absmax scan and a 64-probe rho estimate, each ending in a blocking hipMemcpy; reuse the hints struct (the call writes measured values back) to pay this once. The a_is_reused flag is declared but the code does not cache splits.
- Split, scan and accumulate kernels launch on the default (null) stream, not on the rocBLAS handle's stream, and kernel launch errors are not checked.
- emugemm_init reads the architecture of device 0, not the current device, and with no table file it runs untuned (the code warns up to 1.7x slower bf16); shapes farther than a log2 distance of 1 from any table row fall back to the rocBLAS default solution.
- The headline 1.20-1.22x came from emu_tuned.cpp, which is not in the repository; the published bench/emugemm_test.cpp times three back-to-back calls with no warm-up against an untuned rocblas_gemm_ex default, so it does not reproduce the headline table.

## Known shortcomings

- Harness behind the 1.20-1.22x (emu_tuned.cpp) is not in the repo and the public emugemm_test times untuned native; only 3 shapes; bf16x3 is about 2.8x less accurate than native FP32 at tested K (4.49e-6 vs 1.62e-6), so not like-for-like; timing fixes (2026-08-13) came after the Round 8 numbers.
- Code splits each input into 2 bf16 slices and runs 3 products (record said 'three slices'); public bench times emu vs untuned rocBLAS default with 3 back-to-back calls, no warm-up, not interleaved; globals unsynchronized (not thread-safe); kernels go on the null stream, not the handle stream; bf16x3 error up to 35x FP32 on cancelling data (Round 9).

## Caveats and trade-offs

GPU, not CPU. Only three shapes back the 1.20-1.22x; the harness that produced them (emu_tuned.cpp) is not published. bf16x3 has a relative-error floor of 4.4355e-6, so at the tested K (8192-12288) it is less accurate than native FP32 (4.49e-6 vs 1.62e-6 at K=8192 in the same docs): the speedup is at a lower accuracy tier, not like-for-like. The README records that an earlier 2.1x was really 1.21x because the baseline ran rocBLAS's default kernel, and ties the investigation to ROCm/rocm-libraries issue 9985, so the win depends on how well the native baseline is tuned; the tuning table is specific to gfx90a and ROCm 7.2.3. Timing-harness fixes landed 2026-08-13 ('Stop a failed HIP call from returning a plausible-looking timing'), after the Round 8 numbers (2026-07-25); the docs do not say whether the 1.20-1.22x table was re-measured. Last commit co-authored by an AI assistant. Baseline rocBLAS is not one of OpenBLAS, MKL, Eigen or BLIS.

Not bit-compatible with FP32: accuracy floor of 4.4355e-6 relative error with the bf16x3 scheme, with a request API (max_rel_err) that reports 'TARGET UNREACHABLE' instead of silently under-delivering; only gfx90a was tested; needs a tuning table per GPU and ROCm version; speed ceiling on MI250 is 1.33x.

## Maintenance

Active single-author research repo (MIT, 0 stars, last commit 2026-09-03, no issues filed), unusually candid about its own corrected numbers; small enough to vendor, but treat it as a measured prototype for gfx90a rather than a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** The 1.20-1.22x figures are first-party (README and docs/RESULTS_ROUND8.md section C), and the docs say 'the speed numbers of record come from emu_tuned', but emu_tuned.cpp (and rocblas_tune.cpp) are not in the repository (bench/ and issue9985/src/ listings, 404 on raw). The public bench/emugemm_test.cpp times native rocBLAS with the default solution (index 0), not the tuned baseline, so the headline comparison cannot be reproduced from public code: not A; no peer review: not B.
- **Verifier notes:** Numbers match README and docs/RESULTS_ROUND8.md, but the benchmark source for them is missing from the repo, so A drops to C. Biggest shortcoming to record: emulated result is \~2.8x less accurate than native FP32 at the tested K. Metadata checked on github.com: MIT, 0 stars, not a fork, last commit 2026-09-03.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Mazukiri/emugemm-cdna>
  - <https://github.com/Mazukiri/emugemm-cdna/commits>
  - <https://github.com/Mazukiri/emugemm-cdna/tree/main/docs>
  - <https://github.com/Mazukiri/emugemm-cdna/tree/main/bench>
  - <https://github.com/Mazukiri/emugemm-cdna/tree/main/issue9985/src>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/README.md>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/BUILD.md>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/bench/emugemm_test.cpp>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/docs/RESULTS_ROUND8.md>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/docs/RESULTS_ROUND9.md>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/docs/RESULTS_ROUND10.md>
- **Sources the enricher read:**
  - <https://github.com/Mazukiri/emugemm-cdna/commits>
  - <https://github.com/Mazukiri/emugemm-cdna/issues>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/README.md>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/BUILD.md>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/src/emugemm.h>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/src/emugemm.cpp>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/bench/emugemm_test.cpp>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/docs/RESULTS_ROUND8.md>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/docs/RESULTS_ROUND9.md>
  - <https://raw.githubusercontent.com/Mazukiri/emugemm-cdna/HEAD/docs/RESULTS_ROUND10.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mazukiri/emugemm-cdna`) · [data/wave8/enrich/raw/github_com_mazukiri_emugemm_cdna.json](../../../data/wave8/enrich/raw/github_com_mazukiri_emugemm_cdna.json) (enrichment confidence 0.8)

</details>
