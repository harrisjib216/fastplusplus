# ThunderKittens

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `CUDA/C++` · `MIT` · 🟢 active

> Header-only CUDA tile DSL for writing GEMM/attention/SSM kernels that match cuBLAS and FA3 and beat FA3 backward.

| | |
|---|---|
| **Beats** | cuBLAS GEMM and FlashAttention-3 / cuDNN attention |
| **Claimed result** | matches cuBLAS and FlashAttention-3 on GEMM and attention inference; 10-40% faster than FA3 on attention backward; 14x over FLA polynomial linear attention (6.5x learned-map); 7.9x (seq 1024) / 4.7x (seq 4096) over FlashFFTConv; README: \~855 TFLOPs H100 GEMM (\~86% of peak) |
| **Workload** | Header-only C++20/CUDA tile primitives for GEMM, attention forward/backward, linear attention and SSM kernels on H100. |
| **Metric** | throughput |
| **Hardware** | NVIDIA H100 80GB SXM |
| **Compiler and flags** | CUDA 12.6 (paper); flags not stated |
| **Adoption** | 3.7k stars; used by Together AI, Jump Trading, Cursor (per README) |
| **Last commit** | 2026-09-12 |
| **Links** | [repository](https://github.com/HazyResearch/ThunderKittens) · [benchmark](https://proceedings.iclr.cc/paper_files/paper/2025/hash/05dc08730e32441edff52b0fa6caab5f-Abstract-Conference.html) |

## Verdict

On an H100 80GB SXM with CUDA 12.6, the ICLR 2025 paper by the project team shows TK GEMM competitive with cuBLAS, non-causal attention forward matching FlashAttention-3, and attention backward 10-40% faster than FA3 (largest gain at short sequences). It also shows 14x/6.5x over FLA linear attention and 4.7-7.9x over FlashFFTConv. The README's \~855 TFLOPs (86% of peak) H100 bf16 GEMM figure is first-party, and nvcc flags are not stated.

## Use it when

- You write custom fused kernels (attention variants, linear attention, long convolutions, Mamba-style SSMs) on H100/H200 or B200 and want near-cuBLAS/FA3 throughput without hand-writing PTX.
- Attention training workloads where the backward pass dominates: the ICLR 2025 paper reports 10-40% faster backward than FlashAttention-3 at head dim 64/128.
- Non-standard attention or SSM operators where the incumbent is Triton or a research kernel (FLA, FlashFFTConv): the paper reports 6.5-14x over FLA and 4.7-7.9x over FlashFFTConv.
- Low-precision Blackwell GEMMs (MXFP8, NVFP4) in TK 2.0, where the authors report matching or surpassing cuBLAS on B200.

## Skip it when

- You just need a GEMM or standard attention call: cuBLAS and FlashAttention already deliver matching forward performance with a stable API.
- Ampere or older GPUs (Ampere no longer actively supported), AMD (use HipKittens), or Windows builds (open issue #174).
- Toolchains older than CUDA 12.8 or compilers without C++20 concepts.
- You need a packaged, versioned library: since 2.0 there is no Python package, and each kernel under kernels/ is built separately by its own Makefile.

## How it is fast

Everything is expressed as tensor-core-sized tiles whose shared-memory layouts are chosen at compile time to avoid bank conflicts. A Load-Compute-Store-Finish (LCSF) template splits warps into producers (issuing asynchronous TMA loads) and consumers (issuing asynchronous WGMMA on Hopper, tcgen05 on Blackwell) with register reallocation between them, so memory movement overlaps compute. Persistent grids and supergrouped tile ordering improve L2 reuse; later versions add distributed shared memory and NVLink/NVSwitch multi-GPU primitives.

## Compared with alternatives

Choose it over FlashAttention-3 when you need custom attention/SSM variants or faster backward passes and can write CUDA; stay with FlashAttention-3 for a maintained drop-in attention API with forward performance that TK only matches. Unlike CPU siblings such as LIBXSMM or Fastor, it targets NVIDIA datacenter GPUs only.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | CUDA toolkit 12.8+; PyTorch 2.8+ and pybind11 only for the prebuilt kernels/ and demos |
| **Minimum toolchain** | C++20, CUDA 12.8+ (README suggests gcc-11 / clang-11 or newer) |
| **Platforms** | NVIDIA Hopper (SM90) and Blackwell (SM100/103/120), Vera Rubin added Sept 2026; Ampere (SM80) builds but is unsupported |
| **Thread safety** | Not applicable in the host sense; most ops are warp-scoped and calling one from several warps on the same data is undefined behavior per the README |
| **Drop-in for the baseline** | no |

## Gotchas

- Default operation scope is a single warp; assigning multiple warps to the same op is undefined behavior and can corrupt memory. WGMMA ops live in kittens::warpgroup / group&lt;N&gt;.
- Some ops alias-fail silently: transpose_sep must not be given the same registers as source and destination.
- Layouts are checked at compile time; a 'missing' operation is usually a layout mismatch (e.g. mma B operand needs column layout).
- The README says mma unit tests occasionally fail by a single element due to tensor-core floating-point rounding.

## Known shortcomings

- No cuDNN attention comparison found in the paper; wins are on backward passes and non-standard baselines; flags not stated.
- Kernel-writing API, not a drop-in for cuBLAS or FA3; needs CUDA 12.8+ and C++20; Hopper and Blackwell only (no Ampere; Windows issue #174); no Python package since v2.0; B200 'match or beat cuBLAS' claim is chart-only.

## Caveats and trade-offs

Peer-reviewed (ICLR 2025) but authored by the project team; nvcc flags not stated. Matches rather than beats cuBLAS/FA3 on forward; wins are on backward and non-standard baselines (FLA, FlashFFTConv). No cuDNN attention comparison found in the paper. Current repo needs CUDA 12.8+, targets Hopper/Blackwell; Ampere no longer actively supported.

NVIDIA Hopper/Blackwell only (Ampere no longer supported); needs CUDA 12.8+; AMD via separate HipKittens.

## Maintenance

Actively maintained by Stanford Hazy Research (TK 2.0 in Jan 2026, Vera Rubin support Sept 2026, last commit 2026-09-12), MIT-licensed and header-only, so easy to vendor; expect API churn between major versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C-&gt;B: the paper was published at ICLR 2025 (peer-reviewed proceedings page opened) and shows matching cuBLAS/FA3 on forward, 10-40% faster attention backward on H100 with CUDA 12.6; kernel code public but no nvcc flags stated, so not A.
- **Verifier notes:** Repo MIT, 3.7k stars, last commit 2026-09-12 (active), Together AI/Jump Trading/Cursor named in README; all confirmed. Baseline field mentions cuDNN attention, which the paper does not appear to test.
- **Fields the verifier corrected:** `claimed_speedup`, `benchmark_url`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2410.20399>
  - <https://arxiv.org/html/2410.20399>
  - <https://github.com/HazyResearch/ThunderKittens>
  - <https://github.com/HazyResearch/ThunderKittens/commits>
  - <https://proceedings.iclr.cc/paper_files/paper/2025/hash/05dc08730e32441edff52b0fa6caab5f-Abstract-Conference.html>
- **Sources the enricher read:**
  - <https://github.com/HazyResearch/ThunderKittens>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderKittens/HEAD/README.md>
  - <https://arxiv.org/html/2410.20399>
  - <https://github.com/HazyResearch/ThunderKittens/issues>
  - <https://github.com/HazyResearch/ThunderKittens/issues/187>
  - <https://hazyresearch.stanford.edu/blog/2026-02-19-tk-2>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/hazyresearch/thunderkittens`) · [data/wave8/enrich/raw/github_com_hazyresearch_thunderkittens.json](../../../data/wave8/enrich/raw/github_com_hazyresearch_thunderkittens.json) (enrichment confidence 0.75)

</details>
