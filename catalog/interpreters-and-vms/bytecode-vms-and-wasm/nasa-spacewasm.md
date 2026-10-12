# SpaceWasm (NASA JPL)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> NASA JPL's no_std Wasm 1.0 interpreter for flight software; compiles plus instantiates modules about 60x faster than Wasmtime or Wasmer Cranelift.

| | |
|---|---|
| **Beats** | Wasmtime (Cranelift), Wasmer (Cranelift) startup |
| **Claimed result** | Startup geomean on AMD EPYC 7763 relative to the per-case fastest runtime (lower is better): SpaceWasm x25.84 versus Wasmtime (Cranelift) x1634.19, Wasmer (Cranelift) x1484.15, Wasmtime (Winch) x298.15 and Wasmer (Singlepass) x162.12; V8 is x33.27. About 63x faster startup than Wasmtime (Cranelift) and 57x faster than Wasmer (Cranelift) (derived from page data). Per case in the raw data (wasmi-benchmarks data/amd-epyc-7763/criterion.json): coremark 109.0 us vs 9.87 ms, ffmpeg 293.0 ms vs 17.96 s for Wasmtime (Cranelift). |
| **Workload** | wasmi-benchmarks startup suite: compile + instantiate of 7 modules from tiny to huge, geometric mean of per-case ratios against the fastest runtime for each case. |
| **Metric** | startup |
| **Hardware** | AMD EPYC 7763 (plot title and data/amd-epyc-7763 directory). This is the CPU of GitHub's ubuntu-latest runners and the suite's startup.yml workflow runs there, so the data probably come from a shared CI VM (not confirmed). The plots repo also holds Apple M2 Pro, Apple M4 Pro, Intel i7700 and Intel Xeon Platinum 8573C data, not read here. |
| **Compiler and flags** | wasmi-benchmarks (github.com/wasmi-labs/wasmi-benchmarks) Cargo.toml [profile.bench] lto = "fat", codegen-units = 1, run as 'cargo criterion --bench criterion --all-features ... startup/' (criterion 0.8.2; sample_size 10, 2 s measurement, 1 s warm-up). Rust toolchain: .github/workflows/startup.yml uses dtolnay/rust-toolchain@stable with no rust-toolchain file, so the rustc version is not recorded; the C/C++ runtimes are built with gcc-15/g++-15 (.github/actions/install-dependencies). Runtime versions are pinned only by the Cargo.lock at HEAD (wasmtime 47.0.3, wasmer 7.2.1); the plots repo does not record which suite commit produced them. |
| **Adoption** | 1.6k stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/nasa/spacewasm) · [benchmark](https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg) |

## Verdict

In the third-party wasmi-benchmarks startup suite (time to compile, validate and instantiate 7 modules from a 0.1 ms ERC-20 contract to ffmpeg; criterion; bench profile with fat LTO; AMD EPYC 7763, probably a GitHub Actions VM; spacewasm 0.5.2, wasmtime 47.0.3, wasmer 7.2.1), SpaceWasm's geomean is x25.84 of the per-case fastest, against x1634.19 for Wasmtime (Cranelift) and x1484.15 for Wasmer (Cranelift). That is about 63x and 57x faster startup; per case, CoreMark takes 0.109 ms vs 9.87 ms and ffmpeg 0.293 s vs 17.96 s against Wasmtime (Cranelift). The rustc version and suite commit are not recorded.

## Use it when

- Embedded or no_std Rust hosts that must load a module from flash or a file in chunks, without holding the whole binary in one contiguous buffer.
- Systems with flight-software memory rules: allocation only during module initialisation, from a capped set of fixed-size pages, with failures returned as errors and never panics.
- Hosts that need bounded, resumable execution: run() takes an instruction budget and returns OutOfFuel, host functions can pause the engine and resume it later, and interpreted calls do not use the native stack.
- Short-lived invocations of MVP modules where compile plus instantiate time dominates: about 0.1 ms for CoreMark or an ERC-20 contract on an EPYC 7763, against about 10 ms for Wasmtime (Cranelift).

## Skip it when

