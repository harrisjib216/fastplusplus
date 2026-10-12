# GopherLua

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Pure-Go Lua 5.1 VM for embedding in Go programs; about Python-3.4 speed in 2016, now behind CPython.

| | |
|---|---|
| **Beats** | CPython 3.4.3 (also C Lua 5.1.4, go-lua, otto, anko) |
| **Claimed result** | 2016 wiki: fib(35) 5.40 s vs Python 3.4.3 5.84 s (8% margin, one run) and C Lua 1.71 s. Independent ozanh/ugobenchfib (2020 i5 and 2022 M1 with Go 1.18): CPython 3 1.9-2.0x faster (3.21 s vs 1.64 s) and go-lua faster (2.90 vs 3.21 s); the Tengo README has CPython 2 2.3x faster. The claim does not hold on current versions. |
| **Workload** | Recursive fib(35) (result 9,227,465) timed once per implementation. |
| **Metric** | throughput |
| **Hardware** | Windows 7 64-bit, 2 CPUs, 8 GB RAM (CPU model not stated) |
| **Compiler and flags** | Go 1.7; no flags stated; Lua 5.1.4 and Python 3.4.3 |
| **Adoption** | 7.0k stars |
| **Last commit** | 2026-04-01 |
| **Links** | [repository](https://github.com/yuin/gopher-lua) · [benchmark](https://github.com/yuin/gopher-lua/wiki/Benchmarks) |

## Verdict

The author's 2016 wiki times one recursive fib(35) run per implementation with `time` on Windows 7 64-bit (2 CPUs, 8 GB, CPU not named) and Go 1.7: GopherLua 5.40 s vs CPython 3.4.3 5.84 s (about 1.08x), Lua 5.1.4 1.71 s, go-lua 8.13 s, otto 173.32 s and anko 182.73 s. Independent fib(35) runs since then (ugobenchfib on Intel i5 with Go 1.15 and on Apple M1 with Go 1.18; Tengo's README) show native CPython 1.9-2.0x faster than GopherLua (Python 3, version not stated, in ugobenchfib) and 2.3x faster (Python 2, in Tengo's README).

## Use it when

- You need a Lua 5.1 scripting layer inside a Go binary with no cgo (cross-compiles cleanly, static builds).
- Config, rules or plugin scripts where host-call ergonomics, goroutine and channel integration, or context cancellation matter more than raw interpreter speed.
- Many short-lived or pooled LStates running the same script: compiled FunctionProto bytecode can be shared read-only across states.
- You want the largest Go-Lua ecosystem: about 7,000 stars plus companion modules (gopher-luar, gluamapper, gopher-json, gluahttp, gopher-lua-libs).

## Skip it when

- CPU-bound script hot loops: independent fib(35) runs put it 1.9-2.0x behind CPython 3 (ugobenchfib 2020 and 2022, version not stated) and 2.3x behind CPython 2 (Tengo README) and 3-6x behind C Lua.
- Speed among Go-hosted VMs: Shopify go-lua, goja, Tengo and uGO all beat it in ugobenchfib 2022 (GopherLua 3.21 s vs uGO 1.98 s, go-lua 2.90 s).
- Code that needs Lua 5.2+ semantics (integers, bitwise ops, _ENV), string.dump, package.loadlib, debug hooks or os.setlocale; none are supported.
- Sharing one LState across goroutines: it is not goroutine-safe, and the README recommends one LState per goroutine or a pool.
- Sandboxed untrusted scripts that need cheap timeouts: SetContext switches to a main loop that does a channel select on every instruction (README: 7.5 s vs 5.3 s on fib).

## How it is fast

It makes no special performance claim; the README calls it 'not fast but not too slow'. The main loop dispatches through a function jump table indexed by opcode, with hot register operations inlined into _vm.go by a code-generation step. An unsafe bulk allocator boxes float64 numbers into LValue interfaces from pooled float blocks, and the integers 0-127 are preallocated. Registry and call-stack sizes are tunable, and a fixed-size call stack is the fastest setting.

## Compared with alternatives

Pick GopherLua over uGO, Tengo, goja or Expr when you specifically want Lua syntax and its Go ecosystem inside a pure-Go binary; pick those siblings when interpreter speed matters, since uGO and Tengo are about 1.5-1.6x faster on fib(35). For speed with Lua in Go, Wangshu (catalogued under language-interpreters) reports a 15-18x JIT speedup over gopher-lua v1.1.2.

## Integration

| | |
|---|---|
| **Form** | Go module (go get github.com/yuin/gopher-lua) |
| **Dependencies** | github.com/chzyer/readline (for the glua REPL); otherwise standard library |
| **Minimum toolchain** | Go 1.23 (go.mod since the 2026-04-01 bump; the 2016 benchmark used Go 1.7) |
| **Platforms** | any Go target (pure Go, no cgo) |
| **Thread safety** | LState is not goroutine-safe; use one per goroutine (sync.Pool pattern in the README). Compiled FunctionProto bytecode is safe to share read-only. |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark caveat: the wiki numbers are single `time` runs of fib(35) from 2016 (Go 1.7, Python 3.4.3, Windows 7, CPU model not stated). Later independent runs reverse both headline wins: CPython beats GopherLua by 1.9-2.3x, and Shopify go-lua is faster than GopherLua (2.90 s vs 3.21 s in ugobenchfib 2022; 4,028 ms vs 4,409 ms in Tengo's README).
- Numbers are float64 only (LNumber), as in Lua 5.1. The bulk allocator uses unsafe and reflect.SliceHeader to point interfaces into shared float blocks, so a whole block stays alive until every float in it is dead.
- Setting a context makes every instruction pay a channel select, about 40% slower on the README's fib run. The CPU columns in that README timing (0.01 s user) are not meaningful; only wall time is.
- Hash parts of tables do not shrink when entries are set to nil (issue #214, open since 2018). A fix for pathologically complex Lua patterns and a LOADNIL code-generation bug fix were only merged on 2026-04-01.

## Known shortcomings

- 2016 wiki numbers (5.40 s vs Python 3.4.3 at 5.84 s, C Lua 1.71 s) are an 8% margin from one run with no CPU model, and the independent Tengo table has CPython 2 about 2.3x faster than GopherLua, contradicting the claim. Go; filed under embedded-scripting.
- Enricher: the claim is obsolete: the independent ozanh/ugobenchfib runs (2020 i5, 2022 M1 with Go 1.18) have CPython 3 1.9-2.0x faster (3.21 vs 1.64 s), the Tengo README has CPython 2 2.3x faster, and go-lua now beats GopherLua (2.90 vs 3.21 s), reversing the wiki. SetContext does a channel select per instruction, the float block allocator is unsafe, issue #214 is open, and maintenance is bursty (yearly merge batches, 52 open PRs).

## Caveats and trade-offs

This is a 2016 single-benchmark wiki page (Go 1.7, Python 3.4.3, Windows 7, no CPU model, one run each), and the margin over CPython is about 8%. GopherLua is about 3.2x slower than reference C Lua 5.1.4 on the same page. The CPython comparison is obsolete: CPython 3.11+ is much faster than 3.4. The independent Tengo README table (d5/tengobench, gopher-lua pinned 2019-12-20) contradicts the claim: there GopherLua takes 4,409 ms for fib(35) against 1,907 ms for native CPython 2, so CPython is about 2.3x faster (derived from page data). The wins are really over other Go-hosted interpreters (go-lua, otto, anko), which are not category baselines. Included mainly as the reference for Go-hosted Lua VMs. [retier] Obsolete 2016 wiki numbers with no CPU model; current independent runs put CPython and go-lua ahead. SetContext does a channel select per instruction, the float block allocator is unsafe, issue #214 open, maintenance bursty (yearly merge batches, 52 open PRs). Go; filed under embedded-scripting.

Lua 5.1 VM in pure Go with a Go-friendly (non stack-based) API, goroutine and channel integration; README says it is 'not fast but not too slow'; using Go contexts for cancellation costs about 40% (7.5 s vs 5.3 s in the README example).

## Maintenance

Widely used (about 7,000 stars, 710 forks), MIT, and still maintained, but merges come in yearly batches (Aug 2024, Nov 2024, Apr 2026) with 54 open issues and 52 open PRs. Fine to depend on for embedding, but do not choose it for speed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The first-party wiki page (last edited 2016-08-20 by the author) shows the fib(35) source for every implementation, plus Go 1.7, Lua 5.1.4, Python 3.4.3 and 'Windows7 64bit CPU:2, Memory:8GB'. It names no CPU model and no build flags, and each implementation was timed once, so it is not A; the numbers are first-party, so C.
- **Verifier notes:** The numbers match the wiki page exactly (GopherLua 5.40 s, Python3.4 5.84 s, lua5.1.4 1.71 s, go-lua 8.13 s, otto 173.32 s, anko 182.73 s). Metadata checks out: MIT, about 7.0k stars, last commit 2026-04-01, active (the README was converted from rst to md that day). Main shortcomings: the claimed win over CPython is marginal and obsolete, and it is contradicted by an independent run. As a Go-embedded Lua VM, the better-fitting category is wave 12's embedded-scripting.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/yuin/gopher-lua>
  - <https://github.com/yuin/gopher-lua/commits>
  - <https://github.com/yuin/gopher-lua/wiki/Benchmarks>
  - <https://raw.githubusercontent.com/yuin/gopher-lua/HEAD/README.md>
  - <https://raw.githubusercontent.com/yuin/gopher-lua/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/d5/tengo/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/yuin/gopher-lua>
  - <https://github.com/yuin/gopher-lua/commits/master>
  - <https://github.com/yuin/gopher-lua/wiki/Benchmarks>
  - <https://github.com/yuin/gopher-lua/issues?q=is%3Aissue+performance>
  - <https://github.com/yuin/gopher-lua/issues/225>
  - <https://github.com/yuin/gopher-lua/issues/214>
  - <https://raw.githubusercontent.com/yuin/gopher-lua/HEAD/README.md>
  - <https://raw.githubusercontent.com/yuin/gopher-lua/HEAD/go.mod>
  - <https://raw.githubusercontent.com/yuin/gopher-lua/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/yuin/gopher-lua/HEAD/_vm.go>
  - <https://raw.githubusercontent.com/yuin/gopher-lua/HEAD/vm.go>
  - <https://raw.githubusercontent.com/yuin/gopher-lua/HEAD/state.go>
  - <https://raw.githubusercontent.com/yuin/gopher-lua/HEAD/value.go>
  - <https://raw.githubusercontent.com/yuin/gopher-lua/HEAD/config.go>
  - <https://raw.githubusercontent.com/yuin/gopher-lua/HEAD/alloc.go>
  - <https://raw.githubusercontent.com/d5/tengo/HEAD/README.md>
  - <https://raw.githubusercontent.com/ozanh/ugo/HEAD/README.md>
  - <https://raw.githubusercontent.com/ozanh/ugobenchfib/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/yuin/gopher-lua`) · [data/wave12/enrich/raw/github_com_yuin_gopher_lua.json](../../../data/wave12/enrich/raw/github_com_yuin_gopher_lua.json) (enrichment confidence 0.7)

</details>
