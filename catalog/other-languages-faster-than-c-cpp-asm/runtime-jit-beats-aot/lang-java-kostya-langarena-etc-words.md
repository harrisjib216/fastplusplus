# OpenJDK HotSpot (Java 27) and GraalVM JIT: LangArena Etc::Words

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `MIT` · 🟢 active

> HotSpot (Temurin 27) and GraalVM JIT split and count a 50,000-word text 1.25-1.4x faster than every C and C++ build in LangArena Etc::Words.

| | |
|---|---|
| **Beats** | C++ splitting with std::istringstream and counting in std::unordered_map&lt;std::string,int&gt; (g++ 16, clang++ 22); best C/C++ configuration is C++/G++/PGO at 1.587 s |
| **Claimed result** | Java/OpenJDK 1.272 s vs C++/G++ 1.638 s (prod, -O2), C++/G++ -O3 'Fast' 1.651 s, best of all 16 C/C++ configurations 1.587 s: about 1.25x faster than the best row and 1.29x faster than the prod row (derived from page data). Java on GraalVM JIT 1.15 s (1.4x faster than the best row); C#/JIT 1.422 s also wins; Julia 1.857 s does not. |
| **Workload** | Split a large generated text into words and count word frequencies, then report the most frequent word. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++: Clang 22.1.8 (official LLVM release tarball; the clang_cpp container aliases g++ to clang++ and links the system libstdc++, no -stdlib=libc++) and GCC 16.0.1 20260322 (trunk, Ubuntu build), -std=c++20, glibc malloc. Headline 'prod' build (cpp/Makefile CXXFLAGS_PROD): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections (not -O3). The same suite also builds 'Fast' (-O3 -march=native -mtune=native -pipe -fstack-protector -ftree-vectorize -funroll-loops), 'Unsafe' (-O3 -march=native -ffast-math -fno-stack-protector -fomit-frame-pointer -fvisibility=hidden -fno-trapping-math) and 'PGO' (-O2 plus -fprofile-instr-use or -fprofile-use) variants of every C and C++ benchmark; the Makefile passes -flto=thin (Fast) and -flto=full (Unsafe) only at the link step while the objects are compiled without -flto, so those builds probably get no LTO (inference from cpp/Makefile). All 16 Clang/GCC x C/C++ x prod/Fast/Unsafe/PGO configurations were compared here (instrumented PGO/Gen rows excluded). Managed side: Temurin OpenJDK 27+35 run as 'java -Xmx2g -jar' (default G1 GC, C2 JIT), GraalVM CE 25.4.4.1.1 (JDK 25.0.4.1.1) with -Xmx2g, dotnet 11.0.100-rc.1 (Release), Julia 1.13.1 with --threads=16 (versions and run commands from the results file). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. The C++ version tokenizes with istringstream operator&gt;&gt; and allocates std::string keys; the Java version uses String.split and HashMap (agent inference: library-level differences). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

In the 2026-10-05 LangArena run on an AMD Ryzen 7 3800X under Linux, Temurin OpenJDK 27 (default G1, -Xmx2g) took 1.272 s for 360 timed iterations of splitting and counting a 50,000-word text. That compares with 1.587 s for the best of 16 Clang/GCC C and C++ builds (C++/G++/PGO, GCC 16.0.1 trunk, libstdc++ istringstream and unordered_map) and 1.638 s for C++/G++ at -O2: about 1.25x and 1.29x faster (derived from page data). GraalVM CE 25 JIT took 1.15 s (about 1.38x).

## Use it when

- Deciding whether a JVM log-processing, tokenizing or word-count job needs a C++ rewrite: idiomatic Java beat the idiomatic istringstream plus unordered_map C++ in all five monthly runs (2026-07-14 to 2026-10-05).
- Long-running JVM services or batch jobs that tokenize on a single ASCII delimiter and count a modest vocabulary (about 18.6k distinct 3-8 letter keys here) where the map fits in cache.
- Any JVM GC setup: all five Java rows (G1, ParallelGC 'Opt', SerialGC -Xmx512m, GraalVM CE JIT and GraalVM Serial) finished in 0.974-1.38 s, all faster than the best C++ row at 1.587 s.
- As a reference for how much a stream-based C++ tokenizer gives away compared with a split-into-substrings approach.

## Skip it when

