# ZhiLight

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Zhihu/ModelBest C++/CUDA LLM serving engine tuned for PCIe multi-GPU boxes; cut TTFT versus vLLM and SGLang on 4x AD102.

| | |
|---|---|
| **Beats** | vLLM and SGLang (versions not stated) |
| **Claimed result** | Llama-3.1-70B-Instruct-GPTQ-INT4 on 4x AD102 PCIe: TTFT mean 1419.74 ms vs vLLM 4796.32 ms and SGLang 3962.99 ms, TPOT mean 30.97 vs 41.54 and 63.22 ms. Qwen1.5-110B-GPTQ-Int4 on 4x AD102: QPS 0.18 vs 0.09 for both vLLM and SGLang, TTFT mean 1671.38 vs 3085.74 ms (vLLM). DeepSeek-R1 AWQ on 8x A800: QPS 0.16 vs vLLM 0.08. |
| **Workload** | LLM serving benchmark (QPS, TTFT, TPOT) with 3.7k-token prompts (DeepSeek-R1 AWQ: 2.8k prompt, 750 output tokens) on NVIDIA AD102 PCIe (x1, x2, x4), A800 (x4, x8) and H20 (x8), for models from MiniCPM-2B to DeepSeek-R1. Runs use the ZhiLight benchmark Docker tool, which sweeps offered QPS via --min_qps/--max_qps/--qps_step. |
| **Metric** | latency |
| **Hardware** | NVIDIA AD102 PCIe (1, 2 and 4 GPUs), A800 (x4, x8), H20 (x8); CPU not stated |
| **Adoption** | 908 stars |
| **Last commit** | 2026-03-18 |
| **Links** | [repository](https://github.com/zhihu/ZhiLight) · [benchmark](https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/docs/benchmarks/benchmarks.md) |

## Verdict

Zhihu's own serving benchmark (a closed-source Docker load generator that steps offered QPS, 3.7k-token prompts) on 4x AD102 PCIe shows Llama-3.1-70B GPTQ-INT4 at 1419.74 ms mean TTFT vs vLLM 4796.32 and SGLang 3962.99 ms, and TPOT 30.97 vs 41.54 and 63.22 ms; on A800 and for the 8B model SGLang or vLLM win. Engine versions, CPU, driver and compiler flags are not stated.

## Use it when

- Serving dense 14B-110B INT4 (GPTQ/AWQ) models with tensor parallelism on 2-4 PCIe Ada-class GPUs without NVLink, where time to first token on \~4k-token prompts matters most
- Prefill-heavy traffic such as RAG or long-prompt chat: its clearest wins are TTFT (for example 1111.8 ms vs vLLM 3493.97 and SGLang 2276.1 ms for Qwen2-72B GPTQ on 4x AD102)
- DeepSeek-R1 AWQ or FP8 on 8x A800/H20 nodes where the published run sustained twice vLLM's offered QPS
- Teams that already run Llama, Qwen2 or DeepSeek models and want an OpenAI-compatible endpoint with a self-built CUDA 12 wheel or Docker image

## Skip it when

- Small models or decode-heavy workloads: on 2x AD102 Llama-3.1-8B it lost to vLLM and SGLang on every metric (TPOT 66.24 vs 18.68 ms for vLLM), and its TPOT was also worse for MiniCPM-2B, Qwen1.5-110B on AD102 and DeepSeek-R1
- NVLink data-center GPUs: on 4x A800, SGLang sustained twice ZhiLight's QPS for Qwen2-72B and Qwen1.5-110B
- Non-NVIDIA hardware, pre-Ampere GPUs or aarch64 hosts: default CUDA architectures are 80, 89 and 90a, FP8 conversion needs sm_89+ (open issue #12), and DeepGEMM, FlashMLA and the AVX host all-reduce are x86-64 only
- You need independently reproduced numbers or an open benchmark: the load generator ships only as a Docker image (issue #17 asked for its source), and open issue #59 reports 4017.89 ms mean TTFT on 4x RTX 4090 with a 4k prompt at concurrency 1, about 3.6x the README's \~1112 ms, with no maintainer reply
- Broad model coverage and community support: a small Zhihu team (111 commits), many issues answered in Chinese or not at all, and no GitHub releases

## How it is fast

It targets tensor parallelism over PCIe, where all-reduce is the bottleneck: 'dual streams' overlap prefill (encode) compute with the all-reduce on a second CUDA stream (the CHANGELOG claims 20%+ on a '4090pro'), the all-reduce can be quantized to INT8 above a token threshold (REDUCE_TP_INT8_THRES), and an optional host-side all-reduce sums FP16/FP32 buffers on the CPU with AVX/F16C intrinsics. On the GPU it fuses QKV, feed-forward input, residual and layernorm kernels, uses a tensor-core fused batch attention for decode, flash-attention prefill and chunked prefill, and calls Marlin (GPTQ), TensorRT-LLM W4A16/W4A8/INT8 GEMMs and DeepGEMM/FlashMLA for DeepSeek.

## Compared with alternatives

Pick ZhiLight when you need a whole multi-GPU serving engine for INT4 70B-class models on PCIe GPUs; FasterTransformer is archived in favor of TensorRT-LLM, PowerInfer targets a single consumer GPU with CPU offload and sparse activation, and Marlin is just the GPTQ matmul kernel that ZhiLight itself calls.

## Integration

| | |
|---|---|
| **Form** | module (Python package built by setup.py/CMake into a wheel with a C++/CUDA static backend and pybind11 extension); Docker image ghcr.io/zhihu/zhilight/zhilight |
| **Dependencies** | CUDA 12+ runtime, cuBLAS, NCCL; PyTorch &gt;= 2.4.1; a flash-attn &gt;= 2.7.0.post2 shared library (CMake stops if none is found); transformers, fastapi, uvicorn, pybind11 2.13.6; vendored bmengine, deep_gemm, flash_decoding, flash_mla and zmq; Boost.Serialization for multi-node inference |
| **Minimum toolchain** | C++17 and CUDA C++17, CUDA 12.0+ (Dockerfile: CUDA 12.4.1, NCCL 2.21.5), CMake 3.20+, Python 3.9+; the C++ ABI flag is taken from the installed torch |
| **Platforms** | Linux x86-64 with NVIDIA GPUs (Ampere sm_80, Ada sm_89, Hopper sm_90a by default); tested on AD102 PCIe, A800 and H20 |
| **Thread safety** | not documented (server process with its own scheduler and dynamic batching) |
| **Drop-in for the baseline** | partial — the OpenAI-compatible HTTP API is adapted from vLLM, so clients carry over, but server flags, the --env tuning string and the model loaders differ |

## Gotchas

- The fast published configurations depend on an --env string of knobs (HIGH_PRECISION=0, CPM_FUSE_QKV=1, CPM_FUSE_FF_IN=2, REDUCE_TP_INT8_THRES=100, DUAL_STREAM=1) shown in the benchmark launch lines; HIGH_PRECISION=0 and INT8 all-reduce trade numerical precision for speed, which the vLLM/SGLang baselines did not do
- In several baseline runs SGLang was launched with --disable-radix-cache, while ZhiLight's prefix-cache setting is not stated, so prefix reuse may differ between engines
- The benchmark doc's Qwen1.5-110B launch line misspells the module (api_sever), and the benchmark tool is pulled as image 1.0.1 but run as 1.0.0
- Reported QPS values are offered-load steps (many engines tie at exactly 0.09 or 0.18), so a 2x QPS is the next sustained step, not a measured 2x throughput

## Known shortcomings

- Mixed results: Llama-3.1-8B TPOT 66.24 ms vs vLLM 18.68 ms; SGLang beats it on A800 QPS; QPS values look like offered-load steps; bench tool ships as a Docker image only; a serving engine, not a kernel library, so the category is questionable.
- Claim not reproduced: open issue #59 measured 4017.89 ms mean TTFT on 4x RTX 4090 (72B GPTQ, 4k prompt, concurrency 1) vs README \~1112 ms, no reply; benchmark tool source never released (#17); wins rely on HIGH_PRECISION=0 and INT8 all-reduce; several SGLang baseline runs had --disable-radix-cache.

## Caveats and trade-offs

Results are mixed within the same document. Llama-3.1-8B on 2x AD102: ZhiLight QPS 0.4 vs vLLM 0.46 and SGLang 0.84, TTFT 1091.12 vs 915.58 ms (vLLM), TPOT 66.24 vs 18.68 ms (vLLM). Qwen2-72B on 4x A800: SGLang QPS 0.36 vs ZhiLight 0.18. Qwen1.5-110B on 4x A800: SGLang QPS 0.18 vs ZhiLight 0.1. ZhiLight TPOT is worse in several rows (DeepSeek-R1 AWQ 115.97 vs vLLM 109.86 ms; Qwen1.5-110B on AD102 39.68 vs 30.34 ms; MiniCPM-2B 26.1 vs 16.71 ms). The clearest wins are TTFT on PCIe AD102 multi-GPU runs. QPS values look like offered-load steps from the benchmark tool (many engines tie at exactly 0.09 or 0.18), so QPS ratios may reflect the highest load step sustained rather than measured throughput. The benchmark tool is distributed as a Docker image, with its source not found in the pages opened. vLLM/SGLang versions and compiler flags are not stated, and there is no H20 baseline. This is an LLM serving engine rather than a kernel library, and its baselines are not in the category list.

Targets PCIe-connected GPUs (dual-stream encode and all-reduce overlap, INT8 reduce); supports INT8, FP8, AWQ and GPTQ; OpenAI-compatible server; the repo is C++/CUDA with a Python server layer.

## Maintenance

Active (last commit 2026-03-18, recent work on session generation and W4A8 caching; 908 stars), Apache-2.0, buildable from source or Docker (README tag 0.4.8-cu124), but the speed claims are first-party and one third-party report did not reproduce them.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party tables in docs/benchmarks/benchmarks.md compare ZhiLight against vLLM and SGLang, with exact launch arguments for each engine. The benchmark tool ships only as a Docker image (ghcr.io/zhihu/zhilight/benchmark), engine versions are not stated, and no CPU model, compiler or flags are given, so C.
- **Verifier notes:** All quoted numbers match benchmarks.md and the README. Metadata checked: Apache-2.0, 908 stars, last commit 2026-03-18, not archived, not shown as a fork. The category fit (a serving engine filed under autodiff-and-ml-kernels) is questionable; the orchestrator may want a category override.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/docs/benchmarks/benchmarks.md>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/README.md>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/docs/benchmarks/README.md>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/LICENSE>
  - <https://github.com/zhihu/ZhiLight>
  - <https://github.com/zhihu/ZhiLight/commits>
- **Sources the enricher read:**
  - <https://github.com/zhihu/ZhiLight>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/README.md>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/docs/benchmarks/benchmarks.md>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/docs/benchmarks/README.md>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/setup.py>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/src/model/host_all_reducer.cpp>
  - <https://raw.githubusercontent.com/zhihu/ZhiLight/HEAD/examples/offline_inference.py>
  - <https://github.com/zhihu/ZhiLight/tree/main/3rd>
  - <https://github.com/zhihu/ZhiLight/tree/main/3rd/bmengine>
  - <https://github.com/zhihu/ZhiLight/tree/main/src>
  - <https://github.com/zhihu/ZhiLight/tree/main/src/nn>
  - <https://github.com/zhihu/ZhiLight/tree/main/src/model>
  - <https://github.com/zhihu/ZhiLight/tree/main/examples>
  - <https://github.com/zhihu/ZhiLight/issues?q=is%3Aissue>
  - <https://github.com/zhihu/ZhiLight/issues/59>
  - <https://github.com/zhihu/ZhiLight/issues/17>
  - <https://github.com/zhihu/ZhiLight/issues/58>
  - <https://github.com/zhihu/ZhiLight/issues/12>
  - <https://github.com/zhihu/ZhiLight/commits/main>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/zhihu/zhilight`) · [data/wave8/enrich/raw/github_com_zhihu_zhilight.json](../../../data/wave8/enrich/raw/github_com_zhihu_zhilight.json) (enrichment confidence 0.7)

</details>
