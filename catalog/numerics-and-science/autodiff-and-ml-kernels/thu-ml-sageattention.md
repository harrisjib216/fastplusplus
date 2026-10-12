# SageAttention (SageAttention, SageAttention2, SageAttention2++)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `CUDA/C++ and Triton with Python API` · `Apache-2.0` · 🟢 active

> Quantized (INT8 QK, FP8/FP16 PV) forward attention kernels for NVIDIA GPUs that outrun FlashAttention2 and match FlashAttention3-FP8.

| | |
|---|---|
| **Beats** | FlashAttention2 (also FlashAttention3 and FlashAttention3-FP8) |
| **Claimed result** | README news item (2025-02-15): 'On RTX5090, SageAttention reaches 560T, 2.7x faster than FlashAttention2!'; (2025-01-28) on Hopper (H100, H800, H20) it 'matches the speed of FlashAttention3-FP8' with better accuracy. README end-to-end table, CogVideoX1.5-5B on an NVIDIA H20: FlashAttention2 25'34'', FlashAttention3 17'32'', FlashAttention3-FP8 12'14'', SageAttention 12'07'' (about 2.1x over FlashAttention2 and 1.45x over FlashAttention3, derived from page data). GitHub description: 'speedup of 2-5x compared to FlashAttention'. Per-GPU kernel TOPS plots are images only. ICLR 2025 abstract (seen via a search result; arXiv blocked here): OPS about 2.1x FlashAttention2 and 2.7x xformers; SageAttention2 abstract (same source): about 3x FlashAttention2 and 4.5x xformers on RTX 4090. |
| **Workload** | Quantized (INT8 QK^T, FP8 or FP16 PV) attention kernel TOPS on RTX 5090, RTX 4090, L20, H100, H20, A100 and RTX 3090 (head dim 128), plus end-to-end video, image and language model speed. |
| **Metric** | throughput |
| **Hardware** | RTX 5090 (560 TOPS stated in text); RTX 4090, L20, H100, H20, A100, RTX 3090 shown in README figures; host CPU not stated |
| **Adoption** | 4,000 stars, 521 forks (GitHub page); PyPI sageattention latest 1.0.6 (2024-11-20) |
| **Last commit** | 2026-01-17 |
| **Links** | [repository](https://github.com/thu-ml/SageAttention) · [benchmark](https://github.com/thu-ml/SageAttention) |

## Verdict

First-party kernel benchmarks (bench/ scripts using the flash-attn benchmark API, head_dim 64/128) on RTX 5090/4090/3090, L20, A100/A800/A6000, H100/H20/H800 show the INT8/FP8 kernels above FlashAttention2, for example 560 TOPS on RTX 5090 (2.7x FlashAttention2), and level with FlashAttention3-FP8 on Hopper; CogVideoX1.5-5B end-to-end on an H20 takes 12'07'' vs 25'34'' (FA2) and 17'32'' (FA3). The results are backed by ICLR 2025 and ICML 2025 papers, but CUDA version and flags for the plots are not stated, and the kernel figures leave out quantization time.

## Use it when

- Inference of video and image diffusion transformers (CogVideoX, HunyuanVideo, Mochi examples in the repo) where attention dominates runtime on long token sequences.
- Consumer and workstation GPUs (RTX 3090/4090/5090, L20, A6000) where FlashAttention3 is not available and FlashAttention2 is the realistic baseline.
- Hopper (H100/H20/H800) inference where you would otherwise use FlashAttention3-FP8 and want similar speed with less quantization error.
- Head dimension 64 or 128 with FP16/BF16 inputs, including GQA, varlen batches (sageattn_varlen) and causal masks with qo_len == kv_len.

## Skip it when

- Training or anything needing gradients: the SageAttention2 API in sageattention/core.py has no backward pass.
- Head dimension above 128: the wrappers raise 'Unsupported head_dim'; sizes below 64 or between 64 and 128 are zero-padded, which wastes work.
- Numerically strict workloads that need results close to exact FP16 attention: outputs are approximate, and open issues report black/NaN outputs with some models (#273, #221, #164 on RTX 50xx).
- Very long sequences (above roughly 100k-160k tokens) until the open int32 overflow and FP8 PV corruption issues (#386, #388) are fixed.
- Pre-Ampere GPUs (compute capability below 8.0), AMD or CPU: setup.py only builds sm80, 86, 89, 90, 100, 120 and 121, and the sageattn() dispatcher has no branch for sm100 (B200), so it raises 'Unsupported CUDA architecture' there; SageAttention3 for Blackwell is a separate package in sageattention3_blackwell/.

## How it is fast

Q and K are quantized to INT8 (per-block, per-warp or per-thread granularity) after 'smoothing' K by subtracting its mean over the sequence, which removes channel outliers so the INT8 error stays small. QK^T then runs on INT8 tensor cores (mma / Hopper WGMMA), and PV runs in FP8 (sm89/sm90/sm120) or FP16 with an FP16 accumulator. A two-level accumulation strategy for FP8 PV (SageAttention2++, pv_accum_dtype='fp32+fp16') recovers accuracy lost to the FP8 MMA accumulator. The kernels keep the FlashAttention-style tiled online softmax, so the gain over FlashAttention2 comes from faster low-precision tensor-core throughput, not a different algorithm.

## Compared with alternatives

Pick SageAttention over FlashAttention-3 for inference on Ada/Ampere/Blackwell consumer GPUs or when lossy INT8/FP8 attention is acceptable; keep FlashAttention-3 for training and exact attention on Hopper. Use FFPA instead when head_dim exceeds 128 (SageAttention stops at 128), and FlashInfer for paged-KV LLM decode serving.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Python &gt;=3.9, PyTorch &gt;=2.3.0, Triton &gt;=3.0.0, CUDA toolkit (nvcc) for the source build; flash-attn only for benchmarking |
| **Minimum toolchain** | CUDA 12.0 (Ampere), 12.3 (Hopper FP8), 12.4 (Ada FP8), 12.8 (Blackwell or SageAttention2++); C++17 (setup.py passes -std=c++17 to g++ and nvcc) |
| **Platforms** | Linux with NVIDIA GPUs sm80/86/89/90/100/120/121 (Ampere, Ada, Hopper, Blackwell); other OSes not documented |
| **Thread safety** | not documented; the wrappers call torch.cuda.set_device(v.device) as a workaround for illegal memory access in multi-GPU torchrun runs |
| **Drop-in for the baseline** | partial — same q/k/v call shape as F.scaled_dot_product_attention / flash_attn, but forward-only, head_dim &lt;= 128, approximate numerics, and the README says monkey-patching SDPA does not work for every model |

## Gotchas

- Kernel TOPS plots exclude the quantization and K-smoothing passes (README note), so end-to-end speedup is smaller than the kernel charts suggest.
- Open issue #392 (2026-08-18): output silently diverges about 90% from eager when replayed inside a captured CUDA graph on sm120; the README only claims torch.compile support in non-cudagraphs mode.
- Open issue #386 (2026-08-11): Triton kernels compute offsets in int32, so non-contiguous views (fused QKV buffers) at about 100k tokens silently corrupt output or crash; #388 reports FP8 PV noise above about 160k tokens on sm120.
- Packaging mismatch: the README says 'pip install sageattention==2.2.0', but PyPI only has up to 1.0.6 (the Triton-only SageAttention1, 2024-11-20), whose metadata says BSD 3-Clause while the repo LICENSE is Apache-2.0; build from source to get SageAttention2/2++.

## Known shortcomings

- Kernel TOPS exclude quantize/smooth time; lossy INT8/FP8 attention; README's pip 2.2.0 is absent from PyPI (only 1.0.6); PyPI license string says BSD-3 while the repo says Apache-2.0; ICLR/ICML papers unreadable here (venue from README and search listings).
- Open silent-corruption bugs without maintainer reply: #386 int32 offset overflow in Triton kernels (\~100k tokens, non-contiguous QKV), #388 FP8 PV noise beyond \~160k tokens on sm120, #392 wrong output under CUDA graph replay; forward-only, head_dim &lt;=128; the sageattn() dispatcher has no sm100 (B200) branch and raises there; last code commit 2025-12-22.

## Caveats and trade-offs

Kernel TOPS plots exclude the quantization and smoothing time (README note), so kernel-only ratios overstate the end-to-end gain; end-to-end is shown only for selected video/image/language models. The 2.7x figure is for one GPU (RTX 5090) against FlashAttention2 only; on Hopper it only matches FlashAttention3-FP8. Speedup comes from INT8/FP8/FP4 quantization, so it is a lossy approximation of FP16 attention (the authors report negligible end-to-end metric loss). The code is Python/Triton/CUDA behind a PyTorch API, not a C++ library. The README tells users to 'pip install sageattention==2.2.0', but PyPI lists only releases up to 1.0.6; the PyPI wheel carries a BSD-3-Clause license string while the repository LICENSE is Apache-2.0. CUDA version and nvcc flags used for the published plots are not stated.

Approximate attention: INT8/FP8 (and INT4 in SageAttention2) quantization with outlier smoothing, so outputs are not bit-identical to exact attention; plug-and-play replacement for F.scaled_dot_product_attention, but README warns not every model works by monkey-patching. Tensor-core GPUs only. Kernels are CUDA plus Triton.

## Maintenance

Apache-2.0 research code from Tsinghua (4,000 stars); last code commit 2025-12-22 and README edit 2026-01-17, with silent-corruption bug reports from August 2026 still unanswered, so it is maintained but slowing down; usable if you build from source.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed papers (SageAttention, ICLR 2025; SageAttention2, ICML 2025) report kernel throughput wins over FlashAttention2; the venue is stated in the README and corroborated by search results listing the ICLR 2025 poster page and the arXiv PDF headed 'Published as a conference paper at ICLR 2025', though the papers themselves were blocked here. The repo has a public harness (bench/README.md, bench_qk_int8_pv_fp8_cuda\*.py) and names each GPU, but the CUDA/nvcc version and flags used for the plots are not stated, so not A.
- **Verifier notes:** README numbers match the record. The arXiv, OpenReview and iclr.cc pages are blocked by egress here, so peer review rests on the README plus search-result listings (as with earlier wave-8 B entries). Last commit 2026-01-17 confirmed (active). Baseline FlashAttention is itself a wave-8 entry (dao-ailab/flash-attention).
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/thu-ml/SageAttention/HEAD/README.md>
  - <https://raw.githubusercontent.com/thu-ml/SageAttention/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/thu-ml/SageAttention/HEAD/LICENSE>
  - <https://github.com/thu-ml/SageAttention>
  - <https://github.com/thu-ml/SageAttention/commits>
  - <https://pypi.org/pypi/sageattention/json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/thu-ml/SageAttention/HEAD/README.md>
  - <https://raw.githubusercontent.com/thu-ml/SageAttention/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/thu-ml/SageAttention/HEAD/setup.py>
  - <https://raw.githubusercontent.com/thu-ml/SageAttention/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/thu-ml/SageAttention/HEAD/sageattention/core.py>
  - <https://raw.githubusercontent.com/thu-ml/SageAttention/HEAD/pyproject.toml>
  - <https://pypi.org/pypi/sageattention/json>
  - <https://github.com/thu-ml/SageAttention>
  - <https://github.com/thu-ml/SageAttention/commits/main>
  - <https://github.com/thu-ml/SageAttention/tree/main/csrc>
  - <https://github.com/thu-ml/SageAttention/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/thu-ml/SageAttention/issues?q=is%3Aissue+NaN+OR+black+OR+%22illegal+memory%22>
  - <https://github.com/thu-ml/SageAttention/issues/386>
  - <https://github.com/thu-ml/SageAttention/issues/388>
  - <https://github.com/thu-ml/SageAttention/issues/392>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/thu-ml/sageattention`) · [data/wave8/enrich/raw/github_com_thu_ml_sageattention.json](../../../data/wave8/enrich/raw/github_com_thu_ml_sageattention.json) (enrichment confidence 0.8)

</details>
