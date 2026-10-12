# FlashInfer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `CUDA/C++ with Python` · `Apache-2.0` · 🟢 active

> CUDA kernel library for LLM serving (paged/ragged attention, MLA, GEMM, MoE, sampling); beat vLLM 0.2.6 PageAttention and FlashAttention 2.4.2 kernels.

| | |
|---|---|
| **Beats** | vLLM 0.2.6 PageAttention kernels and FlashAttention 2.4.2 (kernel-level, 2024 launch blog); Triton-based compiler attention backends in LLM serving (MLSys 2025 paper) |
| **Claimed result** | Launch blog 'Accelerating Self-Attentions for LLM Serving with FlashInfer' (2024-02-02, FlashInfer 0.0.1): cascade inference gives 'up to 31x speedup compared to the baseline vLLM PageAttention implementation' for shared-prefix batch decoding (32768-token shared prompt, batch size &gt;=128, unique KV length &lt;=256, H100 SXM 80GB) and 26x over FlashInfer's own non-cascaded batch decode; 'up to 2-3x speedup for Grouped-Query Attention on A100 & H100, compared to vLLM implementation'; batch GQA decode with Tensor Cores '3x faster than vLLM PagaAttention when batch_size=64'; prefill and decode kernels described as best on all 4 GPUs against FlashAttention 2.4.2 (plots only). MLSys 2025 paper abstract (seen via a search result; paper blocked here): 29-69% inter-token-latency reduction compared to compiler backends on an LLM serving benchmark, 28-30% latency reduction for long-context inference, 13-17% speedup for LLM serving with parallel generation. |
| **Workload** | LLM serving attention (paged/ragged KV cache, prefill, decode, MLA), GEMM, fused MoE, sampling and normalization kernels on Turing through Blackwell GPUs. |
| **Metric** | throughput |
| **Hardware** | H100 SXM 80GB, A100 PCIe 80GB, RTX 6000 Ada, RTX 4090 (2024 launch blog) |
| **Compiler and flags** | NVCC from CUDA 12.3.1 for FlashInfer and FlashAttention (built from source); vLLM 0.2.6 from prebuilt pip wheels; build flags not stated; kernels timed with NVIDIA nvbench, cold L2 |
| **Adoption** | 6.5k stars, 1.5k forks; used by vLLM, SGLang, TensorRT-LLM, MLC-LLM; PyPI flashinfer-python 0.7.0.post1 uploaded 2026-09-29 |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/flashinfer-ai/flashinfer) · [benchmark](https://github.com/flashinfer-ai/flashinfer-ai.github.io/blob/main/_posts/2024-01-03-introduce-flashinfer.md) |

## Verdict

The project's 2024 posts timed FlashInfer 0.0.1 kernels (built with NVCC from CUDA 12.3.1, nvbench cold-L2) against FlashAttention 2.4.2 and vLLM 0.2.6 PageAttention on H100 SXM, A100 PCIe, RTX 6000 Ada and RTX 4090 with Llama-2-7B/70B head shapes: prefill and decode were best on all four GPUs (plots only), batch GQA decode was 3x vLLM at batch 64, and cascade attention reached up to 31x vLLM on H100 for a 32k shared prefix. The MLSys 2025 paper (abstract seen via search; PDF blocked here) reports 29-69% lower inter-token latency than compiler (Triton) backends in end-to-end serving. These numbers are first-party and were not re-measured for current versions.

## Use it when

- Building or tuning an LLM serving engine that needs batched decode and prefill over a paged KV cache, with CUDA graphs and torch.compile
- Many requests share a long prompt (document QA, self-consistency or tree search sampling): cascade attention was up to 31x vLLM 0.2.6 PageAttention at a 32k shared prefix, batch &gt;= 128 and short unique suffixes on H100
- GQA models (Llama-2-70B-style 8:1 head ratio and up) in batched decode, where the tensor-core decode path gives the 2-3x over vLLM's kernel
- DeepSeek-style MLA, FP8/FP4 attention, GEMM or MoE on Hopper or Blackwell, where it exposes the TensorRT-LLM and CUTLASS kernels behind one API
- Custom attention variants (logit soft-cap, sliding window, sinks, custom logits/query transforms) without writing a new kernel

## Skip it when

- Training or plain dense attention with fixed shapes: FlashAttention-2/3 or cuDNN SDPA are simpler, and FlashInfer itself dispatches to them in many configurations
- Non-NVIDIA GPUs (AMD, Intel, Apple) or pre-Turing NVIDIA (below SM 7.5); many features exist only on Hopper or Blackwell
- Environments that cannot JIT-compile or download kernels at first use (no nvcc, no network) unless you also install the flashinfer-cubin and flashinfer-jit-cache wheels
- Teams that need a stable API and behaviour: pre-1.0 releases ship every few days (0.6.18, then 0.7.0 on 2026-09-22, 0.7.1rc1 on 2026-09-30) with about 426 open issues, and per-backend bugs keep showing up (see gotchas)

## How it is fast

It treats paged and ragged KV caches as block-sparse matrices (down to page_size=1 'vector sparsity'), so one FlashAttention-2/3-style tiled online-softmax kernel serves every cache layout. Page indices are prefetched into shared memory, so page size does not slow the kernel. Decode uses split-KV (Flash-Decoding style) with a plan-time load-balanced scheduler, and GQA decode reuses the tensor-core prefill kernel, which the 2024 post measured at 3x vLLM at batch 64. Cascade inference computes shared-prefix attention once with a multi-query kernel and merges it with per-request suffix attention via the log-sum-exp 'attention state' merge operator. Kernels are specialized at JIT time from Jinja/CUDA templates, and calls can be dispatched to FlashAttention-3, cuDNN, CUTLASS, TensorRT-LLM or CuTe-DSL backends.

## Compared with alternatives

Pick FlashInfer when you need serving-specific attention (paged or ragged KV, mixed prefill and decode, shared prefixes, MLA) behind one API; use FlashAttention-3 for training or dense Hopper attention, SageAttention for quantized approximate attention, and Bruce-Lee-LY's Decoding Attention only for short-sequence batch-1 decode, where its README beats FlashInfer 0.1.6.

## Integration

| | |
|---|---|
| **Form** | module (pip flashinfer-python, with JIT-compiled or downloaded cubins and optional precompiled flashinfer-cubin / flashinfer-jit-cache wheels); header-only CUDA C++ templates in include/flashinfer for direct C++ use |
| **Dependencies** | PyTorch, CUDA toolkit (nvcc and ninja for JIT), apache-tvm-ffi, cuda-python, nvidia-cudnn-frontend, nvidia-cutlass-dsl, nccl4py/nccl-extensions, numpy, einops; submodules CUTLASS, CCCL, spdlog and nixl |
| **Minimum toolchain** | Python 3.10+; CUDA 12.9 or 13.0 per the README's supported list (13.4 preview); setuptools 77+ for source builds |
| **Platforms** | NVIDIA GPUs SM 7.5 (Turing) through SM 12.x (Blackwell RTX 50, DGX Spark, Jetson Thor); Linux x86-64 and aarch64 wheels; feature coverage varies by compute capability |
| **Thread safety** | Not documented for the wrappers, which hold per-batch plan state and workspace buffers; the experimental prepared SM110 decode API says concurrent launches need independent prepared objects and workspace and may reuse one only on ordered streams |
| **Drop-in for the baseline** | partial — engines such as vLLM and SGLang can select it as their attention backend by configuration, but direct use needs the plan()/run() wrapper API and FlashInfer's page-table (indptr/indices/last_page_len) format |

## Gotchas

- Wrappers need a zero-initialized, 16-byte-aligned workspace buffer (128 MB recommended); with use_cuda_graph=True the batch size is fixed for the wrapper's lifetime and index buffers must be preallocated
- backend='auto' picks fa2, fa3, cudnn, trtllm-gen or cute-dsl by GPU and shape, and features differ per backend (for example the cudnn decode backend lacks RoPE, soft-cap and FP8 KV), so speed and supported options change across GPUs and versions
- Correctness bugs have hit specific backends: ragged prefill on SM90 hit illegal memory accesses at total sequence length &gt;= 16384 (issue #1419, fixed via PR #2801), and trtllm_batch_decode_with_kv_cache_mla wrote NaNs into CUDA-graph padded rows in 0.6.4/0.6.6 (issue #2883, closed as not planned)
- Performance moves between releases: the project's own v0.2 post says v0.1.6 prefill was slower than v0.1.1; allow_fp16_qk_reduction buys about 50% on RTX 4090 at reduced accumulation precision

## Known shortcomings

- 31x vs vLLM 0.2.6 PageAttention is a best case from the 2024 launch blog (2-3x for GQA, CUDA 12.3.1); MLSys 2025 venue from search results (paper unreadable here); numbers are 2024-vintage and FlashInfer now also dispatches to third-party backends.
- Correctness bugs: #1419 SM90 ragged prefill illegal memory access at total seqlen &gt;= 16384 (fixed PR #2801); #2883 MLA decode NaNs in CUDA-graph padding (0.6.4/0.6.6, closed not planned); v0.2 post admits v0.1.6 prefill was slower than v0.1.1; all numbers first-party from 2024.

## Caveats and trade-offs

The quoted kernel numbers are first-party and from 2024 (FlashInfer 0.0.1 against FlashAttention 2.4.2 and vLLM 0.2.6); nobody has re-published them for current versions. The 31x figure is a best-case corner (very long shared prefix, large batch) against a vLLM kernel that did not optimize shared prefixes. Today FlashInfer also dispatches to FlashAttention-2/3, cuDNN, CUTLASS and TensorRT-LLM backends, so part of its current speed comes from third-party kernels, and its benchmarks/flashinfer_benchmark.py only prints per-backend timings (in the README's sample B200 ragged-prefill run the cuDNN backend beat fa2 and cutlass). The MLSys 2025 paper and the flashinfer.ai blog were blocked here; the paper's numbers come from a search-result abstract. Build flags for the published runs are not stated.

Library plus kernel generator with JIT compilation; Python/PyTorch API with CUDA C++ kernels; FP8/FP4 low-precision support; NVIDIA GPUs only.

## Maintenance

Very active (commits daily, 0.7.0.post1 on PyPI 2026-09-29, 6.5k stars), Apache-2.0, and the default attention backend in several major serving engines, so it is safe to adopt, though the published speedups date from 2024 and the API is still pre-1.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now B.
- **Tier reason:** Upgraded from D. The project's launch blog post (source in flashinfer-ai/flashinfer-ai.github.io) gives kernel-level numbers against vLLM 0.2.6 PageAttention and FlashAttention 2.4.2 (NVCC from CUDA 12.3.1, nvbench cold-L2 timing, H100/A100/RTX 6000 Ada/RTX 4090). The peer-reviewed MLSys 2025 paper (proceedings.mlsys.org listing seen in search results; the PDF was blocked here) reports serving-latency wins over compiler (Triton) backends. Build flags and an exact benchmark code path for the published figures are not stated, so not A.
- **Verifier notes:** The record had no benchmark URL; I found the numbers in the blog's GitHub Pages source (flashinfer.ai and \*.github.io are blocked) and confirmed the MLSys 2025 venue from search results, so I upgraded D to B as with earlier wave-8 B entries whose papers were blocked. A later retier check could open the paper (arXiv:2501.01005) to confirm its kernel-level comparisons. Last commit 2026-10-01 (commits Atom feed).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer/HEAD/README.md>
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer/HEAD/benchmarks/README.md>
  - <https://github.com/flashinfer-ai/flashinfer>
  - <https://github.com/flashinfer-ai/flashinfer/commits/main.atom>
  - <https://github.com/flashinfer-ai/flashinfer-ai.github.io/tree/main/_posts>
  - <https://github.com/flashinfer-ai/flashinfer-ai.github.io/blob/main/_posts/2024-01-03-introduce-flashinfer.md>
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer-ai.github.io/HEAD/_posts/2024-01-03-introduce-flashinfer.md>
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer-ai.github.io/HEAD/_posts/2024-01-08-cascade-inference.md>
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer-ai.github.io/HEAD/_posts/2024-12-12-flashinfer-v02-release.md>
  - <https://pypi.org/pypi/flashinfer-python/json>
- **Sources the enricher read:**
  - <https://github.com/flashinfer-ai/flashinfer>
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer/HEAD/README.md>
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer/HEAD/flashinfer/decode.py>
  - <https://github.com/flashinfer-ai/flashinfer/tree/main/include/flashinfer>
  - <https://github.com/flashinfer-ai/flashinfer/tree/main/3rdparty>
  - <https://github.com/flashinfer-ai/flashinfer/issues/2883>
  - <https://github.com/flashinfer-ai/flashinfer/issues/1419>
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer-ai.github.io/HEAD/_posts/2024-01-03-introduce-flashinfer.md>
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer-ai.github.io/HEAD/_posts/2024-01-08-cascade-inference.md>
  - <https://raw.githubusercontent.com/flashinfer-ai/flashinfer-ai.github.io/HEAD/_posts/2024-12-12-flashinfer-v02-release.md>
  - <https://pypi.org/pypi/flashinfer-python/json>
  - https://proceedings.mlsys.org/paper_files/paper/2025/file/dbf02b21d77409a2db30e56866a8ab3a-Paper-Conference.pdf (EGRESS_BLOCKED; abstract seen via search results)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/flashinfer-ai/flashinfer`) · [data/wave8/enrich/raw/github_com_flashinfer_ai_flashinfer.json](../../../data/wave8/enrich/raw/github_com_flashinfer_ai_flashinfer.json) (enrichment confidence 0.75)

</details>
