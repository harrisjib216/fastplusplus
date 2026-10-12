# rez (pure Go and SIMD image resizer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Pure-Go image resizer with SSE2 assembly kernels for YCbCr, RGBA and Gray planes; faster than other pure-Go resizers.

| | |
|---|---|
| **Beats** | ImageMagick convert -resize; also nfnt/resize, disintegration/imaging, gift, bild and golang.org/x/image/draw |
| **Claimed result** | Third-party scenario (3.4GHz Intel Core i7, Ubuntu 16.10): rez_bilinear 0.349 s per file vs ImageMagick_resize 0.568 s (about 1.6x faster, derived from page data), x_image_draw 0.370 s, imaging_box 0.439 s, gift_box 0.440 s, Nfnt_NearestNeighbor 0.447 s, bild_resize 0.515 s. Scenario by rez's author (3.3GHz Core i5, Windows 7): rez_bilinear 148 ms vs imaging_Box 243 ms and Nfnt_NearestNeighbor 233 ms. On the original Pentium T2390 1.86GHz run rez_bilinear took 2.913 s, slower than ImageMagick_resize at 2.316 s. |
| **Workload** | Load 5616x3744 JPEG photos, scale each to a 150x100 thumbnail, write a JPEG, and report average time per file (third-party speedtest-resize shootout; load and save time is included). |
| **Metric** | latency |
| **Hardware** | Several: Intel Pentium T2390 1.86GHz (Ubuntu 14.04), Intel Core i5 3.3GHz (Windows 7), Intel Core i7 3.4GHz (Ubuntu 16.10) |
| **Adoption** | 214 stars |
| **Last commit** | 2017-07-31 |
| **Links** | [repository](https://github.com/bamiaux/rez) · [benchmark](https://github.com/fawick/speedtest-resize) |

## Verdict

In fawick/speedtest-resize (third-party, MIT; run by contributor nono on a 3.4GHz Core i7 with Ubuntu 16.10, one pass over the first ten 5616x3744 JPEGs, decode plus resize plus encode timed together), rez_bilinear averaged 0.349 s per file against 0.568 s for ImageMagick `convert -resize 150x150>` and 0.370-0.515 s for the other pure-Go resizers, while ImageMagick's -thumbnail path took 0.057 s. Reading the harness adds three points to the verifier's notes: rez runs on all cores by default (GOMAXPROCS goroutines) and the harness sets no thread limits for any contender; its bilinear kernel widens to about 76 taps at this 37x reduction, so the resize itself is a real antialiased filter, and every pure-Go row also pays for a full Go image/jpeg decode; and the harness ignores decode and convert errors but still counts the file and its time, although rez's 0.140% average output size (other pure-Go rows: 0.146-0.160%) shows no sign that files were skipped.

## Use it when

- Go services that make thumbnails or scaled copies from JPEGs decoded with image/jpeg and must stay free of cgo; staying in YCbCr skips a full-resolution RGBA conversion.
- Video or frame pipelines in Go that resize many frames of the same size (reuse one Converter per goroutine), including interlaced material and chroma-subsampling changes.
- amd64 servers, where the SSE2 kernels are used; the filter widens on downscale (support divided by the scale factor), so even the bilinear setting is antialiased rather than point-sampled.
- Vendoring a small, dependency-free MIT resizer into a Go codebase that cannot take new upstream maintenance.

## Skip it when

- Whenever cgo or an external process is acceptable: in the same i7 table ImageMagick -thumbnail with jpeg:size (0.057 s), the libvips binding (0.070 s), epeg (0.079 s), fastjpeg (0.082 s), OpenCV (0.110 s) and vipsthumbnail (0.115 s) all beat rez (0.349 s).
- Large-reduction JPEG thumbnails: rez needs the full-resolution decode, while DCT-domain downscaling on load (jpeg:size, epeg, fastjpeg) skips most of the decode work.
- arm64 and other non-amd64 targets: only SSE2 amd64 assembly exists (no AVX2, no NEON), so other architectures run the scalar Go loops.
- Colour-accurate work: filtering runs on gamma-encoded 8-bit values (issue #8, open since 2015, unanswered), NRGBA is filtered as packed bytes without premultiplying alpha, and there is no 16-bit or float path.
- Paletted, CMYK, RGBA64 or Gray16 images: anything other than YCbCr, RGBA, NRGBA or Gray returns 'unknown image format' (issue #12 hit this with a PNG).

## How it is fast

It filters the decoded YCbCr planes directly instead of converting to RGBA first (imaging and gift convert), with a separable two-pass resize (vertical, then horizontal) driven by precomputed 14-bit fixed-point int16 kernels. Hot loops are generated SSE2 assembly per tap count (2 to 12, plus a generic N-tap path) built on PMADDWD multiply-accumulate with PUNPCKLBW/PACKUSWB widening and packing; the tests check that the assembly output is bit-identical to the pure-Go loops. Each plane is split into GOMAXPROCS horizontal slices run as goroutines, and a reusable Converter avoids rebuilding kernels and buffers for repeated geometry.

## Compared with alternatives

Pick rez only when the program must stay pure Go: if cgo or an external process is allowed, libvips, epeg and OpenCV were 3-6x faster in the same shootout, and fast_image_resize is the stronger SIMD choice in Rust (AVX2 and NEON).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Go standard library only) |
| **Minimum toolchain** | CI was Go 1.5 to 1.8 (issue #9, 'Cannot build with Go &gt;1.7', closed 2016); no go.mod, so modules use a pseudo-version. fawick/speedtest-resize's go.mod (go 1.26.0) still pins rez at the 2017-07-31 commit, which suggests it builds on current Go; not verified here |
| **Platforms** | amd64 with SSE2 assembly; any other Go target through the pure-Go fallback (scalers_gen.go) |
| **Thread safety** | Convert starts its own goroutines (GOMAXPROCS slices by default, inline when Threads is 1). A Converter keeps its intermediate plane buffers between calls (converterContext.buffer), so one Converter must not be used from several goroutines at once; use one per goroutine. |
| **Drop-in for the baseline** | no |

## Gotchas

- The destination must be pre-allocated at the target size with the same type and plane layout as the source; YCbCr-to-RGBA or other pack/plane mismatches return an error even though the docs say Convert applies 'any necessary colorspace conversion'.
- One-shot rez.Convert rebuilds kernels and buffers on every call and defaults to GOMAXPROCS goroutines per call; under concurrent request load set ConverterConfig.Threads to 1 and reuse Converters to avoid oversubscription and repeated setup.
- From kernels.go: horizontal kernel offsets are stored as int16 absolute pixel positions, so inputs wider than 32767 px would overflow (slice panic in Go, out-of-range reads in assembly); this was read from the source, not tested.
- Planes smaller than 2 px in either dimension are rejected, and the assembly is disabled for outputs narrower than 16 px (pure-Go path used).

## Known shortcomings

- Downgraded B to C: speedtest-resize (co-authored by the rez author) compares rez bilinear on YCbCr at Go default quality with a spawned ImageMagick convert -resize using its default filter and quality (output 3.9x larger), so the filters differ; ImageMagick's -thumbnail path is about 6x faster than rez; no Go or ImageMagick version or CPU model. Repository archived 2024-05-19.
- Bilinear widens to about 76 taps on downscale (real antialiased work); the harness has no thread control (rez uses GOMAXPROCS goroutines by default) and ignores errors while counting the file; SSE2 only (no AVX2 or NEON); int16 kernel offsets overflow above 32767 px wide (from source, untested); open issue #8 (gamma-space filtering) unanswered; the Converter is not safe for concurrent use.

## Caveats and trade-offs

Different work on the two sides: rez_bilinear (pure.go) decodes with Go image/jpeg, resizes the YCbCr planes with a bilinear filter and re-encodes at Go's default quality, while ImageMagick_resize (exec.go) spawns `convert -resize 150x150>` per file with ImageMagick's default resize filter and quality, so its thumbnails are about 3.9x larger (0.542% vs 0.140% of input, derived from page data) and the filters differ. The fast ImageMagick path in the same harness, `-define jpeg:size=300x300 -thumbnail 150x150>`, takes 0.057 s per file in the i7 table, about 6x faster than rez (derived from page data), and vips, epeg, fastjpeg, opencv, vipsthumbnail, GraphicsMagick, magickwand and T-REZ are all faster than rez there. On the original Pentium T2390 run rez (2.913 s) is slower than ImageMagick -resize (2.316 s). The metric includes JPEG decode and encode. Old hardware and Go versions (2014 to 2016 era), with no Go version, ImageMagick version, flags or CPU model stated. speedtest-resize is MIT-licensed and lists rez's author (Benoît Amiaux) among its authors; the i7 table was run by nono and one Windows table by bamiaux himself. rez's own bench_test.go only compares its Go and assembly paths. Repo archived on 2024-05-19.

Pure Go with AMD64 assembly horizontal and vertical scalers (asm/, hscalers_amd64.s, vscalers_amd64.s); resizes YCbCr, RGBA, NRGBA and Gray, supports chroma subsample conversion, interlaced-aware resize and parallel slices. The repo is archived (2024-05-19).

## Maintenance

Abandoned: last commit 2017-07-31 and archived 2024-05-19 (214 stars, one open issue). It is MIT-licensed with no dependencies, and small enough to vendor (a dozen Go files plus two generated assembly files), but it will get no fixes and has no SIMD outside amd64.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** The speedtest-resize README tables match the record, and the harness is public (pure.go, exec.go, main.go), but the rez row and the ImageMagick_resize row do different work: rez runs a bilinear filter directly on subsampled YCbCr planes and saves with Go's default JPEG quality (jpeg.Encode with nil options), while ImageMagick runs `convert -resize 150x150>` as an external process with its default filter and output quality (output 0.542% of input size vs 0.140% for rez in the i7 table). No Go version, ImageMagick version or CPU model is given (only '3.4GHz Intel Core i7').
- **Verifier notes:** Numbers verified on the speedtest-resize README; downgraded B to C because the ImageMagick -resize baseline uses a different filter, colour path, output quality and process-spawn overhead, and the like-for-like fast ImageMagick thumbnail path beats rez by about 6x. Keep with shortcoming; record's claim that speedtest-resize has no license was wrong (MIT).
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/fawick/speedtest-resize>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/README.md>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/main.go>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/pure.go>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/exec.go>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/go.mod>
  - <https://github.com/bamiaux/rez>
  - <https://github.com/bamiaux/rez/commits/master>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/README.md>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/bench_test.go>
- **Sources the enricher read:**
  - <https://github.com/bamiaux/rez>
  - <https://github.com/bamiaux/rez/commits/master>
  - <https://github.com/bamiaux/rez/issues?q=is%3Aissue>
  - <https://github.com/bamiaux/rez/issues/8>
  - <https://github.com/bamiaux/rez/issues/12>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/README.md>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/image.go>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/resize.go>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/filters.go>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/kernels.go>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/scalers.go>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/scalers_amd64.go>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/scalers_gen.go>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/fixedscalers.go>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/hscalers_amd64.s>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/vscalers_amd64.s>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/asm/asm.go>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/utils.go>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/bench_test.go>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/resize_test.go>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/bamiaux/rez/HEAD/mkscalers.sh>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/README.md>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/main.go>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/pure.go>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/exec.go>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/go.mod>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/bamiaux/rez`) · [data/wave10/enrich/raw/github_com_bamiaux_rez.json](../../../data/wave10/enrich/raw/github_com_bamiaux_rez.json) (enrichment confidence 0.75)

</details>
