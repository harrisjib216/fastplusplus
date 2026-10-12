# WAMR in Zig (cataggar/wamr)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `Apache-2.0` · 🟢 active

> Zig rewrite of WAMR with its own AOT/JIT compiler; about 4.9x faster CLI cold start than 'wasmtime run', 2.1x slower steady state.

| | |
|---|---|
| **Beats** | wasmtime run (default Cranelift JIT) |
| **Claimed result** | Cold start median: in-process JIT (.fast preset) 1.430 ms vs wasmtime 6.964 ms (about 4.9x faster); AOT warm 1.182 ms; AOT cold 2.552 ms. CoreMark steady state: wasmtime 26,462.6 iter/s vs JIT .fast 12,002.8 and AOT 12,442.8, i.e. wasmtime about 2.1x faster. |
| **Workload** | Cold start of a 36-byte no-op module (subprocess wall time, 20 samples after 3 warmups) comparing in-process JIT, AOT cold and warm modes against 'wasmtime run', plus CoreMark steady state. |
| **Metric** | startup |
| **Hardware** | Azure VM, 8 vCPU, AMD EPYC 9V74 80-Core Processor, x86_64 |
| **Compiler and flags** | zig build -Djit=true -Doptimize=fast (ReleaseFast) via scripts/bench_jit_coldstart.py, measured at PR-branch commit 329c29b5 whose build.zig.zon requires Zig &gt;= 0.16.0 (HEAD now requires the signed cataggar/zig 0.17.0); wasmtime taken from \~/.wasmtime/bin with no version stated. |
| **Adoption** | 5 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/cataggar/wamr) · [benchmark](https://github.com/cataggar/wamr/blob/HEAD/docs/bench/jit-cold-start-comparison-2026-07-10.md) |

## Verdict

The author's own run (2026-07-10, AMD EPYC 9V74 8-vCPU Azure VM, zig build -Djit=true -Doptimize=fast at commit 329c29b5, wasmtime version not stated) timed whole-process 'wamr run noop.wasm' with the in-process JIT at a 1.430 ms median against 6.964 ms for 'wasmtime run', about 4.9x faster. On CoreMark, Wasmtime reached 26,462.6 iter/s against 12,442.8 for wamr AOT (3 runs each), so the win is startup-only and there is no baseline against upstream C WAMR.

## Use it when

- One-shot CLI invocations of small modules or components where process startup dominates: 1.43 ms for a no-op module against 6.96 ms for 'wasmtime run' on an 8-vCPU EPYC 9V74 VM.
- Precompiled deployments: 'wamr run' on a .cwasm started in 1.18 ms, and the AOT-only binary carries no compiler.
- Zig projects that want a Zig-native runtime with Component Model and WASI 0.3 (README: 41/41 Preview 3 fixtures and 70/72 Preview 1 fixtures pass, plus the full core spec suite).
- Unikraft-style or compiler-free embedding, where the host owns page tables and loads trusted .cwasm through wamr_aot.h.

## Skip it when

- Compute-bound or long-running guests: Wasmtime ran CoreMark at 26,462.6 iter/s against 12,442.8 (AOT) and 12,002.8 (JIT .fast), about 2.1x faster; open issues #949, #985 and #986 track a further AArch64 CoreMark gap.
- C/C++ hosts that want upstream WAMR: different API, no interpreter on the CLI (the interpreter is reachable only through the library), binaries of about 17 MB (AOT-only) and 25 MB (with JIT) instead of upstream's tens-of-KB microcontroller builds, and no listed MCU/RTOS targets.
- Security-sensitive or production hosting of untrusted code: 5 stars, 0 forks, maintained with AI assistance, and no audit; the README itself points to Wasmtime's track record and security audits.
- SIMD-heavy AOT workloads: in the 2026-05-29 optimize-mode report every SIMD AOT row was 'unsupported' (the interpreter ran them); current AOT SIMD coverage is not documented in the files read.
- Modules large enough to compile for real on every run: the JIT keeps no persistent cache, so each invocation pays compile latency, which the no-op benchmark does not measure.

## How it is fast

The cold-start lead comes from a lean one-process path. The JIT build links the compiler into wamr, compiles the module in memory with a 'fast' pass preset tuned for compile latency, and executes it through the same AOT loader and runtime, so a trivial module costs one execve and almost no compile work. The project's doc attributes wasmtime's 6.96 ms to a higher fixed per-invocation Cranelift/engine startup that a no-op module cannot amortize. The compiler is its own SSA IR (passes such as inlineSmallFunctions and promoteLocalsToSSA) with x86_64 and aarch64 backends, neither LLVM nor Cranelift, which is why steady-state code is about half as fast as Wasmtime's.

## Compared with alternatives

Choose upstream WAMR (bytecodealliance) for C embedding, microcontrollers, interpreters and maturity; choose this only for Zig-hosted, CLI-style AOT/JIT runs with WASI 0.3 components. zwasm (also Zig) targets the same startup-bound niche (tinygo/fib 2.0 ms against wasmtime's 7.2 ms) and adds an interpreter tier; no measurement compares the two.

## Integration

| | |
|---|---|
| **Form** | CLI binaries (wamr, wamrc) and a Zig package; compiler-free C header include/wamr_aot.h for loading precompiled .cwasm |
| **Dependencies** | Zig toolchain plus Zig packages pinned in build.zig.zon: cataggar/wabt fork, cataggar/tls.zig and a wasip2 package (README says 'no dependencies', meaning no system libraries) |
| **Minimum toolchain** | HEAD build.zig.zon sets minimum_zig_version 0.17.0 (the signed cataggar/zig 0.17.0 build, per the README banner), while the README body still says Zig 0.16; the benchmarked commit 329c29b5 required Zig 0.16.0 |
| **Platforms** | x86_64 and aarch64 native code generation (Linux; README shows cross-compiles to aarch64-macos and x86_64-windows); wasm32-wasi build is interpreter-only, with no AOT/JIT, components or threads |
| **Thread safety** | wamr_aot.h: all operations on one instance must be serialized, and an active instance must never be destroyed; otherwise not documented |
| **Drop-in for the baseline** | partial: 'wamr run foo.wasm' mirrors 'wasmtime run' only in a -Djit=true build; flags, cache, embedding API and .cwasm format differ from Wasmtime and from upstream WAMR |

## Gotchas

- Every number was measured with ReleaseFast although the README recommends ReleaseSafe. In the project's 2026-05-29 optimize-mode report, the ReleaseSafe wamrc aborted on CoreMark with 'IR verifier: MultipleTerminators after pass inlineSmallFunctions' (issue #631, since closed), while the ReleaseFast build compiled the same code without complaint. The IR verifier is still opt-in for the differential test suite (docs/ir-verifier-triage.md). bench_jit_coldstart.py parses only CoreMark's 'Iterations/Sec' line and never checks its CRC validation output. This harness gap touches only the throughput rows (where wamr loses anyway), not the cold-start win.
- The same 2026-05-29 report shows a real workload (an Azure keyvault codegen CLI) failing in both modes: ReleaseFast trapped 'out of bounds memory access' inside a guest hash-map function, and ReleaseSafe hit a host panic 'access of union field enum_val while field variant_val is active'.
- The cold-start figure is subprocess wall time for a 36-byte no-op module: 20 samples after 3 warmups on one 8-vCPU Azure VM, with the wasmtime binary taken from \~/.wasmtime/bin and its version unrecorded. No aarch64 numbers.
- Only the name and fork history are shared with bytecodealliance/wasm-micro-runtime: the compiler, the .cwasm format, the CLI and the C API are new, so upstream WAMR docs, CMake flags and benchmarks do not apply, and no comparison against upstream C WAMR exists.

## Known shortcomings

- Win only on a 36-byte no-op cold start (4.9x); wasmtime is 2.1x faster on CoreMark. No comparison against upstream C WAMR, Zig and wasmtime versions not stated, AI-maintained, 5 stars. Zig, not C++.
- Enricher: throughput rows come from ReleaseFast builds while the project's own 2026-05-29 report has the ReleaseSafe wamrc aborting on CoreMark ('IR verifier: MultipleTerminators after pass inlineSmallFunctions', issue #631), bench_jit_coldstart.py never checks the CoreMark CRC validation line, the keyvault codegen workload fails in both modes, and AOT SIMD rows were unsupported in May 2026. Own SSA compiler, .cwasm format and C API (wamr_aot.h), not upstream WAMR code; 17-25 MB binaries; HEAD needs Zig 0.17.0 while the README says 0.16.

## Caveats and trade-offs

Cold-start win is on a trivial 36-byte no-op module where wasmtime's fixed per-invocation cost dominates (process spawn included, 20 samples after 3 warmups); the doc itself says wasmtime is about 2.1x faster on CoreMark steady state (3 runs per mode). No comparison against upstream C WAMR, the project this ports to Zig, so it does not show being faster than its origin. Benchmarked with ReleaseFast while the README recommends ReleaseSafe builds. Single x86_64 host, no aarch64 numbers; wasmtime and Zig versions not stated in the doc. Small fork maintained with AI assistance (every recent commit co-authored with GitHub Copilot); 5 stars.

Zig port of bytecodealliance/wasm-micro-runtime kept as a separate fork (not drop-in for C++ callers without the Zig toolchain); passes the spec suite (257 .wast files, 65,135 assertions) per README; CLI is AOT/JIT only. Steady-state throughput is about half of wasmtime.

## Maintenance

Very active (last commit 2026-10-05, about 3,466 commits) but a 5-star personal fork maintained with AI assistance and now tied to a custom signed Zig 0.17.0 build; Apache-2.0 and usable, but treat it as experimental for anything beyond startup-bound CLI use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party doc with public harness (scripts/bench_jit_coldstart.py at HEAD), build flags (-Djit=true -Doptimize=fast) and CPU model (AMD EPYC 9V74, 8 vCPU Azure VM), but the Zig compiler version and the wasmtime version are not stated, so not A.
- **Verifier notes:** Bench doc numbers match the record exactly (JIT .fast 1.430 ms vs wasmtime run 6.964 ms cold start, about 4.9x; CoreMark wasmtime 26,462.6 vs AOT 12,442.8 iter/s). Shortcomings to record: startup-only win on a no-op module, about 2.1x slower than wasmtime on throughput, no upstream-WAMR comparison, tool versions unstated. Metadata checked: Apache-2.0, fork of bytecodealliance/wasm-micro-runtime, 5 stars, last commit 2026-10-05, active.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cataggar/wamr>
  - <https://github.com/cataggar/wamr/commits>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/docs/bench/jit-cold-start-comparison-2026-07-10.md>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/README.md>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/scripts/bench_jit_coldstart.py>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/cataggar/wamr/329c29b5/build.zig.zon>
- **Sources the enricher read:**
  - <https://github.com/cataggar/wamr>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/README.md>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/docs/bench/jit-cold-start-comparison-2026-07-10.md>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/docs/bench/optimize-mode-comparison-2026-05-29.md>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/docs/bench/native-linux-producer.md>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/docs/ir-verifier-triage.md>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/scripts/bench_jit_coldstart.py>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/cataggar/wamr/HEAD/include/wamr_aot.h>
  - <https://github.com/cataggar/wamr/tree/main/docs/bench>
  - <https://github.com/cataggar/wamr/tree/main/docs>
  - <https://github.com/cataggar/wamr/tree/main/src>
  - <https://github.com/cataggar/wamr/tree/main/src/compiler>
  - <https://github.com/cataggar/wamr/tree/main/src/compiler/codegen>
  - <https://github.com/cataggar/wamr/tree/main/include>
  - <https://github.com/cataggar/wamr/issues?q=is%3Aissue>
  - <https://github.com/cataggar/wamr/issues/393>
  - <https://github.com/cataggar/wamr/issues/631>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/cataggar/wamr`) · [data/wave12/enrich/raw/github_com_cataggar_wamr.json](../../../data/wave12/enrich/raw/github_com_cataggar_wamr.json) (enrichment confidence 0.6)

</details>
