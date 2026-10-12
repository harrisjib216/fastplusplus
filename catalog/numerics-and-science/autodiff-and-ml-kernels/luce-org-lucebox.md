# Lucebox Megakernel (single-launch CUDA forward pass for Qwen 3.5-0.8B)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Model-specific CUDA decode megakernel for Qwen 3.5-0.8B at batch 1; 1.55x llama.cpp BF16 decode on an RTX 3090.

| | |
|---|---|
| **Beats** | llama.cpp (BF16, CUDA backend) and PyTorch + HuggingFace Transformers (BF16) |
| **Claimed result** | RESULTS.md (RTX 3090, BF16): prefill pp520 21,347 tok/s vs llama.cpp BF16 11,247 and PyTorch HF 7,578; decode tg128 413 tok/s vs llama.cpp 267 (1.55x) and PyTorch HF 108 (3.8x). The megakernel README states '1.9x faster prefill, 1.55x faster decode vs llama.cpp'. DVFS table: 411 tok/s and 1.87 tok/J at a 220 W limit, 433 tok/s at stock. |
| **Workload** | Batch-1 prefill of 520 tokens (pp520) and decode of 128 tokens (tg128) for Qwen 3.5-0.8B in BF16 on an RTX 3090. Decode runs as one persistent CUDA kernel for all 24 layers (kernel.cu); prefill on the 3090 uses prefill.cu (cuBLAS plus standalone kernels), not the megakernel (a single-dispatch prefill megakernel exists only on Blackwell). |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 3090 24GB for the llama.cpp comparison; the megakernel README adds RTX 2080 Ti results (13,919 / 250 tok/s, FP16) and RESULTS.md adds DGX Spark GB10 (NVFP4 decode, CUDA 13.2) versus PyTorch HF only; Apple M5 Max 36GB appears only as an LM Studio (llama.cpp) reference at 229 tok/s. Host CPU not stated. |
| **Compiler and flags** | setup.py: nvcc -O3 -arch=sm_&lt;auto-detected, sm_86 for RTX 3090&gt; --use_fast_math -std=c++17 plus NUM_BLOCKS/BLOCK_SIZE defines; host -O3; CUDA toolkit version for the RTX 3090 run not stated. |
| **Adoption** | 2.9k stars (whole Lucebox repo) |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/Luce-Org/lucebox) · [benchmark](https://github.com/Luce-Org/lucebox/blob/main/optimizations/megakernel/RESULTS.md) |

## Verdict

On an RTX 3090 in BF16, the first-party RESULTS.md reports pp520 at 21,347 tok/s against 11,247 for llama.cpp BF16 (unversioned, 'default settings', run outside the harness) and 7,578 for eager Hugging Face Transformers; tg128 is 413 vs 267 vs 108 tok/s (1.55x and 3.8x). The repo's final_bench.py times only the megakernel and Hugging Face (10 warm-up plus 20 timed prefills, perf_counter around cuda.synchronize); the CUDA version and host CPU of the 3090 run are not stated, and the numbers predate the PR #761 and #804 correctness fixes.

## Use it when

- Single-user, batch-1 local generation with Qwen 3.5-0.8B in BF16 on an Ampere or newer NVIDIA consumer GPU (RTX 3090 is the tuned target), where decode latency and tokens per joule matter.
- Power-capped deployments: the DVFS sweep keeps 411 tok/s at a 220 W limit against 433 tok/s at stock.
- As a reference implementation when writing your own persistent decode kernel for a hybrid linear-attention (DeltaNet) plus attention model.
- Turing (RTX 2080 Ti, FP16) or Blackwell (RTX 5090, DGX Spark via an NVFP4 decode path) when you need this model there and accept less-documented paths.

## Skip it when

- Any other model or size: the layer layout, head counts and vocabulary are compile-time constants, and the README says fusion gains shrink as models grow.
- Batched or multi-tenant serving (batch size 1 only; the README points to vLLM or SGLang), quantized weights (no GGUF, GPTQ or AWQ), or prompts longer than the default max_seq_len of 2048.
- Where output must match the reference model today: the in-place RoPE bug fixed by PR #804 (open on 2026-10-01) gave about 47% top-token agreement with Hugging Face before the fix.
- Sampling-based generation: decode does greedy argmax with an optional repetition penalty and has no temperature or top-p.
- A GPU shared with other work (other processes, MPS): the grid barrier needs every block to be resident at the same time.

## How it is fast

Decode runs all 24 layers in one persistent kernel (decode_kernel in kernel.cu, 82 blocks x 512 threads on a 3090), so there are no per-layer launches or CPU round-trips. Blocks meet at a hand-rolled atomic grid barrier (AtomicGridSync) between phases. Each layer is a bandwidth-bound BF16 matrix-vector product with FP32 accumulation, the DeltaNet recurrence keeps its state in FP32, and attention uses online softmax with the KV cache written inside the kernel. A second kernel does the 248,320-row LM head and argmax. On the 3090, prefill (prefill.cu) is cuBLAS GEMMs plus standalone kernels and a chunk-parallel DeltaNet scan (chunk size 8); it is not a megakernel.

## Compared with alternatives

Pick it over yalm or ik_llama.cpp only when the model is exactly Qwen 3.5-0.8B at batch 1 on an NVIDIA GPU and decode tok/s or tok/J is what you are optimizing; those engines run many models. For batched or large-model Gated DeltaNet prefill on datacenter GPUs, FlashQLA's kernels are the closer fit.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | PyTorch 2.0+ (torch.utils.cpp_extension build), cuBLAS (plus cuBLASLt on Blackwell), Hugging Face transformers and the Qwen/Qwen3.5-0.8B weights; built with pip install -e . --no-build-isolation or uv sync --extra megakernel |
| **Minimum toolchain** | CUDA 12+ with nvcc -std=c++17 -O3 --use_fast_math; Blackwell sm_120/sm_121a needs CUDA 12.8+ (cuda_fp4.h); RESULTS.md's GB10 run used CUDA 13.2 |
| **Platforms** | NVIDIA only, Linux: sm_86 (RTX 3090, BF16) is the benchmarked target; sm_75 (FP16), sm_80+ (BF16), Pascal sm_6x shims in the source, and Blackwell sm_120/121a via NVFP4; the arch is auto-detected at build time |
| **Thread safety** | not documented; a Decoder owns one KV cache, DeltaNet state and barrier counters, so use one Decoder per stream, and each step() syncs to the host to read the token |
| **Drop-in for the baseline** | false - a Python Decoder API for one model, not a llama.cpp or Transformers replacement; no OpenAI-compatible server, GGUF loading or batching on this path |

## Gotchas

- Known correctness bugs after the published numbers: PR #761 (merged 2026-09-24) fixed attention blocks overwriting each other's partial results in full_attention_layer (non-repeatable output), and PR #804 (open on 2026-10-01) fixes Q RoPE rotating in place, so the second half of each rotary pair reads an already-rotated value. kernel.cu at HEAD still has this pattern.
- The built-in correctness check in bench_pp_tg.py compares the megakernel against its own step-by-step decode path, not against Hugging Face, so it cannot catch math errors both paths share. final_bench.py prints both completions but does not compare them.
- 'Single dispatch' means the 24 layers: each token still launches decode_kernel plus a separate lm_head_kernel, with three small memsets. The grid barrier is an atomic spin-wait under a normal &lt;&lt;&lt;&gt;&gt;&gt; launch, not cudaLaunchCooperativeKernel; the block count is clamped to the occupancy-reported resident limit, and the README warns that grid.sync inside loops deadlocks silently.
- Prefill speedups on the 3090 come from cuBLAS plus standalone kernels, not the megakernel. Only Blackwell has a single-dispatch prefill megakernel.

## Known shortcomings

- 413 tok/s is the stock run (220 W power cap gives 411). Prefill on the RTX 3090 uses cuBLAS plus separate kernels, not the megakernel. llama.cpp is run separately with no version stated.
- All published numbers predate two correctness fixes: PR #761 (merged 2026-09-24) fixed a cross-block attention race that gave non-repeatable output, and PR #804 (open 2026-10-01) fixes an in-place Q RoPE bug still in kernel.cu at HEAD (before the fix about 47% top-token agreement with HF, cosine 0.70, on an RTX 3050). bench_pp_tg.py's 'correctness' compares the megakernel with its own decode path, not HF. Not one dispatch (decode_kernel plus lm_head_kernel per token); the grid barrier is an atomic spin under a plain launch, not cooperative launch; greedy argmax only; the HF baseline is eager mode. Lucebox sells hardware.

## Caveats and trade-offs

First-party benchmark. llama.cpp is 'latest release at time of testing, BF16 mode, default settings' with no version, command or flags, and final_bench.py does not run it ('(run separately)'); host CPU and the CUDA version of the 3090 run are not stated. Only 0.8B parameters, batch 1, hand-written for one model's 18 DeltaNet + 6 attention layout; the README says fusion benefits shrink as model size grows, and llama.cpp has only generic, unfused DeltaNet support. Prefill on the 3090 is cuBLAS plus separate kernels, so the 1.9x prefill gain is not a megakernel result. The 413 tok/s headline is the stock run; the efficiency comparison table pairs 411 tok/s at a 220 W limit with llama.cpp's 267 tok/s at 350 W, and the DVFS table's stock row (433 tok/s) differs from the 413 headline without explanation. A search summary of the HN thread quoted 37,800 tok/s prefill, which is not on RESULTS.md; only RESULTS.md numbers are used. HN thread not opened (egress blocked). The repo was renamed from luce-megakernel to lucebox and also hosts DFlash, PFlash, KVFlash and Spark, not assessed here.

Hard-wired to one small hybrid DeltaNet/attention model (Qwen 3.5-0.8B); batch size 1 only (README says to use vLLM or SGLang for batched throughput); BF16 on Ampere (FP16 path for Turing, NVFP4 path for Blackwell); built as a PyTorch C++/CUDA extension, so it is not a general kernel library.

## Maintenance

Very active (last commit 2026-10-01) in an Apache-2.0 repo with 2.9k stars from Lucebox, which sells a local-AI PC; the megakernel is a self-described research proof of concept for one model, copyable but with an open RoPE correctness fix at the time of reading.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** RESULTS.md gives first-party RTX 3090 pp520/tg128 numbers against llama.cpp BF16 and PyTorch HF. The harness optimizations/megakernel/final_bench.py (10 warm-up + 20 timed prefill runs, perf_counter with cuda.synchronize) times only the megakernel and PyTorch HF and prints llama.cpp as '(run separately)' with no command or version; setup.py gives nvcc flags, but the CUDA version for the 3090 run and the host CPU are not stated, so C.
- **Verifier notes:** Numbers verified on RESULTS.md and the megakernel README. Corrected the record's caveat: the 413 tok/s figure is not a 220 W reading (220 W gives 411 tok/s in the DVFS table). Metadata on github.com: Apache-2.0 (LICENSE file checked), 2.9k stars, 283 forks, not a fork or archived, 1,945 commits, last commit 2026-10-01 (active).
- **Fields the verifier corrected:** `workload`, `hardware`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/Luce-Org/lucebox>
  - <https://github.com/Luce-Org/lucebox/commits>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/RESULTS.md>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/README.md>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/setup.py>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/final_bench.py>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/README.md>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/README.md>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/README.md>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/RESULTS.md>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/setup.py>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/final_bench.py>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/kernel.cu>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/prefill.cu>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/model.py>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/torch_bindings.cpp>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/bench_pp_tg.py>
  - <https://raw.githubusercontent.com/Luce-Org/lucebox/HEAD/optimizations/megakernel/half_type.h>
  - <https://github.com/Luce-Org/lucebox/issues?q=megakernel>
  - <https://github.com/Luce-Org/lucebox/pull/761>
  - <https://github.com/Luce-Org/lucebox/pull/804>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/luce-org/lucebox`) · [data/wave8/enrich/raw/github_com_luce_org_lucebox.json](../../../data/wave8/enrich/raw/github_com_luce_org_lucebox.json) (enrichment confidence 0.75)

</details>
