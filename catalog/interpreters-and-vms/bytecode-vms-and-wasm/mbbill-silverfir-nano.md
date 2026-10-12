# Silverfir-nano

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust no_std Wasm 3.0 runtime with interpreter and on-device JIT; interpreter about 1.9x WAMR fast-interp on wasmi-benchmarks.

| | |
|---|---|
| **Beats** | WAMR fast interpreter (execution) and Wasmtime Cranelift (startup) |
| **Claimed result** | Execution geomean on AMD EPYC 7763 relative to the per-case fastest runtime (lower is better): Silverfir-nano interpreter x9.02 versus WAMR fast-interpreter x17.07, Wasm3 (eager) x16.51 and Wasmtime (Pulley) x27.92 (about 1.9x faster than WAMR, derived from page data); Silverfir-nano JIT x1.25, close to but not beating Wasmtime (Cranelift) x1.15, Wasmer (Cranelift) x1.17 and V8 x1.05; Wasmtime (Winch) is x2.35 and Wasmer (Singlepass) x2.95. |
| **Workload** | wasmi-benchmarks execution suite: 22 cases (counters, fibonacci, sort, nbody, argon2, json-parse, regex-redux and others), geometric mean of per-case ratios against the fastest runtime for each case. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7763 (named in the plot title; the plots repo also holds data for Apple M2 Pro, Apple M4 Pro, an Intel i7700 and Intel Xeon Platinum 8573C, not read here) |
| **Compiler and flags** | Guests: wasi-sdk clang (version not stated) -O2 --target=wasm32-wasip1 via benchmarks/wasi/Makefile, binaries committed and shared by all engines. Silverfir: cargo --release, workspace profile lto=true, codegen-units=1, opt-level=3. wasmtime Cranelift and Winch 47.0.2 built from source with rustc 1.97.0; Node 25.9.0 (V8 14.1.146); wasm3 '\~/Dev/wasm3 build-release' (commit and flags not stated); wasmi_cli 2.0.0-beta.7 via cargo install (CoreMark cell 2.0.0-beta.10). Harness: benchmarks/wasi/run_tests.py and run_v8.mjs. |
| **Adoption** | 67 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/mbbill/Silverfir-nano) · [benchmark](https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg) |

## Verdict

In the wasmi-benchmarks suite, run by the wasmi author (a competitor) on an AMD EPYC 7763 with Silverfir-nano tag 0.5, the Silverfir interpreter's execute geomean is 9.02x the fastest runtime per case, against 17.07x for WAMR fast-interp, 16.51x for Wasm3 and 12.40x for Wasmi v2. That makes it about 1.9x faster than WAMR and 1.37x faster than Wasmi (derived from page data). Its JIT is 1.25x vs Cranelift 1.15x and V8 1.05x on that machine, but leads on Apple M2 Pro and M4 Pro. The first-party Apple M4 suite (wasi-sdk clang -O2 guests, Silverfir LTO opt-level 3) puts the interpreter 1.07-1.69x ahead of the better of Wasm3 and Wasmi per row and the JIT at parity with wasmtime 47.0.2 Cranelift.

## Use it when

- You need a pure interpreter (W^X platforms, no executable memory, smallest flash) and want the fastest one measured: wasmi-benchmarks execute geomean on AMD EPYC 7763 is 9.02 vs Wasmi v2 12.40, Wasm3 16.51 and WAMR fast-interp 17.07 (lower is better), and it was the fastest interpreter on all five machines in that suite (M2 Pro, M4 Pro, i7700, Xeon 8573C, EPYC).
- Microcontroller deployments where you ship a .wasm and want either tier on chip: recorded RP2350 firmware is 337 KiB flash with the interpreter and about 1,042 KiB with the JIT, on Cortex-M33 and Hazard3 RV32, plus an ESP32-C6 port.
- Apple Silicon hosts that want Cranelift-class compiled throughput from a small no_std crate: its JIT had the best execute geomean of all 23 configurations on Apple M2 Pro (1.06) and M4 Pro (1.07) in wasmi-benchmarks.
- Products that need one runtime across x86_64, ARM64, RV64, RV32, ARMv7-A and Thumb-2 with the same embedding API for interpreter and JIT.

