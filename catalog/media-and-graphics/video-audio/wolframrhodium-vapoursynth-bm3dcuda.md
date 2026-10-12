# VapourSynth-BM3DCUDA

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++ (CUDA, HIP, AVX2)` · `GPL-2.0` · 🟢 active

> BM3D/V-BM3D denoiser for VapourSynth on CUDA, AVX2, HIP and SYCL; no published number against VapourSynth-BM3D.

| | |
|---|---|
| **Beats** | VapourSynth-BM3D (original CPU plugin) and FFmpeg bm3d; no comparison against either found |
| **Claimed result** | None against a named baseline. Own fps from release R2.13 (1920x1080, radius 0, chroma False, final False): NVIDIA T4 342.23 (bm3dcuda), AMD Radeon Pro V520 152.20 (bm3dhip), Hygon C86 7390 207.90, Intel Sapphire Rapids 598.43 and AMD EPYC Zen4 674.37 (bm3dcpu, 32-core each); radius 1 chroma True final True: 18.15, 19.91, 21.50, 49.50, 59.87 fps in the same order. |
| **Workload** | BM3D and V-BM3D denoising of 1920x1080 GrayS and YUV444PS clips, fps by radius, chroma and final stage, on its own CUDA, HIP and AVX2 CPU builds (release R2.13 notes); no baseline implementation is timed. |
| **Metric** | throughput |
| **Hardware** | R2.13 notes: NVIDIA T4 (AWS g4dn.2xlarge, Linux 6.2.0-1014-aws, driver 545.23.06, CUDA 12.3), AMD Radeon Pro V520 (AWS g4ad.2xlarge, Linux 6.2.0-1014-aws, ROCm 5.7.1), Hygon C86 7390 32C @ 2.70 GHz, Intel Sapphire Rapids 32C @ 3.4 GHz and AMD EPYC Zen4 32C @ 3.4 GHz (all three CPUs on Windows Server 2022); VapourSynth R65-RC1-6-g3dcc6a35. R2.14 adds Intel Arc A770 (252.46 fps) and Data Center GPU Max 1100 (323.51 fps) at radius 0, chroma False, final False. |
| **Compiler and flags** | README build command: CMAKE_BUILD_TYPE=Release, CMAKE_CUDA_FLAGS='--threads 0 --use_fast_math -Wno-deprecated-gpu-targets'; the release-note benchmark does not state flags or the benchmark script |
| **Adoption** | 88 stars, 15 forks; release R2.17 (2026-09-26) adds rolling temporal BM3Dv2 |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/WolframRhodium/VapourSynth-BM3DCUDA) · [benchmark](https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/releases/tag/R2.13) |

## Verdict

The only first-party numbers are self-comparisons. R2.13 times its own CUDA (T4), HIP (Radeon Pro V520) and AVX2 (32-core Hygon 7390, Sapphire Rapids, EPYC Zen4, all on Windows Server 2022) builds at 1920x1080 GrayS/YUV444PS, for example 342/152/208/598/674 fps at radius 0 basic, with no script, parameters beyond radius/chroma/final, or CPU compiler flags (current CI builds the CPU DLLs with clang -mtune=&lt;arch&gt; -ffast-math -mavx2 -mfma). The V520 column came from a build whose own notes say output 'may be broken'. Third-party numbers: AmusementClub/vapoursynth-nssfactory PR #23 times bm3dcuda at 636 fps on an RTX 5080 (1080p gray) as the baseline for a faster port. A Doom9 post, seen only as a search snippet, gives 165.55 fps at radius 0 against a single-threaded 'BM3D_cpu' at 22 fps on an i7-8700, but the GPU and which CPU filter was used are unstated. Nothing measures it against VapourSynth-BM3D or FFmpeg bm3d.

## Use it when

- VapourSynth encode chains that already run in 32-bit float and want BM3D or V-BM3D on an NVIDIA GPU (compute capability 5.0+): R2.13 lists 342 fps on a T4 for 1080p GrayS at radius 0, and a third-party harness (AmusementClub/vapoursynth-nssfactory PR #23) measured 636 fps on an RTX 5080 at 1080p gray.
- Many-core AVX2 servers with no GPU: in the R2.13 table, bm3dcpu on a 32-core EPYC Zen4 (674 fps at radius 0) or Sapphire Rapids (598 fps) beats the T4 in every row.
- Temporal denoising on CUDA through BM3Dv2's rolling mode (R2.17). PR #35 reports 1.7x to 2.7x over the old temporal path at radius 1-4 (RTX 5080, 640x360 GrayS); use rolling_chunk=16 for linear renders.
- When you need bit-reproducible GPU output (set extractor_exp &gt;= 3) or want to experiment with other transforms (Haar, WHT, Bior1.5) and block costs (SAD, ZSSD, ZSAD) through the _rtc build.

## Skip it when

- When results must match VapourSynth-BM3D or the reference MATLAB BM3D. This plugin has no Kaiser window, no coarse prefiltering, no th_mse early cut-off, a group size fixed at 8 (issue #19 is open) and no coefficient normalization, so the same sigma does not give the same strength.
- When you need proof that it beats the CPU plugin or FFmpeg's bm3d filter: every first-party table times only its own backends. The only third-party GPU number found compares it with another CUDA port, which was faster (nss_cuda 732 vs bm3dcuda 636 fps).
- On AMD GPUs: the HIP build is disabled in R2.17, issue #23 (artifacts on an RX 6900 XT) and issue #33 (plugin fails to load with Adrenalin 26.5.1+) are open, and R2.13's own notes say HIP output frames 'may be broken'.
- In integer or 16-bit pipelines (input must be 32-bit float), in AviSynth (only requested, in open issues #7 and #26), or with large ps_num, which the README says can lower quality because duplicate temporal candidates are not merged.
- Long UHD encodes on Linux without watching memory: open issue #31 reports host RAM growing until OOM-kill at 3840x2160 (RTX 5060 Ti, Ubuntu 24.04, CUDA 13.0).

## How it is fast

It implements BM3D (Dabov et al. 2007) with fixed 8x8 blocks and a fixed group of 8, so one 3D group is 8x8x8 floats. The CPU build holds that group in 64 AVX2 registers, runs an 8-point DCT taken from FFTW's genfft codelets with FMA, does exhaustive SSD block matching, and keeps a sorted top-8 candidate list in one vector register, updated with permutevar and blend. Reciprocals use the approximate _mm256_rcp_ps, and the Windows release CPU DLLs are built with clang -ffast-math, one DLL per -mtune target. The CUDA kernel gives each reference block 8 lanes of a warp (4 blocks per warp), reduces SSD and maintains the top-8 list with warp shuffles, transposes through shared memory, and aggregates with float atomicAdd. Each frame runs as a CUDA Graph on pinned host buffers, with up to 4 concurrent resource sets when fast=True. The _rtc build compiles the kernel with NVRTC at filter creation, baking width, stride, sigma and the search parameters in as constants, and the R2.17 rolling BM3Dv2 path keeps temporal accumulators on the GPU instead of shipping 2\*(2r+1) intermediate planes to the CPU.

## Compared with alternatives

Pick it over KNLMeansCL or av-denoise when you want BM3D's transform-domain filtering, with its own CUDA, AVX2 and SYCL backends, rather than NLMeans. av-denoise's README claims about 1.3x the speed of V-BM3D on HIP, and KNLMeansCL is OpenCL NLMeans, so neither runs the same algorithm, and none of the three has been timed against the same incumbent.

## Integration

| | |
|---|---|
| **Form** | shared lib (VapourSynth plugin DLL/.so per backend) |
| **Dependencies** | VapourSynth API 3 headers; CUDA toolkit and driver 450+ for bm3dcuda (NVRTC, statically linked by default, for bm3dcuda_rtc); ROCm/HIP for bm3dhip; Intel oneAPI SYCL for bm3dsycl; none for bm3dcpu |
| **Minimum toolchain** | CMake 3.20; C++17 (CPU build, CUDA kernel), C++20 (CUDA/RTC/HIP/SYCL host code); CUDA 11.5+ for the static-NVRTC RTC build; CI uses CUDA 12.8 (Linux) and 13.4.2 (Windows) |
| **Platforms** | x86-64 with AVX2+FMA (bm3dcpu); NVIDIA GPUs sm_50+ (sm_35 with a manual build); AMD RDNA wave32 GPUs (HIP, currently disabled); Intel gen12lp+ GPUs (SYCL); Linux, Windows, macOS build fix merged (PR #25), Linux arm64 workflow present |
| **Thread safety** | Registered as fmParallel. The CPU build keeps one scratch buffer per worker thread (map keyed by std::thread::id, freed only when the filter is freed); the CUDA build hands out 1 or 4 stream/buffer sets under a semaphore; rolling BM3Dv2 uses fmParallelRequests with one resource behind a mutex. Issue #17 (x265 'ParallelFilter race condition' warnings when combined with other CUDA filters) is open and unexplained. |
| **Drop-in for the baseline** | partial: same parameter names as VapourSynth-BM3D (block_step, bm_range, radius, ps_num, ps_range) and the same Basic/Final/VAggregate flow, but different function names, no profiles, float input only, and a different sigma scale |

## Gotchas

- GPU output is non-deterministic by default (float atomicAdd aggregation); only extractor_exp &gt;= 3 (pre-rounding) makes it bitwise reproducible, and CPU and CUDA outputs never match bit for bit. The CPU build also uses \~12-bit approximate reciprocals for weights, Wiener coefficients and the final division.
- With radius &gt; 0, legacy BM3D() returns an intermediate clip of height\*2\*(2r+1) rows; feeding it anywhere except bm3d.VAggregate gives garbage, and unprocessed planes in that path are undefined.
- Open issue #8: the CUDA build hangs for non-power-of-2 block_step (3, 5, 6, 7) on an RTX 2070 Super; the kernel still uses the full-warp __syncwarp(membermask) logic the reporter blamed.
- cpu_source/cpuid.h cpu_supports_avx2() returns 1 when CPUID lacks the AVX or OSXSAVE bits, so on a pre-AVX CPU the creation-time check passes and bm3dcpu would fault with an illegal instruction instead of the intended 'requires AVX2-capable cpu' error.

## Known shortcomings

- Tier D: the R2.13 table times only its own CUDA, HIP and AVX2 backends (T4 342.23 fps, EPYC Zen 4 CPU build 674.37 fps) with no number against VapourSynth-BM3D or FFmpeg bm3d in the README, releases or 25 issues, no bench script and the CPU compiler unstated; it is not the same work as VapourSynth-BM3D (no coefficient normalisation, a ps_num quality regression, non-bitwise-identical output; issues #31 and #33); the HIP release was disabled in R2.17.
- Enricher (e125, 2026-10-05): D stands; no bug behind the CUDA/AVX2 numbers, but the R2.13 V520 (bm3dhip) column was measured on a build the author's own notes say 'may be broken' (#23 open). The CPU build uses _mm256_rcp_ps approximate reciprocals plus -ffast-math in the CI DLLs; no Kaiser window, no th_mse, group size fixed at 8, so the output is not the same work as VapourSynth-BM3D. Bug: cpu_source/cpuid.h cpu_supports_avx2() returns 1 when the AVX/OSXSAVE bits are absent, so a pre-AVX CPU passes the check and then faults. Open #8 hang on non-power-of-two block_step, #31 host RAM leak, #17. Third-party: nssfactory PR #23 on an RTX 5080 measured bm3dcuda 636 fps vs nss_cuda 732 fps; PR #35 rolling mode 1.7-2.7x over the project's own legacy path.

## Caveats and trade-offs

Tier D: no fps or speedup against VapourSynth-BM3D, FFmpeg bm3d or any other recognizable baseline appears in the README, releases R2.8, R2.13, R2.14, R2.17, or the 25 issues (none about speed). The R2.13 table only compares the project's own backends; notably the 32-core AVX2 CPU build beats the T4 GPU build in every row. No benchmark script is published and the CPU builds' compiler and flags are unstated. The README says the filter does not do identical work to VapourSynth-BM3D: sigma strength is only similar because coefficient normalization is not implemented, large ps_num values can regress quality because duplicate block-matching candidates are not handled (not an issue in VapourSynth-BM3D), and CPU and CUDA outputs are not bitwise identical (GPU output is non-deterministic unless extractor_exp is set). Release R2.8 notes a VAggregate rewrite about 40% faster than the previous version (own history, 0-5% overall). A third-party PR (AmusementClub/vapoursynth-nssfactory #10, RTX 5080, 1080p GrayS) times bm3dcuda only as the baseline for another CUDA port (bm3dcuda 206/144/123/82 fps against nss_cuda 191/139/110/66; spatial nss_cuda 1.06-1.10x bm3dcuda), not against the CPU plugin. Doom9 threads that search snippets suggest discuss speed are blocked here. R2.17 temporarily disables the HIP release; open issues report a possible memory leak (#31) and bm3dhip failing to load with AMD Adrenalin 26.5.1+ (#33).

Needs a CUDA GPU of compute capability 5.0+ (or HIP, SYCL, or an AVX2 CPU). Output is not bitwise identical across CPU and CUDA and sigma strength is similar but not equal to VapourSynth-BM3D; large ps_num may reduce denoise quality; fast=True costs 4x GPU memory. GPU memory formula is in the README.

## Maintenance

Active (R2.17 on 2026-09-26 with a contributed rolling BM3Dv2 and CUDA 13.4.2; HIP release paused). The GPL-2.0 plugins are built by CI workflows for Windows and Linux, so they are easy to adopt in a VapourSynth chain, but GPL rules out vendoring into closed code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The R2.13 release table (1920x1080, GrayS/YUV444PS, fps) matches the record exactly (T4 342.23, V520 152.20, Hygon 7390 207.90, Sapphire Rapids 598.43, EPYC Zen4 674.37 at radius 0; 18.15/19.91/21.50/49.50/59.87 at radius 1 chroma final), but it only times the project's own CUDA, HIP and AVX2 backends; no reachable page gives a number against VapourSynth-BM3D, FFmpeg bm3d or any other incumbent, so there is no comparative evidence and the tier stays D.
- **Verifier notes:** Record is accurate: numbers, license (GPL-2.0, LICENSE file is GPL v2), 88 stars, 15 forks, not archived or a fork, last commit 2026-09-26 all match. WebFetch's summary of the releases page dated R2.17 to 2024-09-26, but R2.17's notes cite CUDA 13.4.2 and the matching commit is dated Sep 26, 2026, so the record's 2026 date stands. Kept as D (not rejected) per the keep-and-document rule; under the prompt's strict rules it would qualify as not-notable-tier-d (88 stars).
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Shortcomings recorded by:** first-party README timings; third-party nssfactory PR
- **Pages the verifier opened:**
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/releases/tag/R2.13>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/commits>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/releases>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/releases/tag/R2.17>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/releases/tag/R2.8>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/README.md>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/RyougiKukoc/VapourSynth-BM3DCUDA-api4/HEAD/README.md>
  - <https://raw.githubusercontent.com/HomeOfVapourSynthEvolution/VapourSynth-BM3D/HEAD/README.md>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/pull/10>
- **Sources the enricher read:**
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/README.md>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/LICENSE>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/tree/master/source>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/tree/master/cpu_source>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/tree/master/tests>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/tree/master/.github/workflows>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/source/CMakeLists.txt>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/source/kernel.cu>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/source/source.cpp>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/cpu_source/CMakeLists.txt>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/cpu_source/cpuid.h>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/cpu_source/source.cpp>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/rtc_source/CMakeLists.txt>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/rtc_source/source.cpp>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/hip_source/CMakeLists.txt>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/sycl_source/CMakeLists.txt>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/tests/test_static_cuda_rolling.py>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/tests/test_rtc_cuda_rolling.py>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/.github/workflows/linux.yml>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/.github/workflows/windows.yml>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/releases/tag/R2.13>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/releases/tag/R2.14>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/releases/tag/R2.17>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/issues?q=is%3Aissue>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/issues/8>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/issues/17>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/issues/23>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/issues/31>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/pulls?q=is%3Apr>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/pull/34>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/pull/34/files>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/pull/35>
  - <https://raw.githubusercontent.com/HomeOfVapourSynthEvolution/VapourSynth-BM3D/HEAD/README.md>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/pull/23>
  - WebSearch: BM3DCUDA vs VapourSynth-BM3D speed fps comparison bm3dcpu (Doom9 snippets only; forum.doom9.org and avisynth.nl not opened, avisynth.nl EGRESS_BLOCKED)
  - WebSearch: "BM3DCUDA" "165.55" OR "i7-8700" bm3d radius fps doom9 (snippet only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/wolframrhodium/vapoursynth-bm3dcuda`) · [data/wave10/enrich/raw/github_com_wolframrhodium_vapoursynth_bm3dcuda.json](../../../data/wave10/enrich/raw/github_com_wolframrhodium_vapoursynth_bm3dcuda.json) (enrichment confidence 0.75)

</details>
