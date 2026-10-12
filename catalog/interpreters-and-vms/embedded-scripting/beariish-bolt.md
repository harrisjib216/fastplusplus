# Bolt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Small statically typed embeddable scripting language in C; author's charts show 1.2x to 3.1x Lua 5.4 on 9 of 10 microbenchmarks.

| | |
|---|---|
| **Beats** | Lua 5.4 (PUC-Rio). The same charts also include Luau, LuaJIT with the JIT off (-joff), Lua 5.1 and 5.3, Wren, Python 3.9 and 2.7, and Node with --jitless. |
| **Claimed result** | Versus Lua 5.4 (chart values, ms, lower is better): fib(30) 52 vs 62; closure iterator (10M iterations) 188 vs 300; Mandelbrot 87 vs 184; Vec2 create-create-add 39 (14 with mimalloc) vs 85; Vec2 add 12.7 (4.7 with mimalloc) vs 26.0; Vec2 distance 31 vs 96; binary_tree(4,12) 274 vs 339; spectral(500) 376 vs 471; nbody(500000) 744 vs 1097. Slower on fannkuch(9): 281 vs 148. Ratios derived from page data: about 1.2x (fib) to 3.1x (Vec2 distance) with the system allocator, and 5.5x to 6.1x on the two Vec2 allocation benchmarks with mimalloc. |
| **Workload** | Ten interpreter-only micro-benchmarks: fib(30), 10M-iteration closure iterator, 256x256 Mandelbrot (255 iterations), Vec2 create/add/distance object benchmarks, binary_tree(4, 12), spectral(500), nbody(500000) and fannkuch(9). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3900X, 32 GB DDR4-3200 in dual channel |
| **Compiler and flags** | Bolt: MSVC (version not stated) using the repo's CMake configuration; bolt/CMakeLists.txt sets /O2 /Ob2 /Oi /Ot /Oy /GL /GS- /GR- /arch:AVX for Release (and -Ofast -O3 for non-MSVC builds). Baselines: 'built to recommended build instructions, or using a provided pre-compiled binary, depending on which is faster'; no flags or versions beyond the major version given. |
| **Adoption** | 816 stars |
| **Last commit** | 2026-01-05 |
| **Links** | [repository](https://github.com/Beariish/bolt) · [benchmark](https://github.com/Beariish/bolt/blob/main/doc/Bolt%20Performance.md) |

## Verdict

The author's doc/Bolt Performance.md charts (AMD Ryzen 9 3900X, Windows, Bolt built with MSVC using the repo's CMake Release flags, baselines with unstated builds) show Bolt faster than Lua 5.4 on 9 of 10 interpreter microbenchmarks, from about 1.2x on fib(30) (52 vs 62 ms) to 3.1x on Vec2 distance (31 vs 96 ms), and 5.5x to 6.1x on two Vec2 allocation tests only with mimalloc; it is 1.9x slower on fannkuch(9). The Lua side of the harness is not in the repository, and a Show HN commenter's brainfuck interpreter test (snippet only) put Bolt about 20% ahead of Lua 5.4 and 2x behind LuaJIT with the JIT off.

## Use it when

