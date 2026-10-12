# submilli-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Safe-Rust Wasm 3.0 interpreter with a wasmtime-shaped API; compiles modules about 90x faster than Wasmtime's Cranelift JIT.

| | |
|---|---|
| **Beats** | Wasmtime (Cranelift), Wasmer (Cranelift) startup |
| **Claimed result** | Startup geomean on AMD EPYC 7763 relative to the per-case fastest runtime (lower is better): Submilli-wasm x18.08 versus Wasmtime (Cranelift) x1634.19, Wasmer (Cranelift) x1484.15, Wasmtime (Winch) x298.15 and Wasmer (Singlepass) x162.12; V8 is x33.27. About 90x faster startup than Wasmtime (Cranelift) and 82x faster than Wasmer (Cranelift) (derived from page data). Per case in the raw data (wasmi-benchmarks data/amd-epyc-7763/criterion.json): coremark 118.5 us vs 9.87 ms, ffmpeg 187.3 ms vs 17.96 s for Wasmtime (Cranelift). |
| **Workload** | wasmi-benchmarks startup suite: compile + instantiate of 7 modules from tiny to huge, geometric mean of per-case ratios against the fastest runtime for each case. |
| **Metric** | startup |
| **Hardware** | AMD EPYC 7763 (plot title and data/amd-epyc-7763 directory). This is the CPU of GitHub's ubuntu-latest runners and the suite's startup.yml workflow runs there, so the data probably come from a shared CI VM (not confirmed). The plots repo also holds Apple M2 Pro, Apple M4 Pro, Intel i7700 and Intel Xeon Platinum 8573C data, not read here. |
| **Compiler and flags** | wasmi-benchmarks (github.com/wasmi-labs/wasmi-benchmarks) Cargo.toml [profile.bench] lto = "fat", codegen-units = 1, run as 'cargo criterion --bench criterion --all-features ... startup/' (criterion 0.8.2; sample_size 10, 2 s measurement, 1 s warm-up). Rust toolchain: .github/workflows/startup.yml uses dtolnay/rust-toolchain@stable with no rust-toolchain file, so the rustc version is not recorded; the C/C++ runtimes are built with gcc-15/g++-15 (.github/actions/install-dependencies). Runtime versions are pinned only by the Cargo.lock at HEAD (wasmtime 47.0.3, wasmer 7.2.1); the plots repo does not record which suite commit produced them. |
| **Adoption** | 4 stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/submilli/submilli-wasm) · [benchmark](https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg) |

## Verdict

In the Wasmi author's wasmi-benchmarks startup suite (criterion, Store::new plus Module::new plus instantiate of 7 modules from CoreMark to ffmpeg, AMD EPYC 7763, probably a GitHub Actions VM, bench profile with fat LTO and codegen-units=1, stable rustc of unrecorded version), submilli-wasm 0.1.3 reaches a geomean of x18.08 relative to the per-case fastest runtime. Wasmtime with Cranelift is at x1634.19 and Wasmer with Cranelift at x1484.15, about 90x and 82x slower (derived from page data); for example coremark takes 118.5 us vs 9.87 ms. This is an interpreter beating optimizing JITs on compile time only. Lazy interpreters still start faster, and V8 starts faster on the big modules.

## Use it when

- Modules that run exactly once or a handful of times, where JIT compile time (Cranelift took \~190 ms for a 4 MiB module per the README) is most of the cost.
- Multi-tenant hosts running untrusted guests: the tree has no unsafe code (CI-gated), guest-reachable paths trap instead of panicking, and memory, stack, fuel, epochs and GC heap are bounded per Store.
- Embedders already written against wasmtime's API, including async host functions, who want interpreter-class startup without rewriting their integration.
- Guests compiled from GC languages or using exception handling: it claims full Wasm 3.0 (GC, try_table/exnref, tail calls, memory64, multi-memory, SIMD behind a feature) with zero skips on the upstream spec suite.
- Small modules (tens to hundreds of KiB) with light compute, where its run-once total beats eager Wasmi and Wasmtime in its own benchmark (469 us vs 837 us vs 5.72 ms at sieve(1k)).

## Skip it when

