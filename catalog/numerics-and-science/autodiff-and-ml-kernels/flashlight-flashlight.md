# Flashlight

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++-native deep learning framework from FAIR (wav2letter successor) that trains standard networks slightly faster than PyTorch 1.8 and TensorFlow 2.4.

| | |
|---|---|
| **Beats** | PyTorch 1.8 and TensorFlow 2.4 |
| **Claimed result** | ICML 2022 paper Table 3 (seconds per 100 iterations, lower is better; order PyTorch / TensorFlow / Flashlight; 1 GPU then 8 GPUs): AlexNet 2.0 / 4.0 / 1.4 then 6.0 / 6.5 / 2.1; VGG16 14.8 / 12.6 / 13.2 then 16.3 / 17.9 / 14.9; ResNet-50 11.1 / 12.4 / 10.3 then 12.3 / 15.9 / 11.9; BERT-like 19.6 / 19.8 / 17.5 then 22.7 / 23.6 / 19.2; ASR transformer 58.5 / 63.7 / 53.6 then 63.7 / 69.7 / 57.5; ViT 137.8 / 140.3 / 129.3 then 143.1 / 169.6 / 141.0. Ratios (derived from page data): AlexNet 1 GPU 1.43x vs PyTorch and 2.86x vs TensorFlow, 8 GPUs 2.86x and 3.10x; ResNet-50 1 GPU 1.08x and 1.20x; ViT 8 GPUs 1.02x vs PyTorch and 1.20x vs TensorFlow. On 1 GPU VGG16 TensorFlow (12.6) beats Flashlight (13.2). |
| **Workload** | Wall-clock seconds for 100 iterations of forward plus backward passes including data loading, on six large networks (AlexNet, VGG16, ResNet-50, a BERT-like transformer, an ASR transformer, ViT), on 1 GPU and 8 GPUs with data-parallel gradient synchronization. |
| **Metric** | throughput |
| **Hardware** | Intel E5-2698 CPUs with 512 GB RAM, NVIDIA V100-32GB GPUs in a DGX-1 server, NVLink between GPUs for the 8-GPU runs |
| **Adoption** | 5.5k stars, 503 forks; Meta (FAIR) project, successor of wav2letter |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/flashlight/flashlight) · [benchmark](https://arxiv.org/pdf/2201.12465) |

## Verdict

The authors' ICML 2022 paper (Table 3, read only through search-result snippets because arXiv and PMLR are blocked here) times 100 forward-plus-backward iterations including data loading for AlexNet, VGG16, ResNet-50, a BERT-like Transformer, an ASR Transformer and ViT on a DGX-1 (Intel E5-2698, V100-32GB) with Flashlight 0.3.1 vs PyTorch 1.8 and TensorFlow 2.4. Flashlight is fastest in 11 of 12 rows, but outside AlexNet (1.43x on 1 GPU, 2.86x on 8 GPUs vs PyTorch) the margin over the faster competitor is 1.01x to 1.18x, and TensorFlow wins VGG16 on 1 GPU (12.6 s vs 13.2 s) (ratios derived from page data); compiler, flags and the baseline scripts are not published.

## Use it when

- You need to train or fine-tune networks inside a C++ application or service with no Python runtime at all.
- Research on framework internals: adding a custom tensor backend through fl::Tensor (subclass TensorAdapterBase and TensorBackend), custom memory managers or new autograd ops, in a core of roughly 20k lines.
- Small or launch-overhead-bound models where per-op framework overhead dominates (the paper's AlexNet rows: 1.4 s vs 2.0 s PyTorch on 1 GPU, 2.1 s vs 6.0 s on 8 GPUs per 100 iterations).
- Speech recognition work that builds on the wav2letter lineage (ASR app, CTC and ASG criteria, beam-search decoding via flashlight/text) on Linux with NVIDIA GPUs.

## Skip it when

- Large standard models where the paper shows only 1-18% gains over the faster of PyTorch 1.8 and TensorFlow 2.4 (derived from page data) and TensorFlow wins VGG16 on 1 GPU; current PyTorch releases were never compared, so there is no evidence it is faster today.
- Python-first teams or anyone needing the PyTorch/TensorFlow ecosystem (pretrained models, model import, torch.compile, recent attention kernels): none of these appear in the files read.
- Windows, macOS beyond a minimal OpenCL core build, or AMD GPUs: the vcpkg ports declare !(windows | osx), Windows build issue #1181 and ROCm request #1099 are open, and the README requires a Linux-based OS.
- CPU-only small MLPs: issue #898 (2022) reports the Perceptron example much slower than JAX+Flax with jit on CPU, and issue #630 (2021) reports ResNet-34 training on V100 slower than PyTorch; no maintainer replies or fixes were visible on either page.
- Projects that need upstream support: an open 'Future of Flashlight' issue (#1185, Nov 2025) says PRs are not reviewed, and recent commits are automated Meta fbcode syncs and build fixes.

## How it is fast

The default tensor backend is ArrayFire, which JIT-fuses chains of element-wise ops into generated kernels; convolutions and RNNs go to cuDNN (or oneDNN on CPU), and with benchmark mode on, fl::DynamicBenchmark times the candidate cuDNN algorithms online and keeps the fastest. A caching block allocator (CachingMemoryManager: 512-byte rounding, 2 MiB small-block and 20 MiB large-block pools, block splitting) is installed as the default memory manager, and multi-GPU gradient sync uses a coalescing all-reduce (CoalescingReducer over NCCL). The rest of the edge is low framework overhead: no Python interpreter in the training loop, which is why the gap is largest on small, overhead-bound models such as AlexNet.

## Compared with alternatives

Pick Flashlight over OneFlow or LightSeq when you want a whole training framework that lives entirely in C++ and whose internals you intend to modify; OneFlow offers a PyTorch-like Python API with a public multi-framework DLPerf harness, and LightSeq accelerates Transformer layers inside existing PyTorch training. Pick it over llm.c when you need many architectures (CNNs, ViT, DETR, ASR and LM Transformers) rather than one hand-written GPT-2 training path.

## Integration

| | |
|---|---|
| **Form** | static lib (shared with BUILD_SHARED_LIBS), consumed as the CMake package flashlight::flashlight; also vcpkg ports flashlight-cuda and flashlight-cpu |
| **Dependencies** | ArrayFire &gt;= 3.7.3 (one of its CUDA, CPU or OpenCL backends) for the default tensor backend; CUDA &gt;= 9.2 with cuDNN (and NCCL for distributed) on GPU, or oneDNN &gt;= 2.5.2 with gloo on CPU; an MPI library for distributed training (required by all apps); cereal and stb; a BLAS (Intel MKL or OpenBLAS) for flashlight/lib; gflags and glog for apps; libsndfile and flashlight/text for ASR |
| **Minimum toolchain** | CMake 3.16 (top-level CMakeLists; README still says 3.10); README says C++17 with gcc &gt;= 7, but main uses std::unordered_map::contains (C++20) in fl/runtime/DeviceManager.cpp, so a strict C++17 build fails (issues #1183 with g++ 11.4, #1187); CUDA code is compiled as C++14 |
| **Platforms** | Linux x86-64 with NVIDIA GPUs (CUDA) or CPU (oneDNN or ArrayFire CPU); macOS only as a minimal ArrayFire-OpenCL core build; no Windows vcpkg support; no ROCm |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness bug in the repo's own benchmark (flashlight/app/benchmark/Run.cpp, runDetr): targetBoxes and targetClasses are constructed with batchsize default (empty) Variables and the generated targets are then push_back'ed after them, while HungarianMatcher::compute reads indices 0..batchsize-1; it therefore sees 12 empty targets, takes its 'targetClasses.isEmpty()' shortcut and never builds a cost matrix or runs the Hungarian solve. The README's DETR throughput rows (21.64 img/s FP32 on 1 V100) do not include real set-matching work. This affects only that Flashlight-only table, not the paper's PyTorch/TensorFlow comparison, whose scripts are not public.
- The paper measured Flashlight 0.3.1 (pre fl::Tensor rewrite, ArrayFire-only era); v0.3.2 is described as the last release before the fl::Tensor breaking changes, and main (0.4.0 in CMakeLists, with new JIT and oneDNN tensor backends) is different code. The vcpkg ports pin the 0.3 branch tip, so vcpkg users get the old API, not the one in the README examples.
- The repo's benchmark tool uses synthetic fl::rand inputs reused every iteration (no data loading), 50 warm-up plus 100 timed updates, and an fl::sync() after each of forward, criterion, backward and optimizer step, so its throughputs are not comparable with the paper's data-loading-inclusive times.
- There is no Python API for the core library: bindings/python now only points to flashlight/text and flashlight/sequence.

## Known shortcomings

- First-party ICML 2022 paper (arXiv 2201.12465) seen only through WebSearch snippets: gains under 10% on most models, TensorFlow faster on VGG16 with 1 GPU, the large ratios only on overhead-bound AlexNet; baselines PyTorch 1.8 and TensorFlow 2.4 from 2021; times include data loading; no PyTorch or TensorFlow comparison scripts or flags in the repo, and flashlight/app/benchmark reports Flashlight-only V100 throughput. Filed under numerics-and-science/autodiff-and-ml-kernels although mined into wave 12. Paper-access retier candidate (B).
- Enricher: the repo's own benchmark Run.cpp runDetr prepends 12 empty target Variables, so HungarianMatcher takes its isEmpty shortcut and the README DETR throughput rows (21.64 img/s FP32) skip set matching; the paper's Table 3 is unaffected but its comparison scripts are not public and the paper measured 0.3.1 before the fl::Tensor rewrite (main is 0.4.0). Margins outside AlexNet are 1.01x-1.18x. main uses C++20 unordered_map::contains despite the C++17 claim; core Python bindings removed; PRs unreviewed since 2025-11 (issue #1185).

## Caveats and trade-offs

SNIPPET ONLY: arxiv.org, ar5iv, proceedings.mlr.press, icml.cc (including the ICML 2022 slides PDF), hgpu.org, liner.com and ai.meta.com were EGRESS_BLOCKED, so the paper PDF was never opened; the table and setup (Flashlight 0.3.1, PyTorch 1.8, TensorFlow 2.4, Intel E5-2698 CPUs, V100-32GB GPUs in a DGX-1) come from WebSearch result excerpts of arXiv 2201.12465, and three separately worded searches (two by the search agent, one by the verifier) returned identical numbers for the rows they showed. The 512 GB RAM and NVLink details were not seen in the verifier's snippets. Peer-reviewed at ICML 2022 (a tier B candidate once the PDF can be read), but written by the Flashlight authors, so first-party. The repo's own benchmark tool (flashlight/app/benchmark: ModelBenchmarker.cpp, Run.cpp, models/AsrTransformer and LmTransformer) reports Flashlight-only V100 training throughput (ViT-Base, ResNet-34/50, DETR, LM and ASR transformers, FP32 and AMP, 1 to 32 GPUs) with no PyTorch or TensorFlow baseline; no AlexNet/VGG16 model and no PyTorch/TensorFlow comparison scripts were found in the repo, so the paper's comparison is not reproducible from public code. Compiler, flags, build options and framework configuration were not seen. The gains are under 10 percent on most rows (VGG16, ResNet-50 1 GPU, BERT-like, ASR, ViT), TensorFlow wins VGG16 on 1 GPU, and the large ratios come from AlexNet, a small, overhead-bound model. Framework versions date from 2021 (PyTorch 1.8, TensorFlow 2.4) and are far behind current releases. Times include data loading, so they are not pure kernel speed. Recent commits are mostly Meta fbcode sync and build fixes (CUDA 13 nvToolsExt fix 2026-09-14), not feature work. The awesome-cpp lead lists the license as BSD; GitHub shows MIT.

Research-oriented C++-only framework (small Python bindings) with a much smaller model and ecosystem than PyTorch or TensorFlow; default tensor backend is ArrayFire with JIT kernel compilation, so it needs ArrayFire plus CUDA, OpenCL or CPU libraries; the fl::Tensor API is marked work in progress with possible API breakage.

## Maintenance

Commits are recent (2026-10-06; CUDA 13 nvToolsExt fix 2026-09-14), but they are automated Meta fbcode syncs and lint or build fixes rather than feature work; the last tagged release is v0.3.2, and issue #1185 (Nov 2025) says PRs go unreviewed. It is MIT-licensed and usable, but expect to fix build problems yourself (C++20 use despite the C++17 claim, outdated NCCL in vcpkg #1186).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Numbers come from the authors' own ICML 2022 paper (arXiv 2201.12465), which could not be opened here (arxiv.org, icml.cc, hgpu.org, liner.com all EGRESS_BLOCKED); WebSearch snippets reproduce the Table 3 rows for AlexNet, VGG16 and ResNet-50 exactly as recorded, plus the setup (Flashlight 0.3.1 vs PyTorch 1.8 and TensorFlow 2.4, 100 iterations forward+backward with data loading, E5-2698 + V100-32GB DGX-1). The repo holds no PyTorch/TensorFlow comparison scripts and no compiler/flags, so not A; peer-reviewed but unread and first-party, so C until the PDF is reached (tier B candidate).
- **Verifier notes:** Confirm at C: numbers match WebSearch snippets of the paper's Table 3 (AlexNet, VGG16, ResNet-50 rows checked; BERT-like, ASR and ViT rows not seen by the verifier), but the PDF was unreachable and the comparison scripts are not in the repo. Shortcomings: first-party paper read via snippets only; gains under 10 percent on most models and TensorFlow faster on VGG16 1 GPU; big ratios only on overhead-bound AlexNet; 2021 framework versions; timings include data loading; no public baseline scripts or flags. Queue for the paper-access retier list (arXiv 2201.12465, ICML 2022 PMLR v162 kahn22a); metadata checked: MIT, 5.5k stars, not a fork, not archived, last commit 2026-10-06 (active). Category autodiff-and-ml-kernels is a wave 8 category, not a wave 12 one.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** paper access and published comparison scripts; enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/flashlight/flashlight>
  - <https://github.com/flashlight/flashlight/commits>
  - <https://github.com/flashlight/flashlight/tree/main/flashlight>
  - <https://github.com/flashlight/flashlight/tree/main/flashlight/app>
  - <https://github.com/flashlight/flashlight/tree/main/flashlight/pkg>
  - <https://github.com/flashlight/flashlight/tree/main/flashlight/app/benchmark>
  - <https://github.com/flashlight/flashlight/tree/main/flashlight/app/benchmark/models>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/app/benchmark/README.md>
- **Sources the enricher read:**
  - <https://github.com/flashlight/flashlight>
  - <https://github.com/flashlight/flashlight/commits>
  - <https://github.com/flashlight/flashlight/releases>
  - <https://github.com/flashlight/flashlight/issues>
  - <https://github.com/flashlight/flashlight/issues?q=is%3Aissue+performance+OR+slow+OR+slower>
  - <https://github.com/flashlight/flashlight/issues/1185>
  - <https://github.com/flashlight/flashlight/issues/1187>
  - <https://github.com/flashlight/flashlight/issues/1183>
  - <https://github.com/flashlight/flashlight/issues/898>
  - <https://github.com/flashlight/flashlight/issues/630>
  - <https://github.com/flashlight/flashlight/issues/328>
  - <https://github.com/flashlight/flashlight/issues/707>
  - <https://github.com/flashlight/flashlight/tree/main/flashlight/fl/tensor/backend>
  - <https://github.com/flashlight/flashlight/tree/main/flashlight/fl/tensor/backend/af>
  - <https://github.com/flashlight/flashlight/tree/main/flashlight/fl/tensor/backend/af/mem>
  - <https://github.com/flashlight/flashlight/tree/main/flashlight/fl/autograd/tensor/backend>
  - <https://github.com/orgs/flashlight/repositories>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/README.md>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/app/benchmark/README.md>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/app/benchmark/Run.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/app/benchmark/ModelBenchmarker.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/app/benchmark/ModelBenchmarker.h>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/app/benchmark/Utils.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/app/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/pkg/vision/criterion/SetCriterion.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/pkg/vision/criterion/Hungarian.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/pkg/vision/models/ViT.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/pkg/vision/nn/VisionTransformer.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/fl/tensor/README.md>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/fl/tensor/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/fl/tensor/backend/af/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/fl/tensor/backend/af/mem/MemoryManagerInstaller.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/fl/tensor/backend/af/mem/CachingMemoryManager.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/fl/tensor/Shape.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/fl/tensor/TensorBase.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/fl/autograd/Variable.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/fl/autograd/tensor/backend/cudnn/Conv2D.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/fl/common/DynamicBenchmark.h>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/flashlight/fl/runtime/DeviceManager.cpp>
  - <https://raw.githubusercontent.com/flashlight/flashlight/HEAD/bindings/python/README.md>
  - <https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/flashlight-cuda/vcpkg.json>
  - <https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/flashlight-cpu/vcpkg.json>
  - <https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/flashlight-cuda/portfile.cmake>
  - https://proceedings.mlr.press/v162/kahn22a/kahn22a.pdf (EGRESS_BLOCKED)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/flashlight/flashlight`) · [data/wave12/enrich/raw/github_com_flashlight_flashlight.json](../../../data/wave12/enrich/raw/github_com_flashlight_flashlight.json) (enrichment confidence 0.6)

</details>
