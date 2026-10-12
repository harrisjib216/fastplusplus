# w2c2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Ahead-of-time WebAssembly-to-C89 translator; the compiled output beat Wasmtime in two independent blog runs.

| | |
|---|---|
| **Beats** | Wasmtime (independent blog runs); native C for the README CoreMark figure |
| **Claimed result** | README: 'Coremark 1.0: \~7% slower than native' (no runtime baseline). Independent, search snippets only (pages blocked): Frank Denis, 'The best WebAssembly runtime may be no runtime at all' (00f.net, 2023-12-11): a test module took 124.76 s user time under Wasmtime vs 73.38 s after w2c2 translation and zig cc compilation (1.70x, derived from the snippet numbers; the snippet does not say the module was the libsodium suite). Andy Wingo, 'wastrel, a profligate implementation of webassembly' (wingolog, 2025-10-30): on CoreMark Wastrel is 2-5% slower than native, w2c2 a further 2-5% slower, and Wasmtime 30-40% slower than GCC (roughly 1.2-1.35x in w2c2's favour, derived from snippet numbers). |
| **Workload** | README: CoreMark 1.0 translated by w2c2 and compiled to C, against native CoreMark (examples/coremark). Wasmtime comparisons: an unnamed module in Frank Denis's 2023-12-11 post and CoreMark in Andy Wingo's 2025-10-30 Wastrel post (both blocked, snippet only). |
| **Metric** | throughput |
| **Compiler and flags** | examples/coremark/Makefile: CFLAGS += -O3, compiler (\$(CC)) unstated; Frank Denis's run compiled the generated C with zig cc (snippet only) |
| **Adoption** | 830 stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/turbolent/w2c2) · [benchmark](https://github.com/turbolent/w2c2) |

## Verdict

First-party, the README says only 'CoreMark 1.0: \~7% slower than native' (examples/coremark, the wasm3/wasm-coremark module built with -O3; compiler, CPU and native build not stated; no runtime baseline). The faster-than-Wasmtime evidence is independent but read from search snippets only: Frank Denis (2023-12-11, generated C built with zig cc) measured 124.76 s user time under Wasmtime against 73.38 s for w2c2 (1.70x, derived), and Andy Wingo (2025-10-30) found that on CoreMark w2c2 trails native by roughly 4-10% while Wasmtime trails GCC by 30-40%. Hardware is not known for either run, and both ran the default unchecked output.

## Use it when

- Running trusted Wasm (your own C, C++ or Rust built for wasm32-wasi) at near-native speed when you can rebuild per module.
- Shipping one Wasm build to many OS and CPU targets, including big-endian PowerPC, SPARC and PA-RISC, classic Mac OS, DOS or old compilers that only accept C89.
- CPU-bound workloads where JIT or Cranelift AOT output is 20-40% slower than native (CoreMark, per the Wingo search snippet).
- Embedding Wasm-derived code in a C or C++ program with no runtime dependency beyond libc, libm and the optional WASI library.
- Translating very large modules with little memory: issue #1 reports clang.wasm (about 25 MB) translated in 5.1 s using 193 MB, versus 1 min 23 s and 1432 MB for wasm2c (2021, hardware not stated).

## Skip it when

- Untrusted modules: the default output has no linear-memory bounds checks and no guard pages (memory comes from calloc/realloc), and no call_indirect index, null or signature checks (issue #76, open since 2023-07-27), so an out-of-bounds Wasm access reads or writes the host heap.
- Plugins loaded or hot-swapped at run time: there is no interpreter or JIT, and each module needs a C compiler pass.
- Confining a guest's file access: WASI resolvePath returns absolute guest paths unchanged and joins relative paths to the preopen directory without normalizing '..', so a preopen does not restrict which host files a guest can open.
- Modules that need proposals the README does not list (SIMD, reference types, exception handling, GC) or memory64 (w2c2_base.h: 'Only support for wasm32 for now').
- Threaded modules with the opt-in checks enabled: wasmMemoryCheckRange locks the memory mutex on every load and store to shared memory, a cost no published benchmark measures.

## How it is fast

Single-pass translation maps each Wasm operand-stack slot to a typed C local and structured control flow to labelled gotos, so the host C compiler (-O3 in examples/coremark) does register allocation, inlining and instruction selection with its full optimizer. Linear-memory loads and stores are memcpy at data+addr, which compile to plain moves. By default (W2C2_RUNTIME_CHECKS=0) every bounds, table and call_indirect type check is compiled out, so part of the gap to Wasmtime is safety work that w2c2 does not do.

## Compared with alternatives

Pick w2c2 over wasm2c (WABT) when you need C89 output for old or big-endian targets or must translate very large modules with little memory; pick wasm2c, or LFI where isolating untrusted code is the goal, and keep WAVM or WasmEdge AOT when modules arrive at run time.

## Integration

| | |
|---|---|
| **Form** | source-drop (generated C plus w2c2_base.h); the translator is a CLI, also installable as a static or shared library with a CMake package |
| **Dependencies** | none for generated code beyond libc and libm; WASI programs link libw2c2wasi; threads need pthreads or Win32 plus the bundled futex library; libdwarf optional for #line mapping; the test suite needs Python 3 and wabt (wast2json, wat2wasm) |
| **Minimum toolchain** | a C89 compiler (README: 'mostly' C89, some common extensions used); CMake 2.8.12+ or Make to build the translator |
| **Platforms** | any host with a C compiler; README lists x86, ARM, PowerPC, SPARC, PA-RISC (big-endian supported), Mac OS X, Mac OS 9, Haiku, NeXTSTEP, DOS, Windows XP; guest modules wasm32 only |
| **Thread safety** | Wasm threads and atomics supported when built with WASM_THREADS_PTHREADS or WASM_THREADS_WIN32; shared memories are preallocated at their maximum size; other thread-safety guarantees not documented |
| **Drop-in for the baseline** | partial — replaces running a module under Wasmtime only when the module is known at build time and trusted; the API is generated C functions per export, with no runtime loading and no sandboxing by default |

## Gotchas

- W2C2_RUNTIME_CHECKS defaults to 0, which compiles out memory range checks, table bounds, null-element and call_indirect signature checks, atomic alignment traps and data.drop; in that mode addresses are 32-bit, so addr+offset wraps instead of trapping. The opt-in checks arrived on 2026-09-21 (PR #183, no description); the README CoreMark figure and both blog comparisons ran unchecked code.
- Harness flaw behind the README's 'passes 99.9% of the core semantics test suite': tests/gen.py emits only single-result assert_return and action commands and silently skips assert_trap, assert_invalid, assert_malformed, assert_exhaustion and multi-result assertions, and the suite builds at -O0. Trap behaviour is covered only by a small dedicated runtime_checks test, so the 99.9% figure says nothing about trapping.
- Generated output is large: issue #1 measured 1.3 GiB of C for clang.wasm (versus 301 MiB from wasm2c), so the downstream C compile, not translation, is the build bottleneck; use -f to split files.
- A burst of correctness fixes landed on 2026-09-21 (floating-point rounding under GCC optimization, atomic ordering, unsigned division trap reasons, non-recursive control-flow compilation); earlier versions and earlier benchmark runs had those bugs.

## Known shortcomings

- README number is first-party against native only, with no runtime baseline; the wins over Wasmtime are snippet only (1.70x in Frank Denis 2023-12, about 1.2-1.35x CoreMark in Andy Wingo 2025-10, which the record had credited to Denis). W2C2_RUNTIME_CHECKS=0 by default, so no Wasm memory bounds checks or guard pages (opt-in since 2026-09-21, PR #183): the comparison with Wasmtime is not like-for-like sandboxing.
- Enricher: the default W2C2_RUNTIME_CHECKS=0 strips memory, table, call_indirect and data.drop checks with addresses wrapping at 32 bits, and every published speed number ran this unchecked code; issue #76 (call_indirect not sandboxed) is open. The README's '99.9% spec pass' comes from tests/gen.py, which emits only single-result assert_return and action commands, skips every assert_trap, assert_invalid, assert_malformed and assert_exhaustion, and builds at -O0. WASI resolvePath passes absolute paths through and does not confine '..', so preopens do not sandbox; checked mode locks a mutex on every shared-memory access.

## Caveats and trade-offs

No compiler, CPU or runtime baseline for the README figure; all Wasmtime numbers are from search snippets of blocked posts (00f.net, wingolog.org), and the CoreMark comparison is Andy Wingo's (Wastrel author), not Frank Denis's. Safety is not equivalent to Wasmtime: w2c2_base.h defaults W2C2_RUNTIME_CHECKS to 0, which compiles out memory range checks on every load and store (and atomic alignment checks), and wasmMemoryAllocate takes linear memory from calloc/realloc with no guard pages, so default w2c2 output does not trap on out-of-bounds Wasm memory accesses as a sandboxing runtime does; the opt-in checks only landed on 2026-09-21 (PR #183), so every published comparison ran the unchecked code. The 2026 follow-up post's 0.814x-of-Wasmtime figure is for WABT wasm2c, not w2c2.

Ahead-of-time Wasm to portable C translator (inspired by wabt wasm2c): output must be compiled per module; runs on many OSes and architectures including big-endian; WASI and threads support; no JIT.

## Maintenance

Actively maintained (743 commits, last 2026-09-21) and MIT-licensed, so the translator and runtime header are copyable, but treat the default output as native code for trusted modules, not as a sandbox.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's only number is first-party ('Coremark 1.0: \~7% slower than native', built by examples/coremark/Makefile with -O3, compiler and CPU unstated) and names no runtime baseline. The faster-than-Wasmtime numbers come from two independent blog posts (Frank Denis 2023-12-11, Andy Wingo 2025-10-30) that are blocked here and known from search snippets only, so the tier stays C.
- **Verifier notes:** Kept at C: README number is first-party with no baseline runtime, and the Wasmtime wins (1.70x in Frank Denis 2023-12; about 1.2-1.35x on CoreMark per Andy Wingo 2025-10) are snippet only; record wrongly attributed the CoreMark comparison to Frank Denis. Main shortcoming for decisions: default build has no Wasm memory bounds checks (W2C2_RUNTIME_CHECKS=0, opt-in since 2026-09-21), so speed vs Wasmtime is not like-for-like sandboxing. Metadata confirmed (MIT, 830 stars, not a fork, last commit 2026-09-21).
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/turbolent/w2c2>
  - <https://github.com/turbolent/w2c2/commits>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/README.md>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/examples/coremark/Makefile>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/w2c2/w2c2_base.h>
  - <https://github.com/turbolent/w2c2/pull/183>
  - <https://github.com/turbolent/w2c2/pull/183/files>
- **Sources the enricher read:**
  - <https://github.com/turbolent/w2c2>
  - <https://github.com/turbolent/w2c2/commits>
  - <https://github.com/turbolent/w2c2/issues>
  - <https://github.com/turbolent/w2c2/issues/76>
  - <https://github.com/turbolent/w2c2/issues/1>
  - <https://github.com/turbolent/w2c2/pull/183>
  - <https://github.com/turbolent/w2c2/tree/main/examples/coremark>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/README.md>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/examples/coremark/Makefile>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/examples/coremark/main.c>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/examples/coremark/README.md>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/w2c2/w2c2_base.h>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/w2c2/c.c>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/w2c2/CMakeLists.txt>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/tests/Makefile>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/tests/gen.py>
  - <https://raw.githubusercontent.com/turbolent/w2c2/HEAD/wasi/wasi.c>
  - WebSearch: "w2c2" webassembly benchmark wasmtime "zig cc" "no runtime at all" (snippets of 00f.net posts 2023-12-11 and 2026-07-08)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/turbolent/w2c2`) · [data/wave12/enrich/raw/github_com_turbolent_w2c2.json](../../../data/wave12/enrich/raw/github_com_turbolent_w2c2.json) (enrichment confidence 0.6)

</details>
