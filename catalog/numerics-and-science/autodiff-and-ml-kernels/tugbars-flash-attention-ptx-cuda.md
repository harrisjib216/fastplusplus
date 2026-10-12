# Flash Attention PTX/CUDA (hand-written PTX prefill attention for RTX 5080)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (CUDA/PTX)` · `MIT (stated only in the README's License section; no LICENSE file in the repository, raw LICENSE returns 404)` · 🟢 active

> Hand-written PTX flash-attention prefill and paged decode library for RTX 5080 (sm_120); edges out vLLM's FlashAttention-2 at small batch.

| | |
|---|---|
| **Beats** | FlashAttention-2 as bundled in vLLM 0.23.0 (vllm.vllm_flash_attn.flash_attn_varlen_func, FA2 path) |
| **Claimed result** | docs/vllm-comparison.md (latency-based, vs vLLM 0.23.0 FA2, causal fp16, RTX 5080): 'beats or matches' at 23 of 34 shapes, but it is strictly faster at 17 of 34 (derived from page data). The 23 also counts losses of -0.2% to -1.9% as matches. D=64 H=12 B=1: +18.5% (S=512), +31.9% (1024), +8.9% (2048), +2.1% (4096). D=128 H=12 B=1: +16.6% (512), +12.6% (1024), +3.8% (2048). Losses up to -4.8% (B=8 S=4096 D=64) and -4.5% (B=8 S=8192 D=128); D=128 H=32 wins only at B=1 S=2048 (+0.7%). Peak \~202 TFLOPS vs vLLM \~212. README end-to-end Qwen2.5-1.5B vs vLLM 0.23 (FLASH_ATTN backend, CUDA graphs on): decode B=1 4.70 vs 5.12 ms/token, decode B=8 5.28 vs 5.43 ms/step, prefill 128 tokens B=1 7.1-11 ms vs 10.4 ms, B=8 31.2 vs 32.1 ms. |
| **Workload** | Causal fp16 attention prefill over 34 shapes (B=1..8, H=12 or 32, S=512..8192, D=64 or 128) on an RTX 5080, same-process interleaved timing with shared random inputs; plus end-to-end Qwen2.5-1.5B decode and prefill against vLLM. |
| **Metric** | latency |
| **Hardware** | NVIDIA RTX 5080 (84 SMs, sm_120, 234.8 TFLOPS FP16 theoretical); the vLLM comparison ran with both kernels in one WSL2 process; host CPU not stated |
| **Compiler and flags** | CMake Release: CMAKE_CUDA_FLAGS --use_fast_math -lineinfo, CMAKE_CUDA_FLAGS_RELEASE -O3 -DNDEBUG, CXX -O3 -DNDEBUG, C++17, CMAKE_CUDA_ARCHITECTURES 80;86;89;90;120 (CMakeLists.txt); CUDA Toolkit 12.0+ (tested with 13.1) |
| **Adoption** | 12 stars |
| **Last commit** | 2026-07-03 |
| **Links** | [repository](https://github.com/Tugbars/Flash-Attention-PTX-CUDA) · [benchmark](https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/docs/vllm-comparison.md) |

## Verdict

In a same-process harness on an RTX 5080 (shared torch.randn fp16 inputs, interleaved rounds, outputs cross-checked to \~2e-4 nrmse), causal prefill latency against vLLM 0.23.0's bundled FA2 (flash_attn_varlen_func, driver-JIT from sm_80 PTX) was strictly lower at 17 of 34 shapes; the '23 of 34' headline also counts 6 losses under 2%. Wins concentrate at B=1 and short context (up to +31.9% at B=1, S=1024, D=64); losses reach -4.8% at the largest batch x context shapes; peak is \~202 vs \~212 TFLOPS. The vLLM harness script (fa_sweep2.py) is not in the repo, and the end-to-end Qwen2.5-1.5B decode wins (4.70 vs 5.12 ms/token at B=1, 5.28 vs 5.43 ms at B=8) compare this repo's best-of-3 runs on a Windows desktop GPU (5-15% run-to-run spread) with vLLM's 5-iteration average, including its scheduler and sampler.

## Use it when

- Causal fp16/bf16 prefill on an RTX 5080-class consumer Blackwell GPU at batch 1 with S up to 2048, where it measured 9-32% lower latency than vLLM 0.23's FA2 at D=64 and 4-17% at D=128 (gains shrink to 0-16% at B=4-8 with S&lt;=1024)
- Building a small custom inference loop in C++ or PyTorch on a GeForce card that needs varlen prefill, a paged KV cache and CUDA-graph-captured decode without pulling in vLLM or FlashInfer
- Long-context decode where VRAM is tight, using the FP8 KV cache (documented \~1.8x faster decode at D=128 long context, \~0.035 worst-case nrmse)
- Studying how to reach \~85% of tensor-pipe peak with mma.sync on sm_120; the docs record each optimization step and the failed experiments

## Skip it when

- Large batch times long context (B&gt;=4 with S&gt;=4096, or Llama-class H=32 at B&gt;=4): it loses to vLLM FA2 by 2-5%
- Training: only forward prefill and decode kernels are documented, no backward pass
- Hopper or datacenter Blackwell GPUs, where FlashAttention-3 or cuDNN with WGMMA/TMA apply; it builds for sm_80 and up but was tuned and measured only on one RTX 5080
- Head dims other than 64 or 128, or quantized prefill: FP8/INT4 caches are decode-only, and INT4 KV collapsed generation quality on Qwen2.5-1.5B (30/64 teacher-forced argmax agreement)
- You need a cuDNN comparison or a license file for compliance review: neither exists in the repo (MIT is stated only in the README)

## How it is fast

It uses PTX mma.sync.m16n8k16 with ldmatrix and cp.async, the tensor-core path consumer Blackwell has (no WGMMA or TMA), and keeps the whole online softmax in registers. The saturated-grid 'fat-warp' kernel gives each of 4 warps one 16-row Q tile, so softmax needs only intra-warp shuffles, and feeds P straight from the QK accumulator fragment into the PV MMA without touching shared memory; K and V loads are software-pipelined behind the matmuls. An exp2 fold (scale times log2 e folded into the score multiply) makes every exponential a raw EX2, and a runtime dispatcher sends under-saturated grids (B=1, short S) to a 32-row split-N tile that doubles the CTA count, with optional per-shape autotuning cached in a wisdom file.

## Compared with alternatives

Pick it over learn-cuda's SM120 attention or Mini-Attention when you need a usable library rather than a teaching kernel: varlen, GQA, paged and quantized KV decode, and torch.compile/CUDA-graph-ready bindings. Pick SageAttention instead if quantized QK is acceptable and you want larger consumer-GPU speedups; learn-cuda's RTX 5090 data puts PyTorch's cuDNN SDPA backend ahead of both its own kernel and the flash-attn FA2 package, and this repo never measured cuDNN.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target flash_attention) plus an optional PyTorch CUDAExtension (fa_ptx, pip install -e python/) |
| **Dependencies** | CUDA runtime only for the C++ library; PyTorch with CUDA and nvcc for the Python bindings |
| **Minimum toolchain** | CUDA Toolkit 12.0+ (tested with 13.1), CMake 3.20+, C++17; Python &gt;= 3.9 for fa_ptx |
| **Platforms** | NVIDIA compute capability 8.0+ (CMake builds sm_80/86/89/90/120), tuned only for sm_120 RTX 5080; developed on Windows (MSVC flags in setup.py and docs) and benchmarked against vLLM under WSL2 |
| **Thread safety** | not documented; every call takes an explicit cudaStream_t and the docs say all kernels are deterministic, but concurrent use of autotune and its wisdom file is not covered |
| **Drop-in for the baseline** | partial — same varlen packing and bottom-right causal convention as vLLM's flash_attn_varlen_func, but a different C++/Python API with its own args structs and cache object |

## Gotchas

- Errors terminate the process: bad arguments abort with an 'fa_\*:' message and the header's CUDA_CHECK calls exit(EXIT_FAILURE), so wrap it if your host process must survive misuse
- Index arrays (cu_seqlens, block_table, seq_lens, slot_mapping) must be device memory; host pointers give garbage output without an abort, per the troubleshooting table
- FP8 caches need k_scale/v_scale &gt; 0 set by you (zero-init default aborts); decode needs a scratch buffer sized by fa_cache_attention_scratch_bytes
- The default branch is dev/FlashAtt with no tags or releases, the README clone URL is a placeholder (yourusername/flash-attention-cuda), and docs/cutlass-comparison.md still calls the prefill kernel MHA-only while how-to-use.md documents GQA

## Known shortcomings

- 'Wins 23 of 34' is 17 strict wins plus 6 losses under 2%. The FA2 baseline is sm_80 PTX JIT-compiled on sm_120, a handicapped baseline. The vLLM harness is not in the repo. MIT stated only in the README (no LICENSE file).
- End-to-end Qwen numbers compare the author's best-of-3 on a Windows desktop GPU (5-15% spread) against vLLM's 5-iteration average including the scheduler. No cuDNN comparison. Forward only; errors abort the process.

## Caveats and trade-offs

Strictly faster at only 17 of 34 shapes; the '23 of 34' headline counts small losses as matches. It wins mainly at B=1 and short-to-mid context and loses up to about 5% at the largest batch x context shapes. The baseline vLLM FA2 wheel ships only sm_80 SASS plus PTX, so on sm_120 it runs driver-JIT code not tuned for this GPU. FA3 does not run on sm_120 and there is no cuDNN comparison. The same-process vLLM harness (fa_sweep2.py) lives in the author's WSL environment and is not in the repo, so the comparison cannot be reproduced from the repo alone; the in-repo benchmark is src/bench.cu. Single GPU, first-party, host CPU not stated. MIT is stated only in the README, with no LICENSE file. The first page of commit history goes back only to 2026-06-25.

Consumer Blackwell (sm_120) only; mma.sync-based, no WGMMA/TMA; forward/prefill kernels with paged-KV decode glue; PyTorch bindings (fa_ptx) and a C++ API; the default branch shown on GitHub is dev/FlashAtt.

## Maintenance

Active single-author project (76 commits, last 2026-07-03, 12 stars) with seven correctness-gate executables; MIT per the README but no LICENSE file, so confirm the license with the author before vendoring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/vllm-comparison.md gives first-party per-shape latency deltas against vLLM 0.23.0's FA2 (flash_attn_varlen_func) on an RTX 5080, with a same-process, interleaved, output-cross-checked methodology. The harness that runs vLLM (fa_sweep2.py) is not in the repo: scripts/ has only visualize.py and data, and src/bench.cu times only this kernel. Host CPU is also not stated, so it cannot be A; C.
- **Verifier notes:** All per-shape numbers and the end-to-end decode figures match the vLLM comparison doc and the README. Recordable shortcoming: the '23 of 34' headline is 17 strict wins plus 6 losses under 2%, and the baseline is FA2 JIT-compiled from sm_80 PTX. Metadata on github.com: MIT per README only (no LICENSE file), 12 stars, 2 forks, not a fork, 76 commits on dev/FlashAtt, last commit 2026-07-03 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `license`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/docs/vllm-comparison.md>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/README.md>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/CMakeLists.txt>
  - <https://github.com/Tugbars/Flash-Attention-PTX-CUDA>
  - <https://github.com/Tugbars/Flash-Attention-PTX-CUDA/commits>
  - <https://github.com/Tugbars/Flash-Attention-PTX-CUDA/tree/dev/FlashAtt/scripts>
- **Sources the enricher read:**
  - <https://github.com/Tugbars/Flash-Attention-PTX-CUDA>
  - <https://github.com/Tugbars/Flash-Attention-PTX-CUDA/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/README.md>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/docs/vllm-comparison.md>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/docs/how-to-use.md>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/docs/api-guide.md>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/docs/e2e-model-test.md>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/docs/cutlass-comparison.md>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/include/flash_attention.h>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/python/setup.py>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/src/bench.cu>
  - <https://raw.githubusercontent.com/Tugbars/Flash-Attention-PTX-CUDA/HEAD/LICENSE>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tugbars/flash-attention-ptx-cuda`) · [data/wave8/enrich/raw/github_com_tugbars_flash_attention_ptx_cuda.json](../../../data/wave8/enrich/raw/github_com_tugbars_flash_attention_ptx_cuda.json) (enrichment confidence 0.8)

</details>
