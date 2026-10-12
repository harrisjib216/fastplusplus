# VMIR

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> Single-file C interpreter for LLVM bitcode and early WebAssembly; about 96x faster than LLVM's lli interpreter on one SHA-1 run.

| | |
|---|---|
| **Beats** | LLVM lli (LLVM IR interpreter) |
| **Claimed result** | Core i7 3.2GHz, sha1test over 64MB of random data: VMIR 4.8s vs LLVM LLI 7m 39s (about 96x faster, derived from page data); native 0.39s (VMIR about 12x slower than native, derived from page data). Raspberry Pi 2 (BCM2709): VMIR 1m 42s, VMIR JIT 17.5s, native 3.54s (no LLI figure). README: interpretation is about 10x slower than native on x86. |
| **Workload** | test/misc/src/sha1test.c over 64MB of random data, run as LLVM bitcode in the VMIR interpreter versus lli. |
| **Metric** | throughput |
| **Hardware** | Core i7 3.2GHz (exact model not stated); ARMv7 BCM2709 (Raspberry Pi 2): VMIR 1m42s, VMIR JIT 17.5s, native 3.54s |
| **Adoption** | 700 stars |
| **Last commit** | 2018-08-29 |
| **Links** | [repository](https://github.com/andoma/vmir) · [benchmark](https://raw.githubusercontent.com/andoma/vmir/HEAD/README.md) |

## Verdict

The README's single table times test/misc/src/sha1test.c hashing 64 MB of random data: on an unspecified Core i7 at 3.2 GHz, VMIR 4.8 s versus LLVM lli 7 min 39 s (about 96x, derived from page data) and native 0.39 s (VMIR about 12x slower); on a Raspberry Pi 2, VMIR 1m42s, VMIR JIT 17.5 s, native 3.54 s. No compiler or LLVM versions, flags for native or lli, or the bitcode optimisation level are given, and the README does not say whether the times include bitcode loading and lowering (main.c's -s option times only vmir_run).

## Use it when

- You must execute LLVM bitcode from C without linking LLVM, and lli's interpreter is the alternative (the README's only baseline).
- Small embedded or plugin hosts that want one C file (src/vmir.c includes the rest) and a fixed, caller-allocated memory arena.
- 32-bit ARM Linux targets where the built-in JIT applies (README: Raspberry Pi 2 SHA-1 run 17.5 s with JIT vs 1m42s interpreted).
- Plain C plugins compiled with an old clang that use only the subset of libc VMIR implements and no vector types.
- Research or teaching on lowering SSA IR to a register-based threaded interpreter.

## Skip it when

- Running untrusted code: release builds do no guest bounds checks (only the VM_TRACE debug build checks), so guest pointers and libc calls such as fread can touch host memory outside the arena, and guest division by zero reaches the host as a native fault.
- Modern toolchains: open issue #14 (2018) reports bitcode from Ubuntu Bionic's clang fails to parse ('Type (i8) (index:0) is not a pointer'), issue #5 says clang 3.9 does not work, and LLVM's later opaque-pointer bitcode is not handled by any commit after 2018-08-29.
- Modern WebAssembly: the parser rejects resizable memories and tables, imported memories, tables and globals, multi-value returns, and accepts only constants in init expressions (Go-built wasm fails, issue #9); for wasm use wasm3, WAMR or Wasmi.
- C++ programs needing the STL, code relying on SIMD/vector types, or programs needing a full libc.
- Performance-critical x86-64 work: the interpreter is about 12x slower than native on the README's x86 run and there is no x86 JIT.

## How it is fast

Instead of walking LLVM IR like lli's interpreter, VMIR lowers each function at load time: it leaves SSA, runs liveness analysis with an interference-matrix register allocator and move coalescing, then applies peephole fusions (GEP+load/store into lea addressing, compare+branch, compare+select, multiply+add, load+cast) and emits a compact 16-bit-word instruction stream with type- and constant-specialised opcodes (for example ADD_R32C). The stream is executed with computed-goto threaded dispatch over register frames, and on 32-bit ARM Linux an optional JIT emits native code for the instruction classes it supports. Guest loads and stores in release builds are plain host-pointer arithmetic with no bounds check, which also removes per-access cost.

## Compared with alternatives

Pick VMIR over wasm3, WAMR or Wasmi only when your input is LLVM bitcode rather than wasm and you can live with an unmaintained, unsandboxed interpreter; for any WebAssembly workload those siblings are maintained, spec-conformant, bounds-checked and have published cross-runtime numbers that VMIR lacks.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libm; TLSF allocator vendored in tlsf/ and enabled by the Makefile with -DVMIR_USE_TLSF) |
| **Minimum toolchain** | C99 with GNU extensions (-std=gnu99; computed goto and case ranges); issue #7 reports it only builds with clang, not gcc (not re-tested here). Guest code needs a 2016-2017 era clang emitting le32-unknown-nacl bitcode. |
| **Platforms** | Interpreter: any POSIX host the code builds on (Makefile targets x86-64 host, armv7 and ppc64 with big-endian byte swapping). JIT: 32-bit ARM Linux/Android only. |
| **Thread safety** | not documented; state lives in the per-instance ir_unit_t, but no statement about concurrent instances or calls |
| **Drop-in for the baseline** | no |

