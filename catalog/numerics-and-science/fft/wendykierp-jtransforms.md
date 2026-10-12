# JTransforms

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `BSD-2-Clause` · 🟢 active

> Pure-Java multithreaded FFT/DCT/DST/DHT library; beat a per-call-planned FFTW (via JNI) on smooth 2-D/3-D sizes, lost on primes.

| | |
|---|---|
| **Beats** | FFTW 3 through the ezFFTW Java wrapper (single-threaded) |
| **Claimed result** | FFTBench README (s/op, 3 JMH iterations; 2 for 3-D): 1-D arrayInput, JTransforms with its heuristic multithreading vs single-threaded ezFFTW/FFTW: 10,000,000 elements 3.205 vs 4.560; 1,024 about 1e-4 vs 0.006 (FFTW error +-0.053); FFTW faster at 98,304 (0.029 vs 0.033), 589,829 (0.815 vs 1.052) and 1,000,000 (0.175 vs 0.290). 2-D singleArrayInput with JTransforms threading disabled (snglthrd_JT) vs FFTW: 1280x720 0.137 vs 0.155, 1920x1080 0.331 vs 0.360, 3000x2000 1.100 vs 1.374, 5000x5000 6.033 vs 8.422, but 1087x1931 2.132 vs 0.998 (FFTW 2.1x faster); multithreaded JTransforms 0.058 at 1280x720 and 0.125 at 1920x1080. 3-D single-threaded: 256^3 2.272 vs 4.252, but FFTW faster at 100x120x140 (0.176 vs 0.311) and 400x300x200 (2.955 vs 4.277). |
| **Workload** | Java JMH benchmark in the third-party FFTBench repo (JMH 1.21, JTransforms 3.1 vs ezFFTW 0.1.2): full real-to-complex forward FFT, zero the DC bin, then inverse FFT, for 1-D (1,024 to 10,000,000 elements), 2-D (1280x720 to 5000x5000) and 3-D (100x120x140 to 400x300x200) arrays, as single calls (arrayInput/singleArrayInput) and as parallel invocations. |
| **Metric** | latency |
| **Hardware** | AMD Phenom II X4 955 on Ubuntu 16.04 (from the run-log file name runs/ubuntu_16.04_phenom_II_x4_955.txt) |
| **Compiler and flags** | JMH 1.21 on Oracle JDK 1.8.0_111 (HotSpot 64-Bit Server VM 25.111-b14); VM options none for the 1-D runs and -Xmx6g -Xms3g for the 2-D and 3-D runs (per the linked run log); native FFTW comes from the bytedeco JavaCPP preset via ezFFTW, build and version not stated |
| **Adoption** | 430 stars, 94 forks; version 3.2 on Maven Central |
| **Last commit** | 2025-12-05 |
| **Links** | [repository](https://github.com/wendykierp/JTransforms) · [benchmark](https://github.com/hageldave/FFTBench) |

## Verdict

Third-party FFTBench (JMH 1.21, Oracle JDK 1.8.0_111, AMD Phenom II X4 955, Ubuntu 16.04, 2-3 iterations) ran a real-to-complex forward, DC-zero and inverse round trip with JTransforms 3.1 against FFTW through the ezFFTW 0.1.2 JNI wrapper, which plans FFTW_ESTIMATE inside every call. Single-threaded JTransforms won on smooth 2-D sizes (1.13x at 1280x720 up to 1.40x at 5000x5000) and on 256^3 (1.87x), but lost at 1,087x1,931, 100x120x140 and 400x300x200; threaded 1-D JTransforms won at 10,000,000 elements (1.42x) but lost at 98,304, 589,829 and 1,000,000 (ratios derived from page data).

## Use it when

- JVM applications (Java, Kotlin, Scala) that need FFT, DCT, DST or DHT without JNI or native libraries, e.g. image processing (the companion paper is on large-scale image deblurring).
- Large 2-D or 3-D real/complex transforms on multi-core machines, where the built-in threading helps: in FFTBench, threaded JTransforms ran 1,920x1,080 in 0.125 s vs 0.360 s for single-threaded FFTW via ezFFTW.
- Power-of-two or 2/3/5-smooth sizes (image dimensions like 1280x720, 3000x2000), which use the split-radix or mixed-radix paths.
- 1-D arrays larger than 2^31 elements, through DoubleLargeArray/FloatLargeArray (changelog 3.0: sizes up to 2^63).

## Skip it when

- C or C++ code: this is Java only; native projects should use FFTW, PocketFFT or a sibling C/C++ library.
- Sizes with large prime factors: they go to Bluestein; in FFTBench the prime 1-D size 589,829 (1.052 vs 0.815 s) and the prime-by-prime 1,087x1,931 2-D case (single-threaded 2.132 vs 0.998 s) lost to even a per-call FFTW_ESTIMATE baseline.
- Non-power-of-two DoubleFFT_1D.realInverse: open issue #21 (2020) reports output with twice the expected amplitude (example size 48).
- Workloads where you could use properly planned native FFTW: the only FFTW comparison found re-plans FFTW_ESTIMATE on every call through JNI, so JTransforms has not been shown to beat tuned FFTW.
- Allocation- or latency-sensitive loops: the mixed-radix and Bluestein paths allocate scratch arrays on every call (new double[...] in the source), adding GC pressure.

## How it is fast

The constructor picks one of three algorithms: Ooura's split-radix FFT for powers of two, FFTPack-derived mixed-radix (factors 4, 2, 3, 5, plus generic odd factors) when what remains after those factors is below 211, and Bluestein's chirp-z algorithm (zero-padded to the next power of two at or above 2n-1) otherwise. Twiddle and bit-reversal tables are precomputed in the constructor. Above size thresholds (1-D: 8,192 elements for 2 threads, 65,536 for 4; 2-D/3-D: 65,536) the butterflies and row/column passes are split across a JLargeArrays ConcurrencyUtils thread pool. There is no explicit SIMD.

## Compared with alternatives

No catalogued sibling is a Java library; pick JTransforms when you must stay on the JVM without native code. For C/C++ code, PocketFFT or KFR cover the same transforms faster, and FFTW itself remains the reference.

## Integration

| | |
|---|---|
| **Form** | module (Maven Central JAR com.github.wendykierp:JTransforms:3.2) |
| **Dependencies** | JLargeArrays (org.visnow; 1.7 for release 3.2 per the changelog, 1.8-SNAPSHOT in the HEAD pom); Apache Commons Math was dropped in 3.2 |
| **Minimum toolchain** | HEAD pom compiles with --release 11 and adds module-info.java; JTransforms 3.1 ran on Java 8 (JDK 1.8.0_111) in FFTBench |
| **Platforms** | any JVM |
| **Thread safety** | Not documented. Thread count and the size thresholds for threading are process-wide static settings (CommonUtils, JLargeArrays ConcurrencyUtils), and the internal pool uses non-daemon threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- The internal thread pool uses non-daemon threads, so main() can hang about 60 s before the JVM exits (open issue #14); call ConcurrencyUtils.shutdownThreadPoolAndAwaitTermination() or set the thread count to 1.
- realForward returns a packed half spectrum in place (for even n, a[1] holds Re[n/2]); realForwardFull needs an array of length 2n with only the first n filled, and its inverse is complexInverse.
- Inverse transforms take a boolean scale flag; pass true to get 1/n normalisation.
- Open issue #15 (2018): FloatFFT_2D.realForwardFull hangs at 4,098x4,097 right after a 4,096x4,096 call succeeds.

## Known shortcomings

- Baseline crippled: ezFFTW plans and destroys an FFTW_ESTIMATE plan inside every timed call; 1-D wins are multithreaded JTransforms vs single-thread FFTW, and single-thread results split both ways; Java.
- Open correctness issues: #21 realInverse gives 2x amplitude on non-power-of-two sizes, #15 FloatFFT_2D.realForwardFull hangs at 4098x4097, #14 non-daemon pool threads delay JVM exit; losses line up with prime sizes routed to Bluestein.

## Caveats and trade-offs

Mixed result: the benchmark author's own conclusion is that no library wins everywhere. FFTW is reached through ezFFTW (GPL-2.0, written by the benchmark's author), which creates an FFTW_ESTIMATE plan, executes and destroys it on every call inside the timed operation, serializes planning behind a global lock, uses the split-array guru interface and copies data through JNI, so the baseline is far from tuned FFTW (the 1,024-point 0.006 s figure is overhead, not FFT time). The 1-D JTransforms rows have JTransforms' multithreading enabled while FFTW is single-threaded; in like-for-like single-threaded 2-D and 3-D runs the results split both ways. Hardware is a 2009-era AMD Phenom II on Java 8; each JMH row used only 2-3 iterations and some error bars exceed the score. The JTransforms README itself shows no FFTW numbers. Pure Java, not C++.

Pure Java, multithreaded by default, DFT/DCT/DST/DHT derived from Ooura's FFT package; JVM warm-up and GC apply.

## Maintenance

Active again after ten quiet years (3.1 in 2015, 3.2 released November 2025, last commit 2025-12-05); BSD-2-Clause and on Maven Central, though several correctness and hang issues (#15, #21) are still open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Third-party JMH benchmark (FFTBench, README plus linked run log) with public code, JDK 1.8.0_111, JVM options and an AMD Phenom II X4 955 named in the run-log file name, which would otherwise be A-level; but the FFTW baseline is the benchmark author's own ezFFTW wrapper, which builds and destroys an FFTW_ESTIMATE split-array guru plan inside every timed call under a global planner lock, and the native FFTW build is unstated, so the baseline is handicapped and the entry is held at C (analogous to the debug-baseline cap).
- **Verifier notes:** Numbers in the record match the FFTBench README exactly; corrections add the threading split, the 3-D results, the JVM/CPU details found in the linked run log, and the ezFFTW per-call FFTW_ESTIMATE planning found in its FFTW_Guru.java. JTransforms BSD-2-Clause, 430 stars, last commit 2025-12-05 confirmed (active).
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/hageldave/FFTBench/HEAD/README.md>
  - <https://raw.githubusercontent.com/hageldave/FFTBench/HEAD/runs/ubuntu_16.04_phenom_II_x4_955.txt>
  - <https://raw.githubusercontent.com/hageldave/FFTBench/HEAD/pom.xml>
  - <https://github.com/hageldave/ezfftw>
  - <https://raw.githubusercontent.com/hageldave/ezfftw/HEAD/src/main/java/hageldave/ezfftw/dp/FFT.java>
  - <https://raw.githubusercontent.com/hageldave/ezfftw/HEAD/src/main/java/hageldave/ezfftw/dp/FFTW_Guru.java>
  - <https://github.com/wendykierp/JTransforms>
  - <https://github.com/wendykierp/JTransforms/commits>
  - <https://raw.githubusercontent.com/wendykierp/JTransforms/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wendykierp/JTransforms/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/wendykierp/JTransforms>
  - <https://github.com/wendykierp/JTransforms/commits>
  - <https://github.com/wendykierp/JTransforms/issues?q=is%3Aissue>
  - <https://github.com/wendykierp/JTransforms/issues/14>
  - <https://github.com/wendykierp/JTransforms/issues/15>
  - <https://github.com/wendykierp/JTransforms/issues/21>
  - <https://raw.githubusercontent.com/wendykierp/JTransforms/HEAD/README.md>
  - <https://raw.githubusercontent.com/wendykierp/JTransforms/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wendykierp/JTransforms/HEAD/pom.xml>
  - <https://raw.githubusercontent.com/wendykierp/JTransforms/HEAD/changelog.txt>
  - <https://raw.githubusercontent.com/wendykierp/JTransforms/HEAD/src/main/java/org/jtransforms/utils/CommonUtils.java>
  - <https://raw.githubusercontent.com/wendykierp/JTransforms/HEAD/src/main/java/org/jtransforms/fft/DoubleFFT_1D.java>
  - <https://raw.githubusercontent.com/wendykierp/JTransforms/HEAD/src/main/java/org/jtransforms/fft/DoubleFFT_2D.java>
  - <https://raw.githubusercontent.com/hageldave/FFTBench/HEAD/README.md>
  - https://repo1.maven.org/maven2/com/github/wendykierp/JTransforms/3.2/JTransforms-3.2.pom (HTTP 429, not read)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/wendykierp/jtransforms`) · [data/wave8/enrich/raw/github_com_wendykierp_jtransforms.json](../../../data/wave8/enrich/raw/github_com_wendykierp_jtransforms.json) (enrichment confidence 0.8)

</details>
