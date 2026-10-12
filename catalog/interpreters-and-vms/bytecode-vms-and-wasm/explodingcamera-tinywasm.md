# tinywasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Small safe-Rust, no_std WebAssembly 3.0 interpreter whose eager compile+instantiate beats every JIT runtime's startup, not WAMR's execution.

| | |
|---|---|
| **Beats** | Wasmtime (Cranelift, Winch, Pulley), Wasmer (Cranelift, Singlepass) and WAMR fast-interpreter startup |
| **Claimed result** | Startup geomean on AMD EPYC 7763 relative to the per-case fastest runtime (lower is better): Tinywasm x37.19 versus Wasmtime (Pulley) x1777.72, Wasmtime (Cranelift) x1634.19, Wasmer (Cranelift) x1484.15, Wasmtime (Winch) x298.15, Wasmer (Singlepass) x162.12 and WAMR fast-interpreter x56.73; V8 is x33.27 and Wasmi v2 (lazy) x1.37. About 44x lower than Wasmtime Cranelift and 1.5x lower than WAMR (derived from page data). |
| **Workload** | wasmi-benchmarks startup suite: compile + instantiate of 7 modules from tiny to huge, geometric mean of per-case ratios against the fastest runtime for each case. |
| **Metric** | startup |
| **Hardware** | AMD EPYC 7763 (named in the plot title; the plots repo also holds data for Apple M2 Pro, Apple M4 Pro, an Intel i7700 and Intel Xeon Platinum 8573C, not read here) |
| **Compiler and flags** | wasmi-benchmarks Cargo.toml [profile.bench]: lto = "fat", codegen-units = 1 (cargo criterion --bench criterion uses it; a separate [profile.ci] with thin LTO is not used by the workflows). Rust toolchain unpinned: no rust-toolchain file, CI workflows (.github/workflows/startup.yml, execute.yml) install dtolnay/rust-toolchain@stable; C/C++ runtimes are built by their wrapper crates with the system compiler, version unstated. Tinywasm 0.10.0 is built with default features, without the nightly-tail-calls feature its README recommends for maximum performance. |
| **Adoption** | 594 stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/explodingcamera/tinywasm) · [benchmark](https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg) |

## Verdict

In the Wasmi author's wasmi-benchmarks startup suite (criterion, compile plus instantiate of seven modules from erc20 to ffmpeg, single-threaded compilation, Rust bench profile with fat LTO and codegen-units 1, stable toolchain of unrecorded version) on an AMD EPYC 7763, Tinywasm 0.10.0 has a geomean of x37.19 relative to the per-case fastest runtime versus x56.73 for WAMR fast-interpreter, x298.15 for Wasmtime Winch, x1484.15 for Wasmer Cranelift and x1634.19 for Wasmtime Cranelift, roughly level with Wasmi v2 eager (x38.88) and V8 (x33.27). Per case it ranges from 212 us (erc20) to 409.56 ms (ffmpeg) versus 10.00 ms and 17.96 s for Wasmtime Cranelift.

## Use it when

- You need to load and run many small or short-lived Wasm modules where JIT compile time dominates: on the EPYC 7763 run it compiles+instantiates coremark in 223 us and erc20 in 212 us versus 9.87 ms and 10.00 ms for Wasmtime (Cranelift).
- no_std + alloc targets, Rust code bases that forbid unsafe, or hosts where generating machine code at run time is not wanted (it is a pure interpreter and can itself compile to WebAssembly); with only the archive feature, binaries below 300 KB are claimed.
- You need recent proposals in an interpreter (GC, exception handling, typed function references, memory64, relaxed SIMD) that some older small interpreters lack.
- Precompiling modules ahead of time to .twasm from a trusted build step so devices skip parsing and validation on load.

## Skip it when

