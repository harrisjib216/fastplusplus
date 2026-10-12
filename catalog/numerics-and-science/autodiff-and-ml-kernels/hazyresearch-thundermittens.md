# ThunderMittens

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++ (Metal Shading Language) with Python/MLX bindings` · `no license` · 🟡 stale

> Metal port of the ThunderKittens tile DSL for Apple GPUs; its bf16 GEMM is about 9% faster than MLX's mx.matmul.

| | |
|---|---|
| **Beats** | MLX mx.fast.scaled_dot_product_attention and mx.matmul (Apple's MLX Metal kernels) |
| **Claimed result** | Hazy Research blog post 'ThunderMittens For Your ThunderKittens' (WebSearch snippet only; page egress-blocked): the attention kernel is 'within +-15% of MLX's implementation' (not a clear win) and the GEMM is '\~9% faster on most sizes' than MLX's matmul. The repo stores no results; time_gemm.py and time_attn.py print GFLOPS for 'mlx' and 'tk' side by side. |
| **Workload** | The repo's time_attn.py times a forward attention kernel (bf16, head dim 64 and 128, batch 16, 16 heads, sequence 512 to 2560) against mx.fast.scaled_dot_product_attention, and time_gemm.py times a bf16 square GEMM (1024 to 16384) against mx.matmul, both reported as GFLOPS. |
| **Metric** | throughput |
| **Hardware** | Apple M2 Pro per blog snippets (the post describes the M2 Pro's \~200 GB/s bandwidth and \~6.5 TFLOPs); the repo does not name the chip, and the snippets do not show whether every timing ran on it. |
| **Compiler and flags** | Not stated. Xcode (Metal compiler) for the MSL path, or CMake C++17 with nanobind against MLX for the Python path (kernels/CMakeLists.txt); no optimization flags beyond those defaults. |
| **Adoption** | 24 stars, 7 forks; Metal sibling of the ThunderKittens (HazyResearch) kernel DSL |
| **Last commit** | 2025-08-26 |
| **Links** | [repository](https://github.com/HazyResearch/ThunderMittens) · [benchmark](https://hazyresearch.stanford.edu/blog/2024-11-28-tk-mlx) |

## Verdict

First-party only, read as a WebSearch snippet because the Hazy Research blog is egress-blocked: on an Apple M2 Pro, the bf16 GEMM is about 9% faster than mx.matmul on most square sizes, and the forward attention kernel is within +-15% of mx.fast.scaled_dot_product_attention (B=16, H=16, N 512 to 2560, D 64/128 in time_attn.py). The repo stores no results, and both kernels are built with MLX's default Metal compilation, with no extra flags.

## Use it when

- Learning or porting ThunderKittens-style tile kernels to Apple Silicon (M-series GPUs) through Metal
- Experimenting with a custom bf16 square GEMM inside MLX where every dimension is a multiple of 32 (time_gemm.py sweeps 1024 to 16384)
- Prototyping fused Metal kernels for MLX with tile primitives instead of hand-written simdgroup_matrix code (the blog says the GEMM is 11 lines against MLX's 100+)
- Non-causal, unmasked bf16 forward attention with head dim 64 or 128 and equal Q/K/V shapes, for inference experiments

## Skip it when

- Any shipped product: the repo has no license file for its own code (only the vendored MLX tree is MIT), so legally it is reference-only
- Attention speed: the first-party claim is only 'within +-15%' of mx.fast.scaled_dot_product_attention, so it is not a reliable win
- Training or autodiff: there is no backward kernel, and the JVP transform in attn_fwd.cpp is a commented-out template stub
- Causal or masked attention, GQA/MQA (Q, K and V must share one shape), head dims other than 64/128, or FP16/FP32 attention
- CPU fallback or ragged shapes: eval_cpu ends in assert(false), and sequence lengths and GEMM sizes that are not tile multiples have no tail handling

## How it is fast

The base tile shrinks from ThunderKittens' 16x16 to 8x8 so tiles map directly onto Metal's simdgroup_matrix multiply-accumulate; per the blog snippet this was needed because the M2 Pro allows at most 128 registers per thread. Each threadgroup is one 32-thread SIMD group. The GEMM computes a 32x32 output tile from 32x16 and 16x32 register tiles with FP32 accumulators, reads straight from device memory with no threadgroup-memory staging, and fully unrolls the K loop. The attention kernel is FlashAttention-style: online softmax over 8-row query tiles, with Q pre-scaled by 1/sqrt(D)\*log2(e) so it can use exp2.

## Compared with alternatives

Pick it over ThunderKittens (CUDA) or HipKittens (AMD) only when the target is an Apple GPU and you want the same tile programming model there. Effort (bucketMul) is the other Apple Silicon entry but does approximate matrix-vector products for LLM decoding, not exact GEMM or attention.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | MLX built from the vendored ThunderMittens/mlx tree (requirements: mlx&gt;=0.18.1), nanobind 2.2.0, CMake, setuptools; Xcode for the standalone MSL path |
| **Minimum toolchain** | C++17, CMake 3.27 (kernels/CMakeLists.txt), Python 3.8+, Xcode Command Line Tools |
| **Platforms** | macOS on Apple Silicon (Metal GPU only); the blog's numbers are from an M2 Pro |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — attn_fwd and matmul_custom are separate MLX ops with their own names; attn_fwd takes no scale, mask or causal argument and applies a fixed 1/sqrt(D) scale, so existing mx.fast.scaled_dot_product_attention or mx.matmul calls must be rewritten and shape-padded |

## Gotchas

- Shape and dtype checks are plain assert() calls (N a multiple of 8 for attention; GEMM M/N multiples of 32 and K a multiple of 16), which disappear in release builds, so wrong shapes can produce silent garbage or out-of-bounds reads.
- matmul_custom accepts float16 in its host-side check, but the float16 Metal instantiation is commented out; only float32 and bfloat16 kernels exist.
- time_attn.py warms up MLX's SDPA instead of the ThunderMittens kernel and passes scale=1 to MLX while the TK kernel scales by 1/sqrt(D); neither timing script checks correctness, and each iteration calls mx.eval, so launch overhead is included.
- The repository vanished and was restored on 2025-08-26 (two 'revive thundermittens' commits; ThunderKittens issue #132), so there is no history, issue tracker activity or tests to lean on.

## Known shortcomings

- Raised D to C on the Hazy Research blog (domain-restricted snippet only: GEMM about 9% faster than MLX, attention within +-15%). No license, 24 stars, last commit 2025-08-26, stale.
- Shape checks are assert() only (compiled out in release builds, no tail handling); attn_fwd uses a fixed 1/sqrt(D) scale while time_attn.py passes scale=1 to MLX, so the attention comparison is not like for like; float16 matmul passes the host check but its Metal kernel is commented out; no backward kernel; eval_cpu ends in assert(false); no license.

## Caveats and trade-offs

Numbers are snippet only from the first-party blog post (hazyresearch.stanford.edu was egress-blocked), so the tier is no higher than C. The gain is modest: GEMM \~9% over mx.matmul, and attention is only on par (+-15%) with mx.fast.scaled_dot_product_attention. The repo has no LICENSE file of its own (only the vendored MLX tree is MIT), so the ThunderMittens code is reference-only. The repo history is two commits, both 'revive thundermittens' on 2025-08-26, after the repository had disappeared (ThunderKittens issue #132). Benchmark quirks in time_attn.py: the 'tk' warmup loop calls MLX's SDPA instead of the ThunderMittens kernel, scale=1 is passed to MLX SDPA while the TK kernel takes no scale, each iteration calls mx.eval (launch overhead included), and correctness is not checked. time_gemm.py warms up both kernels correctly. 24 stars, but the ThunderKittens README lists it as the Apple Silicon sibling of ThunderKittens and HipKittens.

Metal Shading Language port of the ThunderKittens tile abstractions: Apple GPUs only, MLX integration through a vendored copy of MLX (ThunderMittens/mlx, MIT, Copyright Apple Inc.). The attention kernel (kernels/attn_fwd/attn_fwd.metal) is bf16 only with head dim 64 or 128 (static_assert) and forward only; the GEMM is a custom bf16 matmul. Early research code with a small kernel set.

## Maintenance

Stale (two restore commits on 2025-08-26, 24 stars) and unlicensed, so it is reference code for reading and re-implementing, not for vendoring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D to C. The first-party Hazy Research blog post (hazyresearch.stanford.edu/blog/2024-11-28-tk-mlx, egress-blocked, seen through a WebSearch snippet restricted to that domain) says the attention kernel is 'within +-15% of MLX' and the GEMM is '\~9% faster on most sizes'. The repo carries the matching timing scripts (ThunderMittens/kernels/time_gemm.py, time_attn.py), but there are no stored results and compiler, flags and chip are not stated in the repo.
- **Verifier notes:** Upgraded D to C on a first-party blog claim seen as a domain-restricted WebSearch snippet (GEMM \~9% faster than MLX; attention within +-15%). The record is otherwise accurate: no license, stale (last commit 2025-08-26), 24 stars and 7 forks.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/HazyResearch/ThunderMittens>
  - <https://github.com/HazyResearch/ThunderMittens/commits>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/README.md>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/ThunderMittens/kernels/time_attn.py>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/ThunderMittens/kernels/time_gemm.py>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderKittens/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/HazyResearch/ThunderMittens>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/README.md>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/ThunderMittens/kernels/time_attn.py>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/ThunderMittens/kernels/time_gemm.py>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/ThunderMittens/kernels/CMakeLists.txt>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/ThunderMittens/kernels/setup.py>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/ThunderMittens/kernels/requirements.txt>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/ThunderMittens/kernels/attn_fwd/attn_fwd.metal>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/ThunderMittens/kernels/attn_fwd/attn_fwd.cpp>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/ThunderMittens/kernels/matmul_custom/matmul_custom.metal>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderMittens/HEAD/ThunderMittens/kernels/matmul_custom/matmul_custom.cpp>
  - <https://raw.githubusercontent.com/HazyResearch/ThunderKittens/HEAD/README.md>
  - <https://github.com/philipturner/metal-flash-attention>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/hazyresearch/thundermittens`) · [data/wave8/enrich/raw/github_com_hazyresearch_thundermittens.json](../../../data/wave8/enrich/raw/github_com_hazyresearch_thundermittens.json) (enrichment confidence 0.6)

</details>
