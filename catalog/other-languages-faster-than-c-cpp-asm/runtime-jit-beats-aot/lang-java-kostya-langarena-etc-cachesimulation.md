# OpenJDK HotSpot (Java 27): LangArena Etc::CacheSimulation

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `MIT` · 🟢 active

> HotSpot (Temurin 27, default G1) runs LangArena's string-keyed LRU cache test 1.28x faster than the best C build and 1.6x faster than C++.

| | |
|---|---|
| **Beats** | C LRU cache with uthash and strdup'd key/value strings (best C/C++ configuration C/Gcc/Unsafe, -O3 -march=native -ffast-math with full LTO, 0.789 s; C/Gcc prod -O2 0.816 s) and C++ LRU with std::unordered_map&lt;std::string, Node\*&gt; plus a hand-rolled doubly linked list (C++/G++ 0.991 s) |
| **Claimed result** | Java/OpenJDK (Temurin 27, -Xmx2g, default GC) 0.617 s vs C/Gcc/Unsafe 0.789 s (best of the 16 Clang/GCC C and C++ configurations, PGO-instrumented builds excluded), C/Gcc 0.816 s (prod, -O2), C++/G++ 0.991 s, C++/G++/Fast 0.97 s: 1.28x faster than the best C row and 1.6x faster than C++/G++ (derived from page data). The JVM GC setting decides the result: Java/OpenJDK/Opt (ParallelGC, large pages, AlwaysPreTouch) 0.476 s (1.66x), but Java/OpenJDK/Serial (SerialGC, -Xmx512m) 0.996 s is slower than every Clang/GCC C row and on par with C++. C#/JIT 0.959 s and Julia 2.917 s are slower than C; Rust/PGO 0.74 s also beats C. Earlier monthly runs show only a 1.02-1.05x lead for Java/OpenJDK over the best C/C++ row: 1.05x on 2026-08-14 (0.758 vs 0.795 s), 1.05x on 2026-09-03 (0.751 vs 0.787 s), 1.02x on 2026-09-18 (OpenJDK 26.0.2, 0.754 vs 0.771 s), with the C rows steady at 0.77-0.82 s (derived from the results files). |
| **Workload** | LRU cache simulation: per iteration 1000 get/put operations on keys 'item_N' (N from the suite's pseudo-random generator, formatted per operation) with values 'new_&lt;iter&gt;' or 'updated_&lt;iter&gt;'; hash map plus doubly linked list nodes allocated per entry and evicted at capacity. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++: Clang 22.1.8 and GCC 16.0.1 20260322 (trunk). Headline 'prod' build is -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer (not -O3). The same suite also builds 'Fast' (-O3 -march=native -mtune=native -funroll-loops, thin LTO), 'Unsafe' (-O3 -march=native -ffast-math, full LTO) and 'PGO' (-O2 plus profile) variants of every C and C++ benchmark; all 16 Clang/GCC x C/C++ configurations were compared here. Managed side: Temurin OpenJDK 27+35 with -Xmx2g, dotnet 11.0.100-rc.1 (Release), Julia 1.13.1 with --threads=16 (versions from the results file). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite (agent inference: cheap per-node allocation and HashMap behavior on HotSpot versus malloc/free of linked-list nodes in C/C++). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

In the 2026-10-05 LangArena run on an AMD Ryzen 7 3800X under Linux, Temurin OpenJDK 27 (default G1, -Xmx2g) took 0.617 s for 5,000 timed iterations of 1,000 LRU operations. That compares with 0.789 s for the best of 16 Clang/GCC C and C++ builds (C/Gcc/Unsafe: GCC 16.0.1 trunk, -O3 -march=native -ffast-math, uthash, glibc snprintf and malloc) and 0.991 s for C++/G++ at -O2 with libstdc++ std::unordered_map: 1.28x and 1.6x faster (derived from page data). In the four earlier monthly runs on OpenJDK 26 the lead was 1.02-1.05x.

## Use it when

- Deciding whether a JVM service's in-process LRU or session cache (short string keys, small values, steady eviction churn) needs a C or C++ rewrite: at default settings HotSpot beat every C and C++ build here.
- Throughput-bound batch or server code on a warmed-up JVM that is dominated by building short strings, hashing fresh keys and allocating small nodes, where bump allocation plus young-generation GC replaces malloc/free.
- Hosts with hundreds of MB of heap headroom and a throughput collector (G1 or ParallelGC; the tuned ParallelGC row reached 0.476 s, 1.66x faster than C).
- As a reference point for how much a naive C/C++ cache (snprintf keys, strdup, node-based map) gives away to the JVM.

## Skip it when

- Memory-constrained deployments: peak RSS was 493 MB for Java against 3.2 MB for C and 6.5 MB for C++ on a cache that holds 2,500 entries.
- SerialGC or small heaps: Java/OpenJDK/Serial (-Xmx512m) took 0.996 s, slower than every Clang/GCC C row, and GraalVM CE 25 JIT (0.865 s) also lost to C.
- Latency-sensitive caches: the suite reports total runtime only, with no GC pause or tail-latency data.
- Against tuned C++: the C++ port stores each key twice as std::string, uses node-based std::unordered_map, copies the value into a std::optional on every hit and formats with snprintf; std::to_chars keys, an open-addressing map and pooled nodes were never measured (inference).
- As a stable result: under OpenJDK 26 the lead was only 1.02-1.05x in four runs (2026-07-14 to 2026-09-18); the 1.28x comes from one run, the first on JDK 27 and a newly installed Arch Linux host.

## How it is fast

The lead comes from runtime and library behaviour rather than from JIT code generation. Allocation is a TLAB bump-pointer, and evicted nodes are reclaimed by a copying young-generation GC instead of one free() per node. String.hashCode is cached in each String, so a key is hashed once per operation, while C++ re-hashes std::hash&lt;std::string&gt; in get's find, put's find, erase(oldest-&gt;key) and operator[] (up to four times on a miss) and C runs strlen plus uthash's Jenkins hash in every HASH_FIND_STR and HASH_ADD_STR. Java builds 'item_'+n through invokedynamic string concatenation (javac target 21), while C and C++ call glibc snprintf twice per operation and C then strdup()s key and value. None of this was profiled by the suite; the breakdown is inference from the code.

## Compared with alternatives

Among the catalogued LangArena HotSpot rows, Binarytrees::Obj (0.479 s vs 2.098 s, about 4.4x) and Calculator::Ast (about 1.8x) show the allocation advantage far more clearly; cite CacheSimulation only for string-keyed hash-map churn, where the margin is the thinnest and the least stable. Unlike the benchLANG and xemantic ring-of-nodes siblings, it puts a real hash table on the C side and shows the GC setting flipping the result.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | A JDK (Temurin OpenJDK 27+35 measured); the suite's harness also uses org.json for its config, but the task itself uses only java.util |
| **Minimum toolchain** | Java 21 bytecode (pom.xml source/target 21); measured on Temurin 27+35 with -Xmx2g |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X); any JVM platform in principle |
| **Thread safety** | Not thread-safe: single-threaded LRU over an unsynchronized HashMap |
| **Drop-in for the baseline** | no |

