# .NET runtime (CoreCLR RyuJIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C# and C++` · `MIT` · 🟢 active

> The .NET runtime's RyuJIT tiered JIT runs kostya's brainfuck interpreters 2-7x faster than Node.js, LuaJIT and PyPy, though still behind HotSpot.

| | |
|---|---|
| **Beats** | LuaJIT 2.1, PyPy 7.3.x and Node.js (V8) on kostya brainfuck in JIT mode; OpenJDK HotSpot only beaten in plb2 NativeAOT mode |
| **Claimed result** | JIT mode, kostya/benchmarks (https://github.com/kostya/benchmarks, .NET 10.0.100, Xeon E-2324G), 'C#/.NET Core' row: brainfuck bench.b 1.280 s vs Node.js 2.954 s, Lua/luajit 5.686 s, Python/pypy 9.398 s (about 2.3x, 4.4x and 7.3x, derived from page data); mandel.b 15.576 s vs luajit 31.804 s, Node.js 34.692 s, pypy 41.153 s (about 2.0x, 2.2x and 2.6x, derived from page data). Slower than Java 24.0.2 (HotSpot) on every kostya test it shares: bench.b 1.280 vs 1.191 s, mandel.b 15.576 vs 13.041 s, base64 2.374 vs 1.435 s, matmul 4.506 vs 3.057 s. NativeAOT mode, plb2 (https://github.com/attractivechaos/plb2, .NET 8.0.100 with PublishAot, Apple M1): nqueen 2.82, matmul 1.38, sudoku 1.62, bedcov 0.99 s vs OpenJDK 20.0.1 3.92, 1.14, 3.20, 3.04 s (faster on 3 of 4), luajit 5.31, 2.66, 4.48, 10.52 s and PyPy 7.3.14 6.91, 4.89, 8.82, 6.27 s (faster on all 4). |
| **Workload** | plb2 single-threaded CPU-bound tasks with the same algorithm in each language: nqueen (15 queens), matmul (1500x1500), sudoku (4000 puzzles), bedcov (1M intervals). |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E-2324G (kostya/benchmarks); Apple M1 MacBook Pro (plb2) |
| **Compiler and flags** | kostya (JIT mode): `dotnet build --nologo -v q -c Release` (common/commands.mk DOTNET_BUILD), net10.0 target, .NET SDK 10.0.100, default tiered JIT; baselines luajit 2.1.1748495995, pypy 7.3.23, Node.js v26.5.0, Java 24.0.2 run with default flags. plb2 (NativeAOT): `dotnet publish -c Release -r osx-arm64` (src/csharp/Makefile) with `<PublishAot>true</PublishAot>` in each of nqueen/matmul/sudoku/bedcov.csproj, .NET 8.0.100; Java, LuaJIT and PyPy invocations are not given in the plb2 README. |
| **Adoption** | 18.3k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/dotnet/runtime) · [benchmark](https://github.com/kostya/benchmarks) |

## Verdict

kostya/benchmarks ran these on an Intel Xeon E-2324G with .NET SDK 10.0.100, `dotnet build -c Release` and the default tiered JIT with Dynamic PGO, timing only the benchmark region. The same op-tree brainfuck interpreter took 1.280 s on bench.b and 15.576 s on mandel.b, against Node.js 26.5 (2.954 / 34.692 s) and PyPy 7.3.23 (9.398 / 41.153 s); LuaJIT 2.1, which runs a closure-based variant, took 5.686 / 31.804 s. Java 24 was faster on every shared test. Separately, plb2 timed a NativeAOT build (.NET 8, Apple M1) against OpenJDK 20, LuaJIT and PyPy.

## Use it when

- You are choosing a managed or JIT language for CPU-bound, interpreter-style or branchy code and would otherwise use JavaScript, Lua or Python. On kostya's op-tree brainfuck interpreter .NET 10 takes 1.280 s, against 2.954 s for Node.js 26.5 and 9.398 s for PyPy 7.3.23.
- Long-running services where tiered JIT warm-up is amortised and Dynamic PGO can specialise hot paths.
- Code that benefits from runtime generic specialisation over structs (staged interpreters, expression evaluators). The kostya staged C# variant runs bench.b in 0.373 s, but it is a different program from the 1.280 s one.
- A C++ application that wants a safe, garbage-collected extension or plugin layer: call managed static methods through function pointers from hostfxr, or link a NativeAOT-built library.
- Startup-sensitive tools where NativeAOT is acceptable: the plb2 NativeAOT build (.NET 8, Apple M1) beat LuaJIT and PyPy on all 4 tasks and OpenJDK 20 on 3 of 4.

## Skip it when

- Peak JIT throughput against the JVM: in kostya, Java 24 HotSpot beats .NET on every shared test (bench.b 1.191 vs 1.280 s, mandel.b 13.041 vs 15.576 s, base64 1.435 vs 2.374 s, matmul 3.057 vs 4.506 s).
- You have to keep existing Lua, Python or JavaScript code: this is a different language and runtime, not a faster engine for theirs.
- Memory-tight embedding: the .NET process starts at about 36.9 MiB RSS on bench.b, against 2.5 MiB for LuaJIT, and hosting means shipping or locating the runtime and hostfxr.
- Short-lived processes that run only JIT Tier0 code: tier-up waits for call counting after a 100 ms quiet period (10x longer on a single-CPU process), so use ReadyToRun or NativeAOT there.
- Numeric array kernels written with rectangular arrays: kostya's C# matmul (double[,]) is slower than Java, Node.js and PyPy.

## How it is fast

C# is statically typed and has value types (structs, ref structs, ref returns). RyuJIT therefore compiles IL with a conventional optimizing pipeline (SSA, value numbering, range-check elimination, register allocation) and needs no speculative type guards. Tiered compilation emits quick Tier0 code first. A method is promoted to Tier1 after 30 calls, once a 100 ms startup-quiet period has passed (TC_CallCountThreshold, TC_CallCountingDelayMs). Long-running loops move to optimized code through on-stack replacement. Tier0 code is instrumented by default (TieredPGO=1), so Tier1 compiles with Dynamic PGO counts for inlining and layout. Generic code instantiated over value types is specialized per type; kostya's 'staged' C# brainfuck variant uses this to compile the BF program into nested generic structs at run time.

## Compared with alternatives

Pick it over Julia or Chez Scheme for interpreter-style code. In the same kostya table it is faster on bench.b (1.280 vs 1.564 and 1.758 s) and mandel.b (15.576 vs 30.315 and 30.884 s), and it starts at far less memory than Julia (36.9 vs 244.0 MiB). Pick Julia for numeric array code, and LuaJIT or libriscv when you need a tiny embeddable engine.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | .NET runtime (shared framework or self-contained); nethost/hostfxr for native hosting; ICU on Linux for globalization (NativeAOT can link it statically) |
| **Minimum toolchain** | kostya used .NET SDK 10.0.100 (net10.0); plb2 used .NET SDK 8.0.100 with PublishAot; a C++ host only needs the C ABI of nethost/hostfxr (__stdcall on Windows) |
| **Platforms** | RyuJIT targets x64, x86, Arm32, Arm64, LoongArch64 and RISC-V64, with a WASM target in progress (src/coreclr/jit/CMakeLists.txt); Windows, Linux, macOS and FreeBSD build targets. The official OS support matrix was not read. |
| **Thread safety** | Multi-threaded runtime; the execution engine ensures a single jitted copy of a method when several threads trigger JIT at once, and Tier1 recompiles on a background thread-pool thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- The plb2 .NET numbers are NativeAOT, not RyuJIT JIT mode: every src/csharp/\*.csproj sets PublishAot=true. They are also hyperfine whole-process times on an M1, so they set an AOT binary against JIT runtimes that include their startup.
- Harness flaw in kostya: the LuaJIT row runs a different program (bf_jit.lua builds one closure per op over an FFI uint8 tape) from the switch-on-op tree that C#, Java, JavaScript and PyPy share. The 4.4x LuaJIT gap therefore mixes program shape with JIT quality.
- Harness flaw in kostya, against .NET: C# matmul uses rectangular double[,] arrays and Java uses jagged double[][], so .NET's matmul loss (4.506 vs 3.057 s) is not a like-for-like JIT comparison. A jagged-array or Span version was not measured.
- kostya times only the region between its start and stop socket notifications, so runtime startup is excluded but Tier0, OSR and Tier1 compilation are included. The base64 and JSON rows measure library code, not the JIT.

## Known shortcomings

- The plb2 numbers are NativeAOT (PublishAot=true in every csproj), not RyuJIT; the JIT-mode evidence is the kostya brainfuck run (dotnet build -c Release, Xeon E-2324G) where it beats LuaJIT, PyPy and V8 but loses to HotSpot on all 4 shared kostya tests. Not C++.
- Enricher: two kostya harness flaws make the comparisons not like for like: the LuaJIT row runs a different program (bf_jit.lua, one closure per op over an FFI uint8 tape), and the C# matmul uses rectangular double[,] arrays against Java's jagged double[][]. plb2 numbers are NativeAOT with whole-process hyperfine timing. Slower than HotSpot on every shared kostya test.

## Caveats and trade-offs

The plb2 .NET row is NativeAOT, not the CoreCLR RyuJIT JIT: every src/csharp/\*.csproj sets PublishAot=true, which matches the AOT star in plb2's table (the earlier note that the mode was unclear was wrong). NativeAOT lives in the same dotnet/runtime repo and uses RyuJIT as its code generator, but those numbers compare an AOT build with JIT runtimes. In JIT mode (kostya) .NET beats LuaJIT, PyPy and Node.js on the brainfuck tests but is slower than Java (HotSpot) on all four shared tests, and on matmul (4.506 s) it is slower than Java 3.057 s, Node.js 3.212 s and PyPy 3.263 s; on base64 (2.374 s) it beats only PyPy (3.534 s), losing to Node.js 0.635 s and Java 1.435 s. The kostya JSON row (System.Text.Json 0.558 s vs Java DSL-JSON 0.571 s, PyPy 0.606 s, Node.js 0.374 s) measures libraries, not the JIT. The 'C# (Staged)/.NET Core' rows (0.373 s and 2.917 s) use a different staged-compilation program and are not comparable. The plb2 author notes that, being mostly a C programmer, his implementations in other languages may be suboptimal.

Large managed runtime; use from C++ goes through the hosting API (nethost/hostfxr) or Native AOT libraries; tiered JIT with warmup.

## Maintenance

Very active (commit 2026-10-06, 18.3k stars, 5k+ open issues, 678 open PRs, MIT). Using it from C++ means hosting the runtime or exporting a NativeAOT library, so 'copyable' means moving hot code to C#, not vendoring a JIT.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now A.
- **Tier reason:** Tier raised from B on stronger evidence: kostya/benchmarks runs .NET in JIT mode with public code (brainfuck/bf.cs, brainfuck/brainfuck.csproj targeting net10.0), build flags in common/commands.mk DOTNET_BUILD (`dotnet build -c Release`), .NET SDK 10.0.100 and Intel Xeon E-2324G stated, against LuaJIT, PyPy, Node.js and Java in the same table. The plb2 numbers in the original claim are real but come from NativeAOT builds, not the JIT.
- **Verifier notes:** Numbers in the original claim match plb2, but plb2 built .NET with PublishAot=true (NativeAOT), so they do not describe RyuJIT JIT mode; rewrote the claim to lead with kostya's JIT-mode results (A-level: code, flags, versions and CPU stated) and kept plb2 as the NativeAOT second source. Against HotSpot the JIT loses everywhere in kostya; the win is against LuaJIT, PyPy and V8 on interpreter-style code. Metadata verified: MIT, 18.3k stars, last commit 2026-10-06.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `caveats`
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
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.cs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/brainfuck.csproj>
  - <https://github.com/attractivechaos/plb2/tree/master/src/csharp>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/src/csharp/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/csharp/nqueen.csproj>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/csharp/matmul.csproj>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/csharp/sudoku.csproj>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/csharp/bedcov.csproj>
  - <https://github.com/dotnet/runtime>
  - <https://github.com/dotnet/runtime/commits>
- **Sources the enricher read:**
  - <https://github.com/dotnet/runtime>
  - <https://raw.githubusercontent.com/dotnet/runtime/HEAD/README.md>
  - <https://raw.githubusercontent.com/dotnet/runtime/HEAD/docs/design/coreclr/jit/ryujit-overview.md>
  - <https://raw.githubusercontent.com/dotnet/runtime/HEAD/docs/design/features/tiered-compilation.md>
  - <https://raw.githubusercontent.com/dotnet/runtime/HEAD/docs/design/features/OnStackReplacement.md>
  - <https://raw.githubusercontent.com/dotnet/runtime/HEAD/docs/design/features/DynamicPgo.md>
  - <https://raw.githubusercontent.com/dotnet/runtime/HEAD/docs/design/features/native-hosting.md>
  - <https://raw.githubusercontent.com/dotnet/runtime/HEAD/docs/workflow/requirements/linux-requirements.md>
  - <https://raw.githubusercontent.com/dotnet/runtime/HEAD/src/coreclr/inc/clrconfigvalues.h>
  - <https://raw.githubusercontent.com/dotnet/runtime/HEAD/src/coreclr/jit/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dotnet/runtime/HEAD/src/coreclr/nativeaot/docs/README.md>
  - <https://raw.githubusercontent.com/dotnet/runtime/HEAD/src/coreclr/nativeaot/docs/compiling.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.cs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/brainfuck.csproj>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/brainfuck-staged.csproj>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf-staged.cs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.java>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.js>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf_jit.lua>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf3.py>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.cs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.java>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/dotnet/runtime`) · [data/wave12/enrich/raw/github_com_dotnet_runtime.json](../../../data/wave12/enrich/raw/github_com_dotnet_runtime.json) (enrichment confidence 0.7)

</details>
