# Lua-CSharp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟢 active

> Pure C# Lua 5.2 interpreter for .NET and Unity with low-overhead C# interop; beats NLua and MoonSharp on host-call loops.

| | |
|---|---|
| **Beats** | NLua (C# binding to native Lua) and MoonSharp (Lua interpreter in C#) |
| **Claimed result** | 8.05 ms vs NLua 36.45 ms and MoonSharp 19.87 ms (about 4.5x and 2.5x faster, derived from page data); allocation 31.3 KB vs NLua 12,306.5 KB and MoonSharp 13,887 KB. |
| **Workload** | add.lua loop calling a host C# add(x, 1) function 25,001 times (for _ = 0, 25000), timed through DoString/DoFile so script compilation is included; time and managed allocation per invocation (sandbox/Benchmark/AddBenchmark.cs). |
| **Metric** | throughput |
| **Compiler and flags** | BenchmarkDotNet 0.14.0 ShortRun job with 10 warmup and 10 measured iterations and MemoryDiagnoser, target net8.0 (sandbox/Benchmark/Benchmark.csproj); baselines MoonSharp 2.0.0 and NLua 1.7.3 NuGet packages; build configuration and runtime used for the chart not stated |
| **Adoption** | 862 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/nuskey8/Lua-CSharp) · [benchmark](https://github.com/nuskey8/Lua-CSharp) |

## Verdict

First-party README chart (made 2024-10-14 with sandbox/Benchmark: BenchmarkDotNet 0.14.0 ShortRun, 10 warm-up and 10 measured single-invocation iterations, MemoryDiagnoser, net8.0, NLua 1.7.3, MoonSharp 2.0.0; CPU, runtime and plotted variant not stated): a Lua loop calling a host add(x, 1) 25,001 times took 8.05 ms in Lua-CSharp vs 36.45 ms in NLua and 19.87 ms in MoonSharp (about 4.5x and 2.5x, derived from page data), allocating 31.3 KB vs 12,306.5 KB and 13,887 KB.

## Use it when

- .NET or Unity applications whose scripts call many small C# functions: the README chart shows a 25,001-iteration Lua loop calling a C# add() in 8.05 ms vs 36.45 ms for NLua 1.7.3 and 19.87 ms for MoonSharp 2.0.0.
- Allocation-sensitive hosts (Unity frame loops, servers watching GC pauses): 31.3 KB allocated for that loop against 12,306.5 KB (NLua) and 13,887 KB (MoonSharp).
- Targets where native Lua binaries or runtime IL generation are a problem: Unity IL2CPP and Mono, NativeAOT; the library is fully managed and does not emit IL.
- Game scripting that wants async/await: a C# LuaFunction can await Task.Delay or other tasks and resume the Lua script afterwards; Lua coroutines can be awaited from C#.
- Exposing C# types to Lua without reflection at run time, via the [LuaObject]/[LuaMember]/[LuaMetamethod] source generator.

## Skip it when

- Raw Lua compute speed: no published numbers against PUC Lua or LuaJIT (the repo's NBodyBenchmark has no results), and the only chart measures host-call overhead.
- Scripts that rely on byte strings: strings are UTF-16, so string.len("あいうえお") returns 5 instead of 15 and all string functions work on UTF-16 units; not every standard library function is implemented; GC follows .NET, so collectgarbage only maps onto .NET GC calls.
- Untrusted scripts that need instruction or time budgets: issue #338 (open) measured the count hook raising a 2,000,000-iteration loop from 22 ms to 72 ms (empty hook) and 127 ms (hook with checks).
- Sharing one interpreter across threads: the README says LuaState is not thread-safe; #309 (open) reports a thread-safety question in [LuaObject] lazy initialization.
- Hosts outside .NET: it is a managed library, not callable from C++ or Rust; Luau or PUC Lua fit native hosts.

## How it is fast

It compiles Lua to the PUC Lua 5.2 register-based instruction set (Move, LoadK, GetTabUp, Call, ForLoop...) and runs a switch-dispatch VM over a shared LuaStack of LuaValue structs (type tag, double, object reference), so numbers are not boxed. C# functions read typed arguments straight off that stack (context.GetArgument&lt;double&gt;) and write results back to it, avoiding the per-call object[] arrays and reflection invokes of NLua and MoonSharp's delegate binding. Execution contexts are pooled and async paths use a custom LightAsyncValueTaskMethodBuilder to keep allocations near zero (31.3 KB for 25,001 host calls in the chart).

## Compared with alternatives

Pick Lua-CSharp when the host is .NET or Unity and you want Lua without native binaries; the catalogued Lua engines (Luau, LuaJIT Remake, Daslang) are native C/C++ VMs that a .NET host would reach only through a binding like NLua, which is exactly the interop cost this library avoids. Roto plays the same role for Rust hosts.

## Integration

| | |
|---|---|
| **Form** | NuGet package (managed .NET assembly, LuaCSharp) plus a Unity package via git URL |
| **Dependencies** | LuaCSharp.Annotations and LuaCSharp.SourceGenerator (its own packages); Microsoft.Bcl.TimeProvider on net6.0 and netstandard2.1; System.Runtime.CompilerServices.Unsafe on netstandard2.1 |
| **Minimum toolchain** | .NET Standard 2.1 (builds for net6.0, net8.0, net10.0, netstandard2.1); Unity 2021.3+; C# 13 to build from source |
| **Platforms** | any .NET runtime including NativeAOT, Unity Mono and IL2CPP; single-threaded WebGL had a coroutine.yield deadlock (#327, closed); #337 (open) reports a missing System.Runtime.CompilerServices.Unsafe on Unity |
| **Thread safety** | LuaState is not thread-safe (README); use one state per thread |
| **Drop-in for the baseline** | partial — Lua 5.2 scripts mostly run unchanged, but the C# API (async LuaState, LuaValue, LuaFunction delegates, [LuaObject]) differs from NLua and MoonSharp, and string semantics are UTF-16 |

## Gotchas

- The README chart is stale and asymmetric: docs/Benchmark.png was last updated 2024-10-14 (v0.2-era code; add.lua went from 10,000 to 25,000 iterations that day and the C# callback API changed again in April 2025) and has not been re-run in the 13 releases since; it names no CPU, runtime or which variant (DoString or DoFile) is plotted. Lua-CSharp's add is a hand-written stack-reading callback, while NLua registers a MethodInfo (reflection invoke per call) and MoonSharp gets an auto-converted Func&lt;double,double,double&gt;; MoonSharp's DynValue.NewCallback and NLua's KeraLua state (lua.State) are not used. The harness uses [IterationSetup], which forces one invocation per iteration and which BenchmarkDotNet says should not be used for microbenchmarks under about 100 ms (each run here is 8-36 ms, 10 iterations, ShortRun).
- Direction matters: in issue #156 (May 2025, Unity Mono on Windows, calling an empty Lua function from C# 5,000 times per frame) Lua-CSharp 0.4.2 ran at 40 fps against NLua 170 and MoonSharp 315; an unofficial 0.5 build reached 395 fps after exception-handling overhead was found in the profiler. User measurement, no hardware stated.
- Open correctness bug #344 (2026-10-05): obj:Method() through a function-valued __index can receive the wrong self after a preceding metamethod call (OP_SELF register/frame reuse suspected); workaround is calling Type.Method(obj, ...) explicitly.
- [LuaObject] classes reserve __index and __newindex for generated code, so those metamethods cannot be set by the user.

## Known shortcomings

- Enricher: the README chart dates from 2024-10-14 (v0.2 era) and was not re-run in 13 releases; the benchmark is asymmetric (Lua-CSharp uses a hand-written stack callback while NLua gets a MethodInfo reflection call via RegisterFunction and MoonSharp an auto-converted Func), and [IterationSetup] forces one invocation per iteration on 8-36 ms runs that BenchmarkDotNet says are too short for it. Issue #156 (Unity Mono) shows the opposite direction (C# calling Lua) at 40 fps for 0.4.2 against NLua 170 and MoonSharp 315; open bug #344 (wrong self on obj:Method() after a metamethod call); count-hook overhead 3.2-5.4x (#338).

## Caveats and trade-offs

The README shows only a chart image (docs/Benchmark.png) with no CPU, .NET runtime version or commit, and does not say whether the DoString or DoFile variant was plotted; the source is in sandbox/Benchmark/AddBenchmark.cs but not linked from the README. The workload measures host-call interop overhead (NLua marshals through reflection-registered methods into native Lua), not Lua execution speed, so it says nothing about Lua-CSharp's VM versus PUC Lua; the repo has an NBodyBenchmark with no published numbers. A .NET library, not callable from C++. First-party numbers. [retier] Interop-call microbenchmark only (sandbox/Benchmark/AddBenchmark.cs, BenchmarkDotNet on net8.0 against NLua 1.7.3 and MoonSharp 2.0.0) with no hardware and the chart variant unstated; the README chart dates from 2024-10-14 (v0.2 era) and was not re-run in 13 releases. Asymmetric: Lua-CSharp uses a hand-written stack callback while NLua gets a MethodInfo reflection call (RegisterFunction) and MoonSharp an auto-converted Func; [IterationSetup] forces one invocation per iteration on 8-36 ms runs, below BenchmarkDotNet's recommended minimum. Issue #156 (Unity Mono): C# calling Lua ran 40 fps on 0.4.2 against NLua 170 and MoonSharp 315 (395 on an unofficial 0.5 build). Open bug #344 (wrong self after a metamethod call); count-hook overhead 3.2-5.4x (#338). C#, not an embeddable C++ engine.

Pure managed C# implementation (works in AOT and Unity, no native dependency, no IL generation) but not every Lua standard library function is supported (see its Compatibility section); strings are UTF-16.

## Maintenance

Active (v0.5.7 on NuGet 2026-09-26, commits from nuskey8 and akeit0, 862 stars), MIT and fully managed, but still 0.x with C# API changes between releases and some open correctness issues.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README chart (docs/Benchmark.png) shows 8.05 ms vs NLua 36.45 ms and MoonSharp 19.87 ms; the benchmark code is public (sandbox/Benchmark/AddBenchmark.cs with add.lua, BenchmarkDotNet 0.14.0, net8.0, MoonSharp 2.0.0, NLua 1.7.3) but CPU, runtime build and which variant (DoString or DoFile) the chart plots are not stated, so first-party C.
- **Verifier notes:** Chart numbers match the record exactly (about 4.5x vs NLua and 2.5x vs MoonSharp, derived from page data; 31.3 KB vs 12,306.5 KB and 13,887 KB allocated). Benchmark code exists in sandbox/Benchmark, correcting the record's claim that it is absent. Main shortcoming: interop-call microbenchmark only, no hardware, chart variant unstated.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/nuskey8/Lua-CSharp>
  - <https://github.com/nuskey8/Lua-CSharp/commits>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/README.md>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/docs/Benchmark.png>
  - <https://github.com/nuskey8/Lua-CSharp/tree/main/sandbox>
  - <https://github.com/nuskey8/Lua-CSharp/tree/main/tests>
  - <https://github.com/nuskey8/Lua-CSharp/tree/main/sandbox/Benchmark>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/sandbox/Benchmark/AddBenchmark.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/sandbox/Benchmark/add.lua>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/sandbox/Benchmark/Benchmark.csproj>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/sandbox/Benchmark/BenchmarkCore.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/sandbox/Benchmark/Program.cs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/README.md>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/docs/Benchmark.png>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/sandbox/Benchmark/AddBenchmark.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/sandbox/Benchmark/add.lua>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/sandbox/Benchmark/Benchmark.csproj>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/sandbox/Benchmark/BenchmarkCore.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/sandbox/Benchmark/Program.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/sandbox/Benchmark/NBodyBenchmark.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/782fadf/sandbox/Benchmark/AddBenchmark.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/782fadf/sandbox/Benchmark/add.lua>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/782fadf/sandbox/Benchmark/Program.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/782fadf/sandbox/Benchmark/Benchmark.csproj>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/782fadf/sandbox/Benchmark/BenchmarkCore.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/src/Lua/Lua.csproj>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/src/Lua/LuaValue.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/src/Lua/LuaFunction.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/src/Lua/LuaState.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/src/Lua/Runtime/LuaVirtualMachine.cs>
  - <https://raw.githubusercontent.com/nuskey8/Lua-CSharp/HEAD/src/Lua/Runtime/OpCode.cs>
  - <https://github.com/nuskey8/Lua-CSharp/tree/main/src/Lua>
  - <https://github.com/nuskey8/Lua-CSharp/tree/main/src/Lua/Runtime>
  - <https://github.com/nuskey8/Lua-CSharp/commits>
  - <https://github.com/nuskey8/Lua-CSharp/commits/main/docs/Benchmark.png>
  - <https://github.com/nuskey8/Lua-CSharp/commits/main/sandbox/Benchmark/AddBenchmark.cs>
  - <https://github.com/nuskey8/Lua-CSharp/commits/main/sandbox/Benchmark/add.lua>
  - <https://github.com/nuskey8/Lua-CSharp/issues?q=is%3Aissue>
  - <https://github.com/nuskey8/Lua-CSharp/issues/156>
  - <https://github.com/nuskey8/Lua-CSharp/issues/272>
  - <https://github.com/nuskey8/Lua-CSharp/issues/338>
  - <https://github.com/nuskey8/Lua-CSharp/issues/344>
  - <https://api.nuget.org/v3/registration5-semver1/luacsharp/index.json>
  - <https://raw.githubusercontent.com/NLua/NLua/HEAD/README.md>
  - <https://raw.githubusercontent.com/moonsharp-devs/moonsharp/HEAD/src/MoonSharp.Interpreter/DataTypes/DynValue.cs>
  - <https://raw.githubusercontent.com/dotnet/BenchmarkDotNet/HEAD/docs/articles/features/setup-and-cleanup.md>
  - <https://raw.githubusercontent.com/dotnet/BenchmarkDotNet/HEAD/docs/articles/samples/IntroSetupCleanupIteration.md>
  - <https://raw.githubusercontent.com/dotnet/BenchmarkDotNet/HEAD/src/BenchmarkDotNet.Annotations/Attributes/IterationSetupAttribute.cs>
  - WebSearch: Lua-CSharp nuskey8 benchmark MoonSharp NLua performance comparison
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/nuskey8/lua-csharp`) · [data/wave12/enrich/raw/github_com_nuskey8_lua_csharp.json](../../../data/wave12/enrich/raw/github_com_nuskey8_lua_csharp.json) (enrichment confidence 0.75)

</details>
