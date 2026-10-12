# nativewebp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Pure-Go lossless WebP (VP8L) encoder; README shows it 1.2-2.3x faster than Go's image/png at BestCompression with 14-26% smaller files.

| | |
|---|---|
| **Beats** | Go standard library image/png encoder at png.BestCompression |
| **Claimed result** | README: 'approximately 50% faster' than the standard Go PNG encoder and smaller files. Per image (image/png at BestCompression vs nativewebp at BestCompression, ns/op): 42,945,049 vs 35,413,726 ('17% faster', 120 kb vs 95 kb); 98,509,399 vs 42,626,779 ('57% faster', 46 vs 35 kb); 178,205,535 vs 96,800,750 ('46% faster', 236 vs 190 kb); 29,088,555 vs 19,877,708 ('32% faster', 53 vs 39 kb); 63,423,995 vs 27,813,126 ('56% faster', 139 vs 119 kb). The README's 'X% faster' is percent less time: 1.21x-2.31x per image, 1.85x in total (412.2 ms vs 222.5 ms), with WebP output 80.5% of the PNG bytes in total (derived from page data). |
| **Workload** | Encoding five images from Google's WebP lossless gallery with the lossless-only nativewebp encoder at nativewebp.BestCompression versus image/png at png.BestCompression, reported in ns/op together with output size. |
| **Metric** | latency |
| **Compiler and flags** | Go benchmark output (ns/op); Go toolchain, flags and benchmark source not published (go.mod declares go 1.22.2, golang.org/x/image v0.24.0). |
| **Adoption** | 462 stars |
| **Last commit** | 2026-05-10 |
| **Links** | [repository](https://github.com/HugoSmits86/nativewebp) · [benchmark](https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/README.md) |

## Verdict

A first-party 'quick benchmark' in the README encodes five images from Google's WebP lossless-and-alpha gallery with nativewebp.BestCompression vs Go's image/png at png.BestCompression: 1.21-2.31x less time per image (412.2 ms vs 222.5 ms in total, 1.85x) and 80.5% of the PNG bytes in total, derived from page data. No benchmark code (no Benchmark functions), Go version or CPU is published, the comparison is across formats (VP8L vs PNG/flate-9) rather than two encoders of one format, and a third-party report from March 2026 (issue #18) found the encoder slower than png.BestCompression on its images.

## Use it when

- Go services that must stay CGO_ENABLED=0 and want lossless WebP output (thumbnails, UI assets, screenshots, LED-matrix frames) without linking libwebp.
- Replacing image/png at png.BestCompression when WebP is an acceptable output format and smaller lossless files matter; the README's five gallery images came out 14-26% smaller.
- Lossless animated WebP from Go (EncodeAll), where image/gif's 256-colour limit is the alternative.
- Small to mid-size images; the published numbers are all on Google's lossless-and-alpha gallery images.

## Skip it when

- When you need lossy WebP, or the best lossless ratio: there is no lossy mode, no meta-Huffman codes and no cross-colour transform, and nothing in the repo compares it with libwebp (cwebp -lossless) on speed or size.
- When the alternative is image/png at its default level or BestSpeed: only png.BestCompression (flate level 9) was compared, and a third-party report (issue #18, i5-13600KF, Go 1.26.1, March 2026, before the May 2026 revision) measured the default encoder at 400 ms vs 150 ms for png.BestCompression on a large image and 9 vs 7 ms on a small one.
- Images above 16,384 pixels on either side: Encode returns 'invalid image size'.
- Large batches needing parallel encode inside one image: the encoder is single-goroutine and allocates several full-image buffers (an NRGBA copy, a pixel slice, a deltas slice and an int slice of 4 entries per pixel).

## How it is fast

It is a deliberately simple VP8L encoder: subtract-green, then a predictor transform that picks one of the 14 VP8L predictors per tile by a Gini-style histogram score, then pixel-granular LZ77 (3-pixel hash, chain depth 128, matches up to 4,096 pixels, VP8L 2-D distance codes) with an 11-bit colour cache, entropy-coded with one set of five Huffman codes for the whole image. Working on 32-bit pixels instead of bytes, with no meta-Huffman image and no cross-colour transform (it is hard-coded off), keeps the work per pixel low compared with Go's compress/flate at level 9 behind png.BestCompression. Paletted inputs (\*image.Paletted) take the colour-indexing transform with pixel bundling instead.

## Compared with alternatives

Pick it when the output must be WebP from a cgo-free Go build; no other catalogued image-codecs entry is a Go WebP encoder. If PNG output is fine and native code is acceptable, fpnge and fpng (C/C++) encode PNG one to two orders of magnitude faster than libpng, and libjxl's fast_lossless or QOI give much faster lossless encodes in other formats.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/image v0.24.0 (decoder only); no cgo |
| **Minimum toolchain** | Go 1.22.2 (go.mod) |
| **Platforms** | any Go target (pure Go, no assembly) |
| **Thread safety** | not documented; Encode keeps no package-level state, so concurrent calls on different images look safe from the code, but EncodeAll writes clamped values back into the caller's Durations and Disposals slices |
| **Drop-in for the baseline** | partial — same Encode(w, img, opts) shape as image/png, but it writes WebP, not PNG, so every consumer must accept WebP |

## Gotchas

- CompressionLevel only changes the predictor tile size (transBits); the LZ77 search, colour cache and Huffman coding are identical at every level. From getHistoBits/getTransformBits, Default and BestCompression produce the same tile size, and so the same output, for images between about 204x204 and 816x816 pixels, so 'both at maximum compression' in the README may mean the default encoder for its gallery images (their sizes are not stated).
- Encode and EncodeAll ignore errors from w.Write and return nil on a failed write, despite the doc comment; internal failures surface as panics rather than errors (bitWriter.writeBits panics on overflow; issues #3, #15 and #16 were encoder panics, all closed).
- The 15-bit Huffman depth limit is a weight floor (counts raised to total&gt;&gt;13), not a guaranteed length-limiting algorithm: a simulation of the same rule gives 16-18-bit codes for Fibonacci-shaped histograms of 17-19 symbols, which the writer would emit as code-length symbols 16-18 (repeat codes) and corrupt the stream. Derived from the code; not observed on a real image.
- Tests compare against stored golden bytes and round-trip only through golang.org/x/image/webp; nothing checks output against libwebp's decoder.

## Known shortcomings

- Different format from the baseline: lossless WebP (VP8L) against Go image/png at BestCompression (DEFLATE level 9), so the 1.85x total (1.21-2.31x per image, derived from page data) and the 80.5% output size compare different codecs. No Benchmark functions in the repo, no Go version or CPU, no comparison against libwebp.
- A third-party run in issue #18 (i5-13600KF, Go 1.26.1, 2026-03-30) puts the default encoder at 400 ms against 150 ms for png.BestCompression on a large image (9 vs 7 ms small), predating the May 2026 README revision. CompressionLevel only changes the predictor tile size, and default and BestCompression give identical output for images of about 204x204 to 816x816 px, so the README's 'both at max compression' is probably the default. Latent bug by code reading: the 15-bit Huffman limit is a weight-floor heuristic, and Fibonacci-shaped histograms yield 16-18-bit codes that would be written as repeat symbols and corrupt the stream (not seen on real images); Encode ignores w.Write errors; never compared with libwebp.

## Caveats and trade-offs

Different work from the baseline: nativewebp writes lossless WebP (VP8L) and image/png writes PNG with DEFLATE level 9, so the speed and size gains compare two formats, not two encoders of one format; both are lossless and both use their maximum-compression setting (nativewebp.BestCompression = method 6, added 2026-05-10 together with the revised README numbers). README calls it 'a quick benchmark': five images from Google's WebP lossless-and-alpha gallery, no harness in the repo, no hardware or Go version. Not compared against libwebp (cwebp -lossless), the natural WebP incumbent, so it shows nothing about speed against libwebp. Encoder is lossless only; decoding wraps golang.org/x/image/webp.

Pure Go, no cgo or libwebp. Encodes only lossless WebP (VP8L) and animations; decoding is a wrapper around golang.org/x/image/webp. Not a lossy encoder.

## Maintenance

Maintained by one author (MIT, 462 stars; last commits 2026-05-10 added compression levels, the revised README numbers and a 256 MiB decode read limit); feature request #17 is open and issue #18's resolution is not visible on the page, but the code is small (about 1,350 lines of non-test Go) and easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table with ns/op and file sizes for five gallery images against Go's image/png at png.BestCompression, but no benchmark code exists in the repo (no Benchmark functions in any \*_test.go) and no Go version or CPU is stated.
- **Verifier notes:** Numbers match the README exactly. Kept at C; the 'about 50%' headline is close to the derived total (46% less time) but per-image gains range from 17% to 57% less time. Metadata checked: MIT, 462 stars, 20 forks, not a fork, last commit 2026-05-10.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/README.md>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/writer.go>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/writer_test.go>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/bitwriter_test.go>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/huffman_test.go>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/reader_test.go>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/transform_test.go>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/go.mod>
  - <https://github.com/HugoSmits86/nativewebp>
  - <https://github.com/HugoSmits86/nativewebp/commits>
- **Sources the enricher read:**
  - <https://github.com/HugoSmits86/nativewebp>
  - <https://github.com/HugoSmits86/nativewebp/commits>
  - <https://github.com/HugoSmits86/nativewebp/issues?q=is%3Aissue>
  - <https://github.com/HugoSmits86/nativewebp/issues/18>
  - <https://github.com/HugoSmits86/nativewebp/issues/17>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/README.md>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/go.mod>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/writer.go>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/reader.go>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/huffman.go>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/transform.go>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/bitwriter.go>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/writer_test.go>
  - <https://raw.githubusercontent.com/HugoSmits86/nativewebp/HEAD/reader_test.go>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/hugosmits86/nativewebp`) · [data/wave10/enrich/raw/github_com_hugosmits86_nativewebp.json](../../../data/wave10/enrich/raw/github_com_hugosmits86_nativewebp.json) (enrichment confidence 0.7)

</details>
