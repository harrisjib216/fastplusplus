# Wasmi

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust WebAssembly interpreter with near-zero startup through lazy translation; its v2 engine also out-executes WAMR, Wasm3 and Pulley interpreters.

| | |
|---|---|
| **Beats** | Wasmtime (Cranelift), Wasmer (Cranelift) and V8 for startup; WAMR fast interpreter and Wasmtime Pulley for execution |
| **Claimed result** | Startup geomean on AMD EPYC 7763, relative to the per-case fastest runtime (lower is better): Wasmi v2 (lazy) x1.37 and Wasmi v1 (lazy) x1.56, versus Wasmtime (Pulley) x1777.72, Wasmtime (Cranelift) x1634.19, Wasmer (Cranelift) x1484.15, Wasmtime (Winch) x298.15, Wasmer (Singlepass) x162.12, WAMR fast-interpreter x56.73 and V8 x33.27; about 1,190x lower than Wasmtime Cranelift (derived from page data). Wasmi v2 with lazy translation but eager validation is x10.66 and eager Wasmi v2 is x38.88. Execution geomean on the same CPU: Wasmi v2 (eager) x12.40 versus WAMR fast-interpreter x17.07 (about 1.38x faster, derived from page data) and Wasmtime (Pulley) x27.92. |
| **Workload** | wasmi-benchmarks startup suite: compile + instantiate of 7 modules from tiny (erc20) to huge (ffmpeg, spidermonkey), geometric mean of per-case ratios against the fastest runtime for each case. |
| **Metric** | startup |
| **Hardware** | AMD EPYC 7763 (named in the plot title; the plots repo also holds data for Apple M2 Pro, Apple M4 Pro, an Intel i7700 and Intel Xeon Platinum 8573C, not read here) |
| **Compiler and flags** | wasmi-benchmarks Cargo.toml [profile.bench]: lto = "fat", codegen-units = 1 (cargo criterion --bench criterion uses it; a separate [profile.ci] with thin LTO is not used by the workflows). Rust toolchain unpinned: no rust-toolchain file, CI workflows (.github/workflows/startup.yml, execute.yml) install dtolnay/rust-toolchain@stable; C/C++ runtimes are built by their wrapper crates with the system compiler, version unstated. At HEAD the suite pins wasmi 2.0.0-beta.10 (features auto-dispatch, validate), wasmtime 47.0.0, wasmer 7.2.0, v8 crate 150.1.0 and wamrx 0.3; versions used for the plotted run are not recorded. |
| **Adoption** | 2.3k stars |
| **Last commit** | 2026-09-01 |
| **Links** | [repository](https://github.com/wasmi-labs/wasmi) · [benchmark](https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg) |

## Verdict

In the author's own wasmi-benchmarks suite (criterion, 10 samples, 2 s measurement, fat-LTO bench profile, unpinned stable Rust) plotted for an AMD EPYC 7763, the startup geomean (Module::new plus instantiate of 7 modules, relative to the fastest runtime per case) was x1.37 for lazy Wasmi v2, x10.66 lazy-translation, x38.88 eager, against x33.27 V8, x298.15 Wasmtime Winch and x1634.19 Wasmtime Cranelift; the execution geomean over 21 cases (instance set up outside the timed loop, several cases assert their outputs) was x12.40 for eager Wasmi v2 against x17.07 WAMR fast-interp, x16.51 Wasm3, x27.92 Pulley and x1.15 Cranelift. I re-read these labels from the SVGs and also read the M4 Pro and Xeon 8573C plots, where Wasmi v2 keeps its interpreter ranking (x8.06 and x8.36).

## Use it when

- Hosts that instantiate many short-lived or large modules and call only a few functions (plugins, smart contracts, per-request sandboxes): lazy Wasmi v2 instantiated the 7-module startup suite at x1.37 of the per-case optimum on EPYC 7763, against x33.27 for V8 and x1634.19 for Wasmtime Cranelift.
- Platforms where native code generation is forbidden or unavailable (iOS, W^X, embedded, no_std) and you still want a fast interpreter: v2 eager executed at x12.40 on EPYC 7763, x8.06 on Apple M4 Pro and x8.36 on Xeon Platinum 8573C, ahead of WAMR fast-interp (x17.07/x18.64/x12.43), Wasm3 eager (x16.51/x10.71/x11.95) and Wasmtime Pulley (x27.92/x23.97/x23.70).
- Rust hosts that need deterministic execution or fuel metering (blockchains such as Soroban and smoldot): fuel is tied to the input Wasm bytecode and costs are configurable in v2.
- Projects that want a Wasmtime-shaped API without Cranelift's binary size and compile latency, or a C/C++ host that can link a Rust-built static library through the Wasm C-API.

## Skip it when

- Compute-bound long-running guests: Wasmtime Cranelift (x1.15) and V8 (x1.05) executed about 10x faster than Wasmi v2 (x12.40) on EPYC 7763, and even Wasmer Singlepass (x2.95) and Wasmtime Winch (x2.35) were about 4-5x faster.
- When the fastest interpreter matters most: Silverfir-nano's interpreter was ahead on every measured CPU (x9.02 vs x12.40 on EPYC 7763, x5.97 vs x8.06 on M4 Pro, x7.01 vs x8.36 on Xeon 8573C).
- Guests that need Wasm GC, typed function references, threads or exception handling (all only tracked, not implemented), or WASI preview 2/components.
- Untrusted modules in fully Lazy mode where results must match other engines: the API docs say Lazy 'must not be used if the result of Wasm execution must be deterministic amongst multiple Wasm implementations', since invalid function bodies are only rejected when first called.
- Debug builds: the usage guide says an unoptimized Wasmi can be 100x slower, and because the executor is generic over Store&lt;T&gt; it is compiled in your crate, so your own profile needs lto = "fat" and codegen-units = 1.

## How it is fast

Startup: with CompilationMode::LazyTranslation (default) or Lazy, Module::new only parses and validates (or, in Lazy mode, does not even validate) function bodies, and each function is translated to Wasmi bytecode on first call, so instantiating a huge module that runs few functions costs almost nothing; translation is linear-time ('JIT bomb resisting'). Execution: Wasmi v2 has a new IR whose operators write results into accumulator registers (the design used by Wasm3 and Stitch), fixed 64-bit cells, operator fusion (compare+branch and similar), tail-call-based operator dispatch where LLVM guarantees tail calls (auto-dispatch, falling back to a loop), a lock-free append-only code map and cached instance data; the changelog reports v2 about 2.2x faster than v1 geomean.

## Compared with alternatives

Pick Wasmi over WAMR, Wasm3 or Stitch when you want the fastest instantiation plus a top-tier interpreter in safe-to-embed Rust with fuel metering and a Wasmtime-like API (it beat all three on execution geomean on EPYC 7763, M4 Pro and Xeon 8573C); pick Silverfir-nano's interpreter instead only if raw interpreter throughput matters more than startup and maturity, and WAMR when you need a C code base with optional AOT/JIT tiers.

## Integration

| | |
|---|---|
| **Form** | crate (wasmi); C-API static/shared library via CMake (crates/c_api); CLI (wasmi) |
| **Dependencies** | pure Rust: wasmparser, spin, internal wasmi_\* crates; optional wat; the C-API build needs CMake and a Rust toolchain |
| **Minimum toolchain** | Rust 1.86 (workspace rust-version), edition 2024 |
| **Platforms** | any Rust target including no_std; tail-call dispatch only on targets with guaranteed LLVM tail calls in optimized builds, portable loop dispatch elsewhere |
| **Thread safety** | Engine is cloneable and shared; Store is Send and Sync (changelog, PR #566); one Store executes on one thread at a time; the Wasm threads proposal is not supported. |
| **Drop-in for the baseline** | partial — the API loosely mirrors Wasmtime's (Engine/Store/Linker/Module), but it is a different crate with a narrower feature set (no components, GC, threads or exception handling) |

## Gotchas

- The startup headline compares deferred work with eager work: the harness times only Module::new plus instantiate and never calls into the module, so in lazy modes no function body is translated (and in Lazy mode none is validated) inside the timed region, while Cranelift, Winch and V8 compile everything. The per-case 'optimal runtime' is mostly Wasmi v2 (lazy, unchecked) itself (x1.04), which uses the unsafe Module::new_unchecked. Fairer numbers on EPYC 7763: default lazy-translation x10.66 and eager x38.88, the latter slower than V8 (x33.27) there and on M4 Pro (x25.69 vs x21.11) but faster on Xeon 8573C (x22.62 vs x29.21).
- Benchmark builds are not the defaults: the suite builds Wasmi v2 with default-features = false and only auto-dispatch and validate (no std and no memory64, which the changelog says 'may improve execution performance'), and Wasmtime with default-features = false (runtime, anyhow, plus the chosen backend), so Cranelift compiles without its default parallel-compilation feature, single-threaded; a stock Wasmtime would start faster on a multi-core host. The plots record no Wasmi beta, baseline versions or rustc version (the README links v2.0.0-beta.7, Cargo.toml pins 2.0.0-beta.10).
- The v2 engine is young: the 2.0 betas fixed several translation bugs (multi-value br_table, fused fabs+fneg, SIMD load accumulator handling, isub immediate lowering, a memory-invalidation bug when tail-calling host functions), and the extra-checks feature, which guards against undefined behaviour if translation invariants break, is off by default (up to 20% cost when on).
- Security history: a critical out-of-bounds write for host-to-Wasm calls with more than 128 parameters (GHSA-75jp-vq8x-h4cq, 2024-03) and a high-severity linear-memory use-after-free (GHSA-g4v2-cjqp-rfmq, 2025-12); the README lists two audits (SRLabs for 0.31.0, Runtime Verification for 0.36-0.38), none of the v2 engine.

## Known shortcomings

- Downgraded A to C: the wasmi-benchmarks suite is run by the Wasmi author, the x1.37 startup headline relies on lazy validation (lazy-translation is x10.66 and eager x38.88 slower than V8), the plotted v2 is a pre-release beta, and rustc and runtime versions are unrecorded. Execution win over WAMR x17.07 and Pulley x27.92 added (v2 eager x12.40). Rust, not C++.
- Enricher (via tinywasm): wasmi-benchmarks builds wasmtime 47.0.0 with default-features=false, so the Cranelift startup column compiles single-threaded and every startup gap against Wasmtime in that suite is overstated against a default multi-core build.
- Enricher: the wasmi-benchmarks startup harness times only Module::new plus instantiate and never calls the guest, so lazy modes defer all translation and the per-case 'optimal' is mostly Wasmi v2 lazy-unchecked (unsafe new_unchecked, x1.04); the suite builds Wasmi without the std and memory64 defaults. On the M4 Pro (x8.06) and Xeon 8573C (x8.36) Wasmi keeps its interpreter rank with Silverfir-nano ahead everywhere; eager v2 startup is slower than V8 on the EPYC and M4 and faster on the Xeon; extra checks are off by default.

## Caveats and trade-offs

First-party: the suite and the plots repo are maintained and run by the Wasmi author (Robbepop). Ratios were read from the text labels of the rendered SVG; the plots repo records no runtime versions, toolchain or run date beyond its commit 'update AMD EPYC 7763 plots' (2026-08-25), so the plotted Wasmi v2 is a pre-release beta (v2.0.0 was released 2026-09-01; the suite README links v2.0.0-beta.7 while Cargo.toml now pins 2.0.0-beta.10). The EPYC 7763 is the CPU of GitHub's ubuntu-latest runners, so the run probably came from the workflow_dispatch CI jobs on a shared VM, but the plots repo does not say so. Startup ratios are dominated by lazy modes: 'lazy' defers both compilation and validation of function bodies to first use, so x1.37 skips work that Cranelift, Winch and V8 do eagerly; lazy-translation with eager validation (x10.66) and eager mode (x38.88) are fairer compile-cost comparisons, and eager Wasmi v2 is slower than V8 (x33.27) on startup. Execution: Wasmi v2 (eager) x12.40 beats WAMR fast-interpreter x17.07, Wasm3 (eager) x16.51 and Wasmtime (Pulley) x27.92, but loses to Silverfir-nano's interpreter x9.02, Wasmtime (Cranelift) x1.15 and V8 x1.05. The Wasmi README itself shows no numbers. Rust, not C++.

Interpreter: steady-state execution is about 11x slower than Wasmtime Cranelift (x12.40 vs x1.15 on the execution geomean, derived from page data at https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg). The fast startup depends on lazy compilation, and the 'lazy' modes defer validating function bodies until first call. Wasmi v2 was a beta (v2.0.0-beta.7) in the benchmark README.

## Maintenance

Actively maintained by its author with Stellar Development Foundation sponsorship; v2.0.0 released 2026-09-01 under Apache-2.0 OR MIT, used by Soroban, Typst, Zellij and smoldot, and copyable as a crate or C library today.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party: wasmi-benchmarks and its plots repo are maintained and run by the Wasmi author (Robbepop). The harness (benches/criterion, runtimes/wasmi-v2/lib.rs), bench profile flags and the CPU (AMD EPYC 7763 in the plot title) are public and every number matches the plot, but no rustc or C compiler version is recorded (CI uses dtolnay/rust-toolchain@stable, no rust-toolchain file) and the plots do not record which Wasmi v2 beta or baseline versions were measured, so not A; own suite with partial methodology is C.
- **Verifier notes:** All numbers in the record match the SVG labels (matched by y position); I added the Pulley, WAMR and lazy-translation startup rows and the execution comparison against the WAMR and Pulley baselines. Downgraded A to C: Wasmi's own suite run by its author, rustc and C compiler versions unrecorded, and the measured Wasmi v2 beta and baseline versions not stated on the plots. Shortcomings to record: first-party benchmark, startup headline relies on lazy validation, eager startup slower than V8, execution far behind JITs and behind Silverfir-nano's interpreter, pre-release v2 beta measured, Rust not C++. Metadata checked: Apache-2.0 OR MIT, 2.3k stars, not a fork or archived, last commit 2026-09-01 (Wasmi v2.0.0 release prep), active.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/commits/main>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/tree/main/data>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://github.com/wasmi-labs/wasmi-benchmarks/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/.github/workflows/startup.yml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/.github/workflows/main.yml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmi-v2/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmi-v2/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmi-v1/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmer/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/v8/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wamr/Cargo.toml>
  - <https://github.com/wasmi-labs/wasmi>
  - <https://github.com/wasmi-labs/wasmi/commits/main>
- **Sources the enricher read:**
  - <https://github.com/wasmi-labs/wasmi>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi/HEAD/crates/wasmi/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi/HEAD/crates/wasmi/src/engine/config.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi/HEAD/docs/usage.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi/HEAD/crates/c_api/README.md>
  - <https://github.com/wasmi-labs/wasmi/security/advisories>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/src/lib.rs>
  - <https://github.com/wasmi-labs/wasmi-benchmarks/tree/main/benches>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/main.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/startup.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/execute.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmi-v2/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmi-v2/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmer/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/v8/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wamr/lib.rs>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/tree/main/data>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/apple-m4-pro/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/apple-m4-pro/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/intel-xeon-platinum-8573c/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/intel-xeon-platinum-8573c/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wasmtime/Cargo.toml>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/wasmi-labs/wasmi`) · [data/wave12/enrich/raw/github_com_wasmi_labs_wasmi.json](../../../data/wave12/enrich/raw/github_com_wasmi_labs_wasmi.json) (enrichment confidence 0.8)

</details>
