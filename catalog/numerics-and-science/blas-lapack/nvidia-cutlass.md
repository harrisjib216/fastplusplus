# CUTLASS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> NVIDIA's header-only CUDA C++ templates (CuTe) and Python DSLs for building GEMM/conv kernels; matches cuBLAS at best, wins on fusion and flexibility.

| | |
|---|---|
| **Beats** | cuBLAS (cublasSgemm, run through the CUDA samples' matrixMulCUBLAS) |
| **Claimed result** | No speedup in the independent data: CUTLASS sgemm_tt 2840.5 GFLOPS (0.069216 ms) versus cuBLAS 3065.46 GFLOPS (0.064 ms), about 92.7% of cuBLAS throughput (derived from page data); the reporter says 'similar results to cublas' and a CUTLASS developer calls sgemm 'comparable to the kernel launched in the CUDA SDK example'. The project's own README claim (CUTLASS 2.x/3.x versions) is 'peak performance comparable to cuBLAS for scalar GEMM', shown only as a chart. |
| **Workload** | Single-precision GEMM, m=640, n=320, k=480 (196,608,000 flops), CUTLASS profiler kernel sgemm_tt versus the CUDA sample matrixMulCUBLAS on the same GTX 1080, posted by a user in a 2018 issue. |
| **Metric** | throughput |
| **Hardware** | GeForce GTX 1080 (compute capability 6.1) in the issue. README chart versions name NVIDIA H100, L40, A100 and A40 GPUs. |
| **Compiler and flags** | CUDA 9.2 toolkit and samples; compiler flags not stated on the page. README charts: CUTLASS 3.0 built with CUDA 12.0 and CUTLASS 3.5.1 with CUDA 12.5u1; flags not stated. |
| **Adoption** | 10.7k stars; the template layer under many deep-learning GPU kernels |
| **Last commit** | 2026-10-20 |
| **Links** | [repository](https://github.com/NVIDIA/cutlass) · [benchmark](https://github.com/NVIDIA/cutlass/issues/11) |

## Verdict

Only parity is shown. A 2018 user run (issue #11, GTX 1080, CUDA 9.2, no flags) measured CUTLASS sgemm_tt at 2840.5 GFLOPS against 3065.46 GFLOPS for the CUDA sample matrixMulCUBLAS at m=640, n=320, k=480 (about 93% of cuBLAS); a 2026 user run (issue #3390, RTX 4070 SUPER at a locked 2400 MHz, CUDA 12.8, cuBLAS 12.8.5.5, CUTLASS 4.5.1, GCC 13.3 -O3, median of CUDA events) measured the public SIMT SGEMM at 19.696 ms against 17.124 ms for cuBLAS at 8192x4096x6144, and the README charts show percent of theoretical peak, not a cuBLAS comparison.

## Use it when

- A GEMM or convolution that needs a fused epilogue (bias, activation, scaling, quantize/dequantize, reductions) that a closed cublasGemmEx/cuBLASLt call cannot express, so you save a separate elementwise kernel and a round trip through memory.
- New or unusual data types on Hopper/Blackwell: FP8, block-scaled NVFP4/MXFP formats, mixed-input (e.g. int4 weights with fp16 activations), or FP32 emulation with 3xTF32 on tensor cores.
- Grouped GEMM (MoE-style batches of different shapes) or awkward shapes where tile quantization leaves SMs idle and Stream-K or split-K decomposition helps.
- Writing your own attention, normalization or GEMM-like kernels on CuTe or the CuTe DSL; catalogued entries such as FlashAttention-4 and QuACK are built that way.
- Shape-specific tuning: cutlass_profiler --enable-best-kernel-for-fixed-shape searches tile configurations for one (m, n, k) and verifies results against cuBLAS.

## Skip it when

- Plain GEMM in standard precisions: no opened source shows CUTLASS beating cuBLAS; issue #11 (GTX 1080) has CUTLASS sgemm at about 93% of cuBLAS, and issue #3390 (RTX 4070 SUPER, 2026) has the public SIMT SGEMM 1.15x slower than cuBLAS.
- Projects that need fast builds or small binaries: kernels are instantiated per type, layout, tile and architecture, and building all profiler kernels means tens of thousands of kernels, long builds and possible linker failures.
- Windows builds (the README says CUTLASS 3.x builds are known to be down on Windows for all CUDA toolkits), pre-Volta GPUs (minimum compute capability 7.0, CUDA 11.4) and non-NVIDIA hardware.
- Teams without CUDA template expertise who only need a stable BLAS-style API: the 2.x and 3.x C++ APIs differ, and the CuTe DSL is still marked public beta in the 4.8.1 README.

## How it is fast

It decomposes GEMM hierarchically (threadblock, warp and thread tiles) to match the GPU memory hierarchy, staging operands in shared memory and registers and feeding tensor cores through mma/wgmma instructions. The main loop is software-pipelined (double buffering, multistage async copies), and Hopper/Blackwell kernels use TMA with warp specialization: producer warps load, consumer warp groups compute, in persistent cooperative or ping-pong schedules. Threadblock rasterization (swizzling) improves L2 reuse, split-K, sliced-K and Stream-K spread the K loop when output tiles cannot fill all SMs, and fused epilogues avoid extra passes over the output. CuTe layouts describe the thread and data mappings.

## Compared with alternatives

Pick CUTLASS over single-purpose hand-tuned kernels such as blackwell-tensorcore-kernels, gpu-compute or CUDA-L2 when you need a maintained, general toolkit with fusion, many data types and architectures rather than a win on one GPU and shape; those siblings report beating cuBLAS on specific shapes, which CUTLASS as shipped does not claim.

## Integration

| | |
|---|---|
| **Form** | header-only (include/ directory); CMake only for tests, examples, profiler and the generated kernel library; Python DSL as a pip package (nvidia-cutlass-dsl) |
| **Dependencies** | CUDA Toolkit; cuBLAS and cuDNN optional (used only as profiler reference/verification providers) |
| **Minimum toolchain** | C++17 host compiler, CUDA 11.4 (12.8 recommended; Blackwell needs 12.8, B300/Thor/DGX Spark 13.0); GCC 7.5 or 9+ (GCC 8.5 has known regressions) |
| **Platforms** | NVIDIA GPUs compute capability 7.0+ (Volta, Turing, Ampere, Ada, Hopper, Blackwell; Rubin SM107 in preview); tested on Ubuntu 18.04-22.04; Windows builds broken for 3.x per README |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Hopper and Blackwell tensor-core kernels need architecture-specific targets (sm_90a, sm_100a): a kernel using SM90a features built for plain sm_90 fails at runtime, and sm_100a kernels do not run on RTX 50-series (SM120) GPUs.
- Kernel choice matters more than the library: in issue #1567 a wildcard filter picked a SIMT (non-tensor-core) hgemm kernel at about 36,000 GFLOP/s against about 50,000 for cublasHgemm on a T4.
- cuBLAS itself dispatches CUTLASS-derived kernels (issue #3390's Nsight trace shows cuBLAS running cutlass_80_simt_sgemm_256x128_8x4_nn_align1), so a hand-instantiated CUTLASS kernel usually ties cuBLAS unless you add fusion or tune for the shape.
- The 4.8 README lists CUDA toolkit codegen bugs: some packed mixed-input ops compile incorrectly on Rubin (sm107a/sm107f) and are flagged rather than rewritten.

## Known shortcomings

- Not faster than cuBLAS (verifier reject not-faster overridden to keep as a parity entry): issue #11 shows sgemm_tt at 2840.5 GFLOPs against cuBLAS 3065.46, about 7% slower, and the v3.0.0 README claims only parity. The Stream-K paper's up to 6.7x over cuBLAS on some shapes is a search summary only (arXiv blocked), an enrichment lead.
- slower than cuBLAS in newer independent reports (SIMT SGEMM 1.15x slower on RTX 4070 SUPER; T4 HGEMM about 36,000 vs 50,000 GFLOP/s)

## Caveats and trade-offs

Not a faster-than-baseline result: the only measured head-to-head found is slightly slower than cuBLAS, so this entry is kept as a parity claim. The measurement is a single 2018 user post (issue opened and closed on 2018-05-21) on a small problem where launch overhead is large, one run per tool, harness timers differ (profiler versus matrixMulCUBLAS), CUDA 9.2 and an old CUTLASS release, no compiler flags. The issue's CUTLASS dgemm lines used a mismatched shape (m=640, n=480, k=320) and are not comparable. README figure for version 3.0 (opened via the v3.0.0 README, bars read by eye and not printed numbers) shows relative peak performance of roughly 85 to 100 percent per data type and layout on A100, A40, H100 and L40; the README text says 'relative to cuBLAS' but the axis is titled relative peak performance of GEMM, and the current README no longer carries any cuBLAS comparison (it shows percent of theoretical peak on Blackwell and Hopper). The v3.4.0 README figure is CUTLASS 3.1 versus 3.0, not versus cuBLAS. Several NVIDIA libraries, cuBLAS included, build on CUTLASS-style kernels, so parity is expected. A third-party page quoting 235+ TFLOPS for FP16 on H100 was blocked here and not used. The book lead says the book benchmarks its own kernel against cuBLAS, not CUTLASS; no book numbers used. Lead not verified here (arXiv and mirrors blocked; search-result summary only): the Stream-K paper (Osama, Merrill, Cecka et al., PPoPP 2023 poster, arXiv 2301.03598), implemented inside CUTLASS, reports a peak speedup of up to 6.7x over cuBLAS on A100 across 32,824 GEMM shapes, with a much smaller average gain (the summary gives about 1.06x average and 0.68x minimum for FP64) and some shapes slower. The repo's examples/47_ampere_gemm_universal_streamk compares Stream-K only with CUTLASS's own data-parallel GEMM (1.196x on 2048x2048x2048 per the source comment, A100 at locked 1005 MHz clocks), not with cuBLAS. [retier] Enricher: issue #3390 (RTX 4070 SUPER locked at 2400 MHz, CUDA 12.8, cuBLAS 12.8.5.5, CUTLASS 4.5.1, GCC 13.3 -O3): SIMT SGEMM 19.696 ms vs cuBLAS 17.124 ms (cuBLAS about 1.15x faster, derived from page data), and cuBLAS itself dispatched a CUTLASS kernel. Issue #1567: T4 SIMT HGEMM about 36,000 vs cublasHgemm about 50,000 GFLOP/s. CUTLASS 3.x Windows builds are broken.

Header-only C++ CUDA template library (CuTe, plus Python DSLs in version 4); kernels are classes with many template arguments, so compile times are long and a kernel must be instantiated per data type, layout, tile shape and architecture; per-architecture tuning (Hopper, Blackwell) is left to the user or the profiler. Offers fusions and epilogues that a closed cuBLAS call cannot.

## Maintenance

Very active (CUTLASS 4.8.1, Oct 2026; last commit 2026-10-20; 10.7k stars), BSD-3-Clause and header-only, so easy to vendor, though API generations (2.x, 3.x, CuTe DSL) and per-architecture targets change often.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification B, tier now C.
- **Tier reason:** NVIDIA/cutlass issue #11 (2018-05-21, one user, GTX 1080, CUDA 9.2 samples path, no flags) shows sgemm_tt 2840.5 GFLOPs (0.069216 ms) against matrixMulCUBLAS 3065.46 GFlop/s (0.064 ms), i.e. CUTLASS about 7 percent slower; a single user run with no methodology is C, and the v3.0.0 README chart (CUDA 12.0; 'Relative Peak Performance of GEMM', bars about 85 to 100 percent) and text claim only parity ('comparable to cuBLAS'), so no source opened shows CUTLASS faster than cuBLAS.
- **Verifier notes:** Record is accurate (numbers, dates, developer quote 'comparable to the kernel launched in the CUDA SDK example', 10.7k stars, BSD-3-Clause, last commit 2026-10-20, current README has no cuBLAS speed comparison); verdict is not-faster because the claim is parity and the measured head-to-head is slower. Notable project (10.7k stars), so per catalog policy it may be kept as a parity entry with this shortcoming. Enrichment lead: the Stream-K paper (CUTLASS-based, peak up to 6.7x over cuBLAS per search summary) could support a shape-specific win if a reachable copy is found.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-182 (wave 8 book seed pass, 2026-10-24); enrichment (wave 8 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/NVIDIA/cutlass/issues/11>
  - <https://github.com/NVIDIA/cutlass>
  - <https://github.com/NVIDIA/cutlass/commits>
  - <https://raw.githubusercontent.com/NVIDIA/cutlass/v3.0.0/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/cutlass/v3.0.0/media/images/cutlass-3.0-gemm-peak-performance.png>
  - <https://raw.githubusercontent.com/NVIDIA/cutlass/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/cutlass/HEAD/examples/47_ampere_gemm_universal_streamk/ampere_gemm_universal_streamk.cu>
- **Sources the enricher read:**
  - <https://github.com/NVIDIA/cutlass>
  - <https://raw.githubusercontent.com/NVIDIA/cutlass/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/cutlass/HEAD/media/docs/cpp/profiler.md>
  - <https://raw.githubusercontent.com/NVIDIA/cutlass/HEAD/media/docs/cpp/efficient_gemm.md>
  - <https://github.com/NVIDIA/cutlass/issues/11>
  - <https://github.com/NVIDIA/cutlass/issues?q=is%3Aissue+cublas+slower>
  - <https://github.com/NVIDIA/cutlass/issues/3390>
  - <https://github.com/NVIDIA/cutlass/issues/1567>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nvidia/cutlass`) · [data/wave8/enrich/raw/github_com_nvidia_cutlass.json](../../../data/wave8/enrich/raw/github_com_nvidia_cutlass.json) (enrichment confidence 0.75)

</details>
