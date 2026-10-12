# OpenJDK HotSpot (Java 27): LangArena Calculator::Ast

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `MIT` · 🟢 active

> Plain Java recursive-descent parser building a small-object AST on HotSpot 27, about 1.7x faster than the suite's C++ std::variant/unique_ptr parser.

| | |
|---|---|
| **Beats** | C++ recursive-descent parser building an AST with std::variant nodes and std::unique_ptr (g++ 16, clang++ 22); best C/C++ configuration is C++/G++/Unsafe at 0.487 s |
| **Claimed result** | Java/OpenJDK 0.294 s vs C++/G++ 0.534 s (prod, -O2), C++/G++ -O3 'Fast' 0.524 s, best of all 16 C/C++ configurations C++/G++/Unsafe 0.487 s: about 1.8x faster than the prod row and 1.7x faster than the best row (derived from page data). Java/GraalVM/Serial 0.249 s and Java/GraalVM/JIT 0.294 s; Julia/Default 0.459 s and Julia/Max 0.44 s also beat the best C++ row, and so do JavaScript and TypeScript on Bun and Deno (0.32-0.348 s); C#/JIT 1.327 s is slower; C/Clang and C/Gcc 1.033-1.077 s. |
| **Workload** | Parse a generated 11,000-line arithmetic program with variables and assignments into an AST with a recursive-descent parser, 100 timed iterations; the timed run() only parses and checksums the expression count and last variable name. Evaluation is a separate test (Calculator::Interpreter). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++: Clang 22.1.8 (official LLVM release tarball; the clang_cpp container aliases g++ to clang++ and links the system libstdc++, no -stdlib=libc++) and GCC 16.0.1 20260322 (trunk, Ubuntu build), -std=c++20, glibc malloc. Headline 'prod' build (cpp/Makefile CXXFLAGS_PROD): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections (not -O3). The same suite also builds 'Fast' (-O3 -march=native -mtune=native -pipe -fstack-protector -ftree-vectorize -funroll-loops), 'Unsafe' (-O3 -march=native -ffast-math -fno-stack-protector -fomit-frame-pointer -fvisibility=hidden -fno-trapping-math) and 'PGO' (-O2 plus -fprofile-instr-use or -fprofile-use) variants of every C and C++ benchmark; the Makefile passes -flto=thin (Fast) and -flto=full (Unsafe) only at the link step while the objects are compiled without -flto, so those builds probably get no LTO (inference from cpp/Makefile). All 16 Clang/GCC x C/C++ x prod/Fast/Unsafe/PGO configurations were compared here (instrumented PGO/Gen rows excluded). Managed side: Temurin OpenJDK 27+35 run as 'java -Xmx2g -jar' (default G1 GC, C2 JIT), GraalVM CE 25.4.4.1.1 (JDK 25.0.4.1.1) with -Xmx2g, dotnet 11.0.100-rc.1 (Release), Julia 1.13.1 with --threads=16 (versions and run commands from the results file). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. Likely allocation of many small AST nodes and virtual dispatch over node types, where HotSpot has cheap allocation and profile-guided inlining, versus unique_ptr allocation per node in the C++ version (agent inference, not measured). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

LangArena results of 2026-10-05 (AMD Ryzen 7 3800X, Linux) time 100 parses of the 11,011-line program after 20 warm-up parses: Java on Temurin OpenJDK 27 (java -Xmx2g, default G1) 0.294 s vs C++ with libstdc++ at -O2 (g++ 16.0.1 trunk) 0.534 s and the best of 16 Clang 22/GCC 16 C and C++ builds (G++ -O3 -march=native -ffast-math, 'Unsafe') 0.487 s, about 1.8x and 1.7x (derived from page data); Java used 369 MB RSS against 19 MB.

## Use it when

- Choosing a runtime for parser, compiler-front-end or config-loader services that build many small immutable tree nodes per request: idiomatic Java on HotSpot parsed this program in 2.94 ms per pass against 4.87 ms for the best C++ build (0.294 s vs 0.487 s per 100 passes).
- Long-running JVM processes where heap headroom is cheap: the default G1 run peaked at 369 MB RSS against 19 MB for C++, and that headroom is what lets dead trees cost nothing.
- As a reference point when a C++ parser written with std::unique_ptr and std::variant nodes is a hotspot: the measured gap is a hint that per-node malloc/free dominates, before reaching for a different language.
- GraalVM users: GraalVM CE 25 with SerialGC and -Xmx512m was the fastest row of the whole file at 0.249 s.

## Skip it when

