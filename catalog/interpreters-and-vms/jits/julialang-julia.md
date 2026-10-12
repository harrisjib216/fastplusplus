# Julia

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Julia (C/C++ runtime on LLVM; embeddable from C/C++ through libjulia)` · `MIT` · 🟢 active

> Dynamic language JIT-compiled through LLVM per concrete argument types; beats LuaJIT, PyPy and Node on loop-heavy CPU code.

| | |
|---|---|
| **Beats** | LuaJIT 2.1, PyPy 3 (7.3.x), Node.js (V8) and OpenJDK HotSpot, on the same CPU-bound algorithms |
| **Claimed result** | kostya/benchmarks brainfuck bench.b: Julia 1.564 s vs luajit 5.686 s, pypy 9.398 s, Node.js 2.954 s (about 3.6x, 6.0x and 1.9x, derived from page data); Java 1.191 s is faster. mandel.b: Julia 30.315 s vs luajit 31.804 s, Node.js 34.692 s, pypy 41.153 s; Java 13.041 s is faster. The kostya matmul 'no BLAS' row (1.113 s vs Java 3.057 s) is not like for like (see caveats); like-for-like plb2 matmul (Apple M1) gives about 1.5x over Java. plb2 Julia 1.10.0: nqueen 3.02 s, matmul 0.76 s, sudoku 2.18 s. |
| **Workload** | Single-threaded CPU-bound programs written with the same algorithm in every language: kostya/benchmarks brainfuck interpreter (bench.b, mandel.b) and naive matrix multiply; plb2 nqueen, matmul (1500x1500), sudoku, bedcov. |
| **Metric** | throughput |
| **Hardware** | kostya/benchmarks: Intel Xeon E-2324G; plb2: Apple M1 MacBook Pro |
| **Compiler and flags** | kostya/benchmarks: julia v1.11.6 run as `julia --optimize=3 --check-bounds=no`; Java 24.0.2, Node.js v26.5.0, luajit 2.1.1748495995, pypy 7.3.23 (Python 3.11.15), Docker on Debian; run commands in common/commands.mk. plb2 versions in its README table (Julia 1.10.0, Java 20.0.1, PyPy 7.3.14, LuaJIT 2.1, Node 21.5.0). |
| **Adoption** | 49.2k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/JuliaLang/julia) · [benchmark](https://github.com/kostya/benchmarks) |

## Verdict

Two public cross-language suites agree on the direction. In kostya/benchmarks (Julia 1.11.6 with `--optimize=3 --check-bounds=no`, Intel Xeon E-2324G, Docker on Debian, medians), the brainfuck bench.b ran in 1.564 s, against Node.js v26.5.0 at 2.954 s, LuaJIT 2.1 at 5.686 s and PyPy 7.3.23 at 9.398 s, while Java 24 was faster at 1.191 s. In plb2 (hyperfine wall-clock time on an Apple M1, Julia 1.10.0), Julia beat Java 20, Node 21.5, LuaJIT 2.1 and PyPy 7.3.14 on nqueen, matmul, sudoku and bedcov.

## Use it when

- Numeric loops over Float64 arrays, written as plain loops: plb2 matmul (1500x1500, Apple M1) took 0.76 s, against 1.14 s for OpenJDK 20, 2.66 s for LuaJIT 2.1, 2.88 s for Node 21.5 and 4.89 s for PyPy 7.3.14.
- Branchy integer and bit-twiddling search: plb2 nqueen took 3.02 s (Java 3.92, LuaJIT 5.31, PyPy 6.91) and sudoku 2.18 s (Java 3.20, LuaJIT 4.48, PyPy 8.82).
- Jobs that run for seconds or longer, where compile time is amortized: kostya's brainfuck interpreter on bench.b took 1.564 s, against 2.954 s for Node.js, 5.686 s for LuaJIT and 9.398 s for PyPy.
- Replacing Python or NumPy prototypes in scientific code with one language that calls C and Fortran libraries without wrapper code.
- Adding a numeric scripting layer to a C or C++ application, provided you can accept a heavy runtime: libjulia exposes jl_init, jl_eval_string and jl_call.

## Skip it when

- Short-lived scripts and CLI tools: every process compiles on first call. Kostya measured a 244 MB base RSS against 2.5 MB for LuaJIT, and plb2 notes JIT runtimes can spend up to about 0.3 s compiling and warming up.
- String, byte and JSON-heavy workloads: in kostya's runs, base64 took 3.085 s (Node 0.635 s, Java 1.435 s), JSON with JSON3 0.700 s (Node 0.374 s) and primes 0.680 s (Java 0.161 s, LuaJIT 0.309 s, PyPy 0.617 s).
- When OpenJDK HotSpot is the bar for interpreter-style code: on kostya's runs Java took 1.191 s on bench.b against Julia's 1.564 s, and 13.041 s on mandel.b against 30.315 s.
- Type-unstable code (untyped globals, abstract-typed containers or fields): the Performance Tips manual says this blocks inference and adds allocation, and speed falls back toward dynamic-language levels.
- Hosts that call into the runtime from arbitrary threads, or that need a small embeddable VM: the C API requires jl_init exactly once and allows jl_ calls only from that thread or from threads Julia started.

## How it is fast

When a function is first called with a given set of argument types, type inference (Compiler/src/typeinfer.jl) bounds every variable's type. It also does constant propagation and inlining. Codegen (codegen.cpp) then emits LLVM IR that LLVM optimizes to native code. This is method specialization driven by multiple dispatch, with no tracing and no deoptimization tier, so type-stable code with concrete-typed arrays compiles much like C. Users can add `@inbounds`, `@simd` and `@fastmath` to drop bounds checks and allow SIMD vectorization and floating-point reassociation. Since 1.9, precompiled packages store native code in pkgimages, which cuts warm-up.

## Compared with alternatives

Pick Julia over the Dart VM or Chez Scheme for numeric and array code: plb2 matmul 0.76 s vs Dart 2.74 s and Chez 9.5.8 at 18.98 s. Julia also beat Dart on all four plb2 tasks. Pick the .NET runtime (CoreCLR) instead for interpreter-style or object-heavy code and when start-up and memory matter: on kostya bench.b C#/.NET took 1.280 s vs Julia's 1.564 s with 37 MB vs 244 MB base RSS, and .NET 8 NativeAOT beat Julia on plb2 nqueen, sudoku and bedcov but not matmul (1.38 s vs 0.76 s).

## Integration

| | |
|---|---|
| **Form** | language runtime: the `julia` executable, plus the libjulia shared library and julia.h for embedding (julia-config.jl prints the cflags, ldflags and ldlibs) |
| **Dependencies** | Prebuilt binaries bundle a patched LLVM (master pins LLVM 22.1.8 in deps/llvm.version), OpenBLAS and other libraries. Building from source needs gcc/g++ 7.1+ or Clang 5.0+, gfortran, libatomic, cmake, python3 and perl. |
| **Minimum toolchain** | Building: gcc 7.1+ or Clang 5.0+ (Apple Clang 9.3+). Embedding: any C/C++ compiler that links libjulia. kostya ran Julia 1.11.6 and plb2 ran 1.10.0. |
| **Platforms** | Linux, macOS, Windows and FreeBSD; x86-64, ARM (aarch64) and RISC-V have build notes. Support tiers are on julialang.org (not opened). |
| **Thread safety** | The language has multithreading (tasks, Threads.@threads). The embedding C API is 'not fully thread-safe': jl_init may be called once, and jl_ functions only from that thread or from threads the Julia runtime started. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the kostya matmul row: 'Julia (no BLAS)' (1.113 s) runs a column-major saxpy loop with `@simd ivdep` and `@fastmath`, while Java (3.057 s) and C/gcc (3.034 s) transpose b and run a strict-IEEE dot-product reduction that cannot vectorize. Plain C matches Java, so the 2.7x reflects loop shape and fast-math, not the runtime. Plb2's like-for-like matmul gives 1.5x over Java (0.76 s vs 1.14 s).
- Kostya runs Julia with `--check-bounds=no`. Core developer Keno Fischer (open issue #48245, 'Consider removing --check-bounds=no?') calls the flag unsafe and says it can make code 'significantly' slower by disabling concrete evaluation in inference. The published numbers therefore come from a non-default, discouraged setting, and default runs may be faster or slower.
- Kostya's timer starts after the notify() call, after a verify() run on the same functions, so most JIT compile time is excluded. Plb2 includes start-up and compile time and reports wall-clock time; its README notes Julia uses noticeably more CPU time than wall time even on nqueen.
- Kostya's bf.jl is a weaker algorithm than the Java and Node ports: it matches brackets by scanning raw characters at run time, where they parse an op tree first. Julia's bench.b win over Node, LuaJIT and PyPy holds despite that, but this row compares code shapes, not only runtimes.

## Known shortcomings

- Loses kostya base64, primes and JSON to most baselines; the kostya no-BLAS matmul uses @simd ivdep plus @fastmath and runs with --check-bounds=no, so it is not like for like. Not an embeddable C++ library.
- Enricher: the kostya matmul 'no BLAS' row is not like for like: Julia runs a column-major saxpy with @simd ivdep and @fastmath while Java and C/gcc run a transposed strict dot product (C/gcc 3.034 s about equals Java 3.057 s), so the 2.7x reflects loop shape rather than the JIT; the like-for-like plb2 matmul gives 1.5x over Java. kostya runs with --check-bounds=no, which issue #48245 calls unsafe and possibly slower. bf.jl scans brackets at run time, so the bench.b win stands.

## Caveats and trade-offs

Workload specific: Java beats Julia on kostya's bench.b and mandel.b, and in kostya's other tests Julia loses to most baselines: base64 3.085 s vs Node.js 0.635 s and Java 1.435 s (Julia does beat PyPy 3.534 s there); primes 0.680 s vs Java 0.161 s, Node.js 0.207 s, luajit 0.309 s and PyPy 0.617 s; JSON (JSON3) 0.700 s vs Node.js 0.374 s, Java DSL-JSON 0.571 s and PyPy 0.606 s. In plb2 Julia beats all four baselines. The kostya run uses --check-bounds=no (bounds checks removed) and plb2's Julia sources use @inbounds in hot loops, which other languages' sources do not. The kostya 'no BLAS' matmul source is not a plain triple loop: it uses @simd ivdep and @fastmath (allowing reassociation and vectorized FMA, which Java and V8 cannot do) and wraps the outer loop in Threads.@threads (single-threaded here, since JULIA_RUN passes no -t and sets no JULIA_NUM_THREADS). Julia matmul rows at 0.12-0.17 s use BLAS and are not comparable. The kostya brainfuck bf.jl scans raw characters and brackets at run time, while the Node, Java and C# versions parse an op tree first, so the code shapes differ. Each program runs a small verify() before the timer starts, which warms the JIT on the same functions, so most compile time is outside the timed region; plb2 includes startup and compile time. kostya's docker/Dockerfile now pins julia-1.12.6 while the README environment lists v1.11.6, so the published numbers predate the current image.

Per-process JIT warmup and large footprint (kostya bench.b base RSS about 244 MB vs 2.5 MB for LuaJIT); package precompilation latency; garbage collected; embedding in C++ goes through the libjulia C API and is heavier than embedding LuaJIT.

## Maintenance

Very active (MIT, 49.2k stars, 3.7k open issues, master at 1.14-dev with commits on 2026-10-06) and production-grade. You adopt it as a whole language and runtime rather than vendoring code, and its wins are limited to loop- and array-heavy code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** kostya/benchmarks README rows match exactly; benchmark code brainfuck/bf.jl and matmul/matmul.jl is public, run via common/commands.mk JULIA_RUN (`julia --optimize=3 --check-bounds=no`), Julia v1.11.6 listed in the README environment, Intel Xeon E-2324G, baselines' versions and run commands in the same files. plb2 (Apple M1, versions in its table) agrees.
- **Verifier notes:** Every number in the claim matches the kostya and plb2 tables. Corrected one caveat (Julia beats PyPy on base64, it does not lose to it) and added that the kostya no-BLAS matmul uses @simd ivdep and @fastmath, so that row is not a like-for-like loop. Metadata verified: MIT, 49.2k stars, last commit 2026-10-06.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kostya/benchmarks>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://github.com/kostya/benchmarks/tree/master/brainfuck>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf_jit.lua>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.js>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf3.py>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.java>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/docker/Dockerfile>
  - <https://github.com/attractivechaos/plb2>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.jl>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.jl>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/Makefile>
  - <https://github.com/attractivechaos/plb2/tree/master/src/julia>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/julia/matmul.jl>
  - <https://github.com/JuliaLang/julia>
  - <https://github.com/JuliaLang/julia/commits>
- **Sources the enricher read:**
  - <https://github.com/JuliaLang/julia>
  - <https://raw.githubusercontent.com/JuliaLang/julia/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaLang/julia/HEAD/NEWS.md>
  - <https://raw.githubusercontent.com/JuliaLang/julia/HEAD/HISTORY.md>
  - <https://raw.githubusercontent.com/JuliaLang/julia/HEAD/doc/src/manual/embedding.md>
  - <https://raw.githubusercontent.com/JuliaLang/julia/HEAD/doc/src/manual/performance-tips.md>
  - <https://raw.githubusercontent.com/JuliaLang/julia/HEAD/doc/src/devdocs/eval.md>
  - <https://raw.githubusercontent.com/JuliaLang/julia/HEAD/doc/src/devdocs/build/build.md>
  - <https://raw.githubusercontent.com/JuliaLang/julia/HEAD/deps/llvm.version>
  - <https://github.com/JuliaLang/julia/issues/48245>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.jl>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.java>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.js>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf_jit.lua>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.jl>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.java>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.js>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/docker/Dockerfile>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/README.md>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/julia/matmul.jl>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/julia/nqueen.jl>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/julia/sudoku.jl>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/julia/bedcov.jl>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/julialang/julia`) · [data/wave12/enrich/raw/github_com_julialang_julia.json](../../../data/wave12/enrich/raw/github_com_julialang_julia.json) (enrichment confidence 0.8)

</details>
