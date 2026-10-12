# FlashAttention-3 (flash-attention)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `CUDA/C++` · `BSD-3-Clause` · 🟢 active

> Fused exact-attention CUDA kernels (FA2/FA3); FA3 on H100 is 1.5-2x faster than FA2 and beats cuDNN at sequence lengths of 1k and up.

| | |
|---|---|
| **Beats** | NVIDIA cuDNN attention |
| **Claimed result** | FP16 forward up to 740 TFLOPs/s (75% utilization), 1.5-2.0x faster than FlashAttention-2 in the forward pass; outperforms cuDNN for medium/long sequences (&gt;= 1k); FP8 reaches close to 1.2 PFLOPs/s and is competitive with cuDNN, but behind it for hdim 128/256 with causal masking. No single speedup ratio vs cuDNN read. |
| **Workload** | FP16/BF16 and FP8 attention forward pass on H100 SXM5 across sequence lengths and head dims. |
| **Metric** | throughput |
| **Hardware** | NVIDIA H100 SXM5 |
| **Compiler and flags** | Paper: nvcc from CUDA 12.3, CUTLASS 3.5, cuDNN 9.1.1.17, H100 80GB SXM5 at 1830 MHz. hopper/setup.py at tag v2.6.3 (2024-07-25), nvcc: -O3 -std=c++17 -U__CUDA_NO_HALF_OPERATORS__ -U__CUDA_NO_HALF_CONVERSIONS__ -U__CUDA_NO_BFLOAT16_OPERATORS__ -U__CUDA_NO_BFLOAT16_CONVERSIONS__ -U__CUDA_NO_BFLOAT162_OPERATORS__ -U__CUDA_NO_BFLOAT162_CONVERSIONS__ --expt-relaxed-constexpr --expt-extended-lambda --use_fast_math --ptxas-options=--verbose,--register-usage-level=10,--warn-on-local-memory-usage -lineinfo -DCUTLASS_DEBUG_TRACE_LEVEL=0 -DNDEBUG -DQBLKSIZE=128 -DKBLKSIZE=128 -DCTA256 -DDQINRMEM -DEXECMODE=0 -gencode arch=compute_90a,code=sm_90a --threads 4; host C++: -O3 -std=c++17. |
| **Adoption** | 24.8k stars |
| **Last commit** | 2026-07-16 |
| **Links** | [repository](https://github.com/Dao-AILab/flash-attention) · [benchmark](https://arxiv.org/abs/2407.08608) |

## Verdict

The NeurIPS 2024 FA3 paper benchmarks attention forward and backward on an H100 SXM5 against FA2, a Triton implementation and cuDNN: FP16 forward is 1.5-2.0x faster than FA2, reaching up to 740 TFLOPs/s (75% utilization), backward is 1.5-1.75x faster, and it beats cuDNN at sequence lengths of 1k and up. FP8 reaches close to 1.2 PFLOPs/s but trails cuDNN for causal hdim 128/256. Toolchain versions differ between paper versions (CUDA 12.1-12.3, cuDNN 9.x, CUTLASS 3.x), and the comparison harness is hopper/benchmark_attn.py in the repo.

## Use it when

- Training or prefill of transformers on H100/H800 with FP16/BF16 and sequence lengths of 1k or more, where the paper shows FA3 ahead of cuDNN.
- Ampere/Ada/Hopper GPUs (A100, RTX 3090/4090, H100) via FA2 when you need exact attention with linear memory instead of PyTorch's materialized attention.
- Autoregressive decoding with KV cache: flash_attn_with_kvcache does append-to-cache, rotary embedding and split-KV attention in one kernel, with paged-KV support.
- Models needing sliding-window, ALiBi, softcapping, or GQA/MQA attention in a single fused kernel.
- AMD MI200/MI300/MI355 and RDNA3/4 via the Composable Kernel or Triton backends (FA2 only).

## Skip it when

- FP8 causal attention with head dim 128 or 256 on H100: the paper shows cuDNN ahead there.
- Short sequences (under about 1k), where the paper does not show a win over cuDNN; recent cuDNN and PyTorch SDPA ship their own flash-style kernels, so check current versions.
- Turing and older GPUs (only a separate third-party flash-attention-turing repo), CPUs, or Windows builds, which the README calls under-tested.
- Pure C++ inference engines without PyTorch: the shipped interface is a Torch extension, so you would have to lift kernels out of csrc/ and hopper/ yourself.
- Builds on small machines: the README warns that compiling can take about 2 hours without ninja and that ninja can exhaust RAM under 96 GB unless MAX_JOBS is set.

## How it is fast

IO-aware tiling with online softmax keeps Q/K/V blocks in shared memory and registers, so the score matrix never goes to HBM. FA3 adds Hopper features: warp specialization with TMA producer warps and WGMMA consumer warps, ping-pong scheduling so one warpgroup's softmax exponentials overlap another's GEMMs, and an intra-warpgroup two-stage pipeline overlapping softmax with the next GEMM. The FP8 path uses block quantization plus incoherent processing (a random orthogonal transform) to tame outliers, which the paper reports gives 2.6x lower error than baseline per-tensor FP8 attention.

## Compared with alternatives

Pick FlashAttention over ThunderKittens when you want a maintained, pip-installable attention module with KV-cache, varlen, GQA and AMD support; ThunderKittens reports 10-40% faster attention backward than FA3 and is the choice for writing custom Hopper kernels. The CPU siblings (LIBXSMM, MNN, T-MAC, llamafile) do not target GPU attention.

## Integration

| | |
|---|---|
| **Form** | module (PyTorch CUDA extension; pip wheels flash-attn, flash-attn-3 from hopper/, flash-attn-4) |
| **Dependencies** | PyTorch 2.2+, CUDA 12.0+ (FA3: CUDA 12.3+, 12.8 recommended) or ROCm 6.0+, CUTLASS (git submodule), packaging, psutil, ninja |
| **Minimum toolchain** | nvcc compiling C++17 (-O3 --use_fast_math, -gencode arch=compute_90a,code=sm_90a for FA3) |
| **Platforms** | Linux; NVIDIA sm80/sm86/sm89/sm90 (FA2), sm90 H100/H800 only for FA3, Hopper/Blackwell for FA4; AMD CDNA/RDNA via CK or Triton |
| **Thread safety** | not documented (standard CUDA-stream semantics through PyTorch) |
| **Drop-in for the baseline** | partial — replaces cuDNN or PyTorch SDPA attention calls, but with its own tensor layout (batch, seqlen, nheads, headdim) and function signatures, and only via PyTorch |

## Gotchas

- Since v2.1 the causal mask is aligned to the bottom-right corner when seqlen_q != seqlen_k; rows that are fully masked return zeros.
- deterministic=False is the default for backward; an open FA3 issue (#2244) reports dQ still differing between runs with deterministic=True, which others could not reproduce.
- flash_attn_with_kvcache has no backward pass and updates k_cache/v_cache in place; paged blocks must be a multiple of 256.
- FA3 wheels compile a large instantiation matrix (head dims x dtypes x paged/split/softcap); use the FLASH_ATTENTION_DISABLE_\* environment flags to cut build time.

## Known shortcomings

- Search record's 'up to 1.5x faster than cuDNN' not found; paper: faster than cuDNN for seq len &gt;= 1k, FP8 slower than cuDNN with causal masking at head dims 128/256; toolchain versions differ between paper versions.
- README still calls FA3 beta; H100/H800 only; PyTorch-only interface, no standalone C++ API; open issue #2244: deterministic=True backward reportedly non-deterministic dQ (not reproduced by others).

## Caveats and trade-offs

NeurIPS 2024 paper; benchmark script location in repo (benchmarks/, hopper/) not confirmed, so tier B not A. Not uniformly faster than cuDNN (FP8 causal hdim128/256 lags). The 'up to 1.5x vs cuDNN' figure in the original record was not found on the pages read. Toolchain versions differ between paper versions (v2: CUDA 12.2, cuDNN 9.0.0, CUTLASS 3.3). cuDNN has since added its own FA-style kernels, so the gap may have narrowed. [retier] Retier B to A rests on the repo and the setup stated in the paper. The paper PDF itself could not be reopened in this session (arxiv.org, proceedings.neurips.cc and tridao.me are blocked by the egress proxy); the toolchain versions come from the paper text as quoted by the orchestrator, and the cuDNN 9.1.1.17 appendix line was confirmed only through search snippets. arXiv v2 listed CUDA 12.2, cuDNN 9.0.0 and CUTLASS 3.3. By search snippets, the NeurIPS/final version's headline numbers are BF16 up to 840 TFLOPs/s (85% utilization) and FP8 1.3 PFLOPs/s, while v1/v2 gave 740 TFLOPs/s (75%) and about 1.2 PFLOPs/s. The public harness's default configuration differs from the paper's (batch_size fixed at 2, seqlen 1k-32k, hidden 2048; the paper sets batch so total tokens = 16k with seqlen 512-16k), so the figures can only be reproduced after editing the script. No tag marks the exact commit used for the paper figures. The FP8 cuDNN harness (hopper/benchmark_flash_attention_fp8.py) is in HEAD but not at v2.6.3. HEAD's hopper/setup.py now downloads nvcc 12.6.85 plus ptxas 12.8.93 and uses different flags, so current builds do not match the paper's toolchain.

Hopper-only for FA3 path; Python/PyTorch front end with CUDA C++ kernels (CUTLASS-based); GPU-only.

## Maintenance

Actively maintained, very widely used (about 24.8k stars), BSD-3-Clause; FA3 is still labelled a beta release in the README, and new work has moved to the CuTeDSL FA4 package.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Peer-reviewed NeurIPS 2024 paper benchmarks FA3 against cuDNN attention on H100 SXM5: FP16 up to 740 TFLOPs/s and faster than cuDNN for sequence lengths &gt;= 1k; FP8 is behind cuDNN for hdim 128/256 with causal masking. The benchmark script path was not confirmed, so not A.
- **Retiered** B to A: The repo publishes the harness behind the cuDNN comparison: hopper/benchmark_attn.py (public since tag v2.6.3, 2024-07-25, two weeks after arXiv v1) times FlashAttention-2, Triton, cuDNN (cudnn-frontend pygraph SDPA, fwd and bwd) and FA3 and prints TFLOPS. hopper/setup.py publishes the nvcc flags, and the paper names the toolchain (CUDA 12.3, cuDNN 9.1.1.17, CUTLASS 3.5) and the GPU (H100 80GB SXM5 at a fixed 1830 MHz), so code, compiler, flags and GPU are all public.
- **Verifier notes:** arXiv v2 states CUDA 12.2 / cuDNN 9.0.0 / CUTLASS 3.3 at 1830 MHz; the record's CUDA 12.3 / cuDNN 9.1.1.17 / CUTLASS 3.5 may come from v3, which I could not open (HTTP 429), so compiler_and_flags is left uncorrected. The commits page is blocked by robots.txt, so last_commit was not checked.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2407.08608>
  - <https://arxiv.org/html/2407.08608>
  - <https://arxiv.org/html/2407.08608v2>
  - <https://github.com/Dao-AILab/flash-attention>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/README.md>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/hopper/setup.py>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/hopper/benchmark_attn.py>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/benchmarks/benchmark_flash_attention.py>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/hopper/flash_api.cpp>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/LICENSE>
  - <https://arxiv.org/html/2407.08608>
  - <https://tridao.me/blog/2024/flash3/>
  - <https://github.com/Dao-AILab/flash-attention/issues/2244>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/dao-ailab/flash-attention`) · [data/wave8/enrich/raw/github_com_dao_ailab_flash_attention.json](../../../data/wave8/enrich/raw/github_com_dao_ailab_flash_attention.json) (enrichment confidence 0.8)

</details>
