# OpenJDK HotSpot (Java 27): LangArena Calculator::Interpreter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `MIT` · 🟢 active

> Plain Java tree-walking evaluator over a prebuilt AST on HotSpot 27, about 1.3x faster than the suite's C++ std::visit plus std::unordered_map version.

| | |
|---|---|
| **Beats** | C++ tree-walking calculator interpreter (g++ 16, clang++ 22); best C/C++ configuration is C++/G++ prod at 0.691 s |
| **Claimed result** | Java/OpenJDK (Temurin 27, -Xmx2g, default GC) 0.52 s vs C++/G++ 0.691 s (prod, -O2; the best of the 16 Clang/GCC C and C++ configurations, PGO-instrumented builds excluded), C++/G++/Fast (-O3 -march=native, thin LTO) 0.705 s, C++/G++/Unsafe 0.702 s, best C row C/Gcc/PGO 1.067 s: 1.33x faster than the best C/C++ row and 1.36x faster than the -O3 row (derived from page data). Other managed rows in the same file also beat C++: Java/OpenJDK/Serial (-XX:+UseSerialGC -Xmx512m) 0.364 s (1.90x), Kotlin/Scala JVM Opt/Max rows 0.37-0.38 s, C#/AOT 0.501 s; C#/JIT 0.67 s is on par; Julia 2.006 s is slower. Earlier monthly runs on the same GCC 16 build show a much smaller lead for Java/OpenJDK over the best C/C++ row: 1.02x on 2026-08-14 (OpenJDK 26.0.1, 0.686 vs 0.699 s), 1.03x on 2026-09-03 (0.677 vs 0.697 s), 1.13x on 2026-09-18 (OpenJDK 26.0.2, 0.62 vs 0.699 s), with the C++ rows steady at 0.69-0.72 s (derived from the results files). |
| **Workload** | Interpret the calculator expression programs directly (the interpreter counterpart of Calculator::Ast). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++: Clang 22.1.8 and GCC 16.0.1 20260322 (trunk). Headline 'prod' build is -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer (not -O3). The same suite also builds 'Fast' (-O3 -march=native -mtune=native -funroll-loops, thin LTO), 'Unsafe' (-O3 -march=native -ffast-math, full LTO) and 'PGO' (-O2 plus profile) variants of every C and C++ benchmark; all 16 Clang/GCC x C/C++ configurations were compared here. Managed side: Temurin OpenJDK 27+35 with -Xmx2g, dotnet 11.0.100-rc.1 (Release), Julia 1.13.1 with --threads=16 (versions from the results file). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite (agent inference: profile-guided inlining and cheap allocation in HotSpot). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

LangArena results of 2026-10-05 (AMD Ryzen 7 3800X, Linux) time 100 evaluations of a 35,011-statement AST after 20 warm-up passes: Java on Temurin OpenJDK 27 (java -Xmx2g, default G1) 0.52 s vs C++ with libstdc++ std::unordered_map at -O2 (g++ 16.0.1 trunk) 0.691 s, which is also the best of 16 Clang 22/GCC 16 C and C++ builds, about 1.33x (derived from page data); the -O3 'Fast' row is 0.705 s and the best C row (uthash) 1.067 s.

## Use it when

- Choosing a runtime for an expression evaluator, rules engine or small scripting layer that walks a resident AST and keeps variables in a string-keyed map: idiomatic Java on HotSpot 27 ran 5.2 ms per 35,011-statement pass against 6.9 ms for the best C++ build.
- JVM deployments that can pick the collector: with -XX:+UseSerialGC -Xmx512m the same code ran 0.364 s, about 1.9x faster than the best C/C++ row and 1.4x faster than default G1 (derived from page data).
- As a reference point when a C++ interpreter keys its environment by std::string in std::unordered_map: the measured gap points at hashing and node allocation, which interning names to integer slots would remove on either side.

## Skip it when

- As a stable win: the lead over the best C/C++ row was 0.99x on 2026-07-14 (Java 0.692 s vs C++/G++/PGO 0.688 s, Java slower), 1.02x on 08-14, 1.03x on 09-03, 1.13x on 09-18 and 1.33x only on 2026-10-05 with Temurin 27 and a new host install (derived from the results files).
- Memory-tight processes: Java/OpenJDK peaked at 239 MB RSS against 28 MB for C++/G++.
- When an AOT binary is required: C#/AOT (NativeAOT, 0.501 s, 55 MB) already beats both Java/OpenJDK and every C++ row on this test, so the JIT is not what wins.
- Short-lived processes: JVM startup and 20 warm-up passes are untimed for every language.
- As a reason to rewrite an optimized interpreter: no C++ variant with an open-addressing map, interned variable slots or reserve() was measured.