- Memory-capped processes: with -XX:+UseSerialGC -Xmx512m HotSpot needs 0.457 s, only about 1.07x faster than the best C++ row (0.487 s), and still uses 243 MB RSS (derived from page data).
- Short-lived or cold-start tools: the timing excludes JVM startup and 20 untimed warm-up passes for every language, so C2 compilation cost is not in the number.
- As evidence that the JIT generates better parsing code: the advantage tracks allocation strategy, the C version with two mallocs per binary node and strdup'd names is twice as slow as C++ (1.033-1.077 s), and an AOT-compiled arena port (Zig/Unchecked 0.465 s) also beats C++.
- As a reason to rewrite a tuned C++ front end: no arena, pool or flat-array AST variant of the C++ code was measured, so the result says nothing about allocation-aware C++.
- Latency-critical services that cannot tolerate GC pauses: the benchmark reports only total throughput for 100 passes, no pause or tail-latency data.

## How it is fast

The gap is in memory management, not parsing logic: per parse the C++ version makes 65,041 heap allocations (54,030 BinaryOp and 11,011 Assignment via std::make_unique; numbers and SSO variable names sit inline in the 40-byte std::variant Node) and frees the previous iteration's whole tree node by node inside the timed loop, while HotSpot allocates by bumping a thread-local pointer and its copying young-generation collector never touches dead trees (counts from replaying the suite's generator and grammar; the mechanism is inferred, the suite gives no explanation). Java actually allocates more, about 130,000 node objects plus 44,727 substring Strings per parse, and still wins. Most garbage-collected JIT rows in the file also beat the best C++ row (GraalVM 0.249-0.294 s, Bun and Deno 0.32-0.348 s, Julia 0.44-0.459 s; C#/JIT at 1.327 s and the Scala/JVM rows do not), and so does one ahead-of-time row, Zig/Unchecked at 0.465 s, whose port uses a per-run ArenaAllocator.

## Compared with alternatives

Pick this over the LangArena Binarytrees::Obj and benchLANG binary-trees siblings (pure node allocation, Java 4.4x and 3.3x ahead) when you want a realistic parser workload: the margin is smaller (1.66x) but it comes from real lexing and recursive descent; the Calculator::Interpreter sibling, which evaluates the same AST, shows a much thinner and newer Java lead (1.33x, under 1.13x before JDK 27).

## Integration

| | |
|---|---|
| **Form** | runtime plus source snippet (one Java file in a Maven project, java/src/main/java/benchmarks/CalculatorAst.java) |
| **Dependencies** | none for the parser itself (java.util only); the suite's harness reads its config through a JSON library (getJSONObject calls in Benchmark.java) |
| **Minimum toolchain** | measured on Temurin OpenJDK 27+35 and GraalVM CE 25.4.4.1.1; the code uses only long-standing java.util and String APIs, the Maven target level was not checked |
| **Platforms** | any JVM platform; measured on x86-64 Linux (AMD Ryzen 7 3800X) |
| **Thread safety** | not documented; the parser is a single-threaded object with mutable position state, one per run |
| **Drop-in for the baseline** | no |

## Gotchas

- The lead depends on heap headroom and collector: default G1 with -Xmx2g gives 0.294 s, SerialGC with -Xmx512m 0.457 s, and the ParallelGC 'Opt' row (which also disables the harness's System.gc() before the timer via -XX:+DisableExplicitGC) 0.36 s.
- The record's caveat that an arena AST in C++ 'would likely reverse the result' is not supported by the suite's nearest proxy: the Zig port allocates its AST from a per-run std.heap.ArenaAllocator and runs 0.465 s (Unchecked) and 0.632 s (safe), still 1.6-2.15x slower than Java/OpenJDK (derived from page data).
- Stable across runs, but the code changed: the lead over the best C/C++ row was 1.55x (2026-07-14), 1.35x (08-14), 1.39x (09-03), 1.39x (09-18) and 1.66x (10-05); a 2026-09-07 commit ('Calculator::Ast unify code for all langs') rewrote both sides, and between the 09-03 and 09-18 runs C++/G++ went from 0.74 to 0.518 s and Java from 0.485 to 0.348 s (derived from the results files).
- No harness defect found: replaying the generator (LCG seed 42) and grammar reproduces the suite's expected checksum 1670614456 exactly; the checksum covers only the expression count and the last variable name, but the tree escapes into a field, so it cannot be elided. One measurement per configuration, no variance.

## Known shortcomings

- Java 0.294 s vs best C++ 0.487 s: the test only parses (evaluation is the separate Calculator::Interpreter test) and the C++ side pays make_unique per node plus timed frees of the previous AST against bump allocation; Julia, Bun and Deno also beat every C++ row; LTO flags only at the link step.
- No harness defect: a Python replay of the generator and parser reproduces checksum 1670614456 exactly, and the lead holds at 1.35-1.66x across 5 runs (07-14 to 10-05; the 2026-09-07 rewrite changed both sides). The lead depends on heap and GC (Java/OpenJDK/Serial -Xmx512m 0.457 s is only 1.07x the best C++ 0.487 s); RSS 369 MB against 19 MB. Record caveat corrected: 'an arena C++ AST would likely reverse the result' is unsupported, since the Zig port already uses a per-run ArenaAllocator and runs 0.465 s unchecked and 0.632 s safe, still 1.6-2.15x slower than Java.

## Caveats and trade-offs

Only the C++ std::variant plus unique_ptr design was measured; a pool-allocated or arena AST in C++ would likely reverse the result (inference, by analogy with Binarytrees::Arena). The C version (C/Clang and C/Gcc 1.033-1.077 s) is slower than the C++ one. The C++ timed region includes freeing the previous AST each iteration, while the JVM's last collection is untimed. Java's program generator emits one extra space in one of its ten line templates (' /  v' in case 1); the parse result and checksum are the same. Memory trade: Java/OpenJDK RSS 369 MB vs C++ 19 MB. LangArena's own README calls it 'a subjective benchmark', and the author says AI tools helped translate the tests between languages. benchmarks.rb runs each test once per configuration in its own process and records that single in-process timing (no repeats, no variance). Every language, C and C++ included, runs a warm-up of 20% of the iterations before the timer starts, so JIT compilation and startup are excluded. The headline C/C++ 'prod' rows are -O2 with hardening flags, but the -O3, PGO and fast-math variants were also measured and still lose on this test; the Makefile's LTO flags are link-only, so no configuration had real LTO. Rows were selected by the search agent as tests where a managed-runtime row beats every C/C++ row; most other tests in the suite go the other way (for example Sort::Quick, Sort::Merge and the Binarytrees::Arena variant). The per-benchmark ratios are derived from the results file, not stated by the suite. [retier] A Python replay reproduces checksum 1670614456 exactly and the lead holds at 1.35-1.66x across 5 runs. The lead depends on heap and GC (Java/OpenJDK/Serial -Xmx512m 0.457 s is only 1.07x the best C++ 0.487 s); RSS 369 MB against 19 MB. The earlier 'an arena C++ AST would likely reverse the result' is unsupported: the Zig port already uses a per-run ArenaAllocator and runs 0.465 s unchecked and 0.632 s safe, still 1.6-2.15x slower than Java.

JVM start-up and warm-up are excluded from the timing; Java peak RSS about 369 MB.

## Maintenance

LangArena is active (MIT, 41 stars, 622 commits, monthly result files, results up to 2026-10-05); the 300-line Java file (generator plus parser) is copyable, but the entry is a measurement of JVM allocation and GC against per-node malloc/free rather than a reusable component.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent third-party suite with public code for both sides (cpp/src/calculator.cpp and .hpp, java/src/main/java/benchmarks/CalculatorAst.java), flags in cpp/Makefile and the results file's run-cmd entries, compiler and JVM versions and the CPU (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js; the record's numbers match the Calculator::Ast-runtime rows.
- **Verifier notes:** Numbers verified (Java/OpenJDK 0.294 s, C++/G++ 0.534 s, C++/G++/Fast 0.524 s, C++/G++/Unsafe 0.487 s best, C#/JIT 1.327 s, C 1.033-1.077 s). Corrected the workload (the test only parses; evaluation is the separate Calculator::Interpreter test) and why_faster (no dispatch involved; per-node make_unique and timed AST frees against bump allocation and young-gen GC); Julia and Bun/Deno JS also beat every C++ row. Shortcomings: allocation-design dependent, single run per configuration, 19x more memory on the JVM.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `claimed_speedup`, `caveats`
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
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/calculator.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/calculator.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/CalculatorAst.java>
  - <https://github.com/kostya/LangArena/commits/master/cpp/src/calculator.cpp>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master/cpp/src/calculator.cpp>
  - <https://github.com/kostya/LangArena/commits/master/java/src/main/java/benchmarks/CalculatorAst.java>
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
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/CalculatorAst.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/java/src/main/java/benchmarks/Benchmark.java>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/calculator_ast.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:java/kostya/langarena#calculator-ast`) · [data/wave14/enrich/raw/lang_java_kostya_langarena_calculator_ast.json](../../../data/wave14/enrich/raw/lang_java_kostya_langarena_calculator_ast.json) (enrichment confidence 0.72)

</details>
