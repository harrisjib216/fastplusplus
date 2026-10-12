# SpargeAttn (SpargeAttention)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++ (CUDA) with Python bindings; Triton example` · `Apache-2.0` · 🟢 active

> Training-free block-sparse, INT8/FP8-quantized attention kernels; 1.8-4.5x per-layer over full attention in model runs, approximate.

| | |
|---|---|
| **Beats** | FlashAttention2 (Figure 2 legend 'FlashAttn'; Table 1 'Full-Attention' does not name the implementation) |
| **Claimed result** | Table 1 (assets/exp_table.png), average per-layer speed in TOPS, Full-Attention vs SpargeAttn (sparsity): Llama3.1 128K 156.9 vs 708.1 (0.54); CogvideoX 17K 166.0 vs 507.9 (0.46); Mochi 22K 164.2 vs 582.4 (0.47); Flux 4.5K 158.2 vs 280.3 (0.38); Stable-Diffusion3.5 4.5K 164.2 vs 293.0 (0.31); about 4.5x, 3.1x, 3.5x, 1.8x and 1.8x (derived from page data). Accuracy stays near dense (e.g. Llama3.1 WikiText perplexity 6.020 vs 6.013; Mochi CLIPSIM 0.1720 vs 0.1725). Figure 2 (assets/speed_comparison.png, RTX 4090, seq 22K, head dim 128; values read from the chart, approximate): FlashAttn about 165 TOPS flat; SageAttn about 300 flat; SpargeAttn+Sage2 about 410 at sparsity 0.1 rising to about 875 at 0.6 (about 2.5-5.3x over FlashAttn, derived); SpargeAttn+Sage about 320 to 675; SpargeAttn+FA2 about 183 at 0.1 to about 370 at 0.6 (about 1.1-2.2x, derived). |
| **Workload** | Figure 2 (README image): attention kernel speed in TOPS versus sparsity on an RTX 4090, sequence length 22K, head dim 128; Table 1 (assets/exp_table.png): average per-layer attention speed in real generation runs for Llama3.1 (NeedleInAHaystack, 128K), CogVideoX (17K), Mochi (22K), Flux (4.5K) and Stable-Diffusion3.5 (4.5K), reported with accuracy metrics. |
| **Metric** | throughput |
| **Hardware** | RTX 4090 stated for Figure 2; the GPU for Table 1 is not stated in the image. |
| **Adoption** | 1.3k stars; ICML 2025 paper (arXiv 2502.18137); from the SageAttention group (thu-ml) |
| **Last commit** | 2026-02-25 |
| **Links** | [repository](https://github.com/thu-ml/SpargeAttn) · [benchmark](https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/assets/speed_comparison.png) |

## Verdict

README Figure 2 (RTX 4090, sequence 22K, head dim 128) plots kernel TOPS against sparsity: FlashAttention2 about 165, SageAttention about 300, SpargeAttn+Sage2 about 410 at sparsity 0.1 rising to about 875 at 0.6 (about 2.5-5.3x, chart readings, derived from page data). Table 1 (assets/exp_table.png, GPU not stated, older SageAttention1-based version) gives per-layer attention speed in real model runs of 1.8x (Flux, SD3.5 at 4.5K) to 4.5x (Llama3.1 at 128K) over full attention with near-dense accuracy; no compiler flags or kernel benchmark script are published.

## Use it when

- Inference of video and image diffusion transformers (CogVideoX, Mochi, Wan, Flux, SD3.5) at long token counts (17K-22K and up), where Table 1 shows 3.1-3.5x per-layer attention speedups with near-dense quality metrics.
- Long-context LLM prefill (Llama3.1 at 128K in Table 1, about 4.5x per layer) when a small accuracy loss is acceptable and you use non-causal attention or the SageAttention1-based API (see gotchas).
- Ampere, Ada or Hopper GPUs (A100, RTX 4090, H100/H20) with head dim 64 or 128 and FP16/BF16 activations.
- You already have a per-head block-sparse pattern (sliding tiles, video-locality masks) and want a fast INT8/FP8 kernel that executes it via block_sparse_sage2_attn_cuda.

## Skip it when

- Training or fine-tuning: there is no backward pass or autograd function.
- Workloads that need exact attention, or causal attention through the recommended SageAttention2-based APIs (see gotchas).
- Short sequences: at 4.5K tokens (Flux, SD3.5) the gain is only about 1.8x, sequences under 128 tokens are rejected, and at low sparsity the FlashAttention2-based variant is only about 1.1x over FlashAttention2 in Figure 2.
- Blackwell GPUs or new toolchains: setup.py lists only compute capabilities 8.0, 8.6, 8.7, 8.9 and 9.0, issue #109 (open, no reply) reports the build rejecting TORCH_CUDA_ARCH_LIST=12.0 on an RTX 5090, and issues #115/#122/#114 report build failures with CUDA 13.0, GCC 13+ and Python 3.14.
- Head dims other than 64 or 128 (you must pad and pass the softmax scale yourself).

## How it is fast

Two multipliers stack: sparsity and SageAttention-style quantization. A Triton pre-pass mean-pools each Q and K block, keeps blocks whose tokens are not self-similar, scores the pooled blocks with a softmax and keeps the top-k fraction (or a CDF threshold) of key blocks, producing a lookup table the kernel walks. The CUDA kernels quantize Q and K to INT8 (K mean-smoothed) and, on sm89/sm90, V to FP8 with FP16 or FP32 accumulation (SageAttention2/2++), and a pv_threshold variant skips further P·V work inside the kernel.

## Compared with alternatives

Pick it over SageAttention when sequences are long and attention maps are sparse: it reuses the same INT8/FP8 kernels and adds block skipping (SageAttention alone is about 300 vs FlashAttention2's 165 TOPS in Figure 2, SpargeAttn+Sage2 up to about 875). Prefer FlashAttention-3/4 when you need exact attention, a backward pass, or causal LLM training, and Chipmunk if you specifically want column-sparse attention for diffusion transformers measured against FlashAttention-3.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | PyTorch&gt;=2.3, Triton (block-map kernels), einops; ninja for the build; CUDA toolkit with nvcc |
| **Minimum toolchain** | C++17 and CUDA 12.0+ (12.4+ for sm89/sm90, 12.8+ for the SageAttention2++ FP16-accumulate path), Python 3.9+; built from source with setup.py (no wheel documented) |
| **Platforms** | Linux, NVIDIA sm80/sm86/sm87 (INT8 QK, FP16 PV), sm89 and sm90a (INT8 QK, FP8 PV); Blackwell not in setup.py's supported list; Windows source builds reported failing at link time (issue #103) |
| **Thread safety** | not documented; every call runs torch.cuda.set_device(v.device), changing the caller's current device, and issue #97 (open) reports that calling it twice can corrupt the CUDA context |
| **Drop-in for the baseline** | partial: same (q, k, v, is_causal) call shape as torch SDPA, but the default layout is HND, head dim must be 64 or 128, attn_mask and dropout_p are accepted and ignored, there is no backward, and the output is an approximation controlled by topk |

## Gotchas

- Causal masking in the recommended APIs: spas_sage2_attn_meansim_topk_cuda (and the other SageAttention2-based entry points) builds a causal block map but launches the kernel with the causal flag hard-coded to False, so the diagonal blocks run unmasked and a query can see up to 127 later tokens in its block (from reading spas_sage_attn/core.py and utils.py, not tested). The SageAttention1-based spas_sage_attn_meansim_topk_cuda passes is_causal through to the kernel.
- Silent dtype changes: output_dtype is ignored (the output takes the input dtype), and for BF16 inputs V is cast to FP16, which overflows for |v| above 65504.
- Open correctness reports against the recommended API: random black output (#110), garbled results (#106), and undefined values in masked tail loads of the block-pooling kernels when the sequence is not a multiple of the block size (#124, fix proposed in PR #125).
- The entry points are decorated with @torch.compiler.disable, so torch.compile graphs break around every attention call; the published Table 1 numbers came from the older SageAttention1-based version, and the README says the SageAttention2-based one is about 30% faster.

## Known shortcomings

- Most of the headline gain over FlashAttention2 comes from SageAttention's INT8 quantization (SageAttn alone is about 1.8x FlashAttn in Figure 2); sparsity adds the rest, and at sparsity 0.1 the FA2-based variant is only about 1.1x. No kernel benchmark script in the repo (Triton_SpargeAttn holds one example file).
- Possible correctness bug read in source (not tested, no issue filed): spas_sage2_attn_meansim_topk_cuda and the other Sage2 APIs launch the kernel with is_causal hard-coded False, and the causal mask is applied only at block level, so a query can see up to 127 later tokens; the Sage1 API passes the flag through. Forward only; attn_mask, dropout_p and output_dtype are ignored; BF16 V is cast to FP16. setup.py archs stop at 9.0 so the RTX 5090 build fails (#109); CUDA 13, GCC 13 and Python 3.14 build failures (#115, #122, #114); open wrong-output issues #110, #106, #124. Last commit 2026-02-25 with 62 open issues, so 'active' overstates it; setup.py says BSD-3 while LICENSE is Apache-2.0.

## Caveats and trade-offs

Peer reviewed (ICML 2025) and the numbers sit in the repo as images from the paper (the README states acceptance, and the rendered README shows Figure 2; Table 1 is in assets/exp_table.png, referenced only inside an HTML comment in the README). Short of tier A: no compiler, flags or CPU model, and I found no kernel benchmark script in the repo listing (evaluate/ holds model examples for CogVideoX, Flux, Hunyuan and Wan; tools/ holds gpu_process.py). The README comment says Table 1 and the paper used the SageAttention-based SpargeAttn and that the SageAttention2-based version is about 30% faster, so Table 1 and the current API differ. TOPS for sparse kernels may count only executed or dense-equivalent operations: not stated on the opened pages. The baseline is FlashAttention2, not a library on the project's list. Numbers were read from images using the image viewer; chart values are approximate.

Approximate attention: a training-free predicted block-sparse mask (block 128x64) skips work, so the 'topk' parameter trades accuracy for sparsity. The headline numbers stack sparsity on SageAttention's low-bit quantization (SpargeAttn+Sage/Sage2), so part of the gain over FlashAttention2 comes from quantized matmuls, not sparsity (SageAttention alone is about 300 vs FlashAttn about 165 TOPS in Figure 2, read from the chart). CUDA-only (CUDA 12.0+ Ampere, 12.3 Hopper fp8, 12.4 Ada fp8, 12.8 Blackwell), PyTorch 2.3+; older versions required per-model tuning, the recommended API now does not.

## Maintenance

Apache-2.0 (LICENSE and source headers; setup.py metadata says BSD 3-Clause) and copyable, but the last commit was 2026-02-25 and 62 issues are open, including unanswered build failures on CUDA 13, GCC 13 and Blackwell, so treat it as research code with slowing maintenance.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed paper (ICML 2025, per the README) whose Figure 2 (README image, RTX 4090) and Table 1 (assets/exp_table.png) show SpargeAttn ahead of FlashAttention2 / full attention in kernel TOPS and per-layer speed, with accuracy metrics. Not A: no kernel benchmark script in the repo (Triton_SpargeAttn holds only triton_kernel_example.py; evaluate/ holds model examples), and no compiler or flags are stated.
- **Verifier notes:** Numbers in the record match the two images. Worth recording: most of the headline gain over FlashAttention2 comes from SageAttention's INT8 quantization (SageAttn alone is about 1.8x FlashAttn in Figure 2), with sparsity adding the rest; at sparsity 0.1 the FA2-based variant is only about 1.1x.
- **Fields the verifier corrected:** `claimed_speedup`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/thu-ml/SpargeAttn>
  - <https://github.com/thu-ml/SpargeAttn/commits/main>
  - <https://github.com/thu-ml/SpargeAttn/tree/main/Triton_SpargeAttn>
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/README.md>
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/assets/speed_comparison.png>
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/assets/exp_table.png>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/README.md>
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/setup.py>
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/spas_sage_attn/__init__.py>
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/spas_sage_attn/core.py>
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/spas_sage_attn/utils.py>
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/spas_sage_attn/autotune.py>
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/csrc/qattn/pybind.cpp>
  - <https://raw.githubusercontent.com/thu-ml/SpargeAttn/HEAD/csrc/qattn/qk_int_sv_f8_cuda_sm89.cu>
  - <https://github.com/thu-ml/SpargeAttn/issues>
  - <https://github.com/thu-ml/SpargeAttn/issues?q=is%3Aissue+causal>
  - <https://github.com/thu-ml/SpargeAttn/issues/124>
  - <https://github.com/thu-ml/SpargeAttn/issues/109>
  - <https://github.com/thu-ml/SpargeAttn/commits/main>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/thu-ml/spargeattn`) · [data/wave8/enrich/raw/github_com_thu_ml_spargeattn.json](../../../data/wave8/enrich/raw/github_com_thu_ml_spargeattn.json) (enrichment confidence 0.75)

</details>
