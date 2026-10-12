# Leptonica

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> BSD-licensed C image-analysis library for document images; its projection-profile deskew was reported 30-40x faster than ImageMagick -deskew.

| | |
|---|---|
| **Beats** | ImageMagick convert -deskew |
| **Claimed result** | Standalone deskew: "around 30-40x faster" than ImageMagick's convert -deskew (PR author's claim, no per-file times). Whole deskew+OCR job: 371 seconds with ImageMagick baseline versus 216 seconds with Leptonica doing the deskew, about 40% less total time. |
| **Workload** | Skew detection and deskew of a 'mixed bag' of scanned page files inside OCRmyPDF's pre-processing, Leptonica versus ImageMagick convert -deskew; also the whole deskew plus Tesseract OCR job. |
| **Metric** | latency |
| **Adoption** | 2.1k stars; used by Tesseract, OpenCV (optional) and jbig2enc per its README |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/DanBloomberg/leptonica) · [benchmark](https://github.com/fritz-hh/OCRmyPDF/pull/61) |

## Verdict

One third-party pull request (jbarlow83, OCRmyPDF PR #61, January 2014, never merged) reports Leptonica deskew '30-40x faster' than ImageMagick convert -deskew on its own, and 216 s versus 371 s (about 40% less) for deskew plus Tesseract OCR on 'a mixed bag of files', with no hardware, versions, file list or per-file times; the ImageMagick side was a separate convert process while Leptonica ran in-process through ctypes, and the two tools do different amounts of work (Leptonica scores reduced binary images, ImageMagick, in its current MagickCore/shear.c, a full-resolution Radon transform; the 2014 build's code was not read), so the ratio is algorithmic and unreproduced.

## Use it when

- Deskewing scanned text pages (OCR pre-processing, archival scanning) where the skew is small (default search +/-7 degrees) and throughput per page matters.
- Pipelines already linking Tesseract, which depends on Leptonica, so the deskew, binarization and background-normalization calls cost no new dependency.
- Batch document work on 1 bpp or grayscale images where you also need connected components, morphology, page segmentation or JBIG2-style classification from one library.
- C or C++ projects that want a permissive (BSD-2-Clause), actively maintained, fuzzed library rather than shelling out to ImageMagick.

## Skip it when

- Pages skewed by more than about 7 degrees: the default sweep misses them (maintainer in issues #622 and #644); widen sweeprange in pixDeskewGeneral at extra cost, and angles near 90 degrees fail because the method uses shears.
- Photographs or images with many strong straight lines that are not text lines, which can mislead the projection score (maintainer in #644); the method assumes text baselines.
- Resampling-quality or throughput work on natural images (resize, colour conversion): Leptonica has no SIMD paths in the files read, and the catalogued SIMD resizers and converters are the better pick.
- Expecting the 30-40x figure to hold today: it is a 2014 anecdote against an ImageMagick binary launched as a subprocess, and OCRmyPDF, the project it was measured for, later dropped Leptonica (v13.0.0 release notes) for ABI and platform-loading reasons, computing the angle with Tesseract and rotating with Pillow instead.

## How it is fast

Skew is found with a projection-profile method (Postl's differential line-sum variance): the 1 bpp page is vertically sheared rather than rotated for each trial angle, black pixels are summed per raster line, and the score is the sum of squared differences between adjacent line sums. A coarse sweep runs on a 4x rank-reduced binary image (default +/-7 degrees in 1 degree steps, peak refined by quadratic fit) and an interval-halving search then runs at 2x reduction down to 0.01 degrees, so very few full-resolution pixels are touched. Binary images are packed into 32-bit words and shears and reductions work word-at-a-time; no SIMD intrinsics or OpenMP appear in skew.c, rotate.c or rotateshear.c. ImageMagick's DeskewImage, by contrast, computes a full-resolution fast Radon transform (MagickCore/shear.c RadonTransform, not a Hough transform as the PR said) over a thresholded copy of the whole image before an affine resample.

## Compared with alternatives

Pick Leptonica over OpenCV, libvips or ImageMagick-class tools when the job is document-page skew detection and binarization, which it does in one call with a text-specific algorithm; pick OpenCV, libvips or the SIMD resizers such as fast_image_resize for natural-image resampling and colour conversion, where Leptonica has no measured advantage.

## Integration

| | |
|---|---|
| **Form** | shared or static lib (CMake, autotools or sw); also packaged in vcpkg and most Linux distributions |
| **Dependencies** | none required; optional zlib, libpng, giflib 5, libjpeg, libtiff, libwebp (webpmux) and OpenJPEG for image formats (each switchable with a CMake ENABLE_\* option) |
| **Minimum toolchain** | C11 (CMAKE_C_STANDARD 11 required), CMake 3.10+ |
| **Platforms** | Linux, macOS, MinGW, Cygwin, Windows per README; CI badges for CMake on Linux, Win64 and autotools on macOS; endian-independent |
| **Thread safety** | README says thread-safe via atomic reference counting (C11 stdatomic l_atomic, falling back to plain int when atomics are unavailable); message severity (LeptMsgSeverity) and the stderr handler are process-global |
| **Drop-in for the baseline** | partial — same job as convert -deskew but a C API (pixDeskew and friends) instead of a CLI flag; results differ (no auto-crop, different rotation filter, deskew skipped below 0.1 degree or low confidence) |

## Gotchas

- pixDeskew and pixDeskewGeneral silently return an unrotated clone when the angle is under 0.1 degree, the confidence (max/min score ratio) is under 3.0, or the search fails; read the pangle/pconf outputs to tell 'no skew' from 'gave up'.
- pixDeskewGeneral calls pixRotate with width and height 0, so the output keeps the input size and corner content rotated outside the frame is clipped, with white brought in; 1 bpp images rotate by shear, other depths by area mapping (colormaps removed).
- Only binary images are scored: colour and gray input is thresholded at 160 by default (or adaptive with thresh -1, via pixFindSkewAdaptAndDeskew), so light-on-dark or inverted text can yield a wrong angle (maintainer in #622).
- Error reporting goes to stderr through a global severity level; bindings such as OCRmyPDF's old ctypes/CFFI wrapper had to trap stderr and later needed a thread lock for Leptonica before 1.79 (OCRmyPDF v10.3.0 notes). Image-format parsers have had fuzzing CVEs (CVE-2020-36277 to 36281, fixed in 1.80.0, snippet only), so keep the library current when reading untrusted files.

## Known shortcomings

- Single 2014 third-party anecdote (OCRmyPDF PR #61, closed unmerged): deskew 30-40x faster than ImageMagick convert -deskew, whole job 371 s to 216 s, no method, hardware or versions; the win is algorithmic (Postl projection profile vs Hough).
- Enricher: ImageMagick's DeskewImage uses a full-resolution Radon transform (MagickCore/shear.c RadonTransform), not Hough as the OCRmyPDF PR said; Leptonica sweeps a 4x-reduced binary image then binary-searches at 2x, so the measured work differs and the gain is algorithmic; default search only +/-7 degrees (#622, #644); silent clone below 0.1 degree or confidence under 3.0; corners clipped. OCRmyPDF dropped Leptonica in v13.0.0 for ABI and platform reasons, not speed.

## Caveats and trade-offs

Third-party contributor's pull-request comment and commit message (jbarlow83, OCRmyPDF PR #61, opened 2014-01-20 against fritz-hh's v2.x branch, closed unmerged 2015-07-28). No hardware, no Leptonica/ImageMagick/Tesseract versions, no commands, no file set beyond 'a mixed bag of files', no repeat counts; the PR only says the change was tested (functionally) on OS X 10.9 and Ubuntu 13.10. The commit message attributes the gap to the algorithm: ImageMagick finds the skew angle with a Hough transform, Leptonica with Postl's variance of differential line sums, so the gain is algorithmic rather than implementation speed; the PR also notes ImageMagick sometimes adds a halftone pattern after rotation. ImageMagick ran as the convert binary from OCRmyPDF v2's script while Leptonica was called through a ctypes wrapper, so process-launch overhead is probably part of the ImageMagick side (not stated). The 30-40x figure has no per-file times; the 371 s and 216 s figures include OCR time, so the end-to-end gain is about 40%. Leptonica's own docs claim DWA morphology is 3-4x faster than its own rasterop morphology (an internal comparison, not recorded as a baseline). No comparison against OpenCV or other image libraries was found. Category set to color-and-resampling because the measured operation is skew detection plus rotation, though Leptonica is a general image-analysis library (guessed category was image-codecs). [retier] ImageMagick DeskewImage = full-resolution Radon transform (MagickCore/shear.c); Leptonica sweeps a 4x-reduced binary image then refines at 2x; default search +/-7 degrees (#622, #644); silent no-op below 0.1 degree or confidence under 3.0; corners clipped; single 2014 anecdote, PR #61 closed unmerged; OCRmyPDF later dropped Leptonica for ABI reasons.

ANSI C library with packed 32-bit-word image data and 1 bpp document-image focus. The deskew speed comes from a cheaper algorithm (Postl's variance of differential line sums) than ImageMagick's Hough transform, so it targets text pages and is not a general-purpose equivalent. The PR author also reports Leptonica gave better output (ImageMagick sometimes added a halftone pattern to the background after rotation).

## Maintenance

Actively maintained (1.87.0 released 2025-12-24, 1.88.0 in progress, commits into October 2026), BSD-2-Clause, fuzzed in OSS-Fuzz per its README, and safe to depend on; the speed claim itself is a single 2014 anecdote.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** OCRmyPDF PR #61 (jbarlow83, 2014-01-20) states 371 s vs 216 s for deskew+OCR on 'a mixed bag of files' and that Leptonica's deskew is '30-40x faster' than ImageMagick convert -deskew standalone; no hardware, versions, commands, file set or benchmark code, so numbers without methodology (C).
- **Verifier notes:** PR #61 page confirms the 371 s / 216 s (about 40% less total deskew+OCR time) and '30-40x faster' standalone deskew claims verbatim; metadata checked: 2.1k stars, 433 forks, BSD-2-Clause (leptonica-license.txt), last commit 2026-10-02, not archived. Shortcomings: single 2014 anecdote from a third party with no methodology, algorithmic rather than implementation win, probable subprocess overhead on the ImageMagick side, PR never merged.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-113 (wave 10); enricher w10 pair-026
- **Pages the verifier opened:**
  - <https://github.com/fritz-hh/OCRmyPDF/pull/61>
  - <https://github.com/DanBloomberg/leptonica>
  - <https://github.com/DanBloomberg/leptonica/commits>
  - <https://raw.githubusercontent.com/DanBloomberg/leptonica/HEAD/leptonica-license.txt>
- **Sources the enricher read:**
  - <https://github.com/DanBloomberg/leptonica>
  - <https://raw.githubusercontent.com/DanBloomberg/leptonica/HEAD/README.md>
  - <https://raw.githubusercontent.com/DanBloomberg/leptonica/HEAD/version-notes.html>
  - <https://raw.githubusercontent.com/DanBloomberg/leptonica/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DanBloomberg/leptonica/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/DanBloomberg/leptonica/HEAD/src/skew.c>
  - <https://raw.githubusercontent.com/DanBloomberg/leptonica/HEAD/src/rotate.c>
  - <https://raw.githubusercontent.com/DanBloomberg/leptonica/HEAD/src/rotateshear.c>
  - <https://raw.githubusercontent.com/DanBloomberg/leptonica/HEAD/src/environ.h>
  - <https://github.com/DanBloomberg/leptonica/issues?q=is%3Aissue+skew>
  - <https://github.com/DanBloomberg/leptonica/issues/644>
  - <https://github.com/DanBloomberg/leptonica/issues/622>
  - <https://github.com/fritz-hh/OCRmyPDF/pull/61>
  - <https://github.com/jbarlow83/OCRmyPDF/blob/v15.4.0/docs/release_notes.rst>
  - <https://raw.githubusercontent.com/ImageMagick/ImageMagick/HEAD/MagickCore/shear.c>
  - WebSearch: OCRmyPDF deskew leptonica removed release notes (snippets)
  - WebSearch: leptonica CVE heap buffer overflow fixed version (security-tracker.debian.org and mageia snippets only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/danbloomberg/leptonica`) · [data/wave10/enrich/raw/github_com_danbloomberg_leptonica.json](../../../data/wave10/enrich/raw/github_com_danbloomberg_leptonica.json) (enrichment confidence 0.75)

</details>