## Gotchas

- No sandboxing in release builds: CHECK_MEM_ACCESS() in src/vmir_mem.c is empty unless VM_TRACE is defined, HOSTADDR(ea) is hostmem + a 32-bit guest address, and libc shims like vmir_fread pass guest buffers and lengths straight to host fread without a length check.
- Seven memory-safety reports against the wasm/bitcode loader were filed on 2024-03-06 (issues #18-#24: null derefs, heap-buffer-overflow in wasm_call, wild reads and writes, stack overflow) and are unanswered, so loading untrusted files can crash or corrupt the host.
- Guest code must be compiled with -fno-vectorize -fno-slp-vectorize and multi-file programs must be llvm-link'ed into one .bc; the le32-unknown-nacl target is required.
- The benchmark's lli baseline is LLVM's IR interpreter, which the README itself calls not intended to be fast; lli's JIT mode, the LLVM version and the bitcode optimisation level (the test Makefile builds -O0, -O1 and -O2) are not stated, so the 96x figure says little about VMIR against any production engine.

## Known shortcomings

- 4.8 s against lli's 7m39s (about 96x, derived from page data) is a weak baseline (the LLVM lli interpreter); VMIR is about 12x slower than native, no CPU model or LLVM version, last commit 2018-08-29 (abandoned).
- Enricher: no sandbox in release builds (CHECK_MEM_ACCESS() in src/vmir_mem.c is empty unless VM_TRACE is defined, host address is hostmem plus the guest address, vmir_fread passes a guest buffer to the host fread unchecked, a guest division by zero crashes the host); 7 memory-safety issues (#18-#24, 2024-03-06) open and unanswered, newer clang bitcode fails (#14), Wasm support is MVP-only (#9). The lli mode, LLVM version and bitcode -O level are unstated.

## Caveats and trade-offs

Single README table, one workload (SHA-1), no exact CPU model, no LLVM version or lli flags, and no statement of which bitcode optimisation level (the test Makefile builds -O0, -O1 and -O2) was timed. The 96x gap is against lli's interpreter, which the README itself says 'is not intended to run code fast in any way', so it is a weak baseline; against native code VMIR is about 12x slower on x86 and about 29x slower on the Pi 2 (JIT about 5x slower; derived from page data). The JIT exists only for 32-bit ARM. VMIR also runs WebAssembly but is not compared with wasm3, WAMR or wasmtime. Built-in libc is incomplete, no vector types (code must be compiled with -fno-vectorize -fno-slp-vectorize), no C++ STL. Last commit 2018-08-29.

Standalone C library that executes both LLVM bitcode (.bc) and WebAssembly (.wasm); the built-in libc is incomplete, no vector types, no C++ STL support, and the JIT exists only for 32-bit ARM and does not cover all instruction classes.

## Maintenance

Abandoned since 2018-08-29 with 18 open issues including unanswered 2024 memory-safety reports; MIT-licensed and easy to vendor as one C file, but only usable with old clang bitcode and only safe for trusted code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance table compares VMIR with LLVM LLI on test/misc/src/sha1test.c (public, as are the VMIR Makefile at -O2 and test/misc/Makefile building bitcode at -O0/-O1/-O2), but the CPU model ('Core i7 3.2GHz'), LLVM/lli version and flags, and which bitcode optimisation level was timed are not stated, so it is first-party C.
- **Verifier notes:** Numbers match the README exactly; benchmark source test/misc/src/sha1test.c exists. Kept at C: weak baseline (lli interpreter), no CPU model/compiler versions. Metadata confirmed: MIT (LICENSE, Lonelycoder AB 2016), 700 stars, 80 forks, last commit 2018-08-29 (abandoned), not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/README.md>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/test/misc/src/sha1test.c>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/Makefile>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/test/misc/Makefile>
  - <https://github.com/andoma/vmir>
  - <https://github.com/andoma/vmir/commits>
- **Sources the enricher read:**
  - <https://github.com/andoma/vmir>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/README.md>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/Makefile>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/test/misc/Makefile>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/test/misc/src/sha1test.c>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/test/misc/src/sha1_c.h>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/docs/wasm.md>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/src/vmir.h>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/src/vmir.c>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/src/vmir_vm.c>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/src/vmir_vm.h>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/src/vmir_mem.c>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/src/vmir_transform.c>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/src/vmir_jit_arm.c>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/src/vmir_libc.c>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/src/vmir_support.c>
  - <https://raw.githubusercontent.com/andoma/vmir/HEAD/src/vmir_wasm_parser.c>
  - <https://github.com/andoma/vmir/issues>
  - <https://github.com/andoma/vmir/issues/14>
  - <https://github.com/andoma/vmir/issues/9>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/andoma/vmir`) · [data/wave12/enrich/raw/github_com_andoma_vmir.json](../../../data/wave12/enrich/raw/github_com_andoma_vmir.json) (enrichment confidence 0.75)

</details>
