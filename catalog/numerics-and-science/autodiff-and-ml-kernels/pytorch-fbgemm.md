# FBGEMM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Meta's x86 low-precision GEMM, convolution and embedding kernel library behind PyTorch quantized CPU ops; INT8 reported 2x MKL FP32 at batch 1.

| | |
|---|---|
| **Beats** | Intel MKL FP32 GEMM (via a cited Microsoft paper), caffe2/perfkernels (embedding SpMDM), a prior 64-bit GEMM implementation |
| **Claimed result** | Wiki page (last edited 2020-01-18): a cited Microsoft/Marian NMT paper reports FBGEMM INT8 at 2x the throughput of MKL FP32 at batch size 1 and 1.3x at batch size 32; EmbeddingSpMDM gives \~2x over caffe2/perfkernels (and 18-25% average-latency gains on production recommendation models); the new 64-bit GEMM reaches 10.5 GOps/s vs 3 GOps/s for the existing implementation (3.5x) on a Xeon Gold 6138 with turbo off; 3D groupwise convolution is 60x faster than the base fused im2col implementation; stride-2 convolutions are 4-10x faster than the existing implementation; 2x-4x speedups at 90% sparsity with specialized sparse kernels. |
| **Workload** | Low-precision GEMM, convolution, embedding and sparse operators for server-side inference, as summarized on the FBGEMM wiki page 'Recent feature additions and improvements'. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6138 (turbo off) for the GEMM number and Xeon D-2191 for the ResNet-50 thread-scaling number; other results state no hardware |
| **Adoption** | 1.6k stars; the CPU backend of PyTorch quantized inference |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/pytorch/FBGEMM) · [benchmark](https://github.com/pytorch/FBGEMM/wiki/Recent-feature-additions-and-improvements-in-FBGEMM) |

## Verdict

The FBGEMM wiki (last edited 2020-01-18) cites a Microsoft/Marian NMT paper reporting FBGEMM INT8 at 2x MKL FP32 throughput at batch 1 (1.3x at batch 32), and reports first-party gains against caffe2 perfkernels (EmbeddingSpMDM about 2x) and FBGEMM's own earlier code (64-bit GEMM 10.5 vs 3 GOps/s on a Xeon Gold 6138 with turbo off; groupwise conv 4-10x and 60x). No compiler, flags or benchmark harness is named for these numbers, and the cited paper and the FBGEMM arXiv paper could not be opened here.

## Use it when

- INT8 quantized inference on x86 servers with AVX2 or AVX-512/VNNI, especially small-batch fully connected layers where packing and requantization overhead matter (cited Marian paper: 2x MKL FP32 throughput at batch 1, 1.3x at batch 32).
- Recommendation models with large embedding tables: EmbeddingSpMDM is about 2x the older caffe2 perfkernels per the wiki, with 18-25% lower average latency on production models.
- Groupwise or depthwise convolutions with few channels per group (2, 4, 8, 16), where the wiki reports 4-10x for stride 2 and 60x for 3D groupwise over FBGEMM's earlier im2col path.
- You already use PyTorch quantization (the fbgemm qengine) and want to call the same kernels directly from C++.
- Moderately sparse weights (around 90%) where the sparse INT8/FP32 kernels report 2x-4x.

## Skip it when

- ARM servers or Apple silicon: the docs require AVX2 or higher; aarch64 builds define reference-kernel fallbacks for FP16/FP32 GEMM, direct convolution is compiled out, and open issue #4679 reports build problems and incorrect SVE kernel results on arm64.
- Plain FP32 BLAS replacement: the API is pack-then-compute with quantization parameters, not sgemm, and the headline gains come from reduced precision versus FP32.
- When you need an independent, reproducible speed claim: the public numbers are 2019-2020 first-party wiki prose or a cited paper, and the large ratios (60x, 3.5x) are against FBGEMM's own earlier code.
- Accuracy-sensitive models that you cannot quantize or calibrate: INT8 and ACC16 paths need per-tensor or per-channel scales and zero points and may need outlier handling.
- Toolchains older than C++20 or CMake 3.21: the current build rejects anything below C++20.

## How it is fast

Inner GEMM kernels are generated at runtime with asmjit, specialized to the matrix shape and the detected instruction set (AVX2, AVX-512, AVX-512 VNNI, with cpuinfo for dispatch), and cached in a code cache shared across threads. Quantization bookkeeping is fused into packing (row offsets computed while packing A) and into a composable output pipeline (requantize, bias, ReLU, sparse outlier SpMDM on the int32 buffer), so bandwidth-bound low-precision GEMMs avoid extra passes. 16-bit-accumulation kernels (ACC16), specialized depthwise and groupwise convolution paths, and EmbeddingSpMDM kernels for embedding bags cover the shapes that dominate recommendation and NLP inference.

## Compared with alternatives

Pick it over LIBXSMM when the job is INT8 quantized inference with fused requantization or embedding-bag lookups on x86, especially inside PyTorch; LIBXSMM is the better fit for small dense FP32/BF16 GEMMs and convolutions on both x86 and ARM, and llamafile tinyBLAS or T-MAC target LLM weight formats instead.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | asmjit and cpuinfo (bundled as submodules, overridable via ASMJIT_SRC_DIR / CPUINFO_SRC_DIR); OpenMP optional; GoogleTest only for tests; Python needed at configure time to read source lists from defs.bzl; KleidiAI on non-Apple aarch64; no MKL dependency |
| **Minimum toolchain** | C++20, CMake 3.21; GCC or Clang (libc++/libomp for Clang), MSVC 2019+ on Windows; GCC 12+ needs -Wno-error workarounds per the build docs; SVE paths need GCC 14+ or Clang 17+ |
| **Platforms** | x86-64 with AVX2 required (AVX-512 and AVX-512 VNNI kernels dispatched at runtime); aarch64 NEON/SVE builds exist but are partial; Linux, macOS, Windows |
| **Thread safety** | Caller-driven: each GEMM/conv call takes thread_id and num_threads and computes only its slice, so you parallelize (e.g. OpenMP) and synchronize yourself; the JIT code cache is shared across threads; groupwise convolution ignores thread_id &gt; 0 (no threading). |
| **Drop-in for the baseline** | no |

## Gotchas

- Call fbgemmSupportedCPU() before use; on CPUs below AVX2 the optimized paths are unavailable.
- fbgemmGroupwiseConv does nothing for thread_id &gt; 0, so splitting it across threads silently leaves work to thread 0.
- Row offsets from packing A and column offsets with zero points must be supplied correctly to ReQuantizeOutput; passing nullptr is only valid for symmetric weight quantization.
- Bug reports in the issue tracker are often for FBGEMM_GPU (for example #5326, zeroed embeddings above dim 1024), not the CPU library; check which package an issue applies to.

## Known shortcomings

- Wiki dates from 2020; most wins are against its own older code or INT8 vs FP32; the Marian WNGT 2019 paper is unreadable here (possible B on retier).
- Open issue #4679 reports incorrect SVE kernel results on arm64; fbgemmGroupwiseConv does nothing for thread_id&gt;0; needs C++20 and AVX2; FP16/FP32 fall back to reference kernels on aarch64.

## Caveats and trade-offs

Most speedups compare reduced precision against FP32 or compare against FBGEMM's own older code paths (the 60x and 3.5x figures), so they say little about external incumbents; accuracy trade-offs apply. The MKL comparison comes from a third-party paper ("From Research to Production and Back: Ludicrously Fast Neural Machine Translation", WNGT at EMNLP 2019) that the wiki cites; its PDF could not be opened here. The wiki dates from January 2020, so the numbers are 2019-era. Many wiki claims state no hardware or flags. The MLSys 2021 paper (arXiv 2101.05615) could not be opened (arxiv.org blocked) and may carry stronger evidence. Baselines are not oneDNN, cuDNN or XNNPACK. [retier] Correction: the FBGEMM paper (Khudia et al., arXiv 2101.05615) is not an MLSys 2021 paper. The README's recommended citation lists it as an 'arXiv preprint' by the FBGEMM team, so it is first-party and would not lift the tier. The independent, peer-reviewed Marian WNGT 2019 paper (ACL D19-5632) remains unopened: aclanthology.org is blocked, the Microsoft Research publication page links only to the ACL Anthology (and its abstract does not mention FBGEMM), and no copy was found on GitHub.

INT8, FP16 and sparse kernels that need quantization-aware model changes; x86 (AVX2, AVX-512) JIT-generated kernels; separate FBGEMM_GPU and GenAI packages exist in the same repo.

## Maintenance

Actively developed by Meta (last commit 2026-10-01, 5,473 commits, 66 open issues) and BSD-3-Clause, but the CPU library's public performance documentation dates from 2020 and most recent work is in the GPU packages.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The wiki page is first-party prose with headline ratios against MKL FP32 (via a cited paper), caffe2/perfkernels and FBGEMM's own earlier code; hardware is named for only two results, and no compiler, flags or benchmark code path is given. The cited Marian WNGT 2019 workshop paper (peer-reviewed) could not be opened (aclanthology.org blocked), so B cannot be confirmed.
- **Verifier notes:** All record numbers appear on the wiki page. Metadata from github.com: LICENSE is the 3-clause BSD text (BSD-3-Clause), 1.6k stars, 791 forks, not archived, last commit 2026-10-01. A re-tier to B would need someone to open the Marian WNGT 2019 paper (ACL Anthology D19-5632) and confirm the FBGEMM vs MKL table.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pytorch/FBGEMM/wiki/Recent-feature-additions-and-improvements-in-FBGEMM>
  - <https://github.com/pytorch/FBGEMM>
  - <https://github.com/pytorch/FBGEMM/commits>
  - <https://raw.githubusercontent.com/pytorch/FBGEMM/HEAD/LICENSE>
  - <https://www.microsoft.com/en-us/research/publication/from-research-to-production-and-back-ludicrously-fast-neural-machine-translation/>
- **Sources the enricher read:**
  - <https://github.com/pytorch/FBGEMM>
  - <https://github.com/pytorch/FBGEMM/wiki/Recent-feature-additions-and-improvements-in-FBGEMM>
  - <https://raw.githubusercontent.com/pytorch/FBGEMM/HEAD/README.md>
  - <https://raw.githubusercontent.com/pytorch/FBGEMM/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/pytorch/FBGEMM/HEAD/cmake/modules/CxxCompilerSetup.cmake>
  - <https://raw.githubusercontent.com/pytorch/FBGEMM/HEAD/defs.bzl>
  - <https://raw.githubusercontent.com/pytorch/FBGEMM/HEAD/include/fbgemm/Fbgemm.h>
  - <https://raw.githubusercontent.com/pytorch/FBGEMM/HEAD/fbgemm_gpu/docs/src/fbgemm/index.rst>
  - <https://raw.githubusercontent.com/pytorch/FBGEMM/HEAD/fbgemm_gpu/docs/src/fbgemm/development/BuildInstructions.rst>
  - <https://github.com/pytorch/FBGEMM/issues?q=is%3Aissue+incorrect+OR+wrong+OR+overflow+OR+segfault>
  - <https://github.com/pytorch/FBGEMM/issues/4679>
  - <https://github.com/pytorch/FBGEMM/issues/5326>
  - WebSearch snippets for arXiv 2101.05615 (arxiv.org and engineering.fb.com egress-blocked)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/pytorch/fbgemm`) · [data/wave8/enrich/raw/github_com_pytorch_fbgemm.json](../../../data/wave8/enrich/raw/github_com_pytorch_fbgemm.json) (enrichment confidence 0.75)

</details>
