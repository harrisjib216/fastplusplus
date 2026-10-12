# PowerInfer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> llama.cpp-derived CPU/GPU hybrid LLM engine that exploits ReLU activation sparsity; up to 11.69x llama.cpp on one RTX 4090.

| | |
|---|---|
| **Beats** | llama.cpp |
| **Claimed result** | Outperforms llama.cpp by up to 11.69x on an RTX 4090 (README: up to 11x on Falcon 40B, up to 3x on Llama 2 70B); on an RTX 2080Ti with INT4 models up to 8x on Falcon 40B and 3x on Llama 2 70B. Average 13.20 tokens/s and peak 29.08 tokens/s on the RTX 4090, 18% below an A100. |
| **Workload** | Single-request LLM generation on one RTX 4090 (24 GB) with FP16 ReLU models (Falcon(ReLU)-40B, Llama(ReLU)-2-70B; the paper abstract also covers OPT-175B) at input length 64, plus an RTX 2080Ti (11 GB) run with INT4 ReLU models at input length 8. Speed is reported as end-to-end tokens/s (prompt + generation time divided by tokens generated). |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 4090 (24 GB) and RTX 2080Ti (11 GB); CPU model not given in the README |
| **Adoption** | 9.8k stars |
| **Last commit** | 2026-05-11 |
| **Links** | [repository](https://github.com/Tiiny-AI/PowerInfer) · [benchmark](https://github.com/SJTU-IPADS/PowerInfer) |

## Verdict

Per the README and the SOSP '24 paper, PowerInfer vs llama.cpp (late-2023 version) on one RTX 4090 with FP16 ReLU models (input length 64) reaches up to 11x on Falcon(ReLU)-40B and up to 3x on Llama(ReLU)-2-70B, averaging 13.20 tokens/s (peak 29.08) and up to 11.69x across models including OPT-175B; on an RTX 2080Ti with INT4 models (input length 8) it reaches up to 8x on Falcon-40B and 3x on Llama-2-70B. WebSearch snippets of the paper give the host as an Intel i9-13900K with 192 GB RAM (paper PDF not opened); compiler and flags are not stated, and the per-configuration numbers are only in README images.

## Use it when

- Single-user, batch-1 local generation on one consumer GPU (RTX 4090 24 GB, RTX 2080Ti 11 GB) with a model 2-6x larger than VRAM, such as a 40B or 70B model in FP16 or INT4.
- You can use or create a ReLU-sparse model variant (ReluLLaMA, ReluFalcon, ProSparse-Llama-2, Bamboo-7B, TurboSparse) and accept its accuracy.
- x86-64 hosts with AVX2 plus an NVIDIA (CUDA) or AMD (ROCm/HIP) GPU, on Linux or Windows.
- Research on activation-sparsity offloading: the predictor, the ILP placement and the sparse ggml operators are all in the tree.

## Skip it when

- Mainstream dense models (Llama 3, Qwen, Mistral and other SiLU/GELU models): the FAQ says only ReLU-family activations are supported, and llama.cpp weights give no gain.
- Accuracy-sensitive use of the 70B ReLU models: the FAQ says the ReLU fine-tune used only 5B tokens and shows a noticeable drop, worst for 70B.
- Multi-GPU boxes, multi-tenant serving or high-batch throughput: multi-GPU is an open TODO and the published speedups are for single-request generation.
- Apple Silicon: CPU-only on macOS, where the README says the improvement 'is not significant', and the Metal backend is still a TODO.
- Projects that need upstream llama.cpp features: the ggml/llama.cpp base is a late-2023 snapshot and the engine code has seen little change since 2024 (recent commits are README edits plus the 2025 SmallThinker drop).

## How it is fast

Neuron activations in ReLU LLMs follow a power law: a few 'hot' FFN neurons fire for most inputs while most 'cold' neurons fire rarely. PowerInfer profiles activations offline, solves an integer linear program (cvxopt GLPK, in powerinfer-py/solver.py) to place hot neurons in VRAM and leave cold ones in host RAM, then at runtime uses small per-layer MLP predictors to guess which neurons will fire and computes only those, hot ones on the GPU and cold ones on the CPU, so weights never cross PCIe per token. ggml gains neuron-aware sparse operators for this (GGML_OP_MUL_MAT_SPARSE, GGML_OP_AXPY, ggml_mul_mat_idx with sparse and GPU index tensors). The baseline loses because llama.cpp offloads whole layers and must run every remaining dense layer on the CPU.

## Compared with alternatives

Pick PowerInfer over ik_llama.cpp, llamafile tinyBLAS, T-MAC or BitNet when the bottleneck is a model larger than your GPU's VRAM and you can run a ReLU-sparse variant: those siblings speed up dense or low-bit matmuls on the CPU, while PowerInfer avoids computing most FFN neurons at all. For standard dense models, or CPU-only machines, ik_llama.cpp or llamafile are the better choice.

## Integration

| | |
|---|---|
| **Form** | static lib + CLI binaries (CMake build of a llama.cpp-style tree: main, server, quantize, batched, perplexity) |
| **Dependencies** | CUDA toolkit with cuBLAS (-DLLAMA_CUBLAS=ON) or ROCm hipBLAS (-DLLAMA_HIPBLAS=ON) for GPU builds; Python 3.8+ with the powerinfer helper package (torch&gt;=2, cvxopt 1.3.2) for GPU-split solving, plus numpy, sentencepiece, transformers and gguf-py for weight conversion; the smallthinker/ engine needs clang-21 and mold |
| **Minimum toolchain** | C11 / C++11, CMake 3.17+ (README; the top-level CMakeLists declares 3.13 and raises it to 3.17 for CUDA) |
| **Platforms** | x86-64 with AVX2 on Linux and Windows, with or without NVIDIA or AMD GPUs; Apple M-series CPU-only on macOS without significant gains |
| **Thread safety** | not documented (inherits llama.cpp's per-context model: one llama_context per thread of generation) |
| **Drop-in for the baseline** | partial — same CLI and examples as llama.cpp with --vram-budget instead of -ngl, but it needs PowerInfer GGUF files with predictors and activation statistics, and runs only ReLU-family models fast |

## Gotchas

- FFN splitting fails quietly: if the powerinfer Python module or the model's activation/ directory is missing, no GPU index is generated and generation falls back to slow mode (see issue #131, 'Activation_32 Not Found (Very slow inference)'); check the log for 'offloaded ... MiB of FFN weights to GPU'.
- The generated .gpuidx placement is cached next to the model; after changing VRAM budget or hardware, a stale cache can cause CUDA_ERROR_OUT_OF_MEMORY, fixed with --reset-gpu-index, a lower --vram-budget or --disable-gpu-index (FAQ).
- LLAMA_NATIVE defaults to ON (-march=native), so binaries built on one CPU may not run on another.
- Dense GGUFs from convert-dense.py may not work in llama.cpp because the activations (ReluLLaMA, ProSparse) or the architecture (Bamboo) were changed.

## Known shortcomings

- Speedup (11.69x vs llama.cpp) needs ReLU-sparsified models: stock llama.cpp weights get no gain and the README FAQ admits the ReLU 70B model loses accuracy; OPT and predictor-training code unreleased; SOSP '24 venue (DOI 10.1145/3694715.3695964) seen only in search results; repo moved to Tiiny-AI/PowerInfer.
- OPT model code was released 2025-02-19 (#245) though the README TODO still lists it; engine code last changed 2025-07 (2026 commits are README-only), so 'active' overstates it; builds with -march=native by default; FFN split quietly falls back to a slow mode (issue #131).

## Caveats and trade-offs

The speedup depends on ReLU-sparsified models (ReLU/ReGLU/Squared-ReLU only). The README says standard llama.cpp weights run with no performance gain, and its FAQ admits the ReLU fine-tuned models (5B tokens of retraining) lose accuracy, especially the 70B. The llama.cpp baseline dates from late 2023. README charts are images, and the text gives only maxima (11x Falcon 40B, 3x Llama 2 70B on the 4090; 8x and 3x on the 2080Ti). The peer-reviewed paper (SOSP '24, DOI 10.1145/3694715.3695964) could not be opened from this container. CPU model, compiler and flags are not stated on pages opened. OPT support code and predictor-training code are still unreleased TODOs. The repo now lives at github.com/Tiiny-AI/PowerInfer (the SJTU-IPADS URL resolves there); Tiiny AI sells hardware built on it. It is derived from llama.cpp (LICENSE copyright Georgi Gerganov and SJTU-IPADS) but is not marked as a GitHub fork.

GPU-CPU hybrid engine that exploits activation sparsity, so it needs ReLU-style sparse model variants (ReLU-fied Falcon and Llama 2, Bamboo, TurboSparse); dense models get no speedup; built on llama.cpp/ggml code and model format; x86-64 with AVX2.

## Maintenance

MIT-licensed with about 9.8k stars, but now owned by Tiiny-AI, which sells hardware built on it; engine code last changed in 2025 (OPT model code on 2025-02-19, SmallThinker on 2025-07-27) with only README commits since, so 'active' overstates the core's maintenance.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** The README gives the paper's headline result (up to 11.69x over llama.cpp, 13.20 tokens/s average and 29.08 peak on one RTX 4090), and WebSearch results list the same paper in ACM DL (DOI 10.1145/3694715.3695964) as SOSP '24, with the authors' copy named song-sosp24.pdf. The work is peer-reviewed, so B. It cannot be A: the README charts are images, no CPU model, compiler or flags are given, and the evaluation scripts (OPT code, predictor training) are listed as unreleased TODOs.
- **Verifier notes:** Numbers match the README. Tier raised from C to B because the paper appeared at SOSP '24, but the venue was seen only in WebSearch result listings (arxiv.org, dl.acm.org and ipads.se.sjtu.edu.cn are blocked here); a retier check can confirm. The repo moved to Tiiny-AI/PowerInfer, so consider overriding repo_url. Metadata checked: MIT, 9.8k stars, last commit 2026-05-11, not archived, not a fork.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SJTU-IPADS/PowerInfer/HEAD/README.md>
  - <https://github.com/SJTU-IPADS/PowerInfer>
  - <https://github.com/Tiiny-AI/PowerInfer/commits>
  - <https://raw.githubusercontent.com/Tiiny-AI/PowerInfer/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Tiiny-AI/PowerInfer/HEAD/README.md>
  - <https://raw.githubusercontent.com/Tiiny-AI/PowerInfer/HEAD/docs/token_generation_performance_tips.md>
  - <https://raw.githubusercontent.com/Tiiny-AI/PowerInfer/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Tiiny-AI/PowerInfer/HEAD/ggml.h>
  - <https://raw.githubusercontent.com/Tiiny-AI/PowerInfer/HEAD/smallthinker/README.md>
  - <https://raw.githubusercontent.com/Tiiny-AI/PowerInfer/HEAD/powerinfer-py/powerinfer/solver.py>
  - <https://raw.githubusercontent.com/Tiiny-AI/PowerInfer/HEAD/powerinfer-py/pyproject.toml>
  - <https://raw.githubusercontent.com/Tiiny-AI/PowerInfer/HEAD/requirements.txt>
  - <https://github.com/Tiiny-AI/PowerInfer>
  - <https://github.com/Tiiny-AI/PowerInfer/commits>
  - <https://github.com/Tiiny-AI/PowerInfer/issues?q=is%3Aissue+slower+OR+segmentation+OR+wrong>
  - WebSearch: PowerInfer SOSP 2024 evaluation hardware (snippets of ipads.se.sjtu.edu.cn/_media/publications/song-sosp24.pdf and arxiv.org/abs/2312.12456)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sjtu-ipads/powerinfer`) · [data/wave8/enrich/raw/github_com_sjtu_ipads_powerinfer.json](../../../data/wave8/enrich/raw/github_com_sjtu_ipads_powerinfer.json) (enrichment confidence 0.75)

</details>
