# Mitey JIT (csjh/mitey-jit)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟢 active

> Experimental Arm64/macOS WebAssembly JIT with a fused validate-and-compile pass; starts big modules about 3x faster than Wasmtime.

| | |
|---|---|
| **Beats** | wasmtime, V8 (Node.js) |
| **Claimed result** | Snippet only (search-result relay of the post's tables, M1 MacBook Air). Startup, ms: SpiderMonkey 52.8 (unrolled JIT) and 65.8 (single-pass JIT) vs 183.3 (Wasmtime), 197.4 (Wasmtime single-pass), 66.3 (Node); esbuild 89.8 / 102.0 vs 209.9 / 243.6 / 75.3; Figma 159.7 / 198.8 vs 710.4 / 767.5 / 92.5 (Node faster on esbuild and Figma). Execution: the 'beats Node and Wasmtime on esbuild' result belongs to the single-pass (baseline) JIT, 3.126 s vs Wasmtime 3.316 s (1.06x) and Node 3.694 s (1.18x) (derived from page data); the unrolled JIT was 'too slow' for esbuild. Single-pass JIT loses to Wasmtime on SpiderMonkey score (347 vs 577) and Coremark (26616.0 vs 28260.4) but beats Node on both (300, 24853.7); the unrolled JIT scores 11.8 and 1326.6, about 21x below Wasmtime on Coremark (derived from page data). |
| **Workload** | Two Arm64 macOS JIT backends in one repo: the 'minimal' unrolled-interpreter JIT (backend/arm64/minimal.cpp) and the 'baseline' single-pass JIT (backend/arm64/baseline.cpp). The author's blog post 'A Tale of Three WebAssembly Runtimes' times startup (load, validate, instantiate) of SpiderMonkey, esbuild and Figma Wasm binaries with hyperfine, and execution speed on esbuild, SpiderMonkey and Coremark, against Wasmtime (default and single-pass) and Node. |
| **Metric** | other |
| **Hardware** | Apple M1 MacBook Air (snippet only); the README says only Arm64 on macOS is expected to work. |
| **Compiler and flags** | Clang only: relies on [[clang::musttail]], __attribute__((noinline)) and __attribute__((preserve_most)); optimization level not stated. |
| **Adoption** | 9 stars |
| **Last commit** | 2026-02-13 |
| **Links** | [repository](https://github.com/csjh/mitey-jit) · [benchmark](https://csjh.blog/posts/a-tale-of-three-wasm-runtimes/) |

## Verdict

Author's own blog post (csjh.blog, unreachable here; numbers relayed by search snippets) timed load+validate+instantiate with hyperfine on an M1 MacBook Air: SpiderMonkey 52.8 ms (unrolled JIT) and 65.8 ms (single-pass JIT) vs Wasmtime 183.3 ms, Wasmtime single-pass 197.4 ms and Node 66.3 ms; Figma 159.7 / 198.8 ms vs Wasmtime 710.4 ms and Node 92.5 ms. Execution (median of three): the single-pass JIT ran esbuild in 3.126 s vs Wasmtime 3.316 s and Node 3.694 s but lost to Wasmtime on Coremark and SpiderMonkey; compiler flags, Wasmtime and Node versions and Wasmtime cache settings are not known.

## Use it when

- Research or teaching: a compact, readable single-pass Wasm-to-Arm64 compiler (register cache, flag tracking, guard-page bounds checks) to study or borrow ideas from.
- Short-lived runs of very large Wasm binaries on an Apple Silicon Mac where compile latency dominates (author's numbers: SpiderMonkey starts in 65.8 ms vs 183.3 ms for Wasmtime).
- Comparing baseline-compiler design choices against Wasmtime Winch or Cranelift on the same Arm64 machine.

## Skip it when

- Anything shipped: no LICENSE file (all rights reserved by default), README says 'Not meant for production use', no build file in the repo.
- Linux, Windows or x86-64: the pager uses MAP_JIT, pthread_jit_write_protect_np and SIGBUS from macOS; backend/current.hpp errors out on x86.
- Peak-throughput workloads: the single-pass backend loses to Wasmtime on Coremark (26616 vs 28260) and the SpiderMonkey score (347 vs 577); only esbuild was faster (3.126 s vs 3.316 s, 1.06x).
- Modules that use SIMD (v128 is commented out in spec.hpp), threads or multiple concurrent instances/threads (one process-wide value stack and trap jmp_buf).
- Multi-tenant or embedding hosts: it installs process-wide SIGBUS and SIGILL handlers and reserves 16 GiB of address space per memory plus 400 bytes of executable space per code-section byte.

## How it is fast

Startup: validation and code generation happen in one linear pass per function (validate_and_compile), with no IR and no optimizer, which is why it beats Wasmtime's Cranelift compile on large binaries. The current 'baseline' backend is a single-pass compiler whose validation stack also tracks where each value lives (register, stack slot, immediate or condition flags): locals live in callee-saved registers, temporaries come from an LRU register cache, constants fold into immediates, and comparisons stay in flags until a branch consumes them. Bounds checks are removed by reserving 16 GiB of PROT_NONE address space per linear memory (guard regions on both sides, mprotect to grow), and stack overflow is caught by a guard page instead of per-push checks. The older 'minimal' backend emits a chain of calls into precompiled C++ handlers ([[clang::musttail]], preserve_most on cold trap paths), an unrolled interpreter.

## Compared with alternatives

Pick it over Wasmi or wasm3 only to study an Arm64 single-pass JIT design, since those are portable, licensed and maintained interpreters with near-zero startup; pick WAMR or Wasmtime itself for anything that must ship. Against wisp (another baseline compiler compared with Winch and Singlepass), mitey-jit's distinctive part is guard-page bounds checks and flag/register tracking during validation on Arm64.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond the macOS SDK (libkern/OSCacheControl.h, pthread JIT write protection); the test harness needs wast2json from WABT and Python 3 |
| **Minimum toolchain** | Clang with C++20 (uses [[clang::musttail]], preserve_most, std::ranges, std::bit_cast); no Makefile or CMake file is committed, so flags are not documented |
| **Platforms** | Arm64 macOS only (Apple Silicon) |
| **Thread safety** | Not thread-safe: Instance::initial_stack is one process-global 5 MB value stack, runtime::trap_buf is a global jmp_buf, and the heap registry used by the SIGBUS handler is a global vector. |
| **Drop-in for the baseline** | no |

## Gotchas

- Code-reading finding: the shipped main.cpp and test/executor.cpp both include backend/arm64/baseline.hpp, and nothing includes the minimal backend (minimal.cpp, backend/minimal/composer.hpp); backend/current.hpp includes a non-existent ./arm64.hpp. The post's 'unrolled JIT' numbers are therefore not reproducible from HEAD without restoring an older wiring.
- Branch-range checks are assert()-only and twice too loose: bcond/cbz/cbnz accept byte offsets below 2 MiB although the 19-bit field reaches only +-1 MiB (b/bl accept 256 MiB vs a +-128 MiB range), and a release build with NDEBUG drops them, so a branch that is out of range would silently wrap. The minimal backend's put_br encodes stack offsets in a 9-bit field with only a comment ('should be handled better when src/dst are higher than 1&lt;&lt;9'). Not observed failing; it bites only very large functions or deep value stacks.
- Trap handling is longjmp out of signal handlers (SIGBUS for guard regions, SIGILL for encoded trap instructions); the handlers are installed process-wide, and the heap registry never removes freed memories, so a later SIGBUS in a reused address range could be taken for a Wasm trap.
- The JIT region is reserved as 400 bytes per code-section byte plus 400 per function, and its size is stored in a uint32_t header, so code sections above about 10.7 MB unmap only part of the region on free; the instruction cache is never invalidated after writing code (sys_icache_invalidate is commented out; the source comment reasons fresh pages cannot hold stale lines).

## Known shortcomings

- The record credited the esbuild win to the wrong backend: the unrolled JIT is 'too slow' for esbuild and the single-pass baseline backend wins it, 3.126 s vs 3.316 s Wasmtime (1.06x) and 3.694 s Node. The single-pass backend loses to Wasmtime on SpiderMonkey (347 vs 577) and Coremark. No licence file, so reference only; Arm64 macOS only; no benchmark code in the repo and the blog is blocked here.
- Enricher: HEAD main.cpp and test/executor.cpp wire only the baseline backend; nothing includes the minimal backend and backend/current.hpp includes a missing ./arm64.hpp, so the blog's 'unrolled JIT' numbers are not reproducible from HEAD. Branch-range checks are assert-only and 2x too loose (bcond/cbz/cbnz allow under 2 MiB against a real +-1 MiB range), so an NDEBUG build would silently wrap out-of-range branches. One global 5 MB value stack, a global trap jmp_buf, process-wide SIGBUS/SIGILL handlers, no SIMD, no LICENSE, no build file. Codegen fixes landed January to February 2026 (i64.sub bug, br_table register overlap, fuzzing fixes) and the post date is unreadable, so it is unknown whether the numbers predate them.

## Caveats and trade-offs

Snippet only: csjh.blog is blocked by the egress proxy (EGRESS_BLOCKED); numbers come from WebSearch summaries of the post's tables. The record attributed the esbuild win to the unrolled JIT, but per the post it is the single-pass (baseline) backend, and only by 1.06x over Wasmtime; that backend is slower than Wasmtime on SpiderMonkey (347 vs 577) and Coremark (26616 vs 28260). The unrolled JIT wins only on startup and is about 21x slower than Wasmtime on Coremark execution (derived from page data). Node starts esbuild and Figma faster than both JITs. No benchmark code, compiler flags or build file (no Makefile or CMakeLists.txt at the repo root) are public; README says 'Not meant for production use'. No LICENSE file in the repository, so usability is reference. Arm64 macOS only; one machine.

Arm64 macOS only, Clang only, README says 'Not meant for production use' although it passes the Wasm spec tests. Uses mmap/mprotect for out-of-bounds handling and a guard-page stack. Repo holds two backends (minimal and baseline single-pass).

## Maintenance

Active (457 commits, last 2026-02-13, with many Jan-Feb 2026 codegen fixes such as 'fix i64sub bug', 'fix br_table to avoid temporary reg overlap' and 'fix validation bugs found by fuzzing', so the post's numbers may predate them; post date not readable here), but unlicensed and macOS-Arm64-only, so reference reading only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party blog post (csjh.blog, blocked here) relayed by WebSearch snippets: startup table (hyperfine, M1 MacBook Air) and execution table against Wasmtime, Wasmtime single-pass and Node. No benchmark code or build flags in the repo, so C.
- **Verifier notes:** Numbers relayed by search snippets match the record's startup figures (52.8 vs 183.3 ms SpiderMonkey); the esbuild win (3.126 vs 3.316 s Wasmtime, 3.694 s Node) belongs to the single-pass baseline backend, not the unrolled JIT, so claim and workload were corrected; tier stays C. Shortcomings: snippet-only first-party evidence, no license, Arm64 macOS only, execution win over Wasmtime on 1 of 3 workloads and only 1.06x.
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** licence, committed harness, independent run; reproducible build of the measured backend
- **Pages the verifier opened:**
  - <https://github.com/csjh/mitey-jit>
  - <https://github.com/csjh/mitey-jit/commits>
  - <https://github.com/csjh/mitey-jit/tree/main/backend>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/csjh/mitey-jit>
  - <https://github.com/csjh/mitey-jit/commits/main>
  - <https://github.com/csjh/mitey-jit/tree/main/backend>
  - <https://github.com/csjh/mitey-jit/tree/main/backend/arm64>
  - <https://github.com/csjh/mitey-jit/tree/main/backend/minimal>
  - <https://github.com/csjh/mitey-jit/tree/main/test>
  - <https://github.com/csjh/mitey-jit/tree/main/pager>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/README.md>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/module.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/module-impl.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/runtime.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/spec.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/interfacing.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/instance.cpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/pager/mac.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/pager/shared.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/backend/current.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/backend/shared.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/backend/arm64/baseline.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/backend/arm64/baseline.cpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/backend/arm64/minimal.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/backend/arm64/minimal.cpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/backend/arm64/reg_lru.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/backend/minimal/composer.hpp>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/test/run_tests.py>
  - <https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/test/executor.cpp>
  - https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/LICENSE (404)
  - https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/Makefile (404)
  - https://raw.githubusercontent.com/csjh/mitey-jit/HEAD/CMakeLists.txt (404)
  - <https://github.com/csjh?tab=repositories>
  - https://csjh.blog/posts/a-tale-of-three-wasm-runtimes/ (EGRESS_BLOCKED; WebSearch snippets only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/csjh/mitey-jit`) · [data/wave12/enrich/raw/github_com_csjh_mitey_jit.json](../../../data/wave12/enrich/raw/github_com_csjh_mitey_jit.json) (enrichment confidence 0.55)

</details>
