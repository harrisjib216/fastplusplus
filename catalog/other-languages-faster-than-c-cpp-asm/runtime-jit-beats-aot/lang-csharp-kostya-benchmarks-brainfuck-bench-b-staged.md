# C# (Staged) on .NET: Brainfuck bench.b in kostya/benchmarks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟢 active

> Single-file C# Brainfuck runner that turns the program into nested generic types for RyuJIT; 2.9x faster than kostya's C++ interpreter.

| | |
|---|---|
| **Beats** | C++/g++ brainfuck (brainfuck/bf.cpp): an AST-walking interpreter with std::vector ops, g++ -O3 -march=native -flto |
| **Claimed result** | kostya/benchmarks Brainfuck table: C# (Staged) bench.b 0.571 s class against the reference C++ interpreter (ratios as recorded), and mandel.b 2.917 s (about 3.5x); plain C# is slower on both programs (bench.b 1.280 vs 1.097 s, mandel.b 15.576 vs 10.143 s). |
| **Workload** | Run the bench.b Brainfuck program; the staged C# version builds a closed generic type per Brainfuck program (static abstract interface members, ref structs) and lets RyuJIT compile it, inside the timed region. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E-2324G (README Environment section); Debian forky/sid Docker image |
| **Compiler and flags** | C++ baseline: g++ 16.1.0 -O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries -std=c++23 (common/commands.mk GCC_CPP_BUILD); clang++ 22.1.8 row uses the same flags plus -stdlib=libc++; C rows -std=c23. C# (Staged): .NET 10.0.100, dotnet build -c Release, root Directory.Build.props sets TieredCompilation=false (every method JIT-compiled once at full optimisation, no tier-0 or dynamic PGO), ServerGarbageCollection=true, ConcurrentGarbageCollection=true; RyuJIT targets the host CPU at run time. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | Runtime specialization on the input program (first Futamura-style staging): the JIT sees the whole Brainfuck program as types and removes interpretation overhead (derived from reading brainfuck/bf-staged.cs; the README gives no explanation). |
| **Adoption** | 2.9k stars |
| **Last commit** | 2026-07-19 |
| **Links** | [repository](https://github.com/kostya/benchmarks) · [benchmark](https://github.com/kostya/benchmarks) |

## Verdict

In kostya/benchmarks (README update 2026-07-19, Intel Xeon E-2324G, medians of repeated runs), the staged C# runner on .NET 10.0.100 with TieredCompilation=false ran bench.b in 0.373 s, 14.33 J, against 1.097 s and 46.21 J for the C++ AST interpreter built with g++ 16.1.0 -O3 -march=native -flto=auto (C/gcc 1.112 s, C++/clang++ 22.1.8 with libc++ 1.167 s), about 2.9x (derived from page data); the same pair runs mandel.b in 2.917 s against 10.143 s (about 3.5x, derived from page data). The win is run-time compilation of the Brainfuck program set against a reference interpreter, not .NET code generation beating g++ at equal work.

## Use it when

- As a reference pattern for runtime specialization in .NET: a small DSL, rule or filter program known only at run time that executes many times (bench.b: 185 instructions run for 0.37 s; mandel.b: 11,451 instructions).
- When you want interpreter-to-native speedups without writing IL, Reflection.Emit or expression trees: the code generator is about 50 lines of MakeGenericType calls.
- Workloads where a few milliseconds of type construction and JIT inside the run are amortized; both suite programs run for 0.37-2.9 s including that cost.
- Teaching or comparing staging across runtimes: the same suite has Scala (Staged) and Racket (Staged) variants of the identical task.

## Skip it when

- As evidence that C# beats C++ at the same work: the plain C# interpreter in the same table is slower than C++/g++ (bench.b 1.280 vs 1.097 s; mandel.b 15.576 vs 10.143 s), and no C++ JIT or staged variant was benchmarked.
- Memory-tight or start-up-sensitive processes: 36.62 MiB base RSS against 3.38 MiB for the C++ interpreter, plus the .NET runtime start-up that the harness excludes from timing.
- NativeAOT, trimmed or other no-JIT deployments: the whole technique depends on Type.MakeGenericType and reflection at run time; the suite builds it only with dotnet build for the JIT runtime.
- Untrusted programs: the tape is read and written with Unsafe.Add and only the right edge is guarded, so moving left of cell 0 writes outside the array instead of throwing.
- Short-lived programs that run once for microseconds: every distinct program costs type loading and JIT before the first instruction runs.

## How it is fast

This is first Futamura-style staging (program specialization) done with the .NET type system. Type.MakeGenericType encodes the parsed program as a type, and the JIT compiles a separate specialized method body for each closed instantiation, so instruction dispatch, the switch on op kind and the walk over an op vector disappear; what remains is straight-line code with calls or inlined bodies chained by Next.Run tail calls. Tape access skips bounds checks (Unsafe.Add on a Span&lt;byte&gt;), and the suite-wide Directory.Build.props sets TieredCompilation=false, so every instantiation is compiled once at full optimisation. The C++ baseline pays a switch and a recursive vector&lt;Op&gt; walk for every instruction.

## Compared with alternatives

Among the staged rows of the same table it is the fastest and leanest (bench.b 0.373 s and 36.6 MiB against Scala (Staged) 0.409 s and 229.6 MiB and Racket (Staged) 0.885 s and 101.4 MiB; mandel.b 2.917 s against 7.118 s and 15.722 s), so pick it when your host language is C#. If you must stay in C++, the catalogued ClangJIT and Proteus entries give C++ the same run-time specialization through LLVM.

## Integration

| | |
|---|---|
| **Form** | source-drop (one C# file, brainfuck/bf-staged.cs, built by brainfuck-staged.csproj) |
| **Dependencies** | none beyond the .NET base class library |
| **Minimum toolchain** | .NET 10 SDK as built (TargetFramework net10.0; README lists .NET 10.0.100, current Dockerfile SDK 10.0.302); uses static abstract interface members and 'allows ref struct' generic constraints |
| **Platforms** | any platform with the CoreCLR JIT; measured on x86-64 Linux only |
| **Thread safety** | not documented; each Run builds its own tape and the Printer is passed by ref, so separate runs share nothing but the runtime's type cache |
| **Drop-in for the baseline** | no |

## Gotchas

- Different algorithm from the baseline: brainfuck/README.md requires every implementation to interpret instructions one by one without squashing, and the maintainer (nuald, issue #485, 2024-03-20) says staged variants are 'not the reference implementations, and rather included just for testing purposes'; the C++ side is the reference interpreter, not a C++ JIT.
- Tape semantics differ: C# uses byte cells that wrap at 256 and loops on != 0, C++ uses int cells and loops on &gt; 0; both suite programs agree on output, but other Brainfuck programs may not.
- AtNoRangeCheck's comment says the address 'has been guarded in AddPointer', but SubPointer never checks the left edge, so a program that steps below cell 0 silently corrupts managed memory (the C++ interpreter's size_t index would also go out of bounds there).
- The JIT and type-construction cost is inside the timed region (xtime.rb times from the program's start message to its stop message), which counts against the staged row; .NET runtime start-up and the Hello World self-check are outside it for every language.

## Known shortcomings

- Different algorithm: the staged C# version compiles the Brainfuck program at runtime while the C++ baseline is an AST interpreter (the suite's brainfuck README requires interpreting) with no C++ staged counterpart; plain C# is slower (1.280 vs 1.097 s); about 11x the memory; .NET run with TieredCompilation=false and Server GC. The mandel.b row (2.917 vs 10.143 s, plain C# 15.576 s) is folded into this record.
- The JSON3.jl enricher found that kostya/benchmarks' 2026-07-19 update re-measured only the Primes table and the environment table: the Json table rows kept their 2025-08-17 values (gcc 14.2.0, clang 19.1.7), so the compiler versions recorded here (gcc 16.1.0, clang 22.1.8) describe the current environment table and may not be the toolchain behind this table's rows; whether this table was re-run on 2026-07-19 was not checked.
- Different algorithm: a run-time generic-type compiler against the reference C++ interpreter; maintainer nuald (issue #485) says the staged variants are not the reference implementations and are just for testing. Plain C# is slower on both programs (bench.b 1.280 vs 1.097 s, mandel.b 15.576 vs 10.143 s); staged also wins mandel.b at 2.917 s (3.5x), missing from the record. Latent bug: SubPointer has no left-edge check with an Unsafe.Add tape, so going below cell 0 writes out of bounds (suite programs unaffected). JIT time sits inside the timed region; byte cells with != 0 against int cells with &gt; 0.

## Caveats and trade-offs

Different algorithm: the C++ baseline (brainfuck/bf.cpp) interprets a vector&lt;Op&gt; AST instruction by instruction, as brainfuck/README.md requires of every implementation ('interprets all bf instructions, one by one, without any squash or other hacks'), while the staged C# variant compiles the Brainfuck program to native code at run time (type construction and JIT inside the timed region), so it is listed as a separate '(Staged)' row. No C++ counterpart that also specializes on the program (template staging, LLVM ORC or asmjit, a BF-to-C compiler) was benchmarked, so the result shows runtime specialization beating an interpreter, not the .NET runtime beating C++ at the same work. The plain C# interpreter in the same suite is slower than C++/g++. The staged tape is a byte array with != 0 loop tests, the C++ tape a vector&lt;int&gt; with &gt; 0 tests (outputs agree by checksum). The staged variant was contributed by hez2010 in PR #511 (merged 2025-11-17). It uses about 11x the memory of the C++ row (36.9 vs 3.38 MiB). Results are medians from one suite run on one machine (Xeon E-2324G), timed between libnotify start and stop messages, so process start-up is excluded for every language. [retier] Different algorithm: a run-time generic-type compiler against the reference C++ interpreter; the maintainer (issue #485) says the staged variants are not the reference implementations. Latent bug: SubPointer has no left-edge check with an Unsafe.Add tape, so going below cell 0 writes out of bounds (suite programs unaffected). JIT time sits inside the timed region; byte cells with != 0 against int cells with &gt; 0.

Run-time compile inside the process: needs the .NET JIT and about 36 MiB resident versus about 3.4 MiB for the C++ interpreter; wins only for programs long enough to amortize compilation.

## Maintenance

The suite is active (MIT, 2.9k stars, last update 2026-07-19), and bf-staged.cs has had exactly one commit (e645c23, PR #511, 2025-11-17); it is a copyable teaching sample of .NET generic staging rather than a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The measurement itself is reproducible (README bench.b table, brainfuck/bf-staged.cs vs brainfuck/bf.cpp, flags in common/commands.mk and Directory.Build.props, Xeon E-2324G), but the staged C# row runs a different algorithm (a run-time compiler) against the suite's C++ interpreter, so it cannot stand at A as a language-level win; capped at C like a tuned variant measured in place of the comparable program (Topaz precedent).
- **Verifier notes:** Numbers match the README row exactly; repo metadata (MIT, 2.9k stars, last commit 2026-07-19) checks out. Shortcoming: staged C# compiles the Brainfuck program at run time while the C++ baseline interprets it (the suite's brainfuck README requires interpretation), no C++ staged or JIT counterpart exists in the suite, and the plain C# interpreter is slower than C++ (1.280 vs 1.097 s); the win is runtime specialization, not the language. If the orchestrator reads the C++ interpreter as naive code against a tuned other-language version, the crippled-baseline precedent would put it at D.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** verifier batch-05 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/commits/master>
  - <https://github.com/kostya/benchmarks/pull/511>
  - <https://github.com/kostya/benchmarks/tree/master/brainfuck>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf-staged.cs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.cs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/brainfuck-staged.csproj>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/Directory.Build.props>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/pull/511>
  - <https://github.com/kostya/benchmarks/pull/512>
  - <https://github.com/kostya/benchmarks/issues?q=staged>
  - <https://github.com/kostya/benchmarks/issues/485>
  - <https://github.com/kostya/benchmarks/commits/master/brainfuck/bf-staged.cs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf-staged.cs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.cs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/brainfuck-staged.csproj>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bench.b>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/mandel.b>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/Directory.Build.props>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/libnotify/libnotify.h>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/xtime.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/LICENSE>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:csharp/kostya/benchmarks#brainfuck-bench.b-staged`) · [data/wave14/enrich/raw/lang_csharp_kostya_benchmarks_brainfuck_bench_b_staged.json](../../../data/wave14/enrich/raw/lang_csharp_kostya_benchmarks_brainfuck_bench_b_staged.json) (enrichment confidence 0.7)

</details>
