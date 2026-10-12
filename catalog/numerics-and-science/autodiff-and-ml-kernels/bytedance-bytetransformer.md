# ByteTransformer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++/CUDA` · `Apache-2.0` · 🟡 stale

> Padding-free fp16 BERT encoder inference on NVIDIA GPUs; first-party A100 numbers show about 2x over PyTorch and 1.8x over FasterTransformer at long, variable lengths.

| | |
|---|---|
| **Beats** | PyTorch 1.13.0, TensorFlow, FasterTransformer, DeepSpeed (BERT-base inference) |
| **Claimed result** | Batch 16, max sequence length 1024: ByteTransformer 24.70 ms vs PyTorch 53.21, TensorFlow 65.94, FasterTransformer 50.28 (45.22 with remove-padding), DeepSpeed 59.96 (about 2.2x vs PyTorch and 1.8x vs FasterTransformer with remove-padding, derived from page data). Batch 1, max 1024: 3.16 ms vs PyTorch 4.2, TensorFlow 6.37, FasterTransformer 4.51, DeepSpeed 4.86. |
| **Workload** | Standard BERT encoder (12 layers, 12 heads x 64, fp16 per benchmark/bert_bench.sh) execution time (ms) on an A100 at batch 1 and batch 16, sequence lengths 64 to 1024, average length 0.6 of maximum. |
| **Metric** | latency |
| **Hardware** | NVIDIA A100 GPU (variant and host CPU not stated); CUDA 11.6, PyTorch 1.13.0+cu116, Python 3.9.16 |
| **Compiler and flags** | CUDA 11.6 nvcc via CMake (-DDataType=FP16, CUDAARCHS=80, -rdc=true); build type, optimisation level and host compiler not stated |
| **Adoption** | 481 stars; deployed in ByteDance in-house serving |
| **Last commit** | 2024-03-15 |
| **Links** | [repository](https://github.com/bytedance/ByteTransformer) · [benchmark](https://github.com/bytedance/ByteTransformer/blob/main/README.md) |

## Verdict

First-party README tables on an A100 (CUDA 11.6, PyTorch 1.13.0, fp16, 12-layer BERT-base, average length 0.6 of max): at batch 16 and max length 1024 ByteTransformer takes 24.70 ms vs 53.21 for PyTorch, 65.94 for TensorFlow, 45.22 for FasterTransformer with remove-padding and 59.96 for DeepSpeed (about 2.2x and 1.8x, derived from page data); at batch 1 it is 3.16 vs 4.2 ms (PyTorch) and 4.51 ms (FasterTransformer). Only the ByteTransformer column has a public script; the IPDPS 2023 paper (best paper award, per WebSearch snippets) reports 6.13x fused MHA over PyTorch and 55% over FasterTransformer end to end but was not opened.

## Use it when

- fp16 inference of BERT-base/large-style encoders (head size 64, GELU, post-LayerNorm) on an A100 with batches of 3 or more variable-length sequences, where padding waste is large.
- Batch 16 with max lengths of 448 to 1024 and average length around 60% of max: the README shows the biggest gap there (e.g. seq 512: 9.22 ms vs 13.79 for FasterTransformer with remove-padding, 21.0 for PyTorch).
- A C++/CUDA inference server that wants a small per-layer encoder API taking raw device pointers, a cuBLAS handle and a stream.
- Studying or vendoring a padding-free plus fused-MHA implementation under Apache-2.0.

## Skip it when

- Anything other than the BERT encoder: no decoder, GPT/LLM, T5 or training/backward pass (README: only the standard BERT encoder; issue #5 asking about training is unanswered).
- Hopper, Ada or other GPUs newer than sm86: the code turns fused attention off above seq 128 when arch &gt; 86 and uses the CUTLASS long-sequence path only on sm80; the README lists only V100, T4 and A100 and tests CUDA 11.6.
- Batch size 1 or 2: padding removal is switched off when max_batch_size &lt;= 2, and at batch 1 FasterTransformer is faster for seq 192-384 per the README.
- Batch 16 at seq 64 or 256-384, where the README shows FasterTransformer with remove-padding ahead (e.g. 5.49 vs 6.85 ms at 256).
- Sequences longer than 1024 tokens (the PyTorch op rejects them with 'Input seq_len too long').

## How it is fast

Padding-free execution: a single-block parallel prefix sum over the mask builds per-token offsets (batch_idx/word_idx), the input is packed to the valid tokens, and every GEMM and elementwise kernel runs on that packed row count; the last add-bias+LayerNorm kernel scatters results back to the padded layout. Attention is chosen by length: a single-kernel tensor-core (WMMA) fused MHA holding Q, K/V and the logits in shared memory for sequences up to 80, a split 'long' fused kernel up to about 384, and on A100 a CUTLASS-based attention for 384 &lt; seq &lt;= 1024 (the paper describes it as grouped-GEMM fused MHA). Other operators are fused too: GEMM with bias+GELU epilogue and add-bias+residual+LayerNorm in one pass.

## Compared with alternatives

Pick it over FasterTransformer for fp16 BERT-encoder serving on A100 with batches of 3+ variable-length inputs and max lengths of 448 and up, where its README beats FT's remove-padding mode by 1.5-2x; FasterTransformer also covers decoding and beam search for translation. LightSeq (also ByteDance) also accelerates training, and FlashAttention's varlen interface is the maintained choice if you only need padding-free attention rather than a whole encoder layer.

## Integration

| | |
|---|---|
| **Form** | shared lib (libbytetransformer.so, plus optional TorchScript op library libths_bytetransformer.so built with -DBUILD_THS=ON) |
| **Dependencies** | CUDA toolkit (README: 11.6), cuBLAS, cuBLASLt (Torch op), CUTLASS (git submodule 3rdparty/cutlass), PyTorch &gt;= 1.8 for the Python plugin |
| **Minimum toolchain** | C++17 with nvcc (CUDA 11.x; tested 11.6), CMake &gt;= 3.13 |
| **Platforms** | Linux, NVIDIA compute capability 7.0 (V100), 7.5 (T4), 8.0 (A100); data type fixed at build time (-DDataType=FP16 or FP32) |
| **Thread safety** | not documented; the PyTorch op builds a fresh encoder object per call and runs on the current CUDA stream and cuBLAS handle |
| **Drop-in for the baseline** | partial — the TorchScript op replaces one BERT encoder layer given raw weight tensors and a dense mask; it is not a drop-in for PyTorch/Hugging Face modules or for FasterTransformer's API |

## Gotchas

- BertTransformer::bert_infer creates two cudaEvents on every call and never destroys them (src/bert_transformer.cu), and the Torch op constructs a new encoder per layer per call, so long-running services leak; open issue #11 (Sep 2023, 'memory leak' on an RTX 3090) has no maintainer reply.
- The padding-free path copies the valid-token count from device to pageable host memory every layer (cudaMemcpyAsync in build_sequence_length_padding_offset_kernelLauncher), which blocks the host once per layer.
- Fused attention needs fp16 and head size 64; FP32 builds and other head sizes fall back to the unfused attention, which allocates a batch x heads x seq x seq score buffer.
- The benchmark harness (unit_test/python_scripts/bert_transformer_test.py) times wall clock with timeit and no final torch.cuda.synchronize(), and bert_bench.sh only times ByteTransformer, so the README's baseline columns cannot be reproduced from the repo.

## Known shortcomings

- bert_bench.sh times only ByteTransformer, so the baseline columns are not reproducible; FasterTransformer with padding removal wins at batch 16 seq 64 and at 256-384; IPDPS paper unopened (arXiv blocked).
- Resource bug: bert_infer (src/bert_transformer.cu) calls cudaEventCreate twice per call and never destroys them, and the Torch op builds a new encoder per layer per call, so serving leaks (matches open issue #11, no reply); padding-free path off for batch&lt;=2; fused/CUTLASS attention gated to sm70-86, so H100/Ada fall back to unfused attention; bench harness has no final torch.cuda.synchronize.

## Caveats and trade-offs

First-party README numbers. The public benchmark script benchmark/bert_bench.sh only times ByteTransformer (fp16, 12 layers); the baseline framework timings cannot be reproduced from the repository, and compiler flags and host CPU are not stated. The IEEE IPDPS 2023 paper (arXiv 2210.03052) was not opened. ByteTransformer is not always fastest: at batch 1, FasterTransformer is ahead at sequence 192-384 (1.26 vs 1.36, 1.35 vs 1.43, 1.63 vs 1.69, 1.64 vs 1.72 ms); at batch 16, FasterTransformer with remove-padding wins at sequence 64 (1.93 vs 2.09 ms) and 256-384 (5.49 vs 6.85, 6.47 vs 7.49, 7.05 vs 8.44 ms). Gains are largest at long sequences with batch 16 (padding-free path). Baselines are frameworks and FasterTransformer, not cuDNN, so it is not shown to beat cuDNN kernels directly. Only BERT encoder supported; last commit March 2024.

Only the standard BERT transformer encoder is supported; padding-free algorithm for variable-length inputs; C++ and Python/PyTorch plugin APIs; NVIDIA GPUs only (V100, T4, A100 compute capability).

## Maintenance

Stale: 11 commits, last on 2024-03-15, no releases, and the open memory-leak issue is unanswered; Apache-2.0 and small enough to vendor, but expect to patch it (event leak, sm90 dispatch) before production use on current CUDA and GPUs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now C.
- **Tier reason:** First-party README tables (A100, CUDA 11.6) with no host CPU or compiler flags; the public script benchmark/bert_bench.sh times only ByteTransformer (via unit_test/python_scripts/bert_transformer_test.py), so the PyTorch, TensorFlow, FasterTransformer and DeepSpeed columns have no public harness. The IPDPS 2023 paper (arXiv 2210.03052) could not be opened (arxiv.org blocked here), so no upgrade to B.
- **Verifier notes:** All claimed numbers match the README tables; added the batch-16 sequence 256-384 cases where FasterTransformer with remove-padding beats ByteTransformer, which the record missed. A WebSearch snippet says the paper was accepted at IPDPS 2023 and reports 6.13x fused-MHA vs PyTorch; the paper itself was not opened. Metadata checked: Apache-2.0, 481 stars, not archived, last commit 2024-03-15 (stale).
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/benchmark/bert_bench.sh>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/unit_test/python_scripts/bert_transformer_test.py>
  - <https://github.com/bytedance/ByteTransformer>
  - <https://github.com/bytedance/ByteTransformer/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/benchmark/bert_bench.sh>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/bytetransformer/include/bert_transformer.h>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/bytetransformer/src/bert_transformer.cu>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/bytetransformer/include/remove_padding.h>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/bytetransformer/include/attention.h>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/bytetransformer/include/cutlass_attention.h>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/bytetransformer/src/attention_fused.cu>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/bytetransformer/src/attention_fused_long.cu>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/bytetransformer/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/bytetransformer/th_op/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/bytetransformer/th_op/ths_op_f.cc>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/bytetransformer/th_op/bert_transformer_ext.h>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/bytetransformer/th_op/util.h>
  - <https://raw.githubusercontent.com/bytedance/ByteTransformer/HEAD/unit_test/python_scripts/bert_transformer_test.py>
  - <https://github.com/bytedance/ByteTransformer>
  - <https://github.com/bytedance/ByteTransformer/tree/main/bytetransformer>
  - <https://github.com/bytedance/ByteTransformer/tree/main/bytetransformer/include>
  - <https://github.com/bytedance/ByteTransformer/tree/main/bytetransformer/src>
  - <https://github.com/bytedance/ByteTransformer/tree/main/bytetransformer/th_op>
  - <https://github.com/bytedance/ByteTransformer/issues>
  - <https://github.com/bytedance/ByteTransformer/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/bytedance/ByteTransformer/issues/2>
  - <https://github.com/bytedance/ByteTransformer/issues/9>
  - <https://github.com/bytedance/ByteTransformer/issues/11>
  - WebSearch: ByteTransformer padding-free fused multi-head attention IPDPS 2023 (snippets only; arxiv.org/abs/2210.03052 egress-blocked)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/bytedance/bytetransformer`) · [data/wave8/enrich/raw/github_com_bytedance_bytetransformer.json](../../../data/wave8/enrich/raw/github_com_bytedance_bytetransformer.json) (enrichment confidence 0.75)

</details>
