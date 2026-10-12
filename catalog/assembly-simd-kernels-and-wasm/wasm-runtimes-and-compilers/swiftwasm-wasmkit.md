# WasmKit register-based interpreter (swiftwasm/WasmKit)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly runtimes and compilers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Swift` · `MIT (runtime modules); the GDBRemoteProtocol and WasmKitGDBHandler modules are Apache-2.0 with a Runtime Library Exception` · 🟢 active

> Pure-Swift embeddable WebAssembly interpreter; register-based VM scores 7.5x its old stack interpreter on CoreMark, roughly level with wasm3.

| | |
|---|---|
| **Beats** | WasmKit's own previous (second-generation) stack-based interpreter; also charted against wasm3, stitch and wasmi |
| **Claimed result** | Docs: CoreMark score 7.4x higher than WasmKit's own second-generation interpreter; versus wasm3, stitch and wasmi the doc says only 'well competitive'. Values read from the chart SVGs (derived from page data): WasmKit 0.1.0 2172.83 iterations/s, wasm3 2180.79, stitch 2280.91, wasmi 1321.24, so WasmKit trails wasm3 by 0.4% and stitch by 4.7% in the same run. The 0.0.8 bar (291.24) and the wasmi bar (1321.24) are the exact figures of the earlier second-generation log already in PR #115 (merged 2024-08-14), while the 0.1.0 bar comes from a 2024-09-17 snapshot, so the 7.4x and the 1.64x-over-wasmi ratios are cross-run; wasmtime (JIT) in the same old log reached 11527. |
| **Workload** | CoreMark compiled to Wasm, interpreted by the old and new WasmKit interpreters and, in a second chart, by wasm3, stitch and wasmi. |
| **Metric** | throughput |
| **Hardware** | 2020 Mac mini (M1, 16GB RAM) |
| **Compiler and flags** | WasmKit built with swift build -c release, toolchain swift-DEVELOPMENT-SNAPSHOT-2024-09-17-a; CoreMark built with wasi-sdk clang 18.1.2 -O3 -D_WASI_EMULATED_PROCESS_CLOCKS (from the CoreMark log on the same page and Benchmarks/bench.py PORT_CFLAGS) |
| **Adoption** | 509 stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/swiftwasm/WasmKit) · [benchmark](https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Documentation/RegisterMachine.md) |

## Verdict

First-party CoreMark (wasi-sdk clang 18.1.2 -O3) on a 2020 M1 Mac mini: the register interpreter (WasmKit 0.1.0, swift-DEVELOPMENT-SNAPSHOT-2024-09-17-a, swift build -c release) scored 2172.8 versus 291.2 for the 0.0.8 stack interpreter (7.46x, derived from page data), where the 291.2 comes from an earlier run; in the interpreter chart it trails wasm3 (2180.8) and stitch (2280.9) and leads a reused wasmi figure (1321.2).

## Use it when

- Running Wasm inside a Swift app or server without bundling a C/C++ or Rust runtime and its build system
- iOS, tvOS, watchOS, visionOS or other targets where JIT is not allowed, so an interpreter is the only choice
- Unoptimised or debug-built Wasm (heavy local.get/const traffic), the case the register design was built for
- Embedded Swift and bare-metal targets (an ESP32 example ships), using token threading by default
- Tooling that needs WAT parsing, validation, fuel-bounded execution or a GDB remote stub in the same Swift package

## Skip it when

- Throughput-bound workloads where a JIT is allowed: the project's own log shows wasmtime about 5.3x the register interpreter's CoreMark score (derived from page data, cross-run)
- Picking the fastest interpreter: in the project's own chart wasm3 (2180.8) and stitch (2280.9) score at or above WasmKit 0.1.0 (2172.8)
- Big-endian hosts (the C shim refuses to compile), or architectures outside x86, x86-64, ARM and AArch64, which get only the token-threaded fallback loop (its speed relative to direct threading is not documented)
- Wasm GC modules (decoded but refused by the translator) or full WASI Preview 2/component model (in progress)
- Functions whose frame exceeds the interpreter's operand reach: they are rejected with 'The frame of this function is too large for the interpreter'

## How it is fast

A single-pass translator turns Wasm stack code into register-machine instructions, after the WAMR fast-interpreter design: 'provider' instructions (local.get, constants) disappear into operand slots of the consuming instruction and local.set is fused into the producer, which matters most for unoptimised (-Onone) Wasm. Dispatch is direct-threaded: each handler is a C function in a header that calls the Swift semantics inline and tail-calls the next handler under the swiftasync (or musttail) convention, with a token-threaded loop as the fallback. The frame layout borrows from the stitch interpreter, and every value occupies a uniform 64-bit slot.

