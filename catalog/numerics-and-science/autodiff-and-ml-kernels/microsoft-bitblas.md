# BitBLAS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Python (TVM/TileLang code generation) with CUDA kernels` · `MIT` · 🔴 abandoned

> Auto-tuned mixed-precision GPU GEMV/GEMM (FP16/INT8 activations x INT4/INT2/INT1/NF4/FP4/FP8 weights) that beats FP16 cuBLAS by moving fewer bytes.

| | |
|---|---|
| **Beats** | cuBLAS (W_FP16 A_FP16 GEMV/GEMM); also CUTLASS, bitsandbytes, FasterTransformer, TensorRT-LLM, vLLM and Marlin |
| **Claimed result** | README: W_INT2 A_INT8 GEMV/GEMM '8x/2x speedup over cuBLAS W_FP16 A_FP16 on A100' (shown only in the op_benchmark_a100_int2_scaling image). benchmark/README.md: on RTX 3090, FP16 and INT8 Tensor Core GEMM 'matches the performance of cuBLAS and CUTLASS'; float16xnf4 GEMV/GEMM 'achieves 2x the speed of bitsandbytes and 4x the base float16 performance'; on A100, int4 dequantize 'outperforms bitsandbytes, faster-transformer, tensorrt-llm, vLLM, and Marlin'. Ladder OSDI'24 Figure 12 (artifact/Figure12/paper_result/operator_performance_a100.png, A100, approximate bar readings normalised to Ladder's own FP16 kernel): at equal FP16 precision cuBLAS is roughly at parity (about 0.85x to 1.3x of Ladder FP16, i.e. cuBLAS is faster on some GEMM shapes); Ladder W_INT4 A_FP16 reaches about 3.5x and W_INT1 A_INT8 about 10x over Ladder FP16 on the largest GEMM shapes; on the 8 convolution shapes cuDNN sits at roughly 0.1x to 0.75x of Ladder FP16. A WebSearch summary of the paper (PDF not opened) also cites average 1.8x over cuBLAS for W_FP16 A_FP16 and 4.5x for W_INT1 A_INT8, up to 13.3x on V100 and 14.6x on A6000; these could not be checked against the text. |
| **Workload** | Mixed-precision GEMV and GEMM for LLM layer shapes (BLOOM, OPT, LLaMA, LLaMA-2 matrix sizes) with FP16, INT8, FP16xINT4/NF4 and W_INT2 A_INT8 formats on A100 and RTX 3090. |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 3090 (24GB) and NVIDIA A100 (80GB); host CPU not stated |
| **Compiler and flags** | CUDA 12.1; bitsandbytes 0.43.0; vLLM 865732342b4e3b8a4ef38f28a2a5bdb87cf3f970; FasterTransformer 1afbf20129647a35d108152fc6789bc1d029cda5; TensorRT-LLM 2bf3a0a4287069ac55ee3304c285b08592d3d1bc; CUTLASS 629f4653c3ea3db3264030382956fabe715f3436; Marlin 512f1b1ba39ff708bcc95419f11cfd1285cd31b3 |
| **Adoption** | 770 stars; archived 2026-02-24; Ladder (OSDI'24) is the technical basis |
| **Last commit** | 2025-05-05 |
| **Links** | [repository](https://github.com/microsoft/BitBLAS) · [benchmark](https://github.com/microsoft/BitBLAS/blob/HEAD/benchmark/README.md) |

## Verdict

First-party plots on an RTX 3090 and an A100-80GB with CUDA 12.1 (third-party baselines pinned by commit: bitsandbytes 0.43.0, vLLM, FasterTransformer, TensorRT-LLM, CUTLASS and Marlin, reproduced via the separate mlc-benchmark repo) show FP16/INT8 tensor-core GEMM matching cuBLAS/CUTLASS, FP16 x NF4 at 2x bitsandbytes and 4x FP16, and W_INT2 A_INT8 GEMV/GEMM at 8x/2x over FP16 cuBLAS on A100 for BLOOM/OPT/LLaMA layer shapes. The peer-reviewed Ladder paper (OSDI'24) covers the TVM-based artifact branch, not the later TileLang release, and all numbers are in images, not text.

## Use it when

- Memory-bound LLM decode (batch 1 to small batches) with weight-only quantization (INT4/NF4/INT2) on Ampere or Ada NVIDIA GPUs (A100, A6000, RTX 3090/4090 are the tested platforms).
- Unusual format pairs that hand-written kernels lack: INT8 x INT2/INT1 (BitNet b1.58), INT4 x INT4, FP16 x FP4/FP8, BF16 x NF4.
- Research on new quantization formats, where you need a kernel for a dtype combination without writing CUDA (TIR/TileLang DSL customization).
- A frozen deployment where you can pre-tune kernels once and load them from BitBLAS's on-disk operator database.

## Skip it when

- New production work: the repo was archived on 2026-02-24 (last commit 2025-05-05) and open wrong-result bug reports will not be fixed.
- FP16 x FP16 or INT8 x INT8 GEMM alone: the benchmark README only claims to match cuBLAS/CUTLASS there.
- Hopper or Blackwell GPUs: the README support matrix has no sm_90 or newer row (tested platforms are V100, A100, A6000 and RTX 4090), so performance there is not documented.
- Latency-sensitive startup: the QuickStart says bitblas.Matmul initialization 'will take minutes' for a one-time kernel library build per configuration.
- Non-Linux hosts or Python-free C++ use: wheels are Ubuntu 20.04+ only, and the kernels are reached through a Python/TVM runtime.

## How it is fast

It implements Ladder (OSDI'24): low-bit weights are stored packed and dequantized on the fly inside the tensor-core GEMM, so a memory-bound GEMV reads 4-16x fewer bytes than FP16. Weights are pre-permuted offline ('ladder permutate' into ldmatrix-friendly layouts, and 'lop3 permutate' so dequantization uses LOP3 bit tricks, fast_decoding), which removes layout shuffles and cheapens unpacking. Kernels are generated by TVM TIR or TileLang schedulers and tuned per shape and GPU, with dynamic-M kernels built for an opt_M list such as [1, 16, 32, 64, 128].

## Compared with alternatives

Pick BitBLAS over Marlin when you need weight formats other than FP16 x INT4 (INT2/INT1/NF4/FP4/FP8, or INT8 activations), or shape coverage beyond small batches; for plain GPTQ INT4 inference Marlin is a smaller, single-purpose kernel that is not archived. T-MAC and BitNet (bitnet.cpp) are the CPU counterparts for the same low-bit LLM workloads.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | PyTorch, a bundled TVM fork and TileLang (3rdparty, built with CMake against a downloaded LLVM 10.0.1 when building from source), CUDA toolkit &gt;= 11.0, plus numpy, scipy, tornado, cloudpickle, ml_dtypes and others from requirements.txt |
| **Minimum toolchain** | Python &gt;= 3.8 and CUDA &gt;= 11.0 for the PyPI wheel (Ubuntu 20.04+); source build needs CMake, gcc and LLVM |
| **Platforms** | Linux x86-64 with NVIDIA GPUs; tested on V100 (sm_70), A100 (sm_80), A6000 (sm_86), RTX 4090 (sm_89); FP8 and INT4xINT4 only on sm_89. The OSDI artifact branch also lists an AMD MI250, and an install_amd.sh script exists (issue #298), but the main README support matrix is NVIDIA-only |
| **Thread safety** | partial — the global OperatorCache guards its dict with a threading.RLock; concurrent kernel calls are otherwise not documented (kernels launch on torch.cuda.current_stream) |
| **Drop-in for the baseline** | partial — bitblas.Linear mimics nn.Linear, but weights must be repacked with load_and_transform_weight, and it replaces cuBLAS only through its own Matmul/Linear API, not as a BLAS-compatible library |

## Gotchas

- Open, unanswered correctness bugs in the formats the headline claim is about: #316 (W_INT2 A_INT8 Matmul, 0.1.0.post1) gives 6.2% mismatched elements (max abs diff 19,645) on the first call but correct results later, which the reporter attributes to a different kernel being selected; #313 reports wrong values from a W_INT4 A_INT8 Linear on an RTX 4090.
- #296 (open): bitblas.Linear with uint4 weights and with_scaling=True leads to a CUDA illegal memory access.
- Inputs whose M is not in opt_M run the next-larger tuned kernel (an M of 15 uses the M=16 kernel), so performance between tuned points is not what the plots show.
- The 8x/2x A100 claim compares W_INT2 A_INT8 against W_FP16 A_FP16 cuBLAS, so most of the gain comes from moving fewer bytes and depends on the model tolerating 2-bit weights; the PyPI release (0.1.0.post1, 2025-02-16) lags the repo, and the OSDI artifact lives on a separate TVM-based branch.

## Known shortcomings

- At equal FP16 it is roughly even with cuBLAS (gains come from low-bit weights); tier B rests on the Ladder OSDI'24 artifact branch; archived 2026-02-24.
- Archived with open wrong-result bugs in the headline formats, unanswered: #316 W2A8 6.2% mismatched on first call, #313 W4A8 Linear wrong values, #296 illegal memory access with scaling; no Hopper row in the support matrix.

## Caveats and trade-offs

The 8x/2x figure compares W_INT2 A_INT8 against a W_FP16 A_FP16 cuBLAS GEMM, so the gain comes largely from moving fewer bytes, not from an equal-precision kernel; at equal FP16/INT8 precision the repo only claims to match cuBLAS/CUTLASS, and the paper's Figure 12 shows cuBLAS at rough parity (faster on some shapes). Result plots are images; figure values are bar readings. The peer-reviewed numbers are for the Ladder artifact branch (TVM/Welder-based compiler, CUDA 12.0), not the later TileLang-based BitBLAS release. Repo archived 2026-02-24; last commit 2025-05-05. cuBLAS is not one of the category baselines; cuDNN appears only in the paper's convolution panel. Third-party baselines in benchmark/README.md are reproduced via the separate LeiWang1999/mlc-benchmark repo (not opened).

Gains come from low-bit weights (INT2/INT4/NF4), so accuracy depends on the quantized model; for plain FP16/INT8 GEMM it only matches cuBLAS. Integrates with PyTorch, vLLM, AutoGPTQ, GPTQModel and BitNet b1.58.

## Maintenance

Archived by Microsoft on 2026-02-24 (last commit 2025-05-05, PyPI 0.1.0.post1 from 2025-02-16); MIT-licensed and usable as a frozen dependency or reference for Ladder-style layout transforms, but bugs will not be fixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: BitBLAS is the library form of Ladder, a peer-reviewed OSDI'24 paper whose artifact (branch osdi24_ladder_artifact of this repo, scripts under artifact/Figure12 and artifact/Table1, CUDA 12.0 Dockerfile) benchmarks against cuBLAS, cuDNN, CUTLASS and vLLM on an A100-80GB-PCIe; the paper-result Figure 12 image was opened. Host CPU and compiler flags are not stated and the paper PDF (usenix.org) was blocked, so B, not A.
- **Verifier notes:** Metadata confirmed via github.com: MIT (Microsoft), 770 stars, archived 2026-02-24, not a fork, last commit 2025-05-05 ('Update tilelang&cutlass to newest (#303)'), so abandoned is right. Ladder paper venue confirmed by README citation (OSDI 24) and the artifact branch README; usenix.org PDF EGRESS_BLOCKED, so paper numbers come from a WebSearch snippet only.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/microsoft/BitBLAS>
  - <https://github.com/microsoft/BitBLAS/commits>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/README.md>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/LICENSE>
  - <https://github.com/microsoft/BitBLAS/tree/osdi24_ladder_artifact>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/osdi24_ladder_artifact/README.md>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/osdi24_ladder_artifact/artifact/Figure12/paper_result/operator_performance_a100.png>
- **Sources the enricher read:**
  - <https://github.com/microsoft/BitBLAS>
  - <https://github.com/microsoft/BitBLAS/tree/main/bitblas/ops>
  - <https://github.com/microsoft/BitBLAS/issues?q=is%3Aissue+wrong+OR+incorrect+OR+mismatch+OR+nan>
  - <https://github.com/microsoft/BitBLAS/issues/296>
  - <https://github.com/microsoft/BitBLAS/issues/313>
  - <https://github.com/microsoft/BitBLAS/issues/316>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/README.md>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/setup.py>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/VERSION>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/docs/QuickStart.md>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/docs/Installation.md>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/docs/PythonAPI.md>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/bitblas/ops/general_matmul/__init__.py>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/bitblas/ops/operator.py>
  - <https://raw.githubusercontent.com/microsoft/BitBLAS/HEAD/bitblas/cache/operator.py>
  - <https://pypi.org/pypi/bitblas/json>
  - <https://github.com/microsoft/BitBLAS/commits/main>
  - <https://github.com/microsoft/BitBLAS/tree/osdi24_ladder_artifact>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/microsoft/bitblas`) · [data/wave8/enrich/raw/github_com_microsoft_bitblas.json](../../../data/wave8/enrich/raw/github_com_microsoft_bitblas.json) (enrichment confidence 0.8)

</details>