- Compute-heavy guests or modules reused many times: its own table shows CoreMark 715 vs Wasmtime 36996 and Wasmi 3032, and sieve(1M) run-once 57.39 ms vs Wasmtime 7.23 ms and Wasmi 11.30 ms. In the wasmi-benchmarks suite its execution geomean is x83.39 behind the fastest runtime.
- If startup is the only goal and you can live without GC and exceptions: Wasmi with lazy translation (x1.37), Wasm3 lazy (x2.77) and DLR wasm-interpreter (x10.95) all start faster than submilli-wasm (x18.08) on the same suite.
- Host-call-heavy loops where the boundary dominates: ping x100k takes 3.52 ms vs 325.92 us for Wasmtime and 1.15 ms for Wasmi (about 35 ns vs 3.3 ns and 11.5 ns per call, derived from page data), even though the README calls the boundary cheap.
- Memory density matters more than startup: fixed 16-byte ops take about 2x Wasmi's resident size (spidermonkey 31.0 MiB vs 16.5 MiB).
- You need WASI, the component model, threads/atomics, custom-page-sizes or wasmtime APIs beyond the subset implemented. The project is experimental: first commit 2026-07-06, 4 stars, no issues filed.

## How it is fast

Module::new does validation and lowering in one fused decode pass over the bytes (wasmparser underneath). Each internal op is written once into module-wide arenas as a fixed 16-byte op, with wide immediates in side pools and branch targets in a folded sidetable, so no second pass and no machine-code generation happens. The authors measure this at about 1.4x the raw wasmparser validation cost. Store::new allocates nothing, and the dispatch loop (`loop { match op }` over explicit operand and frame stacks) runs sync host calls inside the loop without suspending. Execution speed was deliberately traded away for this.

## Compared with alternatives

Pick it over Wasmi, DLR wasm-interpreter, Fizzy, toywasm or tinywasm when you need Wasm GC plus exception handling and wasmtime's API (including async host functions) for untrusted run-once guests. Wasmi with lazy translation starts faster and executes about 4x faster, so it is the better choice whenever GC and exceptions are not required.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | wasmparser 0.252, anyhow, gimli 0.33 (DWARF backtraces), serde, postcard; async-trait with the optional `async` feature |
| **Minimum toolchain** | Rust 2021 edition; no rust-version declared (the code uses Option::is_none_or, stable since Rust 1.82) |
| **Platforms** | any target Rust supports (pure safe Rust, no JIT, no platform-specific code); a wasm32 smoke build is mentioned in commits |
| **Thread safety** | Engine is Arc-backed and Send + Sync; Store&lt;T&gt; is Send when T: Send and !Sync, with one execution at a time per store. Run many stores in parallel on one engine; wasm threads are not supported. |
| **Drop-in for the baseline** | partial — the same type and method names as wasmtime 45.x via a Cargo rename, but only the subset the authors' product uses; no WASI, component model or threads, and some Config knobs (async_stack_size, cranelift_opt_level) are accepted as no-ops |

## Gotchas

- The measured code is old: wasmi-benchmarks pins submilli-wasm 0.1.2 and its Cargo.lock resolves 0.1.3 (2026-08-09). crates.io's latest is 0.1.9 (2026-10-03) and the repo is at 0.1.10. Later versions added lazy module visits and other compile-path changes, so current startup may differ from the plotted x18.08.
- Panic hardening is recent: 'fix(gc): return errors instead of panicking on layout and type-registry lookups' (2026-10-02) and 'Harden interpreter against invariant panics' (2026-10-06). Its own README says a panic takes down every tenant in the process, so older versions, including the benchmarked 0.1.3, had guest-reachable panics. Pin to the newest version for untrusted code.
- Config::async_support defaults to on in Config::default() (unlike wasmtime), but the setter's doc comment says 'Off by default' and ARCHITECTURE.md says sync entry points panic once async is enabled. The wasmi-benchmarks adapter calls the sync API with the default config, so check behaviour rather than trusting the docs. The setter only exists with the `async` feature.
- Backtraces are on by default and cost about 10% startup and 20% module RAM; Config::wasm_backtrace(false) turns them off. The wasmi-benchmarks adapter leaves them on, so the suite's startup figure is slightly conservative. The dispatch loop is generic over the Store&lt;T&gt; data type, so it monomorphizes in your crate once per store type.

## Known shortcomings

- Downgraded A to B: measured 0.1.2/0.1.3 (repo now 0.1.10), 4 stars, startup-only win (about 90x against Cranelift, derived) in the wasmi-benchmarks suite; the README table is first-party on an unnamed Apple machine, host calls are slower than wasmtime, rustc version unrecorded. Rust, not C++.
- Enricher (via tinywasm): wasmi-benchmarks builds wasmtime 47.0.0 with default-features=false, so the Cranelift startup column compiles single-threaded and the about 90x startup gap is overstated against a default multi-core Wasmtime.
- Enricher: the wasmi-benchmarks startup harness is clean (startup.rs times Store, Module::new and instantiate with no compile cache and backtraces on, a conservative 10% penalty), but the measured 0.1.3 predates the guest-reachable panic fixes of 2026-10-02 and 2026-10-06 (crates.io 0.1.9, repo 0.1.10); host calls are slower than wasmtime and wasmi despite the README's 'cheap' claim (35 vs 3.3 vs 11.5 ns, derived), async_support defaults on against its own doc comment, and the cited PERF-NOTES.md is a 404.

