# DLR-FT wasm-interpreter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> no_std Rust in-place WebAssembly 2.0 interpreter for safety-critical use; starts modules \~150x faster than Wasmtime/Wasmer Cranelift.

| | |
|---|---|
| **Beats** | Wasmtime (Cranelift), Wasmer (Cranelift) startup |
| **Claimed result** | wasmi-benchmarks startup geomean x10.95 (relative to the fastest) against Wasmtime Cranelift x1634.19 and Wasmi v2 lazy-translation x10.66 (recomputed from data/amd-epyc-7763/criterion.json); about 149x over single-threaded Cranelift (derived). Execution geomean x122.00 against WAMR x17.07 (third slowest of 23). |
| **Workload** | wasmi-benchmarks startup suite: compile + instantiate of 7 modules from tiny to huge, geometric mean of per-case ratios against the fastest runtime for each case. |
| **Metric** | startup |
| **Hardware** | AMD EPYC 7763 (plot title and data/amd-epyc-7763 directory). This is the CPU of GitHub's ubuntu-latest runners and the suite's startup.yml workflow runs there, so the data probably come from a shared CI VM (not confirmed). The plots repo also holds Apple M2 Pro, Apple M4 Pro, Intel i7700 and Intel Xeon Platinum 8573C data, not read here. |
| **Compiler and flags** | wasmi-benchmarks (github.com/wasmi-labs/wasmi-benchmarks) Cargo.toml [profile.bench] lto = "fat", codegen-units = 1, run as 'cargo criterion --bench criterion --all-features ... startup/' (criterion 0.8.2; sample_size 10, 2 s measurement, 1 s warm-up). Rust toolchain: .github/workflows/startup.yml uses dtolnay/rust-toolchain@stable with no rust-toolchain file, so the rustc version is not recorded; the C/C++ runtimes are built with gcc-15/g++-15 (.github/actions/install-dependencies). Runtime versions are pinned only by the Cargo.lock at HEAD (wasmtime 47.0.3, wasmer 7.2.1); the plots repo does not record which suite commit produced them. |
| **Adoption** | 83 stars |
| **Last commit** | 2026-09-07 |
| **Links** | [repository](https://github.com/DLR-FT/wasm-interpreter) · [benchmark](https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg) |

## Verdict

The independent wasmi-benchmarks suite (criterion, Rust bench profile with fat LTO, crate 0.2.0, AMD EPYC 7763, probably a GitHub Actions VM) times decode + validate + instantiate of 7 modules from erc20 to ffmpeg. DLR's geomean is x10.95 against the per-case fastest runtime, versus x1634.19 for Wasmtime 47 Cranelift and x1484.15 for Wasmer 7.2 Cranelift. I recomputed these from the committed criterion.json. It is a startup-only win over optimizing JITs; Wasmtime was built without parallel compilation.

## Use it when

- You need to load many short-lived or rarely called modules and startup latency dominates. On the wasmi-benchmarks startup suite it instantiates CoreMark in about 63 us and ffmpeg in about 127 ms, where Wasmtime Cranelift takes 9.9 ms and 18 s.
- Bare-metal or no_std targets that have an allocator: it needs only core, alloc and libm, and the authors aim it at avionics and automotive certification (DO-178C design paper, DASC 2025).
- Embedders that want control to come back on every host call, or that need fuel-limited, resumable execution, for example to time-slice Wasm in a partitioned RTOS.
- Rust projects that want a small interpreter that passes the official spec suite and is dual-licensed MIT or Apache-2.0.

## Skip it when

- Compute-heavy code that runs for a long time. Its execution geomean is x122.00 against the per-case fastest runtime, third-slowest of 23 runtimes and about 7x slower than WAMR fast-interpreter (x17.07) or Wasm3 (x16.51).
- When startup is all you care about, lazy interpreters win: Wasmi v2 (lazy) scores x1.37 and Wasm3 (lazy) x2.77 against its x10.95, and V8 starts the two largest modules faster (ffmpeg 35.5 ms vs 127.1 ms).
- Modules that use tail calls: the benchmark suite skips fibonacci-tail for this runtime. GC is not planned, threads atomics are unimplemented and the C bindings are only planned.
- Small embedded RAM budgets on 0.2.0: each invocation preallocates a 65,536-value stack, which is a 1.5 MB allocation, and issue #413 reports this panicking on an nRF52840.
- Projects that need a mature ecosystem: 83 stars, release 0.2.0, and the utility crates (checked, linker, interop, registry) are lightly documented according to the README.

## How it is fast

It uses in-place interpretation after Ben L. Titzer's 'A fast in-place interpreter for WebAssembly'. Validation builds a small side table (target pc, side-table pointer, values to copy, values to pop) for each br, br_if, br_table and else, and the interpreter then dispatches on the original bytes. Startup is just decoding, one validation pass and instantiation. Nothing is compiled or lowered to an internal representation, which is why it beats optimizing JITs by two orders of magnitude on startup. Execution pays for this: LEB128 immediates are decoded on every instruction, and dispatch is a function-call loop by default, with tail-call dispatch available only on nightly.

## Compared with alternatives

Pick it over SpaceWasm (startup x25.84, execute x79.53), Fizzy (x17.83) or toywasm (x18.35) when you want a Rust no_std crate with a certification-oriented design and faster startup. Only Wasmi v2 lazy-translation (x10.66) and the lazy modes of Wasmi and Wasm3 start faster in this suite. Pick Wasmi or Wasm3 if you also need several times faster execution.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | libm (log optional, off by default); the safe wrapper and linker live in the separate dlr-wasm-interpreter-checked and -linker crates |
| **Minimum toolchain** | Rust 1.87.0 (rust-version), edition 2021; the tail-call dispatch mechanism needs the nightly feature |
| **Platforms** | any target with core + alloc (no_std); shared linear memory uses a spin RwLock that needs 32-bit atomics |
| **Thread safety** | Not documented for Store. Shared linear memories (threads proposal) are guarded by a busy-wait RwSpinLock so they can be shared across stores; the atomic instructions are not implemented. |
| **Drop-in for the baseline** | no |

## Gotchas

- The Store borrows the module bytecode for its whole life, because it interprets in place. The wasmi-benchmarks adaptor has to fabricate a 'static slice with unsafe code to hold both together.
- The core API is unsafe at HEAD: module_instantiate, instance_export and invoke require addresses from the same store. Use dlr-wasm-interpreter-checked for safe wrappers, as the benchmark adaptor does.
- Default stack limits change between versions. 0.2.0 preallocates 64Ki values and 4Ki frames on every invocation (1.5 MB, issue #413). Unreleased HEAD (commit of 2026-09-07) cuts the defaults to 208 values and 208 frames, the minimum the spec suite needs. Real programs then need a custom Config, or they fail with StackExhaustion.
- Harness note on the baseline: wasmi-benchmarks builds Wasmtime with default-features = false and no parallel-compilation feature (its Cargo.lock has no rayon under wasmtime 47.0.3), so Cranelift compiles each module single-threaded. The suite also never uses Wasmtime's precompile/deserialize path. That inflates the 149x ratio by up to the runner's core count, though DLR would still win by a wide margin. Wasmer's Cranelift crate does pull rayon.

## Known shortcomings

- Downgraded A to B: startup-only win over optimizing JITs in the wasmi-benchmarks suite (about 149x against Wasmtime Cranelift, derived from page data) with execution at x122 against WAMR's x17.07; V8 is faster on ffmpeg and spidermonkey. rustc version never recorded (dtolnay/rust-toolchain@stable), no suite commit named, data probably from a shared GitHub Actions VM. Rust, not C++.
- Enricher (via tinywasm): wasmi-benchmarks builds wasmtime 47.0.0 with default-features=false, so the Cranelift startup column compiles single-threaded and the about 149x startup gap is overstated against a default multi-core Wasmtime.
- Enricher: startup geomeans recomputed from criterion.json (x10.95 vs Wasmtime Cranelift x1634.19); wasmi-benchmarks builds wasmtime 47.0.3 with default-features=false and no parallel compilation (no rayon under wasmtime in Cargo.lock), inflating the ratio by up to the runner's core count. Execute geomean x122.00 (third slowest of 23); 0.2.0 preallocates a 1.5 MB stack on every invoke (issue #413 panics on nRF52840), unreleased HEAD cuts default stacks to 208 values and 208 frames; soundness issues #406 and #412 open.

## Caveats and trade-offs

The suite is maintained and run by the Wasmi author, so it is third-party for every runtime except Wasmi. Ratios were read from the SVG text labels and checked against the raw criterion data, which reproduce the startup geomeans exactly. The measured crate is dlr-wasm-interpreter 0.2.0 (current crates.io release). Startup is decode + validate + instantiate of 7 modules (erc20 to ffmpeg); the win is an in-place interpreter versus optimizing JITs, which is expected. Against other interpreters it is not the fastest: Wasmi v2 lazy-translation (also validates eagerly) is x10.66, Wasmi v2 lazy x1.37 and Wasm3 lazy x2.77, and V8 starts faster on the two largest modules (ffmpeg 35.5 ms vs 127.1 ms, spidermonkey 10.9 ms vs 32.9 ms). Startup-only win: execution geomean on the same CPU (plot geomean-execute.svg) is x122.00, about 7 times slower than WAMR fast-interpreter x17.07 (derived from page data), over 20 of 21 cases (no tail calls); the committed criterion.json gives a different execute geomean (98.25), so the execute plot came from another run. Data probably from a shared GitHub Actions VM. The project's own README gives no performance numbers. [retier] Startup-only win over optimizing JITs in the wasmi-benchmarks suite; the suite builds wasmtime 47.0.3 with default-features=false and no parallel compilation, so the Cranelift startup column is single-threaded and the gap is overstated against a default multi-core Wasmtime. V8 is faster on ffmpeg and spidermonkey. 0.2.0 preallocates a 1.5 MB stack on every invoke (issue #413 panics on nRF52840); unreleased HEAD cuts default stacks to 208 values and 208 frames; soundness issues #406 and #412 open. rustc version unrecorded, no suite commit named. Rust, not C++.

In-place interpretation of WebAssembly 2.0 with no intermediate representation, no_std, aimed at avionics; no GC proposal planned.

## Maintenance

Actively developed by DLR (last commit 2026-09-07, 0.3.0 unreleased, 59 open issues including soundness items #406 and #412); MIT/Apache-2.0 and dependency-light, so it is easy to vendor, but its API is still changing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now B.
- **Tier reason:** Independent third-party suite (wasmi-labs/wasmi-benchmarks: benches/criterion/startup.rs times rt.instantiate = decode, validate, instantiate; runtimes/dlr-wasm-interpreter/lib.rs) with public code, bench-profile flags, a named CPU and raw criterion data that reproduce the plotted startup geomeans exactly. Not A: no rustc version is recorded (CI uses dtolnay/rust-toolchain@stable) and the plots do not name the suite commit, matching how batch-32 tiered tinywasm from the same plot.
- **Verifier notes:** Every number in the record is on the plot and in the raw data. Downgraded A to B only for the unrecorded rustc version and suite commit. Shortcomings to record: startup-only win against optimizing JITs; at parity with Wasmi v2 lazy-translation and slower than lazy Wasmi/Wasm3 and than V8 on ffmpeg and spidermonkey; execution about 7x slower than WAMR; no tail-call support; 83 stars. Metadata checked: Apache-2.0 OR MIT, 83 stars, not a fork, last commit 2026-09-07.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/README.md>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/commits>
  - <https://github.com/wasmi-labs/wasmi-benchmarks>
  - <https://github.com/wasmi-labs/wasmi-benchmarks/commits>
  - <https://github.com/wasmi-labs/wasmi-benchmarks/tree/main/data>
  - <https://github.com/wasmi-labs/wasmi-benchmarks/tree/main/data/amd-epyc-7763>
  - <https://github.com/wasmi-labs/wasmi-benchmarks/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/.github/workflows/startup.yml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/.github/actions/install-dependencies/action.yml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/main.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/startup.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmer/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/data/amd-epyc-7763/criterion.json>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/dlr-wasm-interpreter/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/dlr-wasm-interpreter/Cargo.toml>
  - <https://github.com/DLR-FT/wasm-interpreter>
  - <https://github.com/DLR-FT/wasm-interpreter/commits>
  - <https://crates.io/api/v1/crates/dlr-wasm-interpreter>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/HEAD/README.md>
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/HEAD/Cargo.toml>
  - <https://github.com/DLR-FT/wasm-interpreter>
  - <https://github.com/DLR-FT/wasm-interpreter/tree/main/src>
  - <https://github.com/DLR-FT/wasm-interpreter/tree/main/src/execution>
  - <https://github.com/DLR-FT/wasm-interpreter/tree/main/src/core>
  - <https://github.com/DLR-FT/wasm-interpreter/tree/main/crates>
  - <https://github.com/DLR-FT/wasm-interpreter/tree/main/crates/benchmark>
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/HEAD/src/core/sidetable.rs>
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/HEAD/src/execution/mod.rs>
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/HEAD/src/core/rw_spinlock.rs>
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/HEAD/src/execution/config.rs>
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/HEAD/src/execution/instructions/mod.rs>
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/HEAD/src/execution/instructions/dispatch/mod.rs>
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/HEAD/src/execution/runtime_structure/value_stack.rs>
  - <https://github.com/DLR-FT/wasm-interpreter/tags>
  - <https://github.com/DLR-FT/wasm-interpreter/commits/main>
  - <https://github.com/DLR-FT/wasm-interpreter/tree/v0.2.0/src/execution>
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/v0.2.0/src/execution/config.rs>
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/v0.2.0/src/execution/runtime_structure/value_stack.rs>
  - <https://raw.githubusercontent.com/DLR-FT/wasm-interpreter/v0.2.0/src/execution/instructions/mod.rs>
  - <https://github.com/DLR-FT/wasm-interpreter/issues>
  - <https://github.com/DLR-FT/wasm-interpreter/issues?q=is%3Aissue+is%3Aopen+performance+OR+bug+OR+slow>
  - <https://github.com/DLR-FT/wasm-interpreter/issues/412>
  - <https://github.com/DLR-FT/wasm-interpreter/issues/413>
  - <https://github.com/DLR-FT/wasm-interpreter/issues/406>
  - <https://crates.io/api/v1/crates/dlr-wasm-interpreter>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/dlr-wasm-interpreter/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/dlr-wasm-interpreter/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/startup.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/execute.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmer/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmer/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/data/amd-epyc-7763/criterion.json>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
  - https://elib.dlr.de/219593/ (EGRESS_BLOCKED)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/dlr-ft/wasm-interpreter`) · [data/wave12/enrich/raw/github_com_dlr_ft_wasm_interpreter.json](../../../data/wave12/enrich/raw/github_com_dlr_ft_wasm_interpreter.json) (enrichment confidence 0.75)

</details>
