# Dlib (dnn module, CUDA/cuDNN deep learning API)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> dlib's dnn module: C++ type-defined CNN training and inference on cuDNN; 2016 author claim of about 1.6x Caffe's speed.

| | |
|---|---|
| **Beats** | Caffe (GPU, cuDNN) |
| **Claimed result** | Fast mode about 1.6x faster than Caffe at about 1.5x the VRAM; low-VRAM mode about 0.85x Caffe's speed at about half the memory (author's blog, June 2016; snippet only) |
| **Workload** | Deep neural network speed and GPU memory against Caffe on a GPU with dlib built on cuDNN v5 (author's June 2016 blog post 'A clean C++11 deep learning API', snippet only); the snippets give no network, batch size, GPU model for the comparison, or whether training or inference was timed. |
| **Metric** | throughput |
| **Adoption** | 14.5k stars, 3.4k forks, 8,382 commits |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/davisking/dlib) · [benchmark](https://blog.dlib.net/2016/06/a-clean-c11-deep-learning-api.html) |

## Verdict

The only external comparison is the author's June 2016 blog post for dlib 19.0 on cuDNN v5, seen through search snippets because blog.dlib.net does not resolve here. It says fast mode was about 1.6x Caffe's speed at about 1.5x the VRAM, and low-VRAM mode about 0.85x the speed at half the VRAM. The snippets name no network, GPU, Caffe version, batch size or whether training or inference was timed, and the repo has no benchmark code for it.

## Use it when

- C++-only deployments that must train or run CNNs without a Python runtime and want one BSL-1.0 library that also covers image processing and classic ML.
- Using dlib's own pretrained models (ResNet face recognition, CNN+MMOD face and vehicle detectors) where dlib is already the inference engine.
- Small to medium convolutional networks (LeNet to ResNet-34 scale) where a compile-time network definition is acceptable.
- Projects that need one code base to run on CPU-only machines and on NVIDIA GPUs.

## Skip it when

- Throughput-sensitive training on current GPUs: every tensor is FP32 NCHW (CUDNN_DATA_FLOAT), there is no FP16/BF16 mixed precision, and since PR #3127 (December 2025) convolutions force CUDNN_FMA_MATH, which turns off TF32 Tensor Cores on Ampere and newer GPUs.
- Choosing a framework on speed today: the only cross-framework number is the 2016 Caffe claim; no benchmark against PyTorch, TensorFlow or ONNX Runtime exists in the repo.
- Dynamic graphs, transformer-scale models or research that needs autograd over arbitrary code: networks are static C++ types and a new layer needs hand-written forward and backward passes.
- Very deep networks where build time matters: compile time of DNN definitions is a known pain point (issue #2638), and nets are recompiled whenever the type changes.
- Embedded GPUs: issue #2766 (slow performance with CUDA on Jetson Nano) is still open.

## How it is fast

It is a thin layer over cuDNN and cuBLAS with the whole network graph fixed at compile time, so there is no runtime graph interpreter. Convolution algorithms are benchmarked with cudnnFindConvolution\*Algorithm and cached; set_dnn_prefer_fastest_algorithms() (the default) takes the fastest algorithm regardless of workspace, while set_dnn_prefer_smallest_algorithms() takes the one with the least workspace, which is the fast mode versus low-VRAM mode trade-off in the 2016 post. Tensors keep their GPU allocation when shrunk (std::vector-like), workspaces are shared per device, and fuse_layers can fold affine and ReLU layers into the preceding convolution.

## Compared with alternatives

Caffe (the baseline, also catalogued) is unmaintained, and KANN is a small CPU-only C library; pick dlib's dnn for a maintained, self-contained C++ library with CPU and cuDNN back ends and pretrained vision models. Pick PyTorch, Flashlight or ONNX Runtime when GPU training or inference throughput is the goal.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none required; optional CUDA toolkit with cuDNN, cuBLAS, cuRAND and cuSOLVER for GPU; optional BLAS/LAPACK (OpenBLAS or Intel MKL) for CPU speed |
| **Minimum toolchain** | C++17 and CMake 3.10+ on master (release 20.0 needs C++14); GPU builds need a CUDA toolkit with cuDNN (code paths for cuDNN 5 through 9) |
| **Platforms** | any platform for CPU; NVIDIA GPUs through CUDA (CMake 3.24+ defaults to the native GPU architecture) |
| **Thread safety** | tensor objects are documented as not thread-safe; cuDNN handles, descriptors and the convolution-algorithm cache are thread_local, so use one network instance per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- If CMake finds CUDA but not cuDNN, it prints 'DID NOT FIND CUDNN' and 'DLIB WILL NOT USE CUDA' and builds a CPU-only dlib without failing, so a GPU build can silently run on the CPU.
- PR #3127 (merged 2025-12-28, to make GPU and CPU test results agree) sets CUDNN_FMA_MATH on every convolution; a reviewer pointed out the lost Tensor Core performance and suggested CUDNN_TENSOR_OP_MATH_ALLOW_CONVERSION, but that is not merged and no speed impact was measured.
- By default, the cuDNN algorithm chosen for the first input of a given stride, padding and filter size is reused for later input shapes, even when it needs much more memory for larger inputs; set_dnn_choose_algorithms_per_input_shape(true) (PR #3161, October 2026) benchmarks each shape instead. The 19.5 release notes say better workspace management means set_dnn_prefer_smallest_algorithms() should no longer be needed, so the 2016 VRAM trade-off no longer describes current code.
- Speed depends on cuDNN behaviour: moving the convolution bias into one cuDNN call made vehicle-detector inference slower (issue #2655, 36.2 ms on 19.22 vs about 39.8 ms on master, GTX 1650), and PR #2656 reverted it to a separate bias call.

## Known shortcomings

- Speed claim is the author's own June 2016 blog post (snippet only, blog.dlib.net blocked): fast mode about 1.6x Caffe at 1.5x VRAM, low-VRAM mode 0.85x Caffe at half the VRAM; no network, GPU, batch size or flags; Caffe and cuDNN v5 baselines out of date; the repo holds no Caffe benchmark. Category autodiff-and-ml-kernels (wave 8) by override.
- Enricher: FP32-only NCHW; PR #3127 (2025-12-28) forces CUDNN_FMA_MATH, so no TF32 Tensor Cores on Ampere and later; a missing cuDNN silently gives a CPU-only build; the 19.5 release notes make the 2016 VRAM trade-off obsolete; bias-fusion regression #2655 reverted.

## Caveats and trade-offs

Snippet only: blog.dlib.net could not be fetched (getaddrinfo ENOTFOUND), so the numbers (fast mode about 1.6x Caffe's speed at about 1.5x the VRAM; low-VRAM mode about 0.85x Caffe's speed at about half the VRAM) come from WebSearch result text for the post https://blog.dlib.net/2016/06/a-clean-c11-deep-learning-api.html; the network, GPU, Caffe version, batch size and flags are unverified. A snippet mentions a ResNet34 model trained in about two weeks on a single Titan X GPU, but it is not clear that this GPU was the one used for the Caffe comparison. First-party author claim from 2016 against 2016-era Caffe and cuDNN v5; both have changed greatly since, and Caffe is no longer a current incumbent. The repo has no benchmark against Caffe or any other framework (README.md, docs/docs/ml.xml and docs/docs/release_notes.xml were checked); the release notes contain only dlib-versus-dlib speedups (CNN+MMOD detectors 2.5x faster) and a tools/convert_dlib_nets_to_caffe converter, so the comparison could be reproduced but is not checked in. Third-party reports in dlib GitHub discussions (video reading against OpenCV cv::VideoCapture) are mixed and trace mostly to thread-count defaults, so they do not support a speed win. The awesome-cpp baselines guess (system I/O or threading) was wrong for this project.

Fast mode trades about 1.5x more VRAM for speed; a low-VRAM mode halves memory at about 0.85x of Caffe's speed. Dlib is a broad toolkit (ML, imaging, optimization, networking) and the dnn module is one component of it.

## Maintenance

Actively maintained (cuDNN binding commits through October 2026) and BSL-1.0, so it is easy to adopt, but the Caffe speed claim is ten years old, measured against a dead baseline, and predates current FP32-only, TF32-disabled code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The only external-baseline numbers are the author's own June 2016 blog post ('A clean C++11 deep learning API'), seen through WebSearch snippets only (blog.dlib.net fails DNS here); it gives ratios against Caffe with no network, batch size, GPU, Caffe version or flags tied to the comparison, and the dlib repo carries no Caffe benchmark code. First-party numbers without methodology are C.
- **Verifier notes:** Numbers match the WebSearch snippets of the specific post (benchmark_url corrected from the month archive to the post); tier C as a snippet-only, first-party, 2016 claim with no methodology. BSL-1.0, 14.5k stars, not a fork, last commit 2026-10-04 ('fix bug in unit test'), active. Category is a wave 8 category (autodiff-and-ml-kernels, domain numerics-and-science) although this record came from a wave 11 seed lead filed under filesystems-and-io; the orchestrator should keep the ML category or record a category override, since dlib has nothing in runtime-and-systems and is not already listed in wave 8.
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-57 (wave 11); enricher w11 pair-020
- **Pages the verifier opened:**
  - <https://github.com/davisking/dlib>
  - <https://github.com/davisking/dlib/commits>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/README.md>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/docs/docs/ml.xml>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/docs/docs/release_notes.xml>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/docs/docs/old_release_notes.xml>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/README.md>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/docs/docs/ml.xml>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/docs/docs/release_notes.xml>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/dlib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/dlib/dnn.h>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/dlib/dnn/core.h>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/dlib/dnn/core_abstract.h>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/dlib/cuda/cudnn_dlibapi.cpp>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/dlib/cuda/cuda_utils.h>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/dlib/cuda/tensor_tools.h>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/dlib/cuda/tensor_abstract.h>
  - <https://raw.githubusercontent.com/davisking/dlib/HEAD/examples/dnn_introduction_ex.cpp>
  - <https://github.com/davisking/dlib/commits/master/dlib/cuda/cudnn_dlibapi.cpp>
  - <https://github.com/davisking/dlib/pull/3127>
  - <https://github.com/davisking/dlib/issues?q=is%3Aissue+dnn+slow>
  - <https://github.com/davisking/dlib/issues/2655>
  - https://blog.dlib.net/2016/06/a-clean-c11-deep-learning-api.html (fetch failed: getaddrinfo ENOTFOUND; WebSearch snippet only)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/davisking/dlib`) · [data/wave11/enrich/raw/github_com_davisking_dlib.json](../../../data/wave11/enrich/raw/github_com_davisking_dlib.json) (enrichment confidence 0.7)

</details>
