# QuACK (CuTe-DSL memory-bound kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (CUTLASS CuTe-DSL)` · `Apache-2.0` · 🟢 active

> Python CuTe-DSL GPU kernels for RMSNorm, softmax and cross-entropy that reach about 3 TB/s on H100, beating torch.compile and Liger.

| | |
|---|---|
| **Beats** | cuDNN v9.10.1 (RMSNorm only), torch.compile (PyTorch 2.7.1, default mode) and Liger Kernel v0.5.10 |
| **Claimed result** | Blog: 'achieves nearly 50% more throughput (e.g., 3.01 TB/s vs 1.89 TB/s for FP32 softmax)' than torch.compile at reduction dim 262k; about 3 TB/s (\~90% of peak) for reduction dim larger than 4k; 'significantly outperforms all baselines when reduction dim &gt;= 65k for all 3 kernels' (cuDNN baseline covers RMSNorm only). |
| **Workload** | Memory-bound kernels (RMSNorm, softmax, cross-entropy; forward and backward), batch 8k to 32k rows, reduction dimension 256 to 262k, FP32 and BF16 inputs, measured as model memory throughput on H100. |
| **Metric** | throughput |
| **Hardware** | 1x NVIDIA H100 80GB HBM3 (3.35 TB/s peak) with Intel Xeon Platinum 8468 CPU |
| **Compiler and flags** | PyTorch 2.7.1 torch.compile default mode, Liger Kernel v0.5.10, cuDNN v9.10.1; QuACK requires CUDA toolkit 12.9+ and Python 3.12 (README). JIT-compiled CuTe-DSL kernels, no compiler flags stated. |
| **Adoption** | 1.2k stars (Dao-AILab, Tri Dao) |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/Dao-AILab/quack) · [benchmark](https://github.com/Dao-AILab/quack/blob/HEAD/media/2025-07-10-membound-sol.md) |

## Verdict

The authors' July 2025 blog measures model memory throughput of RMSNorm, softmax and cross-entropy (forward and backward, FP32 and BF16, batch 8k-32k, reduction dim 256-262k) on one H100 80GB HBM3 (3.35 TB/s peak) with a Xeon Platinum 8468 host, against torch.compile (PyTorch 2.7.1, default mode), Liger Kernel v0.5.10 (up to 65k only) and cuDNN v9.10.1 (RMSNorm only). QuACK holds about 3 TB/s (about 90% of peak) above 4k and reaches 3.01 vs 1.89 TB/s for FP32 softmax at 262k (about 1.59x, derived from page data, which the blog calls 'nearly 50% more'); CuTe-DSL and CUDA versions are not stated and the per-size numbers are only in a figure.

## Use it when

- LLM training or inference on H100, B200/B300 or RTX 50 GPUs where RMSNorm, softmax or cross-entropy shows up in profiles, especially with very wide rows (vocab-size cross-entropy, reduction dim 65k and up), where the blog says QuACK beats every baseline.
- Replacing torch.compile-generated norm or softmax kernels in eager PyTorch code; at reduction dim 262k FP32 softmax it reports 3.01 vs 1.89 TB/s.
- Fused RMSNorm with residual add, prenorm output, per-head (B, S, H, D) weights or Gemma-style weight_offset in a single kernel.
- Teams that want readable kernel source to adapt: the blog walks through the TV-layout, load strategy and reduction helpers used in rmsnorm.py and softmax.py.
- JAX users needing a fast softmax on Hopper/Blackwell via the optional jax extra.

## Skip it when

- A100, Ada (RTX 40) or older GPUs, or AMD: the README lists only H100, B200/B300 and RTX 50 (issue #21 asks about Ada, and a ROCm backend is only an RFC, #178). Cluster reduction, the source of the long-row advantage, needs sm90+.
- C++ or non-Python inference engines: kernels are Python CuTe-DSL compiled at runtime through nvidia-cutlass-dsl, so there is nothing to link from C++.
- Small reduction dims (under about 4k), where the blog claims no advantage and the per-size results exist only in a figure.
- Inside a larger torch.compile graph: open issue #77 reports rmsnorm_fwd going from 0.0413 ms (4685 GB/s) to 0.1067 ms (1815 GB/s) on B200 when wrapped in torch.compile.
- Environments pinned to older toolchains: it needs CUDA 12.9+, a recent nvidia-cutlass-dsl (&gt;=4.7) and Python 3.12 per the README, and several open issues (#187, #188) are crashes from API drift in cuda-bindings and CUTLASS.

## How it is fast

Each row is read from HBM once with 128-bit coalesced cp.async loads into shared memory and registers, then reduced hierarchically: thread, warp (butterfly shuffle), block (shared memory) and, on Hopper and newer, thread-block cluster reduction over distributed shared memory (DSMEM), where up to 16 SMs pool their shared memory. That lets a 3-pass softmax keep a 65k-262k element row on chip instead of re-reading it, whereas torch.compile's Triton softmax reads the input twice and Liger's softmax spills registers above 32k (blog NCU analysis). The reported metric is model memory throughput (minimum bytes over time), so most of the gain over torch.compile comes from moving fewer bytes, not from faster DRAM access.

## Compared with alternatives

Pick QuACK over Liger-Kernel when you are on H100/B200-class GPUs and need the fastest standalone norm, softmax or cross-entropy, especially with rows of 65k elements or more, where Liger spills registers or does not support the size. Liger-Kernel is the easier choice for patching Hugging Face models' RMSNorm, RoPE, SwiGLU and cross-entropy in one step. FlashAttention-3 and ThunderKittens cover attention and GEMM, not these reductions.

## Integration

| | |
|---|---|
| **Form** | module (pip package quack-kernels; Python CuTe-DSL kernels JIT-compiled at first call) |
| **Dependencies** | nvidia-cutlass-dsl&gt;=4.7 (cu13 extra for CUDA 13), torch, apache-tvm-ffi&gt;=0.1.6,&lt;0.2, einops; optional nvidia-matmul-heuristics, jax + jax-tvm-ffi |
| **Minimum toolchain** | CUDA toolkit 12.9+, Python 3.12 (README; pyproject declares &gt;=3.10) |
| **Platforms** | NVIDIA H100 (sm90), B200/B300 (sm100) and RTX 50 (sm120) per the README; OS not documented |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — QuackRMSNorm subclasses torch.nn.RMSNorm and quack.softmax/cross_entropy are function-level swaps for torch.softmax and F.cross_entropy, but only for supported GPUs, dtypes (fp16, bf16, fp32) and shapes (softmax takes 2D (M, N) only) |

## Gotchas

- Kernels are compiled per dtype and row length N on first call (jit_cache), so new hidden or vocab sizes pay a one-time compile; issue #166 asks to bucket N in the norm forward cache key.
- Softmax forward multiplies by an approximate reciprocal (rcp_approx) of the denominator, so outputs differ slightly from torch.softmax; layernorm requires 2D input and fp32 weight and bias.
- Importing quack monkey-patches CuTe's tensor classes process-wide (quack.dsl indexing sugar), which can surprise other CuTe-DSL code in the same process.
- The blog's cross-entropy comparison with Liger is disputed: issue #9 notes that Liger's CE forward also computes the gradient, so timing forward alone understates Liger, and the current benchmarks/benchmark_cross_entropy.py compares only quack against torch.compile.

## Known shortcomings

- CuTe-DSL version not stated (harness public).
- Issue #9: the blog's Liger cross-entropy comparison is unfair (Liger forward also computes the gradient); the current harness benchmarks CE against torch.compile only; issue #77: rmsnorm_fwd 2.6x slower inside torch.compile on B200; softmax uses rcp_approx.

## Caveats and trade-offs

First-party blog numbers; the per-size results are only in a figure (combined_kernel_benchmarks_final.png); the text gives the 262k FP32 softmax ratio (3.01 vs 1.89 TB/s, which the blog calls 'nearly 50% more' though it is about 1.59x (derived from page data)) and the &gt;=65k claim. Liger is only benchmarked up to reduction dim 65k (larger sizes unsupported) and cuDNN only on RMSNorm. Harness is public (benchmarks/benchmark_softmax.py, benchmark_rmsnorm.py, benchmark_cross_entropy.py) but has evolved since the July 2025 blog, and the blog does not state the CuTe-DSL or CUDA versions. Baselines are 2025 versions. Below about 4k reduction dim no advantage is claimed. It is a Python CuTe-DSL kernel library for PyTorch/JAX on H100/B200/RTX 50, not a C++ library.

Needs H100, B200/B300 or RTX 50 series GPUs, CUDA 12.9+ and Python 3.12. The advantage comes from cluster reduction (thread-block clusters with distributed shared memory) on Hopper, so it targets very long reduction dimensions. Also ships Hopper/Blackwell GEMM-with-epilogue kernels.

## Maintenance

Actively developed (Apache-2.0, about 1.2k stars, 48 PyPI releases from 0.1.0 on 2025-06-20 to 0.6.5 on 2026-09-11, last commit 2026-09-13), but pre-1.0 and tracking fast-moving CUTLASS DSL releases, so pin versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The first-party blog (media/2025-07-10-membound-sol.md) states the baselines (torch.compile on PyTorch 2.7.1 default mode, Liger Kernel v0.5.10, cuDNN v9.10.1 for RMSNorm only), the hardware (1x H100 80GB HBM3 with Xeon Platinum 8468) and the quoted 3.01 vs 1.89 TB/s and &gt;=65k sentences verbatim; the harness is public (benchmarks/benchmark_softmax.py times quack, torch.compile and liger with triton do_bench). The CuTe-DSL/CUTLASS and CUDA versions used for the blog run are not stated and the per-size numbers exist only as a figure, so it stays C rather than A.
- **Verifier notes:** Blog text, README, repo page (Apache-2.0, 1.2k stars, not archived) and commits page (latest 2026-09-13) all match the record. Possible A if a later retier accepts PyTorch/Liger/cuDNN versions plus the public harness as sufficient, but the blog lacks the CuTe-DSL compiler version.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Dao-AILab/quack/HEAD/media/2025-07-10-membound-sol.md>
  - <https://raw.githubusercontent.com/Dao-AILab/quack/HEAD/README.md>
  - <https://github.com/Dao-AILab/quack>
  - <https://github.com/Dao-AILab/quack/commits>
  - <https://github.com/Dao-AILab/quack/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/Dao-AILab/quack/HEAD/benchmarks/benchmark_softmax.py>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Dao-AILab/quack/HEAD/README.md>
  - <https://raw.githubusercontent.com/Dao-AILab/quack/HEAD/media/2025-07-10-membound-sol.md>
  - <https://raw.githubusercontent.com/Dao-AILab/quack/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/Dao-AILab/quack/HEAD/quack/__init__.py>
  - <https://raw.githubusercontent.com/Dao-AILab/quack/HEAD/quack/rmsnorm.py>
  - <https://raw.githubusercontent.com/Dao-AILab/quack/HEAD/quack/softmax.py>
  - <https://raw.githubusercontent.com/Dao-AILab/quack/HEAD/quack/cross_entropy.py>
  - <https://raw.githubusercontent.com/Dao-AILab/quack/HEAD/docs/jax.md>
  - <https://raw.githubusercontent.com/Dao-AILab/quack/HEAD/benchmarks/benchmark_cross_entropy.py>
  - <https://github.com/Dao-AILab/quack/tree/main/quack>
  - <https://github.com/Dao-AILab/quack/issues>
  - <https://github.com/Dao-AILab/quack/issues/9>
  - <https://github.com/Dao-AILab/quack/issues/77>
  - <https://pypi.org/pypi/quack-kernels/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/dao-ailab/quack`) · [data/wave8/enrich/raw/github_com_dao_ailab_quack.json](../../../data/wave8/enrich/raw/github_com_dao_ailab_quack.json) (enrichment confidence 0.8)

</details>
