# Type-V

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟡 stale

> Hobby register-based bytecode VM for the Type-C language; beats CPython 3.12 on three microbenchmarks, roughly matches node --jitless.

| | |
|---|---|
| **Beats** | V8 (node --jitless) and CPython 3.12 |
| **Claimed result** | Mean execution time from the README bar charts: array allocation + sum Type-V 0.828s vs node --jitless 0.892s (about 1.08x faster) and python3 1.307s (about 1.58x faster); fib(40) Type-V 9.91s vs node --jitless 8.32s (about 1.19x slower) and python3 11.07s (about 1.12x faster); member access Type-V 0.689s vs node --jitless 0.494s (about 1.39x slower) and python3 1.164s (about 1.69x faster). All ratios derived from page data. |
| **Workload** | Type-C programs compiled to Type-V bytecode versus equivalent node --jitless and python3 scripts: recursive fib(40), 100M-element array allocation and sum, nested member access in a large loop. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC (Family 25, Model 1) 2 logical processors at 2.4 GHz, 2GB RAM, Ubuntu 24.04.1 |
| **Compiler and flags** | Python 3.12.3 (GCC 13.2.0), Node.js v18.19.1 with --jitless; Type-V build flags not stated |
| **Adoption** | 5 stars |
| **Last commit** | 2025-01-29 |
| **Links** | [repository](https://github.com/unlimitedsoftwareworks/type-v) · [benchmark](https://github.com/unlimitedsoftwareworks/type-v) |

## Verdict

First-party bar charts (mean execution time, added in commit 9076ed2 on 2024-11-13) on a 2-vCPU AMD EPYC (Family 25, Model 1) VM with 2 GB RAM, Ubuntu 24.04.1, Python 3.12.3 and Node.js 18.19.1 with --jitless: array allocation + sum 0.828 s vs node 0.892 s vs Python 1.307 s; fib(40) 9.91 s vs 8.32 s vs 11.07 s; nested member access 0.689 s vs 0.494 s vs 1.164 s. Type-V beats CPython on all three (1.12x to 1.69x, derived from page data) but beats node --jitless only on the array test (about 1.08x).

## Use it when

- You are already writing Type-C and need its runtime.
- Studying a small C11 typed register VM with computed-goto dispatch, coroutines, closures and a generational copying GC (about 200 opcodes, handlers in one header).
- Hobby or research work where beating CPython's interpreter on simple numeric loops and recursion (1.1x to 1.7x in the author's charts) is enough.

## Skip it when

- Anything production: the README states it is not production ready, not secure, not documented and not fully tested.
- You need to beat V8's interpreter: in the published charts node --jitless wins fib(40) (8.32 s vs 9.91 s) and nested member access (0.494 s vs 0.689 s); Type-V leads only on the array test (0.828 s vs 0.892 s). With V8's JIT on, it is not in the same league.
- Embedding a scripting language in a C/C++ host: there is no documented embedding API and the source language is a niche one with a TypeScript-hosted compiler.
- Windows/MSVC targets: the dispatch loop relies on labels-as-values and the Windows CI job is commented out.
- Long-running programs that allocate many short-lived arrays (see the array-buffer leak under gotchas).

## How it is fast

It is a register machine with typed instructions (256 registers per call frame, separate opcodes per data type and pointer-vs-value moves), so there is no dynamic type dispatch at run time and fields are reached by fixed offsets instead of property lookups. The interpreter loop uses computed-goto threaded dispatch (GCC/Clang labels-as-values table), call frames are cached in a linked list and reused instead of allocated per call, and array storage is a plain malloc'd buffer outside the GC heap. There is no JIT and, per its author, no optimization in the Type-C compiler.

## Compared with alternatives

Only when you are using Type-C. For a general embeddable bytecode VM, wasm3 or WAMR's fast interpreter are far more mature and benchmarked independently, and RISVM is a comparably small C/C++ register VM with a larger published lead over CPython (about 7.2x) and over Lua 5.3.

## Integration

| | |
|---|---|
| **Form** | static lib (libtypev.a) plus the typev executable, built with CMake 3.25+ |
| **Dependencies** | Vendored: libtable (MIT), yyjson, cpu_info; README also lists cwalk (MIT) and StringZilla (Apache-2.0). The Type-C compiler (TypeScript, Node.js/npm) is needed to produce bytecode. |
| **Minimum toolchain** | C11, CMake 3.25; GCC or Clang (computed goto); CI builds Ubuntu gcc/clang and macOS clang |
| **Platforms** | Linux and macOS (x86-64 and Apple arm64 per CI and the leak-track-mac-arm.sh script); Windows not supported in CI |
| **Thread safety** | not documented; the engine round-robins multiple 'cores' (isolated processes) on one OS thread, and gc_alloc uses an unsynchronized static uid counter |
| **Drop-in for the baseline** | no |

## Gotchas

