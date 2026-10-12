# tdewolff/canvas

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Go` · `MIT (Fribidi component is LGPL)` · 🟢 active

> Pure-Go vector drawing library (paths, booleans, text, raster/PDF/SVG/EPS output); claims 2x over Inkscape/Cairo, no published numbers.

| | |
|---|---|
| **Beats** | Inkscape and Cairo (named in the README as 'existing solutions'; which Cairo-based tool was run, e.g. rsvg-convert or CairoSVG, is not stated on any readable page) |
| **Claimed result** | README (directional, no number on the page): 'Execution performance is actually really good, especially the rasterizer is highly optimized with ASM. See for example a comparison of an extreme case in issue #280 (comment 1995990038), where this library is at least twice as fast as existing solutions, and can handle bigger images than the likes of Inkscape and Cairo.' The linked comment could not be read, so no timing, ratio or image size is verified. |
| **Workload** | End-to-end conversion of one very large SVG (score.svg attached to issue #280, a bug report about a pathIntersections panic) to a raster image; this includes SVG parsing, path processing and rasterization, so it is not a rasterizer-only comparison with Cairo. The comparison comment itself could not be read. |
| **Metric** | throughput |
| **Adoption** | 1.8k stars, 124 forks |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/tdewolff/canvas) · [benchmark](https://github.com/tdewolff/canvas) |

## Verdict

Nothing measured is verifiable: the README asserts at least 2x over 'existing solutions' and larger images than Inkscape and Cairo for one extreme SVG (an end-to-end SVG-to-raster conversion of score.svg from issue #280), but the linked comment does not render, and no Go version, flags, hardware, tool versions or harness exist in the repo or in tdewolff/canvas_benchmarks, which covers only polygon booleans. Treat it as a directional, first-party claim made on a since-replaced rasterizer backend.

## Use it when

- Go services that need one scene rendered to several outputs (PNG plus PDF/SVG/EPS) without cgo or an external Cairo/Inkscape install.
- Server-side charts, maps and documents in Go (it ships go-chart and gonum/plot renderers and OpenStreetMap/Natural Earth examples) where text quality and bidi/complex scripts matter.
- Very large raster outputs from Go: the rasterizer accepts any image up to MaxInt32 pixels (it panics above that), allocated as one image.RGBA at 4 bytes per pixel.
- Robust polygon boolean operations on messy GIS data in pure Go, where it is comparable to Clipper2 in the author's own benchmark.

## Skip it when

- When you need a measured rasterization speedup: the only claim (at least 2x over 'existing solutions' on one extreme SVG, issue #280 comment 1995990038) has no readable number, machine or harness, and if measured it was on the x/image/vector backend that is no longer the default.
- Raster throughput-critical paths: C/C++ rasterizers in this category (Blend2D, ThorVG, tiny-skia) publish measured wins over Cairo or Skia, and gradient fills here go through a per-pixel color callback while sRGB output does a per-pixel At()/SetRGBA pass (marked 'TODO: parallelize').
- Fast polygon booleans: in the author's canvas_benchmarks union(Europe, Chile) at 87,721 segments takes 0.2563 s against 0.0368 s for iOverlay (about 7x slower, derived from page data; no hardware stated).
- Production code that cannot tolerate panics or rough edges: the README says the library 'inevitably must have a great amount of bugs', path-intersection panics recur in the issue tracker (#272, #280, #287, #306, #313), and #348 (SetCoordRect not scaling paths in the rasterizer) is open.
- Projects needing an old Go toolchain or a small module graph: go.mod requires Go 1.26 and lists Fyne, Gio, go-gl, gonum/plot, go-chart and AVIF/WebP encoders as direct requirements.

## How it is fast

The raster backend (renderers/rasterizer) flattens Béziers and arcs to line segments at a tenth-of-a-pixel tolerance, converts them to 26.6 fixed point and feeds them to srwiley/scanx, a Go port of FreeType's 'smooth' area/coverage accumulation scanner that writes spans straight into an image.RGBA; it replaced golang.org/x/image/vector in February 2025 after issue #334 reported x/image/vector as 500-1000x slower for many rounded rectangles. The README's 'highly optimized with ASM' wording dates from the x/image/vector era: scanx is plain Go with no assembly files, and rasterizer.go itself carries a TODO for an ASM version. Path booleans use a Bentley-Ottmann sweep with snap rounding (Hobby, Hershberger) for numerical stability.

## Compared with alternatives

Pick it over stilus (also Go, with measured wins over x/image/vector) when you need the whole pipeline (text layout, booleans, PDF/SVG/EPS output), not only a fast scanline fill; pick Blend2D, ThorVG or tiny-skia when raster speed is the requirement, since they publish measured results against Cairo or Skia and canvas does not.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Go module github.com/tdewolff/canvas; the raster path uses srwiley/scanx (2019 pseudo-version, self-described beta), srwiley/rasterx and golang.org/x/image; text uses go-text/typesetting and benoitkugler/textprocessing (native Go or CGO HarfBuzz/FriBidi). The root go.mod also requires Fyne, Gio, go-gl, gonum/plot, go-chart, go-avif and go-webp for the optional backends. FriBidi is LGPL. |
| **Minimum toolchain** | Go 1.26 (go.mod 'go 1.26.0') |
| **Platforms** | any Go target for the pure-Go raster/PDF/SVG/EPS paths; HTML Canvas via WASM; OpenGL, Gio and Fyne backends need their own platform support |
| **Thread safety** | not documented; a Rasterizer owns one scanx.Scanner and its target image, so use one per goroutine (issue #208 was a race in ToRasterizer, since closed) |
| **Drop-in for the baseline** | no |

## Gotchas

- The README's ASM claim is stale: the default rasterizer has used pure-Go scanx since February 2025, and scanx's own README warns 'Scanx is beta software. There are known bugs being worked on.'
- From reading the code (not tested): Path.ToScanxScanner, the default fill path, emits no implicit closing edge for open subpaths (ToVectorRasterizer closes the last one), and scanx's Start() does not close the previous contour, so filling an open subpath can lose coverage; close fill paths explicitly.
- From reading rasterizer.go: with a non-linear color space (e.g. SRGBColorSpace), RenderImage gamma-decompresses the source image in place when no rotation or shear margin is added, so the caller's image (and the canvas layer that references it) is modified, and a source that is not a draw.Image (e.g. \*image.YCbCr from JPEG decoding) hits an unchecked type assertion and panics.
- Errors surface as panics: FromImage panics on a zero-sized raster and on images over MaxInt32 pixels, and path-intersection panics have been reported repeatedly.

## Known shortcomings

- Go (language-filter mismatch). Downgraded C to D: the only claim is README line 29 ('at least twice as fast' than Inkscape and Cairo) pointing to issue #280 comment 1995990038, which never rendered here; no number, machine or harness anywhere, and canvas_benchmarks tests polygon booleans only. The wording fits the old x/image/vector backend; the default renderer switched to the pure-Go scanx on 2025-02-06 (#334), so the claim describes superseded code. MIT with LGPL FriBidi; 1.8k stars, active.
- The README's assembly claim is stale: the default rasteriser has been the pure-Go srwiley/scanx since 2025-02 (no .s files; the scanx README calls itself beta software with known bugs); issue #280 comment 1995990038 remains unreadable here. Code-reading bugs, untested and not behind numbers (there are none): ToScanxScanner does not implicitly close open subpaths so fills may lose coverage; RenderImage with sRGB gamma-converts the caller's image in place and panics on non-draw.Image inputs (image.YCbCr); open #348 (SetCoordRect scaling). In canvas_benchmarks iOverlay takes 0.0368 s against canvas 0.2563 s at 87,721 segments.

## Caveats and trade-offs

No numbers verifiable: the README links a single issue comment (issue #280, comment 1995990038, March 2024) that does not render outside a browser; no benchmark code, hardware, Go version or command lines for the rasterization comparison are public in the repo. One extreme-case file only; the issue's own opening post says canvas 'takes ages' on that file while JSVG (Java) takes 'a second or two', i.e. before the fixes canvas was slower than another renderer. The README's 'highly optimized with ASM' wording describes the golang.org/x/image/vector backend in use in March 2024 (whose accumulation loop has amd64 assembly); since commit 'Use Scanx rasterizer, fixes #334' (2025-02-06) the default renderers/rasterizer path uses the pure-Go srwiley/scanx scanner (rasterizer.go even carries a TODO to add an ASM version), after issue #334 reported x/image/vector as 500-1000x slower than scanx for GUI rounded-rectangle workloads. So the 2x claim, if it was ever measured, was measured on a superseded backend. The separate tdewolff/canvas_benchmarks repo covers polygon boolean operations only (canvas is slower than iOverlay there and comparable to Clipper2), not rasterization. First-party, no methodology. The code is MIT, but the README warns that FriBidi (used for text bidirectionality) is LGPL. Language is Go.

Pure Go vector graphics with raster, SVG, PDF, EPS, HTML Canvas and Gio outputs; assembly-optimised rasterizer is architecture specific; Fribidi and HarfBuzz can be CGO or native Go.

## Maintenance

Active (1.8k stars, 124 forks, 21 open issues, last commit 2026-09-23) and MIT-licensed apart from the LGPL FriBidi component; the README asks for funding and leaves production readiness to the user's judgment.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now D.
- **Tier reason:** The only rasterizer claim is one README sentence (line 29) saying the library is 'at least twice as fast as existing solutions' and handles bigger images than Inkscape and Cairo for an extreme case, pointing at issue #280 comment 1995990038; that comment does not render in WebFetch (three tries, comments are loaded client-side), and no benchmark code, timing table, machine or harness for rasterization exists in the repo (renderers/rasterizer holds only rasterizer.go and util.go, no \*_test.go benchmarks) or in tdewolff/canvas_benchmarks, which covers only polygon boolean operations. A directional claim with no verifiable number is tier D.
- **Verifier notes:** Downgraded C to D: the claim exists only as a README sentence pointing at an unreadable issue comment, with no number, machine or harness anywhere reachable. Notable (1.8k stars, active, last commit 2026-09-23), so kept rather than rejected; language Go, MIT, copyable. Worth a retier only if someone can read issue #280 comment 1995990038 from an environment that renders GitHub comments.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/README.md>
  - <https://github.com/tdewolff/canvas>
  - <https://github.com/tdewolff/canvas/commits>
  - <https://github.com/tdewolff/canvas/issues/280>
  - <https://github.com/tdewolff/canvas/issues/280#issuecomment-1995990038>
  - <https://github.com/tdewolff/canvas/issues/280?timeline_page=1>
  - <https://github.com/tdewolff/canvas/issues/334>
  - <https://github.com/tdewolff/canvas/tree/master/renderers/rasterizer>
  - <https://github.com/tdewolff/canvas/commits/master/renderers/rasterizer/rasterizer.go>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/renderers/rasterizer/rasterizer.go>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/renderers/rasterizer/util.go>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/path.go>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/go.mod>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/tdewolff/canvas_benchmarks/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/tdewolff/canvas>
  - <https://github.com/tdewolff/canvas/issues/280>
  - <https://github.com/tdewolff/canvas/issues/334>
  - <https://github.com/tdewolff/canvas/issues/348>
  - <https://github.com/tdewolff/canvas/issues/391>
  - <https://github.com/tdewolff/canvas/issues?q=is%3Aissue+rasterizer>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/README.md>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/go.mod>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/renderers/rasterizer/rasterizer.go>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/renderers/rasterizer/util.go>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/renderers/renderers.go>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/canvas.go>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/path.go>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/path_scanner.go>
  - <https://raw.githubusercontent.com/tdewolff/canvas/HEAD/svg.go>
  - <https://raw.githubusercontent.com/tdewolff/canvas_benchmarks/HEAD/README.md>
  - <https://github.com/srwiley/scanx>
  - <https://raw.githubusercontent.com/srwiley/scanx/HEAD/README.md>
  - <https://raw.githubusercontent.com/srwiley/scanx/HEAD/scan.go>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/tdewolff/canvas`) · [data/wave10/enrich/raw/github_com_tdewolff_canvas.json](../../../data/wave10/enrich/raw/github_com_tdewolff_canvas.json) (enrichment confidence 0.65)

</details>
