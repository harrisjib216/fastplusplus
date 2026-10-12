# blackwell-tensorcore-kernels

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `CUDA C++` · `MIT` · 🟢 active

> Teaching repo: raw mma.sync FP16 GEMM that edges past cuBLAS's tensor-core kernel at 4096-8192 on Blackwell sm_120.

| | |
|---|---|
| **Beats** | cuBLAS FP16-in/FP32-accumulate tensor-core GEMM (cublasGemmEx, which dispatches cutlass_80_tensorop_s16816gemm_f16_128x64 on sm_120) |
| **Claimed result** | 243.2 TFLOP/s vs 229.0 TFLOP/s for cuBLAS tensor-core GEMM at 8192^3 on sm_120 (106.1%, README Phase 2 table; five process runs 243.2-244.0 vs 229.0-229.5); the canonical results/bench.csv re-run after the cuBLAS handle-caching fix has 238.47 vs 225.75 TFLOP/s (about 1.056x, derived from page data); nsys per-kernel durations 4.52 ms vs 4.79 ms. The WMMA kernel in the same repo reaches only 44.4% of cuBLAS-TC, and a CUTLASS 3.x wgmma build reaches 85.5% of cuBLAS on H100 (641 TFLOP/s). |
| **Workload** | Hand-written FP16-in/FP32-acc GEMM using raw mma.sync m16n8k16 + ldmatrix, XOR-swizzled shared memory, 16-byte vectorized cp.async with a 2-stage pipeline (sweep winner 2 &gt; 3 &gt; 4), 128x128 CTA and 64x64 per-warp register tiles, M=N=K=8192 on a power-capped (300 W) Blackwell workstation GPU; 10 timed calls after one warm-up, CUDA events. |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX PRO 6000 Blackwell Max-Q (sm_120, CUDA 12.8); cross-generation rows on an H100 80GB SXM5 (sm_90, CUDA 13.1) |
| **Compiler and flags** | nvcc from CUDA 12.8 via CMake (C++17; CMAKE_CUDA_ARCHITECTURES 90 120; sm_120a for FP4 rows); no extra nvcc flags set in CMakeLists.txt |
| **Adoption** | 1 star |
| **Last commit** | 2026-06-04 |
| **Links** | [repository](https://github.com/waynehacking8/blackwell-tensorcore-kernels) · [benchmark](https://github.com/waynehacking8/blackwell-tensorcore-kernels) |

## Verdict

On an RTX PRO 6000 Blackwell Max-Q (sm_120, 300 W cap, CUDA 12.8, CMake build with no extra nvcc flags), FP16-in/FP32-acc M=N=K=8192 GEMM ran at 243.2 TFLOP/s against 229.0 for cublasGemmEx in the README's five-run session, and at 238.47 against 225.75 (about 1.056x, derived from page data) in the canonical results/bench.csv re-run after the cuBLAS handle-caching fix; nsys per-kernel times were 4.52 ms against 4.79 ms. The kernel is ahead only at 4096 (241.40 vs 235.13) and 8192, and behind cuBLAS at 2048 and smaller.

## Use it when

- Learning how a tensor-core GEMM is built on Ampere-style PTX (mma.sync, ldmatrix, cp.async, swizzling, warptiling), with measured TFLOP/s and ncu profiles for each step
- Large square FP16-in/FP32-out GEMMs (about 4096 and up) on an sm_120 workstation Blackwell card such as the RTX PRO 6000, where cuBLAS 12.8 dispatches an sm_80 CUTLASS kernel and this tile shape is 3-6% faster
- A starting point for your own fixed-shape FP16 kernel on sm_120 that you can fuse or modify, since the whole mainloop is about 150 lines in one file
- Reference numbers for FP8, unpacked FP4 and MXFP4 mma throughput on sm_120 (no cuBLAS FP4 GEMM exists there), keeping in mind the MXFP4 row uses unit block scales

## Skip it when

- Small and medium sizes: the fixed 128x128 tile loses to cuBLAS-TC at 2048 (200.96 vs 213.61 TFLOP/s), 1024 (69.45 vs 133.76) and 512 (14.59 vs 33.66) in results/bench.csv
- Hopper, datacenter Blackwell (sm_100) or any GPU other than sm_120: the mma.sync path caps well below wgmma/tcgen05, and on H100 the repo's best kernel (CUTLASS wgmma) reaches 85.5% of cuBLAS-TC, not more
- Production GEMM calls with arbitrary shapes, strides, transposes, alpha/beta, batching, BF16 or FP16 output: none of these exist; use cuBLAS/cuBLASLt or CUTLASS
- Workloads where a newer cuBLAS might pick a Blackwell-native kernel: the 6% win is over cuBLAS 12.8's heuristic choice of an Ampere kernel on this card, measured at one size on a power-capped 300 W Max-Q part

## How it is fast

The kernel issues PTX mma.sync.aligned.m16n8k16 directly, loads fragments with ldmatrix.x4 (and .trans for B) from an XOR-swizzled, bank-conflict-free shared-memory layout, and fills shared memory with 16-byte cp.async copies in a 2-stage pipeline. Its decisive step is warptiling: a 128x128x32 CTA tile split into four 64x64 per-warp register tiles, which issues 32 mma.sync per 8 ldmatrix (a 4:1 ratio) and removes the MIO-queue-full stall that held the WMMA version at about 45% of cuBLAS. ncu at 8192^3 shows 85.0% tensor-pipe utilization against 74.0% for the cutlass_80_tensorop_s16816gemm kernel that cuBLAS picks on this card.

## Compared with alternatives

Pick it over CUDA-L2 when you want a small, readable FP16 tensor-core kernel tuned for sm_120 rather than a large set of searched kernels for A100/H100 shapes; gpu-compute targets true-FP32 SGEMM on an RTX 5080 against pedantic cuBLAS and suits small FP32 problems, while for anything shipped cuBLAS or CUTLASS remains the safer default.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA toolkit (cuBLAS and cuBLASLt for the benchmark driver, NVML for the rate probe); CUTLASS &gt;= 3.4 only for the optional Hopper wgmma row |
| **Minimum toolchain** | CUDA 12.8 nvcc (H100 rows used CUDA 13.1), C++17, CMake 3.24; FP4/MXFP4 kernels need the sm_120a target |
| **Platforms** | NVIDIA GPUs; builds for sm_90 and sm_120 only and is tuned and measured as a winner only on sm_120 (RTX PRO 6000 Blackwell Max-Q). The FP16 kernel's PTX (mma.sync m16n8k16, ldmatrix, cp.async) is Ampere-level, but other architectures were not benchmarked |
| **Thread safety** | Not thread-safe at the launcher level: launch_mma_\* keep the FP16 staging buffers, cached source pointers and a shared-memory-attribute flag in static globals and launch on the default stream; the kernel itself is stateless |
| **Drop-in for the baseline** | false — not a cublasGemmEx-compatible API; only row-major C = A\*B with FP32 device inputs cast internally to FP16 |

## Gotchas

- The FP32-to-FP16 cast is cached by pointer identity (if (A != g_cA)), so calling the launcher again on the same buffer after changing its contents silently multiplies the stale FP16 copy; this is how the benchmark keeps the cast out of the timed loop
- Shape assumptions are unchecked: K is processed as K/32 slabs (a remainder is silently dropped), and the 16-byte cp.async loads need N and K to be multiples of 8 with 16-byte-aligned rows; the code comment says M and N should be multiples of 128
- The tuned kernel uses about 186-196 registers per thread (ncu and ptxas figures differ) and runs 2 CTAs per SM, so it does not co-schedule well with other kernels
- The MXFP4 988 TFLOP/s figure feeds every block scale as 1.0, so it measures throughput only, not real per-block MXFP4 numerics (the README says so)

## Known shortcomings

- cuBLAS harness created a handle per timed call until the 2026-06-02 fix (win holds after the fix: 238.47 vs 225.75); workload is a 2-stage pipeline, not 3.
- Win holds only at 4096 and 8192 (bench.csv loses at 2048: 200.96 vs 213.61, and at 1024 and 512); the launcher caches the FP16 cast by pointer, so new data in the same buffer gives stale results; K remainder past a multiple of 32 is silently dropped; not thread-safe (static globals).

## Caveats and trade-offs

The 6% win is over the older cutlass_80 kernel that cuBLAS picks on this card (a dispatch gap), at one size (8192^3) and one shape, on a power-capped Max-Q part; the README says it is not a cuBLAS replacement and every other row is below cuBLAS (45% for WMMA, 85.5% for the H100 CUTLASS path); the cuBLAS harness originally created a cuBLAS handle on every timed call (fixed 2026-06-02, data re-run 2026-06-04; the post-fix 8192 result still shows the win); CMakeLists sets no CMAKE_BUILD_TYPE or extra nvcc flags; recent commits are co-authored by an AI assistant per the commit list; baseline cuBLAS is not one of OpenBLAS, MKL, Eigen or BLIS.

FP16-in/FP32-acc GEMM only; a teaching/measurement repo with an ablation ladder, not a drop-in library; sm_120 tuned; the Hopper path needs CUTLASS 3.x and sm_90a.

## Maintenance

Active personal learning project (1 star, 46 commits, last commit 2026-06-04, recent commits co-authored with an AI assistant); MIT-licensed, so the kernel and PTX helpers can be copied, but treat them as a tuned example for one GPU rather than a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** README Phase 2 table and results/mma_ablation.md give mma_warptile 243.2 TFLOP/s vs cublas_tc (cublasGemmEx dispatching cutlass_80_tensorop_s16816gemm_f16_128x64_64x3) 229.0 at 8192^3; the post-fix canonical results/bench.csv has 238.47 vs 225.75. Benchmark code is public (src/main.cu, src/gemm_mma.cu, src/cublas_tc.cu, scripts/run_bench.sh), compiler is CUDA 12.8 nvcc, flags are fixed by the public CMakeLists.txt (no extra nvcc flags), and the GPU model is stated (RTX PRO 6000 Blackwell Max-Q).
- **Verifier notes:** Numbers verified in README, results/mma_ablation.md and results/bench.csv. The record's '3-stage cp.async' was wrong (winning kernel uses 2 stages; 3 stages was the WMMA kernel's choice); fixed in workload. Metadata checked on github.com: MIT, 1 star, not a fork, last commit 2026-06-04.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/waynehacking8/blackwell-tensorcore-kernels>
  - <https://github.com/waynehacking8/blackwell-tensorcore-kernels/commits>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/README.md>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/Makefile>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/results/bench.csv>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/results/mma_ablation.md>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/src/main.cu>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/src/cublas_tc.cu>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/include/util.cuh>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/scripts/run_bench.sh>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/VALIDATION.md>
- **Sources the enricher read:**
  - <https://github.com/waynehacking8/blackwell-tensorcore-kernels>
  - <https://github.com/waynehacking8/blackwell-tensorcore-kernels/commits>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/README.md>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/Makefile>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/VALIDATION.md>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/results/bench.csv>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/results/mma_ablation.md>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/src/main.cu>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/src/gemm_mma.cu>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/src/cublas_tc.cu>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/include/util.cuh>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/include/mma_ptx.cuh>
  - <https://raw.githubusercontent.com/waynehacking8/blackwell-tensorcore-kernels/HEAD/scripts/run_bench.sh>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/waynehacking8/blackwell-tensorcore-kernels`) · [data/wave8/enrich/raw/github_com_waynehacking8_blackwell_tensorcore_kernels.json](../../../data/wave8/enrich/raw/github_com_waynehacking8_blackwell_tensorcore_kernels.json) (enrichment confidence 0.85)

</details>
