# Caffe

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> Berkeley's C++/CUDA layer-based deep learning framework; its native im2col+cuBLAS convolutions edged Torch-7's native kernels by 3-7% in 2015.

| | |
|---|---|
| **Beats** | Torch-7 native CUDA convolution (cunn SpatialConvolutionMM) |
| **Claimed result** | Caffe (native ConvolutionLayer) vs Torch-7 (native SpatialConvolutionMM), total ms per forward+backward pass: AlexNet 324 vs 342 (about 1.06x faster, derived from page data), Overfeat-fast 823 vs 878 (about 1.07x, derived from page data), OxfordNet Model-A 1068 vs 1105 (about 1.03x, derived from page data). Also well ahead of the OpenCL ports in the table (CL-nn 963 ms and Caffe-CLGreenTea 1442 ms on AlexNet). |
| **Workload** | Time for a full forward plus backward pass of ImageNet-winner convnets averaged over 10 runs on one NVIDIA Titan X, using each framework's native (non-cuDNN) convolution kernel: AlexNet 128x3x224x224, Overfeat-fast 128x3x231x231, OxfordNet Model-A 64x3x224x224. |
| **Metric** | throughput |
| **Hardware** | 6-core Intel Core i7-5930K CPU @ 3.50GHz + NVIDIA Titan X, Ubuntu 14.04 x86_64 |
| **Adoption** | 34.6k stars |
| **Last commit** | 2020-02-13 |
| **Links** | [repository](https://github.com/BVLC/caffe) · [benchmark](https://github.com/soumith/convnet-benchmarks) |

## Verdict

In soumith/convnet-benchmarks (i7-5930K plus a Titan X, Ubuntu 14.04, compiler, CUDA and cuBLAS versions not stated), Caffe's native non-cuDNN convolution took 324, 823 and 1068 ms for one forward plus backward pass of AlexNet (batch 128), Overfeat-fast (128) and OxfordNet-A (64), against Torch-7's native SpatialConvolutionMM at 342, 878 and 1105 ms, about 1.03-1.07x (derived from page data). The two rows come from runs on different dates, and Caffe did extra conv1 input-gradient work that Torch skipped.

## Use it when

- Maintaining or reproducing a legacy Caffe model (Model Zoo prototxt/caffemodel) where re-implementing it elsewhere is not justified.
- Older NVIDIA GPU stacks (CUDA up to 10.x, cuDNN up to 7) or CPU-only boxes where its BLAS (ATLAS, OpenBLAS, MKL) path is enough.
- Teaching or studying a compact, readable im2col + GEMM CNN implementation in C++/CUDA.
- Deployments that already standardised on Caffe tooling (prototxt nets, LMDB/LevelDB data layers) and cannot take a new framework.

## Skip it when

- Any new project: the same benchmark tables put Caffe native far behind TensorFlow and cuDNN R4 (81 ms vs 324 ms on AlexNet) and on GoogleNet V1 at 1935 ms vs TensorFlow 445 ms; PyTorch or MXNet are the maintained choices.
- Current CUDA/cuDNN toolchains: master calls cudnnGetConvolution\*Algorithm with SPECIFY_WORKSPACE_LIMIT preferences that cuDNN 8 removed, so USE_CUDNN builds fail (issues #6970 and #6982 still open); Makefile.config.example's default arch list includes sm_20/sm_21, which CUDA 9+ rejects.
- Dynamic graphs, autodiff of arbitrary code, mixed precision or modern attention/transformer layers: none are in master.
- Projects that need upstream fixes or security updates: last commit 2020-02-13, 898 open issues and 277 open PRs.

## How it is fast

The native ConvolutionLayer lowers each image to a column matrix with im2col (skipped for 1x1 kernels) and runs one cuBLAS/BLAS GEMM per image and group, so convolution speed is essentially GEMM speed; backward does a second GEMM for the weight gradient and col2im for the data gradient. Blobs keep synchronized CPU/GPU copies so data moves only when a layer on the other device touches it. Built with USE_CUDNN, the layer factory silently swaps every convolution (except dilated ones) to the cuDNN engine, which is where Caffe's later speed came from.

## Compared with alternatives

Pick Caffe over PyTorch, MXNet or Flashlight only to run or reproduce existing Caffe models on an older CUDA/cuDNN stack; for raw convolution speed, fbfft and Nervana neon beat it in the same tables, and FeatherCNN beats Caffe+OpenBLAS on ARM CPUs.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Boost &gt;= 1.55, protobuf, glog, gflags, HDF5, a BLAS (ATLAS default, OpenBLAS or MKL); CUDA for GPU mode; optional cuDNN (v7 per docs), OpenCV &gt;= 2.4, LevelDB, LMDB; boost.python and numpy for pycaffe |
| **Minimum toolchain** | CMake 2.8.7 or the Makefile build; nvcc from CUDA (comment out sm_20/sm_21 for CUDA 9+); cuDNN 7 at most for USE_CUDNN (cuDNN 8 build breaks); no -std flag pinned in CMakeLists; docs list Ubuntu 12.04-16.04 and OS X 10.8-10.11 |
| **Platforms** | x86-64 Linux and macOS; NVIDIA GPUs (compute capability &gt;= 3.0 recommended) or CPU_ONLY builds; OpenCL, Intel CPU and Windows variants live on separate branches |
| **Thread safety** | The global Caffe context (CPU/GPU mode, device, cuBLAS/cuRAND handles) is a thread-local singleton (common.hpp); sharing one Net across threads is not documented as safe |
| **Drop-in for the baseline** | no |

## Gotchas

- Engine choice is a build flag: with USE_CUDNN every Convolution layer uses cuDNN unless engine: CAFFE is set per layer (layer_factory.cpp), so 'Caffe' timings mean different kernels depending on Makefile.config; the cuDNN path also caps algorithm workspace at 8 MB (cudnn_conv_layer.cpp), which can rule out the fastest algorithms.
- Native convolution loops over the batch (one im2col and one GEMM per image, conv_layer.cu) with a per-layer column buffer, so throughput depends heavily on the BLAS and on batch size; backward redoes im2col for the weight gradient.
- Harness asymmetry in soumith/convnet-benchmarks: the Caffe prototxts set force_backward: true, so Caffe also computes the gradient with respect to the input image in conv1, while the current Torch net files set features:get(1).gradInput = nil and skip it. This works against Caffe, so it does not inflate the 3-7% margin, but the two rows are not like-for-like work.
- The README's Caffe rows cannot be traced to the checked-in logs: caffe/output_alexnet.log reports Average Forward-Backward 128.729 ms against the README's 324 ms, with no build configuration (cuDNN on or off, CUDA version) recorded, and the Torch row comes from a May 2015 log, so the comparison mixes runs from different dates. The log also prints 'does not need backward computation' for every layer because the net has no loss; force_backward overrides this after the message.

## Known shortcomings

- convnet-benchmarks: only 3-7% faster than Torch-7 native and far behind cuDNN, TensorFlow and neon. The repo's checked-in Caffe log (128.7 ms AlexNet) does not match the README row (324 ms). Compiler and flags not given. No commits since 2020-02-13.
- Enricher: convnet-benchmarks' Caffe prototxts set force_backward: true, so Caffe also computes the conv1 input gradient while the Torch nets skip it (gradInput = nil); the asymmetry works against Caffe, so the 3-7% margin is not inflated but the rows are not the same work. README rows do not match the checked-in logs (128.729 vs 324 ms). The cuDNN 8 build is broken (#6970, #6982 open) and the default sm_20 arch fails on CUDA 9+.

## Caveats and trade-offs

Margin over Torch-7 native is only 3 to 7 percent, and both are im2col + cuBLAS GEMM fallback kernels (Torch's SpatialConvolutionMM follows the same approach), so the gap is within what separate runs on different dates can produce. The README Caffe rows cannot be traced to the checked-in logs: caffe/output_alexnet.log, output_overfeat.log, output_vgg_a.log and output_googlenet.log (dated Feb 28, build configuration not recorded) report Average Forward-Backward 128.7, 430.1, 680.2 and 484.7 ms, far below the README's Caffe rows of 324, 823, 1068 and 1935 ms, while the Torch nn row matches torch7/imagenet_winners/output_raw.log (339.72 ms, a May 2015 run); so the Caffe-vs-Torch comparison mixes runs from different dates. The same tables show Caffe (native) well behind TensorFlow (81 ms on AlexNet vs 324), cuDNN R4 through Torch bindings (81 ms), Nervana neon (87 ms), fbfft (104 ms), Chainer (177 ms) and cuda-convnet2 (177 ms), and on GoogleNet V1 Caffe is at 1935 ms against TensorFlow 445 ms, so Caffe is not faster than the modern baselines (TensorFlow, PyTorch, cuDNN). The README notes Caffe (native) and Torch (native) are only the default fallback kernels and that cuDNN can also be used through Caffe bindings; caffe/install.sh builds from Makefile.config.example with cuDNN disabled but states no compiler, flags or CUDA version. Benchmark is 2015-2016 era (cuDNN R2/R4, Titan X); Caffe has had no commit since 2020-02-13. The project's own paper (arXiv 1408.5093, 'over 40 million images a day on a K40', snippet only) was not reachable here (arxiv.org blocked) and gives no baseline numbers in the snippet.

Layer-based C++/CUDA framework with prototxt model definitions and a Python/MATLAB interface; cuDNN can be plugged in but the numbers above use the default native kernels.

## Maintenance

Abandoned (last commit 2020-02-13, not archived, cuDNN 8+ builds broken). It is BSD-2-Clause and copyable, but large and dependency-heavy, so use it only for legacy models.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** soumith/convnet-benchmarks is a well-known independent third-party suite with public scripts (caffe/install.sh, caffe/run_imagenet.sh, torch7/imagenet_winners/benchmark.lua) and states CPU model plus GPU (i7-5930K + Titan X), and its README tables show Caffe native ahead of Torch-7 native SpatialConvolutionMM on AlexNet 324 vs 342 ms, Overfeat 823 vs 878 ms and OxfordNet-A 1068 vs 1105 ms; compiler, flags and CUDA version are not stated, so not A.
- **Verifier notes:** Numbers match the convnet-benchmarks README exactly; entry is real but marginal (3-7% over Torch-7 native, far slower than cuDNN/TensorFlow/neon). Shortcomings: README Caffe rows disagree with the repo's own checked-in Caffe logs (128.7 ms AlexNet vs 324 in the table), compiler/flags unstated, 2015-2016 hardware, abandoned since 2020-02-13. Metadata (BSD-2-Clause, 34.6k stars, last commit 2020-02-13, not archived) confirmed.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** convnet-benchmarks README (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/soumith/convnet-benchmarks>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/HEAD/README.md>
  - <https://github.com/soumith/convnet-benchmarks/tree/master/caffe>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/caffe/install.sh>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/caffe/output_alexnet.log>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/caffe/output_overfeat.log>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/caffe/output_vgg_a.log>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/caffe/output_googlenet.log>
  - <https://github.com/soumith/convnet-benchmarks/tree/master/torch7/imagenet_winners>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/torch7/imagenet_winners/output.log>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/torch7/imagenet_winners/output_raw.log>
  - <https://github.com/BVLC/caffe>
  - <https://github.com/BVLC/caffe/commits/master>
  - <https://raw.githubusercontent.com/BVLC/caffe/HEAD/README.md>
  - <https://raw.githubusercontent.com/BVLC/caffe/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/BVLC/caffe>
  - <https://github.com/BVLC/caffe/commits/master>
  - <https://github.com/BVLC/caffe/issues?q=is%3Aissue+cudnn+8>
  - <https://github.com/BVLC/caffe/issues/6970>
  - <https://raw.githubusercontent.com/BVLC/caffe/master/README.md>
  - <https://raw.githubusercontent.com/BVLC/caffe/master/Makefile.config.example>
  - <https://raw.githubusercontent.com/BVLC/caffe/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/BVLC/caffe/master/cmake/Dependencies.cmake>
  - <https://raw.githubusercontent.com/BVLC/caffe/master/docs/installation.md>
  - <https://raw.githubusercontent.com/BVLC/caffe/master/src/caffe/layers/conv_layer.cu>
  - <https://raw.githubusercontent.com/BVLC/caffe/master/src/caffe/layers/base_conv_layer.cpp>
  - <https://raw.githubusercontent.com/BVLC/caffe/master/src/caffe/layers/cudnn_conv_layer.cpp>
  - <https://raw.githubusercontent.com/BVLC/caffe/master/src/caffe/layer_factory.cpp>
  - <https://raw.githubusercontent.com/BVLC/caffe/master/src/caffe/net.cpp>
  - <https://raw.githubusercontent.com/BVLC/caffe/master/include/caffe/common.hpp>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/caffe/install.sh>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/caffe/run_imagenet.sh>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/caffe/output_alexnet.log>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/caffe/imagenet_winners/alexnet.prototxt>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/caffe/imagenet_winners/overfeat.prototxt>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/caffe/imagenet_winners/vgg_a.prototxt>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/torch7/imagenet_winners/benchmark.lua>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/torch7/imagenet_winners/output_raw.log>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/torch7/imagenet_winners/alexnet.lua>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/torch7/imagenet_winners/overfeat.lua>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/torch7/imagenet_winners/vgg_a.lua>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/torch7/imagenet_winners/googlenet.lua>
  - <https://raw.githubusercontent.com/torch/nn/master/SpatialConvolutionMM.lua>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/bvlc/caffe`) · [data/wave8/enrich/raw/github_com_bvlc_caffe.json](../../../data/wave8/enrich/raw/github_com_bvlc_caffe.json) (enrichment confidence 0.75)

</details>
