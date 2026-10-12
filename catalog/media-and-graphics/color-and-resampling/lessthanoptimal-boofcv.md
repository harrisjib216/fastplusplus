# BoofCV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Pure-Java computer vision library; the author's 2019 run beat OpenCV-Python on corners, histogram and Sobel but lost on blur and Canny.

| | |
|---|---|
| **Beats** | OpenCV (opencv-python 4.5.1.48 pip wheel, CPU) |
| **Claimed result** | Mixed result, ratios derived from page data (OpenCV ms divided by BoofCV ms, from the two readme example outputs, both dated 2019-03-21). BoofCV faster: good features 38.313 ms vs 277.2 ms (7.2x), Hough polar 743.051 ms vs 3086.3 ms (4.2x, not like-for-like, see caveats), histogram 2.268 ms vs 7.0 ms (3.1x), external contour 47.055 ms vs 83.3 ms (1.8x), Sobel 8.010 ms vs 14.0 ms (1.7x). BoofCV slower: Gaussian blur 36.139 ms vs 12.1 ms (OpenCV 3.0x faster), Canny 142.658 ms vs 61.7 ms (OpenCV 2.3x faster), local mean threshold 20.495 ms vs 15.4 ms (OpenCV 1.3x faster). No OpenCV row for SIFT or SURF (the 2019 run printed 'Skipping SIFT and SURF. Not installed'). |
| **Workload** | SpeedTestCV example output on one large chessboard JPEG (gray) and one binary PNG: BoofCV 0.33.1 under JMH (avgt, 5 iterations, ms/op, concurrency on) against OpenCV 4.0.0.21 Python calls timed by a script (ms per call, multi-threaded as shipped). Operations: Gaussian blur radius 5, Sobel, local mean threshold radius 5, histogram, Canny edge chains, external contours, Shi-Tomasi corners, polar Hough lines. |
| **Metric** | latency |
| **Compiler and flags** | The two example outputs were written in commit 0bd58bd (2019-03-21) and never re-run: BoofCV 0.33.1 (build.gradle at that commit) under JMH 1.19, 3 warm-up and 5 measurement iterations, 1 fork, BoofConcurrency.USE_CONCURRENT=true; OpenCV side opencv-python and opencv-contrib-python 4.0.0.21 with numpy 1.16.2 (requirements.txt at that commit), timed by opencv/benchmark.py as the mean of 10 time.time() trials (1 for histogram). The current build.gradle (0.38-SNAPSHOT, JDK 14 source level) and requirements.txt (4.5.1.48) were bumped in March 2020/2021 commits that changed only the run commands and the SIFT prose, not the numbers. JDK version not stated beyond 'JDK 1.8 and JDK 11 produce similar output'. |
| **Adoption** | 1.2k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/lessthanoptimal/BoofCV) · [benchmark](https://github.com/lessthanoptimal/SpeedTestCV/blob/master/boofcv/readme.md) |

## Verdict

The author's SpeedTestCV example outputs, both written on 2019-03-21 and never re-run, time BoofCV 0.33.1 under JMH (3 warm-up and 5 measured iterations, concurrency on) against opencv-python 4.0.0.21 timed by a Python loop (mean of 10 calls, multithreaded as shipped) on a 3648x2736 chessboard photo and a binary PNG, on unstated hardware. BoofCV led on Shi-Tomasi corners (7.2x), Hough (4.2x), histogram (3.1x), external contours (1.8x) and Sobel (1.7x), and trailed on Gaussian blur (OpenCV 3.0x), Canny (2.3x) and mean threshold (1.3x); the Hough, contour and Sobel wins compare different work.

## Use it when

- JVM or Android applications that need computer vision without JNI or native OpenCV binaries (pure Java; a boofcv-android module exists).
- Fiducial markers, QR codes, camera calibration or structure from motion inside a Java stack, where BoofCV offers ready-made pipelines.
- Long-running, many-frame pipelines on the JVM that reuse output buffers, so JIT warm-up and allocation are amortised as in the JMH numbers.
- Shi-Tomasi corners, histograms or gradient images on large grayscale frames, where the 2019 run had BoofCV ahead of opencv-python (with the caveats below).

## Skip it when

- Gaussian blur, Canny edges or local mean thresholding: OpenCV was 3.0x, 2.3x and 1.3x faster in the same author run.
- Colour conversion or resampling: no row of the benchmark measures either, so nothing supports placing it in this category; the native siblings (fast_image_resize, kornia-rs, libvips, Pillow-SIMD) have like-for-like numbers.
- C, C++ or Python projects: using it means embedding a JVM; there is no native build.
- Short-lived or cold-start workloads: the JMH figures exclude JIT warm-up, which a one-shot command-line call pays.
- When outputs must match OpenCV bit for bit: RGB-to-gray is a plain average by default and Gaussian blur rounds where OpenCV truncates, per the SpeedTestCV notes.

## How it is fast

Image operations come as type-specialised variants produced by a code generator (the build has an explicit autogenerate step), and hot operations have multithreaded implementations (for example ImplThresholdImageOps_MT) selected through the global BoofConcurrency.USE_CONCURRENT switch. Processor objects reuse preallocated output images instead of allocating per call. Some of the measured wins come from doing less work rather than faster kernels: its Hough polar detector votes only with gradient edges above a threshold, and its contour finder is an external-only linear-time tracer.

## Compared with alternatives

Pick BoofCV only when you are on the JVM and want a whole pure-Java vision stack; for colour conversion or resizing speed, fast_image_resize and kornia-rs carry like-for-like measurements, and OpenCV (also catalogued) won blur, Canny and thresholding in BoofCV's own comparison.

## Integration

| | |
|---|---|
| **Form** | Java library jars on Maven Central (org.boofcv:boofcv-core plus optional modules such as boofcv-swing, boofcv-ffmpeg, boofcv-javacv, boofcv-android, boofcv-kotlin) |
| **Dependencies** | EJML, GeoRegression, DDogleg, DeepBoof and args4j for the core; optional bytedeco FFmpeg and JavaCV native binaries (platform-specific, no longer bundled by default since 1.5.0) for the integration modules |
| **Minimum toolchain** | Java 11 or newer to run (README); building from source uses the bundled Gradle wrapper with an autogenerate step |
| **Platforms** | any JVM platform (desktop, server, Android); native code only in the optional FFmpeg and JavaCV modules |
| **Thread safety** | not documented in what was read; multithreading is a global switch (BoofConcurrency.USE_CONCURRENT) that the benchmark notes must be set before filters are constructed, and processor objects hold their own output and work buffers |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the Sobel row (read this session in opencv/benchmark.py, unchanged since 2019): OpenCV is called with ksize=1, which OpenCV defines as a 3x1/1x3 derivative kernel with no smoothing, while BoofCV computes the 3x3 Sobel; OpenCV also allocates two new CV_16S outputs per call while BoofCV writes into preallocated images, so the 1.7x compares different operators and memory handling.
- Harness flaw in the contour row: BoofCV thresholds binary.png with down=true, so dark pixels (38.9% of the 3648x2736 image) are foreground, while OpenCV traces the non-zero white pixels (61.1%) and is asked for RETR_CCOMP (outer and hole contours) against BoofCV's external-only finder; the two sides trace complementary regions, so the 1.8x is not like-for-like.
- The 4.2x Hough row is an artefact: essentially every pixel of the grayscale chessboard photo is non-zero (checked this session), so OpenCV's HoughLines votes with all \~10 million pixels at 180 angles, whereas BoofCV votes only with gradient edges above 50. The OpenCV histogram row is a single cold call against a JMH average, and BoofCV's threshMean error (plus or minus 9.822 ms on 20.495 ms, about 48%) makes that row noise.
- BoofConcurrency.USE_CONCURRENT is global state read at construction time: filters created before it is set keep the old threading mode.

## Known shortcomings

- Both SpeedTestCV outputs were written in commit 0bd58bd (2019-03-21) and never re-run, so they measure BoofCV 0.33.1 against opencv-python 4.0.0.21; no hardware stated; BoofCV timed with JMH while OpenCV used a Python time.time() loop; the Hough row is not like for like (OpenCV HoughLines runs on the raw grey image); OpenCV is faster on blur, Canny and mean threshold. Java library, loose fit in color-and-resampling.
- Enricher (SpeedTestCV code): the Sobel row runs OpenCV with ksize=1 (1x3 central difference, no smoothing) against BoofCV's 3x3 Sobel and OpenCV allocates two outputs per call; the contour row has BoofCV thresholding dark pixels (38.9%) as foreground while OpenCV traces white (61.1%) with RETR_CCOMP against an external-only finder, so the regions are complementary; the Hough row runs on a 3648x2736 chessboard greyscale that is about 100% non-zero, so OpenCV votes with about 10M pixels; the histogram OpenCV figure is a single cold call; the threshMean error (plus or minus 9.822 on 20.495 ms) is noise. So the Hough, contour and Sobel wins are not like for like.

## Caveats and trade-offs

Weak evidence for a catalogue entry in this category: the numbers are 'Example Output' blocks in two sub-readmes of the author's SpeedTestCV repo (4 stars, no license file, last commit 2022-07-28), not a published results table; hardware and CPU model are not stated (the BoofCV block says 'On my system'). Both blocks date from commit 0bd58bd (2019-03-21) and measure BoofCV 0.33.1 against opencv-python 4.0.0.21; the later version bumps to BoofCV 0.38-SNAPSHOT and opencv-python 4.5.1.48 did not refresh them (the current benchmark.py would print a SIFT row and a different row order and 2-decimal format). BoofCV is timed with JMH (with warm-up, concurrency enabled), OpenCV with a hand-written Python loop (mean of 10 time.time() trials after gc.collect, one trial for the histogram, no warm-up, Python call overhead included); cv2.setNumThreads(0) is commented out, so OpenCV runs multi-threaded as shipped. Rows are not all like-for-like: OpenCV HoughLines is fed the raw grayscale chessboard image (every non-zero pixel votes), whereas BoofCV's houghPolar computes a gradient and keeps only edges above threshold 50 first, so the 4.2x Hough row compares different work; Shi-Tomasi parameters were tuned separately per library; the OpenCV Canny row includes a findContours call while BoofCV's Canny includes a mandatory blur; the libraries also convert RGB to gray differently (weighted vs plain average). The benchmark file itself lists TODOs. The comparison is not a win overall: OpenCV is 2-3x faster on Gaussian blur and Canny. None of the rows is a colour conversion or resampler, so the assigned category fits only loosely (Gaussian blur and Sobel are the nearest; general image processing would fit better). The author's fuller page, boofcv.org Performance:OpenCV:BoofCV, is blocked in this environment (EGRESS_BLOCKED, confirmed 2026-10-07) and was not read. A 2012 SURF paper by the BoofCV author (title only, not opened; arXiv blocked) reportedly compares SURF runtimes of several implementations; nothing from it is used here. Retier idea for a session with arXiv or boofcv.org access. [retier] SpeedTestCV outputs from commit 0bd58bd (2019-03-21; BoofCV 0.33.1 vs opencv-python 4.0.0.21, no hardware, JMH vs a Python time.time() loop): 5 rows faster, 3 slower (blur, Canny, mean threshold). The Sobel row uses OpenCV ksize=1 against BoofCV's 3x3 kernel, the contour row thresholds complementary regions, and the Hough row runs on a nearly all-non-zero 3648x2736 image, so those wins are not like for like. Java library, loose fit in color-and-resampling.

Pure Java, runs on the JVM with JIT warm-up. Gaussian blur rounds results (OpenCV truncates with integer division) and RGB-to-gray is a plain average by default (OpenCV uses a weighted average), per the SpeedTestCV readme. Optional OpenCV interop through JavaCV.

## Maintenance

Actively maintained (last commit 2026-10-06, 5,605 commits, 1.5.0 on Maven Central, 54 open issues) and Apache-2.0, so easy to adopt on the JVM, but the only OpenCV comparison is a seven-year-old first-party run with no hardware stated, and most of its wins rest on rows that are not like-for-like.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party 'Example Output' blocks in the author's SpeedTestCV repo (boofcv/readme.md JMH table, opencv/readme.md script output); benchmark code is public (boofcv/src/jmh/java/speed/BenchmarkImageProcessing.java, opencv/benchmark.py) but no CPU model or hardware is stated and the outputs predate the pinned versions, so C, not A.
- **Verifier notes:** Numbers match the two readmes exactly, but git history shows both example outputs were written on 2019-03-21 (BoofCV 0.33.1 vs opencv-python 4.0.0.21) and never re-run, so the record's 0.38-SNAPSHOT / 4.5.1.48 pairing was wrong and is corrected. Shortcomings to record: no hardware stated, JMH vs Python time.time() harness, Hough row not like-for-like (OpenCV votes on the raw gray image), OpenCV faster on blur, Canny and mean threshold, category fit loose. License Apache-2.0, 1.2k stars, last commit 2026-10-06 confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** same-harness re-run on current versions with hardware stated; like-for-like kernels and thresholds on both sides
- **Pages the verifier opened:**
  - <https://github.com/lessthanoptimal/SpeedTestCV/blob/master/boofcv/readme.md>
  - <https://github.com/lessthanoptimal/SpeedTestCV/blob/master/opencv/readme.md>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/boofcv/readme.md>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/opencv/readme.md>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/opencv/benchmark.py>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/opencv/requirements.txt>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/boofcv/build.gradle>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/boofcv/src/jmh/java/speed/BenchmarkImageProcessing.java>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/0bd58bd/opencv/readme.md>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/0bd58bd/opencv/requirements.txt>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/0bd58bd/opencv/benchmark.py>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/0bd58bd/boofcv/readme.md>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/0bd58bd/boofcv/build.gradle>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/0bd58bd/boofcv/src/main/java/speed/BenchmarkImageProcessing.java>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/f835e72/boofcv/readme.md>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/66dbdc8/boofcv/readme.md>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/66dbdc8/boofcv/build.gradle>
  - <https://github.com/lessthanoptimal/SpeedTestCV>
  - <https://github.com/lessthanoptimal/SpeedTestCV/commits/master>
  - <https://github.com/lessthanoptimal/SpeedTestCV/commits/master/opencv/readme.md>
  - <https://github.com/lessthanoptimal/SpeedTestCV/commits/master/boofcv/readme.md>
  - <https://github.com/lessthanoptimal/SpeedTestCV/tree/master/boofcv>
  - <https://github.com/lessthanoptimal/SpeedTestCV/tree/0bd58bd/boofcv>
  - <https://github.com/lessthanoptimal/BoofCV>
  - <https://github.com/lessthanoptimal/BoofCV/commits>
- **Sources the enricher read:**
  - <https://github.com/lessthanoptimal/BoofCV>
  - <https://github.com/lessthanoptimal/BoofCV/issues?q=is%3Aissue+performance>
  - <https://raw.githubusercontent.com/lessthanoptimal/BoofCV/HEAD/README.md>
  - <https://raw.githubusercontent.com/lessthanoptimal/BoofCV/HEAD/main/boofcv-ip/src/main/java/boofcv/alg/filter/binary/ThresholdImageOps.java>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/boofcv/readme.md>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/opencv/readme.md>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/opencv/benchmark.py>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/boofcv/src/jmh/java/speed/BenchmarkImageProcessing.java>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/boofcv/build.gradle>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/0bd58bd/boofcv/src/main/java/speed/BenchmarkImageProcessing.java>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/0bd58bd/opencv/benchmark.py>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/data/chessboard_large.jpg>
  - <https://raw.githubusercontent.com/lessthanoptimal/SpeedTestCV/HEAD/data/binary.png>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/lessthanoptimal/boofcv`) · [data/wave10/enrich/raw/github_com_lessthanoptimal_boofcv.json](../../../data/wave10/enrich/raw/github_com_lessthanoptimal_boofcv.json) (enrichment confidence 0.8)

</details>
