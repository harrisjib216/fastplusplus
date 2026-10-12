# AsmJit

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib` · 🟡 stale

> C++ machine-code emitter for x86/x86-64/AArch64 with optional register allocator; compiles PostgreSQL expressions about 200x faster than LLVM JIT.

| | |
|---|---|
| **Beats** | PostgreSQL LLVM JIT (llvmjit) in the pg_jitter shootout |
| **Claimed result** | pg_jitter benchmark page (https://github.com/vladich/pg_jitter/blob/master/bench/ARM64/0.3.0/BENCHMARKS_v18.md), JIT compilation overhead from EXPLAIN JSON: SUM_int llvmjit 22.263 ms vs asmjit 0.109 ms; GroupBy_5agg llvmjit 45.5 ms vs asmjit 0.245 ms (about 200x less compile time, derived from page data). Query time with JIT forced on: SUM_int llvmjit 68.090 ms vs asmjit 42.201 ms (interpreter 44.859 ms); GroupBy_5agg llvmjit 149.033 ms vs asmjit 98.079 ms (interpreter 117.367 ms). pg_jitter README: AsmJit compile 'hundreds of microseconds' vs LLVM 'tens to hundreds of milliseconds'; its 'up to 32% faster' for AsmJit on wide-row/deform-heavy queries is relative to the PostgreSQL interpreter, not to LLVM. |
| **Workload** | Machine-code generation for PostgreSQL expression evaluation through the pg_jitter AsmJit backend (PostgreSQL 18.1, 1M-row tables, thresholds forced to 0). |
| **Metric** | compile-time |
| **Hardware** | Apple M1 Pro, 32 GB RAM |
| **Compiler and flags** | PostgreSQL 18.1; build flags not stated. |
| **Adoption** | 4.6k stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/asmjit/asmjit) · [benchmark](https://github.com/vladich/pg_jitter/blob/master/bench/ARM64/0.3.0/BENCHMARKS_v18.md) |

## Verdict

pg_jitter 0.3.0 on PostgreSQL 18.1, Apple M1 Pro, macOS, build flags not stated (2026-03-24): JIT compile time from EXPLAIN JSON was 0.109 ms for the AsmJit backend vs 22.263 ms for llvmjit on SUM_int and 0.245 vs 45.5 ms on GroupBy_5agg (about 200x, derived from page data), with LLVM forced to full optimization and inlining. Query time with JIT forced on was 42.2 vs 68.1 ms; without LLVM's compile time execution is about 42.1 vs 45.8 ms.

## Use it when

- Compile latency matters more than peak code quality: per-query or per-expression JIT in databases (pg_jitter compiles typical PostgreSQL expressions in 0.1-0.4 ms vs 20-60 ms for llvmjit), regex or filter engines, emulators and DSP kernels generated at run time.
- You need full x86/x86-64 instruction coverage including SIMD up to AVX-512, or AArch64 with NEON, from C++ without pulling in LLVM.
- You want a register allocator and calling-convention handling (Compiler) but not an optimizer, because your front end already knows what code it wants.
- Cross-generating x86 or AArch64 code from another host, including from Emscripten with ASMJIT_NO_JIT.

## Skip it when

- Long-running hot code where an optimizing back end pays for itself; AsmJit does no instruction selection or optimization across what you emit.
- Targets other than x86, x86-64 and AArch64: there is no AArch32, RISC-V, PowerPC or s390x backend (core.h lists only X86/X86_64 and AArch64); sljit or MIR cover more architectures.
- When the absolute lowest compile time is the goal: on the pg_jitter PG18 page sljit compiles in roughly half AsmJit's time on almost every query (SUM_int 0.052 vs 0.109 ms), and MIR beats it on the 100- and 300-column deform queries.
- Projects that need a stable API or vendor support: the maintainer opened issue #507 'DEVELOPMENT SUSPENDED' (2026-01-21: no support, only trivial PRs), and API-breaking renames still landed in 2025-09 and 2026-09.
- Teams without assembly-level expertise: correctness of generated code, ABI details outside the Compiler's model and debugging with the Logger are on you.

## How it is fast

Instructions are encoded straight from typed operands using a generated instruction database, with no SSA construction or optimization pipeline, which is where LLVM spends its tens of milliseconds. The Compiler layer adds only a node list and a register-allocation pass (ra_pass/ra_local), and node memory comes from arena allocators that are reset rather than freed. Executable memory comes from JitAllocator, which hands out pieces of large mapped blocks (64 kB default) tracked by bit vectors and an RB tree, with optional dual mapping where W^X is enforced.

## Compared with alternatives

Pick AsmJit over sljit when you want C++ with full x86 SIMD or AArch64 NEON coverage and a register allocator rather than sljit's portable low-level IR (sljit compiles about 2x faster in the same shootout and runs on more architectures); pick TPDE instead when your input is already LLVM IR, and use pg_jitter itself (its README favours the sljit backend) if the goal is just faster PostgreSQL JIT.

## Integration

| | |
|---|---|
| **Form** | static lib, shared lib, or source-drop (ASMJIT_EMBED / ASMJIT_STATIC) |
| **Dependencies** | none beyond libc (pthread, and librt for shm_open on some Linux libcs) |
| **Minimum toolchain** | C++17 per the build docs in core.h, but the current CMakeLists.txt needs CMake 3.24 and sets cxx_std_20 as a PUBLIC feature; CI-tested with GCC 9+, Clang 14+ and VS2022 |
| **Platforms** | x86, x86-64 and AArch64 code generation (including arm64e pointer authentication since v1.23); hosts Linux, Windows 7+, macOS, FreeBSD, NetBSD, OpenBSD; Emscripten only with ASMJIT_NO_JIT |
| **Thread safety** | JitAllocator alloc/release are documented thread-safe (internal lock), JitAllocator::reset is not; CodeHolder and emitters carry no thread-safety guarantee in the docs read, so use one per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Evidence is indirect and partly not like for like: the numbers time pg_jitter's own AsmJit backend inside PostgreSQL with jit_inline_above_cost and jit_optimize_above_cost forced to 0, so LLVM pays full inlining and optimization on every query. On the Wide1K rows (llvmjit 983-2043 ms vs asmjit 0.08-0.18 ms) the benchmarked pg_jitter 0.3.0 skipped deform JIT: its source now says the old cache-derived cap 'incorrectly disabled profitable 1000-column sparse deform', and asmjit execution there equals the interpreter (0.97-0.98x). Do not quote those rows.
- pg_jitter's AsmJit backend creates a fresh JitRuntime per compiled expression (struct AsmjitCode holds its own runtime, default 64 kB block), so the measured 0.1-0.3 ms includes per-expression executable-memory setup; a shared runtime would probably narrow the gap to sljit, but that is not measured.
- The API changes often: the 2025-09-06 refactor renamed every camelCase function to snake_case (for example newIntPtr to new_gp_ptr) and Zone to Arena, and 2026-09-04 renamed the 'support' library to 'axl' and ASMJIT_ARCH_\* macros to ASMJIT_TARGET_ARCH_\*; pin a commit. Static users must define ASMJIT_STATIC in every translation unit that includes AsmJit.
- No exceptions are used: functions return Error codes, so install an ErrorHandler and Logger (the docs recommend both). AArch64 Compiler fixes landed after the 2026-03-24 benchmark (x30/lr use during function calls 2026-09-06, new_gpw width 2026-03-26, FMOV encoding 2025-12-09), and issue #83 (Win64 vector arguments passed indirectly) has been open since 2015.

## Known shortcomings

- Evidence is indirect: pg_jitter's AsmJit backend against PostgreSQL's llvmjit, not the library itself; the 'up to 32%' figure is against the interpreter, not LLVM, and sljit compiles faster than AsmJit on the same page. Compile time SUM_int 0.109 ms vs llvmjit 22.263 ms.
- Enricher: the pg_jitter Wide1K rows are not like for like (pg_jitter 0.3.0 skipped deform JIT there, so asmjit runs at 0.97-0.98x the interpreter while llvmjit pays 983-2043 ms compile); pg_jitter creates a fresh JitRuntime per expression (64 kB default block) and counts that setup as compile time; MIR beats AsmJit compile time on Wide100 and Wide300 and sljit is about 2x faster on almost every query. No AArch32 backend (x86, x86-64, AArch64 only); the maintainer opened issue #507 'DEVELOPMENT SUSPENDED' on 2026-01-21 although commits continue to v1.23 (2026-09-22); CMake now requires C++20 while the docs say C++17.

## Caveats and trade-offs

Indirect evidence: the numbers measure pg_jitter's AsmJit backend (pg_jitter's own code generator design, no optimization passes) inside PostgreSQL, not AsmJit as a library, and the AsmJit repo carries no benchmark against LLVM. The harness forces jit_above_cost, jit_inline_above_cost and jit_optimize_above_cost to 0, so LLVM pays full optimization and inlining on every query and its compile time is inside the measured execution time; execution-only, SUM_int is about 45.8 ms llvmjit vs 42.1 ms asmjit (derived from page data). On the same page the sljit backend compiles about 2x faster than AsmJit (SUM_int 0.052 ms vs 0.109 ms), so AsmJit is not the fastest emitter there. One machine (Apple M1 Pro, macOS), ARM64 only (x86_64 marked TBD), compiler and flags not stated, dated 2026-03-24. Baseline is PostgreSQL's LLVM JIT, not a listed baseline. [retier] Indirect evidence: pg_jitter's AsmJit backend against PostgreSQL's llvmjit, not the library itself; the 'up to 32%' figure is against the interpreter. Do not quote the Wide1K rows: pg_jitter 0.3.0 skipped deform JIT for them, so asmjit runs at 0.97-0.98x the interpreter while llvmjit pays 983-2043 ms of compile time. pg_jitter creates a fresh JitRuntime (64 kB block) per expression and counts it as compile time. MIR compiles faster on Wide100 and Wide300 and sljit is about 2x faster on almost every query. Backends: x86, x86-64, AArch64 only (no AArch32). Maintainer opened issue #507 'DEVELOPMENT SUSPENDED' on 2026-01-21; commits continue to v1.23 (2026-09-22). CMake requires C++20 (docs still say C++17).

Assembler-level C++ API for x86, x86-64, AArch32 and AArch64 with a register allocator in the Compiler layer; no mid-level optimizer; the pg_jitter AsmJit backend supports only arm64 and x86_64.

## Maintenance

Zlib-licensed and easy to vendor, with maintainer commits through 2026-09-22 (v1.23), but the maintainer declared development suspended for lack of funding in issue #507 (still open), so treat it as sporadically maintained by one author with no support commitment rather than 'active'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Only evidence is pg_jitter's own benchmark page (bench/ARM64/0.3.0/BENCHMARKS_v18.md, harness tests/bench_all_backends.sh) timing pg_jitter's AsmJit backend against PostgreSQL's llvmjit on an Apple M1 Pro; compiler and build flags are not stated and the AsmJit repo has no LLVM comparison of its own, so this indirect first-party-style measurement stays at C.
- **Verifier notes:** Numbers on the record match the pg_jitter PG18 page; I added the page's compile-time table since the metric is compile-time, and fixed the 'up to 32%' claim, which is against the interpreter. Metadata checked: Zlib, 4.6k stars, 597 forks, last commit 2026-09-22, active. Shortcomings: indirect evidence via a third-party PostgreSQL extension, LLVM forced to full optimization on every query, sljit beats AsmJit on compile time on the same page, ARM64-only single machine.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `maintenance_status`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/bench/ARM64/0.3.0/BENCHMARKS_v18.md>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/README.md>
  - <https://github.com/vladich/pg_jitter>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/tests/bench_all_backends.sh>
  - <https://github.com/asmjit/asmjit>
  - <https://github.com/asmjit/asmjit/commits/master>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/asmjit/asmjit>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/README.md>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/asmjit/core.h>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/asmjit/core/build_defs.h>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/asmjit/core/jit_runtime.h>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/asmjit/core/jit_allocator.h>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/asmjit/core/jit_allocator.cpp>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/asmjit/core/error_handler.h>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/asmjit/core/compiler.h>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/asmjit-testing/bench/asmjit_bench_overhead.cpp>
  - <https://raw.githubusercontent.com/asmjit/asmjit/HEAD/asmjit-testing/bench/asmjit_bench_codegen.cpp>
  - <https://github.com/asmjit/asmjit/tree/master/asmjit/core>
  - <https://github.com/asmjit/asmjit/tree/master/asmjit-testing/bench>
  - <https://github.com/asmjit/asmjit/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/asmjit/asmjit/issues/507>
  - <https://github.com/asmjit/asmjit/commits/master>
  - <https://github.com/vladich/pg_jitter/blob/master/bench/ARM64/0.3.0/BENCHMARKS_v18.md>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/README.md>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/tests/bench_all_backends.sh>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/tests/bench_comprehensive.sh>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/tests/parse_explain_json.py>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/src/pg_jitter_asmjit.cpp>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/src/pg_jitter_asmjit_arm64.inc>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/src/pg_jitter_common.c>
  - <https://github.com/vladich/pg_jitter/tree/master/tests>
  - <https://github.com/vladich/pg_jitter/tree/master/src>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/asmjit/asmjit`) · [data/wave12/enrich/raw/github_com_asmjit_asmjit.json](../../../data/wave12/enrich/raw/github_com_asmjit_asmjit.json) (enrichment confidence 0.75)

</details>