- Shipped build flags work against it: CMakeLists.txt at the benchmark commit (9076ed2, 2024-11-13, whose executable name type_v matches the chart labels) and at HEAD forces -O0 -fno-inline. A default build is unoptimized; a Release build appends -O3 but keeps -fno-inline, so every opcode handler (declared static inline in instructions.h) stays an out-of-line call from the dispatch loop. Which configuration produced the charts is not stated.
- Array element buffers are malloc'd outside the GC heap (core_array_alloc) and neither the minor nor the major collector frees them: only OT_USER_OBJECT gets a dealloc call when an object dies (gc.c at HEAD), so every dead array leaks its backing store.
- The README's 'scavenger only, up to 1Mb' GC note is stale: HEAD has a generational copying collector that reserves two 80 MiB nursery semispaces plus an 80 MiB old region at start-up (1,310,720 cells of 64 bytes), and gc_alloc retries minor collections in a loop with no out-of-memory exit if a request cannot fit the nursery.
- Benchmark plausibility cannot be checked: test.py, test.js and the Type-C sources are unpublished. The 'large array addition (100M elements), two preallocated arrays' test reports CPython at 1.307 s and node --jitless at 0.892 s on a 2 GB VM, which is fast for 100M-iteration interpreter loops and tight on memory for two 100M-element Python lists or JS arrays (my inference, not measured), so the scripts may lean on builtins or smaller sizes; the cross-language comparison is not demonstrably like-for-like.

## Known shortcomings

- Beats node --jitless only on the array test (0.828 s vs 0.892 s) and is slower on fib(40) and member access; beats CPython 3.12 on all 3 by 1.12-1.69x (derived from page data). Benchmark sources unpublished, build flags unstated; off-baseline for a wasm runtime.
- Enricher: CMakeLists at the benchmark commit 9076ed2 and at HEAD forces -O0 -fno-inline, so the build behind the charts is unknown and probably unoptimized; the GC never frees malloc'd array buffers (only OT_USER_OBJECT deallocates), so dead arrays leak; the Python 1.307 s for a 100M-element alloc-and-sum on a 2 GB VM is implausible and the sources are unpublished.

## Caveats and trade-offs

Mixed result: the README only claims Type-V is 'very comparable to node in interpreter mode' and 'beats node on some benchmarks (unpublished)'; the published charts show it ahead of node --jitless only on the array test (about 7%) and slower on fib(40) and member access, while it beats CPython 3.12 on all three tests (1.12x to 1.69x). The baseline is V8 with the JIT disabled (Ignition interpreter only), and the comparison is cross-language (Type-C programs vs hand-written JS and Python equivalents). Numbers exist only in PNG charts; the node fib(40) bar carries a large error bar (roughly 6.6s to 10.1s). The benchmark programs are not published: the type-v repo has no tests directory, and type-c's tests/test1/test.tc is now a unit test, not the fib benchmark. Type-V build flags not stated; CPU is an unnamed AMD EPYC (Family 25, Model 1) VM with 2 vCPUs. The README says the VM is 'very unoptimized', not production ready and not secure; GC limited to about 1MB. Last commit January 2025.

Typed bytecode VM for the Type-C language (C11, minimal dependencies); no JIT, scavenger-only GC capped at 1MB allocations, not production ready, not documented or fully tested per its own notes.

## Maintenance

Stale since January 2025 (162 commits, 5 stars, no releases); Apache-2.0 and small enough to read, but self-described as unoptimized, insecure and untested, with build flags in its CMakeLists that disable optimization and inlining, so treat it as a study VM rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's three first-party bar charts (assets/bench_fib_40.png, bench_lar_arr_add.png, bench_member_access.png) show mean times for Type-V, node --jitless and python3 with hardware and runtime versions stated, but the benchmark programs (test.py, test.js and the Type-C sources) are not in the repo and Type-V's build flags and exact CPU model are not stated, so it cannot reach A.
- **Verifier notes:** Numbers in the record match the charts exactly; I added the CPython ratios, which are the only consistent win. Kept as a weak flagged C entry: not faster than node --jitless on 2 of 3 tests, benchmark sources unpublished, build flags unstated. License (LICENCE.md, Apache-2.0), 5 stars, last commit 2025-01-29 (stale) all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/README.md>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/assets/bench_fib_40.png>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/assets/bench_lar_arr_add.png>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/assets/bench_member_access.png>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/LICENCE.md>
  - <https://github.com/unlimitedsoftwareworks/type-v>
  - <https://github.com/unlimitedsoftwareworks/type-v/commits>
  - <https://github.com/unlimitedsoftwareworks/type-c/tree/master/tests/test1>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-c/HEAD/tests/test1/test.tc>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/README.md>
  - <https://github.com/unlimitedsoftwareworks/type-v>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/source/engine.c>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/source/core.h>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/source/core.c>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/source/gc/gc.c>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/source/gc/gc.h>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/source/instructions/opcodes.h>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/source/instructions/opfuncs.h>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/source/instructions/instructions.c>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/source/instructions/instructions.h>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/source/main.c>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/.github/workflows/cmake-multi-platform.yml>
  - <https://github.com/unlimitedsoftwareworks/type-v/commits/master/CMakeLists.txt>
  - <https://github.com/unlimitedsoftwareworks/type-v/commits/master/assets/bench_fib_40.png>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/9076ed2/CMakeLists.txt>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/9076ed2/source/gc/gc.h>
  - <https://github.com/unlimitedsoftwareworks/type-v/tree/master/source/instructions>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/assets/bench_fib_40.png>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/assets/bench_lar_arr_add.png>
  - <https://raw.githubusercontent.com/unlimitedsoftwareworks/type-v/HEAD/assets/bench_member_access.png>
  - <https://github.com/unlimitedsoftwareworks/type-c>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/unlimitedsoftwareworks/type-v`) · [data/wave12/enrich/raw/github_com_unlimitedsoftwareworks_type_v.json](../../../data/wave12/enrich/raw/github_com_unlimitedsoftwareworks_type_v.json) (enrichment confidence 0.6)

</details>
