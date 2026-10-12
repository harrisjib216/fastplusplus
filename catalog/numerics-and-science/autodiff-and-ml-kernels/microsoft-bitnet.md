# BitNet (bitnet.cpp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> llama.cpp-based CPU inference engine with ternary-weight kernels; 1.4-6.2x faster than llama.cpp FP16 on BitNet b1.58 models.

| | |
|---|---|
| **Beats** | llama.cpp FP16 inference |
| **Claimed result** | 'speedups of 1.37x to 5.07x on ARM CPUs' (energy -55.4% to -70.0%) and '2.37x to 6.17x on x86 CPUs' (energy -71.9% to -82.2%) vs llama.cpp fp16; 100B BitNet b1.58 model at 5-7 tokens/s on one CPU |
| **Workload** | Ternary (1.58-bit) LLM CPU inference with I2_S, TL1, TL2 kernels versus llama.cpp FP16. |
| **Metric** | throughput |
| **Hardware** | Apple M2 Ultra (Mac Studio, 64GB) for ARM; Intel Core i7-13700H (Surface Laptop Studio 2, 64GB) for x86 (per technical report arXiv 2410.16144) |
| **Adoption** | 40.3k stars |
| **Last commit** | 2026-07-27 |
| **Links** | [repository](https://github.com/microsoft/BitNet) · [benchmark](https://arxiv.org/html/2410.16144v2) |

## Verdict

Microsoft's own technical report (arXiv 2410.16144) measured end-to-end token generation of ternary BitNet-style models at 125M-100B parameters against llama.cpp FP16 on an Apple M2 Ultra (1.37-5.07x) and an Intel Core i7-13700H (2.37-6.17x), best of 2-thread and all-thread runs, with energy cut 55-82%; compiler and flags are not given. The baseline mixes weight compression with kernel speed, since FP16 moves \~8x more weight bytes.

## Use it when

- Running BitNet b1.58-2B-4T, Falcon3/Falcon-E 1.58-bit, Llama3-8B-1.58 or other ternary-trained models on laptop/desktop/server CPUs.
- Memory-bandwidth-bound token generation where weight size dominates, especially larger models (the report's gains grow with model size; 100B ternary model at 5-7 tok/s claimed).
- Energy-constrained edge inference on Apple Silicon or recent x86 (report: 55-82% less energy than llama.cpp FP16).
- CPU embedding workloads with the BitNet-embedding 0.6B/270M models on x86 (README: 1.3-2.3x prefill over F16).

## Skip it when

- Ordinary FP16/INT4 models: it gives no benefit unless weights were trained ternary; Microsoft itself points to T-MAC for general low-bit models.
- Comparing against quantized llama.cpp: the headline 6x is vs FP16 weights; against llama.cpp TQ1_0 the companion paper (arXiv 2502.11880) reports only up to 1.33x (x86) / 1.65x (M2).
- Prompt-heavy workloads: the system paper says prefilling is not addressed by its optimizations (later README updates add GEMM work, but the headline numbers are decode).
- Projects that need a stable embeddable C/C++ API or current upstream llama.cpp features: it pins an older llama.cpp fork.
- Kernel coverage gaps: TL1 is ARM-only, TL2 x86-only, and embedding models have no ARM kernels per the README support table.

## How it is fast

Weights are ternary, so they pack to \~2 bits (I2_S: offline 2-bit packing, unpacked in-register for an int8-activation dot product) or below (TL1: two weights -&gt; 4-bit index into a 9-entry precomputed activation lookup table; TL2: three weights -&gt; 5-bit sign+index, 1/6 smaller than TL1), cutting memory traffic that dominates CPU token generation. The LUT method comes from T-MAC; the 2026 update adds activation-parallel I2_S GEMM/GEMV with tunable row/column tiling (include/gemm-config.h) and optional Q6_K embedding quantization.

## Compared with alternatives

Pick bitnet.cpp over T-MAC when the model is ternary BitNet b1.58 (its TL2/I2_S kernels beat T-MAC by up to 2.32x on x86 per its paper and are lossless); pick T-MAC, llamafile tinyBLAS or Intel Neural Speed for general 2-8-bit or FP16 models where ternary weights are not available.

## Integration

| | |
|---|---|
| **Form** | built application (CMake) driven by Python scripts; vendored llama.cpp/ggml fork |
| **Dependencies** | Python 3.10+ (conversion scripts, requirements.txt), CMake 3.22+, Clang 18+, vendored llama.cpp submodule; Hugging Face models |
| **Minimum toolchain** | Clang 18+ (Visual Studio 2022 with the LLVM toolset on Windows), CMake 3.22 |
| **Platforms** | x86-64 and ARM64 (NEON, incl. Apple Silicon); separate CUDA GPU kernel in gpu/ |
| **Thread safety** | not documented (inherits llama.cpp's per-context model) |
| **Drop-in for the baseline** | partial — same GGUF/llama.cpp CLI workflow, but needs ternary models converted to its own I2_S/TL1/TL2 formats |

## Gotchas

- Builds of the vendored llama.cpp fail on newer compilers due to missing #include &lt;chrono&gt; (issue #334, README FAQ Q1); patch the four files or pin the compiler.
- A third-party test on a pre-AVX2 Xeon E3-1230 v2 hit garbled output (repeated '!' tokens) from a tokenization mismatch in the official pre-converted GGUF and a stack-overflow crash.
- Reported speedups take the best of 2-thread and unrestricted-thread runs; tune threads and gemm-config.h block sizes for your CPU.
- Kernel choice matters: I2_S suits many threads, TL1 limited threads with large models, TL2 memory/bandwidth-limited setups.

## Known shortcomings

- Speedup compares ternary weights against fp16 weights, mixing quantization with kernel gains; Microsoft's own measurements; flags not stated.
- Own paper (arXiv 2502.11880): only up to 1.33x x86 / 1.65x M2 vs llama.cpp's ternary TQ1_0, up to 2.32x vs T-MAC; prefill not covered; only helps ternary-trained models; pins an old llama.cpp fork that fails on newer compilers (issue #334); outside test on pre-AVX2 Xeon got garbled output and a stack overflow.

## Caveats and trade-offs

Baseline is llama.cpp fp16 on full-precision weights vs ternary weights, so the speedup mixes quantization with kernel gains. First-party (Microsoft) report; compiler and flags not stated; best of 2-thread and unrestricted-thread runs reported. Newer README items claim 1.42-2.28x over F16 prefill for embedding models.

Requires ternary-trained models; built on llama.cpp infrastructure.

## Maintenance

Active (last commit July 2026, frequent model/kernel releases), MIT-licensed and widely used (40k+ stars), but first-party evidence only and tied to an older llama.cpp fork.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README quotes the speedup ranges verbatim; the first-party technical report (arXiv 2410.16144) names llama.cpp fp16 as baseline and the CPUs, but no compiler/flags, so C.
- **Verifier notes:** Numbers and metadata (MIT, 40.3k stars, last commit 2026-07-27) confirmed; filled in baseline precision and CPU models from the technical report.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/microsoft/BitNet>
  - <https://github.com/microsoft/BitNet/commits>
  - <https://raw.githubusercontent.com/microsoft/BitNet/HEAD/README.md>
  - <https://arxiv.org/abs/2410.16144>
  - <https://arxiv.org/html/2410.16144>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/microsoft/BitNet/HEAD/README.md>
  - <https://raw.githubusercontent.com/microsoft/BitNet/HEAD/src/README.md>
  - <https://arxiv.org/html/2410.16144v2>
  - <https://arxiv.org/abs/2502.11880>
  - <https://arxiv.org/html/2502.11880>
  - <https://github.com/microsoft/BitNet/issues/334>
  - <https://github.com/pantalipe/cpu-llm-bench>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/microsoft/bitnet`) · [data/wave8/enrich/raw/github_com_microsoft_bitnet.json](../../../data/wave8/enrich/raw/github_com_microsoft_bitnet.json) (enrichment confidence 0.75)

</details>
