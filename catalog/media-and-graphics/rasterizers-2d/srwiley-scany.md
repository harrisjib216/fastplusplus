# scany (multi-threaded scanner, srwiley)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Pure-Go CL-AA antialiasing scanner for rasterx/oksvg; single-thread parity with ScanFT claimed, multi-thread speedup claimed, nothing measured.

| | |
|---|---|
| **Beats** | srwiley/scanFT ScanFT (Go port of the FreeType/golang freetype CL-AA gray antialiaser, same algorithm as FreeType ftgrays) |
| **Claimed result** | No numbers. README: 'ScanS appears to be within 1 or 2 percent as fast as ScanFT'; 'If ScanT is run using a thread count of one it is around 10% slower than ScanFT or ScanS. However, as additional threads are added it will exceed the speed of the single thread implementations'; SVGs with gradients 'particularly benefit from using multiple threads'. |
| **Workload** | Rendering SVG icons through oksvg and rasterx with ScanS (single thread) or ScanT (multi-thread) as the rasterx.Scanner; the repo's Go benchmarks (scant_test.go, scans_test.go) render a set of landscape icons and a gradient-heavy TestShapes6.svg (50 draws per run) at 1x and 5x scale with 1 to 32 threads. |
| **Metric** | throughput |
| **Adoption** | 1 star, 0 forks |
| **Last commit** | 2022-01-17 |
| **Links** | [repository](https://github.com/srwiley/scany) · [benchmark](https://github.com/srwiley/scany) |

## Verdict

Nothing was measured: the README says single-threaded ScanS is within 1-2 percent of ScanFT (parity, not a win), one-thread ScanT about 10 percent slower, and multi-thread ScanT faster at an unstated, image-dependent thread count, with no hardware, Go version or figures. The repository's Go benchmarks only vary ScanT's thread count (1 to 32) and run ScanS on the gradient file, all on square inputs, and never time ScanFT or x/image/vector.

## Use it when

- Go code already rendering SVG through oksvg/rasterx that needs an MIT-licensed scanner instead of ScanFT's FreeType/GPL-licensed port, and only renders square canvases with all geometry on-canvas (see gotchas).
- Gradient-heavy SVGs at large output sizes on multi-core machines, where ScannerT spreads per-pixel ColorFunc evaluation across rows; benchmark it yourself first, because no numbers are published.
- Studying or teaching the CL-AA algorithm: about 1,100 lines of plain Go in three files (scans.go, scant.go, sweep.go), no assembly and no unsafe.

## Skip it when

- Non-square output: SetBounds is declared (height, width) but rasterx calls Scanner.SetBounds(width, height), so the scanner's row and column limits are swapped (code reading this session).
- SVGs that rely on fill-rule="evenodd", clip rectangles, or subpaths of opposite orientation sharing a scanline: SetWinding and SetClip are no-ops and the coverage sign is fixed once per scanline.
- ScanT with 2 or more threads on content that reaches above the top edge (partly off-canvas art, zoom/pan, strokes straddling y = 0): a negative slice index panics in a worker goroutine.
- When you need a demonstrated speedup: neither ScanFT nor the golang.org/x/image/vector scanner is ever timed, while the same author's scanx publishes numbers against both.
- Long-lived services: unmaintained since 2022-01-17, 1 star, and the tests make no assertions on output.

## How it is fast

Both scanners use the CL-AA signed cover/area accumulation from cl-vectors (the same idea as FreeType ftgrays and AGG): each line is walked cell by cell in 26.6 fixed point, integer cover and area are added to a per-scanline linked list of cells kept sorted by x inside one flat slice with per-row sentinels, and each row is then swept left to right to emit alpha runs. ScannerT splits the work into three goroutine stages (line-to-cells, cell storage, sweep) with N goroutines of each; scanlines are assigned round-robin (row y goes to worker y mod N) so each worker owns its rows' lists without locks, while every single cell travels over a channel with a WaitGroup Add/Done. That per-cell channel traffic is why one-thread ScanT is about 10 percent slower per the README; the parallel sweep pays off mainly when the per-pixel rasterx.ColorFunc of a gradient dominates, because different rows are swept concurrently.

## Compared with alternatives

Among the Go siblings, scanx (same author, same rasterx interface) publishes 3.2x over ScanFT's FTScanner and 74x over the x/image/vector GVScanner at 5x scale, and stilus publishes about 2x over x/image/vector, while scany publishes no numbers and has the defects above; pick scany only if you specifically need an MIT-licensed CL-AA scanner with row-parallel gradient sweeping on square, on-canvas, nonzero-winding SVGs, and measure it first.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/image/math/fixed and github.com/srwiley/rasterx in the library code; github.com/srwiley/oksvg in tests and the README usage; go.mod pins 2021 pseudo-versions (rasterx v0.0.0-20210519020934-456a8d69b780, oksvg v0.0.0-20211120171407-1837d6608d8c) |
| **Minimum toolchain** | Go 1.17 (go.mod 'go 1.17') |
| **Platforms** | any Go target (pure Go, no assembly, no unsafe) |
| **Thread safety** | Not documented. A ScannerS or ScannerT instance holds shared mutable state and must be driven from one goroutine. ScannerT starts 3 x N internal goroutines at NewScanT that run until Close(); with a ColorFunc, RGBACollector calls it concurrently from the N sweep goroutines, so the ColorFunc must tolerate concurrent calls. |
| **Drop-in for the baseline** | partial: same rasterx.Scanner interface as ScanFT, so it plugs into rasterx.NewDasher/NewFiller unchanged, but output goes through scany.Collector instead of ScanFT's Painter (only RGBA provided), even-odd winding and SetClip are unimplemented, SetBounds swaps width and height, and ScanT needs Close(). |

## Gotchas

- Swapped bounds (code reading, not executed): ScannerS.SetBounds and ScannerT.SetBounds take (height, width), but the rasterx Scanner interface is SetBounds(w, h) and Filler.SetBounds, which NewDasher, NewStroker and NewFiller call (also at the 2021-05-19 rasterx commit pinned in go.mod), passes (width, height). Following the README (NewScanS(width, height, ...) then rasterx.NewDasher(w, h, scanner)) leaves the scanner with height = image width and width = image height: on a landscape canvas every cell right of column height-1 is pinned to that column so the right side is never painted, on a portrait canvas rows at or below y = width are dropped, and off-canvas geometry can index past the RGBA buffer. Every SVG in testdata is square (TestShapes6 500x500, icons 512x512), so the tests and benchmarks never exercise this.
- Multi-thread crash (code reading, not executed): ScannerT routes each cell with s.cellWorkers[cy%s.threads]; Go's % keeps the sign, so with 2 or more threads any segment whose cell row lies above the image (cy &lt; 0 and not a multiple of the thread count) indexes a negative slot and panics inside a goroutine, killing the process. rasterx forwards lines unclipped (Filler.lineF calls Scanner.Line directly). ScannerS and one-thread ScanT drop such rows safely in saveCell/cellSaver.
- Not output-equivalent to ScanFT: SetWinding and SetClip are empty ('does nothing for now'), so evenodd fills render as nonzero and clip rectangles are ignored, both of which ScanFT implements. Coverage sign is taken from the first non-zero cell of each scanline rather than per cell (ScanFT's areaToAlpha takes the absolute value per cell); when a later subpath on the same row winds the other way its negative int16 alpha wraps to a huge uint32 in RGBACollector and is clamped to full opacity, so those edges lose antialiasing. The README's 'within 1 or 2 percent' therefore compares scanners that do not do the same work on every input.
- Benchmark and test harness: no ScanFT or x/image/vector benchmark exists (ScanFT appears only in commented-out lines), there is no ScanS benchmark on the icon set, RunGradsT/RunGradsS draw a fixed 50 times and ignore b.N (ns/op is only meaningful if one 50-draw call exceeds -benchtime), TestCompHalfCirc only prints ScanT/ScanS green-channel mismatches without failing, and tests write PNGs into testdata/. The sweep also calls the Collector for zero-coverage gaps between cells, so gradient ColorFuncs are evaluated for pixels that receive no paint.

## Known shortcomings

- Prose claim only (ScanS at parity with ScanFT, ScanT faster with more threads): no numbers, ScanFT never timed, the gradient benchmarks ignore b.N; 1 star, abandoned since 2022-01-17. Kept at D under the keep-and-document rule.
- Enricher (code reading): scany's SetBounds takes (height, width) while rasterx Filler/NewDasher call SetBounds(width, height), so non-square canvases break (landscape never paints right of column H-1, portrait drops rows from y=W) and every testdata SVG is square so tests never hit it; ScanT panics at 2 or more threads when content reaches above the top edge (negative cellWorkers index, rasterx passes lines unclipped); SetWinding and SetClip do nothing (no even-odd fill, no clipping, unlike ScanFT) and the sign is set once per scanline so counter-wound subpaths lose antialiasing, meaning the '1-2% of ScanFT' prose compares unequal work. No ScanFT or x/image/vector benchmark, no ScanS icon benchmark, grads benches ignore b.N, TestCompHalfCirc never fails.

## Caveats and trade-offs

No measured results anywhere in the repo or README, so the speedup is a prose claim (tier D). The benchmarks in scant_test.go and scans_test.go only vary ScanT's thread count and ScanS; ScanFT appears only in commented-out test code and x/image/vector is absent, so none of the named baselines is timed. The gradient benchmarks (RunGradsT, RunGradsS) draw a fixed 50 times and ignore b.N, so the ns/op that go test would print for them is not a valid per-iteration time. The README's own claim for single-threaded ScanS is parity (within 1-2 percent of ScanFT), not a win; ScanT with one thread is said to be about 10 percent slower, and only ScanT at several threads is said to be faster, with no hardware, Go version or crossover thread count. The lead's other baselines (golang.org/x/image/vector, scanx, FreeType ftgrays itself) are not compared; ScanFT is the nearest relative of ftgrays. Repository has 1 star, 0 forks, 11 commits, last commit 2022-01-17, 'go 1.17' module, so it is old and unmaintained. Not notable on its own; kept at tier D under the keep-and-document rule. [retier] Prose claim only (ScanS at parity with ScanFT, ScanT faster with more threads), no numbers, ScanFT never timed. Code bugs: SetBounds(height, width) argument order swapped against rasterx callers, so non-square canvases paint wrong (all test SVGs are square); ScanT indexes cellWorkers with a negative value and panics when content reaches above the top edge with 2 or more threads; SetWinding and SetClip are no-ops, so no even-odd fill or clipping and counter-wound subpaths lose antialiasing. 1 star, abandoned since 2022-01-17; separate repo from the catalogued srwiley/scanx.

ScanT starts three kinds of worker thread (cell splitting, cover and area, sweep) and a thread count of N starts N of each, all of which must be shut down with Close(); needs rasterx and oksvg; output via a Collector interface, only an image.RGBA collector is provided. Licensed MIT, while ScanFT is under the FreeType licence because it is a direct port of the C code.

## Maintenance

Abandoned (11 commits from 2021-12-12 to 2022-01-17, 1 star, 0 forks, no issues) but MIT-licensed and small enough to vendor; the swapped SetBounds arguments, the multi-thread negative-row panic and the missing even-odd/clip support found by code reading this session make it unsafe beyond square, fully on-canvas, nonzero-winding SVGs without patches.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** README makes only prose claims relative to ScanFT (single-thread parity within 1-2 percent, ScanT faster with more threads); no measured numbers are published anywhere in the repo, so D.
- **Verifier notes:** Record is accurate: prose-only parity/multi-thread claim vs ScanFT, no numbers, MIT, 1 star, last commit 2022-01-17 (abandoned). Shortcomings to record: no measurements, baselines never timed in the benchmark files, gradient benchmarks ignore b.N, single-thread result is parity not a win, not notable. Distinct from the listed srwiley/scanx (different repo), not a duplicate.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** any timed comparison against x/image/vector or scanx; like-for-like benchmark against ScanFT with clipping and winding implemented
- **Pages the verifier opened:**
  - <https://github.com/srwiley/scany>
  - <https://github.com/srwiley/scany/commits>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/README.md>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/scant_test.go>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/scans_test.go>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/srwiley/scany>
  - <https://github.com/srwiley/scany/commits>
  - <https://github.com/srwiley/scany/issues>
  - <https://github.com/srwiley/scany/tree/master/testdata/svg/landscapeIcons>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/README.md>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/go.mod>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/go.sum>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/scans.go>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/scant.go>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/sweep.go>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/scant_test.go>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/scans_test.go>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/testdata/svg/TestShapes6.svg>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/testdata/svg/halfCirc.svg>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/testdata/svg/landscapeIcons/sea.svg>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/testdata/svg/landscapeIcons/beach.svg>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/testdata/svg/landscapeIcons/village.svg>
  - <https://raw.githubusercontent.com/srwiley/scany/HEAD/testdata/svg/landscapeIcons/mountains.svg>
  - <https://raw.githubusercontent.com/srwiley/rasterx/HEAD/fill.go>
  - <https://raw.githubusercontent.com/srwiley/rasterx/HEAD/dash.go>
  - <https://raw.githubusercontent.com/srwiley/rasterx/HEAD/stroke.go>
  - <https://raw.githubusercontent.com/srwiley/rasterx/456a8d69b780/fill.go>
  - <https://raw.githubusercontent.com/srwiley/rasterx/456a8d69b780/scan.go>
  - <https://github.com/srwiley/scanFT>
  - <https://raw.githubusercontent.com/srwiley/scanFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/srwiley/scanFT/HEAD/scan.go>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/srwiley/scany`) · [data/wave10/enrich/raw/github_com_srwiley_scany.json](../../../data/wave10/enrich/raw/github_com_srwiley_scany.json) (enrichment confidence 0.75)

</details>
