# ImageSharp.Drawing

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C#` · `Six Labors Split License 1.0 (not an SPDX id): Apache-2.0 for open-source use, transitive dependency use, for-profit under 1M USD annual revenue and non-profits; paid Six Labors Commercial License otherwise` · 🟢 active

> Managed C# 2D vector drawing on ImageSharp with a band-parallel CPU rasterizer and an optional WebGPU backend; the vendor reports 2.4x faster than single-threaded SkiaSharp 2.88.

| | |
|---|---|
| **Beats** | Skia via SkiaSharp (BenchmarkDotNet Baseline=true), and System.Drawing (GDI+) |
| **Claimed result** | ImageSharp.Drawing 3.1.0 release post (as reported in search-result text): SkiaSharp 103.4 ms, System.Drawing 147.3 ms, ImageSharp.Drawing CPU 43.0 ms, CPU retained scene 11.9 ms, WebGPU 20.0 ms, WebGPU retained scene 5.6 ms. Ratios versus SkiaSharp (derived from page data): CPU 2.4x, CPU retained 8.7x, WebGPU 5.2x, WebGPU retained 18.5x. 3.0.0 post on .NET 8: SkiaSharp 103.165 ms versus CPU 48.544 ms (about 2.1x), retained CPU 17.879 ms (5.8x), WebGPU retained 5.476 ms (about 19x). |
| **Workload** | FillParis benchmark: render a 1096x1060 Paris street-map SVG (code comment says 30k paths; release post says 50K fill paths) fill-only with per-path transforms and opacity, using BenchmarkDotNet across SkiaSharp, System.Drawing, ImageSharp.Drawing CPU, CPU retained scene, WebGPU and WebGPU retained scene. The repo also has a FillTiger benchmark. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen AI Max+ 395, Windows 11 (3.1.0 post); 3.0.0 post says Windows x64 with .NET 8, CPU model not seen |
| **Compiler and flags** | .NET 10 (3.1.0 post) and .NET 8 (3.0.0 post) with BenchmarkDotNet, per the record; the benchmark project at main targets net10.0 (tests/ImageSharp.Drawing.Benchmarks/ImageSharp.Drawing.Benchmarks.csproj) with package versions set centrally (not seen); Release/JIT settings not seen |
| **Adoption** | 317 stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/SixLabors/ImageSharp.Drawing) · [benchmark](https://sixlabors.com/posts/announcing-imagesharp-drawing-310/) |

## Verdict

The numbers come from the vendor's 3.1.0 release post, known only from search snippets because sixlabors.com is blocked. FillParis is the repo's paris-30k.svg: 50,620 path elements counted in the 14.0 MB file, a 1096x1060 map, fill-only with opacity. It ran on an AMD Ryzen AI Max+ 395 with Radeon 8060S under Windows 11 and .NET 10, using BenchmarkDotNet with Server GC (0.15.8 is pinned at v3.1.0). Results: SkiaSharp 103.4 ms, System.Drawing 147.3 ms, ImageSharp CPU 43.0 ms (2.4x), CPU retained 11.9 ms (8.7x), WebGPU 20.0 ms (5.2x), WebGPU retained 5.6 ms (18.5x); ratios are derived from page data. The baseline is SkiaSharp 2.88.9 drawing single-threaded into a CPU raster SKSurface, while ImageSharp uses every hardware thread, reuses cached flattened curves even in the immediate row, and in the WebGPU rows runs on the integrated GPU with non-blocking submits. No pixel comparison is made: VerifyOutput only saves PNGs.

## Use it when

- .NET services or tools already using ImageSharp that render large fill-heavy vector scenes (maps, charts, SVG-like content) to bitmaps, where one render may use every core.
- Static or slowly changing scenes rendered many times (map tiles at a fixed zoom, dashboards): the retained-scene path took FillParis from 43.0 ms to 11.9 ms in the vendor's run.
- Managed-only deployments: the CPU backend needs no native library, unlike SkiaSharp, whose Linux use needs a separate native-assets package (the benchmark project adds SkiaSharp.NativeAssets.Linux.NoDependencies).
- .NET apps that want GPU drawing into WebGPU windows or offscreen targets with the same canvas code as the CPU path.
- Drawing shaped, bidirectional or complex-script text into images through SixLabors.Fonts.

## Skip it when

- C or C++ code: this is a .NET library. Blend2D, Skia or Blaze are the native options.
- Throughput per core, or many images rendered concurrently: the 2.4x CPU win sets every hardware thread against single-threaded SkiaSharp, and FillParis publishes no single-threaded ImageSharp row. FillTiger has an ImageSharp_SingleThreaded benchmark, but no published result was found.
- Judging against current Skia: the benchmarks pin SkiaSharp 2.88.9 (at the v3.0.0 and v3.1.0 tags and on main), an older line than the SkiaSharp 4.150.1 pinned by the sister Fonts repo.
- Untrusted SVG path data or geometry without limits: crashes on malformed SVG path input (#385, labelled security) and a StackOverflow in DefaultRasterizer.AddContainedLineF24Dot8 (#403) were fixed only in 2026.
- Companies with 1M USD or more annual revenue using it directly in closed-source software, unless they buy the Six Labors commercial license.

## How it is fast

The CPU backend is a flush executor, not a command-at-a-time painter. A batch of drawing commands becomes a retained, row-oriented plan (FlushScene), built in parallel over contiguous command partitions. Paths are flattened once per (path, scale) and cached on the IPath, with rotation and translation carried as a residual matrix. Execution runs a Parallel.For over 16-pixel row bands with worker-local scratch. Each band uses a Blaze-derived 24.8 fixed-point area/cover scan converter (DEFAULT_RASTERIZER.md credits aurimasg/blaze) with bit-vector sparse cell tracking and precomputed start-cover seeds for winding entering from the left. Retained scenes keep the band-local line data and row plan, so a replay skips geometry work entirely. The WebGPU backend is a Vello-derived staged compute pipeline: path-tag prefix scans, binning, tile allocation, coarse and fine passes, with GPU bump-allocated scratch that grows on retry.

## Compared with alternatives

Its CPU rasterizer is derived from Blaze and its GPU pipeline from Vello, so the reason to pick it is the platform: in .NET it gives you those designs plus a full 2D API (strokes, gradients, text, clipping, layers), which fill-only Blaze lacks. In C or C++, pick Blend2D (maintained, with its own multi-threaded context) or Blaze for fill throughput. In Rust, pick Vello CPU.

## Integration

| | |
|---|---|
| **Form** | NuGet packages: SixLabors.ImageSharp.Drawing (managed) plus optional SixLabors.ImageSharp.Drawing.WebGPU (managed with per-RID native WebGPU runtime under runtimes/) |
| **Dependencies** | SixLabors.ImageSharp (&gt;= 4.1.0 for 3.1.0, &gt;= 4.1.2 for 3.1.1+), SixLabors.Fonts (&gt;= 3.1.0), SixLabors.PolygonClipper (&gt;= 1.0.1); WebGPU package adds Silk.NET.Windowing.Glfw and Silk.NET.Windowing.Sdl 2.23.0 (1.0.0 also used Silk.NET.WebGPU.Native.WGPU) |
| **Minimum toolchain** | .NET 8 for the released 3.1.x packages (net8.0 asset); main was retargeted to net10.0/net11.0 (PR #416), and the README says the core package targets .NET 10 |
| **Platforms** | CPU backend: any .NET platform (managed code). WebGPU backend: a GPU with WebGPU compute support and a bundled native library for the runtime identifier; WebGPUEnvironment probes compute-pipeline support at run time |
| **Thread safety** | The rasterizer is static and keeps all mutable state in worker-owned scratch, and the CPU backend parallelizes internally. DrawingCanvas thread safety is not documented. DrawingTextCache became thread safe only with PR #420 (2026-09-14, after 3.1.0). |
| **Drop-in for the baseline** | no |

## Gotchas

- The CPU backend fans out across all cores by default (Parallel.For over row bands, with partitions capped at Environment.ProcessorCount). Cap it with Configuration.MaxDegreeOfParallelism, as FillTiger's single-threaded variant does, when rendering many images concurrently.
- Immediate mode is partly retained: Path and ComplexPolygon cache their flattened LinearGeometry per scale, so redrawing the same IPath objects skips curve subdivision. FillParis reuses one IPath list every iteration (its SVG has 79,353 relative cubic commands), while SkiaSharp rebuilds edges from each SKPath on every draw.
- WebGPU flushes do not wait for the GPU. Scratch-overflow status is read back later (up to 8 pending flushes before a blocking resolve), and offscreen overflows are repaired by a corrective re-render, so call ReadbackImage when you need finished pixels. Timings of WebGPU flushes measure pipelined submission, not per-frame latency.
- The released 3.1.x CPU rasterizer had small edge-accuracy errors, fixed on main by PR #417 (2026-09-11): band-boundary X drift of up to a few hundredths of a pixel on long slanted edges, coverage quantized to 1/256 before blending, and DDA walkers that floored rather than rounded.

## Known shortcomings

- C# (language-filter mismatch); Six Labors Split License (not OSI approved), reference only. Numbers (103.4/43.0/11.9 ms in 3.1.0; 5.476 ms WebGPU retained in 3.0.0) are snippets of the blocked vendor post; FillParis.cs runs single-threaded SkiaSharp SKSurface against ImageSharp's CPU Parallel.For over 16-pixel row bands on all cores, retained rows reuse set-up geometry, and the WebGPU row is GPU against Skia CPU. Hardware unconfirmed.
- Harness asymmetry: even the 'immediate' CPU row (43.0 ms) reuses the per-IPath flattening cache (Path and ComplexPolygon ToLinearGeometry cached per scale) while Skia rebuilds edges on every draw of the 50,620-path, 79,353-cubic SVG; the SkiaSharp baseline is 2.88.9 (old line; the Fonts repo pins 4.150.1); the WebGPU flush never waits for the GPU (up to 8 submits pending), so the WebGPU rows are pipelined submits rather than latency; VerifyOutput only saves PNGs with no pixel diff; FillParis has no single-thread row and FillTiger's ImageSharp_SingleThreaded result is unpublished. Hardware per a search snippet: Ryzen AI Max+ 395 with Radeon 8060S, Windows 11, .NET 10, Server GC.

## Caveats and trade-offs

Snippet only: sixlabors.com is blocked here, so the 3.0.0 and 3.1.0 release-post numbers come from WebSearch result text, not an opened page; this verifier's snippets confirmed SkiaSharp 103.4 ms, CPU 43.0 ms, CPU retained 11.9 ms (3.1.0, up from 48.5 ms and 17.9 ms in 3.0) and WebGPU retained 5.476 ms (3.0.0), but not the Ryzen AI Max+ 395 / Windows 11 machine. Vendor posts, so first-party. Not like-for-like: FillParis.cs draws into a single-threaded SkiaSharp CPU raster SKSurface, while ImageSharp.Drawing's CPU backend builds the scene in parallel partitions and executes 16-pixel row bands with Parallel.For on all cores (src/ImageSharp.Drawing/Processing/Backends/DEFAULT_DRAWING_BACKEND.md; the benchmark's Setup raises the thread-pool minimum to Environment.ProcessorCount), so the 2.4x CPU win is many threads against one and likely slower per core; the retained-scene rows reuse geometry flattened and binned once in GlobalSetup while SkiaSharp redraws every SKPath each iteration; the WebGPU rows are GPU against Skia's CPU raster path (whether canvas.Flush() waits for GPU completion was not checked). Antialiasing is on for Skia (IsAntialias=true) and per-path transforms are pre-applied for every backend in SvgBenchmarkHelper, so the drawn work otherwise matches. The path-count wording differs between the code comment (30k) and the post (50K). C# (.NET) library, not callable from C++. Six Labors Split License 1.0 is not an OSI license for all users (Apache-2.0 only for open-source or source-available software, transitive dependencies, non-profits and companies under 1M USD annual revenue; paid commercial license otherwise), so usability is reference.

.NET only; pure managed CPU rasterizer plus an optional WebGPU backend; retained-scene mode needs the scene to be recorded up front; licence is not OSI-approved for larger commercial users.

## Maintenance

Active: 3.0.0 on 2026-05-12, 3.1.0 on 2026-08-12 and 3.1.2 on 2026-09-17 on NuGet, last commit 2026-09-17, and main already retargeted to net10/net11. It is reference only, because it is C# and under the non-OSI Six Labors Split License (paid licence for direct use by companies with 1M USD or more revenue outside open-source software).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The numbers exist only in the vendor's release posts on sixlabors.com, which is blocked here; WebSearch snippets confirm SkiaSharp 103.4 ms, ImageSharp.Drawing CPU 43.0 ms and retained 11.9 ms (3.1.0) and WebGPU retained 5.476 ms, about 19x faster than SkiaSharp (3.0.0). The benchmark code tests/ImageSharp.Drawing.Benchmarks/Drawing/FillParis.cs is public, but first-party snippet-only numbers cap at C.
- **Verifier notes:** Tier C confirmed; the main finding is that the CPU 'faster than Skia' result compares a multi-threaded rasterizer against single-threaded SkiaSharp. Off-language (C#) and non-OSI license; hardware field left as recorded because the snippets I saw did not state the machine. Metadata checked on github.com: Six Labors Split License 1.0, 317 stars, 47 forks, not a fork, last commit 2026-09-17 (active).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/SixLabors/ImageSharp.Drawing>
  - <https://github.com/SixLabors/ImageSharp.Drawing/commits/main>
  - <https://github.com/SixLabors/ImageSharp.Drawing/tree/main/src/ImageSharp.Drawing/Processing/Backends>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/ImageSharp.Drawing.Benchmarks/Drawing/FillParis.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/ImageSharp.Drawing.Benchmarks/ImageSharp.Drawing.Benchmarks.csproj>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/ImageSharp.Drawing.Tests/TestUtilities/SvgBenchmarkHelper.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/ImageSharp.Drawing.Tests/TestUtilities/SvgBenchmarkHelper.Backends.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing/Processing/Backends/DEFAULT_DRAWING_BACKEND.md>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing/Processing/Backends/DEFAULT_RASTERIZER.md>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing/Processing/Backends/ParallelExecutionHelper.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/SixLabors/ImageSharp.Drawing/tree/main/src>
  - <https://github.com/SixLabors/ImageSharp.Drawing/tree/main/src/ImageSharp.Drawing.WebGPU>
  - <https://github.com/SixLabors/ImageSharp.Drawing/issues?q=is%3Aissue+sort%3Aupdated-desc>
  - <https://github.com/SixLabors/ImageSharp.Drawing/pulls?q=is%3Apr+is%3Amerged+sort%3Aupdated-desc>
  - <https://github.com/SixLabors/ImageSharp.Drawing/pull/417>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/README.md>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing/ImageSharp.Drawing.csproj>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing/Path.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing/ComplexPolygon.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing/Processing/Backends/DEFAULT_DRAWING_BACKEND.md>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing/Processing/Backends/DEFAULT_RASTERIZER.md>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing/Processing/Backends/ParallelExecutionHelper.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing.WebGPU/WEBGPU_BACKEND.md>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing.WebGPU/WEBGPU_RASTERIZER.md>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing.WebGPU/WebGPUDrawingBackend.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing.WebGPU/WebGPUFlushContext.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing.WebGPU/WebGPURenderTarget.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/src/ImageSharp.Drawing.WebGPU/ImageSharp.Drawing.WebGPU.csproj>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/ImageSharp.Drawing.Benchmarks/Drawing/FillParis.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/ImageSharp.Drawing.Benchmarks/Drawing/FillTiger.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/ImageSharp.Drawing.Benchmarks/ImageSharp.Drawing.Benchmarks.csproj>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/ImageSharp.Drawing.Tests/TestUtilities/SvgBenchmarkHelper.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/ImageSharp.Drawing.Tests/TestUtilities/SvgBenchmarkHelper.Backends.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/ImageSharp.Drawing.Tests/TestImages.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/ImageSharp.Drawing.Tests/TestFile.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/Images/Input/Svg/paris-30k.svg>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/main/tests/Directory.Build.targets>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/v3.1.0/tests/Directory.Build.targets>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/v3.0.0/tests/Directory.Build.targets>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/v3.1.0/tests/ImageSharp.Drawing.Benchmarks/Drawing/FillParis.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/v3.0.0/tests/ImageSharp.Drawing.Benchmarks/Drawing/FillParis.cs>
  - <https://raw.githubusercontent.com/SixLabors/ImageSharp.Drawing/v3.1.0/src/ImageSharp.Drawing.WebGPU/WebGPUDrawingBackend.cs>
  - <https://api.nuget.org/v3/registration5-semver1/sixlabors.imagesharp.drawing/index.json>
  - <https://api.nuget.org/v3/registration5-semver1/sixlabors.imagesharp.drawing.webgpu/index.json>
  - WebSearch: "ImageSharp.Drawing" 3.1 benchmark FillParis SkiaSharp Ryzen (snippet of https://sixlabors.com/posts/announcing-imagesharp-drawing-310/)
  - WebSearch: sixlabors ImageSharp.Drawing 3.1.0 FillTiger SingleThreaded SkiaSharp benchmark results (no single-threaded numbers found)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/sixlabors/imagesharp.drawing`) · [data/wave10/enrich/raw/github_com_sixlabors_imagesharp_drawing.json](../../../data/wave10/enrich/raw/github_com_sixlabors_imagesharp_drawing.json) (enrichment confidence 0.7)

</details>
