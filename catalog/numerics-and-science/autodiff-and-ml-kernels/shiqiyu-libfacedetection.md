# libfacedetection (Highway-optimized facedetect_hw_cnn and Rust crate)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Dependency-free YuNet CNN face detector; its 2026 Highway build is 2.8-3.9x faster single-thread than the project's own AVX2 original.

| | |
|---|---|
| **Beats** | libfacedetection original C++ implementation (facedetect_cnn, AVX2 build with _ENABLE_AVX2) from the same repository |
| **Claimed result** | Highway path vs the original AVX2 build: 2.8-3.9x (33.42 ms to 8.48 ms at 640x480 derived); the 6.4x/6.9x rows (269.72 vs 38.85 ms at 1280x960) run the original without _ENABLE_AVX2. |
| **Workload** | CNN (YuNet) face detection on the repo's images/cnnresult.png resized to 640x480, 320x240, 160x120 and 128x96, 128 iterations after 5 warmups, single thread and 28 external caller threads. |
| **Metric** | latency and throughput (ms per image / FPS) |
| **Hardware** | Intel Core i7-14700KF, 20 cores / 28 logical processors, Windows, max clock 3400 MHz as reported by Windows |
| **Compiler and flags** | MSVC 19.40.33821.0 (Visual Studio 17 2022), CMake Release config. Highway build per COMPILE.md 'AVX2 x86 hybrid': -DFDT_HW_X86_ARCH=AVX2 -DFDT_HW_ENABLE_HYBRID_CEILING=ON -DFDT_HW_ENABLE_INTRINSICS_COMPARE=ON, Highway 1.3.0; highway/CMakeLists.txt then compiles the Highway kernels with /arch:AVX2 /W4 /permissive- and compiles the original src/facedetectcnn.cpp into the same fdt_hw_resolution_benchmark executable with _ENABLE_AVX2 and /arch:AVX2 (no OpenMP in this build). Rust 1.95.0 release profile with runtime AVX2 dispatch. Benchmark: highway/benchmark/hw_resolution_benchmark.cpp, command fdt_hw_resolution_benchmark.exe images\cnnresult.png 128 28. |
| **Adoption** | 12.8k stars, 3.0k forks |
| **Last commit** | 2026-06-28 |
| **Links** | [repository](https://github.com/ShiqiYu/libfacedetection) · [benchmark](https://github.com/ShiqiYu/libfacedetection) |

## Verdict

First-party, same-binary benchmark (MSVC 19.40 Release, Highway 1.3.0, Intel Core i7-14700KF, cnnresult.png resized with OpenCV, 128 iterations after 5 warm-ups): the Highway AVX2 hybrid build takes 8.48/2.14/0.53/0.32 ms versus 33.42/7.70/1.49/0.88 ms for the original AVX2 build at 640x480/320x240/160x120/128x96 (about 3.9x to 2.8x), and 7.7x versus the original's non-SIMD build at 640x480. The 28-thread rows (1.9x at 640x480) include thread-creation overhead, and the Rust crate's 4.1x comes from a separate Rust harness.

## Use it when

- CPU-only face detection on x86-64 where you build per instruction set (AVX2 hybrid is the fastest measured build: 8.48 ms at 640x480, 0.32 ms at 128x96 single-thread on an i7-14700KF).
- Small-input real-time pipelines (320x240 or smaller) that need sub-millisecond to \~2 ms detection without a general inference engine.
- Many concurrent camera streams handled by calling facedetect_hw_cnn from several threads, one result buffer per thread.
- Existing facedetect_cnn users who want a near drop-in speedup: same arguments, same result-buffer layout, same post-processing thresholds (0.45/0.2, top-k 1000/512).
- Rust projects that want a self-contained detector with runtime AVX2 dispatch and a scalar fallback (as a git dependency; see gotchas).

## Skip it when

- ARM or Apple Silicon: the Highway version has not been tested on ARM, the published ARM numbers are for the original on a Raspberry Pi 4, and issue #376 reports the original's NEON path being ineffective on ARMv8-A.
- One binary for mixed x86 fleets: Highway static targets with no runtime dispatch, so an AVX2 build requires AVX2+FMA CPUs; AVX-512 builds compile but were never measured.
- Choosing between detectors or runtimes: there is no comparison against OpenCV FaceDetectorYN (same YuNet model), ncnn, MNN, OpenVINO, dlib or RetinaFace, so the gain over running YuNet in an existing engine is unknown.
- Accuracy-critical or tiny-face workloads: YuNet scores AP_easy 0.887, AP_medium 0.871, AP_hard 0.768 on WIDER Face (README), with a minimum face size of about 10x10.
- GCC or Clang builds from before 2026-06-28: AVX2+ targets segfaulted in five Highway kernels that used aligned loads on 16-byte-aligned std::vector data (fixed by PR #383).

## How it is fast

The original computes each 1x1 (pointwise) output channel as a separate dot product with a horizontal reduction (_mm256_mul_ps/_mm256_add_ps plus hadd, no FMA) and allocates fresh blobs for every layer on every call. The Highway path repacks pointwise weights into output-channel blocks at model load and runs a register-blocked outer-product kernel (broadcast one input value, FMA into 2-8 vector accumulators, 64-output specialisation); on x86 the 'hybrid' build swaps in AVX2/FMA intrinsics for 3x3 depthwise and max-pool with fused ReLU and an interior fast path. It also fuses FPN upsample+add and keeps the model in a function-local static and all activations in thread_local workspaces, removing per-call allocation and zeroing; highway/docs/hw-performance-report.md credits the packed pointwise kernel and workspace reuse with the largest gains.

## Compared with alternatives

Pick it over general CPU inference engines such as MNN, OpenVINO, NNPACK or FeatherCNN when the job is only face detection and you want a single self-contained C API with the model baked in; pick those engines when you need other models, ARM-tuned kernels or GPU back ends, since none of them is benchmarked against this detector.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | original: none (copy src/ into the project); Highway version: Google Highway 1.3.0 via find_package(hwy 1.3.0), OpenCV only for the benchmarks and examples; Rust crate: image 0.25.10 (jpeg, png) |
| **Minimum toolchain** | C++11 (cxx_std_11) and CMake 3.15 for highway/; README numbers from MSVC 19.40 (VS 2022); Rust 1.85, edition 2024, for the crate |
| **Platforms** | x86-64 measured (Windows, MSVC; scalar, SSE/default and AVX2 builds); AVX-512 buildable but unmeasured; ARM untested for the Highway version |
| **Thread safety** | facedetect_hw_cnn is safe to call concurrently (function-local static model, thread_local workspaces) as long as each thread has its own result buffer; each thread's workspaces stay allocated for the thread's lifetime. The original facedetect_cnn initialises its global filters through an unsynchronised param_initialized flag, so make one call before going multi-threaded. |
| **Drop-in for the baseline** | partial — same arguments and result layout as facedetect_cnn, but a different header (facedetect_hw.h) and function name, a separate CMake project and a Highway 1.3.0 dependency |

## Gotchas

- Harness flaw in the C++ multi-thread rows: hw_resolution_benchmark.cpp starts the timer before creating the 28 std::threads, runs only 128 iterations in total (4-5 per thread), and its warm-up calls run on the main thread, so each new thread's first facedetect_hw_cnn call allocates its thread_local workspaces inside the timed region. The Rust harness warms each worker and starts timing after a barrier, so the README's Rust-versus-C++ multi-thread rows (e.g. 14812.76 vs 6879.46 FPS at 128x96) are not like-for-like; only the single-thread rows are clean comparisons.
- The '6.4x speed up' commit title and the 6.9x figure in highway/docs/hw-performance-report.md (269.72 ms vs 38.85 ms at 1280x960) compare against the original built without _ENABLE_AVX2: in highway/CMakeLists.txt only fdt_hw_resolution_benchmark gets the AVX2 definition, not fdt_hw_image_benchmark, and 269.72 ms matches four times the README's scalar 640x480 time (derived from page data). Against the AVX2 original the single-thread gain is 2.8-3.9x.
- README numbers (May 2026, MSVC) predate the PR #383 crash fix (aligned to unaligned load/store in MulAddLoop, DotProductHw, AddHw, AddInplaceHw, ReluHw) and were not re-measured; no performance effect is stated.
- The README tells Rust users to add libfacedetection_rs = "0.1", but crates.io returns 'crate libfacedetection_rs does not exist' (checked 2026-10-11) and rust/Cargo.toml points its repository at the Wwupup fork, so it must be used as a git or path dependency; it also exposes no C ABI.

## Known shortcomings

- Highway path and Rust crate measured only against the repo's own original AVX2 build (33.42 ms to 8.48 ms at 640x480, about 3.9x derived; i7-14700KF, MSVC 19.40, public harness highway/benchmark/hw_resolution_benchmark.cpp); no external detector compared. README numbers predate the PR #383 crash fix (aligned loads changed to unaligned, not re-measured), so the tier is capped at C by the later-fixed-bug rule. Filed under autodiff-and-ml-kernels (CNN inference, not an image codec).
- Enricher: the commit-title 6.4x and hw-performance-report 6.9x (269.72 vs 38.85 ms at 1280x960) compare against the original built without _ENABLE_AVX2 (only fdt_hw_resolution_benchmark gets the AVX2 define in highway/CMakeLists.txt, fdt_hw_image_benchmark does not); the fair figure is 2.8-3.9x vs the AVX2 original. In the C++ multithread rows the timer starts before 28 std::thread creations, only 128 iterations total (4-5 per thread) and the warm-up runs on the main thread so per-thread thread_local workspace allocation lands inside the timed region, while the Rust harness warms workers and times after a barrier; single-thread rows are clean. libfacedetection_rs is not on crates.io despite the README; Highway path untested on ARM, no runtime dispatch; the original facedetect_cnn lazy-inits through an unsynchronised global flag; no external detector baseline.
- Domain set to numerics-and-science to match its autodiff-and-ml-kernels category.

## Caveats and trade-offs

Baseline is the project's own original implementation, not an external incumbent: no comparison against OpenCV FaceDetectorYN, dlib, MTCNN, RetinaFace or any other detector appears in the README, opencv_dnn/ (deployment demos only), COMPILE.md or the Rust report. All numbers are first-party and the Highway section is recent (added 2026-05-04 by maintainer Wwupup in 'feature: add highway optimize version for 6.4x speed up'). The benchmark times the detector only (cv::resize happens outside the timed loop) and prints a face count per detector without asserting output parity, but highway/tests/hw_test_kernels.cpp checks the Highway image transform, backbone, heads and decoded tensors against the original CDataBlob flow. In the in-harness origin build the original code is compiled without OpenMP, so its single-thread numbers are fair but differ from the default top-level CMake build (USE_OPENMP ON). Origin AVX2 differs between the two README tables (33.42 ms vs 35.93 ms at 640x480), about 7 percent run-to-run spread; the Rust table uses the image crate's resize instead of OpenCV's and says it is not for result-buffer parity or accuracy. PR #383 (pszemus, merged 2026-06-28) fixed a SIGSEGV on x86 AVX2+ targets in five Highway kernels (MulAddLoop, DotProductHw, AddHw, AddInplaceHw, ReluHw) that used aligned Load/Store on 16-byte-aligned std::vector blobs; the fix switched them to LoadU/StoreU, the README numbers (MSVC on Windows, measured in May 2026) were not re-measured afterwards, and no performance effect is stated. ARM has not been tested for the Highway version. Domain note: this is CNN inference for face detection and could instead be filed under numerics-and-science / autodiff-and-ml-kernels rather than image-codecs. The older README tables (i7-7820X AVX2/AVX512, Raspberry Pi 4B) have no baseline. [retier] Self-baseline only; numbers predate the PR #383 crash fix; C++ MT rows time 28 thread creations and per-thread workspace allocation (128 iterations total) while the Rust harness warms workers and times after a barrier; libfacedetection_rs not on crates.io; Highway untested on ARM, no runtime dispatch.

Highway path is a separate C API (facedetect_hw_cnn, own result buffer size) beside the untouched original; it is built per instruction set with no runtime dispatch and needs the Highway 1.3.0 dependency. The public API uses thread-local workspaces, so scaling comes from calling it from several threads with one result buffer per thread. ARM Linux is untested for the Highway version and AVX512 rows are N/A on the test CPU. The Rust crate (libfacedetection_rs 0.1) has a safe API and runtime AVX2 dispatch but no published C ABI.

## Maintenance

Active (BSD-3-Clause, about 12.8k stars). The Highway and Rust paths were added in May 2026 by maintainer Wwupup and last changed by the June 2026 SIGSEGV fix; they are young, x86-only in practice, and the Rust crate is not yet on crates.io.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now C.
- **Tier reason:** Public harness highway/benchmark/hw_resolution_benchmark.cpp times the original facedetect_cnn and facedetect_hw_cnn in one executable; README states MSVC 19.40.33821.0 Release, the CPU (i7-14700KF) and the command, and COMPILE.md plus highway/CMakeLists.txt give the CMake options and /arch:AVX2 plus _ENABLE_AVX2 flags, so A (first-party, but reproducible).
- **Retiered** A to C: Tier stays C (later-fixed-bug cap). Caveat correction: the 6.4x and 6.9x figures compare against the original built without _ENABLE_AVX2; the fair figure against the AVX2 original is 2.8-3.9x, and the C++ multithread rows include thread creation and thread_local workspace allocation in the timed region.
- **Verifier notes:** Every quoted README number matches (3.9x, 3.6x, 2.8x, 2.8x single-thread; 1.9x MT at 640x480; 6750.38 vs 19047.05 FPS; 7.7x vs scalar; Rust 35.93 vs 8.73 ms); metadata checked: 12.8k stars, 3.0k forks, BSD-3-Clause, last commit 2026-06-28. Kept at A despite PR #383: the fix is a crash fix (aligned to unaligned loads) that cannot have made the measured MSVC runs faster or wrong, since a misaligned aligned-load would have faulted rather than completed; if the orchestrator applies the later-fixed-bug rule strictly, the cap would be C. Shortcomings: self-baseline (original implementation) only, no external detector compared, wrong-ish category (ML inference, not image codec).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-113 (wave 10); enricher w10 pair-030; orchestrator domain fix 2026-10-11
- **Pages the verifier opened:**
  - <https://github.com/ShiqiYu/libfacedetection>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/README.md>
  - <https://github.com/ShiqiYu/libfacedetection/tree/master/highway>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/README.md>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/benchmark/hw_resolution_benchmark.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/tests/hw_test_kernels.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/COMPILE.md>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/LICENSE>
  - <https://github.com/ShiqiYu/libfacedetection/pull/383>
  - <https://github.com/ShiqiYu/libfacedetection/commits/master>
- **Sources the enricher read:**
  - <https://github.com/ShiqiYu/libfacedetection/tree/master/highway>
  - <https://github.com/ShiqiYu/libfacedetection/tree/master/highway/docs>
  - <https://github.com/ShiqiYu/libfacedetection/commits/master>
  - <https://github.com/ShiqiYu/libfacedetection/issues>
  - <https://github.com/ShiqiYu/libfacedetection/pull/383>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/README.md>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/COMPILE.md>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/README.md>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/benchmark/hw_resolution_benchmark.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/tests/hw_test_kernels.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/include/facedetect_hw.h>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/src/facedetect_hw.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/src/hw_network.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/src/hw_kernels_hw.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/src/hw_kernels_intrinsics.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/src/hw_blob.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/src/hw_layers.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/src/hw_filter.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/docs/hw-performance-report.md>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/highway/docs/hw-status.md>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/src/facedetectcnn.h>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/src/facedetectcnn.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/src/facedetectcnn-model.cpp>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/rust/docs/rs-performance-optimization-report.md>
  - <https://raw.githubusercontent.com/ShiqiYu/libfacedetection/HEAD/rust/dev/resolution_benchmark/src/main.rs>
  - <https://crates.io/api/v1/crates/libfacedetection_rs>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/shiqiyu/libfacedetection`) · [data/wave10/enrich/raw/github_com_shiqiyu_libfacedetection.json](../../../data/wave10/enrich/raw/github_com_shiqiyu_libfacedetection.json) (enrichment confidence 0.8)

</details>
