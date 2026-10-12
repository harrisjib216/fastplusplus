# ImageSharp (SixLabors)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C#` · `Six Labors Split License 1.0 (not an SPDX id, non-OSI): Apache-2.0 for open-source or source-available use, transitive dependency use, for-profit under 1M USD annual gross revenue and non-profits; paid Six Labors Commercial License otherwise` · 🟢 active

> Fully managed C# image library; 4.4x faster than Magick.NET and 3.2x faster than System.Drawing on a load-resize-sharpen-save JPEG pipeline.

| | |
|---|---|
| **Beats** | Magick.NET (ImageMagick) and System.Drawing |
| **Claimed result** | Rows quoted from the NetVips benchmark page, ratios derived from page data: JPEG ImageSharp 366.95 ms vs Magick.NET 1,626.85 ms (about 4.4x faster, derived from page data), vs System.Drawing 1,185.58 ms (about 3.2x, derived from page data), vs SkiaSharp 5,362.23 ms (about 14.6x, derived from page data). TIFF ImageSharp 186.51 ms vs Magick.NET 1,533.49 ms (about 8.2x, derived from page data), vs System.Drawing 985.05 ms (about 5.3x, derived from page data). On the same page NetVips is faster than ImageSharp (ratio 4.93 on JPEG, 3.75 on TIFF). |
| **Workload** | Load a large JPEG or TIFF, shrink by 10 percent, sharpen, and save (libvips benchmark scenario), as run by the NetVips benchmark project with BenchmarkDotNet under NativeAOT. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7900 3.70GHz, 12 physical / 24 logical cores, Windows 11 25H2 |
| **Compiler and flags** | BenchmarkDotNet v0.15.8, .NET SDK 10.0.101, .NET 10.0.1 NativeAOT, X64 RyuJIT x86-64-v4, 'dotnet run -c Release'; ImageSharp 3.1.12, Magick.NET 14.10.1, System.Drawing.Common 10.0.1 |
| **Adoption** | 8.0k stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/SixLabors/ImageSharp) · [benchmark](https://github.com/kleisauke/net-vips/tree/master/tests/NetVips.Benchmarks) |

## Verdict

Third-party BenchmarkDotNet suite by the NetVips author (.NET 10.0.1 NativeAOT, x86-64-v4, AMD Ryzen 9 7900 with 24 threads, Windows 11): load a 5000x5000 JPEG or tiled TIFF, crop 100 px, shrink to 90% with a Triangle filter, 3x3 sharpen, save at quality 75. ImageSharp 3.1.12 took 366.95 ms against Magick.NET-Q8-AnyCPU 14.10.1 at 1,626.85 ms (about 4.4x, derived from page data) and System.Drawing at 1,185.58 ms (about 3.2x, no sharpen); on TIFF 186.51 ms against 1,533.49 ms (8.2x) and 985.05 ms (5.3x). Magick.NET ran single-threaded (non-OpenMP package) while ImageSharp's sharpen step used up to 24 threads.

## Use it when

- A .NET service or app that needs in-process decode, resize and encode with no native dependency (containers, ARM64, trimmed builds; the benchmark itself ran under NativeAOT) and currently uses Magick.NET or System.Drawing: 4.4x faster than Magick.NET-Q8-AnyCPU on the JPEG pipeline and 8.2x on TIFF in the NetVips table.
- Replacing System.Drawing for thumbnail-style work: 3.2x faster on JPEG and 5.3x on TIFF even though the System.Drawing path skipped the sharpen step.
- Your use qualifies for the Apache-2.0 side of the Six Labors Split License: transitive dependency, open-source or source-available use, a for-profit under 1M USD annual gross revenue, or a non-profit.
- Pipelines dominated by convolution-type filters on large images, which ImageSharp spreads over every core by default.

## Skip it when

- You want the fastest option in .NET: NetVips (libvips) is 4.93x faster on JPEG and 3.75x on TIFF in the same table, and NetVips (806.8 ms) and MagicScaler (888.0 ms) beat ImageSharp (1,098.4 ms) in Six Labors' own LoadResizeSave stress benchmark.
- A for-profit direct dependency above 1M USD revenue without a paid Six Labors Commercial License; version 4 enforces a build-time licence key (a third-party issue seen as a search snippet says it is an error in Release builds), and the net-vips project pins 3.1.12 for that reason.
- Staying on 3.1.12 to avoid the key while decoding untrusted files: GHSA-jj3q-cwqj-842r (heap out-of-bounds write in TIFF CCITT T4/Modified Huffman decompression, CVSS 7.5) affects &gt;= 3.0.0 and is patched only in 4.1.1, and eight more advisories followed in August-September 2026 (TIFF, ICC, EXR, HistogramEqualization).
- One very large resize where you expect all cores to help: the resampling pass runs as a single worker (the source comments that parallelism would need multiple workers), so parallelise across images instead.
- JPEG decode-bound workloads where Huffman decoding dominates: issue #1607 'JpegDecoder: Optimize HuffmanScanDecoder' has been open since 2021.

## How it is fast

Hot codec paths use .NET hardware intrinsics picked at run time: the JPEG float DCT has an AVX Vector256 path (FloatingPointDCT.Intrinsic.cs) and colour conversion has AVX, Arm and Vector&lt;T&gt; converters (JpegColorConverterBase). Resize is a separable two-pass filter with precomputed ResizeKernelMap weights run by a sliding-window ResizeWorker over a transposed Vector4 first-pass buffer sized to Configuration.WorkingBufferSizeHintInBytes, which keeps the working set in cache; in 3.1.12 and on main it is one sequential worker per image. Convolution-type processors are row-parallel through ParallelRowIterator with MaxDegreeOfParallelism defaulting to Environment.ProcessorCount. Much of the gap to Magick.NET also reflects the baseline: the Magick.NET-Q8-AnyCPU package is built without OpenMP, so ImageMagick runs every step on one thread.

## Compared with alternatives

Among .NET options, pick ImageSharp over NetVips/libvips or MagicScaler when a fully managed library with no native binaries matters more than raw speed, since both are faster in the same benchmarks; against Magick.NET and System.Drawing it is the faster managed choice, provided the Six Labors licence terms fit.

## Integration

| | |
|---|---|
| **Form** | NuGet package (managed assembly SixLabors.ImageSharp) |
| **Dependencies** | none (fully managed, no native libraries) |
| **Minimum toolchain** | 3.1.x targets net6.0 (.NET 6+); 4.x releases moved to .NET 8 (v4.0.0 release notes); the main-branch csproj now targets net10.0 |
| **Platforms** | any platform .NET runs on; SIMD paths for x86 AVX/AVX2 and Arm intrinsics with a Vector&lt;T&gt; fallback chosen at run time; marked IsTrimmable |
| **Thread safety** | not documented in the files read; processors parallelise internally up to Configuration.MaxDegreeOfParallelism (default Environment.ProcessorCount) |
| **Drop-in for the baseline** | false: its own Image/Mutate/Save API, not source compatible with Magick.NET or System.Drawing |

## Gotchas

- MaxDegreeOfParallelism defaults to the processor count; a server that already processes many images concurrently should lower it (Six Labors' own Resize benchmark sets it to 1) to avoid oversubscription.
- In 3.1.12 the general 2D ConvolutionProcessor&lt;TPixel&gt; is internal; the NetVips benchmark reaches it through reflection (Type.GetType plus MakeGenericType), which is fragile under trimming, NativeAOT and version upgrades.
- Convolution kernels are applied exactly as given, with no divisor parameter: the benchmark's sharpen kernel sums to 8, so ImageSharp's output is brighter and clipped compared with libvips and ImageMagick, which divide by 8.
- Processors work on rows converted to Vector4 floats (ToVector4 and FromVector4Destructive per row), so 8-bit pipelines pay a conversion each step; chaining many cheap operations costs more than the per-operation numbers suggest.

## Known shortcomings

- Six Labors Split License 1.0 (not OSI approved), so reference only. In the NetVips Benchmark.cs run (Triangle filter and quality 75 on both sides, Magick.NET-Q8, OpenCL off, .NET 10.0.1 NativeAOT, Ryzen 9 7900, library-default thread counts) NetVips beats ImageSharp in the same table; ImageSharp's own LoadResizeSave bench against Magick.NET is different work (decode-to-target-size versus Q16 full decode).
- Threading asymmetry: Magick.NET-Q8-AnyCPU is built without OpenMP (docs/Readme.md), so the ImageMagick side is single-threaded, while ImageSharp's convolution runs ParallelRowIterator on 24 threads (resize's single ResizeWorker and the JPEG code are single-threaded). 3.1.12 is affected by GHSA-jj3q-cwqj-842r (3.0.0 and later, fixed only in 4.1.1); v4 needs a build-time licence key per a search snippet; the internal ConvolutionProcessor is reached via reflection.

## Caveats and trade-offs

Workload is the libvips load, crop 100 px, shrink to 90 percent, 3x3 sharpen, save pipeline, so decode and encode dominate along with resampling. Settings checked in Benchmark.cs: Magick.NET-Q8-AnyCPU with OpenCL disabled, FilterType Triangle and Quality 75; ImageSharp KnownResamplers.Triangle and default quality 75; neither ImageSharp nor Magick.NET is pinned to a thread count (library defaults on a 24-thread CPU), while NetVips is set to concurrency 4. ImageSharp's convolution kernel is passed without the 1/8 scale the other libraries apply (NetVips scale 8, Magick convolve:scale 0.125, Skia gain 0.125), so its output image differs although the 3x3 cost is the same. System.Drawing skips the sharpen step and uses GDI+ bilinear. The benchmark is by the NetVips author and NetVips beats ImageSharp in the same table (ratio 4.93 on JPEG, 3.75 on TIFF). SixLabors' own LoadResizeSave stress benchmark (tests/ImageSharp.Benchmarks/LoadResizeSave, 2022 comment results, Intel Core i7-6700K, .NET 6.0.5, one thread) shows ImageSharp 1,098.4 ms vs Magick 4,089.8 ms and System.Drawing 3,624.2 ms, but there ImageSharp decodes the JPEG straight to the 150 px target size while Magick.NET-Q16 decodes full size and resizes with its default filter (different work), and NetVips (806.8 ms) and MagicScaler (888.0 ms) beat ImageSharp. The repo's Resize benchmark (tests/ImageSharp.Benchmarks/Processing/Resize.cs) carries 2019 results only against System.Drawing: ImageSharp with MaxDegreeOfParallelism = 1 took 75.32 ms vs 120.11 ms (ratio 0.63) on .NET Framework 4.7.2 and 88.56 ms vs 120.33 ms (0.74) on .NET Core 2.1, bicubic 3032 to 400 px, Intel Core i7-7700HQ. The README itself carries no performance numbers. ImageSharp 3+ is not OSI-licensed and version 4 needs a build-time license key (net-vips footnote).

Fully managed .NET code, no native dependency. License is the Six Labors Split License 1.0, which is not OSI-approved (commercial license required for some uses; the NetVips page notes version 4 needs a build-time license key), so the code is source-available but should be treated as not copyable.

## Maintenance

Actively maintained (v4.1.2 released 2026-09-14, 8.0k stars, 14,518 commits); usability stays reference because of the non-OSI Six Labors Split License and v4's build-time key, and the benchmarked 3.1.12 is the latest 3.x release on the releases page, so it does not carry the fix for GHSA-jj3q-cwqj-842r (patched only in 4.1.1).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Third-party BenchmarkDotNet suite (kleisauke/net-vips tests/NetVips.Benchmarks/Benchmark.cs, README.md) with public code, .NET SDK 10.0.101 NativeAOT Release, x86-64-v4 RyuJIT, AMD Ryzen 9 7900, ImageSharp 3.1.12 vs Magick.NET-Q8-AnyCPU 14.10.1; both sides use the Triangle filter, JPEG quality 75 and the same crop-resize-convolve pipeline, so the Magick.NET comparison is like-for-like. All rows in the record match the README table.
- **Verifier notes:** Confirmed A: NetVips benchmark matches filter (Triangle), quality (75) and pipeline across ImageSharp and Magick.NET Q8; only threading is left at library defaults. Usability stays reference (Six Labors Split License, non-OSI). The image-codecs search's System.Drawing evidence lives in the same tests/ImageSharp.Benchmarks project and is first-party.
- **Fields the verifier corrected:** `license`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kleisauke/net-vips/HEAD/tests/NetVips.Benchmarks/README.md>
  - <https://raw.githubusercontent.com/kleisauke/net-vips/HEAD/tests/NetVips.Benchmarks/Benchmark.cs>
  - <https://raw.githubusercontent.com/kleisauke/net-vips/HEAD/tests/NetVips.Benchmarks/NetVips.Benchmarks.csproj>
  - <https://raw.githubusercontent.com/kleisauke/net-vips/HEAD/tests/NetVips.Benchmarks/Config.cs>
  - <https://raw.githubusercontent.com/kleisauke/net-vips/HEAD/tests/NetVips.Benchmarks/TestImage.cs>
  - <https://github.com/kleisauke/net-vips/tree/master/tests/NetVips.Benchmarks>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/HEAD/tests/ImageSharp.Benchmarks/Processing/Resize.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/HEAD/tests/ImageSharp.Benchmarks/LoadResizeSave/LoadResizeSaveStressBenchmarks.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/HEAD/tests/ImageSharp.Benchmarks/LoadResizeSave/LoadResizeSaveStressRunner.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/HEAD/tests/ImageSharp.Benchmarks/LoadResizeSave/README.md>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/HEAD/tests/ImageSharp.Benchmarks/ImageSharp.Benchmarks.csproj>
  - <https://github.com/SixLabors/ImageSharp/tree/main/tests/ImageSharp.Benchmarks/LoadResizeSave>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/HEAD/LICENSE>
  - <https://github.com/SixLabors/ImageSharp>
  - <https://github.com/SixLabors/ImageSharp/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kleisauke/net-vips/HEAD/tests/NetVips.Benchmarks/README.md>
  - <https://raw.githubusercontent.com/kleisauke/net-vips/HEAD/tests/NetVips.Benchmarks/Benchmark.cs>
  - <https://raw.githubusercontent.com/kleisauke/net-vips/HEAD/tests/NetVips.Benchmarks/NetVips.Benchmarks.csproj>
  - <https://raw.githubusercontent.com/kleisauke/net-vips/HEAD/tests/NetVips.Benchmarks/Config.cs>
  - <https://raw.githubusercontent.com/kleisauke/net-vips/HEAD/tests/NetVips.Benchmarks/TestImage.cs>
  - <https://raw.githubusercontent.com/kleisauke/net-vips/HEAD/tests/NetVips.Benchmarks/Runner.cs>
  - <https://raw.githubusercontent.com/kleisauke/net-vips/HEAD/tests/NetVips.Benchmarks/ImageSharp/ConvolutionProcessor.cs>
  - <https://github.com/kleisauke/net-vips/tree/master/tests/NetVips.Benchmarks>
  - <https://github.com/kleisauke/net-vips/tree/master/tests/NetVips.Benchmarks/ImageSharp>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/README.md>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/LICENSE>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/src/ImageSharp/ImageSharp.csproj>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/src/ImageSharp/Configuration.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/src/ImageSharp/Processing/Processors/Transforms/Resize/ResizeProcessor%7BTPixel%7D.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/src/ImageSharp/Processing/Processors/Transforms/Resize/ResizeWorker.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/src/ImageSharp/Processing/Processors/Convolution/ConvolutionProcessor%7BTPixel%7D.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/src/ImageSharp/Processing/Processors/Convolution/Convolution2DProcessor%7BTPixel%7D.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/src/ImageSharp/Formats/Jpeg/Components/Decoder/SpectralConverter%7BTPixel%7D.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/src/ImageSharp/Formats/Jpeg/Components/Encoder/SpectralConverter%7BTPixel%7D.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/src/ImageSharp/Formats/Jpeg/Components/FloatingPointDCT.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/src/ImageSharp/Formats/Jpeg/Components/FloatingPointDCT.Intrinsic.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/v3.1.12/src/ImageSharp/Formats/Jpeg/Components/ColorConverters/JpegColorConverterBase.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/main/README.md>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/main/src/ImageSharp/ImageSharp.csproj>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp/main/src/ImageSharp/Processing/Processors/Transforms/Resize/ResizeProcessor%7BTPixel%7D.cs>
  - <https://github.com/SixLabors/ImageSharp>
  - <https://github.com/SixLabors/ImageSharp/releases>
  - <https://github.com/SixLabors/ImageSharp/issues?q=is%3Aissue+is%3Aopen+performance>
  - <https://github.com/SixLabors/ImageSharp/security/advisories>
  - <https://github.com/SixLabors/ImageSharp/security/advisories/GHSA-jj3q-cwqj-842r>
  - <https://github.com/dlemstra/Magick.NET>
  - <https://raw.githubusercontent.com/dlemstra/Magick.NET/main/Readme.md>
  - <https://raw.githubusercontent.com/dlemstra/Magick.NET/main/docs/Readme.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/sixlabors/imagesharp`) · [data/wave10/enrich/raw/github_com_sixlabors_imagesharp.json](../../../data/wave10/enrich/raw/github_com_sixlabors_imagesharp.json) (enrichment confidence 0.75)

</details>
