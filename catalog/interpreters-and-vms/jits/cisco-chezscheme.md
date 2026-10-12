# Chez Scheme

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Scheme and C` · `Apache-2.0` · 🟢 active

> R6RS Scheme compiled to native code at load time; beats LuaJIT, PyPy and Node on integer-heavy interpreter loops, loses badly on boxed-float code.

| | |
|---|---|
| **Beats** | LuaJIT 2.1, PyPy 3 and Node.js (V8) |
| **Claimed result** | kostya/benchmarks (https://github.com/kostya/benchmarks), Chez Scheme 10.0.0, brainfuck bench.b: 1.758 s vs Node.js 2.954 s, Lua/luajit 5.686 s, Python/pypy 9.398 s (about 1.68x, 3.23x and 5.35x, derived from page data); Java 1.191 s is faster. mandel.b: 30.884 s vs luajit 31.804 s, Node.js 34.692 s, pypy 41.153 s (about 1.03x, 1.12x and 1.33x, derived from page data); Java 13.041 s is faster. Second source plb2 (https://github.com/attractivechaos/plb2, Chez 9.5.8, Apple M1): nqueen 3.54 s vs luajit 5.31 s, PyPy 6.91 s, Node 3.73 s and Java 3.92 s (faster than all four), but matmul 18.98 s vs luajit 2.66 s, Node 2.88 s, PyPy 4.89 s and Java 1.14 s (7.1x slower than LuaJIT and 16.6x slower than Java, derived from page data); plb2 has no Chez sudoku or bedcov. |
| **Workload** | kostya/benchmarks brainfuck interpreter (bench.b and mandel.b); plb2 nqueen and matmul. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E-2324G (kostya/benchmarks); Apple M1 (plb2) |
| **Compiler and flags** | kostya: `scheme --optimize-level 3 --program` (common/commands.mk SCHEME_RUN), Chez Scheme 10.0.0 from the Debian chezscheme package; baselines luajit 2.1.1748495995, pypy 7.3.23, Node.js v26.5.0, Java 24.0.2, all run with default flags. plb2: src/scheme/run.sh uses the same `scheme --optimize-level 3 --program`, Chez 9.5.8. |
| **Adoption** | 7.4k stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/cisco/ChezScheme) · [benchmark](https://github.com/kostya/benchmarks) |

## Verdict

kostya/benchmarks (Chez Scheme 10.0.0 from Debian, `scheme --optimize-level 3 --program`, Intel Xeon E-2324G, medians with MAD): brainfuck bench.b 1.758 s vs Node.js v26.5.0 2.954 s, LuaJIT 2.1 5.686 s and PyPy 7.3.23 9.398 s; mandel.b 30.884 s vs 31.804 s, 34.692 s and 41.153 s. plb2 (Chez 9.5.8, Apple M1, hyperfine) nqueen 3.54 s beats LuaJIT, PyPy, Node and Java, but matmul 18.98 s is 7.1x slower than LuaJIT.

## Use it when

- Symbolic or integer-heavy workloads (interpreters, tree walking, search with fixnum bit tricks): kostya brainfuck bench.b 1.758 s vs Node.js 2.954 s and LuaJIT 5.686 s; plb2 nqueen 3.54 s vs LuaJIT 5.31 s and PyPy 6.91 s.
- You want predictable speed without JIT warm-up: code is compiled when loaded, so short runs do not pay for profiling tiers.
- Embedding a garbage-collected scripting language with proper tail calls and first-class continuations into a C host, with modest memory (about 26 MiB RSS for bf.ss vs 244 MiB for Julia and 50 MiB for Node.js in kostya).
- Platforms beyond x86-64: native code on AArch64, RV64G, LoongArch64 and PowerPC32, and a portable bytecode (pb) build for anything else, including WebAssembly via Emscripten.

## Skip it when

- Floating-point array code written with generic vectors: plb2 matmul 18.98 s vs LuaJIT 2.66 s, Node 2.88 s and Java 1.14 s, because every element is a boxed flonum; on 10.x rewrite with flvectors and fl operators before judging.
- You need a JIT library for your own language or a drop-in replacement for LuaJIT, V8 or PyPy: Chez runs Scheme only, and the compiler is not exposed as a code-generation API for other languages.
- You need the speed and cannot accept unsafe mode: both benchmarks run at optimize-level 3, which disables run-time type checks; a type error in that mode is undefined behavior, not an exception. Safe-mode numbers are not published in either suite.
- Close races: the mandel.b win over LuaJIT is about 3% (30.884 s vs 31.804 s), and Java beats Chez on both brainfuck tests (1.191 s and 13.041 s).
- Heavy string or file I/O: open issues #877 (string operations) and #428 (performance and memory with string and file I/O) report slow paths.

## How it is fast

An ahead-of-execution optimizing compiler (nanopass-style passes, cross-library inlining, whole-program optimization) emits native code for x86-64, AArch64, RV64G, LoongArch64 and others; there is no tracing or profiling tier, so code is fast from the first call with no warm-up. optimize-level 3 removes run-time type and bounds checks, and fixnum-specific operators (fx+, fxvector-ref) compile to plain machine instructions; since 10.0.0 the compiler also does type recovery and locally unboxes flonum arithmetic, with flvectors that cooperate with unboxing. A generational garbage collector manages allocation.

## Compared with alternatives

Choose Chez over Julia when you want a far smaller runtime (26 MiB vs 244 MiB RSS in kostya) and no warm-up on symbolic or integer code where both are close (bench.b 1.758 s vs 1.564 s); over .NET RyuJIT or the Dart VM when you want an embeddable Scheme with tail calls and continuations rather than a managed platform. For floating-point kernels pick Julia, Dart or .NET (plb2 matmul 0.76 s, 2.74 s and 1.38 s vs 18.98 s).

## Integration

| | |
|---|---|
| **Form** | executable plus boot files (petite.boot, scheme.boot); the C kernel links into a host as a static library or, on Windows, a DLL or static library |
| **Dependencies** | C compiler; ncurses (unless --disable-curses) and X11 headers (unless --disable-x11) on Unix; Visual Studio on Windows |
| **Minimum toolchain** | GCC, Clang or similar on Unix; Microsoft Visual Studio 2017, 2019, 2022 or 2026 on Windows; native AArch64, RV64G and LoongArch64 code needs Chez 10.0.0 or later |
| **Platforms** | Windows x86/x86_64/AArch64; macOS x86/x86_64/AArch64/PowerPC32; Linux x86/x86_64/ARMv6/AArch64/RV64G/LoongArch64/PowerPC32; BSDs, Solaris, Hurd, Haiku, Android, iOS; WebAssembly via the pb bytecode interpreter only |
| **Thread safety** | Threaded builds (the default; --nothreads disables them) run native threads; most primitives and simple mutators are thread-safe, but other destructive operations on shared objects need mutexes, code-loading threads' code should run only in that thread or its children, and threads created in C must call Sactivate_thread before touching Scheme data. |
| **Drop-in for the baseline** | no |

## Gotchas

- plb2 harness flaw: its Chez row is version 9.5.8 on an Apple M1, but upstream Chez gained Apple Silicon (AArch64) code generation only with the v9.9.9 merge in Oct 2023 (PR #607) and 10.0.0 lists AArch64 as newly supported, so the 9.5.8 numbers were most likely x86-64 code run under Rosetta 2. plb2 does not say; this biases both nqueen and matmul against Chez.
- plb2 matmul.scm stores doubles in a plain vector, so each fl+ and fl\* result is heap-allocated; 9.5.8 had no local flonum unboxing or flvectors (both added in 10.0.0), so the 7x loss reflects that version and that code, not Chez 10.x with flvectors.
- kostya bf.ss is not tuned: tape-move allocates a new tape record on every &gt; or &lt;, and the tape grows one cell at a time with a full vector copy; Chez still beats Node, LuaJIT and PyPy with it, but cell values are unbounded integers and loops test &gt; 0, the same semantics as the bf.js and bf_jit.lua baselines.
- kostya times only the region between the start and stop notifications, so Chez's load-time compilation of bf.ss is excluded while LuaJIT, V8 and PyPy JIT compilation happens inside the timed region; for 1.7 s to 41 s runs the effect is small.

## Known shortcomings

- Mixed results: beats LuaJIT, PyPy and Node only on kostya brainfuck (about 3% over LuaJIT on mandel.b) and plb2 nqueen, while plb2 matmul is 7-17x slower than every baseline and Java is faster on brainfuck. Runs at unsafe optimize-level 3 and compiles the whole program at load time rather than tracing. Scheme implementation in C and Scheme, not C++.
- Enricher: plb2 ran Chez 9.5.8, which has no AArch64 backend (added with the 9.9.9 merge in October 2023, PR #607), so the M1 row most likely ran under Rosetta 2 and is biased against Chez; matmul.scm uses boxed flonums and 9.5.8 lacks flvectors and unboxing. The kostya bf.ss is untuned (allocates a tape record per move) but semantically matches bf.js and bf_jit.lua.

## Caveats and trade-offs

Mixed results: Chez wins only the brainfuck interpreter tests in kostya (the only kostya tests that have a Chez row) and plb2 nqueen; plb2 matmul is 7-17x slower than every JIT baseline (its source stores doubles in a generic Scheme vector, so every element is a boxed flonum). The mandel.b margin over LuaJIT is about 3%. Java (HotSpot) beats Chez on both kostya brainfuck tests. optimize-level 3 is Chez's unsafe mode (type and bounds checks removed), which the baselines do not get. Chez is not a tracing or profiling JIT: the full compiler (Debian chezscheme package) compiles the program to native code when it is loaded, so the category fit is load-time compilation. The brainfuck programs differ in shape across languages (Chez walks a parsed op list recursively; LuaJIT's bf_jit.lua dispatches through one closure per op; Node, Java and C# use a parsed op tree with a switch), so the comparison is per idiomatic implementation, not identical code. plb2 numbers are from Chez 9.5.8 (early 2024 versions) and its author notes his non-C implementations may be suboptimal.

Incremental native-code compiler with a Scheme runtime, not a general-purpose embeddable JIT; C interface exists; optimize-level 3 removes safety checks.

## Maintenance

Actively maintained by Cisco with community merges (release notes at Version 10.5.0, May 2026; last commit 2026-10-01); Apache-2.0 and portable, so copyable, though the benchmark numbers come from 10.0.0 and 9.5.8.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** kostya/benchmarks README rows match exactly; benchmark code brainfuck/bf.ss is public, run via common/commands.mk SCHEME_RUN (`scheme --optimize-level 3 --program`), Chez Scheme 10.0.0 from the Debian chezscheme package in docker/Dockerfile, Intel Xeon E-2324G, and the LuaJIT/PyPy/Node.js baselines' versions and run commands are in the same files.
- **Verifier notes:** All kostya and plb2 numbers verified on the pages; added that Chez also beats Java on plb2 nqueen and that the mandel.b win over LuaJIT is only 3%. Resolved the execution-mode question: the Docker image installs the full Debian chezscheme package and both suites run `scheme --optimize-level 3 --program` (compiled to native code at load, unsafe mode). Metadata verified: Apache-2.0, 7.4k stars, last commit 2026-10-01, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
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
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.ss>
  - <https://github.com/attractivechaos/plb2/tree/master/src/scheme>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/scheme/run.sh>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/scheme/matmul.scm>
  - <https://github.com/cisco/ChezScheme>
  - <https://github.com/cisco/ChezScheme/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/cisco/ChezScheme/HEAD/README.md>
  - <https://raw.githubusercontent.com/cisco/ChezScheme/HEAD/BUILDING>
  - <https://raw.githubusercontent.com/cisco/ChezScheme/HEAD/release_notes/release_notes.stex>
  - <https://raw.githubusercontent.com/cisco/ChezScheme/HEAD/csug/use.stex>
  - <https://raw.githubusercontent.com/cisco/ChezScheme/HEAD/csug/threads.stex>
  - <https://raw.githubusercontent.com/cisco/ChezScheme/HEAD/csug/foreign.stex>
  - <https://github.com/cisco/ChezScheme/pull/607>
  - <https://github.com/cisco/ChezScheme/issues?q=is%3Aissue+is%3Aopen+performance>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.ss>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.js>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf_jit.lua>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/docker/Dockerfile>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/README.md>
  - <https://github.com/attractivechaos/plb2/tree/master/src/scheme>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/scheme/run.sh>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/scheme/matmul.scm>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/scheme/nqueens.scm>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/c/nqueen.c>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/cisco/chezscheme`) · [data/wave12/enrich/raw/github_com_cisco_chezscheme.json](../../../data/wave12/enrich/raw/github_com_cisco_chezscheme.json) (enrichment confidence 0.7)

</details>
