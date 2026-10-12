# xxYUV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Small MIT C++ BT.709 RGB/YUV 4:2:0 converter (SSE2/SSSE3/AVX2/NEON) whose README claims to beat libyuv and Accelerate.

| | |
|---|---|
| **Beats** | libyuv (version not stated) and Apple Accelerate |
| **Claimed result** | README, microseconds, xxYUV vs libyuv: i7-8700B AVX2 encode YU12/YV12 31 vs 48, NV12/NV21 33 vs 39; decode YU12/YV12 46 vs 60, NV12/NV21 39 vs 54. Apple M1 NEON encode 37 vs 48 and 38 vs 49; decode 38 vs 122 and 42 vs 89. That is 1.2-1.55x on encode and 1.3x (AVX2) to 3.2x (M1 NEON) on decode (derived from page data). xxYUV also beats Accelerate on every reported row (M1 NEON decode 38 vs 62, i7 AVX2 encode 31 vs 83). On M1 x86 builds (SSSE3) encode is 134 vs libyuv 146. |
| **Workload** | RGB to YUV encode and YUV to RGB decode for YU12/YV12 and NV12/NV21 formats; times in microseconds for an unspecified image size. |
| **Metric** | latency |
| **Hardware** | Apple M1 (NEON, SSSE3 and SSE2 under Rosetta); Intel Core i7-8700B (AVX2) |
| **Adoption** | 81 stars |
| **Last commit** | 2021-10-20 |
| **Links** | [repository](https://github.com/metarutaiga/xxYUV) · [benchmark](https://github.com/metarutaiga/xxYUV/blob/master/README.md) |

## Verdict

First-party README tables give microseconds per conversion for xxYUV against libyuv (version and matrix not stated) and Apple Accelerate on an Apple M1 (NEON, plus x86 rows presumably under Rosetta) and an i7-8700B (AVX2): about 1.2-1.55x faster encode and 1.3x (AVX2) to 3.2x (M1 NEON) faster decode than libyuv. Compiler, flags, image size and pixel layout are not stated and the harness is not public; because only the 4-channel paths are vectorised, the SIMD rows must be RGBA/BGRA, and the microsecond scale implies a small cache-resident image (inference).

## Use it when

- Converting RGBA/BGRA frames to or from I420/NV12/NV21 with BT.709 coefficients when the width is a multiple of 32 (AVX2) or 16 (SSE2/NEON).
- Apple Silicon or AVX2 desktops where you want a few-file MIT source drop instead of building libyuv.
- Preview, thumbnail or GPU-upload paths where a 1-3 code-value difference from a reference converter is acceptable.
- Projects built with Clang or MSVC, where the per-function target attributes (Clang) or MSVC's intrinsic rules let the runtime dispatch work as written.

## Skip it when

- RGB24 (3-channel) data: every SIMD loop runs only for 4 channels, so 3-channel conversion is the scalar loop on all CPUs, and the scalar encoder applies the R coefficient to byte 2 (the SIMD encoders and the decoder treat byte 0 as R), so RGB24 encode swaps R and B unless the swizzle flag is inverted.
- Widths that are not a multiple of the SIMD block: for 4-channel and YUVA conversions the code skips the scalar tail ('if (componentRGB == 4) continue;' after the SIMD loop), leaving the rightmost (halfWidth mod 8, or mod 16 on AVX2) x2 columns unwritten, e.g. 24 columns of a 1080-wide frame on AVX2.
- Video-range content with super-whites on ARM: the NEON decode narrows (Y-16)\*149&gt;&gt;7 with a non-saturating vshrn_n_u16, so luma 236-255 wraps to 0-22 (near black); the x86 paths keep 16 bits and do not wrap.
- Anything beyond 8-bit 4:2:0 BT.709: no BT.601 or BT.2020, no 4:2:2/4:4:4, no 10-bit, no scaling or rotation.
- Code that needs maintenance or tests: last commit 20 Oct 2021, no tests in the repository, and the linked benchmark harness cannot be found.

## How it is fast

Each converter is one template instantiated per (channels, swizzle, interleaved, U-first, range) combination and compiled several times from the same .inl file with HAVE_NEON/SSE2/SSSE3/AVX2 defined, then picked once by CPUID into a function-local static pointer. Kernels process two rows at a time with 8-bit fixed-point coefficients: decode uses 16-bit mulhi (x86) or 8-bit widening multiplies (NEON_FAST, always on for ARM), encode uses maddubs+hadd (SSSE3/AVX2) or widening multiply-accumulate with pairwise adds for 2x2 chroma averaging (NEON), and results are interleaved with unpack transposes or vld4/vst4. Precision is traded for fewer, narrower multiplies.

## Compared with alternatives

Pick xxYUV over libyuv, sparkyuv or yuvutils-rs only when you need a tiny MIT C++ drop for BT.709 RGBA/NV12 on M1 or AVX2 with 32-pixel-aligned widths; sparkyuv covers 4:4:4 to 4:1:0, NV16/NV24 and many matrices, yuvutils-rs is the Rust option with like-for-like rows against libyuv, and libyuv stays the safe default for odd sizes, RGB24 and other matrices.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (Apple Accelerate is only a benchmark comparison; the AMX path uses undocumented Apple instructions taken from dougallj's reverse-engineering gists) |
| **Minimum toolchain** | C++20 for the designated-initializer convenience wrappers in yuv2rgb.h, rgb2yuv.h and yuv.h (define xxYUV_DEPRECATED to drop them); Clang or MSVC for working runtime dispatch; no build files are provided |
| **Platforms** | x86/x86-64 (SSE2 baseline, SSSE3 and AVX2 chosen at run time by CPUID), 32/64-bit ARM with NEON, Apple M1 AMX for YU12 decode; other targets get the scalar loop. AVX-512 kernels exist in yuv2rgb.inl but are never instantiated. |
| **Thread safety** | Not documented; the converters keep no shared mutable state and pick the kernel through C++11 function-local statics, so concurrent calls look safe (inference from the code). |
| **Drop-in for the baseline** | no |

## Gotchas

- The planar entry points pass strideU twice (converter(..., strideY, strideU, strideU, ...)), so a caller-supplied strideV is ignored in yuv2rgb_yu12/yv12 and rgb2yuv_yu12/yv12.
- Under GCC the target-attribute macro expands to nothing (it is defined only for __llvm__), so the AVX2/SSSE3 kernels need -mavx2/-mssse3 on the whole file, which also lets the compiler use AVX2 in the fallback paths and defeats the CPUID dispatch (inference from the macro).
- Outputs differ by platform: NEON_FAST uses 6-7 bit chroma coefficients (full-range B gain 1.844 vs 1.863), x86 decode scales by coefficient\*255/256, and the SSSE3/AVX2 encoders halve the luma weights so full-range white encodes to Y=253 (254 on NEON and scalar, both truncating).
- Odd widths or heights lose the last column or row (loops run over width&gt;&gt;1 and height&gt;&gt;1).

## Known shortcomings

- First-party README tables only (Apple M1 and i7-8700B; decode up to 3.2x derived from page data); the linked xxImGui harness has no YUV code at head, so nothing reproduces the numbers.
- Output bugs by code reading (not proven behind the README numbers): the RGBA and YUVA SIMD loops continue past the scalar tail, so columns after the last 16-pixel (NEON, SSE2) or 32-pixel (AVX2) block are never written (24 columns on a 1080-wide AVX2 frame); the NEON video-range decode uses a non-saturating vshrn_n_u16 so luma 236-255 wraps to 0-22; scalar rgb2yuv applies the R coefficient to byte 2, so the RGB24 encode swaps R and B against the SIMD path; strideV is ignored (strideU passed twice). SIMD exists only for 4-channel data, so the README's SIMD rows must be RGBA; the target attributes are Clang-only, so GCC CPUID dispatch is broken; BT.709 8-bit 4:2:0 only; the AVX-512 code is never instantiated; the benchmark harness was still not found.

## Caveats and trade-offs

First-party, no compiler or flags, no libyuv version, image size not stated. The README points to https://github.com/metarutaiga/xxImGui/tree/experimental as the benchmark environment, but at that branch's head (repository archived 17 Aug 2025) the plugin directory holds only sample and validator plugins with no YUV code, and its commits up to Oct 2021 do not mention YUV or libyuv, so the harness cannot be inspected. Conversions use 8-bit fixed-point BT.709 coefficients (Y scaled by 256, vqdmulh/mulhi multiplies); output accuracy versus libyuv is not reported and the libyuv matrix used is unknown. Last commit 20 Oct 2021.

Small C++ RGB/YUV converter with SSE2, SSSE3, AVX2, NEON and AMX paths; narrow format coverage compared with libyuv.

## Maintenance

Abandoned since October 2021 (64 commits, 2 closed questions, no PRs, no tests) but MIT-licensed and about fifteen small files, so it is easy to vendor if you first fix the tail, strideV, video-range wrap and RGB24 channel-order bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables against libyuv and Apple Accelerate on Apple M1 and i7-8700B; the linked harness (xxImGui experimental branch) no longer contains any YUV benchmark code that I could find, and no compiler, flags, libyuv version or image size are given.
- **Verifier notes:** All README numbers match the record. Tier stays C: the benchmark harness the README links to is not findable at the xxImGui experimental head, so I could not read the measured code. The record's 'SSSE3 and SSE2 under Rosetta' for the M1 table is an inference (the README just lists x86 SIMD rows under Apple M1).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/metarutaiga/xxYUV>
  - <https://github.com/metarutaiga/xxYUV/commits>
  - <https://github.com/metarutaiga/xxYUV/tree/master>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/README.md>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/yuv2rgb.inl>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/rgb2yuv.inl>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/yuv2rgb.h>
  - <https://github.com/metarutaiga/xxImGui/tree/experimental>
  - <https://github.com/metarutaiga/xxImGui/tree/experimental/plugin>
  - <https://github.com/metarutaiga/xxImGui/tree/experimental/plugin/validator>
  - <https://github.com/metarutaiga/xxImGui/tree/experimental/plugin/sample>
  - <https://github.com/metarutaiga/xxImGui/tree/experimental/plugin/3rdParty>
  - <https://github.com/metarutaiga/xxImGui/commits/experimental/?until=2021-10-21>
  - <https://raw.githubusercontent.com/metarutaiga/xxImGui/experimental/plugin/validator/validator.cpp>
  - <https://raw.githubusercontent.com/metarutaiga/xxImGui/experimental/plugin/sample/sample.cpp>
  - <https://raw.githubusercontent.com/metarutaiga/xxImGui/experimental/.gitmodules>
- **Sources the enricher read:**
  - <https://github.com/metarutaiga/xxYUV>
  - <https://github.com/metarutaiga/xxYUV/commits/master>
  - <https://github.com/metarutaiga/xxYUV/issues?q=is%3Aissue>
  - <https://github.com/metarutaiga/xxYUV/issues/1>
  - <https://github.com/metarutaiga/xxYUV/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/README.md>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/yuv2rgb.h>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/yuv2rgb.cpp>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/yuv2rgb.inl>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/rgb2yuv.h>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/rgb2yuv.cpp>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/rgb2yuv.inl>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/cpu.h>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/cpu.cpp>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/yuv.h>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/yuv2yuva.h>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/yuv2yuva.cpp>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/yuv2yuva.inl>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/apple_amx.h>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/yuv2rgb_amx.h>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/yuv2rgb_amx.cpp>
  - <https://github.com/metarutaiga?tab=repositories>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/metarutaiga/xxyuv`) · [data/wave10/enrich/raw/github_com_metarutaiga_xxyuv.json](../../../data/wave10/enrich/raw/github_com_metarutaiga_xxyuv.json) (enrichment confidence 0.75)

</details>
