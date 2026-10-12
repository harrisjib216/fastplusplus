# wasman

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly runtimes and compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Pure-Go, dependency-free WebAssembly MVP interpreter with an optional arm64/amd64 JIT; beats wazero's interpreter 1.1-1.8x on micro-loops.

| | |
|---|---|
| **Beats** | wazero v1.12 (interpreter mode and compiler mode); also wagon v0.4 and life |
| **Claimed result** | Interpreter vs wazero interpreter (Apple M3, ns/op): Fib 974,787 vs 1,787,663; Sum 3,014,618 vs 3,930,498; MemRW 4,751,546 vs 5,153,545; Instantiate 2,129 vs 14,100; README says 1.1-1.8x faster than wazero's interpreter, 1.5-2.4x faster than wagon, about 2x faster than life, instantiation 3-14x faster. JIT vs wazero compiler: MemRW 39,575 vs 70,643, Sort 367,952 vs 477,368, Sum 27,112 vs 26,850 (level), Fib 41,187 vs 37,832 (slower), Indirect 3,926,713 vs 2,812,512 (1.4x slower); on dual EPYC 7K62 Sum 2.0x and MemRW 1.6x ahead of wazero compiler, Fib 1.6x behind. |
| **Workload** | Go benchmarks over tiny hand-written .wat modules: Fib(20) recursive, 100k-iteration Sum loop, 64KiB MemRW, module Instantiate (decode+validate+instantiate), plus JIT-mode kernels Sort (10k i32 quicksort), Dispatch (br_table), Hash, Mandel, Indirect (call_indirect). |
| **Metric** | throughput |
| **Hardware** | Apple M3 (main tables); dual AMD EPYC 7K62 server for the amd64 JIT comparison |
| **Compiler and flags** | Go 1.24 (per bench/README.md); go test -bench . -benchmem ./bench with default Go flags; fixtures compiled from .wat with wat2wasm and checked in. bench/go.mod at HEAD declares go 1.25.0 and pins wazero v1.12.0, wagon v0.4.0 (via replace) and life at a 2019 commit. Every timed iteration checks the returned value against a constant. |
| **Adoption** | 11 stars |
| **Last commit** | 2026-08-19 |
| **Links** | [repository](https://github.com/c0mm4nd/wasman) · [benchmark](https://github.com/c0mm4nd/wasman/blob/master/bench/README.md) |

## Verdict

The author's go test -bench harness (Go 1.24 per the page, Apple M3, single runs, tiny .wat fixtures) measured wasman's interpreter 1.83x faster than wazero v1.12's interpreter on Fib(20), 1.30x on a 100k Sum loop and 1.08x on 64 KiB MemRW, with instantiation 6.6x faster where wazero's row includes Runtime setup and teardown. In JIT mode it beat wazero's compiler on MemRW (1.8x) and Sort (1.3x), tied on Sum and Dispatch, and trailed on Fib (9%), Hash (9%), Mandel (3%) and Indirect (1.4x).

## Use it when

- A Go service that must run small MVP Wasm modules (plugins, rules, smart-contract code) with no cgo and no third-party dependencies in the main module.
- Instantiate-heavy workloads such as one fresh instance per request: 2.1 us to decode, validate and instantiate the Fib module on an Apple M3, plus Reset to recycle instances.
- Deterministic metered execution: per-opcode TollStation gas with bit-identical trap points between interpreter and baseline JIT, plus u256.mul_div and u256.isqrt imports for DeFi-style arithmetic.
- Memory-bound kernels on linux or darwin with arm64/amd64 and EnableJIT, where it led wazero's compiler (MemRW 1.8x, Sort 1.3x on the M3).
- Environments that forbid executable memory, where the interpreter mode was 1.1-1.8x faster than wazero's interpreter on the author's loops.

## Skip it when

- Modules built for Wasm 2.0 or later: SIMD, threads, tail calls, exceptions, memory64 and the memory.init, data.drop and table.\* bulk-memory ops are not implemented (passive segments are parsed but not applied), and no WASI layer is documented.
- Call-heavy or call_indirect-heavy code under the JIT: wazero's compiler was 9% ahead on Fib and 1.4x ahead on Indirect on the M3, and 1.6x ahead on Fib on a dual EPYC 7K62.
- When you need to cancel runaway guest code with the JIT on: interrupts are only checked when native code returns to Go at a call site (see gotchas).
- Windows, FreeBSD or other OS/architecture pairs where you need native speed: the JIT is built only for (darwin or linux) and (arm64 or amd64); everything else runs the interpreter.
- Production use that needs a track record: 11 stars, no issues ever filed, a single maintainer, and the JIT plus several correctness fixes landed in a burst between 2026-08-14 and 2026-08-19.

## How it is fast

The interpreter pre-decodes each function body at load time into side tables (immediates, branch targets, block lookups), pools call frames, takes loop back-branches directly and dispatches trap-free hot opcodes through an inlined jump table, which brings Fib down to about 1 allocation per exported call against wazero-interp's 21,893. EnableJIT adds a tiered compiler: an optimizing tier with a virtual-register IR, linear-scan register allocation, compare/branch fusion, loop rotation and a native calling convention between compiled functions, and a baseline template tier for the rest (notably float code). Memory accesses keep an explicit address+offset+width check against the memory length (no guard pages).

## Compared with alternatives

The catalogued siblings (DTVM, KinoWASM, WasmKit, Cage on Wasmtime, VectorVisor) are C++, Rust or Swift engines that a Go program could only reach through cgo or a subprocess; pick wasman when a pure-Go, dependency-free embed matters more than peak speed or Wasm 2.0 coverage.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (the bench/ subdirectory is a separate Go module that pulls in wazero, wagon and life) |
| **Minimum toolchain** | Go 1.18 per go.mod (CI installs '^1.18', which resolves to the latest Go, so 1.18 itself is not exercised); the bench module declares go 1.25.0 |
| **Platforms** | any Go target for the interpreter; JIT only on linux and darwin for arm64 and amd64 (build tags in wasm/jit), with per-function interpreter fallback |
| **Thread safety** | An Instance is single-goroutine (source comment: no locking); Interrupt is safe to call from any goroutine; use one instance per goroutine or pool them with Reset. |
| **Drop-in for the baseline** | no |

## Gotchas

- With EnableJIT, Interrupt and CallExportedFuncWithContext are checked only when native code exits to Go at a call site (wasm/jit_native.go). The jit.Ctx ABI has no interrupt field, loop back-edges jump without a poll in both tiers, and the interrupt tests (instance_features_test.go) run the interpreter only. A call-free loop compiled by the JIT therefore probably cannot be cancelled, despite the README's 'interruption rails' claim; use a TollStation, which forces the inline-metered baseline tier.
- The '19220/19220, 0 skipped' conformance badge covers the WebAssembly 1.0 MVP suites plus memory_fill and memory_copy (the list in spectest/gen.sh), not the current full testsuite. Its generated testdata is not committed and CI installs no wabt, so CI skips the spec run; the badge is a local result.
- The JIT recompiles every function for each NewInstance (compiled code is owned by the instance; no shared compiled-module cache). It is switched off entirely by CanonicalizeNaNs or by a TollStation with non-uniform opcode prices, and any metering drops the optimizing tier, so metered JIT runs at baseline-tier speed.
- The benchmark harness is fair on correctness (every timed call checks its result) but its Instantiate row makes wazero create and close a whole Runtime per iteration, which inflates the 6.6x win. The tables are single runs that state Go 1.24 while bench/go.mod now requires Go 1.25. The repo root also carries wasman.test, a 4.7 MB darwin/arm64 Mach-O test binary, which is part of the module source.

## Known shortcomings

- bench/bench_test.go public (Go 1.24, Apple M3) but single runs with about 15% noise (Fib 974,787 vs 1,120,975 ns across two tables), larger than the 1.08x MemRW win; the wazero Instantiate row rebuilds the whole Runtime per iteration; the JIT comparison is mixed (behind on Fib, Hash, Mandel, Indirect 1.4x); README bolds Sum though wasman is 1% slower; Go-only; wazero is off the baseline list; shared ancestry with gasm/wazero.
- Enricher (code reading): with EnableJIT, Interrupt and context cancel are checked only at call sites that exit to Go, jit.Ctx has no interrupt field and loop back-edges in both tiers have no poll, so a call-free JIT loop probably cannot be cancelled despite the README's 'interruption rails'; the 19220/0/0 badge covers only the WebAssembly 1.0 MVP suites plus memory_fill and memory_copy and CI never generates the spec testdata; no SIMD, threads, table.\*, memory.init or WASI; the JIT recompiles every function per instance and CanonicalizeNaNs turns it off; the wazero Instantiate row rebuilds the Runtime each iteration; bench README says Go 1.24 but bench/go.mod needs 1.25; a 4.7 MB wasman.test Mach-O binary sits in the repo root.

## Caveats and trade-offs

Self-benchmarked by the author. Each row is a single run with no variance reported, and run-to-run noise is visible: the wasman interpreter's Fib reads 974,787 ns in the main table and 1,120,975 ns in the JIT table, 15% apart, which is larger than the 1.08x MemRW margin over wazero's interpreter. Workloads are very small (Fib(20) is about 13.5k calls). The Instantiate sub-benchmark for wazero creates and closes a whole wazero Runtime on every iteration (NewRuntimeWithConfig + Instantiate + Close, with no CompiledModule reuse), so the 6.6x instantiation win over wazero includes runtime setup and teardown that wasman's row does not pay. The README bolds wasman-jit on Sum even though its 27,112 ns is 1% slower than wazero-compiler's 26,850 ns. The EPYC 7K62 claims (Sum 2.0x, MemRW 1.6x ahead, Fib 1.6x behind) are ratios only, with no table. Only Go engines are compared: cgo runtimes (wasmtime-go, wasmer-go) are excluded, so there is no comparison with wasmtime, wasmer, V8 or WAMR. The JIT result is mixed: ahead of wazero's compiler on memory-bound code (MemRW 1.8x, Sort 1.3x), level on Sum and Dispatch, and behind on Fib (9%), Hash (9%), Mandel (3%) and Indirect (1.4x). LICENSE carries 'Copyright (c) 2020 @mathetake', the author of gasm, which became wazero, so wasman shares ancestry with its main baseline. Interpreter and JIT correctness fixes landed 2026-08-16 to 08-19, after the documented numbers (host-call resolution, toll return sentinel). None of them touches the benchmark workloads, which have no imports and no TollStation. Wazero is the Go incumbent but not one of the listed baselines.

Pure Go with zero dependencies (no cgo), interpreter by default; optional tiered JIT (EnableJIT) only on arm64 and amd64 and per-function interpreter fallback (optimizing tier covers about 86% of spec-suite function bodies). The README claims full official spec-suite conformance, metering and interruption support.

## Maintenance

Active (145 commits, last on 2026-08-19 after a five-day JIT and fix burst) and MIT-licensed pure Go, so copyable, but a one-maintainer project with 11 stars and no outside bug reports; LICENSE also credits @mathetake's gasm, the ancestor of wazero.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** bench/README.md tables match every number in the record. The harness is public (bench/bench_test.go): it runs wasman, wazero v1.12.0 (interpreter and compiler configs), wagon v0.4.0 and life through their public APIs, and checks the expected result on every iteration. The page states Go 1.24, the exact command `go test -bench . -benchmem ./bench` (default flags) and the CPU (Apple M3), which is everything tier A asks for.
- **Verifier notes:** The record is accurate; the README's ratios (1.1-1.8x vs wazero-interp, 1.5-2.4x vs wagon, about 2x vs life, 3-14x instantiate) all check out against the table values. Shortcomings to record: single runs with noise comparable to the smallest win, a wazero Instantiate row that rebuilds a Runtime per iteration, a mixed JIT result, a Go-only field, and an off-list baseline (wazero).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-17 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/c0mm4nd/wasman/blob/master/bench/README.md>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/bench/bench_test.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/bench/go.mod>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/README.md>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/CHANGELOG.md>
  - <https://github.com/c0mm4nd/wasman>
  - <https://github.com/c0mm4nd/wasman/tree/master/bench>
  - <https://github.com/c0mm4nd/wasman/commits/master>
  - <https://github.com/mathetake/gasm>
- **Sources the enricher read:**
  - <https://github.com/c0mm4nd/wasman>
  - <https://github.com/c0mm4nd/wasman/tree/master>
  - <https://github.com/c0mm4nd/wasman/commits/master>
  - <https://github.com/c0mm4nd/wasman/tree/master/wasm>
  - <https://github.com/c0mm4nd/wasman/tree/master/wasm/jit>
  - <https://github.com/c0mm4nd/wasman/issues?q=is%3Aissue>
  - <https://github.com/c0mm4nd/wasman/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/README.md>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/bench/bench_test.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/bench/go.mod>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/bench/testdata/fib.wat>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/bench/testdata/sum.wat>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/bench/testdata/memrw.wat>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/go.mod>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/spectest/README.md>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/spectest/gen.sh>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/instance.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/module.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/linker.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/instance.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/instance_exec.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/memory.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/jit_native.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/jit/mem_unix.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/jit/native_supported.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/jit/native_other.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/jit/stub_other.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/jit/ctx.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/jit/opt.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/jit/opt_arm64.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/jit/opt_arm64_ops.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/jit/opt_amd64_ops.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasm/jit/compile_arm64.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/jit_test.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/config_matrix_test.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/instance_features_test.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/instance_isolation_test.go>
  - <https://raw.githubusercontent.com/c0mm4nd/wasman/HEAD/wasman.test>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/c0mm4nd/wasman`) · [data/wave13/enrich/raw/github_com_c0mm4nd_wasman.json](../../../data/wave13/enrich/raw/github_com_c0mm4nd_wasman.json) (enrichment confidence 0.72)

</details>
