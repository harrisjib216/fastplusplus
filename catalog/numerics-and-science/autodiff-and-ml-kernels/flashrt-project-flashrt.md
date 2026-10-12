# FlashRT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Hand-built CUDA-graph inference pipelines for robot VLA models (Pi0/Pi0.5, GR00T) on Jetson Thor and RTX GPUs; beats TensorRT latency.

| | |
|---|---|
| **Beats** | NVIDIA TensorRT, torch.compile, PyTorch eager, OpenPI reference implementation (numbers copied from NVIDIA Isaac GR00T and Jetson AI Lab pages, not re-measured in one harness) |
| **Claimed result** | docs/benchmark_comparison.md: GR00T N1.6 on Jetson AGX Thor (T=50): 45 ms vs TensorRT 92 ms (2.04x), torch.compile 105 ms (2.33x), PyTorch eager 117 ms (2.60x); RTX 5090 (T=50, 2-view): 13.08 ms vs TensorRT 31 ms (2.37x), torch.compile 37 ms (2.83x), eager 58 ms (4.43x). Pi0.5 NVFP4 3-view on Thor: 51.51 ms vs OpenPI reference 714 ms (13.9x). On the matched GR00T N1.7 LIBERO harness on Thor (NVIDIA's published protocol, re-run by FlashRT): FlashRT FP8 36.8 ms vs TensorRT optimized + FP8 \~44 ms, and FlashRT NVFP4 23.7 ms vs TensorRT mixed NVFP4 \~40 ms (about 1.2x and 1.7x, derived from page data). |
| **Workload** | Vision-language-action model inference (GR00T-N1.6-3B with T=50, Pi0.5 3-view) on Jetson AGX Thor and RTX 5090 using static CUDA Graph capture and hand-written FP8/NVFP4 kernels. |
| **Metric** | latency |
| **Hardware** | Jetson AGX Thor, RTX 5090, RTX 4090 (local baselines), AMD Instinct MI350X |
| **Compiler and flags** | README build requirements: CUDA 12.4+ (Thor/Hopper) or 12.8+ (Blackwell), CUDA 13 recommended, GCC/G++ 11+ (C++17), CMake 3.24+ with -DGPU_ARCH (110 Thor, 120 RTX 5090, 89 RTX 4090); the toolkit version and flags used for the published rows are not stated. Thor N1.7 rows were run under JetPack 7.2, MAXN. |
| **Adoption** | 607 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/flashrt-project/FlashRT) · [benchmark](https://raw.githubusercontent.com/flashrt-project/FlashRT/HEAD/docs/benchmark_comparison.md) |

## Verdict

FlashRT's own FP8 latencies for GR00T-N1.6-3B (Thor 45 ms end to end; RTX 5090 13.08 ms graph replay) are set against NVIDIA's published GR00T-N1.6 TensorRT, torch.compile and eager numbers (92/105/117 ms Thor, 31/37/58 ms RTX 5090), not re-measured in one harness; the only matched-harness rows (GR00T N1.7 LIBERO on Thor, JetPack 7.2 MAXN, 4 denoising steps, batch 1, medians of 20 runs) show 36.8 ms FP8 vs TensorRT FP8 \~44 ms and 23.7 ms NVFP4 vs TensorRT mixed NVFP4 \~40 ms (about 1.2x and 1.7x). Kernels are built with -O3 --use_fast_math; the CUDA toolkit used per row is not stated.

## Use it when

- Closed-loop robot control with Pi0/Pi0.5/GR00T on Jetson AGX Thor: Pi0.5 2-view 44 ms FP8 (27 ms NVFP4) vs 91-95 ms for NVIDIA's TensorRT baseline
- Batch-1 VLA inference on RTX 5090/4090 where per-decision latency matters more than throughput (GR00T N1.6 2-view about 13 ms graph replay)
- You want to skip TensorRT engine builds, per-driver/per-GPU rebuilds and ONNX export; a model change only needs a process restart
- Fixed-architecture realtime workloads it already supports (Qwen3.6-27B NVFP4 single-stream decode, Higgs Audio TTS, Wan2.2/Cosmos video) on Blackwell

## Skip it when

- Multi-user or high-batch serving: one process serves one captured graph, with no continuous batching (the docs point to vLLM/SGLang/TRT-LLM)
- Models it does not ship: each new architecture needs an 800-1500 line hand-written frontend and weight spec, not an automatic import
- When you need FP32/BF16-exact outputs: the fast tiers are FP8/NVFP4 with about 0.998-0.999 action cosine to the reference, and 1-view NVFP4 Pi0.5 misses the project's own 0.995 gate (worst sample 0.971)
- When you need a published number reproduced exactly: open issues report 21.24 ms vs a documented 16.61 ms (GR00T N1.7, RTX 5090, #188) and 25.76 vs 42.8 tok/s (Qwen3.6 on Thor, #153)
- GPUs older than SM80, or Hopper if you need FlashAttention (FA2 is not built for sm90, which falls back to cuBLAS-decomposed attention)

## How it is fast

Each model's whole forward pass (vision encoder, LLM backbone and the 4-step diffusion action head) is written out by hand and captured once as a static CUDA Graph over fixed buffers, so steady-state calls are a graph replay with no Python dispatch. Activations and weights run in static per-tensor FP8 (E4M3), or NVFP4 with AWQ pre-scaling on Blackwell, calibrated on the first call and cached as JSON. Hand-written CUDA kernels fuse the memory-bound steps (residual + RMSNorm + quantize, bias + GELU + quantize, RoPE/QKV split), while GEMMs and attention go to cuBLASLt FP8 with epilogue fusion, CUTLASS and a vendored FlashAttention-2 (FA4 or CUTLASS FMHA on Thor).

## Compared with alternatives

Pick FlashRT for batch-1 robot policy (VLA) inference on Jetson Thor or RTX Blackwell; for LLM serving pick FlashInfer- or ZhiLight-style engines (or vLLM/SGLang), and for general transformer encoders and translation pick FasterTransformer or CTranslate2, which cover many architectures without a hand-written pipeline per model.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | CUDA 12.4+ (12.8+ for Blackwell), PyTorch or pinned JAX 0.5.3, pybind11, CUTLASS v4.4.2 (cloned into third_party), transformers&lt;4.56, safetensors, numpy; vendored FlashAttention-2 v2.7.4.post1 built in; ROCm/hipBLASLt for the separate MI350X backend |
| **Minimum toolchain** | C++17/CUDA C++17, GCC 11+, CMake 3.24+, Python 3.10-3.12; built with -O3 --use_fast_math |
| **Platforms** | NVIDIA SM80+ Linux: Jetson AGX Thor (SM110), RTX 5090 (SM120), DGX Spark (SM121), RTX 4090 (SM89), A100/RTX 3090, Jetson Orin (community port); AMD MI350X (gfx950) via a separate HIP backend |
| **Thread safety** | not documented; one model per process (the Thor troubleshooting table says to subprocess-isolate rather than load several VLA checkpoints in one process) |
| **Drop-in for the baseline** | no |

## Gotchas

- The RTX 5090 figures (GR00T N1.6 13.08 ms, Pi0.5 17.58 ms) are CUDA-graph replay p50 that exclude image normalization, host-device copies and post-processing; Pi0.5 wall-clock p50 is 19.58 ms at 2 views
- GR00T 'T=50' is the action horizon, not the denoising step count; FlashRT's GR00T DiT also runs 4 steps, the same count as NVIDIA's table
- CUDA Graph instantiation on Thor varies by about 2 ms run to run; autotune=3 (default) recaptures, and Pi0.5 NVFP4 needs about 300 warmup calls to settle
- pip install flash-rt ships no compiled kernels; load_model needs an editable install plus a 6-25 minute CMake build with the same Python interpreter; the GR00T base checkpoint emits noise for untrained embodiment slots (use gr1 etc.)

## Known shortcomings

- N1.6 baselines are copied NVIDIA numbers (4 denoising steps; FlashRT rows say T=50, precision unstated); matched-precision N1.7 Thor rows give only about 1.2x (FP8) and 1.7x (NVFP4) over TensorRT.
- RTX 5090 rows (13.08 ms GR00T, 17.58 ms Pi0.5) are CUDA-graph replay only, excluding preprocessing, H2D/D2H and postprocess, yet are set against NVIDIA's end-to-end numbers; open reproduction disputes without maintainer reply (#188: 21.24 vs documented 16.61 ms; #153: 25.76 vs 42.8 tok/s); built with -O3 --use_fast_math; Qwen3-8B baseline is HF eager at 3.6 tok/s (weak). Correction: 'T=50' is the action horizon and FlashRT's DiT also runs 4 denoising steps, so the earlier step-count caveat was wrong.

## Caveats and trade-offs

The doc itself says to compare only rows with matching model, hardware, view count, step count and harness. The N1.6 and Pi0.5 baseline rows are third-party published numbers (NVIDIA GR00T docs, Jetson AI Lab, OpenPI) and were not re-measured; the NVIDIA N1.6 table is for 4 denoising steps while the FlashRT rows are labelled T=50, and their precision is not stated on the row, so the 2.0-2.6x figures may mix precisions and settings. The closest like-for-like rows (GR00T N1.7 on Thor at matched FP8 or NVFP4 precision) show smaller gains of about 1.2x and 1.7x over TensorRT (derived from page data). FP8/NVFP4 FlashRT against BF16 eager or the OpenPI reference adds a precision gap. Repository is new (2026) and all numbers are first-party; the NVIDIA GR00T optimization page could not be opened here (host blocked). [retier] Correction: 'T=50' is the action horizon; FlashRT's DiT also runs 4 denoising steps like NVIDIA's table. RTX 5090 rows are CUDA-graph replay only and exclude pre/postprocessing and transfers.

Model-specific engine (VLA models, some LLMs, video and TTS) with hand-written CUDA/HIP kernels and FP8/NVFP4 quantization; Blackwell and Jetson Thor focus; long first-run initialization (about 6 s on RTX 4090 for groot).

## Maintenance

Very active, young (2026) Apache-2.0 project with frequent releases and community ports (Orin, L40, MI350X), but open, unanswered reproduction disputes (#188, #153) mean you should benchmark it yourself before relying on the headline numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party doc that sets FlashRT's own latencies against baseline numbers published by NVIDIA (Isaac GR00T, Jetson AI Lab) and OpenPI rather than re-measured in one harness; a reproduction script exists for the N1.7 Thor rows (benchmarks/groot_n17_thor_latency.py), but no compiler version or flags are stated for the measured builds.
- **Verifier notes:** All record numbers appear in docs/benchmark_comparison.md. Metadata from github.com: Apache-2.0, 607 stars, 85 forks, not a fork or archived, last commit 2026-09-30; languages about 45% C++, 40% Python, 12% CUDA. The 13.9x Pi0.5 figure is against an unoptimized upstream reference rather than TensorRT.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/flashrt-project/FlashRT/HEAD/docs/benchmark_comparison.md>
  - <https://github.com/flashrt-project/FlashRT>
  - <https://github.com/flashrt-project/FlashRT/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/flashrt-project/FlashRT/HEAD/README.md>
  - <https://raw.githubusercontent.com/flashrt-project/FlashRT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/flashrt-project/FlashRT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flashrt-project/FlashRT/HEAD/docs/benchmark_comparison.md>
  - <https://raw.githubusercontent.com/flashrt-project/FlashRT/HEAD/examples/thor/README.md>
  - <https://raw.githubusercontent.com/flashrt-project/FlashRT/HEAD/examples/blackwell/README.md>
  - <https://raw.githubusercontent.com/flashrt-project/FlashRT/HEAD/docs/inference_engine_differences.md>
  - <https://raw.githubusercontent.com/flashrt-project/FlashRT/HEAD/docs/architecture.md>
  - <https://raw.githubusercontent.com/flashrt-project/FlashRT/HEAD/docs/stable_api.md>
  - <https://raw.githubusercontent.com/flashrt-project/FlashRT/HEAD/docs/kernel_catalog.md>
  - <https://github.com/flashrt-project/FlashRT/issues?q=is%3Aissue>
  - <https://github.com/flashrt-project/FlashRT/issues/188>
  - <https://github.com/flashrt-project/FlashRT/issues/170>
  - <https://github.com/flashrt-project/FlashRT/issues/153>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/flashrt-project/flashrt`) · [data/wave8/enrich/raw/github_com_flashrt_project_flashrt.json](../../../data/wave8/enrich/raw/github_com_flashrt_project_flashrt.json) (enrichment confidence 0.75)

</details>
