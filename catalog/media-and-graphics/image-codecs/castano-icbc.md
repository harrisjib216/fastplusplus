# ICBC (high quality SIMD BC1 encoder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Single-header SIMD BC1 (DXT1) block encoder from NVTT; at the highest quality levels it is faster than RGBCX only when built with AVX2 or AVX-512.

| | |
|---|---|
| **Beats** | RGBCX 1.12 (levels 0-18), squish 1.15, stb_dxt 1.09 with improvements proposed by Rich Geldreich and Ignacio Castano (not stock), and AMD CMP_Core V4.0.4855 |
| **Claimed result** | Chart only (doc/kodim-chart.png, average PSNR on Kodim+Waterloo versus encode time, time unit unlabeled; readings approximate): at the top quality point (PSNR about 30.9) ICBC-AVX512 takes about 5.5 versus about 20.6 for RGBCX and about 19.3 for ICBC-Scalar (about 3.7x versus RGBCX, derived from chart reading); near PSNR 30.83-30.84 ICBC-AVX512 is about 1.1 versus about 5.1 for RGBCX. squish sits at about 7.4 for PSNR about 30.43 and AMD CMP at about 14.6 for PSNR about 30.25, both above the ICBC-AVX512 curve (under 1.0 at those PSNRs). stb_dxt tops out near PSNR 30.06 at about 0.3, where ICBC and RGBCX are similar. ICBC-Scalar is slower than RGBCX at almost every quality level, so the lead comes from SIMD (AVX-512 in the chart). |
| **Workload** | Average PSNR of BC1 encoders against encode time on the Kodim and Waterloo image sets, several quality levels per encoder. |
| **Metric** | throughput |
| **Adoption** | 131 stars; the BC1 encoder used by NVTT |
| **Last commit** | 2022-11-09 |
| **Links** | [repository](https://github.com/castano/icbc) · [benchmark](https://raw.githubusercontent.com/castano/icbc/HEAD/README.md) |

## Verdict

The only comparison is the author's chart of average PSNR on the Kodim and Waterloo sets against encode time, with an unlabelled time unit, made with ICBC 1.03 (current header 1.05), RGBCX 1.12, a modified stb_dxt 1.09, squish 1.15 and AMD CMP_Core. At the top quality (about 30.9 dB), ICBC-AVX512 takes about 5.5 units against about 20.6 for scalar RGBCX; ICBC-Scalar is slower than RGBCX at most levels, so the lead is SIMD rather than the algorithm. The repo's harness (icbc_test.cpp) times only ICBC, on the 24 Kodak images alone, multithreaded through ic_pfor, so the chart's baseline timings, threading and machine cannot be reproduced from public code. Since v1.03, commits from September 2022 changed low-quality inset handling and added level 0, so the chart's curve no longer describes the current code. Third-party data in Goofy's README (i7-7820HQ, one thread) measured the older icbc v1.0 SSE2 at 24 MP/s and 41.00 dB, against rgbcx 1.08 level 0 at 60 MP/s and 40.85 dB and stb_dxt at 43 MP/s and 40.82 dB. No correctness bug was found behind the BC1 numbers.

## Use it when

- Offline or build-pipeline BC1 compression where you want the top quality band (above about 30.7 dB average on the author's Kodim+Waterloo chart). There the AVX-512 build reaches RGBCX's best quality in roughly a quarter of the time.
- x86-64 build machines where you can compile a dedicated AVX2 or AVX-512 binary. The scalar build is slower than RGBCX at almost every quality level on the same chart.
- Texture tools that already use NVTT, or that need BC1 tuned to a specific GPU vendor's decoder rounding (D3D10, NVIDIA, AMD/Apple M1, Intel).
- Embedding with no build system: one MIT header with no dependencies beyond the C/C++ standard headers and SIMD intrinsics.

## Skip it when

- Low and mid quality BC1. In the chart, stb_dxt and RGBCX's lowest levels match ICBC below about 30.1 dB, and RGBCX (about 30.52 dB at about 0.5 time units) beats the AVX-512 ICBC points at about 30.38 and 30.57 dB (about 0.75 each). For real-time encoding, Goofy is far faster at much lower quality.
- Anything beyond BC1 (BC3/4/5/7): compress_bc3 returns 0 and writes nothing, and the alpha/BC4/BC5 encoders are open issue #3. The README itself recommends RGBCX as the better-supported library.
- Shipping one portable x86 binary: there is no runtime CPU dispatch, so an AVX-512 or AVX2 build faults on CPUs without those instructions, and a portable build falls back to the slow SSE2 or scalar path.
- PowerPC: according to open PR #10 (August 2026), the AltiVec/VMX back end never compiled, with typos, missing mask/any/all functions and a wrong vec_div.
- Teams that need maintenance: the last commit was 2022-11-09, and PR #10 and 6 issues are open with no maintainer response.

## How it is fast

The quality ladder runs from bounding-box fit (level 0) through box fit plus least-squares endpoints (level 1) to squish-style cluster fit over every order-preserving 4-cluster partition (968 combinations) and 3-cluster partition (152), with 3-colour mode at levels 8 and 9 and iterative endpoint refinement at level 9. Near-duplicate colours are merged first, under a per-level threshold, to cut the combination count. Each partition's least-squares error comes from summed-area tables, as in rgbcx, and the cluster-fit loop is vectorised over 4/8/16 lanes. The SIMD back end (SSE2, SSE4.1, AVX, AVX2, AVX-512, NEON, AltiVec) is chosen at compile time, and the AVX2 and AVX-512 paths use permute instructions for table lookups. The SIMD path does most of the work: in doc/results.txt the AVX-512 build is about 9x faster than the scalar build on Sky Lake (0.166 s vs 1.519 s), with identical PSNR.

## Compared with alternatives

Pick ICBC over rgbcx in bc7enc only when you need the highest-quality BC1 on AVX2/AVX-512 build machines and can live with an unmaintained, BC1-only header. Otherwise rgbcx (also BC3-5, faster in the mid-quality range) is the default, and Goofy is the choice for real-time speed at a large quality loss.

## Integration

| | |
|---|---|
| **Form** | header-only (define ICBC_IMPLEMENTATION in one translation unit) |
| **Dependencies** | none (standard C headers plus x86/ARM/PowerPC intrinsics headers); the test harness adds stb_image, stb_image_write and ic_pfor.h |
| **Minimum toolchain** | C++11 (icbc_test.cpp's compile comment reads 'g++ icbc_test.cpp -O3 -mavx2 -lpthread -std=c+=11', a typo for c++11; build.bat uses MSVC 2019 'cl /O2 /arch:AVX512'; results.txt runs used MSVC 2017/2019, clang 11/13 and gcc 8.3/10) |
| **Platforms** | x86/x86-64 (SSE2 to AVX-512, selected at compile time from __AVX512F__/__AVX2__/__AVX__/__SSE4_1__ or ICBC_SIMD), ARM NEON, scalar fallback; the PowerPC VMX path is broken |
| **Thread safety** | Call icbc::init() once before encoding: it fills global lookup tables and the default decoder. compress_bc1 then reads only those tables, and icbc_test.cpp calls it from all threads at once through ic_pfor. |
| **Drop-in for the baseline** | no |

## Gotchas

- Encoding before icbc::init() leaves the single-colour and cluster tables zeroed. The decoder passed to init changes the produced blocks, so encode for the decoder you ship on.
- Automatic NEON selection checks only __ARM_NEON__. Compilers that define only the ACLE macro __ARM_NEON (GCC for AArch64, for example) may silently fall back to scalar unless ICBC_SIMD is set to -1.
- three_color_black=true (used in the chart for ICBC and RGBCX) stores black texels with the transparent-black index. That raises PSNR but makes those texels alpha 0 when the texture is sampled as RGBA.
- Input is 16 float RGBA texels per block, not 8-bit pixels. Conversion, edge padding and block layout are the caller's job, and the test harness rounds image sizes down to multiples of 4.

## Known shortcomings

- Only a chart: doc/results.txt holds ICBC-only timings, icbc_test.cpp times ICBC alone, and the chart's machine is unnamed. The lead is AVX-512 against scalar RGBCX; ICBC-Scalar is slower than RGBCX almost everywhere, and the stb_dxt 1.09 baseline was modified. Texture encoder with baselines outside the category list.
- The chart was made with v1.03 and the September 2022 commits changed the low quality levels, so it is stale for v1.05; the harness times ICBC only on the 24 Kodak images (no Waterloo set), multithreaded via ic_pfor. Scalar ICBC is slower than RGBCX, and RGBCX beats ICBC-AVX512 at about 30.4-30.6 dB; ICBC wins only above about 30.7 dB. compress_bc3 is a public stub that returns 0 and writes nothing; the VMX backend never compiled (open PR #10); no runtime SIMD dispatch (NEON auto-select checks only __ARM_NEON__).

## Caveats and trade-offs

The result is a first-party PSNR-versus-time chart with no hardware, compiler or time unit; the AVX-512 series implies an AVX-512 CPU but the machine is not named. doc/results.txt holds ICBC-only timings (Sky Lake AVX512, Coffee Lake, Ryzen Threadripper 2990WX, Apple M1 Pro, Raspberry Pi, etc.) with no baseline rows, and icbc_test.cpp (multithreaded through ic_pfor) runs only ICBC, so how the baselines were timed (threading, flags) is unknown. The comparison pits ICBC's AVX-512 path against scalar RGBCX; ICBC-Scalar is slower than RGBCX across most of the range. stb_dxt was a modified 1.09, not the stock release. The README itself says RGBCX is most likely a better choice for a well supported, actively developed library, and RGBCX is already catalogued. Texture-encoder baselines (stb_dxt, rgbcx, squish, nvtt) are outside the category's baseline list. Last commit 2022-11-09.

BC1 (DXT1) only, single header, SIMD variants up to AVX-512; quality levels trade encode time for PSNR.

## Maintenance

Abandoned since 2022-11-09 (157 commits, 131 stars, MIT), though it remains NVTT's BC1 encoder. It is small and dependency-free enough to vendor; build per-ISA binaries and do not rely on the VMX or BC3 entry points.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party PSNR-versus-time chart (doc/kodim-chart.png) with an unlabeled time axis and no machine or compiler; the repo's harness icbc_test.cpp times only ICBC, and doc/results.txt lists ICBC-only timings per CPU and compiler with no baseline rows, so the baseline numbers cannot be traced to public code.
- **Verifier notes:** No table of baseline numbers exists in the repo; doc/results.txt is ICBC-only. Chart readings in the record match the image. NVTT is not a separate baseline here (ICBC is NVTT's BC1 encoder). Rich Geldreich's BC1 benchmark posts (richg42.blogspot.com) compare stb_dxt 1.09, icbc and rgbcx 1.12 but blogs are blocked, so not used.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** Third-party single-thread run in the Goofy README (i7-7820HQ): icbc v1.0 24 MP/s at 41.00 dB versus rgbcx 1.08 60 MP/s and stb_dxt 43 MP/s.
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/README.md>
  - <https://github.com/castano/icbc>
  - <https://github.com/castano/icbc/commits/master>
  - <https://github.com/castano/icbc/tree/master/doc>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/doc/results.txt>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/doc/kodim-chart.png>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/doc/vector-scaling.png>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/icbc_test.cpp>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/build.bat>
  - <https://raw.githubusercontent.com/richgel999/bc7enc/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/castano/icbc>
  - <https://github.com/castano/icbc/commits/master>
  - <https://github.com/castano/icbc/issues?q=is%3Aissue>
  - <https://github.com/castano/icbc/issues/9>
  - <https://github.com/castano/icbc/pulls?q=is%3Apr>
  - <https://github.com/castano/icbc/pull/10>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/README.md>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/icbc.h>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/icbc_test.cpp>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/ic_pfor.h>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/build.bat>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/doc/results.txt>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/doc/kodim-chart.png>
  - <https://raw.githubusercontent.com/castano/icbc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/README.md>
  - <https://github.com/aras-p?tab=repositories&q=compression>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/castano/icbc`) · [data/wave10/enrich/raw/github_com_castano_icbc.json](../../../data/wave10/enrich/raw/github_com_castano_icbc.json) (enrichment confidence 0.75)

</details>
