# Mini-Attention (FlashAttention-2 from scratch in CUDA C++ for SM120)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++ (CUDA/PTX)` · `no license` · 🟢 active

> Hand-written FlashAttention-2 forward kernel for RTX 5090 (SM120); beats cuDNN SDPA at N&lt;=1024, 3-5% slower beyond.

| | |
|---|---|
| **Beats** | cuDNN fused attention via PyTorch SDPA (SDPBackend.CUDNN_ATTENTION) |
| **Claimed result** | K7 vs cuDNN latency: N=512 0.185 ms vs 0.247 ms (133.2% of cuDNN throughput); N=1024 0.658 vs 0.739 ms (112.2%); N=2048 2.588 vs 2.515 ms (97.2%); N=4096 5.201 vs 4.945 ms (95.1%); N=8192 10.310 vs 9.904 ms (96.1%). README headline: 'K7 beats cuDNN by 12-35% at N&lt;=1024; reaches 97-100% of cuDNN at N&gt;=2048'. |
| **Workload** | FP16 attention forward (non-causal), H=16, D=128, N=512..8192 with batch 16/16/16/8/4 per _bench_sm120.py (5 warm-up runs, mean of 20 timed runs with a 200 MB L2 flush, CUDA events). Kernel progression percentages are 100\*cuDNN_ms/kernel_ms. The script that printed the README's millisecond table is not in the repo, so its shape is assumed to match. |
| **Metric** | latency |
| **Hardware** | NVIDIA RTX 5090 (SM120 Blackwell, 419 TFLOPS FP16 peak, 1792 GB/s); host CPU not stated |
| **Compiler and flags** | nvcc via torch.utils.cpp_extension.load with -std=c++20 --use_fast_math --expt-relaxed-constexpr -gencode arch=compute_120,code=sm_120 -gencode arch=compute_90,code=compute_90 -O3 (from _bench_sm120.py); CUDA/nvcc version not stated |
| **Adoption** | 1 star |
| **Last commit** | 2026-03-31 |
| **Links** | [repository](https://github.com/shlokgpu/Mini-Attention) · [benchmark](https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/Readme.md) |

## Verdict

On one RTX 5090, fp16 non-causal attention with H=16, D=128 and batch 16/16/16/8/4 for N=512/1024/2048/4096/8192 (5 warm-ups, mean of 20 CUDA-event timings with a 200 MB L2 flush), K7 took 0.185 vs 0.247 ms for cuDNN through PyTorch SDPA at N=512 (1.33x) and 0.658 vs 0.739 ms at N=1024 (1.12x), but 2.588 vs 2.515 ms at N=2048 and 10.310 vs 9.904 ms at N=8192 (about 213 vs 222 TFLOPS, derived from page data). The exact PyTorch, cuDNN and CUDA versions and the host CPU are not stated beyond the torch&gt;=2.11.0 cu128 requirement.

## Use it when

- Studying how to write a FlashAttention-2 forward kernel by hand for consumer Blackwell (RTX 5090, SM120), with each optimization isolated in K1-K7.
- Short-sequence, non-causal fp16 prefill-style attention with head dim 128 (N=512 to 1024) on an RTX 5090, where the README measures 1.12x to 1.33x over cuDNN via PyTorch SDPA.
- As a reference for SM120 tile-size and PTX choices (mma.sync instead of WGMMA, Bc=128, L2::256B hints) when tuning your own kernel.

## Skip it when

- Sequences of 2048 tokens or more: the README table shows K7 at 95-97% of cuDNN there, so cuDNN is faster.
- Causal or masked attention, dropout, training (no backward pass), GQA/MQA with different K/V head counts, head dims other than 128, or sequence lengths that are not multiples of the 64/128 tile sizes; the SM120 kernel rejects or does not implement these.
- Any code you plan to ship: there is no LICENSE file (it returns 404), so the code cannot be copied, and the project has 1 star and one author.
- Datacenter Blackwell (B200/SM100) or Hopper: the SM100 kernel is work in progress and FlashAttention-3 or cuDNN target those parts directly.

## How it is fast

Standard FlashAttention-2 tiling with an online softmax in registers, using Ampere-style mma.sync.m16n8k16 tensor-core instructions (consumer Blackwell has no WGMMA or tcgen05), ldmatrix.x4(.trans) fragment loads, XOR-swizzled shared memory to avoid bank conflicts, cp.async.cg global-to-shared copies with an L2::256B prefetch hint, eager first K/V tile load and optional double buffering. SM120 tuning uses Bc=128 tiles (fits within about 100 KB shared memory), exp2-based softmax and one hoisted reciprocal for the final 1/l normalization, with K7 picked by a static scan over Br/Bc/warp configs.

## Compared with alternatives

Pick it over learn-cuda's SM120 attention only for N&lt;=1024 non-causal d=128 forward on an RTX 5090, since learn-cuda reaches about 94% of speed-of-light at long sequences but does not beat cuDNN; for anything production use cuDNN via SDPA or FlashAttention, and SageAttention if quantized attention is acceptable.

## Integration

| | |
|---|---|
| **Form** | source-drop (PyTorch C++/CUDA extension compiled at runtime via torch.utils.cpp_extension.load) |
| **Dependencies** | PyTorch (libtorch and pybind11 through the extension; pyproject requires torch&gt;=2.11.0, cu128 builds for SM120) and the CUDA toolkit; the repo's pyproject also lists triton, vllm, transformers, numpy and matplotlib for the wider experiments |
| **Minimum toolchain** | nvcc with -std=c++20 and sm_120 code generation (CUDA 12.8+ per setup.sh for SM120); Python 3.11+ |
| **Platforms** | NVIDIA SM120 (RTX 5090) for the benchmarked kernel; the extension refuses GPUs below SM80; separate SM86 kernels exist; SM100 is WIP; run instructions use Linux/WSL paths |
| **Thread safety** | not documented; launches on the current PyTorch CUDA stream |
| **Drop-in for the baseline** | partial — covers only non-causal forward attention with fp16/bf16, head dim 128, contiguous [B, N, H, D] inputs (SDPA uses [B, H, N, D]), equal Q/K/V shapes and N a multiple of the tile size |

## Gotchas

- tests/test_correctness.py (the 'All K1-K7 passed' output in the Readme, tolerance 1e-3) loads the SM86 inline kernels, not the SM120 kernel that was benchmarked; the SM120 kernel is only checked inside _bench_sm120.py at B=4, N=1024 with a 0.05 tolerance.
- The baseline timing wraps each call in a 'with sdpa_kernel(...)' context manager inside the CUDA-event window, so Python-side overhead is charged to cuDNN at sub-millisecond sizes where K7 wins; the probe also silently falls back to FLASH_ATTENTION or MATH if cuDNN is unavailable.
- Several Readme figures disagree or are implausible: K7 at N=1024 is 112.2% in the latency table, 114.4% in the progression table and 'beats by \~35%' in the NCU section; the torch.profiler line (0.003 ms) is physically impossible; and the 'NCU-equivalent' metrics come from an analytical script, not Nsight Compute.
- Design notes contradict the code in places, for example notes/why_mma_sync.md cites 228 KB shared memory per block on SM120 while the bench script says 100 KB per SM.

## Known shortcomings

- README contradicts itself (133.2% vs 134.7%; 'beats \~35%' at N=1024 vs 112.2%). One profiler line (0.003 ms) is physically impossible (\~2,900 TFLOPS vs 419 peak), so at least one measurement is wrong. Beats cuDNN SDPA only at N&lt;=1024. No licence.
- tests/test_correctness.py checks the SM86 inline kernels, not the benchmarked SM120 kernel, which is checked only in the bench script at 0.05 tolerance. The baseline timing counts the `with sdpa_kernel()` context manager inside the CUDA-event window, inflating cuDNN at short N where this kernel wins. Non-causal, d=128, forward only.

## Caveats and trade-offs

Wins only at short sequences (N&lt;=1024) and is 3-5% slower than cuDNN from N=2048 up. The Readme contradicts itself: the latency table gives K7/cuDNN 133.2% and 112.2% at N=512/1024 while the progression table gives 134.7% and 114.4% (and 99.8% vs 97.2% at N=2048); the NCU section says K7 'beats by \~35%' at N=1024 against 112.2% in the table; the progression legend says both 'lower = faster' and '&gt;100% = faster' (the script computes 100\*cuDNN/kernel, so higher is faster); and the torch.profiler line (0.003 ms for B=1 H=16 N=1024 D=128) is physically impossible on an RTX 5090, about 2,900 TFLOPS against a 419 TFLOPS peak (derived from page data). The 'NCU-equivalent' metrics come from an analytical script, not an Nsight Compute run. The baseline is PyTorch SDPA under sdpa_kernel(), timed per call including Python dispatch, and the script silently falls back to FLASH_ATTENTION or MATH if the cuDNN probe fails. CUDA, cuDNN and PyTorch versions and the host CPU are not stated. No license file, so the code must not be copied. First-party, 1 star, 59 commits, recent history from March 2026.

FP16 forward only, head dim 128 kernels, consumer Blackwell (SM120) and SM86 ports; hand-tuned PTX (mma.sync, ldmatrix, cp.async) in CUDA C++; benchmarks driven from Python and PyTorch; SM100/B200 kernel is work in progress.

## Maintenance

Active as of the last commit on 2026-03-31 (59 commits, 1 star), but unlicensed, so treat it as reference reading rather than vendorable code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The Readme latency table (cuDNN vs K7 ms and K7/cuDNN %) matches the record; the harness is public (kernels/flash_attn/cuda/sm_120/_bench_sm120.py, CUDA-event timing with an L2 flush, nvcc flags listed) and the GPU is named. The CUDA, cuDNN and PyTorch versions and the host CPU are not stated, so first-party C (same as earlier GPU precedents), not A.
- **Verifier notes:** Numbers verified on the Readme; metadata confirmed on github.com (no license, 1 star, not a fork, last commit 2026-03-31, so active). The Readme PR links point at ShlokVFX/Mini-Attention, an earlier owner name; the repo page at shlokgpu did not redirect. Shortcoming worth recording: several internally inconsistent or impossible figures (profiler 0.003 ms, \~35% vs 12%), so treat the headline cautiously.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/Readme.md>
  - <https://github.com/shlokgpu/Mini-Attention>
  - <https://github.com/shlokgpu/Mini-Attention/commits>
  - <https://github.com/shlokgpu/Mini-Attention/tree/main/kernels/flash_attn>
  - <https://github.com/shlokgpu/Mini-Attention/tree/main/kernels/flash_attn/cuda>
  - <https://github.com/shlokgpu/Mini-Attention/tree/main/kernels/flash_attn/cuda/sm_120>
  - <https://github.com/shlokgpu/Mini-Attention/tree/main/experiments>
  - <https://github.com/shlokgpu/Mini-Attention/tree/main/tests>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/kernels/flash_attn/cuda/sm_120/_bench_sm120.py>
- **Sources the enricher read:**
  - <https://github.com/shlokgpu/Mini-Attention>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/kernels/flash_attn/cuda/sm_120/_bench_sm120.py>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/kernels/flash_attn/cuda/sm_120/kernel/flash_attention.cu>
  - <https://github.com/shlokgpu/Mini-Attention/tree/main/kernels/flash_attn/cuda/sm_120/kernel/include>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/kernels/flash_attn/cuda/sm_120/kernel/include/ptx_functions.cuh>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/kernels/flash_attn/cuda/sm_120/kernel/include/flash_attention.cuh>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/kernels/flash_attn/cuda/sm_120/kernel/include/flash_kernels.cuh>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/kernels/flash_attn/cuda/sm_120/kernel/include/cuda_utils.cuh>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/kernels/flash_attn/cuda/sm_120/kernel/include/softmax.cuh>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/kernels/flash_attn/cuda/sm_120/kernel/include/forward_kernel.cuh>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/notes/why_mma_sync.md>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/notes/pipeline_design.md>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/tests/test_correctness.py>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/setup.sh>
  - <https://raw.githubusercontent.com/shlokgpu/Mini-Attention/HEAD/LICENSE>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/shlokgpu/mini-attention`) · [data/wave8/enrich/raw/github_com_shlokgpu_mini_attention.json](../../../data/wave8/enrich/raw/github_com_shlokgpu_mini_attention.json) (enrichment confidence 0.7)

</details>