- Compute-heavy or long-running code: its execution geomean in the same suite is x79.53 of the fastest, against WAMR fast-interpreter x17.07 and Wasmtime Pulley x27.92, and JITs are far faster.
- Modules that use post-MVP features (bulk memory, sign extension, non-trapping float-to-int, multi-value, SIMD, tail calls). Recent clang and rustc emit some of these by default, so you have to build with -mcpu=mvp or post-process with the bundled wasm2mvp.sh.
- When only the lowest startup matters: Wasmi v2 lazy (x1.37), wasm3 lazy, DLR-FT wasm-interpreter, submilli-wasm and toywasm all start faster, and V8 starts faster on the three largest modules (spidermonkey 10.9 ms vs 65.2 ms, ffmpeg 35.5 ms vs 293.0 ms).
- Untrusted modules on 32-bit targets, or modules with more than 65,535 functions or globals, until open issues #158 and #201 are fixed.
- Projects that need a stable API: 13 crates.io releases between 0.4.4 (2026-07-27) and 0.7.1 (2026-09-04), and CompilerOptions changed between the 0.5.2 API used by the benchmark adapter and the repo's own HEAD bench.

## How it is fast

Startup is cheap because there is no optimizing back end. A single streaming pass decodes, validates and lowers the bytecode into a fixed-width IR of 16-bit words, with indexes and branch targets already resolved. No machine code is generated and nothing gets a second pass. Execution is a plain stack-machine interpreter (a visitor dispatching one IR instruction at a time, counting fuel per instruction), so the startup advantage over JITs disappears on long runs.

## Compared with alternatives

Pick SpaceWasm over Wasmi or wasm3 when its flight-software constraints matter more than speed: no_std, init-only fixed-page allocation, chunked streaming decode and fuel-bounded resumable execution. Wasmi starts and executes faster. Pick it over DLR-FT wasm-interpreter, which starts faster (x10.95 vs x25.84) and whose requirement set SpaceWasm adopted, if you want NASA JPL's implementation with its C API and WASI runner.

## Integration

