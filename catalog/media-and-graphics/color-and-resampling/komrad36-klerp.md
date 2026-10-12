# KLERP / KNERP

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only AVX2 bilinear and nearest-neighbour resize for 8-bit grayscale; author claims 25-100% faster than OpenCV cv::resize.

| | |
|---|---|
| **Beats** | OpenCV resize (bilinear and nearest-neighbor interpolation) |
| **Claimed result** | README: 'exceeding OpenCV's implementation in speed by 25-100% while matching its output and capabilities in both interpolation modes'; 'the magnitude of the speed gain depends on whether you're downscaling or upscaling and by how much'. No per-case numbers are given. |
| **Workload** | Grayscale (8-bit, single channel) image resize with bilinear (KLERP) and nearest-neighbor (KNERP) interpolation, up- and downscaling, AVX2 plus multithreading, matching OpenCV output. |
| **Metric** | throughput |
| **Compiler and flags** | Repo Makefile (not stated as the flags used for the OpenCV comparison): g++ -Ofast -std=gnu++14 -mavx2 -march=native -mfma -flto -funroll-all-loops -fpeel-loops -ftracer -ftree-vectorize, -lpthread |
| **Adoption** | 23 stars |
| **Last commit** | 2021-03-23 |
| **Links** | [repository](https://github.com/komrad36/KLERP) · [benchmark](https://github.com/komrad36/KLERP) |

## Verdict

The only claim is the author's bare '25-100% faster than OpenCV' range with no per-case numbers, CPU, compiler, OpenCV version or thread settings; main.cpp times KLERP alone (2x2 input upscaled to 800x2000, multithreaded, 2000 runs) and never calls cv::resize. The code dates from December 2016, and OpenCV 4.x's resize.cpp still performs the same fixed-point vertical pass with universal intrinsics, so any lead now rests on row reuse and threading and has not been re-measured.

## Use it when

- Upscaling 8-bit grayscale frames or ROIs on x86-64 with AVX2 where row reuse removes most of the horizontal pass.
- Computer-vision code that already relies on OpenCV INTER_LINEAR fixed-point output but wants a dependency-free kernel for this one operation.
- Single-threaded use (KLERP&lt;false&gt;), which avoids the threading defects below and is small enough (about 260 lines) to vendor and audit.
- As a readable reference for OpenCV-compatible fixed-point bilinear resizing with AVX2.

## Skip it when

- Multithreaded calls on machines with many hardware threads unless the row split is patched: it writes past the end of dst for common heights (see gotchas).
- Colour or multi-channel images, 16-bit or float data, or strided ROIs: only packed 8-bit single-channel buffers are supported.
- CPUs without AVX2 or non-x86 targets: there is no SSE, NEON or scalar fallback for KLERP.
- Area, bicubic or Lanczos filtering, or any case needing published, reproducible speed numbers: the repo has no OpenCV timing code.
- Calling KLERP&lt;true&gt; or KNERP&lt;true&gt; from several threads at once: the calls share one function-static std::future array.

## How it is fast

Separable fixed-point bilinear: per-call tables of source columns and 11-bit weights, a scalar horizontal pass into 32-bit row buffers, then an AVX2 vertical pass (shift right 4, packs, _mm256_mulhi_epi16 by the row weights, rounding shift, packus) that writes 32 pixels per iteration; this is the same arithmetic as OpenCV's VResizeLinearVec_32s8u. Horizontally filtered source rows are cached and reused when consecutive output rows map to the same source rows, which skips most of the horizontal work when upscaling. Outputs of 20000 pixels or more are split by rows across std::thread::hardware_concurrency() std::async tasks; KNERP is a scalar table-driven gather threaded the same way.

## Compared with alternatives

Pick KLERP only when a tiny dependency-free header for OpenCV-compatible bilinear on 8-bit grayscale matters more than evidence; CompV publishes measured speedups over cv::resize bilinear, and fast_image_resize, tir and stb-image-resize-opt cover multi-channel data and better filters with published benchmark tables.

## Integration

| | |
|---|---|
| **Form** | header-only (KLERP.h), but its helper functions are not marked inline |
| **Dependencies** | none beyond the C++ standard library, &lt;immintrin.h&gt; and pthreads (Makefile links -lpthread) |
| **Minimum toolchain** | C++14 (Makefile uses g++ -std=gnu++14 -mavx2 -mfma -march=native -Ofast); compiler version not documented |
| **Platforms** | x86-64 with AVX2 (also uses the SSE4.1 _mm_round_ps); no other architectures |
| **Thread safety** | KLERP&lt;false&gt; and KNERP&lt;false&gt; are reentrant; the &lt;true&gt; variants share a function-static array of std::future objects, so concurrent calls race |
| **Drop-in for the baseline** | partial: raw-pointer API for packed 8-bit single-channel images only; intended to reproduce cv::resize INTER_LINEAR / INTER_NEAREST output, but the repo never compares its output with OpenCV |

## Gotchas

- Heap overflow in the multithreaded row split (KLERP and KNERP): stride = ceil(dst_h / hardware_concurrency()) and hardware_concurrency()-1 full chunks are launched before the remainder, so whenever (threads-1)\*stride &gt; dst_h the tasks write rows past the end of dst (and read past the end of the weight table). A simulation of the split shows it for a 2000x10 output on 8 threads (4 extra rows), 1000x100 on 16 threads, and on 64 threads 1891 of the heights 2-4096, including 640x480 (15360 bytes past the buffer), 1280x720 and main.cpp's own 800x2000 (12800 bytes). Fix by launching only ceil(dst_h / stride) chunks.
- _KNERP, pass1, pass2 and _KLERP are non-inline functions defined in the header, so including KLERP.h from two translation units gives duplicate-symbol link errors; add inline or include it in one .cpp.
- Each multithreaded call starts its tasks with std::async(std::launch::async); libstdc++ and libc++ create a new thread per task (MSVC uses a pool), so outputs just above the 20000-pixel cutoff pay thread start-up on every call. A hardware_concurrency() of 0 would divide by zero.
- The demo builds with -Ofast -mfma, which lets the compiler contract the double-precision coordinate maths into FMAs; bit-exact agreement with a given OpenCV build is plausible from the arithmetic but is not tested anywhere in the repo.

## Known shortcomings

- Bare '25-100% faster than OpenCV' claim (grayscale bilinear/nearest resize): main.cpp times KLERP only, with no OpenCV side, machine, flags or OpenCV build; both sides likely multithreaded. Code from 2016, last commit 2021-03-23 (LICENSE only), MIT, 23 stars.
- Correctness bug in the multithreaded row split (KLERP and KNERP): stride = ceil(dst_h/hw) with hw-1 full chunks launched, so writes run past dst when (hw-1)\*stride exceeds dst_h (simulated: 2000x10 on 8 threads, 1000x100 on 16; on 64 threads 640x480 overruns by 15360 bytes and main.cpp's own 800x2000 by 12800), a heap overflow on modern many-core machines (the author's box was probably 16 threads or fewer, so the numbers are likely unaffected). Helpers are non-inline in the header (ODR link errors across two translation units); a static std::future array is not reentrant; std::async spawns a thread per task per call; main.cpp never runs OpenCV, so the claim is untestable from the repo.

## Caveats and trade-offs

Only the percentage range appears in the README (and the identical header comment in KLERP.h and main.cpp). main.cpp is a KLERP-only timing loop (2000 warm-ups and 2000 runs, 2x2 image upscaled to 800x2000, multithreading=true) and never calls OpenCV, so the comparison cannot be reproduced from the repo. CPU, OpenCV version and OpenCV build options (IPP, thread count) are not stated. KLERP spawns std::thread::hardware_concurrency() threads for outputs of 20000 pixels or more; OpenCV's resize is also parallelised with parallel_for_ by default, so threading is probably comparable, but this is not documented. Grayscale 8-bit only and AVX2 required; output is designed to match OpenCV's fixed-point bilinear ('silliness to match opencv's output' in KLERP.h). Code dates from 2016-12-26 (the only later commit, 2021-03-23, added the LICENSE), so the OpenCV compared against was probably 3.x; OpenCV has since reworked resize with wide universal intrinsics, so the lead may have shrunk or vanished.

Single header KLERP.h with no dependencies. Needs an AVX2 CPU, uses its own threads (links pthread), and handles grayscale images only (the README says it is meant for computer vision). A CUDA sibling (CUDALERP, CUDAFLERP) by the same author covers GPU use.

## Maintenance

Abandoned: the code is a single 26 Dec 2016 commit and the only later commit (23 Mar 2021) added the MIT license; no issues or pull requests exist. Small enough to vendor, but patch the row split and mark the helpers inline first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party claim only: the README gives a bare '25-100%' range against OpenCV with no per-case numbers, CPU, OpenCV version or thread settings, and main.cpp times KLERP alone (2x2 to 800x2000, multithreaded) without running OpenCV.
- **Verifier notes:** Record is accurate; metadata checked (MIT LICENSE file, 23 stars, 9 forks, two commits, last 2021-03-23, abandoned). Resize fits the category, unlike the box blur.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/komrad36/KLERP>
  - <https://github.com/komrad36/KLERP/commits/master>
  - <https://raw.githubusercontent.com/komrad36/KLERP/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/KLERP/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/komrad36/KLERP/HEAD/KLERP.h>
  - <https://raw.githubusercontent.com/komrad36/KLERP/HEAD/Makefile>
  - <https://raw.githubusercontent.com/komrad36/KLERP/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/komrad36/KLERP>
  - <https://github.com/komrad36/KLERP/commits/master>
  - <https://github.com/komrad36/KLERP/issues?q=>
  - <https://raw.githubusercontent.com/komrad36/KLERP/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/KLERP/HEAD/KLERP.h>
  - <https://raw.githubusercontent.com/komrad36/KLERP/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/komrad36/KLERP/HEAD/Makefile>
  - <https://raw.githubusercontent.com/komrad36/KLERP/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/resize.cpp>
  - <https://github.com/komrad36?tab=repositories>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/komrad36/klerp`) · [data/wave10/enrich/raw/github_com_komrad36_klerp.json](../../../data/wave10/enrich/raw/github_com_komrad36_klerp.json) (enrichment confidence 0.75)

</details>
