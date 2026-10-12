# csjh wasm-interpreter (in-place WebAssembly interpreter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Small MIT C++20 in-place WebAssembly interpreter: validate and run bytecode directly, starting large modules about 5x faster than Wasmtime.

| | |
|---|---|
| **Beats** | wasmtime |
| **Claimed result** | Snippet only (search-result relay of the post's startup table, hyperfine on an M1 MacBook Air, ms): SpiderMonkey 35.4 (in-place interpreter) vs 183.3 (Wasmtime) vs 197.4 (Wasmtime single-pass) vs 66.3 (Node), about 5.2x faster than Wasmtime (derived from page data); esbuild 64.7 vs 209.9 (Wasmtime) vs 75.3 (Node); Figma 108.3 vs 710.4 (Wasmtime) vs 92.5 (Node, faster than the interpreter). Validation alone takes 24.8 ms on SpiderMonkey. Execution speed is far slower than Wasmtime: Coremark 749.6 vs 28260.4 (higher is better, about 38x slower, derived from page data), SpiderMonkey score about 2.83 vs 577, esbuild 'too slow' to report. |
| **Workload** | Startup (load, validate and instantiate) of a large module (SpiderMonkey compiled to Wasm) in a tail-call in-place interpreter, versus Wasmtime, as reported in the author's blog post 'A Tale of Three WebAssembly Runtimes'. |
| **Metric** | startup |
| **Hardware** | Apple M1 MacBook Air (snippet only: the post says startup was timed with hyperfine on an M1 MacBook Air). |
| **Compiler and flags** | Not stated for the blog numbers. The repo Makefile builds with clang++ (-std=c++20; release target adds -O2). |
| **Adoption** | 6 stars |
| **Last commit** | 2025-07-15 |
| **Links** | [repository](https://github.com/csjh/wasm-interpreter) · [benchmark](https://csjh.blog/posts/a-tale-of-three-wasm-runtimes/) |

## Verdict

Author's own blog post (csjh.blog, blocked here; numbers relayed by search snippets) timed load+validate+instantiate with hyperfine on an M1 MacBook Air: SpiderMonkey 35.4 ms vs Wasmtime 183.3 ms, Wasmtime single-pass 197.4 ms and Node 66.3 ms; esbuild 64.7 vs 209.9 ms (Node 75.3); Figma 108.3 vs 710.4 ms (Node 92.5, faster). Validation alone is 24.8 ms on SpiderMonkey; compiler flags, the driver used and Wasmtime's cache settings are not known, and execution is 38x or more slower than Wasmtime.

## Use it when

- Short-lived invocations of large modules where compile latency dominates and little code runs (author's numbers on an M1: SpiderMonkey module up and instantiated in 35.4 ms vs 183.3 ms for Wasmtime).
- Reading or vendoring a compact, MIT-licensed C++ example of an in-place Wasm interpreter with tail-call dispatch (about 4,300 lines in six source files: module.cpp, instance.cpp, main.cpp and three headers).
- Embedding pure-compute modules with a few custom host imports (no WASI) in a C++ program where portability of plain C++20 matters more than speed.

## Skip it when

- Any compute-heavy run: the author's numbers put it at Coremark 749.6 vs 28260.4 for Wasmtime (about 38x slower), SpiderMonkey score about 2.83 vs 577, and esbuild too slow to report.
- Programs that need WASI, SIMD (v128 is commented out in spec.hpp), threads or 64-bit memories: none are implemented.
- Deeply recursive code: the control stack holds 1000 entries (MAX_DEPTH) shared by every active call and every entered block, after which it traps 'call stack exhausted'.
- Production use: stale since 2025-07-15, 6 stars, README is a single heading with no documentation, and the very largest binary (Figma) starts faster under Node (92.5 vs 108.3 ms).

## How it is fast

Startup is cheap because there is no compile step: one validation pass per function records branch targets in side tables (std::unordered_map from block/if bytecode address to its end or else position), in the style of Ben Titzer's in-place interpreter, and instantiation only allocates stacks and copies those tables. Dispatch is a 256-entry handler table with [[clang::musttail]] tail calls between handlers (threaded code without computed goto), the hot state (instance, bytecode pointer, value stack, control stack) travels in argument registers, and cold paths such as multi-value branch moves and error raising are noinline preserve_most functions.

## Compared with alternatives

For startup alone, Wasmi with lazy translation and the DLR-FT wasm-interpreter have independent wasmi-benchmarks numbers and are maintained, and wasm3 or WAMR's fast interpreter are far faster at execution; pick this one only when you want a small MIT C++ in-place interpreter to read or vendor, with your own host imports and no WASI.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C++ standard library only); the spec-test runner needs wast2json and Python 3 |
| **Minimum toolchain** | C++20; the Makefile uses clang++ and warns that Clang 15 and below have incomplete C++20 support; dispatch relies on [[clang::musttail]] (the Makefile passes -Wno-attributes, so a compiler that ignores the attribute loses the tail-call guarantee); commits mention GCC fixes |
| **Platforms** | Not documented; plain C++20 with no OS-specific calls seen, but uses POSIX ssize_t; memory is calloc/realloc with explicit bounds checks, 32-bit addresses only |
| **Thread safety** | Not documented. Each Instance owns its value stack, control stack and mutable call frame, so use one thread per Instance; no shared mutable globals were seen apart from read-only handler tables. |
| **Drop-in for the baseline** | no |

## Gotchas

- Build-file flaw: plain make builds the debug target (-Og -g3 -DWASM_DEBUG -fsanitize=address,undefined; WASM_DEBUG prints every executed instruction and the stack to stderr), and 'make release' fails with "No rule to make target 'release'" because release only carries a target-specific -O2 (checked with make -n). An optimized build needs something like make executable CFLAGS="-std=c++20 -O2"; which build the blog numbers used is unknown.
- The published driver cannot reproduce the post's startup numbers: main.cpp supplies only env.clock_ms and calls an export named 'run' (a Coremark-style driver), and there is no WASI code in the repo, so the SpiderMonkey, esbuild and Figma binaries would stop at an 'unknown import' link error during instantiation. The harness used for the post is not public.
- Each executed block and if does a std::unordered_map lookup keyed by bytecode address, and loop re-decodes its blocktype on every iteration; every Instance deep-copies both maps from the Module, so instantiation cost and memory grow with the number of blocks.
- Linear memory is calloc/realloc'd (grow copies; calloc failure is not checked) and the bounds check computes current \* PAGE_SIZE in 32 bits, so a memory at the full 65536 pages wraps to 0 and every access traps. Traps and validation failures are C++ exceptions (trap_error, validation_error, link_error).

## Known shortcomings

- Startup-only win: 35.4 ms vs 183.3 ms for Wasmtime on the SpiderMonkey module, but execution is about 38x slower than Wasmtime on Coremark (749.6 vs 28,260.4) and Node starts the Figma module faster (92.5 vs 108.3 ms). No benchmark code in the repo; numbers rest on WebSearch snippets of the author's blog tables (hyperfine, M1 MacBook Air), since csjh.blog is blocked here.
- Enricher: 'make release' fails (No rule to make target 'release') and plain make produces an -Og ASan/UBSan WASM_DEBUG build. HEAD main.cpp supplies only env.clock_ms and calls export 'run'; there is no WASI in the repo, so the SpiderMonkey, esbuild and Figma startup numbers need an unpublished driver. block/if do an unordered_map lookup on each run and each Instance deep-copies both maps; the control stack is capped at 1000 entries; 32-bit current\*PAGE_SIZE wraps at 65536 pages.

## Caveats and trade-offs

Snippet only: csjh.blog is blocked by the egress proxy (EGRESS_BLOCKED), so the numbers come from WebSearch summaries of the post's tables, not from the page itself. The repo README is a single heading and holds no benchmark code. The win is startup only (load, validate, instantiate): the interpreter is roughly 38x slower than Wasmtime on Coremark execution (derived from page data), about 200x lower on the SpiderMonkey score, and too slow to finish esbuild; Node starts the largest binary (Figma) faster (92.5 vs 108.3 ms). Wasmtime startup here includes its up-front Cranelift compile of the whole module (cache settings unknown); Wasmtime's own Pulley interpreter was not compared. Single machine (M1), compiler and flags of the measured build unknown. Last commit 2025-07-15 (merged trunc_sat spec fix), so stale.

Interpreter only, so peak throughput is expected to be far below Wasmtime's Cranelift JIT; the win is cheap startup because no compilation pass is needed. Small hobby codebase (C++ with instance.cpp, module.cpp, main.cpp), no WASI breadth claimed.

## Maintenance

Stale (244 commits, last a merged saturating-truncate fix on 2025-07-15; the author's later work is mitey-jit) but MIT-licensed and small enough to vendor; no documentation, no WASI, and the Makefile's release target is broken.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party blog post by the author (csjh.blog, blocked here); WebSearch snippets of the post relay a startup table (hyperfine, M1 MacBook Air) with the in-place interpreter at 35.4 ms versus Wasmtime 183.3 ms on SpiderMonkey, matching the record. No benchmark code, compiler version or exact build flags are public (repo Makefile release target is clang++ -O2 -std=c++20, but the post's build is not known), so C.
- **Verifier notes:** Startup claim (35.4 vs 183.3 ms SpiderMonkey) matches the post's table as relayed by search snippets; tier stays C. Shortcomings: snippet-only evidence from a blocked first-party blog, no benchmark code in repo, startup-only win while execution is about 38x slower than Wasmtime on Coremark, and Node beats it on startup of the largest binary (Figma).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** committed benchmark harness and an independent run; published driver and release build target
- **Pages the verifier opened:**
  - <https://github.com/csjh/wasm-interpreter>
  - <https://github.com/csjh/wasm-interpreter/commits>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/README.md>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/csjh/wasm-interpreter>
  - <https://github.com/csjh/wasm-interpreter/commits/main>
  - <https://github.com/csjh/wasm-interpreter/branches/all>
  - <https://github.com/csjh/wasm-interpreter/tree/main/test>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/README.md>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/Makefile>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/instance.hpp>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/instance.cpp>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/module.hpp>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/module.cpp>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/spec.hpp>
  - <https://raw.githubusercontent.com/csjh/wasm-interpreter/HEAD/.gitignore>
  - <https://github.com/csjh?tab=repositories>
  - https://csjh.blog/posts/a-tale-of-three-wasm-runtimes/ (EGRESS_BLOCKED; WebSearch snippets only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/csjh/wasm-interpreter`) · [data/wave12/enrich/raw/github_com_csjh_wasm_interpreter.json](../../../data/wave12/enrich/raw/github_com_csjh_wasm_interpreter.json) (enrichment confidence 0.6)

</details>