## Caveats and trade-offs

The suite is maintained and run by the Wasmi author, so it is third-party for submilli-wasm. Ratios were read from the SVG text labels and checked against the raw criterion data. The suite requires submilli-wasm 0.1.2 and its HEAD Cargo.lock resolves 0.1.3 (2026-08-09); the repo is now at 0.1.10, so the measured code is old for a project this young. Win is an interpreter versus optimizing JITs; among interpreters Wasmi v2 lazy x1.37, Wasm3 lazy x2.77, DLR wasm-interpreter x10.95 and Wasmi v2 lazy-translation x10.66 start faster, and V8 starts faster on pulldown-cmark, spidermonkey (10.9 ms vs 49.8 ms) and ffmpeg (35.5 ms vs 187.3 ms). Startup-only win: execution geomean on the same CPU is x83.39. The README's own cross-engine table (one unnamed Apple Silicon machine, wasmtime with Cranelift optimization disabled, wasmi eager) reports Module::new coremark 51.12 us vs wasmtime 792.71 us and wasmi 100.71 us, and CoreMark score 715 vs wasmtime 36996 and wasmi 3032; its sieve(1M) run is 57.39 ms vs wasmtime 7.23 ms and host calls are slower than both (3.52 ms vs 325.92 us per 100k pings). Data probably from a shared GitHub Actions VM. Very new (first commit 2026-07-06), 4 stars.

Built for modules that run exactly once (single-run, untrusted guests); Wasm 3.0 with GC and exception handling and a wasmtime-shaped API. Fixed 16-byte ops make code about 2x larger than Wasmi's IR.

## Maintenance

Active (100 commits since 2026-07-06, last commit 2026-10-06) and Apache-2.0, but self-described as experimental and maintained by one product team with 4 stars and no external issues. Fine to adopt for its stated niche if you pin the latest version and test the wasmtime API subset you use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now B.
- **Tier reason:** Independent third-party suite (wasmi-labs/wasmi-benchmarks: benches/criterion/startup.rs, runtimes/submilli-wasm/lib.rs, Module::new + Linker::instantiate) with public code, bench-profile flags, a named CPU and raw criterion data that reproduce the plotted geomeans exactly. Not A: no rustc version recorded and no suite commit named; the README's own table is first-party on an unnamed Apple Silicon machine.
- **Verifier notes:** Plot, raw data and README numbers all match the record. Downgraded A to B for the unrecorded rustc version and suite commit. Shortcomings to record: measured 0.1.2/0.1.3 against a current 0.1.10; startup-only win against optimizing JITs, slower than lazy Wasmi and DLR wasm-interpreter; execution about 50x behind a JIT on CoreMark per its own README; host calls slower than wasmtime and wasmi; 4 stars. Metadata checked: Apache-2.0, 4 stars, not a fork, last commit 2026-10-06.
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
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/submilli-wasm/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/submilli-wasm/Cargo.toml>
  - <https://github.com/submilli/submilli-wasm>
  - <https://github.com/submilli/submilli-wasm/commits>
  - <https://raw.githubusercontent.com/submilli/submilli-wasm/HEAD/README.md>
  - <https://crates.io/api/v1/crates/submilli-wasm>
- **Sources the enricher read:**
  - <https://github.com/submilli/submilli-wasm>
  - <https://github.com/submilli/submilli-wasm/tree/main/src>
  - <https://github.com/submilli/submilli-wasm/commits>
  - <https://github.com/submilli/submilli-wasm/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/submilli/submilli-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/submilli/submilli-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/submilli/submilli-wasm/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/submilli/submilli-wasm/HEAD/docs/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/submilli/submilli-wasm/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/submilli/submilli-wasm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/submilli/submilli-wasm/HEAD/src/engine.rs>
  - <https://raw.githubusercontent.com/submilli/submilli-wasm/HEAD/src/config.rs>
  - <https://raw.githubusercontent.com/submilli/submilli-wasm/HEAD/src/linker.rs>
  - <https://raw.githubusercontent.com/submilli/submilli-wasm/HEAD/PERF-NOTES.md>
  - <https://crates.io/api/v1/crates/submilli-wasm>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/submilli-wasm/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/submilli-wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/startup.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.lock>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/submilli/submilli-wasm`) · [data/wave12/enrich/raw/github_com_submilli_submilli_wasm.json](../../../data/wave12/enrich/raw/github_com_submilli_submilli_wasm.json) (enrichment confidence 0.7)

</details>
