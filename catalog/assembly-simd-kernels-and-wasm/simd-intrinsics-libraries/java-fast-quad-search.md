# java-fast/quad-search

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Java port of Lemire's SIMD Quad search: quaternary narrowing plus a Vector API block scan, 5-29% lower mean latency than Arrays.binarySearch on int arrays.

| | |
|---|---|
| **Beats** | java.util.Arrays.binarySearch |
| **Claimed result** | README: 'outperform Arrays.binarySearch by up to 25% on Oracle JDK, up to 16% on GraalVM on Apple M4 ARM64 (Neon 128-bit)' and 'up to 24% on Oracle JDK, up to 29% on GraalVM on x86-64 AMD (AVX2 256-bit)'; 'p99 values are better than default binary search almost in all test cases'. The percentages are reductions in mean ns/op of simdQuadSearch versus binarySearchDefault and match the best single result files: arm64 Oracle 4k warm 32.540 vs 24.496 ns/op (24.7%), arm64 GraalVM 64k cold 240.503 vs 201.196 (16.3%), amd64 Oracle 16k warm 202.130 vs 153.170 (24.2%), amd64 GraalVM 8k cold 659.617 vs 466.574 (29.3%, about 1.41x) (derived from page data). docs/results/amd64 Oracle JDK 1m cold: binarySearchDefault 1192.757 ns/op, quadSearch 1020.096 ns/op, simdQuadSearch 1053.785 ns/op (about 12% less time for the SIMD variant, derived from page data). Typical gains across the 72 files are 5 to 15%. |
| **Workload** | Quaternary narrowing over 16-element block boundaries, then a Vector API (jdk.incubator.vector, SPECIES_PREFERRED) block scan, versus Arrays.binarySearch over sorted, strictly increasing int arrays of 4k to 1m elements (array count shrinks from 256k to 1k as size grows, about 4 GB of data per run). Cold-cache runs switch arrays on every query; warm-cache runs reuse each array for 128 consecutive queries (README says 100). Queries are uniform in [0, 8n) while array values average 4.5n, so about 44% of queries lie beyond the last element. JMH sample mode on Oracle JDK and GraalVM. |
| **Metric** | latency |
| **Hardware** | Apple M4 (arm64, NEON 128-bit) and an unnamed x86-64 AMD CPU with AVX2 (model not stated in the README, the results files or docs/index.html) |
| **Compiler and flags** | Java 25 toolchain (Oracle JDK and GraalVM; exact builds not stated), JMH 1.37 via the me.champeau.jmh 0.7.3 Gradle plugin, Mode.SampleTime, 3 forks, 5 x 2 s warmup, 10 x 2 s measurement; JVM args --add-modules=jdk.incubator.vector --enable-preview -Xms12g -Xmx12g -XX:+UseG1GC (build.gradle); run-benchmarks.sh sweeps the nine sizes for both benchmarks |
| **Adoption** | 3 stars |
| **Last commit** | 2026-05-25 |
| **Links** | [repository](https://github.com/java-fast/quad-search) · [benchmark](https://github.com/java-fast/quad-search) |

## Verdict

First-party JMH 1.37 runs (SampleTime, 3 forks, 5 x 2 s warmup, 10 x 2 s measurement, -Xmx12g G1) on Java 25 Oracle JDK and GraalVM, on an Apple M4 and an unnamed AMD AVX2 machine, search sorted int arrays of 4k to 1M elements in cold and 128-query warm modes; simdQuadSearch's mean ns/op is typically 5-15% below Arrays.binarySearch, at best 24.7% (arm64 Oracle 4k warm, 24.5 vs 32.5 ns) and 29.3% (amd64 GraalVM 8k cold, 466.6 vs 659.6 ns), and slower in a few GraalVM cells. All 72 result files are in docs/results.

## Use it when

- Hot lookup loops over sorted int[] of 4k to 1M elements (posting lists, sorted column chunks, many small sorted arrays) on JDK 25 where a 10-25% cut in mean lookup time matters.
- Cold-cache lookups across many arrays, where the quaternary step overlaps cache misses: amd64 Oracle JDK 1m cold measured 1053.8 ns for simdQuadSearch and 1020.1 ns for the scalar QuadSearch vs 1192.8 ns for Arrays.binarySearch.
- x86-64 deployments that cannot enable incubator modules: the scalar QuadSearch needs no jdk.incubator.vector and already beat binarySearch in the amd64 cells cited.
- As readable reference code for porting the SIMD Quad idea to other JVM key types (long, float) with Arrays.binarySearch result semantics.

## Skip it when

- On arm64 without the SIMD variant: the scalar QuadSearch was slower than Arrays.binarySearch at 4k to 16k cold (arm64 Oracle 4k cold 130.9 vs 110.5 ns) and at 4k warm (37.4 vs 32.5 ns).
- On GraalVM at some sizes the SIMD variant loses (amd64 GraalVM 16k warm 206.2 vs 197.2 ns; arm64 GraalVM 4k warm 34.4 vs 33.4 ns); measure on your JVM before switching.
- Code that cannot ship with --add-modules jdk.incubator.vector: the Vector API is still incubating and can change between JDK releases.
- Arrays under 4k elements (not benchmarked; under 16 elements it is a plain linear scan), long[]/double[]/Object[] with a Comparator, or fromIndex/toIndex range searches: none are provided.
- Teams wanting a maintained library: 3 stars, 12 commits over 2026-05-23 to 2026-05-25, no releases, no artifact.

## How it is fast

The array is treated as 16-int blocks. A quaternary (4-ary) search over the block-end keys loads three independent pivots per step, so their cache misses overlap (memory-level parallelism) and the chain of dependent loads drops from about log2(n) to about log4(n/16) levels. Once one to three blocks remain, SimdQuadSearch scans the 16-int block with IntVector.compare(GE) at SPECIES_PREFERRED width (4 lanes on NEON, 8 on AVX2), turns the mask into a long and takes numberOfTrailingZeros, which yields the found index or the insertion point without a per-element branch.

## Compared with alternatives

No sibling in this category is a search routine; the closest catalogued work is Lemire's C++ SIMD Quad search (wave 1, searching), which this ports to Java. Pick this one when you are on the JVM and need Arrays.binarySearch's insertion-point result; use Lemire's C++ code for uint16 membership tests in native code.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for QuadSearch; SimdQuadSearch needs the jdk.incubator.vector module (--add-modules jdk.incubator.vector at compile and run time) |
| **Minimum toolchain** | Java 25 as built and benchmarked (Gradle toolchain languageVersion 25; build also passes --enable-preview); earlier JDKs with the Vector API incubator are untested |
| **Platforms** | any JVM; benchmarked on Apple M4 (NEON, 128-bit) and an unnamed AMD x86-64 CPU (AVX2, 256-bit) with Oracle JDK and GraalVM |
| **Thread safety** | stateless static methods that only read the array; safe for concurrent readers (from source, not documented) |
| **Drop-in for the baseline** | partial — same (int[], int) call shape and return encoding as Arrays.binarySearch for sorted int arrays, but no range, long, float, double or Object overloads; with duplicates it returns the leftmost match where Arrays.binarySearch returns any match; SimdQuadSearch needs the incubator module |

## Gotchas

- Harness flaw on arm64: JMH SampleTime times single calls, and the arm64 files show percentiles in \~41.7 ns steps (Oracle 4k warm: p0 \~0, p50 41, p90 42, p95 83 or 125 ns) while the means are 24 to 37 ns, so each sample is at or below one timer tick; the small-size means are averages of quantized readings and the README's 'p99 better almost in all test cases' compares tick multiples (83 vs 166 ns). On amd64 every sample carries a floor (p0 = 29 ns in each file read) that dilutes, rather than inflates, the reported gains.
- Workload skew: queries are uniform in [0, 8n) while the arrays end near 4.5n on average, so about 44% of queries are past the last element; for those the SIMD block scan never runs and both algorithms walk the same rightmost path. 'Warm' means 128 consecutive queries per array (README says 100) over a 4 GB array set, so the first queries on each array are still cold.
- No result cross-check: the benchmark returns results to JMH without comparing them, and the Spock tests use arrays of at most 51 elements, so the quaternary loop (it only runs with more than 3 blocks, i.e. 64+ elements) is never tested. Reading the loop, its invariant holds (the target is at most the end key of block hi unless hi is the last block, and the remainder tail is scanned linearly), so no correctness bug was found.
- blockSearch assumes the preferred vector holds at most 16 ints and divides 16 (true for NEON, AVX2 and AVX-512); on a wider vector length IntVector.fromArray on the final block would read past the array end and throw.

## Known shortcomings

- AMD CPU model unnamed and JDK builds unstated; README percentages are best-cell time cuts (max 29.3%, about 1.41x); SIMD is slower than binarySearch in 2 warm cells and the non-SIMD quad search is slower than binarySearch on arm64; about 44% of queries fall past the last element. Java.
- Harness flaw: on arm64 the JMH SampleTime percentiles come in about 41.7 ns steps while the means are 24-37 ns, so small-size means and the 'p99 better' claim rest on quantized timer readings; on amd64 a 29 ns p0 floor dilutes the gains. Queries are uniform in [0, 8n) while arrays end near 4.5n, so about 44% of queries fall past the array end and never run the SIMD block scan; unit tests use at most 51 elements, so the quaternary loop (64+ elements) is never tested; blockSearch assumes a vector of at most 16 ints. Loop invariant read and found sound; no correctness bug.

## Caveats and trade-offs

Gains are modest (about 10 to 29%). In the 1m cold sample file the non-SIMD quadSearch variant beat the SIMD variant, so the win comes mostly from quaternary narrowing and cache behaviour rather than SIMD. Idea credited to a Daniel Lemire blog post. CPU models are not stated, so tier C although JMH files are in the repo.

Needs --add-modules jdk.incubator.vector (incubator module); int arrays only; same return semantics as Arrays.binarySearch.

## Maintenance

Weekend experiment from May 2026 (Apache-2.0, 3 stars, 12 commits, no release or artifact); small enough to copy, but SimdQuadSearch ties you to the incubating Vector API and the code has no tests at sizes where the quaternary loop runs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party JMH harness is public (src/jmh/java/dev/yavuztas/javafast/search/ArraySearch{Cold,Hot}CacheBenchmark.java, run-benchmarks.sh, JVM args in build.gradle) and all 72 result files are in docs/results/{amd64,arm64}, but the x86-64 AMD CPU model is not named anywhere (README, results files, docs/index.html chart titles say only 'x86-64 AMD') and the exact JDK builds are not stated, so it falls short of A.
- **Verifier notes:** Numbers, sizes and README percentages all check out against docs/results; the search code keeps Arrays.binarySearch return semantics and looks correct. The record's caveat that the gain comes mostly from quaternary narrowing holds on amd64 only: on arm64 the non-SIMD quadSearch is slower than binarySearch at 4k to 16k cold (up to 18% slower) and the SIMD scan carries the win; simdQuadSearch is itself slower than binarySearch in amd64 GraalVM 16k warm (206.206 vs 197.172 ns/op) and arm64 GraalVM 4k warm (34.412 vs 33.388), and p99 is worse in a few cells. Java-only project (Vector API incubator, --enable-preview), 3 stars, 12 commits, no releases.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`
- **Shortcomings recorded by:** verifier batch-58 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/java-fast/quad-search>
  - <https://github.com/java-fast/quad-search/commits>
  - <https://github.com/java-fast/quad-search/tree/main/docs/results>
  - <https://github.com/java-fast/quad-search/tree/main/docs/results/amd64>
  - <https://github.com/java-fast/quad-search/tree/main/src>
  - <https://github.com/java-fast/quad-search/blob/main/run-benchmarks.sh>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/README.md>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/build.gradle>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/docs/index.html>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/docs/results/amd64/benchmark-oracle-openjdk-1m-cold.txt>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/docs/results/arm64/benchmark-oracle-openjdk-4k-hot.txt>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/src/jmh/java/dev/yavuztas/javafast/search/ArraySearchColdCacheBenchmark.java>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/src/jmh/java/dev/yavuztas/javafast/search/ArraySearchHotCacheBenchmark.java>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/src/main/java/dev/yavuztas/javafast/search/QuadSearch.java>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/src/main/java/dev/yavuztas/javafast/search/SimdQuadSearch.java>
- **Sources the enricher read:**
  - <https://github.com/java-fast/quad-search>
  - <https://github.com/java-fast/quad-search/commits/main>
  - <https://github.com/java-fast/quad-search/tree/main/src/test>
  - <https://github.com/java-fast/quad-search/tree/main/src/test/groovy/dev/yavuztas/javafast/search>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/README.md>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/build.gradle>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/settings.gradle>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/run-benchmarks.sh>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/src/main/java/dev/yavuztas/javafast/search/QuadSearch.java>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/src/main/java/dev/yavuztas/javafast/search/SimdQuadSearch.java>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/src/main/java/dev/yavuztas/javafast/search/BranchlessQuadSearch.java>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/src/jmh/java/dev/yavuztas/javafast/search/ArraySearchColdCacheBenchmark.java>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/src/jmh/java/dev/yavuztas/javafast/search/ArraySearchHotCacheBenchmark.java>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/src/test/groovy/dev/yavuztas/javafast/search/SimdQuadSearchSpec.groovy>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/src/test/groovy/dev/yavuztas/javafast/search/QuadSearchSpec.groovy>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/src/test/groovy/dev/yavuztas/javafast/search/BranchlessQuadSearchSpec.groovy>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/docs/results/arm64/benchmark-oracle-openjdk-4k-hot.txt>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/docs/results/arm64/benchmark-oracle-openjdk-4k-cold.txt>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/docs/results/amd64/benchmark-oracle-openjdk-4k-hot.txt>
  - <https://raw.githubusercontent.com/java-fast/quad-search/HEAD/docs/results/amd64/benchmark-graalvm-16k-hot.txt>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/tree/master/2026>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/tree/master/2026/04>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/tree/master/2026/04/26>
  - <https://raw.githubusercontent.com/lemire/Code-used-on-Daniel-Lemire-s-blog/master/2026/04/26/post.md>
  - <https://raw.githubusercontent.com/lemire/Code-used-on-Daniel-Lemire-s-blog/master/2026/04/26/applem4.txt>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/java-fast/quad-search`) · [data/wave13/enrich/raw/github_com_java_fast_quad_search.json](../../../data/wave13/enrich/raw/github_com_java_fast_quad_search.json) (enrichment confidence 0.8)

</details>
