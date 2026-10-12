# PngEncoder (Java)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Java` · `MIT` · 🟢 active

> Pure-Java PNG encoder that beats javax.imageio's PNG writer by compressing image segments in parallel on a thread pool.

| | |
|---|---|
| **Beats** | javax.imageio PNG writer (ImageIO, JDK built-in encoder) |
| **Claimed result** | Independent JMH run (manticore-projects/FPNG-Java README, JDK 21.0.1 GraalVM, SerialGC, CPU unstated), pngencoder 0.14.0 single-threaded vs javax.imageio: level 2 on a 4900x6000 image 1120 vs 1270 ms (1.13x), 1.29-1.44x on the other cases, 2.26-3.53x at level 1 (derived from page data). First-party README (multithreaded pool of availableProcessors threads): 5.1-7.1x over ImageIO. |
| **Workload** | Encoding BufferedImages to a null OutputStream: a random 1024x1024 TYPE_INT_ARGB image, a 2121x350 logo and a 4900x6000 Looklet photograph converted to TYPE_INT_ARGB; PngEncoder at its default deflate level 9 with predictor (row filter) encoding off and multithreaded segment compression on a pool of availableProcessors threads, against ImageIO.write(image, "png", OutputStream) with default parameters; reported as images encoded per second. |
| **Metric** | throughput |
| **Hardware** | A computer with 8 logical cores (CPU model not stated). |
| **Compiler and flags** | JMH harness PngEncoderBenchmarkPngEncoderVsImageIO.java: Mode.Throughput, 1 fork, 1 warmup iteration of 2 s, 1 measurement iteration of 5 s, 1 benchmark thread when the README table was recorded (2020-09-17; an 8-thread runner was added in 2022). JDK version and JVM flags not stated (project compiles for Java 8, Travis CI used openjdk8; current pom uses JMH 1.37). |
| **Adoption** | 46 stars; used in production at Looklet per README |
| **Last commit** | 2025-11-25 |
| **Links** | [repository](https://github.com/pngencoder/pngencoder) · [benchmark](https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/README.md) |

## Verdict

First-party JMH (1 fork, one 5 s measurement iteration, one benchmark thread, CPU and JDK not stated, '8 logical cores'): PngEncoder at level 9, unfiltered, compressing on an 8-thread pool encoded 5.1x to 7.1x more images per second than single-threaded ImageIO.write with defaults (random 1024x1024 ARGB, a 2121x350 logo, a 4900x6000 photo). An independent JMH suite in manticore-projects/FPNG-Java (JDK 21.0.1 GraalVM CE, -XX:+UseSerialGC, 10 iterations, CPU not stated) ran pngencoder 0.14.0 with multithreading disabled: at level 2 it took 0.70 to 0.88 of ImageIO's time (1.13x to 1.44x faster; 1120 vs 1270 ms on the same 4900x6000 photo) and at level 1 it was 2.26x to 3.53x faster (derived from page data), with output sizes not shown in the README.

## Use it when

- A JVM service or batch job that writes large PNGs (multi-megapixel photos, renders, screenshots) on a machine with several idle cores and no JNI allowed.
- Latency of a single large encode matters more than total CPU spent, e.g. one request thread producing one big image while other cores are free.
- You want a dependency-free, Java 8 compatible ImageIO replacement with a tunable compression level (level 1 trades about 2.5x larger files for about 2.3x more speed per the README table).
- Images known to have at most 256 colors, where withTryIndexedEncoding(true) plus withPredictorEncoding(true) gives smaller files than ImageIO (at extra time).

## Skip it when

- Servers already encoding many images concurrently: the pool is one static fixed pool of availableProcessors threads shared by all callers, so the parallel gain mostly disappears (the project's own 8-thread JMH runner commit is titled 'ImageIO gains more :(' and publishes no numbers).
- Single-core or CPU-limited containers: the README says the speedup will not be significant there, and an independent single-threaded JMH run (FPNG-Java suite, JDK 21) measured only 1.13x to 1.44x over ImageIO even at compression level 2.
- Small images: when the raw scanline data is at most one segment (128 KiB, about 181x181 RGBA, derived from code) it always encodes on the calling thread with a plain Deflater.
- When smallest output matters at default settings: unfiltered rows compress worse than ImageIO's adaptive filtering on photographic content, so you must enable predictor encoding and give back much of the speed.
- When you need much higher throughput and JNI is acceptable: native fpng (SSE2) and fpnge (AVX2) through the FPNG-Java wrapper took about 4x to 20x less time than PngEncoder at level 2 in that same JDK 21 suite (derived from page data).

## How it is fast

The speedup is mostly parallel DEFLATE: scanlines are cut into segments of at least 128 KiB (raw size / (9 x availableProcessors)), each segment is compressed by a thread-local raw java.util.zip.Deflater with SYNC_FLUSH on a shared fixed pool of availableProcessors daemon threads, and the byte-aligned outputs are concatenated with a combined Adler-32, in the style of pigz. Each segment starts with an empty dictionary, which costs about 2% in size. By default it also skips PNG row filtering (filter type 0 on every row), whereas ImageIO tries all five filters per row; scanlines are pulled straight from the raster's int/byte buffer for the common BufferedImage types, and Deflater objects are reused per thread.

## Compared with alternatives

Pick it when you must stay pure Java on the JVM; mtpng and pngenc use the same parallel-deflate idea natively (Rust with a C API, and C), and fpng/fpnge are far faster but need native code and give larger files on big photos.

## Integration

| | |
|---|---|
| **Form** | module (Maven Central jar, com.pngencoder:pngencoder) |
| **Dependencies** | none (JDK java.awt and java.util.zip only; JUnit, Hamcrest and JMH are test-scope) |
| **Minimum toolchain** | Java 8 (maven.compiler.source/target 8); no module-info (issue #59 open; PR #124 for Automatic-Module-Name is unmerged) |
| **Platforms** | any JVM with java.desktop/AWT image classes |
| **Thread safety** | Not documented; the code shows immutable builder objects, thread-local Deflaters and per-call buffer pools, so concurrent calls look safe, but all calls share one static fixed thread pool sized at class-load time and the calling thread blocks while its segments compress. |
| **Drop-in for the baseline** | partial: replaces ImageIO.write(img, "png", ...) only; different API, no ImageWriteParam/IIOMetadata support, encoder only |

## Gotchas

- Default output is unfiltered and split into independent deflate segments, so files are not byte-identical to ImageIO and are typically somewhat larger; the 'about the same size as ImageIO' claim was never measured by the benchmark, and ImageIO itself uses deflate level 9 on JDK 8 but level 4 on JDK 9+.
- Peak transient memory in multithreaded mode is roughly 0.75x the raw scanline size on top of the image: up to 3 x availableProcessors queued segments, each holding two pool buffers of 1.125x the segment size (derived from PngEncoderDeflaterOutputStream and PngEncoderDeflaterBufferPool). That is about 90 MB for a 4900x6000 RGBA image.
- toStream()/toFile() return a byte count that omits the sRGB, gAMA, cHRM, pHYs, iCCP, PLTE and tRNS chunks, because PngEncoderLogic.encode writes those to the raw stream instead of its counting wrapper; do not use the return value as the file size when those chunks are present.
- The test helper PngEncoderTestUtil.assertThatPixelIs computes alphaExpected from the actual pixel, so round-trip tests accept any pixel whose decoded alpha is 0; an earlier indexed-encoding corruption bug (issue #34) was fixed in 2022.

## Known shortcomings

- The gain is multithreading (a pool of availableProcessors threads) against single-threaded ImageIO, with no CPU or JDK stated and one 5 s JMH iteration. PngEncoder writes rows unfiltered while ImageIO picks a filter per row and deflates at level 9 on JDK 8 (4 on JDK 9+), so compressed sizes differ and are not recorded; the ImageIO side keeps its default temp-file cache.
- The random 1024x1024 case is incompressible noise, so ImageIO's five-filter trial there is pure overhead. Code bugs not behind the numbers: the toStream and toFile return values omit the sRGB, gAMA, cHRM, pHYs, iCCP, PLTE and tRNS bytes; the test helper assertThatPixelIs derives alphaExpected from the actual value; getProfileName's UTF-16 branch reads data[endIdx] twice. Multithreaded peak memory is about 0.75x the raw scanlines (about 90 MB at 4900x6000). Retier-29 raises the tier to B on the FPNG-Java measurement.

## Caveats and trade-offs

Speedup comes mainly from multithreading: PngEncoder compresses segments on a fixed pool of availableProcessors threads while ImageIO compresses on one thread, and the README says a single-core machine sees no significant gain; a 2022 commit adding an 8-benchmark-thread mode is titled 'Add benchmark for multiple threads. ImageIO gains more :(' and publishes no numbers. The work differs: PngEncoder by default writes scanlines without row filtering, while ImageIO runs adaptive per-row filter selection; ImageIO's deflate level is 9 on JDK 8 (Deflater.BEST_COMPRESSION in jdk8u PNGImageWriter) but 4 on JDK 9 and later (DEFAULT_COMPRESSION_LEVEL = 4), and the JDK used is not stated. The harness calls ImageIO.write on an OutputStream without ImageIO.setUseCache(false), so by JDK default (useCache = true) the ImageIO side writes through a FileCacheImageOutputStream temp file. The benchmark does not record output sizes; the README only says multithreaded output is about 2% larger than ImageIO's. One 5 s measurement iteration with no error estimate; the 4900x6000 case runs at 0.029 ops/s for ImageIO (about 34 s per encode, derived from page data), so that figure rests on about one encode. CPU model ('8 logical cores' only) and JDK not stated; first-party benchmark. Lowering the compression level to 1 gives 2.31x more speed for 2.50x larger files per the README speed-versus-size table. Baseline is the JDK ImageIO writer, not libpng; the Java wrapper fpng-java (not reported here) reports much larger gains over ImageIO by calling the native fpng library. Commits since the 0.16.0 release (2025-05-19) are dependency bumps only.

Pure Java; speedup comes mainly from multithreaded DEFLATE over blocks, so output is about 2% larger than ImageIO at the same level. Optional predictor encoding and indexed output give smaller files at a speed cost. Encoder only.

## Maintenance

Active but in maintenance mode (last commit 2025-11-25, release 0.16.0 of 2025-05-19, later commits are dependency bumps); MIT licensed, Java 8, no dependencies and small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** The README table (36.324 vs 5.150, 127.034 vs 24.857, 0.159 vs 0.029 ops/s) matches the JMH results recorded in src/test/java/com/pngencoder/PngEncoderBenchmarkPngEncoderVsImageIO.java (commit 5cc8d61, 2020-09-17), but CPU model, JDK version and JVM flags are not stated and the run is the project's own, so C.
- **Retiered** C to B: Raised C to B: the enricher found an independent measurement in manticore-projects/FPNG-Java's README (JMH, JDK 21.0.1 GraalVM, SerialGC, CPU unstated) that runs pngencoder 0.14.0 single-threaded at compression level 2 against javax.imageio on the same looklet 4900x6000 image: 1120 ms versus 1270 ms (1.13x), with 1.29x, 1.44x and 1.36x on the other cases and 2.26-3.53x at level 1 (derived from page data). It confirms the verifier's reading that the README's 5.1-7.1x comes mostly from the 8-thread pool; the random 1024x1024 case is incompressible noise, where ImageIO's five-filter trial is pure overhead. Not A: CPU unstated.
- **Verifier notes:** Numbers verified in README and benchmark source comment (initial 2020-08-17 run gave 6.0x/5.2x/5.6x). Confirmed at C; shortcomings are parallel versus single-threaded encoding, unfiltered versus adaptive-filtered rows, JDK-dependent ImageIO deflate level and ImageIO's default temp-file cache. Last commit corrected to 2025-11-25 (active).
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `compiler_and_flags`, `workload`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** Independent JMH run in manticore-projects/FPNG-Java's README (JDK 21.0.1 GraalVM, SerialGC, CPU unstated): pngencoder 0.14.0 single-threaded at level 2 encodes the 4900x6000 looklet image in 1120 ms against javax.imageio's 1270 ms (1.13x), 1.29x, 1.44x and 1.36x on the other cases, and 2.26-3.53x at level 1 (derived from page data).
- **Pages the verifier opened:**
  - <https://github.com/pngencoder/pngencoder>
  - <https://github.com/pngencoder/pngencoder/commits/develop>
  - <https://github.com/pngencoder/pngencoder/commits/develop/src/test/java/com/pngencoder/PngEncoderBenchmarkPngEncoderVsImageIO.java>
  - <https://github.com/pngencoder/pngencoder/commit/32d367c>
  - <https://github.com/pngencoder/pngencoder/tree/develop/src/test/java/com/pngencoder>
  - <https://github.com/pngencoder/pngencoder/tree/develop/src/main/java/com/pngencoder>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/README.md>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/test/java/com/pngencoder/PngEncoderBenchmarkPngEncoderVsImageIO.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/test/java/com/pngencoder/PngEncoderBenchmarkCompressionSpeedVsSize.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/test/java/com/pngencoder/PngEncoderTestUtil.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoder.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderLogic.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderDeflaterExecutorService.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderDeflaterOutputStream.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderScanlineUtil.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/pom.xml>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/1535025/src/test/java/com/pngencoder/PngEncoderBenchmarkPngEncoderVsImageIO.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/5cc8d61/src/test/java/com/pngencoder/PngEncoderBenchmarkPngEncoderVsImageIO.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.desktop/share/classes/com/sun/imageio/plugins/png/PNGImageWriter.java>
  - <https://raw.githubusercontent.com/openjdk/jdk8u/master/jdk/src/share/classes/com/sun/imageio/plugins/png/PNGImageWriter.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.desktop/share/classes/javax/imageio/ImageIO.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.desktop/share/classes/com/sun/imageio/spi/OutputStreamImageOutputStreamSpi.java>
- **Sources the enricher read:**
  - <https://github.com/pngencoder/pngencoder>
  - <https://github.com/pngencoder/pngencoder/issues?q=is%3Aissue>
  - <https://github.com/pngencoder/pngencoder/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/README.md>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/pom.xml>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/test/java/com/pngencoder/PngEncoderBenchmarkPngEncoderVsImageIO.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/test/java/com/pngencoder/PngEncoderBenchmarkCompressionSpeedVsSize.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/test/java/com/pngencoder/PngEncoderTestUtil.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoder.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderLogic.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderDeflaterExecutorService.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderDeflaterExecutorServiceThreadFactory.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderDeflaterOutputStream.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderDeflaterSegmentTask.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderDeflaterThreadLocalDeflater.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderDeflaterBufferPool.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderIdatChunksOutputStream.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderCountingOutputStream.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderPredictor.java>
  - <https://raw.githubusercontent.com/pngencoder/pngencoder/HEAD/src/main/java/com/pngencoder/PngEncoderScanlineUtil.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.desktop/share/classes/com/sun/imageio/plugins/png/PNGImageWriter.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.desktop/share/classes/com/sun/imageio/plugins/png/RowFilter.java>
  - <https://raw.githubusercontent.com/manticore-projects/FPNG-Java/HEAD/README.md>
  - <https://github.com/manticore-projects/FPNG-Java/tree/master/benchmark>
  - <https://github.com/manticore-projects/FPNG-Java/tree/master/benchmark/src/jmh/java>
  - <https://github.com/manticore-projects/FPNG-Java/tree/master/benchmark/src/jmh/java/com/manticore>
  - <https://raw.githubusercontent.com/manticore-projects/FPNG-Java/master/benchmark/build.gradle>
  - <https://raw.githubusercontent.com/manticore-projects/FPNG-Java/master/benchmark/src/jmh/java/com/manticore/EncoderBenchmark.java>
  - <https://raw.githubusercontent.com/manticore-projects/FPNG-Java/master/benchmark/src/jmh/java/com/manticore/PNGEncoderBenchmark.java>
  - <https://raw.githubusercontent.com/manticore-projects/FPNG-Java/master/benchmark/src/jmh/java/com/manticore/ImageIOEncoderBenchmark.java>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/pngencoder/pngencoder`) · [data/wave10/enrich/raw/github_com_pngencoder_pngencoder.json](../../../data/wave10/enrich/raw/github_com_pngencoder_pngencoder.json) (enrichment confidence 0.75)

</details>
