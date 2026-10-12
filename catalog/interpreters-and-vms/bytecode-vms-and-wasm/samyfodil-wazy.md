# wazy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Pure-Go WebAssembly runtime hard-forked from wazero; about 1.3x faster compiled codegen on a 6.5 MB module, up to 9x on instantiate and interruptible loops.

| | |
|---|---|
| **Beats** | wazero (the Go runtime it descends from; the repo's three-way benchmark arms against wasmtime-go exist but the README states no wasmtime numbers) |
| **Claimed result** | README (Apple M4 unless noted): Instantiate 9.1x (1.724 us vs 15.74 us, 37 KB TinyGo module). Interruptible loops with WithCloseOnContextDone 9.8x vs wazero@main (docs/performance.md: 160 us vs 2074 us on a 100k-iteration loop, fibonacci 6.56 ms vs 76.0 ms, i9-12900HK). memory.fill 1.68x geomean (7.1x at 15 bytes, parity at 64 KiB). Compiled execution: string_manipulation -18%, reverse_array -14%, base64 -12%, fibonacci a wash. Host calls a tie (47.8 ns vs 48.3 ns). Cumulative geomean -17.8% time and -22.9% B/op across internal/integration_test/bench vs the wazero fork point. docs/performance.md adds BenchmarkConstAddrLoads 1.62 us vs 5.10 us (about 3.1x). 6.5 MB Rust module (go-anydoc) vs wazero v1.12.0: 4.9x compiled and 1.7x interpreted on a 5 MB docx body; the README says most of the 4.9x is the cost of WithCloseOnContextDone on wazero and about 1.3x remains with the option off (M5 Pro run). go-anydoc's own README: about 1.8x faster than wazero v1.12.0 interpreted, with 59 vs 40.5 million allocations on a 7.6 MB PDF. |
| **Workload** | benchmarks/vs-wazero in the repo: instantiate a 37 KB TinyGo module, host calls, compile, compiled and interpreted execution kernels, memory.fill and interruptible loops, run against a pinned wazero; plus a 6.5 MB Rust document-converter module (go-anydoc) run as a single instantiate. |
| **Metric** | latency |
| **Hardware** | Apple M4 (native arm64) for the head-to-head and cumulative numbers; core-pinned Intel i9-12900HK for memory.grow and interruptible-loop numbers; a third-party run on Apple M5 Pro (18-core), macOS 26.5 |
| **Compiler and flags** | Go 1.26 (Go 1.26.1 on the go-anydoc third-party run, CGO_ENABLED=0); benchstat over interleaved A/B runs with upstream wazero as a control; commands: cd benchmarks/vs-wazero && go test -run='^\$' -bench=. -benchmem -count=10. That module links wasmtime-go v34 and therefore needs cgo for every arm (docs/performance.md), so the head-to-head was not a CGO_ENABLED=0 build. The wazero pin is ambiguous: the benchmark README says fork point c0f3a4ec6411, docs/performance.md says f4779551afb4, and go.mod pins v1.12.1-0.20260904184217-6edbb8c01a5f; some figures were taken against wazero@main or wazero HEAD. |
| **Adoption** | 44 stars, 7 forks |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/samyfodil/wazy) · [benchmark](https://github.com/samyfodil/wazy) |

## Verdict

In-repo benchstat runs on an Apple M4 (Go 1.26, interleaved A/B, upstream wazero as control) give Instantiate 1.724 us vs 15.74 us and a host-call tie. A core-pinned i9-12900HK gives 160 us vs 2074 us on a 100k-iteration loop with close-on-context-done. A third-party go-anydoc run (Apple M5 Pro, Go 1.26.1, CGO_ENABLED=0, wazy v0.3.0 vs wazero v1.12.0) found about 1.7-1.8x on the interpreter and 1.3x compiled with close-on-context-done off.

## Use it when

- Go services that must stay `CGO_ENABLED=0` and run third-party or Rust/C libraries compiled to Wasm.
- Guests that must be cancellable by context deadline: with `WithCloseOnContextDone` on, wazy costs 1.04x-1.28x over its own option-off build on go-anydoc, where wazero v1.12.0 costs 3.0x-6.4x.
- Many short-lived instances per request: Instantiate measured 1.724 us vs 15.74 us for wazero on a 37 KB TinyGo module (Apple M4), with the caveats under gotchas.
- Wasm Component Model, WASI 0.2 or WASI 0.3 async components from Go, which upstream wazero does not run.
- Memory-access-heavy compiled guests (string manipulation, array reversal, base64), where the README reports 12-18% less time than wazero.

## Skip it when

- When cgo is acceptable and raw throughput matters: Wasmtime (Cranelift) is about 2x faster on the 7.5 MB PDF run (0.37 s vs 0.75 s) and about 16% faster on fibonacci.
- Untrusted multi-tenant hosts on the tagged release v0.3.0 (2026-09-07): the pooled-memory isolation fixes (#74, #69) landed on main on 2026-09-20 with no tag since, and #75 (api.Memory access racing Module.Close can touch reclaimed storage) is still open.
- Teams that need a long-maintained runtime: wazy is a few months old with one author and 44 stars, while wazero is mature and widely deployed. go-anydoc's README says wazy 'makes no API-stability promise'; wazy's README says the API is stable.
- Pure-compute guests without close-on-context-done: fibonacci is a wash (2.849 ms vs 2.798 ms), host calls tie (47.8 ns vs 48.3 ns), and the codegen gap on the large module is about 1.3x.
- Compiling large modules in memory-tight processes: go-anydoc measured a cold compile of its 6.5 MB module at 1.2 s and 517 MB peak RSS; a compilation cache cuts warm loads to 6 ms and 37 MB.

## How it is fast

Interruptible execution (`WithCloseOnContextDone`) compiles to a decrement of a reserved register plus a predicted-not-taken branch at function entries and loop back-edges, where wazero makes a check every iteration. Bounds checks are elided for masked dynamic addresses, leaf functions skip the stack-overflow check, and `memory.fill` calls `memclrNoHeapPointers` for large zero fills. Instantiation recycles linear-memory buffers and wasm stacks through size-classed pools, sizes memory to what the module will grow to, and memoizes funcrefs in a dense table. On Intel parts with the JCC erratum, code is padded with NOPs to keep branches off 32-byte boundaries.

## Compared with alternatives

None of the catalogued wasm siblings (Wasmi, WAMR, wasm3, tinywasm, Fizzy, Silverfir-nano, PolkaVM and others) is a pure-Go runtime with an optimizing compiler. Pick wazy when the host is Go and cgo is ruled out. If you can link C or Rust, a Wasmtime-class JIT runs about 2x faster on large modules and an in-place interpreter like Wasmi starts faster.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys only (the benchmarks/vs-wazero module additionally links wasmtime-go v34 and needs cgo) |
| **Minimum toolchain** | Go 1.25 (go.mod floor; benchmarks run on Go 1.26) |
| **Platforms** | compiler on amd64 and arm64 (linux, darwin, windows tested every commit); interpreter on any Go target (BSDs, illumos, plan9, js/wasm, s390x, ppc64le, riscv64, 386); 32-bit hosts cap linear memory just under 2 GiB |
| **Thread safety** | Inherits wazero's model: api.Function Call is documented as not concurrent (OPTIMIZATIONS.md C10). Open issue #75: api.Memory reads and writes racing Module.Close are unsafe. |
| **Drop-in for the baseline** | partial: same API shape as wazero after changing the import path (go-anydoc ported with a one-line import change), but reflection-based WithFunc host registration is removed in favour of HostFuncN/HostProcN |

## Gotchas

- The 9.1x Instantiate figure was measured before the 2026-09-20 fixes ed4381b8 (#74: 'a fresh instance sees the previous tenant's write' through a recycled pooled memory) and 0f363441 (#69: Close racing api.Memory reads), both on the recycle path the benchmark loops through. The harness also skips `_start` (WithStartFunctions()) and closes each instance right away, so the pool always hits on a barely touched memory. Nothing has been re-measured since the fixes.
- The headline 9.8x (interruptible loops) and 4.9x (6.5 MB module, compiled) mostly measure what `WithCloseOnContextDone` costs wazero v1.12.0; with the option off, the 5 MB docx gap is 1.3x (0.14 s vs 0.11 s), and wazero's in-flight PRs #2529/#2530/#2533 bring its option cost to 1.01x-1.10x.
- The wazero baseline pin has moved three times: README says fork point c0f3a4ec6411, docs/performance.md says f4779551afb4, and benchmarks/vs-wazero/go.mod pins 6edbb8c01a5f; the interruptible and memory.fill rows were run against wazero@main or HEAD. The compiled-execution -18%/-14%/-12% rows have no recorded per-arm numbers (docs/performance.md says so).
- wazy emits no Spectre index clamping on heap or table accesses (Wasmtime clamps by default), and the vs-wazero benchmark module needs cgo because it links wasmtime-go, even for the wazero-only arms.

## Known shortcomings

- Independent go-anydoc bench (wazy v0.3.0 vs wazero v1.12.0, Go 1.26.1, M5 Pro) gives about 1.8x interpreted; the record's '4-18%, geomean 6%' was not on the page and was replaced with README values. docs/performance.md shows wazy about 16% behind Wasmtime on fibonacci and about 2x behind on a 6.5 MB module; the wazero pin is ambiguous (3 values), the 9.1x instantiate figure predates the 2026-09-20 memory-recycling isolation fixes (ed4381b8, 0f363441), and the vs-wazero module needs cgo. Go wazero fork; off-baseline.
- Enricher: the 9.1x instantiate figure was measured on the pooled-memory path before the 2026-09-20 isolation fixes ed4381b8 (#74, a fresh instance sees the previous tenant's write) and 0f363441 (#69), the harness skips _start and closes each instance immediately so the pool always hits, and the last tag v0.3.0 (2026-09-07) lacks those fixes; open #75 (api.Memory racing Module.Close touches reclaimed storage). The 4.9x/9.8x headlines are mostly WithCloseOnContextDone cost on wazero (codegen gap about 1.3x); Wasmtime Cranelift is about 2x faster; cold compile of a 6.5 MB module takes 1.2 s and 517 MB RSS (go-anydoc).

## Caveats and trade-offs

The baseline is wazero, not Wasmtime, Wasmer, WAMR or V8. docs/performance.md shows wazy behind Wasmtime Cranelift: about 16% behind on Case3/fibonacci, and 0.75 s vs 0.37 s (about 2x behind) on the 7.5 MB PDF run of the 6.5 MB module, where wazero took 3.4 s. It is ahead only on dynaddr (1.18x) and at parity on dispatch, and wazy omits the Spectre index clamping that Wasmtime does by default. The README itself says its largest figures (9.8x, 4.9x) come mostly from what WithCloseOnContextDone costs wazero, and that the raw code-generator gap is about 30% on the large module. The host-call and fibonacci results are ties. The README's Instantiate figure (9.1x, 3.3 KB heap per instance) comes from an engineering-log sweep on the pooled linear-memory path. On 2026-09-20 two correctness and isolation fixes landed on that path (commit ed4381b8 'stop recycling a memory a closed module can still reach', commit 0f363441 'stop racing api.Memory readers when a module closes'). The figure was not re-measured after them, and the wazero pin it ran against is not recorded. The project is a young single-author hard fork of wazero (not a GitHub fork) with 44 stars. [retier] Independent go-anydoc bench (wazy v0.3.0 vs wazero v1.12.0, Go 1.26.1, M5 Pro) gives about 1.8x interpreted, but the 4.9x/9.8x headlines are mostly WithCloseOnContextDone cost on wazero (codegen gap about 1.3x) and Wasmtime Cranelift is about 2x faster (docs/performance.md: about 16% behind on fibonacci, about 2x on a 6.5 MB module; cold compile 1.2 s and 517 MB RSS). The 9.1x instantiate figure was measured on the pooled-memory path before the 2026-09-20 isolation fixes ed4381b8 (#74) and 0f363441 (#69), with a harness that skips _start and closes each instance at once so the pool always hits; the last tag v0.3.0 lacks those fixes and #75 (api.Memory racing Module.Close) is open. The wazero pin is ambiguous (3 values) and the vs-wazero module needs cgo. Go wazero fork; off-baseline.

Pure Go, no CGO; has a compiled mode and an interpreter mode (the README benchmarks both and the CLI has an -interpreter flag); adds Component Model, WASI 0.2 and the WASI 0.3 async ABI that wazero lacks; the host-call win comes from deleting reflection-based registration (the API broke compatibility with wazero once). Not callable from C++ directly.

## Maintenance

Very active (seven tags from v0.1.0 on 2026-08-15 to v0.3.0 on 2026-09-07; main last committed 2026-09-20) and Apache-2.0. It is copyable but young and single-author: build from main rather than v0.3.0 for the pooled-memory isolation fixes, and watch the open #75 race before hosting untrusted tenants.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** The README head-to-head comes from public harness code (benchmarks/vs-wazero/bench_test.go, wazy_test.go, wazero_test.go, which I checked: both arms are configured the same) with Go 1.26 and the Apple M4 / i9-12900HK stated. The execution win is also reproduced by an independent user suite (xusenlin/go-anydoc bench_test.go: Go 1.26.1, CGO_ENABLED=0, Apple M5 Pro, wazy v0.3.0 vs wazero v1.12.0, about 1.8x interpreted). That pinned third-party run is what holds A; the in-repo figures have a baseline-pin problem (see notes).
- **Verifier notes:** The numbers are on the README, but 'compiled execution 4-18% (geomean about 6%)' is not on the page; I replaced it with the README values. The record's statement that no Wasmtime numbers are reported is wrong: docs/performance.md shows wazy behind Cranelift on fibonacci and on the large module. Two harness issues are worth recording as shortcomings. First, the wazero baseline pin moved three times and the docs disagree about it. Second, the Instantiate 9.1x figure predates the 2026-09-20 memory-recycling fixes on the path it measures, so treat it as C-level; A rests on the pinned go-anydoc run. The metadata checks out: Apache-2.0, 44 stars, 7 forks, last commit 2026-09-20.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/samyfodil/wazy>
  - <https://github.com/samyfodil/wazy/commits/main.atom>
  - <https://github.com/samyfodil/wazy/tree/main/benchmarks/vs-wazero>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/README.md>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/go.mod>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/OPTIMIZATIONS.md>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/benchmarks/vs-wazero/README.md>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/benchmarks/vs-wazero/go.mod>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/benchmarks/vs-wazero/bench_test.go>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/benchmarks/vs-wazero/wazy_test.go>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/benchmarks/vs-wazero/wazero_test.go>
  - <https://raw.githubusercontent.com/xusenlin/go-anydoc/HEAD/README.md>
  - <https://raw.githubusercontent.com/xusenlin/go-anydoc/HEAD/go.mod>
- **Sources the enricher read:**
  - <https://github.com/samyfodil/wazy>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/README.md>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/OPTIMIZATIONS.md>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/go.mod>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/benchmarks/vs-wazero/README.md>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/benchmarks/vs-wazero/go.mod>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/benchmarks/vs-wazero/bench_test.go>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/benchmarks/vs-wazero/wazy_test.go>
  - <https://raw.githubusercontent.com/samyfodil/wazy/HEAD/benchmarks/vs-wazero/wazero_test.go>
  - <https://github.com/samyfodil/wazy/commits/main.atom>
  - <https://github.com/samyfodil/wazy/commit/ed4381b8>
  - <https://github.com/samyfodil/wazy/tags>
  - <https://github.com/samyfodil/wazy/issues?q=is%3Aissue>
  - <https://github.com/samyfodil/wazy/issues/75>
  - <https://raw.githubusercontent.com/xusenlin/go-anydoc/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/samyfodil/wazy`) · [data/wave12/enrich/raw/github_com_samyfodil_wazy.json](../../../data/wave12/enrich/raw/github_com_samyfodil_wazy.json) (enrichment confidence 0.75)

</details>
