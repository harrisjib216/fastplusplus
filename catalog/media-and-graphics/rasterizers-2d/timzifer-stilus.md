# stilus

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Pure-Go sparse 2D rasterizer; 2.0x x/image/vector on 20k short strokes (first-party); 477x hatch figure is harness-inflated.

| | |
|---|---|
| **Beats** | golang.org/x/image/vector (the Go project's rasterizer) and gogpu/gg v0.52.5 CPU rasterizer |
| **Claimed result** | README comparison table, 20,000 short strokes: stilus 55 ms versus x/image/vector 111 ms (about 2.0x, derived from page data; stilus clips a 10 mm page margin that skips about 9% of the strokes) and gogpu/gg 2,090 ms. The 2,000 hatch-line row (stilus 70 ms versus x/image/vector 33,400 ms, about 477x) is a harness artefact: the x/image/vector side re-creates a page-spanning rasteriser per line (about 3.6e9 bounding-box pixels in total, derived); a single page-sized pass would take roughly 40 ms (derived, unmeasured). Separate 'Numbers' table (minimum of 15): stilus 1 core 67 ms (2,000 hatch lines at 0.35 mm) and 41 ms (20,000 short strokes), 4 cores 19 ms and 12 ms. |
| **Workload** | Synthetic print-style scenes on an A3 landscape page at 150 dpi (2481x1754 px) from internal/scenes: Hatch (2,000 parallel 45-degree hairlines spanning the page, drawn one device pixel wide) and Short (20,000 random 2-8 mm strokes, 0.35 mm wide). stilus draws through its Canvas with a page clip; the x/image/vector run strokes each line with stilus's own stroker and fills each outline with one vector.Rasterizer reset to that outline's bounding box; gogpu/gg strokes each line with no clip. |
| **Metric** | throughput |
| **Hardware** | 'Same machine' as the Numbers table: cloud Xeon @ 2.1 GHz (exact model not stated), minimum of 15 runs; some speed levers were measured on a Ryzen 7 5800H |
| **Compiler and flags** | Go; the comparison lives in the separate bench module (bench/go.mod: go 1.26.0, golang.org/x/image v0.46.0, github.com/gogpu/gg v0.52.5; the core module's go.mod says go 1.24); exact toolchain version for the table not stated; run with `cd bench && go test -bench .` (bench/compare_test.go). |
| **Adoption** | 0 stars, very new repo |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/timzifer/stilus) · [benchmark](https://github.com/timzifer/stilus) |

## Verdict

First-party README table produced by bench/compare_test.go (go test -bench, one goroutine, bench module on Go 1.26 with x/image v0.46.0 and gogpu/gg v0.52.5) on an unnamed 'cloud Xeon @ 2.1 GHz', A3 page at 150 dpi: 20,000 short 0.35 mm strokes take 55 ms with stilus versus 111 ms with x/image/vector (2.0x, derived from page data) and 2,090 ms with gg; 2,000 page-spanning hairline hatch lines take 70 ms versus 33,400 ms (477x) and 14,800 ms. The x/image/vector side uses stilus's own stroker and a separate box-sized rasterizer for each outline.

## Use it when

- Go programs that render technical drawings, CAD- or PDF-like pages, maps or plots with many long thin strokes (hatching, contours) on the CPU, where x/image/vector's cost per path grows with the path's bounding-box area.
- Builds that must stay pure Go with no cgo, for cross-compiling or js/wasm.
- Large pages rendered in bands on several cores: the README Numbers table gives 67 ms on 1 core and 19 ms on 4 cores for 2,000 hatch lines at 0.35 mm, and 41 ms vs 12 ms for 20,000 short strokes.
- Custom compositors or GPU upload paths that want spans rather than pixels, by implementing Blitter or Shader.
- Render loops sensitive to GC pressure, since the README and alloc-gate tests claim zero allocations per scene after warm-up.

## Skip it when

- Production code that needs a stable, proven library: the repository is days old (0 stars, tags v0.4.0 to v0.7.0 all on 1-2 October 2026, one maintainer, some commits authored by an AI coding agent account), and the API is still moving.
- Text layout, font loading, colour management, or SVG/PDF parsing or output: the README lists these as out of scope.
- Dense overlapping fills or strokes of one colour that must look seamless: separately drawn paths conflate at anti-aliased edges. Open issue #28 reports 24.9% of pixels off by more than 16/255 on the 2,000-line hatch at 150 dpi against an exact union (Ghostscript 0.06%), and the proposed union fill is in open PR #29.
- Glyph-sized or short shapes where x/image/vector is already box-efficient: the gain there is about 2x (55 vs 111 ms on 20,000 short strokes), and the SIMD kernels stay scalar below 16 px spans.
- Picking a renderer across languages: only Go baselines (x/image/vector, gogpu/gg) were measured, with no comparison against C/C++ engines such as Blend2D, Skia or AGG.

## How it is fast

Cost follows edge length plus covered spans, not bounding-box area: edges are accumulated as FreeType/AGG-style area/cover cells into a 32-row band (24.8 fixed point) instead of a page-sized buffer, and the sweep integrates only the touched cells of narrow rows, or walks a dirty bitset and emits constant runs on wide rows, zeroing cells as it reads them. Stroked polyline segments take an analytic path in which each pixel's coverage is the difference of two closed-form half-plane areas; only the rows around joins and caps go through the accumulator. Rectangle clips cost nothing per pixel, compositing is SWAR on premultiplied RGBA8 (AVX2/AVX-512 kernels under GOEXPERIMENT=simd), destination rows are pre-touched so cache misses overlap, prepared Shapes let band-parallel workers reuse stroking, and drawing allocates nothing after warm-up.

## Compared with alternatives

The closest catalogued sibling is tdewolff/canvas (Go): pick stilus when you only need a fast, allocation-free rasterizer core for stroke-heavy pages and will build the rest yourself, and tdewolff/canvas when you want a complete Go vector library with text and file output. For C or C++ code, Blend2D or Vello CPU have far stronger evidence.

## Integration

| | |
|---|---|
| **Form** | Go module (github.com/timzifer/stilus); comparison benchmarks live in a separate bench module |
| **Dependencies** | none (standard library only); the bench module adds golang.org/x/image v0.46.0, gogpu/gg v0.52.5 and timzifer/figure |
| **Minimum toolchain** | Go 1.24 (go.mod); Go 1.26 or 1.27 with GOEXPERIMENT=simd for the AVX2/AVX-512 compositing kernels |
| **Platforms** | all GOOS/GOARCH including js/wasm with scalar kernels; SIMD kernels only on amd64 with GOEXPERIMENT=simd, chosen at run time |
| **Thread safety** | Use one Canvas per goroutine; a prepared Shape can be drawn by several band canvases concurrently (README). Other concurrency guarantees are not documented. |
| **Drop-in for the baseline** | partial: it replaces x/image/vector's role as a pure-Go anti-aliased path filler, but the API differs (Path plus Matrix plus FillRule into a Canvas or Blitter, rather than MoveTo/LineTo into a box-sized Rasterizer followed by Draw), so call sites must be rewritten |

## Gotchas

- Strokes thinner than one device pixel are drawn one pixel wide (PDFium-style hairlines), so very thin lines come out wider and darker than their exact geometry.
- Dash patterns past the subdivision budget skip or truncate the affected subpath and set ErrDashBudget, and patterns finer than a quarter pixel are drawn as a solid stroke at the pattern's mean coverage; the Canvas never panics, so check Err() after drawing.
- The SIMD kernels exist only with GOEXPERIMENT=simd on amd64, and the experiment's API changed between Go 1.26 and 1.27 (handled by build-tagged wrappers); STILUS_SIMD=0 or 256 forces scalar or AVX2-only at run time.
- Drawing many paths of one paint one by one gives conflation seams on touching anti-aliased edges (issue #28); until a union fill lands, merge such geometry into one path yourself.

## Known shortcomings

- Go (language-filter mismatch). The 477x on hatch lines is unfair: the baseline builds one golang.org/x/image/vector rasterizer per 45-degree page-spanning line sized to its bounding box; short strokes at 2.0x are roughly fair. Bench module uses Go 1.26.0 on a 'cloud Xeon @ 2.1 GHz' only. Baseline is not a listed incumbent.
- The 477x hatch figure is a harness artefact (retier-22 removes it): the x/image/vector side re-creates a page-spanning rasteriser per 45-degree line, paying about 3.6e9 bounding-box pixels in total, whereas one page-sized pass would take about 40 ms against stilus's 70 ms (derived, unmeasured). stilus clips a 10 mm page margin the others do not, skipping about 9% of the short strokes; comparison times are go test means while the Numbers table is a minimum of 15. Open issue #28 (conflation seams, 24.9% of pixels off by more than 16/255 on hatch; fix in PR #29); tags v0.4.0 to v0.7.0 were all cut on 1-2 October 2026, some commits by an AI agent account.

## Caveats and trade-offs

The 477x hatch ratio is not a fair measure of x/image/vector: that rasterizer is a dense area accumulator whose cost is proportional to the canvas it is sized to, and the harness resets and draws one rasterizer per 45-degree page-spanning line, so each of 2,000 lines pays for a bounding box of up to about 1754x1754 px; a single page-sized rasterizer filled with all outlines (same result for opaque black) would very likely narrow the gap by orders of magnitude, but that was not measured. The short-stroke row (about 2.0x, derived from page data: 111 ms vs 55 ms) is the representative comparison, and it includes stilus's own stroker on both sides. x/image/vector is the Go project's glyph-oriented rasterizer and gogpu/gg a community library, neither a catalogue baseline (Skia, Cairo, Blend2D), so baseline_in_list is false; quality is only checked against PDFium (mean deviation 0.3-1.5/255, SSIM at least 0.998). The comparison's stilus hatch time (70 ms) does not match the Numbers table's hairline hatch (53 ms), so the tables were likely measured at different times. First-party, one author, repo created days ago (0 stars), CPU model not named exactly, benchmark source read but not run.

Pure Go, no cgo, no dependencies, builds for all GOOS/GOARCH including js/wasm; zero allocations after warm-up; sparse cost model (edge length plus covered spans); exact-area coverage like FreeType/AGG; optional AVX2/AVX-512 compositing under GOEXPERIMENT=simd; it is only the rasterizer core of a planned PDF renderer (no fonts, colour spaces or display lists).

## Maintenance

Very active but brand new (95 commits, last commit 2026-10-02, latest tag v0.7.0 on 2026-10-02, 0 stars, one open issue and one open PR); MIT and dependency-free, so copyable, but treat it as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README comparison table comes from the public bench/compare_test.go, but the CPU is only 'cloud Xeon @ 2.1 GHz' and the Go toolchain for the run is not stated; first-party, and the 477x hatch ratio (&gt;50x, from a bounding-box-bound use of the baseline) caps it at C anyway.
- **Verifier notes:** Numbers on README match the record (33,400 ms / 70 ms is 477x, 111 / 55 is 2.0x, derived from page data). Comparison is unfair on hatch lines (per-line bounding-box rasterizers for page-spanning diagonals) and roughly fair on short strokes. Metadata checked: MIT, 0 stars, not a fork, 95 commits, last commit 2026-10-02, active; language Go.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/timzifer/stilus/HEAD/README.md>
  - <https://raw.githubusercontent.com/timzifer/stilus/HEAD/bench/compare_test.go>
  - <https://raw.githubusercontent.com/timzifer/stilus/HEAD/bench/go.mod>
  - <https://raw.githubusercontent.com/timzifer/stilus/HEAD/go.mod>
  - <https://raw.githubusercontent.com/timzifer/stilus/HEAD/internal/scenes/scenes.go>
  - <https://github.com/timzifer/stilus>
  - <https://github.com/timzifer/stilus/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/timzifer/stilus/HEAD/README.md>
  - <https://raw.githubusercontent.com/timzifer/stilus/HEAD/go.mod>
  - <https://raw.githubusercontent.com/timzifer/stilus/HEAD/bench/go.mod>
  - <https://raw.githubusercontent.com/timzifer/stilus/HEAD/bench/compare_test.go>
  - <https://raw.githubusercontent.com/timzifer/stilus/HEAD/internal/scenes/scenes.go>
  - <https://github.com/timzifer/stilus>
  - <https://github.com/timzifer/stilus/tags>
  - <https://github.com/timzifer/stilus/commits/main>
  - <https://github.com/timzifer/stilus/issues>
  - <https://github.com/timzifer/stilus/issues/28>
  - <https://github.com/timzifer/stilus/pulls>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/timzifer/stilus`) · [data/wave10/enrich/raw/github_com_timzifer_stilus.json](../../../data/wave10/enrich/raw/github_com_timzifer_stilus.json) (enrichment confidence 0.75)

</details>
