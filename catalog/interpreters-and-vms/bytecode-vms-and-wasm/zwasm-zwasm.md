# zwasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `Apache-2.0` · 🟢 active

> Zig WebAssembly runtime (interpreter, single-pass JIT, AOT) that starts short WASI guests 2.2-3.6x faster than wasmtime, with less memory.

| | |
|---|---|
| **Beats** | wasmtime 43.0.1; wasmer 5.0.4; wazero 1.11.0; WasmEdge 0.16.1 (interpreter) |
| **Claimed result** | Startup-bound short workloads (mean ms): tinygo/fib zwasm-aot 2.0, interp 2.3, jit 2.8 vs wasmtime 7.2, wazero 7.1, wasmer 12.0, WasmEdge 16.5. Peak RSS on tinygo/fib: zwasm-aot 2.1 MB, jit 3.2, interp 2.7 vs wazero 8.7, wasmtime 13.3, WasmEdge 23.7, wasmer 27.5 ('4-12x less'). |
| **Workload** | End-to-end wall time of '&lt;runtime&gt; run &lt;module&gt;' (spawn, instantiate, execute WASI _start) with hyperfine on short TinyGo and ClojureWasm guests, plus peak RSS via /usr/bin/time -l. |
| **Metric** | startup |
| **Hardware** | Apple M4 Pro (Mac aarch64), one host |
| **Compiler and flags** | zwasm built with Zig 0.16.0 (pinned in flake.nix) via zig build -Doptimize=ReleaseFast; comparators wasmtime 43.0.1, wazero 1.11.0, wasmer 5.0.4, WasmEdge 0.16.1 pinned in flake.nix devShells.bench; hyperfine 5 runs plus 3 warmup; peak RSS via /usr/bin/time -l. |
| **Adoption** | 186 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/zwasm/zwasm) · [benchmark](https://github.com/zwasm/zwasm/blob/main/docs/benchmarks.md) |

## Verdict

On one Apple M4 Pro with zwasm built ReleaseFast by Zig 0.16.0 and comparators pinned by Nix (wasmtime 43.0.1, wazero 1.11.0, wasmer 5.0.4, WasmEdge 0.16.1 interpreter), hyperfine (5 runs, 3 warmups) timed whole '&lt;runtime&gt; run' processes on four tiny TinyGo/ClojureWasm guests: zwasm took 2.0-2.9 ms against 6.3-7.2 ms for wasmtime and wazero, about 12 ms for wasmer and 16 ms for WasmEdge, with 2.1-5.1 MB peak RSS against 8.6-27.5 MB. The same doc shows zwasm 1.5-13.7x slower than wasmtime once startup is amortized, so the result is a cold-start and footprint win only.

## Use it when

- Short-lived CLI, scripting or serverless invocations where each process runs a small WASI guest for a few milliseconds and cold start dominates.
- Memory-constrained hosts running many small guests in separate processes (2-5 MB peak RSS per process on the TinyGo/ClojureWasm fixtures).
- You want WASI 0.2 components or WASI 0.3 native async from a compact C-embeddable runtime that is not wasmtime.
- Ship .cwasm artifacts built ahead of time with zwasm compile and run them with the lowest load latency.

## Skip it when

- Compute-heavy or long-running guests: wasmtime, wasmer and wazero are 1.5-3.9x faster on fib2, sieve, matrix and heapsort and 13.7x faster on base64; issue #500 reports QuickJS fib(30) at 7.59 s on the zwasm JIT vs 0.108 s on wasmtime (about 70x, mostly spill traffic).
- You need a fast interpreter: an independent harness (rebeckerspecialties/wasm-benchmark, M4 Max E-cores) puts the zwasm interpreter at 8.47x the fastest runtime's CPU time, against wasm3 1.01 and WAMR 1.63, and the interpreter has no SIMD.
- Many instances of one large module in-process: the C API recompiles the module per instance (issue #499: 35 MiB RSS and 155 ms per extra JIT instance of a 1.5 MB module), and the independent harness found GC structs are never collected while an instance lives.
- Hostile guests on the JIT before open safety bugs close: frames over 16 KiB crash the process instead of trapping on x86_64 Linux (#495), and temporaries live across call_ref or table.grow can be silently clobbered (#505, wrong result with no error).
- Platforms beyond macOS aarch64, Linux x86_64/aarch64 and Windows x86_64; Linux aarch64 is cross-built and not in the per-release test gate.

## How it is fast

There is no optimizing tier: the JIT lowers each function in one pass with a small register pool, so instantiation costs about 2-3 ms per process instead of paying Cranelift compile time up front, and AOT .cwasm skips codegen at load. Resident memory stays at 2-5 MB because there is no multi-pass compiler state and, for AOT and the interpreter, no JIT code buffers. The same design makes sustained compute 1.5-3.9x slower than Cranelift (13.7x on base64).

## Compared with alternatives

Pick zwasm over wasm3 or WAMR when you need Wasm 3.0 plus WASI 0.2/0.3 components and short cold-start runs rather than interpreter throughput (wasm3 is about 8x faster per call in the independent harness); WAMR in Zig (cataggar/wamr) reports a lower in-process cold start (1.43 ms vs wasmtime 6.96 ms) if you only need core Wasm, and Wasmi leads startup for Rust embedders.

## Integration

| | |
|---|---|
| **Form** | CLI binary, static lib (libzwasm.a with wasm.h, wasi.h, zwasm.h) or Zig module via build.zig.zon; Rust bindings in the separate zwasm-rust-sdk crates |
| **Dependencies** | none at runtime; building from source needs Zig 0.16.0 and wasm-tools (generates the spec-test module) |
| **Minimum toolchain** | Zig 0.16.0 (pinned); any C toolchain that can link the static library for C/C++ hosts |
| **Platforms** | macOS aarch64, Linux x86_64, Linux aarch64 (cross-built, not release-gated), Windows x86_64 (MSVC ABI); JIT on arm64 and x86_64 only |
| **Thread safety** | Not documented in general; Instance.interrupt() is documented as callable from another thread to stop a running guest. |
| **Drop-in for the baseline** | partial: hosts written against the standard wasm-c-api (wasm.h) can relink against libzwasm, and the CLI follows 'wasmtime run' usage, but WASI setup uses zwasm's own wasi.h and there is no wasmtime Rust-API compatibility |

## Gotchas

- The memory claim '4-12x less, uniform across the WASI guests' holds only for the AOT row on fib and tak; derived from the same table, tinygo/sieve is 2.4-6.9x for AOT, and the JIT (the default engine) ranges 1.9-8.9x across fixtures.
- Harness detail: every row times a whole process with hyperfine --shell=none on guests with about 8 KB of code, so the startup table measures process start plus engine init; the zwasm-aot row runs a precompiled .cwasm while wasmtime is run without a cache flag (its CLI cache defaults to off, per search snippets of the wasmtime docs), so compare zwasm-jit (2.2-2.6x faster than wasmtime) for a like-for-like cold start.
- Metering defaults differ by surface: the Zig API instantiates with finite fuel and memory budgets, but a C API instance starts unmetered (per a 2026-09-29 docs commit), so set the zwasm_instance_\* limits explicitly for untrusted code.
- Building with -Dengine=interp did not remove the JIT from libzwasm.a in v2.7.0 (the independent harness patched it out: 17.6 MB to 5.1 MB); v2 is Apache-2.0 with no ABI compatibility with the MIT-licensed v1 line.

## Known shortcomings

- Wins on startup time and RSS only (docs/benchmarks.md, Zig 0.16.0); wasmtime is 1.5-13.7x faster on sustained compute and the zwasm interpreter is 8.47x off the fastest interpreter in the rebeckerspecialties/wasm-benchmark harness. Zig, not C++.
- Enricher: the docs' '4-12x less RSS, uniform' is overstated (the same table gives sieve AOT 2.4-6.9x and JIT 1.9-8.9x), the AOT row runs a precompiled .cwasm while wasmtime runs uncached (its CLI cache defaults off), and like-for-like cold start has the JIT 2.2-2.6x faster than wasmtime. Open issues: #505 silent JIT miscompile across call_ref, #495 crash instead of trap on frames over 16 KiB, #500 QuickJS 70x slower than wasmtime, #499 C API recompiles the module per instance (35 MiB each); C API instances start unmetered.

## Caveats and trade-offs

The win is cold-start latency and memory footprint only. The same doc shows the optimizing JITs ahead on sustained compute: wasmtime/wasmer/wazero beat zwasm-jit/aot by about 1.5-3.9x (shootout/fib2 zwasm-jit 1077 ms vs wasmtime 700 ms; matrix 343 vs 88 ms; base64 781 vs 57 ms, about 13.7x). The startup rows time a whole process (spawn + instantiate + run) on sub-10 ms guests, so they measure startup, not execution; the zwasm-aot row excludes its one-off compile step while comparator rows include their JIT compile, and the doc does not say whether wasmtime/wasmer compilation caches were on. Single host (Apple M4 Pro, macOS); wasmer only on aarch64-darwin. The independent harness at rebeckerspecialties/wasm-benchmark (docs/runtime-comparison-2026-09-22.md, zwasm v2.7.0 with the JIT compiled out) puts zwasm's interpreter at a geomean 8.47x the fastest runtime's CPU time on M4 Max E-cores (wasm3 1.01, WAMR 1.63, WasmEdge 8.42). A fork's README (andypeng2015/zwasm) says the 'majority match or beat wasmtime' on 29 benchmarks, which the canonical benchmarks doc does not support. github.com/clojurewasm/zwasm (used by the rebecker harness) appears to be the project's earlier home. v1 line (frozen at v1.11.1) is MIT; v2 is Apache-2.0. Embeddable from C/C++ via the standard wasm-c-api.

Single-pass JIT, interpreter and AOT backends with Wasm 3.0 and WASI 0.2/0.3; small footprint and fast startup traded for peak throughput.

## Maintenance

Very active (v2.7.0 released 2026-09-13, commits through 2026-10-05) and Apache-2.0, but among its 60 open issues, reports filed on 2026-10-01 include silent JIT miscompilation (#505) and a crash-instead-of-trap (#495), so pin a release and prefer the interpreter or AOT path for untrusted guests until they close.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/benchmarks.md shows the startup and peak-RSS tables exactly as quoted against pinned wasmtime 43.0.1, wazero 1.11.0, wasmer 5.0.4 and WasmEdge 0.16.1; the harness is public (scripts/run_bench.sh with hyperfine 5 runs + 3 warmup, fixtures under bench/runners, comparators pinned in flake.nix devShells.bench), zwasm is built with Zig 0.16.0 (pinned in flake.nix) at -Doptimize=ReleaseFast, and the host is an Apple M4 Pro.
- **Verifier notes:** Numbers match docs/benchmarks.md exactly; repo 186 stars, Apache-2.0, not a fork, last commit 2026-10-05. Shortcoming: only startup and RSS wins; 1.5-13.7x slower than wasmtime on sustained compute, and the interpreter is about 8.5x off the fastest interpreter in an independent harness.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/zwasm/zwasm/blob/main/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/scripts/run_bench.sh>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/bench/README.md>
  - <https://github.com/zwasm/zwasm>
  - <https://github.com/zwasm/zwasm/commits/main>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md>
  - <https://raw.githubusercontent.com/andypeng2015/zwasm/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/zwasm/zwasm>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/scripts/run_bench.sh>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/bench/results/aot_coldstart.md>
  - <https://github.com/zwasm/zwasm/tree/main/bench/runners>
  - <https://github.com/zwasm/zwasm/tree/main/bench/runners/wasm/tinygo>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/bench/runners/wasm/tinygo/fib.wasm>
  - <https://raw.githubusercontent.com/zwasm/zwasm/HEAD/bench/runners/wasm/tinygo/sieve.wasm>
  - <https://github.com/zwasm/zwasm/issues>
  - <https://github.com/zwasm/zwasm/issues/500>
  - <https://github.com/zwasm/zwasm/issues/505>
  - <https://github.com/zwasm/zwasm/issues/495>
  - <https://github.com/zwasm/zwasm/issues/499>
  - <https://github.com/zwasm/zwasm/commits/main>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md>
  - https://docs.wasmtime.dev/cli-options.html (search snippet only)
  - https://github.com/cataggar/ghr/issues/143 (search snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/zwasm/zwasm`) · [data/wave12/enrich/raw/github_com_zwasm_zwasm.json](../../../data/wave12/enrich/raw/github_com_zwasm_zwasm.json) (enrichment confidence 0.7)

</details>
