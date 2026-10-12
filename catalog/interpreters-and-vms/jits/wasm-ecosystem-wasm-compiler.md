# WARP WebAssembly compiler and runtime (wasm-ecosystem/wasm-compiler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> BMW's single-pass C++ Wasm-to-native compiler and runtime for embedded targets; its own chart shows compiles faster than Liftoff, runs near TurboFan.

| | |
|---|---|
| **Beats** | V8 Liftoff and V8 TurboFan; SpiderMonkey Baseline and Ion |
| **Claimed result** | README quadrant chart (normalized scores, compilation / execution): WARP 0.8316 / 0.8172; V8 Liftoff 0.747 / 0.4275; V8 TurboFan 0.0423 / 0.8505; SpiderMonkey Baseline 0.8136 / 0.3456; SpiderMonkey Ion 0.099 / 0.8163; native clang 0.5 (comp. speed N/A) / 0.873. |
| **Workload** | Normalized compilation speed and execution speed of WebAssembly modules from the open-wasm-compiler-benchmark repo (github.com/Schleifner/open-wasm-compiler-benchmark, which returns 404 as of 2026-10-06, so the inputs are not public), WARP's vb_bench versus V8 d8 (Liftoff, TurboFan) and SpiderMonkey js shell (Baseline, Ion) and native clang builds, timed by scripts/benchmark/run_bench.py. |
| **Metric** | compile-time |
| **Compiler and flags** | Benchmark guide (scripts/benchmark/Readme.md): vb_bench built with clang/clang++, CMAKE_BUILD_TYPE=Release, -DINTERRUPTION_REQUEST=0 -DEAGER_ALLOCATION=1, VB_ENABLE_DEV_FEATURE=OFF; V8 d8 built with tools/dev/gm.py x64.release and run with --no-wasm-lazy-compilation --liftoff or --no-liftoff --single-threaded; SpiderMonkey built with an optimized mozconfig and run with --wasm-compiler=baseline or ion --cpu-count=1. Compiler, V8 and SpiderMonkey versions not stated. |
| **Adoption** | 26 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/wasm-ecosystem/wasm-compiler) · [benchmark](https://github.com/wasm-ecosystem/wasm-compiler) |

## Verdict

The only evidence is the README's first-party quadrant chart of normalised scores. Compile speed: WARP 0.83, SpiderMonkey Baseline 0.81, V8 Liftoff 0.75, Ion 0.10, TurboFan 0.04. Execution speed: native 0.87, TurboFan 0.85, WARP 0.82, Ion 0.82, Liftoff 0.43, SpiderMonkey Baseline 0.35. run_bench.py produced the scores by timing whole processes on the unpublished open-wasm-compiler-benchmark modules, with a clang Release build (interruption off, eager allocation) against self-built d8 and SpiderMonkey shells pinned to one thread. No CPU, OS, compiler or engine version is stated.

## Use it when

- Embedded or automotive hosts (AArch64, TriCore v1.8+, QNX, bare metal) that want native-code Wasm with a small footprint and integrator-controlled memory: two contiguous regions plus user allocation hooks.
- Load-time compile cost matters but you still want near-optimising execution: on the README chart it sits right of V8 Liftoff on compile speed (0.83 vs 0.75) and well above Liftoff and SpiderMonkey Baseline on execution (0.82 vs 0.43 and 0.35).
- Ahead-of-time workflows: compile once (possibly cross-compiled), store the artifact and re-instantiate it, optionally with statically linked host functions to save a lookup per call.
- Codebases held to AUTOSAR C++14 or MISRA C++ (no recursion), which the project says it follows.

## Skip it when

- Modules built by current toolchains with default flags: the README lists non-trapping float-to-int conversions as unsupported, and LLVM 20 and later enable that feature (and bulk memory) by default for the generic wasm CPU (LLVM 20.1.0 release notes, seen as a search snippet only), so build guests with -mcpu=mvp or check their features. Only MVP plus sign extension and exported mutable globals are listed; imported globals, tables and memories are listed as unsupported; tail calls only arrived in July-August 2026.
- Peak throughput: on its own chart execution is below V8 TurboFan (0.8505) and native clang (0.873) and level with SpiderMonkey Ion (0.8163).
- Platforms that forbid writable-then-executable memory (iOS App Store and similar) or 32-bit ARM microcontrollers: it emits native code, and the aarch32 backend is not implemented.
- Decisions that need reproducible or independent numbers: there is only a first-party normalised chart with no CPU, compiler or engine versions, and the input suite (Schleifner/open-wasm-compiler-benchmark) returns 404.

## How it is fast

It compiles in one pass using 'Valent Blocks' (Scheidl, iCCECE 2020). Side-effect-free stack instructions are only recorded on a compile-time IR stack. When an instruction with non-stack side effects arrives (a trap, a branch, a local or global write), the pending blocks are 'condensed' into machine code whose results land in a register or stack slot. That gives expression-tree code generation without building a full IR. Linear-memory and stack-overflow checks can be delegated to the MMU: 8 GB of virtual address space is reserved, inaccessible pages are protected and a signal handler turns faults into exceptions. Recent commits add compile-time folding of constant br_if conditions and reuse of call parameters already loaded into registers. The README reports about 10 KB of extra compiler heap for a 170 KB module and a 187 kB stripped AArch64 binary for the benchmark tool, including compiler, assembler and runtime.

## Compared with alternatives

Among the catalogued JITs only WasmNow targets Wasm baseline compilation too, and it has stronger published numbers against Liftoff (5-6.5x faster compiles with 39-63% faster code). Pick WARP when you need a maintained, embeddable compiler with AArch64 and TriCore backends, MISRA-style code and a tiny memory footprint, rather than a research prototype. TPDE compiles LLVM IR, not Wasm.

## Integration

| | |
|---|---|
| **Form** | shared lib by default (CMake option STATIC_LIB=ON for a static lib); Bazel build also supported |
| **Dependencies** | none in production code for x86_64 and AArch64; berkeley-softfloat-3 for the TriCore backend |
| **Minimum toolchain** | README says C++14; the top-level CMakeLists.txt sets CMAKE_CXX_STANDARD 17; CMake 3.15+ |
| **Platforms** | x86-64, AArch64, TriCore v1.8+ (aarch32 not implemented); bare metal, Unix/Linux, macOS, QNX, Windows; MMU-based checks not available on TriCore |
| **Thread safety** | Not documented, except that a running module can be interrupted from another thread when built with INTERRUPTION_REQUEST=1. MMU mode relies on process-wide signal handlers installed through SignalFunctionWrapper. |
| **Drop-in for the baseline** | no |

## Gotchas

- The charted build is not the default configuration. The benchmark guide builds vb_bench with -DINTERRUPTION_REQUEST=0 -DEAGER_ALLOCATION=1, while src/config.hpp defaults to INTERRUPTION_REQUEST 1 (the docs say it impacts performance) and EAGER_ALLOCATION 0 (the first touch of each linear-memory page goes through the signal handler). Expect a default build to run slower than the chart.
- Harness flaws in scripts/benchmark/run_bench.py. Both axes come from whole-process wall time read from /usr/bin/time -p (10 ms resolution), one run per module by default, and the score is 10000 / geomean of those times. So d8 and SpiderMonkey shell startup plus JS harness load count as compile time. The 'execution' axis also includes engine startup and compilation for every engine except native. Result mismatches against native are printed, not enforced. The V8 Liftoff runs omit --no-wasm-tier-up. How scores became the 0-1 chart values is undocumented.
- Static host-function linking bakes absolute addresses into the code, so on systems with ASLR you must recompile per process or use dynamic linking. Active bounds and stack checks are the default on TriCore and QNX and cost speed; ACTIVE_DIV_CHECK defaults on for AArch64.
- 2026 commits fix several code-generation bugs: Windows x86-64 ABI not saving 128-bit xmm registers (June), an i32.div compile crash (July), return_call stack-parameter placement and tail-jump safety (July-August), and a missing stack-fence check in builtin.tracePoint under active protection (September). Pin a recent commit; outside PRs go through BMW's internal CI.

## Known shortcomings

- Benchmark chart normalizes to 0-1 without documenting the normalization, CPU or engine versions; the input repository Schleifner/open-wasm-compiler-benchmark returns 404. run_bench.py times the whole process with /usr/bin/time, so d8 and js startup counts against V8 and SpiderMonkey compile time (favours WARP), with a default of one run. Execution score 0.8172 is below TurboFan's 0.8505, so WARP wins only on compile time.
- Enricher: the charted build is not the default configuration (INTERRUPTION_REQUEST=0 and EAGER_ALLOCATION=1 against defaults 1 and 0); both chart axes are whole-process /usr/bin/time, so the 'execution' axis also includes startup and compile, and result mismatches are printed rather than enforced. The README lists no non-trapping float-to-int, which LLVM 20+ emits by default; 2026 codegen fixes include a Windows xmm save, an i32.div crash, return_call and a missing stack-fence check.

## Caveats and trade-offs

Result is a normalized unitless quadrant chart; run_bench.py prints wall-clock means and a score of 10000/geomean, but how the 0-1 chart values were derived is not documented, and native clang's compile score is a placeholder 0.5 ('comp. speed N/A'). CPU model and tool versions are not stated. Benchmark inputs (Schleifner/open-wasm-compiler-benchmark) are not publicly reachable (404). Harness flaws: the compilation benchmark times the whole process with /usr/bin/time -p (10 ms resolution), so d8 and SpiderMonkey js-shell startup and JS harness load are charged to their compile time while WARP runs as a small native binary, which favours WARP; default is a single run per module (-n 1); the 'V8 Liftoff' runs do not pass --no-wasm-tier-up, so hot code may tier up to TurboFan. WARP's execution score (0.8172) is below V8 TurboFan (0.8505) and native clang (0.873) and about equal to SpiderMonkey Ion (0.8163); its win is compile speed at near-optimizing-tier execution speed, and clearly over the single-pass baselines Liftoff (0.4275) and SpiderMonkey Baseline (0.3456). Backing paper (Scheidl, Valent-Blocks, iCCECE 2020) was not opened (IEEE and ResearchGate blocked); a search snippet only says WebAssembly overhead on embedded targets fell from 87% to 21%.

Single-pass compiler and runtime aimed at embedded systems (x86_64, aarch64, tricore; aarch32 not implemented), written in C++14 with no external dependencies in production code; 187 kB stripped binary (AArch64, Clang 17, macOS). Compiles ahead of time into an ELF-like artifact that the runtime instantiates.

## Maintenance

Actively developed by BMW AG (113 commits on develop, last 2026-10-03, 0 open issues, 26 stars) under Apache-2.0. No GitHub releases are visible (the org's performance-monitor repo refers to wasm-compiler@3.0.3). Usable as a library today for MVP-level modules.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README mermaid quadrant chart gives exactly the normalized compile/execution scores in the record for WARP, V8 Liftoff/TurboFan and SpiderMonkey Baseline/Ion; the harness (scripts/benchmark/run_bench.py, util/d8_harness.js, util/sm_harness.js) and build flags are public, but no CPU model, compiler or engine versions are stated, the normalization to 0-1 is undocumented, and the benchmark input repo (Schleifner/open-wasm-compiler-benchmark) returns 404, so first-party tier C.
- **Verifier notes:** Chart numbers match the record exactly; metadata confirmed (Apache-2.0, 26 stars, last commit 2026-10-03 'Fix CI apt install (#865)', active, BMW AG copyright on harness files). Main shortcomings: undocumented normalization, no CPU or versions, benchmark inputs repo 404, whole-process wall-clock timing charges JS-engine startup to V8/SpiderMonkey compile times.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/wasm-ecosystem/wasm-compiler>
  - <https://github.com/wasm-ecosystem/wasm-compiler/commits>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/scripts/benchmark/Readme.md>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/scripts/benchmark/run_bench.py>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/scripts/benchmark/util/d8_harness.js>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/scripts/benchmark/util/sm_harness.js>
  - <https://github.com/Schleifner/open-wasm-compiler-benchmark>
  - <https://github.com/Schleifner?tab=repositories>
- **Sources the enricher read:**
  - <https://github.com/wasm-ecosystem/wasm-compiler>
  - <https://github.com/wasm-ecosystem/wasm-compiler/commits>
  - <https://github.com/wasm-ecosystem/wasm-compiler/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/src/config.hpp>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/docs/GettingStarted.md>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/docs/InfoForContributors.md>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/scripts/benchmark/Readme.md>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/scripts/benchmark/run_bench.py>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/scripts/benchmark/util/d8_harness.js>
  - <https://raw.githubusercontent.com/wasm-ecosystem/wasm-compiler/HEAD/scripts/benchmark/util/sm_harness.js>
  - <https://github.com/orgs/wasm-ecosystem/repositories>
  - <https://raw.githubusercontent.com/wasm-ecosystem/performance-monitor/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/wasm-ecosystem/wasm-compiler`) · [data/wave12/enrich/raw/github_com_wasm_ecosystem_wasm_compiler.json](../../../data/wave12/enrich/raw/github_com_wasm_ecosystem_wasm_compiler.json) (enrichment confidence 0.65)

</details>
