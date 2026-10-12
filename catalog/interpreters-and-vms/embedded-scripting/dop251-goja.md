# goja

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Go` · `MIT` · 🟢 active

> Pure-Go ECMAScript 5.1+ bytecode engine; about 9x faster than otto on fib(35), far slower than V8.

| | |
|---|---|
| **Beats** | otto (pure-Go JavaScript interpreter) |
| **Claimed result** | goja README: 'it's 6-7 times faster than otto on average'. No workload, code or numbers are given; the linked issue #2 holds only a user's question asking for them. The independent Tengo README table (code in d5/tengobench) gives fib(35): goja 5,194 ms vs otto 48,539 ms, about 9.3x (derived from page data). It also gives fibt(35): goja 4 ms vs otto 6 ms. In the same table goja is slower than Tengo (2,315 ms), go-lua (4,028 ms) and GopherLua (4,409 ms), and native CPython 2 runs fib(35) in 1,907 ms. |
| **Workload** | Tengo table: recursive fib(35) and tail-call fibt(35), one run each, script read from file (tengobench code/ directory). The README's '6-7 times on average' has no stated workload. |
| **Metric** | throughput |
| **Compiler and flags** | tengobench go.mod: go 1.14 directive; goja v0.0.0-20200414142002-77e84ffb8c65, otto v0.0.0-20191219234010-c382bd3c16ff. The Go toolchain and flags used for the published table are not stated. |
| **Adoption** | 7.1k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/dop251/goja) · [benchmark](https://github.com/d5/tengo#benchmark) |

## Verdict

The one reproducible goja-vs-otto timing is the Tengo README table (d5/tengobench; goja build of 2020-04-14, otto of 2019-12-19, Go toolchain and hardware not stated), which times a single wall-clock run including process start: recursive fib(35) took 5,194 ms in goja vs 48,539 ms in otto, about 9.3x (derived from page data). The Expr author's comparison (Apple M2, goja 2023-08-12, otto v0.2.1) gives 146.2 vs 380.1 ns/op on one small boolean expression (about 2.6x); goja's own 'six to seven times' has no published data behind it.

## Use it when

- A Go service that must run user- or tenant-supplied JavaScript (rules, transforms, plugins) and has to cross-compile without cgo.
- Moving off otto: fib(35) about 9.3x faster in the Tengo table, and 2.6x faster (146.2 vs 380.1 ns/op) on a small boolean expression in the Expr author's comparison (both derived from page data).
- Running existing ES5/ES6 JavaScript (the README cites Babel and the TypeScript compiler) inside a Go process.
- Scripts that call into Go often with complex data structures, where the cgo crossing cost of a V8 binding would outweigh V8's faster execution (the README's own argument).
- Sandboxed execution that needs a kill switch: Runtime.Interrupt stops a running script and SetMaxCallStackSize caps call depth.

## Skip it when

- CPU-heavy JavaScript: the README says you are 'definitely better off with V8'; in the Tengo table goja's fib(35) (5,194 ms) is about 6.9x slower than PUC Lua (756 ms) and 2.7x slower than CPython 2 (1,907 ms) (derived from page data).
- When the scripts need not be JavaScript: Tengo (2,315 ms), go-lua (4,028 ms) and GopherLua (4,409 ms) beat goja on fib(35) in the same table, and uGO's own table also puts goja behind them.
- Small boolean or arithmetic rules over Go maps: Expr (70.27 ns/op) and cel-go (91.27 ns/op) beat goja (146.2 ns/op) in the Expr author's comparison.
- Untrusted source of unbounded size: issue #746 (opened 2026-09-30, still open, fix proposed in PR #749) shows about 300,000 nested parentheses kill the process with a fatal goroutine stack overflow that recover() cannot catch.
- Hot loops that call Go methods from JavaScript: issue #657 (open, no reply) measures about 20,000 ns/op for a JS loop calling strings.Builder.WriteString against about 500 ns/op in plain Go.

## How it is fast

Source is parsed and compiled once into a flat array of instructions, each a Go value with an exec(\*vm) method, run by a fetch-and-dispatch loop over a value stack; the Tengo table labels goja a VM and otto an interpreter. The compiler resolves variables at compile time to stack slots or indexed closure 'stash' slots, and only scopes reached by a direct eval() fall back to lookup by name. A compiled \*Program is independent of any runtime, so parsing and compiling can be skipped on reuse.

## Compared with alternatives

Pick goja over Tengo, uGO or GopherLua only when the scripts must be JavaScript or you need to run existing JS libraries. On fib(35), Tengo (2,315 vs 5,194 ms) and uGO (1.98 vs 3.33 s in its own table) are about 2.2x and 1.7x faster (derived from page data). For side-effect-free rules, Expr is about 2x faster than goja on the same boolean expression.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Pure Go, no cgo. go.mod requires github.com/dlclark/regexp2/v2, github.com/go-sourcemap/sourcemap, golang.org/x/text, github.com/google/pprof, github.com/Masterminds/semver/v3, github.com/goccy/go-yaml and github.com/dop251/goja_nodejs (goja_nodejs is used by the goja CLI; which others are test-only was not checked). |
| **Minimum toolchain** | Go 1.25 (README and go.mod) |
| **Platforms** | any Go target (pure Go, no cgo) |
| **Thread safety** | A Runtime may be used by only one goroutine at a time, and object values cannot be passed between runtimes; a compiled \*Program is runtime-independent and documented as safe to use concurrently. Interrupt is the cross-goroutine way to stop a run. |
| **Drop-in for the baseline** | partial — it covers the same pure-Go embedding use as otto, with similar Set/Get/Export ideas, but it is a different package and API (goja.New, RunString/RunProgram, AssertFunction, ExportTo), so call sites must be rewritten. |

## Gotchas

- Use one Runtime per goroutine (for example a pool) and share the compiled \*Program; sharing a Runtime across goroutines is unsupported.
- JSON.parse goes through Go's UTF-8 decoder, so lone UTF-16 surrogates become U+FFFD, and Date calendar-to-epoch conversion uses Go int, so overflowing arguments give wrong results (both listed in the README).
- There is no setTimeout, setInterval or event loop; the separate goja_nodejs project supplies require, console and an event loop.
- Harness flaw behind the independent numbers: tengobench's cmd/bench/main.go times one wall-clock run of each interpreter's CLI, including process start and compilation. It discards the error from cmd.Run() and never checks the result, so an interpreter that crashed would show a near-zero time. The fibt(35) script makes only 35 calls, so its 2-14 ms column (goja 4 ms vs otto 6 ms) measures process start, not tail calls.

## Known shortcomings

- Raised C to B on the independent Tengo README fib(35) table (d5/tengobench, goja pinned 2020-04-14, otto 2019-12-19): 5,194 ms vs otto 48,539 ms, about 9.3x (derived); goja's own '6-7x faster than otto' is unsupported. Beats no category baseline and is slower than GopherLua, go-lua and Tengo in the same table. Go; filed under embedded-scripting.
- Enricher: tengobench's cmd/bench/main.go does one wall-clock run per CLI including process start, drops errors ('_ = cmd.Run()') and never checks output, so a crashed interpreter would show near-zero time; fibt(35) is only 35 calls, so its 4 vs 6 ms column measures process start rather than tail calls; the fib(35) 9.3x over otto stands and the Expr comparison adds a second point (146.2 vs 380.1 ns/op, 2.6x). Open issue #746: deep nesting gives a fatal stack overflow that recover() cannot catch.

## Caveats and trade-offs

The README ratio has no workload, hardware or method. Issue goja#2, which the README links as 'some benchmarks', was opened on 2016-11-11 by a user (mbertschler) asking for the benchmark code and results. It is still open, with no maintainer reply and no numbers. The independent evidence is one 2020-era micro-benchmark (fib(35)) from a competitor's README, with no hardware and no repeated runs. The baseline otto is a slow tree-walking interpreter. goja does not beat V8, QuickJS or any engine in the category baseline list, and its own README says it is not a replacement for V8 or SpiderMonkey. The LICENSE is MIT, with copyrights for both Dmitry Panov and Robert Krimen (otto's author).

ECMAScript 5.1 plus most of ES6+ in pure Go with no cgo; the README states plainly it is not a replacement for V8 or SpiderMonkey and that cgo-based engines are faster for computation-heavy code.

## Maintenance

Actively maintained, with commits through 2026-10-06 and ES2025 iterator helpers merged 2026-10-02; MIT-licensed pure Go that needs Go 1.25, although the README's speed claim still has no data, since issue #2 has been open without a maintainer reply since 2016.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now B.
- **Tier reason:** goja's own README gives only an unsupported '6-7 times faster than otto' sentence, which on its own is tier C. The Tengo README benchmark table is an independent third-party measurement with public code (d5/tengobench, whose go.mod pins goja 2020-04-14 and otto 2019-12-19). It shows fib(35) goja 5,194 ms vs otto 48,539 ms, but it states no hardware or Go toolchain, so B, not A.
- **Verifier notes:** Upgraded C to B on the independent Tengo/tengobench fib(35) numbers. The record's caveat that 'the maintainer's comment holds only the same sentence' was wrong: issue #2 was a user's question that the maintainer never answered. Metadata checks out: MIT, 7.1k stars, last commit 2026-10-06, not archived. As a Go-embedded JS engine, the better-fitting category is wave 12's embedded-scripting. Fork maclof/goja-perf is a separate merged entry that benchmarks against upstream goja.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dop251/goja>
  - <https://github.com/dop251/goja/commits>
  - <https://github.com/dop251/goja/issues/2>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/README.md>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/LICENSE>
  - <https://github.com/d5/tengo>
  - <https://raw.githubusercontent.com/d5/tengo/HEAD/README.md>
  - <https://github.com/d5/tengobench>
  - <https://github.com/d5/tengobench/commits/master>
  - <https://github.com/d5/tengobench/blob/master/go.mod>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/dop251/goja>
  - <https://github.com/dop251/goja/commits>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/README.md>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/go.mod>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/goja/main.go>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/vm.go>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/compiler.go>
  - <https://raw.githubusercontent.com/dop251/goja/HEAD/runtime.go>
  - <https://github.com/dop251/goja/issues?q=is%3Aissue+performance>
  - <https://github.com/dop251/goja/issues/746>
  - <https://github.com/dop251/goja/issues/657>
  - <https://github.com/dop251/goja/issues/494>
  - <https://github.com/d5/tengobench>
  - <https://github.com/d5/tengobench/tree/master/code>
  - <https://github.com/d5/tengobench/tree/master/cmd>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/README.md>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/go.mod>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/cmd/bench/main.go>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/code/fib.js>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/code/fibtc.js>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/code/fibtc.otto>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/code/fib.tengo>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/code/fibtc.tengo>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/code/fib.lua>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/code/fibtc.lua>
  - <https://raw.githubusercontent.com/d5/tengobench/HEAD/code/fib.py>
  - <https://raw.githubusercontent.com/d5/tengo/HEAD/README.md>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/README.md>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/go.mod>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/goja_test.go>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/otto_test.go>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/dop251/goja`) · [data/wave12/enrich/raw/github_com_dop251_goja.json](../../../data/wave12/enrich/raw/github_com_dop251_goja.json) (enrichment confidence 0.75)

</details>
