# uGO

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟡 stale

> Pure-Go bytecode scripting VM for embedding in Go programs; ran fib(35) about 10% faster than Tengo and 1.5x faster than go-lua.

| | |
|---|---|
| **Beats** | Tengo, go-lua, GopherLua and goja (Go-embedded scripting engines); native Lua is faster than uGO in the same table |
| **Claimed result** | fib(35): uGO 1.984686 s vs Tengo 2.185415 s, go-lua 2.898563 s, GopherLua 3.211634 s, goja 3.326141 s, starlark-go 4.726492 s (Go 1.18). Native Lua 1.000147 s is about 2x faster than uGO; on fibt(35) uGO 1.261 ms is slower than Tengo 1.135 ms and go-lua 1.006 ms. |
| **Workload** | Recursive fib(35) and a tail-recursive fibt(35) in the author's ugobenchfib harness, one run per engine, results dated 2022-05-03 for uGO 0.2.0 release candidate. |
| **Metric** | throughput |
| **Hardware** | Apple M1 host, Parallels VM, Ubuntu 20.04 |
| **Compiler and flags** | Go 1.18 (also Go 1.17 tables); engines installed with default `go install` (Makefile setup), no flags; native Lua and Python versions unstated |
| **Adoption** | 125 stars |
| **Last commit** | 2025-05-10 |
| **Links** | [repository](https://github.com/ozanh/ugo) · [benchmark](https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/README.md) |

## Verdict

In the author's ugobenchfib harness (a fork of Tengo's tengobench), one wall-clock run per engine of a recursive fib(35) took 1.98 s for the uGO 0.2.0 release candidate against Tengo 2.19 s, go-lua 2.90 s, GopherLua 3.21 s and goja 3.33 s. That is about 1.10x, 1.46x, 1.62x and 1.68x (derived from page data). The run used Go 1.18 under Ubuntu 20.04 in a Parallels VM on an Apple M1, with process startup included. Native Lua (1.00 s) and Python 3 (1.64 s) were faster than uGO in the same table.

## Use it when

- A Go service needs user-supplied rules or conditions evaluated in-process without cgo; the author uses it in production for Sigma rule conditions.
- Call-heavy or arithmetic script code where you would otherwise pick Tengo: uGO's fib(35) was 1.98 s vs Tengo 2.19 s, go-lua 2.90 s, GopherLua 3.21 s and goja 3.33 s (Go 1.18).
- Scripts that need structured error handling (try/catch/finally with runtime errors as values) and a timeout or abort from another goroutine (VM.Abort is safe across goroutines).
- Cross-compiled or WebAssembly targets where a C interpreter cannot be linked (the project ships a WebAssembly playground).

## Skip it when

- When cgo is acceptable: native Lua ran the same fib(35) in 1.00 s, about 2x faster than uGO, and Go itself took 43 ms.
- When users already write Lua or JavaScript: GopherLua, go-lua and goja run an existing language, while uGO is a small one-author language with its own syntax.
- Deeply recursive scripts: the VM has a hard limit of 1,024 frames and 2,048 value slots per VM.
- When you need an actively developed engine: there was one commit (v0.5.0, 2025-05-10) after May 2023, and minor releases have broken the bytecode encoding (v0.4.0) and compiler options (v0.5.0).
- Simple expression evaluation (filters, predicates): Expr (expr-lang) is the better-measured choice in the catalogue at about 70 ns per evaluation.

## How it is fast