- Memory-tight jobs: peak RSS was 309 MB for Java/OpenJDK and 445 MB for GraalVM JIT, against 7.8 MB for C++/G++ and 5.1 MB for C/Gcc.
- When you control the C++ code: the slow parts are istringstream and a node-based map. A std::string_view splitter with a flat or open-addressing map was never measured (inference), and in the same file Zig/Unchecked (0.57 s), Crystal (0.88 s) and Rust (1.021 s) beat Java with a few MB of RSS.
- General text: split(" ") splits on the single space character only, while operator&gt;&gt; splits on any locale whitespace (tabs, newlines). Both give the same counts here only because the generated text uses single spaces.
- One-shot command-line runs: the suite excludes JVM startup and a 72-iteration warm-up from timing; a single-pass word count would pay JVM start and JIT compilation.
- Results quoted as a JIT advantage: C# AOT (1.397-1.399 s) matched C# JIT (1.422 s), and the category label 'runtime-jit-beats-aot' does not fit this test.

## How it is fast

The win comes from the libraries and the allocator, not from JIT code generation. String.split with a one-character, non-regex delimiter takes the JDK's fast path (an indexOf loop plus substring copies, no java.util.regex). Each String caches its hashCode, so the second lookup (put after getOrDefault) does not re-hash, and counts of 1-9 come from the Integer cache, so boxing allocates nothing. Map nodes and substrings are bump-allocated in a TLAB and dropped wholesale by the young-generation GC. The C++ baseline instead uses std::istringstream, which copies the whole text into its stringbuf every iteration and builds a sentry plus a locale ctype whitespace test for every operator&gt;&gt; extraction. It inserts 18,623 nodes into a std::unordered_map&lt;std::string,int&gt; with no reserve and frees them all at the end of each timed iteration. Ahead-of-time compiled Zig, Crystal, Rust, Go and C# AOT also beat every C++ row, so this is not a JIT-specific effect (results file).

## Compared with alternatives

Use this row specifically for JVM-versus-C++ tokenize-and-count; the separately catalogued Crystal Etc::Words row (0.88 s) is faster with 8.8 MB RSS if the language is open. The LuaJIT word-count gist and LuaJIT k-nucleotide siblings show the same std::unordered_map&lt;std::string,int&gt; weakness, but with one-run, older evidence; this LangArena row has public code, flags and five monthly reruns.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | A JDK (Temurin OpenJDK 27+35 or GraalVM CE 25.0.4.1.1 measured); only java.util is used by the task (the harness reads its config with org.json) |
| **Minimum toolchain** | Java 21 bytecode (pom.xml source/target 21); measured on Temurin 27+35 and GraalVM CE 25.4.4.1.1, both with -Xmx2g |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X); any JVM platform in principle |
| **Thread safety** | Single-threaded; the HashMap is local to each run() call |
| **Drop-in for the baseline** | no |

## Gotchas

- The workload is a small-vocabulary hash test. The suite's LCG (IM 139968) repeats, so the 50,000-word text is an 18,656-word block repeated about 2.7 times, with 18,623 distinct words (all 3-8 letters, within libstdc++'s 15-byte small-string buffer) and one clear winner ('tea', 9 times). My Python replay reproduces run.js's checksum 1998586832 over 432 iterations (72 warm-up plus 360 timed). The C/C++ integer next_int formula and Java's floating-point one produce byte-identical texts, so every language does the same work.
- The Java code does more hash-map work than the C++ code, not less: getOrDefault then put is two lookups per word against C++'s single try_emplace. It still wins because the second lookup reuses the String's cached hash and the C++ cost sits in istream extraction and per-node malloc/free.
- No configuration got real LTO: cpp/Makefile passes -flto=thin (Fast) and -flto=full (Unsafe) only on the link line, and the objects are compiled without -flto. That hardly matters here, because the hot code is libstdc++ templates and istream calls inside words.cpp.
- One in-process timing per configuration with no variance. The direction has held for five months (Java/OpenJDK 1.09-1.25x ahead of the best C/C++ row; GraalVM JIT 1.03x in July and August, 1.29-1.38x since September), but the margin moves by about 15% between runs.

## Known shortcomings

- The win (Java 1.272 s vs best C++ 1.587 s) comes from the C++ side's library choices (an istringstream tokenizer plus one unordered_map node per word); C#/AOT, Rust, Crystal and Zig also beat C++, so it is not a JIT effect; one run per configuration; the JVM uses 40x more memory; the cpp/Makefile LTO flags apply only at the link step.
- No harness bug: a Python replay reproduces checksum 1998586832 and the Java and C++ texts are identical. Java leads in all 5 monthly runs (1.09-1.25x) and all 5 JVM rows beat the best C++ row. The win is istringstream plus a node map against String.split's fast path plus the cached hash; AOT Zig, Crystal, Rust and C# AOT also win, so the runtime-jit-beats-aot label misfits. Semantic gap: split(" ") against operator&gt;&gt; on any whitespace. LTO is link-only in the C++ builds too.