- Execution-heavy workloads: execution geomean on the same EPYC 7763 run is x40.50 versus WAMR fast-interpreter x17.07, Wasm3 (eager) x16.51, Wasmtime Pulley x27.92 and Wasmtime Cranelift x1.15; it is several times slower than the runtimes it beats on startup once code runs for more than a few milliseconds.
- When startup latency is the only goal: lazy interpreters start much faster (Wasmi v2 lazy x1.37, Wasm3 lazy x2.77 versus Tinywasm x37.19), and V8 (x33.27) and most in-place interpreters in the same suite (DLR x10.95, Fizzy x17.83, Toywasm x18.35, SpaceWasm x25.84) also start faster.
- C or C++ hosts: there is no C API yet (the changelog only mentions internal methods for a future c-api crate), unlike WAMR or Wasm3.
- Untrusted .twasm archives: loading checks only the header and encoding, not Wasm validation or runtime invariants; untrusted inputs must go through the validating parser plus ParseLimits, stack, ResourceLimiter and fuel or time limits.
- Projects needing WebAssembly threads or stack switching today (threads only on the unreleased next branch), or a stable API: 0.10 and 0.11 both broke the embedding API and the .twasm format.

## How it is fast

The startup win is simply that it is an eager translating interpreter: it runs one validation-plus-lowering pass (single-pass since 0.11.0) into a compact internal instruction set instead of generating machine code with Cranelift, Winch or Singlepass. The bytecode uses 8-byte instructions (16 bytes before 0.11.0), separate 32/64/128-bit operand lanes and fused superinstructions (LocalCopy32/64/128, IncLocal, BinOpLocalLocal, local compare-and-branch) produced by an optimize rewrite at parse time. Dispatch is a stable-Rust match loop over the instruction enum, or, with the nightly-tail-calls feature, a handler table with explicit tail calls (become), i.e. threaded-code dispatch.

## Compared with alternatives

Pick Tinywasm over Toywasm, Fizzy, SpaceWasm, DLR wasm-interpreter or Submilli-wasm when execution speed also matters (x40.50 versus x45.63 to x318.96 on the same run) and you want safe, no_std Rust with Wasm 3.0 GC and exceptions; pick Wasmi instead when you want both faster startup (lazy modes) and faster execution (x12.40) in Rust, and WAMR, Wasm3 or Silverfir-nano when execution speed or a C API matters most.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | wasmparser (parser/validation) and postcard/serde (.twasm archives) with default features; libm only with default features disabled (no_std + alloc); optional log, portable-atomic |
| **Minimum toolchain** | Rust 1.98 (edition 2024) for 0.11.0; Rust 1.95 for 0.10.0; nightly Rust for the nightly-tail-calls feature |
| **Platforms** | any target Rust supports, including no_std and wasm32; optional simd-x86 feature for x86 SIMD intrinsics (x86-64-v3 recommended); earlier issues fixed for aarch64 build and arm32v7 panics |
| **Thread safety** | Stores and store-local handles are single-threaded unless the send feature is enabled; host function definitions are Send + Sync and reusable across stores (0.11.0); shared memory and atomic wait/notify across stores only on the unreleased next branch |
| **Drop-in for the baseline** | no |

## Gotchas

- The suite measured tinywasm 0.10.0 with default features (stable match-loop dispatch), not 0.11.0 with its single-pass parser, 8-byte instructions or the nightly-tail-calls backend the README recommends for maximum performance; current-release numbers may differ in either direction.
- Harness detail (wasmi-benchmarks): every runtime is timed single-threaded at compile time. The Tinywasm wrapper sets parser threads to 1, and the Wasmtime wrapper builds wasmtime 47.0.0 with default-features = false, which drops Wasmtime's default parallel-compilation (rayon) feature; so the 44x gap to Wasmtime (Cranelift) is against single-threaded Cranelift and would shrink on a multi-core host with default Wasmtime. The Tinywasm wrapper also rebuilds its Store and host functions inside every timed instantiation, a small bias against Tinywasm.
- Wasmtime (Pulley) is the slowest startup in the plot (x1777.72) because Pulley bytecode is produced by Cranelift; it is not a fair stand-in for a lightweight interpreter's startup.
- Execution correctness history: wasmi-benchmarks' author reported Tinywasm trapping with unreachable on the compression benchmark (#47) and hanging on regex_redux (#48, closed as duplicate); 0.10.0 fixed branch stack shaping that could corrupt execution or panic, and 0.11.0 fixed memory64 bulk-memory lanes and memory.init bounds checks.

