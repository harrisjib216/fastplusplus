# Expr (expr-lang)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Statically typed Go expression language compiled to bytecode; about 1.3x faster than cel-go on a small boolean rule.

| | |
|---|---|
| **Beats** | cel-go (also compared against goja, govaluate, otto, gval, starlark-go) |
| **Claimed result** | Main benchmark: expr 70.27 ns/op vs cel-go 91.27, goja 146.2, govaluate 152.9, otto 380.1, gval 412.9, evalfilter 990.6, bexpr 1276, starlark 2653 ns/op (expr about 1.3x faster than cel-go, derived from page data). Extra cases vs cel-go: startsWith 124.9 vs 134.8 ns/op, custom function 92.33 vs 110.2 ns/op, map predicate 4695 vs 24421 ns/op (about 5.2x, derived from page data). |
| **Workload** | Evaluating one precompiled boolean expression per iteration, `(Origin == "MOW" \|\| Country == "RU") && (Value >= 100 \|\| Adults == 1)` over a 4-entry map, in each Go expression library (go test -bench, 20 s per benchmark), plus startsWith, custom function call and map(array of 100 ints, x\*2) cases against cel-go only. |
| **Metric** | latency |
| **Hardware** | Apple M2 (darwin/arm64) |
| **Compiler and flags** | go test -bench=. -benchtime=20s; go.mod declares go 1.20, toolchain version not stated |
| **Adoption** | 8k stars (comparison repo: 55 stars, last commit 2023-08-14) |
| **Last commit** | 2026-07-07 |
| **Links** | [repository](https://github.com/expr-lang/expr) · [benchmark](https://github.com/antonmedv/golang-expression-evaluation-comparison) |

## Verdict

In the Expr author's comparison repo (Apple M2, go test -bench=. -benchtime=20s, one run, Go toolchain not stated, mid-2023 library versions), a precompiled boolean rule over a four-key map took 70.27 ns/op in Expr vs 91.27 in cel-go (about 1.3x) and 146.2 in goja, and map over 100 ints took 4,695 vs 24,421 ns/op (about 5.2x, derived from page data). A separate 2020-era benchmark with protobuf input and an optimised cel-go program shows the reverse: cel-go 123 vs Expr 186 ns/op.

## Use it when

- Business rules, feature flags, filters and access policies compiled once and evaluated many times against Go structs or maps; the README lists Argo, OpenTelemetry Collector, CoreDNS and KEDA as users.
- When type errors in user-written rules should surface at compile time against your Go env type rather than at run time.
- Collection predicates over Go slices: map(array, # \* 2) on 100 ints took 4,695 vs 24,421 ns/op for cel-go (about 5.2x, derived from page data).
- Evaluating untrusted expressions on v1.17.7 or later: evaluation is documented as always terminating, and there is a per-run memory budget (DefaultMemoryBudget 1e6) and a compile-time AST node cap (DefaultMaxNodes 1e4).
- Pure-Go builds that want no dependencies: go.mod has no require lines and declares go 1.18.

## Skip it when

- Inputs that are protobuf messages, or expressions that must also run outside Go: franchb/cel-go-benchmarks (linux/amd64, expr v1.8.9 vs cel-go v0.6.0 with OptOptimize and a custom Activation) measured cel-go at 123 ns/op vs Expr at 186 ns/op on one field comparison.
- Anything that needs state, side effects or loops: Expr is side-effect-free by design; use goja, Tengo or a Lua engine.
- Versions before 1.17.7 with untrusted data or expressions: CVE-2025-68156 (unbounded recursion in flatten, min, max, mean and median crashes the process on deeply nested or cyclic data; fixed in 1.17.7) and CVE-2025-29786 (parser memory exhaustion on huge input; fixed in 1.17.0).
- Hot paths that call methods on a struct env: in issue #734 a user measured 365.2 ns/op for a struct-env method vs 48.26 ns/op for a function in a map env and 60.49 ns/op for expr.Function.

## How it is fast

A type checker infers static types from the env, so the compiler emits specialised opcodes: OpLoadFast for map[string]any lookups, OpEqualInt and OpEqualString, and OpCallTyped for functions whose signature is in a generated list, which avoids reflect.Value.Call. An AST optimizer folds constants, turns 'in' over a constant int or string array into a set lookup, and fuses builtins (filter+map, len(filter) into count, sum over ranges and arrays). The VM is a single switch loop over a []Opcode with an []any stack.

## Compared with alternatives

Pick Expr over goja, Tengo or GopherLua when the job is a single side-effect-free rule or filter evaluated many times: on the same boolean rule it is about 2x faster than goja (70.27 vs 146.2 ns/op), and it adds compile-time type checks and termination guarantees. Use those siblings when scripts need statements, state or loops.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none |
| **Minimum toolchain** | go.mod declares go 1.18 |
| **Platforms** | any Go target (pure Go) |
| **Thread safety** | Not documented in the files read. expr.Run creates a fresh vm.VM on every call, so concurrent runs of one Program do not share VM state; a reused vm.VM holds per-run state (stack, ip, memory) and should stay on one goroutine. |
| **Drop-in for the baseline** | no |

## Gotchas

- expr.Run allocates a new vm.VM per call; hot loops can reuse a vm.VM (the repo has a Benchmark_expr_reuseVm case), one per goroutine.
- Runs that build large arrays or maps (ranges, map, sort) fail once they exceed the 1e6 memory budget, and generated expressions above 10,000 AST nodes are rejected at compile time; raise these with vm.VM.MemoryBudget and expr.MaxNodes.
- Go functions whose signature is not in the generated FuncTypes list are called through reflection (the OpCall path); declare hot functions with expr.Function or a matching signature.
- Harness caveats in the comparison repo (no flaw found that inflates Expr's lead): single runs at -benchtime=20s with no -count, mid-2023 versions (expr v1.13.0 under the old github.com/antonmedv/expr path, cel-go v0.17.1), and cel-go programs built without cel.EvalOptions(cel.OptOptimize). goja and otto receive their variables once via vm.Set before the loop, while Expr, cel-go and govaluate are passed the params map on every iteration, which favours the JavaScript engines. Results are checked only after the timed loop.

## Known shortcomings

- Author's own comparison repo with 2023 dependencies (expr v1.13.0, cel-go v0.17.1) and no Go toolchain version; harness fair but off-baseline (cel-go, not Lua, Duktape or QuickJS). Go expression language; filed under embedded-scripting.
- Enricher: single runs on 2023 versions (expr v1.13.0, cel-go v0.17.1) with cel-go built without OptOptimize; counter-evidence in franchb/cel-go-benchmarks (protobuf input, optimized cel-go, 2020 versions) has cel-go at 123 vs expr 186 ns/op. CVE-2025-68156 (fixed 1.17.7) and CVE-2025-29786 (fixed 1.17.0).

## Caveats and trade-offs

The comparison repo is written by Expr's own author; its README results were last updated with the 2023-08-14 'Update deps' commit, and go.mod pins github.com/antonmedv/expr v1.13.0 (Expr has since moved to expr-lang/expr), cel-go v0.17.1, goja 2023-08-12 and starlark-go 2023-08-14, so all versions are dated. One tiny precompiled expression per iteration says little about larger programs. The category baselines (CPython, Lua, MRI, V8) are not involved; goja and otto stand in for JavaScript engines and are Go-hosted. The Expr README itself only links to the comparison.

Statically typed, side-effect-free expression language compiled to bytecode and run on a stack VM, always terminating; not a general-purpose scripting language.

## Maintenance

Active (last commit 2026-07-07, 8k stars, MIT, no dependencies) and widely embedded (the README lists Google Cloud, Uber, Argo and OpenTelemetry Collector); use v1.17.7 or later to get both 2025 denial-of-service fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party comparison repo by Expr's author with public go test code (expr_test.go, celgo_test.go, goja_test.go and the others, common.go) and Apple M2 stated, but no Go toolchain version, so C.
- **Verifier notes:** Numbers match the comparison README exactly; the harness is fair on inspection (each library compiles outside the timed loop and the result is checked after it). Expr is an embeddable Go expression language rather than a general interpreter, so embedded-scripting (wave 12) may fit better than language-interpreters; no earlier-wave category applies.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/antonmedv/golang-expression-evaluation-comparison>
  - <https://github.com/antonmedv/golang-expression-evaluation-comparison/commits>
  - <https://github.com/antonmedv/golang-expression-evaluation-comparison/commits/master/README.md>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/README.md>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/go.mod>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/expr_test.go>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/celgo_test.go>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/common.go>
  - <https://github.com/expr-lang/expr>
  - <https://github.com/expr-lang/expr/commits>
- **Sources the enricher read:**
  - <https://github.com/expr-lang/expr>
  - <https://github.com/expr-lang/expr/commits>
  - <https://github.com/expr-lang/expr/releases>
  - <https://github.com/expr-lang/expr/security/advisories>
  - <https://github.com/expr-lang/expr/security/advisories/GHSA-cfpf-hrx2-8rv6>
  - <https://github.com/expr-lang/expr/security/advisories/GHSA-93mq-9ffx-83m2>
  - <https://github.com/expr-lang/expr/issues?q=is%3Aissue+performance>
  - <https://github.com/expr-lang/expr/issues/734>
  - <https://github.com/expr-lang/expr/issues/607>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/README.md>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/go.mod>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/expr.go>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/bench_test.go>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/vm/vm.go>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/vm/opcodes.go>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/vm/func_types%5Bgenerated%5D.go>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/conf/config.go>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/optimizer/optimizer.go>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/optimizer/in_array.go>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/optimizer/filter_len.go>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/optimizer/filter_map.go>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/README.md>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/go.mod>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/common.go>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/expr_test.go>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/celgo_test.go>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/goja_test.go>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/otto_test.go>
  - <https://raw.githubusercontent.com/antonmedv/golang-expression-evaluation-comparison/HEAD/govaluate_test.go>
  - <https://github.com/franchb/cel-go-benchmarks>
  - <https://raw.githubusercontent.com/franchb/cel-go-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/franchb/cel-go-benchmarks/HEAD/benchmark_test.go>
  - <https://raw.githubusercontent.com/franchb/cel-go-benchmarks/HEAD/go.mod>
  - <https://github.com/guamoko995/expr-cls>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/expr-lang/expr`) · [data/wave12/enrich/raw/github_com_expr_lang_expr.json](../../../data/wave12/enrich/raw/github_com_expr_lang_expr.json) (enrichment confidence 0.75)

</details>
