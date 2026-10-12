# fast.cu (H100 BF16 matmul and sum-reduction kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++ (CUDA)` · `MIT` · 🟢 active

> From-scratch Hopper BF16 GEMM (TMA + WGMMA) beating cuBLAS by 2-7% on square H100 matmuls, plus a CUB-level reduction.

| | |
|---|---|
| **Beats** | cuBLAS (cublasGemmEx, BF16 inputs, FP32 compute, CUBLAS_GEMM_DEFAULT) for matmul; CUB for sum reduction |
| **Claimed result** | Matmul N=4096: 763 TFLOPs vs cuBLAS 716 TFLOPs (about 1.07x, derived from page data); N=8192: 808 vs 795 TFLOPs (about 1.02x, derived from page data). Sum of 2^30 elements: 3240.11 GB/s vs CUB 3193 GB/s (about 1.01x, derived from page data). |
| **Workload** | Square bf16 matrix multiplication with fp32 accumulation at N=4096 and N=8192, plus a sum over 2^30 elements, all on an H100. |
| **Metric** | throughput |
| **Hardware** | NVIDIA H100 SXM 80GB (132 SMs, 3.35 TB/s HBM) per a search-result snippet of the worklog post; the README says only H100. Clocks and host CPU not stated |
| **Compiler and flags** | nvcc -std=c++17 -O3 -DNDEBUG -w --expt-relaxed-constexpr --expt-extended-lambda --use_fast_math -Xcompiler=-fPIE -Xcompiler=-Wno-psabi -Xcompiler=-fno-strict-aliasing -gencode arch=compute_90a,code=sm_90a -lineinfo, linked with -lcublas -lcuda (Makefile); CUDA toolkit 12.6 per a search-result snippet of the worklog post (post not opened, egress blocked) |
| **Adoption** | 625 stars |
| **Last commit** | 2026-08-15 |
| **Links** | [repository](https://github.com/pranjalssh/fast.cu) · [benchmark](https://github.com/pranjalssh/fast.cu) |

## Verdict

On one H100 (SXM 80GB and CUDA 12.6 per a worklog search snippet), the same binary timed the custom BF16 GEMM against cublasGemmEx (BF16 in and out, CUBLAS_COMPUTE_32F, CUBLAS_GEMM_DEFAULT): 763 vs 716 TFLOPS at N=4096 and 808 vs 795 at N=8192 (about 1.07x and 1.02x, derived from page data); the README does not say which of kernels 1-12 produced them. An independent run in issue #13 (H100 variant unstated, CUDA 12.4, N=8192) measured cuBLAS at 518.6 TFLOPS and kernels 10/12 at 533.4/530.8 TFLOPS, about 1.02-1.03x (derived from page data), so the small margin held there though absolute numbers were far lower. The int32 sum of 2^30 elements ran at 3240.11 GB/s vs CUB's 3193.36 GB/s.

## Use it when

- Large square or near-square BF16 GEMMs (the published sizes are 4096 and 8192) on an H100 SXM, with M and N multiples of 256 and K a multiple of 64.
- Learning or prototyping Hopper GEMM design: the 12-kernel ladder goes from a naive kernel to TMA, WGMMA, warp specialization, clusters and Hilbert scheduling in plain CUDA plus inline PTX, without CUTLASS/CuTe templates.
- A starting point for a custom fused epilogue on Hopper when you control shapes and want a single-file kernel you can edit.
- Studying Blackwell (GB300/B300, sm_103a) NVFP4 GEMM: the gb300/nvfp4 ladder documents each optimization rung and a paired, cooldown-gated benchmark protocol against cuBLASLt.

## Skip it when

- Arbitrary shapes: nothing checks divisibility at runtime (the Makefile's -DNDEBUG compiles out every assert), and issue #4 (open) reports row-shuffled wrong results from matmul_3 at 128x128x64 on an H800.
- Any GPU other than an H100-class sm_90a part: kernels are compiled only for sm_90a, NUM_SM is hard-coded to 128 persistent CTAs, and nothing is tuned for H100 PCIe/H800/H200.
- When a 2-7% gain does not justify owning a kernel: the margin is about 1.07x at N=4096 and 1.02x at N=8192 (derived from page data), and issue #13 (open, 'Unable to reproduce reported numbers') reports much lower absolute throughput on another H100 (cuBLAS 518.6 TFLOPS at N=8192).
- FP16, FP8, transposed, batched or alpha/beta GEMMs, or multi-threaded host code: none are supported, and runKernelN keeps TMA descriptors and the schedule buffer in host globals.
- General reductions: the sum kernels handle int32 only, require N divisible by 4, and win by about 1.5% over CUB.

## How it is fast

The final kernels (11/12) are persistent, warp-specialized Hopper GEMMs: one producer warpgroup issues TMA bulk-tensor loads (cp.async.bulk.tensor with 128B swizzle, multicast across a 2-CTA thread-block cluster) into a 3-stage mbarrier-synchronized shared-memory ring, while two consumer warpgroups run wgmma.mma_async m64n256k16 BF16 instructions with FP32 accumulators, and setmaxnreg moves registers from producer to consumers. Output tiles (128 x 256, BK=64) are assigned to 128 persistent CTAs along a Hilbert curve for L2 reuse, and kernel 12 writes C through stmatrix into padded shared memory followed by a TMA store. The sum kernels use int4 vector loads (16 per thread), redux.sync warp reductions, one shared-memory atomic per warp and one global atomicAdd per block.

## Compared with alternatives

Pick it over ThunderKittens when you want one readable, dependency-free Hopper GEMM file to fork rather than a tile-abstraction framework that matches cuBLAS more generally; pick it over bare-metal when the target is an H100 instead of an sm_86 laptop GPU, where bare-metal's margin is about 1.02x under a clock lock. For quantized or GEMV work, BitBLAS or FastGEMV fit better.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA toolkit with the Driver API (cuTensorMapEncodeTiled, -lcuda); cuBLAS only for the reference/verification path; CUB for the sum comparison |
| **Minimum toolchain** | C++17 nvcc with sm_90a support (Makefile: -gencode arch=compute_90a,code=sm_90a); CUDA 12.6 named only in a search snippet of the worklog, and issue #13 built it with CUDA 12.4; the GB300 NVFP4 kernels need CUDA 13.1 and sm_103a |
| **Platforms** | NVIDIA H100 (sm_90a) for matmul and sum; GB300/B300 (sm_103a) for gb300/nvfp4; Linux build via GNU Make |
| **Thread safety** | not documented; runKernel11/12 cache TMA descriptors and the Hilbert schedule in host-global variables, so concurrent calls with different shapes are unsafe |
| **Drop-in for the baseline** | false - fixed-layout runKernelN(M, N, K, A, B, C) host functions with no handle, stream, alpha/beta or transpose arguments; not a cublasGemmEx replacement |

## Gotchas

- Kernel 12 needs M and N multiples of 256 (BM 128 x 2-CTA cluster, BN 256) and K a multiple of 64 (num_blocks_k = K / BK drops any tail); with -DNDEBUG the device and host asserts that guard this are compiled out, so bad shapes fail silently.
- runKernel11/12 rebuild their cached TMA maps only when M changes (keyed on _prev_m), so calling with the same M but a different N or K reuses stale descriptors; each rebuild also cudaMallocs a new schedule buffer without freeing the old one.
- The matmul harness hard-codes 8192 x 8192 (max_size), times 8 back-to-back launches after one verification run, uses a 0.1 absolute tolerance on BF16 outputs, and keeps benchmarking after a failed check; reproducing the N=4096 row means editing the source.
- The sum kernels zero \*d_out from inside the kernel (thread i == 0) while other blocks atomicAdd to it, a formal race; the benchmark's own int32 total (2^30 values of rand() % 100, about 5.3e10, derived) wraps, identically in CUB.

## Known shortcomings

- Margins over cuBLAS are only 2-7%; CUDA 12.6 and H100 SXM known from a search snippet (blog blocked here).
- Open issue #13 'Unable to reproduce reported numbers': another H100 (variant unstated, CUDA 12.4, N=8192) measured cuBLAS 518.6 TFLOPS vs kernel12 530.8 and kernel10 533.4, so the margin holds at \~1.02-1.03x (derived) but absolute numbers are far lower. Open #4: matmul_3 returns wrong, row-shuffled results at 128x128x64 (H800). -DNDEBUG compiles out the shape asserts (M,N must be multiples of 256, K of 64). TMA maps are cached on M only, so a new N/K with the same M reuses stale maps. The sum kernel zeroes \*d_out inside the kernel while other blocks atomicAdd (formal race). It is 12 kernels plus cuBLAS as kernel 0, not 13.

## Caveats and trade-offs

Margins over cuBLAS are small (about 7% at N=4096, about 2% at N=8192) and only two sizes are reported; the sum-reduction win over CUB is about 1.5% on 2^30 int32 elements. The README does not say which of the 13 kernels in h100/matmul.cu produced 763/808 TFLOPs. The harness averages 8 timed repeats after one correctness/warm-up run. The CUDA 12.6 and H100 SXM details come from a search snippet of the substack worklog, which could not be opened; a newer cuBLAS may close the gap. The GB300 NVFP4 section (gb300/nvfp4, cuBLASLt baseline, run_bench_modes.sh) publishes no numbers in the repo.

Hopper-only (sm_90a); BF16 square matrices with FP32 accumulation; orchestration in h100/matmul.cu with example kernels in h100/matmul/, tuned for specific sizes rather than a general GEMM API. The repo also carries GB300 NVFP4 GEMM kernels that need CUDA 13.1 and a GB300/B300.

## Maintenance

Active (last commit 2026-08-15, 625 stars, MIT, 17 commits) and small enough to vendor, but it is a demonstration repo: open issues #4 (small-shape wrong results) and #13 (reproducibility) have no maintainer replies.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The public harness h100/matmul.cu checks each kernel against cublasGemmEx (BF16 in and out, CUBLAS_COMPUTE_32F, CUBLAS_GEMM_DEFAULT) and times cuBLAS in the same binary; h100/sum.cu times cub::DeviceReduce::Sum the same way. The Makefile states the full nvcc flags and the GPU is named. A search-result snippet of the worklog gives H100 SXM and CUDA toolkit 12.6. That meets A under the wave's GPU-kernel precedent (GPU named in place of a host CPU), though the toolkit version and the SXM variant come from that snippet only.
- **Verifier notes:** README numbers (763 vs 716, 808 vs 795 TFLOPs; 3240.11 vs 3193 GB/s, with cub 3193.36 in the sum.cu header) verified. Metadata on github.com: MIT, 625 stars, 81 forks, not a fork, 17 commits, last commit 2026-08-15 (active). Lead: the 'Outperforming cuBLAS on NVFP4' substack post and gb300/nvfp4 may support a separate NVFP4-vs-cuBLASLt entry.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/README.md>
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/Makefile>
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/h100/matmul.cu>
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/h100/sum.cu>
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/gb300/nvfp4/README.md>
  - <https://github.com/pranjalssh/fast.cu>
  - <https://github.com/pranjalssh/fast.cu/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/README.md>
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/Makefile>
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/h100/matmul.cu>
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/h100/matmul/matmul_11.cuh>
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/h100/matmul/matmul_12.cuh>
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/h100/sum.cu>
  - <https://raw.githubusercontent.com/pranjalssh/fast.cu/HEAD/gb300/nvfp4/README.md>
  - <https://github.com/pranjalssh/fast.cu>
  - <https://github.com/pranjalssh/fast.cu/issues?q=is%3Aissue>
  - <https://github.com/pranjalssh/fast.cu/issues/13>
  - <https://github.com/pranjalssh/fast.cu/issues/4>
  - <https://github.com/pranjalssh/fast.cu/issues/7>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/pranjalssh/fast.cu`) · [data/wave8/enrich/raw/github_com_pranjalssh_fast_cu.json](../../../data/wave8/enrich/raw/github_com_pranjalssh_fast_cu.json) (enrichment confidence 0.8)

</details>