- A C or C++ host (games, real-time tools) that wants compile-time type errors in scripts and cheap native calls, and can accept a new language rather than Lua.
- Float-arithmetic and method-call heavy script code: the author's charts show the largest gaps over Lua 5.4 on Vec2 distance (31 vs 96 ms), Mandelbrot (87 vs 184 ms) and the closure iterator (188 vs 300 ms).
- Allocation-heavy small-object code where you can plug in mimalloc through bt_Handlers; only with mimalloc did Bolt lead the Vec2 create/add charts (14 and 4.7 ms vs Lua 5.4's 85 and 26.0 ms).
- 64-bit x86-64 or arm64 targets built with MSVC, GCC or Clang where a small C codebase you can read and vendor matters more than ecosystem.

## Skip it when

- Production code that needs stability: the README says Bolt is 'not yet stable, expect to encounter compiler bugs and crashes', and issues #77, #70, #67, #59 and #51 (2025) were segfaults or crashes in the compiler or runtime.
- Integer-heavy work such as permutations or bit manipulation: Bolt has only a double 'number' type and was 1.9x slower than Lua 5.4 on fannkuch(9) (281 vs 148 ms); Luau also beat it on binary_tree, nbody and fannkuch in the same charts.
- Deep recursion or tail-call style code: no tail-call optimisation, the default call stack is BT_CALLSTACK_SIZE 128 frames and the value stack 1024 slots ('Stack overflow!' runtime error beyond that), and each Bolt call also recurses on the C stack.
- 32-bit targets (explicitly unsupported, issue #79 open), Windows on ARM64 through the Visual Studio generator (the root CMakeLists aborts unless the VS platform is x64), or untrusted scripts that need a documented sandbox.
- Memory-constrained hosts: the default GC does not start its first cycle until 32 MB (bt_gc.c), and a Show HN commenter reported 47 MB versus 2.5 MB for Lua on a brainfuck interpreter (search snippet only; thread blocked here).

## How it is fast

Values are 8-byte NaN-boxed words where doubles are stored unmasked, and the type checker sets an 'acceleration bit' on opcodes whose operand types are known, so ADD/SUB/MUL/DIV/LT on numbers become a single native operation with no tag check. The VM is register-based (three-operand instructions), uses 'inline threading' (a replicated switch at the end of every handler, the portable stand-in for computed goto on MSVC), resolves imports to an indexed array per module, and uses a setup-light calling convention because arity and returns are known statically. Typed table creation copies a pre-hashed prototype (one alloc plus memcpy), and short strings are interned.

## Compared with alternatives

Pick Bolt over Lua 5.4 or Umka when you want static typing with an interpreter that, by its author's charts, beats PUC Lua on calls and float math, in a small C codebase; pick Luau for comparable or better speed with a mature sandbox and tooling, or Daslang for a statically typed interpreter with independent measurements and a much larger lead over Lua.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake, bolt/ plus the bolt-cli example host); BOLT_SHARED_LIBRARY option for a shared build; plain C source that can be vendored |
| **Dependencies** | C standard library and libm on Unix; bundles the author's picomatch regex library; IO, file loading and printf use can be compiled out (bt_config.h); allocator is pluggable (malloc by default, mimalloc recommended by the author) |
| **Minimum toolchain** | C11 (MSVC /std:c11), CMake 3.16; CI builds with MSVC on Windows, GCC and Clang on Ubuntu, Clang on macOS |
| **Platforms** | x86-64 and arm64 only (README); RISC-V untested; Windows, Linux, macOS |
| **Thread safety** | not documented; each bt_Context owns its GC, modules and objects, bt_Thread is a script call stack (not an OS thread), and no locks or atomics appear in the runtime, so treat a context as single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness: only Bolt's side of the benchmarks is public (benchmarks/_foreign is missing), so the Lua 5.4 timing method is unknown; Bolt's own harness (benchmarks/bench.bolt) times in-process with a wall-clock timer after iter/2 warm-up runs, excludes compile and start-up, and never checks results (Mandelbrot's 'rolling sum to ensure correctness' and fib's result are discarded; Vec2.distance adds rather than subtracts its components).
- Harness: Bolt's Release build uses /fp:fast /arch:AVX /GL (MSVC) or -Ofast -ffast-math -march=native -flto (GCC/Clang) while the baselines were built 'to recommended build instructions' with unstated flags, so the float-heavy wins (Mandelbrot, nbody, spectral, Vec2 distance) may include a fast-math advantage; the mimalloc rows pit Bolt with mimalloc against baselines on their default allocator.
- Correctness risk found by code reading (not run): bt_make_number stores doubles bit-for-bit with no NaN canonicalisation, and BT_VALUE_NULL is 0xFFF8000000000000, the default NaN x86-64 SSE produces for 0/0, sqrt(-1) or inf-inf, so on x86-64 such a result is bitwise identical to null for BT_IS_NUMBER and null checks; arm64's default NaN is positive and stays a number. Fast-math builds also make NaN/inf comparisons in scripts unreliable.
- Runtime errors unwind with setjmp/longjmp, so C++ native functions that hold RAII objects across a Bolt error are skipped without destructors; and CI's ctest step registers no tests (no add_test in the CMake files), so it only checks that the build compiles.

## Known shortcomings

- Chart values match the PNGs, but the benchmarks/_foreign sources (Lua and others) are missing from the repo (404) and the Lua 5.4 build is unstated; slower than Lua on fannkuch (281 vs 148 ms) and needs mimalloc to lead on Vec2 allocation. MSVC flags taken from bolt/CMakeLists.txt.

## Caveats and trade-offs

First-party benchmark; the numbers are bar-chart images in the doc (read from the PNGs), averages of 10 or 15 runs with no pinning or variance stated. The doc says the other languages' implementations are in benchmarks/_foreign, but that directory does not exist in the repository (404), so only the Bolt side of the benchmark code is public. Bolt is slower than Lua 5.4 on fannkuch(9) (281 vs 148 ms). Luau beats Bolt on binary_tree, nbody and fannkuch, Wren beats Bolt on binary_tree (247 vs 274 ms), and with the system allocator Luau and LuaJIT -joff beat Bolt on both Vec2 allocation benchmarks (Bolt only leads there with mimalloc). Only interpreters are compared (JIT runtimes excluded except LuaJIT -joff). The Lua 5.4 minor version and build flags are not stated, and Bolt was built on Windows with MSVC; the chart date is not given, so the numbers may predate the current code. Bolt is a statically typed language of its own, not a Lua drop-in.

A different language, not Lua source-compatible: statically type-checked, 8-byte NaN-boxed values, register VM, embed-first C API. No tail-call optimisation. The compiler is described as early stage. Allocation-heavy results depend on the allocator (system allocator versus mimalloc).

## Maintenance

Active single-author project (816 stars, last commit 2026-01-05, crash fixes through December 2025) but explicitly pre-stable with no version tags; MIT-licensed and small enough to vendor, though expect compiler bugs and language changes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party bar charts in doc/Bolt Performance.md (images under doc/_images) compare Bolt with Lua 5.4 on a named CPU (Ryzen 9 3900X) and Bolt's MSVC flags are public in bolt/CMakeLists.txt, but the Lua 5.4 minor version and build are unstated ('recommended build instructions, or a provided pre-compiled binary') and the foreign-language benchmark sources the doc points to (benchmarks/_foreign) are not in the repository, so it falls short of A.
- **Verifier notes:** All chart values in the record match the PNGs exactly; license MIT, 816 stars, last commit 2026-01-05, not a fork. Shortcomings to record: baseline benchmark sources (benchmarks/_foreign) missing from repo, Lua 5.4 build unstated, slower than Lua 5.4 on fannkuch, needs mimalloc to lead on allocation-heavy benchmarks.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Beariish/bolt/blob/main/doc/Bolt%20Performance.md>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/Bolt%20Performance.md>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/_images/Fib.png>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/_images/Closure%20iterator%20performance.png>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/_images/Mandelbrot.png>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/_images/Vec2%20create%20create%20add.png>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/_images/Vec2%20add.png>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/_images/Vec2%20distance.png>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/_images/BinaryTree.png>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/_images/Spectral.png>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/_images/Nbody.png>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/_images/Fannkuch.png>
  - <https://github.com/Beariish/bolt>
  - <https://github.com/Beariish/bolt/commits/main>
  - <https://github.com/Beariish/bolt/tree/main/benchmarks>
  - <https://github.com/Beariish/bolt/tree/main/benchmarks/_foreign>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/README.md>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/Beariish/bolt>
  - <https://github.com/Beariish/bolt/commits/main>
  - <https://github.com/Beariish/bolt/issues?q=is%3Aissue>
  - <https://github.com/Beariish/bolt/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/README.md>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt-cli/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/.github/workflows/cmake-multi-platform.yml>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/Bolt%20Performance.md>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/Bolt%20Embedding%20Guide.md>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/doc/Bolt%20Users.md>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/benchmarks/all.bolt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/benchmarks/bench.bolt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/benchmarks/recursion.bolt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/benchmarks/loops.bolt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/benchmarks/mandel.bolt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/benchmarks/vec2.bolt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/benchmarks/vec2hoist.bolt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/benchmarks/binary_tree.bolt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/benchmarks/spectral.bolt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/benchmarks/nbodies.bolt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/benchmarks/fannkuch.bolt>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/bolt.c>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/bolt.h>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/bt_value.h>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/bt_value.c>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/bt_config.h>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/bt_context.h>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/bt_op.h>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/bt_prelude.h>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/bt_gc.c>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/bt_embedding.h>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/boltstd/boltstd_math.c>
  - <https://raw.githubusercontent.com/Beariish/bolt/HEAD/bolt/boltstd/boltstd_core.c>
  - WebSearch: 'Beariish bolt embeddable language benchmark Lua Luau comparison' (snippet of https://news.ycombinator.com/item?id=44856935, thread itself not opened)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/beariish/bolt`) · [data/wave12/enrich/raw/github_com_beariish_bolt.json](../../../data/wave12/enrich/raw/github_com_beariish_bolt.json) (enrichment confidence 0.7)

</details>
