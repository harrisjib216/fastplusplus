# Wizard Research Engine

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Virgil` · `Apache-2.0` · 🟢 active

> Research WebAssembly engine in Virgil whose in-place interpreter sets up code about 6x cheaper than wasm3 or WAMR-fast, but executes slower.

| | |
|---|---|
| **Beats** | Rewriting Wasm interpreters wasm3 and WAMR fast-interp (iwasm-fast), plus WAMR classic interpreter and JavaScriptCore's Wasm LLInt (jsc-int); V8 Liftoff/TurboFan and SpiderMonkey tiers also measured (OOPSLA 2022 artifact) |
| **Claimed result** | Setup, not throughput: from the artifact's raw data (derived from page data, medians over 24 PolyBench kernels), Wizard's translation step costs about 4.0 ns per Wasm byte versus 23.0 ns for wasm3, 25.9 ns for WAMR fast-interp and 147.7 ns for the JSC LLInt (about 5.8x, 6.5x and 37x faster setup), and its side table is 0.35 bytes per input byte versus 2.42 (wasm3) and 3.8 (WAMR fast). Execution time (geomean, derived from page data): about 2.5x slower than wasm3, 1.55x slower than WAMR fast-interp, about 1.1x faster than WAMR classic, and on par with jsc-int. Artifact README states: translation time for Wizard 3-4 ns/byte versus \~20-200 ns/byte for rewriting interpreters; Wizard within 1.5x-3.5x of wasm3, on par with wamr-classic (+/-10%) and jsc-int (+/-5%). README: hand-written x86-64 interpreter 'nearly 40x faster than the simple interpreter' (internal baseline). |
| **Workload** | OOPSLA 2022 artifact: 24 PolyBenchC 4.2.1 kernels compiled to Wasm, run 100 times each on Linux 4.15 / i7-8700K; measures whole-program execution time per engine and per-byte translation (setup) time and translated-code space of each engine's pre-execution step versus Wizard's in-place interpreter (which only builds a side table). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8700K, Linux 4.15 (data-linux-4.15-i7-8700K); a second data set on Ryzen 9 5950X / Linux 5.13 is in the artifact |
| **Compiler and flags** | Engines built per artifact src/README.md: V8 gn args is_debug=false; JSC build-jsc --jsc-only; wasm3 and WAMR plain cmake (default build type is Release in current CMakeLists); Wizard via the Virgil (aeneas) bootstrap and make bin/wizeng.x86-64-linux on branch exp_fast_config. Compiler versions and PolyBench-to-wasm flags not stated. |
| **Adoption** | 514 stars; subject of the OOPSLA 2022 paper 'A fast in-place interpreter for WebAssembly' |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/titzer/wizard-engine) · [benchmark](https://github.com/titzer/oopsla22-artifact) |

## Verdict

Recomputed this session from the OOPSLA 2022 artifact's raw data (24 PolyBenchC 4.2.1 kernels, 100 runs each, Intel Core i7-8700K, Linux 4.15; compiler versions and Wasm build flags not stated): median translation cost 3.98 ns per Wasm byte for Wizard versus 22.95 (wasm3), 25.92 (WAMR fast), 144.93 (V8 Liftoff) and 147.73 (JSC LLInt), and translated-code size 0.350 versus 2.419, 3.800, 2.950 and 1.038 bytes per input byte. For execution, Wizard's time is 2.52x wasm3's, 1.55x WAMR-fast's, 0.91x WAMR classic's, 1.01x the JSC LLInt's, and 6.7x and 8.1x those of V8 Liftoff and TurboFan (geomeans, derived from page data), so the win is setup and memory, not throughput.

## Use it when

- Startup-dominated or run-once Wasm modules where translation cost and memory for translated code matter more than steady-state speed (the artifact's four shortest kernels, 12-19 ms total, are where Wizard ties WAMR-fast and beats V8 TurboFan).
- Research on interpreters, instrumentation and dynamic analysis: monitors, probes, Whamm and Wasm-R3 build on Wizard, and in-place execution keeps bytecode offsets meaningful for tooling.
- Experimenting with new Wasm proposals (stack switching, GC, wide arithmetic) in a small codebase that builds in under a second.
- Teaching how a Wasm engine is structured, on x86-64 Linux for the fast tiers.

## Skip it when

- Raw interpreter throughput: on the same 24 PolyBenchC kernels wasm3 is about 2.5x and WAMR fast-interp about 1.55x faster (geomean), so Wizard only beats WAMR classic (about 1.1x) and ties the JSC LLInt.
- Embedding in a C or C++ host: Wizard is a Virgil program with no C API; WAMR, wasm3 or Wasmi are libraries.
- Platforms other than x86-64 Linux when speed matters: the fast interpreter and the single-pass compiler exist only on x86-64-linux; other targets (32-bit x86 Linux and Darwin, JVM, Wasm) get the slow V3 interpreter.
- Programs that need full WASI or Wasm threads: WASI preview 1 is incomplete (issue #4, open since 2022) and the threads proposal is not implemented (issue #155).
- Production SIMD workloads: open 2026 issues report x86-64 interpreter SIMD miscompilations (#648 extract_lane_u not zero-extended, #649 storeN_lane wrong address, #650 i8x16.ne corrupts a local).

## How it is fast

The OOPSLA 2022 design interprets Wasm bytecode in place instead of rewriting it into an internal format: during validation it builds only a side table of branch targets (delta pc, value count, pop count, side-table delta), so the setup step costs a few nanoseconds per input byte and the original bytecode is the executable code. The fast interpreter is hand-written x86-64 assembly with a dispatch table, which the README puts at nearly 40x the portable interpreter.

## Compared with alternatives

Pick Wizard over wasm3 or the WAMR fast interpreter when setup cost, translated-code memory or instrumentability matter more than throughput; pick wasm3 for the fastest interpreter on these kernels, and Wasmi or the csjh in-place interpreter when you need startup-oriented interpretation as an embeddable library.

## Integration

| | |
|---|---|
| **Form** | standalone engine binary (wizeng) built from Virgil source |
| **Dependencies** | Virgil compiler (titzer/virgil), built from source with make because Wizard tracks new Virgil features |
| **Minimum toolchain** | current Virgil (aeneas) built from its repository; no C/C++ toolchain needed |
| **Platforms** | x86-64-linux (fast interpreter, single-pass compiler, native memories); x86-linux, x86-darwin (32-bit), JVM jar and Wasm with the V3 interpreter only |
| **Thread safety** | not documented; the Wasm threads proposal is unimplemented (issue #155) |
| **Drop-in for the baseline** | no |

## Gotchas

- The setup ratios mix measurement methods (artifact run-translation-experiments.bash and patches): Wizard's 3-4 ns/byte is the difference between two builds' validation timers (with and without side-table construction), so it excludes validation; WAMR-fast is likewise a delta over WAMR classic, so the 6.5x versus WAMR-fast is like for like, but wasm3's CompileFunction timer and the JSC LLInt and V8 Liftoff counters time the whole per-function translation including decoding, so the 5.8x versus wasm3 and 37x versus JSC overstate the gap. Timers are gettimeofday microseconds summed per function.
- The space ratio (0.35 bytes per input byte) is computed under a hypothetical encoding: exp_validate_only.patch counts 2 bytes for a 'possible compressed entry' (delta pc and target fit in 7 bits, no values moved) and 16 bytes otherwise, while the measured build and current src/engine/Sidetable.v3 store every branch entry as four 32-bit ints (16 bytes). The real side-table footprint is larger, up to 8x the counted side-table bytes if no entry compresses.
- Execution times are whole-process wall times (btime) that include engine startup and translation; the benchmarked Wizard build (exp_fast_config.patch) also disabled value tagging and SIMD, which the default build enables.
- All numbers come from July 2022 snapshots (Wizard 158d26f, wasm3 9dcfce27, WAMR db210fbc, the wasm3 and WAMR binaries instrumented with timers); the current Wizard, which now has a single-pass compiler, has no published comparison.

## Known shortcomings

- The win is setup, not execution speed: OOPSLA 2022 artifact (titzer/oopsla22-artifact, i7-8700K) gives translation about 4.0 ns/byte vs wasm3 23.0, WAMR fast 25.9 and JSC LLInt 147.7, while execution is about 2.5x slower than wasm3, 1.55x slower than WAMR fast interpreter, about 1.1x faster than WAMR classic and ties the JSC interpreter. Numbers are from 2022 code; written in Virgil, not a C++ library; arXiv, ACM and Tufts copies of the paper are blocked here.
- Enricher: Wizard's translation time is the delta of two validation timers and excludes validation, while the wasm3, JSC and V8 timers include full translation, so the 5.8x and 37x setup ratios are overstated and only the 6.5x vs WAMR fast interpreter is like for like. The 0.35 space ratio counts a hypothetical 2-byte 'possible compressed entry' while real sidetable entries are 16 bytes (current Sidetable.v3 too), so the footprint is up to 8x larger than stated. The measured build had tagging and SIMD off; open x86-64 SIMD bugs #648-#650.

## Caveats and trade-offs

The win is setup time and memory, not raw speed: in the paper's own data Wizard's in-place interpreter runs about 2.5x slower than wasm3 and 1.55x slower than WAMR fast-interp (geomean over 24 PolyBenchC kernels), beats only WAMR classic (about 1.1x) and ties the JSC LLInt. Numbers are from the 2022 paper build (branch exp_fast_config, source zips on Google Drive) and the wasm3/WAMR-fast binaries were instrumented branches; current Wizard (Wasm 3.0, SPC compiler) is unmeasured. The fast interpreter exists only on x86-64-linux. Wizard is written in Virgil and ships as a standalone engine binary, not a C/C++ library. The paper PDF (arXiv 2205.01183, ACM, Tufts copy) was blocked here; claims come from the artifact README and raw data files. [retier] Win is setup, not execution: artifact data (i7-8700K, 2022 code) gives translation about 4.0 ns/byte vs wasm3 23.0, WAMR fast 25.9 and JSC LLInt 147.7, but Wizard's timer excludes validation while the others include full translation, so only the 6.5x vs WAMR fast interpreter is like for like. Execution is about 2.5x slower than wasm3 and 1.55x slower than WAMR fast. The 0.35 space ratio assumes a hypothetical 2-byte entry; real sidetable entries are 16 bytes. Measured build had tagging and SIMD off; written in Virgil. Paper copies blocked here.

Written in Virgil, not C++, and the fast interpreter is hand-written x86-64 assembly for Linux only; README says the design favors flexibility and readability for research over ultimate performance. Benefit of in-place interpretation is low memory use and no rewrite step. WASI support is a work in progress.

## Maintenance

Very active (commits up to 2026-10-06, 514 stars, Apache-2.0) and well suited to research, but it is a Virgil engine binary without a C/C++ API, its fast tiers are x86-64-Linux-only, and its published performance data is from a 2022 build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now B.
- **Tier reason:** Upgraded from D: the peer-reviewed OOPSLA 2022 paper ('A fast in-place interpreter for WebAssembly') has a public artifact (github.com/titzer/oopsla22-artifact: run-execution-experiments.bash, run-translation-experiments.bash, PolyBenchC 4.2.1 sources, engine build commands and the raw data in data-linux-4.15-i7-8700K) comparing Wizard against wasm3, WAMR (classic and fast), JSC, V8 and SpiderMonkey on an i7-8700K. Not A because compiler versions and the PolyBench-to-wasm build flags are not stated, and the paper text itself could not be opened.
- **Verifier notes:** Found the paper's artifact repo (titzer/oopsla22-artifact) and recomputed ratios from data-linux-4.15-i7-8700K: Wizard setup is about 6x cheaper than wasm3/WAMR-fast and 37x cheaper than JSC LLInt, but execution is slower than wasm3 and WAMR-fast. The record's metric should be startup (translation time) rather than throughput; shortcoming to record: not faster at execution than the fastest interpreters, Virgil engine not a C++ library, numbers from 2022 code.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `workload`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** paper access and current-code re-run; like-for-like translation timing including validation
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/titzer/wizard-engine/HEAD/README.md>
  - <https://github.com/titzer/wizard-engine>
  - <https://github.com/titzer/wizard-engine/commits>
  - <https://github.com/titzer/wizard-engine/tree/master/bench>
  - <https://github.com/titzer/wizard-engine/tree/master/doc>
  - <https://github.com/titzer/oopsla22-artifact>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/README.md>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/common.bash>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/run-execution-experiments.bash>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/run-translation-experiments.bash>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/summarize-execution.bash>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/src/README.md>
  - <https://github.com/titzer/oopsla22-artifact/tree/master/data-linux-4.15-i7-8700K>
  - <https://github.com/titzer/oopsla22-artifact/tree/master/benchmarks>
  - <https://github.com/titzer/oopsla22-artifact/tree/master/src>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/data-linux-4.15-i7-8700K/execution.bicg.wizard>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/data-linux-4.15-i7-8700K/translation.bicg.wizard.us>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bytecodealliance/wasm-micro-runtime/HEAD/product-mini/platforms/linux/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/titzer/wizard-engine>
  - <https://raw.githubusercontent.com/titzer/wizard-engine/HEAD/README.md>
  - <https://raw.githubusercontent.com/titzer/wizard-engine/HEAD/doc/Building.md>
  - <https://raw.githubusercontent.com/titzer/wizard-engine/HEAD/Design.md>
  - <https://raw.githubusercontent.com/titzer/wizard-engine/HEAD/src/engine/CodeValidator.v3>
  - <https://raw.githubusercontent.com/titzer/wizard-engine/HEAD/src/engine/Sidetable.v3>
  - <https://github.com/titzer/wizard-engine/issues>
  - <https://github.com/titzer/oopsla22-artifact>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/README.md>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/common.bash>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/run-execution-experiments.bash>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/run-translation-experiments.bash>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/summarize-execution.bash>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/src/README.md>
  - <https://github.com/titzer/oopsla22-artifact/tree/master/src/patches>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/src/patches/wasm3.exp_instrumentation.patch>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/src/patches/wamr.exp_instrumentation.patch>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/src/patches/wamr.exp_classic.patch>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/src/patches/wizard.exp_validate_only.patch>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/src/patches/wizard.exp_validate_only_no_sidetable.patch>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/src/patches/wizard.exp_fast_config.patch>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/src/patches/wasm3.main.git.log>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/src/patches/wamr.main.git.log>
  - <https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/src/patches/wizard.main.git.log>
  - https://raw.githubusercontent.com/titzer/oopsla22-artifact/HEAD/data-linux-4.15-i7-8700K/ (execution.&lt;kernel&gt;.&lt;engine&gt; for 7 engines and translation.&lt;kernel&gt;.&lt;engine&gt;.us/.bytes for 5 engines, 24 kernels, 408 files)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/titzer/wizard-engine`) · [data/wave12/enrich/raw/github_com_titzer_wizard_engine.json](../../../data/wave12/enrich/raw/github_com_titzer_wizard_engine.json) (enrichment confidence 0.65)

</details>
