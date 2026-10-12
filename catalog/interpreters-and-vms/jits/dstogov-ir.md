# dstogov/ir (IR framework and JIT behind PHP 8.4+ JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Small C JIT back end (PHP 8.4+ JIT) that compiles about 40x faster than gcc -O2 for code about 4% slower.

| | |
|---|---|
| **Beats** | gcc -O2 (compile time; the README also reports the generated code speed against it) |
| **Claimed result** | Compile time relative to gcc -O2: oggenc 35.22, minilua 40.50, gzip 37.50, bzip2 49.67, average 40.69, geomean 40.34 ('IR framework provides code that is in average 5% slower, but does this up to \~40 times faster'). Generated code speed relative to gcc -O2: average and geomean 0.96, worst gzip 0.80 and bzip2 0.81, best hash 1.13 and matrix 1.12. |
| **Workload** | 18 programs (14 small benchmarks such as binary-trees, mandelbrot, nbody, hash, sieve plus oggenc, minilua, gzip, bzip2) compiled by clang to LLVM IR without LLVM optimization and then loaded, compiled and run by IR, against the same programs built by gcc -O2; compile time is reported for the four real applications. |
| **Metric** | compile-time |
| **Compiler and flags** | gcc -O2 (version not stated); inputs lowered by clang to LLVM IR with no LLVM optimizations (README example: clang -O -Xclang -disable-llvm-passes -c -emit-llvm -S); IR build flags not stated |
| **Adoption** | 507 stars, 45 forks; the JIT backend of PHP 8.4 and later (README: 'IR-based JIT integrated into PHP-8.4.0 and above') |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/dstogov/ir) · [benchmark](https://github.com/dstogov/ir) |

## Verdict

First-party README tables (last updated 26 Apr 2024): 18 C programs lowered by clang to LLVM IR without optimizations, loaded and JIT-compiled by IR (opt level not stated; the driver defaults to -O2) ran at a geomean 0.96 of gcc -O2 speed (0.80 gzip to 1.13 hash), and on oggenc, minilua, gzip and bzip2 IR compiled 35-50x faster than gcc -O2 (geomean 40.34). No CPU model, gcc version or benchmark scripts are published (bench/ holds only mandelbrot files), and gcc's time includes front-end work IR skipped.

## Use it when

- You are building a method or tracing JIT for an interpreter, query/expression engine or DSL in C or C++ and want code near gcc -O2 quality without shipping LLVM.
- Compile latency matters: hot functions or traces where LLVM -O2 compile time would eat the gain; the README reports 35-50x less compile time than gcc -O2 on oggenc, minilua, gzip and bzip2.
- Your targets are x86-64, 32-bit x86 or AArch64 on Linux, macOS, FreeBSD or Windows (all in CI).
- You need JIT plumbing beyond codegen: SNAPSHOT/GUARD side exits and exit groups for deoptimization, GDB JIT interface, Linux perf jitdump, graphviz dumps and textual IR save/load.
- You want a production-proven back end: PHP 8.4 and later ship it as their JIT.

## Skip it when

- Peak code quality matters more than compile time: the README shows gzip at 0.80 and bzip2 at 0.81 of gcc -O2 speed; no auto-vectorizer is documented (explicit vector types and EXTRACT/REPLACE/SPLAT/SHUFFLE ops were only added in 2026) and alias analysis is still on the TODO list.
- You need a stable, packaged API: IR_VERSION is 0.0.1, the README says it is 'not a stable finished product yet' and recommends embedding the sources, as PHP does.
- Your target is RISC-V or 32-bit ARM: no back end (open issues #168 and #91).
- You want a general C compiler: the C path is clang plus the optional LLVM loader ('partially compatible') or the unfinished RCC; long double is unsupported and by-value struct passing in registers is incomplete per TODO.
- You need the lowest possible compile latency for a baseline tier: copy-and-patch designs (WasmNow, PochiVM) or TPDE aim lower; none of them is compared against IR on the same workload.

## How it is fast

The IR is Sea-of-Nodes (Click) stored LuaJIT-style as one flat two-way array of nodes referenced by index (constants grow one way, instructions the other), so construction and passes touch compact memory with few allocations. Folding (constant folding, copy propagation, algebraic simplification and reassociation, CSE) runs on the fly during construction from declarative rules in ir_fold.h, hashed at build time. The pipeline is deliberately short: optional MEM2SSA, Wegman-Zadeck sparse conditional constant propagation, Click global code motion, topological local scheduling, max-munch tree-pattern instruction selection, linear-scan register allocation on SSA with second-chance bin packing (Wimmer), and DynASM emission straight into executable memory with no assembler or linker step.

## Compared with alternatives

Pick IR over Cranelift and TPDE when you want a small embeddable C library (no Rust toolchain, no LLVM) with SCCP, global code motion and SSA register allocation giving code near gcc -O2; pick TPDE when your front end already emits LLVM IR and LLVM -O0-class code compiled 10-20x faster is enough, and Cranelift for Rust or Wasm runtimes; over AsmJit and sljit, IR adds a real optimizer and global register allocation rather than instruction-level emission. The PHP JIT sibling's kostya numbers are for PHP 8.2.3, before PHP moved to IR, so they say nothing about this back end.

## Integration

| | |
|---|---|
| **Form** | source-drop (the Makefile also builds libir.a and an `ir` driver) |
| **Dependencies** | DynASM (vendored; generating ir_emit_x86.h or ir_emit_aarch64.h needs the bundled minilua compiled with a host C compiler at build time); libcapstone for the disassembler (ir_disasm.c is in the Makefile's libir.a object list and the driver links -lcapstone); LLVM optional (HAVE_LLVM=yes) for the LLVM IR loader |
| **Minimum toolchain** | C11 (a CI job builds with -std=c11); GCC, Clang and MSVC (win32/Makefile via nmake) in CI |
| **Platforms** | x86-64, x86 (32-bit) and AArch64 back ends; CI on Linux x86-64, i386 and aarch64, FreeBSD amd64, macOS arm64 and Intel (ASan/UBSan), Windows (windows-2022, MSVC) |
| **Thread safety** | not documented; compilation state lives in a per-function ir_ctx, but the x86 back end hands a file-static DynASM global-label array (dasm_labels) to every emit and the perf jitdump and GDB JIT hooks use process-wide state, so serialize compilations or audit before compiling from several threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the 40x: the compile-time table compares gcc -O2 from C source (preprocessing, parsing, SSA construction, optimization) with IR starting from clang output that, per the README pipeline of 26 Apr 2024 when the tables were last updated, had already been through LLVM's mem2reg, so front end and SSA construction sat outside IR's timed step; no CPU, gcc version, IR opt level or timing script is published, the numbers have not been re-measured since, and there is no comparison with the LLVM back end (llc), the natural baseline for a JIT code generator.
- Allocation results are not checked: ir_mem_malloc/ir_mem_realloc default to malloc/realloc and ir.c uses the result directly, so out-of-memory is a NULL dereference unless you #define ir_mem_\* to allocators that abort or longjmp (PHP maps them to emalloc/erealloc via ir_php.h).
- Release builds compile IR_ASSERT out and do not validate input; call ir_check() in debug builds. ir_jit_compile returns NULL silently when IR_OPT_FOLDING was set for -O0 or missing for -O1/-O2, and failures report only a ctx-&gt;status code. Builder macros assume a variable named ctx (_ir_CTX) and IR should be emitted in reverse post order or folding scope shrinks.
- Correctness fixes are still landing in 2025-2026, including miscompilations: #134 (diamond-to-COND produced invalid IR), #132 (COND regression), #153 (GCM hoisted PHI uses above LOOP_BEGIN), #145 (snapshot live range not extended to a GUARD) and #205 (guard reused flags across a fused memory binop, closed Sep 2026).

## Known shortcomings

- README numbers are first-party with no hardware, compiler versions or bench scripts; the about 40x compile-time win leaves out the clang front end and the README itself says the comparison is 'not completely fair'; generated code is about 4% slower than gcc -O2 on average.
- Enricher: README tables last updated 26 April 2024 (commit 3b35a1f) and never re-measured; at that date the pipeline ran clang -disable-llvm-passes plus opt mem2reg before IR, so the front end and SSA construction fall outside IR's timed compile but inside the gcc -O2 time, which flatters the about 40x. No CPU, gcc version, IR optimisation level or scripts; no llc/LLVM back-end column. ir_mem_malloc/realloc results are unchecked (OOM is a NULL dereference; PHP maps them to emalloc); the x86 emitter shares a file-static dasm_labels array and perf/GDB hooks are process-global with thread safety undocumented; release builds skip validation; miscompile fixes still landing 2025-2026 (#134, #132, #153, #145, #205). The PHP JIT entry's kostya numbers are PHP 8.2.3, pre-IR, so they say nothing about this backend.

## Caveats and trade-offs

First-party numbers with no CPU model, no compiler versions and no run script: bench/ in the repo holds only mandelbrot.c, mandelbrot.ir and mandelbrot.lua, so the tables are not reproducible from the repo. The README itself says the compile-time comparison 'is not completely fair' because gcc compiles C source while IR consumes precompiled LLVM IR, which leaves out the front-end. The win is compile time only; code quality is below gcc -O2 on average. The table header says 'Execution time ... (the more the better)', which is ambiguous, but the prose ('5% slower, \~20% slower in the worst case') and the 0.80 to 1.13 range read as speed relative to gcc. No LLVM compile-time comparison is on the page. The chart is hosted on dstogov.github.io and was not opened.

Lightweight graph-based SSA IR with APIs for construction, optimization passes, scheduling, register allocation and code generation; optional LLVM interop (convert IR to and from LLVM IR); also used as the backend of the experimental Rational C Compiler. Generates code on average about 4 to 5% slower than gcc -O2, up to about 20% slower in the worst case.

## Maintenance

Actively maintained (last commit 2026-10-05) and MIT-licensed, shipping inside PHP 8.4+ as its JIT, but the author calls it unfinished with no stable library or API versioning; the README benchmark tables date from 26 Apr 2024, cannot be reproduced from the repo, and their compile-time ratio flatters IR because gcc's front end and SSA construction are counted only on the gcc side.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section is first-party: compile time relative to gcc -O2 (oggenc 35.22, minilua 40.50, gzip 37.50, bzip2 49.67, geomean 40.34) and execution time relative to gcc -O2 (geomean 0.96) with no CPU model, compiler versions or run script; bench/ holds only mandelbrot.c, mandelbrot.ir and mandelbrot.lua.
- **Verifier notes:** All README numbers match the record (18 programs; execution average 0.96 and geomean 0.96 re-derived; compile-time average re-derives to 40.72 against the page's 40.69, geomean 40.37 against 40.34, rounding only). Shortcomings to record: first-party, no hardware or compiler versions, no benchmark scripts for the tables; compile-time comparison excludes the clang front end (README admits it is 'not completely fair'); generated code about 4-5% slower than gcc -O2 on average, worst gzip 0.80; chart on dstogov.github.io not opened (blocked host).
- **Fields the verifier corrected:** `stars_or_usage`
- **Shortcomings recorded by:** published bench scripts with hardware and versions; end-to-end compile-time comparison with scripts and hardware
- **Pages the verifier opened:**
  - <https://github.com/dstogov/ir>
  - <https://github.com/dstogov/ir/commits>
  - <https://github.com/dstogov/ir/tree/master/bench>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/README.md>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/dstogov/ir>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/README.md>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/Makefile>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/TODO>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir.h>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir_builder.h>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir_private.h>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir.c>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir_ra.c>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir_emit.c>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir_x86.dasc>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir_disasm.c>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir_gdb.c>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir_perf.c>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir_cpuinfo.c>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir_main.c>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/ir_php.h>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/bench/mandelbrot.c>
  - <https://raw.githubusercontent.com/dstogov/ir/HEAD/.github/workflows/push.yml>
  - <https://raw.githubusercontent.com/dstogov/ir/3b35a1f/README.md>
  - <https://github.com/dstogov/ir/issues?q=is%3Aissue>
  - <https://github.com/dstogov/ir/issues/154>
  - <https://github.com/dstogov/ir/commits/master>
  - <https://github.com/dstogov/ir/commits/master/README.md>
  - <https://github.com/dstogov/ir/commit/7b1c0c2>
  - <https://github.com/dstogov/ir/commit/be63e7c>
  - <https://github.com/dstogov/ir/commit/9ed616c>
  - <https://github.com/dstogov/ir/commit/3b35a1f>
  - <https://github.com/dstogov/ir/commit/1edb22b>
  - <https://github.com/dstogov/ir/commit/6e2aea0>
  - <https://github.com/dstogov/ir/tree/master/tools>
  - <https://github.com/dstogov/ir/tree/master/.github/workflows>
  - <https://github.com/dstogov/ir/tree/master/win32>
  - <https://github.com/dstogov/rcc>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/dstogov/ir`) · [data/wave12/enrich/raw/github_com_dstogov_ir.json](../../../data/wave12/enrich/raw/github_com_dstogov_ir.json) (enrichment confidence 0.8)

</details>
