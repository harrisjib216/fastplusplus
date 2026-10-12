# Wago

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Pure-Go, no-cgo single-pass Wasm-to-native compiler; compiles about 3x quicker than wazero in-process and edges it on cold runs.

| | |
|---|---|
| **Beats** | Wasmtime, Wasmer, V8 and wazero |
| **Claimed result** | README: 'compile 5x quicker and execute 1.9x faster than wazero' (these figures point at wago.sh, which is blocked, and are not reproduced by any committed data). Committed bench/runtime-corpus-study.md geometric means on Ryzen 7 7800X3D: compile wall wago 6.42 ms vs wazero 7.83, wasmtime 9.77, V8 14.44, wasmer 14.80 ms; cold execute wago 7.34 ms vs wazero 8.11, wasmtime 7.56, V8 16.84, wasmer 10.88, wasm3 9.91, wasmi 12.34 ms. On Apple M4 Max: compile wago 4.43 ms vs wazero 5.32, wasmtime 7.12, V8 14.75, wasmer 8.91; cold execute wago 4.77 ms vs wazero 5.27, wasmtime 5.95, V8 15.59, wasmer 6.76. So about 1.2x to 3.3x faster compile and 1.03x (wasmtime, AMD64) to 3.3x (V8, ARM64) lower cold execute latency (derived from page data). From the committed JSON, wago's internal Go-side compile time is a geometric mean 0.32x of wazero's on AMD64 and 0.43x on ARM64 over 63 modules (derived from page data). The separate committed startup sweep (bench/startup/startup-{amd64,arm64}.json, hyperfine -N, 6 Rust compute twins run from _start) gives wago end-to-end geometric means of 0.77x wazero, 0.62x wasmtime and 0.30x V8 on AMD64 and 0.75x wazero, 0.74x wasmtime and 0.30x V8 on ARM64 (derived from page data). |
| **Workload** | A 63-module corpus (PolyBench, Embench, Sightglass, CoreMark, AssemblyScript, zlib, zstd, QOI and others): compile latency (fresh process, load plus validate plus code generation) and cold execute latency (fresh process, load, compile, instantiate and first export call) as geometric means of per-module medians of 3 runs after 1 warmup, on AMD64 and ARM64. |
| **Metric** | startup |
| **Hardware** | AMD Ryzen 7 7800X3D (pinned to CPU 7) and Apple M4 Max |
| **Compiler and flags** | Engine versions listed (wasmtime 45.0.1/46.0.1, wasmer 7.1.0/7.3.0, V8 15.1.42/15.2.20, wazero 1.12.0 adapter, wasm3 0.9.0/0.5.0, wasmi_cli 1.1.0, WAVM prerelease, wazy 0.3.0). bench/go.mod at the study commit 7c382581 pins toolchain go1.22.2, but the study does not say how the wago CLI and the Go adapters were built; build flags not stated. |
| **Adoption** | 17 stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/wago-org/wago) · [benchmark](https://github.com/wago-org/wago/blob/main/bench/runtime-corpus-study.md) |

## Verdict

The first-party corpus study ran 63 modules (PolyBench, Embench, Sightglass, CoreMark, AssemblyScript, zlib, zstd and others) as the median of 3 fresh processes after 1 warmup, on a Ryzen 7 7800X3D pinned to CPU 7 and an Apple M4 Max. On AMD64, Wago's geometric-mean compile wall is 6.42 ms against wazero 7.83, Wasmtime 45.0.1 9.77, V8 14.44 and Wasmer 14.80 ms, and its cold execute (load, compile, instantiate, first call) is 7.34 ms against wazero 8.11 and Wasmtime 7.56 ms. In-process compile time is 0.32x wazero's on AMD64 and 0.43x on ARM64 (derived from page data). The Go toolchain and build flags are not stated.

## Use it when

- A Go service that loads Wasm plugins or per-tenant modules at run time without cgo, where compile latency matters. From the committed JSON, in-process compile is a geometric mean of 0.40 ms vs wazero's 1.23 ms on a Ryzen 7 7800X3D (0.32x) and 0.33 vs 0.77 ms on an M4 Max (derived from page data).
- Short-lived processes running compute kernels for tens of milliseconds. In the hyperfine startup sweep (six Rust twins, fresh process), Wago's end-to-end time is 0.77x wazero's and 0.62x Wasmtime's on AMD64, and 0.75x and 0.74x on ARM64 (derived from page data).
- Pure-Go embedding that needs post-MVP features: Core 3 families (WasmGC, exception handling, tail calls, memory64, relaxed SIMD) are listed as complete on linux/amd64, linux/arm64 and darwin/arm64.
- Shipping a Wasm program as a small standalone native executable via `wago compile`.

## Skip it when

- Long-running, steady-state compute where peak code quality decides. The study never isolates steady-state speed, and Wasmtime (Cranelift) beats Wago on several AMD64 cold-execute cases (polybench floyd-warshall 9.90 vs 14.00 ms, seidel-2d 10.28 vs 11.39, cholesky 7.63 vs 8.25, adi 8.36 vs 8.88 ms).
- Tiny, very short runs, where an interpreter wins outright: wasm3 and wasmi beat Wago on AMD64 for tiny (4.28/4.15 vs 6.33 ms), dispatch, many_funcs, linked_list and several small PolyBench kernels.
- Targets other than amd64/arm64 on Linux, macOS or Windows. Wago has no interpreter fallback, so 32-bit, riscv64 or js/wasm hosts cannot run modules at all.
- Production code that needs API and artifact stability. Wago is beta (v0.1.0-beta.11 on pkg.go.dev, 2026-09-28; the study ran a 0.0.0 dev build), has 17 stars and two main authors, and the .wago artifact codec is already at version 6 with no backward compatibility. A codegen bug in a pure-Go JIT is a memory-safety bug inside your Go process.

## How it is fast

The backend (Railshot) is a single forward pass that fuses code generation and register allocation using the 'Valent-Block' technique taken from the C++ WARP engine. A compile-time symbolic operand stack holds deferred constants, local/global reads and checked memory reads, and materializes them into registers only when a value is consumed or a side effect or join forces it. There is no IR and no separate register-allocation pass, which keeps compile time and Go-heap allocation low. Serial compilation writes code directly into an RW mmap that is flipped to RX on first instantiation (W^X, no copy). Module-wide analysis is followed by optional parallel per-function workers. At run time, calls use a uniform off-heap wrapper ABI (args, linear-memory base, trap slot, results) on a separate 4 MiB native stack, and supported platforms use guard-page bounds checks.

## Compared with alternatives

Over wazy (the catalogued wazero fork, within about 5-15% of Wago in the study) or wazero when compile latency and compile memory matter and you run only on amd64/arm64. Over wasm2go when modules arrive at run time rather than at build time. Over Wasmi or wasm3 once a module runs for more than a few milliseconds, since the interpreters win only the tiniest cold runs.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys only for the core; WASI (github.com/wago-org/wasi) and the Component Model (github.com/wago-org/component-model) are optional plugin modules |
| **Minimum toolchain** | Go 1.22 (go.mod); TinyGo builds are supported with documented restrictions (no cancelable native calls) |
| **Platforms** | Linux, macOS and Windows on amd64 and arm64 only. Guard-page bounds checks are available on linux/amd64, linux/arm64 and darwin/arm64, and explicit checks everywhere. FEATURES.md says the default amd64 backend expects SSSE3/SSE4.x/AVX encodings, with a wago_amd64_sse2 build tag for an SSE2 baseline. |
| **Thread safety** | Each Instance gates its own execution with per-instance activation counts and reservations, and RuntimeConfig is immutable. WasmFunc.OpenSession sessions are documented as not safe for concurrent use, and invocation result slices are borrowed until the next call on that instance. Wasm threads and atomics are an experimental opt-in (CoreFeatureThreads). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: process startup dominates the corpus study's 'compile wall' numbers. In the committed JSON, Wago's in-process compile is a geometric mean of 0.40 ms inside a 6.42 ms wall on AMD64, about 6% (wazero 1.23 of 7.83 ms; 0.33 of 4.43 ms on ARM64). The headline wall ratios against Wasmtime, V8 and Wasmer therefore mostly compare a single-purpose Go adapter's process start with full native CLIs (derived from page data).
- The 'allocated heap' column (Wago 67-110 KiB vs wazero about 1 MiB), which backs the README's 'a few kilobytes of RAM', counts Go TotalAlloc only. Wago writes native code directly into an mmap'd RW mapping and keeps runtime state in off-heap arenas, so those bytes are not counted. Peak RSS is the comparable figure: 6.77 vs 8.35 MiB on AMD64, 7.76 vs 8.90 MiB on ARM64.
- The headline claims drift and none is backed by committed data: the current README says 'execute 1.9x faster than wazero'; the v0.1.0-beta.11 README on pkg.go.dev says '80% faster'; search snippets of the author's dev.to post (blocked) say '5.7x faster to compile, 70% faster at execution', and another snippet says '40% quicker'. The committed study shows 1.03-1.11x lower cold-execute latency than wazero (7.34 vs 8.11 ms AMD64, 4.77 vs 5.27 ms ARM64).
- Reproducibility: at the study commit 7c382581, bench/go.mod and go.sum pin wazero v1.9.0 (toolchain go1.22.2), yet the study labels its wazero engine 'v1.12.0 adapter', and the build of the adapters and the wago CLI is not documented. On the same M4 Max, wasm3 is v0.5.0 in the corpus study and v0.9.0 in the startup sweep, and the two machines ran different Wasmtime, V8 and Wasmer versions. Open issue #826 itself notes that the cold, first-call and prepared-call phases are not yet separated in the benchmarks.

## Known shortcomings

- The README's 5x compile and 1.9x execute claims against wazero appear in no committed data (the study gives 0.32x internal compile, 0.43x on ARM64); cold start is mostly process startup, Wago ties wasmtime on AMD64 cold execute, and the Go build is undocumented. Go.
- Compile wall time is mostly process startup: in-process compile geomean 0.40 ms of 6.42 ms wall on AMD64, wazero 1.23 ms (0.32x). 'Allocated heap' counts Go TotalAlloc only while Wago emits code into mmap and keeps runtime state off-heap; peak RSS 6.77 vs 8.35 MiB is the fair figure. Headline drifts between README 1.9x, pkg.go.dev beta.11 '80% faster' and a dev.to snippet 70%/5.7x, none backed by committed data; the committed study shows 1.03-1.11x vs wazero cold execute. At study commit 7c382581 bench/go.mod pins wazero v1.9.0 while the study labels 'v1.12.0 adapter'. Open issue #826 admits the benchmarks do not separate cold, first-call and prepared-call phases.

## Caveats and trade-offs

Cold-start wall times include process start, so the large wins over V8 and WAVM partly reflect the CLI startup cost of those engines, and wago/wazero/wazy run through single-purpose Go adapters while the others use their native CLIs; the execute metric includes compile and only the first export call. Wago's cold execute is within noise of Wasmtime on AMD64 (7.34 vs 7.56 ms geomean) and loses to it on several PolyBench modules (floyd-warshall 14.00 vs 9.90 ms, seidel-2d 11.39 vs 10.28 ms); the wasm3 and wasmi interpreters beat wago on many small AMD64 cold-execute cases (tiny 4.28/4.15 vs 6.33 ms). Wazy, another pure-Go compiler, is within about 5-15% of wago. Compute-heavy steady-state speed was not isolated in the corpus study. The README's 5x and 1.9x figures point at wago.sh (blocked) and do not match any committed data. Three AssemblyScript modules are execution gaps for every engine. First-party benchmark (harness, JSON and study are public, CPUs named, Go build not documented), so held at C. Version is 0.0.0 beta.

Pure-Go Wasm-to-native compiler (amd64 and arm64); beta, WASI and the Component Model are external plugins. Not a steady-state throughput claim.

## Maintenance

Very active (several commits a day, last 2026-10-06), Apache-2.0, beta with two main authors. It is usable as a Go module today, but expect API and .wago artifact churn, and treat the README's speed headline as unbacked until the website data is committed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party study with public harness and raw JSON (bench/runtime-corpus-study.md, bench/results/runtime-corpus-{amd64,arm64}.json, bench/startup/run.mjs) naming both CPUs and every engine version, but neither the study nor the startup sweep states the Go toolchain or the build command and flags used for the wago CLI and the Go adapters, so it falls short of A.
- **Verifier notes:** Every number in claimed_speedup checks out against the study and the raw JSON; I recomputed the 0.32x internal-compile geomean (0.324 AMD64, 0.426 ARM64) and added the separate bench/startup hyperfine sweep. Shortcomings: the README's 5x/1.9x headline is unbacked by committed data; cold-start numbers are dominated by process startup; wasmtime matches or beats it on AMD64 cold execute; Go build not documented. wago.sh is EGRESS_BLOCKED.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** independent measurement separating compile, cold and warm phases
- **Pages the verifier opened:**
  - <https://github.com/wago-org/wago>
  - <https://github.com/wago-org/wago/commits/main>
  - <https://github.com/wago-org/wago/tree/main/bench>
  - <https://github.com/wago-org/wago/tree/main/bench/results>
  - <https://github.com/wago-org/wago/tree/main/bench/startup>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/README.md>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/runtime-corpus-study.md>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/results/runtime-corpus-amd64.json>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/results/runtime-corpus-arm64.json>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/startup/README.md>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/startup/startup-amd64.json>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/startup/startup-arm64.json>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/go.mod>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/go.mod>
  - <https://raw.githubusercontent.com/wago-org/wago/7c382581d8c53f06bb53879ddf4e28db6c47ce80/bench/go.mod>
  - <https://raw.githubusercontent.com/wago-org/wago/7c382581d8c53f06bb53879ddf4e28db6c47ce80/.just/bench.just>
- **Sources the enricher read:**
  - <https://github.com/wago-org/wago>
  - <https://github.com/wago-org/wago/commits/main>
  - <https://github.com/wago-org/wago/issues>
  - <https://github.com/wago-org/wago/issues/826>
  - <https://github.com/wago-org/wago/tree/main/bench>
  - <https://github.com/wago-org/wago/tree/main/bench/cmd>
  - <https://github.com/wago-org/wago/tree/main/bench/internal>
  - <https://github.com/wago-org/wago/tree/main/scripts>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/README.md>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/FEATURES.md>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/ROADMAP.md>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/go.mod>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/go.mod>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/runtime-corpus-study.md>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/results/runtime-corpus-amd64.json>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/results/runtime-corpus-arm64.json>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/startup/README.md>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/startup/runtimes.json>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/startup/startup-amd64.json>
  - <https://raw.githubusercontent.com/wago-org/wago/HEAD/bench/startup/startup-arm64.json>
  - <https://raw.githubusercontent.com/wago-org/wago/7c382581d8c53f06bb53879ddf4e28db6c47ce80/bench/go.mod>
  - <https://raw.githubusercontent.com/wago-org/wago/7c382581d8c53f06bb53879ddf4e28db6c47ce80/bench/go.sum>
  - <https://raw.githubusercontent.com/wago-org/wago/7c382581d8c53f06bb53879ddf4e28db6c47ce80/go.work>
  - <https://raw.githubusercontent.com/wago-org/wago/7c382581d8c53f06bb53879ddf4e28db6c47ce80/.just/bench.just>
  - <https://pkg.go.dev/github.com/wago-org/wago>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/wago-org/wago`) · [data/wave12/enrich/raw/github_com_wago_org_wago.json](../../../data/wave12/enrich/raw/github_com_wago_org_wago.json) (enrichment confidence 0.75)

</details>