## Compared with alternatives

Pick WasmKit over KinoWASM, wasman or DTVM when the host is Swift or Apple's JIT-free platforms and you want a SwiftPM dependency with no C/Rust toolchain; for raw interpreter speed in a C host KinoWASM's own CoreMark (4385.7 vs wasm3 3555.6) and wasm3 itself score higher, and DTVM is a JIT for a different speed class.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none for the core engine (no Foundation, no external packages); swift-argument-parser and swift-syntax for the CLI and WIT tooling |
| **Minimum toolchain** | Swift 6.3 (swift-tools-version 6.3, uses the experimental RawLayout feature); macOS 15 / iOS 18 deployment targets |
| **Platforms** | macOS 15+, iOS 18+, tvOS, watchOS, visionOS, Linux (Ubuntu 22.04+, Debian 12, Fedora 39+, Amazon Linux), Android API 30, Windows 10+, Embedded Swift bare metal; little-endian only; direct threading only on x86, x86-64, ARM, AArch64 |
| **Thread safety** | Engine is marked @unchecked Sendable (immutable configuration, synchronised type interner; not with interceptors); Store is thread-confined, and each WASI thread gets its own Store |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the only quantified claim: the chart's WasmKit 0.0.8 bar (291.240274) and wasmi bar (1321.236383) are the exact figures from the earlier second-generation log, which already appears in PR #115 (merged 2024-08-14), while the 0.1.0 bar (2172.826551) comes from a later run on the 2024-09-17 snapshot; the 7.4x and the 1.64x-over-wasmi ratios are cross-run, and neither the wasmi version nor the wasm3/stitch builds are named (bench.py has no stitch engine).
- The 'well competitive' sentence hides numbers: rasterising the chart SVG (labels are outlined glyphs) gives WasmKit 2172.8, wasm3 2180.8, stitch 2280.9, wasmi 1321.2, so WasmKit is 0.4% behind wasm3 and 4.7% behind stitch (derived from page data); it beats no external interpreter in the same run.
- The .mprotect bounds-check mode installs process-wide SIGSEGV/SIGBUS handlers and reserves 4 GiB plus a guard tail of address space per wasm32 memory, yet the interpreter still runs checked loads and stores in that mode; .software avoids the signal handlers at little cost.
- Default interpreter stack is 512 KB; deep recursion traps with 'call stack exhausted' until EngineConfiguration.stackSize is raised. Fuel metering is translation-time, so code translated without it cannot be budgeted later (overhead reported under 10% in issue #421).

## Known shortcomings

- 7.4x only against its own gen-2 interpreter; the wasm3/stitch/wasmi chart has no readable numbers and the README says only 'well competitive'. Licence MIT plus Apache-2.0 GDB modules.
- Cross-run claim: rasterising the chart SVGs gives WasmKit 0.1.0 2172.83, wasm3 2180.79, stitch 2280.91 and wasmi 1321.24 CoreMark iterations/s, so WasmKit trails wasm3 by 0.4% and stitch by 4.7% and beats no external interpreter in the same run (derived from page data); the 0.0.8 bar (291.24) and the wasmi bar (1321.24) were copied from the earlier gen-2 log already in PR #115 (merged 2024-08-14) while the 0.1.0 bar comes from a 2024-09-17 snapshot, so the 7.46x and the 1.64x-over-wasmi ratios are cross-run and the wasmi version is unstated.

## Caveats and trade-offs

The headline 7.4x is against WasmKit's own older stack-based interpreter, not an external incumbent. Against wasm3, stitch and wasmi the doc only shows a chart (SVG with outlined glyphs, values not readable) and says 'well competitive', so no faster-than-incumbent claim exists. The second-generation CoreMark log on the same page shows WasmKit gen-2 at 291 iterations/s, wasmi at 1321 and wasmtime (JIT) at 11527; 7.4x of 291 is about 2155 iterations/s (derived from page data), still roughly 5x below wasmtime, and the log's machine and wasmi version are not stated, so a wasmi comparison cannot be derived. The doc says 'we have not done a comprehensive performance evaluation yet'. Single machine (2020 Mac mini M1), single CoreMark run, 2024-09 toolchain snapshot, so numbers are old for the 2026 code. A Benchmarks/bench.py harness (CoreMark, wasmi-benchmarks replay, wasm3/wasmi/wasmtime engines) exists in the repo but no results report. [retier] The headline 7.4x is against WasmKit's own older stack-based interpreter, not an external incumbent, and is cross-run (0.1.0 measured on 2024-09-17 against 0.0.8 and wasmi figures copied from an earlier log). In the same run WasmKit beats no external interpreter (0.4% behind wasm3, 4.7% behind stitch); the machine, wasmi version and wasm3/stitch builds are not named (bench.py has no stitch entry). The .mprotect bounds-check mode installs process-wide SIGSEGV/SIGBUS handlers and reserves 4 GiB plus a guard tail per wasm32 memory while still running checked loads and stores; the default interpreter stack is 512 KB; fuel metering is translation-time (overhead under 10% per issue #421).

Swift runtime; runtime modules are MIT, the GDBRemoteProtocol and WasmKitGDBHandler modules are Apache-2.0 with Runtime Library Exception. Interpreter only, no JIT or AOT; no Fixed-width SIMD claim checked.

## Maintenance

Actively maintained (0.4.2 tagged 2026-10-11, community-maintained, bundled with Swift 6.2+ toolchains) and MIT-licensed except the Apache-2.0 GDB modules; usable today, but the only published performance numbers date from the 2024 0.1.0 interpreter and mix two runs, so treat it as a wasm3-class interpreter rather than a faster one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party doc (Documentation/RegisterMachine.md) states a 7.4x CoreMark gain over WasmKit's own second-generation interpreter on an M1 Mac mini with a named Swift snapshot; the comparison with wasm3, stitch and wasmi is a chart without numbers and only claims 'well competitive'. The doc does not name its harness (Benchmarks/bench.py exists now but cannot be tied to the 2024 run), so C.
- **Retiered** C to D: Enricher: the only quantified claim (7.4x over the second-generation interpreter, 1.64x over wasmi) divides a 2024-09-17 run by figures copied from an earlier log (PR #115), and rasterising the chart shows WasmKit 0.1.0 at 2172.8 CoreMark iterations/s against wasm3 2180.8 and stitch 2280.9 in the same run, so it beats no external interpreter. Cross-run ratio with no faster-than-incumbent result: C to D.
- **Verifier notes:** Accurate record; kept at C. Shortcoming: self-relative 7.4x only, no numeric win over wasm3/stitch/wasmi/wasmtime. An A case exists only for the self-relative claim (M1, Swift snapshot, -O3 CoreMark) but the harness used is unnamed. Metadata checked: 509 stars, last commit 2026-10-11, active.
- **Fields the verifier corrected:** `license`, `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-16 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Documentation/RegisterMachine.md>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/README.md>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Benchmarks/bench.py>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Benchmarks/README.md>
  - <https://github.com/swiftwasm/WasmKit>
  - <https://github.com/swiftwasm/WasmKit/commits>
  - <https://github.com/swiftwasm/WasmKit/tree/main/Benchmarks>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/README.md>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Documentation/RegisterMachine.md>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Documentation/MprotectMemoryBoundsChecking.md>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Documentation/StackLayout.md>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Benchmarks/README.md>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Benchmarks/bench.py>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Package.swift>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Sources/WasmKit/Engine.swift>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Sources/WasmKit/Execution/Store.swift>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Sources/_CWasmKit/include/_CWasmKit.h>
  - <https://raw.githubusercontent.com/swiftwasm/WasmKit/HEAD/Sources/_CWasmKit/include/Platform.h>
  - <https://github.com/user-attachments/assets/2c400efe-fe17-452d-b86e-747c2aba5ae8>
  - <https://github.com/user-attachments/assets/f43c129c-0745-4e52-8e92-17dadc0c7fdd>
  - <https://github.com/swiftwasm/WasmKit>
  - <https://github.com/swiftwasm/WasmKit/issues>
  - <https://github.com/swiftwasm/WasmKit/issues?q=is%3Aissue+performance>
  - <https://github.com/swiftwasm/WasmKit/issues/421>
  - <https://github.com/swiftwasm/WasmKit/pull/115>
  - <https://github.com/swiftwasm/WasmKit/commits/main>
  - <https://github.com/swiftwasm/WasmKit/commits/main/Documentation/RegisterMachine.md>
  - <https://github.com/swiftwasm/WasmKit/tree/main/Documentation>
  - <https://github.com/swiftwasm/WasmKit/tags>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/swiftwasm/wasmkit`) · [data/wave13/enrich/raw/github_com_swiftwasm_wasmkit.json](../../../data/wave13/enrich/raw/github_com_swiftwasm_wasmkit.json) (enrichment confidence 0.6)

</details>
