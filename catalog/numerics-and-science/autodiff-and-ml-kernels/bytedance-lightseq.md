# LightSeq

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++/CUDA` · `Apache-2.0` · 🔴 abandoned

> Fused CUDA Transformer layers for training and beam-search inference; 1.4-2.1x faster training than PyTorch fp16 AMP on A100.

| | |
|---|---|
| **Beats** | PyTorch fp16 mixed precision (training and inference), PyTorch QAT |
| **Claimed result** | README headline: up to 3x fp16 training vs PyTorch fp16, up to 5x int8 training vs PyTorch QAT, and up to 12x (fp16) and 15x (int8) inference vs PyTorch fp16. The README's own tables top out lower: fp16 training at 1.99x (Transformer, 512 tokens) and 2.12x (BERT, batch 8), int8 training 1.86x vs PyTorch fp16, which is about 5.2x vs PyTorch QAT at 0.36 (derived from page data); Transformer inference 11.82x fp16 and 14.44x int8 (batch 32, seq 8); BERT inference 1.82x fp16 and 2.04x int8 at batch 32, seq 128. docs/performance.md (T4, Transformer-base beam search): LightSeq is slower than FasterTransformer at batch 1 (29.66 vs 26.25 ms) and up to about 1.4x faster at batch 32 to 128; with sampling it is 0.85x to 1.40x of FasterTransformer. |
| **Workload** | Training and inference speedup for Transformer and BERT models, relative to PyTorch fp16 mixed precision; training on one A100, inference on eight A100. |
| **Metric** | throughput |
| **Hardware** | NVIDIA A100 (one for training, eight for inference) |
| **Adoption** | 3.3k stars; on PyPI as lightseq 3.0.1 (2022-11-03) |
| **Last commit** | 2023-05-10 |
| **Links** | [repository](https://github.com/bytedance/lightseq) · [benchmark](https://github.com/bytedance/lightseq/blob/master/README.md) |

## Verdict

First-party README tables give speedup ratios over PyTorch fp16 mixed precision on one A100 (training) and eight A100s (inference): fp16 training 1.44-1.99x on Transformer and 1.59-2.12x on BERT, and inference 6.2-11.8x on Transformer and 1.8-10.6x on BERT, with no raw timings, compiler flags or host CPU; the headline 'up to 3x' training figure is not in the tables. docs/performance.md (T4, Transformer-base, beam 4) has raw milliseconds against FasterTransformer: slower at batch 1, up to 1.39x faster at batch 32-128 (derived from page data).

## Use it when

- Training Fairseq or Hugging Face Transformer/BERT/GPT-2/ViT models on V100/A100-class GPUs with small token batches (512-1024 tokens), where the README tables show the largest gains (1.78-1.99x Transformer, 1.92-2.12x BERT vs PyTorch fp16).
- Seq2seq translation serving with beam search at batch 8-128 on T4-class GPUs, where docs/performance.md shows it 1.0-1.39x faster than FasterTransformer (derived from page data).
- Int8 quantisation-aware training followed by int8 inference of the same Transformer, Bert or GPT-2 model in one toolchain.
- Legacy pipelines already pinned to Python 3.6-3.8, PyTorch 1.x and Fairseq 0.10.2.

## Skip it when

- Sequences longer than 1024 tokens: the training softmax kernel throws a runtime_error above to_len 1024 (issue #197 asks for longer sequences and is unanswered); attention is materialised, not FlashAttention-style.
- Hopper or newer GPUs: the CMake and JIT arch lists stop at sm_86/sm_87, and nothing has been updated since 2023.
- Batch-1 beam search latency: on T4 it is slower than FasterTransformer (29.66 vs 26.25 ms at seq 32, 63.04 vs 54.02 ms at seq 64).
- Large token batches: training speedup flattens to about 1.44x at 4096-15000 tokens, which torch.compile or fused-kernel PyTorch paths may already match (not measured here).
- Any project needing a maintained dependency: the repository was archived on 2025-07-21 and PyPI wheels cover only Python 3.6-3.8 on Linux.

## How it is fast

Coarse-grained kernel fusion: chains of element-wise ops (bias add, dropout, residual, layer norm, softmax with mask) run as one launch around cuBLAS GemmEx calls, cutting launch count and intermediate memory traffic. The inference engine adds Hierarchical Auto-Regressive Search (HARS) to remove redundant work in beam search, plus dynamic GPU memory reuse with buffers preallocated for the maximum batch and length. LightSeq2 (SC22) adds a mixed-precision trainer that links all parameters and gradients into one contiguous workspace so the optimizer update is a single fused pass, and int8 GEMM paths for quantised training and inference.

## Compared with alternatives

Pick LightSeq over FasterTransformer or ByteTransformer when you need training acceleration as well as inference (both siblings are inference-only, and ByteTransformer covers only the BERT encoder), or when you run Fairseq beam search at batch 8 and up. For new inference deployments prefer CTranslate2, which is maintained and also covers CPUs.

## Integration

| | |
|---|---|
| **Form** | Python package (pip wheel with prebuilt inference extension; training ops JIT-compiled through torch.utils.cpp_extension and ninja) or C++ static/shared lib built with CMake; Triton backend |
| **Dependencies** | CUDA toolkit (cuBLAS, Thrust, CUB submodule), pybind11, protobuf &gt;= 3.13, HDF5; PyTorch for training; Fairseq 0.10.2, transformers or DeepSpeed for the integrations |
| **Minimum toolchain** | C++14, CMake 3.18; docs/build.md says CUDA &gt;= 10.1 and &lt; 11, but the current CMakeLists requires find_package(CUDA 11) |
| **Platforms** | Linux, NVIDIA GPUs (CMake arch lists 60-86 legacy or 70-87 new arch; training JIT defaults to 6.0/6.1/7.0 plus 8.0/8.6); the new-arch build has fp32-only x86 and arm device targets |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — Fairseq users swap fairseq-train for lightseq-train; Hugging Face models need their encoder layers replaced and weights copied; inference requires exporting to LightSeq protobuf/HDF5 |

## Gotchas

- setup.py catches any build failure of the inference extension, logs a warning and installs the training-only package anyway, so a broken CUDA build can go unnoticed until lightseq.inference is imported.
- Training layers preallocate for max_batch_tokens and max_seq_len set in get_config; exceeding either raises ValueError at forward time.
- Training kernels are JIT-compiled with -O3 --use_fast_math, so results are not bit-identical to PyTorch; the user guide warns Hugging Face BERT fine-tuning 'is unstable and may not converge', and issue #138 reports non-convergence with fairseq --update_freq.
- Open bug reports include wrong BART top-k sampling results (#256), a bug with small decoder vocab sizes (#263) and failures at batch size 1 in the Hugging Face example (#191).

## Known shortcomings

- 'Up to 3x' fp16 training is not in the README tables (max 2.12x); slower than FasterTransformer at batch 1; NAACL 2021 / SC22 papers unreadable here (possible B on retier); archived.
- Training softmax throws above 1024 tokens (message says 512; #197); setup.py swallows inference-extension build failures and installs a training-only package; docs say CUDA &lt;11 while CMakeLists requires 11; no sm_90; --use_fast_math; open bugs #256 (BART top-k wrong) and #263 (small vocab).

## Caveats and trade-offs

First-party speedup ratios without raw timings, compiler, flags or host CPU, and the headline 'up to 3x' fp16 training is not supported by the README tables (maximum 2.12x). The baseline is eager PyTorch fp16, not a tuned path; against FasterTransformer on T4 (docs/performance.md) LightSeq is slower at batch 1 and with sampling at batch 128. The only public timing script found is examples/inference/python/test/ls_bert.py (one timed call vs Hugging Face), not the harness behind the tables. The repository was archived on 2025-07-21.

Custom fused CUDA kernels on top of cuBLAS/Thrust/CUB; Transformer-family models only; Fairseq, Hugging Face and DeepSpeed compatibility; PyPI wheels only for Python 3.6 to 3.8 on Linux.

## Maintenance

Archived on 2025-07-21 with no commits since 2023-05-10, but Apache-2.0 and usable as a frozen dependency on CUDA 11-era stacks (Python 3.6-3.8 wheels, PyTorch 1.x, Ampere or older GPUs).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README speedup tables (relative to PyTorch fp16 on A100) with no raw timings, no compiler or flags, no host CPU and no harness for those tables, so C. The README cites a NAACL-HLT 2021 industry paper and the LightSeq2 paper (search results say SC22), which could support B, but arxiv.org, aclanthology.org and the authors' site were all blocked here, so neither was opened.
- **Verifier notes:** Metadata confirmed on the GitHub page: Apache-2.0 (LICENSE file), 3.3k stars, 333 forks, archived 2025-07-21, last commit 2023-05-10, latest release v3.0.0 (Oct 2022); abandoned is correct. Possible retier to B if a check can open the NAACL 2021 / LightSeq2 (SC22) papers.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bytedance/lightseq>
  - <https://github.com/bytedance/lightseq/commits>
  - <https://github.com/bytedance/lightseq/tree/master/examples>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/examples/inference/python/test/ls_bert.py>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/docs/build.md>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/docs/guide.md>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/docs/examples.md>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/setup.py>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/lightseq/csrc/kernels/cuda/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/lightseq/csrc/kernels/cuda/softmax_kernels.cu>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/lightseq/csrc/kernels/cuda/cublas_wrappers.cu>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/lightseq/training/ops/pytorch/transformer_encoder_layer.py>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/lightseq/training/ops/pytorch/builder/builder.py>
  - <https://raw.githubusercontent.com/bytedance/lightseq/HEAD/lightseq/training/ops/pytorch/builder/transformer_builder.py>
  - <https://github.com/bytedance/lightseq/issues?q=is%3Aissue+bug>
  - <https://github.com/bytedance/lightseq/issues/197>
  - WebSearch snippets: LightSeq2 (arXiv 2110.05722, SC22) and LightSeq (arXiv 2010.13887, NAACL-HLT 2021 industry track) abstracts
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/bytedance/lightseq`) · [data/wave8/enrich/raw/github_com_bytedance_lightseq.json](../../../data/wave8/enrich/raw/github_com_bytedance_lightseq.json) (enrichment confidence 0.75)

</details>
