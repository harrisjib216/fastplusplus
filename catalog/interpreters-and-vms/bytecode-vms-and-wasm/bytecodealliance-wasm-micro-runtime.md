# WebAssembly Micro Runtime (WAMR)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> Small, build-time-configurable C WebAssembly runtime whose fast interpreter beats Wasmtime's Pulley interpreter by about 1.2-1.3x geomean.

| | |
|---|---|
| **Beats** | Wasmtime Pulley interpreter (A-tier numbers); Wasmtime, Wasmer and V8 JIT/AOT (libsodium suite) |
| **Claimed result** | Geomean CPU time per call relative to the fastest runtime over the 17 cases all seven runtimes run (lower is better): M4 Max E-cores WAMR fast-interp 1.63 vs Wasmtime Pulley 2.09 and WasmEdge interpreter 8.42; iPhone XS (A12) E-cores 1.38 vs 1.68 and 9.28. About 1.28x faster than Pulley on the M4 and 1.22x on the A12 (derived from page data). Per case on M4 (CPU ms per call): bulk_memory 10.41 vs 22.14, call_indirect 18.48 vs 31.53, convolution 3.928 vs 5.883, sieve 0.5128 vs 0.7082. The harness repo's earlier docs/cross-runtime-pulley-vs-wamr.md (iPhone 12, 2026-05-15, Pulley with the author's phase-3 fusion patches) has WAMR 1.37-1.86x faster on call_indirect, xmrsplayer, graphql (AssemblyScript) and the vtable suite. |
| **Workload** | Interpreter-only comparison on the 17 Wasm cases every runtime runs (audio, graphql, DSP, MVP kernels), CPU time per call, N=10 per platform, Apple M4 Max E-cores and iPhone XS Max E-cores; WAMR configured as fast interpreter only. |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max E-cores (MacBook Pro, macOS 27.0); iPhone XS Max A12 Bionic E-cores (iOS 18.7.10) |
| **Compiler and flags** | WAMR main (WAMR-2.4.1-364, b70d708d, 2026-09-21) with 29 local patches, cmake Release -O3 -mcpu=apple-a12, INTERP=1 FAST_INTERP=1 AOT=0 JIT=0 FAST_JIT=0 SIMD=1 RELAXED_SIMD=1 BULK_MEMORY=1 TAIL_CALL=1 etc., WAMR_DISABLE_HW_BOUND_CHECK=1; Pulley from wasmtime v49 fork (9 extra commits), rust nightly-2026-07-05, RUSTFLAGS --cfg=pulley_tail_calls -C target-cpu=apple-a12, fat LTO, 1 CGU; Apple clang 21.0.0 (Xcode 27.0). |
| **Adoption** | 6.1k stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/bytecodealliance/wasm-micro-runtime) · [benchmark](https://github.com/rebeckerspecialties/wasm-benchmark/blob/main/docs/runtime-comparison-2026-09-22.md) |

## Verdict

In the independent rebeckerspecialties/wasm-benchmark run of 2026-09-22, WAMR fast-interp (main plus patches, cmake Release -O3 -mcpu=apple-a12, Apple clang 21.0.0, AOT/JIT off) took 1.63x the fastest runtime's CPU time per call versus 2.09x for Wasmtime v49 Pulley (fat LTO, tail-call dispatch) on M4 Max E-cores and 1.38x versus 1.68x on an iPhone XS A12, geomean over the 17 cases all seven interpreters run, N=10; I recomputed both geomeans from the per-case tables and they match. Results are checked against a cross-runtime consensus on every one of those cases except xmrsplayer, whose expected value is unset in cases.rs, and Pulley still wins fib, fib_tail, tailcall_fsm and extended-const instantiation.

## Use it when

- You may not generate native code (iOS/App Store, watchOS, W^X platforms) and want the fastest Wasm interpreter that still runs SIMD-128 and relaxed SIMD: on M4 E-cores WAMR fast-interp was the fastest of seven interpreters on sieve, crc32, matmul, convolution and the relaxed int8 dot product.
- Dispatch-heavy guest code (call_indirect, vtable-style polymorphism, AssemblyScript graphql) where Pulley ran 1.4-2.7x WAMR's CPU time.
- Microcontrollers and RTOSes (Zephyr, ESP-IDF, NuttX, VxWorks, RT-Thread): about 58.9K of text for the fast interpreter on cortex-m4f, with an option to confine all allocations to a caller-supplied buffer.
- Short-lived or freshly loaded modules where Cranelift compile time would dominate, since WAMR's load step is milliseconds instead of hundreds of milliseconds.
- Platforms that need precompiled native code without a JIT at runtime (wamrc AOT, execute-in-place, Intel SGX).

## Skip it when

- Raw MVP/scalar interpreter speed: wasm3 was faster on nearly every case it could run (geomean 1.01 vs WAMR 1.63 on M4, 1.04 vs 1.38 on A12).
- Modules that need Wasm 3.0 features in the fast interpreter: no exnref, memory64 or multi-memory there; GC and typed function references exist but cost 17-42% on call-heavy workloads when enabled; upstream refuses exception handling with FAST_INTERP=1.
- Component model or WASI 0.2/0.3 hosts: the core runtime has no component model; the benchmark's component-model fork ran the WASIp2 CLI component and failed every WASIp3 case, where Wasmtime and zwasm passed.
- Peak throughput against a JIT: the A-tier win is interpreter against interpreter, not against Wasmtime's Cranelift output; for native speed use WAMR's AOT/LLVM JIT modes and measure them yourself.
- Loading untrusted modules on an old build: the fast-interp loader had two memory-safety advisories in 2025-2026.

## How it is fast

The fast interpreter's loader rewrites stack-based Wasm into an internal code where each instruction carries its handler's address (direct-threaded dispatch through labels-as-values/computed goto, with a switch fallback) and operands are 16-bit frame-slot offsets, so most operand-stack pushes, pops and local.get/set copies disappear. The benchmark author attributes WAMR's lead over Pulley to this load-time register-IR rewrite: Pulley's bytecode mirrors the Wasm op stream with light fusion, so it dispatches more often per Wasm op. The rewrite is also cheap at load time (0.16 ms for vtable and about 6.9 ms for xmrsplayer, against about 10 ms and 213 ms of Cranelift lowering for Pulley, iPhone 12). Fast-interp SIMD is implemented on top of the SIMDe library; for AOT, wamrc adds LLVM optimisation, x86 segment-register 'segue' addressing and static PGO.

## Compared with alternatives

Pick WAMR over wasm3 when guests use SIMD, reference types or tail calls in an actively maintained runtime that also offers AOT and JIT tiers (wasm3 is faster on scalar MVP code but runs no SIMD); pick it over wasmz, which ties it on geomean (1.59 vs 1.63 on M4) but failed six rows on wrong results, traps and crashes. For Rust hosts on x86, Wasmi v2 and Silverfir-nano executed faster than WAMR fast-interp in the wasmi-benchmarks suite (12.40 and 9.02 vs 17.07 relative to the fastest).

## Integration

| | |
|---|---|
| **Form** | static lib (or shared lib), built with CMake |
| **Dependencies** | none for the interpreters; SIMDe is pulled in automatically for fast-interp SIMD; LLVM for wamrc and the LLVM JIT; optional uvwasi for WASI |
| **Minimum toolchain** | CMake plus a C compiler (GCC, Clang; MinGW and MSVC on Windows); minimum versions not documented |
| **Platforms** | x86-64, x86-32, ARM/Thumb, AArch64, RISC-V 32/64, Xtensa, MIPS, ARC; Linux, macOS, Windows, Android, iOS (via the darwin build), Linux SGX, Zephyr, ESP-IDF, NuttX, VxWorks, RT-Thread, AliOS-Things |
| **Thread safety** | An exec_env must not be used by several threads at once; give each thread its own exec_env (spawn_exec_env/spawn_thread APIs, lib-pthread or wasi-threads builds); default maximum of 4 threads unless max_thread_num is set. |
| **Drop-in for the baseline** | no |

## Gotchas

- Speed and features are compile-time CMake choices: the fast interpreter is about 2x the classic one but holds about 2x the memory for precompiled code, and enabling Fast JIT, LLVM JIT or the source debugger silently forces the classic interpreter; memory64 works only in classic and AOT modes.
- The benchmarked build is not a release: main b70d708d (WAMR-2.4.5 lacks its 364 commits) with 29 patches by the benchmark author, built with WAMR_DISABLE_HW_BOUND_CHECK=1 (software bounds checks, which also turns off native stack guard pages) as a workaround for a macOS touch_pages stack-walk bug. Patches 0028-0029 add a PROT_NONE linear-memory reservation because stock WAMR on Darwin grows memory by mmap + memcpy + munmap; that change took a growth-heavy Porffor workload from 63.6 ms to 9.7 ms on an iPhone 12, so stock builds will be slower on such workloads.
- Security history: 8 published advisories since 2025, including a critical heap overflow in WASI poll_oneoff and a fast-interp loader heap overflow fixed in WAMR-2.4.5 (2026-06-29), a frame_offset_bottom overflow in the fast interpreter (2025-11) and a uvwasi symlink sandbox escape; keep up with patch releases if modules are untrusted.
- The README says the project is moving from bytecodealliance/wasm-micro-runtime to github.com/wasm-micro-runtime/wasm-micro-runtime (old links redirect; the wamr.dev domain has not moved yet).

## Known shortcomings

- The fast-interpreter win is only over wasmtime's Pulley interpreter (geomean 1.63 vs 2.09 on M4, 1.38 vs 1.68 on A12; Pulley still wins fib, fib_tail, tailcall_fsm and extconst) and WAMR is slower than wasm3; the measured build was an unreleased main plus 29 patches. AOT mode numbers (libsodium 2022-12) lack CPU and flags, so that part is C at best.
- Enricher: the measured build is main b70d708d plus 29 author patches with WAMR_DISABLE_HW_BOUND_CHECK=1 (a macOS touch_pages workaround); stock Darwin memory.grow takes a slow mmap+memcpy+munmap path that patches 0028-0029 fix; the xmrsplayer row in the 17-case geomean has no consensus check (expected None in cases.rs); the fast interpreter lacks exnref, memory64 and multi-memory, and 8 security advisories in 2025-2026 include two in the fast-interp loader. The repo is moving to wasm-micro-runtime/wasm-micro-runtime.

## Caveats and trade-offs

WAMR is itself a category baseline; listed for its measured wins over Wasmtime's Pulley interpreter and, in AOT mode, over JIT runtimes. The win is interpreter versus interpreter, not versus Wasmtime's native Cranelift JIT. Pulley is not ahead everywhere: it beats WAMR on fib (1.13 vs 1.38 relative on M4), fib_tail, tailcall_fsm and extconst_init. In the same harness WAMR is slower than wasm3 (1.63 vs 1.01 geomean) and level with wasmz (1.59 on M4, 1.63 on A12). The benchmarked WAMR is unreleased main (the latest release, 2.4.5, lacks 364 of those commits) carrying 29 patches by the benchmark author (legacy EH, relaxed SIMD, PROT_NONE linear memory), and the Pulley side is a fork with 9 extra commits (including call_indirect argument bundling). Only Apple Silicon E-cores measured. AOT evidence (derived from page data, reproduced by the verifier): in jedisct1/webassembly-benchmarks 2022-12 libsodium CSVs (https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/iwasm.csv with wasmtime.csv, wasmer-cranelift.csv, wasmer-llvm.csv, node.csv, native.csv) the iwasm geomean time over the 61 tests common to all six files is 0.665x Wasmtime, 0.688x Wasmer Cranelift, 0.794x Wasmer LLVM and 0.588x Node/V8, and 2.30x native; the CSVs do not say iwasm ran in AOT mode (inferred from magnitude; CPU and flags not in the repo, and no README for that run). In the wasmi-benchmarks suite (AMD EPYC 7763, execute geomean relative to the fastest runtime per test, date not stated) WAMR fast-interp is 17.07 vs Pulley 27.92, but behind Wasm3 16.51, Wasmz 15.89, Wasmi v2 12.40 and Silverfir-nano's interpreter 9.02. WAMR wiki (https://github.com/bytecodealliance/wasm-micro-runtime/wiki/Performance, i7-7700, GCC 7.5.0 -O3, 2020-09-01) compares only against wasm3 and native.

Configurable runtime (classic and fast interpreter, AOT via wamrc, Fast JIT, LLVM JIT); README lists small text sizes on cortex-m4f (about 58.9K fast interpreter, 56.3K classic interpreter, 29.4K AOT runtime). The fast interpreter is slower than wasm3 (1.63x vs 1.01x in the cited doc).

## Maintenance

Actively developed (last commit 2026-09-30; latest release WAMR-2.4.5 of 2026-06-29 comes from a release branch cut in 2025-07, far behind main) by a Bytecode Alliance TSC with members from Intel, Sony, Amazon, Xiaomi, Siemens and Ant Group; Apache-2.0 with LLVM exception and usable as a library today.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent harness rebeckerspecialties/wasm-benchmark (crates/benchmark-core/src/cases.rs, scripts/build-wamr.sh, scripts/run-m4-pass.sh, all public) measures WAMR fast-interp against wasmtime v49 Pulley with Apple clang 21.0.0, stated flags (cmake Release -O3 -mcpu=apple-a12, AOT/JIT off; Pulley --cfg=pulley_tail_calls, fat LTO) on M4 Max E-cores and an A12; results are consensus-checked so wrong answers fail the row.
- **Verifier notes:** All numbers check against runtime-comparison-2026-09-22.md (geomeans 1.63/2.09 M4 and 1.38/1.68 A12; per-case ms) and docs/cross-runtime-pulley-vs-wamr.md (1.37-1.86x). The current merged record for this id (folded from the wasm and jit searches) also carries the libsodium 2022-12 AOT claim; I recomputed it from the CSVs and got the same 0.665/0.688/0.794/0.588/2.30 geomeans, but the run's mode, CPU and flags are unstated, so that part is tier C at best. Shortcomings: win is only over the Pulley interpreter, Pulley wins 4 cases, slower than wasm3, measured build is patched unreleased main.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/cross-runtime-pulley-vs-wamr.md>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/crates/benchmark-core/src/cases.rs>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/scripts/build-wamr.sh>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/scripts/run-m4-pass.sh>
  - <https://github.com/rebeckerspecialties/wasm-benchmark>
  - <https://github.com/rebeckerspecialties/wasm-benchmark/tree/HEAD/docs>
  - <https://github.com/bytecodealliance/wasm-micro-runtime>
  - <https://github.com/bytecodealliance/wasm-micro-runtime/commits>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/iwasm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmtime.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-cranelift.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-llvm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/node.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/native.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2021-Q1/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bytecodealliance/wasm-micro-runtime/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wasm-micro-runtime/HEAD/doc/perf_tune.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wasm-micro-runtime/HEAD/doc/embed_wamr.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wasm-micro-runtime/HEAD/doc/build_wamr.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wasm-micro-runtime/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wasm-micro-runtime/HEAD/core/iwasm/interpreter/wasm_interp_fast.c>
  - <https://github.com/bytecodealliance/wasm-micro-runtime/security/advisories>
  - <https://github.com/bytecodealliance/wasm-micro-runtime/releases>
  - <https://github.com/bytecodealliance/wasm-micro-runtime/wiki/Performance>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/cross-runtime-pulley-vs-wamr.md>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/scripts/build-wamr.sh>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/crates/benchmark-core/src/cases.rs>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/crates/benchmark-core/src/wamr.rs>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/crates/benchmark-core/src/lib.rs>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/bytecodealliance/wasm-micro-runtime`) · [data/wave12/enrich/raw/github_com_bytecodealliance_wasm_micro_runtime.json](../../../data/wave12/enrich/raw/github_com_bytecodealliance_wasm_micro_runtime.json) (enrichment confidence 0.75)

</details>
