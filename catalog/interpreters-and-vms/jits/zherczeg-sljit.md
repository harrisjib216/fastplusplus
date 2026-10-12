# sljit

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> Portable low-level C JIT assembler; as pg_jitter's PostgreSQL backend it compiles queries in microseconds, not LLVM's tens of milliseconds.

| | |
|---|---|
| **Beats** | PostgreSQL LLVM JIT (llvmjit) in the pg_jitter shootout |
| **Claimed result** | pg_jitter BENCHMARKS_v18.md (PostgreSQL 18, ARM64 M1 Pro): execution SUM_int 68.090 vs llvmjit 42.401 ms and GroupBy_5agg 149.033 vs 99.530 ms (sljit slower than llvmjit at run time; slower than the interpreter on 27 of 108 queries, minimum 0.81x on LIKE_3wild). Compile time 0.04-0.46 ms vs llvmjit 17-2043 ms: 220-1,040x, median about 480x without the Wide1K rows (derived from page data); the Wide1K rows (21,000-29,000x) have sljit compiling almost nothing under pg_jitter 0.3.0's deform cap and are not comparable. |
| **Workload** | Machine-code generation for PostgreSQL expression evaluation through the pg_jitter sljit backend (PostgreSQL 18.1, 1M-row tables, thresholds forced to 0). |
| **Metric** | compile-time |
| **Hardware** | Apple M1 Pro, 32 GB RAM, Darwin 25.2.0 arm64 |
| **Compiler and flags** | PostgreSQL 18.1; C/C++ compiler and build flags for pg_jitter, sljit and PostgreSQL not stated on the page. Benchmark script: tests/bench_comprehensive.sh in vladich/pg_jitter. |
| **Adoption** | 1.1k stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/zherczeg/sljit) · [benchmark](https://github.com/vladich/pg_jitter/blob/master/bench/ARM64/0.3.0/BENCHMARKS_v18.md) |

## Verdict

pg_jitter's own suite on an Apple M1 Pro (PostgreSQL 18.1, 108 queries on 0.1-1M-row tables, JIT forced on, median of 3) shows its sljit backend spending 0.04-0.46 ms in JIT compilation versus 17-2,043 ms for PostgreSQL's LLVM JIT run at full optimization, and beating llvmjit's end-to-end time on 106 of 108 queries. Against the plain interpreter it is a median 1.11x faster but slower on 27 queries, so the win is compile latency, not code quality; the numbers measure pg_jitter's code generator on the vladich/sljit fork (upstream as of February 2026 plus two SIMD-opcode commits), not sljit alone.

## Use it when

- Translating bytecode, query expressions or regexes to machine code where compile latency matters more than peak code quality (per-query or per-pattern JIT).
- You need one code generator for many CPUs, including s390x, PowerPC, LoongArch, MIPS and 32-bit ARM/x86, which AsmJit does not cover.
- Embedding a small, dependency-free JIT in a C or C++ project; it can be built as a hidden all-in-one unit (SLJIT_CONFIG_STATIC) so its symbols never leak.
- Short-running database or filter workloads: in pg_jitter on an M1 Pro, sljit compile overhead was 0.04-0.46 ms per query versus 17-405 ms for PostgreSQL's LLVM JIT outside the 1000-column cases.

## Skip it when

- You want an optimizing compiler: there is no register allocation, inlining or loop optimization, so long-running hot loops are better served by LLVM, Cranelift or a tiered JIT.
- You need a high-level IR or C-like front end; consider MIR or a copy-and-patch compiler instead of hand-writing register-level LIR.
- You rely on debuggers, profilers or C++ exceptions unwinding through JIT frames: unwind/backtrace support is an open proposal (issue #356) and pg_jitter registers Win64 unwind data itself.
- Big-endian AArch64, PowerPC64 debug builds, ARMv6 and RVV SIMD have open correctness or crash issues (#376, #366, #188, #271).
- Functions needing more than 3 machine-word arguments through the ABI-compatible call path (documented limit).

## How it is fast

Compile speed comes from doing almost nothing beyond instruction selection: the LIR maps nearly one-to-one onto native instructions, with no SSA construction, optimization passes or register allocation (registers and stack are managed by the caller). It adds 'complex instructions' (compare-and-branch, select, function enter/return) that it can lower well per CPU without static analysis. In pg_jitter the speedup over llvmjit is mostly avoided LLVM optimization and emission time; the generated code runs close to PostgreSQL's interpreter speed (median about 1.11x faster) rather than beating LLVM-optimized code by much.

## Compared with alternatives

Pick sljit over AsmJit when you need targets beyond x86-64/AArch64 or the fastest possible emission (pg_jitter: about 1.5-6x less compile time than its AsmJit backend), and AsmJit when you want richer x86/ARM instruction coverage and slightly faster generated code on hash joins; pick TPDE or a copy-and-patch compiler (WasmNow, PochiVM) when your input is LLVM IR or Wasm rather than a bytecode you lower by hand.

## Integration

| | |
|---|---|
| **Form** | source-drop (compile sljit_src/sljitLir.c as one translation unit, or #include it with SLJIT_CONFIG_STATIC) |
| **Dependencies** | none beyond libc and the OS virtual-memory API (mmap/VirtualAlloc, pthreads or Windows mutex for the executable allocator) |
| **Minimum toolchain** | C99 compiler (C or C++); GNU Make for tests and examples, CMake only as a Windows/MSVC fallback |
| **Platforms** | x86 32/64, ARM 32 (v6, v7, Thumb2)/64, RISC-V 32/64, s390x, PowerPC 32/64, LoongArch 64, MIPS 32/64 (III, R1); an Alpha 64 backend was added in August 2026; SIMD and atomics only on some targets |
| **Thread safety** | Header states the compiler is thread-safe: use one sljit_compiler per thread; the shared executable-memory allocator takes a global mutex unless SLJIT_SINGLE_THREADED is set. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the measured numbers: the three Wide1K rows behind the headline 21,000-29,000x compile ratio show sljit compiling less (0.05 ms, below Wide300's 0.25 ms) with execution equal to the interpreter, consistent with the old pg_jitter deform cap that current source says 'incorrectly disabled profitable 1000-column sparse deform'; LLVM there compiled a full 1000-column deform. Without those rows the ratio is 220x to 1,040x, median about 480x (derived from page data).
- The benchmark gives llvmjit jit_inline_above_cost and jit_optimize_above_cost of 0 (full optimization every query) while pg_jitter backends get 500000; pg_jitter's sljit path also adds emission time to both generation_counter and emission_counter, so EXPLAIN's Total double-counts sljit emission (conservative for sljit).
- SLJIT_DEBUG and SLJIT_VERBOSE default to 1 in sljitConfig.h, so an unconfigured build carries assertions; set them to 0 (via sljitConfigPre.h) for production speed.
- Register types are strict: feeding an intptr_t register to a 32-bit op (or a float to a double op) is undefined and can crash on some CPUs (e.g. MIPS-64); valgrind needs --smc-check=all.

## Known shortcomings

- Indirect evidence: numbers come from the sljit column of pg_jitter's BENCHMARKS_v18.md (a patched fork vladich/sljit as a PostgreSQL JIT backend, not the library alone), compiler and flags unstated, ARM64 only on a single M1 Pro, and the harness forces LLVM inlining and optimization at cost 0. The README's '5-25% faster than the interpreter across all workloads' is contradicted: sljit is slower on 27 of 108 queries (minimum 0.81x on LIKE_3wild). Compile overhead 0.04-0.46 ms against llvmjit 17-2043 ms (derived from page data).
- Enricher: the three Wide1K rows behind the 21,000-29,000x headline compile ratio have sljit compiling almost nothing (0.05 ms, less than Wide300's 0.25 ms) and running at interpreter speed, matching the old pg_jitter deform cap that current source says 'incorrectly disabled profitable 1000-column sparse deform'; without Wide1K the compile advantage is 220-1,040x, median about 480x (derived). pg_jitter_sljit.c adds emission time to both generation_counter and emission_counter, so EXPLAIN totals double-count it (against sljit). Upstream defaults SLJIT_DEBUG=1 and SLJIT_VERBOSE=1; the vladich/sljit fork is upstream as of February 2026 plus 2 SIMD commits; open crash and miscompile issues #376, #366, #271.

## Caveats and trade-offs

Indirect evidence: the numbers measure pg_jitter's sljit backend (pg_jitter's own code generator emitting through sljit), not the sljit library alone, and the sljit repo carries no benchmark of its own. pg_jitter's README tells users to build the patched fork vladich/sljit ('bug fixes, extra SIMD opcodes, memory management improvements'), so the measured code may not be upstream zherczeg/sljit. The harness runs llvmjit with jit_inline_above_cost=0 and jit_optimize_above_cost=0 (full LLVM inlining and optimization on every query) while the pg_jitter backends get 500000, which maximizes LLVM's compile time; PostgreSQL's defaults would skip LLVM optimization on cheap queries. With all thresholds at 0, LLVM compile cost dominates the end-to-end totals. Some LIKE/regex wins come from PCRE2 and StringZilla, not sljit codegen. Single machine, ARM64 only (x86_64 results 'TBD'), median of 3 runs, first-party pg_jitter numbers. The baseline is PostgreSQL's LLVM JIT, not one of the category baselines (PyPy, LuaJIT, V8, HotSpot). [retier] Indirect evidence: a patched vladich/sljit fork (upstream as of February 2026 plus 2 SIMD commits) as a pg_jitter backend, not the library alone; compiler and flags unstated, ARM64 only on a single M1 Pro, and the harness forces LLVM inlining and optimization at cost 0. The Wide1K rows reflect the old deform cap that current pg_jitter source calls incorrect. pg_jitter_sljit.c adds emission time to both generation_counter and emission_counter, so EXPLAIN totals double-count it. Upstream defaults SLJIT_DEBUG=1 and SLJIT_VERBOSE=1; open crash and miscompile issues #376, #366, #271.

Low-level stack-less JIT with a platform-independent API (x86, ARM, RISC-V, s390x, PowerPC, LoongArch, MIPS); you write the code generator yourself (no optimizer); used by PCRE2.

## Maintenance

Actively maintained (last commit 2026-09-30, 886 commits, 1.1k stars, 16 open issues), BSD-2-Clause and dependency-free, so it is easy to vendor; the version macro still reads 0.95 (pre-1.0) and the repo keeps an API_CHANGES log, so pin a commit when vendoring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The pg_jitter v18 page (generated by tests/bench_comprehensive.sh, public) times pg_jitter's sljit backend against PostgreSQL's llvmjit and the interpreter on an Apple M1 Pro, but compiler and build flags are not stated and it does not say whether upstream sljit or the patched vladich/sljit fork was built, so not A. The measurement comes from pg_jitter's own first-party suite (210 stars, not a well-known independent benchmark) and it measures the integration rather than sljit alone, so not B.
- **Verifier notes:** Numbers in the record are on the page and in the correct sljit column; the record's metric is compile-time, so I added the page's compile-overhead table (sljit 0.04-0.46 ms vs llvmjit 17-2043 ms) and flagged that the README's '5-25% faster than the interpreter across all workloads' claim is contradicted (sljit slower on 27 of 108 queries). Metadata checks out on github.com: 1.1k stars, BSD-2-Clause (Simplified BSD LICENSE file), not a fork, not archived, last commit 2026-09-30 (active). Main shortcomings: indirect evidence through pg_jitter, possibly the patched fork, and the LLVM side is forced to full optimization. sljit is not on an earlier wave's verified list (it was only mentioned as PCRE2's bundled JIT in wave 1), so this is not a duplicate; pg_jitter itself is a separate record in this wave.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/vladich/pg_jitter/blob/master/bench/ARM64/0.3.0/BENCHMARKS_v18.md>
  - <https://github.com/vladich/pg_jitter>
  - <https://github.com/vladich/pg_jitter/tree/master/tests>
  - <https://github.com/vladich/pg_jitter/blob/master/tests/bench_comprehensive.sh>
  - <https://github.com/vladich/pg_jitter/blob/master/build.sh>
  - <https://github.com/zherczeg/sljit>
  - <https://github.com/zherczeg/sljit/commits>
  - <https://github.com/zherczeg/sljit/blob/master/LICENSE>
  - <https://github.com/vladich/sljit>
- **Sources the enricher read:**
  - <https://github.com/zherczeg/sljit>
  - <https://raw.githubusercontent.com/zherczeg/sljit/HEAD/README.md>
  - <https://raw.githubusercontent.com/zherczeg/sljit/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/zherczeg/sljit/HEAD/sljit_src/sljitLir.h>
  - <https://raw.githubusercontent.com/zherczeg/sljit/HEAD/sljit_src/sljitConfig.h>
  - <https://raw.githubusercontent.com/zherczeg/sljit/HEAD/sljit_src/sljitConfigInternal.h>
  - <https://raw.githubusercontent.com/zherczeg/sljit/HEAD/sljit_src/sljitUtils.c>
  - <https://github.com/zherczeg/sljit/tree/master/docs>
  - <https://github.com/zherczeg/sljit/tree/master/docs/general>
  - <https://raw.githubusercontent.com/zherczeg/sljit/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/zherczeg/sljit/HEAD/docs/general/introduction.md>
  - <https://raw.githubusercontent.com/zherczeg/sljit/HEAD/docs/general/architecture.md>
  - <https://raw.githubusercontent.com/zherczeg/sljit/HEAD/docs/general/getting-started/setup.md>
  - <https://raw.githubusercontent.com/zherczeg/sljit/HEAD/docs/general/use-cases/overview.md>
  - <https://raw.githubusercontent.com/zherczeg/sljit/HEAD/docs/general/use-cases/bytecode-interpreters.md>
  - <https://github.com/zherczeg/sljit/commits/master>
  - <https://github.com/zherczeg/sljit/issues>
  - <https://github.com/vladich/sljit>
  - <https://github.com/vladich/sljit/commits>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/README.md>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/bench/ARM64/0.3.0/BENCHMARKS_v18.md>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/tests/bench_comprehensive.sh>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/tests/parse_explain_json.py>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/build.sh>
  - <https://github.com/vladich/pg_jitter/tree/master/src>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/src/pg_jitter_sljit.c>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/src/pg_jitter_deform_jit.c>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/src/pg_jitter_common.c>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/src/pg_jitter_common.h>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/zherczeg/sljit`) · [data/wave12/enrich/raw/github_com_zherczeg_sljit.json](../../../data/wave12/enrich/raw/github_com_zherczeg_sljit.json) (enrichment confidence 0.55)

</details>
