# Paserati

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Pure-Go TypeScript/JavaScript bytecode interpreter, about 1.2-1.7x faster than goja on V8 v7; native QuickJS is about 3x faster.

| | |
|---|---|
| **Beats** | goja (dop251/goja, pure-Go JavaScript engine) and QuickJS ports usable from Go: QJS (fastschema/qjs, QuickJS compiled to WebAssembly) and ModerncQuickJS (ccgo-translated QuickJS) in the third-party shootout; the README's own hyperfine table uses a 'qjs' QuickJS runner binary of unstated origin. Neither native QuickJS nor V8 is measured. |
| **Claimed result** | Third-party shootout (Apple M5 Max, Go 1.27.0): V8 v7 score Paserati 1125 vs goja 751, ModerncQuickJS 787, QJS 761 (about 1.5x goja, derived from page data), duration 36.567 s vs 51.188 s, 48.447 s, 52.086 s; factorial average 515.824 ms vs goja 703.527 ms (1.36x, derived from page data), ModerncQuickJS 653.106 ms, QJS 592.033 ms. GoQuickJS, a pure-Go QuickJS-NG port, is far faster than Paserati (score 3912, factorial 213.392 ms; Paserati is 2.42x slower on factorial). README hyperfine: bench/bench.js 3.924 s vs goja 5.207 s (1.33x) vs QJS 4.945 s (1.26x); bench/objects.js 6.169 s vs goja 7.015 s (1.14x) vs QJS 8.135 s (1.32x). |
| **Workload** | Third-party shootout: V8 v7 suite (Richards, DeltaBlue, Crypto, RayTrace, EarleyBoyer, RegExp, Splay, NavierStokes; one full run per engine) and recursive factorial(10) one million times (5 runs, alternating order). README: bench/bench.js (xorshift arithmetic and array microbenchmark) and bench/objects.js (object/inline-cache microbenchmark) timed with hyperfine via bench/hyperfine.sh (warmup 3, at least 20 runs). |
| **Metric** | throughput |
| **Hardware** | Apple M5 Max, 128 GiB RAM, macOS ARM64 (third-party shootout, results collected 2026-10-05); README hyperfine hardware not stated |
| **Compiler and flags** | Third-party shootout: Go 1.27.0, go run . with default flags, Paserati type checking disabled. README hyperfine run: Go version and build flags not stated; paserati invoked with --no-typecheck. |
| **Adoption** | 26 stars, 1,519 commits |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/nooga/paserati) · [benchmark](https://github.com/go-quickjs/go-js-engines-benchmark) |

## Verdict

In go-quickjs/go-js-engines-benchmark (Apple M5 Max, Go 1.27.0, Paserati v0.9.13 with type checking off, one V8 v7 run per engine in one process) it scored 1125 vs goja 751 and ran recursive factorial(10) x1M in 515.8 ms vs 703.5 ms; ahaoboy's independent V8 v7 runs give 401/538/379 vs goja 264/436/218 on Ubuntu/macOS/Windows. The README's hyperfine microbenchmarks (1.33x and 1.14x over goja) state no hardware or Go version.

## Use it when

- Go services that must embed JavaScript or TypeScript without cgo or a Wasm runtime and currently use goja: independent V8 v7 scores are 1.52x goja on Ubuntu, 1.23x on macOS arm64 and 1.74x on Windows (ahaoboy/js-engine-benchmark, both at the same versions).
- Running TypeScript source directly (no tsc step), including runtime type reflection via Paserati.reflect&lt;T&gt;() for JSON Schema generation.
- Compute- and string-heavy scripts (Crypto, RegExp, NavierStokes, Splay rows) where its lead over goja is largest.
- Experiments and tools where a young, fast-moving engine is acceptable.

## Skip it when

- When speed matters more than staying in pure Go: C QuickJS scores 3.0x (Ubuntu), 3.3x (macOS) and 2.8x (Windows) higher on V8 v7, and the project's audit puts it at 2.98x C QuickJS's and 4.97x jitless V8's execution time.
- When another pure-Go engine is acceptable: GoQuickJS (go-quickjs/go-quickjs) scored 3912 vs 1125 and ran factorial 2.42x faster in the go-js-engines-benchmark shootout, and goant scored 981 vs 401 on ahaoboy's Ubuntu run.
- Call- and property-heavy object code: it is level with or slower than goja on Richards (all three ahaoboy platforms) and DeltaBlue (Ubuntu, macOS); the audit measured Richards 11.4 ms vs goja 10.5 ms.
- Production embedding with untrusted or long-lived workloads: the roadmap (2026-09-05) records retained memory after Reset (78.6 MB in a probe), about 34 MB kept by global shape transitions, a 24 MiB eagerly reserved register stack, and calls itself not production-ready.
- Memory-constrained hosts: the static binary is about 14-16 MB, against about 1 MB for C QuickJS.

## How it is fast

Register-based bytecode compiled directly from the TypeScript AST, hidden-class shapes with per-site property inline caches, indexed globals, cheap ordinary call frames and tail-call optimization. There is no JIT and no compact value encoding yet: the audited build used 24-byte Values, and the project's September 2026 audit found property get at about 36% of CPU (IC lookup about 12%) on its object benchmark.

## Compared with alternatives

Among catalogued siblings it is the JavaScript analogue of Wangshu (a pure-Go Lua beating gopher-lua): pick it when a Go program needs JS/TS without cgo and goja is too slow; pick katsu, lo or a V8-based runtime when you can leave Go, since all are an order of magnitude faster.

## Integration

| | |
|---|---|
| **Form** | module (Go module github.com/nooga/paserati) plus a CLI binary |
| **Dependencies** | github.com/dlclark/regexp2, golang.org/x/text, github.com/rivo/uniseg, golang.org/x/perf (go.mod; the README says two) |
| **Minimum toolchain** | Go 1.27.1 (go.mod at HEAD); the shootout built v0.9.13 with Go 1.27.0 |
| **Platforms** | any Go target, no cgo; benchmarked on linux/amd64, darwin/arm64 and windows |
| **Thread safety** | not documented; the roadmap asks for a single-owner policy per VM and found a data race between independent register allocators on a global diagnostic ID, so use one VM per goroutine |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the README's 'QJS' column (1.26x and 1.32x 'faster than quickjs') was, per the project's own roadmap, the modernc.org/quickjs ccgo translation, not C QuickJS; bench/hyperfine.sh also sends all output, including each engine's checksum, to /dev/null, so results are never compared. Against C QuickJS the same bench.js takes 2.371 s vs 0.810 s.
- Every published third-party number (go-js-engines-benchmark and ahaoboy) measured v0.9.13 (tagged 2026-08-25), which predates fixes for a property-IC bug returning a stale ancestor value after a closer prototype gained the property (#550), a switch-case TDZ stale read (#552) and array-iterator bugs (#551), all closed 2026-09-23; the V8 v7 checks passed, but the fixed IC sits on the measured hot path and post-fix speed is not published.
- The project's earlier Test262 runner counted some failures as passes (audit item A01); figures before September 2026, including 98.1%, are inflated, and the TypeScript conformance is only 41.7% by strict error codes.
- Benchmarks run with type checking off (--no-typecheck or SetSkipTypeCheck(true)); with checking on, the TypeScript checker's cost is added to startup.

## Known shortcomings

- Tier A rests on the third-party go-quickjs/go-js-engines-benchmark (public code, Go 1.27.0, go run ., Apple M5 Max): V8v7 score 1125 vs goja 751 and modernc QuickJS 761, but GoQuickJS is 3.5x faster than Paserati in the same table and there is no V8 or native QuickJS baseline.
- Enricher: the project's own roadmap says the README's 'qjs' column was modernc.org/quickjs (the ccgo translation), not C QuickJS; against C QuickJS Paserati is about 2.98x slower (audit) and scores 2.8-3.3x lower (ahaoboy). hyperfine.sh sends the checksums to /dev/null, so results are never compared. Every third-party number measured v0.9.13 (2026-08-25), before fixes closed 2026-09-23 (property inline cache stale ancestor value #550, switch TDZ #552, array iterator #551); the fixed inline cache is on the measured hot path. Roadmap notes memory retention after Reset, a 24 MiB stack reserve, an allocator data race and not production-ready. Independent ahaoboy/js-engine-benchmark V8 v7 scores 401/538/379 vs goja 264/436/218 (Ubuntu/macOS/Windows).

## Caveats and trade-offs

Beats goja and the Wasm/ccgo QuickJS builds, but not the fastest Go JavaScript engine: GoQuickJS scores 3.5x higher on V8 v7 and is 2.4x faster on factorial in the same third-party shootout; native QuickJS and V8 (the category baseline) are not measured. The shootout is maintained by the go-quickjs organization (a competing engine), forked from ngocphuongnb/go-js-engines-benchmark, has 0 stars, and runs the V8 suite once per engine; it tested Paserati v0.9.13 with type checking disabled. The README's own numbers are two first-party microbenchmarks with no hardware or Go version, run with --no-typecheck, and the identity of its 'qjs' binary is unstated. The author says it prioritizes correctness over speed and that almost all code was written by AI models under direction. The V8-suite page linked from the README is on a blocked github.io site. [retier] Beats goja and the modernc.org/quickjs Go translation, not C QuickJS (about 2.98x slower than C QuickJS per the project's own audit) and no V8 or Node column. All third-party scores measured v0.9.13 before the 2026-09-23 fixes to the property inline cache (#550), switch TDZ (#552) and array iterator (#551); hyperfine.sh discards checksums so results were never compared. Roadmap: not production-ready, memory retention after Reset, allocator data race.

Experimental TypeScript runtime: parses and type-checks TypeScript, compiles directly to bytecode for a register VM with inline caches and shape-based objects, no JIT. README reports Test262 language 98.3% and built-ins 89.9%. The third-party go-js-engines-benchmark runs it with type checking disabled.

## Maintenance

Very active one-person project (commits daily, last 2026-10-06), MIT and pure Go so it is easy to vendor, but the author calls it experimental, most code is AI-written, the newest release tag (v0.9.13) is six weeks behind several correctness fixes, and its own roadmap says production readiness is not established.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgraded from C: the third-party go-quickjs/go-js-engines-benchmark harness (arewefastyet-v8v7/main.go with engines/paserati.go, plus factorial/) is public, pins Paserati v0.9.13, goja and fastschema/qjs v0.0.6 in go.mod, runs with go run . on Go 1.27.0, and names the CPU (Apple M5 Max). The README's own hyperfine table (bench/hyperfine.sh) alone would be C (no hardware or Go version).
- **Retiered** A to C: A to C under the later-fixed-bug rule (yuv2rgb and libjxl fjxl precedent): all third-party numbers (go-quickjs/go-js-engines-benchmark, ahaoboy) measured v0.9.13 of 2026-08-25, before the property inline cache fix #550 (stale ancestor value) closed 2026-09-23, and that cache is on the measured hot path; the README's qjs column was modernc.org/quickjs, not C QuickJS, and the harness discards checksums.
- **Verifier notes:** README numbers match exactly; a public third-party harness with Go version, run command and CPU supports the win over goja and QJS, so tier upgraded C to A. Shortcomings to record: far slower than GoQuickJS (pure-Go QuickJS-NG port), no V8 or native QuickJS baseline (off the category baselines; QuickJS is an embedded-scripting baseline), first-party README table lacks methodology, AI-written code. Could not verify the record's statement that the shootout author also wrote QJS; replaced with the fork lineage.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `compiler_and_flags`, `hardware`, `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** comparison against V8 or native QuickJS; re-run on a post-#550 release with results compared
- **Pages the verifier opened:**
  - <https://github.com/nooga/paserati>
  - <https://github.com/nooga/paserati/commits>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/README.md>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/bench/hyperfine.sh>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/bench/bench.js>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/bench/objects.js>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/LICENSE>
  - <https://github.com/go-quickjs/go-js-engines-benchmark>
  - <https://github.com/go-quickjs/go-js-engines-benchmark/tree/master/arewefastyet-v8v7>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/master/arewefastyet-v8v7/main.go>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/master/arewefastyet-v8v7/go.mod>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/master/arewefastyet-v8v7/engines/paserati.go>
- **Sources the enricher read:**
  - <https://github.com/nooga/paserati>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/README.md>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/bench/hyperfine.sh>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/bench/bench.js>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/bench/objects.js>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/go.mod>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/docs/runtime-production-roadmap.md>
  - <https://raw.githubusercontent.com/nooga/paserati/HEAD/pkg/driver/driver.go>
  - <https://github.com/nooga/paserati/commits>
  - <https://github.com/nooga/paserati/issues>
  - <https://github.com/nooga/paserati/issues?q=is%3Aissue%20state%3Aclosed%20roadmap>
  - <https://github.com/nooga/paserati/tags>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/HEAD/arewefastyet-v8v7/main.go>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/HEAD/arewefastyet-v8v7/go.mod>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/HEAD/arewefastyet-v8v7/engines/paserati.go>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/HEAD/arewefastyet-v8v7/engines/goja.go>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/HEAD/arewefastyet-v8v7/engines/engines.go>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/HEAD/arewefastyet-v8v7/v8-v7/run.js>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/HEAD/factorial/main.go>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/HEAD/factorial/go.mod>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/HEAD/factorial/engines/paserati.go>
  - <https://raw.githubusercontent.com/go-quickjs/go-js-engines-benchmark/HEAD/factorial/engines/goja.go>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/nooga/paserati`) · [data/wave12/enrich/raw/github_com_nooga_paserati.json](../../../data/wave12/enrich/raw/github_com_nooga_paserati.json) (enrichment confidence 0.78)

</details>
