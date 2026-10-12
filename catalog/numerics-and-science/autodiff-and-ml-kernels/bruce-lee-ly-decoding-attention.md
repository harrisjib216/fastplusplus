# Decoding Attention (Bruce-Lee-LY)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `CUDA/C++` · `BSD-3-Clause` · 🟡 stale

> CUDA-core decode-attention kernel for LLM inference; beats Flash-Decoding and FlashInfer only at short KV lengths.

| | |
|---|---|
| **Beats** | Flash-Decoding (FlashAttention v2.6.3) and FlashInfer v0.1.6 decode attention |
| **Claimed result** | README text: faster than Flash-Decoding and FlashInfer below sequence length 1536 (batch 1), slower above it, and faster than both at every batch size with sequence length 128. Approximate plot readings (derived from page data), RTX 3090 FP16 MHA, 32 heads, head dim 128: batch sweep at seq 128, about 0.69 TFLOPS vs FlashInfer 0.50 and Flash-Decoding 0.42 at batch 16 (about 1.4x and 1.6x); at batch 128 and above about 0.86 vs 0.85 and 0.55 (about 1.0x and 1.55x). Sequence sweep at batch 1: about 1.75x both baselines at seq 1024 (0.34 vs 0.19 TFLOPS), but at seq 8192 FlashInfer reaches about 0.84 TFLOPS against 0.43, so the project is about 2x slower there. MLA on H20 (README plots, no other baseline): FlashMLA is faster everywhere, about 12x at batch 1 to about 70x at batch 128 and above in the batch sweep (seq 4096; FlashMLA 41 to 127 TFLOPS vs about 1.7 to 3.4), and 1.3x at seq 256 to about 18x at seq 8192 in the batch-1 sequence sweep. |
| **Workload** | Decode-stage multi-head attention (32 heads, head dim 128, FP16) on an RTX 3090, sweeping sequence length and batch size; MLA on an H20 is also plotted. |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 3090 (CUDA 12.1); H20 (CUDA 12.4) for MLA |
| **Adoption** | 48 stars |
| **Last commit** | 2025-06-11 |
| **Links** | [repository](https://github.com/Bruce-Lee-LY/decoding_attention) · [benchmark](https://github.com/Bruce-Lee-LY/decoding_attention) |

## Verdict

First-party plots from the public Python harness (1 warmup, 10 timed iterations, CUDA events) on an RTX 3090 with CUDA 12.1, FP16, 32 heads, head dim 128, compare against flash_attn_with_kvcache from FlashAttention v2.6.3 and FlashInfer v0.1.6 (the author's fork): faster at KV lengths below 1536 and across a batch sweep at KV length 128, about 2x slower than FlashInfer at 8192. In the batch sweep FlashInfer runs through its paged-KV wrapper with page size 1 while this kernel reads contiguous KV, so the baselines are not on equal footing; host CPU and host compiler are not stated.

## Use it when

- Decode-stage MHA with short contexts (README: faster than Flash-Decoding and FlashInfer below KV length 1536 at batch 1, about 1.75x at 1024 on an RTX 3090 by plot reading).
- Large batches of short sequences: in the KV length 128 batch sweep it led both baselines at every batch size (about 1.4-1.6x at batch 16, roughly level with FlashInfer from batch 128).
- Ampere/Ada consumer or workstation GPUs (sm80, sm86, sm89 build targets) where you control the KV layout and want a small, readable kernel to fork.
- ALiBi models or GQA/MQA decode where a contiguous varlen KV buffer is already available.

## Skip it when

- KV lengths above about 1536: FlashInfer reached about 0.84 vs 0.43 TFLOPS at 8192 on the same plots, roughly 2x faster.
- MLA decoding: on an H20 the README's own plots show FlashMLA 1.3x to about 70x faster; each block re-reads its KV head, so MQA/MLA traffic grows with the number of query heads.
- Paged KV caches, prefill, speculative decoding with more than one query token, or FP8/INT8 KV caches (KV quantization is listed as TODO).
- Long contexts in general: the kernel needs max_seq_k x 4 bytes of shared memory per block, which caps KV length at about 25k tokens on sm86/sm89 and about 58k on sm90 (derived from the source and CUDA per-block shared-memory limits); tests only cover KV lengths up to 512.
- Production use needing maintenance: two commits, no releases or issues, last commit 2025-06-11.

## How it is fast

Avoids tensor cores, which Flash-Decoding underuses when the query length is 1, and instead runs a plain CUDA-core kernel adapted from OpenPPL: one thread block per (sequence, query head), 128-bit vectorised K/V loads, warp-shuffle reductions for the Q.K dot products, all scores kept in shared memory, then a block-wide softmax and a P.V pass. Launch shape is picked per head dim and batch (e.g. 256 threads for batch &lt;= 4, 128 otherwise at head dim 128), and kernels are built with --use_fast_math. With no split over the sequence and a three-pass softmax, it is cheapest when the KV length is short and the batch fills the GPU.

## Compared with alternatives

Pick it over FlashInfer only for short-context, large-batch MHA/GQA decode on Ampere/Ada with a contiguous KV buffer; for long contexts, paged KV caches or MLA, FlashInfer (or FlashMLA) wins, and FlashAttention-3 targets Hopper prefill and training rather than this niche.

## Integration

| | |
|---|---|
| **Form** | source-drop (CUDA sources plus a PyTorch CUDAExtension; the CMake build produces only a benchmark executable) |
| **Dependencies** | CUDA &gt;= 11.4; PyTorch, ninja and psutil for the Python extension; gflags and OpenMP for the C++ benchmark; pytest for tests |
| **Minimum toolchain** | C++17 (nvcc -std=c++17), CMake 3.16+; README says GCC &gt;= 5, but the kernel uses if constexpr and std::is_same_v, so a C++17-capable host compiler is required |
| **Platforms** | Linux; NVIDIA sm80 (A100), sm86 (RTX 3090/A6000), sm89 (L20/L40S), sm90 (H20/H800) |
| **Thread safety** | Stateless launch on the caller's CUDA stream (the PyTorch wrapper uses the current stream); no other guarantees documented |
| **Drop-in for the baseline** | partial — replaces flash_attn_with_kvcache or FlashInfer decode only for one query token per sequence with a contiguous varlen KV buffer; no paged KV, softmax-scale argument or LSE output |

## Gotchas

- Softmax scale is hard-coded to 1/sqrt(dim); models needing another scale (e.g. absorbed MLA with dim 576) must pre-scale Q themselves.
- Sequences with zero KV length return early without writing their output rows, and the PyTorch wrapper allocates the output with torch::empty, so those rows hold uninitialised memory.
- Strides are recomputed from head counts and dims; the wrapper checks only that the last dimension is contiguous, so a strided view (e.g. K sliced from a combined KV tensor) is read incorrectly. For MLA pass v=None, since the V row stride is computed from dim, not dim_v.
- The P.V partial sums are combined with shared-memory float atomicAdd across warps, so outputs are not bitwise reproducible run to run; setup.py also forces _GLIBCXX_USE_CXX11_ABI=0 regardless of how the installed PyTorch was built.

## Known shortcomings

- FlashMLA is 1.3x to \~70x faster than Decoding Attention on H20 MLA plots; the FlashInfer baseline is the author's own fork.
- FlashInfer batch baseline uses paged KV with page_size=1 (not equal footing); context capped near 25k tokens on sm86/89 by the shared-memory score buffer; output rows for zero-length KV left uninitialized (torch::empty); softmax scale hard-coded to 1/sqrt(dim); tests only to seq 512.

## Caveats and trade-offs

Single-developer repository with two commits; results are plots only (the RTX 3090 plots label the TFLOPS axis only at 0 and 1). The win is limited to short contexts: FlashInfer and Flash-Decoding win above sequence length 1536, and on the H20 MLA plots FlashMLA is 1.3x to about 70x faster than this project. The FlashInfer baseline is the author's fork (Bruce-Lee-LY/flashinfer, v0.1.6), and the harness times only 1 warmup and 10 iterations. Host CPU and host compiler are not stated. Baselines are FlashAttention-family kernels, not cuDNN.

Uses CUDA cores, not tensor cores; decode stage only; MHA, MQA, GQA and MLA with FP16/BF16; C++ and Python APIs.

## Maintenance

Stale single-author research code (2 commits, last 2025-06-11, 48 stars, no issues filed), BSD-3-Clause and small (one kernel template), so it is easy to vendor and adapt but has no releases or maintenance.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README plots (performance/RTX3090/\*.png, y-axis in TFLOPS) from the public harness benchmarks/python/benchmark_decoding_attn.py, which times flash_attn_with_kvcache (FlashAttention v2.6.3) and FlashInfer v0.1.6 alongside the project's kernel with CUDA events. GPU and CUDA 12.1 are stated, and nvcc flags are in CMakeLists.txt (-O3 --use_fast_math), but the host CPU and host compiler are not, so it is C, not A.
- **Verifier notes:** Metadata confirmed on the GitHub page: BSD-3-Clause, 48 stars, 4 forks, 2 commits (latest 2025-06-11, 'support mla'), not archived or a fork; stale. Shortcoming to record: the MLA comparison the README plots shows the project far slower than FlashMLA, and the FlashInfer baseline is the author's own fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Bruce-Lee-LY/decoding_attention>
  - <https://github.com/Bruce-Lee-LY/decoding_attention/commits>
  - <https://github.com/Bruce-Lee-LY/decoding_attention/tree/master/benchmarks/python>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/README.md>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/performance/RTX3090/seq_throughput.png>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/performance/RTX3090/batch_throughput.png>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/performance/H20/seq_throughput.png>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/performance/H20/batch_throughput.png>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/build_cpp.sh>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/run_cpp.sh>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/run_python.sh>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/benchmarks/python/benchmark_decoding_attn.py>
- **Sources the enricher read:**
  - <https://github.com/Bruce-Lee-LY/decoding_attention>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/README.md>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/setup.py>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/install_python.sh>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/build_cpp.sh>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/run_python.sh>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/LICENSE>
  - <https://github.com/Bruce-Lee-LY/decoding_attention/tree/master/csrc>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/csrc/torch/decoding_torch.cpp>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/csrc/ops/decoding_attn.cpp>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/csrc/ops/decoding_attn.h>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/csrc/kernel/decoding_attn/decoding_fwd_hd128_hdv128.cu>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/csrc/kernel/decoding_attn/decoding_fwd_launch_template.h>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/csrc/kernel/decoding_attn/decoding_fwd_kernel.h>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/csrc/kernel/decoding_attn/decoding.h>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/csrc/kernel/decoding_attn/block_info.h>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/decoding_attn/__init__.py>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/benchmarks/python/benchmark_decoding_attn.py>
  - <https://raw.githubusercontent.com/Bruce-Lee-LY/decoding_attention/HEAD/tests/test_decoding_attn.py>
  - <https://github.com/Bruce-Lee-LY/decoding_attention/issues?q=is%3Aissue>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/bruce-lee-ly/decoding_attention`) · [data/wave8/enrich/raw/github_com_bruce_lee_ly_decoding_attention.json](../../../data/wave8/enrich/raw/github_com_bruce_lee_ly_decoding_attention.json) (enrichment confidence 0.8)

</details>
