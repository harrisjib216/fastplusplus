# Racket (Staged): Brainfuck bench.b in kostya/benchmarks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Racket` · `MIT` · 🟢 active

> Racket Brainfuck runner that turns the program into Racket syntax and evals it; 1.24x faster than kostya's C++ interpreter on bench.b only.

| | |
|---|---|
| **Beats** | C++/g++ brainfuck (brainfuck/bf.cpp): an AST-walking interpreter with std::vector ops, g++ -O3 -march=native -flto |
| **Claimed result** | bench.b: Racket (Staged) 0.885s (MAD 0.000) vs C++/g++ 1.097s, C/gcc 1.112s, C++/clang++ 1.167s (about 1.24x vs g++, derived from page data); memory 101.37 + 0.06 MiB vs 3.38 + 0.00 MiB. On mandel.b the staged Racket version is slower than C++/g++ (15.722s vs 10.143s). The same-algorithm (non-staged) Racket interpreter is slower than C++/g++ on both (1.761s and 35.373s). |
| **Workload** | Run the bench.b Brainfuck program; the staged Racket version generates a lambda from the program with syntax objects and calls eval (compiled by Racket CS / Chez Scheme) inside the timed region, with unsafe fixnum and vector operations. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E-2324G (README Environment section); Debian forky/sid Docker image |
| **Compiler and flags** | C++ baseline: g++ 16.1.0 -Wall -Wextra -pedantic -Wcast-align -O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries -std=c++23 (common/commands.mk GCC_CPP_BUILD, libstdc++); clang++ 22.1.8 row uses the same flags with -stdlib=libc++. Racket 9.2 (Racket CS) run as PLT_CS_COMPILE_LIMIT=100000 racket bf-staged.rkt (common/commands.mk RACKET_RUN), so the large eval'd form is compiled to machine code rather than interpreted. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | Runtime code generation specialized to the input program (eval of a generated lambda), derived from reading brainfuck/bf-staged.rkt; the README gives no explanation. |
| **Adoption** | 2.9k stars |
| **Last commit** | 2026-07-19 |
| **Links** | [repository](https://github.com/kostya/benchmarks) · [benchmark](https://github.com/kostya/benchmarks) |

## Verdict

kostya/benchmarks (README update 2026-07-19, Intel Xeon E-2324G, Debian forky/sid Docker image, median of 10 quiet runs with MAD) shows the staged Racket 9.2 CS runner at 0.885 s and 34.39 J on bench.b against 1.097 s and 46.21 J for the C++ AST interpreter built with g++ 16.1.0 -O3 -march=native -flto=auto (C/gcc 1.112 s, C++/clang++ 22.1.8 with libc++ 1.167 s), about 1.24x (derived from page data). It is run-time compilation of the Brainfuck program set against an interpreter, and it reverses on mandel.b (15.722 s against 10.143 s).

## Use it when

- As a pattern for Racket DSLs: an embedded rule, filter or bytecode language known only at run time whose programs run long enough to amortise one eval (bench.b: 172 instructions, 0.885 s total).
- Small programs dominated by tight nested loops: bench.b is 172 instructions with loops nested eight deep, ending in a [-] clear loop, the shape where compiling away dispatch pays most.
- When you already ship Racket CS and want interpreter-to-native speedups without writing a compiler back end: the code generator is a 16-line match over characters.
- Comparing staging techniques across runtimes: the same table holds C# (Staged) and Scala (Staged) versions of the identical task.

## Skip it when

- As evidence that Racket beats C++ at equal work: the same-algorithm Racket interpreter (bf.rkt) takes 1.761 s on bench.b and 35.373 s on mandel.b against C++/g++ 1.097 s and 10.143 s, and no C++ staged or JIT variant was measured.
- Large programs: on mandel.b (10,765 instructions) the staged version takes 15.722 s, 1.55x slower than C++/g++ and slower than the plain Rust (14.460 s) and C# (15.576 s) interpreters, with a 71.69 MiB RSS increase against 2.75 MiB for plain Racket.
- Memory- or start-up-sensitive processes: 101.37 MiB base RSS against 3.38 MiB for the C++ interpreter, before any code is generated.
- Untrusted programs: the generated code uses unsafe vector and fixnum operations, so a program that moves left of cell 0 reads and writes outside the vector instead of raising an error.
- Racket BC or deployments that cannot set PLT_CS_COMPILE_LIMIT: the measured configuration depends on Racket CS's machine-code mode and that environment variable for mid-sized programs.

## How it is fast

This is a hand-staged interpreter (a first Futamura projection done with Racket's macro-time syntax objects): each '+', '-', '&lt;', '&gt;' and '.' becomes a call to a small local helper (tape-inc!, tape-move, tape-print) nested around the previous expression, and each '[' becomes a named-let loop whose else branch holds the rest of the program. Under Racket CS, eval hands that form to the Chez Scheme compiler, so the program runs as native code with no instruction fetch, switch or op-vector walk, which is all the C++ baseline does per instruction. The generated code reads and writes the tape with unsafe-vector\*-ref/set! and adds with unsafe-fx+ (imported under the safe names). PLT_CS_COMPILE_LIMIT=100000 in common/commands.mk keeps larger generated forms in machine-code mode instead of Racket CS's interpreter fallback.

## Compared with alternatives

Only when your host language is Racket: C# (Staged) runs bench.b in 0.373 s with 36.6 MiB and Scala (Staged) in 0.409 s with 229.6 MiB against 0.885 s here, and both also beat C++ on mandel.b where this entry loses. If you must stay in C++, the catalogued ClangJIT and Proteus entries give the same run-time specialisation through LLVM.

## Integration

| | |
|---|---|
| **Form** | source-drop (one Racket module, brainfuck/bf-staged.rkt, run with racket and no raco make step) |
| **Dependencies** | Racket base libraries only: racket/file, racket/list, racket/match, racket/cmdline, racket/os, racket/tcp (for the suite's notify hook) and racket/unsafe/ops |
| **Minimum toolchain** | Racket CS; measured with Racket 9.2 (x86_64 linux-cs installer per docker/Dockerfile) and PLT_CS_COMPILE_LIMIT=100000; older versions not documented |
| **Platforms** | any platform Racket CS supports; measured on x86-64 Linux (Intel Xeon E-2324G) only |
| **Thread safety** | not documented; each run builds its own tape vector and the printer is a mutable struct passed in, so concurrent runs would need separate printers |
| **Drop-in for the baseline** | no |

## Gotchas

- Different algorithm from the baseline, accepted by the suite with mixed signals: owner kostya approved PR #296 on 2021-02-24 with 'seems ok, because it still interpret every instruction one by one', while collaborator nuald wrote in issue #485 (2024-03-20) that staged variants are 'not the reference implementations, and rather included just for testing purposes'. Under Racket CS the eval'd lambda is compiled to Chez machine code, not interpreted, and brainfuck/README.md asks every implementation to interpret instructions one by one.
- PLT_CS_COMPILE_LIMIT=100000 was added suite-wide in PR #301 (2021-03-04, no rationale given). Racket CS interprets the outer layer of any linklet larger than the limit (default 10000; racket/src/cs/linklet.sls) and compiles only smaller inner lambdas. Counting the instruction mix with schemify's size rules (an estimate, not measured) gives about 430 terms for bench.b and about 26,000 for mandel.b, so the bench.b result does not depend on the variable but the mandel.b result does.
- The tape grows only on the right: tape-move checks the upper bound, and the reads and writes are unsafe-vector\*-ref/set!, so a negative position silently corrupts memory (the C++ size_t index is undefined behaviour there too). The module's (#%declare #:unsafe) covers the module itself; inside the generated code only the renamed primitives are unsafe, and '&gt;' in the loop test stays the generic racket/base comparison.
- The timed region (between the notify calls) includes parsing, syntax construction and the Chez compile of the generated form, but verify() runs one staged eval of a Hello World program before timing, so expander and compiler warm-up is excluded; .NET, JVM and Racket start-up are outside the timer for every language.

## Known shortcomings

- Different algorithm: the staged Racket version compiles the Brainfuck program at runtime (eval or scala3-staging plus HotSpot) while the C++ baseline is a tree-walking interpreter, breaking the suite's interpret-each-instruction rule and with no C/C++ staged counterpart; non-staged Racket 1.761 s is slower than C++/g++ 1.097 s and it loses mandel.b 15.722 s vs 10.143 s. C++ baseline g++ 16.1.0 -O3 -march=native -flto on a Xeon E-2324G is not crippled, so tier C.
- The JSON3.jl enricher found that kostya/benchmarks' 2026-07-19 update re-measured only the Primes table and the environment table: the Json table rows kept their 2025-08-17 values (gcc 14.2.0, clang 19.1.7), so the compiler versions recorded here (gcc 16.1.0, clang 22.1.8) describe the current environment table and may not be the toolchain behind this table's rows; whether this table was re-run on 2026-07-19 was not checked.
- Compiler against interpreter: the staged variant evals syntax objects that Racket CS compiles to Chez machine code, while the C++ baseline interprets every instruction; owner kostya accepted PR #296 ('still interpret every instruction one by one') but collaborator nuald (issue #485) calls staged variants 'not the reference implementations'. PLT_CS_COMPILE_LIMIT=100000 was added suite-wide in PR #301 without rationale; by the enricher's estimate (not measured) bench.b compiles to about 430 terms and mandel.b to about 26,000, over the default 10,000, so only the mandel.b result depends on it, and the staged variant loses mandel.b (15.722 s vs 10.143 s, plus 71.69 MiB). Unsafe operations: a negative tape index corrupts memory and `>` stays generic. No harness bug behind the numbers.

## Caveats and trade-offs

Not the same algorithm: the C++/g++ baseline (brainfuck/bf.cpp) is a tree-walking interpreter that dispatches every Brainfuck instruction at run time, while the staged variant compiles the Brainfuck program to native code at run time; the suite's own brainfuck/README.md says implementations interpret every instruction one by one, so the staged rows deviate from the suite rule. The repository has no C or C++ staged/JIT counterpart, so the result shows runtime compilation beating an interpreter, not the language beating C++ at equal work. The timed region (between the notify calls) includes parsing and the run-time compile on both sides, but verify() runs one staged compile of a hello-world program before timing, warming the compiler machinery. Measurements run with QUIET=1 (analyze.rb, 10 attempts, median with MAD), so output flushing does not matter. Single machine (Xeon E-2324G), single suite. Wins only on bench.b (1.24x) and loses on mandel.b (15.722s vs 10.143s, 1.55x slower), so the bench.b win does not generalise; the bench.b margin is well outside the reported MADs on this machine. On bench.b C++/g++ is not the fastest AOT interpreter either (V/gcc 0.985s, Rust 1.008s, D/ldc2 1.078s). The generated code uses unsafe fixnum and vector operations (#%declare #:unsafe); bf.cpp also indexes std::vector without bounds checks, so safety checks are comparable. [retier] Enricher: under Racket CS the eval'd lambda is compiled to Chez machine code; owner kostya accepted PR #296 ('still interpret every instruction one by one') but collaborator nuald (issue #485) calls staged variants 'not the reference implementations'. PLT_CS_COMPILE_LIMIT=100000 was added suite-wide in PR #301 without rationale; by the enricher's estimate (not measured) bench.b compiles to about 430 terms and mandel.b to about 26,000, so only mandel.b depends on it, and the staged variant loses mandel.b (15.722 s vs 10.143 s, plus 71.69 MiB). Unsafe operations: a negative tape index corrupts memory and `>` stays generic.

About 100 MiB resident versus 3.4 MiB; uses unsafe ops (#%declare #:unsafe) so no bounds checking, the same as the C++ baseline's unchecked indexing.

## Maintenance

The suite is active and MIT-licensed (README update 2026-07-19); bf-staged.rkt has not changed since its 2023 rename and is a copyable 114-line teaching sample of Racket staging rather than a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The measurement meets A methodology (brainfuck/bf-staged.rkt vs brainfuck/bf.cpp, flags in common/commands.mk, g++ 16.1.0, Xeon E-2324G) and the numbers are on the README, but it compares a run-time compiler with an interpreter (same_algorithm false, against the suite's own interpret-one-by-one rule); the same-algorithm Racket row (1.761s) is slower than C++/g++ (1.097s), so the language-level claim rests on unequal technique and is capped at C (unequal-work precedent).
- **Verifier notes:** Numbers, flags, CPU and code all check out; downgraded A to C because the staged Racket row compiles the Brainfuck program with eval (Chez Scheme backend, PLT_CS_COMPILE_LIMIT=100000) while the C++ baseline interprets it, and the same-algorithm Racket row is 1.6x slower than C++. Not D: the C++ baseline is fully optimised (-O3 -march=native -flto), not crippled. Loses on mandel.b.
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
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf-staged.rkt>
  - <https://github.com/kostya/benchmarks/commits/master/brainfuck/bf-staged.rkt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf-staged.rkt>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.rkt>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bench.b>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/mandel.b>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/xtime.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/analyze.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/LICENSE>
  - <https://github.com/kostya/benchmarks/commits/master/brainfuck/bf-staged.rkt>
  - <https://github.com/kostya/benchmarks/commit/9dd3a91>
  - <https://github.com/kostya/benchmarks/pulls?q=is%3Apr+racket>
  - <https://github.com/kostya/benchmarks/pull/296>
  - <https://github.com/kostya/benchmarks/pull/300>
  - <https://github.com/kostya/benchmarks/pull/301>
  - <https://github.com/kostya/benchmarks/blame/master/common/commands.mk>
  - <https://github.com/kostya/benchmarks/issues/485>
  - <https://github.com/kostya/benchmarks/issues?q=is%3Aissue+racket>
  - <https://raw.githubusercontent.com/racket/racket/master/racket/src/cs/README.txt>
  - <https://raw.githubusercontent.com/racket/racket/master/racket/src/cs/linklet.sls>
  - <https://raw.githubusercontent.com/racket/racket/master/racket/src/schemify/size.rkt>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:racket/kostya/benchmarks#brainfuck-bench.b-staged`) · [data/wave14/enrich/raw/lang_racket_kostya_benchmarks_brainfuck_bench_b_staged.json](../../../data/wave14/enrich/raw/lang_racket_kostya_benchmarks_brainfuck_bench_b_staged.json) (enrichment confidence 0.7)

</details>
