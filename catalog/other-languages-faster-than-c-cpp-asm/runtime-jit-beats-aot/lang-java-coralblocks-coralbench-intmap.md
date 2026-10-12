# HotSpot Java IntMap put latency vs C++ clang++ -O3: coralblocks/CoralBench

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> CoralBlocks' paired Java/C++ IntMap latency benchmark; Java's PUT 'win' comes from a C++ map that grew buckets.

| | |
|---|---|
| **Beats** | C++ IntMap as it stood in December 2024 (src/main/c/int_map.hpp at commit 46103a6: std::vector&lt;std::vector&lt;Entry&gt;&gt; buckets, 64-bit size_t keys, no bucket reserve, so the first three puts into each bucket malloc and reallocate the vector inside the timed region), built with clang++ 18.1.0 -Ofast -march=native -flto -std=c++17 and driven by src/main/c/int_map_benchmark.cpp. The current header (pre-sized buckets since commit 9281b82, 32-bit keys since 259d856, both 2026-08-28) has never been benchmarked in the README. |
| **Claimed result** | No valid speedup. The hidden README section shows PUT 31.34 ns avg for HotSpot with Graal JVMCI (Oracle GraalVM 25.0.4.1, re-run 2026-08-28) and 32.40 ns for HotSpot C2 against C++ 47.75 ns (about 1.5x, derived from page data); GET 26.92 ns and 29.13 ns vs C++ 25.98 ns (parity); DEL 36.29 ns and 37.73 ns vs C++ 25.93 ns (C++ about 1.4x faster). The C++, C2, -Xcomp and native-image outputs are unchanged from the December 2024 README (Java 23.0.1 era), and the C++ PUT figure was measured on code whose PUT grew bucket vectors inside the timer. |
| **Workload** | Integer-keyed hash map put, get and remove: 3,000,000 measured operations per method, map capacity 1,000,000, warm-up 0, per-operation latency in nanoseconds from the repo's Bench class. |
| **Metric** | latency |
| **Hardware** | Intel Xeon E-2288G @ 3.70GHz, Ubuntu 18.04.6 LTS, kernel 4.15.0-20-generic |
| **Compiler and flags** | C++ numbers: Ubuntu clang 18.1.0, clang++ -Ofast -march=native -flto -std=c++17 (December 2024 README); commit f11598d later changed the README commands to -O3 without re-running, so the -O3 commands shown next to the C++ output did not produce it. Java JVMCI run: Oracle GraalVM 25.0.4.1 HotSpot, java -XX:+AlwaysPreTouch -Xms4g -Xmx4g -XX:NewSize=512m -XX:MaxNewSize=1024m. HotSpot C2 (-XX:-UseJVMCICompiler), -Xcomp and native-image outputs date from the earlier Java 23.0.1 run. The C++ standard library is not stated (Ubuntu clang defaults to libstdc++ unless -stdlib is given). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Adoption** | 15 stars |
| **Last commit** | 2026-08-30 |
| **Links** | [repository](https://github.com/coralblocks/CoralBench) · [benchmark](https://raw.githubusercontent.com/coralblocks/CoralBench/main/README.md) |

## Verdict

A section of README.md hidden in an HTML comment shows, on an Intel Xeon E-2288G under Ubuntu 18.04.6, PUT 31.34 ns (Oracle GraalVM 25.0.4.1 JVMCI, 2026 run) and 32.40 ns (HotSpot C2, Java 23.0.1, 2024) against 47.75 ns for C++ (Ubuntu clang 18.1.0 -Ofast -march=native -flto, 2024, standard library not stated); GET 26.92 and 29.13 ns against 25.98 ns; DEL 36.29 and 37.73 ns against 25.93 ns. The PUT gap comes from the C++ map growing bucket vectors inside the timer, so no valid measurement shows Java faster.

## Use it when

- As a template for paired Java and C++ per-operation latency benchmarks with percentile output (Bench.java and bench.cpp have matching mark/measure/printResults APIs).
- To study how HotSpot C2, Graal JVMCI, -Xcomp and native-image compare on the same small Java loop; the README's other sections show warm-up versus -Xcomp effects on Math, BubbleSort and Sleep examples.
- To reproduce the comparison properly: the current C++ header (pre-sized buckets, 32-bit keys) has never been benchmarked, so a fresh run of both sides on one machine with equal warm-up would be new data.

## Skip it when

- As evidence that a JIT beats ahead-of-time C++: the only Java win rests on unequal work, the C++ output dates from 2024 and an -Ofast build, the Java JVMCI output from 2026, and the author hid the whole section in an HTML comment.
- As a hash map for production use in either language: IntMap is a teaching example (per-bucket list chaining, modulo indexing, no resizing), not a tuned map.
- When tail latency matters more than mean: the published Java PUT maximum is 211.7 us against 18.4 us for C++ even though the 99.9th-percentile maximum is lower in Java.
- When deletes dominate: published DEL is 36-38 ns in HotSpot against 26 ns for C++, partly because Java remove also returns each Entry to a pool list.

## How it is fast

There is no demonstrated speedup. The only operation where Java looked faster, PUT, benefits from allocation asymmetry: the Java map pre-sizes every bucket ArrayList to 3 entries in its constructor and each put bump-allocates one small Entry object from the thread-local allocation buffer of a 4 GB heap pre-faulted by -XX:+AlwaysPreTouch, while the December 2024 C++ map started each bucket as an empty std::vector, so its three puts per bucket paid malloc, reallocation and element moves (plus first-touch page faults) inside the timer. GET is at parity and DEL is faster in C++.

## Compared with alternatives

Do not pick it for evidence: the HotSpot benchLANG binary-trees and LangArena Binarytrees siblings record measured Java wins on allocation-heavy workloads, while this entry records none. Its only edge over them is a matched per-operation latency harness with percentiles in both languages.

## Integration

| | |
|---|---|
| **Form** | source-drop (Maven project for the Java Bench class and examples; C++ bench.cpp/bench.hpp plus header-only int_map.hpp) |
| **Dependencies** | Java: CoralDS 1.3.5 (LinkedList and LongMap); JUnit 4.13.1 and Mockito 4.11.0 for tests only. C++: standard library only. |
| **Minimum toolchain** | Java 17 (maven.compiler.release 17); C++17 (clang++ -std=c++17 in bin/compileIntMapBenchmarkCpp.sh) |
| **Platforms** | measured on x86-64 Linux (Intel Xeon E-2288G, Ubuntu 18.04.6); the run scripts also handle macOS since August 2026 |
| **Thread safety** | not documented; IntMap and Bench have no synchronisation and are used from one thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry behind the PUT numbers: Java buckets (ArrayList plus backing array) are allocated in the constructor outside the timer and the heap is pre-faulted with -XX:+AlwaysPreTouch, while the 2024 C++ IntMap (commit 46103a6) had no reserve and no pre-faulting, so every bucket's malloc, two reallocations and first page touch fell inside the timed puts; the reserve was added on 2026-08-28 (9281b82) but C++ was never re-run.
- The 2024 Java benchmark discarded get()'s return value ('map.get(i);'), while the C++ driver stored it into a volatile; only the 2026 JVMCI output prints 'Values found: 3000000', so the C2, -Xcomp and native-image GET rows still come from a loop whose result was unused.
- Shipped scripts compare different work by default: runIntMapBenchmarkJavaC2.sh and runIntMapBenchmarkJavaJVMCI.sh default to 1,000,000 warm-up iterations (commit 58888dd 'Raise Java benchmark warm-up defaults'), runIntMapBenchmarkCpp.sh defaults to 0; warm-up puts insert keys without being measured and change initialBucketSize, so re-running with defaults gives Java an easier measured set.
- Each 20-50 ns operation is bracketed by two clock reads (steady_clock::now, System.nanoTime), so timer cost is a large share of every sample (published minimums of 15-40 ns), and each sample then updates a 2^22-bucket histogram (std::unordered_map in C++, CoralDS LongMap in Java) that touches cache between operations.

## Known shortcomings

- Crippled baseline: the C++ IntMap was built -Ofast without a bucket reserve, so PUT paid malloc plus vector reallocation inside the timer while the Java map was pre-sized; the author hid the whole Java-vs-C++ section in an HTML comment (commit d3f73f5, 2026-08-28), later added reserve (9281b82) and changed the flags text to -O3 without re-running C++; the JVMCI 31 ns row is a 2026 run paired with 2024 C++ output; GET parity, DEL Java slower.
- Beyond the verifier's findings: the Java heap is pre-faulted (AlwaysPreTouch) and the buckets are allocated outside the timer, while the 2024 C++ run paid malloc plus page faults inside the timer; the 2024 Java GET discarded the get() result while C++ stored to a volatile, and only the 2026 JVMCI run prints 'Values found'; the Java run scripts default to a 1,000,000 warm-up while the C++ script uses 0 (commit 58888dd).

## Caveats and trade-offs

The Java-vs-C++ section sits inside an HTML comment (&lt;!-- ... --&gt;) that the author added in commit d3f73f5 ('Revise benchmark data and Java version in README', 2026-08-28), so it does not render on github.com and reads as withdrawn or unfinished. Unequal work: the C++ map that produced the 47.75 ns PUT figure started with empty bucket vectors (no reserve), so PUT paid malloc plus vector reallocation and copy for the first three entries of every bucket inside the timer, while the Java IntMap pre-sized every bucket ArrayList to initialBucketSize = 3 and only bump-allocated an Entry; the author added the matching reserve to C++ on 2026-08-28 (commit 9281b82 'Pre-size C++ IntMap buckets') but did not re-run C++. The 2024 C++ map also used 64-bit size_t keys and 64-bit modulo against Java's 32-bit int keys. Cross-run comparison: the JVMCI figures were re-measured with Java 25.0.4.1 in 2026 (PUT 28.04 ns became 31.34 ns), while C++ and the other Java modes are 2024 outputs; the environment block lists only the 2026 versions. Not the same data structure: C++ stores entries inline in each bucket vector, Java stores references to pooled Entry objects. Mixed result even as published: Java ties GET and loses DEL. One run per configuration with warm-up 0, so JIT compilation is inside the measured region; the C++ and Java Bench classes use different histogram maps (std::unordered_map vs CoralDS LongMap) outside the timed span. [retier] The Java heap is pre-faulted (AlwaysPreTouch) and the buckets are allocated outside the timer while the 2024 C++ run paid malloc plus page faults inside the timer; the 2024 Java GET discarded the get() result while C++ stored to a volatile; the Java run scripts default to a 1,000,000 warm-up while the C++ script uses 0.

Java run needs a 4 GB pre-touched heap and a JVM. Worst-case PUT latency is higher in Java (maximum 211.7 us vs 18.4 us for C++), although the 99.9th-percentile maximum is lower (277 ns vs 1,040 ns).

## Maintenance

Active vendor repository (CoralBlocks LLC, Apache-2.0, 15 stars, 397 commits, last commit 2026-08-30 with release 1.4.3), usable as a harness template, but the Java-versus-C++ comparison is withdrawn into an HTML comment and rests on stale, asymmetric C++ output, so it is tier D.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The numbers are in README.md, but the whole Java-vs-C++ section was wrapped in an HTML comment by the same commit that last revised it (d3f73f5, 2026-08-28), and the C++ output is byte-identical to the December 2024 README: it came from an -Ofast build of a C++ IntMap that did not pre-size its buckets, while the Java IntMap did. The only PUT win therefore rests on unequal work (crippled-baseline precedent) plus a cross-run pairing with the 2026 JVMCI run, so no valid measurement supports a Java speedup.
- **Verifier notes:** Downgrade C to D: the only Java win (PUT) compares a pre-sized Java map with a 2024 C++ map that reallocated buckets inside the timer, the author fixed that asymmetry and switched the flags text to -O3 on 2026-08-28 without re-running C++, paired the stale C++ output with a fresh 2026 JVMCI run, and hid the whole section in an HTML comment. Not a reject (the code and outputs are real and public), but no valid measurement shows Java faster; GET is parity and DEL is slower in Java. Metadata checked: Apache-2.0, 15 stars, 3 forks, last commit 2026-08-30, active.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-54 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/README.md>
  - <https://github.com/coralblocks/CoralBench>
  - <https://github.com/coralblocks/CoralBench/commits/main>
  - <https://github.com/coralblocks/CoralBench/commits/main/README.md>
  - <https://github.com/coralblocks/CoralBench/commits/main/src/main/c/int_map.hpp>
  - <https://github.com/coralblocks/CoralBench/commit/d3f73f5>
  - <https://github.com/coralblocks/CoralBench/commit/f11598d>
  - <https://github.com/coralblocks/CoralBench/commit/6817e95>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/c/int_map.hpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/c/int_map_benchmark.cpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/c/bench.cpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/c/bench.hpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/java/com/coralblocks/coralbench/example/IntMap.java>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/java/com/coralblocks/coralbench/example/IntMapBenchmark.java>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/java/com/coralblocks/coralbench/Bench.java>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/README.md>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/c/int_map.hpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/c/int_map.cpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/c/int_map_benchmark.cpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/java/com/coralblocks/coralbench/example/IntMap.java>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/java/com/coralblocks/coralbench/example/IntMapBenchmark.java>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/33df33e/README.md>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/33df33e/src/main/c/int_map.hpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/f11598d/src/main/c/int_map.hpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/d3f73f5/README.md>
- **Sources the enricher read:**
  - <https://github.com/coralblocks/CoralBench>
  - <https://github.com/coralblocks/CoralBench/commits/main>
  - <https://github.com/coralblocks/CoralBench/issues?q=is%3Aissue>
  - <https://github.com/coralblocks/CoralBench/tree/main/bin>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/README.md>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/pom.xml>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/c/int_map.hpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/c/int_map_benchmark.cpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/c/bench.cpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/c/bench.hpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/java/com/coralblocks/coralbench/example/IntMap.java>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/java/com/coralblocks/coralbench/example/IntMapBenchmark.java>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/src/main/java/com/coralblocks/coralbench/Bench.java>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/bin/int_map.sh>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/bin/compileIntMapBenchmarkCpp.sh>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/bin/runIntMapBenchmarkCpp.sh>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/bin/runIntMapBenchmarkJavaJVMCI.sh>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/main/bin/runIntMapBenchmarkJavaC2.sh>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/README.md>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/c/int_map.hpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/c/int_map.cpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/c/int_map_benchmark.cpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/c/bench.cpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/c/bench.hpp>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/java/com/coralblocks/coralbench/example/IntMap.java>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/java/com/coralblocks/coralbench/example/IntMapBenchmark.java>
  - <https://raw.githubusercontent.com/coralblocks/CoralBench/46103a6/src/main/java/com/coralblocks/coralbench/Bench.java>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:java/coralblocks/coralbench#intmap`) · [data/wave14/enrich/raw/lang_java_coralblocks_coralbench_intmap.json](../../../data/wave14/enrich/raw/lang_java_coralblocks_coralbench_intmap.json) (enrichment confidence 0.65)

</details>
