# go-gfx (resample package)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `BSD-3-Clause` · 🟢 active

> Pure-Go (CGO=0) RGBA resizer whose multicore Bicubic/Lanczos beat single-thread Pillow 12.2 1.7-4.9x; its serial Box loses.

| | |
|---|---|
| **Beats** | Pillow 12.2.0 Image.resize (BICUBIC, LANCZOS, BOX) |
| **Claimed result** | 1024x1024-&gt;256x256: Bicubic 1,886,402 ns vs Pillow 3,139,167 ns (1.66x faster), Lanczos 2,660,899 ns vs 4,587,000 ns (1.72x), Box 3,530,593 ns vs 2,285,292 ns (0.65x, slower). 256x256-&gt;1024x1024: Bicubic 1,621,422 ns vs 8,010,583 ns (4.9x), Lanczos 3,298,516 ns vs 10,446,834 ns (3.2x), Box 6,247,909 ns vs 4,813,333 ns (0.77x, slower). |
| **Workload** | Resize of a 1024x1024 RGBA image to 256x256 and of 256x256 to 1024x1024 with Bicubic, Lanczos and Box modes; go test -bench (ns/op) against Pillow best of 30 after warm-up on the same machine. |
| **Metric** | latency |
| **Hardware** | Apple Silicon (arm64), macOS, 16 logical CPUs; chip model not stated |
| **Compiler and flags** | Go 1.26.4, GOWORK=off, go test -bench; arm64 NEON axpy assembly kernel (resample/asmgen) plus multicore tiling; Pillow 12.2.0 with time.perf_counter |
| **Adoption** | 0 stars; 57 commits; README names go-images, go-widgets and go-webengine as consumers |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/go-gfx/gfx) · [benchmark](https://raw.githubusercontent.com/go-gfx/gfx/HEAD/docs/perf.md) |

## Verdict

On an unnamed Apple Silicon Mac (16 logical CPUs), Go 1.26.4 `go test -bench` resizing random opaque RGBA images beat Pillow 12.2.0 Image.resize (best of 30) 1.66x (Bicubic) and 1.72x (Lanczos) for 1024x1024 to 256x256, and 4.9x and 3.2x for 256x256 to 1024x1024. Box lost 0.65x and 0.77x. go-gfx tiled the filtered modes across all cores against single-thread Pillow; Box was serial on both sides. The Pillow timing script is not committed.

## Use it when

- Go services built with CGO disabled that need Pillow-quality Bicubic or Lanczos thumbnails or enlargements without linking libvips or Pillow.
- Multi-core machines with spare cores per request: the 1.66-4.9x wins come from tiling both passes across GOMAXPROCS goroutines (16 logical CPUs in the published run).
- Images large enough to cross ParThreshold (16384 output elements per pass, about a 128x128 output), e.g. 1024x1024 to 256x256 or 256x256 to 1024x1024.
- Pipelines that must stay numerically close to an existing Python/Pillow pipeline: parity_test.go checks 42.7-61.2 dB premultiplied-space PSNR against Pillow 12 references.
- Cut-out images with transparency, via ResizePremultiplied, which removes the colour fringe that straight-alpha filtering leaves.

## Skip it when

- Box/area downscaling or enlargement: serial and unvectorised, 0.65x (1024 to 256) and 0.77x (256 to 1024) of Pillow's speed.
- Single-core containers, GOMAXPROCS=1, or servers already running one resize per core: no single-thread numbers are published. Rough estimate (not measured): Bicubic 1024 to 256 does about 4x the multiply-adds of Box (16 taps per axis versus 4), and serial Box already takes 3.53 ms, so a single-thread Bicubic run is likely behind Pillow's 3.14 ms. `go test -bench Resize -cpu 1` would settle it.
- Small thumbnails: a pass below ParThreshold (e.g. a 64x64 output's vertical pass) runs serially.
- Bit-exact Pillow output: go-gfx stays in float64 while Pillow uses 22-bit fixed-point integers with an 8-bit intermediate, and Box has no Pillow parity test at all (only a self-consistency test).
- Memory-tight or mature-dependency settings: the scratch plane is srcH x dstW x 4 float64 (8 MiB in both benchmark cases), allocated per call; the repo dates from 2026-08-28 with 0 stars and no tagged releases.

## How it is fast

Bicubic and Lanczos are separable: a horizontal gather pass writes a float64 scratch plane, then the vertical pass builds each output row as one axpy (dst += w\*src) per filter tap over a whole contiguous RGBA row, run by go-asmgen assembly kernels (arm64 NEON VFMLA, amd64 SSE2 MULPD+ADDPD, s390x vector). Both passes split their rows into contiguous bands, one goroutine per band up to GOMAXPROCS, once rows x output width reaches ParThreshold (16384). Most of the measured win is that fan-out: Box, which runs a serial scalar float64 weighted span sum with no SIMD and no tiling, is 0.65-0.77x Pillow.

## Compared with alternatives

Pick it over rez (bamiaux/rez, the other pure-Go SIMD resizer, measured only against ImageMagick and Go resizers) when you want Pillow-matching Bicubic/Lanczos output and multicore tiling built in. Pick fast_image_resize (Rust, single-thread AVX2/NEON wins over libvips) or stb-image-resize-opt and tir (C) when you are not on Go or need a single-thread speed win that has been measured.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | resample imports only go-gfx's own color and raster packages; the module's go.mod also requires golang.org/x/image, sergeymakinen/go-ico, go-images/jpeg2000 and tannevaled/gobig2 (for the codec package), despite the README's 'no third-party dependencies' |
| **Minimum toolchain** | Go 1.26.4 (go.mod 'go 1.26.4'); CI also runs Go stable |
| **Platforms** | any Go target; SIMD axpy kernel on amd64 (SSE2), arm64 (NEON) and s390x (vector); scalar loop plus multicore tiling on loong64, ppc64le, riscv64, 386 and arm (CI runs these under qemu) |
| **Thread safety** | not documented; Resize and ResizePremultiplied allocate their own output and scratch per call and share only the package-level var ParThreshold, which tests mutate |
| **Drop-in for the baseline** | no |

## Gotchas

- Resize filters all four channels independently (straight alpha), while Pillow's Image.resize converts RGBA to RGBa (premultiplied) and back for every non-NEAREST filter; ResizePremultiplied is the Pillow-equivalent call. The benchmark times Resize, and the uncommitted Pillow harness does not say whether Pillow got RGBA (and so paid both conversion passes, the second over the full 1024x1024 output on enlargement).
- docs/perf.md calls Pillow's resampler 'single-threaded C with SIMD' and its BOX 'hand-tuned SIMD C'. Stock Pillow's src/libImaging/Resample.c (main branch) has no SIMD intrinsics: it is a scalar fixed-point convolution (PRECISION_BITS 22), and BOX goes through the same generic convolution as BICUBIC with support 0.5. Pillow-SIMD, the SIMD fork, was not tested.
- raster.Image is straight-alpha with stride 4\*W, unlike the standard library's premultiplied image.RGBA, so going through FromImage and ToRGBA adds a conversion pass that the benchmark does not time.
- The amd64 kernel is SSE2 multiply-then-add (no FMA, no AVX2); TestAxpyMatchesScalar allows a small tolerance for GOAMD64=v3 builds, where the scalar fallback uses fused multiply-add.

## Known shortcomings

- The bicubic and Lanczos wins (docs/perf.md) run multicore (GOMAXPROCS) against single-threaded Pillow 12.2.0 while the serial Box path loses (0.65x, 0.77x); no Pillow timing script is committed (generate.py only writes parity fixtures) and the Apple Silicon chip is unnamed.
- Enricher (2026-10-04): the Pillow comparison (1.66x/1.72x downscale, 4.9x/3.2x upscale; Box loses 0.65x/0.77x) tiles the filtered modes across all 16 logical cores of an unnamed Apple Silicon Mac against single-threaded Pillow 12.2.0; the Pillow timing script is not committed. Work is unequal: Resize filters four straight-alpha channels while Pillow converts RGBA to premultiplied and back for every non-NEAREST filter (ResizePremultiplied is the equivalent call), and the uncommitted harness does not say whether Pillow paid both passes. docs/perf.md calls Pillow's resampler 'single-threaded C with SIMD' and BOX 'hand-tuned SIMD C', but stock Pillow Resample.c has no SIMD intrinsics (scalar fixed-point convolution); Pillow-SIMD was not tested. The amd64 kernel is SSE2 multiply-then-add (no FMA, no AVX2). Brand new (first commit 2026-08-28, 0 stars, no releases). Tier C stands.

## Caveats and trade-offs

Mixed, asymmetric result: Bicubic and Lanczos beat Pillow (1.66x and 1.72x on 1024-&gt;256 reduction, 4.9x and 3.2x on 256-&gt;1024 enlargement), while Box loses (0.65x and 0.77x). The filtered modes fan out across GOMAXPROCS goroutines (resample/parallel.go, up to 16 logical CPUs here) against single-threaded Pillow, so those wins mix algorithm and thread count; Box runs serially in go-gfx, making it the only like-for-like single-thread comparison, and it is a loss. Pillow-SIMD was not tested, and there is no golang.org/x/image, OpenCV or stb_image_resize comparison. bench_test.go says it matches 'the Pillow harness in docs/perf.md', but no Pillow timing script is committed, so the baseline side is not reproducible; perf.md notes Pillow's RGBA resize is premultiplied-alpha aware while the benchmark times the straight-alpha Resize, so if the harness fed Pillow RGBA images Pillow also did premultiply and unpremultiply passes (harness mode not stated). go-gfx works in float64 and Pillow in 8-bit; parity vs Pillow is 42.7-61.2 dB PSNR (parity_test.go). Inputs are random opaque RGBA. Chip model missing (Apple Silicon, 16 logical CPUs). Repo is new (commits seen from 2026-08-28 to 2026-10-01, 57 commits, 0 stars). The vector package section only claims parity with earlier code, with no competitor comparison.

Pure Go with CGO disabled, float64 end-to-end (more memory and compute than 8-bit pipelines). SIMD assembly for amd64 SSE2, arm64 NEON and s390x; loong64, ppc64le and riscv64 use the scalar loop plus multicore tiling. Not bit-exact with Pillow: premultiplied-space PSNR 42.7-61.2 dB. Box mode is slower than Pillow.

## Maintenance

Active (57 commits from 2026-08-28 to 2026-10-01, CI on six 64-bit architectures plus 32-bit, 2 open issues, neither about resample) and BSD-3-Clause, but brand new, with 0 stars and no releases. Its stated consumers are the same author's go-images, go-widgets and go-webengine.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/perf.md carries every number in the record and the Go side is public (resample/bench_test.go), but the Pillow timing script is not committed (docs/ holds only perf.md; testdata/generate.py only writes parity fixtures) and the Apple Silicon chip is not named, so it is first-party with partial methodology.
- **Verifier notes:** Numbers match docs/perf.md exactly; tier C stands. Wins are multi-core Go vs single-thread Pillow on Bicubic/Lanczos; the serial Box path loses 0.65x-0.77x.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party Go benchmark vs uncommitted Pillow script
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/docs/perf.md>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/bench_test.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/parallel.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/testdata/generate.py>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/LICENSE>
  - <https://github.com/go-gfx/gfx>
  - <https://github.com/go-gfx/gfx/commits/main>
  - <https://github.com/go-gfx/gfx/tree/main/docs>
  - <https://github.com/go-gfx/gfx/tree/main/resample>
  - <https://github.com/go-gfx/gfx/tree/main/resample/testdata>
- **Sources the enricher read:**
  - <https://github.com/go-gfx/gfx>
  - <https://github.com/go-gfx/gfx/tree/main/resample>
  - <https://github.com/go-gfx/gfx/issues>
  - <https://github.com/go-gfx/gfx/commits/main>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/README.md>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/docs/perf.md>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/go.mod>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/resample.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/kernel.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/coeffs.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/filter.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/parallel.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/simd.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/simd_arm64.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/simd_arm64.s>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/simd_amd64.s>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/simd_generic.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/bench_test.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/parity_test.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/resample_test.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/resample/testdata/generate.py>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/raster/raster.go>
  - <https://raw.githubusercontent.com/go-gfx/gfx/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/main/src/libImaging/Resample.c>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/main/src/PIL/Image.py>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/go-gfx/gfx`) · [data/wave10/enrich/raw/github_com_go_gfx_gfx.json](../../../data/wave10/enrich/raw/github_com_go_gfx_gfx.json) (enrichment confidence 0.75)

</details>
