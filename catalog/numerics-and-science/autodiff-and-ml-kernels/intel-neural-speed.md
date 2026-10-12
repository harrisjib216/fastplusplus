# Intel Neural Speed / LLM Runtime

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Archived Intel llama.cpp-style CPU LLM runtime with low-bit weight-only GEMM kernels; \~1.2-1.4x faster INT4 next-token latency than ggml on Xeon.

| | |
|---|---|
| **Beats** | ggml-based (llama.cpp) INT4 |
| **Claimed result** | Paper Table 3: GPT-J 6B 19.98 ms (LLM Runtime, group size 128) vs 31.62 ms (ggml-based, group size 32); the 1.6x headline compares LLM Runtime gs128 to ggml gs32. At equal group size 32: 22.99 vs 31.62 ms, \~1.38x (derived from page data); Llama-2 7B 23.4 vs 27.71 ms, GPT-NeoX 20B 80.16 vs 92.36 ms. README claims up to 40x vs llama.cpp (not verified). |
| **Workload** | INT4 LLM inference next-token latency on 4th Gen Xeon (GPT-J 6B, Llama-2 7B, GPT-NeoX 20B) with AVX2/AVX512/VNNI/AMX kernels. |
| **Metric** | latency |
| **Hardware** | 4th Gen Intel Xeon Scalable, single socket |
| **Adoption** | 352 stars |
| **Links** | [repository](https://github.com/intel/neural-speed) · [benchmark](https://arxiv.org/abs/2311.00502) |

## Verdict

The Intel NeurIPS 2023 workshop paper (arXiv 2311.00502) reports next-token latency for INT4 models on an unspecified 4th Gen Xeon Scalable cloud instance (input/output 32 tokens). At equal group size 32 it beats a ggml-based baseline: GPT-J-6B 22.99 vs 31.62 ms, Llama-2-7B 23.4 vs 27.71 ms, GPT-NeoX-20B 80.16 vs 92.36 ms. Group size 128 brings GPT-J to 19.98 ms. No compiler flags, core count or llama.cpp version are given.

## Use it when

- Single-stream INT4 LLM decoding on Intel Xeon (Sapphire/Emerald Rapids with AMX_INT8, or Ice Lake/Cascade Lake with AVX512_VNNI) where you control the build and pin threads with numactl.
- Reading or borrowing BesTLA's JIT weight-only-quantized GEMM kernels for your own x86 inference engine (Apache-2.0, header-only plus Xbyak).
- Experimenting with group size 128 or per-channel int4/int3 instead of llama.cpp Q4_0-style group 32, which the project recommends for speed with similar accuracy (validated on Llama-2-7B per its docs).
- Hybrid client CPUs (12th Gen and later) where its own thread pool is claimed to beat OpenMP.

## Skip it when

- Anything needing maintenance or security fixes: Intel archived the repo on 2024-08-30 and accepts no patches; it points users to Intel Extension for PyTorch.
- Non-Intel or non-x86 CPUs: kernels are x86-only (BesTLA is described as an x64 library); AMD support is not documented and ARM is not supported.
- Models or GGUF quant types released after mid-2024: model support is frozen at v1.0 (March 2024).
- Accuracy-sensitive int1-int3 RTN quantization: docs warn of accuracy loss; int7-asym and int8 can overflow on AVX2-without-VNNI or AVX512BW compute paths.
- If you need an independently reproduced speedup: all numbers are Intel's own, with no published compiler flags or exact CPU SKU in the paper.

## How it is fast

BesTLA is a CUTLASS-style template library (Launcher / Parallel / GemmCore / Prologue / Epilogue) whose micro-kernels are generated at runtime with Xbyak for AVX2, AVX_VNNI, AVX512F/BW/VNNI, AVX512_FP16, AMX_BF16 and AMX_INT8. Weights are group-wise quantized (int1-int8, fp4, nf4, fp8) and activations are dynamically quantized per batch/per K-group to int8 so the dot products run on VNNI/AMX integer units, with fused epilogues (GELU, SWISH etc.) and an L2-cache-blocked parallel split. At graph level it fuses QKV, FFN and multi-head attention and pre-allocates the KV cache instead of reallocating it per token.

## Compared with alternatives

Choose it over llamafile's tinyBLAS when you're on AMX/VNNI Xeons and want integer-unit int4 kernels instead of F16/Q8_0 prompt-eval speedups. Choose it over T-MAC/BitNet when you run ordinary int4 group-quantized models rather than 1-2 bit lookup-table or ternary models. Because it is archived, BesTLA is mainly worth mining for kernel ideas; for a maintained runtime, prefer the siblings.

## Integration

| | |
|---|---|
| **Form** | shared lib (Python package neural-speed); BesTLA alone is header-only |
| **Dependencies** | Xbyak (fetched by CMake), OpenMP (default thread pool), Python toolchain for conversion/quantization scripts; optional Intel Extension for Transformers for HF-style API |
| **Minimum toolchain** | GCC 10+ for Neural Speed (README); BesTLA: GCC 9+ / MSVC 1900+ / oneAPI 2024.0+, GCC 11+ recommended; CMake 3.12+ |
| **Platforms** | x86-64 Intel CPUs (AVX2 minimum; AVX512/VNNI/AMX paths), Linux and Windows |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — reads GGUF models produced by llama.cpp, but uses its own scripts, binary format (ne-\*.bin) and Python API, not llama.cpp's C API |

## Gotchas

- The paper's 1.6x headline compares Neural Speed at group size 128 with ggml at group size 32; like-for-like group 32 is 22.99 vs 31.62 ms on GPT-J (\~1.38x) and 23.4 vs 27.71 ms on Llama-2-7B (\~1.18x) (derived from page data).
- The README's 'up to 40x vs llama.cpp' links to an Oct 2023 Medium post whose text states only 'up to 7.27x' on a Core i9-12900 (input 1024, output 32); the 40x figure is not stated in that text.
- AVX512, VNNI and AMX are OFF by default in the CMake options (NS_AVX512, NS_AVX512_VNNI, NS_AMX); build flags determine which kernels you get.
- AMX_INT8 wants group sizes aligned to 128 for best efficiency.

## Known shortcomings

- 1.6x headline compares group size 128 against ggml group size 32; at equal group size \~1.2-1.4x; archived 2024-08-30; vendor numbers with no compiler flags.
- README's 'up to 40x vs llama.cpp' links to an Oct 2023 Medium post that states only 'up to 7.27x' (Core i9-12900); AVX512, VNNI and AMX off by default in CMake options.

## Caveats and trade-offs

Repo archived 2024-08-30; Intel no longer maintains it (README points to Intel Extension for PyTorch). Paper code link is intel-extension-for-transformers. First-party Intel numbers; compiler flags and exact CPU SKU not stated. The 1.6x headline mixes group sizes (LLM Runtime gs128 vs ggml gs32); like-for-like gs32 gains are \~1.2-1.4x. Baseline llama.cpp/ggml is not a listed incumbent.

Intel-CPU focused (AVX/AMX); repo archived.

## Maintenance

Abandoned: archived by Intel 2024-08-30 (last release v1.0, March 2024); Apache-2.0, so BesTLA can still be vendored, but nobody upstream will fix bugs or add models.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Intel-authored arXiv paper (first-party) Table 3 gives next-token latency vs a ggml-based solution on 4th Gen Xeon, with no compiler/flags, exact CPU model or benchmark code path; C.
- **Verifier notes:** Metadata matches (Apache-2.0, 352 stars, archived 2024-08-30). The 1.6x headline compares different quantization group sizes, which is worth recording as a shortcoming.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2311.00502>
  - <https://arxiv.org/html/2311.00502>
  - <https://github.com/intel/neural-speed>
- **Sources the enricher read:**
  - <https://github.com/intel/neural-speed>
  - <https://raw.githubusercontent.com/intel/neural-speed/HEAD/README.md>
  - <https://raw.githubusercontent.com/intel/neural-speed/HEAD/neural_speed/core/README.md>
  - <https://raw.githubusercontent.com/intel/neural-speed/HEAD/bestla/README.md>
  - <https://raw.githubusercontent.com/intel/neural-speed/HEAD/bestla/CMakeLists.txt>
  - <https://raw.githubusercontent.com/intel/neural-speed/HEAD/CMakeLists.txt>
  - <https://arxiv.org/html/2311.00502>
  - <https://medium.com/@NeuralCompressor/llm-performance-of-intel-extension-for-transformers-f7d061556176>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/intel/neural-speed`) · [data/wave8/enrich/raw/github_com_intel_neural_speed.json](../../../data/wave8/enrich/raw/github_com_intel_neural_speed.json) (enrichment confidence 0.7)

</details>
