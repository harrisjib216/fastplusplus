# SparseDNN

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++/Python` · `Apache-2.0` · 🔴 abandoned

> Python code generator emitting per-weight-matrix x86 assembly SpMM kernels for pruned networks; beats LIBXSMM sparse and dense BLAS above \~70% sparsity.

| | |
|---|---|
| **Beats** | LIBXSMM, Intel MKL/OpenBLAS dense, OpenVINO |
| **Claimed result** | 2.5x geomean over LIBXSMM SpMM single-threaded on Intel (1.7x multi-threaded); \~4x over dense BLAS at 95% sparsity (break-even \~70%); sparse conv 3.0x at 90% and 4.8x at 95% sparsity vs dense oneDNN on Intel; up to 5x throughput vs OpenVINO dense inference on pruneBERT |
| **Workload** | Sparse matrix kernels generated as x86 assembly with autotuning; end-to-end pruneBERT inference. |
| **Metric** | throughput |
| **Hardware** | AWS AMD Epyc 7R32 (AVX2); Intel Xeon Platinum 8124M (AVX512) |
| **Compiler and flags** | direct x86 assembly generation, no compiler flags |
| **Adoption** | 56 stars |
| **Last commit** | 2022-09-28 |
| **Links** | [repository](https://github.com/marsupialtail/sparsednn) · [benchmark](https://arxiv.org/abs/2101.07948) |

## Verdict

The author's own arXiv paper (2101.07948) measured generated FP32 SpMM kernels on an AWS Intel Xeon Platinum 8124M (AVX-512) and AMD Epyc 7R32 (AVX2): 2.5x geomean over LIBXSMM single-threaded on Intel (1.3x on AMD), 1.7x on Intel and breakeven on AMD at 4 threads, about 4x over dense MKL/OpenBLAS at 95% sparsity, sparse conv 3.0x/4.8x (Intel) and 3.4x/6.3x (AMD) over dense oneDNN at 90/95% sparsity, and up to 5x pruneBERT throughput over OpenVINO; compiler and flags for the baselines are not given in the paper.

## Use it when

- CPU inference of models pruned to 80-95% unstructured sparsity with weights fixed at deploy time (pruneBERT-style fully connected / 1x1 conv layers).
- x86-64 servers with AVX2 or AVX-512 where you can afford an offline code-generation and autotune step per weight matrix.
- Research or benchmarking of sparse FP32 SpMM kernels against LIBXSMM/MKL, since it exposes kernel-level timing.
- Single-threaded or low-core-count deployments, where its advantage over LIBXSMM is largest (2.5x geomean on Intel single-thread vs 1.7x at 4 threads).

## Skip it when

- Sparsity below about 70%: the paper puts the break-even with dense BLAS there, so dense MKL/oneDNN wins.
- Dynamic or activation sparsity: patterns must be known at code-generation time; the paper says it does not handle ReLU-induced activation sparsity.
- Production end-to-end inference: the sparse-convolution generator and the inference engine from the paper were never open-sourced; the README itself points end-to-end users to Neural Magic DeepSparse.
- Multi-threaded throughput on AMD (breakeven with LIBXSMM at 4 threads) or aarch64 (code paths for ARM exist in the generator but no ARM results are published).
- Anything needing maintenance or support: last commit 2022, single author who says he works on it sparingly.

## How it is fast

The generator unrolls the whole sparse matrix into straight-line code: each nonzero is a vbroadcastss of the weight followed by vfmadd231ps against a row slice of B whose offset is baked into the instruction as an immediate, so there is no index decoding at run time. It adapts dense-GEMM register blocking (AT x CT microkernel tiles) plus split-K tiling over the reduction dimension, and stores values in a custom order matching the kernel's traversal. Tile sizes are autotuned per matrix by brute-force search over AT/CT/B_blocks.

## Compared with alternatives

Pick it over LIBXSMM when weights are highly sparse (90%+) and fixed, since LIBXSMM is the faster general choice for dense small GEMM and its sparse path lost 2.5x here single-threaded; for LLM inference with quantized rather than pruned weights, T-MAC or llamafile tinyBLAS fit better.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Python + NumPy for the generator; gcc to assemble the generated .s; C++ driver needs cnpy and the autotune script calls icc with -mkl and OpenMP |
| **Minimum toolchain** | C++17 for driver_cpu.cpp (per autotune script); otherwise not documented |
| **Platforms** | x86-64 with AVX2 (AVX-512 used when present); Linux assumed (reads /proc/cpuinfo) |
| **Thread safety** | not documented; the driver parallelizes by splitting work across OpenMP threads with start/end ranges |
| **Drop-in for the baseline** | no |

## Gotchas

- Each generated kernel is valid only for one weight sparsity pattern and one dense column count (C_dim); new weights or batch shapes require regeneration.
- fastsparse.py has module-level test code that loads matrix.npy and benchmarks on import, and compile() writes out.s/out.cpp to the current directory and shells out via os.system.
- The Python API adds noticeable ctypes overhead on small matrices; the paper's numbers come from the C++ driver.
- autotune_cpu_random.sh passes -D CT=\$1 (the A dimension) to the driver instead of \$CT, so the tuning script's driver build looks buggy; check before trusting its output.

## Known shortcomings

- Single-author arXiv paper; no flags in repo; sparse-conv generator and inference engine not open source; abandoned (last commit 2022-09-28).
- Correction: paper says 22% faster on Intel and 9% slower on AMD vs SkimCaffe single-threaded; at 4 threads only breaks even with LIBXSMM on AMD; each kernel works for one fixed sparsity pattern and shape; fastsparse.py runs test code on import; autotune script likely passes wrong -D CT value; driver built with icc -mkl -O3 -march=native (paper states no compiler).

## Caveats and trade-offs

Sparse convolution generator and inference engine were not open-sourced. oneDNN/XNNPACK not directly compared; baselines are LIBXSMM, MKL, OpenVINO. Paper-only benchmark, 22% slower on AMD vs SkimCaffe.

Needs sparse (pruned) weights; Python API has ctypes overhead; C++ API used in paper benchmarks.

## Maintenance

Abandoned since September 2022 but Apache-2.0 and only a handful of Python files, so the generator can be vendored; the parts needed for end-to-end inference were never released.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Single-author arXiv paper (no venue found) by the repo author reports 2.5x single-thread / 1.7x multi-thread geomean over LIBXSMM SpMM, \~4x over dense BLAS at 95% sparsity and up to 5x over OpenVINO; autotune scripts exist in the repo but compiler/flags not stated, so C.
- **Verifier notes:** Repo: Apache-2.0, 56 stars, 30 commits, not archived, last commit 2022-09-28 (abandoned) all confirmed. Paper does compare sparse conv against dense oneDNN, so the caveat 'oneDNN not directly compared' is slightly off; the AMD 1.3x / 22%-slower-than-SkimCaffe figures were not re-checked.
- **Fields the verifier corrected:** `claimed_speedup`
- **Shortcomings recorded by:** paper: sparse conv vs dense oneDNN on AMD 3.4x at 90%, 6.3x at 95% sparsity
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2101.07948>
  - <https://github.com/marsupialtail/sparsednn>
  - <https://github.com/marsupialtail/sparsednn/commits>
- **Sources the enricher read:**
  - <https://github.com/marsupialtail/sparsednn>
  - <https://raw.githubusercontent.com/marsupialtail/sparsednn/HEAD/README.md>
  - <https://raw.githubusercontent.com/marsupialtail/sparsednn/HEAD/fastsparse.py>
  - <https://raw.githubusercontent.com/marsupialtail/sparsednn/HEAD/driver_cpu.cpp>
  - <https://raw.githubusercontent.com/marsupialtail/sparsednn/HEAD/autotune_cpu_random.sh>
  - <https://raw.githubusercontent.com/marsupialtail/sparsednn/HEAD/code_gen_cpu.py>
  - <https://arxiv.org/abs/2101.07948>
  - <https://arxiv.org/pdf/2101.07948>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/marsupialtail/sparsednn`) · [data/wave8/enrich/raw/github_com_marsupialtail_sparsednn.json](../../../data/wave8/enrich/raw/github_com_marsupialtail_sparsednn.json) (enrichment confidence 0.75)

</details>
