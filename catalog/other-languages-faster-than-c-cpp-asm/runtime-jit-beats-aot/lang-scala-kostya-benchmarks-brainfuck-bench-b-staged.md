# Scala (Staged) on the JVM: Brainfuck bench.b in kostya/benchmarks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Scala` · `MIT` · 🟢 active

> Scala 3 quoted-staging Brainfuck runner compiling programs to JVM bytecode at run time; 2.7x faster than kostya's C++ interpreter.

| | |
|---|---|
| **Beats** | C++/g++ brainfuck (brainfuck/bf.cpp): an AST-walking interpreter with std::vector ops, g++ -O3 -march=native -flto |
| **Claimed result** | bench.b: Scala (Staged) 0.409s (MAD 0.011) vs C++/g++ 1.097s, C/gcc 1.112s, C++/clang++ 1.167s (about 2.7x vs g++, derived from page data); memory 229.62 + 7.00 MiB vs 3.38 + 0.00 MiB; energy 26.31 J vs 46.21 J. The same-algorithm (non-staged) Scala interpreter is slower than C++/g++ (2.379s). |
| **Workload** | Run the bench.b Brainfuck program; the staged Scala 3 version uses scala3-staging quotes and staging.run to compile the program to JVM bytecode at run time (inside the timed region), then HotSpot JIT-compiles it. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E-2324G (README Environment section); Debian forky/sid Docker image |
| **Compiler and flags** | C++ baseline: g++ 16.1.0 -Wall -Wextra -pedantic -Wcast-align -O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries -std=c++23 (common/commands.mk GCC_CPP_BUILD, libstdc++); clang++ 22.1.8 row uses the same flags with -stdlib=libc++. Scala 3.8.4 with scala3-staging 3.8.4, run as scala bf-staged.scala (common/commands.mk SCALA_RUN) with default JVM options; the JVM version used for Scala is not stated (README lists Java 24.0.2). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | Runtime code generation specialized to the input program (quoted staging) followed by HotSpot JIT, derived from reading brainfuck/bf-staged.scala; the README gives no explanation. |
| **Adoption** | 2.9k stars |
| **Last commit** | 2026-07-19 |
| **Links** | [repository](https://github.com/kostya/benchmarks) · [benchmark](https://github.com/kostya/benchmarks) |

## Verdict

kostya/benchmarks (README UPDATE 2026-07-19, Intel Xeon E-2324G, median of 10 runs with MAD): Scala (Staged), on Scala 3.8.4 with scala3-staging 3.8.4 and default JVM options, ran bench.b in 0.409 s (MAD 0.011) and 26.31 J. The C++ AST interpreter built with g++ 16.1.0 -O3 -march=native -flto=auto (libstdc++) took 1.097 s and 46.21 J, so the staged runner is about 2.7x faster; on mandel.b it is 7.118 s against 10.143 s, about 1.4x (both derived from page data). The timer includes the run-time compile, and the win is run-time compilation set against a reference interpreter: the same-algorithm Scala interpreter is about 2.2x slower than C++/g++.

## Use it when

- As a reference pattern for Scala 3 programs that receive a small program at run time (rules, filters, query plans, a DSL) and execute it long enough to amortise an in-process compile: bench.b runs in 0.409 s and mandel.b in 7.118 s, compile included.
- When the code already runs on the JVM and pulling the Scala 3 compiler in through the scala3-staging dependency is acceptable.
- Batch or throughput jobs where about 230 MiB resident memory and JVM plus compiler warm-up do not matter.
- Comparing staging techniques across runtimes: the same table has C# (Staged) and Racket (Staged) versions of the identical task.

## Skip it when

- As evidence that Scala or the JVM beats C++ at equal work: the plain Scala interpreter in the same table is slower than C++/g++ (bench.b 2.379 s vs 1.097 s, mandel.b 15.785 s vs 10.143 s), and the suite has no C++ JIT or staged variant.
- Memory-tight processes: 229.62 MiB base plus 7.00 MiB increase on bench.b (plus 71.23 MiB on mandel.b), against 3.38 MiB for the C++ interpreter.
- One-shot or latency-sensitive runs: every Program builds a new staging.Compiler and runs the full Scala 3 compiler. The benchmark's self-check has already compiled one program before the timer starts, so a cold first compile costs more than the row shows; that cost is not measured separately.
- Deployments without a run-time compiler or class loading: the Scala 3 staging reference requires the compiler on the classpath (scala3-staging, or -with-compiler for scalac/scala).
- Untrusted Brainfuck input: the tape grows only to the right, so a program that steps left of cell 0 dies with an ArrayIndexOutOfBoundsException (safe, but not handled).

## How it is fast

This is run-time multi-stage programming with scala.quoted quotes and splices (a first Futamura projection of the interpreter). Each '+', '-', '&gt;', '&lt;' and '.' becomes a direct call such as t.inc(1) in one straight-line block, and each '[' becomes a local def body() plus a while loop, so no op-kind pattern match, Array[Op] walk or recursion over ops is left at run time. HotSpot then JIT-compiles that bytecode and can inline the small Tape methods into tight loops. The C++ baseline pays a switch and a recursive std::vector&lt;Op&gt; walk for every instruction. The source does not squash runs of '+' or '&gt;'; whether HotSpot folds them was not checked.

## Compared with alternatives

Among the staged rows of the same table, C# (Staged) is faster and much leaner (bench.b 0.373 s and 36.62 MiB; mandel.b 2.917 s against 7.118 s), and Racket (Staged) is slower (0.885 s, 101.37 MiB; mandel.b 15.722 s). Pick this one when your host is Scala or the JVM and you want type-checked quoted code generation. To get the same run-time specialisation while staying in C++, look at the catalogued ClangJIT or Proteus entries instead.

## Integration

| | |
|---|---|
| **Form** | source-drop (one Scala CLI script, brainfuck/bf-staged.scala) |
| **Dependencies** | org.scala-lang::scala3-staging 3.8.4, which brings in the Scala 3 compiler; resolved by the scala (Scala CLI) runner |
| **Minimum toolchain** | Scala 3.8.4 as pinned (quiet syntax, scala.quoted staging). The JDK behind the README run is unclear: the README Versions table says Java 24.0.2, but the Dockerfile from the same commit installs OpenJDK 26.0.1 |
| **Platforms** | any JVM platform; measured only on x86-64 Linux (Xeon E-2324G) |
| **Thread safety** | not documented; Tape and Printer are mutable per run, and each Program instance creates its own staging.Compiler |
| **Drop-in for the baseline** | no |

## Gotchas

- This is a different algorithm from the baseline. brainfuck/README.md says implementations interpret 'all bf instructions, one by one', and the maintainer (nuald, issue #485, 2024-03-20) says staged variants are 'not the reference implementations, and rather included just for testing purposes'. The C++ side is the reference interpreter, not a C++ JIT.
- The timed region opens with the notify call after verify() and includes staging.Compiler.make, the Scala 3 compile of bench.b and HotSpot JIT time. verify() has already run a full staged compile of a Hello World program before that, so compiler classes are loaded and partly warmed (the 229.62 MiB base RSS reflects this). The plain bf.scala defines verify but never calls it. For every JVM row, JVM start-up and the Scala CLI script compile are outside the timer.
- The harness does not validate output. xtime.rb and analyze.rb record time, memory and energy only, and nothing compares the printed 'Output checksum' with an expected value for any row; the built-in Hello World self-check is the only correctness guard. By source reading, the staged semantics (Int cells, loop while the cell is &gt; 0, Fletcher-16 mod 255) match bf.cpp.
- The README Versions table is partly stale. Java 24.0.2, Crystal 1.17.1, Julia 1.11.6 and Kotlin 2.2.0 there disagree with the Dockerfile of the same commit 5bc68b3 (OpenJDK 26.0.1, Crystal 1.21.0, Julia 1.12.6, Kotlin 2.4.10), and javac uses --release 26. The README also says measurements are taken 'semi-manually'. The JVM runs with default options (SCALA_RUN is xtime.rb scala, no flags).

## Known shortcomings

- Different algorithm: the staged Scala version compiles the Brainfuck program at runtime (eval or scala3-staging plus HotSpot) while the C++ baseline is a tree-walking interpreter, breaking the suite's interpret-each-instruction rule and with no C/C++ staged counterpart; non-staged Scala 2.379 s is slower; memory 229.62+7.00 MiB vs 3.38 MiB. C++ baseline g++ 16.1.0 -O3 -march=native -flto on a Xeon E-2324G is not crippled, so tier C.
- The JSON3.jl enricher found that kostya/benchmarks' 2026-07-19 update re-measured only the Primes table and the environment table: the Json table rows kept their 2025-08-17 values (gcc 14.2.0, clang 19.1.7), so the compiler versions recorded here (gcc 16.1.0, clang 22.1.8) describe the current environment table and may not be the toolchain behind this table's rows; whether this table was re-run on 2026-07-19 was not checked.
- The timed region holds the run-time Scala compile of bench.b, but verify() already ran one staged compile before the timer (the 229.62 MiB base RSS reflects it); plain bf.scala defines verify and never calls it, and the harness never checks the printed checksum for any row (a Hello World self-check is the only guard). Maintainer issue #485 calls staged variants 'not the reference implementations'. Staged semantics match bf.cpp by reading. The README Versions table is partly stale (Java 24.0.2 vs the Dockerfile's OpenJDK 26.0.1 at the same commit 5bc68b3), so the JVM version behind the Scala rows is unclear.

## Caveats and trade-offs

Not the same algorithm: the C++/g++ baseline (brainfuck/bf.cpp) is a tree-walking interpreter that dispatches every Brainfuck instruction at run time, while the staged variant compiles the Brainfuck program to native code at run time; the suite's own brainfuck/README.md says implementations interpret every instruction one by one, so the staged rows deviate from the suite rule. The repository has no C or C++ staged/JIT counterpart, so the result shows runtime compilation beating an interpreter, not the language beating C++ at equal work. The timed region (between the notify calls) includes parsing and the run-time compile on both sides, but verify() runs one staged compile of a hello-world program before timing, warming the compiler machinery. Measurements run with QUIET=1 (analyze.rb, 10 attempts, median with MAD), so output flushing does not matter. Single machine (Xeon E-2324G), single suite. The staged program is built with scala3-staging quotes: staging.run invokes the Scala 3 compiler at run time to emit JVM bytecode, which HotSpot then JIT-compiles; JVM startup and scala-cli compilation of the script are outside the timed region. Memory is about 68x the C++ footprint. On bench.b C++/g++ is not the fastest AOT interpreter either (V/gcc 0.985s, Rust 1.008s, D/ldc2 1.078s); C# (Staged)/.NET Core is faster still (0.373s). [retier] Enricher: the timed region holds the run-time Scala compile of bench.b, but verify() already ran one staged compile before the timer (the 229.62 MiB base RSS reflects it); plain bf.scala defines verify and never calls it, and the harness never checks the printed checksum for any row. Maintainer issue #485 calls staged variants 'not the reference implementations'. The README Versions table is partly stale (Java 24.0.2 vs the Dockerfile's OpenJDK 26.0.1 at commit 5bc68b3), so the JVM version behind the Scala rows is unclear.

Pulls the Scala compiler into the process: about 230 MiB resident and JVM start-up, versus about 3.4 MiB for the C++ interpreter.

## Maintenance

The suite is active (MIT, 2.9k stars, last update 2026-07-19 in PR #516). bf-staged.scala has four commits, all maintenance or embedding by nuald (latest 5bc68b3, 2026-07-19), on top of philnguyen's original PR #461. It is a copyable teaching sample of Scala 3 staging, not a maintained library, and the C tier cap for the language-level claim stands.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The measurement meets A methodology (brainfuck/bf-staged.scala vs brainfuck/bf.cpp, flags in common/commands.mk, g++ 16.1.0, Xeon E-2324G) and the numbers are on the README, but it compares run-time staging (Scala compiler plus HotSpot) with an AOT-compiled interpreter (same_algorithm false); the same-algorithm Scala row (2.379s) is 2.2x slower than C++/g++ (1.097s), so the language-level claim is capped at C (unequal-work precedent).
- **Verifier notes:** Numbers, flags, CPU and code all check out; downgraded A to C because the staged row compiles the Brainfuck program at run time (scala3-staging plus HotSpot) while the C++ baseline interprets it, and the same-algorithm Scala row is 2.2x slower than C++. Not D: the C++ baseline is fully optimised, not crippled. why_faster is from reading the source; the README gives no mechanism.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-06 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/commits>
  - <https://github.com/kostya/benchmarks/tree/master/brainfuck>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/analyze.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf-staged.scala>
  - <https://github.com/kostya/benchmarks/commits/master/brainfuck/bf-staged.scala>
- **Sources the enricher read:**
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/commits/master/brainfuck/bf-staged.scala>
  - <https://github.com/kostya/benchmarks/commits/master/docker/Dockerfile>
  - <https://github.com/kostya/benchmarks/pull/461>
  - <https://github.com/kostya/benchmarks/pull/472>
  - <https://github.com/kostya/benchmarks/pull/516>
  - <https://github.com/kostya/benchmarks/issues?q=staged>
  - <https://github.com/kostya/benchmarks/issues/485>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/xtime.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/analyze.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/repeat.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/run.sh>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/libnotify/libnotify.h>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf-staged.scala>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.scala>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bench.b>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/mandel.b>
  - <https://raw.githubusercontent.com/scala/scala3/main/docs/_docs/reference/metaprogramming/staging.md>
  - https://docs.scala-lang.org/scala3/reference/metaprogramming/staging.html (fetch failed: ENOTFOUND)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:scala/kostya/benchmarks#brainfuck-bench.b-staged`) · [data/wave14/enrich/raw/lang_scala_kostya_benchmarks_brainfuck_bench_b_staged.json](../../../data/wave14/enrich/raw/lang_scala_kostya_benchmarks_brainfuck_bench_b_staged.json) (enrichment confidence 0.72)

</details>
