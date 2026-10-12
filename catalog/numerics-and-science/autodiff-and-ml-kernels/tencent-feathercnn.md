# FeatherCNN

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Small dependency-free ARM CPU CNN inference library; 2017 wiki shows 2-13x lower latency than Caffe+OpenBLAS and Caffe2+Eigen.

| | |
|---|---|
| **Beats** | Caffe2 with Eigen, Caffe with OpenBLAS, Caffe2 with NNPACK, TensorFlow Lite, ARM Compute Library, TVM |
| **Claimed result** | Wiki, Huawei D05 (64 Cortex-A72 cores), best time at any thread count: VGG-16 102 ms vs Caffe+OpenBLAS 1108 ms (10.86x) and Caffe2+Eigen 1310 ms (12.84x); ResNet-50 3.88x and 2.29x; MobileNet 4.03x and 2.65x. The wiki's Speedup column also lists GoogleNet at 13.7x (Caffe+OpenBLAS) and 4.45x (Caffe2+Eigen), but its own timing tables give 822/125 = about 6.6x and 267/125 = about 2.1x (derived from page data). VGG-16 on iPhone 7, 2 cores: 284 ms vs TensorFlow Lite 905 ms in the 2-core column, about 3.2x (derived from page data). Nvidia TX2 VGG-16: 706 ms (2 cores) vs Caffe2+NNPACK 3569 ms (about 5x, derived from page data). |
| **Workload** | End-to-end CNN inference time in ms (VGG-16, GoogleNet, ResNet-50, SqueezeNet, MobileNet, DenseNet-121) on ARM CPUs: Huawei D05 (64 Cortex-A72), iPhone 7, RK3399, Nvidia TX2, Raspberry Pi 3. |
| **Metric** | latency |
| **Hardware** | Samsung S8 (Snapdragon 835), iPhone 7 (A10), Huawei D05 (2x Hi1616, 64 Cortex-A72), Phytium FT1500A/16, RK3399, Raspberry Pi 3B, Nvidia TX2 |
| **Adoption** | 1.2k stars |
| **Last commit** | 2019-09-24 |
| **Links** | [repository](https://github.com/Tencent/FeatherCNN) · [benchmark](https://github.com/Tencent/FeatherCNN/wikis/Benchmarks) |

## Verdict

The first-party wiki reports whole-network fp32 inference time on ARM CPUs measured in late 2017. On a 64-core Huawei D05 (Cortex-A72), best time at any thread count gives VGG-16 102 ms vs 1108 ms for Caffe+OpenBLAS and 1310 ms for Caffe2+Eigen. On an iPhone 7 with 2 cores, VGG-16 runs in 284 ms vs 905 ms for TensorFlow Lite, and on an Nvidia TX2 in 706 ms vs 3569 ms for Caffe2+NNPACK. No compiler, flags or benchmark harness are published, and the wiki's own GoogleNet speedup column (13.7x) disagrees with its timing tables (about 6.6x, derived from page data).

## Use it when

- Reading the Winograd F(6x6,3x3) and NEON GEMM kernels (src/booster/arm) as BSD-3 reference code for your own ARM convolution work.
- Float32 inference of a classic Caffe CNN built only from conv, depthwise conv, pooling, ReLU, BN/Scale, inner product, eltwise, concat and softmax on an ARMv8 phone or board, where you can accept an unmaintained library.
- VGG-style networks dominated by 3x3 stride-1 convolutions, where the Winograd path does most of the work (the largest gains on the wiki are for VGG-16).

## Skip it when

- Any new production deployment: there have been no commits since 2019-09-24, open issues (segfault on SqueezeNet, unregistered Deconvolution layer, build failures) have no maintainer replies, and MNN, ncnn or XNNPACK cover the same ground and are maintained.
- Models that need ops outside the 13 registered layers (no Deconvolution, Reshape, Permute, detection or SSD layers), partial group convolution, or anything other than fp32 (no int8 or fp16).
- Choosing on the wiki numbers: they were measured on the pre-April-2019 code (the .feathermodel / InitFromPath API the README still describes) against Caffe, Caffe2 and TFLite builds from late 2017, and the code was rewritten on master after that.
- Multi-core inference through the public API: on master Net() hard-codes one thread and exposes no setter, unlike the per-thread-count tables on the wiki.

## How it is fast

3x3 stride-1 convolutions use Winograd F(6x6,3x3) (F(2x2,3x3) also exists), with the transformed tiles multiplied by a batched GEMM the TPDS paper calls TensorGEMM. Other convolutions use im2col plus a hand-written NEON SGEMM (4x12 and 8x12 register-blocked micro-kernels using vfmaq_f32), and depthwise layers get a dedicated kernel. A ReLU that follows a convolution is fused into it, and activations come from a shared memory pool.

## Compared with alternatives

Pick MNN over this for any real ARM deployment: it is maintained, supports far more ops and has its own peer-reviewed (MLSys 2020) comparison against TFLite and ncnn. FeatherCNN is worth taking over NNPACK only as compact BSD-3 reference code for Winograd F(6x6,3x3) with a batched GEMM, not as a runtime.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the library (OpenMP optional, GCD on iOS); the Caffe model converter described in the README needs protobuf |
| **Minimum toolchain** | C++11, CMake 2.8; Android NDK (android-21 for arm64-v8a, android-16 for armeabi-v7a) or the Xcode iOS SDK |
| **Platforms** | aarch64 and armv7 with NEON (Android, iOS, Linux); x86-64 with AVX2 via the BOOSTER_AVX backend (built with -march=core-avx2) |
| **Thread safety** | not documented; a Net owns mutable layer buffers and a shared memory pool, so treat one Net as single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- The README is stale: it documents Net(num_threads), InitFromPath(.feathermodel) and Forward(float\*), while master's net.h has Net(), LoadParam/LoadWeights and ncnn::Mat inputs (the param parser comes from bundled ncnn code).
- The top-level CMakeLists adds -Ofast and -ffast-math globally, so results may differ slightly from strict IEEE fp32.
- ConvLayer::Forward on master calls printf("thread num =%d") on every convolution, which is debug output left in the hot path.
- build_scripts/build_android.sh passes -DCOMPILE_OPENCL=1, which adds src/booster/cl, but that directory is not in master (its CMakeLists.txt returns 404), so expect to edit the script before the Android build works.

## Known shortcomings

- Wiki speedup column does not match its own tables (GoogleNet 13.7x listed vs \~6.6x from the timings); BSD-3-Clause only in file headers, no LICENSE file; TPDS 2020 paper unreadable here (possible B on retier).
- Master was rewritten 2019-04-28; wiki numbers are from 2017 pre-rewrite code (the .feathermodel API the README still documents); master Net() hard-codes 1 thread with no setter, so the wiki's multithread tables cannot be reproduced through the public API; debug printf on every conv Forward; -Ofast -ffast-math global; build_android.sh enables OpenCL but src/booster/cl is missing; SqueezeNet segfault #33 unanswered.

## Caveats and trade-offs

First-party wiki numbers; the D05 section says the tests finished at the end of 2017 and 'performance may change a lot after that time'. No benchmark code is linked and compiler and flags are not stated. The wiki's Speedup column does not match its own tables: GoogleNet is overstated (13.7x listed vs about 6.6x derived; 4.45x vs about 2.1x), while SqueezeNet and DenseNet are understated. There is no top-level LICENSE file (the README badge links a 404), but the source files carry BSD-3-Clause headers (Copyright 2019 THL A29 Limited / Tencent), including the bundled ncnn code. Baselines are Caffe2+Eigen, Caffe+OpenBLAS, TFLite and ACL as of late 2017.

Loads Caffe models converted to its own .feathermodel format; targets ARM CPUs on iOS, Android and embedded or ARM-server Linux; small library with no external dependencies.

## Maintenance

Abandoned since 2019-09-24, and the README does not match the rewritten master code. BSD-3-Clause source headers make the ARM kernels copyable, but treat it as reference code rather than a runtime to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The first-party wiki gives inference-time tables against Caffe+OpenBLAS, Caffe2+Eigen, Caffe2+NNPACK, TensorFlow Lite and ACL on named ARM devices, but it links no benchmark code and states no compiler or flags, so it is C. The README cites a peer-reviewed IEEE TPDS paper (DOI 10.1109/TPDS.2019.2939785) that may justify B, but every host serving it was blocked here and it could not be opened.
- **Verifier notes:** Metadata: 1.2k stars, 275 forks, 19 commits on master, last commit 2019-09-24, not archived; abandoned is correct. Search snippets (paper not opened) say the TPDS 31(3):580-594 abstract reports VGG-16 on a 64-core ARM server 48x/14x/12x faster than Caffe+OpenBLAS/Caffe2+Eigen/NNPACK and 3.19x faster than TFLite on iPhone 7 plus. Candidate for a retier check to B. Shortcoming to record: the wiki's speedup column is internally inconsistent (GoogleNet overstated about 2x).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Tencent/FeatherCNN>
  - <https://github.com/Tencent/FeatherCNN/commits>
  - <https://github.com/Tencent/FeatherCNN/blob/master/LICENSE>
  - <https://github.com/Tencent/FeatherCNN/tree/master/src>
  - <https://github.com/Tencent/FeatherCNN/wiki/Benchmarks>
  - <https://raw.githubusercontent.com/wiki/Tencent/FeatherCNN/Benchmarks.md>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/HEAD/README.md>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/net.cpp>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/ncnn/paramdict.cpp>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/layer.h>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/HEAD/README.md>
  - <https://raw.githubusercontent.com/wiki/Tencent/FeatherCNN/Benchmarks.md>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/net.h>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/net.cpp>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/layer.h>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/rt_param.h>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/layer_factory.cpp>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/layers/conv_layer.h>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/booster/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/booster/arm/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/booster/arm/booster.cpp>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/booster/arm/sgemm.cpp>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/booster/arm/winograd_kernels_F63.cpp>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/booster/include/booster/booster.h>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/booster/avx/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/src/booster/cl/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/build_scripts/build_android.sh>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/build_scripts/build_ios.sh>
  - <https://raw.githubusercontent.com/Tencent/FeatherCNN/master/build_scripts/build_linux_avx.sh>
  - <https://github.com/Tencent/FeatherCNN/tree/master/src>
  - <https://github.com/Tencent/FeatherCNN/tree/master/src/booster>
  - <https://github.com/Tencent/FeatherCNN/tree/master/src/booster/arm>
  - <https://github.com/Tencent/FeatherCNN/commits/master>
  - <https://github.com/Tencent/FeatherCNN/issues?q=is%3Aissue>
  - <https://github.com/Tencent/FeatherCNN/issues/31>
  - <https://github.com/Tencent/FeatherCNN/issues/33>
  - <https://github.com/Tencent/FeatherCNN/issues/50>
  - https://hpcc.siat.ac.cn/jintao/jintao/paper/tpds_feathercnn.pdf (EGRESS_BLOCKED; paper content known only from search snippets)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tencent/feathercnn`) · [data/wave8/enrich/raw/github_com_tencent_feathercnn.json](../../../data/wave8/enrich/raw/github_com_tencent_feathercnn.json) (enrichment confidence 0.8)

</details>
