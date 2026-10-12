# Luau

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Roblox's sandboxed, gradually typed Lua 5.1 derivative whose interpreter runs about 1.2-1.5x PUC Lua 5.5 in independent tests.

| | |
|---|---|
| **Beats** | PUC Lua 5.x interpreter (Lua 5.1 to 5.4) |
| **Claimed result** | borisbat/dasProfile (Luau 0.736 -O2 vs Lua 5.5.1, Clang 19): Luau faster on 12 of 16 kernels, geomean 1.51x on a Ryzen 7 PRO 8700GE and 1.56x on an M1 Max (derived from page data); about 1.4x without the sha256 kernel and about 1.25x without float2string as well (see caveats). Loses integer loops: primes 0.151 s vs 0.059 s. Luau's own performance guide gives ratios only (table.sort about 4x, table insert/remove/move 3x, paged GC sweeper 2-3x). |
| **Workload** | Interpreter dispatch loop, table library, string library and garbage collector sweep, as described in the project's performance guide. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 PRO 8700GE and Apple M1 Max (dasProfile); AWFY run by rochus-keller on an i5-8350U |
| **Compiler and flags** | dasProfile: Clang 19, Luau built -O2, Lua 5.5.1 built with its upstream Makefile; rochus-keller AWFY: GCC 12.2.0 (the Luau guide tunes the interpreter for Clang and MSVC) |
| **Adoption** | 5.9k stars; scripting layer of Roblox, also adopted in commercial games per README |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/luau-lang/luau) · [benchmark](https://github.com/borisbat/dasProfile) |

## Verdict

The project's performance guide gives ratios without numbers, workloads or hardware: interpreter 'noticeably faster than Lua 5.x', table.sort about 4x, table insert/remove/move 3x and more than un-tuned versions, paged GC sweep 2-3x faster than Lua/LuaJIT, table length 50+% faster. Independent data: dasProfile (daslang author, September 2026, Luau 0.736 -O2 vs Lua 5.5.1 built with Clang 19.1.7 Release on a Ryzen 7 PRO 8700GE, and AppleClang on an Apple M1 Max) puts Luau ahead of Lua on 12 of 16 kernels with geomeans of about 1.51x (Linux) and 1.56x (macOS), derived from page data, and Are-we-fast-yet (i5-8350U, GCC 12.2.0) puts the Luau interpreter level with LuaJIT -joff (geomean factor 2.39 vs 2.32 relative to LuaJIT with JIT).

## Use it when

- Embedding a scripting layer in a game or app where JIT is not allowed (consoles, iOS) and you want the fastest portable interpreter in the Lua family without hand-written assembly.
- Running untrusted or user-authored scripts: the project's SECURITY.md promises that no source code can cause memory-safety errors and treats violations as vulnerabilities (bounty via HackerOne), and the sandbox (luaL_sandbox, luaL_sandboxthread) is also what enables the fast paths.
- Code dominated by table access, method calls, builtin math/bit32 calls, string formatting and float-to-string conversion: independent dasProfile runs show Luau 0.736 1.7-2.1x PUC Lua 5.5.1 on dictionary, spectral norm, mandelbrot and exp loop, and about 7x on float2string.
- Teams that want static type checking and editor tooling (luau-analyze, luau-lsp) on top of a Lua-like language, with optional AOT native code for hot modules on x64/arm64.
- Frame-based hosts that need low GC pauses: incremental GC with per-frame lua_gc requests, incremental coroutine marking and shrinkable weak tables.

## Skip it when

- Integer-heavy loops: Luau has only double-precision numbers (no 64-bit integer subtype, no bitwise operators), and in dasProfile it lost to PUC Lua 5.5.1 on primes loop (0.151 s vs 0.059 s on Linux), fibonacci loop, fibonacci recursive and queen.
- Existing Lua 5.2-5.4 code bases that use goto, _ENV, integer semantics, __gc finalizers, io/os file access or debug hooks: none are supported, so this is not a drop-in replacement for modern Lua.
- When LuaJIT's trace JIT is available and allowed: the Are-we-fast-yet run (i5-8350U) puts LuaJIT 2.1 with JIT about 2.4x ahead of the Luau interpreter and 1.6x ahead of Luau with --codegen.
- Scripts that rely on loadstring, getfenv or setfenv: any use marks the environment impure and disables imports, fastcalls and inlining for that environment.
- Hosts built without C++ exception support or that must stay plain C: the VM is C++ (C++11 runtime, C++17 compiler) and raises Lua errors as C++ exceptions unless rebuilt with LUA_USE_LONGJMP=1.

## How it is fast

A portable C++ bytecode interpreter with computed-goto dispatch on GCC/Clang (switch on MSVC) and a bytecode format partly modelled on LuaJIT's, with a multi-pass AST compiler that does constant folding, upvalue capture by value, and, at -O2, function inlining and loop unrolling. Inline caching of table field lookups and method calls (namecall), 'imports' that resolve global chains like math.max at load time, and 'fastcall' builtins invoked from the dispatch loop without a call frame all depend on the sandboxed, immutable global environment. Runtime side: cached table length with branch-free binary search, introsort-based table.sort, a size-class pool allocator, a PID-controlled GC pacer and a paged sweeper that walks 16 KB pages instead of Lua's linked object list.

## Compared with alternatives

Pick Luau over LuaJIT Remake (Deegen) when you need a sandboxed, production-maintained runtime that builds anywhere with a C++ compiler; LuaJIT Remake reports an interpreter 34.6% faster than LuaJIT's, which Are-we-fast-yet puts about level with Luau. Pick Daslang when you can adopt a statically typed non-Lua language (its interpreter beat Luau on all 16 dasProfile kernels on both platforms), and Pallene or Ravi when you want to stay on Lua 5.3/5.4 semantics with compiled typed code.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake targets Luau.VM and Luau.Compiler, optional Luau.CodeGen; LUAU_BUILD_SHARED for a shared library) or source-drop |
| **Dependencies** | none beyond the C++ standard library (doctest for tests, isocline for the REPL) |
| **Minimum toolchain** | C++11 for the VM, C++17 for compiler, analysis and codegen; MSVC 2017+, gcc-7+, clang-7+ per README; interpreter tuned for Clang and recent MSVC |
| **Platforms** | Any platform with a supported C++ compiler for the interpreter; native code generation only on x64 and arm64 (CodeGen::isSupported()) |
| **Thread safety** | Not documented in the pages read beyond the Lua 5.1 model (one lua_State tree per thread); CodeGen.h says a SharedCodeGenContext can be used by multiple Luau VMs concurrently |
| **Drop-in for the baseline** | partial: the Lua 5.1 C API and language are mostly preserved, but compilation is a separate step, __gc and hooks are gone, and Lua 5.2-5.4 features (integers, goto, _ENV, bitwise operators) are missing |

## Gotchas

- Most advertised speedups require calling luaL_sandbox on the global state and luaL_sandboxthread per script; without the sandboxed pure environment, imports and fastcall builtins stay off.
- The VM accepts only bytecode produced by the Luau compiler and gives no safety guarantee for anything else (SECURITY.md); sign or encrypt bytecode that crosses a trust boundary. There are no termination guarantees, so use interrupt callbacks for CPU limits.
- Harness flaw in the independent dasProfile comparison: its PUC Lua 5.5.1 sha256 kernel emulates bit32 through loaded closures wrapped in variadic select() helpers while the Luau kernel calls bit32 builtins directly, so the 5.5-5.7x sha256 ratio mostly measures different code; float2string also prints different strings (Luau shortest round-trip vs Lua %.14g). Excluding sha256 the geomean Luau advantage drops from about 1.5x to about 1.4x, and excluding float2string as well to about 1.25x (derived from page data).
- The Are-we-fast-yet numbers were built with GCC 12.2.0 via make config=release, while the performance guide says the interpreter is tuned for Clang and MSVC, so GCC builds may understate Luau; closure caching also changes function identity, which can break code that uses closures as table keys.

## Known shortcomings

- Ratios only: the interpreter-versus-Lua 5.4 claim has no number on any opened page (luau.org blocked). The independent rochus-keller Are-we-fast-yet Results.pdf (i5-8350U, GCC 12.2.0) puts the Luau interpreter level with LuaJIT -joff (geomean 2.39 vs 2.32) but has no PUC Lua column.
- Enricher: independent dasProfile numbers (Luau 0.736 -O2 vs Lua 5.5.1, Clang 19, Ryzen 7 PRO 8700GE and M1 Max) have Luau faster on 12 of 16 kernels, geomean 1.51x and 1.56x (derived), but the Lua sha256 kernel fakes bit32 with loaded closures inside variadic select() wrappers while Luau calls bit32 builtins directly, so the 5.5x sha256 gap is mostly different code (geomean about 1.4x without it, about 1.25x without float2string as well); Luau loses integer loops (primes 0.151 s vs 0.059 s) since it has no integers. The AWFY run was built with GCC 12 although the guide tunes the interpreter for Clang and MSVC.

## Caveats and trade-offs

First-party documentation page with ratios but no workload list, hardware, compiler flags or raw numbers, so tier C. The interpreter claim ('noticeably faster than Lua 5.x ... Lua 5.4 ... doesn't come close') has no number; the \~4x table.sort figure names no baseline; table insert/remove/move 3x is 'compared to un-tuned versions'; the 50+% table length gain is versus the default binary search computed from scratch. The repo has bench/ (bench.py with --compare for other VMs, micro_tests, gc) but no checked-in result tables. Several gains (fastcall builtins, imports) require the sandboxed pure global environment and are deoptimized by loadstring/getfenv/setfenv. Independent data point against a different baseline: rochus-keller/Are-we-fast-yet Luau/Results.pdf (14 Are-we-fast-yet benchmarks, i5-8350U, GCC 12.2.0, Luau commit 5836a9c, make config=release, 2025-10-25) gives geomean factors relative to LuaJIT 2.1 JIT of 2.39 for Luau default, 2.31 for -g0 -O2, 1.64 for -O2 --codegen, versus 2.32 for LuaJIT -joff; that is, the Luau interpreter is roughly at LuaJIT interpreter speed (about 3% slower), with no PUC Lua 5.x column. [retier] dasProfile is run by the Daslang lead (independent of Luau). Its Lua sha256 kernel fakes bit32 with loaded closures inside variadic select() wrappers while Luau calls bit32 builtins directly, so the 5.5x sha256 gap is mostly different code; float2string prints different strings. Luau has no integer type and loses integer loops. The rochus-keller Are-we-fast-yet Results.pdf (i5-8350U, GCC 12.2.0) puts the Luau interpreter level with LuaJIT -joff (geomean 2.39 vs 2.32) with no PUC Lua column. luau.org blocked here.

Derived from Lua 5.1 with its own type annotations and a sandboxing model (safeenv via luaL_sandbox) that the fastest paths rely on; API mostly Lua 5.1 compatible with caveats; interpreter-first design, JIT/native codegen is optional and not available everywhere.

## Maintenance

Very active (release 741 synced and commits on 2026-10-02), MIT-licensed, backed by Roblox and used in shipped games (Alan Wake 2, Warframe); the VM plus compiler is a moderate C++ dependency that builds with CMake or make on all major platforms.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now B.
- **Tier reason:** First-party performance guide gives ratios only (table.sort \~4x, table insert/remove/move 3x and more vs un-tuned versions, paged sweeper 2-3x vs Lua/LuaJIT linked-list sweep, table length 50+%) with no workloads, hardware, compiler flags or raw numbers; the interpreter-vs-Lua 5.x claim has no number at all. bench/bench.py can compare VMs but no results are checked in. An independent Are-we-fast-yet run exists but compares against LuaJIT, not PUC Lua, so it does not lift the tier.
- **Retiered** C to B: C to B: the enricher found independent numbers in borisbat/dasProfile (Luau 0.736 -O2 vs Lua 5.5.1, Clang 19, Ryzen 7 PRO 8700GE and M1 Max) replacing the first-party ratios; a harness flaw in the sha256 kernel means the fair geomean is about 1.25-1.4x rather than 1.5x.
- **Verifier notes:** Record matches the performance guide; tier C stands. Ratio claims are first-party and loosely baselined; the core interpreter-vs-Lua 5.4 claim has no number. The independent Are-we-fast-yet Results.pdf (i5-8350U, GCC 12.2.0) shows Luau's interpreter about level with LuaJIT 2.1 -joff (geomean 2.39 vs 2.32), useful for the enricher, but it has no PUC Lua column.
- **Fields the verifier corrected:** `caveats`, `benchmark_url`, `claimed_speedup`, `hardware`, `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/luau-lang/site/master/src/content/docs/guides/performance.md>
  - <https://github.com/luau-lang/luau>
  - <https://github.com/luau-lang/luau/commits>
  - <https://github.com/luau-lang/luau/tree/master/bench>
  - <https://raw.githubusercontent.com/luau-lang/luau/HEAD/bench/bench.py>
  - <https://github.com/rochus-keller/Are-we-fast-yet>
  - <https://raw.githubusercontent.com/rochus-keller/Are-we-fast-yet/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/rochus-keller/Are-we-fast-yet/HEAD/Luau/Readme.md>
  - <https://raw.githubusercontent.com/rochus-keller/Are-we-fast-yet/HEAD/Luau/Results.pdf>
  - <https://raw.githubusercontent.com/rochus-keller/Are-we-fast-yet/HEAD/Lua/Readme.md>
  - <https://github.com/rochus-keller/Are-we-fast-yet/tree/main/Lua>
- **Sources the enricher read:**
  - <https://github.com/luau-lang/luau>
  - <https://github.com/luau-lang/luau/commits/master>
  - <https://github.com/luau-lang/luau/tree/master/bench>
  - <https://github.com/luau-lang/luau/issues?q=is%3Aissue+label%3Aperformance>
  - <https://github.com/luau-lang/luau/issues?q=is%3Aissue+slower+than+lua>
  - <https://raw.githubusercontent.com/luau-lang/luau/HEAD/README.md>
  - <https://raw.githubusercontent.com/luau-lang/luau/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/luau-lang/luau/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/luau-lang/luau/HEAD/Makefile>
  - <https://raw.githubusercontent.com/luau-lang/luau/HEAD/bench/bench.py>
  - <https://raw.githubusercontent.com/luau-lang/luau/HEAD/bench/bench_support.lua>
  - <https://raw.githubusercontent.com/luau-lang/luau/HEAD/VM/src/lvmexecute.cpp>
  - <https://raw.githubusercontent.com/luau-lang/luau/HEAD/VM/include/luaconf.h>
  - <https://raw.githubusercontent.com/luau-lang/luau/HEAD/CodeGen/include/Luau/CodeGen.h>
  - <https://raw.githubusercontent.com/luau-lang/site/master/src/content/docs/guides/performance.md>
  - <https://raw.githubusercontent.com/luau-lang/site/master/src/content/docs/getting-started/compatibility.md>
  - <https://raw.githubusercontent.com/rochus-keller/Are-we-fast-yet/HEAD/Luau/Readme.md>
  - <https://raw.githubusercontent.com/rochus-keller/Are-we-fast-yet/HEAD/Luau/Results.pdf>
  - <https://github.com/borisbat/dasProfile>
  - <https://github.com/borisbat/dasProfile/tree/main/tests/luau>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/README.md>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/config.das>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/lua/sha256.lua>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/luau/sha256.luau>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/lua/primes.lua>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/luau/primes.luau>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/lua/f2s.lua>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/luau/f2s.luau>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/luau-lang/luau`) · [data/wave12/enrich/raw/github_com_luau_lang_luau.json](../../../data/wave12/enrich/raw/github_com_luau_lang_luau.json) (enrichment confidence 0.8)

</details>
