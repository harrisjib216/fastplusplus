# dg2d (D 2D vector rasterizer, cerjones)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `D` · `BSL-1.0` · 🔴 abandoned

> Single-threaded SSE2 analytic-coverage 2D path rasterizer in D; claims speed but publishes no comparison with Cairo or Blend2D.

| | |
|---|---|
| **Beats** | Cairo (C) and Blend2D (C++), named only in the orchestrator's lead; the repository names no baseline |
| **Claimed result** | none: the README says only 'Very fast, high performance rasterizer with SIMD support' and 'Best performance is with LDC'. The lead's 'about 2x Cairo' was not found in the README, the issues (#4 on memory, #8 on glyph speed against GDI) or search results; the maintainer estimates a 4x speedup is possible for glyph rendering in issue #8. |
| **Workload** | 2D path rasterization with SIMD (SSE2) into 32 bits-per-pixel buffers; no benchmark is published |
| **Metric** | throughput |
| **Compiler and flags** | README: best with LDC and link-time optimization or cross-module inlining so the intel-intrinsics get inlined; no flags beyond that |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 21 stars; a D forum snippet describes dplug:graphics as a dg2d fork |
| **Last commit** | 2022-05-06 |
| **Links** | [repository](https://github.com/cerjones/dg2d) |

## Verdict

Nothing was measured: the README says only 'Very fast, high performance rasterizer with SIMD support' and that LDC with LTO or cross-module inlining performs best, the lead's 'about 2x Cairo' appears nowhere, and issue #8 discusses glyph speed against GDI without timings while the maintainer estimates a possible 4x glyph speedup from caching.

## Use it when

- A D program that needs anti-aliased solid or gradient path fills into its own 32 bpp buffer on x86 without linking a C or C++ graphics library.
- Studying a compact (about 1,000-line) delta-coverage scanline rasterizer with a span bitmask before reading Blend2D's much larger code base.
- UI or plugin rendering in D where the maintained Dplug fork (dplug:canvas, nothrow @nogc, no alignment requirement) is the real target and dg2d is the upstream reference.
- Filling many small shapes or glyph outlines per frame on one core, which is what the demo panels exercise.

## Skip it when

- You need evidence that it beats Cairo or Blend2D: no benchmark, timing table or baseline exists in the repository or its issues, and the demo's FPS readout compares against nothing.
- You need stroking, images, pattern fills, transforms on paints, compositing operators or multi-threaded rendering; the README lists all of these as not yet done.
- Non-x86 targets or straight-alpha pixel formats: the README requires SSE2, 32 bpp with alpha in the high byte and 16-byte aligned scanlines; the maintainer said ARM testing would need a Linux port that he never did (issue #6).
- Production code that needs maintenance: library code last changed on 2020-11-14 (the 2022 commits touch only the demo's X11/XWayland window), the API is declared unstable, and a 2025 angular-gradient bug report is unanswered.
- @nogc or betterC code: the Rasterizer and Canvas are GC-allocated classes and the rasterizer's scanline, mask, bucket and clip buffers are GC dynamic arrays.

## How it is fast

The rasterizer computes exact-area (analytic) anti-aliased coverage in 24:8 fixed point and stores it per scanline in differentiated (delta) form, so long spans with constant coverage need no per-pixel work. A bitmask with one bit per 4 pixels marks cells where an edge touches the scanline; the blitters bit-scan that mask to skip empty spans or write opaque spans with plain aligned 16-byte stores, an idea the source credits to Blend2D. Blitters integrate the deltas and blend 4 pixels at a time with SSE2 intrinsics (intel-intrinsics), and edges crossing the left or right clip edge are folded into per-row clip accumulation buffers instead of being tested per pixel.

## Compared with alternatives

No rasterizer is catalogued in this category (the siblings are sorters, file tools, allocators and codecs); among catalogued rasterizers Blend2D (wave 10, tier B) and tiny-skia (tier A) have measured numbers and more features, so pick dg2d only for a D-native, dependency-light fill rasterizer, and prefer its maintained Dplug fork for real use.

## Integration

| | |
|---|---|
| **Form** | dub package (library target) or source-drop of source/dg2d/\*.d |
| **Dependencies** | intel-intrinsics \~&gt;1.0 (AuburnSounds); D runtime with GC |
| **Minimum toolchain** | Not documented; any D compiler with intel-intrinsics 1.x, LDC recommended with link-time optimization or cross-module inlining so the intrinsics inline |
| **Platforms** | x86 and x86-64 with SSE2; demo windowing on Win32 and X11; ARM untested |
| **Thread safety** | not documented; rendering is single-threaded and each Canvas and Rasterizer holds mutable per-instance state |
| **Drop-in for the baseline** | no |

## Gotchas

- The 16-byte buffer alignment and stride-multiple-of-4 rules are checked only by assert; release builds drop the checks and the blitters use aligned SSE loads and stores (_mm_load_si128/_mm_store_si128), so an external misaligned buffer can fault. Canvas allocates its own pixels with C realloc, which gives 16-byte alignment on common 64-bit allocators but is not guaranteed everywhere.
- Angular gradients with RepeatMode.Pad never select one quadrant (fixupQuadrant can produce positions down to about -0.25), so part of the gradient is missing; p0nce posted a one-line SSE fix in issue #13 (2025-04-11) that is not merged.
- Coincident edges after clipping once left zero spans in the delta buffer that made blitters skip or solid-fill wrongly (horizontal-line artifacts, issue #2, fixed in dff0979 on 2020-06-03); the delta-integration design means one bad cell corrupts the rest of the scanline. Copying a Font struct double-freed its data (issue #7); the maintainer's fix was to disable copying.
- The demo's FPS figure is the best of 5 timed paints per timer tick, maxed over the last 25 ticks (effectively best of 125), with the canvas clear outside the timed region; it is an optimistic single-core number with no baseline and is not a benchmark.

## Known shortcomings

- No numbers and no baseline; the lead's '2x Cairo' claim was not found anywhere; abandoned since 2022-05-06, 21 stars.
- Enricher: the demo FPS is the best of 125 paints with no comparison, not a benchmark; library code unchanged since 2020-11-14 (2022 commits touch the demo only); open issue #13 (angular gradient Pad mode skips one quadrant, fix unmerged); alignment checked only by assert with aligned SSE stores. A maintained fork lives in AuburnSounds/Dplug as dplug:canvas (no numbers either).

## Caveats and trade-offs

No numbers and no baseline anywhere I could open, so this is a tier D record kept for the 'research' list. The orchestrator's lead (about 2x Cairo) does not appear in the readme, the issues or search results; issue #8 ('Test render speed of 1 glyph', closed 2021-06-29) compares against GDI with no timings, and the maintainer only estimates that a 4x glyph speedup is achievable through caching and pre-flattening, plus about 2x more from a planned font rasterizer. The dub registry page shows the same self-description (search snippet only). Single-threaded, 32 bpp only, 16-byte-aligned scanlines, x86 SSE2 required, work-in-progress API. Last commit 2022-05-06 (more than four years ago), 21 stars, not notable by the tier D rule. The category fits wave 10's rasterizers-2d better than systems-and-safety.

Alpha state with an unstable API; rasterizer needs x86 SSE2, 32 bits per pixel and 16-byte aligned scanlines, depends on intel-intrinsics; single-threaded; no stroking, images or pattern fills yet.

## Maintenance

Abandoned (library code unchanged since 2020-11-14, last commit 2022-05-06 on the demo, 21 stars) but BSL-1.0 and small enough to vendor; its rasterizer lives on, reworked as nothrow @nogc without alignment requirements, in Dplug's dplug:canvas, which is the better-maintained copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The readme only says 'Very fast, high performance rasterizer with SIMD support' and 'Best performance is with LDC'; there is no benchmark directory, no numbers and no named baseline, and issue #8 discusses glyph speed against GDI without timings, so tier D.
- **Verifier notes:** Confirmed as tier D with no measurement and no baseline; keep-and-document rather than reject (low notability, abandoned, 21 stars). No language-level claim can be drawn: nothing compares the D code against Cairo or Blend2D.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-118 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/cerjones/dg2d>
  - <https://raw.githubusercontent.com/cerjones/dg2d/HEAD/readme.md>
  - <https://github.com/cerjones/dg2d/commits>
  - <https://github.com/cerjones/dg2d/issues/8>
- **Sources the enricher read:**
  - <https://github.com/cerjones/dg2d>
  - <https://raw.githubusercontent.com/cerjones/dg2d/HEAD/readme.md>
  - <https://raw.githubusercontent.com/cerjones/dg2d/HEAD/dub.json>
  - <https://github.com/cerjones/dg2d/tree/master/source/dg2d>
  - <https://raw.githubusercontent.com/cerjones/dg2d/HEAD/source/dg2d/rasterizer.d>
  - <https://raw.githubusercontent.com/cerjones/dg2d/HEAD/source/dg2d/colorblit.d>
  - <https://raw.githubusercontent.com/cerjones/dg2d/HEAD/source/dg2d/canvas.d>
  - <https://raw.githubusercontent.com/cerjones/dg2d/HEAD/source/dg2d/blend.d>
  - <https://raw.githubusercontent.com/cerjones/dg2d/HEAD/source/dg2d/misc.d>
  - <https://github.com/cerjones/dg2d/tree/master/demo/source>
  - <https://raw.githubusercontent.com/cerjones/dg2d/HEAD/demo/source/app.d>
  - <https://raw.githubusercontent.com/cerjones/dg2d/HEAD/demo/source/panels.d>
  - <https://github.com/cerjones/dg2d/issues?q=is%3Aissue>
  - <https://github.com/cerjones/dg2d/issues/2>
  - <https://github.com/cerjones/dg2d/issues/6>
  - <https://github.com/cerjones/dg2d/issues/7>
  - <https://github.com/cerjones/dg2d/issues/13>
  - <https://github.com/cerjones/dg2d/commits/master>
  - <https://raw.githubusercontent.com/AuburnSounds/Dplug/HEAD/canvas/dplug/canvas/package.d>
  - <https://raw.githubusercontent.com/AuburnSounds/Dplug/HEAD/canvas/dplug/canvas/rasterizer.d>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/cerjones/dg2d`) · [data/wave14/enrich/raw/github_com_cerjones_dg2d.json](../../../data/wave14/enrich/raw/github_com_cerjones_dg2d.json) (enrichment confidence 0.85)

</details>