## Skip it when

- x86-64 throughput-bound hosts: the JIT trails Cranelift and V8 there (wasmi-benchmarks execute geomean EPYC 7763 1.25 vs 1.15 and 1.05; i7700 1.46 vs 1.25 and 1.13; Xeon 8573C 1.28 vs 1.21 and 1.04), and the first-party Apple M4 table has Cranelift winning 9 of 15 metrics.
- Startup-dominated workloads on the interpreter: its eager predecode makes startup geomean 61.98 on EPYC vs WAMR 56.73, Wasm3 (eager) 51.60 and Wasmi v2 (lazy) 1.37, so Wasmi's lazy modes start far faster.
- Modules that use SIMD or GC on the interpreter (refused at instantiation by design), or SIMD on the RV and ARMv7 JIT backends (JIT SIMD needs ARM64 NEON or x86_64 SSSE3+SSE4.1).
- C or C++ hosts: only a Rust API is documented, unlike WAMR and wasm3.
- Teams needing a long production record: 67 stars, 29 crates.io downloads, a single maintainer, a 0.x API, and design notes (docs/decisions.json) still consolidating about 19 raw \*mut Store dereferences into one audited checkout primitive; no fuzzing setup is mentioned in the docs read.

## How it is fast

The interpreter is a 'folded stack machine': a predecode pass folds Wasm operand-stack traffic into handlers that address 8-byte frame slots directly, and build.rs generates the whole dispatch engine as one global_asm! blob (about 10,300 handler variants specialised by operand class, including pinned-register locals, address-fused loads/stores and pair moves) with absolute branch targets and a hot-families-first emission order. The JIT lowers Wasm to Semantic IR, SSA-IR, MachineIR and native code, gives locals and deep stack values fixed frame-slot homes so only short-lived transients need register allocation, and uses a region-based cache-residency allocator (docs/ALGORITHM4.md) plus late peepholes (addressing-mode fusion, load/store forwarding, branch fusion); guard pages let it elide bounds checks.

## Compared with alternatives

Pick it over Wasmi, Wasm3, Stitch or the WAMR fast interpreter when execution speed of a pure interpreter matters most and the modules need no SIMD or GC: it led every interpreter on all five wasmi-benchmarks machines. Pick Wasmi (lazy) for startup-bound or many-short-lived-instance workloads, and WAMR or Wasm3 when you need a C API and a longer production record.

## Integration

| | |
|---|---|
| **Form** | crate (sf-nano-core; cargo features jit, interp, guard-pages, wasi; defaults jit+interp+guard-pages) |
| **Dependencies** | sf-nano-tracked-alloc (same repository); optional filetime for wasi; needs alloc; bare-metal JIT embedders must supply executable-memory and instruction-cache hooks |
| **Minimum toolchain** | Rust 1.94 (rust-version in sf-nano-core/Cargo.toml, edition 2021) |
| **Platforms** | x86_64, ARM64, RV64, RV32, ARMv7-A, Thumb-2 for both engines; CI runs x64 Linux, ARM64 Linux, ARM64 macOS and x64 Windows MSVC natively, ARMv7/RV64/RV32 under QEMU, and builds bare-metal thumbv8m and RV32IMAC |
| **Thread safety** | not documented; memory views are exclusive within a RuntimeWorld and design notes describe Rc-shared internals, so treat an engine and its instances as single-threaded; eager JIT compilation of large modules is spread over multiple threads by default (Config::parallel_compilation) |
| **Drop-in for the baseline** | no |

## Gotchas

