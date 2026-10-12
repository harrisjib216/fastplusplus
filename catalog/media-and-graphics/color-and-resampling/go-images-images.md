# go-images/images (RGB to HSV and box-blur kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `BSD-3-Clause` · 🟢 active

> Pure-Go (CGO=0) scikit-image-style image library; first-party table shows RGB to HSV and box blur 2-5x faster than float64 scikit-image, far slower than OpenCV.

| | |
|---|---|
| **Beats** | scikit-image 0.26.0 (rgb2hsv, scipy.ndimage.uniform_filter); OpenCV 4.13.0 also measured and is faster |
| **Claimed result** | Single thread, Apple M4 Max: RGB to HSV go-images 65.6 vs scikit-image 13.7 Mpix/s at 512x512 (4.81x), 4.71x at 1024x1024, 4.76x at 4096x4096. Box blur r=2 RGB: 2.64x, 1.78x, 2.29x. Flip horizontal 2.01x to 2.28x. Gaussian sigma 2: 1.02x, 1.26x, 1.30x. OpenCV, the uint8-to-uint8 reference in the same table, is far faster: RGB to HSV 1,554 Mpix/s at 512x512 (about 24x go-images, derived from page data) and box blur r=2 2,322 Mpix/s (about 15x go-images at 512x512, about 30x at 4096x4096, derived from page data). |
| **Workload** | Single-thread parity benchmark at 512x512, 1024x1024 and 4096x4096: RGB to HSV conversion, box blur r=2 on RGB, Gaussian sigma 2, flips and morphology, in Mpix/s. |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max (16 cores), macOS 26.5 arm64 |
| **Compiler and flags** | go1.26.4, 'go test -bench -benchmem -cpu=1 -count=5' (GOMAXPROCS=1); Python 3.14.5, scikit-image 0.26.0, scipy 1.18.0, numpy 2.5.0, OpenCV 4.13.0 pinned to one thread; harness in benchmarks/ |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/go-images/images) · [benchmark](https://raw.githubusercontent.com/go-images/images/HEAD/BENCHMARKS.md) |

## Verdict

Author-run parity table on an Apple M4 Max (macOS 26.5), go1.26.4 with go test -cpu=1 -count=5 against scikit-image 0.26.0/scipy 1.18.0 and OpenCV 4.13.0 pinned to one thread: RGB to HSV 65 vs 13.7 Mpix/s (4.7-4.8x) and box blur r=2 1.8-2.6x over scikit-image, but the scikit-image side runs float64 in and float64 out while go-images and OpenCV run uint8, and OpenCV is 15-30x faster than go-images on those same rows. The code review adds measurement caveats in both directions: morphology rows, labelled '(gray)' by aggregate.py, time go-images on three RGB channels of a random colour image against scikit-image and OpenCV on one uint8 gray plane (so its losses there are overstated), Gaussian is 3-sigma vs 4-sigma, and the HSV numbers (BENCHMARKS.md last edited 2026-07-02) predate the 2026-08-15 move of the HSV kernel onto go-gfx/color, which was not re-timed in the published table.

## Use it when

- Go services or CLIs that must build with CGO_ENABLED=0 (static binaries, cross-compiling to arm64, s390x, riscv64, loong64 or ppc64le) and need blur, edge, morphology or HSV ops without libvips, ImageMagick or OpenCV.
- Batch filtering of large images (1024x1024 and up) on many-core machines, where the goroutine tiling gave 4.2-10.3x over single-threaded scikit-image in the author's 16-core table for box blur, Gaussian, Sobel and morphology.
- Porting a scikit-image pipeline to Go when matching its semantics matters: box blur, morphology, Otsu and Rotate/Warp are written and tested against scipy/skimage references.
- Byte-quantized HSV for thresholding or colour keying inside an RGBA pipeline, where 1.4-degree hue steps are acceptable.

## Skip it when

- Raw throughput: in the same single-thread table OpenCV (uint8 in, uint8 out) is about 24x faster on RGB to HSV, 15-30x on box blur, 6-8x on Gaussian and 7-8x on Sobel (derived from page data). If cgo is acceptable, OpenCV (or libvips) wins every row.
- Small-radius morphology, Rotate90, Crop or Otsu on one thread, where the table shows go-images at 0.24-0.93x of scikit-image.
- Memory-constrained 4096x4096 work: every call allocates a new RGBA output, BoxBlur allocates a width\*height\*3 float64 plane (about 400 MB at 4096x4096) and GaussianBlur six width\*height float64 planes (about 800 MB), derived from the code.
- Code that needs float or 16-bit images, or HSV in OpenCV's 0-180 or skimage's float convention: everything is 8-bit RGBA and RGBToHSV packs hue into 0-255.
- Resizing benchmarks or resize-heavy workloads chosen on these numbers: the parity table has no resize rows and Resize lives in go-gfx/gfx.

## How it is fast

The wins come from algorithm and data layout, not vector code: RGBToHSV is one fused scalar per-pixel pass (via go-gfx/gfx/color.SRGBToHSV) instead of scikit-image's chain of float64 numpy temporaries, and BoxBlur is a separable running-window sum (O(1) per pixel in the radius) with a float64 intermediate plane. The only go-asmgen SIMD kernel the current code calls is a float64 axpy (SSE2 on amd64, NEON FMLA on arm64, z/vector on s390x) used by the separable Gaussian; morphology is a scalar van Herk / Gil-Werman running min/max on bytes. Separable passes fan rows or columns out over GOMAXPROCS goroutines above 16,384 pixels; RGBToHSV has no such tiling.

## Compared with alternatives

Pick it over OpenCV, CompV or DeltaCV (all faster C/C++ RGB to HSV) and FastBoxBlur only when the hard requirement is a cgo-free Go build; on speed alone those win, OpenCV by 15-30x on the measured ops. Against rez, the other pure-Go entry, it is complementary: rez is a SIMD resizer, go-images covers filters, colour and morphology and leaves resizing to go-gfx.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/go-gfx/gfx v0.34.0, go-images/gif v0.1.0, go-images/jpeg v0.2.0, go-images/png v0.1.0, sergeymakinen/go-ico v1.0.0, golang.org/x/image v0.46.0 (indirect: ajroetker/go-highway, go-images/jpeg2000, sergeymakinen/go-bmp, tannevaled/gobig2, golang.org/x/sys); no cgo |
| **Minimum toolchain** | Go 1.26.4 (go.mod) |
| **Platforms** | any Go target; README targets amd64, arm64, riscv64, loong64, ppc64le, s390x. Gaussian axpy is SIMD on amd64 (SSE2), arm64 (NEON) and s390x; other ops are scalar Go everywhere |
| **Thread safety** | Ops are pure functions that never mutate their input and return a new \*image.RGBA (README); internally they spawn up to GOMAXPROCS goroutines above 16,384 pixels. Concurrent calls are not otherwise documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- RGBToHSV stores H as round(hue\*255/360) in the R byte (about 1.41 degrees per step), S and V as bytes; this is neither skimage's float [0,1] nor OpenCV's 0-180 hue. The correctness gate never checks it: benchmarks/verify/main.go writes hsv.bin but benchmarks/verify.py never reads it (only the internal hsv_parity_test.go compares against the previous Go kernel).
- GaussianBlur truncates at ceil(3\*sigma) (13 taps at sigma 2 vs scipy's 17) and rounds the horizontal pass to bytes before the vertical pass; verify.py allows 4 levels of difference from skimage although BENCHMARKS.md and the README say within one level.
- Erode/Dilate/Open/Close work per channel on RGB, so on a colour image they are not luminance morphology; a grayscale result needs Grayscale first.
- Setting GOMAXPROCS (or go test -cpu) changes the internal fan-out; the single-thread numbers in BENCHMARKS.md depend on -cpu=1 collapsing the tiling to one goroutine.

## Known shortcomings

- Downgraded A to C: the scikit-image side times float64 in and out (img_as_float in run.py) while go-images runs uint8 with byte-quantised HSV, and benchmarks/verify.py has no HSV check, so the compared work differs; the Gaussian upper ratio is 1.30x, not as claimed. Off the category baselines, and OpenCV in the same table is about 24x faster on HSV and 15-30x on box blur.
- The headline wins come from algorithm, not SIMD: RGBToHSV is scalar Go on one goroutine and BoxBlur a scalar running sum (only the Gaussian axpy is SIMD). benchmarks/verify/main.go writes hsv.bin but verify.py never reads it, and the gate tolerances (BoxBlur 2, Gaussian 4) contradict the README's 'exact' and 'within 1 LSB'. The morphology rows run 3 RGB channels against 1 uint8 grey plane in skimage and OpenCV, overstating the losses and the OpenCV 165-186x gap. BENCHMARKS.md (2026-07-02) predates the HSV kernel's move to go-gfx/color (2026-08-15) and was not re-timed; transient memory at 4096x4096 is about 400 MB (BoxBlur) to 800 MB (Gaussian) of float64.

## Caveats and trade-offs

Off the category baselines (ImageMagick, stb_image_resize) and not a resampling benchmark: the parity table has no resize rows. OpenCV beats go-images by a wide margin on every op where it is shown (at one thread about 24x on RGB to HSV, 15x to 30x on box blur, 6x to 8x on Gaussian, 7x to 8x on Sobel and 165x to 186x on morphology, derived from page data). The scikit-image side runs float64 input and output (run.py converts with img_as_float before timing) while go-images and OpenCV run uint8, so the HSV and box-blur wins partly reflect float64 memory traffic; go-images also encodes hue into one byte (0-255), and its Gaussian truncates at 3 sigma against scipy's 4 sigma (fewer taps, author-stated). RGB to HSV has no correctness check in benchmarks/verify.py; BENCHMARKS.md calls BoxBlur exact but verify.py allows a 2-level difference. go-images is slower than scikit-image on Rotate90 (0.35x to 0.53x), Crop (0.24x to 0.33x), Otsu (0.37x to 0.47x), Close r=3 (0.64x to 0.93x), Open r=3 (0.69x to 0.91x) and Erode/Dilate at 512 and 1024 (0.79x to 0.87x). Raw result files (go-1t.txt, py-1t.json) are not committed. Author-run, very young project (37 commits, first visible commit June 2026) with one star.

Pure Go with no cgo; hot kernels use SIMD assembly generated by go-asmgen (amd64 SSE2, arm64 NEON, s390x) plus multicore tiling; every op returns a freshly allocated \*image.RGBA. Resize delegates to the go-gfx/gfx resample package.

## Maintenance

Active (37 commits from 2026-06-15 to 2026-09-27, mostly feature work and go-gfx dependency bumps), BSD-3-Clause and pure Go so it is easy to vendor, but it has one star, no releases and no outside users or issue reports yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party parity table (BENCHMARKS.md) with a public harness (benchmarks/parity_test.go, benchmarks/run.py), go1.26.4, go test -cpu=1 -count=5 and an Apple M4 Max, which would meet A on paper, but the measured scikit-image side does different work: run.py feeds skimage float64 arrays (img_as_float) and gets float64 HSV and float64 box-blur output, while go-images reads uint8 RGBA and writes byte-quantized HSV, and the headline RGB to HSV op is not in the correctness gate (benchmarks/verify.py has no HSV check). The like-for-like uint8 reference in the same table, OpenCV, is about 24x faster than go-images on RGB to HSV, so the claimed win is format-dependent and off the category baselines.
- **Verifier notes:** Numbers on BENCHMARKS.md match the record exactly; Gaussian range was understated (1.30x at 4096x4096) and the slower-op ranges were narrower than the page. Keep with the off-baseline, different-precision and OpenCV-wins shortcomings; downgraded A to C because the headline comparison is float64 skimage against uint8 go-images with no HSV correctness gate.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/go-images/images/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/README.md>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/benchmarks/parity_test.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/benchmarks/run.py>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/benchmarks/verify.py>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/color.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/filters.go>
  - <https://github.com/go-images/images>
  - <https://github.com/go-images/images/tree/main/benchmarks>
  - <https://github.com/go-images/images/commits/main>
- **Sources the enricher read:**
  - <https://github.com/go-images/images>
  - <https://github.com/go-images/images/issues>
  - <https://github.com/go-images/images/commits/main>
  - <https://github.com/go-images/images/commits/main/BENCHMARKS.md>
  - <https://github.com/go-images/images/tree/main/internal/kernels>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/README.md>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/go.mod>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/color.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/filters.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/morphology.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/benchmarks/parity_test.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/benchmarks/run.py>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/benchmarks/verify.py>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/benchmarks/go.mod>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/benchmarks/aggregate.py>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/benchmarks/verify/main.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/internal/kernels/kernels.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/internal/kernels/parallel.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/internal/kernels/simd.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/internal/kernels/simd_amd64.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/internal/kernels/simd_amd64.s>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/internal/kernels/simd_arm64.s>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/internal/kernels/hsv_bench_test.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/internal/kernels/hsv_parity_test.go>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/docs/perf.md>
  - <https://raw.githubusercontent.com/go-images/images/HEAD/docs/plan-images.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/go-images/images`) · [data/wave10/enrich/raw/github_com_go_images_images.json](../../../data/wave10/enrich/raw/github_com_go_images_images.json) (enrichment confidence 0.75)

</details>
