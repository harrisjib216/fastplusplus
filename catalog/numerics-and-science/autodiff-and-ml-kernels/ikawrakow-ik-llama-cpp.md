# ik_llama.cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> llama.cpp fork with rewritten CPU quantized-matmul kernels; 1.1-7x faster CPU prompt processing than mainline on the same GGUF.

| | |
|---|---|
| **Beats** | llama.cpp (mainline ggml CPU kernels) |
| **Claimed result** | Jan 2025 wiki page, same quantized model in both engines, pp512 tokens/s llama.cpp vs ik_llama.cpp: Zen4 (Ryzen 7950X) from 1.783x (Q4_0, 146.20 vs 260.71) to 5.179x (IQ3_S, 28.96 vs 149.98), geometric mean 2.883x; AVX2 (Ryzen 5975WX) from 1.524x (Q8_0) to 5.125x (IQ3_S, 44.88 vs 230.03); ARM NEON (M2-Max) from 1.085x (Q4_0, 114.44 vs 124.13) to 7.025x (IQ3_S, 11.34 vs 79.66), geometric mean 3.350x. Discussion 8 (Aug 2024) also gives same-quant rows (llama.cpp vs the fork's own i-quants, ratios derived from page data): 8B IQ3_S AVX2 pp512 28.04 vs 96.28 (3.43x), tg128 6.80 vs 7.62 (1.12x); 8B IQ2_XS AVX2 pp512 46.45 vs 125.46 (2.70x), tg128 10.88 vs 12.07 (1.11x); 7B IQ3_S NEON pp512 12.08 vs 49.72 (4.12x), tg128 10.32 vs 11.11 (1.08x). |
| **Workload** | llama-bench pp512 (512-token prompt processing, CPU only, no BLAS, no Flash Attention) on LLaMA-3.1-8B-Instruct, with the same llama.cpp-quantized GGUF run in both engines (ik_llama.cpp with run-time repacking -rtr) across 17 types (F16, BF16, Q8_0, Q4_0, Q5_0, Q2_K-Q6_K, IQ2_XXS-IQ4_NL) on Zen4 (Ryzen 7950X), AVX2 (Ryzen 5975WX) and ARM NEON (M2-Max). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X (Zen4, AVX-512 path); AMD Ryzen Threadripper PRO 5975WX (AVX2 path); Apple M2 Max (NEON) |
| **Adoption** | 3.3k stars, 470 forks |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/ikawrakow/ik_llama.cpp) · [benchmark](https://github.com/ikawrakow/ik_llama.cpp/wiki/Jan-2025:-prompt-processing-performance-comparison) |

## Verdict

The author's January 2025 llama-bench run (ik_llama.cpp 3c5f8722 vs llama.cpp 9f7add1c, same llama.cpp-quantized LLaMA-3.1-8B-Instruct GGUF, CPU only, no BLAS, no flash attention, -rtr on the fork) measured pp512 speedups of 1.78-5.18x on a Ryzen 7950X (Zen4/AVX-512), 1.52-5.13x on a Ryzen 5975WX (AVX2) and 1.09-7.03x on an M2-Max (NEON) across 15-17 quant types; it is first-party, compilers and flags are not stated, and only prompt processing was tabulated.

## Use it when

- CPU-only or CPU-heavy LLM inference where prompt processing (prefill) dominates: same-GGUF pp512 on LLaMA-3.1-8B was 1.8-5.2x mainline on Zen4 (geometric mean 2.88x) and 1.1-7.0x on M2-Max NEON (3.35x)
- i-quant and k-quant models (IQ2_XXS-IQ4_XS, Q3_K-Q6_K), where the gap was largest (IQ3_S 5.2x Zen4, 7.0x NEON)
- AVX-512 CPUs (Zen4, Sapphire Rapids+), whose VNNI/VBMI paths mainline used little at the time of the comparison
- Large MoE models such as DeepSeek, GLM or Kimi with experts left in system RAM and attention on a CUDA GPU, using tensor overrides, FlashMLA and fused MoE ops
- You want lower-bpw-at-equal-quality IQ\*_K / IQ\*_KT quantizations that mainline does not have

## Skip it when

- Token generation bound by memory bandwidth: same-format TG gains in Discussion 8 were only about 1.08-1.12x
- GPU backends other than CUDA Turing+: the README says ROCm, Vulkan, Metal, older NVIDIA GPUs and AVX-only CPUs are not supported and related issues will not be fixed
- You need upstream llama.cpp's newest features, models or APIs exactly: the fork diverged in August 2024 and ports models itself
- Interoperability: GGUFs made with ik-only quant types do not load in mainline, and Unsloth _XL models containing f16 tensors are likely not to work
- Exposed or untrusted network deployments, especially the RPC backend: there is no SECURITY.md and no published advisories, and an RPC deserialize_tensor bounds-check crash (#2164) is open

## How it is fast

The CPU hot path is the iqk GEMM code (ggml/src/iqk/iqk_gemm_\*.cpp), which multiplies several weight rows against several activation columns per kernel call, with activations quantized to 8-bit and integer dot products (AVX512-VNNI/AVX-VNNI vpdpbusd, NEON dot). Weights can be repacked at load time (-rtr) into row-interleaved layouts (4 or 8 rows), and quants that are slow to unpack (i-quants, k-quants) are expanded a few rows at a time to Q8_0_R8 and fed to one tuned Q8_0_R8 x Q8_2_X4 GEMM (PR 515: IQ2_XXS from about 107 to 288 t/s on a Ryzen 7950X). Its IQ\*_K types use small non-linear lookup tables (4-32 int8 values) held in SIMD registers via pshufb/vqtbl1q, so dequantization costs about the same as a linear format.

## Compared with alternatives

Pick ik_llama.cpp over llamafile's tinyBLAS when you run i-quants or k-quants (tinyBLAS mainly speeds up F16/Q8_0 prefill), and over T-MAC or BitNet unless the model is 1-2 bit or ternary, where their lookup-table kernels are built for it; PowerInfer targets sparse-activation GPU-CPU offload of specific models, while ik_llama.cpp is a general GGUF engine.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none for the CPU build (cmake + compiler; libcurl optional); CUDA toolkit for GPU; vendored cpp-httplib, nlohmann/json, stb-image, miniaudio for the server and multimodal tools |
| **Minimum toolchain** | CMake 3.14; the top-level CMakeLists sets C++20 (docs/build.md says a C++17 compiler); GCC, Clang, or MSVC/clang-cl on Windows |
| **Platforms** | x86-64 with AVX2 or better (AVX-512 path needs VNNI/VL/BW/DQ), aarch64 NEON (Linux, macOS, Android/termux), NVIDIA CUDA Turing or newer; Windows and Linux |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — same CLI tools and llama.h-style API frozen at the August 2024 fork point, and most mainline GGUFs load; ik-only quant types and newer mainline API additions are not interchangeable |

## Gotchas

- On Zen4 / Sapphire Rapids, a plain Release build without -DGGML_NATIVE=ON or the GGML_AVX512_\* options silently falls back to the AVX2 kernels; HAVE_FANCY_SIMD needs AVX512F, VNNI, VL, BW and DQ all defined at compile time
- -rtr (run-time repacking) is needed for the published speedups, but with hybrid CPU/GPU MoE it forces matmuls on repacked RAM tensors onto the CPU (k-quants have no CUDA row-interleaved kernels), which lowers prompt speed
- Split mode 'graph' with partial GPU offload can produce gibberish; the README workaround is -cuda graphs=0
- The Jan 2025 comparison used mainline build 4517 and states mainline's ARM Q4_0/IQ4_NL repacking had already closed most of the gap for those types (1.09x and 1.24x); re-measure against current mainline before switching for those formats

## Known shortcomings

- Claim overstated: Discussion 8's 'iqk' column compares new IQ2_K/IQ3_K quant types against llama.cpp IQ2_XS/IQ3_S, not same-quant kernels; same-quant gain is 3.43x pp and 1.12x tg; benchmark_url switched to the Jan 2025 wiki page (same GGUF in both: pp512 1.08-7.03x, geomeans 2.88x Zen4 and 3.35x NEON); fork of llama.cpp.
- No SECURITY.md or advisories; RPC deserialize_tensor bounds crash open (#2164); last upstream sync Aug 2024; a Zen4 build without GGML_NATIVE/AVX512 flags silently uses AVX2; CMakeLists sets C++20 but docs say C++17; hardware: 7950X is the Zen4/AVX-512 path and the AVX2 box is a Ryzen 5975WX.

## Caveats and trade-offs

The record's original figures (6.45x, 4.61x, 4.19x and so on) come from Discussion 8, where the 'iqk' column is ik_llama.cpp's new IQ2_K/IQ3_K quantization types set against llama.cpp's IQ2_XS/IQ3_S at similar bpw and accuracy, so those ratios mix a format change with kernel speed. The 'this repo' column is the fork running the same IQ2_XS/IQ3_S quants, which is the same-format comparison. The Jan 2025 wiki covers prompt processing only (token-generation gains in Discussion 8 are about 1.1x for same-format quants), and mainline llama.cpp has changed since build 4517, so today's ratios may differ. ik_llama.cpp uses run-time repacking (-rtr) for these runs. Compiler and flags are not stated. The README itself gives no numbers. Fork upstream was originally github.com/ggerganov/llama.cpp, now ggml-org/llama.cpp.

Fork last synced with upstream in August 2024, so it lacks newer mainline features and models unless ported; adds its own quantization types (some GGUF files from other tools, e.g. Unsloth _XL, do not work); only the CPU (AVX2 or better, NEON or better) and CUDA (Turing or newer) backends are performant, ROCm/Vulkan/Metal are not supported; gains are mostly in prompt processing (compute bound), token generation is memory-bandwidth bound and close to mainline.

## Maintenance

Very active (last commit 2026-10-01, 3.3k stars), MIT-licensed, single-maintainer-led fork with a large contributor community; it diverges further from mainline over time, so treat it as a separate engine rather than a patch set.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party llama-bench comparisons with named CPUs and builds; the Jan 2025 wiki page gives the exact script and commits (ik_llama.cpp 3c5f8722, llama.cpp 9f7add1c) and runs the same quantized model in both, but no compiler or flags are stated, so not A. The claim is downgraded because the record's Discussion 8 ratios compare different quantization types, not the same model.
- **Verifier notes:** The record's numbers do appear in Discussion 8, but they are labelled as kernel speedups on the same IQ2_XS/IQ3_S models when the iqk column is really a different quant type (the discussion says so before the table). benchmark_url is switched to the README-linked Jan 2025 wiki comparison, which runs the same GGUF in both engines. Metadata from github.com: MIT, 3.3k stars, 470 forks, not archived, last commit 2026-10-01.
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `claimed_speedup`, `caveats`, `hardware`
- **Pages the verifier opened:**
  - <https://github.com/ikawrakow/ik_llama.cpp/discussions/8>
  - <https://github.com/ikawrakow/ik_llama.cpp>
  - <https://github.com/ikawrakow/ik_llama.cpp/commits>
  - <https://raw.githubusercontent.com/ikawrakow/ik_llama.cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/ikawrakow/ik_llama.cpp/HEAD/LICENSE>
  - <https://github.com/ikawrakow/ik_llama.cpp/wiki>
  - <https://github.com/ikawrakow/ik_llama.cpp/wiki/Jan-2025:-prompt-processing-performance-comparison>
  - <https://raw.githubusercontent.com/wiki/ikawrakow/ik_llama.cpp/Jan-2025:-prompt-processing-performance-comparison.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ikawrakow/ik_llama.cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/ikawrakow/ik_llama.cpp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ikawrakow/ik_llama.cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ikawrakow/ik_llama.cpp/HEAD/docs/build.md>
  - <https://raw.githubusercontent.com/wiki/ikawrakow/ik_llama.cpp/Jan-2025:-prompt-processing-performance-comparison.md>
  - <https://github.com/ikawrakow/ik_llama.cpp/discussions/8>
  - <https://github.com/ikawrakow/ik_llama.cpp/pull/515>
  - <https://github.com/ikawrakow/ik_llama.cpp/issues?q=is%3Aissue+security+OR+CVE+OR+overflow+OR+vulnerability>
  - <https://github.com/ikawrakow/ik_llama.cpp/issues/2164>
  - <https://github.com/ikawrakow/ik_llama.cpp/security>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ikawrakow/ik_llama.cpp`) · [data/wave8/enrich/raw/github_com_ikawrakow_ik_llama_cpp.json](../../../data/wave8/enrich/raw/github_com_ikawrakow_ik_llama_cpp.json) (enrichment confidence 0.8)

</details>
