# Liger-Kernel

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (Triton kernels)` · `BSD-2-Clause` · 🟢 active

> Triton kernels that monkey-patch Hugging Face LLMs for training; mainly cut memory, with roughly 15-40% end-to-end throughput gains over eager PyTorch.

| | |
|---|---|
| **Beats** | Hugging Face Transformers default PyTorch eager modeling code (RMSNorm, RoPE, SwiGLU, cross-entropy, fused linear cross-entropy) |
| **Claimed result** | README: 'increase throughput by more than 20% and reduce memory usage by 60%' (LLaMA 3-8B, batch 8, bf16, AdamW, gradient checkpointing, FSDP1, 8 A100s; chart images); Hugging Face Trainer example 'Train LLaMA 3-8B \~20% faster with over 40% memory reduction' (4 A100s, FSDP); Lightning Trainer 15% throughput and 40% less memory (8 A100s, DeepSpeed ZeRO3); Medusa retraining 40% throughput and 80% less memory (8 A100s, FSDP). Kernel level, benchmark/data/all_benchmark_data.csv, full forward+backward median time ratio vs the huggingface provider (derived from page data): cross_entropy 2.40x to 2.87x, rms_norm 1.11x to 8.63x (median 4.56x), rope 1.88x to 10.24x (median 4.19x), but fused_linear_cross_entropy 0.46x to 0.89x (slower; it trades speed for memory), layer_norm 0.30x to 1.88x, group_norm 0.51x to 3.59x, embedding 0.72x to 1.27x. Versus the torch provider: softmax 0.08x to 1.81x (median 0.33x, i.e. mostly slower); versus torch_compile: embedding 0.50x to 0.80x (slower). README H100 table for the newer fused scaled cross-entropy (H=4096, V=131072, BF16): CuTe SM90 forward 3.12 ms vs Verl Torch fallback 11.36 ms at M=2048 (3.6x, derived from page data); B200 cuTile full 11.36 ms vs Torch 12.85 ms, backward slower (8.35 vs 7.15 ms). |
| **Workload** | LLM training: LLaMA 3-8B, batch size 8, bf16, AdamW, gradient checkpointing, FSDP1 on 8 A100s; plus Hugging Face Trainer, Lightning and Medusa example runs. |
| **Metric** | throughput |
| **Hardware** | 8x NVIDIA A100 (host CPU not stated) |
| **Compiler and flags** | Benchmark conditions per README: LLaMA 3-8B, batch size 8, bf16, AdamW, gradient checkpointing, FSDP1; no Triton/PyTorch versions on the README page. |
| **Adoption** | 6.6k stars; sponsored CI from NVIDIA, AMD, Intel, Hugging Face |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/linkedin/Liger-Kernel) · [benchmark](https://github.com/linkedin/Liger-Kernel) |

## Verdict

End to end, the README charts show more than 20% higher throughput and 60% less memory than stock Hugging Face eager code for Llama 3-8B training (bf16, batch 8, AdamW, gradient checkpointing, FSDP1, 8x A100); the example scripts report 15-40% throughput gains. At kernel level, the repo's benchmark CSV (median timings of full forward+backward, versus the Hugging Face modules, on A100/H100/B200/RTX GPUs with the Liger version recorded but no Triton/PyTorch versions) gives cross-entropy 2.40-2.87x, RMSNorm 1.11-8.63x and RoPE 1.88-10.24x, with fused linear cross-entropy slower (0.46-0.89x) but 1.4-4.8x lighter on memory.

## Use it when

- Fine-tuning or pretraining a supported Hugging Face causal LM (Llama, Qwen, Gemma, Mistral, Phi, DeepSeek and others) where large vocabularies (128k+) make the logits plus cross-entropy step the activation-memory peak; fused linear cross-entropy lets you raise batch size or context (the README chart: Hugging Face OOMs at 4K context while Liger reaches 16K on 8 A100s).
- Eager-mode PyTorch training with FSDP, DeepSpeed or DDP where you cannot or do not want to rely on torch.compile.
- Alignment or distillation losses on large-vocabulary models, where the chunked fused-linear losses save memory (benchmark CSV, CPO/ORPO/SimPO/KTO versus the Hugging Face references: 1.04-1.31x faster and up to 3.9-8.9x less memory, though ORPO uses more memory on one shape, 0.86x).
- Mixed GPU fleets: the same Triton code is run in CI on NVIDIA, AMD and Intel GPUs and on Ascend NPUs.

## Skip it when

- When raw speed of the loss step is the goal: the repo's own CSV shows fused linear cross-entropy at 0.46-0.89x the speed of the Hugging Face baseline (it trades time for memory), and fused_linear_jsd at a median 0.54x.
- Standalone softmax, embedding or Megatron RMSNorm: Liger is slower than torch on most measured shapes (softmax median 0.33x, embedding 0.50-0.80x versus torch.compile, megatron_rms_norm median 0.63x), and layer_norm/group_norm drop to 0.30x/0.51x on some shapes.
- Inference serving: the kernels target training (forward plus backward); use FlashInfer, FasterTransformer or engine-native kernels instead.
- Models or Transformers versions outside the patching table: monkey-patching depends on Hugging Face module names and has broken on upstream changes (issues #543 and #723).
- Code that reuses the logits after passing them to LigerCrossEntropyLoss: the in-place gradient write can silently corrupt gradients (open issue #272).

## How it is fast

Kernel fusion of memory-bound elementwise and row-reduction ops (one Triton program per row, with the forward pass caching per-row rstd for backward), so the gain comes from fewer HBM round trips and kernel launches. Cross-entropy computes the gradient during the forward pass and writes it in place over the logits tensor, so the backward pass only rescales it. Fused linear cross-entropy chunks the batch x tokens dimension so the full BT x V logits matrix is never materialized (by default transient logits are bounded at about BT x H elements), which is where most of the 60% memory saving comes from. Optional cuTile and CuTe-DSL backends (LIGER_KERNEL_IMPL) provide Hopper/Blackwell variants of some kernels.

## Compared with alternatives

Pick Liger over QuACK when you want a one-line patch for Hugging Face models that also runs on AMD, Intel and Ascend; QuACK's CuTe-DSL memory-bound kernels report higher throughput than Liger v0.5.10 on H100 but are NVIDIA-only. Pick it over LightSeq when your models come from current Hugging Face Transformers rather than LightSeq's own Transformer layers.

## Integration

| | |
|---|---|
| **Form** | module (pip package liger-kernel; pure Python plus Triton JIT, optional native liger-cute-kernels wheel) |
| **Dependencies** | torch &gt;= 2.1.2 and triton &gt;= 2.3.1 (CUDA); triton &gt;= 3.0.0 with ROCm PyTorch; torch &gt;= 2.6.0 for Intel XPU; torch/torch_npu 2.9.0 and triton-ascend 3.2.2 for Ascend; transformers for the patching APIs; optional cuda-tile, nvidia-cutlass-dsl &gt;= 4.6.0, liger-cute-kernels with NVSHMEM |
| **Minimum toolchain** | Python 3.10+; torch 2.1.2 and Triton 2.3.1 on CUDA; CUDA Toolkit 13.1+ for the optional cuTile backend; CUDA 12.9 for the native LCK wheel |
| **Platforms** | Anything Triton supports: NVIDIA GPUs (benchmark CSV covers A100, H100, B200, RTX 3090/4090), AMD ROCm GPUs, Intel XPU, Ascend NPU; CuTe-DSL and native kernels only on Hopper/Blackwell |
| **Thread safety** | not documented; native TP/EP kernels are collectives that must be called in the same order on every rank |
| **Drop-in for the baseline** | partial — the one-line patch replaces Hugging Face modules for listed model families, but cross-entropy overwrites its input logits and the patch is tied to specific Transformers module layouts |

## Gotchas

- LigerCrossEntropy stores the gradient in the logits buffer during forward without bumping PyTorch's version counter, so autograd cannot detect a later reuse of those logits; issue #272 shows gradients differing from F.cross_entropy (open since 2024-09).
- With bf16 parameters and accum_dtype=None, fused linear cross-entropy accumulates grad_weight/grad_bias in bf16; pass accum_dtype=torch.float32 if you need fp32 accumulation.
- The fused linear cross-entropy forward calls .item() (a CUDA synchronization, noted as a TODO in the source), and an optional CuTe-DSL backend raises an error if it is selected on an unsupported device.
- The headline 20% throughput and 60% memory numbers are images measured against untuned eager Hugging Face code (no torch.compile, Llama 3-8B, FSDP1, 8 A100s); kernel-level gains vary from 0.3x to 10x by op and shape.

## Known shortcomings

- Its own CSV shows softmax at a median 0.33x of torch, fused linear cross-entropy at 0.46-0.89x of HF, and embedding slower than torch.compile; wins are mostly memory, not speed.
- Open #272: the in-place cross-entropy gradient write skips autograd version tracking, so gradients come out silently wrong if logits are reused. FLCE accumulates grad_weight in bf16 by default (accum_dtype=None). Per the repo CSV, FLCE runs 0.46-0.89x the speed of HF, softmax median 0.33x of torch and megatron_rms_norm median 0.63x, so many kernels are slower than baseline.

## Caveats and trade-offs

End-to-end throughput charts are images; the end-to-end baseline is untuned eager Hugging Face (no torch.compile). The repo's own kernel benchmark data show many Liger kernels slower than the reference on some or most shapes: fused linear cross-entropy is 0.46x to 0.89x the speed of Hugging Face (its gain is memory), softmax is a median 0.33x of torch, embedding is slower than torch.compile, and layer_norm/group_norm drop to 0.30x/0.51x on some shapes. The QuACK (Dao-AILab) report of Liger softmax throughput falling from about 3.0 to 2.0 TB/s at large reduction dims on H100 was carried from the search record and not re-checked. No Triton/PyTorch versions or host CPU on the README. The baseline is not oneDNN/cuDNN/XNNPACK/Eigen.

Drop-in patches for Hugging Face models via one line; Triton only, so NVIDIA/AMD/Intel GPUs. Memory saving from fused linear cross-entropy (chunked logits) is as important as the speed gain.

## Maintenance

Very active (v0.8.4 on PyPI 2026-09-30, commits through 2026-09-30, CI on NVIDIA/AMD/Intel/Ascend), BSD-2-Clause, and widely integrated, so it is safe to adopt; pin the Transformers version you patch against.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README headline numbers are first-party (end-to-end chart images plus text), and the public kernel benchmark suite (benchmark/scripts, results in benchmark/data/all_benchmark_data.csv with GPU names and Liger versions) gives no host CPU or Triton/PyTorch versions, so C. The ICML 2025 CODEML workshop paper (OpenReview) could not be opened (openreview.net blocked), so B is not confirmed.
- **Verifier notes:** Metadata confirmed via github.com: BSD-2-Clause, 6.6k stars, 613 forks, 952 commits, not archived/fork, last commit 2026-09-30. Paper: 'Liger-Kernel: Efficient Triton Kernels for LLM Training', CODEML Workshop @ ICML25 per README citation (peer-reviewed workshop; not opened). Shortcoming worth recording: several kernels are slower than PyTorch per the repo's own CSV.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/linkedin/Liger-Kernel>
  - <https://github.com/linkedin/Liger-Kernel/commits>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/README.md>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/benchmark/data/all_benchmark_data.csv>
- **Sources the enricher read:**
  - <https://github.com/linkedin/Liger-Kernel>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/README.md>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/benchmark/data/all_benchmark_data.csv>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/setup.py>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/src/liger_kernel/ops/fused_linear_cross_entropy.py>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/src/liger_kernel/ops/cross_entropy.py>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/src/liger_kernel/ops/rms_norm.py>
  - <https://raw.githubusercontent.com/linkedin/Liger-Kernel/HEAD/src/liger_kernel/ops/utils.py>
  - <https://github.com/linkedin/Liger-Kernel/issues?q=is%3Aissue%20label%3Abug>
  - <https://github.com/linkedin/Liger-Kernel/issues/272>
  - <https://pypi.org/pypi/liger-kernel/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/linkedin/liger-kernel`) · [data/wave8/enrich/raw/github_com_linkedin_liger_kernel.json](../../../data/wave8/enrich/raw/github_com_linkedin_liger_kernel.json) (enrichment confidence 0.8)

</details>
