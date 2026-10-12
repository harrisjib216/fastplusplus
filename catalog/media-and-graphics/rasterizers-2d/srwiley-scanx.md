# scanx

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Go` · `FTL OR GPL-2.0-or-later on scan.go only (header inherited from freetype-go, which points to a LICENSE file the repo does not have); span.go and the repo carry no license` · 🔴 abandoned

> Pure-Go anti-aliasing scanner for rasterx/oksvg that writes spans straight into image.RGBA; 1.7-3.2x faster than scanFT on the author's icon benchmark.

| | |
|---|---|
| **Beats** | golang.org/x/image/vector rasterizer via rasterx scanGV (GVScanner) and rasterx-family scanFT (FTScanner) |
| **Claimed result** | 5x: ImgSpanner 513,577,800 ns/op vs FTScanner 1,644,670,841 ns/op (3.2x, derived from page data) vs GVScanner 38,052,841,313 ns/op (74x, derived from page data); LinkListSpanner 227,859,937 ns/op (7.2x vs FTScanner, derived from page data). 1x: ImgSpanner 35,224,671 vs FTScanner 75,619,298 vs GVScanner 1,431,206,955. 0.5x: 14,352,161 vs 24,019,383 vs 362,814,157. 15x: ImgSpanner 4,173,881,468 vs FTScanner 10,811,718,931 vs GVScanner 250,690,083,743; LinkListSpanner 1,344,679,006. |
| **Workload** | Draw the whole SVG icon set in testdata/svg/landscapeIcons (parsed by oksvg, stroked by the rasterx Dasher) into an image.RGBA at 0.5x, 1x, 5x and 15x native resolution; ns/op per pass over the set (scanx_benchmark_test.go). |
| **Metric** | latency |
| **Hardware** | linux/amd64, 16 logical CPUs; CPU model not stated |
| **Compiler and flags** | Go version and flags not stated; README prints goos linux, goarch amd64 and the -16 benchmark suffix (GOMAXPROCS 16); go test -bench |
| **Adoption** | 2 stars, 0 forks; default rasteriser of tdewolff/canvas (go.mod pins github.com/srwiley/scanx v0.0.0-20190309010443-e94503791388; renderers/rasterizer/rasterizer.go builds on scanx.NewImgSpanner and scanx.NewScanner) |
| **Last commit** | 2019-03-09 |
| **Links** | [repository](https://github.com/srwiley/scanx) · [benchmark](https://github.com/srwiley/scanx) |

## Verdict

The README's go test -bench results (linux/amd64, GOMAXPROCS 16, CPU and Go version not stated) draw the 8 landscape icons (beach, cape, iceberg, island, mountains, sea, trees, village) through oksvg and the rasterx Dasher into one image.RGBA at 0.5x to 15x. ImgSpanner beats scanFT by 1.67x at 0.5x, 2.15x at 1x, 3.20x at 5x and 2.59x at 15x (derived from page data), and LinkListSpanner by 7.2x at 5x and 8.0x at 15x; most 5x and 15x rows ran only once. Reading the code adds two points. The scanFT comparison is like-for-like: same coverage algorithm and harness, different span writer. The x/image/vector column is not representative: rasterx's ScannerGV.Draw calls vector.Rasterizer.Draw over the whole destination bounds for every path, and Clear calls Reset(w, h) on the full-canvas accumulator, so each path costs time in proportion to image area (not profiled here). The 15x to 74x gap therefore measures that adapter, not x/image/vector used with a path-sized rasterizer.

## Use it when

- Go programs that already render SVG icons with oksvg and rasterx into image.RGBA and want about 2-3x over ScannerFT without cgo.
- Large or hi-DPI renders of solid-colour, heavily overlapping icon art: LinkListSpanner was 7-8x faster than scanFT at 5x and 15x scale in the README, but it was slower than ImgSpanner at 0.5x.
- X11 tools built on xgbutil that draw into \*xgraphics.Image (BGRA): ImgSpanner swaps the R and B channels itself.
- As the rasteriser behind tdewolff/canvas, which pins this module at a 2019 commit (per the record's verification).

## Skip it when

- Anything that needs a clean licence: span.go and the repository have no licence, and scan.go carries the freetype-go FreeType License or GPL-2.0+ header.
- Gradients with LinkListSpanner: SetColor runs every input through getColorRGBA, which returns zero (transparent) for a rasterx.ColorFunc, so gradient fills silently disappear rather than failing.
- Destinations other than \*image.RGBA or \*xgraphics.Image with ImgSpanner. SetImage ignores other types and leaves pix nil, so the first span panics with an index error, despite the README saying it 'draw[s] into any image that supports the draw.Image interface'.
- Generic draw.Image targets with LinkListSpanner: spansToImage calls img.Set(y, x, clr) with the arguments swapped, so output is transposed, and on non-square images pixels land in the wrong place or are dropped. The same line is still in Cogent Core's copy.
- Production use where unexpected output is costly: the README calls it 'beta software' with 'known bugs', advises scanFT or ScannerGV unless every SVG is tested, and notes that line-heavy files such as rl.svg are slow with LinkListSpanner.

## How it is fast

Coverage uses the same FreeType / CL-AA area-and-cover cell accumulation as scanFT (scan.go is the freetype-go algorithm on 26.6 fixed point). The gain is in the span writer. GetSpanFunc picks one of four specialised functions per path (solid colour or colour function, Over or Src), and each writes directly into Pix, hoists the blend factor out of the pixel loop, and handles fully covered opaque spans as plain stores. scanFT instead buffers 64 Spans, calls Painter.Paint through an interface, and recomputes the blend factor for every pixel. LinkListSpanner resolves overdraw in the per-row span lists, merging neighbouring spans of the same colour, so each pixel is written once at the end. That is why it pulls ahead at 5x and 15x, where overlapping paths cover many pixels.

## Compared with alternatives

Pick scanx (or the copy inside tdewolff/canvas or Cogent Core) when you are already on oksvg and rasterx in pure Go and want 2-3x over scanFT. Pick stilus for a standalone, licensed replacement for x/image/vector. Pick Blend2D or another C/C++ renderer when cgo is acceptable and raw speed matters more than staying pure Go.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/srwiley/rasterx, golang.org/x/image/math/fixed, github.com/BurntSushi/xgbutil/xgraphics (always imported by span.go); the tests also use github.com/srwiley/oksvg and github.com/srwiley/scanFT |
| **Minimum toolchain** | not documented; the repository predates Go modules (no go.mod), so consumers pin a pseudo-version |
| **Platforms** | any Go target (pure Go, no assembly) |
| **Thread safety** | not documented; Scanner, ImgSpanner and LinkListSpanner all keep mutable per-render state (cell lists, span lists, lastY/lastP), so use one set per goroutine |
| **Drop-in for the baseline** | partial: it implements rasterx's Scanner interface, so it swaps in for ScannerFT or ScannerGV inside a rasterx Dasher, but it is not a replacement for the golang.org/x/image/vector Rasterizer API |

## Gotchas

- LinkListSpanner blends new spans against its BgColor (default transparent), not against the pixels already in the image, and DrawToImage overwrites every covered pixel. You cannot layer it over existing content, you must call Clear() between images, and it allocated 93 MB per op at 15x in the README.
- Open issue #1 (rcoreilly, 2021-03-03) reports an infinite loop in Scanner.Line when dx and dy are both zero and proposes an early return. HEAD has no such guard. Reading the code, a zero-length segment takes the single-scanline branch, so the loop could not be confirmed from source alone. Line walks every row and cell of a segment, including parts off the canvas, so huge coordinates cost time in proportion to their extent.
- Output is not bit-identical to scanFT: the README reports differences of up to 4 in a channel on randspot.svg, and more with several stacked semi-transparent layers.
- A maintained copy lives in Cogent Core (cogentcore.org/core/paint/renderers/rasterx/scan). It drops the xgbutil dependency and adds a BSD header to span.go, but scan.go keeps the FreeType/GPL notice, and the transposed img.Set call is unchanged.

## Known shortcomings

- README ns/op figures match scanx_benchmark_test.go but no CPU or Go version is stated; usability is mixed because scan.go keeps the freetype-go header (FTL or GPL-2.0+) while span.go and the repo carry no licence; the README calls it beta software with known bugs; last commit 2019.
- Enricher (e121, 2026-10-05): ImgSpanner vs scanFT is like for like (same freetype coverage algorithm, faster span writer). The GV column measures rasterx ScannerGV, which runs vector.Rasterizer.Draw over the whole destination bounds per path and Reset(w, h) per Clear, so the 15x-74x gap is not representative of x/image/vector; caveat level, C unchanged. Bugs: LinkListSpanner.spansToImage calls img.Set(y, x) with swapped arguments (transposed output on a generic draw.Image; still present in the Cogent Core copy); ImgSpanner panics on non-RGBA or xgraphics targets (nil pix) despite the README; LinkListSpanner turns gradients transparent; open issue #1 claims an infinite loop, with no guard at HEAD. cogentcore.org/core/paint/renderers/rasterx/scan is a maintained copy (duplicate).

## Caveats and trade-offs

Baselines are Go scanners: scanFT (the author's own port of the freetype-go antialiaser) and x/image/vector through rasterx ScannerGV. There is no Skia, Cairo or Blend2D comparison and no cross-language comparison. scanx's scan.go is the same freetype-go area/coverage antialiaser adapted to a Spanner interface, so the gain over scanFT comes from the span write path (span.go), not from a new rasterisation algorithm. The CPU model and Go version are missing. At 5x and 15x most rows ran b.N of 1 to 5 times (single-shot). Times include oksvg path traversal and Dasher stroking, and LinkListSpanner timings include DrawToImage. Per the rasterx README, ScannerGV draws through x/image/vector Draw with the path as an alpha mask and 'can be faster for smaller and more complex images'. The harness gives it the full image bounds, which probably explains the 74x gap (not profiled), so the GV figure does not represent x/image/vector on small paths. The README warns 'Scanx is beta software. There are known bugs being worked on. Please use scanFT or scanGV unless you want to test each svg file', and it reports pixel differences from scanFT of up to 4 per pixel (randspot.svg). LinkListSpanner does not support gradients and is slow on line-heavy files (rl.svg). Licence: there is no LICENSE or COPYING file (raw LICENSE, LICENSE.md, LICENSE.txt and COPYING all return 404; the GitHub page shows no license). scan.go carries the freetype-go header (FreeType License or GPL-2.0-or-later); span.go, which holds ImgSpanner and LinkListSpanner, has no license header, so only scan.go is clearly reusable. The last commit is 2019-03-09.

README labels it beta with known bugs and recommends scanFT or scanGV unless each SVG is tested. LinkListSpanner has no gradients and can be slow on files with many random lines (rl.svg). Output differs from scanFT by up to 4 in a channel on randspot.svg. Meant for use with rasterx and image.RGBA or xgraphics.Image targets. Go only.

## Maintenance

Abandoned since 2019-03-09 (2 stars, one open issue from 2021) and effectively unlicensed for its fast part (span.go). Its live users are vendored or pinned copies (tdewolff/canvas, Cogent Core); the same author's later srwiley/scany (MIT, adds a multi-threaded ScanT) is the cleaner-licensed successor to evaluate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** These are first-party go test -bench results in the README, produced by the public scanx_benchmark_test.go, which runs ImgSpanner and LinkListSpanner against scanFT and x/image/vector (via rasterx ScannerGV) on the same icon set. Every quoted ns/op figure matches the README. The CPU model, Go version and flags are not given, so the evidence is C.
- **Verifier notes:** C confirmed and all numbers match the README. Usability corrected from reference to mixed: scan.go keeps the freetype-go FTL/GPL-2.0+ header, while span.go (the fast part) and the repo have no license. The beta and known-bugs warning was added to caveats.
- **Fields the verifier corrected:** `license`, `usability`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** first-party go test -bench
- **Pages the verifier opened:**
  - <https://github.com/srwiley/scanx>
  - <https://github.com/srwiley/scanx/commits/master>
  - <https://raw.githubusercontent.com/srwiley/scanx/HEAD/README.md>
  - <https://raw.githubusercontent.com/srwiley/scanx/HEAD/scanx_benchmark_test.go>
  - <https://raw.githubusercontent.com/srwiley/scanx/master/scan.go>
  - <https://raw.githubusercontent.com/srwiley/scanx/master/span.go>
  - <https://raw.githubusercontent.com/srwiley/scanx/master/LICENSE>
  - <https://raw.githubusercontent.com/srwiley/rasterx/master/README.md>
  - <https://raw.githubusercontent.com/tdewolff/canvas/master/go.mod>
  - <https://raw.githubusercontent.com/tdewolff/canvas/master/renderers/rasterizer/rasterizer.go>
- **Sources the enricher read:**
  - <https://github.com/srwiley/scanx/tree/master/testdata/svg/landscapeIcons>
  - <https://github.com/srwiley/scanx/issues?q=is%3Aissue>
  - <https://github.com/srwiley/scanx/issues/1>
  - <https://raw.githubusercontent.com/srwiley/scanx/HEAD/README.md>
  - <https://raw.githubusercontent.com/srwiley/scanx/HEAD/scan.go>
  - <https://raw.githubusercontent.com/srwiley/scanx/HEAD/span.go>
  - <https://raw.githubusercontent.com/srwiley/scanx/HEAD/scanx_benchmark_test.go>
  - <https://raw.githubusercontent.com/srwiley/scanx/HEAD/go.mod>
  - <https://raw.githubusercontent.com/srwiley/scanx/HEAD/LICENSE>
  - <https://github.com/srwiley/rasterx>
  - <https://raw.githubusercontent.com/srwiley/rasterx/HEAD/README.md>
  - <https://raw.githubusercontent.com/srwiley/rasterx/HEAD/scan.go>
  - <https://raw.githubusercontent.com/srwiley/rasterx/HEAD/fill.go>
  - <https://github.com/srwiley/scanFT>
  - <https://raw.githubusercontent.com/srwiley/scanFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/srwiley/scanFT/HEAD/painter.go>
  - <https://raw.githubusercontent.com/srwiley/scanFT/HEAD/scan.go>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/README.md>
  - <https://raw.githubusercontent.com/cogentcore/core/HEAD/paint/renderers/rasterx/scan/README.md>
  - <https://raw.githubusercontent.com/cogentcore/core/HEAD/paint/renderers/rasterx/scan/scan.go>
  - <https://raw.githubusercontent.com/cogentcore/core/HEAD/paint/renderers/rasterx/scan/span.go>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/srwiley/scanx`) · [data/wave10/enrich/raw/github_com_srwiley_scanx.json](../../../data/wave10/enrich/raw/github_com_srwiley_scanx.json) (enrichment confidence 0.75)

</details>