## Gotchas

- The Java port's removeOldest() leaves the evicted node's prev pointer set (C and C++ free the node; java.util.LinkedHashMap.afterNodeRemoval nulls both links for this reason). The harness also calls System.gc() between the warm-up and the timed loop, which moves the warmed cache into the old generation. Together these let a dead old-generation node keep every later-evicted node, with its key and value Strings, reachable for young collections (GC nepotism). This handicaps Java rather than inflating its result, and may be why the small-heap SerialGC rows lose while the ParallelGC row with -XX:+DisableExplicitGC is fastest (inference; the suite publishes no GC logs).
- The workload is reproducible and identical across languages: my Python replay gives checksum 3263751556 (run.js expects 3263751556) with both the C integer and the Java floating-point next_int formulas, which agree over the LCG's whole 139,968-draw period. The timed run has a 48.6% hit rate (2,431,556 hits, 2,568,444 misses in 5,000,000 operations), and the key sequence repeats about every 140 iterations.
- The 'Unsafe' and 'Fast' C builds do not get the LTO the record mentions: c/Makefile passes -flto=full or -flto=thin only on the link line, and the objects are compiled without -flto. Helper_next_int (helper.c) therefore stays an out-of-line cross-file call in every C build.
- One in-process timing per configuration and no variance. Java's System.gc() after the timer stops means garbage left in the heap at the end is never collected inside the timed region; C and C++ pay free() for every eviction inside the loop.

## Known shortcomings

- Java 0.617 s vs C/Gcc/Unsafe 0.789 s (1.28x) depends on the GC (the SerialGC row at 0.996 s loses to C) and earlier runs gave 1.02-1.05x; the time goes to snprintf/strdup/malloc against JVM string concatenation and TLAB allocation.
- Harness flaw: the Java port's removeOldest() leaves the evicted node's prev link set, and the harness's System.gc() before the timer moves the warmed cache into the old generation, so a dead node may keep every later-evicted node reachable for young collections (GC nepotism); this hurts Java rather than inflating the win and may explain why the SerialGC rows (0.996 s OpenJDK, 1.195 s GraalVM) lose to C while ParallelGC with DisableExplicitGC is fastest (0.476 s); inference only, no GC logs. The win is library-level: Java caches the String hash, C++ rehashes up to 4x per miss, and C and C++ call snprintf twice per operation. A Python replay reproduces checksum 3263751556 with a 48.6% hit rate. LTO in the Unsafe and Fast builds is link-only (objects built without -flto), so the record's 'full LTO' for C/Gcc/Unsafe did not apply. The 1.28x margin is from one run; earlier OpenJDK 26 runs gave 1.02-1.05x.

## Caveats and trade-offs

