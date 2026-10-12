# Terra

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Statically typed, LLVM-JIT-compiled low-level language embedded in LuaJIT; typed fib(34) runs 11x faster than PUC Lua.

| | |
|---|---|
| **Beats** | Lua (PUC) |
| **Claimed result** | terra 0.121 s vs Lua 1.341 s (page shows 'x11.0' relative Lua speed; about 11x derived from page data). |
| **Workload** | Scriptorium: recursive Fibonacci fib(34), whole-process wall time per run (bench.cc times system() calls, averaged over 5 runs, table keeps the best run), seconds, lower is better; 50 scripting-language implementations. |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz, 8 GiB, Windows 7 64bit |
| **Compiler and flags** | Compiled on VS2015 RC if possible, VS2013 elsewhere (per page); Terra build flags and version not stated (run.bat runs terra\terra tests\fib.t). |
| **Adoption** | 2.9k stars |
| **Last commit** | 2026-08-19 |
| **Links** | [repository](https://github.com/terralang/terra) · [benchmark](https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md) |

## Verdict

In r-lyeh's Scriptorium (July 2015; AMD A10 3.8 GHz, Windows 7 64-bit; build flags and Terra version not stated, linked as zdevito/terra), recursive fib(34) took 0.121 s for Terra against 1.341 s for the PUC Lua interpreter: 11x as whole-process wall time, best of repeated 5-run averages. LuaJIT (0.111 s) and MSVC C (0.074 s) were faster on the same page.

## Use it when

- You script in Lua and need a few hot kernels (numeric loops, image or stencil code, DSL backends) at native-C speed without writing a separate C extension.
- You need runtime code generation or specialization (autotuners, staged DSLs, generated SIMD kernels) and want LLVM-quality code from a high-level meta-language.
- Your host is already LuaJIT-based (Lua 5.1 semantics) and you can ship LLVM in the process or in the build.
- Ahead-of-time output is acceptable: Terra can emit `.o` files or executables, which avoids JIT start-up and LLVM at run time.
- You need GPU code from the same source: CUDA, with AMD/HIP and experimental Intel SPIR-V on recent LLVM versions.

## Skip it when

- As a faster runtime for existing dynamically typed Lua scripts: untyped Lua code just runs on LuaJIT, so plain LuaJIT (0.111 s vs Terra 0.121 s on the same fib page) gives the same gain without LLVM.
- PUC Lua 5.3/5.4 hosts: terra.h includes the bundled LuaJIT's lua.h and terra_init expects a LuaJIT state, so Terra cannot be added to a stock Lua 5.4 embedding.
- Small footprint, sandboxed or JIT-forbidden targets (iOS, consoles, hostile scripts): Terra needs LLVM and Clang (11-22; 15 and older deprecated), generates native code, and gives no memory safety (manual memory and raw pointers).
- Windows-centric projects: issue #668 says Terra is looking for Windows maintainers, and the static-library-with-LLVM bundling options are not supported on Windows.
- Short scripts where start-up matters: the 0.121 s whole-process figure includes LLVM initialization and JIT compilation, about 0.05 s above MSVC-compiled C (0.074 s) for the same fib.

## How it is fast

Terra functions are statically typed and lowered to LLVM IR, then optimized and JIT-compiled to native code for the host CPU (since 1.2.1 host detection enables all host CPU features, similar to -march=native). This is multi-stage programming: Lua acts as the meta-language that generates specialized code, for example inlining Lua constants as literals and using quotes, escapes and macros. C headers are imported through Clang, so calls into C have no FFI overhead and can be inlined. The surrounding Lua runs on LuaJIT, which is itself 12x PUC Lua on the same benchmark page.

## Compared with alternatives

Pick Terra over Daslang, Chibi-Scheme, Pawn, TinyVM or c4x86 when you want native LLVM-optimized code generated from Lua meta-programs and can afford an LLVM dependency. For faster ordinary game scripting without LLVM, Daslang or LuaJIT-family engines such as LuaJIT Remake are lighter. On this exact page, c4x86 (0.136 s) is close to Terra with no LLVM at all.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | LLVM and Clang 11-22 (22 recommended, 11-15 deprecated), LuaJIT (downloaded and built automatically), CMake 3.26.4+, GNU Make on Unix; optional CUDA |
| **Minimum toolchain** | C++17 compiler; Visual Studio 2022 on Windows; CMake 3.26.4 |
| **Platforms** | Linux x86-64, AArch64, PPC64le; macOS x86-64 and AArch64; FreeBSD x86-64; Windows x86-64; GPU targets NVIDIA CUDA, AMD HIP, Intel SPIR-V (experimental) |
| **Thread safety** | not documented in the README; each embedding owns a LuaJIT lua_State, which is single-threaded as in Lua. A multiterra.t test exists and fails on PPC64le (issue #583). |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark harness: Scriptorium's tests/fib.t is a typed `terra fib(a : int) : int` compiled by LLVM, while tests/fib.lua is a dynamically typed function run by the PUC interpreter. The 11x compares a compiled language with an interpreter, not two script engines. bench.cc times whole `system()` runs, including LLVM start-up, with no fib(0) overhead subtracted (`overhead = 0`) and no check of program output. Terra's three bench.csv runs (0.124, 0.121, 0.124 s) are consistent.
- JIT performance depends on the LLVM version: release 1.2.2 (2026-08-14) notes 'Restore the manual inliner for JIT mode on LLVM 17+', so 1.2.0 and 1.2.1 builds against LLVM 17+ JIT-compiled without Terra's inliner.
- JIT code targets all host CPU features by default (1.2.1+). Objects or executables saved for distribution need an explicit target, and choosing a default triple and architecture is still an open issue (#633).
- Open crash reports cover embedding (#516, assertion `!lua_isnil(L->L, -1)` failed), segfaults after disassembling code (#450) and with the Vulkan API on prebuilt Linux binaries (#487), and failures on PPC64le (#583, #581, Moonjit bugs).

## Known shortcomings

- One fib test (0.121 s vs Lua 1.341 s) of typed, LLVM-compiled integer code against the Lua interpreter; LuaJIT (0.111 s) is faster and the Terra version is not stated.
- Enricher: the C embedding API (terra.h, terra_init and terra_dofile) needs a LuaJIT lua_State, so it is unusable in PUC Lua 5.4 hosts; the scriptorium run is typed LLVM-compiled fib against the Lua interpreter with whole-process time and no output check (bench.csv runs 0.124/0.121/0.124 s). The JIT inliner was missing on LLVM 17+ from 1.2.0 until 1.2.2 (2026-08-14); open crash issues #516, #450, #487; Windows maintainer wanted (#668).

## Caveats and trade-offs

Single micro-benchmark (recursive fib(34)), July 2015, Windows 7; the page says 'Take it with a grain of salt'. tests/fib.t is a statically typed 'terra fib(a : int) : int' function compiled to native code through LLVM, so this is compiled int code against the dynamically typed PUC Lua interpreter; times include process startup and LLVM JIT compilation. LuaJIT (0.111 s, the Lua that Terra itself embeds) and plain MSVC C (0.074 s) were faster. Terra's LLVM dependency breaks the page's own 'no LLVM backends' rule. Terra version used is not stated (linked as zdevito/terra). Peer-reviewed Terra paper (PLDI 2013) was not reachable here. Scriptorium repo is archived (r-lyeh-archived, last commit 2016-05-24).

Terra is a statically typed low-level language JIT-compiled through LLVM and hosted inside Lua, not a faster Lua interpreter: speedups only apply to code rewritten as Terra, and it needs LLVM. I did not verify a C or C++ embedding API.

## Maintenance

Active and MIT-licensed (Stanford): release 1.2.2 on 2026-08-14 added LLVM 19-22 and fixed calling-convention and JIT-inliner regressions, with 2.9k stars, 92 open issues and Windows maintenance asking for help. Usable via binary releases, but plan for a heavyweight LLVM-plus-LuaJIT dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (r-lyeh Scriptorium) with public harness (bench.cc, run.bat, tests/fib.t) whose row 3 shows terra 0.121 s against PUC Lua 1.341 s; not A because the CPU is given only as 'AMD A10 3.8 GHz' and the Terra and Lua build flags are not stated.
- **Verifier notes:** Numbers match Scriptorium row 3 exactly (11.0x vs PUC Lua); tier B kept. Shortcomings: one recursive-fib test, typed LLVM-compiled code vs Lua interpreter, slower than LuaJIT on the same page, heavy LLVM dependency.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.t>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://github.com/r-lyeh-archived/scriptorium/commits>
  - <https://github.com/terralang/terra>
  - <https://github.com/terralang/terra/commits>
- **Sources the enricher read:**
  - <https://github.com/terralang/terra>
  - <https://github.com/terralang/terra/issues>
  - <https://github.com/terralang/terra/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://raw.githubusercontent.com/terralang/terra/master/README.md>
  - <https://raw.githubusercontent.com/terralang/terra/master/release/share/terra/README.md>
  - <https://raw.githubusercontent.com/terralang/terra/master/release/include/terra/terra.h>
  - <https://raw.githubusercontent.com/terralang/terra/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/terralang/terra/master/CHANGES.md>
  - <https://raw.githubusercontent.com/terralang/terra/master/docs/getting-started.md>
  - <https://raw.githubusercontent.com/terralang/terra/master/LICENSE.txt>
  - <https://raw.githubusercontent.com/terralang/terra/master/release/share/terra/LICENSE.txt>
  - <https://raw.githubusercontent.com/terralang/terra/master/src/terra.h>
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.t>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/terralang/terra`) · [data/wave12/enrich/raw/github_com_terralang_terra.json](../../../data/wave12/enrich/raw/github_com_terralang_terra.json) (enrichment confidence 0.7)

</details>