- Interpreter scores depend on where its handlers land in memory: docs/HANDLER_LAYOUT.md records 48 bytes of unreachable padding moving x64-windows sha256 from -14.83% to +0.27% and arm64-linux STREAM Scale by +103.49%. The fix (pinned 64-byte phase boundaries) landed 2026-08-01, after the 2026-07-25 interpreter column in RESULTS.md, so its micro-kernel rows (sha256, STREAM, CoreMark) may include layout luck in either direction.
- The first-party wasmi column is disputed: in issue #11 (2026-07-27) the wasmi author said the CoreMark numbers looked like wasmi 1.0.9 rather than 2.0.0-beta.7 and that on Apple Silicon Wasm3 and Wasmi beta.7 CoreMark are very close. The issue was closed with no visible reply, and the CoreMark interpreter row was later replaced by standalone scores (wasmi beta.10), so that row mixes measurement modes. Interpreters are single runs, and the wasm3 build is unpinned.
- Harness asymmetries in RESULTS.md: wasmtime 47 returns 0.0 from Lua's os.clock(), so the Lua rows on wasmtime used a 1-second os.time() fallback while other engines used the high-resolution path; the sqlite row is historical speedtest1 data that the current suite no longer runs.
- Engine limits: the JIT once failed to instantiate the SpiderMonkey startup module on Linux and Windows ('linear-value budget exhausted during cache alias materialization', issue #10, fixed in PR #16). The JIT passes host-thrown exceptions to the embedder even when Wasm declares a handler. Interpreter host functions return at most eight results. Module::new_unchecked is unsafe.

## Known shortcomings

- Borderline A: wasi-sdk version and the wasm3 build commit are not stated, interpreter numbers are single runs, the baseline is wasmtime 47.0.2 (one major version old) and CoreMark runs in bounded mode. The JIT is only at parity with Cranelift (Cranelift wins 9 of 15 rows); the clear win is interpreter-only. Rust, not C++.
- Enricher: docs/HANDLER_LAYOUT.md shows interpreter scores swing with handler placement (48 B of padding moved sha256 from -14.83% to +0.27% and STREAM Scale by +103.49%) and the fix landed 2026-08-01, after the 2026-07-25 interpreter column, so micro-kernel rows may hold layout luck; issue #11 (wasmi author: RESULTS.md's wasmi CoreMark looks like v1.0.9) was closed without a visible reply; the wasmtime Lua rows were timed on a 1 s os.time() fallback. Interpreter startup 61.98 vs WAMR 56.73; the JIT trails Cranelift and V8 on x86 (EPYC 1.25 vs 1.15 and 1.05) and leads only on M2 Pro and M4 Pro.

## Caveats and trade-offs

First-party suite, one machine (M4), interpreters are single runs (author says treat as +/-5%) while compiled engines are the mean of two rounds; Cranelift still wins 9 of 15 metrics and is ahead on sqlite and LZ4 decompress (3,478 vs 3,241), so the JIT claim is parity, not a win. Wasmtime 47.0.2 and V8 14.1 are older than current releases (wasmtime v49 was current in September 2026); the numbers are dated 2026-07-24/25 and share no baseline with earlier revisions of the file. CoreMark runs in a non-standard bounded regression mode, except the interpreter CoreMark row, which was refreshed on 2026-08-31 with standalone scores and uses wasmi 2.0.0-beta.10 rather than beta.7. The wasm3 build compared against is not pinned to a version. The sqlite and Lua rows are historical (the active suite has changed those benchmarks). Independent cross-check in the wasmi-benchmarks suite (wasmi-labs, AMD EPYC 7763, plot raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg, date not stated, 23 runtime configurations): execute geomean relative to the fastest runtime per test is Silverfir interpreter 9.02 vs Wasmi v2 12.40, Wasm3 16.51, WAMR fast-interp 17.07 and Pulley 27.92 (fastest interpreter, about 1.37x ahead of Wasmi v2, derived from page data), and Silverfir JIT 1.25 vs Wasmtime Cranelift 1.15, Wasmer Cranelift 1.17 and V8 1.05, so the JIT trails the optimizing compilers slightly on that suite. That suite is run by the author of wasmi, a competing interpreter.

Ships both an interpreter and an on-device optimizing JIT; no_std; targets six ISAs from x86_64 and ARM64 down to RV32 and Thumb-2. Binary 337 KiB with the interpreter and 1,042 KiB with the JIT (README, RP2350 firmware).

## Maintenance

Actively developed by one maintainer (1,306 commits, last commit 2026-10-03, crates.io 0.6.0 on 2026-09-09) under MIT OR Apache-2.0, usable as a crate today, but young and not yet hardened for hostile modules.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** benchmarks/wasi/RESULTS.md compares the Silverfir JIT with wasmtime Cranelift 47.0.2 (built from source, rustc 1.97.0) and V8 (Node 25.9.0, V8 14.1.146) on an Apple M4; the harness (benchmarks/wasi/run_tests.py, run_v8.mjs) and the guest build (benchmarks/wasi/Makefile: wasi-sdk clang -O2 --target=wasm32-wasip1, committed .wasm shared by every engine) are public, and Silverfir's release profile (lto, codegen-units=1, opt-level=3) is in Cargo.toml. Gaps that keep it borderline A: the wasi-sdk version and the wasm3 build (commit, flags) are not stated.
- **Verifier notes:** Every number in claimed_speedup matches RESULTS.md (SHA-256 250.6 vs 216.8, bzip2 30.68 vs 26.86, CoreMark 44,958/45,874/44,378, mandelbrot 1.68x over V8, interpreter 1.16-2.01x over wasm3, 1.07-2.41x over wasmi, 1.07-1.69x over the faster rival, median about 1.39x). Shortcomings: JIT only at parity with Cranelift (9 of 15 rows to Cranelift), interpreter numbers single runs, baseline wasmtime 47.0.2 one major version old, wasm3 build unpinned, CoreMark in non-standard bounded mode, 67 stars. The wasmi-benchmarks plot independently ranks its interpreter first among the interpreter configurations and its JIT just behind Cranelift and V8.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/benchmarks/wasi/RESULTS.md>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/benchmarks/wasi/README.md>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/benchmarks/wasi/Makefile>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/README.md>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/LICENSE-MIT>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/LICENSE-APACHE>
  - <https://github.com/mbbill/Silverfir-nano>
  - <https://github.com/mbbill/Silverfir-nano/commits>
  - <https://github.com/mbbill/Silverfir-nano/tree/HEAD/benchmarks/wasi>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
- **Sources the enricher read:**
  - <https://github.com/mbbill/Silverfir-nano>
  - <https://github.com/mbbill/Silverfir-nano/commits/main>
  - <https://github.com/mbbill/Silverfir-nano/issues?q=is%3Aissue>
  - <https://github.com/mbbill/Silverfir-nano/issues/10>
  - <https://github.com/mbbill/Silverfir-nano/issues/11>
  - <https://github.com/mbbill/Silverfir-nano/tree/main/docs>
  - <https://github.com/mbbill/Silverfir-nano/tree/main/sf-nano-core/interp_gen>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/README.md>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/benchmarks/wasi/README.md>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/benchmarks/wasi/RESULTS.md>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/benchmarks/wasi/Makefile>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/benchmarks/wasi/run_tests.py>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/benchmarks/wasi/run_v8.mjs>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/benchmarks/wasi/common/bench.h>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/benchmarks/wasi/sha256/bench_sha256.c>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/benchmarks/wasi/lua/bench.lua>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/sf-nano-core/README.md>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/sf-nano-core/Cargo.toml>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/sf-nano-core/interp_gen/mod.rs>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/docs/COMPILER_PIPELINE.md>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/docs/ALGORITHM4.md>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/docs/HANDLER_LAYOUT.md>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/docs/decisions.json>
  - <https://raw.githubusercontent.com/mbbill/Silverfir-nano/HEAD/ci/README.md>
  - <https://crates.io/api/v1/crates/sf-nano-core>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/silverfir-nano/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/silverfir-nano/Cargo.toml>
  - <https://github.com/wasmi-labs/wasmi-benchmarks/commits/main>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/commits/main>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/apple-m4-pro/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/apple-m2-pro/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/intel-i7700/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/intel-xeon-platinum-8573c/lin-scale/geomean-execute.svg>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/mbbill/silverfir-nano`) · [data/wave12/enrich/raw/github_com_mbbill_silverfir_nano.json](../../../data/wave12/enrich/raw/github_com_mbbill_silverfir_nano.json) (enrichment confidence 0.8)

</details>