## Caveats and trade-offs

The win comes from the C++ tokenizer and per-node hash-map allocation, not from JIT compilation: C#/AOT and the AOT languages Rust, Crystal and Zig also beat every C++ row, so the 'runtime-jit-beats-aot' framing does not fit; a std::string_view split loop in C++ would likely change the result (inference, not measured). Both versions do the same work (whitespace split, hash count, max scan) over 50,000 words of 3-8 letters (all within libstdc++'s small-string buffer), 360 timed iterations. The C version (strdup of the whole text every iteration, strtok_r, uthash with strdup'd keys) is slower still at 1.963-2.084 s. Memory trade: Java/OpenJDK RSS 309 MB vs C++ 7.5-7.9 MB. Margin is modest (1.25x over the best C++ row, C++/G++/PGO 1.587 s) and rests on one run per configuration, although all 16 C/C++ configurations land between 1.587 and 2.042 s. LangArena's own README calls it 'a subjective benchmark', and the author says AI tools helped translate the tests between languages. benchmarks.rb runs each test once per configuration in its own process and records that single in-process timing (no repeats, no variance). Every language, C and C++ included, runs a warm-up of 20% of the iterations before the timer starts, so JIT compilation and startup are excluded. The headline C/C++ 'prod' rows are -O2 with hardening flags, but the -O3, PGO and fast-math variants were also measured and still lose on this test; the Makefile's LTO flags are link-only, so no configuration had real LTO. Rows were selected by the search agent as tests where a managed-runtime row beats every C/C++ row; most other tests in the suite go the other way (for example Sort::Quick, Sort::Merge and the Binarytrees::Arena variant). The per-benchmark ratios are derived from the results file, not stated by the suite. [retier] A Python replay reproduces checksum 1998586832 and the Java and C++ texts are identical; Java leads in all 5 monthly runs (1.09-1.25x) and all 5 JVM rows beat the best C++ row. The win is istringstream plus a node map against String.split's fast path plus the cached hash; AOT Zig, Crystal, Rust and C# AOT also win, so the JIT label misfits. Semantic gap: split(" ") against operator&gt;&gt; on any whitespace. LTO is link-only in the C++ builds.

Java peak RSS about 309 MB (GraalVM about 445 MB).

## Maintenance

Active MIT-licensed suite (41 stars, last commit 2026-10-08, monthly reruns; Words.java unchanged since it was added on 2026-02-28). The author calls the suite subjective and says AI tools helped port the tasks, so treat the row as a language-level data point, not code to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent third-party suite with public code for both sides (cpp/src/words.cpp, java/src/main/java/benchmarks/Words.java), flags in cpp/Makefile and the results file's run-cmd entries, compiler and JVM versions and the CPU (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js; every number in the record matches the Etc::Words-runtime rows.
- **Verifier notes:** Numbers verified exactly (Java/OpenJDK 1.272 s, Java/GraalVM/JIT 1.15 s, C#/JIT 1.422 s, C++/G++ 1.638 s, C++/G++/Fast 1.651 s, C++/G++/PGO 1.587 s best, Julia 1.857 s). Shortcomings: the win is a standard-library effect (istringstream tokenizer plus node-per-key unordered_map against String.split and a GC'd HashMap), AOT C#, Rust, Crystal and Zig also beat C++, so the category label 'runtime-jit-beats-aot' misattributes it; single run per configuration; 40x more memory on the JVM; the Makefile's LTO flags are link-only.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
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
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Words.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/words.c>
  - <https://github.com/kostya/LangArena/commits/master/cpp/src/words.cpp>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://github.com/kostya/LangArena/commits/master/java/src/main/java/benchmarks/Words.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/words.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/helper.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Words.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Benchmark.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Helper.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/pom.xml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/share/classes/java/lang/String.java>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:java/kostya/langarena#etc-words`) · [data/wave14/enrich/raw/lang_java_kostya_langarena_etc_words.json](../../../data/wave14/enrich/raw/lang_java_kostya_langarena_etc_words.json) (enrichment confidence 0.7)

</details>
