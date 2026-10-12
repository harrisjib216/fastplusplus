# wasmz

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig WebAssembly interpreter with a C API; roughly level with WAMR fast-interp and ahead of Wasmtime Pulley, behind wasm3.

| | |
|---|---|
| **Beats** | Wasmtime Pulley interpreter and WAMR fast interpreter |
| **Claimed result** | CPU time per call relative to the fastest runtime, geometric mean over 17 cases, N=10: Apple M4 Max E-cores wasmz 1.59 vs WAMR 1.63 and Pulley 2.09 (about 1.3x faster than Pulley, derived from page data); iPhone XS (A12) E-cores wasmz 1.63 vs Pulley 1.68 but WAMR 1.38. |
| **Workload** | Interpreter-only comparison of 7 runtimes on Apple Silicon E-cores: 17 shared cases, CPU time per call. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro Apple M4 Max (E-cores) and iPhone XS Max (Apple A12 Bionic, E-cores) |
| **Compiler and flags** | wasmz dev built with 'make release' (Zig ReleaseFast); wasm3 at submodule commit 79d412e built with cmake (its CMakeLists defaults to Release, -O3); WAMR at submodule commit 11eb206 built with cmake -DWAMR_BUILD_INTERP=1 -DWAMR_BUILD_AOT=0 -DWAMR_BUILD_FAST_JIT=0 -DWAMR_BUILD_JIT=0 -DWAMR_BUILD_SIMD=0; wasmi at commit 9f6ff82 built with cargo build --release -p wasmi_cli (all in bench/build.sh). Compiler versions (Zig, gcc, rustc) are not stated in the report. |
| **Adoption** | 83 stars |
| **Last commit** | 2026-08-17 |
| **Links** | [repository](https://github.com/Ray-D-Song/wasmz) · [benchmark](https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md) |

## Verdict

The independent rebeckerspecialties/wasm-benchmark run (2026-09-22; wasmz v0.1.4 static lib, Zig 0.16.0 ReleaseFast; C runtimes with Apple clang 21 -O3 -mcpu=apple-a12; N=10) gives CPU time per call relative to the per-case fastest runtime, geomean over 17 shared cases: M4 Max E-cores wasmz 1.59 vs WAMR fast-interp 1.63, Wasmtime Pulley 2.09, wasm3 1.01; iPhone XS (A12) E-cores 1.63 vs WAMR 1.38, Pulley 1.68, wasm3 1.04. The repo's own report (2026-04-16, Linux 6.17 Azure x86_64, CPU model not stated, hyperfine whole-process medians) shows fib(30) 37.0 ms vs wasmi 38.4, wasm3 v0.5.1 39.7, WAMR 49.6 and QuickJS fib(25) 174.9 ms vs 184.4/217.4/242.9.

## Use it when

- You need a pure interpreter (no executable memory, e.g. iOS/App Store or watchOS) that runs Wasm 3.0 modules using GC, memory64 or exception handling; in the independent harness it was the fastest runtime on the memory64, EH-parser and GC rows.
- Large modules where only part of the code runs: lazy per-function compilation makes start-up of a 19 MB module (esbuild) cheap compared with eager translators.
- Scalar MVP code where WAMR fast-interp is the alternative: the two are within a few percent on M4 E-cores (geomean 1.59 vs 1.63).
- Zig projects, or C/C++/Rust hosts that are fine with a small custom C API and are willing to supply their own host imports.

## Skip it when

- Peak interpreter speed on MVP code: wasm3 v0.9.0 was about 1.6x faster in the independent harness (geomean 1.01 vs 1.59 on M4 E-cores), and WAMR was faster on the A12 (1.38 vs 1.63).
- Untrusted modules: issue #8 (open) reports that spec-invalid modules (bad subtype hierarchies, wrong operand-stack types, wrong result arity) are accepted and run, and the August 2026 history includes silent miscompiles and out-of-bounds address bugs (#1, #2, #10, #12).
- Auto-vectorized (v128) code: v0.1.4 segfaulted on the SIMD builds of sieve and crc32, and extended-const initializers, catch_ref/throw_ref and expression-form elem segments gave wrong results or traps.
- Long-lived instances that allocate GC objects: GC structs are never collected while the instance lives (316 MB peak on gc_trees), despite the README's 'automatic memory management'.
- Multi-memory modules (rejected at compile) or C API callers that need multi-value results (the C API returns at most one value).

## How it is fast

Each function's stack bytecode is lowered to a register IR with 16-bit slot operands, then executed with direct threaded code: every encoded op carries an 8-byte handler pointer and each handler tail-calls the next, spreading branch prediction across dispatch sites. A wasm3-style accumulator pair (r0 for integers, fp0 for floats) keeps the last result in a hardware register, and a peephole pass fuses common patterns into superinstructions (const+binop, compare+branch, binop+local.set, local in-place update, call_leaf). Functions compile lazily on first call, the .wasm file is mmapped, and linear memory is a PROT_NONE reservation committed on memory.grow.

## Compared with alternatives

Pick wasm3 for the fastest MVP interpretation (about 1.6x faster here) and WAMR fast-interp for maturity and the A12-class cores; pick wasmz over them when you need GC, memory64 or both exception-handling flavours in an interpreter, where wasm3 has none and the WAMR build in that harness had no GC or memory64. Against Wasmi and Pulley it trades a smaller, simpler C-callable runtime for less validation and a younger codebase.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (C API via zig build clib / static-lib), Zig module, Rust crate bindings |
| **Dependencies** | none beyond the Zig standard library (a small refcount library, zigrc, is vendored under src/libs) |
| **Minimum toolchain** | Zig 0.16.0 (build.zig.zon minimum_zig_version) |
| **Platforms** | Linux, macOS, Windows release builds; x86-64 and aarch64 (full LTO on Linux for both), 32-bit targets fixed in June 2026; iOS and arm64_32 watchOS built by the independent harness (watchOS with a carried patch); can also compile itself to wasm32-wasi |
| **Thread safety** | Engine and Module refcounts are thread-safe and a compiled Module can be shared; Store and Instance are not thread-safe, so use one Store/Instance per thread (docs/src/c-api.md). |
| **Drop-in for the baseline** | partial — the CLI runs WASI command modules like wasmtime/iwasm, but the C API is a custom wasmz_\* API (not wasm-c-api) and does not expose WASI, so embedders of WAMR or Pulley must rewrite their host glue. |

## Gotchas

- First-party harness flaw: bench/bench.sh times whole processes with hyperfine and never checks program output; the QuickJS and esbuild RSS rows measure the 'sh -c' wrapper's PID (1.8 MB for every runtime), so those memory numbers are invalid; wasmz is built by Zig for the native CPU with full LTO while wasm3 (an old v0.5.1) and WAMR use generic cmake builds.
- The numbers in docs/src/bench.md (2026-04-16) predate the August 2026 miscompilation fixes ('keep operand-stack reads of a local independent of later writes', 'only rename a label slot onto the temporary that a branch consumes'), so they were measured on code later fixed for correctness bugs.
- WASI Preview 1 lives in the CLI and Zig API; the C API (wasmz.h) has no WASI entry points, so C/C++ hosts must register wasi_snapshot_preview1 imports themselves through wasmz_linker_define_func (host functions only landed in the C API on 2026-08-13).
- 'make build' (labelled recommended) is ReleaseSafe with -Dprofiling=true; the benchmarked configuration is 'make release' (ReleaseFast), which also drops Zig's runtime safety checks (a ReleaseFast-only fd_write bug was fixed in July 2026).

## Known shortcomings

- First-party docs/src/bench.md numbers without a CPU model, measured before the August 2026 miscompilation fixes. The independent rebeckerspecialties/wasm-benchmark harness puts wasmz at geomean 1.59 against wasm3 v0.9.0 at 1.01 and WAMR at 1.63 (M4 E-cores) with 6 failing rows, so the claimed win over wasm3 is unconfirmed; the QuickJS and esbuild RSS rows measure an sh wrapper.
- Enricher: bench/bench.sh does whole-process hyperfine timing with no output check, the QuickJS and esbuild RSS rows measure the sh -c wrapper PID (invalid), and wasmz was built for the native CPU (Zig default target) with full LTO against generic cmake builds of wasm3 v0.5.1 and WAMR. Open issue #8: no spec validation, so spec-invalid modules run; the GC never collects; the C API has no WASI; 'make build' defaults to ReleaseSafe plus profiling.

## Caveats and trade-offs

First-party numbers from a 2026-04-16 dev build; CPU model and compiler versions not stated. The wasm3 used is v0.5.1 (submodule commit 79d412e); the independent harness used v0.9.0. Timings are whole-process wall time via hyperfine, so start-up is included and wasmz's lazy (on first call) compilation favours it on the 19 MB esbuild module; WAMR is excluded from esbuild. The harness does not check program output. Many miscompilation fixes landed after the benchmark (August 2026 commits such as 'keep operand-stack reads of a local independent of later writes' and 'only rename a label slot onto the temporary that a branch consumes'), so the numbers were measured on code later fixed for correctness bugs. The QuickJS and esbuild memory rows measure the sh -c wrapper (1.8 MB for every runtime), so those RSS figures are invalid. The independent harness rebeckerspecialties/wasm-benchmark (docs/runtime-comparison-2026-09-22.md, wasmz v0.1.4) puts wasmz behind wasm3 (geomean 1.59 vs 1.01 on M4 Max E-cores). It is roughly level with WAMR fast-interp there (1.63) but behind it on iPhone XS A12 (1.63 vs 1.38), and ahead of wasmtime Pulley (2.09). The same harness reports six failing rows for wasmz: wrong results on extconst_init and extconst_init.mvp, traps on graphql_as and callref_dispatch, and segfaults on v128 ops in sieve and crc32. It also notes that wasmz never collects GC structs and does not support multi-memory or multi-value results through its C API. Treat the win over WAMR and wasm3 as unconfirmed. Zig library with a C API (libwasmz plus wasmz.h), so callable from C++.

Zig library with C API and Rust bindings; GC, SIMD, exceptions and threads claimed.

## Maintenance

Active single-author project (272 commits, last push 2026-08-17, Rust bindings just added), MIT and small enough to vendor, but at 0.1.x with an open spec-validation gap and six failing rows in the independent harness it is best treated as experimental for untrusted or SIMD-heavy modules.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now C.
- **Tier reason:** docs/src/bench.md (generated 2026-04-16 by the public bench/bench.sh and bench/build.sh, hyperfine 20 runs after 5 warmups) shows every claimed number against WAMR iwasm 2.4.3, wasm3 v0.5.1 and wasmi 2.0.0-beta.2, but it states no CPU model and no compiler versions, so it stays first-party tier C. The independent, fully specified harness rebeckerspecialties/wasm-benchmark (docs/runtime-comparison-2026-09-22.md, M4 Max E-cores, all build flags listed) does not confirm a win: wasmz geomean 1.59 vs wasm3 1.01 and WAMR 1.63 on M4 E-cores, and 1.63 vs WAMR 1.38 on iPhone XS (A12).
- **Verifier notes:** Claimed numbers match docs/src/bench.md exactly; README claim 'currently the fastest WebAssembly interpreter I have tested' confirmed verbatim. Metadata checked on github.com: MIT, 83 stars, not a fork, last commit 2026-08-17 (active). Shortcomings to record: first-party only with no CPU model; numbers predate August 2026 miscompilation fixes; an A-grade independent harness shows it 1.6x slower than wasm3 v0.9.0 and behind WAMR on A12, with 6 failing rows (wrong results, traps, crashes); RSS rows for QuickJS and esbuild measure the shell wrapper.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/docs/src/bench.md>
  - <https://github.com/Ray-D-Song/wasmz>
  - <https://github.com/Ray-D-Song/wasmz/commits>
  - <https://github.com/Ray-D-Song/wasmz/tree/main/bench>
  - <https://github.com/Ray-D-Song/wasmz/tree/main/bench/projects>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/README.md>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/bench/bench.sh>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/bench/build.sh>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/bench/deps.sh>
  - <https://raw.githubusercontent.com/wasm3/wasm3/79d412ea5fcf92f0efe658d52827a0e0a96ff442/CMakeLists.txt>
  - <https://github.com/rebeckerspecialties/wasm-benchmark>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md>
- **Sources the enricher read:**
  - <https://github.com/Ray-D-Song/wasmz>
  - <https://github.com/Ray-D-Song/wasmz/commits/main>
  - <https://github.com/Ray-D-Song/wasmz/issues?q=is%3Aissue>
  - <https://github.com/Ray-D-Song/wasmz/issues/12>
  - <https://github.com/Ray-D-Song/wasmz/issues/11>
  - <https://github.com/Ray-D-Song/wasmz/issues/8>
  - <https://github.com/Ray-D-Song/wasmz/tree/main/src>
  - <https://github.com/Ray-D-Song/wasmz/tree/main/src/vm>
  - <https://github.com/Ray-D-Song/wasmz/tree/main/src/vm/handlers>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/README.md>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/docs/src/bench.md>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/bench/bench.sh>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/bench/build.sh>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/build.zig>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/include/wasmz.h>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/docs/src/c-api.md>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/docs/src/wasi.md>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/src/main.zig>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/src/cli/args.zig>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/src/cli/run.zig>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/src/cli/runtime.zig>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/src/vm/dispatch.zig>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/src/vm/handlers/memory.zig>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/src/vm/handlers/common.zig>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/src/vm/handlers/simd.zig>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/src/vm/handlers/atomic.zig>
  - <https://raw.githubusercontent.com/Ray-D-Song/wasmz/HEAD/src/vm/handlers/accumulator.zig>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ray-d-song/wasmz`) · [data/wave12/enrich/raw/github_com_ray_d_song_wasmz.json](../../../data/wave12/enrich/raw/github_com_ray_d_song_wasmz.json) (enrichment confidence 0.75)

</details>
