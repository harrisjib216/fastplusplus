# InkWasm (inkeliz/go_inkwasm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go (wasm target) with generated JavaScript and assembly` · `MIT` · 🟡 stale

> Go js/wasm binding generator and runtime replacing syscall/js calls; about 2x faster on DOM and localStorage micro-benchmarks.

| | |
|---|---|
| **Beats** | Go standard library syscall/js |
| **Claimed result** | Description: up to 2x faster than native syscall/js. ns/op for InkWasm generated bindings vs syscall/js: DOM 11,462 vs 23,550 (2.05x, derived from page data); SetLocalStorage 6,312 vs 11,796 (1.87x, derived); GetLocalStorage 3,300 vs 7,356 (2.23x, derived); GetLocationHostname 2,442 vs 1,979 (InkWasm 23% slower). With the InkWasm runtime API instead of generated bindings, DOM is 14,934 vs 23,550. The BytesRandom row (1,026 vs 1,808) is invalid and excluded (see caveats). Gio fork frame time, InkWasm fork vs upstream gioui.org@bed59024: about 3.02 ms vs 4.65 ms (Chrome 98, Ryzen 3900X), 20.03 vs 31.91 ms (Chrome 98, Xiaomi Note 9) and 4.84 vs 5.58 ms (Safari 15, MacBook Air), a 13% to 37% improvement per the README. |
| **Workload** | Go-to-JS interop calls in a browser: DOM access, random bytes, localStorage get/set and location hostname (inkwasm/tests_js_test.go), plus a Gio WebGL frame-time comparison. |
| **Metric** | latency |
| **Hardware** | Gio table: Chrome 98 @ Ryzen 3900X, Chrome 98 @ Xiaomi Note 9, Safari 15 @ MacBook Air; micro-benchmark machine not stated |
| **Compiler and flags** | Not stated. The README's 'Go 1.20+' line is the main branch's supported Go version, not the benchmark toolchain. The benchmark table is unchanged since tag v0.1.20 (the Go 1.18-1.20 line). |
| **Adoption** | 38 stars; used in a fork of Gio |
| **Last commit** | 2024-05-19 |
| **Links** | [repository](https://github.com/inkeliz/go_inkwasm) · [benchmark](https://github.com/inkeliz/go_inkwasm) |

## Verdict

A first-party Go benchmark table (inkwasm/tests_js_test.go; browser, Go version and machine not stated; run before the May 2024 changes) has generated bindings against syscall/js at 11,462 vs 23,550 ns/op for create-and-append-a-div (2.05x), 6,312 vs 11,796 for localStorage.setItem (1.87x) and 3,300 vs 7,356 for getItem (2.23x), but 2,442 vs 1,979 for location.hostname (slower); the BytesRandom row is invalid. In a Gio fork whose InkWasm commit (baf7d94) sits directly on gioui.org@bed59024 and swaps the GL/JS bindings, frame time drops from about 4.65 to 3.02 ms (Chrome 98, Ryzen 3900X), 31.91 to 20.03 ms (Chrome 98, Xiaomi Note 9) and 5.58 to 4.84 ms (Safari 15, MacBook Air).

## Use it when

- Go (gc toolchain) browser apps whose frame time is dominated by many small JS calls, such as WebGL/WebGPU command streams; the Gio fork that swapped syscall/js for InkWasm cut frame time 13-37%.
- Hot call sites with a fixed JS target and simple argument types (integers, floats, bools, strings, numeric slices, Objects): DOM construction, localStorage, canvas or GL calls in a loop.
- When garbage-collector pressure from syscall/js conversions shows up in profiles (11 allocs/op for the syscall/js DOM loop against 1 for the generated binding).
- Teams willing to vendor the generator, pin a Go toolchain and check the generated code into version control.

## Skip it when

- Go 1.24 or newer without patching: the build, test and bench subcommands look for \$GOROOT/misc/wasm/wasm_exec.js, which Go 1.24 moved to lib/wasm, so they fail with 'failed to find \$GOROOT/misc/wasm/wasm_exec.js driver'.
- TinyGo, Go-to-JS callbacks or exports: TinyGo is unsupported, function arguments are not supported, and exporting Go functions still needs syscall/js js.FuncOf (go:wasmexport is not supported).
- Plain property reads: the location.hostname row is 23% slower than syscall/js (2,442 vs 1,979 ns/op), and the README says results vary with how each API is used.
- Codebases where tools must not rewrite sources: the README warns the generator changes files of the current package and of imported packages.
- Code that needs argument checking or automatic lifetime management: unsupported argument types silently become undefined and every Object must be freed by hand.

## How it is fast

Each declared function becomes its own //go:wasmimport gojs import whose generated JavaScript reads the typed arguments straight off the Go stack (DataView loads, TextDecoder for strings, zero-copy typed-array views for slices), evaluates the fixed JS expression and writes the result back to the stack, so one Go call is one boundary crossing with no js.Value boxing. JS values held by Go live in a plain JS array indexed by an int with a free list instead of finalizer-tracked references, which is why the README rows show 0-1 allocs/op for the generated bindings against 2-11 for syscall/js.

## Compared with alternatives

No other Go interop library is catalogued; zaw and wasm-bindgen address the same JS-boundary cost for Rust, so pick InkWasm only when the app is written in Go for js/wasm and interop calls, not compute, dominate the profile.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Go standard library at run time; the generator uses golang.org/x/tools and golang.org/x/sync, and its test and bench commands drive a local Chrome through chromedp |
| **Minimum toolchain** | Main branch: go.mod declares go 1.22 (PR #2 made it Go 1.21+ compatible; the README says 1.20+); Go 1.18-1.20 use tag v0.1.20; build/test/bench break on Go 1.24+ until the wasm_exec.js path is patched |
| **Platforms** | GOOS=js GOARCH=wasm with the gc compiler, in browsers (the generated glue extends go.importObject.gojs from wasm_exec.js); TinyGo unsupported; Node.js not documented |
| **Thread safety** | Not documented. Go js/wasm runs on one thread; the JS-side object table is a single array with a free list shared by all goroutines. |
| **Drop-in for the baseline** | partial — the runtime API mirrors syscall/js (Global, Get, Call, Invoke, New) but returns inkwasm.Object values that need explicit Free, and the fast path requires generator-declared bodyless functions |

## Gotchas

- The README's BytesRandom row (1,026 vs 1,808 ns/op) measures no work: the binding is declared //inkwasm:get globalThis.TestObject_GetRandom with a []byte argument, and parser/binder.go turns a get with one argument into an index expression (TestObject_GetRandom[&lt;Uint8Array&gt;]), so crypto.getRandomValues never runs, while the syscall/js side calls it and runs CopyBytesToGo. In your own code, too, a get directive with an argument means property indexing, not a call.
- Object lifetime is manual and unchecked: Free only pushes the id onto a free list (inkwasm/wasm_js.js Internal.Free) without clearing the table slot, there is no finalizer, so a missed Free leaks the JS value for good, and freeing two copies of the same Object puts its id on the free list twice, after which two new Objects share one slot and silently alias.
- PR #5 (May 2024) removed argument verification and marked call/callVoid/invoke/invokeVoid/newObj //go:noescape: unsupported Go types (maps, funcs, chans, complex numbers) arrive in JS as undefined with no error unless you call VerifyArgs, and slices reach JS as zero-copy typed-array views over Go memory, so JS must not keep a passed []byte or []float32 after the call returns.
- The published micro-benchmark table predates the go:wasmimport rewrite (PR #2, May 2024) and names no browser, Go version or machine (the bench runner opens a non-headless Chrome via chromedp); re-measure on your own toolchain before relying on the 2x figure.

## Known shortcomings

- The BytesRandom row is invalid (//inkwasm:get emits a property lookup, so crypto.getRandomValues never runs) and is dropped from the claim; micro-benchmark environment unstated; GetLocationHostname is slower; only 13-37% faster in the Gio app. Stale since 2024-05-19.
- BytesRandom row confirmed invalid: a get with an argument becomes property indexing, so getRandomValues never runs; the other rows are equivalent. Build, test and bench fail on Go 1.24+ (hard-coded \$GOROOT/misc/wasm/wasm_exec.js, moved to lib/wasm). Free never clears its table slot, so a double Free aliases two objects; PR #5 removed argument checks and added noescape while slices reach JS as zero-copy views.

## Caveats and trade-offs

The BytesRandom benchmark is invalid. Its InkWasm side declares gen_GetRandom with //inkwasm:get globalThis.TestObject_GetRandom. For a get directive with one argument, the generator (parser/binder.go) emits a property lookup indexed by the byte slice (TestObject_GetRandom[slice]), so crypto.getRandomValues never runs and nothing is copied back. The syscall/js side invokes the function and calls CopyBytesToGo. The micro-benchmark environment (browser, Go version, hardware) is not stated, the numbers are one first-party run, and the table predates the May 2024 changes (Go 1.21+ compatibility #2, noescape and disabled verifications #5). One listed case (GetLocationHostname) is slower, and the README says results vary with how each API is used. The InkWasm DOM loop frees each object explicitly while syscall/js relies on finalizers. In the real Gio application the gain shrinks to 13-37%, measured on a fork against one upstream commit; the live comparison page (gio-bench.pages.dev) was not checked. The generator is experimental and rewrites source files in place. go:wasmexport is not supported.

Experimental generator that rewrites source files of the current and imported packages (README tells users to back up and use version control); covers a subset of syscall/js usage patterns.

## Maintenance

Stale since 2024-05-19 (11 commits, 38 stars) and experimental by its own README; MIT and small enough to copy the generated-glue pattern, but its build tooling needs a one-line path fix for Go 1.24+ and it has no TinyGo or export support.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README's first-party Go benchmark table compares InkWasm with syscall/js, and the code is public (inkwasm/tests_js_test.go), but the browser, Go version and machine for the micro-benchmarks are not stated. The Gio frame-time table names the browsers and devices but is a rough '\~' comparison of a fork against upstream. So C.
- **Verifier notes:** Downgraded for an overstated claim, still tier C: the BytesRandom row compares a property lookup that never calls the random function against a real call plus copy-back (wrong-work row; the other rows look equivalent). Shortcomings to record: invalid BytesRandom row; unstated micro-benchmark environment; one row slower; first-party, stale 2022-era numbers; only a 13-37% gain in the Gio app. Metadata checked: MIT, 38 stars, not a fork, last commit 2024-05-19 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-86 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/inkeliz/go_inkwasm>
  - <https://github.com/inkeliz/go_inkwasm/commits/master>
  - <https://github.com/inkeliz/go_inkwasm/commits/master/README.md>
  - <https://github.com/inkeliz/go_inkwasm/tree/master/inkwasm>
  - <https://github.com/inkeliz/go_inkwasm/tree/master/bind>
  - <https://github.com/inkeliz/go_inkwasm/tree/master/parser>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/v0.1.20/README.md>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/inkwasm/tests_js_test.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/inkwasm/tests_js_test.js>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/parser/binder.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/parser/parser.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/bind/bind.go>
- **Sources the enricher read:**
  - <https://github.com/inkeliz/go_inkwasm>
  - <https://github.com/inkeliz/go_inkwasm/issues?q=is%3Aissue>
  - <https://github.com/inkeliz/go_inkwasm/pulls?q=is%3Apr>
  - <https://github.com/inkeliz/go_inkwasm/pull/5/files>
  - <https://github.com/inkeliz/go_inkwasm/tree/master/inkwasm>
  - <https://github.com/inkeliz/go_inkwasm/tree/master/build>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/go.mod>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/main.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/build/build.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/build/test.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/inkwasm/tests_js_test.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/inkwasm/tests_js_test.js>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/inkwasm/wasm_js.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/inkwasm/wasm_js.js>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/inkwasm/inkwasm_js.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/inkwasm/inkwasm_js.js>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/inkwasm/inkwasm_js.s>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/inkwasm/args_js.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/inkwasm/funcs_js.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/inkwasm/globals_js.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/parser/binder.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/parser/parser.go>
  - <https://raw.githubusercontent.com/inkeliz/go_inkwasm/HEAD/bind/bind.go>
  - <https://github.com/Inkeliz/gio/commit/baf7d943e5d50debf354d4cd5f951d442d4d9b4e>
  - <https://raw.githubusercontent.com/golang/go/go1.24.0/lib/wasm/wasm_exec.js>
  - <https://raw.githubusercontent.com/golang/go/go1.24.0/misc/wasm/wasm_exec.js>
  - <https://raw.githubusercontent.com/golang/go/go1.23.0/misc/wasm/wasm_exec.js>
  - <https://raw.githubusercontent.com/golang/go/go1.25.0/src/cmd/compile/internal/ssagen/abi.go>
  - <https://raw.githubusercontent.com/golang/go/go1.24.0/src/cmd/compile/internal/noder/noder.go>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/inkeliz/go_inkwasm`) · [data/wave13/enrich/raw/github_com_inkeliz_go_inkwasm.json](../../../data/wave13/enrich/raw/github_com_inkeliz_go_inkwasm.json) (enrichment confidence 0.75)

</details>
