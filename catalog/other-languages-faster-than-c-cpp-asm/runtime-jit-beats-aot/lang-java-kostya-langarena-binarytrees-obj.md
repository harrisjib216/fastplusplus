# OpenJDK HotSpot (Java 27): LangArena Binarytrees::Obj

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `MIT` · 🟢 active

> OpenJDK 27 (default G1, -Xmx2g) building and summing depth-20 object trees 4.4x faster than every make_unique C++ and malloc C build.

| | |
|---|---|
| **Beats** | C++ (std::make_unique tree nodes, g++ 16 and clang++ 22) and C (malloc'd nodes); best C/C++ configuration is C++/G++/Fast at 2.098 s |
| **Claimed result** | Java/OpenJDK 0.479 s vs C++/G++ 2.101 s (prod, -O2), C++/G++ -O3 'Fast' 2.098 s (best of the 16 C/C++ prod, Fast, Unsafe and PGO configurations; only the instrumented C++/Clang++/PGO/Gen build is lower at 2.081 s), C/Clang 2.482 s: about 4.4x faster than C++/G++ and 5.2x faster than C/Clang (derived from page data). Kotlin/JVM 0.479 s (Kotlin/JVM/Opt 0.428 s), Scala/JVM 0.48 s, GraalVM JIT 0.807 s. |
| **Workload** | Allocate, sum and free a complete binary tree of individually allocated nodes, repeated per iteration (idiomatic object version of binary-trees). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++: Clang 22.1.8 (official LLVM release tarball; the clang_cpp container aliases g++ to clang++ and links the system libstdc++, no -stdlib=libc++) and GCC 16.0.1 20260322 (trunk, Ubuntu build), -std=c++20, glibc malloc. Headline 'prod' build (cpp/Makefile CXXFLAGS_PROD): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections (not -O3). The same suite also builds 'Fast' (-O3 -march=native -mtune=native -pipe -fstack-protector -ftree-vectorize -funroll-loops), 'Unsafe' (-O3 -march=native -ffast-math -fno-stack-protector -fomit-frame-pointer -fvisibility=hidden -fno-trapping-math) and 'PGO' (-O2 plus -fprofile-instr-use or -fprofile-use) variants of every C and C++ benchmark; the Makefile passes -flto=thin (Fast) and -flto=full (Unsafe) only at the link step while the objects are compiled without -flto, so those builds probably get no LTO (inference from cpp/Makefile). All 16 Clang/GCC x C/C++ x prod/Fast/Unsafe/PGO configurations were compared here (instrumented PGO/Gen rows excluded). Managed side: Temurin OpenJDK 27+35 run as 'java -Xmx2g -jar' (default G1 GC, C2 JIT), GraalVM CE 25.4.4.1.1 (JDK 25.0.4.1.1) with -Xmx2g, dotnet 11.0.100-rc.1 (Release), Julia 1.13.1 with --threads=16 (versions and run commands from the results file). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Inferred from the sources, not stated by the suite: the C++ tree allocates every node with make_unique (one malloc/free per node and recursive destruction), while HotSpot allocates short-lived objects by pointer bump in thread-local buffers and reclaims them with a generational GC. The suite's own index-based Arena variant reverses the result (C/Gcc/Fast 0.255 s vs Java 1.086 s). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

LangArena's 2026-10-05 run on an AMD Ryzen 7 3800X (Linux, Docker) timed 30 depth-20 build-sum-free iterations at 0.479 s for Temurin OpenJDK 27+35 (-Xmx2g, default G1) against 2.098 s for the best C/C++ configuration (C++/G++/Fast, GCC 16.0.1 trunk, -O3 -march=native, std::make_unique nodes, glibc malloc) and 2.482 s for C/Clang 22.1.8; about 4.4x and 5.2x faster (derived from page data), with each language's checksum checked against the expected 75497436.

## Use it when

- JVM services that build and discard large pointer-linked structures (ASTs, document trees, temporary graphs) and are judged on throughput: idiomatic object code with default G1 beat idiomatic make_unique C++ by about 4.4x here.
- Deciding whether to rewrite such code in C++: unless the C++ version will use an arena or pool, this result says per-node new/delete will likely be slower.
- Hosts with spare cores and memory headroom, which G1's parallel workers and a 2 GB heap exploit; even single-threaded SerialGC at 512 MB still beat every C and C++ build (0.886 s vs 2.098 s).
- Other JVM languages: Kotlin/JVM (0.479 s default, 0.428 s with -Xms2g pre-touched G1) and Scala/JVM (0.48 s) share the result.

## Skip it when

- As evidence that Java beats C with an arena: the suite's C index arena grown by realloc (C/Gcc/Fast 0.255 s, 27 MB) is about 1.9x faster than this Java row and uses about 33x less memory.
- Memory-constrained deployments: peak RSS was 892 MB for Java against about 70 MB for C++ and 66 MB for C (about 13x); the -Xms2g Kotlin/JVM/Opt variant reached 2155 MB.
- Latency-sensitive code: GC pauses are inside the 30-iteration total but are not reported separately, and the final collection is outside the timer.
- Other managed runtimes on the same workload: C#/JIT 4.373 s and Julia 2.185 s are no faster than C++, so the win is HotSpot-specific, not a general GC property; GraalVM CE JIT is slower than HotSpot here (0.807 s).
- Most other LangArena tests: rows were picked where a managed runtime beats every C/C++ row; on Binarytrees::Arena the same Java code style (ArrayList of objects) takes 1.086 s.

## How it is fast

Allocation and reclamation, not better code generation. Likely mechanism (inference; the suite does not explain it): HotSpot allocates each 24-byte node by bumping a pointer in a thread-local allocation buffer and reclaims dead trees with generational copying collections whose cost depends on live data, not on the number of dead objects, while C++ calls operator new per node through std::make_unique and runs a recursive unique_ptr destructor that frees all 2.1 million nodes inside the timer (C does the same with malloc/free). That works out to about 7.6 ns per node for Java against 33.4 ns for the best C++ build and 39.5 ns for C/Clang (derived from page data over 62.9M timed nodes). The default G1 run also gets help from parallel GC worker threads: the same JVM limited to the single-threaded SerialGC and a 512 MB heap takes 0.886 s (14.1 ns per node).

## Compared with alternatives

Among catalogued Binarytrees::Obj rows, HotSpot (0.479 s) is about 2x faster than Bun's TypeScript/JS rows (0.973 s and 1.042 s), so pick it when you are on the JVM; compared with the benchLANG Java binary-trees entry, this one is stronger evidence because it measures 16 C/C++ build configurations, a single-threaded GC variant and an arena variant on the same machine.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | A JDK (Temurin OpenJDK 27+35 as measured); the tree code itself uses only java.lang; the suite's harness is a Maven project (java-benchmarks-1.0-SNAPSHOT.jar) run in its langarena:java Docker image |
| **Minimum toolchain** | OpenJDK 27+35 as measured (the previous LangArena run used OpenJDK 26.0.2); the tree class uses only basic Java features, but older JDKs were not measured in this results file |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X, 78 GB RAM) inside Docker with a 16 GB memory limit and no CPU limit |
| **Thread safety** | Not applicable: single-threaded workload; the JVM's GC and JIT threads run beside it |
| **Drop-in for the baseline** | no |