| | |
|---|---|
| **Form** | crate (no_std); also a C static/shared library via crates/spacewasm_c_api |
| **Dependencies** | libm =0.2.16 only (pinned under the project's no-dependencies requirement); the embedder must install an allocator through the spacewasm::global_allocator! macro (its own C-ABI hooks, not Rust's #[global_allocator]) |
| **Minimum toolchain** | Rust 1.87 (2024 edition) |
| **Platforms** | any Rust no_std target in principle; uses x86 inline asm (sqrtss) for some float ops, with a miri-soft-floats feature to switch to soft floats; 32-bit targets have an open decoder-panic bug (#158) |
| **Thread safety** | not documented; an Engine owns one interpreter stack and run() takes &mut Engine, so use one engine per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Open issue #201 (2026-09-14): get_func_ref and get_global_ref narrow a validated index with 'as u16'. A module with 65,537 globals validates, and global.get 65536 silently returns global 0's value. Issue #158: a malformed module panics the decoder on 32-bit targets, which contradicts the no-panic requirement on the flight targets it aims at.
- Benchmark harness asymmetries (from wasmi-benchmarks source, effect on the numbers not measured). The SpaceWasm adapter replaces the flight PageAllocator with plain malloc/free and feeds the module in copied 1 KiB chunks. The Wasmtime adapter builds wasmtime 47.0.3 with default-features = false (runtime and anyhow only), so the default parallel-compilation feature is off: Cargo.lock shows no rayon under wasmtime, while the Wasmer compilers do pull rayon. The 63x gap to stock Wasmtime Cranelift on a multi-core machine is therefore likely overstated, though Wasmer (Cranelift), whose compilers pull rayon, was only about 10% faster than Wasmtime (Cranelift) here.
- Only startup was measured in its favour: the comparison is a single-pass interpreter translator against optimizing JITs. Among eager translators doing the same full validation and translation, SpaceWasm beats Wasmi v2 eager and wasm3 eager on 6 of 7 modules but loses on pulldown-cmark (8.8 ms vs 5.3 ms and 8.1 ms) (derived from page data).
- The IR is fixed-width and usually larger than the bytecode. Hard limits include 256 modules per store, 255 parameter words, 65,535 local words, 32-byte import and custom-section names, and a ±2,097,151-instruction branch range; a longer import name is rejected at decode time. unsafe code sits in the stack, memory and IR-reader hot paths and relies on the up-front validator; the strict-assertions feature re-checks bounds at run time.

## Known shortcomings

- Downgraded A to B: measured version 0.5.2 (current 0.7.1), startup-only win (about 63x against Cranelift, derived) with V8 faster on the 3 largest modules; MVP only, execution x79.53 in the wasmi-benchmarks suite, rustc version unrecorded. Rust, not C++.
- Enricher (via tinywasm): wasmi-benchmarks builds wasmtime 47.0.0 with default-features=false, so the Cranelift startup column compiles single-threaded and the about 63x startup gap is overstated against a default multi-core Wasmtime.
- Enricher: wasmi-benchmarks builds Wasmtime 47.0.3 with default-features=false so parallel compilation is off (no rayon under wasmtime in Cargo.lock while the Wasmer compilers pull it), and the SpaceWasm adapter swaps the flight PageAllocator for malloc and feeds 1 KiB copied chunks, so the 63x over stock Wasmtime is likely overstated; against eager translators doing the same work it beats Wasmi v2 eager and wasm3 eager on 6 of 7 modules and loses pulldown-cmark (8.8 ms vs 5.3 ms, derived). Open bugs #201 ('as u16' narrowing: global.get 65536 silently returns global 0) and #158 (decoder panic on 32-bit); 13 releases in 6 weeks.

## Caveats and trade-offs

The suite is maintained and run by the Wasmi author, so it is third-party for SpaceWasm. Ratios were read from the SVG text labels and checked against the raw criterion data. The suite pins spacewasm 0.5.2 (2026-08-05); the current release is 0.7.1 (2026-09-04), so the numbers predate later changes. Win is an interpreter versus optimizing JITs; among interpreters it is mid-pack (Wasmi v2 lazy x1.37, Wasm3 lazy x2.77, DLR wasm-interpreter x10.95, submilli-wasm x18.08 all start faster), and V8 starts faster on pulldown-cmark (2.30 ms vs 8.82 ms), spidermonkey (10.9 ms vs 65.2 ms) and ffmpeg (35.5 ms vs 293.0 ms). Startup-only win: execution geomean on the same CPU is x79.53, slower than Wasmtime (Pulley) x27.92 and WAMR x17.07, and covers only 18 of 21 cases because SpaceWasm implements Wasm 1.0 MVP only (no multi-value, bulk memory or tail calls). Data probably from a shared GitHub Actions VM. The README states only that Coremark is used to track regressions.

Wasm 1.0 (MVP) only, no_std, deterministic fixed-size page allocation and streaming decode for flight software.

## Maintenance

Active and Apache-2.0 (1.6k stars, last commit 2026-09-28, frequent 0.x releases with API churn). Usable as a crate today for MVP modules, but test and validator coverage is still being fixed: open issue #209 says the README overstates unit-test instruction coverage, and #206 says the differential validator oracle tests never run in CI.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now B.
- **Tier reason:** Independent third-party suite (wasmi-labs/wasmi-benchmarks: benches/criterion/startup.rs, runtimes/spacewasm/lib.rs, which creates the engine, compiles to SpaceWasm IR, validates and instantiates) with public code, bench-profile flags, a named CPU and raw criterion data that reproduce the plotted geomeans exactly. Not A: no rustc version recorded (dtolnay/rust-toolchain@stable) and no suite commit named in the plots repo.
- **Verifier notes:** Numbers match the plot and the raw data. Downgraded A to B for the unrecorded rustc version and suite commit. Shortcomings to record: measured release 0.5.2 is two minor versions old; startup-only win against optimizing JITs; V8 starts faster on the three largest modules; execution about 4.7x slower than WAMR (derived); MVP-only feature set. Metadata checked: Apache-2.0, 1.6k stars, not a fork, last commit 2026-09-28.
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
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/spacewasm/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/spacewasm/Cargo.toml>
  - <https://github.com/nasa/spacewasm>
  - <https://github.com/nasa/spacewasm/commits>
  - <https://crates.io/api/v1/crates/spacewasm>
- **Sources the enricher read:**
  - <https://github.com/nasa/spacewasm>
  - <https://raw.githubusercontent.com/nasa/spacewasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/nasa/spacewasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/nasa/spacewasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/nasa/spacewasm/HEAD/docs/ir.md>
  - <https://raw.githubusercontent.com/nasa/spacewasm/HEAD/docs/REQUIREMENTS.md>
  - <https://raw.githubusercontent.com/nasa/spacewasm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/nasa/spacewasm/HEAD/src/interpreter.rs>
  - <https://github.com/nasa/spacewasm/tree/main/crates/spacewasm_std/benches>
  - <https://raw.githubusercontent.com/nasa/spacewasm/HEAD/crates/spacewasm_std/benches/coremark.rs>
  - <https://github.com/nasa/spacewasm/issues>
  - <https://github.com/nasa/spacewasm/issues/62>
  - <https://github.com/nasa/spacewasm/issues/201>
  - <https://crates.io/api/v1/crates/spacewasm>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/spacewasm/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/spacewasm/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/startup.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmer/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/data/amd-epyc-7763/criterion.json>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/v47.0.3/crates/wasmtime/Cargo.toml>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/nasa/spacewasm`) · [data/wave12/enrich/raw/github_com_nasa_spacewasm.json](../../../data/wave12/enrich/raw/github_com_nasa_spacewasm.json) (enrichment confidence 0.75)

</details>