Margin is modest (1.28x over C) and most of it arrived with the JDK 27 upgrade; earlier runs show 1.02-1.05x. The win depends on the JVM GC configuration: the SerialGC row loses to C. Same hand-written LRU logic in all three languages, but the hash tables and string handling come from each language's own library (uthash plus strdup and glibc snprintf in C, std::unordered_map, std::string and snprintf in C++, HashMap and string concatenation in Java), so much of the measured time is string formatting, allocation and hashing rather than the LRU itself. Only Java wins; C# and Julia do not. LangArena's own README calls it a subjective benchmark ('not an objective, peer-reviewed, or industry-standard benchmark suite'), and the author says AI tools helped translate the tests between languages (each port reviewed, checksums verified). The suite publishes one measurement per test and configuration (no variance). Every language runs the same harness: prepare, a warm-up of 20% of the iterations on the same instance, then the timed run (Java calls System.gc() between warm-up and the timed loop), so startup is excluded for all. The headline C/C++ 'prod' rows are -O2 with hardening flags, but the 'Fast' (-O3 -march=native, thin LTO), 'Unsafe' (-O3 -ffast-math, full LTO) and PGO variants are in the same file and still lose on this test. Rows were selected by the search agent as tests where a managed-runtime row beats every C/C++ row; most of the 50 tests go the other way (for example Sort::Quick, Sort::Merge and Binarytrees::Arena). The 2026-10-05 run is the first on Temurin JDK 27 and on a new Arch Linux host install (the GCC 16 trunk build is unchanged); in the three earlier runs checked (2026-08-14, 2026-09-03, 2026-09-18, OpenJDK 26) Java still led but only narrowly, so most of the margin arrived with the JDK upgrade. Per-benchmark ratios are derived from the results files, not stated by the suite. [retier] The Java port's removeOldest() leaves the evicted node's prev link set, and the harness's System.gc() before the timer moves the warmed cache into the old generation, so dead nodes may keep later-evicted nodes reachable for young collections (GC nepotism; inference, no GC logs), which may explain why the SerialGC rows lose to C while ParallelGC with DisableExplicitGC is fastest (0.476 s). The win is library-level: Java caches the String hash, C++ rehashes up to 4x per miss, C and C++ call snprintf twice per operation. LTO in the Unsafe and Fast builds is link-only (objects built without -flto). The 1.28x margin is from one run; earlier OpenJDK 26 runs gave 1.02-1.05x.

Java peak RSS about 493 MB.

## Maintenance

Active MIT-licensed suite (41 stars, last commit 2026-10-08, monthly reruns; the Java CacheSimulation code has been unchanged since 2026-02-25). This is a benchmark row, not a library: use it as a language-level data point, and in real Java code use LinkedHashMap with accessOrder=true and removeEldestEntry rather than this port, which keeps links on eviction.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public code for both sides (c/src/cache_simulation.c, cpp/src/cache_simulation.cpp, java/src/main/java/benchmarks/CacheSimulation.java, shared harnesses), C/C++ flags in c/Makefile and cpp/Makefile, exact compiler and JDK versions, JVM run flags and the CPU model (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js; independent multi-language suite. All quoted runtimes match the Etc::CacheSimulation-runtime entries.
- **Verifier notes:** Numbers and flags check out; tier A stands. Shortcomings to record: single measurement per run, cherry-picked test, win depends on GC choice (SerialGC row 0.996 s loses to C 0.789 s), 1.28x margin new with JDK 27 (1.02-1.05x in the three prior runs), time dominated by snprintf/strdup/malloc vs JVM string concat and TLAB allocation rather than codegen, subjective suite with AI-assisted ports.
- **Fields the verifier corrected:** `baseline`, `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-26 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/tree/master/results>
  - <https://github.com/kostya/LangArena/tree/master/cpp/src>
  - <https://github.com/kostya/LangArena/tree/master/c/src>
  - <https://github.com/kostya/LangArena/tree/master/java>
  - <https://github.com/kostya/LangArena/tree/master/java/src/main/java/benchmarks>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Benchmark.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/cache_simulation.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/cache_simulation.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/cache_simulation.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/CacheSimulation.java>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://github.com/kostya/LangArena/commits/master/java/src/main/java/benchmarks/CacheSimulation.java>
  - <https://github.com/kostya/LangArena/commits/master/cpp/src/cache_simulation.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/cache_simulation.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.h>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/helper.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/helper.h>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/cache_simulation.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/cache_simulation.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/CacheSimulation.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Benchmark.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Helper.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/pom.xml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/share/classes/java/util/LinkedHashMap.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/share/classes/java/lang/String.java>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:java/kostya/langarena#etc-cachesimulation`) · [data/wave14/enrich/raw/lang_java_kostya_langarena_etc_cachesimulation.json](../../../data/wave14/enrich/raw/lang_java_kostya_langarena_etc_cachesimulation.json) (enrichment confidence 0.6)

</details>
