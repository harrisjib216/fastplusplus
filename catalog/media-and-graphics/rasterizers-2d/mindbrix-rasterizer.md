# Rasterizer (mindbrix)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `C++` · `Custom 'personal use zlib license' (LICENSE.txt): zlib terms, but permission is granted only for personal use, and commercial use needs a licence from the author. Not OSI-approved.` · 🟢 active

> Metal GPU 2D vector renderer (paths, strokes, gradients, clips, SVG/PDF) for macOS and iOS; claims 'up to 60x faster than the CPU', unmeasured.

| | |
|---|---|
| **Beats** | unnamed CPU path rasterization ('the CPU'); the README names no CPU renderer. HN thread snippets (seen through search only) say the author used CoreGraphics as the quality reference and called performance against Vello 'very competitive', with no numbers. |
| **Claimed result** | 'It is up to 60x faster than the CPU, making it ideal for vector animated UI' (README opening paragraph, no workload, hardware or baseline stated). |
| **Workload** | Metal GPU rendering of anti-aliased vector paths (SVG and PDF scenes, vector animated UI; HN thread snippet mentions text at 50,000 glyphs at 60fps) versus CPU rendering. |
| **Metric** | throughput |
| **Adoption** | 346 stars |
| **Last commit** | 2026-05-02 |
| **Links** | [repository](https://github.com/mindbrix/Rasterizer) · [benchmark](https://github.com/mindbrix/Rasterizer/blob/master/README.md) |

## Verdict

No measurement backs the README's 'up to 60x faster than the CPU': the repo has no benchmark code, frame timer or result file, and the demo's 'T' key toggles an animated clock scene (Concentrichron), not a timer. The only CPU renderer in the repo is the demo's '0' key toggle to Core Graphics (RaCG::renderListToBitmap drawing every path into one CGContext through CALayer drawLayer:inContext:), so the implied baseline is probably single-threaded Core Graphics versus Rasterizer's multi-core CPU preparation plus Metal GPU, with scene, hardware and method unstated; HN-thread claims (50,000 glyphs at 60 fps, Vello 'very competitive') were seen only as search snippets.

## Use it when

- macOS 12+ or iOS 13+ app that redraws animated vector UI or large SVG/PDF scenes every frame (zoom, pan, rotate) and is CPU-bound in Core Graphics.
- Text-heavy or glyph-heavy scenes: CoreText glyph outlines go into the small-fill 'molecule' path, which uploads compact 16-bit geometry and draws one instanced quad per glyph.
- You need fuller path semantics than SDF UI renderers offer (non-zero and even-odd fills, cubics, strokes with caps and round joins, dashes, gradients, path clipping) on an Apple GPU.
- Personal, research or evaluation use, or a commercial product whose owner will negotiate a licence with the author.

## Skip it when

- Commercial use without a separate licence: LICENSE.txt grants permission for personal use only; it is not an OSI licence.
- Any non-Apple target: rendering is Metal-only and the ObjC/Swift layers depend on QuartzCore, CoreGraphics and CoreText. The README's claim that it would work on any GPU with instancing and float render targets is not backed by a port.
- When you need a measured speedup before adopting: there is no benchmark harness, frame timer or result file in the repo, so the 60x figure cannot be checked; profile it on your own scenes against Core Graphics, vger or Vello.
- Complex-script text: issue #1 (open since 2025-09-04) reports that Arabic text in PDFs and SVGs renders nothing, and the demo uses a single font.
- Miter joins or exact-area anti-aliasing: the Scene flags expose only round or default joins and butt/round/square caps, and coverage comes from a filtered inverse-lerp approximation, not an exact area integral.

## How it is fast

Each frame the CPU transforms and clips path geometry in parallel (dispatch_apply over one Ra::Context per online core, split by edge-count weight) and memcpys it into a page-aligned shared buffer that Metal wraps with newBufferWithBytesNoCopy; the GPU holds no per-path state. Small fills such as glyphs ('molecules') are uploaded as 16-bit fixed-point points relative to the path bounds and drawn as instanced quads, while larger fills use 'fat scanlines' (16-px bands): edges are binned per band, x-sorted (radix sort), interior spans become solid opaque or blended cells and only edge cells run the coverage shader. Coverage accumulates additively into an R32Float mask texture using the author's 'windowed inverse lerp' (awinding in Shaders.metal: an inverse lerp of signed corner areas, then a slope-dependent filter) and monotone quadratic Beziers are solved per pixel on the GPU, so curves need little CPU flattening. Opaque interiors are drawn front to back with a depth test so hidden pixels are skipped, and strokes are triangulated on the GPU straight into the colour buffer.

## Compared with alternatives

Pick it over vger when you need real PostScript paths (cubics, non-zero fill, joins, dashes, clips, SVG/PDF content) rather than SDF UI primitives, and over Pathfinder 3 or Vello when you only ship on Apple GPUs and can accept a personal-use licence. Pick vger (MIT), Pathfinder, Vello or the Rive Renderer for open-source licensing, other platforms or published numbers, and Blend2D or Blaze when a CPU renderer with measured results is enough.

## Integration

| | |
|---|---|
| **Form** | Swift package (Package/Package.swift: RasterizerCpp headers, RasterizerObjC Metal layer and view, RasterizerSwift) or source-drop of the C++ headers plus Shaders.metal into an Xcode project |
| **Dependencies** | Apple Metal, QuartzCore, CoreGraphics, CoreText; bundled xxhash.h and nanosvg.h; the demo app also bundles pdfium.xcframework and credits stb_truetype |
| **Minimum toolchain** | Swift tools 6.0 and C++11 (cxxLanguageStandard .cxx11 in Package.swift); Xcode with the Metal compiler |
| **Platforms** | macOS 12+ and iOS 13+ (Package.swift) on Metal GPUs only; the README still says an iOS port is 'in the pipeline', but a RasterizeriOS project was added in January 2026 |
| **Thread safety** | Not documented. RasterizerRenderer::renderList fans work out internally with dispatch_apply over per-core Ra::Context objects and is not reentrant. Path, Scene and other Ref&lt;&gt; handles use plain non-atomic size_t reference counts, so do not copy or release shared handles from several threads at once. |
| **Drop-in for the baseline** | no |

## Gotchas

- Possible curvature-estimate bug: Geometry::quadTo assigns x0/y0 = (x2, y2) before computing 'ax = x2 + x0 - x1 - x1', so maxCurve stores 4|p2-p1|^2 instead of the second difference |p0-2p1+p2|^2. For quadratics whose first control leg is much longer than the second this underestimates curvature, and the 'fast' route (maxCurve\*det &lt; 4 for large fills, &lt; 16 for molecules) then draws large-fill quadratics as straight chords (CurveIndexer::Quadratic writes only x0,y0 to x2,y2), which can exceed the intended sub-pixel error at small zoom scales. Cubics are computed correctly.
- Path building drops near-flat curves in user space: quadTo and cubicTo turn a curve into a line when its control points sit within 1% of the chord length from the chord (err = 1e-2), so very long, shallow arcs can lose up to about 0.5% of chord length of sag, which becomes visible when zoomed far in.
- No guard on scene size: the per-frame path index lives in the low 20 bits of each instance word (kPathIndexMask 0xFFFFF, flags in bits 21-31) and neither Scene::addPath nor RasterizerRenderer::renderList checks the total, so keep a frame under about 1.05 million paths.
- Frames are rebuilt from scratch every frame (CPU transform, clip and memcpy of all visible geometry), and RasterizerLayer::display skips a frame when both in-flight buffers are busy rather than blocking.

## Known shortcomings

- The only number is the README's 'up to 60x faster than the CPU' with no named baseline, scene, hardware or benchmark code (tier D); TestFiles/ holds SVG and PDF scenes only, and the HN thread (45090553) is snippet-only (50,000 glyphs at 60 fps, Vello 'very competitive', no numbers). Custom personal-use zlib-style licence, not OSI approved, so usability reference.
- Enricher (e115, 2026-10-05): tier D stands, the 60x has no harness. The only CPU path in the repo is the demo's '0' toggle to single-threaded Core Graphics (RaCG::renderListToBitmap) and there is no frame timer ('T' is an animated clock). Quality bug, not behind any number: Rasterizer.hpp lines 304-305, Geometry::quadTo sets x0 = x2 before computing curvature, so maxCurve stores 4|p2-p1|^2 instead of |p0-2p1+p2|^2 and asymmetric quadratics can take the chord-only fast path at small scales. Personal-use licence; Arabic text broken (open issue #1); no guard on the 20-bit path index (about 1.05M paths per frame).

## Caveats and trade-offs

The only number is the unqualified 'up to 60x faster than the CPU'. It names no baseline library, scene, hardware or flags, and the repo has no benchmark code or results: TestFiles/ is SVG/PDF scenes only and the issues have no performance data. The HN thread 'Rasterizer: A GPU-accelerated 2D vector graphics engine in \~4k LOC' (item 45090553) was seen only as search snippets. They say 50,000 glyphs at 60fps (no hardware and no baseline), CoreGraphics as the quality reference, and Vello 'very competitive', with Rasterizer 'suspected' faster on complex scenes. None of these has a number against a named baseline. The licence is zlib-style but limited to personal use (commercial licence from the author), so it is not OSI-approved. It is macOS/Metal only (an iOS target was added in 2026), and the Xcode demo depends on bundled PDFium, NanoSVG, stb_truetype and xxHash. The \~4k LOC figure comes from the HN title and was not checked in the repo.

Targets macOS with C++11 and Metal only (iOS port in progress; README says it would work on any GPU with instancing and float render targets). Single font in the demo app. Custom 'personal use zlib license': personal use only, commercial use needs a licence from the author. Uses novel windowed-inverse-lerp area coverage and GPU quadratic Bezier solving.

## Maintenance

Active (last commit 2026-05-02, iOS target and Swift API added in 2026, 7,346 commits, single maintainer) but licensed for personal use only, so it is a reference design for commercial projects unless the author grants a licence.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now D.
- **Tier reason:** The README's only number is 'up to 60x faster than the CPU', and it names no CPU renderer, scene, hardware or method. The repo has no benchmark code or result files: TestFiles/ holds only SVG and PDF test scenes, and the 4 issues hold no performance data. With no named baseline and no measurement behind the claim, it is directional only, so D.
- **Verifier notes:** Downgraded from C to D: the 60x claim has no named baseline and no benchmark code anywhere in the repo. Kept as a reference entry under rasterizers-2d (346 stars, 8 forks, not archived, not a fork, 7,346 commits, last commit 2026-05-02, active). The HN thread was not opened because news.ycombinator.com is blocked; its claims come from WebSearch snippets only.
- **Fields the verifier corrected:** `baseline`, `compared_against_cpp_std_directly`, `license`, `caveats`
- **Shortcomings recorded by:** none
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/README.md>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/LICENSE.txt>
  - <https://github.com/mindbrix/Rasterizer>
  - <https://github.com/mindbrix/Rasterizer/commits>
  - <https://github.com/mindbrix/Rasterizer/tree/master/TestFiles>
  - <https://github.com/mindbrix/Rasterizer/issues?q=is%3Aissue>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/README.md>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/LICENSE.txt>
  - <https://github.com/mindbrix/Rasterizer>
  - <https://github.com/mindbrix/Rasterizer/commits>
  - <https://github.com/mindbrix/Rasterizer/tree/master/Rasterizer>
  - <https://github.com/mindbrix/Rasterizer/tree/master/Package>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Package.swift>
  - <https://github.com/mindbrix/Rasterizer/tree/master/Package/Sources/RasterizerCpp/include>
  - <https://github.com/mindbrix/Rasterizer/tree/master/Package/Sources/RasterizerObjC>
  - <https://github.com/mindbrix/Rasterizer/tree/master/Package/Sources/RasterizerObjC/private>
  - <https://github.com/mindbrix/Rasterizer/tree/master/Package/Sources/RasterizerObjC/include>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerCpp/include/Rasterizer.h>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerCpp/include/Rasterizer.hpp>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerCpp/include/RasterizerRenderer.hpp>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerCpp/include/RasterizerWinding.hpp>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerCpp/include/Shaders.metal>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerCpp/include/RasterizerCG.hpp>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerCpp/include/RasterizerSVG.hpp>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerCpp/include/RasterizerCoreText.hpp>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerObjC/RasterizerAPI.mm>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerObjC/RasterizerLayer.mm>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerObjC/RasterizerView.mm>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerObjC/include/RasterizerAPI.h>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Package/Sources/RasterizerObjC/include/RasterizerView.h>
  - <https://github.com/mindbrix/Rasterizer/tree/master/Rasterizer/Demo>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Rasterizer/Demo/DemoView.mm>
  - <https://raw.githubusercontent.com/mindbrix/Rasterizer/HEAD/Rasterizer/Demo/RasterizerDemo.hpp>
  - <https://github.com/mindbrix/Rasterizer/issues?q=is%3Aissue>
  - <https://github.com/mindbrix/Rasterizer/issues/1>
  - <https://github.com/mindbrix/Rasterizer/issues/5>
  - <https://github.com/mindbrix/Rasterizer/pulls?q=is%3Apr>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/mindbrix/rasterizer`) · [data/wave10/enrich/raw/github_com_mindbrix_rasterizer.json](../../../data/wave10/enrich/raw/github_com_mindbrix_rasterizer.json) (enrichment confidence 0.7)

</details>
