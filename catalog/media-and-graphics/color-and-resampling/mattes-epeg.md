# epeg

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `MIT-enna (Enlightenment MIT variant: COPYING requires publicly documented acknowledgment when the source is not published; COPYING-PLAIN is a non-binding plain-English note). Not OSI-approved.` · 🔴 abandoned

> Small C library and CLI for JPEG-to-JPEG thumbnails via libjpeg scaled decode; beats plain 'convert -resize', loses to ImageMagick -thumbnail and libvips.

| | |
|---|---|
| **Beats** | ImageMagick convert -resize 150x150&gt; (plain resize mode); ImageMagick's own -thumbnail mode with the jpeg:size hint is faster than epeg in the same table |
| **Claimed result** | speedtest-resize README, scenario run by contributor nono (3.4GHz Intel Core i7, Ubuntu 16.10, average over the first 10 JPEGs, one pass): epeg 0.079 s per file vs ImageMagick_resize ('convert -resize 150x150&gt;') 0.568 s, 7.2x (derived from page data), but that ImageMagick command decodes the full 5616x3744 image and runs a convolution resize while epeg decodes at 1/8 scale in the DCT domain and point-samples. Against ImageMagick_thumbnail ('convert -define jpeg:size=300x300 -thumbnail 150x150&gt;'), which uses the same libjpeg DCT-domain downscale, epeg is slower: 0.079 s vs 0.057 s (ImageMagick 1.39x faster, derived from page data). The vips binding (0.070 s) is also faster than epeg; vipsthumbnail (0.115 s) and GraphicsMagick_thumbnail (0.172 s) are slower. |
| **Workload** | speedtest-resize (Go driver main.go and exec.go): for each of the first 10 JPEGs (5616x3744) in a folder, spawn the tool, load, scale to a 150x100 thumbnail and write a JPEG; the time includes process start-up. epeg runs as 'epeg -m 150' (libjpeg scale_denom 8 with JDCT_IFAST, no fancy upsampling and no block smoothing, i.e. a 702x468 decode, then nearest-neighbour point sampling in _epeg_scale, JPEG quality 85). ImageMagick_resize runs 'convert -resize 150x150&gt;' (full-resolution decode plus ImageMagick's default convolution filter); ImageMagick_thumbnail runs 'convert -define jpeg:size=300x300 -thumbnail 150x150&gt;' (DCT-domain downscale at decode, then a filtered resize). |
| **Metric** | throughput |
| **Hardware** | 3.4GHz Intel Core i7 (model not stated), Ubuntu 16.10; scenario run by GitHub user nono and added to the README. epeg and ImageMagick versions not stated. |
| **Compiler and flags** | Not stated. |
| **Adoption** | 274 stars |
| **Last commit** | 2023-04-05 |
| **Links** | [repository](https://github.com/mattes/epeg) · [benchmark](https://github.com/fawick/speedtest-resize) |

## Verdict

In one contributor run of fawick/speedtest-resize (nono; 3.4 GHz Intel Core i7, model unstated, Ubuntu 16.10; first 10 JPEGs of 5616x3744 to 150x100; process start-up included; one pass; epeg, libjpeg and ImageMagick versions not stated), 'epeg -m 150' averaged 0.079 s per file against 0.568 s for 'convert -resize 150x150&gt;' (7.2x, derived from page data), but that ImageMagick command decodes at full resolution and filters while epeg decodes at 1/8 scale and point-samples; ImageMagick's own '-define jpeg:size=300x300 -thumbnail 150x150&gt;' (0.057 s, 1.39x faster than epeg) and the vips binding (0.070 s) beat it. The harness times each external command without checking its output, and epeg's CLI exits 0 even on failure; the non-zero average output size (0.207% of the input) shows thumbnails were written but per-file success is unverified.

## Use it when

- Bulk JPEG-to-JPEG thumbnails at 1/8 linear size or smaller (gallery previews from camera files), where nearest-neighbour quality is acceptable and you want an in-process C call rather than spawning a tool.
- Embedding in a C or C++ program that cannot take on ImageMagick or libvips: the library is one 1,450-line C file depending only on libjpeg, libexif and libm.
- Replacing an existing 'convert -resize' thumbnail step that lacks the jpeg:size hint: 0.079 s vs 0.568 s per 21-megapixel file in the one recorded run.
- Feeding reduced-size YUV or grey pixels into your own pipeline via epeg_pixels_get after setting EPEG_YUV8 or EPEG_GRAY8, which skips colour conversion.

## Skip it when

- When ImageMagick or libvips is available: in the same table 'convert -define jpeg:size=300x300 -thumbnail 150x150&gt;' took 0.057 s and the vips binding 0.070 s per file against epeg's 0.079 s, and both resample with a filter instead of point sampling.
- Quality-sensitive thumbnails: JDCT_IFAST, no fancy upsampling and nearest-neighbour sampling give aliasing on fine detail; vipsthumbnail, ImageMagick -thumbnail or the filtered resizers in this category (fast_image_resize, Pillow-SIMD, MagicScaler) look better.
- Thumbnails larger than half the source on either axis: the scale factor falls to 1, so it decodes at full resolution and then point-samples, with no speed advantage.
- Colour-managed or metadata-preserving workflows: ICC profiles are not copied (open issue #26), EXIF other than Orientation is dropped, and pixels are not rotated (only the Orientation tag is carried over).
- Untrusted input at scale: there is no test suite, the project has been idle since April 2023, and _epeg_decode computes the pixel buffer size as a 32-bit unsigned product (output_width \* output_height \* output_components) with no overflow check, which a JPEG of more than about 1.4 gigapixels decoded at scale 1 could wrap (found by code reading, not tested).

## How it is fast

All the speed comes from libjpeg's scaled decoding: _epeg_decode sets scale_denom to min(floor(in_w/out_w), floor(in_h/out_h)) clamped to 1..8, with JDCT_IFAST, do_fancy_upsampling = FALSE and do_block_smoothing = FALSE, so a 5616x3744 photo is decoded straight to 702x468 in the DCT domain. _epeg_scale then point-samples (nearest neighbour, in place) to the exact thumbnail size and libjpeg re-encodes it. There is no SIMD or filtering of its own; the gain is bounded by libjpeg's entropy decoding, which is why the measured 7.2x over a full-resolution ImageMagick resize is far below the 1,402x pixel-count ratio the README's 'speedup proportional to the size difference' would imply (derived from page data).

## Compared with alternatives

Pick epeg over libvips or ImageMagick only when you need a tiny C dependency for JPEG-only thumbnails and accept point-sampled quality; libvips (in-process binding 0.070 s per file) and ImageMagick's -thumbnail with jpeg:size (0.057 s) were faster in the same run and filter properly. Against fast_image_resize, Pillow-SIMD or MagicScaler it trades quality for not decoding at full resolution, so it only wins when the source is far larger than the thumbnail.

## Integration

| | |
|---|---|
| **Form** | C static or shared library (autotools, or CMake 3.0+ with BUILD_STATIC_LIB / BUILD_SHARED_LIB / BUILD_PROGRAM) plus an optional epeg command-line tool |
| **Dependencies** | libjpeg (any IJG-API implementation such as libjpeg-turbo), libexif, libm; open PR #31 (2025, unmerged) would make libexif optional |
| **Minimum toolchain** | Plain C with POSIX headers (unistd.h, sys/stat.h, setjmp.h); autoconf 2.52+ and automake 1.6+, or CMake 3.0+; Windows builds through CMake since the April 2023 commits |
| **Platforms** | Linux and other Unix-likes; Windows via CMake (WIN32 fixes from 2023); any CPU libjpeg supports |
| **Thread safety** | Not documented. Separate Epeg_Image handles are independent except for the file-static exif_byte_order, which every open writes and every encode reads, so concurrent opens and encodes race on the byte order used for the output Orientation tag. |
| **Drop-in for the baseline** | no |

## Gotchas

- The CLI ignores epeg_encode's return value and always exits 0, so scripts (and the speedtest-resize harness, which also counts the time of failed runs) cannot detect a failed thumbnail.
- The CLI always enables thumbnail comments, so every output carries APP7 markers with 'Thumb::URI file://&lt;input path&gt;' and the source mtime, plus an EXIF APP1 block; strip them before publishing if paths are sensitive. With memory input and thumbnail comments enabled, _epeg_encode writes the uninitialised stack buffer buf as the first APP7 marker (bug).
- The decode colour space defaults to EPEG_RGB8 (EPEG_GRAY8 or EPEG_CMYK for those sources), although the epeg_decode_colorspace_set comment says the default is EPEG_YUV8; the CLI therefore converts YCbCr to RGB and back. Call epeg_decode_colorspace_set(im, EPEG_YUV8) to avoid both conversions.
- epeg_encode tears down the decoder and closes the input (issue #20), so a handle produces one output; the library default quality is 75, the CLI's is 85, and quality 90 or higher switches the output to 4:4:4 sampling.

## Known shortcomings

- Not faster than the incumbent's fast path: in the same fawick/speedtest-resize table ImageMagick's own -define jpeg:size=300x300 -thumbnail beats epeg (0.057 s vs 0.079 s; vips 0.070 s also faster; unnamed i7 3.4 GHz, Ubuntu 16.10, no versions). The 7.2x is only against plain convert -resize, which decodes the full 5616x3744 image and runs a convolution filter, while epeg does a 1/8 DCT-scaled decode (JDCT_IFAST) plus nearest neighbour. Licence MIT-enna (not OSI approved), usability reference.
- speedtest-resize times failed runs without checking output and the epeg CLI always exits 0 (the return of epeg_encode is ignored). Code bugs not behind the numbers: an uninitialised buf APP7 marker on memory input; a static exif_byte_order thread race; an unchecked 32-bit malloc size product (possible wrap past 1.4 gigapixels at scale 1, untested); the default colourspace is RGB8 although the docs say YUV8 (two needless conversions). The CLI embeds a Thumb::URI file path plus mtime in every thumbnail; ICC profiles are dropped (#26); thumbnails larger than half the source get a full decode.

## Caveats and trade-offs

Equivalent-work comparison fails: in the same speedtest-resize table ImageMagick's own thumbnail command ('convert -define jpeg:size=300x300 -thumbnail 150x150&gt;'), which uses the same libjpeg DCT-domain downscale, takes 0.057 s per file against epeg's 0.079 s, and the vips binding takes 0.070 s. epeg only beats 'convert -resize 150x150&gt;', which decodes the full 5616x3744 image and runs a convolution resize, while epeg decodes at 1/8 scale (JDCT_IFAST, no fancy upsampling) and then nearest-neighbour samples to 150x100, so it does much less work and gives a lower-quality thumbnail. The numbers are one pass over 10 files by a contributor (nono) on an unnamed Core i7 with process start-up included and no tool versions. The licence is the Enlightenment MIT variant (MIT-enna) with a public-acknowledgment clause, which is not OSI-approved. mattes/epeg is a maintained copy of Enlightenment's epeg, not a GitHub fork.

JPEG only; reduces size by decoding only the DCT coefficients needed (libjpeg scaled decode), so quality is that of DCT-domain scaling rather than a Lanczos or bicubic resample; speedup is proportional to the pixel-count ratio between source and thumbnail.

## Maintenance

Abandoned: the last commits (2023-03-30 to 2023-04-05) added CMake and Windows builds, orientation get/set and a memory-leak fix in epeg_close; 6 issues and 2 pull requests (one from 2015) are open and there are no releases beyond Enlightenment's v0.9.1.042. The Enlightenment MIT variant requires public acknowledgment when source is not shipped, which keeps it a reference entry, though the single C file is easy to read or vendor if that licence is acceptable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): reject; tier before verification B, tier now C.
- **Tier reason:** speedtest-resize is an independent harness with public code (main.go, exec.go), but the epeg row comes from a single contributor pass on an unnamed 'Intel Core i7 3.4GHz' with no tool versions. Its only win is over 'convert -resize', which decodes the full 5616x3744 image and runs a convolution filter, while epeg decodes at 1/8 scale in the DCT domain and point-samples; against the equivalent ImageMagick mode (-define jpeg:size=300x300 -thumbnail) epeg is slower, so the faster-than-ImageMagick claim fails and the evidence is C at most if kept.
- **Verifier notes:** Plainly: epeg loses to ImageMagick's -thumbnail with the jpeg:size hint in the same table (0.079 s vs 0.057 s per file) and to the vips binding (0.070 s); its 7.2x over 'convert -resize' comes from doing much less work (1/8-scale DCT decode with JDCT_IFAST, then nearest-neighbour sampling). If the orchestrator keeps it under the keep-and-document rule, use tier C, usability reference and the corrected caveats. Repo metadata checked on github.com: 274 stars, not a fork, not archived, last commit 2023-04-05 (abandoned).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `baseline`, `hardware`, `license`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/fawick/speedtest-resize>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/README.md>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/main.go>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/exec.go>
  - <https://github.com/mattes/epeg>
  - <https://github.com/mattes/epeg/commits/master>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/README.md>
  - <https://raw.githubusercontent.com/mattes/epeg/master/src/lib/epeg_main.c>
  - <https://raw.githubusercontent.com/mattes/epeg/master/src/bin/epeg_main.c>
  - <https://raw.githubusercontent.com/mattes/epeg/master/COPYING>
  - <https://raw.githubusercontent.com/mattes/epeg/master/COPYING-PLAIN>
- **Sources the enricher read:**
  - <https://github.com/mattes/epeg>
  - <https://github.com/mattes/epeg/commits/master>
  - <https://github.com/mattes/epeg/issues?q=is%3Aissue>
  - <https://github.com/mattes/epeg/pulls>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/README.md>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/COPYING>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/COPYING-PLAIN>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/AUTHORS>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/Makefile.am>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/src/lib/Makefile.am>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/src/lib/Epeg.h>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/src/lib/epeg_private.h>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/src/lib/epeg_main.c>
  - <https://raw.githubusercontent.com/mattes/epeg/HEAD/src/bin/epeg_main.c>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/README.md>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/main.go>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/exec.go>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/mattes/epeg`) · [data/wave10/enrich/raw/github_com_mattes_epeg.json](../../../data/wave10/enrich/raw/github_com_mattes_epeg.json) (enrichment confidence 0.8)

</details>
