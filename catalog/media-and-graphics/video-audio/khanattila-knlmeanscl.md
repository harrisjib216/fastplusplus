# KNLMeansCL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (OpenCL)` · `GPL-3.0` · 🔴 abandoned

> OpenCL non-local means denoiser plugin for AviSynth(+) and VapourSynth; one user anecdote shows it about 2.5-3x faster than HandBrake's CPU NLMeans.

| | |
|---|---|
| **Beats** | HandBrake NLMeans (CPU non-local means filter); not FFmpeg nlmeans or nlmeans_opencl |
| **Claimed result** | 'From my (limited) testing I got with NLMeans \~17-20fps with KNLMeansCL 50-55fps encoding speed of the same file. It is still slower then hqdn3d (\~75fps)' (issue author CvH, 2017-07-26); about 2.5-3.2x (derived from page data). |
| **Workload** | A user's video encode of the same file in HandBrake with its built-in CPU NLMeans filter versus with KNLMeansCL (OpenCL GPU), reporting encode fps; hqdn3d is the speed reference. |
| **Metric** | throughput |
| **Adoption** | 113 stars, 30 forks |
| **Last commit** | 2023-01-05 |
| **Links** | [repository](https://github.com/Khanattila/KNLMeansCL) · [benchmark](https://github.com/HandBrake/HandBrake/issues/839) |

## Verdict

The only comparison is a 2017 HandBrake feature request (issue 839, CvH): about 17-20 fps whole-encode speed with HandBrake's built-in CPU NLMeans versus 50-55 fps with KNLMeansCL on the same file (about 2.5-3.2x), with no hardware, resolution, filter settings or versions. Because the issue asks HandBrake to add KNLMeansCL, the faster run cannot have been inside HandBrake, so the two numbers come from different, unstated pipelines. The wiki Benchmark page gives absolute fps only (v1.0.2, 1080p, d=1 a=2 s=4, Core i5-4690 with Radeon RX 480, Windows 10).

## Use it when

- AviSynth+ or VapourSynth encode scripts that need NLMeans denoising and have an otherwise idle GPU while x264/x265 keep the CPU busy.
- AMD or Intel GPUs where CUDA-only denoisers (for example BM3DCUDA) are not an option; OpenCL 1.2 covers AMD, Intel and NVIDIA.
- Chroma-only or 4:2:0 denoising at 1080p: the wiki's RX 480 table shows the UV planes of 4:2:0 at up to 67 fps versus about 25 fps for 8-bit luma.
- Workflows that compute weights on a prefiltered reference clip (rclip) and apply them to the original.

## Skip it when

- HandBrake- or FFmpeg-only pipelines: it is a frame-server plugin and cannot be loaded there (HandBrake issue 839 requesting it is closed); use FFmpeg nlmeans_opencl or av-denoise instead.
- Apple Silicon or macOS AMD GPUs: issue 56 (flashing pink/green frames on M1, open since 2023-05-02) is only fixed in unmerged PR 60 (2026-04-10).
- CPU-only machines: it needs an OpenCL CPU runtime (issues 51 and 57 report device_type='cpu' failures), and search snippets of the Doom9 thread (forum blocked here) put TNLMeans level with it on a weak CPU.
- 4:4:4, RGB or float clips at high resolution: the wiki table drops to about 9 fps at 1080p on an RX 480, and clips above 8192x8192 are refused.
- Projects that need maintained binaries: the last tagged release is v1.1.1, master (1.1.1e) last changed on 2023-01-05, and issue 58 (2025-11-27) asks for a new build.

## How it is fast

Implements the Goossens et al. (ACIVS 2010) GPU NLMeans scheme: for each search offset q it builds a per-pixel squared-difference image (nlmDistance), box-filters it into patch distances with separable horizontal and vertical kernels that tile through __local memory (O(s) per pixel per pass instead of O(s^2)), turns them into weights (native_exp for the Welsch mode) and accumulates. Weights are symmetric, so only half the (2a+1)^2(2d+1) window is computed and each distance image serves both p+q and p-q. Frame size, radii and channel layout are baked into the kernel as -D constants at build time with -cl-fast-relaxed-math, and work-group shapes are picked per vendor from CL_DEVICE_MAX_WORK_GROUP_SIZE.

## Compared with alternatives

Pick it over av-denoise when the pipeline is AviSynth+ or VapourSynth rather than FFmpeg and you need temporal NLMeans on a non-NVIDIA GPU; pick VapourSynth-BM3DCUDA instead when you have NVIDIA hardware and want BM3D quality, since KNLMeansCL publishes no head-to-head numbers against either.

## Integration

| | |
|---|---|
| **Form** | shared lib (AviSynth/AviSynth+ and VapourSynth plugin) |
| **Dependencies** | OpenCL 1.2 ICD and a vendor runtime; VapourSynth API 3 headers (VapourSynth.h, VSHelper.h) or AviSynth+ headers; meson.build also requires Boost filesystem/system although no source file includes Boost; Windows builds need the Visual C++ 2015 redistributable |
| **Minimum toolchain** | C++11 (meson cpp_std=gnu++11), OpenCL 1.2 (0.6.11 is the last release for OpenCL 1.0/1.1) |
| **Platforms** | Windows, Linux, macOS; any OpenCL 1.2 GPU, CPU or accelerator (wiki lists AMD HD 5800+, Intel HD 2500+, NVIDIA GT 640+); maximum 8192x8192 |
| **Thread safety** | One command queue and one set of device buffers per filter instance; VapourSynth mode fmParallelRequests serialises frame processing per instance, AviSynth+ uses MT_MULTI_INSTANCE (one OpenCL context per thread). Building the kernel calls setlocale(LC_ALL, "C") then setlocale(LC_ALL, ""), which changes the whole process's locale (issue 43, open). |
| **Drop-in for the baseline** | no |

## Gotchas

- Possible stale-frame bug at the end of a clip (from reading NLMVapoursynth.cpp and NLMAvisynth.cpp, not tested): uploads cover frames n+k_start..n+k_end with k_end clamped to the clip end, but the symmetric loop still reads the future slot t-k for every k down to k_start = -min(d, n). For the last d frames those slots hold whatever an earlier request uploaded. In strict sequential order that is the last frame repeated; under out-of-order requests (seeking, multithreaded vspipe) it is an unrelated frame, which would blend into the output.
- Each output frame re-uploads all 2d+1 input frames, issues 4 to 7 kernel launches per search offset (about 37 offsets at the defaults a=2, d=1) and ends with a blocking clFinish, so there is no overlap of transfer and compute across frames; one instance per GPU stays single-stream.
- Driver-specific breakage is fixed only in unmerged PRs: macOS buffer-fill sync (PR 60), Radeon compiler crash from unused nlmUnpack image arguments (PR 59), AUTO device fallback on runtimes that return CL_INVALID_VALUE (PR 61). Mesa OpenCL is not recognised (issue 55).
- Manual ocl_x/ocl_y/ocl_r overrides are not checked against s: the horizontal and vertical kernels need block width and height of at least s, or their __local buffer reads go out of bounds (the auto-selected blocks are at least 8 and s is limited to 8).

## Known shortcomings

- The only number is a HandBrake issue 839 quote of whole-encode fps (50-55 against 17-20 for HandBrake's CPU NLMeans), GPU against CPU with no setup given, and the wiki Benchmark page has no baseline; off the category baselines; GPL-3.0; abandoned since 2023-01-05.
- Enricher (e128, 2026-10-05): tier C stands. Measurement flaw: HandBrake issue 839 asks for KNLMeansCL to be added, so the 50-55 fps run was outside HandBrake, with different unstated pipelines and whole-encode fps; the wiki fps have no baseline. Possible bug (code reading, untested): the last d frames read stale temporal slots t-k that were never uploaded (k_end clamped while the loop runs to k_start) in NLMVapoursynth.cpp and NLMAvisynth.cpp, so out-of-order requests may blend an unrelated frame; not behind the throughput numbers. Per-frame re-upload of 2d+1 frames plus a blocking clFinish; global setlocale change (issue 43); macOS flashing (issue 56, fix only in unmerged PR 60); PRs 59 and 61 unmerged; Boost in meson unused; ocl_x below s gives out-of-bounds local reads.

## Caveats and trade-offs

The only head-to-head number is a 2017 user anecdote in a HandBrake feature-request issue (CvH, issue closed): no GPU or CPU model, resolution, filter settings, versions or compiler stated. The figures are whole-encode fps (encoder included), not filter-only throughput, and compare an OpenCL GPU filter against HandBrake's CPU NLMeans with denoise strength not matched, so the 2.5-3.2x is a rough system-level indication. The baseline is HandBrake's own NLMeans port, not an FFmpeg component or other category incumbent. The project's wiki Benchmark page lists absolute fps only, with no baseline: 1920x1080, KNLMeansCL(d=1, a=2, s=4, device_type='GPU'), version 1.0.2, Intel Core i5-4690 3.9 GHz, 8 GB DDR3-1600, AMD Radeon RX 480, Windows 10 64-bit; GRAY int8 25 fps down to 9 fps for single-precision 4:4:4 and RGB. Search snippets of the Doom9 thread (forum blocked, snippet only) say TNLMeans was about equal or slightly ahead on a weak CPU (C2D 4400) and that a GPU TNLMeans variant reached about 30 fps against 25 fps for KNLMeansCL in one user's test, so the advantage depends on hardware and settings. No FFmpeg nlmeans or nlmeans_opencl comparison with numbers was found (FastFlix issue 202 only says nlmeans_opencl is 'way faster' than the CPU filter). Last commit 2023-01-05 (merge of pinterf pull request #53); pinterf's fork carries later work. Repository page showed 572 commits.

Needs an OpenCL 1.2 capable CPU or GPU (wiki Requirements page; Windows needs the Visual C++ 2015 redistributable); AviSynth, AviSynth+ and VapourSynth plugin only, not an FFmpeg filter. GPL-3.0. Output equivalence to other NLMeans filters was not checked here.

## Maintenance

Abandoned upstream (last commit 2023-01-05, three driver-fix PRs from 2026-04-10 unmerged), GPL-3.0, so it is fine as a plugin but cannot be vendored into permissively licensed code; the pinterf fork carries later AviSynth+ work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** HandBrake issue 839 (opened by CvH, 2017-07-26) gives 'NLMeans \~17-20fps with KNLMeansCL 50-55fps' encode speed with no hardware, resolution, settings or versions, so these are numbers without methodology; the project's wiki Benchmark page states full hardware but has no baseline column.
- **Verifier notes:** Issue 839 quote, date and author match the record; derived 2.5-3.2x is correct (50/20 and 55/17). License GPL-3.0 confirmed from the LICENSE file; 113 stars, 30 forks, not archived or a fork; last commit 2023-01-05 so abandoned (more than 3 years) is correct. The Doom9 archive (forum.doom9.org) returned EGRESS_BLOCKED, so the TNLMeans comparisons there are snippet-only and were not used for the tier.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** user-reported fps (HandBrake issue 839)
- **Pages the verifier opened:**
  - <https://github.com/Khanattila/KNLMeansCL>
  - <https://github.com/Khanattila/KNLMeansCL/commits/master>
  - <https://github.com/Khanattila/KNLMeansCL/wiki/Benchmark>
  - <https://github.com/HandBrake/HandBrake/issues/839>
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/README.md>
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/meson.build>
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/KNLMeansCL/NLMKernel.cpp>
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/KNLMeansCL/NLMKernel.h>
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/KNLMeansCL/NLMDefault.h>
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/KNLMeansCL/NLMVapoursynth.cpp>
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/KNLMeansCL/NLMVapoursynth.h>
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/KNLMeansCL/NLMAvisynth.cpp>
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/KNLMeansCL/shared/ocl_utils.cpp>
  - <https://raw.githubusercontent.com/Khanattila/KNLMeansCL/HEAD/KNLMeansCL/shared/common.cpp>
  - <https://github.com/Khanattila/KNLMeansCL/issues?q=is%3Aissue>
  - <https://github.com/Khanattila/KNLMeansCL/issues/56>
  - <https://github.com/Khanattila/KNLMeansCL/issues/33>
  - <https://github.com/Khanattila/KNLMeansCL/pulls?q=is%3Apr>
  - <https://github.com/Khanattila/KNLMeansCL/pull/60>
  - <https://github.com/Khanattila/KNLMeansCL/pull/59>
  - <https://github.com/Khanattila/KNLMeansCL/wiki/Benchmark>
  - <https://github.com/Khanattila/KNLMeansCL/wiki/Requirements>
  - <https://github.com/Khanattila/KNLMeansCL/releases>
  - <https://github.com/HandBrake/HandBrake/issues/839>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/khanattila/knlmeanscl`) · [data/wave10/enrich/raw/github_com_khanattila_knlmeanscl.json](../../../data/wave10/enrich/raw/github_com_khanattila_knlmeanscl.json) (enrichment confidence 0.65)

</details>
