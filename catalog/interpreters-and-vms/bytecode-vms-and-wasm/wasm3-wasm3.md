# wasm3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Portable, dependency-free C WebAssembly interpreter; fastest of seven interpreters on scalar MVP code, about 1.6x WAMR fast-interp on Apple M4.

| | |
|---|---|
| **Beats** | WAMR fast interpreter (iwasm); Wasmtime Pulley interpreter; WasmEdge interpreter |
| **Claimed result** | Geomean CPU time relative to the fastest runtime (lower is better), M4 Max E-cores: wasm3 1.01, WAMR fast-interp 1.63, Wasmtime Pulley 2.09, WasmEdge interpreter 8.42; A12 E-cores: wasm3 1.04, WAMR 1.38, Pulley 1.68, WasmEdge 9.28. About 1.6x faster than WAMR fast-interp and 2.1x faster than Pulley on the M4 (derived from page data). Page text: 'wasm3 is the fastest interpreter on nearly every case it runs'. |
| **Workload** | Interpreter-only comparison on the 17 Wasm cases every runtime runs (xmrsplayer audio, AssemblyScript graphql, audio DSP, MVP kernels), CPU time per call, N=10 per platform, Apple M4 Max E-cores and iPhone XS Max (A12) E-cores. |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max E-cores (MacBook Pro, macOS 27.0); iPhone XS Max A12 Bionic E-cores (iOS 18.7.10) |
| **Compiler and flags** | wasm3 v0.9.0 built with -O3 -mcpu=apple-a12 -std=c99 -DNDEBUG -fno-exceptions, Apple clang 21.0.0 (Xcode 27.0), no WASI sources; WAMR cmake Release -O3 FAST_INTERP only (AOT/JIT/FAST_JIT off); Pulley rust nightly-2026-07-05, RUSTFLAGS --cfg=pulley_tail_calls, fat LTO |
| **Adoption** | 8.0k stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/wasm3/wasm3) · [benchmark](https://github.com/rebeckerspecialties/wasm-benchmark/blob/main/docs/runtime-comparison-2026-09-22.md) |

## Verdict

In the independent rebeckerspecialties/wasm-benchmark run of 2026-09-22, unpatched wasm3 v0.9.0 (Apple clang 21.0.0, -O3 -mcpu=apple-a12) took 1.01x the fastest runtime's CPU time per call versus 1.63x for WAMR fast-interp and 2.09x for Wasmtime v49 Pulley, geomean over 17 MVP/scalar cases on M4 Max E-cores (1.04 vs 1.38 vs 1.68 on an iPhone XS A12), N=10, results checked against a cross-runtime consensus; I recomputed the Pulley and WAMR M4 geomeans from the per-case table. The competing WAMR, WasmEdge and Pulley builds carried 29, 26 and 9 patches, while wasm3 ran stock.

## Use it when

- You cannot generate native code (iOS/App Store, watchOS, W^X targets, Wasm-in-Wasm) and the guest is scalar MVP code: on M4 E-cores it was fastest on 14 of the 17 shared cases and within 5% on the other three, including xmrsplayer audio (6.9 ms vs WAMR 11.9 ms and Pulley 15.7 ms per call) and AssemblyScript graphql.
- Dispatch-heavy guests (call_indirect, vtable-style polymorphism): 11.7 ms vs WAMR 18.5 ms and Pulley 31.5 ms per call_indirect run on M4.
- Microcontrollers and small SoCs (ESP32, nRF52, Cortex-M3/M4/M7, RISC-V, Xtensa, AVR): the README cites about 64 KB of code and 10 KB of RAM as the minimum useful system.
- Plugin or scripting hosts that want a C99 library that builds in seconds with no dependencies, plus gas metering, resource caps and suspend/resume snapshots (HEAD).
- Short-lived modules where Cranelift compile time would dominate: in wasmi-benchmarks on an EPYC 7763 its lazy-compile startup geomean is 2.77x the fastest versus 56.73x for WAMR fast-interp and 1634x for Wasmtime Cranelift (eager wasm3 is 51.60x, so the win comes from deferring compilation).

## Skip it when

- Peak throughput where a JIT or AOT is allowed: in wasmi-benchmarks on x86-64 it executes at 16.51x the fastest runtime against 1.15x for Wasmtime Cranelift and 1.05x for V8.
- SIMD-128 or relaxed-SIMD guests: there is no fixed-width SIMD at all (README lists it N/A), so auto-vectorised builds fail to load; WAMR leads those rows. GC and the full threads proposal are also N/A.
- Hosts that instantiate the same module many times: an IM3Module is consumed by the runtime it is loaded into and cannot be cloned (open issue #366), so each fresh instance re-parses and re-validates; extended-const instantiation cost 116-122x Pulley's time on M4.
- Assuming the A-tier lead holds on x86-64: in wasmi-benchmarks (EPYC 7763, the same wasm3 v0.9.0 via the wasm3x 0.2.1 crate) it executes at 16.51x the fastest, level with WAMR fast-interp (17.07x) and behind wasmz (15.89x), Stitch (15.73x), Wasmi v2 (12.40x) and Silverfir-nano's interpreter (9.02x).
- Teams that need a steady release cadence: v0.5.0 (2021) was the only release until v0.9.0 in August 2026, and the README still declares a minimal maintenance phase.

## How it is fast

Wasm stack bytecode is translated into 'operations' that are C functions sharing one fixed signature (pc, sp, mem, r0, fp0); each ends by tail-calling the next, so the virtual registers stay in machine registers and there is no central dispatch loop (continuation-passing threaded code, enforced with musttail where the compiler supports it). The compile pass maps the stack machine onto a register-file layout with up to three operation variants per opcode by operand placement, and fuses common sequences. HEAD (after the measured v0.9.0) adds the preserve_none calling convention on x86-64 and AArch64 and fold/fuse passes (set_local folding, compare+branch fusion) that the v0.9.1-beta.1 notes credit with 10-50% speedups on many workloads.

## Compared with alternatives

Pick wasm3 over WAMR fast-interp and wasmz for scalar MVP guests on Apple Silicon (1.01 vs 1.63 and 1.59 geomean on M4) or when you want the smallest C dependency; pick WAMR when the guest needs SIMD or an AOT/JIT tier later. For Rust hosts on x86-64, Wasmi v2 and Silverfir-nano executed faster in wasmi-benchmarks (12.40 and 9.02 vs 16.51).

## Integration

| | |
|---|---|
| **Form** | static lib via CMake, or source-drop (compile source/\*.c directly; the benchmark built 12 files with clang -c and ar) |
| **Dependencies** | none for the core; uvwasi or the built-in simple WASI layer optional for WASI |
| **Minimum toolchain** | C99 compiler (Clang, GCC, MSVC, MinGW-w64, TinyCC, Zig, cosmocc); CMake 3.11+ for the CMake build; guaranteed tail-call dispatch needs a compiler with musttail (Clang, GCC 15) |
| **Platforms** | x86, x86-64, ARM, AArch64, RISC-V, PowerPC, MIPS, Xtensa, ARC32, AVR; Linux, Windows, macOS, FreeBSD, Android, iOS, OpenWrt, Arduino/PlatformIO/ESP-IDF MCUs, browsers (compiled to Wasm); big-endian supported |
| **Thread safety** | Not documented in wasm3.h. Threads are listed N/A; atomics (added 2026-09-29) keep single-thread semantics, and sharing a memory between runtimes needs the separate d_m3HasThreads build option (m3_config.h). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry behind the 'instantiation is its weak spot' figures: for the extended-const rows the benchmark times m3_NewRuntime + m3_ParseModule + m3_LoadModule + m3_FindFunction (lazy compile) + call per sample for wasm3, but only Store + Instance::new + call on a module compiled once for Pulley and WAMR (wasm3.rs vs lib.rs/wamr.rs). wasm3's API forces the re-parse, so the cost is real for users, but the 116-122x compares parse+validate+instantiate against instantiate only. The 17-case execution geomean is unaffected (load and compile are outside the timed window there).
- The measured build is v0.9.0 (2026-08-24). HEAD changed the public API: m3_GetMemory and m3_GetMemorySize now take an IM3Module and size_t sizes instead of an IM3Runtime and uint32_t, so v0.9.0 bindings (including the benchmark's own) need updating; HEAD's exception handling, multi-memory, memory64 and atomics are not in v0.9.0, which failed those smoke tests.
- Exception handling on HEAD has a documented lifetime hole: exception objects belong to the runtime and are released when the outermost m3_Call returns, so an exnref parked in a global or table 'outlives that and dangles' (m3_config.h).
- Security history: several CVEs against v0.5.0, the only release from 2021 to 2026 (heap overflows in m3_compile.c DeallocateSlot, NewCodePage, op_Const64; CVSS up to 9.8; search snippets, NVD pages not opened). v0.9.0 adds full module validation and OSS-Fuzz fixes, so avoid distro or crate packages still pinned to 0.5.0 for untrusted modules.

## Known shortcomings

- Interpreter-only win: the 17-case geomean covers MVP code only (no SIMD, GC, exception handling or memory64), extended-const instantiation takes 116-122x Pulley's time, and wasm3 is far behind JIT runtimes such as wasmtime Cranelift.
- Enricher: in the rebeckerspecialties harness the extconst rows time wasm3 for re-parse, validate, load, compile and call per sample while Pulley and WAMR time only instantiate and call on a module compiled once (wasm3.rs vs lib.rs and wamr.rs), so the 116-122x 'instantiation weak spot' mixes parse cost with instantiation (the 17-case geomean is unaffected). On x86-64 the lead disappears: wasmi-benchmarks on an EPYC 7763 with the same v0.9.0 has wasm3 at 16.51 vs WAMR 17.07, behind wasmz 15.89, Stitch 15.73, Wasmi v2 12.40 and Silverfir-nano 9.02. HEAD changed the API after v0.9.0 (m3_GetMemory takes IM3Module), an exnref parked in a global dangles (m3_config.h), v0.5.0 CVEs; the 'no EH, memory64 or multi-memory' caveat holds for v0.9.0 only (v0.9.1-beta.1 adds them).

## Caveats and trade-offs

Result is interpreter versus interpreter: wasm3 is not faster than JIT/AOT Wasmtime, Wasmer or V8 (its own docs/Performance.md CoreMark table, 2019-2020 on an i5-8250U and labelled historical by the project, has wasmtime 0.8.0 and Wasmer Cranelift 4.0x faster and wasm-micro-runtime 8.1x slower; in the wasmi-benchmarks suite on an AMD EPYC 7763 its execute geomean is 16.51 vs Wasmtime Cranelift 1.15 and V8 1.05, and behind Silverfir-nano's interpreter 9.02 and Wasmi v2 12.40). The 17-case geomean covers only MVP/scalar code: wasm3 cannot run the SIMD-canonical builds, exceptions, GC, typed references, memory64 or multi-memory, and WAMR leads on the SIMD rows. Instantiation is its weak spot: extended-const modules cost it 116-122x Pulley's time on the M4 (62-85x on the A12). The benchmark author built WAMR with 29 carried patches, WasmEdge with 26 and Pulley from a fork branch with 9 extra commits, while wasm3 v0.9.0 ran unpatched. Only Apple Silicon E-cores measured. Independent libsodium 2021-Q1 run (https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2021-Q1/README.md): 'wamr was slower than wasm3 on every single test', native about 30x faster than wasm3 and about 46x faster than WAMR. The README still declares a minimal maintenance phase, though September 2026 commits add atomics and an exception-handling API.

Pure interpreter with no JIT or AOT tier: far slower than compiling runtimes. In the wasmi-benchmarks suite (AMD EPYC 7763, https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg) execute geomean relative to the fastest runtime per test is wasm3 16.51x vs Wasmtime Cranelift 1.15x and V8 1.05x. Very cheap startup: same suite startup geomean wasm3 lazy 2.77x vs WAMR fast-interp 56.73x, V8 33.27x, Wasmer Cranelift 1484.15x, Wasmtime Cranelift 1634.19x. Of the Wasm 3.0 features the benchmark tested it supports only tail calls and extended-const. Maintainer states the project is in a minimal maintenance phase.

## Maintenance

Active again in 2026 (v0.9.0 2026-08-24, v0.9.1-beta.1 2026-09-10, last commit 2026-09-29) though the README still says minimal maintenance; MIT-licensed, dependency-free C99 and easy to vendor, with no published GitHub security advisories or SECURITY.md.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent public harness (rebeckerspecialties/wasm-benchmark: crates/benchmark-core/src/cases.rs, scripts/build-wasm3.sh with COMMON_CFLAGS -O3 -mcpu=apple-a12 -std=c99 -DNDEBUG -fno-exceptions, scripts/run-m4-pass.sh) runs unpatched wasm3 v0.9.0 against WAMR fast-interp and wasmtime v49 Pulley with Apple clang 21.0.0 on M4 Max E-cores and an A12, N=10, results consensus-checked.
- **Verifier notes:** Numbers match the page: geomeans wasm3 1.01, wasmz 1.59, WAMR 1.63, Pulley 2.09, tinywasm 3.20, WasmEdge 8.42 (M4) and 1.04/1.38/1.68 (A12); call_indirect 11.67 vs 18.48 vs 31.53 ms; the libsodium quote is verbatim. Metadata checked: MIT, 8.0k stars, last commit 2026-09-29. Shortcomings: interpreter-only win, far slower than JIT runtimes, no SIMD/GC/EH/memory64 so its geomean covers MVP code only, slow instantiation of extended-const modules.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/scripts/build-wasm3.sh>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/crates/benchmark-core/src/cases.rs>
  - <https://github.com/rebeckerspecialties/wasm-benchmark>
  - <https://github.com/wasm3/wasm3>
  - <https://github.com/wasm3/wasm3/commits>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/docs/Performance.md>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2021-Q1/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/docs/Performance.md>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/docs/Interpreter.md>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/docs/Hardware.md>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/docs/Development.md>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/docs/Cookbook.md>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/source/wasm3.h>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/source/m3_config.h>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/source/m3_config_platforms.h>
  - <https://raw.githubusercontent.com/wasm3/wasm3/v0.9.0/source/m3_config_platforms.h>
  - <https://raw.githubusercontent.com/wasm3/wasm3/v0.9.0/source/wasm3.h>
  - <https://github.com/wasm3/wasm3/commits>
  - <https://github.com/wasm3/wasm3/releases>
  - <https://github.com/wasm3/wasm3/issues>
  - <https://github.com/wasm3/wasm3/security>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/scripts/build-wasm3.sh>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/crates/benchmark-core/src/wasm3.rs>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/crates/benchmark-core/src/wamr.rs>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/crates/benchmark-core/src/lib.rs>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/crates/benchmark-core/src/cases.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasm3/Cargo.toml>
  - <https://crates.io/api/v1/crates/wasm3x>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2021-Q1/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/wasm3/wasm3`) · [data/wave12/enrich/raw/github_com_wasm3_wasm3.json](../../../data/wave12/enrich/raw/github_com_wasm3_wasm3.json) (enrichment confidence 0.85)

</details>
