# ccv (BBF face detector)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Computer vision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Brightness Binary Feature frontal face detector in the C library ccv; about 3x faster than OpenCV's 2.x-era Haar detector, now self-deprecated.

| | |
|---|---|
| **Beats** | OpenCV default frontal face detector (Haar cascade, default settings; OpenCV version not stated) |
| **Claimed result** | bbfdetect real 0m9.304s versus OpenCV default face detector real 0m27.977s on the same machine (about 3.0x faster, derived from page data); the SCD doc states OpenCV is about 3 times slower than BBF with a single-thread setup. Accuracy trade: BBF 82.97% detection with 12 false alarms versus OpenCV 86.69% with 15 false alarms. |
| **Workload** | Run ccv's bbfdetect and OpenCV's face detector over the CMU frontal face test sets A, B and C (converted to PNG, file list of images) on the same computer, timed with `time`. |
| **Metric** | throughput |
| **Hardware** | Author's own computer, CPU not stated |
| **Adoption** | 7.2k stars |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/liuliu/ccv) · [benchmark](https://raw.githubusercontent.com/liuliu/ccv/HEAD/doc/bbf.rst) |

## Verdict

doc/bbf.rst reports one `time ./bbfdetect filelist.txt ../samples/face` run over the CMU/MIT frontal test sets A, B and C converted to PNG taking 9.3 s, versus 28.0 s for an unnamed OpenCV face-detection program at default settings on the same unnamed computer (about 3.0x, derived from page data), with both timings including image decoding and output and no compiler, flags or OpenCV version stated. doc/scd.rst separately says OpenCV is about 3 times slower than BBF single-threaded and that BBF takes 182 ms versus SCD's 381 ms on addams-family.png; the matching accuracy trade on the CMU sets is 82.97% (12 false alarms) for BBF versus 86.69% (15) for OpenCV.

## Use it when

- Legacy or embedded frontal-face detection where a small dependency-free C detector matters more than accuracy, for example as a cheap pre-filter before a stronger model.
- Grayscale images whose shorter side is at least 48 pixels with faces of 24x24 pixels or larger in roughly upright, frontal pose.
- Browser or JavaScript use through the bundled js/ccv.js port, which ccv's own docs describe as the derivative that runs semi-real-time in JavaScript.
- Single-threaded CPU budgets where you can trade some detection rate for speed by setting accurate = 0.

## Skip it when

- Any new project that needs accuracy: the author marks BBF deprecated ('no longer considered either fast or accurate') and on FDDB at about 250 false positives it reaches 66.27% versus 72.93% for ccv's own SCD detector; modern CNN detectors are far stronger.
- Profile, rotated or small faces: the shipped cascade is frontal only, and images with a shorter side under 48 pixels return no detections at the default 24x24 size.
- When you need OpenCV compatibility: it cannot load OpenCV Haar or LBP XML cascades and uses ccv's own matrix and array types.
- ARM or mobile real-time targets expecting SIMD: the detection loop is scalar C, and issue #126 reports ccv's SCD detector at about 1 Hz on an iPhone 5s because its SSE2 paths lack NEON equivalents.
- Projects that must stay strictly BSD without auditing the build: the default configure links GPL FFTW3 and GSL when their headers are present.

## How it is fast

Each weak feature compares up to 8 'positive' and 8 'negative' pixel intensities taken from three pyramid levels (full, half and quarter resolution) and fires only if every positive pixel is brighter than every negative one, exiting at the first violation; there is no integral image or variance normalization, only byte loads and compares (Brightness Binary Feature, after Abramson and Steux's YEF and Huang et al.'s rotation-invariant multiview detector). Boosted stages form an early-reject cascade, the pyramid has 6 scales per octave (interval 5) built by area resampling plus 2x downsampling, and windows are scanned on a 4-pixel grid with 4 phase offsets in accurate mode (a 2-pixel effective stride); accurate = 0 keeps one offset, which the header says is about 3 times faster.

## Compared with alternatives

No siblings catalogued yet; within ccv itself, SCD (scddetect with samples/face.sqlite3) is the maintained replacement, about 2x slower than BBF on the doc's example image (381 ms vs 182 ms) but about 6.7 points better on FDDB at about 250 false positives.

## Integration

| | |
|---|---|
| **Form** | static lib (libccv.a via ./configure and make in lib/; Bazel BUILD and Package.swift also present) |
| **Dependencies** | none required for BBF detection; libpng and libjpeg optional for image reading; GSL (GPL) needed only for bbfcreate training; libccv.a also compiles the bundled NNC deep-learning code, SQLite, kissfft, dSFMT/SFMT and siphash |
| **Minimum toolchain** | C99 compiler (designated initializers); default build flags -O3 -ffast-math -march=native -msse2 on x86 |
| **Platforms** | macOS, Linux, FreeBSD, Windows (marked with an asterisk in the README), iOS, Android, Raspberry Pi; CI on Linux x64, macOS ARM64 and Raspberry Pi 4 |
| **Thread safety** | not documented; detection only reads the cascade and ccv's matrix cache is thread-local (__thread), so concurrent calls on separate images appear safe from the code |
| **Drop-in for the baseline** | no |

## Gotchas

- Accuracy did not reproduce for an outside user: issue #61 reports 53.82% detection with 30 false alarms on the same CMU test sets versus the documented 82.97% (12), and it was closed with no visible maintainer explanation; the speed table has the same single-run, unnamed-OpenCV harness.
- Default build is not portable or license-neutral: configure adds -march=native unless --with-arch is given, compiles with -ffast-math, and links FFTW3 and GSL (both GPL) whenever their headers exist; pass --disable-fftw3 --disable-gsl to keep the binary BSD-only.
- ccv_bbf_detect_objects has no input-size guard: an image whose shorter side is under 48 pixels yields zero scales and no detections at the default 24x24 size, and one under 24 pixels feeds log(0) into the pyramid-depth computation that sizes an alloca (undefined behaviour).
- The trained cascade in samples/face is CC BY 4.0 (attribution required), not BSD, and BBF's windows sit on a 2-pixel grid per scale (4 pixels with accurate = 0), so box localization is coarse; the doc's validator also needs result paths hand-edited with sed before scoring.

## Known shortcomings

- doc/bbf.rst says the BBF detector is deprecated and 'no longer considered either fast or accurate' although the code is still in the repo; OpenCV version and program not named, no CPU or flags; 9.304 s vs 27.977 s is about 3.0x (derived from page data). Docs, samples and trained models are CC BY 4.0, code BSD-3-Clause. Filed under media-and-graphics/computer-vision (new category) by override although mined into wave 1.
- Enricher: an outside user reproduced 53.82% (30 false positives) instead of the documented 82.97% (12) for the BBF detector (issue #61, closed without a maintainer reply); the speed claim is one `time` run against an unnamed OpenCV program. No input-size guard (shorter side under 48 px gives no detections, under 24 px a log(0) alloca is UB). Build defaults to -march=native and -ffast-math and auto-links GPL FFTW3/GSL. BBF is self-deprecated and untouched.
- Re-found by the wave 10 seed backfill (w10-mine-f) with the same first-party doc/bbf.rst evidence (BBF face detector 9.304 s vs OpenCV 27.977 s on the MIT+CMU sets, no CPU or flags); no new evidence.

## Caveats and trade-offs

doc/bbf.rst opens with a Deprecated notice: BBF 'is no longer considered either fast or accurate' for face detection as of libccv 0.7 and was to be removed after 0.7 in favour of SCD; the code (lib/ccv_bbf.c, bin/bbfdetect.c) is still in the repo. The speed numbers are a first-party doc from the OpenCV 2.x era with no CPU model, compiler or flags and no script beyond the shown shell commands, so the tier stops at C. The timed run includes image decoding and output for both programs, the OpenCV program and version are not named, and OpenCV ran with default settings, not necessarily equivalent to bbfdetect's scale and neighbour parameters. Accuracy trade on CMU test sets A/B/C: BBF 82.97% with 12 false alarms versus OpenCV 86.69% with 15; on FDDB (doc/scd.rst) at about 250 false positives BBF reaches 66.27% versus OpenCV frontal 45.18%. doc/scd.rst also reports SCD about 2x slower than BBF (addams-family.png 381 ms vs 182 ms) and OpenCV about 3x slower than BBF single-threaded. ccv's dpm.rst shows OpenCV's HOG pedestrian detector 4.34 times faster than ccv's DPM, and the convnet doc says it chooses correctness over speed, so the claim covers only the BBF face detector. Licence: code BSD-3-Clause (COPYING), but ./doc, ./samples (including the trained face cascade) and ./site are CC BY 4.0; bundled kissfft (BSD) and metal-cpp (Apache-2.0).

BBF detector is lower on detection rate (82.97% vs 86.69% at similar false alarms), and ccv's own FDDB comparison puts OpenCV's frontal detector at 45.18% against BBF at 66.27% at about 250 false positives; C library with a minimal dependency footprint; the source is BSD-3-Clause but the model data and documentation are CC BY 4.0.

## Maintenance

The repository is active (commits on 2026-10-07) but the work is in the NNC deep-learning code, none of the latest commits touch BBF, and the doc has declared BBF deprecated since libccv 0.7; the BSD-3-Clause code (lib/ccv_bbf.c plus ccv's matrix, resample and array core) remains copyable, with the face cascade under CC BY 4.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/bbf.rst gives first-party `time` output for bbfdetect (real 0m9.304s) versus OpenCV's default face detector (real 0m27.977s) on the author's computer, with no CPU model, compiler, flags, OpenCV version or OpenCV program; the bbfdetect side is public (bin/bbfdetect.c) but the method is partial, so C.
- **Verifier notes:** Numbers match doc/bbf.rst exactly (about 3.0x derived from page data) and the 3x statement is in doc/scd.rst. Metadata via github.com: 7.2k stars, not archived or a fork, default branch unstable, last commit 2026-10-07. Main shortcoming to record: BBF is self-declared deprecated ('no longer considered either fast or accurate'), and the benchmark is an undocumented single `time` run against an unnamed OpenCV build.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** current detector benchmark against OpenCV with versions; enricher code reading; backfill w10-mine-f
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/doc/bbf.rst>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/doc/scd.rst>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/COPYING>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/lib/ccv_bbf.c>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/bin/bbfdetect.c>
  - <https://github.com/liuliu/ccv>
  - <https://github.com/liuliu/ccv/commits/unstable>
- **Sources the enricher read:**
  - <https://github.com/liuliu/ccv>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/README.rst>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/doc/bbf.rst>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/doc/scd.rst>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/lib/ccv_bbf.c>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/lib/ccv.h>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/lib/ccv_memory.c>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/lib/configure.ac>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/lib/config.mk.in>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/lib/makefile>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/bin/makefile>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/bin/bbfdetect.c>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/bin/scddetect.c>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/js/ccv.js>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/js/face.js>
  - <https://raw.githubusercontent.com/liuliu/ccv/HEAD/COPYING>
  - <https://github.com/liuliu/ccv/tree/unstable/samples>
  - <https://github.com/liuliu/ccv/commits/unstable>
  - <https://github.com/liuliu/ccv/issues?q=is%3Aissue+bbf>
  - <https://github.com/liuliu/ccv/issues/152>
  - <https://github.com/liuliu/ccv/issues/61>
  - <https://github.com/liuliu/ccv/issues/126>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/liuliu/ccv`) · [data/wave1/enrich/raw/github_com_liuliu_ccv.json](../../../data/wave1/enrich/raw/github_com_liuliu_ccv.json) (enrichment confidence 0.75)

</details>
