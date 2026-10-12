# metal-flash-attention

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Swift` · `MIT` · 🟡 stale

> Swift/Metal port of FlashAttention for Apple GPUs; claims higher ALU utilization than FlashAttention-2/3 on NVIDIA, not wall-clock wins.

| | |
|---|---|
| **Beats** | Dao-AILab FlashAttention-2 (A100) and FlashAttention-3 (H100), compared by utilization percentage, not wall time |
| **Claimed result** | No wall-clock ratio against any other library. README: a consistent 4400 gigainstructions per second on M1 Max (83% ALU utilization) at infinite sequence length and head dimension with BF16 emulation. Forward utilization on M1 architecture 86% (D=64), 85% (D=128), 86% (D=256); forward + backward 62%, 63%, 64%. M3 architecture forward 94%, 91%, 82%; forward + backward 71%, 69%, 61%. Quoted comparison tables: A100 Flash2 FP16 forward + backward 56% (D=64), 65% (D=128), 0% (D=256, no result reported); H100 Flash3 FP16 forward + backward 48%, 59%, 0%. README claims 'Apple hardware is training transformers faster than Nvidia hardware doing the same work' after normalizing for GPU size and utilization. |
| **Workload** | Single-headed attention forward, backward dQ and backward dK/dV kernels in FP16 on Apple GPUs (M1 Max, M4, M3 architecture) at head dimensions D = 64, 128, 256, measured as gigainstructions per second and ALU utilization against a hardware roofline. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max (roofline 10616 GFLOPS, 5308 gigainstructions/s), M4 (3580 GFLOPS); NVIDIA A100 SXM and H100 SXM figures are taken from the FlashAttention papers, not re-measured. |
| **Compiler and flags** | swift build/test with -Xswiftc -Ounchecked (README); Metal kernels are JIT compiled at runtime. |
| **Adoption** | 612 stars; a Draw Things blog post and the derived mps-flash-attention project build on it |
| **Last commit** | 2024-09-22 |
| **Links** | [repository](https://github.com/philipturner/metal-flash-attention) · [benchmark](https://github.com/philipturner/metal-flash-attention) |

## Verdict

First-party README figures only: FP16 ALU utilization on Apple GPUs (M1 architecture forward 85-86%, fwd+bwd 62-64%; M3 architecture forward 82-94%, fwd+bwd 61-71% at D = 64/128/256; 4400 gigainstructions/s, 83%, on M1 Max at large sizes), computed with the author's own work model, set beside A100 FlashAttention-2 and H100 FlashAttention-3 utilization derived from the papers' peak GFLOPS. No same-machine timing against MPS, MLX or PyTorch exists, and the 'faster than Nvidia' sentence refers to utilization normalized for GPU size, not wall time.

## Use it when

- Native Swift/Metal apps on macOS 14+ or iOS 17+ that need attention on Apple silicon and can integrate Metal command encoding directly.
- Training-style workloads that need the backward pass on Apple GPUs; the README reports 62-64% (M1 architecture) and 61-71% (M3 architecture) fwd+bwd ALU utilization at D = 64, 128 and 256.
- Large or odd head dimensions (e.g. 256, or non-power-of-two values), where the D-blocking and register-spilling scheme is designed to keep utilization flat.
- As a reference implementation to port or extend (masks, multi-head, block sparsity) for an Apple-GPU inference engine.

## Skip it when

- You need multi-head attention, causal or padding masks, or a PyTorch/Python API out of the box: none are in this repo; the third-party fork imperatormk/metal-flash-attention and its mps-flash-attention bindings add causal masking, macOS 15 fixes and PyTorch MPS integration (issue #32, unanswered).
- You need a measured speedup against MPS, MLX or PyTorch SDPA on the same Mac: the README compares only utilization percentages against NVIDIA GPUs from the FlashAttention papers, so no wall-clock win is documented.
- Standalone GEMM: users reported its GEMM slower than MPS on M3 (issue #11) and a 4096x4096 GEMM taking about 1 s versus about 0.06 s for MPSMatrixMultiplication on M2 (issue #29, user measurement, cause not established); both issues were closed without a maintainer answer.
- Projects that need an actively maintained dependency: last author commit 2024-08-27, last commit 2024-09-22 (README PR), and recent issues get no replies.

## How it is fast

It implements the FlashAttention tiling with online softmax, so the N x N attention matrix is never written to memory. Because Apple GPUs lack native FP32 atomics, the backward pass is split into separate dQ and dK/dV kernels (7 GEMMs instead of 5, (9D+15)N^2 work instead of (7D+10)N^2) that need no atomics or scratch space and parallelize fully across rows and columns. For large head dimensions it adds a third blocking dimension along D with deliberate, bandwidth-minimizing register spilling, and picks block sizes and register-cached operands from per-architecture parameter tables (M1/M2 vs M3/M4 'apple9' family, which also switches between async load and async cache paths).

## Compared with alternatives

Pick it over ThunderMittens when you need a backward pass or large head dimensions on Apple GPUs from Swift, since ThunderMittens' evidence is a forward attention kernel compared with MLX; on NVIDIA use FlashAttention-3 or SageAttention instead, as this project only runs on Metal.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none beyond Apple's Metal framework (Swift package with no package dependencies) |
| **Minimum toolchain** | Swift tools 5.10; build with -Xswiftc -Ounchecked; macOS 14, iOS 17, tvOS 17, visionOS 1 |
| **Platforms** | Apple silicon GPUs only (Metal); parameter tables tuned for M1/M2 and M3/M4 families |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Every kernel is JIT-compiled at runtime from generated Metal source, so first use of each problem configuration pays shader compilation latency; the older precompiled-metallib version (Xcode 14.2) was replaced by this design.
- Default mixed precision keeps Q/K/V in FP16 and stores dO, D and the gradients dV/dK/dQ in BF16 (emulated on chips without native BF16); source comments report output errors around 5e-2 in typical mixed-precision runs and up to 4e-2 BF16 error when gradients are paged to memory.
- Issue #8 reported NaNs on SSD-1B because the softmax scale is applied after Q\*K^T and the product overflows FP16; the current pseudocode still applies scaleFactor after S = Q\*K^T, so test with large-magnitude activations.
- Performance needs -Ounchecked for the CPU-side Swift; the README says plain Release mode is impractical for development because it recompiles everything.

## Known shortcomings

- Tier C: the only comparison is ALU utilization against FlashAttention-2 (A100) and FlashAttention-3 (H100) figures taken from their papers, not a wall-clock run on the same machine; no MLX, MPS or PyTorch comparison exists. Last commit 2024-09-22, stale.
- Single-head only, no masks, Swift/Metal only. Issue #8 FP16 overflow (scale applied after Q\*K^T) looks unchanged in the current pseudocode. Users report its GEMM slower than MPS (issues #11 and #29: about 1 s vs 0.06 s at 4096^2 on an M2). Stale, recent issues unanswered.

## Caveats and trade-offs

The only comparison is ALU utilization against FlashAttention-2 (A100) and FlashAttention-3 (H100) on different hardware, using the author's own gigainstruction metric; the NVIDIA side is the highest GFLOPS from each paper graph divided by 312000 (A100 SXM) or 989000 (H100 SXM), and D=256 backward entries are 0% because no result was reported. It is not a speed comparison and cannot show Apple hardware is faster in wall time; the README's 'faster than Nvidia hardware' sentence is normalized for GPU size. MFA's backward pass issues more work (7 GEMMs instead of 5), which the utilization figures partly account for via a 7/9 factor. The listed baselines (oneDNN, cuDNN, XNNPACK, Eigen tensor) and MLX/MPS/PyTorch MPS attention are not compared in the README. The derived project imperatormk/mps-flash-attention claims 1.1-4x over PyTorch SDPA on Apple Silicon; that is not evidence for this repo. Last commit 2024-09-22 (a README docs PR); last author commit 2024-08-27.

Single-headed attention only (no multi-head, masks or block sparsity yet). Backward pass avoids FP32 atomics by using 7 GEMMs instead of 5 (9D+15 versus 7D+10 work per N^2), which uses less memory than the official backward pass but more compute. Intentional register spilling with a third blocking dimension along D for large head dimensions. Needs Apple silicon and Swift/Metal; JIT compiles shaders at runtime. Not a drop-in C++ or Python library.

## Maintenance

Stale since 2024-09 with unanswered issues and a third-party fork carrying fixes, but MIT-licensed and small enough to copy into an Xcode project as the README intends.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README carries first-party utilization tables (M1 forward 86/85/86%, fwd+bwd 62/63/64%; M3 forward 94/91/82%, fwd+bwd 71/69/61%; 4400 gigainstructions/s at 83% on M1 Max) and compares them with A100 FlashAttention-2 and H100 FlashAttention-3 utilization converted from the papers' best GFLOPS; there is no same-hardware wall-clock run against any baseline and no stated benchmark harness command or Xcode/macOS version beyond -Ounchecked, so C.
- **Verifier notes:** README numbers match the record exactly (raw README fetched). Metadata confirmed on github.com: MIT, 612 stars, 42 forks, not archived, not a fork, last commit 2024-09-22, so stale is correct.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/philipturner/metal-flash-attention/HEAD/README.md>
  - <https://raw.githubusercontent.com/philipturner/metal-flash-attention/HEAD/LICENSE>
  - <https://github.com/philipturner/metal-flash-attention>
  - <https://github.com/philipturner/metal-flash-attention/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/philipturner/metal-flash-attention/HEAD/README.md>
  - <https://raw.githubusercontent.com/philipturner/metal-flash-attention/HEAD/Package.swift>
  - <https://github.com/philipturner/metal-flash-attention/issues?q=is%3Aissue>
  - <https://github.com/philipturner/metal-flash-attention/issues/8>
  - <https://github.com/philipturner/metal-flash-attention/issues/11>
  - <https://github.com/philipturner/metal-flash-attention/issues/17>
  - <https://github.com/philipturner/metal-flash-attention/issues/29>
  - <https://github.com/philipturner/metal-flash-attention/issues/32>
  - <https://github.com/philipturner/metal-flash-attention/tree/main/Sources/FlashAttention>
  - <https://github.com/philipturner/metal-flash-attention/tree/main/Sources/FlashAttention/Attention>
  - <https://github.com/philipturner/metal-flash-attention/tree/main/Sources/FlashAttention/Attention/AttentionDescriptor>
  - <https://github.com/philipturner/metal-flash-attention/tree/main/Tests/FlashAttentionTests>
  - <https://raw.githubusercontent.com/philipturner/metal-flash-attention/HEAD/Sources/FlashAttention/Attention/AttentionDescriptor/AttentionDescriptor.swift>
  - <https://raw.githubusercontent.com/philipturner/metal-flash-attention/HEAD/Sources/FlashAttention/Attention/AttentionDescriptor/AttentionDescriptor+Precisions.swift>
  - <https://raw.githubusercontent.com/philipturner/metal-flash-attention/HEAD/Sources/FlashAttention/Attention/AttentionDescriptor/AttentionDescriptor+Parameters.swift>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/philipturner/metal-flash-attention`) · [data/wave8/enrich/raw/github_com_philipturner_metal_flash_attention.json](../../../data/wave8/enrich/raw/github_com_philipturner_metal_flash_attention.json) (enrichment confidence 0.75)

</details>
