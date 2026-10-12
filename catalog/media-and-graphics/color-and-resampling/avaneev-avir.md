# AVIR / LANCIR (Aleksey Vaneev)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++ image resizers: AVIR, quality-first sinc resampling, plus LANCIR, a SIMD Lanczos-3. No speed comparison against other libraries exists.

| | |
|---|---|
| **Beats** | No third-party incumbent timed; LANCIR is compared only with the project's own AVIR algorithm |
| **Claimed result** | README: 'LANCIR offers up to three times faster image resizing in comparison to AVIR'; LANCIR 'is likely one of the fastest available for CPUs' (no numbers or named competitor). AVIR timing: 245 ms single thread, 74 ms with 8 threads for the 17.9 to 2.5 Mpixel downscale. |
| **Workload** | Downscale an 8-bit RGB 5184x3456 (17.9 Mpixel) image to 1920x1280 (2.5 Mpixel) with AVIR, single thread and 8 threads; LANCIR (Lanczos resizer in the same header library) is described as faster than AVIR. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-7700K, no overclocking (AVIR timing only) |
| **Compiler and flags** | Intel C++ Compiler 18.2 with AVX2 enabled, no explicit SIMD resizing code (AVIR timing only) |
| **Adoption** | 502 stars |
| **Last commit** | 2026-08-22 |
| **Links** | [repository](https://github.com/avaneev/avir) · [benchmark](https://raw.githubusercontent.com/avaneev/avir/HEAD/README.md) |

## Verdict

Nothing is compared against another resizer. The README times only AVIR itself (245 ms single-threaded, 74 ms with 8 threads, for an 8-bit RGB 5184x3456 to 1920x1280 downscale on an i7-7700K, Intel C++ 18.2 with AVX2, harness not published) and calls LANCIR 'up to three times faster' than AVIR with no numbers. The README's comparison plots are quality-only (frequency response and dynamic range), and their 'Lanczos-3' is the project's own CLancIR per other/frtest.cpp.

## Use it when

- You want a dependency-free, header-only C++ resizer you can vendor (MIT), with an 8-bit Lanczos-3 path that has NEON and WASM SIMD128 kernels as well as SSE2/AVX.
- Batch-resizing many same-sized frames (video pipelines, asset baking): one CLancIR object per thread reuses its filters and buffers between calls.
- Quality-critical downscaling or upscaling of photos where frequency response and low ringing matter more than time: AVIR's sinc and Peaked Cosine design, with selectable low-ringing parameter sets.
- 16-bit or float pipelines that need high-precision resampling (AVIR), accepting that it is slower than LANCIR.
- Fractional-offset sub-pixel shifts or non-uniform x/y scale factors (kx, ky, ox, oy parameters).

## Skip it when

- Choosing the fastest CPU resizer: the repo has no timing against stb_image_resize2, OpenCV, libvips, Pillow-SIMD or IPP, and issue #18 (2020) says of AVIR 'I just tried to use it for real-time processing and, well, it's not fast'. Benchmark against fast_image_resize or zimg first.
- 16-bit-accurate fast resizing: LANCIR accepts uint16 and float buffers, but its precision is limited to 8-bit.
- Built-in parallelism: neither resizer threads by default. AVIR needs your own CImageResizerThreadPool implementation, and LANCIR offers no slicing helper.
- Rotation, affine warps or EWA/radial filtering: only orthogonal (separable) resizing is provided, and the README warns about diagonal aliasing.
- One binary that adapts to the CPU: LANCIR picks SSE2, AVX or NEON from compiler macros, so a default x86-64 build gets SSE2 only unless you compile with AVX enabled.

## How it is fast

LANCIR precomputes a filter bank at 1000 fractional offsets (enough for its 8-bit precision), replicates taps per channel to fit SIMD width, and runs the multiply-accumulate loops with SSE2, AVX, NEON or WASM SIMD128 intrinsics chosen at compile time. It resizes vertically first in batches of output rows sized to a roughly 5.5 MB cache budget, then horizontally per row, and keeps its buffers between calls so batches of same-sized frames skip reallocation and filter regeneration. AVIR relies mostly on compiler auto-vectorization of plain float code, with optional SSE float4 and de-interleaved AVX float8 types; the README says the AVX de-interleaved path gives up to 50% over non-SIMD code for 1-2 channel images.

## Compared with alternatives

Pick LANCIR over stb_image_resize2-based siblings (stb-image-resize-opt, tir) when you need a C++ header with NEON and WASM SIMD Lanczos kernels and will measure speed yourself, and pick AVIR when resampling quality matters more than time. For documented speed wins, zimg (Lanczos about 2x faster than FFmpeg swscale) and fast_image_resize (faster than libvips) have measured numbers that this entry lacks.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard C/C++ library only) |
| **Minimum toolchain** | C++98 (both headers carry pre-C++11 fallbacks for nullptr and cstdint); tested with GCC, MSVC, Clang and Intel C++ |
| **Platforms** | any CPU with IEEE float; LANCIR SIMD on x86 SSE2/AVX, ARM NEON (32- and 64-bit), WASM SIMD128, scalar elsewhere; AVIR optional SSE (avir_float4_sse.h) and AVX (avir_float8_avx.h) types |
| **Thread safety** | AVIR CImageResizer is documented as thread-safe: one object can serve concurrent resizes, but splitting a single image across threads needs your own CImageResizerThreadPool. CLancIR is not thread-safe because it reuses internal buffers, so use one object per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Floating-point output is not clamped in either resizer, so sinc and Lanczos overshoot can leave values outside [0,1]. Issue #12 reported green and pink pixels when resizing float buffers while uint8 was fine. Clamp before converting.
- AVIR at k=1 is not an identity copy: it always low-pass filters first and applies a correction filter at the end. Its default parameters may change between releases, so save the parameter set if you need reproducible output.
- AVIR's sRGB gamma correction is off by default, and when enabled it also applies to alpha unless Vars.AlphaIndex is set. The README warns it can produce 'greenish/reddish/bluish haze' near edges.
- Version 3.1 removed the scanline 'unbiasing' added in 2.8, which the author now calls a compiler-dependent statistical error, and fixed a 16-bit to 8-bit conversion bug. Output from 2.x and 3.1 differs.