## Known shortcomings

- Downgraded A to B: startup-only win in the independent wasmi-benchmarks suite; slower than V8 on startup and slower than WAMR, Pulley and wasm3 on execution; measured version 0.10.0 without nightly tail calls, rustc version unrecorded. Rust, not C++.
- Enricher: wasmi-benchmarks builds wasmtime 47.0.0 with default-features=false, so Wasmtime has no parallel compilation and the Cranelift startup column is single-threaded; the 44x startup gap is overstated against a default multi-core Wasmtime. The tinywasm wrapper rebuilds the Store and host functions inside each timed instantiate (small bias against it). Startup only: slower start than V8 and most in-place interpreter siblings (DLR, Fizzy, toywasm, SpaceWasm), execution x40.50 vs WAMR x17.07, no C API.

## Caveats and trade-offs

The suite is maintained and run by the Wasmi author (Robbepop), so it is third-party for Tinywasm but run by a competitor. Ratios were read from the text labels of the rendered SVG; the plots repo records no runtime versions, toolchain or run date beyond its commit 'update AMD EPYC 7763 plots' (2026-08-25). The EPYC 7763 is the CPU of GitHub's ubuntu-latest runners, so the run probably came from the workflow_dispatch CI jobs on a shared VM, but the plots repo does not say so. The suite pins tinywasm 0.10.0 with default features (no nightly-tail-calls); tinywasm 0.11.0 shipped 2026-09-19. Startup-only win, as expected of an interpreter against compiling JITs, and no better than V8 (x33.27). Execution geomean on the same CPU (https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg) is x40.50, slower than Wasmtime (Pulley) x27.92, WAMR x17.07, Wasm3 (eager) x16.51 and Wasmi v2 (eager) x12.40. The README itself points users wanting better performance to wasmi, wasm3, wazero, wasmer or wasmtime. In the independent Apple Silicon report (https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md, tinywasm 0.11.0 with nightly-tail-calls) tinywasm execution geomean is 3.20 vs Pulley 2.09 and WAMR 1.63 on M4 E-cores (2.98 vs 1.68 and 1.38 on A12), and it fails the legacy-exceptions modules. Last commit on the default branch main is 2026-09-22; the next branch was updated 2026-10-03. [retier] Startup-only win in the independent wasmi-benchmarks suite; the suite builds wasmtime 47.0.0 with default-features=false, so Cranelift compiles single-threaded and the 44x startup gap is overstated against a default multi-core Wasmtime; the tinywasm wrapper rebuilds the Store and host functions inside each timed instantiate. Slower start than V8 and the in-place interpreters DLR, Fizzy, toywasm and SpaceWasm; execution x40.50 vs WAMR x17.07. Measured 0.10.0 without nightly tail calls, rustc version unrecorded, no C API. Rust, not C++.

Safe Rust (except an optional simd-x86 feature), no_std, passes the WebAssembly 3.0 core test suite; can serialize to .twasm for faster loading.

## Maintenance

