# ZigguratGaussian (cicirello/ZigguratGaussian, Java ziggurat normal generator)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `GPL-3.0-or-later` · 🟢 active

> Java ziggurat normal sampler (GSL port); about 6-8x faster than polar-method Random/ThreadLocalRandom.nextGaussian on JDK 17.

| | |
|---|---|
| **Beats** | Java built-in Random.nextGaussian and ThreadLocalRandom.nextGaussian (polar method) |
| **Claimed result** | results17.txt (JMH avgt, ns/op): Random 103.037 built-in versus 17.393 ziggurat; ThreadLocalRandom 88.774 built-in versus 10.901 ziggurat; SplittableRandom 8.927 built-in versus 10.089 ziggurat (built-in faster). About 5.9x and 8.1x faster for Random and ThreadLocalRandom (derived from page data). The same run's wrappedThreadLocalRandom benchmark (ThreadLocalRandom wrapped as a java.util.random.RandomGenerator so Java 17's own modified ziggurat is used) took 10.392 ns/op, slightly faster than the library's 10.901. |
| **Workload** | JMH average time per Gaussian sample on JDK 17 for Random, ThreadLocalRandom and SplittableRandom, built-in versus the library's ziggurat. |
| **Metric** | latency |
| **Compiler and flags** | JMH 1.37, OpenJDK 64-Bit Server VM 17.0.2+8, no VM options, 5 warmup and 5 measurement iterations of 10 s, 1 thread; source and Maven build in experiment/timing17 |
| **Adoption** | 10 stars; published on Maven Central as org.cicirello:ziggurat |
| **Last commit** | 2026-09-09 |
| **Links** | [repository](https://github.com/cicirello/ZigguratGaussian) · [benchmark](https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/experiment/timing17/results17.txt) |

## Verdict

One JMH 1.37 run on OpenJDK 17.0.2 (1 thread, 1 fork, 5x10 s warmup and measurement, Windows host, CPU not stated) measured average ns per sample: Random 103.04 built-in vs 17.39 ziggurat (about 5.9x, derived from page data), ThreadLocalRandom 88.77 vs 10.90 (about 8.1x, derived), but SplittableRandom 8.93 built-in vs 10.09 ziggurat and ThreadLocalRandom-as-RandomGenerator 10.39 vs 10.90, so the JDK 17 modified ziggurat wins wherever it is reachable. Benchmark source and raw output are public; the accompanying arXiv report (2405.19493) was seen only as a search snippet, which states the same conclusion.

## Use it when

- Java code that draws many Gaussians from java.util.Random or SecureRandom on any JDK: those classes still use the synchronized polar method (103.0 vs 17.4 ns/op for Random in the JDK 17 JMH run).
- ThreadLocalRandom on JDK 11 through 25: its nextGaussian is the inherited polar method there (88.8 vs 10.9 ns/op on JDK 17).
- Any of the legacy generators, SplittableRandom included, on JDK 11 to 16, where the JDK has no ziggurat at all (README table).
- Gaussian-mutation-heavy evolutionary algorithms and simulations that must stay on Java 11 and cannot adopt the Java 17 RandomGenerator API; the library was written to speed up a parallel genetic algorithm.

## Skip it when

- C or C++ projects: it is pure Java with no native or C ABI; this catalog's C/C++ ziggurat entries (cauldron random.h, normaldist-benchmark, EigenRand) are the comparable choices.
- SplittableRandom or any java.util.random.RandomGenerator on JDK 17+: the JDK's own McFarland modified ziggurat is faster (8.93 vs 10.09 ns/op for SplittableRandom; wrapping ThreadLocalRandom as a RandomGenerator gave 10.39 vs 10.90 ns/op), and the author's report says the same.
- ThreadLocalRandom on JDK 26 and later: OpenJDK commit 8372134 (master, 2025-11-27) made ThreadLocalRandom.nextGaussian call RandomSupport.computeNextGaussian, the modified ziggurat, so the 8x gap measured on JDK 17 should be gone there (inference from the JDK source; not benchmarked).
- Code that must reproduce existing seeded runs: the output sequence and the number of RNG draws per sample differ from r.nextGaussian(), so fixed-seed experiments change.
- Projects that cannot take GPL-3.0-or-later code (the Java source carries the GSL GPL lineage; there is no permissive variant).

## How it is fast

It replaces the Marsaglia polar method (two uniforms, a rejection loop and a log plus sqrt per pair) with the Marsaglia-Tsang ziggurat as simplified in Jochen Voss's GSL gauss.c: 128 layers, an exponential-wedge tail, and precomputed ytab/ktab/wtab tables. The common path is one 32-bit nextInt() split into sign (1 bit), layer (7 bits) and a 24-bit integer j, an integer compare j &lt; ktab[i] and one multiply, with no transcendental call; StrictMath.exp/log run only on the rare wedge and tail branches. Port changes over GSL: one nextInt() instead of two RNG calls, and multiplication by a precomputed 1/R instead of division.

## Compared with alternatives

Pick it only in Java code still on Random, SecureRandom or (before JDK 26) ThreadLocalRandom, or on JDK 11-16; for C++ the catalogued cauldron random.h ziggurat (4.0 vs 8.9 ns per float sample over std::normal_distribution) or EigenRand's vectorized normals are the relevant choices, and dqrng covers R/C++ users.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (JUnit Jupiter for tests only) |
| **Minimum toolchain** | Java 11 (pom.xml maven.compiler.release 11; jars built with OpenJDK 25 targeting 11) |
| **Platforms** | any JVM, Java 11+ |
| **Thread safety** | Static methods over immutable final tables, so safety follows the generator you pass: the no-argument form uses ThreadLocalRandom.current() and is safe per thread; Random is thread-safe but shared instances contend; SplittableRandom must not be shared across threads. |
| **Drop-in for the baseline** | partial: same N(0,1) contract and Random/SplittableRandom/ThreadLocalRandom sources, but it is a static utility (no override of nextGaussian), so every call site must be rewritten and the random sequence changes. |

## Gotchas

- Easy to bypass by accident: r.nextGaussian() still compiles and still runs the slow JDK method; the source comments name this as the drawback of the static-utility design.
- Fast-path resolution is limited by the 24-bit j: x = j \* wtab[i], so each layer yields at most 2^24 distinct magnitudes (the GSL design), coarser than a 53-bit double; fine for simulation and evolutionary algorithms, worth knowing for tail-sensitive statistics.
- Wedge and tail use StrictMath.exp and StrictMath.log (bit-reproducible across JVMs, slower than Math); they run only in the rare rejection branches.
- The repo says the code has been absorbed into cicirello/rho-mu (GPL-3.0); rho-mu 5.x needs Java 25, 2.x-4.x need Java 17 and 1.x Java 11, so pick that library if you want the same sampler plus RandomGenerator wrappers.

## Known shortcomings

- Tier C: results17.txt JMH numbers from public benchmark source with no CPU model. In the same run JDK 17's own ziggurat (wrappedThreadLocalRandom) took 10.392 ns/op against the library's 10.901, so on Java 17+ the win holds only against the legacy nextGaussian. License is GPL-3.0-or-later (pom.xml). Library absorbed into cicirello/rho-mu.
- On JDK 26+ ThreadLocalRandom gains nothing: OpenJDK commit 8372134 (master 2025-11-27) made ThreadLocalRandom.nextGaussian use the JDK's modified ziggurat, while jdk17u/21u/25u still inherit the polar method. The remaining win is Random/SecureRandom on any JDK, ThreadLocalRandom on JDK 11-25 and everything on JDK 11-16. Java-only, GPL-3.0, 24-bit fast-path resolution; the project is folded into rho-mu.

## Caveats and trade-offs

Java, not callable from C++; the gain is against Java's legacy polar-method nextGaussian, not a C++ facility. On Java 17+ the JDK's own modified ziggurat (RandomGenerator default nextGaussian, used by SplittableRandom and reachable for ThreadLocalRandom by wrapping it as a RandomGenerator) matches or beats this library in the same JMH run (8.927 vs 10.089 and 10.392 vs 10.901 ns/op), so the win only holds against the legacy Random/ThreadLocalRandom/SecureRandom methods or on Java 11-16. Benchmark code and raw JMH output are public but no CPU model is given (JDK path in the output is a Windows path). The arXiv report 2405.19493 was not opened (arXiv and reports.cicirello.org blocked); a search snippet says Java 17's modified ziggurat is faster than this implementation for the PRNGs that support it. README says the library has been absorbed into cicirello/rho-mu (Java 25+).

Java port of the GSL C ziggurat implementation (GPL), with Java-specific optimizations. In Java 17 and later SplittableRandom already uses a ziggurat, so the library helps only for Random, SecureRandom and ThreadLocalRandom there. The author has folded it into the rho-mu library, which needs Java 25.

## Maintenance

Active in name only (v1.1.2 of 2026-07-08 is a CI-only release, 0 open issues, 10 stars, recent commits are dependency bumps) because the author has moved the code into rho-mu; GPL-3.0-or-later, a single \~750-line source file, on Maven Central.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** results17.txt is raw JMH 1.37 output on OpenJDK 17.0.2+8 comparing built-in nextGaussian against the library's ziggurat, and the benchmark source (experiment/timing17/src/main/java/org/cicirello/experiments/ziggurat/TimeZigguratVersusJavaBuiltin.java) and pom.xml are public, but no CPU model is stated in the results, the timing17 README or the repo README; the arXiv report (2405.19493) is a preprint and its host was blocked, so first-party tier C.
- **Verifier notes:** Numbers match results17.txt exactly. Metadata checked on github.com: 10 stars, 1 fork, not archived or a fork, last commit 2026-09-09 (dependabot, active); LICENSE is GPL v3 and pom.xml declares GPL-3.0-or-later (source headers say 'either version 3 ... or any later version'). Maintained activity is dependency bumps; the code now lives on in cicirello/rho-mu.
- **Fields the verifier corrected:** `license`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/cicirello/ZigguratGaussian>
  - <https://github.com/cicirello/ZigguratGaussian/commits>
  - <https://github.com/cicirello/ZigguratGaussian/tree/master/experiment/timing17>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/README.md>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/experiment/timing17/results17.txt>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/experiment/timing17/src/main/java/org/cicirello/experiments/ziggurat/TimeZigguratVersusJavaBuiltin.java>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/pom.xml>
- **Sources the enricher read:**
  - <https://github.com/cicirello/ZigguratGaussian>
  - <https://github.com/cicirello/ZigguratGaussian/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/README.md>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/pom.xml>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/src/main/java/org/cicirello/math/rand/ZigguratGaussian.java>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/src/main/java/org/cicirello/math/rand/PolarGaussian.java>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/experiment/timing17/README.md>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/experiment/timing17/results17.txt>
  - <https://raw.githubusercontent.com/cicirello/ZigguratGaussian/HEAD/experiment/timing17/src/main/java/org/cicirello/experiments/ziggurat/TimeZigguratVersusJavaBuiltin.java>
  - <https://raw.githubusercontent.com/cicirello/rho-mu/HEAD/README.md>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/share/classes/java/util/concurrent/ThreadLocalRandom.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/share/classes/java/util/Random.java>
  - <https://raw.githubusercontent.com/openjdk/jdk17u/master/src/java.base/share/classes/java/util/concurrent/ThreadLocalRandom.java>
  - <https://raw.githubusercontent.com/openjdk/jdk21u/master/src/java.base/share/classes/java/util/concurrent/ThreadLocalRandom.java>
  - <https://raw.githubusercontent.com/openjdk/jdk25u/master/src/java.base/share/classes/java/util/concurrent/ThreadLocalRandom.java>
  - <https://github.com/openjdk/jdk/commits/master/src/java.base/share/classes/java/util/concurrent/ThreadLocalRandom.java>
  - <https://github.com/openjdk/jdk/commit/f1d90b8b25b78b15dc6529a5a6e45633eb250286>
  - WebSearch: Cicirello 'Fast Gaussian Distributed Pseudorandom Number Generation in Java via the Ziggurat Algorithm' (snippet of reports.cicirello.org/24/009/)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/cicirello/zigguratgaussian`) · [data/wave8/enrich/raw/github_com_cicirello_zigguratgaussian.json](../../../data/wave8/enrich/raw/github_com_cicirello_zigguratgaussian.json) (enrichment confidence 0.8)

</details>