## Known shortcomings

- No comparison against stb_image_resize or ImageMagick anywhere in the README, lancir.h or other/ (frtest.cpp measures quality against Lanczos-3): the only numbers are LANCIR 'up to 3x' faster than AVIR itself and bare AVIR timings of 245 and 74 ms on an i7-7700K with ICC 18.2, so tier D.
- Enricher (2026-10-04): nothing is compared against another resizer; the README times only AVIR itself (245 ms single-threaded, 74 ms with 8 threads, 5184x3456 to 1920x1280 on an i7-7700K, Intel C++ 18.2 with AVX2, harness not published, AVIR version unstated and predating the 3.0 upsizing speedup) and calls LANCIR 'up to three times faster' than AVIR without numbers. No timing code exists in the repo: other/frtest.cpp is a quality test that includes a private header and uses CLancIR itself as the 'Lanczos-3' baseline; bin/ holds prebuilt binaries whose sources are not published (issue #26). Floating-point output is not clamped (issue #12 green/pink pixels); k=1 is not an identity copy; version 3.1 removed the 2.8 'unbiasing' as a compiler-dependent statistical error, so 2.x and 3.1 output differ. Tier D stands.

## Caveats and trade-offs

Tier D: the README's only speed comparison is LANCIR against the author's own AVIR ('up to three times faster', no numbers); AVIR's 245 ms / 74 ms (1 / 8 threads) downscale timing on an i7-7700K with Intel C++ 18.2 AVX2 has no baseline, and the timing harness is not in the repo. LANCIR's 'likely one of the fastest available for CPUs' names no competitor. The README's Comparison section (other/frtest.cpp, _fr_up.png, _dr_up.png) is a quality comparison (frequency response, dynamic range) against Lanczos-3, not a speed result. lancir.h contains no benchmark figures. No numeric comparison against stb_image_resize or ImageMagick exists in the repo; a web search found none from third parties either. Notability is borderline (502 stars, 49 forks), though the README lists users (MLV App, Trainz, LVC Audio, Contaware, PretextSnapshot). AVIR's focus is quality, not speed. Separate library from the author's r8brain-free-src (audio resampler); not a duplicate.

Header-only C++ (lancir.h has scalar, SSE2, AVX, NEON and WASM SIMD128 paths); AVIR targets high quality (sinc with Peaked Cosine window), orthogonal resizing may show diagonal aliasing; LANCIR precision limited to 8-bit; LANCIR object is not thread-safe.

## Maintenance

Maintained by its single author (AVIR 3.1, LANCIR 3.1.1, last commit 2026-08-22, no open issues or PRs), MIT-licensed, header-only with no dependencies, so easy to vendor; the README asks for the credit line 'AVIR image resizing algorithm designed by Aleksey Vaneev'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The README gives only absolute AVIR timings (245 ms single thread, 74 ms with 8 threads, i7-7700K, Intel C++ 18.2 AVX2) and an unquantified 'up to three times faster' LANCIR-vs-AVIR claim; no third-party resizer (stb_image_resize, ImageMagick, OpenCV, libvips, IPP) is timed anywhere in the repo, and the Comparison section (other/frtest.cpp) measures frequency response and dynamic range against Lanczos-3, not speed. No speed comparison against an incumbent, so D.
- **Verifier notes:** Confirmed at D: repo top level (avir.h, avir_dil.h, avir_float4_sse.h, avir_float8_avx.h, lancir.h, bin/, other/) and other/ (frtest.cpp, avirdoxy.txt, three PNG plots) hold no speed comparison against any third-party resizer. Metadata checked: MIT (LICENSE and lancir.h header), 502 stars, not archived, not a fork, last commit 2026-08-22 (LANCIR 3.1.1). Below 1k stars at tier D, but keep per the keep-and-document rule.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** none (self-timings only)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/avaneev/avir/HEAD/README.md>
  - <https://raw.githubusercontent.com/avaneev/avir/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/avaneev/avir/HEAD/lancir.h>
  - <https://github.com/avaneev/avir>
  - <https://github.com/avaneev/avir/commits>
  - <https://github.com/avaneev/avir/tree/master/other>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/avaneev/avir/HEAD/README.md>
  - <https://raw.githubusercontent.com/avaneev/avir/HEAD/lancir.h>
  - <https://raw.githubusercontent.com/avaneev/avir/HEAD/avir.h>
  - <https://raw.githubusercontent.com/avaneev/avir/HEAD/avir_dil.h>
  - <https://raw.githubusercontent.com/avaneev/avir/HEAD/avir_float4_sse.h>
  - <https://raw.githubusercontent.com/avaneev/avir/HEAD/avir_float8_avx.h>
  - <https://raw.githubusercontent.com/avaneev/avir/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/avaneev/avir/HEAD/other/frtest.cpp>
  - <https://github.com/avaneev/avir/issues?q=is%3Aissue>
  - <https://github.com/avaneev/avir/issues/18>
  - <https://github.com/avaneev/avir/issues/12>
  - <https://github.com/avaneev/avir/issues/26>
  - <https://github.com/avaneev/avir/issues/8>
  - <https://github.com/avaneev/avir/tree/master/bin>
  - <https://github.com/avaneev/avir/pulls?q=is%3Apr>
  - <https://gist.github.com/bardex/b3668ea77c9ad5d47dd72e01101438d6>
  - WebSearch: LANCIR avir lancir.h benchmark stb_image_resize2 OR libvips OR OpenCV resize speed comparison (no third-party LANCIR or AVIR timings found)
  - WebSearch: "CLancIR" OR "lancir" resize benchmark ms github (no third-party timings found)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/avaneev/avir`) · [data/wave10/enrich/raw/github_com_avaneev_avir.json](../../../data/wave10/enrich/raw/github_com_avaneev_avir.json) (enrichment confidence 0.75)

</details>