Actively developed by one main maintainer (0.11.0 on crates.io 2026-09-19, about 25k downloads, main branch last commit 2026-09-22, next branch newer), dual MIT/Apache-2.0 and easy to add as a crate, but pre-1.0 with breaking API and .twasm changes in each minor release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now B.
- **Tier reason:** The independent wasmi-benchmarks suite (benches/criterion startup group, runtimes/tinywasm/lib.rs, runtimes/wasmtime/lib.rs, plots in wasmi-labs/wasmi-benchmarks-plots data/amd-epyc-7763) compares Tinywasm with Wasmtime, Wasmer, WAMR and V8 on a named AMD EPYC 7763, and the plot's labels match every number in the record. Not A: no rustc or C compiler version is recorded anywhere (the CI workflows use dtolnay/rust-toolchain@stable, no rust-toolchain file), and the plots do not record which runtime versions or suite commit produced them; it is third-party for Tinywasm (run by the Wasmi author), hence B.
- **Verifier notes:** All six numbers in the record match the SVG labels (matched by y position: Tinywasm x37.19, Wasmtime Cranelift x1634.19, Wasmer Cranelift x1484.15, Winch x298.15, Singlepass x162.12, V8 x33.27); I added the Pulley and WAMR startup rows, since WAMR is a category baseline. Downgraded A to B: independent suite, but rustc and C compiler versions and the measured runtime versions are unrecorded (zenjpeg and cataggar/wamr precedents for unpinned toolchains). Shortcomings to record: startup-only win, slower than V8 on startup, slower than WAMR, Pulley and Wasm3 on execution, measured without its recommended nightly-tail-calls build, older 0.10.0 measured, Rust not C++. Metadata checked: Apache-2.0 OR MIT, 594 stars, not a fork, last main commit 2026-09-22 (corrected from the next branch's 2026-10-03).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/README.md>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/commits/main>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/tree/main/data>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://github.com/wasmi-labs/wasmi-benchmarks/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/.github/workflows/startup.yml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/.github/workflows/main.yml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/tinywasm/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/tinywasm/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/lib.rs>
  - <https://github.com/explodingcamera/tinywasm>
  - <https://github.com/explodingcamera/tinywasm/commits/main>
  - <https://github.com/explodingcamera/tinywasm/branches>
  - <https://raw.githubusercontent.com/explodingcamera/tinywasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/explodingcamera/tinywasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/explodingcamera/tinywasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/explodingcamera/tinywasm/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/explodingcamera/tinywasm/HEAD/crates/tinywasm/Cargo.toml>
  - <https://raw.githubusercontent.com/explodingcamera/tinywasm/HEAD/crates/tinywasm/src/lib.rs>
  - <https://raw.githubusercontent.com/explodingcamera/tinywasm/HEAD/crates/tinywasm/src/interpreter/mod.rs>
  - <https://raw.githubusercontent.com/explodingcamera/tinywasm/HEAD/crates/tinywasm/src/interpreter/executor/dispatch.rs>
  - <https://raw.githubusercontent.com/explodingcamera/tinywasm/HEAD/crates/tinywasm/src/interpreter/executor/dispatch_become.rs>
  - <https://raw.githubusercontent.com/explodingcamera/tinywasm/HEAD/crates/tinywasm/src/interpreter/executor/mod.rs>
  - <https://raw.githubusercontent.com/explodingcamera/tinywasm/HEAD/crates/types/src/instructions.rs>
  - <https://github.com/explodingcamera/tinywasm/tree/main/crates/tinywasm/src>
  - <https://github.com/explodingcamera/tinywasm/tree/main/crates/tinywasm/src/interpreter>
  - <https://github.com/explodingcamera/tinywasm/tree/main/crates/tinywasm/src/interpreter/executor>
  - <https://github.com/explodingcamera/tinywasm/issues?q=is%3Aissue>
  - <https://github.com/explodingcamera/tinywasm/issues/48>
  - <https://crates.io/api/v1/crates/tinywasm>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://github.com/wasmi-labs/wasmi-benchmarks/tree/main/benches>
  - <https://github.com/wasmi-labs/wasmi-benchmarks/tree/main/benches/criterion>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/startup.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/tinywasm/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/tinywasm/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wamr/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wamr/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/Cargo.toml>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wasmtime/Cargo.toml>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/tree/main/data/amd-epyc-7763/lin-scale>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/ffmpeg.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/spidermonkey.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/erc20.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/argon2.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/coremark.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/bz2.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/pulldown-cmark.svg>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/explodingcamera/tinywasm`) · [data/wave12/enrich/raw/github_com_explodingcamera_tinywasm.json](../../../data/wave12/enrich/raw/github_com_explodingcamera_tinywasm.json) (enrichment confidence 0.8)

</details>
