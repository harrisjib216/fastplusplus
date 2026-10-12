# LuaJIT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C (with hand-written assembly interpreter)` · `MIT` · 🟢 active

> Tracing JIT compiler and assembler-written interpreter for Lua 5.1; runs Lua code several times faster than PUC-Rio Lua 5.4.

| | |
|---|---|
| **Beats** | Lua 5.4.7 (PUC-Rio reference interpreter, per the README environment table) |
| **Claimed result** | kostya/benchmarks (different scripts per interpreter): bench.b Lua/luajit 5.686 s vs Lua 37.051 s (about 6.5x, derived from page data); primes Lua/luajit 0.309 s vs Lua 1.056 s (about 3.4x, derived from page data); mandel.b Lua/luajit 31.804 s with no plain-Lua row. Same-source kostya/jit-benchmarks (2023, LuaJIT 2.1.0-beta3 vs Lua 5.4.4): nbody 1.44 s vs 19.69 s (about 13.7x, derived from page data), mandelbrot 0.5 s vs 5.39 s (about 10.8x, derived from page data), spectralnorm 0.12 s vs 3.86 s; LuaJIT is slower on regexdna (9.99 s vs 8.94 s). |
| **Workload** | kostya/benchmarks: Brainfuck interpreter (bench.b; mandel.b has LuaJIT only) and the primes test (Atkin sieve plus Trie prefix search). The two interpreters do NOT run the same script: LuaJIT runs bf_jit.lua and primes_jit.lua, which use LuaJIT's FFI (uint8_t[8192] tape, bool[] sieve) and the bit library, while Lua runs bf.lua and primes.lua with Lua tables and 5.3+ integer operators. Same-source corroboration: kostya/jit-benchmarks runs one test.lua per program under both `lua` and `luajit`. |
| **Metric** | throughput |
| **Hardware** | kostya/benchmarks: Intel(R) Xeon(R) E-2324G, Docker (Debian forky/sid). kostya/jit-benchmarks: AMD Ryzen 7 3800X, Docker on Ubuntu 22.10. |
| **Compiler and flags** | Interpreters run as `luajit file.lua` and `lua file.lua` (common/commands.mk). kostya/benchmarks: LuaJIT 2.1.1748495995 built with plain `make -j` from the openresty/luajit2 tag v2.1-20260701 (LuaJIT Makefile default flags) in docker/Dockerfile; Lua from the Debian package (README lists 5.4.7, Dockerfile installs lua5.5). kostya/jit-benchmarks: Lua 5.4.4 and openresty luajit2 2.1.0-beta3 both built from source with plain `make -j4` (docker/lua, docker/luajit). |
| **Adoption** | 5.8k stars (repository description: mirror of the LuaJIT git repository) |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/LuaJIT/LuaJIT) · [benchmark](https://github.com/kostya/benchmarks) |

## Verdict

kostya/benchmarks (Xeon E-2324G, Docker on Debian forky, LuaJIT from openresty/luajit2 built with plain make, Lua from the Debian package) times LuaJIT at 5.686 s vs 37.051 s for Lua on bench.b and 0.309 s vs 1.056 s on primes, but with FFI-based \*_jit.lua scripts on the LuaJIT side. The same-source kostya/jit-benchmarks round from 2023-02-28 (Ryzen 7 3800X, LuaJIT 2.1.0-beta3 vs Lua 5.4.4, both built with plain make, CPU time from os.clock) gives nbody 1.44 s vs 19.69 s and mandelbrot 0.5 s vs 5.39 s, but LuaJIT is slower on regexdna (9.99 s vs 8.94 s).

## Use it when

- Embedding a scripting language in a C or C++ application (games, network proxies such as OpenResty, appliances) where Lua 5.1 semantics are acceptable and script CPU time matters.
- Numeric and loop-heavy Lua code: same-source kostya/jit-benchmarks numbers show about 10x to 30x over Lua 5.4.4 on nbody, mandelbrot, spectralnorm and matmul.
- Code that needs to call C libraries or work on raw C arrays and structs from Lua without writing C binding code (FFI).
- Platforms on the supported list: x86, x64, ARM, ARM64, PPC, MIPS32, MIPS64 on Windows, Linux, BSD, macOS, Android and consoles.

## Skip it when

- Code written for Lua 5.3/5.4: there is no integer subtype, no `//` floor division, no `_ENV`, no bit operator metamethods; 5.2 compatibility is partial and some parts need a -DLUAJIT_ENABLE_LUA52COMPAT build.
- String-library and pattern-matching workloads: LuaJIT lost regexdna to Lua 5.4.4 in kostya/jit-benchmarks (9.99 s vs 8.94 s) and gained only 2.2x on fasta and 2.6x on revcomp.
- Platforms that forbid runtime code generation (iOS, consoles): the JIT is disabled there and only the interpreter runs; the docs say it is still faster than plain Lua, but the large speedups disappear.
- Untrusted scripts that get FFI access: the FFI has no memory safety (out-of-bounds array access or a misdeclared C function can crash the process).
- Allocation-heavy workloads where memory is tight: binarytrees peaked at 307.5 MB under LuaJIT vs 145.2 MB under Lua 5.4.4.

## How it is fast

Two tiers: a fast bytecode interpreter written in assembler through DynASM, and a trace compiler that records hot loops and calls (hotloop default 56 iterations), turns them into SSA IR and optimizes them with constant folding, CSE, loop-invariant hoisting, load/store forwarding, array bounds check elimination, allocation sinking and operand fusion before emitting machine code. FFI cdata accesses (for example a `uint8_t[?]` or `bool[?]` array) are compiled to plain loads and stores, which is part of why the kostya/benchmarks `*_jit.lua` variants are fast.

## Compared with alternatives

Pick LuaJIT over LuaAOT (lua-aot-5.4), whose own README says it is not as fast as LuaJIT, and over Mobius, when your scripts can live with Lua 5.1 semantics; pick LuaAOT or stock Lua 5.4 when you need 5.4 integers and operators. Wren beat LuaJIT only with the JIT turned off (-joff) on its own method-call benchmark, so it is not a reason to skip LuaJIT for throughput.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (libluajit / lua51.dll) plus standalone luajit executable |
| **Dependencies** | none beyond the C library (-lm -ldl on Linux when linking statically) |
| **Minimum toolchain** | Recent GCC, Clang/LLVM or MSVC; GNU Make for the POSIX/MinGW build. The docs ask you to build it with its own build system and not to drop its sources into your tree. Default flags are -O2 -fomit-frame-pointer. |
| **Platforms** | x86, x64, ARM, ARM64, PPC, MIPS32, MIPS64; Windows, Linux, BSD, macOS, POSIX, Android, iOS (interpreter only), PS4/PS5/Xbox/Switch (interpreter only) |
| **Thread safety** | Not documented beyond the Lua 5.1 model: separate lua_State instances are independent; one state must not be used from several threads at once. |
| **Drop-in for the baseline** | partial: drop-in for Lua 5.1 (API+ABI compatible, including C modules); not a drop-in for the Lua 5.4.7 baseline used in the benchmark because 5.3/5.4 integer and operator semantics differ |

## Gotchas

- Harness flaw in the headline source: kostya/benchmarks runs different scripts under the two interpreters. bf_jit.lua is a different design from bf.lua (one closure per instruction, a fixed 8192-cell uint8_t FFI tape with no bounds check, separate inc/dec closures) while bf.lua uses a growing Lua table of unbounded integers and an if-chain dispatcher; primes_jit.lua swaps the Lua table for an FFI bool[] sieve. The 6.5x (bench.b) and 3.4x (primes) ratios therefore mix interpreter speed with data-structure choices. bench.b never underflows a cell, so the outputs agree.
- In kostya's primes.lua (the plain-Lua baseline) fill_array writes a global `a` (missing `local`), adding a global lookup per element over 5,000,001 iterations; primes_jit.lua does not have this cost because it uses ffi.new. The handicap is small but it favours LuaJIT.
- The kostya/benchmarks README version table is partly stale (it lists Java 24.0.2 and Go 1.25.0 while docker/Dockerfile installs JDK 26.0.1 and Go 1.26.5); its LuaJIT row 2.1.1748495995 carries a 2025-05-29 commit timestamp although the Dockerfile builds openresty/luajit2 v2.1-20260701, and it lists Lua 5.4.7 while the Dockerfile installs Debian lua5.5. Which binaries produced the timings is not certain.
- Code the JIT cannot compile (NYI operations, for example some FFI operations such as table initializers, aggregates by value, ffi.cdef calls inside loops) silently falls back to the interpreter; check with `luajit -jv`. Use luaL_newstate, not lua_newstate with a custom allocator, and load the `jit` library, or the JIT stays off.

## Known shortcomings

- kostya/benchmarks runs different scripts per interpreter (bf_jit.lua and primes_jit.lua use FFI arrays), so the 'same script' claim was wrong; the same-source kostya/jit-benchmarks numbers (nbody 13.7x, mandelbrot 10.8x, derived from page data) were added and LuaJIT loses regexdna there. The benchmarked binary is the openresty/luajit2 fork, and the README says Lua 5.4.7 while the Dockerfile installs lua5.5.
- Enricher: kostya's bf_jit.lua is a different design from bf.lua, not just FFI (one closure per instruction over a fixed unchecked 8192-cell uint8_t tape against table if-chain dispatch on unbounded ints; outputs agree), and primes.lua writes a global 'a' (missing local), a small handicap for Lua only. The README version table is stale (LuaJIT row 2.1.1748495995 is a 2025-05-29 build while the Dockerfile builds openresty v2.1-20260701; Java and Go rows also stale). Since 2026-07-20 v2.1 has native bit operators and other LuaJIT 3.0 syntax.

## Caveats and trade-offs

In kostya/benchmarks the LuaJIT rows run different source files from the Lua rows (bf_jit.lua and primes_jit.lua use FFI C arrays and a fixed 8192-cell byte tape), so those ratios mix interpreter speed with FFI data structures; LuaJIT implements Lua 5.1 semantics (no integer subtype or native bitwise operators), which is why separate scripts exist. Same-source kostya/jit-benchmarks gives larger wins (nbody about 13.7x, mandelbrot about 10.8x) but is from 2023 with older versions, and LuaJIT loses regexdna there (9.99 s vs 8.94 s). The benchmarked binary is the openresty/luajit2 fork, not LuaJIT/LuaJIT itself. The kostya README says the baseline is Lua 5.4.7 but docker/Dockerfile installs Debian lua5.5 (both changed in the same 2026-07-19 commit), so the exact baseline version is uncertain. Single median timings on one machine per suite. The GitHub repository is a mirror of the official luajit.org git repository.

Lua 5.1-based, so Lua 5.3/5.4-only features (native integers and similar) are not available. JIT compilation is unavailable on some locked-down platforms. Memory use is higher on allocation-heavy tests (307.5 MB vs 145.2 MB for binarytrees in kostya/jit-benchmarks, 2023).

## Maintenance

Actively maintained by Mike Pall on the rolling v2.1 branch (commits through 2026-09-08, including JIT fixes and the July 2026 syntax backport); MIT-licensed and copyable, with the GitHub repo a mirror of the official git repository and releases only as source or rolling 2.1.&lt;timestamp&gt; versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** kostya/benchmarks (independent, README updated 2026-07-19) publishes the code (brainfuck/bf.lua vs brainfuck/bf_jit.lua, primes/primes.lua vs primes/primes_jit.lua, common/commands.mk runs `lua` and `luajit`), the interpreter builds in docker/Dockerfile (openresty/luajit2 v2.1-20260701 built with plain make, Debian lua package) and the CPU (Xeon E-2324G); the same-source kostya/jit-benchmarks run (nbody/test.lua, mandelbrot/test.lua, docker/lua and docker/luajit built from source with plain make, Ryzen 7 3800X) corroborates at A.
- **Verifier notes:** Numbers match the kostya/benchmarks README rows and the jit-benchmarks tables; record wrongly said the same script ran under both interpreters (kostya uses FFI-based \*_jit.lua files), corrected and added same-source jit-benchmarks numbers. Metadata checked: MIT, 5.8k stars, mirror (not archived), last commit 2026-09-08 on v2.1. Note the spec lists LuaJIT as a baseline of the 'jits' category; here it is filed under language-interpreters against Lua 5.x, which is a valid baseline.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.lua>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf_jit.lua>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/primes/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/primes/primes.lua>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/primes/primes_jit.lua>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://github.com/kostya/benchmarks/commits/master/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.lua>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/lua>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/luajit>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://github.com/LuaJIT/LuaJIT>
  - <https://github.com/LuaJIT/LuaJIT/commits/v2.1>
- **Sources the enricher read:**
  - <https://github.com/LuaJIT/LuaJIT>
  - <https://github.com/LuaJIT/LuaJIT/commits/v2.1>
  - <https://github.com/LuaJIT/LuaJIT/issues/1475>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/README>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/COPYRIGHT>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/doc/luajit.html>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/doc/install.html>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/doc/extensions.html>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/doc/running.html>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/doc/ext_ffi_semantics.html>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/doc/ext_jit.html>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/Makefile>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/luajit_rolling.h>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/xtime.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bench.b>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf.lua>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf_jit.lua>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/primes/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/primes/primes.lua>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/primes/primes_jit.lua>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.lua>
  - <https://github.com/openresty/luajit2/tags>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/luajit/luajit`) · [data/wave12/enrich/raw/github_com_luajit_luajit.json](../../../data/wave12/enrich/raw/github_com_luajit_luajit.json) (enrichment confidence 0.85)

</details>