## Gotchas

- Parallel GC threads are in the Java timing but not in the table: benchmarks.rb records user and system time from /usr/bin/time for every run but saves only wall time and peak RSS, and the container has no CPU limit, so G1's parallel workers use the other cores of the 8-core CPU while C++ runs on one. The suite's own Java/OpenJDK/Serial row (-XX:+UseSerialGC -Xmx512m, 0.886 s) cuts the margin over the best C/C++ build from 4.4x to 2.4x, so about half of the headline comes from GC threads and heap size.
- Timing asymmetry: the Java harness calls System.gc() after warm-up and again after the timer stops, so the timed loop starts with an empty heap and the last young generation's garbage is collected untimed, while the C and C++ programs free every node inside each timed iteration.
- The record's arena comparison needs care: Java's Binarytrees::Arena is an ArrayList&lt;TreeNode&gt; that still allocates one object per node, so its 1.086 s is not an arena result. Comparing like with like, the realloc-grown C arena (0.255 s) beats Java's object tree (0.479 s), but the C++ std::vector arena, grown by emplace_back without reserve and rebuilt each iteration, does not (best C++/G++/Unsafe 0.512 s, prod C++/G++ 0.569 s, C++/Clang++ 0.685 s).
- One in-process timing per configuration, no repeats or variance, and JIT warm-up excluded (6 untimed iterations); the C and C++ 'prod' headline rows are -O2 with hardening flags, though the -O3, fast-math and PGO builds land within 2.098 to 2.498 s, so the baseline is not crippled.

## Known shortcomings

- Java 0.479 s vs C++/G++/Fast 2.098 s is the classic GC-against-per-node-malloc/free case: the suite's own Arena variant reverses it, the C++ timing includes frees while the JVM's final GC is untimed, and the JVM uses 13x more memory; LTO flags only at the link step.
- Harness flaw: benchmarks.rb collects user and sys time but saves only wall time and RSS, and Docker has no CPU limit, so G1's parallel workers run on spare cores; the suite's own Java/OpenJDK/Serial row (-XX:+UseSerialGC -Xmx512m) at 0.886 s cuts the margin from 4.4x to 2.4x against C++/G++/Fast 2.098 s; Java runs System.gc() before and after the timer, both untimed. Record caveat corrected: the Java 'Arena' 1.086 s row is an ArrayList of objects, not an arena; like for like, the C realloc arena at 0.255 s beats Java Obj 0.479 s, but a C++ std::vector arena without reserve does not (best 0.512 s, prod G++ 0.569 s).

