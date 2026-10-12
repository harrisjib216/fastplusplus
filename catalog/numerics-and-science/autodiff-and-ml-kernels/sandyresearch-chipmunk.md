# Chipmunk (column-sparse attention and MLP kernels for diffusion transformers)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `CUDA / Python (Triton ports)` · `MIT` · 🟡 stale

> Training-free dynamic column-sparse attention and MLP kernels for diffusion transformers; about 2.16x end-to-end on HunyuanVideo over torch.compile'd dense.

| | |
|---|---|
| **Beats** | FlashAttention-3 (attention layer) and cuBLAS / torch.compile'd nn.Sequential (MLP layer); torch.compile'd reference repos for end-to-end |
| **Claimed result** | README 'At a glance': Column Sparse Attention layer \~9.3x faster than the FlashAttention3 baseline; Column Sparse MLP layer \~2.5x faster than the cuBLAS baseline (the Benchmarks section says the MLP baseline is torch-compiled nn.Sequential). End-to-end on 1x H100 unless noted: HunyuanVideo 720x1280x129 Chipmunk alone 1030 s -&gt; 477 s (2.16x); Chipmunk + step cache 277 s (3.72x), 412 s on 8x H100 (2.50x); step caching (TeaCache) alone 279 s (3.69x). Wan2.1 Chipmunk + STA 1.56x; Chipmunk-73% + STA + step cache 2.67x (TeaCache alone 2.0x). FLUX.1-dev 768x1280 Chipmunk alone 6.60 s -&gt; 4.90 s (1.41x), Chipmunk + step cache 2.56x; the at-a-glance line says \~1.6x. |
| **Workload** | Dynamic column-sparse attention and MLP layers inside HunyuanVideo, Wan2.1, FLUX.1-dev and Mochi diffusion-transformer inference on H100 GPUs; layer-level and end-to-end video/image generation latency. |
| **Metric** | latency |
| **Hardware** | NVIDIA H100 (1x and 8x), Hopper required for the CUDA kernels; Ampere supported via Triton ports; host CPU not stated |
| **Compiler and flags** | nvcc via torch CUDAExtension (setup.py): -O3 --use_fast_math -std=c++20 -lineinfo -forward-unknown-to-host-compiler -DKITTENS_HOPPER -arch=sm_90a; host C++ -std=c++20 -O3. CUDA Toolkit &gt;= 12.4 (12.8 recommended, conda cuda 12.8.0); baselines torch.compile'd |
| **Adoption** | 114 stars |
| **Last commit** | 2025-09-08 |
| **Links** | [repository](https://github.com/sandyresearch/chipmunk) · [benchmark](https://github.com/sandyresearch/chipmunk) |

## Verdict

First-party README numbers on H100: HunyuanVideo 720x1280x129 at 50 steps drops from 1030 s (torch.compile'd reference repo) to 477 s with Chipmunk alone (2.16x) and to 277 s with step caching (3.72x, vs 3.69x for TeaCache alone); FLUX.1-dev 768x1280 goes from 6.60 s to 4.90 s (1.41x). The layer-level claims (attention 9.3x over FlashAttention-3, MLP 2.5x over torch-compiled nn.Sequential) come from a chart with no stated sparsity level, shapes or script, and the repo's only timing code is commented out and compares against torch SDPA.

## Use it when

- Batch-1 text-to-video or text-to-image DiT inference on H100 (Hopper) where attention dominates, e.g. HunyuanVideo 720x1280x129, where Chipmunk alone cut 1030 s to 477 s
- You already use one of the four integrated models (HunyuanVideo, Wan2.1, FLUX.1-dev, Mochi) and can run the shipped example scripts and configs
- You accept a small, measurable quality change (the README reports VBench, ImageReward, GenEval and CLIP scores per setting) in exchange for latency
- You want to stack sparsity with step caching (TeaCache-style) or sliding-tile attention (STA), which the README combines for 2.5-3.7x end-to-end
- Ampere GPUs, via the Triton ports, if you accept that the README gives no separate Ampere numbers beyond 'comparable E2E generation speedup'

## Skip it when

- You need exact attention or MLP outputs: this is lossy approximate computation, not a drop-in replacement for FlashAttention-3 or cuBLAS
- LLM serving, training, causal attention or head dims other than 128: dense_attn is non-causal with 128-dim heads, and the method relies on the multi-step denoising loop
- Batched generation: SparseDiffMLP asserts input shape (1, N, C) and the static masks are built for batch 1
- You only need the headline 3.7x on HunyuanVideo: step caching alone (TeaCache) reaches 3.69x, so most of that number is not Chipmunk
- Production use needing support: stale since 2025-09-08, open unanswered issues on flickering (Wan 14B I2V on A100) and OOM (Wan2.1-14B on A100 80GB with 120 GB host RAM)

## How it is fast

Activations change slowly across diffusion steps and attention and MLP activations are sparse, so on a dense 'full step' it records each query group's top keys (column sums of attention, via dense_colsum_attn) and a cached output, and on later steps computes only the contribution of those keys/neurons as a delta added to the cache. The sparsity is laid out as [192, 1] column-sparse chunks for attention and [128, 1] for the MLP, so producer warps gather the needed K/V columns into dense shared-memory tiles and the tensor-core GEMMs stay dense; kernels are written in ThunderKittens for Hopper (TMA, cp.async.reduce.bulk for the cache scatter-add). Tokens are reordered into patches or 4x6x8 voxels so neighbouring queries share one sparsity pattern, and dense steps are injected on a schedule to limit drift.

## Compared with alternatives

Pick Chipmunk over FlashAttention-3 or SageAttention only for H100 diffusion-transformer inference where a small quality change is acceptable, since it skips work rather than computing exact (FA3) or quantized-but-dense (SageAttention) attention; for anything else, including LLMs, those two are drop-in and model-agnostic. It is built on ThunderKittens, which remains the choice for dense Hopper kernels.

## Integration

| | |
|---|---|
| **Form** | module (Python package with a torch CUDAExtension built by pip install -e . --no-build-isolation) |
| **Dependencies** | PyTorch &gt;= 2.5, ThunderKittens (git submodule), Triton, flash_attn, CUDA libraries (cuda, cublas, cudart, cudadevrt), plus diffusers, transformers, einops, ray and other packages in requirements.txt |
| **Minimum toolchain** | CUDA Toolkit &gt;= 12.4 (12.8 recommended), nvcc -std=c++20, Python 3.11 in the quickstart; built with -O3 --use_fast_math |
| **Platforms** | NVIDIA Hopper (sm_90a) for the CUDA attention and MLP kernels; other generations (Ampere tested) fall back to Triton ports, with copy_indices, topk_indices and mask_to_indices compiled for all; Linux with conda in the docs |
| **Thread safety** | not documented; configuration is a process-global GLOBAL_CONFIG dict and the static attention masks are module-level singletons, so treat it as one model per process |
| **Drop-in for the baseline** | partial — SparseDiffAttn replaces an F.scaled_dot_product_attention call with the same (q, k, v) signature, but it needs a global config, a LayerCounter per layer and per-step state, and returns approximate outputs |

## Gotchas

- The first one or two generations are slower because of torch.compile cold starts; the README says speedups appear from generation 3
- Pinned-CPU-memory offloading of caches and indices can take up to \~5 minutes at model initialization and can exhaust host RAM (issue #6 needed offloading disabled and a smaller LARGE_BUF_SIZE)
- SparseDiffMLP requires the activation to be a GELU module because the kernel fuses bias, GELU and cache subtraction
- Multi-GPU is supported only for HunyuanVideo, on a separate multigpu branch with its own Dockerfile

## Known shortcomings

- Lossy (approximate sparse attention/MLP). The 3.7x headline is mostly step caching (TeaCache alone gives 3.69x); Chipmunk alone is 2.16x on HunyuanVideo and 1.41x on FLUX. No script for the 9.3x/2.5x per-layer numbers.
- MLP path asserts batch size 1. Open unanswered issues: flicker (#4), OOM (#6). Stale since 2025-09-08.

## Caveats and trade-offs

This is a lossy, approximate method: it caches activations across diffusion steps and recomputes only sparse deltas, so quality scores move (for example HunyuanVideo VBench total 83.24 -&gt; 82.94). The headline 3.7x on HunyuanVideo is almost all step caching: TeaCache alone reaches 3.69x and Chipmunk + step cache 3.72x. Chipmunk's own contribution is 2.16x on HunyuanVideo and 1.41x on FLUX. The 9.3x attention and 2.5x MLP layer speedups compare sparse kernels against dense baselines at sparsity levels the README does not give. No microbenchmark script for them is in the repo; the only timing code is commented out and targets torch SDPA, not FA3. Only workshop papers back it (ES-FoMo at ICML 2025, YPS at MLSys 2025). It is not a drop-in exact kernel replacement, the CUDA kernels need Hopper (Triton ports cover Ampere), and host CPU is not stated.

Approximate and training-free: it skips attention and MLP work by dynamic sparsity (column-sparse deltas against cached activations), so outputs differ from dense baselines (README reports VBench quality scores); Hopper-only CUDA kernels plus Triton ports; needs per-model integration; PyTorch-based.

## Maintenance

Stale (last commit 2025-09-08) research code from Together AI, Hazy Research and Sandy Research; MIT-licensed so the kernels can be copied, but expect to own the integration and the open quality and memory issues yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party layer speedups (9.3x vs FlashAttention3, 2.5x vs cuBLAS / torch-compiled nn.Sequential, also in assets/images/speed.png) and end-to-end latency tables against torch.compile'd reference repos on H100. No script behind the layer microbenchmarks is in the repo: src/chipmunk/tests/test_csp_attn.py has only commented-out do_bench timing against torch SDPA. Sparsity level, shapes and host CPU are not given for the layer numbers. The papers are workshop papers (ES-FoMo at ICML 2025, YPS at MLSys 2025), not proceedings, so C.
- **Verifier notes:** README numbers match the record. The record's 'nvcc flags not stated' was wrong: setup.py gives them. Recordable shortcoming: the headline end-to-end gain mostly comes from step caching (TeaCache alone 3.69x vs Chipmunk + cache 3.72x), and the method is lossy. Metadata on github.com: MIT, 114 stars, 3 forks, not a fork, 246 commits, last commit 2025-09-08 (stale is right, just over 12 months).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/README.md>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/csrc/README.md>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/setup.py>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/src/chipmunk/tests/test_csp_attn.py>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/assets/images/speed.png>
  - <https://github.com/sandyresearch/chipmunk>
  - <https://github.com/sandyresearch/chipmunk/commits>
  - <https://github.com/sandyresearch/chipmunk/tree/master/src/chipmunk>
  - <https://github.com/sandyresearch/chipmunk/tree/master/src/chipmunk/tests>
- **Sources the enricher read:**
  - <https://github.com/sandyresearch/chipmunk>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/README.md>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/csrc/README.md>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/setup.py>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/examples/YOUR-MODEL-HERE/README.md>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/examples/hunyuan/README.md>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/examples/hunyuan/chipmunk-config.yml>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/examples/flux/README.md>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/src/chipmunk/modules/attn.py>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/src/chipmunk/modules/__init__.py>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/src/chipmunk/modules/mlp.py>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/src/chipmunk/ops/__init__.py>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/src/chipmunk/util/config.py>
  - <https://raw.githubusercontent.com/sandyresearch/chipmunk/HEAD/src/chipmunk/tests/test_csp_attn.py>
  - <https://github.com/sandyresearch/chipmunk/tree/master/src/chipmunk>
  - <https://github.com/sandyresearch/chipmunk/tree/master/src/chipmunk/triton>
  - <https://github.com/sandyresearch/chipmunk/issues?q=is%3Aissue>
  - <https://github.com/sandyresearch/chipmunk/issues/4>
  - <https://github.com/sandyresearch/chipmunk/issues/5>
  - <https://github.com/sandyresearch/chipmunk/issues/6>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sandyresearch/chipmunk`) · [data/wave8/enrich/raw/github_com_sandyresearch_chipmunk.json](../../../data/wave8/enrich/raw/github_com_sandyresearch_chipmunk.json) (enrichment confidence 0.75)

</details>
