# learn-cuda attention (hand-written SM120 flash attention)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Study only · `CUDA C++ with inline PTX (PyTorch harness)` · `no license` · 🟢 active

> Educational \~300-line CUDA C++ FlashAttention-2 forward kernel; 4-6% faster than flash-attn on one RTX 5090 shape, 3% slower than cuDNN.

| | |
|---|---|
| **Beats** | flash-attn (FlashAttention-2 package) and PyTorch F.sdpa FlashAttention backend; PyTorch F.sdpa cuDNN backend is NOT beaten |
| **Claimed result** | 07_attention/README.md (RTX 5090 at 400W, CUDA 12.9, SOL 209.5 TFLOPS): kernel v5 197.74 TFLOPS (94.39% of SOL) vs flash-attn 190.58 TFLOPS (90.97%, 1.04x derived from page data) and F.sdpa FlashAttention backend 186.73 TFLOPS (89.13%, 1.06x derived from page data); F.sdpa cuDNN backend reaches 203.61 TFLOPS (97.19%), so v5 is about 3% slower than cuDNN (0.97x, derived from page data). |
| **Workload** | Attention forward only, non-causal, no mask, bf16, head_dim 128 (fixed in 07_attention/main.py), batch 1, 8 heads, len_query 4096, len_kv 8192, RTX 5090 at 400W, theoretical limit 209.5 TFLOPS. |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 5090 at 400W; host CPU not stated |
| **Compiler and flags** | CUDA 12.9 (README); kernels JIT-built with torch.utils.cpp_extension.load and extra_cuda_cflags ['-lineinfo', '--ptxas-options=-v'] on top of PyTorch defaults (07_attention/main.py); PyTorch and flash-attn versions not stated. |
| **Adoption** | 490 stars |
| **Last commit** | 2026-09-07 |
| **Links** | [repository](https://github.com/gau-nernst/learn-cuda) · [benchmark](https://github.com/gau-nernst/learn-cuda/blob/HEAD/07_attention/README.md) |

## Verdict

On one RTX 5090 capped at 400W (CUDA 12.9, bf16, head_dim 128, 8 heads, 4096 queries x 8192 keys, non-causal), the author's harness timed v5 at 197.74 TFLOPS (median from triton do_bench), against 190.58 for the flash-attn package (about 1.04x) and 186.73 for PyTorch SDPA's FlashAttention backend (about 1.06x), but behind SDPA's cuDNN backend at 203.61 TFLOPS (about 0.97x). PyTorch and flash-attn versions and the host CPU are not stated.

## Use it when

- You want a short, readable reference for a near-roofline FlashAttention-2 forward pass in raw CUDA C++ and inline PTX, with each optimization isolated in its own file (swizzling, pipelining, ldmatrix.x4).
- You are writing your own attention kernel for consumer Blackwell (RTX 5090, sm_120) or Ampere/Ada-class GPUs and need a working baseline to modify, for example to try MXFP8/NVFP4 MMA, which the author cites as the reason for using CUDA C++ instead of Triton.
- Non-causal bf16 prefill-style attention with head_dim 128 and sequence lengths that are multiples of 64, where you can verify the result yourself against F.scaled_dot_product_attention.

## Skip it when

- Production inference or training: use PyTorch SDPA with the cuDNN backend (203.61 vs 197.74 TFLOPS on the author's own benchmark), flash-attn or FlashInfer, which handle masks, varlen, GQA and backward.
- Any head_dim other than 128: the host wrapper prints an error and calls exit(1), terminating the Python process.
- Sequence lengths not divisible by 64: the kernel has no tail handling or KV masking, so partial tiles read out of bounds and produce wrong results.
- Causal attention, masks, dropout, fp16 or fp8 inputs, or training (no backward kernel).
- Anything you need to redistribute: the repository has no license file.

## How it is fast

FlashAttention-2 partitioning: each 128-thread block owns a 64-row query tile, the four warps split those rows, and every warp streams through 64-row K/V tiles with an online softmax (running row max and sum, rescaling the output accumulator) so the attention matrix is never materialized. Data moves global to shared with cp.async into XOR-swizzled shared memory to avoid bank conflicts, then to registers with ldmatrix.x4 (transposed for V), and both matmuls use bf16 mma.sync.m16n8k16 tensor-core instructions with fp32 accumulators. v5 double-buffers K and overlaps the next K and V loads with the softmax and the matmuls (2-stage cp.async pipeline).

## Compared with alternatives

Pick this over FlashAttention-3, ThunderKittens or SageAttention only when you want to learn from or fork a minimal kernel: FA3 targets Hopper, SageAttention trades precision for speed on RTX 5090-class GPUs, and both are maintained libraries, whereas this is roughly 300 lines you can read in one sitting.

## Integration

| | |
|---|---|
| **Form** | source-drop (PyTorch C++/CUDA extension JIT-built with torch.utils.cpp_extension.load) |
| **Dependencies** | PyTorch with CUDA (cpp_extension, pybind11), CUDA toolkit (README results with CUDA 12.9); the harness also uses triton.testing.do_bench and pandas, and flash-attn optionally |
| **Minimum toolchain** | CUDA 12.x with an sm_80+ target (mma.sync bf16, cp.async, ldmatrix); README results use CUDA 12.9; exact minimum not documented |
| **Platforms** | NVIDIA GPUs sm_80 and newer that support mma.sync bf16 (measured only on RTX 5090, sm_120); not for AMD/Intel |
| **Thread safety** | not documented; kernels launch on the default CUDA stream rather than PyTorch's current stream |
| **Drop-in for the baseline** | partial — same (Q, K, V) to O semantics as F.scaled_dot_product_attention for non-causal, unmasked, bf16, head_dim 128, contiguous [B, H, L, D] inputs only |

## Gotchas

- attention.cpp does not check dtype, device or contiguity and takes raw data pointers, flattening batch x heads; a transposed or non-contiguous tensor gives silently wrong output.
- Kernels launch with &lt;&lt;&lt;&gt;&gt;&gt; on the default stream, ignoring torch.cuda.current_stream(); code running on other streams can race or serialize.
- Softmax uses the fast-math __expf and P is rounded to bf16 before the P@V matmul (as in FA2); the harness checks output only with torch.testing.assert_close defaults on one random shape.
- The harness default is --bs 4 while the README table states bs=1; reproduce with --bs 1 to compare numbers.

## Known shortcomings

- Slower than cuDNN SDPA (197.74 vs 203.61 TFLOPS); learning repo with no license.
- Correctness: no tail handling or KV masking, so sequence lengths not divisible by 64 read out of bounds and give wrong output; head_dim != 128 calls exit(1); no dtype or contiguity checks. Launches on the default stream, not torch's current stream. Uses sm80 mma.sync PTX with nothing SM120-specific, so 'SM120 flash attention' overstates it. No licence.

## Caveats and trade-offs

Learning repository, not a library: one shape, forward only, non-causal, bf16, head_dim 128, no masking or varlen. Faster than flash-attn and PyTorch's FlashAttention backend by only 4-6% and slower than cuDNN SDPA (197.74 vs 203.61 TFLOPS), so it documents a negative result against cuDNN. No LICENSE file (raw LICENSE, LICENSE.md, LICENSE.txt and COPYING all 404; no license shown on the repo page), so reference only. The harness default is bs=4 while the README states bs=1. Host CPU and library versions not stated.

Educational repository; single benchmark shape and one GPU (consumer Blackwell SM120); no stated support matrix.

## Maintenance

The repo gets commits (last 2026-09-07), but this is a personal learning repository with no license, so treat it as reference reading only; the attention kernel was written up in an August 2025 blog post (gau-nernst.github.io/fa-5090, blocked here and known only from search snippets).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** 07_attention/README.md gives one first-party RTX 5090 measurement against flash-attn and PyTorch SDPA (FlashAttention and cuDNN backends), produced by the public harness 07_attention/main.py (triton do_bench median, output checked with assert_close); host CPU and PyTorch/flash-attn versions are not stated, so C, not A.
- **Verifier notes:** Metadata confirmed via github.com: no license shown, 490 stars, 66 forks, 271 commits, not archived/fork, last commit 2026-09-07 ('rename'). Head dim (128) and dtype (bf16) filled in from main.py. Shortcoming: slower than cuDNN SDPA; educational code without a license.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/gau-nernst/learn-cuda>
  - <https://github.com/gau-nernst/learn-cuda/commits>
  - <https://github.com/gau-nernst/learn-cuda/tree/HEAD/07_attention>
  - <https://raw.githubusercontent.com/gau-nernst/learn-cuda/HEAD/07_attention/README.md>
  - <https://raw.githubusercontent.com/gau-nernst/learn-cuda/HEAD/07_attention/main.py>
  - <https://raw.githubusercontent.com/gau-nernst/learn-cuda/HEAD/README.md>
  - <https://raw.githubusercontent.com/gau-nernst/learn-cuda/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/gau-nernst/learn-cuda>
  - <https://raw.githubusercontent.com/gau-nernst/learn-cuda/HEAD/README.md>
  - https://raw.githubusercontent.com/gau-nernst/learn-cuda/HEAD/LICENSE (404)
  - <https://github.com/gau-nernst/learn-cuda/tree/HEAD/07_attention>
  - <https://raw.githubusercontent.com/gau-nernst/learn-cuda/HEAD/07_attention/README.md>
  - <https://raw.githubusercontent.com/gau-nernst/learn-cuda/HEAD/07_attention/main.py>
  - <https://raw.githubusercontent.com/gau-nernst/learn-cuda/HEAD/07_attention/attention.cpp>
  - <https://raw.githubusercontent.com/gau-nernst/learn-cuda/HEAD/07_attention/attention_v5.cu>
  - <https://raw.githubusercontent.com/gau-nernst/learn-cuda/HEAD/07_attention/common.h>
  - https://gau-nernst.github.io/fa-5090/ (EGRESS_BLOCKED; date and motivation from WebSearch snippets)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/gau-nernst/learn-cuda`) · [data/wave8/enrich/raw/github_com_gau_nernst_learn_cuda.json](../../../data/wave8/enrich/raw/github_com_gau_nernst_learn_cuda.json) (enrichment confidence 0.8)

</details>
