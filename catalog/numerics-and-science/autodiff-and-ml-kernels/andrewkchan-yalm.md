# yalm (Yet Another Language Model, C++/CUDA LLM inference)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++ (CUDA)` · `no license` · 🟡 stale

> Educational single-GPU C++/CUDA LLM inference engine; about 2.4x Hugging Face transformers FP16 decode, roughly tied with llama.cpp.

| | |
|---|---|
| **Beats** | Hugging Face transformers (PyTorch) GPU inference; llama.cpp GPU also measured |
| **Claimed result** | yalm 63.8 and 58.7 tok/s vs huggingface transformers 25.9 and 25.7 tok/s (about 2.5x and 2.3x, derived from page data). vs llama.cpp 61.0 and 58.8 tok/s: about +4.6% at \~120 tokens and a tie at \~4800 tokens (derived from page data). calm (66.0 and 65.7 tok/s) is faster than yalm. |
| **Workload** | Mistral-7B-Instruct-v0.2 in FP16 with 4k context, decode tokens per second averaged over \~120-token and \~4800-token generations on an RTX 4090. |
| **Metric** | throughput |
| **Hardware** | RTX 4090 + EPYC 7702P |
| **Compiler and flags** | Makefile: host C++ -O3 -ffast-math -std=c++20 -fopenmp -mf16c -mavx2 -mfma; nvcc -O2 -lineinfo with default -gencode sm_80 and sm_90 (or -arch=\$(CUARCH)). The compiler and CUDA versions and the CUARCH used for the RTX 4090 run are not stated. |
| **Adoption** | 602 stars |
| **Last commit** | 2025-08-26 |
| **Links** | [repository](https://github.com/andrewkchan/yalm) · [benchmark](https://raw.githubusercontent.com/andrewkchan/yalm/HEAD/README.md) |

## Verdict

Author-run table (README, Mistral-7B-Instruct-v0.2 FP16, 4k context, RTX 4090 + EPYC 7702P): yalm 63.8 and 58.7 tok/s at \~120 and \~4800 generated tokens vs Hugging Face transformers 25.9 and 25.7 (about 2.5x and 2.3x, derived from page data), llama.cpp 61.0 and 58.8, calm 66.0 and 65.7. Transformers, llama.cpp, CUDA and compiler versions are not given and no script reproduces the cross-engine table; the build uses -O3 -ffast-math -mavx2 -mfma -mf16c and nvcc -O2.

## Use it when

- Learning or teaching how a fast single-GPU decoder is built: small codebase (src/infer.cu is about 1,250 lines) with heavily commented kernels and an accompanying blog post.
- Batch-1, single-sequence FP16 decode of Mistral-7B or Llama-3.2 on an NVIDIA GPU with enough VRAM for the whole model, where you want about 2.4x the token rate of Hugging Face transformers eager inference.
- Profiling experiments with Nsight Compute: `./build/test -k [matmul,mha,ffn]` benchmarks individual kernels and `-b`/`-b2` measure memory bandwidth.
- Long-context experiments with a sliding-window KV cache (`-T`) plus two attention-sink tokens, or the built-in perplexity and passkey modes.

## Skip it when

- Production serving: the README says it is an educational exercise 'not meant to be run in production', and there is no license file, so the code cannot be reused.
- Anything needing more speed than llama.cpp: the README's own table has llama.cpp at 61.0/58.8 tok/s vs yalm 63.8/58.7 (a tie at \~4800 tokens) and calm ahead of both at 66.0/65.7.
- Batched or multi-user serving, quantized weights (only fp32/fp16 load; fp8 in convert.py is rejected by the loader), multi-GPU or models larger than VRAM.
- Long prompts: the prompt is hydrated one token at a time through the decode path (no batched prefill), so time-to-first-token grows linearly with prompt length.
- Mixtral/MoE on GPU: the CUDA path asserts 'Mixture of experts not yet supported for CUDA'; Mixtral works on CPU only.

## How it is fast

Decode at batch 1 is memory-bandwidth bound, so the CUDA path is a set of hand-written GEMV-style kernels: one warp per output row with a warp-shuffle reduction (`matmul_row`), a block transpose so 32 row results go out in one coalesced 128-byte store, and fused kernels for QKV projection + clipping, RoPE + KV-cache write, SwiGLU w1/w3 + activation, and output projection + residual add. The whole per-token forward pass is captured once into a CUDA graph and replayed, updating only the kernel-node parameters that change with position, which removes per-kernel launch overhead. The KV cache is FP16 and the attention value-mix kernel unrolls 16-deep register prefetches over the sequence; the design follows zeux/calm, which the README credits.

## Compared with alternatives

Pick yalm over llm.c or ik_llama.cpp only to study a compact, documented single-GPU FP16 decode engine; for actual inference ik_llama.cpp/llama.cpp, CTranslate2 or PowerInfer are licensed, maintained and support quantization, batching and more models.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA toolkit (nvcc, cudart; linked even for CPU runs), OpenMP; vendored fmt and nlohmann json; Python with safetensors, torch and numpy for weight conversion |
| **Minimum toolchain** | C++20 compiler with OpenMP, CUDA toolkit with nvcc (version not documented) |
| **Platforms** | Linux x86-64 host with AVX2, FMA and F16C (hard-coded in the Makefile) plus one NVIDIA GPU; default build emits SASS for sm_80 and sm_90 only, other GPUs need CUARCH set |
| **Thread safety** | not documented; the CLI runs one sequence on one CUDA stream and keeps device properties in file-level globals |
| **Drop-in for the baseline** | no |

## Gotchas

- The README benchmark table dates from Dec 2024 - Jan 2025 README commits and was not re-measured after commit 6cd1ef6 (2025-08-26) fixed att_mix loop bounds (its 16-deep prefetch read past the attended sequence) and CUDA-graph node updates.
- The program's own 'throughput' line divides prompt plus generated tokens by total time including prompt hydration, so it is not the same metric as llama.cpp's separate prompt-eval and eval rates.
- Error handling is `assert(false)`/`abort()`: an unsupported dtype or model aborts, and a build with NDEBUG would let some of those paths continue silently.
- CFLAGS include -Werror, so newer compilers that add warnings can break the build; issue #1 (CPU-only build) is unanswered.

## Known shortcomings

- Only clearly beats HF transformers (2.5x); ties llama.cpp at \~4800 tokens and calm is faster. No script for the cross-engine table. No licence.
- README benchmark table predates commit 6cd1ef6 (2025-08-26), which fixed out-of-bounds prefetch reads in att_mix and CUDA graph node updates, so the numbers come from pre-fix code (tier C rule). yalm's tok/s counts prompt plus generated tokens over total time with the prompt run one token at a time, not llama.cpp's metric. fp8 offered by convert.py but rejected by the loader; MoE asserts on CUDA; default build targets sm_80/sm_90 only.

## Caveats and trade-offs

Only the margin over Hugging Face transformers is large (about 2.5x and 2.3x); against llama.cpp it is +4.6% at \~120 tokens and 58.7 vs 58.8 tok/s (a tie, marginally slower) at \~4800 tokens, and the README shows calm ahead of yalm at both lengths. Versions and settings of transformers and llama.cpp are not stated, the repo has no script that reproduces the cross-engine table (./build/test only benchmarks yalm's own kernels and memory bandwidth), and the CUDA and compiler versions are not given. The author calls it an educational exercise not meant for production; single GPU only, model must fit in VRAM, a few models tested. No LICENSE file in the repo root, so the code is reference only. The author's blog post 'Fast LLM Inference From Scratch' (andrewkchan.dev, also an HN thread) was not opened because personal blogs are egress-blocked; a WebSearch snippet only repeated the README table.

Educational, not for production per its README: single GPU, completions only (no chat interface), a few model families (Mistral-7B, Mixtral, Llama-3.2), requires converting safetensors weights to its own .yalm format.

## Maintenance

Stale (last commit 2025-08-26, 117 commits, three open unanswered issues) and unlicensed, so read it as reference material rather than vendoring it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table (Mistral-7B-Instruct-v0.2 FP16, 4k context, RTX 4090 + EPYC 7702P) gives first-party tok/s for huggingface transformers 25.9/25.7, llama.cpp 61.0/58.8, calm 66.0/65.7 and yalm 63.8/58.7, matching the record. No harness script for the cross-engine table, no baseline versions and no toolchain versions are given, so C.
- **Verifier notes:** Numbers verified verbatim on the README; metadata confirmed on github.com (no license shown, 602 stars, 64 forks, not a fork or archived, last commit 2025-08-26, so stale against 2026-09-26). No shortcoming beyond the thin margin over llama.cpp and the missing license.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/andrewkchan/yalm/HEAD/README.md>
  - <https://github.com/andrewkchan/yalm>
  - <https://github.com/andrewkchan/yalm/commits>
  - <https://raw.githubusercontent.com/andrewkchan/yalm/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/andrewkchan/yalm>
  - <https://raw.githubusercontent.com/andrewkchan/yalm/HEAD/README.md>
  - <https://raw.githubusercontent.com/andrewkchan/yalm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/andrewkchan/yalm/HEAD/src/infer.cu>
  - <https://raw.githubusercontent.com/andrewkchan/yalm/HEAD/src/model.h>
  - <https://raw.githubusercontent.com/andrewkchan/yalm/HEAD/src/model.cpp>
  - <https://raw.githubusercontent.com/andrewkchan/yalm/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/andrewkchan/yalm/HEAD/src/codec.h>
  - <https://raw.githubusercontent.com/andrewkchan/yalm/HEAD/convert.py>
  - <https://raw.githubusercontent.com/andrewkchan/yalm/HEAD/requirements.txt>
  - <https://github.com/andrewkchan/yalm/tree/main/src>
  - <https://github.com/andrewkchan/yalm/tree/main/vendor>
  - <https://github.com/andrewkchan/yalm/issues>
  - <https://github.com/andrewkchan/yalm/issues/1>
  - <https://github.com/andrewkchan/yalm/commits>
  - <https://github.com/andrewkchan/yalm/commits/main/README.md>
  - <https://github.com/andrewkchan/yalm/commit/6cd1ef6e7d6b9f724b6d98a63b273f903928ad2f>
  - <https://github.com/andrewkchan/yalm/commit/ec0a3bc>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/andrewkchan/yalm`) · [data/wave8/enrich/raw/github_com_andrewkchan_yalm.json](../../../data/wave8/enrich/raw/github_com_andrewkchan_yalm.json) (enrichment confidence 0.75)

</details>