## How it is fast

Per pass both sides do 173,250 integer operations, 107,977 variable lookups and 35,011 inserts into a map that grows from empty (counts from replaying the suite's generator). The gap sits in the map: C++ hashes the std::string key on every find and operator[] call, reduces it with libstdc++'s prime-modulo bucket index, allocates one node per insert and frees all 35,011 nodes when the map dies inside the timed loop, while Java's String caches its hash code (the AST's name strings were hashed during warm-up), HashMap masks with a power of two and dead maps are reclaimed by the young collector (mechanism inferred from the sources, not measured by the suite). The win is not specific to a JIT: C# compiled ahead of time with NativeAOT (0.501 s) and Go (0.632 s) also beat every C/C++ row.

## Compared with alternatives

Pick the Calculator::Ast sibling instead when you want a clear managed-runtime win (1.66x, stable 1.35-1.66x across five runs); this entry is the weaker, newer case and mainly useful next to the Etc::Words and Etc::CacheSimulation siblings as another string-keyed std::unordered_map loss, while the kostya/benchmarks Brainfuck siblings (Scala and C# staged, 2.7-2.9x) show what closure compilation rather than plain tree walking buys.

## Integration

| | |
|---|---|
| **Form** | runtime plus source snippet (one Java file in a Maven project, java/src/main/java/benchmarks/CalculatorInterpreter.java, reusing the AST classes of CalculatorAst.java) |
| **Dependencies** | none for the evaluator (java.util only); the suite's harness reads its config through a JSON library (getJSONObject calls in Benchmark.java) |
| **Minimum toolchain** | measured on Temurin OpenJDK 27+35; the code uses only java.util APIs available since Java 8 (Map.getOrDefault), the Maven target level was not checked |
| **Platforms** | any JVM platform; measured on x86-64 Linux (AMD Ryzen 7 3800X) |
| **Thread safety** | not documented; each pass builds its own Interpreter with an unsynchronized HashMap, the shared AST is read-only |
| **Drop-in for the baseline** | no |

## Gotchas

- The C++ baseline relies on undefined behaviour: replaying the generator shows 21,866 signed int64 overflows per pass in + - and \* (values grow multiplicatively through 'v + (v + v) \* v' lines); Java defines wraparound, and GCC and Clang happen to emit wrapping instructions, so the checksum 38749936 matches (reproduced exactly by the replay), but a C++ evaluator for this language should use unsigned or __builtin_\*_overflow arithmetic.
- Collector choice moves the result more than the language does: Java/OpenJDK default G1 0.52 s, SerialGC -Xmx512m 0.364 s, ParallelGC 'Opt' row 0.588 s; GraalVM JIT with default GC 0.663 s is barely ahead of C++ (0.691 s).
- Same-file regressions show run-to-run sensitivity: C#/JIT moved from 0.54 s (2026-09-18, .NET 10) to 0.67 s (2026-10-05, .NET 11 rc.1) while the C++/G++ prod row stayed at 0.69-0.72 s across all five runs checked; one measurement per configuration, no variance.
- The checksum adds only each pass's final value, but every statement feeds the next through v(n-1), so no work can be skipped; the Java and C++ simpleDiv/simple_mod are semantically identical (truncating division, zero divisor returns 0).

## Known shortcomings

- Java 0.52 s vs best C/C++ 0.691 s (1.33x) in one measurement of a cherry-picked test; the lead was only 1.02-1.13x in three earlier runs, so the margin comes mostly from JDK 27; the win is the cached String hash and runtime, not codegen.
- The C++ baseline relies on undefined behaviour: a replay shows 21,866 signed int64 overflows per pass (it wraps in practice, checksum 38749936 reproduced exactly, so the numbers stand). Java lost on 2026-07-14 (0.692 vs C++/G++/PGO 0.688, 0.99x) and led by only 1.02x, 1.03x and 1.13x until the 1.33x after JDK 27. C#/AOT 0.501 s and Go 0.632 s also beat C++, so the win is not JIT-specific; it comes from std::unordered_map string hashing, node churn and GC, and the GC choice swings Java between 0.364 and 0.588 s.

## Caveats and trade-offs

Margin is modest (1.33x) and most of it arrived with the JDK 27 upgrade; before that Java led by only 1.02-1.13x. Both sides walk the same pre-built AST with the same integer semantics; the only data-structure difference is each language's standard string-keyed hash map for variables (std::unordered_map&lt;std::string,int64_t&gt; in C++, uthash in C, HashMap&lt;String,Long&gt; with boxed Long values in Java). The GC setting matters: the SerialGC row is 1.4x faster than the default-GC row. LangArena's own README calls it a subjective benchmark ('not an objective, peer-reviewed, or industry-standard benchmark suite'), and the author says AI tools helped translate the tests between languages (each port reviewed, checksums verified). The suite publishes one measurement per test and configuration (no variance). Every language runs the same harness: prepare, a warm-up of 20% of the iterations on the same instance, then the timed run (Java calls System.gc() between warm-up and the timed loop), so startup is excluded for all. The headline C/C++ 'prod' rows are -O2 with hardening flags, but the 'Fast' (-O3 -march=native, thin LTO), 'Unsafe' (-O3 -ffast-math, full LTO) and PGO variants are in the same file and still lose on this test. Rows were selected by the search agent as tests where a managed-runtime row beats every C/C++ row; most of the 50 tests go the other way (for example Sort::Quick, Sort::Merge and Binarytrees::Arena). The 2026-10-05 run is the first on Temurin JDK 27 and on a new Arch Linux host install (the GCC 16 trunk build is unchanged); in the three earlier runs checked (2026-08-14, 2026-09-03, 2026-09-18, OpenJDK 26) Java still led but only narrowly, so most of the margin arrived with the JDK upgrade. Per-benchmark ratios are derived from the results files, not stated by the suite. [retier] The C++ baseline relies on undefined behaviour (21,866 signed int64 overflows per pass; wraps in practice, checksum 38749936 reproduced). Java lost on 2026-07-14 (0.99x) and led by only 1.02-1.13x until the 1.33x after JDK 27. C#/AOT 0.501 s and Go 0.632 s also beat C++, so the win is not JIT-specific; the GC choice swings Java between 0.364 and 0.588 s.

Java peak RSS about 239 MB.

## Maintenance

LangArena is active (MIT, 41 stars, 622 commits, monthly result files) and the Java evaluator has been unchanged since 2026-02-23; it is copyable, but the result is new and thin (under 1.13x before JDK 27, a loss on 2026-07-14) and measures hash-map and GC behaviour more than JIT code quality.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public code for both sides (cpp/src/calculator.cpp, c/src/calculator.c, java/src/main/java/benchmarks/CalculatorInterpreter.java, shared harnesses cpp/src/benchmark.cpp and Benchmark.java), C/C++ flags in cpp/Makefile and c/Makefile, exact GCC 16.0.1 / Clang 22.1.8 / Temurin 27+35 versions, run commands and the CPU model (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js; an independent multi-language suite, not a vendor. All quoted runtimes match the Calculator::Interpreter-runtime entries.
- **Verifier notes:** Numbers and flags check out against the 2026-10-05 results file and the Makefiles; tier A stands. Shortcomings to record: single measurement per run, cherry-picked test, 1.33x margin is new with JDK 27 (1.02-1.13x in the three prior runs), win rests on Java's cached String hash and runtime rather than codegen, prod C/C++ rows are -O2 (the -O3/LTO/PGO rows also lose), subjective suite with AI-assisted ports.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
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
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/calculator.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/calculator.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/calculator.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/CalculatorInterpreter.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/CalculatorAst.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.cpp>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master/cpp/src/calculator.cpp>
  - <https://github.com/kostya/LangArena/commits/master/java/src/main/java/benchmarks/CalculatorInterpreter.java>
  - <https://github.com/kostya/LangArena/tree/master/results>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue%20calculator>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/calculator.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/calculator.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/calculator.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/CalculatorInterpreter.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/CalculatorAst.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Benchmark.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:java/kostya/langarena#calculator-interpreter`) · [data/wave14/enrich/raw/lang_java_kostya_langarena_calculator_interpreter.json](../../../data/wave14/enrich/raw/lang_java_kostya_langarena_calculator_interpreter.json) (enrichment confidence 0.68)

</details>
