# goja-perf

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> API-compatible fork of the pure-Go goja JavaScript engine with quickening, loop traces and cheaper Go/JS calls; beats upstream goja.

| | |
|---|---|
| **Beats** | Upstream dop251/goja at merge base 8f1c069 (pure-Go JavaScript interpreter); V8 comparison suite exists but publishes no numbers |
| **Claimed result** | Over upstream goja (benchjs harness): MainLoop 24.541 ms to 98.277 us (249.71x) via a special-case lowering for the benchmark's empty global-counter loop; CallJS 2.86x, CallNative 2.07x, FuncCall 1.81x, CallReflect 1.39x. The VmNOP2 (1.96x) and MapDelete (1.48x) rows have no code change behind them (layout or noise artifacts; benchjs reports Goja CV 29-209% on that laptop). benchjs/README.md also shows V8 about 15x faster at steady-state geomean, with Goja runtime setup 25-60x cheaper. |
| **Workload** | 55 shared Go benchmarks from goja's suite, ten samples per version interleaved on Go 1.26.2, comparing fork commit 35cc441 with its upstream merge base; seven benchmarks improved significantly and none regressed significantly. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 PRO 7940HS, Windows/amd64 |
| **Compiler and flags** | Go 1.26.2; go test -run '^\$' -bench . -benchmem -count=10 (default Go build flags), ten samples per version interleaved and compared for significance; eligible integer loop traces compile to native code on Windows/amd64 and Linux/amd64, other platforms use a portable typed Go executor |
| **Adoption** | 2 stars (upstream goja has 7.1k) |
| **Last commit** | 2026-09-02 |
| **Links** | [repository](https://github.com/maclof/goja-perf) · [benchmark](https://github.com/maclof/goja-perf) |

## Verdict

Against its upstream merge base 8f1c069, on Go 1.26.2, Windows/amd64, AMD Ryzen 9 PRO 7940HS, ten interleaved samples per version: Go/JS call micro benchmarks improved 1.39x-2.86x with allocation drops, and an empty global counter loop improved 249.71x through a special-case lowering; 48 of 55 shared benchmarks did not change significantly, and two of the seven significant rows (VmNOP2, MapDelete) measure code the fork did not change. The benchjs suite (published in benchjs/README.md, contrary to the record) shows V8 13.6 about 15x faster on steady-state pure JS and Goja runtime creation 25-60x cheaper than a V8 context.

## Use it when

- Go services that embed goja for scripting and call JS from Go (or Go from JS) many times per request: CallJS 267 ns to 94 ns and CallNative 192 ns to 93 ns, with per-call allocations going to zero.
- Hosts that need a cheap, pure-Go, cgo-free JS runtime per tenant or request: the fork's benchjs suite measured fresh-runtime setup at 13-219 us versus 0.6-1.3 ms for a fresh V8 context.
- Running untrusted user scripts where you want a deny-by-default global allowlist, eval/Function blocking and a timeout without writing that plumbing yourself (still behind OS/container limits).
- Code bases already on upstream goja that can absorb an import-path change and want the boundary speedups without touching scripts.

## Skip it when

- Compute-heavy JavaScript: the fork's own benchjs results put V8 (Node 24.4, V8 13.6) about 15x faster at the steady-state geomean and 36-56x on a 20x20 matmul; use a V8 or QuickJS binding if cgo is acceptable.
- Projects that depend on goja_nodejs packages: the fork is a distinct module, so its \*goja.Runtime and upstream's are different Go types and only console/require/util are bundled as an internal copy.
- When you need upstream's latest fixes and ES2025 features: the fork's last commit is 2026-09-02, while upstream dop251/goja has since merged ES2025 Iterator helpers, a WeakMap reimplementation, async iterator support and several correctness fixes (sparse arrays, ToInt32, bound function length) the fork does not carry.
- Risk-averse production use: two-star single-maintainer fork, about a month old, developed by a coordinator/subagent AI workflow (AGENTS.md), with no issues filed yet.

## How it is fast

Adaptive quickening rewrites hot bytecode (cached global references, unboxed float fast paths for add, multiply and bitwise or) and loop back-edges are counted so hot integer loops lower to a typed trace IR run by a Go executor with range guards and deoptimisation. On Windows/amd64 and Linux/amd64 one trace shape (sum += i over an ascending, descending or constant-step counter) is emitted as x86-64 machine code into an mmap'd W^X region; a separate lowering keeps the empty global counter loop in a Go integer. Boundary paths drop primitive boxing, reuse VM stack storage and cache reflected method templates, which is where the 1.4x-2.9x call-benchmark gains and allocation drops come from.

## Compared with alternatives

Pick it over quickjs-jit (Longbridge QuickJS-NG with JIT), katsu or Graal.js when the host is a Go program that must stay cgo-free and mostly crosses the Go/JS boundary; pick one of those (or a V8 binding) when JS compute throughput matters, since V8 is about 15x faster than this fork on the fork's own pure-JS workloads.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | regexp2, go-sourcemap, golang.org/x/text, google/pprof, Masterminds/semver, goccy/go-yaml (same set as upstream goja) |
| **Minimum toolchain** | Go 1.25 (go.mod); numbers measured with Go 1.26.2 |
| **Platforms** | any Go platform; native-code traces only on windows/amd64 and linux/amd64 (needs mmap/mprotect PROT_EXEC or the Windows equivalent), typed Go executor elsewhere; Linux/386 CI-tested |
| **Thread safety** | Not goroutine-safe per Runtime (one goroutine at a time, as upstream); Sandbox serializes its own Run\* calls. |
| **Drop-in for the baseline** | partial — same API and package name, but the import path changes, upstream and fork Goja values are distinct Go types, and goja_nodejs needs an adapter |

## Gotchas

- Two of the seven 'significant' README rows have no code change behind them: BenchmarkVmNOP2 (1.96x) sets vm.prg to an empty Program, so halted() is true at pc 0 and the jump instruction never executes (the benchmark times only 'vm.pc = 0' plus halted(), whose source is identical in fork and upstream), and BenchmarkMapDelete (1.48x, same 480 B/op and 5 allocs) exercises orderedMap set/remove and asciiString hashing whose fork source matches upstream apart from the import path; both gains are layout or machine-noise artifacts, consistent with the fork's own benchjs note that Goja samples on this laptop had CV 29-209%.
- The 249.71x MainLoop row comes from global_counter_trace.go, a lowering that matches only an empty-body 'for (var i = 0; i &lt; CONSTANT; i++) {}' at global scope; it does not speed up loops that do any work.
- The native x86-64 trace backend accepts exactly one IR shape, an accumulator adding the loop counter (sum += i) with step 1, -1 or a constant step; every other loop stays in the typed Go executor or the interpreter.
- The interpreter dispatch loop now checks tier state on every instruction (vm.tier != nil && ...), and native traces need executable memory, so hardened environments that deny PROT_EXEC fall back silently to the Go executor.

## Known shortcomings

- The 249.71x MainLoop row comes from global_counter_trace.go, a lowering written for exactly the benchmark's empty global-counter loop (output still correct); the other wins are 1.4-2.9x over upstream goja. Go fork of goja; off the category baselines.
- Enricher: 2 of the 7 'significant' rows have no code change behind them (BenchmarkVmNOP2 at 1.96x sets an empty Program so halted() is true at pc 0 and the jump never runs, with halted() identical to upstream; MapDelete at 1.48x runs orderedMap and string-hash code matching upstream apart from import paths), so both are layout or noise artifacts (benchjs reports Goja CV 29-209% on that laptop); the native JIT handles only 'sum += i' loops. benchjs/README.md does publish V8 numbers: V8 about 15x faster at steady-state geomean, Goja runtime setup 25-60x cheaper. The fork stopped 2026-09-02 and lacks upstream September-October fixes.

## Caveats and trade-offs

The 249.71x headline is BenchmarkMainLoop (runtime_test.go), an empty 'for (var i=0; i&lt;100000; i++) {}' loop over a global variable, and global_counter_trace.go is a dedicated lowering for exactly that empty global integer counter loop shape: it keeps the counter in a Go integer (with a per-iteration interrupt check) and writes the property back on exit. The result is semantically correct and the loop still runs (about 1 ns per iteration), but the headline is a special case built for the benchmark's own shape and says little about general code. The other significant rows are 1.39x-2.86x (call boundary and VM dispatch micro benchmarks) and 48 of 55 shared benchmarks did not change significantly. Raw benchstat output is not published, only the summary table. The benchjs suite compares the same JS workloads with V8 but publishes no results; V8 would be far faster on compute. Independent fork with two stars and a separate module path (github.com/maclof/goja-perf), so its Goja values are distinct Go types from upstream's and goja_nodejs needs an adapter. Measured on one Windows laptop CPU. [retier] The 249.71x MainLoop row comes from global_counter_trace.go, written for exactly the benchmark's empty global-counter loop (output still correct), and the native JIT handles only 'sum += i' loops; VmNOP2 and MapDelete gains are artifacts (identical code to upstream apart from import paths). The fork stopped 2026-09-02 and lacks upstream September-October fixes. Go fork of goja; off the category baselines.

API-compatible fork that keeps the upstream package name and swaps the import path; adds adaptive quickening, typed traces with native code for supported numeric loop shapes, cheaper Go/JS boundary calls and an opt-in capability sandbox. Native traces cover only supported integer and float accumulation and counter loops.

## Maintenance

Released v0.2.2 on 2026-09-02 with no commits since and upstream fixes from September-October 2026 not merged; MIT-licensed, pure Go and copyable, but treat as an experimental single-maintainer fork.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** The README 'Measured performance' table carries every quoted number for fork commit 35cc441 against its upstream merge base 8f1c069, with Go 1.26.2, Windows/amd64 and the AMD Ryzen 9 PRO 7940HS named and the exact command given (go test -run '^\$' -bench . -benchmem -count=10). The benchmark code is public and shared with upstream (runtime_test.go BenchmarkMainLoop is byte-for-byte the same script in dop251/goja), so the comparison is reproducible.
- **Verifier notes:** Numbers match the README exactly and the MainLoop benchmark source is identical upstream, so the comparison is fair as measured; the shortcoming is that the 249.71x row comes from global_counter_trace.go, an optimization that matches only the empty global counter loop the benchmark uses. License MIT (Dmitry Panov / Robert Krimen text), 2 stars, last commit 2026-09-02 (v0.2.2), fork of dop251/goja (verified in wave 12 batch-59).
- **Fields the verifier corrected:** `baseline_in_list`, `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/README.md>
  - <https://github.com/maclof/goja-perf>
  - <https://github.com/maclof/goja-perf/commits>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/runtime_test.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/global_counter_trace.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/runtime_test.go>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/README.md>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/go.mod>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/global_counter_trace.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/runtime_test.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/SANDBOX.md>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/benchjs/README.md>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/native_trace_amd64.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/native_trace_memory_linux_amd64.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/native_trace_stub.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/native_trace_amd64_bench_test.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/vm.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/vm_test.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/map.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/builtin_map_test.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/string_ascii.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/value.go>
  - <https://raw.githubusercontent.com/maclof/goja-perf/HEAD/func.go>
  - <https://github.com/maclof/goja-perf>
  - <https://github.com/maclof/goja-perf/commits>
  - <https://github.com/maclof/goja-perf/issues>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/go.mod>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/vm.go>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/vm_test.go>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/map.go>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/builtin_map_test.go>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/string_ascii.go>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/value.go>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/func.go>
  - <https://github.com/dop251/goja/commits/master>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/maclof/goja-perf`) · [data/wave12/enrich/raw/github_com_maclof_goja_perf.json](../../../data/wave12/enrich/raw/github_com_maclof_goja_perf.json) (enrichment confidence 0.8)

</details>
