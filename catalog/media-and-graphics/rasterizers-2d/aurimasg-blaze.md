# Blaze (aurimasg/blaze)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Research-grade multi-threaded CPU rasterizer for solid-color path fills; the author reports 2.6x faster than multi-threaded Blend2D (2023 version) on an M1 Max.

| | |
|---|---|
| **Beats** | Blend2D, Skia (CPU), Apple CoreGraphics |
| **Claimed result** | Search-result summaries of the author's article: Paris-30k (4222x3474, 50,681 layers) renders in 18 ms with Blaze vs 47 ms Blend2D, 190 ms Skia and 390 ms CoreGraphics (about 2.6x over Blend2D and about 10.6x over Skia, derived from snippet data); also described as around 20x faster than Core Graphics overall. Snippet only. |
| **Workload** | Multi-threaded CPU rasterization of large vector scenes (Paris-30k map, 4222x3474 px) and text, compared with Blend2D, Skia and CoreGraphics; each image rendered 500 times, 5 best and 5 worst dropped, remaining 490 averaged (per snippet of the author's article). |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max, 10 cores (per search-result snippet of the author's article) |
| **Adoption** | 201 stars |
| **Last commit** | 2024-09-30 |
| **Links** | [repository](https://github.com/aurimasg/blaze) · [benchmark](https://gasiulis.name/parallel-rasterization-on-cpu/) |

## Verdict

The claim exists only in search snippets of the author's blocked article. On an Apple M1 Max (10 cores), Paris-30k (50,681 paths, drawn at 2x scale to 4222x3474) takes 18 ms with Blaze, 47 ms with Blend2D (2023-era, multi-threaded with threadCount = hardware threads), 190 ms with Skia and 390 ms with CoreGraphics. The harness renders 500 times and averages the middle 490 whole-millisecond system_clock readings. The repo's adapters show that Skia (SkCanvas::MakeRasterDirect) and CoreGraphics (CGBitmapContext) run single-threaded, so the 10.6x and about 20x figures mostly reflect 10 cores against 1. Blend2D is the only like-for-like (multi-threaded) baseline, and its BLContext is created and ended inside every timed frame. Anti-aliasing is the same class for Blaze and Blend2D (analytic area coverage), but no image comparison is published. The harness also has three output-equivalence flaws. The Skia adapter passes Blaze's premultiplied colors to SkPaint::setColor, which expects unpremultiplied ARGB, so Skia draws Paris-30k's 33,171 translucent paths (of 50,681) with wrong colors. All three baseline adapters ignore each path's fill rule, so they draw Tiger's 235 even-odd paths as nonzero (Paris-30k is all nonzero). The CoreGraphics adapter leaves path and color pointers uninitialized for fully transparent paths (none in Paris-30k). None of these changes the work much, but the outputs are not identical. No compiler, flags, library versions or result files are published, and the Benchmarks/ files have no build file.

## Use it when

- Rendering very large, static, fill-only vector scenes (maps, CAD or GIS layers, pre-flattened text) at high resolution on a many-core Apple Silicon Mac, where one frame has tens of thousands of paths.
- WebAssembly apps that can enable SharedArrayBuffer (cross-origin isolation headers) and want a multi-threaded software rasterizer; the repo ships an Emscripten build script and demo.
- As a reference design for band-parallel scanline rasterization (sparse cell accumulation with bit vectors) when building your own renderer.
- When geometry is already converted to fills with premultiplied solid colors, and you need throughput rather than a full 2D API.

## Skip it when

- You need a general 2D API (strokes, dashes, gradients, images, clipping, text, blend modes): use Blend2D, Skia or another full library.
- Windows, which is unsupported per the README. Linux builds also need a patch, because Threads.cpp calls the Darwin-only pthread_set_qos_class_self_np on every non-Emscripten build.
- Single-core or low-core targets, or small scenes: the design relies on parallelism, the README makes no single-thread claim, and a search snippet of a Hacker News comment says Blend2D beats Blaze in some tests on x86_64.
- Production use that needs support: code is essentially unchanged since June 2023, and correctness reports go unanswered. Issue #8 (open) says the Paris-30k output differs from Inkscape's, issue #4 (open since 2023-10) reports a broken Tiger render with suspected threading problems, and issue #7 (radiation symbol defect) was closed with no fix commit.

## How it is fast

Rendering runs in three parallel phases on a pthread worker pool sized to the online CPU count. (1) Paths are transformed, curves flattened in 24.8 fixed point, and the resulting lines binned per path into 16-pixel-tall tile rows, with start-of-row cover values, all in parallel across paths. (2) Per-row lists of contributing paths are built in parallel bands. (3) Each 16-row band is rasterized independently in paint order. Rasterization uses exact-area cover/area accumulation into a dense per-band int32 table, plus a bit vector of touched cells that is walked with popcount and count-trailing-zeros to emit spans. Fully covered runs are filled from the carried cover, and spans are composited with 64-bit SWAR source-over, with a store-only fast path for opaque spans and for zero destination pixels. Per-thread bump allocators avoid malloc during a frame.

## Compared with alternatives

Pick Blaze over Blend2D only for fill-only scenes on many-core macOS or WebAssembly where you can feed pre-converted geometry, and only after benchmarking against a current Blend2D. Blend2D is maintained, full-featured, cross-platform and has its own multi-threaded context. Over Vello CPU, AGG or tiny-skia, Blaze's case is solely parallel fill throughput in C++. Those siblings offer strokes, paints and active maintenance.

## Integration

| | |
|---|---|
| **Form** | source-drop (Blaze/ directory: header templates plus 9 .cpp files; no CMake or library target) |
| **Dependencies** | none beyond POSIX threads and the C11 &lt;stdatomic.h&gt; header used from C++ |
| **Minimum toolchain** | C++20 with Clang: the Xcode demo uses gnu++20 with Release at -Ofast and SIMD_NEON=1, and the WebAssembly build uses em++ -O3 -std=c++20 -fno-rtti -fno-exceptions. GCC builds are not shown. |
| **Platforms** | macOS (arm64 NEON path or generic C++) and WebAssembly with pthreads; other POSIX systems after patching the QoS call; no Windows |
| **Thread safety** | Not documented. Rasterization is internally parallel. A Threads instance owns one shared task list, so do not run two Rasterize calls on the same Threads object concurrently. Its worker threads are never joined or stopped (\~Threads is empty). |
| **Drop-in for the baseline** | no |

## Gotchas

- Colors must be premultiplied RGBA8, and the destination must be cleared by the caller. Call Threads::ResetFrameMemory after each frame (the benchmark does), or per-frame bump memory keeps growing.
- There is no SVG importer: issue #6 asks for the converter that produced the .vectorimage files, and it is not published, so you build Geometry arrays yourself.
- Matrix::PreMultiply computed the wrong translation component until the 2024-09-30 fix (issue #5). The benchmark is unaffected because per-path transforms are identity and the frame matrix is scale plus translate, but older copies are wrong under rotation or skew.
- Curve flattening uses fixed tolerances: quadratics are split until the control point lies within 0.125 px (L1) of the chord midpoint, and cubics until each second difference is at most 0.5 px. That bounds the deviation at roughly 0.18 px (derived from LinearizerUtils.h). Coordinates are quantized to 1/256 px.

## Known shortcomings

- Snippet-only numbers (gasiulis.name article blocked): Paris-30k 18 ms vs Blend2D 47, Skia 190, CoreGraphics 390 on an M1 Max; Benchmarks/Benchmark.cpp matches the 500-run method but publishes no results. Skia ran single-threaded while Blend2D ran multi-threaded, so the Blend2D comparison is not like-for-like.
- The Paris-30k comparison is not configuration-matched: the Skia and CoreGraphics adapters run single-threaded against Blaze's 10 workers, and Blend2D is multi-threaded but has its BLContext created inside each timed frame. The Skia adapter passes premultiplied colours as unpremultiplied (33,171 of 50,681 Paris-30k paths are translucent, so Skia's output colours are wrong); every baseline adapter ignores the fill rule (Tiger: 235 of 301 paths even-odd); no image diff is done. Open issues #8 (Paris-30k output differs from Inkscape, unanswered) and #4 (broken Tiger render); Threads.cpp calls the Darwin-only pthread_set_qos_class_self_np so a Linux build needs a patch; Benchmarks/ has no build file; the demo Release build uses -Ofast. An HN snippet reports Blend2D beating Blaze in some x86_64 tests.

## Caveats and trade-offs

Snippet only: the numbers come from search-result summaries of the author's article gasiulis.name/parallel-rasterization-on-cpu (linked from the README; egress blocked, not opened), and compiler and flags are unknown. The repo's Benchmarks/ code (opened) gives Blend2D a multi-threaded context with threadCount = hardware thread count (BenchmarkBlend2D.cpp), so the 2.6x over Blend2D is multi-threaded against multi-threaded, but Skia renders through a single-threaded SkCanvas::MakeRasterDirect canvas (BenchmarkSkia.cpp), so the 10.6x over Skia is mostly parallelism. Timing uses std::chrono::system_clock truncated to whole milliseconds (Benchmark.cpp), coarse for 18 ms frames although averaged over 490 runs. The Blend2D version measured (2023 era) is much older than current Blend2D. No results file in the repo. No Windows support.

Supports any POSIX-threads system (including WebAssembly) but not Windows; relies on fast bit counting and trailing-zero instructions; multi-threaded design, so single-thread wins are not claimed.

## Maintenance

Stale (feature work ended June 2023; the last commits on 2024-09-30 are a matrix fix and cleanup; three open issues without replies). It is MIT and small enough to vendor, but treat it as a research codebase, not a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers that exist only in search-result snippets of the author's blocked article (Paris-30k: Blaze 18 ms, Blend2D 47 ms, Skia 190 ms, CoreGraphics 390 ms on an M1 Max with 10 cores). The repo's Benchmarks/Benchmark.cpp matches the stated method (RunCount = 500, sorted, 5 best and 5 worst dropped, 490 averaged) but no compiler, flags or result files are published, so C is the cap.
- **Verifier notes:** Two WebSearch snippets of the article confirm 18/47/190/390 ms, the M1 Max 10-core machine and the 500-run method; the 'around 20x faster than CoreGraphics' phrase also appears in snippets. Metadata (MIT, 201 stars, last commit 2024-09-30, stale) checked on github.com.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/aurimasg/blaze>
  - <https://github.com/aurimasg/blaze/commits>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/README.md>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/LICENSE>
  - <https://github.com/aurimasg/blaze/tree/master/Benchmarks>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Benchmarks/Benchmark.cpp>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Benchmarks/BenchmarkBlend2D.cpp>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Benchmarks/BenchmarkSkia.cpp>
- **Sources the enricher read:**
  - <https://github.com/aurimasg/blaze>
  - <https://github.com/aurimasg/blaze/commits>
  - <https://github.com/aurimasg/blaze/commits/master>
  - <https://github.com/aurimasg/blaze/issues?q=is%3Aissue>
  - <https://github.com/aurimasg/blaze/issues/4>
  - <https://github.com/aurimasg/blaze/issues/5>
  - <https://github.com/aurimasg/blaze/issues/7>
  - <https://github.com/aurimasg/blaze/issues/8>
  - <https://github.com/aurimasg/blaze/tree/master/Benchmarks>
  - <https://github.com/aurimasg/blaze/tree/master/Blaze>
  - <https://github.com/aurimasg/blaze/tree/master/Demo_macOS>
  - <https://github.com/aurimasg/blaze/tree/main/Images>
  - <https://github.com/aurimasg?tab=repositories>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/README.md>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Benchmarks/Benchmark.cpp>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Benchmarks/Benchmark.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Benchmarks/BenchmarkBlaze.cpp>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Benchmarks/BenchmarkBlend2D.cpp>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Benchmarks/BenchmarkSkia.cpp>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Benchmarks/BenchmarkCoreGraphics.cpp>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/Blaze.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/Rasterizer.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/Rasterizer_p.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/RasterizerUtils.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/Linearizer.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/Linearizer_p.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/LinearizerUtils.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/CurveUtils.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/CurveUtils.cpp>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/Threads.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/Threads.cpp>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/CompositionOps.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/CompositionOps_64.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/BitOps.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/BitOps_gcc.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/SIMD.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/Utils.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/Geometry.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/PathTag.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/FillRule.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/F24Dot8.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/TileDescriptor_8x8.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/Matrix.cpp>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/VectorImage.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/VectorImage.cpp>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Blaze/DestinationImage.h>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Demo_wasm/build>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Demo_wasm/webserver>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Demo_macOS/Demo_macOS.xcodeproj/project.pbxproj>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Images/Paris-30k.vectorimage>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Images/Paragraphs.vectorimage>
  - <https://raw.githubusercontent.com/aurimasg/blaze/HEAD/Images/Tiger.vectorimage>
  - WebSearch: "Blaze" rasterizer gasiulis "parallel rasterization on CPU" Blend2D threads single-threaded (snippets of gasiulis.name/parallel-rasterization-on-cpu/ and news.ycombinator.com/item?id=46473247; pages not opened)
  - WebSearch (news.ycombinator.com only): Blaze rasterizer Blend2D x86_64 beats benchmark kobalicek (snippets only; threads not opened)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/aurimasg/blaze`) · [data/wave10/enrich/raw/github_com_aurimasg_blaze.json](../../../data/wave10/enrich/raw/github_com_aurimasg_blaze.json) (enrichment confidence 0.75)

</details>