## Caveats and trade-offs

The win is allocation-strategy specific: a C/C++ arena or pool allocator beats the JVM here (Binarytrees::Arena, C/Gcc/Fast 0.255 s vs Java 1.086 s), so 'Java beats C++' only holds against per-node malloc/free and unique_ptr destruction. The C++ timed region includes freeing each tree, while the JVM's last collection (System.gc() after the timer) is not timed; young collections during the run are timed. Memory trade: Java/OpenJDK RSS 892 MB (Kotlin/JVM/Opt 2155 MB) vs C++ 70 MB. Workload: depth-20 tree, 30 timed iterations. LangArena's own README calls it 'a subjective benchmark', and the author says AI tools helped translate the tests between languages. benchmarks.rb runs each test once per configuration in its own process and records that single in-process timing (no repeats, no variance). Every language, C and C++ included, runs a warm-up of 20% of the iterations before the timer starts, so JIT compilation and startup are excluded. The headline C/C++ 'prod' rows are -O2 with hardening flags, but the -O3, PGO and fast-math variants were also measured and still lose on this test; the Makefile's LTO flags are link-only, so no configuration had real LTO. Rows were selected by the search agent as tests where a managed-runtime row beats every C/C++ row; most other tests in the suite go the other way (for example Sort::Quick, Sort::Merge and the Binarytrees::Arena variant). The per-benchmark ratios are derived from the results file, not stated by the suite. [retier] benchmarks.rb collects user and sys time but saves only wall time and RSS, and Docker has no CPU limit, so G1's parallel workers run on spare cores; the suite's own Java/OpenJDK/Serial row (-XX:+UseSerialGC -Xmx512m) at 0.886 s cuts the margin from 4.4x to 2.4x. Correction: the Java 'Arena' 1.086 s row is an ArrayList of objects, not an arena; like for like, the C realloc arena at 0.255 s beats Java Obj 0.479 s, but a C++ std::vector arena without reserve does not (best 0.512 s, prod G++ 0.569 s).

Peak RSS about 892 MB for Java vs about 66 MB for C/Clang on this test; needs a JVM and warm-up; other runtimes do not share the win on this test (C#/JIT 4.373 s, Julia 2.185 s).

## Maintenance

Actively maintained MIT suite (41 stars, 622 commits, last commit 2026-10-08, monthly reruns) with public code, flags and per-configuration results; the per-test numbers are single runs and the author calls the suite subjective, with AI-assisted translations reviewed by hand.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent third-party suite with public code for both sides (cpp/src/binarytrees.cpp and .hpp, c/src/binarytrees.c, java/src/main/java/benchmarks/Binarytrees.java), flags in cpp/Makefile and the results file's run-cmd entries, compiler and JVM versions and the CPU (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js; the record's numbers match the Binarytrees::Obj-runtime rows.
- **Verifier notes:** Numbers verified (Java/OpenJDK 0.479 s, C++/G++ 2.101 s, C++/G++/Fast 2.098 s, C/Clang 2.482 s, Kotlin 0.479 s, Scala 0.48 s, GraalVM JIT 0.807 s); 'best of 16' is right once the instrumented PGO/Gen rows are excluded (C++/Clang++/PGO/Gen 2.081 s). Shortcomings: classic GC-vs-malloc case, reversed by the suite's own arena variant; C++ timing includes per-node frees while the JVM's final GC is untimed; 13x more memory on the JVM; single run per configuration.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-25 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/tree/master/cpp/src>
  - <https://github.com/kostya/LangArena/tree/master/java>
  - <https://github.com/kostya/LangArena/tree/master/java/src/main/java/benchmarks>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker-compose.yaml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/clang_cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/base_clang>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/gcc_cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/main.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Benchmark.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/binarytrees.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/binarytrees.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Binarytrees.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/binarytrees.c>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue%20binarytrees>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Binarytrees.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Benchmark.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/binarytrees.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/binarytrees.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/binarytrees.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker-compose.yaml>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:java/kostya/langarena#binarytrees-obj`) · [data/wave14/enrich/raw/lang_java_kostya_langarena_binarytrees_obj.json](../../../data/wave14/enrich/raw/lang_java_kostya_langarena_binarytrees_obj.json) (enrichment confidence 0.8)

</details>
