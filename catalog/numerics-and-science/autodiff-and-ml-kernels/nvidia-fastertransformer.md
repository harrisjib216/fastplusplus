# FasterTransformer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> NVIDIA's discontinued CUDA C++ transformer inference library; beats TensorFlow XLA and TorchScript FP16 BERT on T4, mostly via INT8.

| | |
|---|---|
| **Beats** | TensorFlow XLA (FP16) and PyTorch TorchScript (FP16) for the BERT encoder; TensorFlow and PyTorch decoder and beam-search implementations for translation decoding |
| **Claimed result** | README (T4, FP16 baselines): BERT base vs TensorFlow XLA about 3x for small batch and sequence, about 5x for large ones with Effective FasterTransformer plus INT8-v2; vs PyTorch TorchScript 4x to 6x small, about 5x large. Translation decoding vs TensorFlow: FT-Decoder 1.5x to 3x, FT-Decoding 4x to 18x; vs PyTorch: 1.2x to 3x and 3.8x to 13x. docs/bert_guide.md T4 tables: same-precision FP16 FT vs TF XLA 1.28x to 3.04x (EFF-FT 1.33x to 3.29x); FP16 FT vs TorchScript 1.52x to 6.41x (EFF-FT 2.44x to 3.78x); EFF-FT INT8-v2 vs TF-FP16 up to 5.53x (batch 8, seq 384: 39.50 ms vs 7.14 ms). |
| **Workload** | BERT-base encoder inference at small and large batch size and sequence length, translation decoder/decoding throughput, both on T4 (FP16/INT8), and GPT-89B/175B tensor-parallel generation on 8xA100 versus Megatron. |
| **Metric** | latency |
| **Hardware** | T4 (mclk 5000 MHz, pclk 1590 MHz) with Intel Xeon E5-2670 @ 2.60 GHz; 8xA100-80GB (mclk 1593 MHz, pclk 1410 MHz) with AMD EPYC 7742 |
| **Compiler and flags** | Not stated for the measurements; CMakeLists.txt Release build uses -O3 for C++ and -Xcompiler -O3 --use_fast_math for CUDA, and the guide recommends the NGC tensorflow:22.09-tf1-py3 / pytorch:22.09-py3 containers |
| **Adoption** | 6.5k stars |
| **Last commit** | 2023-10-19 |
| **Links** | [repository](https://github.com/NVIDIA/FasterTransformer) · [benchmark](https://github.com/NVIDIA/FasterTransformer) |

## Verdict

NVIDIA's own docs/bert_guide.md tables on a T4 (Xeon E5-2670 host) show BERT-base FP16 FT 1.28x to 3.04x faster than TensorFlow XLA FP16 and 1.52x to 6.41x faster than TorchScript FP16, rising to 5.53x over TF FP16 with padding removal plus INT8-v2 (batch 8, seq 384: 39.50 vs 7.14 ms). The numbers come from the public benchmark scripts, but the compiler and CUDA versions used are not stated and the comparison mixes INT8 FT with FP16 baselines.

## Use it when

- Legacy deployments already pinned to FasterTransformer 5.x (TF1/PyTorch ops or the Triton FT backend) where the model is in its support matrix and you cannot move to TensorRT-LLM yet.
- BERT-style encoder inference on Turing/Ampere GPUs with variable-length batches, where padding removal plus INT8-v2 gives the largest gains (docs: up to 5.5x over TF FP16 at batch 32, seq 384 on T4).
- Studying or borrowing proven fused CUDA kernels (layernorm, fused MHA, beam search, top-k/top-p sampling) under Apache-2.0.
- Encoder-decoder translation decoding where FT-Decoding replaces a framework beam search loop (README: 4x to 18x over TensorFlow FP16 on T4).

## Skip it when

- New LLM serving: NVIDIA states development has moved to TensorRT-LLM and the repo will get no further development; serving engines and newer kernels (ByteTransformer, CTranslate2 per their own READMEs) beat it in several settings.
- Non-NVIDIA hardware or CPU inference: it is CUDA, cuBLAS and cuBLASLt only, verified for compute capability 7.0 and newer.
- Same-precision FP32 speedups: on T4, FP32 FT is only 1.03x to 1.44x faster than TensorFlow (bert_guide tables), so most of the headline gain needs FP16 or INT8 plus padding removal.
- Modern toolchains without patching: open bug-labelled issues report CUDA 12.2 incompatibility, clang CUDA build errors and a C++17 compile error, and the README's Known issues list TensorFlow 2.10 undefined symbols and C++ ABI mismatches when importing the PyTorch extension.
- Models outside the support matrix: each architecture is hand-written C++, so a new model means writing a new model class.

## How it is fast

Each BERT layer is reduced to 6 or 8 cuBLAS GEMMs plus 6 fused custom CUDA kernels (bias, activation, residual and layernorm fused), with an offline GEMM autotuner (bert_gemm writes gemm_config.in) choosing cuBLAS algorithms per shape. Effective FasterTransformer removes padding tokens before the encoder (the ByteDance Effective Transformer idea) and uses TensorRT's fused multi-head attention kernel; INT8 modes v1 (per-channel weights, int32 GEMM output) and v2 (per-tensor, int8 residual and GEMM output) run through cuBLASLt, and Ampere 2:4 sparse GEMM via cuSPARSELt is optional. Generation models use a fused masked multi-head attention kernel for the 1-token decode step, a preallocated key/value cache, buffer reuse across layers, and Megatron-style tensor parallelism with two all-reduces per block.

## Compared with alternatives

Pick it over ByteTransformer or LightSeq only when you need its wider model zoo (GPT, T5, BLOOM, multi-GPU tensor/pipeline parallel) or an existing Triton FT backend; for BERT alone ByteTransformer reports 24.70 vs 50.28 ms at batch 16, seq 1024, and CTranslate2 is the better-maintained choice for translation models on CPU and GPU.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | CUDA (10.2+ in CMake, 11.0+ in the BERT guide, 11.8+ for FP8), cuBLAS, cuBLASLt, optional cuDNN, CUTLASS submodule; MPI and NCCL for multi-GPU; cuSPARSELt for sparsity; TensorFlow 1.15 or PyTorch &gt;= 1.5 for the framework ops |
| **Minimum toolchain** | CMake 3.8 (3.13 for PyTorch), C++14 by default (CXX_STD cache variable; CXX flags also pass -std=c++17), nvcc with -DSM per target GPU; NGC 22.09 containers recommended |
| **Platforms** | Linux x86-64 with NVIDIA GPUs (SM 52 to 90 in the build list; correctness verified on SM 70+; INT8 on Turing+, sparsity on Ampere+, FP8 on Hopper) |
| **Thread safety** | Not documented for the C++ classes; the cuBLAS wrapper is guarded by a caller-supplied std::mutex, and the QA list warns that calling one FasterTransformer TF op from many threads may deadlock and recommends CUDA MPS instead. |
| **Drop-in for the baseline** | partial — the TF and PyTorch ops replace a framework's encoder/decoder module, but weights must be converted or loaded into FT's layout, INT8 needs a separately quantized model, and the C++ API is unrelated to TF/PyTorch |

## Gotchas

- Run the GEMM autotuner (bert_gemm, gpt_gemm and similar) for your batch/sequence shapes; without gemm_config.in it falls back to default algorithms and the guide says inference may be slower.
- The TorchScript FP16 baseline sits near 10.4 to 11 ms for every small case and TF FP16 at batch 1 seq 32 is slower than at seq 128, so small-batch ratios reflect framework overhead, not kernel speed.
- Release builds compile CUDA with --use_fast_math by default (BUILD_FAST_MATH=ON), and decoding results differ from TensorFlow because of accumulated log probabilities (Known issues).
- TensorRT's fused MHA kernel is used only on Turing+ with size_per_head 64; other shapes fall back to FT's own slower attention, and INT8 mode 1 needs sequence length a multiple of 32 above 384.

## Known shortcomings

- The 5x headline is INT8 FasterTransformer vs FP16 baselines; same-precision gains are 1.28-3.04x; the TorchScript baseline is overhead-bound.
- Discontinued (moved to TensorRT-LLM); FP32 FT vs TF on T4 only 1.03-1.44x; a TF FP16 baseline anomaly (b1/s32 at 5.84 ms slower than s128 at 3.30 ms) inflates small-batch ratios; open bugs #736 (BLOOM 0% accuracy) and #790 (position_encoding_table malloc); docs warn multithreaded op calls may deadlock.

## Caveats and trade-offs

First-party NVIDIA numbers. The '5x' headlines compare INT8 FasterTransformer against FP16 framework baselines; same-precision FP16 FT vs TF XLA on T4 is 1.28x to 3.04x. The TorchScript FP16 baseline stays near 10.4 to 11 ms for all small cases (overhead-bound), which inflates the 4x to 6x small-batch ratios. Compiler and CUDA version for the runs are not stated. Baselines are framework implementations of the era, not cuDNN. NVIDIA states the repo will see no further development (moved to TensorRT-LLM). Third-party tables (ByteTransformer, CTranslate2 READMEs) show newer kernels beating it in several settings.

NVIDIA GPUs only (Volta, Turing, Ampere, Hopper for FP8); built on CUDA, cuBLAS and cuBLASLt; TensorFlow, PyTorch and Triton wrappers; the README says development moved to TensorRT-LLM.

## Maintenance

Discontinued: last commit 2023-10-19, last release 5.2 (Dec 2022), a notice moving development to TensorRT-LLM, and 250 open issues and 38 open PRs; Apache-2.0, so kernels can be copied, but treat it as a reference rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party NVIDIA README figures and docs/bert_guide.md latency tables against TensorFlow XLA and TorchScript on a T4 with an Intel Xeon E5-2670 host, produced by public scripts (benchmarks/bert/tf_benchmark.sh, pyt_benchmark.sh, benchmarks/decoding/\*.sh). CMakeLists.txt holds the Release flags, but the compiler and CUDA version used for the measurements are not stated, so it is C, not A.
- **Verifier notes:** Metadata confirmed on the GitHub page: Apache-2.0, 6.5k stars, 935 forks, not archived or a fork, last commit 2023-10-19 (README update); release 5.2 (Dec 2022). Stale by date and will pass 3 years in October 2026; the README's discontinuation notice could justify abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/NVIDIA/FasterTransformer>
  - <https://github.com/NVIDIA/FasterTransformer/commits>
  - <https://raw.githubusercontent.com/NVIDIA/FasterTransformer/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/FasterTransformer/HEAD/docs/bert_guide.md>
  - <https://raw.githubusercontent.com/NVIDIA/FasterTransformer/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NVIDIA/FasterTransformer/HEAD/benchmarks/bert/tf_benchmark.sh>
- **Sources the enricher read:**
  - <https://github.com/NVIDIA/FasterTransformer>
  - <https://raw.githubusercontent.com/NVIDIA/FasterTransformer/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/FasterTransformer/HEAD/docs/bert_guide.md>
  - <https://raw.githubusercontent.com/NVIDIA/FasterTransformer/HEAD/docs/gpt_guide.md>
  - <https://raw.githubusercontent.com/NVIDIA/FasterTransformer/HEAD/docs/QAList.md>
  - <https://raw.githubusercontent.com/NVIDIA/FasterTransformer/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NVIDIA/FasterTransformer/HEAD/src/fastertransformer/utils/cublasMMWrapper.h>
  - <https://github.com/NVIDIA/FasterTransformer/issues?q=is%3Aissue+label%3Abug>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nvidia/fastertransformer`) · [data/wave8/enrich/raw/github_com_nvidia_fastertransformer.json](../../../data/wave8/enrich/raw/github_com_nvidia_fastertransformer.json) (enrichment confidence 0.8)

</details>