A switch-dispatched stack VM (vm.go loop) runs byte-encoded instructions over a fixed array of 2,048 value slots and 1,024 call frames inside the VM struct, so calls do not allocate frames. Binary operations go through a type switch on the common concrete types (Int, String, Float, Uint, Char, Bool) before falling back to the interface method, and equality has dedicated opcodes. Self-recursive tail calls reuse the current frame, and an AST optimizer does constant folding, constant propagation (v0.5.0) and compile-time evaluation of side-effect-free builtins. The 0.2.0 rewrite (issue #7) targeted interface allocations in binary operations, the main cost in the 0.1 line.

## Compared with alternatives

Pick uGO over Tengo when you want Tengo's model (Go-native, bytecode VM, no cgo) with try/catch error handling and slightly faster calls (about 10% on fib(35)). Tengo has the larger user base and is the safer default. Pick GopherLua or goja instead when script authors must write Lua or JavaScript.

## Integration

| | |
|---|---|
| **Form** | Go module (github.com/ozanh/ugo), pure Go, no cgo |
| **Dependencies** | none for the core package (it imports only its own parser, token and registry packages); the ugo REPL command adds github.com/peterh/liner |
| **Minimum toolchain** | Go 1.19 (go.mod and the v0.5.0 notes); the README still says Go 1.15 and above, which is out of date |
| **Platforms** | any Go target, including WebAssembly |
| **Thread safety** | One VM runs one script at a time (Run holds a mutex); Abort and Aborted are safe from other goroutines; Eval and Invoker are documented as not safe for concurrent use. Run separate VMs per goroutine. |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark harness flaws (ugobenchfib cmd/bench/main.go): each engine is timed once as a whole process with `_ = cmd.Run()`, so exit status and output are never checked and startup, parse and compile are included. The fibt(35) column makes only 35 calls (tail-recursive fib(n-1, b, a+b)), so its 0.46 to 6.3 ms values measure process startup, not interpreter speed. Use only the fib(35) column.
- The measured build is not reproducible: go.mod pins github.com/ozanh/ugo v0.1.2 and the Makefile runs `go install` without a version, yet the table reports a 0.2.0 release candidate. The numbers are from 2022-05-03 inside a Parallels VM on an Apple M1, and the engine has since changed through v0.5.0.
- From reading vm.go (not run): only frame depth is checked (ErrStackOverflow at 1,024 frames). The 2,048-slot value stack is not bounds-checked on push or call, so deep non-tail recursion can hit a Go index-out-of-range panic first. NewVM leaves recovery off (the README example never calls SetRecover), so that panic reaches the host goroutine. Call SetRecover(true) or recover in the caller when running untrusted scripts.
- parser/parser.go is a modified Go and Tengo parser that carries BSD-style (Go) and MIT (Tengo) notices besides the project's MIT licence. Keep those notices when vendoring.

## Known shortcomings

- Downgraded A to C: the harness times one whole-process run and ignores errors (cmd.Run() result discarded), go.mod pins ugo v0.1.2 while the table says 0.2.0-rc, the Lua version is unstated, and uGO loses to native Lua by 2x (beats only Go engines). Stale since 2025-05-10; Go.
- Enricher: fibt(35) is only 35 calls, so that whole column is process startup; the value stack has 2048 unchecked slots with only the 1024 frames checked, so deep recursion likely reaches the host as a Go index panic unless SetRecover(true) is set (read, not run); the README's 'Go 1.15+' is stale against go.mod's 1.19.

## Caveats and trade-offs

Not faster than the category baseline: native Lua runs fib(35) in 1.000147 s against uGO's 1.984686 s (about 2x faster), and on fibt(35) uGO (1.261 ms) is slower than Tengo (1.135 ms), go-lua (1.006 ms) and native Lua (463 us); the win is only over other Go-embedded engines (Tengo, go-lua, GopherLua, goja). Harness flaws: cmd/bench/main.go times one wall-clock run per engine of the whole process (startup, parse and compile included), ignores the exit status (`_ = cmd.Run()`) and never checks the printed result, so fibt rows in the 1 ms range are mostly process startup. go.mod pins github.com/ozanh/ugo v0.1.2 while the table reports uGO 0.2.0 release candidate, so the measured build is not reproducible from the repo. Run inside a Parallels VM on an Apple M1 host. Numbers date from 2022-05-03; the project is now at v0.5.0 (May 2025).

Bytecode stack VM in pure Go, inspired by Tengo (code includes Tengo's BSD-3-Clause/MIT parts), so no cgo; dynamic typing with Go interop. Roughly half the speed of native Lua on fib.

## Maintenance

Stale (v0.5.0 on 2025-05-10 is the only commit after May 2023; 193 commits, 125 stars, open issues are the author's own feature ideas), MIT-licensed pure Go with no core dependencies, so it is easy to vendor, but you would be maintaining a one-author language.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party harness (ozanh/ugobenchfib cmd/bench/main.go, code/) with Go 1.18 and an Apple M1 VM stated, but it falls short of A: each engine is timed once as a whole process with errors ignored (`_ = cmd.Run()`), go.mod pins ugo v0.1.2 while the table is for 0.2.0-rc (installed by unpinned `go install`), and the native Lua version is unstated.
- **Verifier notes:** Numbers in the record match the 2022-05-03 Go 1.18 table exactly. Downgraded A to C for the single-run, error-ignoring process-timing harness and the unpinned 0.2.0-rc build; it also loses to native Lua (category baseline), so it is a Go-ecosystem data point only. Metadata checked: MIT, 125 stars, last commit 2025-05-10 (v0.5.0), stale.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/README.md>
  - <https://github.com/ozanh/ugobenchfib>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/go.mod>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/cmd/bench/main.go>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/code/fib.ugo>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/code/fib.lua>
  - <https://github.com/ozanh/ugo>
  - <https://github.com/ozanh/ugo/commits>
  - <https://raw.githubusercontent.com/ozanh/ugo/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/ozanh/ugo>
  - <https://raw.githubusercontent.com/ozanh/ugo/HEAD/README.md>
  - <https://raw.githubusercontent.com/ozanh/ugo/HEAD/go.mod>
  - <https://raw.githubusercontent.com/ozanh/ugo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ozanh/ugo/HEAD/vm.go>
  - <https://raw.githubusercontent.com/ozanh/ugo/HEAD/optimizer.go>
  - <https://raw.githubusercontent.com/ozanh/ugo/HEAD/ugo.go>
  - <https://raw.githubusercontent.com/ozanh/ugo/HEAD/eval.go>
  - <https://raw.githubusercontent.com/ozanh/ugo/HEAD/docs/optimizer.md>
  - <https://raw.githubusercontent.com/ozanh/ugo/HEAD/cmd/ugo/main.go>
  - <https://raw.githubusercontent.com/ozanh/ugo/HEAD/parser/parser.go>
  - <https://github.com/ozanh/ugo/tree/main/parser>
  - <https://github.com/ozanh/ugo/commits/main>
  - <https://github.com/ozanh/ugo/releases>
  - <https://github.com/ozanh/ugo/releases/tag/v0.2.0>
  - <https://github.com/ozanh/ugo/issues?q=is%3Aissue>
  - <https://github.com/ozanh/ugo/issues/7>
  - <https://github.com/ozanh/ugo/issues/31>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/README.md>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/go.mod>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/cmd/bench/main.go>
  - <https://github.com/ozanh/ugobenchfib/tree/master/code>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/code/fib.ugo>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/code/fibtc.ugo>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/code/fib.tengo>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/code/fibtc.tengo>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/code/fib.lua>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/code/fibtc.lua>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/code/fib.js>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/code/fib.py>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/code/fibtc.py>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ozanh/ugo`) · [data/wave12/enrich/raw/github_com_ozanh_ugo.json](../../../data/wave12/enrich/raw/github_com_ozanh_ugo.json) (enrichment confidence 0.7)

</details>
