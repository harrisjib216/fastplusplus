# expr-cls (Go expression evaluator from typed closures)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟡 stale

> Experimental Go expression compiler that turns expr-lang/expr's AST into typed closure chains; \~19x faster evaluation than expr.Run on one formula.

| | |
|---|---|
| **Beats** | expr-lang/expr and google/cel-go |
| **Claimed result** | README: evaluation 9.015 ns/op, 0 B/op, 0 allocs/op versus expr 172.0 ns/op (136 B/op, 6 allocs) and cel-go 267.9 ns/op (368 B/op, 6 allocs), 'evaluates expressions \~18x faster'; derived from page data 19.1x versus expr and 29.7x versus cel-go. Compilation: 1802 ns/op (31 allocs) versus expr 10928 ns/op and cel-go 36255 ns/op ('more than 6x faster'; derived 6.1x and 20.1x). |
| **Workload** | Go benchmarks of compiling the expression and of repeatedly evaluating compiled 'X+(6.0\*Y)' (X=3, Y=5, struct input) with expr-cls, expr-lang/expr and cel-go; evaluation timed per call. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 5 5600H with Radeon Graphics (12 threads), linux/amd64 |
| **Compiler and flags** | Go toolchain version not stated (go.mod requires go 1.24; the benchmark uses b.Loop); default go test -bench flags, linux/amd64 |
| **Adoption** | 3 stars |
| **Last commit** | 2025-09-18 |
| **Links** | [repository](https://github.com/guamoko995/expr-cls) · [benchmark](https://github.com/guamoko995/expr-cls) |

## Verdict

First-party go test -bench output on an AMD Ryzen 5 5600H (linux/amd64, Go version not stated) from commit fa7cc5c: evaluating 'X+(6.0\*Y)' over a two-float64 struct took 9.0 ns/op with 0 allocations versus 172.0 ns/op (6 allocs) for expr-lang/expr via expr.Run and 267.9 ns/op for cel-go Eval with a per-call map (about 19x and 30x, derived from page data); compiling took 1.8 us versus 10.9 us and 36.3 us. The baselines were not run in their fastest configuration (fresh VM and interface boxing per expr call, per-call map for cel-go).

## Use it when

- Hot single-goroutine loops (or one compiled program per goroutine) evaluating a user-supplied arithmetic or comparison formula over a fixed Go struct of int, float64, string or bool fields, e.g. pricing or scoring rules.
- Many short-lived formulas where compile latency dominates: about 1.8 us and 31 allocations per compile versus about 10.9 us for expr-lang/expr on the README machine.
- GC-sensitive paths that need zero allocations per evaluation and a statically known result type.
- Domain-specific operator overloading on your own Go types (matrices, complex numbers, units) by registering plain Go functions per argument-type combination.
- As a reference design to vendor and extend: the closure builder (ast/compiler.go, env/registrators) is a few hundred lines.

## Skip it when

- Evaluating one compiled program from several goroutines: every call writes the input into one variable captured at compile time, so concurrent calls race and can return another caller's result; expr-lang/expr documents its compiled programs as safe for concurrent use.
- Expressions that need maps, slices, member access (a.b), nested struct fields, nil, ternary, let, builtins such as len or filter, or untyped inputs like map[string]any: none of these AST nodes has a Build implementation.
- Formulas that rely on short-circuit && or || to guard a division or a function call: both operands are always evaluated, and Go runtime panics (integer divide by zero) propagate out of the compiled func instead of becoming an error as in expr.Run.
- Production or untrusted-input use: no releases, minimal error reporting, 3 stars, single author, last commit 2025-09-18, and SECURITY.md says issues may be ignored.
- Struct fields of types not registered exactly (int32, float32, named types, pointers): they are silently not variables and compile fails with 'identifier not found'.

## How it is fast

Closure compilation: each AST node is built once into a strictly typed Go closure (func() T via generics), so evaluation is a chain of direct closure calls with no dispatch loop, no []any stack and no interface boxing. Overloads are resolved at compile time by hashing the reflect types of the argument closures, and constant subtrees are folded at compile time with reflect.Call. Struct fields are read by closures that dereference a pointer precomputed from the captured input variable's address plus the field offset (unsafe pointer arithmetic), so a call allocates nothing. Compilation is cheap because overload lookup doubles as the type check and there are no separate checker, optimizer or bytecode passes.

## Compared with alternatives

Against Expr (expr-lang), pick expr-cls only for single-goroutine, struct-typed numeric formulas where per-call nanoseconds and zero allocations matter and the missing language features do not; expr-lang is the mature, concurrency-safe choice for everything else. uGO, Tengo and GopherLua are full embedded scripting languages and solve a different problem than a formula evaluator.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Go standard library plus the module's own packages in the files read (expr.go, env, ast, env/registrators use reflect and unsafe); go.mod also requires expr-lang/expr v1.17.6, google/cel-go v0.26.1 and testify for the tests and benchmarks. No operator set ships in the library itself; the usable example environment lives under tests/example/def_env. |
| **Minimum toolchain** | Go 1.24 (go.mod); code uses reflect.TypeFor and range-over-int, and the benchmarks use testing.B.Loop. |
| **Platforms** | any Go platform (pure Go; field access uses unsafe pointer arithmetic on struct offsets) |
| **Thread safety** | Compiled functions are not safe for concurrent use (ast/compiler.go: the returned closure does srcC = src on a variable shared by all calls, then reads fields through pointers into it). Compile and the Register\* functions mutate plain global maps in env.DefaultEnv without locking, so concurrent first compiles of new struct types can hit Go's concurrent map write fault. |
| **Drop-in for the baseline** | false: different API (generic Compile[In, Out] returning func(In) Out, no error return from evaluation), operators and functions must be registered, the input must be a struct, and most of expr's language (members, collections, ternary, builtins) is missing. |

## Gotchas

- Data race by design: the compiled func copies its argument into a single captured variable and the field-reader closures dereference pointers into that variable, so two goroutines calling the same program can read each other's inputs with no error; compile one program per goroutine or guard it with a mutex, which the 9 ns figure does not include.
- No short-circuit evaluation: registrators.NewBinary builds func() outT { return src(lazyF1(), lazyF2()) }, so 'B != 0 && A / B &gt; 1' still computes A / B and an int divide by zero panics through the caller (there is no recover, unlike expr's VM.Run).
- Types must match exactly: only top-level fields whose type equals a registered variable type are visible, int and float64 need explicit mixed overloads, the requested Out type must equal the expression's result type (otherwise 'unexpectet type result'), and the example env defines == and != only for bool, int and string, not float64. With WithEnv(custom), Compile registers an unseen struct type into the global DefaultEnv instead of the custom env, so its fields are then not found.
- Harness flaws behind the README numbers: they come from commit fa7cc5c ('X+(6.0\*Y)'); HEAD's tests/benchmarks/vs_bench_test.go now uses the constant expression '(.0+1+2+3+4+5+6+7+8+9+10)/2' and comments out cel-go, so HEAD does not reproduce them. The expr baseline calls expr.Run, which allocates a fresh vm.VM and stack on every call (vm.Run: vm := VM{}) and boxes the struct into an interface; the cel-go loop builds a new map[string]interface{} per call; Go version, -count and variance are not given. No correctness bug found: the benchmark asserts all three engines return 33.

## Known shortcomings

- README numbers (eval 9.015 vs expr 172.0 vs cel-go 267.9 ns/op) come from commit fa7cc5c; HEAD 380d646 changed the expression and commented out the cel-go evaluation. Not like for like: expr.Run boxes the struct and builds a fresh VM per call, cel-go builds a map per call. Go version unstated; fork of expr-lang/expr, 3 stars, stale.
- Enricher: data race by design (the compiled func copies its argument into a single captured variable and the field readers dereference pointers into it, so two goroutines calling one program read each other's inputs); no short-circuit evaluation, so 'B != 0 && A / B &gt; 1' still divides and an integer divide by zero panics through the caller with no recover; types must match exactly and WithEnv(custom) registers unseen struct types into the global DefaultEnv. The expr baseline allocates a fresh VM and stack per call and boxes the struct; cel-go builds a map per call; HEAD no longer reproduces the README numbers.

## Caveats and trade-offs

The benchmark code is committed but the README numbers match commit fa7cc5c ('Added performance comparison with cel-go', expression 'X+(6.0\*Y)', cel-go evaluated), not the current HEAD: commit 380d646 ('Fixed constancy optimization', same day) changed tests/benchmarks/vs_bench_test.go to the constant expression '(.0+1+2+3+4+5+6+7+8+9+10)/2' in both benchmarks and commented out the cel-go evaluation benchmark, so the README results cannot be reproduced from HEAD as committed. That commit's code change moved the isConst checks in ast/node.go after the child Build calls, i.e. constant folding was previously not applied; it was a missed-optimization fix, and the benchmark asserts expr-cls and expr agree (33), so the README numbers are not from a wrong-answer path. Comparison is not like for like: expr-cls takes a typed struct and returns float64 through closures; expr.Run takes an interface (boxing the struct) and runs a fresh VM per call; the cel-go loop builds a map[string]interface{} on every call and evaluates through Eval, so allocation and boxing costs are counted against the baselines. Go version, -benchtime and -count unstated, single run, no variance shown. It is a GitHub fork of expr-lang/expr reusing its parser, AST and checker with the evaluator replaced (LICENSE is upstream's MIT, Copyright (c) 2018 Anton Medvedev). govaluate, a listed baseline, is not benchmarked. Last commit September 2025.

Experimental MVP: strictly typed compiled closures taking a Go struct as input (only struct variable sources); operator set fixed, ternary and custom literals not implemented, some expr-lang/expr built-ins disabled, minimal error reporting; compile and evaluate require registering types, functions and constants through an environment package; no dynamic maps or untyped inputs.

## Maintenance

Stale experimental MVP (last commit 2025-09-18, no releases, 3 stars, 0 issues) under upstream's MIT licence; copyable as a design or small vendored package, but compiled programs are not goroutine-safe and the README benchmark is not reproducible from HEAD, so treat the speed-up as single-goroutine, best-case and first-party.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party go test -bench output in the README (AMD Ryzen 5 5600H) against expr-lang/expr and cel-go, with the benchmark code public in tests/benchmarks/vs_bench_test.go; Go version and -benchtime/-count are not stated and the README numbers come from commit fa7cc5c, not HEAD, so it is C, not A.
- **Verifier notes:** Confirmed at C: README numbers (eval 9.015 vs 172.0 vs 267.9 ns/op; compile 1802 vs 10928 vs 36255 ns/op) are as recorded and the derived ratios (19.1x, 29.7x, 6.1x, 20.1x) check out; HEAD's benchmark no longer matches the README (fa7cc5c vs 380d646 diff verified). Metadata confirmed: MIT, 3 stars, 0 forks, forked from expr-lang/expr, last commit 2025-09-18 (stale, just over 12 months).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** like-for-like comparison at a pinned commit; goroutine-safe design and like-for-like baselines
- **Pages the verifier opened:**
  - <https://github.com/guamoko995/expr-cls>
  - <https://github.com/guamoko995/expr-cls/commits/master>
  - <https://github.com/guamoko995/expr-cls/commit/380d646>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/README.md>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/tests/benchmarks/vs_bench_test.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/go.mod>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/fa7cc5c/README.md>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/fa7cc5c/tests/benchmarks/vs_bench_test.go>
- **Sources the enricher read:**
  - <https://github.com/guamoko995/expr-cls>
  - <https://github.com/guamoko995/expr-cls/commits/master>
  - <https://github.com/guamoko995/expr-cls/issues>
  - <https://github.com/guamoko995/expr-cls/tree/master/ast>
  - <https://github.com/guamoko995/expr-cls/tree/master/env>
  - <https://github.com/guamoko995/expr-cls/tree/master/env/registrators>
  - <https://github.com/guamoko995/expr-cls/tree/master/tests/example>
  - <https://github.com/guamoko995/expr-cls/tree/master/tests/example/def_env>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/README.md>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/tests/benchmarks/vs_bench_test.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/fa7cc5c/tests/benchmarks/vs_bench_test.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/go.mod>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/expr.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/env.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/Ideas.md>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/ast/node.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/ast/compiler.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/conf/config.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/env/env.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/env/vars.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/env/binares.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/env/registrators/var.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/env/registrators/binary.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/tests/example/def_env/binares.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/tests/example/def_env/vars.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/tests/example/def_env/env.go>
  - <https://raw.githubusercontent.com/guamoko995/expr-cls/HEAD/tests/example/def_env/funcs.go>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/README.md>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/expr.go>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/vm/vm.go>
  - <https://raw.githubusercontent.com/expr-lang/expr/HEAD/docs/getting-started.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/guamoko995/expr-cls`) · [data/wave12/enrich/raw/github_com_guamoko995_expr_cls.json](../../../data/wave12/enrich/raw/github_com_guamoko995_expr_cls.json) (enrichment confidence 0.82)

</details>
