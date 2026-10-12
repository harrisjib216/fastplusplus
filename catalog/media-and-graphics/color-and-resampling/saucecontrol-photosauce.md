# MagicScaler (PhotoSauce)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟢 active

> .NET image resizing pipeline (MagicScaler) that makes JPEG thumbnails 5-9x faster than Magick.NET in its author's runs.

| | |
|---|---|
| **Beats** | ImageMagick via Magick.NET-Q8-AnyCPU 12.2.0 (also System.Drawing, ImageSharp, SkiaSharp, NetVips/libvips 8.13.2) |
| **Claimed result** | Load, resize to 150 px, save 12 JPEGs of about 1 MP (BenchmarkDotNet ShortRun means). Windows 10 x64, Xeon W-11855M: MagicScaler 46.85 ms vs ImageMagick (Magick.NET-Q8 12.2.0) 345.99 ms, about 7.4x (derived from page data); NetVips 100.92 ms, SkiaSharp 117.43 ms, ImageSharp 115.90 ms, System.Drawing 354.73 ms. Ubuntu 20.04 x64, same CPU: 99.8 ms vs ImageMagick 522.6 ms, about 5.2x (derived from page data); NetVips 380.5 ms, System.Drawing 271.7 ms. Windows 11 ARM64 (Snapdragon): 65.72 ms vs ImageMagick 588.63 ms, about 9.0x (derived from page data). Linux ARM64 (Raspberry Pi 4b): 214.7 ms vs ImageMagick 1,688.5 ms. Resize-only synthetic (blank 1280x853 to 150x99, Windows x64): 621.8 us vs ImageMagick 39,426.5 us, which the author says to take with a grain of salt. |
| **Workload** | Semi-real-world benchmark: load 12 JPEGs of about 1 MP, resize to 150 px wide thumbnails, save as JPEG, BenchmarkDotNet ShortRun. |
| **Metric** | latency |
| **Hardware** | Intel Xeon W-11855M 3.20 GHz (6 cores, 12 threads) on Windows 10 x64 and Ubuntu 20.04; Snapdragon Compute Platform on Windows 11 ARM64; Raspberry Pi 4b 2GB on Ubuntu 22.04 ARM64 |
| **Compiler and flags** | .NET 6.0.10 RyuJIT (X64 AVX2; Arm64 AdvSIMD), SDK 7.0.100-rc.2 on Windows x64 and SDK 6.0.402 on Ubuntu and Windows ARM64; BenchmarkDotNet 0.13.2.1974-nightly ShortRun (IterationCount=5, WarmupCount=3, LaunchCount=1, UnrollFactor=32 or 8). ImageMagick (Magick.NET-Q8-AnyCPU 12.2.0), libvips 8.13.2 and libjpeg-turbo (PhotoSauce.NativeCodecs.Libjpeg 2.1.4-preview1) are prebuilt NuGet binaries; their compiler flags are not stated. |
| **Adoption** | 735 stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/saucecontrol/PhotoSauce) · [benchmark](https://github.com/saucecontrol/PhotoSauce/blob/master/readme.md) |

## Verdict

The author ran a locally modified copy of bleroy/core-imaging-playground in Nov 2022 (BenchmarkDotNet ShortRun, .NET 6.0.10, MagicScaler 0.13.2 with libjpeg-turbo, Magick.NET-Q8 12.2.0): loading, resizing to 150 px and saving 12 JPEGs of about 1 MP took 46.85 ms against 345.99 ms for ImageMagick on a Xeon W-11855M under Windows 10, about 7.4x, and 65.72 against 588.63 ms on a Snapdragon ARM64 dev kit. The 'Linux x64' table (99.8 against 522.6 ms) is labelled WSL2, so it ran in a VM on the same Windows laptop, not on bare-metal Linux.

## Use it when

- .NET server code (CMS, e-commerce, upload handlers) that turns large JPEGs into thumbnails or web-size renditions at high throughput on Windows or Linux.
- You want good-quality defaults (linear-light blending, automatic filter choice, post-resize unsharp mask, colour-profile normalisation) without writing filter or ICC code.
- Memory-constrained parallel batch resizing: in the author's 351-image Bee Heads run MagicScaler peaked at 420 MB and 37,153 ms CPU against ImageMagick's 878 MB and 277,780 ms.
- Strong reductions (roughly 3x and up) of JPEG input, where decode-time DCT scaling and planar processing give the biggest gains.

## Skip it when

- C or C++ projects: it is C# only; libvips, fast_image_resize or Skia are the native options in this category.
- macOS: the README says it runs on Windows and Linux, and the native codec packages ship Windows and glibc Linux binaries only.
- Many small images through an encode step: issue #180 (2025) reports 144 images of 256x256 resized to about 144x144 taking 360 ms against 130 ms with GDI+, even with nearest-neighbour; no maintainer reply was visible.
- BMP or TIFF input on Linux: the README lists them as the notable formats the cross-platform codec plugins do not support.
- Bit-exact or reference-filter output: hybrid mode trades a little quality for speed, and the defaults pick filter, sharpening and JPEG quality for you; set HybridMode=Off and explicit Interpolation and Sharpen values if you need control.

## How it is fast

Hybrid scaling: for large reductions it asks libjpeg-turbo for a DCT-domain scaled decode (scale_denom) or box-averages by a power of two (HybridScaleTransform), then runs the high-quality filter only for the remaining ratio. JPEGs are processed planar: Y is resampled (in approximate linear light) and Cb/Cr at chroma resolution, then handed straight to the encoder, so no full-size YCbCr-to-RGB conversion happens. Resampling is a separable convolution with precomputed kernel maps, hand-written SSE/AVX2/FMA convolvers on x86 (System.Numerics.Vector fallbacks elsewhere), fixed-point UQ15 or float paths, and lookup-table gamma conversion. The pipeline streams lines through sliding and windowed buffers from a pool instead of materialising whole images, which keeps peak memory low.

## Compared with alternatives

Pick it over ImageSharp when you are on .NET for Windows or Linux and want the fastest JPEG thumbnailing (46.85 ms against ImageSharp's 115.90 ms in the same Windows x64 run). Pick ImageSharp for pure-managed portability including macOS, and libvips (NetVips) or Skia when you need native, cross-language or macOS support; NetVips was 2.2x slower here on Windows x64 and 3.8x on WSL2 Linux (derived from page data).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | None on Windows (WIC codecs); on Linux one or more PhotoSauce.NativeCodecs.\* NuGet plugins with bundled native libraries (libjpeg-turbo built from a custom psjpeg vcpkg port, libpng, libwebp, libheif, libjxl, giflib). |
| **Minimum toolchain** | Library targets net8.0 and net472, with net462, netstandard2.0 and netstandard2.1 added in the Dist build (MagicScaler.csproj); hardware-intrinsic paths only on .NET Core 3.0+ targets. |
| **Platforms** | Windows x86, x64 and ARM64; Linux glibc x64 and ARM64. Hand-written intrinsics on x86 SSE2/AVX/AVX2 only; other architectures use Vector&lt;T&gt; or scalar paths. |
| **Thread safety** | Not documented; ProcessImage is static and the README's own parallel benchmark calls it concurrently from Parallel.ForEach, one image per call. |
| **Drop-in for the baseline** | no |

## Gotchas

- Default HybridMode=FavorQuality changes the work done: for about 1 MP to 150 px it decodes at half size and then uses Catmull-Rom on the rest (SettingUtil.GetDefaultInterpolation), while the Magick.NET harness decodes full size and applies ImageMagick's default Lanczos (MagickCore/resize.c), roughly 17 against 51 filter taps per output pixel per axis (derived from code).
- In planar JPEG mode only luma is linearised, with the sRGB curve forced when the source profile is not sRGB (MagicTransforms.AddInternalFormatConverter); chroma is resampled gamma-encoded and only luma is sharpened.
- Gamma lookup tables are 256 entries (to linear) and 1024 entries (from linear, interpolated), which issue #183 says is too coarse for float or 16-bit HDR pipelines.
- The 1.0 version has not shipped: the latest NuGet release is 0.15.0 (Dec 2024), and the README says APIs are not yet stable.

## Known shortcomings

- C# library (language-filter mismatch). README timings (7.4x/5.2x/9.0x vs ImageMagick, derived) come from the author's locally modified copy of bleroy/core-imaging-playground; the measured work differs: MagicScaler uses hybrid decoder pre-shrink, linear-light processing with sharpening and the libjpeg-turbo codec, while ImageMagick decodes the full image in gamma space. NetVips's margin is larger on Linux.
- The work done differs from the baseline: hybrid mode decodes at half scale through libjpeg-turbo's scale_denom and then applies Catmull-Rom (SettingUtil), while Magick.NET does a full decode plus its default Lanczos (resize.c), roughly 17 against 51 taps per axis (derived from code). The 'Linux x64' table ran in WSL2 (a VM), not bare metal. Planar mode linearises only luma (sRGB curve forced) and sharpens only luma; no hand-written intrinsics on ARM64 (Sse2 gate); issue #180 reports 360 ms against GDI+'s 130 ms on small images; last NuGet release 0.15.0 (December 2024).

## Caveats and trade-offs

First-party run of a locally modified copy of the public core-imaging-playground suite; results date from Nov 2022 package versions (MagicScaler 0.13.2). End-to-end JPEG decode, resize and encode with file I/O, not pure resampling, and the JPEG codec under MagicScaler is native libjpeg-turbo (C) via PhotoSauce.NativeCodecs.Libjpeg. Different work from the ImageMagick baseline: MagicScaler's default HybridMode (FavorQuality) may use the decoder or a lower-quality scaler to shrink to an intermediate size first (ratio 2 for about 1 MP to 150 px, derived from ProcessImageSettings.HybridScaleRatio), then resamples in linear light with sharpening; the Magick.NET path decodes the full image (no size hint), resizes in gamma-encoded space with ImageMagick's default filter on a Q8 build with OpenCL disabled. NetVips' Thumbnail also shrinks on load. MagicScaler's margin over ImageMagick is smaller on Linux x64 (5.2x) than on Windows x64 (7.4x), while its margin over NetVips is larger on Linux (3.8x) than on Windows (2.2x) (both derived from page data). Language filter mismatch: C#/.NET, not callable from C++. ImageMagick (on the category list) is present; stb_image_resize is not.

.NET only; the pipeline combines JPEG DCT-domain scaling with high-quality resampling, so part of the speed comes from decode-time scaling. Windows and Linux supported; some libraries are not supported on all platforms.

## Maintenance

Active: dependency and native-codec updates landed in Sep-Oct 2026 after a gap since Apr 2025, but the last NuGet release is 0.15.0 (Dec 2024); MIT licensed, so the code can be copied, but it is C# and of no direct use to C++ code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** All quoted timings are in readme.md (BenchmarkDotNet ShortRun tables, Xeon W-11855M and Snapdragon, .NET 6.0.10). The harness is the public third-party bleroy/core-imaging-playground (NetCore/LoadResizeSave.cs), but the MagicScaler author ran it, locally modified (constant UnrollFactor, WarmupCount=3 against upstream's 5) and with Nov 2022 package versions, while upstream master now targets net10.0, MagicScaler 0.15.0 and Magick.NET 14.15.0; the native libraries are prebuilt NuGet binaries with unstated flags. First-party run, so C.
- **Verifier notes:** All numbers verified in readme.md. Fixed a wrong caveat: the NetVips margin is larger on Linux x64, not smaller. The decoder-assisted hybrid scaling makes the thumbnail comparison favour MagicScaler on work done, not only on code speed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/readme.md>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/Core/ProcessImageSettings.cs>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/Core/Enums.cs>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/Docs/Remarks.xml>
  - <https://github.com/saucecontrol/PhotoSauce>
  - <https://github.com/saucecontrol/PhotoSauce/commits/master>
  - <https://github.com/bleroy/core-imaging-playground>
  - <https://github.com/bleroy/core-imaging-playground/tree/master/NetCore>
  - <https://raw.githubusercontent.com/bleroy/core-imaging-playground/master/NetCore/LoadResizeSave.cs>
  - <https://raw.githubusercontent.com/bleroy/core-imaging-playground/master/NetCore/NetCore.csproj>
  - <https://raw.githubusercontent.com/bleroy/core-imaging-playground/master/NetCore/Program.cs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/readme.md>
  - <https://raw.githubusercontent.com/bleroy/core-imaging-playground/master/NetCore/LoadResizeSave.cs>
  - <https://github.com/saucecontrol/PhotoSauce/tree/master/src/MagicScaler/Magic>
  - <https://github.com/saucecontrol/PhotoSauce/tree/master/src>
  - <https://github.com/saucecontrol/PhotoSauce/tree/master/src/MagicScaler/Utilities>
  - <https://github.com/saucecontrol/PhotoSauce/tree/master/src/NativeCodecs/Libjpeg>
  - <https://github.com/saucecontrol/PhotoSauce/tree/master/build/vcpkg/ports/psjpeg>
  - <https://github.com/saucecontrol/PhotoSauce/commits/master>
  - <https://github.com/saucecontrol/PhotoSauce/issues?q=is%3Aissue+performance>
  - <https://github.com/saucecontrol/PhotoSauce/issues/180>
  - <https://github.com/saucecontrol/PhotoSauce/issues/183>
  - <https://github.com/saucecontrol/PhotoSauce/issues/45>
  - <https://github.com/saucecontrol/PhotoSauce/issues/27>
  - <https://github.com/saucecontrol/PhotoSauce/issues/82>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/Magic/ConvolutionTransform.cs>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/Magic/HybridScaleTransform.cs>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/Magic/MagicTransforms.cs>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/Magic/MagicImageProcessor.cs>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/Core/ProcessImageSettings.cs>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/Core/PipelineContext.cs>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/Utilities/SettingUtil.cs>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/Utilities/HWIntrinsics.cs>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/MagicScaler.csproj>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/Directory.Build.props>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/MagicScaler/Docs/Remarks.xml>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/NativeCodecs/Libjpeg/JpegDecoder.cs>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/src/NativeCodecs/Libjpeg/readme.md>
  - <https://raw.githubusercontent.com/saucecontrol/PhotoSauce/HEAD/build/vcpkg/ports/psjpeg/portfile.cmake>
  - <https://api.nuget.org/v3-flatcontainer/photosauce.magicscaler/index.json>
  - <https://raw.githubusercontent.com/ImageMagick/ImageMagick/main/MagickCore/resize.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/saucecontrol/photosauce`) · [data/wave10/enrich/raw/github_com_saucecontrol_photosauce.json](../../../data/wave10/enrich/raw/github_com_saucecontrol_photosauce.json) (enrichment confidence 0.8)

</details>
