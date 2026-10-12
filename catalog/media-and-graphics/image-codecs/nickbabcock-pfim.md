# Pfim

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟢 active

> Managed .NET decoder for Targa and DDS (BC1-BC7) images; beats FreeImage, DevIL and Magick.NET called from C#.

| | |
|---|---|
| **Beats** | FreeImage (via FreeImage-dotnet-core 4.3.6 with a bundled FreeImage.dll), DevIL (via DevILSharp 0.2.4) and ImageMagick (via Magick.NET-Q16-AnyCPU 7.12.0), all native C/C++ libraries driven from .NET, plus managed Targa decoders TargaImage 1.0, ImageFormats 1.0, StbSharp 0.7.2.38 and TgaSharpLib 1.0 |
| **Claimed result** | README: 'Pfim is hands down the fastest targa decoder. More than 10x faster than the closest competitor'; for DDS 'one of the fastest if not the fastest', first everywhere except DXT5 where it is 1% slower. From TargaBenchmark-report.csv (Mean column, unit not printed, BenchmarkDotNet default is ns): 24bit-rle.tga Pfim 5,083.1 vs FreeImage 65,756.5 vs DevILSharp 47,792.0 (about 12.9x and 9.4x, derived from page data); 32bit.tga Pfim 3,655.9 vs DevILSharp 52,740.6 (about 14.4x, derived from page data). DdsBenchmark-report.csv: 32bit.dds Pfim 1,569.2 vs DevILSharp 115,072.4; dxt1.dds Pfim 46,734.1 vs FreeImage 75,354.5; dxt5.dds Pfim 93,732.4 vs FreeImage 92,683.4 (Pfim slightly slower). |
| **Workload** | Decoding one 120x120 image from an in-memory byte[] in 3 Targa variants (24-bit RLE, 32-bit RLE, 32-bit raw) and 4 DDS variants (32-bit, DXT1, DXT3, DXT5), measured with BenchmarkDotNet as mean time per decode; Pfim decodes with a pooled ArrayPool allocator (PfimAllocator) that reuses the output buffer, the other libraries allocate a fresh image per call. |
| **Metric** | throughput |
| **Compiler and flags** | BenchmarkDotNet 0.11.5, net461 target (.NET Framework 4.6.1; CSV shows Runtime=Clr, Jit=RyuJit, Platform=X64), PlatformTarget AnyCPU, Release build (benchmark project as of commit 6bdf779, April 2019); CSV times are nanoseconds (BaseConfig exports TimeUnit.Nanosecond, analysis.R converts ns to microseconds). The current csproj (net8.0, BenchmarkDotNet 0.15.6, Magick.NET 14.9.1, DevILSharp 0.2.20, FreeImage.Standard 4.3.8) has not been re-run. |
| **Adoption** | 133 stars |
| **Last commit** | 2026-07-15 |
| **Links** | [repository](https://github.com/nickbabcock/Pfim) · [benchmark](https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/analysis/TargaBenchmark-report.csv) |

## Verdict

BenchmarkDotNet 0.11.5 on .NET Framework 4.6.1 (Clr, RyuJit, x64, CPU not recorded), April 2019 (commit 6bdf779): decoding one 120x120 image from an in-memory byte[], Pfim with a pooled allocator took 5.1 us for 24-bit RLE TGA versus 65.8 us for FreeImage and 47.8 us for DevILSharp (12.9x and 9.4x), and 1.6 us versus 115 us for DevILSharp on uncompressed 32-bit DDS, but only 1.61x faster than FreeImage on DXT1, 1.16x on DXT3 and 1.1% slower on DXT5. The test image has only 4 distinct colors, so each RLE file is 240 run packets (two 60-pixel runs per row) and no raw packets, Pfim's best case, and the uncompressed paths are a single Buffer.BlockCopy (row-flipped for TGA) of 57,600 bytes, while the competitors pay .NET interop costs and convert to their own pixel formats.

## Use it when

- C# or Unity/MonoGame/Xamarin code that must read .tga or .dds assets without shipping native FreeImage, DevIL or ImageMagick binaries.
- Bulk loading of many small game textures or sprites, where per-call fixed cost and GC pressure dominate and a pooled IImageAllocator can be reused across decodes.
- Tools that need DDS metadata or the still-compressed BC payload (PfimConfig decompress: false) to upload to the GPU directly.
- Pipelines that want raw BGR(A) bytes with a 4-byte-aligned stride for GDI+, WPF or SkiaSharp interop.

## Skip it when

- Anything beyond TGA and DDS: no PNG, JPEG, WebP, KTX or encoding (DDS encoding is only an open PR, #131).
- Untrusted TGA input: the RLE fast path writes runs and reads input through raw pointers with no bounds checks (see gotchas).
- Volume (3D) DDS textures, which decode only the first slice (open issue #110), or the DDS files reported unreadable in open issue #107.
- Top-right or bottom-right oriented TGA files, which are decoded as bottom-left without the horizontal flip (release notes 0.6.0, open issue #38).
- Choosing a texture decoder on speed from the published numbers: they come from a 2019 run on one 120x120, four-color image and pre-fix DXT code.

## How it is fast

For RLE Targa read from a byte[] or publicly visible MemoryStream, an unsafe pointer loop (CompressedTarga.FastPass) expands run packets with 32-bit stores (Util.memset) and a three-int rotation trick for 24-bit pixels (RunLength3), and copies raw packets with Buffer.MemoryCopy; uncompressed Targa is a row-by-row Buffer.BlockCopy that only flips row order. DDS blocks are decoded one 4x4 block at a time with plain scalar C# (no SIMD; since 0.11.0 the color interpolation uses float lerp). Output buffers can come from a caller-supplied IImageAllocator (for example ArrayPool), which the benchmarks use. Much of the measured gap is the competitors' cost of going through .NET interop wrappers and converting to their own pixel formats, not a faster block-decode algorithm.

## Compared with alternatives

No catalogued sibling decodes TGA or DDS in managed .NET: bc7enc, bc7e, icbc, Goofy and etcpak are C/C++ texture encoders, and the rest are PNG/JPEG/QOI codecs. Pick Pfim to read BC-compressed DDS or TGA from C# without native code; use those siblings to produce BC/ETC textures, and a C/C++ BCn decoder when you can ship native code.

## Integration

| | |
|---|---|
| **Form** | NuGet package (managed assembly, strong-named) |
| **Dependencies** | none (Pfim.csproj has no package references) |
| **Minimum toolchain** | .NET Standard 2.0 (.NET Framework 4.6.1+, .NET Core 2.0+ or Mono/Unity with netstandard2.0); unsafe code is compiled into the package |
| **Platforms** | any .NET runtime with netstandard2.0 support (Windows, Linux, macOS, mobile through Xamarin) |
| **Thread safety** | not documented; the Targa decoders are stateless static singletons in current code, and a shared IImageAllocator must itself be thread-safe (ArrayPool.Shared is) |
| **Drop-in for the baseline** | no |

## Gotchas

- Use DataLen, not Data.Length: pooled buffers can be larger than the image and DDS mipmaps share the buffer; Dispose the image to return buffers to a custom allocator.
- Despite the Rgb24/Rgba32 names, bytes are in B,G,R(,A) order as stored in TGA (the README maps Rgba32 to GDI+ Format32bppArgb); there is no channel swap pass.
- Possible memory-safety bug from reading the code: CompressedTarga.FastPass and RunLength write each RLE run with pointer stores without checking the row or buffer end, and FastPass reads the input pointer without checking the input length, so a crafted or truncated RLE TGA (or one whose runs cross scanlines, which TGA 2.0 forbids) can write past the output array or read past the input array.
- DXT1 output changed from 24-bit RGB to 32-bit RGBA in 0.10.0, and DXT1/3/5 interpolation changed to float lerp in 0.11.0 to fix systematic rounding errors (issue #88, PR #98); code written against older versions sees different formats and pixel values.

## Known shortcomings

- Numbers come from a 2019-04-20 run (net461, BenchmarkDotNet 0.11.5, Pfim 0.7.0, DevILSharp 0.2.4) with no CPU model; the README relabelled the library versions in 2022 without rerunning. Only Pfim gets a pooled ArrayPool allocator (release notes credit pooling with up to 3x), the FreeImage result is never disposed, and Magick.NET is the Q16 build; the '10x' headline fails on 24bit-rle (9.4x).
- The bench image has 4 distinct colours: 24bit-rle.tga and 32bit-rle.tga are each 240 run packets (two 60-pixel runs per row) with zero raw packets, Pfim's best case, and the uncompressed paths are a single Buffer.BlockCopy of 57,600 bytes. The 2019 DXT numbers ran pre-fix decoders: DXT1 wrote 24-bit RGB (32-bit RGBA only since 0.10.0) while the competitors wrote 32-bit, and the integer interpolation had systematic rounding errors (issue #88, PR #98, fixed in 0.11.0). Security by code reading (no issue filed): CompressedTarga.FastPass and RunLength write RLE runs through unchecked pointers and FastPass reads input without a length check, so a malformed or truncated TGA can overflow the heap.

## Caveats and trade-offs

One 120x120 test image per format, so per-call fixed costs dominate. No CPU model anywhere in the repo. The CSVs were committed on 2019-04-20 (Pfim 0.7.0 era, .NET Framework 4.6.1, DevILSharp 0.2.4); a 2022 README edit relabelled the contestants as Pfim 0.10.0 and DevIL 0.2.19 without new data, so the README version list does not describe the measured run. Unequal work: the Pfim benchmark passes a pooled ArrayPool allocator, so its output buffer is reused (312 B allocated per Targa decode versus 5,361 B for FreeImage and 343,195 B for TargaImage in the CSV), and Pfim's own 0.7.0 release notes say naive pooling gives up to a 3x speedup in these benchmarks; the FreeImage benchmark returns the FreeImageBitmap without disposing it (native memory reclaimed by finalizers, Gen 2 collections in its row); ImageMagick runs the Q16 build (16-bit-per-channel pixel cache) and native libraries are reached through .NET interop wrappers whose marshalling cost is included. README claim 'more than 10x faster than the closest competitor' does not hold for 24bit-rle.tga against DevILSharp (9.4x, derived from page data); for DDS Pfim leads FreeImage by 1.61x on DXT1 and 1.16x on DXT3 and is 1.1% slower on DXT5 (derived from page data). Baselines are not libjpeg-turbo/libpng/libwebp/libavif, so the result says little about mainstream codecs.

.NET library that decodes only Targa (TGA) and DirectDraw Surface (DDS) files; no PNG/JPEG/WebP. Returns raw pixel data with optional pooled allocator, so display needs extra glue (System.Drawing, ImageSharp, WPF samples in the README).

## Maintenance

Active (last commit 2026-07-15, release 0.11.4 on 2025-11-29, benchmark project moved to net8.0 but not re-run), MIT-licensed and on NuGet; copyable, but the published speed numbers predate the DXT correctness fixes and should be re-measured before relying on them.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party BenchmarkDotNet code is public (src/Pfim.Benchmarks/TargaBenchmark.cs, DdsBenchmark.cs, BaseConfig.cs) and every number in the record matches analysis/TargaBenchmark-report.csv and DdsBenchmark-report.csv (Mean, ns), but no CPU model is recorded anywhere and the CSVs come from an April 2019 run that has not been repeated, so C.
- **Verifier notes:** Numbers verified against both CSVs. The measured Pfim path uses a pooled allocator that the competitors do not get, and the CSV predates the README's stated versions by about three years; kept at C with those shortcomings.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/nickbabcock/Pfim>
  - <https://github.com/nickbabcock/Pfim/commits/master>
  - <https://github.com/nickbabcock/Pfim/commits/master/analysis>
  - <https://github.com/nickbabcock/Pfim/commits/master/README.md>
  - <https://github.com/nickbabcock/Pfim/tree/master/analysis>
  - <https://github.com/nickbabcock/Pfim/tree/master/src/Pfim.Benchmarks>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/README.md>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/analysis/TargaBenchmark-report.csv>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/analysis/DdsBenchmark-report.csv>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/analysis/analysis.R>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim.Benchmarks/TargaBenchmark.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim.Benchmarks/DdsBenchmark.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim.Benchmarks/BaseConfig.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim.Benchmarks/Program.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim.Benchmarks/Pfim.Benchmarks.csproj>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/tests/Pfim.Tests/PfimAllocator.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/RELEASE_NOTES.md>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/6bdf779/README.md>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/6bdf779/src/Pfim.Benchmarks/Pfim.Benchmarks.csproj>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/6bdf779/src/Pfim.Benchmarks/TargaBenchmark.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/a2ca6af/README.md>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/8aa2900/README.md>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/c34aa1a/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/README.md>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/RELEASE_NOTES.md>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/analysis/TargaBenchmark-report.csv>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/analysis/DdsBenchmark-report.csv>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim.Benchmarks/TargaBenchmark.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim.Benchmarks/DdsBenchmark.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim.Benchmarks/BaseConfig.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim.Benchmarks/Pfim.Benchmarks.csproj>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/Pfim.csproj>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/Pfimage.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/IImage.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/IImageAllocator.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/PfimConfig.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/Util.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/DefaultAllocator.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/targa/Targa.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/targa/CompressedTarga.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/targa/UncompressedTarga.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/dds/Dds.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/dds/CompressedDds.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/dds/Dxt1Dds.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/dds/Dxt5Dds.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/src/Pfim/dds/UncompressedDds.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/tests/Pfim.Tests/PfimAllocator.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/tests/Pfim.Tests/data/bench/24bit-rle.tga>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/tests/Pfim.Tests/data/bench/32bit-rle.tga>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/tests/Pfim.Tests/data/bench/32bit.tga>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/tests/Pfim.Tests/data/bench/dxt1.dds>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/tests/Pfim.Tests/data/bench/dxt3.dds>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/tests/Pfim.Tests/data/bench/dxt5.dds>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/HEAD/tests/Pfim.Tests/data/bench/32bit.dds>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/6bdf779/src/Pfim/dds/Dxt1Dds.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/6bdf779/src/Pfim/dds/Dxt5Dds.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/6bdf779/src/Pfim/dds/CompressedDds.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/6bdf779/src/Pfim/targa/CompressedTarga.cs>
  - <https://raw.githubusercontent.com/nickbabcock/Pfim/6bdf779/src/Pfim.Benchmarks/DdsBenchmark.cs>
  - <https://github.com/nickbabcock/Pfim/tree/master/src/Pfim>
  - <https://github.com/nickbabcock/Pfim/tree/master/src/Pfim/dds>
  - <https://github.com/nickbabcock/Pfim/tree/master/src/Pfim/targa>
  - <https://github.com/nickbabcock/Pfim/issues?q=is%3Aissue>
  - <https://github.com/nickbabcock/Pfim/issues?q=is%3Aissue&page=2>
  - <https://github.com/nickbabcock/Pfim/issues/88>
  - <https://github.com/nickbabcock/Pfim/issues/104>
  - <https://github.com/nickbabcock/Pfim/commits/master>
  - <https://github.com/nickbabcock/Pfim/pulls?q=is%3Apr>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/nickbabcock/pfim`) · [data/wave10/enrich/raw/github_com_nickbabcock_pfim.json](../../../data/wave10/enrich/raw/github_com_nickbabcock_pfim.json) (enrichment confidence 0.75)

</details>
