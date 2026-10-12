# Daslang (daScript)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Statically typed game scripting language with tree interpreter, C++ AOT and LLVM JIT; interpreter outpaces Lua 5.5 and QuickJS.

| | |
|---|---|
| **Beats** | Lua 5.5.1 and QuickJS 2026-06-04 (the same table also has LuaJIT 2.1 with -joff, Luau 0.736, Quirrel 4.29.1, Mono --interpreter) |
| **Claimed result** | borisbat/dasProfile (Linux, Ryzen 7 PRO 8700GE, Clang 19): the DAS interpreter beats Lua 5.5.1 and QuickJS on all 16 kernels, but the largest gaps (sha256 27x, mandelbrot 32x, particles 41x over Lua) come from Lua kernels written differently (bit operations through vararg select() wrappers, metatable Complex tables, 11 passes vs 10); the like-for-like recursive fib is parity (0.048174 vs 0.048747 s), and the independent sashi0034/script-language-benchmark suite puts the DAS advantage over Lua at about 2.5x (derived from page data). QuickJS: sha256 0.002510 vs 0.021312 s, mandelbrot 0.001791 vs 0.006346 s, sort 0.015450 vs 0.037570 s. |
| **Workload** | 16 kernels (sha256, dictionary, n-bodies, spectral norm, mandelbrot, exp loop, string2float, particles kinematics, queen, interop host calls, primes loop, tree, sort, fibonacci loop, float2string, fibonacci recursive); each cell is the median of five samples, each sample runs the kernel as often as fits a 0.5 s budget; interpreter lane compared with the Lua and QuickJS interpreters |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 PRO 8700GE w/ Radeon 780M Graphics (Linux) and Apple M1 Max (macOS) |
| **Compiler and flags** | Clang 19.1.7 on Linux, AppleClang 21.0.0.21000101 on macOS; daslang 0.6.4 SDK (consumed through find_package(DAS), built separately from the daScript repo), LLVM 22.1.5. dasProfile's CMakeLists.txt forces CMAKE_BUILD_TYPE Release (CMake default -O3 -DNDEBUG on Clang; the '-O3' comment in the file refers to the C++ lane). Lua 5.5.1 is compiled from the SHA256-pinned lua.org tarball inside the same Release project (linit.c patched to add a profile_native module); QuickJS 2026-06-04 is built from the pinned bellard.org tarball with its upstream Makefile (hosts/quickjs_host.mk includes it), so QuickJS uses its own default flags. |
| **Adoption** | 1.2k stars (GaijinEntertainment/daScript); 0 stars on the benchmark repo borisbat/dasProfile |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/GaijinEntertainment/daScript) · [benchmark](https://github.com/borisbat/dasProfile) |

## Verdict

borisbat/dasProfile, written by the daslang lead developer, times 16 kernels; each cell is the median of five processes, each running the kernel for a 0.5 s budget. On Linux (Ryzen 7 PRO 8700GE, Clang 19.1.7, daslang 0.6.4) the DAS interpreter beats Lua 5.5.1 and QuickJS 2026-06-04 on every kernel, from parity on fibonacci recursive (0.048174 s vs 0.048747 s vs 0.088087 s) to 27x and 8.5x on sha256 (0.002510 s vs 0.068548 s vs 0.021312 s), and the M1 Max table shows the same pattern. The largest gaps come from Lua kernels written with vararg bit-op wrappers or table-allocating complex numbers; an independent Windows suite (sashi0034, unreviewed Codex-generated code, CPU and units not stated) puts Daslang 1.4x to 3.4x ahead of Lua on 13 of 16 workloads.

## Use it when

- A C++ game engine or ECS that calls scripts every frame, where Lua or Squirrel marshaling costs too much: 1M host calls took 0.003740 s in the DAS interpreter vs 0.015360 s in Lua 5.5.1 on Linux.
- Targets that forbid JIT (consoles, iOS): use the interpreter during development and AOT-to-C++ for shipping, with hybrid mode falling back to the interpreter for functions whose semantic hash changed.
- Numeric and vector-heavy gameplay code (particles, n-body, spectral norm) that benefits from static types and SIMD value types.
- Teams that want static types, hot reload (the docs cite about 5 s to recompile a full production game) and a compile-time macro system.
- Desktop or server hosts that can ship LLVM, where the JIT tier gets near-C++ speed from script code.

## Skip it when

- Existing Lua or JavaScript code, or modders who expect those languages: Daslang is not source-compatible with either.
- Short-lived or startup-sensitive scripts: hello world takes 0.0187 s (macOS) and 0.0261 s (Linux) in the interpreter, and 0.089 to 0.113 s under JIT, against about 0.0024 to 0.0039 s for Lua and QuickJS.
- Running untrusted scripts: the language is '99% safe, not 100%', with unsafe blocks and raw pointers, and open issues include a deep recursion that kills the interpreter with SIGSEGV (#4110) and fuzzer crashes (#4101).
- Small-footprint embedding: it is a large C++17 code base (23,104 commits) with submodules, and the JIT needs LLVM; the 'nano' runtime is smaller but drops the GC, string builders, the math module and threads.
- Recursion- or allocation-heavy code where other interpreters are faster: on Linux LuaJIT -joff beat it on tree (0.018248 vs 0.023617 s) and fibonacci recursive (0.034842 vs 0.048174 s), and Mono --interpreter won tree on both platforms.

## How it is fast

Static typing lets the compiler build unboxed, type-specialised evaluation nodes, and the interpreter walks that tree of specialised simulation nodes (SimNode_\*) directly instead of decoding bytecode with run-time type checks. Vector types such as float2 and float3 are built-in value types (the particles kernel uses a vec3_ldu hint), so vector math needs no heap objects, and host calls cost little because no data is converted. The AOT and LLVM JIT tiers reach C++ speed on the same suite (Linux fibonacci recursive: DAS JIT 0.002811 s, C++ 0.002811 s).

## Compared with alternatives

Pick Daslang over Luau, Ravi or Pallene when a C++ engine calls scripts every frame and you can adopt a new statically typed language: it avoids marshaling and has an AOT path for JIT-less consoles. Pick Luau when you need Lua compatibility and sandboxing, QuickJS when you need JavaScript, and LuaJIT Remake only for research into interpreter generation.

## Integration

| | |
|---|---|
| **Form** | static lib (libDaScript) or shared lib (libDaScriptDyn) via CMake find_package(DAS); AOT output is C++ source compiled into the host |
| **Dependencies** | git submodules (README build step); an LLVM shared library only for the JIT tier, which is off by default (CMake option DAS_LLVM_DISABLED defaults to ON); optional modules (dasHV, GLFW, ImGui, Vulkan, Metal) are switched by CMake options |
| **Minimum toolchain** | C++17 and CMake 3.17+; the benchmark used Clang 19.1.7 (Linux) and AppleClang 21 (macOS); MSVC is supported |
| **Platforms** | Windows, Linux and macOS (x86-64 and Apple M1 in the benchmark), WebAssembly through an Emscripten build, and consoles/iOS through AOT per the design notes |
| **Thread safety** | One Context per script instance holds its own globals, stack and heap; the integration notes say several standalone instances can be created and driven on any thread. Sharing one Context across threads is not documented as safe (the benchmark runner sets threadlock_context). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the largest ratio: dasProfile's Lua sha256 sends every AND and XOR through vararg wrappers (select('#', ...) loops over closures built with load()) although Lua 5.5 has native bitwise operators, and assembles words with string.byte. The DAS kernel uses inline operators with unsafe_deref and unsafe_range_check hints and loads 32-bit words straight from memory without a byte swap; it matches the reference hash only because the 1024-byte input is all '.'. The 27x over Lua on sha256 therefore mostly measures the Lua kernel's style; the independent sashi0034 suite shows Daslang about 2.5x faster than Lua on sha256 (224.411 vs 549.956).
- Mandelbrot and particles are not like-for-like either. The Lua mandelbrot (Ligneul 2017) uses metatable Complex objects that allocate several tables per iteration, and its repeat-until loop counts iterations differently, while DAS uses float2 values and QuickJS uses plain doubles. The Lua particles kernel runs 'for i = 0, count' (11 passes against DAS's 10) on nested pos/vel tables, while DAS uses SIMD float3. The 32x and 41x gaps on the Linux table shrink to about 2.4x and 2.6x in sashi0034's suite.
- On like-for-like kernels the margin is small: on Linux fibonacci recursive the DAS interpreter took 0.048174 s and Lua 0.048747 s (parity; 1.55x on macOS). The clear structural win is interop host calls (about 4.1x Lua on Linux). In sashi0034's Windows suite, Lua wins sort (6.175 vs 237.142) and string2float (68.624 vs 107.174).
- Open stability issues: deep recursion kills the interpreter with SIGSEGV (#4110), heap_collect frees strings that are still live (#3734), a stale .shared_module ABI mismatch crashes with SIGSEGV (#3466), and fuzzer crashes remain (#4101). The README still says the JIT needs LLVM 16.0.6 at lib/LLVM.dll, while the benchmark used LLVM 22.1.5.

## Known shortcomings

- borisbat/dasProfile is a first-party suite by the Daslang lead with no licence, DAS SDK flags are not in the bench repo, LuaJIT -joff and Mono --interpreter win some kernels, and the dictionary cell varies by about 25%; the -O3 comment refers to the C++ lane while QuickJS was built with its own upstream Makefile.
- Enricher: the dasProfile Lua kernels are not like for like (Lua sha256 routes every bit operation through vararg select() wrappers despite Lua 5.5's native operators, the DAS sha256 loads raw words without byteswap and is right only because the input is all '.', the Lua mandelbrot allocates metatable Complex tables, Lua particles does 11 passes against DAS's 10), so the 27x/32x/41x headline gaps over Lua shrink to about 2.5x in the independent sashi0034 suite and the like-for-like recursive fib is parity on Linux (0.048174 vs 0.048747 s). Open crash issues #4110, #3734, #4101.

## Caveats and trade-offs

The benchmark repo is written and maintained by the daslang lead developer (borisbat also merges on the daScript repo), so this is a first-party suite although it is fully public and reproducible; dasProfile shows no licence (no LICENSE file; the language repo is BSD-3-Clause). The daslang SDK's own build flags are set by the daScript repo, not stated in dasProfile. LuaJIT -joff beats the DAS interpreter on 'tree' and 'fibonacci recursive' on Linux, Mono --interpreter beats it on 'tree' on both platforms, and Lua is within about 1% on Linux fibonacci recursive (0.048174s vs 0.048747s); the Linux DAS dictionary cell has ±25% spread. A separate third-party suite (sashi0034/script-language-benchmark, Windows, Visual Studio 17 2022, code generated with Codex and flagged by its author as unreviewed, CPU not stated) reports Daslang fastest on 13 of 16 workloads against Lua and AngelScript (fibonacci_recursive 266.421 vs Lua 599.702) but Lua wins sort (6.175 vs 237.142 ms) and string2float (68.624 vs 107.174 ms); the two suites use different kernel code, so the sort result is not directly comparable with the dasProfile row where DAS wins. [retier] dasProfile is a first-party suite by the Daslang lead with no licence; DAS SDK flags are not in the bench repo, LuaJIT -joff and Mono --interpreter win some kernels, the dictionary cell varies by about 25%, and the Lua kernels are not like for like (the DAS sha256 also loads raw words without byteswap and is right only because the input is all '.'). Open crash issues #4110, #3734, #4101.

Statically typed language with its own syntax (not drop-in for Lua or JavaScript code); zero-copy C++ interop by design; three execution tiers (interpreter, AOT to C++, LLVM JIT); interpreter startup is slower than Lua/QuickJS (hello world 0.0187s macOS / 0.0261s Linux vs about 0.0024-0.0039s for Lua and QuickJS).

## Maintenance

Actively developed (last commit 2026-10-06, 23,104 commits) under BSD-3-Clause and built for Gaijin's ECS game engine per its design notes; a large and fast-moving code base with open crash issues, so pin a release such as 0.6.4.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** borisbat/dasProfile README tables compare the DAS interpreter with Lua 5.5.1 and QuickJS 2026-06-04 on 16 kernels; benchmark code is public (main.das, tests/, hosts/, CMakeLists.txt pinning Lua and QuickJS tarballs by SHA256), toolchain (Clang 19.1.7 / AppleClang 21), Release build type and CPU models (Ryzen 7 PRO 8700GE, Apple M1 Max) are stated. Every quoted number matches the Linux and macOS interpreted tables.
- **Verifier notes:** Numbers, ratios (27.3x vs Lua and 8.5x vs QuickJS on Linux sha256, derived from page data) and the 'all 16 kernels vs Lua and QuickJS' claim check out on the Linux table. Shortcoming: first-party suite by the daslang developer, no licence on dasProfile, DAS SDK flags not in the benchmark repo; LuaJIT -joff and Mono --interpreter beat the DAS interpreter on some kernels.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/borisbat/dasProfile>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/README.md>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/hosts/quickjs_host.mk>
  - <https://github.com/GaijinEntertainment/daScript>
  - <https://github.com/GaijinEntertainment/daScript/commits>
  - <https://raw.githubusercontent.com/GaijinEntertainment/daScript/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/sashi0034/script-language-benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/GaijinEntertainment/daScript>
  - <https://github.com/GaijinEntertainment/daScript/commits/master>
  - <https://github.com/GaijinEntertainment/daScript/issues?q=is%3Aissue+is%3Aopen+crash+OR+interpreter+OR+thread>
  - <https://github.com/GaijinEntertainment/daScript/tree/master/skills>
  - <https://raw.githubusercontent.com/GaijinEntertainment/daScript/HEAD/README.md>
  - <https://raw.githubusercontent.com/GaijinEntertainment/daScript/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/GaijinEntertainment/daScript/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GaijinEntertainment/daScript/HEAD/doc/source/reference/design_philosophy.rst>
  - <https://raw.githubusercontent.com/GaijinEntertainment/daScript/HEAD/skills/design_philosophy.md>
  - <https://raw.githubusercontent.com/GaijinEntertainment/daScript/HEAD/skills/cpp_integration.md>
  - <https://raw.githubusercontent.com/GaijinEntertainment/daScript/HEAD/skills/project_overview.md>
  - <https://github.com/borisbat/dasProfile>
  - <https://github.com/borisbat/dasProfile/tree/master/tests>
  - <https://github.com/borisbat/dasProfile/tree/main/tests/lua>
  - <https://github.com/borisbat/dasProfile/tree/main/tests/js>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/README.md>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/main.das>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/config.das>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/hosts/quickjs_host.mk>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/sha256.das>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/lua/sha256.lua>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/js/sha256.js>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/particles.das>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/lua/particles.lua>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/js/particles.js>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/mandelbrot.das>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/lua/mandelbrot.lua>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/js/mandelbrot.js>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/fib_recursive.das>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/lua/fib_recursive.lua>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/native.das>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/lua/native.lua>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/table-sort.das>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/lua/table-sort.lua>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/tests/lua/profile.lua>
  - <https://raw.githubusercontent.com/sashi0034/script-language-benchmark/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/gaijinentertainment/dascript`) · [data/wave12/enrich/raw/github_com_gaijinentertainment_dascript.json](../../../data/wave12/enrich/raw/github_com_gaijinentertainment_dascript.json) (enrichment confidence 0.8)

</details>
